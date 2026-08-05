import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0,'.')
from core_import import *
from scipy import stats
surv,t=pickle.load(open('quantSurv.pkl','rb'))
R=t.R.values
print("A) CONFONDANT TEMPOREL — la variable derive-t-elle simplement avec le temps ?\n")
ti=np.arange(len(t))
for k in ['cout_mouvement','cout_rel','efficience_96']:
    x=t[k].values; ok=np.isfinite(x)
    rt,pt=stats.spearmanr(ti[ok],x[ok])
    rr,pr=stats.spearmanr(x[ok],R[ok])
    print(f"  {k:18s} correlation avec le TEMPS : rho={rt:+.3f} (p={pt:.4f})   |   avec le resultat : rho={rr:+.3f}")
rT,pT=stats.spearmanr(ti,R)
print(f"  {'le resultat lui-meme':18s} correlation avec le TEMPS : rho={rT:+.3f} (p={pT:.4f})")

print("\nB) L'EFFET SURVIT-IL ANNEE PAR ANNEE ? (si c'est du temps, il disparait)\n")
t['an']=t.t_in.dt.year
for k in ['cout_mouvement','cout_rel']:
    print(f"  {k}")
    ok_years=0; tot=0
    for y,s in t.groupby('an'):
        x=s[k].values; r=s.R.values; m=np.isfinite(x)
        if m.sum()<60: continue
        rho,p=stats.spearmanr(x[m],r[m]); tot+=1; ok_years+= (rho<0 and p<0.10)
        print(f"     {y}  n={int(m.sum()):3d}  rho={rho:+.3f}  p={p:.3f}")
    print(f"     annees ou l'effet est present : {ok_years}/{tot}\n")

print("C) EFFET PARTIEL — en neutralisant le temps (correlation partielle)\n")
for k in ['cout_mouvement','cout_rel']:
    x=t[k].values; m=np.isfinite(x)
    xr=stats.rankdata(x[m]); rr=stats.rankdata(R[m]); tr=stats.rankdata(ti[m])
    def resid(a,b): return a-np.polyval(np.polyfit(b,a,1),b)
    rho_p=np.corrcoef(resid(xr,tr),resid(rr,tr))[0,1]
    n=m.sum(); tt=rho_p*np.sqrt((n-3)/(1-rho_p**2)); p=2*(1-stats.norm.cdf(abs(tt)))
    print(f"  {k:18s} rho brut = {stats.spearmanr(x[m],R[m])[0]:+.3f}  ->  rho PARTIEL (temps neutralise) = {rho_p:+.3f}  p={p:.4f}")

print("\nD) TEST PRATIQUE — un filtre bati dessus change-t-il quelque chose ?\n")
for k in ['cout_mouvement','cout_rel']:
    x=t[k].values; m=np.isfinite(x)
    for q in [0.5,0.7]:
        thr=np.nanquantile(x[m],q); sel=m&(x<=thr)
        r1,r0=R[sel],R[m&~(x<=thr)]
        if len(r1)<80 or len(r0)<80: continue
        pf1=r1[r1>0].sum()/abs(r1[r1<=0].sum()); pf0=r0[r0>0].sum()/abs(r0[r0<=0].sum())
        tt,p=stats.ttest_ind(r1,r0,equal_var=False)
        print(f"  {k:18s} garder les {q:.0%} plus BAS : n={len(r1):3d} PF={pf1:.3f} E={r1.mean():+.3f}  |  "
              f"rejetes n={len(r0):3d} PF={pf0:.3f} E={r0.mean():+.3f}  |  ecart {r1.mean()-r0.mean():+.3f} p={p:.3f}")
