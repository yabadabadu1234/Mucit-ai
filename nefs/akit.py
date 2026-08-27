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

from . import akil, beyan, idrak, murakabe  # noqa: F401  (sicili doldurur)
from .meleke import Meleke, melekeler, sicil

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
    1:  Uzuv("nefs.idrak", "FNO spektral ön-süzgeç + odak çekirdeği"),
    2:  Uzuv("nefs.idrak", "hissî suret kodlaması"),
    3:  Uzuv("nefs.idrak", "muhayyile serbestliği"),
    4:  Uzuv("nefs.sahit", "şahit bölütlemesi (kopma ölçüsü, MAD eşiği)"),
    5:  Uzuv("nefs.idrak", "Grassmann kesiti ``w ∈ ℳ`` + Betti sayıları"),
    6:  Uzuv("nefs.idrak", "tasavvur: mana uzayına geçiş"),
    7:  Uzuv("nefs.idrak", "vâhime çekirdeği"),
    8:  Uzuv("nefs.idrak", "SVD tahlili"),
    9:  Uzuv("nefs.idrak", "terkip"),
    10: Uzuv("nefs.idrak", "tezat kutbu → 𝒪₁₁ çelişki çekirdeği"),
    11: Uzuv("nefs.uzaylar", "çelişki çekirdeği ``C = −S(AᵀA)Sᵀ`` + ıslah"),
    12: Uzuv("nefs.akil", "üç başlıklı maliyet ve eleme"),
    13: Uzuv("nefs.akil", "tasdik mührü → ``d.hukum`` kaydı"),
    14: Uzuv("nefs.akil", "gaye"),
    15: Uzuv("nefs.akil", "sual"),
    16: Uzuv("nefs.akil", "taban çıkarmalı REINFORCE → Mutasarrıfa R_t (𝒪₂₁)"),
    17: Uzuv("nefs.akil", "Bayes ardılı → 𝒪₂₅ Teemmül önseli"),
    18: Uzuv("nefs.sahit", "şahit başına dik Procrustes kaidesi (kapalı form)"),
    19: Uzuv("nefs.akil", "sözde ters ile somut temsil → 𝒪₂₇ kusur ölçüsü"),
    20: Uzuv("nefs.akil", "vech-i şebeh → 𝒪₃₉ Belâgat"),
    21: Uzuv("nefs.akil", "tefekkür devri"),
    22: Uzuv("nefs.akil", "NOTEARS asiklik + arka kapı"),
    23: Uzuv("mizan.munazara", "nakz sınaması + Gazâlî yakîni (``min``)"),
    24: Uzuv("nefs.akil", "burhân zinciri"),
    25: Uzuv("nefs.murakabe", "büzücü devridaim + durma ölçütü"),
    26: Uzuv("nefs.murakabe", "asgarî arama + vakarla harman (S yazar)"),
    27: Uzuv("nefs.murakabe", "kusur haritası → 𝒪₂₈ Tashih"),
    28: Uzuv("nefs.murakabe", "şartlı tashih (ölçerek kabul)"),
    29: Uzuv("fitrat.tevafuk", "tevafuk ölçüsü + fazla sayma → müteber şahit"),
    30: Uzuv("nefs.sahit", "küllî kaide (nakzedilmiş şahit hariç) + taklit ayırımı"),
    31: Uzuv("nefs.murakabe", "Monte Carlo âkıbet riski → 𝒪₃₃ mîzân"),
    32: Uzuv("mizan.istikra", "ardışıklık kaidesi ``(k+α)/(n+α+β)`` → makam, sükût"),
    33: Uzuv("nefs.murakabe", "mizan ve rejim değişimi"),
    34: Uzuv("nefs.murakabe", "tafsil dalları → 𝒪₃₇ Fesâhat"),
    35: Uzuv("nefs.murakabe", "siyak-sibak muradı → 𝒪₃₉ Belâgat"),
    36: Uzuv("nefs.murakabe", "şartlı te'vil (iki şart)"),
    37: Uzuv("nefs.beyan", "fesâhat + **sükût kapısı**"),
    38: Uzuv("nefs.beyan", "talâkat düzleştirmesi"),
    39: Uzuv("nefs.beyan", "muktezâ-yı hâl"),
    40: Uzuv("nefs.beyan", "simetrik harmoni + altın oran → kelam ölçeği (𝒪₄₁)"),
    41: Uzuv("mizan.munazara", "``yakin_zinciri`` ile burhân kuvveti"),
}

# Sofrada geçen harici modüllerin, ``nefs/`` içinde fiilen ithal edilmesi
# beklenir. ``nefs.*`` kendi içindedir; denetim onları aramaz.
_HARICI = ("fitrat.", "mizan.", "ogrenme.", "akis.", "hesap.", "kuantum.",
           "arama.", "yaklasim.", "olcek.", "omega_kategori_nbe.",
           "token_uzaylari.", "reel.")


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
