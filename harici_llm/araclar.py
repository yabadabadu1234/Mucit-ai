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


def train_examples_sandbox_bicimine_donustur(train_examples: Any) -> List[Tuple[List[List[int]], List[List[int]]]]:
    """`task.train_examples` (arc.Example nesnelerinin listesi -- her biri
    `.input`/`.output` numpy Grid taşır) girdisini, execute_python
    sandbox'ına enjekte edilecek düz Python (liste-of-liste) çiftlerine
    çevirir. numpy'a bağımlı kalmamak için burada `arc.Example`'ı
    doğrudan İMPORT ETMİYORUZ -- yalnızca `.input`/`.output` özniteliğine
    (ve onların `.tolist()`'ine) güveniyoruz, bu da araclar.py'nin arc.py
    ile gereksiz bir bağımlılık ilişkisine girmesini önler."""
    return [(ornek.input.tolist(), ornek.output.tolist()) for ornek in train_examples]


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
        # KRİTİK (kullanıcının gerçek Kaggle transkriptinde bulduğu kök
        # neden): sistem promptumuzun KENDİ örneği (arc_prompt.py,
        # "Example function call format") modele `train_examples` adlı
        # bir değişkenin execute_python sandbox'ında HAZIR olduğunu
        # (`for inp, out in train_examples: ...`) ÖĞRETİYOR -- ama bu
        # SÖZ hiçbir yerde GERÇEKTEN TUTULMUYORDU, sandbox'a böyle bir
        # değişken HİÇ enjekte edilmiyordu. Model, TAM OLARAK verdiğimiz
        # örneği takip ettiği için "name 'train_examples' is not defined"
        # hatasını ALIYORDU -- bu bir halüsinasyon değil, bizim kendi
        # örneğimizin tutulmayan bir vaadiydi. Artık çağıran taraf (coz_
        # yurutucu.py / coz_yurutucu_toplu.py), gerçek Task nesnesinden
        # GÜNCEL görevin train_examples'ını (input/output çiftleri, düz
        # Python listesi olarak) BURAYA yazıyor; execute_python_arac bunu
        # okuyup GERÇEKTEN sandbox'a enjekte ediyor (bkz. aşağıda).
        self.train_examples: Optional[List[Tuple[List[List[int]], List[List[int]]]]] = None


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
    train_examples = defter.train_examples if defter is not None else None
    basarili, sonuc = kodu_guvenle_calistir_serbest(code, train_examples=train_examples)
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


def kodu_guvenle_calistir_serbest(
    kod: str, train_examples: Optional[List[Tuple[List[List[int]], List[List[int]]]]] = None,
) -> Tuple[bool, Any]:
    """execute_python araci icin: transform(grid) imzasi sart kosmadan,
    serbest bir kod parcasini ayni AST guvenlik/izolasyon rejimiyle
    calistirir (kod_ajani.py'deki izolasyon mekanizmasini yeniden kullanir).

    `train_examples` verilirse (bkz. CevapDefteri.train_examples'daki not),
    sandbox namespace'ine `train_examples` adıyla GERÇEKTEN enjekte edilir
    -- sistem promptunun kendi örneğinin (arc_prompt.py) vaat ettiği ama
    eskiden HİÇ tutulmayan şey artık gerçekten tutuluyor. None ise (görev
    bağlamı olmayan çağrılar/testler) hiçbir şey enjekte edilmez, eski
    davranış (NameError) korunur."""
    import builtins
    import multiprocessing

    from kod_ajani import _guvenli_mi

    if not _guvenli_mi(kod):
        return False, "code failed the security check (forbidden eval/exec/open/dunder)"

    def _calistir(kuyruk: "multiprocessing.Queue", train_examples: Optional[List[Tuple[Any, Any]]]) -> None:
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

        # NOT (KRİTİK -- kullanıcının gerçek Kaggle transkriptinde tekrar
        # tekrar görülen "name 'train_examples' is not defined",
        # "name 'execute_python' is not defined", "name 'submit_answer'
        # is not defined", "name '__name__' is not defined" gibi -- BİRBİRİYLE
        # HİÇ İLGİSİZ görünen ama HEPSİ AYNI kök nedene sahip -- hataların
        # GERÇEK kaynağı burasıydı: exec(kod, globals_sozlugu, ns) İKİ AYRI
        # sözlükle çağrılıyordu. Python'ın klasik (ve iyi bilinen) bir
        # tuzağı: exec()'e AYRI globals/locals verildiğinde, üst seviye kod
        # `locals` (ns) sözlüğüne yazılır, AMA kod İÇİNDE tanımlanan bir
        # fonksiyonun __globals__'ı `globals` sözlüğüne (locals'a DEĞİL)
        # bağlanır -- yani üst seviyede tanımlanan bir değişkeni/fonksiyonu
        # (ör. `train_examples = [...]` veya `def transform(): ...`)
        # SONRADAN tanımlanan başka bir fonksiyonun İÇİNDEN çağırmak
        # NameError verir, sanki o isim hiç var olmamış gibi -- BU MODELİN
        # HATASI DEĞİLDİ, tamamen bizim sandbox'ımızın yapısındaki bir
        # kusurdu. Standalone bir script'te REPRODUCE edilip (aynı hata
        # mesajıyla) doğrulandı. Düzeltme: TEK bir paylaşılan sözlük hem
        # globals hem locals olarak kullanılıyor (exec(kod, ns)) -- gerçek
        # bir Python modülünün namespace davranışıyla AYNI, üst seviyedeki
        # HİÇBİR isim artık nested fonksiyonlardan görünmez değil.
        ns: Dict[str, Any] = {"__name__": "__main__", "__builtins__": {
            "range": range, "len": len, "list": list, "dict": dict, "set": set,
            "min": min, "max": max, "sum": sum, "enumerate": enumerate, "zip": zip,
            "sorted": sorted, "reversed": reversed, "abs": abs, "int": int, "float": float,
            "bool": bool, "str": str, "tuple": tuple, "map": map, "filter": filter,
            "any": any, "all": all, "isinstance": isinstance, "print": print,
            "iter": iter, "next": next, "round": round, "frozenset": frozenset,
            "divmod": divmod, "pow": pow, "__import__": builtins.__import__,
        }}
        if train_examples is not None:
            ns["train_examples"] = train_examples
        try:
            # Import kisitlamasi KALDIRILDI (kullanici talebiyle): kod zaten
            # izole bir alt surecte (5 sn zaman asimiyla) calisiyor, ana
            # makineye zarar verme ihtimali yok -- gercek `builtins.__import__`
            # kullanilarak model istedigi HERHANGI BIR modulu (numpy, scipy,
            # vs.) serbestce import edebiliyor.
            exec(kod, ns)
            kuyruk.put(("basari", _json_uyumlu_yap(ns.get("sonuc", ns.get("result")))))
        except Exception as exc:
            kuyruk.put(("hata", str(exc)))

    kuyruk: multiprocessing.Queue = multiprocessing.Queue()
    surec = multiprocessing.Process(target=_calistir, args=(kuyruk, train_examples))
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


# Gerçek Kaggle transkriptlerinde model, "execute_python" YERİNE kod
# çalıştırma NİYETİYLE (ama pretrain verisinden hatırladığı BAŞKA bir
# ajan/fonksiyon-çağırma şemasının ismiyle) bu isimlerden birini
# çağırıyordu -- HEPSİ anlamca "kod çalıştır" demek, TEK bir gerçek
# yeteneğimize (execute_python) karşılık geliyorlar. Bunları TANIMAK
# (execute_python'a yönlendirmek), modelin ANLAMSIZ/alakasız isimleri
# (ör. "calculate_shipping", "validate_password" -- ARC bulmacasıyla
# HİÇBİR ilgisi olmayan, sentetik fonksiyon-çağırma eğitim verisinden
# ezberlenmiş isimler) TANIMLAMAKTAN farklıdır: buradakiler GERÇEKTEN
# bizim TEK BİR yeteneğimizin (execute_python) eş anlamlılarıdır, o
# yüzden yönlendirmek doğru bir düzeltme; alakasız isimleri "tanımlamak"
# ise modelin hiçbir anlamı olmayan bir çağrıyı sanki bir şey yapmış gibi
# ödüllendirmek olurdu.
_EXECUTE_PYTHON_TAKMA_ADLARI = frozenset({
    "execute_bash", "execute_system", "execute_code", "execute_python_code",
    "execute_program", "add_and_execute_jupyter_code_cell", "run_python",
    "run_code", "python", "code_interpreter", "bash",
})


def arac_cagrisini_yurut(cagri: Dict[str, Any], defter: CevapDefteri) -> Dict[str, Any]:
    ad = cagri.get("name")
    if ad in _EXECUTE_PYTHON_TAKMA_ADLARI:
        ad = "execute_python"
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
        # NOT: takma-ad ile yönlendirilen çağrılarda model "code" yerine
        # kendi hatırladığı şemanın alan adını (ör. "command"/"script")
        # kullanmış olabilir -- ilk boş olmayanı kabul ediyoruz.
        kod = args.get("code") or args.get("command") or args.get("script") or ""
        return execute_python_arac(kod, defter)
    if ad == "submit_answer":
        return submit_answer_arac(args.get("grid"), defter)
    # NOT (Turkce): bu mesaj artik MODELE GERI BESLENIYOR (bkz.
    # coz_yurutucu_toplu.py'deki tool_response enjeksiyonu) -- ONCEDEN bu
    # geri besleme HIC yapilmiyordu, model "Unknown tool" hatasini asla
    # GORMUYORDU. Artik gorecegi icin, mesaj GECERLI iki aracin ADLARINI
    # ACIKCA tekrarliyor -- boylece model kendi hatali/hayali arac adindan
    # (ör. execute_bash, calculate_shipping -- ARC bulmacasiyla ilgisiz,
    # sentetik egitim verisinden ezberlenmis isimler) VAZGECIP dogru
    # araclara DONEBILIR.
    return {
        "success": False,
        "error": (
            f"Unknown tool: {ad!r}. The ONLY two tools available are execute_python and "
            f"submit_answer (see the system prompt's tool list). Call one of those two, "
            f"using their exact names."
        ),
    }


def tool_response_mesaji_olustur(sonuc: Dict[str, Any]) -> str:
    return f"<tool_response>\n{json.dumps(sonuc, ensure_ascii=False)}\n</tool_response>"
