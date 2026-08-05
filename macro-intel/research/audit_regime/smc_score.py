import pandas as pd, numpy as np, re
from scipy import stats
exec(open('smc_verdict.py').read().split('def M(')[0])
def M(s):
    r=s.R.values; w=r[r>0]; lo=r[r<=0]
    return dict(n=len(r),wr=100*len(w)/len(r),pf=(w.sum()/abs(lo.sum())) if lo.sum()<0 else np.inf,E=r.mean())
ts=t[t.score.notna()].copy()
hi=ts[ts.score>=95]
print("LE SOUS-GROUPE 'SCORE >= 95' TIENT-IL DANS LE TEMPS ?\n")
print(f"{'annee':>6s} {'n':>4s} {'WR':>7s} {'PF':>7s} {'E':>8s}   |  {'reste (score<95)':>18s}")
ok=0; tot=0
for y in sorted(ts.dt.dt.year.unique()):
    a=hi[hi.dt.dt.year==y]; b=ts[(ts.dt.dt.year==y)&(ts.score<95)]
    if len(a)<20 or len(b)<20: continue
    ma,mb=M(a),M(b); tot+=1; ok+= ma['E']>mb['E']
    print(f"{y:6d} {ma['n']:4d} {ma['wr']:6.1f}% {ma['pf']:7.3f} {ma['E']:+8.3f}   |  n={mb['n']:3d} PF={mb['pf']:6.3f} E={mb['E']:+.3f}")
print(f"\n  annees ou score>=95 fait mieux : {ok}/{tot}")
a=hi.R.values; b=ts.loc[ts.score<95,'R'].values
tt,pv=stats.ttest_ind(a,b,equal_var=False)
rng=np.random.default_rng(17)
bs=np.array([rng.choice(a,len(a)).mean()-rng.choice(b,len(b)).mean() for _ in range(10000)])
print(f"  ecart score>=95 vs reste = {a.mean()-b.mean():+.3f} R  t={tt:+.2f}  p={pv:.4f}  IC95 [{np.percentile(bs,2.5):+.3f} ; {np.percentile(bs,97.5):+.3f}]")
h=len(ts)//2
for nm,s in [('1re moitie',ts.iloc[:h]),('2e moitie',ts.iloc[h:])]:
    x=s[s.score>=95].R.values; y2=s[s.score<95].R.values
    if len(x)<20 or len(y2)<20: continue
    tt2,pv2=stats.ttest_ind(x,y2,equal_var=False)
    print(f"  {nm} ({s.dt.min().date()} -> {s.dt.max().date()}) : score>=95 {x.mean():+.3f} vs reste {y2.mean():+.3f}  ecart {x.mean()-y2.mean():+.3f}  p={pv2:.3f}")
print("\n  MONOTONIE (le critere qui distingue un effet reel d'un artefact) :")
for lo_,hi_ in [(85,87),(88,90),(91,93),(94,96),(97,100)]:
    s=ts[(ts.score>=lo_)&(ts.score<=hi_)]
    if len(s)>=25: m=M(s); print(f"    score {lo_}-{hi_:3d} : n={m['n']:3d}  PF={m['pf']:6.3f}  E={m['E']:+.3f} R")
