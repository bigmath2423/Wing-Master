import sys, numpy as np, pandas as pd
sys.path.insert(0,'.')
from v11sim import *
from scipy import stats
U='/root/.claude/uploads/b22822dc-6a41-522c-931f-c596aee488bc/'
df=load_mt5(U+'4b5607af-XAUUSD_M15_202204290100_202608041500.csv')
L,S,a,_=v11_signals(df)
base=simulate(df,a,L,S,ExitPlan(sl_atr=2.5,tp1_r=99,tp2_r=99,tp3_r=99,part1=0,part2=0,
              breakeven_after_tp1=False,trail_r=0.3,trail_start_r=1.5),COSTS)

print("A) SENSIBILITE AUX REGLAGES DE L'ADX (longueur x fenetre de percentile)")
print(f"{'len':>4s} {'fenetre':>8s} {'n gardes':>9s} {'PF':>7s} {'E':>8s} {'ecart bas-haut':>15s} {'p':>8s}")
for n_ in [10,14,20]:
    for win in [250,500,1000,2000]:
        ax=adx_pct(df,n=n_,win=win)
        t=base.copy(); t['ax']=ax.reindex(t.t_in).values; t=t[t.ax.notna()]
        m=(t.ax<=0.5).values; r=t.R.values
        pf=r[m&(r>0)].sum()/abs(r[m&(r<=0)].sum())
        tt,pv=stats.ttest_ind(r[m],r[~m],equal_var=False)
        print(f"{n_:4d} {win:8d} {int(m.sum()):9d} {pf:7.3f} {r[m].mean():+8.3f} {r[m].mean()-r[~m].mean():+15.3f} {pv:8.4f}")

print("\nB) ADX BRUT (sans percentile) — un seuil FIXE marche-t-il aussi ?")
h,l=df.high,df.low; pc=df.close.shift()
tr=pd.concat([h-l,(h-pc).abs(),(l-pc).abs()],axis=1).max(axis=1)
aw=tr.ewm(alpha=1/14,adjust=False).mean()
up,dn=h.diff(),-l.diff()
p_=np.where((up>dn)&(up>0),up,0.); m_=np.where((dn>up)&(dn>0),dn,0.)
pdi=100*pd.Series(p_,index=df.index).ewm(alpha=1/14,adjust=False).mean()/aw
mdi=100*pd.Series(m_,index=df.index).ewm(alpha=1/14,adjust=False).mean()/aw
adxr=(100*(pdi-mdi).abs()/(pdi+mdi).replace(0,np.nan)).ewm(alpha=1/14,adjust=False).mean()
t=base.copy(); t['adx']=adxr.reindex(t.t_in).values; t=t[t.adx.notna()]
print(f"{'seuil ADX':>10s} {'garde':>7s} {'n':>4s} {'WR':>6s} {'PF':>7s} {'E':>8s} {'p':>8s}")
for thr in [15,18,20,22,25,28,30,35]:
    mm=(t.adx<=thr).values; r=t.R.values
    if mm.sum()<40 or (~mm).sum()<40: continue
    tt,pv=stats.ttest_ind(r[mm],r[~mm],equal_var=False)
    print(f"{thr:10d} {100*mm.mean():6.1f}% {int(mm.sum()):4d} {100*(r[mm]>0).mean():5.1f}% "
          f"{r[mm&(r>0)].sum()/abs(r[mm&(r<=0)].sum()):7.3f} {r[mm].mean():+8.3f} {pv:8.4f}")

print("\nC) CONFUSION AVEC LES MODULES EXISTANTS ?")
ax=adx_pct(df)
t=base.copy(); t['ax']=ax.reindex(t.t_in).values
cov=pd.read_pickle('cov15.pkl')
print("  correlation ADXpct avec les autres variables de contexte (sur les trades reels) :")
for k in ['atrpct','pos','pocdist','biasstr','h1str','body','volrel']:
    c_=cov[['adxpct',k]].dropna()
    print(f"    {k:10s} r = {np.corrcoef(c_.adxpct,c_[k])[0,1]:+.3f}")
print("\n  L'effet survit-il DANS chaque sous-groupe ? (controle des confusions)")
for lab,msk in [('session Asie',cov.h<7),('session Londres+',cov.h>=7),
                ('volatilite basse',cov.atrpct<=0.5),('volatilite haute',cov.atrpct>0.5),
                ('long',cov.dir==1),('short',cov.dir==-1)]:
    s=cov[msk]; mm=(s.adxpct<=0.5).values; r=s.R.values
    if mm.sum()<20 or (~mm).sum()<20: print(f"    {lab:18s} echantillon insuffisant"); continue
    print(f"    {lab:18s} n={len(s):3d}  E bas={r[mm].mean():+.3f}  E haut={r[~mm].mean():+.3f}  ecart={r[mm].mean()-r[~mm].mean():+.3f} R")
