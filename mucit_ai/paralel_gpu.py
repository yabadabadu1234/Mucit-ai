#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
BİLİŞSEL KANVAS TOPOLOJİK REKÜRENS MİMARİSİ
Çoklu GPU Paralel Eğitim ve Çıkarım Dağıtım Modülü (paralel_gpu.py)
================================================================================
Bu modül; Kaggle/Colab veya sunucu ortamlarında tahsis edilen 1, 2, 4 veya daha fazla
GPU (Tesla T4, NVIDIA L4, A100 vb.) donanımlarını otomatik tespit eder.
PyTorch nn.DataParallel ve CUDA Akış Yöneticisi altyapısı ile model eğitimini ve
çıkarım sürecini çoklu GPU'lara paralelleştirerek katbekat hızlandırır.
"""

import os
import sys
import logging
from typing import Dict, Any, List, Tuple, Optional, Union

import torch
import torch.nn as nn

try:
    from .seri_gpu_akimi import Seri_GPU_Akim_Yoneticisi, Coklu_GPU_Esnek_Aktarim_Motoru
except ImportError:
    from seri_gpu_akimi import Seri_GPU_Akim_Yoneticisi, Coklu_GPU_Esnek_Aktarim_Motoru

logger = logging.getLogger('ParalelGPU')

class GPU_Tespitci:
    """
    Sistemdeki kullanılabilir GPU donanımlarını (CUDA device count, VRAM, isimler)
    otomatik tespit eden ve PyTorch cihaz haritasını kuran sınıf.
    """
    def __init__(self):
        self.cuda_mevcut = torch.cuda.is_available()
        self.gpu_sayisi = torch.cuda.device_count() if self.cuda_mevcut else 0
        self.cihaz_idleri: List[int] = list(range(self.gpu_sayisi)) if self.gpu_sayisi > 0 else []
        self.ana_cihaz_adi = f"cuda:{self.cihaz_idleri[0]}" if self.gpu_sayisi > 0 else "cpu"
        self.device = torch.device(self.ana_cihaz_adi)
        self._raporla()

    def _raporla(self) -> None:
        if not self.cuda_mevcut or self.gpu_sayisi == 0:
            logger.info("  [GPU Tespitçisi] CUDA donanımı bulunamadı. İşlemler CPU üzerinde yürütülecek.")
            return

        logger.info(f"  [GPU Tespitçisi] Toplam {self.gpu_sayisi} Adet GPU Donanımı Tespit Edildi:")
        for i in self.cihaz_idleri:
            props = torch.cuda.get_device_properties(i)
            toplam_vram_gb = props.total_memory / (1024 ** 3)
            logger.info(f"    ├─ GPU #{i}: {props.name} | Toplam VRAM: {toplam_vram_gb:.2f} GB | Compute: {props.major}.{props.minor}")
        logger.info(f"  [GPU Tespitçisi] Ana Cihaz Seçildi: {self.ana_cihaz_adi} | Cihaz İndeksleri: {self.cihaz_idleri}")

    @property
    def coklu_gpu_mu(self) -> bool:
        return self.gpu_sayisi > 1

    @property
    def ana_cihaz(self) -> torch.device:
        return self.device


class GPU_EgitimDagitimcisi:
    """
    Model sinir ağlarını ve bileşenlerini PyTorch DataParallel ile 2/4 veya daha fazla GPU'ya
    dağıtan, GRPO grup genişliğini GPU sayısına göre ölçekleyen ve StiefelManifoldu dikgenliğini
    kök modül üzerinden yöneten paralel eğitim dağıtıcısı.
    """
    def __init__(self, tespitci: GPU_Tespitci):
        self.tespitci = tespitci

    def modulleri_paralellestir(self, moduller: Dict[str, nn.Module]) -> Dict[str, nn.Module]:
        """
        LOCO ve Sheaf Laplasyeni mimarisi uyarınca DataParallel sarmalaması sökülmüş;
        tüm modüller ana CUDA cihazına doğrudan bağlanır.
        """
        logger.info(f"  [GPU Eğitim Dağıtıcısı] DataParallel sarmalaması devre dışı bırakıldı. Tüm modüller ana cihaz ({self.tespitci.ana_cihaz}) üzerine taşınıyor...")
        paralel_moduller: Dict[str, nn.Module] = {}
        for ad, mod in moduller.items():
            if isinstance(mod, nn.Module):
                mod = mod.to(self.tespitci.ana_cihaz)
            paralel_moduller[ad] = mod
        return paralel_moduller

    def kok_modul_al(self, mod: nn.Module) -> nn.Module:
        """DataParallel ile sarılı modülün kök (.module) örneğini döndürür."""
        if isinstance(mod, nn.DataParallel):
            return mod.module
        return mod

    def stiefel_dikgenlestir(self, stiefel_izdusurucu: Any, phi_matrisleri: Any) -> None:
        """DataParallel sarmalamasından etkilenmeden Stiefel manifoldu dikgenleştirmesini güvenle çalıştırır."""
        try:
            stiefel_izdusurucu.izdüsür(phi_matrisleri)
        except Exception as e:
            logger.warning(f"  [Stiefel Paralel Warning] Dikgenleştirme uyarısı: {e}")


class GPU_CikarsamaDagitimcisi:
    """
    Çıkarım (inference) ve test sürecinde model değerlendirmesini çoklu GPU'lara
    dağıtan, bellek önbelleğini boşaltan ve CUDA senkronizasyonunu sağlayan çıkarım yöneticisi.
    """
    def __init__(self, tespitci: GPU_Tespitci):
        self.tespitci = tespitci

    def cikarsama_modeli_hazirla(self, model: nn.Module) -> nn.Module:
        """Çıkarım modelini ana GPU'ya veya çoklu GPU DataParallel yapısına bağlar."""
        model.eval()
        if self.tespitci.coklu_gpu_mu:
            logger.info(f"  [GPU Çıkarım Dağıtıcısı] Model {self.tespitci.gpu_sayisi} GPU üzerinde çıkarım moduna alındı.")
            return nn.DataParallel(model, device_ids=self.tespitci.cihaz_idleri)
        return model

    def bellek_temizle(self) -> None:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()


class Veri_Paralel_Dagitici:
    """
    [Hakiki Veri-Paralel Dosya Dağıtım Yöneticisi]
    5 TB veya herhangi bir boyuttaki ham veri dosyalarını donanımdaki GPU sayısına (1, 2, 4, 8 vb.)
    göre önceden dosya bazında hesaplayarak deterministik ve yük-dengeli olarak bölüştürür.
    
    Bu sayede eğitim esnasında GPU'lar arası dosya transferi veya dosya parçalanması gereksinimi
    tamamen ortadan kalkar. GRPO çeşitliliği, gürültü/hack formülleriyle değil, GPU'ların
    farklı veri dosyaları üzerinde paralel çalışmasıyla doğal olarak sağlanır.
    """
    def __init__(self, tespitci: GPU_Tespitci):
        self.tespitci = tespitci
        self.gpu_sayisi = max(1, tespitci.gpu_sayisi)

    def dosyalari_dagit(self, tum_dosyalar: List[str]) -> Dict[int, List[str]]:
        """
        Tüm dosya listesini GPU'lar arasında boyut ve indeks bazında önceden dengeli böler.
        Döndürür: {gpu_id: [dosya_yolu_1, dosya_yolu_2, ...]}
        """
        gpu_haritasi: Dict[int, List[str]] = {i: [] for i in range(self.gpu_sayisi)}
        
        # Dosyaları boyutlarına göre azalan sırada sırala (Greedy Load Balancing / Bin Packing)
        dosya_boyutlari: List[Tuple[str, int]] = []
        for d in tum_dosyalar:
            try:
                sz = os.path.getsize(d)
            except Exception:
                sz = 0
            dosya_boyutlari.append((d, sz))
            
        dosya_boyutlari.sort(key=lambda x: x[1], reverse=True)

        # Her dosyayı o an en az toplam yüke sahip GPU'ya ata
        gpu_yukleri = [0] * self.gpu_sayisi
        for d_path, d_sz in dosya_boyutlari:
            min_gpu = gpu_yukleri.index(min(gpu_yukleri))
            gpu_haritasi[min_gpu].append(d_path)
            gpu_yukleri[min_gpu] += max(1, d_sz)

        for gpu_id in range(self.gpu_sayisi):
            mb_toplam = gpu_yukleri[gpu_id] / (1024 * 1024)
            logger.info(f"  [Veri-Paralel Dağıtım] GPU #{gpu_id} için atanan dosya sayısı: {len(gpu_haritasi[gpu_id])} ({mb_toplam:.2f} MB)")

        return gpu_haritasi

    def get_gpu_dosyalari(self, tum_dosyalar: List[str], gpu_rank: int = 0) -> List[str]:
        """Belirtilen GPU rank'ine düşen dosya listesini döndürür."""
        harita = self.dosyalari_dagit(tum_dosyalar)
        return harita.get(gpu_rank % self.gpu_sayisi, tum_dosyalar)

class Homojen_Chunk_Dagitici:
    """
    Verisetindeki tüm dosyaları 64 KB'lık eşit parçalara bölüp,
    GPU'lara Modulo mantığıyla (global_chunk_idx % world_size == rank)
    milimetrik eşitlikle dağıtan modül.
    """
    def __init__(self, chunk_size_bytes: int = 65536, rank: int = 0, world_size: int = 1):
        self.chunk_size = chunk_size_bytes
        self.rank = rank
        self.world_size = max(1, world_size)

    def should_process_chunk(self, global_chunk_idx: int) -> bool:
        return (global_chunk_idx % self.world_size) == self.rank

# Geriye uyumluluk için takma ad (Yapay gürültüsüz veri-paralel çeşitlendirici)
class Topolojik_GPU_Cesitlendirici(nn.Module):
    """Stiefel teğet uzayı Lie-Cebiri jeodezik dönüşümlü topolojik GRPO çeşitlendiricisi."""
    def __init__(self, config: Any, noise_std: float = 0.01):
        super().__init__()
        self.config = config
        self.noise_std = noise_std

    def cesitlendir(self, x_start_grouped: torch.Tensor, step_seed: int = 0) -> torch.Tensor:
        """
        Stiefel teğet uzayında Lie-Cebiri so(D) antisimetrik üreteç matrisi A_g türeterek
        jeodezik üstel haritalama (matrix exponential) x_g = x_0 * exp(eps * A_g) uygular.
        Bu sayede manifold dikgenlik ve izometri korunarak hakiki GRPO çeşitliliği sağlanır.
        """
        if x_start_grouped.ndim < 2:
            return x_start_grouped
            
        G, D = x_start_grouped.shape[0], x_start_grouped.shape[-1]
        eps = self.noise_std if self.noise_std > 0 else 0.005
        
        # Generatör matrisler M_g [G, D, D]
        gen = torch.Generator(device=x_start_grouped.device)
        gen.manual_seed(step_seed)
        M = torch.randn((G, D, D), device=x_start_grouped.device, dtype=x_start_grouped.dtype, generator=gen)
        
        # Antisimetrik Lie-cebiri üreteci: A_g = 0.5 * (M - M^T) in so(D)
        A_g = 0.5 * (M - M.transpose(-1, -2))
        
        # 1. Derece Cayley Dönüşümü: Cayley(A) = (I - eps/2 * A)^-1 * (I + eps/2 * A)
        I = torch.eye(D, device=x_start_grouped.device, dtype=x_start_grouped.dtype).unsqueeze(0)
        A_eps = (0.5 * eps) * A_g
        with torch.cuda.amp.autocast(enabled=False):
            I_minus_A = (I - A_eps).float()
            I_plus_A = (I + A_eps).float()
            cayley_A = torch.linalg.solve(I_minus_A, I_plus_A).to(dtype=x_start_grouped.dtype)
        
        # Jeodezik dönüşüm: x_g = x_0 * Cayley(eps * A_g)
        x_g = torch.bmm(x_start_grouped.unsqueeze(1), cayley_A).squeeze(1)
        return x_g