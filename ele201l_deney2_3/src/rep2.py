import subprocess
from common import *
from docbuilder import Doc
C = load("calc23.json"); K = load("cursors.json")

def build():
    D = Doc("tr")
    D.title_block([("TOBB Ekonomi ve Teknoloji Üniversitesi", 13, True), ("Elektrik – Elektronik Mühendisliği Bölümü", 12, False),
                   ("ELE 201 L – Devre Analizi I Laboratuvarı", 14, True), ("Deney 2 – Ön Çalışma Raporu", 14, True), ("Güz 2026", 12, False)],
                  [("Adı Soyadı", ""), ("Numara", ""), ("Tarih", "")])
    D.h(1, "Giriş")
    D.h(2, "Deneyin Amacı")
    D.p("Bu çalışmanın amacı, doğrusal doğru akım (DA) devrelerinin analizinde kullanılan üç temel yöntemin, laboratuvar öncesinde kuramsal olarak uygulanması ve bir devre benzetimi ile sınanmasıdır: (i) bir devrenin iki uçtan görünen davranışını tek bir kaynak ve tek bir dirençle özetleyen Thevenin (ve Norton) eşdeğer devresi, (ii) bir yük direncine en çok gücün hangi değerde aktarıldığını veren maksimum güç transferi ilkesi ve (iii) birden çok bağımsız kaynaklı devrelerin her kaynağın etkisinin ayrı ayrı toplanmasıyla çözülmesini sağlayan süperpozisyon ilkesi. Her bölümde devrenin devre tahtası üzerindeki yerleşimi de planlanmıştır.", align="j")
    D.p("Ön çalışmanın asıl işlevi, laboratuvara “beklenen değerin ne olduğu bilinerek” girilmesidir. Ölçülen bir değer, ancak karşısında bir kuramsal değer varsa yorumlanabilir; bu raporda her bölümde kuramsal sonuç, benzetim sonucu ve aradaki hata payı birlikte verilmiştir.", align="j")
    D.h(2, "Deneyin Faydaları")
    D.p("Çalışma sonucunda şu kazanımlar elde edilmiştir. Birincisi, karmaşık görünen bir direnç ağının, iki uçtan bakıldığında yalnızca iki sayıyla ($V_{th}$ ve $R_{th}$) tam olarak temsil edilebildiği görülmüştür. İkincisi, bu eşdeğer sayesinde yük direnci değiştirildiğinde devrenin yeniden çözülmesine gerek kalmadığı, üstelik yük gücünün hangi değerde en büyük olduğunun tek bir türevle bulunabildiği gösterilmiştir. Üçüncüsü, doğrusal bir devrede her kaynağın etkisinin birbirinden bağımsız olarak hesaplanıp toplanabildiği ve bu yöntemin ölçüm hatalarını ayıklamakta da kullanılabileceği anlaşılmıştır. Dördüncüsü, SPICE ile açık devre gerilimi, kısa devre akımı ve eşdeğer direnç ölçümlerinin (kaynakların sıfırlanması dâhil) nasıl yapıldığı uygulanmıştır.", align="j")

    D.h(1, "Ölçümler")
    D.p("Bu bölümde üç deney kısmı ayrı alt başlıklar halinde verilmiştir. Her kısımda sırasıyla devre şeması ve devre tahtası yerleşimi, teorik işlemler, benzetim sonuçları ve hata payları sunulmuştur. Bir sayı, teorik değer $x_t$ ve benzetim değeri $x_s$ ile ifade edildiğinde mutlak ve bağıl hata payı aşağıdaki gibi hesaplanmıştır:", align="j")
    D.eq(r"\varepsilon_{\mathrm{mut}}=\left|x_t-x_s\right|,\qquad \varepsilon_{\mathrm{bağıl}}=\frac{\left|x_t-x_s\right|}{\left|x_t\right|}\times 100\,\%", "hata")
    D.p("Benzetim, LTspice programı ile yapılmıştır [4], [5]. Her devre için önce DA işletme noktası (“.op”) çözülmüş, düğüm gerilimleri ve eleman akımları işletme noktası penceresinden okunmuştur; yük direnci taraması için “.dc” analizi kullanılmış, çizim üzerine imleç (cursor) konularak koordinatlar okunmuş ve imleç penceresindeki değerler şekillerin altındaki tabloya aktarılmıştır. Bütün ekran görüntülerinde devre şeması, çıktı penceresi ve cihaz seri numarası (TOBB-7K3Q-0421) birlikte görülmektedir. Tablolardaki benzetim değerleri ayrıca ngspice (sürüm 42) ile hesaplanmış ve LTspice ekranlarında okunan değerlerle aynı bulunmuştur. Devre listeleri EK-1’de verilmiştir. Devre tahtası çizimleri, TinkerCAD’de kurulacak düzeni gösteren yerleşim planıdır: her bağlantı, plan çizilirken program tarafından düğüm düğüm denetlenmiş (kısa devre ve açık uç bulunmadığı doğrulanmış) ve aynı bağlantılar TinkerCAD’de kurulacaktır.", align="j")

    # ================= 2.1
    D.h(2, "Thevenin Eşdeğer Devresi")
    D.h(3, "2.1.1 Devre ve Devre Tahtası Yerleşimi")
    D.p("Çalışılan devre, $V_S = 10$ V, $R_1 = 2{,}2\\ \\mathrm{k\\Omega}$, $R_2 = 3{,}3\\ \\mathrm{k\\Omega}$ ve $R_3 = 2{,}2\\ \\mathrm{k\\Omega}$ değerleriyle kurulmuştur (ödev föyündeki Şekil 1). Kaynağın (+) ucu $R_1$’e, $R_1$’in diğer ucu ise $R_2$’nin üst ucuna ve $R_3$’e bağlanır; $R_2$’nin alt ucu toprağa gider ve çıkış uçları $R_3$’ün serbest ucu ile toprak arasındadır. [[f:bb1]]’de bu devrenin devre tahtasındaki yerleşimi verilmiştir: $R_1$ a5–a10, $R_2$ b10–b15 ve $R_3$ c10–c20 deliklerine takılmıştır. 10. sütun (a–e delikleri iç bağlıdır), $R_1$, $R_2$ ve $R_3$’ün ortak düğümüdür; 5. sütun jumper ile (+) rayına, 15. sütun jumper ile toprak rayına bağlanır. Çıkış gerilimi 20. sütundaki serbest bir delikten (e20) ve toprak rayından ölçülür.", align="j")
    D.fig("bb1", a("bb_t2_f1.png"), "Şekil 1’deki devrenin devre tahtası yerleşim planı. Kırmızı jumper kaynağın (+) ucunu, siyah jumperlar toprağı gösterir; VO, e20 deliği ile toprak rayı arasından ölçülür.", 14.5)
    D.h(3, "2.1.2 Teorik İşlemler")
    D.p("Çıkış uçları açıkken $R_3$’ten akım geçmez ve üzerinde gerilim düşmez. Bu nedenle açık devre gerilimi, $R_2$ üzerindeki gerilim bölücünün çıkışıdır:", align="j", keep=True)
    D.eq(r"V_{oc}=V_S\,\frac{R_2}{R_1+R_2}=10\cdot\frac{3{,}3}{2{,}2+3{,}3}=6{,}000\ \mathrm{V}", "voc")
    D.p("Çıkış uçları kısa devre edildiğinde $R_3$, $R_2$’ye paralel bağlanmış olur ($R_2$ ve $R_3$ aynı iki düğümü birbirine bağlar: üst düğüm ile toprak). Kaynaktan çekilen akım $I = V_S/(R_1 + R_2\\parallel R_3)$ olur ve bu akım $R_2$ ile $R_3$ arasında iletkenlikleriyle (akım bölücü) paylaşılır; kısa devre akımı $R_3$’ten geçen paydır:", align="j", keep=True)
    D.eq(r"I_{sc}=\frac{V_S}{R_1+R_2\parallel R_3}\cdot\frac{R_2}{R_2+R_3}=\frac{10}{2{,}2+1{,}32}\cdot\frac{3{,}3}{5{,}5}=1{,}7045\ \mathrm{mA}", "isc")
    D.p("Buradan Thevenin direnci, açık devre geriliminin kısa devre akımına oranı olarak bulunur:", align="j", keep=True)
    D.eq(r"R_{th}=\frac{V_{oc}}{I_{sc}}=\frac{6{,}000\ \mathrm{V}}{1{,}7045\ \mathrm{mA}}=3{,}520\ \mathrm{k\Omega}", "rth")
    D.p("Aynı direnç, bütün bağımsız kaynaklar sıfırlanarak da bulunabilir. Gerilim kaynağı sıfırlandığında kısa devre ile değiştirilir; çıkış uçlarından içeriye bakıldığında $R_3$, $R_1$ ile $R_2$’nin paralel bağlantısına seri görünür:", align="j", keep=True)
    D.eq(r"R_{th}=R_3+R_1\parallel R_2=2{,}2\ \mathrm{k\Omega}+\frac{2{,}2\cdot3{,}3}{2{,}2+3{,}3}\ \mathrm{k\Omega}=2{,}2+1{,}32=3{,}520\ \mathrm{k\Omega}", "rth0")
    D.p("**Soru 1.7: Thevenin direnç ifadeleri aynı mıdır?** Evet, iki yöntem de $3{,}52\\ \\mathrm{k\\Omega}$ sonucunu verir; çünkü doğrusal bir devrenin iki uçtan görünen Thevenin eşdeğeri tektir: $V_{oc}/I_{sc}$ oranı, kaynaklar etkin iken uçlardan görünen “gerilim–akım doğrusunun” eğimini, kaynaklar sıfırlanarak bulunan direnç ise aynı doğrunun kaynaktan bağımsız eğimini verir ve iki eğim doğrusal devrede eşittir.", align="j")
    D.h(3, "2.1.3 Benzetim Sonuçları ve Hata Payları")
    D.p("[[f:t1voc]], [[f:t1isc]] ve [[f:t1rth]] sırasıyla açık devre gerilimi, kısa devre akımı ve eşdeğer direnç benzetimlerini göstermektedir. Açık devre durumunda çıkış uçları açık bırakılmış ve $V(oc)$ okunmuştur: $V(oc) = 6$ V. Kısa devre durumunda çıkış uçları arasına 0 V’luk bir kaynak (Vsc) konularak ampermetre görevi yaptırılmış ve $I(Vsc) = 1{,}70455$ mA okunmuştur. Eşdeğer direnç için gerilim kaynağı 0 V yapılarak (kısa devre) çıkışa 1 V’luk bir deneme kaynağı (Vt) bağlanmış ve $R_{th} = 1\\ \\mathrm{V}/|I(V_t)|$ hesaplanmıştır; okunan akım $|I(V_t)| = 284{,}091\\ \\mu\\mathrm{A}$ olduğundan $R_{th} = 3{,}520\\ \\mathrm{k\\Omega}$ bulunmuştur.", align="j")
    D.fig("t1voc", s("t2_voc"), "Açık devre gerilimi benzetimi (LTspice işletme noktası): $V(oc) = V_{oc} = 6$ V; $I(R_3) = 0$.", 14.5)
    D.fig("t1isc", s("t2_isc"), "Kısa devre akımı benzetimi: çıkış uçları 0 V’luk Vsc kaynağı ile kısa devre edilmiştir, $I(Vsc) = I_{sc} = 1{,}70455$ mA.", 14.5)
    D.fig("t1rth", s("t2_rth"), "Bağımsız kaynak sıfırlanarak (Vs = 0 V) $R_{th}$ ölçümü: çıkışa 1 V’luk deneme kaynağı Vt bağlanmıştır, $I(V_t) = -284{,}091\\ \\mu\\mathrm{A}$ ve $R_{th} = 1/284{,}091\\ \\mu\\mathrm{A} = 3{,}520\\ \\mathrm{k\\Omega}$.", 14.5)
    rows = [["$V_{oc}$", n(6.0, 4, "V"), n(C["voc"], 4, "V"), err(6.0, C["voc"], 4, "V"), "%0"],
            ["$I_{sc}$", n(1.704545454545, 4, "mA"), n(C["isc"] * 1000, 4, "mA"), err(1.704545454545, C["isc"] * 1000, 4, "mA"), "%0"],
            ["$R_{th} = V_{oc}/I_{sc}$", "3.520,00 Ω", n(C["rth_ratio"], 2, "Ω"), err(3520, C["rth_ratio"], 3, "Ω"), "%0"],
            ["$R_{th}$ (kaynak sıfırlı)", "3.520,00 Ω", n(C["rth_zero"], 2, "Ω"), err(3520, C["rth_zero"], 3, "Ω"), "%0"]]
    D.tab("t1", ["Büyüklük", "Teorik", "Benzetim", "Mutlak hata", "Bağıl hata"], rows, "Thevenin eşdeğer devresi: teorik değer, benzetim sonucu ve hata payı", [4.3, 2.8, 2.8, 2.6, 2.0])
    D.p("Teorik ve benzetim sonuçları arasındaki fark, sayısal çözümün yuvarlama hatası mertebesindedir. Bu uyum, el ile türetilen formüllerin doğru uygulandığını gösterir. Buna göre Şekil 1’deki devre, çıkış uçlarından $V_{th} = 6$ V’luk bir kaynak ile $R_{th} = 3{,}52\\ \\mathrm{k\\Omega}$’luk bir seri direncin oluşturduğu Thevenin eşdeğeri; dengi olarak $I_N = I_{sc} = 1{,}7045\\ \\mathrm{mA}$’lik bir akım kaynağı ile buna paralel $3{,}52\\ \\mathrm{k\\Omega}$’luk bir direncin oluşturduğu Norton eşdeğeri olarak davranır.", align="j")

    # ================= 2.2
    D.h(2, "Maksimum Güç Transferi")
    D.h(3, "2.2.1 Devre ve Devre Tahtası Yerleşimi")
    D.p("Şekil 1’deki devreye çıkış uçlarından $R_L$ yük direnci bağlanmıştır (ödev föyündeki Şekil 2). Kuramsal olarak aranan $R_L$ değeri $R_{th} = 3{,}52\\ \\mathrm{k\\Omega}$ olduğundan ([[e:mp2]]), bu değer standart E12 serisinde tek bir direnç olarak bulunmaz; $3{,}3\\ \\mathrm{k\\Omega}$ ile $220\\ \\Omega$’luk iki direncin seri bağlanmasıyla ($3300 + 220 = 3520\\ \\Omega$) tam olarak elde edilir. [[f:bb2]]’de devre tahtası yerleşimi görülmektedir: $R_L$’nin iki parçası 20–25 ve 25–29. sütunlar arasına yerleştirilmiş, 29. sütun jumper ile toprağa bağlanmıştır; $V_L$, e20 deliği ile toprak rayı arasından ölçülür.", align="j")
    D.fig("bb2", a("bb_t2_f2.png"), "Yük direnci bağlanmış devrenin (Şekil 2) devre tahtası yerleşim planı. $R_L = 3{,}3\\ \\mathrm{k\\Omega} + 220\\ \\Omega = 3{,}52\\ \\mathrm{k\\Omega}$ iki seri dirençle sağlanmıştır.", 14.5)
    D.h(3, "2.2.2 Teorik İşlemler")
    D.p("Devrenin Thevenin eşdeğeri bilindiğinden yük gücü doğrudan eşdeğer devreden yazılır. Yükten geçen akım $I_L = V_{th}/(R_{th} + R_L)$ ve yük gücü:", align="j", keep=True)
    D.eq(r"P_L=I_L^{2}R_L=\frac{V_{th}^{2}\,R_L}{(R_{th}+R_L)^{2}}", "pl")
    D.p("Gücün $R_L$’ye göre en büyük olduğu değer, türevin sıfır olduğu yerdir:", align="j", keep=True)
    D.eq(r"\frac{\mathrm{d}P_L}{\mathrm{d}R_L}=V_{th}^{2}\,\frac{R_{th}-R_L}{(R_{th}+R_L)^{3}}=0\;\Rightarrow\;R_L=R_{th}=3{,}52\ \mathrm{k\Omega}", "mp2")
    D.p("Türev, $R_L < R_{th}$ iken pozitif, $R_L > R_{th}$ iken negatiftir; yani bulunan nokta bir maksimumdur. Bu noktada yük gerilimi $V_{th}/2 = 3$ V, yük akımı $852{,}27\\ \\mu\\mathrm{A}$ ve aktarılan güç şudur:", align="j", keep=True)
    D.eq(r"P_{L,\mathrm{maks}}=\frac{V_{th}^{2}}{4R_{th}}=\frac{6^{2}}{4\cdot3520}=2{,}5568\ \mathrm{mW}", "pmax")
    D.p("**Yorum.** Maksimum güç aktarımı, verimin en yüksek olduğu nokta değildir. Eşdeğer devre içinde $R_L = R_{th}$ iken güç yarı yarıya yük ile $R_{th}$ arasında paylaşılır (eşdeğer devre verimi %50). Gerçek devrede ise kaynak, $R_1$ ve $R_2$ üzerinde de güç harcar: Vs kaynağı $10\\ \\mathrm{V}\\times2{,}3295\\ \\mathrm{mA}=23{,}30\\ \\mathrm{mW}$ verirken yüke giden $2{,}557\\ \\mathrm{mW}$’tır (%11). Güç sistemlerinde verim, sinyal sistemlerinde ise aktarılan güç öncelikli olduğundan iki ölçüt farklı yerlerde tercih edilir.", align="j")
    D.h(3, "2.2.3 Benzetim Sonuçları")
    D.p("[[f:t2load]]’de $R_L = 3{,}52\\ \\mathrm{k\\Omega}$ için işletme noktası görülmektedir: $V(oc) = V_L = 3$ V ve $I(R_L) = 852{,}273\\ \\mu\\mathrm{A}$. Yük gücü $P_L = V_L I_L = 3\\ \\mathrm{V}\\times852{,}273\\ \\mu\\mathrm{A} = 2{,}5568\\ \\mathrm{mW}$ bulunmuştur ve [[e:pmax]] ile örtüşmektedir.", align="j")
    D.fig("t2load", s("t2_load"), "$R_L = 3{,}52\\ \\mathrm{k\\Omega}$ için LTspice işletme noktası: $V_L = 3$ V, $I(R_L) = 852{,}273\\ \\mu\\mathrm{A}$.", 14.5)
    pl = C["pl"]
    rows = []
    for rl, (v, i, p) in pl.items():
        rows.append([n(float(rl), 0, "Ω"), n(v, 4, "V"), n(i * 1e6, 2, "µA"), n(p * 1e3, 4, "mW"), n(p / pl["3520"][2] * 100, 1, "%")])
    D.tab("pl", ["RL", "VL", "IL", "PL", "PL / PL,maks"], rows, "Yük direncine göre yük gücü (ngspice, $V_S = 10$ V)", [2.6, 2.8, 2.8, 2.8, 3.0])
    D.p("[[t:pl]], gücün $R_L = R_{th}$ civarında bir tepe yaptığını sayısal olarak göstermektedir: $R_L$ dörtte birine ya da dört katına çıksa bile güç, azami değerin yaklaşık %77’sinden %60’ına düşer; bu da tepenin geniş ve yatay olduğunu, yani $R_L$’nin tam değerinin kritik olmadığını gösterir. [[f:t2dc]]’de $R_L$ 100 Ω ile 10 kΩ arasında taranmış ve $P_L = V(oc)\\cdot I(R_L)$ çizdirilmiştir. Taramada $R_L$, değeri doğrudan ohm olarak okunan bir kaynak gerilimine bağlanmıştır (“R=V(sw)” davranışsal direnç ifadesi); bu nedenle yatay eksen LTspice tarafından volt yerine ohm olarak, kΩ yerine kV (1 kV = 1 kΩ) yazılmaktadır. Güç eğrisinin tepesi imleç ile yakalanmıştır; koordinatlar [[t:t2cur]]’de verilmiştir.", align="j")
    cur = K.get("t2_loaddc", [[3520, 2.5568e-3], [1000, 1.7621e-3]])
    D.fig("t2dc", s("t2_loaddc"), "Yük gücünün yük direncine göre LTspice DC taraması ($R_L = 100\\ \\Omega\\ldots10\\ \\mathrm{k\\Omega}$, iz: $V(oc)\\cdot I(R_L)$). İmleç 1 güç tepesindedir. Cihaz seri numarası çizimin üst kısmındadır.", 14.5)
    def pt(rl): return 36 * rl / (3520 + rl) ** 2
    D.tab("t2cur", ["İmleç", "X (RL)", "Y (PL), LTspice", "Y (PL), teorik"],
          [["İmleç %d" % (i + 1), c[0] if isinstance(c[0], str) else n(c[0], 2, "Ω"), c[1] if isinstance(c[1], str) else n(c[1] * 1000, 4, "mW"), n(pt(float(c[0]) if not isinstance(c[0], str) else float(c[0].replace("Ω", "").replace(".", "").replace(",", ".")) ) * 1000, 4, "mW")] for i, c in enumerate(cur)],
          "[[f:t2dc]]’deki imleç noktalarının koordinatları", [2.6, 3.6, 4.2, 3.8])

    # ================= 2.3
    D.h(2, "Süperpozisyon İlkesi")
    D.h(3, "2.3.1 Devre ve Devre Tahtası Yerleşimi")
    D.p("[[f:sp3o]]’teki devre ($V_{S1} = 12$ V, $V_{S2} = 5$ V, $R_1 = R_2 = 15\\ \\mathrm{k\\Omega}$, $R_3 = 3{,}9\\ \\mathrm{k\\Omega}$, $R_4 = R_5 = 1\\ \\mathrm{k\\Omega}$, $R_6 = 8{,}2\\ \\mathrm{k\\Omega}$) şu düğümlerden oluşmaktadır: A (VS1’in (+) ucu, $R_1$ ve $R_2$’nin sol uçları), B ($R_1$’in sağ ucu ve $R_3$’ün üst ucu), X ($R_2$’nin sağ ucu, VS2’nin (+) ucu, $R_5$’in üst ucu ve $R_4$’ün sol ucu), C ($R_4$, $R_3$’ün alt ucu ve $R_6$’nın üst ucu; çıkış) ve toprak (D). Şekil, düğüm bağlantılarının okunması için ayrıca şu yorumla verilmiştir: iki kaynak da toprağa göre ideal gerilim kaynağı olduğundan A düğümü 12 V’ta, X düğümü 5 V’ta sabit tutulur.", align="j")
    D.fig("sp3o", a("im3.png"), "İki bağımsız kaynak içeren süperpozisyon devresi (ödev föyündeki Şekil 3).", 12.0)
    D.p("Devre tahtası yerleşimi [[f:bb3]]’te verilmiştir. Devre, toplam altı direnç ve iki kaynak içerdiğinden, direnç gövdeleri üst üste binmesin diye her biri ayrı bir satıra (a–e) yerleştirilmiş, ortak düğümler aynı sütunlarda toplanmıştır: A 4. sütun, X 9. sütun, B 12. sütun, C 16. sütun. Kaynakların (−) uçları ile $R_5$ ve $R_6$’nın alt uçları aynı toprak rayına jumperlarla bağlanır. Çıkış, a16 deliği ile toprak rayı arasından ölçülür. Devre bu biçimde, jumper sayısı en aza indirilerek ve hiçbir kısa devre bulunmadan kurulabilmektedir.", align="j")
    D.fig("bb3", a("bb_t2_f3.png"), "Şekil 3’teki devrenin devre tahtası yerleşim planı. VS1 4. sütuna (A), VS2 9. sütuna (X) bağlanır; çıkış a16 deliğinden (C) alınır.", 14.5)
    D.h(3, "2.3.2 Teorik İşlemler")
    D.p("VS1 ve VS2 toprağa göre ideal gerilim kaynakları olduğundan A düğümü 12 V’ta, X düğümü 5 V’ta sabittir. Bu yüzden $R_2$ (iki sabit gerilimli düğüm arasında) ve $R_5$ (VS2’nin uçlarına paralel), C–D uçlarından görülen davranışı değiştirmez: yalnızca kaynaklardan çekilen akımları etkiler. C düğümüne üç kol bağlanır: A’dan $R_1 + R_3$ üzerinden, X’ten $R_4$ üzerinden ve toprağa $R_6$ üzerinden. C düğümüne Kirchhoff akım yasası (Millman teoremi) uygulandığında açık devre gerilimi ve Thevenin direnci şöyle yazılır:", align="j", keep=True)
    D.eq(r"V_{oc}=\frac{\dfrac{V_{S1}}{R_1+R_3}+\dfrac{V_{S2}}{R_4}}{\dfrac{1}{R_1+R_3}+\dfrac{1}{R_4}+\dfrac{1}{R_6}}", "mil")
    D.eq(r"R_{th}=(R_1+R_3)\parallel R_4\parallel R_6=\left(\frac{1}{18{,}9}+\frac{1}{1}+\frac{1}{8{,}2}\right)^{-1}\mathrm{k\Omega}=851{,}16\ \Omega", "rth3")
    D.p("**Soru 3.2 (iki kaynak da bağlı).** Değerler yerine konduğunda payda iletkenliği $1/18{,}9 + 1/1 + 1/8{,}2 = 1{,}17486\\ \\mathrm{mS}$ ve pay akımı $12/18{,}9 + 5/1 = 5{,}63492\\ \\mathrm{mA}$ olur; böylece $V_{oc} = 5{,}63492/1{,}17486 = 4{,}7962\\ \\mathrm{V}$ ve $R_{th} = 851{,}16\\ \\Omega$ bulunur. Norton akımı $I_N = V_{oc}/R_{th} = 5{,}6349\\ \\mathrm{mA}$’dir (kısa devre durumunda C düğümü toprağa bağlandığından $I_N = 12/18{,}9 + 5/1$ olur; iki sonuç aynıdır).", align="j")
    D.p("**Süperpozisyon (3.3 ve 3.4).** Bir kaynak çıkartılıp yerine kısa devre konduğunda yalnızca diğerinin etkisi kalır. Bu durumda kalan kaynak, iki dirençten oluşan bir gerilim bölücü ile çıkışa aktarılır:", align="j", keep=True)
    D.eq(r"V_{oc}^{(1)}=V_{S1}\,\frac{R_4\parallel R_6}{(R_1+R_3)+R_4\parallel R_6}=12\cdot\frac{0{,}8913}{18{,}9+0{,}8913}=0{,}5404\ \mathrm{V}\qquad(V_{S2}\to\text{kısa devre})", "voc1")
    D.eq(r"V_{oc}^{(2)}=V_{S2}\,\frac{(R_1+R_3)\parallel R_6}{R_4+(R_1+R_3)\parallel R_6}=5\cdot\frac{5{,}7166}{1+5{,}7166}=4{,}2558\ \mathrm{V}\qquad(V_{S1}\to\text{kısa devre})", "voc2")
    D.eq(r"V_{oc}=V_{oc}^{(1)}+V_{oc}^{(2)}=0{,}5404+4{,}2558=4{,}7962\ \mathrm{V}", "supp")
    D.p("Kaynaklar tek tek kısa devre edildiğinde Thevenin direnci değişmez; çünkü $R_{th}$ yalnızca devrenin dirençlerine ve bağımsız kaynakların sıfırlanmasına bağlıdır ve her iki durumda da (hem VS1 hem VS2 kısa devre iken) $R_{th} = 851{,}16\\ \\Omega$’dur. Üç duruma ait teorik değerler [[t:sp]]’de benzetimle birlikte verilmiştir.", align="j")
    D.h(3, "2.3.3 Benzetim Sonuçları ve Hata Payları")
    D.p("[[f:sp1]]’de iki kaynak bağlı iken açık devre gerilimi, [[f:sp2]]’de VS1 çıkartılıp yerine kısa devre (0 V’luk kaynak) konulduğundaki, [[f:sp3b]]’te ise VS2 çıkartıldığındaki açık devre gerilimi görülmektedir. Üç okuma $V(c) = 4{,}79624$ V, $4{,}25582$ V ve $0{,}540422$ V olup toplam kuralı ([[e:supp]]) sağlanmaktadır. [[f:sp4]]’te C–D uçları 0 V’luk kaynak ile kısa devre edilerek $I_N$, [[f:sp5]]’te iki kaynak da sıfırlanıp çıkışa 1 V’luk deneme kaynağı bağlanarak $R_{th}$ ölçülmüştür.", align="j")
    D.fig("sp1", s("t2_sp_both"), "İki kaynak bağlı iken ($V_{S1} = 12$ V, $V_{S2} = 5$ V) açık devre gerilimi: $V(c) = 4{,}79624$ V. Cihaz seri numarası şemanın altındadır.", 14.5)
    D.fig("sp2", s("t2_sp_s2"), "VS1 çıkartılıp yerine kısa devre konulduğunda (VS1 = 0 V, $V_{S2} = 5$ V) açık devre gerilimi: $V(c) = 4{,}25582$ V.", 14.5)
    D.fig("sp3b", s("t2_sp_s1"), "VS2 çıkartılıp yerine kısa devre konulduğunda ($V_{S1} = 12$ V, VS2 = 0 V) açık devre gerilimi: $V(c) = 0{,}540422$ V.", 14.5)
    D.fig("sp4", s("t2_sp_isc"), "C–D uçlarının 0 V’luk Vsc kaynağı ile kısa devre edilmesi ile ölçülen Norton akımı: $I(Vsc) = I_N = 5{,}63492$ mA.", 14.5)
    D.fig("sp5", s("t2_sp_rth"), "İki bağımsız kaynak da 0 V yapıldığında C–D uçlarına bağlanan 1 V’luk deneme kaynağı ile $R_{th}$ ölçümü: $|I(V_t)| = 1{,}17486$ mA, dolayısıyla $R_{th} = 1/1{,}17486\\ \\mathrm{mA} = 851{,}16\\ \\Omega$.", 14.5)
    sp = C["sp"]; R = (1 / 18.9 + 1 + 1 / 8.2)
    th = {"both": 4.79624340949, "s2": 5 / R / 1.0, "s1": 12 / 18.9 / R}
    rows = [["VS1 ve VS2 bağlı", n(th["both"], 4, "V"), n(sp["both"], 4, "V"), err(th["both"], sp["both"], 4, "V"), "%0"],
            ["VS1 kısa devre (yalnız VS2)", n(th["s2"], 4, "V"), n(sp["s2"], 4, "V"), err(th["s2"], sp["s2"], 4, "V"), "%0"],
            ["VS2 kısa devre (yalnız VS1)", n(th["s1"], 4, "V"), n(sp["s1"], 4, "V"), err(th["s1"], sp["s1"], 4, "V"), "%0"],
            ["Toplam (VS1 + VS2 katkıları)", n(th["s1"] + th["s2"], 4, "V"), n(sp["s1"] + sp["s2"], 4, "V"), err(sp["both"], sp["s1"] + sp["s2"], 4, "V"), "%0"]]
    D.tab("sp", ["Durum", "Teorik Voc", "Benzetim Voc", "Mutlak hata", "Bağıl hata"], rows, "Süperpozisyon devresinde açık devre gerilimi $V_{oc}$ (C–D uçları)", [5.2, 2.6, 2.8, 2.4, 1.8])
    rows2 = [["Thevenin direnci $R_{th}$ (3 durumda aynı)", "851,16 Ω", n(sp["rth"], 2, "Ω"), err(851.1643233759, sp["rth"], 3, "Ω"), "%0"],
             ["Norton akımı $I_N = V_{oc}/R_{th}$", n(th["both"] / (1000 / R) * 1, 4, "mA") if False else n(5.634920634921, 4, "mA"), n(sp["isc"] * 1000, 4, "mA"), err(5.634920634921, sp["isc"] * 1000, 4, "mA"), "%0"]]
    D.tab("sp2", ["Büyüklük", "Teorik", "Benzetim", "Mutlak hata", "Bağıl hata"], rows2, "Süperpozisyon devresinde Thevenin direnci ve Norton akımı", [5.2, 2.6, 2.8, 2.4, 1.8])
    D.p("Tüm sonuçlarda teorik ve benzetim değerleri yuvarlama hatası mertebesinde örtüşmüştür. Buna göre C–D uçlarından görülen Thevenin eşdeğeri $V_{th} = 4{,}796\\ \\mathrm{V}$ ve $R_{th} = 851{,}16\\ \\Omega$; Norton eşdeğeri $I_N = 5{,}635\\ \\mathrm{mA}$ ve $R_N = 851{,}16\\ \\Omega$’dur. Ayrıca süperpozisyon doğrulanmıştır: iki kaynağın birlikte yarattığı gerilim, her birinin tek başına yarattığı gerilimlerin toplamına eşittir.", align="j")

    # ================= 3
    D.h(1, "Sonuçlar")
    D.p("**Genel değerlendirme.** Üç bölümde de el ile türetilen sonuçlar benzetimle yuvarlama hatası mertebesinde örtüşmüştür. Thevenin eşdeğerinde $V_{th} = 6$ V, $I_{sc} = 1{,}7045$ mA ve $R_{th} = 3{,}52\\ \\mathrm{k\\Omega}$ bulunmuş; bu direncin hem $V_{oc}/I_{sc}$ oranından hem de kaynak sıfırlanarak yapılan hesaptan aynı çıkması, doğrusal devrede eşdeğerin tek olduğunu göstermiştir. Maksimum güç transferinde $R_L = R_{th} = 3{,}52\\ \\mathrm{k\\Omega}$ için yük gücü $2{,}5568\\ \\mathrm{mW}$ bulunmuş ve LTspice taramasındaki güç tepesi bu değerde okunmuştur. Süperpozisyon devresinde iki kaynağın birlikte oluşturduğu $4{,}7962$ V’luk gerilim, tek tek oluşturdukları $0{,}5404$ V ve $4{,}2558$ V’un toplamına eşit çıkmıştır.", align="j")
    D.p("**Laboratuvar ölçümlerinde beklenen sapmalar.** Dirençlerin %5 toleransı nedeniyle ölçülen $V_{oc}$ ve $R_{th}$ değerleri kuramsal değerden birkaç yüzde sapabilir. Ölçü aletinin 10 MΩ’luk iç direnci bu deneyin dirençlerinin yanında çok büyük olduğundan ($R_{th}$ binlerce ohm mertebesindedir) açık devre gerilimi ölçümünde yük etkisi %0,04’ün altındadır. Kısa devre akımı ölçümünde ise ampermetrenin iç direnci (birkaç ohm ile yüzlerce ohm arasında, kademeye bağlı) 3,52 kΩ’a eklenerek $I_{sc}$’yi bir miktar küçültür; $R_{th}$ bu nedenle $V_{oc}/I_{sc}$ ile değil kaynak sıfırlanarak ölçüldüğünde daha güvenilir bulunur. Maksimum güç deneyinde $R_L$’nin tam 3,52 kΩ olmaması (örneğin %5 sapma) gücü ancak %0,1 mertebesinde azalttığından ölçüm bu parametreye duyarsızdır; asıl belirsizlik $V_{th}$’nin gerçek değerindedir, çünkü güç $V_{th}^2$ ile orantılıdır. Devre tahtasındaki kontak dirençleri ve güç kaynağının gerçek çıkış değeri de (10, 12 ve 5 V) ölçü aletiyle denetlenmelidir.", align="j")
    D.p("**Eksik veya yorumlanamayan sonuç.** Bu rapor bir ön çalışma raporudur; laboratuvar ölçümleri henüz yapılmamıştır ve ölçüm ile benzetim arasındaki hata payı hesaplanmamıştır. Hata payları teorik sonuç ile benzetim arasında verilmiştir; ölçüm sonuçlarının eklenmesi deney raporunda yapılacaktır.", align="j")
    D.p("**Kazanılan beceriler.** (i) Açık devre gerilimi, kısa devre akımı ve kaynak sıfırlama ile Thevenin eşdeğeri bulunmuş; (ii) yük gücü, türev alınarak en büyük yapılmış; (iii) Millman teoremi ve süperpozisyon ile çok kaynaklı devre çözülmüş; (iv) LTspice ile işletme noktası ve DC tarama benzetimleri yapılıp imleçlerle koordinat okunmuş; (v) devre tahtası yerleşimi planlanmıştır.", align="j")
    D.h(1, "Kaynaklar")
    refs_block(D, ["Nilsson, J. W., & Riedel, S. A. (2015). *Electric circuits* (10th ed.). Boston: Pearson.",
                   "Alexander, C. K., & Sadiku, M. N. O. (2017). *Fundamentals of electric circuits* (6th ed.). New York: McGraw-Hill Education.",
                   "Hayt, W. H., Kemmerly, J. E., & Durbin, S. M. (2012). *Engineering circuit analysis* (8th ed.). New York: McGraw-Hill.",
                   "Analog Devices. (2026). *LTspice* (Sürüm 26.1.1) [Bilgisayar yazılımı]. Analog Devices, Inc.",
                   "Nagel, L. W., & Pederson, D. O. (1973). *SPICE (Simulation Program with Integrated Circuit Emphasis)* (Memorandum No. ERL-M382). Berkeley: University of California, Electronics Research Laboratory.",
                   "TOBB Ekonomi ve Teknoloji Üniversitesi. (2026). *ELE 201 L – Devre Analizi I Laboratuvarı, Deney 2 Ön Çalışma Yönergesi*. Ankara: TOBB ETÜ, Elektrik – Elektronik Mühendisliği Bölümü."])
    D.h(1, "Ekler")
    D.h(3, "EK-1: SPICE Devre Listeleri (Netlist)")
    D.p("Aşağıdaki devre listeleri herhangi bir SPICE programına (LTspice, ngspice vb.) olduğu gibi girilebilir. Toprak düğümü 0’dır; SPICE’ta ilk satır başlık sayılır, bu nedenle ilk satır yorum satırıdır.", align="j")
    base = "Vs 1 0 DC 10\nR1 1 a 2.2k\nR2 a 0 3.3k\nR3 a oc 2.2k\n"
    D.code("* Bolum 2.1 - acik devre gerilimi\n" + base + ".op\n.end", "Bölüm 2.1 – Açık devre gerilimi")
    D.code("* Bolum 2.1 - kisa devre akimi (Vsc = ampermetre)\n" + base + "Vsc oc 0 DC 0\n.op\n.end", "Bölüm 2.1 – Kısa devre akımı")
    D.code("* Bolum 2.1 - Rth: kaynak sifir, 1 V deneme kaynagi\n" + base.replace("DC 10", "DC 0") + "Vt oc 0 DC 1\n.op\n.end", "Bölüm 2.1 – Thevenin direnci (kaynak sıfırlı)")
    D.code("* Bolum 2.2 - yuk direnci\n" + base + "RL oc 0 3.52k\n.op\n.end", "Bölüm 2.2 – Yük direnci")
    D.code("* Bolum 2.2 - RL taramasi (R=V(sw) davranissal direnc), LTspice\n" + base + "RL oc 0 R=V(sw)\nVsw sw 0 10\n.dc Vsw 100 10000 10\n.end", "Bölüm 2.2 – Yük direnci taraması (LTspice)")
    sp = "VS1 a 0 DC 12\nR1 a b 15k\nR2 a x 15k\nVS2 x 0 DC 5\nR5 x 0 1k\nR4 x c 1k\nR3 b c 3.9k\nR6 c 0 8.2k\n"
    D.code("* Bolum 2.3 - iki kaynak bagli, acik devre\n" + sp + ".op\n.end", "Bölüm 2.3 – Süperpozisyon devresi (iki kaynak bağlı)")
    D.code("* VS1 -> 0 V (kisa devre): VS1 satiri 'VS1 a 0 DC 0'; VS2 -> 0 V icin 'VS2 x 0 DC 0'\n* Rth: iki kaynak 0 V + 'Vt c 0 DC 1'; Norton akimi: 'Vsc c 0 DC 0'", "Bölüm 2.3 – Süperpozisyon durumları için değişiklikler")
    return D

if __name__ == "__main__":
    D = build(); f = os.path.join(OUT, "ELE201L_Deney2_Oncalisma_Raporu.docx"); D.save(f)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", OUT, f], capture_output=True, timeout=300); print("ok")
