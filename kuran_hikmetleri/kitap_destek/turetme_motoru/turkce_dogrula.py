import turkce as T

# Vezinler Tablosu (padişahın resmi, F 360 ve F 3-I 3xx): her satır = (Türkçe fiil kökü, ism-i fâil, ism-i mef'ûl)
TABLO = [
    ('ikram et', 'ikram eden', 'ikram edilmiş'), ('inkâr et', 'inkâr eden', 'inkâr edilmiş'),
    ('haber et', 'haber eden', 'haber edilmiş'), ('tertip et', 'tertip eden', 'tertip edilmiş'),
    ('ders ver', 'ders veren', 'ders görmüş'), ('ilim öğret', 'ilim öğreten', 'ilim görmüş'),
    ('şekillen', 'şekillenen', 'şekillenmiş'), ('gülümse', 'gülümseyen', 'gülümsenen'),
    ('düşün', 'düşünen', 'düşünülmüş'), ('birik', 'biriken', 'birikmiş'),
    ('uygun ol', 'uygun olan', 'uygun olunmuş'), ('tesadüf et', 'tesadüf eden', 'tesadüf edilmiş'),
    ('karış', 'karışan', 'karışmış'), ('uy', 'uyan', 'uymuş'),
    ('öğün', 'öğünen', 'öğünülmüş'), ('sıkıntı ol', 'sıkıntı olan', 'sıkıntı olunmuş'),
    ('bekle', 'bekleyen', 'beklenmiş'), ('yetiştir', 'yetiştiren', 'yetiştirilmiş'),
    ('söyle', 'söyleyen', 'söylenmiş'), ('hazırla', 'hazırlayan', 'hazırlanmış'),
]


def calistir():
    tuttu, tutmadi = 0, []
    for v, f, m in TABLO:
        tr, _ = T.gecislilik(v)
        gecisli = tr in ('tr', 'aux')
        g = T.f_fail(v)
        mm = T.f_mefp(v) if gecisli else T.f_pf(v)
        for ad, uret, bek in (('fâil', g, f), ('mef‘ûl', mm, m)):
            if uret == bek:
                tuttu += 1
            else:
                tutmadi.append((v, ad, bek, uret))
    return tuttu, tutmadi


if __name__ == '__main__':
    t, m = calistir()
    print('tuttu', t, 'tutmadı', len(m))
    for x in m:
        print(x)
