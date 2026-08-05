import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0,'.')
from core_import import *
from scipy import stats
df,K=pickle.load(open('lab.pkl','rb'))
c,h,l=df.close,df.high,df.low
e5,e20,e50=[c.ewm(span=n,adjust=False,min_periods=n).mean() for n in (5,20,50)]
# ribbon sur H1 et D1, bougies CLOTUREES
h1=c.resample('1h').last().dropna(); d1=c.resample('1D').last().dropna()
def up(s,n): return (s>s.ewm(span=n,adjust=False,min_periods=n).mean()).shift(1)
def ribH(x,a,b,cc):
    A,B,C=[x.ewm(span=n,adjust=False,min_periods=n).mean() for n in (a,b,cc)]
    return ((A>B)&(B>C)).shift(1),((A<B)&(B<C)).shift(1)
rh_u,rh_d=ribH(h1,5,20,50); rd_u,rd_d=ribH(d1,5,20,50)
toH=lambda s: pd.Series(df.index.floor('1h').map(s),index=df.index)
toD=lambda s: pd.Series(df.index.normalize().map(s),index=df.index)

def don(n): return (c>h.shift().rolling(n).max()).fillna(False),(c<l.shift().rolling(n).min()).fillna(False)
BOS=(K['bosUp'],K['bosDn'])
BASE=((K['htf']==True)&(c>K['vwap'])&(K['biasD']==True)&(K['biasW']==True)&(c>K['poc']),
      (K['htf']==False)&(c<K['vwap'])&(K['biasD']==False)&(K['biasW']==False)&(c<K['poc']))
RIB=((e5>e20)&(e20>e50), (e5<e20)&(e20<e50))
TRIG={
 'EMA5 croise EMA20'  : ((e5>e20)&(e5.shift()<=e20.shift()),(e5<e20)&(e5.shift()>=e20.shift())),
 'EMA5 croise EMA50'  : ((e5>e50)&(e5.shift()<=e50.shift()),(e5<e50)&(e5.shift()>=e50.shift())),
 'EMA20 croise EMA50' : ((e20>e50)&(e20.shift()<=e50.shift()),(e20<e50)&(e20.shift()>=e50.shift())),
 'ruban s aligne'     : (RIB[0]&~RIB[0].shift().fillna(False), RIB[1]&~RIB[1].shift().fillna(False)),
 'prix repasse EMA20' : ((c>e20)&(c.shift()<=e20.shift()),(c<e20)&(c.shift()>=e20.shift())),
}
FILT={
 'ruban M15 aligne (5>20>50)': RIB,
 'prix au-dessus EMA50 M15'  : (c>e50, c<e50),
 'prix au-dessus EMA20 M15'  : (c>e20, c<e20),
 'ruban H1 aligne'           : (toH(rh_u)==True, toH(rh_d)==True),
 'ruban D1 aligne'           : (toD(rd_u)==True, toD(rd_d)==True),
}
def run(tu,td,aL,aS):
    return simulate(df,K['atr'],cooldown((tu&aL.fillna(False)).fillna(False)),
        cooldown((td&aS.fillna(False)).fillna(False)),
        ExitPlan(sl_atr=2.5,tp1_r=99,tp2_r=99,tp3_r=99,part1=0,part2=0,
                 breakeven_after_tp1=False,trail_r=0.3,trail_start_r=1.5),COSTS)
def show(t,lab):
    m=metrics(t,lab)
    if m.get('n',0)<50: print(f"  {lab:34s} trop peu ({m.get('n',0)})"); return None
    a=metrics(t[t.t_in<'2024-08-01'],'')['E']; b=metrics(t[t.t_in>='2024-08-01'],'')['E']
    q=[metrics(t.iloc[i],'')['E'] for i in np.array_split(np.arange(len(t)),4)]
    print(f"  {lab:34s} n={m['n']:4d} WR={m['wr']:5.1f}% PF={m['pf']:6.3f} E={m['E']:+.3f} DD={m['dd']:6.1f} "
          f"tot={m['tot']:+6.1f}R t={m['t']:+5.2f} | appr {a:+.3f} valid {b:+.3f} ecart {abs(b-a):.3f} {sum(1 for x in q if x>0)}/4")
    return m
print("="*128); print("REFERENCE"); print("="*128)
tRef=run(*BOS,BASE[0],BASE[1]); show(tRef,'v11 actuelle (BOS + 5 filtres)')
show(run(*don(48),(K['htf']==True)&(K['biasD']==True)&(K['biasW']==True),
                  (K['htf']==False)&(K['biasD']==False)&(K['biasW']==False)),'candidat Donchian48 + 3')
print("\n"+"="*128); print("A. LES EMA COMME DECLENCHEUR (avec les 5 filtres actuels)"); print("="*128)
res={}
for k,(tu,td) in TRIG.items():
    t=run(tu.fillna(False),td.fillna(False),BASE[0],BASE[1]); res['T:'+k]=t; show(t,k)
print("\n"+"="*128); print("B. LES EMA COMME FILTRE AJOUTE au systeme actuel"); print("="*128)
for k,(fl,fs) in FILT.items():
    t=run(*BOS,BASE[0]&fl.fillna(False),BASE[1]&fs.fillna(False)); res['F:'+k]=t; show(t,'+ '+k)
print("\n"+"="*128); print("C. LES EMA EN REMPLACEMENT (BOS + EMA seules)"); print("="*128)
for k,(fl,fs) in FILT.items():
    t=run(*BOS,fl.fillna(False),fs.fillna(False)); show(t,k+' seul')
print("\n"+"="*128); print("D. SYSTEME 100 % EMA (ruban aligne + croisement, sans rien d'autre)"); print("="*128)
for k in ['EMA5 croise EMA20','EMA5 croise EMA50','ruban s aligne']:
    tu,td=TRIG[k]
    show(run(tu.fillna(False),td.fillna(False),RIB[0],RIB[1]),'ruban + '+k)
pickle.dump((res,tRef),open('ema.pkl','wb'))
