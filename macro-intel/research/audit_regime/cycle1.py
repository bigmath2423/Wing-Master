import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0,'.')
from core_import import *
df,K=pickle.load(open('lab.pkl','rb'))
c=df.close; PLAN=ExitPlan(sl_atr=2.5,tp1_r=99,tp2_r=99,tp3_r=99,part1=0,part2=0,
                          breakeven_after_tp1=False,trail_r=0.3,trail_start_r=1.5)
FILT={
 'struct': (K['trend']==1,                K['trend']==-1),
 'htf'   : (K['htf']==True,               K['htf']==False),
 'vwap'  : (c>K['vwap'],                  c<K['vwap']),
 'biasD' : (K['biasD']==True,             K['biasD']==False),
 'biasW' : (K['biasW']==True,             K['biasW']==False),
 'poc'   : (c>K['poc'],                   c<K['poc']),
}
TRIG={'BOS':(K['bosUp'],K['bosDn'])}
def build(trig, on, cd=10):
    tu,td=TRIG[trig]
    aL=pd.Series(True,index=df.index); aS=pd.Series(True,index=df.index)
    for k in on:
        l_,s_=FILT[k]; aL=aL&l_.fillna(False); aS=aS&s_.fillna(False)
    return cooldown((tu&aL).fillna(False)), cooldown((td&aS).fillna(False))
def ev(L,S,lab,plan=PLAN):
    t=simulate(df,K['atr'],L,S,plan,COSTS)
    return t, metrics(t,lab)
ALL=list(FILT)
SEG={'apprentissage 2022-2024':('2022-01-01','2024-08-01'),
     'validation 2024-2026'   :('2024-08-01','2027-01-01')}
def seg(t,lab):
    out={}
    for n,(a,b) in SEG.items():
        s=t[(t.t_in>=a)&(t.t_in<b)]
        out[n]=metrics(s,lab)
    return out

print("="*104)
print("CYCLE 1 — ABLATION : que se passe-t-il si on RETIRE chaque composant ?")
print("="*104)
L,S=build('BOS',ALL); t0,m0=ev(L,S,'SYSTEME COMPLET (6 filtres)')
show(m0); s0=seg(t0,'')
print(f"     {'apprentissage':>16s} PF {s0['apprentissage 2022-2024']['pf']:.3f} E {s0['apprentissage 2022-2024']['E']:+.3f}"
      f"  |  {'validation':>10s} PF {s0['validation 2024-2026']['pf']:.3f} E {s0['validation 2024-2026']['E']:+.3f}\n")
rows=[]
for k in ALL:
    on=[x for x in ALL if x!=k]
    L,S=build('BOS',on); t,m=ev(L,S,f'SANS {k}')
    s=seg(t,'')
    rows.append((k,m,s))
    d=m['E']-m0['E'] if m.get('n',0)>=30 else np.nan
    show(m, f"  dE={d:+.3f}")
    if m.get('n',0)>=30:
        print(f"     {'apprentissage':>16s} PF {s['apprentissage 2022-2024']['pf']:.3f} E {s['apprentissage 2022-2024']['E']:+.3f}"
              f"  |  {'validation':>10s} PF {s['validation 2024-2026']['pf']:.3f} E {s['validation 2024-2026']['E']:+.3f}")
print("\nLecture : dE NEGATIF = retirer le composant DEGRADE => il sert.")
print("          dE POSITIF ou nul = le composant ne sert pas, ou nuit.\n")
print("="*104)
print("CYCLE 1b — SIMPLIFICATION : et si on n'en gardait que quelques-uns ?")
print("="*104)
import itertools
best=[]
for k in range(1,7):
    for combo in itertools.combinations(ALL,k):
        L,S=build('BOS',list(combo)); t,m=ev(L,S,'+'.join(combo))
        if m.get('n',0)<80: continue
        s=seg(t,'')
        a=s['apprentissage 2022-2024']; b=s['validation 2024-2026']
        if a.get('n',0)<30 or b.get('n',0)<30: continue
        best.append((m,a,b,combo))
best.sort(key=lambda x:-x[0]['E'])
print(f"{'combinaison':44s} {'n':>4s} {'WR':>6s} {'PF':>6s} {'E':>7s} {'DD':>7s} | {'E appr':>7s} {'E valid':>8s}")
for m,a,b,combo in best[:14]:
    print(f"{m['nom']:44s} {m['n']:4d} {m['wr']:5.1f}% {m['pf']:6.3f} {m['E']:+7.3f} {m['dd']:7.1f} | "
          f"{a['E']:+7.3f} {b['E']:+8.3f}")
print(f"\n(reference = les 6 filtres : n={m0['n']}, PF {m0['pf']:.3f}, E {m0['E']:+.3f})")
pickle.dump(best,open('cycle1.pkl','wb'))
