"""
"GÖRÜNEN" GPU ile "GERÇEKTEN KULLANILABİLEN" GPU AYNI ŞEY DEĞİLDİR.

Kullanıcının gerçek Kaggle deneyiminde doğrulandığı gibi: `torch.cuda.
is_available()` True ve `torch.cuda.device_count()` doğru sayıyı
döndürse bile, bu cihazlardan biri veya birkaçı arka planda GERÇEKTE
kullanılamayabilir (ör. sürücü/uyumluluk sorunu, başka bir sürecin
tuttuğu/izole edilmiş bir MIG dilimi, bozuk bir PCIe bağlantısı, ya da
görünür ama fiilen erişilemeyen bir "hayalet" cihaz indeksi). Hazır
`torch.cuda.*` sorgularına güvenmek YETMEZ -- her cihaza GERÇEKTEN küçük
bir hesaplama (matris çarpımı) YAPTIRIP sonucu doğrulamak gerekir.

Neden AYRI BİR ALT SÜREÇTE (subprocess) sınanıyor: bozuk bir GPU sürücüsü
matmul çağrısını sonsuza kadar ASKIDA bırakabilir (donabilir) -- bu, ana
süreçte olsaydı TÜM programı kilitlerdi. Alt süreç + zaman aşımı, donan
bir sınamayı `terminate()` ile öldürüp diğer GPU'ların sınamasına devam
etmeyi sağlar (bkz. rwkv_native._rwkv_cuda_kernelini_dene_etkinlestir'deki
aynı desen -- RWKV_CUDA_ON derlemesini de aynı sebeple izole subprocess'te
sınıyoruz).
"""
import multiprocessing
from typing import List, Optional

_ONEK = "[gpu_tespit]"


def _gpu_calisir_mi_alt_surec(indeks: int, kuyruk: "multiprocessing.Queue") -> None:
    """AYRI bir Python sürecinde çalışır: cuda:{indeks}'te GERÇEK bir
    matris çarpımı yapıp sonucun sonlu (NaN/Inf değil) olduğunu doğrular.
    Ana sürecin belleğini/CUDA bağlamını hiç paylaşmaz -- bu yüzden bu
    süreç donsa/çökse bile ana süreç ve DİĞER GPU sınamaları etkilenmez."""
    try:
        import torch
        cihaz = f"cuda:{indeks}"
        a = torch.randn(1024, 1024, device=cihaz)
        b = torch.randn(1024, 1024, device=cihaz)
        c = a @ b
        torch.cuda.synchronize(indeks)
        tamam = bool(torch.isfinite(c).all().item())
        bos_bayt, toplam_bayt = torch.cuda.mem_get_info(indeks)
        kuyruk.put((indeks, tamam, bos_bayt, toplam_bayt, None))
    except Exception as hata:  # noqa: BLE001 -- her türlü sürücü/CUDA hatasını yakalayıp raporla
        kuyruk.put((indeks, False, 0, 0, repr(hata)))


def kullanilabilir_gpu_indeksleri(azami_gpu: Optional[int] = None, zaman_asimi_sn: float = 45.0) -> List[int]:
    """`torch.cuda.device_count()`'in GÖRDÜĞÜ her cihaz indeksini, İZOLE
    bir alt süreçte GERÇEK bir matmul ile tek tek sınar; yalnızca bu
    sınamadan GERÇEKTEN başarıyla geçen indeksleri döndürür. "Görünüyor
    ama kullanılamıyor" durumundaki cihazlar (donma/hata/erişilemezlik)
    sessizce ATLANIR ve NEDEN atlandığı loglanır -- coklu_gpu.py bu
    listeden az sayıda (hatta 1) GPU dönse bile çalışmaya devam edebilir."""
    import torch

    if not torch.cuda.is_available():
        print(f"{_ONEK} torch.cuda.is_available()=False -- hiç GPU yok, kullanılabilir liste boş.")
        return []

    goruleb_sayisi = torch.cuda.device_count()
    if azami_gpu is not None:
        goruleb_sayisi = min(goruleb_sayisi, azami_gpu)
    print(f"{_ONEK} torch {torch.cuda.device_count()} GPU GÖRÜYOR (ilk {goruleb_sayisi} tanesi sınanacak) -- her biri İZOLE bir alt süreçte GERÇEK matmul ile doğrulanıyor...")

    baglam = multiprocessing.get_context("spawn")
    gercekten_calisan: List[int] = []
    for i in range(goruleb_sayisi):
        kuyruk = baglam.Queue()
        surec = baglam.Process(target=_gpu_calisir_mi_alt_surec, args=(i, kuyruk), daemon=True)
        surec.start()
        surec.join(timeout=zaman_asimi_sn)

        if surec.is_alive():
            surec.terminate()
            surec.join()
            print(f"{_ONEK} cuda:{i} SINAMASI {zaman_asimi_sn:.0f} SN İÇİNDE BİTMEDİ (donmuş/erişilemez sürücü belirtisi) -- GERÇEKTE KULLANILAMIYOR kabul edilip ATLANDI.")
            continue

        try:
            _idx, tamam, bos_bayt, toplam_bayt, hata = kuyruk.get_nowait()
        except Exception:
            print(f"{_ONEK} cuda:{i} sınama süreci sonuç DÖNDÜRMEDEN sonlandı (çökme belirtisi) -- ATLANDI.")
            continue

        if not tamam:
            print(f"{_ONEK} cuda:{i} GÖRÜNÜYOR ama GERÇEK matmul sınaması BAŞARISIZ oldu ({hata}) -- ATLANDI.")
            continue

        print(f"{_ONEK} cuda:{i} GERÇEKTEN kullanılabilir olarak doğrulandı ({bos_bayt / 1024**3:.1f}/{toplam_bayt / 1024**3:.1f} GB boş VRAM).")
        gercekten_calisan.append(i)

    print(
        f"{_ONEK} SONUÇ: torch {goruleb_sayisi} GPU görüyordu, bunlardan YALNIZCA "
        f"{len(gercekten_calisan)} tanesi GERÇEKTEN çalışır bulundu: {gercekten_calisan} "
        f"({'hiçbiri GÖRÜNENLE eşleşmiyor -- görünen sayıya körü körüne güvenmek yanlış olurdu!' if len(gercekten_calisan) != goruleb_sayisi else 'görünenle birebir eşleşiyor'})"
    )
    return gercekten_calisan
