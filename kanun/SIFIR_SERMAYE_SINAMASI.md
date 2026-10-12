> **[GÜNCELLEME 12/10/2026, F 3-I 293, 299, 302]** Bu sınama eski tasarım (4/b primi (p) grubunda sürer, %10,5, gerçek gider) üzerinedir. Güncel tasarımda: eşit giriş ve sabit 4/b primi yoktur (§1'in son paragrafı geçersiz; açık kalem 3 kapandı), düz %13,5, ücretli çalışan rejim dışındadır; gün-0 nakit sonucu (0 TL) değişmez. Güncel genç sonuçları: `MALI_MODEL/GENC3_RAPOR.md`. Aşağıdaki §3 simülasyon eski modeldir (tarihî).

# SIFIR SERMAYELİ GENÇ SINAMASI (F 3-I 274)

Ölçüt (padişahın): sıfır sermayeli genç şirket kurmaya kalktığında **kurabilmelidir**; kuramadığı kanun kabul edilmez. Prim (4/b) şimdilik değişmez; şirket kurmanın önşartı değilse kalabilir. Kod: `MALI_MODEL/sifir_sermaye.py`, çıktı `sifir_sermaye_out.txt`, `sonuc_sifir_sermaye.json`; `genc2.py`ye `k0` (başlangıç nakdi/borcu) ve `b_ilk` (ilk müşteri payı) eklendi. Metin: `DEVLETE_SUNULACAK_METIN.md` Madde 1-12 (satır 1-229 okundu; geri kalanı gerekçe ve ekler, okunmadı).

## 1. Kapı testi: gün-0 nakit ihtiyacı
| Yol | Gün-0 nakit | İlk ay toplam | Sıfır sermayeyle kurabilir mi |
| :-- | --: | --: | :-- |
| Şahıs işletmesi, **mevcut kanun** | 8 000 - 12 000 - 20 000 TL (blog tahminleri, ikincil) | 21 808 - 25 808 - 33 808 TL (+ 4/b primi 11 808 + muhasebe 2 000, hasılat olmasa da) | **Hayır** |
| **Mikro mükellef (Teklif)** | **0 TL**: portal tescili, UETS adresi ve banka hesabı ücretsiz (Madde 2 (a), Madde 6), muhasebeci, mali mühür, ruhsat, oda yok (Madde 2); 4/b primi yok (Madde 5 (o)) | 0 TL | **Evet**, aşağıdaki kapılar hariç |
| Limited şirket | nakdi sermaye 50 000 TL, tescilden önce 1/4 = **12 500 TL** + tescil masrafı | -- | **Hayır** (TTK; teklif değiştirmiyor) |
| Anonim şirket | 250 000 TL, 1/4 = **62 500 TL** | -- | **Hayır** |
Kaynak: [asgari sermaye](https://kpmgvergi.com/yayinlar/mali-bultenler/vergi/anonim-ve-limited-sirketlerde-asgari-sermaye-tutarina-uyum-suresi-31-aralik-2026da-sona-eriyor/4518) ve [şahıs şirketi maliyetleri](https://mukellef.co/blog/sahis-sirketi-kurma-maliyeti/) (ikincil; resmî harç ve ücret yoklanmadı).
**Prim kuruluş önşartı mı?** Yeni giren için **hayır**: tescil 4/b sigortalılığı doğurmaz. Tek istisna Madde 1 (p): son 24 ayda bir gün bile 4/b sigortalısı olmuş genç, rejime girer ama **11 808 TL/ay primi sürer** (gelirden bağımsız). Daha önce şahıs işletmesi açıp kapatmış, sıfır sermayeli gençler tam bu gruptadır; onlar için prim gün-0'dan itibaren sabit yüktür. Bu grubun büyüklüğü **ölçülmedi**.

## 2. Teklifin hâlâ kapattığı kapılar (kurabilmeyi engelleyen)
1. **Faaliyet türü (Madde 1 (g)):** yalnız hizmet, emek ve fikrî üretim. **Ticaret (al-sat), komisyon, acentelik, dropshipping kapsam dışı.** Sıfır sermayeli genç ticaret yapmak isterse bu kanunla kuramaz (stok sermayesi de gerekir). Padişahın "şirket" ölçütü ticareti de kapsıyorsa **teklif bu ölçütü geçmez.**
2. **Hukuki şekil:** teklif gerçek kişi (şahıs) rejimidir; limited/anonim şirket sıfır sermayeyle kurulamaz ve teklif TTK'ya dokunmaz. Birlikte iş yapmak için "emek ortaklığı" (Madde 1 (o)) var, tüzel kişilik yok.
3. **Vatandaşlık ve yaş:** yalnız T.C. vatandaşı; 16-17 yaşta yasal temsilcinin elektronik rızası şart (Madde 1 (ö)). Rıza vermeyen veli = kuramaz. Oranı ölçülmedi.
4. **Cihaz ve internet:** teklif cihaz sağlamaz; KDV mahsubu tevkifattan ve sonradan (Madde 3), finansman 12 ay tevkifat sonrası (Madde 8). Cihazsız genç kuramaz. Cihazsız oran **ölçülmedi** (TÜİK: internet kullanan %90,9 (16-74, 2025); bilgisayar/16-24 kırılımı bulunamadı); d oranı kadar kuramayan: d=%10 → %90 kurabilir, %30 → %70.
5. **Sağlık primi:** hak sahipliği olmayan 18+ genç **GSS primini** öder (Madde 5 (o); 60/1-g, %6; ikincil kaynak 2026'da yaklaşık 1 982 TL/ay, doğrulanmadı). Tescil önşartı değildir ama gelirden bağımsız sabit yüktür (F 257 ile çelişir). Gelir testi ilişkisi okunmadı.

## 3. Simülasyon (3 000 genç, 72 ay, ortak şoklar; **bütün davranış parametreleri varsayım**)
Tip payları: okuyor-lise %24, okuyor-üniversite %37, okumuyor lise altı %15, lise %18, lisans+ %6. "Soğuk başlangıç": ilk müşteri yok. Mevcut kanun/kayıtlı: açılış masrafı 12 000 TL borçla başlar. Aç ay = yaşama eşiğinin (net asgari 1/3) altında kalan ay.
| Kalibrasyon, soğuk başlangıç | Rejim | İlk gelir (medyan ay) | 12 ayda gelir | Yıkım (en az bir) | Kalıcı üst |
| :-- | :-- | --: | --: | --: | --: |
| orta | Mevcut kanun, kayıtlı | 10 | %59 | %99 | %0,9 |
| orta | Mevcut kanun, kayıt dışı | 9 | %57 | %86 | %2,0 |
| orta | **Teklif S** | **4** | **%75** | **%55** | **%10,7** |
| orta | Model G2 | 4 | %75 | %59 | %6,7 |
| zor | Teklif S | 6 | %63 | %80 | %2,3 |
| kolay | Teklif S | 3 | %80 | %37 | %28,7 |
Tipe göre (orta, soğuk, Teklif S): okuyor-lise 12 ayda gelir %60, yıkım %70, kalıcı üst %0; okuyor-üniversite %72, %38, %6,7; okumuyor lise altı %88, %73, %11,8; lise %86, %64, %16,2; lisans+ %89, %33, %64,3.
Okunuş: (1) **Kapı** bakımından teklif ölçütü hizmet/emek için geçer: gün-0 nakit sıfır. (2) Kurduktan sonra kanun gence mevcut kanundan açıkça iyi davranır (ilk gelir 4 ay, 12 ayda gelir %75, yıkım %55; mevcut kanunda 10 ay, %59, %99). (3) Yine de **çoğunluk en az bir kez yıkıma düşer** ve kalıcı üst %11'dir; tarafsız ölçüde (kanunsuz) kalıcı üst %14. Kalan açık kanundan değil piyasadan (okuma vakti, diploma kapısı, rekabet) gelir. (4) Okuyan lise öğrencisi hiçbir rejimde kalıcı üste çıkamaz (%0).
Sınırlar: ilk müşteri, talep akışı, beceri, şoklar varsayımdır; model "kurma kararını" ve cihaz sahipliğini içermez; yıkım tanımı sert (borç 6 net asgari/3'ü).

## 4. Muhasebeciler: geçiş ve yeni imkân teklifleri (iş yapıldıktan sonra; çıkarım, ölçülmemiş)
Kayıp: mevcut müşteri s×N×12 000 TL = 0,36 / 0,60 / 0,66 milyar TL/yıl (K/O/İ; `GUNCEL_MODEL.md` §8). Yeni havuz: simülasyonda gençlerin ömründe bir yıl tavanı aşan oranı %4,3 (zor) / %20,1 (orta) / %47,4 (kolay); tavanı aşan gerçek usule geçer ve muhasebeciye ihtiyaç duyar. Orta için kaba hesap: 331 bin × %20,1 × 12 000 = **0,80 milyar TL/yıl** (6 yıl içinde; yıllık değil kümülatif oran, bu yüzden üst tahmin; Kötümser 0,05, İyimser 2,6).
| # | Teklif | Muhasebeciye ne verir | Bedel/risk |
| :-- | :-- | :-- | :-- |
| M1 | **Geçiş:** mevcut kayıtlıların (Madde 1 (p) grubu) rejime girişi yürürlükten 12 ay sonra; mevcut muhasebe sözleşmeleri süre sonunda sona erer, cezai şart yok | 12 ay uyum süresi; kayıp ertelenir | Sıfır sermayeli yeni girenleri **etkilemez**; yutulma da geciktiği için Hazineye lehte |
| M2 | **Tavan köprüsü:** tavanın %70'ine ulaşan mükellefe portal uyarısı ve tarafsız, sıra esaslı meslek mensubu listesi (ücret serbest) | Tavanı aşanlar yeni müşteri (yukarıdaki havuz) | Listeleme kuralı ve rotasyon gerekir; sıra adaleti |
| M3 | **Gönüllü refakat hizmeti:** mikro mükellef isterse SMMM ile gerçek gider seçimi (Madde 1 (a)), itiraz dilekçesi, finansman dosyası (Madde 8 karekodlu belge) için paket | Gönüllü yeni hizmet kalemi | Ücret mükellefe yük olmasın diye zorunlu değil, Hazine bedeli yok |
| M4 | **Alıcı tarafı uyum:** kurumsal alıcının tevkifat ve muhtasar işi (Madde 1 (b)) | Alıcı şirketlerin muhasebesi iş kazanır | Kurumsal alıcı sayısı ölçülmedi |
| M5 | **Hakem Heyeti:** TÜRMOB temsilcisi zaten üye (Madde 10); meslek mensubu görevlendirme havuzu | Kurumsal rol | Yeni bütçe maddesi gerektirebilir |
Sınırlar: ücret 12 000 TL/yıl varsayımdır; tavanı aşma oranı 3 000 kişilik simülasyondan, N'ye kaba tatbik edilmiştir.

## 5. Padişaha açık kalemler
1. "Şirket" ölçütü **ticareti** de kapsıyor mu? Kapsıyorsa teklif bu ölçütü geçmez; ticaret için sıfır stoklu yol (kaydî emanet satış) ayrıca tasarlanır, suistimal riskiyle.
2. "Şirket" tüzel kişiyi (limited/anonim) kapsıyor mu? Sıfır sermayeyle TTK'ya aykırı olmadan kurulamaz; "emek ortaklığı" mı yeterli?
3. Madde 1 (p) grubunda (son 24 ayda 4/b'li) sıfır sermayeli gençler için sabit prim gün-0 yükü: dokunulmasın mı (F 274: prime şimdilik dokunulmaz) yoksa yalnız bu grup için ayrıca konuşulsun mu?
4. GSS primi (yaklaşık 1 982 TL/ay, doğrulanmadı) hak sahibi olmayan gençte sabit yük; gelir testiyle ilişkisi yoklansın mı?
5. Cihaz engeli: ölçülmedi; veri aransın mı?
