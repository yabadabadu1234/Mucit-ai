#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kur'an-ı Kerim Sureleri ve Hikmetleri - Grafik ve Görsel Üretim Modülü
Bu modül:
1. Tertip sırasına göre 114 surenin ayet sayıları ve mevzu sütun grafiğini üretir.
2. Nüzul sırasına göre 114 surenin ayet sayıları ve mevzu sütun grafiğini üretir.
3. Her bir sure için özel büyütülmüş detaylı grafik/haritayı (tüm ayetlerin Arapça ve Türkçe metinleriyle) üretir.
4. Headless Chrome ile bu grafiklerin yüksek çözünürlüklü kesit ekran görüntülerini PNG olarak kaydeder.
"""

import os
import re
import glob
import json
import subprocess
from html import escape as html_escape
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent
KAYNAK_SURE_DIR = BASE_DIR / "kaynak" / "sure"
SURELER_DIR = BASE_DIR / "sureler"
GRAFIKLER_DIR = BASE_DIR / "grafikler"
GRAFIKLER_SURE_DIR = GRAFIKLER_DIR / "sureler"
HTML_OUT_DIR = BASE_DIR / "html_grafikler"

# Standart 114 Sure Nüzul Sırası (Diyanet / İbn Abbas kanonik sırası)
NUZUL_SIRASI = [
    96, 68, 73, 74, 1, 111, 81, 87, 92, 89, 93, 94, 103, 100, 108, 102, 107, 109,
    105, 113, 114, 112, 53, 80, 97, 91, 85, 95, 106, 101, 75, 104, 77, 50, 90, 86,
    54, 38, 7, 72, 36, 25, 35, 19, 20, 56, 26, 27, 28, 17, 10, 11, 12, 15,
    6, 37, 31, 34, 39, 40, 41, 42, 43, 44, 45, 46, 51, 88, 18, 16, 71, 14,
    21, 23, 32, 52, 67, 69, 70, 78, 79, 82, 84, 30, 29, 83, 2, 8, 3, 33,
    60, 4, 99, 57, 47, 13, 55, 76, 65, 98, 59, 24, 22, 63, 58, 49, 66, 64,
    61, 62, 48, 5, 9, 110
]

# Nüzul sıra haritası: sure_no -> nuzul_sirasi (1..114)
NUZUL_MAP = {sno: idx + 1 for idx, sno in enumerate(NUZUL_SIRASI)}

# Zengin, vakur İslami tema renk paleti (12 renk)
RENK_PALETI = [
    {"bg": "#1e40af", "border": "#1d4ed8", "text": "#ffffff", "name": "Safir Mavisi"},
    {"bg": "#065f46", "border": "#047857", "text": "#ffffff", "name": "Zümrüt Yeşili"},
    {"bg": "#b45309", "border": "#d97706", "text": "#ffffff", "name": "Kehribar Altını"},
    {"bg": "#991b1b", "border": "#b91c1c", "text": "#ffffff", "name": "Lal Kırmızısı"},
    {"bg": "#4338ca", "border": "#4f46e5", "text": "#ffffff", "name": "İndigo Moru"},
    {"bg": "#0e7490", "border": "#0891b2", "text": "#ffffff", "name": "Turkuaz"},
    {"bg": "#c2410c", "border": "#ea580c", "text": "#ffffff", "name": "Kiremit"},
    {"bg": "#4d7c0f", "border": "#65a30d", "text": "#ffffff", "name": "Zeytin Yeşili"},
    {"bg": "#86198f", "border": "#a21caf", "text": "#ffffff", "name": "Mürdüm"},
    {"bg": "#334155", "border": "#475569", "text": "#ffffff", "name": "Grafit"},
    {"bg": "#a16207", "border": "#ca8a04", "text": "#ffffff", "name": "Toprak Altını"},
    {"bg": "#115e59", "border": "#0f766e", "text": "#ffffff", "name": "Hazer Yeşili"},
]

_D_KONULAR = None


def _d_konulari():
    """Feyzül Furkan (D) bölümlemesinden sûre → [(başlangıç, bitiş, konu)] haritası."""
    global _D_KONULAR
    if _D_KONULAR is not None:
        return _D_KONULAR
    _D_KONULAR = {}
    metin = (BASE_DIR / "kaynak" / "sure_bolumlemeleri" / "sure_bolumlemeleri.md").read_text(encoding="utf-8")
    for sno_str, govde in re.findall(r"^## (\d+)\. .*?\n(.*?)(?=^## \d+\. |\Z)", metin, re.M | re.S):
        bolum = re.search(r"\*\*D\. Feyzül Furkan\*\*(.*)", govde, re.S)
        if not bolum:
            continue
        for satir in bolum.group(1).splitlines():
            m = re.match(r"- (.*?)\s*\((\d+)/(\d+)(?:-(\d+))?\)\s*$", satir.strip())
            if m:
                a = int(m.group(3))
                b = int(m.group(4) or a)
                _D_KONULAR.setdefault(int(sno_str), []).append((a, b, m.group(1)))
    return _D_KONULAR


def _d_konusu(sno, bas, son):
    """Aralıkla en çok çakışan Feyzül Furkan konusu; yoksa None."""
    en_iyi, en_cakisma = None, 0
    for a, b, konu in _d_konulari().get(sno, []):
        cakisma = min(b, son) - max(a, bas) + 1
        if cakisma > en_cakisma:
            en_iyi, en_cakisma = konu, cakisma
    return en_iyi


def load_all_surah_data():
    """Tüm 114 surenin metadata ve ayet verilerini derler."""
    surahs = []
    
    # 00_FIHRIST.md üzerinden ana listeyi çek
    fihrist_file = BASE_DIR / "00_FIHRIST.md"
    fihrist_meta = {}
    if fihrist_file.exists():
        with open(fihrist_file, "r", encoding="utf-8") as f:
            ftext = f.read()
        trows = re.findall(
            r"\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([^\|]+)\|\s*([^\|]+)\|\s*([^\|]+)\|\s*(\d+)\s*\|\s*([^\|]+)\|",
            ftext
        )
        for _sira, _nuzul, sno_str, name, arabic, meaning, vcount_str, place in trows:
            sno = int(sno_str)
            fihrist_meta[sno] = {
                "id": f"S{sno:03d}",
                "name": name.strip(),
                "arabic": arabic.strip(),
                "meaning": meaning.strip(),
                "verses": int(vcount_str.strip()),
                "place": place.strip()
            }

    for sno in range(1, 115):
        # Klasör bul
        matches = list(SURELER_DIR.glob(f"{sno:03d}-*"))
        if not matches:
            continue
        sdir = matches[0]
        sure_md_path = sdir / "sure.md"
        gayeler_md_path = sdir / "gayeler-ve-hikmetler.md"
        json_path = KAYNAK_SURE_DIR / f"{sno}.json"

        # Temel bilgiler
        meta = fihrist_meta.get(sno, {
            "id": f"S{sno:03d}",
            "name": sdir.name.split("-", 1)[1].replace("-", " ").title(),
            "arabic": "",
            "meaning": "",
            "verses": 0,
            "place": "Mekkî"
        })

        if sure_md_path.exists():
            with open(sure_md_path, "r", encoding="utf-8") as f:
                stext = f.read()
            hm = re.search(r"#\s*S\d+\s*·\s*([^(\n]+)(?:\(([^)]+)\))?", stext)
            if hm:
                meta["name"] = hm.group(1).strip()
                if hm.group(2):
                    meta["arabic"] = hm.group(2).strip()
            vm = re.search(r"\*\*Âyet sayısı:\*\*\s*(\d+)", stext)
            if vm:
                meta["verses"] = int(vm.group(1))
            mm = re.search(r"\*\*Anlamı:\*\*\s*([^·\n]+)", stext)
            if mm:
                meta["meaning"] = mm.group(1).strip()
            pm = re.search(r"\*\*İniş:\*\*\s*([^·\n]+)", stext)
            if pm:
                meta["place"] = pm.group(1).strip()
        else:
            stext = ""

        # Ayet metinlerini JSON'dan al
        verses_data = []
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                jdata = json.load(f)
                verses_data = jdata.get("verses", [])
        if meta["verses"] == 0 and verses_data:
            meta["verses"] = len(verses_data)

        # Kısımları ve mevzuları ayrıştır
        parts_raw = []
        # Öncelik: Varsa gayeler-ve-hikmetler.md
        if gayeler_md_path.exists():
            with open(gayeler_md_path, "r", encoding="utf-8") as f:
                gtext = f.read()
            gm = re.search(r"## 2\. Ayet dizisine göre gayeler\s*\n(.*?)(?:\n##|\Z)", gtext, re.DOTALL)
            if gm:
                for line in gm.group(1).strip().split("\n"):
                    m = re.search(r"-\s*\*\*([\d\-,\s]+)(?:\s*\(([^)]+)\))?:\*\*\s*(.*)", line)
                    if m:
                        rng = m.group(1).strip()
                        top = m.group(2).strip() if m.group(2) else ""
                        dsc = m.group(3).strip()
                        title = top if top else dsc.split(".")[0]
                        parts_raw.append({"range_str": rng, "title": title, "desc": dsc})

        # Yoksa sure.md kısımlarını al
        if not parts_raw and stext:
            km = re.search(r"## 10\. Kısımlar.*?\n(.*?)(?:\n---|\Z)", stext, re.DOTALL)
            if km:
                for line in km.group(1).strip().split("\n"):
                    m = re.search(r"-\s*\*\*(K\d{3}-\d{2})\*\* — (.*?)(?:\s*\(([\d\-,\s]+)\))?$", line)
                    if m:
                        code = m.group(1).strip()
                        desc = m.group(2).strip()
                        rng = m.group(3).strip() if m.group(3) else ""
                        parts_raw.append({"code": code, "range_str": rng, "title": desc, "desc": desc})

        # Aralıkları düzenle ve 1'den meta['verses']'e kadar kesintisiz segmentler oluştur
        total_v = meta["verses"]
        parsed_ranges = []
        for p in parts_raw:
            rng_s = p.get("range_str", "")
            if not rng_s:
                continue
            # örn: "1-20", "30", "1-2, 3-4"
            subparts = rng_s.split(",")
            for sp in subparts:
                sp = sp.strip()
                if "-" in sp:
                    s_str, e_str = sp.split("-", 1)
                    try:
                        s_val = int(s_str.strip())
                        e_val = int(e_str.strip())
                        parsed_ranges.append({
                            "start": s_val,
                            "end": e_val,
                            "title": p.get("title", ""),
                            "desc": p.get("desc", ""),
                            "code": p.get("code", "")
                        })
                    except ValueError:
                        pass
                else:
                    try:
                        val = int(sp)
                        parsed_ranges.append({
                            "start": val,
                            "end": val,
                            "title": p.get("title", ""),
                            "desc": p.get("desc", ""),
                            "code": p.get("code", "")
                        })
                    except ValueError:
                        pass

        # Sırala
        parsed_ranges.sort(key=lambda x: x["start"])

        # Kesintisiz segmentlere dönüştür
        contiguous_segments = []
        cur_ayah = 1

        for pr in parsed_ranges:
            if pr["start"] > cur_ayah:
                # Aradaki boşluğu kapat
                gap_start = cur_ayah
                gap_end = pr["start"] - 1
                ara_konu = _d_konusu(sno, gap_start, gap_end) or "Konusu kaynakta belirtilmemiş"
                contiguous_segments.append({
                    "start": gap_start,
                    "end": gap_end,
                    "count": gap_end - gap_start + 1,
                    "title": ara_konu,
                    "desc": ara_konu,
                    "code": f"K{sno:03d}-F"
                })
            
            seg_start = max(cur_ayah, pr["start"])
            seg_end = min(total_v, pr["end"])
            if seg_end >= seg_start:
                contiguous_segments.append({
                    "start": seg_start,
                    "end": seg_end,
                    "count": seg_end - seg_start + 1,
                    "title": pr["title"],
                    "desc": pr["desc"],
                    "code": pr.get("code", "")
                })
                cur_ayah = seg_end + 1

        if cur_ayah <= total_v:
            son_konu = _d_konusu(sno, cur_ayah, total_v) or "Konusu kaynakta belirtilmemiş"
            contiguous_segments.append({
                "start": cur_ayah,
                "end": total_v,
                "count": total_v - cur_ayah + 1,
                "title": son_konu,
                "desc": son_konu,
                "code": f"K{sno:03d}-H"
            })

        # Renk ata
        for idx, seg in enumerate(contiguous_segments):
            palette_color = RENK_PALETI[idx % len(RENK_PALETI)]
            seg["color"] = palette_color["bg"]
            seg["border"] = palette_color["border"]
            seg["text_color"] = palette_color["text"]
            seg["idx"] = idx + 1

        surahs.append({
            "sno": sno,
            "id": meta["id"],
            "name": meta["name"],
            "arabic": meta["arabic"],
            "meaning": meta["meaning"],
            "verses_count": total_v,
            "place": meta["place"],
            "nuzul_order": NUZUL_MAP.get(sno, sno),
            "segments": contiguous_segments,
            "verses": verses_data,
            "slug": sdir.name
        })

    return surahs


def generate_panoramic_chart_html(surahs, order_by="tertip"):
    """
    114 surenin tamamını içeren yüksek çözünürlüklü sütun grafiği HTML'i üretir.
    order_by: 'tertip' (1..114) veya 'nuzul' (kronolojik sıra)
    """
    if order_by == "nuzul":
        sorted_surahs = sorted(surahs, key=lambda s: s["nuzul_order"])
        title_text = "Kur'an-ı Kerim Sureleri Âyet Sayıları ve Mevzular Cetveli (Nüzul Sırasına Göre)"
        subtitle_text = "İlk inen Alak Suresinden son inen Nasr Suresine kronolojik nüzul sırasıyla 114 surenin mevzu taksimatı"
        x_label_title = "Sureler (Nüzul Sırasıyla)"
    else:
        sorted_surahs = sorted(surahs, key=lambda s: s["sno"])
        title_text = "Kur'an-ı Kerim Sureleri Âyet Sayıları ve Mevzular Cetveli (Mushaf Tertip Sırasına Göre)"
        subtitle_text = "Fâtiha'dan Nâs Suresine kadar 114 surenin âyet sayıları ve kendi içlerindeki mevzu bölümleri"
        x_label_title = "Sureler (Tertip Sırasıyla)"

    # SVG Boyutları
    svg_width = 4600
    svg_height = 1350
    margin_left = 90
    margin_right = 60
    margin_top = 110
    margin_bottom = 220

    chart_w = svg_width - margin_left - margin_right
    chart_h = svg_height - margin_top - margin_bottom

    max_verses = 286  # Bakara suresi
    # 290 tavan
    y_max = 290
    y_scale = chart_h / y_max

    num_surahs = len(sorted_surahs)
    col_width = (chart_w / num_surahs) - 6
    col_gap = 6

    # Y ekseni çizgileri (0, 25, 50, 75, 100, 150, 200, 250, 286)
    grid_steps = [0, 25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 286]

    svg_elements = []

    # Izgara çizgileri
    for step in grid_steps:
        y_pos = margin_top + chart_h - (step * y_scale)
        stroke_color = "#334155" if step in [0, 100, 200, 286] else "#1e293b"
        stroke_width = "2" if step in [0, 286] else "1"
        dash_arr = "none" if step in [0, 286] else "4,4"
        svg_elements.append(
            f'<line x1="{margin_left}" y1="{y_pos}" x2="{margin_left + chart_w}" y2="{y_pos}" '
            f'stroke="{stroke_color}" stroke-width="{stroke_width}" stroke-dasharray="{dash_arr}" />'
        )
        # Y etiketleri
        svg_elements.append(
            f'<text x="{margin_left - 15}" y="{y_pos + 5}" fill="#94a3b8" font-size="16" '
            f'font-family="monospace" text-anchor="end" font-weight="600">{step}</text>'
        )

    # Her sure sütunu
    for idx, s in enumerate(sorted_surahs):
        x_pos = margin_left + idx * (col_width + col_gap)
        base_y = margin_top + chart_h

        curr_bottom = base_y

        # Sütunun kısımları (Aşağıdan yukarıya: 1. ayetten son ayete)
        for seg in s["segments"]:
            seg_h = seg["count"] * y_scale
            seg_y = curr_bottom - seg_h

            seg_title_esc = seg["title"].replace('"', '&quot;').replace("'", "&#39;")
            tooltip_data = (
                f"{s['sno']}. {s['name']} ({s['place']}) | Âyet: {seg['start']}-{seg['end']} "
                f"({seg['count']} âyet) | {seg_title_esc}"
            )

            # Segment kutusu
            svg_elements.append(
                f'<rect class="segment-rect" x="{x_pos}" y="{seg_y}" width="{col_width}" height="{seg_h}" '
                f'fill="{seg["color"]}" stroke="{seg["border"]}" stroke-width="1.5" rx="3" '
                f'data-tooltip="{tooltip_data}" '
                f'onclick="showSurahModal({s["sno"]})" style="cursor: pointer; transition: all 0.2s;" />'
            )

            # Sütun içi metin (Eğer segment yeterince yüksekse)
            if seg_h >= 32:
                # Kısaltılmış mevzu başlığı
                clean_title = seg["title"]
                if len(clean_title) > 22:
                    clean_title = clean_title[:20] + "…"
                text_y = seg_y + seg_h / 2 + 5
                # Metni dikey veya yatay yerleştir
                svg_elements.append(
                    f'<text x="{x_pos + col_width/2}" y="{text_y}" fill="#ffffff" font-size="11" '
                    f'font-family="sans-serif" font-weight="600" text-anchor="middle" '
                    f'pointer-events="none" opacity="0.95">'
                    f'{seg["start"]}-{seg["end"]}'
                    f'</text>'
                )

            curr_bottom = seg_y

        # Sütun tepe toplam âyet sayısı
        top_y = base_y - (s["verses_count"] * y_scale) - 8
        svg_elements.append(
            f'<text x="{x_pos + col_width/2}" y="{top_y}" fill="#38bdf8" font-size="13" '
            f'font-family="monospace" font-weight="700" text-anchor="middle">{s["verses_count"]}</text>'
        )

        # X ekseni alt etiketleri (Sure No, Adı, İniş Rozeti)
        label_y = base_y + 20
        place_color = "#10b981" if "Meden" in s["place"] else "#f59e0b"
        place_symbol = "Med." if "Meden" in s["place"] else "Mek."

        # Sure adı ve nüzul / tertip bilgisi
        order_info = f"N:{s['nuzul_order']}" if order_by == "tertip" else f"T:{s['sno']}"
        display_no = f"{s['sno']}" if order_by == "tertip" else f"N{s['nuzul_order']}"

        svg_elements.append(
            f'<g transform="translate({x_pos + col_width/2}, {label_y}) rotate(55)" style="cursor:pointer;" onclick="showSurahModal({s["sno"]})">'
            f'<text x="0" y="0" fill="#f8fafc" font-size="13" font-family="sans-serif" font-weight="600">{display_no}. {s["name"]}</text>'
            f'<text x="0" y="15" fill="{place_color}" font-size="11" font-family="sans-serif">[{place_symbol} · {order_info}]</text>'
            f'</g>'
        )

    svg_content = "\n".join(svg_elements)

    html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<title>{title_text}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Amiri:wght@700&display=swap" rel="stylesheet">
<style>
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  padding: 24px;
  background: #090d16;
  color: #f1f5f9;
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
  overflow-x: auto;
}}
.header {{
  max-width: 4600px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #0f172a;
  padding: 24px 32px;
  border-radius: 16px;
  border: 1px solid #1e293b;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}}
.title-box h1 {{
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 800;
  background: linear-gradient(135deg, #38bdf8, #818cf8, #c084fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}}
.title-box p {{
  margin: 0;
  color: #94a3b8;
  font-size: 15px;
}}
.controls {{
  display: flex;
  gap: 16px;
  align-items: center;
}}
.btn {{
  padding: 10px 20px;
  background: #1e293b;
  color: #f8fafc;
  border: 1px solid #334155;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}}
.btn:hover, .btn.active {{
  background: #2563eb;
  border-color: #3b82f6;
  color: #ffffff;
}}
.chart-container {{
  position: relative;
  background: #0b1120;
  padding: 20px;
  border-radius: 20px;
  border: 1px solid #1e293b;
  box-shadow: 0 20px 50px rgba(0,0,0,0.6);
  display: inline-block;
}}
.legend {{
  max-width: 4600px;
  margin-top: 24px;
  padding: 20px;
  background: #0f172a;
  border-radius: 12px;
  border: 1px solid #1e293b;
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  align-items: center;
  font-size: 14px;
}}
.legend-item {{
  display: flex;
  align-items: center;
  gap: 8px;
}}
.legend-color {{
  width: 18px;
  height: 18px;
  border-radius: 4px;
}}
#tooltip {{
  position: absolute;
  display: none;
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid #38bdf8;
  padding: 12px 18px;
  border-radius: 10px;
  color: #ffffff;
  font-size: 13px;
  font-weight: 500;
  pointer-events: none;
  z-index: 1000;
  box-shadow: 0 10px 25px rgba(0,0,0,0.8);
  max-width: 400px;
  backdrop-filter: blur(8px);
}}
.segment-rect:hover {{
  filter: brightness(1.25);
  stroke: #ffffff !important;
  stroke-width: 2.5px !important;
}}
/* Modal */
.modal-overlay {{
  display: none;
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.85);
  z-index: 9999;
  backdrop-filter: blur(6px);
  justify-content: center;
  align-items: center;
  padding: 40px;
}}
.modal-content {{
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 16px;
  width: 90%;
  max-width: 1100px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 32px;
  box-shadow: 0 25px 60px rgba(0,0,0,0.9);
  position: relative;
}}
.close-btn {{
  position: absolute;
  top: 20px;
  right: 24px;
  font-size: 28px;
  cursor: pointer;
  color: #94a3b8;
}}
.close-btn:hover {{ color: #ffffff; }}
</style>
</head>
<body>

<div class="header">
  <div class="title-box">
    <h1>{title_text}</h1>
    <p>{subtitle_text} · Toplam 114 Sure · 6236 Âyet</p>
  </div>
  <div class="controls">
    <a href="grafik_tertip.html" class="btn {'active' if order_by=='tertip' else ''}">Mushaf Tertip Sırası</a>
    <a href="grafik_nuzul.html" class="btn {'active' if order_by=='nuzul' else ''}">Nüzul Sırası</a>
    <span style="color:#64748b; font-size:14px;">(Sütunlara tıklayarak ayet seviyesindeki detaylı haritaya geçebilirsiniz)</span>
  </div>
</div>

<div class="chart-container">
  <div id="tooltip"></div>
  <svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg">
    <!-- Başlık ve Eksanler -->
    <text x="{margin_left}" y="50" fill="#38bdf8" font-size="22" font-weight="700">Y Ekseni: Âyet Sayısı (0 - 286)</text>
    <text x="{svg_width - margin_right}" y="50" fill="#94a3b8" font-size="18" font-weight="600" text-anchor="end">{x_label_title}</text>
    
    {svg_content}
  </svg>
</div>

<div class="legend">
  <strong style="color:#f8fafc; font-size:15px;">Mevzu Renkleri:</strong>
  {"".join([f'<div class="legend-item"><div class="legend-color" style="background:{c["bg"]}; border:1px solid {c["border"]};"></div><span>{c["name"]}</span></div>' for c in RENK_PALETI])}
  <div style="margin-left: auto; display:flex; gap:16px;">
    <span style="color:#f59e0b; font-weight:600;">● Mekkî Sureler</span>
    <span style="color:#10b981; font-weight:600;">● Medenî Sureler</span>
  </div>
</div>

<!-- Modal Container -->
<div class="modal-overlay" id="surahModal">
  <div class="modal-content" id="modalBody"></div>
</div>

<script>
const tooltip = document.getElementById('tooltip');
document.querySelectorAll('.segment-rect').forEach(rect => {{
  rect.addEventListener('mousemove', (e) => {{
    const data = rect.getAttribute('data-tooltip');
    tooltip.innerHTML = data;
    tooltip.style.display = 'block';
    tooltip.style.left = (e.pageX + 15) + 'px';
    tooltip.style.top = (e.pageY - 35) + 'px';
  }});
  rect.addEventListener('mouseleave', () => {{
    tooltip.style.display = 'none';
  }});
}});

function showSurahModal(sno) {{
  window.open('sureler/' + sno + '_detay.html', '_blank');
}}
</script>
</body>
</html>"""
    return html


KELIME_RENKLERI = ["#dc2626", "#2563eb", "#16a34a", "#9333ea", "#ea580c",
                   "#0891b2", "#be185d", "#ca8a04", "#4f46e5", "#0d9488"]

ELMALILI_DIZIN = BASE_DIR / "kaynak" / "tafseer" / "elmalili"
_ELMALILI_BASLIK = re.compile(r"^(?:\d+/(\d+)\.|(\d+)((?:-\d+)*)-)\s*((?:.*))$", re.S)
_ELMALILI_BOLUM = re.compile(r"^\d+-[A-ZÇĞİÖŞÜ' ]+:\s*$")


def _elmalili_temiz(p):
    """Kaynak dosyadaki kaçış işaretlerini ve satır kırımlarını temizler."""
    p = p.replace("\\'", "'").replace('\\"', '"').replace("\\", "")
    return re.sub(r"\s*\n\s*", " ", p).strip()


def _elmalili_meal_cikar(paragraflar, n_ayet):
    """"Meâl-i Şerifi" bölümlerindeki kısa âyet satırlarını (Elmalılı'nın meâli) çıkarır; geri kalanı döner."""
    kalan = []
    meal_modu = False
    beklenen = 1
    for p in paragraflar:
        s = _elmalili_temiz(p)
        if not s or set(s) <= set("-= ") or _ELMALILI_BOLUM.match(s):
            continue
        if re.match(r"Me[âa]l\s*-?\s*i\s*[Şş]\s*e\s*r", s, re.I):
            meal_modu = True
            continue
        m = _ELMALILI_BASLIK.match(s)
        ilk, son = None, None
        if m:
            if m.group(1):
                ilk = son = int(m.group(1))
            else:
                ilk = int(m.group(2))
                son = max([ilk] + [int(x) for x in m.group(3).split("-") if x])
        if meal_modu:
            if ilk is not None and beklenen <= ilk <= beklenen + 5 and ilk <= n_ayet and len(s) <= 400:
                beklenen = son + 1
                continue
            meal_modu = False
        if ilk is not None and beklenen <= ilk <= beklenen + 5 and ilk <= n_ayet:
            beklenen = son + 1
        kalan.append(s)
    return kalan


def _elmalili_sirali_bol(metin, n_ayet):
    """Metinde 1, 2, 3… sırasıyla ayet numaralarını arar; her numaranın arkasındaki parça o âyetin tefsiridir.
    Ayet numarası, sayı/eğik çizgi (sûre-ayet atıfları: 10/96) veya rakamın parçası olmadığında kabul edilir."""
    starts = []
    pos = 0
    for v in range(1, n_ayet + 1):
        # Biçimler: "13-", "13 ", "13)" ve "54/1." (sûre/âyet başlığı); "10/96" gibi atıflar âyet sayılmaz.
        m = re.compile(r"(?:(?<![\d/\w])" + str(v) + r"(?![\d/])(?=\s*[-.)\]:]|\s))|(?:(?<=\d/)" + str(v) + r"(?=\.\s))").search(metin, pos)
        if not m:
            continue  # Bu âyet metinde yok; sonrakini aramaya devam et.
        starts.append((v, m.start(), m.end()))
        pos = m.end()
    intro = metin[:starts[0][1]].strip() if starts else metin.strip()
    harita = {}
    dolu = []
    for i, (v, st, en) in enumerate(starts):
        end = starts[i + 1][1] if i + 1 < len(starts) else len(metin)
        govde = re.sub(r"^[\s\-.)\]:]+", "", metin[en:end]).strip()
        # Ikinci geçişte âyet numarasının hemen arkasındaki tırnaklı meâl alıntısı tefsir değildir.
        govde = re.sub(r'^"[^"\n]{0,300}"\s*', "", govde)
        parcalar = [x.strip() for x in govde.split("\n\n") if x.strip()]
        if parcalar:
            harita[v] = parcalar
            dolu.append(v)
        else:
            dolu.append(None)
    # Metni boş kalan âyetler: sonraki dolu âyetin kutusunda gösterilir.
    for i, (v, _, _) in enumerate(starts):
        if v in harita:
            continue
        j = i + 1
        while j < len(starts) and starts[j][0] not in harita:
            j += 1
        if j < len(starts):
            harita[v] = ("ortak", starts[j][0])
    return ([intro] if intro else []), harita


def elmalili_tefsiri(sno, n_ayet):
    """Elmalılı tefsirini sûre bazında âyetlere böler; yalnız tefsir metnini verir.
    Döner: (sûre_başı_paragrafları, {âyet: paragraflar | ("ortak", âyet)})."""
    yol = ELMALILI_DIZIN / f"{sno}.md"
    if not yol.exists():
        return [], {}
    paragraflar = [p for p in re.split(r"\n\s*\n", yol.read_text(encoding="utf-8")) if p.strip()]
    kalan = _elmalili_meal_cikar(paragraflar, n_ayet)
    metin = "\n\n".join(kalan)
    return _elmalili_sirali_bol(metin, n_ayet)


def kelime_satiri_html(kelimeler):
    """Âyetin kelime mealli satırı: her kelime ayrı renkte; altında Türkçe karşılığı."""
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


def _tefsir_paragraflari(paragraflar):
    return "".join(f"<p>{html_escape(p)}</p>" for p in paragraflar)


def generate_surah_detail_chart_html(surah_data, kelimeler=None):
    """
    Her sûre için detay sayfası. Kitap gibi okunur: üstte kitaba dönüş çubuğu;
    mevzular altında âyet kutuları (kitapla aynı boyutta: Arapça, kelime mealli, Türkçe meal).
    Her âyet kutusunda, âyet metninden sonra Elmalılı tefsiri (açılır kapanır) yer alır.
    kelimeler: {(sure, âyet): [{'ar','tr','lem'}]} (kelime_mealli.yukle()).
    """
    kelimeler = kelimeler or {}
    sno = surah_data["sno"]
    name = surah_data["name"]
    arabic = surah_data["arabic"]
    meaning = surah_data["meaning"]
    vcount = surah_data["verses_count"]
    place = surah_data["place"]
    nuzul = surah_data["nuzul_order"]
    segments = surah_data["segments"]
    verses = surah_data["verses"]

    verse_dict = {v["verseNumber"]: v for v in verses}
    tanitim, tefsir_haritasi = elmalili_tefsiri(sno, vcount)

    tanitim_html = ""
    if tanitim:
        tanitim_html = (
            '<section class="tanitim"><h3>Elmalılı tefsiri: sûre tanıtımı</h3>'
            f'{_tefsir_paragraflari(tanitim)}</section>'
        )

    mini_bar_parts = []
    for seg in segments:
        mini_bar_parts.append(
            f'<div style="flex: {seg["count"]}; background:{seg["color"]}; border:1px solid {seg["border"]}; '
            f'padding:8px 4px; text-align:center; color:#ffffff; font-size:11px; font-weight:600; '
            f'overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" '
            f'title="{seg["title"]} ({seg["start"]}-{seg["end"]})">'
            f'{seg["title"]} ({seg["count"]})'
            f'</div>'
        )
    mini_bar_html = '<div style="display:flex; width:100%; border-radius:8px; overflow:hidden; margin:20px 0 8px; box-shadow:0 2px 10px rgba(0,0,0,0.12);">' + "".join(mini_bar_parts) + '</div>'

    sections_html = []
    for seg in segments:
        kutular = []
        for vnum in range(seg["start"], seg["end"] + 1):
            vobj = verse_dict.get(vnum, {})
            v_arabic = vobj.get("arabic", "")
            turkish_dict = vobj.get("turkish", {})
            v_meal = turkish_dict.get("diyanet_vakfi") or turkish_dict.get("hayrat_nesriyat") or turkish_dict.get("omer_nasuhi_bilmen") or ""
            tefsir = tefsir_haritasi.get(vnum)
            if isinstance(tefsir, tuple):
                tefsir_html = f'<div class="ag-ortak">Tefsiri {tefsir[1]}. âyetin kutusundadır.</div>'
            elif tefsir:
                tefsir_html = (
                    f'<details class="tefsir"><summary>Elmalılı tefsiri · Âyet {vnum}</summary>'
                    f'{_tefsir_paragraflari(tefsir)}</details>'
                )
            else:
                tefsir_html = ""
            kutular.append(f"""
            <article class="ag-kart" style="border-top:4px solid {seg['color']};">
              <div class="ag-kart-baslik" style="color:{seg['color']};">Âyet {vnum}</div>
              <div class="verse-ar">{v_arabic}</div>
              {kelime_satiri_html(kelimeler.get((sno, vnum), []))}
              <div class="verse-tr">{v_meal}</div>
              {tefsir_html}
            </article>
            """)

        sections_html.append(f"""
        <section class="mevzu">
          <header class="mevzu-baslik" style="border-left:6px solid {seg['color']}; background:{seg['color']}14;">
            <div class="mevzu-ad" style="color:{seg['color']};">
              <span class="mevzu-kod">{seg.get('code', '')}</span>{seg['title']}
            </div>
            <div class="mevzu-meta">Âyet {seg['start']} - {seg['end']} · <span class="rozet" style="background:{seg['color']};">{seg['count']} âyet</span></div>
          </header>
          <div class="ayetler">{"".join(kutular)}</div>
        </section>
        """)

    html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>S{sno:03d} · {name} Suresi Âyet ve Mevzu Haritası</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Amiri:wght@400;700&display=swap" rel="stylesheet">
<style>
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  padding-top: 64px;
  background: #f5f1e8;
  color: #1e293b;
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
  line-height: 1.65;
  font-size: 11pt;
}}
.ust-cubuk {{
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 56px;
  background: #0f172a;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  z-index: 10;
}}
.geri {{
  color: #fbbf24;
  text-decoration: none;
  font-weight: 700;
  font-size: 11pt;
  padding: 6px 12px;
  border: 1px solid #334155;
  border-radius: 8px;
}}
.geri:hover {{ background: #1e293b; }}
.ust-baslik {{ color: #e2e8f0; font-weight: 600; font-size: 10.5pt; }}
.kitap-sayfa {{
  max-width: 1100px;
  margin: 0 auto;
  background: #ffffff;
  padding: 32px 36px 56px;
  min-height: 100vh;
  box-shadow: 0 2px 18px rgba(15, 23, 42, 0.08);
}}
.sure-no {{
  font-size: 9.5pt;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: #64748b;
}}
.sure-baslik h1 {{
  font-family: 'Cinzel', 'Plus Jakarta Sans', serif;
  font-size: 22pt;
  color: #0f172a;
  margin: 4px 0 8px;
  line-height: 1.3;
}}
.sure-arapca {{
  font-family: 'Amiri', serif;
  color: #1e40af;
  font-size: 24pt;
  margin-left: 12px;
  font-weight: 400;
}}
.sure-rozetler {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }}
.rozet {{
  display: inline-block;
  padding: 3px 10px;
  border-radius: 14px;
  font-size: 9pt;
  color: #ffffff;
  font-weight: 600;
}}
.rozet-acik {{ background: #475569; }}
.tanitim {{
  margin-top: 26px;
  padding: 12px 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 9.5pt;
  color: #334155;
}}
.tanitim h3 {{ margin: 0 0 6px; font-size: 11pt; color: #1e3a8a; }}
.tanitim p {{ margin: 0 0 6px; }}
.mevzu {{ margin-top: 30px; }}
.mevzu-baslik {{ padding: 10px 16px; border-radius: 6px; margin-bottom: 12px; }}
.mevzu-ad {{ font-size: 13pt; font-weight: 700; }}
.mevzu-kod {{
  font-family: monospace;
  font-size: 9pt;
  background: rgba(15, 23, 42, 0.06);
  color: #334155;
  padding: 2px 6px;
  border-radius: 4px;
  margin-right: 8px;
}}
.mevzu-meta {{ color: #64748b; font-size: 9.5pt; margin-top: 4px; }}
/* Âyet kutuları: kitaptaki ag-kart ile aynı boyut */
.ayetler {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 6px;
  align-items: start;
}}
.ag-kart {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 6px 8px;
  page-break-inside: avoid;
}}
.ag-kart-baslik {{
  font-size: 8.5pt;
  font-weight: 700;
  margin-bottom: 2px;
}}
.verse-ar {{
  font-family: 'Amiri', serif;
  font-size: 12pt;
  line-height: 1.8;
  direction: rtl;
  text-align: right;
  color: #0f172a;
}}
.verse-tr {{
  font-size: 8pt;
  color: #475569;
  line-height: 1.5;
  border-top: 1px dashed #e2e8f0;
  padding-top: 4px;
  margin-top: 2px;
}}
.ag-ortak {{
  font-size: 7.5pt;
  color: #94a3b8;
  font-style: italic;
  margin-top: 4px;
}}
.tefsir {{
  margin-top: 5px;
  border-top: 1px dashed #e2e8f0;
  padding-top: 4px;
  font-size: 7.5pt;
  color: #334155;
  line-height: 1.5;
}}
.tefsir summary {{
  cursor: pointer;
  color: #1e40af;
  font-weight: 700;
  font-size: 7.5pt;
}}
.tefsir p {{ margin: 4px 0 0; }}
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
.kelime-ar {{ font-family: 'Amiri', serif; font-size: 13pt; line-height: 1.6; }}
.kelime-tr {{ direction: ltr; font-size: 7pt; color: #334155; text-align: center; line-height: 1.2; }}
@media (max-width: 640px) {{
  .kitap-sayfa {{ padding: 20px 16px 40px; }}
  .sure-arapca {{ display: block; margin: 6px 0 0; }}
  .ayetler {{ grid-template-columns: 1fr; }}
}}
@media print {{
  .ust-cubuk {{ display: none; }}
  body {{ padding-top: 0; background: #ffffff; }}
  .tefsir {{ display: block; }}
  .tefsir > :not(summary) {{ display: block; }}
}}
</style>
</head>
<body>
<header class="ust-cubuk">
  <a class="geri" href="../../kuran_hikmetleri_kitap.html#sure-{sno}">&larr; Kitaba dön</a>
  <span class="ust-baslik">Kur'an Hikmetleri · S{sno:03d}</span>
</header>
<main class="kitap-sayfa">
  <header class="sure-baslik">
    <div class="sure-no">Sure {sno}</div>
    <h1>{sno}. {name} Suresi <span class="sure-arapca">{arabic}</span></h1>
    <div class="sure-rozetler">
      <span class="rozet rozet-acik">Mushaf Tertibi: {sno}</span>
      <span class="rozet rozet-acik">Nüzul Sırası: {nuzul}</span>
      <span class="rozet rozet-acik">{place}</span>
      <span class="rozet rozet-acik">Anlamı: {meaning}</span>
      <span class="rozet rozet-acik">{vcount} Âyet</span>
    </div>
  </header>

  {tanitim_html}

  {mini_bar_html}

  {"".join(sections_html)}
</main>
</body>
</html>"""
    return html


def build_all_charts():
    """Tüm grafikleri üretir ve HTML/PNG olarak kaydeder."""
    HTML_OUT_DIR.mkdir(parents=True, exist_ok=True)
    (HTML_OUT_DIR / "sureler").mkdir(parents=True, exist_ok=True)
    GRAFIKLER_DIR.mkdir(parents=True, exist_ok=True)
    GRAFIKLER_SURE_DIR.mkdir(parents=True, exist_ok=True)

    print("1. Kur'an sure verileri yükleniyor...")
    surahs = load_all_surah_data()
    print(f"   {len(surahs)} sure başarıyla yüklendi.")

    # 1. Tertip Grafiği HTML
    print("2. Tertip sırası panoramik grafiği üretiliyor...")
    tertip_html = generate_panoramic_chart_html(surahs, order_by="tertip")
    tertip_path = HTML_OUT_DIR / "grafik_tertip.html"
    with open(tertip_path, "w", encoding="utf-8") as f:
        f.write(tertip_html)
    print(f"   Kaydedildi: {tertip_path}")

    # 2. Nüzul Grafiği HTML
    print("3. Nüzul sırası panoramik grafiği üretiliyor...")
    nuzul_html = generate_panoramic_chart_html(surahs, order_by="nuzul")
    nuzul_path = HTML_OUT_DIR / "grafik_nuzul.html"
    with open(nuzul_path, "w", encoding="utf-8") as f:
        f.write(nuzul_html)
    print(f"   Kaydedildi: {nuzul_path}")

    # 3. Her Sure için Ayet Pencereli Detay Harita HTML
    print("4. 114 sure için ayet seviyesinde pencereli detay haritaları üretiliyor...")
    import kelime_mealli
    kelimeler = kelime_mealli.yukle()
    for s in surahs:
        s_html = generate_surah_detail_chart_html(s, kelimeler)
        s_path = HTML_OUT_DIR / "sureler" / f"{s['sno']}_detay.html"
        with open(s_path, "w", encoding="utf-8") as f:
            f.write(s_html)
    print("   114 surenin detay haritaları tamamlandı.")

    # 4. Headless Chrome ile Ekran Görüntüleri (Screenshots)
    print("5. Panoramik grafiklerin yüksek çözünürlüklü ekran görüntüleri alınıyor...")
    tertip_png = GRAFIKLER_DIR / "kuran_sureleri_tertip_cetveli.png"
    nuzul_png = GRAFIKLER_DIR / "kuran_sureleri_nuzul_cetveli.png"

    # Tertip ekran görüntüsü (Ultra-wide 4600x1400)
    subprocess.run([
        "google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu",
        "--window-size=4650,1450", f"--screenshot={tertip_png}", str(tertip_path)
    ], check=True, capture_output=True)
    print(f"   Ekran görüntüsü alındı: {tertip_png} ({os.path.getsize(tertip_png)} bayt)")

    # Nüzul ekran görüntüsü
    subprocess.run([
        "google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu",
        "--window-size=4650,1450", f"--screenshot={nuzul_png}", str(nuzul_path)
    ], check=True, capture_output=True)
    print(f"   Ekran görüntüsü alındı: {nuzul_png} ({os.path.getsize(nuzul_png)} bayt)")

    # Surelerin örnek / temsilî kesit ekran görüntüleri (Örn: Fâtiha, Bakara, Yâsîn, Kasas, İhlas vb.)
    print("6. Sure bazlı kesit ekran görüntüleri alınıyor...")
    sample_sures = [1, 2, 28, 36, 67, 108, 112, 114]
    for sno in sample_sures:
        s_html_path = HTML_OUT_DIR / "sureler" / f"{sno}_detay.html"
        s_png_path = GRAFIKLER_SURE_DIR / f"sure_{sno:03d}_kesit.png"
        subprocess.run([
            "google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu",
            "--window-size=1400,900", f"--screenshot={s_png_path}", str(s_html_path)
        ], check=True, capture_output=True)
        print(f"   Sure {sno} kesit görüntüsü alındı: {s_png_path}")

    return {
        "tertip_html": tertip_path,
        "nuzul_html": nuzul_path,
        "tertip_png": tertip_png,
        "nuzul_png": nuzul_png,
        "surahs": surahs
    }


if __name__ == "__main__":
    build_all_charts()
