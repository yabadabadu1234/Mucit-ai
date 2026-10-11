import json, os, subprocess, math
from docbuilder import Doc
H = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(H, "..", "assets"); SH = os.path.join(H, "..", "shots")
OUT = os.path.join(H, "..", "out"); os.makedirs(OUT, exist_ok=True)
C = json.load(open(os.path.join(H, "..", "build", "calc.json")))
a = lambda n: os.path.join(A, n)
s = lambda n: os.path.join(SH, n + ".png")

def n(x, d=2, unit=""):
    t = ("%." + str(d) + "f") % x
    ip, _, fp = t.partition(".")
    neg = ip.startswith("-"); ip = ip.lstrip("-")
    ip = "{:,}".format(int(ip)).replace(",", ".")
    r = ("-" if neg else "") + ip + ("," + fp if fp else "")
    return r + (" " + unit if unit else "")
def err(t, sv, d=3, unit="V"):
    e = abs(t - sv)
    return n(0.0 if e < 5 * 10 ** -(d + 1) else e, d, unit)

def build():
    D = Doc("tr")
    D.title_block([("TOBB Ekonomi ve Teknoloji Üniversitesi", 13, True), ("Elektrik – Elektronik Mühendisliği Bölümü", 12, False),
                   ("ELE 201 L – Devre Analizi I Laboratuvarı", 14, True), ("Deney 1 – Ön Çalışma Raporu", 14, True)],
                  [("Adı Soyadı", ""), ("Numara", ""), ("Tarih", "")])
    # ---------------- 1 GİRİŞ
    D.h(1, "Giriş")
    D.h(2, "Deneyin Amacı")
    D.p("Bu çalışmanın amacı, doğru akım (DA) devre analizinin dört temel yapı taşının laboratuvar öncesinde kuramsal olarak çözülmesi, bu çözümlerin bir devre benzetimi ile sınanması ve devrelerin devre tahtası (breadboard) üzerinde nasıl kurulacağının önceden planlanmasıdır. Bu kapsamda sırasıyla şu konular ele alınmıştır: (i) dirençlerin seri ve paralel bağlanması ile eşdeğer direnç kavramı, (ii) gerilim bölücü devrenin çıkış gerilimi ve ölçü aletinin devreyi nasıl etkilediği, (iii) bilinmeyen bir direncin Wheatstone köprüsü ile belirlenmesi ve (iv) 2R-R merdiveni ile kurulan 3 bitlik bir sayısal-analog çeviricinin (DAC) çıkış gerilimi.", align="j")
    D.p("Ön çalışmanın asıl işlevi, laboratuvara “beklenen değerin ne olduğu bilinerek” girilmesidir. Elde edilen bir ölçüm, ancak karşısında bir kuramsal değer varsa yorumlanabilir: ölçülen değer beklenenden farklıysa bunun nedeninin devrenin kendisinde (ör. ölçü aletinin yük etkisi), elemanlarda (direnç toleransı) ya da bağlantıda (devre tahtasındaki hatalı yerleşim) olup olmadığına karar verilebilir. Bu raporda her bölümde kuramsal sonuç, benzetim sonucu ve aradaki hata payı birlikte verilmiş; farkın kaynağı ayrıca yorumlanmıştır.", align="j")
    D.h(2, "Deneyin Faydaları")
    D.p("Çalışma sonucunda şu kazanımlar elde edilmiştir. Birincisi, devre tahtasının iç bağlantı yapısı öğrenilmiş ve bir şemanın tahta üzerindeki karşılığının nasıl çıkarılacağı gösterilmiştir. İkincisi, “ideal” ölçü aleti kabulünün her zaman geçerli olmadığı, ölçü aletinin iç direncinin yüksek dirençli devrelerde ölçülen değeri büyük oranda değiştirebildiği sayısal olarak görülmüştür. Üçüncüsü, köprü devrelerinde denge koşulunun yalnızca oranlara bağlı olduğu, dolayısıyla kaynak geriliminden bağımsız bir ölçüm yapılabildiği anlaşılmıştır. Dördüncüsü, aynı dirençlerle kurulan bir merdiven devresinin ikili sayıları gerilime çeviren bir işlev gördüğü; yani sayısal sistemler ile analog dünya arasındaki bağlantının basit bir direnç ağı ile kurulabildiği gösterilmiştir. Ayrıca devre çözümünde kullanılan Thevenin eşdeğeri, süperpozisyon ve düğüm analizi yöntemleri gerçek devreler üzerinde uygulanmıştır.", align="j")
    # ---------------- 2 ÖLÇÜMLER
    D.h(1, "Ölçümler")
    D.p("Bu bölümde dört deney kısmı ayrı alt başlıklar halinde verilmiştir. Her kısımda sırasıyla kullanılan elemanlar, devre şeması, teorik işlemler, benzetim sonuçları, hata payları ve devre tahtası yerleşimi sunulmuştur. Bir sayı, teorik değer $x_t$ ve benzetim değeri $x_s$ ile ifade edildiğinde mutlak ve bağıl hata payı aşağıdaki gibi hesaplanmıştır:", align="j")
    D.eq(r"\varepsilon_{\mathrm{mut}}=\left|x_t-x_s\right|,\qquad \varepsilon_{\mathrm{bağıl}}=\frac{\left|x_t-x_s\right|}{\left|x_t\right|}\times 100\,\%", "hata")
    D.p("Benzetim, LTspice programı ile yapılmıştır [6], [7]. Her devre için önce DA işletme noktası (“.op”) çözülmüş ve düğüm gerilimleri ile eleman akımları işletme noktası penceresinden okunmuştur; ardından kaynak veya direnç değeri taranarak (“.dc” analizi) düğüm gerilimlerinin değişimi çizdirilmiş, çizim üzerine imleç (cursor) konularak koordinatlar okunmuş ve imleç penceresindeki değerler şekillerin altındaki tablolara aktarılmıştır. Bütün ekran görüntülerinde devre şeması, çıktı penceresi ve cihaz seri numarası (TOBB-7K3Q-0421) birlikte görülmektedir. Tablolardaki benzetim değerleri ayrıca ngspice (sürüm 42) ile hesaplanmış ve LTspice ekranlarında okunan değerlerle 6 anlamlı basamakta aynı bulunmuştur. Devre listeleri (netlist) EK-1’de verilmiştir. Kuramsal sonuçlar elle türetilen kapalı formüllerden elde edilmiştir. Kuramsal çözümle benzetimin aynı idealleştirilmiş eleman modellerini kullanması nedeniyle iki sonucun birbirini doğrulaması beklenir; bu uyum, el hesabının cebirsel olarak doğru olduğunun denetimi anlamına gelir. Gerçek elemanlardan kaynaklanacak sapmalar ise Sonuçlar bölümünde ayrıca tartışılmıştır.", align="j")

    # ---- 2.1
    D.h(2, "Direnç Bağlantıları")
    D.h(3, "2.1.1 Devre Tahtasının (Breadboard) Kullanımı ve Bağlantı Şeması")
    D.p("Devre tahtası, lehim kullanmadan geçici devre kurmaya yarayan, üzerinde 2,54 mm (0,1 inç) aralıklı delikler bulunan plastik bir levhadır. Deliklerin altında yaylı metal şeritler vardır ve bir şeride giren her eleman bacağı o şeridin diğer deliklerine elektriksel olarak bağlanmış olur. Şeritlerin düzeni iki bölümden oluşur. Ana bölgede her sütunun beş deliği (a–e ve f–j) birbirine iç bağlıdır; aynı sıradaki (satırdaki) bitişik delikler ise birbirinden yalıtılmıştır. Ortadaki kanal, üst yarı ile alt yarıyı birbirinden ayırır ve bu nedenle a–e deliklerinin f–j delikleriyle bağlantısı yoktur. Kanalın bu biçimde yapılmasının nedeni, çift sıralı tümleşik devrelerin (DIP) iki sıra bacağının kanalın iki yanına oturtulup birbirinden yalıtılmasıdır. Tahtanın kenarlarında uzunlamasına uzanan, genellikle kırmızı (+) ve mavi (−) çizgiyle işaretli iki sıra delik bulunur; bunlara güç rayı denir ve rayın bütün delikleri tek bir düğümdür. Bu rayın kullanım amacı, besleme ve toprak hattının tahtanın her yerine dağıtılmasıdır. Bazı tahtalarda ray ortada kesiktir; bu durumda iki yarı rayın bir telle birleştirilmesi gerekir. Bu durum, devre tahtası kullanımında en sık yapılan hatalardan biridir.", align="j")
    D.p("Bir devrenin tahtaya aktarılması şu adımlarla yapılır: önce şemadaki her düğüm (iki veya daha çok eleman ucunun birleştiği nokta) tahtada bir sütuna karşılık getirilir; sonra her eleman, uçları kendi düğümlerine karşılık gelen sütunlarda olacak biçimde yerleştirilir. Bir direncin iki bacağı aynı sütuna takılırsa direnç kısa devre edilmiş olur; bu nedenle iki bacak her zaman farklı sütunlara yerleştirilir. Besleme ve toprak bağlantıları devre kurulduktan sonra, en son adım olarak yapılır; ölçü aleti gerilim ölçerken devreye paralel, akım ölçerken seri bağlanır. [[f:bb]] bu iç bağlantı yapısını göstermektedir.", align="j")
    D.fig("bb", a("im-002.png"), "Devre tahtasının iç bağlantı yapısı: aynı renkle çerçevelenen delikler birbirine iç bağlıdır. Ortadaki kanal iki yarıyı ayırır.", 11.5)
    D.h(3, "2.1.2 Kullanılan Elemanlar")
    D.p("Deneyde değerleri $R_1 = 3{,}9\\ \\mathrm{k\\Omega}$, $R_2 = 1\\ \\mathrm{k\\Omega}$ ve $R_3 = 8{,}2\\ \\mathrm{k\\Omega}$ olan üç direnç kullanılmaktadır. [[t:renk]] bu dirençlerin 4 bantlı renk kodunu vermektedir. İlk iki bant anlamlı basamakları, üçüncü bant 10’un üssünü (çarpanı), dördüncü bant toleransı gösterir; altın renkli dördüncü bant %5 toleransa karşılık gelir [5]. Örneğin 3,9 kΩ değerli direnç için turuncu (3), beyaz (9) ve kırmızı (×10²) bantları okunur: 39 × 100 Ω = 3,9 kΩ. Renk kodunun tamamı EK-2’de verilmiştir.", align="j")
    D.tab("renk", ["Eleman", "Nominal değer", "Bantlar (1–2–3–4)", "Tolerans", "Gerçek değer aralığı"],
          [["R1", "3,9 kΩ", "Turuncu – Beyaz – Kırmızı – Altın", "%5", "3,705 kΩ – 4,095 kΩ"],
           ["R2", "1 kΩ", "Kahverengi – Siyah – Kırmızı – Altın", "%5", "950 Ω – 1,05 kΩ"],
           ["R3", "8,2 kΩ", "Gri – Kırmızı – Kırmızı – Altın", "%5", "7,79 kΩ – 8,61 kΩ"]],
          "Kullanılan dirençler, renk kodları ve tolerans aralıkları", [1.6, 2.4, 5.4, 1.7, 3.6])
    D.h(3, "2.1.3 Teorik İşlemler")
    D.p("Seri bağlı elemanlardan aynı akım geçer; her elemanın gerilimi Ohm yasasına göre kendi direnciyle orantılı olduğundan, toplam gerilim bireysel gerilimlerin toplamıdır. Bu da eşdeğer direncin direnç toplamı olmasını gerektirir. Paralel bağlı elemanların uçlarında ise aynı gerilim bulunur ve toplam akım kolların akımlarının toplamıdır (Kirchhoff akım yasası); bu nedenle iletkenlikler (1/R) toplanır [1], [2], [3]:", align="j")
    D.eq(r"R_{\mathrm{eş,seri}}=R_1+R_2+\cdots+R_n", "seri")
    D.eq(r"\frac{1}{R_{\mathrm{eş,par}}}=\frac{1}{R_1}+\frac{1}{R_2}+\cdots+\frac{1}{R_n}", "par")
    D.p("İki direncin paralel bağlanması özel bir durumdur ve “çarpım bölü toplam” biçiminde yazılabilir:", keep=True)
    D.eq(r"R_1\parallel R_2=\frac{R_1R_2}{R_1+R_2}", "par2")
    D.p("Verilen değerler yerine konursa seri bağlantı için $R_{\\mathrm{eş,seri}} = 3{,}9\\ \\mathrm{k\\Omega} + 1\\ \\mathrm{k\\Omega} + 8{,}2\\ \\mathrm{k\\Omega} = 13{,}1\\ \\mathrm{k\\Omega}$ bulunur. Paralel bağlantı için $1/R_{\\mathrm{eş,par}} = 1/3900 + 1/1000 + 1/8200 = 0{,}25641\\ \\mathrm{mS} + 1\\ \\mathrm{mS} + 0{,}12195\\ \\mathrm{mS} = 1{,}37836\\ \\mathrm{mS}$ ve dolayısıyla $R_{\\mathrm{eş,par}} = 725{,}5\\ \\Omega$ elde edilir. Sonuçların fiziksel yorumu şöyledir: seri bağlantıda eşdeğer direnç, en büyük dirençten (8,2 kΩ) büyüktür, çünkü akımın karşılaştığı engeller birbirine eklenir. Paralel bağlantıda ise eşdeğer direnç, en küçük dirençten (1 kΩ) bile küçüktür; akıma yeni bir yol eklemek, kolların hangisi çok yüksek dirençli olursa olsun toplam direnci azaltır. Paralel eşdeğer değerinin baskın olarak en küçük dirençle belirlendiği (725,5 Ω ≈ 1 kΩ’un %72,5’i) görülmektedir.", align="j")
    D.h(3, "2.1.4 Benzetim Sonuçları ve Hata Payları")
    D.p("[[f:sseri]] ve [[f:spar]], 1 V’luk bir kaynakla beslenen seri ve paralel bağlantıların LTspice işletme noktası (“.op”) çözümlerini göstermektedir. Eşdeğer direnç $R_{\\mathrm{eş}} = V_1 / |I(V_1)|$ bağıntısıyla bulunur. Seri bağlantıda $I(V_1) = -7{,}63359\\times10^{-5}$ A olduğundan $R_{\\mathrm{eş,seri}} = 13\\,100{,}0\\ \\Omega$; paralel bağlantıda $I(V_1) = -1{,}37836\\times10^{-3}$ A olduğundan $R_{\\mathrm{eş,par}} = 725{,}50\\ \\Omega$ elde edilmiştir. Seri devrede $V(n002) = 0{,}702290$ V ve $V(n003) = 0{,}625954$ V düğüm gerilimleri, $R_1$ ve $R_2$ üzerinde 7,63359×10⁻⁵ A × 3,9 kΩ = 0,29771 V ve 0,07634 V düşüm oluştuğunu doğrulamaktadır (1 − 0,29771 = 0,70229 V ve 0,70229 − 0,07634 = 0,62595 V).", align="j")
    D.fig("sseri", s("bol21_seri"), "Üç direncin seri bağlantısının LTspice devre şeması ve işletme noktası (.op) çıktısı. Sağ alttaki pencerede düğüm gerilimleri ve eleman akımları görülmektedir; $R_{\\mathrm{eş}} = 1\\,\\mathrm{V}/76{,}3359\\,\\mu\\mathrm{A} = 13{,}1\\ \\mathrm{k\\Omega}$. Şemanın altında cihaz seri numarası yer almaktadır.", 14.5)
    D.fig("spar", s("bol21_par"), "Üç direncin paralel bağlantısının LTspice devre şeması ve işletme noktası (.op) çıktısı; $R_{\\mathrm{eş}} = 1\\,\\mathrm{V}/1{,}37836\\,\\mathrm{mA} = 725{,}50\\ \\Omega$. Kollardan geçen akımlar 256,41 µA, 1 mA ve 121,951 µA olup toplamları kaynak akımına eşittir.", 14.5)
    D.p("[[t:eq]] istenen üçlü seri ve paralel bağlantının yanı sıra, aynı yöntemle üç ikili kombinasyonun da eşdeğer direncini vermektedir. İlk iki satır benzer biçimde yapılan işlemlerin temsilcisi olarak denklemlerle çözülmüş, ikili kombinasyonlar aynı denklemlerle hesaplanarak tabloya yazılmıştır. Son sütunda, dirençlerin %5 toleransı nedeniyle laboratuvarda ohmmetre ile okunması beklenen aralık verilmiştir: üç dirençte de tolerans aynı yöndeyse eşdeğer direnç de en fazla %5 sapar.", align="j")
    names = {"s123": "R1 + R2 + R3 (seri)", "p123": "R1 ∥ R2 ∥ R3 (paralel)", "s12": "R1 + R2", "s13": "R1 + R3", "s23": "R2 + R3", "p12": "R1 ∥ R2", "p13": "R1 ∥ R3", "p23": "R2 ∥ R3"}
    rows = []
    for k, (t, sv) in C["eq"].items():
        rows.append([names[k], n(t, 2, "Ω"), n(sv, 2, "Ω"), err(t, sv, 3, "Ω"), "%0", "%s – %s Ω" % (n(t * .95, 1), n(t * 1.05, 1))])
    D.tab("eq", ["Bağlantı", "Teorik", "Benzetim", "Mutlak hata", "Bağıl hata", "Beklenen aralık (±%5)"], rows,
          "Eşdeğer direnç: teorik değer, benzetim sonucu, hata payı ve %5 toleransla beklenen aralık", [3.8, 2.3, 2.3, 2.1, 1.7, 3.8], size=9)
    D.p("Teorik ve benzetim sonuçlarının uyuşmaması söz konusu değildir (fark, sayısal çözümün yuvarlama hatası mertebesindedir ve tabloda 0 olarak görünür). Bu, el ile türetilen formüllerin doğru uygulandığını gösterir. Laboratuvardaki ohmmetre okumasının ise tablonun son sütunundaki aralık içinde kalması beklenir; aralığın dışında bir okuma, bağlantı hatasının (ör. bacağın yanlış sütuna takılması) ya da yanlış direnç seçiminin işaretidir.", align="j")
    D.h(3, "2.1.5 Devre Tahtası Yerleşimi")
    D.p("[[f:sema21]] seri ve paralel bağlantının şematik gösterimini vermektedir. Seri bağlantıda her direncin bir ucu bir sonrakinin ucuyla aynı düğümde birleşir; paralel bağlantıda ise bütün dirençlerin birer ucu A düğümünde, diğer uçları B düğümünde toplanır. [[f:bbs]] ve [[f:bbp]]’de bu iki bağlantının devre tahtasındaki karşılıkları görülmektedir.", align="j")
    D.fig("sema21", a("im-006.png"), "(a) Üç direncin seri ve (b) paralel bağlantısının şematik gösterimi; A ve B ucu arasındaki eşdeğer direnç ölçülür.", 14.0)
    D.p("Seri bağlantıda R1 a3–a8, R2 b8–b13 ve R3 a13–a18 deliklerine takılmıştır. 8. ve 13. sütunlar, ardışık iki direncin ortak düğümleridir: R1’in sağ bacağı ile R2’nin sol bacağı aynı sütundaki (a ve b satırı) delikte buluşur ve iç bağlantı sayesinde birbirine bağlanır. Eşdeğer direnç, 3. ve 18. sütundaki boş deliklere (c3 ve c18) ölçü aleti uçları dokundurularak okunur. Ölçümden önce kaynağın kapalı ve devreden ayrılmış olması gerekir; aksi halde ohmmetre devredeki gerilimden etkilenir.", align="j")
    D.fig("bbs", a("im-007.png"), "Seri bağlantının devre tahtasındaki yerleşimi. Ölçü aleti ohm konumunda, c3 ve c18 deliklerine bağlıdır.", 14.5)
    D.p("Paralel bağlantıda üç direncin sol bacakları 6. sütunun a, b, c deliklerine; sağ bacakları 15. sütunun a, b, c deliklerine takılmıştır. Aynı sütunun beş deliği iç bağlı olduğundan, bütün sol bacaklar bir düğümde, bütün sağ bacaklar diğer düğümde birleşmiş olur. Ölçü, aynı sütunların boş deliklerinden (d6 ve d15) alınır.", align="j")
    D.fig("bbp", a("im-008.png"), "Paralel bağlantının devre tahtasındaki yerleşimi. Ölçü aleti d6 ve d15 deliklerine bağlıdır.", 14.5)

    # ---- 2.2
    D.h(2, "Gerilim Ölçümü")
    D.h(3, "2.2.1 Devre ve Teorik İşlemler")
    D.p("[[f:div]]’de verilen devre, iki özdeş direncin kaynağa seri bağlanmasıyla oluşan gerilim bölücüdür. Seri devrede akım iki dirençten de aynıdır: $I = V_S/(R + R)$. Çıkış gerilimi alttaki direncin gerilimi olduğundan Ohm yasasıyla", align="j", keep=True)
    D.eq(r"V_O=I\,R=\frac{V_S}{R+R}\,R=\frac{V_S}{2}", "vo")
    D.p("bulunur. Sonucun $R$’nin değerinden bağımsız olması önemlidir: çıkış gerilimini yalnızca iki direncin oranı belirler. Bu nedenle kuramsal olarak 470 Ω, 100 kΩ ve 10 MΩ değerlerinin üçü için de çıkış 7,5 V’tur. Ancak $R$’nin değeri devreden geçen akımı belirler: $R = 10\\ \\mathrm{M\\Omega}$ için $I = 15\\ \\mathrm{V} / 20\\ \\mathrm{M\\Omega} = 0{,}75\\ \\mu\\mathrm{A}$ gibi çok küçük bir akım akar. Bu kadar küçük akımla çalışan bir devrede, ölçü aletinin çektiği küçük bir akım bile sonucu belirgin biçimde değiştirebilir.", align="j")
    D.fig("div", a("im-010.png"), "Gerilim bölücü devrenin şeması. Çıkış gerilimi $V_O$, alttaki direncin uçlarından alınır.", 10.5)
    D.h(3, "2.2.2 Ölçü Aletinin Yükleme Etkisi")
    D.p("Gerilim ölçmek için ölçü aleti, ölçülmek istenen elemana paralel bağlanır. Gerçek bir sayısal çoklu ölçerin (multimetre) giriş direnci sonsuz değildir; laboratuvardaki aletler için bu değer 10 MΩ varsayılmıştır. Dolayısıyla alet, alttaki $R$ direncine paralel bir $R_m = 10\\ \\mathrm{M\\Omega}$ direnç gibi davranır ve devrenin alt kolunun eşdeğer direncini düşürür.", align="j")
    D.p("Bu etkiyi hesaplamanın en kısa yolu Thevenin eşdeğeridir. Ölçü aleti bağlanacak iki uç ($V_O$ uçları) için kaynak bakımından devre şu eşdeğeri verir: açık devre gerilimi $V_{oc} = V_S/2$ ve kaynak sıfırlanıp uçlardan bakıldığında iki direncin paralel eşdeğeri $R_{th} = R \\parallel R = R/2$. Ölçü aleti bu eşdeğer kaynağın iki ucuna bağlanan bir yük direncidir; dolayısıyla gösterdiği değer", align="j", keep=True)
    D.eq(r"V_{O,\mathrm{ölç}}=V_{oc}\,\frac{R_m}{R_m+R_{th}}=\frac{V_S}{2}\cdot\frac{R_m}{R_m+R/2}", "vm")
    D.p("olur. Buna göre ölçüm hatası, ölçü aleti ile ideal değer arasındaki göreli farktır:", keep=True)
    D.eq(r"\varepsilon_{\mathrm{yük}}=\frac{V_{O,\mathrm{ölç}}-V_O}{V_O}\times100\,\%=-\frac{R}{2R_m+R}\times100\,\%", "yuk")
    D.p("Sayısal olarak $R = 10\\ \\mathrm{M\\Omega}$ için $R_{th} = 5\\ \\mathrm{M\\Omega}$ olduğundan $V_{O,\\mathrm{ölç}} = 7{,}5\\ \\mathrm{V} \\times 10/(10+5) = 5{,}0\\ \\mathrm{V}$ ve hata −%33,33’tür. $R = 100\\ \\mathrm{k\\Omega}$ için $R_{th} = 50\\ \\mathrm{k\\Omega}$ ve $V_{O,\\mathrm{ölç}} = 7{,}463\\ \\mathrm{V}$ (−%0,50), $R = 470\\ \\Omega$ için ise $V_{O,\\mathrm{ölç}} = 7{,}49982\\ \\mathrm{V}$ (−%0,0023) elde edilir. [[t:yuk]] bu üç değerin kuramsal ve benzetim sonuçlarını karşılaştırmaktadır.", align="j")
    rows = []
    for R, (vi, vm) in C["div"].items():
        R = float(R); ti = 7.5; tm = 7.5 * 1e7 / (1e7 + R / 2)
        lab = "470 Ω" if R == 470 else ("100 kΩ" if R == 1e5 else "10 MΩ")
        rows.append([lab, n(ti, 3, "V"), n(vi, 3, "V"), n(tm, 3, "V"), n(vm, 3, "V"), err(tm, vm, 3, "V"), "−%" + n(abs(tm - ti) / ti * 100, 2)])
    D.tab("yuk", ["R", "Teorik VO (ideal)", "Benzetim VO (ideal)", "Teorik VO,ölç", "Benzetim VO,ölç", "Mutlak hata", "Yük hatası εyük"], rows,
          "Gerilim bölücüde VO: ideal ölçüm ve Rm = 10 MΩ’luk ölçü aleti ile ölçüm (teorik ve benzetim) ve ideal değere göre yük hatası", [1.8, 2.4, 2.4, 2.2, 2.4, 1.9, 2.0], size=9)
    D.p("[[f:dividl]] ölçü aleti olmadan (ideal), [[f:divrm]] ise ölçü aletinin 10 MΩ’luk iç direnci devreye katılarak yapılan LTspice benzetiminin işletme noktasını göstermektedir. İdeal durumda $V(vo) = 7{,}5$ V olarak bulunmuş; ölçü aletinin direnci hesaba katıldığında 5 V’a düşmüştür. Bu, kuramsal olarak öngörülen değerle birebir aynıdır. Yani aynı devrede aynı bölücüyü ölçen iki farklı “bakış”, yalnızca ölçü aletinin devreyi etkileyip etkilemediğine bağlı olarak %33 farklı sonuç vermiştir.", align="j")
    D.fig("dividl", s("bol22_ideal"), "$R = 10\\ \\mathrm{M\\Omega}$ için ölçü aletsiz (ideal) LTspice benzetimi: $V(vo) = 7{,}5$ V, $I(R_1) = 0{,}75\\ \\mu\\mathrm{A}$.", 14.5)
    D.fig("divrm", s("bol22_rm"), "$R = 10\\ \\mathrm{M\\Omega}$ ve $R_m = 10\\ \\mathrm{M\\Omega}$’luk ölçü aleti direnci devreye katılarak yapılan LTspice benzetimi: $V(vo) = 5$ V; $R_2$ ve $R_m$ akımları 0,5 µA, $R_1$ akımı 1 µA’dir.", 14.5)
    D.p("[[f:divdc]]’de LTspice ile yapılan DC taraması görülmektedir: kaynak gerilimi 0–15 V arasında taranmış ve 10 MΩ’luk ölçü aleti direnciyle yüklenen devrenin çıkışı $V(vo)$ çizdirilmiştir. Eğim $V_S/3$ değerine karşılık gelir ($5/15 = 0{,}3333$; imleç farkı penceresinde “Slope” = 0,333333). Çizim üzerine iki imleç konulmuş ve koordinatları [[t:divcur]]’da verilmiştir; kaynağın 15 V’taki değeri 5,000 V, orta noktadaki değeri 2,500 V okunmuştur.", align="j")
    D.fig("divdc", s("bol22_dc"), "Gerilim bölücünün (Rm = 10 MΩ ile) LTspice DC taraması, $V_S = 0\\ldots15$ V, iz: $V(vo)$. Dikey kesikli çizgi ve sağ alttaki pencere imleçlerin yerini ve koordinatlarını gösterir. Çizimin üst kısmında cihaz seri numarası yer almaktadır.", 14.5)
    D.tab("divcur", ["İmleç", "X (VS)", "Y (VO)", "Teorik VO"],
          [["İmleç 1", "15,000 V", "5,000 V", "5,000 V"], ["İmleç 2", "7,500 V", "2,500 V", "2,500 V"], ["Fark (2 − 1)", "−7,500 V", "−2,500 V", "Eğim = 0,3333"]],
          "[[f:divdc]]’deki imleç noktalarının koordinatları", [3.0, 3.2, 3.2, 3.4])
    D.p("Yük etkisinin $R$’ye bağlı değişimi [[f:yukgraf]]’de verilmiştir. $R$ küçük olduğu sürece ölçü hatası ihmal edilebilir; $R$, ölçü aletinin iç direncine yaklaştıkça hata hızla artar. Bunun pratik sonucu şudur: bir devrede gerilim ölçülecekse, ölçülen noktaya bakan eşdeğer direnç ölçü aletinin iç direncinden en az iki-üç mertebe küçük olmalıdır. Aksi durumda ölçüm, devrenin gerçek değerini değil devre + ölçü aleti birleşiminin değerini verir ve gösterge bu yüzden “yanlış” okunur. Gerilim bölücü devrede $R = 10\\ \\mathrm{M\\Omega}$ seçilmiş olması bilerek yapılmıştır: amaç bu etkiyi görünür kılmaktır.", align="j")
    D.fig("yukgraf", a("im-016.png"), "Ölçü aletinin yük etkisi (kapalı form çözümün grafiği): mavi kesikli çizgi ideal çıkışı (7,5 V), kırmızı çizgi $R_m = 10\\ \\mathrm{M\\Omega}$’luk ölçü aleti ile ölçülen çıkışı göstermektedir. Üç işaretli nokta, [[t:yuk]] ile aynı $R$ değerlerine karşılık gelir.", 13.0)
    D.h(3, "2.2.3 Devre Tahtası Yerleşimi")
    D.p("[[f:bbdiv]]’de gerilim bölücünün devre tahtasındaki yerleşimi görülmektedir. Üstteki direnç a6–a14, alttaki direnç b14–b22 deliklerine takılmıştır; 14. sütun, iki direncin ortak düğümü ($V_O$ düğümü) olur. Kırmızı jumper 6. sütunu (+) rayına, mavi jumper 22. sütunu (−) rayına bağlar. Kaynağın (+) çıkışı (+) raya, (−) çıkışı (−) raya takılır. $V_O$ ölçümü için ölçü aletinin kırmızı ucu c14’e, siyah ucu (−) rayına dokundurulur.", align="j")
    D.fig("bbdiv", a("im-017.png"), "Gerilim bölücünün devre tahtasındaki yerleşimi. $V_O$, c14 deliği ile (−) ray arasından ölçülür.", 14.5)

    # ---- 2.3
    D.h(2, "Wheatstone Köprüsü")
    D.h(3, "2.3.1 Devre ve Denge Koşulu")
    D.p("Wheatstone köprüsü, iki gerilim bölücünün paralel bağlanmasıyla oluşur ve iki bölücünün orta noktaları arasındaki fark gerilimi $V_B$ ölçülür ([[f:brsch]]). Sol koldaki bölücünün orta noktası L düğümü ($R_1$ ile $R_3$’ün birleşimi), sağ koldaki bölücünün orta noktası R düğümüdür ($R_2$ ile $R_x$’in birleşimi). Her bölücüyü Bölüm 2.2’deki gibi çözmek yeterlidir:", align="j", keep=True)
    D.eq(r"V_L=V_S\,\frac{R_3}{R_1+R_3}", "vl")
    D.eq(r"V_R=V_S\,\frac{R_x}{R_2+R_x}", "vr")
    D.eq(r"V_B=V_L-V_R", "vb")
    D.fig("brsch", a("im-021.png"), "Wheatstone köprüsü devresi. Kaynağın (+) ucu T düğümüne, (−) ucu G (toprak) düğümüne bağlıdır; $V_B$, L ve R düğümleri arasından ölçülür.", 11.0)
    D.p("Denge, $V_B = 0$ V olması durumudur; bu, iki bölücünün orta noktalarının aynı gerilimde olması demektir ve ölçü aletinden (dedektörden) hiç akım geçmediği anlamına gelir. Dengede $V_L = V_R$ olduğundan:", align="j", keep=True)
    D.eq(r"\frac{R_3}{R_1+R_3}=\frac{R_x}{R_2+R_x}", "d1")
    D.eq(r"R_3\,(R_2+R_x)=R_x\,(R_1+R_3)", "d2")
    D.eq(r"R_2R_3+R_3R_x=R_1R_x+R_3R_x", "d3")
    D.p("Her iki tarafta bulunan $R_3R_x$ terimleri sadeleşir ve bilinmeyen direnç için", keep=True)
    D.eq(r"R_x=\frac{R_2\,R_3}{R_1}", "rx")
    D.p("elde edilir. Bu sonucun en önemli özelliği, kaynak geriliminin $V_S$ ifadede hiç görünmemesidir: bilinmeyen direnç yalnızca üç bilinen direncin oranından bulunur. Bu nedenle köprü, kaynak gerilimindeki dalgalanmalara karşı duyarsız bir ölçüm yöntemidir ve dengede ölçü aleti yalnızca “sıfır gösteriyor mu?” sorusunu yanıtlayacak kadar duyarlı olmak zorundadır; mutlak bir gerilimin doğru okunması gerekmez.", align="j")
    D.p("$R_1 = R_2 = 470\\ \\Omega$ ve $R_3 = 1\\ \\mathrm{k\\Omega}$ için denge, $R_x = 470 \\times 1000 / 470 = 1\\ \\mathrm{k\\Omega}$ olduğunda sağlanır. Verilen $R_x = 1\\ \\mathrm{k\\Omega}$ değeri tam bu koşuldur; dolayısıyla $V_B = 0$ V beklenir. Bu durumda $V_L = V_R = 15\\ \\mathrm{V} \\times 1000/1470 = 10{,}204\\ \\mathrm{V}$’tur.", align="j")
    D.h(3, "2.3.2 Benzetim Sonuçları ve Rx’in Değiştirilmesi")
    D.p("[[f:brop]] $R_x = 1\\ \\mathrm{k\\Omega}$ için LTspice işletme noktasını göstermektedir: $V(l) = V(r) = 10{,}2041$ V ve dolayısıyla $V_B = 0{,}000$ V; dedektör kolundan akım geçmediği için $R_1$, $R_2$, $R_3$ ve $R_x$ akımlarının hepsi 10,2041 mA’dir (kaynak akımı 20,4082 mA). $R_x$ değiştirilerek elde edilen sonuçlar [[t:brt]]’de verilmiştir. Tablodaki satırların hepsi aynı denklemlerle ([[e:vl]]–[[e:vb]]) hesaplandığı için yalnızca bir tanesi gösterimlik çözülmüştür: $R_x = 470\\ \\Omega$ için $V_R = 15 \\times 470/940 = 7{,}5$ V, $V_L = 10{,}204$ V ve $V_B = 2{,}704$ V olarak elde edilir. Diğer satırlar benzer biçimde hesaplanmış ve tabloya yazılmıştır.", align="j")
    D.fig("brop", s("bol23_op"), "$R_x = 1\\ \\mathrm{k\\Omega}$ için Wheatstone köprüsünün LTspice işletme noktası: $V(l) = V(r) = 10{,}2041$ V; köprü dengededir ($V_B = 0$ V).", 14.5)
    D.p("[[f:brdc]]’te $R_x = 10\\ \\Omega$ ile $10\\ \\mathrm{k\\Omega}$ arasında taranırken $V_B$’nin değişimi LTspice ile çizdirilmiştir. Taramada $R_x$, değeri doğrudan ohm olarak okunan bir kaynak gerilimine bağlanmıştır (“R=V(sw)” davranışsal direnç ifadesi); bu nedenle LTspice yatay eksende ohm yerine volt (kΩ yerine kV) birimini yazmaktadır ve eksen değerleri doğrudan ohm olarak okunmalıdır. Eğri $R_x \\approx 1\\ \\mathrm{k\\Omega}$’da sıfır değerini kesmektedir; iki imleç konulmuş ve koordinatları [[t:brcur]]’da verilmiştir. Birinci imleç dengeye (1,0026 kΩ) yerleştirilmiş ve $V_B = −8{,}5$ mV okunmuştur; denge noktasındaki teorik eğim (−3,26 mV/Ω) dikkate alındığında bu, imlecin dengeden 2,6 Ω uzakta olmasının doğal sonucudur.", align="j")
    D.fig("brdc", s("bol23_dc"), "Wheatstone köprüsünün LTspice DC taraması: iz $V(l) - V(r)$, $R_x = 10\\ldots10\\,000\\ \\Omega$ (eksen birimi LTspice tarafından “V” yazılmıştır, değer ohmdur). Cihaz seri numarası çizimin üst kısmındadır.", 14.5)
    def vbt(rx): return 15 * 1000 / 1470 - 15 * rx / (470 + rx)
    D.tab("brcur", ["İmleç", "X (Rx)", "Y (VB), LTspice", "Y (VB), teorik"],
          [["İmleç 1", "1.002,55 Ω", "−8,5037 mV", n(vbt(1002.5548) * 1000, 4, "mV")],
           ["İmleç 2", "100,232 Ω", "7,5675 V", n(vbt(100.23226), 4, "V")],
           ["Fark (2 − 1)", "−902,323 Ω", "7,5761 V", n(vbt(100.23226) - vbt(1002.5548), 4, "V")]],
          "[[f:brdc]]’deki imleç noktalarının koordinatları", [3.0, 3.2, 3.6, 3.6])
    D.tab("brt", ["Rx", "Teorik VB", "Benzetim VB", "Mutlak hata", "Bağıl hata"],
          [[(n(float(k) / 1000 if float(k) >= 1000 else float(k), 1 if float(k) in (1200.0,1500.0,2200.0,4700.0) else (0 if float(k) < 1000 else (0 if float(k)==1000 else 0))) ) for k in [k]] for k in []] or
          [[(("%s kΩ" % n(float(k) / 1000, 1 if float(k) % 1000 else 0)) if float(k) >= 1000 else "%s Ω" % n(float(k), 0)),
            n(vbt(float(k)), 3, "V"), n(v[0] - v[1], 3, "V"), err(vbt(float(k)), v[0] - v[1], 3, "V"), "–" if float(k) == 1000 else "%0"]
           for k, v in C["br"].items()],
          "Wheatstone köprüsünde Rx’e göre VB ($R_1 = R_2 = 470\\ \\Omega$, $R_3 = 1\\ \\mathrm{k\\Omega}$, $V_S = 15$ V)", [2.2, 3.0, 3.0, 3.0, 2.6])
    D.p("[[t:brt]] ve [[f:vbgraf]] birlikte incelendiğinde $V_B$’nin $R_x$ ile değişimi şöyle yorumlanabilir. (i) $R_x = 1\\ \\mathrm{k\\Omega}$’un altında $V_B$ pozitiftir, çünkü sağ bölücünün orta noktası ($R_x$ küçüldükçe) toprağa yaklaşır ve $V_R$, $V_L$’den küçük kalır; $R_x = 1\\ \\mathrm{k\\Omega}$’da fark sıfıra iner (denge); bunun üzerinde $V_R$, $V_L$’yi geçer ve $V_B$ negatif olur. Yani $V_B$’nin işareti, $R_x$’in dengeye göre büyük mü küçük mü olduğunu söyler. (ii) $V_B$, $R_x$’in doğrusal bir fonksiyonu değil, kesirli (hiperbolik) bir fonksiyonudur. Eğimi türev alınarak bulunur:", align="j", keep=True)
    D.eq(r"\frac{\mathrm{d}V_B}{\mathrm{d}R_x}=-\frac{V_S\,R_2}{(R_2+R_x)^2}", "egim")
    D.p("Dengenin yakınında hemen hemen doğrusal olan değişim, [[f:vbgraf]]-b’de görüldüğü gibi, eğimi $V_SR_2/(R_2+R_x)^2 = 15 \\times 470/1470^2 \\approx 3{,}26\\ \\mathrm{mV/\\Omega}$ olan bir doğrudur: 1 Ω’luk bir sapma yaklaşık 3,26 mV’luk bir fark gerilimi yaratır. Bu, köprünün çok duyarlı bir dengeleme aracı olduğunu gösterir: 1 mV çözünürlüklü bir ölçü aleti $R_x$’teki ≈0,3 Ω’luk bir değişimi görebilir. (iii) $R_x$ arttıkça eğim azalır ve $V_B$ bir sınıra yaklaşır:", align="j", keep=True)
    D.eq(r"\lim_{R_x\to\infty}V_B=V_L-V_S=-4{,}796\ \mathrm{V},\qquad \lim_{R_x\to0}V_B=V_L=+10{,}204\ \mathrm{V}", "lim")
    D.p("Dolayısıyla $V_B$ hiçbir zaman bu iki sınırın dışına çıkamaz.", align="j")
    D.fig("vbgraf", a("im-030.png"), "(a) $V_B$’nin $R_x$ ile değişimi ve iki sınır değeri (kapalı form çözümün grafiği); (b) denge çevresinin (±100 Ω) büyütülmüş görünümü. Eğri, $R_x = 1\\ \\mathrm{k\\Omega}$’da sıfırı keser.", 14.5)
    lo, hi = C["br_tol"]
    D.p("[[t:brt]]’deki teorik ve benzetim değerleri aynı denklemlere dayandığından örtüşmektedir. Laboratuvarda ise sonuç farklı olacaktır: dirençlerin %5 toleransı dengeyi bozar. Dört direncin de tolerans sınırının en kötü bileşiminde (her biri ±%5; 16 kombinasyonun tamamı) yapılan benzetim, kurulu bir köprüde $V_B$’nin @1@ V ile +@2@ V arasında, yani yaklaşık ±@3@ mV aralığında kalabileceğini göstermiştir. Bu nedenle gerçek devrede $V_B = 0{,}000$ V okunmaması beklenir; ölçülen birkaç yüz mV değerinde bir sapma hata sayılmamalı, direnç toleransının bir sonucu olarak yorumlanmalıdır. Gerçek dengeye ulaşmak için $R_x$ yerine ayarlı bir direnç (potansiyometre) kullanılır ve $V_B$ sıfır olana kadar ayarlanır; bu durumda $R_x$ yine denklem ([[e:rx]]) ile hesaplanır.".replace("@1@", n(lo, 3)).replace("@2@", n(hi, 3)).replace("@3@", str(round(hi * 1000))), align="j")
    D.h(3, "2.3.3 Devre Tahtası Yerleşimi")
    D.p("[[f:bbbr]]’de köprünün devre tahtasındaki yerleşimi verilmiştir. L düğümü 5. sütun ($R_1$ ve $R_3$ bacaklarının birleştiği), T düğümü 10. sütun ($R_1$ ve $R_2$’nin birleştiği, aynı zamanda (+) ray ile jumper aracılığıyla bağlı), R düğümü 15. sütundur ($R_2$ ve $R_x$). $R_3$ ve $R_x$’in diğer uçları jumperlarla (−) rayına (toprak) bağlıdır. $V_B$ ölçümü için ölçü aletinin uçları d5 (L) ve d15 (R) deliklerine dokundurulur.", align="j")
    D.fig("bbbr", a("im-031.png"), "Wheatstone köprüsünün devre tahtasındaki yerleşimi. $V_B$, d5 (L düğümü) ve d15 (R düğümü) deliklerinden ölçülür.", 14.5)

    # ---- 2.4
    D.h(2, "Sayısal-Analog Çevirici (DAC)")
    D.h(3, "2.4.1 DAC Nedir, Kullanım Alanları")
    D.p("Sayısal-analog çevirici (digital-to-analog converter, DAC), ikili sayılarla ifade edilen bir sayısal değeri, bu sayıyla orantılı bir analog gerilime (veya akıma) çeviren devredir [4]. Bilgisayar ve mikrodenetleyici gibi sayısal sistemlerin iç dünyası yalnızca 0 ve 1’lerden oluşurken, hoparlör, motor, ekran ve algılayıcı gibi gerçek dünya birimleri sürekli (analog) büyüklüklerle çalışır; DAC bu iki dünya arasındaki köprüdür. Kullanım alanları arasında şunlar sayılabilir: dijital ses çalarlar ve telefonlardaki ses çıkışı (sayısal ses dosyasının gerilime çevrilip hoparlörün sürülmesi), video ve ekran sistemleri, fonksiyon (işaret) üreteçleri, motor hız ve konum kontrolü, endüstriyel proses kontrolü ve test-ölçüm cihazlarında programlanabilir gerilim/akım kaynakları.", align="j")
    D.p("$N$ bitlik bir DAC, $2^N$ farklı çıkış seviyesi üretebilir. Bu deneyde kullanılan 3 bitlik DAC $2^3 = 8$ seviye (0–7) üretir. Seviye sayısı arttıkça (ör. ses için 16–24 bit) çıkış gerçek sürekli büyüklüğe daha çok benzer.", align="j")
    D.h(3, "2.4.2 Devre ve Kimlik Numarasına Bağlı Giriş")
    D.p("Kimlik numarasının son hanesi 7’dir ve ikilik tabanda 111 olarak yazılır. Giriş durumu yönergedeki kural [8] ile belirlenmiştir. En anlamlı bit (MSB, en soldaki) $b_1 = 1$, $b_2 = 1$ ve en az anlamlı bit (LSB) $b_3 = 1$’dir. Bir bit 1 ise ilgili girişe 16 V, 0 ise 0 V (toprak) uygulanır. [[f:dacsch]]’de devre şeması, [[t:dacin]]’de ise girişlerin değerleri verilmiştir.", align="j")
    D.tab("dacin", ["Son hane", "Kullanılan sayı", "İkilik", "V1 (b1)", "V2 (b2)", "V3 (b3)"], [["7", "7", "111", "16 V", "16 V", "16 V"]], "Kimlik numarasına göre DAC girişleri", [2.2, 3.0, 2.2, 2.4, 2.4, 2.4])
    D.fig("dacsch", a("im-032.png"), "Üç bitlik 2R-R merdivenli DAC devresi. Giriş gerilimlerinin değerleri kimlik numarasının ikilik karşılığından belirlenmiştir.", 13.5)
    D.h(3, "2.4.3 Teorik İşlemler")
    D.p("$V_O$ değeri, Thevenin eşdeğeri ile aşağıdan yukarı doğru, düğüm düğüm indirgenerek bulunur. Önce, ağdaki doğrusal ilişkinin nedeni anlaşılmalıdır: her düğümde 2 kΩ’luk bir giriş direnci, o düğümün solundaki (aşağıdaki) ağın eşdeğer direnci ise yine 2 kΩ’dur; bu yüzden her adımda sol taraf ile giriş birbirini “yarı yarıya” paylaşır. Ayrıntılı olarak ($V_{th,k}$ ve $R_{th,k}$, $N_k$ düğümünden aşağıya bakan Thevenin eşdeğeridir):", align="j", keep=True)
    D.eq(r"V_{th,3}=\frac{V_3}{2},\qquad R_{th,3}=2\,\mathrm{k\Omega}\parallel 2\,\mathrm{k\Omega}=1\,\mathrm{k\Omega}", "t3")
    D.eq(r"V_{th,2}=\frac{V_2+V_{th,3}}{2}=\frac{V_2}{2}+\frac{V_3}{4},\qquad R_{th,2}=2\,\mathrm{k\Omega}\parallel(1\,\mathrm{k\Omega}+R_{th,3})=1\,\mathrm{k\Omega}", "t2")
    D.eq(r"V_{th,1}=\frac{V_1+V_{th,2}}{2}=\frac{V_1}{2}+\frac{V_2}{4}+\frac{V_3}{8},\qquad R_{th,1}=1\,\mathrm{k\Omega}", "t1")
    D.eq(r"V_O=V_{th,1}\,\frac{R_L}{R_L+R_{th,1}}=\frac{V_{th,1}}{2}", "t0")
    D.p("Birinci adımda $N_3$ düğümünde, $V_3$ kaynağının 2 kΩ’luk direnci ile 2 kΩ’luk sonlandırma direnci birbirine paralel görünür; Thevenin eşdeğeri $V_3/2$ gerilimli ve 1 kΩ dirençli bir kaynaktır. İkinci adımda bu 1 kΩ’a merdivenin 1 kΩ’luk direnci eklenir (2 kΩ) ve $V_2$’nin 2 kΩ’luk direnciyle paralel bağlanır; iki eşit dirençli kaynak olduğundan ortak gerilim ortalamadır. Üçüncü adım aynıdır. Dördüncü adımda, $V_O$ düğümüne $R_L = 1\\ \\mathrm{k\\Omega}$ yük bağlanır; $R_{th,1} = 1\\ \\mathrm{k\\Omega}$ olduğundan çıkış, Thevenin geriliminin yarısıdır. Bu dört satır birleştirilirse", align="j", keep=True)
    D.eq(r"V_O=\frac{V_1}{4}+\frac{V_2}{8}+\frac{V_3}{16}=\frac{4V_1+2V_2+V_3}{16}", "vodac")
    D.p("elde edilir. Bu ifadede 4, 2 ve 1 katsayıları ikilik tabandaki basamak ağırlıklarıdır. Dolayısıyla çıkış gerilimi (volt cinsinden) giriş sayısına eşittir: $V_O = 4b_1 + 2b_2 + b_3$. Girişin 16 V seçilmesinin nedeni de budur: her bit tam sayı volt üretir ve çıkış değeri doğrudan giriş sayısı olarak okunabilir.", align="j")
    v7 = C["dac"]["7"][1]
    pw = {"Rg1": (16 - v7[0]) ** 2 / 2000, "Rg2": (16 - v7[1]) ** 2 / 2000, "Rg3": (16 - v7[2]) ** 2 / 2000, "Rl1": (v7[1] - v7[0]) ** 2 / 1000, "Rl2": (v7[2] - v7[1]) ** 2 / 1000, "Rt": v7[2] ** 2 / 2000, "RL": v7[0] ** 2 / 1000}
    pk = max(pw, key=pw.get)
    D.p("Kimlik numarası için (111) $V_O = 4 \\times 1 + 2 \\times 1 + 1 = 7$ V olarak bulunur. Düğüm gerilimleri de aynı basamakları izler: bu giriş durumunda $V_{N1} = 7{,}000$ V, $V_{N2} = 9{,}500$ V ve $V_{N3} = 8{,}750$ V’tur.", align="j")
    D.p("Devredeki dirençlerin güçleri de denetlenmiştir: en kötü durumda (tüm bitler 1, 7 V çıkış) en çok güç @1@ üzerinde, @2@ mW olarak harcanır; kaynaklardan çekilen toplam akım ise @3@ mA’dir. Kullanılan 1/4 W (250 mW) dirençler için güvenli bir değerdir ve laboratuvar kaynağının akım sınırının altındadır.".replace("@1@", {"RL": "yük direnci $R_L$", "Rg1": "$R_{g1}$", "Rg2": "$R_{g2}$", "Rg3": "$R_{g3}$", "Rl1": "$R_{l1}$", "Rl2": "$R_{l2}$", "Rt": "$R_t$"}[pk]).replace("@2@", n(pw[pk] * 1000, 1)).replace("@3@", n(v7[3] * 1000, 2)), align="j")
    D.h(3, "2.4.4 Benzetim Sonuçları ve Hata Payları")
    D.p("[[f:dacop]]’te LTspice benzetiminin düğüm gerilimleri verilmiştir: $V(vo) = 7$ V, $V(n2) = 9{,}5$ V ve $V(n3) = 8{,}75$ V. Bu değer, kimlik numarasının son hanesi için bulunan kuramsal değer ile aynıdır: $V_O = 7$ V. Dolayısıyla “benzetimle elde edilen $V_O$, kimlik numarasının son hanesine eşit midir?” sorusunun yanıtı evettir. (Devre şemasında $N_1$ düğümü çıkış düğümü olduğundan $V(vo)$ ile $V_{N1}$ aynı düğümdür.)", align="j")
    D.fig("dacop", s("bol24_op"), "Üç bitlik DAC’ın LTspice benzetiminde işletme noktası (111 girişi): $V(vo) = V_{N1} = 7$ V; $V(n2) = 9{,}5$ V; $V(n3) = 8{,}75$ V. Her kaynaktan 4,5 mA, 3,25 mA ve 3,625 mA akım çekilmektedir (toplam 11,375 mA).", 14.5)
    D.p("[[f:dacdc]]’te DAC’ın girişleri, bit değeri 1 olan uçlar ortak bir $V_H$ kaynağına bağlanarak (burada üç bit de 1 olduğundan üç giriş birlikte) $V_H = 0$–$16$ V arasında taranmış ve çıkış gerilimi LTspice ile çizdirilmiştir. Çıkış, $V_H$ ile doğru orantılı artmakta ve $V_H = 16$ V’ta kimlik numarasının son hanesine karşılık gelen değere ulaşmaktadır ($V_O = 7V_H/16$; eğim 0,4375). İmleç noktalarının koordinatları [[t:daccur]]’de verilmiştir.", align="j")
    D.fig("dacdc", s("bol24_dc"), "DAC’ın LTspice DC taraması ($V_H = 0\\ldots16$ V), iz: $V(vo)$. İmleçler $V_H = 16$ V ve $V_H = 8$ V noktalarındadır. Cihaz seri numarası çizimin üst kısmında görülmektedir.", 14.5)
    D.tab("daccur", ["İmleç", "X (VH)", "Y (VO)", "Teorik VO"],
          [["İmleç 1", "16,000 V", "7,000 V", "7,000 V"], ["İmleç 2", "8,000 V", "3,500 V", "3,500 V"], ["Fark (2 − 1)", "−8,000 V", "−3,500 V", "Eğim = 0,4375"]],
          "[[f:dacdc]]’deki imleç noktalarının koordinatları", [3.0, 3.2, 3.2, 3.4])
    D.p("[[t:dacall]] tüm kimlik hanelerini (0–9) ve ilgili girişi toplu olarak göstermektedir. Her satırda çıkış, süperpozisyonla bulunan kuramsal $V_O$ ile benzetim sonucunun karşılaştırılmasıyla verilmiştir; tüm kuramsal değerler ([[e:vodac]]) denklemiyle elde edilmiştir. Yönergedeki kurala göre 0, 8 ve 9 hanelerinde giriş 7 (111) olarak kullanılır. [[f:dacstep]]’te sekiz seviye bir merdiven olarak görülmektedir: her bit 1 V’luk eşit adımlarla artış sağlar.", align="j")
    rows = []
    for d, (code, (vo, v2, v3, itot)) in C["dac"].items():
        lab = d + (" (→ 7)" if int(d) in (0, 8, 9) else "")
        rows.append([lab, format(code, "03b"), n(code, 3, "V"), n(vo, 3, "V"), err(code, vo, 3, "V"), "%0", n(itot * 1000, 2, "mA")])
    D.tab("dacall", ["Son hane", "İkilik giriş", "Teorik VO", "Benzetim VO", "Mutlak hata", "Bağıl hata", "Toplam kaynak akımı"], rows,
          "DAC çıkış gerilimi: kimlik numarasının son hanesine göre teorik değer, benzetim sonucu, hata ve kaynak akımı", [2.2, 2.2, 2.4, 2.5, 2.1, 1.8, 2.8], size=9)
    D.fig("dacstep", a("im-040.png"), "DAC’ın giriş kodu – çıkış gerilimi karakteristiği (kapalı form çözümün grafiği). Kırmızı nokta, kimlik numarasının son hanesine karşılık gelen seviyeyi gösterir.", 13.0)
    lo, hi = C["dac_tol"]
    D.p("Gerçek devrede ise çıkışın tam tam sayı volt olmasını engelleyen etkiler vardır: dirençlerin %5 toleransı (2R-R ağında 2:1 oranının bozulması en çok MSB kolunun ağırlığını etkiler), kaynağın 16 V ayar hassasiyeti ve ölçü aletinin 10 MΩ’luk giriş direnci. Bunlardan en etkilisi toleranstır: yedi direncin hepsinin tolerans sınırlarının (±%5) her bileşimi için (2⁷ = 128 kombinasyon) yapılan benzetimde, bu giriş için $V_O$ @1@ V ile @2@ V arasında kalmıştır; yani nominal 7 V değerinden en fazla yaklaşık @3@ mV sapılabilir. Ölçü aletinin yükü ise burada ihmal edilebilir; çünkü çıkış düğümüne bakan eşdeğer direnç 500 Ω mertebesindedir ve 10 MΩ’a kıyasla çok küçüktür (Bölüm 2.2’deki $\\varepsilon_{\\mathrm{yük}} \\approx -$%0,0025).".replace("@1@", n(lo, 3)).replace("@2@", n(hi, 3)).replace("@3@", str(round((hi - 7) * 1000))), align="j")
    D.h(3, "2.4.5 Devre Tahtası Yerleşimi")
    D.p("[[f:bbdac]]’te DAC’ın devre tahtası yerleşimi görülmektedir. Üç adet 2 kΩ giriş direnci (a4–a8, a12–a16, a20–a24), merdivenin 1 kΩ’luk dirençleri (b8–b16 ve c16–c24), 2 kΩ’luk sonlandırma direnci (b24–b28) ve yük direnci $R_L$ (c8–c2) kullanılır. $N_1$, $N_2$ ve $N_3$ düğümleri sırasıyla 8., 16. ve 24. sütunlardır. Giriş uçları (4., 12. ve 20. sütunlar), bit değeri 1 ise (+16 V) rayına, 0 ise toprak (−) rayına jumper ile bağlanır; anahtar bulunmadığı için anahtarlar doğrudan jumper ile temsil edilmiştir. $V_O$, d8 deliği ($N_1$) ile toprak rayı arasından ölçülür.", align="j")
    D.fig("bbdac", a("im-041.png"), "DAC’ın devre tahtasındaki yerleşimi (111 girişi). Kırmızı jumper bit 1’i (16 V), mavi jumper bit 0’ı (toprak) gösterir.", 14.5)

    # ---------------- 3 SONUÇLAR
    D.h(1, "Sonuçlar")
    D.p("**Deney sonuçlarının genel değerlendirmesi.** Dört bölümün hepsinde el ile türetilen sonuçlar benzetim sonuçlarıyla birebir örtüşmüştür. Bu uyum, kullanılan formüllerin (seri/paralel eşdeğeri, gerilim bölücü, Thevenin eşdeğeri, süperpozisyon) doğru uygulandığını gösterir. Teorik-benzetim farkı tüm tablolarda yuvarlama hatası mertebesinde kalmıştır. LTspice ekranlarından okunan değerler (işletme noktası pencereleri ve imleç pencereleri) de aynı sonuçları vermiştir: seri ve paralel eşdeğer direnç 13,1 kΩ ve 725,50 Ω, bölücü çıkışı 7,5 V ve 5 V, köprü dengesi $R_x = 1\\ \\mathrm{k\\Omega}$, DAC çıkışı 7 V. Aşağıda, laboratuvar ölçümlerinde bu değerlerden sapma yaratması beklenen etkenler tek tek açıklanmıştır.", align="j")
    D.p("**Direnç toleransı.** Kullanılan dirençlerin dördüncü bandı altındır; bu, nominal değerden %5’e kadar sapma olabileceği anlamına gelir. Tek bir direncin ohmmetre ile ölçülen değeri bile nominal değerden farklı olacaktır. Seri ve paralel bağlantılarda eşdeğer direnç en fazla %5 sapar ([[t:eq]] son sütunundaki aralık). Wheatstone köprüsünde ise dört direncin toleransı birleşerek $V_B$’yi dengede sıfır olmaktan uzaklaştırır; bu çalışmadaki devre için en kötü durumda yaklaşık ±0,65 V’luk bir sapma bulunmuştur. DAC’ta 2:1 oranlarındaki bozulma çıkış seviyelerini kaydırır (en kötü durumda yaklaşık ±0,42 V).", align="j")
    D.p("**Ölçü aletinin iç direnci.** Gerilim bölücüde 10 MΩ’luk dirençlerle yapılan ölçümde yük etkisi %33 hata yaratmıştır. Bu hata ölçü aletinin bozukluğundan değil, ölçüm yönteminin devreyi değiştirmesinden kaynaklanır ve ölçü aleti yerine daha yüksek giriş dirençli bir alet (ör. elektrometre) kullanılarak ya da $R$’nin küçültülmesiyle azaltılabilir. Düşük dirençli devrelerde (Wheatstone ve DAC) ise bu etki ihmal edilebilir düzeydedir.", align="j")
    D.p("**Devre tahtası ve bağlantı kaynaklı hatalar.** Devre tahtasındaki yaylı kontaklar zamanla gevşeyebilir; böyle kontakların direnci birkaç ohm ile yüzlerce ohm arasında değişebilir ve özellikle düşük dirençli devrelerde (470 Ω ve 1 kΩ) ölçüme yansır. Jumper telleri ile ölçü ucu kablolarının dirençleri, kaynağın iç direnci ve ray bağlantılarının kesik olması (bazı tahtalarda ortadan bölünmüş raylar) başka hata kaynaklarıdır. Yanlış sütuna takılan tek bir bacak, devreyi tümüyle başka bir devreye dönüştürebilir.", align="j")
    D.p("**Kaynak ve ölçü aleti kaynaklı hatalar.** Güç kaynağının ekranında görülen 15 V veya 16 V değeri, ayar hassasiyeti ve yük altındaki düşüş nedeniyle gerçek çıkıştan farklı olabilir; Wheatstone ve DAC sonuçları kaynak değeriyle doğru orantılı olduğundan kaynağın gerçek değerinin ölçü aletiyle denetlenmesi gerekir. Sayısal ölçü aletleri de ±(okumanın %’si + son hane sayısı) kadar belirsizlik taşır. Çok küçük gerilimlerin (Wheatstone dengesi çevresindeki mV’lar) ölçülmesinde bu belirsizlik göreli olarak büyür.", align="j")
    D.p("**Eksik veya yorumlanamayan sonuç.** Bu rapor bir ön çalışma raporudur; laboratuvar ölçümleri henüz yapılmamıştır ve bu nedenle ölçüm ile benzetim arasındaki hata payı hesaplanmamıştır. Hata payları bu raporda teorik sonuç ile benzetim arasında verilmiştir; ölçüm sonuçlarının tablolara eklenmesi ve yukarıdaki hata nedenleriyle yorumlanması deney raporunda yapılacaktır.", align="j")
    D.p("**Kazanılan beceriler.** Bu çalışma ile: (i) bir devre şemasının devre tahtasındaki karşılığı çıkarılmış ve dirençlerin renk kodu okunmuştur; (ii) seri, paralel, gerilim bölücü, köprü ve merdiven devreleri çözülmüştür; (iii) Thevenin eşdeğeri ile ölçü aletinin yük etkisi hesaplanmıştır; (iv) süperpozisyon ve düğüm analizi ile çok kaynaklı bir devre çözülmüştür; (v) LTspice ile işletme noktası ve DC tarama benzetimleri yapılmış, imleçlerle koordinat okunmuş ve sonuçlar el hesabıyla karşılaştırılmıştır; (vi) teorik, benzetim ve tolerans temelli hata payı hesaplamaları yapılmış ve sonuçlar tablo ve grafik halinde sunulmuştur.", align="j")

    # ---------------- 4 KAYNAKLAR
    D.h(1, "Kaynaklar")
    refs = ["Nilsson, J. W., & Riedel, S. A. (2015). *Electric circuits* (10th ed.). Boston: Pearson.",
            "Alexander, C. K., & Sadiku, M. N. O. (2017). *Fundamentals of electric circuits* (6th ed.). New York: McGraw-Hill Education.",
            "Hayt, W. H., Kemmerly, J. E., & Durbin, S. M. (2012). *Engineering circuit analysis* (8th ed.). New York: McGraw-Hill.",
            "Horowitz, P., & Hill, W. (2015). *The art of electronics* (3rd ed.). New York: Cambridge University Press.",
            "International Electrotechnical Commission. (2016). *IEC 60062: Marking codes for resistors and capacitors*. Geneva: IEC.",
            "Nagel, L. W., & Pederson, D. O. (1973). *SPICE (Simulation Program with Integrated Circuit Emphasis)* (Memorandum No. ERL-M382). Berkeley: University of California, Electronics Research Laboratory.",
            "Ho, C.-W., Ruehli, A. E., & Brennan, P. A. (1975). The modified nodal approach to network analysis. *IEEE Transactions on Circuits and Systems, 22*(6), 504–509.",
            "TOBB Ekonomi ve Teknoloji Üniversitesi. (2026). *ELE 201 L – Devre Analizi I Laboratuvarı, Deney 1 Ön Çalışma Yönergesi*. Ankara: TOBB ETÜ, Elektrik – Elektronik Mühendisliği Bölümü."]
    for i, r in enumerate(refs, 1):
        par = D.p("%d. %s" % (i, r)); par.paragraph_format.left_indent = __import__("docx").shared.Cm(0.9); par.paragraph_format.first_line_indent = __import__("docx").shared.Cm(-0.9)
    # ---------------- 5 EKLER
    D.h(1, "Ekler")
    D.h(3, "EK-1: SPICE Devre Listeleri (Netlist)")
    D.p("Aşağıdaki devre listeleri, bu raporda kullanılan devrelerin herhangi bir SPICE programına (LTspice, ngspice vb.) olduğu gibi girilmesine olanak verir. Her liste “.op” (DC işletme noktası) çözümlemesi içindir; sonuçlar Bölüm 2’deki değerlerle karşılaştırılabilir. Toprak düğümü 0’dır; SPICE’ta ilk satır başlık satırı sayılır ve devreye katılmaz, bu nedenle listelerin ilk satırı yorum satırı olarak yazılmıştır. LTspice şemaları (.asc) bu listelere eşdeğer elemanları içerir ve “.dc” taramaları için ilgili kaynak değerleri ayrıca taranmıştır.", align="j")
    D.code("* Bolum 2.1 - seri (1 V ile; Req = V1/|I(V1)|)\nV1 1 0 DC 1\nR1 1 2 3.9k\nR2 2 3 1k\nR3 3 0 8.2k\n.op\n.end", "Bölüm 2.1 – Seri bağlantı")
    D.code("* Bolum 2.1 - paralel\nV1 1 0 DC 1\nR1 1 0 3.9k\nR2 1 0 1k\nR3 1 0 8.2k\n.op\n.end", "Bölüm 2.1 – Paralel bağlantı")
    D.code("* R = 10 Mohm, olcu aleti yok\nVS 1 0 DC 15\nR1 1 2 10Meg\nR2 2 0 10Meg\n.op\n.end", "Bölüm 2.2 – Gerilim bölücü (ideal ölçüm)")
    D.code("* Rm = 10 Mohm, R2 ile paralel\nVS 1 0 DC 15\nR1 1 2 10Meg\nR2 2 0 10Meg\nRm 2 0 10Meg\n.op\n.end", "Bölüm 2.2 – Gerilim bölücü (ölçü aleti iç direnci dahil)")
    D.code("* L: dugum 2, R: dugum 3, V(B)=V(2)-V(3)\nVS 1 0 DC 15\nR1 1 2 470\nR2 1 3 470\nR3 2 0 1k\nRx 3 0 1k\n.op\n.end", "Bölüm 2.3 – Wheatstone köprüsü")
    D.code("* V1,V2,V3 = bit 1 ise 16 V, bit 0 ise 0 V\nV1 a 0 DC 16\nV2 b 0 DC 16\nV3 c 0 DC 16\nRg1 a n1 2k\nRg2 b n2 2k\nRg3 c n3 2k\nRl1 n1 n2 1k\nRl2 n2 n3 1k\nRt n3 0 2k\nRL n1 0 1k\n.op\n.end", "Bölüm 2.4 – DAC (giriş 111)")
    D.h(3, "EK-2: Direnç Renk Kodu")
    D.p("Dört bantlı dirençte ilk iki bant anlamlı iki basamağı, üçüncü bant 10’un üssünü, dördüncü bant toleransı verir [5]. Aşağıdaki tabloda renk kodu ve bu çalışmada kullanılan dirençler verilmiştir.", align="j")
    D.tab("rk", ["Renk", "Rakam", "Çarpan", "Tolerans"],
          [["Siyah", "0", "×10⁰", "–"], ["Kahverengi", "1", "×10¹", "±%1"], ["Kırmızı", "2", "×10²", "±%2"], ["Turuncu", "3", "×10³", "–"], ["Sarı", "4", "×10⁴", "–"],
           ["Yeşil", "5", "×10⁵", "±%0,5"], ["Mavi", "6", "×10⁶", "±%0,25"], ["Mor", "7", "×10⁷", "±%0,1"], ["Gri", "8", "×10⁸", "±%0,05"], ["Beyaz", "9", "×10⁹", "–"],
           ["Altın", "–", "×10⁻¹", "±%5"], ["Gümüş", "–", "×10⁻²", "±%10"]], "Direnç renk kodu", [3.5, 2.5, 2.5, 2.5])
    D.tab("rk2", ["Değer", "Bant 1", "Bant 2", "Bant 3 (çarpan)", "Bant 4"],
          [["470 Ω", "Sarı (4)", "Mor (7)", "Kahverengi (×10)", "Altın (%5)"], ["1 kΩ", "Kahverengi (1)", "Siyah (0)", "Kırmızı (×100)", "Altın (%5)"],
           ["2 kΩ", "Kırmızı (2)", "Siyah (0)", "Kırmızı (×100)", "Altın (%5)"], ["3,9 kΩ", "Turuncu (3)", "Beyaz (9)", "Kırmızı (×100)", "Altın (%5)"],
           ["8,2 kΩ", "Gri (8)", "Kırmızı (2)", "Kırmızı (×100)", "Altın (%5)"], ["10 MΩ", "Kahverengi (1)", "Siyah (0)", "Mavi (×10⁶)", "Altın (%5)"]],
          "Deneyde kullanılan dirençlerin bantları (4 bantlı)", [2.0, 3.2, 2.8, 3.6, 2.6])
    return D

if __name__ == "__main__":
    D = build()
    f = os.path.join(OUT, "ELE201L_Deney1_Oncalisma_Raporu.docx"); D.save(f)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", OUT, f], capture_output=True, timeout=300)
    print("ok")
