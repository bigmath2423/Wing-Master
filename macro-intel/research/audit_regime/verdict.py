import pandas as pd, numpy as np, re
from scipy import stats
U='/root/.claude/uploads/b22822dc-6a41-522c-931f-c596aee488bc/'
def load(p,lab):
    d=pd.read_csv(p,encoding='utf-8-sig'); d.columns=[c.strip() for c in d.columns]
    rows=[]
    for tn,sub in d.groupby('Numéro de trade'):
        e=sub[sub['Type'].str.contains('Entrer',na=False)]; x=sub[sub['Type'].str.contains('Sortir',na=False)]
        if len(e)==0 or len(x)==0: continue
        e0=e.iloc[0]
        rows.append(dict(dt=pd.to_datetime(e0['Date et heure']),
            dir=1 if 'long' in str(e0['Type']).lower() else -1,
            pnl=float(e0['P&L net EUR']),pct=float(e0['Retour %']),exit=str(x.iloc[-1]['Signal'])))
    t=pd.DataFrame(rows).sort_values('dt').reset_index(drop=True)
    t['R']=t.pct/abs(t.loc[t.pct<=0,'pct'].median()); t['sys']=lab
    return t
CAND=load(U+'28b178e1-XAU_Momentum_v11_3.csv','CANDIDAT Donchian')
REF =load(U+'89f8f18e-XAU_Momentum_v11.csv','REFERENCE BOS')
def M(s):
    r=s.R.values; p=s.pnl.values; w=r[r>0]; lo=r[r<=0]; eq=np.cumsum(r)
    dd=(eq-np.maximum.accumulate(np.concatenate([[0],eq]))[1:]).min()
    st=0;mx=0
    for x in r: st=st+1 if x<=0 else 0; mx=max(mx,st)
    return dict(n=len(r),wr=100*len(w)/len(r),pf=w.sum()/abs(lo.sum()),E=r.mean(),dd=dd,
                t=r.mean()/(r.std(ddof=1)/np.sqrt(len(r))),tot=r.sum(),streak=mx,net=p.sum())
def line(lab,m):
    print(f"  {lab:34s} n={m['n']:4d} WR={m['wr']:5.1f}% PF={m['pf']:6.3f} E={m['E']:+.3f}R DD={m['dd']:6.1f}R "
          f"t={m['t']:+5.2f} serie={m['streak']:2d} tot={m['tot']:+6.1f}R net={m['net']:+7.0f}EUR")
CUT=pd.Timestamp('2022-04-29')
print("="*118)
print("VERDICT — LE CANDIDAT SUR DONNEES INEDITES (2020-04 -> 2022-04)")
print("="*118)
for lab,seg in [('*** 2020-2022 : JAMAIS UTILISE ***',lambda t:t[t.dt<CUT]),
                ('2022-2026 : deja utilise',lambda t:t[t.dt>=CUT]),
                ('ENSEMBLE',lambda t:t)]:
    print(f"\n{lab}")
    a,b=seg(REF),seg(CAND)
    if len(a)<20 or len(b)<20: print('  echantillon insuffisant'); continue
    mr,mc=M(a),M(b); line('REFERENCE  (BOS + 5 filtres)',mr); line('CANDIDAT   (Donchian + 3)',mc)
    tt,pv=stats.ttest_ind(b.R.values,a.R.values,equal_var=False)
    rng=np.random.default_rng(21)
    bs=np.array([rng.choice(b.R.values,len(b)).mean()-rng.choice(a.R.values,len(a)).mean() for _ in range(10000)])
    print(f"  {'ecart':34s} dE={mc['E']-mr['E']:+.3f}R  p={pv:.3f}  IC95 [{np.percentile(bs,2.5):+.3f} ; {np.percentile(bs,97.5):+.3f}]"
          f"  P(candidat mieux)={100*np.mean(bs>0):.0f}%  dPF={mc['pf']-mr['pf']:+.3f}  dDD={mc['dd']-mr['dd']:+.1f}R")
print("\n"+"="*118)
print("PAR ANNEE")
print("="*118)
print(f"{'annee':>6s} | {'REFERENCE':^34s} | {'CANDIDAT':^34s}")
print(f"{'':6s} | {'n':>4s} {'WR':>6s} {'PF':>6s} {'E':>7s} {'tot':>7s} | {'n':>4s} {'WR':>6s} {'PF':>6s} {'E':>7s} {'tot':>7s}")
for y in sorted(set(REF.dt.dt.year)|set(CAND.dt.dt.year)):
    a=REF[REF.dt.dt.year==y]; b=CAND[CAND.dt.dt.year==y]
    if len(a)<15 or len(b)<15: continue
    ma,mb=M(a),M(b)
    print(f"{y:6d} | {ma['n']:4d} {ma['wr']:5.1f}% {ma['pf']:6.3f} {ma['E']:+7.3f} {ma['tot']:+7.1f} | "
          f"{mb['n']:4d} {mb['wr']:5.1f}% {mb['pf']:6.3f} {mb['E']:+7.3f} {mb['tot']:+7.1f}")
print(f"\nperiode candidat : {CAND.dt.min()} -> {CAND.dt.max()}")
print(f"directions candidat : {CAND.dir.value_counts().to_dict()}")
