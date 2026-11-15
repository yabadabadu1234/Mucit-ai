# ŞERHLİ OSMANLICA TERCÜME USULÜ — `خلق` (tek dosya üzerinde çalışma)

Bu klasör `خلق` kökünün bütün çevrilecek satırlarını (kök anlamı, fiil sapı, kelime biçimleri, müştaklar) taşır. Sen bir ajansın; **dosyalar üzerinde çalışırsın** (Read ve Write/Edit araçlarıyla), sohbetle değil.

## Girdi (okuyacakların)
- `KAYNAKLAR/` : kökün **bütün** Arapça ve İngilizce kaynağı (Cebel, Mekâyîs, Vikisözlük, Arabic Ontology, EtymArab, Osmanlıca lügatler, Zemahşerî hakîkat/mecaz, prototip, WordNet dayanağı). Hüküm ve delil **yalnız buradan** çıkar.
- `bolum_NN_<tür>.md` : çalışma bölümleri. Her bölüm şu biçimdedir:

```
durum: bos | tercume-yapiliyor | tercume-tamam | inceleniyor | inceleme-tamam
bolum: <tür> — <başlık>
tercume_eden: -
inceleyen: -

---

## <satır kimliği>
arapça: <Arapça biçim>
bilgi: <tür, bâb, zaman, kalıp, vezin, ingilizce_tanik …>
duz_tercume: <hazır düz Osmanlıca tercüme; git geçmişindeki en iyi sürüm (OVH Qwen3.5-397B-A17B)>
tercüme:
ilave:
```

`duz_tercume:` alanı **hazır esas metindir**; tercüman onu baştan çevirmez, **üstüne şerh yazar**. Alanı kimse değiştirmez.

## Şerhli tercüme biçimi (`tercüme:` satırı — tercüman yazar)
Tercüman `duz_tercume:` değerini esas alır: doğruysa **aynen** kısa tercüme olarak alır, açıkça yanlışsa (kaynakla çelişen mânâ, uydurma, aynı kalıpta tekrar, Türkçe olmayan ifade) kaynaktan düzeltir ve düzeltmenin sebebini ⟨Neden⟩ zincirinde söyler. Tek satır; önce **kısa Osmanlıca tercüme**, sonra etiketli kısımlar (etiketler AYNEN, sırayla):

`<kısa tercüme> ⟨Ne⟩ … ⟨Nasıl⟩ … ⟨Neden⟩ … ⟨Neden 2⟩ … ⟨Neden 3⟩ … ⟨Esas⟩ … ⟨Niçin⟩ …`

- **⟨Ne⟩** bu biçim/müştak ne demektir, tarif. **⟨Nasıl⟩** kökteki asıl mânâdan bu mânâya (varsa mecâza) nasıl gelindi; vezin, ek, ön ek, zamir mânâyı nasıl doğurdu.
- **⟨Neden⟩** bu mânâya geldiği neden ve nasıl biliniyor: **KAYNAKLAR'daki hangi madde söylüyor** (kaynağı ve ilgili cümleyi/kelimeyi anarak). İki ayrı mânâ yazdıysan her biri için ayrı ⟨Neden⟩.
- **Nedene tekrar neden sor:** her sebebin sebebi **⟨Neden 2⟩, ⟨Neden 3⟩ …**; zincir daha geriye gidilemeyen ilk kabul edilen esâsa (kök mânâsı, lügatin kendisi, Arap kullanımı, sarf kaidesi) varınca **⟨Esas⟩** ile biter.
- **⟨Niçin⟩** bu mânâ/kalıp/ek ne gaye ile var, ne işe yarar.
- Dosyada dayanağı olmayan hüküm **⟨Çıkarım⟩** etiketiyle ve çıkarım olduğu söylenerek yazılır. **Kitap, müellif, âyet adı uydurma yasak.**
- Her kısım yalnız kendi sualinin cevabını taşır (sonradan otomatik derlenecek).

## Tercüme kuralları
1. Dil Osmanlı Türkçesi, Latin harfli; Ömer Seyfettin ve Mehmed Âkif nesri; yerleşik Arapça-Fârisî asıllı kelimeler; **cevap Türkçe ifade olsun**, Arapça okunuş (naḍada gibi), bilimsel işaret (ḥ, ʿ), uydurma Arapça kalıp yazma.
2. **AYIRT ET:** aynı kalıp adı altındaki satırlar farklı vezinlerdir (fa'l, fi'l, fu'l, fa'al…). Hiçbirinin **kısa tercümesi** aynı kalıptaki bir başkasınınkiyle aynı olamaz; vezinin kendine has inceliği (hâl, mübalağa, tekrar, mef'ûl mânâlı masdar, isim-i hey'et, hacim, âlet, mekân, tasğîr, çokluk…) tercümenin içine tabiî yedirilir.
3. **ÇOK MÂNÂ:** bir biçim gerçekten birden çok farklı mânâya geliyorsa bütün mânâlar ` / ` ile ayrılır; eş anlamlı iki kelime ` / ` ile ayrılmaz.
4. Her mânâ o satırın Arapça biçiminden, vezninden ve kaynaklardan çıkmalı; komşu satırın mânâsını doldurma amacıyla taşıma.
5. Kök anlamı satırı: başlıkları (Halk: … gibi Latin başlıklar) aynen koru, mânâları Osmanlıca yaz; fiil sapı tek mastar olur.

## İnceleyici görevi (`ilave:` satırı)
- `tercüme:` satırını **değiştirme**. Okuyup **ilave sebepler** ekle: tercümenin ⟨Neden⟩ zincirinde olmayan ek deliller, başka kaynaklardan (KAYNAKLAR'ı taray) teyit veya itiraz, eksik **⟨Neden k⟩** halkaları, atlanmış mânâlar için ⟨Ne⟩/⟨Nasıl⟩/⟨Neden⟩/⟨Esas⟩/⟨Niçin⟩ kısımları.
- Tercümede **hata** varsa (yanlış mânâ, uydurma kaynak, kayma, aynı kalıpta tekrar) `⟨Tashih⟩ doğrusu şudur: … ⟨Neden⟩ …` diye yaz; kaynağı anarak.
- Yeni delil yalnız KAYNAKLAR'dan; alıntıyı kısa ve doğru yaz. Tekrar etme; sebep eklenmeyen satırda `ilave: -` bırak (ama her satır **gerçekten** incelenmiş olsun).

## Durum protokolü (dosyaları çakıştırmamak için KESİN)
- Bir bölüm dosyasını **aynı anda yalnız bir ajan** yazar. Tercüman yalnız `durum: bos` bölümü alır: `tercume-yapiliyor` yap, bitirince `tercume-tamam`; `tercume_eden: tercüman`.
- İnceleyici yalnız **kendine atanmış** ve `durum: tercume-tamam` olan bölümü alır: `inceleniyor` yap (`inceleyen: <adın>`), bitirince `inceleme-tamam`.
- Bölümü **Write ile bütün hâliyle** yaz: başlık satırlarını, `---` ayracını, her satırın `##`, `arapça:`, `bilgi:` alanlarını **aynen koru**; yalnız kendi alanını doldur.
- Hazır bölüm yoksa `until grep -l "durum: tercume-tamam" ...; do sleep 20; done` türü bir bekleme döngüsüyle bekle (en çok 8 dakikalık turlar).
