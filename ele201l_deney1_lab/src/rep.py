import subprocess, math
from common import *
from docbuilder import Doc

def build():
    D = Doc("tr")
    D.title_block([("TOBB Ekonomi ve Teknoloji Üniversitesi", 13, True), ("Elektrik – Elektronik Mühendisliği Bölümü", 12, False),
                   ("ELE 201 L – Devre Analizi I Laboratuvarı", 14, True), ("Deney 1 – Laboratuvar Raporu", 14, True), ("Güz 2026", 12, False)],
                  [("Ad Soyad", ""), ("Numara", ""), ("Tarih", ""), ("Grup Arkadaşı", "Işıl Fidancan, Bahar Işıklar")])

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
    D.p("Bu deneyde dört şey yaptık: (i) dirençleri seri ve paralel bağlayıp eşdeğer direnci ölçtük, (ii) gerilim bölücü devrenin çıkışını hem multimetre hem osiloskopla ölçüp ölçü aletinin devreyi nasıl etkilediğine baktık, (iii) Wheatstone köprüsüyle bilinmeyen bir direnci ölçtük ve (iv) 3 bitlik R-2R merdiven tipi sayısal-analog çevirici (DAC) devresinin çıkış gerilimini ölçtük. Her bölümde önce beklenen değeri hesapladık, sonra ölçtüğümüz değerle karşılaştırıp farkın nedenini yorumladık.", align="j")
    D.h(2, "Deneyin Faydaları")
    D.p("Deney sonunda şunları gördük. Direncin üzerindeki renk kodu bir hedef değerdir; gerçek değer toleransı kadar bu hedeften sapar. Ölçü aleti devreye paralel girdiği için devreyi değiştirir ve bu etki, devre direnci aletin iç direncine yaklaştıkça büyür. Köprü yönteminde sonuç bir alet okumasına değil bir denge şartına dayandığı için hassas olabilir. Sayısal bir kod, direnç ağıyla analog gerilime çevrilebilir; bu çevirinin doğruluğu direnç toleranslarına bağlıdır.", align="j")

    # ================= ÖLÇÜMLER
    D.h(1, "Ölçümler")
    D.p("Bütün ölçümleri laboratuvarda UNI-T UT33D+ el tipi multimetre ve Tektronix TBS 1022 osiloskopla yaptık; değerleri aletlerin ekranından okuyup kaydettik. Beklenen (kuramsal) değerleri elle hesapladık. Kuramsal değer $x_k$ ve ölçülen değer $x_o$ için farkı şöyle tanımladık:", align="j")
    D.eq(r"\text{Fark}\,(\%)=\frac{x_o-x_k}{x_k}\times 100", "fark")
    D.p("Fark hesaplarında tablolardaki ölçülen değerler kullanılmıştır; ekrandaki son basamağın duyarlığı her yerde ayrıca belirtilmiştir.", align="j")

    # ---- 1
    D.h(2, "Dirençlerin Seri ve Paralel Bağlantıları")
    D.h(3, "Devre Tahtası Yerleşimi")
    D.p("Dirençlerin renk kodundaki değerleri $R_1 = 470\\ \\Omega$, $R_2 = 100\\ \\mathrm{k\\Omega}$ ve $R_3 = 10\\ \\mathrm{M\\Omega}$’dur; gerçek değerlerini aşağıda ölçtük. [[f:bbs]]’te dirençlerin seri, [[f:bbp]]’te paralel bağlanmış hâlinin devre tahtası yerleşimi görülmektedir. Seri bağlantıda dirençler uç uca takılır; aradaki ortak sütun (a–e delikleri iç bağlıdır) bağlantı noktasıdır. Paralel bağlantıda üç direncin birer ucu aynı sütuna, diğer uçları başka bir ortak sütuna takılır.", align="j")
    D.fig("bbs", a("bb_seri.png"), "Dirençlerin seri bağlantısı (devre tahtası yerleşimi). Multimetre Ω kademesinde iki serbest uç arasına bağlanır.", 14.0)
    D.fig("bbp", a("bb_par.png"), "Dirençlerin paralel bağlantısı (devre tahtası yerleşimi).", 14.0)
    D.h(3, "Ölçümler ve Hesaplar")
    D.p("Dirençleri önce tek tek ölçtük ([[f:fd]]), sonra seri bağlayıp toplam direnci, ardından paralel bağlayıp eşdeğer direnci ölçtük ([[f:fsp]]). Seri elemanlardan aynı akım geçtiği ve gerilimler toplandığı için seri eşdeğer dirençlerin toplamıdır:", align="j", keep=True)
    D.eq(r"R_{seri}=R_1+R_2+R_3=464\ \Omega+99{,}1\ \mathrm{k\Omega}+10{,}30\ \mathrm{M\Omega}=" + (n(S / 1e6, 4)).replace(",", "{,}") + r"\ \mathrm{M\Omega}", "seri")
    D.p("Paralel bağlantıda her dirence aynı gerilim uygulanır ve akımlar toplanır; bu yüzden iletkenlikler toplanır:", align="j", keep=True)
    D.eq(r"\frac{1}{R_{par}}=\frac{1}{R_1}+\frac{1}{R_2}+\frac{1}{R_3}=\frac{1}{464}+\frac{1}{99100}+\frac{1}{10{,}30\times10^{6}}\;\Rightarrow\;R_{par}=" + n(P, 1).replace(",", "{,}") + r"\ \Omega", "par")
    D.fig("fd", a("f_dirnc.jpg"), "Dirençlerin ayrı ayrı ölçümü: $R_1 = 464\\ \\Omega$, $R_2 = 99{,}1\\ \\mathrm{k\\Omega}$, $R_3 = 10{,}30\\ \\mathrm{M\\Omega}$.", 15.5)
    D.fig("fsp", a("f_serpar.jpg"), "Seri bağlantının ($10{,}45\\ \\mathrm{M\\Omega}$) ve paralel bağlantının ($0{,}46\\ \\mathrm{k\\Omega}$) doğrudan ölçümü.", 12.0)
    rows = [["$R_1$", "464 Ω"], ["$R_2$", "99,1 kΩ"], ["$R_3$", "10,30 MΩ"], ["$R_1+R_2+R_3$ (hesaplanan)", n(S / 1e6, 4) + " MΩ"],
            ["Seri bağlantının doğrudan ölçümü", "10,45 MΩ"], ["Fark", pc(pct(Sd, S))]]
    D.tab("t1", ["Büyüklük", "Değer"], rows, "Seri bağlantı ölçümleri (föy Tablo 1)", [8.5, 4.5])
    rows = [["$R_1 \\parallel R_2 \\parallel R_3$ (hesaplanan)", n(P, 1) + " Ω"], ["Paralel bağlantının doğrudan ölçümü", "0,46 kΩ (460 Ω)"], ["Fark", pc(pct(Pd, P))]]
    D.tab("t2", ["Büyüklük", "Değer"], rows, "Paralel bağlantı ölçümleri (föy Tablo 2)", [8.5, 4.5])
    D.p("**Sonuç ve yorum.** Seri bağlantının doğrudan ölçümü hesaplanan toplamdan %0,48, paralel bağlantının ölçümü hesaplanandan %0,39 farklı çıktı. İki fark da multimetrenin son basamağı ve devre tahtasındaki kontak direnci mertebesindedir: 10 MΩ’luk ölçümde son basamak 10 kΩ (yaklaşık %0,1), 0,46 kΩ’luk okumada ise 10 Ω’dur (yaklaşık %2); yani paralel okumada 460 Ω ile 461,8 Ω arasındaki fark ekranın tek basamağından küçüktür. Paralel eşdeğerin en küçük dirençten (464 Ω) bile küçük çıkması bir hata değildir: paralel eklenen her yol iletkenliği artırır. Paralel eşdeğeri esas olarak en küçük direnç, seri eşdeğeri ise esas olarak en büyük direnç belirler; 100 kΩ ve 10 MΩ’luk dirençler paralel eşdeğeri sırasıyla yalnızca %0,5 ve %0,005 kadar etkiledi.", align="j")

    # ---- 2
    D.h(2, "Gerilim Bölücü Devresi")
    D.h(3, "Devre ve Devre Tahtası Yerleşimi")
    D.p("Föydeki Şekil 1’deki devreyi kurduk: $V_S = 15$ V’luk kaynağa seri bağlı iki eşit direnç ($R$) vardır ve çıkış $V_O$ alt dirençten alınır. Devre tahtası yerleşimi [[f:bbd]]’de görülmektedir. Aynı devreyi üç direnç değeri için ($R = 470\\ \\Omega,\\ 100\\ \\mathrm{k\\Omega},\\ 10\\ \\mathrm{M\\Omega}$) yalnızca dirençleri değiştirerek kullandık.", align="j")
    D.fig("bbd", a("bb_bol.png"), "Gerilim bölücü devrenin devre tahtası yerleşimi. Güç kaynağı 15 V’a ayarlıdır; $V_O$ düğümünü multimetre ve osiloskop ölçer (iki alet aynı düğüme bağlıdır). Çizimde 470 Ω’luk dirençler gösterilmiştir.", 14.0)
    D.h(3, "Kuramsal Hesap")
    D.p("İki eşit direnç ideal bir bölücü oluşturduğundan beklenen çıkış gerilimi direnç değerinden bağımsızdır:", align="j", keep=True)
    D.eq(r"V_O=V_S\,\frac{R}{R+R}=\frac{15\ \mathrm{V}}{2}=7{,}5\ \mathrm{V}", "div")
    D.p("Ölçü aleti $V_O$ düğümüne bağlanınca alt dirence paralel bir $R_{ic}$ iç direnci girer. Alt direncin yerini $R_p = R R_{ic}/(R+R_{ic})$ alır ve çıkış şuna düşer:", align="j", keep=True)
    D.eq(r"V_O=V_S\,\frac{R_p}{R+R_p},\qquad R_p=\frac{R\,R_{ic}}{R+R_{ic}}", "load")
    D.p("Multimetrenin iç direncinin katalogda yaklaşık $10\\ \\mathrm{M\\Omega}$, osiloskopun (1× uç) giriş direncinin yaklaşık $1\\ \\mathrm{M\\Omega}$ olduğunu biliyoruz (kılavuzdan ayrıca doğrulamadık). Bu değerlerle [[e:load]]’den bulunan yüklü değerler şöyledir:", align="j")
    rows = []
    for R in (470, 100e3, 10e6):
        rows.append([("%s" % {470: "470 Ω", 100e3: "100 kΩ", 10e6: "10 MΩ"}[R]), "7,500", n(loaded(R, 10e6), 3), n(loaded(R, 1e6), 3)])
    D.tab("t3k", ["R", "İdeal $V_O$ (V)", "Multimetre yüklü (10 MΩ)", "Osiloskop yüklü (1 MΩ)"], rows, "Ölçü aletinin iç direncinin kuramsal etkisi ($V_S = 15$ V, iki eşit direnç)", [2.5, 3.2, 4.2, 4.2])
    D.h(3, "Ölçümler")
    D.fig("fdmm", a("f_dmm.jpg"), "Multimetre okumaları (soldan sağa): $470\\ \\Omega$ için 7,4 V; $100\\ \\mathrm{k\\Omega}$ için 6,5 V; $10\\ \\mathrm{M\\Omega}$ için 0,9 V.", 15.5)
    D.fig("fosc", a("f_osc.jpg"), "Osiloskop (Tektronix TBS 1022) ekranları: $470\\ \\Omega$ için 7,40 V; $100\\ \\mathrm{k\\Omega}$ için 7,4 V; $10\\ \\mathrm{M\\Omega}$ için 49,998 Hz’lik sinüs (en küçük −12,0 V, en büyük 9,40 V, tepeden tepeye 21,4 V).", 15.5)
    rows = [["470 Ω", "7,5", "7,4", "7,40"],
            ["100 kΩ", "7,5", "6,5", "7,4"],
            ["10 MΩ", "7,5", "0,9", "9,40 (en büyük değer; sinyal 50 Hz, 21,4 V tepeden tepeye)"]]
    D.tab("t3", ["R", "Beklenen $V_O$ (V)", "Multimetre (V)", "Osiloskop (V)"], rows, "Gerilim bölücü ölçümleri (föy Tablo 3)", [2.4, 3.2, 3.0, 6.3])
    D.h(3, "Sorular")
    D.p("**Soru 1: Teorik ve ölçülen $V_O$ arasında fark gözlendi mi? Nedenleri nelerdir?**", align="j", keep=True)
    D.p("Fark vardır ve direnç büyüdükçe çok büyüdü. $470\\ \\Omega$ satırında multimetre 7,4 V, osiloskop 7,40 V gösterdi (beklenen 7,5 V; %1,3 fark). Bu küçük fark iç dirençten değil, iki direncin tam eşit olmamasından gelir (ölçtüğümüz $R_1 = 464\\ \\Omega$, nominalden %1,3 küçük); bu satırda iç direnç etkisi yoktur. $100\\ \\mathrm{k\\Omega}$ satırında multimetre 6,5 V (%13 düşük), osiloskop 7,4 V (%1,3 düşük) gösterdi; yani iki alet aynı noktada 0,9 V farklı değer verdi. $10\\ \\mathrm{M\\Omega}$ satırında multimetre 0,9 V gösterdi, bu beklenen değerin yalnızca %12’sidir; osiloskopta ise DA değer yerine 50 Hz’lik büyük bir sinüs gördük. Bu farkların nedeni ölçü aletlerinin iç direncinin alt dirence paralel girerek bölücü oranını değiştirmesidir ([[e:load]]). Aletlerin devreye gösterdiği direnci ölçtüğümüz değerlerden hesapladık.", align="j")
    D.p("**Ölçülen değerlerden iç direncin bulunması.** [[e:load]]’i $R_{ic}$ için çözersek ($k = V_O/(V_S - V_O)$ olmak üzere, iki direncin eşit olduğunu kabul ederek $R_p = kR$):", align="j", keep=True)
    D.eq(r"R_{ic}=\frac{R\,R_p}{R-R_p}=\frac{k\,R}{1-k},\qquad k=\frac{V_O}{V_S-V_O}", "ric")
    D.p("Multimetre için $100\\ \\mathrm{k\\Omega}$ satırında ($R = 99{,}1\\ \\mathrm{k\\Omega}$, $V_O = 6{,}5$ V) $k = 6{,}5/8{,}5 = 0{,}765$ ve $R_{ic} \\approx 0{,}32\\ \\mathrm{M\\Omega}$ bulduk (ekranın son basamağı olan ±0,05 V için $0{,}30$–$0{,}34\\ \\mathrm{M\\Omega}$). $10\\ \\mathrm{M\\Omega}$ satırında ($R = 10{,}30\\ \\mathrm{M\\Omega}$, $V_O = 0{,}9$ V) $k = 0{,}9/14{,}1 = 0{,}0638$ ve $R_{ic} \\approx 0{,}70\\ \\mathrm{M\\Omega}$ bulduk ($0{,}66$–$0{,}75\\ \\mathrm{M\\Omega}$). Osiloskop için $100\\ \\mathrm{k\\Omega}$ satırında ($V_O = 7{,}4$ V) $R_{ic} \\approx 3{,}7\\ \\mathrm{M\\Omega}$ bulduk; ekran basamağı yüzünden aralık geniştir ($2{,}4$–$7{,}4\\ \\mathrm{M\\Omega}$).", align="j")
    D.p("**Yorum.** Bulduğumuz sayılara göre multimetre bu ölçümlerde devreye yaklaşık $0{,}3$–$0{,}7\\ \\mathrm{M\\Omega}$’luk bir yük gibi davrandı; bu, katalogdaki $10\\ \\mathrm{M\\Omega}$’dan yaklaşık 15–30 kat küçüktür. İki satırın farklı çıkması (0,32 ve 0,70 $\\mathrm{M\\Omega}$) $10\\ \\mathrm{M\\Omega}$ satırında $R_{ic}$’nin direnç değerlerine (özellikle ölçmediğimiz ikinci dirence) çok duyarlı olmasındandır. Bu küçük iç direncin fiziksel nedenini tam belirleyemedik; bunu kesinleştirmek için aleti bilinen bir dirençle (örneğin $1\\ \\mathrm{M\\Omega}$) bir kaynağa seri bağlayıp [[e:load]]’i ters çözmek gerekir. Osiloskop $100\\ \\mathrm{k\\Omega}$ satırında yalnızca %1,3 düşük okudu; yani giriş direnci multimetreninkinden çok daha büyük göründü (10× uçla $10\\ \\mathrm{M\\Omega}$ için [[e:load]] 7,46 V, 1× uçla $1\\ \\mathrm{M\\Omega}$ için 7,14 V verir; okuduğumuz 7,4 V birinciye yakındır, ancak ucun türünü kaydetmedik).", align="j")
    D.p("**Soru 2: Multimetre ve osiloskop aynı $V_O$ noktasında farklı değer gösterdi mi? Neden?**", align="j", keep=True)
    D.p("Evet, $100\\ \\mathrm{k\\Omega}$ ve $10\\ \\mathrm{M\\Omega}$ satırlarında. Neden, iki aletin devreye farklı iç direnç göstermesidir: alt dirence paralel giren direnç ne kadar küçükse düğüm gerilimi o kadar düşer ([[e:load]]). $100\\ \\mathrm{k\\Omega}$’da iç direnci yüksek alet (osiloskop, 7,4 V) beklenene yakın, iç direnci düşük görünen alet (multimetre, 6,5 V) belirgin biçimde düşük okudu. $10\\ \\mathrm{M\\Omega}$ satırında fark daha da büyüktür: multimetre 0,9 V gösterdi; osiloskopta ise beklenen DA değer yerine, en büyük değeri 9,40 V olan 50 Hz’lik bir sinüs gördük. Bu sinüs, şebekenin yüksek empedanslı düğüme kapasitif olarak kattığı paraziti gösterir: düğümün direnci (bu satırda yaklaşık $5\\ \\mathrm{M\\Omega}$) büyük olunca aynı küçük kaçak akım büyük bir gerilim doğurur. Buradaki 9,40 V bir DA değeri değil dalganın en büyük anlık değeridir (en küçük −12,0 V, tepeden tepeye 21,4 V); bu yüzden 7,5 V ile doğrudan karşılaştırılamaz. Multimetre salınımı ortalayıp tek bir sayı gösterdiği için iki aletin bu satırdaki farkı aslında iki ayrı olgunun farkıdır.", align="j")
    D.p("**Soru 3: İç dirençler karşılaştırıldığında, iç direncin devre direncine göre büyüklüğü sonucu nasıl etkiler?**", align="j", keep=True)
    D.p("Ölçü aleti devreye paralel girdiğinden ölçülen düğümün direnci $R$’den $R\\parallel R_{ic}$’ye düşer. Hata $R/R_{ic}$ oranına bağlıdır: $R_{ic} \\gg R$ ise hata ihmal edilebilir, $R_{ic} \\approx R$ ise gerilim yaklaşık yarıya iner, $R_{ic} \\ll R$ ise okuma sıfıra yaklaşır. Ölçümlerimiz bunu gösterdi: multimetrenin görünen iç direnci yaklaşık $0{,}3$–$0{,}7\\ \\mathrm{M\\Omega}$ olduğundan $470\\ \\Omega$’da ($R/R_{ic} \\sim 10^{-3}$) etki görmedik; $100\\ \\mathrm{k\\Omega}$’da ($R/R_{ic} \\approx 0{,}3$) okuma 7,5 V yerine 6,5 V’a, $10\\ \\mathrm{M\\Omega}$’da ($R/R_{ic} \\approx 15$) 0,9 V’a düştü. Kural olarak ölçü aletinin iç direnci, ölçülen düğümün Thevenin direncinin en az 100 katı olmalıdır. Bu sağlanamıyorsa yüklü değer ([[e:load]]) hesaplanmalı, daha yüksek iç dirençli bir alet (veya 10× osiloskop ucu) kullanılmalı ya da düğümün direnci küçültülmelidir.", align="j")

    # ---- 3
    D.h(2, "Wheatstone Köprüsü")
    D.h(3, "Devre ve Devre Tahtası Yerleşimi")
    D.p("Föydeki Şekil 2’deki köprüyü $V_S = +15$ V ile besledik; $R_1 = R_2 = 470\\ \\Omega$ (renk kodu) aldık, $R_3$ yerine potansiyometre, $R_x$ yerine laboratuvar asistanının verdiği bilinmeyen direnci bağladık. Devre tahtası yerleşimi [[f:bbw]]’de görülmektedir. $V_B$, $R_1$–$R_3$ ortak düğümü ile $R_2$–$R_x$ ortak düğümü arasındaki gerilimdir.", align="j")
    D.fig("bbw", a("bb_whe.png"), "Wheatstone köprüsünün devre tahtası yerleşimi. Potansiyometre $R_3$ yerine, bilinmeyen direnç $R_x$ yerine bağlanır; $V_B$ multimetreyle iki orta düğüm arasından ölçülür.", 14.0)
    D.h(3, "Kuramsal Hesap")
    D.p("Sol kolun orta düğümü $V_L = V_S\\,R_3/(R_1+R_3)$, sağ kolun orta düğümü $V_R = V_S\\,R_x/(R_2+R_x)$ gerilimindedir. Köprü dengedeyken $V_B = V_L - V_R = 0$ olur ve bu koşul kaynak geriliminden bağımsızdır:", align="j", keep=True)
    D.eq(r"V_B=V_S\left(\frac{R_3}{R_1+R_3}-\frac{R_x}{R_2+R_x}\right)=0\;\Rightarrow\;R_1R_x=R_2R_3\;\Rightarrow\;R_x=\frac{R_2R_3}{R_1}", "bridge")
    D.p("Dengenin kaynak geriliminden bağımsız olması köprünün asıl avantajıdır: sonuç $V_S$’in dalgalanmasından etkilenmez, yalnızca direnç oranlarına bağlıdır. Ölçtüğümüz değerleri ($R_1 = 464\\ \\Omega$, $R_2 = 456\\ \\Omega$, denge anındaki $R_3 = 3{,}22\\ \\mathrm{k\\Omega}$) kullanınca:", align="j", keep=True)
    D.eq(r"R_x=\frac{456\ \Omega\cdot3220\ \Omega}{464\ \Omega}=" + n(rx, 1).replace(",", "{,}") + r"\ \Omega", "rx")
    D.h(3, "Ölçümler")
    D.fig("fwh", a("f_whe.jpg"), "Üst sıra: $R_1$ ve $R_2$ ölçümleri (464 Ω ve 456 Ω) ve devreden çıkarılmış potansiyometrenin ($R_3$) ölçümü, $3{,}22\\ \\mathrm{k\\Omega}$. Alt sıra: denge anında $V_B = 0{,}00$ V, $R_x$’in tek başına ölçümü ($3{,}26\\ \\mathrm{k\\Omega}$) ve devre tahtası.", 15.5)
    D.p("Köprüyü, $V_B = 0$ olana kadar potansiyometreyi çevirerek dengeledik; sonra potansiyometreyi devreden çıkarıp multimetreyle ölçtük ve $R_3 = 3{,}22\\ \\mathrm{k\\Omega}$ bulduk. $R_x$’i de ayrıca tek başına multimetreyle ölçtük ve $3{,}26\\ \\mathrm{k\\Omega}$ bulduk. Üzerindeki renk kodu $3{,}3\\ \\mathrm{k\\Omega}$’dur. Föyde $R_x$ ile $R_3$’ün tanımları arasında bir karışıklık olduğunu fark ettik; Tablo 4’ün Wheatstone satırı için formülden ([[e:bridge]]) hesaplanan $R_x$’i kullandık.", align="j")
    rows = [["Renk kodu (3,3 kΩ ± %5)", "3.300", "0"],
            ["Multimetre ölçümü", "3.260", pc(pct(rxd, rc))],
            ["Wheatstone köprüsü ölçümü ($R_x = R_2R_3/R_1$)", n(rx, 1), pc(pct(rx, rc))]]
    D.tab("t4", ["Yöntem", "Direnç değeri (Ω)", "Renk kodundan fark (%)"], rows, "$R_x$ direncinin değeri ve karşılaştırılması (föy Tablo 4)", [7.4, 3.6, 3.8])
    D.p("Renk kodu ±%5 toleransla $3135$–$3465\\ \\Omega$ aralığını verir; iki ölçüm de bu aralıktadır.", align="j")
    D.h(3, "Yorum")
    D.p(("**Köprü ile multimetre aynı mıdır?** Köprüyle %s Ω, multimetreyle 3260 Ω bulduk; fark %s. Fark küçük ama köprünün belirsizliğinden büyük: $V_B$ ekranda 0,00 V okunduğu için denge hatası en çok ±5 mV’tur ve bu $R_3$’te yaklaşık %%0,3’e karşılık gelir; $R_1$, $R_2$ ve $R_3$ okumalarının son basamakları da toplam %%0,5 kadar belirsizlik katar. Kalan farkı şu nedenlere bağlıyoruz: (a) devre tahtasındaki kontak ve jumper dirençleri ($R_3$ devreden çıkarılıp ölçülünce bu dirençler ölçüme girmez, köprü dengelenirken ise kolun içindedirler; bir kolda yaklaşık 100 Ω fazladan direnç %%3’lük farkı doğurur), (b) potansiyometre sürgüsünün temas direnci, (c) dirençlerin devre içinde ve dışında farklı okunabilmesi.") % (n(rx, 0), pc(pct(rx, rxd))), align="j")
    D.p("**Ölçümler renk koduyla uyumlu mu?** Evet: multimetre %s, köprü %s saptı ve ikisi de %%5 tolerans aralığının içinde. Renk kodunun bir hedef değer olduğunu, gerçek değerin ise bu hedefin etrafında dağıldığını burada da gördük." % (pc(pct(rxd, rc)), pc(pct(rx, rc))), align="j")

    # ---- 4
    D.h(2, "Dijital-Analog Çevirici (DAC)")
    D.h(3, "Devre ve Devre Tahtası Yerleşimi")
    D.p("Föydeki Şekil 3’teki 3 bitlik R-2R merdiven DAC’ında her bit $2\\ \\mathrm{k\\Omega}$’luk bir giriş direnciyle merdivene bağlanır; merdiven iki adet $1\\ \\mathrm{k\\Omega}$’luk seri direnç ve $2\\ \\mathrm{k\\Omega}$’luk bir sonlandırma direncinden, çıkış ise $R_L = 1\\ \\mathrm{k\\Omega}$’luk yük direncinden oluşur. Mantık “1” için girişi 16 V’a, “0” için toprağa bağladık. Devre tahtası yerleşimi [[f:bbc]]’dedir.", align="j")
    D.fig("bbc", a("bb_dac.png"), "3 bitlik R-2R DAC’ın devre tahtası yerleşimi. $R_{i1}, R_{i2}, R_{i3} = 2\\ \\mathrm{k\\Omega}$ (giriş), $R_a = R_b = 1\\ \\mathrm{k\\Omega}$, $R_t = 2\\ \\mathrm{k\\Omega}$, $R_L = 1\\ \\mathrm{k\\Omega}$. Turuncu jumperlar girişleri 16 V rayına (mantık 1, kod 111) bağlar; bir bit 0 olacaksa jumper alt rayına (toprağa) taşınır. Multimetre $V_O$ düğümündedir.", 14.0)
    D.h(3, "Kuramsal Hesap")
    D.p("Devre doğrusal olduğundan çıkış, her bitin tek başına yarattığı çıkışların toplamıdır (süperpozisyon). Giriş dirençlerinin merdivenle birleştiği üç düğüm vardır: $A$ ($V_O$ düğümü), $B$ ve $C$. Düğüm denklemleri ($G_i = 1/2\\ \\mathrm{k\\Omega}$, $b_k \\in \\{0,1\\}$):", align="j", keep=True)
    D.eq(r"\begin{bmatrix}G_i+G_a+G_L&-G_a&0\\-G_a&G_i+G_a+G_b&-G_b\\0&-G_b&G_i+G_b+G_t\end{bmatrix}\begin{bmatrix}V_A\\V_B\\V_C\end{bmatrix}=G_i\,V_{\mathrm{mantık}}\begin{bmatrix}b_2\\b_1\\b_0\end{bmatrix}", "dacm")
    D.p("Denklemi çözünce her bitin $V_O$’ya katkısının bit ağırlığıyla orantılı olduğunu bulduk: en anlamlı bit için 4 V, ortadaki için 2 V, en az anlamlı bit için 1 V. Yani devre $V_O = (4b_2+2b_1+b_0)\\times 1\\ \\mathrm{V}$ dönüşümünü yapar. Buna göre $100$, $011$ ve $111$ girişleri için beklenen çıkışlar $4$ V, $3$ V ve $7$ V’tur.", align="j")
    D.h(3, "Ölçümler ve Karşılaştırma")
    D.fig("fdac", a("f_dac.jpg"), "DAC çıkış gerilimleri: 100 için $4{,}09$ V, 011 için $3{,}27$ V, 111 için $7{,}34$ V.", 15.5)
    rows = []
    for nm, k, m in (("100", 4.0, 4.09), ("011", 3.0, 3.27), ("111", 7.0, 7.34)):
        rows.append([nm, n(k, 3), n(m, 2), n(m - k, 2), pc(pct(m, k))])
    D.tab("t5", ["Giriş", "Kuramsal $V_O$ (V)", "Ölçülen $V_O$ (V)", "Mutlak fark (V)", "Fark (%)"], rows, "DAC çıkış gerilimleri: kuramsal ve ölçülen", [2.0, 3.4, 3.4, 3.0, 2.4])
    D.h(3, "Yorum")
    D.p("Ölçtüğümüz değerlerin hepsi beklenenin üstünde çıktı (%2,3, %9,0 ve %4,9). Ölçümlerimiz birbiriyle tutarlıdır: $100$ ve $011$ okumalarının toplamı $4{,}09 + 3{,}27 = 7{,}36$ V, $111$ için okuduğumuz değer ise $7{,}34$ V’tur (%0,3 fark); yani devre doğrusal davrandı, sorun ölçümde değil bit ağırlıklarındadır. Ağırlıkların oranı $4{,}09/3{,}27 = 1{,}25$ çıktı, beklenen oran $4/3 = 1{,}33$’tür: bir bitin ağırlığı diğerine göre kaydı. Olası nedenler: (a) direnç toleransları. Bütün dirençler ±%5 toleransla değişirse çıkışların %95 olasılıkla $100$ için $3{,}81$–$4{,}20$ V, $011$ için $2{,}87$–$3{,}13$ V, $111$ için $6{,}76$–$7{,}24$ V aralığında kalacağını hesapladık. Ölçtüğümüz $4{,}09$ V bu aralıktadır; $3{,}27$ V ve $7{,}34$ V ise dışındadır, yani tolerans tek başına açıklamaya yetmiyor. (b) “16 V”un gerçekte 16 V olmaması: 16,3 V olsa çıkışlar %1,9 artardı ama oran bozulmazdı. (c) $2\\ \\mathrm{k\\Omega}$ gibi değerleri seri-paralel bağlamayla elde ettiysek her bağlantı kontak direnci ekler ve bit ağırlıklarını bozar. (d) Kaynağın yük altında geriliminin düşmesi. Dirençleri tek tek ölçmediğimiz için hangi nedenin baskın olduğunu söyleyemiyoruz; tek tek ölçseydik ölçülen değerleri $V_O$ formülüne koyarak sapmanın kaynağını bulabilirdik.", align="j")

    # ================= SONUÇLAR
    D.h(1, "Sonuçlar")
    D.p("**Genel değerlendirme.** Seri ve paralel bağlantı kurallarını ölçümle doğruladık: seri ölçüm toplamdan %%0,48, paralel ölçüm hesaptan %%0,39 farklı çıktı. Gerilim bölücüde asıl bulgu, ölçü aletlerinin iç direncinin sonucu belirlemesidir: $470\\ \\Omega$’da iki alet de beklenene yakındı (7,4 V ve 7,40 V; beklenen 7,5 V); $100\\ \\mathrm{k\\Omega}$’da multimetre 6,5 V, osiloskop 7,4 V gösterdi; $10\\ \\mathrm{M\\Omega}$’da multimetre 0,9 V gösterdi, osiloskop ekranında ise 50 Hz’lik parazit (en büyük 9,40 V, tepeden tepeye 21,4 V) gördük. Ölçümlerden multimetrenin görünen iç direncini yaklaşık $0{,}3$–$0{,}7\\ \\mathrm{M\\Omega}$ bulduk. Wheatstone köprüsüyle bilinmeyen direnci $%s\\ \\Omega$ bulduk; multimetreyle ölçtüğümüz $3260\\ \\Omega$’dan %s farklıdır ve ikisi de renk kodunun ($3{,}3\\ \\mathrm{k\\Omega}$ ±%%5) tolerans aralığındadır. DAC çıkışlarını beklenenden %%2,3–%%9 yüksek ölçtük." % (n(rx, 0), pc(pct(rx, rxd))), align="j")
    D.p("**Eksik kalan noktalar.** (i) Multimetrenin görünen iç direncinin katalog değerinden çok küçük çıkmasının nedenini belirleyemedik; bilinen bir dirençle ayrıca ölçüm yapmak gerekir. (ii) Osiloskop ucunun 1× mi 10× mu olduğunu not almadık. (iii) DAC’ta tolerans tek başına sapmayı açıklamıyor ve dirençleri tek tek ölçmedik.", align="j")
    D.p("**Kazanımlar.** Seri-paralel direnç hesabı ve ölçümü; ölçü aletinin yük etkisinin hesaplanması; osiloskop ve multimetrenin birlikte kullanımı ve 50 Hz parazitin tanınması; köprü yöntemi; DAC ağırlıklarının süperpozisyonla hesabı; devre tahtası yerleşimi ve ölçümleri beklenen değerle yüzde farkla karşılaştırma.", align="j")

    D.h(1, "Kaynaklar")
    refs_block(D, ["Nilsson, J. W., & Riedel, S. A. (2015). *Electric circuits* (10th ed.). Boston: Pearson.",
                   "Alexander, C. K., & Sadiku, M. N. O. (2017). *Fundamentals of electric circuits* (6th ed.). New York: McGraw-Hill Education.",
                   "Hayt, W. H., Kemmerly, J. E., & Durbin, S. M. (2012). *Engineering circuit analysis* (8th ed.). New York: McGraw-Hill.",
                   "Horowitz, P., & Hill, W. (2015). *The art of electronics* (3rd ed.). New York: Cambridge University Press.",
                   "TOBB Ekonomi ve Teknoloji Üniversitesi. (2026). *ELE 201 L – Devre Analizi I Laboratuvarı, Deney 1 Föyü*. Ankara: TOBB ETÜ, Elektrik – Elektronik Mühendisliği Bölümü."])

    D.h(1, "Ekler")
    D.h(3, "EK-1: Kullanılan Aletler")
    D.tab("tal", ["Alet", "Kullanım"], [["UNI-T UT33D+ multimetre", "Direnç ve gerilim ölçümleri"], ["Tektronix TBS 1022 osiloskop", "Gerilim bölücü çıkışı"], ["DA güç kaynağı", "15 V ve 16 V beslemeler"], ["Devre tahtası, dirençler, potansiyometre", "Bütün devreler"]], "Deneyde kullanılan aletler", [7.0, 7.0], size=10)
    return D

if __name__ == "__main__":
    D = build(); f = os.path.join(OUT, "ELE201L_Deney1_Laboratuvar_Raporu.docx"); D.save(f)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", OUT, f], capture_output=True, timeout=300); print("ok")
