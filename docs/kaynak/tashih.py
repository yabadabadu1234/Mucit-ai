"""
Tashih cetveli: kaynak risalelerdeki formül hatalarının tespiti ve düzeltmesi.

Her tashih bir **veri** kaydıdır: hangi dosya, hangi metin, yerine ne, ve
**niçin**. Böylece:

  * düzeltme kaynak metne birebir uygulanabilir (``uygula()``),
  * her düzeltmenin tam olarak bir kere eşleştiği sınanabilir,
  * cetvel elle değil kayıttan üretilir (``cetvel_yaz()``), yani metin ile
    kod ayrışamaz.

    python3 docs/kaynak/tashih.py            # tashihli nüshaları üretir
    python3 docs/kaynak/tashih.py --cetvel   # cetveli basar

**Ölçüt.** Buraya yalnız *gösterilebilir* hatalar alındı: tip/boyut
uyuşmazlığı, işaret hatası, tanımsız veya erişilemez ifade, mantıkî
denklik hatası, ve bir ifadenin kendi tanım kümesinde özdeş olarak
sıfırlanması. Üslûp tercihleri, gösterim alışkanlıkları ve modelleme
seçimleri **alınmadı** -- onlar hata değildir.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Dict, List, Tuple

KAYNAK = os.path.dirname(os.path.abspath(__file__))
HEDEF = os.path.join(KAYNAK, "tashihli")

KULLI = "nefs_i_mudrike_kulli_formulasyon.tex"
MELEKE = "nefs_i_mudrike_41_meleke.tex"
HOTT = "nefs_i_mudrike_hott_topos.tex"
FITRAT = "nefs_i_mudrike_fitrat_ve_topos.tex"

# ikinci küme: mantık külliyatı ve mimari risaleleri
MIZAN = "mizan_i_muhakemat.tex"
ZEYL = "mizan_zeyl.tex"
GENIS = "mizan_genisletilmis.tex"
MUTEDAHILE = "mizan_mutedahile.tex"
FITRI = "nefs_fitri_tahsil.tex"
TOKEN = "nefs_token_uzaylari.tex"
SORGU = "nefs_sorgu_uzayi.tex"
NORON = "mantik_noronlari.tex"
BUTUNSEL = "nefs_butunsel_idrak.tex"

DOSYALAR = (KULLI, MELEKE, HOTT, FITRAT,
            MIZAN, ZEYL, GENIS, MUTEDAHILE,
            FITRI, TOKEN, SORGU, NORON, BUTUNSEL)


@dataclass(frozen=True)
class Tashih:
    no: int
    yer: str            # hangi meleke / bölüm
    baslik: str
    dosyalar: Tuple[str, ...]
    eski: str
    yeni: str
    sebep: str
    tur: str            # tip | boyut | isaret | mantik | erisilmez | ozdes-sifir | tanimsiz


T: List[Tashih] = []


def _t(no, yer, baslik, dosyalar, eski, yeni, sebep, tur):
    T.append(Tashih(no, yer, baslik, tuple(dosyalar), eski, yeni, sebep, tur))


# =====================================================================
#  1-12: idrak mertebesi
# =====================================================================
_t(1, "𝒪₁ Müşahede", "Dikkat çekirdeğinde $W_k$ düşmüş",
   [KULLI],
   r"\text{Softmax}\left(\frac{X_t W_q X_t^T}{\sqrt{d}}\right) X_t W_v",
   r"\text{Softmax}\left(\frac{(X_t W_q)(X_t W_k)^T}{\sqrt{d}}\right) X_t W_v",
   "Yazıldığı hâliyle anahtar dizeyi birim alınmış oluyor ($W_k = I$). "
   "Bu, aynı külliyattaki HoTT nüshasının "
   r"$\langle X_t W_q, X_t W_k\rangle$ ifadesiyle ve bir satır yukarıdaki "
   r"$V_{\text{odak}}$ tanımında geçen $W_k$ ile çelişir.",
   "tip")

_t(2, "𝒪₁ Müşahede", "Dikkat çekirdeğinde $W_k$ düşmüş",
   [MELEKE],
   r"\text{Softmax}\left(\frac{X_t W_q X_t^T}{\sqrt{d_{\text{in}}}}\right) X_t W_v",
   r"\text{Softmax}\left(\frac{(X_t W_q)(X_t W_k)^T}{\sqrt{d_{\text{in}}}}\right) X_t W_v",
   "Aynı sebep (bkz. T1).",
   "tip")

_t(3, "𝒪₅ Tecrit", "Grassmannian'a izdüşüm diye bir şey yoktur",
   [KULLI],
   r"P_D(X_t) &= \text{Proj}_{\text{Gr}(k,d)}\left( X_t \right) = U_k U_k^T X_t",
   r"P_D(X_t) &= \Pi_V(X_t) = U_k U_k^T X_t, \quad V = \text{span}(U_k) \in \text{Gr}(k,d)",
   "Grassmannian, alt uzayLARIN uzayıdır. Bir vektör Grassmannian'a "
   "izdüşürülmez; Grassmannian'ın bir NOKTASI olan $V$ alt uzayına "
   "izdüşürülür. Yazılışta izdüşümün hedefi ile hedefin yaşadığı uzay "
   "birbirine karışmış.",
   "tip")

_t(4, "𝒪₅ Tecrit", "Grassmannian'a izdüşüm diye bir şey yoktur",
   [MELEKE],
   r"\text{Proj}_{\text{Gr}(k,d_{\text{in}})}\left( X_t \right) = U_k U_k^T X_t",
   r"\Pi_V(X_t) = U_k U_k^T X_t, \quad V = \text{span}(U_k) \in \text{Gr}(k, d_{\text{in}})",
   "Aynı sebep (bkz. T3).",
   "tip")

_t(5, "𝒪₅ Tecrit", "Softmax çıktısı Grassmannian noktası değildir",
   [MELEKE],
   r"D_t &= \text{Softmax}\left( \frac{\Delta_{\text{Laplasyen}}(X_t) W_d}{\sqrt{d_k}} \right) \in \mathcal{T}_{\text{inv}}",
   r"D_t &= U_k U_k^T, \quad \Delta_{\text{Laplasyen}} u_j = \lambda_j u_j, \ \lambda_1 \le \dots \le \lambda_k \quad (\text{izdüşüm; softmax değil})",
   "Softmax çıktısı satır-stokastik bir dizeydir: negatif olmayan, "
   "satır toplamı 1. Bir Grassmannian noktası ise idempotent ve simetrik "
   "bir izdüşüm ($P^2 = P = P^T$) ile temsil edilir. İkisi ayrı "
   "nesnelerdir. Değişmez alt uzay, Laplasyen'in en küçük özdeğerlerine "
   "ait ÖZVEKTÖRLERİN gerdiği uzaydır.",
   "tip")

_t(6, "𝒪₅ Tecrit", "Softmax çıktısı Grassmannian noktası değildir",
   [HOTT],
   r"D_t &= \text{Softmax}\left( \frac{\Delta_{\text{Laplasyen}}(X_t) W_d}{\sqrt{d_k}} \right) \in \text{Gr}(k, d_{\text{in}})",
   r"D_t &= U_k U_k^T, \quad \Delta_{\text{Laplasyen}} u_j = \lambda_j u_j, \ \lambda_1 \le \dots \le \lambda_k \quad (\text{izdüşüm; softmax değil})",
   "Aynı sebep (bkz. T5).",
   "tip")

_t(7, "𝒪₅ Tecrit", "$D_t \\cdot (X_t W_s)$ çarpımı boyut tutmuyor",
   [KULLI, MELEKE],
   r"S_t^{(\text{tecrit})} &= D_t \cdot (X_t W_s) \in \mathcal{S}",
   r"S_t^{(\text{tecrit})} &= (X_t D_t) W_s \in \mathcal{S} \quad (\text{önce izdüşüm, sonra eşleme})",
   r"$D_t \in \mathbb{R}^{d_{\text{in}} \times d_{\text{in}}}$ iken "
   r"$X_t W_s \in \mathbb{R}^{n \times d_{\text{sem}}}$; çarpım tanımsız. "
   "İzdüşüm ham uzayda alınmalı, semantik eşleme ondan SONRA gelmeli.",
   "boyut")

_t(8, "𝒪₅ Tecrit", "$D_t \\cdot (X_t W_s)$ çarpımı boyut tutmuyor",
   [HOTT],
   r"S_t^{(\text{tecrit})} &= D_t \otimes_{\mathcal{O}_{\mathcal{X}}} (X_t W_s) \in \mathcal{S}",
   r"S_t^{(\text{tecrit})} &= (X_t D_t) W_s \in \mathcal{S} \quad (\text{önce izdüşüm, sonra eşleme})",
   "Aynı sebep (bkz. T7); tensör çarpımı ile dizey çarpımı da "
   "birbirinin yerine kullanılmış.",
   "boyut")

_t(9, "𝒪₅ Tecrit", "Betti sayılarının gradyanı alınamaz",
   [MELEKE, HOTT],
   r"\mu_{\text{inv}} \sum_k \|\nabla_{\text{araz}} \beta_k\|^2",
   r"\mu_{\text{inv}} \sum_k \|\nabla_{\text{araz}} \lambda_k(\Delta_{\text{Laplasyen}})\|^2",
   r"$\beta_k \in \mathbb{Z}$; tam sayı değerli fonksiyon hiçbir yerde "
   "türevlenebilir değildir, gradyanı tanımsızdır. Aynı topolojik "
   "kararlılığı denetleyen ve türevlenebilir olan büyüklük Laplasyen'in "
   "spektrumudur (basit özdeğerlerde analitik).",
   "tanimsiz")

_t(10, "𝒪₆ Tasavvur", "Homoloji GRUBU ile ağırlık dizeyi tensörlenemez",
    [KULLI, MELEKE],
    r"H_p\left(\mathcal{S}_{[1:t]}\right) \otimes W_{\text{macro}}",
    r"H_p\left(\mathcal{S}_{[1:t]}; \mathbb{R}\right) \otimes W_{\text{macro}}",
    r"$H_p(\cdot;\mathbb{Z})$ bir değişmeli GRUPTUR; burulma (torsion) "
    "taşıyabilir ve gerçel bir ağırlık dizeyiyle tensörlenmesi ulam "
    r"hatasıdır. Gerçel katsayılarla $H_p(\cdot;\mathbb{R})$ bir vektör "
    "uzayıdır ve çarpım anlam kazanır.",
    "tip")

_t(11, "𝒪₇ Mana", "``RicciFlatTensor`` diye bir işlemci yok; gradyan eğriliğe eşitlenemez",
    [KULLI],
    r"\nabla \mu &= \text{RicciFlatTensor}(S_t)",
    r"\text{Ric}(g) &= 0 \iff R_{ij} = 0 \quad (n \ge 3 \text{ iken } R_{ij} - \tfrac{1}{2}R g_{ij} = 0 \text{ ile denk})",
    r"$\nabla\mu$ bir eş-vektördür, $\text{Ric}$ ise $(0,2)$-tensör; "
    "eşitlenemezler. Kastedilen şart, semantik manifoldun Ricci-düz "
    r"olmasıdır. Ayrıca $n = 2$'de Einstein tensörü ÖZDEŞ olarak sıfırdır, "
    r"yani $R_{ij}-\frac12 Rg_{ij}=0$ orada hiçbir şey söylemez; "
    r"Ricci-düzlüğün doğru ifadesi $R_{ij}=0$'dır.",
    "tip")

_t(12, "𝒪₇ Mana", "``RicciFlatTensor`` diye bir işlemci yok",
    [MELEKE],
    r"\nabla \mu &= \text{RicciFlatTensor}(S_t) \implies R_{ij} - \frac{1}{2} R g_{ij} = 0",
    r"\text{Ric}(g) &= 0 \iff R_{ij} = 0 \quad (n \ge 3 \text{ iken } R_{ij} - \tfrac{1}{2}R g_{ij} = 0 \text{ ile denk})",
    "Aynı sebep (bkz. T11).",
    "tip")

_t(13, "𝒪₂₂ İllet", "$\\dot{I}_t$ bir vektördür, DAG değil",
    [KULLI, MELEKE, HOTT],
    r"\dot{I}_t &= \text{GELU}\left( (S_t W_i) \odot (H_t W_{hi}) \right) \in \mathcal{G}_{\text{neden}}",
    r"\dot{I}_t &= \text{GELU}\left( (S_t W_i) \odot (H_t W_{hi}) \right) \in \mathbb{R}^{d_{\text{sem}}} \quad (\text{nedensel KOD; çizgenin kendisi } A_{\text{neden}})",
    "GELU çıktısı bir vektördür; bir yönlendirilmiş asiklik çizge değil. "
    r"Yanlış tip beyanı belgede üç yerde daha taşıyıcıdır: 𝒪₇'de "
    r"$\langle S_t, \dot{I}_t\rangle_{\mathcal{S}}$ iç çarpımı, 𝒪₁₂'de "
    r"$[S_t \oplus \dot{I}_t \oplus G_t]$ birleştirmesi ve 𝒪₃₃'te "
    r"$\beta \dot{I}_t$ terimi ancak $\dot I_t$ vektör ise anlamlıdır. "
    "Çizge ayrı bir nesnedir ve zaten $A_{\\text{neden}}$ adıyla var.",
    "tip")

_t(14, "𝒪₃₃ Muhakeme", "Skaler integrale vektör eklenmiş",
    [KULLI],
    r"\alpha \langle S_t, G_t \rangle + \beta \dot{I}_t - \gamma \text{Tenakuz}(S_t)",
    r"\alpha \langle S_t, G_t \rangle + \beta \|\dot{I}_t\| - \gamma \text{Tenakuz}(S_t)",
    r"İntegral altındaki ifade skaler olmalı; $\langle S_t,G_t\rangle$ ve "
    r"$\text{Tenakuz}$ skaler iken $\dot I_t$ vektördür.",
    "boyut")

_t(15, "𝒪₃₃ Muhakeme", "Skaler integrale vektör eklenmiş",
    [MELEKE],
    r"\alpha \langle S_t, G_t \rangle + \beta \dot{I}_t - \gamma \text{Tenakuz}(S_t) \Big] dt",
    r"\alpha \langle S_t, G_t \rangle + \beta \|\dot{I}_t\| - \gamma \text{Tenakuz}(S_t) \Big] dt",
    "Aynı sebep (bkz. T14).",
    "boyut")

# =====================================================================
#  13-26: hüküm ve burhân mertebesi
# =====================================================================
_t(16, "𝒪₈ Tahlil", "HSIC'in merkezleme dizeyi tanımsız bırakılmış",
    [MELEKE],
    r"\text{Tr}(K_{\text{cins}} H_{\text{ort centrality}} L_{\text{fasıl}} H_{\text{ort centrality}})",
    r"\text{Tr}(K H L H), \quad H = I_n - \tfrac{1}{n}\mathbf{1}\mathbf{1}^T \ (\text{merkezleme dizeyi})",
    r"``$H_{\text{ort centrality}}$'' bir nesne adı değil; HSIC "
    "kestiricisinde $H$ merkezleme dizeyidir ve tanımlanmadan kestirici "
    "belirsizdir. Merkezleme olmadan ölçüt bağımsızlıkta sıfırlanmaz.",
    "tanimsiz")

_t(17, "𝒪₈ Tahlil", "HSIC'in merkezleme dizeyi tanımsız bırakılmış",
    [HOTT],
    r"\text{Tr}(K_{\text{cins}} H_{\text{ort}} L_{\text{fasıl}} H_{\text{ort}})",
    r"\text{Tr}(K H L H), \quad H = I_n - \tfrac{1}{n}\mathbf{1}\mathbf{1}^T \ (\text{merkezleme dizeyi})",
    "Aynı sebep (bkz. T16).",
    "tanimsiz")

_t(18, "𝒪₉ Terkip", "Metrik geri çekiminde serbest indis",
    [KULLI, MELEKE, HOTT],
    r"g_{\mu\nu}^{(\text{yeni})} &= \sum_{i,j} \frac{\partial x^a}{\partial y^\mu} \frac{\partial x^b}{\partial y^\nu} g_{ab}^{(i)}",
    r"g_{\mu\nu}^{(\text{yeni})} &= \sum_{i=1}^m w_i \frac{\partial x^a}{\partial y^\mu} \frac{\partial x^b}{\partial y^\nu} g_{ab}^{(i)} \quad (a, b \text{ üzerinden Einstein toplamı})",
    r"$j$ toplam indisi olarak yazılmış fakat sağ tarafta hiç geçmiyor; "
    "yazıldığı gibi toplam $m$ katına çıkar. Ayrıca her bileşenin geri "
    r"çekimi, o bileşenin terkipteki ağırlığı $w_i$ ile alınmalıdır.",
    "tanimsiz")

_t(19, "𝒪₁₀ Tezat", "Zıtlık operatörü involüsyon değil",
    [KULLI],
    r"\mathbf{M}_{\text{tezat}} &= \mathbf{S} \cdot \mathbf{W}_{\text{opp}} \cdot \mathbf{S}^T",
    r"\mathbf{M}_{\text{tezat}} &= \mathbf{S} \mathbf{W}_{\text{opp}} \mathbf{S}^T, \quad \mathbf{W}_{\text{opp}} = 2\hat{\mathbf{v}}_{\text{zıt}}\hat{\mathbf{v}}_{\text{zıt}}^T - I, \ \|\hat{\mathbf{v}}_{\text{zıt}}\| = 1",
    r"``Zıtlık'' operatörünün iki kere uygulanınca aslına dönmesi "
    r"beklenir ($\mathbf{W}^2 = I$) ve normu korumalıdır. Householder "
    r"biçimi bunu sağlar; $-I + \mathbf{v}\mathbf{v}^T$ ise ancak "
    r"$\|\mathbf{v}\|^2 = 2$ iken sağlar, ki bu şart metinde yok.",
    "tip")

_t(20, "𝒪₁₀ Tezat", "Zıtlık operatörü involüsyon değil",
    [MELEKE],
    r"\mathbf{W}_{\text{opp}} &= -I_{d \times d} + \mathbf{v}_{\text{zıt}} \mathbf{v}_{\text{zıt}}^T",
    r"\mathbf{W}_{\text{opp}} &= 2\hat{\mathbf{v}}_{\text{zıt}} \hat{\mathbf{v}}_{\text{zıt}}^T - I_{d \times d}, \quad \|\hat{\mathbf{v}}_{\text{zıt}}\| = 1 \ \Rightarrow \ \mathbf{W}_{\text{opp}}^2 = I",
    "Aynı sebep (bkz. T19).",
    "tip")

_t(21, "𝒪₁₁ Tenakuz", "Çelişki çekirdeği iki şartı birden sağlamalı",
    [MELEKE, HOTT],
    r"\langle S_i, S_j \rangle_{\text{çelişki}} &= S_i^T \mathbf{W}_{\text{tenakuz}} S_j",
    r"\langle S_i, S_j \rangle_{\text{çelişki}} &= -S_i^T (A^T A) S_j \quad \Rightarrow \quad \langle S,S \rangle \le 0, \ \ \langle S, -S \rangle = \|AS\|^2",
    "Tenakuzun tarifi iki şart dayatır: (i) hiçbir önerme kendisiyle "
    "çelişmez, (ii) her önerme kendi NAKÎZİYLE çelişir. Kısıtsız "
    r"$\mathbf{W}$ ikisini de sağlamaz. Ters simetrik $\mathbf{W}$ "
    r"(i)'yi sağlar fakat (ii)'yi YIKAR: $S^T\mathbf{W}(-S) = 0$. "
    r"Yarı-negatif $\mathbf{W} = -A^TA$ ikisini birden sağlar. Bu, "
    r"``nefs'' modülünde önce ters simetrik kurulup sınamayla yakalanan "
    "ve ölçümle düzeltilen hatadır.",
    "mantik")

_t(22, "𝒪₁₁ Tenakuz", "Gösterge klasik olarak $\\neg S_i$'ye denk",
    [MELEKE, HOTT],
    r"\mathbb{I}_{\text{tenakuz}} &= \mathbb{I}\left( (S_i \implies S_j) \land (S_i \implies \neg S_j) \right)",
    r"\mathbb{I}_{\text{tenakuz}} &= \mathbb{I}\left( S_i \land S_j \vdash \bot \right) \quad (\text{eski hâl} \equiv \neg S_i, \text{ yani } S_i\text{'nin YANLIŞLIĞI})",
    r"Klasik mantıkta $(S_i \to S_j) \land (S_i \to \neg S_j) \equiv "
    r"\neg S_i$. Yani yazılan gösterge, $S_i$ ile $S_j$ arasındaki "
    r"çelişkiyi değil, $S_i$'nin yanlış olduğunu tespit eder -- "
    r"$S_i$ yanlışsa iki gerektirme de boşluktan doğrudur.",
    "mantik")

_t(23, "𝒪₁₃ Tasdik", "Tasdik mührü ERİŞİLEMEZ bir eşikte",
    [KULLI, MELEKE, HOTT],
    r"T_t &= \sigma\left( \text{CosSim}(M_t^{(\mathcal{K})} W_t, G_t) - \text{Tenakuz}(M_t^{(\mathcal{K})}, S_t, H_t) \right) \in [0, 1]",
    r"T_t &= \sigma\left( \beta_T \left[ \text{CosSim}(M_t^{(\mathcal{K})} W_t, G_t) - \text{Tenakuz}(M_t^{(\mathcal{K})}, S_t, H_t) \right] \right) \in (0,1), \quad \beta_T \ge 4",
    r"$\text{CosSim} \le 1$ ve $\text{Tenakuz} \ge 0$ olduğundan "
    r"$\sigma$'nın argümanı $1$'i aşamaz, dolayısıyla "
    r"$T_t \le \sigma(1) = 0{,}731$. Buna karşılık mühür şartı "
    r"$\mathbb{I}(T_t \ge 1-\epsilon)$, $\epsilon = 0{,}05$ için "
    r"$T_t \ge 0{,}95$ ister. Yani tasdik mührü HİÇBİR ZAMAN vurulamaz. "
    r"Kazanç katsayısı $\beta_T$ şarttır; $\beta_T \ge 4$ eşiği "
    "erişilebilir kılar.",
    "erisilmez")

_t(24, "𝒪₃₀ Tahkik", "Aynı erişilemez eşik kusuru",
    [KULLI, MELEKE],
    r"T_{\text{tahkik}} &= \sigma\left( \text{CosSim}(S_{\text{tahkik}}, S_{\text{asıl}}) \right)",
    r"T_{\text{tahkik}} &= \sigma\left( \beta_T \left[ \text{CosSim}(S_{\text{tahkik}}, S_{\text{asıl}}) - \theta \right] \right), \quad \beta_T \ge 4",
    r"$\text{CosSim} \in [-1,1]$ olduğundan $\sigma(\text{CosSim}) \in "
    r"[0{,}269,\ 0{,}731]$. $\mathbb{I}(T > 1-\delta)$ şartı "
    r"$\delta < 0{,}269$ için hiç sağlanamaz (bkz. T23).",
    "erisilmez")

_t(25, "𝒪₁₃ Tasdik", "Skaler türeve vektör çarpanı eklenmiş",
    [MELEKE, HOTT],
    r"\nabla_T \mathcal{L} &= (T_t - T_{\text{hedef}}) \cdot S_t",
    r"\frac{\partial \mathcal{L}}{\partial T_t} &= T_t - T_{\text{hedef}}, \qquad \nabla_{S_t} \mathcal{L} = (T_t - T_{\text{hedef}}) \, \nabla_{S_t} T_t",
    r"$\mathcal{L} = \tfrac12 (T_t - T_{\text{hedef}})^2$ için "
    r"$T_t$'ye göre türev SKALERDİR. $S_t$ çarpanı zincir kuralından "
    r"gelir ve $\nabla_{S_t}\mathcal{L}$'ye aittir; ikisi karışmış.",
    "boyut")

_t(26, "𝒪₁₅ Merak", "Olasılığın varyansı değil, $S_t$'nin şartlı varyansı",
    [KULLI],
    r"\mathcal{H}_{\text{bilgisizlik}}(S_t) &= \text{Var}(P(S_t \mid H_t))",
    r"\mathbb{V}_{\text{bilgisizlik}}(S_t) &= \text{Var}_{P(\cdot \mid H_t)}[S_t]",
    r"``Bir olasılığın varyansı'' tanımsızdır; kastedilen, $S_t$'nin "
    r"$P(\cdot \mid H_t)$ altındaki varyansıdır. Ayrıca $\mathcal{H}$ "
    r"simgesi aynı belgede (𝒪₈, 𝒪₁₇, 𝒪₂₁) ENTROPİ için ayrılmış; "
    r"varyans için kullanılması iki ayrı büyüklüğü karıştırır.",
    "tanimsiz")

_t(27, "𝒪₁₅ Merak", "Olasılığın varyansı değil, $S_t$'nin şartlı varyansı",
    [MELEKE, HOTT],
    r"\mathcal{H}_{\text{bilgisizlik}}(S_t) &= \text{Var}(P(S_t \mid H_t)) = \mathbb{E}[(S_t - \mu_S)^2 \mid H_t]",
    r"\mathbb{V}_{\text{bilgisizlik}}(S_t) &= \text{Var}_{P(\cdot \mid H_t)}[S_t] = \mathbb{E}[(S_t - \mu_S)^2 \mid H_t]",
    "Aynı sebep (bkz. T26). Sağ taraftaki ifade zaten varyanstır; "
    "yanlış olan sol taraftaki yazılış ve simgedir.",
    "tanimsiz")

_t(29, "𝒪₁₇ İhtimal", "Laplace kaidesi bir toplama terimi değil",
    [MELEKE, HOTT],
    r"\mathbf{L}_{\text{Laplace}} &= P_0(S) + \frac{k+1}{n+2}",
    r"\hat{P}_{\text{Laplace}}(S) &= \frac{n_S + \alpha}{n + \alpha |\mathcal{S}|}, \quad \alpha = 1 \ \Rightarrow \ \frac{k+1}{n+2} \ (\text{ikili hâl})",
    r"$\frac{k+1}{n+2}$ (ardıllık kaidesi) kestirimin KENDİSİDİR. "
    r"Bir önsele eklenirse ortaya çıkan büyüklük ne olasılıktır ne de "
    r"normalizedir. Genel hâli toplamalı düzleştirmedir (additive "
    r"smoothing) ve $\alpha=1$'de ardıllık kaidesine iner.",
    "mantik")

_t(30, "𝒪₁₈ Kıyas", "Vektörler arasında kapsama ($\\subset$) tanımsız",
    [MELEKE, HOTT],
    r"\mathbb{I}(S_{\text{cüz'î}} \subset S_{\text{küllî}}) \cdot P(S_{\text{küllî}})",
    r"\mathbb{I}\big(\text{span}(S_{\text{cüz'î}}) \subseteq \text{span}(S_{\text{küllî}})\big) \cdot P(S_{\text{küllî}})",
    r"$\subset$ kümeler arasındadır. Cüz'înin küllî altına girmesi, "
    "gerdikleri alt uzayların kapsanmasıdır.",
    "tip")

_t(31, "𝒪₂₀ Teşbih", "Vektörün izi alınamaz",
    [MELEKE, HOTT],
    r"\mathbf{P}_{\text{ortak\_altuzay}} &= \text{Proj}_{\mathcal{S}_A \cap \mathcal{S}_B}(S_A) \\",
    r"\mathbf{P}_{\text{ortak}} &= \text{ortak alt uzaya dik izdüşüm DİZEYİ}, \quad \Pi_{\text{ortak}}(S_A) = \mathbf{P}_{\text{ortak}} S_A \\",
    r"$\text{Proj}_V(S_A)$ bir VEKTÖRDÜR; bir satır sonra izi alınıyor, "
    "oysa iz dizeylere aittir. İz, izdüşüm DİZEYİNE aittir ve değeri "
    "tam olarak ortak alt uzayın boyutudur -- vech-i şebeh ölçüsü "
    "olarak da aranan budur.",
    "tip")

_t(32, "𝒪₂₀ Teşbih", "Benzerlik skoru izdüşüm dizeyinin izidir",
    [MELEKE, HOTT],
    r"\text{BenzerlikSkoru} &= \text{Tr}(\mathbf{P}_{\text{ortak\_altuzay}})",
    r"\text{BenzerlikSkoru} &= \text{Tr}(\mathbf{P}_{\text{ortak}}) = \dim(\mathcal{S}_A \cap \mathcal{S}_B)",
    "T31'in doğrudan devamı: izdüşüm DİZEYİNİN izi, ortak alt uzayın "
    "boyutuna eşittir; vech-i şebeh ölçüsü olarak aranan da budur.",
    "tip")

_t(33, "𝒪₂₁ Tefekkür", "İŞARET HATASI: akış gayeden uzaklaştırıyor",
    [KULLI, MELEKE, HOTT],
    r"\dot{S}_t &= \nabla \mathcal{V}_{\text{tefekkür}}(S_t)",
    r"\dot{S}_t &= -\nabla \mathcal{V}_{\text{tefekkür}}(S_t) \quad (\text{İNİŞ; artı işaret gayeden UZAKLAŞTIRIR})",
    r"$\mathcal{V}_{\text{tefekkür}} = \tfrac12\|S-G_t\|^2 + "
    r"\lambda\,\text{Tenakuz}$ bir maliyettir. Artı işaretli akış "
    "gradyan ÇIKIŞIDIR: hem gayeden uzaklaşır hem tenakuzu artırır. "
    "Metnin kendi tarifiyle (tefekkür neticeye yaklaştırır) çelişir.",
    "isaret")

_t(34, "𝒪₂₁ Tefekkür", "İŞARET HATASI: entropinin eksisi düşmüş",
    [KULLI, MELEKE, HOTT],
    r"\mathcal{H}_{\text{tefekkür}} &= \int_{\mathcal{S}} P(S_t) \log P(S_t) dS",
    r"\mathcal{H}_{\text{tefekkür}} &= -\int_{\mathcal{S}} P(S_t) \log P(S_t) \, dS",
    "Entropi eksi işaretlidir. Aynı belge 𝒪₁₇'de "
    r"$-\int P \log P$ diye DOĞRU yazıyor; iki yer birbiriyle çelişiyor.",
    "isaret")

_t(35, "𝒪₂₂ İllet", "Nedensel karmaşıklık DAG üzerinde ÖZDEŞ SIFIR",
    [KULLI, MELEKE, HOTT],
    r"\mathcal{C}_{\text{nedensel}} &= \text{Trace}(A_{\text{neden}}) - \log \det(I + A_{\text{neden}})",
    r"\mathcal{C}_{\text{nedensel}} &= \|A_{\text{neden}}\|_1 \quad (\text{eski hâl DAG'da} \equiv 0: \ \text{Tr}(A) = 0, \ \det(I+A) = 1)",
    "Bir DAG'ın komşuluk dizeyi topolojik sıralamada üst üçgen, yani "
    r"nilpotenttir. O hâlde $\text{Tr}(A) = 0$ ve $I+A$ birim köşegenli "
    r"üst üçgen olduğundan $\det(I+A) = 1$, $\log\det = 0$. Yani ifade "
    r"kendi tanım kümesinde özdeş olarak sıfırdır ve hiçbir şey ölçmez. "
    r"``nefs'' modülünde sayısal olarak da 0 ölçüldü.",
    "ozdes-sifir")

_t(36, "𝒪₂₂ İllet", "Softmax dizeyi DAG değildir",
    [MELEKE, HOTT],
    r"\dot{I}_{\text{kebîr}} &= \text{DAG\_Sentezi}(S_{\text{kebîr}}, H_{[1:t]}) = \text{Softmax}\left( \frac{S_{\text{kebîr}} A_{\text{neden}} S_{\text{kebîr}}^T}{\sqrt{d_{\text{sem}}}} \right)",
    r"A_{\text{neden}} &= \Pi_{\prec} \left[ \text{Softmax}\left( \frac{S_{\text{kebîr}} W_{\text{dag}} S_{\text{kebîr}}^T}{\sqrt{d_{\text{sem}}}} \right) \right], \quad \Pi_{\prec} = \text{topolojik sıraya göre üst üçgen maske}",
    "Softmax çıktısı yoğun, satır-stokastik ve köşegeni sıfırdan "
    "farklıdır -- yani her düğümün kendine kenarı vardır. Böyle bir "
    "dizey hiçbir zaman asiklik değildir. Asiklik DAYATILMALIDIR: bir "
    "topolojik sıra sabitlenip yalnız o sırayla uyumlu girdiler "
    r"bırakılır; o zaman $h(A) = \text{Tr}(e^{A \circ A}) - d = 0$ inşa "
    r"gereği sağlanır. Ayrıca $A_{\text{neden}}$ hem tanımın girdisi hem "
    "çıktısı olarak kullanılmış (döngüsel tanım).",
    "tip")

_t(37, "𝒪₂₃ Mantık", "Geçerlilik ile tutarlılık aynı şey değil",
    [KULLI, MELEKE, HOTT],
    r"\text{Geçerlilik}(R) &= \mathbb{I}(\text{Tenakuz}(R) = 0)",
    r"\text{Geçerlilik}(P_1, \dots, P_n \vdash Q) &= \mathbb{I}\big( \models (P_1 \land \dots \land P_n) \to Q \big)",
    "Çelişki barındırmayan bir çıkarım geçerli olmak zorunda değildir. "
    "Geçerlilik, gerektirmenin HER modelde doğru olmasıdır; "
    "tutarlılık ise kesinlikle daha zayıf bir şarttır. İkisi "
    "özdeşleştirilirse geçersiz çıkarımlar geçerli sayılır.",
    "mantik")

_t(38, "𝒪₂₆ Temkin", "Dizey ile örneklem toplanamaz",
    [KULLI, MELEKE, HOTT],
    r"\mathbf{K}_{\text{temkin}} &= \mathbf{S}_t + \mu_{\text{emniyet}} \cdot \mathbf{\Sigma}_{\text{gürültü}}",
    r"\mathbf{K}_{\text{temkin}} &= \mathbf{S}_t + \mu_{\text{emniyet}} \, \xi, \quad \xi \sim \mathcal{N}(0, \mathbf{\Sigma}_{\text{gürültü}})",
    r"$\mathbf{S}_t \in \mathbb{R}^{n \times d}$ iken "
    r"$\mathbf{\Sigma}_{\text{gürültü}} = \mathbb{E}[\delta\delta^T] "
    r"\in \mathbb{R}^{d\times d}$; toplanamazlar. Sarsma, o kovaryanstan "
    "çekilen bir ÖRNEKLEMLE girer.",
    "boyut")

_t(39, "𝒪₂₇ Tetkik", "Skalerin LayerNorm'u tanımsız",
    [KULLI, MELEKE],
    r"\text{Skor}_{\text{tetkik}} &= \text{LayerNorm}\left(\sum \text{KusurHaritası}\right)",
    r"\text{Skor}_{\text{tetkik}} &= \text{LayerNorm}\Big( \textstyle\sum_{i} \text{KusurHaritası}_{i\cdot} \Big) \in \mathbb{R}^{d_{\text{sem}}}",
    r"İndissiz $\sum$ bütün girdileri toplar ve skaler verir. LayerNorm "
    "ortalamayı çıkarıp standart sapmaya böler; skalerde ikisi de "
    r"dejenere olur ($0/0$). Toplam TEK eksen üzerinden alınmalı ki "
    "sonuç vektör kalsın.",
    "tanimsiz")

_t(40, "𝒪₂₇ Tetkik", "Tensör çarpımı yerine Hadamard çarpımı",
    [KULLI, MELEKE],
    r"|\delta S_{t, \text{kılcal}} - S_{\text{ideal}}| \otimes W_{\text{tetkik}}",
    r"|\delta S_{t, \text{kılcal}} - S_{\text{ideal}}| \odot W_{\text{tetkik}}",
    r"$\otimes$ mertebeyi yükseltir ve bir sonraki satırda toplanan "
    "nesneyle uyuşmaz; kastedilen ve boyutların izin verdiği işlem "
    "öge-öge çarpımdır.",
    "tip")

_t(41, "𝒪₂₉ Teyit", "Bayes güncellemesi ŞARTLI bağımsızlık ister",
    [KULLI, MELEKE, HOTT],
    r"E_{\text{bağımsız}} &= \text{Kanal}_2(X_t) \quad (\text{Kanal}_1 \perp \text{Kanal}_2)",
    r"E_{\text{bağımsız}} &= \text{Kanal}_2(X_t), \quad E_1 \perp\!\!\!\perp E_2 \mid H \quad (\text{ŞARTLI bağımsızlık})",
    r"Bir satır aşağıdaki $P(H\mid E_1,E_2) = "
    r"\frac{P(E_2\mid H)P(H\mid E_1)}{P(E_2\mid E_1)}$ güncellemesi tam "
    r"olarak $E_1 \perp\!\!\!\perp E_2 \mid H$ şartı altında geçerlidir. "
    "Metnin yazdığı MARJİNAL bağımsızlık ne yeterlidir ne de -- iki "
    r"kanal da $H$ hakkında bilgi taşıyorken -- şartlı bağımsızlıkla "
    "genelde bir arada bulunabilir.",
    "mantik")

_t(42, "𝒪₂₉ Teyit", "Kovaryans sınırsız; bağımsızlık düzeyi negatife kaçar",
    [MELEKE, HOTT],
    r"\text{BağımsızlıkDüzeyi} &= 1 - |\text{Cov}(E_1, E_2)|",
    r"\text{BağımsızlıkDüzeyi} &= 1 - |\rho(E_1, E_2)| \in [0,1], \quad \rho = \frac{\text{Cov}(E_1,E_2)}{\sigma_{E_1}\sigma_{E_2}}",
    r"Kovaryans normalize değildir ve $1$'i aşabilir; o zaman "
    r"``bağımsızlık düzeyi'' negatif olur ve bir sonraki satırdaki "
    "çarpım teyit skorunu ters çevirir. Korelasyon katsayısı "
    r"$[-1,1]$'de sınırlıdır.",
    "tip")

_t(43, "𝒪₃₁ Tedebbür", "ArgMax değişkeni amaç fonksiyonunda geçmiyor",
    [MELEKE, HOTT],
    r"\text{ArgMax}_a \left( \mathcal{V}_{\text{akıbet}}(S_t) - \gamma \mathcal{Risk}_{\text{tedebbür}} \right)",
    r"\text{ArgMax}_a \left( \mathcal{V}_{\text{akıbet}}(S_t, a) - \gamma \mathcal{Risk}_{\text{tedebbür}}(S_t, a) \right)",
    r"Her iki terim de $a$'dan bağımsız yazılmış; o hâlde argmax boş bir "
    "işlemdir ve emniyetli hamle seçilemez.",
    "tanimsiz")

_t(44, "𝒪₃₂ Şek-Zan-Yakîn", "Makam parçalanışında BOŞLUK",
    [KULLI, MELEKE, HOTT],
    r"\text{Yakîn } (\%100), & P_{\text{idrak}} \ge 1 - \epsilon_{\text{yakîn}}",
    r"\text{Yakîn } (\%100), & P_{\text{idrak}} \ge 1 - \epsilon_{\text{yakîn}} \\" "\n"
    r"\text{Vehim } (\%1-\%49), & P_{\text{idrak}} < 0.5 - \epsilon_{\text{şek}}",
    r"Yazılan üç şart $P_{\text{idrak}} < 0{,}5 - \epsilon_{\text{şek}}$ "
    r"aralığını KAPSAMIYOR; orada $\text{Makam}$ tanımsız kalıyor. "
    r"Aleyhte zan (Vehim) eklenince parçalanış hem TAM hem AYRIK olur "
    r"ve $P$ arttıkça makam gerilemez.",
    "tanimsiz")

_t(45, "𝒪₃₅ Tefsir", "Dikkat ağırlıkları murâd değildir",
    [KULLI],
    r"\text{Softmax}\left( \frac{S_{\text{müphem}} W_{\text{tefsir}} \cdot [\text{Siyak} \oplus \text{Sibak}]^T}{\sqrt{d}} \right)",
    r"\text{Softmax}\left( \frac{S_{\text{müphem}} W_{\text{tefsir}} [\text{Siyak} \oplus \text{Sibak}]^T}{\sqrt{d}} \right) [\text{Siyak} \oplus \text{Sibak}] W_v",
    "Softmax tek başına yalnız AĞIRLIK verir; murâd, bağlamın o "
    "ağırlıklarla harmanıdır. Değer çarpanı olmadan sol taraf bir "
    "mana vektörü değil, bir olasılık dağılımıdır. 41-meleke "
    "nüshasında bu çarpan zaten var; iki nüsha çelişiyor.",
    "tip")

_t(46, "𝒪₃₇ Fesâhat", "Skor aşağıdan sınırsız",
    [KULLI, MELEKE, HOTT],
    r"\text{FesâhatScore}(N_t) &= 1 - \left[ \mu_1 \text{Tenâfür}(N_t) + \mu_2 \text{Garâbet}(N_t) + \mu_3 \text{Ta'kîd}(N_t) \right]",
    r"\text{FesâhatScore}(N_t) &= 1 - \left[ \mu_1 \tilde{T}(N_t) + \mu_2 \tilde{G}(N_t) + \mu_3 \tilde{K}(N_t) \right] \in [0,1], \quad \tilde{\cdot} = \tfrac{x}{1+x} \in [0,1], \ \textstyle\sum_i \mu_i = 1",
    r"Üç kusur terimi de yukarıdan sınırsızdır (özellikle "
    r"$\text{Garâbet} = -\sum \log P$ uzunlukla büyür), dolayısıyla "
    r"skor aşağıdan sınırsızdır ve bir ``derece'' olmaktan çıkar. "
    r"``nefs'' modülünde sıkıştırmasız hâli $-18$ ölçüldü. Her terim "
    r"$[0,1]$'e sıkıştırılıp ağırlıklar toplamı 1 yapılınca skor "
    r"gerçekten $[0,1]$'de kalır.",
    "tip")

_t(47, "𝒪₃₇ Fesâhat", "Frekans olasılık değildir",
    [MELEKE, HOTT],
    r"P_{\text{lügat}}(y) &= \text{Frekans}_{\text{korpus}}(y)",
    r"P_{\text{lügat}}(y) &= \frac{\text{Frekans}_{\text{korpus}}(y)}{\sum_{w} \text{Frekans}_{\text{korpus}}(w)}",
    r"Normalize edilmemiş bir frekans $1$'i aşabilir; o zaman "
    r"$-\log P$ NEGATİF olur ve garâbet, kusur ölçüsü olmaktan çıkıp "
    "ödüle döner.",
    "tip")

_t(48, "𝒪₃₉ Belâgat", "$\\exp$ Lie CEBRİNDEN Lie GRUBUNA gider",
    [MELEKE, HOTT],
    r"R_{\text{belâgat}} &= \exp\left( \theta \mathbf{X}_{\text{muktezâ\_hâl}} \right) \in \mathfrak{g}",
    r"\mathbf{X}_{\text{muktezâ\_hâl}} \in \mathfrak{g}, \quad R_{\text{belâgat}} &= \exp(\theta \mathbf{X}_{\text{muktezâ\_hâl}}) \in G = \exp(\mathfrak{g})",
    r"Üstel eşleme $\exp : \mathfrak{g} \to G$ cebirden GRUBA gider. "
    r"$\exp(\theta X)$ bir grup ögesidir, cebir ögesi değil. "
    r"($X$ ters simetrik seçilirse $R \in SO(d)$ olur ve normu korur -- "
    r"``tasarruf''un muhtaç olduğu da budur.)",
    "tip")

_t(49, "𝒪₄₀ Sanat", "Simetrik harmoni normalize değil, negatife düşüyor",
    [MELEKE, HOTT],
    r"\text{SimetrikHarmoni}(Y) &= 1 - \| Y - Y^T \|_{\mathcal{F}}",
    r"\text{SimetrikHarmoni}(Y) &= 1 - \frac{\| Y - Y^T \|_{\mathcal{F}}}{2\|Y\|_{\mathcal{F}}} \in [0,1], \quad Y \text{ kare}",
    r"İki kusur var. (i) Payda yok: ölçü $Y$'nin BÜYÜKLÜĞÜNE bağlı olur, "
    r"oysa ahenk bir orandır -- aynı şekilli iki dizeden büyük olanı "
    r"``daha ahenksiz'' görünür. (ii) $\|Y-Y^T\|^2 = 2\|Y\|^2 - "
    r"2\langle Y, Y^T\rangle \le 4\|Y\|^2$ olduğundan yalnız $\|Y\|$'a "
    r"bölmek ölçüyü $[-1,1]$'e taşır; ``ahenk'' negatif olabilir "
    r"(``nefs'' modülünde $-0{,}351$ ölçüldü). $2\|Y\|$ ile bölününce "
    "ölçü simetrik dizede tam 1, ters simetrik dizede tam 0'dır.",
    "tip")

# =====================================================================
#  50-58: HoTT / kübik nüshaya mahsus
# =====================================================================
_t(50, "𝒪₁ Müşahede (HoTT)", "Glue $\\beta$-kuralı gösterge diye yazılmış",
    [HOTT],
    r"\mathbf{1}_{\text{müşahede}} &= \text{unglue}(\text{glue } X_t \, [\dots])",
    r"\text{unglue}\big(\text{glue } X_t \, [\varphi \mapsto (t, e)]\big) &\equiv X_t \quad (\text{Glue } \beta\text{-kuralı})",
    r"Kübik tip teorisinde $\text{unglue}(\text{glue } a\,[\dots]) "
    r"\equiv a$ TANIMSAL bir denkliktir; yani sol taraf $X_t$'nin "
    r"kendisidir, bir gösterge ($\mathbf{1}$) değil. Özdeşlik olarak "
    r"yazılınca doğru ve mânâlı olur. Bu kural bu depoda MAKİNEYLE "
    r"denetleniyor (\texttt{omega\_kategori\_nbe}).",
    "tip")

_t(51, "𝒪₁ Müşahede (HoTT)", "Sabit çizgide $\\text{transp}$ özdeşliktir, süzgeç değil",
    [HOTT],
    r"X_{t, \text{süzülmüş}} &= \text{transp}^i (\lambda i. \mathcal{X}) \, \varphi \, X_t",
    r"X_{t, \text{süzülmüş}} &= X_t \odot \sigma(W_{\text{süzgeç}} X_t); \quad \text{transp}^i (\lambda i.\, \mathcal{X}) \, \varphi \, X_t \equiv X_t \ (\text{SABİT çizgi})",
    r"Çizgi sabit olduğunda ($\lambda i.\,\mathcal{X}$) taşıma tanımsal "
    r"olarak özdeşliktir: $\text{transp}^i (\lambda i. A)\,\varphi\,u "
    r"\equiv u$. Yani yazılan ifade hiçbir şey süzmez. Gerçek süzgeç "
    "41-meleke nüshasındaki kapı çarpanıdır.",
    "ozdes-sifir")

_t(52, "𝒪₄ Tertip (HoTT)", "$\\simeq$ TİPLER arasındadır, terimler arasında değil",
    [HOTT],
    r"\text{Equiv}_{\text{tertip}} &= (\mathbf{Z}_{\text{ham}} \simeq \mathbf{Z}_{\text{düzenli}}) \in \mathbf{U}",
    r"\sigma_\pi : \mathcal{H}^N &\simeq \mathcal{H}^N \in \mathbf{U} \quad (\text{permütasyon tersinir} \Rightarrow \text{tertip bilgi kaybetmez})",
    r"$\simeq$ tipler arası denkliktir; $\mathbf{Z}_{\text{ham}}$ ve "
    r"$\mathbf{Z}_{\text{düzenli}}$ ise TERİMDİR (ve zaten eşit "
    "değildirler -- tertip onları değiştirir). Tersinir olan, tip "
    "üzerindeki permütasyon etkisidir; kastedilen mânâyı taşıyan da odur.",
    "tip")

_t(53, "𝒪₁₀ Tezat (HoTT)", "Türetilmiş kritik yer bir ögesi değil, KENDİSİDİR",
    [HOTT],
    r"\text{Fiber}_{\text{tezat}} &= \text{Crit}(\Theta_{\text{tezat}}) \in \mathbf{R}\text{Crit}(f)",
    r"\mathbf{R}\text{Crit}(\Theta_{\text{tezat}}) &= \mathcal{S} \times^{h}_{d\Theta, \, T^*\mathcal{S}, \, 0} \mathcal{S} \quad (\text{homotopi lif çarpımı})",
    r"$\mathbf{R}\text{Crit}(\Theta)$ bir NESNEDİR: $d\Theta$ ile sıfır "
    r"kesitinin homotopi lif çarpımı. ``$\text{Crit}(\Theta) \in "
    r"\mathbf{R}\text{Crit}(f)$'' hem nesneyi kendi ögesi yapıyor hem de "
    r"alakasız bir $f$ getiriyor.",
    "tip")

_t(54, "𝒪₁₁ Tenakuz (HoTT)", "Özdeşlik tipi $\\mathbf{Prop}$ üzerinde değil",
    [HOTT],
    r"\text{Path}_{\text{tenakuz}} &= (\text{Tenakuz}(S_i, S_j) =_{\mathbf{Prop}} \mathbf{0})",
    r"\text{Path}_{\text{tenakuz}} &= \big\| \text{Tenakuz}(S_i, S_j) =_{\mathbb{R}} 0 \big\| \in \mathbf{Prop}",
    r"$\text{Tenakuz}$ gerçel değerlidir; özdeşlik tipi $\mathbb{R}$ "
    r"üzerinde kurulur. $\mathbf{Prop}$'a inen şey o özdeşlik tipinin "
    r"ÖNERMESEL KESMESİDİR ($\|\cdot\|$).",
    "tip")

_t(55, "𝒪₁₃ Tasdik (HoTT)", "Univalence gerçel sayılara tatbik edilemez",
    [HOTT],
    r"\text{Univalence}_{\text{tasdik}} &= (T_t \simeq 1) \simeq (S_t =_{\mathcal{S}} G_t)",
    r"\text{ua} : (A \simeq B) &\simeq (A =_{\mathcal{U}} B) \ (\text{TİPLER arası}); \quad \mathbf{1}_{\text{tasdik}} = 1 \iff \big\| S_t =_{\mathcal{S}} G_t \big\|",
    r"Univalence aksiyomu TİPLER hakkındadır. $T_t \simeq 1$ iki gerçel "
    "sayı arasında bir tip denkliği değildir. Tasdikin doğru ifadesi, "
    r"$\mathcal{S}$'deki bir yolun varlığına dair bir ÖNERMEDİR.",
    "tip")

# --- Fıtrat ve topos tebliği ---
_t(56, "Tebliğ §1.1", "Serbest enerji $\\ge 0$ değildir",
    [FITRAT],
    r"\mathcal{F}(X, S) &= \mathbb{E}_{q(S)} \left[ \ln q(S) - \ln p(X, S) \right] \ge 0",
    r"\mathcal{F}(X, S) &= \text{KL}\big( q(S) \,\|\, p(S \mid X) \big) - \ln p(X) \ \ge \ -\ln p(X)",
    r"Değişimsel serbest enerji $-\ln p(X)$ ile alttan sınırlıdır, "
    r"$0$ ile değil. $\mathcal{F} \ge 0$ ancak $p(X) \le 1$ iken, yani "
    r"AYRIK $X$ için doğrudur; yoğunluklarda yanlıştır. Negatif "
    r"olmayan büyüklük KL terimidir. (Ayrıca ``Viyana-Ayrışma'' diye "
    r"bir ayrışma yoktur; ıraksama Kullback--Leibler'dir.)",
    "mantik")

_t(57, "Tebliğ §1.2", "ICP kesişimi YORDAYICI KÜMELER üzerinden alınır",
    [FITRAT],
    r"\bigcap_{e \in \mathcal{E}} \text{Supp}\left( P_e(Y \mid X_{\text{Sâbit}}) \right) &= X_{\text{Hakiki\_İllet}}",
    r"S^{\star} &= \bigcap \big\{ S \subseteq \{1,\dots,p\} : P_e(Y \mid X_S) \text{ her } e \in \mathcal{E} \text{ için AYNI} \big\} \ \subseteq \ \text{PA}(Y)",
    r"Desteklerin (support) kesişimi bir SONUÇ kümesi verir; oysa aranan "
    r"bir DEĞİŞKEN kümesidir. Invariant Causal Prediction "
    r"(Peters--Bühlmann--Meinshausen), kabul edilen yordayıcı "
    r"kümelerini kesiştirir ve netice gerçek ebeveyn kümesinin ALT "
    "KÜMESİDİR -- eşitlik değil, kapsama.",
    "tip")

_t(58, "Tebliğ §2.1", "Ayrık taban üzerinde ``pürüzsüz lifli demet''",
    [FITRAT],
    r"\pi : \mathcal{S} &\longrightarrow \mathcal{N} \quad (\text{Lifli Demet})",
    r"\pi : \mathcal{S} \to \mathcal{N}, \quad \mathcal{S} &\cong \coprod_{w \in \mathcal{N}} \mathbf{Fib}_w \quad (\mathcal{N} \text{ AYRIK} \Rightarrow \text{demet} = \text{indeksli eş-çarpım})",
    r"Token uzayı $\mathcal{N}$ ayrıktır. Ayrık taban üzerindeki bir "
    r"lifli demet, liflerin ayrık birleşiminden ibarettir; "
    r"``pürüzsüzlük'' orada hiçbir şey söylemez. Pürüzsüzlük liflerin "
    r"İÇİNDE yaşar ve öyle yazılmalıdır.",
    "tip")

_t(59, "Tebliğ §2.2", "Sonsuz boyutlu lifin hacmi yoktur",
    [FITRAT],
    r"\text{ManaKapsamı}(w) &= \int_{\pi^{-1}(w)} d\text{vol}_{\mathcal{S}} = \text{TopolojikHacim}\left( \mathbf{Fib}_w \right)",
    r"\text{ManaKapsamı}(w) &= H\big[ P(S \mid w) \big] = -\int_{\pi^{-1}(w)} P(S \mid w) \log P(S \mid w) \, dS",
    r"Aynı paragraf lifi ``sonsuz boyutlu'' ilân ediyor. Sonsuz boyutlu "
    r"bir Banach uzayında öteleme değişmez, $\sigma$-sonlu ve aşikâr "
    "olmayan bir ölçü YOKTUR (Weil); dolayısıyla o integral tanımsızdır. "
    "Şartlı entropi mevcuttur ve aynı şeyi -- tek bir tokenin ne kadar "
    "mana taşıdığını -- ölçer.",
    "tanimsiz")

_t(60, "Tebliğ §2.2", "``Kayıpsız çarpım'' bir özdeşlik değil, bir HİPOTEZ",
    [FITRAT],
    r"\| \text{Mana}(w_1 w_2 \dots w_n) - \bigotimes_{k=1}^n \mathbf{Fib}_{w_k} \|_{\mathbf{H}} &= 0 \quad (\text{Kayıpsız Çarpım})",
    r"\text{Mana}(w_1 \dots w_n) &= \mu\Big( \bigotimes_{k=1}^n \mathbf{Fib}_{w_k} \Big) \oplus \varepsilon_{\text{bağlam}}, \quad \varepsilon_{\text{bağlam}} = 0 \iff \mu \text{ izomorfizma}",
    "İki kusur: (i) Tip -- sol taraf bir ÖGE, sağ taraf bir UZAY; "
    "çıkarılamazlar. (ii) Muhteva -- tam bileşimsellik (exact "
    "compositionality) bir özdeşlik değil, bileşim eşlemesi "
    r"$\mu$'nün izomorfizma olması şartıdır; deyimler ve bağlam "
    "bağımlılığı yüzünden tabiî lisanda genelde sağlanmaz. Kusur "
    "terimiyle yazılınca iddia SINANABİLİR hâle gelir.",
    "tip")

_t(61, "Tebliğ §3.2", "Zincir kuralı ile monoidallik tek denkleme sıkıştırılmış",
    [FITRAT],
    r"(g \circ f)^*(T_1 \otimes_{\mathcal{O}} T_2) &\equiv f^* T_1 \otimes_{\mathcal{O}} f^* T_2 \quad (\text{Strict Refl ile Kayıpsız Aktarım})",
    r"(g \circ f)^* &\equiv f^* \circ g^* \quad (\text{zincir kuralı}) \\" "\n"
    r"f^*(T_1 \otimes_{\mathcal{O}} T_2) &\equiv f^* T_1 \otimes_{\mathcal{O}} f^* T_2 \quad (\text{monoidallik})",
    r"Sol taraf $g \circ f$ boyunca taşıyor, sağ taraf yalnız $f$ "
    "boyunca; eşitlik olduğu gibi YANLIŞTIR. Bunlar iki AYRI kanundur "
    "ve ikisi de bu depoda TANIMSAL olarak sağlanır, yani "
    r"$\texttt{refl}$ ile ispatlanır "
    r"(\texttt{omega\_kategori}: \texttt{test\_zincir\_kurali\_tanimsal}).",
    "mantik")

_t(62, "Tebliğ §3.3", "$hLevel\\ 0$ çıktıyı bir NOKTAYA çökertir",
    [FITRAT],
    r"N_{\text{kebîr}} &= \text{Truncate}_{hLevel 0}\left( \text{Lan}_{\text{Lisan}} \left( \mathcal{R} \triangleright \bigoplus_{j=1}^k \mathcal{A}_j \right) \right)",
    r"N_{\text{kebîr}} &= \big\| \text{Lan}_{\text{Lisan}} \big( \mathcal{R} \triangleright \textstyle\bigoplus_{j=1}^k \mathcal{A}_j \big) \big\|_0 = \text{Truncate}_{hLevel\,2}(\cdots) \quad (\text{KÜME kesmesi})",
    r"Voevodsky'nin hlevel sayımında $hLevel\ 0$ BÜZÜLEBİLİRDİR: o "
    "mertebeye kesmek çıktıyı tek bir noktaya indirir ve bölümün "
    "korumaya çalıştığı bilginin tamamını yok eder. Küme kesmesi "
    r"$n$-tip gösteriminde $\|\cdot\|_0$, hlevel gösteriminde "
    r"$hLevel\ 2$'dir. Aynı belge 𝒪₂'de $hLevel\ 2$ yazıyor; iki yer "
    "çelişiyor.",
    "tip")

_t(63, "Tebliğ §3.3", "Kesme ile ``univalence mührü'' birbirini yalanlıyor",
    [FITRAT],
    r"\text{Path}_{\text{akıl}} &= \left( \bigoplus_{j=1}^k \mathcal{A}_j \; \simeq_{\text{kayıpsız}} \; N_{\text{kebîr}} \right) \in \mathbf{U} \quad (\text{Univalence Mührü})",
    r"\bigoplus_{j=1}^k \mathcal{A}_j \simeq N_{\text{kebîr}} &\iff \bigoplus_{j=1}^k \mathcal{A}_j \text{ ZATEN } 0\text{-kesik (küme)}; \ \text{aksi hâlde } N_{\text{kebîr}} \text{ bir GERİ ÇEKİMDİR}",
    r"Bir önceki satır kesme yapıyor. Kesme, kaynak zaten o mertebede "
    r"kesik DEĞİLSE bir denklik değildir: $\|\cdot\|_0$ bir "
    r"yansımadır (reflection) ve $A \to \|A\|_0$ ancak $A$ bir küme "
    "iken denkliktir. Dolayısıyla iki satır birbirini yalanlıyor. "
    r"``Kayıpsızlık'' iddiasının riyazî çekirdeği tam olarak bu şarttır "
    "ve açıkça yazılmalıdır.",
    "mantik")


# ---------------------------------------------------------------------
#  64-70: HoTT nüshasındaki aynı hataların o nüshaya mahsus yazılışları
# ---------------------------------------------------------------------
_t(64, "𝒪₅ Tecrit (HoTT)", "Grassmannian'a izdüşüm diye bir şey yoktur",
    [HOTT],
    r"\text{Proj}_{\text{Gr}(k,d_{\text{in}})}(X_t) = U_k U_k^T X_t \in \mathcal{T}_{\text{inv}}",
    r"\Pi_V(X_t) = U_k U_k^T X_t, \quad V = \text{span}(U_k) \in \text{Gr}(k, d_{\text{in}})",
    "Aynı sebep (bkz. T3).",
    "tip")

_t(65, "𝒪₆ Tasavvur (HoTT)", "Homoloji GRUBU ile ağırlık dizeyi tensörlenemez",
    [HOTT],
    r"H_p\left( \mathcal{S}_{[1:t]} \right) \otimes_{\mathcal{O}} W_{\text{macro}}",
    r"H_p\left( \mathcal{S}_{[1:t]}; \mathbb{R} \right) \otimes_{\mathcal{O}} W_{\text{macro}}",
    "Aynı sebep (bkz. T10).",
    "tip")

_t(66, "𝒪₃₃ Muhakeme (HoTT)", "Skaler integrale vektör eklenmiş",
    [HOTT],
    r"\rangle_{\mathbf{H}} + \beta \dot{I}_t - \gamma \text{Tenakuz}(S_t) \Big] dt",
    r"\rangle_{\mathbf{H}} + \beta \|\dot{I}_t\| - \gamma \text{Tenakuz}(S_t) \Big] dt",
    "Aynı sebep (bkz. T14).",
    "boyut")

_t(67, "𝒪₁₀ Tezat (HoTT)", "Zıtlık operatörü involüsyon değil; ayrıca çifte eşlenik",
    [HOTT],
    r"\mathbf{W}_{\text{opp}} &= -I_{d \times d} + \mathbf{v}_{\text{zıt}} \otimes \mathbf{v}_{\text{zıt}}^T",
    r"\mathbf{W}_{\text{opp}} &= 2\hat{\mathbf{v}}_{\text{zıt}} \hat{\mathbf{v}}_{\text{zıt}}^T - I_{d \times d}, \quad \|\hat{\mathbf{v}}_{\text{zıt}}\| = 1 \ \Rightarrow \ \mathbf{W}_{\text{opp}}^2 = I",
    "T19'daki involüsyon kusuruna ek olarak burada dış çarpım "
    "$\\mathbf{v} \\otimes \\mathbf{v}^T$ diye yazılmış. Bu çifte "
    "eşleniktir (bir vektörle bir eş-vektörün tensörü); doğrusu ya "
    "$\\mathbf{v}\\mathbf{v}^T$ ya $\\mathbf{v} \\otimes \\mathbf{v}$'dir. "
    "Aynı karışıklık 𝒪₄, 𝒪₁₄, 𝒪₁₇ ve 𝒪₁₈'de de tekrarlanıyor.",
    "tip")

_t(68, "𝒪₃₀ Tahkik (HoTT)", "Aynı erişilemez eşik kusuru",
    [HOTT],
    r"T_{\text{tahkik}} &= \sigma\left( \text{CosSim}_{\mathbf{H}}(S_{\text{tahkik}}, S_{\text{asıl}}) \right)",
    r"T_{\text{tahkik}} &= \sigma\left( \beta_T \left[ \text{CosSim}_{\mathbf{H}}(S_{\text{tahkik}}, S_{\text{asıl}}) - \theta \right] \right), \quad \beta_T \ge 4",
    "Aynı sebep (bkz. T23, T24).",
    "erisilmez")

_t(69, "𝒪₂₇ Tetkik (HoTT)", "Skalerin LayerNorm'u tanımsız",
    [HOTT],
    r"\text{Skor}_{\text{tetkik}} &= \text{LayerNorm}\left( \sum \text{KusurHaritası} \right)",
    r"\text{Skor}_{\text{tetkik}} &= \text{LayerNorm}\Big( \textstyle\sum_{i} \text{KusurHaritası}_{i\cdot} \Big) \in \mathbb{R}^{d_{\text{sem}}}",
    "Aynı sebep (bkz. T39).",
    "tanimsiz")

_t(70, "𝒪₂₇ Tetkik (HoTT)", "Tensör çarpımı yerine Hadamard çarpımı",
    [HOTT],
    r"|\delta S_{t, \text{kılcal}} - S_{\text{ideal}}| \otimes_{\mathcal{O}} W_{\text{tetkik}}",
    r"|\delta S_{t, \text{kılcal}} - S_{\text{ideal}}| \odot W_{\text{tetkik}}",
    "Aynı sebep (bkz. T40).",
    "tip")

# =====================================================================
#  71-...: Mantık külliyatı ve mimari risaleleri
# =====================================================================

# --- A. DERLEMEYİ KIRAN yapı hataları ------------------------------
_t(71, "Münazara §1.3 (Mîzân)", "Ortam kapanışı bozuk: derleme KIRILIYOR",
    [MIZAN],
    "\\end{align\">",
    "\\end{align}",
    "``\\end{align\\\"}'' diye kapanmış; LaTeX bunu ortam kapanışı saymaz ve "
    "belge derlenmez. Yapı denetleyicisi (\\texttt{tex\\_denetle.py}) bunu "
    "``\\begin{align} (satır 323) ile \\end{document} uyuşmuyor'' diye "
    "yakaladı. Bu, muhtevaya dair bir tashih değil; belgenin derlenmesinin "
    "ön şartıdır.",
    "yapi")

_t(72, "Relevans §1 (Zeyl)", "Ortam kapanışı bozuk: derleme KIRILIYOR",
    [ZEYL],
    "(\\text{Değişme})\n\\end{align\">",
    "(\\text{Değişme})\n\\end{align}",
    "Aynı kusur (bkz. T71).",
    "yapi")

_t(73, "Doğrusal Mantık §1.2 (Zeyl)", "Ortam kapanışı bozuk: derleme KIRILIYOR",
    [ZEYL],
    "tüketilip B elde edilir})\n\\end{align\">",
    "tüketilip B elde edilir})\n\\end{align}",
    "Aynı kusur (bkz. T71).",
    "yapi")

_t(74, "Kıyas-ı İstisnasî (Mîzân)", "Markdown başlığı LaTeX'e sızmış",
    [MIZAN],
    r"\## 1. Bitişik Şartlı Kıyaslar (Muttasıla)",
    r"\subsection{1. Bitişik Şartlı Kıyaslar (Muttasıla)}",
    r"``\\##'' LaTeX'te başlık değildir: ``\\#'' kaçırılmış diyez, ardından "
    r"gelen ``#'' ise metin kipinde parametre karakteridir ve hata verir. "
    r"Ayrıca altındaki \texttt{subsubsection}'lar sahipsiz kalır.",
    "yapi")

_t(75, "Modal Mantık (Mîzân)", "Markdown başlığı LaTeX'e sızmış",
    [MIZAN],
    r"\## 1. Modal Mantık (Kiplik Mantığı - Zorumluluk ve İmkân)",
    r"\subsection{1. Modal Mantık (Kiplik Mantığı --- Zorunluluk ve İmkân)}",
    r"Aynı kusur (bkz. T74). Ayrıca ``Zorumluluk'' $\to$ ``Zorunluluk''.",
    "yapi")

_t(76, "Sezgisellik (Zeyl)", "Markdown başlığı LaTeX'e sızmış",
    [ZEYL],
    r"\## 1. BHK (Brouwer-Heyting-Kolmogorov) İnşacı Semantigi",
    r"\subsection{1. BHK (Brouwer--Heyting--Kolmogorov) İnşacı Semantiği}",
    r"Aynı kusur (bkz. T74). Ayrıca ``Semantigi'' $\to$ ``Semantiği''.",
    "yapi")

# --- B. Klasik mantık: varlık faraziyesi --------------------------
_t(77, "Darapti (Mîzân)", "VARLIK FARAZİYESİ eksik: kıyas geçersiz",
    [MIZAN, GENIS],
    r"P_2 &: \forall x (M(x) \implies S(x)) \quad (\text{Her M, S'dir}) \\"
    "\n" r"\mathcal{Q}_{\text{Darapti}} &: \exists x (S(x) \land P(x)) \quad (\text{Bazı S'ler P'dir})",
    r"P_2 &: \forall x (M(x) \implies S(x)) \quad (\text{Her M, S'dir}) \\"
    "\n" r"P_3 &: \exists x \, M(x) \quad (\text{VARLIK FARAZİYESİ --- M boş değildir}) \\"
    "\n" r"\mathcal{Q}_{\text{Darapti}} &: \exists x (S(x) \land P(x)) \quad (\text{Bazı S'ler P'dir})",
    r"İki tümel öncülden tikel netice çıkarılıyor. $M$ BOŞ ise iki öncül de "
    r"boşluktan doğrudur, netice ise yanlıştır --- yani kıyas yazıldığı "
    r"hâliyle GEÇERSİZDİR (klasik adıyla ``varlık safsatası''). Aristo "
    r"terimlerin boş olmadığını zımnen kabul eder; modern yüklem mantığında "
    r"bu kabul YAZILMAK zorundadır.",
    "mantik")

_t(78, "Felapton (Mîzân)", "VARLIK FARAZİYESİ eksik: kıyas geçersiz",
    [MIZAN, GENIS],
    r"P_2 &: \forall x (M(x) \implies S(x)) \quad (\text{Her M, S'dir}) \\"
    "\n" r"\mathcal{Q}_{\text{Felapton}} &: \exists x (S(x) \land \neg P(x))",
    r"P_2 &: \forall x (M(x) \implies S(x)) \quad (\text{Her M, S'dir}) \\"
    "\n" r"P_3 &: \exists x \, M(x) \quad (\text{VARLIK FARAZİYESİ}) \\"
    "\n" r"\mathcal{Q}_{\text{Felapton}} &: \exists x (S(x) \land \neg P(x))",
    "Aynı sebep (bkz. T77).",
    "mantik")

_t(79, "Bamalip (Mîzân)", "VARLIK FARAZİYESİ eksik: kıyas geçersiz",
    [MIZAN, GENIS],
    r"P_2 &: \forall x (M(x) \implies S(x)) \quad (\text{Her M, S'dir}) \\"
    "\n" r"\mathcal{Q}_{\text{Bamalip}} &: \exists x (S(x) \land P(x))",
    r"P_2 &: \forall x (M(x) \implies S(x)) \quad (\text{Her M, S'dir}) \\"
    "\n" r"P_3 &: \exists x \, P(x) \quad (\text{VARLIK FARAZİYESİ --- burada P boş değildir}) \\"
    "\n" r"\mathcal{Q}_{\text{Bamalip}} &: \exists x (S(x) \land P(x))",
    r"Aynı sebep (bkz. T77); fakat dördüncü şekilde boş olmaması gereken "
    r"terim $M$ değil BÜYÜK TERİM $P$'dir. Öncüller $P \subseteq M \subseteq "
    r"S$ verir; netice $\exists x (S \land P)$ ancak $P$ boş değilse çıkar.",
    "mantik")

_t(80, "Fesapo (Mîzân)", "VARLIK FARAZİYESİ eksik: kıyas geçersiz",
    [MIZAN, GENIS],
    r"P_2 &: \forall x (M(x) \implies S(x)) \quad (\text{Her M, S'dir}) \\"
    "\n" r"\mathcal{Q}_{\text{Fesapo}} &: \exists x (S(x) \land \neg P(x))",
    r"P_2 &: \forall x (M(x) \implies S(x)) \quad (\text{Her M, S'dir}) \\"
    "\n" r"P_3 &: \exists x \, M(x) \quad (\text{VARLIK FARAZİYESİ}) \\"
    "\n" r"\mathcal{Q}_{\text{Fesapo}} &: \exists x (S(x) \land \neg P(x))",
    "Aynı sebep (bkz. T77).",
    "mantik")

_t(81, "Aks-i Müstevî (Mîzân)", "Arazî çevirme de varlık faraziyesi ister",
    [MIZAN],
    r"\text{Aks}(\forall x (S(x) \implies P(x))) &\implies \exists x (P(x) \land S(x)) \quad (\text{Mûcebe-i Külliyye'nin aksi Mûcebe-i Cüz'iyyedir})",
    r"\text{Aks}(\forall x (S(x) \implies P(x))) \land \exists x \, S(x) &\implies \exists x (P(x) \land S(x)) \quad (\text{arazî çevirme; } S \ne \emptyset \text{ ŞARTIYLA})",
    r"``Aks-i müstevî bi'l-araz'' tümelden tikele iner; $S$ boşsa öncül "
    r"boşluktan doğru, netice yanlıştır. Aynı belgede Darapti/Felapton/"
    r"Bamalip/Fesapo'da düşen şart budur (bkz. T77-T80).",
    "mantik")

# --- C. Klasik mantık: diğer ---------------------------------------
_t(82, "İstikra-i Nâkıs (Mîzân)", "Formül ``en az biri'' olasılığı; tümevarım güveni değil",
    [MIZAN, GENIS],
    r"P\left( \forall x \in K, P(x) \right) = 1 - \prod_{i=1}^k (1 - p_i)",
    r"P\left( \forall x \in K, P(x) \mid k \text{ doğrulayıcı örnek} \right) = \frac{k+1}{N+1}, \quad N = |K| \quad (\text{Laplace})",
    r"$1 - \prod(1-p_i)$, bağımsız olayların EN AZ BİRİNİN gerçekleşme "
    r"olasılığıdır; tümel bir genellemeye duyulan güven değildir. Üstelik "
    r"$k \to \infty$ iken her $p_i$ ne kadar küçük olursa olsun $1$'e gider "
    r"--- yani ``çok örnek gördüm, öyleyse kesindir'' safsatasını FORMÜLE "
    r"eder. Doğru hâli Laplace'ın ardıllık hesabıdır: $N$ elemanlı bir "
    r"kümede $k$ doğrulayıcı örnekten sonra istisnasızlık olasılığı "
    r"$(k+1)/(N+1)$'dir ve ancak $k = N$ iken $1$ olur. Bu, belgenin kendi "
    r"``istikra-i tâmm kesindir, nâkıs değildir'' ayrımını riyazî olarak "
    r"görünür kılar.",
    "mantik")

_t(83, "Burhan (Mîzân)", "Öncüllerin doğruluğu tek başına neticeyi kesinleştirmez",
    [MIZAN],
    r"\text{Sıhhat}(P_i) &= 1.0 \implies \text{Sıhhat}(\mathcal{Q}_{\text{Burhan}}) = 1.0 \quad (\text{Yakînî Netice})",
    r"\text{Sıhhat}(\mathcal{Q}_{\text{Burhan}}) &= \min_i \text{Sıhhat}(P_i) \times \mathbb{I}(\text{Şekil Geçerli}) \quad (\text{Yakîn ancak GEÇERLİ şekilde intikal eder})",
    r"Doğru öncüller GEÇERSİZ bir şekilde dizilirse netice yakînî olmaz. "
    r"Şekil geçerliliği çarpanı düşürülünce ``burhan'' tarifi, muğalatayı "
    r"da içine alır. Nitekim aynı külliyatın zeyl risalesinde Gazâlî'nin "
    r"mîzânı bu çarpanla DOĞRU yazılmış; iki metin birbiriyle çelişiyordu.",
    "mantik")

_t(84, "Hitabet (Mîzân)", "Zannî öncüllerden zannî netice KENDİLİĞİNDEN çıkmaz",
    [MIZAN],
    r"P_i &\in \text{Maznûnât} \implies P(\mathcal{Q}_{\text{Hitabet}}) > 0.5 \quad (\text{Zannî İkna})",
    r"P_i \in \text{Maznûnât} &\implies P(\mathcal{Q}_{\text{Hitabet}}) \ge 1 - \sum_i \left( 1 - P(P_i) \right) \quad (\text{Adams sınırı})",
    r"$k$ öncülün her biri $0{,}6$ olsa bile neticenin olasılığı $0{,}5$'in "
    r"çok altına düşebilir; belirsizlikler TOPLANIR. Doğru ifade Adams'ın "
    r"olasılıksal modus ponens sınırıdır --- ki aynı külliyatın zeyl "
    r"risalesinde zaten doğru yazılmış: "
    r"$\text{Belirsizlik}(B) \le \text{Belirsizlik}(A) + "
    r"\text{Belirsizlik}(A \implies B)$.",
    "mantik")

_t(85, "Modal aksiyomlar (Genişletilmiş)", "``5'' diye yazılan aksiyom aslında B'dir",
    [GENIS],
    r"\mathbf{5} : \alpha \implies \Box \Diamond \alpha",
    r"\mathbf{5} : \Diamond \alpha \implies \Box \Diamond \alpha, \quad \mathbf{B} : \alpha \implies \Box \Diamond \alpha",
    r"$\alpha \implies \Box\Diamond\alpha$ Brouwersche aksiyomu ($\mathbf{B}$, "
    r"simetrik $R$) iken $\mathbf{5}$ (Öklidyen $R$) "
    r"$\Diamond\alpha \implies \Box\Diamond\alpha$'dır. İkisi farklı "
    r"çerçeve şartlarına karşılık gelir. Aynı külliyatın ana nüshasında "
    r"$\mathbf{5}$ DOĞRU yazılmış; iki metin çelişiyordu.",
    "mantik")

_t(86, "Deontik/Temporal (Mîzân)", "``P'' aynı sayfada ÜÇ ayrı şey",
    [MIZAN],
    r"O P \quad (\text{P ödevdir / mecburdur}), \quad P P \quad (\text{P caizdir / izinlidir}), \quad F P \quad (\text{P memnudur / yasaktır}) \\"
    "\n" r"P P &\equiv \neg O \neg P \\"
    "\n" r"F P &\equiv O \neg P \\",
    r"\mathrm{O}\varphi \ (\text{ödev}), \quad \mathrm{Pm}\,\varphi \ (\text{caiz}), \quad \mathrm{F}\varphi \ (\text{yasak}) \\"
    "\n" r"\mathrm{Pm}\,\varphi &\equiv \neg \mathrm{O} \neg \varphi \\"
    "\n" r"\mathrm{F}\varphi &\equiv \mathrm{O} \neg \varphi \\",
    r"``$P$'' bu iki alt bölümde (i) önerme değişkeni, (ii) deontik "
    r"``caiz'' işlemcisi ve (iii) temporal ``geçmişte bir an'' işlemcisi "
    r"olarak kullanılıyor. ``$PP$'' ifadesi bu yüzden okunamaz. Önerme "
    r"değişkeni $\varphi$'ye, deontik izin $\mathrm{Pm}$'ye alındı.",
    "tanimsiz")

_t(87, "Temporal (Mîzân)", "``$HP \\equiv \\neg P \\neg P$'' okunamaz",
    [MIZAN],
    r"G P \quad (\text{Gelecekte daima P}), \quad F P \quad (\text{Gelecekte bir zaman P}) \\"
    "\n" r"H P \quad (\text{Geçmişte daima P}), \quad P P \quad (\text{Geçmişte bir zaman P}) \\"
    "\n" r"G P &\equiv \neg F \neg P \\"
    "\n" r"H P &\equiv \neg P \neg P \\",
    r"\mathrm{G}\varphi, \ \mathrm{F}\varphi \ (\text{gelecekte daima / bir an}), \quad \mathrm{H}\varphi, \ \mathsf{P}\varphi \ (\text{geçmişte daima / bir an}) \\"
    "\n" r"\mathrm{G}\varphi &\equiv \neg \mathrm{F} \neg \varphi \\"
    "\n" r"\mathrm{H}\varphi &\equiv \neg \mathsf{P} \neg \varphi \\",
    r"T86'daki çakışmanın doğrudan neticesi: ``$\neg P \neg P$'' üç ayrı "
    r"``$P$''nin yan yana gelmesidir ve ayrıştırılamaz. Geçmiş-imkân "
    r"işlemcisi $\mathsf{P}$'ye alınınca kural okunur hâle gelir.",
    "tanimsiz")

_t(88, "Until (Mîzân)", "Alt sınırsız ``until'' sonsuz geçmişi de kapsar",
    [MIZAN],
    r"P \, \mathbf{U} \, Q &\iff \exists t (Q(t) \land \forall t' < t, P(t')) \quad (\text{Until / -e Kadar Operatörü})",
    r"\varphi \, \mathbf{U} \, \psi &\iff \exists t \ge t_0 \, \big( \psi(t) \land \forall t' \in [t_0, t), \, \varphi(t') \big) \quad (t_0: \text{şimdiki an})",
    r"$\forall t' < t$ alt sınırsızdır; sonsuz geçmişte de $P$'nin "
    r"sağlanmasını ister. ``-e kadar'' ŞİMDİDEN başlar.",
    "tanimsiz")

_t(89, "Łukasiewicz (Mîzân)", "Gerektirme ile bağlaçlar birbirinin eşleniği değil",
    [MIZAN],
    r"v(P \land Q) &= \min(v(P), v(Q)) \\"
    "\n" r"v(P \lor Q) &= \max(v(P), v(Q)) \\",
    r"v(P \otimes Q) &= \max(0, v(P) + v(Q) - 1) \quad (\text{KUVVETLİ ve; } \to \text{'nin eşleniği}) \\"
    "\n" r"v(P \land Q) = \min(v(P), v(Q)), &\quad v(P \lor Q) = \max(v(P), v(Q)) \quad (\text{zayıf/kafes bağlaçları}) \\",
    r"$v(P \to Q) = \min(1, 1-v(P)+v(Q))$ Łukasiewicz T-normunun "
    r"KALINTISIDIR (residuum). Kalıntı bağıntısı "
    r"$v(A \otimes B) \le v(C) \iff v(A) \le v(B \to C)$ ancak $\otimes$ "
    r"kuvvetli ``ve'' iken sağlanır; $\min$ ile SAĞLANMAZ. Yazıldığı hâliyle "
    r"gerektirme ile bağlaçlar aynı cebre ait değildir. Zayıf bağlaçlar da "
    r"Łukasiewicz'de vardır, fakat eşlenik olan onlar değildir.",
    "mantik")

_t(90, "Product mantığı (Mîzân)", "$v(P)=0$'da tanımsız",
    [MIZAN],
    r"v(P \implies Q) &= \min\left(1, \frac{v(Q)}{v(P)}\right)",
    r"v(P \implies Q) &= \begin{cases} 1, & v(P) \le v(Q) \\ v(Q)/v(P), & v(P) > v(Q) \end{cases} \quad (v(P) = 0 \Rightarrow 1)",
    r"$v(P) = 0$ iken bölme tanımsızdır; oysa çarpım mantığında "
    r"$0 \to Q$ doğrudur ($=1$). Kalıntı biçiminde yazılınca hem tanım "
    r"kümesi tamamlanır hem $\min$ gereksizleşir.",
    "tanimsiz")

_t(91, "Stoacı 4. usul (Zeyl)", "Usul yanlış adlandırılmış",
    [ZEYL],
    r"\subsection{4. Dördüncü Kanıtlanamaz Usul (Modus Tollendo Ponens I)}",
    r"\subsection{4. Dördüncü Kanıtlanamaz Usul (Modus Ponendo Tollens II)}",
    r"Dördüncü usul ``$P \veebar Q$, $P$; öyleyse $\neg Q$''dur: bir tarafı "
    r"KOYARAK öbürünü KALDIRIR, yani \textit{ponendo tollens}. "
    r"\textit{Tollendo ponens} ise kaldırarak koyar --- o da beşinci "
    r"usuldür ve orada doğru adlandırılmış.",
    "mantik")

_t(92, "Heyting cebri (Zeyl)", "Meta-``ve'' ile kafes ``$\\wedge$''i karışmış; ad yanlış",
    [ZEYL],
    r"A \le B \land A \le C \implies A \le B \land C \qquad &(\text{Ekok})",
    r"(A \le B) \ \text{ve} \ (A \le C) \iff A \le B \land C \qquad &(\text{en büyük alt sınırın evrensel hususiyeti})",
    r"Soldaki ``$\land$'' meta-seviyede ``ve'', sağdaki ise kafes "
    r"buluşmasıdır; aynı simge iki ayrı seviyede kullanılınca ifade "
    r"ayrıştırılamaz. Ayrıca bağıntı tek yönlü değil, ÇİFT yönlüdür --- "
    r"buluşmayı tanımlayan evrensel hususiyet budur. ``Ekok'' (en küçük "
    r"ortak kat) ise alâkasız bir addır; burada söz konusu olan en büyük "
    r"ALT sınırdır.",
    "mantik")

_t(93, "Kuantum mantık (Zeyl)", "Dağılma her zaman BOZULMAZ; genel bağıntı bir eşitsizliktir",
    [ZEYL],
    r"A \land (B \lor C) &\neq (A \land B) \lor (A \land C) \quad (\text{Dağılma Geçersizdir})",
    r"(A \land B) \lor (A \land C) &\le A \land (B \lor C) \quad (\text{dâima}); \quad \text{eşitlik GEREKMEZ (dağılma geçersiz)}",
    r"``$\neq$'' yazmak ``her zaman eşit değildir'' demektir; oysa uyumlu "
    r"(commuting) alt uzaylarda eşitlik SAĞLANIR. Ortolatislerde her zaman "
    r"geçerli olan bağıntı yukarıdaki eşitsizliktir; kuantum mantığını "
    r"klasikten ayıran şey, ters yönün genelde sağlanmamasıdır.",
    "mantik")

_t(94, "Dombi T-normu (Zeyl)", "$a=0$ yahut $b=0$'da tanımsız",
    [ZEYL],
    r"T_{D}(a, b; p) = \frac{1}{1 + \left( \left(\frac{1-a}{a}\right)^p + \left(\frac{1-b}{b}\right)^p \right)^{1/p}}, \quad p > 0",
    r"T_{D}(a, b; p) = \begin{cases} 0, & a = 0 \ \text{yahut} \ b = 0 \\ \dfrac{1}{1 + \left( \left(\frac{1-a}{a}\right)^p + \left(\frac{1-b}{b}\right)^p \right)^{1/p}}, & \text{aksi hâlde} \end{cases}, \quad p > 0",
    r"$a = 0$'da $(1-a)/a$ tanımsızdır. T-norm olabilmesi için "
    r"$T(0,b) = 0$ şartı zaten gereklidir; sınır hâli açıkça yazılmalıdır.",
    "tanimsiz")

_t(95, "Schweizer--Sklar (Zeyl)", "Verilen biçim yalnız $p>0$ için doğru",
    [ZEYL],
    r"T_{SS}(a, b; p) = \left( \max(0, a^p + b^p - 1) \right)^{1/p}, \quad p \neq 0",
    r"T_{SS}(a, b; p) = \left( \max(0, a^p + b^p - 1) \right)^{1/p}, \quad p > 0 \qquad \left( p < 0: \ (a^p + b^p - 1)^{1/p} \right)",
    r"$p < 0$ iken $a^p + b^p - 1 > 0$ dâima sağlanır ve $\max(0,\cdot)$ "
    r"gereksizleşir; dahası $1/p < 0$ olduğundan kesme yanlış dala "
    r"yönlendirir. Ailenin negatif kolu ayrı yazılır.",
    "tanimsiz")

_t(96, "Adams (Zeyl)", "$P(A) = 0$'da şartlı olasılık tanımsız",
    [ZEYL],
    r"P(A \implies B) &\coloneqq P(B \mid A) = \frac{P(A \land B)}{P(A)} \quad (\text{Adams Şartlı Olasılık Kuralı})",
    r"P(A \implies B) &\coloneqq P(B \mid A) = \frac{P(A \land B)}{P(A)}, \quad P(A) > 0 \quad (\text{Adams tezi})",
    r"Adams tezi ancak öncül olumlu olasılıklıyken kurulur; $P(A) = 0$ "
    r"hâlinde şartlı olasılık tanımsızdır ve bir sonraki satırdaki "
    r"belirsizlik sınırı da düşer.",
    "tanimsiz")

# --- D. Mimari risaleleri ------------------------------------------
_t(97, "Token Uzayları §Glue", "SAĞLAMLIK HATASI: hcomp $u_0$'a indirgenmez",
    [TOKEN],
    r"\text{hcomp}^i \, \mathcal{X}_{w_k} \, [\dots] \, u_0 &\longrightarrow u_0 \quad (\text{Ayrık Lif İç Dolgu İndirgemesi})",
    r"\text{hcomp}^i \, \mathcal{X}_{w_k} \, [\varphi \mapsto u] \, u_0 &\equiv u(1) \ \text{ on } \varphi; \quad \varphi = \bot \Rightarrow \equiv u_0 \quad (\text{SINIR şartı})",
    r"Bu kural SAĞLAM DEĞİLDİR ve depoda makineyle çürütüldü. "
    r"$\text{hcomp}$'un tarifi gereği $\varphi$ üzerinde $u$'ya eşit olması "
    r"gerekir; $u_0$'a indirgemek tam olarak o sınır şartını kırar. "
    r"\texttt{omega\_kategori} çekirdeğinde bu kural bir ara kurulmuştu ve "
    r"neticeleri ölçüldü: \texttt{isoToEquiv}'in kare inşası bozuldu "
    r"($\texttt{fill0 1 1}$ $x_0$ yerine $g(f\,x_0)$ verdi) ve $\mathbb{Z}$ "
    r"üzerindeki bütün dolgular çöktü. Kaldırıldı; yerine kurucuya iten "
    r"YAPISAL kural konuldu. Metinde ``ayrık lif'' gerekçesi de tutmaz: "
    r"liflerin ayrıklığı $\varphi$ boş olmadıkça dolguyu tabana indirmez.",
    "sağlamlık")

_t(98, "Token Uzayları §Kan", "Bitişiklik üçlüsünde $F$ fazladan",
    [TOKEN],
    r"\text{Lan}_{f_{i,j}} F &\dashv f_{i,j}^* \dashv \text{Ran}_{f_{i,j}} F \quad (\text{Üçlü Bitişiklik / Adjoint Triple})",
    r"\text{Lan}_{f_{i,j}} &\dashv f_{i,j}^* \dashv \text{Ran}_{f_{i,j}} \quad (\text{funktorlar arası üçlü bitişiklik})",
    r"Bitişiklik FUNKTORLAR arasındadır, funktorun bir değerdeki çıktısı "
    r"arasında değil. $\text{Lan}_f F$ bir funktor değil, bir nesnedir; "
    r"$\dashv$'in solunda duramaz.",
    "tip")

_t(99, "Token Uzayları §Kan", "Birim ile eş-birim bu sırayla bileşemez",
    [TOKEN],
    r"\text{Coeff}_{\text{Kan}} &= \text{Tr}(\eta_{\text{unit}} \circ \varepsilon_{\text{counit}})",
    r"(\varepsilon \ast \text{Lan}_f) \cdot (\text{Lan}_f \ast \eta) &= \mathrm{id}_{\text{Lan}_f}, \quad (f^* \ast \varepsilon) \cdot (\eta \ast f^*) = \mathrm{id}_{f^*} \quad (\text{üçgen özdeşlikleri})",
    r"$\eta : \mathrm{id} \Rightarrow f^* \circ \text{Lan}_f$ ile "
    r"$\varepsilon : \text{Lan}_f \circ f^* \Rightarrow \mathrm{id}$ "
    r"doğrudan bileşemez: birinin hedefi öbürünün kaynağı değildir. "
    r"Bitişikliği karakterize eden bağıntılar ÜÇGEN ÖZDEŞLİKLERİDİR ve "
    r"yatay ($\ast$) ile dikey ($\cdot$) bileşimi ayırarak yazılır. Bir de "
    r"``$\text{Tr}$'' burada tanımsızdır; iz bir doğal dönüşümün değil, "
    r"bir endomorfizmanın niteliğidir.",
    "tip")

_t(100, "Token Uzayları §1-Morfizm", "Tek yanlı ters denklik vermez",
    [TOKEN],
    r"\text{Diffeo}(\mathcal{X}_{w_i} \simeq \mathcal{X}_{w_j}) &\iff \exists f_{i,j}, f_{j,i} \quad \text{öyle ki } f_{j,i} \circ f_{i,j} \simeq \text{id}",
    r"\text{Diffeo}(\mathcal{X}_{w_i} \simeq \mathcal{X}_{w_j}) &\iff \exists f_{i,j}, f_{j,i}: \ f_{j,i} \circ f_{i,j} \simeq \mathrm{id}_{\mathcal{X}_{w_i}} \ \textbf{ve} \ f_{i,j} \circ f_{j,i} \simeq \mathrm{id}_{\mathcal{X}_{w_j}}",
    r"Yalnız bir bileşke birime homotop ise $f_{i,j}$ ancak bir "
    r"BÖLÜMLENMİŞ monomorfizmadır (section/retract); denklik değildir. "
    r"Denklik iki yanlı tersi ister.",
    "mantik")

_t(101, "Token Uzayları §Glue", "Lif hacminin çarpım olması TRİVİALLİK ister",
    [TOKEN],
    r"\text{Vol}(\mathbf{Fib}_{\text{cümle}}) &= \int_{\mathcal{S}_{\text{cümle}}} d\text{vol}_{\text{cümle}} = \prod_{k=1}^N \text{Vol}(\mathbf{Fib}_{w_k})",
    r"\mathcal{S}_{\text{cümle}} \cong \textstyle\prod_k \mathbf{Fib}_{w_k} \ (\text{TRİVİAL demet}) \ &\Rightarrow \ \text{Vol}(\mathbf{Fib}_{\text{cümle}}) = \prod_{k=1}^N \text{Vol}(\mathbf{Fib}_{w_k})",
    r"Hacmin çarpım olması, demetin çarpım demeti (trivial) olmasına "
    r"bağlıdır. Oysa aynı bölüm cümleyi $\text{glue}$ ile, yani "
    r"AŞİKÂR OLMAYAN bir yapıştırmayla kuruyor; bükülü bir demette lif "
    r"hacimleri çarpılmaz. İki satır birbiriyle çelişiyor. Şart açıkça "
    r"yazılınca iddia geçerli hâle gelir.",
    "mantik")

_t(102, "Sorgu Uzayı §2", "Liouville akışı hacmi KORUR; burada değişiyor",
    [SORGU, NORON],
    r"\frac{d}{dt} \text{Vol}(L_S(\mathcal{X}_{\text{şüphe}})) &= -\int_{L_S(\mathcal{X})} \left( \Delta \mathcal{F}_{\text{iç}} + \|\nabla \mathcal{F}_{\text{iç}}\|^2 \right) d\text{vol}_g \quad (\text{Liouville Akışı})",
    r"\frac{d}{dt} \text{Vol}(L_S(\mathcal{X}_{\text{şüphe}})) &= -\int_{L_S(\mathcal{X})} \Delta \mathcal{F}_{\text{iç}} \, d\text{vol}_g \quad (\text{GRADYAN akışı; Liouville DEĞİL})",
    r"İki kusur. (i) \textbf{Ad}: Liouville teoremi Hamilton akışının hacmi "
    r"KORUDUĞUNU söyler ($\mathrm{div}\, X_{\mathcal{H}} = 0$, "
    r"$d\text{Vol}/dt = 0$) --- nitekim aynı yazarın mantık nöronları "
    r"risalesi bunu doğru yazıyor. Hacmi değiştiren bir akışa Liouville "
    r"denemez. (ii) \textbf{Formül}: hız alanı $v = -\nabla\mathcal{F}$ olan "
    r"bir akışta hacmin türevi $\int \mathrm{div}(v) = -\int \Delta"
    r"\mathcal{F}$'dir; $\|\nabla\mathcal{F}\|^2$ terimi buradan gelmez "
    r"(o, ağırlıklı hacim $\int e^{-\mathcal{F}}$ alınırsa doğar ve o "
    r"zaman da işareti ARTIDIR).",
    "isaret")

_t(103, "Sorgu Uzayı §2", "Hacmi sonsuza giden uzay çürütülmüş değil, ASKIDADIR",
    [SORGU],
    r"\text{Bâtıl / Cerh (Uzay Yırtılması)}, & \mathcal{R}_{\text{karantina\_büzülme}} \to \infty \\"
    "\n" r"\text{Tahkik / Tasdik (Noktaya Büzülme)}, & \mathcal{R}_{\text{karantina\_büzülme}} \to 0 \\"
    "\n" r"\text{Askıda (Şüphe Uzayı Kalıcı)}, & \text{Diğer}",
    r"\text{Tahkik / Tasdik (noktaya büzülme)}, & \mathcal{R}_{\text{karantina\_büzülme}} \to 0 \\"
    "\n" r"\text{Bâtıl / Cerh}, & \Delta_{\text{tenakuz}} > \tau_{\text{fıtrat}} \ \text{ hâlâ} \ (t = \tau_{\text{teemmül}}) \\"
    "\n" r"\text{Askıda}, & \text{aksi hâlde (hacim büyüyor yahut sabit)}",
    r"``Büzülme'' adı taşıyan bir büyüklüğün sonsuza gitmesi zaten çelişkili; "
    r"asıl kusur ise mânâdadır: şüphe uzayının hacminin BÜYÜMESİ, o bilginin "
    r"çürütüldüğü değil, belirsizliğin arttığı anlamına gelir --- yani tam "
    r"olarak ``askıda''dır. Cerh, hacim ölçüsünden değil, tenakuzun eşiğin "
    r"üstünde KALMASINDAN çıkar. Yazıldığı hâliyle üçüncü dal da fiilen boş "
    r"kalıyordu.",
    "mantik")

_t(104, "Sorgu Uzayı §Kesme", "$hLevel\,0$ çıktıyı bir noktaya çökertir",
    [SORGU],
    r"N_{\text{kebîr}} &= \text{Truncate}_{hLevel 0}\left( \text{Lan}_{\text{Lisan}} \left( \mathcal{R} \triangleright \mathcal{S}_{\text{yeni}} \right) \right) \in \mathcal{N}",
    r"N_{\text{kebîr}} &= \big\| \text{Lan}_{\text{Lisan}} \big( \mathcal{R} \triangleright \mathcal{S}_{\text{yeni}} \big) \big\|_0 = \text{Truncate}_{hLevel\,2}(\cdots) \in \mathcal{N} \quad (\text{KÜME kesmesi})",
    r"Bu külliyatın kendi kullandığı hlevel sayımında (mantık nöronları "
    r"risalesi, \S2.1) $hLevel\,0$ BÜZÜLEBİLİR, $hLevel\,1$ önerme, "
    r"$hLevel\,2$ kümedir. O hâlde $hLevel\,0$'a kesmek çıktıyı tek bir "
    r"noktaya indirir ve korunmaya çalışılan bilginin TAMAMINI yok eder. "
    r"$n$-tip gösteriminde küme kesmesi $\|\cdot\|_0$, hlevel gösteriminde "
    r"$hLevel\,2$'dir.",
    "tip")

_t(105, "Token Uzayları §Glue", "$hLevel\,0$ çıktıyı bir noktaya çökertir",
    [TOKEN],
    r"N_{\text{kebîr}} &= \text{Truncate}_{hLevel 0}\left( \text{Lan}_{\text{Lisan}} \left( \mathcal{R} \triangleright \mathcal{S}_{\text{cümle}} \right) \right) \in \mathcal{N}",
    r"N_{\text{kebîr}} &= \big\| \text{Lan}_{\text{Lisan}} \big( \mathcal{R} \triangleright \mathcal{S}_{\text{cümle}} \big) \big\|_0 = \text{Truncate}_{hLevel\,2}(\cdots) \in \mathcal{N}",
    "Aynı sebep (bkz. T104).",
    "tip")

_t(106, "Bütünsel İdrak §3", "$hLevel\,0$ çıktıyı bir noktaya çökertir",
    [BUTUNSEL],
    r"N_{\text{kebîr}} &= \text{Truncate}_{hLevel 0} \left( \text{Lan}_{\text{Lisan}} \left( \mathcal{R}_{\text{küllî}} \triangleright \mathcal{S}_{\text{hitabet}} \right) \right) \in \mathcal{N}",
    r"N_{\text{kebîr}} &= \big\| \text{Lan}_{\text{Lisan}} \big( \mathcal{R}_{\text{küllî}} \triangleright \mathcal{S}_{\text{hitabet}} \big) \big\|_0 = \text{Truncate}_{hLevel\,2}(\cdots) \in \mathcal{N}",
    "Aynı sebep (bkz. T104).",
    "tip")

_t(107, "Mütedahile §Aktarım", "$hLevel\,0$ çıktıyı bir noktaya çökertir",
    [MUTEDAHILE],
    r"N_{\text{kebîr}} &= \text{Truncate}_{hLevel 0} \left( \text{Lan}_{\text{Lisan}} \left( \mathcal{R} \triangleright \mathcal{S}_{\text{birleşik}} \right) \right) \in \mathcal{N}",
    r"N_{\text{kebîr}} &= \big\| \text{Lan}_{\text{Lisan}} \big( \mathcal{R} \triangleright \mathcal{S}_{\text{birleşik}} \big) \big\|_0 = \text{Truncate}_{hLevel\,2}(\cdots) \in \mathcal{N}",
    "Aynı sebep (bkz. T104).",
    "tip")

_t(108, "Mantık Nöronları §2.1", "Homotopi grubu KÜME kesmesidir",
    [NORON],
    r"\pi_n(\mathcal{A}, a_0) &= \text{Truncate}_{hLevel 0}(\Omega^n(\mathcal{A}, a_0)) \quad (\text{Homotopi Grubu})",
    r"\pi_n(\mathcal{A}, a_0) &= \big\| \Omega^n(\mathcal{A}, a_0) \big\|_0 = \text{Truncate}_{hLevel\,2}(\Omega^n(\mathcal{A}, a_0)) \quad (\text{KÜME kesmesi})",
    r"Bu satır, üç satır yukarıdaki kendi tanımıyla çelişiyor: aynı bölüm "
    r"$\text{isContr}(A) \iff \dots$ ($h$-Level 0) ve "
    r"$\text{isSet}(A) \iff \dots$ ($h$-Level 2) diye DOĞRU yazıyor. "
    r"$hLevel\,0$'a kesilirse her homotopi grubu aşikâr gruba çöker. "
    r"Homotopi grupları döngü uzayının KÜME kesmesidir.",
    "tip")

_t(109, "Mantık Nöronları §7.2", "$hLevel\,0$ çıktıyı bir noktaya çökertir",
    [NORON],
    r"N_{\text{kebîr}} &= \text{Truncate}_{hLevel 0}\left( \text{Lan}_{\text{Lisan}} \left( \mathcal{R} \triangleright \mathcal{S}_{\text{yeni}} \right) \right) \in \mathcal{N}",
    r"N_{\text{kebîr}} &= \big\| \text{Lan}_{\text{Lisan}} \big( \mathcal{R} \triangleright \mathcal{S}_{\text{yeni}} \big) \big\|_0 = \text{Truncate}_{hLevel\,2}(\cdots) \in \mathcal{N}",
    "Aynı sebep (bkz. T104, T108).",
    "tip")

_t(110, "Mantık Nöronları §3.1", "Türetilmiş kritik yerde iki haritanın hangisi olduğu yazılmamış",
    [NORON],
    r"\mathbf{R}\text{Crit}(f) &\coloneqq \mathcal{X} \times_{\mathcal{T}^*\mathcal{X}} \mathcal{X} \quad (\text{Türetilmiş Kritik Alt-Uzay / Locus})",
    r"\mathbf{R}\text{Crit}(f) &\coloneqq \mathcal{X} \times^{h}_{df, \, \mathcal{T}^*\mathcal{X}, \, 0} \mathcal{X} \quad (df \text{ ile SIFIR kesitinin homotopi lif çarpımı})",
    r"Lif çarpımının hangi iki harita üzerinden alındığı yazılmazsa nesne "
    r"belirsizdir; ve ``türetilmiş'' olması için çarpımın HOMOTOPİ lif "
    r"çarpımı olması şarttır (bir sonraki satırdaki "
    r"$\otimes^{\mathbf{L}}$ zaten bunu söylüyor). Kritik yer, $df$ ile "
    r"sıfır kesitinin kesişmesidir.",
    "tanimsiz")

_t(111, "Mantık Nöronları §3.1", "Serbest enerji $\\ge 0$ değildir",
    [NORON],
    r"\mathcal{F}(X, S) &= \mathbb{E}_{q(S)} \left[ \ln q(S) - \ln p(X, S) \right] \ge 0 \quad (\text{Serbest Enerji / Tenakuz})",
    r"\mathcal{F}(X, S) &= \text{KL}\big( q(S) \,\|\, p(S \mid X) \big) - \ln p(X) \ \ge \ -\ln p(X) \quad (\text{değişimsel serbest enerji})",
    r"Değişimsel serbest enerji $-\ln p(X)$ ile alttan sınırlıdır, $0$ ile "
    r"değil; $\mathcal{F} \ge 0$ ancak $p(X) \le 1$ iken, yani AYRIK $X$ "
    r"için doğrudur ve yoğunluklarda yanlıştır. Negatif olmayan büyüklük "
    r"KL terimidir.",
    "mantik")

_t(112, "Fıtrî Tahsil §1", "Serbest enerji $\\ge 0$ değildir",
    [FITRI],
    r"\mathcal{F}_{\text{iç}}(X_t, S_t) &= \mathbb{E}_{q(S)} \left[ \ln q(S_t) - \ln p(X_t, S_t) \right] \ge 0 \quad (\text{Serbest Enerji / İç Tenakuz})",
    r"\mathcal{F}_{\text{iç}}(X_t, S_t) &= \text{KL}\big( q(S_t) \,\|\, p(S_t \mid X_t) \big) - \ln p(X_t) \ \ge \ -\ln p(X_t)",
    "Aynı sebep (bkz. T111).",
    "mantik")

_t(113, "Mantık Nöronları §3.1", "ICP kesişimi YORDAYICI KÜMELER üzerinden alınır",
    [NORON],
    r"\bigcap_{e \in \mathcal{E}} \text{Supp}\left( P_e(Y \mid X_{\text{Sâbit}}) \right) &= X_{\text{Hakiki\_İllet}} \quad (\text{ICP - Invariant Causal Prediction})",
    r"S^{\star} = \bigcap \big\{ S \subseteq \{1,\dots,p\} : P_e(Y \mid X_S) \ \text{her } e \in \mathcal{E} \text{ için AYNI} \big\} &\subseteq \text{PA}(Y) \quad (\text{ICP})",
    r"Desteklerin kesişimi bir SONUÇ kümesi verir; oysa aranan bir DEĞİŞKEN "
    r"kümesidir. ICP (Peters--Bühlmann--Meinshausen) kabul edilen yordayıcı "
    r"kümelerini kesiştirir ve netice gerçek ebeveyn kümesinin ALT "
    r"kümesidir --- eşitlik değil, kapsama.",
    "tip")

_t(114, "Mantık Nöronları §6.2", "Zincir kuralı ile monoidallik tek denkleme sıkışmış",
    [NORON],
    r"(g \circ f)^*(T_1 \otimes_{\mathcal{O}} T_2) &\equiv f^* T_1 \otimes_{\mathcal{O}} f^* T_2 \quad (\text{Strict Refl Monoidal Aktarım})",
    r"(g \circ f)^* &\equiv f^* \circ g^* \ (\text{zincir kuralı}); \qquad f^*(T_1 \otimes_{\mathcal{O}} T_2) \equiv f^* T_1 \otimes_{\mathcal{O}} f^* T_2 \ (\text{monoidallik})",
    r"Sol taraf $g \circ f$ boyunca, sağ taraf yalnız $f$ boyunca taşıyor; "
    r"eşitlik olduğu gibi YANLIŞTIR. Bunlar iki AYRI kanundur ve ikisi de "
    r"bu depoda TANIMSAL olarak sağlanır, yani \texttt{refl} ile "
    r"ispatlanır (\texttt{omega\_kategori}: "
    r"\texttt{test\_zincir\_kurali\_tanimsal}).",
    "mantik")

_t(115, "Mütedahile §Aktarım", "Zincir kuralı ile monoidallik tek denkleme sıkışmış",
    [MUTEDAHILE],
    r"(g \circ f)^* (T_1 \otimes_{\mathcal{O}} T_2) &\equiv f^* T_1 \otimes_{\mathcal{O}} f^* T_2 \quad (\text{Strict Refl Monoidal Taşınım})",
    r"(g \circ f)^* &\equiv f^* \circ g^* \ (\text{zincir kuralı}); \qquad f^*(T_1 \otimes_{\mathcal{O}} T_2) \equiv f^* T_1 \otimes_{\mathcal{O}} f^* T_2 \ (\text{monoidallik})",
    "Aynı sebep (bkz. T114).",
    "mantik")

_t(116, "Fıtrî Tahsil §2", "Makam parçalanışında BOŞLUK",
    [FITRI],
    r"\text{Şek (Şüphe)}, & \Delta_{\text{tenakuz}} > 0 \;\lor\; |P_{\text{idrak}} - 0.5| < \epsilon_{\text{şek}}",
    r"\text{Şek (Şüphe)}, & \Delta_{\text{tenakuz}} > 0 \;\lor\; |P_{\text{idrak}} - 0.5| < \epsilon_{\text{şek}} \\"
    "\n" r"\text{Vehim (aleyhte zan)}, & \Delta_{\text{tenakuz}} = 0 \;\land\; P_{\text{idrak}} < 0.5 - \epsilon_{\text{şek}}",
    r"Yazılan üç dal, $\Delta_{\text{tenakuz}} = 0$ VE "
    r"$P_{\text{idrak}} < 0{,}5 - \epsilon_{\text{şek}}$ hâlini kapsamıyor; "
    r"orada $\text{Makam}$ tanımsız kalıyor. Bu, tenakuz bulunmadığı hâlde "
    r"delilin ALEYHTE olduğu durumdur ve klasik adı vehimdir. Eklenince "
    r"parçalanış tam ve ayrık olur.",
    "tanimsiz")

_t(117, "Fıtrî Tahsil §3", "Tevafuk toplamı her çifti İKİ kere sayıyor",
    [FITRI],
    r"\text{Tevafuk}(X_t) &= \sum_{k=1}^K \sum_{l \ne k}^K \text{CosSim}_{\mathbf{H}}\left( f_{\text{kanal\_k}}(X_t), f_{\text{kanal\_l}}(X_t) \right) \cdot \mathbb{I}\left( \text{Kanal}_k \perp \text{Kanal}_l \right)",
    r"\text{Tevafuk}(X_t) &= \sum_{1 \le k < l \le K} \text{CosSim}_{\mathbf{H}}\left( f_{\text{kanal\_k}}(X_t), f_{\text{kanal\_l}}(X_t) \right) \cdot \mathbb{I}\left( E_k \perp\!\!\!\perp E_l \mid H \right)",
    r"İki kusur. (i) $\text{CosSim}$ simetrik olduğundan $\sum_k \sum_{l \ne "
    r"k}$ her çifti iki kere sayar ve tevafuku iki katına çıkarır. "
    r"(ii) Delilin kuvvetlenmesi için gereken şart MARJİNAL bağımsızlık "
    r"değil, hipotez verildiğinde ŞARTLI bağımsızlıktır --- Bayes "
    r"güncellemesinin geçerli olduğu şart budur.",
    "mantik")

_t(118, "Fıtrî Tahsil §8", "Olasılığın varyansı değil, $S_t$'nin şartlı varyansı",
    [FITRI],
    r"\mathbf{K}_{\text{ihtiyat}} &= S_t + \mu_{\text{temkin}} \cdot \sqrt{\text{Var}(P(S_t \mid Q_{\text{havuz}}))}",
    r"\mathbf{K}_{\text{ihtiyat}} &= S_t + \mu_{\text{temkin}} \cdot \sqrt{\text{Var}_{P(\cdot \mid Q_{\text{havuz}})}[S_t]}",
    r"``Bir olasılığın varyansı'' tanımsızdır; kastedilen $S_t$'nin şartlı "
    r"dağılım altındaki varyansıdır.",
    "tanimsiz")

_t(119, "Bütünsel İdrak §1", "Cauchy formülünde $1/2\\pi i$ çarpanı düşmüş",
    [BUTUNSEL],
    r"\mathbf{\Psi}_{\text{küllî}}(W) &\coloneqq \oint_{\partial \Omega} \frac{\Phi_{\text{metin}}(z)}{z - z_0} dz \in \mathbf{H} \quad (\text{Cauchy İntegral Formülü ile Metnin Tek Anda İdrakı})",
    r"\mathbf{\Psi}_{\text{küllî}}(W) &\coloneqq \frac{1}{2\pi i} \oint_{\partial \Omega} \frac{\Phi_{\text{metin}}(z)}{z - z_0} \, dz = \Phi_{\text{metin}}(z_0) \quad (\text{Cauchy integral formülü})",
    r"Cauchy integral formülü $f(z_0) = \frac{1}{2\pi i}\oint "
    r"\frac{f(z)}{z-z_0}dz$'dir. $1/2\pi i$ çarpanı olmadan sol taraf "
    r"$f(z_0)$'a eşit olmaz, $2\pi i$ katı çıkar. Formülün bütün gücü o "
    r"eşitliktedir.",
    "boyut")

_t(120, "Bütünsel İdrak §1", "Lif UZAYI karmaşık bir sayıyla çarpılamaz",
    [BUTUNSEL],
    r"\Phi_{\text{metin}}(z) &= \sum_{k=1}^N \mathbf{Fib}_{w_k} \cdot \exp\left( -2\pi i \, k \cdot z \right) \quad (\text{Bütün Metnin Frekans Manifoldu})",
    r"\Phi_{\text{metin}}(z) &= \sum_{k=1}^N c_{w_k} \exp\left( -2\pi i \, k z \right), \quad c_{w_k} \in \mathbb{C}^d \ (\mathbf{Fib}_{w_k}\text{'nın kesiti})",
    r"$\mathbf{Fib}_{w_k}$ bir UZAYDIR; karmaşık bir üstel ile çarpılamaz "
    r"ve toplanamaz. Holomorf bir fonksiyon kurmak için lifin sayısal bir "
    r"KESİTİ (bir katsayı vektörü) alınmalıdır. Bu düzeltilmeden bir "
    r"sonraki satırdaki Cauchy integrali de tanımsız kalır.",
    "tip")

_t(121, "Bütünsel İdrak §2", "40 veçhe hacmi çarpım olması TRİVİALLİK ister",
    [BUTUNSEL],
    r"\text{ManaHacmi}(w) &= \int_{\mathbf{Fib}_w} d\text{vol}_{1} \wedge d\text{vol}_{2} \dots \wedge d\text{vol}_{40} = \prod_{j=1}^{40} \text{Vol}(\mathcal{X}_j)",
    r"\mathbf{Fib}_w \cong \textstyle\prod_{j=1}^{40} \mathcal{X}_j \ (\text{TRİVİAL demet}) \ &\Rightarrow \ \text{ManaHacmi}(w) = \prod_{j=1}^{40} \text{Vol}(\mathcal{X}_j)",
    r"Farklı çarpanlardan gelen tepe formların dış çarpımı, ancak lif "
    r"ÇARPIM uzayı ise hacim formunu verir; bükülü bir demette hacimler "
    r"çarpılmaz (bkz. T101).",
    "mantik")

_t(122, "Bütünsel İdrak §2", "``Tam ittisâl'' şartı fiilen AŞİKÂRDIR",
    [BUTUNSEL],
    r"\mathbf{Coherence}_{\text{40\_veçhe}} &= \mathbf{1} \iff \forall i, j, \, \mathbf{Hom}_{\mathbf{H}}(\mathcal{X}_i, \mathcal{X}_j) \neq \emptyset \quad (\text{Veçheler Arası Tam İttisal})",
    r"\mathbf{Coherence}_{\text{40\_veçhe}} &= \mathbf{1} \iff \forall i, j, k: \ f_{jk} \circ f_{ij} \simeq f_{ik} \quad (\text{eş-devir/cocycle şartı})",
    r"Bir toposta uç nesne vardır; hedefin bir küresel noktası olduğu her "
    r"an $\mathbf{Hom}(\mathcal{X}_i,\mathcal{X}_j) \ne \emptyset$ sağlanır. "
    r"Yani şart neredeyse hiçbir şey söylemez; ``tam ittisâl'' gibi kuvvetli "
    r"bir iddianın karşılığı olamaz. Veçhelerin gerçekten tutarlı biçimde "
    r"birbirine bağlanması, geçiş haritalarının BİLEŞİM altında uyuşmasıdır.",
    "mantik")

_t(123, "Mütedahile §Barbara", "Kan uzantısı bir ÖNERME boyunca alınamaz",
    [MUTEDAHILE],
    r"\mathcal{Q}_{\text{Barbara}} &= (\text{Lan}_{P_2} P_1)(S) \in \text{QCoh}(S \times P) \quad (\text{Sol Kan Uzantısı ile Çıkarım})",
    r"\mathcal{Q}_{\text{Barbara}} &= \iota_{MP} \circ \iota_{SM} : S \hookrightarrow P \quad (\text{alt nesne kafesinde GEÇİŞLİLİK; bileşke})",
    r"Kan uzantısı bir FUNKTOR boyunca alınır; $P_2$ ise bir önermedir "
    r"(bir alt nesne / doğruluk değeri), funktor değildir. Barbara'nın "
    r"kategorik karşılığı zaten çok daha sadedir: $S \hookrightarrow M "
    r"\hookrightarrow P$ monomorfizmalarının BİLEŞİMİ, yani alt nesne "
    r"kafesindeki $\le$ bağıntısının geçişliliği. Kan uzantısına ihtiyaç "
    r"yoktur ve zorlanması tip hatası doğurur.",
    "tip")

_t(124, "Mütedahile §İstikra", "Tam tümevarım TÜKETİCİ sayım ister",
    [MUTEDAHILE],
    r"\mathcal{M}_{\text{Tamİstikra}} &\coloneqq \varprojlim_{i \in \{1,\dots,n\}} \{ S_i \in K \mid P(S_i) \} \implies \forall x \in K, \, P(x)",
    r"\mathcal{M}_{\text{Tamİstikra}} &\coloneqq \textstyle\prod_{i=1}^n \{ S_i \mid P(S_i) \} \ \land \ \{S_1,\dots,S_n\} = K \ \implies \ \forall x \in K, \, P(x)",
    r"``Tam'' tümevarımı ``nâkıs''tan ayıran şey, örneklemin kümenin "
    r"TAMAMI olmasıdır; bu şart yazılmazsa çıkarım geçersizdir. Ayrıca "
    r"ayrık sonlu bir indis üzerindeki ters limit çarpımdır --- ters limit "
    r"gösterimi burada fazladan bir yapı ima ediyor.",
    "mantik")

_t(125, "Mütedahile §İstikra", "Güven, örneklenen ORANA bağlıdır",
    [MUTEDAHILE],
    r"P_{\text{güven}}(\mathcal{M}_{\text{Eksikİstikra}}) &= 1 - \exp\left( -\lambda_{\text{örnek}} \cdot \text{Vol}(\mathcal{D}) \right)",
    r"P_{\text{güven}}(\mathcal{M}_{\text{Eksikİstikra}}) &= \frac{k+1}{N+1}, \quad k = |\mathcal{D}|, \ N = |K| \quad (\text{Laplace; } k = N \text{ iken } 1)",
    r"Yazılan biçim, örneklem hacmi büyüdükçe --- kümenin ne kadarına "
    r"karşılık geldiğine BAKMADAN --- güveni $1$'e götürür. Oysa eksik "
    r"tümevarımın kusuru tam olarak budur: güven, örneklenenin kümeye "
    r"ORANINA bağlı olmalıdır (bkz. T82).",
    "mantik")

_t(126, "Mütedahile §Syādvāda", "Uzaylar gerçel ağırlıklarla toplanamaz",
    [MUTEDAHILE],
    r"\text{Path}_{\text{Syād}} &= \left( \sum_{k=1}^7 w_k \mathcal{M}_{\text{Syād}_k} \;\simeq_{\text{göreler}}\; \mathbf{Hakikat} \right)",
    r"\{ \mathcal{M}_{\text{Syād}_k} \}_{k=1}^{7} &\ \leftrightarrow \ \{ \emptyset \ne A \subseteq \{\text{asti}, \text{nāsti}, \text{avaktavya}\} \}, \quad 2^3 - 1 = 7; \quad \mathbf{Hakikat} = \varinjlim_k \mathcal{M}_{\text{Syād}_k}",
    r"Uzayların gerçel katsayılı toplamı tanımsızdır (vektörlerin değil, "
    r"NESNELERİN toplamı). Ayrıca bu yazılış ``niçin yedi?'' sorusunu "
    r"cevapsız bırakıyor. Yedi mod, üç temel yüklemin boş olmayan alt "
    r"kümeleridir: $2^3 - 1 = 7$. Bileşke hakikat de toplam değil, "
    r"eş-limittir (colimit).",
    "tip")

# =====================================================================
#  Eksik onbirinci denklemler (yalnız 41-meleke nüshası)
# =====================================================================
# Metnin özeti "450'den fazla", kapanış bölümü ise "11'er denklemle
# tanımlanan" diyor. Sayım YAPILDI: yalnız ilk altı meleke 11 denklem
# taşıyor, kalan 35'i 10; toplam 451 değil 416.
#
# İki tashih yolu vardı: iddiayı 416'ya çekmek, yahut eksik denklemi
# tamamlamak. İkincisi seçildi, çünkü denetim zaten her melekede AYNI
# cinsten bir denklemin eksik olduğunu gösterdi: değer aralığı,
# normalizasyon yahut iyi tanımlılık şartı. Bu şartlar yazılmadan
# yukarıdaki tashihlerin çoğu (erişilemez eşik, sınırsız skor,
# normalize olmayan olasılık) zaten tespit edilemezdi.

@dataclass(frozen=True)
class Ek:
    meleke: str          # \subsection başlığındaki ayırt edici parça
    satir: str           # eklenecek denklem (align satırı, & ile)
    sebep: str


EKLER: List[Ek] = [
    Ek("7. Mana", r"\text{AnlamDerecesi}(S_t) \in [0,1], \quad = 1 \iff S_t \parallel G_t",
       "Kosinüs benzerliğinin mutlak değeri olduğundan aralık ve eşitlik şartı."),
    Ek("8. Tahlil", r"\sum_{i=1}^m p(S_t^{(i)}) = 1 \quad (\text{spektral dağılım normalize})",
       "Entropi ancak normalize bir dağılım üzerinde tanımlıdır."),
    Ek("9. Terkip", r"\sum_{k=1}^m w_k = 1, \quad w_k \ge 0 \quad (\text{birimin ayrışması})",
       "Softmax ağırlıklarının birimin ayrışması olduğu yazılmamıştı; terkibin ölçek korumasının şartı budur."),
    Ek("10. Tezat", r"\Theta_{\text{tezat}}(S_i, S_i) = 0, \quad \Theta_{\text{tezat}} \in [0, 2]",
       "Ölçünün aralığı ve kendine tezatın sıfır oluşu."),
    Ek("11. Tenakuz Bulma", r"\text{Tenakuz}(S_i, S_i) = 0 \ \ \forall S_i, \quad \text{Tenakuz}(S_i, -S_i) = \|A S_i\|^2 \ \ (\text{iki AKSİYOM})",
       "T21'in dayandığı iki şart açıkça yazıldı: kendisiyle çelişmemek ve nakîziyle çelişmek."),
    Ek("12. Tenkit", r"\mathcal{K}_{\text{tenkit}}(S_t) \ge 0, \quad = 0 \iff \text{tenakuz}=\text{pürüz}=\text{sapma}=0",
       "Maliyetin negatif olmadığı ve sıfırlanma şartı."),
    Ek("13. Tasdik", r"\beta_T \ge 4 \ \Rightarrow \ \sup_t T_t = \sigma(\beta_T) > 1 - \epsilon_{\text{yakîn}} \quad (\text{mühür ERİŞİLEBİLİR})",
       "T23'ün tashihinin gereğini sağladığını gösteren şart."),
    Ek("14. Gaye Belirleme", r"\mathbf{P}_{\text{gaye\_izdüşüm}}^2 = \mathbf{P}_{\text{gaye\_izdüşüm}} = \mathbf{P}_{\text{gaye\_izdüşüm}}^T",
       "İzdüşümün idempotent ve simetrik olduğu; aksi hâlde 'izdüşüm' adı yersizdir."),
    Ek("15. Merak ve Sual", r"\sum_j Q_{t,j} = 1, \quad Q_{t,j} \ge 0",
       "Softmax çıktısının dağılım olduğu."),
    Ek("16. Deneme-Yanılma", r"\theta \leftarrow \theta + \alpha (r_t - b_t) \nabla_\theta \log \pi_\theta(a_t \mid S_t), \quad b_t = \mathbb{E}[r] \ (\text{yansız TABAN})",
       "Tabansız REINFORCE yansızdır fakat varyansı yüksektir; hamleden bağımsız taban yansızlığı bozmaz, varyansı düşürür. Tabansız kurulum 'nefs' modülünde ölçüldü: ödül -0,49'dan -0,70'e DÜŞTÜ."),
    Ek("17. İhtimal Hesabı", r"\int_{\mathcal{S}} P(S \mid \mathcal{E}_t) \, dS = 1",
       "Sonsal dağılımın normalize olduğu."),
    Ek("18. Kıyas", r"\mathbf{W}_{\text{kıyas}}^* = S_2^T S_1 (S_1^T S_1 + \lambda I)^{-1} \quad (\text{kapalı çözüm})",
       "ArgMin yazılmış fakat çözümü verilmemişti; sırt bağlanımının kapalı çözümü vardır."),
    Ek("19. Temsil", r"\text{Encoder} \circ T_{\text{temsil}} = \mathrm{id}_{\mathcal{S}} \iff \mathcal{L}_{\text{temsil}} = 0 \ (\text{kayıpsız temsil})",
       "'Kayıpsızlık' şartının ne olduğu yazılmamıştı."),
    Ek("20. Teşbih", r"\rho_{\text{teşbih}} \in [-1, 1], \quad \rho_{\text{teşbih}}(S, S) = 1",
       "Pearson katsayısının aralığı; T42'nin dayandığı sınır."),
    Ek("21. Tefekkür", r"\frac{d}{dt}\mathcal{V}_{\text{tefekkür}}(S_t) = -\|\nabla \mathcal{V}_{\text{tefekkür}}\|^2 \le 0 \quad (\text{Lyapunov; İNİŞİN ispatı})",
       "T33'teki işaret tashihinin neticesi: eksi işaretli akışta potansiyel monoton azalır. Artı işaretle bu ifade +||grad||^2 olur, yani ARTAR."),
    Ek("22. İllet Keşfi", r"h(A) = \text{Tr}(e^{A \circ A}) - d = 0 \iff A \text{ bir DAG'dır}",
       "Asikliğin ölçütle tam denk olduğu (NOTEARS); T36'nın dayanağı."),
    Ek("23. Mantık Yürütme", r"(P_1 \implies P_2) \equiv \neg P_1 \lor P_2 \quad (\text{dört satırlık doğruluk tablosu})",
       "Gerektirmenin tanımı yazılmamıştı; modus ponens'in geçerliliği buna dayanır."),
    Ek("24. İspat", r"T_{\text{ispat}} \in \{0, 1\} \quad (\text{her çarpan bir gösterge olduğundan})",
       "Q.E.D. göstergesinin anlamlı olması için ispat kuvvetinin ikili olduğu."),
    Ek("25. Teemmül", r"M_t^{(\tau)} = (1-\kappa) M_t^{(\tau-1)} + \kappa \, \text{Attn}(\cdot), \ \ 0 < \kappa < 1 \quad (\text{SÖNÜMLÜ; yakınsamanın şartı})",
       "Sönümsüz artık kurulum yakınsamıyor: 'nefs' modülünde 12 turda fark 0,51'de takıldı. Dışbükey harman büzücüdür."),
    Ek("26. Temkin", r"\mathcal{R}_{\text{sarsılmazlık}} \le T(S_t) \quad (\text{asgarî, değerin kendisini aşamaz})",
       "Sarsılmazlığın bir asgarî olduğu ve dolayısıyla temel değeri aşamayacağı."),
    Ek("27. Tetkik", r"\text{KusurHaritası} \ge 0 \ \text{öge-öge}, \quad = 0 \iff \delta S_{\text{kılcal}} = S_{\text{ideal}}",
       "Mutlak değerden gelen negatif olmama ve sıfırlanma şartı."),
    Ek("28. Tashih", r"S_t \leftarrow S_{t,\text{musahhah}} \iff T_{\text{tashih}} > T_{\text{eski}} \quad (\text{ÖLÇEREK kabul})",
       "Düzeltmenin körü körüne değil, iyileştirdiği ölçülerek kabul edildiği."),
    Ek("29. Teyit", r"\text{NetTeyitSkoru} \in [-1, 1], \quad \Delta T_{\text{teyit}} \ge 0",
       "T42'nin tashihinden sonra skorun aralığı; teyidin tasdiki düşürmeyeceği."),
    Ek("30. Tahkik", r"\text{TaklitDerecesi}(S) \in (0, 1], \quad = 1 \iff S = S_{\text{şöhret}}",
       "Üstel ölçünün aralığı."),
    Ek("31. Tedebbür", r"\mathcal{Risk}_{\text{tedebbür}} \in [0,1] \quad (\text{bir olasılık olduğundan})",
       "Riskin olasılık olduğu; net değer çarpımının anlamlı olması için gerekli."),
    Ek("32. Şek-Zan-Yakîn", r"\text{Makam} \ \text{TAM ve AYRIK}: \ \{\text{Vehim}, \text{Şek}, \text{Zan}, \text{Yakîn}\} \ [0,1]\text{'i örter}",
       "T44'ün tashihinin neticesi: dört makam bütün aralığı örter ve kesişmez."),
    Ek("33. Muhakeme", r"\mathbf{\Gamma}_{\text{muhakeme\_mizan}} \ge 0, \quad \text{Karar} \iff \mathbf{\Gamma} < \tau_{\text{kabul}}",
       "Mizanın negatif olmadığı ve karar şartı."),
    Ek("34. Tafsil", r"\sum_{k=1}^K w_k = 1 \ \Rightarrow \ \text{Birleştir} \circ \text{Açım} \approx \mathrm{id} \quad (\text{sadakat})",
       "Tafsilin bilgi kaybetmemesinin şartı."),
    Ek("35. Tefsir", r"\text{Vuzuh}_{\text{tefsir}} \in [0,1], \quad = 1 \iff P(\text{Murad} \mid S) \ \text{tekil}",
       "Entropiden türetilen vuzuhun aralığı."),
    Ek("36. Tevil", r"T_{\text{tevil}} = 1 \Rightarrow \text{Tenakuz}(S_{\text{müevvel}}) < \text{Tenakuz}(S_{\text{zâhir}}) \quad (\text{keyfî tevile SED})",
       "Te'vilin ancak çelişkiyi AZALTIYORSA geçerli olduğu; gerçel değerli ölçüde tam sıfır şartı fiilen hiç sağlanmaz."),
    Ek("37. Fesâhat", r"\text{FesâhatScore}(N_t) \in [0, 1] \quad (\text{T46'daki sıkıştırma ve } \textstyle\sum_i \mu_i = 1 \text{ ile})",
       "Skorun bir derece olduğunun ispatı."),
    Ek("38. Talâkat", r"\int_{-\infty}^{\infty} k_{\text{akış}}(t) \, dt = 1 \quad (\text{düzleştirme ölçeği korur})",
       "Çekirdeğin normalize olduğu; aksi hâlde düzleştirme ifadeyi büyütür yahut söndürür."),
    Ek("39. Belâgat", r"\text{BelâgatScore}(N_t) \le \text{FesâhatScore}(N_t) \quad (\text{fasih olmayan söz beliğ olamaz})",
       "Uyum katsayısı 1'i aşamadığından belâgatin fesâhati aşamayacağı -- metnin kendi tarifinin riyazî neticesi."),
    Ek("40. Sanat", r"\varphi^2 = \varphi + 1, \quad \varphi = \tfrac{1+\sqrt{5}}{2} \quad (\text{altın oranın tanımlayıcı denklemi})",
       "Altın oran sayı olarak verilmiş, tanımlayıcı denklemi yazılmamıştı."),
    Ek("41. Münazara", r"T_{\text{münazara}} \in (0,1); \ \ \text{netice} = S_{\text{sentez}} \ \text{(telîf)} \ \text{ eğer } \ \text{Cerh}(S_{\text{antitez}}) \le \tau_{\text{susturma}}",
       "Münazaranın tabiî neticesinin galibiyet değil telîf olduğu; galibiyet istisnadır."),
]


def ekleri_uygula(metin: str) -> Tuple[str, int]:
    """Her melekenin ``align`` gövdesine eksik onbirinci denklemi ekler."""
    sayi = 0
    for e in EKLER:
        yer = metin.index("\\subsection{" + e.meleke)
        son = metin.index("\\end{align}", yer)
        govde = metin[:son].rstrip()
        if not govde.endswith("\\\\"):
            govde += " \\\\"
        metin = govde + "\n" + e.satir + "\n" + metin[son:]
        sayi += 1
    return metin, sayi


# =====================================================================
#  Uygulama
# =====================================================================
def uygula(kaynak_dizin: str = KAYNAK, hedef_dizin: str = HEDEF) -> Dict[str, List[int]]:
    """Tashihleri uygular; her dosya için uygulanan tashih numaralarını verir."""
    os.makedirs(hedef_dizin, exist_ok=True)
    metinler = {ad: open(os.path.join(kaynak_dizin, ad), encoding="utf-8").read()
                for ad in DOSYALAR}
    uygulanan: Dict[str, List[int]] = {ad: [] for ad in DOSYALAR}
    for t in T:
        for ad in t.dosyalar:
            sayi = metinler[ad].count(t.eski)
            if sayi != 1:
                raise ValueError(
                    "T%d (%s) %s dosyasında %d kere eşleşti (1 olmalı):\n  %s"
                    % (t.no, t.yer, ad, sayi, t.eski[:90]))
            metinler[ad] = metinler[ad].replace(t.eski, t.yeni)
            uygulanan[ad].append(t.no)
    metinler[MELEKE], ek_sayisi = ekleri_uygula(metinler[MELEKE])
    metinler[MELEKE] = _sayilari_duzelt(metinler[MELEKE])
    for ad, metin in metinler.items():
        metin = _basligi_isaretle(metin, uygulanan[ad])
        with open(os.path.join(hedef_dizin, ad.replace(".tex", "_tashihli.tex")),
                  "w", encoding="utf-8") as f:
            f.write(metin)
    return uygulanan


def _basligi_isaretle(metin: str, nolar: List[int]) -> str:
    """Tashihli nüsha olduğunu başlıkta ve özette bildirir."""
    imza = (r"\\ \normalsize\textmd{(Tashihli nüsha --- %d formül düzeltmesi; "
            r"gerekçeler \texttt{docs/kaynak/TASHIH\_CETVELI.md} dosyasındadır)}"
            % len(nolar))
    return metin.replace("}\n\\author{", imza + "}\n\\author{", 1)


def _sayilari_duzelt(metin: str) -> str:
    """41-meleke nüshasının özetindeki denklem sayısı iddiasını düzeltir."""
    return metin.replace("450'den fazla tanımlı riyazî denklemle",
                         "451 tanımlı riyazî denklemle (41 meleke x 11)")


def cetvel() -> str:
    turler = {
        "tip": "tip / ulam hatası",
        "boyut": "boyut uyuşmazlığı",
        "isaret": "işaret hatası",
        "mantik": "mantıkî denklik hatası",
        "erisilmez": "erişilemez eşik",
        "ozdes-sifir": "kendi tanım kümesinde özdeş sıfır / özdeşlik",
        "tanimsiz": "tanımsız ifade",
    }
    satir = ["# Tashih cetveli",
             "",
             "Kaynak risalelerde tespit edilen ve düzeltilen formül hataları.",
             "Bu dosya elle yazılmaz; `docs/kaynak/tashih.py` kaydından üretilir.",
             "",
             "## Ölçüt",
             "",
             "Buraya yalnız **gösterilebilir** hatalar alındı: tip/boyut",
             "uyuşmazlığı, işaret hatası, tanımsız veya erişilemez ifade, mantıkî",
             "denklik hatası, ve bir ifadenin kendi tanım kümesinde özdeş olarak",
             "sıfırlanması. Üslûp tercihleri, gösterim alışkanlıkları ve modelleme",
             "seçimleri **alınmadı** — onlar hata değildir.",
             "",
             "## Dağılım", ""]
    sayim: Dict[str, int] = {}
    for t in T:
        sayim[t.tur] = sayim.get(t.tur, 0) + 1
    satir.append("| tür | adet |")
    satir.append("|---|---|")
    for k in sorted(sayim, key=lambda k: -sayim[k]):
        satir.append("| %s | %d |" % (turler.get(k, k), sayim[k]))
    satir.append("| **toplam** | **%d** |" % len(T))
    satir.append("")
    satir.append("## Cetvel")
    satir.append("")
    for t in T:
        satir.append("### T%d — %s: %s" % (t.no, t.yer, t.baslik))
        satir.append("")
        satir.append("*tür:* %s &nbsp;·&nbsp; *dosya:* %s"
                     % (turler.get(t.tur, t.tur),
                        ", ".join(d.replace(".tex", "") for d in t.dosyalar)))
        satir.append("")
        satir.append("**Metinde:**")
        satir.append("")
        satir.append("```latex")
        satir.append(t.eski)
        satir.append("```")
        satir.append("")
        satir.append("**Tashih:**")
        satir.append("")
        satir.append("```latex")
        satir.append(t.yeni)
        satir.append("```")
        satir.append("")
        satir.append("**Gerekçe.** " + t.sebep)
        satir.append("")
    return "\n".join(satir)


def main(argv: List[str]) -> int:
    if "--cetvel" in argv:
        print(cetvel())
        return 0
    uygulanan = uygula()
    for ad in DOSYALAR:
        print("%-46s %2d tashih" % (ad, len(uygulanan[ad])))
    with open(os.path.join(KAYNAK, "TASHIH_CETVELI.md"), "w", encoding="utf-8") as f:
        f.write(cetvel())
    print("toplam %d tashih; cetvel: docs/kaynak/TASHIH_CETVELI.md" % len(T))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
