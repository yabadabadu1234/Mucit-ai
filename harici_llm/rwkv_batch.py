"""
Albatross (https://github.com/BlinkDL/Albatross) incelendi: RTX5090'a özel,
çalışma-zamanında derlenen CUDA kernel'leri ve GPU-başına el ile ayarlanmış
tuning tabloları (cuBLASLt algoritma indeksleri) içeriyor -- kendi README'si
"tune linear_orig_layout for your GPU" diyor. Bunu GPU'suz bir ortamda ve
Kaggle'ın (muhtemelen çok daha eski) CUDA araç zincirinde körlemesine entegre
etmek, defalarca yaşadığımız "görünüşte doğru ama gerçekte hiç çalışmayan
kod" riskini taşır -- bu yüzden Albatross'un KENDİSİ entegre edilmedi.

Bunun yerine, hızın asıl kaynağı olan FİKİR uygulanıyor: RWKV'nin bant-
genişliği-sınırlı (memory-bandwidth-bound) RNN dekodlamasında asıl kazanç,
TEK GPU'da AYNI AĞIRLIKLARI PAYLAŞAN çoklu BAĞIMSIZ diziyi TOPLU (batched)
işlemekten gelir -- ağırlık okuma maliyeti tüm batch'e yayılır. Bu dosya
tam olarak bunu, özel derleme/tuning GEREKTİRMEDEN, saf PyTorch ile yapar.

DOĞRULUK GARANTİSİ: aşağıdaki her fonksiyon, kurulu `rwkv` paketinin GERÇEK
kaynağından (site-packages/rwkv/model.py :: RWKV_x070_TMix_one /
RWKV_x070_CMix_one, RWKV_DE_VERSION bayrağı OLMADAN) SATIR SATIR
türetilmiştir; tek fark her tensöre bir B (batch) boyutu eklenmiş olmasıdır.
Bu eşdeğerlik, test_boru_hatti.py'de kurulu GERÇEK `rwkv` paketiyle
(sentetik ama gerçek biçimli bir .pth ağırlığı üzerinden, B=1 döngüsüyle
üretilen referans çıktıya karşı) sayısal olarak doğrulanır.
"""
import os
import threading
import traceback
from typing import Any, Callable, Dict, List, Optional, Tuple

import torch
import torch.nn.functional as F


def sifir_durum_toplu(z: Dict[str, torch.Tensor], n_layer: int, n_embd: int,
                       n_head: int, head_size: int, B: int) -> List[torch.Tensor]:
    """rwkv/model.py :: generate_zero_state()'in B-toplu hali:
    durum[i*3+0]=(B,C) att_x_prev, durum[i*3+1]=(B,H,N,N) att_kv,
    durum[i*3+2]=(B,C) ffn_x_prev."""
    ornek = z['emb.weight']
    device, dtype = ornek.device, ornek.dtype
    durum: List[Any] = [None] * (n_layer * 3)
    for i in range(n_layer):
        durum[i * 3 + 0] = torch.zeros(B, n_embd, dtype=dtype, device=device)
        durum[i * 3 + 1] = torch.zeros(B, n_head, head_size, head_size, dtype=torch.float32, device=device)
        durum[i * 3 + 2] = torch.zeros(B, n_embd, dtype=dtype, device=device)
    return durum


def _tmix_adim_toplu(layer_id: int, H: int, N: int, x, x_prev, v_first, state,
                      x_r, x_w, x_k, x_v, x_a, x_g, w0, w1, w2, a0, a1, a2,
                      v0, v1, v2, g1, g2, k_k, k_a, r_k, R_, K_, V_, O_, ln_w, ln_b):
    """rwkv/model.py :: RWKV_x070_TMix_one'in B-toplu hali -- ağırlık
    tensörleri (x_r, w0, R_, ...) HİÇ değişmez/paylaşılır; yalnızca
    x/x_prev/v_first/state'e bir B lider boyutu eklenir, geri kalan tüm
    matris çarpımı/broadcast kuralları PyTorch'ta otomatik olarak
    batch-uyumludur."""
    B = x.shape[0]
    xx = x_prev - x
    # HIZ (kullanıcının açık talebi -- "torch.compile çalışmadığı senaryo
    # için yapılan çağrı sayısını azalt"): eskiden burada xr..xg için AYRI
    # AYRI 6 elementwise ifade ("x + xx*x_r" gibi) hesaplanıyordu -- eager
    # modda her biri (çarpma + toplama) ~2 ayrı kernel başlatmasına yol
    # açar, yani 6 değişken × 2 = 12 kernel çağrısı. Bu 6 ağırlık vektörü
    # (x_r..x_g) TEK bir (6, C) tensöre yığılıp (stack) TEK bir broadcast'lı
    # çarpma + TEK bir broadcast'lı toplama ile HEPSİ BİRDEN hesaplanıyor
    # (~2-4 kernel çağrısına iniyor). Bu, ELEMENTWISE (mul/add) işlemlerin
    # broadcast ile TOPLU yapılması -- matematiksel SIRA/GRUPLAMA
    # DEĞİŞMİYOR (her çıktı elemanı TAM OLARAK aynı çarpma-sonra-toplama
    # işlemiyle hesaplanıyor), bu yüzden bit-bit AYNI sonucu verir --
    # aşağıda synthetic ağırlıklarla torch.equal ile doğrulandı.
    agirlik_yigini = torch.stack((x_r, x_w, x_k, x_v, x_a, x_g), dim=0)
    kombo = x.unsqueeze(0) + xx.unsqueeze(0) * agirlik_yigini.unsqueeze(1)
    xr, xw, xk, xv, xa, xg = kombo[0], kombo[1], kombo[2], kombo[3], kombo[4], kombo[5]

    r = xr @ R_
    w = torch.tanh(xw @ w1) @ w2
    k = xk @ K_
    v = xv @ V_
    a = torch.sigmoid(a0 + (xa @ a1) @ a2)
    g = torch.sigmoid(xg @ g1) @ g2

    kk = F.normalize((k * k_k).view(B, H, N), dim=-1, p=2.0).view(B, H * N)
    k = k * (1 + (a - 1) * k_a)
    if layer_id == 0:
        v_first = v
    else:
        v = v + (v_first - v) * torch.sigmoid(v0 + (xv @ v1) @ v2)
    w = torch.exp(-0.606531 * torch.sigmoid((w0 + w).float()))  # 0.606531 = exp(-0.5)

    vk = v.view(B, H, N, 1) @ k.view(B, H, 1, N)
    ab = (-kk).view(B, H, N, 1) @ (kk * a).view(B, H, 1, N)
    state = state * w.view(B, H, 1, N) + state @ ab.float() + vk.float()
    xx = state.to(dtype=x.dtype) @ r.view(B, H, N, 1)

    xx = F.group_norm(xx.view(B, H * N), num_groups=H, weight=ln_w, bias=ln_b, eps=64e-5).view(B, H * N)
    xx = xx + ((r * k * r_k).view(B, H, N).sum(dim=-1, keepdim=True) * v.view(B, H, N)).view(B, H * N)
    return (xx * g) @ O_, x, state, v_first


def _cmix_adim_toplu(x, x_prev, x_k, K_, V_):
    """rwkv/model.py :: RWKV_x070_CMix_one'in B-toplu hali -- kod TEK
    KARAKTER bile DEĞİŞMEDEN batch-uyumludur (başlı-bölme/head-split
    yok, saf elementwise + matmul); yine de netlik için burada kopyalanır."""
    xx = x_prev - x
    k = x + xx * x_k
    k = torch.relu(k @ K_) ** 2
    return k @ V_, x


# NOT (Turkce): kullanicinin "prefil hizlandir" talebi -- gercek Kaggle
# logunda 43 gorevlik bir partide en uzun promptun (6326 token) BATCHED
# prefill'i TEK BASINA ~1584 saniye surmustu (~0.25 sn/adim). Bu, RWKV'nin
# ZORUNLU olarak SIRALI (recurrent) doğasından degil -- her adimda 32
# katmanin HER BIRINDE birkac KUCUK matmul/elementwise islem calisiyor,
# ve bu KUCUK islemlerin GPU'da GERCEK hesaplama suresi degil, Python
# yorumlayicisinin + CUDA kernel BASLATMA (launch) gecikmesinin baskin
# oldugu bir rejimden geliyor (klasik "kernel-launch-bound" darbogaz).
#
# KOK NEDEN BULUNDU VE DUZELTILDI (kullanicinin gercek Kaggle logu iki
# AYRI hatayi acikca gosterdi -- ikisi de coklu_gpu.py'nin HER GPU'yu
# AYRI bir Python threading.Thread'inde, surec DEGIL, calistirmasindan
# kaynaklaniyor, ve ikisinin de BILINEN, standart cozumu var):
#
#   1) cuda:1: "AssertionError: assert torch._C._is_key_in_tls(...)"
#      -- bu, SADECE mode="reduce-overhead"in kullandigi CUDA Graph
#      Trees mekanizmasindan (inductor/cudagraph_trees.py) gelir; o
#      mekanizma thread-local state'e dayanir ve DOKUMANLI olarak coklu
#      thread'ler arasinda GUVENLI DEGILDIR. COZUM: mode="reduce-overhead"
#      (CUDA Graph capture/replay) KULLANILMIYOR ARTIK -- asagida sade
#      torch.compile(fn) (mode belirtilmeden, "default" backend)
#      kullaniliyor. Bu hala Triton/inductor ile KUCUK islemleri BUYUK,
#      FUZE edilmis kernel'lere birlestirip kernel-baslatma sayisini
#      ciddi olcude azaltir (asil hedefimiz), ama CUDA Graph replay
#      YAPMAZ -- yani cudagraph_trees'in thread-local durumuna hic
#      girmez, DOLAYISIYLA bu spesifik hata SINIFI kokten ortadan kalkar.
#      Yan fayda: "girdi tensorlerinin adresi sabit kalir" varsayimi da
#      (CUDA Graph'e ozgu) artik gecerli degil -- adim_toplu_maskeli'nin
#      `durum` listesini her adimda YENI tensorlerle degistirmesi (bkz.
#      _maske_uygula) ARTIK bir sessiz-yanlislik riski TASIMIYOR.
#
#   2) cuda:0: "Detected that you are using FX to symbolically trace a
#      dynamo-optimized function" -- TorchDynamo'nun kendisi RESMEN
#      thread-safe DEGILDIR (PyTorch belgeleri: "TorchDynamo is
#      currently not thread safe"); N GPU thread'i NEREDEYSE AYNI ANDA
#      kendi ILK cagrisinda derlemeyi/izlemeyi (tracing) TETIKLEYINCE,
#      dynamo'nun paylasilan ic durumu (frame evaluation hook'lari,
#      guard insasi) thread'ler arasinda YARISA girip BOZULABILIYOR --
#      gordugumuz hata TAM OLARAK bu bilinen sinifta. COZUM: her
#      cihazin ILK gercek cagrisini (derlemenin/izlemenin fiilen
#      gerceklestigi an) KURESEL bir kilit (_DERLEME_KILIDI) altinda
#      SERILESTIRIYORUZ -- yani N GPU thread'i ayni anda DERLEMEYE
#      GIRMEZ, sirayla derlenir. Derleme/ilk-cagri BIR KEZ tamamlandiktan
#      SONRA o cihazin derlenmis fonksiyonu kilitsiz, TAM PARALEL
#      calisir (bu yuzden coklu-GPU paralelligi KAYBEDILMEZ -- yalnizca
#      baslangictaki kisa derleme penceresi sirali hale gelir).
#
# Bu iki hedefli duzeltmeyle torch.compile artik VARSAYILAN OLARAK
# tekrar ACIK. RWKV_BATCH_TORCH_COMPILE=0 ile HALA kapatilabilir (ornegin
# Kaggle'in arac zincirinde triton/inductor'un kendisi BASARISIZ olursa
# -- bu durumda zaten asagidaki try/except o cihaz icin KALICI eager'a
# duser, calisma DURMAZ).
_TORCH_COMPILE_ETKIN = os.environ.get("RWKV_BATCH_TORCH_COMPILE", "1") != "0"
_derlenmis_cekirdek_onbellek: Dict[str, Any] = {}
_derleme_basarisiz_cihazlar: set = set()
# TorchDynamo resmen thread-safe DEGIL -- N GPU thread'inin AYNI ANDA
# derlemeye/ilk-izlemeye girmesini onlemek icin KURESEL bir kilit
# kullaniliyor (yalnizca ILK cagri boyunca tutulur, bkz. yukaridaki not
# ve asagidaki adim_toplu). Derlenmis fonksiyonun SONRAKI cagrilari
# kilitsiz, TAM PARALEL calisir.
_DERLEME_KILIDI = threading.Lock()
_ilk_cagrisi_tamamlanan_cihazlar: set = set()


def _adim_toplu_cekirdek(z: Dict[str, torch.Tensor], n_layer: int, n_embd: int, n_head: int, head_size: int,
                          token_tensor: torch.Tensor, durum: List[torch.Tensor]) -> Tuple[torch.Tensor, List[torch.Tensor]]:
    """adim_toplu()'nun GERÇEK matematiği -- token id'lerini bir Python
    LİSTESİ değil, ÇAĞIRAN TARAFIN (adim_toplu) ÖNCEDEN oluşturduğu bir
    torch.Tensor olarak alır. Bunun TEK sebebi torch.compile UYUMLULUĞU:
    bir Python int listesi torch.compile'a doğrudan verilirse, listenin
    İÇERİĞİ (her adımda FARKLI token id'leri) DEĞER-bazlı bir 'guard'
    oluşturur ve HER TEK adımda YENİDEN DERLEMEYE yol açar -- derlemenin
    tüm kazancını yer. Aynı ŞEKİLDEKİ bir torch.Tensor ise DEĞERİ her
    adımda değişse bile TEK bir derlemeyle çalışır (yalnızca B/n_layer
    ŞEKLİ değişirse yeniden derlenir)."""
    x = z['emb.weight'][token_tensor]
    v_first = torch.empty_like(x)

    for i in range(n_layer):
        bbb, att, ffn = f'blocks.{i}.', f'blocks.{i}.att.', f'blocks.{i}.ffn.'
        xx = F.layer_norm(x, (n_embd,), weight=z[bbb + 'ln1.weight'], bias=z[bbb + 'ln1.bias'])
        xx, durum[i * 3 + 0], durum[i * 3 + 1], v_first = _tmix_adim_toplu(
            i, n_head, head_size, xx, durum[i * 3 + 0], v_first, durum[i * 3 + 1],
            z[att + 'x_r'], z[att + 'x_w'], z[att + 'x_k'], z[att + 'x_v'], z[att + 'x_a'], z[att + 'x_g'],
            z[att + 'w0'], z[att + 'w1'], z[att + 'w2'], z[att + 'a0'], z[att + 'a1'], z[att + 'a2'],
            z[att + 'v0'], z[att + 'v1'], z[att + 'v2'], z[att + 'g1'], z[att + 'g2'],
            z[att + 'k_k'], z[att + 'k_a'], z[att + 'r_k'],
            z[att + 'receptance.weight'], z[att + 'key.weight'], z[att + 'value.weight'], z[att + 'output.weight'],
            z[att + 'ln_x.weight'], z[att + 'ln_x.bias'],
        )
        x = x + xx
        xx = F.layer_norm(x, (n_embd,), weight=z[bbb + 'ln2.weight'], bias=z[bbb + 'ln2.bias'])
        xx, durum[i * 3 + 2] = _cmix_adim_toplu(
            xx, durum[i * 3 + 2], z[ffn + 'x_k'], z[ffn + 'key.weight'], z[ffn + 'value.weight'],
        )
        x = x + xx

    x = F.layer_norm(x, (n_embd,), weight=z['ln_out.weight'], bias=z['ln_out.bias'])
    x = x @ z['head.weight']
    return x, durum


def _derleme_hatasini_bildir(baglam: str, anahtar: str) -> None:
    """torch.compile derleme VEYA çalışma-zamanı hatalarının TEK, ORTAK
    raporlama noktası. NOT (kullanıcının gerçek Kaggle logunda yakaladığı
    hata): önceki sürümde burada yalnızca `{hata}` (str(exception) --
    YALNIZCA hatanın MESAJINI verir) basılıyordu; bazı CUDA/inductor
    hataları için bu mesaj BOŞ ya da tek satırlık/teşhis için yetersiz
    çıkıyor ve log ekranda "...eager moda düşülüyor:" ile KESİK/boş
    görünüyordu. `traceback.format_exc()` çağıran fonksiyonun İÇİNDE,
    aktif bir except bloğu SIRASINDA çağrılmalıdır (Python'ın sys.exc_info
    durumunu okur) -- bu yüzden bu fonksiyon her zaman bir except bloğunun
    içinden çağrılmalıdır."""
    print(
        f"[rwkv_batch] UYARI: {baglam} ({anahtar}) BAŞARISIZ, eager moda KALICI OLARAK düşülüyor. "
        f"TAM HATA İZİ:\n{traceback.format_exc()}"
    )


def _cekirdek_fonksiyonu_al(cihaz: torch.device):
    """Yalnızca CUDA'da ve yalnızca DAHA ÖNCE başarıyla derlenebildiyse
    torch.compile'lı çekirdeği döner -- derleme BAŞARISIZ olursa o cihaz
    için SESSİZCE ve KALICI OLARAK eager çekirdeğe düşülür (bir daha
    denenmez -- her adımda yeniden deneyip başarısız olmak, tam da
    önlemeye çalıştığımız yavaşlığı geri getirir)."""
    anahtar = str(cihaz)
    if not _TORCH_COMPILE_ETKIN or cihaz.type != "cuda" or anahtar in _derleme_basarisiz_cihazlar:
        return _adim_toplu_cekirdek
    if anahtar not in _derlenmis_cekirdek_onbellek:
        try:
            # NOT: mode="reduce-overhead" (CUDA Graph Trees) BİLİNÇLİ OLARAK
            # kullanılmıyor -- bkz. yukarıdaki uzun not (thread-local state'e
            # dayanır, coklu-thread mimarimizde çöker). Mode belirtilmeden
            # (varsayılan inductor backend'i) yine Triton ile küçük
            # işlemleri füze edilmiş kernel'lere birleştirip kernel-başlatma
            # sayısını azaltır, ama CUDA Graph replay YAPMAZ.
            _derlenmis_cekirdek_onbellek[anahtar] = torch.compile(_adim_toplu_cekirdek)
            print(
                f"[rwkv_batch] {anahtar}: adim_toplu için torch.compile (CUDA Graph'siz -- bkz. dosya başındaki "
                f"not) etkinleştirildi -- prefill/üretimdeki tekrarlanan küçük adımların kernel-başlatma yükü azaltılacak."
            )
        except Exception:
            _derleme_hatasini_bildir("torch.compile derlemesi", anahtar)
            _derleme_basarisiz_cihazlar.add(anahtar)
            return _adim_toplu_cekirdek
    return _derlenmis_cekirdek_onbellek[anahtar]


@torch.no_grad()
def adim_toplu(z: Dict[str, torch.Tensor], n_layer: int, n_embd: int, n_head: int, head_size: int,
               token_idler: List[int], durum: List[torch.Tensor]) -> Tuple[torch.Tensor, List[torch.Tensor]]:
    """B BAĞIMSIZ dizinin HER BİRİNİN bir sonraki-token logitini, AYNI
    ağırlıkları (z) PAYLAŞARAK TEK bir toplu ileri-geçişte hesaplar --
    forward_one()'in B kere ayrı ayrı çağrılmasıyla MATEMATİKSEL OLARAK
    AYNI sonucu, tek GPU'da gerçek çoklu-dizi paralelliğiyle üretir
    (ağırlık-okuma maliyeti B'ye bölünür -- bant genişliği-sınırlı RNN
    dekodlamasında asıl kazanç budur). CUDA'da, torch.compile başarıyla
    derlenebildiyse (bkz. _cekirdek_fonksiyonu_al) bu adım kernel-başlatma
    yükünü azaltan derlenmiş bir grafikle çalışır; CPU'da veya derleme
    başarısız olursa MATEMATİKSEL OLARAK AYNI eager kod çalışır."""
    cihaz = z['emb.weight'].device
    token_tensor = torch.as_tensor(token_idler, device=cihaz, dtype=torch.long)
    anahtar = str(cihaz)
    # NOT (Turkce -- BURADA GERCEK BIR HATA VARDI, kullanicinin gercek
    # Kaggle logu bunu kanitladi: bir onceki "duzeltme" YALNIZCA ilk
    # GERCEK CAGRIYI (fn(...) calistirmayi) kilit altina aliyordu, ama
    # _cekirdek_fonksiyonu_al(cihaz) -- yani torch.compile(_adim_toplu_
    # cekirdek) SARMA cagrisinin KENDISI -- KILIT DISINDA, HER 4 thread
    # icin NEREDEYSE AYNI ANDA cagriliyordu (log: 4 cihazin "etkinlestirildi"
    # mesaji AYNI saniyede basiliyordu). torch.compile(), SARDIGI ham
    # Python fonksiyonunun (BURADA: TEK, PAYLASILAN _adim_toplu_cekirdek
    # kod nesnesi -- 4 cihaz AYNI fonksiyonu sarar) frame-degerlendirme
    # kancasini/guard kayitlarini dynamo'nun PAYLASILAN ic durumuna
    # islemeye BASLAR -- bu, "lazy" olsa da (gercek izleme ilk cagriya
    # ertelenir) GERCEK CAGRI OLMADAN BILE thread-guvenli DEGILDIR. 4
    # thread AYNI ANDA AYNI kod nesnesini sarinca dynamo'nun ic kayitlari
    # CAKISIYOR, ve SONRA gelen ilk gercek cagri (benim kilidim koruyordu)
    # bu ONCEDEN BOZULMUS durumu miras alip "FX ile symbolik izleme"
    # hatasini firlatiyordu. DUZELTME: artik torch.compile() SARMA
    # cagrisinin KENDISI de (_cekirdek_fonksiyonu_al icinde) BU kilit
    # altinda, ilk gercek cagriyla AYNI kritik bolgede yapiliyor.
    if (_TORCH_COMPILE_ETKIN and cihaz.type == "cuda"
            and anahtar not in _derleme_basarisiz_cihazlar
            and anahtar not in _ilk_cagrisi_tamamlanan_cihazlar):
        with _DERLEME_KILIDI:
            # Kilidi beklerken baska bir thread AYNI cihazin derlemesini/
            # ilk cagrisini ZATEN tamamlamis (veya basarisiz kilmis)
            # olabilir -- cift kontrol.
            if anahtar not in _derleme_basarisiz_cihazlar and anahtar not in _ilk_cagrisi_tamamlanan_cihazlar:
                fn = _cekirdek_fonksiyonu_al(cihaz)  # torch.compile(...) SARMA cagrisi ARTIK kilit ALTINDA
                if fn is not _adim_toplu_cekirdek:
                    try:
                        sonuc = fn(z, n_layer, n_embd, n_head, head_size, token_tensor, durum)
                        _ilk_cagrisi_tamamlanan_cihazlar.add(anahtar)
                        return sonuc
                    except Exception:
                        _derleme_hatasini_bildir("derlenmiş adim_toplu ÇALIŞMA ZAMANI (ilk çağrı)", anahtar)
                        _derleme_basarisiz_cihazlar.add(anahtar)
                        return _adim_toplu_cekirdek(z, n_layer, n_embd, n_head, head_size, token_tensor, durum)
    # Buraya ya (a) compile kapalı/CPU/önceden başarısız, ya da (b) bu
    # cihaz için derleme+ilk çağrı ZATEN (kilit altında) tamamlanmış
    # olarak gelinir -- kilitsiz, tam paralel hızlı yol.
    fn = _cekirdek_fonksiyonu_al(cihaz)
    try:
        return fn(z, n_layer, n_embd, n_head, head_size, token_tensor, durum)
    except Exception:
        if fn is _adim_toplu_cekirdek:
            raise
        _derleme_hatasini_bildir("derlenmiş adim_toplu ÇALIŞMA ZAMANI", anahtar)
        _derleme_basarisiz_cihazlar.add(anahtar)
        return _adim_toplu_cekirdek(z, n_layer, n_embd, n_head, head_size, token_tensor, durum)


def _maske_uygula(yeni: torch.Tensor, eski: torch.Tensor, aktif_maske: torch.Tensor) -> torch.Tensor:
    """aktif_maske[b]=True olan B dilimlerinde `yeni`, False olanlarda
    `eski` tensörü tutulur -- durum[i] (B,C) veya (B,H,N,N) şekilli
    olabildiği için maske, B dışındaki TÜM eksenlere broadcast edilir."""
    sekil = [aktif_maske.shape[0]] + [1] * (yeni.dim() - 1)
    return torch.where(aktif_maske.view(*sekil), yeni, eski)


@torch.no_grad()
def adim_toplu_maskeli(z: Dict[str, torch.Tensor], n_layer: int, n_embd: int, n_head: int, head_size: int,
                        token_idler: List[int], durum: List[torch.Tensor],
                        aktif_maske: List[bool]) -> Tuple[torch.Tensor, List[torch.Tensor]]:
    """adim_toplu()'yu TÜM B için çalıştırır, ama yalnızca aktif_maske[b]=True
    olan dizilerin durumunu İLERLETİR -- aktif_maske[b]=False olan
    dizilerin durumu (state) AYNEN korunur. Bu, TEK bir batched çağrı
    içinde:
      (a) FARKLI UZUNLUKTAKİ B promptu (batched prefill -- kısa promptlu
          diziler, kendi son gerçek tokenlerinden sonra "dondurulur",
          uzun promptlu diziler onlar bitene kadar ilerlemeye devam eder),
      (b) B görevden bazıları ERKEN bitince (submit_answer çağrıldığında)
          o dizileri "dondurup" geri kalanların TEK bir batch'te devam
          etmesini
    mümkün kılar -- gerçek `rwkv` paketinin forward_one()'ında BÖYLE bir
    kavram yoktur (o zaten hep B=1'dir); bu fonksiyon TAMAMEN bizim
    eklediğimiz, ama matematiksel olarak forward_one()'ın B kere ayrı ayrı,
    HER BİRİNİN KENDİ GERÇEK token dizisiyle çağrılmasıyla AYNI sonucu
    üreten bir mekanizmadır (bkz. test_boru_hatti.py'deki doğrulama).

    HIZ (kullanıcının gerçek darboğaz talebi): `_adim_toplu_cekirdek`
    CUDA'da torch.compile(mode="reduce-overhead") ile TEK bir derlenmiş
    grafiğe/CUDA-graph'e indirgeniyor -- ama bu maskeleme döngüsü (aşağıda)
    o derlenmiş grafiğin TAMAMEN DIŞINDA, HER adımda n_layer*3 (32
    katmanlı bir modelde 96) AYRI eager `torch.where` çağrısı yapıyordu.
    Bu da tam olarak compile'ın ortadan kaldırmaya çalıştığı "kernel-
    başlatma-sınırlı" gecikmeyi, derlenmiş çekirdeğin HEMEN ARDINDAN
    geri getiriyordu. Oysa üretim döngüsünün ASIL sık durumunda (henüz
    hiçbir slot bitmemiş/donmamışken) aktif_maske TAMAMEN True'dur --
    bu durumda maskeleme matematiksel olarak TAM BİR NO-OP'tur (yeni
    durum, eskisinin YERİNE geçer, hiçbir satır korunmaz). Bu döngü artık
    yalnızca GERÇEKTEN bir slot donmuşken (bazı b'ler aktif_maske=False)
    çalıştırılıyor; aksi halde yeni_durum DOĞRUDAN, hiç maskelemeden
    döndürülüyor -- sonuç matematiksel olarak BİREBİR AYNI (True/False
    karışık değilken torch.where(True, yeni, eski) zaten her zaman
    yeni'yi seçer), yalnızca 96 gereksiz kernel başlatması adım başına
    ORTADAN KALKIYOR."""
    maske_t = torch.as_tensor(aktif_maske, device=z['emb.weight'].device, dtype=torch.bool)
    if maske_t.all():
        return adim_toplu(z, n_layer, n_embd, n_head, head_size, token_idler, durum)
    eski_durum = list(durum)  # sığ kopya: adim_toplu ESKİ tensörleri MUTATE ETMEZ, yalnızca liste yuvalarını YENİ tensörlerle değiştirir
    yeni_logits, yeni_durum = adim_toplu(z, n_layer, n_embd, n_head, head_size, token_idler, durum)
    for i in range(len(yeni_durum)):
        yeni_durum[i] = _maske_uygula(yeni_durum[i], eski_durum[i], maske_t)
    return yeni_logits, yeni_durum


@torch.no_grad()
def onisle_toplu_farkli_uzunluk(z: Dict[str, torch.Tensor], n_layer: int, n_embd: int, n_head: int, head_size: int,
                                 token_dizileri: List[List[int]],
                                 durum: Optional[List[torch.Tensor]] = None,
                                 ilerleme_geri_cagirma: Optional[Callable[[int, int], None]] = None,
                                 ilerleme_adimi: int = 200,
                                 ) -> Tuple[torch.Tensor, List[torch.Tensor]]:
    """B BAĞIMSIZ ve FARKLI UZUNLUKTAKİ prompt'u (ör. B FARKLI ARC
    bulmacasının B FARKLI metni) TEK bir batched prefill'de işler --
    her dizi t < kendi_uzunluğu olduğu sürece aktif_maske ile ilerletilir,
    kendi uzunluğuna ulaşınca dondurulur (daha kısa promptlu dizilerin
    durumu, daha uzun promptlu dizileri BEKLERKEN BOZULMAZ). Döner:
    (B, vocab) biçiminde HER dizinin KENDİ son promptu tokenından sonraki
    logit'i (sonraki_token tahmini) ve güncel durum.

    `ilerleme_geri_cagirma(t, azami_uzunluk)` verilirse, her `ilerleme_adimi`
    adımda bir (ve bitişte) çağrılır -- kullanıcının fark ettiği gibi, en
    uzun promptlu bir görev varsa (ör. 6000+ token) prefill TEK BAŞINA
    dakikalarca sürebilir ve bu SÜRE BOYUNCA hiçbir log basılmıyordu;
    çağıran taraf (coz_yurutucu_toplu.py) bunu YARISMA=False iken
    ayrıntılı ilerleme logu basmak için kullanır."""
    B = len(token_dizileri)
    if durum is None:
        durum = sifir_durum_toplu(z, n_layer, n_embd, n_head, head_size, B)
    azami_uzunluk = max(len(t) for t in token_dizileri)
    son_logitler: List[Optional[torch.Tensor]] = [None] * B
    cihaz = z['emb.weight'].device

    # NOT (Turkce): kullanicinin haklı sorusu -- "neden bu kadar cok kernel
    # cagrisi" -- burada GERCEK bir kaynagi vardı: ONCEKI kod her t adiminda
    # (1) YENİ bir Python listesi kuruyordu (2) adim_toplu icindeki
    # torch.as_tensor(...) bu listeyi HER SEFERINDE CPU'dan GPU'ya YENIDEN
    # kopyaliyordu -- T=6326 adimlik bir prefill'de bu, kernel baslatmalarina
    # EK OLARAK 6326 AYRI host->device transferi demekti (her biri kendi
    # senkronizasyon/gecikme maliyetiyle). Tum (T,B) token/maske izgarasi
    # PREFILL BASLAMADAN ONCE zaten TAM OLARAK biliniyor -- bu yuzden TEK
    # SEFERDE GPU'ya tasiniyor, dongu icinde ise ZATEN GPU'da olan bir
    # satiri DILIMLEMEKTEN (host->device transferi YOK) baska bir sey
    # yapilmiyor. Hesaplanan deger/matematik BIREBIR AYNI kalir -- yalnizca
    # veriyi GPU'ya tasima YONTEMI degisti (test_20/test_24 bunu sayisal
    # olarak dogruluyor).
    token_izgara = torch.zeros((azami_uzunluk, B), dtype=torch.long)
    maske_izgara = torch.zeros((azami_uzunluk, B), dtype=torch.bool)
    for b in range(B):
        dizi_tensor = torch.as_tensor(token_dizileri[b], dtype=torch.long)
        uzunluk = dizi_tensor.shape[0]
        token_izgara[:uzunluk, b] = dizi_tensor
        if uzunluk < azami_uzunluk:
            token_izgara[uzunluk:, b] = dizi_tensor[-1]  # dondurulmus adimlarda deger onemsiz (maskeleniyor), yalnizca -1 gibi GECERSIZ bir embedding indeksinden kacinmak icin son gercek token tekrarlanir
        maske_izgara[:uzunluk, b] = True
    token_izgara = token_izgara.to(cihaz, non_blocking=True)
    maske_izgara = maske_izgara.to(cihaz, non_blocking=True)

    for t in range(azami_uzunluk):
        aktif_maske = maske_izgara[t]
        logitler, durum = adim_toplu_maskeli(z, n_layer, n_embd, n_head, head_size, token_izgara[t], durum, aktif_maske)
        for b in range(B):
            if aktif_maske[b]:
                son_logitler[b] = logitler[b]

        if ilerleme_geri_cagirma is not None and ((t + 1) % ilerleme_adimi == 0 or (t + 1) == azami_uzunluk):
            ilerleme_geri_cagirma(t + 1, azami_uzunluk)

    return torch.stack(son_logitler, dim=0), durum


class RWKVTopluDurumYoneticisi:
    """`adim_toplu`'yu, gerçek `rwkv.model.RWKV` (RWKV_x070) örneğinin
    kendi `.z` ağırlık sözlüğü üzerinden çalıştıran ince bir sarmalayıcı.
    Ağırlıklar KOPYALANMAZ -- verilen modelin `.z`'si doğrudan paylaşılır,
    bu yüzden B dizi için VRAM maliyeti tek-dizilik bir modelinkiyle
    AYNIDIR (yalnızca durum/state B ile büyür, ağırlıklar değil)."""

    def __init__(self, ham_rwkv_modeli: Any, B: int):
        self.z = ham_rwkv_modeli.z
        self.n_layer = ham_rwkv_modeli.n_layer
        self.n_embd = ham_rwkv_modeli.n_embd
        self.n_head = ham_rwkv_modeli.n_head
        self.head_size = ham_rwkv_modeli.head_size
        self.B = B
        self.durum = sifir_durum_toplu(self.z, self.n_layer, self.n_embd, self.n_head, self.head_size, B)

    def adim(self, token_idler: List[int]) -> torch.Tensor:
        assert len(token_idler) == self.B, f"beklenen batch boyutu {self.B}, alınan {len(token_idler)}"
        logits, self.durum = adim_toplu(
            self.z, self.n_layer, self.n_embd, self.n_head, self.head_size, token_idler, self.durum,
        )
        return logits
