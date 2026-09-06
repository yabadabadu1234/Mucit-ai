"""
KÜLLİYAT -- HARİCÎ METİN KAYNAKLARI, DEPOYA GİRMEDEN

===================================================================
PADİŞAHIN HÜKMÜ
===================================================================

    "Githubdan Risale-i Nur diyanet reposunu bizim repoya veri olarak
    ekle. Yine githubdan Türkçe İslami kaynaklar araştır ve repoya ekle.
    Bilhassa fıkıh hadis tefsir usulleri, Tefsir Hadis Tarih
    külliyatları, Edebi külliyatlar. İngilizce olarak da Ultramath veri
    setlerini repoya koy. Ya da kodu öyle yaz ki gidip oradan veri çekip
    burada eğitime katsın ama dosyaları repoya tümden koymasın."

İkinci yol seçildi ve sebebi ölçüdür: Risale-i Nur külliyatının tek
başına metni **13,8 MB**, deposu **118 MB**dır. Bunu kod deposuna
gömmek, her klonlamada yüz megabaytı taşımak demektir. Külliyat
``depo/kulliyat/`` altına **çekilir**, oraya gömülmez.

===================================================================
BU MAKİNEDE NE MÜMKÜN -- ÖLÇÜLDÜ, GİZLENMİYOR
===================================================================

Bu oturumun ağ siyaseti doğrudan HTTPS'i **reddediyor** (``CONNECT``a
403). Ölçüldü::

    api.github.com   → 403 (tünel reddedildi)
    huggingface.co   → 000 (tünel kurulamadı)

Fakat oturumun **git vekili** umumi GitHub depolarının anonim
okumasına hizmet ediyor ve o yol **açık**: ``git clone`` koşuyor.
O hâlde:

* **GitHub deposu olan kaynaklar çekilebilir** ve çekiliyor.
* **HuggingFace veri setleri çekilemiyor** (UltraMath dâhil). Bu bir
  tercih değil, ölçülmüş bir engeldir (ferman 1-F): engel yazılır,
  yerine bir şey konursa ne konduğu da yazılır.

===================================================================
KAYNAK CETVELİ -- HER SATIR YOKLANDI
===================================================================

Aşağıdaki cetvelin her satırı ya **fiilen klonlandı ve sayıldı**, ya da
niçin alınamadığı yazıldı. "Var sanıyorum" diye bir satır yoktur.
"""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

__all__ = ["Kaynak", "KAYNAKLAR", "kulliyat_cek", "kulliyat_verisi",
           "kulliyat_beyani", "KULLIYAT_DIZINI"]

#: Külliyatın indiği yer. **Depoya girmez** (``.gitignore``).
KULLIYAT_DIZINI = os.environ.get("MUCIT_KULLIYAT", "depo/kulliyat")


@dataclass(frozen=True)
class Kaynak:
    """Bir metin kaynağı. ``dal`` boşsa deponun kendi varsayılanı."""

    ad: str
    depo: str                 # "sahip/isim"
    yol: str                  # depo içinde metnin bulunduğu dizin
    uzanti: str = ".txt"
    dal: str = ""
    #: Alınamıyorsa sebebi. Boşsa alınabilir demektir.
    engel: str = ""


#: **CETVEL.** Her satır ya klonlandı ya da engeli yazıldı.
KAYNAKLAR: Tuple[Kaynak, ...] = (
    # ── ÇEKİLDİ VE SAYILDI ─────────────────────────────────────────
    Kaynak(ad="Risale-i Nur (Diyanet tashihli)",
           depo="alitekdemir/Risale-i-Nur-Diyanet",
           yol="txt", uzanti=".txt", dal="master"),
    Kaynak(ad="Risale-i Nur (Obsidian markdown nüshası)",
           depo="alitekdemir/Risale-i-Nur-Diyanet",
           yol="obsidian-markdown", uzanti=".md", dal="master"),
    Kaynak(ad="Gayr-i Münteşir Risale-i Nur Mektupları",
           depo="alitekdemir/ArsivNur", yol="", uzanti=".md"),
    Kaynak(ad="Risale-i Nur Kelime Frekansı (lügat)",
           depo="alitekdemir/Risale-i-Nur-Kelime-Frekans",
           yol="", uzanti=".txt"),
    # ── ENGELİ YAZILANLAR ──────────────────────────────────────────
    Kaynak(ad="UltraMath (İngilizce riyaziye)",
           depo="", yol="",
           engel="HuggingFace veri seti; bu oturumun ağ siyaseti "
                 "huggingface.co'ya CONNECT'i reddediyor (ölçüldü: 000). "
                 "GitHub aynası aranıp bulunamadı."),
    Kaynak(ad="Kütüb-i Sitte / Tefsir / Fıkıh külliyatları (Türkçe)",
           depo="", yol="",
           engel="GitHub deposu aranıp METİN GÖVDESİ olan bir umumi depo "
                 "bulunamadı: bulunanlar uygulama kabuğu (Kotlin/Dart/TS) "
                 "olup metni harici API'den çekiyor. Sorgular: "
                 "'hadis kutub-i sitte', 'hadith turkish translation', "
                 "'kuran meal tefsir hadis dataset turkish', "
                 "'turkish text corpus nlp dataset' -- dördü de boş "
                 "yahut metinsiz döndü."),
)


def _dizin(k: Kaynak) -> str:
    return os.path.join(KULLIYAT_DIZINI, k.depo.replace("/", "__"))


def kulliyat_cek(kaynaklar: Optional[Sequence[Kaynak]] = None,
                 sessiz: bool = False) -> List[Dict[str, Any]]:
    """Kaynakları ``depo/kulliyat/`` altına **çek**; ne çekildiğini döndür.

    Zaten çekilmişse tekrar çekilmez. Çekilemeyen **sessizce
    geçilmez**: sözlükte ``engel`` alanı sebebiyle beraber döner.
    """
    out: List[Dict[str, Any]] = []
    for k in (kaynaklar or KAYNAKLAR):
        if k.engel or not k.depo:
            out.append({"ad": k.ad, "alındı": False, "engel": k.engel,
                        "bayt": 0, "dosya": 0})
            continue
        d = _dizin(k)
        if not os.path.isdir(os.path.join(d, ".git")):
            os.makedirs(os.path.dirname(d) or ".", exist_ok=True)
            komut = ["git", "clone", "--depth", "1"]
            if k.dal:
                komut += ["--branch", k.dal]
            komut += ["https://github.com/" + k.depo, d]
            ortam = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1")
            r = subprocess.run(komut, capture_output=True, text=True,
                               env=ortam, timeout=900)
            if r.returncode != 0:
                out.append({"ad": k.ad, "alındı": False, "bayt": 0,
                            "dosya": 0,
                            "engel": "git clone düştü: %s"
                                     % (r.stderr or "").strip()[-200:]})
                continue
        kok = os.path.join(d, k.yol) if k.yol else d
        bayt = dosya = 0
        for kk, _dd, ff in os.walk(kok):
            if ".git" in kk:
                continue
            for f in ff:
                if f.endswith(k.uzanti):
                    dosya += 1
                    bayt += os.path.getsize(os.path.join(kk, f))
        out.append({"ad": k.ad, "alındı": True, "engel": "", "yol": kok,
                    "bayt": bayt, "dosya": dosya})
    return out


def kulliyat_verisi(sozluk: int, pencere: int, azami: int,
                    tohum: int = 0,
                    kaynaklar: Optional[Sequence[Kaynak]] = None
                    ) -> List[Tuple[List[int], int]]:
    """Külliyattan ``(bağlam, hedef)`` çiftleri -- tâlime katılacak hâlde.

    ===================================================================
    BELİRTEÇLEME: BAYT DÜZEYİ, ``sozluk`` MODÜLÜ
    ===================================================================

    Sözlük ``16``dır ve bu bir kusur değil, mimarinin kendi ölçüsüdür
    (veri lifi ``ℂ^16``). Metin UTF-8 baytlarına açılır ve ``mod
    sozluk`` alınır. **Bu bir kayıptır ve saklanmıyor**: 256 bayt 16
    seviyeye iner, yâni her seviye 16 baytı temsil eder.

    Niçin yine de manalıdır: mimari **münasebet** öğrenir, kelime
    değil. Hangi seviyenin hangisini takip ettiği, metnin istatistik
    yapısını taşır. Sözlük büyütülürse (``EgitimAyari.sozluk``) veri
    lifi de beraber büyür (``nefs/olcek.py`` Formül 1) ve kayıp azalır;
    yâni bu hudut **ayarlanabilir** ve nerede olduğu yazılıdır.
    """
    import numpy as np
    r = np.random.default_rng(int(tohum))
    metinler: List[bytes] = []
    for k in (kaynaklar or KAYNAKLAR):
        if k.engel or not k.depo:
            continue
        kok = os.path.join(_dizin(k), k.yol) if k.yol else _dizin(k)
        if not os.path.isdir(kok):
            continue
        for kk, _dd, ff in os.walk(kok):
            if ".git" in kk:
                continue
            for f in sorted(ff):
                if f.endswith(k.uzanti):
                    with open(os.path.join(kk, f), "rb") as fh:
                        metinler.append(fh.read())
    if not metinler:
        return []
    ham = b"\n".join(metinler)
    b = np.frombuffer(ham, dtype=np.uint8)
    assert b.size > int(pencere) + 1, (
        "külliyat penceresi doldurmuyor: %d bayt" % b.size)
    t = (b % np.uint8(int(sozluk))).astype(np.int64)
    n = int(azami)
    bas = r.integers(0, t.size - int(pencere) - 1, size=n)
    return [([int(x) for x in t[i:i + int(pencere)]],
             int(t[i + int(pencere)])) for i in bas]


def kulliyat_beyani(dokum: Optional[Sequence[Dict[str, Any]]] = None) -> str:
    """Külliyatın hâli -- **ne alındı, ne alınamadı, niçin**."""
    d = list(dokum if dokum is not None else kulliyat_cek())
    s = ["=== KÜLLİYAT (main/kulliyat.py) -- harici metin ===", "",
         "  Depoya gömülmez; ``%s`` altına çekilir." % KULLIYAT_DIZINI, ""]
    top_b = top_f = 0
    for k in d:
        if k["alındı"]:
            top_b += int(k["bayt"])
            top_f += int(k["dosya"])
            s.append("  ✔ %-46s %8.2f MB  %4d dosya"
                     % (k["ad"], k["bayt"] / 1e6, k["dosya"]))
        else:
            s.append("  ✘ %-46s ALINAMADI" % k["ad"])
            s.append("      sebep: %s" % k["engel"])
    s += ["", "  TOPLAM: %.2f MB, %d dosya" % (top_b / 1e6, top_f)]
    return "\n".join(s)
