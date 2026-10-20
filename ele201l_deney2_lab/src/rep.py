import subprocess
from common import *
from docbuilder import Doc

def build():
    D = Doc("tr")
    D.sec = 2
    D.title_block([("TOBB Ekonomi ve Teknoloji Üniversitesi", 13, True), ("Elektrik – Elektronik Mühendisliği Bölümü", 12, False),
                   ("ELE 201 L – Devre Analizi I Laboratuvarı", 14, True), ("Deney 2 – Deney Raporu", 14, True), ("Güz 2026", 12, False)],
                  [("Adı Soyadı", "Beşir Kerem Üstüntürk"), ("Numara", "251201037"), ("Tarih", "20.10.2026")])

    # ---- Thevenin (Şekil 1): R1 seri, R2 şönt, R3 seri çıkış
    V1s, R1, R2, R3 = 10.0, 2200.0, 3300.0, 2200.0
    Voc = V1s * R2 / (R1 + R2)
    Rp23 = R2 * R3 / (R2 + R3)
    VN = V1s * Rp23 / (R1 + Rp23)
    Isc = VN / R3
    Rth1 = Voc / Isc
    Rth1b = R3 + R1 * R2 / (R1 + R2)

    # ---- Maksimum güç
    PL = Voc ** 2 / (4 * Rth1)
    IL = Voc / (2 * Rth1)

    # ---- Süperpozisyon (Şekil 3), kΩ ve V
    V1, V2 = 12.0, 5.0
    Rb = 15.0 + 3.9
    G4, Gb, G6 = 1 / 1.0, 1 / Rb, 1 / 8.2
    Gs = G4 + Gb + G6
    VocS = (V2 * G4 + V1 * Gb) / Gs
    VocS1 = V1 * Gb / Gs
    VocS2 = V2 * G4 / Gs
    RthS = 1 / Gs
    IN = VocS / RthS

    D.h(1, "Giriş")
    D.h(2, "Deneyin Amacı")
    D.p("Bu deneyde doğrusal bir devrenin iki ucundan görülen davranışının bir gerilim kaynağı ve seri bir dirençle temsil edilebileceği (Thevenin eşdeğeri), bu eşdeğer üzerinden yük direncine aktarılan gücün en büyük olduğu koşul ve bağımsız kaynaklı devrelerde süperpozisyon ilkesi incelenmiştir. Her bölümde önce teorik değerler hesaplanmış, ardından simülasyon ve ölçüm sonuçlarıyla karşılaştırılacak biçimde düzenlenmiştir.", align="j")
    D.h(2, "Deneyin Faydaları")
    D.p("Deney sonucunda, karmaşık bir devrenin yük uçlarına göre iki elemanlı bir eşdeğerle çözülebildiği gösterilmiştir. Yükün alabileceği gücün, yük direnci kaynağın iç direncine eşit olduğunda en büyük olduğu ve bu değerin hesapla bulunabildiği görülmüştür. Süperpozisyon ilkesi ile birden fazla bağımsız kaynağın katkısının ayrı ayrı hesaplanıp toplanabildiği, bu toplamın tüm kaynakların birlikte çalıştığı devrenin sonucuna eşit çıktığı görülmüştür.", align="j")

    D.h(1, "Ölçümler")
    D.h(2, "Thevenin Eşdeğer Devresi")
    D.p("Şekil 1’deki devre [1] için $V_S = 10$ V, $R_1 = 2{,}2\\ \\mathrm{k\\Omega}$, $R_2 = 3{,}3\\ \\mathrm{k\\Omega}$ ve $R_3 = 2{,}2\\ \\mathrm{k\\Omega}$ alınmıştır. Devre açık devre ve kısa devre koşullarında ngspice ile analiz edilmiş, sonuçlar tablolarda SPICE sütununda verilmiştir.", align="j")
    D.fig("s1", a("foy_s1.png"), "Basit bir dirençli devre (föy Şekil 1 [1]). Açık devre gerilimi $V_{oc}$ ile kısa devre akımı $I_{sc}$ devrenin $+$ ve $-$ uçlarından ölçülür.", 8.0)
    D.fig("bb1", a("bb2_s1.png"), "Şekil 1 devresinin devre tahtası yerleşimi. Kaynak artı ucu üst rayda, eksi ucu alt rayda bulunur.", 14.0)
    D.p("Açık devre gerilimi, çıkışta akım olmadığı için $R_3$ üzerinden düşen gerilim sıfırdır ve $V_{oc}$ doğrudan $R_2$ üzerindeki gerilimdir:", align="j", keep=True)
    D.eq(r"V_{oc}=V_S\,\frac{R_2}{R_1+R_2}=10\ \mathrm{V}\cdot\frac{3{,}3}{2{,}2+3{,}3}=6{,}00\ \mathrm{V}", "voc")
    D.p("Kısa devrede $R_2$ ve $R_3$ aynı iki düğüm arasında paralel olur; $R_2 \\parallel R_3 = 1{,}32\\ \\mathrm{k\\Omega}$ dir. Bu paralel kolun üzerindeki gerilim, $V_S$ nin $R_1$ ile bölünmesiyle bulunur; kısa devre akımı ise yalnızca $R_3$ kolundan geçen akımdır:", align="j", keep=True)
    D.eq(r"V_N=V_S\,\frac{R_2\parallel R_3}{R_1+R_2\parallel R_3}=3{,}75\ \mathrm{V},\qquad I_{sc}=\frac{V_N}{R_3}=\frac{3{,}75\ \mathrm{V}}{2{,}2\ \mathrm{k\Omega}}=1{,}705\ \mathrm{mA}", "isc")
    D.p("Thevenin direnci, açık devre gerilimi ile kısa devre akımının oranıdır:", align="j", keep=True)
    D.eq(r"R_{TH}=\frac{V_{oc}}{I_{sc}}=\frac{6{,}00\ \mathrm{V}}{1{,}705\ \mathrm{mA}}=3{,}52\ \mathrm{k\Omega}", "rth1")
    D.p("Bağımsız kaynaklar sıfırlandığında ($V_S$ kısa devre) $R_1 \\parallel R_2$ ile $R_3$ seri bağlanır ve aynı değer doğrudan elde edilir:", align="j", keep=True)
    D.eq(r"R_{TH}=R_3+R_1\parallel R_2=2{,}2\ \mathrm{k\Omega}+1{,}32\ \mathrm{k\Omega}=3{,}52\ \mathrm{k\Omega}", "rth2")
    rows = [["$V_{oc}$ (V)", n(Voc, 2), "6,00"], ["$I_{sc}$ (mA)", n(Isc, 3), "1,705"], ["$R_{TH}=V_{oc}/I_{sc}$ (kΩ)", n(Rth1 / 1e3, 2), "3,52"],
            ["$R_{TH}$, kaynaklar sıfırlanarak (kΩ)", n(Rth1b / 1e3, 2), "3,52"]]
    D.tab("t1", ["Büyüklük", "Teorik değer", "SPICE"], rows, "Thevenin eşdeğeri için teorik ve SPICE değerleri (Şekil 1)", [6.0, 3.5, 3.5])
    D.p("İki yöntemle bulunan Thevenin direnci de $3{,}52\\ \\mathrm{k\\Omega}$ çıkmıştır. Bu eşitlik, $R_{TH}$ ifadesinin kaynakların sıfırlanarak elde edilmesinin ve $V_{oc}/I_{sc}$ oranının aynı büyüklüğü verdiğini gösterir; iki ifade bu devrede aynıdır.", align="j")

    D.h(2, "Maksimum Güç Transferi")
    D.p("Şekil 1’deki devrenin çıkışına Şekil 2’deki gibi yük direnci $R_L$ bağlanmıştır [1].", align="j")
    D.fig("s2", a("foy_s2.png"), "Yük direnci bağlanmış devre (föy Şekil 2 [1]). Yük gerilimi $V_L$ ve çıkış gerilimi $V_0$ ayrıca belirtilmiştir.", 8.0)
    D.fig("bb2", a("bb2_s2.png"), "Şekil 2 devresinin devre tahtası yerleşimi. Yük direnci $R_L$, çıkış düğümü ile alt ray arasına bağlanmıştır.", 14.0)
    D.p("Yük uçlarından bakıldığında devre, $V_{TH} = V_{oc} = 6{,}00$ V gerilim kaynağı ile $R_{TH}$ seri direncine eşdeğerdir. Yük akımı ve yükte harcanan güç şöyledir:", align="j", keep=True)
    D.eq(r"I_L=\frac{V_{TH}}{R_{TH}+R_L},\qquad P_L=I_L^2R_L=\left(\frac{V_{TH}}{R_{TH}+R_L}\right)^2R_L", "pl")
    D.p("Güç $R_L$ ye göre türetilip sıfıra eşitlenirse, yükteki gücün en büyük olduğu koşul bulunur:", align="j", keep=True)
    D.eq(r"\frac{dP_L}{dR_L}=0\;\Rightarrow\;R_L=R_{TH}=3{,}52\ \mathrm{k\Omega}", "rlopt")
    D.p("Bu koşulda yük akımı ve en büyük güç şöyle hesaplanır:", align="j", keep=True)
    D.eq(r"I_L=\frac{6{,}00\ \mathrm{V}}{3{,}52\ \mathrm{k\Omega}+3{,}52\ \mathrm{k\Omega}}=0{,}852\ \mathrm{mA},\qquad P_{L,max}=\frac{V_{TH}^2}{4R_{TH}}=2{,}557\ \mathrm{mW}", "pmax")
    rows = [["$R_L$ (kΩ)", "3,52", "3,52"], ["$V_L$ (V)", n(Voc / 2, 3), "3,000"], ["$I_L$ (mA)", n(IL * 1e3, 3), "0,852"], ["$P_L$ (mW)", n(PL * 1e3, 3), "2,557"]]
    D.tab("t2", ["Büyüklük", "Teorik değer", "SPICE"], rows, "Maksimum güç transferi için teorik ve SPICE değerleri ($R_L = R_{TH}$)", [6.0, 3.5, 3.5])

    D.h(2, "Süperpozisyon İlkesi")
    D.p("Şekil 3’teki devrede iki bağımsız gerilim kaynağı bulunmaktadır [1]. Bileşen değerleri $R_1 = R_2 = 15\\ \\mathrm{k\\Omega}$, $R_3 = 3{,}9\\ \\mathrm{k\\Omega}$, $R_4 = R_5 = 1\\ \\mathrm{k\\Omega}$, $R_6 = 8{,}2\\ \\mathrm{k\\Omega}$, $V_{S1} = 12$ V ve $V_{S2} = 5$ V’tur.", align="j")
    D.fig("s3", a("foy_s3.png"), "İki bağımsız kaynak içeren devre (föy Şekil 3 [1]). Terminal C–D’den görülen Thevenin eşdeğeri hesaplanmıştır.", 9.0)
    D.fig("bb3", a("bb2_s3.png"), "Şekil 3 devresinin devre tahtası yerleşimi. VS1 ve VS2 kaynakları ile toprak bağlantısı alt rayda gösterilmiştir.", 14.0)
    D.p("Devrenin düğümleri şöyledir. $V_{S1}$ kaynağının artı ucu, $R_2$ nin sol ucu ve $A$ ucu aynı düğümdedir; bu düğümün gerilimi $12$ V tur. $V_{S2}$ kaynağının artı ucu, $R_2$ nin sağ ucu, $R_5$ in üst ucu ve $R_4$ ün sol ucu aynı düğümdedir; bu düğümün gerilimi $5$ V tur. $R_3$, $R_4$ ün sağ ucu ve $R_6$ terminal $C$ ile birlikte $N$ düğümünü oluşturur. Tüm eksi uçlar ve $D$ ortak düğümdür. $R_1$ ile $R_3$ , $A$ ile $N$ arasında seri bir kol oluşturur ($R_1+R_3 = 18{,}9\\ \\mathrm{k\\Omega}$).", align="j")
    D.p("Önce iki kaynak da devrede iken $N$ düğümünde akımların toplamı sıfır yazılır. $G$ ile iletkenlik gösterilmek üzere ($\\mathrm{mS}$):", align="j", keep=True)
    D.eq(r"\frac{V_{S2}-V_N}{R_4}+\frac{V_{S1}-V_N}{R_1+R_3}=\frac{V_N}{R_6}\;\Rightarrow\;V_N=\frac{V_{S2}G_4+V_{S1}G_{b}}{G_4+G_b+G_6}", "nodal")
    D.p("Burada $G_4 = 1$ mS, $G_b = 1/18{,}9$ mS ve $G_6 = 1/8{,}2$ mS dir. Sayılar yerine konduğunda $V_{oc} = 4{,}796$ V bulunur. Terminal C–D’den bakıldığında kaynaklar sıfırlandığında düğüm $R_4$, $R_1+R_3$ ve $R_6$ ile paraleldir:", align="j", keep=True)
    D.eq(r"R_{TH}=\frac{1}{G_4+G_b+G_6}=\frac{1}{1{,}1749\ \mathrm{mS}}=0{,}851\ \mathrm{k\Omega},\qquad I_N=\frac{V_{oc}}{R_{TH}}=5{,}635\ \mathrm{mA}", "supth")
    D.p("Süperpozisyon ile katkılar ayrı ayrı hesaplanmıştır. $VS_1$ kısa devre edilerek ($V_{S1}=0$) elde edilen açık devre gerilimi ve $VS_2$ kısa devre edilerek ($V_{S2}=0$) elde edilen açık devre gerilimi şöyledir:", align="j", keep=True)
    D.eq(r"V_{oc,S2}=\frac{V_{S2}G_4}{G_4+G_b+G_6}=4{,}256\ \mathrm{V},\qquad V_{oc,S1}=\frac{V_{S1}G_b}{G_4+G_b+G_6}=0{,}540\ \mathrm{V}", "supparts")
    D.p("Bu iki katkının toplamı $4{,}256 + 0{,}540 = 4{,}796$ V olup, iki kaynağın birlikte çalıştığı durumdaki $V_{oc}$ ile aynıdır. Kaynaklar sıfırlandığında Thevenin direnci değişmediği için her iki katkı da aynı $R_{TH} = 0{,}851\\ \\mathrm{k\\Omega}$ ile çalışır.", align="j")
    rows = [["$V_{oc}$, iki kaynak birlikte (V)", n(VocS, 3), "4,796"],
            ["$V_{oc}$, yalnız $V_{S2}$ (V)", n(VocS2, 3), "4,256"],
            ["$V_{oc}$, yalnız $V_{S1}$ (V)", n(VocS1, 3), "0,540"],
            ["$R_{TH}$ (kΩ)", n(RthS, 3), "0,851"],
            ["$I_N = V_{oc}/R_{TH}$ (mA)", n(IN, 3), "5,635"]]
    D.tab("t3", ["Büyüklük", "Teorik değer", "SPICE"], rows, "Süperpozisyon devresi için teorik ve SPICE değerleri (Şekil 3)", [6.0, 3.5, 3.5])

    D.h(1, "Sonuçlar")
    D.p("**Thevenin eşdeğeri.** Şekil 1’deki devrenin açık devre gerilimi $6{,}00$ V, kısa devre akımı $1{,}705$ mA ve Thevenin direnci $3{,}52\\ \\mathrm{k\\Omega}$ olarak hesaplanmıştır. Kaynakları sıfırlayarak bulunan direnç aynı değeri vermiştir. SPICE sonuçları teorik değerlerle yuvarlama düzeyinde uyuşmaktadır.", align="j")
    D.p("**Maksimum güç.** Yük direnci Thevenin direncine eşit ($3{,}52\\ \\mathrm{k\\Omega}$) seçildiğinde yükte harcanan güç $2{,}557$ mW olarak bulunmuştur. Bu değerden farklı yük dirençlerinde güç daha küçük çıkar.", align="j")
    D.p("**Süperpozisyon.** İki kaynağın birlikte oluşturduğu açık devre gerilimi, her kaynağın ayrı katkısının toplamına eşittir. Bu toplam $4{,}796$ V olarak bulunmuş, Thevenin direnci $0{,}851\\ \\mathrm{k\\Omega}$ olarak hesaplanmıştır.", align="j")
    D.p("Bu çalışmadaki değerler teorik hesaba ve SPICE simülasyonuna dayanmaktadır.", align="j")

    D.h(1, "Kaynaklar")
    refs_block(D, ["TOBB Ekonomi ve Teknoloji Üniversitesi. (2026). *ELE 201 L – Devre Analizi I Laboratuvarı, Deney 2 Ön Çalışma*. Ankara: TOBB ETÜ, Elektrik – Elektronik Mühendisliği Bölümü."])
    return D

if __name__ == "__main__":
    B = os.path.join(os.path.dirname(OUT), "build"); os.makedirs(B, exist_ok=True)
    D = build(); f = os.path.join(B, "ELE201L_Deney2_Laboratuvar_Raporu.docx"); D.save(f)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", OUT, f], capture_output=True, timeout=300); print("ok")
