from __future__ import annotations

import ast
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

__all__ = ["Sabit", "KOK", "ATLANAN", "tara", "ozet", "rapor"]

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ATLANAN = frozenset({0, 1, -1, 2, -2, 0.0, 1.0, -1.0, 2.0, 0.5})

_HARIC = ("__pycache__", ".git", "depo", "yedek")

_KOD_DEGIL = (os.path.join("idrak", "veri"), "docs")


@dataclass
class Sabit:

    dosya: str
    satir: int
    kap: str
    ad: str
    deger: str
    cins: str
    serh: bool


def _deger(d: ast.AST) -> Optional[str]:
    if isinstance(d, ast.Constant) and isinstance(
            d.value, (int, float, str, bool)) and not isinstance(
            d.value, bool):
        return repr(d.value)
    if isinstance(d, ast.UnaryOp) and isinstance(d.op, ast.USub):
        i = _deger(d.operand)
        return None if i is None else "-" + i
    if isinstance(d, (ast.Tuple, ast.List)):
        parcalar = [_deger(x) for x in d.elts]
        if all(x is not None for x in parcalar):
            return "(" + ", ".join(p for p in parcalar if p) + ")"
    if isinstance(d, ast.Call):
        f = getattr(d.func, "id", None) or getattr(d.func, "attr", None)
        if f in ("field", "frozenset", "dict"):
            return f + "(…)"
    return None


def _sayi_mi(d: ast.AST) -> bool:
    if isinstance(d, ast.Constant) and isinstance(d.value, (int, float)):
        return not isinstance(d.value, bool) and d.value not in ATLANAN
    if isinstance(d, ast.UnaryOp) and isinstance(d.op, ast.USub):
        return _sayi_mi(d.operand)
    return False


def _dosyalar(alt: Optional[str] = None) -> List[str]:
    out: List[str] = []
    kok = os.path.join(KOK, alt) if alt else KOK
    for dizin, alt_dizinler, adlar in os.walk(kok):
        alt_dizinler[:] = [d for d in alt_dizinler if d not in _HARIC]
        for ad in sorted(adlar):
            if not ad.endswith(".py") or ad.startswith("test_"):
                continue
            yol = os.path.join(dizin, ad)
            bagil = os.path.relpath(yol, KOK)
            if any(bagil.startswith(x) for x in _KOD_DEGIL):
                continue
            out.append(yol)
    return sorted(out)


def tara(alt: Optional[str] = None) -> List[Sabit]:
    cikti: List[Sabit] = []
    for yol in _dosyalar(alt):
        bagil = os.path.relpath(yol, KOK)
        kaynak = open(yol, encoding="utf-8").read()
        satirlar = kaynak.split("\n")
        agac = ast.parse(kaynak, filename=bagil)

        def serhli(no: int) -> bool:
            i = no - 2
            while i >= 0 and satirlar[i].strip().startswith("#"):
                return True
            return False

        def gez(dugum: ast.AST, kap: str, sinif: bool) -> None:
            for c in ast.iter_child_nodes(dugum):
                if isinstance(c, ast.ClassDef):
                    gez(c, c.name, True)
                elif isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for arg, var in zip(
                            c.args.args[len(c.args.args)
                                        - len(c.args.defaults):],
                            c.args.defaults):
                        if _sayi_mi(var):
                            cikti.append(Sabit(
                                bagil, var.lineno, c.name, arg.arg,
                                _deger(var) or "?", "İLAN", False))
                    gez(c, ("%s.%s" % (kap, c.name)) if kap else c.name,
                        False)
                elif isinstance(c, (ast.Assign, ast.AnnAssign)):
                    hedefler = ([c.target] if isinstance(c, ast.AnnAssign)
                                else c.targets)
                    d = c.value
                    for t in hedefler:
                        ad = getattr(t, "id", None)
                        if ad is None or ad.startswith("__"):
                            continue
                        v = _deger(d) if d is not None else None
                        if sinif:
                            if v is not None:
                                cikti.append(Sabit(bagil, c.lineno, kap, ad,
                                                   v, "AYARDA",
                                                   serhli(c.lineno)))
                        elif ad.isupper():
                            if v is not None:
                                cikti.append(Sabit(bagil, c.lineno, kap, ad,
                                                   v, "İLAN",
                                                   serhli(c.lineno)))
                        elif kap and d is not None and _sayi_mi(d):
                            cikti.append(Sabit(bagil, c.lineno, kap, ad,
                                               _deger(d) or "?", "GÖMÜLÜ",
                                               serhli(c.lineno)))
                    gez(c, kap, False)
                elif isinstance(c, ast.Compare) and kap:
                    for k in c.comparators:
                        if _sayi_mi(k):
                            cikti.append(Sabit(bagil, k.lineno, kap,
                                               "(kıyas eşiği)",
                                               _deger(k) or "?", "GÖMÜLÜ",
                                               False))
                    gez(c, kap, False)
                else:
                    gez(c, kap, sinif)

        gez(agac, "", False)
    return cikti


def ozet(alt: Optional[str] = None) -> Dict[str, Any]:
    s = tara(alt)
    say = {"AYARDA": 0, "İLAN": 0, "GÖMÜLÜ": 0}
    for x in s:
        say[x.cins] += 1
    dosya: Dict[str, int] = {}
    for x in s:
        if x.cins == "GÖMÜLÜ":
            dosya[x.dosya] = dosya.get(x.dosya, 0) + 1
    return {"sabit": s, "sayım": say,
            "gömülü_dosya": sorted(dosya.items(), key=lambda t: -t[1])}


def rapor(alt: Optional[str] = None, hadd: int = 60) -> str:
    o = ozet(alt)
    s: List[Sabit] = o["sabit"]
    say = o["sayım"]
    y = ["=== SABİT TEFTİŞİ -- elle tayin edilmiş her sayı ===", "",
         "  AYARDA : %4d   (dataclass alanı -- dışarıdan değiştirilebilir)"
         % say["AYARDA"],
         "  İLAN   : %4d   (modül sabiti / varsayılan argüman -- görünür)"
         % say["İLAN"],
         "  GÖMÜLÜ : %4d   (fonksiyon gövdesinde çıplak -- **TEHLİKELİ**)"
         % say["GÖMÜLÜ"], ""]

    y.append("  --- 1. AYARDA (meşru; değeri değiştirilebilir) ---")
    ayar_kap: Dict[str, List[Sabit]] = {}
    for x in s:
        if x.cins == "AYARDA":
            ayar_kap.setdefault("%s :: %s" % (x.dosya, x.kap), []).append(x)
    for k in sorted(ayar_kap):
        y.append("    %s" % k)
        for x in ayar_kap[k]:
            y.append("      %-24s = %-22s %s"
                     % (x.ad, x.deger[:22], "şerhli" if x.serh else "ŞERHSİZ"))
    y.append("")

    y.append("  --- 2. İLAN (modül sabiti; koda gömülü fakat görünür) ---")
    for x in s:
        if x.cins == "İLAN" and x.ad.isupper():
            y.append("    %-34s %-22s %s:%d"
                     % (x.ad, x.deger[:22], x.dosya, x.satir))
    y.append("")

    y.append("  --- 3. GÖMÜLÜ (en tehlikeli; dosya dosya sayım) ---")
    for dosya, kac in o["gömülü_dosya"][:20]:
        y.append("    %-40s %4d" % (dosya, kac))
    y.append("")
    y.append("  --- GÖMÜLÜ SABİTLERİN İLK %d TANESİ ---" % hadd)
    n = 0
    for x in s:
        if x.cins != "GÖMÜLÜ":
            continue
        n += 1
        if n > hadd:
            break
        y.append("    %-30s %-18s %-16s %s:%d"
                 % (x.kap[:30], x.ad[:18], x.deger[:16], x.dosya, x.satir))
    return "\n".join(y)


if __name__ == "__main__":
    import sys
    print(rapor(sys.argv[1] if len(sys.argv) > 1 else None))
