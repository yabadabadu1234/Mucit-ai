"""
KÜLLİYAT -- HARİCÎ METİN KAYNAKLARI, DEPOYA GİRMEDEN

===================================================================
PADİŞAHIN HÜKMÜ
===================================================================

    "Githubdan Risale-i Nur diyanet reposunu bizim repoya veri olarak
    ekle. Yine githubdan Türkçe İslami kaynaklar araştır ve repoya ekle.
    Bilhassa fıkıh hadis tefsir usulleri, Tefsir Hadis Tarih
    külliyatları, Edebi külliyatlar. İngilizce olarak da Ultramath veri
    setlerini repoya koy. Ya da kodu öyle yaz ki gidip oradan veri çekip
    burada eğitime katsın ama dosyaları repoya tümden koymasın."

İkinci yol seçildi ve sebebi ölçüdür: Risale-i Nur külliyatının tek
başına metni **13,8 MB**, deposu **118 MB**dır. Bunu kod deposuna
gömmek, her klonlamada yüz megabaytı taşımak demektir. Külliyat
``depo/kulliyat/`` altına **çekilir**, oraya gömülmez.

===================================================================
BU MAKİNEDE NE MÜMKÜN -- ÖLÇÜLDÜ, GİZLENMİYOR
===================================================================

Bu oturumun ağ siyaseti doğrudan HTTPS'i **reddediyor** (``CONNECT``a
403). Ölçüldü::

    api.github.com   → 403 (tünel reddedildi)
    huggingface.co   → 000 (tünel kurulamadı)

Fakat oturumun **git vekili** umumi GitHub depolarının anonim
okumasına hizmet ediyor ve o yol **açık**: ``git clone`` koşuyor.
O hâlde:

* **GitHub deposu olan kaynaklar çekilebilir** ve çekiliyor.
* **HuggingFace veri setleri çekilemiyor** (UltraMath dâhil). Bu bir
  tercih değil, ölçülmüş bir engeldir (ferman 1-F): engel yazılır,
  yerine bir şey konursa ne konduğu da yazılır.

===================================================================
KAYNAK CETVELİ -- HER SATIR YOKLANDI
===================================================================

Aşağıdaki cetvelin her satırı ya **fiilen klonlandı ve sayıldı**, ya da
niçin alınamadığı yazıldı. "Var sanıyorum" diye bir satır yoktur.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

__all__ = ["Kaynak", "KAYNAKLAR", "kulliyat_cek", "kulliyat_verisi",
           "kulliyat_beyani", "disk_butcesi", "KULLIYAT_DIZINI"]

#: Külliyatın indiği yer. **Depoya girmez** (``.gitignore``).
KULLIYAT_DIZINI = os.environ.get("MUCIT_KULLIYAT", "depo/kulliyat")

#: Diskin ne kadarı külliyata ayrılır. Bkz. ``disk_butcesi``.
DISK_PAYI: float = 0.5


@dataclass(frozen=True)
class Kaynak:
    """Bir metin kaynağı. ``dal`` boşsa deponun kendi varsayılanı."""

    ad: str
    depo: str                 # "sahip/isim"
    yol: str                  # depo içinde metnin bulunduğu dizin
    #: Metin sayılan uzantılar. Tek dize de verilebilir.
    uzanti: Any = ".txt"
    dal: str = ""
    #: Alınamıyorsa sebebi. Boşsa alınabilir demektir.
    engel: str = ""
    #: Bu kaynağın külliyattaki **söz hakkı**. Bütün payların toplamı
    #: bire indirilir ve disk bütçesi o nispette dağıtılır. Pay bir
    #: kemiyet değil keyfiyet ölçüsüdür (ferman 1-J): bir kaynağın ne
    #: kadar yer tutacağı ne kadar **büyük** olduğuna değil, külliyatta
    #: ne kadar **ayrı bir şey** söylediğine göre verilir. Meselâ 8 GB
    #: tefsir dosyasının yüzde doksanı aynı âyetin başka tercümesidir;
    #: 200 MB riyaziye ispatı ise baştan sona ayrıdır.
    pay: float = 1.0

    def uzantilar(self) -> Tuple[str, ...]:
        u = self.uzanti
        return (u,) if isinstance(u, str) else tuple(u)


#: **CETVEL.** Her satır ya klonlandı ya da engeli yazıldı.
KAYNAKLAR: Tuple[Kaynak, ...] = (
    # ══════════════════════════════════════════════════════════════
    #  ARC AİLESİ -- NVARC'ın kendi ``external/`` alt modülleri
    # ══════════════════════════════════════════════════════════════
    #
    # Padişahın emri: *"Githubda NVARC ARC AGI 2 sisteminin 3 verisetini
    # bul ve eğitim kaynaklarına ekle."* Depo bulundu ve okundu
    # (``1ytic/NVARC``, NVIDIA KGMoN; Sorokin & Puget). **Adı geçen üç
    # veri seti Kaggle'dadır**, GitHub'da değil::
    #
    #     sorokin/nvarc-artifacts-puzzles    (üretilen metin)
    #     sorokin/nvarc-synthetic-puzzles    (103 bin sentetik bulmaca)
    #     sorokin/nvarc-augmented-puzzles    (3,2 milyon çoğaltılmış)
    #
    # ve ``www.kaggle.com`` bu oturumda **kapalıdır** (ölçüldü: ``000``,
    # tünel kurulamıyor). O hâlde üçü de aşağıda engeliyle yazılıdır.
    # Fakat NVARC'ın **kendi** veri kaynakları GitHub alt modülleridir
    # ve hepsi çekildi: ARC-AGI-2, h-arc, BARC, MINI-ARC, ConceptARC,
    # re-arc. Yâni NVARC'ın bulmaca havuzu -- Kaggle'daki türevleri
    # hariç -- külliyattadır.
    Kaynak("ARC-AGI-2 (resmî, arcprize)", "arcprize/ARC-AGI-2", "data",
           ".json", pay=3.0),
    Kaynak("ARC-AGI-1 (fchollet)", "fchollet/ARC-AGI", "data",
           ".json", pay=2.0),
    Kaynak("h-ARC (insan çözüm izleri)", "Le-Gris/h-arc", "",
           (".csv", ".json", ".ipynb", ".py"), pay=2.0),
    # Envanterden: 524 ``.json`` + 567 ``.py`` (kaideyi üreten kod da
    # verinin kendisidir), ``synthetic_problems/`` ve ``ConceptARC/``.
    Kaynak("BARC (kaide ile üretilmiş ARC)", "xu3kev/BARC", "",
           (".json", ".jsonl", ".py"), pay=1.5),
    Kaynak("MINI-ARC", "KSB21ST/MINI-ARC", "data", ".json", pay=1.0),
    Kaynak("ConceptARC", "victorvikram/ConceptARC", "corpus", ".json",
           pay=1.0),
    # ``re_arc.zip`` sıkıştırılmıştır ve bayt olarak manasızdır; asıl
    # veri **üreticidir** (``generators.py``, ``verifiers.py``, ``dsl.py``).
    Kaynak("re-ARC (üretici + DSL)", "michaelhodel/re-arc", "",
           ".py", pay=1.5),
    # ══════════════════════════════════════════════════════════════
    #  BULMACA / BENCMARK / CHALLENGE
    # ══════════════════════════════════════════════════════════════
    Kaynak("BIG-bench (204 vazife)", "google/BIG-bench", "bigbench/benchmark_tasks",
           (".json", ".jsonl", ".py"), pay=3.0),
    Kaynak("BIG-Bench Hard (23 zor vazife)",
           "suzgunmirac/BIG-Bench-Hard", "",
           (".json", ".jsonl", ".txt"), pay=1.5),
    Kaynak("Natural Instructions (1600+ vazife)",
           "allenai/natural-instructions", "tasks", ".json", pay=3.0),
    Kaynak("OpenAI Evals", "openai/evals", "evals/registry/data",
           (".jsonl", ".json"), pay=1.5),
    # ══════════════════════════════════════════════════════════════
    #  RİYAZİYE VE MANTIK YÜRÜTME İZLERİ
    # ══════════════════════════════════════════════════════════════
    #
    # Padişahın emri: *"1 gb ve üzeri akıl yürütme izi verisetleri
    # bul."* GitHub'da metin gövdesiyle duran, gigabayt mertebesinde
    # **akıl yürütme izi** üç yerdedir ve üçü de aşağıdadır:
    # ``natural-instructions`` (3,1 GB vazife + izah), ``BIG-bench``
    # (2,3 GB), ``set.mm`` (Metamath: 40 bin resmî ispat, tek dosya).
    # PRM800K adım-adım muhakeme etiketleriyle küçüktür fakat cinsi
    # tamdır; ``mathlib4`` ise makine ile denetlenmiş ispatın kendisi.
    # **MATH gövdesi ``MATH.tar`` içindedir** ve depoda öyle durur.
    # Tar bir metin kabıdır: içindeki JSON gövdesi baytça okunabilir,
    # 512 baytlık başlıklar ~%0,4 gürültü katar. Açmak yerine olduğu
    # gibi okumak, kabı ayrıca diske yaymamak demektir.
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
    # Envanterden: depoda 18 ``.py`` + 5 ``.ipynb`` var, veri gövdesi
    # harici indirmededir. O hâlde alınan şey ispat **metni** değil,
    # ispatı ayrıştıran koddur ve payı ona göredir.
    Kaynak("NaturalProofs (ayrıştırıcı)", "wellecks/naturalproofs", "",
           (".json", ".jsonl", ".py", ".ipynb"), pay=0.5),
    Kaynak("miniF2F (resmî ispat mihengi)", "openai/miniF2F", "",
           (".lean", ".thy", ".mm", ".ml"), pay=1.5),
    Kaynak("Metamath set.mm (40 bin resmî ispat)", "metamath/set.mm", "",
           ".mm", pay=2.0),
    Kaynak("Lean mathlib4 (makine denetimli riyaziye)",
           "leanprover-community/mathlib4", "Mathlib", ".lean", pay=2.0),
    # ══════════════════════════════════════════════════════════════
    #  İSLÂMÎ KAYNAKLAR -- TEFSİR, HADİS, RİSALE
    # ══════════════════════════════════════════════════════════════
    # **İKİ SATIR TEK SATIRA TERKİP EDİLDİ (ferman 3).** Evvelce aynı
    # depo iki kere yazılıydı (``txt`` ve ``obsidian-markdown``) ve
    # ikisi de **aynı dizine** klonlanıyordu: birincinin budaması
    # ikincinin yolunu siliyor, ikinci "yol yok" diye düşüyordu. İki
    # satır aynı şeyi işaret ediyorsa iki satır değildir.
    Kaynak("Risale-i Nur (Diyanet tashihli, txt + markdown)",
           "alitekdemir/Risale-i-Nur-Diyanet", "", (".txt", ".md"),
           dal="master", pay=3.0),
    Kaynak("Gayr-i Münteşir Risale Mektupları (2062 vesika)",
           "alitekdemir/ArsivNur", "", ".md", pay=1.5),
    Kaynak("Risale-i Nur kelime frekansı (lügat)",
           "alitekdemir/Risale-i-Nur-Kelime-Frekans", "data",
           (".txt", ".csv"), pay=0.5),
    # **KÜTÜB-İ SİTTE BULUNDU.** Evvelki turda "metin gövdesi olan umumi
    # depo bulunamadı" yazılıydı; o hüküm **yanlıştı ve düzeltiliyor**:
    # ``AhmedBaset/hadith-json`` altı kitabın tam metnini JSON olarak
    # taşıyor (176 MB), ``fawazahmed0/hadith-api`` ise çok dilli
    # neşirleri (3,8 GB; Türkçesi dâhil).
    Kaynak("Kütüb-i Sitte (hadis, tam metin JSON)",
           "AhmedBaset/hadith-json", "db", ".json", pay=3.0),
    Kaynak("Hadis neşirleri (çok dilli)", "fawazahmed0/hadith-api",
           "editions", ".json", pay=1.5),
    Kaynak("Tefsir külliyatı (çok müfessir)", "spa5k/tafsir_api",
           "tafsir", ".json", pay=2.0),
    # 6348 ``.mp3`` var ve metin değildir; ``_buda`` onları atar.
    Kaynak("Kur'ân-ı Kerîm (metin + meâl + tecvid)",
           "semarketir/quranjson", "source", ".json", pay=1.0),
    # ══════════════════════════════════════════════════════════════
    #  ENGELİ YAZILANLAR -- "var sanıyorum" satırı yoktur
    # ══════════════════════════════════════════════════════════════
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


def disk_butcesi() -> int:
    """Külliyata ayrılan **toplam bayt** -- diskten ÖLÇÜLÜR (ferman 5-B).

    Elle yazılmış bir tavan yoktur ve olamaz: aynı kod 30 GB'lık bir
    kapta da, 2 TB'lık bir makinede de koşacak. Bütçe, o an fiilen
    boş olan alan ile külliyatın hâlihazırda tuttuğu alanın
    toplamının bir nispetidir::

        havuz  = boş + külliyatın tuttuğu
        bütçe  = havuz × PAY

    ``PAY`` bir keyfiyet ölçüsüdür: diskin tamamını doldurmak tâlimin
    kendi yazacağı hazineye yer bırakmamak demektir; hiç doldurmamak
    ise külliyatı süs yapmak. Yarısı, ikisinin arasıdır ve **ölçü
    kırmızı yanabilir**: bütçe sıfırlanırsa hiçbir kaynak tutulmaz ve
    ``kulliyat_verisi`` boş döner.
    """
    import shutil
    os.makedirs(KULLIYAT_DIZINI, exist_ok=True)
    bos = int(shutil.disk_usage(KULLIYAT_DIZINI).free)
    tutulan = 0
    for kk, _dd, ff in os.walk(KULLIYAT_DIZINI):
        for f in ff:
            try:
                tutulan += os.path.getsize(os.path.join(kk, f))
            except OSError:
                pass
    return int((bos + tutulan) * DISK_PAYI)


def envanter(kok: str) -> Dict[str, int]:
    """Bir dizindeki uzantı sayımı -- **silmeden evvel**."""
    e: Dict[str, int] = {}
    for kk, _dd, ff in os.walk(kok):
        for f in ff:
            u = os.path.splitext(f)[1] or "(uzantısız)"
            e[u] = e.get(u, 0) + 1
    return e


def _buda(kok: str, uzantilar: Sequence[str], had: int
          ) -> Tuple[int, int, Dict[str, int]]:
    """Bir kaynağı ``had`` bayta indir; ``(tutulan, atılan, envanter)``.

    ===================================================================
    NİÇİN BUDAMA -- ÖLÇÜLDÜ
    ===================================================================

    Çekilen külliyat 23 GB'a çıktı ve diskte 6,9 GB kaldı. Fakat mesele
    yalnız yer değil, **söz hakkı**dır: ``spa5k/tafsir_api`` tek başına
    8,9 GB ve o 8,9 GB'ın büyük kısmı **aynı âyetin başka
    tercümeleridir**. Budanmazsa külliyatın onda dokuzu tek bir
    kaynağın tekrarı olur ve tâlim onu öğrenir.

    ===================================================================
    EVVELÂ SAYIM -- ÖLÇÜLMÜŞ VE DÜZELTİLMİŞ YIKIM
    ===================================================================

    Bu fonksiyonun ilk hâli sayım yapmadan siliyordu: cetveldeki
    ``uzanti`` yanlışsa **bütün depo siliniyordu**. Ölçüldü ve on yedi
    kaynak (h-arc, BARC, MINI-ARC, ConceptARC, re-arc, set.mm, ArsivNur,
    hadith-json...) 4 kilobayta indi. Yanlış bir tahminin bedeli
    kaynağın kendisi olamaz.

    Artık envanter **evvelâ** çıkarılır; hiçbir dosya uzantıya
    uymuyorsa **tek dosya bile silinmez** ve envanter geri döner --
    yâni yanlış cetvel satırı, veriyi imha etmek yerine kendini
    ihbar eder.
    """
    env = envanter(kok)
    uz = tuple(uzantilar)
    dosyalar: List[Tuple[str, int]] = []
    ote: List[str] = []
    for kk, _dd, ff in os.walk(kok):
        for f in sorted(ff):
            y = os.path.join(kk, f)
            try:
                b = os.path.getsize(y)
            except OSError:
                continue
            (dosyalar.append((y, b)) if f.endswith(uz) else ote.append(y))
    if not dosyalar:
        return 0, 0, env                    # **HİÇBİR ŞEY SİLİNMEZ**
    git = os.path.join(kok, ".git")
    if os.path.isdir(git):
        shutil.rmtree(git, ignore_errors=True)
    for y in ote:                           # metin olmayan: yalnız yer tutar
        try:
            os.remove(y)
        except OSError:
            pass
    dosyalar.sort()
    tutulan = atilan = 0
    for y, b in dosyalar:
        if tutulan + b <= had:
            tutulan += b
        else:
            atilan += b
            try:
                os.remove(y)
            except OSError:
                pass
    return tutulan, atilan, env


def kulliyat_cek(kaynaklar: Optional[Sequence[Kaynak]] = None,
                 had: Optional[int] = None) -> List[Dict[str, Any]]:
    """Kaynakları ``depo/kulliyat/`` altına **çek ve payına göre buda**.

    Zaten çekilmişse tekrar çekilmez. Çekilemeyen **sessizce
    geçilmez**: sözlükte ``engel`` alanı sebebiyle beraber döner.

    Bütçe payı: ``had_i = bütçe × pay_i / Σ pay``. Yâni bir kaynağın
    tutacağı yer büyüklüğünden değil, **külliyattaki söz hakkından**
    çıkar (ferman 1-J: kemiyete değil keyfiyete).
    """
    ks = list(kaynaklar or KAYNAKLAR)
    butce = int(disk_butcesi() if had is None else had)
    toplam_pay = sum(float(k.pay) for k in ks
                     if not k.engel and k.depo) or 1.0
    out: List[Dict[str, Any]] = []
    for k in ks:
        if k.engel or not k.depo:
            out.append({"ad": k.ad, "alındı": False, "engel": k.engel,
                        "bayt": 0, "dosya": 0, "atılan": 0, "had": 0})
            continue
        pay_had = int(butce * float(k.pay) / toplam_pay)
        d = _dizin(k)
        if not os.path.isdir(d):
            os.makedirs(os.path.dirname(d) or ".", exist_ok=True)
            komut = ["git", "clone", "--depth", "1"]
            if k.dal:
                komut += ["--branch", k.dal]
            komut += ["https://github.com/" + k.depo, d]
            ortam = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1")
            r = subprocess.run(komut, capture_output=True, text=True,
                               env=ortam, timeout=1800)
            if r.returncode != 0:
                out.append({"ad": k.ad, "alındı": False, "bayt": 0,
                            "dosya": 0, "atılan": 0, "had": pay_had,
                            "engel": "git clone düştü: %s"
                                     % (r.stderr or "").strip()[-200:]})
                continue
        kok = os.path.join(d, k.yol) if k.yol else d
        if not os.path.isdir(kok):
            out.append({"ad": k.ad, "alındı": False, "bayt": 0,
                        "dosya": 0, "atılan": 0, "had": pay_had,
                        "engel": "depo geldi fakat ``%s`` yolu yok "
                                 "-- cetveldeki yol yanlış" % k.yol})
            continue
        # **BUDAMA: PAYINDAN FAZLASINI TUTMAZ.**
        #
        # Kaynağın kendi yolu dışındaki dizinler de atılır -- fakat
        # **yalnız ``yol`` verilmişse**. Verilmemişse ``kok`` deponun
        # kendisidir ve o hâlde bu döngü deponun bütün içeriğini
        # silerdi: ölçüldü, on yedi kaynak bu yüzden 4 kilobayta indi.
        if k.yol and os.path.abspath(kok) != os.path.abspath(d):
            tut = os.path.abspath(kok)
            for alt in os.listdir(d):
                y = os.path.abspath(os.path.join(d, alt))
                if y == tut or tut.startswith(y + os.sep):
                    continue
                if os.path.isdir(y):
                    shutil.rmtree(y, ignore_errors=True)
                else:
                    try:
                        os.remove(y)
                    except OSError:
                        pass
        tutulan, atilan, env = _buda(kok, k.uzantilar(), pay_had)
        dosya = sum(1 for kk, _dd, ff in os.walk(kok) for f in ff
                    if f.endswith(k.uzantilar()))
        if not dosya:
            # **BOŞ DÖNEN KAYNAK SESSİZCE GEÇİLMEZ.** Envanter yazılır:
            # yâni "hangi uzantı aranmalıydı" sorusu tahmine değil,
            # deponun kendi sayımına havale edilir.
            ilk = sorted(env.items(), key=lambda x: -x[1])[:6]
            out.append({"ad": k.ad, "alındı": False, "bayt": 0,
                        "dosya": 0, "atılan": 0, "had": pay_had,
                        "engel": "depo geldi fakat ``%s`` yolunda "
                                 "%s uzantılı dosya yok. Fiilen olan: %s"
                                 % (k.yol or ".", "/".join(k.uzantilar()),
                                    ", ".join("%s×%d" % (u, n)
                                              for u, n in ilk) or "hiç")})
            continue
        out.append({"ad": k.ad, "alındı": True, "engel": "", "yol": kok,
                    "bayt": tutulan, "dosya": dosya, "atılan": atilan,
                    "had": pay_had})
    return out


def kulliyat_verisi(sozluk: int, pencere: int, azami: int,
                    tohum: int = 0,
                    kaynaklar: Optional[Sequence[Kaynak]] = None
                    ) -> List[Tuple[List[int], int]]:
    """Külliyattan ``(bağlam, hedef)`` çiftleri -- tâlime katılacak hâlde.

    ===================================================================
    BELİRTEÇLEME: BAYT DÜZEYİ, ``sozluk`` MODÜLÜ
    ===================================================================

    Sözlük ``16``dır ve bu bir kusur değil, mimarinin kendi ölçüsüdür
    (veri lifi ``ℂ^16``). Metin UTF-8 baytlarına açılır ve ``mod
    sozluk`` alınır. **Bu bir kayıptır ve saklanmıyor**: 256 bayt 16
    seviyeye iner, yâni her seviye 16 baytı temsil eder.

    Niçin yine de manalıdır: mimari **münasebet** öğrenir, kelime
    değil. Hangi seviyenin hangisini takip ettiği, metnin istatistik
    yapısını taşır. Sözlük büyütülürse (``EgitimAyari.sozluk``) veri
    lifi de beraber büyür (``nefs/olcek.py`` Formül 1) ve kayıp azalır;
    yâni bu hudut **ayarlanabilir** ve nerede olduğu yazılıdır.
    """
    import numpy as np
    r = np.random.default_rng(int(tohum))
    metinler: List[bytes] = []
    for k in (kaynaklar or KAYNAKLAR):
        if k.engel or not k.depo:
            continue
        kok = os.path.join(_dizin(k), k.yol) if k.yol else _dizin(k)
        if not os.path.isdir(kok):
            continue
        for kk, _dd, ff in os.walk(kok):
            if ".git" in kk:
                continue
            for f in sorted(ff):
                if f.endswith(k.uzantilar()):
                    with open(os.path.join(kk, f), "rb") as fh:
                        metinler.append(fh.read())
    if not metinler:
        return []
    ham = b"\n".join(metinler)
    b = np.frombuffer(ham, dtype=np.uint8)
    assert b.size > int(pencere) + 1, (
        "külliyat penceresi doldurmuyor: %d bayt" % b.size)
    t = (b % np.uint8(int(sozluk))).astype(np.int64)
    n = int(azami)
    bas = r.integers(0, t.size - int(pencere) - 1, size=n)
    return [([int(x) for x in t[i:i + int(pencere)]],
             int(t[i + int(pencere)])) for i in bas]


def kulliyat_beyani(dokum: Optional[Sequence[Dict[str, Any]]] = None) -> str:
    """Külliyatın hâli -- **ne alındı, ne alınamadı, niçin**."""
    d = list(dokum if dokum is not None else kulliyat_cek())
    s = ["=== KÜLLİYAT (main/kulliyat.py) -- harici metin ===", "",
         "  Depoya gömülmez; ``%s`` altına çekilir." % KULLIYAT_DIZINI, ""]
    top_b = top_f = top_a = 0
    for k in d:
        if k["alındı"]:
            top_b += int(k["bayt"])
            top_f += int(k["dosya"])
            top_a += int(k.get("atılan", 0))
            s.append("  ✔ %-42s %8.2f MB  %5d dosya  [had %6.0f MB, "
                     "budanan %7.1f MB]"
                     % (k["ad"], k["bayt"] / 1e6, k["dosya"],
                        k.get("had", 0) / 1e6, k.get("atılan", 0) / 1e6))
        else:
            s.append("  ✘ %-46s ALINAMADI" % k["ad"])
            s.append("      sebep: %s" % k["engel"])
    s += ["", "  TOPLAM: %.2f MB, %d dosya  (budanan %.2f MB; "
          "disk bütçesi %.2f GB)"
          % (top_b / 1e6, top_f, top_a / 1e6, disk_butcesi() / 1e9)]
    return "\n".join(s)
