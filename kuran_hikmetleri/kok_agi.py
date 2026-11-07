#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kök ağı: Kur'ân'ın kök haritası.

Her âyette birlikte geçen kökler arasında normalleştirilmiş karşılıklı bilgi (NPMI) hesaplanır;
en güçlü bağlar çizge olur, Louvain ile topluluklara ayrılır, Fruchterman-Reingold ile yerleştirilir.
Çıktı tek dosyalık etkileşimli sayfadır: kok_agi.html. Etimolojisi mühürlü kökler altın halkalıdır.
Sabit tohum kullanılır; aynı veri aynı haritayı verir.
"""

import collections
import json
import math
import re
from pathlib import Path

import networkx as nx

BASE_DIR = Path(__file__).resolve().parent
MORFOLOJI = BASE_DIR / "veri_harici" / "eyupipler" / "quran-morphology.txt"
KOK_ANLAM = BASE_DIR / "kaynak" / "lugat" / "kok_anlamlari.json"
ETIM = BASE_DIR / "kaynak" / "lugat" / "etimoloji"
PILOT = BASE_DIR / "kaynak" / "lugat" / "pilot"
CIKTI = BASE_DIR / "kok_agi.html"

DUGUM_SAYISI = 650
EN_AZ_ORTAK = 4
KOMSU = 6
TOHUM = 7


def ayet_kokleri():
    ay = collections.defaultdict(set)
    with open(MORFOLOJI, encoding="utf-8") as f:
        for satir in f:
            p = satir.rstrip("\n").split("\t")
            if len(p) < 4:
                continue
            m = re.search(r"ROOT:([^|]+)", p[3])
            if m:
                sure, ayet, _, _ = p[0].split(":")
                ay[(sure, ayet)].add(m.group(1))
    return ay


def kisa_anlam(t):
    t = re.split(r"[;:(/]", t)[0].strip()
    return t[:34]


def uret():
    ay = ayet_kokleri()
    n_ayet = len(ay)
    sayac = collections.Counter(k for v in ay.values() for k in v)
    secilen = [k for k, _ in sayac.most_common(DUGUM_SAYISI)]
    kume = set(secilen)
    ortak = collections.Counter()
    for v in ay.values():
        x = sorted(v & kume)
        for i in range(len(x)):
            for j in range(i + 1, len(x)):
                ortak[(x[i], x[j])] += 1
    adaylar = collections.defaultdict(list)
    for (a, b), c in ortak.items():
        if c < EN_AZ_ORTAK:
            continue
        pij = c / n_ayet
        pmi = math.log(pij / ((sayac[a] / n_ayet) * (sayac[b] / n_ayet)))
        npmi = pmi / (-math.log(pij))
        if npmi <= 0.05:
            continue
        adaylar[a].append((npmi, b, c))
        adaylar[b].append((npmi, a, c))
    kenar = {}
    for k, lst in adaylar.items():
        for npmi, o, c in sorted(lst, reverse=True)[:KOMSU]:
            kenar[tuple(sorted((k, o)))] = (npmi, c)
    G = nx.Graph()
    G.add_nodes_from(secilen)
    for (a, b), (w, c) in kenar.items():
        G.add_edge(a, b, weight=w, ortak=c)
    dev = max(nx.connected_components(G), key=len)
    G = G.subgraph(dev).copy()
    secilen = [k for k in secilen if k in dev]
    topluluk = nx.community.louvain_communities(G, weight="weight", seed=TOHUM, resolution=1.0)
    topluluk = sorted(topluluk, key=lambda s: -sum(sayac[k] for k in s))
    kimlik = {k: i for i, s in enumerate(topluluk) for k in s}
    for a, b, d in G.edges(data=True):
        d["yerlesim"] = d["weight"] * (6.0 if kimlik[a] == kimlik[b] else 0.7)
    kb = nx.circular_layout(nx.path_graph(len(topluluk)))
    ilk = {k: (kb[kimlik[k]][0] * 1.0, kb[kimlik[k]][1] * 1.0) for k in G.nodes}
    konum = nx.spring_layout(G, weight="yerlesim", pos=ilk, k=2.4 / math.sqrt(len(G)), iterations=500, seed=TOHUM)

    anlam = {x["kok"]: x["turkce"] for x in json.loads(KOK_ANLAM.read_text(encoding="utf-8"))}
    muhurlu = {p.stem for p in ETIM.glob("*.md")}
    pilot = {p.stem for p in PILOT.glob("*.json")}

    sira = {k: i for i, k in enumerate(secilen)}
    dugumler = []
    xs = [konum[k][0] for k in secilen]
    ys = [konum[k][1] for k in secilen]
    def yuzdelik(v, q):
        v = sorted(v)
        return v[int(q * (len(v) - 1))]
    x0, x1, y0, y1 = yuzdelik(xs, .02), yuzdelik(xs, .98), yuzdelik(ys, .02), yuzdelik(ys, .98)
    for k in secilen:
        dugumler.append({
            "k": k,
            "x": round(min(1.04, max(-.04, (konum[k][0] - x0) / (x1 - x0))), 4),
            "y": round(min(1.04, max(-.04, (konum[k][1] - y0) / (y1 - y0))), 4),
            "f": sayac[k],
            "c": kimlik[k],
            "a": anlam.get(k, ""),
            "e": 1 if k in muhurlu else 0,
            "p": 1 if k in pilot else 0,
        })
    kenarlar = [[sira[a], sira[b], round(w, 3), c] for (a, b), (w, c) in kenar.items()]
    topluluklar = []
    for i, s in enumerate(topluluk):
        ust = sorted(s, key=lambda k: -sayac[k])[:4]
        uyeler = [d for d in dugumler if d["c"] == i]
        topluluklar.append({
            "cx": round(sum(d["x"] for d in uyeler) / len(uyeler), 4),
            "cy": round(sum(d["y"] for d in uyeler) / len(uyeler), 4),
            "ad": " · ".join(kisa_anlam(anlam.get(k, k)) or k for k in ust[:3]),
            "n": len(s),
            "kokler": ust,
        })
    return {"dugumler": dugumler, "kenarlar": kenarlar, "topluluklar": topluluklar,
            "ayet": n_ayet, "kok": len(sayac)}


SAYFA = r"""<!DOCTYPE html>
<html lang="tr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kök Ağı · Kur'ân'ın kök haritası</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=Amiri:wght@400;700&display=swap" rel="stylesheet">
<style>
:root { --z:#0b1220; --y:#e2e8f0; --s:#94a3b8; --k:#111a2c; --c:#243247; --v:#fbbf24; }
* { box-sizing:border-box; }
html,body { margin:0; height:100%; background:var(--z); color:var(--y); font-family:'Plus Jakarta Sans',system-ui,sans-serif; overflow:hidden; }
#alan { position:fixed; inset:0; touch-action:none; cursor:grab; }
#alan.tut { cursor:grabbing; }
canvas { display:block; width:100%; height:100%; }
.ust { position:fixed; top:0; left:0; right:0; padding:10px 14px; display:flex; flex-wrap:wrap; gap:10px; align-items:center; background:linear-gradient(#0b1220f2,#0b122000); z-index:3; pointer-events:none; }
.ust > * { pointer-events:auto; }
.ust h1 { font-size:14pt; margin:0 12px 0 0; }
.ust h1 small { font-weight:400; color:var(--s); font-size:9.5pt; display:block; }
.ust a { color:var(--v); text-decoration:none; font-weight:700; font-size:10pt; }
#ara { padding:8px 11px; border-radius:9px; border:1px solid var(--c); background:var(--k); color:var(--y); font-size:11pt; width:220px; }
#tip { position:fixed; pointer-events:none; background:#0f172aee; border:1px solid var(--c); border-radius:8px; padding:6px 10px; font-size:10pt; display:none; z-index:4; max-width:260px; }
#tip .ar { font-family:'Amiri',serif; font-size:18pt; line-height:1.2; }
#panel { position:fixed; top:0; right:0; bottom:0; width:min(380px,100%); background:var(--k); border-left:1px solid var(--c); transform:translateX(100%); transition:transform .22s; z-index:5; overflow-y:auto; padding:16px 16px 40px; }
#panel.acik { transform:none; }
#panel .kapat { position:absolute; top:8px; right:12px; background:none; border:0; color:var(--s); font-size:20pt; cursor:pointer; }
#panel .ar { font-family:'Amiri',serif; font-size:42pt; direction:rtl; line-height:1.1; }
#panel h2 { font-size:12pt; margin:18px 0 6px; color:var(--v); }
#panel .anlam { color:#cbd5e1; font-size:11pt; }
#panel .rozet { display:inline-block; font-size:9pt; padding:2px 9px; border-radius:99px; margin-right:6px; background:#1e293b; color:var(--y); }
#panel .komsu { display:flex; flex-wrap:wrap; gap:6px; }
#panel .komsu button { background:#1e293b; border:1px solid var(--c); color:var(--y); border-radius:8px; padding:3px 9px; cursor:pointer; font-size:10pt; }
#panel .komsu button .ar2 { font-family:'Amiri',serif; font-size:15pt; margin-right:6px; }
#panel .etim { background:#fffbeb; color:#1e293b; border-radius:8px; padding:4px 14px; font-size:10pt; line-height:1.6; margin-top:6px; }
#panel .etim h2 { color:#92400e; font-size:11.5pt; }
#panel a.git { display:inline-block; margin-top:8px; color:#0f172a; background:var(--v); text-decoration:none; font-weight:700; padding:6px 14px; border-radius:8px; }
#lejant { position:fixed; left:12px; bottom:12px; background:#0f172aee; border:1px solid var(--c); border-radius:10px; padding:8px 10px; font-size:9.5pt; z-index:3; max-height:42vh; overflow:auto; max-width:min(330px,70vw); }
#lejant div { display:flex; gap:7px; align-items:center; padding:2px 0; cursor:pointer; }
#lejant div.sonuk { opacity:.3; }
#lejant i { width:11px; height:11px; border-radius:50%; flex:none; }
#alt { position:fixed; right:12px; bottom:12px; color:var(--s); font-size:9pt; z-index:2; text-align:right; }
@media (max-width:640px) { #ara { width:150px; } #lejant { max-height:28vh; font-size:8.5pt; } .ust h1 small { display:none; } }
</style></head><body>
<div id="alan"><canvas id="cv"></canvas></div>
<div class="ust"><h1>Kök Ağı<small>@AYET@ âyet · @KOK@ kök · @SECILEN@ kök haritada</small></h1>
<input id="ara" type="search" placeholder="kök ara: صبر, sabır, kalp…" autocomplete="off">
<a href="kuran_hikmetleri_lugat.html">Lugat</a></div>
<div id="tip"></div>
<aside id="panel"><button class="kapat" onclick="kapat()">×</button><div id="pi"></div></aside>
<div id="lejant"></div>
<div id="alt">Aynı âyette birlikte geçen kökler yakın durur.<br>Altın halka: etimolojisi yazılı kök.</div>
<script>
var V = @VERI@;
var cv = document.getElementById('cv'), cx = cv.getContext('2d');
var N = V.dugumler, E = V.kenarlar, T = V.topluluklar;
var W = 0, H = 0, dpr = Math.min(2, window.devicePixelRatio || 1);
var gor = { x:0, y:0, z:1 }, secili = -1, ustte = -1, gizli = {};
var komsu = N.map(function(){ return []; });
E.forEach(function(e){ komsu[e[0]].push([e[1], e[2], e[3]]); komsu[e[1]].push([e[0], e[2], e[3]]); });
komsu.forEach(function(l){ l.sort(function(a,b){ return b[1]-a[1]; }); });
function renk(c, a){ return 'hsla(' + ((c * 137.508) % 360) + ',68%,' + (c % 2 ? 62 : 54) + '%,' + (a == null ? 1 : a) + ')'; }
function yeniden(){
  W = innerWidth; H = innerHeight; cv.width = W * dpr; cv.height = H * dpr;
  var m = Math.min(W, H) * 0.9; gor.s = m; gor.ox = (W - m) / 2; gor.oy = (H - m) / 2 + 24;
  ciz();
}
function ekran(n){ return [ (n.x * gor.s + gor.ox) * gor.z + gor.x, (n.y * gor.s + gor.oy) * gor.z + gor.y ]; }
function yar(n){ return (2.6 + Math.sqrt(n.f) * 0.42) * Math.sqrt(gor.z); }
var kuyruk = 0;
function ciz(){ if (kuyruk) return; kuyruk = requestAnimationFrame(cizAsil); }
function cizAsil(){
  kuyruk = 0;
  cx.setTransform(dpr, 0, 0, dpr, 0, 0);
  cx.clearRect(0, 0, W, H);
  var sec = secili >= 0 ? secili : ustte;
  var yakin = {};
  if (sec >= 0) { yakin[sec] = 1; komsu[sec].forEach(function(k){ yakin[k[0]] = 1; }); }
  cx.lineWidth = 0.6;
  for (var i = 0; i < E.length; i++) {
    var e = E[i], a = N[e[0]], b = N[e[1]];
    if (gizli[a.c] || gizli[b.c]) continue;
    var vur = sec >= 0 && (e[0] === sec || e[1] === sec);
    if (sec >= 0 && !vur) { cx.strokeStyle = 'rgba(148,163,184,0.05)'; }
    else if (vur) { cx.strokeStyle = 'rgba(251,191,36,0.85)'; cx.lineWidth = 1.4; }
    else { cx.strokeStyle = 'rgba(148,163,184,' + (0.06 + e[2] * 0.16) + ')'; }
    var pa = ekran(a), pb = ekran(b);
    cx.beginPath(); cx.moveTo(pa[0], pa[1]); cx.lineTo(pb[0], pb[1]); cx.stroke();
    cx.lineWidth = 0.6;
  }
  var etiket = [];
  for (var j = 0; j < N.length; j++) {
    var n = N[j]; if (gizli[n.c]) continue;
    var p = ekran(n); if (p[0] < -20 || p[0] > W + 20 || p[1] < -20 || p[1] > H + 20) continue;
    var soluk = sec >= 0 && !yakin[j];
    cx.globalAlpha = soluk ? 0.18 : 1;
    cx.fillStyle = renk(n.c); cx.beginPath(); cx.arc(p[0], p[1], yar(n), 0, 6.2832); cx.fill();
    if (n.e) { cx.strokeStyle = '#fbbf24'; cx.lineWidth = 2.2; cx.beginPath(); cx.arc(p[0], p[1], yar(n) + 2.5, 0, 6.2832); cx.stroke(); cx.lineWidth = 0.6; }
    if (n.p) { cx.strokeStyle = '#34d399'; cx.lineWidth = 2; cx.beginPath(); cx.arc(p[0], p[1], yar(n) + 6, 0, 6.2832); cx.stroke(); cx.lineWidth = 0.6; }
    cx.globalAlpha = 1;
    if (!soluk && (gor.z > 2.2 || n.f > 520 / Math.pow(gor.z, 1.6) || yakin[j] || j === ustte)) etiket.push([n, p]);
  }
  cx.textAlign = 'center'; cx.textBaseline = 'middle';
  if (gor.z < 2.4 && sec < 0) {
    cx.globalAlpha = Math.max(0, Math.min(1, (2.4 - gor.z) / 1.2));
    T.slice(0, 14).forEach(function(t, i){
      if (gizli[i]) return;
      var q = ekran({ x: t.cx, y: t.cy });
      cx.font = '700 ' + (12 + Math.min(6, Math.sqrt(t.n) * 0.7)) + 'px "Plus Jakarta Sans", sans-serif';
      cx.fillStyle = 'rgba(2,6,23,0.55)'; var ad = t.ad.split(' · ')[0]; var w = cx.measureText(ad).width + 14;
      cx.beginPath(); cx.roundRect ? cx.roundRect(q[0] - w / 2, q[1] - 11, w, 22, 8) : cx.rect(q[0] - w / 2, q[1] - 11, w, 22); cx.fill();
      cx.fillStyle = renk(i); cx.fillText(ad, q[0], q[1]);
    });
    cx.globalAlpha = 1;
  }
  etiket.forEach(function(t){
    var s = Math.min(24, 11 + Math.sqrt(t[0].f) * 0.11 * Math.sqrt(gor.z));
    cx.font = s + "px Amiri, serif"; cx.fillStyle = '#f8fafc';
    cx.shadowColor = '#0b1220'; cx.shadowBlur = 5; cx.fillText(t[0].k, t[1][0], t[1][1] - yar(t[0]) - s * 0.55); cx.shadowBlur = 0;
  });
}
function en_yakin(mx, my){
  var en = -1, d = 1e9;
  for (var i = 0; i < N.length; i++) {
    if (gizli[N[i].c]) continue;
    var p = ekran(N[i]), dx = p[0] - mx, dy = p[1] - my, dd = dx * dx + dy * dy, r = yar(N[i]) + 5;
    if (dd < r * r && dd < d) { d = dd; en = i; }
  }
  return en;
}
var alan = document.getElementById('alan'), tip = document.getElementById('tip');
var ptr = {}, surukle = false, ilkD = 0, ilkZ = 1, hareket = 0;
alan.addEventListener('pointerdown', function(e){ alan.setPointerCapture(e.pointerId); ptr[e.pointerId] = [e.clientX, e.clientY]; hareket = 0; alan.classList.add('tut'); if (Object.keys(ptr).length === 2) { var k = Object.values(ptr); ilkD = Math.hypot(k[0][0]-k[1][0], k[0][1]-k[1][1]); ilkZ = gor.z; } });
alan.addEventListener('pointermove', function(e){
  var onceki = ptr[e.pointerId];
  if (onceki) {
    var ks = Object.keys(ptr).length;
    if (ks === 1) { gor.x += e.clientX - onceki[0]; gor.y += e.clientY - onceki[1]; hareket += Math.abs(e.clientX - onceki[0]) + Math.abs(e.clientY - onceki[1]); ptr[e.pointerId] = [e.clientX, e.clientY]; tip.style.display = 'none'; ciz(); }
    else { ptr[e.pointerId] = [e.clientX, e.clientY]; var k = Object.values(ptr); var d = Math.hypot(k[0][0]-k[1][0], k[0][1]-k[1][1]); yakinlas((k[0][0]+k[1][0])/2, (k[0][1]+k[1][1])/2, ilkZ * d / ilkD / gor.z); hareket += 9; }
    return;
  }
  var i = en_yakin(e.clientX, e.clientY);
  if (i !== ustte) { ustte = i; ciz(); }
  if (i >= 0) { var n = N[i]; tip.innerHTML = '<span class="ar">' + n.k + '</span><br>' + (n.a || '').split(';')[0] + '<br><span style="color:#94a3b8">' + n.f + ' âyet</span>'; tip.style.left = Math.min(e.clientX + 14, W - 270) + 'px'; tip.style.top = (e.clientY + 14) + 'px'; tip.style.display = 'block'; } else tip.style.display = 'none';
});
alan.addEventListener('pointerup', function(e){
  delete ptr[e.pointerId]; alan.classList.remove('tut');
  if (hareket < 6) { var i = en_yakin(e.clientX, e.clientY); if (i >= 0) sec(i); else if (secili >= 0) kapat(); }
});
alan.addEventListener('pointercancel', function(e){ delete ptr[e.pointerId]; alan.classList.remove('tut'); });
function yakinlas(mx, my, oran){ var z = Math.max(0.5, Math.min(14, gor.z * oran)); oran = z / gor.z; gor.x = mx - (mx - gor.x) * oran; gor.y = my - (my - gor.y) * oran; gor.z = z; ciz(); }
alan.addEventListener('wheel', function(e){ e.preventDefault(); yakinlas(e.clientX, e.clientY, Math.exp(-e.deltaY * 0.0015)); }, { passive:false });
function git(i){ var p = [N[i].x * gor.s + gor.ox, N[i].y * gor.s + gor.oy]; gor.z = Math.max(gor.z, 2.6); gor.x = W * 0.35 - p[0] * gor.z; gor.y = H / 2 - p[1] * gor.z; ciz(); }
function sec(i){
  secili = i; ciz(); git(i);
  var n = N[i], p = document.getElementById('pi');
  var h = '<div class="ar">' + n.k + '</div><div class="anlam">' + (n.a || 'anlamı henüz yazılmadı') + '</div>';
  h += '<div style="margin-top:10px"><span class="rozet">' + n.f + ' âyet</span><span class="rozet" style="background:' + renk(n.c, .35) + '">' + T[n.c].ad + '</span></div>';
  h += '<h2>En yakın kökler</h2><div class="komsu">' + komsu[i].slice(0, 14).map(function(k){ var m = N[k[0]]; return '<button onclick="sec(' + k[0] + ')" title="' + k[2] + ' âyette birlikte"><span class="ar2">' + m.k + '</span>' + ((m.a || '').split(/[;:]/)[0].slice(0, 16)) + '</button>'; }).join('') + '</div>';
  if (n.p) h += '<a class="git" href="kok/' + encodeURIComponent(n.k) + '.html">Kök sayfasını aç →</a>';
  h += '<div id="etim"></div>';
  p.innerHTML = h; document.getElementById('panel').classList.add('acik');
  if (n.e) fetch('etimoloji/' + encodeURIComponent(n.k) + '.html').then(function(r){ return r.text(); }).then(function(t){ document.getElementById('etim').innerHTML = '<h2>Etimoloji</h2><div class="etim">' + t + '</div>'; }).catch(function(){});
}
function kapat(){ secili = -1; document.getElementById('panel').classList.remove('acik'); ciz(); }
var lej = document.getElementById('lejant');
lej.innerHTML = T.slice(0, 14).map(function(t, i){ return '<div data-c="' + i + '"><i style="background:' + renk(i) + '"></i>' + t.ad + ' <span style="color:#94a3b8">(' + t.n + ')</span></div>'; }).join('');
lej.addEventListener('click', function(e){ var d = e.target.closest('div[data-c]'); if (!d) return; var c = +d.getAttribute('data-c'); gizli[c] = !gizli[c]; d.classList.toggle('sonuk', !!gizli[c]); ciz(); });
var ara = document.getElementById('ara');
ara.addEventListener('input', function(){
  var q = ara.value.trim(); if (!q) return;
  var d = q.replace(/[ً-ٰ]/g, '');
  var i = N.findIndex(function(n){ return n.k === d; });
  if (i < 0) i = N.findIndex(function(n){ return (n.a || '').toLowerCase().indexOf(q.toLowerCase()) >= 0; });
  if (i >= 0) sec(i);
});
addEventListener('resize', yeniden); yeniden();
</script></body></html>
"""


def yaz():
    v = uret()
    sayfa = (SAYFA.replace("@VERI@", json.dumps(v, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
             .replace("@AYET@", str(v["ayet"])).replace("@KOK@", str(v["kok"])).replace("@SECILEN@", str(len(v["dugumler"]))))
    CIKTI.write_text(sayfa, encoding="utf-8")
    return v


if __name__ == "__main__":
    v = yaz()
    print(len(v["dugumler"]), "düğüm", len(v["kenarlar"]), "kenar", len(v["topluluklar"]), "topluluk")
    for i, t in enumerate(v["topluluklar"][:12]):
        print(i, t["n"], t["ad"])
