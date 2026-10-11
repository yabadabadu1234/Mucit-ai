import json, numpy as np
from model_m import *
H=np.array([1,2,4,8,16,24])*W
TAS={"S (mevcut teklif)":dict(),
 "K1":dict(r_y=0.05,kulucka=3),
 "M-A (tam süreklilik + yeni gelir primi %10, alt eşik 2W, kuluçka 2, alıcı katkısı %2)":dict(r_y=0.10,prog=1.5,e0=2,kulucka=2,levy=0.02),
 "M-B (M-A + eski primi gelirin %40'ı ile sınırlı)":dict(r_y=0.10,prog=1.5,e0=2,kulucka=2,levy=0.02,cap_e=0.4)}
MIT=dict(pej_onlem=0.7,ghost_onlem=0.7,cyc_onlem=0.8,onlem=0.7)
R={}
print("deterministik")
for nm,kw in TAS.items():
    R[nm]={a:kos(pm(a,**kw))[0]/1e9 for a in ["Kötümser","Orta","İyimser"]}; print(nm,R[nm])
MC={}
rng=np.random.default_rng(20261012)
CEK=[]
for _ in range(3000):
    CEK.append(dict(f_phi=rng.uniform(0.5,2.5),pd=(1.0 if rng.random()>0.25 else rng.uniform(0,1)),dolasma=rng.uniform(0,0.2),pej=rng.uniform(0,0.05),
      eps_pp=rng.uniform(0,0.03),maliyet=rng.uniform(0.4,1.1),ghost=rng.uniform(0,0.02),uyum=rng.uniform(0.6,1.0),cyc=rng.uniform(0,0.3),c_e=rng.uniform(0.5,1.0),lk=rng.uniform(1,6)))
for nm,kw in TAS.items():
    for mit in [False,True]:
        if mit and nm.startswith("S"): continue
        for a in ["Kötümser","Orta"]:
            v=[]
            for c in CEK:
                base=sc(a)
                q=dict(kw); q.update(dolasma=c['dolasma'],pej=c['pej'],eps_pp=c['eps_pp'],kp_maliyet_pay=c['maliyet'],ghost=c['ghost'],uyum_bireysel=c['uyum'],cyc=c['cyc'],c_e=c['c_e'],levy_kacis=c['lk'],phi=min(0.08,base['phi']*c['f_phi']))
                if 'cap_e' not in q and 'r_y' not in q: q['prim_devam']=c['pd']
                if 'r_y' in q and 'cap_e' not in q: q['prim_devam']=c['pd']
                if mit: q.update(MIT)
                v.append(kos(pm(a,**q))[0]/1e9)
            v=np.array(v); k=nm+(" +önlemler" if mit else "")+" | "+a
            MC[k]=dict(p_negatif=float((v<0).mean()),p5=float(np.percentile(v,5)),medyan=float(np.median(v)),p95=float(np.percentile(v,95))); print(k,{x:round(y,3) for x,y in MC[k].items()})
# adalet
ad={}
po=pm("Orta")
gel=(1-po['gider'])*H
for nm,kw in TAS.items():
    p=pm("Orta",**kw); pe=prim_e(p,H); py=prim_y(p,H); v=tevkifat(H,po['gider'])
    ad[nm]=dict(H_W=[1,2,4,8,16,24],eski_yuk=[float(x) for x in (v+pe)/gel],yeni_yuk=[float(x) for x in (v+py)/gel])
    print(nm,"eski",np.round((v+pe)/gel,2),"yeni",np.round((v+py)/gel,2))
json.dump(dict(det=R,mc=MC,adalet=ad),open('sonuc_m.json','w'),ensure_ascii=False,indent=1)
