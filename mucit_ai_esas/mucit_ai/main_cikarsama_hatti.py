

import os
import sys


try:
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    CURRENT_DIR = os.path.abspath(os.getcwd())

if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import json
import time
import logging
from typing import Dict, Any, List, Tuple, Optional, Union

import kontratlar
import torch
import torch.nn as nn
import torch.nn.functional as F

from kontratlar import (
    Model_TopolojikKonfigurasyon,
    SistemYapilandirmasi,
    E1_HamMetinAkisi,
    E2_ByteTensoru,
    E3_SinirOperatorleri,
    E4_LifDemeti,
    E5_A_MevcutGizilDurum,
    E5_B_BellekGonderimi,
    E6_GizilSorgu,
    E7_LokalBilgi,
    E8_SentetikAraDurum,
    E9_GuncellenmisGizilDurum,
    E10_KulliManaMatrisi,
    E11_ParalelGomuluVektorlerMatrisi,
    E12_ParalelTokenOlasilikMatrisi,
    E13_HedefTokenDizisi,
    E14_SistemKayipMetrikleri,
    E15_GuncellenmisBellekMatrisi,
    E16_UretilenMetinCiktisi,
    E17_EgitimGradiyantPaketi,
    E18_TopolojiDenetimRaporu,
    N1_ByteAyristirici,
    N2_TopoXHucreOlusumu,
    N3_LifSinirlamaAtama,
    N4_SorguSecici,
    N5_CevapSuzucu,
    N6_KohomolojikAktor,
    N7_LifLaplasyeniCozucu,
    N8_ChebyshevKatsayiProjeksiyon,
    N8_B_DinamikUzunlukSecici,
    N9_ChebyshevVandermondeCarpim,
    N10_SozlukSoftmaxIzdusem,
    N11_LifLaplasyeniBlokInsaEdici,
    N12_BellekBaglamYoneticisi,
    N13_StiefelManifolduIzdusumu,
    N14_OdulTopolojikDevresmezlikMotoru,
    N15_EgitimKontrolNoktasiYoneticisi,
    N16_ArcIzgaraDonusturucu,
    Sheaf_KAN_Superpozisyon_Operatoru,
    SMW_SifirParazit_BellekYoneticisi,
    al_cevrimdisi_veya_tiktoken_tokenizer,
    N4_SorguSecici_AltAg,
    N5_CevapSuzucu_AltAg,
    N6_KohomolojikAktor_AltAg,
    Maarif_NedenselSuzgec,
    Yardimci_ChebyshevMatrisHesaplayici,
    Riyazi_LifLaplasyeniBlokInsaEdici,
    Bellek_BaglamYoneticisi,
    Riyazi_StiefelManifolduIzdusumu,
    BiliselKanvasModeli
)

from logging.handlers import RotatingFileHandler


def kur_logging_sistemi(log_dosyasi: str = 'cikarsama_hatti_icra.log') -> None:
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.handlers.clear()  

    
    fh = RotatingFileHandler(log_dosyasi, maxBytes=10*1024*1024, backupCount=1, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s - [%(levelname)s] - (%(name)s) - %(message)s'))
    root.addHandler(fh)

    
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s'))
    root.addHandler(ch)

kur_logging_sistemi()
logger = logging.getLogger('MainCikarsama')


class Arc_IzgaraDonusturucu:
    def donustur(self, gorev_verisi: Dict[str, Any]) -> str:
        return json.dumps(gorev_verisi.get("train", []))


class Arc_CiktiIzgaraInsaEdici:
    def insa_et(self, olasilik_matrisi: E12_ParalelTokenOlasilikMatrisi, hedef_boyut: Tuple[int, int] = (3, 3)) -> Dict[str, List[List[int]]]:
        
        if getattr(olasilik_matrisi, 'preds_full', None) is not None:
            preds = olasilik_matrisi.preds_full[0].cpu().numpy()  
        else:
            P = olasilik_matrisi.P
            preds = torch.argmax(P, dim=1)[0].cpu().numpy()  

        rows, cols = hedef_boyut
        izgara = []
        idx = 0
        for r in range(rows):
            row = []
            for c in range(cols):
                val = int(preds[idx % len(preds)]) % 10  
                row.append(val)
                idx += 1
            izgara.append(row)
            
        return {
            "attempt_1": izgara,
            "attempt_2": izgara
        }


from checkpoint_manager import NPZCheckpointManager, CheckpointManager

class Model_Agirlik_ve_CikarsamaYoneticisi:
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        self.config = config

    def yukle(self, model_dizini: str, model: BiliselKanvasModeli) -> Tuple[BiliselKanvasModeli, bool]:
        target_dir = model_dizini
        
        priority_paths = [
            model_dizini,
            "/kaggle/input/notebooks/ulankaggle/mucit-ai"
        ]

        has_ckpt = False
        for p in priority_paths:
            if os.path.exists(p) and os.path.isdir(p):
                if any(f.endswith('.pt') or f.endswith('.npz') for f in os.listdir(p) if os.path.isfile(os.path.join(p, f))):
                    target_dir = p
                    has_ckpt = True
                    logger.info(f"  [Öncelikli Yol] Model kontrol noktası dizini bulundu: {target_dir}")
                    break
        
        if not has_ckpt:
            def find_checkpoint_dir(start_dir: str) -> Optional[str]:
                if not os.path.exists(start_dir):
                    return None
                for root, dirs, files in os.walk(start_dir):
                    if any(f.endswith('.pt') or f.endswith('.npz') for f in files):
                        return root
                return None

            logger.info(f"Öncelikli dizinlerde checkpoint bulunamadı. Genel Kaggle dataset yolları taranıyor...")
            found = find_checkpoint_dir("/kaggle/input") or find_checkpoint_dir("./checkpoints") or find_checkpoint_dir("./")
            if found:
                target_dir = found
                logger.info(f"  [Otomatik Tespit] Model kontrol noktası dizini bulundu: {target_dir}")
            else:
                logger.error(f"  [HATA] Hiçbir dizinde kontrol noktası (.pt / .npz) bulunamadı! Rastgele ilklendirilmiş ağırlıklar kullanılacak.")
                return model, False

        npz_mgr = NPZCheckpointManager(checkpoint_dir=target_dir)
        latest_ckpt = npz_mgr.get_latest()






        try:
            step_loaded, _ = npz_mgr.load_pytorch_model(model=model, path=latest_ckpt)
        except Exception as yukleme_hatasi:
            logger.error("=" * 80)
            logger.error(f"MODEL AĞIRLIKLARI YÜKLENEMEDİ: {yukleme_hatasi}")
            logger.error(
                "Çıkarım burada durduruluyor. Rastgele ağırlıklarla üretilen metin "
                "modelin kabiliyeti hakkında hiçbir şey göstermez; 'çalışıyor ama kötü' "
                "ile 'hiç yüklenmedi' birbirine karıştırılmamalıdır."
            )
            logger.error("=" * 80)
            raise

        logger.info(
            f"Model ağırlıkları yüklendi. (Dizin: {target_dir} | Kaydedilen adım: {step_loaded})"
        )
        return model, True


def Main_CikarsamaYurutucu(model_yolu: str = "./checkpoints", test_girdisi: str = "Ahmet eve gitti.") -> str:
    baslangic_zamani = time.time()
    zaman_siniri_saniye = 900.0  
    
    logger.info("================================================================================")
    logger.info("BİLİŞSEL KANVAS TOPOLOJİK REKÜRENS MİMARİSİ ÇIKARSAMA HATTI BAŞLATILIYOR")
    logger.info("================================================================================")

    
    config = Model_TopolojikKonfigurasyon()
    config.device = "cuda:0" if torch.cuda.is_available() else "cpu"
    config.batch_size = 1  
    logger.info(f"Çıkarım Cihazı: {config.device} | Varsayılan Dizi Uzunluğu (N): {config.N} | Azami Kapasite (N_max): {config.N_max} | Zaman Sınırı: {zaman_siniri_saniye} sn")

    
    arc_donusturucu = Arc_IzgaraDonusturucu()
    arc_insa_edici = Arc_CiktiIzgaraInsaEdici()
    agirlik_yonetici = Model_Agirlik_ve_CikarsamaYoneticisi(config)

    model = BiliselKanvasModeli(config).to(config.device)
    model, yuklendi_mi = agirlik_yonetici.yukle(model_yolu, model)

    
    stiefel_izdusurucu = N13_StiefelManifolduIzdusumu()
    
    eval_model = model.module if isinstance(model, nn.DataParallel) else model





    stiefel_izdusurucu.izdüsür(eval_model.n3_lif.phi_base)

    
    is_arc_json = False
    if test_girdisi.endswith('.json') and os.path.exists(test_girdisi):
        is_arc_json = True
        with open(test_girdisi, 'r', encoding='utf-8') as f:
            gorev_verisi = json.load(f)
        girdi_str = arc_donusturucu.donustur(gorev_verisi)
        logger.info(f"ARC-AGI JSON Girdisi İşleniyor: {test_girdisi}")
    else:
        girdi_str = test_girdisi
        logger.info(f"Ham Metin Girdisi İşleniyor: '{test_girdisi}'")

    
    with torch.no_grad():
        gecen_saniye = time.time() - baslangic_zamani
        if gecen_saniye > zaman_siniri_saniye:
            logger.warning(f"Emniyet Zaman Sınırı Aşıldı ({gecen_saniye:.2f}s). İşlem iptal ediliyor.")
            return "{}"

        
        e1_girdi = E1_HamMetinAkisi(X_text=girdi_str)

        
        e2_byte, x_initial = eval_model.n1_byte(e1_girdi)
        logger.debug(f"[N1 Byte Ayrıştırıcı] E2 Byte Tensoru Şekli: {e2_byte.byte_tensor.shape} | İlk Gizil Durum x^(0): {x_initial.shape}")

        
        e3_sinir = eval_model.n2_topox(e2_byte, x_initial=x_initial, mode='eval')
        logger.debug(f"[N2 TopoX Kompleksi] E3 D1 (Sınır 1) Şekli: {e3_sinir.D1.shape} | D2 (Sınır 2) Şekli: {e3_sinir.D2.shape}")

        
        e4_lif = eval_model.n3_lif(e3_sinir, x_initial)
        logger.debug(f"[N3 Sınırlama Matrisi Atama] E4 Lif Matrisleri Sayısı: {len(e4_lif.phi_matrisleri)}")

        
        D0_op, _ = eval_model.laplasyen_insa.insa_et(e3_sinir, e4_lif.phi_matrisleri)
        logger.debug(f"[N_LA Lif Laplasyeni İnşası] E4_B D0 Coboundary: {D0_op.shape}")

        
        x_current = x_initial.clone()




        M_current = eval_model.bellek_yonetici.get_memory(1).M
        eval_model.n6_aktor.update_operators(D0_op)

        for r in range(1, config.R + 1):
            
            e3_sinir = eval_model.n2_topox(e2_byte, x_initial=x_current, mode='eval', D0_base=D0_op)
            D0_op, _ = eval_model.laplasyen_insa.insa_et(e3_sinir, e4_lif.phi_matrisleri)
            eval_model.n6_aktor.update_operators(D0_op)
            
            e5_a = E5_A_MevcutGizilDurum(x_r=x_current)
            e5_b = E5_B_BellekGonderimi(M=M_current)
            
            
            e6_sorgu = eval_model.n4_sorgu(e5_a, D0_operator=D0_op, A_adjacency=e3_sinir.D1, bellek=e5_b)
            logger.debug(f"  ├─ [N4 Sorgu Seçici] (r={r}) Sorgu Vektörü q^({r}) Şekli: {e6_sorgu.q_r.shape}")
            
            
            e7_lokal = eval_model.n5_cevap(e6_sorgu, e5_b)
            logger.debug(f"  ├─ [N5 Cevap Süzücü] (r={r}) Lokal Cevap Vektörü a^({r}) Şekli: {e7_lokal.a_r.shape}")
            
            
            e8_sentetik = eval_model.n6_aktor(e5_a, e6_sorgu, e7_lokal)
            logger.debug(f"  ├─ [N6 Kohomolojik Aktüatör & Sheaf-KAN] (r={r}) Sentetik Hüküm h* Şekli: {e8_sentetik.synthetic_state.shape}")
            
            
            e9_guncel = eval_model.n7_cozucu(e8_sentetik, D0_op, e5_a)
            logger.debug(f"  ├─ [N7 Lif Laplasyeni Çözücü & Green's Kernel] (r={r}) Güncellenmiş Durum x^({r}) Şekli: {e9_guncel.x_next.shape}")
            
            
            if hasattr(eval_model, 'bellek_yonetici') and isinstance(eval_model.bellek_yonetici, SMW_SifirParazit_BellekYoneticisi):
                k_r_key = e6_sorgu.q_r[:, :getattr(config, 'K', 16)] if e6_sorgu.q_r.shape[1] >= getattr(config, 'K', 16) else F.pad(e6_sorgu.q_r, (0, getattr(config, 'K', 16) - e6_sorgu.q_r.shape[1]))
                v_r_val = e7_lokal.a_r
                e5_b_yeni = eval_model.bellek_yonetici.write(k_r=k_r_key, v_r=v_r_val)
            else:
                e5_b_yeni = eval_model.n_yazici.yaz(e9_guncel.x_next, e6_sorgu, e5_b, e7_lokal)
            logger.debug(f"  ├─ [N12 SMW Sıfır Parazitli Bellek] (r={r}) Güncellenmiş Bellek E5_B_YENI Şekli: {e5_b_yeni.M.shape}")

            
            x_current = e9_guncel.x_next.detach()
            M_current = e5_b_yeni.M.detach()

            d_disc_r = eval_model.n7_cozucu.hesapla_uyumsuzluk(x_current, D0_op)
            dirichlet_r = eval_model.n7_cozucu.hesapla_dirichlet_enerjisi(x_current, D0_op)
            logger.debug(f"  └─ (Döngü r={r}/{config.R}) Uyumsuzluk: {d_disc_r:.6f} | Dirichlet Enerjisi E(x): {dirichlet_r:.6f}")

        logger.debug(f"[DÖNGÜ SONU (r={config.R})] Nihai Gizil Durum x^(R) Şekli: {x_current.shape}")

        
        e10_kulli = eval_model.n8_chebyshev(e9_guncel)
        logger.debug(f"[N8 Chebyshev Katsayı Projeksiyon] E10 Külli Mana Matrisi C Şekli: {e10_kulli.C.shape}")

        
        N_star, L_arc_val, N_teorik_val, delta_n_tensor = eval_model.n8_b_uzunluk(e10_kulli, eval_model.cheby_calc)
        logger.info(f"[N8_B Dinamik Uzunluk Seçici] Yay Uzunluğu L_arc: {L_arc_val:.4f} | Nyquist N_teorik: {N_teorik_val} | Kestirilen N*: {N_star}")

        
        T_matrix = eval_model.cheby_calc.hesapla(N=N_star)
        e11_gomulu = eval_model.n9_vandermonde(e10_kulli, T_matrix)
        logger.debug(f"[N9 Vandermonde Çarpım] E11 Gömülü Yörünge Şekli: {e11_gomulu.X_output.shape}")

        
        olasilik_matrisi = eval_model.n10_sozluk(e11_gomulu)
        logger.debug(f"[N10 Sözlük Softmax İzdüşüm] E12 Token Olasılık Matrisi P Şekli: {olasilik_matrisi.P.shape}")

        
        d_vec = eval_model.n7_cozucu.hesapla_uyumsuzluk_vektoru(x_current, D0_op)
        e_vec = eval_model.n7_cozucu.hesapla_dirichlet_enerjisi_vektoru(x_current, D0_op)
        d_discrepancy = float(d_vec.mean().detach().item())
        dirichlet_energy = float(e_vec.mean().detach().item())
        logger.info(f"[Topolojik Metrikler] Vektörel Dirichlet Enerjisi E(x) in R^{len(e_vec)}: {dirichlet_energy:.6f} | Kohomolojik Uyumsuzluk in R^{len(d_vec)}: {d_discrepancy:.6f}")

        
        if is_arc_json:
            sonuc_dict = arc_insa_edici.insa_et(olasilik_matrisi, hedef_boyut=(3, 3))
            nihai_cikti = json.dumps(sonuc_dict, ensure_ascii=False)
        else:
            
            if getattr(olasilik_matrisi, 'preds_full', None) is not None:
                token_preds = olasilik_matrisi.preds_full[0].cpu().tolist()  
            else:
                P_mat = olasilik_matrisi.P[0]  
                token_preds = torch.argmax(P_mat, dim=0).cpu().tolist()  

            
            tokenizer = al_cevrimdisi_veya_tiktoken_tokenizer("o200k_base")
            valid_token_ids = [t % tokenizer.n_vocab for t in token_preds]
            dec_str = tokenizer.decode(valid_token_ids)
            
            if len(dec_str.strip()) > 0:
                nihai_cikti = dec_str
            else:
                nihai_cikti = "..."


    import gc as _gc_cikarsama
    _gc_cikarsama.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    toplam_sure = time.time() - baslangic_zamani
    logger.info(f"Çıkarım Başarıyla Tamamlandı | Toplam Süre: {toplam_sure * 1000.0:.2f} ms")
    logger.info("================================================================================")
    
    return nihai_cikti


if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    test_metni = "Ahmet iyi bir yüzücüdür. Bu yüzden güçlü kasları vardır."
    cikti = Main_CikarsamaYurutucu(model_yolu="./checkpoints", test_girdisi=test_metni)
    print(f"\n[MODEL SİMÜLTANE ÇIKTISI]:\n{cikti}\n")
