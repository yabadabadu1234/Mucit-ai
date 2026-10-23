from icerik import a_cev

ID = 'cevmodem'
BASLIK = '3. Modem çeviricisi (12 V → 4,0 V, 2,8 A tepe)'
OZET = 'Aynı çip, farklı bir iş: 4G modemin kısa süreli 2,8 amperlik darbelerini besleyen 4,0 voltluk hattı, büyük çıkış kondansatörü ve zener diyot ile.'
REFS = ['U6', 'C10', 'C11', 'C12', 'C13', 'L2', 'R4', 'R5', 'C14', 'C15', 'C16', 'D3', 'R6', 'R7']

CFG = dict(
    id=ID, baslik=BASLIK, ozet=OZET, ad='Modem çeviricisi', ic='U6', cin='C10', cin_hf='C11', cbst='C12', css='C13', L='L2', rt='R4', rb='R5',
    cout=['C14', 'C15', 'C16', 'D3'], kutuplu=['C16'], sw_net='SW_MOD', out_net='VBAT_MOD', fb_net='FB_MOD', ss_net='SS_MOD', sema_genislik=1180, xs=[740, 830, 920, 1060], en=True,
    bolge_baslik='MODEM ÇEVİRİCİSİ  —  TPS62933: 12 V → 4,0 V (A7670SA besleme ucu VBAT)', iyuk=2.8, yuk='A7670SA modem (VBAT 3,4–4,2 V, tipik 3,8 V)', refs=REFS,
    sema_not='EN ucu işlemciden kontrol edilir: R6 normalde 3,3 V’a çeker, işlemci R7 üzerinden alçaltarak modemi kapatabilir.',
    isaret_ref=['U6', 'L2', 'C10', 'C12', 'C13', 'R4', 'C14'],
    ozel_ogren='Çok büyük bir çıkış kondansatörü neden gerekir ve veri sayfası bu konuda ne uyarır?',
    buyuk_resim='Modem, normal çalışmada az akım çeker ama verici katı darbe halinde çalışırken <b>kısa süreli 2,8 A</b> ister (SIMCom A7670 donanım belgesi: GSM darbesi 577 µs, her 4,615 ms). [[ds]] Besleme gerilimi bu darbede 300 mV’tan fazla düşmemeli ve hiçbir an 3,4 V’un altına inmemelidir. Bu yüzden ayrı bir çevirici ve büyük bir çıkış kondansatörü kullanılır: 3,3 V hattı modem yüzünden çökmez ve modem diğer yüklerden bağımsız olur.',
    isaretler=['<b>Çip (U6, TPS62933).</b> 3,3 V çeviricisiyle aynı çip; farkı bölücü değerleri ve EN ucunun kullanılmasıdır.',
               '<b>Bobin (L2, 4,7 µH, Bourns SRP7028A, Isat ≈ 10 A).</b> 2,8 A tepe yükte bobin akımı yaklaşık 3 A’e çıkar; ilk seçilen bobinin doyma akımı (2,7 A) bu yük için yetersizdi, bu yüzden değiştirildi. [[ds]]',
               '<b>Giriş kondansatörleri (C10, C11).</b> 3,3 V çeviricisindekilerle aynı.',
               '<b>Bootstrap (C12).</b> BST–SW arası 100 nF.',
               '<b>Yumuşak başlatma (C13).</b> 33 nF ≈ 4,8 ms; 374 µF çıkış kondansatörünü yavaş yükler.',
               '<b>Bölücü (R4: 40,2 kΩ, R5: 10 kΩ).</b> Çıkışı 4,02 V yapar (3,94–4,10 V; referans ±%2). [[ds]]',
               '<b>Çıkış (C14, C15: 22 µF seramik; C16: 330 µF polimer; D3: 5,1 V zener).</b> Seramikler yüksek frekansı, polimer büyük kondansatör akım darbesini karşılar; zener SIMCom’un önerdiği aşırı gerilim sigortasıdır (≥ 500 mW).'],
    ihtiyac_satirlari='<tr><td>Giriş</td><td>12 V</td><td>1. bölüm</td></tr><tr><td>Çıkış</td><td>4,0 V (3,4–4,2 V içinde)</td><td>[[ds]] SIMCom tablo 6</td></tr><tr><td>Yük akımı</td><td>tepe 2,8 A, ortalama çok daha az</td><td>[[ds]] SIMCom §3.1</td></tr><tr><td>Çıkış gerilimi çökmesi</td><td>darbede ≤ 300 mV</td><td>[[ds]] SIMCom §3.1</td></tr><tr><td>Çıkış kondansatörü (SIMCom önerisi)</td><td>2,8 A veren besleme için toplam ≥ 300 µF</td><td>[[ds]] SIMCom §3.1.1</td></tr>',
    tolerans_yorum=lambda a, b: 'Modemin kabul aralığı 3,4–4,2 V’tur [[ds]]; hesaplanan aralık bunun içindedir.',
    bobin_yorum=lambda ipk, irms, dI: 'Tepe akım %s A’dır; çipin yüksek taraf akım sınırının (4,2 / 5 / 5,8 A) altındadır, bobin Isat ≥ 5 A ile uyumludur (tipik sınır kadar).' % ('%.2f' % ipk).replace('.', ','),
    cout_yorum=lambda cout, tss: 'Çıkıştaki toplam kapasite ≈ %s µF’tır; SIMCom’un önerdiği ≥ 300 µF’ı sağlar. Fakat TPS62933 veri sayfası, tablo 10-2’deki değerlerin <b>çok üstünde</b> kapasite kullanılırsa başlangıç ve döngü kararlılığının dikkatle çalışılmasını ister. [[ds]] Başlangıç akımı C·dV/dt = %s × 4,02 / %s ms ≈ %s A, akım sınırının çok altındadır; fakat <b>döngü kararlılığı (Bode analizi) bu çalışmada yapılmadı</b>. [[dogrulanmadi]]' % (
        ('%.0f' % (cout * 1e6)), ('%.0f' % (cout * 1e6)) + ' µF', ('%.1f' % (tss * 1e3)).replace('.', ','), ('%.2f' % (cout * 4.016 / tss)).replace('.', ',')),
    uc_satirlari='<tr><td>Modem darbe çekerken</td><td>Çıkış 2,8 A’lik darbede kondansatörden ve çeviriciden beslenir: ΔV ≈ I·ESR + ΔQ/C; 330 µF polimer ve seramikler 300 mV sınırını sağlamak için seçildi. Gerçek ölçüm gerekir. [[dogrulanmadi]]</td></tr>'
                 '<tr><td>EN işlemciden düşürülürse</td><td>Çevirici durur, modem beslemesi kesilir (kapalı akım ≤ 2 µA [[ds]]). EN’i yeniden yükseltmek yumuşak başlatmayı yeniden başlatır.</td></tr>'
                 '<tr><td>FB bölücüsü kopsa</td><td>FB ucu 0 V görür, çıkış yükselmeye çalışır; çipin aşırı gerilim koruması (nominalin %115’i ≈ 4,36 V) devreye girer; 5,1 V zener ikinci güvencedir. [[ds]]</td></tr>'
                 '<tr><td>Zener yanıp kısa devre olursa</td><td>Çıkış toprağa çekilir; çip kısa devre korumasına ve hıçkırığa girer.</td></tr>'
                 '<tr><td>Modem bağlı değil</td><td>Çevirici hafif yükte PFM’de çalışır; ek akım çıkış kondansatörünün kaçağı ve bölücüdür.</td></tr>',
    kaynak_ek='SIMCom A7670 Series Hardware Design V1.00 §3.1 (VBAT 3,4–4,2 V, 2,8 A tepe, 300 µF, 2 mm iz, TVS önerisi) okundu. Benzetim: simulasyon/modem_gsm_patlama.cir; sonuç çeviricinin döngü bant genişliğine bağlıdır, bu değer veri sayfasında yok (bkz. simulasyon/SONUCLAR.md 1). [[dogrulanmadi]]',
)


def uret(ver, ctx):
    return a_cev.bolum_html(ver, CFG)
