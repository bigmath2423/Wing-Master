import pandas as pd, numpy as np, re
from scipy import stats
U='/root/.claude/uploads/b22822dc-6a41-522c-931f-c596aee488bc/'
def load(p):
    d=pd.read_csv(p,encoding='utf-8-sig'); d.columns=[c.strip() for c in d.columns]
    cur='USD' if 'P&L net USD' in d.columns else 'EUR'
    r=[]
    for tn,sub in d.groupby('Numéro de trade'):
        e=sub[sub['Type'].str.contains('Entrer',na=False)]; x=sub[sub['Type'].str.contains('Sortir',na=False)]
        if len(e)==0 or len(x)==0: continue
        e0=e.iloc[0]
        r.append(dict(dt=pd.to_datetime(e0['Date et heure']),
            dir=1 if 'long' in str(e0['Type']).lower() else -1,
            pnl=float(e0[f'P&L net {cur}']),pct=float(e0['Retour %']),exit=str(x.iloc[-1]['Signal'])))
    t=pd.DataFrame(r).sort_values('dt').reset_index(drop=True)
    t['R']=t.pct/abs(t.loc[t.pct<=0,'pct'].median()); return t
v12=load(U+'2d1c3210-XAU_v12_BT_TVC_GOLD_20260805.csv')
v11=load(U+'89f8f18e-XAU_Momentum_v11.csv')
def M(s):
    r=s.R.values; w=r[r>0]; lo=r[r<=0]; eq=np.cumsum(r)
    dd=(eq-np.maximum.accumulate(np.concatenate([[0],eq]))[1:]).min()
    st=0;mx=0
    for x in r: st=st+1 if x<=0 else 0; mx=max(mx,st)
    return dict(n=len(r),wr=100*len(w)/len(r),pf=w.sum()/abs(lo.sum()),E=r.mean(),dd=dd,
                t=r.mean()/(r.std(ddof=1)/np.sqrt(len(r))),tot=r.sum(),streak=mx)
def line(lab,m):
    print(f"  {lab:36s} n={m['n']:4d} WR={m['wr']:5.1f}% PF={m['pf']:6.3f} E={m['E']:+.3f}R DD={m['dd']:6.1f}R t={m['t']:+5.2f} serie={m['streak']:2d}")
print("="*100)
print("CE QUE CONTIENT REELLEMENT LE FICHIER")
print("="*100)
print(f"  periode : {v12.dt.min()}  ->  {v12.dt.max()}")
print(f"  duree   : {(v12.dt.max()-v12.dt.min()).days} jours, soit {(v12.dt.max()-v12.dt.min()).days/365.25:.2f} an")
print(f"  trades  : {len(v12)}   directions {v12.dir.value_counts().to_dict()}")
line('v12 sur SA fenetre',M(v12))
print(f"\n  Pour memoire, la v11 couvrait : {v11.dt.min().date()} -> {v11.dt.max().date()}, soit {(v11.dt.max()-v11.dt.min()).days/365.25:.2f} ans et {len(v11)} trades.")
print(f"  Le fichier v12 commence {(v12.dt.min()-v11.dt.min()).days} jours plus tard.\n")
print("="*100)
print("MEME FENETRE, MEME PERIODE — v11 vs v12")
print("="*100)
a=v11[(v11.dt>=v12.dt.min())&(v11.dt<=v12.dt.max())]
line('v11 restreinte a la fenetre v12',M(a))
line('v12',M(v12))
tt,pv=stats.ttest_ind(v12.R.values,a.R.values,equal_var=False)
print(f"\n  ecart d'esperance v12 - v11 = {v12.R.mean()-a.R.mean():+.3f} R   t={tt:+.2f}   p={pv:.3f}")
print("="*100)
print("CETTE FENETRE EST-ELLE REPRESENTATIVE ? (v11 sur 6,3 ans, annee par annee)")
print("="*100)
for y in sorted(v11.dt.dt.year.unique()):
    s=v11[v11.dt.dt.year==y]
    if len(s)>=25: line(str(y),M(s))
print()
line('v11 AVANT sept. 2025',M(v11[v11.dt<v12.dt.min()]))
line('v11 DEPUIS sept. 2025',M(v11[v11.dt>=v12.dt.min()]))
