# EXCEL DOSYASININ GÖRÜNÜMÜ: MIKRO_MUKELLEF_MALI_MODEL.xlsx (formüllü; sayfalar: Girdiler, Hesap, Sonuc, Senaryolar_Python)

Excel'in 'Sonuc' sayfası bağımsız formül hesaplayıcısıyla (`formulas` kütüphanesi) çalıştırıldı: Orta senaryoda net etki 1,3187 milyar TL; Python modeliyle aynıdır. Aşağıda Girdiler sayfası ve üç senaryonun sonucu yazılıdır.

## Girdiler

| Girdi | Kod | Kötümser | Orta | İyimser | Kaynak/durum |
| :-- | :-- | --: | --: | --: | :-- |
| Brüt asgari ücret (TL/ay) | W | 33030 | 33030 | 33030 | Birden çok kaynakta tutarlı; resmî metin okunmadı |
| Medyan yıllık hasılat (asgari ücret katı) | medyan_W | 4 | 5 | 6 | Varsayım |
| Hasılat dağılımı yayılımı (σ, log-normal) | sigma | 0.9 | 0.9 | 0.9 | Varsayım |
| Katılımcı sayısı (kararlı durum, kişi) | n_toplam | 100000 | 331000 | 1.096e+06 | Kötümser: F 3-I 268; İyimser: F 3-I 269 oranları × ILO 2025 + F 3-I 273 gayrıresmî tanımı (n_veri.py); Orta: geometrik ortalama (Claude) |
| Halen kayıtlı olup rejime geçenlerin payı (s) | s_kayitli | 0.3 | 0.15 | 0.05 | Varsayım; prim isteğe bağlı olduğundan sonucu çok etkiler |
| Gelire bağlı prim: tam prim eşiği (brüt asgari ücret katı) | prim_k | 6 | 6 | 6 | Teklif Madde 5 (o); genç simülasyonunda seçildi (prim_esigi_out2.txt); F 3-I 304 |
| Tam prim tutarı (TL/ay) | prim_ay | 11808.2 | 11808.2 | 11808.2 | 5510 m.81: 33.030 x %35,75 |
| Gelire bağlı primin tahsil oranı | prim_toplama | 1 | 1 | 1 | Tevkifatla birlikte kaynakta kesilir (tasarım); ölçülmemiş |
| Eski kayıtlıların sabit primi sürdürme payı (0 = hiç sürdürmez) | prim_devam | 0 | 0 | 0 | Sabit prim kalktığı için 0 |
| Maaşlı çalışanın mikro mükellef olma payı (u) | u_ucretli | 0.25 | 0.2 | 0.15 | Varsayım; maaşlı isterse girer (F 3-I 304) |
| Tevkifat oranı (gayrisafi hasılatın) | duz_oran | 0.135 | 0.135 | 0.135 | Teklif Madde 1 (e): %13,5 ile %27 arası; F 3-I 299 |
| BES aktarım oranı (tevkifatın) | bes | 0.03 | 0.03 | 0.03 | Teklif Madde 9 |
| Devlet katkısı oranı | devlet_katki | 0.2 | 0.2 | 0.2 | 4632 Ek 1 + 10811 sayılı Karar (ikincil) |
| BES vazgeçme payı | bes_vazgecme | 0.2 | 0.35 | 0.5 | Varsayım |
| MYÖ prim oranı | myo_oran | 0.21 | 0.21 | 0.21 | 5510 m.81 |
| Hibe prim süresi (ay) | myo_gun_ay | 3 | 3 | 3 | Teklif 5510 Ek 25 (90 gün) |
| 90 gün primi hak edenlerin payı (çakışmasız) | myo_uygun | 0.5 | 0.35 | 0.2 | Varsayım |
| Donanım alan payı | kdv_donanim_pay | 0.5 | 0.4 | 0.3 | Varsayım |
| Yıllık donanım KDV ortalaması (TL) | kdv_donanim_kdv | 5000 | 5000 | 5000 | Varsayım |
| KDV mahsup üst sınırı (tevkifatın oranı) | kdv_mahsup_tavan | 0.5 | 0.5 | 0.5 | Teklif Madde 3 önerisi |
| Eski rejimde kâr marjı | marj | 0.5 | 0.5 | 0.5 | Varsayım |
| Eski 4/b yıllık asgari prim (TL) | prim_eski | 141699 | 141699 | 141699 | 33.030×%35,75×12 |
| Eski prim ödeme oranı | prim_odeme | 0.8 | 0.8 | 0.8 | Varsayım |
| Ücretlinin marjinal oranı | r_marj_ucretli | 0.27 | 0.27 | 0.27 | Varsayım |
| Ücretlinin eski rejimde uyum oranı | uyum_ucretli | 0.5 | 0.5 | 0.5 | Varsayım |
| Kurumsal alıcı payı | kurumsal_pay | 0.7 | 0.7 | 0.7 | Varsayım |
| Kurumlar vergisi oranı | kv | 0.25 | 0.25 | 0.25 | Varsayım (kanunda %25) |
| Sahte fatura payı (kurumsal akışta, φ) | phi | 0.02 | 0.01 | 0.005 | Varsayım |
| Önlem etkinliği | onlem | 0.3 | 0.5 | 0.7 | Varsayım |
| KGF kullanım oranı | kgf_alim | 0.08 | 0.05 | 0.03 | Varsayım |
| KGF temerrüt oranı | kgf_temerrut | 0.15 | 0.1 | 0.06 | Varsayım |
| KGF kurtarma oranı | kgf_kurtarma | 0.3 | 0.3 | 0.3 | Varsayım |
| Kefalet tutarı (hasılatın payı) | kgf_pay | 0.5 | 0.5 | 0.5 | Teklif Madde 8 |
| PTT UETS birim gideri (TL) | ptt_birim | 50 | 50 | 50 | Varsayım |
| UETS tahsis payı | ptt_pay | 0.8 | 0.8 | 0.8 | Varsayım |
| Tek seferlik BT gideri (TL) | bt_tek | 2.5e+08 | 2.5e+08 | 2.5e+08 | Varsayım |
| Yıllık BT işletme gideri (TL) | bt_yillik | 5e+07 | 5e+07 | 5e+07 | Varsayım |
| İtiraz oranı | itiraz_oran | 0.04 | 0.04 | 0.04 | Varsayım |
| İtiraz birim gideri (TL) | itiraz_maliyet | 2000 | 2000 | 2000 | Varsayım |
| Denetim gideri (brüt tevkifatın oranı) | denetim | 0.01 | 0.01 | 0.01 | Varsayım |

## Sonuç (4. yıl, milyar TL)

| Kalem | Kötümser | Orta | İyimser |
| :-- | --: | --: | --: |
| Brüt tevkifat | 2,36 | 9,23 | 34,63 |
| BES ve Devlet katkısı | -0,07 | -0,22 | -0,62 |
| 90 gün prim hibesi | -0,10 | -0,34 | -0,83 |
| Donanım KDV mahsubu | -0,23 | -0,62 | -1,57 |
| Yutulma: vergi | -0,70 | -1,72 | -3,60 |
| Yutulma: eski prim | -3,40 | -5,63 | -6,21 |
| Gelire bağlı yeni prim | 0,26 | 1,25 | 5,44 |
| **NET** | -2,05 | 1,64 | 26,56 |
