"""SWE-bench görevleri için gerçek doğrulayıcı.

Akış: depoyu temel commit'te aç -> test yamasını uygula -> model yamasını uygula -> F2P ve P2P
test kimliklerini pytest ile koş -> sonucu ölç.

Mesafe [0,1]: 1 − (F2P geçen oranı) · (P2P geçen oranı). Tam çözüm (her F2P ve her P2P geçer) = 0.
Yama uygulanamazsa mesafe = 1. Test yamasının uygulanmaması görev verisinin bozuk olduğunu gösterir
ve hata fırlatır (sessiz ikame yok).

Kullanım:
  python3 swe_dogrula.py ÖRNEK_ID --yama gold|DOSYA [--python PY] [--zaman 600]
  gold: görev verisindeki altın yama (doğrulayıcının kendi sınaması: sonuç resolved=True olmalı).

Not: test ortamı (bağımlılıklar) çağıran tarafından hazırlanır; --python o ortamın yorumlayıcısıdır.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

CACHE = os.environ.get("SWE_CACHE", os.path.join(tempfile.gettempdir(), "swe_cache"))
VERI_DOSYASI = os.environ.get("SWE_VERI", "")

SONUC_RE = re.compile(r"^(PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS) (.+)$", re.M)


def depo_yolu(repo):
    return os.path.join(CACHE, repo.replace("/", "__"))


def depoyu_hazirla(repo):
    """Depo yoksa klonlar; varsa olduğu gibi kullanır."""
    d = depo_yolu(repo)
    if not os.path.isdir(os.path.join(d, ".git")):
        os.makedirs(CACHE, exist_ok=True)
        subprocess.run(["git", "clone", "-q", f"https://github.com/{repo}.git", d], check=True)
    return d


ANLIK_GORUNTU_KLASORU = os.environ.get("SWE_SNAPSHOTS", "")


def agaci_ac(gorev, hedef):
    """Görevin temel durumunu hedef dizine açar.

    SWE_SNAPSHOTS tanımlıysa yarışmanın anlık görüntüsü (<instance_id>.tgz, .git hariç) kullanılır:
    içeriği temel commit ile aynıdır (test ve altın yamalar bu ağaca temiz uygulanır). Yoksa depo
    GitHub'dan klonlanıp temel commit'in ağacı git archive ile açılır.
    """
    os.makedirs(hedef, exist_ok=True)
    if ANLIK_GORUNTU_KLASORU:
        tgz = os.path.join(ANLIK_GORUNTU_KLASORU, f"{gorev['instance_id']}.tgz")
        if not os.path.exists(tgz):
            raise EnvHatasi(f"{gorev['instance_id']}: anlık görüntü yok: {tgz}")
        subprocess.run(["tar", "-xzf", tgz, "-C", hedef, "--exclude=./.git"], check=True)
        return
    kaynak = depoyu_hazirla(gorev["repo"])
    arsiv = subprocess.run(["git", "-C", kaynak, "archive", gorev["base_commit"]],
                           capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", hedef], input=arsiv, check=True)


def yama_uygula(hedef, yama, ad):
    """Yamayı git apply ile uygular. Başarılıysa True. Boş yama: False."""
    if not yama.strip():
        return False
    dosya = os.path.join(hedef, f".{ad}.diff")
    with open(dosya, "w", encoding="utf-8") as f:
        f.write(yama if yama.endswith("\n") else yama + "\n")
    try:
        r = subprocess.run(["git", "apply", "--whitespace=nowarn", dosya], cwd=hedef,
                           capture_output=True, text=True)
        return r.returncode == 0
    finally:
        os.remove(dosya)


def testleri_kos(hedef, kimlikler, python, zaman):
    """Test kimliklerini koşar; {kimlik: sonuç} döner. Zaman aşımında o ana kadarki çıktı okunur;
    toplanamayan (bulunamayan) kimlikler sonuç listesinde olmaz ve başarısız sayılır."""
    if not kimlikler:
        return {}
    komut = [python, "-m", "pytest", "-q", "-rA", "-p", "no:cacheprovider", "--no-header", "--tb=no",
             "--continue-on-collection-errors", *kimlikler]
    ortam = dict(os.environ, PYTHONPATH=hedef)
    try:
        r = subprocess.run(komut, cwd=hedef, capture_output=True, text=True, timeout=zaman, env=ortam)
        cikti = r.stdout
    except subprocess.TimeoutExpired as e:
        cikti = e.stdout.decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
    sonuc = {}
    for m in SONUC_RE.finditer(cikti):
        kimlik = m.group(2).split(" - ")[0].strip()
        sonuc.setdefault(kimlik, m.group(1))
    return sonuc


class EnvHatasi(RuntimeError):
    """Altın yama bu ortamda çözülemiyor: görev bu ortamda ölçülemez (veriye yazılmaz)."""


def _kosum(gorev, yama, python, zaman, ad):
    """Test yamasını ve verilen yamayı uygular, F2P+P2P kimliklerini koşar. (sonuç, f2p, p2p) döner;
    yama uygulanamazsa sonuç None."""
    hedef = tempfile.mkdtemp(prefix="swe_")
    try:
        agaci_ac(gorev, hedef)
        if not yama_uygula(hedef, gorev["test_patch"], "test"):
            raise RuntimeError(f"{gorev['instance_id']}: test yaması uygulanamadı (görev verisi bozuk)")
        if not yama_uygula(hedef, yama, ad):
            return None
        f2p = json.loads(gorev["FAIL_TO_PASS"])
        p2p = json.loads(gorev["PASS_TO_PASS"])
        sonuc = testleri_kos(hedef, f2p + p2p, python, zaman)
        if not sonuc:
            raise EnvHatasi(f"{gorev['instance_id']}: {ad} yamasıyla hiç test sonucu alınamadı")
        return sonuc
    finally:
        shutil.rmtree(hedef, ignore_errors=True)


def altin_kapi(gorev, python, zaman):
    """Altın yamayla ortam kapısı. Dönüş: ölçümden çıkarılacak P2P kimlikleri (ortamda bozuk olanlar).
    F2P'den biri bile altın yamada geçmiyorsa EnvHatasi: sinyal ortamdan gelmesin diye görev atlanır."""
    sonuc = _kosum(gorev, gorev["patch"], python, zaman, "gold")
    f2p = json.loads(gorev["FAIL_TO_PASS"])
    p2p = json.loads(gorev["PASS_TO_PASS"])
    f2p_bozuk = [t for t in f2p if sonuc.get(t) != "PASSED"]
    if f2p_bozuk:
        raise EnvHatasi(f"{gorev['instance_id']}: altın yamada F2P geçmiyor ({len(f2p_bozuk)}): {f2p_bozuk[:3]}")
    return [t for t in p2p if sonuc.get(t) != "PASSED"]


def test_dosyalari(test_yamasi):
    """Test yamasının dokunduğu test dosyaları. Her iki biçimi de okur:
    'diff --git a/X b/X' (SWE-bench) ve yalnız '+++ b/X' (yarışma verisi)."""
    dosyalar = []
    for m in re.finditer(r"^(?:diff --git a/\S+ b/|\+\+\+ b/)(\S+)", test_yamasi, re.M):
        yol = m.group(1)
        if "test" in yol.lower() and yol.endswith(".py") and yol not in dosyalar:
            dosyalar.append(yol)
    return dosyalar


def _turet_tek(gorev, python, zaman, etiket):
    """Tek ortamda türetme. Dönüş: (f2p, p2p) listeleri; F2P boşsa None (sebep çağırana bırakılır)."""
    kokler = sorted({yol.split("/")[0] for yol in test_dosyalari(gorev["test_patch"])})
    hedef = tempfile.mkdtemp(prefix="turet_")
    try:
        agaci_ac(gorev, hedef)
        if not yama_uygula(hedef, gorev["test_patch"], "test"):
            raise RuntimeError(f"{gorev['instance_id']}: test yaması uygulanamadı")
        temel = testleri_kos(hedef, kokler, python, zaman)
        if not yama_uygula(hedef, gorev["patch"], "gold"):
            raise RuntimeError(f"{gorev['instance_id']}: altın yama uygulanamadı")
        altin = testleri_kos(hedef, kokler, python, zaman)
        if not altin:
            raise EnvHatasi(f"{gorev['instance_id']}: altın yamayla hiç test sonucu alınamadı ({etiket})")
    finally:
        shutil.rmtree(hedef, ignore_errors=True)
    f2p = sorted(t for t, s in altin.items() if s == "PASSED" and temel.get(t) != "PASSED")
    p2p = sorted(t for t, s in altin.items() if s == "PASSED" and temel.get(t) == "PASSED")
    if not f2p:
        return None
    return f2p, p2p


# Sırayla denenir; ilk F2P'si boş olmayan profil kullanılır. Profil etikete yazılır.
TUR_PROFILLERI = ("varsayilan", "starlette0")


def f2p_p2p_turet(gorev, python=None, zaman=600, etiket="elle"):
    """Yarışma görevleri F2P/P2P listesi içermez; pipeline tanımına göre türetilir:
    F2P = test yaması uygulanmış temel ağaçta BAŞARISIZ olup altın yamayla GEÇEN testler;
    P2P = her iki durumda da GEÇEN testler (kökün tamamı). Sonuç önbelleğe yazılır."""
    yol = os.path.join(CACHE, f"turet_{gorev['instance_id']}.json")
    if os.path.exists(yol):
        with open(yol, encoding="utf-8") as f:
            return json.load(f)
    if not test_dosyalari(gorev["test_patch"]):
        raise EnvHatasi(f"{gorev['instance_id']}: test yaması Python test dosyası içermiyor")
    kokler = sorted({yol_.split("/")[0] for yol_ in test_dosyalari(gorev["test_patch"])})
    if len(kokler) != 1:
        raise EnvHatasi(f"{gorev['instance_id']}: test yaması birden çok test kökü dokunuyor: {kokler}")
    if python is not None:
        sonuc = _turet_tek(gorev, python, zaman, etiket)
        if sonuc is None:
            raise EnvHatasi(f"{gorev['instance_id']}: F2P boş (test yaması bir şey ayırt etmiyor)")
        f2p, p2p = sonuc
        ortam_etiketi = etiket
    else:
        from yarisma_ortam import ortam_kur  # geç içe aktarma: yarisma_ortam bu modülü kullanır

        for profil in TUR_PROFILLERI:
            py, et = ortam_kur(gorev, zaman, profil)
            sonuc = _turet_tek(gorev, py, zaman, et)
            if sonuc is not None:
                f2p, p2p = sonuc
                ortam_etiketi = f"{et}+{profil}"
                break
        else:
            raise EnvHatasi(f"{gorev['instance_id']}: F2P boş (tüm profiller: {', '.join(TUR_PROFILLERI)})")
    sonuc = {"FAIL_TO_PASS": json.dumps(f2p), "PASS_TO_PASS": json.dumps(p2p), "ortam": ortam_etiketi}
    os.makedirs(CACHE, exist_ok=True)
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False)
    return sonuc


def dogrula(gorev, yama, python=None, zaman=600, kapi=True):
    """Bir görev ve model yaması için ölçüm. gorev: SWE-bench satırı (dict).

    Önce altın kapı: altın yamada bozuk P2P testleri ölçümden çıkarılır (dislanan listesinde döner).
    Model yaması uygulanamazsa mesafe = 1. python None ise görev için karma ortam seçilir.
    """
    etiket = "elle"
    if python is None:
        from yarisma_ortam import ortam_kur

        # Görev türetilirken seçilen profil kullanılır (ör. 'pypi+starlette0'); aksi hâlde ortam farklı olur.
        profil = gorev["ortam"].split("+", 1)[1] if "+" in gorev.get("ortam", "") else "varsayilan"
        python, etiket = ortam_kur(gorev, zaman, profil)
    if "FAIL_TO_PASS" not in gorev:
        # Yarışma formatı: listeler yok; altın yamayla türetilir (türetme kapıyı zaten içerir).
        gorev = dict(gorev, **f2p_p2p_turet(gorev, python, zaman, etiket))
        dislanan = []
    elif kapi:
        dislanan = altin_kapi(gorev, python, zaman)
    else:
        dislanan = []  # türetme sırasında altın kapı zaten koştu (verified.jsonl)
    f2p = json.loads(gorev["FAIL_TO_PASS"])
    p2p = [t for t in json.loads(gorev["PASS_TO_PASS"]) if t not in set(dislanan)]
    sonuc = _kosum(gorev, yama, python, zaman, "model")
    if sonuc is None:
        return {"uygulandi": False, "f2p": None, "p2p": None, "cozuldu": False, "mesafe": 1.0,
                "dislanan": dislanan}
    f2p_oran = sum(sonuc.get(t) == "PASSED" for t in f2p) / max(1, len(f2p))
    p2p_oran = sum(sonuc.get(t) == "PASSED" for t in p2p) / max(1, len(p2p))
    return {
        "uygulandi": True,
        "f2p": f2p_oran,
        "p2p": p2p_oran,
        "cozuldu": f2p_oran == 1.0 and p2p_oran == 1.0,
        "mesafe": 1.0 - f2p_oran * p2p_oran,
        "dislanan": dislanan,
    }


def gorev_bul(ornek_id, veri_dosyasi):
    with open(veri_dosyasi, encoding="utf-8") as f:
        veri = json.load(f)
    for g in veri:
        if g["instance_id"] == ornek_id:
            return g
    raise KeyError(f"{ornek_id} bulunamadı")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ornek_id")
    ap.add_argument("--yama", default="gold")
    ap.add_argument("--veri", default=VERI_DOSYASI)
    ap.add_argument("--python", default=None, help="boşsa karma ortam (yarisma_ortam) seçilir")
    ap.add_argument("--zaman", type=int, default=600)
    a = ap.parse_args()
    if not a.veri:
        raise SystemExit("--veri (SWE-bench satırları JSON) verilmeli")
    g = gorev_bul(a.ornek_id, a.veri)
    yama = g["patch"] if a.yama == "gold" else open(a.yama, encoding="utf-8").read()
    print(json.dumps(dogrula(g, yama, a.python, a.zaman), ensure_ascii=False))


if __name__ == "__main__":
    main()
