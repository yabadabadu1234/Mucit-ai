import numpy as np, json
from genc_model import REJIM
from genc2 import nufus, sok2, kos2, olc2, KAL
N=3000
P=nufus(N,20261030); S=sok2(N,72,20261031)
MEV=REJIM["Mevcut kanun, kayıtlı"]; TS=REJIM["Teklif S"]
SENARYO=[
 ("Bugün esnaf/şahıs (açılış 12000, sabit yük)",MEV,-12000.0,0.0),
 ("Bugün LTD (12500 peşin sermaye + 5400 oda/tescil; sabit yük)",MEV,-17900.0,0.0),
 ("Bugün kollektif (noter/sicil 3000 VARSAYIM; sabit yük)",MEV,-3000.0,0.0),
 ("Bugün ticaret, stoklu (stok 20000 VARSAYIM + esnaf 12000)",MEV,-32000.0,0.0),
 ("Çare: tek kapı, hizmet/emek (gün-0 0)",TS,0.0,0.0),
 ("Çare: tek kapı + sermayesiz tüzel (gün-0 0)",TS,0.0,0.0),
 ("Çare: tek kapı + emanet/siparişle ticaret (gün-0 0)",TS,0.0,0.0),
]
OUT={}
for kad,kw in KAL.items():
    print("== kalibrasyon",kad,"(soğuk başlangıç: ilk müşteri yok)")
    for ad,rj,k0,_ in SENARYO:
        r=kos2(rj,P,S,N,k0=k0,b_ilk=0.0,**kw); R=r['R']
        var=R>1.0; ilk=np.where(var.any(axis=0),var.argmax(axis=0)+1,99)
        g=olc2(r)
        OUT["%s|%s"%(kad,ad)]=dict(ilk6=float((ilk<=6).mean()),ilk12=float((ilk<=12).mean()),yikim=float(r['iflas'].mean()),ac=float(r['ac_ay'].mean()),kalici=g['kalici_ust'],dip=g['dip'],devlet_pv=g['devlet_pv'])
        o=OUT["%s|%s"%(kad,ad)]
        print("  %-62s 6ay gelir %.2f | 12ay %.2f | yıkım %.2f | aç ay %.1f | kalıcı üst %.3f | dip %.3f | devletPV %8.0f"%(ad,o['ilk6'],o['ilk12'],o['yikim'],o['ac'],o['kalici'],o['dip'],o['devlet_pv']))
json.dump(OUT,open("sonuc_bariyer.json","w"),ensure_ascii=False,indent=1)
