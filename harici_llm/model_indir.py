"""
INTERNETLI ilk calistirma icin indirme betigi.

Kullanim akisi (kullanicinin belirttigi iki asamali yontem):
  1) BU dosya, internet ACIK bir Kaggle notebook'unda calistirilir. Model
     ONCE /tmp altina (GECICI_INDIRME_KOKU) indirilir; /kaggle/working'in
     20GB cikti sinirini asip asmadigi olculur. Asmiyorsa /tmp'deki
     her sey oldugu gibi /kaggle/working/modeller'e KOPYALANIR. Asiyorsa,
     /tmp'de biriken TUM model dosyalari TEK bir zip dosyasinda toplanip
     yalnizca o zip /kaggle/working'e yazilir.
  2) O cikti (klasor ya da zip), ikinci (internet KAPALI) calistirmada
     girdi olarak eklenir. model_yapilandirmalari.py, ortam degiskenleri
     (MUCIT_RWKV_YOLU) veya asagidaki VARSAYILAN_INDIRME_KOKU altindaki
     yerel yolu otomatik bulur.

  NOT: `rwkv` pip paketi ARTIK BU BETIK TARAFINDAN INDIRILMIYOR --
  Kaggle notebook'unun kendi "Install dependencies" bolumune eklendi,
  notebook baslamadan once (internet acik/kapali farketmeksizin)
  kuruluyor. Asagida hangi paketlerin o bolume eklenmesi gerektigi
  listelenir.

Onemli duzeltmeler / kararlar:
  - Mamba-Codestral YEDEK MODEL OLARAK KALDIRILDI (kullanici talebiyle).
    Yalnizca RWKV-7 indirilir; ttt_lora.py'deki ana/yedek dusme mantigi
    artik tek adaya sahip.
  - RWKV-7 icin ANA secim 7.2B'dir (7.2B FP16 ~14.4GB agirlik, 22.5GB VRAM
    butcesinde LoRA+TTT+MCTS dallanmasi icin hala yer birakiyor; 1.5B'ye
    gore akil yurutme kapasitesi farki, quantization kaybindan cok daha
    buyuktur).
  - BlinkDL/rwkv7-g1 deposu HEM ham .pth kontrol noktalarini (orijinal
    `rwkv` pip paketiyle kullanilir) HEM DE (varsa) transformers-uyumlu
    config/tokenizer dosyalarini barindirabilir. Bu betik once deponun
    GERCEK dosya listesini `list_repo_files` ile okur (kor tahmin
    yapmaz), sonra istenmeyen diger boy .pth dosyalarini HARIC tutarak
    geri kalan her seyi + secilen .pth'i indirir.
  - NOT: .pth/.safetensors dosyalari zaten yogun ikili (float16) veri
    oldugundan zip sikistirmasi bunlarda buyuk bir boyut kazanci
    SAGLAMAYABILIR; yine de istenen usul (20GB'i asinca tek zip'e alma)
    harfiyen uygulanir.
"""
import os
import shutil
from typing import List, Optional

GECICI_INDIRME_KOKU = "/tmp/mucit_gecici_indirmeler"
VARSAYILAN_INDIRME_KOKU = "/kaggle/working/modeller"
ZIP_CIKTI_YOLU = "/kaggle/working/mucit_harici_llm_paketi.zip"

CIKTI_ESIK_BAYT = 20 * 1024 ** 3  # 20 GB — /kaggle/working çıktı sınırı

RWKV_REPO_ID = "BlinkDL/rwkv7-g1"
RWKV_DOSYA_ADLARI = {
    "0.1b": "rwkv7b-g1b-0.1b-20250822-ctx4096.pth",
    "1.5b": "rwkv7-g1i-1.5b-20260805-ctx16384.pth",
    "7.2b": "rwkv7-g1i-7.2b-20260805-ctx16384.pth",
}
RWKV_ANA_BOYUT = "7.2b"  # öneri: bkz. bu dosyanın başındaki gerekçe


def _tum_pth_disindaki_dosyalari_ve_secileni_indir(
    repo_id: str, secilen_pth: str, hedef_dizin: str
) -> List[str]:
    from huggingface_hub import hf_hub_download, list_repo_files

    tum_dosyalar = list_repo_files(repo_id)
    print(f"[model_indir] '{repo_id}' deposundaki gerçek dosya listesi ({len(tum_dosyalar)} dosya):")
    for d in tum_dosyalar:
        print(f"    - {d}")

    indirilecekler = [
        d for d in tum_dosyalar
        if not d.endswith(".pth") or d == secilen_pth or os.path.basename(d) == secilen_pth
    ]
    if not any(d.endswith(".pth") for d in indirilecekler):
        raise FileNotFoundError(
            f"'{repo_id}' deposunda '{secilen_pth}' adlı dosya bulunamadı. "
            f"Depodaki gerçek .pth dosyaları: {[d for d in tum_dosyalar if d.endswith('.pth')]}"
        )

    os.makedirs(hedef_dizin, exist_ok=True)
    indirilenler = []
    for dosya in indirilecekler:
        print(f"[model_indir] indiriliyor: {repo_id}/{dosya}")
        yerel_yol = hf_hub_download(repo_id=repo_id, filename=dosya, local_dir=hedef_dizin)
        indirilenler.append(yerel_yol)
    return indirilenler


def rwkv_indir(boyut: str = RWKV_ANA_BOYUT, hedef_kok: str = GECICI_INDIRME_KOKU) -> str:
    if boyut not in RWKV_DOSYA_ADLARI:
        raise ValueError(f"Bilinmeyen RWKV boyutu: {boyut!r}. Seçenekler: {sorted(RWKV_DOSYA_ADLARI)}")

    secilen_pth = RWKV_DOSYA_ADLARI[boyut]
    # NOT: burada AYRICA "modeller" alt-klasoru EKLENMEZ -- nihai_kok zaten
    # ".../modeller" adiyla /kaggle/working'e kopyalaniyor
    # (_geciciyi_nihaiye_tasi); iki kez "modeller" eklemek eskiden
    # /kaggle/working/modeller/modeller/rwkv/... gibi cift ic ice
    # gecmis, kirilgan bir yapi uretiyordu.
    hedef_dizin = os.path.join(hedef_kok, "rwkv")

    print(f"[model_indir] === RWKV-7 G1 ({boyut}, dosya: {secilen_pth}) /tmp'ye indiriliyor -> {hedef_dizin} ===")
    _tum_pth_disindaki_dosyalari_ve_secileni_indir(RWKV_REPO_ID, secilen_pth, hedef_dizin)
    print(f"[model_indir] RWKV-7 G1 /tmp'ye indirme tamamlandı: {hedef_dizin}")
    return hedef_dizin


# `rwkv` (ve tum bagimliliklari) artik Kaggle notebook'unun "Install
# dependencies" bolumune eklendi -- notebook baslamadan ONCE, internet
# acik/kapali farketmeksizin kuruluyor. Bu betik artik pip paketi
# indirmiyor; yalnizca model agirligini indirir.


def _dizin_boyutu_bayt(dizin: str) -> int:
    toplam = 0
    for kok, _dizinler, dosyalar in os.walk(dizin):
        for ad in dosyalar:
            yol = os.path.join(kok, ad)
            if os.path.isfile(yol):
                toplam += os.path.getsize(yol)
    return toplam


def _geciciyi_nihaiye_tasi(gecici_kok: str, nihai_kok: str, zip_yolu: str) -> str:
    """/tmp'de biriken her sey icin: 20GB'i asiyorsa TEK bir zip'e
    toplayip zip'i /kaggle/working'e yazar; asmiyorsa /tmp'deki agac
    oldugu gibi /kaggle/working'e kopyalanir."""
    toplam_bayt = _dizin_boyutu_bayt(gecici_kok)
    toplam_gb = toplam_bayt / 1024 ** 3
    print(f"[model_indir] /tmp'de biriken toplam boyut: {toplam_gb:.2f} GB (eşik: {CIKTI_ESIK_BAYT / 1024**3:.0f} GB)")

    if toplam_bayt > CIKTI_ESIK_BAYT:
        print(f"[model_indir] Eşik aşıldı -> ZIP sıkıştırma etkinleştirildi: {zip_yolu}")
        os.makedirs(os.path.dirname(zip_yolu), exist_ok=True)
        taban_yol = zip_yolu[:-4] if zip_yolu.endswith(".zip") else zip_yolu
        uretilen_zip = shutil.make_archive(taban_yol, "zip", root_dir=gecici_kok)
        zip_boyutu_gb = os.path.getsize(uretilen_zip) / 1024 ** 3
        print(f"[model_indir] ZIP tamamlandı: {uretilen_zip} ({zip_boyutu_gb:.2f} GB)")
        return uretilen_zip

    print(f"[model_indir] Eşik aşılmadı -> doğrudan kopyalanıyor: {nihai_kok}")
    shutil.copytree(gecici_kok, nihai_kok, dirs_exist_ok=True)
    print(f"[model_indir] Kopyalama tamamlandı: {nihai_kok}")
    return nihai_kok


def hepsini_indir(
    rwkv_boyutu: str = RWKV_ANA_BOYUT,
    gecici_kok: str = GECICI_INDIRME_KOKU,
    nihai_kok: str = VARSAYILAN_INDIRME_KOKU,
    zip_yolu: str = ZIP_CIKTI_YOLU,
) -> str:
    print("[model_indir] ================= RWKV-7 G1 (/tmp'ye) =================")
    rwkv_indir(boyut=rwkv_boyutu, hedef_kok=gecici_kok)

    print("\n[model_indir] ================= /tmp -> /kaggle/working AKTARIMI =================")
    sonuc_yolu = _geciciyi_nihaiye_tasi(gecici_kok, nihai_kok, zip_yolu)

    print("\n[model_indir] ================= TAMAMLANDI =================")
    print(f"[model_indir] Nihai çıktı: {sonuc_yolu}")
    print(
        "[model_indir] Bu çıktı notebook bitince otomatik olarak veri kümesi haline gelir. "
        "İkinci (internet KAPALI) çalıştırmada bunu girdi olarak ekleyip "
        "(zip ise önce unzip edin), MUCIT_RWKV_YOLU ortam değişkeniyle gerçek yolu geçin."
    )
    return sonuc_yolu


if __name__ == "__main__":
    import argparse

    ayristirici = argparse.ArgumentParser(description="RWKV-7 G1 modelini /tmp üzerinden indirir")
    ayristirici.add_argument("--rwkv_boyutu", type=str, default=RWKV_ANA_BOYUT, choices=sorted(RWKV_DOSYA_ADLARI))
    ayristirici.add_argument("--gecici_kok", type=str, default=GECICI_INDIRME_KOKU)
    ayristirici.add_argument("--nihai_kok", type=str, default=VARSAYILAN_INDIRME_KOKU)
    ayristirici.add_argument("--zip_yolu", type=str, default=ZIP_CIKTI_YOLU)
    args = ayristirici.parse_args()

    hepsini_indir(
        rwkv_boyutu=args.rwkv_boyutu, gecici_kok=args.gecici_kok,
        nihai_kok=args.nihai_kok, zip_yolu=args.zip_yolu,
    )
