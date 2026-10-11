import numpy as np, json, model
from model import *
from model_k import prim_k
BAZ=dict(kp_taban=0.0,kp_tavan=1e12,kulucka=3,kp_oran=0.0,kp_maliyet_pay=0.6,eps_pp=0.0,dolasma=0.0,pej=0.0,pej_onlem=0.0,pej_sgk=0.30,pej_vergi=0.15)
def kos(p):
    H,w=agirliklar(p); ys=[]
    for i in range(5):
        r=p['ramp'][i]; y=yil(p,r,ilk=(i==0)); ys.append(y['net'])
    return ys[3]
orj=model.tevkifat
def sonuc(oran):
    if oran is None: model.tevkifat=orj
    else: model.tevkifat=lambda h,g,o=oran: o*(1-g)*h
    out={}
    for ad in ["Kötümser","Orta","İyimser"]:
        p=sc(ad); p.update(BAZ); out[ad]=kos(p)/1e9
    return out
print("kademeli (teklif)  :",{k:round(v,2) for k,v in sonuc(None).items()})
for o in (0.15,):
    print("düz tevkifat oranı = ham %0.2f x safi(0.70) = %.3f:"%(o,o*0.7),{k:round(v,2) for k,v in sonuc(o).items()})
model.tevkifat=orj
