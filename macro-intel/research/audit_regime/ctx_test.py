import pandas as pd, numpy as np
from scipy import stats
cov=pd.read_pickle('cov15.pkl'); R=cov.R.values; pnl=cov.pnl.values; d=cov.dir.values
base_E=R.mean(); base_PF=pnl[pnl>0].sum()/-pnl[pnl<=0].sum()
print(f"REFERENCE : n={len(cov)}  WR={100*(pnl>0).mean():.1f}%  PF={base_PF:.3f}  E={base_E:+.3f} R\n")

F={
 'F01 exclure session Asie (00-07)'        : cov.h.values>=7,
 'F02 garder Londres+Overlap (07-16)'      : (cov.h.values>=7)&(cov.h.values<16),
 'F03 garder Overlap+NY (12-21)'           : (cov.h.values>=12)&(cov.h.values<21),
 'F04 exclure la cloture (>=21)'           : cov.h.values<21,
 'F05 exclure lundi'                       : cov.dow.values!=0,
 'F06 exclure vendredi'                    : cov.dow.values!=4,
 'F07 exclure marche mort (ATRpct<0.25)'   : cov.atrpct.values>=0.25,
 'F08 exclure vol extreme (ATRpct>0.75)'   : cov.atrpct.values<=0.75,
 'F09 ADX bas = range (ADXpct<=0.50)'      : cov.adxpct.values<=0.50,
 'F10 ADX haut = tendance (ADXpct>0.50)'   : cov.adxpct.values>0.50,
 'F11 proche du POC (<3 ATR)'              : np.abs(cov.pocdist.values)<3.0,
 'F12 discount/premium favorable'          : np.where(d==1,cov.pos.values<0.5,cov.pos.values>0.5),
}
def blk(m):
    r,p=R[m],pnl[m]
    if len(r)<20: return None
    gl=-p[p<=0].sum()
    return dict(n=len(r),wr=100*(p>0).mean(),pf=p[p>0].sum()/gl if gl>0 else np.inf,E=r.mean())
print(f"{'filtre':40s} {'garde':>6s} {'n':>4s} {'WR':>6s} {'PF':>7s} {'E':>8s} {'ΔE':>7s} {'t':>6s} {'p':>7s}")
print("-"*100)
rows=[]
for k,m in F.items():
    m=np.asarray(m,bool); a=blk(m); b=blk(~m)
    if a is None or b is None: print(f"{k:40s} groupe trop petit"); continue
    t,p=stats.ttest_ind(R[m],R[~m],equal_var=False); rows.append((k,m,a,b,t,p))
    print(f"{k:40s} {100*m.mean():5.1f}% {a['n']:4d} {a['wr']:5.1f}% {a['pf']:7.3f} {a['E']:+8.3f} "
          f"{a['E']-base_E:+7.3f} {t:+6.2f} {p:7.4f}")
print("-"*100)
ps=np.array([r[5] for r in rows]); order=np.argsort(ps); mn=len(ps); crit=(np.arange(1,mn+1)/mn)*0.10
print("\nBenjamini-Hochberg (FDR 10%) sur les 12 tests :")
surv=[]
for rank,i in enumerate(order):
    ok=ps[i]<=crit[rank]
    if ok: surv.append(rows[i])
    print(f"  {rows[i][0]:40s} p={ps[i]:.4f}  seuil={crit[rank]:.4f}  {'RETENU' if ok else '—'}")
if not surv: print("\n  => aucun filtre ne survit.")
np.save('surv.npy',np.array([r[0] for r in surv],dtype=object),allow_pickle=True)
