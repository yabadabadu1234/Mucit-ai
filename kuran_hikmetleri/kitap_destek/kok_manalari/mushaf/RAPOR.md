# Mushaf dizgisi — kural defteri ve imtihan raporu (F 3-I 406-407)

Uygulama: `mushaf_dizgi.py` (kural motoru) · `kok_uzayi_yerlesim.py` (kök uzayına bağlanır; âyet odasının başlığı bu dizgiyle yazılır) · `kok_uzayi_sablon.html` (çizim) · `mushaf_sina.py` (imtihan). Anahtarlar: `anahtar.json`. Ölçüm çıktısı: `OLCUM_CIKTISI.txt`.

## 1. Sabit kural seti (7 kural; yeni icat yok, zar yok)
Metne yalnız satır kırma, girinti, yaslama ve boşluk uygulanır; harf, hareke, kelime sırası ve âyet sonu işareti değişmez (`metin_butunlugu`: bütün Kur'ân'da 12 472/12 472 âyet×genişlik tamam).

| Kural | Tetik (kelimenin imlâsından okunur) | Geometri |
|---|---|---|
| NAKIL | söz fiili (قال، قل، يقول، تقل، قيل … tam çekim listesi) | söz, sağdan 1 kademe girintili blok; sonraki söz fiiline yahut durak işaretine kadar |
| ARA | iki müânaka işareti ۛ ... ۛ arası | sağdan 2 kademe girinti |
| CEVAP | şart edatı (إذا، إن، لو، لولا، كلما، إما، zayıf: ما/من) + sonraki "فَ" cevap bağı | cevap sola yaslı blok |
| ISTISNA | إِلَّا (hemze altı kesre) | sol kenardan 1 kademe girintili blok |
| HITAP | nidâ imlâsı (يَـٰ), "رَبِّ" nidâsı | üstte ve altta geniş boşlukla ayrılmış blok (uçlar kenar sayılır) |
| ZITLIK | بل، لكن | üstünde tek boşluk bulunan blok |
| PARALEL | atıf vâvı (وَ + harf) ve durak işareti sonrası | kelimeler arasında geniş boşluk (satır başında sağdan küçük pay) |

## 2. İmtihan düzeni
Anahtar her küme için, kural kodu o âyetlere koşturulmadan evvel yazıldı ve mühürlendi (git geçmişinde). Kümeler: dev (5 âyet, 16 bağ) · test (8, 36) · test2 (10, 32) · test3 (11, 49) · **test4 (11, 46; dondurulmuş kural defterine karşı tek atış)**. dev, test, test2, test3 kural geliştirirken görüldüğü için **tecrübeye dâhil (kirli)** sayılır; yalnız test4 temizdir.
Maskeleme: bütün kelimeler ve işaretler uzunluğu kadar █; geriye iskelet kalır. Geri okuma: (a) kod defterini **mekanik** uygulayan çözücü; (b) sıfır bağlamlı, araçsız, ayrı ajanlar (iskelet ve defter dışında hiçbir şey verilmedi).
Puan = anahtardaki bağlardan doğru okunan (aynı tür, kelime kümesi IoU ≥ 0,5). V = puan / (kural sayısı × alan); alan = en dar uygun genişlikte sınır kutusu, düz metne oranla.

## 3. Sonuçlar (dürüst)
| Küme | Mekanik çözücü | Alan | V |
|---|---|---|---|
| dev (kirli) | %93,8 (15/16) | ×1,87 | 0,072 |
| test (kirli) | %88,9 (32/36) | ×1,56 | 0,081 |
| test2 (kirli) | %90,6 (29/32) | ×1,45 | 0,089 |
| test3 (kirli) | %87,8 (43/49) | ×1,74 | 0,072 |
| **test4 (temiz)** | **%78,3 (36/46)** | ×1,60 | 0,070 |
| düz metin (taban) | %0 | ×1,00 | 0 |

Sıfır bağlamlı ajan okuması, test4 (temiz): ajan 1 (ilk biçim, kutu sayısı yok) **%26,1**; ajan 2 (kutu sayısı ile) **%63,0** (29/46); ajan 3 (kutu sıra numarası satırı ile) **%63,6** (28/44; ajana pasaj 10'u bu rapor yazarı yanlış yapıştırdığı için 10. pasaj 2 bağla hariç tutuldu). Mekanik çözücü aynı iskelette %77,3 (34/44).

**Durma şartı (≥%85 temiz, sırf iskeletten) SAĞLANMADI.** Kirli kümelerde %88–94, temizde mekanik %78 ve ajan %63. Fark iki yerden gelir: (1) kural, sözlüğünün karşılamadığı bağları görmez (yâsız nidâ, "غير" gibi karşıtlık, hâl vâvı, durak işaretiyle kesilen söz); (2) ajanlar sağdan-sola devam eden çok satırlı kalem sınırlarını yanlış okuyor.

## 4. Kararlılık ve sıfır müdahale
- Aynı âyet grubu, aynı kural setiyle bağımsız iki süreçte: özet sağlaması aynı. Bütün Kur'ân yerleşimi (`yerlesim_onbellek.json`, `kok_uzayi.html`) sıfırdan iki üretimde birebir aynı sağlamayı verdi (zar yok).
- Hâl: `metin_butunlugu` bütün Kur'ân'da sağlandı.

## 5. Kusurlar ve kayıtlar
- test2/4:1 anahtarında HITAP aralığı [0,2] yanlış yazılmıştı; [0,1] olarak tashih edildi (sonuçtan bağımsız; not `anahtar.json`'da).
- Kural defteri test, test2, test3 sonuçlarına bakılarak yedi küçük düzeltmeyle geliştirildi; bu yüzden bu kümeler temiz değildir. test4 donduktan sonra yalnız "رَبِّ" nidâsı ve istisna imzası ayırımı eklendi (test4 âyetlerini etkilemedi).
- Ablasyon (OLCUM_CIKTISI.txt): her kümede en çok bağı PARALEL, sonra NAKIL, CEVAP, HITAP taşır; ARA, ISTISNA ve ZITLIK temiz kümede sıfır bağ taşıdı (örnek azlığı; kaldırma kararı verilmedi).
