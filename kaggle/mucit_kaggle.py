"""Kaggle Script kerneli -- Mucit-ai'yi Kaggle'da koşturur, hazineyi ve
külliyatı bir Kaggle Dataset'e sevk ederek konteyner kapanınca da veriyi
kalıcı tutar.

Bu dosyayı Kaggle'a bir "Script" türü kernel olarak yükle
(kernel-metadata.json ile ``kaggle kernels push``), yahut içeriğini bir
Notebook hücresine yapıştır. Kernel ayarlarında İNTERNET AÇIK olmalı
(GitHub'dan çekmek ve Kaggle API çağrıları için).

Tek seferlik hazırlık (elle, Kaggle tarafında):
  1. Bir Kaggle hesabı (ulankaggle) ve API jetonu -- kernelin "Add-ons >
     Secrets" bölümünden KAGGLE_USERNAME / KAGGLE_KEY olarak eklenir
     (kullanıcı adı + şifre DEĞİL, kaggle.json'daki gerçek jeton).
  2. Veriseti: ulankaggle/zekayi-mucidani-osmani (başlığı "Zekayı
     Mucidanı Osmani"). İlk koşuda böyle bir veriseti henüz yoksa kod
     bunu algılar ve boş depo ile başlar; ilk ``nöbetçi`` tetiklendiğinde
     veriseti PUBLIC olarak oluşturulur (private verisetleri Kaggle'da
     çok daha dar bir hadde çarpar).
"""
from __future__ import annotations

import os
import subprocess
import sys

REPO_URL = os.environ.get("MUCIT_REPO_URL",
                          "https://github.com/yabadabadu1234/Mucit-ai")
REPO_DAL = os.environ.get("MUCIT_REPO_DAL", "main")
CALISMA = "/kaggle/working/Mucit-ai"

# --- Padişahın belirlediği tek kabza: veriseti adı ve profil -----------
os.environ.setdefault("MUCIT_KAGGLE_VERISETI",
                      "ulankaggle/zekayi-mucidani-osmani")
os.environ.setdefault("MUCIT_KAGGLE_BASLIK", "Zekayı Mucidanı Osmani")
os.environ.setdefault("MUCIT_KAGGLE_HADDI", str(15 << 30))  # 15 GiB
PROFIL = os.environ.get("MUCIT_PROFIL", "orta")
TUR_SAYISI = int(os.environ.get("MUCIT_TUR", "1000000"))


def _kos(komut, **kw):
    r = subprocess.run(komut, **kw)
    if r.returncode != 0:
        raise RuntimeError("komut düştü: %r (kod %d)" % (komut, r.returncode))
    return r


def _depoyu_hazirla() -> None:
    if os.path.isdir(os.path.join(CALISMA, ".git")):
        _kos(["git", "-C", CALISMA, "pull", "--ff-only"])
        return
    _kos(["git", "clone", "--depth", "1", "--branch", REPO_DAL,
         REPO_URL, CALISMA])


def _ortami_kur() -> None:
    os.environ.setdefault("MUCIT_HAZINE", os.path.join(CALISMA, "depo",
                                                        "hazine"))
    os.environ.setdefault("MUCIT_KULLIYAT", os.path.join(CALISMA, "depo",
                                                          "kulliyat"))
    sys.path.insert(0, CALISMA)
    os.chdir(CALISMA)


def basla() -> None:
    _depoyu_hazirla()
    _ortami_kur()
    assert os.environ["MUCIT_KAGGLE_VERISETI"], (
        "MUCIT_KAGGLE_VERISETI boş -- kalıcılığın gideceği veriseti adı "
        "verilmeden koşulmaz (ferman 5): script başında "
        "os.environ['MUCIT_KAGGLE_VERISETI'] = '<kullanıcı>/<slug>' yaz")
    from main.egitim import kos
    from main.kaggle_koprusu import (kaggle_hazir_mi, veriseti_gonder,
                                     dogrula_ve_bosalt, depo_boyutu)

    slug = os.environ["MUCIT_KAGGLE_VERISETI"]
    try:
        for tur in range(int(TUR_SAYISI)):
            print("=== MUCIT-AI KAGGLE TUR %d (profil=%s) ==="
                 % (tur, PROFIL), flush=True)
            kos(PROFIL, cikti=os.path.join("depo", "olcum"))
    finally:
        if kaggle_hazir_mi()["hazır"] and depo_boyutu("depo") > 0:
            print("=== OTURUM BİTİYOR -- SON SEVK ===", flush=True)
            veriseti_gonder(slug, "depo")
            dogrula_ve_bosalt(slug, "depo")


if __name__ == "__main__":
    basla()
