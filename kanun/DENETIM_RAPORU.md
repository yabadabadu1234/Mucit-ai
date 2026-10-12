# DENETİM RAPORU (F 3-I 292; güncel: F 3-I 299, 300, 302; 12/10/2026)

Kaynaklar: `MALI_MODEL/genc3.py` (genç modeli, `genc3_out.txt`), `model.py` (mali model, `DUYARLILIK_TABLOLARI.md`), `notr_kural_sim_out.txt`, `esitlik_sim_out.txt`, `denetim_mali_out.txt`, `bolme_kazanci_out.txt`, `imkansizlik_sim_out.txt`. Tasarım: düz %13,5 (kanunda üst sınır %27), eşit giriş, prim isteğe bağlı, ücretli çalışan rejim dışında, Madde AD (doğrulanmamış B2B'de nötr kural). Girdilerin çoğu ölçülmemiş varsayımdır.

## 1. Gencin kazandığı kadar mesul olmasına mani kaldı mı?
Gün-0 yük sıfırdır (tescil, hesap, adres ücretsiz; sabit prim ve muhasebeci yok). Kalan manilar: (a) tavan (792.720 TL/yıl) aşılınca genel hükümler; sabit prim (141.699 TL/yıl) ve muhasebe aşıldığı aydan sonra geri gelir ve tavan hasılatının yaklaşık %21'ine denk gelir; (b) doğrulanmamış B2B hizmette satıcı %13,5 yerine alıcı oranını (%25) öder (gelire orantılı, sabit değil); (c) stoklu ticaret negatif listede; (d) GSS primi (yaklaşık 1.982 TL/ay, hak sahibi olmayan 18+ için) sabit yüktür ve ölçülmemiştir; (e) cihaz ve internet ölçülmedi; (f) TTK ve diğer kanunlar değişmeden sermayesiz limited ve anonim şirket kurulamaz.
Genç modeli (8 tohum, 72. ay): geçim eşiğini sürdürme 0,805 (mevcut kayıtlı 0,586, kayıt dışı 0,555, tarafsız 0,890); şirketin açık ve nakitte kalması 0,883 (0,621 / 0,677 / 0,925); kalıcı üst segment 0,312 (0,175 / 0,127 / 0,536); yıkım yaşayan 0,483 (0,907 / 0,730 / 0,340). Teklif mevcut kayıtlı düzenden her ölçüde iyidir; tarafsız ölçüye (kanunsuz) göre hâlâ geridedir. Oran %27 olursa geçim 0,731'e iner (hâlâ mevcut kayıtlıdan iyi).

## 2. Devletin zaafiyette olduğu saha
Tek kapı entegrasyonu (GİB, SGK, sicil, oda) ve portal kapasitesi; denetim kapasitesi; halen kayıtlı olanların topluca geçişi (yutulma) ve primi sürdürenlerin payı; doğrulayıcı tanımı ve taklit olasılığı ölçülmedi; kimlik kiralama.

## 3. Sahtekârın engellenemediği / devletin malen zararda olduğu saha
Sıfır: doğrulanmamış B2B'de sahte fatura (nötr kural, taramada azamî kazanç 0,000; `notr_kural_sim_out.txt`).
Sıfır değil: (i) doğrulanmış kanalda doğrulayıcı taklidi: p=0,05 için birim başına +0,0057; (ii) **tavan üstü bölme:** H=1,5 milyon TL hasılat 2 kimliğe bölünürse kazanç 189.199 TL (hasılatın %12,6'sı); H=6 milyon TL, 8 kimlik: 684.199 TL (%11,4) (`bolme_kazanci_out.txt`); kimlik işbirliği gerekir, yabancıyı Madde V ve Y yıkar, aile ve örgütte kalır; (iii) kimlik kiralama; (iv) sahte seri numarası ≤ 5.000 TL, 36 ayda bir.
Devletin malen zararda olduğu hâl: 4. yıl net (%13,5, prim hiç sürmezse): **Kötümser −2,01**, Orta +1,32, İyimser +23,72 milyar TL. Kötümser; oran %25,5'e çıkarsa veya halen kayıtlıların %59'u isteğe bağlı primi sürdürürse sıfırı geçer. Halen kayıtlı olup geçenlerin payı Orta'da %18'i aşarsa net etki negatiftir; hepsi geçse üç senaryo da negatiftir (Orta −35,08).

## 4. Mevcut kanuna göre
İyileşme: genç başına devlet payı ve geçim/şirket oranları yukarıdadır; gün-0 yük 0 (bugün: kayıt, oda, muhasebe, sabit prim 141.699 TL/yıl). Kötüleşen: halen kayıtlı olup geçenlerde devlet geliri (yutulma); doğrulanmamış B2B satıcının vergisi (%13,5 yerine %25); sosyal güvence (GSS ve emeklilik hakkı) gönüllü hâle gelir, hakkın birikmesi gönüllü ödemeye bağlıdır (`EMEKLILIK_HESABI.md`); muhasebeci geliri kaybı yılda 0,36–0,66 milyar TL (padişah: telafi yok, F 3-I 294); oda geliri.

## 5. Eşitlik ve muhasebeci (F 3-I 293, 294)
Eski ve yeni aynı şartla girer (Madde 1 (p)); sabit prim yoktur. Yıl-4 net (π=0,8): Kötümser −1,99 (s=0,30), Orta +1,35 (s=0,15), İyimser +23,75 (s=0,05) (`esitlik_sim_out.txt`); s=0,5'te Orta −13,64. Muhasebeciye devlet iş icat etmez (F 3-I 294): Madde AG gelir ikamesi olarak sunulamaz; geçiş ve telafi yoktur.

## 6. Madde AG'nin sınırı (padişah sorusu, 14/10/2026)
(a) Kanunda hizmet gerçekliğini onaylama yetkisi taşıyan meslek mensubu bulunamadı: 3568 m.12 YMM tasdikini mali tablo ve beyannamenin mevzuata uygunluğuna bağlar (ikincil kaynak). (b) Yazılım, tasarım, tercüme gibi işlerin fiilen yapılıp yapılmadığı muhasebe bilgisiyle anlaşılmaz; Madde AG'nin gelir kaybını karşılama iddiası geçersizdir (F 3-I 294).
