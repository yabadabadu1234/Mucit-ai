import numpy as np, json
from genc_model import REJIM
from genc2 import nufus, sok2, kos2, olc2, KAL
N=3000
P=nufus(N,20261040); S=sok2(N,72,20261041)
TS=REJIM["Teklif S"]; MEV=REJIM["Mevcut kanun, kayıtlı"]
SEN=[("Çare, hizmet, sermayesiz (k0 0)",TS,0.0,0.0,None),
     ("Çare, stoklu ticaret, borçla stok (k0 -20000)",TS,-20000.0,0.0,None)]
for sm in (10000.0,20000.0):
    for p in (0.3,0.5):
        for kat in (None,1.3,1.5):
            SEN.append(("Çare + mudârebe/azalan: sermaye %d, pay %.1f, tavan %s"%(sm,p,"yok" if kat is None else "%.1f×sermaye"%kat),TS,sm,p,kat))
OUT={}
for kad,kw in KAL.items():
    print("== kalibrasyon",kad,"(soğuk başlangıç)")
    for ad,rj,k0,p,kat in SEN:
        r=kos2(rj,P,S,N,k0=k0,b_ilk=0.0,kar_payi=p,pay_tavan=(None if kat is None else kat*k0),**kw); g=olc2(r); R=r['R']
        var=R>1.0; ilk=np.where(var.any(axis=0),var.argmax(axis=0)+1,99)
        o=dict(ilk12=float((ilk<=12).mean()),yikim=float(r['iflas'].mean()),kalici=g['kalici_ust'],dip=g['dip'],devlet_pv=g['devlet_pv'])
        if p>0:
            kayip=r['iflas'].mean()*k0
            o['sermayedar_getiri_72ay']=float((r['pay_toplam'].mean()-kayip)/k0)
        OUT["%s|%s"%(kad,ad)]=o
        print("  %-76s 12ay gelir %.2f | yıkım %.2f | kalıcı üst %.3f | dip %.3f | devletPV %7.0f%s"%(ad,o['ilk12'],o['yikim'],o['kalici'],o['dip'],o['devlet_pv'],(" | sermayedar 72 ay net getiri %+.2f×"%o['sermayedar_getiri_72ay']) if p>0 else ""))
json.dump(OUT,open("sonuc_ortaklik.json","w"),ensure_ascii=False,indent=1)
