#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kök sayfası üreticisi: kaynak/lugat/pilot/<kök>.json + etimoloji/<kök>.md -> kok/<kök>.html

Sayfa katmanları: kapsül · şecere · âyet haritası · komşu kökler · geri çağırma · tam şerh.
Âyet metni, Türkçe meal ve kök geçişleri kaynaklardan okunur; elle yazılan yalnız pilot JSON'dur.
"""

import json
import re
from html import escape
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MORFOLOJI = BASE_DIR / "veri_harici" / "eyupipler" / "quran-morphology.txt"
PILOT_DIZIN = BASE_DIR / "kaynak" / "lugat" / "pilot"
ETIM_DIZIN = BASE_DIR / "kaynak" / "lugat" / "etimoloji"
CIKTI_DIZIN = BASE_DIR / "kok"
MEAL_ANAHTAR = "diyanet_vakfi"

STIL = """
:root { --zemin:#f5f1e8; --kart:#fff; --yazi:#1e293b; --sessiz:#64748b; --cizgi:#e2e8f0; --vurgu:#92400e; }
* { box-sizing:border-box; }
body { margin:0; font-family:'Plus Jakarta Sans',system-ui,sans-serif; background:var(--zemin); color:var(--yazi); line-height:1.65; }
.ust { background:#0f172a; padding:10px 16px; }
.ust a { color:#fbbf24; text-decoration:none; font-weight:700; }
main { max-width:920px; margin:0 auto; padding:18px 16px 70px; }
.ar { font-family:'Amiri',serif; direction:rtl; }
.kapsul { background:var(--kart); border:1px solid var(--cizgi); border-radius:14px; padding:22px 20px; text-align:center; }
.harfler { font-family:'Amiri',serif; font-size:64pt; line-height:1.1; letter-spacing:.3em; direction:rtl; color:#0f172a; }
.imge { font-size:19pt; font-weight:700; margin:6px 0 10px; color:var(--vurgu); }
.kapsul p { max-width:640px; margin:6px auto; color:#334155; }
.sayi { color:var(--sessiz); font-size:10pt; margin-top:10px; }
h2 { font-size:15pt; margin:34px 0 10px; color:var(--vurgu); }
h2 small { font-weight:400; color:var(--sessiz); font-size:10pt; }
.sahne { background:#fffbeb; border-left:4px solid #d97706; padding:12px 16px; border-radius:6px; }
.sahne b { color:var(--vurgu); }
/* şecere */
.agac { margin:0; padding:0; list-style:none; }
.agac ul { list-style:none; margin:0 0 0 22px; padding:0 0 0 18px; border-left:2px solid #cbd5e1; }
.dal { position:relative; margin:10px 0; }
.dal::before { content:''; position:absolute; left:-18px; top:20px; width:18px; border-top:2px solid #cbd5e1; }
.agac > .dal::before { display:none; }
.dugum { background:var(--kart); border:2px solid var(--renk,#94a3b8); border-radius:10px; padding:8px 12px; cursor:pointer; }
.dugum.tahmin { border-style:dashed; background:#f8fafc; }
.dugum .ad { font-weight:700; }
.dugum .rozet { font-size:8.5pt; padding:1px 7px; border-radius:99px; margin-left:6px; color:#fff; background:#15803d; white-space:nowrap; }
.dugum.tahmin .rozet { background:#64748b; }
.dugum .mana { font-size:10.5pt; color:#334155; }
.dugum .ayrinti { display:none; margin-top:6px; font-size:10pt; color:#475569; border-top:1px solid var(--cizgi); padding-top:6px; }
.dal.acik > .dugum .ayrinti { display:block; }
.dugum .kelime { font-family:'Amiri',serif; font-size:14pt; direction:rtl; display:block; text-align:right; color:#0f172a; }
.gosterge { font-size:9.5pt; color:var(--sessiz); margin:6px 0 12px; }
.gosterge span { margin-right:14px; display:inline-block; }
.gosterge i { display:inline-block; width:26px; height:0; border-top:2px solid #475569; vertical-align:middle; margin-right:5px; }
.gosterge i.k { border-top-style:dashed; }
/* âyet haritası */
.ayetler { display:grid; gap:12px; }
.ayet { background:var(--kart); border:1px solid var(--cizgi); border-right:6px solid var(--renk,#94a3b8); border-radius:10px; padding:12px 14px; }
.ayet.vurgulu { box-shadow:0 0 0 3px var(--renk,#f59e0b); }
.ayet .ayar { font-family:'Amiri',serif; font-size:20pt; line-height:2; direction:rtl; text-align:right; }
.ayet .ayar mark { background:var(--zemin-renk,#fde68a); color:inherit; border-radius:5px; padding:0 3px; }
.ayet .meal { color:#334155; font-size:11pt; }
.ayet .etiket { font-size:9.5pt; color:var(--sessiz); margin-bottom:4px; }
.ayet .etiket b { color:var(--renk,#334155); }
/* komşular */
.komsu { display:grid; gap:10px; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); }
.komsu div { background:var(--kart); border:1px solid var(--cizgi); border-radius:10px; padding:10px 14px; }
.komsu .kk { font-family:'Amiri',serif; font-size:20pt; direction:rtl; display:block; text-align:right; color:#0f172a; }
/* sorular */
details.soru { background:var(--kart); border:1px solid var(--cizgi); border-radius:8px; margin:8px 0; }
details.soru > summary { cursor:pointer; padding:9px 14px; font-weight:600; }
details.soru > div { padding:2px 14px 12px; color:#334155; }
details.serh > summary { cursor:pointer; padding:10px 14px; font-weight:700; background:var(--kart); border:1px solid var(--cizgi); border-radius:8px; }
details.serh .ic { background:var(--kart); border:1px solid var(--cizgi); border-top:0; padding:6px 18px 16px; }
details.serh h2 { font-size:13pt; }
.gecisler { display:flex; flex-wrap:wrap; gap:5px; margin-top:8px; }
.gecisler span { font-size:9pt; background:#eef2f7; border-radius:6px; padding:2px 7px; color:#475569; }

.cebir h3 { font-size:12.5pt; margin:22px 0 8px; color:var(--vurgu); }
.cebir .giris { font-size:11.5pt; }
.formul { background:var(--kart); border:1px solid var(--cizgi); border-radius:12px; padding:6px 14px; margin:12px 0; }
.formul .satir { display:grid; grid-template-columns:78px minmax(150px,230px) 1fr; gap:12px; align-items:baseline; padding:9px 0; border-bottom:1px solid var(--cizgi); }
.formul .satir:last-child { border-bottom:0; }
.formul .ad { font-weight:700; color:var(--vurgu); font-size:10.5pt; }
.formul .f { font-family:'Cambria Math','STIX Two Math',Georgia,serif; font-size:13.5pt; }
.formul .a { color:var(--sessiz); font-size:10pt; }
table.roller { width:100%; border-collapse:collapse; font-size:10pt; background:var(--kart); border:1px solid var(--cizgi); border-radius:10px; overflow:hidden; }
table.roller th, table.roller td { padding:7px 9px; text-align:left; border-bottom:1px solid var(--cizgi); vertical-align:top; }
table.roller th { background:#f1ede1; font-size:9.5pt; }
table.roller tr.vur td { background:#fffbeb; }
table.roller td:first-child { font-family:'Amiri',serif; font-size:13pt; white-space:nowrap; }
table.roller td.y { color:#15803d; font-weight:700; } table.roller td.t { color:var(--sessiz); }
svg.sema { width:100%; height:auto; margin:14px 0; background:var(--kart); border:1px solid var(--cizgi); border-radius:12px; color:var(--yazi); }
svg.sema .bas { font:700 13px 'Plus Jakarta Sans',sans-serif; text-anchor:middle; fill:var(--vurgu); }
svg.sema .e { font:12px Georgia,serif; text-anchor:middle; fill:currentColor; }
svg.sema .eks { stroke:var(--cizgi); stroke-width:1.5; }
svg.sema .p { fill:#0f766e; } svg.sema .x { fill:#b45309; }
svg.sema .yay { fill:none; stroke:#475569; stroke-width:2; } svg.sema .yay.kopuk { stroke-dasharray:3 4; opacity:.55; }
svg.sema .K { stroke:#b91c1c; stroke-width:2.4; color:#b91c1c; } svg.sema .don { fill:none; stroke:#0f766e; stroke-width:2.2; color:#0f766e; }
svg.sema .eps { stroke:#64748b; stroke-width:1.5; stroke-dasharray:4 3; }
ol.netice { padding-left:20px; } ol.netice li { margin:10px 0; }
.sinir { background:#fffbeb; border-left:4px solid #d97706; padding:10px 14px; border-radius:6px; font-size:10.5pt; }
@media (max-width:620px) { .formul .satir { grid-template-columns:1fr; gap:2px; } table.roller { font-size:9pt; } }
@media (prefers-color-scheme:dark) { table.roller th { background:#1a2438; } table.roller tr.vur td { background:#1c1608; } .sinir { background:#1c1608; } svg.sema .K { stroke:#f87171; color:#f87171; } svg.sema .don { stroke:#34d399; color:#34d399; } }
@media (max-width:560px) { .harfler { font-size:48pt; } .imge { font-size:15pt; } }
@media (prefers-color-scheme:dark) {
  :root { --zemin:#0b1220; --kart:#111a2c; --yazi:#e2e8f0; --sessiz:#94a3b8; --cizgi:#243247; --vurgu:#fbbf24; }
  .harfler, .dugum .kelime, .komsu .kk { color:#f1f5f9; }
  .dugum .mana, .ayet .meal, .kapsul p, details.soru > div { color:#cbd5e1; }
  .dugum.tahmin { background:#0f172a; }
  .sahne { background:#1c1608; }
  .gecisler span { background:#1e293b; color:#cbd5e1; }
}
"""

JS = """
document.querySelectorAll('.dugum').forEach(function(d){
  d.addEventListener('click', function(){
    var dal = d.parentElement; dal.classList.toggle('acik');
    var id = dal.getAttribute('data-id');
    document.querySelectorAll('.ayet').forEach(function(a){
      a.classList.toggle('vurgulu', dal.classList.contains('acik') && a.getAttribute('data-dal') === id);
    });
    var ilk = document.querySelector('.ayet.vurgulu');
    if (ilk && dal.classList.contains('acik')) ilk.scrollIntoView({behavior:'smooth', block:'center'});
  });
});
document.querySelectorAll('.ayet').forEach(function(a){
  a.addEventListener('click', function(){
    var id = a.getAttribute('data-dal');
    var dal = document.querySelector('.dal[data-id="' + id + '"]');
    if (dal) { dal.classList.add('acik'); dal.scrollIntoView({behavior:'smooth', block:'center'}); }
  });
});
"""


def morfoloji_oku(kok):
    """kök -> ((sure, ayet) -> [(kelime, kökten_mi)]), bütün geçiş anahtarları, bütün âyetlerin kelime dizisi."""
    kelimeler = {}
    gecis = []
    with open(MORFOLOJI, encoding="utf-8") as f:
        for satir in f:
            p = satir.rstrip("\n").split("\t")
            if len(p) < 4:
                continue
            sure, ayet, no, _ = (int(x) for x in p[0].split(":"))
            kokte = f"ROOT:{kok}" in p[3]
            kelimeler.setdefault((sure, ayet), {}).setdefault(no, ["", False])
            kelimeler[(sure, ayet)][no][0] += p[1]
            kelimeler[(sure, ayet)][no][1] = kelimeler[(sure, ayet)][no][1] or kokte
            if kokte:
                gecis.append((sure, ayet))
    return kelimeler, sorted(set(gecis))


def meal_oku(sure, ayet, onbellek):
    if sure not in onbellek:
        onbellek[sure] = json.loads((BASE_DIR / "kaynak" / "sure" / f"{sure}.json").read_text(encoding="utf-8"))["verses"]
    for v in onbellek[sure]:
        if v["verseNumber"] == ayet:
            return re.sub(r"<[^>]+>", "", v["turkish"].get(MEAL_ANAHTAR, "") or "")
    return ""


def dal_listesi(dallar, derinlik=0):
    for d in dallar:
        yield d, derinlik
        yield from dal_listesi(d.get("alt", []), derinlik + 1)


def dal_html(d, renk_ana):
    renk = d.get("renk", renk_ana)
    tahmin = d.get("derece") == "tahmin"
    rozet = "tahmin" if tahmin else "yazılı"
    alt = "".join(dal_html(a, renk) for a in d.get("alt", []))
    alt_html = f"<ul>{alt}</ul>" if alt else ""
    return (
        f'<li class="dal" data-id="{escape(d["id"])}"><div class="dugum{" tahmin" if tahmin else ""}" style="--renk:{renk}">'
        f'<div><span class="ad">{escape(d["ad"])}</span><span class="rozet">{rozet}</span></div>'
        f'<div class="mana">{escape(d["mana"])}</div>'
        f'<div class="ayrinti"><span class="kelime">{escape(d["kelime"])}</span>Kaynak: {escape(d["kaynak"])}</div></div>'
        f'{alt_html}</li>'
    )


def sayfa_uret(kok, md_conv):
    veri = json.loads((PILOT_DIZIN / f"{kok}.json").read_text(encoding="utf-8"))
    kelimeler, gecis = morfoloji_oku(kok)
    meal_onbellek = {}
    renk_dal = {}
    for ust in veri["dallar"]:
        for d, _ in dal_listesi([ust]):
            renk_dal[d["id"]] = ust.get("renk", "#475569")
    ayet_kartlari = []
    gorulen = set()
    for d, _ in dal_listesi(veri["dallar"]):
        for anahtar in d.get("ayetler", []):
            if anahtar in gorulen:
                continue
            gorulen.add(anahtar)
            sure, ayet = (int(x) for x in anahtar.split(":"))
            assert (sure, ayet) in gecis, f"{anahtar} bu kökü içermiyor"
            parcalar = kelimeler[(sure, ayet)]
            ar = " ".join(
                (f"<mark>{escape(k)}</mark>" if kok_mu else escape(k))
                for _, (k, kok_mu) in sorted(parcalar.items())
            )
            renk = renk_dal[d["id"]]
            ayet_kartlari.append(
                f'<div class="ayet" data-dal="{escape(d["id"])}" style="--renk:{renk}">'
                f'<div class="etiket"><b>{anahtar}</b> · {escape(d["ad"])}</div>'
                f'<div class="ayar">{ar}</div><div class="meal">{escape(meal_oku(sure, ayet, meal_onbellek))}</div></div>'
            )
    agac = "".join(dal_html(d, "#475569") for d in veri["dallar"])
    komsular = "".join(
        f'<div><span class="kk">{escape(k["kok"])}</span>{escape(k["fark"])}'
        f'{f" <small>(" + escape(k["ayet"]) + ")</small>" if k.get("ayet") else ""}</div>'
        for k in veri["komsular"]
    )
    sorular = "".join(
        f'<details class="soru"><summary>{escape(q["s"])}</summary><div>{escape(q["c"])}</div></details>'
        for q in veri["sorular"]
    )
    md_conv.reset()
    serh = md_conv.convert((ETIM_DIZIN / f"{kok}.md").read_text(encoding="utf-8"))
    chips = "".join(f"<span>{s}:{a}</span>" for s, a in gecis)
    k = veri["kapsul"]
    cebir_yol = PILOT_DIZIN / f"{kok}.cebir.html"
    cebir = (f'<h2>Mana cebiri <small>sabır neyin fonksiyonudur</small></h2><div class="cebir">{cebir_yol.read_text(encoding="utf-8")}</div>') if cebir_yol.exists() else ""
    return f"""<!DOCTYPE html>
<html lang="tr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(kok)} · Kök sayfası</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=Amiri:wght@400;700&display=swap" rel="stylesheet">
<style>{STIL}</style></head><body>
<div class="ust"><a href="../kuran_hikmetleri_lugat.html">← Lugat</a></div>
<main>
<section class="kapsul">
<div class="harfler">{" ".join(escape(h) for h in veri["harfler"])}</div>
<div class="imge">{escape(k["imge"])}</div>
<p>{escape(k["aciklama"])}</p>
<div class="sayi">{escape(k["sayi"])}</div>
</section>

<h2>Gövde <small>kökün asıl sahnesi</small></h2>
<div class="sahne"><b>{escape(veri["sahne"]["baslik"])}.</b> {escape(veri["sahne"]["metin"])}</div>

{cebir}

<h2>Şecere <small>bir dala dokun: kelimeyi, kaynağı ve âyetini gör</small></h2>
<div class="gosterge"><span><i></i>lügatte yazılı bağ</span><span><i class="k"></i>tahmin ya da yazılı olmayan bağ</span></div>
<ul class="agac">{agac}</ul>

<h2>Âyet haritası <small>renk, dalın rengidir; âyete dokununca dalına gidilir</small></h2>
<div class="ayetler">{"".join(ayet_kartlari)}</div>

<h2>Komşu kökler <small>fark, karışmayı önler</small></h2>
<div class="komsu">{komsular}</div>

<h2>Önce kendin hatırla</h2>
{sorular}

<h2>Tam şerh</h2>
<details class="serh"><summary>Kaynak nakilleriyle uzun şerhi aç</summary><div class="ic">{serh}</div></details>

<h2>Kur'ân'daki bütün geçişler <small>{len(gecis)} âyet</small></h2>
<div class="gecisler">{chips}</div>
</main>
<script>{JS}</script>
</body></html>"""


def hepsini_uret(md_conv):
    """Pilot JSON'u bulunan her kök için kok/<kök>.html yazar; üretilen köklerin kümesini döndürür."""
    CIKTI_DIZIN.mkdir(exist_ok=True)
    uretilen = set()
    for p in sorted(PILOT_DIZIN.glob("*.json")) if PILOT_DIZIN.exists() else []:
        (CIKTI_DIZIN / f"{p.stem}.html").write_text(sayfa_uret(p.stem, md_conv), encoding="utf-8")
        uretilen.add(p.stem)
    return uretilen
