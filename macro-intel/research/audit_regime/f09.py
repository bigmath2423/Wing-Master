import pandas as pd, numpy as np
from scipy import stats
cov=pd.read_pickle('cov15.pkl').reset_index(drop=True)
R=cov.R.values; pnl=cov.pnl.values; ax=cov.adxpct.values
def st(m):
    r,p=R[m],pnl[m]; gl=-p[p<=0].sum()
    return len(r),100*(p>0).mean(),(p[p>0].sum()/gl if gl>0 else np.inf),r.mean()

print("A) MONOTONIE — l'effet doit etre graduel, pas un pic\n")
print(f"{'quintile ADX':18s} {'n':>4s} {'WR':>6s} {'PF':>7s} {'E':>8s}")
q=pd.qcut(cov.adxpct,5,labels=False)
for i in range(5):
    n,w,pf,e=st((q==i).values); print(f"quintile {i+1} {'(bas)' if i==0 else '(haut)' if i==4 else '     ':6s} {n:4d} {w:5.1f}% {pf:7.3f} {e:+8.3f}")

print("\nB) SENSIBILITE AU SEUIL — un effet reel ne depend pas d'un reglage precis\n")
print(f"{'seuil':>8s} {'garde':>7s} {'n':>4s} {'WR':>6s} {'PF':>7s} {'E':>8s} {'ΔE':>7s}")
for thr in [0.35,0.40,0.45,0.50,0.55,0.60,0.65]:
    m=ax<=thr; n,w,pf,e=st(m)
    print(f"{thr:8.2f} {100*m.mean():6.1f}% {n:4d} {w:5.1f}% {pf:7.3f} {e:+8.3f} {e-R.mean():+7.3f}")

print("\nC) APPRENTISSAGE / VALIDATION (coupe chronologique a la moitie)\n")
half=len(cov)//2
for nm,sl in [('apprentissage',slice(0,half)),('validation  ',slice(half,None))]:
    sub=cov.iloc[sl]; r=sub.R.values; p=sub.pnl.values; a=sub.adxpct.values
    m=a<=0.50
    gl1=-p[m&(p<=0)].sum(); gl0=-p[(~m)&(p<=0)].sum()
    t,pv=stats.ttest_ind(r[m],r[~m],equal_var=False)
    print(f"{nm} ({sub.dt.min().date()} -> {sub.dt.max().date()})")
    print(f"   sans filtre : n={len(r):3d} PF={p[p>0].sum()/-p[p<=0].sum():.3f} E={r.mean():+.3f}")
    print(f"   ADX bas     : n={int(m.sum()):3d} PF={p[m&(p>0)].sum()/gl1:.3f} E={r[m].mean():+.3f}")
    print(f"   ADX haut    : n={int((~m).sum()):3d} PF={p[(~m)&(p>0)].sum()/gl0:.3f} E={r[~m].mean():+.3f}")
    print(f"   ecart bas-haut = {r[m].mean()-r[~m].mean():+.3f} R   t={t:+.2f}  p={pv:.4f}\n")

print("D) STABILITE SUR 4 SOUS-PERIODES\n")
print(f"{'periode':26s} {'n':>4s} {'E sans':>8s} {'E ADXbas':>9s} {'ecart':>8s} {'PF sans':>8s} {'PF filtre':>10s}")
cut=np.array_split(np.arange(len(cov)),4)
ok=0
for i,idx in enumerate(cut):
    sub=cov.iloc[idx]; r=sub.R.values; p=sub.pnl.values; m=sub.adxpct.values<=0.50
    gl0=-p[p<=0].sum(); gl1=-p[m&(p<=0)].sum()
    e0,e1=r.mean(),r[m].mean(); ok+= (e1>e0)
    print(f"{str(sub.dt.min().date())+' -> '+str(sub.dt.max().date()):26s} {len(r):4d} {e0:+8.3f} {e1:+9.3f} "
          f"{e1-e0:+8.3f} {p[p>0].sum()/gl0:8.3f} {p[m&(p>0)].sum()/gl1:10.3f}")
print(f"\n   sous-periodes ameliorees : {ok}/4")

print("\nE) DRAWDOWN\n")
for nm,m in [('sans filtre',np.ones(len(cov),bool)),('ADX bas seulement',ax<=0.50)]:
    p=pnl[m]; eq=10000+np.cumsum(p); dd=(eq/np.maximum.accumulate(eq)-1)
    s=0;mx=0
    for x in p: s=s+1 if x<=0 else 0; mx=max(mx,s)
    print(f"   {nm:20s} DD max {100*dd.min():6.2f}%   serie de pertes max {mx:2d}   net {p.sum():+8.0f} EUR   trades/an {len(p)/4.3:.0f}")
