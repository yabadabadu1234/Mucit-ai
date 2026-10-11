import numpy as np, json
from genc_model import REJIM, ASGARI_NET, PRIM_AYLIK, SABIT_AYLIK
from genc2 import nufus, sok2, kos2, olc2, TIPLER, KAL
SMIN=ASGARI_NET/3
ACILIS={"dusuk":8000.0,"orta":12000.0,"yuksek":20000.0}
LTD_PESIN=50000.0/4
AS_PESIN=250000.0/4
RJ={"Mevcut kanun, kayıtlı":(REJIM["Mevcut kanun, kayıtlı"],"acilis"),
    "Mevcut kanun, kayıt dışı":(REJIM["Mevcut kanun, kayıt dışı"],0.0),
    "Teklif S":(REJIM["Teklif S"],0.0),
    "Model G2":(REJIM["Model G2 (tavanda uçurum yok)"],0.0)}
N=3000
P=nufus(N,20261020); S=sok2(N,72,20261021)
def ilk_gelir(R,esik=1.0):
    var=R>esik
    ilk=np.where(var.any(axis=0),var.argmax(axis=0)+1,99)
    return ilk
def olc_kurulus(r,P):
    R=r['R']; ilk=ilk_gelir(R)
    ay12_gel=(R[:12]>1.0).sum(axis=0)
    sag12=(~r['iflas']) 
    ac12=r['ac_ay']
    return dict(ilk_gelir_medyan=float(np.median(ilk)),ilk_6_ay_gelir=float((ilk<=6).mean()),ilk_12_ay_gelir=float((ilk<=12).mean()),
                gelirli_ay_12=float(ay12_gel.mean()),yikim=float(r['iflas'].mean()),ac_ay_72=float(ac12.mean()))
print("A. KURULUŞ KAPISI: gün-0 nakit ihtiyacı (TL) ve sıfır sermayeli gencin kurabilmesi")
print("   şahıs işletmesi, mevcut kanun: açılış %.0f-%.0f-%.0f + ilk ay 4/b primi %.0f + muhasebe %.0f"%(ACILIS['dusuk'],ACILIS['orta'],ACILIS['yuksek'],PRIM_AYLIK,SABIT_AYLIK))
for k,v in ACILIS.items(): print("     açılış %s: gün-0 nakit %.0f TL; ilk ay toplam %.0f TL"%(k,v,v+PRIM_AYLIK+SABIT_AYLIK))
print("   mikro mükellef (Teklif S, Madde 1/2/6): gün-0 nakit 0 TL (portal, UETS ücretsiz, hesap ücretsiz, muhasebeci/mali mühür/oda yok); 4/b primi yok")
print("   limited şirket: nakdi sermaye 50 000 TL, peşin 1/4 = %.0f TL + tescil masrafı ; anonim: 250 000 TL, peşin 1/4 = %.0f TL"%(LTD_PESIN,AS_PESIN))
print("   aile desteği yaşama eşiği (net asgari 1/3) = %.0f TL/ay (sim'de aylık geçim desteği, kuruluş fonu değil)"%SMIN)
print()
print("B. SİMÜLASYON (3000 genç, 72 ay). Kalibrasyon orta. Tip payları: "+", ".join("%s %.0f%%"%(t[0],100*t[1]/sum(x[1] for x in TIPLER)) for t in TIPLER))
KALIB=KAL
OUT={}
for kad,kw in KALIB.items():
    for soguk in (False,True):
        b_ilk=0.0 if soguk else 0.5
        print("== kalibrasyon %s ; %s"%(kad,"SOĞUK BAŞLANGIÇ (ilk müşteri yok)" if soguk else "ilk müşteri var"))
        for ad,(rj,k0) in RJ.items():
            kk=-ACILIS['orta'] if k0=="acilis" else 0.0
            r=kos2(rj,P,S,N,k0=kk,b_ilk=b_ilk,**kw)
            m=olc_kurulus(r,P); g=olc2(r)
            OUT["%s|%s|%s"%(kad,soguk,ad)]=dict(m=m,g=g)
            print("  %-26s ilk gelir medyan %5.1f ay | 6 ayda gelir %.2f | 12 ayda gelir %.2f | ilk yılda gelirli ay %.1f | yıkım %.2f | aç ay(72) %.1f | kalıcı üst %.3f"%(ad,m['ilk_gelir_medyan'],m['ilk_6_ay_gelir'],m['ilk_12_ay_gelir'],m['gelirli_ay_12'],m['yikim'],m['ac_ay_72'],g['kalici_ust']))
print()
print("C. TİPE GÖRE (orta, soğuk başlangıç): Teklif S")
kw=KALIB['orta']; r=kos2(RJ['Teklif S'][0],P,S,N,b_ilk=0.0,**kw)
for i,t in enumerate(TIPLER):
    idx=np.where(P['tip']==i)[0]; ilk=ilk_gelir(r['R'][:,idx])
    print("  %-22s n=%4d | 6 ayda gelir %.2f | 12 ayda gelir %.2f | yıkım %.2f | kalıcı üst %.3f"%(t[0],len(idx),(ilk<=6).mean(),(ilk<=12).mean(),r['iflas'][idx].mean(),olc2(r,idx)['kalici_ust']))
print()
print("D. CİHAZ ENGELİ (duyarlılık; ölçülmedi): cihazı olmayan oranı d ise kuramayan oranı en az d; Teklif S için 'kurabilen' = 1-d")
for d in (0.0,0.1,0.2,0.3,0.4): print("   d=%.1f -> kurabilen %.2f"%(d,1-d))
json.dump(OUT,open("sonuc_sifir_sermaye.json","w"),ensure_ascii=False,indent=1)
print()
print("E. TAVAN (24 brüt asgari ücret = %.0f TL) AŞAN GENÇ ORANI (muhasebeci için yeni müşteri havuzu), Teklif S, soğuk başlangıç"%(24*33030.0))
for kad,kw in KALIB.items():
    r=kos2(RJ['Teklif S'][0],P,S,N,b_ilk=0.0,**kw); R=r['R']
    yillik=np.stack([R[12*i:12*i+12].sum(axis=0) for i in range(6)])
    ever=(yillik.max(axis=0)>24*33030.0)
    yak=(yillik.max(axis=0)>0.7*24*33030.0)
    print("  %-5s ömründe bir yıl tavanı aşan %.3f | tavanın %%70'ine ulaşan %.3f"%(kad,ever.mean(),yak.mean()))
