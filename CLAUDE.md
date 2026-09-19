# MUCİT-AI -- EMİRNÂME (TABLOLU)

| Bab | Muhteva |
| :-- | :-- |
| § 1 | İPTAL OLAN USULLER TABLOSU |
| § 2 | YASAKLAR TABLOSU |
| § 3 | YAPILMASI ZARURİLER TABLOSU |
| § 4 | BÜTÜN SİSTEMİN DURUM MAKİNESİ ŞEMASI |

| Kaide | Hüküm |
| :-- | :-- |
| Bağlayıcılık | Her satır emirdir; ihlâl edilirse yapılan iş geçersizdir. |
| Okuma | Her oturumun başında bu dosya baştan sona okunur. |
| Genişleme | Padişah *bundan böyle · bundan sonra · ebediyyen · artık · asla · daima · her defasında · bir daha* dediğinde o söz cevaptan **evvel** buraya satır olarak eklenir (F 1-B). |
| Atıf | Her satırın sonundaki `F …` o hükmün ferman numarasıdır; hüküm o fermanın tam metnidir, satır onun mührüdür. |

---

# § 1. İPTAL OLAN USULLER TABLOSU

Çağrılamaz. Kodda durursa fazlalıktır ve kökünden kesilir (F 2-B).

## 1-A. TAŞIYICI VE YAZMAÇ

| # | İPTAL OLAN | YERİNE GELEN | F |
| :-- | :-- | :-- | :-- |
| 1 | SVD / MPS / bond truncation | Qudit; durum TAM tutulur | 7 |
| 2 | TTN / MERA / tensör büzülmesi | KAN-NQS fonksiyoneli | 2-T |
| 3 | İkili kübit kodlaması | Qudit seviye kodlaması | 7 |
| 4 | O(d²) GEMM / yoğun 4096 matris | Matrix-free Kronecker-SIMD [16,16,16], L1'de | 7 |
| 5 | Sürekli açılı kapıyı kübit tabanında vurmak | Matchgate/FLO düalitesi, SO(2N) Givens, χ_stab = 1 | 7 |
| 6 | Gayri-lineerliğin sürekli B-spline olması | Rijndael-Galois otomorfizmi `x ↦ x²⁵⁴` | 7 |
| 7 | Köşegen fazı genlik vektörüne tek tek vurmak | Faz üssünü `Z_m`de biriktirmek | 7 |
| 8 | Kombinatorik monom taraması | `vpshufb` faz otomatı, 64 baytlık LUT | 7 |
| 9 | Ana akışta Python/dispatch ve tahsis | Sıfır tahsisli kaynaşık C çekirdeği | 7 |
| 10 | TDD'nin HESAP MOTORU olması | TDD yalnız kanonik denetçi, O(1) adres | 7 |
| 11 | `kuantum/kubit_taksimati.py` | İmha; taksim edilecek zincir yok | 7 |
| 12 | Sürekli Hilbert ℂ^d + float genlik **faz kanadında** | Galois GF(2⁸) + stabilizer tableau | 7, 2-J |
| 13 | Transandantal faz e^{iθ} **faz defterinde** | Palmer 2-bit rotasyonu `i(a,b) = (−b, a)` | 7, 2-J |
| 14 | `_kok_tablosu` ve `faz`ın `motor != "galois"` kolu | İmha | 2-J |
| 15 | Aşkın yasağının **gövdede** geçerli olması | Kalktı: `exp·cos·sin·eigh` çağrılır; muhasebe kaldı | 2-Ş, 2-U |
| 16 | Tekrarlama bağıntısı ikamesi `T_{j+1}=2u·T_j−T_{j−1}` | Hakikî `cos(j·arccos u)` / `sin` | 2-U |
| 17 | `_psi = (B, d)` açık dizisi | Mahallî yazmaç ℂ^{N×q} + turda bir KAN çağrısı | 2-Ĝ |
| 18 | `_psi`yi bir özellik (property) yapmak | Kazınır; kefeler üç kaynağa doğrudan bağlanır | 2-Ĝ |
| 19 | `yer = d ÷ sözlük` bağlam ekseni | Bağlam mahallî yazmacın qudit indisinde | 2-Ĝ |
| 20 | `d = veri_lifi × karo × karo = 65 536` | Uydurmadır, kesildi; yerine hiçbir sayı konmaz | 2-Ù |
| 21 | Mahallî yazmacın `ℝ^{N×2}` (genlik, faz) taşıyıcısı | `ℂ^{N×q}`, 1 048 576 × 64 × 16 bayt = 1 GiB | 2-V |
| 22 | Zırhın 16 MB olması | 1 GiB; sabitlik bâkî, rakam değişti | 2-V |
| 23 | Sabit ebatlı yazmaç; bağlamın harmonik tek skalere ezilmesi | Yazmaç seviyesi ≥ bağlam penceresi; her basamak kendi seviyesine | 2-M |
| 24 | Doldurma (padding) -- hem faz yazması hem dizinin kendisi | Alt sınır yoktur; 45 basamaklık suâl 45 basamaklık durumdur | 2-O |
| 25 | `QAyar.kulli_alanlar` on bir bölge + `q.bolge_var` | **Açık çelişki:** yazmaçta bölge yoktur; kaldırılması F 2-D ile sorulacak | 1-Ş |

## 1-B. ADRESLEME VE SEKTÖR

| # | İPTAL OLAN | YERİNE GELEN | F |
| :-- | :-- | :-- | :-- |
| 26 | "Yuva" tabiri, `q.kulli(ad, j)`, `gecerli()` bekçisi | Sektörün zâtî Cartan jeneratörüne kilitlenme | 2-Ö |
| 27 | "Cetvel" lafzı; elle cetvel **ve** melekelerden aralık derleyen cetvel | DHR Cartan kök nizamı; indis kayması sıfır | 2-İ |
| 28 | Bağlam basamağı (positional index) | Veri manifoldu üzerindeki rezonans noktası | 2-Z |
| 29 | All-to-all kenet (CKW monogamisini çiğner) | Dinamik lif: gerilim tepesine kilitlenme | 2-Z |
| 30 | Statik adres ("11. meleke daima 186. sektöre") | Her kodlamada yeniden tayin | 2-Z |
| 31 | `tek(yuva)` tamsayı adresi | Kapı bütün `N` qudide tek çevrimde vurur | 2-Ú |
| 32 | Kapının dokunmadığı seyirci qudit bulunması (**kapı tatbiki kanadı**) | Dokunmadığı qudit yoktur; seyirci ilkesi `q^N`in açılmaması kanadında bâkî | 2-Ú, 2-V |
| 33 | Yığın ekseni kenetlemesi: `dilim_acisi`, `dal_agirligi` | Seyirci qudit ilkesi | 2-V |
| 34 | `QParametre` ve `p.al(anahtar, n)` tahsisat defteri | Parametre yazmacının adreslemesi | 2-R |
| 35 | `oku(adres) → float` parametre okuması | Kontrollü kapı: parametre kontrol, veri hedef | 2-R |
| 36 | `Z_m` tamsayı fazının **parametre yazmacında** olması | Sürekli Lie-Cartan açısı `θ ∈ [−π, π]` | 2-V |
| 37 | θ_cartan'ı bir milyon qudite serpmek / izdüşüm haritası aramak | Küresel ayar fazı doğrudan KAN üssüne | 2-Â |
| 38 | Her turda gerilim tepesi arama, Casimir ölçümü hamallığı | Yok | 2-Â |
| 39 | Sektörün değerinin rotasyon açısının büyüklüğü olması | Genlik ağırlığı × faz = Cartan beklenti değeri | 2-Ô |

## 1-C. ÖLÇÜM, ÜRETİM VE KARAR

| # | İPTAL OLAN | YERİNE GELEN | F |
| :-- | :-- | :-- | :-- |
| 40 | Zayıf ölçüm / POVM / "hafif okuma" | Klon (`psi.copy()`) + klon üstünde TAM ölçüm | 1-T |
| 41 | Nihaî cevapta Born çökmesi (F 1-T'nin istisnası) | Deterministik Fubini-Study okuması `argmax[g_FS⁺·∇log P]` | 2-T, 2-Ĵ |
| 42 | `nefs/soyle.py:_sec` Born çekilişi / zar | Aynı | 2-Ĵ |
| 43 | Kör `temperature` örneklemesi | Vakum kıvılcımı (`nefs/ayna.py`) -- yalnız durum üretiminde, intaçta değil | 7, 2-Ĵ |
| 44 | `_mertebe_adi`nin `argmax` ile tek mertebe seçmesi | Tayf süperpozisyonda taşınır ve raporlanır | 2-Ú-B |
| 45 | Hâlin basamak ekseni boyunca `\|ψ\|²` toplamı | Aktif hedef quditin izdüşümü | 2-Ê |
| 46 | KAN'ı sözlük boyunda şişirmek | Turda tek küllî çağrı | 2-Ê |
| 47 | `kodla` içinde KAN çağrısı | Hazırlık → evrim → intaç (KAN bir kez) → ölçüm | 2-A |
| 48 | Ebat kestiren yardımcı mimari (satır/sütun) | Tek model; ebat modelin metninden ayrıştırılır | 1-P |
| 49 | "Kalıp bilinmiyor" sükût sebebi | Ayrıştırılamayan cevap **yanlış cevap** sayılır | 1-P |
| 50 | Konuşmayı reddetmek ("bu akla mugayirdir, üretmiyorum") | Ret kapıda, **girecek veri** hakkında: kabul/tasnif + hafıza kaydının cinsi | 2-Ó |
| 51 | `ℓ_Uzunluk` ayrı kefesi / uzunluk kestiricisi | `ℓ_Dizi` bütün uzunlukları zaten beraber öğrenir | 2-Ó-B |
| 52 | Çıktıya üst hudut koymak | Durma modelin hükmüdür; üst hudut yoktur | 2-Ó-B |
| 53 | Pencereyi azamî görev boyuna kısmak (798, 158) | pencere = 1 048 576 belirteç | 2-Õ |
| 54 | Pencerenin bütçe artığı olması | Verinin ölçülen boyundan türer; bütçe pencereyi kısamaz | 1-Ö |

## 1-D. MİZAN, ÖĞRENME VE ENİYİLEME

| # | İPTAL OLAN | YERİNE GELEN | F |
| :-- | :-- | :-- | :-- |
| 55 | Kör NLL / CrossEntropy | Mîzân-ı Küllî (`nefs/kulli_mizan.py`) | 7 |
| 56 | Meclis: `zayif_halka(ne="azamî")`, `ℒ_Meleke` skaleri | Her meleke ayrı kefe; mizan bir kefeler listesidir | 1-U |
| 57 | `KulliMelekeManifoldu` | İmha | 1-U |
| 58 | Skaler kayıp | Kayıp vektördür `ℒ = (ℓ₁ … ℓ_m)` | 1-V |
| 59 | Cinse göre ayrı kayıp gövdesi `if cins == "arc": … else:` | Tek hata fonksiyonu; cins **ağırlık** olarak girer | 1-S |
| 60 | Keyfiyetin adım kabulünde mutlak veto olması | Keyfiyet bir kefedir; kabul tam mizan vektöründen | 2-Ü |
| 61 | `PAYLAR` sabit tablosu ve `paylar_olc` | λ nispeti Birleşik Hamiltonyen'den: `Ĥ.nispetler()` | 2-Þ |
| 62 | `lam_hiz` hayalet kefesi | Kesildi | 1-M |
| 63 | 18 kör çağrı: `V_ilk`, `_had_yaricap`, `_toptan_yon` | Tek hamlede analitik eğim `2·Im⟨ψ|Üreteç_a·Hata|ψ⟩`; kayıp çağrısı sıfır | 2-P |
| 64 | Hat araması; Gauss-Chebyshev-Lobatto düğümlerinin **arama** olarak kullanılması | Yarıçap yalnız adımın boyudur, tarama daveti değildir (GCL, Chebyshev dönüşümünün düğüm kümesi olarak bâkîdir) | 2-P, 2-T |
| 65 | F 1-V'nin türev yasağının **yön** kanadında geçerli olması | Türev analitik alınır; yanına dört memur verilir; kayıp vektör kalır | 2-P |
| 66 | DUVAR memuru ve `mecz`in maske kolu | Dört memur: EĞİM · ÇUKUR · VADİ · NAKİL. Eleme hiç yoktur | 2-Ú, 2-P |
| 67 | F 2-P'nin "eleme yalnız duvarın işidir" satırı | Kalktı | 2-Ú |
| 68 | Tenakuzlu örneğin tâlimden çıkarılması | Terfi: iki örnek de girer, ayrı modalite yapraklarına | 2-Ú |
| 69 | Süre haddi `AZAMI_SANIYE` | Kalktı; bedeli anbean nöbettir | 2-G |
| 70 | Süre haddi kalkınca **örneği** büyütmek (88 kat, OOM) | Küme bellekten, tur süreden, veri imleçten | 2-I |
| 71 | Profile göre (`dimag_dar`, `dimag_orta`) ayrı hazine dosyası | Tek tâlim dosyası; profil bir bütçedir, ayrı model değil | 1-Y |

## 1-E. ÂLEM, VECİH VE MUKAYESE

| # | İPTAL OLAN | YERİNE GELEN | F |
| :-- | :-- | :-- | :-- |
| 72 | Âlem adının `"%s.%s" % (tayf, mertebe)` diye uydurulması | `matematik/sonsuz_mertebeler_teorisi.py`den fiilen türetilen ∞-kategori | 2-Ā |
| 73 | `ℓ=2 KATEGORİ, ℓ=3 TİP` sırası | nokta < uzay < tip < **kategori** (en umumî) | 2-Ā |
| 74 | Tek indisli `ℓ ∈ {0,1,2,3}` merdiveni | `(r, n)` çifti; r = nesne, n = morfizm mertebesi; tavan `(∞, ∞)` | 2-Þ |
| 75 | `"∞-kategori"` ve `"∞-tip"` iki ayrı taşıyıcı adı | Tek taşıyıcı: `(r, n)`-kategori | 2-Þ |
| 76 | Elle yazılmış `VECIHLER` listesi (`genlik`, `faz`, `fark`, `dilim`) | Vecih ∞-kategori ve ∞-tip teorisinden neşet eder | 2-Ú |
| 77 | Vechin rank-1 izdüşüm `t·⟨t\|v⟩` olması | Vecih bir **âlem** taşır: ⟨Âlem, Kaideler, Taşıyıcı Mertebe⟩ | 2-Ú |
| 78 | Vechin yoğunluk matrisinin **özdeğerinden** neşet etmesi | Münasebetin (Δ₂, Δ₃) kaide imzasından; aynı imza bir âlemdir | 2-Ú |
| 79 | Küllî matris ameliyesinin (eigh, svd) vecih istihracında çağrılması | Çağrılmaz | 2-Ú |
| 80 | Statik vecih listesi / bir defa koşup elde tutulan cetvel | Ateşleme → doğum → ameliye → **kapanış** | 2-Ú-D |
| 81 | "Yetersiz olduğu için vecih değiştirme" | Yetersizlik tek başına sebep değildir; J-aynası · tensörel terkip · üst mertebe tefekkür | 1-Ğ |
| 82 | Şahit (üçgenin üçüncü kutbu) | Ayniyet ↔ ihtilaf: çift bütün vecihlerde tartılır | 2-Ú |
| 83 | `kapi_tertibi`nin `a = i % len(H)` keyfî eşleşmesi ve `son_haller()` | Örneğin kendi hâli, kendi eşi | 2-Ú |
| 84 | Kapının ham örneğe bakıp anahtar eşleşmesiyle hüküm vermesi | Kodlamadan **sonra**, üç hudut hâl üstünde Bargmann ile | 2-Ú |
| 85 | `çevrim_boyu` sabiti | Bütün halka boyları `2..m` beraber | 2-Ú |
| 86 | Kaidenin "cebirsel eşleşmenin sıfıra/simetriye/rank'a eşitliği" şartına indirgenmesi | Kaide bir **kanunlar manzumesidir**: tip · kategori · uzay · nokta seviyelerinde aksiyomlar | 2-Ú-E |
| 87 | Sorgunun dışarıdan rastgele seçilen vektör yahut öğrenilen parametre olması | Kanonik (öz) evrensel operatör; öğrenilmez | 2-Ú-E |

## 1-F. HAFIZA

| # | İPTAL OLAN | YERİNE GELEN | F |
| :-- | :-- | :-- | :-- |
| 88 | Hafızadan silme / budama; "gereksiz yer" hükmü | Kayıt silinmez, yeniden tertiplenir (dört adım) | 2-Ú |
| 89 | "Hafızasını kendi silecek" (F 2-Þ'nin 4. maddesi) | Unutma yok, **tecrit** var: üst mertebeden balyalama | 2-Ƶ |
| 90 | "Genlik söner, faz kalır" teklifi | Sönme de bir unutmadır; ilga | 2-Ƶ |
| 91 | "Ne sileceğiz, ne silmeyeceğiz" hesabının kendisi | Tek suâl: hangi üst kategori bu yığını balyalar? | 2-Ƶ |
| 92 | Hafıza için üçüncü bir yazmaç | Mevcut qudit taşıyıcısı: kayıt ℂ^q, adres Cartan kökü | 2-Ú-C |
| 93 | Her mizan çağrısında yeniden tertip koşması | Küme kapanınca bir defa | 2-Ú |

## 1-G. USUL VE İDDİA

| # | İPTAL OLAN | YERİNE GELEN | F |
| :-- | :-- | :-- | :-- |
| 94 | İthal grafına / erişilebilirliğe dayanan sınamalar: `tanilama/nizam.py`, `nefs/akit.py`, `tanilama/divan.py`, `YETIM_BORCU` | İmha; kodu okuyana sorulur | 1-C/a |
| 95 | `yedek/` dizini | Yoktur ve açılmayacaktır | 2 |
| 96 | "Ne iddia edilmiyor" babı (`FORMUL.md` 8. bab, `SERH.md` satırları) | İcra · sual · imkânsızlığın delili | 2-Y, 2-K |
| 97 | Kod içindeki bütün yorum satırları ve izah eden belge dizgileri | `SERH.md`ye terkip edilip taşındı | 1-W |
| 98 | "CNOT-Dihedral sınıfındadır" iddiası (derece 12 çıktı) | Siklotomik koset + Frobenius iz indirgemesi `Tr(α·x¹²) = Tr(α^{1/4}·x³)` | 7-B |
| 99 | Elle yazılmış ARC kâideleri, öznitelik mühendisliği, göreve mahsus çözücü | Motor | 6, 7 |
| 100 | Sırf ARC ızgarası için yazılmış, motora tabiî katkısı olmayan kod | Çöp (ölü dosya silinmez hükmünün tek istisnası) | 1-N-C |
| 101 | "En uzun zamandır okumadığım dosya" ölçüsü (kendi kuyruğunu yer) | Her turda **en eskiden yazılmış** dosya | 2-H |
| 102 | `nefs/hamiltonyen.py`, `nefs/cozum_uzayi.py` ayrı dosyaları | `mukayese.py` · `kulli_mizan.py` · `soyle.py` içine terkip | 3, 2-D |
| 103 | Müşahedenin **ARC ızgarasına mahsus olma vasfı** | Mutlaka imha edilecek; kalacak olan kanadın taşıyıcısı **açık sualdir** | 2-Œ, 1-N-C |
| 104 | Mantığa sadakatin bir **alarm** yahut **kefe** olması | **Doğrulayıcı devre**: mantıksız olanın fazını eler, imha eder | 2-Đ |

---

# § 2. YASAKLAR TABLOSU

## 2-A. USUL YASAKLARI

| # | YASAK | F |
| :-- | :-- | :-- |
| 1 | Hususiden başlayıp umumide bitirmek | 1 |
| 2 | Çağrısı evvelce yazılmamış bir dosya yazmak; "şimdi bağlayacağım" demek | 1 |
| 3 | Beyan edilen kaideyi cevaptan sonraya bırakmak | 1-B |
| 4 | Ana akışta fiilen ne koştuğunu **ölçmek** (profil, coverage, erişilebilirlik, "beylik modül" sayımı) | 1-C/a |
| 5 | İthal etmeyi · listeye ad yazmayı · ayar alanı eklemeyi · rapor satırı koymayı "bağlamak" saymak | 1-C/b, 2-Ø |
| 6 | `grep` ile arama yapmak -- taht kodunda ve **bütün dosyalarda** | 1-D, 2-Ø |
| 7 | "Şu kısmı yapıldı, şu kısmı yapılmadı" demek | 1-E |
| 8 | "Ne iddia edilmiyor / … olduğu iddia edilmiyor" yazmak, hangi kılıkta olursa | 1-E, 2-Y |
| 9 | Mazereti delil saymak: "vaktim olmadı", "riskli", "büyük iş" | 1-E |
| 10 | Yeni usul gelince eskisini aynı turda imha etmemek (yarım iş) | 1-E |
| 11 | Tahtta rapor metni kurmak: `"%.4f" %`, `s += [...]`, `"\n".join(...)` | 1-G |
| 12 | Tahtın dışında koşu: `python -c`, `/tmp` betiği, `cProfile`, A/B hattı, `depo/` koşturucuları, `pytest` | 1-L |
| 13 | Tertibat planını tek başına yapmak; kenetlemek yerine ayrı kanat açmak | 2-D |
| 14 | Sıra suali sormak ("evvelâ hangisini yapayım?", "bu turda kaç aksam?") | 2-E |
| 15 | Yarım bırakılan işi "sıraya kondu" diye savunmak | 2-E, 1-E |
| 16 | Beklemek ("koşuyu bekliyorum", "neticeyi bekliyorum") | 2-Ç |
| 17 | Sual sormayı kesmek; cevabın gereğini biriktirmek ("sonraki turda") | 2-Ç |
| 18 | Bu turda yazılan/değiştirilen dosyayı okuyup "F 2-H icra edildi" demek | 2-H |
| 19 | Manasız kütük satırında konuşmak ("yeni bir şey yok", "koşu sürüyor", "bekliyorum") | 2-N |
| 20 | Koşuyu arkada bırakıp unutmak | 2-G |
| 21 | Dakka başı test; sınamaya mecbur kalacak kadar dikkatsiz olmak | 2-Ø |
| 22 | Padişaha bağlanmamış kod bırakmak; "içe aktarıp rapor verdirdim" diye bağladığını iddia etmek | 2-Ø |
| 23 | Padişahın verdiği metinde yalnız suâle bakan yeri okumak | 2-ẞ |
| 24 | Metindeki **misali** esas sanmak | 2-ẞ |
| 25 | Metni okuyup eski çerçeveye bir madde eklemek (metin ilave değil ikamedir) | 2-ẞ |
| 26 | Kod içine yorum yahut izah eden belge dizgisi yazmak | 1-W |
| 27 | Misal kodu körü körüne kopyalamak; yorumundaki iddiayı gövdesinde yokken tekrarlamak | 7-C |
| 28 | "Zabıt ℂ^d diyor, o hâlde F 7 kalksın" -- ve tersi: "F 7 var, bu formül icra edilemez" | 7-D |
| 29 | Terkibi ölçerek ispat etmek (`assert abs(a(x)−b(x)) < 1e-12`) | 3-B |
| 30 | İki şeyi aynı isim altına koyup terkip demek | 3 |
| 31 | `except` ile sessiz ikame | 5 |
| 32 | Yapılmayan şeyi yapıldı diye yazmak | 5 |
| 33 | HF jetonunu yahut herhangi bir sırrı depodaki bir dosyaya yazmak (yalnız `${{ secrets.HF_TOKEN }}`) | Padişah emri |

## 2-B. İMHA VE TERTİP YASAKLARI

| # | YASAK | F |
| :-- | :-- | :-- |
| 34 | İptal olanı yedekte tutmak; "ileride lâzım olur" | 2 |
| 35 | Dört mazeret: "başkası da ithal ediyor" · "bir kısmı işe yarıyor" · "referans olsun" · "silmek şunu kırar" | 2-B |
| 36 | Bu safhada delilsiz imha; "koşmuyor", "bağlı değil", "bana zorluk çıkardı" | 2-C |
| 37 | Devletin kalemini kullanmak: kısayol, geçici bayrak, "şimdilik kapatalım" | 2-C |
| 38 | Tek hamlede her şeye el atmak; orduyu dümdüz ileri sürmek | 2-C |
| 39 | Yeni dosya açıp eskisini kesmek (cerrahî **yerinde** yapılır) | 2-Ú, 2-D |
| 40 | Kopuk dosya bırakmak; "bağlantısı yok ama işini görüyor" | 1-Z |
| 41 | İki yerde iki ayrı sayı tutmak (çift başlılık); ikisini "yaklaştırmak" | 1-M |
| 42 | İkinci bir tertip yolu, ikinci bir motor, ikinci bir ileri geçiş açmak | 2-Ú, 1-M |
| 43 | Tarifi gelmemiş melekeyi "cinsi tayin edilmemiş" diye kesmek; `𝒪44`ü silmek | 2-Ú, 1-Ş |
| 44 | Melekeleri kendi başıma tasnif etmek | 2-Ú |

## 2-C. MİMARÎ YASAKLARI

| # | YASAK | F |
| :-- | :-- | :-- |
| 45 | Yazmacı bölgelere/tahsisata taksim etmek | 1-Ş |
| 46 | `q^N`i herhangi bir yerde açmak (kapasite uzay iddiasıdır, bellek iddiası değil) | 2-T, 2-V, 2-Ĝ |
| 47 | Çıplak parametre: `float` dizisi, `p[17]` diye okunan açı | 2-R |
| 48 | Körlemesine parametre çoğaltmak ("39 katına çıkaralım") | 2-R |
| 49 | Kapasiteyi `2N` sanmak (`2N` yalnız mahallî serbestliktir) | 2-R |
| 50 | Darlığı çözüm saymak ("16 yuvaya sığdıralım"); hadde kadar açmayıp boşluk bırakmak | 2-S |
| 51 | Sırf mahallî yazmaç (dolaşıklık sıfır) yahut sırf fonksiyonel (adres yok) | 2-Ş |
| 52 | Mahallî zırhta dinamik bellek tahsisi (CUDA Graph bozulur, adres kayar) | 2-Ğ |
| 53 | Bağlamı yazmaca sığdırmak için kısmak; harmonik ağırlıkla sönümlemek | 2-M |
| 54 | Doldurma -- üretimde, tâlim örneğinde, değerlendirmede | 2-O |
| 55 | Seyrek senet bandı ("yalnız dokunulan indis") yahut senedin toptan kaldırılması | 2-V |
| 56 | Arada bekçi koyup kapıyı sessizce düşürmek; sektör indisini elle yamamak | 2-Ö |
| 57 | KAN'ın `C`, `S` katsayılarına çıkarım anında dokunmak | 2-Û |
| 58 | Turda iki KAN çağrısı; `kodla` içinde KAN çağrısı | 2-A |
| 59 | Melekeyi "hâle vurulan bir şey" saymak; hâli melekelerin terkibine indirmek | 1-Ç |
| 60 | Tersi (`F⁻¹`) olmayan bir hâl açmak | 1-Ç |
| 61 | Sual üreticinin bir sual **vektörü** üretmesi | 1-Ç |
| 62 | Hâlin **içini** tartışmak (içi riyaziye ile tayin olunur; ıslah edilecek yer motorun seçimidir) | 1-Ç |
| 63 | Hâli bir **kip seçici** olarak kullanmak; mizanda **dal** açmak | 1-Ç, 1-S |
| 64 | Vechi açık bırakmak (açılan ≠ kapanan) | 2-Ú-D |
| 65 | Her meseleye ayrı uzay / ayrı Hilbert havuzu açmak (kovaryans ölür) | 2-Þ |
| 66 | `N` tane kutu çizmek; sabit boyutlu mesele vektörü açmak | 2-Þ |
| 67 | Yavaş modu elle yazmak ("`k` daima yavaştır") | 2-Þ |
| 68 | Çözüm uzayını her vakit koşturmak; kip anahtarıyla, bayrakla açmak | 2-Ý |
| 69 | Kalbe (`sonsuz_mertebeler_teorisi`) aracı zincirle ulaşmak | 2-Ý, 2-C |
| 70 | "Âlem" lafzını ∞-kategori fiilen çağrılmadan yazmak; âlem adı uydurmak | 2-Ā |
| 71 | Jeton bağına ara katman, MLP, izdüşüm matrisi, öğrenilen ağırlık koymak; SFT safsatası | 2-Æ |
| 72 | Rezonansı tek yönlü kurmak (geri yol / norm maskesi olmadan) | 2-Æ |
| 73 | Çıktı uzayını taramak (kural uzayına kapanılır) | 2-Æ |
| 74 | Hafıza kaydını mevzudan koparacak şekilde ele almak; model ne söylediğini unutmak | 2-Þ |

## 2-D. ÖLÇÜ VE HÜKÜM YASAKLARI

| # | YASAK | F |
| :-- | :-- | :-- |
| 75 | Koda sabit eşik yazmak (`0.35`); kemiyeti eşik yapmak | 1-J |
| 76 | Donanım ölçüsünü elle yazmak; yoklanamayanı "kabul ettim" diye uydurmak | 5-B |
| 77 | Kaynağı yoklamadan cetvele yazmak ("var sanıyorum"); yol/uzantı tahmini | 1-K |
| 78 | Uzantıya uymayan diye dosya silmek (hiçbiri uymuyorsa tek dosya bile silinmez) | 1-K |
| 79 | Talimatı tahrif etmek; örtük ikame; yerini tutanı koşturup "koşturdum" demek | 1-F |
| 80 | Yalnız haber veren denetçi (istihbarat); kusuru bulup gereğini yapmamak | 1-Ü |
| 81 | İmkânsızlığı (`n = 0`) mizana kefe olarak koymak | 2-Ē |
| 82 | Cevher silmek; "bu kefe şu cinste manasız" demek | 1-S |
| 83 | 41 melekeyi tek skalere indirmek (yumuşak azamî, ortalama, softmax, norm) | 1-U |
| 84 | Salt mukayese ("Ahmet Mehmet'ten büyüktür"); vecihsiz hüküm | 1-Ğ |
| 85 | Sıralamanın bir vechi kapatması (çarpım sıralar, elemez) | 1-Ğ |
| 86 | Eleme -- yalnız mantıksızlıkta vardır; tenakuz ve kısırdöngü **tasnif** edilir | 2-Ú |
| 87 | Tip tayfını `argmax` ile çökertmek | 2-Ú-B |
| 88 | Zar atmak; stokastiklik; rastgele izdüşüm, rastgele eksen, rastgele tohumlu vecih | 2-Ĵ, 2-Ø, 2-Ú |
| 89 | Cevabı gerilim tepesine yazdırmak (nedensellik ölür) | 2-Ï |
| 90 | Taşan belirteç kimliğini sözlük mertebesine göre katlayarak susturmak | 2-L |
| 91 | Mana ve usul konuşulmadan ölçüye atlamak | 2-Ñ |
| 92 | İhtimalden ibaret öğrenme (melekeler süs olur) | 2-Ó |
| 93 | Mihenk verisini tâlim kümesine koymak | 2-Î |
| 94 | "Model bunu görmemiş olabilir" demeden evvel külliyatı yoklamamak | 2-Î |
| 95 | Mantık formülü dayatmak (kuralda `veya` yokken `veya`ya zorlamak) | 2-Ý |
| 96 | Mukayesenin dalgaya tesirini tek başıma vidalamak | 2-Ý, 2-D |
| 97 | Kuleyi (`Nokta^Uzay^Kategori^Tip^200000^1000000`) şimdi münakaşa etmek; `d` yerine uydurma sayı koymak | 2-Ù |

## 2-E. VERİ VE BELİRTEÇ YASAKLARI

| # | YASAK | F |
| :-- | :-- | :-- |
| 98 | `sozluk = 16` gibi elle sözlük ebadı yazmak | 1-N |
| 99 | İkinci bir belirteçleyici; "bu veri için bayt düzeyi yeter" demek | 1-N |
| 100 | Tek belirteç tahmin etmek; "en yüksek olasılıklı belirteç"i tek başına seçmek | 1-N-B |
| 101 | Veriseti sınırlamak, budamak; depoya eksik indirmek | 1-O |
| 102 | "Diskim/belleğim yetmiyor" demeyi hüküm saymak (boru hattının yanlış kurulduğunun delilidir) | 1-O, 2-I |
| 103 | Külliyatı tek hamlede kaba almak | 1-O |
| 104 | Hazine varken baştan başlamak; imleci kaydetmemek | 1-Y |
| 105 | Küme üç hudut temizlenmeden imleci ilerletmek | 2-I, 1-I |
| 106 | Sözlü veriyi eğitim/test diye bölmek | 1-R |
| 107 | Cinse göre ayrı motor, ayrı kayıp, ayrı yazmaç | 1-R |
| 108 | Tâlimin konuşmadan bitmesi; çıkarım ile eğitim arasında eniyileme dışında fark | 1-H |
| 109 | Zorlama katkı ile ARC uzvunu motora iliştirmek | 1-N-C |
| 110 | ARC'ı gaye saymak (mihenktir) | 2-Ø |
| 111 | Faz **defteri** kanadında aşkın çağrı (orada `Z_m` tamsayı, Palmer çeyreği bâkî) | 2-J, 2-Ş |
| 112 | `FORMUL.md`ye koşmayan ameliye yazmak; kod değişince aynı turda güncellememek | 2-K |
| 113 | Kütüğü (`docs/KUTUK.md`) tahrif etmek | 2-Y |
| 114 | **Mantığı henüz ayan beyan görünmeyen ihtimali elemek.** Maksat mantıksız olanı imha etmektir, kendimizi kilitlemek değil | 2-Đ |
| 115 | Bir süperpozisyonu sadakat devresinden **muaf tutmak** -- hangisi olursa olsun | 2-Đ |
| 116 | Çıkarımda özerk gaye koşturmak (özerklik **yalnız tâlimdedir**) | 2-Ħ |
| 117 | Kalbi şimdi inşa etmek yahut kalbe bir vazife uydurmak | 2-Ł |
| 118 | Mantık yürütmeyi (usul seferini) tek başıma makineye vidalamak -- **karar beklemektedir** | 2-Đ, 2-D |

---

# § 3. YAPILMASI ZARURİLER TABLOSU

## 3-A. İCRA USULÜ

| # | ZARURET | F |
| :-- | :-- | :-- |
| 1 | Sıra değişmez: **1 TAHT** (`main/egitim.py`, `main/cikarim.py`) → **2 ARA KAT** (`nefs/`, `ogrenme/`) → **3 HUSUSİ** (fonksiyonun kendisi). Çağrı, dosya yokken de yazılır | 1 |
| 2 | Taht baştan sona **bir kez** okunur; unutulursa baştan sona tekrar okunur | 1-D |
| 3 | Bütün dosyalar baştan sona okunur | 2-Ø |
| 4 | Kaide beyan edilince, cevap verilmeden **evvel**, bu dosyaya satır olarak mühürlenir | 1-B |
| 5 | Bağlamak = ana akışın koştuğu bir yerde fonksiyonun **fiilen çağrılması** ve neticesinin kullanılması; varsayılanda koşar, kapatılabilir, kapatılınca ölçü kırmızı yanar | 1-C/b, 5 |
| 6 | Tahtta bulunabilecek tek şey: uzvun ithali · ayarının kurulması · fiilen çağrılması · kendi beyan fonksiyonunun çağrılması | 1-G |
| 7 | Hüküm harfiyyen ve **tamamen** icra edilir; iddia edilir ve sözün ardında durulur | 1-E |
| 8 | Telafi: doğru usulle şimdi düzeltmek | 1-C/c |
| 9 | Hata ayıklama **kod okuyarak** yapılır; lâzım olan sayıyı **taht** basar | 1-L |
| 10 | Bu safhada çare tertiptir: her aksamın hangi menfeze hangi şartla vidalanacağını bilmek | 2-C |
| 11 | Kalp (taht) her uzuvla **aracısız** bağ kurar; karaciğer (çok vazifeli uzuv) her vazifesini ayrı **şartlı dal** olarak yazar | 2-C |
| 12 | Tertibat usulü: zabıt okunur → cevherleri çıkarılır → menfezi tespit edilir → **şıklar sayısıyla padişaha sunulur** → karardan sonra vidalanır ve sınanır | 2-D |
| 13 | Becerilebilen her iş **aynı anda** bitirilir; sorulacak tek şey **tetabuk**tur | 2-E |
| 14 | Her adımda sual sorulur; birden fazla yol belirince yahut tek yol iş görmeyince fikir sorulur | 2-Ø, 2-Ç |
| 15 | Cevabın gereği **anında** yapılır, sonra yeni sual sorulur | 2-Ç |
| 16 | Üç şıktan biri: **icra et** · **sual sor** · **imkânsızlığın delilini koy**. Dördüncüsü yoktur | 2-Y |
| 17 | Her oturumda **en eskiden yazılmış** dosya baştan sona okunur; mimariyle münasebeti ve garabetleri **sayılarak** yazılır | 2-H |
| 18 | Padişahın metni baştan sona okunur → küllî yenilikler çıkarılır → misal ayıklanır → mühürlenir → **ancak ondan sonra** dar suâle dönülür | 2-ẞ |
| 19 | Terkip üç adım: dosya kendi içinde → dosyalar birleşir → birleşikte bir daha. Terkip **kimliktir**, tabela değil | 3 |
| 20 | Terkipte ispat **formül cebriyle**: a'nın cebrinden b'nin cebrine kapalı form türetilir. İndirgenemiyorsa terkip edilmez | 3-B |
| 21 | Halkça isim: yapılan işi en az kelimeyle en çok yönden kapsayan, projedeki rolü doğrudan tarif eden | 4 |
| 22 | Şerh tek dosyadadır: `SERH.md` | 1-W |
| 23 | `FORMUL.md` mimarinin formülünü **kelimelerle** tutar; kod değişirse **aynı turda** değişir; yalnız fiilen koşan ameliye girer | 2-K |
| 24 | En derin kod bizzat koşturulur; donanım yoksa yol aranır (emülatör, bulut, çapraz derleme); aşılamazsa engel **sayıyla** yazılır | 1-F |
| 25 | Kaynak yoklanır (`git ls-remote` → klon → envanter); yol ve uzantı deponun envanterinden okunur | 1-K |

## 3-B. ÖLÇÜ VE MUHASEBE

| # | ZARURET | F |
| :-- | :-- | :-- |
| 26 | Her iddianın bir **sayısı** olur; ölçü kapatılabilir olur ve kapatılınca kırmızı yanar | 5 |
| 27 | Sessiz ikame yerine **assert**: boş bir şey dönmesin | 5 |
| 28 | Eşik bir **keyfiyetin** hangi nispete eriştiğini ölçen fonksiyonun çıktısıdır | 1-J |
| 29 | Donanım ölçüsü `nefs/donanim.py` ile fiilen yoklanır; yoklanamıyorsa `None` ve ona dayanan iddia kurulmaz | 5-B |
| 30 | Sözlük ebadı tiktoken `n_vocab`ından yoklanır; kodlamanın adı, `n_vocab`ı ve basamak sayısı raporda görünür | 1-N |
| 31 | Müfettiş **gereğini yapar**, sonra sayar: "kaç ihlâl düzeltildi, kaçı düzeltilemedi" | 1-Ü |
| 32 | Aşkın çağrı gövdede serbesttir fakat **sayılır** ve beyanda görünür | 2-Ş, 2-U, 2-J |
| 33 | Mantıksızlık **iki taşmadır**: parite taşması + belirteç taşması. İkisi de ayrı kefe, ikisinin **çarpımı** hudut | 2-L |
| 34 | Kapasite sayıyla: `q`, `N`, `q^N`in basamak sayısı; `2N` ayrı satırda mahallî serbestlik olarak | 2-R |
| 35 | Bütçe sayıyla: `d`, lif, `log₂ d`, müşterek durumun baytı, ölçülen bellek haddi yan yana | 2-S |
| 36 | Mertebe doğru yazılır: genlik üretimi `O(1)`, havuz `O(N)`. "Toptan O(1)" denmez | 2-T |
| 37 | Kapı maliyeti ölçülür: `N × q` dizey çarpımı turda kaç defa, kaç saniye | 2-Ú |
| 38 | Kapıda koşan idrak çağrısı sayılır; kapının elediği ile geleni arasındaki fark sayılır | 2-Ú |
| 39 | Düşen kapı **sıfırdır** ve sıfır olduğu sayılır | 2-Ö |
| 40 | Açılan vecih = kapanan vecih; fark sıfırdan büyükse sayılır ve raporda görünür | 2-Ú-D |
| 41 | Fock'ta `a†` sayısı = `a` sayısı; fark raporda görünür | 2-Þ |
| 42 | Kategori doygunluğu ölçülür: kaç balya, hangi mertebede, doygunluk nispeti | 2-Ƶ |
| 43 | Hafıza kapasitesi sayıyla: kaç kayıt, kaç seviye, kaç kök | 2-Ú-C |
| 44 | Her kanunun adı, tuttuğu mertebe ve **ölçülen nispeti** raporda görünür; tutmayan kanun nispetiyle kırmızı yanar | 2-Ú-E |
| 45 | Filtrenin çöktüğü üç hâl sayılır: (1) doğrulama da zor · (2) iğne samanlıkta, faz irtibatı yok · (3) örnek yetersiz, hipotez yığını | 2-Æ |
| 46 | Bargmann halkasının bedeli `O(m²)` iç çarpımdır ve ölçülür | 2-Ú |
| 47 | Senet bandının bedeli ölçülür ve raporda yazılır | 2-V |
| 48 | Tâlim raporunda ağırlığın hazineden mi rastgele `p₀`dan mı geldiği yazılır | 1-Y |
| 49 | `q^N` bir **uzay iddiasıdır**, bellek iddiası değildir; hiçbir yerde açılmaz | 2-T, 2-Ù |
| 50 | No-cloning'in bu projede bağlayıcı olmadığı **açıkça ilan edilir**: kod gerçek donanımda bu hâliyle koşmaz; kazanılan doğruluk ve hız, kaybedilen donanım taşınabilirliğidir | 1-T |

## 3-C. MOTOR VE VERİ

| # | ZARURET | F |
| :-- | :-- | :-- |
| 51 | **Tek motor**: `hazine + hafıza + söyle` her iki kapıda da koşar. Tek fark: çıkarımda eniyileme koşmaz (istisnası: Test Time Training, açıkça ilan edilir) | 1-H |
| 52 | **Tek belirteçleyici: tiktoken.** ARC ızgarası da, tefsir de, ispat da aynı kapıdan. Gömme bir matris değil, **tip vektörüdür** | 1-N |
| 53 | Yazmaç `sözlük^pencere` mertebesindeki bütün **dizileri** taşır; aranan şey dizinin tamamının genliğidir | 1-N-B |
| 54 | **Her şey yazmaçtan girer, yazmaçtan çıkar.** Tek kaynak yazmaçtır | 1-M |
| 55 | **İki veri cinsi aynı tâlimde beraber koşar**: (a) ARC -- "bu bulmacanın testine ne verirsin", ızgarada %100 uyum; (b) sözlü -- "sen olsan ne söylerdin", bölünmez | 1-R |
| 56 | **Tek hata fonksiyonu**: cevherler toplanır (`a+b` ∪ `c+d+a` ∪ `x+y+b` = `a+b+c+d+x+y`), hiçbiri silinmez, cins **ağırlık** olarak girer | 1-S |
| 57 | Kayıp **vektördür**; toplama ancak en sonda, eniyileyici sıralama isterken, **açıkça** yapılır | 1-V |
| 58 | Her meleke **ayrı kefedir**; mizan bir kefeler listesidir | 1-U |
| 59 | Bir veri için **üç hudut temizlenene kadar** durulur: tenakuz yok · kısırdöngü yok · mantıksızlık yok. Ancak ondan sonra imleç ilerler | 1-I, 2-I |
| 60 | Küme belleğe sığan kadardır (bütçe ∩ kenar ∩ ölçülen bellek); kalkan süre haddi **turu** büyütür, örneği değil | 2-I |
| 61 | Boru hattı: depoda verinin **tamamı** durur, kapta parça çekilir, işi bitirilir, bırakılır | 1-O |
| 62 | **Tek tâlim dosyası**: hazine varsa oradan yüklenir ve devam edilir; hangi kaynağın hangi **baytında** kalındığı saklanır; sıfırlama açık bir fiildir (`python -m main.egitim sıfırla`) | 1-Y |
| 63 | Model **geneller**: görmediği suâlde makul konuşur, hiç değilse "bilmiyorum" der | 2-Î |
| 64 | Öğrenilen şey: `Olabilirlik(sonraki DİZİ \| evvelki DİZİ)`. "Ne zaman ne konuşacağını bilmek" bunun neticesidir | 2-Ò |
| 65 | Merkez kefe `ℓ_Dizi = −ln \|Genlik(hedef dizi \| evvelki dizi)\|²` | 2-Ó |
| 66 | Ret **muhakemeden** gelir, ihtimalden değil; ret **kapının önünde**, girecek veri hakkındadır ve hafıza kaydının cinsini tayin eder | 2-Ó |
| 67 | Kapı bir **tasnif merciidir**: TENAKUZ → terfi (modalite lifi) · KISIRDÖNGÜ → tevakkuf damgası · MANTIKSIZLIK → ret | 2-Ú |
| 68 | Konuşma hafızaya bağlıdır: konuşulan hafızaya yazılır, hafızadaki konuşmaya girer | 2-Ó |
| 69 | Tâlimde **adım miktarı** süperpozisyondadır: 1'er, 2'şer, 3'er … `n` `n` ilerleyen hâller aynı anda. Çıkarımda gerek yoktur | 2-Ó-C |
| 70 | **Uzunluk** süperpozisyondadır: 1, 2, 3 … pencere kadar belirteç üretilmiş hâllerin hepsi aynı anda | 2-Õ |
| 71 | pencere = **1 048 576** belirteç; azamî huduttur, alt sınır yoktur | 2-O, 2-Õ |
| 72 | Hedef ikidir: **ARC-AGI-2 ve ARC-AGI-3**; ikisi de aynı motorla | 1-X |
| 73 | Mihenk **alelade bir İngilizce sualdir**; sual sabittir ve raporda aynen yazılır; tâlim her birkaç yüz saniyede bir o anki ağırlığıyla cevap verir ve kütüğe yazar | 2-F, 2-G |
| 74 | Kütük **anında akar**; manalı satıra derhal bakılır, manasıza sükût edilir | 2-N |
| 75 | ARC **yalnız** LLM motoruyla çözülür | 6 |
| 76 | Nihaî gaye: **herhangi bir şey hakkında konuşabilen bir model**. ARC bir mihenktir | 2-Ø |

## 3-D. YAZMAÇ VE TAŞIYICI

| # | ZARURET | F |
| :-- | :-- | :-- |
| 77 | Yazmaç bir tahsisat defteri değil **tek bir hâldir**: `Y_n` tip · kategori · uzay mertebelerinde aynı anda süperpozisyonda | 1-Ş |
| 78 | Hibrit yazmaç -- **ikisi beraber**: donanım kanadı ayrık mahallî yazmaç (zırh), idrak kanadı fonksiyonel küllî genlik | 2-Ş |
| 79 | Mahallî yazmaç `ℂ^{N×q}`, `N = 1 048 576`, `q = 64`, 1 GiB; şekil **sabittir**, adres asla kaymaz | 2-V, 2-Ğ |
| 80 | Aktif pencere gelen suâl kadardır; kalanı seyircidir, hesaplanmaz · taranmaz · çarpılmaz | 2-Ğ, 2-V |
| 81 | Yazmaç seviyesi ≥ bağlam penceresi; bağlamdan büyük de tutulmaz | 2-M, 2-O |
| 82 | Genlik bellekte **açık dizi olarak tutulmaz**, KAN-NQS ile üretilir: `Ψ = (1/√Z)·exp(Σ_k Φ_k(ω(w;θ)))`, `Φ_k = Σ_j C[k,j]T_j(u) + i·Σ_j S[k,j]U_j(u)` | 2-T |
| 83 | İşlem hattı: Θ havuzu → Gauss-Chebyshev-Lobatto kökleri → FCT `O(K log K)` → QSVT Gibbs süzgeci → deterministik ağaç intacı. Matris tersi yoktur (`κ = 1.0`); küsürat korunur | 2-T |
| 84 | Hakikî fonksiyon çağrılır: `cos(j·arccos u)`, `sin((j+1)·arccos u)/sin(arccos u)`, `exp` | 2-U |
| 85 | Faz **defteri** Galois'dadır: `Z_m` tamsayı üssü, Palmer çeyreği `i(a,b)=(−b,a)`, faz borcu ölçülür ve rapora basılır | 2-J |
| 86 | Parametre yazmacı ayrı bir qudit sistemidir; meleke bir **sayı okumaz**, kontrollü kapı vurur; bedeli müşterek durumdur ve ödenir | 2-R |
| 87 | Veri yazmacı da `N` qudit × taban `q`dur; iki yazmaç **aynı mertebede** karşılaşır | 2-V, 2-Ĝ |
| 88 | Kenetlenme üçüncü menfezdir: genlik KAN fonksiyonelinden, yön ve faz sürekli Lie-Cartan defterinden; 51 kapı köşegendir, genlikleri karıştırmaz, üsse skaler etkileşim ekler. Yığın boyu 1'dir | 2-V |
| 89 | Kenet eşlemesi her kodlamada yeniden: `Rezonans* = argmax_j Gerilim(j \| Münasebet, g_FS)` | 2-Z |
| 90 | Sektör bir bellek dilimi değil, Lie cebrinin zâtî süperseçim (DHR) yüküdür; meleke doğrudan kendi **kök jeneratörüne** yazar; on birinci sektör doğunca evvelkilerin adresinden tek bit oynamaz | 2-İ, 2-Ö |
| 91 | Sektör ağırlığı `Σ_j \|MahallîYazmaç[j, genlik]\|²`, kefesi `Ağırlık · exp(i·θ_cartan[k])` | 2-Ô |
| 92 | θ_cartan küresel ayar fazıdır: doğrudan KAN üssüne rezonans fazı olarak girer (kök sayısı kadar skaler çarpım); mahallî tesir yalnız temas edilen kapı indislerine | 2-Â |
| 93 | Kapı **bütün `N` qudide tek vektörel çevrimde** vurur: `hal @ Uᵀ` | 2-Ú |
| 94 | Melekenin evi mahallî yazmaç ve `θ_cartan`dır; meleke yalnız faza değil **genliğe de** hükmeder (Zeno izdüşümü, tenakuz sönümlemesi) | 2-Û |
| 95 | Hafıza da qudittir: kayıt `ℂ^q`, adres Cartan kökü, yaprak = modalite lifi = aynı kök | 2-Ú-C |
| 96 | Ölçüm klon üzerinde **tam** yapılır; asıl akış dokunulmadan devam eder | 1-T |
| 97 | Hâl okuması: `Hâl(kelâm) = \|⟨kelâm \| Genlik(hedef qudit; θ_cartan)⟩\|²`, maliyet `O(1)` | 2-Ê |
| 98 | Hedef qudit **nedensel cephedir** -- bağlamın bittiği yer | 2-Ï |
| 99 | Kelâm deterministtir: `Kelâm* = argmax_b [g_FS⁺·∇log Olabilirlik(b \| evvelkiler)]`; çeşitlilik vecih spektrumundan gelir | 2-Ĵ |
| 100 | Dolaşıklık nizamı: melekelerin bir kısmı **inşa edici**, büyük kısmı **koruyucu/iktisatlı**, en mühim kısmı **çözücü/tasfiye edici (uncompute)**. Gaye: `χ ≤ 64`, `S_vN` alan kanunu sınırında, ara hesap çöpleri `3.3×10⁻¹⁵` hassasiyetle sıfırlanmış | 2-Ø |
| 101 | Non-Clifford çıkmazının **üç çaresi de** icra edilir: (1) Matchgate/FLO · (2) Galois `F_2^8` S-box `x↦M·x²⁵⁴+b (mod P)`, `P(x)=x⁸+x⁴+x³+x+1` · (3) `Z_m` faz üssü + siklotomik koset | 7-A |
| 102 | Zabıt formülleri (`ℂ^d` dilinde yazılmış olsalar da) yeni nesil taşıyıcıya **tercüme edilir**; tercümenin sıhhati ölçülür ve fark sayıyla yazılır | 7-D |

## 3-E. HÂL, VECİH, ÂLEM

| # | ZARURET | F |
| :-- | :-- | :-- |
| 103 | Hâl, ana hâlin **bir suale verilmiş nihaî cevabıdır**; evvelden tarif edilmez, **açılır** | 1-Ç |
| 104 | Hâli doğuran funktör `F_hâl` ise `F_hâl⁻¹` de mevcut olmalıdır; tersi olmayan hâl açılmaz | 1-Ç |
| 105 | Meleke dört şeyi tayin eder -- hâlin **cinsi · vasfı · nasıl bina edileceği · neticesinde ne elde edileceği** -- yâni bir **sual** üretir | 1-Ç |
| 106 | Sual üretmek: durum **klonlanır**, klonun üstünde değişme-dönüşme kuralları **toptan değiştirilir**; vasıf değişimi hakikî tip/kategori/uzay teorisinden gelir | 1-Ç |
| 107 | Sual üretici çok kapıdan beslenir: diziden · hafızadan · saf durumdan · mantık devrelerinden · tenakuz ve kısırdöngü bulucularından | 1-Ç |
| 108 | Hâl **düşünme yollarını çeşitlendirmek** içindir: güvenilirlik · zâhir · art niyet · malzeme · kapasite -- hepsi beraber | 1-Ç |
| 109 | Hâlin içi riyaziye ile tayin olunur; ıslah edilecek yer motorun **hangi uzayları üretmeyi seçtiğidir** | 1-Ç |
| 110 | Mukayese daima bir **vecih** seçerek yapılır | 1-Ğ |
| 111 | Vecih tayini: `Vecih* = argmax [Gaye × Tenasüp × İnşikak]`; `Gaye = iz(ρ(Dizi)·Üreteç(Vecih))`, `Tenasüp = ort_k \|⟨belirteç_k\|Vecih⟩\|²`, `İnşikak = 1 − \|⟨A^(V)\|B^(V)⟩\|²`. Çarpım bir **sıralamadır**, eleme değil | 1-Ğ |
| 112 | Yetersizlik olmadan vecih değiştirmenin üç yolu: **J-aynası** (`J·M_v·J = M_v'`) · **tensörel terkip** (`\|A^(maaş)⟩⊗\|A^(takva)⟩`) · **üst mertebe tefekkür** (foliation) | 1-Ğ |
| 113 | Kâide dışarıdan ezberletilmez, **diziden istihraç edilir**: metrik (Fubini-Study/Fisher) · sıra (Lie yapı sabitleri `[X_a,X_b]=f_ab^c X_c`) · kompozisyon (sol Kan uzantısı, ko-end integrali) | 1-Ğ |
| 114 | Mertebe merdiveni `(r, n)` çiftidir; tavan `(∞, ∞)`. En umumî olan **KATEGORİ**dir; çöküş oradan başlar, cevap (nokta) en son varılan yerdir | 2-Þ, 2-Ā |
| 115 | Mertebe içindeki tür de izole edilir: UZAY → hiperbolik/Öklid/Lie torusu · KATEGORİ → poset/Heyting/DAG · TİP → Σ-bağımlı/HIT/Univalent | 1-Ğ |
| 116 | Âlem `matematik/sonsuz_mertebeler_teorisi.py`den fiilen türetilir; cevap o kategorinin **kimliğidir**, bir etiket değil | 2-Ā |
| 117 | Vecih bir âlem taşır: ⟨**Âlem** (sıhhat · tenakuz · teşbih · kinaye · gizli niyet · sualin parametreleri …), **Kaideler** (o âlemin kendine has metriği, sırası, kompozisyonu), **Taşıyıcı Mertebe** (ölçülerek seçilir, yetmezse bir üst açılır)⟩ | 2-Ú |
| 118 | Vecih sayısı elle konmaz, özdeğerden de gelmez: **kaç ayrı kaide imzası varsa o kadar âlem** doğar | 2-Ú |
| 119 | Vechin ömrü dört safhadır: **ATEŞLEME** (`𝒪15` Merak ve Sual) → **DOĞUM** → **AMELİYE** (saftirikçe beklemez) → **KAPANIŞ** | 2-Ú-D |
| 120 | Tip tayfı süperpozisyonda taşınır; hangi tipler varmış ve **kaideleri neymiş** raporda görünür | 2-Ú-B |
| 121 | Kaide bir **kanunlar manzumesidir**: TİP → küllî aksiyomlar · KATEGORİ → morfizm/terkip/birleşme/monoidal kanunları · UZAY → metrik tensör, diferansiyel formlar, eğrilik · NOKTA → hepsini sağlayan somut hâller | 2-Ú-E |
| 122 | Sorgu **kanoniktir** -- dış türev `d` gibi manifoldun kendi cebrî tabiatından doğar | 2-Ú-E |
| 123 | Üç usul de, **sırasıyla**: **1 YONEDA** (dış münasebet, `Hom(−, Y_n)`, hudut kanunları) → **2 KOHOMOLOJİ** (iç doku, `δ∘δ=0`, korunum kanunları) → **3 LIE/CASIMIR** (dinamik, Erlangen, dönüşüm kanunları). Dış hudut çizilmeden iç omurga aranmaz | 2-Ú-E |
| 124 | `n = 0` kesin eler (riyazî imkânsızlık tartılmaz); `0 < n < 1` mizana kefe olur | 2-Ē |

## 3-F. MUKAYESE MELEKESİ

| # | ZARURET | F |
| :-- | :-- | :-- |
| 125 | Melekeler tek cins değildir: **CİNS 1 EVİREN** (durumu bir hâlden başkasına çevirir) · **CİNS 2 NETİCE ÇIKARAN** (hüküm çıkarır, hafızaya yazılır yahut durumla takıştırılır). Her melekenin cinsi **zabıtla, ayrı ayrı** tarif edilir | 2-Ú |
| 126 | Bargmann `n`-nokta invaryantı: `Δ_n = ⟨ψ₁\|ψ₂⟩…⟨ψ_n\|ψ₁⟩ = r_n·exp(i·Φ_n)`. `r_n` halka koheransı, `Φ_n` Pancharatnam katı açısı | 2-Ú |
| 127 | Üç mukayese mertebesi de koşar: **2'li** `½(1−\|⟨1\|2⟩\|²)` · **3'lü** `arg(⟨1\|2⟩⟨2\|3⟩⟨3\|1⟩)` · **n'li** `iz(Π₁…Π_n)`. `Φ_n = Σ_{k=2}^{n−1} Φ₃(ψ₁,ψ_k,ψ_{k+1}) (mod 2π)` | 2-Ú |
| 128 | Bütün halka boyları `2..m` beraber tartılır | 2-Ú |
| 129 | Sorites tuzağı `O(1)`de yakalanır: yerel `⟨ψ_k\|ψ_{k+1}⟩ ≈ 1` iken kapalı halkada `Φ_n → π` Möbius taklası | 2-Ú |
| 130 | Mukayesenin çıktısı dört bileşenlidir: ⟨Topolojik doku, Bargmann spektrumu, Tertip/kafes, Amelî vecih⟩. Hiyerarşi mecburî değildir: poset/ağaç · çember · dipol · kafes/çizge -- hangisi olduğunu `Δ_n` söyler | 2-Ú |
| 131 | Netice tekil bir **morfizm durumu** `\|σ_Y⟩` olarak paketlenir; `⟨σ_Y\|σ_Z⟩ = iz(ρ_Y·ρ_Z) → 1` ise hüküm **analojidir** | 2-Ú |
| 132 | Hüküm ayniyet ↔ ihtilaftan okunur: `Örtüşme(v) = \|⟨hâl_i^(v)\|hâl_eş^(v)⟩\|²`, `İhtilaf = max − min`, `İttifak = 1 − İhtilaf`. **TENAKUZ**: İhtilaf > İttifak. **KISIRDÖNGÜ**: İttifak > İhtilaf ve min Örtüşme ≥ İttifak | 2-Ú |
| 133 | Hükmü mukayese melekesi verir ve **hafızaya kaydeder** | 2-Ú |
| 134 | Kapı kodlamadan **sonra** koşar; üç hudut hâl üstünde ölçülür: tenakuz `Φ₃→π`, kısırdöngü `Φ₃→0`, mantıksızlık iki taşma | 2-Ú |
| 135 | Kapı imleçten gelen **her parçada** koşar; parça ölçülen bellekten türer; tenakuz çıkan çiftin iki kutbu saklanır | 2-Ú |
| 136 | Her âlem **kendi halkasını kapatır**: `Cins(hâl) = ‖Vecih(hâl)‖'i azamî yapan vechin âlemi` | 2-Ú |
| 137 | Hafıza **yeniden tertiplenir**, silinmez: **1** alâka tespiti `A(k) = iz(ρ^(k)·Π_R)` → **2** düğüm çözme → **3** taban değişimi (yeni modalite lif koordinatı) → **4** yeniden mühür `ρ_yeni = U·ρ_eski·U† + Δρ` | 2-Ú |
| 138 | Re-gluing iki kapıdan tetiklenir, **tek** ameliye koşar: **sorites yırtığı** (`istisna_yeri`, sapma > 3× ortanca → metakognitif tashih) · **kapı reddi** (`veri_kapisi`, aynı bağlam iki hedefle → veri tenakuzu) | 2-Ú |
| 139 | Modalite lifi: `Δ₃` vechi tayin eder (`Φ₃`ü azamî yapan vecih), Cartan kökü taşır -- yeni **ortogonal** kök açılır, indis kayması sıfır | 2-Ú |
| 140 | Tertip **küme kapanınca bir defa** koşar; arada yırtıklar deftere yazılır, kapanışta boşaltılır | 2-Ú |
| 141 | Cerrahî **yerinde** yapılır: `qyazmac.py` kalır, adı kalır, çağıranları kırılmaz; içi dönüştürülür | 2-Ú |

## 3-G. ÇOK İNDİSLİ SÜPERPOZİSYON VE ÇÖZÜM UZAYI

| # | ZARURET | F |
| :-- | :-- | :-- |
| 142 | Süperpozisyon **birçok yerdedir**: hafıza · parametre · veri · uzunluk · adım miktarı · çözüm uzayı … tavan yoktur; yenisi doğdukça sayılır | 2-Ý |
| 143 | **Evren ve uzay tektir**, indis çoktur: `\|Ψ⟩ = \|m⟩⊗\|l⟩⊗\|k⟩⊗…`. `m`, `l`, `k` birer **misaldir**, esas değil | 2-Þ |
| 144 | `Ĥ = Ĥ₁ + Ĥ₂ + … + V̂_kuplaj`. Bütün sır `V̂_kuplaj`dadır: çelişen konfigürasyonun enerjisi göğe fırlar, genlik **yıkıcı girişimle** söner -- aranmaz, elenmez, maskelenmez | 2-Þ |
| 145 | Tek kısıt bütün eksenleri büker; kısıt (bütçe) elle yazılmaz, **ölçülür** | 2-Þ, 5-B |
| 146 | Hiyerarşik çöküş: **1** yavaş mod sürüklenir (hangisi olduğu kuplaj kütlesi × entropiden **ölçülür**) → **2** tali şartlandırılır, şartlı alt uzaya inilir (`N³ → N`) → **3** tek ölçüm, tek uyumlu konfigürasyon | 2-Þ |
| 147 | Fock uzayı: vakumdan başlanır, `a†` mesele doğurur, `a` söndürür; `\|Ψ⟩ ∈ ⊕_n H^(n)`. Mesele sayısı bir de olsa bin de olsa **aynı cebir** koşar | 2-Þ |
| 148 | Üç ortak para birimi Lagrange çarpanı gibi davranır: **entropi/belirsizlik** · **kapasite/bütçe** · **çelişki katsayısı**. Mahiyeti bilmek şart değildir | 2-Þ |
| 149 | Akışkan faktör grafı: her kâide bir düğüm, her tesir bir kuplaj kenarı; düğümler durum dalgası fırlatır; metin bitince graf kaç düğümlü olursa olsun **dengeye çöker** | 2-Þ |
| 150 | Hafıza üç kat'î hüküm: **1** tekrar az tutulur · **2** model ne zaman ne söylediğini unutmaz · **3** kayıt mevzudan koparmaz | 2-Þ |
| 151 | **Unutma yok, tecrit var**: hafıza artar → kategori doygunlaşır → mertebe yükselir → eski kayıtlar üst kategorinin bir nesnesinde **balyalanır** ve oradan **açılabilir** (funktörün tersi şart) | 2-Ƶ |
| 152 | Tekrarın az yer tutması balyalamanın **tabiî neticesidir**: aynı şeyin `n` nüshası `n` nesne değil, tek üst nesnenin `n` katlı hâlidir | 2-Ƶ |
| 153 | Çözüm uzayı **sabit değildir**: kaidesinden doğar (Yoneda → Kohomoloji → Lie). Ne önceden sabitlenir ne listelenip seçtirilir | 2-Ý, 2-Þ |
| 154 | Çözüm uzayı **ortada sual varken** koşar; koşup koşmayacağı **girdiden** anlaşılır | 2-Ý |
| 155 | Ana süperpozisyon kapı memurudur, dört suâli cevaplar: **1** burada bir mesele var mı → **2** yeni uzayın kaideleri nedir → **3** neticenin geri getirilmesi nasıl olacak (funktörün tersi) → **4** nihayette üretilecek metin nedir | 2-Ý |
| 156 | Doğrulayıcı filtre iki kapıdan gelir: **verinin kendisi** ve **bütün mantık/mukayese melekeleri** | 2-Ý |
| 157 | **MANTIK FİLTRESİ** üç şeye düşmemektir: çelişki (tenakuz) · safsata (mugalata, sorites) · kısır döngü (teselsül). Tesiri faz çevirmek olabilir | 2-Ý |
| 158 | **MUKAYESE FİLTRESİ**nin mahiyeti farklıdır, dalgaya tesiri de farklı olacaktır; neticesinin kategorisi her zaman aynı değildir. **Bu mesele açıktır ve müştereken karara bağlanacaktır** | 2-Ý, 2-D |
| 159 | Kalp `matematik/sonsuz_mertebeler_teorisi.py`dir; her uzuvla **aracısız** bağı vardır | 2-Ý |
| 160 | Kule `Nokta^Uzay^Kategori^Tip^200000^1000000` bir **uzay iddiasıdır**; `200 000` tiktokenden yoklanır, `1 000 000` penceredir, iç mertebenin tavanı yoktur. Müzakere **tehir edildi**: evvelâ model konuşsun | 2-Ù |

## 3-H. JETON, REZONANS VE KELÂM

| # | ZARURET | F |
| :-- | :-- | :-- |
| 161 | Jeton bir kelime değil, arama uzayında koşan **üniter dönüşüm operatörüdür**: `Ψ ← P_n ∘ … ∘ P_1 (Ψ₀)`. Bağ **cebirsel izdüşümdür** | 2-Æ |
| 162 | Logit doğrudan **faz kaydırıcıdır**: `θ_j = π·p_j`. `p_j→1` yıkıcı girişim, `p_j≈0.5` bulanık girişim. Şüphe ile kesinlik girişimin derinliğini ayarlar | 2-Æ |
| 163 | Rezonans **çift yönlüdür**: İLERİ kâide söylenir, uymayan dalların fazı çevrilir · GERİ kalan `‖Ψ‖²` ölçülür, sıfırlanırsa LLM'e **negatif logit cezası** iner ("bu jetonu geri al") | 2-Æ |
| 164 | Kısıt metinden türer: metnin **entropi gradyanı** sabitleri ve değişkenleri ayırır; **entropisi en yüksek bölge aranan şeydir**. Kısıtlar bir kısıt grafına dökülür | 2-Æ |
| 165 | Arama uzayı lügatin **serbest çarpım uzayıdır** (piksel değil); vakum: bütün diziler eşit genlikte | 2-Æ |
| 166 | **Kural uzayına kapanılır**, çıktı uzayı taranmaz; kural rezonansa girince çıktı tek saat darbesidir | 2-Æ |
| 167 | Kelâm iki şarta bağlıdır: ya **burhan tamamlanmıştır**, ya **iç muhakeme tıkanmıştır ve sual tevcih edilir**. Üçüncüsü yoktur | 2-Ø |
| 168 | Müşahede esasları: müdahalesiz takip (ölçerken veri tahrif edilmez) · kanalın temizliği · tekrarlanabilirlik ve istikrar · **müşahede gaye ile olur** | 2-Ø |
| 169 | Padişahın tayin ettiği sıra: **1** eğitim motoru tam doğru koşsun → **2** 41 melekenin **tamamı**, aynı maksat etrafında yeniden tarif edilsin → **3** kuyunun dibine varmadan durulmasın | 2-Ø |
| 170 | İspat testle değil, **gerçek padişahı koşturmakla** olur | 2-Ø |

## 3-I. MANTIĞA SADAKAT · ÖZERKLİK · TEHİR EDİLENLER

| # | ZARURET | F |
| :-- | :-- | :-- |
| 171 | **MANTIĞA SADAKAT BİR DOĞRULAYICI DEVREDİR.** Bulmacanın kâidesi nasıl bir süzgeç olarak kullanılıyorsa, mantık da öyledir: **mantıken mümkün olmayanın fazını eler** | 2-Đ |
| 172 | **İSTİSNASIZ BÜTÜN SÜPERPOZİSYONLARDA KOŞAR.** Hafıza · parametre · veri · uzunluk · adım miktarı · çözüm uzayı -- hangisi varsa (F 2-Ý'nin listesi ve ona eklenecek her yenisi) sadakat devresi oraya da vurulur. Eksik bırakılan süperpozisyon **sayılır ve kırmızı yanar** | 2-Đ, 2-Ý |
| 173 | **YALNIZ MANTIKSIZ OLAN İMHA EDİLİR.** Mantığı henüz ayan beyan görünmeyen ihtimal **devre dışı bırakılmaz**; eleme imkânsızlığa mahsustur (F 2-Ē'nin `n = 0` hükmünün sadakat kanadı) | 2-Đ, 2-Ē |
| 174 | Eleme nispeti **iki sayıyla** yazılır: kaç dal mantıksız diye imha edildi, kaç dal *"mantığı görünmüyor"* diye **kasten bırakıldı** | 2-Đ, 5 |
| 175 | **ÖZERK GAYE YALNIZ TÂLİMDEDİR**: girdi yokken iç tenakuz enerjisi ve merak gediğinden `G_t` doğar, tâlim kendi suâlini üretir. Çıkarımda koşmaz | 2-Ħ |
| 176 | **MANTIK YÜRÜTME (USUL SEFERİ) TEHİR EDİLDİ.** `nefs/usul.py`'nin on usul devresi, `gedik_bul`u, üç gayesi (istihrac · cerh · tahkik) ve hadd-i evsat tasfiyesi **yerinde durur ve kesilmez**; makineye nasıl vidalanacağı padişahın kararını bekler | 2-Đ, 2-D, 2-C |
| 177 | **KALP TEHİR EDİLDİ.** İleride ahlâken uyulması gereken kâidelerin ve taklit vicdanının yeri olacaktır; şimdi inşa edilmez, vazife uydurulmaz | 2-Ł |
| 178 | **MÜŞAHEDENİN ARC VASFI İMHA EDİLİR.** Kalacak kanadın taşıyıcısı açık sualdir ve teklif sunulmuştur: münasebet vasıfları (ihtilaf · teşabüh · hareket · sükûn · teferruk · ittisal · adet · tenasüb · bu'd) **Bargmann ve münasebet haritasında hâlihazırda ölçülenlerle terkip edilsin** (ferman 3-B: cebrî ispat), ışık vasıfları (levn · huşunet · meles · zıl · şeffafiyet · kesafet) kesilsin. Ölçü mevcuttur: 3 kanal AUC 0.8981, 22 kanal 0.8686 | 2-Œ, 1-N-C, 3 |
| 179 | **İÇTİHAD İÇTİHADI NAKZETMEZ.** Yeni hüküm eskisini sessizce silmez; silecekse **nakz açıkça yazılır** ve nakzın kendisi de kaydedilir | 2-Y |
| 180 | **HER MESAJDA HEM KENDİMİ HEM PADİŞAHI TENKİT EDERİM**; padişahın her sözü doğru değildir, yoklanır | 2-Ø |

---

# § 4. BÜTÜN SİSTEMİN DURUM MAKİNESİ ŞEMASI

## 4-A. KOŞU KAPILARI

| Fiil | Emir | Kapı |
| :-- | :-- | :-- |
| Tâlim | `python -m main.egitim tâlim kısa` | eniyileme **koşar** |
| Teftiş | `python -m main.egitim teftiş` | divan |
| Sıfırlama | `python -m main.egitim sıfırla` | hazine silinir |
| Çıkarım | `python -m main.cikarim` | eniyileme **koşmaz** (TTT hariç) |

Koşturulabilen **tek** şey budur (F 1-L).

## 4-B. KÜLLÎ ÇEVRİM -- KÜME HALKASI

```
        ┌─────────────────────────────────────────────────────────────┐
        │                                                             │
        ▼                                                             │
   ┌─────────┐   ölçülen bellek     ┌──────────┐                      │
   │ K0      │   haddi kadar örnek  │ K1       │                      │
   │ İMLEÇ   │ ───────────────────▶ │ KÜME     │                      │
   │ (hazine)│   F 1-Y, 2-I         │ AÇIK     │                      │
   └─────────┘                      └────┬─────┘                      │
        ▲                                │                            │
        │                                ▼                            │
        │                          ┌──────────┐                       │
        │                          │ K2       │  kodla → idrak → hâl  │
        │                          │ KAPI     │  Δ₂/Δ₃ ile üç hudut   │
        │                          │ TASNİFİ  │  F 2-Ú                │
        │                          └────┬─────┘                       │
        │                               │                             │
        │        tenakuz → TERFİ (modalite lifi)                      │
        │        kısırdöngü → TEVAKKUF damgası                        │
        │        mantıksızlık → RET (tek eleme)                       │
        │                               │                             │
        │                               ▼                             │
        │                         ┌──────────┐                        │
        │                         │ K3       │  TUR (§ 4-C)           │
        │                         │ TÂLİM    │◀──────┐                │
        │                         │ TURU     │       │ üç hudut       │
        │                         └────┬─────┘       │ kirli          │
        │                              │             │ F 1-I          │
        │                              ▼             │                │
        │                         ┌──────────┐       │                │
        │                         │ K4       │───────┘                │
        │                         │ HUDUT    │                        │
        │                         │ YOKLAMASI│                        │
        │                         └────┬─────┘                        │
        │                              │ TEMİZ                        │
        │                              ▼                              │
        │                         ┌──────────┐                        │
        │                         │ K5       │  biriken bütün         │
        │                         │ TERTİP   │  yırtıklar tek         │
        │                         │ (bir kez)│  hamlede  F 2-Ú        │
        │                         └────┬─────┘                        │
        │                              │                              │
        │                              ▼                              │
        │                         ┌──────────┐                        │
        └─────────────────────────│ K6       │──────────────────────┘
          imleç ilerler, hazine   │ MÜHÜR    │
          güncellenir  F 1-Y      │ (hazine) │
                                  └──────────┘
```

| Geçiş | Şart | F |
| :-- | :-- | :-- |
| K0 → K1 | Küme ölçülen belleğe sığar (bütçe ∩ kenar ∩ bellek) | 2-I, 5-B |
| K1 → K2 | Parça imleçten geldi | 2-Ú, 1-O |
| K2 → K3 | Tasnif tamam; yalnız mantıksızlık elendi | 2-Ú |
| K3 → K4 | Tur bitti (§ 4-C intaç) | 2-A |
| K4 → K3 | Üç hudut kirli -- **küme bırakılmaz** | 1-I, 2-I |
| K4 → K5 | Tenakuz · kısırdöngü · mantıksızlık üçü de temiz | 1-I |
| K5 → K6 | Tertip bir defa koştu | 2-Ú |
| K6 → K0 | İmleç ilerledi; bayt konumu hazineye yazıldı | 1-Y |

## 4-C. TUR SİLSİLESİ -- HAZIRLIK → EVRİM → İNTAÇ → ÖLÇÜM

```
  T1 HAZIRLIK          T2 EVRİM                T3 İNTAÇ         T4 ÖLÇÜM
  ───────────          ────────                ────────         ────────
  kodla                melekeler koşar         KAN              genlik
  tohum eker           θ_cartan birikir        İLK VE SON       okunur
  (genlik+faz)   ──▶   kapılar N qudide  ──▶   DEFA bir     ──▶ kelâm
  KAN ÇAĞRILMAZ        tek çevrimde vurur      kez çağrılır     çıkar
  F 2-A                F 2-Ú, 2-Û              F 2-A, 2-T       F 2-Ê, 2-Ĵ
```

| Kaide | Hüküm | F |
| :-- | :-- | :-- |
| Tek çağrı | Turda **bir** KAN çağrısı; ne iki, ne sözlük kadar | 2-A, 2-Ê |
| Gecikme yok | Melekelerin ve θ_cartan'ın bütün fazı **aynı turun** cevabına girer | 2-A |
| Boşluğa koşmaz | Melekeler `kodla`nın ektiği **dolu** yazmaca temas eder | 2-A |
| Okuma | Hedef quditin izdüşümü; basamak toplamı yok | 2-Ê |
| Karar | Determinist Fubini-Study; zar yok | 2-Ĵ |

## 4-D. ÇÖZÜM UZAYI MAKİNESİ -- YEDİ DURUM

```
   ╔═══════════════════════════════════════════════════════════════════╗
   ║  SADAKAT DEVRESİ -- her durumda, her süperpozisyonda, İSTİSNASIZ  ║
   ║  mantıksız dal imha edilir · mantığı görünmeyen dal BIRAKILIR     ║
   ╚═══════════════════════════════════════════════════════════════════╝   F 2-Đ
          ┊            ┊            ┊            ┊            ┊
          ▼            ▼            ▼            ▼            ▼
                     ┌──────────────┐
                     │ S0  VAKUM    │  Fock |0⟩; hiçbir mod açık değil
                     └──┬────────┬──┘  F 2-Þ
         metin geldi    │        │   girdi YOK  ve  kapı = TÂLİM
                        │        │   iç tenakuz + merak gediği taranır
                        ▼        │   → G_t doğar          F 2-Ħ
                 ┌──────────────┐│
                 │ S1  SINIR    ││  entropi gradyanı ölçülür
                 │              ││  kısıt grafı kurulur   F 2-Æ
                 └──────┬───────┘│
                        │        │
                        ▼        ▼
                     ┌──────────────┐
                     │ S2  MESELE   │  ANA SÜPERPOZİSYON dört suâli
                     │              │  cevaplar; a† ile mod doğar
                     └──┬────────┬──┘  F 2-Ý, 2-Þ
          mesele yok    │        │  mesele var  ve  F⁻¹ mevcut
                        │        │
   ┌────────────────────┘        ▼
   │                      ┌──────────────┐
   │                      │ S3  UZAY     │◀────────────┐
   │                      │              │  kaidesinden│
   │                      └──────┬───────┘  doğar      │
   │                             │          F 2-Ý      │
   │                             ▼                     │
   │                      ┌──────────────┐             │
   │                      │ S4 SÜZÜLMÜŞ  │  sadakat + mukayese
   │                      │              │  F 2-Đ, 2-Ý │
   │                      └──────┬───────┘             │
   │                             ▼                     │
   │                      ┌──────────────┐             │
   │                      │ S5  HÜKÜM    │─────────────┘
   │                      │              │  yeni vecih ateşlendi
   │                      └──────┬───────┘  F 2-Ú-D
   │                             │ hüküm kapandı; a ile mod söner
   ▼                             ▼
   ┌───────────────────────────────────────────┐
   │ S6  İNTAÇ   funktörün tersiyle ana hâle   │
   │             dönülür; netice kelâma girer  │
   └───────────────────────────────────────────┘   F 1-Ç, 2-Ý

   [ USUL SEFERİ -- TEHİR EDİLDİ (F 2-Đ, 2-D) ]
   nefs/usul.py: 10 devre · gedik_bul · istihrac/cerh/tahkik ·
   hadd-i evsat U† tasfiyesi · Lan_K. Kodda durur, KESİLMEZ;
   makineye hangi durumdan açılacağı padişahın kararını bekler.
```

### Geçiş tablosu (bunun dışında geçiş yoktur)

| Durum | Meşru hedefler | Geçişin şartı | F |
| :-- | :-- | :-- | :-- |
| S0 VAKUM | S1 | Metin geldi | 2-Þ |
| S0 VAKUM | **S2** | Girdi **yok** ve kapı **tâlim**: iç tenakuz + merak gediğinden `G_t` doğdu. Çıkarımda bu geçiş **yoktur** | 2-Ħ |
| S1 SINIR | S2 | Entropi gradyanı ölçüldü, kısıt grafı kuruldu | 2-Æ |
| S2 MESELE | S3, S6 | S3 için: mesele var **ve** `F⁻¹` mevcut. Aksi hâlde S6 | 2-Ý, 1-Ç |
| S3 UZAY | S4 | Uzay kaidesinden doğdu (Yoneda → Kohomoloji → Lie) | 2-Ý, 2-Ú-E |
| S4 SÜZÜLMÜŞ | S5 | **Sadakat devresi** ve mukayese filtresi koştu | 2-Đ, 2-Ý |
| S5 HÜKÜM | S3, S6 | S3 için: yeni vecih ateşlendi. Aksi hâlde S6 | 2-Ú-D |
| S6 İNTAÇ | -- | Nihaî hâl | -- |

### Değişmezler

| # | İNVARYANT | İhlâlin adı | F |
| :-- | :-- | :-- | :-- |
| I1 | Açılan vecih = kapanan vecih; `a†` sayısı = `a` sayısı | Saftirikçe bekleyen vecih | 2-Ú-D, 2-Þ |
| I2 | `F⁻¹` yoksa S2 → S3 geçişi **olmaz** | Geri getirilemeyen uzay; biriken idrak kaybolur | 1-Ç |
| I3 | Norm üniterdir; tek istisna mukayese filtresinin Gibbs merceğidir ve o da yeniden normalize eder | Genliğin sessizce sızması | 2-Ý |
| I4 | Bir jeton iki defa maskelenemez | Kısırdöngü (teselsül) | 2-Æ, 1-I |
| I5 | Hiçbir durumda zar atılmaz | Stokastiklik | 2-Ĵ, 2-Ø |
| I6 | S3'te açılan her uzay S5'te bir **hüküm** doğurur; hükümsüz uzay kapanmaz | Boşa açılmış uzay | 2-Ú-D |
| I7 | Her durumda üç hudut ölçülebilir olmalıdır; ölçü kapatılınca kırmızı yanmalıdır | İş görmeyen ölçü | 5, 1-I |
| I8 | **Her durumdan çıkarken, o durumda mevcut BÜTÜN süperpozisyonlar sadakat devresinden geçer.** Geçmeyen süperpozisyon sayılır | Muaf tutulmuş süperpozisyon | 2-Đ |
| I9 | Sadakat **yalnız mantıksız** dalı imha eder. *"Mantığı görünmüyor"* diye kapatılan dal sayısı **sıfır** olmalıdır | Kendini kilitleme | 2-Đ |
| I10 | S0 → S2 öz-geçişi **yalnız tâlim kapısında** meşrudur | Çıkarımda özerklik | 2-Ħ |

## 4-E. JETON HALKASI (S6 içinde koşar)

```
   ┌────────────────────────────────────────────────────────────┐
   │                                                            │
   ▼                                                            │
 ┌──────────────┐   θ_j = π·p_j   ┌──────────────┐              │
 │ J1  LOGİT    │ ───────────────▶│ J2  FAZ      │              │
 │ p_j okunur   │                 │ KAYDIRICI    │              │
 └──────────────┘   F 2-Æ         └──────┬───────┘              │
                                         │ P_jeton uygulanır    │
                                         ▼                      │
                                  ┌──────────────┐              │
                                  │ J3  NORM     │              │
                                  │ ‖Ψ‖² ölçülür │              │
                                  └──┬────────┬──┘              │
                        ‖Ψ‖² = 0     │        │  ‖Ψ‖² > 0       │
                                     │        │                 │
                                     ▼        ▼                 │
                            ┌──────────────┐ ┌──────────────┐   │
                            │ J4  CEZA     │ │ J5  KELÂM    │   │
                            │ negatif logit│ │ jeton geçti  │   │
                            │ maskesi      │ └──────┬───────┘   │
                            └──────┬───────┘        │           │
                                   │                │ durma     │
                                   └────────────────┴───────────┘
                                     jeton geri alınır / devam
```

| Kaide | Hüküm | F |
| :-- | :-- | :-- |
| Çift yön | Tek yönlü rezonans kurulamaz | 2-Æ |
| Ara katman | Yoktur: ne MLP, ne izdüşüm matrisi, ne öğrenilen ağırlık | 2-Æ |
| Bütün dallar kapanırsa | `assert`: sessiz ikame yoktur | 5, 2-Æ |
| Durma | Bir sayı değil bir **hükümdür**; üst hudut yoktur, alt hudut da yoktur | 2-Ó-B, 2-O |
| Kelâmın şartı | Burhan tamam **yahut** iç muhakeme tıkandı → sual tevcih edilir | 2-Ø |

## 4-F. MİZAN VE ADIM MAKİNESİ

```
  M1 KEFELER          M2 MECZ                    M3 KABUL
  ──────────          ───────                    ────────
  ℒ = (ℓ₁ … ℓ_m)      EĞİM   yön verir           tam mizan
  her meleke ayrı     ÇUKUR  durak mı söyler     vektörü
  kefe, toplam yok ─▶ VADİ   engeli aşırtır  ─▶  konuşur;
  F 1-U, 1-V          NAKİL  sıçratır            keyfiyet
                      (DUVAR yoktur)             bir kefedir
                      F 2-P, 2-Ú                 F 2-Ü, 1-S
```

| Kaide | Hüküm | F |
| :-- | :-- | :-- |
| λ nispeti | Birleşik Hamiltonyen'den: `Ĥ.nispetler()`. Sabit `PAYLAR` tablosu yoktur | 2-Þ |
| Yön | `Eğim_a = 2·Im⟨ψ\|Üreteç_a·Hata\|ψ⟩`, bütün `a` için tek hamlede; kayıp çağrısı **sıfır** | 2-P |
| Yarıçap | `Keyfiyet(üç hudut) / √iz(g_FS)`. Tarama daveti değil, yalnız adımın boyu | 2-P, 1-J |
| Mecz ≠ meclis | Beş vazifenin çıktısının **cinsi** başkadır, toplanamazlar | 2-P, 1-U |
| Kefe → operatör | Her kefe için yazmaç üstünde bir operatör kurulur; kurulamayan kefe yönü kurmaz fakat **hükmü verir** | 2-P, 1-S |

## 4-G. İKİ KAPININ TEK MOTORU

```
   ┌──────────────────────┐        ┌──────────────────────┐
   │  main/egitim.py      │        │  main/cikarim.py     │
   └──────────┬───────────┘        └──────────┬───────────┘
              │                               │
              └───────────────┬───────────────┘
                              ▼
                    ┌───────────────────┐
                    │  hazine + hafıza  │   F 1-H
                    └─────────┬─────────┘
                              ▼
                    ┌───────────────────┐
                    │  § 4-D  ÇÖZÜM     │
                    │  UZAYI MAKİNESİ   │
                    └─────────┬─────────┘
                              ▼
                    ┌───────────────────┐
                    │  § 4-C  TUR       │
                    └─────────┬─────────┘
                              ▼
                    ┌───────────────────┐
                    │  § 4-E  KELÂM     │   her iki kapıda da
                    └─────────┬─────────┘   F 1-H, 2-F
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
   ┌──────────────────────┐        ┌──────────────────────┐
   │ § 4-F MİZAN + ADIM   │        │  (eniyileme YOK)     │
   │ § 4-B KÜME HALKASI   │        │  TTT hariç           │
   └──────────────────────┘        └──────────────────────┘
```

**İki kapı arasındaki fark tek satırdır: çıkarımda eniyileme koşmaz.** Başka hiçbir fark meşru değildir (F 1-H) -- özerk gaye öz-geçişi hariç, ki o da bir eniyileme kanadıdır (F 2-Ħ).

## 4-H. SADAKAT DEVRESİ -- İSTİSNASIZ HER SÜPERPOZİSYONDA

```
   her süperpozisyon Ψ  (hafıza · parametre · veri · uzunluk ·
                         adım miktarı · çözüm uzayı · … tavan yok)
             │
             ▼
   ┌──────────────────────────────────────────────────────────┐
   │ 1. KOD UZAYINI TAYİN ET                                  │
   │    Ŝ_mantık : mantıken MÜMKÜN olan dalların gerdiği uzay  │
   └───────────────────────────┬──────────────────────────────┘
                               ▼
   ┌──────────────────────────────────────────────────────────┐
   │ 2. ÜÇ KÜMEYE AYIR -- ikiye değil ÜÇE                     │
   │    MÜMKÜN      Ŝ|ψ⟩ = +|ψ⟩            → dokunulmaz       │
   │    MEÇHUL      hüküm verilemiyor      → DOKUNULMAZ       │
   │    MANTIKSIZ   riyazî olarak imkânsız → FAZI ELENİR      │
   └───────────────────────────┬──────────────────────────────┘
                               ▼
   ┌──────────────────────────────────────────────────────────┐
   │ 3. YALNIZ MANTIKSIZI İMHA ET, YENİDEN NORMALİZE ET       │
   └───────────────────────────┬──────────────────────────────┘
                               ▼
   ┌──────────────────────────────────────────────────────────┐
   │ 4. İKİ SAYIYI BAS (F 5)                                  │
   │    imha edilen dal  ·  meçhul diye BIRAKILAN dal         │
   └──────────────────────────────────────────────────────────┘
```

| Kaide | Hüküm | F |
| :-- | :-- | :-- |
| Kapsam | Bir süperpozisyon bile muaf değildir; yenisi doğduğunda devre ona da vurulur | 2-Đ, 2-Ý |
| Üç küme | **MÜMKÜN · MEÇHUL · MANTIKSIZ.** İki kümeye indirmek meçhulü mantıksız saymaktır ve kendimizi kilitler | 2-Đ |
| Eleme haddi | Riyazî imkânsızlık; `n = 0` hükmünün sadakat kanadı | 2-Đ, 2-Ē |
| Muhasebe | İmha edilen ve **bırakılan** dal ayrı ayrı sayılır; bırakılan sıfırsa devre fazla eliyor demektir | 2-Đ, 5 |
| Müfettişlik | Devre haber vermez, **gereğini yapar**: mantıksız dalı fiilen imha eder | 1-Ü |
| Uzuv | `nefs/sadakat.py` -- yerinde dönüştürülür, yeni dosya açılmaz | 2-Ú, 2-D |
