import sys, numpy as np, pandas as pd
sys.path.insert(0,'.')
from v11sim import *
U='/root/.claude/uploads/b22822dc-6a41-522c-931f-c596aee488bc/'
df=load_mt5(U+'4b5607af-XAUUSD_M15_202204290100_202608041500.csv')
L,S,a,_=v11_signals(df)
P=ExitPlan
def run(sl,tp):
    t=simulate(df,a,L,S,P(sl_atr=sl,tp1_r=tp,tp2_r=99,tp3_r=99,part1=1.0,part2=0,
               breakeven_after_tp1=False,trail_r=0),COSTS)
    r=t.R.values; w=r[r>0]; lo=r[r<=0]
    if len(lo)==0 or len(r)<50: return None
    eq=np.cumsum(r); dd=(eq-np.maximum.accumulate(np.concatenate([[0],eq]))[1:]).min()
    return dict(n=len(r),wr=100*len(w)/len(r),pf=w.sum()/abs(lo.sum()),E=r.mean(),dd=dd,
                rr=w.mean()/abs(lo.mean()))
print("FRONTIERE WIN RATE / PROFIT FACTOR — 56 combinaisons stop x TP")
print("(TP en multiples du risque ; stop en ATR ; couts 0.20 $/oz)\n")
print(f"{'stop':>5s} {'TP':>5s} {'n':>4s} {'WR':>7s} {'PF':>7s} {'E':>8s} {'gain/perte':>11s} {'DD(R)':>7s}")
best=[]
for sl in [1.0,1.5,2.0,2.5,3.0,4.0,6.0,8.0]:
    for tp in [0.25,0.4,0.5,0.75,1.0,1.5,2.0]:
        m=run(sl,tp)
        if m is None: continue
        best.append((sl,tp,m))
        flag=''
        if m['wr']>=65: flag+=' <-WR OK'
        if m['pf']>=2.0: flag+=' <-PF OK'
        print(f"{sl:5.1f} {tp:5.2f} {m['n']:4d} {m['wr']:6.1f}% {m['pf']:7.3f} {m['E']:+8.3f} {m['rr']:11.2f} {m['dd']:7.1f}{flag}")

print("\n" + "="*78)
w65=[b for b in best if b[2]['wr']>=65]
pf2=[b for b in best if b[2]['pf']>=2.0]
both=[b for b in best if b[2]['wr']>=65 and b[2]['pf']>=2.0]
print(f"combinaisons atteignant WR >= 65 %        : {len(w65)}")
if w65:
    b=max(w65,key=lambda x:x[2]['pf'])
    print(f"   la MEILLEURE d'entre elles : stop {b[0]} ATR / TP {b[1]} R -> WR {b[2]['wr']:.1f}%  PF {b[2]['pf']:.3f}  E {b[2]['E']:+.3f} R")
print(f"combinaisons atteignant PF >= 2.0          : {len(pf2)}")
if pf2:
    b=max(pf2,key=lambda x:x[2]['wr'])
    print(f"   celle au meilleur WR : stop {b[0]} ATR / TP {b[1]} R -> WR {b[2]['wr']:.1f}%  PF {b[2]['pf']:.3f}")
print(f"combinaisons atteignant LES DEUX          : {len(both)}")
b=max(best,key=lambda x:x[2]['pf'])
print(f"\nPF maximum atteignable, toutes combinaisons : {b[2]['pf']:.3f} (stop {b[0]} / TP {b[1]}, WR {b[2]['wr']:.1f}%)")
b=max(best,key=lambda x:x[2]['wr'])
print(f"WR maximum atteignable, toutes combinaisons : {b[2]['wr']:.1f}% (stop {b[0]} / TP {b[1]}, PF {b[2]['pf']:.3f})")
