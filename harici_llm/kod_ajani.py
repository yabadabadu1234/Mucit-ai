import ast

# Import kisitlamasi KALDIRILDI (kullanici talebiyle): kod zaten izole bir
# alt surecte (multiprocessing.Process, 5 sn zaman asimi) calisiyor, ana
# makineye zarar verme ihtimali yok -- model istedigi HERHANGI BIR modulu
# (numpy, scipy, vs.) serbestce import edebilir.


def _guvenli_mi(kod: str) -> bool:
    try:
        agac = ast.parse(kod)
    except SyntaxError:
        return False

    for dugum in ast.walk(agac):
        if isinstance(dugum, ast.Call) and isinstance(dugum.func, ast.Name):
            if dugum.func.id in ("eval", "exec", "open", "compile"):
                return False
        if isinstance(dugum, ast.Attribute) and dugum.attr.startswith("__"):
            return False

    return True
