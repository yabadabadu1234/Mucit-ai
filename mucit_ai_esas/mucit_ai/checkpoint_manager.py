#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHECKPOINT_MANAGER — NPZ Tabanlı Mucit AI Model Durum Yöneticisi
=============================================================================
Bu modül, Mucit AI Bilişsel Kanvas model durumunu, PyTorch ağırlıklarını (N1-N16),
SMW Biyortogonal Bellek matrislerini (M ve R) ve optimizer durumunu
sıkıştırılmış NPZ ve .pt formatlarında atomik biçimde kaydeder ve yükler.

Temel Tasarım Kararları:
  - Format: numpy.savez_compressed (.npz) ve PyTorch (.pt)
  - Boyut garantisi: ≤ 300.6 MB (ağırlıklar gerektiğinde FP16'ya dönüştürülür)
  - Token offset: int64 indeks olarak kaydedilir
  - Metadata: JSON sidecar dosyasına yazılır
=============================================================================
"""

import json
import logging
import os
import pickle
import time
from dataclasses import dataclass, field
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


def _tensor_to_numpy_safe(tensor: Any) -> np.ndarray:
    """
    DÜZELTME (KUSUR 1): `tensor.detach().cpu().numpy()` çağrısı bfloat16 dtype'lı
    tensörlerde NumPy'nin bfloat16'yı doğrudan desteklememesi nedeniyle
    `TypeError: Got unsupported ScalarType BFloat16` ile patlar. Bu, N1-N16
    modüllerinin state_dict()'i (save/save_pytorch_model) her çağrıldığında —
    gradyan projeksiyonu (kontratlar.py) bellek tasarrufu için bfloat16
    kullandığından bazı parametre/tampon tensörleri bu dtype'ta olabilir —
    checkpoint kaydını tamamen çökertebilirdi. Artık bfloat16 tensörler NumPy'ye
    aktarılmadan önce float32'ye yükseltiliyor; diğer dtype'lar etkilenmiyor.
    """
    if torch is not None and hasattr(tensor, "dtype") and tensor.dtype == torch.bfloat16:
        tensor = tensor.to(torch.float32)
    return tensor.detach().cpu().numpy()


# ===========================================================================
# SABİTLER
# ===========================================================================
CHECKPOINT_MAX_MB: float = 300.6
CHECKPOINT_VERSION: str = "3.0.0-MUCIT-AI"


# ===========================================================================
# VERİ YAPILARI
# ===========================================================================
@dataclass
class CheckpointMetadata:
    version: str = CHECKPOINT_VERSION
    timestamp: float = 0.0
    step: int = 0
    token_offset: int = 0
    last_loss: float = 0.0
    hiyerarsik_hafiza: Optional[Dict] = None


@dataclass
class CognitiveState:
    """
    Mucit AI Bilişsel Model Durum Container'ı.
    """
    model_params: Optional[Dict] = None
    smw_M_matrix: Optional[np.ndarray] = None
    smw_R_matrix: Optional[np.ndarray] = None
    optimizer_state: Optional[Dict] = None
    hiyerarsik_hafiza: Optional[Dict] = None


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
        
        if tum_klasor_dosyalari and len(tum_klasor_dosyalari) > 0:
            all_files_done = all(os.path.normpath(f) in self.biten_dosyalar for f in tum_klasor_dosyalari)
            if all_files_done:
                self.biten_klasorler.add(norm_folder)
                for f in tum_klasor_dosyalari:
                    self.biten_dosyalar.discard(os.path.normpath(f))
                logger.info(f"  [Hafıza] Klasördeki TÜM dosyalar tamamlandı! Klasör seviyesine yükseltildi: {norm_folder}")
                
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
    Mucit AI için NPZ ve PyTorch tabanlı checkpoint yöneticisi.
    """

    def __init__(self,
                 checkpoint_dir: str = "/kaggle/working",
                 keep_last: int = 2,
                 max_mb: float = CHECKPOINT_MAX_MB):
        # 1026 GB /tmp NVMe Yönlendirmesi: Kaggle 19.5 GB kotasını doldurmamak için /tmp/kulli_checkpoints tercih edilir
        if checkpoint_dir == "/kaggle/working" and os.path.exists("/tmp"):
            target_dir = "/tmp/kulli_checkpoints"
        else:
            target_dir = checkpoint_dir

        self.checkpoint_dir = target_dir
        self.keep_last      = keep_last
        self.max_mb         = max_mb
        self.hafiza         = HiyerarşikHafizaYoneticisi()
        self._history: List[str] = []
        import threading
        self._save_lock     = threading.Lock()
        os.makedirs(self.checkpoint_dir, exist_ok=True)

    def _hafiza_state_path(self) -> str:
        return os.path.join(self.checkpoint_dir, "hafiza_state.json")

    def save_hafiza_state(self) -> str:
        """
        Hiyerarşik hafıza takibini anlık ve atomik JSON olarak kaydeder.
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
        """
        candidate_paths = [
            self._hafiza_state_path(),
            "/tmp/kulli_checkpoints/hafiza_state.json",
            "/kaggle/working/hafiza_state.json",
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
        Gereksiz geçici ve yetim dosyaları diskten temizler.
        """
        if not os.path.isdir(self.checkpoint_dir):
            return
        purged_count = 0
        for fname in os.listdir(self.checkpoint_dir):
            fpath = os.path.join(self.checkpoint_dir, fname)

            if os.path.isdir(fpath):
                continue

            # KAPSAMLI DENETİM (madde 24): Gerçek geçici dosya adları
            # `topolojik_model_{tag}_tmp_{uuid_hex}.pt` / `checkpoint_{tag}_tmp_{uuid_hex}.npz`
            # biçimindedir (alt çizgi + hex, NOKTA değil) — önceki `"_tmp." in fname` deseni
            # bunların HİÇBİRİYLE eşleşmiyordu. Arka plan kaydı çöken bir süreç (Kaggle
            # oturum zaman aşımı, OOM-kill) tarafından yarıda kesilirse bu yüzlerce MB'lık
            # yetim dosyalar hiç temizlenmeden birikip disk kotasını (bu fonksiyonun kendi
            # amacı) sessizce tüketiyordu.
            is_tmp_file = fname.endswith(".tmp") or "_tmp." in fname or "_tmp_" in fname
            is_dynamic_pt = (fname.startswith("topolojik_model_step_") or fname.startswith("topolojik_model_epoch_")) and fname.endswith(".pt")
            is_dynamic_npz = fname.startswith("checkpoint_") and fname.endswith(".npz") and not (fname.startswith("checkpoint_latest") or fname.startswith("checkpoint_best"))
            is_dynamic_meta = fname.startswith("checkpoint_") and fname.endswith("_meta.json") and not (fname.startswith("checkpoint_latest") or fname.startswith("checkpoint_best"))

            if is_tmp_file or is_dynamic_pt or is_dynamic_npz or is_dynamic_meta:
                try:
                    os.remove(fpath)
                    purged_count += 1
                except OSError as exc:
                    logger.warning(f"  [Purge] Dosya silinemedi: {fpath} ({exc})")

        if purged_count > 0:
            logger.info(f"  [Purge] {purged_count} adet eski geçici/yetim checkpoint dosyası temizlendi.")

    def _npz_path(self, step: int, is_best: bool = False) -> str:
        tag = "best" if is_best else "latest"
        return os.path.join(self.checkpoint_dir, f"checkpoint_{tag}.npz")

    def _meta_path(self, npz_path: str) -> str:
        return npz_path.replace(".npz", "_meta.json")

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
        BiliselStateNPZPaketle (Algoritma 1):
        Hakiki PyTorch model ağırlıklarını, SMW Biyortogonal Bellek matrislerini (M ve R),
        ve optimizer durumunu atomik NPZ olarak kaydeder.
        """
        payload: Dict[str, np.ndarray] = {}

        # 1. Hakiki PyTorch Ağırlıklarının Toplanması (N1-N16 Modülleri)
        if torch is not None and hasattr(model, "state_dict"):
            try:
                sd = model.state_dict()
                for param_adi, tensor in sd.items():
                    if hasattr(tensor, "detach"):
                        payload[f"param_{param_adi}"] = _tensor_to_numpy_safe(tensor)
            except Exception as e:
                logger.debug(f"state_dict okuma uyarısı: {e}")
        elif isinstance(model, dict):
            for mod_name, mod in model.items():
                if torch is not None and hasattr(mod, "state_dict"):
                    for param_adi, tensor in mod.state_dict().items():
                        if hasattr(tensor, "detach"):
                            payload[f"param_{mod_name}.{param_adi}"] = _tensor_to_numpy_safe(tensor)

        # 2. SMW Biyortogonal Bellek Matrislerini Topla (Rükn 5)
        # DÜZELTME (30 hatalık kapsamlı denetim, madde 3): `model`, canlı eğitim yolunda
        # (main_egitim_dongusu.py:save_pytorch_model çağrısı) her zaman bir DICT'tir
        # (tum_moduller, hafıza anahtarı 'bellek') — bir dict'te `.meclis_bellek` niteliği
        # YOKTUR, `getattr(model, "meclis_bellek", None)` bu durumda HER ZAMAN None döner.
        # Sonuç: smw_M_matrix/smw_R_matrix hiçbir zaman NPZ'ye yazılmıyordu (yükleme tarafı
        # zaten ayrıca bozuktu — bkz. load_pytorch_model düzeltmesi). Artık hem dict hem
        # nitelik-tabanlı model temsili destekleniyor.
        if isinstance(model, dict):
            meclis_bellek = model.get("bellek") or model.get("meclis_bellek")
        else:
            meclis_bellek = getattr(model, "meclis_bellek", None)
            if meclis_bellek is None and hasattr(model, "SMW_SifirParazit_BellekYoneticisi"):
                meclis_bellek = getattr(model, "SMW_SifirParazit_BellekYoneticisi", None)

        if meclis_bellek is not None:
            if hasattr(meclis_bellek, "M") and meclis_bellek.M is not None:
                payload["smw_M_matrix"] = meclis_bellek.M.detach().cpu().numpy() if hasattr(meclis_bellek.M, "detach") else np.asarray(meclis_bellek.M)
            if hasattr(meclis_bellek, "R") and meclis_bellek.R is not None:
                payload["smw_R_matrix"] = meclis_bellek.R.detach().cpu().numpy() if hasattr(meclis_bellek.R, "detach") else np.asarray(meclis_bellek.R)

        # 3. AdamW Optimizer Durumu
        if optimizer_m is not None:
            payload["adam_m"] = np.asarray(optimizer_m, dtype=np.float32)
        elif hasattr(model, "_adam_m") and model._adam_m is not None:
            payload["adam_m"] = np.asarray(model._adam_m, dtype=np.float32)

        if optimizer_v is not None:
            payload["adam_v"] = np.asarray(optimizer_v, dtype=np.float32)
        elif hasattr(model, "_adam_v") and model._adam_v is not None:
            payload["adam_v"] = np.asarray(model._adam_v, dtype=np.float32)

        # 4. Step, Token Offset ve Loss History Bilgileri
        payload["step"] = np.array([step], dtype=np.int64)
        payload["token_offset"] = np.array([token_offset], dtype=np.int64)
        hist = loss_history or []
        payload["loss_history"] = np.array(hist[-100:], dtype=np.float32)

        # Ek alanlar
        if extra:
            for k, v in extra.items():
                payload[k] = np.asarray(v)

        # 5. VRAM Muhafızı (Algoritma 2)
        try:
            if torch is not None and torch.cuda.is_available():
                allocated = torch.cuda.memory_allocated()
                total = torch.cuda.get_device_properties(0).total_memory
                free = total - allocated
                free_pct = (free / total) * 100.0 if total > 0 else 100.0
                free_mb = free / (1024 * 1024)
                if free_pct < 15.0 or free_mb < 4096.0:
                    logger.warning(
                        f"  [Ckpt VRAM Guard] VRAM Muhafızı: Boş VRAM Kritik Eşikte (%{free_pct:.1f}, {free_mb:.1f} MB)! "
                        f"Ağırlıklar FP16'ya sıkıştırılıyor..."
                    )
                    for k, v in payload.items():
                        if isinstance(v, np.ndarray) and v.dtype == np.float32:
                            payload[k] = v.astype(np.float16)
        except Exception as vram_exc:
            logger.debug(f"[Checkpoint VRAM Guard Warning] {vram_exc}")

        # 6. Dosyaya Atomik Yazma (tmp -> replace)
        # KAPSAMLI DENETİM (madde 10): ÖNCEDEN sabit bir geçici dosya adı (`_tmp.npz`)
        # kullanılıyordu ve hiçbir kilitle korunmuyordu — save_pytorch_model'in .pt
        # yazımı (bkz. _bg_save_worker) hem benzersiz bir UUID'li ad hem de
        # self._save_lock kullanırken bu NPZ yazımı ikisinden de yoksundu. Eşzamanlı/
        # üst üste binen çağrılarda (ör. yavaş NVMe I/O altında bir önceki yazım
        # bitmeden yenisi tetiklenirse) iki yazıcı aynı geçici dosyayı hedefleyip
        # birbirinin verisini bozabilir veya os.replace() yarım yazılmış bir dosyayı
        # "atomik" diye tanıtabilirdi. Artık benzersiz UUID'li ad + aynı kilit
        # (self._save_lock) kullanılıyor.
        import uuid as _uuid
        out_path = self._npz_path(step, is_best=is_best)
        tmp_path = out_path.replace(".npz", f"_tmp_{_uuid.uuid4().hex}.npz")

        # DÜZELTME (16 hatalık ikinci denetim, madde 15): NVMe takas dosyaları
        # (/tmp/kulli_scratchpad) diski doldurmuş olabileceği hâlde bu hiç kontrol
        # edilmiyordu — disk gerçekten dolduğunda np.savez_compressed/os.replace
        # "No space left on device" ile patlıyor ve tüm eğitim çöküyordu. Artık
        # yazımdan önce hedef dizindeki boş disk alanı ölçülüyor; kritik eşiğin
        # altındaysa (checkpoint boyutunun ~3 katından az boş alan) NVMe takas
        # yöneticisinin agresif süpürmesi TETİKLENİYOR, eğitim çökertilmiyor.
        try:
            import shutil as _shutil
            _disk = _shutil.disk_usage(self.checkpoint_dir)
            _bos_mb = _disk.free / (1024 * 1024)
            if _bos_mb < (self.max_mb * 3.0):
                logger.warning(
                    f"  [Ckpt Disk Guard] Boş disk alanı kritik ({_bos_mb:.1f} MB) — "
                    "NVMe takas dosyaları süpürülüyor..."
                )
                # checkpoint_manager.py bir NvmeTakasYoneticisi örneğine referans tutmaz
                # (bağımsız modül); bilinen takas dizinini doğrudan süpürüyoruz.
                try:
                    from kulli_gpu.nvme_takas_yoneticisi import GuvenliVramVeTmpSupurgesi
                    GuvenliVramVeTmpSupurgesi.supur(swap_dir="/tmp/kulli_scratchpad", eskime_esigi_sn=0.0)
                except Exception as _supur_exc:
                    logger.warning(f"  [Ckpt Disk Guard] Süpürme denemesi başarısız: {_supur_exc}")
        except Exception as _disk_exc:
            logger.debug(f"[Ckpt Disk Guard] Disk alanı kontrol edilemedi: {_disk_exc}")

        with self._save_lock:
            np.savez_compressed(tmp_path, **payload)

            # 7. 300.6 MB Boyut Garantisi
            size_mb = os.path.getsize(tmp_path) / (1024 * 1024)
            if size_mb > self.max_mb:
                logger.warning(
                    f"  [Ckpt] Boyut {size_mb:.1f} MB > {self.max_mb} MB — "
                    f"Float32 matrisler FP16'ya dönüştürülüyor..."
                )
                for k, v in payload.items():
                    if isinstance(v, np.ndarray) and v.dtype == np.float32:
                        payload[k] = v.astype(np.float16)
                np.savez_compressed(tmp_path, **payload)
                size_mb = os.path.getsize(tmp_path) / (1024 * 1024)

            os.replace(tmp_path, out_path)

        # 8. JSON Sidecar Metadata (Algoritma 3)
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
        """
        extra_weights: Dict[str, np.ndarray] = {}
        
        if torch is not None:
            if hasattr(model, 'state_dict'):
                for k, v in model.state_dict().items():
                    extra_weights[f"param_{k}"] = _tensor_to_numpy_safe(v)
            elif isinstance(model, dict):
                for mod_name, mod in model.items():
                    if hasattr(mod, 'state_dict'):
                        for k, v in mod.state_dict().items():
                            extra_weights[f"param_{mod_name}.{k}"] = _tensor_to_numpy_safe(v)

        npz_path = self.save(
            step=step,
            token_offset=token_offset,
            model=model,
            loss_history=loss_history,
            extra=extra_weights,
            is_best=is_best
        )

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

            # KAPSAMLI DENETİM (madde 23): ÖNCEDEN save_pytorch_model() her çağrıldığında
            # KOŞULSUZ yeni bir arka plan thread'i başlatılıyordu. Bu fonksiyon önceki
            # yazım (self._save_lock ile korunan torch.save+os.replace) bitmeden daha sık
            # çağrılırsa (ör. yavaş NVMe I/O altında), thread'ler kilit arkasında sınırsızca
            # kuyruğa giriyordu — hiçbir üst sınır, hiçbir join yoktu. Artık bir önceki
            # arka plan kaydı hâlâ sürüyorsa (kilit meşgulse) yeni bir thread BAŞLATILMIYOR;
            # bu adımın en güncel durumu bir SONRAKİ periyodik save_pytorch_model
            # çağrısında zaten kaydedilecektir (checkpoint'ler periyodik/en-iyi-kayıp
            # tetiklemeli olduğundan bir turun atlanması veri kaybı değildir).
            if self._save_lock.locked():
                logger.warning(
                    "  [Ckpt Mgr] Önceki arka plan .pt kaydı hâlâ sürüyor — bu turun "
                    "kaydı atlanıyor (bir sonraki çağrıda güncel durum kaydedilecek)."
                )
                return npz_path

            def _to_cpu_async(obj: Any) -> Any:
                if isinstance(obj, dict):
                    return {k: _to_cpu_async(v) for k, v in obj.items()}
                elif hasattr(obj, 'detach') and hasattr(obj, 'to'):
                    try:
                        return obj.detach().clone().to('cpu', non_blocking=False)
                    except Exception as exc:
                        # DÜZELTME (madde 30): Önceden `.detach().clone().to('cpu')`
                        # başarısız olursa orijinal CANLI tensör (hâlâ GPU'da, hâlâ
                        # autograd grafiğine bağlı, hâlâ ana eğitim döngüsü tarafından
                        # yerinde mutasyona uğrayabilir) olduğu gibi döndürülüyordu.
                        # Bu nesne arka plan _bg_save_worker thread'ine geçiyordu — ana
                        # eğitim thread'i bir sonraki adımda aynı tensörü in-place
                        # güncellerken (ör. optimizer.step()) arka plan thread'i onu
                        # torch.save ile diske yazabilir, bu da checkpoint'e yarı
                        # güncellenmiş/tutarsız veri yazılmasına (torn write) yol
                        # açabilirdi. Artık canlı referans asla arka plana sızdırılmıyor:
                        # en azından senkron .cpu() denenir; o da başarısız olursa bu
                        # tensör None ile değiştirilip uyarı loglanır (checkpoint'te o
                        # alan eksik kalır ama bozuk/yarışan veri yazılmaz).
                        try:
                            return obj.detach().cpu().clone()
                        except Exception:
                            logger.warning(
                                f"  [Ckpt Mgr] Tensör CPU'ya kopyalanamadı ({exc}), "
                                "canlı GPU referansı arka plan kaydına SIZDIRILMIYOR — alan atlanıyor."
                            )
                            return None
                return obj

            state_dict_cpu = _to_cpu_async(state_dict_to_save)

            def _bg_save_worker(sd: Dict[str, Any], tmp_p: str, final_p: str, lock: Any):
                with lock:
                    try:
                        torch.save(sd, tmp_p)
                        os.replace(tmp_p, final_p)
                        logger.info(f"  [Ckpt Mgr] Sabit PyTorch Kontrol Noktası (.pt) Kaydedildi: {final_p}")
                    except Exception as ex:
                        logger.warning(f"  [Ckpt Mgr] Arka plan checkpoint kaydı hatası: {ex}")

            threading.Thread(target=_bg_save_worker, args=(state_dict_cpu, pt_tmp, pt_path, self._save_lock), daemon=True).start()
            
        return npz_path

    def final_model_kopyala_kaggle_working(self, is_best: bool = True) -> bool:
        """
        Eğitim bittiğinde /tmp/kulli_checkpoints altındaki en iyi model ve metadata dosyalarını
        Kaggle persistent dizinine (/kaggle/working) kopyalar.
        """
        if not os.path.exists("/kaggle/working"):
            return False
        import shutil
        tag = "best" if is_best else "latest"
        sources = [
            os.path.join(self.checkpoint_dir, f"checkpoint_{tag}.npz"),
            os.path.join(self.checkpoint_dir, f"checkpoint_{tag}_meta.json"),
            os.path.join(self.checkpoint_dir, f"topolojik_model_{tag}.pt"),
            self._hafiza_state_path()
        ]
        copied_any = False
        for src in sources:
            if os.path.isfile(src):
                dst = os.path.join("/kaggle/working", os.path.basename(src))
                try:
                    shutil.copy2(src, dst)
                    logger.info(f"  [Final Kopyalama] {src} -> {dst}")
                    copied_any = True
                except Exception as e:
                    logger.warning(f"  [Final Kopyalama Hatası] {src}: {e}")
        return copied_any

    def load_pytorch_model(self,
                           model: Any,
                           optimizer: Optional[Any] = None,
                           path: Optional[str] = None,
                           step: Optional[int] = None) -> Tuple[int, List[float]]:
        """
        NPZ veya .pt kontrol noktasından PyTorch model, optimizer ve hiyerarşik hafızayı yükler.
        """
        self.load_hafiza_state()

        resolved = self._resolve_path(path, step)

        # DÜZELTME (30 hatalık kapsamlı denetim, madde 3): SMW Biyortogonal Bellek
        # matrisleri (M/R) NPZ'ye yazılıyordu (bkz. save() düzeltmesi) ama bu fonksiyon
        # onları HİÇBİR ZAMAN GERİ OKUMUYORDU — ne .pt başarı yolunda (satırın altında,
        # step/loss alıp erken return ediyordu) ne NPZ-fallback yolunda. Her resume'da
        # saatlerce eğitilmiş hafıza sessizce taze/sıfır durumuna dönüyordu, hiçbir hata
        # veya uyarı olmadan. Artık ağırlık kaynağı (.pt/.npz) ne olursa olsun, M/R
        # NPZ'den okunup modelin meclis_bellek'ine (varsa) AÇIKÇA geri yazılıyor.
        if resolved is not None:
            try:
                _hafiza_data = self.load(path=resolved)
                _smw_M = _hafiza_data.get("smw_M_matrix")
                _smw_R = _hafiza_data.get("smw_R_matrix")
                if _smw_M is not None or _smw_R is not None:
                    _meclis_bellek = model.get("bellek") if isinstance(model, dict) else getattr(model, "meclis_bellek", None)
                    if _meclis_bellek is not None:
                        if _smw_M is not None and hasattr(_meclis_bellek, "M"):
                            _hedef_M = _meclis_bellek.M
                            if torch is not None and hasattr(_hedef_M, "device"):
                                _meclis_bellek.M = torch.as_tensor(_smw_M, dtype=_hedef_M.dtype, device=_hedef_M.device)
                            else:
                                _meclis_bellek.M = _smw_M
                        if _smw_R is not None and hasattr(_meclis_bellek, "R"):
                            _hedef_R = _meclis_bellek.R
                            if torch is not None and hasattr(_hedef_R, "device"):
                                _meclis_bellek.R = torch.as_tensor(_smw_R, dtype=_hedef_R.dtype, device=_hedef_R.device)
                            else:
                                _meclis_bellek.R = _smw_R
                        logger.info("  [Ckpt Mgr] SMW Biyortogonal Bellek (M/R) matrisleri geri yüklendi.")
                    else:
                        logger.warning("  [Ckpt Mgr] Checkpoint'te SMW M/R verisi var ama model'de meclis_bellek bulunamadı, atlandı.")
            except Exception as exc:
                logger.warning(f"  [Ckpt Mgr] SMW Bellek (M/R) geri yükleme uyarısı: {exc}")

        pt_candidates = []
        if path and path.endswith(".pt") and os.path.isfile(path):
            pt_candidates.append(path)
        pt_candidates.append(os.path.join(self.checkpoint_dir, "topolojik_model_best.pt"))
        pt_candidates.append(os.path.join(self.checkpoint_dir, "topolojik_model_latest.pt"))
        pt_candidates.append("/tmp/kulli_checkpoints/topolojik_model_best.pt")
        pt_candidates.append("/tmp/kulli_checkpoints/topolojik_model_latest.pt")
        pt_candidates.append("/kaggle/working/topolojik_model_best.pt")
        pt_candidates.append("/kaggle/working/topolojik_model_latest.pt")
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
            # DÜZELTME (madde 26): Eskiden torch.load() VE state_dict uygulaması AYNI
            # try/except Exception bloğundaydı. Eğer bazı modüller (mod_obj) BAŞARIYLA
            # state_dict yüklüyor, sonraki bir modül hata veriyorsa, except bloğu
            # bunu ".pt yok/bozuk, npz'ye geç" ile aynı şekilde ele alıyordu — halbuki
            # model artık YARI-YÜKLENMİŞ (bazı modüller .pt'den, bazıları ilklenmiş
            # durumda) karışık bir haldeydi ve npz fallback ağırlıkları HİÇ yüklemediği
            # için bu tutarsız durum sessizce eğitime/çıkarsamaya devam ediyordu.
            # Artık torch.load() (dosya okuma/bozukluk) ayrı, state_dict uygulaması
            # (kısmi durum riski) ayrı ele alınıyor: ikincisi başarısız olursa npz'ye
            # sessizce düşülmüyor, hata açıkça yükseltiliyor.
            try:
                checkpoint = torch.load(pt_file, map_location="cpu")
            except Exception as load_exc:
                logger.warning(f"  [Ckpt Mgr] .pt dosyası okunamadı ({load_exc}), .npz yüklemesine geçiliyor.")
                checkpoint = None

            if checkpoint is not None:
              try:
                import re
                if 'model' in checkpoint:
                    st = checkpoint['model']

                    if isinstance(model, dict):
                        # Model bir modül sözlüğü: her modülü ayrı ayrı yükle
                        for mod_key, mod_obj in model.items():
                            if not hasattr(mod_obj, 'load_state_dict'):
                                continue

                            # İç içe sözlükten modüle ait alt sözlüğü çek
                            if isinstance(st, dict) and mod_key in st:
                                mod_st_raw = st[mod_key]
                            else:
                                # Düzleştirilmiş sözlükten filtrele
                                flat_st = _flatten_nested_state_dict(st) if isinstance(st, dict) else st
                                mod_st_raw = {
                                    k[len(mod_key)+1:]: v
                                    for k, v in flat_st.items()
                                    if isinstance(k, str) and k.startswith(f"{mod_key}.")
                                }

                            if not mod_st_raw:
                                logger.warning(f"  [Ckpt Mgr] '{mod_key}' için checkpoint verisi bulunamadı, atlandı.")
                                continue

                            # DDP / sarmalayıcı prefix temizliği
                            temiz_st = {}
                            for k, v in mod_st_raw.items():
                                yeni_k = re.sub(r'^(module\.|model\.|modeller\.)', '', str(k))
                                temiz_st[yeni_k] = v

                            # strict=True ile yükle; hata olursa strict=False ile fallback
                            try:
                                mod_obj.load_state_dict(temiz_st, strict=True)
                                logger.info(f"  [Ckpt Mgr] '{mod_key}' strict=True ile yüklendi.")
                            except RuntimeError as strict_err:
                                logger.warning(f"  [Ckpt Mgr] '{mod_key}' strict=True başarısız ({strict_err}), strict=False deneniyor.")
                                mod_obj.load_state_dict(temiz_st, strict=False)

                    elif hasattr(model, 'load_state_dict'):
                        flat_st = _flatten_nested_state_dict(st) if isinstance(st, dict) else st
                        # DDP prefix temizliği
                        temiz_st = {re.sub(r'^(module\.|model\.|modeller\.)', '', str(k)): v for k, v in flat_st.items()}
                        try:
                            model.load_state_dict(temiz_st, strict=True)
                        except RuntimeError as strict_err:
                            logger.warning(f"  [Ckpt Mgr] strict=True başarısız ({strict_err}), strict=False ile devam.")
                            model.load_state_dict(temiz_st, strict=False)

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
                # NPZ'ye DÜŞÜLMÜYOR: bu noktaya gelindiyse torch.load() zaten başarılıydı
                # ve bazı modüllerin state_dict'i muhtemelen ZATEN uygulanmış olabilir.
                # Sessizce npz fallback'e geçmek modeli yarı-yüklenmiş bırakıp bunu
                # gizlerdi. Hata açıkça yükseltiliyor ki çağıran taraf gerçek durumu görsün.
                logger.error(f"  [Ckpt Mgr] .pt state_dict uygulama hatası ({exc}) — model YARI-YÜKLENMİŞ olabilir, npz'ye sessizce düşülmüyor.")
                raise

        if resolved is None:
            logger.warning(f"  [Ckpt Mgr] Yüklenecek kontrol noktası bulunamadı.")
            return 0, []

        ckpt_data = self.load(path=resolved)
        step_ret = ckpt_data.get("step", 0)
        loss_ret = ckpt_data.get("loss_history", [])
        return step_ret, loss_ret

    def _write_meta(self, npz_path: str, step: int, token_offset: int,
                    size_mb: float, loss_history: Optional[List[float]]) -> None:
        """
        BiliselMetadataOlustur (Algoritma 3):
        Hakiki Mucit AI Metadata Yapısı.
        """
        meta = {
            "versiyon":          CHECKPOINT_VERSION,
            "zaman_damgasi":     time.time(),
            "step":              step,
            "token_offset":      token_offset,
            "size_mb":           round(size_mb, 2),
            "son_kayip":         float(loss_history[-1]) if loss_history else 0.0,
            "hiyerarsik_hafiza": self.hafiza.to_dict()
        }
        meta_path = self._meta_path(npz_path)
        # DÜZELTME (KUSUR 5): Meta JSON, esas .npz/.pt dosyalarının aksine (tmp+os.replace
        # ile atomik yazılıyor) doğrudan open(meta_path, "w") ile üzerine yazılıyordu.
        # Yazma sırasında süreç kesilirse (OOM-kill, Kaggle oturum zaman aşımı) yarım
        # yazılmış/bozuk bir JSON dosyası kalır; sonraki load()/list_checkpoints() çağrıları
        # bunu sessizce atlar (json.JSONDecodeError yakalanıyor) ama step/hiyerarşik hafıza
        # bilgisi kaybolur. Artık aynı UUID'li tmp + os.replace deseni kullanılıyor.
        import uuid as _uuid_meta
        meta_tmp = meta_path + f".tmp_{_uuid_meta.uuid4().hex}"
        try:
            with open(meta_tmp, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2, ensure_ascii=False)
            os.replace(meta_tmp, meta_path)
        except OSError as exc:
            logger.warning(f"  [Ckpt] Meta yazılamadı: {exc}")
            try:
                if os.path.isfile(meta_tmp):
                    os.remove(meta_tmp)
            except OSError:
                pass

    def load(self, path: Optional[str] = None,
             step: Optional[int] = None) -> Dict[str, Any]:
        resolved = self._resolve_path(path, step)
        if resolved is None:
            raise FileNotFoundError(
                f"Checkpoint bulunamadı: dir={self.checkpoint_dir} "
                f"path={path} step={step}"
            )

        # KAPSAMLI DENETİM (madde 22): np.load() bir NpzFile döndürür — bu, açık bir zip
        # dosya tanıtıcısını (fd) sarmalar; önceden ne `with` ne `.close()` çağrılıyordu.
        # load() her checkpoint resume'da ve verify()/list_checkpoints() gibi periyodik
        # izleme çağrılarında tekrar tekrar çağrıldığından, fd'ler işletim sistemi
        # limitine kadar birikip sonraki dosya açmalarının (bir sonraki checkpoint
        # kaydı dahil) "Too many open files" ile başarısız olmasına yol açabilirdi.
        # `with` bloğu içinde indekslenen diziler (data["..."]) zaten tam bellek içi
        # kopyalardır, bloktan çıkıldıktan sonra da güvenle kullanılabilir.
        with np.load(resolved, allow_pickle=False) as data:
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
                # DÜZELTME (madde 27): save() VRAM/boyut baskısı altında payload'daki
                # TÜM float32 dizileri (smw_M_matrix/smw_R_matrix/param_* dahil) FP16'ya
                # sıkıştırabiliyordu (bkz. satır ~348, ~377), ama load() yalnızca
                # adam_m/adam_v'yi geri float32'ye yükseltiyordu. Sonuç: SMW Biyortogonal
                # Bellek matrisleri ve model ağırlıkları FP16 hassasiyetiyle sessizce
                # geri yükleniyor, ardından FP32 tensörlerle karıştırıldığında dtype
                # uyuşmazlığı hatalarına veya sessiz hassasiyet kaybına yol açıyordu.
                # Artık hepsi tutarlı biçimde float32'ye yükseltiliyor.
                "smw_M_matrix":      data["smw_M_matrix"].astype(np.float32) if "smw_M_matrix" in data else None,
                "smw_R_matrix":      data["smw_R_matrix"].astype(np.float32) if "smw_R_matrix" in data else None,
                "adam_m":            data["adam_m"].astype(np.float32) if "adam_m" in data else None,
                "adam_v":            data["adam_v"].astype(np.float32) if "adam_v" in data else None,
                "hiyerarsik_hafiza": self.hafiza.to_dict(),
                "model_params":      {
                    k[6:]: (data[k].astype(np.float32) if np.issubdtype(data[k].dtype, np.floating) else data[k])
                    for k in data.files if k.startswith("param_")
                }
            }

        logger.info(
            f"  [Ckpt] Yüklendi: {resolved} | "
            f"step={result['step']} | "
            f"token_offset={result['token_offset']:,}"
        )
        return result

    def _resolve_path(self, path: Optional[str],
                      step: Optional[int]) -> Optional[str]:
        if path is not None and os.path.isfile(path):
            return path
        if step is not None:
            # DÜZELTME (madde 28): _npz_path(step) parametresini SESSİZCE görmezden
            # gelip her zaman "checkpoint_latest.npz" döndürüyordu (bu depolama şeması
            # yalnızca latest/best adında iki dönen dosya tutuyor, step-bazlı ayrı
            # dosyalar hiç yazılmıyor). os.path.isfile(p) çoğu zaman True dönerdi
            # (çünkü checkpoint_latest.npz genelde vardır) — böylece çağıran taraf
            # BELİRLİ bir step'i istediğinde, o step'e ait olmayan (örn. daha sonraki)
            # bir checkpoint'i sessizce, hatasız biçimde geri alırdı. Artık adayın
            # meta dosyasındaki gerçek step değeri istenenle karşılaştırılıyor;
            # eşleşmezse bu yol kullanılmıyor ve normal fallback'e devam ediliyor.
            p = self._npz_path(step)
            if os.path.isfile(p):
                meta_path = self._meta_path(p)
                kayitli_step = None
                if os.path.isfile(meta_path):
                    try:
                        with open(meta_path, "r", encoding="utf-8") as f:
                            kayitli_step = json.load(f).get("step")
                    except Exception:
                        kayitli_step = None
                if kayitli_step == step:
                    return p
                logger.debug(
                    f"  [Ckpt] step={step} istendi ama {p} dosyasının kayıtlı "
                    f"step'i {kayitli_step} — eşleşmiyor, normal aramaya devam ediliyor."
                )
        if self._history:
            return self._history[-1]
        return self.get_latest()

    def get_latest(self) -> Optional[str]:
        if not os.path.isdir(self.checkpoint_dir):
            return None
        
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
        if not os.path.isdir(self.checkpoint_dir):
            return []
        results = []
        for fname in sorted(os.listdir(self.checkpoint_dir)):
            if not (fname.startswith("checkpoint_") and fname.endswith(".npz")):
                continue
            fpath    = os.path.join(self.checkpoint_dir, fname)
            size_mb  = os.path.getsize(fpath) / (1024 * 1024)
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
        result: Dict = {"valid": False, "errors": [], "size_mb": 0.0}
        if not os.path.isfile(path):
            result["errors"].append("Dosya bulunamadı")
            return result
        result["size_mb"] = round(os.path.getsize(path) / (1024 * 1024), 2)
        try:
            # KAPSAMLI DENETİM (madde 22): bkz. load()'daki aynı düzeltme — fd sızıntısını
            # önlemek için `with` kullanılıyor.
            with np.load(path, allow_pickle=False) as data:
                required = ["token_offset", "step"]
                for key in required:
                    if key not in data:
                        result["errors"].append(f"Eksik alan: {key}")
                if result["size_mb"] > self.max_mb:
                    result["errors"].append(
                        f"Boyut sınırı aşıldı: {result['size_mb']:.1f} MB > {self.max_mb} MB"
                    )
                # KAPSAMLI DENETİM (madde 25): ÖNCEDEN yalnızca anahtar VARLIĞI ve toplam
                # dosya boyutu kontrol ediliyordu — dizilerin kendisi hiç okunmuyordu
                # (np.load NPZ girdilerini TEMBEL açar, gerçek zlib decompression yalnızca
                # bir dizi indekslendiğinde gerçekleşir). Bozuk bir sıkıştırılmış blok
                # (bit çürümesi, atomik yeniden adlandırma SONRASI oluşan kısmi disk
                # yazımı) "valid": True raporlanıyordu, sonra load() gerçekten o diziye
                # eriştiğinde eğitim çökerdi. Artık her dizi GERÇEKTEN açılıp bütünlüğü
                # doğrulanıyor.
                for key in data.files:
                    try:
                        _ = data[key]  # zlib decompression'ı zorla tetikle
                    except Exception as arr_exc:
                        result["errors"].append(f"Bozuk veri ({key}): {arr_exc}")
                result["valid"] = len(result["errors"]) == 0
                result["keys"]  = list(data.keys())
        except Exception as exc:
            result["errors"].append(str(exc))
        return result


# ===========================================================================
# GERİYE UYUMLU PICKLE VE KATMAN ARAYÜZÜ
# ===========================================================================
class CheckpointSerializer:
    """Korunan serializer — NPZCheckpointManager'a yönlendirir."""

    def __init__(self, precision: str = "float32"):
        self.precision = precision

    def serialize_array(self, arr: np.ndarray) -> bytes:
        return arr.astype(np.float32).tobytes()

    def deserialize_array(self, data: bytes, shape: Tuple[int, ...]) -> np.ndarray:
        return np.frombuffer(data, dtype=np.float32).reshape(shape)


class CheckpointManager:
    """
    Geriye uyumlu ana sınıf. Dahili olarak NPZCheckpointManager'ı çağırır.
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
        self._npz_mgr = NPZCheckpointManager(
            checkpoint_dir=checkpoint_dir,
            keep_last=keep_last,
            max_mb=max_checkpoint_mb,
        )
        os.makedirs(checkpoint_dir, exist_ok=True)

    def save_checkpoint(self,
                        step: int,
                        chunk_index: int,
                        cognitive_state: CognitiveState,
                        metadata: Optional[CheckpointMetadata] = None) -> str:
        if metadata is None:
            metadata = CheckpointMetadata()
        metadata.version   = CHECKPOINT_VERSION
        metadata.timestamp = time.time()
        metadata.step      = step

        fake_model = type("ModelWrapper", (), {})()
        if cognitive_state.model_params:
            for k, v in cognitive_state.model_params.items():
                setattr(fake_model, k, v)

        if cognitive_state.smw_M_matrix is not None or cognitive_state.smw_R_matrix is not None:
            fake_meclis = type("MeclisWrapper", (), {
                "M": cognitive_state.smw_M_matrix,
                "R": cognitive_state.smw_R_matrix
            })()
            setattr(fake_model, "meclis_bellek", fake_meclis)

        opt_m = None
        opt_v = None
        if cognitive_state.optimizer_state:
            opt = cognitive_state.optimizer_state
            opt_m = opt.get("m") or opt.get("adam_m")
            opt_v = opt.get("v") or opt.get("adam_v")

        path = self._npz_mgr.save(
            step=step,
            token_offset=metadata.token_offset,
            model=fake_model,
            optimizer_m=opt_m,
            optimizer_v=opt_v,
            loss_history=[metadata.last_loss] if metadata.last_loss else [],
        )
        self.current_path = path
        self.metadata = metadata
        return path

    def load_checkpoint(self,
                        path: Optional[str] = None,
                        step: Optional[int] = None,
                        chunk_index: Optional[int] = None
                        ) -> Tuple[CognitiveState, CheckpointMetadata]:
        resolved = self._npz_mgr._resolve_path(path, step)
        if resolved is None:
            raise FileNotFoundError(
                f"Checkpoint bulunamadı: dir={self.checkpoint_dir}"
            )

        d = self._npz_mgr.load(path=resolved)

        state = CognitiveState(
            model_params=d.get("model_params"),
            smw_M_matrix=d.get("smw_M_matrix"),
            smw_R_matrix=d.get("smw_R_matrix"),
            optimizer_state={
                "m": d.get("adam_m"),
                "v": d.get("adam_v"),
                "step": d.get("step", 0),
            },
            hiyerarsik_hafiza=d.get("hiyerarsik_hafiza")
        )
        meta = CheckpointMetadata(
            version=CHECKPOINT_VERSION,
            step=d["step"],
            token_offset=d["token_offset"],
            timestamp=time.time(),
        )
        self.current_path = resolved
        self.metadata = meta
        self.cognitive_state = state
        return state, meta


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
