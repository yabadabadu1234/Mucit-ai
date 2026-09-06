"""
BELİRTEÇ -- TİKTOKEN KAPISI VE TİP VEKTÖRÜ

===================================================================
PADİŞAHIN HÜKMÜ (ferman 1-N)
===================================================================

    "Workflowda bana sözlük boyutu sorup 16 demişsin, bu ne rezalet,
    sence ultramath verisetinde 16 token mi var, tiktoken kadar token
    mi var? Ana tokenizer ister arc ister metin, ne olursa olsun **her
    daim tiktokendir**, sen tiktokenin altındaki mekanizmayı değiştirip
    bizim tip vektörleri yapacaksın! Tüm ayarlarda sözlük ebatını sen
    değil **tiktoken belirleyecek, otomatik!!**"

===================================================================
NE YANLIŞTI -- SAKLANMIYOR
===================================================================

``sozluk = 16`` bir kök diye yazılıydı ve bütün mimarî ona
oturuyordu: ``belirtecleri_kodla`` belirteci ``mod 16`` alıp **tek
sıcak** (one-hot) bir vektöre yazıyordu, yâni *belirteç, veri lifinin
bir taban durumunun kendisiydi*. O yapıda 16'dan fazla belirteç
**imkânsızdır**; külliyat da baytlara indirilip ``mod 16`` alınıyordu.

Bu bir tercih değil, bir kısıttı ve kısıt yanlış yerden geliyordu:
belirteç uzayının ebadını taşıyıcı tayin edemez. Tiktoken
``o200k_base``de 200 019 belirteç vardır; onu 16'ya indirmek
"metni öğrendik" demeyi imkânsız kılar.

===================================================================
DEĞİŞEN ŞEY TİKTOKEN DEĞİL, ALTINDAKİ MEKANİZMADIR
===================================================================

Tiktoken belirteç **kimliğini** verir. O kimliğin taşıyıcıya nasıl
gireceği bizimdir ve **tip vektörüdür**::

    t ∈ [0, V)  →  (b₀, b₁, …, b_{n−1}) ,  bᵢ ∈ [0, taban)
    t = Σ bᵢ · taban^i        (taban = veri lifi, n = basamak)

Her basamak **bir qudit seviyesidir**; yâni bir belirteç ``n`` satır
işgal eder. Böylece::

    sözlük 200 019 , taban 16  →  basamak 5      (16⁵ = 1 048 576)
    sözlük  50 257 , taban 16  →  basamak 4      (16⁴ =    65 536)

ve ``d = taban · karo²`` **hiç büyümez**. Sürekli bir "embedding
matrisi" yoktur: gömme, kimliğin kendi basamak açılımıdır ve
**tersinirdir** -- ``tipten`` onu birebir geri verir.

===================================================================
BPE TABLOSU: BU KAPTA NASIL BULUNUYOR (ferman 1-F)
===================================================================

Tiktoken birleştirme tablosunu ``openaipublic.blob.core.windows.net``
adresinden indirir ve o adres bu oturumda **kapalıdır** (ölçüldü:
``000``, tünel kurulamıyor). Ferman 1-F: *"Donanım yoksa yol aranır,
talimat kısaltılmaz."*

Yol bulundu ve GitHub'dadır: ``zurawiki/tiktoken-rs`` deposu
``tiktoken-rs/assets/`` altında ``cl100k_base.tiktoken`` ve
``o200k_base.tiktoken`` dosyalarını **aynen** taşır. Tiktoken'in kendi
önbellek kaidesi de koddan okundu (``tiktoken/load.py``)::

    cache_key  = sha1(blobpath).hexdigest()
    cache_path = TIKTOKEN_CACHE_DIR / cache_key

O hâlde dosya oraya konur ve tiktoken **hiç ağa çıkmadan** açılır.
Tiktoken ayrıca içeriği ``sha256`` ile denetler; yâni GitHub'dan gelen
nüshanın aslıyla aynı olduğu **kendi kodunca** doğrulanır. Bir ikame
değildir: aynı tablodur ve öyle olduğu ölçülür.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["Kodlama", "KODLAMALAR", "belirtec_kapisi", "belirtec_sozlugu",
           "basamak_sayisi", "tip_vektoru", "tipten", "belirtec_beyani",
           "BPE_DEPOSU", "onbellek_dizini"]

#: BPE tablosunu **aynen** taşıyan umumi GitHub deposu. Yoklandı:
#: ``tiktoken-rs/assets/`` altında dört kodlamanın tablosu duruyor.
BPE_DEPOSU = "zurawiki/tiktoken-rs"
BPE_YOLU = "tiktoken-rs/assets"


@dataclass(frozen=True)
class Kodlama:
    """Bir tiktoken kodlaması: adı, ağ adresi ve aslının özeti.

    ``blobpath`` tiktoken'in **kendi** sabitidir
    (``tiktoken_ext/openai_public.py``); önbellek anahtarı onun
    ``sha1``idir. ``ozet`` yine tiktoken'in beklediği ``sha256``dır ve
    GitHub'dan gelen nüshayı tiktoken kendisi onunla denetler.
    """

    ad: str
    blobpath: str
    ozet: str
    dosya: str


#: Yoklanmış kodlamalar. Her satırın dosyası ``BPE_DEPOSU``nda vardır.
KODLAMALAR: Tuple[Kodlama, ...] = (
    Kodlama(ad="o200k_base",
            blobpath="https://openaipublic.blob.core.windows.net/"
                     "encodings/o200k_base.tiktoken",
            ozet="446a9538cb6c348e3516120d7c08b09f57c36495"
                 "e2acfffe59a5bf8b0cfb1a2d",
            dosya="o200k_base.tiktoken"),
    Kodlama(ad="cl100k_base",
            blobpath="https://openaipublic.blob.core.windows.net/"
                     "encodings/cl100k_base.tiktoken",
            ozet="223921b76ee99bde995b7ff738513eef100fb51d"
                 "18c93597a113bcffe865b2a7",
            dosya="cl100k_base.tiktoken"),
)

#: Açılmış kodlamalar -- bir kere açılır, koşu boyunca durur.
_KAPI: Dict[str, Any] = {}
_SAYAC: Dict[str, float] = {"kodlama": 0.0, "coz": 0.0, "belirtec": 0.0,
                            "yerlestirme": 0.0}


def onbellek_dizini() -> str:
    """Tiktoken'in okuyacağı önbellek dizini -- **koddan okundu**.

    ``tiktoken/load.py:read_file_cached`` sırayla ``TIKTOKEN_CACHE_DIR``
    ve ``DATA_GYM_CACHE_DIR``a bakar. Birini biz kurarız ki dosyayı
    koyduğumuz yerle tiktoken'in baktığı yer **aynı** olsun; ikisi ayrı
    olursa tablo yerinde durur, tiktoken yine ağa çıkar ve düşer.
    """
    d = os.environ.get("TIKTOKEN_CACHE_DIR") \
        or os.environ.get("DATA_GYM_CACHE_DIR")
    if not d:
        d = os.path.join(os.environ.get("MUCIT_KULLIYAT", "depo/kulliyat"),
                         "tiktoken")
        os.environ["TIKTOKEN_CACHE_DIR"] = d
    os.makedirs(d, exist_ok=True)
    return d


def _kodlama(ad: str) -> Kodlama:
    for k in KODLAMALAR:
        if k.ad == ad:
            return k
    raise ValueError(
        "bilinmeyen kodlama %r; yoklanmışlar: %s"
        % (ad, ", ".join(k.ad for k in KODLAMALAR)))


def bpe_yerlestir(ad: str) -> Dict[str, Any]:
    """BPE tablosunu GitHub'dan al ve tiktoken'in önbelleğine koy.

    Zaten yerindeyse **hiçbir şey yapmaz**. Alınamıyorsa sessizce
    geçilmez: ``assert`` ile durur ve sebebi yazılır (ferman 5).
    """
    k = _kodlama(ad)
    onb = onbellek_dizini()
    anahtar = hashlib.sha1(k.blobpath.encode()).hexdigest()
    hedef = os.path.join(onb, anahtar)
    if os.path.isfile(hedef) and os.path.getsize(hedef) > 0:
        return {"kodlama": ad, "yol": hedef, "yerleştirildi": False,
                "bayt": os.path.getsize(hedef)}
    kok = os.path.join(onb, "_bpe_deposu")
    if not os.path.isdir(os.path.join(kok, ".git")):
        shutil.rmtree(kok, ignore_errors=True)
        r = subprocess.run(
            ["git", "clone", "--depth", "1", "--filter=blob:none",
             "https://github.com/" + BPE_DEPOSU, kok],
            capture_output=True, text=True,
            env=dict(os.environ, GIT_LFS_SKIP_SMUDGE="1"), timeout=1800)
        assert r.returncode == 0, (
            "BPE tablosu alınamadı -- belirteçleyici olmadan tâlim "
            "başlayamaz.\n  depo : %s\n  sebep: %s\n"
            "  (tiktoken'in kendi adresi bu kapta kapalı: "
            "openaipublic.blob.core.windows.net → 000)"
            % (BPE_DEPOSU, (r.stderr or "").strip()[-300:]))
    kaynak = os.path.join(kok, BPE_YOLU, k.dosya)
    if not os.path.isfile(kaynak):
        r = subprocess.run(["git", "-C", kok, "checkout", "HEAD", "--",
                            os.path.join(BPE_YOLU, k.dosya)],
                           capture_output=True, text=True, timeout=900)
        assert r.returncode == 0 and os.path.isfile(kaynak), (
            "BPE dosyası depoda bulunamadı: %s/%s/%s -- %s"
            % (BPE_DEPOSU, BPE_YOLU, k.dosya, (r.stderr or "").strip()[-200:]))
    # **ASLIYLA AYNI MI -- ÖLÇÜLÜR, KABUL EDİLMEZ.** Tiktoken zaten
    # ``sha256`` denetler; biz de koymadan evvel bakarız ki bozuk bir
    # nüsha önbelleğe girip her koşuda yeniden indirilmeye çalışmasın.
    with open(kaynak, "rb") as f:
        ham = f.read()
    olculen = hashlib.sha256(ham).hexdigest()
    assert olculen == k.ozet, (
        "BPE tablosunun özeti tutmuyor -- bu, tiktoken'in beklediği "
        "tablo DEĞİLDİR.\n  beklenen: %s\n  ölçülen : %s\n  dosya   : %s"
        % (k.ozet, olculen, kaynak))
    gecici = hedef + ".yaz"
    with open(gecici, "wb") as f:
        f.write(ham)
    os.replace(gecici, hedef)
    _SAYAC["yerlestirme"] += 1.0
    return {"kodlama": ad, "yol": hedef, "yerleştirildi": True,
            "bayt": len(ham), "sha256": olculen}


def belirtec_kapisi(ad: str = "o200k_base"):
    """Tiktoken kodlamasını aç. **Bir kere açılır**, sonra hatırlanır."""
    if ad in _KAPI:
        return _KAPI[ad]
    bpe_yerlestir(ad)
    import tiktoken

    kod = tiktoken.get_encoding(ad)
    _KAPI[ad] = kod
    return kod


def belirtec_sozlugu(ad: str = "o200k_base") -> int:
    """**SÖZLÜK EBADI: ÖLÇÜLÜR, YAZILMAZ** (ferman 1-N)."""
    return int(belirtec_kapisi(ad).n_vocab)


def basamak_sayisi(sozluk: int, taban: int) -> int:
    """``⌈log_taban(sözlük)⌉`` -- bir belirteç kaç qudit basamağı tutar.

    Tamsayı ile hesaplanır; ``math.log`` kayan nokta gürültüsüyle
    hudutta bir basamak eksik verebilir ve o zaman sözlüğün üst ucu
    **sessizce sarılırdı**.
    """
    t, n, kap = max(2, int(taban)), 1, max(2, int(taban))
    while kap < int(sozluk):
        kap *= t
        n += 1
    return int(n)


def tip_vektoru(belirtecler: Sequence[int], taban: int, basamak: int
                ) -> np.ndarray:
    """Belirteç kimliklerini **tip vektörüne** aç: ``(n·basamak,)``.

    Her belirteç ``basamak`` adet ``[0, taban)`` basamağına açılır ve
    basamaklar **düşük anlamlıdan yükseğe** sıralanır. Sıra keyfî
    değildir: düşük basamak belirteçler arasında en çok değişen
    kısımdır, o hâlde yazmacın ilk (en sık vurulan) seviyesine düşer.
    """
    t = np.asarray(belirtecler, np.int64).reshape(-1)
    b, n = max(2, int(taban)), max(1, int(basamak))
    out = np.empty((t.size, n), np.int64)
    kalan = t.copy()
    for i in range(n):
        out[:, i] = kalan % b
        kalan //= b
    return out.reshape(-1)


def tipten(basamaklar: Sequence[int], taban: int, basamak: int
           ) -> np.ndarray:
    """Tip vektöründen belirteç kimliğine -- **tersi, birebir**.

    Gömmenin tersinir olduğu iddia edilmez, **kurulur**: bu fonksiyon
    ``tip_vektoru``nün tersidir ve ikisi arasında kayıp yoktur.
    """
    a = np.asarray(basamaklar, np.int64).reshape(-1, max(1, int(basamak)))
    b = max(2, int(taban))
    carp = b ** np.arange(a.shape[1], dtype=np.int64)
    return (a * carp[None, :]).sum(axis=1)


def belirtecle(metin, ad: str = "o200k_base") -> List[int]:
    """Metni (yahut baytı) belirteçle. **Tek kapı budur** (ferman 1-N)."""
    kod = belirtec_kapisi(ad)
    if isinstance(metin, (bytes, bytearray)):
        metin = bytes(metin).decode("utf-8", "replace")
    t = kod.encode(str(metin), disallowed_special=())
    _SAYAC["kodlama"] += 1.0
    _SAYAC["belirtec"] += float(len(t))
    return list(t)


def coz(belirtecler: Sequence[int], ad: str = "o200k_base") -> str:
    """Belirteçten metne -- modelin ne söylediği **okunabilsin** diye."""
    _SAYAC["coz"] += 1.0
    return belirtec_kapisi(ad).decode(
        [int(x) % int(belirtec_sozlugu(ad)) for x in belirtecler])


def belirtec_beyani(ad: str = "o200k_base") -> Dict[str, Any]:
    """Belirteç uzayının hâli -- **iddia değil, sayı** (ferman 5)."""
    acik = ad in _KAPI
    return {"kodlama": ad, "açık": acik,
            "sözlük": int(_KAPI[ad].n_vocab) if acik else 0,
            "kodlama_çağrısı": int(_SAYAC["kodlama"]),
            "çözme_çağrısı": int(_SAYAC["coz"]),
            "belirteç": int(_SAYAC["belirtec"]),
            "bpe_yerleştirme": int(_SAYAC["yerlestirme"]),
            "önbellek": onbellek_dizini()}
