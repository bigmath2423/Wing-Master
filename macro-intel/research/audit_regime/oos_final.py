import pandas as pd, numpy as np
from scipy import stats
t=pd.read_pickle('newrun.pkl')
CUT=pd.Timestamp('2022-04-29')      # debut des donnees que j'ai utilisees pour trouver le filtre
oos=t[t.dt<CUT].copy(); ins=t[t.dt>=CUT].copy()
def blk(s):
    p=s.pnl.values; r=s.R.values; gl=-p[p<=0].sum()
    return len(s),100*(p>0).mean(),(p[p>0].sum()/gl if gl>0 else np.inf),r.mean()
def report(s,lab,thr=50):
    m=(s.adx<=thr).values; r=s.R.values
    if m.sum()<20 or (~m).sum()<20:
        print(f"{lab}: sous-groupes trop petits"); return
    n0,w0,pf0,e0=blk(s); n1,w1,pf1,e1=blk(s[m]); n2,w2,pf2,e2=blk(s[~m])
    tt,pv=stats.ttest_ind(r[m],r[~m],equal_var=False)
    rng=np.random.default_rng(4); bs=[rng.choice(r[m],m.sum()).mean()-rng.choice(r[~m],(~m).sum()).mean() for _ in range(10000)]
    lo,hi=np.percentile(bs,[2.5,97.5])
    print(f"\n{lab}  ({s.dt.min().date()} -> {s.dt.max().date()})")
    print(f"   sans filtre  n={n0:4d}  WR={w0:5.1f}%  PF={pf0:6.3f}  E={e0:+.3f} R")
    print(f"   ADX <= {thr}    n={n1:4d}  WR={w1:5.1f}%  PF={pf1:6.3f}  E={e1:+.3f} R   <- ce que le filtre garde")
    print(f"   ADX >  {thr}    n={n2:4d}  WR={w2:5.1f}%  PF={pf2:6.3f}  E={e2:+.3f} R   <- ce qu'il jette")
    print(f"   ecart {e1-e2:+.3f} R   t={tt:+.2f}   p={pv:.4f}   IC95 [{lo:+.3f} ; {hi:+.3f}]")
    return e1-e2,pv

print("="*84)
print("TEST HORS ECHANTILLON — donnees jamais utilisees pour trouver le filtre")
print("="*84)
report(oos,'*** 2020-04 -> 2022-04 : DONNEES INEDITES ***')
report(ins,'2022-04 -> 2026-07 : donnees deja utilisees')
report(t,'run complet 2020-2026')

print("\n\nPAR ANNEE — l'ecart garde-vs-jete")
print(f"{'annee':8s} {'n':>4s} {'n gardes':>9s} {'E gardes':>9s} {'E jetes':>9s} {'ecart':>8s}")
for y in sorted(t.dt.dt.year.unique()):
    s=t[t.dt.dt.year==y]
    if len(s)<25: continue
    m=(s.adx<=50).values; r=s.R.values
    if m.sum()<8 or (~m).sum()<8: continue
    print(f"{y:8d} {len(s):4d} {int(m.sum()):9d} {r[m].mean():+9.3f} {r[~m].mean():+9.3f} {r[m].mean()-r[~m].mean():+8.3f}")

print("\n\nGRADIENT PAR QUINTILE D'ADX (hors echantillon SEULEMENT)")
q=pd.qcut(oos.adx,5,labels=False,duplicates='drop')
for i in sorted(pd.unique(q.dropna())):
    s=oos[q==i]; n,w,pf,e=blk(s)
    print(f"   quintile {int(i)+1}  n={n:3d}  ADX {s.adx.min():3.0f}-{s.adx.max():3.0f}  WR={w:5.1f}%  PF={pf:6.3f}  E={e:+.3f} R")
