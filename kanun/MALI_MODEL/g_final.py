import json, numpy as np
from model_m import *
H=np.array([1,2,4,8,16,24])*W; B=np.array(ORANLAR)
G=dict(oranlar=[0.15,0.24,0.27,0.35,0.40],eski_ayni=True,r_y=0.10,e0=2,prog=2.0,kulucka=0,levy=0.02,tel=0.5)
G2=dict(G,oranlar=[0.15,0.24,0.35,0.455,0.52])
TAS={"S (mevcut teklif)":{},"G (maksada uygun: sabit yük yok, eski=yeni gelir primi %10 (>10W gelirde %20), alt eşik 2W, alıcı katkısı %2, orta dilim ×1,2)":G,
 "G2 (G + 400 bin TL üstü dilimler ×1,3)":G2}
MIT=dict(pej_onlem=0.7,ghost_onlem=0.7,cyc_onlem=0.8,onlem=0.7)
R={nm:{a:kos(pm(a,**kw))[0]/1e9 for a in ["Kötümser","Orta","İyimser"]} for nm,kw in TAS.items()}
for k,v in R.items(): print(k[:20],{a:round(x,2) for a,x in v.items()})
rng=np.random.default_rng(20261013); CEK=[dict(f_phi=rng.uniform(0.5,2.5),pd=(1.0 if rng.random()>0.25 else rng.uniform(0,1)),dolasma=rng.uniform(0,0.2),pej=rng.uniform(0,0.05),eps_pp=rng.uniform(0,0.03),mal=rng.uniform(0.4,1.1),ghost=rng.uniform(0,0.02),uy=rng.uniform(0.6,1.0),cyc=rng.uniform(0,0.3),ce=rng.uniform(0.5,1.0),lk=rng.uniform(1,6),tel=rng.uniform(0.25,1.5)) for _ in range(1500)]
MC={}
for nm,kw in TAS.items():
    for mit in ([False] if nm.startswith("S") else [False,True]):
        for a in ["Kötümser","Orta"]:
            v=[]
            for c in CEK:
                q=dict(kw); base=sc(a)
                q.update(dolasma=c['dolasma'],pej=c['pej'],eps_pp=c['eps_pp'],kp_maliyet_pay=c['mal'],ghost=c['ghost'],uyum_bireysel=c['uy'],cyc=c['cyc'],c_e=c['ce'],levy_kacis=c['lk'],phi=min(0.08,base['phi']*c['f_phi']))
                if nm.startswith("S"): q['prim_devam']=c['pd']
                else: q['tel']=c['tel']
                if mit: q.update(MIT)
                v.append(kos(pm(a,**q))[0]/1e9)
            v=np.array(v); k=nm.split(' (')[0]+(" +önlem" if mit else "")+" | "+a
            MC[k]=dict(p_negatif=float((v<0).mean()),p5=float(np.percentile(v,5)),medyan=float(np.median(v)),p95=float(np.percentile(v,95))); print(k,{x:round(y,3) for x,y in MC[k].items()})
for nm,kw in TAS.items():
    p=pm("Orta",**kw); print(nm[:3],"eski prim/gelir",np.round(prim_e(p,H)/((1-.3)*H),3),"yeni",np.round(prim_y(p,H)/((1-.3)*H),3))
json.dump(dict(det=R,mc=MC),open('sonuc_g.json','w'),ensure_ascii=False,indent=1)
