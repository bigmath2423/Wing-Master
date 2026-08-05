import sys, numpy as np, pandas as pd
sys.path.insert(0,'.')
from v11sim import load_mt5
from scipy import stats
U='/root/.claude/uploads/b22822dc-6a41-522c-931f-c596aee488bc/'
df=load_mt5(U+'4b5607af-XAUUSD_M15_202204290100_202608041500.csv')
h,l,c,o,v=df.high,df.low,df.close,df.open,df.volume
pc=c.shift(); tr=pd.concat([h-l,(h-pc).abs(),(l-pc).abs()],axis=1).max(axis=1)
atr=tr.ewm(alpha=1/14,adjust=False).mean()
day=pd.Series(df.index.date,index=df.index)
hl2=(h+l)/2

# --- POC / VAH / VAL quotidiens ---
recs={}
for d_,sub in hl2.groupby(day):
    vol=v.loc[sub.index]; lo_,hi_=sub.min(),sub.max()
    if len(sub)<20 or hi_<=lo_: continue
    step=(hi_-lo_)/50
    k=np.minimum(49,np.maximum(0,((sub-lo_)/step).astype(int)))
    acc=np.bincount(k,weights=vol.values,minlength=50)
    kx=acc.argmax(); poc=lo_+(kx+0.5)*step
    tot=acc.sum(); a1=b1=kx; cum=acc[kx]
    while cum<tot*0.70 and (a1>0 or b1<49):
        up_=acc[b1+1] if b1<49 else -1; dn_=acc[a1-1] if a1>0 else -1
        if up_>=dn_ and b1<49: b1+=1; cum+=up_
        elif a1>0: a1-=1; cum+=dn_
        else: break
    recs[d_]=dict(poc=poc,vah=lo_+(b1+1)*step,val=lo_+a1*step,end=sub.index[-1])
days=sorted(recs)
print(f"{len(days)} journees profilees\n")

idx=df.index; H=h.values; L=l.values; C=c.values; A=atr.values
pos={t:i for i,t in enumerate(idx)}

def first_touch(level, start_i, horizon=96*20):
    """premier retour du prix sur le niveau apres start_i ; renvoie (i, sens d'approche)"""
    end=min(len(idx),start_i+horizon)
    for i in range(start_i,end):
        if L[i]<=level<=H[i]:
            return i, (1 if C[start_i]<level else -1)   # 1 = on monte vers le niveau
    return None,None

def forward(i,sens,k):
    j=min(len(idx)-1,i+k)
    return sens*(C[j]-C[i])/A[i]     # >0 = le prix a CONTINUE dans le sens de l'approche

def study(name, levels):
    """levels : liste de (index de depart, prix du niveau)"""
    out={k:[] for k in (12,24,48,96)}
    n=0
    for si,lv in levels:
        i,s=first_touch(lv,si)
        if i is None or not np.isfinite(A[i]) or A[i]<=0: continue
        n+=1
        for k in out: out[k].append(forward(i,s,k))
    return name,n,{k:np.array(x) for k,x in out.items()}

# --- niveaux testes ---
pocL=[];vahL=[];valL=[];ctrl=[]
rng=np.random.default_rng(5)
for d_ in days:
    r=recs[d_]; si=pos[r['end']]+1
    if si>=len(idx)-96: continue
    pocL.append((si,r['poc'])); vahL.append((si,r['vah'])); valL.append((si,r['val']))
    # controle : un niveau ALEATOIRE dans la meme fourchette de prix, meme jour
    span=r['vah']-r['val']
    ctrl.append((si, r['poc']+rng.uniform(-1.5,1.5)*max(span,1e-9)))

print("REACTION AU PREMIER RETOUR SUR LE NIVEAU")
print("(valeur = continuation dans le sens de l'approche, en ATR. NEGATIF = le prix a ete repousse)\n")
print(f"{'niveau':22s} {'n':>4s} {'+3h':>8s} {'+6h':>8s} {'+12h':>8s} {'+24h':>8s}")
res={}
for nm,lv in [('POC de la veille',pocL),('VAH (haut de VA)',vahL),('VAL (bas de VA)',valL),('CONTROLE aleatoire',ctrl)]:
    nm,n,d_=study(nm,lv); res[nm]=d_
    print(f"{nm:22s} {n:4d} "+" ".join(f"{d_[k].mean():+8.3f}" for k in (12,24,48,96)))

print("\nECART AVEC LE CONTROLE (test de Welch)")
for nm in ['POC de la veille','VAH (haut de VA)','VAL (bas de VA)']:
    line=f"  {nm:22s} "
    for k in (12,24,48,96):
        a,b=res[nm][k],res['CONTROLE aleatoire'][k]
        t,p=stats.ttest_ind(a,b,equal_var=False)
        line+=f"{a.mean()-b.mean():+7.3f}(p={p:.3f}) "
    print(line)
