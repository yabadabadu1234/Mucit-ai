import ast
import multiprocessing
import re
from typing import Any, List, Optional, Tuple

from arc_veri import Cift, Grid

_KOD_BLOK_DESENI = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL)

_IZIN_VERILEN_MODULLER = frozenset({"math", "itertools", "collections", "functools"})


def kodu_metinden_cikar(model_ciktisi: str) -> Optional[str]:

    en_iyi = None
    for eslesme in _KOD_BLOK_DESENI.finditer(model_ciktisi):
        aday = eslesme.group(1)
        if "def transform" in aday:
            en_iyi = aday
    return en_iyi


def _guvenli_mi(kod: str) -> bool:
    try:
        agac = ast.parse(kod)
    except SyntaxError:
        return False

    for dugum in ast.walk(agac):
        if isinstance(dugum, (ast.Import, ast.ImportFrom)):
            modul_adlari = (
                [a.name.split(".")[0] for a in dugum.names]
                if isinstance(dugum, ast.Import)
                else [dugum.module.split(".")[0]] if dugum.module else []
            )
            if any(m not in _IZIN_VERILEN_MODULLER for m in modul_adlari):
                return False
        if isinstance(dugum, ast.Call) and isinstance(dugum.func, ast.Name):
            if dugum.func.id in ("eval", "exec", "open", "__import__", "compile"):
                return False
        if isinstance(dugum, ast.Attribute) and dugum.attr.startswith("__"):
            return False

    return True


def _izole_calistir(kod: str, grid: Grid, kuyruk: "multiprocessing.Queue") -> None:
    isimlendirme_alani: dict = {}
    try:
        exec(kod, {"__builtins__": {
            "range": range, "len": len, "list": list, "dict": dict, "set": set,
            "min": min, "max": max, "sum": sum, "enumerate": enumerate, "zip": zip,
            "sorted": sorted, "reversed": reversed, "abs": abs, "int": int, "float": float,
            "bool": bool, "str": str, "tuple": tuple, "map": map, "filter": filter,
            "any": any, "all": all, "isinstance": isinstance, "ValueError": ValueError,
            "IndexError": IndexError, "KeyError": KeyError, "TypeError": TypeError,
            "iter": iter, "next": next, "StopIteration": StopIteration, "round": round,
            "frozenset": frozenset, "divmod": divmod, "pow": pow,
        }}, isimlendirme_alani)
        transform_fn = isimlendirme_alani.get("transform")
        if transform_fn is None:
            kuyruk.put(("hata", "transform fonksiyonu tanımlanmamış"))
            return
        sonuc = transform_fn([list(satir) for satir in grid])
        kuyruk.put(("basari", sonuc))
    except Exception as exc:
        kuyruk.put(("hata", str(exc)))


def kodu_guvenle_calistir(kod: str, grid: Grid, zaman_asimi_sn: float = 5.0) -> Tuple[bool, Any]:

    if not _guvenli_mi(kod):
        return False, "kod güvenlik denetiminden geçemedi (yasak import/eval/exec/dunder)"

    kuyruk: multiprocessing.Queue = multiprocessing.Queue()
    surec = multiprocessing.Process(target=_izole_calistir, args=(kod, grid, kuyruk))
    surec.start()
    surec.join(timeout=zaman_asimi_sn)

    if surec.is_alive():
        surec.terminate()
        surec.join()
        return False, f"zaman aşımı ({zaman_asimi_sn} sn)"

    if kuyruk.empty():
        return False, "alt süreç sonuç döndürmeden sonlandı"

    durum, sonuc = kuyruk.get()
    return (durum == "basari"), sonuc


def kodu_egitim_ornekleriyle_dogrula(kod: str, train_ciftleri: List[Cift]) -> bool:

    if not train_ciftleri:
        return False
    for girdi, beklenen_cikti in train_ciftleri:
        basarili, sonuc = kodu_guvenle_calistir(kod, girdi)
        if not basarili or sonuc != beklenen_cikti:
            return False
    return True
