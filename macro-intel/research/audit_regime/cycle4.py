import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0,'.')
from core_import import *
from scipy import stats
df,K=pickle.load(open('lab.pkl','rb'))
c,h,l=df.close,df.high,df.low
FULL=((K['htf']==True)&(c>K['vwap'])&(K['biasD']==True)&(K['biasW']==True)&(c>K['poc']),
      (K['htf']==False)&(c<K['vwap'])&(K['biasD']==False)&(K['biasW']==False)&(c<K['poc']))
def don(n): return (c>h.shift().rolling(n).max()).fillna(False),(c<l.shift().rolling(n).min()).fillna(False)
def ev(tu,td,al,lab,sl=2.5,td_=0.3,ts=1.5):
    L=cooldown((tu&al[0]).fillna(False)); S=cooldown((td&al[1]).fillna(False))
    t=simulate(df,K['atr'],L,S,ExitPlan(sl_atr=sl,tp1_r=99,tp2_r=99,tp3_r=99,part1=0,part2=0,
               breakeven_after_tp1=False,trail_r=td_,trail_start_r=ts),COSTS)
    m=metrics(t,lab)
    if m.get('n',0)>=30:
        q=[metrics(t.iloc[i],'')['E'] for i in np.array_split(np.arange(len(t)),4)]
        m['q']=q; m['pos']=sum(1 for x in q if x>0)
    return t,m
def line(m,q=True):
    if m.get('n',0)<30: print(f"  {m['nom']:26s} trop peu"); return
    s=f"  {m['nom']:26s} n={m['n']:4d} WR={m['wr']:5.1f}% PF={m['pf']:6.3f} E={m['E']:+.3f} DD={m['dd']:6.1f} tot={m['tot']:+6.1f}R t={m['t']:+5.2f}"
    if q: s+=f" | quarts "+" ".join(f"{x:+.2f}" for x in m['q'])+f" ({m['pos']}/4)"
    print(s)

print("="*126)
print("CYCLE 4 — LE DECLENCHEUR DONCHIAN EST-IL UN PIC OU UN PLATEAU ?")
print("="*126)
print("(un vrai effet donne un PLATEAU large ; un pic isole est du bruit)\n")
for n in [16,24,32,40,48,56,64,80,96,128]:
    tu,td=don(n); _,m=ev(tu,td,FULL,f'Donchian {n} ({n*15/60:.0f} h)'); line(m)
print()
_,m=ev(K['bosUp'],K['bosDn'],FULL,'BOS (actuel)'); line(m)

print("\n"+"="*126)
print("CYCLE 4b — LE BOS APPORTE-T-IL QUELQUE CHOSE QUE DONCHIAN N'A PAS ?")
print("="*126)
tu48,td48=don(48)
combos={'BOS seul':(K['bosUp'],K['bosDn']),'Donchian 48 seul':(tu48,td48),
        'BOS ET Donchian':((K['bosUp']&tu48),(K['bosDn']&td48)),
        'BOS OU Donchian':((K['bosUp']|tu48),(K['bosDn']|td48)),
        'Donchian SANS BOS':((tu48&~K['bosUp']),(td48&~K['bosDn'])),
        'BOS SANS Donchian':((K['bosUp']&~tu48),(K['bosDn']&~td48))}
for k,(tu,td) in combos.items():
    _,m=ev(tu,td,FULL,k); line(m)

print("\n"+"="*126)
print("CYCLE 4c — TEST DIRECT : Donchian 48 est-il MEILLEUR que BOS, statistiquement ?")
print("="*126)
tB,_=ev(K['bosUp'],K['bosDn'],FULL,'B'); tD,_=ev(tu48,td48,FULL,'D')
rB,rD=tB.R.values,tD.R.values
tt,pv=stats.ttest_ind(rD,rB,equal_var=False)
rng=np.random.default_rng(8)
bs=[rng.choice(rD,len(rD)).mean()-rng.choice(rB,len(rB)).mean() for _ in range(10000)]
print(f"  ecart d'esperance Donchian - BOS = {rD.mean()-rB.mean():+.3f} R   t={tt:+.2f}  p={pv:.3f}")
print(f"  IC95 [{np.percentile(bs,2.5):+.3f} ; {np.percentile(bs,97.5):+.3f}]   P(Donchian meilleur) = {100*np.mean(np.array(bs)>0):.1f}%")
print("  => l'ecart d'ESPERANCE n'est pas significatif. Ce qui differe, c'est la STABILITE :")
print(f"     BOS      : apprentissage {metrics(tB[tB.t_in<'2024-08-01'],'')['E']:+.3f}  validation {metrics(tB[tB.t_in>='2024-08-01'],'')['E']:+.3f}"
      f"   ecart {metrics(tB[tB.t_in>='2024-08-01'],'')['E']-metrics(tB[tB.t_in<'2024-08-01'],'')['E']:+.3f}")
print(f"     Donchian : apprentissage {metrics(tD[tD.t_in<'2024-08-01'],'')['E']:+.3f}  validation {metrics(tD[tD.t_in>='2024-08-01'],'')['E']:+.3f}"
      f"   ecart {metrics(tD[tD.t_in>='2024-08-01'],'')['E']-metrics(tD[tD.t_in<'2024-08-01'],'')['E']:+.3f}")
