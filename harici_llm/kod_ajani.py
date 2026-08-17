import ast

# Import kisitlamasi KALDIRILDI (kullanici talebiyle): kod zaten izole bir
# alt surecte (multiprocessing.Process, 5 sn zaman asimi) calisiyor, ana
# makineye zarar verme ihtimali yok -- model istedigi HERHANGI BIR modulu
# (numpy, scipy, vs.) serbestce import edebilir.


def _guvenli_mi(kod: str) -> bool:
    # NOT (Turkce): gercek Kaggle kosusunda modelin uretttigi execute_python
    # cagrisinin "code" alani GECERLI JSON ama bir METIN DEGILSE (ornegin
    # {"code": {"ic": "ice"}} gibi bir nesne/liste/sayi) ast.parse(kod)
    # SyntaxError DEGIL TypeError firlatiyordu ("compile() arg 1 must be a
    # string, bytes or AST object") -- bu, YALNIZCA SyntaxError yakalanan
    # eski kodda YAKALANMADAN yukari firliyor, TUM 43 gorevlik SUREKLI
    # ADMISYON partisini (coklu_gpu.py'nin dis except'i partiyi TAMAMEN
    # bosa dusuruyor) coker hale getiriyordu -- tek bir bozuk arac cagrisi
    # yuzunden partideki DIGER gorevler de kaybediliyordu.
    if not isinstance(kod, str):
        return False
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
