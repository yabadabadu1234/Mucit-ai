#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kur'an-ı Kerim Sureleri ve Hikmetleri - Otomatik Belge ve PDF Derleyici
Bu betik:
1. 'derleme_yapilandirma.json' içinde işaret edilen dosyaları ve grafikleri uygun sırayla uç uca ekler.
2. Grafiklerin ekran görüntülerini (tertip ve nüzul cetvelleri, sure kesitleri) otomatik olarak araya yerleştirir.
3. Her sure için ayet seviyesinde pencereli mevzu haritasını kitaba ekler.
4. Google Chrome headless kullanarak otomatik olarak baskı kalitesinde PDF üretir.
5. '--watch' seçeneği ile çalıştırıldığında kaynak dosyalardaki her değişiklikte derlemeyi otomatik yeniler.
"""

import os
import re
import sys
import time
import json
import argparse
import subprocess
from pathlib import Path

try:
    import markdown
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "markdown"], check=True)
    import markdown

from grafik_uretici import build_all_charts, load_all_surah_data
import kelime_mealli

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent
CONFIG_PATH = BASE_DIR / "derleme_yapilandirma.json"


def get_markdown_converter():
    return markdown.Markdown(extensions=[
        "tables",
        "fenced_code",
        "toc",
        "nl2br"
    ])


def _ayet_metni(verse_dict, v):
    """Âyet Arapça ve Türkçe metnini sure JSON'undan (verse_dict) otomatik okur."""
    vobj = verse_dict.get(v, {})
    t = vobj.get("turkish", {})
    return vobj.get("arabic", ""), t.get("diyanet_vakfi") or t.get("hayrat_nesriyat") or ""


def flat_segment_tablosu(segments):
    """Sade tablo: Mevzu / Fasıl | Âyet Aralığı | Âyet Sayısı | Açıklama (üstte, değişmeden)."""
    seg_rows = []
    for seg in segments:
        seg_rows.append(f"""
                        <tr>
                          <td style="width:12px; background:{seg['color']};"></td>
                          <td><strong>{seg['title']}</strong></td>
                          <td>Âyet {seg['start']} - {seg['end']}</td>
                          <td>{seg['count']} âyet</td>
                          <td style="font-size:9pt; color:#64748b;">{seg['desc']}</td>
                        </tr>
                        """)
    return f"""
                    <table class="segments-table">
                      <thead>
                        <tr>
                          <th></th>
                          <th>Mevzu / Fasıl</th>
                          <th>Âyet Aralığı</th>
                          <th>Âyet Sayısı</th>
                          <th>Açıklama</th>
                        </tr>
                      </thead>
                      <tbody>
                        {"".join(seg_rows)}
                      </tbody>
                    </table>
                    """


KELIME_RENKLERI = ["#dc2626", "#2563eb", "#16a34a", "#9333ea", "#ea580c",
                   "#0891b2", "#be185d", "#ca8a04", "#4f46e5", "#0d9488"]


def _kelime_mealli(verse_dict, v):
    """Âyetin kelime mealli satırı: her kelime ayrı renkte; altında Türkçe karşılığı."""
    kelimeler = verse_dict.get(v, {}).get("kelimeler", [])
    if not kelimeler:
        return ""
    parcalar = []
    for i, k in enumerate(kelimeler):
        renk = KELIME_RENKLERI[i % len(KELIME_RENKLERI)]
        parcalar.append(
            f'<span class="kelime" style="border-bottom:3px solid {renk};" title="{k["lem"]}">'
            f'<span class="kelime-ar" style="color:{renk};">{k["ar"]}</span>'
            f'<span class="kelime-tr">{k["tr"] or "—"}</span></span>'
        )
    return f'<div class="kelime-satiri">{"".join(parcalar)}</div>'


def _kart(renk, v, etiket, verse_dict):
    ar, tr = _ayet_metni(verse_dict, v)
    return (
        f'<div class="ag-kart" style="border-top:4px solid {renk};">'
        f'<div class="ag-kart-baslik" style="color:{renk};">Âyet {v}{" · " + etiket if etiket else ""}</div>'
        f'<div class="verse-ar">{ar}</div>{_kelime_mealli(verse_dict, v)}'
        f'<div class="verse-tr">{tr}</div></div>'
    )


def _yaprak_sayisi(x):
    if x.get("alt"):
        return sum(_yaprak_sayisi(c) for c in x["alt"])
    a, b = x["aralik"]
    return b - a + 1


def _baslik_kutusu(x, renk):
    a, b = x["aralik"]
    return (
        f'<div class="ag-sutun-baslik" style="background:{renk};">{x["baslik"]} '
        f'<small>(Âyet {a}{"-" + str(b) if a != b else ""} · {_yaprak_sayisi(x)} âyet)</small></div>'
    )


def _yatay_satir(dugumler, renk, verse_dict):
    """Mevzu ağacını yatay satır olarak dizer. Alt mevzusu olan düğüm, altındaki yatay satırla bir sütun olur.
    Alt mevzusu olmayan yapraklar ardışık olarak tek bir dikey âyet sütununda toplanır."""
    sutunlar = []
    yaprak_grubu = []

    def grubu_bosalt():
        if yaprak_grubu:
            sayi = sum(_yaprak_sayisi(y) for y in yaprak_grubu)
            kartlar = "".join(_kart(renk, y["aralik"][0], y["baslik"], verse_dict) for y in yaprak_grubu)
            sutunlar.append(
                f'<div class="ag-sutun" style="flex-grow:{sayi};">'
                f'<div class="ag-kart-stack">{kartlar}</div></div>'
            )
            yaprak_grubu.clear()

    for x in dugumler:
        if x.get("alt"):
            grubu_bosalt()
            sutunlar.append(
                f'<div class="ag-sutun" style="flex-grow:{_yaprak_sayisi(x)};">'
                f'{_baslik_kutusu(x, renk)}{_yatay_satir(x["alt"], renk, verse_dict)}</div>'
            )
        else:
            yaprak_grubu.append(x)
    grubu_bosalt()
    return f'<div class="ag-yatay">{"".join(sutunlar)}</div>'


def _yumak_kutusu(x, renk):
    a, b = x["aralik"]
    return (
        f'<div class="ag-yumak-kutu" style="border-top:4px solid {renk};">'
        f'<strong>{x["baslik"]}</strong>'
        f'<div class="ag-meta">Âyet {a}{"-" + str(b) if a != b else ""} · {_yaprak_sayisi(x)} âyet</div></div>'
    )


def _yumak_satiri(dugumler, renk):
    """Sadece mevzu ağacını yatay dizer; âyet metni içermez."""
    sutunlar = []
    for x in dugumler:
        alt = _yumak_satiri(x["alt"], renk) if x.get("alt") else ""
        sutunlar.append(
            f'<div class="ag-sutun" style="flex-grow:{_yaprak_sayisi(x)};">'
            f'{_yumak_kutusu(x, renk)}{alt}</div>'
        )
    return f'<div class="ag-yatay">{"".join(sutunlar)}</div>'


def mevzu_yumagi(segments, agac_segmentler):
    """Sûreye mahsus tek yumak: bütün segmentler yan yana, her birinin altında kendi mevzu ağacı.
    Âyet metni içermez. Sütun genişliği segmentin âyet sayısına göre orantılıdır."""
    sutunlar = []
    for seg in segments:
        renk = seg["color"]
        anahtar = f"{seg['start']}-{seg['end']}"
        govde = _yumak_satiri(agac_segmentler[anahtar], renk) if anahtar in agac_segmentler else ""
        sutunlar.append(
            f'<div class="ag-sutun" style="flex-grow:{seg["count"]};">'
            f'<div class="ag-yumak-kutu" style="border-top:4px solid {renk};">'
            f'<strong>{seg["title"]}</strong>'
            f'<div class="ag-meta">Âyet {seg["start"]} - {seg["end"]} · {seg["count"]} âyet</div></div>'
            f'{govde}</div>'
        )
    return f'<div class="ag-yatay">{"".join(sutunlar)}</div>'


def _derinlik(x):
    return 1 if not x.get("alt") else 1 + max(_derinlik(c) for c in x["alt"])


def _cetvel_hucreleri(x, satir, son_satir, renk, cells):
    """Düğümü cetvelde yerleştirir: sütunlar âyet numarası, satırlar mevzu düzeyi.
    Alt mevzusu olan düğüm kendi satırına oturur; yaprak en alt satıra kadar uzanır."""
    a, b = x["aralik"]
    if x.get("alt"):
        cells.append(
            f'<div class="ag-hucre" style="grid-column:{a}/{b + 1}; grid-row:{satir};'
            f' border-top:4px solid {renk};"><strong>{x["baslik"]}</strong>'
            f'<div class="ag-meta">Âyet {a}{"-" + str(b) if a != b else ""}</div></div>'
        )
        for c in x["alt"]:
            _cetvel_hucreleri(c, satir + 1, son_satir, renk, cells)
    else:
        cells.append(
            f'<div class="ag-hucre ag-yaprak" style="grid-column:{a}/{b + 1}; grid-row:{satir}/{son_satir + 1};'
            f' border-top:4px solid {renk};" title="{x["baslik"]}">'
            f'<div class="ag-meta">Âyet {a}{"-" + str(b) if a != b else ""}</div>'
            f'<strong>{x["baslik"]}</strong></div>'
        )


def mevzu_cetveli(segments, agac_segmentler):
    """Sûreye mahsus cetvel: genel mevzular üst satırda yan yana, alt düzeyler altta; genişlik âyet sayısıyla orantılı.
    Her âyet bir sütundur, bu yüzden bütün sûre tek bir ızgarada hizalanır. Âyet metni içermez."""
    ilk = min(seg["start"] for seg in segments)
    son = max(seg["end"] for seg in segments)
    sutun_sayisi = son - ilk + 1
    dugumler = []
    for seg in segments:
        anahtar = f"{seg['start']}-{seg['end']}"
        alt = agac_segmentler.get(anahtar)
        dugumler.append((seg, {"baslik": seg["title"], "aralik": [seg["start"], seg["end"]], "alt": alt} if alt else
                         {"baslik": seg["title"], "aralik": [seg["start"], seg["end"]]}))
    satir_sayisi = max(_derinlik(d) for _, d in dugumler)
    cells = []
    for seg, d in dugumler:
        _cetvel_hucreleri(d, 1, satir_sayisi, seg["color"], cells)
    # Izgara koordinatları sûrenin ilk âyetine göre kaydırılır
    cells_html = "".join(cells)
    if ilk != 1:
        cells_html = re.sub(r'grid-column:(\d+)/(\d+)',
                            lambda m: f"grid-column:{int(m.group(1)) - ilk + 1}/{int(m.group(2)) - ilk + 1}", cells_html)
    return (
        f'<div class="ag-cetvel" style="grid-template-columns: repeat({sutun_sayisi}, minmax(0, 1fr));'
        f' grid-template-rows: repeat({satir_sayisi}, auto);">{cells_html}</div>'
    )


def sure_sutun_grafigi(segments):
    """Sûre taksimatı sütun grafiği: X ekseninde mevzular (tam metin, yatay ve sarmalı), Y ekseninde âyet sayıları."""
    import textwrap
    from html import escape
    n = len(segments)
    slot, bar_w, left, top, plot_h = 150, 60, 110, 30, 220
    satir_kar = 16
    etiketler = []
    for seg in segments:
        etiket = f"{seg['title']} ({seg['start']}-{seg['end']})"
        etiketler.append(textwrap.wrap(etiket, 22) or [etiket])
    en_cok_satir = max(len(e) for e in etiketler)
    maks = max(seg["count"] for seg in segments)
    olcek = plot_h / maks
    genislik = max(700, left + n * slot + 40)
    yukseklik = top + plot_h + 20 + en_cok_satir * satir_kar + 20
    adim = max(1, round(maks / 4))
    parcalar = []
    for deger in range(0, maks + 1, adim):
        y = top + plot_h - deger * olcek
        parcalar.append(f'<line x1="{left}" y1="{y}" x2="{genislik - 20}" y2="{y}" stroke="#e2e8f0" stroke-dasharray="3,3"/>')
        parcalar.append(f'<text x="{left - 8}" y="{y + 4}" font-size="11" text-anchor="end" fill="#64748b">{deger}</text>')
    for i, seg in enumerate(segments):
        x0 = left + i * slot
        merkez = x0 + slot / 2
        h = seg["count"] * olcek
        y = top + plot_h - h
        parcalar.append(
            f'<rect x="{merkez - bar_w / 2}" y="{y}" width="{bar_w}" height="{h}" fill="{seg["color"]}" rx="3">'
            f'<title>{escape(seg["title"])} ({seg["start"]}-{seg["end"]}, {seg["count"]} âyet)</title></rect>'
        )
        parcalar.append(f'<text x="{merkez}" y="{y - 5}" font-size="11" text-anchor="middle" fill="#0f172a">{seg["count"]}</text>')
        satirlar = "".join(
            f'<tspan x="{merkez}" dy="{0 if k == 0 else satir_kar}">{escape(t)}</tspan>'
            for k, t in enumerate(etiketler[i])
        )
        parcalar.append(
            f'<text x="{merkez}" y="{top + plot_h + 22}" font-size="12" text-anchor="middle" fill="#334155">{satirlar}</text>'
        )
    parcalar.append(f'<text x="{left}" y="14" font-size="12" font-weight="700" fill="#1e3a8a">Y: Âyet sayısı</text>')
    parcalar.append(f'<text x="{genislik - 20}" y="14" font-size="12" font-weight="700" text-anchor="end" fill="#1e3a8a">X: Mevzular</text>')
    return (
        f'<div class="sure-sutun-grafik" style="overflow-x:auto;">'
        f'<svg width="{genislik}" height="{yukseklik}" viewBox="0 0 {genislik} {yukseklik}" xmlns="http://www.w3.org/2000/svg">'
        + "".join(parcalar) + "</svg></div>"
    )


def _madde(x):
    """Mevzu düğümünü iç içe madde olarak yazar (md listesi gibi). Yaprak: tek âyet."""
    a, b = x["aralik"]
    aralik = f"Âyet {a}" if a == b else f"Âyet {a}-{b}"
    if x.get("alt"):
        alt = "".join(_madde(c) for c in x["alt"])
        return f"<li><strong>{x['baslik']}</strong> <small>({aralik} · {_yaprak_sayisi(x)} âyet)</small><ul>{alt}</ul></li>"
    return f"<li>{x['baslik']} <small>({aralik})</small></li>"


def mevzu_listesi(segments, agac_segmentler):
    """Sûreye mahsus mevzu listesi: genel mevzu → bölüm → alt bölüm → âyet, iç içe madde listesi."""
    parcalar = []
    for seg in segments:
        anahtar = f"{seg['start']}-{seg['end']}"
        d = {"baslik": seg["title"], "aralik": [seg["start"], seg["end"]]}
        if anahtar in agac_segmentler:
            d["alt"] = agac_segmentler[anahtar]
        parcalar.append(_madde(d))
    return f'<ul class="ag-liste">{"".join(parcalar)}</ul>'


def detay_bolumu(segments, agac_segmentler, verse_dict):
    """Ayrıntılı görünüm: genel mevzu başlığı üstte; altında mevzu ağacı yatay olarak dizilir,
    her mevzunun âyetleri o mevzunun altında dikey sütunlar halinde bağlanır."""
    bloklar = []
    for seg in segments:
        renk = seg["color"]
        anahtar = f"{seg['start']}-{seg['end']}"
        ust = (
            f'<div class="ag-ust" style="border-left:6px solid {renk};">'
            f'<strong>{seg["title"]}</strong>'
            f'<div class="ag-meta">Âyet {seg["start"]} - {seg["end"]} · {seg["count"]} âyet</div>'
            f'<div class="ag-aciklama">{seg["desc"]}</div></div>'
            f'<div class="ag-ok" style="border-left-color:{renk};"></div>'
        )
        if anahtar in agac_segmentler:
            govde = _yatay_satir(agac_segmentler[anahtar], renk, verse_dict)
        else:
            kartlar = "".join(_kart(renk, v, "", verse_dict) for v in range(seg["start"], seg["end"] + 1))
            govde = f'<div class="ag-yatay"><div class="ag-sutun" style="flex-grow:1;"><div class="ag-kart-stack ag-cok-sutun">{kartlar}</div></div></div>'
        bloklar.append(f'<div class="ag-blok">{ust}{govde}</div>')
    return f'<div class="ag-ayrintili">{"".join(bloklar)}</div>'


def build_unified_html(config, surahs_data):
    """Yapılandırmada işaret edilen dosyaları ve grafikleri uygun sırayla uç uca ekleyip tek bir HTML oluşturur."""
    md_conv = get_markdown_converter()
    surah_dict = {s["sno"]: s for s in surahs_data}
    kelimeler = kelime_mealli.yukle()

    body_sections = []

    # Dosya sırasını işle
    for item in config.get("dosya_sirasi", []):
        tur = item.get("tur")

        if tur == "KAPAK":
            cover_html = f"""
            <div class="page cover-page">
              <div class="cover-border">
                <div class="cover-inner">
                  <div class="bismillah">بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ</div>
                  <h1 class="cover-title">{config.get('proje_adi', "Kur'an-ı Kerim Sureleri ve Hikmetleri")}</h1>
                  <div class="cover-divider"></div>
                  <p class="cover-subtitle">{config.get('alt_baslik', '')}</p>
                  
                  <div class="cover-meta-box">
                    <div class="meta-item"><strong>Kapsam:</strong> 114 Sure · 6236 Âyet</div>
                    <div class="meta-item"><strong>Tertip & Nüzul:</strong> Karşılaştırmalı Sütun Cetvelleri</div>
                    <div class="meta-item"><strong>Taksimat:</strong> Mevzu ve Âyet Pencereli Haritalar</div>
                  </div>

                  <div class="cover-footer">
                    <span>Otomatik Derleme Sistemi · MUCİT-AI</span>
                  </div>
                </div>
              </div>
            </div>
            """
            body_sections.append(cover_html)

        elif tur == "GRAFIK_TERTIP":
            img_rel = item.get("dosya", "grafikler/kuran_sureleri_tertip_cetveli.png")
            img_abs = (BASE_DIR / img_rel).resolve().relative_to(BASE_DIR)
            chart_html = f"""
            <div class="page landscape-page">
              <div class="section-title-box">
                <h2>{item.get('baslik', 'Mushaf Tertip Sırasına Göre Sureler Cetveli')}</h2>
                <p>{item.get('aciklama', '')}</p>
              </div>
              <div class="panoramic-img-container">
                <img src="{img_abs}" alt="Tertip Sırası Cetveli" class="panoramic-img" />
              </div>
              <div class="chart-caption">
                <strong>Grafik İzahı:</strong> X ekseni Mushaf tertibindeki 114 sureyi (1. Fatiha'dan 114. Nâs'a kadar) gösterir. Y ekseni surelerin âyet sayılarını (0-286) verir. Sütunlar kendi içlerinde mevzularına ve fasıllarına göre renklendirilmiştir.
              </div>
            </div>
            """
            body_sections.append(chart_html)

        elif tur == "GRAFIK_NUZUL":
            img_rel = item.get("dosya", "grafikler/kuran_sureleri_nuzul_cetveli.png")
            img_abs = (BASE_DIR / img_rel).resolve().relative_to(BASE_DIR)
            chart_html = f"""
            <div class="page landscape-page">
              <div class="section-title-box">
                <h2>{item.get('baslik', 'Nüzul Sırasına Göre Sureler Cetveli')}</h2>
                <p>{item.get('aciklama', '')}</p>
              </div>
              <div class="panoramic-img-container">
                <img src="{img_abs}" alt="Nüzul Sırası Cetveli" class="panoramic-img" />
              </div>
              <div class="chart-caption">
                <strong>Grafik İzahı:</strong> X ekseni kronolojik nüzul sırasını (ilk inen 96. Alak'tan son inen 110. Nasr suresine kadar) gösterir. Y ekseni âyet sayılarını verir. Vahyin iniş sürecindeki sure uzunlukları ve mevzu geçişleri doğrudan izlenebilir.
              </div>
            </div>
            """
            body_sections.append(chart_html)

        elif tur == "FIHRIST":
            fihrist_file = BASE_DIR / item.get("dosya", "00_FIHRIST.md")
            if fihrist_file.exists():
                with open(fihrist_file, "r", encoding="utf-8") as f:
                    fcontent = f.read()
                fihrist_html = md_conv.convert(fcontent)
                body_sections.append(f"""
                <div class="page doc-page">
                  <div class="markdown-content">
                    {fihrist_html}
                  </div>
                </div>
                """)

        elif tur == "SURELER":
            # Tüm sureleri sırayla kitaba ekle
            dahil_ekler = item.get("dahil_edilecek_ekler", ["sure.md", "gayeler-ve-hikmetler.md"])
            sure_grafik_dahil = item.get("sure_grafik_dahil_et", True)

            for sno in range(1, 115):
                matches = list((BASE_DIR / "sureler").glob(f"{sno:03d}-*"))
                if not matches:
                    continue
                sdir = matches[0]
                s_meta = surah_dict.get(sno, {})
                for v in s_meta.get("verses", []):
                    v["kelimeler"] = kelimeler.get((sno, v["verseNumber"]), [])

                sure_elements = []

                # 1. sure.md
                sure_md_file = sdir / "sure.md"
                if sure_md_file.exists():
                    with open(sure_md_file, "r", encoding="utf-8") as f:
                        stext = f.read()
                    md_conv.reset()
                    sure_elements.append(f'<div class="sure-md-block">{md_conv.convert(stext)}</div>')

                # 2. gayeler-ve-hikmetler.md (varsa)
                if "gayeler-ve-hikmetler.md" in dahil_ekler:
                    gayeler_file = sdir / "gayeler-ve-hikmetler.md"
                    if gayeler_file.exists():
                        with open(gayeler_file, "r", encoding="utf-8") as f:
                            gtext = f.read()
                        md_conv.reset()
                        sure_elements.append(f'<div class="gayeler-md-block">{md_conv.convert(gtext)}</div>')

                # 3. Sureye Mahsus Âyet Seviyesinde Pencereli Harita Grafiği
                if sure_grafik_dahil and s_meta:
                    ayet_modu = item.get("ayet_pencereleri_modu", "ozet_ve_harita")
                    segments = s_meta.get("segments", [])
                    
                    # Mevzu ağacı (varsa): anahtar "başlangıç-bitiş" segmentin aralığıdır
                    agac_path = sdir / "mevzu_agaci.json"
                    agac_segmentler = {}
                    if agac_path.exists():
                        with open(agac_path, "r", encoding="utf-8") as f:
                            agac_segmentler = json.load(f).get("segmentler", {})
                    verse_dict_agac = {v["verseNumber"]: v for v in s_meta.get("verses", [])}


                    # Kesit ekran görüntüsü var mı kontrol et
                    kesit_img_path = BASE_DIR / "grafikler" / "sureler" / f"sure_{sno:03d}_kesit.png"
                    kesit_html = ""
                    if kesit_img_path.exists():
                        kesit_html = f"""
                        <div class="sure-kesit-box">
                          <img src="{kesit_img_path.relative_to(BASE_DIR)}" alt="Sure {sno} Kesit Haritası" class="sure-kesit-img" />
                        </div>
                        """

                    # Mevzu tablosu (ağacı olan segmentler alt düzeylerle ve âyet metniyle)
                    seg_table = flat_segment_tablosu(segments)
                    ayrintili = detay_bolumu(segments, agac_segmentler, verse_dict_agac)

                    if ayet_modu == "tam_metin":
                        verse_dict = {v["verseNumber"]: v for v in s_meta.get("verses", [])}
                        verse_blocks = []
                        for seg in segments:
                            v_windows = []
                            for vn in range(seg["start"], seg["end"] + 1):
                                vobj = verse_dict.get(vn, {})
                                v_ar = vobj.get("arabic", "")
                                t_dict = vobj.get("turkish", {})
                                v_tr = t_dict.get("diyanet_vakfi") or t_dict.get("hayrat_nesriyat") or ""
                                v_windows.append(f"""
                                <div class="verse-card" style="border-top: 3px solid {seg['color']};">
                                  <div class="verse-num" style="color:{seg['color']};">Âyet {vn}</div>
                                  <div class="verse-ar">{v_ar}</div>
                                  <div class="verse-tr">{v_tr}</div>
                                </div>
                                """)
                            verse_blocks.append(f"""
                            <div class="topic-box">
                              <div class="topic-banner" style="background:{seg['color']}; color:white;">
                                <strong>{seg['title']}</strong> (Âyet {seg['start']}-{seg['end']} · {seg['count']} âyet)
                              </div>
                              <div class="verses-flow">
                                {"".join(v_windows)}
                              </div>
                            </div>
                            """)
                        detail_content = f'<div class="topics-container">{"".join(verse_blocks)}</div>'
                    else:
                        detail_content = kesit_html + seg_table + '<h4 class="ag-baslik">Mevzuların listesi</h4>' + mevzu_listesi(segments, agac_segmentler) + '<h4 class="ag-baslik">Ayrıntılı görünüm: mevzular ve âyet metinleri</h4>' + ayrintili

                    chart_section_html = f"""
                    <div class="surah-chart-section">
                      <h3 class="chart-heading">S{sno:03d} · {s_meta['name']} Suresi Âyet Taksimatı ve Mevzu Haritası</h3>
                      {sure_sutun_grafigi(segments)}
                      {detail_content}
                      <p style="font-size:9pt; color:#64748b; margin-top:8px;">
                        <em>(Detaylı interaktif harita ve ayet pencereleri için bkz: <code>html_grafikler/sureler/{sno}_detay.html</code>)</em>
                      </p>
                    </div>
                    """
                    sure_elements.append(chart_section_html)

                body_sections.append(f"""
                <div class="page sure-page" id="sure-{sno}">
                  {"".join(sure_elements)}
                </div>
                """)

    kenar_maddeler = "".join(
        f'<a href="#sure-{s["sno"]}" onclick="surelerKapat()">{s["sno"]}. {s["name"]}</a>'
        for s in sorted(surahs_data, key=lambda s: s["sno"])
    )
    kenar_html = (
        '<header class="ust-cubuk">'
        '<button type="button" class="menu-dugme" onclick="menuAc()" aria-label="Menü">&#9776; Menü</button>'
        '<a class="ust-baslik" href="#kitap-basi">Kur\'an Hikmetleri</a>'
        '<span class="ust-bos"></span></header>'
        '<div class="menu-panel" id="menuPanel">'
        '<button type="button" class="menu-sekme" onclick="surelerAc()">Sureler</button>'
        '</div>'
        '<nav class="kenar" id="kenar"><div class="kenar-ust"><span>Sureler</span>'
        '<button type="button" class="kenar-kapat" onclick="surelerKapat()" title="Kapat">&#10005;</button></div>'
        f'{kenar_maddeler}</nav>'
    )

    full_html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<title>{config.get('proje_adi', 'Kur-an Hikmetleri')}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Amiri:wght@400;700&display=swap" rel="stylesheet">
<style>
@page {{
  size: A4 portrait;
  margin: 18mm 15mm 20mm 15mm;
  @bottom-right {{
    content: counter(page);
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 10pt;
    color: #64748b;
  }}
}}
@page landscape-section {{
  size: A4 landscape;
  margin: 12mm;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  padding: 0;
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: #1e293b;
  background: #ffffff;
  line-height: 1.65;
  font-size: 11pt;
}}

.page {{
  page-break-after: always;
  break-after: page;
}}
.landscape-page {{
  page: landscape-section;
  page-break-after: always;
  break-after: page;
  padding: 10px;
}}

/* KAPAK */
.cover-page {{
  height: 98vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #090d16;
  color: #ffffff;
  border-radius: 12px;
}}
.cover-border {{
  width: 90%;
  height: 92%;
  border: 3px double #d97706;
  border-radius: 16px;
  padding: 12px;
}}
.cover-inner {{
  width: 100%;
  height: 100%;
  border: 1px solid rgba(217, 119, 6, 0.4);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px;
}}
.bismillah {{
  font-family: 'Amiri', serif;
  font-size: 32pt;
  color: #fbbf24;
  margin-bottom: 30px;
}}
.cover-title {{
  font-family: 'Cinzel', serif, 'Plus Jakarta Sans';
  font-size: 30pt;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  letter-spacing: 1px;
}}
.cover-divider {{
  width: 120px;
  height: 4px;
  background: linear-gradient(90deg, transparent, #fbbf24, transparent);
  margin: 25px 0;
}}
.cover-subtitle {{
  font-size: 15pt;
  color: #94a3b8;
  max-width: 650px;
  margin: 0 0 40px 0;
}}
.cover-meta-box {{
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid #334155;
  border-radius: 10px;
  padding: 20px 30px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  text-align: left;
  font-size: 11pt;
  color: #cbd5e1;
}}
.cover-footer {{
  margin-top: 50px;
  color: #64748b;
  font-size: 10pt;
  letter-spacing: 2px;
}}

/* PANORAMİK GRAFİKLER */
.section-title-box {{
  text-align: center;
  margin-bottom: 12px;
}}
.section-title-box h2 {{
  font-size: 18pt;
  color: #0f172a;
  margin: 0 0 4px 0;
}}
.section-title-box p {{
  color: #64748b;
  font-size: 10pt;
  margin: 0;
}}
.panoramic-img-container {{
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #090d16;
  border-radius: 10px;
  padding: 10px;
  border: 1px solid #1e293b;
}}
.panoramic-img {{
  max-width: 100%;
  max-height: 150mm;
  object-fit: contain;
}}
.chart-caption {{
  margin-top: 10px;
  padding: 8px 14px;
  background: #f1f5f9;
  border-left: 4px solid #2563eb;
  font-size: 9.5pt;
  color: #334155;
}}

/* SURE VE DOKÜMAN SAYFALARI */
.sure-page, .doc-page {{
  padding: 10px 0;
}}
h1, h2, h3, h4 {{
  color: #0f172a;
  page-break-after: avoid;
}}
h1 {{ font-size: 20pt; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 0; }}
h2 {{ font-size: 14pt; margin-top: 20px; color: #1e3a8a; }}
h3 {{ font-size: 12pt; margin-top: 15px; }}

table {{
  width: 100%;
  border-collapse: collapse;
  margin: 15px 0;
  font-size: 9.5pt;
}}
table, th, td {{
  border: 1px solid #cbd5e1;
}}
th {{
  background: #f8fafc;
  color: #0f172a;
  font-weight: 700;
  padding: 8px 10px;
  text-align: left;
}}
td {{
  padding: 6px 10px;
}}
tr:nth-child(even) {{ background: #f8fafc; }}

/* SURE GRAFİĞİ VE AYET PENCERELERİ */
.surah-chart-section {{
  margin-top: 30px;
  page-break-before: always;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 18px;
}}
.chart-heading {{
  margin: 0 0 12px 0;
  font-size: 13pt;
  color: #1e40af;
}}
.surah-mini-bar {{
  display: flex;
  width: 100%;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}}
.sure-kesit-box {{
  margin: 15px 0;
  text-align: center;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  overflow: hidden;
  background: #090d16;
}}
.sure-kesit-img {{
  max-width: 100%;
  max-height: 120mm;
  object-fit: contain;
}}
.segments-table {{
  width: 100%;
  margin-top: 15px;
}}
.segments-table th {{
  background: #f1f5f9;
  font-size: 9pt;
}}
.segments-table td {{
  font-size: 8.5pt;
}}
.agac-table {{
  width: 100%;
  margin-top: 15px;
  font-size: 8.5pt;
  page-break-inside: auto;
}}
.agac-table th {{
  background: #f1f5f9;
  font-size: 8.5pt;
}}
.agac-table td {{
  vertical-align: top;
  padding: 4px 6px;
}}
.agac-table tr {{
  page-break-inside: avoid;
}}
.agac-table .verse-ar {{
  font-size: 13pt;
}}
.ag-ayrintili {{
  margin-top: 10px;
}}
.ag-baslik {{
  margin: 22px 0 6px 0;
  color: #1e3a8a;
}}
.ag-blok {{
  margin-bottom: 22px;
  page-break-inside: auto;
}}
.ag-ust {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 10pt;
}}
.ag-meta {{
  color: #64748b;
  font-size: 8.5pt;
}}
.ag-aciklama {{
  color: #475569;
  font-size: 8.5pt;
  margin-top: 4px;
}}
.ag-ok {{
  position: relative;
  width: 0;
  height: 22px;
  margin-left: 28px;
  border-left: 3px solid #64748b;
}}
.ag-ok::after {{
  content: "";
  position: absolute;
  left: -8px;
  bottom: -8px;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-top: 10px solid #64748b;
}}
.ag-yatay {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: stretch;
  width: 100%;
}}
.ag-sutun {{
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1 1 170px;
  min-width: 170px;
  overflow-wrap: anywhere;
}}
.ag-sutun-baslik {{
  color: #ffffff;
  font-size: 9pt;
  font-weight: 700;
  padding: 5px 8px;
  border-radius: 5px;
}}
.ag-sutun-baslik small {{
  font-weight: 400;
}}
.ag-kart-stack {{
  display: flex;
  flex-direction: column;
  gap: 6px;
}}
.ag-yumak-kutu {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 6px 8px;
  font-size: 9pt;
}}
.ag-cetvel {{
  display: grid;
  gap: 3px;
  width: 100%;
}}
.ag-hucre {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  padding: 4px 5px;
  font-size: 7.5pt;
  overflow: hidden;
  min-width: 0;
}}
.ag-yaprak {{
  font-size: 6.5pt;
}}
.ag-liste {{
  font-size: 9.5pt;
  line-height: 1.6;
}}
.ag-liste ul {{
  margin: 2px 0 2px 18px;
  padding: 0;
}}
.ag-liste small {{
  color: #64748b;
}}
.ag-cok-sutun {{
  display: block;
  column-count: 4;
  column-gap: 8px;
}}
.ag-cok-sutun .ag-kart {{
  display: inline-block;
  width: 100%;
  margin-bottom: 8px;
}}
.ag-kart {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 6px 8px;
  width: 100%;
  page-break-inside: avoid;
}}
.ag-kart-baslik {{
  font-size: 8.5pt;
  font-weight: 700;
  margin-bottom: 2px;
}}
.ag-kart .verse-ar {{
  font-size: 12pt;
}}
.ag-kart .verse-tr {{
  font-size: 8pt;
}}
.topic-box {{
  margin-bottom: 20px;
}}
.topic-banner {{
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 11pt;
  margin-bottom: 10px;
}}
.verses-flow {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}}
.verse-card {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px 14px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  page-break-inside: avoid;
}}
.verse-num {{
  font-size: 9.5pt;
  font-weight: 700;
  margin-bottom: 4px;
}}
.verse-ar {{
  font-family: 'Amiri', serif;
  font-size: 16pt;
  line-height: 1.8;
  direction: rtl;
  text-align: right;
  color: #0f172a;
  margin-bottom: 8px;
}}
.verse-tr {{
  font-size: 9pt;
  color: #475569;
  line-height: 1.5;
  border-top: 1px dashed #e2e8f0;
  padding-top: 6px;
}}

.ust-cubuk {{
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: #0f172a;
  border-bottom: 1px solid #1e293b;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  z-index: 200;
}}
.menu-dugme {{
  background: #1e293b;
  color: #f8fafc;
  border: 1px solid #334155;
  border-radius: 10px;
  padding: 8px 18px;
  font-size: 13pt;
  font-weight: 700;
  cursor: pointer;
}}
.menu-dugme:hover {{ background: #2563eb; border-color: #3b82f6; }}
.ust-baslik {{
  color: #fbbf24;
  font-size: 15pt;
  font-weight: 800;
  text-decoration: none;
  letter-spacing: 0.5px;
}}
.ust-bos {{ width: 110px; }}
.menu-panel {{
  display: none;
  position: fixed;
  top: 72px;
  left: 16px;
  min-width: 220px;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 10px;
  padding: 8px;
  z-index: 201;
  box-shadow: 0 10px 25px rgba(0,0,0,0.5);
}}
.menu-panel.acik {{ display: block; }}
.menu-sekme {{
  display: block;
  width: 100%;
  text-align: left;
  background: transparent;
  color: #e2e8f0;
  border: none;
  border-radius: 6px;
  padding: 10px 14px;
  font-size: 12pt;
  cursor: pointer;
}}
.menu-sekme:hover {{ background: #1e293b; color: #fff; }}
.kenar {{
  position: fixed;
  top: 64px;
  left: 0;
  bottom: 0;
  width: 270px;
  overflow-y: auto;
  background: #0f172a;
  color: #e2e8f0;
  padding: 12px 10px;
  font-size: 9pt;
  border-right: 1px solid #1e293b;
  z-index: 150;
  transform: translateX(-105%);
  transition: transform 0.2s ease;
  box-shadow: 4px 0 20px rgba(0,0,0,0.4);
}}
.kenar.acik {{ transform: none; }}
.kenar-ust {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 700;
  color: #fbbf24;
  padding: 0 6px 8px 6px;
  border-bottom: 1px solid #1e293b;
  margin-bottom: 6px;
}}
.kenar-kapat {{
  background: transparent;
  color: #e2e8f0;
  border: 1px solid #334155;
  border-radius: 6px;
  cursor: pointer;
  font-size: 22.5pt;
  line-height: 1;
  padding: 2px 12px;
}}
.kenar-kapat:hover {{ background: #1e293b; color: #fff; }}
.kenar a {{
  display: block;
  color: inherit;
  text-decoration: none;
  padding: 3px 6px;
  border-radius: 4px;
  line-height: 1.35;
}}
.kenar a:hover {{
  background: #1e293b;
  color: #ffffff;
}}
body {{ padding-top: 72px; }}
.sure-page, .sure-sutun-grafik, .ag-blok {{ scroll-margin-top: 80px; }}
.kelime-satiri {{
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  direction: rtl;
  margin: 6px 0 8px 0;
}}
.kelime {{
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  padding: 2px 6px 3px 6px;
  background: #f8fafc;
  border-radius: 4px;
  min-width: 0;
}}
.kelime-ar {{
  font-family: 'Amiri', serif;
  font-size: 13pt;
  line-height: 1.6;
}}
.kelime-tr {{
  direction: ltr;
  font-size: 7pt;
  color: #334155;
  text-align: center;
  line-height: 1.2;
}}
@media print {{
  .kenar {{ display: none; }}
  .kitap-govde {{ margin-left: 0; }}
  body {{ background: transparent; }}
  .page {{ page-break-after: always; }}
  .verse-card {{ page-break-inside: avoid; }}
}}
</style>
</head>
<body>
{kenar_html}
<div class="kitap-govde">
<div id="kitap-basi"></div>
{"".join(body_sections)}
</div>
<script>
function menuAc() {{ document.getElementById('menuPanel').classList.toggle('acik'); }}
function surelerAc() {{
  document.getElementById('kenar').classList.add('acik');
  document.getElementById('menuPanel').classList.remove('acik');
}}
function surelerKapat() {{ document.getElementById('kenar').classList.remove('acik'); }}
</script>

</body>
</html>
"""
    return full_html


def compile_all(rebuild_charts=True):
    """Bütün süreci yönetir: grafikler -> HTML kitap -> PDF üretimi."""
    print("=" * 65)
    print("Kur'an Hikmetleri ve Cetvelleri Derleme İşlemi Başlatıldı")
    print("=" * 65)

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    if rebuild_charts:
        print("\n[ADIM 1/3] Grafikler ve ekran görüntüleri üretiliyor...")
        chart_result = build_all_charts()
        surahs_data = chart_result["surahs"]
    else:
        print("\n[ADIM 1/3] Mevcut veriler yükleniyor...")
        surahs_data = load_all_surah_data()

    print("\n[ADIM 2/3] Bütün belgeler ve grafikler uygun sırayla uç uca ekleniyor...")
    unified_html = build_unified_html(config, surahs_data)
    html_out_path = BASE_DIR / config.get("cikti_html", "kuran_hikmetleri_kitap.html")
    with open(html_out_path, "w", encoding="utf-8") as f:
        f.write(unified_html)
    print(f"   Kitap HTML dosyası hazırlandı: {html_out_path} ({os.path.getsize(html_out_path)} bayt)")

    pdf_out_path = BASE_DIR / config.get("cikti_pdf", "kuran_hikmetleri.pdf")
    print(f"\n[ADIM 3/3] Headless Chrome ile PDF derleniyor -> {pdf_out_path.name}...")
    
    cmd = [
        "google-chrome",
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        "--print-to-pdf-no-header",
        f"--print-to-pdf={pdf_out_path}",
        str(html_out_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and pdf_out_path.exists():
        pdf_size_mb = os.path.getsize(pdf_out_path) / (1024 * 1024)
        print(f"\n BAŞARILI! PDF dosyası üretildi: {pdf_out_path}")
        print(f"   Boyut: {pdf_size_mb:.2f} MB")
    else:
        print(f"\n PDF üretimi sırasında hata oluştu:\n{res.stderr}")
        return False

    return True


def watch_and_compile():
    """Kaynak dosyalardaki değişiklikleri izler ve otomatik yeniden derler."""
    print("=" * 65)
    print("İzleme Modu Aktif: Dosyalardaki değişiklikler izleniyor...")
    print("Çıkmak için CTRL+C tuşlarına basabilirsiniz.")
    print("=" * 65)

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    watch_dirs = config.get("izleme_ayarlari", {}).get("klasorler", ["sureler", "kaynak"])
    extensions = tuple(config.get("izleme_ayarlari", {}).get("uzantilar", [".md", ".json", ".html"]))
    poll_interval = config.get("izleme_ayarlari", {}).get("kontrol_araligi_saniye", 3)

    def get_max_mtime():
        max_m = 0
        for d in watch_dirs:
            dp = BASE_DIR / d
            if dp.is_file():
                max_m = max(max_m, dp.stat().st_mtime)
            elif dp.is_dir():
                for p in dp.rglob("*"):
                    if p.is_file() and p.suffix in extensions:
                        # Çıktı dosyalarını izleme dışında tut
                        if "kuran_hikmetleri_kitap" in p.name or "kuran_hikmetleri.pdf" in p.name:
                            continue
                        max_m = max(max_m, p.stat().st_mtime)
        return max_m

    last_mtime = get_max_mtime()
    # İlk derleme
    compile_all(rebuild_charts=False)

    try:
        while True:
            time.sleep(poll_interval)
            cur_mtime = get_max_mtime()
            if cur_mtime > last_mtime:
                print(f"\n[DEĞİŞİKLİK ALGILANDI] {time.strftime('%Y-%m-%d %H:%M:%S')} - Yeniden derleniyor...")
                compile_all(rebuild_charts=True)
                last_mtime = cur_mtime
    except KeyboardInterrupt:
        print("\nİzleme durduruldu.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kur'an Hikmetleri ve Cetvelleri Otomatik Derleyici")
    parser.add_argument("--watch", action="store_true", help="Dosyaları izle ve her değişiklikte otomatik derle")
    parser.add_argument("--no-charts", action="store_true", help="Grafikleri yeniden üretmeden sadece PDF'i derle")
    args = parser.parse_args()

    if args.watch:
        watch_and_compile()
    else:
        compile_all(rebuild_charts=not args.no_charts)
