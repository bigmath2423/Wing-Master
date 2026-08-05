import sys, numpy as np, pandas as pd
sys.path.insert(0,'.')
from v11sim import *
from scipy import stats
U='/root/.claude/uploads/b22822dc-6a41-522c-931f-c596aee488bc/'
df=load_mt5(U+'4b5607af-XAUUSD_M15_202204290100_202608041500.csv')
L,S,a,trend=v11_signals(df)
t=simulate(df,a,L,S,ExitPlan(sl_atr=2.5,tp1_r=99,tp2_r=99,tp3_r=99,part1=0,part2=0,
           breakeven_after_tp1=False,trail_r=0.3,trail_start_r=1.5),COSTS)
h,l,c=df.high,df.low,df.close; pc=c.shift()
tr=pd.concat([h-l,(h-pc).abs(),(l-pc).abs()],axis=1).max(axis=1)
aw=tr.ewm(alpha=1/14,adjust=False).mean()
up,dn=h.diff(),-l.diff()
p_=np.where((up>dn)&(up>0),up,0.); m_=np.where((dn>up)&(dn>0),dn,0.)
pdi=100*pd.Series(p_,index=df.index).ewm(alpha=1/14,adjust=False).mean()/aw
mdi=100*pd.Series(m_,index=df.index).ewm(alpha=1/14,adjust=False).mean()/aw
adxr=(100*(pdi-mdi).abs()/(pdi+mdi).replace(0,np.nan)).ewm(alpha=1/14,adjust=False).mean()
axp=adxr.rolling(500,min_periods=200).rank(pct=True)

# --- mesures d'"avancement du mouvement" INDEPENDANTES de l'ADX ---
flip=(trend!=trend.shift())
since=pd.Series(np.arange(len(df)),index=df.index)
since=since-since.where(flip).ffill()                    # barres depuis le dernier changement de tendance
atrn=a
mv=(c-c.where(flip).ffill()).abs()/atrn                  # amplitude deja parcourue depuis le flip, en ATR
rng96=(h.rolling(96).max()-l.rolling(96).min())/atrn     # etendue des 24 dernieres heures, en ATR

t['ax']=axp.reindex(t.t_in).values
t['since']=since.reindex(t.t_in).values
t['mv']=mv.reindex(t.t_in).values
t['rng']=rng96.reindex(t.t_in).values
t=t[t.ax.notna()].reset_index(drop=True)
m=(t.ax<=0.5).values

print("A) L'ADX MESURE-T-IL BIEN 'LE MOUVEMENT EST DEJA AVANCE' ?")
print("   (variables construites sans aucun ADX)\n")
for k,lab in [('since','barres depuis le dernier changement de tendance'),
              ('mv','amplitude deja parcourue depuis le flip (ATR)'),
              ('rng','etendue des 24 dernieres heures (ATR)')]:
    A=t[k].values[m]; B=t[k].values[~m]
    tt,pv=stats.ttest_ind(A[np.isfinite(A)],B[np.isfinite(B)],equal_var=False)
    print(f"   {lab:48s} ADXbas {np.nanmedian(A):7.2f} | ADXhaut {np.nanmedian(B):7.2f} | t={tt:+6.2f} p={pv:.4f}")

print("\nB) CES VARIABLES PREDISENT-ELLES LE RESULTAT ELLES AUSSI ?")
print("   Si le mecanisme est reel, elles doivent marcher SANS l'ADX.\n")
r=t.R.values
for k,lab in [('since','barres depuis le flip'),('mv','amplitude parcourue'),('rng','etendue 24h')]:
    v=t[k].values; ok=np.isfinite(v)
    med=np.nanmedian(v[ok])
    lo_=(v<=med)&ok; hi_=(v>med)&ok
    tt,pv=stats.ttest_ind(r[lo_],r[hi_],equal_var=False)
    print(f"   {lab:26s} bas {r[lo_].mean():+.3f}R (n={lo_.sum():3d}) | haut {r[hi_].mean():+.3f}R (n={hi_.sum():3d})"
          f" | ecart {r[lo_].mean()-r[hi_].mean():+.3f} p={pv:.4f}")

print("\nC) L'EFFET ADX SURVIT-IL EN CONTROLANT L'AVANCEMENT DU MOUVEMENT ?")
for k,lab in [('since','barres depuis le flip'),('mv','amplitude parcourue')]:
    v=t[k].values; med=np.nanmedian(v[np.isfinite(v)])
    for side,nm in [(v<=med,'mouvement JEUNE'),(v>med,'mouvement AVANCE')]:
        s=side&np.isfinite(v)
        mm=m&s; hh=(~m)&s
        if mm.sum()<25 or hh.sum()<25: continue
        tt,pv=stats.ttest_ind(r[mm],r[hh],equal_var=False)
        print(f"   [{lab:22s}] {nm:17s} ADXbas {r[mm].mean():+.3f} (n={mm.sum():3d}) | "
              f"ADXhaut {r[hh].mean():+.3f} (n={hh.sum():3d}) | ecart {r[mm].mean()-r[hh].mean():+.3f} p={pv:.4f}")
