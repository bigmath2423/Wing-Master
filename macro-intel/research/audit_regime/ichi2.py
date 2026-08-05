import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0,'.')
from core_import import *
from scipy import stats
exec(open('ichimoku.py').read().split('print("="*126); print("REFERENCE")')[0].replace('print("="*126)',''))
def run(tu,td,aL,aS):
    return simulate(df,K['atr'],cooldown((tu&aL.fillna(False)).fillna(False)),
        cooldown((td&aS.fillna(False)).fillna(False)),
        ExitPlan(sl_atr=2.5,tp1_r=99,tp2_r=99,tp3_r=99,part1=0,part2=0,
                 breakeven_after_tp1=False,trail_r=0.3,trail_start_r=1.5),COSTS)
tRef=run(*BOS,BASE[0],BASE[1]); rRef=tRef.R.values
cands={
 'declencheur = sortie du nuage M15': run(TRIG['sortie du nuage'][0].fillna(False),TRIG['sortie du nuage'][1].fillna(False),BASE[0],BASE[1]),
 'filtre ajoute = D1 au-dessus du nuage': run(*BOS,BASE[0]&COND['D1 au-dessus du nuage'][0].fillna(False),
                                                   BASE[1]&COND['D1 au-dessus du nuage'][1].fillna(False)),
}
print("A) TEST DE SIGNIFICATIVITE CONTRE LA REFERENCE (v11, E=+0.185 R)\n")
ps=[]
for k,t in cands.items():
    r=t.R.values; tt,pv=stats.ttest_ind(r,rRef,equal_var=False); ps.append((k,pv,r))
    rng=np.random.default_rng(31)
    bs=np.array([rng.choice(r,len(r)).mean()-rng.choice(rRef,len(rRef)).mean() for _ in range(10000)])
    print(f"  {k:40s} dE={r.mean()-rRef.mean():+.3f}R  t={tt:+.2f}  p={pv:.3f}  IC95 [{np.percentile(bs,2.5):+.3f} ; {np.percentile(bs,97.5):+.3f}]")
print(f"\n  Benjamini-Hochberg sur les 20 hypotheses Ichimoku testees (FDR 10 %) :")
for rank,(k,pv,_) in enumerate(sorted(ps,key=lambda x:x[1])):
    seuil=(rank+1)/20*0.10
    print(f"    {k:40s} p={pv:.3f}  seuil={seuil:.4f}  {'RETENU' if pv<=seuil else '—'}")

print("\n\nB) LE NUAGE D1 EST-IL MEILLEUR QUE L'EMA20 D1 ? (remplacement, pas ajout)\n")
b2=(K['biasW']==True); b2s=(K['biasW']==False)
variants={
 'biais D1 = EMA20 (actuel)'   : ((K['htf']==True)&(c>K['vwap'])&(K['biasD']==True)&b2&(c>K['poc']),
                                  (K['htf']==False)&(c<K['vwap'])&(K['biasD']==False)&b2s&(c<K['poc'])),
 'biais D1 = nuage Ichimoku'   : ((K['htf']==True)&(c>K['vwap'])&COND['D1 au-dessus du nuage'][0]&b2&(c>K['poc']),
                                  (K['htf']==False)&(c<K['vwap'])&COND['D1 au-dessus du nuage'][1]&b2s&(c<K['poc'])),
 'biais D1 = les DEUX'         : ((K['htf']==True)&(c>K['vwap'])&(K['biasD']==True)&COND['D1 au-dessus du nuage'][0]&b2&(c>K['poc']),
                                  (K['htf']==False)&(c<K['vwap'])&(K['biasD']==False)&COND['D1 au-dessus du nuage'][1]&b2s&(c<K['poc'])),
}
for k,(aL,aS) in variants.items():
    t=run(*BOS,aL,aS); m=metrics(t,k)
    a=metrics(t[t.t_in<'2024-08-01'],'')['E']; b=metrics(t[t.t_in>='2024-08-01'],'')['E']
    print(f"  {k:30s} n={m['n']:4d} WR={m['wr']:5.1f}% PF={m['pf']:6.3f} E={m['E']:+.3f} DD={m['dd']:6.1f} "
          f"tot={m['tot']:+6.1f}R t={m['t']:+5.2f} | appr {a:+.3f} valid {b:+.3f} ecart {abs(b-a):.3f}")
ov=(K['biasD']==True)&COND['D1 au-dessus du nuage'][0]
print(f"\n  Recouvrement : quand D1 > EMA20, le prix est aussi au-dessus du nuage D1 dans "
      f"{100*ov.sum()/max((K['biasD']==True).sum(),1):.1f} % des bougies.")

print("\n\nC) SORTIE DU NUAGE vs LES AUTRES DECLENCHEURS (memes filtres)\n")
for k,(tu,td) in [('BOS',BOS),('Donchian 48',don(48)),('sortie du nuage',TRIG['sortie du nuage'])]:
    t=run(tu.fillna(False),td.fillna(False),BASE[0],BASE[1]); m=metrics(t,k)
    a=metrics(t[t.t_in<'2024-08-01'],'')['E']; b=metrics(t[t.t_in>='2024-08-01'],'')['E']
    print(f"  {k:20s} n={m['n']:4d} PF={m['pf']:6.3f} E={m['E']:+.3f} DD={m['dd']:6.1f} tot={m['tot']:+6.1f}R "
          f"t={m['t']:+5.2f} | appr {a:+.3f} valid {b:+.3f} ecart {abs(b-a):.3f}")
tN=run(TRIG['sortie du nuage'][0].fillna(False),TRIG['sortie du nuage'][1].fillna(False),BASE[0],BASE[1])
tD=run(*don(48),BASE[0],BASE[1])
tt,pv=stats.ttest_ind(tN.R.values,tD.R.values,equal_var=False)
print(f"\n  nuage vs Donchian48 : dE={tN.R.mean()-tD.R.mean():+.3f} R  p={pv:.3f}")
print(f"  total : nuage {tN.R.sum():+.1f} R contre Donchian {tD.R.sum():+.1f} R sur la meme periode")
