MAHREC = {'halk': 'ءهعحغخ', 'lehevî': 'قك', 'şecrî': 'جشي', 'dil kenarı': 'ض', 'tarafî': 'لنر', "nıt'î": 'طدت', 'lisevî': 'ظذث', 'esle': 'صزس', 'şefevî': 'فبمو'}
SIFAT = {'hems': 'فحثهشخصسكت', 'şiddet': 'ءجدقطبكت', 'tavassut': 'لنعمر', 'istilâ': 'خصضغطقظ', 'itbâk': 'صضطظ', 'kalkale': 'قطبجد', 'safîr': 'صزس', 'gunne': 'نم', 'izlâk': 'فرمنلب'}
SINIF = {**{f'mahreç: {k}': set(v) for k, v in MAHREC.items()}, **{f'sıfat: {k}': set(v) for k, v in SIFAT.items()}}
def norm(h): return {'أ': 'ء', 'إ': 'ء', 'ؤ': 'ء', 'ئ': 'ء', 'آ': 'ء', 'ى': 'ي'}.get(h, h)
