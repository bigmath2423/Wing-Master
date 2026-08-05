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
idx=df.index; N=len(idx)
day=pd.Series(idx.date,index=idx); hl2=((h+l)/2)

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
def show(nm,d,ref=None):
    line=f"{nm:30s} {len(d[12]):4d} "
    for k in (12,24,48,96):
        line+=f"{d[k].mean():+8.3f}"
        if ref is not None:
            t,p=stats.ttest_ind(d[k],ref[k],equal_var=False); line+=f"(p{p:.2f})"
    print(line)

# ---------- 1. POC "vierges" : jamais retouches depuis N jours ----------
recs={}
for d_,sub in hl2.groupby(day):
    vol=v.loc[sub.index]; lo_,hi_=sub.min(),sub.max()
    if len(sub)<20 or hi_<=lo_: continue
    step=(hi_-lo_)/50
    k=np.minimum(49,np.maximum(0,((sub-lo_)/step).astype(int)))
    acc=np.bincount(k,weights=vol.values,minlength=50)
    recs[d_]=(lo_+(acc.argmax()+0.5)*step, sub.index[-1])
days=sorted(recs); pos={t:i for i,t in enumerate(idx)}
rng=np.random.default_rng(9)
vierge={2:[],5:[],10:[]}; ctrl=[]
for d_ in days:
    poc,end=recs[d_]; si=pos[end]+1
    if si>=N-96: continue
    for nd in vierge:
        j=min(N,si+96*nd)
        if not ((L[si:j]<=poc)&(poc<=H[si:j])).any():      # pas retouche pendant nd jours
            vierge[nd].append((j,poc))
    ctrl.append((si,C[si]*(1+rng.uniform(-0.012,0.012))))
print("A) POC VIERGES — un POC jamais retouche depuis N jours reagit-il plus ?")
print(f"{'niveau':30s} {'n':>4s} {'+3h':>8s} {'+6h':>8s} {'+12h':>8s} {'+24h':>8s}")
rc=study(ctrl); show('CONTROLE aleatoire',rc)
for nd in (2,5,10): show(f'POC vierge depuis {nd} jours',study(vierge[nd]),rc)

# ---------- 2. HVN / LVN sur profil glissant 500 bougies ----------
print("\nB) NOEUDS DE VOLUME sur profil glissant (500 bougies, 30 niveaux)")
hvn=[];lvn=[]
for si in range(600,N-96*10,96):        # un profil par jour
    w=slice(si-500,si)
    lo_,hi_=hl2.values[w].min(),hl2.values[w].max()
    if hi_<=lo_: continue
    step=(hi_-lo_)/30
    k=np.minimum(29,np.maximum(0,((hl2.values[w]-lo_)/step).astype(int)))
    acc=np.bincount(k,weights=V[w],minlength=30)
    hvn.append((si,lo_+(acc.argmax()+0.5)*step))
    inner=acc.copy(); inner[:5]=inner.max(); inner[-5:]=inner.max()   # ignorer les extremes vides
    lvn.append((si,lo_+(inner.argmin()+0.5)*step))
print(f"{'niveau':30s} {'n':>4s} {'+3h':>8s} {'+6h':>8s} {'+12h':>8s} {'+24h':>8s}")
c2=[(si,C[si]*(1+rng.uniform(-0.012,0.012))) for si,_ in hvn]
rc2=study(c2); show('CONTROLE aleatoire',rc2)
show('HVN (noeud de volume haut)',study(hvn),rc2)
show('LVN (noeud de volume bas)',study(lvn),rc2)

# ---------- 3. Zones d'offre : sommets a volume climax ----------
print("\nC) ZONES DE VENTE PENDANT UNE HAUSSE (sommet a volume climax)")
sw=10
isph=(h.rolling(2*sw+1,center=True).max()==h).values
volmed=pd.Series(V).rolling(500).median().values
sup=[];sup_hi=[]
for i in range(600,N-96*10):
    if isph[i] and np.isfinite(volmed[i]) and volmed[i]>0:
        # tendance haussiere : cloture au-dessus de sa moyenne 200
        if C[i]>pd.Series(C).rolling(200).mean().values[i]:
            (sup_hi if V[i]>2*volmed[i] else sup).append((i+sw,H[i]))
print(f"{'niveau':30s} {'n':>4s} {'+3h':>8s} {'+6h':>8s} {'+12h':>8s} {'+24h':>8s}")
c3=[(si,C[si]*(1+rng.uniform(-0.012,0.012))) for si,_ in sup]
rc3=study(c3); show('CONTROLE aleatoire',rc3)
show('sommet, volume normal',study(sup),rc3)
show('sommet, volume climax (>2x)',study(sup_hi),rc3)
