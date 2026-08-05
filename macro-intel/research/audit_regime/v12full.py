import pandas as pd, numpy as np
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
    t['R']=t.pct/abs(t.loc[t.pct<=0,'pct'].median()); t.attrs['cur']=cur; return t
v12=load(U+'c11cdeb7-XAU_v12_BT_TVC_GOLD_20260805.csv')
v11=load(U+'89f8f18e-XAU_Momentum_v11.csv')
def M(s):
    r=s.R.values; w=r[r>0]; lo=r[r<=0]; eq=np.cumsum(r)
    dd=(eq-np.maximum.accumulate(np.concatenate([[0],eq]))[1:]).min()
    st=0;mx=0
    for x in r: st=st+1 if x<=0 else 0; mx=max(mx,st)
    return dict(n=len(r),wr=100*len(w)/len(r),pf=w.sum()/abs(lo.sum()),E=r.mean(),dd=dd,
                t=r.mean()/(r.std(ddof=1)/np.sqrt(len(r))),tot=r.sum(),streak=mx)
def line(lab,m):
    print(f"  {lab:32s} n={m['n']:4d} WR={m['wr']:5.1f}% PF={m['pf']:6.3f} E={m['E']:+.3f}R DD={m['dd']:6.1f}R t={m['t']:+5.2f} serie={m['streak']:2d}")
print("="*96); print("v12 SUR TOUT L'HISTORIQUE"); print("="*96)
print(f"  periode : {v12.dt.min()} -> {v12.dt.max()}   ({(v12.dt.max()-v12.dt.min()).days/365.25:.2f} ans)")
print(f"  devise  : {v12.attrs['cur']}   directions {v12.dir.value_counts().to_dict()}\n")
line('v12',M(v12)); line('v11 (reference)',M(v11))
print("\n  ATTENDU : ~783 trades, PF ~1.23")
same=v11[(v11.dt>=v12.dt.min())&(v11.dt<=v12.dt.max())]
print(f"\n  fenetre commune : v11 y compte {len(same)} trades, v12 {len(v12)}")
A=set(v12.dt); B=set(same.dt)
print(f"  entrees communes {len(A&B)}  |  seulement v12 {len(A-B)}  |  seulement v11 {len(B-A)}")
if len(A^B)>0 and len(A^B)<25:
    for x in sorted(A-B)[:8]: print(f"    v12 seule : {x}")
    for x in sorted(B-A)[:8]: print(f"    v11 seule : {x}")
print("\nPAR ANNEE")
for y in sorted(v12.dt.dt.year.unique()):
    a=v12[v12.dt.dt.year==y]; b=v11[v11.dt.dt.year==y]
    if len(a)>=15: line(f'  {y}  v12',M(a))
    if len(b)>=15: line(f'  {y}  v11',M(b))
