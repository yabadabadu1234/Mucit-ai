"""
Ajanin cagirabilecegi araclar (tools). Ajan HICBIR aracdan mahrum
birakilmaz: her donusumde execute_python VE submit_answer ikisi de
mevcuttur, sistem promptunda daima ikisi birden listelenir.

submit_answer (cevap verme araci): cagrildiginda cevabi okur ve kaydeder.
Eger izgaranin her satirinda FARKLI SAYIDA sutun varsa (tutarsiz sekil) bu
BARIZ BIR HATADIR; boyutlari kendimiz esitlemeye KALKMAYIZ (izgaranin
boyutu bulmacadan bulmacaya degisebilir, ama kendi icinde HER ZAMAN tutarli
olmalidir). Boyle bir hata varsa arac, ajana devam etmesi icin sebebiyle
birlikte bir hata mesaji doner; ajan bu mesaji gorup tekrar dener.
"""
import json
import re
from typing import Any, Dict, List, Optional, Tuple

TOOL_TANIMLARI: List[Dict[str, Any]] = [
    {
        "name": "execute_python",
        "description": "Execute a Python snippet (standard library only) and return its stdout/result.",
        "arguments": {"code": {"type": "string"}},
    },
    {
        "name": "submit_answer",
        "description": (
            "Submit your final answer grid for the current test input. The grid must be a "
            "rectangular 2D array of integers 0-9: every row must have the SAME number of "
            "columns as every other row in THIS grid (the shape itself may be anything, and "
            "may differ from the train examples' shapes, but it must be internally consistent)."
        ),
        "arguments": {"grid": {"type": "array", "items": {"type": "array", "items": {"type": "integer"}}}},
    },
]


def tool_tanimlari_json_metni() -> str:
    return json.dumps(TOOL_TANIMLARI, ensure_ascii=False)


_JSON_BLOK_DESENI = re.compile(r"```json\s*\n(.*?)```", re.DOTALL)
_TOOL_CALL_ETIKET_DESENI = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.DOTALL)


def _dengeli_ciplak_json_adaylarini_bul(metin: str) -> List[str]:
    """Çıplak (```json ``` ya da <tool_call> ile SARILMAMIŞ) bir JSON
    nesnesini metin içinde bulur. ESKİ regex (`\\{[^{}]*"name"...[^{}]*\\}`)
    süslü parantez İÇİNDE süslü parantez OLAMAZ varsayıyordu -- ama GERÇEK
    her araç çağrısının "arguments" alanı da bir nesnedir
    (`{"name": "submit_answer", "arguments": {"grid": [[1,1]]}}`), yani
    HER çıplak araç çağrısı en az BİR İÇ İÇE süslü parantez içerir. Bu
    yüzden eski regex ÇIPLAK (fence'siz) HİÇBİR gerçek araç çağrısını asla
    eşleştiremiyordu -- kullanıcının paylaştığı gerçek Kaggle transkriptinde
    model tam olarak bu biçimde ("...}}}" ile biten, fence'siz) bir
    submit_answer çağrısı üretmiş ve "araç çağrısı bulunamadı" uyarısı
    almıştı; kök neden buydu. Python'ın `re` modülü keyfi derinlikte iç
    içe geçmeyi ifade EDEMEZ (recursion desteklemez), bu yüzden burada
    basit bir YIĞIN tabanlı (stack-based) parantez eşleştirici kullanılır
    -- ANY nesting derinliğini doğru bulur; sahte eşleşmeler zaten
    çağıran tarafta json.loads + "name" anahtarı kontrolüyle elenir."""
    adaylar: List[str] = []
    derinlik = 0
    baslangic: Optional[int] = None
    for i, karakter in enumerate(metin):
        if karakter == "{":
            if derinlik == 0:
                baslangic = i
            derinlik += 1
        elif karakter == "}":
            if derinlik > 0:
                derinlik -= 1
                if derinlik == 0 and baslangic is not None:
                    adaylar.append(metin[baslangic:i + 1])
                    baslangic = None
    return adaylar


def arac_cagrilarini_ayikla(model_ciktisi: str) -> List[Dict[str, Any]]:

    adaylar: List[str] = []
    adaylar += _TOOL_CALL_ETIKET_DESENI.findall(model_ciktisi)
    adaylar += _JSON_BLOK_DESENI.findall(model_ciktisi)
    if not adaylar:
        adaylar += _dengeli_ciplak_json_adaylarini_bul(model_ciktisi)

    cagrilar = []
    for aday in adaylar:
        try:
            veri = json.loads(aday.strip())
        except json.JSONDecodeError:
            continue
        if isinstance(veri, dict) and "name" in veri:
            cagrilar.append(veri)
    return cagrilar


def _izgara_tutarliligini_denetle(grid: Any) -> Tuple[bool, str]:

    # NOT (Turkce): bu mesajlar dogrudan model'e (tool_response olarak)
    # GERI BESLENIR -- model cogunlukla Ingilizce egitim verisiyle
    # calistigi icin bu metinler DAIMA Ingilizce olmali, aksi halde model
    # HATASININ NE OLDUGUNU ANLAYAMAZ ve kendini duzeltemez (kullanicinin
    # gercek Kaggle transkriptinde gozlemledigi -- gecersiz bir grid
    # gonderdikten sonra modelin donup dolasip ayni seyi tekrarladigi
    # cikmaz dongunun dogrudan sebeplerinden biri buydu).
    if not isinstance(grid, list) or not grid:
        return False, "Invalid: 'grid' must be a non-empty list of lists."

    satir_uzunluklari = []
    for i, satir in enumerate(grid):
        if not isinstance(satir, list) or not satir:
            return False, f"Invalid: row {i} is empty or is not a list."
        satir_uzunluklari.append(len(satir))

    farkli = sorted(set(satir_uzunluklari))
    if len(farkli) > 1:
        detay = ", ".join(
            f"row {i}: {n} columns" for i, n in enumerate(satir_uzunluklari) if n in farkli
        )
        return False, (
            f"Invalid: inconsistent row lengths ({detay}). "
            f"The grid's overall shape may differ from puzzle to puzzle, but WITHIN a single "
            f"grid every row must have the same number of columns. We will not fix the shape "
            f"for you; please re-check your rule and produce a consistent grid."
        )

    for i, satir in enumerate(grid):
        for j, hucre in enumerate(satir):
            if not isinstance(hucre, int) or not (0 <= hucre <= 9):
                return False, f"Invalid: [{i}][{j}] = {hucre!r} is not an integer between 0 and 9."

    return True, "Valid."


class CevapDefteri:
    """submit_answer ile kaydedilen son gecerli cevabi tutar."""

    def __init__(self) -> None:
        self.kaydedilen_cevap: Optional[List[List[int]]] = None
        self.deneme_gecmisi: List[Dict[str, Any]] = []


def submit_answer_arac(grid: Any, defter: CevapDefteri) -> Dict[str, Any]:
    # NOT (Turkce): bu sozlugun ANAHTARLARI da (asagida "success"/"error"
    # olarak) modele GERI BESLENIR -- "basarili"/"hata" gibi Turkce
    # anahtar adlari, Ingilizce egitim verisiyle calisan model icin
    # bilinmeyen/anlamsiz kelimeler olurdu. Anahtarlar da (deger metinleri
    # gibi) daima Ingilizce olmali.
    gecerli, mesaj = _izgara_tutarliligini_denetle(grid)
    defter.deneme_gecmisi.append({"grid": grid, "gecerli": gecerli, "mesaj": mesaj})
    if not gecerli:
        return {"success": False, "error": mesaj}

    defter.kaydedilen_cevap = grid
    return {"success": True, "message": "Answer recorded."}


def execute_python_arac(code: str) -> Dict[str, Any]:
    basarili, sonuc = kodu_guvenle_calistir_serbest(code)
    if not basarili:
        return {"success": False, "error": sonuc}
    return {"success": True, "result": sonuc}


def kodu_guvenle_calistir_serbest(kod: str) -> Tuple[bool, Any]:
    """execute_python araci icin: transform(grid) imzasi sart kosmadan,
    serbest bir kod parcasini ayni AST guvenlik/izolasyon rejimiyle
    calistirir (kod_ajani.py'deki izolasyon mekanizmasini yeniden kullanir)."""
    import builtins
    import multiprocessing

    from kod_ajani import _guvenli_mi

    if not _guvenli_mi(kod):
        return False, "code failed the security check (forbidden eval/exec/open/dunder)"

    def _calistir(kuyruk: "multiprocessing.Queue") -> None:
        ns: Dict[str, Any] = {}
        try:
            # Import kisitlamasi KALDIRILDI (kullanici talebiyle): kod zaten
            # izole bir alt surecte (5 sn zaman asimiyla) calisiyor, ana
            # makineye zarar verme ihtimali yok -- gercek `builtins.__import__`
            # kullanilarak model istedigi HERHANGI BIR modulu (numpy, scipy,
            # vs.) serbestce import edebiliyor.
            exec(kod, {"__builtins__": {
                "range": range, "len": len, "list": list, "dict": dict, "set": set,
                "min": min, "max": max, "sum": sum, "enumerate": enumerate, "zip": zip,
                "sorted": sorted, "reversed": reversed, "abs": abs, "int": int, "float": float,
                "bool": bool, "str": str, "tuple": tuple, "map": map, "filter": filter,
                "any": any, "all": all, "isinstance": isinstance, "print": print,
                "iter": iter, "next": next, "round": round, "frozenset": frozenset,
                "divmod": divmod, "pow": pow, "__import__": builtins.__import__,
            }}, ns)
            kuyruk.put(("basari", ns.get("sonuc", ns.get("result"))))
        except Exception as exc:
            kuyruk.put(("hata", str(exc)))

    kuyruk: multiprocessing.Queue = multiprocessing.Queue()
    surec = multiprocessing.Process(target=_calistir, args=(kuyruk,))
    surec.start()
    surec.join(timeout=5.0)
    if surec.is_alive():
        surec.terminate()
        surec.join()
        return False, "timeout (5.0 s)"
    if kuyruk.empty():
        return False, "subprocess exited without returning a result"
    durum, sonuc = kuyruk.get()
    return (durum == "basari"), sonuc


def arac_cagrisini_yurut(cagri: Dict[str, Any], defter: CevapDefteri) -> Dict[str, Any]:
    ad = cagri.get("name")
    args = cagri.get("arguments", {})
    if ad == "execute_python":
        return execute_python_arac(args.get("code", ""))
    if ad == "submit_answer":
        return submit_answer_arac(args.get("grid"), defter)
    return {"success": False, "error": f"Unknown tool: {ad}"}


def tool_response_mesaji_olustur(sonuc: Dict[str, Any]) -> str:
    return f"<tool_response>\n{json.dumps(sonuc, ensure_ascii=False)}\n</tool_response>"
