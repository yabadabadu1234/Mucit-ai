import numpy as np
from genc3 import *
ARALIK=dict(hedef_canli12=(0.5,0.85),kappa=(0.0,0.3),mal_pay=(0.2,0.6),c_mal=(0.40,0.65),c_hiz=(0.10,0.25),faiz=(0.0,0.03),sv=(0.2,0.6),
  aile_olcek=(0.5,1.3),erisim_kd=(0.4,0.9),kayip_kd=(0.08,0.20),talep_bolge=(0.6,1.1),gss_esik_katsayi=(0.5,2.0),drag=(0.0,0.2),duz_oran=(0.105,0.27))
def rank(x): return np.argsort(np.argsort(x)).astype(float)
def spearman(a,b):
    ra,rb=rank(a),rank(b); ra-=ra.mean(); rb-=rb.mean(); return float((ra*rb).sum()/np.sqrt((ra*ra).sum()*(rb*rb).sum()))
g=np.random.default_rng(7); M=80; rows=[]; X=[]
for i in range(M):
    par=dict(VARSAYILAN)
    x={k:g.uniform(*v) for k,v in ARALIK.items()}; par.update(x)
    b0,o=calistir(par,N=1500,seed=int(g.integers(1,10**6)))
    rows.append(o); X.append(x)
def dizi(ad,k): return np.array([r[ad][k] for r in rows])
print("== B) KÜRESEL DUYARLILIK: %d rastgele parametre çekilişi (aralıklar aşağıda); teklif − referans farkı =="%M)
for k,v in ARALIK.items(): print("   %-18s %s"%(k,v))
for ref in ["mevcut, kayıtlı","mevcut, kayıt dışı"]:
    print("-- referans:",ref)
    for k,yon in (("gecim72",1),("yarim72",1),("bir72",1),("acik_firma",1),("kalici",1),("dip",-1),("yikim",-1),("sabit_borc",-1),("net_son",1)):
        d=dizi("teklif",k)-dizi(ref,k)
        iyi=(d*yon>0).mean()
        print("   %-8s fark ort %+.3f  [min %+.3f, max %+.3f]  teklifin lehine olduğu çekiliş oranı %.2f"%(k,d.mean(),d.min(),d.max(),iyi))
print("-- 'teklif' kalıcı üst segment oranı: ort %.3f  min %.3f  max %.3f"%(dizi("teklif","kalici").mean(),dizi("teklif","kalici").min(),dizi("teklif","kalici").max()))
print("-- 'teklif' dip (kalıcı alt) oranı: ort %.3f  min %.3f  max %.3f"%(dizi("teklif","dip").mean(),dizi("teklif","dip").min(),dizi("teklif","dip").max()))
print("-- Spearman: hangi parametre 'teklif kalıcı üst segment' sonucunu en çok oynatıyor")
y=dizi("teklif","kalici")
s=sorted([(abs(spearman(np.array([x[k] for x in X]),y)),k,spearman(np.array([x[k] for x in X]),y)) for k in ARALIK],reverse=True)
for _,k,v in s: print("   %-18s %+.2f"%(k,v))
print("-- Spearman: teklif − mevcut(kayıtlı) kalıcı fark")
y=dizi("teklif","kalici")-dizi("mevcut, kayıtlı","kalici")
s=sorted([(abs(spearman(np.array([x[k] for x in X]),y)),k,spearman(np.array([x[k] for x in X]),y)) for k in ARALIK],reverse=True)
for _,k,v in s[:6]: print("   %-18s %+.2f"%(k,v))
print("\n== C) ORAN TARAMASI (varsayılan parametre, 8 tohum, N=2000): düz tevkifat oranı ==")
for r in (0.105,0.135,0.17,0.20,0.27):
    par=dict(VARSAYILAN); par["duz_oran"]=r; res=[calistir(par,N=2000,seed=20261101+100*sd)[1]["teklif"] for sd in range(8)]
    f=lambda k:(np.mean([x[k] for x in res]),1.96*np.std([x[k] for x in res])/np.sqrt(8))
    print("  oran %.3f  geçim72 %.3f±%.3f  yarım72 %.3f  bir72 %.3f  kalıcı %.3f  dip %.3f  yıkım %.3f  net_son %.2f"%((r,)+f("gecim72")+(f("yarim72")[0],f("bir72")[0],f("kalici")[0],f("dip")[0],f("yikim")[0],f("net_son")[0])))
