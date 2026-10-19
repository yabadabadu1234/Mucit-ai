import subprocess, math
from common import *
from docbuilder import Doc

def build():
    D = Doc("tr")
    D.sec = 2  # format: 1 Yazım kuralları ve 2 Rapor içeriği bölümleri kapsam dışı; rapor 3'ten başlar
    D.title_block([("TOBB Ekonomi ve Teknoloji Üniversitesi", 13, True), ("Elektrik – Elektronik Mühendisliği Bölümü", 12, False),
                   ("ELE 201 L – Devre Analizi I Laboratuvarı", 14, True), ("Deney 1 – Deney Raporu", 14, True), ("Güz 2026", 12, False)],
                  [("Adı Soyadı", "Işıl Fidancan / Bahar Işıklar / Beşir Kerem Üstüntürk"), ("Numara", "251201045 / 241201036 / 251201037"), ("Tarih", "")])

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
    D.p("Bu deneyde dört çalışma yapılmıştır: (i) dirençler seri ve paralel bağlanarak eşdeğer direnç ölçülmüştür, (ii) gerilim bölücü devrenin çıkışı hem multimetre hem osiloskopla ölçülerek ölçü aletinin devreye etkisi incelenmiştir, (iii) Wheatstone köprüsüyle bilinmeyen bir direnç ölçülmüştür ve (iv) 3 bitlik R-2R merdiven tipi sayısal-analog çevirici (DAC) devresinin çıkış gerilimi ölçülmüştür. Her bölümde önce beklenen değer hesaplanmış, ardından ölçülen değerle karşılaştırılarak farkın nedeni yorumlanmıştır.", align="j")
    D.h(2, "Deneyin Faydaları")
    D.p("Deney sonucunda şu hususlar görülmüştür. Direncin üzerindeki renk kodu bir hedef değerdir; gerçek değer toleransı kadar bu hedeften sapar. Ölçü aleti devreye paralel girdiği için devreyi değiştirir ve bu etki, devre direnci aletin iç direncine yaklaştıkça büyür. Köprü yönteminde sonuç bir alet okumasına değil bir denge şartına dayandığı için hassas olabilir. Sayısal bir kod, direnç ağıyla analog gerilime çevrilebilir; bu çevirinin doğruluğu direnç toleranslarına bağlıdır.", align="j")

    # ================= ÖLÇÜMLER
    D.h(1, "Ölçümler")
    D.p("Bütün ölçümler laboratuvarda UNI-T UT33D+ el tipi multimetre [1] ve Tektronix TBS 1022 osiloskop [2] ile yapılmış; değerler aletlerin ekranından okunup kaydedilmiştir. Beklenen (kuramsal) değerler hesaplanmıştır. Kuramsal değer $x_k$ ve ölçülen değer $x_o$ için fark şöyle tanımlanmıştır:", align="j")
    D.eq(r"\text{Fark}\,(\%)=\frac{x_o-x_k}{x_k}\times 100", "fark")
    D.p("Fark hesaplarında tablolardaki ölçülen değerler kullanılmıştır; ekrandaki son basamağın duyarlığı her yerde ayrıca belirtilmiştir.", align="j")

    # ---- 1
    D.h(2, "Dirençlerin Seri ve Paralel Bağlantıları")
    D.h(3, "Devre Tahtası Yerleşimi")
    D.p("Dirençlerin renk kodundaki değerleri $R_1 = 470\\ \\Omega$, $R_2 = 100\\ \\mathrm{k\\Omega}$ ve $R_3 = 10\\ \\mathrm{M\\Omega}$’dur; gerçek değerleri aşağıda ölçülmüştür. [[f:bbs]]’te dirençlerin seri, [[f:bbp]]’te paralel bağlanmış hâlinin devre tahtası yerleşimi görülmektedir. Seri bağlantıda dirençler uç uca takılır; aradaki ortak sütun (a–e delikleri iç bağlıdır) bağlantı noktasıdır. Paralel bağlantıda üç direncin birer ucu aynı sütuna, diğer uçları başka bir ortak sütuna takılır.", align="j")
    D.fig("bbs", a("bb_seri.png"), "Dirençlerin seri bağlantısı (devre tahtası yerleşimi). Multimetre Ω kademesinde iki serbest uç arasına bağlanır.", 14.0)
    D.fig("bbp", a("bb_par.png"), "Dirençlerin paralel bağlantısı (devre tahtası yerleşimi).", 14.0)
    D.h(3, "Ölçümler ve Hesaplar")
    D.p("Dirençler önce tek tek ölçülmüş ([[f:fd]]), ardından seri bağlanıp toplam direnç, paralel bağlanıp eşdeğer direnç ölçülmüştür ([[f:fsp]]). Seri elemanlardan aynı akım geçtiği ve gerilimler toplandığı için seri eşdeğer dirençlerin toplamıdır:", align="j", keep=True)
    D.eq(r"R_{seri}=R_1+R_2+R_3=464\ \Omega+99{,}1\ \mathrm{k\Omega}+10{,}30\ \mathrm{M\Omega}=10{,}3996\ \mathrm{M\Omega}", "seri")
    D.p("Hesaplanan toplam ile doğrudan ölçümün farkı, kuramsal değere göre yüzde olarak şöyle bulunur:", align="j", keep=True)
    D.eq(r"\text{Fark}=\frac{10{,}45-10{,}3996}{10{,}3996}\times100=\frac{0{,}0504}{10{,}3996}\times100=0{,}48\,\%", "farkseri")
    D.p("Paralel bağlantıda her dirence aynı gerilim uygulanır ve akımlar toplanır; bu nedenle iletkenlikler toplanır:", align="j", keep=True)
    D.eq(r"\frac{1}{R_{par}}=\frac{1}{464}+\frac{1}{99100}+\frac{1}{10{,}30\times10^{6}}=2{,}1552\times10^{-3}+1{,}009\times10^{-5}+9{,}7\times10^{-8}=2{,}1654\times10^{-3}\ \mathrm{S}\;\Rightarrow\;R_{par}=\frac{1}{2{,}1654\times10^{-3}}=461{,}8\ \Omega", "par")
    D.eq(r"\text{Fark}=\frac{460-461{,}8}{461{,}8}\times100=-0{,}39\,\%", "farkpar")
    D.fig("fd", a("f_dirnc.jpg"), "Dirençlerin ayrı ayrı ölçümü: $R_1 = 464\\ \\Omega$, $R_2 = 99{,}1\\ \\mathrm{k\\Omega}$, $R_3 = 10{,}30\\ \\mathrm{M\\Omega}$.", 15.5)
    D.fig("fsp", a("f_serpar.jpg"), "Seri bağlantının ($10{,}45\\ \\mathrm{M\\Omega}$) ve paralel bağlantının ($0{,}46\\ \\mathrm{k\\Omega}$) doğrudan ölçümü.", 12.0)
    rows = [["$R_1$", "464 Ω"], ["$R_2$", "99,1 kΩ"], ["$R_3$", "10,30 MΩ"], ["$R_1+R_2+R_3$ (hesaplanan)", n(S / 1e6, 4) + " MΩ"],
            ["Seri bağlantının doğrudan ölçümü", "10,45 MΩ"], ["Fark", pc(pct(Sd, S))]]
    D.tab("t1", ["Büyüklük", "Değer"], rows, "Seri bağlantı ölçümleri (föy Tablo 1 [3])", [8.5, 4.5])
    rows = [["$R_1 \\parallel R_2 \\parallel R_3$ (hesaplanan)", n(P, 1) + " Ω"], ["Paralel bağlantının doğrudan ölçümü", "0,46 kΩ (460 Ω)"], ["Fark", pc(pct(Pd, P))]]
    D.tab("t2", ["Büyüklük", "Değer"], rows, "Paralel bağlantı ölçümleri (föy Tablo 2 [3])", [8.5, 4.5])
    D.p("**Sonuç ve yorum.** Seri bağlantının doğrudan ölçümü hesaplanan toplamdan %0,48, paralel bağlantının ölçümü hesaplanandan %0,39 farklı çıkmıştır. Bu farkların ölçü aletinin doğruluğu içinde kalıp kalmadığı, kılavuzdaki doğruluk değerleriyle incelenmiştir (EK-2). Cihazla birlikte verilen kılavuza [1] göre direnç ölçümünün doğruluğu 20 MΩ kademesinde ±(%1,2 + 3 basamak), 20 kΩ kademesinde ±(%0,8 + 2 basamak)’tır. 10,45 MΩ okumasında son basamak 10 kΩ olduğundan belirsizlik ±(0,012·10,45 MΩ + 3·10 kΩ) = ±(125,4 kΩ + 30 kΩ) = ±155,4 kΩ bulunur; ölçülen fark 50,4 kΩ olduğu için bu aralığın içindedir. 0,46 kΩ okumasında son basamak 10 Ω olduğundan belirsizlik ±(0,008·460 Ω + 2·10 Ω) = ±(3,7 Ω + 20 Ω) = ±23,7 Ω bulunur; ölçülen fark 1,8 Ω olduğu için bu aralığın da içindedir. Paralel eşdeğerin en küçük dirençten (464 Ω) bile küçük çıkması bir hata değildir: paralel eklenen her yol iletkenliği artırır. Paralel eşdeğeri esas olarak en küçük direnç, seri eşdeğeri ise esas olarak en büyük direnç belirler; 100 kΩ ve 10 MΩ’luk dirençler paralel eşdeğeri yalnızca %0,5 ve %0,005 kadar etkilemiştir (iletkenliklerin toplamdaki payları $1{,}009\\times10^{-5}/2{,}1654\\times10^{-3}=0{,}47\\,\\%$ ve $9{,}7\\times10^{-8}/2{,}1654\\times10^{-3}=0{,}004\\,\\%$).", align="j")

    # ---- 2
    D.h(2, "Gerilim Bölücü Devresi")
    D.h(3, "Devre ve Devre Tahtası Yerleşimi")
    D.p("Föydeki Şekil 1’deki devre [3] kurulmuştur: $V_S = 15$ V’luk kaynağa seri bağlı iki eşit direnç ($R$) vardır ve çıkış $V_O$ alt dirençten alınır. Devre tahtası yerleşimi [[f:bbd]]’de görülmektedir. Aynı devre üç direnç değeri için ($R = 470\\ \\Omega,\\ 100\\ \\mathrm{k\\Omega},\\ 10\\ \\mathrm{M\\Omega}$) yalnızca dirençler değiştirilerek kullanılmıştır.", align="j")
    D.fig("bbd", a("bb_bol.png"), "Gerilim bölücü devrenin devre tahtası yerleşimi. Güç kaynağı 15 V’a ayarlıdır; $V_O$ düğümünü multimetre ve osiloskop ölçer (iki alet aynı düğüme bağlıdır). Çizimde 470 Ω’luk dirençler gösterilmiştir.", 14.0)
    D.h(3, "Kuramsal Hesap")
    D.p("İki eşit direnç ideal bir bölücü oluşturduğundan beklenen çıkış gerilimi direnç değerinden bağımsızdır:", align="j", keep=True)
    D.eq(r"V_O=V_S\,\frac{R}{R+R}=\frac{15\ \mathrm{V}}{2}=7{,}5\ \mathrm{V}", "div")
    D.p("Ölçü aleti $V_O$ düğümüne bağlanınca alt dirence paralel bir $R_{ic}$ iç direnci girer. Alt direncin yerini $R_p = R R_{ic}/(R+R_{ic})$ alır ve çıkış şuna düşer:", align="j", keep=True)
    D.eq(r"V_O=V_S\,\frac{R_p}{R+R_p},\qquad R_p=\frac{R\,R_{ic}}{R+R_{ic}}", "load")
    D.p("Multimetrenin giriş direnci, cihazla birlikte verilen kılavuzda DA gerilim için yaklaşık 10 MΩ olarak verilmiştir [1]. Osiloskop girişi ise Tektronix kılavuzuna göre 1 MΩ ±%2 ile 20 pF ±3 pF’ın paralel bağlantısıdır [2]. Örnek olarak $R = 100\\ \\mathrm{k\\Omega}$ ve multimetre için ($R_{ic} = 10\\ \\mathrm{M\\Omega}$) [[e:load]] sayılarla yazılır:", align="j", keep=True)
    D.eq(r"R_p=\frac{100\cdot10\,000}{100+10\,000}\ \mathrm{k\Omega}=99{,}01\ \mathrm{k\Omega},\qquad V_O=15\cdot\frac{99{,}01}{100+99{,}01}=7{,}463\ \mathrm{V}", "loadex")
    D.p("Aynı hesap osiloskop için ($R_{ic} = 1\\ \\mathrm{M\\Omega}$) ve diğer dirençler için yapıldığında [[t:t3k]]’teki değerler elde edilmiştir; örneğin $R = 10\\ \\mathrm{M\\Omega}$ ve multimetre için $R_p = 5\\ \\mathrm{M\\Omega}$ ve $V_O = 15\\cdot5/(10+5) = 5{,}0$ V bulunur.", align="j")
    rows = []
    for R, nm in ((470, "470 Ω"), (100e3, "100 kΩ"), (10e6, "10 MΩ")):
        for an, Ri in (("Multimetre (10 MΩ)", 10e6), ("Osiloskop (1 MΩ)", 1e6)):
            Rp_ = R * Ri / (R + Ri); rows.append([nm, an, n(Rp_ / 1e3, 2), n(loaded(R, Ri), 3)])
    D.tab("t3k", ["R", "Alet (iç direnç)", "$R_p$ (kΩ)", "$V_O$ (V)"], rows, "Ölçü aletinin iç direncinin kuramsal etkisi ($V_S = 15$ V, iki eşit direnç; ideal değer 7,5 V)", [2.4, 4.6, 3.2, 3.2])
    D.h(3, "Ölçümler")
    D.fig("fdmm", a("f_dmm.jpg"), "Multimetre okumaları (soldan sağa): $470\\ \\Omega$ için 7,4 V; $100\\ \\mathrm{k\\Omega}$ için 6,5 V; $10\\ \\mathrm{M\\Omega}$ için 0,9 V.", 15.5)
    D.fig("fo1", a("p07.jpg"), "Osiloskop ekranı, $R = 470\\ \\Omega$: DA 7,40 V (en küçük 7,40 V, en büyük 7,60 V, tepeden tepeye 200 mV).", 13.5)
    D.fig("fo2", a("p11.jpg"), "Osiloskop ekranı, $R = 100\\ \\mathrm{k\\Omega}$: DA, en küçük 7,20 V, en büyük 7,40 V, tepeden tepeye 200 mV; osiloskop değeri olarak 7,4 V alınmıştır.", 13.5)
    D.fig("fo3", a("p09.jpg"), "Osiloskop ekranı, $R = 10\\ \\mathrm{M\\Omega}$: 49,998 Hz’lik sinüs; en küçük −12,0 V, en büyük 9,40 V, tepeden tepeye 21,4 V.", 13.5)
    rows = [["470 Ω", "7,5", "7,4", "7,40"],
            ["100 kΩ", "7,5", "6,5", "7,4"],
            ["10 MΩ", "7,5", "0,9", "9,40 (dalganın en büyük değeri; sinyal 50 Hz, 21,4 V tepeden tepeye)"]]
    D.tab("t3", ["R", "Beklenen $V_O$ (V)", "Multimetre (V)", "Osiloskop (V)"], rows, "Gerilim bölücü ölçümleri (föy Tablo 3 [3])", [2.4, 3.2, 3.0, 6.3])
    D.h(3, "Sorular")
    D.p("**Soru 1: Teorik ve ölçülen $V_O$ arasında fark gözlendi mi? Nedenleri nelerdir?**", align="j", keep=True)
    D.p("Fark vardır ve direnç büyüdükçe çok büyümüştür. $R = 470\\ \\Omega$ iken multimetre 7,4 V, osiloskop 7,40 V göstermiştir; beklenen 7,5 V olduğundan fark $(7{,}5-7{,}4)/7{,}5\\times100 = 1{,}3\\,\\%$’tür. Bu değerde fark iç dirençten gelmez, çünkü iç direncin etkisi $R/R_{ic} = 470/10^{7} = 0{,}005\\,\\%$ mertebesindedir; multimetrenin 20 V kademesindeki doğruluğu ±(%0,7 + 3 basamak) = ±(0,052 + 0,03) V ≈ ±0,08 V olduğundan 7,4 V okuması 7,32–7,48 V aralığını temsil eder. Fark esas olarak iki direncin tam eşit olmamasından gelir: ölçülen $R_1 = 464\\ \\Omega$, nominal değerden $(470-464)/470\\times100 = 1{,}3\\,\\%$ küçüktür. $R = 100\\ \\mathrm{k\\Omega}$ iken multimetre 6,5 V göstermiştir; bu beklenenden $(7{,}5-6{,}5)/7{,}5\\times100 = 13\\,\\%$ düşüktür, osiloskop ise 7,4 V ($1{,}3\\,\\%$ düşük) göstermiştir; yani iki alet aynı düğümde 0,9 V farklı okumuştur. $R = 10\\ \\mathrm{M\\Omega}$ iken multimetre 0,9 V göstermiş, bu beklenen değerin $0{,}9/7{,}5 = 12\\,\\%$’si olmuştur; osiloskopta ise DA değer yerine 50 Hz’lik büyük bir sinüs görülmüştür. Farkların nedeninin ölçü aletlerinin iç direnci olduğu düşünülmektedir [[e:load]]. Kılavuzdaki 10 MΩ ile hesaplanan değerler $R = 100\\ \\mathrm{k\\Omega}$ için 7,46 V, $R = 10\\ \\mathrm{M\\Omega}$ için 5,0 V idi ([[t:t3k]]); oysa 6,5 V ve 0,9 V okunmuştur. Yani multimetre bu ölçümlerde kılavuzdaki 10 MΩ’dan çok daha büyük bir yük gibi davranmıştır. Bu yükün büyüklüğü, ölçülen değerlerden aşağıda hesaplanmaktadır:", align="j")
    D.p("**Ölçülen değerlerden iç direncin bulunması.** [[e:load]]’i $R_{ic}$ için çözülür. $k = V_O/(V_S - V_O)$ tanımıyla ve iki direncin eşit olduğu kabul edilerek $R_p = kR$ olur ve:", align="j", keep=True)
    D.eq(r"R_{ic}=\frac{R\,R_p}{R-R_p}=\frac{k\,R}{1-k},\qquad k=\frac{V_O}{V_S-V_O}", "ric")
    D.p("Multimetre, $R = 99{,}1\\ \\mathrm{k\\Omega}$ ve $V_O = 6{,}5$ V için:", align="j", keep=True)
    D.eq(r"k=\frac{6{,}5}{15-6{,}5}=0{,}7647,\qquad R_p=kR=0{,}7647\cdot99{,}1\ \mathrm{k\Omega}=75{,}78\ \mathrm{k\Omega}", "ric1")
    D.eq(r"R_{ic}=\frac{99{,}1\cdot75{,}78}{99{,}1-75{,}78}\ \mathrm{k\Omega}=322\ \mathrm{k\Omega}\approx0{,}32\ \mathrm{M\Omega}", "ric1b")
    D.p("Multimetre, $R = 10{,}30\\ \\mathrm{M\\Omega}$ ve $V_O = 0{,}9$ V için:", align="j", keep=True)
    D.eq(r"k=\frac{0{,}9}{15-0{,}9}=0{,}06383,\qquad R_p=0{,}06383\cdot10{,}30\ \mathrm{M\Omega}=0{,}6574\ \mathrm{M\Omega}", "ric2")
    D.eq(r"R_{ic}=\frac{10{,}30\cdot0{,}6574}{10{,}30-0{,}6574}\ \mathrm{M\Omega}=0{,}70\ \mathrm{M\Omega}", "ric2b")
    D.p("Osiloskop, $R = 99{,}1\\ \\mathrm{k\\Omega}$ ve $V_O = 7{,}4$ V için:", align="j", keep=True)
    D.eq(r"k=\frac{7{,}4}{15-7{,}4}=0{,}9737,\qquad R_p=0{,}9737\cdot99{,}1\ \mathrm{k\Omega}=96{,}49\ \mathrm{k\Omega}", "ric3")
    D.eq(r"R_{ic}=\frac{99{,}1\cdot96{,}49}{99{,}1-96{,}49}\ \mathrm{k\Omega}=3{,}7\ \mathrm{M\Omega}", "ric3b")
    D.p("Ekranın son basamağı olan ±0,05 V’un bu sonuçlara etkisi: multimetre için $0{,}30$–$0{,}34\\ \\mathrm{M\\Omega}$ ve $0{,}66$–$0{,}75\\ \\mathrm{M\\Omega}$; osiloskop için $2{,}4$–$7{,}4\\ \\mathrm{M\\Omega}$ (yüksek iç dirençlerde sonuç ekran basamağına çok duyarlıdır).", align="j")
    D.p("**Yorum.** Hesaba göre multimetre bu ölçümlerde devreye yaklaşık $0{,}3$–$0{,}7\\ \\mathrm{M\\Omega}$’luk bir yük gibi davranmıştır; bu, kılavuzdaki $10\\ \\mathrm{M\\Omega}$’dan yaklaşık 15–30 kat küçüktür. İki sonucun birbirinden farklı çıkması (0,32 ve 0,70 $\\mathrm{M\\Omega}$) $R_{ic}$’nin direnç değerlerine (özellikle ölçülmeyen ikinci dirence) çok duyarlı olmasındandır. Bu farkın fiziksel nedeni belirlenememiştir; bunun için aletin bilinen bir dirençle (örneğin $1\\ \\mathrm{M\\Omega}$) bir kaynağa seri bağlanıp [[e:load]]’in ters çözülmesi gerekir. Osiloskop $R = 100\\ \\mathrm{k\\Omega}$ iken yalnızca %1,3 düşük okumuştur. Kılavuza [2] göre 1 MΩ’luk girişle 7,14 V okunması gerekirdi; 10× uçla (uç dâhil toplam giriş 10 MΩ) ise 7,46 V okunurdu. Okunan 7,4 V ikinciye yakındır; uç ayarı deney sırasında kaydedilmediği için bu kesin olarak söylenemez.", align="j")
    D.p("**Soru 2: Multimetre ve osiloskop aynı $V_O$ noktasında farklı değer gösterdi mi? Neden?**", align="j", keep=True)
    D.p("Evet, $R = 100\\ \\mathrm{k\\Omega}$ ve $R = 10\\ \\mathrm{M\\Omega}$ iken. Nedeni, iki aletin devreye farklı iç direnç göstermesidir: alt dirence paralel giren direnç ne kadar küçükse düğüm gerilimi o kadar düşer [[e:load]]. $R = 100\\ \\mathrm{k\\Omega}$ iken iç direnci yüksek görünen alet (osiloskop, 7,4 V) beklenene yakın, iç direnci düşük görünen alet (multimetre, 6,5 V) belirgin biçimde düşük okumuştur. $R = 10\\ \\mathrm{M\\Omega}$ iken fark daha da büyüktür: multimetre 0,9 V göstermiş; osiloskopta ise DA değer yerine, en büyük değeri 9,40 V olan 50 Hz’lik bir sinüs görülmüştür. Bu sinüs, şebekenin yüksek empedanslı düğüme kapasitif olarak kattığı paraziti gösterir: düğümün direnci (bu durumda $10\\ \\mathrm{M\\Omega}\\parallel10\\ \\mathrm{M\\Omega} = 5\\ \\mathrm{M\\Omega}$) büyük olunca aynı küçük kaçak akım büyük bir gerilim doğurur. Buradaki 9,40 V bir DA değeri değil dalganın en büyük anlık değeridir (en küçük −12,0 V, tepeden tepeye 21,4 V); bu nedenle 7,5 V ile doğrudan karşılaştırılamaz. Multimetre salınımı ortalayıp tek bir sayı gösterdiği için iki aletin buradaki farkı aslında iki ayrı olgunun farkıdır.", align="j")
    D.p("**Soru 3: İç dirençler karşılaştırıldığında, iç direncin devre direncine göre büyüklüğü sonucu nasıl etkiler?**", align="j", keep=True)
    D.p("Ölçü aleti devreye paralel girdiğinden ölçülen düğümün direnci $R$’den $R\\parallel R_{ic}$’ye düşer. Hata $R/R_{ic}$ oranına bağlıdır: $R_{ic} \\gg R$ ise hata ihmal edilebilir, $R_{ic} \\approx R$ ise gerilim yaklaşık yarıya iner, $R_{ic} \\ll R$ ise okuma sıfıra yaklaşır. Ölçümler bunu göstermiştir: multimetrenin görünen iç direnci yaklaşık $0{,}3$–$0{,}7\\ \\mathrm{M\\Omega}$ olduğundan $R = 470\\ \\Omega$ iken ($R/R_{ic} \\approx 470/0{,}32\\times10^{6} = 1{,}5\\times10^{-3}$) etki görülmemiştir; $R = 100\\ \\mathrm{k\\Omega}$ iken ($R/R_{ic} \\approx 100/322 = 0{,}31$) okuma 7,5 V yerine 6,5 V’a, $R = 10\\ \\mathrm{M\\Omega}$ iken ($R/R_{ic} \\approx 10{,}3/0{,}70 = 15$) 0,9 V’a düşmüştür. Kural olarak ölçü aletinin iç direnci, ölçülen düğümün Thevenin direncinin en az 100 katı olmalıdır. Bu sağlanamıyorsa yüklü değer [[e:load]] ile hesaplanmalı, daha yüksek iç dirençli bir alet (veya 10× osiloskop ucu) kullanılmalı ya da düğümün direnci küçültülmelidir.", align="j")

    # ---- 3
    D.h(2, "Wheatstone Köprüsü")
    D.h(3, "Devre ve Devre Tahtası Yerleşimi")
    D.p("Föydeki Şekil 2’deki köprü [3] $V_S = +15$ V ile beslenmiştir; $R_1 = R_2 = 470\\ \\Omega$ (renk kodu) alınmış, $R_3$ yerine potansiyometre, $R_x$ yerine laboratuvar asistanının verdiği bilinmeyen direnç bağlanmıştır. Devre tahtası yerleşimi [[f:bbw]]’de görülmektedir. $V_B$, $R_1$–$R_3$ ortak düğümü ile $R_2$–$R_x$ ortak düğümü arasındaki gerilimdir.", align="j")
    D.fig("bbw", a("bb_whe.png"), "Wheatstone köprüsünün devre tahtası yerleşimi. Potansiyometre $R_3$ yerine, bilinmeyen direnç $R_x$ yerine bağlanır; $V_B$ multimetreyle iki orta düğüm arasından ölçülür.", 14.0)
    D.h(3, "Kuramsal Hesap")
    D.p("Sol kolun orta düğümü $V_L = V_S\\,R_3/(R_1+R_3)$, sağ kolun orta düğümü $V_R = V_S\\,R_x/(R_2+R_x)$ gerilimindedir. Köprü dengedeyken $V_B = V_L - V_R = 0$ olur ve bu koşul kaynak geriliminden bağımsızdır:", align="j", keep=True)
    D.eq(r"V_B=V_S\left(\frac{R_3}{R_1+R_3}-\frac{R_x}{R_2+R_x}\right)=0\;\Rightarrow\;R_1R_x=R_2R_3\;\Rightarrow\;R_x=\frac{R_2R_3}{R_1}", "bridge")
    D.p("Dengenin kaynak geriliminden bağımsız olması köprünün asıl avantajıdır: sonuç $V_S$’in dalgalanmasından etkilenmez, yalnızca direnç oranlarına bağlıdır. Ölçülen değerler ($R_1 = 464\\ \\Omega$, $R_2 = 456\\ \\Omega$, denge anındaki $R_3 = 3{,}22\\ \\mathrm{k\\Omega}$) kullanılınca:", align="j", keep=True)
    D.eq(r"R_x=\frac{456\ \Omega\cdot3220\ \Omega}{464\ \Omega}=\frac{1\,468\,320}{464}\ \Omega=3164{,}5\ \Omega", "rx")
    D.h(3, "Ölçümler")
    D.fig("fwh", a("f_whe.jpg"), "Üst sıra: $R_1$ ve $R_2$ ölçümleri (464 Ω ve 456 Ω) ve devreden çıkarılmış potansiyometrenin ($R_3$) ölçümü, $3{,}22\\ \\mathrm{k\\Omega}$. Alt sıra: denge anında $V_B = 0{,}00$ V, $R_x$’in tek başına ölçümü ($3{,}26\\ \\mathrm{k\\Omega}$) ve devre tahtası.", 15.5)
    D.p("Köprü, $V_B = 0$ olana kadar potansiyometre çevrilerek dengelenmiştir; sonra potansiyometre devreden çıkarılarak multimetreyle ölçülmüş ve $R_3 = 3{,}22\\ \\mathrm{k\\Omega}$ bulunmuştur. $R_x$ ayrıca tek başına multimetreyle ölçülmüş ve $3{,}26\\ \\mathrm{k\\Omega}$ bulunmuştur. Üzerindeki renk kodu $3{,}3\\ \\mathrm{k\\Omega}$’dur. Föyde $R_x$ ile $R_3$’ün tanımları arasında bir karışıklık olduğu fark edilmiş; Tablo 4’te Wheatstone yöntemi için formülden ([[e:bridge]]) hesaplanan $R_x$ kullanılmıştır.", align="j")
    rows = [["Renk kodu (3,3 kΩ ± %5)", "3.300", "0"],
            ["Multimetre ölçümü", "3.260", pc(pct(rxd, rc))],
            ["Wheatstone köprüsü ölçümü ($R_x = R_2R_3/R_1$)", n(rx, 1), pc(pct(rx, rc))]]
    D.tab("t4", ["Yöntem", "Direnç değeri (Ω)", "Renk kodundan fark (%)"], rows, "$R_x$ direncinin değeri ve karşılaştırılması (föy Tablo 4 [3])", [7.4, 3.6, 3.8])
    D.p("Renk kodunun ±%5 tolerans aralığı $3300\\cdot0{,}95 = 3135\\ \\Omega$ ile $3300\\cdot1{,}05 = 3465\\ \\Omega$ arasındadır; iki ölçüm de bu aralıktadır. Farklar şöyle bulunur:", align="j", keep=True)
    D.eq(r"\text{Multimetre:}\ \frac{3260-3300}{3300}\times100=-1{,}21\,\%,\qquad \text{Köprü:}\ \frac{3164{,}5-3300}{3300}\times100=-4{,}11\,\%", "farkrx")
    D.h(3, "Yorum")
    D.p("**Köprü ile multimetre aynı mıdır?** Köprüyle 3.165 Ω, multimetreyle 3.260 Ω bulunmuştur; fark $(3260-3164{,}5)=95{,}5\\ \\Omega$, yani %3,0’dır. Bu farkın ölçü aletinin doğruluğu içinde kalıp kalmadığı kılavuzdaki değerlerle incelenmiştir (EK-2) [1]: direnç ölçümünün doğruluğu 2 kΩ ve 20 kΩ kademelerinde ±(%0,8 + 2 basamak)’tır. $R_1 = 464\\ \\Omega$ (basamak 1 Ω) için ±(0,008·464 + 2·1) = ±5,7 Ω, yani %1,2; $R_2 = 456\\ \\Omega$ için ±5,6 Ω, yani %1,2; $R_3 = 3{,}22\\ \\mathrm{k\\Omega}$ (basamak 10 Ω) için ±(0,008·3220 + 2·10) = ±45,8 Ω, yani %1,4. $R_x = R_2R_3/R_1$ olduğundan bağıl belirsizlikler en kötü durumda toplanır: %1,2 + %1,2 + %1,4 = %3,9, yani $3164{,}5\\cdot0{,}039 = \\pm123\\ \\Omega$. Köprü sonucu $3041$–$3288\\ \\Omega$ aralığında kalır ve multimetrenin 3.260 Ω’u bu aralıktadır; yani iki ölçüm arasındaki fark aletin kılavuzdaki doğruluğuyla açıklanabilir. Bunlara ek olarak devre tahtasındaki kontak ve jumper dirençleri ($R_3$ devreden çıkarılıp ölçülünce ölçüme girmez, köprü dengelenirken kolun içindedir) ve potansiyometre sürgüsünün temas direnci de farka katkı yapmış olabilir. $V_B$ ekranda 0,00 V okunduğundan denge hatası en çok ±5 mV’tur ve bu $R_3$’te yaklaşık %0,3’e karşılık gelir; yani denge hatası fark için yeterli değildir.", align="j")
    D.p("**Ölçümler renk koduyla uyumlu mu?** Evet: multimetre %s, köprü %s saptamış ve ikisi de %%5 tolerans aralığının içinde kalmıştır. Renk kodunun bir hedef değer olduğu, gerçek değerin ise bu hedefin etrafında dağıldığı burada da görülmüştür." % (pc(pct(rxd, rc)), pc(pct(rx, rc))), align="j")

    # ---- 4
    D.h(2, "Dijital-Analog Çevirici (DAC)")
    D.h(3, "Devre ve Devre Tahtası Yerleşimi")
    D.p("Föydeki Şekil 3’teki [3] 3 bitlik R-2R merdiven DAC’ında her bit $2\\ \\mathrm{k\\Omega}$’luk bir giriş direnciyle merdivene bağlanır; merdiven iki adet $1\\ \\mathrm{k\\Omega}$’luk seri direnç ve $2\\ \\mathrm{k\\Omega}$’luk bir sonlandırma direncinden, çıkış ise $R_L = 1\\ \\mathrm{k\\Omega}$’luk yük direncinden oluşur. Mantık “1” için girişe 16 V, “0” için toprağa bağlanmıştır. Devre tahtası yerleşimi [[f:bbc]]’dedir.", align="j")
    D.fig("bbc", a("bb_dac.png"), "3 bitlik R-2R DAC’ın devre tahtası yerleşimi. $R_{i1}, R_{i2}, R_{i3} = 2\\ \\mathrm{k\\Omega}$ (giriş), $R_a = R_b = 1\\ \\mathrm{k\\Omega}$, $R_t = 2\\ \\mathrm{k\\Omega}$, $R_L = 1\\ \\mathrm{k\\Omega}$. Turuncu jumperlar girişleri 16 V rayına (mantık 1, kod 111) bağlar; bir bit 0 olacaksa jumper alt rayına (toprağa) taşınır. Multimetre $V_O$ düğümündedir.", 14.0)
    D.h(3, "Kuramsal Hesap")
    D.p("Devre doğrusal olduğundan çıkış, her bitin tek başına yarattığı çıkışların toplamıdır (süperpozisyon). Giriş dirençlerinin merdivenle birleştiği üç düğüm vardır: $A$ ($V_O$ düğümü), $B$ ve $C$. Düğüm denklemleri ($G_i = 1/2\\ \\mathrm{k\\Omega}$, $b_k \\in \\{0,1\\}$):", align="j", keep=True)
    D.eq(r"\begin{bmatrix}G_i+G_a+G_L&-G_a&0\\-G_a&G_i+G_a+G_b&-G_b\\0&-G_b&G_i+G_b+G_t\end{bmatrix}\begin{bmatrix}V_A\\V_B\\V_C\end{bmatrix}=G_i\,V_{\mathrm{mantık}}\begin{bmatrix}b_2\\b_1\\b_0\end{bmatrix}", "dacm")
    D.p("Sayılar yerine konulursa: $G_i = 1/2\\ \\mathrm{k\\Omega} = 0{,}5$ mS, $G_a = G_b = G_L = 1$ mS, $G_t = 0{,}5$ mS ve $G_iV_{\\mathrm{mantık}} = 0{,}5\\ \\mathrm{mS}\\cdot16\\ \\mathrm{V} = 8$ mA olur. Matris ve sağ taraf (mS ve mA birimlerinde, gerilimler V):", align="j", keep=True)
    D.eq(r"\begin{bmatrix}2{,}5&-1&0\\-1&2{,}5&-1\\0&-1&2\end{bmatrix}\begin{bmatrix}V_A\\V_B\\V_C\end{bmatrix}=8\begin{bmatrix}b_2\\b_1\\b_0\end{bmatrix}", "dacs")
    D.p("Giriş $100$ için ($b_2=1$, diğerleri 0) üçüncü denklemden $V_C = V_B/2$; ikinci denklemden $-V_A + 2{,}5V_B - V_B/2 = 0$, yani $V_A = 2V_B$; birinci denklemden $2{,}5\\cdot2V_B - V_B = 8$, yani $V_B = 2$ V, $V_A = V_O = 4$ V bulunur. Giriş $011$ için ($b_1 = b_0 = 1$) üçüncü denklemden $V_C = (8+V_B)/2$; ikinci denklemden $-V_A + 2{,}5V_B - (8+V_B)/2 = 8$, yani $V_A = 2V_B - 12$; birinci denklemden $2{,}5(2V_B-12) - V_B = 0$, yani $V_B = 7{,}5$ V, $V_A = V_O = 3$ V bulunur. Devre doğrusal olduğundan $111$ için çıkış ikisinin toplamıdır: $V_O = 4+3 = 7$ V. Aynı hesap yalnızca $b_0 = 1$ için yapılırsa $V_O = 1$ V bulunur; yani devre $V_O = (4b_2+2b_1+b_0)\\times1\\ \\mathrm{V}$ dönüşümünü yapar.", align="j")
    D.h(3, "Ölçümler ve Karşılaştırma")
    D.fig("fdac", a("f_dac.jpg"), "DAC çıkış gerilimleri: 100 için $4{,}09$ V, 011 için $3{,}27$ V, 111 için $7{,}34$ V.", 15.5)
    rows = []
    for nm, k, m in (("100", 4.0, 4.09), ("011", 3.0, 3.27), ("111", 7.0, 7.34)):
        rows.append([nm, n(k, 3), n(m, 2), n(m - k, 2), pc(pct(m, k))])
    D.tab("t5", ["Giriş", "Kuramsal $V_O$ (V)", "Ölçülen $V_O$ (V)", "Mutlak fark (V)", "Fark (%)"], rows, "DAC çıkış gerilimleri: kuramsal ve ölçülen", [2.0, 3.4, 3.4, 3.0, 2.4])
    D.h(3, "Yorum")
    D.p("Ölçülen değerlerin hepsi beklenenin üstünde çıkmıştır: $(4{,}09-4)/4 = 2{,}3\\,\\%$, $(3{,}27-3)/3 = 9{,}0\\,\\%$ ve $(7{,}34-7)/7 = 4{,}9\\,\\%$. Ölçümler birbiriyle tutarlıdır: $100$ ve $011$ okumalarının toplamı $4{,}09 + 3{,}27 = 7{,}36$ V, $111$ için okunan değer ise $7{,}34$ V’tur ($\\%0{,}3$ fark); yani devre doğrusal davranmıştır. Ağırlıkların oranı $4{,}09/3{,}27 = 1{,}25$ çıkmıştır, beklenen oran $4/3 = 1{,}33$’tür: bir bitin ağırlığı diğerine göre kaymıştır. Olası nedenler: (a) Direnç toleransları. Yedi direncin her biri ±%5 toleransın bir ucuna ($0{,}95$ ya da $1{,}05$ katına) konularak $2^7 = 128$ kombinasyonun hepsi için düğüm denklemleri çözülmüştür; çıkışlar $100$ için $3{,}71$–$4{,}31$ V, $011$ için $2{,}74$–$3{,}28$ V, $111$ için $6{,}59$–$7{,}42$ V aralığında kalmıştır. Ölçülen üç değer de bu aralıktadır; ancak $3{,}27$ V üst sınıra ($3{,}28$ V) çok yakındır, yani bu sonuç için dirençlerin çoğunun aynı yönde toleranslarının ucunda olması gerekir. (b) “16 V”un gerçekte 16 V olmaması: örneğin 16,3 V olsa bütün çıkışlar $16{,}3/16 = 1{,}019$ kat, yani %1,9 artardı, fakat oranlar bozulmazdı. (c) $2\\ \\mathrm{k\\Omega}$ gibi değerlerin seri-paralel bağlamayla elde edilmesi hâlinde her bağlantı kontak direnci ekler ve bit ağırlıklarını bozar. (d) Kaynağın yük altında geriliminin düşmesi. Dirençler tek tek ölçülmediği için hangi nedenin baskın olduğu söylenemez; tek tek ölçülseydi ölçülen değerler düğüm denklemlerine konularak sapmanın kaynağı bulunabilirdi.", align="j")

    # ================= SONUÇLAR
    D.h(1, "Sonuçlar")
    D.p("**Genel değerlendirme.** Seri ve paralel bağlantı kuralları ölçümle doğrulanmıştır: seri ölçüm toplamdan %0,48, paralel ölçüm hesaptan %0,39 farklı çıkmış ve ikisi de ölçü aletinin kılavuzdaki doğruluğu içindedir. Gerilim bölücüde asıl bulgu, ölçü aletlerinin iç direncinin sonucu belirlemesidir: $R = 470\\ \\Omega$ iken iki alet de beklenene yakın göstermiştir (7,4 V ve 7,40 V; beklenen 7,5 V); $R = 100\\ \\mathrm{k\\Omega}$ iken multimetre 6,5 V, osiloskop 7,4 V göstermiştir; $R = 10\\ \\mathrm{M\\Omega}$ iken multimetre 0,9 V göstermiş, osiloskop ekranında ise 50 Hz’lik parazit (en büyük 9,40 V, tepeden tepeye 21,4 V) görülmüştür. Ölçümlerden multimetrenin görünen iç direnci yaklaşık $0{,}3$–$0{,}7\\ \\mathrm{M\\Omega}$ hesaplanmıştır; kılavuz yaklaşık 10 MΩ vermektedir [1]. Wheatstone köprüsüyle bilinmeyen direnç $3165\\ \\Omega$ bulunmuştur; multimetreyle ölçülen $3260\\ \\Omega$’dan %3,0 farklıdır, bu fark aletlerin doğruluğuyla açıklanabilir ve ikisi de renk kodunun ($3{,}3\\ \\mathrm{k\\Omega}$ ±%5) tolerans aralığındadır. DAC çıkışları beklenenden %2,3–%9 yüksek ölçülmüştür; üç değer de ±%5 tolerans için hesaplanan uç durum aralıklarının içindedir.", align="j")
    D.p("**Eksik kalan noktalar.** (i) Multimetrenin $R = 100\\ \\mathrm{k\\Omega}$ ve $R = 10\\ \\mathrm{M\\Omega}$ iken kılavuzdaki 10 MΩ’dan çok küçük görünen iç direncinin nedeni belirlenememiştir; bilinen bir dirençle ayrıca ölçüm yapmak gerekir. (ii) Osiloskop ucunun 1× mi 10× mu olduğu kaydedilmemiştir. (iii) DAC dirençleri tek tek ölçülmemiştir.", align="j")
    D.p("**Kazanımlar.** Seri-paralel direnç hesabı ve ölçümü; ölçü aletinin yük etkisinin hesaplanması; osiloskop ve multimetrenin birlikte kullanımı ve 50 Hz parazitin tanınması; köprü yöntemi; DAC ağırlıklarının süperpozisyonla hesabı; devre tahtası yerleşimi ve ölçümlerinin beklenen değerle yüzde farkla karşılaştırılması.", align="j")

    D.h(1, "Kaynaklar")
    refs_block(D, ["UNI-T. (t.y.). *UT33+ series palm size multimeter operating manual* [Cihazla birlikte verilen basılı kılavuz, İngilizce]. UNI-TREND Technology (China) Co., Ltd.",
                   "Tektronix. (t.y.). *TBS1000 series digital storage oscilloscopes service manual* (Parça No. 077077201, Rev. B). https://download.tek.com/manual/TBS1000-Series-Oscilloscope-Service-Manual-077077201_RevB.pdf",
                   "TOBB Ekonomi ve Teknoloji Üniversitesi. (2026). *ELE 201 L – Devre Analizi I Laboratuvarı, Deney 1 Föyü*. Ankara: TOBB ETÜ, Elektrik – Elektronik Mühendisliği Bölümü."])

    D.h(1, "Ekler")
    D.h(3, "EK-1: Kullanılan Aletler")
    D.tab("tal", ["Alet", "Kullanım"], [["UNI-T UT33D+ multimetre", "Direnç ve gerilim ölçümleri"], ["Tektronix TBS 1022 osiloskop", "Gerilim bölücü çıkışı"], ["DA güç kaynağı", "15 V ve 16 V beslemeler"], ["Devre tahtası, dirençler, potansiyometre", "Bütün devreler"]], "Deneyde kullanılan aletler", [7.0, 7.0], size=10)
    D.h(3, "EK-2: Ölçü Aletlerinin Kılavuz Sayfaları")
    D.p("Rapordaki iç direnç ve doğruluk değerleri, multimetrenin kutusundan çıkan basılı İngilizce kılavuzdan [1] ve osiloskop için Tektronix kılavuzundan [2] alınmıştır. İlgili sayfalar aşağıdadır.", align="j")
    D.fig("ek1", a("ek_ut33_dcv.png"), "UNI-T UT33D+ kılavuzu [1], “IX. Technical specification”, 1. DC voltage. 20,00 V kademesinde doğruluk ±(%0,7 + 3 basamak), çözünürlük 0,01 V; “Input impedance: about 10 MΩ”.", 13.0)
    D.fig("ek2", a("ek_ut33_res.png"), "Aynı kılavuz [1], 3. Resistance. 2000 Ω ve 20,00 kΩ kademelerinde ±(%0,8 + 2 basamak), 20,00 MΩ kademesinde ±(%1,2 + 3 basamak). Altta: “Measurement result = reading of resistor − reading of shorted test leads”.", 13.0)
    D.fig("ek3", a("ek_tbs.png"), "Tektronix TBS1000 serisi servis kılavuzu [2], sayfa 1-1, Tablo 1-1 (TBS1022 dâhil bütün modeller için geçerli). “Input Impedance, DC Coupled: 1 MΩ ±2% in parallel with 20 pF ±3 pF.”", 13.5)
    return D

if __name__ == "__main__":
    B = os.path.join(os.path.dirname(OUT), "build"); os.makedirs(B, exist_ok=True)
    D = build(); f = os.path.join(B, "ELE201L_Deney1_Laboratuvar_Raporu.docx"); D.save(f)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", OUT, f], capture_output=True, timeout=300); print("ok")
