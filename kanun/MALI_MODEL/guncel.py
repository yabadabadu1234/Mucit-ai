import json, numpy as np
import model
from model import *
KALEM=['brut_tevkifat','bes_ve_devlet_katkisi','myo_primi','kdv_mahsubu','yutulma_vergi','yutulma_prim','sahte_fatura_kaybi','kgf_maliyeti','ptt','bt','itiraz','denetim']
def y4(p):
    return yil(p,1.0,ilk=False)
def ayrisim(ad,**kw):
    p=sc(ad); p.update(kw); y=y4(p); return {k:y[k]/1e9 for k in KALEM+['net']}
OUT={}
print("A. YIL-4 KALEM AYRISIMI (mlr TL; + gelir, - gider)")
TAS=[("S: prim surer",dict()),("prim kalkar (prim_devam=0)",dict(prim_devam=0.0)),("duz %23 tek odeme, prim kalkar, hibe yok",dict(duz_oran=0.23,myo_oran=0.0,prim_devam=0.0))]
for ad in ["Kötümser","Orta","İyimser"]:
    for nm,kw in TAS:
        a=ayrisim(ad,**kw); OUT[ad+"|"+nm]=a
        print(ad,nm,"brut %.2f | BES %.2f hibe %.2f KDV %.2f yut.vergi %.2f yut.prim %.2f sahte %.2f KGF %.2f diger %.2f | NET %.2f"%(a['brut_tevkifat'],a['bes_ve_devlet_katkisi'],a['myo_primi'],a['kdv_mahsubu'],a['yutulma_vergi'],a['yutulma_prim'],a['sahte_fatura_kaybi'],a['kgf_maliyeti'],a['ptt']+a['bt']+a['itiraz']+a['denetim'],a['net']))
print()
print("B. TEK ODEME ORANI r (ciro uzerinden; vergi+SGK birlikte), prim kalkar, hibe ve KDV mahsubu yok; Orta, yil-4 net mlr TL")
SW={}
for s in (0.05,0.15,0.30,1.0):
    row=[]
    for r in (0.05,0.10,0.15,0.20,0.23,0.28,0.35,0.45,0.60):
        p=sc("Orta"); p.update(duz_oran=r,myo_oran=0.0,kdv_donanim_pay=0.0,prim_devam=0.0,s_kayitli=s,u_ucretli=min(0.2,1-s))
        row.append(y4(p)['net']/1e9)
    SW[s]=row; print("s=%.2f"%s," ".join("%7.2f"%x for x in row))
print("   r:   5%    10%    15%    20%    23%    28%    35%    45%    60%")
def rstar(s,ad="Orta",**kw):
    lo,hi=0.0,1.0
    for _ in range(60):
        m=(lo+hi)/2
        p=sc(ad); p.update(duz_oran=m,myo_oran=0.0,kdv_donanim_pay=0.0,prim_devam=0.0,s_kayitli=s,u_ucretli=min(0.2,1-s)); p.update(kw)
        if y4(p)['net']>=0: hi=m
        else: lo=m
    return hi
RS={}
for ad in ["Kötümser","Orta","İyimser"]:
    RS[ad]={s:rstar(s,ad) for s in (0.05,0.15,0.30,0.60,1.0)}
    print("r* (net=0) ",ad,{s:round(v,3) for s,v in RS[ad].items()})
print()
print("C. MEVCUT STOK STRESI: kayitli kendi hesabina (2123 bin) hepsi rejime gecse")
ST={}
for med in (5.0,12.0,17.0):
    for nm,kw in [("prim surer",dict()),("prim kalkar",dict(prim_devam=0.0)),("duz %23, prim kalkar",dict(duz_oran=0.23,myo_oran=0.0,prim_devam=0.0))]:
        p=sc("Orta"); p.update(n_toplam=2123000,s_kayitli=1.0,u_ucretli=0.0,medyan_W=med); p.update(kw)
        a=y4(p); ST[(med,nm)]=a['net']/1e9
        print("medyan %.0fW %-22s net %.2f mlr (yut.vergi %.2f yut.prim %.2f brut %.2f)"%(med,nm,a['net']/1e9,a['yutulma_vergi']/1e9,a['yutulma_prim']/1e9,a['brut_tevkifat']/1e9))
print()
print("D. EN KUCUK SIZINTI s* (net=0) Orta, prim kalkar; baz tasarim ve alternatifler")
def sstar(**kw):
    lo,hi=0.0,1.0
    p=sc("Orta"); p.update(kw); p['s_kayitli']=1.0; p['u_ucretli']=0.0
    if y4(p)['net']>=0: return None
    for _ in range(60):
        m=(lo+hi)/2; p=sc("Orta"); p.update(kw); p['s_kayitli']=m; p['u_ucretli']=min(0.2,1-m)
        if y4(p)['net']>=0: lo=m
        else: hi=m
    return lo
for nm,kw in [("S prim surer",dict()),("prim kalkar",dict(prim_devam=0.0)),("prim kalkar, hibe yok",dict(prim_devam=0.0,myo_oran=0.0)),("duz %15 tek odeme",dict(duz_oran=0.15,myo_oran=0.0,prim_devam=0.0)),("duz %23 tek odeme",dict(duz_oran=0.23,myo_oran=0.0,prim_devam=0.0)),("duz %35 tek odeme",dict(duz_oran=0.35,myo_oran=0.0,prim_devam=0.0))]:
    print(nm,sstar(**kw))
print()
H=np.array([1,2,4,8,16,24])*W; p=sc("Orta")
print("E. ESKI YUK / YENI YUK (ayni hasilat)")
for h in H:
    yeni=float(tevkifat(h,p['gider'])); eski=float(tarife(p['marj']*h))+p['prim_odeme']*p['prim_eski']
    print("H=%.0fW eski %.0f yeni %.0f oran %.1f ; eski/ciro %.2f"%(h/W,eski,yeni,eski/yeni,eski/h))
json.dump(dict(ayrisim=OUT,sweep={str(k):v for k,v in SW.items()},rstar={a:{str(s):v for s,v in d.items()} for a,d in RS.items()},stok={"%s|%s"%k:v for k,v in ST.items()}),open('sonuc_guncel.json','w'),ensure_ascii=False,indent=1)
