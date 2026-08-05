import sys, numpy as np, pandas as pd
sys.path.insert(0,'/home/user/Wing-Master/macro-intel/research')
from core.backtest import simulate, ExitPlan, Costs

U='/root/.claude/uploads/b22822dc-6a41-522c-931f-c596aee488bc/'
COSTS=Costs(per_unit=0.20, risk_pct=1.0)

def load(p=U+'4b5607af-XAUUSD_M15_202204290100_202608041500.csv'):
    d=pd.read_csv(p,sep='\t'); d.columns=[c.strip('<>').lower() for c in d.columns]
    d['dt']=pd.to_datetime(d['date']+' '+d['time'],format='%Y.%m.%d %H:%M:%S')
    d=d.set_index('dt')[['open','high','low','close','tickvol']].sort_index()
    return d.rename(columns={'tickvol':'volume'})[lambda x: ~x.index.duplicated()]

def components(df, swing=10, atr_len=14, htf_ema=50, bias_d=20, bias_w=10):
    """Toutes les briques, calculees UNE fois, chacune isolable."""
    h,l,c,o,v=df.high,df.low,df.close,df.open,df.volume
    pc=c.shift(); tr=pd.concat([h-l,(h-pc).abs(),(l-pc).abs()],axis=1).max(axis=1)
    K={}
    K['atr']=tr.ewm(alpha=1/atr_len,adjust=False,min_periods=atr_len).mean()
    # --- structure / BOS (le declencheur actuel)
    w=2*swing+1
    ph=h.rolling(w,center=True).max().eq(h); pl=l.rolling(w,center=True).min().eq(l)
    sh=h.where(ph).shift(swing).ffill(); sl_=l.where(pl).shift(swing).ffill()
    K['bosUp']=((c>sh)&(c.shift()<=sh.shift())&sh.eq(sh.shift())).fillna(False)
    K['bosDn']=((c<sl_)&(c.shift()>=sl_.shift())&sl_.eq(sl_.shift())).fillna(False)
    K['trend']=pd.Series(np.where(K['bosUp'],1,np.where(K['bosDn'],-1,np.nan)),index=df.index).ffill().fillna(0)
    # --- H1
    h1=c.resample('1h').last().dropna()
    h1b=(h1>h1.ewm(span=htf_ema,adjust=False,min_periods=htf_ema).mean()).shift(1)
    K['htf']=pd.Series(df.index.floor('1h').map(h1b),index=df.index)
    # --- VWAP session
    day=pd.Series(df.index.date,index=df.index); hlc3=(h+l+c)/3
    K['vwap']=(hlc3*v).groupby(day).cumsum()/v.groupby(day).cumsum()
    # --- biais D1 / W1
    d1=c.resample('1D').last().dropna()
    d1b=(d1>d1.ewm(span=bias_d,adjust=False,min_periods=bias_d).mean()).shift(1)
    w1=c.resample('W').last().dropna()
    w1b=(w1>w1.ewm(span=bias_w,adjust=False,min_periods=bias_w).mean()).shift(1)
    K['biasD']=pd.Series(df.index.normalize().map(d1b),index=df.index)
    ws=pd.Series(df.index,index=df.index).map(lambda x: w1b.asof(x))
    K['biasW']=pd.Series(ws.values,index=df.index)
    # --- POC veille
    hl2=(h+l)/2; pocs={}
    for dd,sub in hl2.groupby(day):
        vv=v.loc[sub.index]; lo_,hi_=sub.min(),sub.max()
        if len(sub)<6 or not np.isfinite(lo_) or hi_<=lo_: pocs[dd]=np.nan; continue
        st=(hi_-lo_)/50
        k=np.minimum(49,np.maximum(0,((sub-lo_)/st).astype(int)))
        pocs[dd]=lo_+(np.bincount(k,weights=vv.values,minlength=50).argmax()+0.5)*st
    ds=sorted(pocs); K['poc']=day.map({ds[i]:pocs[ds[i-1]] for i in range(1,len(ds))})
    # --- briques ALTERNATIVES (hors SMC)
    K['donchUp']=(c>h.shift().rolling(48).max()).fillna(False)      # cassure 12 h
    K['donchDn']=(c<l.shift().rolling(48).min()).fillna(False)
    K['ema20']=c.ewm(span=20,adjust=False).mean()
    K['ema200']=c.ewm(span=200,adjust=False).mean()
    K['tsmom']=(c-c.shift(96*20))                                    # momentum 20 jours
    K['volN']=K['atr']/c                                             # volatilite normalisee
    K['volMed']=K['volN'].rolling(96*20,min_periods=500).median()
    K['ret']=c.pct_change()
    K['rv']=K['ret'].rolling(96).std()                                # vol realisee 24 h
    # ratio de variance : >1 = tendance, <1 = retour a la moyenne
    K['vr']=(K['ret'].rolling(96).sum().rolling(480).std()/(K['rv']*np.sqrt(96))).replace([np.inf,-np.inf],np.nan)
    return K

def cooldown(sig, n=10):
    out=np.zeros(len(sig),bool); last=-10**9; v=np.asarray(sig)
    for i in range(len(v)):
        if v[i] and (i-last)>n: out[i]=True; last=i
    return pd.Series(out,index=sig.index)

def metrics(t,lab=''):
    if t is None or len(t)<30: return dict(nom=lab,n=len(t) if t is not None else 0)
    r=t.R.values; w=r[r>0]; lo=r[r<=0]; eq=np.cumsum(r)
    dd=(eq-np.maximum.accumulate(np.concatenate([[0],eq]))[1:]).min()
    return dict(nom=lab,n=len(r),wr=100*len(w)/len(r),pf=w.sum()/abs(lo.sum()) if lo.sum()<0 else np.inf,
                E=r.mean(),dd=dd,t=r.mean()/(r.std(ddof=1)/np.sqrt(len(r))),tot=r.sum())
def show(m,extra=''):
    if m.get('n',0)<30: print(f"  {m['nom']:38s}  trop peu de trades ({m.get('n',0)})"); return
    print(f"  {m['nom']:38s} n={m['n']:4d} WR={m['wr']:5.1f}% PF={m['pf']:6.3f} E={m['E']:+.3f}R "
          f"DD={m['dd']:6.1f}R t={m['t']:+5.2f}{extra}")
