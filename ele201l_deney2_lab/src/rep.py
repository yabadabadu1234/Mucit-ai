import subprocess
from common import *
from docbuilder import Doc

def build():
    D = Doc("tr")
    D.sec = 2
    D.title_block([("TOBB Ekonomi ve Teknoloji Üniversitesi", 13, True), ("Elektrik – Elektronik Mühendisliği Bölümü", 12, False),
                   ("ELE 201 L – Devre Analizi I Laboratuvarı", 14, True), ("Deney 2 – Ön Çalışma Raporu", 14, True), ("Güz 2026", 12, False)],
                  [("Adı Soyadı", "Beşir Kerem Üstüntürk"), ("Numara", "251201037"), ("Tarih", "20.10.2026")])

    V1s, R1, R2, R3 = 10.0, 2200.0, 3300.0, 2200.0
    Voc = V1s * R2 / (R1 + R2)
    Rp23 = R2 * R3 / (R2 + R3)
    VN = V1s * Rp23 / (R1 + Rp23)
    Isc = VN / R3
    Rth1 = Voc / Isc
    Rth1b = R3 + R1 * R2 / (R1 + R2)

    PL = Voc ** 2 / (4 * Rth1)
    IL = Voc / (2 * Rth1)

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
    D.h(2, "Ön Çalışmanın Amacı")
    D.p("Bu ön çalışmada doğrusal bir devrenin iki ucundan görülen davranışının Thevenin eşdeğeriyle temsil edilmesi, yük direncine en büyük gücün aktarıldığı koşulun belirlenmesi ve bağımsız kaynaklı bir devrede süperpozisyon ilkesinin uygulanması incelenmiştir. Her soru için devre çizimi, teorik hesap ve SPICE kontrolü verilmiştir.", align="j")
    D.h(2, "Ön Çalışmanın Faydaları")
    D.p("Karmaşık bir devrenin yük uçlarına göre iki elemanlı bir eşdeğerle çözülebildiği, yükün çektiği gücün kaynağın iç direncine eşit yük direncinde en büyük olduğu ve birden fazla kaynaklı devrenin katkılarının ayrı ayrı hesaplanıp toplanabildiği görülmüştür.", align="j")

    D.h(1, "Hesaplar ve Simülasyonlar")
    D.h(2, "Thevenin Eşdeğer Devresi")
    D.h(3, "Devre Çizimi")
    D.p("Şekil 1’deki devre [1] için $V_S = 10$ V, $R_1 = 2{,}2\\ \\mathrm{k\\Omega}$, $R_2 = 3{,}3\\ \\mathrm{k\\Omega}$ ve $R_3 = 2{,}2\\ \\mathrm{k\\Omega}$ alınmıştır. Devrenin TinkerCAD tarzı çizimi ve devre tahtası yerleşimi aşağıda verilmiştir.", align="j")
    D.fig("tk1", a("tk_s1.png"), "Şekil 1 devresinin TinkerCAD tarzı çizimi.", 9.0)
    D.fig("bb1", a("bb2_s1.png"), "Şekil 1 devresinin devre tahtası yerleşimi.", 14.0)
    D.h(3, "Açık Devre Gerilimi ve Kısa Devre Akımı")
    D.p("Açık devrede çıkışta akım olmadığından $R_3$ üzerinde gerilim düşmez ve $V_{oc}$, $R_2$ üzerindeki gerilime eşittir:", align="j", keep=True)
    D.eq(r"V_{oc}=V_S\,\frac{R_2}{R_1+R_2}=10\ \mathrm{V}\cdot\frac{3{,}3}{2{,}2+3{,}3}=6{,}00\ \mathrm{V}", "voc")
    D.p("Kısa devrede $R_2$ ve $R_3$ aynı iki düğüm arasında paralel olur, $R_2 \\parallel R_3 = 1{,}32\\ \\mathrm{k\\Omega}$ dur. Kısa devre akımı yalnızca $R_3$ kolundan geçen akımdır:", align="j", keep=True)
    D.eq(r"V_N=V_S\,\frac{R_2\parallel R_3}{R_1+R_2\parallel R_3}=3{,}75\ \mathrm{V},\qquad I_{sc}=\frac{V_N}{R_3}=\frac{3{,}75\ \mathrm{V}}{2{,}2\ \mathrm{k\Omega}}=1{,}705\ \mathrm{mA}", "isc")
    D.fig("spice", a("spice_cikti.png"), "Şekil 1 devresinin ngspice (batch modu) ile analiz çıktısı. Açık devre gerilimi 6,000 V, kısa devre akımı 1,7045 mA olarak elde edilmiştir.", 13.0)
    D.h(3, "Thevenin Direnci")
    D.p("Thevenin direnci, açık devre gerilimi ile kısa devre akımının oranıdır:", align="j", keep=True)
    D.eq(r"R_{TH}=\frac{V_{oc}}{I_{sc}}=\frac{6{,}00\ \mathrm{V}}{1{,}705\ \mathrm{mA}}=3{,}52\ \mathrm{k\Omega}", "rth1")
    D.p("Bağımsız kaynaklar sıfırlandığında ($V_S$ kısa devre) $R_1 \\parallel R_2$ ile $R_3$ seri bağlanır ve aynı değer doğrudan elde edilir:", align="j", keep=True)
    D.eq(r"R_{TH}=R_3+R_1\parallel R_2=2{,}2\ \mathrm{k\Omega}+1{,}32\ \mathrm{k\Omega}=3{,}52\ \mathrm{k\Omega}", "rth2")
    D.p("İki yöntemle bulunan direnç aynı değeri verdiği için bu devrede iki ifade aynıdır.", align="j")
    rows = [["$V_{oc}$ (V)", n(Voc, 2), "6,00"], ["$I_{sc}$ (mA)", n(Isc, 3), "1,705"],
            ["$R_{TH}=V_{oc}/I_{sc}$ (kΩ)", n(Rth1 / 1e3, 2), "3,52"],
            ["$R_{TH}$, kaynaklar sıfırlanarak (kΩ)", n(Rth1b / 1e3, 2), "3,52"]]
    D.tab("t1", ["Büyüklük", "Teorik değer", "SPICE"], rows, "Thevenin eşdeğeri için teorik ve SPICE değerleri (Şekil 1)", [6.0, 3.5, 3.5])

    D.h(2, "Maksimum Güç Transferi")
    D.h(3, "Devre Çizimi")
    D.p("Şekil 2’deki devre [1], Şekil 1’in çıkışına yük direnci $R_L$ bağlanarak elde edilmiştir. Devrenin TinkerCAD tarzı çizimi ve devre tahtası yerleşimi aşağıdadır.", align="j")
    D.fig("tk2", a("tk_s2.png"), "Şekil 2 devresinin TinkerCAD tarzı çizimi.", 9.0)
    D.fig("bb2", a("bb2_s2.png"), "Şekil 2 devresinin devre tahtası yerleşimi.", 14.0)
    D.h(3, "Yük Direncinin Teorik Seçimi")
    D.p("Yük uçlarından bakıldığında devre $V_{TH} = V_{oc} = 6{,}00$ V gerilim kaynağı ile $R_{TH}$ seri direncine eşdeğerdir. Yük akımı ve yükte harcanan güç şöyledir:", align="j", keep=True)
    D.eq(r"I_L=\frac{V_{TH}}{R_{TH}+R_L},\qquad P_L=I_L^2R_L=\left(\frac{V_{TH}}{R_{TH}+R_L}\right)^2R_L", "pl")
    D.p("Gücün $R_L$ ye göre türevi sıfıra eşitlendiğinde yükteki güç en büyük olur:", align="j", keep=True)
    D.eq(r"\frac{dP_L}{dR_L}=0\;\Rightarrow\;R_L=R_{TH}=3{,}52\ \mathrm{k\Omega}", "rlopt")
    D.p("Bu koşulda yük akımı ve en büyük güç şöyle hesaplanır:", align="j", keep=True)
    D.eq(r"I_L=\frac{6{,}00\ \mathrm{V}}{3{,}52\ \mathrm{k\Omega}+3{,}52\ \mathrm{k\Omega}}=0{,}852\ \mathrm{mA},\qquad P_{L,max}=\frac{V_{TH}^2}{4R_{TH}}=2{,}557\ \mathrm{mW}", "pmax")
    D.h(3, "SPICE Kontrolü")
    D.p("$R_L = 3{,}52\\ \\mathrm{k\\Omega}$ ile kurulan devrede yük gerilimi ngspice ile $3{,}000$ V bulunmuştur. Bu değerden yükteki güç $3{,}000^2/3520 = 2{,}557$ mW olarak hesaplanır.", align="j")
    rows = [["$R_L$ (kΩ)", "3,52", "3,52"], ["$V_L$ (V)", n(Voc / 2, 3), "3,000"], ["$I_L$ (mA)", n(IL * 1e3, 3), "0,852"], ["$P_L$ (mW)", n(PL * 1e3, 3), "2,557"]]
    D.tab("t2", ["Büyüklük", "Teorik değer", "SPICE"], rows, "Maksimum güç transferi için teorik ve SPICE değerleri ($R_L = R_{TH}$)", [6.0, 3.5, 3.5])

    D.h(2, "Süperpozisyon İlkesi")
    D.h(3, "Devre Çizimi")
    D.p("Şekil 3’teki devre [1] iki bağımsız kaynak içerir. Bileşen değerleri $R_1 = R_2 = 15\\ \\mathrm{k\\Omega}$, $R_3 = 3{,}9\\ \\mathrm{k\\Omega}$, $R_4 = R_5 = 1\\ \\mathrm{k\\Omega}$, $R_6 = 8{,}2\\ \\mathrm{k\\Omega}$, $V_{S1} = 12$ V ve $V_{S2} = 5$ V tur. Devrenin TinkerCAD tarzı çizimi ve devre tahtası yerleşimi aşağıda verilmiştir.", align="j")
    D.fig("tk3", a("tk_s3.png"), "Şekil 3 devresinin TinkerCAD tarzı çizimi.", 10.0)
    D.fig("bb3", a("bb2_s3.png"), "Şekil 3 devresinin devre tahtası yerleşimi.", 14.0)
    D.h(3, "Her İki Kaynak Birlikte")
    D.p("Düğümler şöyledir: $V_{S1}$ kaynağının artı ucu, $R_1$ in bir ucu ve $R_2$ nin sol ucu aynı düğümdedir ve $12$ V tur. $V_{S2}$ kaynağının artı ucu, $R_2$ nin sağ ucu, $R_5$ in üst ucu ve $R_4$ ün sol ucu aynı düğümdedir ve $5$ V tur. $R_3$, $R_4$ ün sağ ucu ve $R_6$, terminal $C$ ile birlikte $N$ düğümünü oluşturur. Tüm eksi uçlar ve $D$ ortak düğümdür. $R_1$ ile $R_3$ seri bir kol oluşturur ve toplam direnci $18{,}9\\ \\mathrm{k\\Omega}$ dur.", align="j")
    D.p("$N$ düğümünde akımların toplamı sıfır yazılarak açık devre gerilimi bulunur. Burada $G_4 = 1$ mS, $G_b = 1/18{,}9$ mS ve $G_6 = 1/8{,}2$ mS dir:", align="j", keep=True)
    D.eq(r"V_{oc}=\frac{V_{S2}G_4+V_{S1}G_b}{G_4+G_b+G_6}=\frac{5\cdot1+12\cdot0{,}05291}{1{,}17486}=4{,}796\ \mathrm{V}", "voc3")
    D.h(3, "Thevenin Direnci")
    D.p("Terminal $C$–$D$’den bakıldığında kaynaklar sıfırlandığında $R_4$, $R_1+R_3$ ve $R_6$ paralel bağlanır:", align="j", keep=True)
    D.eq(r"R_{TH}=\frac{1}{G_4+G_b+G_6}=\frac{1}{1{,}17486\ \mathrm{mS}}=0{,}851\ \mathrm{k\Omega}", "rth3")
    D.h(3, "VS1 Kısa Devre Edildiğinde")
    D.p("$V_{S1}$ kaynağı kısa devre edildiğinde açık devre gerilimi ve Thevenin direnci şöyle bulunur:", align="j", keep=True)
    D.eq(r"V_{oc,S1=0}=\frac{V_{S2}G_4}{G_4+G_b+G_6}=\frac{5}{1{,}17486}=4{,}256\ \mathrm{V},\qquad R_{TH}=0{,}851\ \mathrm{k\Omega}", "vs1short")
    D.h(3, "VS2 Kısa Devre Edildiğinde")
    D.p("$V_{S2}$ kaynağı kısa devre edildiğinde açık devre gerilimi ve Thevenin direnci şöyledir:", align="j", keep=True)
    D.eq(r"V_{oc,S2=0}=\frac{V_{S1}G_b}{G_4+G_b+G_6}=\frac{12\cdot0{,}05291}{1{,}17486}=0{,}540\ \mathrm{V},\qquad R_{TH}=0{,}851\ \mathrm{k\Omega}", "vs2short")
    D.p("Her iki durumda Thevenin direnci aynıdır, çünkü kaynak değerleri direnç ağını değiştirmez. Açık devre gerilimleri toplamı $4{,}256 + 0{,}540 = 4{,}796$ V olup iki kaynaklı durumdaki değerle aynıdır.", align="j")
    rows = [["$V_{oc}$, iki kaynak birlikte (V)", n(VocS, 3), "4,796"],
            ["$V_{oc}$, $V_{S1}$ kısa devre (V)", n(VocS2, 3), "4,256"],
            ["$V_{oc}$, $V_{S2}$ kısa devre (V)", n(VocS1, 3), "0,540"],
            ["$R_{TH}$ (kΩ)", n(RthS, 3), "0,851"],
            ["$I_N = V_{oc}/R_{TH}$ (mA)", n(IN, 3), "5,635"]]
    D.tab("t3", ["Büyüklük", "Teorik değer", "SPICE"], rows, "Süperpozisyon devresi için teorik ve SPICE değerleri (Şekil 3)", [6.0, 3.5, 3.5])

    D.h(1, "Sonuçlar")
    D.p("**Thevenin eşdeğeri.** Şekil 1’deki devrenin açık devre gerilimi $6{,}00$ V, kısa devre akımı $1{,}705$ mA ve Thevenin direnci $3{,}52\\ \\mathrm{k\\Omega}$ dur. Kaynaklar sıfırlanarak bulunan direnç de aynı değeri verir. SPICE sonuçları teorik değerlerle yuvarlama düzeyinde uyuşmaktadır.", align="j")
    D.p("**Maksimum güç.** Yük direnci Thevenin direncine eşit seçildiğinde yükte harcanan güç $2{,}557$ mW dır. Bu değerden farklı yük dirençlerinde güç daha küçük çıkar.", align="j")
    D.p("**Süperpozisyon.** Şekil 3’te iki kaynağın birlikte oluşturduğu açık devre gerilimi, her kaynağın ayrı katkısının toplamına eşittir: $4{,}796$ V. Thevenin direnci $0{,}851\\ \\mathrm{k\\Omega}$ dur.", align="j")

    D.h(1, "Kaynaklar")
    refs_block(D, ["TOBB Ekonomi ve Teknoloji Üniversitesi. (2026). *ELE 201 L – Devre Analizi I Laboratuvarı, Deney 2 Ön Çalışma*. Ankara: TOBB ETÜ, Elektrik – Elektronik Mühendisliği Bölümü."])
    return D

if __name__ == "__main__":
    B = os.path.join(os.path.dirname(OUT), "build"); os.makedirs(B, exist_ok=True)
    D = build(); f = os.path.join(B, "ELE201L_Deney2_On_Calisma_Raporu.docx"); D.save(f)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", OUT, f], capture_output=True, timeout=300); print("ok")
