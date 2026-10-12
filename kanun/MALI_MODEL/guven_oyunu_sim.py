import math
from genc_model import TAVAN
D=0.25; TEV=0.135; UCRET=0.03; ODUL=0.10
KAZ_B=D-UCRET-TEV+TEV
B_KAZ=-1.0+(1.0-TEV-UCRET)+D
B_ZARAR=-1.0+D
ESIK_P=-B_ZARAR/(B_KAZ-B_ZARAR)
def cdf(x,med,sig):
    if x<=0: return 0.0
    return 0.5*(1+math.erf((math.log(x)-math.log(med))/(sig*math.sqrt(2))))
TIPLER=(("yabancı (piyasadan bulunan kimlik)",0.50,0.05),("tanıdık/arkadaş",0.25,0.30),("aile (ikinci derece içi)",0.20,1.00),("örgüt (tekrarlı, şiddet/itibar)",0.05,3.00))
SIG=0.8
def aktif(med,rehin,odul):
    esik=(1.0-TEV)-UCRET+odul-rehin
    return 1.0-cdf(esik,med,SIG)
print("Oyun: B sahte faturayı öder (1,0); S işbirliği ederse B'ye %.3f geri verir. B kazancı %+.3f, S ihanet ederse B %+.3f"%(1-TEV-UCRET,B_KAZ,B_ZARAR))
print("B'nin girmesi için S'nin işbirliğine güveni en az %.3f olmalı"%ESIK_P)
print("S'nin işbirliği şartı: yaptırım gücü + rehin >= %.3f - ücret %.3f + ödül(%.3f)\n"%(1-TEV,UCRET,ODUL))
print("%-40s %7s %9s %9s %9s"%("ilişki tipi","pay","bugün","tedbir","kapanma"))
top0=top1=0.0
for ad,pay,med in TIPLER:
    a0=aktif(med,0.40,0.0); a1=aktif(med,0.0,ODUL*(D-TEV))
    top0+=pay*a0; top1+=pay*a1
    print("%-40s %7.2f %9.3f %9.3f %9.3f"%(ad,pay,a0,a1,1-a1/a0 if a0>0 else 0))
print("%-40s %7s %9.3f %9.3f %9.3f"%("AĞIRLIKLI",1.0,top0,top1,1-top1/top0))
print("\nDuyarlılık: yaptırım medyanı çarpanı (tüm tipler), aktif sahte teşebbüs payı")
for m in (0.5,1,2,4,8):
    s0=sum(p*aktif(med*m,0.40,0.0) for _,p,med in TIPLER); s1=sum(p*aktif(med*m,0.0,ODUL*(D-TEV)) for _,p,med in TIPLER)
    print("  x%-4s bugün %.3f  tedbir %.3f"%(m,s0,s1))
print("\nSınır: kimlik başı yıllık azamî sızıntı tavan x (D-tev) = %.0f TL; ilişkili kişiler (i) ile toplulaştırıldığı için aile başına aynı sınır; tek alıcı ilk yıl (f) kuralıyla %.0f TL"%(TAVAN*(D-TEV),(D-TEV)*6*33030))
print("Yaptırım medyanları, pay dağılımı, ödül ve rehin değerleri VARSAYIMDIR (ölçülmedi); sonuç yalnız yönü ve duyarlılığı gösterir")
