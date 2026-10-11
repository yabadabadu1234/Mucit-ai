import numpy as np, json, copy
from genc_model import tarife, W, GIDER, PRIM_AYLIK, SABIT_AYLIK, TAVAN
HEDEF=0.15
rng=np.random.default_rng(20261050)
def vektorler():
    return {
     "V1 Naylon fatura (alıcı gider şişirir)":dict(g0=0.145,c=(0.03,0.14),L=0.145,Pb=0.25,m=1.0,rec=0.25),
     "V2 Kimlik kiralayıp eşik bölme":dict(g0=0.037,c=(0.01,0.05),L=0.037,Pb=0.142,m=1.0,rec=0.142),
     "V3a Aile bireyini sahte ortak yapıp tavan çoğaltma":dict(g0=0.118,c=(0.0,0.0),L=0.118,Pb=0.118,m=1.0,rec=0.118),
     "V3b Aile dışı sahte ortak ile tavan çoğaltma":dict(g0=0.118,c=(0.02,0.06),L=0.118,Pb=0.118,m=1.0,rec=0.118),
     "V5 24 ay beklemeyip kayıt dışı çalışma (prim kaçışı)":dict(g0=0.35,c=(0.0,0.05),L=0.35,Pb=0.35,m=1.0,rec=0.35),
     "V6 Sahte bağımsızlık (işçiyi mikro mükellef yapma)":dict(g0=0.2175,c=(0.0,0.02),L=0.345,Pb=0.30,m=1.0,rec=0.30),
     "V7 Sermaye–emek ortaklığında gizli faiz":dict(g0=0.10,c=(0.0,0.02),L=0.0,Pb=0.10,m=1.0,rec=0.10),
     "V11 Donanım KDV mahsubunda fatura şişirme":dict(g0=0.10,c=(0.03,0.08),L=0.10,Pb=0.20,m=1.0,rec=0.10)}
def pstar(v):
    g=v['g0']-v['c'][0]
    if g<=0: return 0.0,0.0
    P=v['m']*v['Pb']
    pa=g/(g+P)
    ph=v['L']/(v['L']+v['rec']+P) if v['L']>0 else 0.0
    return pa,ph
def ajan(v,p_gercek,N=200000):
    c=rng.uniform(v['c'][0],v['c'][1]+1e-12,N) if v['c'][1]>v['c'][0] else np.full(N,v['c'][0])
    ps=rng.beta(2,6,N)
    g=v['g0']-c; P=v['m']*v['Pb']
    sald=((1-ps)*g-ps*P)>0
    kayip=np.where(sald,(1-p_gercek)*v['L']-p_gercek*(v['rec']+P),0.0)
    return float(sald.mean()),float(kayip.mean())
def rapor(V,etiket):
    print("== %s (hedef kırılma yakalama olasılığı ≤ %.2f; ölçülmemiş varsayım)"%(etiket,HEDEF))
    ok=True
    for ad,v in V.items():
        pa,ph=pstar(v); a,k=ajan(v,HEDEF)
        gec=(pa<=HEDEF and ph<=HEDEF)
        ok&=gec
        print("  %-58s p*saldırgan %.3f | p*Hazine %.3f | saldıran oranı %.3f | Hazine kaybı/TL %+.4f | %s"%(ad,pa,ph,a,k,"KAPANDI" if gec else "AÇIK"))
    return ok
V=vektorler()
ok=rapor(V,"TUR 0: mevcut teklif (J–N dâhil), ceza katsayısı 1")
TEDBIRLER=[
 ("T1 Sahte belge, sahte ortaklık ve gizli faizde alıcı/işveren/sermayedar için ceza katsayısı 3 + tescil iptali + üç yıl yasak",
   lambda V:[v.__setitem__('m',3.0) for k,v in V.items() if k[:3] in("V1 ","V3a","V3b","V5 ","V6 ","V7 ")]),
 ("T2 Hane toplulaştırması: eş, usul ve füruun hasılatı ve ortaklığı tavanda tek sayılır (aynı adres, aynı banka sahibi, aynı alıcı)",
   lambda V:V["V3a Aile bireyini sahte ortak yapıp tavan çoğaltma"].update(g0=0.0)),
 ("T3 Geri akış karinesi genişletilir: iade, mahsup ve üçüncü kişi hesabı; ortaklık ödemeleri yalnız payın kâr beyanına oranlı olarak portaldan",
   lambda V:(V["V1 Naylon fatura (alıcı gider şişirir)"].update(c=(0.06,0.14)),V["V7 Sermaye–emek ortaklığında gizli faiz"].update(g0=0.02))),
 ("T4 İşçi ihbar hakkı ve fark primi iki yıl geriye + ilişkili ödeyici toplulaştırması (tek müşteri sınırı ilişkili ödeyicilerin toplamıdır)",
   lambda V:V["V6 Sahte bağımsızlık (işçiyi mikro mükellef yapma)"].update(g0=0.12)),
 ("T5 Hasılat karinesi: 24 aylık geriye bakışta banka girişleri tevkifatsız ise karine ve tahakkuk",
   lambda V:V["V5 24 ay beklemeyip kayıt dışı çalışma (prim kaçışı)"].update(m=4.0)),
 ("T6 Ortaklıkta tavan ortak sayısıyla doğrusal artmaz: n ortaklıkta toplam tavan = tek tavan × (1 + 0,5·(n−1)); her ortak kendi hesabına tahsil eder",
   lambda V:V["V3b Aile dışı sahte ortak ile tavan çoğaltma"].update(g0=0.059,L=0.059,rec=0.059)),
 ("T7 Sahte bağımsızlıkta fark prim ve ücret vergisi işverenden asıl borçlu olarak tahsil + üç kat ceza (katsayı 4)",
   lambda V:V["V6 Sahte bağımsızlık (işçiyi mikro mükellef yapma)"].update(m=4.0,rec=0.45)),
 ("T8 Donanım faturasında seri numarası ve muadil tanımlayıcı sahteliğinde ceza katsayısı 3",
   lambda V:V["V11 Donanım KDV mahsubunda fatura şişirme"].update(m=3.0)),
 ("T9 Kimlik kiralamada kiralayan da cezalandırılır (katsayı 3) ve aynı ödeyiciden gelen ödemeler kimlikler arasında toplulaştırılır",
   lambda V:V["V2 Kimlik kiralayıp eşik bölme"].update(m=3.0,g0=0.02)),
]
LOG=[]
i=0
while not ok and i<len(TEDBIRLER):
    ad,f=TEDBIRLER[i]; f(V); LOG.append(ad); i+=1
    ok=rapor(V,"TUR %d: + %s"%(i,ad[:70]))
print("\nUygulanan tedbirler:",len(LOG)); 
for l in LOG: print(" -",l)
print("\nDuyarlılık: hedef yakalama olasılığı farklı olunca açık kalan vektör sayısı")
for h in (0.10,0.15,0.2,0.3,0.4,0.5):
    acik=[k[:3] for k,v in V.items() if not (pstar(v)[0]<=h and pstar(v)[1]<=h)]
    print("  hedef %.2f -> açık: %s"%(h,acik if acik else "yok"))
print("\nCeza katsayısı duyarlılığı (V6, tur sonu g0): m=1,2,3,4 için p*saldırgan:",[round(pstar(dict(V["V6 Sahte bağımsızlık (işçiyi mikro mükellef yapma)"],m=m))[0],3) for m in (1,2,3,4)])
# V4 ve yapısal vektörler
from genc_model import tarife
print("\nV4 Aile adına tescil: eski rejim kâr usulü vergi/hasılat − yeni tevkifat/hasılat (negatifse teşvik yok; prim eski mükellefte sürdüğü için yalnız vergi farkı kalır)")
pm=PRIM_AYLIK+SABIT_AYLIK
maks=-9
for h in [1,2,4,8,16,24]:
    H=h*W; kar=max((1-GIDER)*H-12*pm-400000,0); eski=float(tarife(np.array([kar]))[0])/H
    yeni=float(tarife(np.array([(1-GIDER)*H]))[0])/H
    maks=max(maks,eski-yeni); print("  H=%2d W: eski vergi oranı %.3f yeni tevkifat oranı %.3f fark %+.3f"%(h,eski,yeni,eski-yeni))
print("  azamî teşvik (eski−yeni):",round(maks,3),"-> %s"%("yok, yapısal olarak kapalı" if maks<=0 else "VAR"))
json.dump({k:dict(v,p_star=pstar(v)) for k,v in V.items()},open("sonuc_suistimal.json","w"),ensure_ascii=False,indent=1)
