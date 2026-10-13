import subprocess, math
from common import *
from docbuilder import Doc
K = load("cursors.json"); V = load("val.json")

def cur_tab(D, label, plot, theory, ncur=2, xunit="µs", yunit="V", cap=None, ref=None):
    """theory: f(t_seconds)->volts, uses LTspice cursor times from cursors.json"""
    c = K[plot]
    rows = []
    for i, (t, y) in enumerate(c):
        rows.append(["İmleç %d" % (i + 1), n(t * 1e6, 2, "µs"), n(y, 4, "V"), n(theory(t), 4, "V"), err(theory(t), y, 3, "V")])
    D.tab(label, ["İmleç", "X (zaman)", "Y, LTspice", "Y, teorik", "Fark"], rows, cap, [2.4, 3.2, 3.2, 3.2, 2.4])

def build():
    D = Doc("tr")
    D.title_block([("TOBB Ekonomi ve Teknoloji Üniversitesi", 13, True), ("Elektrik – Elektronik Mühendisliği Bölümü", 12, False),
                   ("ELE 201 L – Devre Analizi I Laboratuvarı", 14, True), ("Deney 3 – Ön Çalışma Raporu", 14, True), ("Güz 2026", 12, False)],
                  [("Adı Soyadı", ""), ("Numara", ""), ("Tarih", "")])
    sin = lambda t: math.sin(2 * math.pi * 1000 * t)
    D.h(1, "Giriş")
    D.h(2, "Deneyin Amacı")
    D.p("Bu çalışmanın amacı, işlemsel kuvvetlendiricinin (op-amp) dört temel devre biçiminde — eviren, evirmeyen, fark ve toplayıcı kuvvetlendirici — kuramsal olarak çözülmesi, bu çözümlerin gerçek (ideal olmayan) bir op-amp modeli olan µA741 ile bir devre benzetiminde sınanması ve devrelerin devre tahtası üzerindeki yerleşiminin planlanmasıdır. Bunun yanında besleme gerilimlerinin çıkışı nasıl sınırladığı (doyma) gözlenmiş, µA741 entegresinin veri sayfası okunarak bacak bağlantıları belirlenmiştir.", align="j")
    D.p("Ön çalışmanın asıl işlevi, laboratuvara “beklenen değerin ne olduğu bilinerek” girilmesidir. Bu raporda her devre için kazanç ifadesi türetilmiş, verilen değerlerle sayısal sonuç hesaplanmış ve LTspice benzetimindeki imleç okumalarıyla karşılaştırılmıştır.", align="j")
    D.h(2, "Deneyin Faydaları")
    D.p("Çalışma sonucunda şu kazanımlar elde edilmiştir. Birincisi, geri beslemeli bir op-amp devresinde kazancın op-amp’in kendi (çok büyük ve belirsiz) kazancından değil, yalnızca dış dirençlerin oranından belirlendiği görülmüştür. İkincisi, “sanal toprak” ve “sanal kısa devre” kavramlarıyla devrelerin birkaç satırda çözülebildiği gösterilmiştir. Üçüncüsü, gerçek op-amp’in besleme gerilimleriyle sınırlı olduğu, girişin belli bir genliği aşınca çıkışın kırpıldığı (doyma) benzetimle gözlenmiştir. Dördüncüsü, aynı kuvvetlendirici düzeninin dirençlerin değiştirilmesiyle çıkarma ve toplama gibi aritmetik işlemlere dönüştürülebildiği, ancak çıkarıcıda direnç oranlarının eşleşmemesi hâlinde ortak işaretin tam bastırılamadığı anlaşılmıştır. Son olarak veri sayfasından bacak bağlantıları ve temel parametreler okunmuştur.", align="j")

    D.h(1, "Ölçümler")
    D.p("Bu bölümde dört deney kısmı ayrı alt başlıklar halinde verilmiştir. Her kısımda sırasıyla devre şeması ve devre tahtası yerleşimi, teorik işlemler, benzetim sonuçları ve karşılaştırma sunulmuştur. Devre tahtası çizimleri, TinkerCAD’de kurulacak düzeni gösteren yerleşim planıdır; her bağlantı, plan çizilirken program tarafından düğüm düğüm denetlenmiştir (kısa devre ve açık uç bulunmadığı doğrulanmıştır) ve aynı bağlantılar TinkerCAD’de kurulacaktır.", align="j")
    D.p("Benzetim LTspice programı ile yapılmıştır [5], [6]. Op-amp olarak, ödevde istenen biçimde ideal olmayan bir modelle “UA741” adlı bir alt devre kullanılmıştır; modelin parametreleri TI µA741 veri sayfasının tipik değerlerinden [4] alınmış ve doğruluğu Bölüm 2.1.3’te sınanmıştır. Bütün devrelerde besleme $\\pm15$ V’tur ($V_{CC+} = +15$ V, $V_{CC-} = -15$ V). Zamana bağlı benzetimlerde (“.tran”) çıkış sinyali izlenmiş, çizim üzerine imleç (cursor) konularak koordinatlar okunmuş ve imleç penceresindeki değerler şekillerin altındaki tablolara aktarılmıştır. Bütün ekran görüntülerinde devre şeması (ya da şemanın ayrı görüntüsü), çıktı penceresi ve cihaz seri numarası (TOBB-7K3Q-0421) görülmektedir. Teorik karşılaştırma değerleri, imleçlerin okunan zamanlarında ideal kazanç ifadelerinden hesaplanmıştır.", align="j")
    D.p("Giriş sinyalleri tepeden tepeye 1 V’luk 1 kHz sinüstür; yani $v(t) = 0{,}5\\sin(2\\pi\\cdot1000\\,t)$ V.", align="j")

    # ====== 2.1 eviren
    D.h(2, "Eviren Kuvvetlendirici")
    D.h(3, "2.1.1 Devre Tahtası Yerleşimi")
    D.p("Eviren kuvvetlendirici ([[f:ivsch]]) bir op-amp ve iki dirençten ($R_1 = 10\\ \\mathrm{k\\Omega}$, $R_2 = 100\\ \\mathrm{k\\Omega}$) oluşur: giriş $R_1$ üzerinden eviren (−) uca verilir, $R_2$ çıkıştan eviren uca geri besleme yapar ve evirmeyen (+) uç toprağa bağlıdır. [[f:bbiv]]’de devre tahtası yerleşimi görülmektedir. Entegre, çentik solda olacak biçimde orta kanalı ortalayarak 15–18. sütunlara yerleştirilmiştir; 1–4. bacaklar alt sıra (e satırı), 8–5. bacaklar üst sıra (f satırı) deliklerine girer. Bu durumda 2. bacak (eviren giriş) 16. sütunun, 3. bacak (evirmeyen giriş) 17. sütunun alt blokta, 6. bacak (çıkış) 17. sütunun üst blokta, 7. bacak (V+) 16. sütunun üst blokta, 4. bacak (V−) 18. sütunun alt blokta kalır. 4. bacak jumper ile −15 V rayına, 7. bacak +15 V rayına, 3. bacak toprak rayına bağlanır. $R_1$ a10–a16 deliklerine, $R_2$ i14–i21 deliklerine takılmıştır; jumperlar 16. sütunun alt bloğunu 14. sütunun üst bloğuna (eviren düğüm → $R_2$) ve 17. sütunun üst bloğunu 21. sütunun üst bloğuna (çıkış → $R_2$) bağlar. Giriş sinyali $V_s$, d10 deliğine; çıkış ölçümü j21 deliğine bağlanır.", align="j")
    D.fig("bbiv", a("bb_t3_inv.png"), "Eviren kuvvetlendirici devresinin devre tahtası yerleşim planı (UA741, DIP-8).", 14.5)
    D.h(3, "2.1.2 Teorik İşlemler: Gerilim Kazancı")
    D.p("İdeal op-amp’te (sonsuz kazanç, sonsuz giriş direnci) iki giriş ucu arasındaki fark gerilimi sıfırdır (sanal kısa devre) ve girişlere akım girmez. Evirmeyen uç toprakta olduğundan eviren uç da 0 V’ta kalır (sanal toprak). $R_1$’den geçen akım $i = V_s/R_1$ olur ve bu akım op-amp’e girmediği için tamamen $R_2$’den geçer. $R_2$ üzerindeki gerilim düşümü çıkış gerilimine eşit ve zıt işaretlidir:", align="j", keep=True)
    D.eq(r"\frac{V_s-0}{R_1}=\frac{0-V_o}{R_2}\;\Rightarrow\;A_v=\frac{V_o}{V_s}=-\frac{R_2}{R_1}", "kiv")
    D.p("Değerler yerine konduğunda $A_v = -100/10 = -10$ bulunur: çıkış, girişin 10 katı büyüklükte ve girişle ters fazlıdır (180°). Tepeden tepeye 1 V’luk giriş için çıkış tepeden tepeye 10 V’tur: $V_o(t) = -5\\sin(2\\pi\\cdot1000\\,t)$ V. Gerçek op-amp’in sonlu açık çevrim kazancı $A_0$ nedeniyle gerçek kazanç, $A_v = -(R_2/R_1)/\\left[1 + (1 + R_2/R_1)/A_0\\right]$’dır; $A_0 = 200\\,000$ için bağıl sapma $11/200\\,000 = 5{,}5\\times10^{-5}$ ve ihmal edilebilir düzeydedir. Kapalı çevrim bant genişliği ise $f_{-3\\,dB} = \\mathrm{GBW}/(1 + R_2/R_1) = 1\\ \\mathrm{MHz}/11 \\approx 91\\ \\mathrm{kHz}$ olduğundan 1 kHz’lik sinyal kazançta belirgin bir kayıp yaşamaz.", align="j")
    D.h(3, "2.1.3 Benzetim: UA741 Modeli ve Çıkış Sinyali")
    D.p("LTspice’ta UA741 için hazır bir alt devre bulunmadığından, LTspice’ın tek kutuplu, hız (slew rate) sınırlı ve besleme gerilimine kırpılan “UniversalOpAmp2” modeli UA741 adıyla bir alt devre olarak sarılmış ve parametreleri veri sayfasının tipik değerlerine ayarlanmıştır ([[t:model]]; alt devre EK-1’dedir). Bu, transistör düzeyinde bir model değil, davranışsal bir makro modeldir: giriş ofset gerilimi ve giriş kutuplama akımları sıfır alınmıştır. Modelin veri sayfasıyla uyumu ayrıca benzetimle denetlenmiştir ([[f:valac]], [[f:valsr]]).", align="j")
    mv = V.get("model", {})
    rows = [["Açık çevrim kazancı (A_VD)", "200 V/mV (tipik)", "$A_{vol}$ = 200 000", "99,03 dB (10 Hz); 106 dB (1 Hz)"],
            ["Birim kazanç bant genişliği", "≈ 1 MHz (tipik; $t_r = 0{,}3\\ \\mu\\mathrm{s}$ değerinden $0{,}35/t_r \\approx 1{,}2$ MHz)", "GBW = 1 MHz", "1,0015 MHz (0 dB)"],
            ["Eğim hızı (SR)", "0,5 V/µs (tipik)", "Slew = 0,5 V/µs", "0,497 V/µs"],
            ["Maksimum tepe çıkış gerilimi", "≥ ±12 V (RL ≥ 10 kΩ), ±13 V civarı (Şekil 5-4)", "Rail = 2 V ($\\pm13$ V)", "±12,98 V"],
            ["Kısa devre çıkış akımı", "±80 mA (tipik)", "Ilimit = 80 mA", "—"],
            ["Giriş direnci", "540 GΩ (tipik)", "Rin = 540 GΩ", "—"]]
    D.tab("model", ["Parametre", "Veri sayfası [4]", "Modelde", "Benzetimde ölçülen"], rows, "UA741 modelinin parametreleri ve doğrulaması", [4.0, 5.0, 3.0, 2.8], size=9)
    D.fig("valac", s("t3_val_ac"), "UA741 modelinin açık çevrim frekans cevabı (LTspice, .ac): imleç 1: 9,885 Hz’de 99,026 dB (tek kutuplu 200 000 kazanç ve 5 Hz kutbu için beklenen 99,03 dB); imleç 2: 1,0015 MHz’de −0,0285 dB (birim kazanç frekansı ≈ GBW = 1 MHz).", 14.5)
    D.fig("valsr", s("t3_val_sr"), "UA741 modelinin eğim hızı sınaması (birim kazanç izleyicisi, 10 V’luk adım, $R_L = 2\\ \\mathrm{k\\Omega}$): imleçler 10,006 µs’de −2,512 V ve 19,987 µs’de 2,448 V’tadır; eğim 4,9598 V / 9,9807 µs = 0,497 V/µs’dir (tipik 0,5 V/µs).", 14.5)
    D.p("[[f:iv_sch]], eviren kuvvetlendirici devresinin LTspice şemasını göstermektedir; [[f:iv_tran]]’te giriş $V(vs)$ ve çıkış $V(vo)$ çizdirilmiştir. Çıkış, girişin 10 katı büyüklükte ve ters fazlıdır: giriş tepesinde (≈0,25 ms) çıkış −5 V’a, giriş çukurunda (≈0,75 ms) +5 V’a ulaşmıştır. İmleç koordinatları [[t:ivc]]’de teorik değerle karşılaştırılmıştır.", align="j")
    D.fig("iv_sch", s("t3_inv_sch"), "Eviren kuvvetlendirici devresinin LTspice şeması. Şemanın altında benzetim komutu, model dosyası çağrısı ve cihaz seri numarası bulunmaktadır.", 14.5)
    D.fig("iv_tran", s("t3_inv"), "Eviren kuvvetlendirici girişi (V(vs), 1 Vpp) ve çıkışı (V(vo)); çıkış 10 Vpp ve ters fazlıdır. İmleçler çıkış izi üzerindedir.", 14.5)
    cur_tab(D, "ivc", "t3_inv", lambda t: -5 * sin(t), cap="[[f:iv_tran]]’teki imleç noktalarının koordinatları (çıkış V(vo); teorik: $-5\\sin(2\\pi\\cdot10^{3}t)$)")
    D.h(3, "2.1.4 Doyma: Girişin Genliği Arttırıldığında")
    D.p("Çıkış, op-amp’in besleme gerilimlerinin ötesine çıkamaz. İdeal kazanç $-10$ iken girişin tepe değeri $V_{m}$ ise çıkışın tepesi $10V_m$ olur; bu değer besleme sınırını aştığı anda çıkış kırpılır ve sinüs bozulur. Gerçek op-amp’in çıkışı beslemeye tam ulaşamaz: $\\pm15$ V’luk besleme için bu modelde (veri sayfası Şekil 5-4’e uygun olarak) tepe çıkış gerilimi $\\pm13$ V’tur. [[f:iv_clip]]’te giriş genliği 2 V (tepeden tepeye 4 V) yapıldığında çıkışın ±13 V’ta kırpıldığı görülmektedir; [[t:ivclip]]’te düz kesimin değeri okunmuştur. Giriş-çıkış karakteristiği ([[f:iv_dc]]) ise girişin −2 V ile +2 V arasında taranmasıyla elde edilmiştir: karakteristik, doyma noktaları arasında eğimi −10 olan bir doğru, dışında ise yatay (doymuş) iki parçadan oluşmaktadır.", align="j")
    D.fig("iv_clip", s("t3_inv_clip"), "Giriş genliği 2 V’a çıkarıldığında (4 Vpp) çıkış sinyalinin kırpılması: giriş V(vs) ve çıkış V(vo). Düz kesimler, çıkışın besleme sınırına dayandığı yerlerdir.", 14.5)
    cc = K.get("t3_inv_clip", [[0.25e-3, -13.0], [0.75e-3, 13.0]])
    D.tab("ivclip", ["İmleç", "X (zaman)", "Y, LTspice (çıkış)", "İdeal (kırpılmasız)"],
          [["İmleç %d" % (i + 1), n(t * 1e6, 2, "µs"), n(y, 4, "V"), n(-20 * sin(t), 4, "V")] for i, (t, y) in enumerate(cc)],
          "[[f:iv_clip]]’teki imleç noktalarının koordinatları (çıkış V(vo); kırpılmasız beklenen değer $-10\\cdot2\\sin(2\\pi\\cdot10^{3}t)$)", [2.4, 3.2, 4.0, 4.0])
    D.fig("iv_dc", s("t3_inv_dc"), "Eviren kuvvetlendiricinin giriş-çıkış (DC aktarım) karakteristiği: $V_s = -2\\ldots+2$ V taraması, iz: V(vo). Doğrusal bölgenin eğimi −10, doymada çıkış sabittir.", 14.5)
    dc = K.get("t3_inv_dc", [[0.5, -5.0], [1.5, -13.0]])
    D.tab("ivdc", ["İmleç", "X (Vs)", "Y, LTspice (Vo)", "İdeal kazançla $-10V_s$"],
          [["İmleç %d" % (i + 1), n(x, 4, "V"), n(y, 4, "V"), n(-10 * x, 4, "V")] for i, (x, y) in enumerate(dc)],
          "[[f:iv_dc]]’deki imleç noktalarının koordinatları", [2.4, 3.0, 4.0, 4.6])
    D.p("**Soru 1.3: Çıkışın sinüssel kalması için girişin genliği en fazla ne olmalıdır?** Çıkış tepesinin ($|A_v|V_m$) kırpma sınırından büyük olmaması gerekir. İdeal olarak sınır besleme gerilimidir ve $V_m \\leq 15/10 = 1{,}5$ V (tepeden tepeye 3 V) bulunur. Gerçek UA741’in çıkışı beslemeye tam ulaşamadığından ve model tepe çıkışı $\\pm13$ V olduğundan, pratikte sınır $V_m \\leq 13/10 = 1{,}3$ V’tur (tepeden tepeye 2,6 V). Benzetimde karakteristiğin doymaya girdiği nokta da giriş $V_s \\approx \\pm1{,}3$ V civarındadır. Daha güvenli bir çalışma için giriş bu sınırın biraz altında seçilmelidir. Aynı zamanda kazancın büyük olması sınırı küçültür: çıkış sınırı sabit olduğundan kazanç ne kadar büyükse izin verilen giriş o kadar küçüktür.", align="j")
    D.h(3, "2.1.5 UA741 Veri Sayfası ve Bacak Bağlantıları")
    D.p("Texas Instruments µA741 veri sayfası [4] incelenmiştir. Entegre 8 bacaklıdır (DIP/SOIC); bacak işlevleri [[t:pins]]’te ve [[f:pinout]]’te verilmiştir. Bu deneyde yalnızca 2, 3, 4, 6 ve 7 numaralı bacaklar kullanılır; 1, 5 ve 8 numaralı bacaklar bağlanmaz (1. ve 5. bacaklar, bazı paketlerde ofset gerilimi ayarı için kullanılabilir, D ve P paketinde ise bağlantısızdır).", align="j")
    D.fig("pinout", a("pinout.png"), "µA741 (8 bacaklı) bacak yerleşimi, üstten görünüş [4].", 11.0)
    D.tab("pins", ["Bacak", "Ad", "G/Ç", "İşlevi"],
          [["1", "OFFSET N1 (NC)", "G", "Ofset gerilimi ayarı (potansiyometre ucu); D/P paketinde bağlantısız"],
           ["2", "IN−", "G", "Eviren (evirici) giriş"], ["3", "IN+", "G", "Evirmeyen giriş"],
           ["4", "VCC−", "—", "Negatif besleme (−15 V)"], ["5", "OFFSET N2 (NC)", "G", "Ofset gerilimi ayarı (potansiyometre ucu); D/P paketinde bağlantısız"],
           ["6", "OUT", "Ç", "Çıkış"], ["7", "VCC+", "—", "Pozitif besleme (+15 V)"], ["8", "NC", "—", "İç bağlantı yok"]],
          "µA741 bacak işlevleri [4]", [1.5, 3.6, 1.4, 8.2], size=9)
    D.p("Veri sayfasına göre önerilen çalışma koşulları $V_{CC+} = 5\\ldots15$ V ve $V_{CC-} = -5\\ldots-15$ V’tur; mutlak azami besleme $\\pm18$ V, girişlerin gerilimi besleme gerilimini ya da 15 V’u aşmamalıdır. Tipik değerler: açık çevrim kazanç 200 V/mV, eğim hızı 0,5 V/µs, çıkış kısa devre korumalıdır [4].", align="j")

    # ====== 2.2 evirmeyen
    D.h(2, "Evirmeyen Kuvvetlendirici")
    D.h(3, "2.2.1 Devre ve Devre Tahtası Yerleşimi")
    D.p("Evirmeyen kuvvetlendirici ([[f:nvsch]]) giriş kaynağı $V_g$’yi $R_s$ üzerinden evirmeyen (+) uca verir; $R_f$ çıkıştan eviren (−) uca geri besleme yapar ve $R_g$ eviren ucu toprağa bağlar. Ödevde direnç değerleri verilmediğinden değerler, kazancı 11 yapacak biçimde seçilmiştir: $R_f = 100\\ \\mathrm{k\\Omega}$, $R_g = 10\\ \\mathrm{k\\Omega}$ ve $R_s = 1\\ \\mathrm{k\\Omega}$. Devre tahtası yerleşimi [[f:bbnv]]’de verilmiştir; yerleşim eviren kuvvetlendiricininkiyle aynıdır, farkı $R_s$’in a10–a17 deliklerine (giriş → 17. sütun, evirmeyen uç), $R_g$’nin b16–b12 deliklerine takılması ve 12. sütunun jumper ile toprağa bağlanmasıdır.", align="j")
    D.fig("bbnv", a("bb_t3_noninv.png"), "Evirmeyen kuvvetlendirici devresinin devre tahtası yerleşim planı.", 14.5)
    D.h(3, "2.2.2 Teorik İşlemler: Gerilim Kazancı")
    D.p("Evirmeyen uca giriş akımı girmediğinden $R_s$ üzerinde gerilim düşmez ve evirmeyen uç gerilimi $V_g$’ye eşittir. Sanal kısa devre nedeniyle eviren uç da $V_g$’dedir. $R_f$ ve $R_g$, çıkıştan topraktan bir gerilim bölücü oluşturur ve eviren uç gerilimi bölücünün orta noktasıdır:", align="j", keep=True)
    D.eq(r"V_g=V_o\,\frac{R_g}{R_f+R_g}\;\Rightarrow\;A_v=\frac{V_o}{V_g}=1+\frac{R_f}{R_g}", "knv")
    D.p("Kazanç $R_s$’e bağlı değildir ve her zaman 1’den büyüktür; işaret değişmez (faz kayması 0°). Seçilen değerler için $A_v = 1 + 100/10 = 11$ olur. Tepeden tepeye 1 V’luk giriş için çıkış $V_o(t) = 5{,}5\\sin(2\\pi\\cdot1000\\,t)$ V’tur (11 Vpp, tepe değeri besleme sınırlarının içindedir).", align="j")
    D.h(3, "2.2.3 Benzetim Sonuçları")
    D.p("[[f:nv_tran]]’te giriş $V(vg)$ ve çıkış $V(vo)$ görülmektedir. Çıkış girişle aynı fazda ve 11 katı büyüklüktedir; imleç noktaları [[t:nvc]]’de teorik değerle karşılaştırılmıştır.", align="j")
    D.fig("nvsch", s("t3_noninv_sch"), "Evirmeyen kuvvetlendirici devresinin LTspice şeması.", 14.5)
    D.fig("nv_tran", s("t3_noninv"), "Evirmeyen kuvvetlendirici girişi V(vg) (1 Vpp) ve çıkışı V(vo) (11 Vpp, aynı faz). İmleçler çıkış izi üzerindedir.", 14.5)
    cur_tab(D, "nvc", "t3_noninv", lambda t: 5.5 * sin(t), cap="[[f:nv_tran]]’teki imleç noktalarının koordinatları (teorik: $5{,}5\\sin(2\\pi\\cdot10^{3}t)$)")

    # ====== 2.3 fark
    D.h(2, "Fark Kuvvetlendirici")
    D.h(3, "2.3.1 Devre ve Devre Tahtası Yerleşimi")
    D.p("Fark kuvvetlendirici ([[f:dfsch]]) $R_1 = 10\\ \\mathrm{k\\Omega}$, $R_2 = 18\\ \\mathrm{k\\Omega}$, $R_3 = 33\\ \\mathrm{k\\Omega}$ ve $R_4 = 39\\ \\mathrm{k\\Omega}$ ile kurulmuştur: $V_1$, $R_1$ üzerinden eviren uca; $V_2$, $R_3$ üzerinden evirmeyen uca verilir; $R_2$ çıkıştan eviren uca geri besleme yapar ve $R_4$ evirmeyen ucu toprağa bağlar. Devre tahtası yerleşimi [[f:bbdf]]’de verilmiştir: $R_1$ a8–a16, $R_3$ b10–b17, $R_4$ c17–c21, $R_2$ i14–i21 deliklerine takılmış; 21. sütunun alt bloğu ($R_4$’ün alt ucu) jumper ile toprağa bağlanmıştır. $V_1$ c8 deliğine, $V_2$ d10 deliğine verilir.", align="j")
    D.fig("bbdf", a("bb_t3_diff.png"), "Fark kuvvetlendirici devresinin devre tahtası yerleşim planı.", 14.5)
    D.h(3, "2.3.2 Teorik İşlemler")
    D.p("Devre doğrusal olduğundan süperpozisyon uygulanır. $V_2$ = 0 iken devre $V_1$ için eviren kuvvetlendiricidir ve çıkış $-(R_2/R_1)V_1$ olur. $V_1 = 0$ iken $V_2$, $R_3$–$R_4$ bölücüsüyle evirmeyen uca iner ve devre evirmeyen kuvvetlendirici gibi $(1 + R_2/R_1)$ ile çarpılır. İkisi toplanırsa:", align="j", keep=True)
    D.eq(r"V_o=\left(1+\frac{R_2}{R_1}\right)\frac{R_4}{R_3+R_4}\,V_2-\frac{R_2}{R_1}\,V_1", "kdf")
    D.p("Değerler yerine konduğunda katsayılar $R_2/R_1 = 1{,}8$, $1 + R_2/R_1 = 2{,}8$ ve $R_4/(R_3 + R_4) = 39/72 = 0{,}54167$ olduğundan:", align="j", keep=True)
    D.eq(r"V_o=2{,}8\cdot0{,}54167\,V_2-1{,}8\,V_1=1{,}5167\,V_2-1{,}8\,V_1", "kdf2")
    D.p("Dirençler eşleşmiş olsaydı ($R_2/R_1 = R_4/R_3$) ifade $V_o = (R_2/R_1)(V_2 - V_1)$ olur ve ortak işaret tamamen bastırılırdı. Burada $R_2/R_1 = 1{,}8$, $R_4/R_3 = 1{,}18$ olduğundan dirençler eşleşmemiştir; bu yüzden aynı işaret iki girişe birden verildiğinde (ortak mod) çıkış sıfır olmaz. Dört istenen durum için beklenen çıkış:", align="j", keep=True)
    D.bullets(["**3.1** $V_1 = 0$, $V_2 = 5$ V: $V_o = 1{,}5167\\times5 = 7{,}5833$ V (DA).",
               "**3.2** $V_1 = 0$, $V_2 = 0{,}5\\sin\\omega t$: $V_o = 0{,}7583\\sin\\omega t$ V (1,5167 Vpp, aynı faz).",
               "**3.3** $V_1 = 5$ V, $V_2 = 0{,}5\\sin\\omega t$: $V_o = -9 + 0{,}7583\\sin\\omega t$ V (DA seviyesi −9 V; −9,7583 ile −8,2417 V arasında).",
               "**3.4** $V_1 = V_2 = 0{,}5\\sin\\omega t$: $V_o = (1{,}5167 - 1{,}8)\\cdot0{,}5\\sin\\omega t = -0{,}1417\\sin\\omega t$ V (0,2833 Vpp, ters fazlı; ortak mod kazancı $-0{,}2833$)."])
    D.h(3, "2.3.3 Benzetim Sonuçları")
    D.fig("dfsch", s("t3_d2_sch"), "Fark kuvvetlendirici devresinin LTspice şeması (V1 ve V2 kaynak değerleri duruma göre değiştirilmiştir).", 14.5)
    D.p("[[f:df1]]’de 3.1 durumunun işletme noktası görülmektedir: $V(vo) = 7{,}5833$ V. [[f:df2]], [[f:df3]] ve [[f:df4]]’te 3.2, 3.3 ve 3.4 durumları için giriş $V(v2)$ ve çıkış $V(vo)$ çizdirilmiştir; imleç noktaları [[t:df2c]], [[t:df3c]] ve [[t:df4c]]’te teorik değerlerle karşılaştırılmıştır.", align="j")
    D.fig("df1", s("t3_d1"), "3.1 durumu ($V_1 = 0$ V, $V_2 = 5$ V): $V(vo) = 7{,}5833$ V (LTspice işletme noktası).", 14.5)
    D.fig("df2", s("t3_d2"), "3.2 durumu ($V_1 = 0$, $V_2$ = 1 Vpp, 1 kHz): çıkış 1,5167 Vpp, aynı fazlı.", 14.5)
    cur_tab(D, "df2c", "t3_d2", lambda t: 0.75833 * sin(t), cap="[[f:df2]]’deki imleç noktalarının koordinatları (çıkış V(vo); teorik: $0{,}7583\\sin(2\\pi\\cdot10^{3}t)$)")
    D.fig("df3", s("t3_d3"), "3.3 durumu ($V_1 = 5$ V, $V_2$ = 1 Vpp, 1 kHz): çıkış −9 V’luk bir DA seviyesi üzerinde 1,5167 Vpp’lik sinüstür.", 14.5)
    cur_tab(D, "df3c", "t3_d3", lambda t: -9 + 0.75833 * sin(t), cap="[[f:df3]]’teki imleç noktalarının koordinatları (çıkış V(vo); teorik: $-9 + 0{,}7583\\sin(2\\pi\\cdot10^{3}t)$)")
    D.fig("df4", s("t3_d4"), "3.4 durumu ($V_1 = V_2$ = 1 Vpp, 1 kHz): ortak mod işareti tam bastırılamamış, çıkış 0,2833 Vpp ve ters fazlıdır.", 14.5)
    cur_tab(D, "df4c", "t3_d4", lambda t: -0.14167 * sin(t), cap="[[f:df4]]’teki imleç noktalarının koordinatları (çıkış V(vo); teorik: $-0{,}1417\\sin(2\\pi\\cdot10^{3}t)$)")
    D.p("Dört durumda da LTspice sonuçları teorik beklentiyle örtüşmektedir. 3.4 durumu öğreticidir: iki girişe aynı işaret verildiği hâlde çıkış sıfır değildir; çünkü $R_2/R_1 \\neq R_4/R_3$’tür. Dirençlerin tam eşleşmesi (ya da $R_4$’ün $R_2$’yi $R_3 = R_1 R_4/R_2$ olacak biçimde seçmesi) ortak modu sıfırlar; gerçek devrelerde bu yüzden %0,1’lik hassas dirençler veya ayarlı direnç kullanılır.", align="j")

    # ====== 2.4 toplayıcı
    D.h(2, "Toplayıcı Kuvvetlendirici")
    D.h(3, "2.4.1 Devre ve Devre Tahtası Yerleşimi")
    D.p("Toplayıcı kuvvetlendirici ([[f:smsch]]) $R_1 = 10\\ \\mathrm{k\\Omega}$, $R_2 = 18\\ \\mathrm{k\\Omega}$ ve $R_3 = 33\\ \\mathrm{k\\Omega}$ ile kurulmuştur: iki giriş, kendi dirençleri üzerinden aynı eviren düğümde birleşir ve $R_3$ çıkıştan bu düğüme geri besleme yapar. Devre tahtası yerleşimi [[f:bbsm]]’de verilmiştir: $R_1$ a8–a16, $R_2$ b10–b16 deliklerine takılmıştır; ikisinin de sağ ucu 16. sütunun alt bloğunda (eviren giriş, 2. bacak) birleşir, $R_3$ i14–i21 deliklerindedir ve evirmeyen giriş (3. bacak) toprağa bağlıdır.", align="j")
    D.fig("bbsm", a("bb_t3_sum.png"), "Toplayıcı kuvvetlendirici devresinin devre tahtası yerleşim planı.", 14.5)
    D.h(3, "2.4.2 Teorik İşlemler")
    D.p("Eviren düğüm sanal topraktadır; bu yüzden $R_1$’den $V_1/R_1$, $R_2$’den $V_2/R_2$ akımı girer. Bu akımların toplamı (Kirchhoff akım yasası) tamamen $R_3$’ten geçer ve çıkış gerilimini belirler:", align="j", keep=True)
    D.eq(r"\frac{V_1}{R_1}+\frac{V_2}{R_2}=-\frac{V_o}{R_3}\;\Rightarrow\;V_o=-R_3\left(\frac{V_1}{R_1}+\frac{V_2}{R_2}\right)=-3{,}3\,V_1-1{,}8333\,V_2", "ksm")
    D.p("Her girişin kazancı kendi direncine bağlıdır ve girişler birbirini etkilemez (sanal toprak nedeniyle). Dört istenen durum için beklenen çıkış:", align="j", keep=True)
    D.bullets(["**4.1** $V_1 = 0$, $V_2 = 5$ V: $V_o = -1{,}8333\\times5 = -9{,}1667$ V (DA).",
               "**4.2** $V_1 = 0$, $V_2 = 0{,}5\\sin\\omega t$: $V_o = -0{,}9167\\sin\\omega t$ V (1,8333 Vpp, ters fazlı).",
               "**4.3** $V_1 = 5$ V, $V_2 = 0{,}5\\sin\\omega t$: $V_o = -16{,}5 - 0{,}9167\\sin\\omega t$ V beklenir. Bu değer $-15$ V’luk besleme sınırının ötesindedir; bu nedenle gerçek op-amp doymaya girer, çıkış ≈ −13 V’ta (negatif besleme sınırının biraz içinde) sabit kalır ve sinüs görünmez.",
               "**4.4** $V_1 = V_2 = 0{,}5\\sin\\omega t$: $V_o = -(3{,}3 + 1{,}8333)\\cdot0{,}5\\sin\\omega t = -2{,}5667\\sin\\omega t$ V (5,1333 Vpp, ters fazlı)."])
    D.h(3, "2.4.3 Benzetim Sonuçları")
    D.fig("smsch", s("t3_s2_sch"), "Toplayıcı kuvvetlendirici devresinin LTspice şeması.", 14.5)
    D.p("[[f:sm1]]’de 4.1 durumunun işletme noktası; [[f:sm2]], [[f:sm3]] ve [[f:sm4]]’te 4.2, 4.3 ve 4.4 durumlarının zaman çizimleri verilmiştir. İmleç noktaları [[t:sm2c]], [[t:sm3c]] ve [[t:sm4c]]’te teorik değerlerle karşılaştırılmıştır.", align="j")
    D.fig("sm1", s("t3_s1"), "4.1 durumu ($V_1 = 0$ V, $V_2 = 5$ V): $V(vo) = -9{,}1667$ V (LTspice işletme noktası).", 14.5)
    D.fig("sm2", s("t3_s2"), "4.2 durumu ($V_1 = 0$, $V_2$ = 1 Vpp, 1 kHz): çıkış 1,8333 Vpp ve ters fazlıdır.", 14.5)
    cur_tab(D, "sm2c", "t3_s2", lambda t: -0.91667 * sin(t), cap="[[f:sm2]]’deki imleç noktalarının koordinatları (çıkış V(vo); teorik: $-0{,}9167\\sin(2\\pi\\cdot10^{3}t)$)")
    D.fig("sm3", s("t3_s3"), "4.3 durumu ($V_1 = 5$ V, $V_2$ = 1 Vpp, 1 kHz): beklenen −16,5 V seviyesi besleme sınırının ötesinde olduğundan çıkış negatif doymada sabit kalmıştır.", 14.5)
    c3 = K.get("t3_s3", [[0.25e-3, -13.0], [0.75e-3, -13.0]])
    D.tab("sm3c", ["İmleç", "X (zaman)", "Y, LTspice", "Kırpılmasız teorik"],
          [["İmleç %d" % (i + 1), n(t * 1e6, 2, "µs"), n(y, 4, "V"), n(-16.5 - 0.91667 * sin(t), 4, "V")] for i, (t, y) in enumerate(c3)],
          "[[f:sm3]]’teki imleç noktalarının koordinatları (çıkış V(vo))", [2.4, 3.2, 3.6, 4.6])
    D.fig("sm4", s("t3_s4"), "4.4 durumu ($V_1 = V_2$ = 1 Vpp, 1 kHz): çıkış 5,1333 Vpp ve ters fazlıdır.", 14.5)
    cur_tab(D, "sm4c", "t3_s4", lambda t: -2.56667 * sin(t), cap="[[f:sm4]]’teki imleç noktalarının koordinatları (çıkış V(vo); teorik: $-2{,}5667\\sin(2\\pi\\cdot10^{3}t)$)")
    D.p("4.3 durumu dışında bütün durumlarda LTspice sonuçları teorik beklentiyle örtüşmektedir. 4.3 durumunda beklenen çıkış ($-16{,}5$ V) besleme gerilimiyle ($-15$ V) uyumsuz olduğundan benzetim, op-amp’in gerçek davranışını gösterir: çıkış ≈ −13 V’ta kalır ve kuramsal denklem artık geçerli değildir. Bu, “ideal op-amp” kabulünün çıkışın besleme sınırları içinde kalması koşuluyla geçerli olduğunu gösterir.", align="j")

    D.h(1, "Sonuçlar")
    D.p("**Genel değerlendirme.** Dört devrede de el ile türetilen kazanç ifadeleri LTspice benzetimiyle (UA741 modeli) örtüşmüştür: eviren kuvvetlendiricide $-R_2/R_1 = -10$, evirmeyen kuvvetlendiricide $1 + R_f/R_g = 11$, fark kuvvetlendiricide $V_o = 1{,}5167V_2 - 1{,}8V_1$ ve toplayıcıda $V_o = -3{,}3V_1 - 1{,}8333V_2$. İmleç okumaları ile teorik değerler arasındaki fark milivolt altındadır; bu fark, imleç konumunun zaman ekseninde piksel çözünürlüğüyle yerleştirilebilmesi ve modelin sonlu açık çevrim kazancından kaynaklanır.", align="j")
    D.p("**Doyma.** Op-amp çıkışı besleme gerilimiyle sınırlıdır. Eviren kuvvetlendiricide giriş genliği 1,3 V’u (modelde) aştığında çıkış kırpılır; toplayıcıda 4.3 durumunda beklenen −16,5 V çıkış, besleme sınırı nedeniyle gerçekleşmez ve çıkış ≈ −13 V’ta kalır. Laboratuvarda gerçek bir µA741 kullanıldığında doyma gerilimi veri sayfasındaki tipik ve asgari değerler arasında olacaktır (asgari ±12 V, RL ≥ 10 kΩ).", align="j")
    D.p("**Laboratuvarda beklenen sapmalar.** (i) Dirençlerin %5 toleransı kazançlarda aynı oranda sapmaya yol açar; fark kuvvetlendiricide eşleşmeyen dirençler ortak mod bastırmasını ayrıca bozar. (ii) Gerçek µA741’in giriş ofset gerilimi (tipik 0,3 mV, azami 6 mV) çıkışta kazançla çarpılarak DA kayması oluşturur; eviren kuvvetlendiricide (kazanç 11 üzerinden gürültü kazancı) 3,3 mV’tan 66 mV’a kadar olabilir. (iii) Giriş kutuplama akımları (azami 500 nA) giriş dirençlerinde ek gerilim düşümü yaratır. (iv) Güç kaynağının ve fonksiyon üretecinin gerçek çıkışı ayar hassasiyeti nedeniyle farklı olabilir; üretecin 50 Ω’luk iç direnci (yüksüz 1 Vpp ayarı yüklü devrede farklı gösterebilir) dikkate alınmalıdır. (v) Devre tahtasındaki kontak ve kablo dirençleri ile osiloskop probunun kapasitesi yüksek frekanslarda sapma yaratır.", align="j")
    D.p("**Eksik veya yorumlanamayan sonuç.** Bu rapor bir ön çalışma raporudur; laboratuvar ölçümleri henüz yapılmamıştır. Hata payları teorik sonuç ile benzetim arasında verilmiştir; ölçüm sonuçlarının eklenmesi deney raporunda yapılacaktır.", align="j")
    D.p("**Kazanılan beceriler.** (i) Dört temel op-amp devresinin kazancı sanal kısa devre kavramıyla çıkarılmış; (ii) doyma gözlenmiş ve girişin azami genliği hesaplanmış; (iii) veri sayfası okunarak bacak bağlantıları belirlenmiş; (iv) LTspice ile ideal olmayan bir op-amp modeli kurulmuş, doğrulanmış ve zaman ile DC tarama benzetimlerinde kullanılmış; (v) devre tahtası yerleşimleri planlanmıştır.", align="j")
    D.h(1, "Kaynaklar")
    refs_block(D, ["Nilsson, J. W., & Riedel, S. A. (2015). *Electric circuits* (10th ed.). Boston: Pearson.",
                   "Alexander, C. K., & Sadiku, M. N. O. (2017). *Fundamentals of electric circuits* (6th ed.). New York: McGraw-Hill Education.",
                   "Sedra, A. S., & Smith, K. C. (2015). *Microelectronic circuits* (7th ed.). New York: Oxford University Press.",
                   "Texas Instruments. (2026). *µA741 general-purpose operational amplifiers* (SLOS094H) [Veri sayfası]. https://www.ti.com/lit/ds/symlink/ua741.pdf",
                   "Analog Devices. (2026). *LTspice* (Sürüm 26.1.1) [Bilgisayar yazılımı]. Analog Devices, Inc.",
                   "Analog Devices. (2026). *LTspice help: Universal op-amp models* [Çevrimiçi yardım belgesi]. Analog Devices, Inc.",
                   "TOBB Ekonomi ve Teknoloji Üniversitesi. (2026). *ELE 201 L – Devre Analizi I Laboratuvarı, Deney 3 Ön Çalışma Yönergesi*. Ankara: TOBB ETÜ, Elektrik – Elektronik Mühendisliği Bölümü."])
    D.h(1, "Ekler")
    D.h(3, "EK-1: UA741 Modeli ve SPICE Devre Listeleri")
    D.p("Aşağıdaki alt devre (UA741.lib) LTspice’ın “level2” (tek kutuplu, eğim hızı sınırlı, besleme gerilimine kırpılan) op-amp modelini veri sayfasının tipik değerleriyle sarar. Devre listelerinde op-amp “XU1 evirmeyen eviren V+ V− çıkış UA741” biçiminde çağrılır.", align="j")
    D.code(open(os.path.join(H, "..", "asc", "UA741.lib")).read(), "UA741.lib")
    D.code("* Bolum 2.1 - eviren kuvvetlendirici\nXU1 0 inv vcc vee vo UA741\nVs vs 0 SINE(0 0.5 1k)\nR1 vs inv 10k\nR2 inv vo 100k\nVcc vcc 0 15\nVee vee 0 -15\n.lib UA741.lib\n.tran 0 3m 0 2u\n.end", "Bölüm 2.1 – Eviren kuvvetlendirici")
    D.code("* Bolum 2.2 - evirmeyen kuvvetlendirici\nXU1 np inv vcc vee vo UA741\nVg vg 0 SINE(0 0.5 1k)\nRs vg np 1k\nRg inv 0 10k\nRf inv vo 100k\nVcc vcc 0 15\nVee vee 0 -15\n.lib UA741.lib\n.tran 0 3m 0 2u\n.end", "Bölüm 2.2 – Evirmeyen kuvvetlendirici")
    D.code("* Bolum 2.3 - fark kuvvetlendirici (3.2 durumu)\nXU1 np inv vcc vee vo UA741\nV1 v1 0 0\nV2 v2 0 SINE(0 0.5 1k)\nR1 v1 inv 10k\nR2 inv vo 18k\nR3 v2 np 33k\nR4 np 0 39k\nVcc vcc 0 15\nVee vee 0 -15\n.lib UA741.lib\n.tran 0 3m 0 2u\n.end", "Bölüm 2.3 – Fark kuvvetlendirici")
    D.code("* Bolum 2.4 - toplayici kuvvetlendirici (4.2 durumu)\nXU1 0 inv vcc vee vo UA741\nV1 v1 0 0\nV2 v2 0 SINE(0 0.5 1k)\nR1 v1 inv 10k\nR2 v2 inv 18k\nR3 inv vo 33k\nVcc vcc 0 15\nVee vee 0 -15\n.lib UA741.lib\n.tran 0 3m 0 2u\n.end", "Bölüm 2.4 – Toplayıcı kuvvetlendirici")
    return D

if __name__ == "__main__":
    D = build(); f = os.path.join(OUT, "ELE201L_Deney3_Oncalisma_Raporu.docx"); D.save(f)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", OUT, f], capture_output=True, timeout=300); print("ok")
