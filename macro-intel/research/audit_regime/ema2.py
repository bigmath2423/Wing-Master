import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0,'.')
from core_import import *
from scipy import stats
df,K=pickle.load(open('lab.pkl','rb'))
c,h,l=df.close,df.high,df.low
d1=c.resample('1D').last().dropna()
def ribD(a,b,cc):
    A,B,C=[d1.ewm(span=n,adjust=False,min_periods=n).mean() for n in (a,b,cc)]
    u=((A>B)&(B>C)).shift(1); d=((A<B)&(B<C)).shift(1)
    return (pd.Series(df.index.normalize().map(u),index=df.index)==True,
            pd.Series(df.index.normalize().map(d),index=df.index)==True)
BOS=(K['bosUp'],K['bosDn'])
BASE=((K['htf']==True)&(c>K['vwap'])&(K['biasD']==True)&(K['biasW']==True)&(c>K['poc']),
      (K['htf']==False)&(c<K['vwap'])&(K['biasD']==False)&(K['biasW']==False)&(c<K['poc']))
def don(n): return (c>h.shift().rolling(n).max()).fillna(False),(c<l.shift().rolling(n).min()).fillna(False)
def run(tu,td,aL,aS):
    return simulate(df,K['atr'],cooldown((tu&aL.fillna(False)).fillna(False)),
        cooldown((td&aS.fillna(False)).fillna(False)),
        ExitPlan(sl_atr=2.5,tp1_r=99,tp2_r=99,tp3_r=99,part1=0,part2=0,
                 breakeven_after_tp1=False,trail_r=0.3,trail_start_r=1.5),COSTS)
def st(t,lab):
    m=metrics(t,lab)
    if m.get('n',0)<50: return None
    m['Ea']=metrics(t[t.t_in<'2024-08-01'],'')['E']; m['Eb']=metrics(t[t.t_in>='2024-08-01'],'')['E']
    m['gap']=abs(m['Eb']-m['Ea'])
    q=[metrics(t.iloc[i],'')['E'] for i in np.array_split(np.arange(len(t)),4)]
    m['pos']=sum(1 for x in q if x>0); return m
def line(m):
    print(f"  {m['nom']:30s} n={m['n']:4d} WR={m['wr']:5.1f}% PF={m['pf']:6.3f} E={m['E']:+.3f} DD={m['dd']:6.1f} "
          f"tot={m['tot']:+6.1f}R t={m['t']:+5.2f} | appr {m['Ea']:+.3f} valid {m['Eb']:+.3f} ecart {m['gap']:.3f} {m['pos']}/4")

print("A) SENSIBILITE AUX PERIODES DU RUBAN D1 — plateau ou pic ?\n")
for tri in [(3,10,30),(5,10,30),(5,15,40),(5,20,50),(8,21,55),(10,20,50),(10,30,60),(5,20,100),(9,26,52)]:
    u,d=ribD(*tri); m=st(run(*BOS,u,d),f'ruban D1 {tri[0]}/{tri[1]}/{tri[2]}')
    if m: line(m)
print("\nB) RECOUVREMENT AVEC CE QUE LE SYSTEME A DEJA\n")
u,d=ribD(5,20,50)
bd=(K['biasD']==True); bw=(K['biasW']==True); both=bd&bw
for nm,x in [('biais D1 (EMA20)',bd),('biais W1 (EMA10)',bw),('biais D1 ET W1',both)]:
    inter=(u&x).sum(); print(f"  quand le ruban D1 est haussier, {nm:20s} l est aussi dans {100*inter/max(u.sum(),1):5.1f} % des bougies")
print(f"  correlation des deux conditions (haussier=1) : {np.corrcoef(u.astype(int),both.astype(int))[0,1]:+.3f}")

print("\nC) TEST DIRECT CONTRE LES DEUX SYSTEMES DE REFERENCE\n")
tRef=run(*BOS,BASE[0],BASE[1])
tCan=run(*don(48),(K['htf']==True)&(K['biasD']==True)&(K['biasW']==True),
                  (K['htf']==False)&(K['biasD']==False)&(K['biasW']==False))
tRib=run(*BOS,u,d)
for m in [st(tRef,'v11 (BOS + 5 filtres)'),st(tCan,'Donchian48 + 3'),st(tRib,'BOS + ruban D1 SEUL')]: line(m)
rng=np.random.default_rng(44)
for nm,tb in [('v11',tRef),('Donchian48+3',tCan)]:
    a,b=tRib.R.values,tb.R.values
    tt,pv=stats.ttest_ind(a,b,equal_var=False)
    bs=np.array([rng.choice(a,len(a)).mean()-rng.choice(b,len(b)).mean() for _ in range(10000)])
    bt=np.array([rng.choice(a,len(a)).sum()-rng.choice(b,len(b)).sum() for _ in range(10000)])
    print(f"\n  ruban D1 vs {nm:14s} dE={a.mean()-b.mean():+.3f}R p={pv:.3f} IC95 [{np.percentile(bs,2.5):+.3f} ; {np.percentile(bs,97.5):+.3f}]")
    print(f"  {'':18s} dTotal={a.sum()-b.sum():+.1f}R  IC95 [{np.percentile(bt,2.5):+.1f} ; {np.percentile(bt,97.5):+.1f}]  P(mieux)={100*np.mean(bt>0):.0f}%")
print("\n  Benjamini-Hochberg sur les 18 hypotheses EMA de ce cycle (FDR 10 %) : seuil du 1er rang = 0.0056")

print("\nD) ET AVEC LE DECLENCHEUR DONCHIAN ?\n")
for lab,(tu,td) in [('BOS',BOS),('Donchian 48',don(48))]:
    m=st(run(tu.fillna(False),td.fillna(False),u,d),f'ruban D1 + {lab}')
    if m: line(m)
