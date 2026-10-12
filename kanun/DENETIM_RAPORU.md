# DENETİM RAPORU (F 3-I 292; A şıkkı kabul sonrası; 12/10/2026)

Kaynaklar: `MALI_MODEL/denetim_sim.py` (genç, 3000 kişi, 72 ay), `denetim_mali.py` (yıl-4 net), `bolme_kazanci_out.txt`, `imkansizlik_sim.py`. Bütün girdiler eski dosyalardaki varsayımlardır (ölçülmemiş girdi: medyan hasılat, B2B payı, taklit olasılığı).

## 1. Gencin kazandığı kadar mesul olmasına mani
Kalan: (a) tavan (792 720 TL/yıl) aşılınca genel hükümler, yani sabit yük geri döner (ani uçurum); (b) doğrulanmamış B2B hizmette satıcı %10,5 yerine alıcı oranını öder (gelire orantılı, sabit değil); (c) stoklu ticaret: kendi namına mal alım satımı negatif listede, vadeli alım tavanı 6 brüt asgari; (d) GSS primi yoklanmadı; (e) riskli ruhsat sınıfı, işçi çalıştırma (SGK, İSG), 16 yaş altı ve yabancı uyruk; (f) TTK ve vergi kanunlarının değişmesi gerekir.
Padişahın F 258 ölçütü (kalıcı üst segment) Orta: tarafsız 0,140; mevcut kayıtlı 0,007; teklif düz %10,5 0,081; A kuralı %35: 0,067, %70: 0,051. Yıkım: 0,541 / 0,994 / 0,592 / 0,636 / 0,683. Kanun, tarafsız ölçüye göre hâlâ kayıp bırakıyor (0,06 ila 0,09); iflasın büyük kısmı kanunsuz dünyada da var (0,541).

## 2. Devletin zaafiyeti
Doğrulanmış kanal için bağımsız doğrulayıcı tanımı ve taklit olasılığı ölçülmedi; tek kapı entegrasyonu (GİB, SGK, sicil, oda) ve denetim kapasitesi; yeni ve eski mükellef arasındaki eşitlik itirazı; yutulma ve prim sürekliliğinin hukuken tutması.

## 3. Sahtekâr ve devletin malen zararı
Sıfır: doğrulanmamış B2B sahte fatura (taramada azamî kazanç 0,000).
Sıfır değil: (i) doğrulanmış kanalda doğrulayıcı taklidi: p kadar (p=0,05 için +0,0073 birim); (ii) tavan üstü bölme: `bolme_kazanci_out.txt`; kimlik işbirliği gerekir, yabancıyı Madde V ve Y yıkar, aile ve örgütte kalır; (iii) kimlik kiralama; (iv) sahte seri no ≤ 5 000 TL, 36 ayda bir.
Devletin zararda olduğu hâl: yıl-4 net, Kötümser, doğrulanmamış B2B %35, prim sürekliliği %50: −0,25 mlr TL (diğer bütün hücrelerde pozitif; "herkes geçse ve prim sürekliliği %50" bütün senaryolarda negatif).

## 4. Mevcut kanuna göre
İyileşme (Orta): kalıcı üst 0,007 → 0,051–0,081; yıkım 0,994 → 0,592–0,683; açlık ayı 33,4 → 23,9–26,8; gün-0 yük 0 (bugün: kayıt, oda, muhasebe, sabit prim). Kötüleşen: halen kayıtlı olup geçenlerde devlet payı (genç başı PV 274 731 → 140 965–182 749); doğrulanmamış B2B satıcının vergisi teklifin ilk vaadine göre; eski ve yeni mükellef prim asimetrisi; sosyal güvence (GSS ve emeklilik hakkı) hesaplanmadı; muhasebeci geliri kaybı yılda 0,36–0,66 mlr TL; oda geliri.

## 5. F 3-I 293: muhasebeciler ve eski–yeni eşitliği (13/10/2026)
**Muhasebeci (Madde AG, Hizmet Doğrulama Raporu).** Kaybı karşılayan ücret oranı (Orta): doğrulanmamış B2B payı %35 için %3,58, %70 için %1,79; Kötümser %8,40 / %4,20; İyimser %1,05 / %0,53 (`esitlik_sim_out.txt`). Taraflar rapor yaptırınca satıcı %10,5 öder, alıcı tam indirir (14,5 puanlık fark), yani oranlar farkın altındadır: isteyen kazanır, istemeyen Madde AD'de kalır. Kişi başı kayıp (aktif ~59 958 SM/SMMM, ikincil): 6 004 / 10 007 / 11 008 TL/yıl. Devlet ödemez. Riskler: doğrulayıcı taklidi (p), kapasite (rapor sayısı ölçülmedi), ücret tarifesinin davranış etkisi.
**Eşitlik (Madde 1 (p) yeniden yazıldı).** Eski ve yeni aynı şartla girer, sabit prim yok. Yıl-4 net (π=0,8): Orta A%35 +1,78, A%70 +5,12; İyimser +26,3 / +38,9; **Kötümser −1,95 / −1,10** (s=0,30 benim varsayımım). Geçiş payı büyürse Orta: s=0,5'te −13,2 / −9,9. Güvenli sınır π*: gerçekte tahsil edilen sabit prim payı; veri yoktur (SGK birincil veri bulunamadı).
