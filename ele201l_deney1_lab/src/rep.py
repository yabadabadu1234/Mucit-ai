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
    D.fig("fdmm", a("f_dmm.jpg"), "Multimetre okumaları (soldan sağa): $470\\ \\Omega$ için 7,4 V; $100\\ \\mathrm{k\\Omega}$ için 6,5 V; $10\\ \\mathrm{M\\Omega}$ için 0,9 V.", 15.5)
    D.fig("fosc", a("f_osc.jpg"), "Osiloskop (Tektronix TBS 1022) ekranları: $470\\ \\Omega$ için 7,40 V; $100\\ \\mathrm{k\\Omega}$ için 7,4 V; $10\\ \\mathrm{M\\Omega}$ için 49,998 Hz’lik sinüs (en küçük −12,0 V, en büyük 9,40 V, tepeden tepeye 21,4 V).", 15.5)
    rows = [["470 Ω", "7,5", "7,4", "7,40"],
            ["100 kΩ", "7,5", "6,5", "7,4"],
            ["10 MΩ", "7,5", "0,9", "9,40 (en büyük değer; sinyal 50 Hz, 21,4 V tepeden tepeye)"]]
    D.tab("t3", ["R", "Beklenen $V_O$ (V)", "Multimetre (V)", "Osiloskop (V)"], rows, "Gerilim bölücü ölçümleri (föy Tablo 3)", [2.4, 3.2, 3.0, 6.3])
    D.h(3, "Sorular")
    D.p("**Soru 1: Teorik ve ölçülen $V_O$ arasında fark gözlendi mi? Nedenleri nelerdir?**", align="j", keep=True)
    D.p("Fark vardır ve direnç büyüdükçe çok büyümüştür. $470\\ \\Omega$ satırında multimetre 7,4 V, osiloskop 7,40 V göstermiştir (beklenen 7,5 V; %1,3 fark). Bu fark ölçü aletlerinden değil, iki direncin birbirine tam eşit olmamasından gelir (ölçülen $R_1 = 464\\ \\Omega$; nominalden %1,3 küçük) ve bu satırda iç direnç etkisi yoktur ($R/R_{ic} \\approx 10^{-3}$’ten küçüktür). $100\\ \\mathrm{k\\Omega}$ satırında multimetre 6,5 V (%13 düşük), osiloskop ise 7,4 V (%1,3 düşük) göstermiştir; yani iki alet aynı noktada 0,9 V farklı değer vermiştir. $10\\ \\mathrm{M\\Omega}$ satırında multimetre 0,9 V (beklenen değerin yalnızca %12’si) göstermiştir; osiloskopta ise DA değer yerine 50 Hz’lik büyük bir sinüs görülmüştür. Bu üç satırdaki farkların tek nedeni, ölçü aletlerinin iç direncinin alt dirence paralel girerek bölücü oranını değiştirmesidir ([[e:load]]). Aşağıdaki hesap, ölçülen değerlerden aletlerin “görünen” iç direncini bulmaktadır.", align="j")
    D.p("**Ölçülen değerlerden iç direncin bulunması.** [[e:load]] $R_{ic}$’e göre çözülürse ($k = V_O/(V_S - V_O)$ olmak üzere, iki direnç eşit varsayılırsa $R_p = kR$) şu elde edilir:", align="j", keep=True)
    D.eq(r"R_{ic}=\frac{R\,R_p}{R-R_p}=\frac{k\,R}{1-k},\qquad k=\frac{V_O}{V_S-V_O}", "ric")
    D.p("Multimetre için $100\\ \\mathrm{k\\Omega}$ satırında ($R = 99{,}1\\ \\mathrm{k\\Omega}$, $V_O = 6{,}5$ V): $k = 6{,}5/8{,}5 = 0{,}765$ ve $R_{ic} \\approx 0{,}32\\ \\mathrm{M\\Omega}$ bulunur (ekranın son basamağı olan ±0,05 V’a karşılık $0{,}30$–$0{,}34\\ \\mathrm{M\\Omega}$). $10\\ \\mathrm{M\\Omega}$ satırında ($R = 10{,}30\\ \\mathrm{M\\Omega}$, $V_O = 0{,}9$ V): $k = 0{,}9/14{,}1 = 0{,}0638$ ve $R_{ic} \\approx 0{,}70\\ \\mathrm{M\\Omega}$ bulunur ($0{,}66$–$0{,}75\\ \\mathrm{M\\Omega}$). Osiloskop için $100\\ \\mathrm{k\\Omega}$ satırında ($V_O = 7{,}4$ V): $R_{ic} \\approx 3{,}7\\ \\mathrm{M\\Omega}$ bulunur; ekran basamağı nedeniyle aralık geniştir ($2{,}4$–$7{,}4\\ \\mathrm{M\\Omega}$).", align="j")
    D.p("**Yorum.** Bu sayılar şunu söylemektedir: ölçümde multimetrenin devreye gösterdiği direnç yaklaşık $0{,}3$–$0{,}7\\ \\mathrm{M\\Omega}$ mertebesindedir; katalog değeri olan $10\\ \\mathrm{M\\Omega}$’dan yaklaşık 15–30 kat küçüktür. Bu iki sonucun birbirinden farklı çıkması (0,32 ve 0,70), $10\\ \\mathrm{M\\Omega}$ satırında $R_{ic}$’nin direnç değerlerine (ölçülmeyen ikinci direnç dâhil) çok duyarlı olmasındandır; iki sayı birlikte tek bir gerçeği gösterir: bu ölçümlerde multimetre, iç direnci katalogdaki $10\\ \\mathrm{M\\Omega}$’dan çok daha küçük bir yük gibi davranmıştır. Bunun nedenini (aletin giriş devresi, kademe, aynı düğüme aynı anda bağlı başka bir ölçü kablosu vb.) fotoğraflardan ve kayıtlardan kesinleştiremedim; kesinleştirmenin yolu, aleti bilinen bir dirençle (örneğin $1\\ \\mathrm{M\\Omega}$) bir gerilim kaynağına seri bağlayıp [[e:load]]’i ters çözmektir. Osiloskop ise $100\\ \\mathrm{k\\Omega}$ satırında yalnızca %1,3 düşük okumuştur; bu, giriş direncinin multimetreninkinden çok daha büyük göründüğünü gösterir (10× uçla $10\\ \\mathrm{M\\Omega}$ için [[e:load]] 7,46 V verir, 1× uçla $1\\ \\mathrm{M\\Omega}$ için 7,14 V verirdi; okunan 7,4 V birinciye yakındır, uç tipi kayıtlı değildir).", align="j")
    D.p("**Soru 2: Multimetre ve osiloskop aynı $V_O$ noktasında farklı değer gösterdi mi? Neden?**", align="j", keep=True)
    D.p("Evet, $100\\ \\mathrm{k\\Omega}$ ve $10\\ \\mathrm{M\\Omega}$ satırlarında. Nedeni iki aletin devreye farklı iç direnç göstermesidir: [[e:load]]’e göre alt dirence paralel giren direnç ne kadar küçükse düğüm gerilimi o kadar düşer. $100\\ \\mathrm{k\\Omega}$’da yüksek iç dirençli alet (osiloskop, 7,4 V) beklenen değere yakın, daha düşük iç dirençli alet (multimetre, 6,5 V) ise belirgin biçimde düşük göstermiştir. $10\\ \\mathrm{M\\Omega}$ satırında fark daha da büyüktür (multimetre 0,9 V; osiloskopta 7,5 V civarında beklenen DA değer yerine, en büyük değeri 9,40 V olan 50 Hz’lik bir sinüs). Osiloskoptaki sinüs, şebekenin (50 Hz) yüksek empedanslı düğüme kapasitif olarak indüklediği parazit gerilimdir: düğümün kaynak direnci (bu satırda yaklaşık $5\\ \\mathrm{M\\Omega}$) büyük olduğunda aynı küçük kaçak akım büyük bir gerilim doğurur. Burada 9,40 V bir DA değeri değil, dalganın en büyük anlık değeridir (tepeden tepeye 21,4 V, en küçük −12,0 V), bu yüzden 7,5 V’la karşılaştırılamaz; osiloskop ekranında DA değeri ancak bu parazit süzülürse (örneğin bir kapasitörle veya AC kuplaj yerine DA kuplajda ortalama alınarak) okunabilir. Multimetre ise bu salınımı ortalar ve tek bir sayı gösterir; bu yüzden iki aletin bu satırdaki “farkı” gerçekte iki ayrı olgunun farkıdır.", align="j")
    D.p("**Soru 3: İç dirençler karşılaştırıldığında, iç direncin devre direncine göre büyüklüğü sonucu nasıl etkiler?**", align="j", keep=True)
    D.p("Ölçü aleti devreye paralel girdiğinden, ölçülen düğümün direnci $R$’den $R\\parallel R_{ic}$’ye iner. Bağıl yük hatası yaklaşık $R/R_{ic}$ oranına bağlıdır: $R_{ic} \\gg R$ ise hata ihmal edilebilir; $R_{ic} \\approx R$ ise gerilim yaklaşık yarıya iner; $R_{ic} \\ll R$ ise okuma sıfıra yaklaşır. Ölçümlerimiz bunu açıkça göstermektedir: multimetrenin görünen iç direnci yaklaşık $0{,}3$–$0{,}7\\ \\mathrm{M\\Omega}$ olduğundan $470\\ \\Omega$’da ($R/R_{ic} \\sim 10^{-3}$) etki yoktur, $100\\ \\mathrm{k\\Omega}$’da ($R/R_{ic} \\approx 0{,}3$) okuma 7,5 V yerine 6,5 V’a, $10\\ \\mathrm{M\\Omega}$’da ($R/R_{ic} \\approx 15$) 0,9 V’a inmiştir. Kural şudur: ölçü aleti, ölçülen düğümün Thevenin direncinin en az 100 katı kadar iç dirence sahip olmalıdır. Bu sağlanamadığında ya kuramsal yüklü değer ([[e:load]]) hesaplanmalı, ya daha yüksek iç dirençli bir alet (veya 10× osiloskop ucu) kullanılmalı, ya da ölçülen düğümün direnci küçültülmelidir.", align="j")

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
    D.p("Föydeki el yazısı notlarda $R_1 = 464\\ \\Omega$ ve $R_2 = 456\\ \\Omega$ yazılıdır; hesap bu değerlerle yapılmıştır. $R_3$ potansiyometredir; $V_B = 0$ olunca devreden çıkarılıp multimetreyle ölçülmüş ve $3{,}22\\ \\mathrm{k\\Omega}$ bulunmuştur. $R_x$ ise tek başına multimetreyle ölçülmüş ve $3{,}26\\ \\mathrm{k\\Omega}$ bulunmuştur. Üzerindeki renk kodu $3{,}3\\ \\mathrm{k\\Omega}$’dur. Föyde $R_x$ ve $R_3$’ün tanımı arasında bir tutarsızlık vardır (föydeki Tablo 4’ün Wheatstone satırına el ile $R_3$’ün kendisi, $3{,}22\\ \\mathrm{k\\Omega}$ yazılmıştır); bu raporda Wheatstone ölçümü olarak [[e:bridge]] ile hesaplanan $R_x$ kullanılmıştır.", align="j")
    rows = [["Renk kodu (3,3 kΩ ± %5)", "3.300", "0"],
            ["Multimetre ölçümü", "3.260", pc(pct(rxd, rc))],
            ["Wheatstone köprüsü ölçümü ($R_x = R_2R_3/R_1$)", n(rx, 1), pc(pct(rx, rc))]]
    D.tab("t4", ["Yöntem", "Direnç değeri (Ω)", "Renk kodundan fark (%)"], rows, "$R_x$ direncinin değeri ve karşılaştırılması (föy Tablo 4)", [7.4, 3.6, 3.8])
    D.p("Renk kodu ± %5 toleransla $3135$–$3465\\ \\Omega$ aralığını verir. Her iki ölçüm de bu aralıktadır.", align="j")
    D.h(3, "Yorum")
    D.p(("**Köprü ile multimetre aynı mıdır?** Köprü yöntemiyle %s Ω, multimetreyle 3260 Ω bulunmuştur; fark %s’dir. Fark küçüktür ama köprünün belirsizliğinden büyüktür: $V_B$ ekranda 0,00 V okunduğundan denge hatası en çok ±5 mV’tur ve bu $R_3$’te yaklaşık %%0,3 sapmaya karşılık gelir; $R_1$, $R_2$ ve $R_3$ okumalarının son basamakları toplam %%0,5 mertebesinde belirsizlik ekler. Kalan farkın olası nedenleri: (a) devre tahtasındaki kontak ve jumper dirençleri ($R_3$ devreden çıkarılıp ölçüldüğünde bu dirençler ölçüme girmez, oysa köprü dengelenirken kolun içindedirler; bir kolda yaklaşık 100 Ω fazladan direnç %%3’lük farkı doğurur), (b) potansiyometre sürgüsünün temas direnci, (c) $R_1$ ve $R_2$ değerlerinin, devre içinde ve devre dışında ölçüldüğünde farklı okunabilmesi. Köprünün kendi gücü ise sonucun kaynak geriliminden bağımsız olmasıdır.") % (n(rx, 0), pc(pct(rx, rxd))), align="j")
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
    D.p("**Genel değerlendirme.** Seri ve paralel bağlantı kuralları ölçümle doğrulanmıştır: seri ölçüm toplamdan %%0,48, paralel ölçüm hesaptan %%0,39 farklıdır. Gerilim bölücüde asıl bulgu, ölçü aletlerinin iç direncinin sonucu belirlediğidir: $470\\ \\Omega$’da iki alet de beklenene yakındır (7,4 V ve 7,40 V; beklenen 7,5 V); $100\\ \\mathrm{k\\Omega}$’da multimetre 6,5 V, osiloskop 7,4 V; $10\\ \\mathrm{M\\Omega}$’da multimetre 0,9 V ve osiloskop ekranında 50 Hz’lik parazit (en büyük 9,40 V, tepeden tepeye 21,4 V) görülmüştür. Ölçümlerden multimetrenin görünen iç direnci yaklaşık $0{,}3$–$0{,}7\\ \\mathrm{M\\Omega}$ bulunmuştur. Wheatstone köprüsünde bilinmeyen direnç $%s\\ \\Omega$ bulunmuş, multimetre ölçümüyle ($3260\\ \\Omega$) %s farkla karşılaştırılmıştır; ikisi de renk kodunun ($3{,}3\\ \\mathrm{k\\Omega}$ ± %%5) tolerans aralığındadır. DAC çıkışları beklenenin %%2,3–%%9 üzerinde ölçülmüştür." % (n(rx, 0), pc(pct(rx, rxd))), align="j")
    D.p("**Açık kalan hususlar.** (i) Multimetrenin görünen iç direncinin (yaklaşık $0{,}3$–$0{,}7\\ \\mathrm{M\\Omega}$) katalog değerinden çok küçük çıkmasının fiziksel nedeni fotoğraflardan belirlenememiştir; bilinen dirençle kalibrasyon ölçümü bunu kesinleştirir; (ii) osiloskopun uç tipi (1× veya 10×) kayıtlı değildir; (iii) DAC’ta tolerans tek başına sapmayı açıklamamaktadır ve direnç değerleri tek tek ölçülmemiştir.", align="j")
    D.p("**Kazanılan beceriler.** Dirençlerin seri-paralel hesabı ve ölçümü; ölçü aletinin yük etkisinin hesaplanması; osiloskop ve multimetrenin birlikte kullanımı ve 50 Hz parazitin tanınması; köprü yöntemi; DAC ağırlıklarının süperpozisyonla hesabı; devre tahtası yerleşiminin planlanması ve ölçümlerin kuramsal değerle yüzde farkla karşılaştırılması.", align="j")

    D.h(1, "Kaynaklar")
    refs_block(D, ["Nilsson, J. W., & Riedel, S. A. (2015). *Electric circuits* (10th ed.). Boston: Pearson.",
                   "Alexander, C. K., & Sadiku, M. N. O. (2017). *Fundamentals of electric circuits* (6th ed.). New York: McGraw-Hill Education.",
                   "Hayt, W. H., Kemmerly, J. E., & Durbin, S. M. (2012). *Engineering circuit analysis* (8th ed.). New York: McGraw-Hill.",
                   "Horowitz, P., & Hill, W. (2015). *The art of electronics* (3rd ed.). New York: Cambridge University Press.",
                   "TOBB Ekonomi ve Teknoloji Üniversitesi. (2026). *ELE 201 L – Devre Analizi I Laboratuvarı, Deney 1 Föyü*. Ankara: TOBB ETÜ, Elektrik – Elektronik Mühendisliği Bölümü."])

    D.h(1, "Ekler")
    D.h(3, "EK-1: Fotoğraf Okuma Çizelgesi ve Eşleştirme Gerekçesi")
    D.p("Aşağıda her fotoğrafın (yükleme sırasıyla numaralanmıştır) gösterdiği okuma ve rapordaki karşılığı verilmiştir. Gerilim bölücü okumaları (multimetre: 7,4 / 6,5 / 0,9 V; osiloskop: 7,40 / 7,4 / 9,40 V) deneyi yapan kişinin kesin beyanıdır; fotoğraf eşleştirmesi bu beyana ve osiloskop saatlerine (08:20, 08:23, 08:25) dayanmaktadır.", align="j")
    rows = [["1", "464 Ω", "$R_1$ ayrı ölçüm"], ["2", "99,1 kΩ", "$R_2$ ayrı ölçüm"], ["3", "0,46 kΩ", "Paralel bağlantı"], ["4", "10,45 MΩ", "Seri bağlantı"], ["5", "10,30 MΩ", "$R_3$ ayrı ölçüm"],
            ["6", "7,4 V", "Multimetre, bölücü"], ["7", "7,40 V (08:20)", "Osiloskop, bölücü"], ["8", "6,5 V", "Multimetre, bölücü (100 kΩ)"], ["9", "50 Hz; en büyük 9,40 V; t.t. 21,4 V", "Osiloskop (08:25), 10 MΩ"],
            ["10", "0,9 V", "Multimetre, bölücü (10 MΩ)"], ["11", "7,4 V (08:23)", "Osiloskop, bölücü (100 kΩ)"], ["12", "3,26 kΩ", "$R_x$ doğrudan (devre tahtası sahnesi)"], ["13", "0,00 V", "Köprü $V_B$ (denge)"],
            ["14", "3,22 kΩ", "$R_3$ (potansiyometre, devreden çıkarılmış)"], ["15", "3,26 kΩ", "$R_x$ doğrudan"], ["16", "456 Ω", "Köprü direnç ölçümü"], ["17", "7,34 V", "DAC 111"], ["18", "464 Ω", "Köprü direnç ölçümü"],
            ["19", "4,09 V", "DAC 100"], ["20", "3,27 V", "DAC 011"]]
    D.tab("tek", ["Fotoğraf", "Okuma", "Karşılığı"], rows, "Fotoğraf okuma çizelgesi", [2.2, 4.4, 7.4], size=9)
    D.p("Osiloskop 10 MΩ satırındaki 9,40 V, ekrandaki 50 Hz’lik dalganın en büyük değeridir (fotoğraf 9); ortalama DA değeri değildir.", align="j")
    return D

if __name__ == "__main__":
    D = build(); f = os.path.join(OUT, "ELE201L_Deney1_Laboratuvar_Raporu.docx"); D.save(f)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", OUT, f], capture_output=True, timeout=300); print("ok")
