import re
import torch
import torch.nn as nn

AYAR = {
    "boyut": 50,
    "hafiza": 50,
    "devir": 20,
    "parti": 64,
    "oran": 0.005,
    "tohum": 1453,
}

SEMA_ANAHTARLARI = ("hifz", "terkip", "kip_zaman")


def ayristir(yol):
    hikaye, ornekler = [], []
    for satir in open(yol, encoding="utf-8"):
        no, metin = satir.rstrip("\n").split(" ", 1)
        if int(no) == 1:
            hikaye = []
        if "\t" in metin:
            soru, cevap = metin.split("\t")[:2]
            ornekler.append((list(hikaye), kelimeler(soru), cevap))
        else:
            hikaye.append(kelimeler(metin))
    return ornekler


def kelimeler(c):
    return [w for w in re.findall(r"[a-z]+", c.lower())]


class Sozluk:
    def __init__(self, ornekler):
        self.k = {"<bos>": 0}
        self.c = {}
        for h, s, a in ornekler:
            for w in [x for c in h for x in c] + s:
                self.k.setdefault(w, len(self.k))
            self.c.setdefault(a, len(self.c))

    def kelime(self, w):
        return self.k.get(w, 0)


def tensorle(ornekler, sz, hafiza, uzun):
    n = len(ornekler)
    H = torch.zeros(n, hafiza, uzun, dtype=torch.long)
    Q = torch.zeros(n, uzun, dtype=torch.long)
    Y = torch.full((n,), -1, dtype=torch.long)
    for i, (h, s, a) in enumerate(ornekler):
        h = h[-hafiza:]
        for j, c in enumerate(h):
            for t, w in enumerate(c[:uzun]):
                H[i, hafiza - len(h) + j, t] = sz.kelime(w)
        for t, w in enumerate(s[:uzun]):
            Q[i, t] = sz.kelime(w)
        Y[i] = sz.c.get(a, -1)
    return H, Q, Y


class Cozucu(nn.Module):
    def __init__(self, v, cevap, sema):
        super().__init__()
        d, m = AYAR["boyut"], AYAR["hafiza"]
        self.sema = sema
        self.adim = 3 if sema["terkip"] else 1
        self.E = nn.ModuleList([nn.Embedding(v, d, padding_idx=0) for _ in range(self.adim + 1)])
        self.T = nn.ParameterList([nn.Parameter(torch.randn(m, d) * 0.1) for _ in range(self.adim + 1)])
        self.W = nn.Linear(d, cevap, bias=False)

    def konum(self, x, uzun):
        d = AYAR["boyut"]
        j = torch.arange(1, uzun + 1).float().unsqueeze(1)
        k = torch.arange(1, d + 1).float().unsqueeze(0)
        return (1 - j / uzun) - (k / d) * (1 - 2 * j / uzun)

    def cumle(self, E, x):
        L = self.konum(x, x.shape[-1])
        return (E(x) * L).sum(-2)

    def forward(self, H, Q):
        u = self.cumle(self.E[0], Q)
        if not self.sema["hifz"]:
            torba = self.cumle(self.E[0], H.flatten(1, 2).unsqueeze(1)).squeeze(1)
            return self.W(u + torba)
        dolu = (H.sum(-1) > 0).float()
        for k in range(self.adim):
            A = self.cumle(self.E[k], H)
            C = self.cumle(self.E[k + 1], H)
            if self.sema["kip_zaman"]:
                A = A + self.T[k]
                C = C + self.T[k + 1]
            p = (A @ u.unsqueeze(-1)).squeeze(-1)
            p = p.masked_fill(dolu == 0, -1e9).softmax(-1)
            u = u + (p.unsqueeze(-1) * C).sum(1)
        return self.W(u)


def egit(tren, sema, gunluk):
    torch.manual_seed(AYAR["tohum"])
    sz = Sozluk(tren)
    uzun = max(max([len(c) for h, _, _ in tren for c in h] + [1]), max(len(s) for _, s, _ in tren))
    H, Q, Y = tensorle(tren, sz, AYAR["hafiza"], uzun)
    model = Cozucu(len(sz.k), len(sz.c), sema)
    opt = torch.optim.Adam(model.parameters(), lr=AYAR["oran"])
    n = len(Y)
    for devir in range(AYAR["devir"]):
        sira = torch.randperm(n)
        top = 0.0
        for b in range(0, n, AYAR["parti"]):
            i = sira[b:b + AYAR["parti"]]
            kayip = nn.functional.cross_entropy(model(H[i], Q[i]), Y[i])
            opt.zero_grad()
            kayip.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 40.0)
            opt.step()
            top += kayip.item() * len(i)
        gunluk("devir %d kayip %.4f" % (devir + 1, top / n))
    return model, sz, uzun


def cevapla(model, sz, uzun, ornekler):
    H, Q, Y = tensorle(ornekler, sz, AYAR["hafiza"], uzun)
    ters = {v: k for k, v in sz.c.items()}
    with torch.no_grad():
        tahmin = torch.cat([model(H[b:b + 512], Q[b:b + 512]).argmax(-1) for b in range(0, len(Y), 512)])
    return [ters[int(t)] for t in tahmin]
