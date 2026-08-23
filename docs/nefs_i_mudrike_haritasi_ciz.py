"""
docs/nefs_i_mudrike_mimarisi.tex dosyasinin sonundaki "VAKIA-I IDRAK VE
INSANI SEBEKE (41 MELEKENIN KOPUKSUZ GIRDI-CIKTI MANIFOLDU)" bolumunu
DOGRUDAN LaTeX kaynagindan ayristirip (regex ile, elle transkripsiyon
YAPILMADAN -- 41 dugum x ~5-11 kenar, elle kopyalamak hataya acik olurdu)
bir yonlendirilmis cizge (DiGraph) olarak insa eder ve iki ayri gorsel
uretir:

  1) nefs_i_mudrike_haritasi_tam.png     -- 41 melekenin TAMAMI, guclu
     baglanti bilesenlerine gore renklendirilmis, yaylanma (spring)
     duzeniyle.
  2) nefs_i_mudrike_haritasi_cekirdek.png -- yalnizca en yuksek dereceli
     (en cok baglantili) 12 melekeyi ve aralarindaki kenarlari gosteren,
     okunakli bir "cekirdek" alt-cizge (41 dugumlu tam grafik gorsel
     olarak asiri kalabalik oldugu icin ayrica).

Sistemin KENDI iddia ettigi "Talim/Tahsil halkasi" (sona -- basa donen
kapanma) da metinden ayrica ayristirilip cizgeye eklenir.
"""
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

TEX_YOLU = Path(__file__).parent / "nefs_i_mudrike_mimarisi.tex"


def _latex_temizle(metin: str) -> str:
    """LaTeX kacis dizilerini (\\c{s} -> s, \\u{g} -> g, \\^{i} -> i vb.)
    ve \\mathcal{...} gibi matematik sarmalayicilarini temizleyip okunur
    duz metne cevirir."""
    metin = re.sub(r"\\mathcal\{([^}]*)\}", r"\1", metin)
    metin = re.sub(r"\\bm\{([^}]*)\}", r"\1", metin)
    metin = re.sub(r"\\[a-zA-Z]\{([^}]*)\}", r"\1", metin)  # \c{s}, \u{g}, \^{i} vb.
    metin = metin.replace("\\", "")
    return metin.strip()


def _agi_ayristir() -> nx.DiGraph:
    metin = TEX_YOLU.read_text(encoding="utf-8")

    baslangic = metin.index("VÂKIA-İ İDRAK VE İNSANÎ ŞEBEKE")
    bitis = metin.index("Sistemik Kapanış: Talim ve Tahsil Halkası")
    govde = metin[baslangic:bitis]
    kapanis = metin[bitis:bitis + 900]

    # Her dugum: "N. MelekeAdi\n * Girdiler (\leftarrow): a, b, c\n * Ciktilar (\rightarrow): d, e, f"
    dugum_deseni = re.compile(
        r"^\d+\.\s+(?P<ad>[^\n]+?)\s*\n"
        r"\s*\*?\s*Girdiler[^:]*:\s*(?P<girdiler>[^\n]+)\n"
        r"\s*\*?\s*Çıktılar[^:]*:\s*(?P<ciktilar>[^\n]+)",
        re.MULTILINE,
    )

    G = nx.DiGraph()
    for eslesme in dugum_deseni.finditer(govde):
        ad = _latex_temizle(eslesme.group("ad"))
        G.add_node(ad)
        ciktilar = [_latex_temizle(x) for x in eslesme.group("ciktilar").split(",")]
        for hedef in ciktilar:
            hedef = hedef.strip()
            if hedef:
                G.add_edge(ad, hedef)
        # Girdiler de -- kaynak dugum bu listede bir "melekeler dısı" oge
        # (ör. "Dış Âlem Hadiseleri") olabilir; yine de dahil ediyoruz,
        # cizgenin GERCEK tum girdi kaynaklarini gostersin diye.
        girdiler = [_latex_temizle(x) for x in eslesme.group("girdiler").split(",")]
        for kaynak in girdiler:
            kaynak = kaynak.strip()
            if kaynak:
                G.add_edge(kaynak, ad)

    # Kapanis halkasi (Talim/Tahsil) -- ayni dugum-deseniyle, biraz farkli
    # girinti/madde isaretiyle yazilmis, ayri ayristiriliyor.
    kapanis_deseni = re.compile(
        r"(?P<ad>Talim|Tahsil)\s*\n"
        r"\s*\*?\s*Girdiler[^:]*:\s*(?P<girdiler>[^\n]+)\n"
        r"\s*\*?\s*Çıktılar[^:]*:\s*(?P<ciktilar>[^\n]+)",
        re.MULTILINE,
    )
    for eslesme in kapanis_deseni.finditer(kapanis):
        ad = eslesme.group("ad")
        G.add_node(ad)
        for hedef in eslesme.group("ciktilar").split(","):
            hedef = _latex_temizle(hedef).strip()
            if hedef and "Zâtî Melekeleşme" not in hedef:
                G.add_edge(ad, hedef)
        for kaynak in eslesme.group("girdiler").split(","):
            kaynak = _latex_temizle(kaynak).strip()
            if kaynak:
                G.add_edge(kaynak, ad)

    return G


def _tam_haritayi_ciz(G: nx.DiGraph, cikti_yolu: Path) -> None:
    fig, ax = plt.subplots(figsize=(22, 22))
    pos = nx.spring_layout(G, k=0.9, iterations=200, seed=7)

    dereceler = dict(G.degree())
    boyutlar = [300 + dereceler[n] * 90 for n in G.nodes()]

    # Guclu baglanti bilesenlerine (SCC) gore renklendir -- "41 melekenin
    # KOPUKSUZ [birbirine donen] sebeke" iddiasini gorsel olarak da
    # dogrulamak/sinamak icin: gercekten TEK bir buyuk SCC mi olusuyor,
    # yoksa kopuk adacıklar mi var?
    sccler = list(nx.strongly_connected_components(G))
    sccler.sort(key=len, reverse=True)
    renk_haritasi = {}
    renkler = plt.cm.tab20(range(20))
    for i, bilesen in enumerate(sccler):
        for dugum in bilesen:
            renk_haritasi[dugum] = renkler[i % 20] if len(bilesen) > 1 else (0.75, 0.75, 0.75, 1.0)
    dugum_renkleri = [renk_haritasi[n] for n in G.nodes()]

    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.25, arrows=True, arrowsize=8, width=0.6, connectionstyle="arc3,rad=0.05")
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=boyutlar, node_color=dugum_renkleri, edgecolors="black", linewidths=0.5)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=8, font_family="DejaVu Sans")

    en_buyuk_scc_boyutu = len(sccler[0]) if sccler else 0
    ax.set_title(
        f"Nefs-i Müdrike Mimarisi -- 41 Meleke Girdi/Çıktı Şebekesi\n"
        f"{G.number_of_nodes()} düğüm, {G.number_of_edges()} kenar -- "
        f"en büyük güçlü-bağlantı bileşeni: {en_buyuk_scc_boyutu} düğüm "
        f"({'TEK bir kopuksuz çekirdek' if en_buyuk_scc_boyutu > G.number_of_nodes() * 0.7 else 'BEKLENENDEN DAĞINIK'})",
        fontsize=13,
    )
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(cikti_yolu, dpi=160)
    plt.close(fig)


def _cekirdek_haritayi_ciz(G: nx.DiGraph, cikti_yolu: Path, n: int = 12) -> None:
    dereceler = dict(G.degree())
    en_yuksek = sorted(dereceler, key=dereceler.get, reverse=True)[:n]
    alt_G = G.subgraph(en_yuksek).copy()

    fig, ax = plt.subplots(figsize=(13, 13))
    pos = nx.circular_layout(alt_G)
    boyutlar = [800 + dereceler[n_] * 60 for n_ in alt_G.nodes()]

    nx.draw_networkx_edges(alt_G, pos, ax=ax, alpha=0.5, arrows=True, arrowsize=14, width=1.1,
                            connectionstyle="arc3,rad=0.12", node_size=boyutlar)
    nx.draw_networkx_nodes(alt_G, pos, ax=ax, node_size=boyutlar, node_color="#f4a261", edgecolors="black")
    nx.draw_networkx_labels(alt_G, pos, ax=ax, font_size=11, font_weight="bold")

    ax.set_title(
        f"Nefs-i Müdrike Mimarisi -- En Yüksek Dereceli {n} Meleke (Çekirdek Şebeke)",
        fontsize=14,
    )
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(cikti_yolu, dpi=160)
    plt.close(fig)


def main() -> None:
    G = _agi_ayristir()
    print(f"[nefs_i_mudrike_haritasi_ciz] Ayrıştırılan şebeke: {G.number_of_nodes()} düğüm, {G.number_of_edges()} kenar.")

    if G.number_of_nodes() < 30:
        print(
            f"[nefs_i_mudrike_haritasi_ciz] UYARI: yalnızca {G.number_of_nodes()} düğüm bulundu, "
            f"metin 41 meleke iddia ediyordu -- regex deseni dosyanın gerçek biçimiyle TAM eşleşmemiş "
            f"olabilir, çıktıyı EKSİK kabul edip kontrol edin.",
            file=sys.stderr,
        )

    cikti_dizini = Path(__file__).parent
    _tam_haritayi_ciz(G, cikti_dizini / "nefs_i_mudrike_haritasi_tam.png")
    _cekirdek_haritayi_ciz(G, cikti_dizini / "nefs_i_mudrike_haritasi_cekirdek.png")
    print("[nefs_i_mudrike_haritasi_ciz] İki görsel de yazıldı: nefs_i_mudrike_haritasi_tam.png, nefs_i_mudrike_haritasi_cekirdek.png")


if __name__ == "__main__":
    main()
