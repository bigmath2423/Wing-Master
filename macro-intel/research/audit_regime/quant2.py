import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0,'.')
from core_import import *
from scipy import stats
df,K=pickle.load(open('lab.pkl','rb'))
F=pickle.load(open('quantF.pkl','rb')); keep=pickle.load(open('quantKeep.pkl','rb'))
c,h,l=df.close,df.high,df.low
BASE=((K['htf']==True)&(c>K['vwap'])&(K['biasD']==True)&(K['biasW']==True)&(c>K['poc']),
      (K['htf']==False)&(c<K['vwap'])&(K['biasD']==False)&(K['biasW']==False)&(c<K['poc']))
t=simulate(df,K['atr'],cooldown((K['bosUp']&BASE[0]).fillna(False)),
           cooldown((K['bosDn']&BASE[1]).fillna(False)),
           ExitPlan(sl_atr=2.5,tp1_r=99,tp2_r=99,tp3_r=99,part1=0,part2=0,
                    breakeven_after_tp1=False,trail_r=0.3,trail_start_r=1.5),COSTS)
t['dir']=np.where(t.sens=='long',1,-1)
DIRECTIONNEL={'flux_6','migration_valeur','ib_position'}
for k in keep:
    v=F[k].reindex(t.t_in).values
    t[k]=v*t['dir'].values if k in DIRECTIONNEL else v
R=t.R.values
print(f"Echantillon : {len(t)} trades, esperance {R.mean():+.3f} R\n")
print(f"{'concept':22s} {'n':>4s} {'rho':>7s} {'p':>7s} | {'Q1':>7s} {'Q2':>7s} {'Q3':>7s} {'Q4':>7s} {'Q5':>7s} | {'monotone':>8s}")
print("-"*104)
rows=[]
for k in keep:
    x=t[k].values; ok=np.isfinite(x)
    if ok.sum()<300: print(f"{k:22s} donnees insuffisantes"); continue
    xx,rr=x[ok],R[ok]
    rho,p=stats.spearmanr(xx,rr)
    q=pd.qcut(pd.Series(xx),5,labels=False,duplicates='drop')
    qe=[rr[q==i].mean() for i in range(5)]
    dif=np.diff(qe); mono='oui' if (all(d>0 for d in dif) or all(d<0 for d in dif)) else 'non'
    rows.append((k,p,rho,qe,mono,ok.sum()))
    print(f"{k:22s} {ok.sum():4d} {rho:+7.3f} {p:7.4f} | "+" ".join(f"{e:+7.3f}" for e in qe)+f" | {mono:>8s}")
print("-"*104)
ps=np.array([r[1] for r in rows]); order=np.argsort(ps); m=len(ps)
print(f"\nBenjamini-Hochberg sur les {m} concepts (FDR 10 %) :")
surv=[]
for rank,i in enumerate(order):
    seuil=(rank+1)/m*0.10; ok=ps[i]<=seuil
    if ok: surv.append(rows[i][0])
    print(f"  {rows[i][0]:22s} p={ps[i]:.4f}  seuil={seuil:.4f}  {'RETENU' if ok else '—'}"
          +(f"   (monotone : {rows[i][4]})" if ok else ""))
if not surv: print("\n  => aucun concept ne survit.")
pickle.dump((surv,t),open('quantSurv.pkl','wb'))
