import numpy as np, json, itertools
from genc_model import tarife, W, GIDER, TAVAN
SAFI=1-GIDER
def tev_kademeli(H): return float(tarife(np.array([SAFI*H]))[0])
def tev_duz(H): return 0.105*H
print("V2 BÖLME: saldırgan H hasılatı k kimliğe böler, kimlik başı bedel c_id; kazanç = tek kimlik vergisi − k kimlik vergisi − k·c_id·H/k")
for ad,f in (("kademeli (mevcut 1(e))",tev_kademeli),("düz %10,5 (yeni 1(e))",tev_duz)):
    enb=0.0;arg=None
    for H in np.arange(1,24.01,0.5)*W:
        for k in range(1,11):
            for c in (0.0,0.005,0.01,0.02):
                g=f(H)-k*f(H/k)-c*H*(k-1)
                if g>enb: enb=g;arg=(round(H/W,1),k,c)
    print("  %-26s azamî kazanç %.0f TL (strateji %s) -> %s"%(ad,enb,arg,"imkân VAR" if enb>1 else "imkân KESİLDİ (azamî kazanç 0)"))
print("\nV6, V7, V11: YAPISAL ÖZDEŞLİK (mantıksal ispat; simülasyon DEĞİL, sonucu kuralın tanımından çıkar)")
print("  V6: kaynakta tahakkuk eden tutar = işverenin kaçınacağı SGK payı ve ücret farkı (bağımlı pay üzerinden, ilişkili ödeyiciler toplanarak). Kazanç = kaçınılan − tahakkuk eden = 0, ödeyiciyi bölmek bağımlı payı değiştirmez.")
print("      Dürüst bağımsız serbest çalışan etkilenmez: bağımlı pay yalnız son 24 ayda bordrolu çalıştığı ödeyicilerden gelen paydır.")
print("      KESİLEMEYEN: gerçek bir üçüncü kişi aracı şirket (taşeron) zinciri; iz yalnız mikro hesaplar ve ilişkili kişi bağı üzerinden sürülür.")
print("  V7: portalca kayıtlı her ödeme formül payını aşan kısmıyla birlikte anapara geri ödemesi sayılır; sistem dışı elden ödeme sözleşmede yoktur ve alacağa hak vermez.")
print("  V11: aynı seri numarası ikinci kez mahsup edilemez; KESİLEMEYEN: gerçek olmayan seri numarası (satıcının e-belge mükellefi olması ve banka ödemesi şartı yalnız sınırlar).")
print("\nV1 NAYLON FATURA ve V3b SAHTE ORTAK: gelir kaydırma; ekonomik kök = alıcı oranı (%25) ile tevkifat (%10,5) farkı; paranın sistem dışı geri dönüşü hiçbir hesap kuralıyla kapatılamaz")
for ad,fark in (("V1 alıcı kurumlar vergisi %25",0.25-0.105),("V1 alıcı gelir vergisi %40",0.40-0.105)):
    sınır=fark*TAVAN
    print("  %-34s kimlik başı azamî sızıntı = fark × tavan = %.3f × %.0f = %.0f TL/yıl"%(ad,fark,TAVAN,sınır))
print("  Dürüste zarar vermeyen sınırlayıcılar: (r) geri akış karinesi, (s) kimlik tekliği, (i) toplulaştırma, (n) alıcı yoğunluğu işareti; hepsi mevcut metindedir")
