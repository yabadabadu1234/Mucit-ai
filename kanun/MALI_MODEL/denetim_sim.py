import numpy as np
from genc2 import nufus,sok2,kos2,olc2,KAL
from genc_model import REJIM
N=3000; P=nufus(N,20261015); S=sok2(N,72,20261016)
T_MIK=0.105; R_B=0.25
SATIR=[("Tarafsız ölçü (kanunsuz)","Tarafsız ölçü (kanunsuz)",None),
 ("Mevcut kanun, kayıtlı","Mevcut kanun, kayıtlı",None),
 ("Mevcut kanun, kayıt dışı","Mevcut kanun, kayıt dışı",None),
 ("Teklif (eski: kademeli tevkifat)","Teklif S",None),
 ("Teklif düz %10,5 (Madde P)","Teklif S",T_MIK)]
for pb in (0.35,0.70):
    SATIR.append(("A kuralı: doğrulanmamış B2B payı %d%%"%round(pb*100),"Teklif S",pb*R_B+(1-pb)*T_MIK))
for kad,kw in KAL.items():
    print("== kalibrasyon",kad)
    for ad,rk,duz in SATIR:
        r=kos2(REJIM[rk],P,S,N,duz_oran=duz,**kw); o=olc2(r)
        print("  %-42s kalıcı üst %.3f | yıkım %.3f | dip %.3f | aç-ay %5.1f | devlet PV %8.0f"%(ad,o['kalici_ust'],o['yikim'],o['dip'],o['ac_ay'],o['devlet_pv']))
