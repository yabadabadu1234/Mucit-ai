import numpy as np, json, model
from model import *
from model_k import prim_k
_orj=model.kisi_basi
def _yama(H,p):
    k=_orj(H,p); d=p.get('dolasma',0.0)
    if d>0:
        yarim=_orj(H/2,p); m=(H>=0.5*TAVAN)
        for x in ['T','bes','dk','myo','kdv']: k[x]=np.where(m,(1-d)*k[x]+d*2*yarim[x],k[x])
        k['yeni_net']=k['T']-k['bes']-k['dk']-k['myo']-k['kdv']
    return k
model.kisi_basi=_yama
BAZR=dict(kp_taban=0.0,kp_tavan=1e12,kulucka=3,kp_oran=0.0,kp_maliyet_pay=0.6,eps_pp=0.0,dolasma=0.0,pej=0.0,pej_onlem=0.0,pej_sgk=0.30,pej_vergi=0.15)
def p_kur(ad,**kw):
    p=sc(ad); p.update(BAZR); p.update(kw); return p
def kos(p):
    H,w=agirliklar(p); ys=[]; top=0.0
    for i in range(5):
        f=1.0
        if i>=p['kulucka'] and p['kp_oran']>0: f=1-p['eps_pp']*100*p['kp_oran']
        r=p['ramp'][i]*f; y=yil(p,r,ilk=(i==0)); n=y['net']; N=p['n_toplam']*r
        if i>=p['kulucka'] and p['kp_oran']>0:
            nyeni=1-p['s_kayitli']-p['u_ucretli']
            g=N*nyeni*float((w*prim_k(p,H)).sum()); n+=g*(1-p['kp_maliyet_pay'])
        if p['pej']>0:
            k=model.kisi_basi(H,p); kisi=p['pej']*(1-p['pej_onlem'])*N
            kazanc=float((w*k['yeni_net']).sum()); kayip=(p['pej_sgk']+p['pej_vergi'])*float((w*(1-p['gider'])*H).sum())
            n+=kisi*(kazanc-kayip)
        ys.append(n); top+=n/(1+p['iskonto'])**(i+1)
    return ys[3],top
def ikili(ad,**kw):
    return kos(p_kur(ad,**kw))[0]/1e9, kos(p_kur(ad,kp_oran=0.05,**kw))[0]/1e9
R={}
RISKLER=[("R0 Risksiz taban",{}),
 ("R1 Prim sürekliliği %50 tutar",dict(prim_devam=0.5)),
 ("R2 Prim sürekliliği hiç tutmaz",dict(prim_devam=0.0)),
 ("R3 Dolaşma %10 (yüksek gelirli, 2'ye bölünür)",dict(dolasma=0.10)),
 ("R4 Dolaşma %30",dict(dolasma=0.30)),
 ("R5 Sahte bağımsızlık %3 (tek müşteri testi yok)",dict(pej=0.03)),
 ("R6 Sahte bağımsızlık %3 (test, %70 önler)",dict(pej=0.03,pej_onlem=0.7)),
 ("R7 Kayıtlı payı s=%30",dict(s_kayitli=0.30)),
 ("R8 Geri akış %100 (K'de prim kazancı yok)",dict(kp_maliyet_pay=1.0)),
 ("R9 Geri akış %150",dict(kp_maliyet_pay=1.5)),
 ("R10 K katılım kaybı: her prim puanı %1 (4. yıl %5 -> %5 kayıp)",dict(eps_pp=0.01)),
 ("R11 K katılım kaybı: her puan %3 (%15 kayıp)",dict(eps_pp=0.03)),
 ("R12 Bileşik: prim %50 + dolaşma %10 + sahte %3 + geri akış %100 + kayıp %1/puan",dict(prim_devam=0.5,dolasma=0.10,pej=0.03,kp_maliyet_pay=1.0,eps_pp=0.01)),
 ("R13 Bileşik + testler (sahte %70 önlenir)",dict(prim_devam=0.5,dolasma=0.10,pej=0.03,pej_onlem=0.7,kp_maliyet_pay=1.0,eps_pp=0.01))]
for ad in ["Kötümser","Orta","İyimser"]:
    R[ad]={}
    for nm,kw in RISKLER:
        s,k=ikili(ad,**kw); R[ad][nm]=dict(S=s,K1=k); print(ad,nm,"S %.2f  K1 %.2f"%(s,k))
rng=np.random.default_rng(20261011); MC={}
for ad in ["Kötümser","Orta"]:
    for nm,kp in [("S",0.0),("K1",0.05)]:
        v=[]
        for _ in range(4000):
            kw=dict(kp_oran=kp,prim_devam=(1.0 if rng.random()>0.25 else rng.uniform(0,1)),dolasma=rng.uniform(0,0.2),pej=rng.uniform(0,0.05),
                    pej_onlem=rng.choice([0.0,0.7]),eps_pp=rng.uniform(0,0.03),kp_maliyet_pay=rng.uniform(0.4,1.1))
            v.append(kos(p_kur(ad,**kw))[0]/1e9)
        v=np.array(v); MC[ad+" "+nm]=dict(p_negatif=float((v<0).mean()),p5=float(np.percentile(v,5)),medyan=float(np.median(v)),p95=float(np.percentile(v,95)))
        print(ad,nm,MC[ad+" "+nm])
H=np.array([1,2,4,8,16,24])*W; p=sc("Orta")
yuk=[]
for h in H:
    yeni=float(tevkifat(h,p['gider'])); eski=float(tarife(p['marj']*h))+p['prim_odeme']*p['prim_eski']
    yuk.append(dict(H_W=float(h/W),yeni=yeni,eski=eski,oran=eski/yeni))
print(yuk)
json.dump(dict(risk=R,mc=MC,adalet=yuk),open('sonuc_risk.json','w'),ensure_ascii=False,indent=1)
