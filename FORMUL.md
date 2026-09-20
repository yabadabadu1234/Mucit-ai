# MUCİT-AI -- MİMARİNİN TAM FORMÜLÜ, DURUM MAKİNESİ OLARAK

Semboller yerine isimler kelimedir; ameliyeler formüldür (ferman 2-K).
Yazılan şey **koşan koddur**, niyet değil.

Her durum üç sütunla yazılır ve bir durumun **ÇIKTI**sı, kendisinden
sonraki durumun **GİRDİ**sidir. Zincirde adı geçmeyen hiçbir şey
kullanılamaz; kullanılan hiçbir şey adsız kalamaz.

| Bab | Muhteva |
| :-- | :-- |
| § 0 | KIYAS -- transformer ve biz |
| § 1 | KÜLLÎ ZİNCİR -- durumdan duruma girdi/çıktı |
| § 2 | D0 … D11 -- her durumun tam formülü |
| § 3 | ÇÖZÜM UZAYI ALT MAKİNESİ (S0 … S6) |
| § 4 | SADAKAT DEVRESİ -- her durumda koşan doğrulayıcı |
| § 5 | KONUŞMA ALT MAKİNESİ (J1 … J5) |
| § 6 | ÖLÇÜLEN HUDUTLAR VE AÇIK ÇELİŞKİLER |

---

## § 0. KIYAS -- TRANSFORMER VE BİZ

```
TRANSFORMER:
  Baş(Gizli) = Gizli + yumuşakenbüyük(Gizli·Sorgu · (Gizli·Anahtar)ᵀ / √boyut)
               · Gizli·Değer
  Kat(Girdi) = Baş(Girdi) + doğrultucu(Baş(Girdi)·Ağırlık₁) · Ağırlık₂
  Çıktı      = Kat₃(Kat₂(Kat₁(Girdi)))

BİZ:
  Meleke(Yazmaç) = Kapı(Yazmaç, Açı(ParametreYazmacı))     ← katman değil, ameliye
  Yazmaç         = Sadakat(Meleke₄₅(… Meleke₁(Yazmaç₀) …))
  Çıktı          = DeterministOkuma(Hâl)                   ← zar yok (ferman 2-Ĵ)
```

**DETERMİNİZM BORN'U İNKÂR DEĞİLDİR.** Born çökmesi *örnekleme*dir; biz
örneklemeyi kaldırdık, **girişimi** değil. Genlik toplanır, faz çevrilir,
yıkıcı girişim dalı söndürür -- klasik ihtimal bunu yapamaz, çünkü klasik
ihtimalde negatif/karmaşık ağırlık yoktur. Kaybedilen şey donanım
taşınabilirliğidir ve ferman 1-T'de **açıkça ilan edilmiştir**: bu kod
gerçek kuantum donanımında bu hâliyle koşmaz. Kazanılan: tekrarlanabilirlik
(I5) ve `O(1)` okuma.

**GALOİS İZİ MATRİS İZİ DEĞİLDİR.** `İz(α·x¹²) = İz(α^(1/4)·x³)` iddiası
`GF(2⁸)` üzerindeki **mutlak Frobenius izidir**:
`İz_GF(y) = y + y² + y⁴ + … + y^128`. Bu izin zâtî hassası `İz_GF(y²) =
İz_GF(y)`dir; iki defa tatbik edilince `İz_GF(y⁴) = İz_GF(y)` olur.
`y = α^(1/4)·x³` konulursa `y⁴ = α·x¹²` çıkar, eşitlik **tam** sağlanır.
Lineer cebirdeki `Tr(A¹²) ≠ Tr(A³)` burada bağlayıcı değildir: ortada
matris yok, sonlu cismin kendi izi vardır (ferman 7-B).

---

## § 1. KÜLLÎ ZİNCİR -- DURUMDAN DURUMA GİRDİ/ÇIKTI

```
 ┌─────┐  kodlama · Cömertlik     ┌─────┐  Sözlük · Ölçü · LifYapısı┌─────┐
 │ D0  │ ───────────────────────▶ │ D1  │ ───────────────────────▶ │ D2  │
 │GEÇİT│  İlletÇizgesi · Hız      │ÖLÇÜ │  Gelen (ARC + Külliyat)  │HEND.│
 └─────┘                          └─────┘                          └──┬──┘
                          Gelen (değişmeden geçer) · MertebeTayfı     │
                          LifDemeti · Büzülme · PariteLifi · Ω        │
                                                                      ▼
 ┌─────┐  Veri (kabul edilen)     ┌─────┐  Nefs · Hafıza · Fock     ┌─────┐
 │ D5  │ ◀─────────────────────── │ D4  │ ◀─────────────────────── │ D3  │
 │UZAY │                          │KAPI │                          │KURUL│
 └──┬──┘                          └─────┘                          └─────┘
    │ Netice (pencere · hâl · mesele · hafıza kapasitesi)
    ▼
 ┌─────┐  Ψ' (her süperpozisyon   ┌─────┐  Kefeler (vektör)         ┌─────┐
 │ D5b │ ───── süzülmüş) ───────▶ │ D6  │ ───────────────────────▶ │ D7  │
 │SADK.│                          │MİZAN│                          │  Ĥ  │
 └─────┘                          └─────┘                          └──┬──┘
                                                          λ nispetleri │
                                                                      ▼
 ┌─────┐  p* (öğrenilmiş)         ┌─────┐  Küme temiz mi?           ┌─────┐
 │ D9  │ ◀─────────────────────── │ D8  │ ◀─────────────────────── │  ⟲  │
 │KAPAN│                          │DÖNGÜ│   hayır ise tur tekrar    └─────┘
 └──┬──┘                          └─────┘
    │ Hafıza (tertiplenmiş) · Balya · İmleç
    ▼
 ┌─────┐  Kelâm · Sükût           ┌─────┐
 │ D10 │ ───────────────────────▶ │ D11 │  Hazine (tek dosya)
 │KELÂM│                          │MÜHÜR│
 └─────┘                          └─────┘
```

**ÇIKARIM KAPISI** aynı zincirin **D1 → D2 → D3 → D5 → D5b → D10**
dilimidir. Tek fark: D6-D7-D8-D9-D11 koşmaz (ferman 1-H). Özerk gaye
öz-geçişi (§ 3, S0 → S2) yalnız tâlimde açıktır (ferman 2-Ħ).

**D1 VE D2 ÇIKARIMDA DA KOŞAR** -- ferman 1-H'nin gereği budur: iki kapı
arasındaki **tek** fark eniyilemedir. Çıkarımda D1'in `Gelen`i külliyat
değil **gelen suâlin kendisidir**; D2 o suâlin dizisinden mertebe tayfını
ve `PariteLifi`ni yeniden örer. `PariteLifi`nin hazineden sabit gelmesi
**iptal edilmiştir**: sabit lif, suâlin hendesesini görmezden gelmek olurdu.
Hazineden gelen şey ağırlıktır (`p₀`), lif değil.

---

## § 2. DURUMLARIN TAM FORMÜLÜ

### D0 GEÇİT -- `main/egitim.py:gecit`

| | |
| :-- | :-- |
| **GİRDİ** | `EgitimAyari` (profil: dar · orta · azamî) -- profil **yalnız** `Cömertlik`i taşır: dar 0.15 · orta 0.5 · azamî 1.0 |
| **AMELİYE** | `AlanÇizgesi → Çevrimler` · `ZamanÇizgesi → Çevrimler` · `KelâmAyrışması` · (yalnız `HızGeçiti ≠ 0` ise) `HızTeftişi` |
| **ÇIKTI** | `İlletÇizgesi = (düğüm, kenar, çevrim)` · `KelâmAyrıştı ∈ {doğru, yanlış}` · `Cömertlik` · (şart ise) `BelirteçSn` |

```
ZamanÇevrimi ≠ ∅          ⇒ DURUR: bir adım kendi geleceğine bağlı
KelâmAyrıştı = yanlış     ⇒ DURUR: kelâm veriden doğrudan besleniyor,
                                    hüküm atlanabiliyor (ezberin kapısı)
BelirteçSn < Had          ⇒ DURUR: hız garantisi olmadan tâlim başlamaz
```

**D0'DA NE VERİ VARDIR NE MODEL -- VE OLMASI DA GEREKMEZ.**

`KelâmAyrışması` bir **tensör ölçüsü değil, statik illet çizgesi
ölçüsüdür** (`nefs/illet.py`): kodun kendisi düğüm, çağrı bağı kenardır.
Sorduğu suâl şudur: *kelâm düğümüne veri düğümünden, hüküm düğümüne
uğramadan bir yol var mı?* Bu yol varsa ezberin kapısı açıktır. Veriye de
modele de ihtiyacı yoktur, çünkü ölçtüğü şey **akışın şeklidir**, akan
değerler değil.

`HızTeftişi` ise **iç içe (nested) bir minyatür koşudur**: `tanilama/
hiz_teftisi.olc` D1→D3→D6 zincirinin en küçük ölçeğini kendi içinde kurar
ve **bir kayıp çağrısını** fiilen koşturur. Zincirde gizlenmiş özyineleme
yoktur; burada **adıyla ilan edilmiştir**:

```
HızTeftişi = Minyatür(D1 → D3 → D6)    ← kendi nefsini kendi kurar
BelirteçSn = minyatürün ölçülen belirteç/saniyesi
Had        = tanilama/hiz_teftisi.had()      ← ÖLÇÜLÜR, elle yazılmaz
```

Kısırdöngü yoktur çünkü minyatür **tâlimin nefsini beklemez**, kendi
nefsini kurar ve yıkar. `DAR` profilinde `HızGeçiti = 0`dır: teftiş hiç
koşmaz, `BelirteçSn` çıktı listesinde **yer almaz** ve ona dayanan hiçbir
hüküm kurulmaz (ferman 5-B: yoklanamayan `None`dır).

### D1 ÖLÇÜ VE VERİ -- `EgitimAyari.__post_init__` · `qegitim.ornekler` · `main/kulliyat.py`

| | |
| :-- | :-- |
| **GİRDİ** | D0'ın çıktısı (`Cömertlik` dâhil) · `kodlama` · hazinedeki `İmleç` · hazinedeki `ÖlçülenHız` |
| **AMELİYE** | Sözlük yoklanır, ölçü tablosu türetilir, iki cins veri çekilir |
| **ÇIKTI** | `Sözlük` · `VeriLifi` · `Karo` · `Pencere` · `LifYapısı` · `BasamakSayısı` · `Gelen` · `İmleç′` |

```
Sözlük        = tiktoken(kodlama).n_vocab          ← ELLE YAZILMAZ (ferman 1-N)
BasamakSayısı = en küçük k öyle ki VeriLifi^k ≥ Sözlük
Cömertlik     ← D0'DAN GELİR (profilin taşıdığı tek sayı)
ÖlçülenHız    ← HAZİNEDEN GELİR (main/egitim.hazineden_hiz); hazine yoksa
                0.0'dır ve ona dayanan hiçbir iddia kurulmaz (ferman 5-B)
Ölçü          = olcek( Sözlük, Cömertlik, Tohum, ÖlçülenHız )
                ← veri_lifi · karo · pencere · örnek_sayısı · tur … hepsi buradan
LifYapısı     = (VeriLifi, Karo, Karo)     ← DEMET BURADA KURULUR, D2 kurmaz

Gelen = Örnekler(ARC görevleri, azamî = ÖrnekSayısı ÷ 2)
      ∪ KülliyatVerisi(imleç = hazinedeki imleç, azamî = kalan)
        ← İKİ CİNS BERABER (ferman 1-R); külliyat imleçten devam eder (1-Y)
```

**BOYUT PATLAMASI YOKTUR ÇÜNKÜ `q^N` HİÇ AÇILMAZ.** `BasamakSayısı`
belirteci qudit **seviyelerine** kodlar; `Sözlük ≈ 2·10⁵` ve `VeriLifi =
16` iken `k = 5` basamaktır. Taşınan bellek `q^N` değil, **mahallî zırhtır**:
`ℂ^{N×q}`, `N = 1 048 576`, `q = 64` → `1 GiB`, sabit. `q^N` bir **uzay
iddiasıdır**, bellek iddiası değildir (ferman 2-T, 3-B #49); genlik
bellekte açık dizi olarak durmaz, KAN-NQS fonksiyonelinden **üretilir**
(ferman 2-T). Açılmayan şey patlamaz.

### D2 HENDESE -- `nefs/hendese.py:hendese_teshisi`

| | |
| :-- | :-- |
| **GİRDİ** | `Gelen`in bağlamları · D1'den gelen `LifYapısı` · `VeriLifi` (alfabe) |
| **AMELİYE** | Opetopik kompleks örülür → üç evrensel test → Hodge ayrışımı → Ω sınıflayıcı → spektral tabakalaşma → dikey asansör |
| **ÇIKTI** | `Gelen` (değişmeden geçer) · `MertebeTayfı` (7 katman) · `Hodge` · `Ω_cebiri` · `LifDemeti` · `Büzülme` · `PariteLifi` |

**NAKZ (ferman 2-Ā-B, padişahın hükmü):** eski `argmax(dört puan)` ve
`PariteLifi = Mertebe.kat` iptal edildi. Onun yerine koyduğum **yedi isimli
KATMANLAR cetveli ve elle yazılmış KISITLAMA tablosu da iptal edildi** --
o, kesilen listeyi geri getirmekti. Cins **listelenmez**; veri kendi cinsini
kendi örer.

**TÜRETİM MOTORU TEKTİR VE KALPTEDİR.** En üst cins -- Yönlü Opetopik
`(∞,∞)`-Properad Toposu -- `matematik/sonsuz_mertebeler_teorisi.py`de
yaşar. O dosya tam bir kübik tip teorisi çekirdeğidir: `Aralik`/`Kofibrasyon`
yüz kafesi (= Ω alt-nesne sınıflayıcısının cebiri), `komp`/`dolgu` (= Kan
doldurucusu), `Yapistir` (= Glue, demetleşme), `rn_sarti` (= `(r,n)`
merdiveni), `denetle`/`sentezle` (= tip denetçisi). **Hendese ölçer, kalp
türetir.** Başka hiçbir dosyada türetim yoktur (ferman 114-A).

```
UZUV (nefs/hendese.py) -- YALNIZ ÖLÇER, HÜKÜM VERMEZ
─────────────────────────────────────────────────────
1. SERBEST OPETOPİK KOMPLEKS  (kural dayatılmaz, dizi kendi hücresini örer)
   0-hücre = ayrı basamaklar          1-hücre = ardışık geçiş (a → b)
   2-hücre = bağlam AĞACI ({a,b} → c) 3-hücre = kuralın kurala dönüşümü
   HücreMertebesi = dolu en yüksek hücre boyutu   ← TAVAN BURADAN, elle değil

2. ALTI SERBESTLİK NİSPETİ -- hepsi [0,1], hepsi ÖLÇÜLÜR
   morfizm  = 1-hücre ÷ (0-hücre)²          yüksek = 2-hücre ÷ (1-h · 0-h)
   arite    = 1 − 1/(ortGirdi · ortÇıktı)   yön₁   = Hodge asimetri payı
   yön₂     = aynı ayrışım, 2-hücre üstünde koherans = dolu boynuz ÷ boynuz

3. TAMSAYI SAYIMLARI -- bunlar nispet DEĞİL, SAYIDIR ve int tutulur
   0/1/2/3-hücre · boynuz · dolu_boynuz · tıkanma · yönlü_kenar ·
   simetrik_kenar · şelale_uzay · şelale_kategori · şelale_operad ·
   dörtlü · üçgen_ihlâli · dag_mertebesi · kafes
   `nefs/hendese.py`de _SAYI (int) ile _NISPET (float) AYRI defterlerdir;
   bir sayımı float yazmaca koymak fermanın ihlâlidir.

4. ŞELALE HÂLİNDE BÜZÜLME -- sayaç değil, FİİLEN DOLDURUR
   her boş boynuz (a→b→c, a→c yok) sırayla şu üç hendeseye sorulur:
     UZAY      c→a var mı?              → simetriyle kapanır
     KATEGORİ  a→m→c başka m var mı?    → yönlü okla kapanır
     OPERAD    {a,b}→c ağacı var mı?    → çoklu birleşimle kapanır
     TIKANMA   hiçbiri değilse          → HAKİKÎ OBSTRÜKSİYON, kapanmaz
   kapanan her boynuz `a→c` kenarını AÇAR; koherans yeniden ölçülür.
   Ω_yırtık = tıkanma ÷ boynuz  ← modelin DÜŞÜNMESİ gereken yer

KALP (matematik/sonsuz_mertebeler_teorisi.py) -- TÜRETİR
─────────────────────────────────────────────────────────
5. KAFES ÜRETİLİR, LİSTELENMEZ  (turetim_kafesi)
   her (r, n) için `rn_sarti(A, r, n)` KURULUR ve `denetle_t` ile
   TİP DENETİMİNDEN GEÇİRİLİR. Tutan (r,n) kafese girer, düşen girmez.
   r ∈ [0, HücreMertebesi],  n ∈ [−1, KoheransMertebesi]  ← tavan veriden

6. SERBESTLİK PROFİLİ BİTTİR -- float değil  (_serbestlik_profili)
   kurulan tipin kendi imzasından okunur (Π · Σ · Yol derinliği sayılır):
     morfizm = 1 ⟺ imza.pi  > 0      yön₁ = 1 ⟺ n ≥ 1
     yüksek  = 1 ⟺ imza.yol > 0      yön₂ = 1 ⟺ n ≥ 2
     arite   = 1 ⟺ imza.sigma > 0    koherans = 1 ⟺ n ≥ 0
   Kısıtlama derecesi = sıfır olan serbestlik sayısı. Zirve hepsi 1 olandır;
   aşağı inmek bir serbestliği KAPATMAKTIR (dejenerasyon).

7. TAYF -- Boole kafesi üstünde çarpım ölçüsü, argmax YOK
   ağırlık(r,n) = Π_a ( x_a  eğer profil_a = 1 ; 1 − x_a  eğer 0 )
   ρ = ağırlık ÷ Σ ağırlık        Σρ = 1, hiçbir düğüm elenmez
   Bu float bir mesafe değil, bit profili üstünde tanımlı ÖLÇÜDÜR.

8. Ω ALT-NESNE SINIFLAYICISI -- kafesin kendi cebri karar verir
   boş boynuz yoksa  kofibrasyon = ⊤, ifade = 1
   boş boynuz varsa  kofibrasyon = (κ=1), ifade = κ
   ÜÇÜNCÜ ŞIK testi: `ifade ∨ ¬ifade` BİR mi?   ← Aralik kafesinde koşar
     yönlü kenar > simetrik kenar  → YÖNLÜ KAFES (lineer/kuantum mantığı)
     üçüncü şık tutuyor            → BOOLE      (klasik mantık)
     tutmuyor                      → HEYTİNG    (sezgisel mantık)
   Hüküm AYRIKTIR; üç isme sürekli ağırlık dağıtılmaz. Yanında tamsayı
   sayımlar (dolu · boş · yönlü_kenar · simetrik_kenar) raporda görünür.

ÇIKTI -- TEKİL LİF DEĞİL, DEMET
─────────────────────────────────
9. İZDÜŞÜM DEMETİ  Π = ⟨Π_uzay, Π_kategori, Π_operad⟩   (n × n dizey)
   Π_uzay     = (P + Pᵀ)/2    simetrik   → üniter kapı
   Π_kategori = (P − Pᵀ)/2    ters simetrik → yönlü ortogonal kapı
   Π_operad   = 2-hücre ağaç tensörü → üniter OLMAYAN izdüşüm

10. DERECELİ FOCK/QUDİT DEVRİ -- her katman kendi hendesesinde nefes alır
    D3'te kafesin her düğümü için bir Fock modu doğar (`a†`):
      mod "mertebe·(r,n)-kategori"  doluluk ∝ ρ, çelişki = Ω_yırtık
    Küme kapanışında hepsi söndürülür (`a`); I1 korunur.
    Mahallî zırhın aktif penceresi Hodge üçlüsüne göre ÜÇE BÖLÜNÜR:
      ‖𝒮‖ payı kadar qudit  → Π_uzay'ın ürettiği ÜNİTER kapıyı yer
      ‖𝒜‖ payı kadar qudit  → Π_kategori'nin YÖNLÜ ORTOGONAL kapısını
      Ω payı kadar qudit    → Π_operad'ın ÜNİTER OLMAYAN izdüşümünü
    `nefs/mahalli_yazmac.py:modlari_vur`, her `kodla`da fiilen koşar.
    Aşkın çağrılar (eigh · exp) SAYILIR ve beyanda görünür (ferman 2-Ş).

11. KANONİK BÜZÜLME (ε: F(G(x)) → x) -- argmax değil
    tayf, kısıtlama derecesine göre LifYapısı'nın katlarına dağıtılır
    LifDemeti[j] = Σ ρ,  Büzülme = Σ j·LifDemeti[j],  PariteLifi = ⌊Büzülme⌉
    Tayf ÇÖKMEZ: LifDemeti, Hodge, Ω ve şelale D3'e beraber geçer.
```

**ÖLÇÜLEN (kısa profil, 7 ARC + 7 külliyat örneği):** kafes **4** düğüm ·
tıkanma **50** boynuz · büzülme **1.001** → PariteLifi **1** · dereceli Fock
modu **4**. Bütün bu sayılar `safha` damgalarıyla kütüğe **anında** akar.

**TAMSAYIYLA ÖLÇÜLEN TASHİHLER (padişahın tenkidi, hepsi haklıydı):**

```
a) KarşılıklıHaber'de log(0) yoktur: toplam YALNIZ Ortak > 0 üstünde koşar;
   payda np.finfo(float).tiny ile korunur -- elle yazılmış 1e-300 kesildi.
b) Nilpotentlik: GeçişDizeyi SATIR-STOKASTİK DEĞİL, ALT-STOKASTİKTİR
   (çıkış derecesi sıfır olan satır sıfır kalır), o yüzden Perron-Frobenius'un
   λ=1 hükmü bağlayıcı değildir. Yine de float kuvvetle "= 0" ölçmek ve
   `1e-12` eşiği fermana aykırıydı: artık BOOLE ERİŞİLEBİLİRLİĞİ ile TAM
   ölçülür (`kenar^k` mantıksal çarpım), `k` kayması giderildi, adı
   `dag_mertebesi` oldu ve mertebe teşhisinde ARTIK KULLANILMAZ.
c) Gromov dörtlüsü ZARLA SEÇİLMEZ: `default_rng(...).choice` kesildi,
   yerine determinist adım taraması geldi (I5: hiçbir durumda zar atılmaz).
d) Ölçek uyuşmazlığı: bit · matris normu · kosinüs artık yarıştırılmıyor;
   profil BİT, ölçü NİSPET, sayım TAMSAYI -- üç defter ayrı.
```

### D3 KURULUŞ -- `QNefs` · `Hafiza` · `FockUzayi` · `Hamiltonyen`

| | |
| :-- | :-- |
| **GİRDİ** | `Ölçü` · `PariteLifi` · `Tohum` · hazinedeki `p` |
| **AMELİYE** | Yazmaçlar açılır, hazine varsa ağırlık **oradan yüklenir** |
| **ÇIKTI** | `Nefs` · `Hafıza` · `Fock` · `Ĥ` · `p₀` |

```
p₀ = hazinedeki p        eğer hazine VARSA          ← DEVAM ASILDIR (1-Y)
   | rastgele            eğer hazine YOKSA          ← raporda hangisi YAZILIR

Yazmaçlar (hepsi qudit):
  VERİ YAZMACI       girdi dizisini tip · kategori · uzay mertebelerinde
                     süperpozisyonda tutar                      (ferman 1-Ş)
  PARAMETRE YAZMACI  ayrı qudit sistemi; ÇIPLAK PARAMETRE YOK   (ferman 2-R)
                     Kapasite = Taban ^ QuditSayısı             ← uzay iddiası
                     MahallîSerbestlik = 2 × QuditSayısı        ← bellek iddiası
  MAHALLÎ YAZMAÇ     ZIRH = 1 048 576 qudit × (genlik, faz), SABİT (2-Ğ)
                     aktif pencere içinde nefes alır; kalanı SEYİRCİ
  HAFIZA             kayıt = normalize kavram vektörü + (ω, hüküm, μ, yaprak)
```

### D4 VERİ KAPISI -- `nefs/veri_kapisi.py:veri_kapisi`

| | |
| :-- | :-- |
| **GİRDİ** | `Gelen` · `Nefs` · `Hafıza` |
| **AMELİYE** | Her örnek **kodlanır**, hâli doğar, üç hudut **hâl üstünde** ölçülür |
| **ÇIKTI** | `Veri` (kabul edilen) · `KapıHükmü` (her örneğin tasnifi) |

```
Hâl(Örnek)  = İdrak(Kodla(Bağlam + Hedef))   ← kapı KODLAMADAN SONRA koşar
Eş(i)       = aynı Bağlamı paylaşan evvelki örnek, yoksa i−1
              ← bu bir HÜKÜM değil, çiftin İKİNCİ KUTBUDUR

ŞAHİT YOKTUR (ferman 2-Ú). Hüküm çiftin BÜTÜN VECİHLERDEKİ okumasından:

  Örtüşme(v) = |⟨Hâl_i^(v) | Hâl_Eş^(v)⟩|²        her vecih v için
  İhtilaf    = azamî Örtüşme − asgarî Örtüşme
  İttifak    = 1 − İhtilaf                        ← ikisi toplamı BİR (1-J)

  Hüküm = MANTIKSIZLIK  eğer basamak ∉ [0, VeriLifi)        → RET (tek eleme)
        | TENAKUZ       eğer İhtilaf > İttifak               → TERFİ
        | KISIRDÖNGÜ    eğer İttifak > İhtilaf ve asgarî ≥ İttifak → TEVAKKUF
        | TASDİK        değilse

KAPI BİR ELEK DEĞİL, TASNİF MERCİİDİR: eleme YALNIZ mantıksızlıktadır.
Tenakuzlu örnek çıkarılmaz, modalite lifiyle TERFİ eder (ferman 2-Ú).
```

### D5 ÇÖZÜM UZAYI -- `nefs/mukayese.py` (alt makine § 3)

| | |
| :-- | :-- |
| **GİRDİ** | `Veri` · `Nefs` · `Hafıza` · `Fock` |
| **AMELİYE** | `AnaSüperpozisyon → UzayAç → Süzgeçler → UzayKapat` |
| **ÇIKTI** | `Netice = (Pencere, Hâl, Mesele, MeseleNispeti, EnZayıfKanun, ArananBasamak, HafızaKapasitesi)` |

```
ayar.Pencere        ← Netice.Pencere
Hafıza.Kapasite     ← Netice.HafızaKapasitesi
                      ← ikisi de MAKİNENİN HÜKMÜDÜR, elle yazılmaz
```

### D5b SADAKAT DEVRESİ -- `nefs/sadakat.py:sadakat_devresi` (§ 4)

| | |
| :-- | :-- |
| **GİRDİ** | `Nefs` · `Hafıza` · `Fock` · `Netice` -- yâni **her süperpozisyon** |
| **AMELİYE** | Üç kümeye ayır, **yalnız mantıksızı** imha et, yeniden normalize et |
| **ÇIKTI** | Süzülmüş süperpozisyonlar · `(İmha, MeçhulBırakılan, Muaf, Bağlanmamış)` |

Her turda, her durumdan çıkarken koşar (invaryant I8).

### D6 MİZAN -- `nefs/kulli_mizan.py:kulli_mizan`

| | |
| :-- | :-- |
| **GİRDİ** | `Nefs` · `Veri` · `p` · `Sözlük` · `MizanAyarı` · `Hafıza` · `KapıHükmü` |
| **AMELİYE** | İleri geçiş koşar, kefeler **ayrı ayrı** ölçülür |
| **ÇIKTI** | `Kefeler` -- bir **vektör**, bir skaler değil (ferman 1-V) |

```
İLERİ GEÇİŞ (bir turda TEK KAN çağrısı -- ferman 2-A):

  T1 HAZIRLIK   Kodla: mahallî yazmaca tohum ek (genlik + faz). KAN ÇAĞRILMAZ.
                  Genlik[j] = Dolu(j) / ‖Dolu‖
                  Açı[j]    = π · Basamak(j)
  T2 EVRİM      Meleke_k(Yazmaç) = Kapı_k(Yazmaç, Açı_k(ParametreYazmacı))
                  k = 1 … 45 (44 meleke, 𝒪₁₃ iki kere)
                  Kapı BÜTÜN N qudide tek vektörel çevrimde vurur (2-Ú)
                  θ_cartan birikir                                (2-Â)
  T3 İNTAÇ      KAN fonksiyoneli İLK VE SON DEFA çağrılır:
                  Genlik = üstel( −Enerji + i·(Σ_j w_j + θ_cartan·KökAğırlığı) )
                           / √Bölen
                  Reel  = Σ_{k,j} C[k,j] · kosinüs( j · arkkosinüs(u) )
                  Sanal = Σ_{k,j} S[k,j] · sinüs((j+1)·arkkosinüs u)/sinüs(arkkosinüs u)
                  ← HAKİKÎ FONKSİYON; tekrarlama ikamesi yasak (ferman 2-U)
  T4 ÖLÇÜM      Hâl(kelâm) = |⟨kelâm | Genlik(hedef qudit; θ_cartan)⟩|²
                  hedef qudit = NEDENSEL CEPHE (bağlamın bittiği yer, 2-Ï)
                  basamak ekseni boyunca TOPLAMA YOK (ferman 2-Ê)

KEFELER (hiçbiri ötekinin yerine geçmez -- ferman 1-S, 1-U):

  Hata_uzay     = 1 − Uhlmann(Hâl, Hedef)                  ← ÇIPA
  Hata_nokta    = −ln İz(HedefİzdüşümÜ · YoğunlukMatrisi(Hâl))
  Hata_kategori = ‖ Morfizm(g∘f) − Morfizm(g)·Morfizm(f) ‖²
  Hata_tip      = ⟨Artık, HodgeLaplasyeni·Artık⟩ / ‖Artık‖²
  Hata_çevrim   = |Holonomi(Çevrim) − Fıtrat|
  Hata_tenakuz  = −ln((İz(Birim+GerçekKısım(ÇevrimÜniteri))+ε)/(2·Boyut+ε))
                  × DışlamaEntropisi(Çevrim)
  Hata_gedik    = Borç(Usul, KaranlıkÇevrimler)
  Hata_monogami = enbüyük(0, Dolaşıklık(bütün) − Σ Dolaşıklık(ikili))
  Hata_engel    = Engellenme(Yazmaç, SürekliÖlçüm)
  Hata_lif      = 1 − SıraBağıntısı( Mesafe(Bağlam_i,Bağlam_j),
                                     −ln |⟨Hâl_i|Hâl_j⟩| )
  Hata_taşma    = PariteTaşması ⊕ BelirteçTaşması           ← İKİ taşma (2-L)
  Hata_kaideHalkası:
      Bargmann = ∏_j ⟨Hipotez_j | Hipotez_{j+1 mod n}⟩
      = (1−|Bargmann|) + [açı ≈ π: tenakuz] + [açı ≈ 0: kısırdöngü]
                       + [enküçük |⟨·|·⟩| ≈ 0: kopukluk]
      ← ELLE YAZILMIŞ KAİDE YOK: kaide, modelin kendi hâlidir (ferman 6)
  Hata_meleke[k] = ortalama_{ad ∈ İlan_k} Eksik(Okuma_k[ad], Sözleşme_k[ad])
                   ← 44 meleke 44 AYRI KEFE; tek skalere indirilmez (1-U)
```

### D7 BİRLEŞİK HAMİLTONYEN -- `nefs/kulli_mizan.py:Hamiltonyen`

| | |
| :-- | :-- |
| **GİRDİ** | `Kefeler` |
| **AMELİYE** | Kefeler öbeklere düşer, kuplaj kurulur, yavaş mod **ölçülür** |
| **ÇIKTI** | `λ nispetleri` · `TabanDurumu` |

```
Ĥ      = Ĥ_öbek₁ + Ĥ_öbek₂ + … + V̂_kuplaj              (ferman 2-Þ)
Alan   = h + β · V[:, yavaşMod];   Alan[yavaşMod] = h[yavaşMod]
λ      = Nispetler(Alan)                    ← SABİT PAYLAR TABLOSU YOK
Skaler = Σ_j λ[j] × Kefe[j]                 ← TOPLAMA YALNIZ BURADA (1-V)

YavaşMod = kuplaj kütlesi × entropi'yi AZAMÎ yapan öbek ← ÖLÇÜLÜR (ferman 2-Þ)
```

### D8 DÖNGÜ -- `nefs/munasebet.py:munasebet_kos` + `ogrenme/mecz.py`

| | |
| :-- | :-- |
| **GİRDİ** | `Veri` · `p₀` · `λ` · `MünasebetHaritası` (hazineden) |
| **AMELİYE** | Küme seç → tur koş → adım at → hudut yokla → temizse imleci ilerlet |
| **ÇIKTI** | `p*` · `MünasebetHaritası′` · `(temizlenen, kirliKalan)` |

```
Zayıflık(Örnek) = ortalama( 1 / (1 + MünasebetHaritası[Bağlam(Örnek)]) )
Küme            = en zayıf öbek; boyu ÖLÇÜLEN BELLEKTEN (ferman 2-I)

tekrarla:
    SadakatDevresi(bütün süperpozisyonlar)          ← her turda (I8)
    λ         ← Ĥ.Nispetler( Kefeler(p, Küme) )     ← her turda YENİDEN
    p         ← Adım(p, Küme)
    dur eğer HudutTemiz(Küme)

HudutTemiz   = (Tenakuz = 0) ve (Kısırdöngü = 0) ve (Mantıksızlık = 0)
Mantıksızlık = PariteTaşması + BelirteçTaşması              ← İKİ taşma
NispetMantık = (1 − PariteTaşması) × (1 − BelirteçTaşması)  ← HUDUT ÇARPANI

değil HudutTemiz ⇒ Küme kuyruğun BAŞINA döner
    HudutTemiz ⇒ İmleç ← İmleç + bayt(Küme)                 ← ancak o zaman
```

#### D8-a ADIM -- MECZ: DÖRT MEMUR, TUR BAŞINA TEK KAYIP ÇAĞRISI

```
SENET    = [ (tür, yer, dizey) ]                 her kapı vuruşu sırayla
SenetSadakati = ‖SenediOynat(Yazmaç₀) − Yazmaç_son‖ / ‖Yazmaç_son‖

EĞİM -- üç mekanizma, tek hakikat:
  Üreteç   Eğim[p] = Σ 2·ölçek·Re⟨ Hata⊙Yazmaç_son | dKapı·Yazmaç_son ⟩
  EkDurum  λ_son = Hata ⊙ Yazmaç_son
           λ_{i−1} = Eşlenik(Kapı_i)·λ_i      ← λ EŞLENİK ister
           ψ_{i−1} = Evrik(Kapı_i)·ψ_i        ← ψ EVRİK ister
           Eğim[p]   += 2·ölçek·Re⟨ λ_i | dKapı_i·ψ_{i−1} ⟩
           Metrik[p] += ölçek²·( ‖dKapı_i·ψ_{i−1}‖² − |⟨ψ_{i−1}|dKapı_i·ψ_{i−1}⟩|² )
  İkiz     dψ_i = Kapı_i·dψ_{i−1} + ölçek·yön[p]·dKapı_i·ψ_{i−1}
           Türev = 2·Re⟨ Hata⊙ψ_son | dψ_son ⟩
  Mutabakat = |EkDurum·yön − İkiz| / |İkiz|    ← sıfır değilse biri yalan söylüyor

DÖRT MEMUR -- toplanmaz, her biri ayrı cins (MECZ, meclis değil):
  ÇUKUR    ΔE = √(⟨Hata²⟩ − ⟨Hata⟩²)                → hüküm: durak mı
  EĞİM     Yön = −Eğim, SIRALANIR                   → yön verir
  VADİ     Yön = birim(enbüyükArgüman(Metrik·Sıra))  → adımın YERİNE
  NAKİL    Kuyu = −|Dizinin genliği| / tepe
           T    = WKB geçirgenliği(Kuyu)
           U    = Evrim(H_kuyu, H_atlama, π·T)       ← Trotter-Suzuki, zar YOK
           Yön  = birim( |U · (en kuvvetli koordinat)|² )
  DUVAR İLGA EDİLDİ (ferman 1-Ğ, 2-Ú): koordinat ELENMEZ, yalnız SIRALANIR.

YARIÇAP  = Keyfiyet(üç hudut) / √İz(FubiniStudy)     ← sabit eta YOK (1-J)
           Eğrilik = BükülmeEnerjisi / (BükülmeEnerjisi + Artık²)
           Yarıçap ← Yarıçap / (1 + Eğrilik)
           ← tarama daveti DEĞİL, yalnız adımın boyu; hat araması YOK (2-P)

Aday   = p + Yarıçap · Yön
V_aday = Skaler(Aday)                        ← TUR BAŞINA YEGÂNE ÇAĞRI

KABUL: hükmü TAM MİZAN VEKTÖRÜ verir; keyfiyet bir KEFEDİR, veto değil (2-Ü)
RET   : hat eğriliğinden ANALİTİK düzeltme, EK ÇAĞRI YOK
        κ = 2(ΔV_gerçek − ΔV_lineer) / Yarıçap²
        Yarıçap* = −ΔV_lineer / (κ · Yarıçap)        ← hat üstünde tam Newton
        κ ≤ 0 ise hat bükey değildir: Yarıçap* = 2·Yarıçap

Öğrenme oranı YOK. Momentum YOK. Geri yayılım YOK. Hat araması YOK.
```

### D9 KÜME KAPANIŞI -- bir defa, küme temizlenince

| | |
| :-- | :-- |
| **GİRDİ** | `Hafıza` · `KapıHükmü` · `Fock` · biriken yırtık defteri |
| **AMELİYE** | Yırtıklar tertiplenir, kapı tenakuzları terfi eder, balyalanır |
| **ÇIKTI** | `Hafıza′` · `Balya` |

```
HAFIZA SİLİNMEZ, YENİDEN TERTİPLENİR (ferman 2-Ú):
  1 ALÂKA     A(k) = İz( YoğunlukMatrisi(kayıt_k) · Π_R )
  2 DÜĞÜM ÇÖZ eski yapıştırma bağları gevşetilir
  3 TABAN DEĞ. Yaprak = Örtüşmesi EN DÜŞÜK vecih   ← şahitsiz, en çok ayıran
               Kök    = MahallîYazmaç.CartanEkle("modalite."+Yaprak, Ayırt)
               ← YENİ ORTOGONAL kök; evvelki köklerin adresi KAYMAZ (2-İ)
  4 YENİDEN MÜHÜR  ρ_yeni = U_tertip·ρ_eski·U_tertip† + Δρ

BALYALAMA -- UNUTMA YOK, TECRİT VAR (ferman 2-Ƶ):
  Hafıza artar → kategori doygunlaşır → mertebe yükselir
  → eski kayıtlar üst kategorinin BİR NESNESİNDE balyalanır
  → balya AÇILABİLİR (funktörün tersi şarttır)
  Tekrarın az yer tutması bunun TABİÎ NETİCESİDİR: aynı şeyin n nüshası
  n nesne değil, tek üst nesnenin n katlı hâlidir.
  SİLİNEN SIFIR OLMALIDIR.

TERTİP KÜME KAPANINCA BİR DEFA KOŞAR; arada yırtıklar deftere birikir.
```

### D10 KELÂM -- `nefs/soyle.py` (alt makine § 5)

| | |
| :-- | :-- |
| **GİRDİ** | `Nefs(p*)` · `Hafıza` · `Netice` · `Suâl` |
| **AMELİYE** | Vecih açılır, cümle üretilir, vecih kapanır |
| **ÇIKTI** | `Kelâm` yahut `Sükût` · `Güven` · `UzunlukHükmü` |

### D11 MÜHÜR -- `main/hazine.py:muhurle`

| | |
| :-- | :-- |
| **GİRDİ** | `p*` · `Hafıza′` · `MünasebetHaritası′` · `İmleç′` · `TabanDurumu` · `Fock` |
| **AMELİYE** | **TEK DOSYAYA** yazılır |
| **ÇIKTI** | `Hazine` -- sonraki koşunun D3 girdisi |

```
Hazine = (p, Hafıza, MünasebetHaritası, SilsileDefteri, İmleç,
          TabanDurumu, Fock, ÖlçülenHız, Tur)
         ← DEVAM ASILDIR; sıfırlama açık bir FİİLDİR: main.egitim sıfırla
```

---

## § 3. ÇÖZÜM UZAYI ALT MAKİNESİ -- S0 … S6

```
S0 VAKUM ──metin geldi──▶ S1 SINIR ──▶ S2 MESELE ──┬──F⁻¹ var──▶ S3 UZAY
   │                                               └──mesele yok─▶ S6
   └──girdi YOK ve kapı TÂLİM──────────────────────▶ S2      (ferman 2-Ħ)

S3 UZAY ──▶ S4 SÜZÜLMÜŞ ──▶ S5 HÜKÜM ──┬──yeni vecih──▶ S3
                                        └──kapandı─────▶ S6 İNTAÇ
```

| Durum | GİRDİ | AMELİYE | ÇIKTI |
| :-- | :-- | :-- | :-- |
| S0 VAKUM | -- | Fock `\|0⟩`; hiçbir mod açık değil | boş hâl |
| S0 → S2 (tâlim) | iç hâl havuzu | `G_t = argmax_G { E_tenakuz(G) − λ·Entropi(G) }` | özerk gaye |
| S1 SINIR | metin | entropi gradyanı; **entropisi en yüksek bölge aranan şeydir** | kısıt grafı |
| S2 MESELE | kısıt grafı | dört suâl: mesele var mı · kaide ne · geri yol nasıl · metin ne | `Sual` · `a†` ile mod |
| S3 UZAY | `Sual` | uzay **kaidesinden doğar**: Yoneda → Kohomoloji → Lie | `Uzay` · funktör `F` |
| S4 SÜZÜLMÜŞ | `Uzay` | **sadakat devresi** + mukayese süzgeci | süzülmüş hâl |
| S5 HÜKÜM | süzülmüş hâl | hüküm çıkar; yeni vecih ateşlendiyse S3'e dön | hüküm · `a` ile sönüm |
| S6 İNTAÇ | hüküm | `ψ ← ψ · conj(F)`  ← **funktörün tersi** | `Netice` |

```
KAİDE BİR KANUNLAR MANZUMESİDİR (ferman 2-Ú-E); üç usul SIRAYLA koşar,
her biri bir evvelkinin ÇIKTISINI girdi alır:

1 YONEDA -- DIŞ MÜNASEBET, hudut kanunları
    Hom(−,a)     = ( ⟨Hâl_k | Hâl_a⟩ )  bütün k için
    tip.hudut    = 1 − |⟨birim Hom(−,a) | birim Hom(−,b)⟩|²
    tip.temas    = Σ_k |Hom_k(a)|·|Hom_k(b)| / (‖·‖·‖·‖)
    Dokunan(a,b) = { k : |Hom_k(a)|·|Hom_k(b)| > ortanca }
                   ↓ ÇIKTI: Dokunan
2 KOHOMOLOJİ -- İÇ DOKU, korunum kanunları   (δ∘δ = 0)
    Holonomi(k)       = ⟨a|b⟩⟨b|k⟩⟨k|a⟩         k ∈ Dokunan(a,b)
    kategori.korunum  = | ortalama_k e^(i·arg Holonomi(k)) |
    Çekirdek(a,b)     = { k : |arg Holonomi(k)| ≤ ortanca }
                   ↓ ÇIKTI: Çekirdek
3 LIE / CASIMIR -- DİNAMİK, dönüşüm kanunları
    e₁ = Hâl_a,  e₂ = birim( Hâl_b − ⟨e₁|Hâl_b⟩e₁ ),  X = e₂e₁† − e₁e₂†
    Açı_ab       = arccos |⟨Hâl_a|Hâl_b⟩|        ← taşıma zamanı, ÖLÇÜLÜR
    U            = Evrim(σ_y, σ_x, Açı_ab)       ← Trotter-Suzuki
    uzay.dönüşüm = ortalama_{Çekirdek} ( 1 − |⟨z_k | U z_k⟩|² )
    uzay.casimir = ‖ ortalama_{Çekirdek} BlochVektörü ‖   ← su(2) DEĞİŞMEZİ

SIRA DEĞİŞMEZ: dış hudut çizilmeden iç omurga aranmaz, omurga
sabitlenmeden dinamik hesaplanmaz.

Kaide(a,b) = ( tip.hudut, tip.temas, kategori.korunum, kategori.çekirdek,
               uzay.dönüşüm, uzay.casimir )
Ölçek      = ortancaSapma(Kaide over bütün çiftler)   ← eşik ÖLÇÜLÜR (1-J)
İmza(a,b)  = yuvarla( Kaide(a,b) / Ölçek )
Âlem       = aynı İmzalı münasebetlerin öbeği
             ← KAÇ AYRI KAİDE İMZASI VARSA O KADAR ÂLEM; özdeğerden GELMEZ
Vecih(Âlem)= izdüşüm( birim( Σ_öbek AyırtEdiciYön(a,b) ) )
Tayf(Âlem) = ( Nispet(r,n | öbeğin kutupları) )  BÜTÜN (r,n) için
             ← ÇÖKERTİLMEZ (ferman 2-Ú-B): argmax ile tek mertebe SEÇİLMEZ
```

**MUKAYESE MELEKESİ -- durumu EVİRMEZ, hüküm çıkarır (ferman 2-Ú):**

```
Δ_n(ψ₁…ψ_n) = ⟨ψ₁|ψ₂⟩⟨ψ₂|ψ₃⟩ … ⟨ψ_n|ψ₁⟩ = r_n · e^(i·Φ_n)
Φ_n         = Σ_{k=2}^{n−1} Φ₃(ψ₁, ψ_k, ψ_{k+1})   (mod 2π)
Halka boyu  : BÜTÜN BOYLAR BERABER, n = 2 … m      ← sabit boy YOK
Tenakuz Φ_n → π  ·  Kısırdöngü Φ_n → 0  ·  Kopuk r_n = 0
Sorites tuzağı O(1)'de: yerel ⟨ψ_k|ψ_{k+1}⟩ ≈ 1 iken kapalı halkada Möbius
Cins(hâl)   = ‖Vecih(hâl)‖'i AZAMÎ yapan vechin ÂLEMİ
              ← HER ÂLEM KENDİ HALKASINI KAPATIR; veri cinsi CİNS DEĞİLDİR
```

---

## § 4. SADAKAT DEVRESİ -- HER DURUMDA KOŞAN DOĞRULAYICI

| | |
| :-- | :-- |
| **GİRDİ** | O anda mevcut **bütün** süperpozisyonlar |
| **ÇIKTI** | Süzülmüş süperpozisyonlar + dört sayı |

```
her Ψ için:
    Güç       = |Genlik|²
    MANTIKSIZ = kod uzayının dışı (parite) ∪ sonlu olmayan ∪ imkânsız işaret
    MÜMKÜN    = kod uzayının içi, Güç ≥ ortanca(içerideki Güç)
    MEÇHUL    = kod uzayının içi, 0 < Güç < ortanca     ← DOKUNULMAZ

    Ψ[MANTIKSIZ] ← 0 ;  Ψ ← Ψ / ‖Ψ‖
    İmha   += |MANTIKSIZ ∩ dolu|
    Meçhul += |MEÇHUL|

ÜÇ KÜME ŞARTTIR. İkiye indirmek meçhulü mantıksız saymaktır ve
kendimizi kilitler (ferman 2-Đ).

Meçhul = 0 ise devre FAZLA ELİYOR demektir; sayı raporda görünür.
Muaf   ≠ ∅ ise invaryant I8 ihlâl edilmiştir; taht DURUR.

KAPSANAN SÜPERPOZİSYONLAR:
    veri · parametre · mahallî · hafıza · mesele(Fock) · çözüm · uzunluk
    ← liste KAPALI DEĞİLDİR; yeni süperpozisyon doğduğunda devre ona da
      vurulur, aksi hâlde "bağlanmamış" diye sayılır (ferman 2-Ý, 2-Đ)
```

---

## § 5. KONUŞMA ALT MAKİNESİ -- J1 … J5

```
J1 LOGİT ──θ_j = π·p_j──▶ J2 FAZ KAYDIRICI ──P_jeton──▶ J3 NORM
                                                           │
                          ‖Ψ‖² = 0 ──▶ J4 CEZA (negatif logit maskesi)
                                                           │
                          ‖Ψ‖² > 0 ──▶ J5 KELÂM ──durma?──▶ dur / devam
```

| | |
| :-- | :-- |
| **GİRDİ** | `Bağlam` · `Netice` · `Hafıza` · `Vecihler` |
| **ÇIKTI** | `Belirteç dizisi` yahut `Sükût` |

```
Bağlam_basamak = TabanAçılımı(tiktoken(Suâl), VeriLifi, BasamakSayısı)
                 ← modülo katlama YOK; her belirteç basamağa açılır

VECİH CÜMLE ÖMÜRLÜDÜR: bir defa açılır, cümle boyunca açık kalır,
DURMA HÜKMÜ gelince kapanır (ferman 2-Ú-D).
  Merak    = { k : Şüphe(k) > Yakîn(k) }      ← 𝒪15 ateşlemesi, BİR KEZ
  Vecihler = VecihAç(AçılışHâlleri, Merak)    ← Merak sönükse BOŞ

tekrarla:
  Hâl        = İleriGeçiş(Yerleştir(Bağlam))
  eğer Durma(adım): dur                        ← ÜST HUDUT YOK (2-Ó-B)
  Dağılım    = Σ_{v ∈ Vecihler} Ağırlık(v)·Marjinal(İzdüşüm(v, Hâl)) / ΣAğırlık
               Vecih yoksa düz Marjinal(Hâl)   ← nedensel cephede
  Budanmış   = Buda(Dağılım, Hafıza.cerh)
  jeton      = enbüyükArgüman( ∇log Budanmış / g_FubiniStudy )
               ← ZAR ATILMAZ (ferman 2-Ĵ): determinist Fubini-Study okuması
  GERİ YOL   : n(jeton) = ‖P_kısıt·Ψ(jeton)‖² / ‖Ψ‖²
               n = 0 ⇒ negatif logit cezası, jeton GERİ ALINIR
               ← aynı jeton İKİNCİ DEFA maskelenemez (kısırdöngü, I4)
  Bağlam    ← Bağlam + jeton

VecihKapat(Vecihler)        ← açık kalan vecih SIFIR olmalıdır

Durma(adım) = UzunlukKatmanı[adım] > Σ_{k>adım} UzunlukKatmanı[k]
              ← uzunluk bir KARAR değil, süperpozisyonun hükmü (2-Õ)

Hafıza ← Yaz(Yazmaç_son, ω = e^(−Bedel/uzunluk), hüküm = tasdik)
         ← KONUŞMA HAFIZAYA BAĞLIDIR (ferman 2-Ó)

Kesinlik = (Güven − 1/VeriLifi) / (1 − 1/VeriLifi),  Güven = e^(−Bedel/boy)
Sükût eğer AlanDeğeri(sükût) > Kesinlik  yahut  Şüphe = teâruz
       ← eşik SABİT DEĞİL, cevabın kendi kesinlik nispeti (ferman 1-J)

KELÂM İKİ ŞARTA BAĞLIDIR (ferman 2-Ø): ya burhan tamamlanmıştır, ya iç
muhakeme tıkanmıştır ve SUAL TEVCİH EDİLİR. Üçüncüsü yoktur.

Mihenk: her ~300 saniyede  Cevap(p_şimdiki, sabit İngilizce suâl) → kütük
```

---

## § 6. ÖLÇÜLEN HUDUTLAR VE AÇIK ÇELİŞKİLER

### 6-A. İDDİA EDİLEN VE ARKASINDA DURULAN

| İddia | Sayı / delil | F |
| :-- | :-- | :-- |
| Faz defteri Galois'dadır; genlik büyüklüğü süreklidir ve öyle kalır | `Z_m` tamsayı üssü + Palmer çeyreği | 2-J |
| Aşkın çağrı gövdede serbesttir, **sayılır** | beyanda görünür | 2-Ş, 2-U |
| Derece-12 iz terimi derece-3'e **tam** iner | `İz(α·x¹²) = İz(α^¼·x³)` | 7-B |
| Klonlanamazlık **kasten** ihlâl edildi | bedel: donanım taşınabilirliği; karşılık: doğruluk ve hız | 1-T |
| Üç eğimin mutabakatı | `2.2e-16` | 2-P |
| Senet sadakati | `1.3e-15` | 2-P |
| Eğimin kapsadığı serbestlik | `130 / 676` tahsis edilen (**%19.2**) | 5 |
| DUVAR kodda **ilga edildi** | `mecz` dört memurla koşar, koordinat elenmez | 1-Ğ, 2-Ú |
| Mihenk cevabı hezeyandır | ölçüldü; geçersiz 0/8, ayrı basamak 2 | 5 |
| Küme(temiz) | `0` -- üç hudut henüz sönmedi | 1-I |

### 6-B. AÇIK ÇELİŞKİLER -- GİZLENMEZ, SAYILIR

| # | Çelişki | Hüküm |
| :-- | :-- | :-- |
| 1 | `_psi` hâlâ yaşıyor (`nefs.y.psi`), ferman 2-Ĝ ise **kazınmasını** emrediyor | Kazıma yarım; sadakat devresi şimdilik `psi` üstünden koşuyor. Tam kazıma ayrı bir tertibattır ve **sorulacaktır** (2-D) |
| 2 | `QAyar.kulli_alanlar` on bir bölge sayıyor; ferman 1-Ş **yazmaçta bölge yoktur** diyor | Bu satır silinmeden *"yazmaçta bölge kalmadı"* denemez |
| 3 | Pencere haddi ferman 2-O/2-Õ'de `1 048 576`; koşan pencere ise çözüm uzayı makinesinin hükmü | Hadd bâkîdir; koşan değer makinenin ölçtüğüdür ve raporda **ikisi yan yana** yazılır |
| 4 | Mantık yürütme (`nefs/usul.py`) kodda tam fakat makineye **vidalanmadı** | **TEHİR EDİLDİ** (2-Đ): kesilmez, padişahın kararını bekler |
| 5 | Müşahede (`nefs/musahede.py`) ARC ızgarasına mahsus | ARC vasfı **imha edilecek**; kalacak kanadın taşıyıcısı açık sualdir (2-Œ) |
| 6 | Kalp uzvu yok | **TEHİR EDİLDİ** (2-Ł): ahlâk ve taklit vicdanının yeri olacak |
| 7 | Uzunluk süperpozisyonu tahttan geçmiyor | Sadakat devresinde **"bağlanmamış"** diye sayılıyor; kırmızı yanıyor |
