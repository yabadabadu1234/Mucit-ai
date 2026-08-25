"""
Kuantum ve küllî öğrenme risalelerinin tashih cetveli.

:mod:`tashih` ile aynı usul: her düzeltme bir **veri** kaydıdır, kaynağa
birebir uygulanır, tam bir kere eşleştiği sınanır, ve cetvel elle değil
kayıttan üretilir.

    python3 docs/kaynak/tashih_kuantum.py            # tashihli nüshalar
    python3 docs/kaynak/tashih_kuantum.py --cetvel   # cetvel

**Ölçüt aynı:** yalnız *gösterilebilir* hatalar. Üslûp tercihi, gösterim
alışkanlığı ve modelleme seçimi hata sayılmadı. Buradaki kayıtların bir
kısmı ayrıca **makine ile sağlanmaktadır**; hangi testin hangi tashihi
tarttığı ``sağlama`` alanında yazılıdır.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

KAYNAK = os.path.dirname(os.path.abspath(__file__))
HEDEF = os.path.join(KAYNAK, "tashihli")

KAPI = "kuantum_kapi_kulliyati.tex"
TOPOS = "kuantum_topos.tex"
KULLI = "kulli_ogrenme_nazariyesi.tex"
OPERATOR = "kuantum_operator_ogrenmesi.tex"
DARBOGAZ = "analitik_darbogazlar.txt"

DOSYALAR = (KAPI, TOPOS, KULLI, OPERATOR, DARBOGAZ)


@dataclass(frozen=True)
class Tashih:
    no: int
    yer: str
    baslik: str
    dosyalar: Tuple[str, ...]
    eski: str
    yeni: str
    sebep: str
    tur: str                       # derleme | tip | isaret | mantik | vakum |
                                   # tanimsiz | olcek | istatistik
    saglama: Optional[str] = None  # bu tashihi tartan test


T: List[Tashih] = []


def _t(no, yer, baslik, dosyalar, eski, yeni, sebep, tur, saglama=None):
    T.append(Tashih(no, yer, baslik, tuple(dosyalar), eski, yeni,
                    sebep, tur, saglama))


# =====================================================================
#  K1-K6: derlemeyi kıran bozukluklar (kuantum kapı külliyatı)
# =====================================================================
# Aynı sınıf hata daha önce mizan risalelerinde de bulunmuştu: ortam
# kapanışının tırnakla bozulması. Metin bu hâliyle HİÇ derlenmiyor.

_t(1, "§1 Pauli", "Ortam kapanışı bozuk: \\end{equation\">",
   [KAPI],
   "[\\sigma_a, \\sigma_b] = 2i \\sum_c \\epsilon_{abc} \\sigma_c, "
   "\\quad \\{\\sigma_a, \\sigma_b\\} = 2 \\delta_{ab} \\mathbf{I}\n"
   "\\end{equation\">",
   "[\\sigma_a, \\sigma_b] = 2i \\sum_c \\epsilon_{abc} \\sigma_c, "
   "\\quad \\{\\sigma_a, \\sigma_b\\} = 2 \\delta_{ab} \\mathbf{I}\n"
   "\\end{equation}",
   "``\\end{equation\">`` diye bir ortam kapanışı yoktur; LaTeX ortamı "
   "kapatamadan belgeyi sürükler. ``tex_denetle.py`` bu dosyada 7 bulgu "
   "veriyor ve hepsinin kökü bu sınıftan.",
   "derleme", "test_kuantum_kapi_derleniyor"),

_t(2, "§1.3 Dönme kapıları", "Ortam kapanışı bozuk: \\end{align\">",
   [KAPI],
   "R_z(\\theta) &= \\exp\\left(-i \\frac{\\theta}{2} Z\\right) = "
   "\\begin{pmatrix} e^{-i\\theta/2} & 0 \\\\ 0 & e^{i\\theta/2} "
   "\\end{pmatrix}\n\\end{align\">",
   "R_z(\\theta) &= \\exp\\left(-i \\frac{\\theta}{2} Z\\right) = "
   "\\begin{pmatrix} e^{-i\\theta/2} & 0 \\\\ 0 & e^{i\\theta/2} "
   "\\end{pmatrix}\n\\end{align}",
   "Aynı sebep (bkz. K1).",
   "derleme", "test_kuantum_kapi_derleniyor"),

_t(3, "§5 Spektral", "Markdown başlığı LaTeX'e sızmış",
   [KAPI],
   "\\## 1. Kuantum Fourier Dönüşümü (QFT) ve Tersi (IQFT)",
   "\\subsection{Kuantum Fourier Dönüşümü (QFT) ve Tersi (IQFT)}",
   "``\\##`` LaTeX'te tanımsız bir komuttur ve derlemeyi durdurur. "
   "Belgedeki diğer bütün alt başlıklar ``\\subsection`` ile yazılmış; "
   "bu satır markdown'dan kalmış.",
   "derleme", "test_kuantum_kapi_derleniyor"),

_t(4, "§6.2 QSP", "Ortam kapanışı bozuk: \\end{align\">",
   [KAPI],
   "U_{\\vec{\\phi}} &= \\prod_{j=1}^d \\left( U_A \\cdot "
   "(\\Pi_{\\phi_j} \\otimes \\mathbf{I}) \\right) \\quad "
   "(\\text{Polinom Seviyeli Özdeğer Dönüşümü})\n\\end{align\">",
   "U_{\\vec{\\phi}} &= \\prod_{j=1}^d \\left( U_A \\cdot "
   "(\\Pi_{\\phi_j} \\otimes \\mathbf{I}) \\right) \\quad "
   "(\\text{Polinom Seviyeli Özdeğer Dönüşümü})\n\\end{align}",
   "Aynı sebep (bkz. K1).",
   "derleme", "test_kuantum_kapi_derleniyor"),

_t(5, "§7.1 Sınır operatörü", "Ortam kapanışı bozuk",
   [KAPI],
   "\\hat{\\partial}_k |v_0, v_1, \\dots, v_k\\rangle = \\sum_{j=0}^k "
   "(-1)^j |v_0, \\dots, \\hat{v}_j, \\dots, v_k\\rangle\n\\end{equation\">",
   "\\hat{\\partial}_k |v_0, v_1, \\dots, v_k\\rangle = \\sum_{j=0}^k "
   "(-1)^j |v_0, \\dots, \\hat{v}_j, \\dots, v_k\\rangle\n\\end{equation}",
   "Aynı sebep (bkz. K1).",
   "derleme", "test_kuantum_kapi_derleniyor"),

_t(6, "§7.4 HHL", "Ortam kapanışı bozuk",
   [KAPI],
   "U_{\\text{HHL}} = (\\mathbf{I} \\otimes \\text{IQFT}) \\cdot "
   "U_{\\text{Rot}} \\cdot (\\mathbf{I} \\otimes \\text{QPE}) \\quad "
   "\\implies |x\\rangle = A^{-1}|b\\rangle / \\|A^{-1}|b\\rangle\\|\n"
   "\\end{equation\">",
   "U_{\\text{HHL}} = (\\mathbf{I} \\otimes \\text{IQFT}) \\cdot "
   "U_{\\text{Rot}} \\cdot (\\mathbf{I} \\otimes \\text{QPE}) \\quad "
   "\\implies |x\\rangle = A^{-1}|b\\rangle / \\|A^{-1}|b\\rangle\\|\n"
   "\\end{equation}",
   "Aynı sebep (bkz. K1).",
   "derleme", "test_kuantum_kapi_derleniyor"),


# =====================================================================
#  K7-K8: kapı cebri
# =====================================================================
_t(7, "§1.4 Genel üniter", "$U_1(\\lambda) \\equiv R_z(\\lambda)$ değil",
   [KAPI],
   "U_1(\\lambda) &= \\begin{pmatrix} 1 & 0 \\\\ 0 & e^{i\\lambda} "
   "\\end{pmatrix} \\equiv R_z(\\lambda) \\\\",
   "U_1(\\lambda) &= \\begin{pmatrix} 1 & 0 \\\\ 0 & e^{i\\lambda} "
   "\\end{pmatrix} = e^{i\\lambda/2} R_z(\\lambda) \\quad "
   "(\\text{yalnız KÜRESEL FAZ kadar farklı; kontrollü hâlde}"
   "\\ CU_1 \\neq CR_z) \\\\",
   "$R_z(\\lambda) = \\mathrm{diag}(e^{-i\\lambda/2}, e^{i\\lambda/2})$, "
   "$U_1(\\lambda) = \\mathrm{diag}(1, e^{i\\lambda})$. İkisi eşit değil; "
   "aralarında $e^{i\\lambda/2}$ küresel fazı var. Tek başına kullanıldığında "
   "fark ölçülemez, fakat **kontrol altında ölçülebilir hâle gelir**: "
   "$CU_1(\\lambda) \\neq CR_z(\\lambda)$, çünkü kontrol kübiti küresel fazı "
   "göreli faza çevirir. $\\equiv$ işareti bu farkı siliyor.",
   "tip", "test_U1_ile_Rz_kuresel_faz_kadar_farkli"),

_t(8, "§5.1 QFT", "QFT'nin çarpım formu köşegen operatör gibi yazılmış",
   [KAPI],
   "\\text{QFT}_N &= \\frac{1}{\\sqrt{2^n}} \\bigotimes_{j=1}^n \\left( "
   "|0\\rangle\\langle 0| + |1\\rangle\\langle 1| e^{2\\pi i "
   "\\sum_{l=1}^j j_l / 2^l} \\right) \\\\",
   "\\text{QFT}_N |j_1 j_2 \\dots j_n\\rangle &= \\frac{1}{\\sqrt{2^n}} "
   "\\bigotimes_{l=1}^n \\left( |0\\rangle + e^{2\\pi i\\, 0.j_{n-l+1} "
   "\\dots j_n} |1\\rangle \\right) \\quad (\\text{çarpım formu}) \\\\",
   "Yazıldığı hâliyle sağ taraf $|0\\rangle\\langle 0| + "
   "|1\\rangle\\langle 1| e^{i\\varphi}$ biçiminde **köşegen** bir "
   "operatör; QFT ise köşegen değildir (köşegen olsaydı süperpozisyon "
   "üretemezdi ve Hadamard'ı içeremezdi). Çarpım formu bir *operatör "
   "ayrışımı* değil, bir **temel durumun görüntüsüdür**; o yüzden sol "
   "tarafa $|j\\rangle$ konmalıdır.",
   "tip", "test_qft_kosegen_degil"),


# =====================================================================
#  K9-K14: kuantum-topos risalesi
# =====================================================================
_t(9, "§2.1 Lif metriği", "Fubini–Study metriğinde izdüşüm terimi eksik",
   [TOPOS],
   "g_{\\mu\\nu}^{(k)}(u) &= \\langle \\partial_\\mu \\Psi_{w_k} | "
   "\\partial_\\nu \\Psi_{w_k} \\rangle \\quad (\\text{Fubini-Study / "
   "Riemannian İç Metriği}) \\\\",
   "g_{\\mu\\nu}^{(k)}(u) &= \\mathrm{Re}\\,\\langle \\partial_\\mu "
   "\\Psi_{w_k} | \\partial_\\nu \\Psi_{w_k} \\rangle - \\mathrm{Re}\\,"
   "\\langle \\partial_\\mu \\Psi_{w_k} | \\Psi_{w_k} \\rangle \\langle "
   "\\Psi_{w_k} | \\partial_\\nu \\Psi_{w_k} \\rangle \\quad "
   "(\\text{Fubini-Study Metriği}) \\\\",
   "$\\langle \\partial_\\mu\\Psi | \\partial_\\nu\\Psi\\rangle$ "
   "**kuantum geometrik tensörüdür**, Fubini–Study metriği değil. İki "
   "kusuru var: (i) karmaşıktır, yani simetrik bir Riemann metriği "
   "olamaz -- sanal kısmı Berry eğriliğidir; (ii) faz ayarına (gauge) "
   "duyarlıdır, oysa FS metriği ışın uzayında (projektif Hilbert "
   "uzayında) tanımlıdır. İzdüşüm terimi çıkarılınca ikisi de düzelir.",
   "tip", "test_fubini_study_metrigi"),

_t(10, "§2.1 Bütünlük", "$\\mathrm{Tr}(\\rho^2) \\le 1$ vakum bir denetim",
   [TOPOS],
   "\\mathbf{1}_{\\text{kuantum\\_bütünlük}} &= \\mathbb{I}\\left( "
   "\\text{Tr}(\\rho_{w_k}^2) \\le 1 \\right)",
   "\\mathbf{1}_{\\text{kuantum\\_bütünlük}} &= \\mathbb{I}\\left( "
   "\\text{Tr}(\\rho_{w_k}) = 1 \\;\\wedge\\; \\rho_{w_k} \\succeq 0 "
   "\\right), \\quad \\text{Tr}(\\rho_{w_k}^2) = 1 \\iff \\text{saf hâl}",
   "$\\mathrm{Tr}(\\rho^2) \\le 1$ **her** yoğunluk matrisi için "
   "sağlanır; dolayısıyla bu gösterge sabit $1$'dir ve hiçbir şeyi "
   "denetlemez. Bir denetimin denetim olabilmesi için bazen $0$ "
   "vermesi lazımdır. Asıl denetlenecek olan iz-birliği ile pozitif "
   "yarı-belirliliktir; saflık ise ayrı bir sorudur ve $=1$ ile "
   "ölçülür.",
   "vakum", "test_iz_kare_olcutu_vakum_degil"),

_t(11, "§2.2 Dolaşıklık", "Karşılıklı bilgi dolaşıklık ölçüsü değildir",
   [TOPOS],
   "\\text{DolaşıklıkÖlçüsü}(w_i, w_j) &= S(\\rho_i) + S(\\rho_j) - "
   "S(\\rho_{ij}) \\quad (\\text{Kuantum Bağlam Karşılıklı Bilgisi}) \\\\",
   "I(w_i : w_j) &= S(\\rho_i) + S(\\rho_j) - S(\\rho_{ij}) \\quad "
   "(\\text{Kuantum Karşılıklı Bilgi -- klasik bağıntıyı DA sayar}) \\\\\n"
   "E(w_i, w_j) &= S(\\rho_i) = S(\\rho_j) \\quad (\\text{saf }\\rho_{ij}"
   "\\text{ için dolaşıklık entropisi}) \\\\",
   "Kuantum karşılıklı bilgi, klasik bağıntıyı da içerir; ayrılabilir "
   "(dolaşıksız) bir hâlde bile sıfırdan büyük olabilir. Dolayısıyla "
   "onu \"dolaşıklık ölçüsü\" diye adlandırmak, dolaşık olmayan hâlleri "
   "dolaşık gösterir. Metnin parantez içindeki açıklaması zaten doğru; "
   "yanlış olan **adı**dır ve ad, aşağıdaki bütün akıl yürütmeyi "
   "sürüklüyor.",
   "mantik", "test_karsilikli_bilgi_dolasiklik_degil"),

_t(12, "§3.1 QFNO", "Kıyas tabanı yanlış: klasik FFT $O(2^N)$ değil",
   [TOPOS],
   "\\text{TimeComplexity}(\\text{QFNO}) &\\in \\mathcal{O}(\\log^2 N) "
   "\\ll \\mathcal{O}(2^N) \\quad (\\text{Üstel Sürat Kazanımı})",
   "\\text{QFT}: \\mathcal{O}(\\log^2 N) \\text{ kapı} \\quad "
   "\\text{v} \\quad \\text{FFT}: \\mathcal{O}(N \\log N) \\text{ işlem} "
   "\\quad (\\text{kıyas tabanı FFT'dir; ayrıca QFT çıktıyı GENLİK "
   "olarak tutar, okumak ayrı maliyettir})",
   "$N$ nokta üzerinde klasik Fourier dönüşümü $O(N\\log N)$'dir, "
   "$O(2^N)$ değil; $2^N$ ancak $N$ *kübitlik* bir durumun tam "
   "vektörünü yazmanın maliyetidir ve o ayrı bir büyüklüktür. İkisini "
   "aynı $N$ ile karşılaştırmak, kazanımı olduğundan üstel derecede "
   "büyük gösterir. Ayrıca QFT'nin çıktısı genliklerde saklıdır; "
   "spektrumu **okumak** ölçüm tekrarları ister, bu da kıyasa dâhil "
   "edilmelidir.",
   "olcek", "test_qft_ile_fft_kiyas_tabani"),

_t(13, "§4.1 İttisal", "Koherens ölçüsünde boyuta bölme eksik",
   [TOPOS],
   "\\mathbf{Coherence}_{\\text{40\\_veçhe}} &= \\left| \\text{Tr}\\left( "
   "\\prod_{j=1}^{40} \\hat{A}_{j, j+1} \\right) \\right| = 1 \\implies "
   "\\text{Tam İttisal}",
   "\\mathbf{Coherence}_{\\text{40\\_veçhe}} &= \\frac{1}{d} \\left| "
   "\\text{Tr}\\left( \\prod_{j=1}^{40} \\hat{A}_{j, j+1} \\right) "
   "\\right| \\in [0, 1], \\quad = 1 \\iff \\prod_j \\hat{A}_{j,j+1} = "
   "e^{i\\varphi}\\mathbf{I} \\implies \\text{Tam İttisal}",
   "$d$ boyutlu bir uzayda üniter $U$ için $|\\mathrm{Tr}\\,U| \\le d$ "
   "ve üst sınıra ancak $U = e^{i\\varphi}\\mathbf{I}$ iken ulaşılır. "
   "Normalize edilmemiş hâlde $|\\mathrm{Tr}| = 1$ şartı, $d > 1$ için "
   "\"tam ittisal\"i değil **rastgele bir ara değeri** seçer; $d = 1$ "
   "dışında hiçbir yerde iddia edilen manaya gelmez.",
   "olcek", "test_koherens_normalizasyonu"),

_t(14, "§6.1 İntaç", "hLevel 0 büzülebilirliktir, küme değil",
   [TOPOS],
   "40 veçhede tamamlanan kuantum hesabı, dış dünyaya kelâm olarak "
   "döküleceği an Kübik Tip Teorisi $Glue$ kuralı ve $h$-Level 0 "
   "(büzülebilir/küme) kesmesi ile ölçülür.",
   "40 veçhede tamamlanan kuantum hesabı, dış dünyaya kelâm olarak "
   "döküleceği an Kübik Tip Teorisi $Glue$ kuralı ve **küme kesmesi** "
   "$\\|\\cdot\\|_0$ (yani hLevel \\textbf{2}) ile ölçülür. hLevel 0 "
   "büzülebilirliktir ve her şeyi tek bir noktaya indirir.",
   "Voevodsky sıralamasında hLevel 0 = büzülebilir, 1 = önerme, "
   "2 = küme. Metin \"hLevel 0 (büzülebilir/küme)\" diyerek iki ayrı "
   "mertebeyi bir sayıyor. Fark tâlî değil: hLevel 0'a kesmek çıktıyı "
   "**tek bir elemana** indirir, yani bütün lafızları aynı lafza "
   "çevirir. Kastedilen küme kesmesi $\\|\\cdot\\|_0$'dır ve o hLevel "
   "2'dir. (Kesme indisi ile hLevel arasında $n \\mapsto n+2$ kayması "
   "vardır; karışıklık buradan doğuyor.)",
   "tip", "test_hlevel_sirasi"),


# =====================================================================
#  K15-K21: küllî öğrenme risalesi
# =====================================================================
_t(15, "§2.1 KAN", "B-spline temel sayısı $G$ değil $G+p$",
   [KULLI],
   "\\phi_{q,p}(x) &= w_{\\text{base}} \\cdot \\text{silu}(x) + "
   "w_{\\text{spline}} \\cdot \\sum_{k=1}^G c_k B_k(x) \\in "
   "\\mathcal{O}_{\\mathcal{X}} \\\\",
   "\\phi_{q,p}(x) &= w_{\\text{base}} \\cdot \\text{silu}(x) + "
   "w_{\\text{spline}} \\cdot \\sum_{k=1}^{G+p} c_k B_{k,p}(x) \\in "
   "\\mathcal{O}_{\\mathcal{X}} \\\\",
   "$G$ aralığa bölünmüş bir ızgarada $p$ dereceli B-spline temelinin "
   "eleman sayısı $G+p$'dir, $G$ değil. $G$ ile kesilirse son $p$ temel "
   "fonksiyonu düşer, birliğin bölünmesi ($\\sum_k B_k = 1$) sağ uçta "
   "bozulur ve eğri kenarda çöker. Ayrıca $B_k$ yazımında derece indisi "
   "düşmüş; bir sonraki satırda $B_{k,p-1}$ kullanıldığı için gösterim "
   "kendi içinde de tutarsız.",
   "boyut", "test_bspline_temel_sayisi"),

_t(16, "§2.1 KAN", "Cox--de Boor'un sol tarafında derece indisi yok",
   [KULLI],
   "B_k(x) &= \\frac{x - t_k}{t_{k+p} - t_k} B_{k, p-1}(x) + "
   "\\frac{t_{k+p+1} - x}{t_{k+p+1} - t_{k+1}} B_{k+1, p-1}(x) \\\\",
   "B_{k,p}(x) &= \\frac{x - t_k}{t_{k+p} - t_k} B_{k, p-1}(x) + "
   "\\frac{t_{k+p+1} - x}{t_{k+p+1} - t_{k+1}} B_{k+1, p-1}(x), \\quad "
   "\\text{payda } = 0 \\text{ ise o terim düşer} \\\\",
   "Özyineleme $p$ dereceyi $p-1$ dereceden kuruyor; sol tarafta derece "
   "yazılmazsa denklem kendi kendine gönderme yapar ve tanımsız kalır. "
   "Ayrıca tekrarlı düğümlerde payda sıfırlanır; o hâlde terimin "
   "**düştüğü** (limit) belirtilmezse gerçekleme $0/0$ üretir.",
   "tanimsiz", "test_cox_de_boor_sifir_payda"),

_t(17, "§2.1 KAN", "İntegral sınırı bozuk: $\\int_a b$",
   [KULLI],
   "\\mathcal{E}_{\\text{bükülme}} &= \\sum_{q,p} \\int_a b \\left( "
   "\\phi_{q,p}''(x) \\right)^2 dx \\quad (\\text{Spline Elastik "
   "Bükülme Enerjisi}) \\\\",
   "\\mathcal{E}_{\\text{bükülme}} &= \\sum_{q,p} \\int_a^b \\left( "
   "\\phi_{q,p}''(x) \\right)^2 dx \\quad (\\text{Spline Elastik "
   "Bükülme Enerjisi}) \\\\",
   "``\\int_a b`` üst sınırı olmayan bir integral yazar ve ``b`` "
   "çarpan olarak dizilir; ifade $b \\int_a (\\cdot)$ diye okunur. "
   "Üst sınır işareti (``^``) düşmüş.",
   "derleme", None),

_t(18, "§3.1 FNO", "$\\mathrm{ArgMin}$ bir doğruluk değeri üzerinde alınmış",
   [KULLI],
   "k_{\\text{kesme}} &= \\text{ArgMin}_k \\left( \\sum_{|k'|>k} "
   "\\mathbf{SpectralEnergy}(k') < \\epsilon_{\\text{kayıp}} \\right) \\\\",
   "k_{\\text{kesme}} &= \\min \\left\\{ k \\;\\middle|\\; "
   "\\sum_{|k'|>k} \\mathbf{SpectralEnergy}(k') < \\epsilon_{\\text{kayıp}} "
   "\\cdot \\sum_{k'} \\mathbf{SpectralEnergy}(k') \\right\\} \\\\",
   "İki ayrı kusur: (i) ``ArgMin`` bir *sayı* üzerinde alınır, "
   "parantez içindeki ifade ise doğru/yanlış -- şartı sağlayan en küçük "
   "$k$ isteniyorsa ``min\\{k \\mid \\dots\\}`` yazılmalıdır; "
   "(ii) eşik **mutlak** konmuş, oysa spektral enerji sinyalin "
   "ölçeğiyle birlikte büyür. Bağıl eşik konmazsa aynı $\\epsilon$ "
   "genliği iki katına çıkmış bir sinyalde bambaşka bir $k$ verir.",
   "olcek", "test_kesme_kipi_bagil_esikle"),

_t(19, "§4.1 RKHS", "Skaler büyüklüğe norm çubuğu konmuş",
   [KULLI],
   "\\lambda \\|\\bm{\\alpha}^T \\mathbf{K}_{\\text{Gram}} "
   "\\bm{\\alpha}\\|",
   "\\lambda \\, \\bm{\\alpha}^T \\mathbf{K}_{\\text{Gram}} "
   "\\bm{\\alpha}",
   "$\\bm{\\alpha}^T \\mathbf{K}\\bm{\\alpha}$ zaten bir skalerdir ve "
   "$\\mathbf{K}$ pozitif yarı-belirli olduğundan negatif olamaz; norm "
   "çubuğu hem gereksizdir hem de mutlak değer alarak düzenleme "
   "teriminin işaretini gizler. Bir satır yukarıda aynı büyüklük "
   "$\\|f^*\\|^2_{\\mathcal{H}_K}$ olarak çubuksuz yazılmış.",
   "tip", None),

_t(20, "§5.1 Tıkızlaştırma", "Stone--Čech bir $\\mathrm{ArgMax}$ değildir",
   [KULLI],
   "\\beta\\mathcal{X} &\\coloneqq \\text{ArgMax}_{\\overline{\\mathcal{X}}} "
   "\\{ \\overline{\\mathcal{X}} \\text{ tıkız} \\mid f : \\mathcal{X} "
   "\\to [-M, M] \\implies \\overline{f} : \\overline{\\mathcal{X}} \\to "
   "[-M, M] \\} \\\\",
   "\\beta\\mathcal{X} &\\coloneqq \\text{evrensel özellikle tanımlı: } "
   "\\forall\\, f : \\mathcal{X} \\to K \\;(K \\text{ tıkız Hausdorff}), "
   "\\;\\exists!\\, \\overline{f} : \\beta\\mathcal{X} \\to K, \\; "
   "\\overline{f} \\circ \\iota = f \\\\",
   "Tıkızlaştırmalar bir **küme** teşkil etmez (uygun sınıftır), o "
   "yüzden üzerinde ``ArgMax`` alınamaz. Stone--Čech, bir eniyileme "
   "değil bir **evrensel özellik** ile tanımlanır ve o özellik onu "
   "izomorfizm kadarıyla tek yapar. Yazıldığı hâliyle tanım hem "
   "kümesel olarak geçersiz hem de tekliği vermiyor.",
   "tanimsiz", None),

_t(21, "§6.1 Deriv-Crit", "Küme ile sayı kıyaslanmış",
   [KULLI],
   "\\pi_0(\\mathbf{R}\\text{Crit}(f)) &< \\infty \\implies "
   "\\text{Mutlak Ekstremum Sonlu Adımda Seçilir} \\\\",
   "\\left| \\pi_0(\\mathbf{R}\\text{Crit}(f)) \\right| &< \\infty "
   "\\implies \\text{Mutlak Ekstremum Sonlu Adımda Seçilir} \\\\",
   "$\\pi_0$ bir **kümedir**; bir küme ile $\\infty$ arasında sıralama "
   "yoktur. Kastedilen kardinalitedir. Aynı belgenin 35.5 numaralı "
   "formülünde doğru yazılmış ($|\\pi_0(\\cdot)| \\le K_{\\max}$), "
   "yani belge kendi içinde tutarsız.",
   "tip", None),


# =====================================================================
#  K22: serbest enerji sınırı -- üç belgede birden
# =====================================================================
_t(22, "§7.1 Do-Calculus", "Serbest enerjinin alt sınırı $0$ değil",
   [KULLI],
   "\\mathcal{F}(X, S) &= \\mathbb{E}_{q(S)} \\left[ \\ln q(S) - "
   "\\ln p(X, S) \\right] \\ge 0 \\quad (\\text{Serbest Enerji}) \\\\",
   "\\mathcal{F}(X, S) &= \\mathbb{E}_{q(S)} \\left[ \\ln q(S) - "
   "\\ln p(X, S) \\right] \\;\\ge\\; -\\ln p(X) \\quad "
   "(\\text{eşitlik ancak } q(S) = p(S \\mid X) \\text{ iken}) \\\\",
   "Doğru sınır $\\mathcal{F} \\ge -\\ln p(X)$'tir; bu, "
   "$\\mathcal{F} = -\\ln p(X) + D_{\\mathrm{KL}}(q \\,\\|\\, p(S|X))$ "
   "özdeşliğinden ve KL'in negatif olamamasından çıkar. "
   "$\\mathcal{F} \\ge 0$ ancak $p(X) \\le 1$ iken, yani ayrık $X$'te "
   "doğrudur; sürekli yoğunluklarda $p(X) > 1$ olabilir ve o hâlde "
   "$\\mathcal{F}$ **negatif** olur. Daha mühimi: $0$ sınırı sıkı "
   "değildir, $-\\ln p(X)$ ise sıkıdır ve eniyilemenin nereye "
   "yakınsadığını söyler.",
   "mantik", "test_serbest_enerji_alt_siniri"),

_t(23, "§8.1 Hacim akışı", "Eyer noktası şartı eksik yazılmış",
   [KULLI],
   "\\lambda_{\\max}(\\nabla^2 f) > 0 &\\implies \\text{Eyer Noktasında "
   "Hacim Üssel Yırtılarak Vadiye Çöker} \\\\",
   "\\lambda_{\\min}(\\nabla^2 f) < 0 < \\lambda_{\\max}(\\nabla^2 f) "
   "&\\implies \\text{Eyer Noktası; hacim } \\lambda_{\\min} "
   "\\text{ yönünde yırtılıp vadiye çöker} \\\\",
   "$\\lambda_{\\max} > 0$ tek başına eyer noktası vermez: **yerel "
   "asgarîde de** bütün özdeğerler pozitiftir, dolayısıyla "
   "$\\lambda_{\\max} > 0$'dır. Şart, aynı belgenin 36.2 numaralı "
   "formülünde doğru kurulmuş (Morse indisi = negatif özdeğer sayısı). "
   "Kaçış yönü de $\\lambda_{\\max}$ değil $\\lambda_{\\min}$'in öz "
   "vektörüdür.",
   "mantik", "test_eyer_noktasi_olcutu"),


# =====================================================================
#  K24: operatör öğrenmesi risalesi
# =====================================================================
_t(24, "§6 Sonsuz-kategorik", "Yol integrali çekirdeği PSD değildir",
   [OPERATOR],
   "K_\\infty(x, y) = \\int_{\\text{Map}(I, \\mathcal{C}_\\infty)} "
   "\\mathcal{D}\\gamma \\, \\exp\\left( i S_\\infty(\\gamma; x, y) "
   "\\right)",
   "K_\\infty(x, y) = \\int_{\\text{Map}(I, \\mathcal{C}_\\infty)} "
   "\\mathcal{D}\\gamma \\; \\overline{\\Phi(\\gamma, x)}\\, "
   "\\Phi(\\gamma, y), \\quad \\Phi(\\gamma, x) = e^{i S_\\infty"
   "(\\gamma; x)} \\;\\Longrightarrow\\; K_\\infty \\succeq 0",
   "RKHS kurulabilmesi için çekirdeğin **Hermitesel ve pozitif "
   "yarı-belirli** olması şarttır (Moore--Aronszajn). "
   "$\\exp(i S_\\infty(\\gamma; x, y))$ ne simetriktir ne de PSD; salt "
   "salınımlı bir faz olduğundan Gram dizeyi negatif özdeğer taşır ve "
   "belgenin bir bölüm önce kullandığı Temsil Teoremi (Formül 5.1) "
   "geçersiz kalır. Doğru inşa, çekirdeği bir **öznitelik haritasının "
   "iç çarpımı** olarak kurmaktır; o hâlde PSD'lik yapı gereği sağlanır.",
   "mantik", "test_faz_cekirdegi_psd_degil"),


# =====================================================================
#  K25-K33: analitik darboğazlar külliyatı
# =====================================================================
_t(25, "Darboğaz 1", "Tikhonov çekirdeği yok eder, korumaz",
   [DARBOGAZ],
   " * Formül 1.5 (Analitik Betti-0 Korunum Dengesi): dim(ker(L_eps)) "
   "== beta_0(X)",
   " * Formül 1.5 (Analitik Betti-0 Korunum Dengesi): "
   "#{i | lambda_i(L) <= eps} == beta_0(X)   "
   "[L_eps = L + eps*I icin dim(ker(L_eps)) = 0'dir; duzenleme cekirdegi "
   "yok eder, Betti sayisi eps-esikli ozdeger SAYIMIYLA okunur]",
   "$L_\\epsilon = L + \\epsilon I$ ise $L$'nin her özdeğeri "
   "$\\epsilon$ kadar yukarı kayar; sıfır özdeğer kalmaz ve "
   "$\\dim\\ker(L_\\epsilon) = 0$ olur. Yani Formül 1.1'in getirdiği "
   "düzenleme, Formül 1.5'in ölçmek istediği büyüklüğü **tam olarak "
   "yok eder**. İkisi bir arada tutarsızdır. $\\beta_0$, kaydırılmış "
   "dizeyde çekirdek boyutuyla değil, $\\epsilon$ eşiğinin altındaki "
   "özdeğerlerin sayısıyla okunmalıdır.",
   "mantik", "test_tikhonov_cekirdegi_yok_eder"),

_t(26, "Darboğaz 2", "Grassmann logaritmasında $\\arcsin$ yerine açı",
   [DARBOGAZ],
   " * Formül 2.4 (Logaritma Dönüşüm Haritası): Log_(G_1)(G_2) = U * "
   "arcsin(Sigma) * V^T",
   " * Formül 2.4 (Logaritma Donusum Haritasi): Log_(G_1)(G_2) = "
   "U * diag(theta_i) * V^T,  theta_i = arccos(sigma_i(U_1^T U_2))   "
   "[Formul 2.1'de cos(theta_i) tanimlandigina gore ana acilar "
   "arccos ile okunur; arcsin baska bir buyuklugu verir]",
   "Formül 2.1 asal açıları $\\cos\\theta_i = \\sigma_i(U_1^T U_2)$ "
   "ile tanımlıyor. O hâlde açılar $\\theta_i = \\arccos\\sigma_i$'dir. "
   "Formül 2.4'te $\\arcsin\\Sigma$ yazmak, hangi $\\Sigma$ olduğu "
   "söylenmediği için ya tanımsızdır ya da 2.1 ile çelişir "
   "($\\arcsin\\sigma \\neq \\arccos\\sigma$, ikisi $\\pi/2$'de "
   "toplanır). Formül 2.2'deki mesafe $\\sqrt{\\sum\\theta_i^2}$ ancak "
   "$\\arccos$ ile 2.1'e bağlanır.",
   "isaret", "test_grassmann_asal_acilari"),

_t(27, "Darboğaz 4", "Morse bağıntısı eşitliktir, eşitsizlik değil",
   [DARBOGAZ],
   " * Formül 4.3 (Morse Kuramı Kritik Nokta Eşleşmesi): sum_(k=0)^n "
   "(-1)^k * M_k >= chi(X)",
   " * Formul 4.3 (Morse Bagintisi -- ESITLIK): sum_(k=0)^n (-1)^k * M_k "
   "== chi(X)\n"
   " * Formul 4.3b (Zayif Morse ESITSIZLIKLERI): M_k >= beta_k(X), "
   "forall k",
   "Morse kuramında **iki ayrı** ifade vardır ve karıştırılmıştır: "
   "alterne toplam $\\sum(-1)^k M_k$ Euler karakteristiğine tam "
   "**eşittir** (Morse bağıntısı); eşitsizlikler ise mertebe mertebe "
   "$M_k \\ge \\beta_k$ biçimindedir. Yazıldığı hâliyle eşitlik "
   "gevşetilerek bilgi kaybediliyor ve $\\ge$ yönü zayıf "
   "eşitsizliklerden de gelmiyor.",
   "mantik", "test_morse_bagintisi"),

_t(28, "Darboğaz 10", "Simetrikleştirme idempotentliği geri getirmez",
   [DARBOGAZ],
   " * Formül 10.3 (Analitik İzdüşüm Onarımı): P_düzeltilmiş = 0.5 * "
   "(P_Gr + P_Gr^T)",
   " * Formul 10.3 (Analitik Izdusum Onarimi): U_ortho = Polar(U_k) = "
   "U*V^T  (U_k = U*Sigma*V^T),  P_duzeltilmis = U_ortho * U_ortho^T   "
   "[simetriklestirme idempotentligi VERMEZ; onarim tabani yeniden "
   "dikleyerek yapilir]",
   "Simetrik olmak ile idempotent olmak ayrı şartlardır: "
   "$\\tfrac12(P+P^T)$ simetriktir ama $P^2 = P$'yi sağlamaz. "
   "Sayısal olarak bozulmuş bir izdüşümün onarımı, **tabanın yeniden "
   "diklenmesinden** geçer (kutup ayrışımı veya QR); bu, Formül "
   "10.4'ün zaten söylediği şeydir. 10.3 ile 10.4 aynı işi iddia "
   "ediyor ama yalnız 10.4 doğru.",
   "mantik", "test_simetriklestirme_idempotent_yapmaz"),

_t(29, "Darboğaz 12", "``isSet`` tanımsal indirgeme vermez",
   [DARBOGAZ],
   " * Formül 12.3 (Ayrık Lif hcomp İndirgemesi): hcomp^i A [...] u_0 "
   "---> u_0  (isSet(A) ise)",
   " * Formul 12.3 (Ayrik Lif hcomp Yol-Esitligi): "
   "isSet(A) ==> Path A (hcomp^i A [...] u_0) u_0   "
   "[ONERMESEL esitlik; TANIMSAL indirgeme (--->) DEGILDIR]",
   "``--->`` tanımsal (hesaplamalı) indirgemeyi gösterir. "
   "$\\mathsf{isSet}(A)$ ise $A$'daki *yollar* önerme olur, yani "
   "$\\mathsf{hcomp}$'un neticesi $u_0$ ile **yol-eşit** olur; fakat "
   "değerlendirici onu $u_0$'a indirgemez, sistem boş değilse nötr "
   "kalır. Bu ayrım aynı külliyattaki bir başka risalede de aynı "
   "şekilde kurulmuş ve ``omega_kategori`` modülünde makine ile "
   "çürütülmüştü.",
   "mantik", "test_hcomp_isset_ile_indirgenmez"),

_t(30, "Darboğaz 30", "Ölçek çarpanı alana değil norma aittir",
   [DARBOGAZ],
   " * Formül 30.1 (Izgara Bağımsız Doğrusal Ölçekleme): v_norm(x) = "
   "v(x) * sqrt( Area(Omega) / N_grid )",
   " * Formul 30.1 (Izgara Bagimsiz Norm): ||v_N||_L2 = "
   "sqrt( (Area(Omega)/N_grid) * sum_i |v(x_i)|^2 )   "
   "[olcek carpani QUADRATURE agirligidir; ALANIN kendisine "
   "uygulanirsa alan cozunurluge bagimli hale gelir]",
   "$\\sqrt{|\\Omega|/N}$ bir **quadrature ağırlığıdır**: Riemann "
   "toplamını integrale çevirir ve *norm* hesabına girer. Alanın "
   "kendisini bu çarpanla ölçeklemek, $v$'yi çözünürlüğe bağımlı "
   "kılar -- yani Formül 30.4'ün ($G_{4096}(v) = G_{128}(v)$) tam "
   "aksini yapar. Formül 30.3 zaten doğru hâlini yazıyor; 30.1 onunla "
   "çelişiyor.",
   "olcek", "test_quadrature_agirligi_alana_uygulanmaz"),

_t(31, "Darboğaz 42", "Sıfır kovaryans bağımsızlık demek değildir",
   [DARBOGAZ],
   " * Formül 42.5 (B-Separation İnvaryantı): I( X_i ||_B X_j | Z ) == "
   "I( Cov(X_i, X_j | Z) == 0 )",
   " * Formul 42.5 (B-Separation Invaryanti): I( X_i ||_B X_j | Z ) "
   "==> I( Cov(X_i, X_j | Z) == 0 )   "
   "[tek yonlu; tersi ancak MUSTEREK GAUSS halde dogrudur. Genel halde "
   "sartli bagimsizlik testi kullanilir, kovaryans yetmez]",
   "Sıfır (şartlı) kovaryans, (şartlı) bağımsızlığın **gerek** "
   "şartıdır, yeter şartı değil. $X \\sim U(-1,1)$, $Y = X^2$ alın: "
   "$\\mathrm{Cov}(X,Y) = 0$ fakat $Y$ tamamen $X$ tarafından "
   "belirlenmiştir. Formül çift yönlü ($==$) yazıldığı için, doğrusal "
   "olmayan her bağımlılığı \"bağımsız\" ilan eder -- ki nedensellik "
   "keşfinde en tehlikeli yanılgı budur.",
   "istatistik", "test_sifir_kovaryans_bagimsizlik_degil"),

_t(32, "Darboğaz 62", "Kahan hata sınırı $N$'den bağımsızdır",
   [DARBOGAZ],
   " * Formül 62.5 (Sayısal Duyarlılık İnvaryantı): | KahanSum({x_i}) - "
   "sum_analitik(x_i) | <= N * eps_mach * sum|x_i|",
   " * Formul 62.5 (Sayisal Duyarlilik Invaryanti): "
   "| KahanSum({x_i}) - sum_analitik(x_i) | <= (2*eps_mach + "
   "O(N*eps_mach^2)) * sum|x_i|   "
   "[N'den BAGIMSIZ; N*eps siniri naif toplamanin sinridir ve Kahan'in "
   "butun faydasini siler]",
   "Kahan toplamasının klasik hata sınırı "
   "$(2\\varepsilon + O(N\\varepsilon^2))\\sum|x_i|$'dir ve baş terim "
   "$N$'den **bağımsızdır**; usulün bütün değeri buradadır. "
   "$N\\varepsilon\\sum|x_i|$ ise tam olarak **naif** toplamanın "
   "sınırıdır. Yazıldığı hâliyle formül, Kahan kullanmakla "
   "kullanmamak arasında fark olmadığını söylüyor.",
   "olcek", "test_kahan_hata_siniri_N_den_bagimsiz"),

_t(33, "Darboğaz 63", "Lif hacmi çarpım hacmine eşitse demet aşikârdır",
   [DARBOGAZ],
   " * Formül 63.5 (Lifli Mana Korunumu): ManaHacmi(w) == prod_(j=1)^40 "
   "vol(X_j) > 0",
   " * Formul 63.5 (Lifli Mana Korunumu): 0 < ManaHacmi(w) <= "
   "prod_(j=1)^40 vol(X_j),  ve  int_(w in Taban) ManaHacmi(w) dw == "
   "vol(Theta_40)   [lif TOPLAM uzaya esit olamaz; esit olsaydi "
   "pi bilgi tasimazdi]",
   "$\\mathrm{Fib}_w = \\pi^{-1}(w)$ toplam uzayın bir **lifidir**; "
   "hacmi bütün veçhe uzaylarının çarpımına eşit olsaydı, lif toplam "
   "uzayın kendisi olurdu ve $\\pi$ hiçbir şeyi ayırt etmezdi -- yani "
   "kelimeye göre değişen bir mana kalmazdı. Doğru korunum, liflerin "
   "taban üzerinde **integralinin** toplam hacmi vermesidir (Fubini).",
   "mantik", None),

_t(34, "Darboğaz 66", "Pencereden sonra Parseval eşitliği bozulur",
   [DARBOGAZ],
   " * Formül 66.5 (Girişimsiz Sinyal Korunumu): || Phi_metin_sade ||^2 "
   "== sum || Fib_(w_k) ||^2",
   " * Formul 66.5 (Girisimsiz Sinyal Korunumu): "
   "|| Phi_metin_sade ||^2 == (||w_kaiser||^2 / L) * sum || Fib_(w_k) "
   "||^2   [pencereleme enerjiyi DEGISTIRIR; Parseval ancak pencere "
   "enerjisi carpaniyla kurulur, penceresiz halde ise esitlik tamdir]",
   "Parseval eşitliği ortonormal taban için geçerlidir. Formül 66.3 "
   "sinyali $w_{\\text{kaiser}}$ ile çarpıyor; çarpılmış sinyalin "
   "enerjisi pencerenin enerjisiyle ölçeklenir ve ham katsayı "
   "toplamına **eşit olmaz**. Yani 66.3 ile 66.5 bir arada "
   "duramaz: ya pencere kalkar (eşitlik tam olur) ya da eşitliğe "
   "pencere enerjisi çarpanı girer.",
   "olcek", "test_pencereden_sonra_parseval"),

_t(35, "Darboğaz 41", "Kare olmayan Jacobi'nin tayfı yoktur",
   [DARBOGAZ],
   " * Formül 41.4 (Kararlı Denge Şartı): forall lambda in Spec(J_phi), "
   "Re(lambda) < 0",
   " * Formul 41.4 (Kararli Denge Sarti): m == n olmali (denklem sayisi "
   "= bilinmeyen sayisi); o halde forall lambda in Spec(J_phi), "
   "Re(lambda) < 0.  m != n ise denge tekil degildir ve kararlilik "
   "Spec ile degil, tekil degerlerle (sigma_min(J_phi) > 0) okunur",
   "Formül 41.3 $J_\\phi = [\\partial\\phi_j/\\partial X_k]$'yi "
   "$m \\times n$ olarak tanımlıyor (Formül 41.2'de "
   "$A_{\\text{BGCM}} \\in \\mathbb{R}^{n\\times m}$). Kare olmayan bir "
   "dizeyin **özdeğeri yoktur**, dolayısıyla $\\mathrm{Spec}(J_\\phi)$ "
   "tanımsızdır. Kararlılık ancak $m = n$ iken özdeğerlerle konuşulur.",
   "tip", None),


_t(36, "Darboğaz 2", "İz eşitliği alt uzay eşitliğini göstermez",
   [DARBOGAZ],
   " * Formül 2.5 (Kesintisiz İki-Uzay Aktarım İnvaryantı): "
   "Tr(Exp_(G_1)(Log_(G_1)(G_2))) == Tr(G_2)",
   " * Formul 2.5 (Kesintisiz Iki-Uzay Aktarim Invaryanti): "
   "|| P(Exp_(G_1)(Log_(G_1)(G_2))) - P(G_2) ||_F == 0, "
   "P(Y) = Y (Y^T Y)^(-1) Y^T.  (Iz esitligi ZAYIFTIR: Gr(k,d)'nin "
   "HER noktasinin izi k'dir, dolayisiyla Tr esitligi yanlis bir "
   "Log haritasinda da saglanir)",
   "Grassmann noktalarının izdüşümlerinin izi **her zaman** ``k``dır; "
   "bu yüzden ``Tr(Exp(Log(G₂))) = Tr(G₂)`` her zaman sağlanır ve "
   "hiçbir şey sınamaz. Ölçüldü: kasten yanlış ``arcsin`` Log'uyla "
   "bile iz 3.0000000000 çıkıyor, oysa izdüşümler arası Frobenius "
   "farkı 0.7154. Doğru değişmez izdüşüm farkıdır.",
   "olcut", "test_iz_olcutu_yanlis_log_u_yakalamiyor"),

_t(37, "Darboğaz 46", "Abduction'ın tekilleşme şartı yazılmamış",
   [DARBOGAZ],
   "Sorun: Abduction (Gözlemden gürültü u bulma) safhasında "
   "u = Y_obs - pred denkleminin tekil kalması.",
   "Sorun: Abduction (Gozlemden gurultu u bulma) safhasinda "
   "f_i(pa_i, u_i) = X_i denkleminin u_i icin tek cozumu olmamasi.  "
   "SART: gurultu TOPLAMSAL girdigi surece (X_i = f_i(pa_i) + u_i) "
   "Jacobi alt ucgenseldir, kosegeni I'dir ve u HER ZAMAN tek turlu "
   "cozulur; tekillik ancak gurultu dogrusal olmayan bicimde "
   "girerse (ornek: X_i = f_i(pa_i) + u_i^2) dogar.",
   "Kaynak \"tekil kalıyor\" diyor ama şartını yazmıyor; bu hâliyle "
   "hiçbir zaman tekil olmayan modellerde de bir sorun varmış gibi "
   "görünüyor. Ölçüldü: toplamsal gürültüde abduction 4.4e-16 "
   "hatayla geri çözülüyor; ``B = A + u²`` modelinde ise ``B < A`` "
   "gözleminde kök yoktur ve karşıolgusal hüküm verilemez.",
   "eksik_sart", "test_dogrusal_olmayan_gurultude_tekil"),

_t(38, "Darboğaz 48", "Teğet izdüşümü tek başına locus'ta tutmuyor",
   [DARBOGAZ],
   " * Formül 48.3 (Locus İçi İlerleme Step): "
   "X_(k+1) = X_k + eta * P_locus * v_teğet",
   " * Formul 48.3 (Locus Ici Ilerleme Step): "
   "X_(k+1/2) = X_k + eta * P_locus * v_teget, ardindan Newton "
   "duzeltmesi X_(k+1) = X_(k+1/2) - J_phi^+ phi(X_(k+1/2)).  "
   "(Teget izdusumu yalniz BIRINCI mertebeden dogrudur; ikinci "
   "mertebeden kayma her adimda birikir)",
   "Formül 48.2 doğru, 48.3 **eksiktir**. Teğet izdüşümü ``φ``yi "
   "birinci mertebeden korur; eğrilik yüzünden her adımda "
   "``O(η²)`` kayma birikir. Ölçüldü (birim çember, 200 adım): "
   "düzeltmesiz azamî ihlal ``η=0.05``te 9.9e-02, ``η=0.5``te "
   "1.2e+00. Newton düzeltmesiyle 1.6e-06 ve 1.3e-02.",
   "eksik_adim", "test_duzeltmesiz_tegetin_locustan_kaydigi"),


# =====================================================================
#  Uygulama
# =====================================================================
def uygula(kaynak_dizin: str = KAYNAK,
           hedef_dizin: str = HEDEF) -> Dict[str, List[int]]:
    """Tashihleri uygular; her tashihin TAM BİR KERE eşleştiğini sınar."""
    os.makedirs(hedef_dizin, exist_ok=True)
    metinler = {ad: open(os.path.join(kaynak_dizin, ad),
                         encoding="utf-8").read()
                for ad in DOSYALAR}
    uygulanan: Dict[str, List[int]] = {ad: [] for ad in DOSYALAR}
    for t in T:
        for ad in t.dosyalar:
            sayi = metinler[ad].count(t.eski)
            if sayi != 1:
                raise ValueError(
                    "K%d (%s) %s dosyasında %d kere eşleşti (1 olmalı):\n  %r"
                    % (t.no, t.yer, ad, sayi, t.eski[:100]))
            metinler[ad] = metinler[ad].replace(t.eski, t.yeni)
            uygulanan[ad].append(t.no)
    for ad, metin in metinler.items():
        metin = _basligi_isaretle(metin, uygulanan[ad], ad)
        uzanti = ".txt" if ad.endswith(".txt") else ".tex"
        hedef = ad.replace(uzanti, "_tashihli" + uzanti)
        with open(os.path.join(hedef_dizin, hedef), "w",
                  encoding="utf-8") as f:
            f.write(metin)
    return uygulanan


def _basligi_isaretle(metin: str, nolar: List[int], ad: str) -> str:
    """Tashihli nüshanın başına hangi tashihlerin uygulandığını yazar."""
    if not nolar:
        return metin
    satir = ("Bu nüshaya %d tashih uygulanmıştır (K%s). "
             "Cetvel: docs/kaynak/TASHIH_CETVELI_KUANTUM.md"
             % (len(nolar), ", K".join(str(n) for n in nolar)))
    if ad.endswith(".txt"):
        return "% " * 0 + "[" + satir + "]\n" + metin
    return "%% " + satir + "\n" + metin


def cetvel() -> str:
    """Cetveli kayıtlardan üretir -- elle yazılmaz."""
    turler: Dict[str, int] = {}
    for t in T:
        turler[t.tur] = turler.get(t.tur, 0) + 1
    s: List[str] = []
    s.append("# Tashih cetveli — kuantum ve küllî öğrenme risaleleri")
    s.append("")
    s.append("Bu cetvel `docs/kaynak/tashih_kuantum.py` içindeki "
             "kayıtlardan **üretilmiştir**; elle yazılmamıştır.")
    s.append("")
    s.append("Toplam **%d** tashih, %d belgede." % (len(T), len(DOSYALAR)))
    s.append("")
    s.append("| tür | adet | ne demek |")
    s.append("|---|---:|---|")
    aciklama = {
        "derleme": "belge bu hâliyle derlenmiyor",
        "tip": "tip/boyut uyuşmazlığı veya tanımsız gösterim",
        "boyut": "sayım veya indis aralığı yanlış",
        "mantik": "ifade, kendi öncüllerinden çıkmıyor",
        "vakum": "denetim her zaman doğru — hiçbir şeyi elemiyor",
        "olcek": "ölçek/normalizasyon çarpanı yanlış yerde",
        "isaret": "işaret veya ters fonksiyon hatası",
        "istatistik": "gerek şart yeter şart gibi kullanılmış",
        "tanimsiz": "ifade tanımlı değil",
    }
    for tur in sorted(turler, key=lambda k: -turler[k]):
        s.append("| `%s` | %d | %s |"
                 % (tur, turler[tur], aciklama.get(tur, "")))
    s.append("")
    saglanan = [t for t in T if t.saglama]
    s.append("Bunların **%d**'i ayrıca makine ile sağlanıyor "
             "(`docs/kaynak/test_tashih_kuantum.py`)." % len(saglanan))
    s.append("")
    for t in T:
        s.append("## K%d — %s" % (t.no, t.baslik))
        s.append("")
        s.append("*Yer:* %s  ·  *Tür:* `%s`  ·  *Belge:* %s"
                 % (t.yer, t.tur, ", ".join(t.dosyalar)))
        if t.saglama:
            s.append("")
            s.append("*Makine sağlaması:* `%s`" % t.saglama)
        s.append("")
        s.append("**Kaynakta:**")
        s.append("")
        s.append("```")
        s.append(t.eski)
        s.append("```")
        s.append("")
        s.append("**Tashih:**")
        s.append("")
        s.append("```")
        s.append(t.yeni)
        s.append("```")
        s.append("")
        s.append("**Gerekçe.** " + t.sebep)
        s.append("")
    return "\n".join(s)


def main(argv: List[str]) -> int:
    if "--cetvel" in argv:
        print(cetvel())
        return 0
    uygulanan = uygula()
    for ad in DOSYALAR:
        print("%-40s %2d tashih" % (ad, len(uygulanan[ad])))
    yol = os.path.join(KAYNAK, "TASHIH_CETVELI_KUANTUM.md")
    with open(yol, "w", encoding="utf-8") as f:
        f.write(cetvel())
    print("toplam %d tashih; cetvel: docs/kaynak/TASHIH_CETVELI_KUANTUM.md"
          % len(T))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
