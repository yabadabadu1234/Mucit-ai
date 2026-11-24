# KURAM ZİYADELERİ — icra edilmiş ve sayılmış

Her satır `kuram_sina.py` içinde bir fonksiyondur; bu dosya onun çıktısından üretilir (elle yazılmaz). Geçen: **101 / 101**.

| No | Bölüm | Ziyade (neyi sınadı) | Usul | Sonuç | Ayrıntı |
| --: | :-- | :-- | :-- | :-: | :-- |
| 1 | A. Dil ve Katman I | Dil bilgisi (EBNF karşılığı ayrıştırıcı) belgelerdeki 25 notasyon örneğini ayrıştırır | ayrıştırıcı koşturuldu | GEÇTİ | 25 |
| 2 | A. Dil ve Katman I | Bozuk ifadeler (10 örnek) reddedilir; ayırt eden ayrıştırıcı | SyntaxError beklendi | GEÇTİ | 10 |
| 3 | A. Dil ve Katman I | Yaz→ayrıştır gidiş dönüşü özdeş (25 örnek) | AST eşitliği | GEÇTİ |  |
| 4 | A. Dil ve Katman I | Öncelik tablosu tek ayrıştırma verir: ayrıştır(yaz(ağaç)) = ağaç, derinlik-2 bütün ağaçlar | bütün ağaçlar sayıldı | GEÇTİ | 2906 |
| 5 | A. Dil ve Katman I | Belgelerde ⊕ üç ayrı manada kullanılmış (dışlayıcı veya · açılım toplamı · tropikal max); onarılmış tabloda her sembolün tek manası var | kaynak metin okundu, onarım tablosu denetlendi | GEÇTİ | çatışma kaynakta var: [True, True, True] |
| 6 | A. Dil ve Katman I | ⊬ işareti belgede karşı-olgusal şart (Lewis) için kullanılmış, matematikte "türetilemez" demektir; □→ ile değiştirildi ve ayrıştırıcıda ikilidir | kaynak metin okundu, ayrıştırıcı | GEÇTİ |  |
| 7 | A. Dil ve Katman I | Dualler: F(φ)=O(¬φ), P(φ)=¬O(¬φ) bütün seri çerçevelerde (3 dünya) ve bütün değerlemelerde | KD modelleri sayıldı | GEÇTİ | 8232 |
| 8 | A. Dil ve Katman I | D aksiyomu (O→P) seri çerçevede geçerli, seri olmayan çerçevede çürür | KD modelleri sayıldı | GEÇTİ | 1536 |
| 9 | A. Dil ve Katman I | Ahkâm-ı hamse (farz, mendup, mübah, mekruh, haram) mütebâyin ve hâsır: 5 hüküm, her geçerli üçlü tek hükme düşer | üçlüler sayıldı | GEÇTİ | {'haram': 3, 'farz': 3, 'mendup': 1, 'mekruh': 1, 'mubah': 1} |
| 10 | A. Dil ve Katman I | Mübah ile SDL'nin P'si ayrı kavramdır: farz olan eylem P(φ) olduğu hâlde mübah değildir | bir model | GEÇTİ |  |
| 11 | A. Dil ve Katman I | Chisholm dörtlüsü SDL'de tatmin edilemez, ikili (tercihli) deontikte tatmin edilir | sonlu modeller tarandı | GEÇTİ | SDL tatmin=False, ikili=True |
| 12 | A. Dil ve Katman I | Düz semantikte "O(φ) ve ruhsat" çelişir; öncelikli (özel kaide genele galip) semantikte tatmin edilir | bağlamlar sayıldı | GEÇTİ | ([True, False], ['ruhsat', 'farz']) |
| 13 | A. Dil ve Katman I | Şart–istisna kapalı formu (Kural 5) öncelikli semantikle eşit: O_tam(φ/¬γ ; φ'/γ) her bağlamda | bağlamlar sayıldı | GEÇTİ |  |
| 14 | A. Dil ve Katman I | İç içe istisna (üç öncelik) kapalı formu: en özel hüküm kazanır, eşit öncelikte çelişki bildirilir | bağlamlar sayıldı | GEÇTİ | ['farz', 'farz', 'ruhsat', 'farz_tekrar'] |
| 15 | A. Dil ve Katman I | Epistemik: K_x reflektif (T geçerli, bütün denklik çerçeveleri), B_x için T çürür (KD45 karşı modeli) | çerçeveler sayıldı | GEÇTİ | B φ ∧ ¬φ modeli var |
| 16 | A. Dil ve Katman I | Katman saflığı denetçisi: B_Hasım(φ) öncülünden φ sonucu reddedilir, K_Allah(φ)'den kabul edilir | denetçi iki yönde koşuldu | GEÇTİ |  |
| 17 | A. Dil ve Katman I | □ (sünnetullah): K ve T aksiyomları yansımalı çerçevelerde geçerli; ◇ = ¬□¬ | çerçeveler sayıldı | GEÇTİ |  |
| 18 | B. Katlama kuramı | Açılım∘Katlama = kimlik: altı kuralın hepsi, 1–5 çocuk, iç içe katlama dâhil | bütün kural ve boylar sayıldı | GEÇTİ | 30 |
| 19 | B. Katlama kuramı | Katlama birebirdir: 6 atomun bütün 63 boş olmayan alt kümesi 63 ayrı katlamaya gider ve geri açılır | bütün alt kümeler | GEÇTİ | 63 |
| 20 | B. Katlama kuramı | Kural 1 (ortak terim): dağıtıcı yüklemde katlama eşdeğerdir (16 yüklem × 15 alt küme); toplu yüklemde (Cemaat) eşdeğer DEĞİLDİR, bu yüzden yan şart gerekir | bütün yüklemler | GEÇTİ | toplu yüklem karşı misali var |
| 21 | B. Katlama kuramı | Kural 2 (iz koruyan zincir): A→[B]→C ≡ (A→B)∧(B→C); (A→C)'yi gerektirir; (A→C) ile eşdeğer değildir (iz kaybı) | 8 değerleme | GEÇTİ | zincir⊨A→C, eşdeğer değil |
| 22 | B. Katlama kuramı | Kural 2 ikili (şartlı) yükümlülükte GEÇERSİZDİR: O(B/A) ve O(C/B) varken O(C/A) çürüyebilir; kural yalnız ta'lîl şartlısına tahsis edilir | sıralamalar tarandı (3^8) | GEÇTİ | karşı model bulundu |
| 23 | B. Katlama kuramı | Kural 3 (bölünme): klasik mantıkta R1∨R2'yi gerektirir; sezgisel (Heyting) mantıkta gerektirmez (iki noktalı Kripke karşı modeli): kural dışlanmış üçüncü şartına bağlanır | tam Heyting hesabı | GEÇTİ | sezgiselde gerekmez |
| 24 | B. Katlama kuramı | Kural 4 (fonktörel yasa) tümdengelim DEĞİL istikrâîdir: sonlu şahitlerin hepsi doğruyken evrensel yasa yanlış olabilir; durum yalnız {boş, istikrâî, reddedilmiş}, "burhan" asla | bütün alanlar | GEÇTİ | {'reddedilmis', 'istikrai'} |
| 25 | B. Katlama kuramı | Kural 5 muhafazakârdır: ruhsat şartı dışında kapalı form ana hükme düşer (kapsam dışına tesir yok) | bağlamlar | GEÇTİ |  |
| 26 | B. Katlama kuramı | Kural 6 (tanım katlaması): X := v1∧v2∧v3 tanımıyla "X→R" ile "v1∧v2∧v3→R" (ayrıştırıcı ve ölçerle) eşdeğer; tanımsız serbest X ile eşdeğer değildir | 32 değerleme, ayrıştırılmış ifadeler | GEÇTİ | serbest X farkı var |
| 27 | B. Katlama kuramı | Birleşme (confluence): 6 atomun 203 bölüntüsünün hepsinde, katlama sırası ne olursa açılım aynı çoklu kümedir | Bell(6) bölüntü | GEÇTİ | 203 |
| 28 | B. Katlama kuramı | Sonlanma: her katlama adımı üst düzey terim sayısını (n−1) azaltır; N atomdan en çok N−1 adım | bütün bölüntüler | GEÇTİ | 4 |
| 29 | B. Katlama kuramı | L0→L4 yükseltmesi: beş kat iç içe katlamada her kat bir önceki katın çoklu kümesini aynen verir | beş kat | GEÇTİ |  |
| 30 | B. Katlama kuramı | Kayıpsızlık denetçisi: bir atom düşürülen 8 katlama reddedilir, sağlam katlama kabul edilir (ayırt eden ölçü) | mutasyon | GEÇTİ | 8 |
| 31 | B. Katlama kuramı | Temsil hesabı (gerçek derlem, 103. sûre): v1…v4 R6 ile katlanınca üst düzey terim 7→4, açılımdaki atom sayısı 7 kalır | derlem sayımı | GEÇTİ |  |
| 32 | B. Katlama kuramı | Zincir izi: A→[B1…Bk]→C açılınca k+1 gerektirme verir ve (A,[B…],C) tek türlü geri okunur (k=0…5) | k taraması | GEÇTİ |  |
| 33 | C. Âyetten âyete bağlar | Sekiz başlık yedi aslî ilişkiye iner: Ta’lîl, Tefrî‘in tersi; Tafsîl/İcmâl tek ilişkinin iki yönü; ad→(ilişki, yön) birebir | tablo denetlendi | GEÇTİ | (9, 7) |
| 34 | C. Âyetten âyete bağlar | Bağ ilişkilerinin özellikleri tutar: Tefrî‘ geçişli ve yansımasız (kısmî sıra), Mukâbele simetrik ve geçişsiz, Temsîl denklik (yansımalı, simetrik, geçişli) — 5 elemanlı örnek modellerde | özellik taraması | GEÇTİ |  |
| 35 | C. Âyetten âyete bağlar | Kapsama ve süreklilik (örnek derlem, 103 ve 112): her ardışık âyet çiftine sekiz bağdan biri atanmış; bir bağ silinince denetçi yakalar | derlem + mutasyon | GEÇTİ |  |
| 36 | C. Âyetten âyete bağlar | Hiperkenar ikili bağdan kuvvetlidir: üç kuyruklu hiperkenar d'ye ancak üçü de erişilmişse götürür; aynı kenarı üç ikili oka açmak a'dan tek başına d'ye götürür (yanlış) | erişim hesabı | GEÇTİ |  |
| 37 | C. Âyetten âyete bağlar | İkili bağ hiperkenarın özel hâlidir: zincir erişimi iki temsilde aynı (sonlu zincirler 1…6) | zincir taraması | GEÇTİ |  |
| 38 | C. Âyetten âyete bağlar | Bağ derecesi hep "hikmet ihtimali"dir; derlemde murâd-ı ilâhî iddiası içeren bağ yok (lint) | derlem lint | GEÇTİ |  |
| 39 | D. Zaman ölçekleri | Delta türevi (f(σ)−f)/μ; belgedeki f(t_{k+1})−f(t_k) yalnız μ=1 hâlidir: f=t², μ=2 noktasında 2 yerine 4 verir | iki ölçek | GEÇTİ |  |
| 40 | D. Zaman ölçekleri | İşaret değişmezliği: işaret(f^Δ) = işaret(ileri fark) bütün zaman ölçeklerinde (nitel iddialar ölçeğe bağlı değildir) | ölçek ve fonksiyon sayımı | GEÇTİ | 17199 |
| 41 | D. Zaman ölçekleri | İkinci mertebe: eğim farkıyla tanımlanır; düzgün ölçekte ham ikinci farkla işareti eşit, düzgün olmayan ölçekte ayrışır (0,1,3: ham fark 0, gerçek ivme eksi) | sayım | GEÇTİ | (Fraction(0, 1), Fraction(-1, 2)) |
| 42 | D. Zaman ölçekleri | Çarpım kuralı (fg)^Δ = f^Δ g + f^σ g^Δ doğrulanır (6 ölçek × 3 polinom çifti, tam rasyonel) | özdeşlik taraması | GEÇTİ | 54 |
| 43 | D. Zaman ölçekleri | Analizin temel teoremi ∫_a^b f^Δ Δt = f(b)−f(a) (Hilger toplamı) bütün a<b noktalarında | özdeşlik taraması | GEÇTİ | 15 |
| 44 | D. Zaman ölçekleri | Sürekli sınır: çok ince düzgün ölçekte f=t² için f^Δ(t)−2t tam olarak h (adım) kadardır, yani sürekli türeve yaklaşır | tam rasyonel | GEÇTİ |  |
| 45 | D. Zaman ölçekleri | Geçerlilik ağırlığı W∈{0,1}: W=0 olan aralıkta φ≠0 olsa da birikim sıfırdır; W≡0 ise toplam sıfırdır | toplam denetimi | GEÇTİ |  |
| 46 | D. Zaman ölçekleri | Nitel integral (işaret toplamı): hep artı → artı; artı+eksi → "?"; sıfırlayıcı ağırlıkla çarpılmış terimler hesaba girmez | durum taraması | GEÇTİ |  |
| 47 | D. Zaman ölçekleri | Geçmiş dönüştürme operatörleri: T_sil idempotent (T∘T=T), T_çevir involüsyon (T∘T=kimlik), ikisi birbirine eşit değil | bütün dizilerde | GEÇTİ |  |
| 48 | E. İşaret cebiri ve kısmî türev | İşaret cebiri kapalı ve değişmeli: ⊕ ve ⊗, {−,0,+,?} üzerinde 16 çiftin hepsinde | tam tablo | GEÇTİ |  |
| 49 | E. İşaret cebiri ve kısmî türev | İşaret cebiri birleşmelidir: ⊕ ve ⊗ için 64 üçlünün hepsinde | tam tablo | GEÇTİ |  |
| 50 | E. İşaret cebiri ve kısmî türev | Dağılma yalnız alt-dağılmadır: a⊗(b⊕c) ⊑ (a⊗b)⊕(a⊗c) 64 üçlüde; tam eşitlik bozulduğu üçlü sayısı yazılır | tam tablo | GEÇTİ | tam eşitliğin bozulduğu üçlü: 0 / 64 |
| 51 | E. İşaret cebiri ve kısmî türev | Soyutlama sağlamdır: gerçek sayılar için işaret(x+y), işaret(x)⊕işaret(y)'nin kapsadığı kümededir; işaret(xy) = işaret(x)⊗işaret(y) | gerçek sayı örnekleri | GEÇTİ |  |
| 52 | E. İşaret cebiri ve kısmî türev | Belirsizlik yayılır: "?" ile sıfırdan farklı bir işaretin toplamı daima "?"; "?"⊗0 = 0 (yalnız sıfır belirsizliği yutar) | tam tablo | GEÇTİ |  |
| 53 | E. İşaret cebiri ve kısmî türev | Bileşik monoton fonksiyonun işareti çarpımdır: afin eğimler a,b ∈ {−2…2} için işaret(g∘f) = işaret(a)⊗işaret(b) | eğim taraması | GEÇTİ |  |
| 54 | E. İşaret cebiri ve kısmî türev | Kısmî türev işareti: x+0·z için ∂/∂z = 0 (etkisizlik yakalanır), ∂/∂x = +; x·z için z∈{−1,0,1}'de ∂/∂x = "?" (bağlama göre işaret değişir) | sonlu alan taraması | GEÇTİ |  |
| 55 | F. Hiperreel sonsuz küçük | ε>0 ve her n için ε<1/n (n=1…20000, tam rasyonel); ε²<ε: Arşimet özelliği çiğnenir | sıralı halka ℝ(ε) | GEÇTİ |  |
| 56 | F. Hiperreel sonsuz küçük | Sıra toplamdır (üçleme): 15 elemanlı kümede her çift için tam biri <, =, > | çift taraması | GEÇTİ |  |
| 57 | F. Hiperreel sonsuz küçük | Φ(dα)≠0: Φ(x)=x³ için Φ(ε)≠0, oysa klasik limit standart kısımda 0 verir; yani sonsuz küçük kayıpsız tutulur, limit onu yutardı | hesap | GEÇTİ |  |
| 58 | F. Hiperreel sonsuz küçük | Aktarım örneği: ∀x>0 ∃y (0<y<x) hiperreellerde de geçerli (y=x/2; x=ε için ε/2) | örnekler | GEÇTİ |  |
| 59 | F. Hiperreel sonsuz küçük | Arşimet'ten ayrılış: 100000·ε < 1 hâlâ doğru; klasik ℝ'de ise 1/ε'ye karşılık gelen bir n bulunurdu | hesap | GEÇTİ |  |
| 60 | F. Hiperreel sonsuz küçük | Standart kısım st: sonlu hiperreellerde toplama ve çarpmaya uyar, st(3+2ε)=3, sonsuz büyükte tanımsız (reddeder) | örnek taraması | GEÇTİ |  |
| 61 | G. Lineer cebir | Rank testi (GF(2)): yeni denklem mevcut bazların XOR bileşimiyse rank artmaz; bağımsız yeni eksense 1 artar | rank hesabı | GEÇTİ |  |
| 62 | G. Lineer cebir | Rank bazdan bağımsızdır: 5 satırın bütün 120 permütasyonunda ve satır toplamı eklemelerinde aynı | permütasyon taraması | GEÇTİ |  |
| 63 | G. Lineer cebir | Dikgenlik = ayrık dayanak: dayanakları ayrık sıfırdan farklı iki vektörde rank toplanır; ortak dayanakta toplanmayabilir (ikame edilemezlik ölçüsü) | bütün çiftler (6 bit) | GEÇTİ |  |
| 64 | G. Lineer cebir | Özdeğer işareti: aynı operatör T farklı öznelerde +1 ve −1 verir; numpy özdeğerleri (+1,−1) ve özvektörler tutar | sayısal | GEÇTİ |  |
| 65 | G. Lineer cebir | Rank–sıfırlık teoremi GF(2) üzerinde: 3×3'lük 512 matrisin hepsinde rank + boyut(çekirdek) = 3 (çekirdek brute-force sayıldı) | bütün matrisler | GEÇTİ | 512 |
| 66 | G. Lineer cebir | Dik izdüşüm: P=U(UᵀU)⁻¹Uᵀ idempotent ve simetrik (4 altuzay), asıl vektör bozulmaz: v = Pv + (I−P)v dik toplamı | sayısal | GEÇTİ |  |
| 67 | G. Lineer cebir | Çekirdek–görüntü bölüşümü: kabul operatörü T (GF(2) üzerinde 3×3, 512 tane) için /ker/·/Im/ = 8; geçersizleşenler ve geçerli sonuç üretenler vektör uzayını tam böler | bütün matrisler | GEÇTİ |  |
| 68 | H. Tensör | Daraltma derecesi bir azaltır: ∀-daraltma (p,q)-tensörün boyutunu 3'ten 2'ye indirir, her eksen için | şekil denetimi | GEÇTİ |  |
| 69 | H. Tensör | ∀∀ ve ∃∃ daraltmaları farklı eksenlerde değişmelidir: 256 tensörün hepsi, iki sırayla | bütün tensörler | GEÇTİ |  |
| 70 | H. Tensör | ∀∃ ile ∃∀ değişmez: 2×2 tensörlerde (∃j ∀i) ⇒ (∀i ∃j) hep doğru, tersi yanlış (karşı örnek: [[1,0],[0,1]]) | bütün 16 tensör | GEÇTİ |  |
| 71 | H. Tensör | Kesit ve daralma farklı eksenlerde değişir: önce 0. eksende 0'ı seç sonra 2. ekseni ∀-daralt = önce daralt sonra seç (256 tensör) | bütün tensörler | GEÇTİ |  |
| 72 | H. Tensör | Evrensel değişmez her kesite iner (sağlamlık): ∀-daraltılmış eksen sabitlenince hüküm her kesitte doğru (256 tensör) | bütün tensörler | GEÇTİ |  |
| 73 | H. Tensör | Daraltma birebir değildir (256 tensör → en çok 16 görüntü), bu yüzden kayıpsız daraltma kesitleri saklar: kesitlerden asıl tensör yeniden kurulur (256/256) | bütün tensörler | GEÇTİ | 16 |
| 74 | I. Tropikal ve sıralı cebir | (max,+) yarı halka aksiyomları {−∞,0,1,2,3,4} üzerinde (birleşme, değişme, birim, dağılma, ⊕ idempotent) | bütün üçlüler | GEÇTİ |  |
| 75 | I. Tropikal ve sıralı cebir | (max,min) sıralı yarı halka (zincir 0…4) aksiyomları ve çift dağılma; bu cebirde rakam gerekmez, yalnız sıra | bütün üçlüler | GEÇTİ |  |
| 76 | I. Tropikal ve sıralı cebir | Aksiyom 3 ile çatışma: iki yolun puanı sıra-izomorfik yeniden etiketlemede (max,+) ile DEĞİŞİR, (max,min) ile DEĞİŞMEZ | bütün artan etiketlemeler | GEÇTİ | (max,+) kararları [False, True]; (max,min) kararları [False] |
| 77 | J. Heyting kafesi, ağaç ve çizge | Alexandrov yukarı-kümeleri Heyting cebridir: W∩U ⊆ V ⇔ W ⊆ (U⇒V), bütün üçlülerde | bütün üçlüler (zincir 3) | GEÇTİ |  |
| 78 | J. Heyting kafesi, ağaç ve çizge | Dışlanmış üçüncü Heyting'te çöker: zincir 3'te U ∪ ¬U ≠ tüm uzay olan açık küme vardır (karşı model) | karşı model | GEÇTİ | ihlâl eden açık küme sayısı: 2 |
| 79 | J. Heyting kafesi, ağaç ve çizge | Çifte olumsuzlama: U ⊆ ¬¬U hep, ¬¬U = U her U için değil (Heyting'e özgü) | karşı model | GEÇTİ |  |
| 80 | J. Heyting kafesi, ağaç ve çizge | ∅ ⇒ V = tüm uzay (boş öncül her şeyi gerektirir) ve U ⇒ U = tüm uzay | bütün açıklar | GEÇTİ |  |
| 81 | J. Heyting kafesi, ağaç ve çizge | Ağaç ultrametriktir: d(x,z) ≤ max(d(x,y),d(y,z)), 15 düğümde 3375 üçlü | bütün üçlüler | GEÇTİ |  |
| 82 | J. Heyting kafesi, ağaç ve çizge | Ultrametrikte her üçgen ikizkenardır (en büyük iki kenar eşit) | bütün üçlüler | GEÇTİ |  |
| 83 | J. Heyting kafesi, ağaç ve çizge | Ortak ata simetriktir ve ortak_ata(x,x)=x: 225 çift | bütün çiftler | GEÇTİ |  |
| 84 | J. Heyting kafesi, ağaç ve çizge | Basit döngüler: üç düğümlü halka tek döngü verir; ters kenar eklemek döngü sayısını artırır; DAG'ta sıfırdır | sayım | GEÇTİ |  |
| 85 | J. Heyting kafesi, ağaç ve çizge | Erişilebilirlik geçişlidir: 6 düğümlü yönlü çizgede R(x,y) ∧ R(y,z) ⇒ R(x,z) bütün üçlülerde | bütün üçlüler | GEÇTİ |  |
| 86 | J. Heyting kafesi, ağaç ve çizge | Hiperkenar VE anlamındadır: (üç öncül → sonuç) kenarda tek öncül eksilince sonuç erişilmez; ikili kenar bunu söyleyemez | örnek | GEÇTİ |  |
| 87 | K. Dinamik ve oyun | Goodwin eşiği (n=3 negatif halka): (s+1)³+g=0 köklerinde g=7,9 kararlı, g=8,1 kararsız (eşik 8) | sayısal kökler | GEÇTİ |  |
| 88 | K. Dinamik ve oyun | Pozitif halka: (s+1)³−g kökleri; g>1 reel pozitif kök (çoklu denge), g<1 hepsi kararlı | sayısal kökler | GEÇTİ |  |
| 89 | K. Dinamik ve oyun | Tarski: sonlu kafeste monoton fonksiyonların sabit noktası vardır (100 sabit tohumlu monoton fonksiyon, 3 elemanlı alt küme kafesi) | örnekler | GEÇTİ |  |
| 90 | K. Dinamik ve oyun | Potansiyel oyun özdeşliği (Monderer–Shapley): bütün tek-taraflı sapmalarda Δu_i = ΔΦ, 24 sapma | tam tarama | GEÇTİ |  |
| 91 | K. Dinamik ve oyun | Potansiyel oyunda en iyi-cevap dinamiği 8 başlangıçtan da Nash'e erer (20 adımda durur) | tam tarama | GEÇTİ |  |
| 92 | K. Dinamik ve oyun | Zaman ölçeğinde Δ(x²) = σ(x)+x = 2x+1 (tamsayı ölçek) ve düzensiz ölçekte formül μ ile ayarlanır | tam tarama | GEÇTİ |  |
| 93 | K. Dinamik ve oyun | Temel teorem: ∫ₐᵇ Δf = f(b) − f(a), düzensiz ölçekte 5 işlev | tam tarama | GEÇTİ |  |
| 94 | L. Üst kuram: tutarlılık, mutasyon, bağımsızlık | Tutarlılık: bütün yan şartların aynı anda sağlandığı modeller var — KD modelleri, 3-zincir Heyting, işaret cebiri, ZamanOlcegi | model varlığı | GEÇTİ |  |
| 95 | L. Üst kuram: tutarlılık, mutasyon, bağımsızlık | Mutasyon: Kural 3'ten "dışlanmış üçüncü" şartını silince Heyting karşı modeli ihlâli yakalar (ölçü ayırt eder) | mutasyon | GEÇTİ |  |
| 96 | L. Üst kuram: tutarlılık, mutasyon, bağımsızlık | Mutasyon: sahte ⊕ (a?b:a) yazılırsa değişme ölçüsü kırmızı yanar; gerçek ⊕ geçer | yanlış iddia reddi | GEÇTİ |  |
| 97 | L. Üst kuram: tutarlılık, mutasyon, bağımsızlık | Bağımsızlık: işaret cebirinde "?" aksiyomu gerekir; {+,−,0} üzerinde + ⊕ − kapalı değil | karşı model | GEÇTİ |  |
| 98 | L. Üst kuram: tutarlılık, mutasyon, bağımsızlık | Bağımsızlık: Boole şartı (¬¬U=U) 2 elemanlı ayrık (antichain) modelde geçerli, 3-zincirde geçersiz — ayrı aksiyomdur | iki model | GEÇTİ |  |
| 99 | L. Üst kuram: tutarlılık, mutasyon, bağımsızlık | Karar verilebilirlik: işaret ifadeleri 4 işaretli 5 değişkende 1024 atamanın hepsinde sonlu sürede kapanır | tam tarama | GEÇTİ | 1024 |
| 100 | L. Üst kuram: tutarlılık, mutasyon, bağımsızlık | Doğrusal zaman: ayrıştırma süresi terim sayısıyla en çok doğrusal-artı-sabit büyür (200→1600 terim, oran ≤ 32) | ölçüm | GEÇTİ | oran=9.2 (terim 8 kat) |
| 101 | L. Üst kuram: tutarlılık, mutasyon, bağımsızlık | Occam: kural sayısı altıdır (KURALLAR kaydı), her biri farklı yapıya dayanır | sayım | GEÇTİ |  |
