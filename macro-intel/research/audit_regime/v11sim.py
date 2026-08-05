"""Reproduction fidele de la logique d'entree de v11 + simulateur d'exits."""
import sys, numpy as np, pandas as pd
sys.path.insert(0,'/home/user/Wing-Master/macro-intel/research')
from core.backtest import simulate, ExitPlan, Costs, metrics

def load_mt5(p):
    d=pd.read_csv(p,sep='\t'); d.columns=[c.strip('<>').lower() for c in d.columns]
    d['dt']=pd.to_datetime(d['date']+' '+d['time'],format='%Y.%m.%d %H:%M:%S')
    d=d.set_index('dt')[['open','high','low','close','tickvol']].sort_index()
    d=d.rename(columns={'tickvol':'volume'})
    return d[~d.index.duplicated()]

def v11_signals(df, swing=10, atr_len=14, htf_ema=50, bias_d=20, bias_w=10, cooldown=10):
    h,l,c,o=df.high,df.low,df.close,df.open
    pc=c.shift()
    tr=pd.concat([h-l,(h-pc).abs(),(l-pc).abs()],axis=1).max(axis=1)
    a=tr.ewm(alpha=1/atr_len,adjust=False,min_periods=atr_len).mean()
    # --- structure : pivots confirmes avec `swing` barres de retard + garde de stabilite
    w=2*swing+1
    ph=h.rolling(w,center=True).max().eq(h); pl=l.rolling(w,center=True).min().eq(l)
    sh=h.where(ph).shift(swing).ffill(); sl_=l.where(pl).shift(swing).ffill()
    up=(c>sh)&(c.shift()<=sh.shift())&sh.eq(sh.shift())
    dn=(c<sl_)&(c.shift()>=sl_.shift())&sl_.eq(sl_.shift())
    trend=pd.Series(np.where(up,1,np.where(dn,-1,np.nan)),index=df.index).ffill().fillna(0)
    # --- H1 : cloture H1 precedente vs son EMA50
    h1=c.resample('1h').last().dropna()
    h1b=(h1>h1.ewm(span=htf_ema,adjust=False,min_periods=htf_ema).mean()).shift(1)
    htf=df.index.floor('1h').map(h1b); htf=pd.Series(htf,index=df.index)
    # --- VWAP de session (ancrage journalier)
    day=pd.Series(df.index.date,index=df.index)
    hlc3=(h+l+c)/3
    vw=(hlc3*df.volume).groupby(day).cumsum()/df.volume.groupby(day).cumsum()
    # --- biais D1 + W1 sur bougies CLOTUREES
    d1=c.resample('1D').last().dropna()
    d1b=(d1>d1.ewm(span=bias_d,adjust=False,min_periods=bias_d).mean()).shift(1)
    w1=c.resample('W').last().dropna()
    w1b=(w1>w1.ewm(span=bias_w,adjust=False,min_periods=bias_w).mean()).shift(1)
    bd=pd.Series(df.index.normalize().map(d1b),index=df.index)
    bw=pd.Series(pd.Series(df.index,index=df.index).map(lambda x: w1b.asof(x)),index=df.index)
    # --- POC de la veille
    hl2=(h+l)/2
    pocs={}
    for dd,sub in hl2.groupby(day):
        v=df.volume.loc[sub.index]
        lo_,hi_=sub.min(),sub.max()
        if len(sub)<6 or not np.isfinite(lo_) or hi_<=lo_: pocs[dd]=np.nan; continue
        step=(hi_-lo_)/50
        k=np.minimum(49,np.maximum(0,((sub-lo_)/step).astype(int)))
        pocs[dd]=lo_+(np.bincount(k,weights=v.values,minlength=50).argmax()+0.5)*step
    ds=sorted(pocs); prev={ds[i]:pocs[ds[i-1]] for i in range(1,len(ds))}
    poc=day.map(prev)
    alignL=(trend==1)&(htf==True)&(c>vw)&(bd==True)&(bw==True)&(c>poc)
    alignS=(trend==-1)&(htf==False)&(c<vw)&(bd==False)&(bw==False)&(c<poc)
    rawL=(up&alignL&a.notna()&(a>0)).fillna(False)
    rawS=(dn&alignS&a.notna()&(a>0)).fillna(False)
    # cooldown
    def cd(s):
        out=np.zeros(len(s),bool); last=-10**9; v=s.to_numpy()
        for i in range(len(v)):
            if v[i] and (i-last)>cooldown: out[i]=True; last=i
        return pd.Series(out,index=s.index)
    return cd(rawL),cd(rawS),a,trend

def adx_pct(df,n=14,win=500):
    h,l=df.high,df.low
    pc=df.close.shift()
    tr=pd.concat([h-l,(h-pc).abs(),(l-pc).abs()],axis=1).max(axis=1)
    aw=tr.ewm(alpha=1/n,adjust=False).mean()
    up,dn=h.diff(),-l.diff()
    p=np.where((up>dn)&(up>0),up,0.0); m=np.where((dn>up)&(dn>0),dn,0.0)
    pdi=100*pd.Series(p,index=df.index).ewm(alpha=1/n,adjust=False).mean()/aw
    mdi=100*pd.Series(m,index=df.index).ewm(alpha=1/n,adjust=False).mean()/aw
    dx=100*(pdi-mdi).abs()/(pdi+mdi).replace(0,np.nan)
    return dx.ewm(alpha=1/n,adjust=False).mean().rolling(win,min_periods=200).rank(pct=True)

PLAN=ExitPlan(sl_atr=2.5,tp1_r=99,tp2_r=99,tp3_r=99,part1=0.0,part2=0.0,
              breakeven_after_tp1=False,trail_r=0.3,trail_start_r=1.5)
COSTS=Costs(per_unit=0.20,risk_pct=1.0)
