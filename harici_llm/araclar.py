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
    """submit_answer ile kaydedilen son gecerli cevabi tutar.

    `execute_python_basariyla_calisti_mi`: gerçek Kaggle transkriptlerinde
    tekrar tekrar görüldü -- model, kuralını train örnekleriyle HİÇ
    doğrulamadan (tek bir execute_python çağrısı bile yapmadan) doğrudan
    submit_answer'a atlıyor ve kendi "Final Rule Sentence"iyle çelişen bir
    grid gönderiyordu (bkz. sistem promptunun kendi 4. maddesi: "ALWAYS
    WORK BY CALLING TOOLS... use execute_python as many times as you need
    to write and test code that implements your rule against the train
    examples"). Bu artık yalnızca bir TELKİN değil, submit_answer_arac
    tarafından FİİLEN ZORUNLU kılınıyor (bkz. aşağıdaki kontrol)."""

    def __init__(self) -> None:
        self.kaydedilen_cevap: Optional[List[List[int]]] = None
        self.deneme_gecmisi: List[Dict[str, Any]] = []
        self.execute_python_basariyla_calisti_mi: bool = False


def submit_answer_arac(grid: Any, defter: CevapDefteri) -> Dict[str, Any]:
    # NOT (Turkce): bu sozlugun ANAHTARLARI da (asagida "success"/"error"
    # olarak) modele GERI BESLENIR -- "basarili"/"hata" gibi Turkce
    # anahtar adlari, Ingilizce egitim verisiyle calisan model icin
    # bilinmeyen/anlamsiz kelimeler olurdu. Anahtarlar da (deger metinleri
    # gibi) daima Ingilizce olmali.
    #
    # ZORUNLU DOGRULAMA: gercek Kaggle transkriptlerinde model, kuralini
    # train orneklerine karsi HIC test etmeden dogrudan (yanlis/tutarsiz
    # bir) cevap gonderiyordu. Sistem promptu zaten "execute_python'i
    # kuralini train ornekleriyle dogrulamak icin kullan" diyor ama bu
    # yalnizca bir TELKINDI, hicbir sey ZORUNLU KILMIYORDU. Simdi en az
    # BIR basarili execute_python cagrisi yapilmadan submit_answer
    # REDDEDILIR -- bu, kuralin dogru oldugunun KANITI degildir (model
    # yanlis bir dogrulama kodu da yazabilir), ama en azindan modeli HIC
    # DUSUNMEDEN/TEST ETMEDEN cevap gondermekten ALIKOYAR.
    if not defter.execute_python_basariyla_calisti_mi:
        mesaj = (
            "Rejected: you must call execute_python at least once, successfully, to test your "
            "rule against the train examples BEFORE calling submit_answer. Write code that "
            "applies your candidate rule to each train input and checks it against the real "
            "train output -- then call submit_answer once that check passes."
        )
        defter.deneme_gecmisi.append({"grid": grid, "gecerli": False, "mesaj": mesaj})
        return {"success": False, "error": mesaj}

    gecerli, mesaj = _izgara_tutarliligini_denetle(grid)
    defter.deneme_gecmisi.append({"grid": grid, "gecerli": gecerli, "mesaj": mesaj})
    if not gecerli:
        return {"success": False, "error": mesaj}

    defter.kaydedilen_cevap = grid
    return {"success": True, "message": "Answer recorded."}


def execute_python_arac(code: str, defter: Optional[CevapDefteri] = None) -> Dict[str, Any]:
    basarili, sonuc = kodu_guvenle_calistir_serbest(code)
    if defter is not None and basarili:
        defter.execute_python_basariyla_calisti_mi = True
    if not basarili:
        return {"success": False, "error": sonuc}
    return {"success": True, "result": sonuc}


def _json_uyumlu_yap(deger: Any) -> Any:
    """execute_python ile çalıştırılan (numpy'yi serbestçe kullanabilen)
    modelin ürettiği 'sonuc'/'result' değişkenini, JSON'a (transkript.py,
    tool_response) GÜVENLE yazılabilecek düz Python türlerine çevirir --
    numpy.ndarray/numpy skaler türleri GEÇERLİ JSON DEĞİLDİR ve json.dumps
    bunlarla TypeError fırlatır (kullanıcının gerçek Kaggle logunda gördüğü
    "Object of type ndarray is not JSON serializable" çökmesinin kök nedeni
    tam olarak buydu -- tek bir görevin numpy döndüren kodu, o görevin
    bulunduğu 65 görevlik SÜREKLİ ADMİSYON partisinin TAMAMINI çöktürüyordu)."""
    if hasattr(deger, "tolist"):  # numpy.ndarray ve numpy skaler türleri
        return _json_uyumlu_yap(deger.tolist())
    if isinstance(deger, dict):
        return {str(k): _json_uyumlu_yap(v) for k, v in deger.items()}
    if isinstance(deger, (list, tuple)):
        return [_json_uyumlu_yap(v) for v in deger]
    if deger is None or isinstance(deger, (bool, int, float, str)):
        return deger
    return str(deger)


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
        import io
        import os as _os
        import sys as _sys

        # NOT (Turkce): kullanicinin gercek Kaggle logunda sikayet ettigi
        # "ekrana basliksiz, manasiz garip seyler basiliyor" (ornegin
        # tekrar tekrar basilan sayi dizileri) -- kok neden: model uretilen
        # execute_python kodu icinde ozgurce print() cagirabiliyor
        # (asagida "print": print ile GERCEK builtin veriliyor), ve bu kod
        # AYRI bir OS surecinde (multiprocessing.Process) calistigi icin o
        # surecin stdout'u VARSAYILAN OLARAK ana surecinkiyle AYNI dosya
        # tanimlayicisini (fd 1) miras aliyordu -- yani modelin KENDI
        # ic-gozlem/debug amacli print()leri, bizim GERCEK log satirlarimizla
        # AYNI Kaggle log akisina, hicbir etiket olmadan karisiyordu. Burada
        # bu ALT SURECIN stdout/stderr'i os.devnull'a yonlendirilerek TAMAMEN
        # susturuluyor -- modelin print() cikisi zaten skorlanmiyor/
        # kullanilmiyor (yalnizca "sonuc"/"result" degiskeni okunuyor), bu
        # yuzden atmak veri kaybi degil, gurultu temizligi.
        _sys.stdout = open(_os.devnull, "w")
        _sys.stderr = open(_os.devnull, "w")

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
            kuyruk.put(("basari", _json_uyumlu_yap(ns.get("sonuc", ns.get("result")))))
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
    # NOT (Turkce): gercek Kaggle kosusunda modelin urettigi bir cagride
    # "arguments" alani (JSON olarak GECERLI olsa bile) bir nesne DEGIL,
    # duz bir metin/liste/sayi olabiliyordu (ör. {"name": "execute_python",
    # "arguments": "print(1)"}). Bu durumda asagidaki args.get(...)
    # cagrilari 'str' object has no attribute 'get' ile COKUYORDU ve
    # coklu_gpu.py'de bu hata TUM 43 gorevlik partiyi bos tahminle
    # (BOS_TAHMIN) isaretleyip atlaniyordu -- tek bir bozuk arac cagrisi
    # yuzunden partideki DIGER gorevler de kaybediliyordu.
    if not isinstance(args, dict):
        args = {}
    if ad == "execute_python":
        return execute_python_arac(args.get("code", ""), defter)
    if ad == "submit_answer":
        return submit_answer_arac(args.get("grid"), defter)
    return {"success": False, "error": f"Unknown tool: {ad}"}


def tool_response_mesaji_olustur(sonuc: Dict[str, Any]) -> str:
    return f"<tool_response>\n{json.dumps(sonuc, ensure_ascii=False)}\n</tool_response>"
