import sys, numpy as np, pandas as pd
sys.path.insert(0,'.')
from v11sim import *
U='/root/.claude/uploads/b22822dc-6a41-522c-931f-c596aee488bc/'
df=load_mt5(U+'4b5607af-XAUUSD_M15_202204290100_202608041500.csv')
L,S,a,_=v11_signals(df); ax=adx_pct(df)
P=ExitPlan
def sim(sl,ts,td):
    return simulate(df,a,L,S,P(sl_atr=sl,tp1_r=99,tp2_r=99,tp3_r=99,part1=0,part2=0,
                    breakeven_after_tp1=False,trail_r=td,trail_start_r=ts),COSTS)
def M(t):
    r=t.R.values; w=r[r>0]; lo=r[r<=0]; eq=np.cumsum(r)
    dd=(eq-np.maximum.accumulate(np.concatenate([[0],eq]))[1:]).min()
    return len(r),100*len(w)/len(r),w.sum()/abs(lo.sum()),r.mean(),dd,r.mean()/(r.std(ddof=1)/np.sqrt(len(r)))
def wf(t,k=4):
    """walk-forward : E par quart chronologique"""
    idx=np.array_split(np.arange(len(t)),k)
    return [t.R.values[i].mean() for i in idx]

print("A) GRADIENT DE LA DISTANCE DE TRAILING (armement 1.5 R, stop 2.5 ATR)")
print(f"{'trail':>7s} {'n':>4s} {'WR':>6s} {'PF':>7s} {'E':>8s} {'DD':>7s} {'t':>6s}   walk-forward par quart")
for td in [0.15,0.20,0.25,0.30,0.40,0.50,0.70]:
    t=sim(2.5,1.5,td); n,w,pf,e,dd,ts_=M(t)
    print(f"{td:7.2f} {n:4d} {w:5.1f}% {pf:7.3f} {e:+8.3f} {dd:7.1f} {ts_:+6.2f}   "+" ".join(f"{x:+.2f}" for x in wf(t)))

print("\nB) GRADIENT DU STOP (trailing 1.5/0.3)")
print(f"{'stop':>7s} {'n':>4s} {'WR':>6s} {'PF':>7s} {'E':>8s} {'DD':>7s} {'t':>6s}   walk-forward par quart")
for sl in [2.0,2.25,2.5,2.75,3.0,3.5,4.0]:
    t=sim(sl,1.5,0.3); n,w,pf,e,dd,ts_=M(t)
    print(f"{sl:7.2f} {n:4d} {w:5.1f}% {pf:7.3f} {e:+8.3f} {dd:7.1f} {ts_:+6.2f}   "+" ".join(f"{x:+.2f}" for x in wf(t)))

print("\nC) COMBINAISONS")
print(f"{'config':30s} {'n':>4s} {'WR':>6s} {'PF':>7s} {'E':>8s} {'DD':>7s} {'t':>6s}   walk-forward")
for sl,ts_,td,lab in [(2.5,1.5,0.3,'REFERENCE v11'),(2.5,1.5,0.2,'trail 0.2'),(3.0,1.5,0.3,'stop 3.0'),
                      (3.0,1.5,0.2,'stop 3.0 + trail 0.2'),(3.5,1.5,0.2,'stop 3.5 + trail 0.2')]:
    t=sim(sl,ts_,td); n,w,pf,e,dd,tt=M(t)
    print(f"{lab:30s} {n:4d} {w:5.1f}% {pf:7.3f} {e:+8.3f} {dd:7.1f} {tt:+6.2f}   "+" ".join(f"{x:+.2f}" for x in wf(t)))

print("\nD) LE FILTRE ADX REPRODUIT-IL SUR LE MOTEUR PYTHON ? (independant du Pine)")
t=sim(2.5,1.5,0.3); t['ax']=ax.reindex(t.t_in).values; t=t[t.ax.notna()]
print(f"{'quintile ADX':16s} {'n':>4s} {'WR':>6s} {'PF':>7s} {'E':>8s}")
q=pd.qcut(t.ax,5,labels=False)
for i in range(5):
    s=t[q==i]; r=s.R.values; w=r[r>0]; lo=r[r<=0]
    print(f"quintile {i+1:<8d} {len(r):4d} {100*len(w)/len(r):5.1f}% {w.sum()/abs(lo.sum()):7.3f} {r.mean():+8.3f}")
m=t.ax<=0.5
print(f"\n  sans filtre : n={len(t)} PF={t.R[t.R>0].sum()/abs(t.R[t.R<=0].sum()):.3f} E={t.R.mean():+.3f}")
print(f"  ADX bas     : n={int(m.sum())} PF={t.R[m&(t.R>0)].sum()/abs(t.R[m&(t.R<=0)].sum()):.3f} E={t.R[m].mean():+.3f}")
print(f"  ADX haut    : n={int((~m).sum())} PF={t.R[~m&(t.R>0)].sum()/abs(t.R[~m&(t.R<=0)].sum()):.3f} E={t.R[~m].mean():+.3f}")
from scipy import stats
tt,pv=stats.ttest_ind(t.R[m],t.R[~m],equal_var=False)
print(f"  ecart = {t.R[m].mean()-t.R[~m].mean():+.3f} R   t={tt:+.2f}  p={pv:.4f}")
print("  walk-forward du filtre (E ADXbas - E ADXhaut par quart) :")
idx=np.array_split(np.arange(len(t)),4)
for i,ii in enumerate(idx):
    s=t.iloc[ii]; mm=s.ax<=0.5
    print(f"    quart {i+1} ({s.t_in.min().date()} -> {s.t_in.max().date()}) : {s.R[mm].mean()-s.R[~mm].mean():+.3f} R  (n={int(mm.sum())}/{len(s)})")
