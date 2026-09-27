from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any, Dict, List, Optional, Tuple

__all__ = ["KAGGLE_VERISETI", "KAGGLE_CALISMA_HADDI", "kaggle_hazir_mi",
           "depo_boyutu", "veriseti_indir", "veriseti_gonder",
           "uzak_dosya_listesi", "dogrula_ve_bosalt", "nobetci",
           "koprusu_beyani"]

KAGGLE_VERISETI = os.environ.get("MUCIT_KAGGLE_VERISETI", "")

KAGGLE_CALISMA_HADDI = int(
    os.environ.get("MUCIT_KAGGLE_HADDI", str(15 << 30)))

_SAYAC: Dict[str, float] = {"indirme": 0.0, "gönderme": 0.0,
                            "boşaltılan_bayt": 0.0, "doğrulama_reddi": 0.0}


def koprusu_beyani() -> Dict[str, float]:
    return dict(_SAYAC)


def kaggle_hazir_mi() -> Dict[str, Any]:
    ikili = shutil.which("kaggle")
    kimlik = (os.path.isfile(os.path.expanduser("~/.kaggle/kaggle.json"))
             or bool(os.environ.get("KAGGLE_USERNAME"))
             and bool(os.environ.get("KAGGLE_KEY")))
    return {"ikili_var": bool(ikili), "kimlik_var": bool(kimlik),
            "veriseti": KAGGLE_VERISETI,
            "hazır": bool(ikili and kimlik and KAGGLE_VERISETI)}


def depo_boyutu(dizin: str = "depo") -> int:
    top = 0
    for kk, _dd, ff in os.walk(dizin):
        for f in ff:
            try:
                top += os.path.getsize(os.path.join(kk, f))
            except OSError:
                pass
    return int(top)


def veriseti_indir(slug: str, hedef: str = "depo") -> Dict[str, Any]:
    assert slug, (
        "Kaggle veriseti adı boş -- MUCIT_KAGGLE_VERISETI ortam "
        "değişkeni ayarlanmadı (ferman 5: sessiz atlanmaz)")
    os.makedirs(hedef, exist_ok=True)
    r = subprocess.run(
        ["kaggle", "datasets", "download", "-d", slug, "-p", hedef,
         "--unzip", "--force"],
        capture_output=True, text=True, timeout=3600)
    _SAYAC["indirme"] += 1.0
    if r.returncode != 0:
        dusuk = (r.stderr or "").lower()
        if "404" in dusuk or "not found" in dusuk:
            return {"indirildi": False, "sebep": "veriseti henüz yok "
                    "(ilk koşu olabilir) -- boş depo ile başlanıyor",
                    "ilk_kosu": True}
        raise AssertionError(
            "Kaggle verisetinden indirme düştü: %s\n%s"
            % (slug, (r.stderr or "").strip()[-500:]))
    return {"indirildi": True, "sebep": "", "ilk_kosu": False}


def veriseti_gonder(slug: str, kaynak: str = "depo",
                    mesaj: str = "mucit hazine + külliyat güncellemesi"
                    ) -> Dict[str, Any]:
    assert slug, "Kaggle veriseti adı boş -- gönderilecek yer yok"
    assert os.path.isdir(kaynak) and os.listdir(kaynak), (
        "gönderilecek %r boş -- boş veriseti sürümü açılmaz" % kaynak)
    meta_yolu = os.path.join(kaynak, "dataset-metadata.json")
    if not os.path.isfile(meta_yolu):
        with open(meta_yolu, "w", encoding="utf-8") as f:
            json.dump({"title": slug.split("/")[-1], "id": slug,
                      "licenses": [{"name": "CC0-1.0"}]}, f)
    r = subprocess.run(
        ["kaggle", "datasets", "version", "-p", kaynak, "-m", mesaj,
         "-r", "zip", "--dir-mode", "zip"],
        capture_output=True, text=True, timeout=7200)
    _SAYAC["gönderme"] += 1.0
    ilk_mi = "404" in (r.stderr or "") or "not found" in (r.stderr or "").lower()
    if r.returncode != 0 and ilk_mi:
        r = subprocess.run(
            ["kaggle", "datasets", "create", "-p", kaynak, "--public",
             "-r", "zip", "--dir-mode", "zip"],
            capture_output=True, text=True, timeout=7200)
    if r.returncode != 0:
        raise AssertionError(
            "Kaggle verisetine gönderme düştü: %s\n%s"
            % (slug, (r.stderr or "").strip()[-500:]))
    return {"gönderildi": True, "çıktı": (r.stdout or "").strip()[-300:]}


def uzak_dosya_listesi(slug: str) -> Dict[str, int]:
    r = subprocess.run(["kaggle", "datasets", "files", "-d", slug,
                       "--csv"], capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        return {}
    out: Dict[str, int] = {}
    satirlar = (r.stdout or "").strip().splitlines()
    for satir in satirlar[1:]:
        parcalar = satir.rsplit(",", 2)
        if len(parcalar) < 3:
            continue
        ad = parcalar[0].strip()
        try:
            bayt = int(float(parcalar[1].strip()))
        except ValueError:
            continue
        out[ad] = bayt
    return out


def dogrula_ve_bosalt(slug: str, dizin: str = "depo",
                      haric: Tuple[str, ...] = ("dataset-metadata.json",)
                      ) -> Dict[str, Any]:
    uzak = uzak_dosya_listesi(slug)
    assert uzak, (
        "UZAK DOSYA LİSTESİ BOŞ -- gönderimin gerçekten Kaggle'a "
        "ulaştığı doğrulanamadı, hiçbir yerel dosya silinmez (ferman 5: "
        "yoklanamayan bir şey üzerine imha kurulmaz)")
    silinen: List[str] = []
    korunan: List[str] = []
    bosalan = 0
    for kk, _dd, ff in os.walk(dizin):
        for f in ff:
            if f in haric or f.endswith(".kademe.json"):
                continue
            y = os.path.join(kk, f)
            try:
                yerel_boy = os.path.getsize(y)
            except OSError:
                continue
            uzak_boy = uzak.get(f)
            if uzak_boy is not None and int(uzak_boy) == int(yerel_boy):
                os.remove(y)
                silinen.append(y)
                bosalan += yerel_boy
            else:
                korunan.append(y)
    _SAYAC["boşaltılan_bayt"] += float(bosalan)
    if korunan:
        _SAYAC["doğrulama_reddi"] += 1.0
    return {"silinen": silinen, "korunan": korunan,
            "boşalan_bayt": int(bosalan)}


def nobetci(dizin: str = "depo", slug: Optional[str] = None,
           hadd_bayt: Optional[int] = None) -> Dict[str, Any]:
    slug = slug if slug is not None else KAGGLE_VERISETI
    hadd = int(hadd_bayt if hadd_bayt is not None else KAGGLE_CALISMA_HADDI)
    boy = depo_boyutu(dizin)
    if boy < hadd:
        return {"koştu": False, "boy": boy, "hadd": hadd}
    assert slug, (
        "ÇALIŞMA ALANI HADDİ AŞILDI (%d ≥ %d bayt) FAKAT "
        "MUCIT_KAGGLE_VERISETI TANIMLI DEĞİL -- boşaltacak yer yok, "
        "veri sessizce silinmez (ferman 5)" % (boy, hadd))
    gonderim = veriseti_gonder(slug, dizin)
    bosaltma = dogrula_ve_bosalt(slug, dizin)
    return {"koştu": True, "boy_önce": boy,
           "boy_sonra": depo_boyutu(dizin), "hadd": hadd,
           "gönderim": gonderim, "boşaltma": bosaltma}
