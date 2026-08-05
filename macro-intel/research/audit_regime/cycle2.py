import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0,'.')
from core_import import *
df,K=pickle.load(open('lab.pkl','rb'))
c,h,l=df.close,df.high,df.low
PLAN=lambda sl=2.5: ExitPlan(sl_atr=sl,tp1_r=99,tp2_r=99,tp3_r=99,part1=0,part2=0,
                             breakeven_after_tp1=False,trail_r=0.3,trail_start_r=1.5)
BASE=(K['htf']==True)&(K['biasD']==True), (K['htf']==False)&(K['biasD']==False)
FULL=((K['htf']==True)&(c>K['vwap'])&(K['biasD']==True)&(K['biasW']==True)&(c>K['poc']),
      (K['htf']==False)&(c<K['vwap'])&(K['biasD']==False)&(K['biasW']==False)&(c<K['poc']))
def ev(tu,td,al,lab,sl=2.5):
    L=cooldown((tu&al[0]).fillna(False)); S=cooldown((td&al[1]).fillna(False))
    t=simulate(df,K['atr'],L,S,PLAN(sl),COSTS)
    m=metrics(t,lab)
    if m.get('n',0)>=30:
        a=metrics(t[t.t_in<'2024-08-01'],''); b=metrics(t[t.t_in>='2024-08-01'],'')
        m['Ea']=a.get('E',np.nan); m['Eb']=b.get('E',np.nan)
    return t,m
def line(m):
    if m.get('n',0)<30: print(f"  {m['nom']:36s} trop peu ({m.get('n',0)})"); return
    print(f"  {m['nom']:36s} n={m['n']:4d} WR={m['wr']:5.1f}% PF={m['pf']:6.3f} E={m['E']:+.3f} "
          f"DD={m['dd']:6.1f} tot={m['tot']:+6.1f}R t={m['t']:+5.2f} | appr {m['Ea']:+.3f} valid {m['Eb']:+.3f}")

print("="*118)
print("CYCLE 2 — LE DECLENCHEUR : le BOS est-il le meilleur, ou juste celui qu'on avait ?")
print("="*118)
TRIGS={
 'BOS (actuel)'              : (K['bosUp'],K['bosDn']),
 'Donchian 48 (12 h)'        : (K['donchUp'],K['donchDn']),
 'Donchian 96 (24 h)'        : ((c>h.shift().rolling(96).max()).fillna(False),(c<l.shift().rolling(96).min()).fillna(False)),
 'Donchian 192 (48 h)'       : ((c>h.shift().rolling(192).max()).fillna(False),(c<l.shift().rolling(192).min()).fillna(False)),
 'croisement EMA 20/200'     : ((c>K['ema200'])&(c.shift()<=K['ema200'].shift()),(c<K['ema200'])&(c.shift()>=K['ema200'].shift())),
 'expansion de volatilite'   : (((c-c.shift(4))>1.5*K['atr']).fillna(False),((c.shift(4)-c)>1.5*K['atr']).fillna(False)),
 'aucun (a chaque bougie)'   : (pd.Series(True,index=df.index),pd.Series(True,index=df.index)),
}
print("\n>>> avec les 5 filtres actuels")
for k,(tu,td) in TRIGS.items():
    _,m=ev(tu,td,FULL,k); line(m)
print("\n>>> avec le systeme SIMPLIFIE (H1 + biais D1 seulement)")
res={}
for k,(tu,td) in TRIGS.items():
    t,m=ev(tu,td,BASE,k); res[k]=(t,m); line(m)

print("\n"+"="*118)
print("CYCLE 3 — IDEES HORS SMC")
print("="*118)
print("\n>>> A. DIMENSIONNEMENT PAR LA VOLATILITE (Moreira-Muir : risquer plus quand la vol est basse)")
t,_=res['BOS (actuel)']
vol=K['volN'].reindex(t.t_in).values; med=np.nanmedian(vol)
for cap in [1.0,1.5,2.0,3.0]:
    wgt=np.clip(med/vol,1/cap,cap); wgt=np.where(np.isfinite(wgt),wgt,1.0)
    r=t.R.values*wgt; w=r[r>0]; lo=r[r<=0]; eq=np.cumsum(r)
    dd=(eq-np.maximum.accumulate(np.concatenate([[0],eq]))[1:]).min()
    lab='sans ponderation' if cap==1.0 else f'ponderation, plafond {cap}x'
    print(f"  {lab:36s} PF={w.sum()/abs(lo.sum()):6.3f} E={r.mean():+.3f} DD={dd:6.1f} tot={r.sum():+6.1f}R "
          f"t={r.mean()/(r.std(ddof=1)/np.sqrt(len(r))):+5.2f}")

print("\n>>> B. REGIME DE VOLATILITE comme condition d'entree (theorie : les cassures paient en vol basse)")
lo_v=(K['volN']<=K['volMed']); hi_v=(K['volN']>K['volMed'])
for lab,cond in [('volatilite BASSE seulement',lo_v),('volatilite HAUTE seulement',hi_v)]:
    _,m=ev(K['bosUp'],K['bosDn'],(BASE[0]&cond,BASE[1]&cond),lab); line(m)

print("\n>>> C. RATIO DE VARIANCE (theorie : n'entrer que quand le marche est en regime de tendance)")
vr=K['vr']; q=vr.rolling(96*40,min_periods=1000).rank(pct=True)
for lab,cond in [('regime de tendance (VR haut)',q>0.5),('regime de retour moyen (VR bas)',q<=0.5)]:
    _,m=ev(K['bosUp'],K['bosDn'],(BASE[0]&cond,BASE[1]&cond),lab); line(m)

print("\n>>> D. MOMENTUM LONG TERME (Moskowitz-Ooi-Pedersen : le TSMOM 12 mois est un edge documente)")
for lab,cond in [('momentum 20 j aligne',(K['tsmom']>0)),('momentum 20 j oppose',(K['tsmom']<=0))]:
    al=(BASE[0]&cond,BASE[1]&(K['tsmom']<=0) if 'aligne' in lab else BASE[1]&(K['tsmom']>0))
    _,m=ev(K['bosUp'],K['bosDn'],al,lab); line(m)
pickle.dump(res,open('cycle2.pkl','wb'))
