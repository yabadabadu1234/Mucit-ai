# PCB Termal / IR-Drop Hızlı Çözücü — Ön Fizibilite (4 Ekim 2026)

Yöntem: 5 web araması; tam okuma yapılmadı. Bu **ön yoklamadır**, nesting raporu kadar derin değil. Ölçülmemiş her şey işaretlidir.

## Hüküm
**"Yerli çözümü yok, 30–80 bin $'lık tekel" tezi büyük ölçüde yanlış çıktı.** Fikir bir boşluk değil, dolu bir alanın en ucuz ucudur; ayrıca açık kaynak seçenekler var. Girilecekse konum "yerli tekelin boşluğu" değil, "KiCad/Altium kullanan küçük ekip için hızlı, tek tuşluk, çevrimdışı güç kartı denetçisi" olabilir; bu bile doğrulanmamış bir hipotezdir.

## Bulgular
1. **Fiyat iddiası çelişiyor.** Altium PDN Analyzer (IR-drop ve güç dağılımı) bir kullanıcıya göre 2.590 $ tek sefer; liste fiyatı ~163 $/ay (~1.956 $/yıl) ([Vendr/FEDEVEL/SourceForge](https://sourceforge.net/software/product/PDN-Analyzer/)). Cadence Sigrity PowerDC "geçmişte 25.000 $'dan" (eski fiyat). 30–80 bin $ ancak Icepak/Celsius gibi tam paketler için doğru olabilir; PCB IR-drop için çıtanın altı çok daha ucuz.
2. **Ürün kategorisi doludur:** Ansys SIwave (DC IR-drop, akım yoğunluğu) + Icepak, Cadence Sigrity PowerDC / Celsius, Altium PDN Analyzer, Siemens HyperLynx Thermal ve Simcenter Flotherm. Hepsi Gerber/ODB++ veya ECAD doğrudan içe aktarır.
3. **Yerel dağıtıcılar var:** Icepak (Venon Yazılım), Flotherm (DTA), elektronik güvenilirlik (Numesys) Türkiye'de satılıyor. Yerli *geliştirilmiş* PCB termal çözücü bulamadım (aramada çıkmadı); bu "yok" demek değil, "bulamadım" demektir.
4. **Açık kaynak rakipler ücretsiz:** KiCad Thermal Sim (çok katmanlı bakır termal tahmin + DC akım çözücü), SPIKE (KiCad için PI/SI/termal), Elmer FEM + FreeCAD/Salome akışı (GPL), ayrıca dergilerde yayınlanmış FEM yöntemleri. Bunlar fiyat tezini doğrudan zayıflatır.
5. **Savunma/gizlilik argümanı:** "Yabancı buluta yüklemek yasak" iddiasını **doğrulayamadım.** Ayrıca SIwave/Altium zaten masaüstü, çevrimdışı çalışır; offline olmak tek başına fark değil. ASELSAN/ROKETSAN/TUSAŞ alt yüklenicilerinin yerli yazılımı tercih ettiği veya şart koştuğu bir belgeye de rastlamadım.
6. **"1.500'den fazla yerli donanım firması" sayısı kaynaksız.** Doğrulamadım.
7. **Matematik doğru ve olgun:** Laplace/Poisson DC çözümü + Joule kaynağıyla ısı denklemi, FDM/FVM, sparse çözücü (CG, multigrid) standart; zor kısım matematik değil, **Gerber/ODB++ içe aktarma, via/plating modellemesi, sıcaklığa bağlı iletkenlik, doğrulama (IPC-2152 ile kıyas) ve güven.** Güç elektroniğinde hata maliyeti yüksek; "yerli simülatör yanlış söyledi, kart yandı" riski hendektir. Sadece Gerber'den bakır geometrisi çıkarılır; net/pin/akım kaynağı bilgisi netlist ister, tek başına Gerber yetmez (kendi tahminim, kaynaksız).

## Neyi bilmiyorum
- Türkiye'de kaç firmanın gerçekten bu aracı satın aldığı veya ihtiyaç duyduğu.
- Yerli çözümün gerçekten olmadığı (bulamadım ≠ yok).
- Müşterilerin ödeme isteği: 40–60 bin TL/yıl tutarının pazarlığı, kimden duyduğum bir rakam değil (kullanıcı önerisi).

## Önerilen ucuz sınama (1 hafta, kod yazmadan)
1. KiCad Thermal Sim ve Elmer ile 3 gerçek güç kartı (BMS, şarj, motor sürücü) çalıştır; sonucu IPC-2152 tablosu veya kamera ölçümüyle karşılaştır.
2. 10 mühendisle görüş: şimdi ne kullanıyorsun, ne kadar ödüyorsun, kart yanınca ne yapıyorsun?
3. Eğer çoğu "Altium PDN/ücretsiz araç yetiyor" derse dur. "Hiçbirini kullanmıyoruz, bilmiyoruz" derse boşluk bilgi/kullanım kolaylığıdır, matematik değil.

## Kaynaklar
- [DCIR SIwave](https://www.leapaust.com.au/blog/emag/dcir-analysis-of-pcb-in-ansys-siwave/); [Sigrity PowerDC](https://resources.pcb.cadence.com/sigrity-datasheets/sigrity-powerdc-4); [Celsius PowerDC](https://www.flowcad.com/en/celsius-powerdc.htm); [Altium termal](https://resources.altium.com/p/pcb-thermal-analysis-software)
- [PDN Analyzer fiyat](https://sourceforge.net/software/product/PDN-Analyzer/); [Vendr Altium](https://www.vendr.com/marketplace/altium)
- [Icepak (Venon)](https://www.venonyazilim.com/icepak); [Flotherm (DTA)](https://www.dta.com.tr/simcenter-flotherm); [Numesys](https://www.numesys.com.tr/elektronik-guvenilirlik/)
- [KiCad Thermal Sim](https://github.com/Dietschi10/KiCad_Thermal_Sim); [SPIKE](https://github.com/wayri/SPIKE); [OSS PCB termal](https://jrainimo.com/build/2024/11/oss-thermal-simulation-of-pcbs/)
- [Siemens: akım taşıma kapasitesi](https://blogs.sw.siemens.com/simulating-the-real-world/2021/01/20/thermal-influence-on-maximum-current-carrying-capacity/)
