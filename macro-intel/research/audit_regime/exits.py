import sys, numpy as np, pandas as pd
sys.path.insert(0,'.')
from v11sim import *
U='/root/.claude/uploads/b22822dc-6a41-522c-931f-c596aee488bc/'
df=load_mt5(U+'4b5607af-XAUUSD_M15_202204290100_202608041500.csv')
L,S,a,trend=v11_signals(df); ax=adx_pct(df)

def run(plan,lab,costs=COSTS):
    t=simulate(df,a,L,S,plan,costs)
    r=t.R.values; w=r[r>0]; lo=r[r<=0]
    eq=np.cumsum(r); dd=(eq-np.maximum.accumulate(np.concatenate([[0],eq]))[1:]).min()
    return dict(nom=lab,n=len(r),wr=100*len(w)/len(r),pf=w.sum()/abs(lo.sum()),
                E=r.mean(),dd=dd,t=r.mean()/(r.std(ddof=1)/np.sqrt(len(r))),tot=r.sum()), t

P=ExitPlan
V=[
 (P(sl_atr=2.5,tp1_r=99,tp2_r=99,tp3_r=99,part1=0,part2=0,breakeven_after_tp1=False,trail_r=0.3,trail_start_r=1.5),'E0 REFERENCE v11 (trailing 1.5/0.3)'),
 (P(sl_atr=2.5,tp1_r=1.0,tp2_r=99,tp3_r=99,part1=1.0,part2=0,breakeven_after_tp1=False,trail_r=0),'E1 TP fixe 1 R'),
 (P(sl_atr=2.5,tp1_r=2.0,tp2_r=99,tp3_r=99,part1=1.0,part2=0,breakeven_after_tp1=False,trail_r=0),'E2 TP fixe 2 R'),
 (P(sl_atr=2.5,tp1_r=3.0,tp2_r=99,tp3_r=99,part1=1.0,part2=0,breakeven_after_tp1=False,trail_r=0),'E3 TP fixe 3 R'),
 (P(sl_atr=2.5,tp1_r=1.0,tp2_r=2.0,tp3_r=99,part1=0.5,part2=0.5,breakeven_after_tp1=True,trail_r=0),'E4 50% a 1R + 50% a 2R + BE'),
 (P(sl_atr=2.5,tp1_r=1.0,tp2_r=99,tp3_r=99,part1=0.5,part2=0,breakeven_after_tp1=False,trail_r=0.3,trail_start_r=1.5),'E5 50% a 1R + trailing'),
 (P(sl_atr=2.5,tp1_r=2.0,tp2_r=99,tp3_r=99,part1=0.5,part2=0,breakeven_after_tp1=False,trail_r=0.3,trail_start_r=1.5),'E6 50% a 2R + trailing'),
 (P(sl_atr=2.5,tp1_r=1.0,tp2_r=99,tp3_r=99,part1=0.0,part2=0,breakeven_after_tp1=True,trail_r=0.3,trail_start_r=1.5),'E7 BE a 1R + trailing'),
 (P(sl_atr=2.0,tp1_r=99,tp2_r=99,tp3_r=99,part1=0,part2=0,breakeven_after_tp1=False,trail_r=0.3,trail_start_r=1.5),'E8 stop 2.0 ATR'),
 (P(sl_atr=3.0,tp1_r=99,tp2_r=99,tp3_r=99,part1=0,part2=0,breakeven_after_tp1=False,trail_r=0.3,trail_start_r=1.5),'E9 stop 3.0 ATR'),
 (P(sl_atr=2.5,tp1_r=99,tp2_r=99,tp3_r=99,part1=0,part2=0,breakeven_after_tp1=False,trail_r=0.5,trail_start_r=1.0),'E10 trailing 1.0/0.5'),
 (P(sl_atr=2.5,tp1_r=99,tp2_r=99,tp3_r=99,part1=0,part2=0,breakeven_after_tp1=False,trail_r=0.3,trail_start_r=2.0),'E11 trailing 2.0/0.3'),
 (P(sl_atr=2.5,tp1_r=99,tp2_r=99,tp3_r=99,part1=0,part2=0,breakeven_after_tp1=False,trail_r=0.2,trail_start_r=1.5),'E12 trailing 1.5/0.2'),
]
print("ETAPE 4 — SORTIES (meme flux de signaux, cout 0.20 $/oz, 2022-2026)\n")
print(f"{'variante':38s} {'n':>4s} {'WR':>6s} {'PF':>7s} {'E':>8s} {'DD(R)':>8s} {'t':>6s} {'R tot':>8s}")
print("-"*95)
res={}
for plan,lab in V:
    m,t=run(plan,lab); res[lab]=(m,t)
    print(f"{lab:38s} {m['n']:4d} {m['wr']:5.1f}% {m['pf']:7.3f} {m['E']:+8.3f} {m['dd']:8.1f} {m['t']:+6.2f} {m['tot']:+8.1f}")
print("-"*95)
import pickle; pickle.dump({k:v[1] for k,v in res.items()},open('exitruns.pkl','wb'))
