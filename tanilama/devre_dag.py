from __future__ import annotations

import ast
import os
from dataclasses import dataclass
from typing import List, Tuple

__all__ = ["Dallanma", "KAPI_CAGRILARI", "OLCUM_ISARETLERI", "tara", "rapor"]

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KAPI_CAGRILARI = frozenset({"tek", "cift", "harman"})
OLCUM_ISARETLERI = ("psi", "olcum", "argmax", "entropi", "oku")


@dataclass
class Dallanma:

    meleke: str
    satir: int
    kosul: str


def _kosulda_olcum_var_mi(test: ast.AST) -> bool:
    kaynak = ast.dump(test)
    return any(isaret in kaynak for isaret in OLCUM_ISARETLERI)


def _govdede_kapi_cagrisi_var_mi(govde: List[ast.AST]) -> bool:
    for dugum in govde:
        for alt in ast.walk(dugum):
            if (isinstance(alt, ast.Call)
                    and isinstance(alt.func, ast.Attribute)
                    and alt.func.attr in KAPI_CAGRILARI):
                return True
    return False


def tara(kaynak_dosyasi: str = "nefs/melekeler.py"
        ) -> Tuple[Tuple[Dallanma, ...], int]:
    yol = os.path.join(KOK, kaynak_dosyasi)
    with open(yol, "r", encoding="utf-8") as fh:
        agac = ast.parse(fh.read(), filename=yol)
    bulunan: List[Dallanma] = []
    taranan_meleke = 0
    for dugum in ast.walk(agac):
        if not isinstance(dugum, ast.ClassDef):
            continue
        for uye in dugum.body:
            if not (isinstance(uye, ast.FunctionDef) and uye.name == "uygula"):
                continue
            taranan_meleke += 1
            for ic in ast.walk(uye):
                if not isinstance(ic, ast.If):
                    continue
                if (_kosulda_olcum_var_mi(ic.test)
                        and _govdede_kapi_cagrisi_var_mi(ic.body)):
                    bulunan.append(Dallanma(
                        meleke=dugum.name, satir=int(ic.lineno),
                        kosul=ast.unparse(ic.test)))
    return tuple(bulunan), taranan_meleke


def rapor(kaynak_dosyasi: str = "nefs/melekeler.py") -> str:
    bulunan, taranan_meleke = tara(kaynak_dosyasi)
    s = ["=== DEVRE DAG DENETİMİ (adaptif geri-besleme taraması) ===", "",
         "  Aranan: bir meleke.uygula() içinde, TUR-İÇİ ölçüme/psi'ye bakıp",
         "  HANGİ kapının vurulacağına karar veren bir dallanma -- devre",
         "  sabit-derinlikli, ileri-yönlü (DAG) kalmalı.", ""]
    if not bulunan:
        s.append("  BULUNAN: 0 -- devre ADAPTİF DEĞİL (%d meleke tarandı)"
                  % taranan_meleke)
    else:
        s.append("  BULUNAN: %d -- aşağıdakiler adaptif geri-besleme "
                  "içeriyor, DAG kısıtı ihlâl edildi:" % len(bulunan))
        for d in bulunan:
            s.append("    %s:%d  if %s" % (d.meleke, d.satir, d.kosul))
    return "\n".join(s)
