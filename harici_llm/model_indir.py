"""
INTERNETLI ilk calistirma icin indirme betigi.

Kullanim akisi (kullanicinin belirttigi iki asamali yontem):
  1) BU dosya, internet ACIK bir Kaggle notebook'unda calistirilir.
     Modeller /kaggle/working/modeller altina indirilir; notebook
     bitince bu klasor otomatik olarak notebook'un CIKTI veri kumesi
     (output dataset) olur.
  2) O cikti, ikinci (internet KAPALI) calistirmada girdi olarak eklenir.
     model_yapilandirmalari.py, ortam degiskenleri (MUCIT_RWKV_YOLU /
     MUCIT_MAMBA_YOLU) veya asagidaki VARSAYILAN_INDIRME_KOKU altindaki
     yerel yolu otomatik bulur -- ayni harici_llm/gonderim_uret.py hicbir
     degisiklik yapilmadan calisir.

Onemli duzeltmeler:
  - mlx-community/Mamba-Codestral-7B-v0.1 Apple MLX formatindadir, CUDA/
    PyTorch ile CALISMAZ. Bunun yerine orijinal, PyTorch/safetensors
    formatindaki mistralai/Mamba-Codestral-7B-v0.1 indirilir.
  - RWKV-7 icin ANA secim 7.2B'dir (7.2B FP16 ~14.4GB agirlik, 22.5GB VRAM
    butcesinde LoRA+TTT+MCTS dallanmasi icin hala yer birakiyor; 1.5B'ye
    gore akil yurutme kapasitesi farki, quantization kaybindan cok daha
    buyuktur). VRAM sikisirsa `8bit_quantize_et=True` ile calistirin.
  - BlinkDL/rwkv7-g1 deposu HEM ham .pth kontrol noktalarini (orijinal
    `rwkv` pip paketiyle kullanilir) HEM DE (varsa) transformers-uyumlu
    config/tokenizer dosyalarini barindirabilir. Bu betik once deponun
    GERCEK dosya listesini `list_repo_files` ile okur (kor tahmin
    yapmaz), sonra istenmeyen diger boy .pth dosyalarini HARIC tutarak
    geri kalan her seyi + secilen .pth'i indirir.
"""
import os
from typing import List, Optional

VARSAYILAN_INDIRME_KOKU = "/kaggle/working/modeller"

RWKV_REPO_ID = "BlinkDL/rwkv7-g1"
RWKV_DOSYA_ADLARI = {
    "0.1b": "rwkv7b-g1b-0.1b-20250822-ctx4096.pth",
    "1.5b": "rwkv7-g1i-1.5b-20260805-ctx16384.pth",
    "7.2b": "rwkv7-g1i-7.2b-20260805-ctx16384.pth",
}
RWKV_ANA_BOYUT = "7.2b"  # öneri: bkz. bu dosyanın başındaki gerekçe

MAMBA_REPO_ID = "mistralai/Mamba-Codestral-7B-v0.1"  # mlx-community DEĞİL — o Apple MLX formatı, CUDA'da çalışmaz


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


def rwkv_indir(boyut: str = RWKV_ANA_BOYUT, hedef_kok: str = VARSAYILAN_INDIRME_KOKU) -> str:
    if boyut not in RWKV_DOSYA_ADLARI:
        raise ValueError(f"Bilinmeyen RWKV boyutu: {boyut!r}. Seçenekler: {sorted(RWKV_DOSYA_ADLARI)}")

    secilen_pth = RWKV_DOSYA_ADLARI[boyut]
    hedef_dizin = os.path.join(hedef_kok, "rwkv")

    print(f"[model_indir] === RWKV-7 G1 ({boyut}, dosya: {secilen_pth}) indiriliyor -> {hedef_dizin} ===")
    _tum_pth_disindaki_dosyalari_ve_secileni_indir(RWKV_REPO_ID, secilen_pth, hedef_dizin)
    print(f"[model_indir] RWKV-7 G1 tamamlandı: {hedef_dizin}")
    return hedef_dizin


def mamba_indir(hedef_kok: str = VARSAYILAN_INDIRME_KOKU) -> str:
    from huggingface_hub import snapshot_download

    hedef_dizin = os.path.join(hedef_kok, "mamba")
    print(f"[model_indir] === Mamba-Codestral-7B-v0.1 (mistralai, PyTorch) indiriliyor -> {hedef_dizin} ===")
    snapshot_download(
        repo_id=MAMBA_REPO_ID, local_dir=hedef_dizin,
        allow_patterns=["*.json", "*.safetensors", "*.safetensors.index.json", "*.model", "*.txt", "tokenizer*"],
    )
    print(f"[model_indir] Mamba-Codestral tamamlandı: {hedef_dizin}")
    return hedef_dizin


PAKET_HEDEF_KOK = "/kaggle/working/paketler"

# `rwkv` PyPI'de gercekten var (BlinkDL yayinliyor) -- offline calistirmada
# `pip install rwkv` internete erisemedigi icin basarisiz olur. Cozum: bu
# INTERNET-ACIK betikte wheel'i (ve tum bagimliliklarini) KURMADAN, sadece
# indirip diske kaydediyoruz; offline calistirmada `pip install --no-index`
# ile yerel klasordan kuruluyor.
PAKET_ADLARI = ["rwkv", "tokenizers", "ninja"]


def paketleri_indir(hedef_kok: str = PAKET_HEDEF_KOK, paketler: List[str] = PAKET_ADLARI) -> str:
    import subprocess
    import sys

    os.makedirs(hedef_kok, exist_ok=True)
    print(f"[model_indir] === pip paketleri indiriliyor (KURULMUYOR, sadece indiriliyor) -> {hedef_kok} ===")
    komut = [sys.executable, "-m", "pip", "download", "-d", hedef_kok] + paketler
    print(f"[model_indir] çalıştırılıyor: {' '.join(komut)}")
    subprocess.run(komut, check=True)
    print(f"[model_indir] paketler indirildi: {hedef_kok}")
    return hedef_kok


def hepsini_indir(
    rwkv_boyutu: str = RWKV_ANA_BOYUT, hedef_kok: str = VARSAYILAN_INDIRME_KOKU
) -> None:
    print("[model_indir] ================= ÖNCELİKLİ MODEL: RWKV-7 G1 =================")
    rwkv_yolu = rwkv_indir(boyut=rwkv_boyutu, hedef_kok=hedef_kok)

    print("\n[model_indir] ================= YEDEK MODEL: Mamba-Codestral-7B-v0.1 =================")
    mamba_yolu = mamba_indir(hedef_kok=hedef_kok)

    print("\n[model_indir] ================= PIP PAKETLERİ (rwkv ve bağımlılıkları) =================")
    paket_yolu = paketleri_indir()

    print("\n[model_indir] ================= TAMAMLANDI =================")
    print(f"[model_indir] RWKV yerel yolu : {rwkv_yolu}")
    print(f"[model_indir] Mamba yerel yolu: {mamba_yolu}")
    print(f"[model_indir] pip paketleri   : {paket_yolu}")
    print(
        "[model_indir] Bu klasörler (\"/kaggle/working/modeller\" ve \"/kaggle/working/paketler\") "
        "notebook bitince otomatik olarak çıktı veri kümesi haline gelir. İkinci (internet KAPALI) "
        "çalıştırmada bu çıktıyı girdi olarak ekleyip:\n"
        "  1) Kaggle'ın verdiği gerçek model yolunu MUCIT_RWKV_YOLU / MUCIT_MAMBA_YOLU ortam "
        "değişkenleriyle geçin (model_yapilandirmalari.py bunları otomatik okur).\n"
        "  2) `pip install --no-index --find-links=<paketler_yolu> rwkv` ile paketi TAMAMEN "
        "internete dokunmadan kurun (notebook_giris.py'nin başına eklenmeli)."
    )


if __name__ == "__main__":
    import argparse

    ayristirici = argparse.ArgumentParser(description="RWKV-7 G1 (öncelikli) ve Mamba-Codestral (yedek) modellerini HF'den indir")
    ayristirici.add_argument("--rwkv_boyutu", type=str, default=RWKV_ANA_BOYUT, choices=sorted(RWKV_DOSYA_ADLARI))
    ayristirici.add_argument("--hedef_kok", type=str, default=VARSAYILAN_INDIRME_KOKU)
    ayristirici.add_argument("--sadece", type=str, default=None, choices=["rwkv", "mamba", "paketler"])
    args = ayristirici.parse_args()

    if args.sadece == "rwkv":
        rwkv_indir(boyut=args.rwkv_boyutu, hedef_kok=args.hedef_kok)
    elif args.sadece == "mamba":
        mamba_indir(hedef_kok=args.hedef_kok)
    elif args.sadece == "paketler":
        paketleri_indir()
    else:
        hepsini_indir(rwkv_boyutu=args.rwkv_boyutu, hedef_kok=args.hedef_kok)
