# Tashih cetveli

Kaynak risalelerde tespit edilen ve düzeltilen formül hataları.
Bu dosya elle yazılmaz; `docs/kaynak/tashih.py` kaydından üretilir.

## Ölçüt

Buraya yalnız **gösterilebilir** hatalar alındı: tip/boyut
uyuşmazlığı, işaret hatası, tanımsız veya erişilemez ifade, mantıkî
denklik hatası, ve bir ifadenin kendi tanım kümesinde özdeş olarak
sıfırlanması. Üslûp tercihleri, gösterim alışkanlıkları ve modelleme
seçimleri **alınmadı** — onlar hata değildir.

## Dağılım

| tür | adet |
|---|---|
| tip / ulam hatası | 48 |
| mantıkî denklik hatası | 33 |
| tanımsız ifade | 21 |
| boyut uyuşmazlığı | 8 |
| yapi | 6 |
| erişilemez eşik | 3 |
| işaret hatası | 3 |
| kendi tanım kümesinde özdeş sıfır / özdeşlik | 2 |
| sağlamlık | 1 |
| **toplam** | **125** |

## Cetvel

### T1 — 𝒪₁ Müşahede: Dikkat çekirdeğinde $W_k$ düşmüş

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_kulli_formulasyon

**Metinde:**

```latex
\text{Softmax}\left(\frac{X_t W_q X_t^T}{\sqrt{d}}\right) X_t W_v
```

**Tashih:**

```latex
\text{Softmax}\left(\frac{(X_t W_q)(X_t W_k)^T}{\sqrt{d}}\right) X_t W_v
```

**Gerekçe.** Yazıldığı hâliyle anahtar dizeyi birim alınmış oluyor ($W_k = I$). Bu, aynı külliyattaki HoTT nüshasının $\langle X_t W_q, X_t W_k\rangle$ ifadesiyle ve bir satır yukarıdaki $V_{\text{odak}}$ tanımında geçen $W_k$ ile çelişir.

### T2 — 𝒪₁ Müşahede: Dikkat çekirdeğinde $W_k$ düşmüş

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_41_meleke

**Metinde:**

```latex
\text{Softmax}\left(\frac{X_t W_q X_t^T}{\sqrt{d_{\text{in}}}}\right) X_t W_v
```

**Tashih:**

```latex
\text{Softmax}\left(\frac{(X_t W_q)(X_t W_k)^T}{\sqrt{d_{\text{in}}}}\right) X_t W_v
```

**Gerekçe.** Aynı sebep (bkz. T1).

### T3 — 𝒪₅ Tecrit: Grassmannian'a izdüşüm diye bir şey yoktur

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_kulli_formulasyon

**Metinde:**

```latex
P_D(X_t) &= \text{Proj}_{\text{Gr}(k,d)}\left( X_t \right) = U_k U_k^T X_t
```

**Tashih:**

```latex
P_D(X_t) &= \Pi_V(X_t) = U_k U_k^T X_t, \quad V = \text{span}(U_k) \in \text{Gr}(k,d)
```

**Gerekçe.** Grassmannian, alt uzayLARIN uzayıdır. Bir vektör Grassmannian'a izdüşürülmez; Grassmannian'ın bir NOKTASI olan $V$ alt uzayına izdüşürülür. Yazılışta izdüşümün hedefi ile hedefin yaşadığı uzay birbirine karışmış.

### T4 — 𝒪₅ Tecrit: Grassmannian'a izdüşüm diye bir şey yoktur

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_41_meleke

**Metinde:**

```latex
\text{Proj}_{\text{Gr}(k,d_{\text{in}})}\left( X_t \right) = U_k U_k^T X_t
```

**Tashih:**

```latex
\Pi_V(X_t) = U_k U_k^T X_t, \quad V = \text{span}(U_k) \in \text{Gr}(k, d_{\text{in}})
```

**Gerekçe.** Aynı sebep (bkz. T3).

### T5 — 𝒪₅ Tecrit: Softmax çıktısı Grassmannian noktası değildir

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_41_meleke

**Metinde:**

```latex
D_t &= \text{Softmax}\left( \frac{\Delta_{\text{Laplasyen}}(X_t) W_d}{\sqrt{d_k}} \right) \in \mathcal{T}_{\text{inv}}
```

**Tashih:**

```latex
D_t &= U_k U_k^T, \quad \Delta_{\text{Laplasyen}} u_j = \lambda_j u_j, \ \lambda_1 \le \dots \le \lambda_k \quad (\text{izdüşüm; softmax değil})
```

**Gerekçe.** Softmax çıktısı satır-stokastik bir dizeydir: negatif olmayan, satır toplamı 1. Bir Grassmannian noktası ise idempotent ve simetrik bir izdüşüm ($P^2 = P = P^T$) ile temsil edilir. İkisi ayrı nesnelerdir. Değişmez alt uzay, Laplasyen'in en küçük özdeğerlerine ait ÖZVEKTÖRLERİN gerdiği uzaydır.

### T6 — 𝒪₅ Tecrit: Softmax çıktısı Grassmannian noktası değildir

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_hott_topos

**Metinde:**

```latex
D_t &= \text{Softmax}\left( \frac{\Delta_{\text{Laplasyen}}(X_t) W_d}{\sqrt{d_k}} \right) \in \text{Gr}(k, d_{\text{in}})
```

**Tashih:**

```latex
D_t &= U_k U_k^T, \quad \Delta_{\text{Laplasyen}} u_j = \lambda_j u_j, \ \lambda_1 \le \dots \le \lambda_k \quad (\text{izdüşüm; softmax değil})
```

**Gerekçe.** Aynı sebep (bkz. T5).

### T7 — 𝒪₅ Tecrit: $D_t \cdot (X_t W_s)$ çarpımı boyut tutmuyor

*tür:* boyut uyuşmazlığı &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_kulli_formulasyon, nefs_i_mudrike_41_meleke

**Metinde:**

```latex
S_t^{(\text{tecrit})} &= D_t \cdot (X_t W_s) \in \mathcal{S}
```

**Tashih:**

```latex
S_t^{(\text{tecrit})} &= (X_t D_t) W_s \in \mathcal{S} \quad (\text{önce izdüşüm, sonra eşleme})
```

**Gerekçe.** $D_t \in \mathbb{R}^{d_{\text{in}} \times d_{\text{in}}}$ iken $X_t W_s \in \mathbb{R}^{n \times d_{\text{sem}}}$; çarpım tanımsız. İzdüşüm ham uzayda alınmalı, semantik eşleme ondan SONRA gelmeli.

### T8 — 𝒪₅ Tecrit: $D_t \cdot (X_t W_s)$ çarpımı boyut tutmuyor

*tür:* boyut uyuşmazlığı &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_hott_topos

**Metinde:**

```latex
S_t^{(\text{tecrit})} &= D_t \otimes_{\mathcal{O}_{\mathcal{X}}} (X_t W_s) \in \mathcal{S}
```

**Tashih:**

```latex
S_t^{(\text{tecrit})} &= (X_t D_t) W_s \in \mathcal{S} \quad (\text{önce izdüşüm, sonra eşleme})
```

**Gerekçe.** Aynı sebep (bkz. T7); tensör çarpımı ile dizey çarpımı da birbirinin yerine kullanılmış.

### T9 — 𝒪₅ Tecrit: Betti sayılarının gradyanı alınamaz

*tür:* tanımsız ifade &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\mu_{\text{inv}} \sum_k \|\nabla_{\text{araz}} \beta_k\|^2
```

**Tashih:**

```latex
\mu_{\text{inv}} \sum_k \|\nabla_{\text{araz}} \lambda_k(\Delta_{\text{Laplasyen}})\|^2
```

**Gerekçe.** $\beta_k \in \mathbb{Z}$; tam sayı değerli fonksiyon hiçbir yerde türevlenebilir değildir, gradyanı tanımsızdır. Aynı topolojik kararlılığı denetleyen ve türevlenebilir olan büyüklük Laplasyen'in spektrumudur (basit özdeğerlerde analitik).

### T10 — 𝒪₆ Tasavvur: Homoloji GRUBU ile ağırlık dizeyi tensörlenemez

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_kulli_formulasyon, nefs_i_mudrike_41_meleke

**Metinde:**

```latex
H_p\left(\mathcal{S}_{[1:t]}\right) \otimes W_{\text{macro}}
```

**Tashih:**

```latex
H_p\left(\mathcal{S}_{[1:t]}; \mathbb{R}\right) \otimes W_{\text{macro}}
```

**Gerekçe.** $H_p(\cdot;\mathbb{Z})$ bir değişmeli GRUPTUR; burulma (torsion) taşıyabilir ve gerçel bir ağırlık dizeyiyle tensörlenmesi ulam hatasıdır. Gerçel katsayılarla $H_p(\cdot;\mathbb{R})$ bir vektör uzayıdır ve çarpım anlam kazanır.

### T11 — 𝒪₇ Mana: ``RicciFlatTensor`` diye bir işlemci yok; gradyan eğriliğe eşitlenemez

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_kulli_formulasyon

**Metinde:**

```latex
\nabla \mu &= \text{RicciFlatTensor}(S_t)
```

**Tashih:**

```latex
\text{Ric}(g) &= 0 \iff R_{ij} = 0 \quad (n \ge 3 \text{ iken } R_{ij} - \tfrac{1}{2}R g_{ij} = 0 \text{ ile denk})
```

**Gerekçe.** $\nabla\mu$ bir eş-vektördür, $\text{Ric}$ ise $(0,2)$-tensör; eşitlenemezler. Kastedilen şart, semantik manifoldun Ricci-düz olmasıdır. Ayrıca $n = 2$'de Einstein tensörü ÖZDEŞ olarak sıfırdır, yani $R_{ij}-\frac12 Rg_{ij}=0$ orada hiçbir şey söylemez; Ricci-düzlüğün doğru ifadesi $R_{ij}=0$'dır.

### T12 — 𝒪₇ Mana: ``RicciFlatTensor`` diye bir işlemci yok

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_41_meleke

**Metinde:**

```latex
\nabla \mu &= \text{RicciFlatTensor}(S_t) \implies R_{ij} - \frac{1}{2} R g_{ij} = 0
```

**Tashih:**

```latex
\text{Ric}(g) &= 0 \iff R_{ij} = 0 \quad (n \ge 3 \text{ iken } R_{ij} - \tfrac{1}{2}R g_{ij} = 0 \text{ ile denk})
```

**Gerekçe.** Aynı sebep (bkz. T11).

### T13 — 𝒪₂₂ İllet: $\dot{I}_t$ bir vektördür, DAG değil

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_kulli_formulasyon, nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\dot{I}_t &= \text{GELU}\left( (S_t W_i) \odot (H_t W_{hi}) \right) \in \mathcal{G}_{\text{neden}}
```

**Tashih:**

```latex
\dot{I}_t &= \text{GELU}\left( (S_t W_i) \odot (H_t W_{hi}) \right) \in \mathbb{R}^{d_{\text{sem}}} \quad (\text{nedensel KOD; çizgenin kendisi } A_{\text{neden}})
```

**Gerekçe.** GELU çıktısı bir vektördür; bir yönlendirilmiş asiklik çizge değil. Yanlış tip beyanı belgede üç yerde daha taşıyıcıdır: 𝒪₇'de $\langle S_t, \dot{I}_t\rangle_{\mathcal{S}}$ iç çarpımı, 𝒪₁₂'de $[S_t \oplus \dot{I}_t \oplus G_t]$ birleştirmesi ve 𝒪₃₃'te $\beta \dot{I}_t$ terimi ancak $\dot I_t$ vektör ise anlamlıdır. Çizge ayrı bir nesnedir ve zaten $A_{\text{neden}}$ adıyla var.

### T14 — 𝒪₃₃ Muhakeme: Skaler integrale vektör eklenmiş

*tür:* boyut uyuşmazlığı &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_kulli_formulasyon

**Metinde:**

```latex
\alpha \langle S_t, G_t \rangle + \beta \dot{I}_t - \gamma \text{Tenakuz}(S_t)
```

**Tashih:**

```latex
\alpha \langle S_t, G_t \rangle + \beta \|\dot{I}_t\| - \gamma \text{Tenakuz}(S_t)
```

**Gerekçe.** İntegral altındaki ifade skaler olmalı; $\langle S_t,G_t\rangle$ ve $\text{Tenakuz}$ skaler iken $\dot I_t$ vektördür.

### T15 — 𝒪₃₃ Muhakeme: Skaler integrale vektör eklenmiş

*tür:* boyut uyuşmazlığı &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_41_meleke

**Metinde:**

```latex
\alpha \langle S_t, G_t \rangle + \beta \dot{I}_t - \gamma \text{Tenakuz}(S_t) \Big] dt
```

**Tashih:**

```latex
\alpha \langle S_t, G_t \rangle + \beta \|\dot{I}_t\| - \gamma \text{Tenakuz}(S_t) \Big] dt
```

**Gerekçe.** Aynı sebep (bkz. T14).

### T16 — 𝒪₈ Tahlil: HSIC'in merkezleme dizeyi tanımsız bırakılmış

*tür:* tanımsız ifade &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_41_meleke

**Metinde:**

```latex
\text{Tr}(K_{\text{cins}} H_{\text{ort centrality}} L_{\text{fasıl}} H_{\text{ort centrality}})
```

**Tashih:**

```latex
\text{Tr}(K H L H), \quad H = I_n - \tfrac{1}{n}\mathbf{1}\mathbf{1}^T \ (\text{merkezleme dizeyi})
```

**Gerekçe.** ``$H_{\text{ort centrality}}$'' bir nesne adı değil; HSIC kestiricisinde $H$ merkezleme dizeyidir ve tanımlanmadan kestirici belirsizdir. Merkezleme olmadan ölçüt bağımsızlıkta sıfırlanmaz.

### T17 — 𝒪₈ Tahlil: HSIC'in merkezleme dizeyi tanımsız bırakılmış

*tür:* tanımsız ifade &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\text{Tr}(K_{\text{cins}} H_{\text{ort}} L_{\text{fasıl}} H_{\text{ort}})
```

**Tashih:**

```latex
\text{Tr}(K H L H), \quad H = I_n - \tfrac{1}{n}\mathbf{1}\mathbf{1}^T \ (\text{merkezleme dizeyi})
```

**Gerekçe.** Aynı sebep (bkz. T16).

### T18 — 𝒪₉ Terkip: Metrik geri çekiminde serbest indis

*tür:* tanımsız ifade &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_kulli_formulasyon, nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
g_{\mu\nu}^{(\text{yeni})} &= \sum_{i,j} \frac{\partial x^a}{\partial y^\mu} \frac{\partial x^b}{\partial y^\nu} g_{ab}^{(i)}
```

**Tashih:**

```latex
g_{\mu\nu}^{(\text{yeni})} &= \sum_{i=1}^m w_i \frac{\partial x^a}{\partial y^\mu} \frac{\partial x^b}{\partial y^\nu} g_{ab}^{(i)} \quad (a, b \text{ üzerinden Einstein toplamı})
```

**Gerekçe.** $j$ toplam indisi olarak yazılmış fakat sağ tarafta hiç geçmiyor; yazıldığı gibi toplam $m$ katına çıkar. Ayrıca her bileşenin geri çekimi, o bileşenin terkipteki ağırlığı $w_i$ ile alınmalıdır.

### T19 — 𝒪₁₀ Tezat: Zıtlık operatörü involüsyon değil

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_kulli_formulasyon

**Metinde:**

```latex
\mathbf{M}_{\text{tezat}} &= \mathbf{S} \cdot \mathbf{W}_{\text{opp}} \cdot \mathbf{S}^T
```

**Tashih:**

```latex
\mathbf{M}_{\text{tezat}} &= \mathbf{S} \mathbf{W}_{\text{opp}} \mathbf{S}^T, \quad \mathbf{W}_{\text{opp}} = 2\hat{\mathbf{v}}_{\text{zıt}}\hat{\mathbf{v}}_{\text{zıt}}^T - I, \ \|\hat{\mathbf{v}}_{\text{zıt}}\| = 1
```

**Gerekçe.** ``Zıtlık'' operatörünün iki kere uygulanınca aslına dönmesi beklenir ($\mathbf{W}^2 = I$) ve normu korumalıdır. Householder biçimi bunu sağlar; $-I + \mathbf{v}\mathbf{v}^T$ ise ancak $\|\mathbf{v}\|^2 = 2$ iken sağlar, ki bu şart metinde yok.

### T20 — 𝒪₁₀ Tezat: Zıtlık operatörü involüsyon değil

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_41_meleke

**Metinde:**

```latex
\mathbf{W}_{\text{opp}} &= -I_{d \times d} + \mathbf{v}_{\text{zıt}} \mathbf{v}_{\text{zıt}}^T
```

**Tashih:**

```latex
\mathbf{W}_{\text{opp}} &= 2\hat{\mathbf{v}}_{\text{zıt}} \hat{\mathbf{v}}_{\text{zıt}}^T - I_{d \times d}, \quad \|\hat{\mathbf{v}}_{\text{zıt}}\| = 1 \ \Rightarrow \ \mathbf{W}_{\text{opp}}^2 = I
```

**Gerekçe.** Aynı sebep (bkz. T19).

### T21 — 𝒪₁₁ Tenakuz: Çelişki çekirdeği iki şartı birden sağlamalı

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\langle S_i, S_j \rangle_{\text{çelişki}} &= S_i^T \mathbf{W}_{\text{tenakuz}} S_j
```

**Tashih:**

```latex
\langle S_i, S_j \rangle_{\text{çelişki}} &= -S_i^T (A^T A) S_j \quad \Rightarrow \quad \langle S,S \rangle \le 0, \ \ \langle S, -S \rangle = \|AS\|^2
```

**Gerekçe.** Tenakuzun tarifi iki şart dayatır: (i) hiçbir önerme kendisiyle çelişmez, (ii) her önerme kendi NAKÎZİYLE çelişir. Kısıtsız $\mathbf{W}$ ikisini de sağlamaz. Ters simetrik $\mathbf{W}$ (i)'yi sağlar fakat (ii)'yi YIKAR: $S^T\mathbf{W}(-S) = 0$. Yarı-negatif $\mathbf{W} = -A^TA$ ikisini birden sağlar. Bu, ``nefs'' modülünde önce ters simetrik kurulup sınamayla yakalanan ve ölçümle düzeltilen hatadır.

### T22 — 𝒪₁₁ Tenakuz: Gösterge klasik olarak $\neg S_i$'ye denk

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\mathbb{I}_{\text{tenakuz}} &= \mathbb{I}\left( (S_i \implies S_j) \land (S_i \implies \neg S_j) \right)
```

**Tashih:**

```latex
\mathbb{I}_{\text{tenakuz}} &= \mathbb{I}\left( S_i \land S_j \vdash \bot \right) \quad (\text{eski hâl} \equiv \neg S_i, \text{ yani } S_i\text{'nin YANLIŞLIĞI})
```

**Gerekçe.** Klasik mantıkta $(S_i \to S_j) \land (S_i \to \neg S_j) \equiv \neg S_i$. Yani yazılan gösterge, $S_i$ ile $S_j$ arasındaki çelişkiyi değil, $S_i$'nin yanlış olduğunu tespit eder -- $S_i$ yanlışsa iki gerektirme de boşluktan doğrudur.

### T23 — 𝒪₁₃ Tasdik: Tasdik mührü ERİŞİLEMEZ bir eşikte

*tür:* erişilemez eşik &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_kulli_formulasyon, nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
T_t &= \sigma\left( \text{CosSim}(M_t^{(\mathcal{K})} W_t, G_t) - \text{Tenakuz}(M_t^{(\mathcal{K})}, S_t, H_t) \right) \in [0, 1]
```

**Tashih:**

```latex
T_t &= \sigma\left( \beta_T \left[ \text{CosSim}(M_t^{(\mathcal{K})} W_t, G_t) - \text{Tenakuz}(M_t^{(\mathcal{K})}, S_t, H_t) \right] \right) \in (0,1), \quad \beta_T \ge 4
```

**Gerekçe.** $\text{CosSim} \le 1$ ve $\text{Tenakuz} \ge 0$ olduğundan $\sigma$'nın argümanı $1$'i aşamaz, dolayısıyla $T_t \le \sigma(1) = 0{,}731$. Buna karşılık mühür şartı $\mathbb{I}(T_t \ge 1-\epsilon)$, $\epsilon = 0{,}05$ için $T_t \ge 0{,}95$ ister. Yani tasdik mührü HİÇBİR ZAMAN vurulamaz. Kazanç katsayısı $\beta_T$ şarttır; $\beta_T \ge 4$ eşiği erişilebilir kılar.

### T24 — 𝒪₃₀ Tahkik: Aynı erişilemez eşik kusuru

*tür:* erişilemez eşik &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_kulli_formulasyon, nefs_i_mudrike_41_meleke

**Metinde:**

```latex
T_{\text{tahkik}} &= \sigma\left( \text{CosSim}(S_{\text{tahkik}}, S_{\text{asıl}}) \right)
```

**Tashih:**

```latex
T_{\text{tahkik}} &= \sigma\left( \beta_T \left[ \text{CosSim}(S_{\text{tahkik}}, S_{\text{asıl}}) - \theta \right] \right), \quad \beta_T \ge 4
```

**Gerekçe.** $\text{CosSim} \in [-1,1]$ olduğundan $\sigma(\text{CosSim}) \in [0{,}269,\ 0{,}731]$. $\mathbb{I}(T > 1-\delta)$ şartı $\delta < 0{,}269$ için hiç sağlanamaz (bkz. T23).

### T25 — 𝒪₁₃ Tasdik: Skaler türeve vektör çarpanı eklenmiş

*tür:* boyut uyuşmazlığı &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\nabla_T \mathcal{L} &= (T_t - T_{\text{hedef}}) \cdot S_t
```

**Tashih:**

```latex
\frac{\partial \mathcal{L}}{\partial T_t} &= T_t - T_{\text{hedef}}, \qquad \nabla_{S_t} \mathcal{L} = (T_t - T_{\text{hedef}}) \, \nabla_{S_t} T_t
```

**Gerekçe.** $\mathcal{L} = \tfrac12 (T_t - T_{\text{hedef}})^2$ için $T_t$'ye göre türev SKALERDİR. $S_t$ çarpanı zincir kuralından gelir ve $\nabla_{S_t}\mathcal{L}$'ye aittir; ikisi karışmış.

### T26 — 𝒪₁₅ Merak: Olasılığın varyansı değil, $S_t$'nin şartlı varyansı

*tür:* tanımsız ifade &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_kulli_formulasyon

**Metinde:**

```latex
\mathcal{H}_{\text{bilgisizlik}}(S_t) &= \text{Var}(P(S_t \mid H_t))
```

**Tashih:**

```latex
\mathbb{V}_{\text{bilgisizlik}}(S_t) &= \text{Var}_{P(\cdot \mid H_t)}[S_t]
```

**Gerekçe.** ``Bir olasılığın varyansı'' tanımsızdır; kastedilen, $S_t$'nin $P(\cdot \mid H_t)$ altındaki varyansıdır. Ayrıca $\mathcal{H}$ simgesi aynı belgede (𝒪₈, 𝒪₁₇, 𝒪₂₁) ENTROPİ için ayrılmış; varyans için kullanılması iki ayrı büyüklüğü karıştırır.

### T27 — 𝒪₁₅ Merak: Olasılığın varyansı değil, $S_t$'nin şartlı varyansı

*tür:* tanımsız ifade &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\mathcal{H}_{\text{bilgisizlik}}(S_t) &= \text{Var}(P(S_t \mid H_t)) = \mathbb{E}[(S_t - \mu_S)^2 \mid H_t]
```

**Tashih:**

```latex
\mathbb{V}_{\text{bilgisizlik}}(S_t) &= \text{Var}_{P(\cdot \mid H_t)}[S_t] = \mathbb{E}[(S_t - \mu_S)^2 \mid H_t]
```

**Gerekçe.** Aynı sebep (bkz. T26). Sağ taraftaki ifade zaten varyanstır; yanlış olan sol taraftaki yazılış ve simgedir.

### T29 — 𝒪₁₇ İhtimal: Laplace kaidesi bir toplama terimi değil

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\mathbf{L}_{\text{Laplace}} &= P_0(S) + \frac{k+1}{n+2}
```

**Tashih:**

```latex
\hat{P}_{\text{Laplace}}(S) &= \frac{n_S + \alpha}{n + \alpha |\mathcal{S}|}, \quad \alpha = 1 \ \Rightarrow \ \frac{k+1}{n+2} \ (\text{ikili hâl})
```

**Gerekçe.** $\frac{k+1}{n+2}$ (ardıllık kaidesi) kestirimin KENDİSİDİR. Bir önsele eklenirse ortaya çıkan büyüklük ne olasılıktır ne de normalizedir. Genel hâli toplamalı düzleştirmedir (additive smoothing) ve $\alpha=1$'de ardıllık kaidesine iner.

### T30 — 𝒪₁₈ Kıyas: Vektörler arasında kapsama ($\subset$) tanımsız

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\mathbb{I}(S_{\text{cüz'î}} \subset S_{\text{küllî}}) \cdot P(S_{\text{küllî}})
```

**Tashih:**

```latex
\mathbb{I}\big(\text{span}(S_{\text{cüz'î}}) \subseteq \text{span}(S_{\text{küllî}})\big) \cdot P(S_{\text{küllî}})
```

**Gerekçe.** $\subset$ kümeler arasındadır. Cüz'înin küllî altına girmesi, gerdikleri alt uzayların kapsanmasıdır.

### T31 — 𝒪₂₀ Teşbih: Vektörün izi alınamaz

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\mathbf{P}_{\text{ortak\_altuzay}} &= \text{Proj}_{\mathcal{S}_A \cap \mathcal{S}_B}(S_A) \\
```

**Tashih:**

```latex
\mathbf{P}_{\text{ortak}} &= \text{ortak alt uzaya dik izdüşüm DİZEYİ}, \quad \Pi_{\text{ortak}}(S_A) = \mathbf{P}_{\text{ortak}} S_A \\
```

**Gerekçe.** $\text{Proj}_V(S_A)$ bir VEKTÖRDÜR; bir satır sonra izi alınıyor, oysa iz dizeylere aittir. İz, izdüşüm DİZEYİNE aittir ve değeri tam olarak ortak alt uzayın boyutudur -- vech-i şebeh ölçüsü olarak da aranan budur.

### T32 — 𝒪₂₀ Teşbih: Benzerlik skoru izdüşüm dizeyinin izidir

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\text{BenzerlikSkoru} &= \text{Tr}(\mathbf{P}_{\text{ortak\_altuzay}})
```

**Tashih:**

```latex
\text{BenzerlikSkoru} &= \text{Tr}(\mathbf{P}_{\text{ortak}}) = \dim(\mathcal{S}_A \cap \mathcal{S}_B)
```

**Gerekçe.** T31'in doğrudan devamı: izdüşüm DİZEYİNİN izi, ortak alt uzayın boyutuna eşittir; vech-i şebeh ölçüsü olarak aranan da budur.

### T33 — 𝒪₂₁ Tefekkür: İŞARET HATASI: akış gayeden uzaklaştırıyor

*tür:* işaret hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_kulli_formulasyon, nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\dot{S}_t &= \nabla \mathcal{V}_{\text{tefekkür}}(S_t)
```

**Tashih:**

```latex
\dot{S}_t &= -\nabla \mathcal{V}_{\text{tefekkür}}(S_t) \quad (\text{İNİŞ; artı işaret gayeden UZAKLAŞTIRIR})
```

**Gerekçe.** $\mathcal{V}_{\text{tefekkür}} = \tfrac12\|S-G_t\|^2 + \lambda\,\text{Tenakuz}$ bir maliyettir. Artı işaretli akış gradyan ÇIKIŞIDIR: hem gayeden uzaklaşır hem tenakuzu artırır. Metnin kendi tarifiyle (tefekkür neticeye yaklaştırır) çelişir.

### T34 — 𝒪₂₁ Tefekkür: İŞARET HATASI: entropinin eksisi düşmüş

*tür:* işaret hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_kulli_formulasyon, nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\mathcal{H}_{\text{tefekkür}} &= \int_{\mathcal{S}} P(S_t) \log P(S_t) dS
```

**Tashih:**

```latex
\mathcal{H}_{\text{tefekkür}} &= -\int_{\mathcal{S}} P(S_t) \log P(S_t) \, dS
```

**Gerekçe.** Entropi eksi işaretlidir. Aynı belge 𝒪₁₇'de $-\int P \log P$ diye DOĞRU yazıyor; iki yer birbiriyle çelişiyor.

### T35 — 𝒪₂₂ İllet: Nedensel karmaşıklık DAG üzerinde ÖZDEŞ SIFIR

*tür:* kendi tanım kümesinde özdeş sıfır / özdeşlik &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_kulli_formulasyon, nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\mathcal{C}_{\text{nedensel}} &= \text{Trace}(A_{\text{neden}}) - \log \det(I + A_{\text{neden}})
```

**Tashih:**

```latex
\mathcal{C}_{\text{nedensel}} &= \|A_{\text{neden}}\|_1 \quad (\text{eski hâl DAG'da} \equiv 0: \ \text{Tr}(A) = 0, \ \det(I+A) = 1)
```

**Gerekçe.** Bir DAG'ın komşuluk dizeyi topolojik sıralamada üst üçgen, yani nilpotenttir. O hâlde $\text{Tr}(A) = 0$ ve $I+A$ birim köşegenli üst üçgen olduğundan $\det(I+A) = 1$, $\log\det = 0$. Yani ifade kendi tanım kümesinde özdeş olarak sıfırdır ve hiçbir şey ölçmez. ``nefs'' modülünde sayısal olarak da 0 ölçüldü.

### T36 — 𝒪₂₂ İllet: Softmax dizeyi DAG değildir

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\dot{I}_{\text{kebîr}} &= \text{DAG\_Sentezi}(S_{\text{kebîr}}, H_{[1:t]}) = \text{Softmax}\left( \frac{S_{\text{kebîr}} A_{\text{neden}} S_{\text{kebîr}}^T}{\sqrt{d_{\text{sem}}}} \right)
```

**Tashih:**

```latex
A_{\text{neden}} &= \Pi_{\prec} \left[ \text{Softmax}\left( \frac{S_{\text{kebîr}} W_{\text{dag}} S_{\text{kebîr}}^T}{\sqrt{d_{\text{sem}}}} \right) \right], \quad \Pi_{\prec} = \text{topolojik sıraya göre üst üçgen maske}
```

**Gerekçe.** Softmax çıktısı yoğun, satır-stokastik ve köşegeni sıfırdan farklıdır -- yani her düğümün kendine kenarı vardır. Böyle bir dizey hiçbir zaman asiklik değildir. Asiklik DAYATILMALIDIR: bir topolojik sıra sabitlenip yalnız o sırayla uyumlu girdiler bırakılır; o zaman $h(A) = \text{Tr}(e^{A \circ A}) - d = 0$ inşa gereği sağlanır. Ayrıca $A_{\text{neden}}$ hem tanımın girdisi hem çıktısı olarak kullanılmış (döngüsel tanım).

### T37 — 𝒪₂₃ Mantık: Geçerlilik ile tutarlılık aynı şey değil

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_kulli_formulasyon, nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\text{Geçerlilik}(R) &= \mathbb{I}(\text{Tenakuz}(R) = 0)
```

**Tashih:**

```latex
\text{Geçerlilik}(P_1, \dots, P_n \vdash Q) &= \mathbb{I}\big( \models (P_1 \land \dots \land P_n) \to Q \big)
```

**Gerekçe.** Çelişki barındırmayan bir çıkarım geçerli olmak zorunda değildir. Geçerlilik, gerektirmenin HER modelde doğru olmasıdır; tutarlılık ise kesinlikle daha zayıf bir şarttır. İkisi özdeşleştirilirse geçersiz çıkarımlar geçerli sayılır.

### T38 — 𝒪₂₆ Temkin: Dizey ile örneklem toplanamaz

*tür:* boyut uyuşmazlığı &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_kulli_formulasyon, nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\mathbf{K}_{\text{temkin}} &= \mathbf{S}_t + \mu_{\text{emniyet}} \cdot \mathbf{\Sigma}_{\text{gürültü}}
```

**Tashih:**

```latex
\mathbf{K}_{\text{temkin}} &= \mathbf{S}_t + \mu_{\text{emniyet}} \, \xi, \quad \xi \sim \mathcal{N}(0, \mathbf{\Sigma}_{\text{gürültü}})
```

**Gerekçe.** $\mathbf{S}_t \in \mathbb{R}^{n \times d}$ iken $\mathbf{\Sigma}_{\text{gürültü}} = \mathbb{E}[\delta\delta^T] \in \mathbb{R}^{d\times d}$; toplanamazlar. Sarsma, o kovaryanstan çekilen bir ÖRNEKLEMLE girer.

### T39 — 𝒪₂₇ Tetkik: Skalerin LayerNorm'u tanımsız

*tür:* tanımsız ifade &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_kulli_formulasyon, nefs_i_mudrike_41_meleke

**Metinde:**

```latex
\text{Skor}_{\text{tetkik}} &= \text{LayerNorm}\left(\sum \text{KusurHaritası}\right)
```

**Tashih:**

```latex
\text{Skor}_{\text{tetkik}} &= \text{LayerNorm}\Big( \textstyle\sum_{i} \text{KusurHaritası}_{i\cdot} \Big) \in \mathbb{R}^{d_{\text{sem}}}
```

**Gerekçe.** İndissiz $\sum$ bütün girdileri toplar ve skaler verir. LayerNorm ortalamayı çıkarıp standart sapmaya böler; skalerde ikisi de dejenere olur ($0/0$). Toplam TEK eksen üzerinden alınmalı ki sonuç vektör kalsın.

### T40 — 𝒪₂₇ Tetkik: Tensör çarpımı yerine Hadamard çarpımı

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_kulli_formulasyon, nefs_i_mudrike_41_meleke

**Metinde:**

```latex
|\delta S_{t, \text{kılcal}} - S_{\text{ideal}}| \otimes W_{\text{tetkik}}
```

**Tashih:**

```latex
|\delta S_{t, \text{kılcal}} - S_{\text{ideal}}| \odot W_{\text{tetkik}}
```

**Gerekçe.** $\otimes$ mertebeyi yükseltir ve bir sonraki satırda toplanan nesneyle uyuşmaz; kastedilen ve boyutların izin verdiği işlem öge-öge çarpımdır.

### T41 — 𝒪₂₉ Teyit: Bayes güncellemesi ŞARTLI bağımsızlık ister

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_kulli_formulasyon, nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
E_{\text{bağımsız}} &= \text{Kanal}_2(X_t) \quad (\text{Kanal}_1 \perp \text{Kanal}_2)
```

**Tashih:**

```latex
E_{\text{bağımsız}} &= \text{Kanal}_2(X_t), \quad E_1 \perp\!\!\!\perp E_2 \mid H \quad (\text{ŞARTLI bağımsızlık})
```

**Gerekçe.** Bir satır aşağıdaki $P(H\mid E_1,E_2) = \frac{P(E_2\mid H)P(H\mid E_1)}{P(E_2\mid E_1)}$ güncellemesi tam olarak $E_1 \perp\!\!\!\perp E_2 \mid H$ şartı altında geçerlidir. Metnin yazdığı MARJİNAL bağımsızlık ne yeterlidir ne de -- iki kanal da $H$ hakkında bilgi taşıyorken -- şartlı bağımsızlıkla genelde bir arada bulunabilir.

### T42 — 𝒪₂₉ Teyit: Kovaryans sınırsız; bağımsızlık düzeyi negatife kaçar

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\text{BağımsızlıkDüzeyi} &= 1 - |\text{Cov}(E_1, E_2)|
```

**Tashih:**

```latex
\text{BağımsızlıkDüzeyi} &= 1 - |\rho(E_1, E_2)| \in [0,1], \quad \rho = \frac{\text{Cov}(E_1,E_2)}{\sigma_{E_1}\sigma_{E_2}}
```

**Gerekçe.** Kovaryans normalize değildir ve $1$'i aşabilir; o zaman ``bağımsızlık düzeyi'' negatif olur ve bir sonraki satırdaki çarpım teyit skorunu ters çevirir. Korelasyon katsayısı $[-1,1]$'de sınırlıdır.

### T43 — 𝒪₃₁ Tedebbür: ArgMax değişkeni amaç fonksiyonunda geçmiyor

*tür:* tanımsız ifade &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\text{ArgMax}_a \left( \mathcal{V}_{\text{akıbet}}(S_t) - \gamma \mathcal{Risk}_{\text{tedebbür}} \right)
```

**Tashih:**

```latex
\text{ArgMax}_a \left( \mathcal{V}_{\text{akıbet}}(S_t, a) - \gamma \mathcal{Risk}_{\text{tedebbür}}(S_t, a) \right)
```

**Gerekçe.** Her iki terim de $a$'dan bağımsız yazılmış; o hâlde argmax boş bir işlemdir ve emniyetli hamle seçilemez.

### T44 — 𝒪₃₂ Şek-Zan-Yakîn: Makam parçalanışında BOŞLUK

*tür:* tanımsız ifade &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_kulli_formulasyon, nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\text{Yakîn } (\%100), & P_{\text{idrak}} \ge 1 - \epsilon_{\text{yakîn}}
```

**Tashih:**

```latex
\text{Yakîn } (\%100), & P_{\text{idrak}} \ge 1 - \epsilon_{\text{yakîn}} \\
\text{Vehim } (\%1-\%49), & P_{\text{idrak}} < 0.5 - \epsilon_{\text{şek}}
```

**Gerekçe.** Yazılan üç şart $P_{\text{idrak}} < 0{,}5 - \epsilon_{\text{şek}}$ aralığını KAPSAMIYOR; orada $\text{Makam}$ tanımsız kalıyor. Aleyhte zan (Vehim) eklenince parçalanış hem TAM hem AYRIK olur ve $P$ arttıkça makam gerilemez.

### T45 — 𝒪₃₅ Tefsir: Dikkat ağırlıkları murâd değildir

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_kulli_formulasyon

**Metinde:**

```latex
\text{Softmax}\left( \frac{S_{\text{müphem}} W_{\text{tefsir}} \cdot [\text{Siyak} \oplus \text{Sibak}]^T}{\sqrt{d}} \right)
```

**Tashih:**

```latex
\text{Softmax}\left( \frac{S_{\text{müphem}} W_{\text{tefsir}} [\text{Siyak} \oplus \text{Sibak}]^T}{\sqrt{d}} \right) [\text{Siyak} \oplus \text{Sibak}] W_v
```

**Gerekçe.** Softmax tek başına yalnız AĞIRLIK verir; murâd, bağlamın o ağırlıklarla harmanıdır. Değer çarpanı olmadan sol taraf bir mana vektörü değil, bir olasılık dağılımıdır. 41-meleke nüshasında bu çarpan zaten var; iki nüsha çelişiyor.

### T46 — 𝒪₃₇ Fesâhat: Skor aşağıdan sınırsız

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_kulli_formulasyon, nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\text{FesâhatScore}(N_t) &= 1 - \left[ \mu_1 \text{Tenâfür}(N_t) + \mu_2 \text{Garâbet}(N_t) + \mu_3 \text{Ta'kîd}(N_t) \right]
```

**Tashih:**

```latex
\text{FesâhatScore}(N_t) &= 1 - \left[ \mu_1 \tilde{T}(N_t) + \mu_2 \tilde{G}(N_t) + \mu_3 \tilde{K}(N_t) \right] \in [0,1], \quad \tilde{\cdot} = \tfrac{x}{1+x} \in [0,1], \ \textstyle\sum_i \mu_i = 1
```

**Gerekçe.** Üç kusur terimi de yukarıdan sınırsızdır (özellikle $\text{Garâbet} = -\sum \log P$ uzunlukla büyür), dolayısıyla skor aşağıdan sınırsızdır ve bir ``derece'' olmaktan çıkar. ``nefs'' modülünde sıkıştırmasız hâli $-18$ ölçüldü. Her terim $[0,1]$'e sıkıştırılıp ağırlıklar toplamı 1 yapılınca skor gerçekten $[0,1]$'de kalır.

### T47 — 𝒪₃₇ Fesâhat: Frekans olasılık değildir

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
P_{\text{lügat}}(y) &= \text{Frekans}_{\text{korpus}}(y)
```

**Tashih:**

```latex
P_{\text{lügat}}(y) &= \frac{\text{Frekans}_{\text{korpus}}(y)}{\sum_{w} \text{Frekans}_{\text{korpus}}(w)}
```

**Gerekçe.** Normalize edilmemiş bir frekans $1$'i aşabilir; o zaman $-\log P$ NEGATİF olur ve garâbet, kusur ölçüsü olmaktan çıkıp ödüle döner.

### T48 — 𝒪₃₉ Belâgat: $\exp$ Lie CEBRİNDEN Lie GRUBUNA gider

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
R_{\text{belâgat}} &= \exp\left( \theta \mathbf{X}_{\text{muktezâ\_hâl}} \right) \in \mathfrak{g}
```

**Tashih:**

```latex
\mathbf{X}_{\text{muktezâ\_hâl}} \in \mathfrak{g}, \quad R_{\text{belâgat}} &= \exp(\theta \mathbf{X}_{\text{muktezâ\_hâl}}) \in G = \exp(\mathfrak{g})
```

**Gerekçe.** Üstel eşleme $\exp : \mathfrak{g} \to G$ cebirden GRUBA gider. $\exp(\theta X)$ bir grup ögesidir, cebir ögesi değil. ($X$ ters simetrik seçilirse $R \in SO(d)$ olur ve normu korur -- ``tasarruf''un muhtaç olduğu da budur.)

### T49 — 𝒪₄₀ Sanat: Simetrik harmoni normalize değil, negatife düşüyor

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_41_meleke, nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\text{SimetrikHarmoni}(Y) &= 1 - \| Y - Y^T \|_{\mathcal{F}}
```

**Tashih:**

```latex
\text{SimetrikHarmoni}(Y) &= 1 - \frac{\| Y - Y^T \|_{\mathcal{F}}}{2\|Y\|_{\mathcal{F}}} \in [0,1], \quad Y \text{ kare}
```

**Gerekçe.** İki kusur var. (i) Payda yok: ölçü $Y$'nin BÜYÜKLÜĞÜNE bağlı olur, oysa ahenk bir orandır -- aynı şekilli iki dizeden büyük olanı ``daha ahenksiz'' görünür. (ii) $\|Y-Y^T\|^2 = 2\|Y\|^2 - 2\langle Y, Y^T\rangle \le 4\|Y\|^2$ olduğundan yalnız $\|Y\|$'a bölmek ölçüyü $[-1,1]$'e taşır; ``ahenk'' negatif olabilir (``nefs'' modülünde $-0{,}351$ ölçüldü). $2\|Y\|$ ile bölününce ölçü simetrik dizede tam 1, ters simetrik dizede tam 0'dır.

### T50 — 𝒪₁ Müşahede (HoTT): Glue $\beta$-kuralı gösterge diye yazılmış

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\mathbf{1}_{\text{müşahede}} &= \text{unglue}(\text{glue } X_t \, [\dots])
```

**Tashih:**

```latex
\text{unglue}\big(\text{glue } X_t \, [\varphi \mapsto (t, e)]\big) &\equiv X_t \quad (\text{Glue } \beta\text{-kuralı})
```

**Gerekçe.** Kübik tip teorisinde $\text{unglue}(\text{glue } a\,[\dots]) \equiv a$ TANIMSAL bir denkliktir; yani sol taraf $X_t$'nin kendisidir, bir gösterge ($\mathbf{1}$) değil. Özdeşlik olarak yazılınca doğru ve mânâlı olur. Bu kural bu depoda MAKİNEYLE denetleniyor (\texttt{omega\_kategori\_nbe}).

### T51 — 𝒪₁ Müşahede (HoTT): Sabit çizgide $\text{transp}$ özdeşliktir, süzgeç değil

*tür:* kendi tanım kümesinde özdeş sıfır / özdeşlik &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_hott_topos

**Metinde:**

```latex
X_{t, \text{süzülmüş}} &= \text{transp}^i (\lambda i. \mathcal{X}) \, \varphi \, X_t
```

**Tashih:**

```latex
X_{t, \text{süzülmüş}} &= X_t \odot \sigma(W_{\text{süzgeç}} X_t); \quad \text{transp}^i (\lambda i.\, \mathcal{X}) \, \varphi \, X_t \equiv X_t \ (\text{SABİT çizgi})
```

**Gerekçe.** Çizgi sabit olduğunda ($\lambda i.\,\mathcal{X}$) taşıma tanımsal olarak özdeşliktir: $\text{transp}^i (\lambda i. A)\,\varphi\,u \equiv u$. Yani yazılan ifade hiçbir şey süzmez. Gerçek süzgeç 41-meleke nüshasındaki kapı çarpanıdır.

### T52 — 𝒪₄ Tertip (HoTT): $\simeq$ TİPLER arasındadır, terimler arasında değil

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\text{Equiv}_{\text{tertip}} &= (\mathbf{Z}_{\text{ham}} \simeq \mathbf{Z}_{\text{düzenli}}) \in \mathbf{U}
```

**Tashih:**

```latex
\sigma_\pi : \mathcal{H}^N &\simeq \mathcal{H}^N \in \mathbf{U} \quad (\text{permütasyon tersinir} \Rightarrow \text{tertip bilgi kaybetmez})
```

**Gerekçe.** $\simeq$ tipler arası denkliktir; $\mathbf{Z}_{\text{ham}}$ ve $\mathbf{Z}_{\text{düzenli}}$ ise TERİMDİR (ve zaten eşit değildirler -- tertip onları değiştirir). Tersinir olan, tip üzerindeki permütasyon etkisidir; kastedilen mânâyı taşıyan da odur.

### T53 — 𝒪₁₀ Tezat (HoTT): Türetilmiş kritik yer bir ögesi değil, KENDİSİDİR

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\text{Fiber}_{\text{tezat}} &= \text{Crit}(\Theta_{\text{tezat}}) \in \mathbf{R}\text{Crit}(f)
```

**Tashih:**

```latex
\mathbf{R}\text{Crit}(\Theta_{\text{tezat}}) &= \mathcal{S} \times^{h}_{d\Theta, \, T^*\mathcal{S}, \, 0} \mathcal{S} \quad (\text{homotopi lif çarpımı})
```

**Gerekçe.** $\mathbf{R}\text{Crit}(\Theta)$ bir NESNEDİR: $d\Theta$ ile sıfır kesitinin homotopi lif çarpımı. ``$\text{Crit}(\Theta) \in \mathbf{R}\text{Crit}(f)$'' hem nesneyi kendi ögesi yapıyor hem de alakasız bir $f$ getiriyor.

### T54 — 𝒪₁₁ Tenakuz (HoTT): Özdeşlik tipi $\mathbf{Prop}$ üzerinde değil

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\text{Path}_{\text{tenakuz}} &= (\text{Tenakuz}(S_i, S_j) =_{\mathbf{Prop}} \mathbf{0})
```

**Tashih:**

```latex
\text{Path}_{\text{tenakuz}} &= \big\| \text{Tenakuz}(S_i, S_j) =_{\mathbb{R}} 0 \big\| \in \mathbf{Prop}
```

**Gerekçe.** $\text{Tenakuz}$ gerçel değerlidir; özdeşlik tipi $\mathbb{R}$ üzerinde kurulur. $\mathbf{Prop}$'a inen şey o özdeşlik tipinin ÖNERMESEL KESMESİDİR ($\|\cdot\|$).

### T55 — 𝒪₁₃ Tasdik (HoTT): Univalence gerçel sayılara tatbik edilemez

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\text{Univalence}_{\text{tasdik}} &= (T_t \simeq 1) \simeq (S_t =_{\mathcal{S}} G_t)
```

**Tashih:**

```latex
\text{ua} : (A \simeq B) &\simeq (A =_{\mathcal{U}} B) \ (\text{TİPLER arası}); \quad \mathbf{1}_{\text{tasdik}} = 1 \iff \big\| S_t =_{\mathcal{S}} G_t \big\|
```

**Gerekçe.** Univalence aksiyomu TİPLER hakkındadır. $T_t \simeq 1$ iki gerçel sayı arasında bir tip denkliği değildir. Tasdikin doğru ifadesi, $\mathcal{S}$'deki bir yolun varlığına dair bir ÖNERMEDİR.

### T56 — Tebliğ §1.1: Serbest enerji $\ge 0$ değildir

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_fitrat_ve_topos

**Metinde:**

```latex
\mathcal{F}(X, S) &= \mathbb{E}_{q(S)} \left[ \ln q(S) - \ln p(X, S) \right] \ge 0
```

**Tashih:**

```latex
\mathcal{F}(X, S) &= \text{KL}\big( q(S) \,\|\, p(S \mid X) \big) - \ln p(X) \ \ge \ -\ln p(X)
```

**Gerekçe.** Değişimsel serbest enerji $-\ln p(X)$ ile alttan sınırlıdır, $0$ ile değil. $\mathcal{F} \ge 0$ ancak $p(X) \le 1$ iken, yani AYRIK $X$ için doğrudur; yoğunluklarda yanlıştır. Negatif olmayan büyüklük KL terimidir. (Ayrıca ``Viyana-Ayrışma'' diye bir ayrışma yoktur; ıraksama Kullback--Leibler'dir.)

### T57 — Tebliğ §1.2: ICP kesişimi YORDAYICI KÜMELER üzerinden alınır

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_fitrat_ve_topos

**Metinde:**

```latex
\bigcap_{e \in \mathcal{E}} \text{Supp}\left( P_e(Y \mid X_{\text{Sâbit}}) \right) &= X_{\text{Hakiki\_İllet}}
```

**Tashih:**

```latex
S^{\star} &= \bigcap \big\{ S \subseteq \{1,\dots,p\} : P_e(Y \mid X_S) \text{ her } e \in \mathcal{E} \text{ için AYNI} \big\} \ \subseteq \ \text{PA}(Y)
```

**Gerekçe.** Desteklerin (support) kesişimi bir SONUÇ kümesi verir; oysa aranan bir DEĞİŞKEN kümesidir. Invariant Causal Prediction (Peters--Bühlmann--Meinshausen), kabul edilen yordayıcı kümelerini kesiştirir ve netice gerçek ebeveyn kümesinin ALT KÜMESİDİR -- eşitlik değil, kapsama.

### T58 — Tebliğ §2.1: Ayrık taban üzerinde ``pürüzsüz lifli demet''

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_fitrat_ve_topos

**Metinde:**

```latex
\pi : \mathcal{S} &\longrightarrow \mathcal{N} \quad (\text{Lifli Demet})
```

**Tashih:**

```latex
\pi : \mathcal{S} \to \mathcal{N}, \quad \mathcal{S} &\cong \coprod_{w \in \mathcal{N}} \mathbf{Fib}_w \quad (\mathcal{N} \text{ AYRIK} \Rightarrow \text{demet} = \text{indeksli eş-çarpım})
```

**Gerekçe.** Token uzayı $\mathcal{N}$ ayrıktır. Ayrık taban üzerindeki bir lifli demet, liflerin ayrık birleşiminden ibarettir; ``pürüzsüzlük'' orada hiçbir şey söylemez. Pürüzsüzlük liflerin İÇİNDE yaşar ve öyle yazılmalıdır.

### T59 — Tebliğ §2.2: Sonsuz boyutlu lifin hacmi yoktur

*tür:* tanımsız ifade &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_fitrat_ve_topos

**Metinde:**

```latex
\text{ManaKapsamı}(w) &= \int_{\pi^{-1}(w)} d\text{vol}_{\mathcal{S}} = \text{TopolojikHacim}\left( \mathbf{Fib}_w \right)
```

**Tashih:**

```latex
\text{ManaKapsamı}(w) &= H\big[ P(S \mid w) \big] = -\int_{\pi^{-1}(w)} P(S \mid w) \log P(S \mid w) \, dS
```

**Gerekçe.** Aynı paragraf lifi ``sonsuz boyutlu'' ilân ediyor. Sonsuz boyutlu bir Banach uzayında öteleme değişmez, $\sigma$-sonlu ve aşikâr olmayan bir ölçü YOKTUR (Weil); dolayısıyla o integral tanımsızdır. Şartlı entropi mevcuttur ve aynı şeyi -- tek bir tokenin ne kadar mana taşıdığını -- ölçer.

### T60 — Tebliğ §2.2: ``Kayıpsız çarpım'' bir özdeşlik değil, bir HİPOTEZ

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_fitrat_ve_topos

**Metinde:**

```latex
\| \text{Mana}(w_1 w_2 \dots w_n) - \bigotimes_{k=1}^n \mathbf{Fib}_{w_k} \|_{\mathbf{H}} &= 0 \quad (\text{Kayıpsız Çarpım})
```

**Tashih:**

```latex
\text{Mana}(w_1 \dots w_n) &= \mu\Big( \bigotimes_{k=1}^n \mathbf{Fib}_{w_k} \Big) \oplus \varepsilon_{\text{bağlam}}, \quad \varepsilon_{\text{bağlam}} = 0 \iff \mu \text{ izomorfizma}
```

**Gerekçe.** İki kusur: (i) Tip -- sol taraf bir ÖGE, sağ taraf bir UZAY; çıkarılamazlar. (ii) Muhteva -- tam bileşimsellik (exact compositionality) bir özdeşlik değil, bileşim eşlemesi $\mu$'nün izomorfizma olması şartıdır; deyimler ve bağlam bağımlılığı yüzünden tabiî lisanda genelde sağlanmaz. Kusur terimiyle yazılınca iddia SINANABİLİR hâle gelir.

### T61 — Tebliğ §3.2: Zincir kuralı ile monoidallik tek denkleme sıkıştırılmış

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_fitrat_ve_topos

**Metinde:**

```latex
(g \circ f)^*(T_1 \otimes_{\mathcal{O}} T_2) &\equiv f^* T_1 \otimes_{\mathcal{O}} f^* T_2 \quad (\text{Strict Refl ile Kayıpsız Aktarım})
```

**Tashih:**

```latex
(g \circ f)^* &\equiv f^* \circ g^* \quad (\text{zincir kuralı}) \\
f^*(T_1 \otimes_{\mathcal{O}} T_2) &\equiv f^* T_1 \otimes_{\mathcal{O}} f^* T_2 \quad (\text{monoidallik})
```

**Gerekçe.** Sol taraf $g \circ f$ boyunca taşıyor, sağ taraf yalnız $f$ boyunca; eşitlik olduğu gibi YANLIŞTIR. Bunlar iki AYRI kanundur ve ikisi de bu depoda TANIMSAL olarak sağlanır, yani $\texttt{refl}$ ile ispatlanır (\texttt{omega\_kategori}: \texttt{test\_zincir\_kurali\_tanimsal}).

### T62 — Tebliğ §3.3: $hLevel\ 0$ çıktıyı bir NOKTAYA çökertir

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_fitrat_ve_topos

**Metinde:**

```latex
N_{\text{kebîr}} &= \text{Truncate}_{hLevel 0}\left( \text{Lan}_{\text{Lisan}} \left( \mathcal{R} \triangleright \bigoplus_{j=1}^k \mathcal{A}_j \right) \right)
```

**Tashih:**

```latex
N_{\text{kebîr}} &= \big\| \text{Lan}_{\text{Lisan}} \big( \mathcal{R} \triangleright \textstyle\bigoplus_{j=1}^k \mathcal{A}_j \big) \big\|_0 = \text{Truncate}_{hLevel\,2}(\cdots) \quad (\text{KÜME kesmesi})
```

**Gerekçe.** Voevodsky'nin hlevel sayımında $hLevel\ 0$ BÜZÜLEBİLİRDİR: o mertebeye kesmek çıktıyı tek bir noktaya indirir ve bölümün korumaya çalıştığı bilginin tamamını yok eder. Küme kesmesi $n$-tip gösteriminde $\|\cdot\|_0$, hlevel gösteriminde $hLevel\ 2$'dir. Aynı belge 𝒪₂'de $hLevel\ 2$ yazıyor; iki yer çelişiyor.

### T63 — Tebliğ §3.3: Kesme ile ``univalence mührü'' birbirini yalanlıyor

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_fitrat_ve_topos

**Metinde:**

```latex
\text{Path}_{\text{akıl}} &= \left( \bigoplus_{j=1}^k \mathcal{A}_j \; \simeq_{\text{kayıpsız}} \; N_{\text{kebîr}} \right) \in \mathbf{U} \quad (\text{Univalence Mührü})
```

**Tashih:**

```latex
\bigoplus_{j=1}^k \mathcal{A}_j \simeq N_{\text{kebîr}} &\iff \bigoplus_{j=1}^k \mathcal{A}_j \text{ ZATEN } 0\text{-kesik (küme)}; \ \text{aksi hâlde } N_{\text{kebîr}} \text{ bir GERİ ÇEKİMDİR}
```

**Gerekçe.** Bir önceki satır kesme yapıyor. Kesme, kaynak zaten o mertebede kesik DEĞİLSE bir denklik değildir: $\|\cdot\|_0$ bir yansımadır (reflection) ve $A \to \|A\|_0$ ancak $A$ bir küme iken denkliktir. Dolayısıyla iki satır birbirini yalanlıyor. ``Kayıpsızlık'' iddiasının riyazî çekirdeği tam olarak bu şarttır ve açıkça yazılmalıdır.

### T64 — 𝒪₅ Tecrit (HoTT): Grassmannian'a izdüşüm diye bir şey yoktur

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\text{Proj}_{\text{Gr}(k,d_{\text{in}})}(X_t) = U_k U_k^T X_t \in \mathcal{T}_{\text{inv}}
```

**Tashih:**

```latex
\Pi_V(X_t) = U_k U_k^T X_t, \quad V = \text{span}(U_k) \in \text{Gr}(k, d_{\text{in}})
```

**Gerekçe.** Aynı sebep (bkz. T3).

### T65 — 𝒪₆ Tasavvur (HoTT): Homoloji GRUBU ile ağırlık dizeyi tensörlenemez

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_hott_topos

**Metinde:**

```latex
H_p\left( \mathcal{S}_{[1:t]} \right) \otimes_{\mathcal{O}} W_{\text{macro}}
```

**Tashih:**

```latex
H_p\left( \mathcal{S}_{[1:t]}; \mathbb{R} \right) \otimes_{\mathcal{O}} W_{\text{macro}}
```

**Gerekçe.** Aynı sebep (bkz. T10).

### T66 — 𝒪₃₃ Muhakeme (HoTT): Skaler integrale vektör eklenmiş

*tür:* boyut uyuşmazlığı &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\rangle_{\mathbf{H}} + \beta \dot{I}_t - \gamma \text{Tenakuz}(S_t) \Big] dt
```

**Tashih:**

```latex
\rangle_{\mathbf{H}} + \beta \|\dot{I}_t\| - \gamma \text{Tenakuz}(S_t) \Big] dt
```

**Gerekçe.** Aynı sebep (bkz. T14).

### T67 — 𝒪₁₀ Tezat (HoTT): Zıtlık operatörü involüsyon değil; ayrıca çifte eşlenik

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\mathbf{W}_{\text{opp}} &= -I_{d \times d} + \mathbf{v}_{\text{zıt}} \otimes \mathbf{v}_{\text{zıt}}^T
```

**Tashih:**

```latex
\mathbf{W}_{\text{opp}} &= 2\hat{\mathbf{v}}_{\text{zıt}} \hat{\mathbf{v}}_{\text{zıt}}^T - I_{d \times d}, \quad \|\hat{\mathbf{v}}_{\text{zıt}}\| = 1 \ \Rightarrow \ \mathbf{W}_{\text{opp}}^2 = I
```

**Gerekçe.** T19'daki involüsyon kusuruna ek olarak burada dış çarpım $\mathbf{v} \otimes \mathbf{v}^T$ diye yazılmış. Bu çifte eşleniktir (bir vektörle bir eş-vektörün tensörü); doğrusu ya $\mathbf{v}\mathbf{v}^T$ ya $\mathbf{v} \otimes \mathbf{v}$'dir. Aynı karışıklık 𝒪₄, 𝒪₁₄, 𝒪₁₇ ve 𝒪₁₈'de de tekrarlanıyor.

### T68 — 𝒪₃₀ Tahkik (HoTT): Aynı erişilemez eşik kusuru

*tür:* erişilemez eşik &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_hott_topos

**Metinde:**

```latex
T_{\text{tahkik}} &= \sigma\left( \text{CosSim}_{\mathbf{H}}(S_{\text{tahkik}}, S_{\text{asıl}}) \right)
```

**Tashih:**

```latex
T_{\text{tahkik}} &= \sigma\left( \beta_T \left[ \text{CosSim}_{\mathbf{H}}(S_{\text{tahkik}}, S_{\text{asıl}}) - \theta \right] \right), \quad \beta_T \ge 4
```

**Gerekçe.** Aynı sebep (bkz. T23, T24).

### T69 — 𝒪₂₇ Tetkik (HoTT): Skalerin LayerNorm'u tanımsız

*tür:* tanımsız ifade &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_hott_topos

**Metinde:**

```latex
\text{Skor}_{\text{tetkik}} &= \text{LayerNorm}\left( \sum \text{KusurHaritası} \right)
```

**Tashih:**

```latex
\text{Skor}_{\text{tetkik}} &= \text{LayerNorm}\Big( \textstyle\sum_{i} \text{KusurHaritası}_{i\cdot} \Big) \in \mathbb{R}^{d_{\text{sem}}}
```

**Gerekçe.** Aynı sebep (bkz. T39).

### T70 — 𝒪₂₇ Tetkik (HoTT): Tensör çarpımı yerine Hadamard çarpımı

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_i_mudrike_hott_topos

**Metinde:**

```latex
|\delta S_{t, \text{kılcal}} - S_{\text{ideal}}| \otimes_{\mathcal{O}} W_{\text{tetkik}}
```

**Tashih:**

```latex
|\delta S_{t, \text{kılcal}} - S_{\text{ideal}}| \odot W_{\text{tetkik}}
```

**Gerekçe.** Aynı sebep (bkz. T40).

### T71 — Münazara §1.3 (Mîzân): Ortam kapanışı bozuk: derleme KIRILIYOR

*tür:* yapi &nbsp;·&nbsp; *dosya:* mizan_i_muhakemat

**Metinde:**

```latex
\end{align">
```

**Tashih:**

```latex
\end{align}
```

**Gerekçe.** ``\end{align\"}'' diye kapanmış; LaTeX bunu ortam kapanışı saymaz ve belge derlenmez. Yapı denetleyicisi (\texttt{tex\_denetle.py}) bunu ``\begin{align} (satır 323) ile \end{document} uyuşmuyor'' diye yakaladı. Bu, muhtevaya dair bir tashih değil; belgenin derlenmesinin ön şartıdır.

### T72 — Relevans §1 (Zeyl): Ortam kapanışı bozuk: derleme KIRILIYOR

*tür:* yapi &nbsp;·&nbsp; *dosya:* mizan_zeyl

**Metinde:**

```latex
(\text{Değişme})
\end{align">
```

**Tashih:**

```latex
(\text{Değişme})
\end{align}
```

**Gerekçe.** Aynı kusur (bkz. T71).

### T73 — Doğrusal Mantık §1.2 (Zeyl): Ortam kapanışı bozuk: derleme KIRILIYOR

*tür:* yapi &nbsp;·&nbsp; *dosya:* mizan_zeyl

**Metinde:**

```latex
tüketilip B elde edilir})
\end{align">
```

**Tashih:**

```latex
tüketilip B elde edilir})
\end{align}
```

**Gerekçe.** Aynı kusur (bkz. T71).

### T74 — Kıyas-ı İstisnasî (Mîzân): Markdown başlığı LaTeX'e sızmış

*tür:* yapi &nbsp;·&nbsp; *dosya:* mizan_i_muhakemat

**Metinde:**

```latex
\## 1. Bitişik Şartlı Kıyaslar (Muttasıla)
```

**Tashih:**

```latex
\subsection{1. Bitişik Şartlı Kıyaslar (Muttasıla)}
```

**Gerekçe.** ``\\##'' LaTeX'te başlık değildir: ``\\#'' kaçırılmış diyez, ardından gelen ``#'' ise metin kipinde parametre karakteridir ve hata verir. Ayrıca altındaki \texttt{subsubsection}'lar sahipsiz kalır.

### T75 — Modal Mantık (Mîzân): Markdown başlığı LaTeX'e sızmış

*tür:* yapi &nbsp;·&nbsp; *dosya:* mizan_i_muhakemat

**Metinde:**

```latex
\## 1. Modal Mantık (Kiplik Mantığı - Zorumluluk ve İmkân)
```

**Tashih:**

```latex
\subsection{1. Modal Mantık (Kiplik Mantığı --- Zorunluluk ve İmkân)}
```

**Gerekçe.** Aynı kusur (bkz. T74). Ayrıca ``Zorumluluk'' $\to$ ``Zorunluluk''.

### T76 — Sezgisellik (Zeyl): Markdown başlığı LaTeX'e sızmış

*tür:* yapi &nbsp;·&nbsp; *dosya:* mizan_zeyl

**Metinde:**

```latex
\## 1. BHK (Brouwer-Heyting-Kolmogorov) İnşacı Semantigi
```

**Tashih:**

```latex
\subsection{1. BHK (Brouwer--Heyting--Kolmogorov) İnşacı Semantiği}
```

**Gerekçe.** Aynı kusur (bkz. T74). Ayrıca ``Semantigi'' $\to$ ``Semantiği''.

### T77 — Darapti (Mîzân): VARLIK FARAZİYESİ eksik: kıyas geçersiz

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* mizan_i_muhakemat, mizan_genisletilmis

**Metinde:**

```latex
P_2 &: \forall x (M(x) \implies S(x)) \quad (\text{Her M, S'dir}) \\
\mathcal{Q}_{\text{Darapti}} &: \exists x (S(x) \land P(x)) \quad (\text{Bazı S'ler P'dir})
```

**Tashih:**

```latex
P_2 &: \forall x (M(x) \implies S(x)) \quad (\text{Her M, S'dir}) \\
P_3 &: \exists x \, M(x) \quad (\text{VARLIK FARAZİYESİ --- M boş değildir}) \\
\mathcal{Q}_{\text{Darapti}} &: \exists x (S(x) \land P(x)) \quad (\text{Bazı S'ler P'dir})
```

**Gerekçe.** İki tümel öncülden tikel netice çıkarılıyor. $M$ BOŞ ise iki öncül de boşluktan doğrudur, netice ise yanlıştır --- yani kıyas yazıldığı hâliyle GEÇERSİZDİR (klasik adıyla ``varlık safsatası''). Aristo terimlerin boş olmadığını zımnen kabul eder; modern yüklem mantığında bu kabul YAZILMAK zorundadır.

### T78 — Felapton (Mîzân): VARLIK FARAZİYESİ eksik: kıyas geçersiz

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* mizan_i_muhakemat, mizan_genisletilmis

**Metinde:**

```latex
P_2 &: \forall x (M(x) \implies S(x)) \quad (\text{Her M, S'dir}) \\
\mathcal{Q}_{\text{Felapton}} &: \exists x (S(x) \land \neg P(x))
```

**Tashih:**

```latex
P_2 &: \forall x (M(x) \implies S(x)) \quad (\text{Her M, S'dir}) \\
P_3 &: \exists x \, M(x) \quad (\text{VARLIK FARAZİYESİ}) \\
\mathcal{Q}_{\text{Felapton}} &: \exists x (S(x) \land \neg P(x))
```

**Gerekçe.** Aynı sebep (bkz. T77).

### T79 — Bamalip (Mîzân): VARLIK FARAZİYESİ eksik: kıyas geçersiz

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* mizan_i_muhakemat, mizan_genisletilmis

**Metinde:**

```latex
P_2 &: \forall x (M(x) \implies S(x)) \quad (\text{Her M, S'dir}) \\
\mathcal{Q}_{\text{Bamalip}} &: \exists x (S(x) \land P(x))
```

**Tashih:**

```latex
P_2 &: \forall x (M(x) \implies S(x)) \quad (\text{Her M, S'dir}) \\
P_3 &: \exists x \, P(x) \quad (\text{VARLIK FARAZİYESİ --- burada P boş değildir}) \\
\mathcal{Q}_{\text{Bamalip}} &: \exists x (S(x) \land P(x))
```

**Gerekçe.** Aynı sebep (bkz. T77); fakat dördüncü şekilde boş olmaması gereken terim $M$ değil BÜYÜK TERİM $P$'dir. Öncüller $P \subseteq M \subseteq S$ verir; netice $\exists x (S \land P)$ ancak $P$ boş değilse çıkar.

### T80 — Fesapo (Mîzân): VARLIK FARAZİYESİ eksik: kıyas geçersiz

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* mizan_i_muhakemat, mizan_genisletilmis

**Metinde:**

```latex
P_2 &: \forall x (M(x) \implies S(x)) \quad (\text{Her M, S'dir}) \\
\mathcal{Q}_{\text{Fesapo}} &: \exists x (S(x) \land \neg P(x))
```

**Tashih:**

```latex
P_2 &: \forall x (M(x) \implies S(x)) \quad (\text{Her M, S'dir}) \\
P_3 &: \exists x \, M(x) \quad (\text{VARLIK FARAZİYESİ}) \\
\mathcal{Q}_{\text{Fesapo}} &: \exists x (S(x) \land \neg P(x))
```

**Gerekçe.** Aynı sebep (bkz. T77).

### T81 — Aks-i Müstevî (Mîzân): Arazî çevirme de varlık faraziyesi ister

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* mizan_i_muhakemat

**Metinde:**

```latex
\text{Aks}(\forall x (S(x) \implies P(x))) &\implies \exists x (P(x) \land S(x)) \quad (\text{Mûcebe-i Külliyye'nin aksi Mûcebe-i Cüz'iyyedir})
```

**Tashih:**

```latex
\text{Aks}(\forall x (S(x) \implies P(x))) \land \exists x \, S(x) &\implies \exists x (P(x) \land S(x)) \quad (\text{arazî çevirme; } S \ne \emptyset \text{ ŞARTIYLA})
```

**Gerekçe.** ``Aks-i müstevî bi'l-araz'' tümelden tikele iner; $S$ boşsa öncül boşluktan doğru, netice yanlıştır. Aynı belgede Darapti/Felapton/Bamalip/Fesapo'da düşen şart budur (bkz. T77-T80).

### T82 — İstikra-i Nâkıs (Mîzân): Formül ``en az biri'' olasılığı; tümevarım güveni değil

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* mizan_i_muhakemat, mizan_genisletilmis

**Metinde:**

```latex
P\left( \forall x \in K, P(x) \right) = 1 - \prod_{i=1}^k (1 - p_i)
```

**Tashih:**

```latex
P\left( \forall x \in K, P(x) \mid k \text{ doğrulayıcı örnek} \right) = \frac{k+1}{N+1}, \quad N = |K| \quad (\text{Laplace})
```

**Gerekçe.** $1 - \prod(1-p_i)$, bağımsız olayların EN AZ BİRİNİN gerçekleşme olasılığıdır; tümel bir genellemeye duyulan güven değildir. Üstelik $k \to \infty$ iken her $p_i$ ne kadar küçük olursa olsun $1$'e gider --- yani ``çok örnek gördüm, öyleyse kesindir'' safsatasını FORMÜLE eder. Doğru hâli Laplace'ın ardıllık hesabıdır: $N$ elemanlı bir kümede $k$ doğrulayıcı örnekten sonra istisnasızlık olasılığı $(k+1)/(N+1)$'dir ve ancak $k = N$ iken $1$ olur. Bu, belgenin kendi ``istikra-i tâmm kesindir, nâkıs değildir'' ayrımını riyazî olarak görünür kılar.

### T83 — Burhan (Mîzân): Öncüllerin doğruluğu tek başına neticeyi kesinleştirmez

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* mizan_i_muhakemat

**Metinde:**

```latex
\text{Sıhhat}(P_i) &= 1.0 \implies \text{Sıhhat}(\mathcal{Q}_{\text{Burhan}}) = 1.0 \quad (\text{Yakînî Netice})
```

**Tashih:**

```latex
\text{Sıhhat}(\mathcal{Q}_{\text{Burhan}}) &= \min_i \text{Sıhhat}(P_i) \times \mathbb{I}(\text{Şekil Geçerli}) \quad (\text{Yakîn ancak GEÇERLİ şekilde intikal eder})
```

**Gerekçe.** Doğru öncüller GEÇERSİZ bir şekilde dizilirse netice yakînî olmaz. Şekil geçerliliği çarpanı düşürülünce ``burhan'' tarifi, muğalatayı da içine alır. Nitekim aynı külliyatın zeyl risalesinde Gazâlî'nin mîzânı bu çarpanla DOĞRU yazılmış; iki metin birbiriyle çelişiyordu.

### T84 — Hitabet (Mîzân): Zannî öncüllerden zannî netice KENDİLİĞİNDEN çıkmaz

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* mizan_i_muhakemat

**Metinde:**

```latex
P_i &\in \text{Maznûnât} \implies P(\mathcal{Q}_{\text{Hitabet}}) > 0.5 \quad (\text{Zannî İkna})
```

**Tashih:**

```latex
P_i \in \text{Maznûnât} &\implies P(\mathcal{Q}_{\text{Hitabet}}) \ge 1 - \sum_i \left( 1 - P(P_i) \right) \quad (\text{Adams sınırı})
```

**Gerekçe.** $k$ öncülün her biri $0{,}6$ olsa bile neticenin olasılığı $0{,}5$'in çok altına düşebilir; belirsizlikler TOPLANIR. Doğru ifade Adams'ın olasılıksal modus ponens sınırıdır --- ki aynı külliyatın zeyl risalesinde zaten doğru yazılmış: $\text{Belirsizlik}(B) \le \text{Belirsizlik}(A) + \text{Belirsizlik}(A \implies B)$.

### T85 — Modal aksiyomlar (Genişletilmiş): ``5'' diye yazılan aksiyom aslında B'dir

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* mizan_genisletilmis

**Metinde:**

```latex
\mathbf{5} : \alpha \implies \Box \Diamond \alpha
```

**Tashih:**

```latex
\mathbf{5} : \Diamond \alpha \implies \Box \Diamond \alpha, \quad \mathbf{B} : \alpha \implies \Box \Diamond \alpha
```

**Gerekçe.** $\alpha \implies \Box\Diamond\alpha$ Brouwersche aksiyomu ($\mathbf{B}$, simetrik $R$) iken $\mathbf{5}$ (Öklidyen $R$) $\Diamond\alpha \implies \Box\Diamond\alpha$'dır. İkisi farklı çerçeve şartlarına karşılık gelir. Aynı külliyatın ana nüshasında $\mathbf{5}$ DOĞRU yazılmış; iki metin çelişiyordu.

### T86 — Deontik/Temporal (Mîzân): ``P'' aynı sayfada ÜÇ ayrı şey

*tür:* tanımsız ifade &nbsp;·&nbsp; *dosya:* mizan_i_muhakemat

**Metinde:**

```latex
O P \quad (\text{P ödevdir / mecburdur}), \quad P P \quad (\text{P caizdir / izinlidir}), \quad F P \quad (\text{P memnudur / yasaktır}) \\
P P &\equiv \neg O \neg P \\
F P &\equiv O \neg P \\
```

**Tashih:**

```latex
\mathrm{O}\varphi \ (\text{ödev}), \quad \mathrm{Pm}\,\varphi \ (\text{caiz}), \quad \mathrm{F}\varphi \ (\text{yasak}) \\
\mathrm{Pm}\,\varphi &\equiv \neg \mathrm{O} \neg \varphi \\
\mathrm{F}\varphi &\equiv \mathrm{O} \neg \varphi \\
```

**Gerekçe.** ``$P$'' bu iki alt bölümde (i) önerme değişkeni, (ii) deontik ``caiz'' işlemcisi ve (iii) temporal ``geçmişte bir an'' işlemcisi olarak kullanılıyor. ``$PP$'' ifadesi bu yüzden okunamaz. Önerme değişkeni $\varphi$'ye, deontik izin $\mathrm{Pm}$'ye alındı.

### T87 — Temporal (Mîzân): ``$HP \equiv \neg P \neg P$'' okunamaz

*tür:* tanımsız ifade &nbsp;·&nbsp; *dosya:* mizan_i_muhakemat

**Metinde:**

```latex
G P \quad (\text{Gelecekte daima P}), \quad F P \quad (\text{Gelecekte bir zaman P}) \\
H P \quad (\text{Geçmişte daima P}), \quad P P \quad (\text{Geçmişte bir zaman P}) \\
G P &\equiv \neg F \neg P \\
H P &\equiv \neg P \neg P \\
```

**Tashih:**

```latex
\mathrm{G}\varphi, \ \mathrm{F}\varphi \ (\text{gelecekte daima / bir an}), \quad \mathrm{H}\varphi, \ \mathsf{P}\varphi \ (\text{geçmişte daima / bir an}) \\
\mathrm{G}\varphi &\equiv \neg \mathrm{F} \neg \varphi \\
\mathrm{H}\varphi &\equiv \neg \mathsf{P} \neg \varphi \\
```

**Gerekçe.** T86'daki çakışmanın doğrudan neticesi: ``$\neg P \neg P$'' üç ayrı ``$P$''nin yan yana gelmesidir ve ayrıştırılamaz. Geçmiş-imkân işlemcisi $\mathsf{P}$'ye alınınca kural okunur hâle gelir.

### T88 — Until (Mîzân): Alt sınırsız ``until'' sonsuz geçmişi de kapsar

*tür:* tanımsız ifade &nbsp;·&nbsp; *dosya:* mizan_i_muhakemat

**Metinde:**

```latex
P \, \mathbf{U} \, Q &\iff \exists t (Q(t) \land \forall t' < t, P(t')) \quad (\text{Until / -e Kadar Operatörü})
```

**Tashih:**

```latex
\varphi \, \mathbf{U} \, \psi &\iff \exists t \ge t_0 \, \big( \psi(t) \land \forall t' \in [t_0, t), \, \varphi(t') \big) \quad (t_0: \text{şimdiki an})
```

**Gerekçe.** $\forall t' < t$ alt sınırsızdır; sonsuz geçmişte de $P$'nin sağlanmasını ister. ``-e kadar'' ŞİMDİDEN başlar.

### T89 — Łukasiewicz (Mîzân): Gerektirme ile bağlaçlar birbirinin eşleniği değil

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* mizan_i_muhakemat

**Metinde:**

```latex
v(P \land Q) &= \min(v(P), v(Q)) \\
v(P \lor Q) &= \max(v(P), v(Q)) \\
```

**Tashih:**

```latex
v(P \otimes Q) &= \max(0, v(P) + v(Q) - 1) \quad (\text{KUVVETLİ ve; } \to \text{'nin eşleniği}) \\
v(P \land Q) = \min(v(P), v(Q)), &\quad v(P \lor Q) = \max(v(P), v(Q)) \quad (\text{zayıf/kafes bağlaçları}) \\
```

**Gerekçe.** $v(P \to Q) = \min(1, 1-v(P)+v(Q))$ Łukasiewicz T-normunun KALINTISIDIR (residuum). Kalıntı bağıntısı $v(A \otimes B) \le v(C) \iff v(A) \le v(B \to C)$ ancak $\otimes$ kuvvetli ``ve'' iken sağlanır; $\min$ ile SAĞLANMAZ. Yazıldığı hâliyle gerektirme ile bağlaçlar aynı cebre ait değildir. Zayıf bağlaçlar da Łukasiewicz'de vardır, fakat eşlenik olan onlar değildir.

### T90 — Product mantığı (Mîzân): $v(P)=0$'da tanımsız

*tür:* tanımsız ifade &nbsp;·&nbsp; *dosya:* mizan_i_muhakemat

**Metinde:**

```latex
v(P \implies Q) &= \min\left(1, \frac{v(Q)}{v(P)}\right)
```

**Tashih:**

```latex
v(P \implies Q) &= \begin{cases} 1, & v(P) \le v(Q) \\ v(Q)/v(P), & v(P) > v(Q) \end{cases} \quad (v(P) = 0 \Rightarrow 1)
```

**Gerekçe.** $v(P) = 0$ iken bölme tanımsızdır; oysa çarpım mantığında $0 \to Q$ doğrudur ($=1$). Kalıntı biçiminde yazılınca hem tanım kümesi tamamlanır hem $\min$ gereksizleşir.

### T91 — Stoacı 4. usul (Zeyl): Usul yanlış adlandırılmış

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* mizan_zeyl

**Metinde:**

```latex
\subsection{4. Dördüncü Kanıtlanamaz Usul (Modus Tollendo Ponens I)}
```

**Tashih:**

```latex
\subsection{4. Dördüncü Kanıtlanamaz Usul (Modus Ponendo Tollens II)}
```

**Gerekçe.** Dördüncü usul ``$P \veebar Q$, $P$; öyleyse $\neg Q$''dur: bir tarafı KOYARAK öbürünü KALDIRIR, yani \textit{ponendo tollens}. \textit{Tollendo ponens} ise kaldırarak koyar --- o da beşinci usuldür ve orada doğru adlandırılmış.

### T92 — Heyting cebri (Zeyl): Meta-``ve'' ile kafes ``$\wedge$''i karışmış; ad yanlış

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* mizan_zeyl

**Metinde:**

```latex
A \le B \land A \le C \implies A \le B \land C \qquad &(\text{Ekok})
```

**Tashih:**

```latex
(A \le B) \ \text{ve} \ (A \le C) \iff A \le B \land C \qquad &(\text{en büyük alt sınırın evrensel hususiyeti})
```

**Gerekçe.** Soldaki ``$\land$'' meta-seviyede ``ve'', sağdaki ise kafes buluşmasıdır; aynı simge iki ayrı seviyede kullanılınca ifade ayrıştırılamaz. Ayrıca bağıntı tek yönlü değil, ÇİFT yönlüdür --- buluşmayı tanımlayan evrensel hususiyet budur. ``Ekok'' (en küçük ortak kat) ise alâkasız bir addır; burada söz konusu olan en büyük ALT sınırdır.

### T93 — Kuantum mantık (Zeyl): Dağılma her zaman BOZULMAZ; genel bağıntı bir eşitsizliktir

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* mizan_zeyl

**Metinde:**

```latex
A \land (B \lor C) &\neq (A \land B) \lor (A \land C) \quad (\text{Dağılma Geçersizdir})
```

**Tashih:**

```latex
(A \land B) \lor (A \land C) &\le A \land (B \lor C) \quad (\text{dâima}); \quad \text{eşitlik GEREKMEZ (dağılma geçersiz)}
```

**Gerekçe.** ``$\neq$'' yazmak ``her zaman eşit değildir'' demektir; oysa uyumlu (commuting) alt uzaylarda eşitlik SAĞLANIR. Ortolatislerde her zaman geçerli olan bağıntı yukarıdaki eşitsizliktir; kuantum mantığını klasikten ayıran şey, ters yönün genelde sağlanmamasıdır.

### T94 — Dombi T-normu (Zeyl): $a=0$ yahut $b=0$'da tanımsız

*tür:* tanımsız ifade &nbsp;·&nbsp; *dosya:* mizan_zeyl

**Metinde:**

```latex
T_{D}(a, b; p) = \frac{1}{1 + \left( \left(\frac{1-a}{a}\right)^p + \left(\frac{1-b}{b}\right)^p \right)^{1/p}}, \quad p > 0
```

**Tashih:**

```latex
T_{D}(a, b; p) = \begin{cases} 0, & a = 0 \ \text{yahut} \ b = 0 \\ \dfrac{1}{1 + \left( \left(\frac{1-a}{a}\right)^p + \left(\frac{1-b}{b}\right)^p \right)^{1/p}}, & \text{aksi hâlde} \end{cases}, \quad p > 0
```

**Gerekçe.** $a = 0$'da $(1-a)/a$ tanımsızdır. T-norm olabilmesi için $T(0,b) = 0$ şartı zaten gereklidir; sınır hâli açıkça yazılmalıdır.

### T95 — Schweizer--Sklar (Zeyl): Verilen biçim yalnız $p>0$ için doğru

*tür:* tanımsız ifade &nbsp;·&nbsp; *dosya:* mizan_zeyl

**Metinde:**

```latex
T_{SS}(a, b; p) = \left( \max(0, a^p + b^p - 1) \right)^{1/p}, \quad p \neq 0
```

**Tashih:**

```latex
T_{SS}(a, b; p) = \left( \max(0, a^p + b^p - 1) \right)^{1/p}, \quad p > 0 \qquad \left( p < 0: \ (a^p + b^p - 1)^{1/p} \right)
```

**Gerekçe.** $p < 0$ iken $a^p + b^p - 1 > 0$ dâima sağlanır ve $\max(0,\cdot)$ gereksizleşir; dahası $1/p < 0$ olduğundan kesme yanlış dala yönlendirir. Ailenin negatif kolu ayrı yazılır.

### T96 — Adams (Zeyl): $P(A) = 0$'da şartlı olasılık tanımsız

*tür:* tanımsız ifade &nbsp;·&nbsp; *dosya:* mizan_zeyl

**Metinde:**

```latex
P(A \implies B) &\coloneqq P(B \mid A) = \frac{P(A \land B)}{P(A)} \quad (\text{Adams Şartlı Olasılık Kuralı})
```

**Tashih:**

```latex
P(A \implies B) &\coloneqq P(B \mid A) = \frac{P(A \land B)}{P(A)}, \quad P(A) > 0 \quad (\text{Adams tezi})
```

**Gerekçe.** Adams tezi ancak öncül olumlu olasılıklıyken kurulur; $P(A) = 0$ hâlinde şartlı olasılık tanımsızdır ve bir sonraki satırdaki belirsizlik sınırı da düşer.

### T97 — Token Uzayları §Glue: SAĞLAMLIK HATASI: hcomp $u_0$'a indirgenmez

*tür:* sağlamlık &nbsp;·&nbsp; *dosya:* nefs_token_uzaylari

**Metinde:**

```latex
\text{hcomp}^i \, \mathcal{X}_{w_k} \, [\dots] \, u_0 &\longrightarrow u_0 \quad (\text{Ayrık Lif İç Dolgu İndirgemesi})
```

**Tashih:**

```latex
\text{hcomp}^i \, \mathcal{X}_{w_k} \, [\varphi \mapsto u] \, u_0 &\equiv u(1) \ \text{ on } \varphi; \quad \varphi = \bot \Rightarrow \equiv u_0 \quad (\text{SINIR şartı})
```

**Gerekçe.** Bu kural SAĞLAM DEĞİLDİR ve depoda makineyle çürütüldü. $\text{hcomp}$'un tarifi gereği $\varphi$ üzerinde $u$'ya eşit olması gerekir; $u_0$'a indirgemek tam olarak o sınır şartını kırar. \texttt{omega\_kategori} çekirdeğinde bu kural bir ara kurulmuştu ve neticeleri ölçüldü: \texttt{isoToEquiv}'in kare inşası bozuldu ($\texttt{fill0 1 1}$ $x_0$ yerine $g(f\,x_0)$ verdi) ve $\mathbb{Z}$ üzerindeki bütün dolgular çöktü. Kaldırıldı; yerine kurucuya iten YAPISAL kural konuldu. Metinde ``ayrık lif'' gerekçesi de tutmaz: liflerin ayrıklığı $\varphi$ boş olmadıkça dolguyu tabana indirmez.

### T98 — Token Uzayları §Kan: Bitişiklik üçlüsünde $F$ fazladan

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_token_uzaylari

**Metinde:**

```latex
\text{Lan}_{f_{i,j}} F &\dashv f_{i,j}^* \dashv \text{Ran}_{f_{i,j}} F \quad (\text{Üçlü Bitişiklik / Adjoint Triple})
```

**Tashih:**

```latex
\text{Lan}_{f_{i,j}} &\dashv f_{i,j}^* \dashv \text{Ran}_{f_{i,j}} \quad (\text{funktorlar arası üçlü bitişiklik})
```

**Gerekçe.** Bitişiklik FUNKTORLAR arasındadır, funktorun bir değerdeki çıktısı arasında değil. $\text{Lan}_f F$ bir funktor değil, bir nesnedir; $\dashv$'in solunda duramaz.

### T99 — Token Uzayları §Kan: Birim ile eş-birim bu sırayla bileşemez

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_token_uzaylari

**Metinde:**

```latex
\text{Coeff}_{\text{Kan}} &= \text{Tr}(\eta_{\text{unit}} \circ \varepsilon_{\text{counit}})
```

**Tashih:**

```latex
(\varepsilon \ast \text{Lan}_f) \cdot (\text{Lan}_f \ast \eta) &= \mathrm{id}_{\text{Lan}_f}, \quad (f^* \ast \varepsilon) \cdot (\eta \ast f^*) = \mathrm{id}_{f^*} \quad (\text{üçgen özdeşlikleri})
```

**Gerekçe.** $\eta : \mathrm{id} \Rightarrow f^* \circ \text{Lan}_f$ ile $\varepsilon : \text{Lan}_f \circ f^* \Rightarrow \mathrm{id}$ doğrudan bileşemez: birinin hedefi öbürünün kaynağı değildir. Bitişikliği karakterize eden bağıntılar ÜÇGEN ÖZDEŞLİKLERİDİR ve yatay ($\ast$) ile dikey ($\cdot$) bileşimi ayırarak yazılır. Bir de ``$\text{Tr}$'' burada tanımsızdır; iz bir doğal dönüşümün değil, bir endomorfizmanın niteliğidir.

### T100 — Token Uzayları §1-Morfizm: Tek yanlı ters denklik vermez

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* nefs_token_uzaylari

**Metinde:**

```latex
\text{Diffeo}(\mathcal{X}_{w_i} \simeq \mathcal{X}_{w_j}) &\iff \exists f_{i,j}, f_{j,i} \quad \text{öyle ki } f_{j,i} \circ f_{i,j} \simeq \text{id}
```

**Tashih:**

```latex
\text{Diffeo}(\mathcal{X}_{w_i} \simeq \mathcal{X}_{w_j}) &\iff \exists f_{i,j}, f_{j,i}: \ f_{j,i} \circ f_{i,j} \simeq \mathrm{id}_{\mathcal{X}_{w_i}} \ \textbf{ve} \ f_{i,j} \circ f_{j,i} \simeq \mathrm{id}_{\mathcal{X}_{w_j}}
```

**Gerekçe.** Yalnız bir bileşke birime homotop ise $f_{i,j}$ ancak bir BÖLÜMLENMİŞ monomorfizmadır (section/retract); denklik değildir. Denklik iki yanlı tersi ister.

### T101 — Token Uzayları §Glue: Lif hacminin çarpım olması TRİVİALLİK ister

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* nefs_token_uzaylari

**Metinde:**

```latex
\text{Vol}(\mathbf{Fib}_{\text{cümle}}) &= \int_{\mathcal{S}_{\text{cümle}}} d\text{vol}_{\text{cümle}} = \prod_{k=1}^N \text{Vol}(\mathbf{Fib}_{w_k})
```

**Tashih:**

```latex
\mathcal{S}_{\text{cümle}} \cong \textstyle\prod_k \mathbf{Fib}_{w_k} \ (\text{TRİVİAL demet}) \ &\Rightarrow \ \text{Vol}(\mathbf{Fib}_{\text{cümle}}) = \prod_{k=1}^N \text{Vol}(\mathbf{Fib}_{w_k})
```

**Gerekçe.** Hacmin çarpım olması, demetin çarpım demeti (trivial) olmasına bağlıdır. Oysa aynı bölüm cümleyi $\text{glue}$ ile, yani AŞİKÂR OLMAYAN bir yapıştırmayla kuruyor; bükülü bir demette lif hacimleri çarpılmaz. İki satır birbiriyle çelişiyor. Şart açıkça yazılınca iddia geçerli hâle gelir.

### T102 — Sorgu Uzayı §2: Liouville akışı hacmi KORUR; burada değişiyor

*tür:* işaret hatası &nbsp;·&nbsp; *dosya:* nefs_sorgu_uzayi, mantik_noronlari

**Metinde:**

```latex
\frac{d}{dt} \text{Vol}(L_S(\mathcal{X}_{\text{şüphe}})) &= -\int_{L_S(\mathcal{X})} \left( \Delta \mathcal{F}_{\text{iç}} + \|\nabla \mathcal{F}_{\text{iç}}\|^2 \right) d\text{vol}_g \quad (\text{Liouville Akışı})
```

**Tashih:**

```latex
\frac{d}{dt} \text{Vol}(L_S(\mathcal{X}_{\text{şüphe}})) &= -\int_{L_S(\mathcal{X})} \Delta \mathcal{F}_{\text{iç}} \, d\text{vol}_g \quad (\text{GRADYAN akışı; Liouville DEĞİL})
```

**Gerekçe.** İki kusur. (i) \textbf{Ad}: Liouville teoremi Hamilton akışının hacmi KORUDUĞUNU söyler ($\mathrm{div}\, X_{\mathcal{H}} = 0$, $d\text{Vol}/dt = 0$) --- nitekim aynı yazarın mantık nöronları risalesi bunu doğru yazıyor. Hacmi değiştiren bir akışa Liouville denemez. (ii) \textbf{Formül}: hız alanı $v = -\nabla\mathcal{F}$ olan bir akışta hacmin türevi $\int \mathrm{div}(v) = -\int \Delta\mathcal{F}$'dir; $\|\nabla\mathcal{F}\|^2$ terimi buradan gelmez (o, ağırlıklı hacim $\int e^{-\mathcal{F}}$ alınırsa doğar ve o zaman da işareti ARTIDIR).

### T103 — Sorgu Uzayı §2: Hacmi sonsuza giden uzay çürütülmüş değil, ASKIDADIR

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* nefs_sorgu_uzayi

**Metinde:**

```latex
\text{Bâtıl / Cerh (Uzay Yırtılması)}, & \mathcal{R}_{\text{karantina\_büzülme}} \to \infty \\
\text{Tahkik / Tasdik (Noktaya Büzülme)}, & \mathcal{R}_{\text{karantina\_büzülme}} \to 0 \\
\text{Askıda (Şüphe Uzayı Kalıcı)}, & \text{Diğer}
```

**Tashih:**

```latex
\text{Tahkik / Tasdik (noktaya büzülme)}, & \mathcal{R}_{\text{karantina\_büzülme}} \to 0 \\
\text{Bâtıl / Cerh}, & \Delta_{\text{tenakuz}} > \tau_{\text{fıtrat}} \ \text{ hâlâ} \ (t = \tau_{\text{teemmül}}) \\
\text{Askıda}, & \text{aksi hâlde (hacim büyüyor yahut sabit)}
```

**Gerekçe.** ``Büzülme'' adı taşıyan bir büyüklüğün sonsuza gitmesi zaten çelişkili; asıl kusur ise mânâdadır: şüphe uzayının hacminin BÜYÜMESİ, o bilginin çürütüldüğü değil, belirsizliğin arttığı anlamına gelir --- yani tam olarak ``askıda''dır. Cerh, hacim ölçüsünden değil, tenakuzun eşiğin üstünde KALMASINDAN çıkar. Yazıldığı hâliyle üçüncü dal da fiilen boş kalıyordu.

### T104 — Sorgu Uzayı §Kesme: $hLevel\,0$ çıktıyı bir noktaya çökertir

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_sorgu_uzayi

**Metinde:**

```latex
N_{\text{kebîr}} &= \text{Truncate}_{hLevel 0}\left( \text{Lan}_{\text{Lisan}} \left( \mathcal{R} \triangleright \mathcal{S}_{\text{yeni}} \right) \right) \in \mathcal{N}
```

**Tashih:**

```latex
N_{\text{kebîr}} &= \big\| \text{Lan}_{\text{Lisan}} \big( \mathcal{R} \triangleright \mathcal{S}_{\text{yeni}} \big) \big\|_0 = \text{Truncate}_{hLevel\,2}(\cdots) \in \mathcal{N} \quad (\text{KÜME kesmesi})
```

**Gerekçe.** Bu külliyatın kendi kullandığı hlevel sayımında (mantık nöronları risalesi, \S2.1) $hLevel\,0$ BÜZÜLEBİLİR, $hLevel\,1$ önerme, $hLevel\,2$ kümedir. O hâlde $hLevel\,0$'a kesmek çıktıyı tek bir noktaya indirir ve korunmaya çalışılan bilginin TAMAMINI yok eder. $n$-tip gösteriminde küme kesmesi $\|\cdot\|_0$, hlevel gösteriminde $hLevel\,2$'dir.

### T105 — Token Uzayları §Glue: $hLevel\,0$ çıktıyı bir noktaya çökertir

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_token_uzaylari

**Metinde:**

```latex
N_{\text{kebîr}} &= \text{Truncate}_{hLevel 0}\left( \text{Lan}_{\text{Lisan}} \left( \mathcal{R} \triangleright \mathcal{S}_{\text{cümle}} \right) \right) \in \mathcal{N}
```

**Tashih:**

```latex
N_{\text{kebîr}} &= \big\| \text{Lan}_{\text{Lisan}} \big( \mathcal{R} \triangleright \mathcal{S}_{\text{cümle}} \big) \big\|_0 = \text{Truncate}_{hLevel\,2}(\cdots) \in \mathcal{N}
```

**Gerekçe.** Aynı sebep (bkz. T104).

### T106 — Bütünsel İdrak §3: $hLevel\,0$ çıktıyı bir noktaya çökertir

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_butunsel_idrak

**Metinde:**

```latex
N_{\text{kebîr}} &= \text{Truncate}_{hLevel 0} \left( \text{Lan}_{\text{Lisan}} \left( \mathcal{R}_{\text{küllî}} \triangleright \mathcal{S}_{\text{hitabet}} \right) \right) \in \mathcal{N}
```

**Tashih:**

```latex
N_{\text{kebîr}} &= \big\| \text{Lan}_{\text{Lisan}} \big( \mathcal{R}_{\text{küllî}} \triangleright \mathcal{S}_{\text{hitabet}} \big) \big\|_0 = \text{Truncate}_{hLevel\,2}(\cdots) \in \mathcal{N}
```

**Gerekçe.** Aynı sebep (bkz. T104).

### T107 — Mütedahile §Aktarım: $hLevel\,0$ çıktıyı bir noktaya çökertir

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* mizan_mutedahile

**Metinde:**

```latex
N_{\text{kebîr}} &= \text{Truncate}_{hLevel 0} \left( \text{Lan}_{\text{Lisan}} \left( \mathcal{R} \triangleright \mathcal{S}_{\text{birleşik}} \right) \right) \in \mathcal{N}
```

**Tashih:**

```latex
N_{\text{kebîr}} &= \big\| \text{Lan}_{\text{Lisan}} \big( \mathcal{R} \triangleright \mathcal{S}_{\text{birleşik}} \big) \big\|_0 = \text{Truncate}_{hLevel\,2}(\cdots) \in \mathcal{N}
```

**Gerekçe.** Aynı sebep (bkz. T104).

### T108 — Mantık Nöronları §2.1: Homotopi grubu KÜME kesmesidir

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* mantik_noronlari

**Metinde:**

```latex
\pi_n(\mathcal{A}, a_0) &= \text{Truncate}_{hLevel 0}(\Omega^n(\mathcal{A}, a_0)) \quad (\text{Homotopi Grubu})
```

**Tashih:**

```latex
\pi_n(\mathcal{A}, a_0) &= \big\| \Omega^n(\mathcal{A}, a_0) \big\|_0 = \text{Truncate}_{hLevel\,2}(\Omega^n(\mathcal{A}, a_0)) \quad (\text{KÜME kesmesi})
```

**Gerekçe.** Bu satır, üç satır yukarıdaki kendi tanımıyla çelişiyor: aynı bölüm $\text{isContr}(A) \iff \dots$ ($h$-Level 0) ve $\text{isSet}(A) \iff \dots$ ($h$-Level 2) diye DOĞRU yazıyor. $hLevel\,0$'a kesilirse her homotopi grubu aşikâr gruba çöker. Homotopi grupları döngü uzayının KÜME kesmesidir.

### T109 — Mantık Nöronları §7.2: $hLevel\,0$ çıktıyı bir noktaya çökertir

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* mantik_noronlari

**Metinde:**

```latex
N_{\text{kebîr}} &= \text{Truncate}_{hLevel 0}\left( \text{Lan}_{\text{Lisan}} \left( \mathcal{R} \triangleright \mathcal{S}_{\text{yeni}} \right) \right) \in \mathcal{N}
```

**Tashih:**

```latex
N_{\text{kebîr}} &= \big\| \text{Lan}_{\text{Lisan}} \big( \mathcal{R} \triangleright \mathcal{S}_{\text{yeni}} \big) \big\|_0 = \text{Truncate}_{hLevel\,2}(\cdots) \in \mathcal{N}
```

**Gerekçe.** Aynı sebep (bkz. T104, T108).

### T110 — Mantık Nöronları §3.1: Türetilmiş kritik yerde iki haritanın hangisi olduğu yazılmamış

*tür:* tanımsız ifade &nbsp;·&nbsp; *dosya:* mantik_noronlari

**Metinde:**

```latex
\mathbf{R}\text{Crit}(f) &\coloneqq \mathcal{X} \times_{\mathcal{T}^*\mathcal{X}} \mathcal{X} \quad (\text{Türetilmiş Kritik Alt-Uzay / Locus})
```

**Tashih:**

```latex
\mathbf{R}\text{Crit}(f) &\coloneqq \mathcal{X} \times^{h}_{df, \, \mathcal{T}^*\mathcal{X}, \, 0} \mathcal{X} \quad (df \text{ ile SIFIR kesitinin homotopi lif çarpımı})
```

**Gerekçe.** Lif çarpımının hangi iki harita üzerinden alındığı yazılmazsa nesne belirsizdir; ve ``türetilmiş'' olması için çarpımın HOMOTOPİ lif çarpımı olması şarttır (bir sonraki satırdaki $\otimes^{\mathbf{L}}$ zaten bunu söylüyor). Kritik yer, $df$ ile sıfır kesitinin kesişmesidir.

### T111 — Mantık Nöronları §3.1: Serbest enerji $\ge 0$ değildir

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* mantik_noronlari

**Metinde:**

```latex
\mathcal{F}(X, S) &= \mathbb{E}_{q(S)} \left[ \ln q(S) - \ln p(X, S) \right] \ge 0 \quad (\text{Serbest Enerji / Tenakuz})
```

**Tashih:**

```latex
\mathcal{F}(X, S) &= \text{KL}\big( q(S) \,\|\, p(S \mid X) \big) - \ln p(X) \ \ge \ -\ln p(X) \quad (\text{değişimsel serbest enerji})
```

**Gerekçe.** Değişimsel serbest enerji $-\ln p(X)$ ile alttan sınırlıdır, $0$ ile değil; $\mathcal{F} \ge 0$ ancak $p(X) \le 1$ iken, yani AYRIK $X$ için doğrudur ve yoğunluklarda yanlıştır. Negatif olmayan büyüklük KL terimidir.

### T112 — Fıtrî Tahsil §1: Serbest enerji $\ge 0$ değildir

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* nefs_fitri_tahsil

**Metinde:**

```latex
\mathcal{F}_{\text{iç}}(X_t, S_t) &= \mathbb{E}_{q(S)} \left[ \ln q(S_t) - \ln p(X_t, S_t) \right] \ge 0 \quad (\text{Serbest Enerji / İç Tenakuz})
```

**Tashih:**

```latex
\mathcal{F}_{\text{iç}}(X_t, S_t) &= \text{KL}\big( q(S_t) \,\|\, p(S_t \mid X_t) \big) - \ln p(X_t) \ \ge \ -\ln p(X_t)
```

**Gerekçe.** Aynı sebep (bkz. T111).

### T113 — Mantık Nöronları §3.1: ICP kesişimi YORDAYICI KÜMELER üzerinden alınır

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* mantik_noronlari

**Metinde:**

```latex
\bigcap_{e \in \mathcal{E}} \text{Supp}\left( P_e(Y \mid X_{\text{Sâbit}}) \right) &= X_{\text{Hakiki\_İllet}} \quad (\text{ICP - Invariant Causal Prediction})
```

**Tashih:**

```latex
S^{\star} = \bigcap \big\{ S \subseteq \{1,\dots,p\} : P_e(Y \mid X_S) \ \text{her } e \in \mathcal{E} \text{ için AYNI} \big\} &\subseteq \text{PA}(Y) \quad (\text{ICP})
```

**Gerekçe.** Desteklerin kesişimi bir SONUÇ kümesi verir; oysa aranan bir DEĞİŞKEN kümesidir. ICP (Peters--Bühlmann--Meinshausen) kabul edilen yordayıcı kümelerini kesiştirir ve netice gerçek ebeveyn kümesinin ALT kümesidir --- eşitlik değil, kapsama.

### T114 — Mantık Nöronları §6.2: Zincir kuralı ile monoidallik tek denkleme sıkışmış

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* mantik_noronlari

**Metinde:**

```latex
(g \circ f)^*(T_1 \otimes_{\mathcal{O}} T_2) &\equiv f^* T_1 \otimes_{\mathcal{O}} f^* T_2 \quad (\text{Strict Refl Monoidal Aktarım})
```

**Tashih:**

```latex
(g \circ f)^* &\equiv f^* \circ g^* \ (\text{zincir kuralı}); \qquad f^*(T_1 \otimes_{\mathcal{O}} T_2) \equiv f^* T_1 \otimes_{\mathcal{O}} f^* T_2 \ (\text{monoidallik})
```

**Gerekçe.** Sol taraf $g \circ f$ boyunca, sağ taraf yalnız $f$ boyunca taşıyor; eşitlik olduğu gibi YANLIŞTIR. Bunlar iki AYRI kanundur ve ikisi de bu depoda TANIMSAL olarak sağlanır, yani \texttt{refl} ile ispatlanır (\texttt{omega\_kategori}: \texttt{test\_zincir\_kurali\_tanimsal}).

### T115 — Mütedahile §Aktarım: Zincir kuralı ile monoidallik tek denkleme sıkışmış

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* mizan_mutedahile

**Metinde:**

```latex
(g \circ f)^* (T_1 \otimes_{\mathcal{O}} T_2) &\equiv f^* T_1 \otimes_{\mathcal{O}} f^* T_2 \quad (\text{Strict Refl Monoidal Taşınım})
```

**Tashih:**

```latex
(g \circ f)^* &\equiv f^* \circ g^* \ (\text{zincir kuralı}); \qquad f^*(T_1 \otimes_{\mathcal{O}} T_2) \equiv f^* T_1 \otimes_{\mathcal{O}} f^* T_2 \ (\text{monoidallik})
```

**Gerekçe.** Aynı sebep (bkz. T114).

### T116 — Fıtrî Tahsil §2: Makam parçalanışında BOŞLUK

*tür:* tanımsız ifade &nbsp;·&nbsp; *dosya:* nefs_fitri_tahsil

**Metinde:**

```latex
\text{Şek (Şüphe)}, & \Delta_{\text{tenakuz}} > 0 \;\lor\; |P_{\text{idrak}} - 0.5| < \epsilon_{\text{şek}}
```

**Tashih:**

```latex
\text{Şek (Şüphe)}, & \Delta_{\text{tenakuz}} > 0 \;\lor\; |P_{\text{idrak}} - 0.5| < \epsilon_{\text{şek}} \\
\text{Vehim (aleyhte zan)}, & \Delta_{\text{tenakuz}} = 0 \;\land\; P_{\text{idrak}} < 0.5 - \epsilon_{\text{şek}}
```

**Gerekçe.** Yazılan üç dal, $\Delta_{\text{tenakuz}} = 0$ VE $P_{\text{idrak}} < 0{,}5 - \epsilon_{\text{şek}}$ hâlini kapsamıyor; orada $\text{Makam}$ tanımsız kalıyor. Bu, tenakuz bulunmadığı hâlde delilin ALEYHTE olduğu durumdur ve klasik adı vehimdir. Eklenince parçalanış tam ve ayrık olur.

### T117 — Fıtrî Tahsil §3: Tevafuk toplamı her çifti İKİ kere sayıyor

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* nefs_fitri_tahsil

**Metinde:**

```latex
\text{Tevafuk}(X_t) &= \sum_{k=1}^K \sum_{l \ne k}^K \text{CosSim}_{\mathbf{H}}\left( f_{\text{kanal\_k}}(X_t), f_{\text{kanal\_l}}(X_t) \right) \cdot \mathbb{I}\left( \text{Kanal}_k \perp \text{Kanal}_l \right)
```

**Tashih:**

```latex
\text{Tevafuk}(X_t) &= \sum_{1 \le k < l \le K} \text{CosSim}_{\mathbf{H}}\left( f_{\text{kanal\_k}}(X_t), f_{\text{kanal\_l}}(X_t) \right) \cdot \mathbb{I}\left( E_k \perp\!\!\!\perp E_l \mid H \right)
```

**Gerekçe.** İki kusur. (i) $\text{CosSim}$ simetrik olduğundan $\sum_k \sum_{l \ne k}$ her çifti iki kere sayar ve tevafuku iki katına çıkarır. (ii) Delilin kuvvetlenmesi için gereken şart MARJİNAL bağımsızlık değil, hipotez verildiğinde ŞARTLI bağımsızlıktır --- Bayes güncellemesinin geçerli olduğu şart budur.

### T118 — Fıtrî Tahsil §8: Olasılığın varyansı değil, $S_t$'nin şartlı varyansı

*tür:* tanımsız ifade &nbsp;·&nbsp; *dosya:* nefs_fitri_tahsil

**Metinde:**

```latex
\mathbf{K}_{\text{ihtiyat}} &= S_t + \mu_{\text{temkin}} \cdot \sqrt{\text{Var}(P(S_t \mid Q_{\text{havuz}}))}
```

**Tashih:**

```latex
\mathbf{K}_{\text{ihtiyat}} &= S_t + \mu_{\text{temkin}} \cdot \sqrt{\text{Var}_{P(\cdot \mid Q_{\text{havuz}})}[S_t]}
```

**Gerekçe.** ``Bir olasılığın varyansı'' tanımsızdır; kastedilen $S_t$'nin şartlı dağılım altındaki varyansıdır.

### T119 — Bütünsel İdrak §1: Cauchy formülünde $1/2\pi i$ çarpanı düşmüş

*tür:* boyut uyuşmazlığı &nbsp;·&nbsp; *dosya:* nefs_butunsel_idrak

**Metinde:**

```latex
\mathbf{\Psi}_{\text{küllî}}(W) &\coloneqq \oint_{\partial \Omega} \frac{\Phi_{\text{metin}}(z)}{z - z_0} dz \in \mathbf{H} \quad (\text{Cauchy İntegral Formülü ile Metnin Tek Anda İdrakı})
```

**Tashih:**

```latex
\mathbf{\Psi}_{\text{küllî}}(W) &\coloneqq \frac{1}{2\pi i} \oint_{\partial \Omega} \frac{\Phi_{\text{metin}}(z)}{z - z_0} \, dz = \Phi_{\text{metin}}(z_0) \quad (\text{Cauchy integral formülü})
```

**Gerekçe.** Cauchy integral formülü $f(z_0) = \frac{1}{2\pi i}\oint \frac{f(z)}{z-z_0}dz$'dir. $1/2\pi i$ çarpanı olmadan sol taraf $f(z_0)$'a eşit olmaz, $2\pi i$ katı çıkar. Formülün bütün gücü o eşitliktedir.

### T120 — Bütünsel İdrak §1: Lif UZAYI karmaşık bir sayıyla çarpılamaz

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* nefs_butunsel_idrak

**Metinde:**

```latex
\Phi_{\text{metin}}(z) &= \sum_{k=1}^N \mathbf{Fib}_{w_k} \cdot \exp\left( -2\pi i \, k \cdot z \right) \quad (\text{Bütün Metnin Frekans Manifoldu})
```

**Tashih:**

```latex
\Phi_{\text{metin}}(z) &= \sum_{k=1}^N c_{w_k} \exp\left( -2\pi i \, k z \right), \quad c_{w_k} \in \mathbb{C}^d \ (\mathbf{Fib}_{w_k}\text{'nın kesiti})
```

**Gerekçe.** $\mathbf{Fib}_{w_k}$ bir UZAYDIR; karmaşık bir üstel ile çarpılamaz ve toplanamaz. Holomorf bir fonksiyon kurmak için lifin sayısal bir KESİTİ (bir katsayı vektörü) alınmalıdır. Bu düzeltilmeden bir sonraki satırdaki Cauchy integrali de tanımsız kalır.

### T121 — Bütünsel İdrak §2: 40 veçhe hacmi çarpım olması TRİVİALLİK ister

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* nefs_butunsel_idrak

**Metinde:**

```latex
\text{ManaHacmi}(w) &= \int_{\mathbf{Fib}_w} d\text{vol}_{1} \wedge d\text{vol}_{2} \dots \wedge d\text{vol}_{40} = \prod_{j=1}^{40} \text{Vol}(\mathcal{X}_j)
```

**Tashih:**

```latex
\mathbf{Fib}_w \cong \textstyle\prod_{j=1}^{40} \mathcal{X}_j \ (\text{TRİVİAL demet}) \ &\Rightarrow \ \text{ManaHacmi}(w) = \prod_{j=1}^{40} \text{Vol}(\mathcal{X}_j)
```

**Gerekçe.** Farklı çarpanlardan gelen tepe formların dış çarpımı, ancak lif ÇARPIM uzayı ise hacim formunu verir; bükülü bir demette hacimler çarpılmaz (bkz. T101).

### T122 — Bütünsel İdrak §2: ``Tam ittisâl'' şartı fiilen AŞİKÂRDIR

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* nefs_butunsel_idrak

**Metinde:**

```latex
\mathbf{Coherence}_{\text{40\_veçhe}} &= \mathbf{1} \iff \forall i, j, \, \mathbf{Hom}_{\mathbf{H}}(\mathcal{X}_i, \mathcal{X}_j) \neq \emptyset \quad (\text{Veçheler Arası Tam İttisal})
```

**Tashih:**

```latex
\mathbf{Coherence}_{\text{40\_veçhe}} &= \mathbf{1} \iff \forall i, j, k: \ f_{jk} \circ f_{ij} \simeq f_{ik} \quad (\text{eş-devir/cocycle şartı})
```

**Gerekçe.** Bir toposta uç nesne vardır; hedefin bir küresel noktası olduğu her an $\mathbf{Hom}(\mathcal{X}_i,\mathcal{X}_j) \ne \emptyset$ sağlanır. Yani şart neredeyse hiçbir şey söylemez; ``tam ittisâl'' gibi kuvvetli bir iddianın karşılığı olamaz. Veçhelerin gerçekten tutarlı biçimde birbirine bağlanması, geçiş haritalarının BİLEŞİM altında uyuşmasıdır.

### T123 — Mütedahile §Barbara: Kan uzantısı bir ÖNERME boyunca alınamaz

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* mizan_mutedahile

**Metinde:**

```latex
\mathcal{Q}_{\text{Barbara}} &= (\text{Lan}_{P_2} P_1)(S) \in \text{QCoh}(S \times P) \quad (\text{Sol Kan Uzantısı ile Çıkarım})
```

**Tashih:**

```latex
\mathcal{Q}_{\text{Barbara}} &= \iota_{MP} \circ \iota_{SM} : S \hookrightarrow P \quad (\text{alt nesne kafesinde GEÇİŞLİLİK; bileşke})
```

**Gerekçe.** Kan uzantısı bir FUNKTOR boyunca alınır; $P_2$ ise bir önermedir (bir alt nesne / doğruluk değeri), funktor değildir. Barbara'nın kategorik karşılığı zaten çok daha sadedir: $S \hookrightarrow M \hookrightarrow P$ monomorfizmalarının BİLEŞİMİ, yani alt nesne kafesindeki $\le$ bağıntısının geçişliliği. Kan uzantısına ihtiyaç yoktur ve zorlanması tip hatası doğurur.

### T124 — Mütedahile §İstikra: Tam tümevarım TÜKETİCİ sayım ister

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* mizan_mutedahile

**Metinde:**

```latex
\mathcal{M}_{\text{Tamİstikra}} &\coloneqq \varprojlim_{i \in \{1,\dots,n\}} \{ S_i \in K \mid P(S_i) \} \implies \forall x \in K, \, P(x)
```

**Tashih:**

```latex
\mathcal{M}_{\text{Tamİstikra}} &\coloneqq \textstyle\prod_{i=1}^n \{ S_i \mid P(S_i) \} \ \land \ \{S_1,\dots,S_n\} = K \ \implies \ \forall x \in K, \, P(x)
```

**Gerekçe.** ``Tam'' tümevarımı ``nâkıs''tan ayıran şey, örneklemin kümenin TAMAMI olmasıdır; bu şart yazılmazsa çıkarım geçersizdir. Ayrıca ayrık sonlu bir indis üzerindeki ters limit çarpımdır --- ters limit gösterimi burada fazladan bir yapı ima ediyor.

### T125 — Mütedahile §İstikra: Güven, örneklenen ORANA bağlıdır

*tür:* mantıkî denklik hatası &nbsp;·&nbsp; *dosya:* mizan_mutedahile

**Metinde:**

```latex
P_{\text{güven}}(\mathcal{M}_{\text{Eksikİstikra}}) &= 1 - \exp\left( -\lambda_{\text{örnek}} \cdot \text{Vol}(\mathcal{D}) \right)
```

**Tashih:**

```latex
P_{\text{güven}}(\mathcal{M}_{\text{Eksikİstikra}}) &= \frac{k+1}{N+1}, \quad k = |\mathcal{D}|, \ N = |K| \quad (\text{Laplace; } k = N \text{ iken } 1)
```

**Gerekçe.** Yazılan biçim, örneklem hacmi büyüdükçe --- kümenin ne kadarına karşılık geldiğine BAKMADAN --- güveni $1$'e götürür. Oysa eksik tümevarımın kusuru tam olarak budur: güven, örneklenenin kümeye ORANINA bağlı olmalıdır (bkz. T82).

### T126 — Mütedahile §Syādvāda: Uzaylar gerçel ağırlıklarla toplanamaz

*tür:* tip / ulam hatası &nbsp;·&nbsp; *dosya:* mizan_mutedahile

**Metinde:**

```latex
\text{Path}_{\text{Syād}} &= \left( \sum_{k=1}^7 w_k \mathcal{M}_{\text{Syād}_k} \;\simeq_{\text{göreler}}\; \mathbf{Hakikat} \right)
```

**Tashih:**

```latex
\{ \mathcal{M}_{\text{Syād}_k} \}_{k=1}^{7} &\ \leftrightarrow \ \{ \emptyset \ne A \subseteq \{\text{asti}, \text{nāsti}, \text{avaktavya}\} \}, \quad 2^3 - 1 = 7; \quad \mathbf{Hakikat} = \varinjlim_k \mathcal{M}_{\text{Syād}_k}
```

**Gerekçe.** Uzayların gerçel katsayılı toplamı tanımsızdır (vektörlerin değil, NESNELERİN toplamı). Ayrıca bu yazılış ``niçin yedi?'' sorusunu cevapsız bırakıyor. Yedi mod, üç temel yüklemin boş olmayan alt kümeleridir: $2^3 - 1 = 7$. Bileşke hakikat de toplam değil, eş-limittir (colimit).
