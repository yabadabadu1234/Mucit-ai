# "Yerlisi ve açık kaynağı olmayan matematik sahası" taraması (4 Ekim 2026)

Ölçüt (kullanıcı): hem yerli hem açık kaynak karşılığı bulunmayan, yabancıya mahkûm bir saha. Yöntem: aday başına 1–3 web araması; sayfaların çoğu tam okunmadı. **Yokluk kanıtı ancak "aramada çıkmadı" kadar güçlüdür;** kapalı savunma kodları ve küçük açık kaynak depolar kaçmış olabilir.

## Elenenler (açık kaynak karşılığı bulundu)
| Saha | Açık kaynak bulgusu | Yerli bulgusu |
| :-- | :-- | :-- |
| Enjeksiyon kalıp akışı (Moldflow) | [openInjMoldSim](https://github.com/krebeljk/openInjMoldSim) (OpenFOAM, GPL, Moldex3D/Moldflow'a karşı akademik doğrulama) | yerli bulunamadı |
| Kaynak çarpılması (SYSWELD) | OS-WeldSim, MOOSE | yerli bulunamadı |
| Sac şekillendirme (AutoForm/PAM-STAMP) | Keysight BM-Stamp "FOSS lisans" (iddia, doğrulanmadı) | yerli bulunamadı |
| Çok fazlı hat akışı (OLGA/LedaFlow) | [Marlim3](https://github.com/petrobras/marlim3) (Petrobras, 1B drift-flux, geçici) ve OpenSTREAM | TPAO "ZEKİ" platformu var (içeriği belirsiz, yabancı ortaklarla) |
| Gaz şebekesi geçici akış (SIMONE) | Grazer (AGPL), GasModels.jl; pandapipes **yalnız kalıcı rejim** | yerli bulunamadı |
| Sismik veri işleme | — | **SDT+TPAO "Orhun" milli proje** |
| Madencilik planlama (Whittle/Datamine) | modüler Python araçları, bütünleşik değil | yoklanmadı |
| Basınçlı kap (PV Elite/COMPRESS) | Excel/VBA ASME-PVDE (küçük) | yerli bulunamadı |
| Boru gerilme (CAESAR II) | PSAT/script'ler (küçük) | yerli bulunamadı (Rohr2 ithal) |
| Eşanjör (HTRI) | ht kütüphanesi, DWSIM | yerli bulunamadı |
| Döküm katılaşma (MAGMA/ProCAST) | OpenFOAM katılaşma çözücüleri (anahtar teslim araç yok) | yerli bulunamadı |

## En zayıf rakipli kalan: **dişli/aktarma organları yük dağılımı ve ömür analizi**
- **Standart notu:** ISO 6336/AGMA 2101 mukavemet hesabı için küçük açık kaynak var: [python-gearbox](https://github.com/efirvida/python-gearbox).
- **Asıl matematik (LTCA — yüklü diş temas analizi, yük dağılımı, mikro-geometri):** arama sonucuna göre bunu yapan ticari sistemler "az sayıda firma" (GEMS, KiMOS, BECAL, HyGears); **olgun açık kaynak LTCA bulamadım.**
- **Rulman iç yük dağılımı (ISO/TS 16281):** MESYS, BearingSolve, KISSsoft ticari; açık kaynak karşılık **bulamadım.**
- **Yerli durum:** Birom Makina gibi firmalar Masta, KISSsoft, Ansys kullanıyor ve ASELSAN, MKE, Otokar, FNSS, Tümosan'a alt yüklenicilik yapıyor ([Birom](http://www.birom.com.tr/savunma.php)); TEI'nin turboşaft motorunda milli dişli kutusu *donanımı* geliştirilmiş ([TÜBA](https://tuba.gov.tr/files/yayinlar/bilim-ve-dusun/TUBA-978-625-8352-16-0_ch26.pdf)); **yerli bir hesap yazılımı bulamadım** (akademik VB/AutoLISP parametrik çizim çalışmaları hariç).
- **Alıcılar (varsayım):** savunma alt yükleniciler, rüzgâr türbini redüktörü, otomotiv/tarım aktarma organları, TEI/motor programları.
- **Matematik:** Hertz teması ve eğrilik, diş eğilmesi/kök gerilmesi için sonlu eleman veya analitik esneklik, temas yük dağılımı (ayrık doğrusal olmayan kısıtlı denge), mikro-geometri (profil/helis düzeltmesi) optimizasyonu, titreşim/iletim hatası, sistem seviyesi şaft-yatak-dişli bağlaşımı. Hepsi seyrek/yoğun lineer cebir ve optimizasyon: tam bir "ağır riyaziye" sahası.

## Bu, "kesin boş" değildir; nedenleri
1. python-gearbox gibi açık kaynak mevcut (standart hesabı için); LTCA'yı sıfırdan yazan akademik kodlar da muhtemelen vardır, makale ekleri olarak.
2. Yerli bir savunma içi kod gizli olabilir; "bulamadım" ≠ "yok".
3. **Ticari engel:** KISSsoft/MASTA'nın değeri hesabın kendisi kadar *doğrulanmış* olması (test ve sertifika). Bunu yeni bir araç kısa sürede kuramaz.
4. Pazar küçük ve niş (yüzlerce mühendis, binlerce değil).

## Önerilen sınama
1. python-gearbox'ı ve bir LTCA makale kodunu, açık bir referans dişli çifti için KISSsoft eğitim sürümü veya yayınlanmış deney verisiyle karşılaştır.
2. Birom, Aselsan, TEI, Tümosan'daki dişli tasarımcılarına: şu anda hangi araç, ne maliyet, LTCA için ne kullanıyorsunuz?
3. Karşılaştırmada fark yoksa dur; varsa ilk ürün **LTCA + mikro-geometri optimizasyonu** (python-gearbox'ın eksik bıraktığı kısım).

## Kaynaklar
[openInjMoldSim](https://github.com/krebeljk/openInjMoldSim) · [Marlim3](https://github.com/petrobras/marlim3) · [OpenSTREAM](https://github.com/OpenSTREAM-solvers/openstream) · [Grazer ve GasModels.jl](https://github.com/lanl-ansi/GasModels.jl) · [pandapipes vs SIMONE](https://www.sciencedirect.com/science/article/pii/S2949821X26001195) · [SDT Orhun](https://www.sdt.com.tr/tr/cozumlerimiz/simulasyon-sistemleri-ve-bilisim-teknolojileri/milli-sismik-veri-islem-yazilimi) · [ZEKİ](https://www.trthaber.com/foto-galeri/iste-milli-yazilim-zekinin-gozunden-sakarya-gaz-sahasi/51518.html) · [python-gearbox](https://github.com/efirvida/python-gearbox) · [Birom](http://www.birom.com.tr/savunma.php) · [MESYS ISO 16281](https://www.mesys.ch/doc/FlyerRollingBearingAnalysis.pdf) · [OS-WeldSim](https://www.researchgate.net/publication/394288280_OS-WeldSim_an_open-source_framework_for_finite_element-based_welding_simulation) · [ASME-PVDE](https://github.com/ry4ngch/ASME-PVDE)

---
## Ek (simülasyon dışı tarama, 4 Ekim 2026)
| Saha | Açık kaynak | Yerli | Not |
| :-- | :-- | :-- | :-- |
| **Çip tasarım araçları (EDA), özellikle sign-off (DRC/LVS/zamanlama/güç) ve analog/RF** | OpenROAD, Yosys (sentez, yerleştirme-yönlendirme); sign-off ve analog/RF **eşdeğer değil** (kaynaklar: Smart Silicon, arXiv 2511.15564) | EDA aracı olarak yerli çözücü **bulamadım** (çıkan "CAEeda" bir mühendislik analiz aracı, çip EDA'sı değil) | Cadence/Synopsys oligopol; ABD 2025'te Çin'e EDA satışını lisansa bağladı, iki ay sonra kaldırdı ([CNBC](https://www.cnbc.com/2025/07/03/us-lifts-chip-software-curbs-on-china-amid-trade-truce-synopsys-says-.html)). Türkiye'de TÜBİTAK BİLGEM Çakıl/YONCA, HIT-30 çip çağrısı (5 milyar $ hedef) devlet talebini gösteriyor |
| **Karma tamsayılı doğrusal programlama (MILP) çözücüsü** | HiGHS ve SCIP var; zor örneklerde ticarilerden yaklaşık 10–20 kat yavaş ([HiGHS tartışması](https://github.com/ERGO-Code/HiGHS/discussions/1683)) | yerli çözücü **bulamadım** | Gurobi ~10–50 bin $/yıl; savunma lojistiği, enerji, üretim planlamada kullanılıyor |
| Seyrüsefer (GNSS/INS) süzgeç yazılımı | KF-GINS, NaveGo, INSLIB (DO-178 testli), OpenIMU | — | **Elendi**: açık kaynak bol |

Not: EDA'da yerli yokluğu "aramada çıkmadı"dır; devlet içi (BİLGEM/ASELSAN) kapalı araçlar bu aramaya görünmez.
