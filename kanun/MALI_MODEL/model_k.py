import numpy as np, json
from model import *
def prim_k(p,H):
    gelir=(1-p['gider'])*H
    return np.clip(p['kp_oran']*gelir,p['kp_taban'],p['kp_tavan'])
def yil_k(p,i,ilk):
    y=yil(p,p['ramp'][i],ilk=ilk)
    if i<p['kulucka']: return y,0.0,0.0
    H,w=agirliklar(p); N=p['n_toplam']*p['ramp'][i]
    nyeni=1-p['s_kayitli']-p['u_ucretli']
    gelirk=N*nyeni*float((w*prim_k(p,H)).sum())
    maliyet=p['kp_maliyet_pay']*gelirk
    return y,gelirk,maliyet
def npv_k(p):
    top=0.0; ys=[]
    for i in range(5):
        y,g,m=yil_k(p,i,i==0); n=y['net']+g-m; ys.append(n); top+=n/(1+p['iskonto'])**(i+1)
    return top,ys
def kp(ad,**kw):
    p=sc(ad); p.update(dict(kulucka=3,kp_oran=0.0,kp_taban=0.0,kp_tavan=1e12,kp_maliyet_pay=0.6)); p.update(kw); return p
if __name__=="__main__":
    out={}
    for ad in SENARYO:
        for nm,kw in [("S (seçilen)",{}),("K1 kuluçka3 + %5 gelir primi",dict(kp_oran=0.05)),("K2 kuluçka3 + %8",dict(kp_oran=0.08)),("K3 kuluçka2 + %5",dict(kp_oran=0.05,kulucka=2)),("K4 kuluçka3 + %5, maliyet %100",dict(kp_oran=0.05,kp_maliyet_pay=1.0))]:
            v,ys=npv_k(kp(ad,**kw)); out.setdefault(ad,{})[nm]=dict(npv5=v,yil4=ys[3],yil5=ys[4]); print(ad,nm,"yıl4 %.2f yıl5 %.2f npv5 %.2f mlr"%(ys[3]/1e9,ys[4]/1e9,v/1e9))
    json.dump(out,open('sonuc_k.json','w'),ensure_ascii=False,indent=1)
