# Modern söylem kuramlarından çıkan matematik

Kayıt: CLAUDE.md § 3-I 324 (önce modernler, sonra klasikler matematik modele çevrilir). Her satırın **durum**u: *birinci el* (bu oturumda asıl metinde görüldü), *ikinci el* (özet/arama), *hafıza* (yoklanmadı). Klasik kitap okunmadı (3-I 230).

## 1. Grosz–Sidner niyet yapısı (birinci el)

| Nesne | Tanım | Bizdeki karşılığı |
|---|---|---|
| Söylem bölümü amacı (DSP) | Bölümü doğuran niyet; Intend S (Believe/Know-how-to/Intend H p) biçimindedir | ihtiyaç (`I…`) |
| DOM (hâkimiyet) | A'yı tatmin etmek B'yi tatmin etmeye katkıdır → B, A'ya hâkim | `ust` (ters yön) |
| SP (tatmin önceliği) | A, B'den önce tatmin edilmeli | `onkosul` |
| Türetilmiş niyet | Açık söylenmemiş ama niyet yapısından çıkan | dolaylı gaye (83. âyet örneği) |
| Sınır | Bölüm sınırı niyet yapısından çıkarılır | kısım hududu (ağaç bitince, 3-I 320) |

Fark: GS'de Believe / Know-how-to / Intend var; **his, statü, celb, def** yok. Bunlar bizim genişletmemizdir ve ayrı hipotez olarak taşınır (3-I 319).

## 2. RSA (birinci el: denklemler)

L0(s|u) ∝ [[u]](s)·P(s); S1(u|s) ∝ exp(α(log L0(s|u) − C(u))); L1(s|u) ∝ P(s)·S1(u|s).

Eşleme (yalnız modelleme; Allah'ın kelâmı hakkında iddia değildir): s = muhatabın ihtiyacı/hâli, u = söz, C(u) = söz maliyeti ↔ icâz/itnâb (`miktar`). Kullanım yönü L1: metinden ihtiyacı çıkarmak. Ön bilgi P(s) ve anlam fonksiyonu elimizde yok; bu yüzden **ertelendi**, ölçü olarak kodlanmadı.

## 3. Kodlanan ölçü: sağ sınır (SDRT'den; ikinci el)

Kural: yeni birim ancak son birimin cephesine (ihtiyaç ve ataları) bağlanabilir; kapanmış alt ağaca dönüş ihlaldir. `karar_denetle.py` → `sag_sinir_ihlali`.

| Veri | Sonuç |
|---|---|
| Fâtiha | 0 ihlal |
| 83. âyet örneği | 1 ihlal: `KW3:W3->W2` |
| Negatif sınama (Fâtiha'da I6 → I1d) | 0 → 1, reddedildi |

Dürüst bulgu: 83 örneğinde DOM zinciri nedensel (W4→W3→W2→W1→W0), metin sırası ise W2, W6, W3, W4. İhlal bir veri hatası olmayabilir; sebep-sonuç sırası ile söyleniş sırası farkıdır. Veri değiştirilmedi.

## 4. Ötekiler (ikinci el / hafıza)

| Kuram | Nesne | Bizdeki yeri | Durum |
|---|---|---|---|
| RST | çekirdek–uydu ilişkisi, açık ilişki sözlüğü | münâsebet türü; kapalı liste riski (3-I 317) | ikinci el |
| UID | birim başına bilgi düzgünlüğü | icâz/itnâb; dil modeli gerekir | ikinci el, ertelendi |
| Centering | konu sürekliliği geçişleri | `konu` yönü; Rab→Rahmân→Mâlik sırasını açıklamaz (SP boş, 12 geçerli sıra) | ikinci el |
| Söz edimleri | haber/inşâ | sonraki devir | ikinci el |

## 5. Klasikleri çevirme planı (okuma izni gelince)

| Klasik | Matematik karşılığı adayı |
|---|---|
| Münâsebet türleri | bağlanma türü + sağ sınır |
| Makâsıd (zarûriyyât/hâciyyât/tahsîniyyât) | ihtiyaçlara öncelik ağırlığı |
| Usûl-i tefsîr bağlamı (siyâk, sebeb-i nüzûl) | P(s) ön bilgisi |
| Meânî (icâz/itnâb) | alternatif söz kümesi U ve maliyet C |
| Nazm | yerel yapı |

Hepsi aday; okunmadan hüküm değildir.
