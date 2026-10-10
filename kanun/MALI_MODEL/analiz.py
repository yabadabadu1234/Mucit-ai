import numpy as np, json, copy
from model import *
rng=np.random.default_rng(20261010)
def kos(p): 
    v,ys=npv(p); return ys[3],v,ys
SONUC={}
# 1 senaryolar
SONUC['senaryo']={}
for ad in SENARYO:
    p=sc(ad); s4,v,ys=kos(p); SONUC['senaryo'][ad]=dict(yil4=s4,npv5=v,yillar=[y['net'] for y in ys],param={k:p[k] for k in ['medyan_W','n_toplam','s_kayitli','u_ucretli','phi','onlem','myo_uygun','bes_vazgecme','kgf_alim','kgf_temerrut','kdv_donanim_pay']})
# 2 kırılma noktası (Orta): net=0 için s*
def net_s(s,base=None):
    p=sc('Orta') if base is None else dict(base); p['s_kayitli']=s; return kos(p)[0]['net']
lo,hi=0.0,0.6
for _ in range(60):
    m=(lo+hi)/2
    if net_s(m)>0: lo=m
    else: hi=m
SONUC['s_kirilma']=lo
# 3 politika varyantları (Orta tabanında)
V={}
def var(ad,**kw):
    p=sc('Orta'); p.update(kw); V[ad]=kos(p)[0]['net']
var('G0 Güncel teklif: 24 ay giriş kapısı var (Orta, s=0,05)')
var('G1 Önceki taslak: kapı yok (s=0,25)',s_kayitli=0.25)
var('G2 Kapı sızıntısı yüksek (s=0,10)',s_kayitli=0.10)
var('G3 Kapı sızıntısı çok yüksek (s=0,20)',s_kayitli=0.20)
var('G4 Kapı + götürü gider %25',gider=0.25)
var('G5 Kapı + (e) bendi yok: düz %10,5',duz_oran=0.105)
var('G6 Kapı + 90 gün prim hibesi yok',myo_uygun=0.0)
var('G7 Kapı + donanım KDV mahsubu yok',kdv_donanim_pay=0.0)
var('G8 Kapı yok + geçenler primi yarı oranda sürdürür (s=0,25)',s_kayitli=0.25,prim_devam=0.5)
SONUC['varyant']=V
# 4 tornado (Orta, yıl4)
base=sc('Orta'); b0=kos(base)[0]['net']
ARALIK={'n_toplam':(150000,700000),'s_kayitli':(0.0,0.20),'u_ucretli':(0.10,0.30),'medyan_W':(3.0,8.0),'prim_odeme':(0.4,1.0),'phi':(0.0,0.03),'onlem':(0.2,0.8),
 'myo_uygun':(0.1,0.6),'bes_vazgecme':(0.1,0.6),'kdv_donanim_pay':(0.2,0.6),'kgf_alim':(0.02,0.10),'kgf_temerrut':(0.05,0.20),'uyum_ucretli':(0.2,0.8),'marj':(0.35,0.65),'r_marj_ucretli':(0.2,0.35),'sigma':(0.6,1.2)}
T=[]
for k,(a,b) in ARALIK.items():
    pa=dict(base);pa[k]=a;pb=dict(base);pb[k]=b
    T.append((k,a,b,kos(pa)[0]['net']-b0,kos(pb)[0]['net']-b0))
T.sort(key=lambda x:-max(abs(x[3]),abs(x[4])))
SONUC['tornado']=T; SONUC['b0']=b0
# 5 Monte Carlo
def tri(a,m,b): return rng.triangular(a,m,b)
NS=4000; net=[];npvs=[];prm=[]
for i in range(NS):
    p=dict(BAZ)
    p['n_toplam']=float(np.exp(rng.normal(np.log(350000),0.55)))
    p['s_kayitli']=float(rng.beta(2,38)); p['u_ucretli']=float(rng.beta(3,12))
    p['medyan_W']=tri(3,5,8); p['sigma']=tri(0.6,0.9,1.2)
    p['prim_odeme']=tri(0.4,0.7,1.0); p['phi']=tri(0,0.01,0.03); p['onlem']=tri(0.2,0.5,0.8)
    p['myo_uygun']=tri(0.1,0.35,0.6); p['bes_vazgecme']=tri(0.1,0.35,0.6); p['kdv_donanim_pay']=tri(0.2,0.4,0.6)
    p['kgf_alim']=tri(0.02,0.05,0.10); p['kgf_temerrut']=tri(0.05,0.10,0.20); p['uyum_ucretli']=tri(0.2,0.5,0.8)
    p['marj']=tri(0.35,0.5,0.65); p['r_marj_ucretli']=tri(0.2,0.27,0.35)
    s4,v,ys=kos(p); net.append(s4['net']); npvs.append(v); prm.append(p['s_kayitli'])
net=np.array(net);npvs=np.array(npvs)
q=lambda a:{k:float(np.percentile(a,k)) for k in (5,10,25,50,75,90,95)}
SONUC['mc']=dict(n=NS,net_q=q(net),npv_q=q(npvs),p_net_pozitif=float((net>0).mean()),p_npv_pozitif=float((npvs>0).mean()),net=net.tolist())
json.dump(SONUC,open('sonuc.json','w'),ensure_ascii=False,default=float)
print("kırılma s*=%.3f"%SONUC['s_kirilma'])
for k,v in V.items(): print("%-55s %.2f mlr"%(k,v/1e9))
print("Orta yıl4 net %.2f"%(b0/1e9))
for t in T[:8]: print(t[0],"%.2f %.2f"%(t[3]/1e9,t[4]/1e9))
print("MC net P5/P50/P95: %.2f %.2f %.2f ; P(net>0)=%.2f ; NPV P50 %.2f"%(SONUC['mc']['net_q'][5]/1e9,SONUC['mc']['net_q'][50]/1e9,SONUC['mc']['net_q'][95]/1e9,SONUC['mc']['p_net_pozitif'],SONUC['mc']['npv_q'][50]/1e9))
