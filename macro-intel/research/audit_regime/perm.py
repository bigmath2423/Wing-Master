import sys, numpy as np, pandas as pd
sys.path.insert(0,'.')
from v11sim import *
U='/root/.claude/uploads/b22822dc-6a41-522c-931f-c596aee488bc/'
df=load_mt5(U+'4b5607af-XAUUSD_M15_202204290100_202608041500.csv')
L,S,a,_=v11_signals(df)
t=simulate(df,a,L,S,ExitPlan(sl_atr=2.5,tp1_r=99,tp2_r=99,tp3_r=99,part1=0,part2=0,
           breakeven_after_tp1=False,trail_r=0.3,trail_start_r=1.5),COSTS)
h,l,c=df.high,df.low,df.close; pc=c.shift()
tr=pd.concat([h-l,(h-pc).abs(),(l-pc).abs()],axis=1).max(axis=1)
aw=tr.ewm(alpha=1/14,adjust=False).mean()
up,dn=h.diff(),-l.diff()
p_=np.where((up>dn)&(up>0),up,0.); m_=np.where((dn>up)&(dn>0),dn,0.)
pdi=100*pd.Series(p_,index=df.index).ewm(alpha=1/14,adjust=False).mean()/aw
mdi=100*pd.Series(m_,index=df.index).ewm(alpha=1/14,adjust=False).mean()/aw
adx=(100*(pdi-mdi).abs()/(pdi+mdi).replace(0,np.nan)).ewm(alpha=1/14,adjust=False).mean()
axp=adx.rolling(500,min_periods=200).rank(pct=True)

pos=df.index.get_indexer(t.t_in)
axv=axp.to_numpy(); R=t.R.to_numpy(); n=len(df)
ok=np.isfinite(axv[pos]); pos=pos[ok]; R=R[ok]
obs_m=axv[pos]<=0.5
obs=R[obs_m].mean()-R[~obs_m].mean()
print(f"effet observe : {obs:+.4f} R  (n gardes {obs_m.sum()} / rejetes {(~obs_m).sum()})\n")

# --- PLACEBO : on decale circulairement la serie ADX. La structure temporelle
#     de l'ADX (autocorrelation, cycles) et celle des trades sont conservees ;
#     seule leur correspondance est detruite. C'est le null correct quand les
#     deux series sont fortement autocorrelees, ce que le test de Student ignore.
rng=np.random.default_rng(3); null=[]
for _ in range(5000):
    s=rng.integers(2000,n-2000)
    v=np.roll(axv,s)[pos]
    g=np.isfinite(v)
    if g.sum()<100: continue
    med=np.nanmedian(v[g])
    m2=(v<=med)&g
    if m2.sum()<50 or (g&~m2).sum()<50: continue
    null.append(R[m2].mean()-R[g&~m2].mean())
null=np.array(null)
p=np.mean(np.abs(null)>=abs(obs))
print(f"TEST DE PLACEBO PAR DECALAGE CIRCULAIRE ({len(null)} tirages)")
print(f"  null : moyenne {null.mean():+.4f}  ecart-type {null.std():.4f}")
print(f"  quantiles 2.5/97.5 : [{np.percentile(null,2.5):+.3f} ; {np.percentile(null,97.5):+.3f}]")
print(f"  p bilateral = {p:.4f}   (le test de Student donnait 0.0015)")
print(f"  => {'effet distinguable du hasard' if p<0.05 else 'NON distinguable du hasard'}")

# meme test sur la version a seuil fixe, et sur les quintiles extremes
print("\nMeme placebo, mesure par quintiles extremes (Q1+Q2 vs Q4+Q5) :")
q=pd.qcut(pd.Series(axv[pos]),5,labels=False).to_numpy()
obs2=R[q<=1].mean()-R[q>=3].mean()
null2=[]
for _ in range(5000):
    s=rng.integers(2000,n-2000)
    v=np.roll(axv,s)[pos]; g=np.isfinite(v)
    if g.sum()<200: continue
    qq=pd.qcut(pd.Series(v[g]),5,labels=False).to_numpy()
    rr=R[g]
    null2.append(rr[qq<=1].mean()-rr[qq>=3].mean())
null2=np.array(null2); p2=np.mean(np.abs(null2)>=abs(obs2))
print(f"  observe {obs2:+.4f} R   null sd {null2.std():.4f}   p = {p2:.4f}")
