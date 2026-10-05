# Rakip ne kadar kötü, fark atmak ne kadar kolay? — aday yeniden puanlama (5 Ekim 2026)

Ölçüt (kullanıcı): (1) **mevcut rakipler ne kadar kötü** (belgelenmiş açık), (2) **fark atmak ne kadar kolay**. Eklediğim iki yardımcı ölçüt: (3) **burada tek başına test edilebilir mi** (açık veri/benchmark), (4) **alıcı net mi**.
Puanlar (1–5) **benim yargımdır**; kanıt kalitesi ayrı yazılmıştır. Ticari yazılımları doğrudan koşamadığım için "rakip açığı" literatürden dolaylıdır.

| Aday | 1. Rakip açığı | Kanıt | 2. Fark atma kolaylığı | 3. Tek başına test | 4. Alıcı | Not |
| :-- | :-: | :-- | :-: | :-: | :-: | :-- |
| **Gerçek şekilli, çok levhalı nesting çekirdeği** | 4 | Literatürde "en iyi akademik doluluk, ticari sonuçtan çok yüksek" (çoğu kıyas kümesinde); kitle kaynaklı çözümler ticari tabandan ~%4 iyi; GCS "yaygın bir ticari sistemi belirgin geçiyor" ([arXiv 2206.00032 ve ilgili çalışmalar](https://arxiv.org/pdf/2206.00032), [Crowdsourcing](https://www.tandfonline.com/doi/full/10.1080/00207543.2015.1102355)) | 3 | 5 | 3 | Sparrow MIT lisanslı, şerit dolumunda en iyi; çok levha ve kalan parça açık kalan yer. Moat zayıf. Ticari rakipler (Lantek, SigmaNEST) kapalı |
| **1B/2B kesim (profil, panel, demir)** | 2–3 | Akademik tam çözüm, ticari paketlere göre bir kâğıt-fabrikası örneğinde ortalama %2,5 üretim tasarrufu; bir vakada atık %3,5→%1 (tek tek çalışmalar) ([JIEM](https://www.jiem.org/index.php/jiem/article/download/1653/781)) | 4 | 5 | 4 | Türkiye'de ucuz/ücretsiz yerli programlar çok (KopEksper, Yedikare, Aluvector, CutOpt); fark küçük olabilir |
| **Küçük imalatçı için sonlu kapasiteli çizelgeleme (APS)** | 4 | ERP'lerin çoğu sonsuz kapasite varsayar; sonlu kapasiteli çizelgeleme ile OTD %10–25, WIP %20–40 düşüş (satıcı iddiası, doğrulanmadı) ([UserSolutions](https://usersolutions.com/blog/how-production-scheduling-improves-on-time-delivery)) | 3 | 3 | 3 | Gerçekçi kısıtlı veri bulmak zor; Logo/Mikro/Netsis eklentisi olabilir |
| Taze ürün sipariş/talep | 3 | Taban çizgileri zayıf (belgelenen), ama yerli "YZ ile sipariş önerisi" ürünleri var | 3 | 4 | 2 | Muhatap testini zor geçiyor (önceki rapor) |
| Sanayi elektrik fatura/tüketim analizi | 3 | Rekabet çoğunlukla elle yapılan danışmanlık; veri açık değil | 4 | 2 | 4 | Kamuya açık veri yok; tek başına test zor |
| Depo toplama rotası/parti | 2 | Optimal ile S-şekli arasında "önemli" tasarruf diyen çalışmalar var, ama pratikte fark küçük olabilir | 4 | 4 | 3 | Açık küçük |
| Konteyner/palet yükleme | 2 | Akademik ortalama %89–91 hacim; en iyi rekor üstüne +%0,62 | 2 | 5 | 3 | Başlıca tavan küçük |
| MIP çözücüsü | 2 | COPT/Optverse güçlü; HiGHS 5x yavaş ve kapanıyor | 1 | 4 | 4 | Genel amaç için kapı kapalı |
| Dişli LTCA | 1 | KISSsoft/MASTA olgun | 2 | 3 | 2 | |
| Çip EDA sign-off | 1 | Cadence/Synopsys olgun | 1 | 1 | 2 | |
| PCB termal/IR-drop | 2 | Altium PDN ~2k$/yıl, açık kaynak var | 3 | 3 | 3 | Boşluk yok |

## Sonuç (çıkarım, kanıt değil)
Ölçüte göre en iyi iki aday: **(1) çok levhalı gerçek şekilli nesting çekirdeği**, **(2) küçük imalatçı için sonlu kapasiteli çizelgeleme**. Hızlıca kanıtlanabilecek üçüncüsü **1B/2B kesim** (fark küçük ama ispatı kolay; nesting ve çizelgelemeyle ortak çekirdek kullanabilir).

## Patent notu (hafızadan, doğrulanmadı)
Matematiksel yöntemler ve bilgisayar programları "kendi başına" patent konusu dışında sayılır (Türk Sınai Mülkiyet Kanunu ve Avrupa Patent Sözleşmesi'nin ortak ilkesi). Teknik bir sonuç üreten, makineye bağlı yöntem istisnasına girebilir. Bir patent vekiliyle teyit edilmeden ticari planın patente dayandırılması önerilmez.

## Ölçüm planı (kamuya açık veriyle, kimseye gitmeden)
- **Nesting:** ESICUP kümeleri ve literatürdeki en iyi bilinen değerler; taban çizgileri Sparrow ve Deepnest-next. Ticari sistem açığı literatürden alınır.
- **Çizelgeleme:** job-shop kıyas kümeleri + sonlu kapasiteli kural tabanlı çizelge ile "sonsuz kapasite" taban çizgisinin karşılaştırması; eksik olan kısıtlar açıkça yazılır.
- **1B/2B kesim:** gerçek atölye parça listeleri benzeri sentetik kümeler + yerli programların (Yedikare vb.) aynı kümelerde çıktısı.
- Her aday için önceden eşik: ortanca iyileşme ≥ X puan, yoksa dur.

---
## Ek (5 Ekim 2026, ikinci tur): yapıştırılan "verimsiz sektörler" listesinin yoklanması
Listede (15 sektör) çoğu çözüm "blokzincir, NFT, pazaryeri" türü; matematik ve kıyas verisi olanlar yoklandı:

| Aday | Rakip açığı (kanıt) | Fark kolaylığı | Tek başına test | Alıcı | Not |
| :-- | :-: | :-: | :-: | :-: | :-- |
| **Kaynak kısıtlı proje çizelgeleme (RCPSP): inşaat** | **4–5.** PSPLIB J30 kümesinde optimale göre gecikme: MS Project %5,18; Primavera %9,45; Spider %2,24 ([PlanningPlanet test raporu](https://planningplanet.com/forums/planning-scheduling-programming-discussion/531539/test-report-comparison-resource-leveling-en)) — **forum testi, hakemli değil**; J30 küçük bir küme | 4 (açık kaynak CP-SAT ve metasezgiseller; PSPLIB'de bilinen optimumlar) | **5** (PSPLIB açık) | 3–4 (inşaat planlamacıları; Primavera/MSP'ye bağlılık güçlü, dosya tabanlı eklenti mümkün) | Aynı çekirdek küçük imalatçı çizelgelemeye de uygulanır |
| Ağır ekipman kiralama atıl kapasite | 3. Filo kullanım oranı tipik %55–70, hedef %65–85 ([Quipli](https://www.quipli.com/resources/calculators/general-and-heavy-equipment-rental-utilization/)); mevcut araçlar çoğunlukla izleme, optimizasyon değil | 3 | 1 (açık veri yok) | 3 | Sentetik veriye mahkûm |
| Boş konteyner konumlandırma | 3. Yıllık 15–20 milyar $; maliyetin ~%33'ü şirket verimsizliği ([BCG](https://www.bcg.com/publications/2015/transportation-travel-logistics-think-outside-your-boxes-solving-global-container-repositioning-puzzle), [Loadstar](https://theloadstar.com/empty-container-repositioning-costs-shipping-industry-20bn-year/)) | 2 | 2 | 1 (armatörler çok büyük, kapalı) | |
| Son kilometre teslimat | 2. Amazon son kilometre veri seti açık (6.112 rota) ([LMRRC](https://github.com/donato-maragno/Amazon-LMRRC)); hedef şoför davranışını tahmin | 3 | 4 | 3 | Rakipler çok, VRP açık kaynak güçlü |

### Listedeki rakamların yoklaması
- "Projelerin %80'inden fazlası bütçeyi aşar": McKinsey'e göre **mega projelerin %98'i %30'dan fazla aşıyor** ve milyar dolar üstü mega projelerde ortalama aşım ~%80; liste bu rakamı bütün projelere yaymış ([McKinsey](https://www.mckinsey.com/capabilities/operations/our-insights/megaprojects-the-good-the-bad-and-the-better)).
- "Konteynerlerin %20'si boş": BCG bölgeye göre %14–29 (ABD %15, Avrupa %29, Çin %25); başka bir kaynak "her üçüncü konteyner boş" diyor; **tek bir sayı yok**.
- "Yaş sebze-meyve %30–40 yolda ziyan": doğrulamadım.
- "E-ticarette %20–40 iade": doğrulamadım.
- Blokzincir/NFT çözümleri: bu ölçütlere (rakip açığı, test edilebilirlik) uymuyor; matematik içermiyor.

### Güncel sıralama
1. **Kaynak kısıtlı çizelgeleme çekirdeği** (inşaat ve küçük imalatçı): rakip açığı belgeli, kıyas verisi açık, rakibin gelişmiş yöntemi var ama kapalı ve eski.
2. **Çok levhalı gerçek şekilli nesting çekirdeği**.
3. 1B/2B kesim (kanıtı kolay, açığı küçük).
