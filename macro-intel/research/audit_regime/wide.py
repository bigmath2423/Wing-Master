import sys, numpy as np, pandas as pd
sys.path.insert(0,'.')
from v11sim import *
U='/root/.claude/uploads/b22822dc-6a41-522c-931f-c596aee488bc/'
df=load_mt5(U+'4b5607af-XAUUSD_M15_202204290100_202608041500.csv')
L,S,a,_=v11_signals(df); P=ExitPlan
def run(sl,tp):
    t=simulate(df,a,L,S,P(sl_atr=sl,tp1_r=tp,tp2_r=99,tp3_r=99,part1=1.0,part2=0,
               breakeven_after_tp1=False,trail_r=0),COSTS)
    return t.R.values,t
def pf(r):
    w=r[r>0]; lo=r[r<=0]
    return w.sum()/abs(lo.sum()) if lo.sum()<0 else np.inf

print("A) GRILLE FINE DU STOP (TP 2 R) — monotone ou en dents de scie ?")
print(f"{'stop':>6s} {'n':>4s} {'PF':>7s} {'IC95 du PF (bootstrap)':>26s} {'E':>8s} {'trades/an':>10s}")
for sl in [6,7,8,9,10,11,12,14,16,18,20]:
    r,_=run(sl,2.0)
    if len(r)<35: print(f"{sl:6.1f} {len(r):4d}  trop peu de trades"); continue
    rng=np.random.default_rng(2)
    bs=[pf(rng.choice(r,len(r))) for _ in range(4000)]
    bs=[x for x in bs if np.isfinite(x)]
    lo_,hi_=np.percentile(bs,[2.5,97.5])
    star=' <- PF 2 atteint' if pf(r)>=2 else ''
    print(f"{sl:6.1f} {len(r):4d} {pf(r):7.3f} {'['+f'{lo_:.2f}':>13s} ; {f'{hi_:.2f}'+']':>10s} {r.mean():+8.3f} {len(r)/4.3:10.0f}{star}")

print("\nB) LE PF 2 EST-IL DISTINGUABLE DU PF ACTUEL ?")
r0,_=run(2.5,2.0); r1,_=run(10.0,2.0)
rng=np.random.default_rng(6)
d=[pf(rng.choice(r1,len(r1)))-pf(rng.choice(r0,len(r0))) for _ in range(4000)]
d=[x for x in d if np.isfinite(x)]
print(f"   ecart de PF (stop 10 - stop 2.5) = {pf(r1)-pf(r0):+.3f}")
print(f"   IC95 [{np.percentile(d,2.5):+.3f} ; {np.percentile(d,97.5):+.3f}]   P(ecart>0) = {100*np.mean(np.array(d)>0):.1f}%")
print(f"   la borne basse depasse-t-elle 2 ? {'OUI' if np.percentile([pf(rng.choice(r1,len(r1))) for _ in range(4000)],2.5)>=2 else 'NON'}")

print("\nC) COMBIEN DE TEMPS LES POSITIONS RESTENT-ELLES OUVERTES ?")
for sl in [2.5,8.0,10.0,16.0]:
    _,t=run(sl,2.0)
    print(f"   stop {sl:4.1f} ATR : duree mediane {t.bars.median():5.0f} bougies = {t.bars.median()*15/60/24:5.1f} jours | "
          f"max {t.bars.max():5.0f} = {t.bars.max()*15/60/24:.0f} jours | {len(t)/4.3:.0f} trades/an")

print("\nD) LE RISQUE REEL EST-IL LE MEME ? (le stop est plus large, la taille plus petite)")
print("   A 1 % de risque par trade, un stop 4x plus large = position 4x plus petite.")
print("   Le drawdown en R est donc directement comparable :")
for sl in [2.5,8.0,10.0,16.0]:
    r,_=run(sl,2.0); eq=np.cumsum(r)
    dd=(eq-np.maximum.accumulate(np.concatenate([[0],eq]))[1:]).min()
    st=0;mx=0
    for x in r: st=st+1 if x<=0 else 0; mx=max(mx,st)
    print(f"   stop {sl:4.1f} : DD {dd:6.1f} R | pire serie {mx:2d} | total {r.sum():+7.1f} R sur 4.3 ans = {r.sum()/4.3:+.1f} R/an")
