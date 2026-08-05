import sys, numpy as np, pandas as pd
sys.path.insert(0,'.')
from v11sim import *
from scipy import stats
U='/root/.claude/uploads/b22822dc-6a41-522c-931f-c596aee488bc/'
df=load_mt5(U+'4b5607af-XAUUSD_M15_202204290100_202608041500.csv')
L,S,a,_=v11_signals(df)
t=simulate(df,a,L,S,ExitPlan(sl_atr=2.5,tp1_r=99,tp2_r=99,tp3_r=99,part1=0,part2=0,
           breakeven_after_tp1=False,trail_r=0.3,trail_start_r=1.5),COSTS)
h,l=df.high,df.low; pc=df.close.shift()
trr=pd.concat([h-l,(h-pc).abs(),(l-pc).abs()],axis=1).max(axis=1)
aw=trr.ewm(alpha=1/14,adjust=False).mean()
up,dn=h.diff(),-l.diff()
p_=np.where((up>dn)&(up>0),up,0.); m_=np.where((dn>up)&(dn>0),dn,0.)
pdi=100*pd.Series(p_,index=df.index).ewm(alpha=1/14,adjust=False).mean()/aw
mdi=100*pd.Series(m_,index=df.index).ewm(alpha=1/14,adjust=False).mean()/aw
adxr=(100*(pdi-mdi).abs()/(pdi+mdi).replace(0,np.nan)).ewm(alpha=1/14,adjust=False).mean()
t['adx']=adxr.reindex(t.t_in).values; t=t[t.adx.notna()].reset_index(drop=True)

def M(r):
    w=r[r>0]; lo=r[r<=0]; eq=np.cumsum(r)
    dd=(eq-np.maximum.accumulate(np.concatenate([[0],eq]))[1:]).min()
    s=0;mx=0
    for x in r: s=s+1 if x<=0 else 0; mx=max(mx,s)
    return dict(n=len(r),wr=100*len(w)/len(r),pf=w.sum()/abs(lo.sum()),E=r.mean(),dd=dd,
                t=r.mean()/(r.std(ddof=1)/np.sqrt(len(r))),tot=r.sum(),streak=mx)
def line(lab,r):
    m=M(r); print(f"{lab:28s} n={m['n']:4d} WR={m['wr']:5.1f}% PF={m['pf']:6.3f} E={m['E']:+.3f}R "
                  f"DD={m['dd']:6.1f}R t={m['t']:+5.2f} serie={m['streak']:2d} tot={m['tot']:+7.1f}R")
    return m
THR=25
mk=(t.adx<=THR).values
print(f"AVANT / APRES — filtre ADX <= {THR} (2022-2026, moteur Python, cout 0.20 $/oz)\n")
b=line("AVANT (v11 actuelle)",t.R.values)
a2=line(f"APRES (ADX<={THR})",t.R.values[mk])
line(f"  [rejete : ADX>{THR}]",t.R.values[~mk])
print(f"\n  trades/an : {b['n']/4.3:.0f} -> {a2['n']/4.3:.0f}   (retention {100*mk.mean():.1f}%)")
print(f"  PF {b['pf']:.3f} -> {a2['pf']:.3f}   WR {b['wr']:.1f}% -> {a2['wr']:.1f}%   "
      f"E {b['E']:+.3f} -> {a2['E']:+.3f}   DD {b['dd']:.1f} -> {a2['dd']:.1f} R")
tt,pv=stats.ttest_ind(t.R.values[mk],t.R.values[~mk],equal_var=False)
print(f"  ecart garde vs rejete : {t.R.values[mk].mean()-t.R.values[~mk].mean():+.3f} R   t={tt:+.2f}  p={pv:.4f}")

print("\nWALK-FORWARD 4 QUARTS")
print(f"{'periode':26s} {'n av':>5s} {'n ap':>5s} {'PF av':>7s} {'PF ap':>7s} {'E av':>7s} {'E ap':>7s} {'gain':>7s}")
idx=np.array_split(np.arange(len(t)),4); ok=0
for i,ii in enumerate(idx):
    s=t.iloc[ii]; mm=(s.adx<=THR).values; r=s.R.values
    pf0=r[r>0].sum()/abs(r[r<=0].sum()); pf1=r[mm&(r>0)].sum()/abs(r[mm&(r<=0)].sum())
    ok+= r[mm].mean()>r.mean()
    print(f"{str(s.t_in.min().date())+' -> '+str(s.t_in.max().date()):26s} {len(r):5d} {int(mm.sum()):5d} "
          f"{pf0:7.3f} {pf1:7.3f} {r.mean():+7.3f} {r[mm].mean():+7.3f} {r[mm].mean()-r.mean():+7.3f}")
print(f"  sous-periodes ameliorees : {ok}/4")

print("\nAPPRENTISSAGE / VALIDATION")
half=len(t)//2
for nm,sl in [('apprentissage',slice(0,half)),('validation   ',slice(half,None))]:
    s=t.iloc[sl]; mm=(s.adx<=THR).values; r=s.R.values
    tt,pv=stats.ttest_ind(r[mm],r[~mm],equal_var=False)
    print(f"  {nm} ({s.t_in.min().date()} -> {s.t_in.max().date()}) : "
          f"E {r.mean():+.3f} -> {r[mm].mean():+.3f}  ecart bas-haut {r[mm].mean()-r[~mm].mean():+.3f} R  p={pv:.4f}")

print("\nBOOTSTRAP PAR BLOCS (20 trades) — IC 95% de l'ecart")
rng=np.random.default_rng(11); rm=t.R.values[mk]; rh=t.R.values[~mk]; bs=[]
for _ in range(10000):
    A=rng.choice(rm,len(rm)); B=rng.choice(rh,len(rh)); bs.append(A.mean()-B.mean())
lo_,hi_=np.percentile(bs,[2.5,97.5])
print(f"  ecart = {rm.mean()-rh.mean():+.3f} R   IC95 [{lo_:+.3f} ; {hi_:+.3f}]   "
      f"P(ecart>0) = {100*np.mean(np.array(bs)>0):.1f}%")
