import pandas as pd, numpy as np, re
from scipy import stats
p='/root/.claude/uploads/b22822dc-6a41-522c-931f-c596aee488bc/89f8f18e-XAU_Momentum_v11.csv'
d=pd.read_csv(p,encoding='utf-8-sig'); d.columns=[c.strip() for c in d.columns]
rows=[]
for tn,sub in d.groupby('Numéro de trade'):
    e=sub[sub['Type'].str.contains('Entrer',na=False)]; x=sub[sub['Type'].str.contains('Sortir',na=False)]
    if len(e)==0 or len(x)==0: continue
    e0=e.iloc[0]; sig=str(e0['Signal'])
    m=re.search(r'A(-?\d+)',sig); sc=re.search(r'(BUY|SELL) (\d+)',sig)
    rows.append(dict(dt=pd.to_datetime(e0['Date et heure']),
        dir=1 if 'long' in str(e0['Type']).lower() else -1,
        adx=int(m.group(1)) if m else np.nan, score=int(sc.group(2)) if sc else np.nan,
        pnl=float(e0['P&L net EUR']),pct=float(e0['Retour %']),
        exit=str(x.iloc[-1]['Signal']),px=float(e0['Prix USD']),val=float(e0['Taille (valeur)'])))
t=pd.DataFrame(rows).sort_values('dt').reset_index(drop=True)
R=abs(t.loc[t.pnl<=0,'pct'].median()); t['R']=t.pct/R
def M(s,lab):
    p_=s.pnl.values; r=s.R.values; gl=-p_[p_<=0].sum()
    eq=np.cumsum(p_)+10000; dd=(eq/np.maximum.accumulate(eq)-1).min()
    st=0;mx=0
    for x in p_: st=st+1 if x<=0 else 0; mx=max(mx,st)
    print(f"{lab:26s} n={len(s):4d} WR={100*(p_>0).mean():5.1f}% PF={p_[p_>0].sum()/gl:6.3f} "
          f"E={r.mean():+.3f}R DD={100*dd:6.2f}% t={r.mean()/(r.std(ddof=1)/np.sqrt(len(r))):+5.2f} "
          f"serie={mx:2d} net={p_.sum():+8.0f}")
print(f"Periode : {t.dt.min()} -> {t.dt.max()}   ({(t.dt.max()-t.dt.min()).days/365.25:.2f} ans)")
print(f"Directions : {t.dir.value_counts().to_dict()}   Commission : {d['Commission EUR'].astype(float).sum():.2f}")
print(f"\nPercentile ADX inscrit : min {t.adx.min():.0f}  max {t.adx.max():.0f}  mediane {t.adx.median():.0f}  na={t.adx.isna().sum()}")
print(f"  trades avec A > 50 : {(t.adx>50).sum()}  =>  FILTRE {'ACTIF' if (t.adx>50).sum()==0 else 'INACTIF (run de reference)'}\n")
M(t,'RUN COMPLET')
print()
for y in sorted(t.dt.dt.year.unique()):
    s=t[t.dt.dt.year==y]
    if len(s)>=15: M(s,f'  {y}')
t.to_pickle('newrun.pkl')
