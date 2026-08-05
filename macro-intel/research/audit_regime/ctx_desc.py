import pandas as pd, numpy as np
from scipy import stats
cov=pd.read_pickle('cov15.pkl')
cov['h']=cov.dt.dt.hour; cov['dow']=cov.dt.dt.dayofweek
def sess(x): return 'Asie' if x<7 else 'Londres' if x<12 else 'Overlap L/NY' if x<16 else 'New York' if x<21 else 'Cloture'
cov['sess']=cov.h.map(sess)
win=cov[cov.pnl>0]; los=cov[cov.pnl<=0]
print(f"ETAPE 2 — PROFIL DES GAGNANTS ({len(win)}) vs PERDANTS ({len(los)})\n")
print(f"{'variable':26s} {'gagnants':>10s} {'perdants':>10s} {'ecart':>9s} {'t':>7s} {'p':>7s}")
print("-"*76)
for k,lab in [('atrpct','volatilite (pct)'),('adxpct','ADX (pct)'),('pos','position range 24h'),
              ('pos4','position range 4j'),('pocdist','distance POC (ATR)'),('biasstr','force biais D1 (%)'),
              ('h1str','force H1 (%)'),('body','corps bougie (ATR)'),('volrel','volume relatif'),
              ('spread','spread (points)'),('h','heure UTC'),('bars','duree (barres)')]:
    a=win[k].dropna(); b=los[k].dropna()
    if k in('pos','pos4','pocdist','biasstr','h1str','body'):   # orienter selon le sens du trade
        a=(win[k]*win.dir).dropna() if k in('pocdist','biasstr','h1str','body') else a
        b=(los[k]*los.dir).dropna() if k in('pocdist','biasstr','h1str','body') else b
    t,p=stats.ttest_ind(a,b,equal_var=False)
    print(f"{lab:26s} {a.median():10.3f} {b.median():10.3f} {a.median()-b.median():+9.3f} {t:+7.2f} {p:7.4f}")

print("\n\nPAR SESSION (heure UTC)")
print(f"{'session':16s} {'n':>4s} {'part':>6s} {'WR':>6s} {'PF':>7s} {'E':>8s}")
for s in ['Asie','Londres','Overlap L/NY','New York','Cloture']:
    g=cov[cov.sess==s]
    if len(g)<5: continue
    gl=-g.loc[g.pnl<=0,'pnl'].sum()
    print(f"{s:16s} {len(g):4d} {100*len(g)/len(cov):5.1f}% {100*(g.pnl>0).mean():5.1f}% "
          f"{g.loc[g.pnl>0,'pnl'].sum()/gl if gl>0 else np.inf:7.3f} {g.R.mean():+8.3f}")

print("\nPAR JOUR DE LA SEMAINE")
for i,nm in enumerate(['lundi','mardi','mercredi','jeudi','vendredi']):
    g=cov[cov.dow==i]
    if len(g)<5: continue
    gl=-g.loc[g.pnl<=0,'pnl'].sum()
    print(f"{nm:16s} {len(g):4d} {100*len(g)/len(cov):5.1f}% {100*(g.pnl>0).mean():5.1f}% "
          f"{g.loc[g.pnl>0,'pnl'].sum()/gl if gl>0 else np.inf:7.3f} {g.R.mean():+8.3f}")

print("\nPAR REGIME DE VOLATILITE (percentile ATR)")
cov['vq']=pd.qcut(cov.atrpct,4,labels=['tres calme','calme','actif','tres actif'])
for q in cov.vq.cat.categories:
    g=cov[cov.vq==q]; gl=-g.loc[g.pnl<=0,'pnl'].sum()
    print(f"{str(q):16s} {len(g):4d} {100*len(g)/len(cov):5.1f}% {100*(g.pnl>0).mean():5.1f}% "
          f"{g.loc[g.pnl>0,'pnl'].sum()/gl if gl>0 else np.inf:7.3f} {g.R.mean():+8.3f}")

print("\nPAR REGIME DE TENDANCE (percentile ADX)")
cov['aq']=pd.qcut(cov.adxpct,4,labels=['range fort','range','tendance','tendance forte'])
for q in cov.aq.cat.categories:
    g=cov[cov.aq==q]; gl=-g.loc[g.pnl<=0,'pnl'].sum()
    print(f"{str(q):16s} {len(g):4d} {100*len(g)/len(cov):5.1f}% {100*(g.pnl>0).mean():5.1f}% "
          f"{g.loc[g.pnl>0,'pnl'].sum()/gl if gl>0 else np.inf:7.3f} {g.R.mean():+8.3f}")
cov.to_pickle('cov15.pkl')
