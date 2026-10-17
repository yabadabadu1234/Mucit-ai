import numpy as np, json, copy
from model import *
rng=np.random.default_rng(20261010)
def kos(p): 
    v,ys=npv(p); return ys[3],v,ys
SONUC={}
# 1 senaryolar
SONUC['senaryo']={}
for ad in SENARYO:
    p=sc(ad); s4,v,ys=kos(p); SONUC['senaryo'][ad]=dict(yil4=s4,npv5=v,yillar=[y['net'] for y in ys],param={k:p[k] for k in ['ort_H_W','sigma','n_toplam','s_kayitli','u_ucretli','phi','onlem','myo_uygun','bes_vazgecme','kgf_alim','kgf_temerrut','kdv_donanim_pay']})
# 2 kırılma noktası (Orta): net=0 için s*
def net_s(s,base=None):
    p=sc('Orta') if base is None else dict(base); p['s_kayitli']=s; return kos(p)[0]['net']
def net_s1(s):
    p=sc('Orta'); p['s_kayitli']=s; p['u_ucretli']=min(p['u_ucretli'],1-s); return kos(p)[0]['net']
lo,hi=0.0,1.0
if net_s1(1.0)>0: lo=None
else:
    for _ in range(60):
        m=(lo+hi)/2
        if net_s1(m)>0: lo=m
        else: hi=m
SONUC['s_kirilma']=lo
# 3 politika varyantları (Orta tabanında; baz: oran %13,5, gelire bağlı prim, maaşlı isterse girer)
V={}
def var(ad,**kw):
    p=sc('Orta'); p.update(kw); V[ad]=kos(p)[0]['net']
var('V0 Baz: %13,5; gelire bağlı prim, tam prim 6 asgari ücrette')
var('V1 Gelire bağlı prim hiç alınmasaydı (prim sıfır)',prim_toplama=0.0)
var('V2 Tam prim eşiği 3 asgari ücret',prim_k=3.0)
var('V3 Tam prim eşiği 12 asgari ücret',prim_k=12.0)
var('V4 Oran %20',duz_oran=0.20)
var('V6 Oran %27 (üst sınır)',duz_oran=0.27)
var('V7 Maaşlı hiç mikro mükellef olmasaydı (u=0)',u_ucretli=0.0)
var('V8 SGK tahsil oranı %50',prim_odeme=0.5)
var('V9 Gelire bağlı primin tahsil oranı %80',prim_toplama=0.8)
var('V10 Halen kayıtlıların hepsi geçse (s=%100)',s_kayitli=1.0)
var('V11 90 gün prim hibesi olmasaydı',myo_uygun=0.0)
var('V12 Donanım KDV mahsubu olmasaydı',kdv_donanim_pay=0.0)
SONUC['varyant']=V
# 4 tornado (Orta, yıl4)
base=sc('Orta'); b0=kos(base)[0]['net']
ARALIK={'n_toplam':(119000,475000),'s_kayitli':(0.0,0.20),'prim_k':(3.0,12.0),'prim_toplama':(0.5,1.0),'u_ucretli':(0.0,0.4),'duz_oran':(0.105,0.27),'ort_H_W':(30.0,85.0),'prim_odeme':(0.4,1.0),'phi':(0.0,0.03),'onlem':(0.2,0.8),
 'myo_uygun':(0.1,0.6),'bes_vazgecme':(0.1,0.6),'kdv_donanim_pay':(0.2,0.6),'kgf_alim':(0.02,0.10),'kgf_temerrut':(0.05,0.20),'marj':(0.35,0.65),'sigma':(1.25,2.0)}
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
    p['n_toplam']=float(np.exp(rng.normal(np.log(238000),0.55)))
    p['s_kayitli']=float(rng.beta(2,6)); p['prim_toplama']=tri(0.6,0.9,1.0); p['u_ucretli']=tri(0.05,0.2,0.35)
    p['ort_H_W']=tri(30,43,85); p['sigma']=tri(1.25,1.75,2.0)
    p['prim_odeme']=tri(0.4,0.7,1.0); p['phi']=tri(0,0.01,0.03); p['onlem']=tri(0.2,0.5,0.8)
    p['myo_uygun']=tri(0.1,0.35,0.6); p['bes_vazgecme']=tri(0.1,0.35,0.6); p['kdv_donanim_pay']=tri(0.2,0.4,0.6)
    p['kgf_alim']=tri(0.02,0.05,0.10); p['kgf_temerrut']=tri(0.05,0.10,0.20); 
    p['marj']=tri(0.35,0.5,0.65)
    s4,v,ys=kos(p); net.append(s4['net']); npvs.append(v); prm.append(p['s_kayitli'])
net=np.array(net);npvs=np.array(npvs)
q=lambda a:{k:float(np.percentile(a,k)) for k in (5,10,25,50,75,90,95)}
SONUC['mc']=dict(n=NS,net_q=q(net),npv_q=q(npvs),p_net_pozitif=float((net>0).mean()),p_npv_pozitif=float((npvs>0).mean()),net=net.tolist())
json.dump(SONUC,open('sonuc.json','w'),ensure_ascii=False,default=float)
print("kırılma s*=",SONUC['s_kirilma'])
for k,v in V.items(): print("%-55s %.2f mlr"%(k,v/1e9))
print("Orta yıl4 net %.2f"%(b0/1e9))
for t in T: print(t[0],"%.2f %.2f"%(t[3]/1e9,t[4]/1e9))
print("MC net P5/P50/P95: %.2f %.2f %.2f ; P(net>0)=%.2f ; NPV P50 %.2f"%(SONUC['mc']['net_q'][5]/1e9,SONUC['mc']['net_q'][50]/1e9,SONUC['mc']['net_q'][95]/1e9,SONUC['mc']['p_net_pozitif'],SONUC['mc']['npv_q'][50]/1e9))
