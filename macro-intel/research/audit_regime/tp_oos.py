import pandas as pd, numpy as np
p='/root/.claude/uploads/b22822dc-6a41-522c-931f-c596aee488bc/89f8f18e-XAU_Momentum_v11.csv'
d=pd.read_csv(p,encoding='utf-8-sig'); d.columns=[c.strip() for c in d.columns]
rows=[]
for tn,sub in d.groupby('Numéro de trade'):
    e=sub[sub['Type'].str.contains('Entrer',na=False)]; x=sub[sub['Type'].str.contains('Sortir',na=False)]
    if len(e)==0 or len(x)==0: continue
    e0=e.iloc[0]
    rows.append(dict(dt=pd.to_datetime(e0['Date et heure']),pct=float(e0['Retour %']),
        mfe=float(e0['Excursion favorable %']),mae=abs(float(e0['Excursion adverse %'])),
        exit=str(x.iloc[-1]['Signal']),pnl=float(e0['P&L net EUR'])))
t=pd.DataFrame(rows).sort_values('dt').reset_index(drop=True)
Rr=abs(t.loc[t.pnl<=0,'pct'].median())
for c in ['pct','mfe','mae']: t[c+'R']=t[c]/Rr
sl=t[t.exit=='SL']
print(f"Coherence : sur les sorties SL, excursion adverse mediane = {sl.maeR.median():.3f} R (attendu ~1.00)")
print(f"            perte mediane = {sl.pctR.median():.3f} R\n")

def sim_tp(s,tp):
    """TP fixe a `tp` R, MEME stop de 1 R. Le MFE enregistre etant tronque par la
    sortie reelle, un trade classe 'TP non atteint' aurait pu l'atteindre plus
    tard : on SOUS-ESTIME donc le TP. Le resultat est un plancher."""
    out=[]
    for _,r in s.iterrows():
        # PRECEDENCE CORRECTE : l'excursion favorable enregistree s'est produite
        # PENDANT le trade, donc AVANT sa sortie. Si elle atteint le TP, le TP
        # etait touche en premier — meme si le trade a fini au stop.
        if r.mfeR>=tp: out.append(tp)
        elif r.maeR>=0.98: out.append(-1.0)
        else: out.append(r.pctR)
    a=np.array(out); w=a[a>0]; lo=a[a<=0]
    return dict(n=len(a),wr=100*len(w)/len(a),pf=(w.sum()/abs(lo.sum())) if lo.sum()<0 else np.inf,E=a.mean())

CUT=pd.Timestamp('2022-04-29')
oos=t[t.dt<CUT]; ins=t[t.dt>=CUT]
print("TP FIXE, MEME STOP — le win rate monte-t-il HORS ECHANTILLON aussi ?")
print(f"{'TP':>7s} | {'2020-2022 INEDIT':^33s} | {'2022-2026 connu':^33s}")
print(f"{'':7s} | {'n':>4s} {'WR':>7s} {'PF':>7s} {'E':>8s} | {'n':>4s} {'WR':>7s} {'PF':>7s} {'E':>8s}")
for tp in [0.5,0.75,1.0,1.25,1.5,2.0]:
    A=sim_tp(oos,tp); B=sim_tp(ins,tp)
    print(f"{tp:7.2f} | {A['n']:4d} {A['wr']:6.1f}% {A['pf']:7.3f} {A['E']:+8.3f} | "
          f"{B['n']:4d} {B['wr']:6.1f}% {B['pf']:7.3f} {B['E']:+8.3f}")
def ref(s):
    a=s.pctR.values; w=a[a>0]; lo=a[a<=0]
    return len(a),100*len(w)/len(a),w.sum()/abs(lo.sum()),a.mean()
ao=ref(oos); ai=ref(ins)
print(f"{'ACTUEL':>7s} | {ao[0]:4d} {ao[1]:6.1f}% {ao[2]:7.3f} {ao[3]:+8.3f} | {ai[0]:4d} {ai[1]:6.1f}% {ai[2]:7.3f} {ai[3]:+8.3f}")

print("\n\nCE QU'IL FAUDRAIT POUR UN PF DE 2")
print("PF = (WR x gain moyen) / ((1 - WR) x perte moyenne)\n")
for wr in [0.65,0.70,0.75]:
    print(f"   a {wr:.0%} de reussite : gain moyen = {2.0*(1-wr)/wr:.2f} x la perte moyenne")
a=t.pctR.values; w=a[a>0]; lo=a[a<=0]
print(f"\n   systeme actuel : WR {100*len(w)/len(a):.1f}% | gain moyen {w.mean():.2f} R | perte moyenne {abs(lo.mean()):.2f} R")
print(f"                    rapport {w.mean()/abs(lo.mean()):.2f} | PF {w.sum()/abs(lo.sum()):.3f}")
print(f"\n   Pour un PF de 2 sans rien changer d'autre, il faudrait que chaque gain")
print(f"   soit {2.0*abs(lo.sum())/w.sum():.2f}x plus grand qu'aujourd'hui, ou qu'une perte sur deux disparaisse.")
