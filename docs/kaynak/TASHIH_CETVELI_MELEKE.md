# 41 Meleke ve Reel Operatör Risaleleri — Tashih Cetveli

Yedi kaynak, **34 tashih**. Her kayıt `docs/kaynak/tashih_meleke.py` içinde bir veri satırıdır; bu cetvel elle değil o kayıttan üretilir.

| No | Yer | Başlık | Tür | Sağlama |
|---|---|---|---|---|
| M1 | §FNO-KAN büküm | Ortam kapanışı bozuk: \end{align"> | derleme | `test_dalga_bukum_derleniyor` |
| M2 | §Durr-Høyer adımları | Ortam kapanışı bozuk: \end{enumerate"> | derleme | `test_asgari_arama_derleniyor` |
| M3 | §Adyabatik Hamiltonian | Ortam kapanışı bozuk: \end{align"> | derleme | `test_asgari_arama_derleniyor` |
| M4 | §Karmaşıklık cetveli | ``\end{caption{...}`` diye bir şey yok | derleme | `test_veri_akis_derleniyor` |
| M5 | §1 Müşahede (reel) | Ortam kapanışı bozuk: \end{equation"> | derleme | `test_reel_meleke_derleniyor` |
| M6 | §13 İspat (reel) | Ortam kapanışı bozuk: \end{equation"> | derleme | `test_reel_meleke_derleniyor` |
| M7 | §Reel komütatörler | Ortam kapanışı bozuk: \end{equation"> | derleme | `test_reel_meleke_derleniyor` |
| M8 | §Reel çakışma | Ortam kapanışı bozuk: \end{equation"> | derleme | `test_reel_meleke_derleniyor` |
| M9 | §8 Tenakuz | Householder yansıması durumun TAMAMINI negatiflemez | uniterlik | `test_householder_butun_durumu_negatiflemiyor` |
| M10 | §8 Tenakuz (reel) | Householder yansıması durumun TAMAMINI negatiflemez | uniterlik | `test_householder_butun_durumu_negatiflemiyor` |
| M11 | §16 İhtimal Hesabı | $\sum_x \sqrt{P(x)}\|x\rangle\langle x\|$ üniter değildir | uniterlik | `test_kok_p_kosegeni_uniter_degil` |
| M12 | §16 İhtimal Hesabı (reel) | $\sum_x P(x)\|x\rangle\langle x\|$ üniter değildir | uniterlik | `test_kok_p_kosegeni_uniter_degil` |
| M13 | §11 Şek-Zan-Yakîn | Yazılan operatör üniter değil, tabanı da tutarsız | uniterlik | `test_sek_zan_yakin_uniter_degil` |
| M14 | §Komütasyon bağıntıları | Yapı sabitleri cebir için geçerlidir, grup elemanları için değil | cebir | `test_grup_komutatoru_cebirde_degil` |
| M15 | §Reel komütatörler | Dik matrislerin komütatörü $\mathfrak{so}(2N)$'de değildir | cebir | `test_grup_komutatoru_cebirde_degil` |
| M16 | §Usul (küllî idrak devresi) | Zaman-sıralı üstel ancak SIRA DEĞİŞTİREN üreteçlerde çarpıma eşittir | cebir | `test_carpim_usteli_ancak_komut_edende_esit` |
| M17 | §Sual 2 (haberleşme) | Dolaşıklık uzak melekenin durumunu değiştirmez (no-communication) | mantik | `test_yerel_uniter_uzak_indirgenmisi_degistirmiyor` |
| M18 | §Durr-Høyer 4. adım | $K$ bilinmeden tur sayısı $m$ seçilemez | eksik_sart | `test_grover_yanlis_m_ile_basari_dusuyor` |
| M19 | §Adyabatik netice | Sonlu $T$'de başarı asla \%100 değildir | mantik | `test_adiyabatik_sonlu_T_de_tam_degil` |
| M20 | §Tünelleme | Tünelleme olasılığı üsteldir; geçiş $O(1)$ değildir | mantik | `test_tunelleme_ussel_pahali` |
| M21 | §Wilson döngüsü | Düz bağlantı ($F=0$) holonominin trivial olmasını gerektirmez | mantik | `test_duz_baglanti_trivial_holonomi_vermiyor` |
| M22 | §GRAPE | GRAPE gradyanı eşitlik değil, $\mathcal{O}(\Delta t^2)$ yaklaşımıdır | eksik_sart | `test_grape_gradyani_dt_kare_yaklasimi` |
| M23 | §Nefs-i Müdrike entegrasyonu | $\sum \|c_i\|_p^2 = 1$ bir normalizasyon şartı değildir | olcut | `test_p_adik_toplam_normalizasyon_degil` |
| M24 | §İrrasyonel sayı yanılsaması | Yuvarlama hatasının tek sebebi irrasyonellik değildir | mantik | `test_float_hatasi_rasyonelde_de_var` |
| M25 | §$p$-adic metrik | Terim yanlış: "ultradinamik" değil, ultrametrik | terim | — |
| M26 | §26--41 Hafıza (reel) | Terim yanlış: "ultradinamik" değil, ultrametrik | terim | — |
| M27 | §Atom sayısı kısıtlamasının reddi | İtiraz boyuta değil, keyfî durumun saklanmasına dairdir | test_yapili_durumlar_400_kubitin_otesinde | — |
| M28 | §Usul (reel Schrödinger) | İşaret ters: $-J H_\mathbb{R}$ olmalı | isaret | `test_reel_schrodinger_isareti` |
| M29 | §15 Terkip (reel) | Hartley uzayında köşegen çarpan evrişim DEĞİLDİR | eksik_sart | `test_hartley_kosegen_evrisim_degil` |
| M30 | §4 Fıtrâtı İdrak (reel) | Genel işaret ölçülemez; parite kapısı kontrollü olmalıdır | uniterlik | — |
| M31 | §Karmaşıklık cetveli | $\log^2 N$ değeri yanlış hesaplanmış | aritmetik | `test_veri_akis_logaritma_aritmetigi` |
| M32 | §Efektif sürat | $N^3/\log^2 N$ değeri yanlış hesaplanmış | aritmetik | `test_veri_akis_sikistirma_orani` |
| M33 | §Efektif sürat | Bant genişliğini karmaşıklık oranıyla çarpmak boyutça geçersizdir | boyut | `test_bant_genisligi_carpimi_boyutsuz_degil` |
| M34 | §Bölüm 3 (throughput) | Tepe FLOPS ancak büyük yığında erişilir; küçük yığında iş bellek-bağlı | eksik_sart | `test_aritmetik_yogunluk_yigina_bagli` |

## M1 — Ortam kapanışı bozuk: \end{align">

**Yer:** §FNO-KAN büküm   **Dosya:** kuantum_dalga_bukum.tex   **Tür:** derleme

**Kaynak:**

```
|\Psi(T)\rangle &= \mathcal{P} \exp \left( -\frac{i}{\hbar} \int_0^T \left( H_{\text{FNO}}(t) + H_{\text{KAN}}(t) \right) dt \right) |\Psi(0)\rangle
\end{align">
```

**Tashih:**

```
|\Psi(T)\rangle &= \mathcal{P} \exp \left( -\frac{i}{\hbar} \int_0^T \left( H_{\text{FNO}}(t) + H_{\text{KAN}}(t) \right) dt \right) |\Psi(0)\rangle
\end{align}
```

**Gerekçe.** ``\end{align">`` diye bir ortam kapanışı yoktur; ortam kapanmadan belgenin sonuna kadar sürükleniyor. Bu tek bozukluk ``tex_denetle.py``de üç bulgu üretiyor.

## M2 — Ortam kapanışı bozuk: \end{enumerate">

**Yer:** §Durr-Høyer adımları   **Dosya:** kuantum_asgari_arama.tex   **Tür:** derleme

**Kaynak:**

```
$f(x^*)$ değerine ulaşılana kadar tekrarlanır.
\end{enumerate">
```

**Tashih:**

```
$f(x^*)$ değerine ulaşılana kadar tekrarlanır.
\end{enumerate}
```

**Gerekçe.** ``\end{enumerate">`` geçersizdir; ``enumerate`` ortamı kapanmıyor.

## M3 — Ortam kapanışı bozuk: \end{align">

**Yer:** §Adyabatik Hamiltonian   **Dosya:** kuantum_asgari_arama.tex   **Tür:** derleme

**Kaynak:**

```
H(t) &= \left( 1 - \frac{t}{T} \right) H_{\text{başlangıç}} + \frac{t}{T} H_{\text{hedef}}, \quad t \in [0, T]
\end{align">
```

**Tashih:**

```
H(t) &= \left( 1 - \frac{t}{T} \right) H_{\text{başlangıç}} + \frac{t}{T} H_{\text{hedef}}, \quad t \in [0, T]
\end{align}
```

**Gerekçe.** ``\end{align">`` geçersizdir.

## M4 — ``\end{caption{...}`` diye bir şey yok

**Yer:** §Karmaşıklık cetveli   **Dosya:** veri_akis_hizi.tex   **Tür:** derleme

**Kaynak:**

```
\end{tabular}
\end{caption{Karmaşıklık Mukayese Cetveli}
\end{table}
```

**Tashih:**

```
\end{tabular}
\caption{Karmaşıklık Mukayese Cetveli}
\end{table}
```

**Gerekçe.** ``caption`` bir ortam değil, bir komuttur: ``\caption{...}`` diye yazılır. ``\end{caption{...}`` hem açılmamış bir ortamı kapatmaya çalışıyor hem de ``table`` ortamını bozuyor; ``tex_denetle.py`` burada dört bulgu veriyor.

## M5 — Ortam kapanışı bozuk: \end{equation">

**Yer:** §1 Müşahede (reel)   **Dosya:** reel_meleke_operatorleri.tex   **Tür:** derleme

**Kaynak:**

```
\hat{U}_{\mathcal{O}_1} = \exp\left( \theta_1(\mathbf{x}) J \cdot (\hat{x}(\mathbf{x}) + \hat{p}(\mathbf{x})) \right) \in SO(2N)
\end{equation">
```

**Tashih:**

```
\hat{U}_{\mathcal{O}_1} = \exp\left( \theta_1(\mathbf{x}) J \cdot (\hat{x}(\mathbf{x}) + \hat{p}(\mathbf{x})) \right) \in SO(2N)
\end{equation}
```

**Gerekçe.** Aynı bozukluk bu dosyada **dört** yerde tekrarlanıyor (§1, §13, §komütatör, §çakışma); her biri ayrı tashih olarak kaydedildi.

## M6 — Ortam kapanışı bozuk: \end{equation">

**Yer:** §13 İspat (reel)   **Dosya:** reel_meleke_operatorleri.tex   **Tür:** derleme

**Kaynak:**

```
\hat{U}_{\mathcal{O}_{13}} |\mathcal{A}\rangle_{\mathbb{R}} = |\mathcal{B}\rangle_{\mathbb{R}}
\end{equation">
```

**Tashih:**

```
\hat{U}_{\mathcal{O}_{13}} |\mathcal{A}\rangle_{\mathbb{R}} = |\mathcal{B}\rangle_{\mathbb{R}}
\end{equation}
```

**Gerekçe.** Bkz. M5.

## M7 — Ortam kapanışı bozuk: \end{equation">

**Yer:** §Reel komütatörler   **Dosya:** reel_meleke_operatorleri.tex   **Tür:** derleme

**Kaynak:**

```
\sum_{k=1}^{41} C_{ij}^k \hat{U}_{\mathcal{O}_k} \in \mathfrak{so}(2N)
\end{equation">
```

**Tashih:**

```
\sum_{k=1}^{41} C_{ij}^k \hat{U}_{\mathcal{O}_k} \in \mathfrak{so}(2N)
\end{equation}
```

**Gerekçe.** Bkz. M5.

## M8 — Ortam kapanışı bozuk: \end{equation">

**Yer:** §Reel çakışma   **Dosya:** reel_meleke_operatorleri.tex   **Tür:** derleme

**Kaynak:**

```
\right) |\Psi_{\text{metin}}\rangle_{\mathbb{R}}
\end{equation">
```

**Tashih:**

```
\right) |\Psi_{\text{metin}}\rangle_{\mathbb{R}}
\end{equation}
```

**Gerekçe.** Bkz. M5.

## M9 — Householder yansıması durumun TAMAMINI negatiflemez

**Yer:** §8 Tenakuz   **Dosya:** meleke_kuantum_kapilari.tex   **Tür:** uniterlik

**Kaynak:**

```
\hat{U}_{\mathcal{O}_8} |\Psi_{\text{metin}}\rangle &= \begin{cases} -|\Psi_{\text{metin}}\rangle, & \text{Çelişki Var} \implies e^{i\pi} = -1 \text{ (Yok Edici Girişim)} \\ |\Psi_{\text{metin}}\rangle, & \text{Çelişki Yok} \end{cases}
```

**Tashih:**

```
\hat{U}_{\mathcal{O}_8} |\Psi_{\text{metin}}\rangle &= |\Psi_{\text{metin}}\rangle - 2 \langle \Psi_{\text{tenakuz}} | \Psi_{\text{metin}} \rangle |\Psi_{\text{tenakuz}}\rangle \quad (\text{yalnız tenakuz BİLEŞENİ işaret değiştirir}) \\ &= -|\Psi_{\text{metin}}\rangle \iff |\Psi_{\text{metin}}\rangle \parallel |\Psi_{\text{tenakuz}}\rangle
```

**Gerekçe.** ``I − 2|v⟩⟨v|`` bir **yansımadır**: yalnız ``|v⟩`` yönündeki bileşeni negatifler, ona dik bileşeni aynen bırakır. Bütün durumu ``−1`` ile çarpması ancak ``|Ψ⟩ ∥ |v⟩`` iken olur. Ölçüldü (``d=8``, rastgele birim vektörler): ``‖UΨ + Ψ‖ = 1.937`` -- sıfır değil; ``Ψ = v`` seçilirse 2.8e-16. Üstelik ``U`` üniterdir, yani ``‖UΨ‖ = ‖Ψ‖``: genlik **yok edilemez**, yalnız yeniden dağıtılır.

## M10 — Householder yansıması durumun TAMAMINI negatiflemez

**Yer:** §8 Tenakuz (reel)   **Dosya:** reel_meleke_operatorleri.tex   **Tür:** uniterlik

**Kaynak:**

```
\hat{U}_{\mathcal{O}_8} |\Psi_{\text{metin}}\rangle_{\mathbb{R}} &= \begin{cases} -|\Psi_{\text{metin}}\rangle_{\mathbb{R}}, & \text{Çelişki Var} \implies (-1) \text{ İşaret Değişimi} \\ |\Psi_{\text{metin}}\rangle_{\mathbb{R}}, & \text{Çelişki Yok} \end{cases}
```

**Tashih:**

```
\hat{U}_{\mathcal{O}_8} |\Psi_{\text{metin}}\rangle_{\mathbb{R}} &= |\Psi_{\text{metin}}\rangle_{\mathbb{R}} - 2 \langle \Psi_{\text{tenakuz}} | \Psi_{\text{metin}} \rangle |\Psi_{\text{tenakuz}}\rangle_{\mathbb{R}} \quad (\text{yalnız tenakuz BİLEŞENİ}) \\ &\quad \text{ve } \| \hat{U}_{\mathcal{O}_8} \Psi \| = \| \Psi \| \text{ olduğundan genlik YOK OLMAZ}
```

**Gerekçe.** Bkz. M9. Reel hâlde durum daha da açıktır: ``U`` diktir, norm korunur; ``v + (−v) = 0`` ancak iki vektör birbirinin tam zıddıysa olur, yansımanın çıktısı ise girdisinin zıddı değildir.

## M11 — $\sum_x \sqrt{P(x)}|x\rangle\langle x|$ üniter değildir

**Yer:** §16 İhtimal Hesabı   **Dosya:** meleke_kuantum_kapilari.tex   **Tür:** uniterlik

**Kaynak:**

```
\hat{U}_{\mathcal{O}_{16}} = \sum_x \sqrt{P(x)} |x\rangle \langle x|
```

**Tashih:**

```
\hat{M}_{\mathcal{O}_{16}} = \sum_x \sqrt{P(x)} |x\rangle \langle x| \quad (\text{ÜNİTER DEĞİL: } \hat{M}^\dagger \hat{M} = \mathrm{diag}(P) \neq \mathbf{I}; \text{ bu bir Kraus/ölçüm işlecidir, kapı değildir})
```

**Gerekçe.** ``\hat U`` gösterimi üniterlik iddia eder; oysa ``A = diag(√P)`` için ``A†A = diag(P)``dır ve ``P`` bir olasılık dağılımı olduğundan ``diag(P) = I`` ancak bütün ``P(x) = 1`` iken olur -- ki o zaman ``P`` dağılım olmaz. Ölçüldü (rastgele 4'lü dağılım): ``‖A†A − I‖_∞ = 0.859``. Doğrusu bunu bir **ölçüm işleci** saymaktır; üniter kapılarla aynı listede sayılamaz.

## M12 — $\sum_x P(x)|x\rangle\langle x|$ üniter değildir

**Yer:** §16 İhtimal Hesabı (reel)   **Dosya:** reel_meleke_operatorleri.tex   **Tür:** uniterlik

**Kaynak:**

```
\hat{U}_{\mathcal{O}_{16}} = \sum_x P(x) |x\rangle_{\mathbb{R}} \langle x|_{\mathbb{R}}, \quad P(x) = \psi(x)_{\mathbb{R}}^2
```

**Tashih:**

```
\hat{M}_{\mathcal{O}_{16}} = \sum_x \sqrt{P(x)} |x\rangle_{\mathbb{R}} \langle x|_{\mathbb{R}}, \quad P(x) = \psi(x)_{\mathbb{R}}^2 \quad (\text{ÜNİTER DEĞİL, ölçüm işleci: } \hat{M}^T \hat{M} = \mathrm{diag}(P))
```

**Gerekçe.** Bkz. M11; reel hâlde iki kat bozuk, çünkü ``√P`` değil doğrudan ``P`` yazılmış. ``diag(P)``nin kendisi de dik değildir ve üstelik Born kuralını iki kere uygular.

## M13 — Yazılan operatör üniter değil, tabanı da tutarsız

**Yer:** §11 Şek-Zan-Yakîn   **Dosya:** meleke_kuantum_kapilari.tex   **Tür:** uniterlik

**Kaynak:**

```
\hat{U}_{\mathcal{O}_{11}} = \cos(\theta_{\text{yakîn}}) |1\rangle\langle 1| + \sin(\theta_{\text{zan}}) |0\rangle\langle 1| + \frac{1}{\sqrt{2}} (|0\rangle + |1\rangle) \langle \text{şek}|
```

**Tashih:**

```
\hat{U}_{\mathcal{O}_{11}} = \begin{pmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{pmatrix} \in SO(2), \quad \theta_{\text{şek}} = \pi/4,\ \theta_{\text{zan}} \in (0,\pi/4),\ \theta_{\text{yakîn}} \to 0
```

**Gerekçe.** İki kusur: (i) yazılan işlecin sütunları dik değil -- ölçüldü, ``‖M†M − I‖ = 1.0``; (ii) ``⟨şek|`` iki boyutlu uzayda üçüncü bir taban vektörü gibi kullanılmış, oysa ``{|0⟩,|1⟩}`` tabanı iki elemanlıdır. Şek/zan/yakîn üç ayrı **durum** değil, tek bir dönme açısının üç aralığıdır; ``SO(2)`` dönmesi bunu üniterliği bozmadan verir. (Risalenin reel nüshası zaten böyle yazmış ve orası doğrudur.)

## M14 — Yapı sabitleri cebir için geçerlidir, grup elemanları için değil

**Yer:** §Komütasyon bağıntıları   **Dosya:** meleke_kuantum_kapilari.tex   **Tür:** cebir

**Kaynak:**

```
[\hat{U}_{\mathcal{O}_i}, \hat{U}_{\mathcal{O}_j}] &= i \hbar \sum_{k=1}^{41} C_{ij}^k \hat{U}_{\mathcal{O}_k} \quad (\text{41 Melekenin Lie Cebrail Yapı Sabitleri})
```

**Tashih:**

```
[\hat{H}_{\mathcal{O}_i}, \hat{H}_{\mathcal{O}_j}] &= i \hbar \sum_{k=1}^{41} C_{ij}^k \hat{H}_{\mathcal{O}_k} \quad (\text{yapı sabitleri ÜRETEÇLER için; } \hat{U} = e^{-i\hat{H}t/\hbar} \text{ grup elemanlarının komütatörü kapalı DEĞİLDİR})
```

**Gerekçe.** Yapı sabitleriyle kapalılık bir **Lie cebri** özelliğidir; üreteçler (Hamiltonyenler) için geçerlidir. Grup elemanlarının (üniter kapıların) komütatörü genel olarak o kapıların lineer açılımında değildir. Ayrıca ``ħ`` üreteçlerin ölçeğinden gelir; boyutsuz üniterlerin komütatöründe yeri yoktur.

## M15 — Dik matrislerin komütatörü $\mathfrak{so}(2N)$'de değildir

**Yer:** §Reel komütatörler   **Dosya:** reel_meleke_operatorleri.tex   **Tür:** cebir

**Kaynak:**

```
[\hat{U}_{\mathcal{O}_i}, \hat{U}_{\mathcal{O}_j}] = \sum_{k=1}^{41} C_{ij}^k \hat{U}_{\mathcal{O}_k} \in \mathfrak{so}(2N)
```

**Tashih:**

```
[\hat{X}_{\mathcal{O}_i}, \hat{X}_{\mathcal{O}_j}] = \sum_{k=1}^{41} C_{ij}^k \hat{X}_{\mathcal{O}_k} \in \mathfrak{so}(2N), \quad \hat{X}_{\mathcal{O}_k} = J \cdot \hat{H}_{\mathcal{O}_k} \in \mathfrak{so}(2N), \quad \hat{U}_{\mathcal{O}_k} = e^{\hat{X}_{\mathcal{O}_k}} \in SO(2N)
```

**Gerekçe.** Bkz. M14. Reel hâlde iddia ayrıca **ölçülebilir biçimde** yanlıştır: ``so(2N)`` yatkın-simetrik matrislerden oluşur, oysa iki dik matrisin komütatörü genelde yatkın-simetrik değildir. Ölçüldü (``n=6``, iki rastgele dik matris): ``‖C + Cᵀ‖ = 1.932`` -- sıfır olsaydı ``so(6)``da olurdu. Cebir ``U``ların değil ``X = J·H`` üreteçlerinindir.

## M16 — Zaman-sıralı üstel ancak SIRA DEĞİŞTİREN üreteçlerde çarpıma eşittir

**Yer:** §Usul (küllî idrak devresi)   **Dosya:** meleke_kuantum_kapilari.tex   **Tür:** cebir

**Kaynak:**

```
\hat{U}_{\text{Küllî\_İdrak}} = \mathcal{T} \exp\left( -\frac{i}{\hbar} \int_0^T \sum_{k=1}^{41} \hat{H}_{\mathcal{O}_k}(t) \, dt \right) = \prod_{k=1}^{41} \hat{U}_{\mathcal{O}_k}
```

**Tashih:**

```
\hat{U}_{\text{Küllî\_İdrak}} = \mathcal{T} \exp\left( -\frac{i}{\hbar} \int_0^T \sum_{k=1}^{41} \hat{H}_{\mathcal{O}_k}(t) \, dt \right) \approx \prod_{k=1}^{41} \hat{U}_{\mathcal{O}_k} \quad (\text{eşitlik ancak } [\hat{H}_{\mathcal{O}_i}, \hat{H}_{\mathcal{O}_j}] = 0 \text{ iken; aksi hâlde Trotter hatası } \mathcal{O}(T^2/n))
```

**Gerekçe.** Risalenin kendisi bir sonraki bölümde melekelerin **sıra değiştirmediğini** (``[U_i,U_j] ≠ 0``) vurguluyor; o hâlde bu eşitlik kendi iddiasıyla çelişir. Ölçüldü (4×4, üç rastgele Hermitesel): ``‖exp(−iΣH) − Πexp(−iH_k)‖ = 1.231``; aynı işlem köşegen (sıra değiştiren) ``H``lerle 2.0e-16.

## M17 — Dolaşıklık uzak melekenin durumunu değiştirmez (no-communication)

**Yer:** §Sual 2 (haberleşme)   **Dosya:** meleke_kuantum_kapilari.tex   **Tür:** mantik

**Kaynak:**

```
Bir melekedeki faz değişimi, ona bağlı diğer 40 melekenin durumunu anında ve kayıpsız olarak bükertir.
```

**Tashih:**

```
Bir melekedeki faz değişimi, dolaşık bütünün ORTAK durumunu değiştirir; fakat diğer 40 melekenin **indirgenmiş** durumu (kısmî iz) hiç değişmez -- haberleşmeme (no-communication) teoremi. Melekeler arası bilgi ancak ortak bir kapı uygulandığında veya ölçüm neticesi klasik kanalla taşındığında akar.
```

**Gerekçe.** Yerel bir üniter, ``ρ_B = Tr_A|Ψ⟩⟨Ψ|``yi **hiç** değiştirmez: ``Tr_A[(U_A⊗I)ρ(U_A†⊗I)] = ρ_B``. Ölçüldü (4×4 dolaşık durum, rastgele yerel üniter): ``‖ρ_B önce − ρ_B sonra‖ = 3.3e-16``. "Anında bükertir" cümlesi bu teoremle çelişir ve mimarîde yanlış bir haberleşme kanalı varsayımına yol açar.

## M18 — $K$ bilinmeden tur sayısı $m$ seçilemez

**Yer:** §Durr-Høyer 4. adım   **Dosya:** kuantum_asgari_arama.tex   **Tür:** eksik_sart

**Kaynak:**

```
\item $\mathbf{G}_y$ operatörü $m \approx \frac{\pi}{4} \sqrt{\frac{2^N}{K}}$ defa döndürülür; $K$, $f(x) < f(y)$ şartını sağlayan eleman sayısıdır.
```

**Tashih:**

```
\item $\mathbf{G}_y$ operatörü $m$ defa döndürülür. $K$ (yani $f(x) < f(y)$ şartını sağlayan eleman sayısı) ÖNCEDEN BİLİNMEZ; $m = \frac{\pi}{4}\sqrt{2^N/K}$ doğrudan kullanılamaz. Bunun yerine $m$, $[0, \lceil \lambda^j \rceil)$ aralığından rastgele seçilir ($\lambda = 6/5$, $j = 0,1,2,\dots$); beklenen toplam sorgu $\mathcal{O}(\sqrt{2^N/K})$ kalır.
```

**Gerekçe.** Formülün kendisi doğrudur ama ``K``yı içerir ve ``K`` aramanın **neticesine** bağlıdır. Yanlış ``m`` ile Grover dönmesi hedefi aşar ve başarı **düşer**. Ölçüldü (``N = 2^10``): gerçek ``K = 64`` iken ``K = 1`` varsayılıp ``m = 25`` koşulursa başarı **0.099**; doğru ``m = 3`` ile 0.961. Ayrıca ``2·m_opt`` turda başarı ``K=1`` için 0.9995'ten **0.0002**'ye iniyor: fazla dönmek zarardır.

## M19 — Sonlu $T$'de başarı asla \%100 değildir

**Yer:** §Adyabatik netice   **Dosya:** kuantum_asgari_arama.tex   **Tür:** mantik

**Kaynak:**

```
Böylece $t=T$ anında kuantum çipi ölçüldüğünde, %100 doğrulukla fonksiyonu minimum kılan $x^*$ noktası elde edilir.
```

**Tashih:**

```
Böylece $t=T$ anında ölçüldüğünde $x^*$ noktası $1 - \mathcal{O}(1/(g_{\min}^2 T^2))$ olasılıkla elde edilir; \%100 ancak $T \to \infty$ limitindedir ve $g_{\min}$ zor problemlerde $N$ ile üstel küçüldüğünden gereken $T$ de üstel büyür.
```

**Gerekçe.** İki kusur bir arada. (i) Yüzde işareti kaçırılmamış: LaTeX'te ``%`` yorum karakteridir, ``%100 doğrulukla ... elde edilir.`` cümlesinin **tamamı** derlemede yok olur; ``\%`` yazılmalıydı. (ii) İddianın kendisi de yanlış: adyabatik teorem bir **limit** ifadesidir; sonlu ``T``de sızıntı vardır. Ölçüldü (4 kubit, 4-döngü MaxCut): ``T = 0.5``te başarı 0.1456, ``T = 8``de 0.8987, ``T = 128``de 1.0000'e yuvarlanıyor ama hiçbir sonlu ``T``de tam 1 değil. Aynı risalenin kendi ``T ≥ ħ·max|⟨E₁|dH/dt|E₀⟩|/g_min²`` şartı da bunu söyler.

## M20 — Tünelleme olasılığı üsteldir; geçiş $O(1)$ değildir

**Yer:** §Tünelleme   **Dosya:** kuantum_dalga_bukum.tex   **Tür:** mantik

**Kaynak:**

```
Klasik sistemde aşılması imkansız olan $V(x) > E$ engelleri, kuantum dalga bükümü sayesinde üstel zamanda değil, $O(1)$ mertebesinde doğrudan geçilir.
```

**Tashih:**

```
Klasik sistemde aşılması imkansız olan $V(x) > E$ engelleri kuantum tünellemesiyle sıfırdan farklı bir olasılıkla geçilir; fakat bu olasılık $T = e^{-\gamma}$ ile ÜSTEL KÜÇÜKTÜR, dolayısıyla beklenen geçiş süresi $1/T = e^{+\gamma}$ ile ÜSTEL BÜYÜKTÜR. Kazanç $O(1)$'e inmek değil, klasik olarak sıfır olan olasılığın pozitif olmasıdır.
```

**Gerekçe.** Risalenin kendi Formül'ü (WKB) ``T = exp(−γ)`` diyor; bir sonraki cümlede aynı şeyin ``O(1)`` olduğunu söylemek kendi formülüyle çelişir. Ölçüldü (``V=1, E=0.2, m=ħ=1``): engel genişliği 1'de ``T = 7.97e-02`` (beklenen deneme 12.6), genişlik 8'de ``T = 1.62e-09`` (beklenen deneme **6.2e+08**).

## M21 — Düz bağlantı ($F=0$) holonominin trivial olmasını gerektirmez

**Yer:** §Wilson döngüsü   **Dosya:** kuantum_dalga_bukum.tex   **Tür:** mantik

**Kaynak:**

```
\item **Fasih / Muhkem Cümle:** Eğrilik $F_{\mu\nu} = 0$ (düz bağlantı) verir. Faz kayması $\Delta \Phi = 0$ olur.
```

**Tashih:**

```
\item **Fasih / Muhkem Cümle:** Eğrilik $F_{\mu\nu} = 0$ (düz bağlantı) verir. Faz kayması BÜZÜLEBİLİR çevrimlerde $\Delta\Phi = 0$ olur; büzülemeyen çevrimlerde düz bir bağlantı da trivial olmayan holonomi taşıyabilir (Aharonov--Bohm). Ölçüt bu yüzden $F = 0$ değil, $W(\gamma_S) = \mathbf{1}$ olmalıdır.
```

**Gerekçe.** Stokes ile ``ΔΦ = ∬_Σ F`` yazabilmek için çevrimin bir ``Σ`` yüzeyi **sınırlaması** gerekir. Halka gibi büzülemeyen bir bölgede böyle bir ``Σ`` yoktur ve ``F ≡ 0`` iken bile holonomi 1 olmayabilir; Aharonov--Bohm etkisinin tamamı budur. Ölçüldü (8 düğümlü çevrim, her kenarda yerel düz bağlantı, toplam akı ``0.37·2π``): ``W = −0.6845 + 0.7290i``, ``|W − 1| = 1.836``. Cümle patikaları kapalı çevrimler olduğundan bu, mimarînin tam merkezindeki bir ölçüttür.

## M22 — GRAPE gradyanı eşitlik değil, $\mathcal{O}(\Delta t^2)$ yaklaşımıdır

**Yer:** §GRAPE   **Dosya:** kuantum_dalga_bukum.tex   **Tür:** eksik_sart

**Kaynak:**

```
\frac{\partial \mathcal{F}_{\text{hedef}}}{\partial \Omega_k(t)} &= -2 \text{Re} \left[ \langle \Psi(t) | P(t) \rangle \cdot \langle P(t) | i \Delta t H_k | \Psi(t) \rangle \right]
```

**Tashih:**

```
\frac{\partial \mathcal{F}_{\text{hedef}}}{\partial \Omega_k(t)} &\approx -2 \text{Re} \left[ \langle \Psi(t) | P(t) \rangle \cdot \langle P(t) | i \Delta t H_k | \Psi(t) \rangle \right] + \mathcal{O}(\Delta t^2) \quad (\text{tam türev için } U_j \text{'nin Fréchet türevi gerekir})
```

**Gerekçe.** Bu bağıntı ``e^{-iH_j Δt}``nin ``Δt``de birinci mertebeden açılımından gelir; ``[H_j, H_k] ≠ 0`` olduğu için tam türev değildir. Ölçüldü (4 seviyeli sistem, ``T=1``): ``Δt``yi yarıya indirdikçe sonlu farkla arasındaki fark ``7.7e-03 → 2.1e-03 → 5.0e-04 → 1.3e-04 → 3.2e-05 → 8.0e-06`` diye **dörtte bire** iniyor, yani hata ``O(Δt²)``. Yaklaşım olduğu yazılmazsa yakınsamayan bir eniyilemenin sebebi aranırken yanlış yerde aranır.

## M23 — $\sum |c_i|_p^2 = 1$ bir normalizasyon şartı değildir

**Yer:** §Nefs-i Müdrike entegrasyonu   **Dosya:** kuantum_hudutsuzluk.tex   **Tür:** olcut

**Kaynak:**

```
\text{Mizan}_{\text{rasyonel}} &= \mathbb{I}\left( \sum_i |c_i|_p^2 = 1 \right) \quad (\text{$p$-Adic Kuantum Mizanı})
```

**Tashih:**

```
\text{Mizan}_{\text{rasyonel}} &= \mathbb{I}\left( \sum_i c_i^2 = 1 \right) \ \wedge\ \mathbb{I}\left( \max_i |c_i|_p \le 1 \right) \quad (\text{Born normalizasyonu ARŞİMET normdadır; $p$-adic norm ancak TAMLIK denetimi verir})
```

**Gerekçe.** Born kuralı arşimet mutlak değerle yazılır. ``|·|_p`` değerleri ``{p^k}`` kümesindedir ve toplamları bir olasılık toplamı değildir. Ölçüldü (``p=2``): normalize edilmiş ``c = (½,½,½,½)`` durumunda arşimet toplam ``Σc² = 1`` iken ``p``-adik toplam **16**; ``c = (3/5,4/5,0,0)`` durumunda arşimet 1 iken ``p``-adik **17/16**. İki ölçüt birbirinin yerine geçmez. ``p``-adik normun doğru işi, katsayıların ``ℤ_p``de kalıp kalmadığını (``|c|_p ≤ 1``) denetlemektir.

## M24 — Yuvarlama hatasının tek sebebi irrasyonellik değildir

**Yer:** §İrrasyonel sayı yanılsaması   **Dosya:** kuantum_hudutsuzluk.tex   **Tür:** mantik

**Kaynak:**

```
Kuantum çipindeki floating-point yuvarlama hatalarının tek sebebi bu hayali irrasyonel sayı kabulüdür.
```

**Tashih:**

```
Floating-point yuvarlama hatası irrasyonel sayılara mahsus değildir: ikilik tabanda sonlu açılımı olmayan RASYONEL sayılar (1/10, 1/3) da yuvarlanır. Hatanın sebebi irrasyonellik değil, sonlu mantissadır; çare de irrasyonelleri ilga etmek değil, TAM aritmetik (rasyonel veya cebirsel tamsayı) kullanmaktır.
```

**Gerekçe.** Ölçüldü: ``0.1 + 0.2 ≠ 0.3`` (fark 5.55e-17) ve ``0.1``i on kere toplamak ``0.9999999999999999`` veriyor. Her iki örnekte de bütün sayılar rasyoneldir; ortada irrasyonellik yoktur. Teşhis yanlış olunca çare de yanlış yere kurulur.

## M25 — Terim yanlış: "ultradinamik" değil, ultrametrik

**Yer:** §$p$-adic metrik   **Dosya:** kuantum_hudutsuzluk.tex   **Tür:** terim

**Kaynak:**

```
|x + y|_p &\le \max(|x|_p, |y|_p) \quad (\text{Ultradinamik Üçgen Eşitsizliği})
```

**Tashih:**

```
|x + y|_p &\le \max(|x|_p, |y|_p) \quad (\text{Ultrametrik Üçgen Eşitsizliği})
```

**Gerekçe.** ``|x+y| ≤ max(|x|,|y|)`` şartını sağlayan metriğe **ultrametrik** denir. "Ultradinamik" diye bir metrik sınıfı yoktur; aynı yanlış terim reel operatörler risalesinde de tekrarlanıyor (M26).

## M26 — Terim yanlış: "ultradinamik" değil, ultrametrik

**Yer:** §26--41 Hafıza (reel)   **Dosya:** reel_meleke_operatorleri.tex   **Tür:** terim

**Kaynak:**

```
\hat{U}_{\text{Hafıza}} &= \mathbf{I}_{\mathbb{Q}_p} \quad (\text{$p$-Adic Ultradinamik Bozulmasız Saklama Kapısı})
```

**Tashih:**

```
\hat{U}_{\text{Hafıza}} &= \mathbf{I}_{\mathbb{Q}_p} \quad (\text{$p$-Adic ULTRAMETRİK Bozulmasız Saklama Kapısı})
```

**Gerekçe.** Bkz. M25.

## M27 — İtiraz boyuta değil, keyfî durumun saklanmasına dairdir

**Yer:** §Atom sayısı kısıtlamasının reddi   **Dosya:** kuantum_hudutsuzluk.tex   **Tür:** test_yapili_durumlar_400_kubitin_otesinde

**Kaynak:**

```
Klasik bilgisayar mühendisliğindeki "300 kubitlik bir kuantum durumunun $2^{300}$ parametresi evrendeki $10^{80}$ atomdan fazladır, dolayısıyla imkansızdır" iddiası ontolojik bir hataya dayanır. Bilgi, maddenin kütlesine veya atom adedine tabi değildir.
```

**Tashih:**

```
Klasik mühendislikteki itiraz uzayın BOYUTUNA değil, KEYFÎ bir durumun katsayı katsayı saklanmasına dairdir ve o hâliyle doğrudur: genel bir $N$-kubit durumu $2^N$ karmaşık sayı ister. Fakat itiraz YAPILI durum sınıflarını kapsamaz: kararlayıcı (stabilizer) durumlar $\mathcal{O}(N^2)$ bit, düşük bağlı MPS durumları $\mathcal{O}(N \chi^2)$ sayı ile TAM olarak saklanır ve $N > 400$ bunlarda sıradan bir hesaptır. Mimarî bu yüzden "sınır yoktur" demek yerine HANGİ yapılı sınıfta çalıştığını yazmalıdır.
```

**Gerekçe.** eksik_sart

## M28 — İşaret ters: $-J H_\mathbb{R}$ olmalı

**Yer:** §Usul (reel Schrödinger)   **Dosya:** reel_meleke_operatorleri.tex   **Tür:** isaret

**Kaynak:**

```
\hbar \frac{d}{dt} |\Psi(t)\rangle_{\mathbb{R}} &= J \cdot H_{\mathbb{R}} |\Psi(t)\rangle_{\mathbb{R}}
```

**Tashih:**

```
\hbar \frac{d}{dt} |\Psi(t)\rangle_{\mathbb{R}} &= -J \cdot H_{\mathbb{R}} |\Psi(t)\rangle_{\mathbb{R}}
```

**Gerekçe.** ``iħ∂_tψ = Hψ`` ⟹ ``∂_tψ = −(i/ħ)Hψ``; ``i ↔ J`` ikamesi altında reel karşılığı ``ħ∂_tΨ = −J H_R Ψ``dır. Ölçüldü (``N=3``, ``H = A + iB``, ``t = 0.6``): ``exp(+tJH_R)`` ile doğru ``exp(−iHt)`` arasındaki fark **2.174**; ``exp(−tJH_R)`` ile fark **1.05e-15**. İşaret zamanı tersine çevirir. (Aynı işaret hatası §7 Teemmül ve §17--25 Mizan kapılarında da tekrarlanıyor; kök buradadır.)

## M29 — Hartley uzayında köşegen çarpan evrişim DEĞİLDİR

**Yer:** §15 Terkip (reel)   **Dosya:** reel_meleke_operatorleri.tex   **Tür:** eksik_sart

**Kaynak:**

```
\hat{U}_{\mathcal{O}_{15}} = \text{RHT}^{-1} \cdot R_{\text{reel}} \cdot \text{RHT}
```

**Tashih:**

```
\hat{U}_{\mathcal{O}_{15}} = \text{RHT}^{-1} \cdot R_{\text{reel}} \cdot \text{RHT}, \quad R_{\text{reel}}[k] = R_{\text{reel}}[N-k] \ (\text{ÇİFT-simetri şart}); \text{ aksi hâlde netice bir evrişim (dolaşımlı dizey) değildir}
```

**Gerekçe.** ``QFT⁻¹ diag(r) QFT`` her ``r`` için dolaşımlıdır (evrişimdir); ``RHT`` için bu **yanlıştır**. Ölçüldü (``N=8``, rastgele ``r``): ``RHT``de dolaşımlıdan sapma **0.402**, ``QFT``de 5.6e-17. ``r`` çift-simetrik alınırsa sapma 9.4e-16'ya iniyor. Sebep: Hartley evrişim kaidesi çarpım değildir -- ``H(f*g) = √N(F·G_çift + F_ters·G_tek)``. Ölçüldü: naif çarpım kaidesinin hatası **13.30**, doğru kaidenin hatası 8.0e-14. FNO süzgecini RHT'ye taşırken bu şart yazılmazsa süzgeç sessizce başka bir işleç olur.

## M30 — Genel işaret ölçülemez; parite kapısı kontrollü olmalıdır

**Yer:** §4 Fıtrâtı İdrak (reel)   **Dosya:** reel_meleke_operatorleri.tex   **Tür:** uniterlik

**Kaynak:**

```
\hat{U}_{\mathcal{O}_4} = (-1)^{\hat{P}_{\text{fıtrat\_ihlali}}} \cdot \mathbf{I} \in \mathbb{R}^{2N \times 2N}
```

**Tashih:**

```
\hat{U}_{\mathcal{O}_4} = \mathbf{I} - 2 \hat{P}_{\text{fıtrat\_ihlali}} \quad (\text{ihlal ALT UZAYINDA işaret; genel çarpan olarak $(-1)$ ölçülemez})
```

**Gerekçe.** ``(−1)^k · I`` bütün uzayı aynı işaretle çarpar; genel bir işaret hiçbir ölçümle görülmez (K7'de aynı mesele karmaşık faz için ölçülmüştü). İşaretin bir tesiri olması için ihlal alt uzayına **bağlı** olması, yani bir izdüşüm üzerinden yazılması gerekir.

## M31 — $\log^2 N$ değeri yanlış hesaplanmış

**Yer:** §Karmaşıklık cetveli   **Dosya:** veri_akis_hizi.tex   **Tür:** aritmetik

**Kaynak:**

```
Spektral Dönüşüm (FNO) & $O(N^2) \sim 10^{24}$ işlem & $O(\log^2 N) \sim 20^2 = 400$ kapı adımı \\
```

**Tashih:**

```
Spektral Dönüşüm (FNO) & $O(N^2) \sim 10^{24}$ işlem & $O(\log^2 N) \sim 39.9^2 \approx 1590$ kapı adımı \\
```

**Gerekçe.** ``N = 10^12`` için ``log₂N = 39.86``, dolayısıyla ``log₂²N ≈ 1589``. ``20`` sayısı hiçbir tabanla çıkmıyor: ``log₁₀N = 12`` (karesi 144), ``ln N = 27.6`` (karesi 764). Ölçüldü.

## M32 — $N^3/\log^2 N$ değeri yanlış hesaplanmış

**Yer:** §Efektif sürat   **Dosya:** veri_akis_hizi.tex   **Tür:** aritmetik

**Kaynak:**

```
\text{İşlem Sıkıştırma Oranı} (\mathcal{K}) &= \frac{O_{\text{klasik}}(N)}{O_{\text{kuantum}}(N)} \approx \frac{N^3}{\log^2 N} \approx 10^{28}
```

**Tashih:**

```
\text{İşlem Sıkıştırma Oranı} (\mathcal{K}) &= \frac{O_{\text{klasik}}(N)}{O_{\text{kuantum}}(N)} \approx \frac{N^3}{\log^2 N} \approx 6.3 \times 10^{32}
```

**Gerekçe.** ``N = 10^12`` için ``N³/log₂²N = 6.293e+32``, ``1e28`` değil. (``N²/log₂²N`` alınsaydı 6.293e+20 olurdu; o da 1e28 değil.) Ölçüldü.

## M33 — Bant genişliğini karmaşıklık oranıyla çarpmak boyutça geçersizdir

**Yer:** §Efektif sürat   **Dosya:** veri_akis_hizi.tex   **Tür:** boyut

**Kaynak:**

```
\text{Efektif İşleme Hızı} &= \text{Fizikî Hız} \times \mathcal{K}_{\text{mantık}} \approx \mathbf{10^{15} - 10^{18} \text{ GB/sn}}
```

**Tashih:**

```
\text{Eşdeğer Klasik İş} &= \text{İşlenen Veri} \times \mathcal{K}_{\text{mantık}} \quad (\text{birimi FLOP, GB/sn DEĞİL}) \\ \text{Fizikî İşleme Hızı} &= \frac{\text{Net Hesap Gücü (FLOP/sn)}}{\text{Token başına FLOP}} \quad (\text{gerçek veri hızı yalnız budur})
```

**Gerekçe.** ``K`` boyutsuz bir orandır (işlem/işlem); bir veri hızıyla (bayt/sn) çarpımı yine bayt/sn verir ama bu sayı **hiçbir fizikî akışa karşılık gelmez** -- çip yine saniyede 1.2 TB alıyordur. "Eşdeğer" sıfatı iki ayrı büyüklüğü (yapılan iş ile veri hızı) birbirine karıştırıyor. Nitekim aynı külliyattaki L4 GPU raporu, gerçek donanımda ``D=4096``te **1.67 MB/sn**, ``D=512``de **106.7 MB/sn** veriyor; risalenin yazdığı ``10^18 GB/sn`` ile arasında ölçülen fark **19 mertebe** (``D=4096``te 21). Risalenin formülü harfiyen uygulanırsa (``1.2 TB/sn × K``) ``7.55e44`` bayt/sn çıkar ve fark **37 mertebe** olur. İki belge aynı külliyatta olduğu için bu çelişki açıkça giderilmelidir.

## M34 — Tepe FLOPS ancak büyük yığında erişilir; küçük yığında iş bellek-bağlı

**Yer:** §Bölüm 3 (throughput)   **Dosya:** l4_gpu_hiz_raporu.md   **Tür:** eksik_sart

**Kaynak:**

```
3.1. Saniyede İşlenebilen Maksimum Token Sayısı
```

**Tashih:**

```
3.1. Saniyede İşlenebilen Maksimum Token Sayısı
(ŞART: Aşağıdaki rakamlar Tensor Core tepe gücünün doyurulduğunu, yani BÜYÜK YIĞIN (batch) ile çalışıldığını varsayar. Yığın B=1 iken her ağırlık bir kere okunup bir kere kullanıldığından aritmetik yoğunluk 1 FLOP/bayt'tır ve iş tamamen BELLEK BAĞLIDIR: ~300 GB/sn bant genişliğiyle tavan GPU başına ~3.0e11 FLOP/sn, yani tepe gücün 1/524'u. FLOP-baglı olmak icin D=512'de de D=4096'da da B >= 1024 mertebesinde yigin gerekir.)
```

**Gerekçe.** Raporun **bütün aritmetiği doğrudur** ve bu bir tashih değil, yazılmamış bir şartın eklenmesidir. Doğrulandı: 968 TFLOPS × 0.65 = 629.2 TFLOPS; ``D=4096``te 90·D² = 1.51 GFLOP/token → 416.7 bin token/sn → 1.67 MB/sn → 3.41 GB/sn tensör akışı; ``D=512``de 106.7 MB/sn. Eksik olan tek şey yığın şartıdır: ölçüldü, ``B=1``de aritmetik yoğunluk **1.0 FLOP/bayt** ve çatı **3.0e+11 FLOP/sn** (tepe gücün 1/524'ü); ``D=4096, B=4096``te yoğunluk **3922 FLOP/bayt** ve iş nihayet FLOP-bağlı oluyor. Eşik ölçüldü: her iki boyutta da ``B ≥ 1024``. Şart yazılmazsa rapor tek bir cümlelik istekte (``B=1`` etkileşimli kullanım) 500 kat iyimser okunur.
