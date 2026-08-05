import sys, pickle, itertools, numpy as np, pandas as pd
sys.path.insert(0,'.')
from core_import import *
from scipy import stats
df,K=pickle.load(open('lab.pkl','rb'))
c,h,l=df.close,df.high,df.low
def don(n): return (c>h.shift().rolling(n).max()).fillna(False),(c<l.shift().rolling(n).min()).fillna(False)
F={'htf':(K['htf']==True,K['htf']==False),'vwap':(c>K['vwap'],c<K['vwap']),
   'biasD':(K['biasD']==True,K['biasD']==False),'biasW':(K['biasW']==True,K['biasW']==False),
   'poc':(c>K['poc'],c<K['poc'])}
def ev(trig,on,lab,sl=2.5,n=48):
    tu,td=don(n) if trig=='don' else (K['bosUp'],K['bosDn'])
    aL=pd.Series(True,index=df.index); aS=pd.Series(True,index=df.index)
    for k in on: aL&=F[k][0].fillna(False); aS&=F[k][1].fillna(False)
    t=simulate(df,K['atr'],cooldown((tu&aL).fillna(False)),cooldown((td&aS).fillna(False)),
        ExitPlan(sl_atr=sl,tp1_r=99,tp2_r=99,tp3_r=99,part1=0,part2=0,
                 breakeven_after_tp1=False,trail_r=0.3,trail_start_r=1.5),COSTS)
    m=metrics(t,lab)
    if m.get('n',0)>=60:
        m['Ea']=metrics(t[t.t_in<'2024-08-01'],'')['E']; m['Eb']=metrics(t[t.t_in>='2024-08-01'],'')['E']
        m['gap']=abs(m['Eb']-m['Ea'])
        q=[metrics(t.iloc[i],'')['E'] for i in np.array_split(np.arange(len(t)),4)]
        m['pos']=sum(1 for x in q if x>0); m['q']=q
    return t,m
print("CYCLE 5 — LE SYSTEME MINIMAL. Critere : total R eleve ET ecart appr/valid FAIBLE.\n")
res=[]
for k in range(1,6):
    for combo in itertools.combinations(F,k):
        t,m=ev('don',list(combo),'+'.join(combo))
        if m.get('n',0)<150 or 'gap' not in m: continue
        res.append(m)
res.sort(key=lambda m:-(m['tot']/max(m['gap'],0.02)))
print(f"{'combinaison':30s} {'n':>4s} {'WR':>6s} {'PF':>6s} {'E':>7s} {'DD':>6s} {'tot':>7s} {'t':>5s} {'appr':>7s} {'valid':>7s} {'ecart':>6s} {'4q':>3s}")
for m in res[:12]:
    print(f"{m['nom']:30s} {m['n']:4d} {m['wr']:5.1f}% {m['pf']:6.3f} {m['E']:+7.3f} {m['dd']:6.1f} {m['tot']:+7.1f} "
          f"{m['t']:+5.2f} {m['Ea']:+7.3f} {m['Eb']:+7.3f} {m['gap']:6.3f} {m['pos']}/4")
_,ref=ev('bos',['htf','vwap','biasD','biasW','poc'],'REFERENCE v11 (BOS + 5)')
print(f"\n{ref['nom']:30s} {ref['n']:4d} {ref['wr']:5.1f}% {ref['pf']:6.3f} {ref['E']:+7.3f} {ref['dd']:6.1f} {ref['tot']:+7.1f} "
      f"{ref['t']:+5.2f} {ref['Ea']:+7.3f} {ref['Eb']:+7.3f} {ref['gap']:6.3f} {ref['pos']}/4")
pickle.dump(res,open('cycle5.pkl','wb'))
