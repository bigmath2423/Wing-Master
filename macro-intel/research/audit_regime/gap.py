import sys, numpy as np, pandas as pd
sys.path.insert(0,'.')
from v11sim import *
U='/root/.claude/uploads/b22822dc-6a41-522c-931f-c596aee488bc/'
df=load_mt5(U+'4b5607af-XAUUSD_M15_202204290100_202608041500.csv')
L,S,a,_=v11_signals(df); P=ExitPlan
def run(sl,tp=None,ts=1.5,td=0.3):
    pl=P(sl_atr=sl,tp1_r=tp if tp else 99,tp2_r=99,tp3_r=99,part1=1.0 if tp else 0,part2=0,
         breakeven_after_tp1=False,trail_r=0 if tp else td,trail_start_r=ts)
    t=simulate(df,a,L,S,pl,COSTS); r=t.R.values
    if len(r)<40: return None
    w=r[r>0]; lo=r[r<=0]; eq=np.cumsum(r)
    dd=(eq-np.maximum.accumulate(np.concatenate([[0],eq]))[1:]).min()
    q=[r[i].mean() for i in np.array_split(np.arange(len(r)),4)]
    return dict(n=len(r),wr=100*len(w)/len(r),pf=w.sum()/abs(lo.sum()),E=r.mean(),dd=dd,
                bars=t.bars.median(),q=q,tot=r.sum())

print("LEVIER 1 — ELARGIR LE STOP (TP fixe 2 R). Le gradient continue-t-il ?")
print(f"{'stop':>6s} {'n':>4s} {'WR':>7s} {'PF':>7s} {'E':>8s} {'DD(R)':>7s} {'duree':>7s}  walk-forward par quart")
for sl in [2.5,4.0,6.0,8.0,10.0,12.0,16.0,20.0]:
    m=run(sl,tp=2.0)
    if m is None: print(f"{sl:6.1f}  echantillon trop petit"); continue
    print(f"{sl:6.1f} {m['n']:4d} {m['wr']:6.1f}% {m['pf']:7.3f} {m['E']:+8.3f} {m['dd']:7.1f} {m['bars']:7.0f}  "
          +" ".join(f"{x:+.2f}" for x in m['q']))

print("\nLEVIER 1bis — meme chose en trailing (pas de TP)")
print(f"{'stop':>6s} {'n':>4s} {'WR':>7s} {'PF':>7s} {'E':>8s} {'DD(R)':>7s} {'duree':>7s}  walk-forward")
for sl in [2.5,4.0,6.0,8.0,12.0,16.0]:
    m=run(sl)
    if m is None: continue
    print(f"{sl:6.1f} {m['n']:4d} {m['wr']:6.1f}% {m['pf']:7.3f} {m['E']:+8.3f} {m['dd']:7.1f} {m['bars']:7.0f}  "
          +" ".join(f"{x:+.2f}" for x in m['q']))

print("\n\nLEVIER 2 — SELECTIVITE : combien de pertes faudrait-il eviter pour un PF de 2 ?")
t=simulate(df,a,L,S,P(sl_atr=2.5,tp1_r=99,tp2_r=99,tp3_r=99,part1=0,part2=0,
           breakeven_after_tp1=False,trail_r=0.3,trail_start_r=1.5),COSTS)
r=t.R.values; w=r[r>0]; lo=np.sort(r[r<=0])     # pertes triees de la pire a la moins pire
print(f"   base : PF {w.sum()/abs(lo.sum()):.3f}  ({len(w)} gains, {len(lo)} pertes)")
for frac in [0.10,0.20,0.30,0.40,0.50]:
    k=int(len(lo)*frac)
    print(f"   en supprimant les {frac:.0%} PIRES pertes ({k:3d} trades) -> PF {w.sum()/abs(lo[k:].sum()):.3f}")
for frac in [0.10,0.20,0.30,0.40,0.50]:
    k=int(len(lo)*frac)
    idx=np.random.default_rng(1).choice(len(lo),len(lo)-k,replace=False)
    print(f"   en supprimant {frac:.0%} de pertes AU HASARD          -> PF {w.sum()/abs(lo[idx].sum()):.3f}")

print("\n\nLEVIER 3 — PRECISION D'ENTREE REQUISE")
print("   A gain/perte constant (rapport 1.64), quel win rate donne PF 2 ?")
rr=w.mean()/abs(lo.mean())
wr_need=2.0/(2.0+rr)
print(f"   -> WR requis = {100*wr_need:.1f} %   (actuel {100*len(w)/len(r):.1f} %)")
print(f"   soit {100*(wr_need-len(w)/len(r)):.1f} points de precision directionnelle en plus.")
