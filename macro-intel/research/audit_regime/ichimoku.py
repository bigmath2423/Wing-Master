import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0,'.')
from core_import import *
from scipy import stats
df,K=pickle.load(open('lab.pkl','rb'))
c,h,l=df.close,df.high,df.low

def ichi(hh,ll,cc,t=9,k=26,b=52,sh=26):
    """Ichimoku CAUSAL. Les nuages sont projetes en AVANT : a la bougie i, le
    nuage visible est calcule sur des donnees de i-26. Aucune valeur future."""
    ten=(hh.rolling(t).max()+ll.rolling(t).min())/2
    kij=(hh.rolling(k).max()+ll.rolling(k).min())/2
    sa=((ten+kij)/2).shift(sh)          # Senkou A deja en place a la bougie i
    sb=((hh.rolling(b).max()+ll.rolling(b).min())/2).shift(sh)
    return dict(ten=ten,kij=kij,sa=sa,sb=sb,
                top=pd.concat([sa,sb],axis=1).max(axis=1),
                bot=pd.concat([sa,sb],axis=1).min(axis=1))
I=ichi(h,l,c)
# Ichimoku H1, ramene en M15 par la bougie H1 CLOTUREE (aucun repaint)
h1=df.resample('1h').agg({'high':'max','low':'min','close':'last'}).dropna()
I1=ichi(h1.high,h1.low,h1.close)
def toM15(s): return pd.Series(df.index.floor('1h').map(s.shift(1)),index=df.index)
# Ichimoku D1
d1=df.resample('1D').agg({'high':'max','low':'min','close':'last'}).dropna()
ID=ichi(d1.high,d1.low,d1.close)
def toD(s): return pd.Series(df.index.normalize().map(s.shift(1)),index=df.index)

# --- conditions Ichimoku ---
COND={
 'M15 au-dessus du nuage'    : (c>I['top'], c<I['bot']),
 'M15 au-dessus du Kijun'    : (c>I['kij'], c<I['kij']),
 'M15 Tenkan > Kijun'        : (I['ten']>I['kij'], I['ten']<I['kij']),
 'M15 nuage haussier (A>B)'  : (I['sa']>I['sb'], I['sa']<I['sb']),
 'M15 Chikou degage'         : (c>h.shift(26), c<l.shift(26)),
 'H1 au-dessus du nuage'     : (c>toM15(I1['top']), c<toM15(I1['bot'])),
 'D1 au-dessus du nuage'     : (c>toD(ID['top']),  c<toD(ID['bot'])),
}
TRIG={
 'croisement Tenkan/Kijun'   : ((I['ten']>I['kij'])&(I['ten'].shift()<=I['kij'].shift()),
                                (I['ten']<I['kij'])&(I['ten'].shift()>=I['kij'].shift())),
 'cassure du Kijun'          : ((c>I['kij'])&(c.shift()<=I['kij'].shift()),(c<I['kij'])&(c.shift()>=I['kij'].shift())),
 'sortie du nuage'           : ((c>I['top'])&(c.shift()<=I['top'].shift()),(c<I['bot'])&(c.shift()>=I['bot'].shift())),
}
def don(n): return (c>h.shift().rolling(n).max()).fillna(False),(c<l.shift().rolling(n).min()).fillna(False)
BOS=(K['bosUp'],K['bosDn'])
BASE=((K['htf']==True)&(c>K['vwap'])&(K['biasD']==True)&(K['biasW']==True)&(c>K['poc']),
      (K['htf']==False)&(c<K['vwap'])&(K['biasD']==False)&(K['biasW']==False)&(c<K['poc']))
def ev(tu,td,aL,aS,lab):
    t=simulate(df,K['atr'],cooldown((tu&aL.fillna(False)).fillna(False)),
               cooldown((td&aS.fillna(False)).fillna(False)),
               ExitPlan(sl_atr=2.5,tp1_r=99,tp2_r=99,tp3_r=99,part1=0,part2=0,
                        breakeven_after_tp1=False,trail_r=0.3,trail_start_r=1.5),COSTS)
    m=metrics(t,lab)
    if m.get('n',0)<50: return m,None
    m['Ea']=metrics(t[t.t_in<'2024-08-01'],'')['E']; m['Eb']=metrics(t[t.t_in>='2024-08-01'],'')['E']
    m['gap']=abs(m['Eb']-m['Ea'])
    q=[metrics(t.iloc[i],'')['E'] for i in np.array_split(np.arange(len(t)),4)]
    m['pos']=sum(1 for x in q if x>0)
    return m,t
def line(m):
    if m.get('n',0)<50: print(f"  {m['nom']:34s} trop peu ({m.get('n',0)})"); return
    print(f"  {m['nom']:34s} n={m['n']:4d} WR={m['wr']:5.1f}% PF={m['pf']:6.3f} E={m['E']:+.3f} DD={m['dd']:6.1f} "
          f"tot={m['tot']:+6.1f}R t={m['t']:+5.2f} | appr {m['Ea']:+.3f} valid {m['Eb']:+.3f} ecart {m['gap']:.3f} {m['pos']}/4")

print("="*126); print("REFERENCE"); print("="*126)
ref,_=ev(*BOS,BASE[0],BASE[1],'v11 actuelle (BOS + 5 filtres)'); line(ref)
d48=don(48)
cand,_=ev(*d48,(K['htf']==True)&(K['biasD']==True)&(K['biasW']==True),
              (K['htf']==False)&(K['biasD']==False)&(K['biasW']==False),'candidat Donchian48 + 3'); line(cand)

print("\n"+"="*126); print("A. ICHIMOKU COMME DECLENCHEUR (avec les 5 filtres actuels)"); print("="*126)
for k,(tu,td) in TRIG.items():
    m,_=ev(tu.fillna(False),td.fillna(False),BASE[0],BASE[1],k); line(m)

print("\n"+"="*126); print("B. ICHIMOKU COMME FILTRE AJOUTE au systeme actuel"); print("="*126)
for k,(cl,cs) in COND.items():
    m,_=ev(*BOS,BASE[0]&cl.fillna(False),BASE[1]&cs.fillna(False),'+ '+k); line(m)

print("\n"+"="*126); print("C. ICHIMOKU EN REMPLACEMENT (BOS + Ichimoku SEUL, sans les filtres actuels)"); print("="*126)
for k,(cl,cs) in COND.items():
    m,_=ev(*BOS,cl.fillna(False),cs.fillna(False),k+' seul'); line(m)

print("\n"+"="*126); print("D. SYSTEME ICHIMOKU COMPLET (nuage + Tenkan/Kijun + Chikou)"); print("="*126)
fullL=(c>I['top'])&(I['ten']>I['kij'])&(I['sa']>I['sb'])&(c>h.shift(26))
fullS=(c<I['bot'])&(I['ten']<I['kij'])&(I['sa']<I['sb'])&(c<l.shift(26))
for lab,(tu,td) in [('declencheur BOS',BOS),('declencheur Donchian48',d48),
                    ('declencheur Tenkan/Kijun',TRIG['croisement Tenkan/Kijun'])]:
    m,_=ev(tu.fillna(False),td.fillna(False),fullL,fullS,'Ichimoku complet + '+lab); line(m)
