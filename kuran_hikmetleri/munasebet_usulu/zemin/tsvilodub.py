import numpy as np


def softmax(x):
    e = np.exp(x - np.max(x))
    return e / e.sum()


def lojistik(x):
    return 1.0 / (1.0 + np.exp(-x))


def karar(P, U, alfa, tau, c):
    """P: maksat ihtimalleri (G,), U: fayda (G,R). Dönen: π(r), r*, beklenen pişmanlık, P(r_cq), P(r)."""
    EU = P @ U
    pi = softmax(alfa * EU)
    r = int(np.argmax(pi))
    pismanlik = U.max(axis=1) - U[:, r]
    ep = float(P @ pismanlik)
    pcq = float(lojistik(tau * (ep - c)))
    return pi, r, ep, pcq, (1 - pcq) * pi


def bar(eps, delta):
    P = np.array([1 - eps, eps])
    U = np.array([[1.0, 0.0, 1 - delta], [0.0, 1.0, 1 - delta]])
    return P, U


if __name__ == "__main__":
    for eps, delta in ((0.17, 0.32), (0.49, 0.32), (0.49, 0.11)):
        P, U = bar(eps, delta)
        pi, r, ep, pcq, _ = karar(P, U, 5.0, 3.6, 0.18)
        print(eps, delta, "r*", r, "ExpRegret", round(ep, 2), "P(r_cq)", round(pcq, 3))
