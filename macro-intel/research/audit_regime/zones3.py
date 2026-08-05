import sys, numpy as np, pandas as pd
sys.path.insert(0,'.')
from v11sim import load_mt5
from scipy import stats
U='/root/.claude/uploads/b22822dc-6a41-522c-931f-c596aee488bc/'
df=load_mt5(U+'4b5607af-XAUUSD_M15_202204290100_202608041500.csv')
h,l,c,v=df.high,df.low,df.close,df.volume
pc=c.shift(); tr=pd.concat([h-l,(h-pc).abs(),(l-pc).abs()],axis=1).max(axis=1)
atr=tr.ewm(alpha=1/14,adjust=False).mean()
H,L,C,A,V=h.values,l.values,c.values,atr.values,v.values
N=len(df); hl2=((h+l)/2).values
def fwd(i,s,k):
    j=min(N-1,i+k); return s*(C[j]-C[i])/A[i]
def touch(level,si,horizon=96*30):
    for i in range(si,min(N,si+horizon)):
        if L[i]<=level<=H[i]: return i,(1 if C[si]<level else -1)
    return None,None
def study(levels):
    out={k:[] for k in (12,24,48,96)}
    for si,lv in levels:
        i,s=touch(lv,si)
        if i is None or not np.isfinite(A[i]) or A[i]<=0: continue
        for k in out: out[k].append(fwd(i,s,k))
    return {k:np.array(x) for k,x in out.items()}

# Pour chaque profil : on prend le HVN, puis un niveau APPARIE — meme distance
# au prix, meme cote, mais volume FAIBLE. Seule la densite de volume differe.
hvn=[];pair=[];lvn_far=[]
for si in range(600,N-96*10,96):
    w=slice(si-500,si)
    seg=hl2[w]; vol=V[w]
    lo_,hi_=seg.min(),seg.max()
    if hi_<=lo_: continue
    step=(hi_-lo_)/30
    k=np.minimum(29,np.maximum(0,((seg-lo_)/step).astype(int)))
    acc=np.bincount(k,weights=vol,minlength=30)
    lv=lo_+(np.arange(30)+0.5)*step
    kx=int(acc.argmax()); px=lv[kx]
    d=px-C[si]                                   # distance signee au prix
    if abs(d)<1e-9: continue
    # candidats du MEME cote, a distance comparable (+-30%), volume dans le tiers bas
    same=np.where(np.sign(lv-C[si])==np.sign(d))[0]
    if len(same)<4: continue
    dist=np.abs(lv[same]-C[si])
    near=same[(dist>abs(d)*0.7)&(dist<abs(d)*1.3)]
    if len(near)==0: continue
    lowvol=near[acc[near]<=np.percentile(acc[same],40)]
    if len(lowvol)==0: continue
    hvn.append((si,px)); pair.append((si,lv[int(lowvol[np.argmin(np.abs(acc[lowvol]))])]))

print("HVN vs NIVEAU APPARIE (meme distance, meme cote, volume faible)")
print("valeur = continuation dans le sens de l'approche, en ATR ; negatif = repousse\n")
print(f"{'niveau':34s} {'n':>4s} {'+3h':>8s} {'+6h':>8s} {'+12h':>8s} {'+24h':>8s}")
a=study(hvn); b=study(pair)
for nm,d in [('HVN (volume le plus dense)',a),('APPARIE (volume faible)',b)]:
    print(f"{nm:34s} {len(d[12]):4d} "+" ".join(f"{d[k].mean():+8.3f}" for k in (12,24,48,96)))
print(f"\n{'ecart HVN - apparie':34s} {'':4s} "+" ".join(f"{a[k].mean()-b[k].mean():+8.3f}" for k in (12,24,48,96)))
print(f"{'p (Welch)':34s} {'':4s} "+" ".join(f"{stats.ttest_ind(a[k],b[k],equal_var=False)[1]:8.3f}" for k in (12,24,48,96)))
