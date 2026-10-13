import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Wedge
import os
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
fig, ax = plt.subplots(figsize=(7.2, 3.9)); ax.set_xlim(-6, 6); ax.set_ylim(-3.4, 3.4); ax.axis("off"); ax.set_aspect("equal")
ax.add_patch(Rectangle((-1.5, -2.2), 3, 4.4, fc="#2b2b2b", ec="k")); ax.add_patch(Wedge((0, 2.2), 0.45, 180, 360, fc="#e9e9e9", ec="k"))
ax.text(0, 0, "µA741", color="white", ha="center", va="center", fontsize=13, fontweight="bold", rotation=90)
L = [("1", "OFFSET N1 / NC", ""), ("2", "IN−", "evirmeyen giriş"), ("3", "IN+", "evirmeyen olmayan giriş".replace("evirmeyen olmayan", "evirmeyen")), ("4", "VCC−", "negatif besleme")]
R = [("8", "NC", "bağlantı yok"), ("7", "VCC+", "pozitif besleme"), ("6", "OUT", "çıkış"), ("5", "OFFSET N2 / NC", "")]
L[1] = ("2", "IN−", "eviren giriş"); L[2] = ("3", "IN+", "evirmeyen giriş")
for i, (n, nm, ds) in enumerate(L):
    y = 1.65 - i * 1.1
    ax.add_patch(Rectangle((-2.3, y - 0.12), 0.8, 0.24, fc="#c0c0c0", ec="#777")); ax.text(-1.2, y, n, color="white", ha="center", va="center", fontsize=9)
    ax.text(-2.45, y + 0.02, nm + ("\n" + ds if ds else ""), ha="right", va="center", fontsize=9.5)
for i, (n, nm, ds) in enumerate(R):
    y = 1.65 - i * 1.1
    ax.add_patch(Rectangle((1.5, y - 0.12), 0.8, 0.24, fc="#c0c0c0", ec="#777")); ax.text(1.2, y, n, color="white", ha="center", va="center", fontsize=9)
    ax.text(2.45, y + 0.02, nm + ("\n" + ds if ds else ""), ha="left", va="center", fontsize=9.5)
ax.text(0, -2.95, "Üstten görünüş (çentik yukarıda). Kaynak: TI, SLOS094H, Tablo 4-1 ve 4-2", ha="center", fontsize=8.5, color="#444")
fig.tight_layout(); fig.savefig(os.path.join(A, "pinout.png"), dpi=200)
