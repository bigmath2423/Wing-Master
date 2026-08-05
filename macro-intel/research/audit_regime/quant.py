"""Concepts institutionnels : construction, puis ECRAN DE REDONDANCE avant tout test."""
import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0,'.')
from core_import import *
df,K=pickle.load(open('lab.pkl','rb'))
o,h,l,c,v=df.open,df.high,df.low,df.close,df.volume
ret=c.pct_change(); day=pd.Series(df.index.date,index=df.index)
F={}

# 1. EFFICIENCE FRACTALE (Kaufman). Mesure : quelle part du chemin parcouru va
#    dans une direction. 1 = impulsion pure, 0 = bruit. Les desks l'utilisent
#    pour distinguer une tendance d'un aller-retour de meme amplitude.
for n in (24,96):
    F[f'efficience_{n}']=(c-c.shift(n)).abs()/c.diff().abs().rolling(n).sum()

# 2. ILLIQUIDITE D'AMIHUD. Mesure : combien de mouvement de prix par unite de
#    volume. Eleve = le prix bouge sans volume, donc peu d'information derriere.
F['amihud']=(ret.abs()/v.replace(0,np.nan)).rolling(96).median()
F['amihud_rel']=F['amihud']/F['amihud'].rolling(96*20,min_periods=500).median()

# 3. PRESSION D'ORDRES (proxy de flux). Position de la cloture dans la bougie,
#    ponderee par le volume, cumulee. Approche le desequilibre acheteur/vendeur
#    sans carnet d'ordres.
clv=(((c-l)-(h-c))/(h-l).replace(0,np.nan)).fillna(0)
F['flux_24']=(clv*v).rolling(96).sum()/v.rolling(96).sum()
F['flux_6'] =(clv*v).rolling(24).sum()/v.rolling(24).sum()

# 4. RATIO DE BRUIT (Parkinson / close-to-close). Si la volatilite de RANGE
#    depasse largement celle des clotures, la bougie fait des aller-retours
#    intra-bougie : le mouvement est bruite. Different de l'ATR, qui ne mesure
#    que l'amplitude.
park=np.sqrt((np.log(h/l)**2).rolling(96).mean()/(4*np.log(2)))
cc=ret.rolling(96).std()
F['bruit']=(park/cc.replace(0,np.nan))

# 5. MIGRATION DE VALEUR (Auction Market Theory). Le coeur de la theorie des
#    encheres : ce n'est pas le NIVEAU de la value area qui informe, c'est son
#    DEPLACEMENT d'un jour a l'autre. Value qui monte = acceptation haussiere.
hl2=(h+l)/2; vamid={}
for d_,sub in hl2.groupby(day):
    vv=v.loc[sub.index]; lo_,hi_=sub.min(),sub.max()
    if len(sub)<20 or hi_<=lo_: vamid[d_]=np.nan; continue
    st=(hi_-lo_)/50; k=np.minimum(49,np.maximum(0,((sub-lo_)/st).astype(int)))
    acc=np.bincount(k,weights=vv.values,minlength=50); kx=acc.argmax()
    tot=acc.sum(); a1=b1=kx; cum=acc[kx]
    while cum<tot*0.7 and (a1>0 or b1<49):
        up_=acc[b1+1] if b1<49 else -1; dn_=acc[a1-1] if a1>0 else -1
        if up_>=dn_ and b1<49: b1+=1; cum+=up_
        elif a1>0: a1-=1; cum+=dn_
        else: break
    vamid[d_]=lo_+((a1+b1+1)/2)*st
ds=sorted(vamid); vs=pd.Series([vamid[d_] for d_ in ds],index=pd.to_datetime(ds))
mig=(vs.diff()/vs).shift(1)                    # migration de la veille : causal
F['migration_valeur']=pd.Series(df.index.normalize().map(mig),index=df.index)

# 6. BALANCE INITIALE (Market Profile). Range de la premiere heure de seance ;
#    l'extension au-dela est le signal d'enchere classique des desks.
first=df.between_time('00:00','00:59')
ibh=first.high.groupby(pd.Series(first.index.date,index=first.index)).max()
ibl=first.low.groupby(pd.Series(first.index.date,index=first.index)).min()
IBH=pd.Series(df.index.normalize().map(ibh),index=df.index)
IBL=pd.Series(df.index.normalize().map(ibl),index=df.index)
F['ib_position']=((c-IBL)/(IBH-IBL).replace(0,np.nan))

# 7. STRUCTURE PAR TERME DE LA VOLATILITE. Vol courte / vol longue : > 1 =
#    expansion en cours, < 1 = compression. Different du NIVEAU de vol (ATR).
F['vol_terme']=ret.rolling(96).std()/ret.rolling(96*20).std()

# 8. COUT DU MOUVEMENT. Volume consomme par unite de deplacement net : mesure
#    directe de la resistance rencontree par le prix.
F['cout_mouvement']=(v.rolling(96).sum()/(c-c.shift(96)).abs().replace(0,np.nan))
F['cout_rel']=F['cout_mouvement']/F['cout_mouvement'].rolling(96*20,min_periods=500).median()

for k in F: F[k]=F[k].replace([np.inf,-np.inf],np.nan)
pickle.dump(F,open('quantF.pkl','wb'))

# ---------- ECRAN DE REDONDANCE ----------
EXIST={
 'biais D1+W1'       : ((K['biasD']==True).astype(float)-(K['biasD']==False).astype(float))
                       +((K['biasW']==True).astype(float)-(K['biasW']==False).astype(float)),
 'tendance H1'       : (K['htf']==True).astype(float)-(K['htf']==False).astype(float),
 'cote du VWAP'      : np.sign(c-K['vwap']),
 'cote du POC'       : np.sign(c-K['poc']),
 'etat structure'    : K['trend'],
 'ATR normalise'     : K['atr']/c,
 'distance EMA200'   : (c-c.ewm(span=200,adjust=False).mean())/K['atr'],
}
print("ECRAN DE REDONDANCE — un concept n'est teste que s'il mesure autre chose\n")
print(f"{'concept':22s} "+" ".join(f"{k[:11]:>12s}" for k in EXIST)+"   |  max |r|")
keep=[]
for k,s in F.items():
    row=[]
    for k2,s2 in EXIST.items():
        d2=pd.concat([s,s2],axis=1).dropna()
        row.append(np.corrcoef(d2.iloc[:,0],d2.iloc[:,1])[0,1] if len(d2)>500 else np.nan)
    mx=np.nanmax(np.abs(row))
    flag='  REDONDANT' if mx>0.50 else ''
    if mx<=0.50: keep.append(k)
    print(f"{k:22s} "+" ".join(f"{x:+12.3f}" for x in row)+f"   |  {mx:.3f}{flag}")
print(f"\nConcepts retenus pour la phase de test : {len(keep)}/{len(F)}")
print("  "+", ".join(keep))
pickle.dump(keep,open('quantKeep.pkl','wb'))
