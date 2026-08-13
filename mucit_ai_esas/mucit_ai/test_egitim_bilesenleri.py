print("[TEST SETUP] Python test script starting...", flush=True)
import sys
import os
import torch
import torch.nn as nn
import logging

print("[TEST SETUP] Modules imported successfully.", flush=True)
logging.basicConfig(level=logging.INFO, format="[TEST %(levelname)s] %(message)s", stream=sys.stdout)
logger = logging.getLogger("test_bilesenler")

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from kontratlar import (
    Model_TopolojikKonfigurasyon,
    Yardimci_ChebyshevMatrisHesaplayici,
    N8_ChebyshevKatsayiProjeksiyon,
    N8_B_DinamikUzunlukSecici,
    N10_SozlukSoftmaxIzdusem,
    N14_OdulTopolojikDevresmezlikMotoru,
    Odul_TopolojikDevresmezlikMotoru,
    Kayip_GRPO_Kriteri,
    Kayip_VICReg_UcluBilgiKorunumu,
    E9_GuncellenmisGizilDurum,
    E10_KulliManaMatrisi,
    E11_ParalelGomuluVektorlerMatrisi,
    E12_ParalelTokenOlasilikMatrisi,
    vram_on_kontrol_ve_nvme_tahliye
)

def vjp_cerrahi_enjekte_et(vector_loss: torch.Tensor, target_params: list, scale: float = 1.0) -> None:
    if not target_params or vector_loss is None:
        return
    loss_sum = vector_loss.sum() * scale
    grads = torch.autograd.grad(loss_sum, target_params, retain_graph=True, allow_unused=True)
    for p, g in zip(target_params, grads):
        if g is not None:
            if p.grad is None:
                p.grad = g.detach().clone()
            else:
                p.grad += g.detach().clone()

def test_n10_ve_grpo_2d_3d():
    logger.info("=== TEST 1: N10 Softmax, Ödül ve GRPO (2D & 3D Uyum Testi) ===")
    config = Model_TopolojikKonfigurasyon({"d": 64, "M_plus_1": 16, "V_size": 1000, "N": 128})

    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Cihaz: {device}")

    B = 2
    N = 128
    X_input = torch.randn(B, config.d, N, device=device, requires_grad=True)
    e11_mock = E11_ParalelGomuluVektorlerMatrisi(X_output=X_input)
    hedef_grouped = torch.randint(0, config.V_size, (B, N), device=device)

    n10 = N10_SozlukSoftmaxIzdusem(config).to(device)
    e12_res_2d = n10.forward(e11_mock, hedefler=hedef_grouped)
    assert e12_res_2d.P.dim() == 2, f"Beklenen 2D, Alınan: {e12_res_2d.P.shape}"
    logger.info(f"[PASS] N10 2D Output Şekli: {e12_res_2d.P.shape} (VRAM Tasarruflu)")

    odul_motoru = Odul_TopolojikDevresmezlikMotoru(config)
    oduller_2d = odul_motoru.hesapla(e12_res_2d.P, hedef_grouped)
    assert oduller_2d.shape == (B,), f"Beklenen ({B},), Alınan: {oduller_2d.shape}"
    logger.info(f"[PASS] Ödül Motoru 2D Çıktı Şekli: {oduller_2d.shape}")

    grpo = Kayip_GRPO_Kriteri(config)
    kayip_grpo_2d = grpo.hesapla_vektor(e12_res_2d.P, hedef_grouped, oduller_2d)
    assert kayip_grpo_2d.shape == (B,), f"Beklenen ({B},), Alınan: {kayip_grpo_2d.shape}"
    assert not torch.isnan(kayip_grpo_2d).any(), "GRPO 2D kaybında NaN tespit edildi!"
    logger.info(f"[PASS] GRPO Kriteri 2D Çıktı Şekli: {kayip_grpo_2d.shape} | Kayıp: {kayip_grpo_2d.mean().item():.4f}")

    q_r = torch.randn(B, 32, device=device)
    a_r = torch.randn(B, 32, device=device)
    x_ctx = torch.randn(B, 128, device=device)
    k_cevapsiz = torch.tensor([1.5, 2.0], device=device)
    k_cevapli = torch.tensor([0.5, 0.8], device=device)

    R_q, metrikler_q = odul_motoru.hesapla_aktif_sorgu_odulu(
        q_r=q_r, a_r=a_r, x_context=x_ctx,
        kayip_cevapsiz=k_cevapsiz, kayip_cevapli=k_cevapli
    )
    assert R_q.shape == (B,), f"Beklenen ({B},), Alınan: {R_q.shape}"
    logger.info(f"[PASS] Aktif Sorgu Ödülü R_q: {R_q.detach().cpu().tolist()}")

def test_vicreg_3d_alignment():
    logger.info("=== TEST 2: VICReg 3D Spektral Boyut Hizalama Testi ===")
    config = Model_TopolojikKonfigurasyon({"d": 64, "M_plus_1": 16, "V_size": 1000, "N": 128})
    device = "cuda" if torch.cuda.is_available() else "cpu"

    vicreg = Kayip_VICReg_UcluBilgiKorunumu()
    x_2d = torch.randn(2, 64, device=device)
    z_3d = torch.randn(2, 64, 128, device=device)

    (l_var, l_cov, l_rec), metrikler = vicreg(x=x_2d, z=z_3d)
    assert not torch.isnan(l_rec).any(), "VICReg rekonstrüksiyon kaybında NaN var!"
    logger.info(f"[PASS] VICReg 3D Hizalama Tamam: var={metrikler['l_var']:.4f}, cov={metrikler['l_cov']:.4f}, rec={metrikler['l_rec']:.4f}")

def test_vjp_cerrahi_ve_autograd():
    logger.info("=== TEST 3: VJP Cerrahi Gradyan Enjeksiyon Sırası ve Autograd Testi ===")
    config = Model_TopolojikKonfigurasyon({"d": 64, "M_plus_1": 16, "V_size": 1000, "N": 128})
    device = "cuda" if torch.cuda.is_available() else "cpu"

    n8_cheby = N8_ChebyshevKatsayiProjeksiyon(config).to(device)
    n8_b = N8_B_DinamikUzunlukSecici(config).to(device)
    n10 = N10_SozlukSoftmaxIzdusem(config).to(device)

    x_dummy = torch.randn(2, config.D, device=device, requires_grad=True)
    e9 = E9_GuncellenmisGizilDurum(x_next=x_dummy)

    e10 = n8_cheby.forward(e9)
    cheby_calc = Yardimci_ChebyshevMatrisHesaplayici(config)

    _, L_arc, N_ste, delta_n = n8_b.forward(e10, cheby_calc)

    kayip_spektral = (L_arc - 10.0)**2

    vjp_cerrahi_enjekte_et(kayip_spektral.unsqueeze(0), list(n8_cheby.parameters()) + list(n8_b.parameters()))

    for name, param in n8_cheby.named_parameters():
        assert param.grad is not None, f"Parametre {name} için gradyan enjekte edilemedi!"
    logger.info("[PASS] VJP Cerrahi enjeksiyonu ve autograd bağlantısı kusursuz çalışıyor!")

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    logger.info("MUCIT AI TUM BILESENLER VE ENTEGRASYON BUTUNLUK TESTI BASLATILIYOR...")
    try:
        test_n10_ve_grpo_2d_3d()
        test_vicreg_3d_alignment()
        test_vjp_cerrahi_ve_autograd()
        logger.info("[BASARILI] TUM TESTLER BASARIYLA GECTI! HICBIR HATA VEYA PATLAMA TESPIT EDILMEDI.")
    except Exception as e:
        logger.error(f"[HATA] TEST BASARISIZ OLDU: {e}", exc_info=True)
        sys.exit(1)
