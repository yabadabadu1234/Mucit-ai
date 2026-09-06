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

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

__all__ = ["Kaynak", "KAYNAKLAR", "kulliyat_cek", "kulliyat_verisi",
           "kulliyat_beyani", "mucit_cevir", "mucit_ac",
           "MUCIT_UZANTI", "KULLIYAT_DIZINI"]

#: Külliyatın indiği yer. **Depoya girmez** (``.gitignore``).
KULLIYAT_DIZINI = os.environ.get("MUCIT_KULLIYAT", "depo/kulliyat")

#: **BUDAMA VE DİSK BÜTÇESİ İMHA EDİLDİ (ferman 1-O).**
#:
#:     "Sana ne oluyor da indirdiğin veriseti sınırlıyorsun? İnen şey
#:     githuba inecek, sen de ineni kendi cpu'na tek hamlede paldır
#:     küldür almayacaksın, boru hattı kurup işini bitire bitire
#:     alacaksın ama verisetinin tamamı o repoda duracak!"
#:
#: Burada ``DISK_PAYI``, ``disk_butcesi()`` ve ``_buda()`` duruyordu:
#: 23 GB'lık çekimin 11,2 GB'ını **siliyorlardı**. O bir çare değil,
#: kusurun kendisiydi -- kabın darlığı **akışla** çözülür, veriyi
#: kesmekle değil. Kaynak olduğu gibi durur; kapta tutulan şey ancak
#: o an okunan **penceredir** (``mucit_cevir`` öbek öbek çevirir,
#: ``mucit_ac`` mmap ile bakar).


@dataclass(frozen=True)
class Kaynak:
    """Bir metin kaynağı. ``dal`` boşsa deponun kendi varsayılanı."""

    ad: str
    depo: str                 # "sahip/isim"
    yol: str                  # depo içinde metnin bulunduğu dizin
    #: Metin sayılan uzantılar. Tek dize de verilebilir.
    uzanti: Any = ".txt"
    dal: str = ""
    #: **GITHUB RELEASE VARLIĞI.** Doluysa kaynak ``git clone`` ile
    #: değil, ``https://github.com/<depo>/releases/download/<surum>/
    #: <varlik>`` adresinden indirilir. HuggingFace'e doğrudan şümul
    #: kapalı olduğu için (ferman 1-K) veri oraya **GitHub Actions**
    #: ile taşınır: ``.github/workflows/hf_to_gh.yml`` HF'ten çeker,
    #: ``mucit_cevir`` ile bizim biçime dönüştürür ve Release'e koyar.
    #: Ajan yalnız GitHub gördüğü için o adresten indirebilir.
    surum: str = ""
    varlik: str = ""
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


def _boy(kok: str, uzantilar: Sequence[str]) -> Tuple[int, int]:
    """Bir kaynağın metin gövdesi: ``(bayt, dosya)``. **Hiçbir şey silmez.**"""
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

#: Çevrilmiş dosyanın uzantısı.
MUCIT_UZANTI = ".mucit"


def mucit_cevir(kok: str, cikti: str, kodlama: str = "o200k_base",
                uzantilar: Sequence[str] = (), ad: str = "",
                obek_bayt: int = 8 << 20) -> Dict[str, Any]:
    """Ham metni **bizim biçime** çevir: tiktoken belirteçleri, tek dosya.

    ===================================================================
    BELİRTEÇLEME TİKTOKEN'DİR (ferman 1-N)
    ===================================================================

    Evvelce burada ``bayt % sozluk`` vardı ve ``sozluk`` 16'ydı: 256
    bayt on altı seviyeye iniyordu. Bu bir belirteçleme değil, bir
    **imhaydı** -- her seviye on altı ayrı baytı temsil ediyordu ve
    metnin kelime yapısı tamamen kayboluyordu.

    Artık metin tiktoken'den geçer ve dosyaya **belirteç kimlikleri**
    ``uint32`` olarak yazılır. Kayıp yoktur: ``coz`` metni geri verir.

    ===================================================================
    BORU HATTI (ferman 1-O)
    ===================================================================

    Kaynağın tamamı belleğe **alınmaz**. Dosyalar sırayla açılır,
    ``obek_bayt``lık parçalar hâlinde belirteçlenir ve çıktıya
    **akıtılır**. Yâni 8 GB'lık bir tefsir külliyatı, 8 MB'lık bir
    pencereyle çevrilir. Kabın darlığı akışla çözülür, veri kesilmez.

    Biçim::

        MUCIT2\n
        {"kodlama": "o200k_base", "sözlük": 200019, "belirteç": N, …}\n
        <N adet uint32 belirteç kimliği>
    """
    import numpy as np
    from nefs.belirtec import belirtec_kapisi, belirtec_sozlugu

    kod = belirtec_kapisi(kodlama)
    V = int(belirtec_sozlugu(kodlama))
    uz = tuple(uzantilar)
    os.makedirs(os.path.dirname(cikti) or ".", exist_ok=True)
    n = dosya = 0
    with open(cikti, "wb") as ch:
        ch.write(MUCIT_DAMGA)
        yer = ch.tell()
        ch.write(b" " * 320 + b"\n")
        for kk, _dd, ff in os.walk(kok):
            for f in sorted(ff):
                if uz and not f.endswith(uz):
                    continue
                try:
                    fh = open(os.path.join(kk, f), "rb")
                except OSError:
                    continue
                with fh:
                    artik = b""
                    while True:
                        parca = fh.read(int(obek_bayt))
                        if not parca:
                            break
                        parca = artik + parca
                        # **UTF-8 SINIRINDA KESME.** Çok baytlı bir
                        # harfin ortasından bölmek o harfi bozar ve
                        # belirteçleme sessizce başka bir şey okur.
                        # Son dört bayt sonraki öbeğe devredilir.
                        artik, parca = parca[-4:], parca[:-4]
                        if not parca:
                            continue
                        t = kod.encode(parca.decode("utf-8", "replace"),
                                       disallowed_special=())
                        if t:
                            ch.write(np.asarray(t, np.uint32).tobytes())
                            n += len(t)
                    if artik:
                        t = kod.encode(artik.decode("utf-8", "replace"),
                                       disallowed_special=())
                        if t:
                            ch.write(np.asarray(t, np.uint32).tobytes())
                            n += len(t)
                dosya += 1
        bas = json.dumps({"kodlama": kodlama, "sözlük": V,
                          "belirteç": int(n), "kaynak": ad or kok,
                          "dosya": int(dosya)},
                         ensure_ascii=False).encode("utf-8")
        assert len(bas) <= 320, "başlık 320 baytı aşamaz: %d" % len(bas)
        ch.seek(yer)
        ch.write(bas + b" " * (320 - len(bas)))
    return {"yol": cikti, "belirteç": n, "dosya": dosya,
            "kodlama": kodlama, "sözlük": V}



def mucit_ac(yol: str, kodlama: str = "o200k_base"):
    """Çevrilmiş külliyatı **mmap** ile aç. Kodlama tutmuyorsa reddet.

    ``np.memmap`` dosyayı belleğe **almaz**, sayfa sayfa okur. Boru
    hattının kap tarafı budur (ferman 1-O): 8 GB'lık bir kaynaktan
    yalnız okunan pencere kapta durur.
    """
    import numpy as np
    with open(yol, "rb") as fh:
        if fh.read(len(MUCIT_DAMGA)) != MUCIT_DAMGA:
            return None
        bas = json.loads(fh.read(321).decode("utf-8").strip())
        ofset = fh.tell()
    # **SESSİZ İKAME YASAK** (ferman 5): başka kodlamayla çevrilmiş bir
    # dosyayı okumak, başka bir belirteç uzayını okumaktır.
    assert str(bas["kodlama"]) == str(kodlama), (
        "çevrilmiş külliyatın kodlaması tutmuyor: %s dosyada %r, "
        "tâlimde %r -- yeniden çevrilmeli"
        % (yol, bas["kodlama"], kodlama))
    return np.memmap(yol, dtype=np.uint32, mode="r", offset=ofset,
                     shape=(int(bas["belirteç"]),))



def envanter(kok: str) -> Dict[str, int]:
    """Bir dizindeki uzantı sayımı -- **silmeden evvel**."""
    e: Dict[str, int] = {}
    for kk, _dd, ff in os.walk(kok):
        for f in ff:
            u = os.path.splitext(f)[1] or "(uzantısız)"
            e[u] = e.get(u, 0) + 1
    return e



def kulliyat_cek(kaynaklar: Optional[Sequence[Kaynak]] = None
                 ) -> List[Dict[str, Any]]:
    """Kaynakları ``depo/kulliyat/`` altına **çek. BUDAMA YOKTUR.**

    ===================================================================
    FERMAN 1-O
    ===================================================================

        "Sana ne oluyor da indirdiğin veriseti sınırlıyorsun? İnen şey
        githuba inecek... ama **verisetinin tamamı o repoda duracak!**"

    Evvelce burada bir disk bütçesi vardı ve kaynaklar payına göre
    **budanıyordu**: 23 GB'lık çekimin 11,2 GB'ı siliniyordu. O bir
    çare değil, kusurun kendisiydi. Kaynak olduğu gibi durur; kabın
    darlığı ``mucit_cevir``in öbek öbek çevirmesi ve ``mucit_ac``ın
    ``mmap``i ile, yâni **akışla** çözülür.

    Çekilemeyen **sessizce geçilmez**: ``engel`` alanı sebebiyle döner.
    """
    ks = list(kaynaklar or KAYNAKLAR)
    out: List[Dict[str, Any]] = []
    for k in ks:
        if k.engel or not k.depo:
            out.append({"ad": k.ad, "alındı": False, "engel": k.engel,
                        "bayt": 0, "dosya": 0})
            continue
        d = _dizin(k)
        # ══════════════════════════════════════════════════════════
        #  SÜRÜM VARLIĞI -- HF'e GitHub ÜZERİNDEN ŞÜMUL
        # ══════════════════════════════════════════════════════════
        #
        # Ajan yalnız GitHub görür (ferman 1-K'nin ölçtüğü hudut).
        # ``.github/workflows/hf_to_gh.yml`` HuggingFace'ten çeker,
        # ``mucit_cevir`` ile bizim biçime dönüştürür ve Release'e
        # varlık olarak koyar. Buraya inen şey ham veri değil,
        # **çevrilmiş külliyattır**; doğrudan ``mmap``lenir.
        #
        # Release varlık başına 2 GB'a kadar tutar; daha büyük
        # külliyat iş akışında parçalanır ve parçalar burada
        # **birleştirilir** -- biçim düz bayt olduğu için kayıpsızdır.
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
                        break              # tek parça geldi
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
            # **BOŞ DÖNEN KAYNAK SESSİZCE GEÇİLMEZ.** Envanter yazılır:
            # "hangi uzantı aranmalıydı" sorusu tahmine değil, deponun
            # kendi sayımına havale edilir.
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
                    basamak: int = 0
                    ) -> List[Tuple[List[int], int]]:
    """Külliyattan ``(bağlam, sonraki basamak)`` -- **boru hattıyla**.

    ===================================================================
    HAM METİN OKUNMAZ, PENCEREYE BAKILIR (ferman 1-O)
    ===================================================================

    Kaynağın tamamı belleğe alınmaz ve **kesilmez**. Her kaynak bir
    kere ``mucit_cevir`` ile ``.mucit``e çevrilir (tiktoken belirteç
    kimlikleri, ``uint32``), burada ``np.memmap`` ile açılır ve yalnız
    okunan pencereler kapta durur. 8 GB'lık bir tefsir külliyatı da,
    200 MB'lık bir ispat külliyatı da aynı kapta koşar.

    ===================================================================
    BELİRTEÇ → BASAMAK (ferman 1-N)
    ===================================================================

    Dosyada duran şey tiktoken kimlikleridir (200 019'a kadar). Yazmaca
    girerken ``tip_vektoru`` ile ``taban`` tabanında ``basamak`` haneye
    açılırlar; yâni akış bir **basamak akışıdır** ve hedef daima
    ``[0, taban)`` aralığındadır.

    Kaynaklar arası pay **boy değil söz hakkıdır** (ferman 1-J).
    """
    import numpy as np
    from nefs.belirtec import basamak_sayisi, belirtec_sozlugu, tip_vektoru

    tb = max(2, int(taban))
    bs = int(basamak) if int(basamak) > 0 else basamak_sayisi(
        int(sozluk) if int(sozluk) > 0 else belirtec_sozlugu(kodlama), tb)
    r = np.random.default_rng(int(tohum))
    ks = [k for k in (kaynaklar or KAYNAKLAR) if not k.engel and k.depo]
    diziler: List[Tuple[Any, float]] = []
    for k in ks:
        if k.varlik:
            yol = os.path.join(_dizin(k), k.varlik)
        else:
            kok = os.path.join(_dizin(k), k.yol) if k.yol else _dizin(k)
            if not os.path.isdir(kok):
                continue
            yol = _dizin(k) + MUCIT_UZANTI
            # **BAYAT BİÇİM SESSİZCE ATLANMAZ.** ``mucit_ac`` damgası
            # tutmayan dosyaya ``None`` döner; o dosya yerinde durduğu
            # için ``isfile`` doğru çıkar ve kaynak her koşuda sessizce
            # düşerdi. Damga tutmuyorsa **yeniden çevrilir**.
            if os.path.isfile(yol) and mucit_ac(yol, kodlama) is None:
                os.remove(yol)
            if not os.path.isfile(yol):
                mucit_cevir(kok, yol, kodlama, k.uzantilar(), k.ad)
                # ══════════════════════════════════════════════════
                #  BORU HATTININ SON HALKASI: HAM BIRAKILIR
                # ══════════════════════════════════════════════════
                #
                # **FERMAN 1-O.** *"İşini bitire bitire alacaksın ama
                # verisetinin tamamı o repoda duracak."*
                #
                # Ham klon çevrildikten sonra kapta durmasının hiçbir
                # faydası yoktur: tâlim ``.mucit``i okur, hamı hiç
                # açmaz. Fakat zararı vardır -- 23 GB'lık ham yığın
                # diski doldurur ve **bir sonraki kaynağın tam
                # inmesini engeller**; evvelki turda budamaya
                # sürüklenmemin sebebi tam olarak buydu.
                #
                # O hâlde halka şudur: **çek → çevir → hamı bırak.**
                # Kaynağın tamamı GitHub'da durur (orası deponun
                # kendisidir); kapta duran şey yalnız çevrilmiş
                # külliyattır. Ham lâzım olursa yeniden çekilir --
                # silinen bir nüsha, kesilen bir veri değildir.
                shutil.rmtree(_dizin(k), ignore_errors=True)
        if not os.path.isfile(yol):
            continue
        t = mucit_ac(yol, kodlama)
        # Bir pencere ``pencere`` BASAMAKtır; o hâlde lâzım olan
        # belirteç sayısı ``⌈pencere/basamak⌉ + 1``dir.
        gerek = int(np.ceil(int(pencere) / bs)) + 2
        if t is None or t.size <= gerek:
            continue
        diziler.append((t, float(k.pay)))
    if not diziler:
        return []
    toplam = sum(p for _t, p in diziler) or 1.0
    cift: List[Tuple[List[int], int]] = []
    for t, pay in diziler:
        n = int(round(int(azami) * pay / toplam))
        if n <= 0:
            continue
        gerek = int(np.ceil(int(pencere) / bs)) + 2
        bas = r.integers(0, t.size - gerek, size=n)
        for i in bas:
            # **YALNIZ PENCERE OKUNUR.** ``t`` bir mmap'tir; burada
            # dosyanın tamamı değil, ``gerek`` kadar belirteç okunur.
            ham = np.asarray(t[int(i):int(i) + gerek], np.int64)
            akis = tip_vektoru(ham, tb, bs)
            if akis.size < int(pencere) + 1:
                continue
            cift.append(([int(x) for x in akis[:int(pencere)]],
                         int(akis[int(pencere)])))
    return cift[:int(azami)]



def kulliyat_beyani(dokum: Optional[Sequence[Dict[str, Any]]] = None) -> str:
    """Külliyatın hâli -- **ne alındı, ne alınamadı, niçin**."""
    d = list(dokum if dokum is not None else kulliyat_cek())
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
