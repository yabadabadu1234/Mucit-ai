# MUCİT-AI -- MİMARİNİN TAM FORMÜLÜ

Semboller yerine isimler kelimedir; ameliyeler formüldür. Yazılan şey
**koşan koddur**, niyet değil (ferman 2-K).

---

## 0. KIYAS -- TRANSFORMER VE BİZ

    TRANSFORMER:
      Baş(Gizli) = Gizli + yumuşakenbüyük(Gizli·Sorgu · (Gizli·Anahtar)ᵀ / √boyut) · Gizli·Değer
      Kat(Girdi) = Baş(Girdi) + doğrultucu(Baş(Girdi)·Ağırlık₁) · Ağırlık₂
      Çıktı      = Kat₃(Kat₂(Kat₁(Girdi)))

    BİZ:
      Meleke(Yazmaç) = Kapı(Yazmaç, Açı(Parametre))            ← katman değil, ameliye
      Yazmaç         = Vicdan(Meleke₄₅(…Meleke₂(Meleke₁(Yazmaç₀))…))
      Çıktı          = Normalize(Toplam(SatırlaraBöl(Yazmaç)))

---

## 1. GİRDİ

    Belirteç    = tiktoken(Metin)                         tiktoken.n_vocab = 200019
    BasamakSayısı = enküçük k öyle ki VeriLifi^k ≥ tiktoken.n_vocab      = 5
    Basamak     = TabanAçılımı(Belirteç, VeriLifi, BasamakSayısı)
    Kodlanmış[satır, sütun] = 1 eğer sütun = Basamak[satır], değilse 0

    Örnek       = (Bağlam, Hedef, Cins, Makam)             Cins ∈ {ARC, sözlü}
                  Makam = Hedef basamağın grup içindeki yeri, 0..BasamakSayısı−1
    Pencere     = ikininkuvveti(enuzunGörev × BasamakSayısı) = 65536
                  Boyut ≥ Pencere olmak ZORUNDA (ferman 2-M)

---

## 2. YAZMAÇ

    Karo    = ikininkuvveti(√Pencere)                     öyle ki Yer ≥ Pencere
    Yer     = Karo × Karo                                 BASAMAK BAŞINA yer
    Boyut   = VeriLifi × Yer
    Yazmaç  = Genlik[yığın, Boyut]                        karmaşık, TAM tutulur

    Seviye(basamak, mevki) = basamak × Yer + mevki
              ← 0. EKSEN BASAMAKTIR, adımı Yer'dir; mevki kalan eksenlerdedir.
                Yazmaç bağlam kadardır (ferman 2-M) fakat hadd basamak
                başına yerdedir, Boyut'ta değil (ferman 2-O).

    Sektör(ad) = Genlik[başlangıç(ad) : bitiş(ad)]
    AlanDeğeri(ad) = Toplam(|Sektör(ad)|²)

    ad ∈ {makam, mizan, tenakuz, tasdik, sükût, nakz, kelâm, kaide,
          orak, gaye, tertip}

    SEKTÖR CEVABIN EVİ DEĞİLDİR. Sektör bitişik bir dilimdir, basamak
    ekseni ise Yer adımıyla yazmacın tamamına yayılır; ikisi ayrı
    koordinattır. Cevap YALNIZ basamak ekseninin marjinalinden okunur
    (§ Hâl), sektörden değil. Sektör yalnız küllî ölçüleri taşır.

### Belirtecin genliğe girişi -- Rijndael otomorfizmi

    yuva ∈ Seviye(Belirteç, 0 … Yer−1)            ← belirtecin KENDİ basamak bloğu
    Zarf(yuva)   = 1 / (1 + (yuva − orta)² / genişlik)              ← rasyonel
    Çeyrek       = (1, i, −1, −i)
    Genlik[yuva] = Zarf(yuva) × Çeyrek[ SBox((yuva + Belirteç) mod 256) mod 4 ]

    SBox(x) = AfinKatman(x^254)  içinde  GF(2⁸),  P(x) = x⁸+x⁴+x³+x+1

### Faz -- tamsayı defteri, aşkın işlem yok

    Üs        = (Üs + yuvarla(−Açı × FazMertebesi / 2π) + Artık) mod FazMertebesi
    Artık     = Üs mod (FazMertebesi / 4)
    ÇeyrekNo  = (Üs − Artık) / (FazMertebesi / 4)
    Genlik    = Palmer(Genlik, ÇeyrekNo)

    Palmer(gerçek + sanal·i, 0) = gerçek + sanal·i
    Palmer(gerçek + sanal·i, 1) = −sanal + gerçek·i
    Palmer(gerçek + sanal·i, 2) = −gerçek − sanal·i
    Palmer(gerçek + sanal·i, 3) = sanal − gerçek·i

    Artık genliğe İNMEZ, deftere geri konur.
    FazBorcu = ortalama(Artık) / (FazMertebesi / 4)          ← ölçülür, basılır

---

## 3. İLERİ GEÇİŞ

    Yazmaç₀ = Harman(Yerleştir(Kodlanmış))

    Yerleştir(Kodlanmış):
        mevki ∈ 0 … n_satır−1,   basamak = Basamak[mevki]
        Genlik[ Seviye(basamak, mevki) ] = 1                 ← GENLİĞE
        Açı   [ Seviye(basamak, mevki) ] = −2π (basamak + 1) / VeriLifi
        FazDefteri ← FazDefteri + Açı                        ← FAZA
        Genlik = Normalize(Genlik)

    Bağlam HEM GENLİĞE HEM FAZA girer. Yalnız faza girseydi cevaba hiç
    ulaşmazdı: Hâl |Genlik|² okur, faz ise büyüklüğü değiştirmez.

    Bağlam bir skalere EZİLMEZ: son basamak ilk basamak kadar ağırlık taşır.
    DOLDURMA YOKTUR: n_satır neyse yazmaç o kadardır (ferman 2-O).

    Yazmaç  = Faz(Yazmaç, CartanFazı)        ← II. safha, harmandan EVVEL
    Harman(Yazmaç) = ⨀(kademe, lif, bitdüzlemi) Dönme(Açı(Parametre))
              ← açılar TOHUMDAN değil PARAMETREDEN gelir; böylece tâlim
                faz→genlik yolunu kendi açar ve genişletir.

    Yazmaç_k = Vicdan(Meleke_k(Yazmaç_{k−1}, Parametre))        k = 1 … 45

      Meleke_k(Yazmaç, Parametre) = Kapı_k(Yazmaç, Açı_k(Parametre))
      Okuma_k[ad]                 = AlanDeğeri(Yazmaç_k, ad)      ad ∈ İlan_k
      ΔEntropi_k                  = Entropi(Yazmaç_k) − Entropi(Yazmaç_{k−1})

    Sıra = (1..24, 25..32, 33, 13, 34..36, 37..41, 42..44)       45 adım, 44 meleke

### Sıranın sonundaki dört ameliye

    Gaye(Yazmaç) = KontrollüİşaretKapısı(nakz, gaye)
                 ∘ KontrollüİşaretKapısı(tenakuz, gaye)
                 ∘ FazTopla(gaye, (+tasdik, +tasdik, −tenakuz, −nakz) × Açı(Parametre))
                 ∘ ÇeyrekDönme(gaye)

    Yazmaç_son = Normalize(FazKilidi(Sadakat(İntaç(Gaye(Yazmaç₄₅)))))

### Hâl -- hem cevap hem kaide hipotezi

    Satırlar = YenidenŞekillendir(Yazmaç_son, VeriLifi, Yer)
    Hâl      = Normalize(Toplam(|Satırlar|², son eksen))

    Hâl BASAMAK EKSENİNİN MARJİNALİDİR. Yerleştir hangi eksene yazdıysa
    Hâl o ekseni okur; ikisi aynı eksendir ve kesişimleri TAMDIR.

---

## 4. HATA -- SKALER DEĞİL, VEKTÖR

    Hata = ( Hata_meleke[1..44],
             Hata_alan[makam..tertip],
             Hata_kademe[1..kademeGörevi],
             Hata_zırh[demet, betti, kohomoloji, homotopi, nizam],
             Hata_kaideHalkası, Hata_taşma,
             Hata_nokta, Hata_uzay, Hata_kategori, Hata_tip,
             Hata_çevrim, Hata_tenakuz, Hata_gedik,
             Hata_monogami, Hata_engel, Hata_lif )

### Bileşenler

    Hata_meleke[k]  = ortalama over ad ∈ İlan_k of Eksik(Okuma_k[ad], Sözleşme_k[ad])
    Hata_zırh[nizam] = enbüyük over k of Yüzleştir(Sınıf_k, ΔEntropi_k)

    Hata_uzay     = 1 − Uhlmann(Hâl, Hedef)                       ← ÇIPA, ağırlık 1
    Hata_nokta    = −ln İz(HedefİzdüşümÜ · YoğunlukMatrisi(Hâl))
    Hata_kategori = ‖ Morfizm(g∘f) − Morfizm(g) · Morfizm(f) ‖²
    Hata_tip      = ⟨Artık, HodgeLaplasyeni · Artık⟩ / ‖Artık‖²
                       Artık = Hâl − Harmonik(Hâl)
    Hata_çevrim   = |Holonomi(Çevrim) − Fıtrat|
    Hata_tenakuz  = −ln((İz(Birim + GerçekKısım(ÇevrimÜniteri)) + ε) / (2·Boyut + ε))
                    × DışlamaEntropisi(Çevrim)
    Hata_gedik    = Borç(Usul, KaranlıkÇevrimler)
    Hata_monogami = enbüyük(0, Dolaşıklık(bütün) − Toplam(Dolaşıklık(ikili)))
    Hata_engel    = Engellenme(Yazmaç, SürekliÖlçüm)
    Hata_lif      = 1 − SıraBağıntısı( Mesafe(Bağlam_i, Bağlam_j),
                                       −ln |⟨ Hâl_i | Hâl_j ⟩| )
                    over bütün çiftler (i<j) of Çözünürlük örnek
                       Çözünürlük = VeriLifi                  ← yazmaçtan gelir
                       ayrışmayan mesafe ⇒ Hata_lif = 1 (kırmızı)

    Eşik_taşma    = tavan(n_vocab / VeriLifi^(BasamakSayısı−1))       = 4
    Hata_taşma    = ortalama over {örnek : Makam = BasamakSayısı−1}
                    of Σ(basamak ≥ Eşik_taşma) Dağılım[basamak]
                    ← üst makamda Eşik_taşma ve üstü basamak DAİMA taşar

### Kaide halkası -- modelin kendi hipotezlerinin teftişi

    Hipotez[j]  = Hâl[j]                            aynı Cins'ten örnekler
    Bargmann    = ∏(j) ⟨Hipotez[j] | Hipotez[j+1 mod n]⟩

    Hata_kaideHalkası = (1 − |Bargmann|)
                      + [açı(Bargmann) ≈ π]          ← tenakuz
                      + [açı(Bargmann) ≈ 0]          ← kısırdöngü
                      + [enküçük |⟨·|·⟩| ≈ 0]        ← kopukluk

    Elle yazılmış kaide YOKTUR: kaide, modelin kendi hâlidir.

### Ağırlık ve tek toplama

    Ağırlık = Rezonans(Hata) / Rezonans(Hata)[uzay]              ← ölçülür, yazılmaz
    Skaler  = Σ(j) Ağırlık[j] × Hata[j]                          ← TOPLAMA YALNIZ BURADA

---

## 5. ADIM -- MECZ: BEŞ MEMURİYET, TEK KAYIP ÇAĞRISI

Kör yön araması ilga edildi (ferman 2-P). Türev geri geldi fakat tek
başına değil: yanına dört yardımcı memur verildi. Hat araması YOKTUR.

### 5-A SENET -- ileri geçişin kaydı

    Senet   = [ (tür, yer, dizey) ]                 her kapı vuruşu sırayla
    tür ∈ {karo, bant, çift_lif, faz, ölçek, sektör, maske, durum}
    Bağlantı = [ (senetNo, parametre, ölçek, türevTarifi) ]

    SenetSadakati = ‖SenetiOynat(Yazmaç₀) − Yazmaç_son‖ / ‖Yazmaç_son‖
                  ← senet TAM ise sıfır; ölçülür ve basılır

### 5-B EĞİM -- üç mekanizma, tek hakikat

    Üreteç:    Eğim[p] = Σ 2·ölçek·Re⟨ Hata⊙Yazmaç_son | dKapı·Yazmaç_son ⟩
                         ← nihaî durumdan, DERİNLİK KÖRÜ, en ucuz

    EkDurum:   λ_son = Hata ⊙ Yazmaç_son
               λ_{i−1} = Eşlenik(Kapı_i) · λ_i        ← λ EŞLENİK ister
               ψ_{i−1} = Evrik(Kapı_i) · ψ_i          ← ψ EVRİK ister
               Eğim[p] += 2·ölçek·Re⟨ λ_i | dKapı_i·ψ_{i−1} ⟩
               Metrik[p] += ölçek²·( ‖dKapı_i·ψ_{i−1}‖² − |⟨ψ_{i−1}|dKapı_i·ψ_{i−1}⟩|² )
                         ← metrik köşegeni BEDAVA: U_{>i} üniter

    İkiz:      dψ_i = Kapı_i·dψ_{i−1} + ölçek·yön[p]·dKapı_i·ψ_{i−1}
               Türev = 2·Re⟨ Hata⊙ψ_son | dψ_son ⟩
                         ← ileri kip, YAPISAL OLARAK BAĞIMSIZ

    Mutabakat = |EkDurum·yön − İkiz| / |İkiz|
              ← ikisi de TAM olmalı; sıfır değilse biri yalan söylüyor

    dKapı  Dönme için  [[−sin, −cos], [cos, −sin]]
           DikİkiKübit için Daleckii-Krein:
               [Vᵀ·dexp(A)·V]_pq = [Vᵀ·M_k·V]_pq · (e^{λp} − e^{λq})/(λp − λq)

### 5-C BEŞ MEMURİYET -- toplanmaz, her biri ayrı cins (mecz, meclis değil)

    ÇUKUR   ΔE = √(⟨Hata²⟩ − ⟨Hata⟩²)                  → hüküm: durak mı
    DUVAR   Maske = Metrik/enbüyük(Metrik) > ortanca·10⁻³
                                                        → koordinat ELER
    EĞİM    Yön = −Eğim ⊙ Maske, normalize                → yön verir
    YARIÇAP Yarıçap = 1 / √Σ Metrik                       → boy verir
            Eğrilik = BükülmeEnerjisi / (BükülmeEnerjisi + Artık²)
            Yarıçap ← Yarıçap / (1 + Eğrilik)
    VADİ    Yön = birim(enbüyükArgüman(Metrik ⊙ Maske))   → adımın YERİNE
    NAKİL   aynı fakat sapma en büyük olan eksende        → adımın YERİNE

    Aday = Parametre + Yarıçap · Yön
    V_aday = Skaler(Aday)                       ← TUR BAŞINA YEGÂNE ÇAĞRI

    KABUL KAPISI -- keyfiyet adımın BOYUNU değil KABULÜNÜ tayin eder:
    Keyfiyet_aday = KeyfiyetSon()          ← V_aday çağrısında ölçülen
    Kirletti = Keyfiyet_aday < Keyfiyet

    eğer V_aday < V ve değil Kirletti:
                      Parametre ← Aday,  YarıçapDüzeltmesi ← 0
    değilse:          hat eğriliğinden ANALİTİK düzeltme, ek çağrı YOK
        Çözünürlük = MakineEpsilonu · enbüyük(|V|, |V_aday|)
        eğer |ΔV_gerçek| ≤ Çözünürlük:   kayıp adımı HİSSETMEDİ
                                          Yarıçap* = 2·Yarıçap
        ΔV_lineer = ⟨Eğim, Yarıçap·Yön⟩
        κ         = 2(ΔV_gerçek − ΔV_lineer) / Yarıçap²
        Yarıçap*  = −ΔV_lineer / (κ · Yarıçap)      ← hat üstünde TAM Newton
        κ ≤ 0 ise hat bükey değildir: Yarıçap* = 2·Yarıçap

    Öğrenme oranı YOK. Momentum YOK. Geri yayılım YOK. Hat araması YOK.
    Sabit eta YOK, kelepçe YOK (ferman 1-J).


### 5-D PARAMETRE YAZMACI -- İKİNCİ QUDİT SİSTEMİ (ferman 2-R)

    ParametreSeviyesi = enbüyük ikinin kuvveti k öyle ki
                        Yığın · VeriSeviyesi · k · 16 ≤ ÖlçülenBellek · Pay

    Parametre[k] = ( Genlik[k],  Açı[k] )        Açı[k] ∈ [−π, π]
                 ← FAZ SÜREKLİDİR; Z_m tamsayı kafesi İLGA (ferman 2-V)
    Açı(anahtar, k) = Açı[ Adres(anahtar)[k] ]
                    ← ÇIPLAK PARAMETRE YOKTUR; melekenin her açısı budur
    Σ_k Genlik[k]² = 1

    TaşımaKapasitesi = Taban ^ QuditSayısı        ← uzay iddiası
    MahallîSerbestlik = 2 · QuditSayısı           ← bellek iddiası

### 5-E ÇİFT YAZMAÇ KENETLENMESİ -- SEYİRCİ QUDİT (ferman 2-V)

    TemasKapıları = defterde tahsis edilmiş bütün adresler
    Seyirci       = QuditSayısı − |TemasKapıları|
                  ← seyircinin iç çarpımı 1'dir; q^N dal AÇILMAZ

    Basamak(t)    = 2 · Veri[t] / (Taban − 1) − 1
    Gerilim(j)    = |Basamak(j) − Basamak(j−1)| + |Basamak(j) − Basamak(j+1)|
    Rezonans(k)   = k. sırada en yüksek Gerilime sahip qudit koordinatı
    Hedef(k)      = Rezonans(k)
                  ← BAĞLAM BASAMAĞI LAĞVEDİLDİ (ferman 2-Z): hedef elle
                    yazılmaz, veri manifoldunun kendi geriliminden çıkar
                    ve her kodlamada yeniden tayin edilir.

    EtkileşimEnerjisi(Veri) =
        − toplam over k of  Genlik[Kontrol(k)] · Açı[Kontrol(k)]
                            · Basamak(Hedef(k))

    EklenenFaz(Veri) = toplam over k of  Açı[Kontrol(k)] · Basamak(Hedef(k))

    Genlik(Veri, Parametre) = üstel( Reel(Veri) − EtkileşimEnerjisi(Veri)
                              + i · ( Sanal(Veri) + EklenenFaz(Veri) ) )
                              / Bölen
        Reel(Veri)  = toplam over k,j of Katsayı_C[k,j] · ChebyshevBirinci
        Sanal(Veri) = toplam over k,j of Katsayı_S[k,j] · ChebyshevİkinciU

    ChebyshevBirinci(u, j) = kosinüs( j · arkkosinüs(u) )
    ChebyshevİkinciU(u, j)  = sinüs((j+1)·arkkosinüs(u)) / sinüs(arkkosinüs(u))
                            ← HAKİKÎ FONKSİYON; tekrarlama ikamesi yasak (2-U)

    Yığın ekseni kenetlemesi (Dilim, DalAğırlığı, MüşterekYığın) İLGA;
    Palmer çeyreği ile faz çökmesi de İLGA -- faz sürekli üstel.

### 5-F MAHALLÎ YAZMAÇ -- DONANIM KANADI (ferman 2-Ş)

    MahallîYazmaç[örnek, j] = ( Genlik[j],  Açı[j] )     Açı ∈ [−π, π]
        Genlik[j] = Dolu(j) / ‖Dolu‖              ← ayrık, mahallî
        Açı[j]    = π · Basamak(j)

    KapıVur(Kontrol, Hedef, Bağ):
        Açı[Hedef(k)] ← Açı[Hedef(k)] + Bağ(k) · Açı[Kontrol(k)]
        ← yalnız temas edilen qudit döner; kalanı SEYİRCİDİR

    Genlik(Veri, Parametre, MahallîYazmaç) =
        üstel( Reel − EtkileşimEnerjisi
               + i · ( Sanal + EklenenFaz + MahallîYazmaç.Açı ) ) / Bölen

    İKİ SEVİYE AYRIDIR (ferman 2-Ş):
        Yazmaç(B, d)      TEKİL KAVRAM LİFİ -- bir quditin iç anatomisi
        MahallîYazmaç     KÜLLÎ yazmacın mahallî tensörü (qudit × 2)

---

## 6. DIŞ DÖNGÜ -- BİR VERİ, HUDUDU TEMİZLENENE KADAR

    Zayıflık(Örnek) = ortalama(1 / (1 + MünasebetHaritası[Bağlam(Örnek)]))
    Küme            = enbüyük öbek tanesi Zayıflık(Kalan)

    tekrarla en çok AzamiTur kere:
        Ağırlık   ← Rezonans(Hata(Parametre, Küme))         ← her turda YENİDEN
        Parametre ← Adım(Parametre, Küme)
        dur eğer HudutTemiz(Küme)

    HudutTemiz    = (Tenakuz = 0) ve (Kısırdöngü = 0) ve (Mantıksızlık = 0)
    Mantıksızlık  = PariteTaşması + BelirteçTaşması          ← İKİ taşma
    Nispet_mantık = (1 − PariteTaşması) × (1 − BelirteçTaşması)

    MünasebetHaritası[a, b] += Nispet(Küme)     her a, b ∈ Bağlam(Küme)
                     ← TEK harita, hazineden yüklenir, hazineye geri konur;
                       turlar boyunca BİRİKİR (ferman 1-I, 1-Y)

    SilsileDefteri[Tip][Kategori][Uzay] += Σ(a ∈ Bağlam) MünasebetHaritası[a, ·]
        Tip       = "arc"  yahut  "sözlü"                    ← veri cinsi
        Kategori  = MertebeSeç(Bağlam).ℓ*                    ← nefs/hendese.py
        Uzay      = enyakın yuva of UzaylarıKur(Dinamik).mertebe ↔ boy(Bağlam)
                       Dinamik = 10 ölçülen bağlam boyu       ← idrak/kategori.py
        Kopukluk  = |{hücre : enbüyük örtüşme ≤ Eşik}| / |hücre|
                       Eşik = ortalama(örtüşme) × oran(örtüşme > 0)   ← keyfiyet

    eğer değil HudutTemiz:  Küme → Kuyruğun BAŞINA,  Sabır = f(Nispet)
    eğer HudutTemiz:        İmleç ← İmleç + bayt(Küme)   → Hazine

    Hazine = (Parametre, Hafıza, MünasebetHaritası, SilsileDefteri,
              İmleç, ÖlçülenHız, Tur)                        ← devam ASILDIR

---

## 6-B. VECİH VE MUKAYESE -- NETİCE ÇIKARAN MELEKE

    VERİ KAPISI (ferman 2-Ó) -- ret girene bakar, konuşmaya değil
                 KAPI KODLAMADAN SONRA KOŞAR: hüküm HÂLDEN okunur

    Parça        = ölçülen bellek haddine sığan örnek adedi  (ferman 5-B)
                   ← kapı imleçten gelen HER PARÇADA koşar, yığında değil
    Hâl(Örnek)   = İdrak(Kodla(Bağlam + Hedef))    ← örnek başına BİR idrak
    Vecihler     = VecihleriİstihraçEt(parçanın hâlleri)
    Eş(i)        = aynı Bağlamı paylaşan evvelki örnek, yoksa i−1
                   ← bu bir HÜKÜM değil, çiftin İKİNCİ KUTBUDUR

    ŞAHİT YOKTUR. Hüküm çiftin BÜTÜN VECİHLERDEKİ okumasından çıkar:

    Örtüşme(v)   = |⟨Hâl_i^(v) | Hâl_Eş^(v)⟩|²         her vecih v için
    İhtilaf      = azamî Örtüşme − asgarî Örtüşme
    İttifak      = 1 − İhtilaf        ← iki nispet toplamı BİR (ferman 1-J)

    Hüküm(Örnek) = mantıksızlık eğer basamak ∉ [0, VeriLifi)   → RET
                 | tenakuz      eğer İhtilaf > İttifak          → TERFİ
                 | kısırdöngü   eğer İttifak > İhtilaf ve asgarî ≥ İttifak
                 | tasdik       değilse
                 ← hükmü MUKAYESE MELEKESİ verir ve HAFIZAYA yazar
    Kabul(Örnek) = yanlış YALNIZ mantıksızlıkta;  tenakuz TERFİ eder
    HafızaKaydı  = tasdik | tevakkuf | cerh       ← kaydın CİNSİNİ kapı tayin eder

    VECİH İSTİHRACI (ferman 1-Ğ, 2-Ú) -- küllî matris ameliyesi YOK

    SORGU KANONİKTİR (ferman 2-Ú-E): ne öğrenilir ne dışarıdan gelir.
    KAİDE BİR KANUNLAR MANZUMESİDİR; üç usul SIRAYLA, üçü de koşar --
    her biri bir evvelkinin neticesini girdi alır:

    1 YONEDA -- DIŞ MÜNASEBET, hudut kanunları
      Hom(−,a)     = ( ⟨Hâl_k | Hâl_a⟩ )  bütün k için   ← nesnenin ağı
      tip.hudut    = 1 − |⟨birim Hom(−,a) | birim Hom(−,b)⟩|²
      tip.temas    = toplam over k of |Hom_k(a)|·|Hom_k(b)| / (‖·‖·‖·‖)
      Dokunan(a,b) = { k : |Hom_k(a)|·|Hom_k(b)| > ortanca(aynısı) }

    2 KOHOMOLOJİ -- İÇ DOKU, korunum kanunları  (δ∘δ = 0)
      Holonomi(k)        = ⟨a|b⟩⟨b|k⟩⟨k|a⟩            k ∈ Dokunan(a,b)
      kategori.korunum   = | ortalama over k of e^(i·arg Holonomi(k)) |
                           ← 1 ise kapalı 1-eşzincir TAM: sınıf âşikâr
      kategori.çekirdek  = |{ k : |arg Holonomi(k)| ≤ ortanca }| / |Dokunan|
      Çekirdek(a,b)      = o k'ler                     ← bozulamaz omurga

    3 LIE / CASIMIR -- DİNAMİK, dönüşüm kanunları
      e₁ = Hâl_a,  e₂ = birim( Hâl_b − ⟨e₁|Hâl_b⟩e₁ ),  X = e₂e₁† − e₁e₂†
      α_k = ⟨e₁|Hâl_k⟩,  β_k = ⟨e₂|Hâl_k⟩,  w_k = |α_k|² + |β_k|²
      uzay.dönüşüm = ortalama over Çekirdek of
                       ( w_k − 4·Im(β̄_k α_k)² ) / w_k     ← FS sürati
      uzay.casimir = ‖ ortalama over Çekirdek of BlochVektörü(α_k, β_k) ‖
                     ← su(2) dönmesi altında DEĞİŞMEZ

    Kaide(a,b)     = ( tip.hudut , tip.temas
                     , kategori.korunum , kategori.çekirdek
                     , uzay.dönüşüm , uzay.casimir )
                     ← SIRA DEĞİŞMEZ: dış hudut çizilmeden iç omurga
                       aranmaz, omurga sabitlenmeden dinamik hesaplanmaz
    KanunTayfı     = toplam over âlem of Kaide(âlem) × Ağırlık(âlem)
                     ← her kanunun ölçülen nispeti RAPORDA görünür;
                       tutmayan kanun gizlenmez, nispetiyle kırmızı yanar
    Ölçek          = ortancaSapma(Kaide over bütün çiftler)   ← eşik ÖLÇÜLÜR (1-J)
    İmza(a,b)      = yuvarla(Kaide(a,b) / Ölçek)
    Âlem           = aynı İmzalı münasebetlerin öbeği
    ÂlemAdı        = Tayf türü + hangi MERTEBENİN kanunları ölçeği aşıyorsa
                     ( tip · kategori · uzay ), hiçbiri aşmıyorsa "serbest"
    Vecih(Âlem)    = izdüşüm( birim( toplam over öbek of AyırtEdiciYön(a,b) ) )
                     AyırtEdiciYön(a,b) = birim( Hâl_a − ⟨Hâl_b|Hâl_a⟩·Hâl_b )
    Tayf(Âlem)     = ( Nispet(ℓ | öbeğin kutupları) )  BÜTÜN ℓ için, normalize
                     ℓ = 0 nokta · 1 uzay · 2 kategori · 3 tip · 4… Postnikov
                     ← ÇÖKERTİLMEZ (ferman 2-Ú-B): argmax ile tek mertebe
                       SEÇİLMEZ; bütün tipler süperpozisyonda taşınır,
                       tip çorbası analitik çözümlenir ve tayf raporlanır
    TipTayfı       = toplam over âlem of  Tayf(âlem) × Ağırlık(âlem)
                     ← "hangi tipler varmış, kaideleri neymiş" bundan okunur

    Yaprak(A,B)    = Örtüşme'si EN DÜŞÜK vecih   ← şahitsiz, en çok ayıran

    MİZANDA VECİH -- HER KEFE KENDİ ATEŞLEMESİYLE (ferman 2-Ú-D)

    Mizan bir vecih cetveli tutmaz; vecihe ihtiyaç duyan her kefe
    kendi merakını ateşler, vechini doğurur, neticesini alır, kapatır:

      HalkaKefesi   = MeraklaÇöz( ilk hâller , Merak(ilk hâller, ω) ,
                                  v ↦ ( Spektrum(v) , HipotezHalkası(v) ) )
      MukayeseKefesi= MeraklaÇöz( bütün hâller , Merak(bütün hâller, ω) ,
                                  v ↦ MukayeseMelekesi(cins = Âlem(v), v) )

    MUKAYESE MELEKESİ -- durumu EVİRMEZ, hüküm çıkarır

    Δ_n(ψ₁…ψ_n) = ⟨ψ₁|ψ₂⟩⟨ψ₂|ψ₃⟩ … ⟨ψ_n|ψ₁⟩ = r_n · e^(i·Φ_n)
    Φ_n         = toplam over k=2..n−1 of Φ₃(ψ₁, ψ_k, ψ_{k+1})   (mod 2π)
    Halka boyu  : BÜTÜN BOYLAR BERABER, n = 2 … m                 (ferman 2-Ú)
    Tenakuz     eğer Φ_n → π ·  Kısırdöngü eğer Φ_n → 0 ·  Kopuk eğer r_n = 0
    Yırtık      eğer sapma(üçgen*) > 3 × ortanca(sapma)

    Cins(hâl)   = ‖Vecih(hâl)‖'i AZAMÎ yapan vechin ÂLEMİ
                  ← HER ÂLEM KENDİ HALKASINI KAPATIR (ferman 1-Ç, 2-Ú):
                    veri cinsi (arc/sözlü) yahut kapı hükmü CİNS DEĞİLDİR

    HAFIZA YENİDEN TERTİBİ -- silme YOK, terfi VAR

    Yaprak   = Örtüşme'si EN DÜŞÜK Vecih          ← şahit yok, ayırt eden vecih
    Ayırt    = 1 − Örtüşme(Yaprak)
    Kök      = MahallîYazmaç.CartanEkle("modalite." + Yaprak, Ayırt)
               ← yeni ORTOGONAL kök; evvelki köklerin adresi KAYMAZ (2-İ)
    Hafıza   ← TabanDeğiştir(birim(A + B), Yaprak, ω = cos Φ₃)
    Tertip KÜME KAPANINCA bir defa koşar; yırtıklar deftere birikir.

---

## 7. KONUŞMA -- HER İKİ KAPIDA DA

    Bağlam_basamak = TabanAçılımı(tiktoken(Suâl), VeriLifi, BasamakSayısı)
                     ← modülo katlama YOK; her belirteç basamağa açılır

    VECİH CÜMLE ÖMÜRLÜDÜR -- adım ömürlü DEĞİL (ferman 2-Ú-D)
    Bir defa açılır, cümle boyunca açık kalır, DURMA HÜKMÜ gelince kapanır.

    AçılışHâlleri = ( İleriGeçiş(Bağlam[i : i+Pencere]) )  i = 0, P, 2P …
                    ← cümlenin suâli neyse vecih ONDAN doğar
    Merak         = { k : Şüphe(k) > Yakîn(k) }       ← 𝒪15 ATEŞLEMESİ, BİR KEZ
                    eşik sabit değil: şüphe ile yakîn birbiriyle tartılır (1-J)
    Vecihler      = VecihAç(AçılışHâlleri, Merak)     ← Merak sönükse BOŞ

    tekrarla:                                          ← AMELİYE: cümlenin tamamı
      Hâl        = İleriGeçiş(Yerleştir(Bağlam))
      eğer Durma(adım):  dur                           ← üst hudut YOK (2-Ó-B)
      Dağılım    = toplam over v ∈ Vecihler of
                     Ağırlık(v) · Marjinal(İzdüşüm(v, Hâl)) / Σ Ağırlık
                   Vecih yoksa düz Marjinal(Hâl)       ← nedensel cephede
      Budanmış   = Buda(Dağılım, Hafıza.cerh)
      Basamak_yeni = enbüyükArgüman( ∇log Budanmış / g_FubiniStudy )
                     ← ZAR ATILMAZ (ferman 2-Ĵ): determinist okuma
      Bağlam     ← Bağlam + Basamak_yeni

    VecihKapat(Vecihler)                               ← NETİCE ALINDI, KAPANDI
                   ← açık kalan vecih sayısı SIFIR olmalıdır; kapanış
                     ameliyenin kendisi hata verse de icra edilir

    Durma(adım) = UzunlukKatmanı[adım] > toplam over k>adım of UzunlukKatmanı[k]
                  ← uzunluk bir KARAR değil, süperpozisyonun hükmü (2-Õ)

    Hafıza ← Yaz(Yazmaç_son, ω = e^(−Bedel/uzunluk), hüküm = tasdik)
             ← konuşma hafızaya BAĞLIDIR (ferman 2-Ó)

    Belirteç = TabandanTopla(Basamak[BasamakSayısı'lı], VeriLifi)
    Cevap    = tiktoken⁻¹(Belirteç eğer Belirteç < n_vocab)
               taşan Belirteç SUSTURULMAZ, sayılır (ferman 2-L)

    Kesinlik = (Güven − 1/VeriLifi) / (1 − 1/VeriLifi),   Güven = e^(−Bedel/boy)
    Sükût eğer AlanDeğeri(sükût) > Kesinlik  ya da  Şüphe = teâruz
           ← eşik SABİT DEĞİL: cevabın kendi kesinlik nispeti (ferman 1-J)

    Tâlim ile Çıkarım arasındaki TEK fark:  çıkarımda Adım koşmaz.

    ÜRETİM YOLU TEKTİR (ferman 1-H). İkinci bir üretim yolu (kendi
    yazmacını kuran, parametresiz, bağlamı (t+1)/(k+1) diye tek skalere
    ezen) vardı ve kesildi; onunla beraber motor seçimi de kalktı.

    Mihenk: her ~300 saniyede  Cevap(Parametre_şimdiki, sabitSuâl)  →  kütük

---

## 8. ÖLÇÜLEN HUDUTLAR -- İDDİA EDİLEN VE ARKASINDA DURULAN

    Genlik.büyüklük ∈ kayanNokta   →  FAZ DEFTERİ Galois'dadır, genlik
                                      büyüklüğü süreklidir ve öyle kalır
    Aşkın çağrı ∈ canlı yol        →  formül hangi fonksiyonu söylüyorsa
                                      O ÇAĞRILIR; sayılır, gizlenmez (2-Ş)
    ReedMuller(Faz) = 12           →  İz(α·x¹²) = İz(α^¼·x³): derece-12 iz
                                      terimi derece-3'e TAM iner (7-B)
    Klonlanamazlık  = ihlâl edildi →  kasten; bedeli donanım taşınabilirliği,
                                      karşılığı doğruluk ve hız (ferman 1-T)

    Cevap(mihenk) = ""                     boş
        ölçüldü: geçersiz 1801/1801 = %100  (kestirdiğim %81 değil)
        sebep 1: mihenk Ayna'yı geçirmiyordu → düz enbüyük → sabit nokta
        sebep 2: külliyatta Makam daima (Pencere mod BasamakSayısı) idi,
                 yâni ÜST BASAMAK hiç hedef olmuyordu
        ikisi de düzeltildi; Hata_taşma artık kefe VE hudut çarpanıdır

    Cevap(mihenk) = " cei ёсць ёсць ёsць …"   hezeyan, sekizde yedisi tekrar
        ölçüldü: geçersiz 0/8, ayrı basamak 2, kabul 1/1, adım‖9,4e−1‖
        evvelki koşuda aynı yerde: geçersiz 8/8, ayrı basamak 1 SABİT NOKTA
        SABİT NOKTANIN SEBEBİ BULUNDU VE KESİLDİ: Yerleştir 0. basamağa
            yazıyor, Hâl ise kelâm sektöründen (v ≈ 0,378…0,486·VeriLifi)
            okuyordu -- İKİ KOORDİNAT, KESİŞİM BOŞ. Artık ikisi de
            basamak eksenidir.
        ÖLÇÜLEN: cevap hezeyandır. İDDİA EDİLEN: yolun açıldığı --
            adım 1'de, hiç eniyileme koşmadan cevabın değişmesi delildir.
        Küme(temiz) = 0                        üç hudut henüz sönmedi

    Üç eğimin mutabakatı = 2.2e-16   senet sadakati = 1.3e-15
        ölçüldü ve TUTUYOR. Kod okunarak bulunan dört kusurdan sonra:
        senedin eksikliği, durumun harita sanılması, yalan söyleyen
        geri ölçü, ve λ'da evrik/eşlenik karışması.
    Eğimin kapsadığı serbestlik = 130 / 676 tahsis edilen (%19.2)
        ÖLÇÜLEN: üreteci bildirilmemiş kapıya bağlı parametre kımıldamaz;
        eğim ancak üreteci ispatlanmış kapıların serbestliğini kapsar.## 0-A HENDESE TEŞHİSİ (Zabıt 11, I. safha)

    GeçişDizeyi[a,b]  = sayım(basamak_a → basamak_b) / satırToplamı
    KarşılıklıHaber   = Σ Ortak·log(Ortak / (Satır·Sütun))
    Sapma             = ‖GeçişDizeyi − GeçişDizeyiᵀ‖
    Nilpotent         = en küçük k öyle ki GeçişDizeyi^k = 0
    Denklik           = ⟨GeçişDizeyi(ilkYarı), GeçişDizeyi(sonYarı)⟩ / normlar
    Mesafe            = ensKısaYol(−log(GeçişDizeyi + GeçişDizeyiᵀ))
    δ_Gromov          = enbüyük |(d_ab+d_cd) − enbüyük(d_ac+d_bd, d_ad+d_bc)|

    Mertebe = enbüyükArgüman(
        1/(1+Haber+ŞartSapması),                        ← ayrık nokta
        (1−ÜçgenİhlâliNispeti)/(1+Sapma),               ← sürekli uzay
        Sapma × (1 eğer Nilpotent>0 değilse 1/4),       ← yönlü kategori
        enbüyük(0, Denklik) × (1+Haber))                ← univalent tip

    DikeyAsansör = Mertebe. kat
    BAĞ: ParitéLifi = DikeyAsansör.kat   (elle verilmediyse)
         yâni teşhis edilen katman, mantık muhafızı lifini seçer

---

## 0-B DHR SÜPERSEÇİM AYRIŞIMI (Zabıt 11, II. safha)

    CasimirYükü[seviye] = Σ_eksen biteSayısı(seviyeninEksenBasamağı)
    Sektör(q)           = {seviye | CasimirYükü[seviye] = q}
    Pay[yığın, q]       = Σ_{seviye ∈ Sektör(q)} |Yazmaç[yığın, seviye]|²

    CartanFazı[seviye]  = −Açı[CasimirYükü[seviye]]
    Yazmaç              = Faz(Yazmaç, CartanFazı)      ← FİİLEN VURULUR

    Sızıntı             = |1 − Σ_q ortalama(Pay[·, q])|
    AraYaGirmeİhlâli    = sayım(sıralıPay[i] < sıralıPay[i+1]) / denenen
    BlokKöşegenArtığı   = 1 − Σ_q (Σ_{Sektör(q)}|Yazmaç|²)² / (Σ|Yazmaç|²)²

    BAĞ: üçü de MİZANA KEFE olarak girer (bkz. § 4)

---


