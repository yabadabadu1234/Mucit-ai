"""
Kademe 1 -- **envanter ve arayüz akdi**.

Nizamnamenin birinci kademesi şunu ister: dağınık modüllerin ana icra
hattıyla akdi *makinece okunabilir* olsun; kimin neyi okuduğu, neyi
yazdığı ve hangi uzva bağlandığı belge değil **veri** olsun.

Burada üç şey vardır:

1. ``UZUV_SOFRASI`` -- her meleke için: hangi harici modül fiilen
   çağrılıyor, yoksa hâlâ **vekil** mi (yani melekenin işini bir skaler
   formül mü görüyor).
2. ``envanter()`` -- sicilden okunan sözleşme + sofradaki uzuv kaydı,
   tek tabloda.
3. ``akdi_denetle()`` -- sofra ile kodun **uyuşup uyuşmadığı**. Sofrada
   "şu modül kullanılıyor" yazıp kodda çağırmamak, en tehlikeli yalandır:
   belge doğru görünür, sistem boştur. Denetim kaynak metni tarayıp
   ``import`` var mı diye bakar.

**Ölçüt (kütük H1).** Bir modülün "bağlı" sayılması için ``nefs/``
altındaki bir melekenin onu çağırması gerekir. Kendi dosyasında
mükemmel yazılmış olması bağlılık değildir.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

from . import melekeler as akil  # noqa: F401  (sicili doldurur)
from . import melekeler as beyan
from . import melekeler as idrak
from . import melekeler as murakabe
from .melekeler import Meleke, melekeler, sicil

__all__ = ["Uzuv", "UZUV_SOFRASI", "envanter", "akdi_denetle", "rapor",
           "vekil_kalanlar", "yazmayanlar"]

_NEFS = Path(__file__).resolve().parent


# =====================================================================
@dataclass(frozen=True)
class Uzuv:
    """Bir melekenin uzvu: hangi modülün hangi kabiliyeti.

    ``vekil`` doğruysa meleke hâlâ yerine konmuş bir formülle çalışıyor
    demektir -- yani o kabiliyet **yok**, taklidi var. Bunu gizlemek
    yerine tabloya yazmak esastır; ilerleme ancak sayılabilirse olur.
    """
    modul: str
    kabiliyet: str
    vekil: bool = False
    not_: str = ""


# ---------------------------------------------------------------------
#  Uzuv sofrası: 𝒪ₙ → uzuv
# ---------------------------------------------------------------------
UZUV_SOFRASI: Dict[int, Uzuv] = {
    1:  Uzuv("nefs.melekeler", "FNO spektral ön-süzgeç + odak çekirdeği"),
    2:  Uzuv("nefs.melekeler", "hissî suret kodlaması"),
    3:  Uzuv("nefs.melekeler", "muhayyile serbestliği"),
    4:  Uzuv("nefs.sahit", "şahit bölütlemesi (kopma ölçüsü, MAD eşiği)"),
    5:  Uzuv("nefs.melekeler", "Grassmann kesiti ``w ∈ ℳ`` + Betti sayıları"),
    6:  Uzuv("nefs.melekeler", "tasavvur: mana uzayına geçiş"),
    7:  Uzuv("nefs.melekeler", "vâhime çekirdeği"),
    8:  Uzuv("nefs.melekeler", "SVD tahlili"),
    9:  Uzuv("nefs.melekeler", "terkip"),
    10: Uzuv("nefs.melekeler", "tezat kutbu → 𝒪₁₁ çelişki çekirdeği"),
    11: Uzuv("nefs.melekeler", "çelişki çekirdeği ``C = −S(AᵀA)Sᵀ`` + ıslah"),
    12: Uzuv("nefs.melekeler", "üç başlıklı maliyet ve eleme"),
    13: Uzuv("nefs.melekeler", "tasdik mührü → ``d.hukum`` kaydı"),
    14: Uzuv("nefs.melekeler", "gaye"),
    15: Uzuv("nefs.melekeler", "sual"),
    16: Uzuv("nefs.melekeler", "taban çıkarmalı REINFORCE → Mutasarrıfa R_t (𝒪₂₁)"),
    17: Uzuv("nefs.melekeler", "Bayes ardılı → 𝒪₂₅ Teemmül önseli"),
    18: Uzuv("nefs.sahit", "şahit başına dik Procrustes kaidesi (kapalı form)"),
    19: Uzuv("nefs.melekeler", "sözde ters ile somut temsil → 𝒪₂₇ kusur ölçüsü"),
    20: Uzuv("nefs.melekeler", "vech-i şebeh → 𝒪₃₉ Belâgat"),
    21: Uzuv("nefs.melekeler", "tefekkür devri"),
    22: Uzuv("nefs.melekeler", "NOTEARS asiklik + arka kapı"),
    23: Uzuv("matematik.mizan", "nakz sınaması + Gazâlî yakîni (``min``)"),
    24: Uzuv("nefs.melekeler", "burhân zinciri"),
    25: Uzuv("nefs.melekeler", "büzücü devridaim + durma ölçütü"),
    26: Uzuv("nefs.melekeler", "asgarî arama + vakarla harman (S yazar)"),
    27: Uzuv("nefs.melekeler", "kusur haritası → 𝒪₂₈ Tashih"),
    28: Uzuv("nefs.melekeler", "şartlı tashih (ölçerek kabul)"),
    29: Uzuv("matematik.fitrat", "tevafuk ölçüsü + fazla sayma → müteber şahit"),
    30: Uzuv("nefs.sahit", "küllî kaide (nakzedilmiş şahit hariç) + taklit ayırımı"),
    31: Uzuv("nefs.melekeler", "Monte Carlo âkıbet riski → 𝒪₃₃ mîzân"),
    32: Uzuv("matematik.mizan", "ardışıklık kaidesi ``(k+α)/(n+α+β)`` → makam, sükût"),
    33: Uzuv("nefs.melekeler", "mizan ve rejim değişimi"),
    34: Uzuv("nefs.melekeler", "tafsil dalları → 𝒪₃₇ Fesâhat"),
    35: Uzuv("nefs.melekeler", "siyak-sibak muradı → 𝒪₃₉ Belâgat"),
    36: Uzuv("nefs.melekeler", "şartlı te'vil (iki şart)"),
    37: Uzuv("nefs.melekeler", "fesâhat + **sükût kapısı**"),
    38: Uzuv("nefs.melekeler", "talâkat düzleştirmesi"),
    39: Uzuv("nefs.melekeler", "muktezâ-yı hâl"),
    40: Uzuv("nefs.melekeler", "simetrik harmoni + altın oran → kelam ölçeği (𝒪₄₁)"),
    41: Uzuv("matematik.mizan", "``yakin_zinciri`` ile burhân kuvveti"),
}

# Sofrada geçen harici modüllerin, ``nefs/`` içinde fiilen ithal edilmesi
# beklenir. ``nefs.*`` kendi içindedir; denetim onları aramaz.
#: **BAYAT ADLAR DÜZELTİLDİ (ferman turu).** Sofra dört satırda
#: ``mizan.munazara``, ``mizan.istikra`` ve ``fitrat.tevafuk`` diyordu;
#: o paketler ``matematik/`` altına taşınalı çok olmuştu ve denetim
#: haklı olarak "bildiriyor fakat ithal edilmiyor" diye şikâyet
#: ediyordu. Şikâyet doğruydu, **kod değil sofra bayattı**: ilgili
#: kabiliyetler ``nefs/mantik.py`` (``matematik.mizan``) ve
#: ``nefs/musahede.py`` (``matematik.fitrat``) içinde fiilen ithal
#: ediliyor. Şikâyeti susturmak için denetimi gevşetmek yerine tabloyu
#: hakikate uydurdum.
_HARICI = ("matematik.", "fitrat.", "mizan.", "ogrenme.", "akis.",
           "hesap.", "kuantum.", "arama.", "yaklasim.", "olcek.",
           "omega_kategori_nbe.", "token_uzaylari.", "reel.")


# =====================================================================
def _nefs_kaynagi() -> str:
    """``nefs/`` altındaki bütün kaynağın birleşimi."""
    return "\n".join(y.read_text(encoding="utf-8")
                     for y in sorted(_NEFS.glob("*.py"))
                     if y.name not in ("akit.py", "test_nefs.py"))


def _ithal_edilenler(kaynak: Optional[str] = None) -> Set[str]:
    """``nefs/`` içinde fiilen ithal edilen harici modüller."""
    kaynak = _nefs_kaynagi() if kaynak is None else kaynak
    bulunan: Set[str] = set()
    for m in re.finditer(r"^\s*from\s+([\w.]+)\s+import", kaynak, re.M):
        bulunan.add(m.group(1))
    for m in re.finditer(r"^\s*import\s+([\w.]+)", kaynak, re.M):
        bulunan.add(m.group(1))
    return bulunan


def envanter() -> List[Dict[str, object]]:
    """Sözleşme + uzuv, tek tablo. Makinece okunur; belge değildir."""
    satirlar: List[Dict[str, object]] = []
    for m in melekeler():
        u = UZUV_SOFRASI.get(m.no)
        satirlar.append({
            "no": m.no,
            "ad": m.ad,
            "okur": tuple(m.okur),
            "yazar": tuple(m.yazar),
            "ihtiyari": tuple(m.ihtiyari),
            "modül": u.modul if u else None,
            "kabiliyet": u.kabiliyet if u else None,
            "vekil": bool(u.vekil) if u else True,
            "not": u.not_ if u else "sofrada kaydı yok",
            "yazmıyor": len(m.yazar) == 0,
        })
    return satirlar


def vekil_kalanlar() -> List[int]:
    """Hâlâ vekil formülle çalışan melekeler -- kütük H8'in sayacı."""
    return [s["no"] for s in envanter() if s["vekil"]]


def yazmayanlar() -> List[int]:
    """Veri yoluna hiçbir şey yazmayan melekeler.

    Bunlar akışta koşar, hesap yapar, günlüğe yazar ve **tesirsiz**
    kalır: düşürüldüklerinde netice değişmez. Nizamnamenin 4. kademesi
    tam olarak bunu hedef alır.
    """
    return [s["no"] for s in envanter() if s["yazmıyor"]]


def akdi_denetle() -> Tuple[bool, List[str]]:
    """Sofra ile kod uyuşuyor mu?

    Üç şey aranır:

    1. Sicildeki her meleke sofrada var mı (ve tersi)?
    2. Sofrada bildirilen **harici** modül ``nefs/`` içinde fiilen ithal
       ediliyor mu? (Belgede var, kodda yok -- en tehlikeli hâl.)
    3. ``yazar`` bildiren meleke, o alanı yazacak mı? Bu ``Meleke.kosu``
       tarafından zaten her adımda denetleniyor; burada yalnız akdin
       boş olmadığı bildirilir.
    """
    hatalar: List[str] = []
    s = sicil()
    for no in s:
        if no not in UZUV_SOFRASI:
            hatalar.append("𝒪%d sofrada yok" % no)
    for no in UZUV_SOFRASI:
        if no not in s:
            hatalar.append("sofrada olan 𝒪%d sicilde yok" % no)

    ithal = _ithal_edilenler()
    for no, u in sorted(UZUV_SOFRASI.items()):
        if not u.modul.startswith(_HARICI):
            continue
        kok = u.modul
        if not any(x == kok or x.startswith(kok + ".") for x in ithal):
            hatalar.append("𝒪%d '%s' modülünü bildiriyor fakat nefs/ "
                           "içinde ithal edilmiyor" % (no, kok))
    return (not hatalar), hatalar


# =====================================================================
def rapor() -> str:
    satir = ["=== Kademe 1: envanter ve arayüz akdi ==="]
    gecerli, hatalar = akdi_denetle()
    satir.append("akit geçerli: %s" % gecerli)
    satir += ["  ! " + h for h in hatalar]
    satir.append("")
    satir.append("%-4s %-18s %-24s %-22s %s"
                 % ("𝒪", "ad", "yazar", "modül", "hâl"))
    satir.append("-" * 92)
    for s in envanter():
        hal = "VEKİL" if s["vekil"] else "uzuv"
        if s["yazmıyor"]:
            hal += " · yazmıyor"
        satir.append("%-4d %-18s %-24s %-22s %s"
                     % (s["no"], s["ad"],
                        ",".join(s["yazar"]) or "—",
                        s["modül"] or "—", hal))
    v, y = vekil_kalanlar(), yazmayanlar()
    satir.append("")
    satir.append("vekil kalan: %d  %s" % (len(v), v))
    satir.append("veri yoluna yazmayan: %d  %s" % (len(y), y))
    return "\n".join(satir)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
