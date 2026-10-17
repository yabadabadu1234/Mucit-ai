# Kırılma (net=0) haritası: her senaryoda s (kayıtlı geçiş) × phi (sahte fatura) ve s × onlem.
import numpy as np, json
from model import *
def net4(p): return npv(p)[1][3]['net']/1e9
S=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
PH=[0,0.01,0.02,0.05,0.1,0.2]
out={}
for ad in SENARYO:
    base=sc(ad); g=[]
    for ph in PH:
        row=[]
        for s in S:
            p=dict(base); p['s_kayitli']=s; p['phi']=ph; p['n_yeni_pay']=1-s-p['u_ucretli']
            row.append(round(net4(p),2))
        g.append(row)
    # s* (net=0) with phi taban
    sst=None
    for s in np.linspace(0,1,201):
        p=dict(base); p['s_kayitli']=s; p['n_yeni_pay']=1-s-p['u_ucretli']
        if net4(p)<0: sst=float(s); break
    # phi* (net=0) with s taban
    phst=None
    for ph in np.linspace(0,0.5,501):
        p=dict(base); p['phi']=ph
        if net4(p)<0: phst=float(ph); break
    out[ad]=dict(grid_s=S,grid_phi=PH,net=g,s_kirilma=sst,phi_kirilma=phst)
    print(ad,"s* =",sst,"  phi* =",phst)
    print("  phi\\s "+" ".join("%5.1f"%s for s in S))
    for ph,row in zip(PH,g): print("  %5.2f "%ph+" ".join("%5.1f"%x for x in row))
json.dump(out,open('kirilma_izgara.json','w'),ensure_ascii=False,indent=1)
