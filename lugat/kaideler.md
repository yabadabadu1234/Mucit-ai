# Karşılık Terkibinin Kaideleri

Bu kaideler, lügatin her maddesine Osmanlıca karşılık bulunurken ve yeni karşılık terkip edilirken uyulacak esaslardır.

## Birinci kaide: Üç mühür

Her karşılık şu üç mühürden yalnız biriyle işaretlenir:

- **kadîm**: Karşılığın aynen kendisi, İbn-i Sînâ'nın el-Kânûn fi't-Tıbb'ında, Şerafeddin Sabuncuoğlu'nun Cerrâhiyyetü'l-Hâniyye'sinde yahut başka bir Osmanlı tıp kitabında geçtiği bilinen karşılıktır. Bu mühürlü satırın "delil" sütunu boş bırakılamaz. Delilde eser, mümkünse bab yahut fasıl, ve kullanıldığı mânâ yazılır.
- **teklif**: Kaidesine göre yeni terkip edilen karşılıktır. Terkibin parçaları kadîm olsa bile, bütün terkip o şekliyle bir kaynakta görülmemişse mühür "teklif"tir; kadîm parçalar "izah" sütununda gösterilir.
- **şüpheli**: Emin olunmayan karşılıktır. Bir kelimenin o mânâda kullanıldığı zannedilir fakat doğrulanmamışsa, yahut mefhumun hududu tam seçilemiyorsa bu mühür vurulur ve sebebi izahta yazılır.

Bir mühür, delil bulundukça değişebilir. Fakat eski satır silinmez; yeni satır eklenir ve izahında eskisine işaret edilir. Telif dosyasında bir maddenin son satırı geçerli karşılık sayılır, öncekiler tarih olarak durur.

## İkinci kaide: Yarı Latince karşılık kabul edilmez

"Kardiyomiyopati", "gastrit", "nöropati" gibi Latince yahut Yunanca kökü Türkçe harfle yazmaktan ibaret olan karşılık, karşılık sayılmaz. Doğrulama betiği bu türlü parçaları arar ve uyarı verir. İstisna: Osmanlıcaya asırlar önce girmiş ve halkın dilinde yerleşmiş kelimeler (mesela "kolera", "efrenciyye" gibi) delil gösterilerek kullanılabilir; bunlar da izahta zikredilir.

## Üçüncü kaide: Mefhumun mânâsı esastır

Yeni terkipte Latince kelimenin harfi değil, mefhumun ne olduğu esas alınır. Önce mefhumun tarifi okunur (tasnif kaydındaki tarif sütunu), sonra o mânâyı veren Arapça, Farsça yahut Türkçe kökler aranır. Mesela "neoplasm" kelimesinin harfiyen tercümesi "yeni teşekkül"dür; fakat mefhum "yeni hâsıl olmuş ur" olduğu için "evrâm-ı müstahdese" terkip edilir.

## Dördüncü kaide: Terkip usulü

1. Önce kadîm kelime aranır. el-Kânûn'un ıstılahları (mesela "maraz", "araz", "alâmet", "veram", "asab", "a'zâ", "ahlât", "mizâc") birinci derecede kaynaktır.
2. Kadîm kelime yoksa Osmanlı tıbbının son devrinde, Mekteb-i Tıbbiye kitaplarında kullanılan ıstılah aranır.
3. İkisi de yoksa Arapça yahut Farsça terkip kaidelerine göre, izafet ve sıfat tamlamasıyla yeni terkip yapılır. Sıfat, mevsufuna müennes ve müzekker cihetinden uyar ("emrâz-ı cildiyye", "cihâz-ı asabî").
4. Bir terkip, aynı mefhum ailesinde aynı kalıpla kurulur; mesela bir cihazın hastalıkları daima "emrâz-ı cihâz-ı ..." kalıbıyla yazılır.
5. Uzun Latince ve İngilizce adlarda, madde adındaki her kayıt (mesela "başka yerde tasnif edilmemiş", "tabakası", "nev'i") karşılıkta da aynen bulunur; hiçbir kayıt düşürülmez.

## Beşinci kaide: Kısaltma yoktur

Karşılıklarda ve izahlarda kısaltma kullanılmaz.

## Karşılık dosyasının şekli

`karsiliklar/` klasöründeki her dosya sekmeyle ayrılmış metindir. Sütunlar şunlardır:

| sütun | mânâsı |
|---|---|
| kimlik | Maddenin kimliği. Şu şekillerden biri: `MeSH:<tavsif numarası>`, `MeSH-agac:<ağaç numarası>`, `MeSH-kita:<harf>`, `ICD11:<unsur kimliği>`, `ICD11-kod:<kod>`, `ICD11-bab:<bab numarası>`, `ICD11-ad:<İngilizce ad>` |
| ingilizce | Maddenin İngilizce adı; yoklama içindir. Maddedeki adla uyuşmazsa `telif/ingilizce_uyusmazligi.tsv` dosyasına yazılır. |
| osmanlica | Osmanlıca karşılık |
| muhur | kadîm, teklif yahut şüpheli |
| delil | Kadîm karşılığın kaynağı |
| izah | Terkibin sebebi, kadîm parçaları, şüphenin sebebi |
