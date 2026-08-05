import pandas as pd, numpy as np
from scipy import stats
p='/root/.claude/uploads/b22822dc-6a41-522c-931f-c596aee488bc/89f8f18e-XAU_Momentum_v11.csv'
d=pd.read_csv(p,encoding='utf-8-sig'); d.columns=[c.strip() for c in d.columns]
rows=[]
for tn,sub in d.groupby('Numéro de trade'):
    e=sub[sub['Type'].str.contains('Entrer',na=False)]; x=sub[sub['Type'].str.contains('Sortir',na=False)]
    if len(e)==0 or len(x)==0: continue
    e0=e.iloc[0]
    rows.append(dict(dt=pd.to_datetime(e0['Date et heure']),pct=float(e0['Retour %']),
        mfe=float(e0['Excursion favorable %']),mae=abs(float(e0['Excursion adverse %'])),
        exit=str(x.iloc[-1]['Signal'])))
t=pd.DataFrame(rows).sort_values('dt').reset_index(drop=True)
Rr=abs(t.loc[t.pct<=0,'pct'].median())
for c in ['pct','mfe','mae']: t[c+'R']=t[c]/Rr
print(f"Controle : MFE minimum des sorties en trailing = {t.loc[t.exit=='Trailing','mfeR'].min():.2f} R")
print(f"           => tout TP <= {t.loc[t.exit=='Trailing','mfeR'].min():.2f} R est simule EXACTEMENT\n")

def sim(s,tp):
    a=np.where(s.mfeR.values>=tp, tp, np.where(s.maeR.values>=0.98, -1.0, s.pctR.values))
    w=a[a>0]; lo=a[a<=0]; eq=np.cumsum(a)
    dd=(eq-np.maximum.accumulate(np.concatenate([[0],eq]))[1:]).min()
    st=0;mx=0
    for x in a: st=st+1 if x<=0 else 0; mx=max(mx,st)
    return dict(n=len(a),wr=100*len(w)/len(a),pf=w.sum()/abs(lo.sum()),E=a.mean(),dd=dd,streak=mx,
                t=a.mean()/(a.std(ddof=1)/np.sqrt(len(a))),tot=a.sum(),arr=a)
def act(s):
    a=s.pctR.values; w=a[a>0]; lo=a[a<=0]; eq=np.cumsum(a)
    dd=(eq-np.maximum.accumulate(np.concatenate([[0],eq]))[1:]).min()
    st=0;mx=0
    for x in a: st=st+1 if x<=0 else 0; mx=max(mx,st)
    return dict(n=len(a),wr=100*len(w)/len(a),pf=w.sum()/abs(lo.sum()),E=a.mean(),dd=dd,streak=mx,
                t=a.mean()/(a.std(ddof=1)/np.sqrt(len(a))),tot=a.sum(),arr=a)
CUT=pd.Timestamp('2022-04-29')
segs=[('2020-2022 INEDIT',t[t.dt<CUT]),('2022-2026 connu',t[t.dt>=CUT]),('ENSEMBLE 2020-2026',t)]
print(f"{'config':>12s} | "+" | ".join(f"{n:^40s}" for n,_ in segs))
print(f"{'':12s} | "+" | ".join(f"{'n':>4s} {'WR':>6s} {'PF':>6s} {'E':>7s} {'DD':>7s} {'t':>5s}" for _ in segs))
for lab,tp in [('TP 0.40 R',0.40),('TP 0.50 R',0.50),('TP 0.60 R',0.60),('TP 0.75 R',0.75),('TP 1.00 R',1.00),('ACTUEL',None)]:
    line=f"{lab:>12s} | "
    for _,s in segs:
        m=act(s) if tp is None else sim(s,tp)
        line+=f"{m['n']:4d} {m['wr']:5.1f}% {m['pf']:6.3f} {m['E']:+7.3f} {m['dd']:7.1f} {m['t']:+5.2f} | "
    print(line)

print("\n\nDETAIL DE L'OPTION 'WIN RATE' (TP 0.50 R) vs L'ACTUELLE, sur les 6.3 ans")
A=act(t); B=sim(t,0.50)
print(f"{'':22s} {'ACTUEL':>12s} {'TP 0.50 R':>12s}")
for k,lab in [('n','trades'),('wr','win rate %'),('pf','profit factor'),('E','esperance R'),
              ('dd','drawdown (R)'),('streak','pertes d affilee'),('t','t-stat'),('tot','total R')]:
    print(f"{lab:22s} {A[k]:12.2f} {B[k]:12.2f}")
tt,pv=stats.ttest_rel(B['arr'],A['arr'])
print(f"\ndifference d'esperance : {B['E']-A['E']:+.3f} R par trade   (t apparie {tt:+.2f}, p={pv:.4f})")
print(f"sur 124 trades par an : {(B['E']-A['E'])*124:+.1f} R par an, soit {(B['E']-A['E'])*124*1.0:+.1f} % du capital a 1 % de risque")
