# ELE 224L – Ön Çalışma 1–5 (İngilizce teslim raporu + Türkçe öğretici rehber)

Bu klasör, ELE 224L Elektronik Devreler Laboratuvarı'nın **5 ön çalışması** için hazırlanmıştır.
Her deney için iki belge vardır:

| Dosya (`out/`) | Ne işe yarar |
| :-- | :-- |
| `EN_ExperimentN_Preliminary_Report.docx` / `.pdf` | **Teslim edilecek İngilizce ön çalışma.** Föy şablonuna göre (Giriş / Hesaplar ve Simülasyonlar / Sonuçlar / Kaynaklar / Ekler), edilgen anlatım, numaralı şekil-tablo-denklem, Word denklemleri. |
| `TR_DeneyN_Ogretici_Rehber.docx` / `.pdf` | **Sadece öğrenmek için** Türkçe rehber: temel bilgi, her adımın nedeni, tamamen çözülmüş örnekler, tuzaklar, olası sorular. Teslim edilmez. |

Ad-soyad, numara, tarih alanları **boştur** (doldurunuz).

## Teslimden önce yapmanız gerekenler (dürüst liste)

1. **Simülasyon ekran görüntüleri sizin programınızdan (LTspice / Micro-Cap) alınmalıdır.** Bu belgelerdeki simülasyon grafikleri bu ortamda **ngspice** ile üretildi ve imleç (cursor) noktaları elle işaretlendi. Föy, ekran görüntüsünde **cihaz seri numaranızın** görünmesini ve imleç koordinatlarının tabloyla yazılmasını ister. Netlistler `ltspice/` klasöründedir (`File → Open`); **LTspice'ta bu ortamda açılmadı, test edilmedi.**
2. Raporda kullandığınız **MOSFET kare yasası tanımı**nı (`I_D = (K_N/2)(V_GS − V_TH)²`) kendiniz de doğrulayın; gerekçe Deney 2 rehberinde (veri sayfası sınaması) yazılıdır. Hocanız `I_D = K_N (V_GS − V_TH)²` kullanıyorsa Deney 2 rehberindeki "alternatif tanım" kutusuna bakın.
3. Şekil/tablo başlıkları ve atıflar **düz metindir** (Word "Resim Yazısı/Çapraz Başvuru" alanı değildir). Föy bunların Word alanlarıyla yapılmasını ister; teslimden önce isterseniz Word'de yeniden alana çevirin.
4. Breadboard çizimleri Tinkercad değil, bu klasördeki betikle üretilmiştir (bağlantıları otomatik denetlenmiştir). İsterseniz Tinkercad'de aynı yerleşimi yeniden çizin.
5. Deney 5 §1.1'deki **5 hata** (E1–E5) verilen çizimin *benim gözle okumama* dayanır (renk kodları büyütülerek okundu, bağlantılar delik delik çıkarılıp otomatik düğüm analizi yapıldı). Çizimi kendi gözünüzle de doğrulayın.
6. Fonksiyon üreteci frekansı Deney 1 §3.1'de föyde verilmediği için 1 kHz seçildi; Deney 5'te "bozulmasız" ölçütü olarak **THD ≤ %1** seçildi (kabulünüzü raporda belirtin).

## Deneysel olarak doğrulananlar (ve nasıl)

* Deney 1: el hesabı (iterasyon + Lambert-W) ↔ ngspice (föydeki parametrelerle ve sıcaklığı 0,026 V'a ayarlayarak %0,0012 içinde) ↔ MATLAB kodu **Octave'ta gerçekten çalıştırıldı** (sonuçlar Python ile birebir).
* Deney 2: el modeli (1. seviye denklemler) ↔ ngspice (CMOS evirici eşik gerilimi 2,2013 V ↔ 2,2020 V).
* Deney 3: fazör analizi ↔ ngspice AC/geçici analiz (10 kHz kazancı 7,69 ↔ 7,78).
* Deney 4: el modeli ↔ ngspice; hata senaryoları (12 V / 0 V) ayrı ayrı simüle edildi.
* Deney 5: CE (100 kHz) 52,74 ↔ 52,75; CC 0,9924 ↔ 0,9923; breadboard bağlantıları otomatik denetlendi.

## Kabuller ve sınırlar

* BC238A SPICE modeli veri sayfasındaki tipik değerlere (V_BE(on)=0,62 V @2 mA; β=170) ve doyma gerilimlerine göre **uydurulmuştur**; Early etkisi yoktur. BR, RB değerleri kalibrasyondur (Deney 4 Ek A).
* BS170/BS250 modellerinde föydeki `.model` satırlarından ngspice'ın tanımadığı RG, RB, Rds, Tt çıkarıldı (DC sonuçları etkilemez); `ltspice/` klasöründeki dosyalarda aslî satırlar korunmuştur.
* 1N4148 modeli (IS=2,52n; N=1,752; RS=0,568) bir üretici modelidir; LTspice kütüphanesindeki ile farklı olabilir.
* BS250'nin bacak sırası (S-G-D) veri sayfasının alttan görünüş çiziminden **çıkarılmıştır**.

## Yeniden üretim

```
cd src
python3 build.py 1 2 3 4 5     # hesap + simülasyon + şekiller + belgeler (ngspice, scipy, matplotlib, schemdraw, python-docx, pandoc, libreoffice gerekir)
python3 export_ltspice.py      # ltspice/ klasörü
```

Klasörler: `src/` (kod), `spice/` (ngspice netlistleri), `ltspice/` (LTspice'a açılabilir netlistler), `matlab/` (Deney 1 MATLAB kodu), `fig/` (şekiller), `out/` (belgeler).
