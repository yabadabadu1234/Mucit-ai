# Münâsebet usulü · hiperkenar temeli

Kayıt: CLAUDE.md § 3-I 317. Bu belge `zaruret_zinciri/` ve `kitap_destek/USUL_TEKLIFLERI.md` ile birlikte okunur; hiçbiri silinmez.

## 1. Mesele

Soru: münâsebet kaydı "ok" ile (∴ → ⊥ ? ⌒) yazılırsa dışarıda kalan bağ çeşidi var mı?

Cevap: var. Ok **ikili ve yönlüdür**; aşağıdaki sekiz durumu kendi başına taşıyamaz. Beş oklu listenin hasrı da yoktur: kaynaklarda sayılan beş kenar tipi (istifham-cevap, illiyet, matla'-maktâ', istitrâd, tezâd; bkz. `kitap_destek/MUNASEBET_KANIT_OZETI.md`) **sayarak** (istikrâî) çıkmıştır. Aynı dosya halka/kiazmus ve "amud" yapısının bu dört metinde terim olarak bulunmadığını söyler; yani sayım kaynağın kullandığı dille sınırlıdır.

| # | Ok'un taşıyamadığı durum | Misal (kaynağı) |
|---|---|---|
| 1 | Üç ve daha çok üyenin **birlikte** taşıdığı bağ; ikili bağlara ayrılınca anlam kaybolur | Fâtiha 1:2, 1:3, 1:4 birlikte 1:5'in gerekçesi |
| 2 | Bölüntü: bir bütünün birbirini dışlayan kısımları | Fâtiha 1:7 (nimet verilenler · gazaba uğrayanlar · sapanlar); Bakara 2:2-5 mü'minler, 2:6-7 kâfirler, 2:8-20 münafıklar |
| 3 | Yönsüz (simetrik) bağ | Fâtiha 1:5 iki eş cümle |
| 4 | **Çok sayıda üyeli aynı kalıp** (nakarat) | Rahmân sûresinde "fe bi eyyi âlâi rabbikümâ tükezzibân" |
| 5 | Birimle **bütün** arasındaki bağ | Sûrenin gayesi ile âyetleri |
| 6 | **Bağın bağa** bağı | Bir tezâd bağının bir illiyet bağını desteklemesi |
| 7 | Metin **dışı** üye | Nüzûl sebebi, hitap şartı |
| 8 | **Örtüşen** kümeler; bölüm (bölüntü) modeli bir âyeti tek bölüme koyar | Fâtiha 1:5 hem hitaba dönüşün hem talebin içinde (bkz. `FATIHA_KAYITLARI.json` F02, F06; denetimde 1:5 dört kayıtta, 1:6 dört kayıtta yer alır) |

## 2. Temel: bağ bir hiperkenardır

Tanım: **bağ = üyeler kümesi + her üyenin kenardaki rolü + taşıyıcı + iddia cümlesi.**

Hasr (nefy–isbât):
1. Bir bağ, tanım gereği, bir alandan alınmış üyelerin (rolleriyle) kümesidir. Rolü olan üye kümesinden daha genel bir bağ biçimi yoktur; ikili ok iki üyeli ve rolleri {kaynak, hedef} olan özel hâldir.
2. Üye üç şeyden biridir: **metin birimi** (kelime, âyet, kısım, sûre, Mushaf), **bağ** (üst mertebe) veya **metin dışı** olgu. Dördüncüsü bulunamaz; çünkü bağlanan şey ya metindir, ya bağdır, ya ikisi de değildir. "Metin dışı" bilerek açık sınıftır: yeni nevi çıksa bile dışlanmaz.
3. Üye sayısı 1, 2 veya ≥ 3'tür (sayı hasrı).
4. Kapalı bir **cins listesi** (sebep, karşıtlık, …) yoktur. Cins etiketi, rol imzasından türeyen **açık sözlüktür**: her etiket kendi rol imzasıyla tanımlanır ve daha önce tanımlılardan kurulamadığı gösterilerek eklenir. Etiket eklenmesi usulü bozmaz; bozulan şey **eksenlerin tamlığıdır** (bkz. § 4 tamlık denetimi).

Sınır (zayıf nokta): § 2/2'deki "üç tür" hasrı bir tanım hasrıdır; derecelendirilmiş (ne kadar) bağlar için isteğe bağlı `ölçü` alanı konmuştur, fakat ölçüsü olmayan bir bağın ölçü almadan kaydı mümkündür. Bu hasra itiraz gelirse eksen genişletilir.

## 3. Kümenin hududu: kabul şartı

Hudut **nevi** ile değil **şart** ile çizilir. Her aday bağ şu üç şartla kabul edilir; üçünü de sağlayan, nevi ne olursa olsun girer.

- **İz:** bağın dayandığı şey gösterilir (lafız · yapı · mana · dış). İz yoksa kayıt açılmaz.
- **Yıkan şart:** "şu olsaydı bu bağ düşerdi" cümlesi yazılır. Yazılamayan bağ sınanamaz; kabul edilmez.
- **Katiyet derecesi:** `iz-doğrulandı` (metinden okunur) · `hipotez` · `rivayet-yoklanmadı` (kaynağı sonra bakılacak). Zayıf bağ **silinmez**, derecesiyle kalır. "Tematik komşuluk" de böyle bir kayıttır; derecesi hipotezdir ve `degistirilebilir: true` taşır.

## 4. Eksenler ve tamlık denetimi

Her bağ şu eksenlerde **hesaplanarak** sınıflanır (elle etiket yok):

| Eksen | Değerler | Hasrın dayanağı |
|---|---|---|
| E1 üye sayısı | 1 · 2 · ≥3 | sayı |
| E2 simetri | rol değişince iddia değişmez / değişir | iki ihtimal; üyelerin rol kümesi eşit mi diye hesaplanır |
| E3 taşıyıcı | lafız · yapı · mana · dış (küme; birden çok olabilir) | Bir metin birimi hakkında söylenebilecek şey: **biçimi** (kök, ses, kalıp, fâsıla) = lafız, **dizilişi** (sıra, simetri, tekrar, boşluk) = yapı, **içeriği** = mana; bunların dışı metin dışıdır |
| E4 mertebe | birim–birim · birim–bütün · bağ–bağ · birim–dış | üye türü kombinasyonu |

Tamlık denetimi: `denetle.py` her kaydın her eksende bir değer aldığını ve cins etiketinin tanımlı olduğunu sayar. **Yerleşmeyen bağ** çıkarsa suç bağda değil eksendedir: eksen eklenir, bağ atılmaz. Yerleşmeyen sayısı raporda yazılır (`F 3-B 26`).

## 5. Testler (sınama aracı; ispat aracı değil)

Her test sonucu `geçti · kaldı · uygulanmadı` yazılır. Uygulanmayan test "geçti" sayılmaz.

| Test | Soru | Not |
|---|---|---|
| T1 çıkarma | Üye çıkarılınca bağın taşıdığı hüküm eksilir mi? | Hükme dayanır; makine ölçmez |
| T2 ikame | Aynı işi başka birim görür mü? | **Yalnız çürütür.** "Bilinmiyor" delili "zaruri" iddiasını kuramaz (cehalete başvuru). Bu yüzden `DUZELTILMIS_ZINCIR.md`deki A ölçüsünün 2. şartı hüküm kurmaz; A satırları "metin bağı var" olarak kalır, "zaruri" sıfatı düşer (nakz, 3-I 179) |
| T3 iz | İddia, metinden doğrulanan bir lafız/yapı olgusu gösteriyor mu? | Makine ile sınanabilir kısmıdır |
| T4 beklenti | Bu noktada okuyucu ne bekler; metin karşılıyor, erteliyor, bozuyor mu? | Hipotezdir |
| T5 kademe | Bağ, üst kademenin (kısım, sûre gayesi) kanıtı mı? | Kısım adları **argümandaki rol** olarak yazılır |
| T6 kör geri getirme | Kayıttaki cümleyle, sonraki birimi görmeden, sonraki birimin özellikleri tahmin edilebiliyor mu? | Protokol: tahmin eden metni görmez; sonuç sayıyla yazılır; bu oturumda **koşturulmadı** |
| T7 karşı-bağ avı | Aynı lafız/kalıp başka yerlerde aynı işi görüyor mu? Görüyorsa bağ yerel değil, kalıptır | Külliyat taraması gerekir; yoklanmadı |
| T8 yıkan şart | § 3'teki yıkan şart yazılı ve sınanabilir mi? | Kabul şartı |

## 6. Yapıştırılan metnin tenkidi (yoklandı)

Metin padişahın sözü değildir (3-I 33-B). Yoklama sonucu:

- Doğru bulunanlar: T2'nin yalnız çürütücü olduğu tespiti; "ilişkili/benzer" cümlelerinin boşluğu; münâsebetin geriye ve ileriye bakması; kayıtta cümle-i külliyenin gerekliliği (mantıken sağlam, kaynağı gösterilmedi).
- Hatalı bulunanlar: (a) Şems 91'in nefs yemininden sonraki hükmü "fealhaza" diye geçer; metindeki Arapça 91:8 "fe-elhemehâ fucûrahâ ve takvâhâ" ve 91:9 "kad efleha men zekkâhâ"dır. (b) Fâtiha 1:5 için "na'büdü ile takdim" yazar; takdim (öne alma) **"iyyâke"** lafzındadır, "na'büdü" fiildir. (c) "iyyâke tekildir, herkes kendi hesabıyla yüz yüzedir" der; oysa aynı âyette fiiller "na'büdü / nesta'în" çoğuldur, yani tek başına tekillik hükmü kurmaz.
- Yoklanamayan atıflar: Zerkânî *Menâhil*, İmâdüddin İsmail *Minâhicü'd-derâsât* ve bunlara yüklenen görüşler. Yoklanan: Bikâî'nin *Nazmü'd-dürer*i ve münâsebet tanımı Zerkeşî'ye atfı (TDV İslâm Ansiklopedisi'nde geçer: <https://islamansiklopedisi.org.tr/munasebatul-ayat-ves-suver>, <https://islamansiklopedisi.org.tr/nazmud-durer>). İzzeddin b. Abdisselâm'ın münâsebeti şart saymadığı yolundaki hafızadaki görüş **yoklanamadı**.
- Fâtiha 1:6'daki "ihdinâ" ile 2:2'deki "hüden" aynı kökten (h-d-y) gelir; bu **lafız izi**dir. "Duanın cevabı" okuması ise hipotezdir (T7 yapılmadı).

## 7. Açık sualler

1. Kısım adlarının "argümandaki rol" olarak yazılması mevcut `sure.md` kısımlarını (K001-01..03) değiştirir; Fâtiha'da 1:5 `sure.md`de 5-7 kısmındadır, burada hem hitap hem talep kenarındadır. Hangisi esas olacak?
2. İlk toplu uygulama için hangi sûreler? Fâtiha yedi âyetlik olduğundan bağ–bağ kaydı yalnız bir tanedir (F08) ve zayıftır; nakarat (madde 4) ve metin dışı üye (madde 7) Fâtiha'da hiç kayıt almadı, Rahmân ve nüzûl sebepli bir sûre gerekir.
