import math
KP_N, KP_P = 0.1233, 150e-6
from common import *

M = "−"


def qa(d, items):
    for q, a in items:
        d.p("**S:** " + q)
        d.p("**C:** " + a)


def f(x, nd=3):
    return fmt(x, nd).replace("-", M)


def tr_extra(n, d, R):
    d.h(1, "Akla Gelebilecek Ek Sorular (\"Ya şöyle olsaydı?\")")
    d.p("Bu bölüm, deney sırasında ya da sözlü/quiz anında akla gelebilecek ihtimalleri sayısıyla cevaplar. Hepsi bu klasördeki modellerle hesaplanmış ya da veri sayfasından alınmıştır; kendi başıma kabul ettiğim bir sayı varsa belirtilmiştir.")
    if n == 1:
        vd07 = 0.5
        for _ in range(60):
            vd07 = VT * math.log((0.7 - vd07) / (1e3 * IS_D) + 1)
        id07 = (0.7 - vd07) / 1e3
        qa(d, [
            ("Diyodu ters bağlarsam çıkış ne olur?", "Diyot negatif yarı dalgada iletir: çıkış, girişin negatif yarısı eksi 0,7 V (CVD) olur, yani tepe −4,3 V; pozitif yarı dalga kesilir. Ters dayanım gerilimi artık −5 V yerine +5 V'ta görülür."),
            ("R1'i 1 kΩ yerine 100 Ω yaparsam?", "Tepe akım (5−0,7)/100 = 43 mA olur; 1N4148 için sürekli akım sınırı (veri sayfası ~200 mA mertebesi, yoklanmadı; kendi hafızam) içindedir. Diyot gerilimi 60 mV/dekad kuralıyla yaklaşık 0,05 V artar (akım 10 kat): CVD'nin 0,7 V'u hâlâ makul."),
            ("Frekansı 100 kHz yaparsam çıkış değişir mi?", "1N4148 modelinde CJO=4 pF ve TT=20 ns var. 100 kHz'de periyot 10 µs, TT=20 ns bunun %0,2'si; dalga biçimi fark edilir değişmez. MHz mertebesinde ters toparlanma (diyot kapanırken kısa süre ters akım) görünmeye başlar."),
            ("Sıcaklık artarsa?", "Aynı akım için $V_D$ yaklaşık −2 mV/°C azalır (genel yarı iletken bilgisi, bu klasörde ölçülmedi); $I_S$ kabaca her 5 °C'de ikiye katlanır. Yani sıcak diyot 'daha erken' açar."),
            ("$V_S=0{,}7$ V iken CVD ne diyor, gerçek ne?", "CVD: tam eşikte $I_D=0$ (kapalı). Üstel modelde (föy parametreleri) $V_D=%s$ V ve $I_D=%s$ mA bulunur: yani 'eşik' diye keskin bir sınır yoktur, akım küçük ama sıfır değildir." % (f(vd07, 4), f(id07 * 1e3, 4))),
            ("SPICE ile teorinin farkı hata mı?", "Hayır: model parametreleri farklı ($n=1{,}752$, $I_S=2{,}52$ nA, $R_S=0{,}568\\ \\Omega$). Föy parametreleriyle SPICE'ı ayarlayınca fark %0,0012'ye iner (rapordaki kalibrasyon)."),
            ("Neden LTspice ile ngspice aynı sonucu verdi?", "İkisi de Berkeley SPICE3 denklemlerini kullanır; aynı model satırı ve aynı çözücü ilkesi. Rapordaki tablolarda imleç değerleri 1e-5 bağıl farkla örtüşür."),
        ])
    elif n == 2:
        kn, kp = KP_N / 2, KP_P / 2
        def vm(vdd):
            return (2.1 * math.sqrt(kn) + (vdd - 1.0) * math.sqrt(kp)) / (math.sqrt(kn) + math.sqrt(kp))
        qa(d, [
            ("$V_{DD}$'yi 5 V yaparsam eviricinin eşiği nerede?", "Formül ($\\lambda$ ihmal): $V_M=%s$ V (6 V iken %s V). NMOS çok güçlü olduğundan eşik besleme gerilimine neredeyse hiç bağlı değildir; hâlâ NMOS eşiğinin biraz üstündedir." % (f(vm(5), 3), f(vm(6), 3))),
            ("$V_{DD}$ = 2 V yapsam evirici çalışır mı?", "Çalışmaz: PMOS'u açmak için $V_{SG}>1$ V, NMOS'u açmak için $V_{GS}>2{,}1$ V gerekir; 2 V'ta NMOS hiçbir giriş değerinde tam iletmez, çıkış 0 V'a çekilemez."),
            ("BS170 ile BS250'nin yerini değiştirirsem?", "NMOS yerine PMOS, PMOS yerine NMOS kaynağa bağlanır: kaynak-kapı polaritesi tersine döner, çıkış hiçbir girişte mantıklı değildir ve gövde diyotları iletebilir. Bu yüzden bacak sırası (D-G-S ve S-G-D) kritik."),
            ("Giriş sinyalini 0–6 V yerine 0–3 V verirsem?", "Girişin tepesi 3 V, NMOS eşiği 2,1 V: çıkış 6 V ile ~0 V arasında yine geçer ama NMOS'un sürülmesi zayıf kalır (aşırı sürme 0,9 V); geçiş bölgesi yüksek frekansta yavaşlar."),
            ("Kutuplama devresinde BS170'in eşiği 3 V olan bir parça takarsam?", "$V_{GS}=3$ V altında kapı gerilimi yetmez: tabloda $V_1$ değerlerini yeniden ayarlamanız gerekir. Örneğin $V_{GS}=3$ V sütununda akım %s mA olmaz, 0 olur. Veri sayfası aralığı (0,8–3,0 V) bunu açıkça söyler." % f(36 * (3 - 2) ** 2, 3)),
            ("Neden akım tepesi tam $V_M$'de değil?", "Tepe, iki transistörün de doymada olduğu ve PMOS'un sınırladığı noktadadır; rapordaki tabloda tepe %s V civarında (SPICE) görünür, $V_M$ ise çıkışın girişe eşit olduğu noktadır. İkisi farklı sorulardır." % "2,2"),
            ("LTspice'ta bu modeller sorunsuz mu çalıştı?", "Evet: föydeki iki `.model` satırı LTspice'ta olduğu gibi (RG, RB, Rds, Tt dâhil) hatasız koştu; ngspice'ta bu parametreler desteklenmediği için çıkarıldı ve DC sonuç farkı 0,02% mertebesinde kaldı."),
        ])
    elif n == 3:
        gm = 6.418e-3
        fz = 1 / (2 * math.pi * 10e3 * 22e-9)
        fcs = gm / (2 * math.pi * 22e-9)
        fc1 = 1 / (2 * math.pi * (47e3 * 33e3 / 80e3) * 22e-9)
        fc2 = 1 / (2 * math.pi * 25e3 * 2.2e-9)
        def q(vth):
            vg = 12 * 33 / 80
            vov = (-1 + math.sqrt(1 + 4 * 360 * (vg - vth))) / 720
            idq = 36e-3 * vov ** 2
            return vov, idq, 12 - idq * 25e3
        v08, v30 = q(0.8), q(3.0)
        qa(d, [
            ("$R_L$ bağlı değilse kazanç ne olur?", "Orta bantta $A_V=-g_mR_D=-6{,}418\\text{ mS}\\times15\\text{ k}\\Omega=%s$ (yük varken %s)." % (f(-gm * 15e3, 3), "−38,5")),
            ("$C_S$'in etkisi hangi frekanstan başlar?", "Sıfır: $f_z=1/(2\\pi R_SC_S)=%s$ Hz. Kazanç, $1/(\\omega C_S)\\approx1/g_m$ olduğu $f\\approx g_m/(2\\pi C_S)=%s$ kHz civarında düzleşir. Bu yüzden 10 kHz tam geçiş bölgesinin ortasındadır." % (f(fz, 3), f(fcs / 1e3, 3))),
            ("Kuplaj kondansatörlerinin köşe frekansları?", "Giriş: $1/(2\\pi R_{in}C_{C1})\\approx%s$ Hz ($R_{in}=19{,}4$ kΩ); çıkış: $1/(2\\pi(R_D+R_L)C_{C2})\\approx%s$ kHz. İkisi de 10 kHz'in altında/yakınında; çıkış kondansatörü 10 kHz'te kazancı hâlâ biraz düşürür." % (f(fc1, 3), f(fc2 / 1e3, 3))),
            ("Eşiği 0,8 V olan (veri sayfası alt sınırı) bir BS170 takarsam Q noktası?", "Aynı devre: $V_{OV}=%s$ V, $I_D=%s$ mA, $V_{DS}=%s$ V; transistör doymada kalır ama $V_{DS}$ 12 V'tan 2 V'a düşer, salınım genliği ciddi kısıtlanır." % (f(v08[0], 3), f(v08[1] * 1e3, 3), f(v08[2], 3))),
            ("Eşiği 3,0 V olan (üst sınır) parça takarsam?", "Kesime girmez (benim önceki cümlem yanlıştı): $V_G=4{,}95$ V eşiğin üstünde; $V_{OV}=%s$ V, $I_D=%s$ mA, $V_{DS}=%s$ V. Yani iletir ama $g_m$ çok küçülür ($g_m=K_NV_{OV}=%s$ mS), kazanç %s kat düşer." % (f(v30[0], 3), f(v30[1] * 1e3, 3), f(v30[2], 3), f(72 * v30[0], 3), f(gm * 1e3 / (72 * v30[0]), 2))),
            ("Neden fazör analizi de SPICE de 7,7–7,8, hesap 38,5?", "İki sayı farklı sorulara cevap veriyor: 38,5 orta bant (kondansatörler kusursuz kısa), 7,7 ise 10 kHz'te gerçek kondansatörlerle. Föy tablosuna 38,5 yazılır, ölçümü 7,7 yorumlanır."),
            ("Akım aynasında $R_2$'yi büyütürsem?", "Çıkış transistörü doymadan çıkar: $V_{DS2}=V_{DD}-I_{out}R_2\\geq V_{OV}$ koşulu daha küçük $V_i$'da bozulur; ayna 'daha erken' kopyalamayı bırakır. $R_2=1$ kΩ için sınır 12–13 V civarındaydı."),
            ("Kanal boyu modülasyonu ($\\lambda$) olsaydı aynada ne değişirdi?", "$V_{DS2}$ büyüdükçe $I_{out}$ biraz artardı; çıkış direnci sonsuz değil $1/(\\lambda I_D)$ olurdu. BS170 modelinde $\\lambda=0$ olduğundan rapordaki sonuçta fark yoktur."),
        ])
    elif n == 4:
        qa(d, [
            ("$\\beta$ değişirse Q noktası ne kadar oynar?", "Rapordaki duyarlılık tablosuna bakın (β = 120, 170, 220 için aynı devre hesaplandı): emetör dirençli kutuplamada akım β'ya çok az, dirençsiz kutuplamada neredeyse orantılı bağlıdır. Bu yüzden pratikte $R_E$'li kutuplama tercih edilir."),
            ("$V_{BE}$ 0,62 V yerine 0,7 V alınırsa?", "Taban akımı $V_{BB}-V_{BE}$'ye bağlıdır; 80 mV fark, $V_{BB}$ küçükse akımı %'lerle, büyükse %1 mertebesinde değiştirir. Hesap tablosunda 0,62 V (veri sayfası tipik) kullanıldı."),
            ("Sıcaklık artarsa?", "$V_{BE}$ yaklaşık −2 mV/°C azalır (genel bilgi, bu klasörde ölçülmedi); sabit $V_{BB}$ ile taban akımı artar, kolektör akımı artar, $V_{CE}$ düşer. $R_E$ bu etkiyi negatif geri beslemeyle bastırır."),
            ("Doyma ile aktif bölge farkı nasıl anlaşılır?", "$V_{CE}>0{,}2$ V ve $I_B>0$ ise ve $I_C=\\beta I_B$ ile bulunan $V_{CE}$ pozitif kalıyorsa aktif; hesaplanan $V_{CE}$ 0,2 V'un altına düşüyorsa doymadadır ve $I_C=(V_{CC}-0{,}2)/(R_C+R_E)$ alınır (rapordaki tablolar bu iki durumu ayırır)."),
            ("Hata senaryolarında neden $V_{CE}$ 12 V ya da 0 V çıkıyor?", "Bağlantı kopukluğu akımı keser (kesim): $R_C$ üstünde düşüm yok, kolektör $V_{CC}$'ye çıkar; ya da hiç besleme yoksa 0 V okunur. Bu, hata ayıklamada ilk bakılacak ipucudur."),
            ("LTspice'ta neden bu devrelerde ekran görüntüsü yok?", "Bu deneyin analizi yalnız DC çalışma noktasıdır (`.op`); zaman ya da frekans grafiği yoktur. Çalışma noktası, simülatörün 'Operating Point' çıktısı olarak okunur."),
        ])
    elif n == 5:
        gm = 1.171e-3 / 0.026
        fce = gm / (2 * math.pi * 22e-9)
        qa(d, [
            ("$C_E$ bypass'ı hangi frekanstan sonra etkili olur?", "$1/(\\omega C_E)\\approx r_e=1/g_m=%s\\ \\Omega$ olduğu frekansta: $f\\approx g_m/(2\\pi C_E)=%s$ kHz. 100 kHz bunun altında; bu yüzden 100 kHz'te kazanç orta bant değerinin (%s) hayli altında kalır (SPICE ve fazör: 52,7)." % (f(1 / gm, 3), f(fce / 1e3, 3), "−252")),
            ("$R_L$ kaldırılırsa CE kazancı?", "İdeal $C_E$ ile $A_V=-g_mR_C=-%s\\text{ mS}\\times5{,}6\\text{ k}\\Omega=%s$; gerçek $C_E$ ile 100 kHz'te yine daha küçüktür." % (f(gm * 1e3, 3), f(-gm * 5.6e3, 3))),
            ("Emitör takipçi neden kazancı 1'in üstüne çıkamaz?", "$A_V=(\\beta+1)R_E'/[r_\\pi+(\\beta+1)R_E']$ paydası payından büyüktür; $r_\\pi$ sıfır olsaydı 1 olurdu. Gerilim kazancı yok ama akım kazancı ($\\beta+1$) var: bu devre 'tampon' olarak kullanılır."),
            ("CC'de neden çıkış direnci küçük?", "Emetörden bakınca taban tarafı $r_\\pi/(\\beta+1)$ olarak görünür (kaynak direnci $\\beta+1$ kat küçülür); bu yüzden düşük dirençli yükleri sürer."),
            ("THD ölçütü olarak %1 yerine %5 seçseydim?", "Rapordaki THD tablosunda her ikisinin sınırı verildi; %5 ölçütüyle izin verilen genlik yaklaşık iki kat büyür (CE'li devrede çarpık dalga biçiminin gözle ayırt edilebildiği sınır %5 civarıdır)."),
            ("Breadboard'da hata ararken sırayla ne yapılır?", "(1) Besleme rayları gerçekten bağlı mı; (2) her direncin iki ucunun düğümü şemadakiyle aynı mı; (3) transistör bacakları C-B-E sırasıyla doğru sütunda mı; (4) kondansatörler (özellikle $C_E$) takılı mı. Rapordaki E1–E5 bu sırayla bulunabilir."),
            ("LTspice sonuçları neden ngspice ile aynı?", "Aynı model satırları ve aynı denklem seti. 100 kHz'te LTspice 34,419 dB, ngspice 34,420 dB okudu (rapordaki tablo)."),
        ])
