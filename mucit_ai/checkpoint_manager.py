#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHECKPOINT_MANAGER — NPZ Tabanlı Model Durum Yöneticisi
=============================================================================
Bu modül, HDPEngine pretraining state'ini ve TTA optimizer state'ini
sıkıştırılmış NPZ formatında güvenilir biçimde kaydeder ve yükler.

Temel Tasarım Kararları:
  - Format: numpy.savez_compressed (.npz) — pickle bağımlılığı yok
  - Boyut garantisi: ≤ 300.6 MB (theta_spec float16'ya düşürülerek zorunlu hale getirilir)
  - Token offset: token_offset uint16 indeks olarak (byte değil) kaydedilir
  - Givens açıları ve gamma ölçekler: float32 olarak kaydedilir
  - Adam optimizer state (m, v): float32 olarak kaydedilir
  - Metadata (step, timestamp, loss): JSON sidecar dosyasına yazılır

Serileştirilen Alanlar:
  ┌──────────────────────────────┬────────────┬───────────────┐
  │ Alan                         │ dtype      │ Yaklaşık Boyut│
  ├──────────────────────────────┼────────────┼───────────────┤
  │ theta_spec [256,2880,184]    │ float32*   │ ~547 MB (fp32)│
  │                              │ float16†   │ ~274 MB (fp16)│
  │ givens_angles [120,1440]     │ float32    │ ~691 KB       │
  │ gamma_scales [120,4]         │ float32    │ ~2 KB         │
  │ qkv_phases [200]             │ float32    │ <1 KB         │
  │ G_boundary [120]             │ float32    │ <1 KB         │
  │ adam_m [13120]               │ float32    │ ~51 KB        │
  │ adam_v [13120]               │ float32    │ ~51 KB        │
  │ token_offset [1]             │ int64      │ negligible    │
  │ step [1]                     │ int64      │ negligible    │
  │ loss_history [≤100]          │ float32    │ <1 KB         │
  └──────────────────────────────┴────────────┴───────────────┘
  * float32 ile total ~548 MB → sınırı aşar → † float16'ya dönüştürülür
  † Sıkıştırma sonrası theta_spec float16 ≈ 260–280 MB → sınır içinde

Eski pickle tabanlı arayüz geriye uyumlu bırakılmıştır (CheckpointSerializer,
CognitiveState, CheckpointMetadata). Yeni kod NPZCheckpointManager kullanır.
=============================================================================
"""

import json
import logging
import os
import pickle
import time
from dataclasses import dataclass, field
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
try:
    import torch
except ImportError:
    torch = None

logger = logging.getLogger("CheckpointMgr")


def _flatten_nested_state_dict(st: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """
    Hiyerarşik (iç içe geçmiş) PyTorch state_dict nesnelerini düzleştirir.
    Modül isim silsilesini ('n1_byte.weight' vb.) korur ve çakışmaları engeller.
    """
    flat = {}
    if not isinstance(st, dict):
        return st
    for k, v in st.items():
        key = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, dict):
            flat.update(_flatten_nested_state_dict(v, prefix=key))
        else:
            flat[key] = v
    return flat

# ===========================================================================
# SABITLER
# ===========================================================================
CHECKPOINT_MAX_MB: float = 300.6
CHECKPOINT_VERSION: str  = "2.0.0"    # NPZ formatı versiyonu


# ===========================================================================
# VERI YAPILARI — Geriye Uyumluluk
# ===========================================================================
@dataclass
class CheckpointMetadata:
    version: str = CHECKPOINT_VERSION
    timestamp: float = 0.0
    step: int = 0
    chunk_index: int = 0
    token_offset: int = 0          # uint16 indeks (byte değil) — YENİ
    loss: float = 0.0
    dcm_rank: int = 0
    dcm_saturation: float = 0.0
    dcm_synthesis_count: int = 0
    memory_rank: int = 0
    phase: str = "pretraining"
    engine_mode: str = "kaggle"
    config_snapshot: Optional[Dict] = None


@dataclass
class CognitiveState:
    """
    Geriye uyumluluk için korunan eski state container.
    Yeni kod NPZCheckpointManager.save() / .load() kullanır.
    """
    model_params: Optional[Dict] = None       # {"theta_spec": np.ndarray, ...}
    topos_state: Optional[Dict] = None
    m_matrix: Optional[np.ndarray] = None
    hegel_memory: Optional[Dict] = None
    lsh_forest: Optional[Dict] = None
    optimizer_state: Optional[Dict] = None    # {"m": ..., "v": ..., "step": ...}
    sheaf_buffer: Optional[Dict] = None
    spectral_field: Optional[Dict] = None
    shader_state: Optional[Dict] = None
    shader_uniforms: Optional[Dict] = None
    hologram_H_weights: Optional[np.ndarray] = None
    hologram_H_context: Optional[np.ndarray] = None


# ===========================================================================
# 3 KADEMELİ HİYERARŞİK DOSYA VE VERİ KÜMESİ TAKİP HAFIZASI
# ===========================================================================
class HiyerarşikHafizaYoneticisi:
    """
    3 Kademeli Hiyerarşik Dosya ve Veri Kümesi Takip Hafızası.
    - Level 1: biten_dosyalar (Set[str]) -> Tekil tamamlanmış dosya yolları
    - Level 2: biten_klasorler (Set[str]) -> Bir klasördeki tüm dosyalar bittiğinde eklenir, tekil dosyalar temizlenir.
    - Level 3: biten_verisetleri (Set[str]) -> Bir veri kümesindeki tüm klasörler bittiğinde eklenir, klasör/dosyalar temizlenir.
    """
    def __init__(self):
        self.biten_dosyalar: set = set()
        self.biten_klasorler: set = set()
        self.biten_verisetleri: set = set()

    def is_dosya_islenmis(self, dosya_yolu: str, klasor_yolu: str = "", veriseti_adi: str = "") -> bool:
        norm_file = os.path.normpath(dosya_yolu) if dosya_yolu else ""
        norm_folder = os.path.normpath(klasor_yolu) if klasor_yolu else (os.path.dirname(norm_file) if norm_file else "")
        
        if veriseti_adi and veriseti_adi in self.biten_verisetleri:
            return True
        if norm_folder and norm_folder in self.biten_klasorler:
            return True
        if norm_file and norm_file in self.biten_dosyalar:
            return True
        return False

    def dosya_tamamlandi(self, dosya_yolu: str, klasor_yolu: str = "", veriseti_adi: str = "", tum_klasor_dosyalari: Optional[List[str]] = None, tum_veriseti_klasorleri: Optional[List[str]] = None):
        norm_file = os.path.normpath(dosya_yolu)
        norm_folder = os.path.normpath(klasor_yolu) if klasor_yolu else os.path.dirname(norm_file)
        
        self.biten_dosyalar.add(norm_file)
        logger.debug(f"  [Hafıza] Dosya tamamlandı: {norm_file}")
        
        # Klasördeki tüm dosyalar bitti mi kontrol et
        if tum_klasor_dosyalari and len(tum_klasor_dosyalari) > 0:
            all_files_done = all(os.path.normpath(f) in self.biten_dosyalar for f in tum_klasor_dosyalari)
            if all_files_done:
                self.biten_klasorler.add(norm_folder)
                for f in tum_klasor_dosyalari:
                    self.biten_dosyalar.discard(os.path.normpath(f))
                logger.info(f"  [Hafıza] Klasördeki TÜM dosyalar tamamlandı! Klasör seviyesine yükseltildi, dosyalar temizlendi: {norm_folder}")
                
                # Veri setindeki tüm klasörler bitti mi kontrol et
                if veriseti_adi and tum_veriseti_klasorleri and len(tum_veriseti_klasorleri) > 0:
                    all_folders_done = all(os.path.normpath(k) in self.biten_klasorler for k in tum_veriseti_klasorleri)
                    if all_folders_done:
                        self.biten_verisetleri.add(veriseti_adi)
                        for k in tum_veriseti_klasorleri:
                            self.biten_klasorler.discard(os.path.normpath(k))
                        logger.info(f"  [Hafıza] Veri setindeki TÜM klasörler tamamlandı! Veri seti seviyesine yükseltildi: {veriseti_adi}")

    def to_dict(self) -> Dict[str, List[str]]:
        return {
            "biten_verisetleri": sorted(list(self.biten_verisetleri)),
            "biten_klasorler": sorted(list(self.biten_klasorler)),
            "biten_dosyalar": sorted(list(self.biten_dosyalar))
        }

    def from_dict(self, data: Dict[str, Any]):
        if not data:
            return
        self.biten_verisetleri = set(data.get("biten_verisetleri", []))
        self.biten_klasorler = set(data.get("biten_klasorler", []))
        self.biten_dosyalar = set(data.get("biten_dosyalar", []))


# ===========================================================================
# NPZ CHECKPOINT MANAGER — Ana Sınıf
# ===========================================================================
class NPZCheckpointManager:
    """
    HDPEngine için NPZ tabanlı checkpoint yöneticisi.

    Seri/deserializasyon:
      - theta_spec: float32 kaydedilir; boyut > 300.6 MB ise float16'ya düşürülür
      - givens_angles, gamma_scales, qkv_phases, G_boundary: float32
      - adam_m, adam_v: float32 (~51 KB her biri)
      - token_offset, step: int64 skaler
      - loss_history: float32 [son 100]
    Tüm alanlar numpy.savez_compressed ile tek .npz dosyasına yazılır.
    Metadata (step, timestamp, version, hiyerarşik hafıza) JSON sidecar'a da yazılır.
    """

    def __init__(self,
                 checkpoint_dir: str = "/kaggle/working",
                 keep_last: int = 2,
                 max_mb: float = CHECKPOINT_MAX_MB):
        self.checkpoint_dir = checkpoint_dir
        self.keep_last      = keep_last
        self.max_mb         = max_mb
        self.hafiza         = HiyerarşikHafizaYoneticisi()
        self._history: List[str] = []
        import threading
        self._save_lock     = threading.Lock()
        os.makedirs(checkpoint_dir, exist_ok=True)

    # -----------------------------------------------------------------------
    # Hiyerarşik Hafıza Durumu (Hafif JSON Kaydı)
    # -----------------------------------------------------------------------
    def _hafiza_state_path(self) -> str:
        return os.path.join(self.checkpoint_dir, "hafiza_state.json")

    def save_hafiza_state(self) -> str:
        """
        Hiyerarşik hafıza takibini (işlenen dosya/klasör/veriseti kümesi)
        ağır model ağırlıklarından bağımsız olarak anlık ve atomik JSON olarak kaydeder (~5 KB).
        """
        path = self._hafiza_state_path()
        tmp_path = os.path.join(self.checkpoint_dir, "hafiza_state_tmp.json")
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self.hafiza.to_dict(), f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, path)
        except Exception as exc:
            logger.warning(f"  [Hafıza State] Kayıt hatası: {exc}")
        return path

    def load_hafiza_state(self) -> bool:
        """
        Hiyerarşik hafıza durumunu JSON dosyasından okur.
        Yerel dizini ve bağlı eğitim notebook çıktısını (/kaggle/input/notebooks/ulankaggle/mucit-ai) kontrol eder.
        """
        candidate_paths = [
            self._hafiza_state_path(),
            "/kaggle/input/notebooks/ulankaggle/mucit-ai/hafiza_state.json"
        ]
        for path in candidate_paths:
            if os.path.isfile(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.hafiza.from_dict(data)
                        logger.info(f"  [Hafıza State] Hiyerarşik hafıza durumu okundu: {path}")
                        return True
                except Exception as exc:
                    logger.warning(f"  [Hafıza State] Okuma hatası ({path}): {exc}")
        return False

    def purge_orphan_checkpoints(self) -> None:
        """
        Kaggle disk dolmasını önlemek için birikmiş tüm dinamik step/epoch .pt, geçici _tmp ve
        eski format checkpoint_*.npz yetim dosyalarını diskten tamamen temizler. Diskte sadece sabit 'latest' ve 'best' kalır.
        """
        if not os.path.isdir(self.checkpoint_dir):
            return
        purged_count = 0
        for fname in os.listdir(self.checkpoint_dir):
            fpath = os.path.join(self.checkpoint_dir, fname)

            if os.path.isdir(fpath):
                continue

            # Geçici veya yetim dosya kalıplarını yakala
            is_tmp_file = fname.endswith(".tmp") or "_tmp." in fname
            is_dynamic_pt = (fname.startswith("topolojik_model_step_") or fname.startswith("topolojik_model_epoch_")) and fname.endswith(".pt")
            is_dynamic_npz = fname.startswith("checkpoint_") and fname.endswith(".npz") and not (fname.startswith("checkpoint_latest") or fname.startswith("checkpoint_best"))
            is_dynamic_meta = fname.startswith("checkpoint_") and fname.endswith("_meta.json") and not (fname.startswith("checkpoint_latest") or fname.startswith("checkpoint_best"))

            if is_tmp_file or is_dynamic_pt or is_dynamic_npz or is_dynamic_meta:
                try:
                    os.remove(fpath)
                    purged_count += 1
                except OSError as exc:
                    logger.warning(f"  [Purge] Dosya silinemedi: {fpath} ({exc})")

        # Karşılaşılabilecek sheaf_restrictions alt klasöründeki eski verileri de temizle
        sheaf_dir = os.path.join(self.checkpoint_dir, "sheaf_restrictions")
        if os.path.isdir(sheaf_dir):
            try:
                import shutil
                shutil.rmtree(sheaf_dir)
                logger.info(f"  [Purge] Geçici sheaf_restrictions dizini temizlendi.")
            except Exception as e:
                logger.warning(f"  [Purge] Sheaf dizini temizleme hatası: {e}")

        if purged_count > 0:
            logger.info(f"  [Purge] {purged_count} adet eski dinamik/geçici checkpoint artığı diskten temizlendi.")

    # -----------------------------------------------------------------------
    # Yol Yardımcıları
    # -----------------------------------------------------------------------
    def _npz_path(self, step: int, is_best: bool = False) -> str:
        tag = "best" if is_best else "latest"
        return os.path.join(self.checkpoint_dir, f"checkpoint_{tag}.npz")

    def _meta_path(self, npz_path: str) -> str:
        return npz_path.replace(".npz", "_meta.json")

    # -----------------------------------------------------------------------
    # Kayıt (Sabit İsimli Atomik Üzerine Yazma)
    # -----------------------------------------------------------------------
    def save(self,
             step: int,
             token_offset: int,
             model: Any,
             optimizer_m: Optional[np.ndarray] = None,
             optimizer_v: Optional[np.ndarray] = None,
             loss_history: Optional[List[float]] = None,
             extra: Optional[Dict[str, np.ndarray]] = None,
             is_best: bool = False) -> str:
        """
        Model durumunu ve token_offset'i sabit isimli NPZ olarak atomik kaydeder.
        """
        payload: Dict[str, np.ndarray] = {}

        # Spektral ağırlıklar
        theta = getattr(model, "theta_spec", None)
        if theta is not None:
            payload["theta_spec"] = theta.astype(np.float32)

        # Sürekli parametreler
        payload["givens_angles"] = np.asarray(
            getattr(model, "givens_angles", np.zeros((120, 1440), np.float32)),
            dtype=np.float32
        )
        payload["gamma_scales"] = np.asarray(
            getattr(model, "gamma_scales", np.ones((120, 4), np.float32)),
            dtype=np.float32
        )
        payload["qkv_phases"] = np.asarray(
            getattr(model, "qkv_phases", np.zeros(200, np.float32)),
            dtype=np.float32
        )
        payload["G_boundary"] = np.asarray(
            getattr(model, "G_boundary", np.zeros(120, np.float32)),
            dtype=np.float32
        )

        # Adam optimizer state
        if optimizer_m is not None:
            payload["adam_m"] = optimizer_m.astype(np.float32)
        elif hasattr(model, "_adam_m") and model._adam_m is not None:
            payload["adam_m"] = model._adam_m.astype(np.float32)

        if optimizer_v is not None:
            payload["adam_v"] = optimizer_v.astype(np.float32)
        elif hasattr(model, "_adam_v") and model._adam_v is not None:
            payload["adam_v"] = model._adam_v.astype(np.float32)

        # Token offset ve step
        payload["token_offset"] = np.array([token_offset], dtype=np.int64)
        payload["step"]         = np.array([step],         dtype=np.int64)

        # Loss history
        hist = loss_history or []
        payload["loss_history"] = np.array(hist[-100:], dtype=np.float32)

        # Ek alanlar
        if extra:
            for k, v in extra.items():
                payload[k] = np.asarray(v)

        # ---- VRAM MUHAFIZI (VMM Allocator Guard) & 300.6 MB Boyut Garantisi ----
        try:
            import kulli_gpu
            if kulli_gpu._GLOBAL_DRIVER_INSTANCE is not None and hasattr(kulli_gpu._GLOBAL_DRIVER_INSTANCE, "vmm_allocator"):
                allocator = kulli_gpu._GLOBAL_DRIVER_INSTANCE.vmm_allocator
                free_gb = (allocator.virtual_vram_bytes - allocator.allocated_vram_bytes) / (1024**3)
                total_gb = allocator.virtual_vram_gb
                free_pct = (free_gb / total_gb) * 100 if total_gb > 0 else 100
                if free_pct < 15.0 or free_gb < 4.0:
                    logger.warning(
                        f"  [Ckpt VRAM Guard] Serbest VRAM %{free_pct:.1f} ({free_gb:.1f} GB) seviyesine düştü. "
                        f"'theta_spec' FP16'ya otomatik dönüştürülüyor..."
                    )
                    if "theta_spec" in payload and payload["theta_spec"].dtype != np.float16:
                        payload["theta_spec"] = payload["theta_spec"].astype(np.float16)
        except Exception as vmm_exc:
            logger.debug(f"[Checkpoint VRAM Guard Notice] {vmm_exc}")

        # ---- Dosyaya Atomik Yaz (tmp -> replace) ----
        out_path = self._npz_path(step, is_best=is_best)
        tmp_path = out_path.replace(".npz", "_tmp.npz")
        np.savez_compressed(tmp_path, **payload)

        # ---- 300.6 MB Boyut Garantisi ----
        size_mb = os.path.getsize(tmp_path) / 1024 / 1024
        if size_mb > self.max_mb:
            logger.warning(
                f"  [Ckpt] Boyut {size_mb:.1f} MB > {self.max_mb} MB — "
                f"theta_spec float16'ya dönüştürülüyor..."
            )
            if "theta_spec" in payload and payload["theta_spec"].dtype != np.float16:
                payload["theta_spec"] = payload["theta_spec"].astype(np.float16)
            np.savez_compressed(tmp_path, **payload)
            size_mb = os.path.getsize(tmp_path) / 1024 / 1024

        os.replace(tmp_path, out_path)

        # ---- JSON Sidecar Metadata ----
        self._write_meta(out_path, step, token_offset, size_mb, loss_history)

        # Hafıza durumunu da anlık kaydet
        self.save_hafiza_state()

        logger.info(
            f"  [Ckpt] Sabit Atomik NPZ Kaydedildi: {out_path} "
            f"({size_mb:.1f} MB) | step={step} | token_offset={token_offset:,}"
        )
        return out_path

    def save_pytorch_model(self,
                           step: int,
                           token_offset: int,
                           model: Any,
                           optimizer: Optional[Any] = None,
                           loss_history: Optional[List[float]] = None,
                           is_best: bool = False) -> str:
        """
        Hakiki PyTorch nn.Module ve Optimizer durumunu sabit isimli atomik .pt ve .npz olarak kaydeder.
        Diskte her zaman sabit 'latest' ve 'best' sürümleri kalır, yer dolması kesin engellenir.
        """
        extra_weights: Dict[str, np.ndarray] = {}
        
        # 1. Modül Ağırlıklarının Çıkarılması
        if torch is not None:
            if hasattr(model, 'state_dict'):
                for k, v in model.state_dict().items():
                    extra_weights[f"param_{k}"] = v.detach().cpu().numpy()
            elif isinstance(model, dict):
                for mod_name, mod in model.items():
                    if hasattr(mod, 'state_dict'):
                        for k, v in mod.state_dict().items():
                            extra_weights[f"param_{mod_name}.{k}"] = v.detach().cpu().numpy()

        # 2. NPZ Kaydı
        npz_path = self.save(
            step=step,
            token_offset=token_offset,
            model=model if hasattr(model, 'theta_spec') else type("SpecHolder", (), {"theta_spec": None})(),
            loss_history=loss_history,
            extra=extra_weights,
            is_best=is_best
        )

        # 3. Hakiki PyTorch .pt Atomik Kaydı (_tmp.pt -> replace)
        if torch is not None:
            tag = "best" if is_best else "latest"
            pt_path = os.path.join(self.checkpoint_dir, f"topolojik_model_{tag}.pt")
            import uuid
            pt_tmp = os.path.join(self.checkpoint_dir, f"topolojik_model_{tag}_tmp_{uuid.uuid4().hex}.pt")

            state_dict_to_save = {}
            if hasattr(model, 'state_dict'):
                state_dict_to_save['model'] = model.state_dict()
            elif isinstance(model, dict):
                state_dict_to_save['model'] = {k: m.state_dict() for k, m in model.items() if hasattr(m, 'state_dict')}
            
            if optimizer is not None and hasattr(optimizer, 'state_dict'):
                state_dict_to_save['optimizer'] = optimizer.state_dict()
            state_dict_to_save['step'] = step
            state_dict_to_save['loss_history'] = loss_history or []
            
            import threading
            
            def _to_cpu_async(obj: Any) -> Any:
                if isinstance(obj, dict):
                    return {k: _to_cpu_async(v) for k, v in obj.items()}
                elif hasattr(obj, 'detach') and hasattr(obj, 'to'):
                    try:
                        return obj.detach().clone().to('cpu', non_blocking=False)
                    except Exception:
                        return obj
                return obj

            state_dict_cpu = _to_cpu_async(state_dict_to_save)

            def _bg_save_worker(sd: Dict[str, Any], tmp_p: str, final_p: str, lock: Any):
                with lock:
                    try:
                        torch.save(sd, tmp_p)
                        os.replace(tmp_p, final_p)
                        logger.info(f"  [Ckpt Mgr] Sabit PyTorch Kontrol Noktası (.pt) Arka Planda Kaydedildi: {final_p}")
                    except Exception as ex:
                        logger.warning(f"  [Ckpt Mgr] Arka plan checkpoint kaydı hatası: {ex}")

            threading.Thread(target=_bg_save_worker, args=(state_dict_cpu, pt_tmp, pt_path, self._save_lock), daemon=True).start()
            
        return npz_path

    def load_pytorch_model(self,
                           model: Any,
                           optimizer: Optional[Any] = None,
                           path: Optional[str] = None,
                           step: Optional[int] = None) -> Tuple[int, List[float]]:
        """
        NPZ veya .pt kontrol noktasından Hakiki PyTorch model, optimizer ve hiyerarşik hafızayı yükler.
        """
        # Hiyerarşik hafıza state'ini anlık JSON'dan da yüklemeyi dene
        self.load_hafiza_state()

        resolved = self._resolve_path(path, step)
        
        # Öncelikli PyTorch candidate yollarını sorgula (best > latest > resolved)
        pt_candidates = []
        if path and path.endswith(".pt") and os.path.isfile(path):
            pt_candidates.append(path)
        pt_candidates.append(os.path.join(self.checkpoint_dir, "topolojik_model_best.pt"))
        pt_candidates.append(os.path.join(self.checkpoint_dir, "topolojik_model_latest.pt"))
        pt_candidates.append("/kaggle/input/notebooks/ulankaggle/mucit-ai/topolojik_model_best.pt")
        pt_candidates.append("/kaggle/input/notebooks/ulankaggle/mucit-ai/topolojik_model_latest.pt")
        if resolved:
            pt_candidates.append(resolved.replace(".npz", ".pt").replace("checkpoint_", "topolojik_model_"))

        pt_file = None
        for cand in pt_candidates:
            if os.path.isfile(cand):
                pt_file = cand
                break

        if torch is not None and pt_file is not None:
            try:
                checkpoint = torch.load(pt_file, map_location="cpu")
                if 'model' in checkpoint:
                    st = checkpoint['model']
                    flat_st = _flatten_nested_state_dict(st) if isinstance(st, dict) else st
                    if hasattr(model, 'load_state_dict'):
                        model.load_state_dict(flat_st, strict=False)
                    elif isinstance(model, dict):
                        for k, m in model.items():
                            if hasattr(m, 'load_state_dict'):
                                sub_st = {sub_k[len(k)+1:]: v for sub_k, v in flat_st.items() if isinstance(sub_k, str) and sub_k.startswith(f"{k}.")}
                                if sub_st:
                                    m.load_state_dict(sub_st, strict=False)
                                elif isinstance(st, dict) and k in st and hasattr(st[k], 'items'):
                                    m.load_state_dict(st[k], strict=False)
                    logger.info(f"  [Ckpt Mgr] Hakiki PyTorch Modül Ağırlıkları Yüklendi: {pt_file}")
                
                if optimizer is not None and 'optimizer' in checkpoint and hasattr(optimizer, 'load_state_dict'):
                    try:
                        optimizer.load_state_dict(checkpoint['optimizer'])
                        logger.info(f"  [Ckpt Mgr] Hakiki Optimizer Durumu Yüklendi.")
                    except Exception as e:
                        logger.warning(f"  [Ckpt Mgr] Optimizer yükleme uyarısı: {e}")

                step_ret = checkpoint.get('step', 0)
                loss_ret = checkpoint.get('loss_history', [])
                return step_ret, loss_ret
            except Exception as exc:
                logger.warning(f"  [Ckpt Mgr] .pt yükleme hatası ({exc}), .npz yüklemesine geçiliyor.")

        if resolved is None:
            logger.warning(f"  [Ckpt Mgr] Yüklenecek kontrol noktası bulunamadı.")
            return 0, []

        # NPZ yüklemesi fallback
        ckpt_data = self.load(path=resolved)
        step_ret = ckpt_data.get("step", 0)
        loss_ret = ckpt_data.get("loss_history", [])
        return step_ret, loss_ret

    def _write_meta(self, npz_path: str, step: int, token_offset: int,
                    size_mb: float, loss_history: Optional[List[float]]) -> None:
        meta = {
            "version":           CHECKPOINT_VERSION,
            "timestamp":         time.time(),
            "step":              step,
            "token_offset":      token_offset,
            "size_mb":           round(size_mb, 2),
            "last_loss":         float(loss_history[-1]) if loss_history else 0.0,
            "hiyerarsik_hafiza": self.hafiza.to_dict()
        }
        meta_path = self._meta_path(npz_path)
        try:
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2, ensure_ascii=False)
        except OSError as exc:
            logger.warning(f"  [Ckpt] Meta yazılamadı: {exc}")


    # -----------------------------------------------------------------------
    # Yükleme
    # -----------------------------------------------------------------------
    def load(self, path: Optional[str] = None,
             step: Optional[int] = None) -> Dict[str, Any]:
        resolved = self._resolve_path(path, step)
        if resolved is None:
            raise FileNotFoundError(
                f"Checkpoint bulunamadı: dir={self.checkpoint_dir} "
                f"path={path} step={step}"
            )

        data = np.load(resolved, allow_pickle=False)

        # Meta dosyasından hiyerarşik hafızayı yükle
        meta_path = self._meta_path(resolved)
        meta_dict = {}
        if os.path.isfile(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta_dict = json.load(f)
                    if "hiyerarsik_hafiza" in meta_dict:
                        self.hafiza.from_dict(meta_dict["hiyerarsik_hafiza"])
            except Exception as exc:
                logger.warning(f"  [Ckpt] Meta okunurken hata: {exc}")

        result: Dict[str, Any] = {
            "path":              resolved,
            "token_offset":      int(data["token_offset"][0]) if "token_offset" in data else 0,
            "step":              int(data["step"][0])          if "step"         in data else 0,
            "loss_history":      list(data["loss_history"])    if "loss_history" in data else [],
            "theta_spec":        data["theta_spec"].astype(np.float32) if "theta_spec"    in data else None,
            "givens_angles":     data["givens_angles"].astype(np.float32) if "givens_angles" in data else None,
            "gamma_scales":      data["gamma_scales"].astype(np.float32)  if "gamma_scales"  in data else None,
            "qkv_phases":        data["qkv_phases"].astype(np.float32)    if "qkv_phases"    in data else None,
            "G_boundary":        data["G_boundary"].astype(np.float32)    if "G_boundary"    in data else None,
            "adam_m":            data["adam_m"].astype(np.float32)        if "adam_m"        in data else None,
            "adam_v":            data["adam_v"].astype(np.float32)        if "adam_v"        in data else None,
            "hiyerarsik_hafiza": self.hafiza.to_dict()
        }

        logger.info(
            f"  [Ckpt] Yüklendi: {resolved} | "
            f"step={result['step']} | "
            f"token_offset={result['token_offset']:,}"
        )
        return result

    def restore_to_engine(self, engine: Any,
                          path: Optional[str] = None,
                          step: Optional[int] = None) -> int:
        """
        Checkpoint'i HDPEngine'e geri yükler.

        Döndürür: devam edilecek step numarası.
        """
        d = self.load(path=path, step=step)

        model = engine.model

        # Spektral ağırlıklar
        if d["theta_spec"] is not None:
            model.theta_spec = d["theta_spec"]

        # Sürekli parametreler
        if d["givens_angles"] is not None:
            model.givens_angles = d["givens_angles"]
        if d["gamma_scales"] is not None:
            model.gamma_scales = d["gamma_scales"]
        if d["qkv_phases"] is not None:
            model.qkv_phases = d["qkv_phases"]
        if d["G_boundary"] is not None:
            model.G_boundary = d["G_boundary"]

        # Adam optimizer state
        if d["adam_m"] is not None:
            model._adam_m = d["adam_m"]
        if d["adam_v"] is not None:
            model._adam_v = d["adam_v"]

        # Token offset (pretraining kaldığı yerden devam)
        engine.data_offset.token_offset = d["token_offset"]
        engine.optimizer_state["step"]  = d["step"]

        # Loss history
        if d["loss_history"]:
            engine.loss_history = d["loss_history"]

        logger.info(
            f"  [Ckpt] HDPEngine geri yüklendi | "
            f"step={d['step']} | token_offset={d['token_offset']:,}"
        )
        return d["step"]

    # -----------------------------------------------------------------------
    # Yol Çözme
    # -----------------------------------------------------------------------
    def _resolve_path(self, path: Optional[str],
                      step: Optional[int]) -> Optional[str]:
        if path is not None and os.path.isfile(path):
            return path
        if step is not None:
            p = self._npz_path(step)
            if os.path.isfile(p):
                return p
        # Geçmiş listesinden en son
        if self._history:
            return self._history[-1]
        # Dizinde en son .npz dosyası
        return self.get_latest()

    def get_latest(self) -> Optional[str]:
        """Checkpoint dizinindeki en son sabit veya dinamik NPZ dosyasını döndürür."""
        if not os.path.isdir(self.checkpoint_dir):
            return None
        
        # Sabit dosya isimleri önceliği
        latest_fixed = os.path.join(self.checkpoint_dir, "checkpoint_latest.npz")
        if os.path.isfile(latest_fixed):
            return latest_fixed

        best_fixed = os.path.join(self.checkpoint_dir, "checkpoint_best.npz")
        if os.path.isfile(best_fixed):
            return best_fixed

        candidates = sorted([
            f for f in os.listdir(self.checkpoint_dir)
            if f.startswith("checkpoint_") and f.endswith(".npz")
        ])
        if not candidates:
            return None
        return os.path.join(self.checkpoint_dir, candidates[-1])

    def list_checkpoints(self) -> List[Dict]:
        """Mevcut tüm checkpoint'lerin özetini döndürür."""
        if not os.path.isdir(self.checkpoint_dir):
            return []
        results = []
        for fname in sorted(os.listdir(self.checkpoint_dir)):
            if not (fname.startswith("checkpoint_") and fname.endswith(".npz")):
                continue
            fpath    = os.path.join(self.checkpoint_dir, fname)
            size_mb  = os.path.getsize(fpath) / 1024 / 1024
            meta_path = self._meta_path(fpath)
            meta: Dict = {}
            if os.path.isfile(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                except (json.JSONDecodeError, OSError):
                    pass
            results.append({
                "path":         fpath,
                "filename":     fname,
                "size_mb":      round(size_mb, 2),
                "within_limit": size_mb <= self.max_mb,
                "metadata":     meta,
            })
        return results

    def verify(self, path: str) -> Dict:
        """NPZ checkpoint bütünlüğünü doğrular."""
        result: Dict = {"valid": False, "errors": [], "size_mb": 0.0}
        if not os.path.isfile(path):
            result["errors"].append("Dosya bulunamadı")
            return result
        result["size_mb"] = round(os.path.getsize(path) / 1024 / 1024, 2)
        try:
            data = np.load(path, allow_pickle=False)
            required = ["token_offset", "step"]
            for key in required:
                if key not in data:
                    result["errors"].append(f"Eksik alan: {key}")
            if result["size_mb"] > self.max_mb:
                result["errors"].append(
                    f"Boyut sınırı aşıldı: {result['size_mb']:.1f} MB > {self.max_mb} MB"
                )
            result["valid"] = len(result["errors"]) == 0
            result["keys"]  = list(data.keys())
        except Exception as exc:
            result["errors"].append(str(exc))
        return result

    # -----------------------------------------------------------------------
    # Eski Checkpoint Temizliği
    # -----------------------------------------------------------------------
    def _cleanup_old(self) -> None:
        if len(self._history) <= self.keep_last:
            return
        to_remove = self._history[: -self.keep_last]
        for old in to_remove:
            try:
                if os.path.isfile(old):
                    os.remove(old)
                meta = self._meta_path(old)
                if os.path.isfile(meta):
                    os.remove(meta)
                logger.debug(f"  [Ckpt] Eski checkpoint silindi: {old}")
            except OSError as exc:
                logger.warning(f"  [Ckpt] Silme hatası: {exc}")
        self._history = self._history[-self.keep_last:]



# ===========================================================================
# GERİYE UYUMLU PICKLE KATMANI
# (Eski train_launcher.py ve arc_solver.py çağrıları için korundu)
# ===========================================================================
class CheckpointSerializer:
    """Korunan eski serializer — NPZCheckpointManager'a yönlendirir."""

    def __init__(self, precision: str = "float32"):
        self.precision = precision

    def serialize_array(self, arr: np.ndarray) -> bytes:
        return arr.astype(np.float32).tobytes()

    def deserialize_array(self, data: bytes,
                          shape: Tuple[int, ...]) -> np.ndarray:
        return np.frombuffer(data, dtype=np.float32).reshape(shape)

    def serialize_dict_of_arrays(self, d: Dict) -> Dict:
        result = {}
        for k, v in d.items():
            if isinstance(v, np.ndarray):
                result[k] = {"_type": "ndarray", "_shape": v.shape,
                              "_data": self.serialize_array(v)}
            elif isinstance(v, dict):
                result[k] = self.serialize_dict_of_arrays(v)
            else:
                result[k] = v
        return result

    def deserialize_dict_of_arrays(self, d: Dict) -> Dict:
        result = {}
        for k, v in d.items():
            if isinstance(v, dict) and v.get("_type") == "ndarray":
                shape = tuple(v["_shape"])
                raw   = v["_data"] if isinstance(v["_data"], bytes) \
                        else v["_data"].encode("latin1")
                result[k] = self.deserialize_array(raw, shape)
            elif isinstance(v, dict):
                result[k] = self.deserialize_dict_of_arrays(v)
            else:
                result[k] = v
        return result


def _flatten_nested_state_dict(st: dict) -> dict:
    """İç içe geçmiş modül sözlüklerini (örn. {'n1_byte': {'weight': ...}}) düzleştirir."""
    if not isinstance(st, dict):
        return st
    flat = {}
    def _recurse(d, prefix=""):
        if isinstance(d, dict):
            for k, v in d.items():
                pfx = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    _recurse(v, pfx)
                else:
                    flat[pfx] = v
        else:
            if prefix:
                flat[prefix] = d
    _recurse(st)
    
    cleaned = {}
    for k, v in flat.items():
        clean_k = k[6:] if isinstance(k, str) and k.startswith("param_") else k
        cleaned[clean_k] = v
    return cleaned


class CheckpointManager:
    """
    Geriye uyumlu ana sınıf.
    Dahili olarak NPZCheckpointManager'ı çağırır.
    Eski pickle formatındaki checkpoint'leri de okuyabilir (fallback).
    """

    def __init__(self,
                 checkpoint_dir: str = "checkpoints",
                 keep_last: int = 2,
                 precision: str = "float32",
                 max_checkpoint_mb: float = CHECKPOINT_MAX_MB):
        self.checkpoint_dir     = checkpoint_dir
        self.keep_last          = keep_last
        self.max_checkpoint_mb  = max_checkpoint_mb
        self.serializer         = CheckpointSerializer(precision=precision)
        self.cognitive_state    = CognitiveState()
        self.metadata           = CheckpointMetadata()
        self.current_path: Optional[str] = None
        self._checkpoint_history: List[str] = []
        self._npz_mgr = NPZCheckpointManager(
            checkpoint_dir=checkpoint_dir,
            keep_last=keep_last,
            max_mb=max_checkpoint_mb,
        )
        os.makedirs(checkpoint_dir, exist_ok=True)

    # ---- NPZ Yolu Yardımcıları (eski .bin yolu gibi görünen API) ----
    def _get_checkpoint_path(self, step: int, chunk_index: int) -> str:
        # Yeni format: .npz; eski API chunk_index kullanırdı
        return os.path.join(
            self.checkpoint_dir,
            f"checkpoint_s{step:06d}_c{chunk_index:03d}.npz",
        )

    def _get_metadata_path(self, checkpoint_path: str) -> str:
        base = checkpoint_path.replace(".npz", "").replace(".bin", "")
        return base + "_meta.json"

    # ---- Kayıt (NPZ formatı) ----
    def save_checkpoint(self,
                        step: int,
                        chunk_index: int,
                        cognitive_state: CognitiveState,
                        metadata: Optional[CheckpointMetadata] = None) -> str:
        """
        CognitiveState'i NPZ olarak kaydeder.
        model_params'tan theta_spec ve optimizer_state'ten adam_m/adam_v alınır.
        """
        if metadata is None:
            metadata = CheckpointMetadata()
        metadata.version   = CHECKPOINT_VERSION
        metadata.timestamp = time.time()
        metadata.step      = step
        metadata.chunk_index = chunk_index

        # Sahte model nesnesi oluştur (NPZCheckpointManager model bekler)
        class _FakeModel:
            pass
        fake = _FakeModel()
        fake._adam_m = None
        fake._adam_v = None

        if cognitive_state.model_params:
            for k, v in cognitive_state.model_params.items():
                setattr(fake, k, v)

        if cognitive_state.optimizer_state:
            opt = cognitive_state.optimizer_state
            fake._adam_m = opt.get("m") or opt.get("adam_m")
            fake._adam_v = opt.get("v") or opt.get("adam_v")

        # Varsayılan sürekli parametreler (model_params'ta yoksa sıfır)
        for attr, default in [
            ("givens_angles", np.zeros((120, 1440), np.float32)),
            ("gamma_scales",  np.ones((120, 4),    np.float32)),
            ("qkv_phases",    np.zeros(200,   np.float32)),
            ("G_boundary",    np.zeros(120,   np.float32)),
        ]:
            if not hasattr(fake, attr):
                setattr(fake, attr, default)

        path = self._npz_mgr.save(
            step=step,
            token_offset=metadata.token_offset,
            model=fake,
            loss_history=[metadata.loss] if metadata.loss else [],
        )
        self.current_path = path
        self.metadata = metadata
        self._checkpoint_history.append(path)
        self._cleanup_old_checkpoints()
        return path

    # ---- Yükleme (NPZ önce, pickle fallback) ----
    def load_checkpoint(self,
                        path: Optional[str] = None,
                        step: Optional[int] = None,
                        chunk_index: Optional[int] = None
                        ) -> Tuple[CognitiveState, CheckpointMetadata]:
        # Eski .bin yolu verilmişse NPZ muadilini dene
        if path is not None and path.endswith(".bin"):
            npz_candidate = path.replace(".bin", ".npz")
            if os.path.isfile(npz_candidate):
                path = npz_candidate
            elif os.path.isfile(path):
                return self._load_pickle(path)

        resolved = self._npz_mgr._resolve_path(path, step)
        if resolved is None:
            # Son çare: dizinde pickle .bin ara
            latest_bin = self._find_latest_bin()
            if latest_bin:
                return self._load_pickle(latest_bin)
            raise FileNotFoundError(
                f"Checkpoint bulunamadı: dir={self.checkpoint_dir}"
            )

        d = self._npz_mgr.load(path=resolved)

        # CognitiveState'e dönüştür
        state = CognitiveState(
            model_params={k: d[k] for k in
                          ["theta_spec", "givens_angles", "gamma_scales",
                           "qkv_phases", "G_boundary"]
                          if d.get(k) is not None},
            optimizer_state={
                "m":    d.get("adam_m"),
                "v":    d.get("adam_v"),
                "step": d.get("step", 0),
            },
        )
        meta = CheckpointMetadata(
            version=CHECKPOINT_VERSION,
            step=d["step"],
            token_offset=d["token_offset"],
            timestamp=time.time(),
        )
        self.current_path   = resolved
        self.metadata       = meta
        self.cognitive_state = state
        return state, meta

    def _load_pickle(self, path: str) -> Tuple[CognitiveState, CheckpointMetadata]:
        """Eski pickle .bin formatını okur (geriye uyumluluk)."""
        logger.info(f"  [Ckpt] Eski pickle formatı yükleniyor: {path}")
        with open(path, "rb") as f:
            data = pickle.load(f)
        raw_meta = data.get("metadata", {})
        meta = CheckpointMetadata(
            version=raw_meta.get("version", "1.0.0"),
            timestamp=raw_meta.get("timestamp", 0.0),
            step=raw_meta.get("step", 0),
            chunk_index=raw_meta.get("chunk_index", 0),
            loss=raw_meta.get("loss", 0.0),
            dcm_rank=raw_meta.get("dcm_rank", 0),
            dcm_saturation=raw_meta.get("dcm_saturation", 0.0),
            dcm_synthesis_count=raw_meta.get("dcm_synthesis_count", 0),
            memory_rank=raw_meta.get("memory_rank", 0),
            phase=raw_meta.get("phase", "pretraining"),
            engine_mode=raw_meta.get("engine_mode", "kaggle"),
        )
        cs_raw = data.get("cognitive_state", {})
        state = CognitiveState(
            model_params=self.serializer.deserialize_dict_of_arrays(
                cs_raw.get("model_params", {})
            ),
            topos_state=cs_raw.get("topos_state", {}),
            optimizer_state=cs_raw.get("optimizer_state", {}),
            sheaf_buffer=cs_raw.get("sheaf_buffer", {}),
        )
        self.current_path = path
        self.metadata = meta
        self.cognitive_state = state
        return state, meta

    def _find_latest_bin(self) -> Optional[str]:
        bins = sorted([
            f for f in os.listdir(self.checkpoint_dir)
            if f.endswith(".bin")
        ])
        if bins:
            return os.path.join(self.checkpoint_dir, bins[-1])
        return None

    def _cleanup_old_checkpoints(self) -> None:
        if len(self._checkpoint_history) <= self.keep_last:
            return
        for old in self._checkpoint_history[: -self.keep_last]:
            try:
                if os.path.isfile(old):
                    os.remove(old)
                meta = self._get_metadata_path(old)
                if os.path.isfile(meta):
                    os.remove(meta)
            except OSError:
                pass
        self._checkpoint_history = self._checkpoint_history[-self.keep_last:]

    def list_checkpoints(self) -> List[Dict]:
        return self._npz_mgr.list_checkpoints()

    def get_latest_checkpoint(self) -> Optional[str]:
        return self._npz_mgr.get_latest()

    def verify_checkpoint(self, path: str) -> Dict:
        return self._npz_mgr.verify(path)

    def save_sheaf_restrictions(self, step: int,
                                 sheaf_data: Dict[str, np.ndarray]) -> str:
        sheaf_dir = os.path.join(self.checkpoint_dir, "sheaf_restrictions")
        os.makedirs(sheaf_dir, exist_ok=True)
        path = os.path.join(sheaf_dir, f"sheaf_s{step:06d}.npz")
        np.savez_compressed(path, **{
            k: v.astype(np.float32) if v.dtype not in (np.float16, np.float32, np.float64)
            else v for k, v in sheaf_data.items()
        })
        return path

    def load_sheaf_restrictions(self, path: str) -> Dict[str, np.ndarray]:
        data = np.load(path)
        return {k: data[k] for k in data}


# ===========================================================================
# CHUNK SWITCHER — Korunan Eski Sınıf
# ===========================================================================
class ChunkSwitcher:
    """Korunan eski sınıf — çok-parçalı dataset yönetimi."""

    def __init__(self, total_chunks: int = 26, chunk_size_gb: int = 200,
                 checkpoint_manager: Optional[CheckpointManager] = None):
        self.total_chunks       = total_chunks
        self.chunk_size_gb      = chunk_size_gb
        self.checkpoint_manager = checkpoint_manager
        self.current_chunk      = 0
        self.current_step       = 0
        self.chunk_history: List[Dict] = []

    def next_chunk(self) -> Tuple[int, int, Optional[str]]:
        if self.current_chunk >= self.total_chunks:
            return self.current_chunk, self.current_step, None
        prev = (self.checkpoint_manager.current_path
                if self.current_chunk > 0 and self.checkpoint_manager else None)
        self.current_chunk += 1
        self.chunk_history.append({
            "chunk": self.current_chunk,
            "step":  self.current_step,
            "prev":  prev,
        })
        return self.current_chunk, self.current_step, prev

    def advance_step(self, n: int = 1) -> None:
        self.current_step += n

    def get_progress(self) -> Dict:
        return {
            "current_chunk":  self.current_chunk,
            "total_chunks":   self.total_chunks,
            "current_step":   self.current_step,
            "progress_pct":   round(100.0 * self.current_chunk / self.total_chunks, 1),
            "total_data_gb":  self.total_chunks * self.chunk_size_gb,
        }


# ===========================================================================
# KOLAYLIK FONKSİYONLARI
# ===========================================================================
def create_default_checkpoint_manager(
    checkpoint_dir: str = "checkpoints",
) -> CheckpointManager:
    return CheckpointManager(
        checkpoint_dir=checkpoint_dir,
        keep_last=2,
        precision="float32",
        max_checkpoint_mb=CHECKPOINT_MAX_MB,
    )


def create_npz_manager(
    checkpoint_dir: str = "/kaggle/working",
) -> NPZCheckpointManager:
    return NPZCheckpointManager(
        checkpoint_dir=checkpoint_dir,
        keep_last=2,
        max_mb=CHECKPOINT_MAX_MB,
    )