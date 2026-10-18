"""Yarışma görevleri için karma test ortamı.

Her görev için: temel commit'in bağımlılık dosyaları (pyproject.toml, setup.cfg, setup.py,
requirements*.txt) özetlenir; aynı özeti paylaşan görevler tek ortamı kullanır.
Ortam kurulumu iki kademelidir:
  1. çevrimdışı: yarışmanın wheels klasörü (--no-index --find-links)
  2. PyPI: çevrimdışı kurulum başarısız olursa (eksik bağımlılık) PyPI'den
Hangi kademenin kullanıldığı ("cevrimdisi" | "pypi") ortam meta verisine yazılır ve türetilen
F2P/P2P etiketlerine eklenir; böylece etiketin hangi ortamda üretildiği her zaman görünür.

Ortam Python 3.13 venv'idir (yarışma imajıyla aynı); pytest ve pytest-timeout==2.1.0 ile birlikte
imp.py ve telnetlib.py uyumluluk dosyaları kopyalanır (docker/ klasöründen).
"""
import hashlib
import json
import os
import shutil
import subprocess
import tempfile

from swe_dogrula import agaci_ac, EnvHatasi  # noqa: F401  (agaci_ac: ağaç açma)

ORTAM_KOKU = os.environ.get("YARISMA_ORTAM", os.path.join(tempfile.gettempdir(), "yarisma_ortam"))
TEKERLEK_KLASORU = os.environ.get("YARISMA_WHEELS", "")
UYUMLULUK_DOSYALARI = os.environ.get("YARISMA_DOCKER", "")  # imp.py ve telnetlib.py'nin bulunduğu dizin
PYTHON = os.environ.get("YARISMA_PYTHON313", "/usr/bin/python3.13")


def _calistir(komut, cwd=None, zaman=900):
    r = subprocess.run(komut, cwd=cwd, capture_output=True, text=True, timeout=zaman)
    return r.returncode, (r.stdout + r.stderr)[-2000:]


def bagimlilik_anahtari(agac):
    """Bağımlılık dosyalarının içeriğinin özeti. Aynı özet = aynı ortam."""
    h = hashlib.sha256()
    for ad in ("pyproject.toml", "setup.cfg", "setup.py"):
        yol = os.path.join(agac, ad)
        if os.path.exists(yol):
            h.update(ad.encode() + b"\0" + open(yol, "rb").read())
    for ad in sorted(os.listdir(agac)):
        if ad.startswith("requirements") and ad.endswith(".txt"):
            h.update(ad.encode() + b"\0" + open(os.path.join(agac, ad), "rb").read())
    return h.hexdigest()[:16]


def test_bagimliliklari(agac):
    """pyproject.toml'daki test bağımlılıkları: [dependency-groups] 'tests' (include-group dâhil)
    ve [project.optional-dependencies] içindeki 'tests'/'test'. Yoksa boş liste."""
    yol = os.path.join(agac, "pyproject.toml")
    if not os.path.exists(yol):
        return []
    import tomllib

    with open(yol, "rb") as f:
        veri = tomllib.load(f)
    gruplar = veri.get("dependency-groups", {})
    sonuc, gorulen = [], set()

    def grup_topla(ad):
        if ad in gorulen or ad not in gruplar:
            return
        gorulen.add(ad)
        for oge in gruplar[ad]:
            if isinstance(oge, str):
                sonuc.append(oge)
            elif isinstance(oge, dict) and "include-group" in oge:
                grup_topla(oge["include-group"])

    grup_topla("tests")
    for ad in ("tests", "test"):
        sonuc.extend(veri.get("project", {}).get("optional-dependencies", {}).get(ad, []))
    return sonuc


def _surum_anahtari(surum):
    """'0.52.1' -> (0, 52, 1); sayısal olmayan parçalar için yalnız sayısal kısım."""
    parcalar = []
    for p in surum.split("."):
        rakam = "".join(c for c in p if c.isdigit())
        parcalar.append(int(rakam) if rakam else 0)
    return tuple(parcalar)


def tekerlek_kisitlari(klasor):
    """Her paket için klasördeki en yeni sürüme kadar üst sınır: 'paket<=sürüm' satırları.
    Wheel dosya adı: ad-sürüm-... (ad içindeki '-' '_' ile yazılmış)."""
    en_yeni = {}
    for ad in os.listdir(klasor):
        if not ad.endswith(".whl"):
            continue
        parcalar = ad.split("-")
        if len(parcalar) < 2:
            continue
        paket = parcalar[0].lower().replace("_", "-")
        surum = parcalar[1]
        if paket not in en_yeni or _surum_anahtari(surum) > _surum_anahtari(en_yeni[paket]):
            en_yeni[paket] = surum
    return "".join(f"{p}<={s}\n" for p, s in sorted(en_yeni.items()))


def _bagimlilik_tutarli(py):
    """pip check: kurulu paketlerin bağımlılıkları eksiksiz mi? Eksikse kurulum sayılmaz."""
    rc, _ = _calistir([py, "-m", "pip", "check"])
    return rc == 0


def _venv_hazirla(dizin):
    rc, cikti = _calistir([PYTHON, "-m", "venv", dizin])
    if rc != 0:
        raise EnvHatasi(f"venv oluşturulamadı: {cikti}")
    py = os.path.join(dizin, "bin", "python")
    # Yarışma imajının (docker/Dockerfile.public) temel paketleri: pytest, pytest-timeout, typer
    _calistir([py, "-m", "pip", "install", "-q", "pytest", "pytest-timeout==2.1.0", "typer"])
    if UYUMLULUK_DOSYALARI:
        site = os.path.join(dizin, "lib", "python3.13", "site-packages")
        for ad in ("imp.py", "telnetlib.py"):
            kaynak = os.path.join(UYUMLULUK_DOSYALARI, ad)
            if os.path.exists(kaynak):
                shutil.copy(kaynak, site)
    return py


PROFILLER = {
    "varsayilan": "",
    # starlette 1.x testclient'ı httpx2 ister (yarışma setinde yok); 0.x sürümleri httpx kullanır.
    "starlette0": "starlette<1.0\n",
}


def ortam_kur(gorev, zaman=900, profil="varsayilan"):
    """Görev için (python, etiket) döner. Etiket: 'cevrimdisi' veya 'pypi', profil ile birlikte
    'etiket+profil' biçiminde. Aynı bağımlılık özeti + profil = aynı ortam (önbellek)."""
    if profil not in PROFILLER:
        raise ValueError(f"bilinmeyen profil: {profil}")
    agac = tempfile.mkdtemp(prefix="anahtar_")
    try:
        agaci_ac(gorev, agac)
        anahtar = bagimlilik_anahtari(agac) + "-" + profil
        kurulum = agac
        dizin = os.path.join(ORTAM_KOKU, anahtar)
        meta_yol = os.path.join(dizin, "meta.json")
        if os.path.exists(meta_yol):
            with open(meta_yol, encoding="utf-8") as f:
                meta = json.load(f)
            return meta["python"], meta["etiket"]
        os.makedirs(ORTAM_KOKU, exist_ok=True)
        py = _venv_hazirla(dizin)
        # Kısıtlar: tekerlek klasöründeki en yeni sürümler + profil ek kısıtı
        kisit = os.path.join(dizin, "kisitlar.txt")
        with open(kisit, "w", encoding="utf-8") as f:
            if TEKERLEK_KLASORU:
                f.write(tekerlek_kisitlari(TEKERLEK_KLASORU))
            f.write(PROFILLER[profil])
        test_deps = test_bagimliliklari(kurulum)
        etiket = None
        if TEKERLEK_KLASORU:
            rc, cikti = _calistir([py, "-m", "pip", "install", "-q", "--no-index",
                                   "--find-links", TEKERLEK_KLASORU, "-c", kisit,
                                   *test_deps, kurulum], zaman=zaman)
            if rc == 0 and _bagimlilik_tutarli(py):
                etiket = "cevrimdisi"
        if etiket is None:
            # PyPI kademesi: tekerlekte olmayan paketler (ör. typing-inspection) PyPI'den gelir.
            komut = [py, "-m", "pip", "install", "-q"]
            if TEKERLEK_KLASORU:
                komut += ["--find-links", TEKERLEK_KLASORU]
            komut += ["-c", kisit, *test_deps]
            rc, cikti = _calistir(komut + [kurulum], zaman=zaman)
            if rc != 0 or not _bagimlilik_tutarli(py):
                raise EnvHatasi(f"{gorev['instance_id']}: bağımlılıklar kurulamadı/tutarsız: {cikti[-400:]}")
            etiket = "pypi"
        os.makedirs(dizin, exist_ok=True)
        with open(meta_yol, "w", encoding="utf-8") as f:
            json.dump({"python": py, "etiket": etiket, "profil": profil, "anahtar": anahtar},
                      f, ensure_ascii=False)
        return py, etiket
    finally:
        shutil.rmtree(agac, ignore_errors=True)
