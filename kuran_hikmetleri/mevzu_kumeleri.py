"""Mevzu başlıklarını üst kümelere ayırır ve Kur'ân geneli mevzu pastasını üretir.

Sûre bölümlemesindeki (sureler/*/sure.md) her mevzu başlığı, aşağıdaki KURALLAR
sırasıyla denenerek ilk eşleşen kümeye girer. Eşleşmeyen başlık "Diğer" olur.
Âyet sayısı segmentin (end - start + 1) toplamıdır; yüzdeler toplam 6236 âyete göre.
"""
import math
import re
from html import escape

# (küme adı, desen). Sıra önemlidir: ilk eşleşen kazanır.
KURALLAR = [
    ("Genel muhteva (sûre içi ilgili âyetler)", r"^Muhteva ve İlgili"),
    ("Hatime ve son hükümler", r"^Hatime ve Son Hükümler"),
    ("Hamd, dua ve doğru yol", r"Hamd|Duâ|Rahmet ve ahiret|Sırat"),
    ("Kıyamet, ahiret ve cezâ-mükâfât",
     r"Kıyamet|Ahiret|Ahirette|Cennet|Cehennem|Dirilme|Diriliş|Hutame|Terazi|Tartı|Sarsıntı|"
     r"Ebrar|Haber ve|Büyük haber|Aldanış|Ateş ve|Dönüş|Gruplar|Gelen|Tur'a yemin|Yemin ve kıyamet"),
    ("Müşrikler, inkârcılar ve münafıklar",
     r"Kâfir|Müşrik|Münafık|Nifak|İnkâr|İtiraz|Yalanla|Ebu Cehil|Velid|Ebu Leheb|Lat,|Şeytan|İblis|"
     r"Dostluk ve muhalefet|Karısı ve ip|Kavmin reddi|Peygambere iftira|Zalimler|Zina ve iftira|Mısır ve iftira|"
     r"Küfr|Üç grup|Düşmanın|Dört şart|Fücur|Kevser|İmtihan"),
    ("Peygamber kıssaları ve kavimler",
     r"Mûsâ|Musa|Nûh|Hûd|Sâlih|Lût|Şuayb|Firavun|İbrâhîm|İbrahim|Âd\b|Semûd|Süleyman|Davud|Eyyub|Bahçe sahipleri|"
     r"İsa|Meryem|Zekeriyyâ|Yûnus|Kehf|Zülkarneyn|Kârûn|Medyen|Ashâb|Ashab|Hicr|Ebrehe|Mâide kıssası|"
     r"Kavim|Kıssa|Kıssalar|Âdem|Hızır|İsrailoğulları|Sebe'|Kureyş|Yûsuf|Yusuf|Zülkarneyn|Lokmân"),
    ("Savaş, gazve ve Medine dönemi",
     r"Uhud|Tebük|Hendek|Hudeybiye|Benî Nadîr|Ganimet|Savaş|Cihad|Bizans|Esir|Berâe|Hıyanet|"
     r"Mübâhele|Necran|Yardım ve fetih|Zafer|Muhacir|Ehl-i kitap ve cihad|Hac, münafık"),
    ("Peygamberlik, vahiy ve Kur'ân",
     r"Vahi|Kur'an|Kur'ân|Kitab|Furkân|Nûr|Risalet|Tebliğ|Peygamber|Hikmet|Tevrat|Arını|Şairler|Demir ve|Yahudiler|"
     r"Şairlerin|Ruhu|Hidayet|Mesajı|İlk vahiy|Delil ve|Ehl-i kitap|Muhkem|Esma"),
    ("Hukuk, ibadet ve aile",
     r"Hukuk|Namaz|Oruç|Nikâh|Boşam|Miras|Yetim|Abdest|Zina|Hırsız|Kısas|Faiz|Borç|Helal|Haram|Hüküm|Rüya|Tanışma|"
     r"Hac|Zekât|İnfak|Gece ibadeti|Secde|Cuma|Zikir|Kullar ve ibadet|Tesbih|Aile|Evlere|Zıhar|"
     r"Tartıda|Kadınların|Ahitler|Gizli görüşme|Tesettür|Zikir|Adalet ve|Zeyd|Boşama|Iddet|Mal fitnesi"),
    ("Mümin, takva ve sabır",
     r"Mümin|Müttakî|Müttakiler|Takva|Sabır|Tevekkül|Müminlerin|Şükür|İhsan|Sahabe|Amel|İstiğfar|Ahlakî|İstikâmet|Abdullah|Zikir|"
     r"Tevbe|Tevbe|Kalplerin|İç vesvese|Dış şerler|Teselli|Melekler ve sabır|Ayıplayanlar|Gıybet|"
     r"Haber doğrulama|Dostluk|Yoksul|Tavsiye|Mülk|Sorumluluk|Yalancı|Vahyin ağırlığı|Son hüküm|Kitabın"),
    ("İnsan ve nefs",
     r"İnsan|İnsanın|Nimet|Karakter|Kader|Yaratılış|Fıtrat|Riya|Çokluk|Kendini|Gizli|Gece ve gündüz|"
     r"Nefis|Yemin ve nefis|Göğsün|Zorluk|Yaratıcının nimetleri|İlaf|Namazda riya|Ahitten"),
    ("Tevhid, kâinat ve kozmik deliller",
     r"Tevhid|Kozmik|Kâinat|kâinat|Delil|Yemin|Gece|Burç|İncir|Zamana|Rüzgâr|Atlar|Şehre|Örümcek|"
     r"Tesbih|Kadir|Kur'an'ın Arapçalığı|Cin|Hak-bâtıl|Ayın yarılması|Mülk|Büyük|Kâinat"),
]

KURAL_DERLENMIS = [(ad, re.compile(desen, re.IGNORECASE)) for ad, desen in KURALLAR]
DIGER = "Diğer"


def kume_adi(baslik):
    """Bir mevzu başlığının üst kümesini döndürür."""
    for ad, desen in KURAL_DERLENMIS:
        if desen.search(baslik):
            return ad
    return DIGER


def kume_toplamlari(surahs_data):
    """Üst küme → (âyet sayısı, segment sayısı, başlık sayısı) sözlüğü."""
    toplam = {}
    for s in surahs_data:
        for seg in s.get("segments", []):
            ad = kume_adi(seg["title"])
            ayet = seg["end"] - seg["start"] + 1
            t = toplam.setdefault(ad, {"ayet": 0, "segment": 0, "basliklar": set()})
            t["ayet"] += ayet
            t["segment"] += 1
            t["basliklar"].add(seg["title"])
    return toplam


PALET = ["#1e40af", "#065f46", "#b45309", "#991b1b", "#4338ca", "#0e7490",
         "#6d28d9", "#be185d", "#3f6212", "#44403c", "#0f766e", "#9a3412"]


def _dilim_yolu(cx, cy, r, bas, son):
    """Merkezi (cx, cy), yarıçapı r olan dilimin SVG yolu. Açılar radyan, saat yönünde, üstten başlar."""
    if son - bas >= 2 * math.pi - 1e-9:
        return f"M {cx} {cy - r} A {r} {r} 0 1 1 {cx} {cy + r} A {r} {r} 0 1 1 {cx} {cy - r} Z"
    x1, y1 = cx + r * math.sin(bas), cy - r * math.cos(bas)
    x2, y2 = cx + r * math.sin(son), cy - r * math.cos(son)
    buyuk = 1 if son - bas > math.pi else 0
    return f"M {cx} {cy} L {x1:.2f} {y1:.2f} A {r} {r} 0 {buyuk} 1 {x2:.2f} {y2:.2f} Z"


def mevzu_pasta(surahs_data):
    """Kur'ân geneli mevzu pastası: dilimlerde âyet sayısı ve yüzde, açıklamada mevzu adı."""
    toplam = kume_toplamlari(surahs_data)
    genel = sum(t["ayet"] for t in toplam.values())
    sirali = sorted(toplam.items(), key=lambda kv: -kv[1]["ayet"])

    cx, cy, r = 260, 260, 230
    dilimler, aciklamalar = [], []
    aci = 0.0
    for i, (ad, t) in enumerate(sirali):
        oran = t["ayet"] / genel
        fark = oran * 2 * math.pi
        renk = PALET[i % len(PALET)]
        dilimler.append(f'<path d="{_dilim_yolu(cx, cy, r, aci, aci + fark)}" fill="{renk}" '
                        f'stroke="#ffffff" stroke-width="1.5"/>')
        if oran >= 0.05:
            orta = aci + fark / 2
            tx, ty = cx + r * 0.62 * math.sin(orta), cy - r * 0.62 * math.cos(orta)
            dilimler.append(
                f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="middle" fill="#ffffff" '
                f'font-size="15" font-weight="700">%{oran * 100:.1f}</text>'
                f'<text x="{tx:.1f}" y="{ty + 16:.1f}" text-anchor="middle" fill="#ffffff" '
                f'font-size="12">{t["ayet"]} âyet</text>')
        aciklamalar.append(
            f'<li><span class="mp-renk" style="background:{renk}"></span>'
            f'<span class="mp-ad">{escape(ad)}</span>'
            f'<span class="mp-say">{t["ayet"]} âyet · %{oran * 100:.1f} · {t["segment"]} bölüm</span></li>')
        aci += fark

    return f"""
    <div class="page doc-page mevzu-pasta">
      <h2>Kur'ân-ı Kerim · mevzu nispetleri</h2>
      <p class="mo-not">Bütün Kur'ân ({genel} âyet) sûre bölümlemesindeki mevzu başlıklarının üst kümelere göre dağılımı.
      Dilimlerde âyet sayısı ve nispet; açıklamada mevzu adı yazılıdır.</p>
      <div class="mp-kap">
        <svg viewBox="0 0 520 520" class="mp-svg" role="img" aria-label="Kur'ân mevzu pastası">{"".join(dilimler)}</svg>
        <ul class="mp-aciklama">{"".join(aciklamalar)}</ul>
      </div>
    </div>
    """
