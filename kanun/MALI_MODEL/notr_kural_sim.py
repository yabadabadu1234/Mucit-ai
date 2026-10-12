import numpy as np
from genc_model import tarife, W, TAVAN
import model
T_MIKRO=0.135; G=0.30
ALICI_ORAN=(0.15,0.20,0.27,0.35,0.40,0.25)
UCRET=(0.0,0.01,0.03,0.05,0.10)
def kazanc_mevcut(r_b,c,mahsup):
    s_vergi=T_MIKRO
    geri=1.0-s_vergi-c
    b=-1.0+geri+(r_b if mahsup else 0.0)
    return b
def kazanc_notr(r_b,c,mahsup):
    s_vergi=r_b if mahsup else T_MIKRO
    geri=1.0-s_vergi-c
    return -1.0+geri+(r_b if mahsup else 0.0)
print("Strateji taraması: alıcı oranı r_b, ücret c, mahsup talebi {evet,hayır}; birim ödeme 1,0 sahte")
for ad,f in (("mevcut Madde 1(e) (alıcı mahsubu serbest, satıcı %13,5)",kazanc_mevcut),("NÖTR kural (satıcı oranı = mahsup talep edilirse alıcı oranı)",kazanc_notr)):
    en=-9;arg=None
    for r in ALICI_ORAN:
        for c in UCRET:
            for m in (True,False):
                g=f(r,c,m)
                if g>en: en=g;arg=(r,c,m)
    print("  %-62s azamî kazanç %+.3f (strateji r_b=%.2f c=%.2f mahsup=%s)"%(ad,en,arg[0],arg[1],arg[2]))
print("\nAlıcı mahsup talep eder ve ücret c=0 iken kazanç (nötr):",["%.3f"%kazanc_notr(r,0.0,True) for r in ALICI_ORAN])
print("\nSAHİCİ SATICI YÜKÜ: yıllık H için satıcının ödediği toplam (hasılata oranı); alıcı mahsup talep ederse (alıcı kurumlar %25)")
print("%-6s %12s %12s %14s %14s"%("H/W","eski rejim","teklif %13,5","nötr (hepsi mahsup)","nötr (%70 mahsup)"))
for k in (1,2,4,8,16,24):
    H=k*W
    eski=(float(tarife(np.array([0.5*H]))[0])+0.8*141699.0)/H
    notr_tum=0.25
    notr_70=0.7*0.25+0.3*T_MIKRO
    print("%-6d %12.3f %12.3f %14.3f %14.3f"%(k,eski,T_MIKRO,notr_tum,notr_70))
print("\nMali etki (yıl-4 net, mlr TL): sahte fatura kaybı sıfır, B2B payı kurumsal_pay=0,70 modelin varsayımı; katılım kaybı modellenmedi")
for ad in ("Kötümser","Orta","İyimser"):
    p=model.sc(ad); p0=dict(p); p0['duz_oran']=T_MIKRO
    a=model.yil(p0,p0['ramp'][3])['net']/1e9
    p1=dict(p); p1['duz_oran']=0.7*0.25+0.3*T_MIKRO; p1['phi']=0.0
    b=model.yil(p1,p1['ramp'][3])['net']/1e9
    print("  %-9s teklif düz %%13,5: %+.2f   nötr kural (etkin %.4f): %+.2f"%(ad,a,0.7*0.25+0.3*T_MIKRO,b))
