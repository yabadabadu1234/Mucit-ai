"""Konu dizininden (00_FIHRIST.md, 'Kısımlar' bölümünden sonra) âyet haritası üretir.

Her sûre bir satırdır; her âyet bir hücredir. Hücrenin rengi, o âyetin kaç konu girdisinde
anıldığını gösterir. Hücrenin üzerine gelindiğinde konu adları listelenir.
Çıktı: konu_haritasi.html (repo kökündeki kitapla birlikte kullanılabilir).

Kullanım (kuran_hikmetleri/ içinden): python3 konu_haritasi.py
"""
import re
from collections import defaultdict
from html import escape
from pathlib import Path

BASE = Path(__file__).resolve().parent
FIHRIST = BASE / "00_FIHRIST.md"
CIKTI = BASE / "konu_haritasi.html"
TOPLAM_AYET = 6236


def konulari_oku():
    """(konu, [(sûre, başlangıç, bitiş), ...]) listesi."""
    satirlar = FIHRIST.read_text(encoding="utf-8").splitlines()
    bas = next(i for i, s in enumerate(satirlar) if s.startswith("*'(rivayet)'"))
    konular = []
    for ham in satirlar[bas + 1:]:
        s = ham.strip()
        if not s or s.startswith(("|", "#", "- **")) or ":" not in s:
            continue
        # Tırnaklı alıntının içindeki iki nokta konu ayırıcısı değildir: atıf, sayıdan önceki iki noktadadır.
        parcalar = re.split(r":\s+(?=\d)", s, maxsplit=1) if "“" in s else s.split(":", 1)
        konu, refs = parcalar[0], parcalar[1]
        konular.append((konu.strip(), refs.strip()))
    atif_haritasi = {k: _atiflari_ayristir(r) for k, r in konular}
    cozulmus = []
    for konu, refs in konular:
        if refs.startswith("bk.") or konu in CAPRAZ_GONDERMELER:
            hedefler = CAPRAZ_GONDERMELER.get(konu) or [refs[3:].strip().rstrip(".").strip("()")]
            atiflar = []
            for hedef in hedefler:
                atiflar += atif_haritasi.get(hedef, [])
        else:
            atiflar = _atiflari_ayristir(refs)
        cozulmus.append((konu, atiflar))
    return cozulmus


# Çapraz gönderme düzeltmeleri: dizinde bulunmayan ya da yazımı farklı hedefler, mantıkla karşılığına eşlendi.
CAPRAZ_GONDERMELER = {
    "Âd kavmi": ["Hûd’un kavmi"],
    "Arzularını putlaştıranlar": ["Hevâ ve heves"],
    "Camilerin imârı": ["Mescidler"],
    "Cibrîl": ["Cebrail"],
    "Rûhu’l-Kudüs": ["Cebrail"],
    "Ekolojik denge": ["Çevresel denge"],
    "Emr-i mâruf": ["İyiliği emretmek"],
    "Ferâiz": ["Mîras"],
    "Gayb": ["İnsan idrakini aşan bilgi sahası"],
    "Gök cisimlerinin durumları": ["Kozmoğrafya"],
    "Hadd": ["Cezâlar"],
    "Halîfe": ["İnsanın halîfe olarak yaratılması"],
    "İblîs": ["Şeytan"],
    "İblîs’in isyanı": ["Şeytanın Âdem’e secde etmeyişi"],
    "İnsanların hayvana benzemesi": ["Hayvanlar gibi olanlar"],
    "Kıyâmet ve Hesap": ["Âhiret gününde olacak olaylar"],
    "Korku ânında yapılanlar": ["Felâket ânı"],
    "Korunma âyetleri": ["Hıfz âyetleri"],
    "Kozmoloji": ["Kâinat md."],
    "Kör olanlar": ["Dünyada mânen kör olanlar"],
    "Kur’an’da temsîlî anlatımlar": ["Darb-ı meseller"],
    "Mürted": ["Dinden dönenler"],
    "Nezâfet": ["Temizlik"],
    "Önderler": ["Din dışı dünyalık liderler"],
    "Peygamber’in sünnetine uymak": ["Sünnete uymak"],
    "Ribâ": ["Fâiz"],
    "Semûd kavmi": ["Salih’in (as.) kavmi"],
    "Talak": ["Boşama"],
    "Tenâsuh": ["Reenkarnasyon"],
    "Terazi": ["Ölçü, tartı"],
    "Toplum": ["Ümmet"],
    "Uzuvlar": ["Âzâların şehadeti"],
    "Üç sınıf insan": ["Sağın/solun adamları, hayırda önde gidenler"],
    "Ümmetlerin helâki": ["Ecel"],
    "Yok olma": ["Helâk olma"],
    "Zekât-sadaka verin, namaz kılın": ["Namaz kılın, zekât-sadaka verin"],
    "Dört büyük kitap": ["Kur’an", "Tevrat", "İncil ve Zebûr"],
}


def _atiflari_ayristir(refs):
    """'2/124, 258; 4/168-169' → [(2,124,124), (2,258,258), (4,168,169)].

    Sonundaki açıklamalar ('ve dipnotu', 'dipnotu', '(İyi):' gibi etiketler) atılır.
    Boşluklu yazımlar ('12/ 4-18', '4/38,119 43/36-38') da okunur.
    """
    refs = re.sub(r"\([^)]*\):\s*", "", refs)
    refs = re.sub(r"/\s+", "/", refs)
    gövde = re.split(r"\s+(?=[A-Za-zÇĞİÖŞÜçğıöşü(’'])", refs.strip(), maxsplit=1)[0]
    cikti, sure = [], None
    for tok in re.findall(r"\d+/\d+(?:-\d+)?|\d+(?:-\d+)?", gövde):
        if "/" in tok:
            sure_s, aralik = tok.split("/")
            sure = int(sure_s)
        else:
            aralik = tok
        if sure is None:
            continue
        a, _, b = aralik.partition("-")
        cikti.append((sure, int(a), int(b or a)))
    return cikti


def sure_adlari():
    """Sûre numarası → Türkçe ad (fihrist tablosundan)."""
    adlar = {}
    for ln in FIHRIST.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*\d+\s*\|\s*(\d+)\s*\|\s*\d+\s*\|\s*[^|]+\|\s*([^|]+?)\s*\|", ln)
        if m:
            adlar[int(m.group(1))] = m.group(2)
    return adlar


def sure_ayet_sayilari():
    """Sûre numarası → âyet sayısı (fihrist tablosundan)."""
    sayilar = {}
    for ln in FIHRIST.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*\d+\s*\|\s*(\d+)\s*\|\s*(?:[^|]*\|){4}\s*(\d+)\s*\|", ln)
        if m:
            sayilar[int(m.group(1))] = int(m.group(2))
    return sayilar


def harita_verisi(konular):
    """(sûre, âyet) → konu adlarının listesi."""
    anilma = defaultdict(list)
    for konu, atiflar in konular:
        for sure, a, b in atiflar:
            for ayet in range(a, b + 1):
                anilma[(sure, ayet)].append(konu)
    return anilma


def bolum_html(anilma, adlar, sayilar):
    """Kitaba girecek harita bölümü (stil bölümün başında gömülü)."""
    en_cok = max((len(v) for v in anilma.values()), default=1)
    satirlar = []
    for sure in range(1, 115):
        n = sayilar.get(sure, 0)
        hucreler = []
        for ayet in range(1, n + 1):
            konular = anilma.get((sure, ayet), [])
            oran = len(konular) / en_cok
            renk = "#e2e8f0" if not konular else f"rgba(30,64,175,{0.15 + 0.85 * oran:.2f})"
            ipucu = f"{sure}:{ayet} · {len(konular)} konu" + ("\n" + "\n".join(konular) if konular else "")
            hucreler.append(f'<i style="background:{renk}" title="{escape(ipucu)}"></i>')
        satirlar.append(
            f'<div class="kh-satir"><span class="kh-sure">{sure}. {escape(adlar.get(sure, ""))}</span>'
            f'<span class="kh-hucreler">{"".join(hucreler)}</span></div>'
        )
    return f"""
    <style>{KONU_HARITA_CSS}</style>
    <div class="page doc-page konu-harita">
      <h2>Konu haritası · Kur'ân âyetlerinin konu yoğunluğu</h2>
      <p class="kh-not">Her hücre bir âyettir; koyu olan, konu dizininde daha çok anılmış âyettir. Üzerine gelin: âyet numarası ve konuları görünür. Kaynak: 00_FIHRIST.md konu dizini ({sum(len(v) for v in anilma.values())} âyet-konu girişi, {len(anilma)} farklı âyet).</p>
      {"".join(satirlar)}
      <p class="kh-not">Açık gri: hiçbir konuda anılmamış âyet. Koyu mavi: en çok konuda anılan âyetler (en fazla {en_cok} konu).</p>
    </div>
    """


KONU_HARITA_CSS = """
.kh-satir { display:flex; align-items:center; gap:8px; margin-bottom:2px; }
.kh-sure { width:180px; flex:0 0 180px; font-size:9pt; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.kh-hucreler { display:flex; flex-wrap:nowrap; gap:1px; }
.kh-hucreler i { display:block; width:7px; height:12px; border-radius:1px; }
.kh-not { font-size:9pt; color:#475569; margin:6px 0; }
"""


def harita_bolumu():
    """Kitap derlemesi için harita bölümü HTML'i."""
    konular = konulari_oku()
    return bolum_html(harita_verisi(konular), sure_adlari(), sure_ayet_sayilari())


def html_uret(anilma, adlar, sayilar):
    en_cok = max((len(v) for v in anilma.values()), default=1)
    satirlar = []
    for sure in range(1, 115):
        n = sayilar.get(sure, 0)
        hucreler = []
        for ayet in range(1, n + 1):
            konular = anilma.get((sure, ayet), [])
            oran = len(konular) / en_cok
            renk = "#e2e8f0" if not konular else f"rgba(30,64,175,{0.15 + 0.85 * oran:.2f})"
            ipucu = f"{sure}:{ayet} · {len(konular)} konu" + ("\n" + "\n".join(konular) if konular else "")
            hucreler.append(f'<i style="background:{renk}" title="{escape(ipucu)}"></i>')
        satirlar.append(
            f'<div class="satir"><span class="sure">{sure}. {escape(adlar.get(sure, ""))}</span>'
            f'<span class="hucreler">{"".join(hucreler)}</span></div>'
        )
    return f"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Konu Haritası · Âyet Yoğunluğu</title>
<style>
  body {{ margin:0; padding:16px; font-family: system-ui, sans-serif; background:#ffffff; color:#0f172a; }}
  h1 {{ font-size:18px; margin:0 0 4px; }}
  p.not {{ font-size:12px; color:#475569; margin:0 0 12px; }}
  .satir {{ display:flex; align-items:center; gap:8px; margin-bottom:2px; }}
  .sure {{ width:180px; flex:0 0 180px; font-size:11px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
  .hucreler {{ display:flex; flex-wrap:nowrap; gap:1px; }}
  .hucreler i {{ display:block; width:7px; height:12px; border-radius:1px; }}
  .lejant {{ font-size:11px; color:#475569; margin:12px 0 0; }}
</style></head>
<body>
<h1>Konu Haritası · Kur'ân âyetlerinin konu yoğunluğu</h1>
<p class="not">Her hücre bir âyettir; koyu olan, konu dizininde daha çok anılmış âyettir. Üzerine gelin: âyet numarası ve konuları görünür. Kaynak: 00_FIHRIST.md konu dizini ({sum(len(v) for v in anilma.values())} âyet-konu girişi, {len(anilma)} farklı âyet).</p>
{"".join(satirlar)}
<p class="lejant">Açık gri: hiçbir konuda anılmamış âyet. Koyu mavi: en çok konuda anılan âyetler (en fazla {en_cok} konu).</p>
</body></html>
"""


def main():
    konular = konulari_oku()
    anilma = harita_verisi(konular)
    html = html_uret(anilma, sure_adlari(), sure_ayet_sayilari())
    CIKTI.write_text(html, encoding="utf-8")
    print(f"konu: {len(konular)}, âyet: {len(anilma)}, çıktı: {CIKTI}")


if __name__ == "__main__":
    main()
