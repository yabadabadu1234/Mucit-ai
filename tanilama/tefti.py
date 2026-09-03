"""
TEFTİŞ -- padişahın **fiilen koşturduğu** her fonksiyon, dosyasıyla beraber.

===================================================================
NİÇİN VAR: İÇE AKTARMA BAĞLAMA DEĞİLDİR
===================================================================

Kullanıcı hükmü ve **haklıdır**:

> *"Padişahın modelin kendisi olduğunu unutmamalısın. Sadece içe aktarıp
> rapor verdirmek o kodları padişaha bağladığını göstermez… Padişahın
> kendi kodunu okuyacaksın, karşılaştığın her bir fonksiyonu not
> alacaksın, o fonksiyonların hangi dosyalardan olduğunu not alacaksın.
> Hiç notuna girmemiş dosyayı bağlamamışsın demektir."*

`nefs/divan.py` (H123) bir **içe aktarma** kapanışı kuruyordu ve
`tanilama/nizam.py` de onu ölçüyordu. İkisi de doğru şeyi ölçüyor
fakat **yanlış şeyi**: bir modülün yüklenmesi, padişahın onu
çalıştırdığını göstermez. ``import x`` yazıp "bağladım" demek, kütük
H96'nın (*"uzuv olmadıysa at değil, uzuv hâline getir"*) etrafından
dolaşmaktır.

Burada ölçülen şey **icra**dır: padişah koşarken hangi dosyadan hangi
fonksiyon **fiilen çağrıldı**. Tahmin yok, ``ast`` yok, içe aktarma
yok -- ``sys.setprofile`` ile canlı kayıt.

===================================================================
NE DÖNER
===================================================================

* ``kosan``     -- ``(dosya, fonksiyon)`` çiftleri: fiilen çağrılanlar.
* ``kosan_dosya`` -- en az bir fonksiyonu koşan dosyalar.
* ``olu_dosya`` -- kod tabanında olup **hiç** çağrılmayan dosyalar.
  Bunlar padişaha bağlı DEĞİLDİR; ``import`` edilmiş olmaları bir şey
  değiştirmez.
* ``atlanan_fonksiyon`` -- koşan dosyalarda tanımlı olup çağrılmayanlar.

===================================================================
HUDUT -- açıkça
===================================================================

Tek bir koşu, kodun **o koşuda** geçtiği yolu gösterir; başka bir
girdi başka dalları uyandırabilir. Onun için teftiş hem **eğitim**
hem **çıkarım** yolunu koşturur ve neticeler birleştirilir. Yine de
"bu fonksiyon hiç çalışmıyor" demek yerine "bu koşularda çalışmadı"
denir; fark mühimdir ve korunur.
"""
from __future__ import annotations

import ast
import io
import os
import sys
from typing import Dict, List, Optional, Sequence, Set, Tuple

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Teftişte **hariç** tutulan dizinler -- kütük H113 ile aynı gerekçe.
HARIC = ("docs", "mucit_ai_esas", os.path.join("idrak", "veri"))

__all__ = ["KOK", "izle", "tanimli_fonksiyonlar", "tefti_et", "rapor"]


def _bizim_mu(yol: str) -> bool:
    if not yol or not yol.startswith(KOK):
        return False
    b = os.path.relpath(yol, KOK)
    if b.startswith(".") or os.sep + "." in b:
        return False
    return not any(b == h or b.startswith(h + os.sep) for h in HARIC)


def izle(fn, *a, **k) -> Tuple[object, Set[Tuple[str, str]]]:
    """``fn``i koştur ve **çağrılan her fonksiyonu** kaydet.

    ``sys.setprofile`` kullanılır (``settrace`` değil): satır satır
    değil **çağrı** seviyesinde tetiklenir, yani yavaşlatması kat kat
    azdır ve bize lazım olan zaten çağrıdır.
    """
    gorulen: Set[Tuple[str, str]] = set()

    def profil(cerceve, olay, arg):
        if olay not in ("call", "c_call"):
            return
        try:
            kod = cerceve.f_code
            yol = kod.co_filename
        except AttributeError:
            return
        if _bizim_mu(yol):
            gorulen.add((os.path.relpath(yol, KOK), kod.co_name))

    eski = sys.getprofile()
    sys.setprofile(profil)
    try:
        netice = fn(*a, **k)
    finally:
        sys.setprofile(eski)
    return netice, gorulen


def tanimli_fonksiyonlar() -> Dict[str, Set[str]]:
    """Kod tabanındaki her dosyanın tanımladığı fonksiyon adları."""
    out: Dict[str, Set[str]] = {}
    for kok, dizinler, dosyalar in os.walk(KOK):
        dizinler[:] = [d for d in dizinler
                       if not d.startswith((".", "__"))]
        for d in dosyalar:
            if not d.endswith(".py"):
                continue
            tam = os.path.join(kok, d)
            if not _bizim_mu(tam):
                continue
            bagil = os.path.relpath(tam, KOK)
            try:
                agac = ast.parse(io.open(tam, encoding="utf-8").read())
            except Exception:                                # noqa: BLE001
                continue
            adlar: Set[str] = set()
            for dugum in ast.walk(agac):
                if isinstance(dugum, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    adlar.add(dugum.name)
            out[bagil] = adlar
    return out


def tefti_et(kisa: bool = True) -> Dict[str, object]:
    """Padişahı koştur ve neyin çalıştığını kaydet.

    İki yol da koşturulur ve birleştirilir:

    * **eğitim** -- `nefs/kulli_egitim.py`, en kısa ayarla,
    * **çıkarım** -- aynı motorun değerlendirme yolu (ARC görevleri).

    ``kisa=True`` iken ayar ``KISA_CPU``dur; maksat kapsamı görmek,
    netice almak değil.
    """
    from nefs.kulli_egitim import KISA_CPU, KulliEgitim

    ayar = KISA_CPU
    gor: Set[Tuple[str, str]] = set()
    yollar: Dict[str, int] = {}

    # 1) EĞİTİM yolu -- padişahın kendisi (`ogrenme/kaggle_donanim.py::kos` bunu çağırır).
    E = KulliEgitim(ayar)
    _, g1 = izle(E.kos)
    gor |= g1
    yollar["eğitim"] = len(g1)

    # 2) ÇIKARIM yolu -- **ayrıca** koşulur. Eğitimin içindeki
    #    değerlendirme kısa tutulduğu için müdrike çevriminin bütün
    #    dalları orada uyanmaz; burada ARC görevleriyle doğrudan
    #    koşturulur. Şerh bunu vaat ediyordu, artık icra da ediyor.
    try:
        from nefs.qegitim import degerlendir
        _, g2 = izle(degerlendir, E.nefs, E.dogrulama, azami=6,
                     pencere=ayar.pencere, sozluk=ayar.sozluk)
        gor |= g2
        yollar["çıkarım"] = len(g2)
    except Exception as e:                                   # noqa: BLE001
        yollar["çıkarım_hatası"] = 0
        print("ÇIKARIM yolu koşturulamadı: %s" % e, file=sys.stderr)

    tanimli = tanimli_fonksiyonlar()
    kosan_dosya = {d for d, _ in gor}
    butun_dosya = set(tanimli)
    olu = sorted(butun_dosya - kosan_dosya)

    atlanan: Dict[str, List[str]] = {}
    for d in sorted(kosan_dosya):
        cagrilan = {f for dd, f in gor if dd == d}
        eksik = sorted(tanimli.get(d, set()) - cagrilan)
        if eksik:
            atlanan[d] = eksik
    return {
        "kosan": sorted(gor),
        "kosan_dosya": sorted(kosan_dosya),
        "olu_dosya": olu,
        "atlanan_fonksiyon": atlanan,
        "toplam_dosya": len(butun_dosya),
        "yollar": yollar,
    }


def rapor(kisa: bool = True) -> str:
    r = tefti_et(kisa)
    kd, od = len(r["kosan_dosya"]), len(r["olu_dosya"])
    s = ["=== TEFTİŞ -- padişahın FİİLEN koşturduğu kod ===",
         "",
         "İçe aktarma bağlama değildir. Burada ölçülen şey icradır:",
         "padişah koşarken hangi dosyadan hangi fonksiyon çağrıldı.",
         "",
         "  kod tabanındaki dosya : %d" % r["toplam_dosya"],
         "  KOŞAN dosya           : %d  (%%%.1f)"
         % (kd, 100.0 * kd / max(r["toplam_dosya"], 1)),
         "  ÖLÜ dosya             : %d  (%%%.1f)  ← padişaha BAĞLI DEĞİL"
         % (od, 100.0 * od / max(r["toplam_dosya"], 1)),
         "  çağrılan fonksiyon    : %d" % len(r["kosan"]),
         "  yol başına çağrı      : %s"
         % ", ".join("%s=%d" % (k, v) for k, v in r["yollar"].items()),
         "",
         "ÖLÜ DOSYALAR (üst dizine göre):"]
    grup: Dict[str, List[str]] = {}
    for d in r["olu_dosya"]:
        grup.setdefault(d.split(os.sep)[0], []).append(d)
    for k in sorted(grup, key=lambda x: -len(grup[x])):
        s.append("  %-20s %2d : %s"
                 % (k, len(grup[k]),
                    ", ".join(os.path.basename(x) for x in grup[k])))
    s += ["",
          "KOŞAN DOSYALARDA ATLANAN FONKSİYONLAR (ilk 12 dosya):"]
    for d in sorted(r["atlanan_fonksiyon"],
                    key=lambda x: -len(r["atlanan_fonksiyon"][x]))[:12]:
        e = r["atlanan_fonksiyon"][d]
        s.append("  %-34s %2d atlandı" % (d, len(e)))
    s += ["",
          "HUDUT: tek koşu, kodun O KOŞUDA geçtiği yolu gösterir.",
          "'Bu fonksiyon hiç çalışmıyor' değil, 'bu koşuda çalışmadı'",
          "denir; fark mühimdir."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
