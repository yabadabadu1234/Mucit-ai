# Kök tercüme vazifesi

Dosyalar: `kuran_hikmetleri/kelime_kaydi/kuranda_var/kokler/<kök>.json` (1661 kök).

Her kök dosyasında `sozlukler` altındaki Arapça ve İngilizce metinler (mekayis, cebel_mihveri, arabic_ontology tanim ve misal, etymarab, kaikki_vikisozluk, osmanlica_lugatler Arapça kısımları, kok_anlamlari vb.) Türkçeye tercüme edilir ve `sozlukler.tercume` altına yazılır. `sozlukler.tercume` alanı olmayan her dosya sıradadır.

Örnek biçim: `خوف.json`, `ءبب.json`, `ءخر.json` (daha önce tercüme edilmiş dosyalar). Aynı yapıyı, aynı anahtarları ve aynı sırayı koru; eski alanlara dokunma, hiçbir şey silme.

Üslûp: Osmanlıca, Mehmet Âkif ciddiyetinde; kurulu, yerli yerinde, çeviri kokmayan cümleler (müteşebbis gibi uydurma kelime, "nice" gibi eklemeler, kırık cümle yok). Anlamı eksiltme. Boş `{}` bırakma; kaynakta metin yoksa o girdi atlanır.

Sıra: alfabetik; her 20 dosyada bir `git commit`. Hepsi bitene kadar durma. Kısa bir model (High değil) yeterli.
