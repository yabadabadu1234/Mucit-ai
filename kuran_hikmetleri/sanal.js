(function () {
  'use strict';
  /* Sanal liste: her sûrenin âyet bloğu yalnız görünür yakınlıktayken DOM'da bulunur. */
  var BLOKLAR = [];
  var OZEL = '<\\/script';

  function hazirla() {
    var liste = document.querySelectorAll('.ag-sanal');
    for (var i = 0; i < liste.length; i++) {
      var el = liste[i];
      var sc = el.querySelector('script[type="text/x-sanal"]');
      if (!sc) continue;
      el._html = sc.textContent.split(OZEL).join('</script');
      el._durum = 0;
      el.removeChild(sc);
      el.style.minHeight = (parseInt(el.getAttribute('data-tahmin'), 10) || 600) + 'px';
      BLOKLAR.push(el);
    }
  }

  function ciz(el) {
    if (el._durum === 1) return;
    el.innerHTML = el._html;
    el._durum = 1;
    var h = el.offsetHeight;
    if (h > 0) el.style.minHeight = h + 'px';
    document.dispatchEvent(new CustomEvent('sanal-render', { detail: el }));
  }

  function bosalt(el) {
    if (el._durum !== 1) return;
    var h = el.offsetHeight;
    if (h > 0) el.style.minHeight = h + 'px';
    el.innerHTML = '';
    el._durum = 0;
  }

  function gozle() {
    if (!('IntersectionObserver' in window)) { BLOKLAR.forEach(ciz); return; }
    var io = new IntersectionObserver(function (kayitlar) {
      kayitlar.forEach(function (k) {
        if (k.isIntersecting) ciz(k.target); else bosalt(k.target);
      });
    }, { rootMargin: '2500px 0px 2500px 0px' });
    BLOKLAR.forEach(function (el) { io.observe(el); });
  }

  function hepsiniCiz() { BLOKLAR.forEach(ciz); }

  function hedefeGit() {
    var h = decodeURIComponent((location.hash || '').slice(1));
    if (!h) return;
    var hedef = document.getElementById(h);
    if (!hedef) {
      for (var i = 0; i < BLOKLAR.length; i++) {
        if (BLOKLAR[i]._html.indexOf('id="' + h + '"') !== -1) { ciz(BLOKLAR[i]); break; }
      }
      hedef = document.getElementById(h);
    }
    if (hedef) hedef.scrollIntoView();
  }

  window.sanalHepsiniCiz = hepsiniCiz;
  window.addEventListener('beforeprint', hepsiniCiz);
  window.addEventListener('hashchange', hedefeGit);

  document.addEventListener('DOMContentLoaded', function () {
    hazirla();
    gozle();
    hedefeGit();
    if (location.hash) {
      setTimeout(hedefeGit, 400);
      setTimeout(hedefeGit, 1200);
    }
  });
})();
