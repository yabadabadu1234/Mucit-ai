# ZABIT -- KÜME 3–7 TERKİP EMİRLERİ (padişahın eliyle)

> Bu dosya padişahın verdiği terkip emirlerinin **harfiyen** kaydıdır.
> Sıkıştırmada kaybolmasın diye çalışma ortamına mühürlenmiştir.

## KAT'Î USUL KAİDELERİ (her kümede geçerli)

1. **Halkça isim kaidesi (KAT'Î, DEĞİŞMEZ).** Ne yazarsan yaz: her küme
   fonksiyonuna/sınıfına, o kümenin müştereken yapmaya çalıştığı işin,
   yani mahiyetinin **halkça ifade edilmiş ismi** verilecektir.
2. **Terkip sırası (dosya birleştirmelerinde).**
   a. Evvelâ **her dosyanın kendi içinde** terkip yapılacak.
   b. Sonra dosyalar **birleştirilecek**.
   c. Sonra **birleşik dosyada bir daha** terkip yapılacak.
3. **Cevher kaybı yasağı.** Hiçbir cevher seçilip imha edilmez; artakalan
   asıllar `yedek/` altına şahit olarak konur.
4. **Test yasağı.** Bütün terkip işlemleri bitmeden hiçbir test
   çalıştırılmaz. Commit için test beklenmez.
5. **Madenci usulü** (H220/H221): her dosyayı ayrı ele al → her sınıfı ayrı
   ele al → her fonksiyonu ayrı ele al → fonksiyonları kümele → kümeye
   halkça ismini ver → o ismi bir fonksiyona ver → kümenin BÜTÜN
   cevherlerini o fonksiyonun içinde bir **terkibe** getir → kümeyi tek
   fonksiyona yükselt. Aynı usul sonra sınıflara, sonra dosyalara.

---

## 🏛️ KÜME 3: DÖRTLÜ TOPOLOJİK ZIRH & MANTIK SADAKATİ
### (Topolojik Süzgeçler, Mantık Kuralları, CZ İşaret MPO'su ve Dolaşıklık Nizamının Tekil Çip Mimarîsi)

Gaye: `nefs/zirh.py`, `ogrenme/zirh.py`, `ogrenme/zirh_mizan.py`,
`kuantum/tda.py`, `nefs/sadakat.py`, `nefs/tertip.py`, `nefs/isaret.py`,
`nefs/nizam.py`, `nefs/kod_uzayi.py` -- 9 dosyaya dağılmış topolojik
süzgeçleri, mantık kurallarını, MPO işaret operatörlerini ve stabilizer
doğrulama mekanizmalarını **tek bir saf zırh çipinde (`nefs/zirh.py`)**
birleştirmek.

### I. 9 DOSYANIN CEVHER / TOPRAK BİLANÇOSU

| # | DOSYA | ALINACAK CEVHER | ATILACAK TOPRAK |
|---|---|---|---|
| 1 | `nefs/zirh.py` | Dörtlü süzgeç cebri: Sheaf `S = I − ΔΔᵀ/(‖Δ‖²+ε)`; Betti `Π_betti = exp(−λΔ_Hodge)`; Koho `Π_koho = I − Σ|ω⟩⟨ω|` (fazla adalar); Homotopi `W(γ) = Π U_k` (Wilson holonomisi). Yumuşak âzamî zırh kaybı `L = (1/τ) ln Σ w_i exp(τ ℓ_i)`. | Yalnız soyut matrisler üzerinden çalışıp MPS dalgasına enine kapı olarak vurulmaması. `ogrenme/zirh.py` ile mükerrerlik. |
| 2 | `ogrenme/zirh.py` | `_kompleks_kur`: operatörden simplisyel kompleks (Vietoris–Rips gölgesi) çıkarma. | `nefs/zirh.py` etrafında ince, lüzumsuz sarmalayıcı olması. |
| 3 | `ogrenme/zirh_mizan.py` | MPS üzerinde enine çalışan 4 süzgeç (Sheaf düzeltmesi, Homotopi işaret hizalama, β₀ adacık cezası, Kohomoloji dik yön yutma). Zayıf POVM `okuma_vektoru`. | Dalgaya σ_z ve Betti tartısı vururken ayar (gauge) takibi yapamaması. `nefs/zirh.py`deki analitik formüllerden ayrı kod yolu işletmesi. |
| 4 | `kuantum/tda.py` | Kombinatoryal Hodge Laplasyeni `Δ_k = ∂_{k+1}∂_{k+1}ᵀ + ∂_kᵀ∂_k`. Çekirdek boyutu `β_k = dim ker Δ_k`. Kahan hassas toplaması (O(1) birikim hatası). | Yalnız kütüphane seviyesinde kalıp zırh akışına MPO/projektör olarak bağlanmaması. |
| 5 | `nefs/sadakat.py` | Mantık dışı kollara CZ ile π fazı vurma (`|tasdik=1,nakz=1⟩`, `|tasdik=1,mizan=0⟩`). `sadakat_intaci`: kübit bloğunda tek geçişli yansıtma ile mantık dışı kolları söndürme. | Kural listesinin sabit kodlanması; `tertip.py` ve `mizan`dan bağımsız olması. Ayrı MPO süpürmesiyle fazladan masraf. |
| 6 | `nefs/tertip.py` | `mizan.onerme`den otomatik yasak kuralı çıkarma (`Usul.yasaklar`). Sadece ilgili değişkenleri kısıtlayarak MPO bağ boyutunu D=2'de tutma. | `sadakat.py` ile mükerrer MPO çalıştırması. 4 usul için 4 ayrı süpürme çağrısı. |
| 7 | `nefs/isaret.py` | D=2 bağ boyutlu çok-kontrollü işaret MPO'su (`cok_kontrollu_isaret`). Ancillasız `R₀ = I − 2|0…0⟩⟨0…0|` yansıtması (`sifir_yansitmasi`). | Tek başına minik dosya olarak kalması; sadakat/tertip içinde doğrudan yer alması gerekirken ayrı durması. |
| 8 | `nefs/nizam.py` | Dolaşıklık nizamı taahhüt denetimi: Kurucu (ΔS ≥ +B), Çözücü (ΔS ≤ −B), Koruyucu (\|ΔS\| ≤ B). Bölgesel ihlâl `tanh(max(0, eksik))`. | Tâlim kaybına (`kulli_kayip`) harici ek olarak verilmesi; zırhın içine gömülmemesi. |
| 9 | `nefs/kod_uzayi.py` | Stabilizer kod uzayı `|φ_{D,J}⟩`: dolaşıklıkta rank=1 kalan Clifford temsili. MPS ile stabilizer dağılımı TVD yüzleştirmesi (`yuzlestir`). | Yalnız pasif karşılaştırma aracı olması; aktif koruma projektörü olarak müdahale etmemesi. |

### II. ÇELİŞKİ VE KOPUKLUKLARIN İZALESİ

1. **Topolojik süzgeç ikiliği (soyut matris vs MPS dalga süzgeci).**
   `nefs/zirh.py` süzgeçleri soyut Ĥ matrisine projektör olarak tatbik
   ederken `ogrenme/zirh_mizan.py` aynı süzgeçleri MPS durum vektörü
   üzerinde O(N) yerel kapılarla çalıştırıyor.
   **Karar:** iki veçhe tek merkezde birleşecek: zırh çipi hem Ĥ_Dimağ
   matrisini projektörlerle budayacak (`Π_koho Π_betti 𝒮_m Ĥ_m 𝒮_m† …`)
   hem de `Yazmac` üzerindeki duruma O(N) ile enine Sheaf, Homotopi,
   Betti ve Kohomoloji kapılarını vuracak.
2. **Sadakat ve tertip MPO süpürme israfı.** `sadakat.py` 6 ayrı yasak
   için CZ vuruyor, `tertip.py` 4 usul için ayrı MPO çalıştırıyor; tek
   idrak geçişinde onlarca gereksiz süpürme doğuyor.
   **Karar:** `isaret.py`deki D=2 MPO çekirdeği temel alınıp mantık
   kuralları (`mizan.onerme`), epistemik sadakat yasakları ve R₀ intacı
   **tek bir birleşik mantık süpürmesinde** birleşecek.
3. **Nizam ve stabilizer denetiminin dilsizliği.** Melekelerin ΔS
   taahhütleri (`nizam.py`) ve Clifford kod uzayı doğrulaması
   (`kod_uzayi.py`) ana akışın dışında ayrı teftişler olarak kalmış.
   **Karar:** zırh çipi her melekenin ΔS ihlâlini doğrudan zırh kaybına
   katacak; stabilizer TVD sapması zırhın **delinmezlik mührü** olarak
   raporlanacak.

### III. TEVHİD EDİLMİŞ ÇİPİN 4 ODASI (`nefs/zirh.py`)

1. **Analitik dörtlü topolojik süzgeçler**
   - `sheaf_izdusumu`: `S = I − ΔΔᵀ/(‖Δ‖²+ε)` -- ek yeri uyumsuzluğunu yutan projektör.
   - `hodge_projektoru`: `Π_betti = exp(−λ Δ_Hodge)` -- Betti-1 deliklerini ve ezber adacıklarını temizleme.
   - `koho_suzgeci`: `Π_koho = I − Σ_{ω∈H⁰, ω≠sabit} |ω⟩⟨ω|` -- kopuk mana adalarını ve çelişkiyi sıfırlama.
   - `wilson_holonomisi`: `W(γ) = Π U_k` -- eş anlamlı dönüşümlerde faz kapalılığı `|W(γ) − 1|` denetimi.
2. **Yazmaç enine topolojik operatörleri (MPS transverse gates)**
   - `zirh_dalga_uygula(yazmac)`: O(N) karmaşıklıkla -- Sheaf (komşu yuvaların indirgenmiş yoğunluk farkını bastırma), Homotopi (baskın bileşenin işaretine faz kilitleme), Betti (β₀ > 1 adacıklarında genlik söndürme cezası), Kohomoloji (önceki uzaya dik taşınamaz bileşeni yutma ve tıkanıklık sinyali).
3. **Birleşik mantık sadakati ve işaret motoru**
   - `cok_kontrollu_isaret`: D=2 MPO bağıyla ancillasız tek geçişli mantık dışı kol işaretleme.
   - `sadakat_ve_tertip_kos(yazmac)`: Tenakuzsuzluk (`|tasdik=1,nakz=1⟩`), Ayniyet, Kâfi Sebep (`|tasdik=1,mizan=0⟩`), Kelâm ve Sükût şartları; `mizan.onerme`den türetilen formülleri süperpozisyonda **tek süpürmede** işaretleme.
   - `sadakat_intaci`: `R₀ = I − 2|0…0⟩⟨0…0|` MPO yansıtmasıyla işaretli kolları genlikte söndürme.
4. **Nizam taahhüdü, stabilizer doğrulaması ve zırh kaybı**
   - `dolasiklik_nizami_olc`: melekelerin ΔS değişimlerini Kurucu/Çözücü/Koruyucu bantlarıyla yüzleştirme.
   - `stabilizer_yuzlestir`: hüküm bloğunun tam Clifford stabilizer durumuyla MPS arasındaki TVD mesafesi.
   - `kulli_zirh_kaybi`: Sheaf, Betti, Koho, Homotopi ve Nizam ihlâllerini τ-Softmax ile tek skaler kayba indirme.

### IV. HAREKÂT PLÂNI
1. `nefs/zirh.py` merkez üs olarak açılacak.
2. Diğer 8 dosyadaki cevherler tek tek ayıklanıp `nefs/zirh.py` gövdesinde birleşecek.
3. D=2 MPO işaretleme motoru ve R₀ intaç yansıtıcısı tek çatıya bağlanıp gereksiz süpürme yükü kalkacak.
4. Hem Ĥ_Dimağ projektörlerinin hem yazmaç enine süzgeçlerinin 1e-16 hassasiyette çalıştığı ve kasten bozuk durumlarda **kırmızı yandığı** doğrulanacak (`test_zirh_butunlugu`).
5. Mükerrer 8 dosya ilga edilip geride tek `nefs/zirh.py` çipi kalacak.

---

## 🏛️ KÜME 4: ENİYİLEME MOTORU, DALGA DİNAMİĞİ & TÂLİM
### (`ogrenme/optimize.py`, `ogrenme/hoca.py`, `main/egitim.py`, `nefs/qegitim.py`, `kuantum/dalga.py`, `kuantum/nqs.py`, `kuantum/qsvt.py`, `kuantum/ceride.py`, `kuantum/bec.py`, `kuantum/fubini.py`, `nefs/gaye.py`, `nefs/ogda.py`, `nefs/tabii_gradyan.py`, `nefs/ikiz.py`)

### I. VARLIK SEBEBİ VE KÖK PROBLEM

Sistemin **nasıl öğrendiğini** tayin eden merkez. Klasik ∇L ve geri
yayılım lağvedildiği için yerine **dalga mekaniği, spektral projeksiyon,
bilgi geometrisi ve kapalı formlu cebir** ikame edilmiştir. Mevcut hâlde:
`optimize.py` sürekli uzayda GCL/FCT hat araması yapar; `dalga.py`+`nqs.py`
ayrık uzayda Metropolis-MCMC ile Grover polinomları uydurur;
`main/egitim.py` içinde 3 ayrı tâlim hattı birbirinden habersiz döner;
`qegitim.py` eski belirteç tahminli kayıpla uğraşır; `gaye.py` teleolojik
çekiciyi kurar, `ogda.py` min-max oyununu çözer, `ikiz.py` çift sayılarla
tam türev alır. 14 dosyanın **bütün hakiki cevherleri** tek çipte
(`main/egitim.py` + icra çekirdeği `ogrenme/optimize.py`) birleşecek.

### II. 14 DOSYANIN CEVHER / TOPRAK BİLANÇOSU

| # | DOSYA | ALINACAK CEVHER | ATILACAK TOPRAK |
|---|---|---|---|
| 1 | `ogrenme/optimize.py` | `KulliOptimizer` blok koordinatlı FCT hat araması; `_had_yaricap` dinamik güven kutusu freni; `_durgunluk` Grassmann asal açı takibi; `_yon_asgarisi` GCL düğümlerinde Chebyshev serisiyle analitik minimuma inme; `butce_kestirimi` koşmadan evvel FLOP/çağrı ilanı. | Skaler doğrultuda `(1,1..1)` körlüğü (yön başına GCL ile çözüldü, korunacak). Yön taramasında bütçe aşımının ön-denetimsiz kalabilmesi. |
| 2 | `ogrenme/hoca.py` | `boyut_guvenlik_siniri` (milyonluk parametrede sessiz kilitlenme yerine RuntimeError); `_vekil_sec` RKHS vekiliyle en umutlu aday; `_tunelle` H29 çift-şartlı STA tünelleme. | `KulliOptimizer`dan miras alıp sadece sarmalayıcı ekleyen gereksiz ikinci sınıf hiyerarşisi. |
| 3 | `main/egitim.py` | `EgitimAyari` (KISA_CPU, ORTA, AZAMI_KAGGLE); `tek_iplik_zorla` BLAS kilitlenmesi önleme; `_isci_kur`/`_isci_kayip` fork paralelliği; `kulli_kayip_talimi` 44 melekeyi optimize eden hat. | 3 ayrı paralel tâlim hattının birbirini ezmesi (tevhid edilecek). Şema dalgasında zırh kaybının 104.65'te sabit kilitli kalması. |
| 4 | `nefs/qegitim.py` | `belirtecleri_kodla` (girdiyi kayıpsız ±1 bit matrisine çeviren Hadamard ortogonal kodlama); `ornekler` görev bağlam-hedef veri hazırlığı. | Eski belirteç tahminli (−log P) kayıp ve MCMC dalga uydurma kalıntıları. |
| 5 | `kuantum/dalga.py` | `en_iyi_k` Grover optimal dönüş adımı k*; `grover_ikili` iki boyutlu (α,β) kapalı form genlik katsayıları; `_tartili` ESS tabanlı Boltzmann ağırlıklandırması. | Klasik GPU'da O(√N) hızlanması varmış gibi sunulan eski orak yanılgısı. Sürekli fazda faz uyumu aranması. |
| 6 | `kuantum/nqs.py` | `chebyshev` T₀..T_d(x) stabil özyineleme; analitik `log ψ_θ(x)` yapısı; doğrusal özellik uzayından kapalı form katsayı oturtma (`ozellik`, `son_kat_oturt`). | Ayrık {0,1}^N için yazılan Metropolis MCMC motorunun sürekli açı optimizasyonuna uymaması. |
| 7 | `kuantum/qsvt.py` + `kuantum/ceride.py` | `qsvt_gibbs_sogutma` exp(−βĤ) Gibbs termal filtresi; `GIBBS_FAZ_TABLOSU` çevrimdışı mühürlü faz açıları; `fct_tasarimi` XᵀX = I (κ=1.0) analitik taban; `sta_surusu` Ĥ_CD(t) = (θ̇/2)·J. | QSP faz açılarının runtime'da arandığı eski taslaklar. Eşaralıklı düğümlerin kötü koşulluluğu. |
| 8 | `kuantum/bec.py` | `bose_einstein_faz_kilidi` split-step hayalî zaman Gross–Pitaevskii faz senkronizasyonu; `faz_uyumu` Kuramoto `T = |⟨e^{iθ}⟩|`. | Sabit dt seçildiğinde dalga modlarının sönümlenmemesi (ızgaraya göre dinamik dt korunacak). |
| 9 | `kuantum/fubini.py` | `fisher_metrigi_tam` `(1/4N) Σ (φφᵀ) ⊗ Cov(P_k)` tam Fubini–Study/QFI; `fubini_study_agac_cozumu` metrik güdümlü deterministik x* okuma. | `G = ΦᵀΦ ⊗ I` kestirmesinin %59 sapması (kestirme lağvedildi, tam form tutulacak). |
| 10 | `nefs/gaye.py` | `gaye_kos` hükümden gayeye teleolojik akış; θ₀ = π/4 çalışma noktası düzeltmesi (H159). | Gaye alanının |0⟩'da kilitli kalması (π/4 ile çözüldü). |
| 11 | `nefs/ogda.py` | `OgdaTarti` entropi aynalı inişli (çarpımsal) OGDA; `oyun_degeri` Fenchel eşleniği yumuşak âzamî değeri. | Dışbükey olmayan yüzeyde tek başına GDA'nın ıraksaması. |
| 12 | `nefs/tabii_gradyan.py` | Alt uzayda Fubini–Study ön-şartlı adım `Δθ = −η (S + λI)⁻¹ ∇V`. | Geri adımlı çizgi araması olmaksızın adımların uçuruma düşmesi. |
| 13 | `nefs/ikiz.py` | `Ikiz` sınıfı: ε²=0 cebriyle tam türev taşıma; `yonlu_turev` sonlu fark gürültüsü olmadan makine hassasiyetinde yönlü türev. | SVD kesmesi gibi sıralama basamaklarına ikiz sayıların sokulmaya çalışılması. |

### III. NİHAÎ MOTORUN 5 ODASI

1. **Eniyileme karargâhı & bütçe kontrolü** -- `boyut_guvenlik_siniri`
   (d > 5000 veya bütçe aşımında güvenli durdurma), `EgitimAyari` tek elden
   konfigürasyon, `tek_iplik_zorla`, fork süreç havuzu ile paralel kayıp.
2. **Yön ve vekil arama motoru** -- HAD yarıçap freni `[−R_t, R_t]^d`;
   yön başına GCL/FCT inişi (`x_j = cos(jπ/M)` düğümlerinde okuyup
   Chebyshev serisinin analitik asgarisine inme; XᵀX = I, κ = 1.0, matris
   tersi YOK); RKHS vekil yüzeyi (Cholesky kapalı form Gauss çekirdeği);
   Grassmann durgunluk denetimi (asal açılar).
3. **Dinamik dalga ve spektral tâlim** -- QSVT dinamik Gibbs soğutması
   (mühürlü `GIBBS_FAZ_TABLOSU`); FPAA monotonik difüzyon (Yoder–Low–Chuang
   kök dizisiyle 1 − δ tavanına kilitlenme, overcooking yok); BEC
   Gross–Pitaevskii faz kilidi (20 mertebenin fazını tek makroskobik
   süperakışkan faza kilitleme, T ≡ 1).
4. **Tünelleme, çift sayılar ve oyun dengesi** -- H29 çift şartlı STA
   sürüşü (durgunluk < ε_θ VE kayıp sıkışması < ε_L ise Ĥ_CD(t) = (θ̇/2)·J
   ile O(1) tünelleme); çift sayılarla ε²=0 tam yönlü türev; OGDA min-max
   `w_{t+1} = Π_Δ[w_t · exp(η(2g_t − g_{t−1}))]` ile 44 meleke yük dengesi.
5. **Deterministik intaç & bilgi geometrisi** -- tam QFI
   `g = (1/4N) Σ (φφᵀ) ⊗ Cov(P_k)`; deterministik ağaç okuması
   `x_k* = argmax [g⁺ · ∇_θ log P(x_k = b | x_<k*)]` ile tam N adımda intaç.

### IV. KRİTİK KAİDELER (tuzak engelleme)
1. **GCL düğüm sayısı:** M derece ise düğüm sayısı **M+1**dir
   (`x_j = cos(jπ/M), j = 0..M`). M ile M+1 karıştırılmayacak.
2. **Çalışma noktası:** gaye ve sükût kapılarında θ = 0 değil **θ₀ = π/4**;
   aksi hâlde sin² türevi sıfırlanır, işaretli bastırma çalışmaz.
3. **QSP faz arama yasağı:** faz açıları runtime'da aranmaz,
   `GIBBS_FAZ_TABLOSU`ndan çekilir (padişahın 2. kat'î emri).
4. **Çift sayılar SVD sınırı:** `Ikiz` skaler ve matris çarpımlarında tam
   türev taşır; `np.linalg.svd` gibi kapalı C kütüphanelerine sokulamaz.
   SVD sınırındaki pürüzler tekil değer boşluklarıyla (s_{r−1} − s_r) takip
   edilir.
5. **Kayıp yayılımı:** ortalama σ/√n ile işareti söndürdüğünden küllî
   birleşimde LogSumExp yumuşak âzamîsi `L = (1/β) ln Σ e^{β e_i}` kullanılır.

### V. HAREKÂT PLÂNI
1. `main/egitim.py` ve `ogrenme/optimize.py` ana karargâh.
2. Kalan 12 dosyanın cevherleri 5 odalı mimariye nakledilecek.
3. `test_kulli_talim_motoru` ile GCL ortogonalliği (κ=1.0), STA tünelleme
   sadakati (>0.999), OGDA yakınsaması ve Fubini–Study deterministik intacı
   sınanacak.
4. Mükerrer ara dosyalar tasfiye edilip tek **Tâlim ve Eniyileme Çipi** kalacak.

---

## 🏛️ KÜME 5: KÜLLÎ KAYIP, ÖLÇÜ FUNKTÖRÜ & KADEME HİYERARŞİSİ
### (`nefs/kulli_kayip.py`, `nefs/olcu.py`, `nefs/kademeler.py`, `nefs/mudrike.py`, `nefs/sozlesme.py`, `nefs/tesir.py`)

### I. KÖK PROBLEM
Çok mertebeli kuantum-sembolik zihinde hatalar farklı uzaylarda doğar
(tenakuz, kopuk adacık, mîzân dengesi, sükût ihlâli, sadakat kesmesi,
istikrâ yakîni). Depodaki kök hatalar:
1. **Toplanamaz büyüklüklerin toplanması** -- `0.25·mîzân − 0.1·entropi +
   kayıp` gibi elle uydurulmuş katsayılarla metre ile kilogramı toplamak.
2. **36 melekenin eğitimsiz kalması** -- kaybın yalnız 5 küllî alanı okuyup
   44 melekenin 36'sına sıfır eğitim sinyali vermesi.
3. **Faaliyet ile isabetin karıştırılması (H45)** -- "çalıştım/konuştum"a
   1 puan vermek; modele doğru bilmeyi değil susmamayı ve uydurmayı öğretir.
4. **Yapısal kusur ile öğrenilebilir hatanın karışması (H154)** -- mimarî
   kesmenin (kapı başına 1−F) açı parametreleriyle değişmediği hâlde kayba
   sokulup yumuşak âzamîyi kilitlemesi.
5. **Ortalama alarak işareti söndürme (H145)** -- 105 uzvun ortalaması
   alınınca σ/√n ile parametre yayılımının 0.05'e çökmesi, aramanın körleşmesi.

### II. 6 DOSYANIN CEVHER / TOPRAK BİLANÇOSU

| # | DOSYA | ALINACAK CEVHER | ATILACAK TOPRAK |
|---|---|---|---|
| 1 | `nefs/kulli_kayip.py` | 44 melekenin kendi taahhüt bölgesinden zayıf okuma ile hatasını çıkarma (`meleke_olcumleri`); öğrenilebilir hata → kayba girer, yapısal kusur (kesme) → yalnız raporlanır; `olcumlu_idrak` yığın hâlinde (B) paralel geçiş; `QParametre` ile düz vektör tâlimi. | `veri` alanının POVM ortalaması alınıp "büyüğü iyi" sanılması (doymuş sıfır). Kademe ölçülerinin parametresizken kayba sokulup 18 kat seyreltme yapması. Verilerin döngüde tek tek işlenmesi. |
| 2 | `nefs/olcu.py` | Ölçü funktörü `F_S : S → 𝔐` (her uzayı müşterek [0,1] mertebe uzayına çeker; 1=Yakîn, 0=Vehim); cihet (`buyugu_iyi`) ile monotonluk dönüşümü; `yumusak_asgari` yığının en zayıf üyesi; `dinamik_beta` √n aktif uzuv hedefli ikili aramayla dinamik perpleksite LogSumExp. | Terkip kaidesinin `F_T⁻¹ ∘ F_T` ile cebren aşikâr olduğunu gizleyip delil gibi sunması (sıra koruma asıldır). `BETA = 8` sabitinin doymuş uzuv varken aramayı kilitlemesi. |
| 3 | `nefs/kademeler.py` | 6 kademe zinciri: İdrak → Tasavvur → Muhakeme → İspat → Tasdik → Beyan; **Bırak-Birini (LOO) notu** (son çifti saklayıp hakikatle yüzleştirme: Doğru=1.00 Yakîn, Sükût=0.25 Şek, Yanlış=0.00 Vehim); `_par` kademe parametrelerinin (eşik, ceza) meleke açılarıyla aynı düz vektörden öğrenilmesi; tasdik ayar notu `1 − |ilan_edilen − isabet|`. | Kademelere "faaliyet" notu verilmesi (konuştu=1, sustu=0 -- oynanabilir tuzaktı). Muhakemede kaba döngüyle şablon aranması (dalgaya bağlandı). |
| 4 | `nefs/mudrike.py` | 6 adımlı iç muhakeme: 1) vazife nevi (bulmaca/kelâm) 2) tesadüf mü (renk/şekil düzeni) 3) örtü kapanıyor mu (Čech H¹) 4) kâide/dalga nedir 5) yakîn ne mertebede (istikrâ + meclis) 6) beyan (yakîn ≥ eşik ise konuş, yoksa sus); açıklanabilir `muhakeme` düşünce günlüğü. | Čech tıkanıklığının (H¹≠0) mutlak veto sayılıp çözülebilir görevlerin atılması (ihtiyat indirimine çevrildi). Dalga güveninin yakîne girmemesi. |
| 5 | `nefs/sozlesme.py` | 44 melekenin bölge taahhüt sicili (`SOZLESME`); ayrık bölgelerde `ρ_A' = ρ_A` değişmezlik kuralı; hedef/güzergâh ayrımıyla MPS transit sapması; `dokunulan_bolgeler` ile ESIK = 1e-6 sınır testi. | Salt pasif denetim dosyası olarak kalması; ihlâllerin kayba otomatik ceza olarak akmaması. |
| 6 | `nefs/tesir.py` | Kademe 5 hassasiyet ve ablasyon teşhisi; bir meleke düşünce ‖ΔN‖, makam, sükût, nakz, mühür değişimini bileşik tartma; yapısal zaruret / tesirli / tesirsiz ayrımı. | Rastgele gürültüde model sustuğu için melekeleri "tesirsiz" ölçmesi (şahitli yapılandırılmış girdi şarttır). |

### III. NİHAÎ ÇİPİN 5 BÖLÜMÜ (`nefs/kulli_kayip.py`)
1. **Ölçü funktörü ve mertebe uzayı köprüsü** -- `OlcuUzayi` & `funktor(x,S)`
   ([alt,üst] ve `buyugu_iyi` cihetiyle [0,1] dönüşüm); `mertebele`
   (Vehim, Şek, Zan, Zann-ı gālib, Yakîn); `funktor_dogrula` monotonluk ve
   sıra koruma testi.
2. **44 meleke hata ve sözleşme muhasebesi** -- `olcumlu_idrak` yığın tek
   geçiş; öğrenilebilir ölçüler (tasdik, tenakuz, nakz, makam, sukut, kelam,
   mizan, gaye, nizam ΔS); yapısal ölçüler (MPO kesmesi) kayba GİRMEZ;
   `sozlesme_denetle` ESIK = 1e-6.
3. **6 kademeli zihinsel hiyerarşi** -- LOO notlandırması (1.00 / 0.25 / 0.00);
   tasdik ayar notu; `_par` ile `QParametre` düz vektöründen eşzamanlı öğrenme.
4. **Müdrike iç muhakeme ve açıklanabilir beyan** -- `mudrike_muhakemesi`
   ve `muhakeme` günlüğü (niçin konuştu, niçin sustu).
5. **Dinamik LogSumExp küllî toplayıcı** -- `yumusak_asgari` (zayıf halka),
   `dinamik_beta` (√n aktif uzuv), küllî kayıp
   `ℒ = (1/β)[ln Σ w_i exp(β·eksik_i) − ln Σ w_i]`.

### IV. KRİTİK KAİDELER
1. **Faaliyet notu yasağı (H45):** hiçbir kademeye "çalıştı/konuştu" diye
   1.0 verilmez; bütün notlar LOO'dan (1.00/0.25/0.00) çıkar.
2. **Yapısal kesme yasağı (H154):** MPO kesmesi (1−F) parametre değil
   mimarî özelliktir; ℒ'ye katılmaz, `yapısal_kayıp` anahtarında raporlanır.
3. **Veri alanı yasağı:** veri kübitlerinin POVM ortalaması hüküm değildir;
   melekenin ne kadar bilgi tuttuğu `exp(−Δsadakat)` ölçülür.
4. **Čech kuralı (H132):** H¹ ≠ 0 mutlak veto değil **ihtiyat indirimidir**
   (yakîni %20 düşürür).
5. **Dinamik β emniyeti:** β ikili araması √n perpleksitesini hedefler;
   tüm uzuvlar eşitse arama bırakılıp taban β kullanılır.

### V. HAREKÂT PLÂNI
1. `nefs/kulli_kayip.py` ana merkez.
2. `olcu.py`, `kademeler.py`, `mudrike.py`, `sozlesme.py`, `tesir.py`
   cevherleri gövdeye nakledilecek.
3. `KADEME_VARSAYILAN` `QParametre` düz vektörüne bağlanıp LOO çapraz
   notlandırması aktif kılınacak.
4. `test_kulli_kayip_ve_kademeler` ile funktör sıra korunumu, dinamik β
   perpleksitesi, 44 meleke sözleşme uyumu ve müdrike günlüğü doğrulanacak.
5. Mükerrer 5 ara dosya ilga edilip tek `nefs/kulli_kayip.py` kalacak.

---

## 🏛️ KÜME 6: İZAFÎ LİSAN, DUYUSAL MÜŞAHEDE, ŞAHİTLİK & VERİ
### (`nefs/lisan.py`, `nefs/mubser.py`, `nefs/sahit.py`, `nefs/sahitlik.py`, `nefs/boyut.py`, `idrak/sekil.py`, `nefs/iki_olcek.py`, `nefs/operad.py`, `nefs/kopru.py`, `nefs/gomme.py`, `idrak/arc.py`)

### I. KÖK PROBLEM
Modelin dış âlemi gördüğü, işittiği, belirteçlediği ve şahitlikten kural
çıkardığı duyu organı. Kök problemler:
1. **İki ayrı boyut/şekil indüksiyon sistemi** -- `idrak/sekil.py` kesirli
   oran ve çapraz kurallarla, `nefs/boyut.py` başka bir heuristik listesiyle;
   ikisi konuşmuyor.
2. **Kategorik renklerin sayı sanılması** -- ARC renkleri (0..9) kategorik
   semboldür; 3 ile 7 arasında parlaklık farkı yoktur. Ziyâ'nın hakikati
   **mevcudiyet (varlık/yokluk)**, Levn'in hakikati **karşıt renk eksenleri**.
3. **Mutlak koordinat bağımlılığı ve 5×5 pencere körlüğü** -- x=5, y=3 mutlak
   koordinatları genellemeyi öldürür; yerel 5×5 penceresi evaluation
   görevlerinin %60'ında cevabın pencere dışında kalmasıyla kör kalır.
4. **Şahitlerin bayrakla bildirilmesi yanılgısı** -- "bu görev 3 örnekten
   oluşuyor" dışarıdan bayrakla verilmemeli; duyu akışındaki kopma ve MAD
   eşiğiyle **bizzat sezilmeli**.
5. **Ağ bağımlı tiktoken iflası** -- yerel `o200k_base.tiktoken` dosyası
   üzerinden çevrimdışı ve deterministik çalışılmalı.

### II. 11 DOSYANIN CEVHER / TOPRAK BİLANÇOSU

| # | DOSYA | ALINACAK CEVHER | ATILACAK TOPRAK |
|---|---|---|---|
| 1 | `nefs/lisan.py` | `Kodlayici`: yerel `o200k_base.tiktoken` ile 3 kademeli (yerel → ağ → bayt) BPE motoru; `OZEL_BELIRTECLER` 19 adet; Lie öteleme üreteçleri `T̂_x, T̂_y` çevrimsel ortogonal permütasyon dizeyleri ve `D(Δx,Δy)`; `IzafiMevki` 8-komşuluk izafî örüntü kodu. | `IzafiMevki2D` sarmalayıcısının `main/cikarim.py`ye bağımlı ara kodlar taşıması. |
| 2 | `nefs/mubser.py` | İbnü'l-Heysem 22 mübser vasfı → 15 kanal. Tabaka 0: Işık (varlık/yokluk), Levn (karşıt RGB), Geçirgenlik (0=+1, dolu=−1), Mekân (retinotopik). Tabaka 1: Bağlantı (ittisal/teferruk), Doku. Tabaka 2: `Nesne`, `_sekil_tarifi` (Betti-1 delik, çevre, tıkızlık, doluluk, simetri, momentler). Tabaka 3: Emsal (`_dihedral_kanonik` 8-katlı), Süreklilik (örtme hadisesi), Küllî tenasüb, Hüsn. Tabaka 4: `devinim_olc` (hareket/sükûn, Δ kanalları). | Renklere zorla atanan eski uydurma parlaklık tablosu. `_emsal` içinde her çift için tekrar rotasyon hesaplayan döngü (kanonik dihedral ile çözüldü). |
| 3 | `nefs/sahit.py` | `bolutle`: ayıraç aramadan medyan + 3·MAD eşiğiyle ham duyudaki kopmalardan otonom şahit çıkarma; `_cerceve` merkezleme ve ölçekleme ile yerel kaymayı silip saf şekil dönüşümünü bırakma; `kulli_kaide` çapraz kovaryans toplamı `R = polar(Σ C_kᵀ G_k)` kapalı form Procrustes; `nakz_bul` LOO ile en kötü aykırı şahidi kademeli eleme. | Şahit kaidesinin satırları karışmış `S` üzerinde uydurulması (kaide ham duyu `E` üzerinde uydurulmalı). |
| 4 | `nefs/sahitlik.py` | `kanal_bagimsizligi`: iki şahit kanalının (ham duyu vs yerel hüküm) bağımsızlığını Pearson uyuşması ve `fitrat.tevafuk` ile ölçme. | Standart sürekli değişkenle fazla sayma hesabının log(NaN) üretmesi (medyan ikilileştirme şarttır). |
| 5 | `nefs/boyut.py` + `idrak/sekil.py` | `idrak/sekil.py`: `EksenKaidesi`, `SekilKaidesi` ile kesirli (`Fraction`) tam kural türetimi (oran, çapraz, sabit). `nefs/boyut.py`: `dolu_kutu`, `en_büyük_nesne`, `tek_nesne` gibi zengin geometrik kurallar. Kural bulunamazsa `(None, "sükût")`. | İki ayrı klasörde iki ayrı boyut bulma sisteminin bağımsız yaşaması. |
| 6 | `nefs/iki_olcek.py` | Sağîr (göreve mahsus kapalı form RKHS) ve Kebîr (44 meleke küllî açısı) çift ölçek ayrımı; Grassmann asal açıları (`olcek_acilari`) ile alt uzay ayrışma denetimi. | 14 boyutlu `_izgara_tarifi` vektörünün kaba kalıp çakışma üretmesi (mübser öznitelikleriyle değiştirilecek). |
| 7 | `nefs/operad.py` | `cech_tikanikligi`: gösterim yamalarının 1-kozikıl tutarsızlığından H¹ obstrüksiyonu; `tikaniklik_kapisi`: H¹'i kuantum yazmaçta sükût kübitine `R(arctan(H¹))` dönmesiyle aktarma. | H¹ ≠ 0 tıkanıklığının mutlak veto sayılması (ihtiyat indirimi olacak). |
| 8 | `nefs/kopru.py` | `belirtec_morfizmi`: belirteç → açı geçişinin sürekli diferansiyel morfizmi φ(t); `kodlamayi_olc` tersinirlik ve izometri denetimi. | İzometri bozulduğunda sessiz kalması (çarpışma sayısı açıkça sayılacak). |
| 9 | `nefs/gomme.py` | 35-kübitlik adresleme `|j⟩₁₁ ⊗ |t⟩₁₂ ⊗ |k⟩₁₂` (B=2048, L=4096, D=4096); QTT standartları (taban 2, kademe 12, bağ χ=8); `qtt_gomme` 4096-vektörü 1536 parametreye indirme. | 22M kübit ile adresleme kübitlerinin aynı şey sanılması (ayrım mühürlendi). Ham dizilerin sıfırla doldurulmadan kırpılması. |
| 10 | `idrak/arc.py` | `yukle_hepsi`, `bol` resmi 900/100/120 bölmesi; `izgara_belirtecle`/`belirtec_izgara` sıkı doğrulama (malformed ızgaraları onarmadan reddetme); `gorev_dizisi` hedef çıktıyı bağlamdan çıkararak sızıntıyı önleyen akış. | Veri yükleyicinin idrak paketinde izole bir ada olarak kalması. |

### III. NİHAÎ ÇİPİN 6 ODASI (`nefs/musahede.py`)
1. **Lisan, BPE kodlayıcı ve 35-kübit QTT gömmesi** -- `Kodlayici` (yerel
   tiktoken + 19 özel belirteç + bayt yedeği); 35-kübit adresleme
   `|j⟩_yığın(11) ⊗ |t⟩_yer(12) ⊗ |k⟩_mana(12)`; `qtt_gomme` (12 ikili QTT
   çekirdeği, χ=8, 1536 parametre); `belirtec_morfizmi` tersinirlik/izometri.
2. **2D izafî hendese ve Lie öteleme üreteçleri** -- `T̂_x, T̂_y` çevrimsel
   ortogonal öteleme dizeyleri (kenarsız, sınırsız devir); `izafi_operator`
   `D(Δx,Δy) = T̂_x^{Δx} ⊗ T̂_y^{Δy}`; `IzafiMevki` 8 komşuluk örüntü kodu.
3. **İbnü'l-Heysem 15 kanallı tabakalı müşahede (`Mesud`)** -- Tabaka 0
   (hücre): Işık (varlık=+1, yokluk=−1, zıl=eğim), Levn (karşıt RGB),
   Geçirgenlik, Mekân. Tabaka 1 (kenar): Bağlantı (4-komşuluk dengesi),
   Doku (huşunet/meles). Tabaka 2 (nesne): bağlantılı bileşenler,
   `_dihedral_kanonik` (8-katlı D₄), Betti-1 delik, tıkızlık, bu'd.
   Tabaka 3 (küllî): adet, emsal, süreklilik (örtme hadisesi), küllî
   tenasüb, hüsn (intizam türevi), kubh. Tabaka 4 (devinim): `devinim_olc`.
4. **Otonom şahit bölütlemesi ve kapalı form Procrustes** -- `bolutle`
   (medyan + 3·MAD kopmaları); `_cerceve`; `kulli_kaide`
   `R = polar(Σ C_kᵀ G_k)`; `nakz_bul` (LOO); `sahitlik_denetimi`
   (Pearson uyuşması ve fazla sayma oranıyla müteber şahit sayısı).
5. **Kesirli şekil/ebat indüksiyonu ve Čech tıkanıklığı** -- `Hendese`
   (`H_out = pH·H + qH·W + cH` denklemlerini `fractions.Fraction` ile tam
   çözme); `boyut_tahmin` (yoksa `(None, "sükût")`); `cech_tikanikligi`;
   `tikaniklik_kapisi` `R(arctan(H¹))`.
6. **ARC-AGI-2 veri nizamı ve sızıntısız akış** -- `yukle_hepsi`, `bol`
   (900/100/120); `izgara_belirtecle`/`belirtec_izgara` kayıpsız gidiş-dönüş;
   `gorev_dizisi` ezber sızıntısını engelleyen akış.

### IV. KRİTİK KAİDELER
1. **Kategorik renk kuralı:** renkler sayı değildir. Işık ekseni daima
   varlık(+1)/yokluk(−1); renk mesafeleri ℝ³ karşıt renk koordinatları
   (R−G, B−Y, parlaklık) üzerinden.
2. **Kanonik dihedral emsallik:** her nesnenin 8 dönüşümü çift döngüsü
   içinde tekrar hesaplanmaz; `_dihedral_kanonik` ile nesne başına bir kere
   çıkarılıp hash ile O(1) kıyaslanır.
3. **Procrustes merkezleme şartı:** `CᵀG` uydurulurken girdi ve çıktı
   matrisleri mutlaka ortalamalarından arındırılıp (`G − Ḡ`) normalize
   edilir; aksi hâlde offset dik dönmeyi bozar.
4. **Çoklu şahit toplama kaidesi:** şahit kaideleri tek tek bulunup
   ortalanmaz; çapraz kovaryanslar toplanıp (`Σ A_k`) **tek** kutupsal
   izdüşüm alınır.
5. **Čech sükût kuralı:** H¹ ≠ 0 mutlak yasaklayıcı değil, yakîni %20
   düşüren bir ihtiyat çarpanıdır.

### V. HAREKÂT PLÂNI
1. `nefs/musahede.py` ana merkez üs.
2. 11 dosyanın cevherleri 6 odalı mimari altında toplanacak.
3. `test_musahede_butunlugu` ile yerel BPE, D₄ izafî komşuluk, 15 kanallı
   `Mesud` kaydı, otonom şahit bölütlemesi, kesirli ebat indüksiyonu ve ARC
   sızıntısız akış 1e-16 hassasiyette doğrulanacak.
4. Mükerrer 10 dosya ilga edilip tek `nefs/musahede.py` kalacak.

---

## 🏛️ KÜME 7: MATEMATİKSEL ALTYAPI, TİP TEORİSİ & ANALİTİK KÜTÜPHANELER
### (`omega_kategori_nbe/`, `mizan/`, `fitrat/`, `reel/`, `hesap/`, `akis/`, `token_uzaylari/`, `yaklasim/`, `olcek/`)

### I. KÖK PROBLEM
Sistemin üzerine bastığı değişmez matematiksel, mantıkî, geometrik ve fizikî
hakikat zemini. Bu dosyalar yardımcı kütüphane değil, her biri bir kuramsal
yanılgıyı veya fiziksel imkânsızlığı ampirik test eden **sağlama motorudur**.
1. **Tip teorisi ikiliği** (`omega_kategori/` vs `omega_kategori_nbe/`): eski
   sürüm terim seviyesinde ağaç kopyaladığı için π₁(S¹) ≅ ℤ hesabında
   takılıyordu; NbE sürümü kapanış ve ortamlarla saniyenin altında çözüyor.
   Eski sürüm tamamen tasfiye edilmeli.
2. **Dağınık mantık ve kıyas motorları** (`mizan/`): önerme mantığı, Kripke
   kiplikleri, çok-değerli mantıklar, altyapısal mantıklar ve Gazâlî mîzânı
   mükemmel çalışıyor fakat dağınık.
3. **Nedensellik ve denge ayrışması** (`fitrat/`): Bayes-ball O(V+E)
   d-ayrışması, NOTEARS çevrimsizlik değişmezi, varyasyonel serbest enerji
   (F ≥ −ln p(x)) ve BGCM oyun dengesi kenetlenmeli.
4. **Analitik geometri, tam aritmetik ve fizik kütüphaneleri**: `reel/`
   (RHT, J²=−I), `hesap/` (Galois halkası ℤ[ζ₈], p-adik norm), `akis/`
   (Lie cebri, Bochner süzgeci, Cayley çekilmesi), `token_uzaylari/`
   (Riemann metriği, Laplace–Beltrami) içindeki mükerrer sarmalayıcılar
   temizlenip tek analitik çekirdeğe indirgenmeli.

**4 temel analitik karargâh:**
* `matematik/tip_teorisi.py` (kübik tip teorisi & HoTT)
* `matematik/mizan.py` (mantık, cedel & epistemik hüküm)
* `matematik/fitrat.py` (nedensellik, illiyet & oyun dengesi)
* `matematik/geometri.py` (Riemann manifoldu, Lie cebri & tam aritmetik)

### II. CEVHER / TOPRAK BİLANÇOSU

| ALAN | ALINACAK CEVHER | ATILACAK TOPRAK |
|---|---|---|
| **1. Tip teorisi** (`omega_kategori_nbe/` vs `omega_kategori/`) | NbE indirgeyicisi (değerler, kapanışlar/ortam, Kan işlemleri); De Morgan aralık cebri (antizincir DNF normal form); Glue/Univalence `ua(e)` boyunca kayıpsız taşıma; S¹ döngü uzayı ve sarım sayısı `sarim(donguⁿ) = n`; geometri: sonsuz küçükler `D = {x | x²=0}`, teğet demeti `TX = Xᴰ`, kotanjant duali, de Rham kompleksi. | `omega_kategori/` eski sürümünün terim ağacı kopyalama yükü ve π₁(S¹) tıkanması. Postulatların hesaplanabilir gibi sunulması (açık kütük korunacak). |
| **2. Mantık & cedel** (`mizan/`) | `onerme.py` hash-consing formül düğümleri + bit-paralel doğruluk tablosu (2ⁿ değerleme tek bit); `kiyas.py` 256 monadik modelle tam karar; `cikarim.py` Dyckhoff G4ip büzülmesiz hesap; `kiplik.py` 512 Kripke çerçevesiyle K,T,4,5,B,D; `cokdegerli.py` kalıntı bağıntısı `a ⊗ b ≤ c ⟺ a ≤ (b → c)`, Priest LP paratutarlı mantığı; `altyapisal.py` doğrusal/affine/sıkı mantık, kuantum alt uzay mantığı (ortomodüler kafes); `munazara.py` Men'/Nakz/Muâraza cedeli, Gazâlî yakîn mîzânı `min(öncül) · 𝟙[şekil geçerli]`. | Kıyas darblarının ezbere listeden okunması (256 model sayımı şarttır). Łukasiewicz gerektirmesinin min ile uyuştuğu yanılgısı (T89 tashihi). Deontik D serilik şartının ihmali. |
| **3. İlliyet & denge** (`fitrat/`) | `ayrisma.py` Bayes-Ball O(V+E) d-ayrışması, arka kapı/ön kapı ölçütleri, B-ayrışması; `karsi_olgusal.py` karşıolgusal 3-pas (abduction → action → prediction), NOTEARS `h(A)=tr(e^{A∘A})−d`, örtük değişkenler; `serbest_enerji.py` `F = −ELBO ≥ −ln p(x)`, F = kesinsizlik + karmaşıklık (KL) tam ayrışımı; `denge.py` damped Newton kök bulucu, spektral yarıçap, örtük fonksiyon teoremi türevi; `tevafuk.py` şartlı bağımsızlık ağırlıklı konsensüs, fazla sayma oranı, müteber şahit. | Doğrusal olmayan gürültüde abduction tekilliğinin gizlenmesi. Locus üzerinde sadece teğet izdüşümle yürümek (Newton düzeltmesi şart). Tevâfukta sürekli veriye log atılması (medyan ikilileştirme şart). |
| **4. Geometri & aritmetik** (`token_uzaylari/`, `akis/`, `reel/`, `hesap/`, `ogrenme/`) | `manifold.py` Riemann metriği g_ij, Christoffel Γ, Riemann tensörü, Laplace–Beltrami; `morfizm.py` itme dφ, çekme φ*, metrik çekme φ*h, izometri ve konformal denetim; `kan.py` sonlu kategorilerde Lan/Ran (coend/end); `akis/lie.py` matris komütatör braketi, Jacobi, so(n) izdüşümü, kutup ayrışımı en yakın dik UVᵀ; `akis/ikmal.py` Lions konsantrasyon-tıkızlığı, RCD(K,N) Bochner eğrilik artığı, Cayley çekilmesi; `reel/hartley.py` RHT, M29 çift simetri şartı; `hesap/galois.py` ℤ[ζ₈][1/√2] tam halka aritmetiği; `hesap/padic.py` p-adik norm, ultrametrik eşitsizlik. | Grassmann log haritasında arcsin kullanılması (θ > π/4'te patlar; arctan ve Cayley şart). Tikhonov `L + εI` ile Betti-0 aramak (çekirdeği yok eder; K25). p-adik toplamın Born normalizasyonu sanılması (M23). Karmaşık Schrödinger işaret hatası (M28: `−J H_ℝ` olmalı). Hartley evrişiminin naif çarpım sanılması (M29). |

### III. 4 BİRLEŞİK ANALİTİK ÇİP (`matematik/`)
1. **`matematik/tip_teorisi.py`** ← `omega_kategori_nbe/`: De Morgan aralık
   cebri + yüz kafesi (kofibrasyonlar); NbE değerlendirme çekirdeği
   (değerler, kapanışlar, ortam, `comp`, `transp`, `hcomp`, `fill`);
   Glue/Univalence motoru; homotopi mertebeleri (h-seviyeleri) ve S¹ çember
   tümevarımı (π₁(S¹) ≅ ℤ tam hesabı); SDG geometri, sentetik teğet demeti
   `TX = Xᴰ`.
2. **`matematik/mizan.py`** ← `mizan/`: bit-paralel doğruluk tablosu;
   kıyas-ı iktiranî (256 monadik model, 24 mûteber darb, varlık faraziyesi);
   çıkarım hesapları (Hilbert denetçisi, Gentzen LK, Dyckhoff G4ip); kiplik
   (512 Kripke çerçevesi, sonlu LTL); kalıntı cebri ve çok-değerli mantıklar
   (Łukasiewicz, Gödel, ürün, nilpotent, Priest LP, Syādvāda); Gazâlî mîzânı
   ve münâzara cedeli (min t-normu).
3. **`matematik/fitrat.py`** ← `fitrat/`: graf teorik illiyet (Bayes-Ball,
   arka/ön kapı); karşıolgusal 3-pas; NOTEARS asiklik değişmezi ve gradyan
   doğrulaması; varyasyonel serbest enerji; çok failli iktisadî denge (BGCM:
   damped Newton, spektral yarıçap, IFT hassasiyet türevi); tevâfuk ve
   şahitlik.
4. **`matematik/geometri.py`** ← `token_uzaylari/`, `akis/`, `hesap/`,
   `reel/`: Riemann manifoldu; funktöryel morfizmler; Grassmann Gr(k,d)
   (asal açılar, doğru geodezik `Log = U arctan(Σ) Vᵀ`, Karcher ortalaması);
   akışlar ve tıkızlık (MCF, Fokker–Planck akı korunumu, Lions
   konsantrasyonu, RCD(K,N) Bochner süzgeci, Cayley çekilmesi `R_X(ξ)`,
   Alexandroff küre izdüşümü); Lie cebri ve dönüşümler; tam aritmetik
   (ℤ[ζ₈][1/√2] sıfır yuvarlama hatasıyla Clifford+T, p-adik norm,
   ultrametrik); reel gömme (`J² = −I` ile ℂᴺ ≅ ℝ²ᴺ, M28 doğru işareti
   `ħ ∂_t Ψ = −J H_ℝ Ψ`).

### IV. KRİTİK KAİDELER
1. **NbE zorunluluğu:** eski terim ikameli `omega_kategori/` kullanılmaz;
   `omega_kategori_nbe/` çekirdeği esastır.
2. **Kalıntı eşlenikliği (T89):** `a → b = min(1, 1−a+b)` alındığında
   eşlenik t-norm `min(a,b)` değil **kuvvetli ve** `a ⊗ b = max(0, a+b−1)`dir.
3. **Reel Schrödinger işareti (M28):** `H_ℝ = [[A, −B], [B, A]]` gömmede
   evrim üreteci `+J H_ℝ` değil **`−J H_ℝ`** olmalıdır.
4. **Hartley evrişimi (M29):** `ℋ(f*g) = √N (F·G_ç + F[−k]·G_t)` simetri
   parçalanması mecburidir; naif nokta çarpımı değildir.
5. **Grassmann log haritası (K26):** `Log_{Y₁}(Y₂)` arcsin ile kurulamaz
   (θ > π/4'te çöker); doğru formül **`U arctan(Σ) Vᵀ`**dir.
6. **Betti-0 çekirdek kuralı (K25):** Hodge Laplasyeninde Betti-0 aranırken
   `L + εI` Tikhonov yapılmaz; çekirdek doğrudan özdeğer eşik sayımıyla
   (`λ_i ≤ tol`) okunur.

### V. HAREKÂT PLÂNI
1. `matematik/` dizini altında 4 karargâh dosyası açılacak.
2. Nakil: `omega_kategori_nbe/` → `tip_teorisi.py`; `mizan/` → `mizan.py`;
   `fitrat/` → `fitrat.py`; `token_uzaylari/`, `akis/`, `reel/`, `hesap/`,
   `ogrenme/` analitik araçları → `geometri.py`.
3. `test_matematik_butunlugu` ile π₁(S¹) sarım sayısı, 256 kıyas modeli,
   NOTEARS gradyanı, Bochner eğriliği, Grassmann arctan log haritası ve
   Galois halka norm korunumu mühürlenecek.
4. Eski mükerrer paketler (`omega_kategori/`, `mizan/`, `fitrat/`, `reel/`,
   `hesap/`, `akis/`, `token_uzaylari/`, `yaklasim/`, `olcek/`) tasfiye
   edilip temiz bir `matematik/` çekirdeği kalacak.

---

## 🏁 NİHAÎ PANORAMA -- 5 TAŞIYICI SÜTUN

| # | ÇİP | KÜME |
|---|---|---|
| 1 | `kuantum/yazmac.py` | KÜME 1 -- 1D/2D/HDTF/QTT kuantum durum yazmacı ve tensör motoru |
| 2 | `nefs/melekeler.py` | KÜME 2 -- 44 meleke, 20 mertebe ve Lie cebri dimağ manifoldu |
| 3 | `nefs/zirh.py` | KÜME 3 -- dörtlü topolojik zırh, mantık sadakati ve MPO işaret çipi |
| 4 | `main/egitim.py` | KÜME 4 & 5 -- deterministik QSVT/FCT/STA tâlim motoru & funktöryel küllî kayıp |
| 5 | `nefs/musahede.py` | KÜME 6 -- izafî 2D lisan, 15 kanallı mübser duyu organı ve şahit bölütlemesi |
| * | `matematik/` | KÜME 7 -- sistemin bastığı değişmez analitik, tip teorik ve geometrik zemin |
