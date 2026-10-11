import json
from risk import *
out={}
for ad in ["Kötümser","Orta","İyimser"]:
    for nm,kp in [("S",0.0),("K1",0.05)]:
        lo,hi=0.0,1.0
        f=lambda d:kos(p_kur(ad,kp_oran=kp,prim_devam=d))[0]
        if f(0.0)>0: b=0.0
        else:
            for _ in range(50):
                m=(lo+hi)/2
                if f(m)>0: hi=m
                else: lo=m
            b=hi
        out[ad+" "+nm]=b; print(ad,nm,"prim_devam kırılma %.3f"%b)
json.dump(out,open('sonuc_risk2.json','w'),ensure_ascii=False,indent=1)
