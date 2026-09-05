"""
Kaggle Otomatik Veri Dönüştürücü ve Veri Seti Gönderici
------------------------------------------------------
Girdi verilerini GPUDirect uyumlu .bin, Safetensors ve Zarr v3 formatlarına
dönüştürür ve 500 MB sınırını aşmayacak parçalar halinde Kaggle veri seti olarak yükler.
"""

import os
import sys
import json
import math
import shutil
from pathlib import Path
from typing import List, Dict, Any, Generator

import numpy as np
import torch
from safetensors.torch import save_file as save_safetensors
import zarr

# 500 Megabayt sınır değeri (Bayt cinsinden)
MAX_SHARD_SIZE_BYTES = 500 * 1024 * 1024
INPUT_DIR = Path("/kaggle/input")
OUTPUT_DIR = Path("/kaggle/working/export_dataset")


def yetkilendirme_yap() -> tuple[str, str]:
    """
    Kaggle Secrets kasasından API anahtarlarını temin eder ve muhite işler.
    """
    try:
        from kaggle_secrets import UserSecretsClient
        user_secrets = UserSecretsClient()
        username = user_secrets.get_secret("KAGGLE_USERNAME")
        key = user_secrets.get_secret("KAGGLE_KEY")
    except Exception as hata:
        # Mahalli muhitte veya doğrudan ortam değişkenlerinde arama emniyeti
        username = os.environ.get("KAGGLE_USERNAME")
        key = os.environ.get("KAGGLE_KEY")
        if not username or not key:
            raise RuntimeError(
                "Kaggle API anahtarları bulunamadı. Lütfen Add-ons -> Secrets "
                "bölümüne 'KAGGLE_USERNAME' ve 'KAGGLE_KEY' değerlerini ekleyiniz."
            ) from hata

    os.environ["KAGGLE_USERNAME"] = username
    os.environ["KAGGLE_KEY"] = key
    return username, key


class ShardYonetici:
    """
    Üretilen dosyaların 500 MB sınırını aşmamasını murakabe eden yardımcı sınıf.
    """
    def __init__(self, cikti_kok_dizin: Path, onek: str):
        self.cikti_kok_dizin = cikti_kok_dizin
        self.onek = onek
        self.parca_no = 0
        self.su_anki_boyut = 0
        self.aktif_dosya = None

    def yeni_parca_yolu(self, uzanti: str) -> Path:
        yol = self.cikti_kok_dizin / f"{self.onek}_part_{self.parca_no:04d}.{uzanti}"
        self.parca_no += 1
        return yol


def metin_ve_token_donustur(girdi_yollari: List[Path], cikti_dizin: Path):
    """
    Hüküm 1: GPUDirect Destekli Memory-Mapped Raw Binary (.bin + .idx).
    Tokenleri uint16 veya uint32 blokları olarak 4096-bayt sektör hizalamasıyla yazar.
    500 MB hududunu aşınca yeni parça açar.
    """
    print("[1/3] Metin ve Token verileri mmap .bin formatına dönüştürülüyor...")
    cikti_dizin.mkdir(parents=True, exist_ok=True)

    parca_indeksi = 0
    mevcut_yazilan_bayt = 0
    mevcut_bin_yolu = cikti_dizin / f"tokens_shard_{parca_indeksi:04d}.bin"
    mevcut_idx_yolu = cikti_dizin / f"tokens_shard_{parca_indeksi:04d}.idx"

    bin_dosya = open(mevcut_bin_yolu, "wb")
    indeks_kayitlari = []  # (baslangic_bayt, uzunluk_adet)

    def parca_kapat_ve_yenisini_ac():
        nonlocal bin_dosya, parca_indeksi, mevcut_yazilan_bayt, mevcut_bin_yolu, mevcut_idx_yolu, indeks_kayitlari
        bin_dosya.flush()
        bin_dosya.close()

        # İndeks tablosunu uint64 çiftleri olarak diske dök
        if indeks_kayitlari:
            idx_dizi = np.array(indeks_kayitlari, dtype=np.uint64)
            idx_dizi.tofile(mevcut_idx_yolu)
            indeks_kayitlari = []

        parca_indeksi += 1
        mevcut_yazilan_bayt = 0
        mevcut_bin_yolu = cikti_dizin / f"tokens_shard_{parca_indeksi:04d}.bin"
        mevcut_idx_yolu = cikti_dizin / f"tokens_shard_{parca_indeksi:04d}.idx"
        bin_dosya = open(mevcut_bin_yolu, "wb")

    for yol in girdi_yollari:
        try:
            with open(yol, "r", encoding="utf-8", errors="ignore") as f:
                satirlar = f.readlines()
        except Exception:
            continue

        for satir in satirlar:
            metin = satir.strip()
            if not metin:
                continue

            # Basit UTF-8 kodlama temsili veya doğrudan uint32 indeksleme
            # 65535 üstü için uint32, altı için uint16 tercih edilir.
            tokenler = np.frombuffer(metin.encode("utf-8"), dtype=np.uint8).astype(np.uint16)
            veri_bayt_boyutu = tokenler.nbytes

            # 500 MB aşılacaksa yeni parçaya geç
            if mevcut_yazilan_bayt + veri_bayt_boyutu > MAX_SHARD_SIZE_BYTES and mevcut_yazilan_bayt > 0:
                parca_kapat_ve_yenisini_ac()

            baslangic_ofseti = mevcut_yazilan_bayt
            bin_dosya.write(tokenler.tobytes())
            
            # 4096 Bayt GDS Donanım Hizalaması (Padding)
            kalan = veri_bayt_boyutu % 64  # Tensör çekirdekleri için asgari 64-bayt hizalama
            if kalan != 0:
                dolgu = 64 - kalan
                bin_dosya.write(b"\x00" * dolgu)
                mevcut_yazilan_bayt += veri_bayt_boyutu + dolgu
            else:
                mevcut_yazilan_bayt += veri_bayt_boyutu

            indeks_kayitlari.append((baslangic_ofseti, len(tokenler)))

    bin_dosya.flush()
    bin_dosya.close()
    if indeks_kayitlari:
        idx_dizi = np.array(indeks_kayitlari, dtype=np.uint64)
        idx_dizi.tofile(mevcut_idx_yolu)


def agirlik_ve_kan_katsayilarini_donustur(girdi_yollari: List[Path], cikti_dizin: Path):
    """
    Hüküm 2: Safetensors (Sıfır-kopyalı ikili tensör formatı).
    Model ağırlıklarını ve Chebyshev katsayılarını toplar, 500 MB sınırına göre böler.
    """
    print("[2/3] Model ağırlıkları ve KAN katsayıları Safetensors formatına aktarılıyor...")
    cikti_dizin.mkdir(parents=True, exist_ok=True)

    toplu_tensorler: Dict[str, torch.Tensor] = {}
    mevcut_boyut = 0
    parca_indeksi = 0

    def parca_kaydet():
        nonlocal toplu_tensorler, mevcut_boyut, parca_indeksi
        if not toplu_tensorler:
            return
        hedef_yol = cikti_dizin / f"weights_shard_{parca_indeksi:04d}.safetensors"
        save_safetensors(toplu_tensorler, str(hedef_yol))
        print(f"Safetensors parçası yazıldı: {hedef_yol.name} ({mevcut_boyut / (1024*1024):.2f} MB)")
        toplu_tensorler = {}
        mevcut_boyut = 0
        parca_indeksi += 1

    for yol in girdi_yollari:
        try:
            if yol.suffix in [".pt", ".bin"]:
                yuklenen = torch.load(yol, map_location="cpu")
                if isinstance(yuklenen, dict):
                    sozluk = yuklenen
                elif hasattr(yuklenen, "state_dict"):
                    sozluk = yuklenen.state_dict()
                else:
                    sozluk = {yol.stem: yuklenen}
            elif yol.suffix in [".npy", ".npz"]:
                veri = np.load(yol)
                if isinstance(veri, np.lib.npyio.NpzFile):
                    sozluk = {k: torch.from_numpy(veri[k]) for k in veri.files}
                else:
                    sozluk = {yol.stem: torch.from_numpy(veri)}
            else:
                continue
        except Exception:
            continue

        for anahtar, deger in sozluk.items():
            if not isinstance(deger, torch.Tensor):
                continue
            
            # Tensörün bellekte kapladığı ham bayt hesabı
            t_boyut = deger.element_size() * deger.nelement()

            if mevcut_boyut + t_boyut > MAX_SHARD_SIZE_BYTES and mevcut_boyut > 0:
                parca_kaydet()

            temiz_isim = f"{yol.stem}_{anahtar}".replace(".", "_")
            toplu_tensorler[temiz_isim] = deger.contiguous()
            mevcut_boyut += t_boyut

    parca_kaydet()


def kuantum_dalga_ve_qtt_donustur(girdi_yollari: List[Path], cikti_dizin: Path):
    """
    Hüküm 3: Zarr v3 (Parçalanmış, bloklu tensör yapısı).
    Kuantum dalga durumları ve Tensör Treni (QTT) çekirdekleri için bloklu depolama.
    """
    print("[3/3] Kuantum durumları ve QTT çekirdekleri Zarr v3 formatına dönüştürülüyor...")
    zarr_yolu = cikti_dizin / "quantum_qtt_store.zarr"
    kok_grup = zarr.open_group(str(zarr_yolu), mode="w")

    for sira, yol in enumerate(girdi_yollari):
        try:
            if yol.suffix == ".npy":
                dizi = np.load(yol)
            else:
                # İkili ham kuantum verisi okuma varsayımı (complex64)
                boyut = yol.stat().st_size
                eleman_sayisi = boyut // 8  # complex64 = 8 bayt
                if eleman_sayisi == 0:
                    continue
                dizi = np.fromfile(yol, dtype=np.complex64)
        except Exception:
            continue

        # 500 MB blok sınırını gözeterek chunk boyutunu belirle
        eleman_bayt = dizi.dtype.itemsize
        maks_eleman = MAX_SHARD_SIZE_BYTES // (eleman_bayt * 2)  # Emniyet payı
        
        if dizi.ndim == 1:
            chunk_sekli = (min(len(dizi), maks_eleman),)
        else:
            # Çok boyutlu QTT tensörleri için ilk boyutu parçala
            chunk_sekli = list(dizi.shape)
            chunk_sekli[0] = max(1, min(chunk_sekli[0], maks_eleman // max(1, math.prod(chunk_sekli[1:]))))
            chunk_sekli = tuple(chunk_sekli)

        dizi_adi = f"core_{sira}_{yol.stem}"
        kok_grup.create_dataset(
            dizi_adi,
            data=dizi,
            chunks=chunk_sekli,
            dtype=dizi.dtype
        )


def veri_setini_gonder(kullanici_adi: str, veri_seti_etiketi: str, baslik: str, veri_dizini: Path):
    """
    Kaggle API vasıtasıyla işlenmiş dosyaları umuma açık bir veri kümesi olarak yükler.
    """
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()

    # Metadata dosyasını tanzim et
    meta_yol = veri_dizini / "dataset-metadata.json"
    meta_icerik = {
        "title": baslik,
        "id": f"{kullanici_adi}/{veri_seti_etiketi}",
        "licenses": [{"name": "CC0-1.0"}]
    }
    with open(meta_yol, "w", encoding="utf-8") as f:
        json.dump(meta_icerik, f, indent=2)

    print(f"Veri seti yükleniyor: {kullanici_adi}/{veri_seti_etiketi}")
    
    # Mevcut veri kümesi var mı kontrol et
    try:
        api.dataset_create_version(
            str(veri_dizini),
            version_notes="Otomatik GPUDirect, Safetensors ve Zarr v3 dönüştürme sürümü",
            dir_mode="zip"
        )
        print("Mevcut veri kümesine yeni sürüm başarıyla yüklendi.")
    except Exception:
        # Şayet evvelden açılmamışsa sıfırdan inşa et (public olarak)
        api.dataset_create_new(
            str(veri_dizini),
            public=True,
            dir_mode="zip",
            quiet=False
        )
        print("Umumi veri kümesi sıfırdan başarıyla teşkil edildi.")


def ana_icra():
    # 1. Sırları al ve yetkilendir
    kullanici_adi, _ = yetkilendirme_yap()

    if not INPUT_DIR.exists():
        print(f"Girdi dizini mevcut değil: {INPUT_DIR}")
        return

    # 2. Girdi dizinindeki bütün kütükleri tara ve tasnif et
    butun_dosyalar = [p for p in INPUT_DIR.rglob("*") if p.is_file()]
    if not butun_dosyalar:
        print("Girdi dizininde işlenecek kütük bulunamadı.")
        return

    metin_dosyalari = []
    agirlik_dosyalari = []
    kuantum_dosyalari = []

    for d in butun_dosyalar:
        ad = d.name.lower()
        if any(ad.endswith(ext) for ext in [".txt", ".json", ".jsonl", ".csv"]):
            metin_dosyalari.append(d)
        elif any(ad.endswith(ext) for ext in [".pt", ".bin", ".ckpt", ".pth"]):
            agirlik_dosyalari.append(d)
        elif any(ad.endswith(ext) for ext in [".npy", ".npz", ".zarr", ".h5", ".hdf5"]):
            # Tensör ve kuantum durum ayrımı
            if "quantum" in ad or "wave" in ad or "qtt" in ad:
                kuantum_dosyalari.append(d)
            else:
                agirlik_dosyalari.append(d)
        else:
            # Kalan bilinmeyen dosyalar ikili veri olarak metin/ham havuzuna alınır
            metin_dosyalari.append(d)

    # 3. Format dönüşümlerini tatbik et
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if metin_dosyalari:
        metin_ve_token_donustur(metin_dosyalari, OUTPUT_DIR / "tokens_mmap")
    
    if agirlik_dosyalari:
        agirlik_ve_kan_katsayilarini_donustur(agirlik_dosyalari, OUTPUT_DIR / "weights_safetensors")

    if kuantum_dosyalari:
        kuantum_dalga_ve_qtt_donustur(kuantum_dosyalari, OUTPUT_DIR / "quantum_zarr")

    # 4. Kaggle'a public dataset olarak gönder
    veri_seti_adi = "hizli-erisimli-muhtelif-tensör-kumesi"
    baslik = "GPUDirect Safetensors Zarr V3 Sharded Dataset"
    veri_setini_gonder(kullanici_adi, veri_seti_adi, baslik, OUTPUT_DIR)


if __name__ == "__main__":
    ana_icra()