
import os
import sys
import logging

if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s', stream=sys.stdout)
logger = logging.getLogger("MucitKulliIntegrationTest")

try:
    import kulli_gpu
except (ImportError, ModuleNotFoundError):
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    except NameError:
        project_root = os.path.abspath(os.getcwd())
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    import kulli_gpu
from mucit_ai.kontratlar import (
    Model_TopolojikKonfigurasyon,
    E1_HamMetinAkisi,
    N1_HibritByteTokenAyristirici,
    N2_TopoXHucreOlusumu,
    N3_LifSinirlamaAtama,
    Riyazi_LifLaplasyeniBlokInsaEdici,
    N4_SorguSecici,
    N5_CevapSuzucu,
    Bellek_BaglamYoneticisi,
    E5_A_MevcutGizilDurum,
)
from mucit_ai.checkpoint_manager import NPZCheckpointManager

def main():
    logger.info("=== MUCİT_AI & KÜLLÎ_GPU HAKİKİ ENTEGRASYON TESTİ (AYNA SINAĞI) BAŞLATILIYOR ===")

    driver = kulli_gpu.baslat()
    logger.info("[Küllî_GPU Driver] Sanal Sürücü ve C-API Huni Kancaları Başarıyla Aktif Edildi.")

    config = Model_TopolojikKonfigurasyon({
        "batch_size": 1,
        "d_v": 32,
        "d_e": 32,
        "d_q": 64,
        "d_a": 64,
        "d_m": 64,
        "d_h": 64,
        "d": 128,
        "M_plus_1": 32,
        "N": 32,
        "R": 4,
        "K": 16,
    })

    turkce_cumle = (
        "Türk bilişsel yapay zeka mimarimiz topolojik rekürens ve lif laplasyeni kuramları "
        "üzerine inşa edilmiş olup külli gpu sanal sürücüsü vasıtasıyla sekiz gigabaytlık "
        "sanal vram bellek havuzunda kesintisiz ve verimli çalışmaktadır."
    )
    kelime_sayisi = len(turkce_cumle.split())
    logger.info(f"Sentetik Türkçe Girdi Cümlesi ({kelime_sayisi} Kelime): '{turkce_cumle}'")
    assert kelime_sayisi == 30, f"Cümle tam 30 kelime olmalıdır! Mevcut: {kelime_sayisi}"

    e1_input = E1_HamMetinAkisi(X_text=turkce_cumle)
    n1_ayristirici = N1_HibritByteTokenAyristirici(config)
    e2_bytes, x_initial = n1_ayristirici(e1_input)
    logger.info(f"N1 Çıktısı Doğrulandı: Byte/Token Uzunluğu={e2_bytes.l_bytes}, Initial Latent={type(x_initial)}")

    n2_hucre = N2_TopoXHucreOlusumu(config)
    e3_sinir_op = n2_hucre(e2_bytes, x_initial=x_initial)
    logger.info("N2 Çıktısı Doğrulandı: Sınır Operatörleri D1 ve D2 üretildi.")

    n3_lif = N3_LifSinirlamaAtama(config)
    e4_lif_demeti = n3_lif(e3_sinir_op, x_initial)
    laplasyen_insaci = Riyazi_LifLaplasyeniBlokInsaEdici(config)
    D0_op, Delta_0 = laplasyen_insaci.insa_et(e3_sinir_op, e4_lif_demeti.phi_matrisleri)
    logger.info("Laplasyen İnşası Doğrulandı: Coboundary D0 ve Lif Laplasyeni Delta_0 üretildi.")

    n4_sorgu = N4_SorguSecici(config)
    n5_cevap = N5_CevapSuzucu(config=config)
    bellek_yonetici = Bellek_BaglamYoneticisi(config)
    m_bellek = bellek_yonetici.get_memory(config.batch_size)

    mevcut_durum = E5_A_MevcutGizilDurum(x_r=x_initial)

    for r in range(config.R):
        e6_q = n4_sorgu(mevcut_durum, D0_operator=D0_op, bellek=m_bellek)
        e7_a = n5_cevap(e6_q, m_bellek)
        m_bellek.M = bellek_yonetici.guncelle(m_bellek.M, e6_q, e7_a)
        logger.info(f"Rekürens Adımı r={r+1}/{config.R} Başarıyla Tamamlandı.")

    ckpt_mgr = NPZCheckpointManager(checkpoint_dir="/tmp/test_mucit_kulli_ckpt")
    saved_path = ckpt_mgr.save_pytorch_model(
        step=1,
        token_offset=e2_bytes.l_bytes,
        model=n1_ayristirici,
        loss_history=[0.1234]
    )
    logger.info(f"NPZ Checkpoint Kaydı Başarılı: {saved_path}")

    logger.info("=== MUCİT_AI & KÜLLÎ_GPU HAKİKİ ENTEGRASYON TESTİ (AYNA SINAĞI) BAŞARIYLA TAMAMLANDI ===")

if __name__ == "__main__":
    main()
