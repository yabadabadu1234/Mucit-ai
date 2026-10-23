(function () {
'use strict';
var kok = document.getElementById('gezgin');
if (!kok) return;
var VERI = JSON.parse(document.getElementById('gezgin-veri').textContent);
function $(s, k) { return (k || document).querySelector(s); }
function $$(s, k) { return Array.prototype.slice.call((k || document).querySelectorAll(s)); }
function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
function nitel(s) { return String(s).replace(/\\/g, '\\\\').replace(/"/g, '\\"'); }
function virgul(x) { return String(x).replace('.', ','); }

var semaSvg = $('#sema-svg'), kartSvg = $('#kart-svg'), bilgi = $('#gz-bilgi');
var secRef = null, secAg = null, aktif = 'sema';

/* ---------- kaydırma ve yakınlaştırma (iki tuval için ortak) ---------- */
function panzoom(svg) {
  var vb = svg.getAttribute('viewBox').split(' ').map(parseFloat), tam = vb.slice();
  svg._tam = tam;
  function ayar() { svg.setAttribute('viewBox', vb.map(function (v) { return Math.round(v * 100) / 100; }).join(' ')); }
  svg._vb = function (yeni) { if (yeni) { vb = yeni.slice(); ayar(); } return vb; };
  svg.addEventListener('wheel', function (e) {
    e.preventDefault();
    var r = svg.getBoundingClientRect();
    var mx = (e.clientX - r.left) / r.width, my = (e.clientY - r.top) / r.height;
    var k = e.deltaY < 0 ? 0.8 : 1.25;
    var w = vb[2] * k, h = vb[3] * k;
    if (w > tam[2] * 1.5) { w = tam[2] * 1.5; h = tam[3] * 1.5; }
    // en-boy oranı korunur; görünür alan svg kutusuna göre hesaplanır
    vb[0] += (vb[2] - w) * mx; vb[1] += (vb[3] - h) * my; vb[2] = w; vb[3] = h; ayar();
  }, { passive: false });
  var isaretci = {}, sur = null, hareket = false;
  svg.addEventListener('pointerdown', function (e) {
    isaretci[e.pointerId] = { x: e.clientX, y: e.clientY };
    var n = Object.keys(isaretci).length;
    sur = { x: e.clientX, y: e.clientY, d: n === 2 ? mesafe() : 0 };
    hareket = false;
  });
  function mesafe() {
    var k = Object.keys(isaretci).map(function (i) { return isaretci[i]; });
    return k.length < 2 ? 0 : Math.hypot(k[0].x - k[1].x, k[0].y - k[1].y);
  }
  window.addEventListener('pointermove', function (e) {
    if (!sur || !isaretci[e.pointerId]) return;
    isaretci[e.pointerId] = { x: e.clientX, y: e.clientY };
    var r = svg.getBoundingClientRect();
    var n = Object.keys(isaretci).length;
    if (n === 2) {
      var m = mesafe();
      if (sur.d && m) {
        var k = sur.d / m, w = vb[2] * k, h = vb[3] * k;
        vb[0] += (vb[2] - w) / 2; vb[1] += (vb[3] - h) / 2; vb[2] = w; vb[3] = h; ayar();
      }
      sur.d = m; hareket = true; return;
    }
    var dx = e.clientX - sur.x, dy = e.clientY - sur.y;
    if (!hareket && Math.hypot(dx, dy) < 4) return;
    hareket = true;
    // görünür kutu oranı: meet kuralı yüzünden ölçek, viewBox'ın büyük kenarına göredir
    var olcek = Math.max(vb[2] / r.width, vb[3] / r.height);
    vb[0] -= dx * olcek; vb[1] -= dy * olcek; sur.x = e.clientX; sur.y = e.clientY; ayar();
  });
  window.addEventListener('pointerup', function (e) { delete isaretci[e.pointerId]; if (!Object.keys(isaretci).length) sur = null; });
  svg.addEventListener('dblclick', function (e) { e.preventDefault(); vb = tam.slice(); ayar(); });
  svg._tikHareket = function () { var h = hareket; hareket = false; return h; };
}
[semaSvg, kartSvg].forEach(function (s) { if (s) panzoom(s); });

/* ---------- ekrandaki bir kümeyi görünür alana oturt ---------- */
function goster(svg, els) {
  if (!svg || !els.length || svg.getBoundingClientRect().width === 0) return;
  var ctm = svg.getScreenCTM(); if (!ctm) return;
  var ters = ctm.inverse(), pt = svg.createSVGPoint();
  var x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
  els.forEach(function (el) {
    var r = el.getBoundingClientRect(); if (!r.width && !r.height) return;
    [[r.left, r.top], [r.right, r.bottom]].forEach(function (q) { pt.x = q[0]; pt.y = q[1]; var p = pt.matrixTransform(ters); x0 = Math.min(x0, p.x); y0 = Math.min(y0, p.y); x1 = Math.max(x1, p.x); y1 = Math.max(y1, p.y); });
  });
  if (x0 > x1) return;
  var tam = svg._tam, minw = tam[2] / (svg === kartSvg ? 12 : 4);
  var w = Math.max(x1 - x0, minw * 0.6) * 1.6, h = Math.max(y1 - y0, minw * 0.4) * 1.6;
  var r2 = svg.getBoundingClientRect(), oran = r2.width / r2.height;
  if (w / h < oran) w = h * oran; else h = w / oran;
  svg._vb([(x0 + x1) / 2 - w / 2, (y0 + y1) / 2 - h / 2, w, h]);
}

/* ---------- seçim ---------- */
function temizle() {
  $$('.secili-ref,.secili-ag', kok).forEach(function (x) { x.classList.remove('secili-ref', 'secili-ag'); });
  [semaSvg, kartSvg].forEach(function (s) { if (s) s.classList.remove('agsecili'); });
  $$('.gz-tablo tr.secili', kok).forEach(function (x) { x.classList.remove('secili'); });
}
function parcaSatiri(ref) { return $('#tab-parca tr[data-ref="' + nitel(ref) + '"]', kok); }
function agSatiri(ag) { return $('#tab-ag tr[data-ag="' + nitel(ag) + '"]', kok); }

function agSec(ag, git) {
  temizle(); secAg = ag; secRef = null;
  var els = $$('[data-ag="' + nitel(ag) + '"]', kok);
  els.forEach(function (x) { x.classList.add('secili-ag'); });
  [semaSvg, kartSvg].forEach(function (s) { if (s) s.classList.add('agsecili'); });
  var r = agSatiri(ag); if (r) r.classList.add('secili');
  agBilgi(ag);
  if (git !== false) gitAktif();
}
function refSec(ref, git) {
  temizle(); secRef = ref; secAg = null;
  $$('[data-ref="' + nitel(ref) + '"]', kok).forEach(function (x) { x.classList.add('secili-ref'); });
  var r = parcaSatiri(ref); if (r) r.classList.add('secili');
  refBilgi(ref);
  if (git !== false) gitAktif();
}
function gitAktif() {
  if (aktif === 'sema') {
    var els = secRef ? $$('.parca[data-ref="' + nitel(secRef) + '"]', semaSvg) : $$('[data-ag="' + nitel(secAg) + '"]', semaSvg);
    goster(semaSvg, els);
  } else if (aktif === 'kart') {
    var e2 = secRef ? $$('.pd[data-ref="' + nitel(secRef) + '"],.npth[data-ref="' + nitel(secRef) + '"]', kartSvg) : $$('[data-ag="' + nitel(secAg) + '"]', kartSvg);
    goster(kartSvg, e2);
  }
}
function baglanti(tur, ad, metin) { return '<a href="#" data-sec-' + tur + '="' + esc(ad) + '">' + esc(metin || ad) + '</a>'; }

function refBilgi(ref) {
  var p = VERI.parcalar[ref]; if (!p) return;
  var h = '<h3>' + esc(ref) + ' — ' + esc(p.d) + '</h3>';
  h += '<div class="alt">' + esc(p.s) + (p.m ? ' · ' + esc(p.m) : '') + '</div>';
  h += '<div class="alt">Kılıf <code>' + esc(p.fp) + '</code> · kartta <b>' + p.yuz + ' yüzde</b>, (' + virgul(p.x) + '; ' + virgul(p.y) + ') mm, dönüş ' + virgul(p.a) + '°' + (p.dnp ? ' · <b>takılmaz (DNP)</b>' : '') + '</div>';
  h += '<div class="alt">Bölüm: ' + esc(p.g || '') + '</div>';
  var sat = Object.keys(p.p).sort(function (a, b) { return a.length - b.length || (a < b ? -1 : 1); }).map(function (no) {
    var q = p.p[no];
    return '<tr><td>' + esc(no) + '</td><td>' + esc(q[0] || '') + '</td><td>' + (q[1] ? baglanti('ag', q[1]) : '<span class="kaynak">bağlı değil</span>') + '</td></tr>';
  }).join('');
  h += '<details open><summary>Ayaklar (' + Object.keys(p.p).length + ')</summary><table><tr><th>No</th><th>Ad</th><th>Ağ (tıkla)</th></tr>' + sat + '</table></details>';
  var k = document.getElementById('kart-' + ref);
  if (k) { var c = k.cloneNode(true); c.removeAttribute('id'); h += c.outerHTML; }
  bilgi.innerHTML = h;
}
function agBilgi(ag) {
  var a = VERI.aglar[ag]; if (!a) { bilgi.innerHTML = '<h3>' + esc(ag) + '</h3>'; return; }
  var h = '<h3>Ağ: ' + esc(ag) + '</h3>';
  h += '<div class="alt">' + a.pin.length + ' ayak · kartta iz uzunluğu ' + virgul(a.uz) + ' mm · iz genişliği ' + (a.gen.length ? a.gen.map(virgul).join(', ') + ' mm' : '—') + ' · viya ' + a.viya + ' · katmanlar ' + (a.kat.join(', ') || '—') + '</div>';
  var s = a.pin.map(function (q) {
    var p = VERI.parcalar[q[0]];
    return '<tr><td>' + baglanti('ref', q[0]) + '</td><td>' + esc(q[1]) + '</td><td>' + esc(p ? (p.p[q[1]] || [''])[0] : '') + '</td><td>' + esc(p ? p.d : '') + '</td></tr>';
  }).join('');
  h += '<table><tr><th>Parça</th><th>Ayak</th><th>Ayak adı</th><th>Değer</th></tr>' + s + '</table>';
  bilgi.innerHTML = h;
}

/* ---------- tıklama: şema ve kart ---------- */
function vurguBul(svg, e) {
  var el = e.target.closest('[data-ref],[data-ag]');
  if (el && el.getAttribute('data-ag') === '' && !el.getAttribute('data-ref')) el = null;
  if (el) return el;
  // küçük hedefler için komşu noktaları dene
  var d = [[6, 0], [-6, 0], [0, 6], [0, -6], [10, 10], [-10, -10]];
  for (var i = 0; i < d.length; i++) {
    var l = document.elementsFromPoint(e.clientX + d[i][0], e.clientY + d[i][1]);
    for (var j = 0; j < l.length; j++) {
      var c = l[j].closest && l[j].closest('[data-ref],[data-ag]');
      if (c && svg.contains(c) && !(c.getAttribute('data-ag') === '' && !c.getAttribute('data-ref'))) return c;
    }
  }
  return null;
}
[semaSvg, kartSvg].forEach(function (svg) {
  if (!svg) return;
  svg.addEventListener('click', function (e) {
    if (e.target.closest('a')) return;
    if (svg._tikHareket()) return;
    var el = vurguBul(svg, e); if (!el) return;
    var ref = el.getAttribute('data-ref'), ag = el.getAttribute('data-ag');
    var parca = el.classList.contains('parca') || el.classList.contains('pd') || el.classList.contains('npth') || el.tagName === 'text' && ref;
    if (ref && parca) refSec(ref, false);
    else if (ag) agSec(ag, false);
  });
});

/* ---------- bilgi paneli ve tablolar ---------- */
kok.addEventListener('click', function (e) {
  var a = e.target.closest('[data-sec-ref],[data-sec-ag]');
  if (a) { e.preventDefault(); if (a.hasAttribute('data-sec-ref')) refSec(a.getAttribute('data-sec-ref')); else agSec(a.getAttribute('data-sec-ag')); return; }
  var tr = e.target.closest('.gz-tablo tbody tr');
  if (tr) { if (tr.hasAttribute('data-ref')) refSec(tr.getAttribute('data-ref'), false); else agSec(tr.getAttribute('data-ag'), false); }
});
$$('.gz-filtre', kok).forEach(function (i) {
  i.addEventListener('input', function () {
    var q = i.value.toLowerCase();
    $$('#' + i.getAttribute('data-hedef') + ' tbody tr').forEach(function (tr) { tr.style.display = tr.textContent.toLowerCase().indexOf(q) < 0 ? 'none' : ''; });
  });
});

/* ---------- arama ---------- */
var ara = $('#gz-ara');
ara.addEventListener('keydown', function (e) {
  if (e.key !== 'Enter') return;
  var q = ara.value.trim(); if (!q) return;
  var B = q.toUpperCase();
  if (VERI.parcalar[q] || VERI.parcalar[B]) return refSec(VERI.parcalar[q] ? q : B);
  if (VERI.aglar[q]) return agSec(q);
  var adaylar = Object.keys(VERI.aglar).filter(function (n) { return n.toLowerCase().indexOf(q.toLowerCase()) >= 0; });
  if (adaylar.length) return agSec(adaylar[0]);
  var p = Object.keys(VERI.parcalar).filter(function (n) { return (VERI.parcalar[n].d + ' ' + VERI.parcalar[n].m).toLowerCase().indexOf(q.toLowerCase()) >= 0; });
  if (p.length) return refSec(p[0]);
  bilgi.innerHTML = '<p>“' + esc(q) + '” bulunamadı.</p>';
});

/* ---------- sekmeler ---------- */
function sekme(ad) {
  aktif = ad;
  $$('.gz-sekme', kok).forEach(function (s) { s.classList.toggle('gizli', s.id !== 'sekme-' + ad); });
  $$('.gz-ust button[data-sekme]', kok).forEach(function (b) { b.classList.toggle('aktif', b.getAttribute('data-sekme') === ad); });
  if (secRef || secAg) setTimeout(gitAktif, 30);
}
$$('.gz-ust button[data-sekme]', kok).forEach(function (b) { b.addEventListener('click', function () { sekme(b.getAttribute('data-sekme')); }); });

/* ---------- kart: yüz, katman, ayna ---------- */
function katmanAyar(k, ac) {
  var c = $('input[data-gk="' + k + '"]', kok); if (c) c.checked = ac;
  $$('.k-' + k, kartSvg).forEach(function (x) { x.classList.toggle('gizli', !ac); });
}
function yuz(y) {
  var arka = y === 'arka', ic = $('#kart-ic', kartSvg), cx2 = kartSvg.getAttribute('data-ayna');
  kartSvg.classList.toggle('v-arka', arka); kartSvg.classList.toggle('v-on', !arka); kartSvg.classList.toggle('ayna', arka);
  ic.setAttribute('transform', arka ? 'translate(' + cx2 + ',0) scale(-1,1)' : '');
  var F = $('#g-FCu', kartSvg), B = $('#g-BCu', kartSvg);
  if (arka) ic.insertBefore(F, B); else ic.insertBefore(B, F);
  katmanAyar('FCu', !arka); katmanAyar('BCu', arka);
  $$('.panokontrol button[data-yuz]', kok).forEach(function (b) { b.classList.toggle('aktif', b.getAttribute('data-yuz') === y); });
}
$$('.panokontrol button[data-yuz]', kok).forEach(function (b) { b.addEventListener('click', function () { yuz(b.getAttribute('data-yuz')); }); });
$$('.panokontrol input[data-gk]', kok).forEach(function (c) {
  c.addEventListener('change', function () {
    var k = c.getAttribute('data-gk');
    $$('.k-' + k, kartSvg).forEach(function (x) { x.classList.toggle('gizli', !c.checked); });
    if (k === 'ipekF') $$('.k-ipekB', kartSvg).forEach(function (x) { x.classList.toggle('gizli', !c.checked); });
  });
});
var sf = $('button[data-sifirla]', kok);
if (sf) sf.addEventListener('click', function () { kartSvg._vb(kartSvg._tam); });

// adres çubuğundan açılış: tam.html#U1 ya da tam.html#ag=SPI_SCK
if (location.hash.length > 1) {
  var hs = decodeURIComponent(location.hash.slice(1));
  if (hs.indexOf('ag=') === 0) agSec(hs.slice(3), true); else if (VERI.parcalar[hs]) refSec(hs, true);
}
})();
