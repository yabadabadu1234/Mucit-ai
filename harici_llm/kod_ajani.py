import ast

# NOT: modelin GERCEKTE urettigi kodun neredeyse tamami "import numpy as np"
# ile basliyor (bkz. transkript kayitlari) -- numpy eksikti, bu yuzden HER
# execute_python cagrisi AST asamasinda "yasak import" diye reddediliyordu.
_IZIN_VERILEN_MODULLER = frozenset({"math", "itertools", "collections", "functools", "numpy"})


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
