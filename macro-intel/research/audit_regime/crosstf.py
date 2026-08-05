import sys, numpy as np, pandas as pd
sys.path.insert(0,'.')
from v11sim import *
from scipy import stats
U='/root/.claude/uploads/b22822dc-6a41-522c-931f-c596aee488bc/'

def resample(df,rule):
    o=df.resample(rule).agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'})
    return o.dropna()

def adx_raw(df,n=14):
    h,l=df.high,df.low; pc=df.close.shift()
    tr=pd.concat([h-l,(h-pc).abs(),(l-pc).abs()],axis=1).max(axis=1)
    aw=tr.ewm(alpha=1/n,adjust=False).mean()
    up,dn=h.diff(),-l.diff()
    p_=np.where((up>dn)&(up>0),up,0.); m_=np.where((dn>up)&(dn>0),dn,0.)
    pdi=100*pd.Series(p_,index=df.index).ewm(alpha=1/n,adjust=False).mean()/aw
    mdi=100*pd.Series(m_,index=df.index).ewm(alpha=1/n,adjust=False).mean()/aw
    return (100*(pdi-mdi).abs()/(pdi+mdi).replace(0,np.nan)).ewm(alpha=1/n,adjust=False).mean()

PLAN_=ExitPlan(sl_atr=2.5,tp1_r=99,tp2_r=99,tp3_r=99,part1=0,part2=0,
               breakeven_after_tp1=False,trail_r=0.3,trail_start_r=1.5)

def test(df,lab,win=500):
    L,S,a,_=v11_signals(df)
    t=simulate(df,a,L,S,PLAN_,COSTS)
    if len(t)<60: print(f"{lab:24s} seulement {len(t)} trades — insuffisant"); return
    ax=adx_raw(df).rolling(win,min_periods=200).rank(pct=True)
    t['ax']=ax.reindex(t.t_in).values; t=t[t.ax.notna()]
    r=t.R.values; m=(t.ax<=0.5).values
    if m.sum()<25 or (~m).sum()<25: print(f"{lab:24s} sous-groupes trop petits"); return
    def blk(x):
        w=x[x>0]; lo=x[x<=0]
        return len(x),100*len(w)/len(x),(w.sum()/abs(lo.sum()) if lo.sum()<0 else np.inf),x.mean()
    n0,w0,pf0,e0=blk(r); n1,w1,pf1,e1=blk(r[m]); n2,w2,pf2,e2=blk(r[~m])
    tt,pv=stats.ttest_ind(r[m],r[~m],equal_var=False)
    print(f"{lab:24s} {n0:4d} | sans {pf0:5.2f}/{e0:+.3f} | ADXbas {n1:4d} {w1:4.1f}% {pf1:5.2f}/{e1:+.3f} "
          f"| ADXhaut {n2:4d} {w2:4.1f}% {pf2:5.2f}/{e2:+.3f} | ecart {e1-e2:+.3f}R p={pv:.4f}")

m15=load_mt5(U+'4b5607af-XAUUSD_M15_202204290100_202608041500.csv')
m5 =load_mt5(U+'2825bf2f-XAUUSD_M5_202502272030_202608050445.csv')
print("FALSIFICATION CROISEE — le meme mecanisme apparait-il ailleurs ?")
print("(format : n | reference PF/E | ADX bas n WR PF/E | ADX haut n WR PF/E | ecart)\n")
test(m5,'M5  2025-2026')
test(m15,'M15 2022-2026 (ref)')
test(resample(m15,'30min'),'M30 2022-2026')
test(resample(m15,'1h'),'H1  2022-2026')
test(resample(m15,'4h'),'H4  2022-2026')

print("\nSOUS-PERIODES DISJOINTES du M15 (aucun trade commun entre les lignes)")
L,S,a,_=v11_signals(m15); t=simulate(m15,a,L,S,PLAN_,COSTS)
ax=adx_raw(m15).rolling(500,min_periods=200).rank(pct=True)
t['ax']=ax.reindex(t.t_in).values; t=t[t.ax.notna()].reset_index(drop=True)
for y in [2022,2023,2024,2025,2026]:
    s=t[t.t_in.dt.year==y]
    if len(s)<40: continue
    r=s.R.values; m=(s.ax<=0.5).values
    if m.sum()<15 or (~m).sum()<15: continue
    print(f"  {y}  n={len(s):3d}  E sans {r.mean():+.3f}  ADXbas {r[m].mean():+.3f} (n={int(m.sum())})  "
          f"ADXhaut {r[~m].mean():+.3f} (n={int((~m).sum())})  ecart {r[m].mean()-r[~m].mean():+.3f} R")
