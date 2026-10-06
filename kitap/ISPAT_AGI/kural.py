HABER = ('U10', 'U11', 'U18')
SINIF = ('U19', 'U20', 'U21', 'U22', 'U23', 'U24', 'U25')

HABER_SEBEP = 'Aklî–metafizik hüküm haberle ispat edilmez; muhatap haberi ve vahyi kabul etmeden onu öncül yapmak kısırdöngüdür (F 3-I 187; V.0.5).'
SEBEP_YOK = 'Vâcib’in sebebi yoktur; limmî ve mutlak burhân sebepsiz şeyde kurulamaz (I.4.6.16).'

HEPSI = ('zemin', 'kavram', 'sayi', 'tenzih', 'fiil', 'sifat', 'ulûhiyet', 'bilgi', 'illet', 'vacib-varlik')


def yapilamaz(u, tur, soru_id, hukum, felsefe_say, tag_var):
    if u in HABER:
        return HABER_SEBEP
    if u == 'U12':
        return 'Müşâhede edilemeyen şeyi (gayb, Vâcib) doğrudan ispat edemez; bu hücrede öncül de sağlamıyor (I.4.3.5).'
    if u == 'U13':
        return 'Metafizik varlığa uygulanamaz; bu hücrede kanun düzeni öncülü de kullanılmıyor.'
    if u == 'U14':
        if tur in ('kavram', 'tenzih', 'sayi', 'illet', 'sifat', 'ulûhiyet', 'zemin', 'bilgi'):
            return 'Hükmün konusu taranabilir cüz’îlerden oluşmaz; istikrâ uygulanamaz.'
        return None
    if u == 'U15':
        return 'Hads sonradan doğrulama ister; bu hükümde doğrulayıcı bir ikinci yol yok.'
    if u in ('U02', 'U20', 'U21'):
        if tur in ('vacib-varlik', 'illet', 'kavram', 'zemin', 'bilgi', 'sayi', 'tenzih', 'ulûhiyet'):
            return SEBEP_YOK
        return None
    if u == 'U22':
        if soru_id != 'Q16':
            return 'Vâcib basittir ve maddesi yoktur; maddî sebep orta terim olamaz.'
        return None
    if u == 'U23':
        if tur in ('zemin', 'bilgi', 'fiil', 'sayi'):
            return 'Hükmün konusu bir tanım veya sûret değildir.'
        return None
    if u == 'U24':
        if tur in ('zemin', 'kavram', 'tenzih', 'sayi', 'bilgi', 'illet'):
            return 'Hükmün konusu fiil ve fâil değildir.'
        return None
    if u == 'U25':
        if tur in ('zemin', 'kavram', 'tenzih', 'sayi', 'bilgi', 'illet'):
            return 'Hükmün konusu gâye değildir.'
        return None
    if u == 'U19':
        if tur in ('zemin',):
            return 'Zemin hükmü bir varlık bildirmez; enne burhânının konusu varlıktır.'
        return None
    if u == 'U01':
        if tur in ('kavram', 'tenzih', 'sayi', 'zemin', 'bilgi', 'illet', 'ulûhiyet'):
            return 'Hükmün konusu bir eserden müessire geçiş değildir.'
        return None
    if u == 'U03':
        if tur in ('zemin', 'kavram', 'bilgi', 'ulûhiyet'):
            return 'Hükmün konusu mümkinin müreccihe muhtaçlığına bağlanmaz.'
        return None
    if u == 'U04':
        if tur not in ('vacib-varlik', 'fiil'):
            return 'Hudûs delili âlemin başlangıcı ve hâdisin muhdisi üzerinedir; bu hükmün konusu o değildir.'
        return None
    if u in ('U05', 'U06'):
        if tur not in ('vacib-varlik', 'illet'):
            return 'Hükümde sebep zinciri veya dairesi yoktur.'
        return None
    if u == 'U09':
        if tur != 'sifat':
            return 'Vâcib’in benzeri yoktur; temsil yalnız kemâl cinsinden sıfatlarda zan verir.'
        return None
    if u == 'U17':
        if tur in ('zemin', 'kavram', 'bilgi'):
            return 'Hükmün konusu bir verinin açıklaması değildir.'
        return None
    if u == 'U26':
        return 'Karşı iddia kendi ifadesiyle kendini çürütmüyor; ilzamın şartı bu hükümde yok (Claude hükmü, yoklanmadı).'
    if u in ('U27', 'U29'):
        if hukum == 'DOĞRU':
            return 'Doğru hücrede çürütülecek bir iddia yoktur.'
        if felsefe_say == 0:
            return 'Bu hücreyi savunan kayıtlı bir felsefe yok; muhatabın öncülü bilinmiyor.'
        return None
    if u == 'U28':
        if tur in ('zemin', 'bilgi'):
            return 'Hükmün konusu bir kavramın tutarlılığı değildir.'
        return None
    if u == 'U31':
        return 'Bu usul yalnız Vâcib’in varlığı mefhumundan yürür (V.6.2.167).'
    if u == 'U32':
        if tur not in ('vacib-varlik', 'ulûhiyet'):
            return 'Tenbih delil değildir; yalnız varlık ve ulûhiyet hücrelerinde muhatabı yönlendirir.'
        return None
    return None
