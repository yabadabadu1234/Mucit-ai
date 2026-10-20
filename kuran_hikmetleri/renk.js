/* Renkli anlam: Arapça kelime ile onun meal karşılığı aynı renkte görünür.
 * Veri: renk_sozluk.json (Arapça yüzey → Türkçe karşılık), ilk tıklamada yüklenir.
 * Kitap HTML'i şişmez; düğmeye basılınca her ayet işlenir (idempotent). */
(function () {
  var PALET = ['#fde68a', '#a7f3d0', '#bfdbfe', '#fbcfe8', '#fecaca', '#ddd6fe',
               '#bae6fd', '#fed7aa', '#d9f99d', '#fca5a5', '#c7d2fe', '#99f6e4'];
  var SOZLUK = null;

  function norm(s) {
    return s.replace(/[ً-ٰٟـۖ-ۭ]/g, '')
      .replace(/[إأآٱ]/g, 'ا').replace(/ى/g, 'ي').trim();
  }
  function kaçış(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
  function adaylar(karsilik) {
    return karsilik.toLocaleLowerCase('tr').split(/[\s,;()\/.:]+/)
      .filter(function (w) { return w.length >= 3 && w !== 'ile' && w !== 'olan' && w !== 'için'; });
  }
  function eslesir(meal, adaylar) {
    var m = meal.toLocaleLowerCase('tr');
    for (var i = 0; i < adaylar.length; i++) {
      var a = adaylar[i];
      if (m === a || (a.length >= 4 && m.indexOf(a) === 0)) return true;
    }
    return false;
  }

  function ayetiIsle(arEl, trEl) {
    if (arEl.dataset.renk) return;
    var arMetin = arEl.textContent.trim();
    var kelimeler = arMetin.split(/\s+/).filter(Boolean);
    var renkler = kelimeler.map(function (k) { return SOZLUK[norm(k)] || null; });
    var arHtml = [], sira = 0, pair = [];
    kelimeler.forEach(function (k, i) {
      if (renkler[i]) {
        var c = sira++ % PALET.length;
        pair[i] = c;
        arHtml.push('<span class="rk" data-c="' + c + '">' + kaçış(k) + '</span>');
      } else {
        arHtml.push(kaçış(k));
      }
    });
    arEl.innerHTML = arHtml.join(' ');

    // Meal: her Arapça kelimenin karşılığı, sırayla, kullanılmamış ilk eşleşme.
    var trMetin = trEl.textContent;
    var parcalar = trMetin.split(/([\p{L}’'’\-]+)/u);
    var kullanildi = {};
    var trHtml = [];
    var atama = {};
    kelimeler.forEach(function (k, i) {
      if (renkler[i] == null) return;
      var c = pair[i];
      var ad = adaylar(renkler[i]);
      for (var j = 0; j < parcalar.length; j++) {
        if (j % 2 === 0 || kullanildi[j]) continue;
        if (eslesir(parcalar[j], ad)) { kullanildi[j] = true; atama[j] = c; break; }
      }
    });
    parcalar.forEach(function (p, j) {
      if (j % 2 === 1 && atama[j] !== undefined) {
        trHtml.push('<span class="rk" data-c="' + atama[j] + '">' + kaçış(p) + '</span>');
      } else {
        trHtml.push(kaçış(p));
      }
    });
    trEl.innerHTML = trHtml.join('');
    arEl.dataset.renk = '1';
    trEl.dataset.renk = '1';
  }

  function stil() {
    var s = document.createElement('style');
    s.textContent = PALET.map(function (c, i) {
      return 'body.renk-acik .rk[data-c="' + i + '"]{background:' + c + ';border-radius:3px;}';
    }).join('\n') + '\nbody.renk-acik .rk{padding:0 1px;}';
    document.head.appendChild(s);
  }

  function baslat(dugme) {
    dugme.disabled = true; dugme.textContent = 'Renkler yükleniyor…';
    fetch('renk_sozluk.json').then(function (r) { return r.json(); }).then(function (veri) {
      SOZLUK = {};
      Object.keys(veri).forEach(function (k) { SOZLUK[k] = veri[k]; });
      stil();
      var arlar = document.querySelectorAll('.verse-ar');
      arlar.forEach(function (arEl) {
        var kart = arEl.closest('.ag-kart, .ayet, .ayet-d, .verse') || arEl.parentElement;
        var trEl = kart ? kart.querySelector('.verse-tr') : null;
        if (trEl) ayetiIsle(arEl, trEl);
      });
      document.body.classList.add('renk-acik');
      dugme.disabled = false; dugme.textContent = 'Renkli anlam: açık / kapalı';
    }).catch(function () {
      dugme.disabled = false; dugme.textContent = 'Renk verisi yüklenemedi';
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var dugme = document.createElement('button');
    dugme.textContent = 'Renkli anlam';
    dugme.style.cssText = 'position:fixed;top:60px;right:12px;z-index:9999;padding:6px 10px;' +
      'border:1px solid #334155;border-radius:6px;background:#fff;color:#0f172a;font-size:12px;cursor:pointer;';
    dugme.addEventListener('click', function () {
      if (SOZLUK) { document.body.classList.toggle('renk-acik'); return; }
      baslat(dugme);
    });
    document.body.appendChild(dugme);
  });
})();
