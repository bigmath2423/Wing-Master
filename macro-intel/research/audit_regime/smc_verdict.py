import pandas as pd, numpy as np, re
from scipy import stats
U='/root/.claude/uploads/b22822dc-6a41-522c-931f-c596aee488bc/'
d=pd.read_csv(U+'bcf683ec-SMC_Gold_BT_TVC_GOLD_20260805.csv',encoding='utf-8-sig')
d.columns=[c.strip() for c in d.columns]
rows=[]
for tn,sub in d.groupby('Numéro de trade'):
    e=sub[sub['Type'].str.contains('Entrer',na=False)]; x=sub[sub['Type'].str.contains('Sortir',na=False)]
    if len(e)==0 or len(x)==0: continue
    e0=e.iloc[0]; sig=str(e0['Signal']); m=re.search(r'(BUY|SELL)\s+(\d+)',sig)
    rows.append(dict(dt=pd.to_datetime(e0['Date et heure']),
        dir=1 if 'long' in str(e0['Type']).lower() else -1,
        score=int(m.group(2)) if m else np.nan, pnl=float(e0['P&L net EUR']),
        pct=float(e0['Retour %']),exit=str(x.iloc[-1]['Signal']),
        val=float(e0['Taille (valeur)']),bars=float(e0['Durée (barres)'])))
t=pd.DataFrame(rows).sort_values('dt').reset_index(drop=True)
t['R']=t.pct/abs(t.loc[t.pct<=0,'pct'].median())
def M(s):
    r=s.R.values; p=s.pnl.values; w=r[r>0]; lo=r[r<=0]; eq=np.cumsum(r)
    dd=(eq-np.maximum.accumulate(np.concatenate([[0],eq]))[1:]).min()
    return dict(n=len(r),wr=100*len(w)/len(r),pf=(w.sum()/abs(lo.sum())) if lo.sum()<0 else np.inf,
                E=r.mean(),dd=dd,t=r.mean()/(r.std(ddof=1)/np.sqrt(len(r))),tot=r.sum(),net=p.sum())
def line(lab,m):
    print(f"  {lab:30s} n={m['n']:4d} WR={m['wr']:5.1f}% PF={m['pf']:6.3f} E={m['E']:+.3f}R DD={m['dd']:7.1f}R "
          f"t={m['t']:+5.2f} tot={m['tot']:+7.1f}R net={m['net']:+8.0f}EUR")
print("="*112)
print("ANCIEN SYSTEME SMC — VERDICT SUR 6,5 ANS")
print("="*112)
print(f"periode {t.dt.min()} -> {t.dt.max()}   |   commission totale {d['Commission EUR'].astype(float).sum():.2f}")
print(f"tranches : {len(t)}  ({t.dir.value_counts().to_dict()})\n")
m=M(t); line('TOTAL',m)
rng=np.random.default_rng(3); bs=[rng.choice(t.R.values,len(t)).mean() for _ in range(10000)]
print(f"  {'IC95 de l esperance':30s} [{np.percentile(bs,2.5):+.3f} ; {np.percentile(bs,97.5):+.3f}] R    P(E>0) = {100*np.mean(np.array(bs)>0):.1f}%")
print("\nSORTIES"); print(t.exit.value_counts().to_string())
print("\nPAR ANNEE")
for y in sorted(t.dt.dt.year.unique()):
    s=t[t.dt.dt.year==y]
    if len(s)>=20: line(str(y),M(s))
print("\n"+"="*112)
print("LE SCORE /100 CLASSE-T-IL QUOI QUE CE SOIT ?  (c'est le coeur de l'ancien systeme)")
print("="*112)
ts=t[t.score.notna()]
print(f"scores presents : min {ts.score.min():.0f}  max {ts.score.max():.0f}  mediane {ts.score.median():.0f}\n")
for lo_,hi_ in [(0,74),(75,84),(85,89),(90,94),(95,100)]:
    s=ts[(ts.score>=lo_)&(ts.score<=hi_)]
    if len(s)>=25: line(f'score {lo_}-{hi_}',M(s))
c=np.corrcoef(ts.score,ts.R)[0,1]
sl,ic,r_,p_,se=stats.linregress(ts.score,ts.R)
print(f"\n  correlation score / resultat = {c:+.4f}")
print(f"  pente = {sl:+.5f} R par point de score   p = {p_:.3f}")
print(f"  => un score de 100 rend {sl*100+ic:+.3f} R, un score de 75 rend {sl*75+ic:+.3f} R")
print("\n"+"="*112)
print("COMPARAISON AVEC LE SYSTEME ACTUEL (memes annees, meme unite : R)")
print("="*112)
ref=pd.read_csv(U+'89f8f18e-XAU_Momentum_v11.csv',encoding='utf-8-sig'); ref.columns=[c2.strip() for c2 in ref.columns]
rr=[]
for tn,sub in ref.groupby('Numéro de trade'):
    e=sub[sub['Type'].str.contains('Entrer',na=False)]
    if len(e)==0: continue
    e0=e.iloc[0]; rr.append(dict(dt=pd.to_datetime(e0['Date et heure']),pct=float(e0['Retour %']),pnl=float(e0['P&L net EUR'])))
R2=pd.DataFrame(rr).sort_values('dt'); R2['R']=R2.pct/abs(R2.loc[R2.pct<=0,'pct'].median())
a=t[t.dt>='2020-06-22']; b=R2[R2.dt>='2020-06-22']
line('ANCIEN SMC',M(a)); line('ACTUEL (Momentum v11)',M(b))
tt,pv=stats.ttest_ind(b.R.values,a.R.values,equal_var=False)
print(f"\n  ecart d esperance actuel - ancien = {b.R.mean()-a.R.mean():+.3f} R   t={tt:+.2f}   p={pv:.5f}")
