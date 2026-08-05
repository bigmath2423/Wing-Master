import pandas as pd, numpy as np
from zoneinfo import ZoneInfo
U='/root/.claude/uploads/b22822dc-6a41-522c-931f-c596aee488bc/'

m=pd.read_csv(U+'4b5607af-XAUUSD_M15_202204290100_202608041500.csv',sep='\t')
m.columns=[c.strip('<>').lower() for c in m.columns]
m['dt']=pd.to_datetime(m['date']+' '+m['time'],format='%Y.%m.%d %H:%M:%S')
m=m[['dt','open','high','low','close','tickvol','spread']].sort_values('dt').reset_index(drop=True)

c,h,l,o=m.close,m.high,m.low,m.open
tr=np.maximum(h-l,np.maximum((h-c.shift()).abs(),(l-c.shift()).abs()))
m['atr']=tr.ewm(alpha=1/14,adjust=False).mean()
m['atrpct']=m.atr.rolling(2000,min_periods=400).rank(pct=True)      # regime de volatilite
# ADX (14)
up=h.diff(); dn=-l.diff()
plus=np.where((up>dn)&(up>0),up,0.0); minus=np.where((dn>up)&(dn>0),dn,0.0)
atr_w=tr.ewm(alpha=1/14,adjust=False).mean()
pdi=100*pd.Series(plus).ewm(alpha=1/14,adjust=False).mean()/atr_w
mdi=100*pd.Series(minus).ewm(alpha=1/14,adjust=False).mean()/atr_w
dx=100*(pdi-mdi).abs()/(pdi+mdi).replace(0,np.nan)
m['adx']=dx.ewm(alpha=1/14,adjust=False).mean()
m['adxpct']=m.adx.rolling(500,min_periods=200).rank(pct=True)
# position dans la range recente (premium / discount)
hi50=h.rolling(96).max(); lo50=l.rolling(96).min()
m['pos']=((c-lo50)/(hi50-lo50).replace(0,np.nan))                    # 0=bas, 1=haut
hi200=h.rolling(384).max(); lo200=l.rolling(384).min()
m['pos4']=((c-lo200)/(hi200-lo200).replace(0,np.nan))
# POC de la veille (meme construction que le Pine)
day=m.dt.dt.date
hl2=(h+l)/2
poc={}
for dd,sub in m.groupby(day):
    if len(sub)<6: poc[dd]=np.nan; continue
    lo_,hi_=sub[['open','high','low','close']].values.min(),sub[['open','high','low','close']].values.max()
    lo_,hi_=(hl2.loc[sub.index]).min(),(hl2.loc[sub.index]).max()
    if hi_<=lo_: poc[dd]=np.nan; continue
    step=(hi_-lo_)/50
    k=np.minimum(49,np.maximum(0,((hl2.loc[sub.index]-lo_)/step).astype(int)))
    acc=np.bincount(k,weights=sub.tickvol.values,minlength=50)
    poc[dd]=lo_+(acc.argmax()+0.5)*step
days=sorted(poc); pocprev={days[i]:poc[days[i-1]] for i in range(1,len(days))}
m['poc']=[pocprev.get(d,np.nan) for d in day]
m['pocdist']=(c-m.poc)/m.atr
# distance a l'EMA journaliere (force du biais)
d1=m.set_index('dt').close.resample('1D').last().dropna()
e20=d1.ewm(span=20,adjust=False).mean()
bias_str=((d1-e20)/d1*100).shift(1)                                  # bougie D1 CLOTUREE
m['biasstr']=m.dt.dt.normalize().map(bias_str)
# H1 : distance a l'EMA50
h1=m.set_index('dt').close.resample('1h').last().dropna()
h1e=h1.ewm(span=50,adjust=False).mean()
h1d=((h1-h1e)/h1*100).shift(1)
m['h1str']=m.dt.dt.floor('1h').map(h1d)
m['body']=(c-o)/m.atr
m['volrel']=m.tickvol/m.tickvol.rolling(96*20,min_periods=500).median()
m.to_pickle('m15f.pkl'); print('features M15 :',len(m),m.dt.min(),'->',m.dt.max())

# ---- trades ----
d=pd.read_csv(U+'5171c639-XAU_Momentum_v11_sur_4ans.csv',encoding='utf-8-sig');d.columns=[c.strip() for c in d.columns]
rows=[]
for tn,sub in d.groupby('Numéro de trade'):
    e=sub[sub['Type'].str.contains('Entrer',na=False)];x=sub[sub['Type'].str.contains('Sortir',na=False)]
    if len(e)==0 or len(x)==0: continue
    e0=e.iloc[0]
    rows.append(dict(dt=pd.to_datetime(e0['Date et heure']),dir=1 if 'long' in str(e0['Type']).lower() else -1,
        px=float(e0['Prix USD']),pnl=float(e0['P&L net EUR']),pct=float(e0['Retour %']),
        mfe=float(e0['Excursion favorable EUR']),mae=float(e0['Excursion adverse EUR']),
        bars=float(e0['Durée (barres)']),exit=str(x.iloc[-1]['Signal'])))
t=pd.DataFrame(rows).sort_values('dt').reset_index(drop=True)
tz=ZoneInfo('Europe/Athens')
t['off']=t.dt.map(lambda x:180 if x.to_pydatetime().replace(tzinfo=tz).utcoffset().total_seconds()==10800 else 120)
t['bdt']=t.dt+pd.to_timedelta(t.off,unit='m')     # bougie M15 de signal, heure broker
mi=m.set_index('dt')
j=mi.reindex(t.bdt)
t['perr']=np.abs(j.close.values-t.px.values)
for k in ['atr','atrpct','adx','adxpct','pos','pos4','pocdist','biasstr','h1str','body','volrel','spread']:
    t[k]=j[k].values
cov=t[t.perr.notna()&(t.perr<3.0)].copy()
R=abs(cov.loc[cov.pnl<=0,'pct'].median()); cov['R']=cov.pct/R
print(f"trades apparies : {len(cov)}/{len(t)}  erreur mediane {cov.perr.median():.3f}$")
print(f"reference : n={len(cov)} WR={100*(cov.pnl>0).mean():.1f}% PF={cov.loc[cov.pnl>0,'pnl'].sum()/-cov.loc[cov.pnl<=0,'pnl'].sum():.3f} E={cov.R.mean():+.3f}R")
cov.to_pickle('cov15.pkl')
