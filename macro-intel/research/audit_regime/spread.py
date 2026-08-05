import sys, numpy as np, pandas as pd
sys.path.insert(0,'.')
from zoneinfo import ZoneInfo
from scipy import stats
U='/root/.claude/uploads/b22822dc-6a41-522c-931f-c596aee488bc/'
m=pd.read_csv(U+'4b5607af-XAUUSD_M15_202204290100_202608041500.csv',sep='\t')
m.columns=[c.strip('<>').lower() for c in m.columns]
m['dt']=pd.to_datetime(m['date']+' '+m['time'],format='%Y.%m.%d %H:%M:%S')
m=m.set_index('dt').sort_index()
sp=m['spread'].astype(float)
print("A) LA DONNEE EST-ELLE EXPLOITABLE ?\n")
print(f"  spread : mediane {sp.median():.1f} points ({sp.median()/100:.3f} $/oz)  moyenne {sp.mean():.1f}  max {sp.max():.0f}")
print(f"  valeurs a zero (donnee manquante) : {(sp==0).sum()} soit {100*(sp==0).mean():.2f} %")
print(f"  quantiles : "+"  ".join(f"q{q}={np.percentile(sp[sp>0],q):.0f}" for q in (10,25,50,75,90,99)))
sp=sp.replace(0,np.nan)
print(f"  par annee (mediane) : "+"  ".join(f"{y}:{sp[sp.index.year==y].median():.0f}" for y in sorted(set(sp.index.year))))

# --- features de spread ---
F={}
F['spread_brut']=sp
F['spread_rel']=sp/sp.rolling(96*20,min_periods=500).median()      # vs son propre regime
F['spread_pct']=sp.rolling(96*20,min_periods=500).rank(pct=True)   # percentile glissant
F['spread_choc']=sp/sp.rolling(96,min_periods=48).median()          # vs les 24 dernieres heures

# --- alignement sur les trades reels (export TradingView, 2020-2026) ---
d=pd.read_csv(U+'89f8f18e-XAU_Momentum_v11.csv',encoding='utf-8-sig'); d.columns=[c.strip() for c in d.columns]
rows=[]
for tn,sub in d.groupby('Numéro de trade'):
    e=sub[sub['Type'].str.contains('Entrer',na=False)]
    if len(e)==0: continue
    e0=e.iloc[0]
    rows.append(dict(dt=pd.to_datetime(e0['Date et heure']),px=float(e0['Prix USD']),
        pct=float(e0['Retour %']),dir=1 if 'long' in str(e0['Type']).lower() else -1))
t=pd.DataFrame(rows).sort_values('dt').reset_index(drop=True)
t['R']=t.pct/abs(t.loc[t.pct<=0,'pct'].median())
tz=ZoneInfo('Europe/Athens')
t['off']=t.dt.map(lambda x:180 if x.to_pydatetime().replace(tzinfo=tz).utcoffset().total_seconds()==10800 else 120)
t['bdt']=t.dt+pd.to_timedelta(t.off,unit='m')
j=m.reindex(t.bdt)
t['perr']=np.abs(j.close.values-t.px.values)
for k in F: t[k]=F[k].reindex(t.bdt).values
cov=t[t.perr.notna()&(t.perr<3.0)&t.spread_rel.notna()].copy()
print(f"\n  trades apparies avec un spread valide : {len(cov)} / {len(t)}  (erreur de prix mediane {cov.perr.median():.3f} $)")

print("\nB) ECRAN DE REDONDANCE\n")
c2=m.close; pc=c2.shift()
trv=pd.concat([m.high-m.low,(m.high-pc).abs(),(m.low-pc).abs()],axis=1).max(axis=1)
atr=trv.ewm(alpha=1/14,adjust=False).mean()
EX={'ATR normalise':(atr/c2),'volume':m['tickvol'].astype(float),
    'range de la bougie':(m.high-m.low)/atr,'heure UTC':pd.Series(m.index.hour,index=m.index)}
for k in F:
    row=[]
    for k2,s2 in EX.items():
        dd=pd.concat([F[k],s2],axis=1).dropna()
        row.append(np.corrcoef(dd.iloc[:,0],dd.iloc[:,1])[0,1] if len(dd)>1000 else np.nan)
    mx=np.nanmax(np.abs(row))
    print(f"  {k:14s} "+"  ".join(f"{k2[:10]}={x:+.3f}" for k2,x in zip(EX,row))+f"   max|r|={mx:.3f}"+("   REDONDANT" if mx>0.5 else ""))

print("\nC) VALEUR PREDICTIVE (4 hypotheses, correction BH)\n")
R=cov.R.values; ti=np.arange(len(cov))
res=[]
for k in F:
    x=cov[k].values; ok=np.isfinite(x)
    rho,p=stats.spearmanr(x[ok],R[ok])
    q=pd.qcut(pd.Series(x[ok]),5,labels=False,duplicates='drop')
    qe=[R[ok][q==i].mean() for i in sorted(pd.unique(q))]
    xr=stats.rankdata(x[ok]); rr=stats.rankdata(R[ok]); tr=stats.rankdata(ti[ok])
    rs=lambda a,b:a-np.polyval(np.polyfit(b,a,1),b)
    rp=np.corrcoef(rs(xr,tr),rs(rr,tr))[0,1]
    res.append((k,p,rho,rp))
    print(f"  {k:14s} n={ok.sum():4d} rho={rho:+.3f} p={p:.4f} | quintiles "+" ".join(f"{e:+.2f}" for e in qe)+f" | rho partiel (temps) {rp:+.3f}")
ps=np.array([r[1] for r in res]); order=np.argsort(ps)
print(f"\n  Benjamini-Hochberg (FDR 10 %, 4 tests) :")
surv=[]
for rank,i in enumerate(order):
    s=(rank+1)/4*0.10; ok=ps[i]<=s
    if ok: surv.append(res[i][0])
    print(f"    {res[i][0]:14s} p={ps[i]:.4f}  seuil={s:.4f}  {'RETENU' if ok else '—'}")

print("\nD) TEST PRATIQUE — filtrer les cassures nees dans un spread anormal\n")
for k in ['spread_rel','spread_choc','spread_pct']:
    x=cov[k].values; ok=np.isfinite(x)
    for q in [0.80,0.90]:
        thr=np.nanquantile(x[ok],q); keep=ok&(x<=thr); rej=ok&(x>thr)
        if rej.sum()<40: continue
        r1,r0=R[keep],R[rej]
        pf1=r1[r1>0].sum()/abs(r1[r1<=0].sum()); pf0=r0[r0>0].sum()/abs(r0[r0<=0].sum()) if (r0<=0).any() else np.inf
        tt,p=stats.ttest_ind(r1,r0,equal_var=False)
        print(f"  {k:12s} rejeter au-dessus du q{q:.0%} : gardes n={keep.sum():3d} PF={pf1:.3f} E={r1.mean():+.3f} | "
              f"rejetes n={rej.sum():3d} PF={pf0:.3f} E={r0.mean():+.3f} | ecart {r1.mean()-r0.mean():+.3f} p={p:.3f}")
cov.to_pickle('spread_cov.pkl')
