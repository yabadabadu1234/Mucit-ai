# Müştak veri tabanları (F 3-I 365)

| dosya | kaynak | ne taşır | lisans |
| :-- | :-- | :-- | :-- |
| `ar_kok.jsonl` | kaikki.org İngilizce Vikisözlük'ün Arapça dökümü (`ar_ayikla.py` ile süzüldü; 233 417 maddeden kökü belli 12 505'i) | kök · harekeli madde · tür · fiil bâbı · İngilizce tanım · etiket (geçişli, ettirgen) · masdar listesi | CC BY-SA |
| `tr_vikisozluk.json` | Türkçe Vikisözlük dökümü (`tr_vikisozluk_ayikla.py` ile süzüldü) | `ar2tr`: Arapça fiil → Türkçe fiil (2656) · `en2tr`: İngilizce madde → Türkçe karşılık (21 729) | CC BY-SA |

Ham dökümler depoya alınmaz (3,4 GB ve 0,9 GB); süzme betikleri aynen koşturulursa aynı dosyalar çıkar.

| (dosya yok) | kaikki.org İngilizce Vikisözlük'ün Arapça dökümü, 233 417 madde: https://kaikki.org/dictionary/Arabic/kaikki.org-dictionary-Arabic.jsonl | `kelime_kaydi.py [ham döküm]` doğrudan okur; ham aslın tek nüshası depoda: `kaynak/lugat/ham/kaikki_arabic.jsonl.xz` (31,9 MB, F 3-I 377) (`kaikki_suz.py` yalnız madde süzme kütüphanesi); ara dosya açılmaz. Maddeler `kokler/<kök>.json` içinde `sozlukler.kaikki_vikisozluk`, köksüzler `kuranda_yok/kelimeler/<kelime>.json` | CC BY-SA 4.0 |

**Atıf (CC BY-SA):** Veri, Vikisözlük (en.wiktionary.org) katkıcılarına aittir; Tatu Ylonen'in wiktextract aracıyla çıkarılan kaikki.org dökümünden alınmıştır. Aynı lisansla (CC BY-SA 4.0) paylaşılır; yapılan değişiklik: alan süzme ve kök dosyalarına dağıtma.
`ar_kok.jsonl` yalnız köklü maddelerin eski ve dar süzmesidir; müştak tanıklığı (`wikt.py`) onu okur, kök dosyalarındaki `kaikki_vikisozluk` alanı onun yerini tutar.
