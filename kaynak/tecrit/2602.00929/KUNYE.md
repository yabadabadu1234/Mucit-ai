# Künye — arXiv:2602.00929

- Başlık: Learning Abstractions for Hierarchical Planning in Program-Synthesis Agents (TheoryCoder-2)
- Yazarlar: Zergham Ahmed, Kazuki Irie, Joshua B. Tenenbaum, Christopher J. Bates, Samuel J. Gershman — 31 Ocak 2026 (ICML 2026 şablonu)
- Adres: https://arxiv.org/abs/2602.00929 — kod: https://github.com/ZerghamAhmed/TheoryCoder
- Orijinal dil: İngilizce. Kaynak: arXiv LaTeX e-print (`orijinal/main.tex`); OCR yok (F 3-A #25-E).
- Tercüme: Claude (yapay zekâ), `tercume.md`; insan tarafından doğrulanmadı.
- Okuma/tercüme: özet, 7 bölüm, Ek A (istemler) ve Ek B (öğrenilmiş programlar) baştan sona okundu. Gövde tümüyle çevrildi. İstemlerin ham İngilizce metni ve düşük seviyeli dünya modeli Python kodu çevrilmedi (model girdisi/koddur; işlevleri özetlendi, kısa PDDL blokları aynen alındı). Kaynakça çevrilmedi.
- Okuyucu tenkidi: (1) Tablo 1 ile metin bir noktada çelişir (Combined Skills 3'te LLM+π tabloda çözmüş görünür; metin "yalnız TheoryCoder-2" der); ayrıca "Combined Skills 2"de TheoryCoder-2 de başarısızdır. (2) "Tecrit" burada elle yazılmış 3 oyuncak PDDL örneğinin şablonuna göre LLM'nin ürettiği işleç/yüklem takımıdır; öğrenme = LLM'nin bağlam-içi sentezi, bir tecrit ilkesi (sıkıştırma, denklik, çıkarım) yoktur. "Kalite Kâhin'e benzer" iddiası niceliksel değildir (kendileri de söyler); öğrenilen `unlock` ön-koşulu Kâhin'den eksiktir. (3) "0 belirteç" Minihack'te tecritin yeniden kullanımını gösterir ama düşük seviyeli dünya modeli de aynı ortamdan türediği için karşılaştırma ayarlıdır. Mevzumuz açısından kıymetli kısım: tecritin iki seviyeli hâli — işleç (ön-koşul/etki) kütüphanesi + onu somut eyleme temellendiren denetçi; ve bir işlecin birden çok eylemi kapsayabilmesi (`attack` = al-nişan-ateşle).
