import subprocess, math
from common import *
from docbuilder import Doc

def build():
    D = Doc("tr")
    D.title_block([("TOBB Ekonomi ve Teknoloji Üniversitesi", 13, True), ("Elektrik – Elektronik Mühendisliği Bölümü", 12, False),
                   ("ELE 201 L – Devre Analizi I Laboratuvarı", 14, True), ("Deney 1 – Laboratuvar Raporu", 14, True), ("Güz 2026", 12, False)],
                  [("Ad Soyad", ""), ("Numara", ""), ("Tarih", ""), ("Grup Arkadaşı", "Işıl Fidancan, Buhe Işıklar")])

    # ---- sayılar
    R1, R2, R3 = 464.0, 99100.0, 10.30e6
    S = R1 + R2 + R3; Sd = 10.45e6
    P = 1 / (1 / R1 + 1 / R2 + 1 / R3); Pd = 460.0
    r1, r2, r3, rxd = 464.0, 456.0, 3220.0, 3260.0
    rx = r2 * r3 / r1; rxs = r1 * r3 / r2; rc = 3300.0
    def pct(a, b): return (a - b) / b * 100
    def pc(x, d=2): return n(x, d) + " %"
    def loaded(R, Rin, Vs=15.0):
        Rp = R * Rin / (R + Rin); return Vs * Rp / (R + Rp)

    # ================= GİRİŞ
    D.h(1, "Giriş")
    D.h(2, "Deneyin Amacı")
    D.p("Bu deneyin amacı, devre analizinin dört temel yapı taşını gerçek elemanlar ve gerçek ölçü aletleriyle sınamaktır: (i) dirençlerin seri ve paralel bağlanmasıyla eşdeğer direncin nasıl oluştuğunun ölçülmesi, (ii) gerilim bölücü devresinde çıkış geriliminin hem multimetreyle hem osiloskopla ölçülüp ölçü aletinin devreyi nasıl etkilediğinin görülmesi, (iii) Wheatstone köprüsü ile bilinmeyen bir direncin ölçülmesi ve (iv) 3 bitlik R-2R merdiven tipi sayısal-analog çevirici (DAC) devresinin çıkış geriliminin ölçülmesi. Her bölümde önce kuramsal değer hesaplanmış, sonra ölçülen değerle karşılaştırılmış ve aradaki fark açıklanmıştır.", align="j")
    D.h(2, "Deneyin Faydaları")
    D.p("Deney sonunda şu kazanımlar elde edilmiştir. Birincisi, bir direncin üzerinde yazan değerin (renk kodu) bir “hedef” olduğu, gerçek değerin tolerans içinde bu hedeften saptığı görülmüştür. İkincisi, ölçü aletinin devreye paralel veya seri girdiği için devreyi değiştirdiği, bu etkinin devre dirençleri aletin iç direncine yaklaştıkça büyüdüğü gösterilmiştir. Üçüncüsü, köprü yönteminde sonucun bir alet okumasına değil bir denge koşuluna dayandığı ve bu yüzden hassas olabildiği anlaşılmıştır. Dördüncüsü, sayısal bir kodun doğrusal bir direnç ağıyla analog gerilime çevrilebildiği ve bu çevirinin doğruluğunun direnç toleranslarına bağlı olduğu görülmüştür.", align="j")

    # ================= ÖLÇÜMLER
    D.h(1, "Ölçümler")
    D.p("Bütün ölçümler laboratuvarda UNI-T UT33D+ el tipi multimetre ve Tektronix TBS 1022 osiloskop ile yapılmış, değerler aletlerin ekranından okunmuş ve her okuma fotoğraflanmıştır (fotoğraf numaraları EK-1’deki okuma çizelgesinde verilmiştir). Çıkış gerilimlerinin ve DAC çıkışlarının kuramsal değerleri elle ve Python ile düğüm analizi yapılarak hesaplanmıştır. Kuramsal değer $x_k$ ve ölçülen değer $x_o$ için fark yüzdesi şöyle tanımlanmıştır:", align="j")
    D.eq(r"\text{Fark}\,(\%)=\frac{x_o-x_k}{x_k}\times 100", "fark")
    D.p("Bir not: Rapordaki değerler fotoğraflardaki ekran okumalarından ve elle doldurulmuş föyden alınmıştır; okunamayan veya yorumlanması belirsiz kalan okumalar ilgili yerde belirtilmiştir ve hiçbir değer tahmin edilerek yazılmamıştır.", align="j")

    # ---- 1
    D.h(2, "Dirençlerin Seri ve Paralel Bağlantıları")
    D.h(3, "Devre Tahtası Yerleşimi")
    D.p("Seçilen dirençler $R_1 = 470\\ \\Omega$, $R_2 = 100\\ \\mathrm{k\\Omega}$ ve $R_3 = 10\\ \\mathrm{M\\Omega}$ (anılan değerler renk kodundan; gerçek değerler aşağıda ölçülmüştür) dirençleridir. [[f:bbs]]’te dirençlerin seri, [[f:bbp]]’te paralel bağlanmış hâlinin devre tahtası yerleşimi gösterilmiştir. Seri bağlantıda dirençler uç uca eklenir, aralarındaki ortak sütun (a–e delikleri iç bağlıdır) bağlantı noktasıdır; paralel bağlantıda üç direncin birer ucu aynı sütuna, diğer uçları ise başka bir ortak sütuna takılmıştır. Çizimler TinkerCAD’e benzer biçimde hazırlanmış olup her bağlantı çizim sırasında program tarafından düğüm düğüm denetlenmiştir.", align="j")
    D.fig("bbs", a("bb_seri.png"), "Dirençlerin seri bağlantısı (devre tahtası yerleşimi). Multimetre iki serbest ucu arasına bağlanır.", 14.0)
    D.fig("bbp", a("bb_par.png"), "Dirençlerin paralel bağlantısı (devre tahtası yerleşimi).", 14.0)
    D.h(3, "Ölçümler ve Hesaplar")
    D.p("Dirençler önce ayrı ayrı ölçülmüş ([[f:fd]]), sonra seri bağlanıp toplam direnç ölçülmüş, daha sonra paralel bağlanıp ölçülmüştür ([[f:fsp]]). Seri bağlantının eşdeğeri dirençlerin toplamıdır; çünkü seri elemanlardan aynı akım geçer ve gerilimler toplanır:", align="j", keep=True)
    D.eq(r"R_{seri}=R_1+R_2+R_3=464\ \Omega+99{,}1\ \mathrm{k\Omega}+10{,}30\ \mathrm{M\Omega}=" + (n(S / 1e6, 4)).replace(",", "{,}") + r"\ \mathrm{M\Omega}", "seri")
    D.p("Paralel bağlantıda ise her dirençten aynı gerilim geçer ve akımlar toplanır; bu yüzden iletkenlikler toplanır:", align="j", keep=True)
    D.eq(r"\frac{1}{R_{par}}=\frac{1}{R_1}+\frac{1}{R_2}+\frac{1}{R_3}=\frac{1}{464}+\frac{1}{99100}+\frac{1}{10{,}30\times10^{6}}\;\Rightarrow\;R_{par}=" + n(P, 1).replace(",", "{,}") + r"\ \Omega", "par")
    D.fig("fd", a("f_dirnc.jpg"), "Dirençlerin ayrı ayrı ölçümü: $R_1 = 464\\ \\Omega$, $R_2 = 99{,}1\\ \\mathrm{k\\Omega}$, $R_3 = 10{,}30\\ \\mathrm{M\\Omega}$.", 15.5)
    D.fig("fsp", a("f_serpar.jpg"), "Seri bağlantının ($10{,}45\\ \\mathrm{M\\Omega}$) ve paralel bağlantının ($0{,}46\\ \\mathrm{k\\Omega}$) doğrudan ölçümü.", 12.0)
    rows = [["$R_1$", "464 Ω"], ["$R_2$", "99,1 kΩ"], ["$R_3$", "10,30 MΩ"], ["$R_1+R_2+R_3$ (hesaplanan)", n(S / 1e6, 4) + " MΩ"],
            ["Seri bağlantının doğrudan ölçümü", "10,45 MΩ"], ["Fark", pc(pct(Sd, S))]]
    D.tab("t1", ["Büyüklük", "Değer"], rows, "Seri bağlantı ölçümleri (föy Tablo 1)", [8.5, 4.5])
    rows = [["$R_1 \\parallel R_2 \\parallel R_3$ (hesaplanan)", n(P, 1) + " Ω"], ["Paralel bağlantının doğrudan ölçümü", "0,46 kΩ (460 Ω)"], ["Fark", pc(pct(Pd, P))]]
    D.tab("t2", ["Büyüklük", "Değer"], rows, "Paralel bağlantı ölçümleri (föy Tablo 2)", [8.5, 4.5])
    D.p("**Sonuç ve yorum.** Toplam seri direnç, ayrı ayrı ölçümlerin toplamıyla %0,48 farkla, paralel bağlantı ise %0,39 farkla örtüşmüştür. Bu farklar, multimetrenin kademesinin son basamağının duyarlığı (10 MΩ’luk ölçümde son basamak 10 kΩ, yani yaklaşık %0,1; 0,46 kΩ’luk okumada son basamak 10 Ω, yani yaklaşık %2) ve devre tahtasındaki kontak direnciyle açıklanabilecek mertebededir. Paralel okumada 460 Ω ile 461,8 Ω farkının ekranın tek basamağından küçük olduğuna dikkat edilmelidir. Paralel eşdeğerin en küçük dirençten (464 Ω) bile küçük çıkması bir hata değil, paralel bağlantının kuralıdır: paralel eklenen her yol iletkenliği artırır. Bu sonuçta paralel eşdeğeri esas olarak 470 Ω’luk dirençle belirlenmiştir; 100 kΩ ve 10 MΩ’luk dirençler eşdeğeri sırasıyla yalnızca %0,5 ve %0,005 kadar etkilemiştir. Aynı nedenle seri eşdeğeri esas olarak 10 MΩ’luk direnç belirlemiştir.", align="j")

    # ---- 2
    D.h(2, "Gerilim Bölücü Devresi")
    D.h(3, "Devre ve Devre Tahtası Yerleşimi")
    D.p("Föydeki Şekil 1’deki devre, $V_S = 15$ V’luk kaynağa seri bağlanmış iki eşit dirençten ($R$) oluşur; çıkış $V_O$ alt dirençten alınır. Devre tahtası yerleşimi [[f:bbd]]’de gösterilmiştir. Aynı yerleşim üç direnç değeri için de ($R = 470\\ \\Omega,\\ 100\\ \\mathrm{k\\Omega},\\ 10\\ \\mathrm{M\\Omega}$) yalnızca dirençler değiştirilerek kullanılmıştır.", align="j")
    D.fig("bbd", a("bb_bol.png"), "Gerilim bölücü devrenin devre tahtası yerleşimi. $V_O$ düğümünden multimetre ve osiloskop ayrı ayrı ölçüm yapar.", 14.0)
    D.h(3, "Kuramsal Hesap")
    D.p("İki eşit direnç ideal bir bölücü oluşturduğundan beklenen çıkış gerilimi direnç değerinden bağımsızdır:", align="j", keep=True)
    D.eq(r"V_O=V_S\,\frac{R}{R+R}=\frac{15\ \mathrm{V}}{2}=7{,}5\ \mathrm{V}", "div")
    D.p("Ancak ölçü aleti $V_O$ düğümüne bağlanınca alt dirence paralel bir $R_{iç}$ iç direnci eklenir. Alt direncin yerine paralel eşdeğer $R_p = R R_{iç}/(R+R_{iç})$ geçer ve çıkış şuna iner:", align="j", keep=True)
    D.eq(r"V_O=V_S\,\frac{R_p}{R+R_p},\qquad R_p=\frac{R\,R_{ic}}{R+R_{ic}}", "load")
    D.p("Multimetrenin iç direnci üretici verisine göre yaklaşık $10\\ \\mathrm{M\\Omega}$, osiloskopun (1× kablo) giriş direnci ise yaklaşık $1\\ \\mathrm{M\\Omega}$’dur; bu değerler katalog bilgisidir ve kullanılan aletlerin kılavuzundan ayrıca doğrulanmalıdır. [[e:load]] ile hesaplanan yüklü değerler şunlardır:", align="j")
    rows = []
    for R in (470, 100e3, 10e6):
        rows.append([("%s" % {470: "470 Ω", 100e3: "100 kΩ", 10e6: "10 MΩ"}[R]), "7,500", n(loaded(R, 10e6), 3), n(loaded(R, 1e6), 3)])
    D.tab("t3k", ["R", "İdeal $V_O$ (V)", "Multimetre yüklü (10 MΩ)", "Osiloskop yüklü (1 MΩ)"], rows, "Ölçü aletinin iç direncinin kuramsal etkisi ($V_S = 15$ V, iki eşit direnç)", [2.5, 3.2, 4.2, 4.2])
    D.h(3, "Ölçümler")
    D.fig("fdmm", a("f_dmm.jpg"), "Multimetre okumaları: 7,4 V ($470\\ \\Omega$ ve $100\\ \\mathrm{k\\Omega}$ satırları için 7,4 V yazılmıştır), 6,5 V ve 0,9 V (üçüncü okumanın hangi duruma ait olduğu Sorular kısmında tartışılmıştır).", 15.5)
    D.fig("fosc", a("f_osc.jpg"), "Osiloskop (Tektronix TBS 1022) ölçümleri: soldaki ve ortadaki ekranlar DA gerilim (7,40 V ve 7,30 V RMS), sağdaki 50 Hz’lik sinüs görünümüdür (en küçük −12,0 V, en büyük 9,40 V, tepeden tepeye 21,4 V).", 15.5)
    rows = [["470 Ω", "7,5", "7,4", "7,40 (RMS 7,40; tepeden tepeye 0,2 V)"],
            ["100 kΩ", "7,5", "7,4", "7,30 (RMS 7,30; tepeden tepeye 0,2 V)"],
            ["10 MΩ", "7,5", "6,5", "DA değer okunamadı: 50 Hz, 21,4 V tepeden tepeye parazit"]]
    D.tab("t3", ["R", "Beklenen $V_O$ (V)", "Multimetre (V)", "Osiloskop (V)"], rows, "Gerilim bölücü ölçümleri (föy Tablo 3). Satır eşleştirmesi osiloskop ekranlarının saatlerinden ve föydeki el yazısından çıkarılmıştır (EK-1).", [2.4, 3.2, 3.0, 6.3])
    D.h(3, "Sorular")
    D.p("**Soru 1: Teorik ve ölçülen $V_O$ arasında fark gözlendi mi? Nedenleri nelerdir?**", align="j", keep=True)
    D.p("Fark vardır ve direnç büyüdükçe artmıştır. $470\\ \\Omega$ ve $100\\ \\mathrm{k\\Omega}$ için 7,5 V’a karşı 7,4 V okunmuştur (%1,3 aşağıda). Bu fark iki nedenle açıklanır: (a) iki direncin birbirine tam eşit olmaması: ölçülen $R_1 = 464\\ \\Omega$ ve $R_2 = 99{,}1\\ \\mathrm{k\\Omega}$ değerleri nominalden %1 mertebesinde sapmıştır ve bölücü oranı bunlara duyarlıdır; (b) multimetrenin iç direncinin alt dirence paralel girmesi: $100\\ \\mathrm{k\\Omega}$ için [[e:load]] 7,463 V verir (bu 0,05 V’luk yük etkisi %0,5’e denk gelir). $10\\ \\mathrm{M\\Omega}$ satırında fark çok büyüktür: 7,5 V yerine 6,5 V okunmuştur. Yüklenme hesabı bu satırda $\\approx 5{,}0$ V bekletir ($R_p \\approx 5{,}08\\ \\mathrm{M\\Omega}$), çünkü iç direnç devre direncine eşit mertebededir; ancak okunan 6,5 V bu değerin de üzerindedir. Bu okumayı kuramsal hesapla bağdaştıramadım: $R_{üst} = R_{alt} = 10{,}30\\ \\mathrm{M\\Omega}$ ve $V_S = 15$ V alınırsa 6,5 V okumak için aletin iç direncinin yaklaşık $33\\ \\mathrm{M\\Omega}$ olması gerekir; bu katalog değerinin ($10\\ \\mathrm{M\\Omega}$) çok üzerindedir. Olası nedenler: alt ve üst dirençlerin eşit olmaması (yalnızca $R_3 = 10{,}30\\ \\mathrm{M\\Omega}$ ölçülmüş, iki 10 MΩ direncin ikisi ayrı ayrı ölçülmemiştir), kaynak geriliminin 15 V olmaması veya bu çok yüksek empedanslı düğümde aletin okumasının dalgalanması (aşağıdaki Soru 2’ye bakınız). Bu nedenle 10 MΩ satırı kesin bir sayısal sonuç değil, “yük etkisi büyüktür ve ölçüm kararsızdır” sonucu olarak yorumlanmalıdır. Üçüncü multimetre fotoğrafındaki 0,9 V okumasının hangi bağlantıya ait olduğu belgelerden anlaşılamamıştır (fotoğraf, föyde 7,4 V ve 6,5 V yazıldıktan sonra çekilmiştir); bu yüzden tabloya alınmamış, EK-1’de ayrı satır olarak bırakılmıştır.", align="j")
    D.p("**Soru 2: Multimetre ve osiloskop aynı $V_O$ noktasında farklı değer gösterdi mi? Neden?**", align="j", keep=True)
    D.p("$470\\ \\Omega$ satırında iki alet de 7,40 V göstermiştir; $100\\ \\mathrm{k\\Omega}$ satırında multimetre 7,4 V, osiloskop 7,30 V göstermiştir. Osiloskopun düşük okuması iç direncinin daha küçük olmasıyla uyumludur: $1\\ \\mathrm{M\\Omega}$ iç dirençle [[e:load]] 7,15 V; $10\\ \\mathrm{M\\Omega}$ ile 7,46 V verir; okunan 7,30 V ikisinin arasındadır (okuma ekranda 0,1 V basamaklıdır ve DA sinyal üzerinde 0,2 V tepeden tepeye gürültü bulunmaktadır, bu yüzden bu uyum nicel bir ispat sayılmamalıdır). $10\\ \\mathrm{M\\Omega}$ satırında osiloskop ekranında DA değer yerine 49,998 Hz’lik, 21,4 V tepeden tepeye bir sinüs görülmüştür. Bu, şebekenin (50 Hz) yüksek empedanslı düğüme kapasitif olarak indüklediği parazit gerilimdir: kaynak direnci ne kadar büyükse aynı kaçak akım o kadar büyük gerilim doğurur. Aletin kendi ölçüm duyarlığı ise sorun değildir; sorun kaynak direncinin büyüklüğüdür. Multimetre ise bu gürültüyü ortalayarak (DA kademesinde yavaş örnekleme) tek bir sayı gösterir ve bu yüzden iki aletin bu satırdaki “farkı” gerçekte iki ayrı olgunun farkıdır: biri ortalama, diğeri anlık değer gösterir.", align="j")
    D.p("**Soru 3: İç dirençler karşılaştırıldığında, iç direncin devre direncine göre büyüklüğü sonucu nasıl etkiler?**", align="j", keep=True)
    D.p("Ölçü aleti devreye paralel girdiğinden, ölçülen düğümün direnci $R$’den $R\\parallel R_{iç}$’ye iner. Bağıl yük hatası yaklaşık $R/R_{iç}$ ile orantılıdır: $R_{iç} \\gg R$ ise hata ihmal edilebilir. Dört satırlık bir özet yeterlidir: multimetre ($10\\ \\mathrm{M\\Omega}$) için $R = 470\\ \\Omega$’da $R/R_{iç} = 4{,}7\\times10^{-5}$ (hata yok), $R = 100\\ \\mathrm{k\\Omega}$’da $10^{-2}$ (yaklaşık %0,5 çıkış hatası), $R = 10\\ \\mathrm{M\\Omega}$’da $1$ (çıkış yaklaşık %33 düşer). Osiloskop ($1\\ \\mathrm{M\\Omega}$) için bu oranlar sırasıyla $4{,}7\\times10^{-4}$, $0{,}1$ ve $10$’dur. Kural şudur: ölçü aleti, ölçülen düğümün Thevenin direncinin en az 100 katı kadar iç dirence sahip olmalıdır. Bunun sağlanamadığı durumda ya kuramsal yüklü değer ([[e:load]]) hesaplanmalı ya da yüksek empedanslı (10 MΩ ve üzeri) bir giriş kullanılmalıdır.", align="j")

    # ---- 3
    D.h(2, "Wheatstone Köprüsü")
    D.h(3, "Devre ve Devre Tahtası Yerleşimi")
    D.p("Föydeki Şekil 2’deki köprü $V_S = +15$ V ile beslenmiş, $R_1 = R_2 = 470\\ \\Omega$ (renk kodu), $R_3$ yerine potansiyometre ve $R_x$ yerine laboratuvar asistanının verdiği bilinmeyen direnç bağlanmıştır. [[f:bbw]]’de devre tahtası yerleşimi gösterilmiştir. $V_B$, $R_1$–$R_3$ ortak düğümü ile $R_2$–$R_x$ ortak düğümü arasındaki gerilimdir.", align="j")
    D.fig("bbw", a("bb_whe.png"), "Wheatstone köprüsünün devre tahtası yerleşimi. Potansiyometre $R_3$ yerine, bilinmeyen direnç $R_x$ yerine bağlanmıştır; $V_B$ sarı ve mavi uçlar arasından ölçülür.", 14.0)
    D.h(3, "Kuramsal Hesap")
    D.p("Sol kolun orta düğümü $V_L = V_S\\,R_3/(R_1+R_3)$, sağ kolun orta düğümü $V_R = V_S\\,R_x/(R_2+R_x)$ gerilimindedir. Köprü dengedeyken $V_B = V_L - V_R = 0$ olur ve bu koşul kaynak geriliminden bağımsızdır:", align="j", keep=True)
    D.eq(r"V_B=V_S\left(\frac{R_3}{R_1+R_3}-\frac{R_x}{R_2+R_x}\right)=0\;\Rightarrow\;R_1R_x=R_2R_3\;\Rightarrow\;R_x=\frac{R_2R_3}{R_1}", "bridge")
    D.p("Dengenin kaynak değerinden bağımsız olması köprünün asıl gücüdür: sonuç $V_S$’in dalgalanmasından etkilenmez ve yalnızca üç direncin oranına dayanır. Ölçülen değerlerle ($R_1 = 464\\ \\Omega$, $R_2 = 456\\ \\Omega$, denge anındaki $R_3 = 3{,}22\\ \\mathrm{k\\Omega}$) bilinmeyen direnç:", align="j", keep=True)
    D.eq(r"R_x=\frac{456\ \Omega\cdot3220\ \Omega}{464\ \Omega}=" + n(rx, 1).replace(",", "{,}") + r"\ \Omega", "rx")
    D.h(3, "Ölçümler")
    D.fig("fwh", a("f_whe.jpg"), "Üst sıra: $R_1 = 456\\ \\Omega$ ve $R_2 = 464\\ \\Omega$ okumaları (fotoğraf sırasıyla), $R_3$ (devreden çıkarılmış potansiyometre) $= 3{,}22\\ \\mathrm{k\\Omega}$. Alt sıra: denge anında $V_B = 0{,}00$ V, $R_x$’in doğrudan ölçümü $3{,}26\\ \\mathrm{k\\Omega}$ ve potansiyometrenin devre tahtasındaki hâli.", 15.5)
    D.p("Föydeki el yazısı notlarda $R_1 = 464\\ \\Omega$, $R_2 = 456\\ \\Omega$ yazılıdır; hesap bu atamayla yapılmıştır. İki ölçüm fotoğrafı bu iki sayıyı ters sırayla (456, sonra 464) gösterdiğinden, hangi direncin hangisi olduğu fotoğraflardan ayrıca doğrulanamamıştır; ters atamanın etkisi aşağıda verilmiştir.", align="j")
    rows = [["Renk kodu (3,3 kΩ ± %5)", "3.300", "0"],
            ["Multimetre ölçümü", "3.260", pc(pct(rxd, rc))],
            ["Wheatstone köprüsü ölçümü ($R_x = R_2R_3/R_1$)", n(rx, 1), pc(pct(rx, rc))]]
    D.tab("t4", ["Yöntem", "Direnç değeri (Ω)", "Renk kodundan fark (%)"], rows, "$R_x$ direncinin değeri ve karşılaştırılması (föy Tablo 4)", [7.4, 3.6, 3.8])
    D.p("Renk kodu ± %5 toleransla $3135$–$3465\\ \\Omega$ aralığını verir. Her iki ölçüm de bu aralıktadır.", align="j")
    D.h(3, "Yorum")
    D.p(("**Köprü ile multimetre aynı mıdır?** Hayır: köprü yöntemiyle %s Ω, multimetreyle 3260 Ω bulunmuştur; fark %s’dir. Bu fark, köprü ölçümünün belirsizliğinden büyüktür: $V_B$ ekranda 0,00 V okunduğundan denge hatası en çok ±5 mV’tur ve bu $R_3$’te yaklaşık %%0,3 sapmaya karşılık gelir; $R_1$, $R_2$ ve $R_3$ okumalarının son basamakları toplam %%0,5 mertebesinde bir belirsizlik ekler. Kalan farkın olası nedenleri şunlardır: (a) devre tahtasındaki kontak ve jumper dirençleri ($R_3$ devreden çıkarılıp ölçüldüğünde bu dirençler ölçüme girmez, oysa köprü dengelenirken kolun içindedirler; bir kolda yaklaşık 100 Ω fazladan direnç %%3’lük farkı doğurur), (b) potansiyometre sürgüsünün temas direnci, (c) $R_1$ ve $R_2$’nin hangisinin hangisi olduğunun doğrulanamaması. (c) maddesi önemlidir: $R_1 = 456\\ \\Omega$ ve $R_2 = 464\\ \\Omega$ alınırsa $R_x = 464\\cdot3220/456 = %s\\ \\Omega$ bulunur ve bu değer multimetreden yalnızca %s uzaktadır. Hangi atamanın doğru olduğu devre tahtasına bakılarak kesinleştirilmelidir. Föyün Tablo 4’ünde Wheatstone satırına el ile 3,22 kΩ yazılmıştır; bu sayı $R_3$’ün kendisidir, $R_x$ değildir ($R_x = R_2R_3/R_1$ olduğundan $R_1 \\approx R_2$ ise yaklaşık $R_3$ çıkar, ama eşit değildir); bu raporda formülden hesaplanan değer kullanılmıştır.") % (n(rx, 0), pc(pct(rx, rxd)), n(rxs, 0), pc(pct(rxs, rxd))), align="j")
    D.p("**Ölçümler renk koduyla uyumlu mudur?** Evet: multimetre %s, köprü %s sapmıştır ve ikisi de %%5 tolerans aralığının içindedir. Renk kodunun bir hedef değer, ölçümün gerçek değer olduğu bu örnekte de görülmektedir." % (pc(pct(rxd, rc)), pc(pct(rx, rc))), align="j")

    # ---- 4
    D.h(2, "Dijital-Analog Çevirici (DAC)")
    D.h(3, "Devre ve Devre Tahtası Yerleşimi")
    D.p("Föydeki Şekil 3’teki 3 bitlik R-2R merdiven DAC’ında her bit, $2\\ \\mathrm{k\\Omega}$’luk bir giriş direnciyle merdivene bağlanır; merdiven iki adet $1\\ \\mathrm{k\\Omega}$’luk seri direnç ile $2\\ \\mathrm{k\\Omega}$’luk bir sonlandırma direncinden, çıkış ise $R_L = 1\\ \\mathrm{k\\Omega}$ yük direncinden oluşur. Mantık “1” için giriş 16 V’a, “0” için toprağa bağlanır. [[f:bbc]]’de devre tahtası yerleşimi gösterilmiştir (en üstteki bit MSB, ilk giriştir).", align="j")
    D.fig("bbc", a("bb_dac.png"), "3 bitlik R-2R DAC’ın devre tahtası yerleşimi. Üç giriş ucu (MSB, orta bit, LSB) 16 V veya toprağa bağlanır; $V_O$ ve $R_L$ ilk düğümdedir.", 14.0)
    D.h(3, "Kuramsal Hesap")
    D.p("Devre doğrusal olduğundan çıkış, her bitin tek başına yarattığı çıkışların toplamıdır (süperpozisyon). Düğümler, giriş dirençlerinin merdivenle birleştiği $A$ ($V_O$ düğümü), $B$ ve $C$ olmak üzere üç tanedir; düğüm denklemleri iletkenlik matrisiyle şöyle yazılır ($G_i = 1/2\\ \\mathrm{k\\Omega}$, $b_k \\in \\{0,1\\}$):", align="j", keep=True)
    D.eq(r"\begin{bmatrix}G_i+G_a+G_L&-G_a&0\\-G_a&G_i+G_a+G_b&-G_b\\0&-G_b&G_i+G_b+G_t\end{bmatrix}\begin{bmatrix}V_A\\V_B\\V_C\end{bmatrix}=G_i\,V_{\mathrm{mantık}}\begin{bmatrix}b_2\\b_1\\b_0\end{bmatrix}", "dacm")
    D.p("Bu denklem çözüldüğünde (Python ile sayısal çözülmüş ve elle de doğrulanmıştır) her bitin $V_O$’ya katkısının, bit ağırlıklarıyla orantılı olduğu görülür: MSB için 4 V, orta bit için 2 V, LSB için 1 V. Yani devre $V_O = (4b_2+2b_1+b_0)\\times 1\\ \\mathrm{V}$ dönüşümünü yapar. Giriş $100$, $011$ ve $111$ için kuramsal çıkışlar sırasıyla $4$ V, $3$ V ve $7$ V’tur ($4+2+1 = 7$; $100$ ve $011$’in toplamı da $7$ V’tur).", align="j")
    D.h(3, "Ölçümler ve Karşılaştırma")
    D.fig("fdac", a("f_dac.jpg"), "DAC çıkış gerilimleri: 100 için $4{,}09$ V, 011 için $3{,}27$ V, 111 için $7{,}34$ V.", 15.5)
    rows = []
    for nm, k, m in (("100", 4.0, 4.09), ("011", 3.0, 3.27), ("111", 7.0, 7.34)):
        rows.append([nm, n(k, 3), n(m, 2), n(m - k, 2), pc(pct(m, k))])
    D.tab("t5", ["Giriş", "Kuramsal $V_O$ (V)", "Ölçülen $V_O$ (V)", "Mutlak fark (V)", "Fark (%)"], rows, "DAC çıkış gerilimleri: kuramsal ve ölçülen", [2.0, 3.4, 3.4, 3.0, 2.4])
    D.h(3, "Yorum")
    D.p("Ölçülen değerler kuramsal değerlerin hepsinin üzerindedir (%2,3, %9,0 ve %4,9). Üç ölçümün birbirine tutarlı olduğu görülmektedir: $100$ ve $011$ okumalarının toplamı $4{,}09 + 3{,}27 = 7{,}36$ V’tur ve $111$ için okunan $7{,}34$ V’la %0,3 farklıdır; yani devre doğrusal davranmıştır, sorun ölçüden değil devrenin bit ağırlıklarındadır. Ağırlıkların oranı $4{,}09/3{,}27 = 1{,}25$’tir, kuramsal oran ise $4/3 = 1{,}33$’tür: bir bitin ağırlığı diğerine göre kaymıştır. Sapmanın nedenleri şunlar olabilir: (a) direnç toleransları: yedi direnç ± %5 toleransla rastgele seçildiğinde (20 000 deneme ile hesaplanmıştır) çıkışlar $100$ için $3{,}81$–$4{,}20$ V, $011$ için $2{,}87$–$3{,}13$ V ve $111$ için $6{,}76$–$7{,}24$ V aralığında kalır (%95 olasılıkla). Ölçülen $4{,}09$ V bu aralıktadır; $3{,}27$ V ve $7{,}34$ V ise dışındadır, yani tolerans tek başına açıklamak için yetersiz kalmaktadır; (b) “16 V” giriş geriliminin gerçek değerinin 16 V olmaması: gerilim 16,3 V olsaydı çıkışlar %1,9 artardı, fakat oran bozulmazdı; (c) $2\\ \\mathrm{k\\Omega}$ ve benzeri değerler tek direnç yerine seri-paralel bağlamayla elde edildiyse her bağlantı kontak direnci ekler (föy bu bağlamaya izin vermektedir) ve bu, doğrudan bit ağırlıklarını bozar; (d) kaynağın yüklenince gerilimini koruyamaması (iç direnç). Bu raporda direnç değerleri ayrı ayrı ölçülmediği için hangi nedenin baskın olduğu söylenemez; hangi dirençlerin kullanıldığı ve ayrı ayrı değerleri ölçülmüş olsaydı ($V_O$ formülüne konarak) sapmanın kaynağı kesin olarak bulunabilirdi.", align="j")

    # ================= SONUÇLAR
    D.h(1, "Sonuçlar")
    D.p("**Genel değerlendirme.** Seri ve paralel bağlantı kuralları ölçümle doğrulanmıştır: seri ölçüm toplamdan %%0,48, paralel ölçüm hesaptan %%0,39 farklıdır; her iki fark ekranın son basamağı ve kontak direnci düzeyindedir. Gerilim bölücüde ölçü aletinin etkisi görülmüştür: $470\\ \\Omega$ ve $100\\ \\mathrm{k\\Omega}$’da multimetre 7,4 V okumuş (beklenen 7,5 V, %%1,3 fark), $10\\ \\mathrm{M\\Omega}$’da yük etkisi ve ortam gürültüsü (50 Hz, 21,4 V tepeden tepeye) ölçümü kararsız kılmıştır. Wheatstone köprüsünde bilinmeyen direnç $%s\\ \\Omega$ bulunmuş ve multimetre ölçümüyle ($3260\\ \\Omega$) %s farkla karşılaştırılmıştır; ikisi de renk kodunun ($3{,}3\\ \\mathrm{k\\Omega}$ ± %%5) tolerans aralığındadır. DAC çıkışları beklenenin %%2,3–%%9 üzerinde ölçülmüştür." % (n(rx, 0), pc(pct(rx, rxd))), align="j")
    D.p("**Açık kalan hususlar.** (i) 10 MΩ’luk bölücü satırındaki 6,5 V okuması kuramsal yük hesabıyla (≈ 5 V) bağdaşmamaktadır ve bu raporda açıklanamamıştır; (ii) üçüncü multimetre fotoğrafındaki 0,9 V’un hangi bağlantıya ait olduğu belirsizdir; (iii) Wheatstone hesabında $R_1$ ve $R_2$ atamasının doğrulanması gerekir (iki atama %3 farklı sonuç verir); (iv) DAC’ta tolerans tek başına sapmayı açıklamamaktadır ve direnç değerleri tek tek ölçülmemiştir.", align="j")
    D.p("**Kazanılan beceriler.** Dirençlerin seri-paralel hesabı ve ölçümü; ölçü aletinin yük etkisinin hesaplanması; osiloskop ve multimetrenin birlikte kullanımı ve 50 Hz parazitin tanınması; köprü yöntemi; DAC ağırlıklarının süperpozisyonla hesabı; devre tahtası yerleşiminin planlanması ve ölçümlerin kuramsal değerle yüzde farkla karşılaştırılması.", align="j")

    D.h(1, "Kaynaklar")
    refs_block(D, ["Nilsson, J. W., & Riedel, S. A. (2015). *Electric circuits* (10th ed.). Boston: Pearson.",
                   "Alexander, C. K., & Sadiku, M. N. O. (2017). *Fundamentals of electric circuits* (6th ed.). New York: McGraw-Hill Education.",
                   "Hayt, W. H., Kemmerly, J. E., & Durbin, S. M. (2012). *Engineering circuit analysis* (8th ed.). New York: McGraw-Hill.",
                   "Horowitz, P., & Hill, W. (2015). *The art of electronics* (3rd ed.). New York: Cambridge University Press.",
                   "TOBB Ekonomi ve Teknoloji Üniversitesi. (2026). *ELE 201 L – Devre Analizi I Laboratuvarı, Deney 1 Föyü*. Ankara: TOBB ETÜ, Elektrik – Elektronik Mühendisliği Bölümü."])

    D.h(1, "Ekler")
    D.h(3, "EK-1: Fotoğraf Okuma Çizelgesi ve Eşleştirme Gerekçesi")
    D.p("Aşağıda her fotoğrafın (yükleme sırasıyla numaralanmıştır) gösterdiği okuma ve rapordaki karşılığı verilmiştir. Gerilim bölücü satırlarının eşleştirilmesi fotoğrafların içeriğinden ve osiloskop saatlerinden çıkarılmıştır: osiloskop ekranları 08:20 (7,40 V), 08:23 (7,30 V RMS) ve 08:25 (50 Hz parazit) saatlerini göstermekte, föydeki el yazısında ise multimetre sütununda 7,4 V ve 6,5 V, osiloskop sütununda 7,40 V ve 7,40 V yazılmaktadır. Bu nedenle eşleştirme bir çıkarımdır; asıl kayıt tutan kişinin doğrulamasına açıktır.", align="j")
    rows = [["1", "464 Ω", "$R_1$ ayrı ölçüm"], ["2", "99,1 kΩ", "$R_2$ ayrı ölçüm"], ["3", "0,46 kΩ", "Paralel bağlantı"], ["4", "10,45 MΩ", "Seri bağlantı"], ["5", "10,30 MΩ", "$R_3$ ayrı ölçüm"],
            ["6", "7,4 V", "Multimetre, bölücü"], ["7", "7,40 V (08:20)", "Osiloskop, bölücü"], ["8", "6,5 V", "Multimetre, bölücü (10 MΩ)"], ["9", "50 Hz, 21,4 V t.t.", "Osiloskop (08:25), 10 MΩ"],
            ["10", "0,9 V", "Multimetre; bağlantısı belirsiz"], ["11", "7,30 V RMS (08:23)", "Osiloskop, bölücü"], ["12", "3,26 kΩ", "Potansiyometre/Rx ölçümü sahnesi"], ["13", "0,00 V", "Köprü $V_B$ (denge)"],
            ["14", "3,22 kΩ", "$R_3$ (potansiyometre, devreden çıkarılmış)"], ["15", "3,26 kΩ", "$R_x$ doğrudan"], ["16", "456 Ω", "Köprü direnç ölçümü"], ["17", "7,34 V", "DAC 111"], ["18", "464 Ω", "Köprü direnç ölçümü"],
            ["19", "4,09 V", "DAC 100"], ["20", "3,27 V", "DAC 011"]]
    D.tab("tek", ["Fotoğraf", "Okuma", "Karşılığı"], rows, "Fotoğraf okuma çizelgesi", [2.2, 4.4, 7.4], size=9)
    D.p("Tablo 3’te 100 kΩ satırı için multimetre değeri olarak 7,4 V yazılmıştır: föyde 7,4 V ve 6,5 V olmak üzere yalnızca iki multimetre değeri bulunduğundan ve 100 kΩ için kuramsal yüklü değer (7,46 V) ile 7,4 V’un uyumlu olmasından dolayı. Bu da bir çıkarımdır; 470 Ω ve 100 kΩ satırlarının ikisinde de 7,4 V okunmuş olması mümkündür.", align="j")
    return D

if __name__ == "__main__":
    D = build(); f = os.path.join(OUT, "ELE201L_Deney1_Laboratuvar_Raporu.docx"); D.save(f)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", OUT, f], capture_output=True, timeout=300); print("ok")
