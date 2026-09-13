from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

__all__ = ["Kaynak", "KAYNAKLAR", "kulliyat_cek", "kulliyat_verisi",
           "kulliyat_beyani", "kulliyat_dokumu", "mucit_cevir",
           "mucit_ac", "hf_boru", "yer_ac", "bos_alan",
           "MUCIT_UZANTI", "KULLIYAT_DIZINI"]

KULLIYAT_DIZINI = os.environ.get("MUCIT_KULLIYAT", "depo/kulliyat")


@dataclass(frozen=True)
class Kaynak:

    ad: str
    depo: str
    yol: str
    uzanti: Any = ".txt"
    dal: str = ""
    surum: str = ""
    varlik: str = ""
    yerel: str = ""
    engel: str = ""
    pay: float = 1.0

    def uzantilar(self) -> Tuple[str, ...]:
        u = self.uzanti
        return (u,) if isinstance(u, str) else tuple(u)


KAYNAKLAR: Tuple[Kaynak, ...] = (
    Kaynak("ARC soyutlamaları -- sözlü çözüm (ferman 1-R'nin sözlü kanadı)",
           "", "", (".md", ".py"), pay=3.0,
           yerel="idrak/veri/soyutlamalar"),
    Kaynak("ARC-AGI-2 (resmî, arcprize)", "arcprize/ARC-AGI-2", "data",
           ".json", pay=3.0),
    Kaynak("ARC-AGI-1 (fchollet)", "fchollet/ARC-AGI", "data",
           ".json", pay=2.0),
    Kaynak("ARC-AGI-3 (resmî ajan takımı, arcprize)",
           "arcprize/ARC-AGI-3-Agents", "", (".py", ".md", ".json"),
           pay=3.0),
    Kaynak("Enigmata (36 bulmaca ailesi, doğrulayıcılı)",
           "yabadabadu1234/Mucit-ai", "", surum="kulliyat-9",
           varlik="BytedTsinghua-SIA__Enigmata-Data.mucit", pay=3.0),
    Kaynak("SynLogic (sentetik mantık, doğrulayıcılı)",
           "yabadabadu1234/Mucit-ai", "", surum="kulliyat-10",
           varlik="MiniMaxAI__SynLogic.mucit", pay=2.0),
    Kaynak("ZebraLogic (ızgara mantık bulmacası, açık uçlu)",
           "yabadabadu1234/Mucit-ai", "", surum="kulliyat-12",
           varlik="allenai__ZebraLogicBench__grid_mode.mucit", pay=2.0),
    Kaynak("ARC veri kümeleri derlemesi (neoneye)",
           "neoneye/arc-dataset-collection", "", (".json", ".jsonl"),
           pay=2.0),
    Kaynak("AutumnBench (43 etkileşimli ızgara dünyası, 129 vazife)",
           "BasisResearch/MARAProtocol", "",
           (".json", ".jsonl", ".py", ".sexp", ".au", ".md"), pay=3.0),
    Kaynak("Autumn dili (dünyanın kaideleri, sembolik)",
           "BasisResearch/Autumn.cpp", "",
           (".au", ".sexp", ".jl", ".py", ".cpp", ".hpp", ".md"),
           pay=2.0),
    Kaynak("LARC (ARC'ın lisanla anlatılmış çözümleri)",
           "samacqua/LARC", "", (".json", ".csv", ".py"), pay=3.0),
    Kaynak("Minigrid + BabyAI (üretici ızgara dünyaları)",
           "Farama-Foundation/Minigrid", "",
           (".py", ".md", ".json"), pay=2.0),
    Kaynak("h-ARC (insan çözüm izleri)", "Le-Gris/h-arc", "",
           (".csv", ".json", ".ipynb", ".py"), pay=2.0),
    Kaynak("BARC (kaide ile üretilmiş ARC)", "xu3kev/BARC", "",
           (".json", ".jsonl", ".py"), pay=1.5),
    Kaynak("MINI-ARC", "KSB21ST/MINI-ARC", "data", ".json", pay=1.0),
    Kaynak("ConceptARC", "victorvikram/ConceptARC", "corpus", ".json",
           pay=1.0),
    Kaynak("re-ARC (üretici + DSL)", "michaelhodel/re-arc", "",
           ".py", pay=1.5),
    Kaynak("BIG-bench (204 vazife)", "google/BIG-bench", "bigbench/benchmark_tasks",
           (".json", ".jsonl", ".py"), pay=3.0),
    Kaynak("BIG-Bench Hard (23 zor vazife)",
           "suzgunmirac/BIG-Bench-Hard", "",
           (".json", ".jsonl", ".txt"), pay=1.5),
    Kaynak("Natural Instructions (1600+ vazife)",
           "allenai/natural-instructions", "tasks", ".json", pay=3.0),
    Kaynak("OpenAI Evals", "openai/evals", "evals/registry/data",
           (".jsonl", ".json"), pay=1.5),
    Kaynak("MATH (Hendrycks, 12500 mesele + çözüm)",
           "hendrycks/math", "", (".tar", ".txt"), pay=3.0),
    Kaynak("PRM800K (adım adım muhakeme etiketi)", "openai/prm800k",
           "prm800k", (".jsonl", ".json", ".py"), pay=3.0),
    Kaynak("GSM8K (mekteb riyaziyesi, çözümlü)",
           "openai/grade-school-math", "grade_school_math/data",
           ".jsonl", pay=2.0),
    Kaynak("AQuA (cebir, mantık izahlı)", "deepmind/AQuA", "",
           ".json", pay=1.5),
    Kaynak("DeepMind Mathematics (üretici)",
           "google-deepmind/mathematics_dataset", "", ".py", pay=0.5),
    Kaynak("NaturalProofs (ayrıştırıcı)", "wellecks/naturalproofs", "",
           (".json", ".jsonl", ".py", ".ipynb"), pay=0.5),
    Kaynak("miniF2F (resmî ispat mihengi)", "openai/miniF2F", "",
           (".lean", ".thy", ".mm", ".ml"), pay=1.5),
    Kaynak("Metamath set.mm (40 bin resmî ispat)", "metamath/set.mm", "",
           ".mm", pay=2.0),
    Kaynak("Lean mathlib4 (makine denetimli riyaziye)",
           "leanprover-community/mathlib4", "Mathlib", ".lean", pay=2.0),
    Kaynak("Risale-i Nur (Diyanet tashihli, txt + markdown)",
           "alitekdemir/Risale-i-Nur-Diyanet", "", (".txt", ".md"),
           dal="master", pay=3.0),
    Kaynak("Gayr-i Münteşir Risale Mektupları (2062 vesika)",
           "alitekdemir/ArsivNur", "", ".md", pay=1.5),
    Kaynak("Risale-i Nur kelime frekansı (lügat)",
           "alitekdemir/Risale-i-Nur-Kelime-Frekans", "data",
           (".txt", ".csv"), pay=0.5),
    Kaynak("Kütüb-i Sitte (hadis, tam metin JSON)",
           "AhmedBaset/hadith-json", "db", ".json", pay=3.0),
    Kaynak("Hadis neşirleri (çok dilli)", "fawazahmed0/hadith-api",
           "editions", ".json", pay=1.5),
    Kaynak("Tefsir külliyatı (çok müfessir)", "spa5k/tafsir_api",
           "tafsir", ".json", pay=2.0),
    Kaynak("Kur'ân-ı Kerîm (metin + meâl + tecvid)",
           "semarketir/quranjson", "source", ".json", pay=1.0),
    Kaynak("NVARC Artifacts Puzzles", "", "", pay=0.0,
           engel="Kaggle veri seti (sorokin/nvarc-artifacts-puzzles). "
                 "Bu oturumun ağ siyaseti www.kaggle.com'a tüneli "
                 "reddediyor (ölçüldü: 000). GitHub aynası yok: "
                 "1ytic/NVARC klonlandı ve README'si üçünü de "
                 "``kaggle datasets download`` ile tarif ediyor."),
    Kaynak("NVARC Synthetic Puzzles (103 bin)", "", "", pay=0.0,
           engel="Kaggle veri seti (sorokin/nvarc-synthetic-puzzles). "
                 "Aynı engel; ölçüldü."),
    Kaynak("NVARC Augmented Puzzles (3,2 milyon)", "", "", pay=0.0,
           engel="Kaggle veri seti (sorokin/nvarc-augmented-puzzles). "
                 "Aynı engel; ölçüldü."),
    Kaynak("UltraData-Math (openbmb)", "", "", pay=0.0,
           engel="Padişahın verdiği iki kumanda da yoklandı ve ikisi de "
                 "düştü: (1) ``git clone https://huggingface.co/"
                 "datasets/openbmb/UltraData-Math`` → 'CONNECT tunnel "
                 "failed, response 403'; (2) ``git clone "
                 "git@hf.co:datasets/...`` → 'cannot run ssh: No such "
                 "file or directory' (bu kapta ssh ikilisi yok). "
                 "Vekil kaydı da teyit ediyor: huggingface.co:443 için "
                 "'gateway answered 403 to CONNECT (policy denial)'. "
                 "Yâni HuggingFace'e şümul **siyasetle** kapalıdır, "
                 "kod eksikliğiyle değil."),
    Kaynak("OpenITI (Arapça İslâmî külliyat, ~10 bin metin)", "", "",
           pay=0.0,
           engel="``OpenITI/RELEASE`` klonlanmaya teşebbüs edildi ve "
                 "``git clone`` düştü (depo git-lfs ile taşınıyor, "
                 "işaretçi çekimi tamamlanmadı). Yerine Kütüb-i Sitte "
                 "(AhmedBaset/hadith-json) ve tefsir külliyatı "
                 "(spa5k/tafsir_api) kondu ve ikisi de ÇEKİLDİ."),
    Kaynak("arXiv tam metin arşivi", "", "", pay=0.0,
           engel="``arxiv.org`` ve ``export.arxiv.org`` ölçüldü: ikisi "
                 "de 000 (tünel kurulamıyor). Toplu arşiv zaten "
                 "requester-pays S3'tedir ve o da kapalıdır. GitHub'da "
                 "**metin gövdesi** taşıyan bir arXiv aynası yok; "
                 "bulunanlar (mattbierbaum/arxiv-public-datasets) "
                 "yalnız indirme takımıdır, metin taşımaz."),
    Kaynak("Project Gutenberg (kitap arşivi)", "", "", pay=0.0,
           engel="``gutenberg.org`` ölçüldü: 000. GITenberg'de her kitap "
                 "AYRI bir depodur (binlerce depo); toplu çekimi "
                 "GitHub API'siyle sıralamak gerekir ve ``api.github.com`` "
                 "bu oturumda 403 veriyor. Edebî külliyat yerine "
                 "Risale-i Nur ailesi (468 MB) ve Türkçe metin olarak "
                 "o kondu."),
)


def _dizin(k: Kaynak) -> str:
    return os.path.join(KULLIYAT_DIZINI, k.depo.replace("/", "__"))


def bos_alan(yol: str = "") -> int:
    import shutil as _sh
    d = yol or KULLIYAT_DIZINI
    os.makedirs(d, exist_ok=True)
    return int(_sh.disk_usage(d).free)


def yer_ac(gerek: int, koru: Sequence[str] = ()) -> Dict[str, Any]:
    korunan = {os.path.abspath(y) for y in koru}
    atilan: List[str] = []
    kazanc = 0
    if bos_alan() >= int(gerek):
        return {"gerek": int(gerek), "atılan": atilan, "kazanç": 0,
                "boş": bos_alan()}
    adaylar = []
    for f in os.listdir(KULLIYAT_DIZINI):
        if not f.endswith(MUCIT_UZANTI):
            continue
        y = os.path.join(KULLIYAT_DIZINI, f)
        if os.path.abspath(y) in korunan:
            continue
        try:
            adaylar.append((os.path.getmtime(y), os.path.getsize(y), y))
        except OSError:
            pass
    for _t, b, y in sorted(adaylar):
        if bos_alan() >= int(gerek):
            break
        try:
            os.remove(y)
            atilan.append(y)
            kazanc += b
        except OSError:
            pass
    return {"gerek": int(gerek), "atılan": atilan, "kazanç": kazanc,
            "boş": bos_alan()}


def _boy(kok: str, uzantilar: Sequence[str]) -> Tuple[int, int]:
    uz, b, n = tuple(uzantilar), 0, 0
    for kk, _dd, ff in os.walk(kok):
        for f in ff:
            if f.endswith(uz):
                try:
                    b += os.path.getsize(os.path.join(kk, f))
                    n += 1
                except OSError:
                    pass
    return b, n


MUCIT_DAMGA = b"MUCIT2\n"

MUCIT_UZANTI = ".mucit"


BELIRTEC_PENCERESI: int = 1 << 16


def _belirtecle(kod, metin: str, pencere: int = BELIRTEC_PENCERESI):
    if not metin:
        return []
    out = []
    i, boy = 0, len(metin)
    while i < boy:
        j = min(i + int(pencere), boy)
        if j < boy:
            k = max(metin.rfind("\n", i, j), metin.rfind(" ", i, j))
            if k > i:
                j = k + 1
        out.extend(kod.encode(metin[i:j], disallowed_special=()))
        i = j
    return out


def _parquet_akit(yol: str, kod, ch) -> Tuple[int, int]:
    import numpy as np
    try:
        import pyarrow.parquet as pq
    except ImportError as e:
        raise AssertionError(
            "``%s`` bir parquet dosyası fakat ``pyarrow`` kurulu değil. "
            "Sessizce atlamak, verinin bir kısmını gizlice düşürmek "
            "olurdu (ferman 5). Kurun: ``pip install pyarrow``" % yol) from e
    dosya = pq.ParquetFile(yol)
    import pyarrow as pa
    n = 0
    for obek in dosya.iter_batches(batch_size=4096):
        for ad, sut in zip(obek.schema.names, obek.columns):
            if not (pa.types.is_string(sut.type)
                    or pa.types.is_large_string(sut.type)):
                continue
            metin = "\n".join(str(v) for v in sut.to_pylist()
                               if v is not None)
            if not metin:
                continue
            t = _belirtecle(kod, metin)
            if t:
                ch.write(np.asarray(t, np.uint32).tobytes())
                n += len(t)
    return n, 1


def _metin_akit(yol: str, kod, ch, obek_bayt: int = 8 << 20
                ) -> Tuple[int, int]:
    import numpy as np
    if yol.endswith(".parquet"):
        return _parquet_akit(yol, kod, ch)
    try:
        fh = open(yol, "rb")
    except OSError:
        return 0, 0
    n = 0
    with fh:
        artik = b""
        while True:
            parca = fh.read(int(obek_bayt))
            if not parca:
                break
            parca = artik + parca
            artik, parca = parca[-4:], parca[:-4]
            if not parca:
                continue
            t = _belirtecle(kod, parca.decode("utf-8", "replace"))
            if t:
                ch.write(np.asarray(t, np.uint32).tobytes())
                n += len(t)
        if artik:
            t = _belirtecle(kod, artik.decode("utf-8", "replace"))
            if t:
                ch.write(np.asarray(t, np.uint32).tobytes())
                n += len(t)
    return n, 1


def mucit_cevir(kok: str, cikti: str, kodlama: str = "o200k_base",
                uzantilar: Sequence[str] = (), ad: str = "",
                obek_bayt: int = 8 << 20,
                getirici=None) -> Dict[str, Any]:
    import numpy as np
    from nefs.belirtec import belirtec_kapisi, belirtec_sozlugu

    kod = belirtec_kapisi(kodlama)
    V = int(belirtec_sozlugu(kodlama))
    uz = tuple(uzantilar)
    os.makedirs(os.path.dirname(cikti) or ".", exist_ok=True)
    n = dosya = 0
    gecici = cikti + ".yaziliyor"
    with open(gecici, "wb") as ch:
        ch.write(MUCIT_DAMGA)
        yer = ch.tell()
        ch.write(b" " * 320 + b"\n")
        if getirici is not None:
            for y, birak in getirici:
                if uz and not str(y).endswith(uz):
                    if birak is not None:
                        birak()
                    continue
                try:
                    n_m, d_m = _metin_akit(y, kod, ch, int(obek_bayt))
                finally:
                    if birak is not None:
                        birak()
                n += n_m
                dosya += d_m
        for kk, _dd, ff in (() if getirici is not None else os.walk(kok)):
            for f in sorted(ff):
                if uz and not f.endswith(uz):
                    continue
                y = os.path.join(kk, f)
                if f.endswith(".parquet"):
                    n_p, d_p = _parquet_akit(y, kod, ch)
                    n += n_p
                    dosya += d_p
                    continue
                n_m, d_m = _metin_akit(y, kod, ch, int(obek_bayt))
                n += n_m
                dosya += d_m
        bas = json.dumps({"kodlama": kodlama, "sözlük": V,
                          "belirteç": int(n), "kaynak": ad or kok,
                          "dosya": int(dosya)},
                         ensure_ascii=False).encode("utf-8")
        assert len(bas) <= 320, "başlık 320 baytı aşamaz: %d" % len(bas)
        ch.seek(yer)
        ch.write(bas + b" " * (320 - len(bas)))
    os.replace(gecici, cikti)
    return {"yol": cikti, "belirteç": n, "dosya": dosya,
            "kodlama": kodlama, "sözlük": V}


def hf_boru(kimlik: str, cikti: str, kodlama: str = "o200k_base",
            alt_yol: str = "", uzantilar: Sequence[str] = (),
            jeton: Optional[str] = None,
            gecici_dizin: str = "hf_parca") -> Dict[str, Any]:
    from huggingface_hub import HfApi, hf_hub_download

    api = HfApi(token=jeton or None)
    hepsi = [f for f in api.list_repo_files(kimlik, repo_type="dataset")
             if not f.endswith("/")]
    onler = tuple(y.strip().strip("/") + "/" for y in
                  str(alt_yol).replace(",", " ").split() if y.strip())
    if onler:
        hepsi = [f for f in hepsi if f.startswith(onler)]
    uz = tuple(uzantilar)
    if uz:
        hepsi = [f for f in hepsi if f.endswith(uz)]
    assert hepsi, (
        "``%s`` deposunda çevrilecek dosya yok: alt_yol=%r uzantı=%r. "
        "Depoda bulunan uzantılar: %s"
        % (kimlik, alt_yol, uz,
           sorted({os.path.splitext(f)[1] or "(uzantısız)"
                   for f in api.list_repo_files(kimlik,
                                                repo_type="dataset")})))
    os.makedirs(gecici_dizin, exist_ok=True)
    sayac = {"indi": 0, "bayt": 0}

    def _akis():
        for f in sorted(hepsi):
            y = hf_hub_download(kimlik, f, repo_type="dataset",
                                local_dir=gecici_dizin, token=jeton or None)
            sayac["indi"] += 1
            try:
                sayac["bayt"] += int(os.path.getsize(y))
            except OSError:
                pass

            def _birak(_y=y):
                for hedef in {_y, os.path.realpath(_y)}:
                    try:
                        os.remove(hedef)
                    except OSError:
                        pass
            yield y, _birak

    o = mucit_cevir("", cikti, kodlama, uzantilar=uz, ad=kimlik,
                    getirici=_akis())
    shutil.rmtree(gecici_dizin, ignore_errors=True)
    o["inen_dosya"] = int(sayac["indi"])
    o["inen_bayt"] = int(sayac["bayt"])
    return o


def mucit_ac(yol: str, kodlama: str = "o200k_base"):
    import numpy as np
    with open(yol, "rb") as fh:
        if fh.read(len(MUCIT_DAMGA)) != MUCIT_DAMGA:
            return None
        ham = fh.read(321).decode("utf-8", "replace").strip()
        ofset = fh.tell()
    if not ham or not ham.startswith("{"):
        return None
    try:
        bas = json.loads(ham)
    except ValueError:
        return None
    assert str(bas["kodlama"]) == str(kodlama), (
        "çevrilmiş külliyatın kodlaması tutmuyor: %s dosyada %r, "
        "tâlimde %r -- yeniden çevrilmeli"
        % (yol, bas["kodlama"], kodlama))
    return np.memmap(yol, dtype=np.uint32, mode="r", offset=ofset,
                     shape=(int(bas["belirteç"]),))


def envanter(kok: str) -> Dict[str, int]:
    e: Dict[str, int] = {}
    for kk, _dd, ff in os.walk(kok):
        for f in ff:
            u = os.path.splitext(f)[1] or "(uzantısız)"
            e[u] = e.get(u, 0) + 1
    return e


def kulliyat_cek(kaynaklar: Optional[Sequence[Kaynak]] = None
                 ) -> List[Dict[str, Any]]:
    ks = list(kaynaklar or KAYNAKLAR)
    out: List[Dict[str, Any]] = []
    for k in ks:
        if k.engel or not k.depo:
            out.append({"ad": k.ad, "alındı": False, "engel": k.engel,
                        "bayt": 0, "dosya": 0})
            continue
        d = _dizin(k)
        if k.varlik:
            hedef = os.path.join(d, k.varlik)
            if not os.path.isfile(hedef):
                os.makedirs(d, exist_ok=True)
                kok_adres = ("https://github.com/%s/releases/download/%s/"
                             % (k.depo, k.surum))
                parcalar: List[str] = []
                i = 0
                while True:
                    ad_p = k.varlik if i == 0 else "%s.parca%02d" % (k.varlik, i - 1)
                    yer = os.path.join(d, ad_p)
                    r = subprocess.run(
                        ["curl", "-fsSL", "-o", yer, kok_adres + ad_p],
                        capture_output=True, text=True, timeout=7200)
                    if r.returncode != 0:
                        if i == 0:
                            out.append({
                                "ad": k.ad, "alındı": False, "bayt": 0,
                                "dosya": 0,
                                "engel": "sürüm varlığı inmedi (%s): %s"
                                         % (kok_adres + ad_p,
                                            (r.stderr or "").strip()[-160:])})
                        break
                    parcalar.append(yer)
                    i += 1
                    if i == 1 and os.path.isfile(hedef):
                        break
                if not parcalar:
                    continue
                if len(parcalar) > 1:
                    with open(hedef + ".birlesik", "wb") as ch:
                        for y in parcalar:
                            with open(y, "rb") as f:
                                shutil.copyfileobj(f, ch, 8 << 20)
                            os.remove(y)
                    os.replace(hedef + ".birlesik", hedef)
            b = os.path.getsize(hedef) if os.path.isfile(hedef) else 0
            out.append({"ad": k.ad, "alındı": b > 0, "engel": "",
                        "yol": d, "bayt": b, "dosya": 1,
                        "çevrilmiş": True})
            continue
        if not os.path.isdir(d):
            os.makedirs(os.path.dirname(d) or ".", exist_ok=True)
            komut = ["git", "clone", "--depth", "1"]
            if k.dal:
                komut += ["--branch", k.dal]
            komut += ["https://github.com/" + k.depo, d]
            ortam = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1")
            r = subprocess.run(komut, capture_output=True, text=True,
                               env=ortam, timeout=7200)
            if r.returncode != 0:
                out.append({"ad": k.ad, "alındı": False, "bayt": 0,
                            "dosya": 0,
                            "engel": "git clone düştü: %s"
                                     % (r.stderr or "").strip()[-200:]})
                continue
        kok = os.path.join(d, k.yol) if k.yol else d
        if not os.path.isdir(kok):
            out.append({"ad": k.ad, "alındı": False, "bayt": 0, "dosya": 0,
                        "engel": "depo geldi fakat ``%s`` yolu yok -- "
                                 "cetveldeki yol yanlış" % k.yol})
            continue
        bayt, dosya = _boy(kok, k.uzantilar())
        if not dosya:
            env = envanter(kok)
            ilk = sorted(env.items(), key=lambda x: -x[1])[:6]
            out.append({"ad": k.ad, "alındı": False, "bayt": 0, "dosya": 0,
                        "engel": "``%s`` yolunda %s uzantılı dosya yok. "
                                 "Fiilen olan: %s"
                                 % (k.yol or ".", "/".join(k.uzantilar()),
                                    ", ".join("%s×%d" % (u, n)
                                              for u, n in ilk) or "hiç")})
            continue
        out.append({"ad": k.ad, "alındı": True, "engel": "", "yol": kok,
                    "bayt": bayt, "dosya": dosya, "çevrilmiş": False})
    return out


def kulliyat_verisi(sozluk: int, pencere: int, azami: int,
                    tohum: int = 0,
                    kaynaklar: Optional[Sequence[Kaynak]] = None,
                    kodlama: str = "o200k_base", taban: int = 16,
                    basamak: int = 0,
                    imlec: Optional[Dict[str, Any]] = None,
                    ne: str = "veri"):
    import numpy as np
    from nefs.belirtec import basamak_sayisi, belirtec_sozlugu, tip_vektoru

    tb = max(2, int(taban))
    bs = int(basamak) if int(basamak) > 0 else basamak_sayisi(
        int(sozluk) if int(sozluk) > 0 else belirtec_sozlugu(kodlama), tb)
    ks = [k for k in (kaynaklar or KAYNAKLAR)
          if not k.engel and (k.depo or k.yerel)]
    onceki = dict(imlec or {})
    yeni: Dict[str, Any] = {}
    diziler: List[Tuple[Any, float, str]] = []
    for k in ks:
        if k.yerel:
            assert os.path.isdir(k.yerel), (
                "yerel kaynak dizini YOK: %s (%s). Uydurulmuş bir yol "
                "cetvele giremez (ferman 1-K)." % (k.yerel, k.ad))
            yol = os.path.join(KULLIYAT_DIZINI,
                               k.yerel.replace("/", "__") + MUCIT_UZANTI)
            if os.path.isfile(yol) and mucit_ac(yol, kodlama) is None:
                os.remove(yol)
            if not os.path.isfile(yol):
                os.makedirs(KULLIYAT_DIZINI, exist_ok=True)
                mucit_cevir(k.yerel, yol, kodlama, k.uzantilar(), k.ad)
        elif k.varlik:
            yol = os.path.join(_dizin(k), k.varlik)
        else:
            yol = _dizin(k) + MUCIT_UZANTI
            kok = os.path.join(_dizin(k), k.yol) if k.yol else _dizin(k)
            if not os.path.isfile(yol) and not os.path.isdir(kok):
                kulliyat_cek([k])
                kok = os.path.join(_dizin(k), k.yol) if k.yol else _dizin(k)
            if not os.path.isfile(yol) and not os.path.isdir(kok):
                continue
            if not os.path.isfile(yol) and os.path.isdir(kok):
                ham, _n = _boy(kok, k.uzantilar())
                acik = [str(getattr(t, "filename", "") or "")
                        for t, _p in diziler]
                yer_ac(int(ham * 1.5) + (1 << 30),
                       koru=[y for y in acik if y])
            if os.path.isfile(yol) and mucit_ac(yol, kodlama) is None:
                os.remove(yol)
            if not os.path.isfile(yol):
                mucit_cevir(kok, yol, kodlama, k.uzantilar(), k.ad)
                shutil.rmtree(_dizin(k), ignore_errors=True)
        if not os.path.isfile(yol):
            continue
        t = mucit_ac(yol, kodlama)
        gerek = int(np.ceil(int(pencere) / bs)) + 2
        if t is None or t.size <= gerek:
            continue
        diziler.append((t, float(k.pay), k.ad))
    if not diziler:
        return ([], {}) if ne == "imleçli" else []
    toplam = sum(p for _t, p, _a in diziler) or 1.0
    cift: List[Tuple[List[int], int, str]] = []
    gerek = int(np.ceil(int(pencere) / bs)) + 2
    for t, pay, ad in diziler:
        n = int(round(int(azami) * pay / toplam))
        eski = onceki.get(ad) or {}
        yer = int(eski.get("belirteç", 0) or 0)
        if yer >= t.size - gerek:
            yer = 0
        okunan = 0
        for _k in range(max(0, n)):
            if yer >= t.size - gerek:
                yer = 0
            ham = np.asarray(t[yer:yer + gerek], np.int64)
            yer += gerek
            okunan += gerek
            akis = tip_vektoru(ham, tb, bs)
            kay = int(_k % max(1, bs))
            if akis.size < int(pencere) + 1 + kay:
                continue
            cift.append(([int(x) for x in akis[kay:kay + int(pencere)]],
                         int(akis[kay + int(pencere)]), "sözlü",
                         int((kay + int(pencere)) % max(1, bs))))
        yeni[ad] = {"belirteç": int(yer), "bayt": int(yer) * 4,
                    "boy": int(t.size), "boy_bayt": int(t.size) * 4,
                    "okunan": int(okunan),
                    "devir": int(eski.get("devir", 0) or 0)
                             + (1 if yer < int(eski.get("belirteç", 0) or 0)
                                else 0),
                    "nispet": float(yer) / float(max(int(t.size), 1))}
    cift = cift[:int(azami)]
    return (cift, yeni) if ne == "imleçli" else cift


def kulliyat_dokumu(kaynaklar: Optional[Sequence[Kaynak]] = None
                    ) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for k in (kaynaklar or KAYNAKLAR):
        if k.engel or not k.depo:
            out.append({"ad": k.ad, "alındı": False, "engel": k.engel,
                        "bayt": 0, "dosya": 0})
            continue
        yol = (os.path.join(_dizin(k), k.varlik) if k.varlik
               else _dizin(k) + MUCIT_UZANTI)
        if os.path.isfile(yol):
            out.append({"ad": k.ad, "alındı": True, "engel": "",
                        "yol": yol, "bayt": os.path.getsize(yol),
                        "dosya": 1, "çevrilmiş": True})
            continue
        kok = os.path.join(_dizin(k), k.yol) if k.yol else _dizin(k)
        if os.path.isdir(kok):
            b, n = _boy(kok, k.uzantilar())
            out.append({"ad": k.ad, "alındı": n > 0, "engel": "" if n else
                        "ham duruyor, henüz çevrilmedi", "yol": kok,
                        "bayt": b, "dosya": n, "çevrilmiş": False})
            continue
        out.append({"ad": k.ad, "alındı": False, "bayt": 0, "dosya": 0,
                    "engel": "kapta yok -- sırası gelince çekilecek "
                             "(boru hattı, ferman 1-O)"})
    return out


def kulliyat_beyani(dokum: Optional[Sequence[Dict[str, Any]]] = None) -> str:
    d = list(dokum if dokum is not None else kulliyat_dokumu())
    s = ["=== KÜLLİYAT (main/kulliyat.py) -- harici metin ===", "",
         "  Depoya gömülmez; ``%s`` altına çekilir." % KULLIYAT_DIZINI, ""]
    top_b = top_f = 0
    for k in d:
        if k["alındı"]:
            top_b += int(k["bayt"])
            top_f += int(k["dosya"])
            s.append("  ✔ %-46s %9.2f MB  %6d dosya%s"
                     % (k["ad"], k["bayt"] / 1e6, k["dosya"],
                        "  [çevrilmiş]" if k.get("çevrilmiş") else ""))
        else:
            s.append("  ✘ %-46s ALINAMADI" % k["ad"])
            s.append("      sebep: %s" % k["engel"])
    s += ["", "  TOPLAM: %.2f MB, %d dosya  -- **budama yok** "
          "(ferman 1-O: veri kesilmez, akışla okunur)"
          % (top_b / 1e6, top_f)]
    return "\n".join(s)
