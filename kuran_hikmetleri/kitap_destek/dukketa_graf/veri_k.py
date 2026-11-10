def W(ad,mana,kalip,incelik,komsu,tr,dayanak):
    return {'etiket':ad,'ok':False,'ogeler':[('Mana',mana),('Geçiş',kalip),('İncelik',incelik),('Komşu/zıt',komsu),('Türkçe',tr),('Dayanak',dayanak)]}
K={'baslik':'د ك ك  ·  kökten türeyen bütün kelimeler ve her birinin manası','bolumler':[
{'baslik':'ÇEKİRDEK · bir şey ezilip ÖYLE düzlenir ki eski kabarıklığı kalmaz','bloklar':[
 {'etiket':'Çekirdek','ok':True,'ogeler':[('Mana','Vurup ezmek, kabarığı yerle bir edip düz ve sıkı kılmak'),('İki yüz','Yıkma (hasar) + düzleme (sonuç): iş bir yönde biter, geri dönmez'),('Çoğalması','Ezmek → düz yer → sıkışmış yer → seki/oturak → satış yeri; ezilen insan → zayıflayıp düşen'),('Ayrım','Dakk (dövüp inceltmek) başka köktür; dekk kabarığı alır, dakk parçayı inceltir'),('Dayanak','● Kamus, Vankulu, Luggat: ezmek, düz yer, hasta etmek; ○ iki kökün yakınlığı')]}]},
{'baslik':'FİİLLER · iş olarak','bloklar':[
 W('دَكَّ dekke (mâzî)','Ezip yerle bir etti','Fâil + ezilen şey (geçişli): duvar, dağ, yer, höyük','Tek hamlede bitirir; kısmî kırma değildir','Kasr/kesr: kırar fakat düzlemez; hedm: yıkar fakat ezmez','ezdi, yerle bir etti, dümdüz etti','● Kamus, Vankulu, Luggat'),
 W('يَدُكُّ yedukku (muzâri‘)','Eziyor / ezer','Şimdi veya sürekli iş; tekrar eden darbe','Tekrarla düzlenen yol, kum, set','—','eziyor, çiğneyip sıkıştırıyor','● biçimden; ○ kullanım kaydı yok'),
 W('دُكَّ dukke (meçhul)','Ezildi, yerle bir edildi','Fâil söylenmez: ezilen şey özne olur (yer, dağ)','Failin büyüklüğü sezdirilir: kim olduğunu söylemeyecek kadar kuvvetli','Infa‘ale: kendiliğinden olan ezilme, burada failsiz bırakıldı','ezildi, düzlendi','● Kur’ân biçimi (müsennâ meçhul: iki şey birden)'),
 W('دُكَّ dukke (başka meçhul)','Hastalıktan zayıf düştü','Ezilen kişi: hastalık fâil, insan ezilen','Ezilmiş gibi gücü kesilmek: mecâz','Maraz: hasta etmek (genel); dukke ezilmişlik rengini verir','çöktü, ezildi (hastalıktan)','● Kamus; ○ yaygınlığı'),
 W('اِنْدَكَّ indekke','Kendiliğinden ezilip düzleşti','Fâil yok: şey kendi hâlinde yıkılır (inf‘âl)','Dışarıdan darbenin değil sonucun anlatımı','Infecere: yarılmak; indekke düzlenmek','çöktü, yıkıldı, yerle bir oldu','○ biçim kıyastır, kaynakta okunmadı'),
 W('دَكْدَكَ dekdeke (rubâ‘î)','Sarsıp sarsıp ezmek, yeri titretmek','Fâil + ezilen; tekrarlı ve şiddetli: sancım, sarsıntı, def etme','Dekk’in tekrarı: art arda darbe','Zelzele: yeri titretmek (tekrarlı sallanma); dekdeke ezme de katar','çiğneyip ezmek, sarsmak','● Luggat'),
 W('تَدَكْدَكَ tedekdeke','Darbeyle parçalanıp çöktü','Dekdeke’nin kendiliğinden hâli','Küçük parçalara dökülerek çökmek','Tefettete: ufalanmak, burada tepe ve duvar','çöktü, döküldü','○ biçim kıyastır')
]},
{'baslik':'MASDARLAR · iş adları','bloklar':[
 W('دَكّ dekk (masdar)','Ezip düzleme işi','Hem iş adı hem düz yer adı','Fiilin kendisi isim olur: iş ile sonuç bir','Hedm: yıkma işi; dekk düzlemeyi de içerir','ezme, yıkıp düzleme','● Kamus (masdar: yeri mühre gibi düzeltmek)'),
 W('دَكَّة dekke (merre)','Bir ezilişlik darbe','Sayı belirtir: tek vuruş, tek çarpış','Tek seferde bitmek: “bir daha gerekmez”','Dekdeke: tekrarlı; dekke: bir kerelik','tek ezişte','● Kur’ân biçimi dekketen; ○ başka kullanım'),
 W('دَكّ dekk (tekit masdarı)','İşin şiddetini kuvvetlendirir','Fiilden sonra gelip “tam anlamıyla ezmek” der','Kuvvetle ezme, hafifletmeye yer bırakmaz','—','tam ezip','● Kur’ân biçimi dekken')
]},
{'baslik':'İSİMLER · düz yer, seki, höyük','bloklar':[
 W('دَكّ dekk (isim)','Düz ve sıkı yer, hemvar kumluk','Mekân adı: yürünen, oturulan düzlük','Ezilmiş gibi sıkı olan toprak','Höyük ve çukur zıttır: düzlük bunların arası','düzlük, sıkı toprak','● Kamus (dukûk, dikâk)'),
 W('دَكَّة dekke (isim)','Seki, oturak, yüksekçe düz yer','Eşya adı: üstüne oturulur, mal konur','Hem düz hem yükseltilmiş: ezilen gövdeye eklenen','Kürsî: sandalye; minber: yüksek ve dik; dekke yayvan','seki, sofa, tezgâh','● Luggat; ○ kökleşme yolu'),
 W('دَكَّاء dekkâ’ (müennes sıfat)','Düz, yerle bir olmuş (arz, yer)','Müennes sıfat: “yer” kelimesinin sıfatı','Ahfeş: dekk’in yerin kendisi demek olması','Mestûh: yayılmış; musattah: düzlenmiş','dümdüz','● Vankulu, Ahfeş sözü; ○ medli okuyuş'),
 W('دُكُوك dukûk / دِكَاك dikâk','Düz yerlerin çoğulu','Cem‘-i mükesser: kırık çoğul','Düzlüklerin çokluğu','—','düzlükler','● Kamus'),
 W('مُنْدَكّ mündekk','Düz, dümdüz olmuş','İsm-i fâil: kendiliğinden ezilmiş','Sonuç hâli: yerle bir olmuş görüntü','Mestûh/musattah komşu, mündekk ezilişi sezdirir','düzleşmiş, çökük','● Luggat'),
 W('دَكّ dekk (höyük)','Toprağı doldurulup yükseltilmiş yer, höyük','Hem yok edilen hem biriken: dekk ile doldurmak','Çukur doldurulup kuyu örtülünce kabarık höyük doğar','Tell: höyük; dekk bu sonucun adı','höyük, tümsek','● Kamus (çukuru toprakla doldurmak, kuyuyu örtmek, höyük)'),
 W('مَدْكُوك medkûk','Ezilmiş şey','İsm-i mef‘ûl: ezilen','Acı ve çaresizlik rengi','—','ezik, yıkık','○ biçim kıyastır')
]},
{'baslik':'YAKIN AMA AYRI · karışmasın','bloklar':[
 W('دَقِيق dakîk (د ق ق)','İnce, un, gâmız','Sıfat: kalınlık veya anlam inceliği','Dövüp inceltmek: dakk','Dekîk: tam ve kâmil, ayrı madde','ince, un, narin','● Kamus ayrı yazar'),
 W('دَكِيك dekîk','Tam, kâmil (yevm dekîk: tam gün)','Sıfat: eksiksiz olmak','Ezilmişlikle ilgisi yok','Dakîk ile aynı yazılıp karışır','tam, bütün','● Kamus (ayrı madde)'),
 W('دَكَان dukkân','Satış yeri, tezgâh','Mekân adı','Dekke (seki) → tezgâh → dükkân','Hânût: dükkân, daha eski','dükkân','○ kök bağı kaynakta yok: muarreb de olabilir'),
 W('Türkçe dek','Hile, oyun','Yabancı kelime: Arapçadan Türkçeye','Ezip yıkmak → hokkabazlıkla altüst etmek','Tuzak, düzen','dek, dolap','● Kubbealtı (Ar. dekk ‘hokkabazlık’)')
]},
]}
