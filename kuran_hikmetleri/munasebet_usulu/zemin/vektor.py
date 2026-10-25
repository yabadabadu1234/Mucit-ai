import os
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "Qwen/Qwen3.5-0.8B"
PENCERE = 2048
ADIM = 1536
KOMSU = PENCERE - ADIM
ONBELLEK = Path(__file__).resolve().parents[2] / ".hf_cache" / "zemin"


class Zemin:
    def __init__(self):
        torch.set_num_threads(os.cpu_count())
        self.tok = AutoTokenizer.from_pretrained(MODEL)
        self.model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float32).eval()
        self.bas = self.tok.convert_tokens_to_ids("<|endoftext|>")

    def token_vektorleri(self):
        return self.model.get_input_embeddings().weight.detach()

    def _hidden(self, ids):
        with torch.no_grad():
            return self.model.model(input_ids=ids.unsqueeze(0)).last_hidden_state[0]

    def _logp(self, hidden, hedef):
        with torch.no_grad():
            lp = []
            for i in range(0, hidden.shape[0], 256):
                z = self.model.lm_head(hidden[i:i + 256])
                lp.append(torch.log_softmax(z, dim=-1).gather(1, hedef[i:i + 256].unsqueeze(1))[:, 0])
            return torch.cat(lp)

    def tara(self, ids):
        """ids: 1-boyutlu token dizisi (başında bas yok). Dönen: her token için -log p (nats) ve gizli vektör (bağlam)."""
        girdi = torch.cat([torch.tensor([self.bas]), ids])
        n = girdi.shape[0]
        surp = np.zeros(n - 1, dtype=np.float32)
        gizli = np.zeros((n - 1, self.model.config.hidden_size), dtype=np.float32)
        bas = 0
        while True:
            son = min(bas + PENCERE, n)
            h = self._hidden(girdi[bas:son])
            ilk = 0 if bas == 0 else KOMSU
            hed = girdi[bas + 1:son]
            lp = self._logp(h[:-1], hed)
            for j in range(max(ilk, 0), son - bas - 1):
                surp[bas + j] = -lp[j].item()
                gizli[bas + j] = h[j + 1].numpy()
            if son == n:
                break
            bas += ADIM
        return surp, gizli

    def sure(self, ayet_listesi):
        """ayet_listesi: [(ayet_no, [kelime,...])]. Dönen: kelime başına yüzey (nats), ayet sınırları, ayet sonu gizli vektörü."""
        metin = ""
        kelime_bas = []
        kelime_ayet = []
        for a, kel in ayet_listesi:
            for k in kel:
                kelime_bas.append((len(metin), len(metin) + len(k)))
                kelime_ayet.append(a)
                metin += k + " "
            metin = metin[:-1] + "\n"
        enc = self.tok(metin, return_offsets_mapping=True, add_special_tokens=False)
        ids = torch.tensor(enc["input_ids"])
        off = enc["offset_mapping"]
        surp, gizli = self.tara(ids)
        kel_surp = np.zeros(len(kelime_bas), dtype=np.float32)
        kel_tok = np.zeros(len(kelime_bas), dtype=np.int32)
        kel_gizli = np.zeros((len(kelime_bas), gizli.shape[1]), dtype=np.float32)
        w = 0
        for t, (b, e) in enumerate(off):
            while w < len(kelime_bas) and b >= kelime_bas[w][1]:
                w += 1
            if w >= len(kelime_bas):
                break
            if e > kelime_bas[w][0]:
                kel_surp[w] += surp[t]
                kel_tok[w] += 1
                kel_gizli[w] = gizli[t]
        return np.array(kelime_ayet), kel_surp, kel_tok, kel_gizli


def _ek(self):
    pass


def loglik(self, onek, metin):
    """log p(metin | onek), nats; onek '' ise yalnız başlangıç belirteci."""
    a = torch.tensor(self.tok(onek, add_special_tokens=False)["input_ids"], dtype=torch.long) if onek else torch.tensor([], dtype=torch.long)
    b = torch.tensor(self.tok(metin, add_special_tokens=False)["input_ids"], dtype=torch.long)
    girdi = torch.cat([torch.tensor([self.bas]), a, b])
    h = self._hidden(girdi)
    lp = self._logp(h[:-1], girdi[1:])
    return float(lp[len(a):].sum())


Zemin.loglik = loglik
