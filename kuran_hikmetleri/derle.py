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


def _kart(renk, v, etiket, verse_dict):
    ar, tr = _ayet_metni(verse_dict, v)
    return (
        f'<div class="ag-kart" style="border-top:4px solid {renk};">'
        f'<div class="ag-kart-baslik" style="color:{renk};">Âyet {v}{" · " + etiket if etiket else ""}</div>'
        f'<div class="verse-ar">{ar}</div><div class="verse-tr">{tr}</div></div>'
    )


def _yumak_icerigi(dugumler, renk, verse_dict):
    """Bir yumağın içi: alt mevzu başlıkları ve bu başlıkların altındaki âyet kartları (iç içe, sonsuz düzey)."""
    parcalar = []
    for x in dugumler:
        if x.get("alt"):
            a, b = x["aralik"]
            parcalar.append(
                f'<div class="ag-alt-baslik" style="border-left:4px solid {renk};">'
                f'{x["baslik"]} <small>(Âyet {a}{"-" + str(b) if a != b else ""})</small></div>'
            )
            parcalar.append(_yumak_icerigi(x["alt"], renk, verse_dict))
        else:
            parcalar.append(_kart(renk, x["aralik"][0], x["baslik"], verse_dict))
    return f'<div class="ag-yumak-icerik">{"".join(parcalar)}</div>'


def detay_bolumu(segments, agac_segmentler, verse_dict):
    """Ayrıntılı görünüm: her genel mevzu başlığı üstte, tek bir ok altındaki âyet matrisine bağlanır.
    Matris, mevzunun bölümlerine göre ayrı yumaklar halinde alt alta dizilir. Aidiyet renkle gösterilir."""
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
            yumaklar = []
            for bolum in agac_segmentler[anahtar]:
                a, b = bolum["aralik"]
                yumaklar.append(
                    f'<div class="ag-yumak" style="border:2px solid {renk};">'
                    f'<div class="ag-yumak-baslik" style="background:{renk};">'
                    f'{bolum["baslik"]} <small>(Âyet {a}{"-" + str(b) if a != b else ""} · {b - a + 1} âyet)</small></div>'
                    + (_yumak_icerigi(bolum["alt"], renk, verse_dict) if bolum.get("alt") else
                       _kart(renk, a, bolum["baslik"], verse_dict))
                    + "</div>"
                )
        else:
            kartlar = "".join(_kart(renk, v, "", verse_dict) for v in range(seg["start"], seg["end"] + 1))
            yumaklar = [
                f'<div class="ag-yumak" style="border:2px solid {renk};">'
                f'<div class="ag-yumak-icerik">{kartlar}</div></div>'
            ]
        bloklar.append(f'<div class="ag-blok">{ust}{"".join(yumaklar)}</div>')
    return f'<div class="ag-ayrintili">{"".join(bloklar)}</div>'


def build_unified_html(config, surahs_data):
    """Yapılandırmada işaret edilen dosyaları ve grafikleri uygun sırayla uç uca ekleyip tek bir HTML oluşturur."""
    md_conv = get_markdown_converter()
    surah_dict = {s["sno"]: s for s in surahs_data}

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

                    # Mini sütun mevzu çubuğu
                    mini_bar = []
                    for seg in segments:
                        mini_bar.append(
                            f'<div style="flex:{seg["count"]}; background:{seg["color"]}; '
                            f'padding:6px 2px; color:#ffffff; font-size:11px; font-weight:700; '
                            f'text-align:center; overflow:hidden;">'
                            f'{seg["title"]} ({seg["start"]}-{seg["end"]})'
                            f'</div>'
                        )
                    mini_bar_html = f'<div class="surah-mini-bar">{"".join(mini_bar)}</div>'

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
                        detail_content = kesit_html + seg_table + '<h4 class="ag-baslik">Ayrıntılı görünüm: mevzular ve âyet metinleri</h4>' + ayrintili

                    chart_section_html = f"""
                    <div class="surah-chart-section">
                      <h3 class="chart-heading">S{sno:03d} · {s_meta['name']} Suresi Âyet Taksimatı ve Mevzu Haritası</h3>
                      {mini_bar_html}
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
  height: 26px;
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
.ag-yumak {{
  border-radius: 8px;
  padding: 8px;
  margin: 0 0 10px 28px;
  background: #fbfdff;
}}
.ag-yumak-baslik {{
  color: #ffffff;
  font-size: 9.5pt;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 5px;
  margin-bottom: 8px;
}}
.ag-yumak-icerik {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: flex-start;
}}
.ag-alt-baslik {{
  width: 100%;
  font-size: 9pt;
  font-weight: 700;
  color: #1e293b;
  padding: 2px 8px;
  margin: 6px 0 2px 0;
}}
.ag-alt-baslik small {{
  font-weight: 400;
  color: #64748b;
}}
.ag-kart {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 6px 8px;
  width: calc(50% - 4px);
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

@media print {{
  body {{ background: transparent; }}
  .page {{ page-break-after: always; }}
  .verse-card {{ page-break-inside: avoid; }}
}}
</style>
</head>
<body>

{"".join(body_sections)}

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
