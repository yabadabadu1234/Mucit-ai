/* Müştak listesi düzeni ve çizimi (kavram uzayı ve zihin haritası ortak).
   Usul: yer sabittir (asıl, mecaz, ıstılah, deyim hep aynı sırada); biçim manayı taşır; bir kapta en çok 4 mana;
   misal kendi manasının altında; sınama kipi manaları gizler, dokununca açar; süs yoktur. */
const MC_ = {}, MDurum = {acik: new Set(), gor: new Set(), sina: false, surum: 0};
const ZON = {
  A: {yaz: '#3b2f1e', acik: '#eadcbc', ad: 'Asıl mana', isaret: '■', zemin: 'rgba(184,134,11,.10)', kenar: '#a8842a'},
  M: {yaz: '#1f3550', acik: '#c8dcf3', ad: 'Mecaz ve genişleme', isaret: '◐', zemin: 'rgba(47,111,179,.09)', kenar: '#4f7fb3'},
  I: {yaz: '#24402a', acik: '#cde6c6', ad: 'Istılah', isaret: '◆', zemin: 'rgba(63,127,58,.10)', kenar: '#4f8a46'},
  D: {yaz: '#3d2648', acik: '#e4cdee', ad: 'Deyimler', isaret: '❝', zemin: 'rgba(138,63,160,.08)', kenar: '#8a5aa0'}};
const ISTILAH = /^(huk|hukuk|tasavvuf|fık|fel|felsefe|mant|edeb|gram|dilb|spor|tıp|kim|fiz|mat|astr|ask|müz|biy|coğ|din|kelâm|hadis|tefsir|ekon|tic|zool|bot|mim|hes|mûsikî|denizcilik|denizc|bilişim|anat|jeol|tiyatro|sin|psik|sosy)/i;
function zonu(etiket, eser) {
  const e = (etiket || '').toLowerCase();
  if (/^mec|^teşmil|^kısa|^halk ağzı|^argo|^alay|^mecaz/.test(e)) return 'M';
  if (ISTILAH.test(e)) return 'I';
  return 'A';
}
function sar_(t, n) { const w = String(t).split(' '), o = []; let b = ''; for (const x of w) { if ((b + ' ' + x).trim().length > n && b) { o.push(b); b = x } else b = (b + ' ' + x).trim() } if (b) o.push(b); return o }
function kelimeBlok(x, ix, kok) {
  const [ar, tr, sn, G] = x, key = kok + '|' + ar, S = 19, O = [], W = 430;
  let y = 0;
  O.push(['w', 0, y, ar, tr, sn, key]); y += 26;
  if (!G) return {O, h: y, key};
  const Z = {A: [], M: [], I: [], D: []}, gor = new Set();
  G.forEach(e => {
    e[3].forEach(n => { const z = e[0] === 'Kamus' || e[0] === 'Vankulu' ? (n[1] ? zonu(n[1]) : 'A') : zonu(n[1]); const t = n[2]; if (!t || gor.has(t)) return; gor.add(t); Z[z].push({t, et: (n[1] || '').replace(/\.$/, ''), mis: n[3], ky: e[0]}) });
    e[4].forEach(d => { if (gor.has(d[0])) return; gor.add(d[0]); Z.D.push({t: d[0] + ': ' + d[1], et: '', mis: d[2], ky: e[0]}) });
  });
  const acik = MDurum.acik.has(key);
  for (const z of ['A', 'M', 'I', 'D']) {
    const L = Z[z]; if (!L.length) continue;
    const y0 = y; y += 8; O.push(['zl', 34, y + 11, ZON[z].ad + ' (' + L.length + ')', z]); y += 22;
    const goster = acik ? L : L.slice(0, 4);
    goster.forEach((s, i) => {
      const satirlar = sar_((i + 1) + '. ' + (s.et ? '[' + s.et + '] ' : '') + s.t, 62);
      satirlar.forEach((l, j) => { O.push(['zt', 32, y + 10, l, j === satirlar.length - 1 ? s.ky : '', key, z]); y += S });
      (acik ? s.mis : s.mis.slice(0, 2)).forEach(m => {
        const ml = sar_('“' + m[0] + '”' + (m[1] ? ' — ' + m[1] : ''), 58), b0 = y + 2;
        ml.forEach(l => { O.push(['mt', 52, y + 15, l, key]); y += 17 });
        O.push(['bal', 44, b0, W - 70, y - b0 + 8]); y += 12;
      });
    });
    if (!acik && (L.length > 4 || L.some(s => s.mis.length > 2))) { O.push(['fold', 32, y + 10, '… ' + (L.length > 4 ? (L.length - 4) + ' mana daha' : 'misallerin hepsi') + ' (dokun)', key]); y += S }
    if (acik && (L.length > 4 || L.some(s => s.mis.length > 2))) { O.push(['fold', 32, y + 10, '▲ topla (dokun)', key]); y += S }
    O.push(['box', 14, y0, W - 24, y - y0 + 10, z]); y += 22;
  }
  return {O, h: y + 4, key};
}
const BABAD = {II: "tef'îl", III: "mufâ'ale", IV: "if'âl", V: "tefe''ul", VI: "tefâ'ul", VII: "infi'âl", VIII: "ifti'âl", IX: "if'ilâl", X: "istif'âl", XI: "if'îlâl", XII: "if'î'âl", XIII: "if'ivvâl"};
function babAdi(b) { return String(b).replace(/bâb (XIII|XII|XI|IX|X|VIII|VII|VI|IV|V|III|II)\b/, (m, r) => BABAD[r] + ' bâbı') }
function mustakDuzen(k) {
  const v = MDurum.surum; if (MC_[k] && MC_[k].v === v) return MC_[k];
  const D2 = SA[k]; if (!D2) return null;
  const blok = [], halka = [], kirmizi = [];
  D2.forEach(([b, K]) => {
    const bad = babAdi(b), lb = [], hb = [], kb = [];
    K.forEach(([t, L]) => { L.forEach((x, i) => { if (x[2] === 0) { kb.push([t, x]); return } hb.push(x); if (x[3]) { const B = kelimeBlok(x, i, k); B.tip = 'k'; B.t = t; lb.push(B) } }) });
    if (hb.length) halka.push([bad, hb]); if (kb.length) kirmizi.push([bad, kb]);
    if (lb.length) { blok.push({tip: 'b', t: bad, h: 40}); let ot = null; lb.forEach(B => { if (B.t !== ot) { blok.push({tip: 't', t: B.t, h: 30}); ot = B.t } blok.push(B) }) }
  });
  const WC = 520, top = blok.reduce((a, b) => a + b.h, 0);
  let en = null;
  for (let C = 1; C <= 8; C++) {
    const hed = top / C, O = [], HIT = []; let col = 0, y = 30, mx = 0;
    blok.forEach(b => {
      if (y - 30 + b.h > hed * 1.03 && col < C - 1 && y > 30 && b.tip !== 'b' && b.tip !== 't') { mx = Math.max(mx, y); col++; y = 30 }
      const x = col * WC;
      if (b.tip === 'b') { O.push(['b', x, y + 22, b.t]); y += b.h; return }
      if (b.tip === 't') { O.push(['t', x, y + 18, b.t]); y += b.h; return }
      b.O.forEach(o => { const p = o.slice(); p[1] += x; p[2] += y; O.push(p) });
      HIT.push([x, y, WC - 40, 26, 'gor', b.key]);
      b.O.forEach(o => { if (o[0] === 'fold') HIT.push([x + o[1], y + o[2] - 14, 300, 18, 'acik', o[4]]) });
      y += b.h;
    });
    mx = Math.max(mx, y); const Wd = (col + 1) * WC - 60, sk = 1 / Math.max(Wd, mx);
    if (!en || sk > en.sk) en = {O, HIT, W: Wd, H: mx, sk};
  }
  const sira = {box: 0, bal: 1}; en.O.sort((a, b) => (sira[a[0]] ?? 2) - (sira[b[0]] ?? 2));
  en.halka = halka; en.kirmizi = kirmizi; en.v = v; en.bos = !blok.length;
  return MC_[k] = en;
}
const HOLC = {};
function halkaOlc(ctx, M) {
  if (M.olc) return M.olc;
  const L = []; ctx.save();
  M.halka.forEach(([b, X]) => { ctx.font = 'bold 10px Georgia'; L.push({b: 1, t: b + ' ·', w: ctx.measureText(b + ' ·').width + 8});
    X.forEach(x => { ctx.font = '12px Amiri'; const wa = ctx.measureText(x[0]).width; ctx.font = '10px Georgia'; const wt = ctx.measureText('(' + x[1] + ')').width; L.push({ar: x[0], tr: '(' + x[1] + ')', sn: x[2], wa, wt, w: wa + wt + 14}) }) });
  ctx.restore(); return M.olc = L;
}
function halkaYerlestir(L, maxR, ic) {
  const ws = L.filter(x => !x.b).map(x => x.w).sort((a, b) => a - b), w0 = Math.max(60, ws[Math.floor(ws.length * .85)] || 60) + 10, h0 = 22;
  const dizi = []; L.forEach(it => { if (it.b) dizi.push({bas: 1, it}); else dizi.push({it}) });
  for (let f = 0.006; f > 0.00015; f *= 0.95) {
    const dr = h0 * f;
    for (let R = 1; R <= maxR; R++) {
      const rs = 0.985 - (R - 0.5) * dr; if (rs - dr / 2 < ic) break;
      const K = Math.floor(2 * Math.PI * rs / (w0 * f)); if (K < 4) break;
      let j = 0; const P = [];
      for (const d of dizi) { if (d.bas && j % R) j += R - j % R; P.push([d.it, Math.floor(j / R), j % R]); j++ }
      if (j <= K * R) return {f, K, R, dr, w0, h0, P: P.map(([it, c, r]) => [it, 0.985 - (r + 0.5) * dr, (c + 0.5) * 2 * Math.PI / K]), ri: 0.985 - R * dr};
    }
  }
  return null;
}
function halkaCiz(ctx, M, cx, cy, rc, es) {
  const L = halkaOlc(ctx, M), H = M.yer || (M.yer = halkaYerlestir(L, M.bos ? 40 : 10, M.bos ? 0.12 : 0.5));
  if (!H) return 0.6 * rc;
  const f = H.f * rc, uzak = f * 12 * es < 2.5;
  ctx.save();
  for (const [it, r, a0] of H.P) {
    const a = a0 - Math.PI / 2, x = cx + Math.cos(a) * r * rc, y = cy + Math.sin(a) * r * rc, alt = Math.sin(a) > 0.02, bw = H.w0 - 8, bh = H.h0 - 5;
    ctx.save(); ctx.translate(x, y); ctx.rotate(alt ? a - Math.PI / 2 : a + Math.PI / 2); ctx.scale(f, f);
    ctx.beginPath(); ctx.roundRect(-bw / 2, -bh / 2, bw, bh, bh / 2);
    ctx.fillStyle = it.b ? '#e6eef8' : it.sn === 1 ? '#f4f1e8' : '#f6ecd2'; ctx.fill(); ctx.lineWidth = 1; ctx.strokeStyle = it.b ? '#2f6fb3' : it.sn === 1 ? '#bdb59e' : '#a8842a'; ctx.stroke();
    if (!uzak) { ctx.textBaseline = 'middle';
      if (it.b) { ctx.fillStyle = '#2f6fb3'; ctx.font = 'bold 10px Georgia'; ctx.textAlign = 'center'; const k = Math.min(1, (bw - 8) / (it.w - 8)); ctx.scale(k, k); ctx.fillText(it.t.replace(/ ·$/, ''), 0, 0) }
      else { const k = Math.min(1, (bw - 8) / (it.w - 10)); ctx.scale(k, k); const x0 = -(it.wa + it.wt + 3) / 2; ctx.fillStyle = it.sn === 1 ? '#7a7058' : '#3b2f1e'; ctx.font = '12px Amiri'; ctx.textAlign = 'left'; ctx.fillText(it.ar, x0, 0); ctx.font = '10px Georgia'; ctx.fillText(it.tr, x0 + it.wa + 3, 0) } }
    ctx.restore();
  }
  ctx.restore(); return H.ri * rc;
}

function mustakTikla(M, lx, ly) {
  for (const h of M.HIT) if (lx >= h[0] && lx <= h[0] + h[2] && ly >= h[1] && ly <= h[1] + h[3]) {
    const S = h[4] === 'acik' ? MDurum.acik : MDurum.gor;
    if (h[4] === 'gor' && !MDurum.sina) return false;
    S.has(h[5]) ? S.delete(h[5]) : S.add(h[5]); MDurum.surum++; return true }
  return false;
}
function sekil_(c, z, x, y, w, h) {
  c.beginPath();
  if (z === 'A') c.rect(x, y, w, h);
  else if (z === 'M') c.roundRect(x, y, w, h, Math.min(16, h / 2));
  else if (z === 'I') { c.moveTo(x, y + 6); c.lineTo(x + 70, y + 6); c.lineTo(x + 78, y); c.lineTo(x + 150, y); c.lineTo(x + 158, y + 6); c.lineTo(x + w, y + 6); c.lineTo(x + w, y + h); c.lineTo(x, y + h); c.closePath() }
  else c.roundRect(x, y, w, h, 8);
}
function balon_(c, x, y, w, h) { c.beginPath(); c.roundRect(x, y, w, h, 7); c.moveTo(x + 14, y); c.lineTo(x + 8, y - 6); c.lineTo(x + 22, y) }
function mustakCiz(ctx, M, lx0, ly0, lx1, ly1, es, R) {
  const yazi = 12.5 * es > 3.5, gizli = k => MDurum.sina && !MDurum.gor.has(k);
  for (const o of M.O) {
    const t = o[0], x = o[1], y = o[2];
    if (t === 'box') { const [, bx, by, bw, bh, z] = o; if (bx + bw < lx0 || bx > lx1 || by + bh < ly0 || by > ly1) continue; sekil_(ctx, z, bx, by, bw, bh); ctx.fillStyle = ZON[z].zemin; ctx.fill(); if (yazi) { cerceve_(ctx, z, bx, by, bw, bh) } else { ctx.strokeStyle = ZON[z].kenar; ctx.lineWidth = 1; ctx.stroke() } continue }
    if (t === 'bal') { if (x + o[3] < lx0 || x > lx1 || y + o[4] < ly0 || y > ly1) continue; balon_(ctx, x, y, o[3], o[4]); ctx.fillStyle = 'rgba(255,250,235,.85)'; ctx.fill(); ctx.strokeStyle = '#c9b27a'; ctx.lineWidth = .8; ctx.stroke(); continue }
    if (x + 460 < lx0 || x > lx1 || y + 20 < ly0 || y - 20 > ly1) continue;
    if (t === 'b') { ctx.fillStyle = '#2f6fb3'; ctx.fillRect(x, y + 7, 430, 1.5); if (yazi) { ctx.font = 'bold 19px Georgia'; ctx.textAlign = 'left'; ctx.fillText(o[3], x, y) } }
    else if (t === 't') { ctx.fillStyle = '#b3541e'; if (yazi) { ctx.font = 'bold 15px Georgia'; ctx.textAlign = 'left'; ctx.fillText(o[3], x + 4, y) } else ctx.fillRect(x + 4, y - 6, 150, 5) }
    else if (t === 'w') { const c = ['#c0392b', '#9a917a', R.yaz][o[5]]; if (yazi) semse_(ctx, x - 4, y - 3, 122, 24, c); ctx.fillStyle = c;
      if (yazi) { ctx.font = '18px Amiri'; ctx.textAlign = 'right'; ctx.fillText(o[3], x + 110, y + 14); ctx.font = '12.5px Georgia'; ctx.textAlign = 'left'; ctx.fillText(gizli(o[6]) && o[5] === 2 ? '( ? dokun, hatırla )' : '(' + o[4] + ')', x + 118, y + 13) }
      else { ctx.globalAlpha = .55; ctx.fillRect(x + 60, y + 5, 50, 7); ctx.fillRect(x + 118, y + 5, 7 * String(o[4]).length, 6); ctx.globalAlpha = 1 } }
    else if (t === 'zl') { motif_(ctx, o[4], x - 11, y - 4, 7); ctx.fillStyle = ZON[o[4]].kenar; if (yazi) { ctx.font = 'bold 11px Georgia'; ctx.textAlign = 'left'; ctx.fillText(o[3], x, y) } }
    else if (t === 'zt' || t === 'mt') { const gz = gizli(o[t === 'zt' ? 5 : 4]); ctx.fillStyle = t === 'mt' ? '#54431f' : ZON[o[6]].yaz;
      if (yazi && !gz) { ctx.font = (t === 'mt' ? 'italic 10.5px' : '11.5px') + ' Georgia'; ctx.textAlign = 'left'; ctx.fillText(o[3], x, y); if (t === 'zt' && o[4]) { const w = ctx.measureText(o[3]).width; ctx.fillStyle = R.inc; ctx.font = '9px Georgia'; ctx.fillText('  ' + o[4], x + w, y) } }
      else { ctx.globalAlpha = gz ? .18 : .3; ctx.fillRect(x, y - 7, Math.min(370, o[3].length * 5.6), 7); ctx.globalAlpha = 1 } }
    else if (t === 'fold') { if (yazi) { ctx.fillStyle = '#2f6fb3'; ctx.font = '10.5px Georgia'; ctx.textAlign = 'left'; ctx.fillText(o[3], x, y) } }
  }
}
/* Motifler: açık kaynaktan resim almak yerine riyazî olarak çizilir (yıldız çokgenleri, rozet, şemse kartuşu).
   Her motif bir mana cinsine bağlıdır: asıl = sekiz köşe yıldız, mecaz = altı köşe yıldız, ıstılah = dört kollu kilit, deyim = beş yapraklı rozet. */
function yildiz_(c, x, y, r, n, ic) { c.beginPath(); for (let i = 0; i < 2 * n; i++) { const a = Math.PI * i / n - Math.PI / 2, rr = i % 2 ? r * ic : r; c.lineTo(x + rr * Math.cos(a), y + rr * Math.sin(a)) } c.closePath() }
function rozet_(c, x, y, r, n) { c.beginPath(); for (let i = 0; i < n; i++) { const a = 2 * Math.PI * i / n - Math.PI / 2; c.moveTo(x, y); c.ellipse(x + r * .5 * Math.cos(a), y + r * .5 * Math.sin(a), r * .5, r * .26, a, 0, 2 * Math.PI) } }
function motif_(c, z, x, y, r) {
  const k = ZON[z].kenar; c.save(); c.lineWidth = Math.max(.6, r / 9); c.strokeStyle = k; c.fillStyle = ZON[z].zemin.replace(/[\d.]+\)$/, '.55)');
  if (z === 'A') { yildiz_(c, x, y, r, 8, .62); c.fill(); c.stroke(); yildiz_(c, x, y, r * .5, 8, .62); c.stroke() }
  else if (z === 'M') { yildiz_(c, x, y, r, 6, .58); c.fill(); c.stroke(); c.beginPath(); c.arc(x, y, r * .3, 0, 7); c.stroke() }
  else if (z === 'I') { c.beginPath(); for (let i = 0; i < 4; i++) { const a = Math.PI / 2 * i; c.rect(x + Math.cos(a) * r * .55 - r * .22, y + Math.sin(a) * r * .55 - r * .22, r * .44, r * .44) } c.rect(x - r * .3, y - r * .3, r * .6, r * .6); c.fill(); c.stroke() }
  else { rozet_(c, x, y, r, 5); c.fill(); c.stroke() }
  c.restore();
}
function semse_(c, x, y, w, h, renk) {
  const cx = x + w / 2, cy = y + h / 2; c.save(); c.beginPath();
  c.moveTo(x, cy); c.quadraticCurveTo(x + 10, y, x + 26, y); c.lineTo(x + w - 26, y); c.quadraticCurveTo(x + w - 10, y, x + w, cy);
  c.quadraticCurveTo(x + w - 10, y + h, x + w - 26, y + h); c.lineTo(x + 26, y + h); c.quadraticCurveTo(x + 10, y + h, x, cy); c.closePath();
  c.fillStyle = 'rgba(184,134,11,.08)'; c.fill(); c.strokeStyle = renk; c.lineWidth = 1; c.stroke();
  yildiz_(c, x + 9, cy, 4, 8, .55); c.fillStyle = renk; c.fill(); yildiz_(c, x + w - 9, cy, 4, 8, .55); c.fill(); c.restore();
}

/* Çerçeve: kenar, kutunun mana cinsine ait motifin tekrarıyla örülür; motifler arası ince bağ çizgisi. */
function cerceve_(c, z, x, y, w, h) {
  const r = 4.2, ad = 15, nx = Math.max(2, Math.round(w / ad)), ny = Math.max(2, Math.round(h / ad));
  c.save(); c.globalAlpha = .75; c.strokeStyle = ZON[z].kenar; c.lineWidth = .5; c.beginPath(); c.rect(x, y, w, h); c.stroke();
  for (let i = 0; i <= nx; i++) { const px = x + w * i / nx; motif_(c, z, px, y, r); motif_(c, z, px, y + h, r) }
  for (let j = 1; j < ny; j++) { const py = y + h * j / ny; motif_(c, z, x, py, r); motif_(c, z, x + w, py, r) }
  c.restore();
}

function KARA_(c){c=String(c).trim();const m=String(c).match(/\d+/g);let r,g,b;if(String(c)[0]==='#'){const h=c.slice(1);[r,g,b]=[0,2,4].map(i=>parseInt(h.length===3?h[i/2]+h[i/2]:h.slice(i,i+2),16))}else[r,g,b]=m.map(Number);return .299*r+.587*g+.114*b<128}
