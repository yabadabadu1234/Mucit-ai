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

from swe_dogrula import agaci_ac, EnvHatasi

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


def ortam_kur(gorev, zaman=900):
    """Görev için (python, etiket) döner. Etiket: 'cevrimdisi' veya 'pypi'."""
    agac = tempfile.mkdtemp(prefix="anahtar_")
    try:
        agaci_ac(gorev["repo"], gorev["base_commit"], agac)
        anahtar = bagimlilik_anahtari(agac)
        kurulum = os.path.join(agac)  # bağımlılık kurulumu bu ağaçtan yapılır
        dizin = os.path.join(ORTAM_KOKU, anahtar)
        meta_yol = os.path.join(dizin, "meta.json")
        if os.path.exists(meta_yol):
            with open(meta_yol, encoding="utf-8") as f:
                meta = json.load(f)
            return meta["python"], meta["etiket"]
        os.makedirs(ORTAM_KOKU, exist_ok=True)
        py = _venv_hazirla(dizin)
        etiket = None
        if TEKERLEK_KLASORU:
            rc, cikti = _calistir([py, "-m", "pip", "install", "-q", "--no-index",
                                   "--find-links", TEKERLEK_KLASORU, kurulum], zaman=zaman)
            if rc == 0:
                etiket = "cevrimdisi"
        if etiket is None:
            rc, cikti = _calistir([py, "-m", "pip", "install", "-q", kurulum], zaman=zaman)
            if rc != 0:
                raise EnvHatasi(f"{gorev['instance_id']}: bağımlılıklar kurulamadı: {cikti[-400:]}")
            etiket = "pypi"
        with open(meta_yol, "w", encoding="utf-8") as f:
            json.dump({"python": py, "etiket": etiket, "anahtar": anahtar}, f, ensure_ascii=False)
        return py, etiket
    finally:
        shutil.rmtree(agac, ignore_errors=True)
