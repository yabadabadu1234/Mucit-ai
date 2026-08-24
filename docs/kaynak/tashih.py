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

DOSYALAR = (KULLI, MELEKE, HOTT, FITRAT)


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
    "T31'in devamı.",
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
