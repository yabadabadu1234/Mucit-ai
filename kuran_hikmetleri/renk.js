/* Renkli anlam: Arapça kelime ile onun meal karşılığı aynı renkte görünür.
 * Eşleşme üç aşamalıdır: (1) sözlük karşılığının Türkçe sözcükleri, (2) Arapça ekleri
 * (و ف ب ل ك ... ve -hum, -hüm, -kum ...) ayıklanmış biçimin sözlüğü, (3) ünsüz iskeleti
 * (bihim = بهم, leküm = لكم, ente = أنت). Veri: renk_sozluk.json, ilk tıklamada yüklenir.
 * Kitap HTML'i şişmez; düğmeye basılınca her ayet işlenir (idempotent). */
(function () {
  var PALET = ['#fde68a', '#a7f3d0', '#bfdbfe', '#fbcfe8', '#fecaca', '#ddd6fe',
               '#bae6fd', '#fed7aa', '#d9f99d', '#fca5a5', '#c7d2fe', '#99f6e4'];
  var SOZLUK = null;

  var ARAP_ISKELET = {
    'ب': 'b', 'ت': 't', 'ط': 't', 'ث': 's', 'س': 's', 'ص': 's', 'ج': 'c', 'ح': 'h',
    'ه': 'h', 'ة': 'h', 'خ': 'h', 'غ': 'g', 'ق': 'k', 'ك': 'k', 'ف': 'f', 'د': 'd',
    'ذ': 'd', 'ض': 'd', 'ظ': 'd', 'ر': 'r', 'ز': 'z', 'ش': 'S', 'ل': 'l', 'م': 'm',
    'ن': 'n'
  };
  var TUR_ISKELET = {
    'b': 'b', 'p': 'b', 'c': 'c', 'ç': 'c', 'j': 'c', 'd': 'd', 'f': 'f', 'g': 'g',
    'h': 'h', 'k': 'k', 'q': 'k', 'l': 'l', 'm': 'm', 'n': 'n', 'r': 'r', 's': 's',
    'ş': 'S', 't': 't', 'v': 'f', 'z': 'z'
  };
  // Sözlükte olmayan zamirler ve edatlar (normalize biçim → meal karşılığı). Eşleşme yalnız meal'de bu sözcüklerle yapılır.
  var ZAMIR = {
    'هو': 'o, onu, ona, onda', 'هي': 'o, onu, ona, onda', 'هم': 'onlar, onları, onlara',
    'هما': 'onlar, ikisi, onları', 'هن': 'onlar, onları, onlara',
    'انت': 'sen, seni, sana, sende', 'انتم': 'siz, sizi, size, sizde', 'نحن': 'biz, bizi, bize, bizde',
    'انا': 'ben, beni, bana, bende',
    'له': 'onun, ona, onu', 'لها': 'onun, ona, onu', 'لهم': 'onların, onlara, onlar', 'لهما': 'onların, onlara',
    'لك': 'senin, sana, seni', 'لكم': 'sizin, size, sizi', 'لنا': 'bizim, bize, bizi', 'لي': 'benim, bana, beni',
    'به': 'onunla, ona, onda, bununla', 'بها': 'onunla, onda, bununla', 'بهم': 'onlarla, onlarda, onlara',
    'بهما': 'onlarla', 'بك': 'seninle, sende', 'بنا': 'bizimle, bizde',
    'منه': 'ondan, onun', 'منها': 'ondan, onun', 'منهم': 'onlardan', 'منكم': 'sizden, sizin',
    'عنه': 'ondan, onun', 'عنها': 'ondan, onun', 'عنهم': 'onlardan', 'فيه': 'onda, içinde, onun',
    'فيها': 'onda, içinde', 'فيهم': 'onlarda, içinde', 'اليه': 'ona, ona doğru', 'اليها': 'ona, ona doğru',
    'اليهم': 'onlara, onlara doğru', 'اليكم': 'size, size doğru', 'معه': 'onunla, ile', 'معهم': 'onlarla, ile',
    'عليه': 'onun üzerine, ona, onun üstüne', 'عليها': 'onun üzerine', 'عليهم': 'onların üzerine, onlara'
  };
  // Bitişik zamir ekleri: Arapça kelimenin sonu (norm biçimi) → meal'deki karşılık sözcükleri.
  var ZAMIR_EKI = [
    { ek: 'هم', meal: ['onlar', 'onları', 'onlara', 'onların', 'onlardan', 'onlarla', 'onlarda'] },
    { ek: 'كم', meal: ['siz', 'sizi', 'size', 'sizin', 'sizden', 'sizinle'] },
    { ek: 'نا', meal: ['biz', 'bizi', 'bize', 'bizim', 'bizden', 'bizimle'] },
    { ek: 'ني', meal: ['ben', 'beni', 'bana', 'benim', 'bende'] }
  ];
  var ZAMIR_DURAK =/^[ۖ-ۭ]+$/; // yalnız durak işareti (ۚ ۖ ۗ ۞ ۙ): kelime değildir
  var ONEKLER = ['والـ', 'وال', 'فال', 'بال', 'لل', 'ال', 'و', 'ف', 'ب', 'ل', 'ك', 'س'];
  var SONEKLER = ['هما', 'هم', 'هن', 'ها', 'كم', 'كن', 'نا', 'ني', 'ه', 'ي', 'ة', 'ك'];

  // Hemzeler (ء ؤ ئ) ve harekeler atılır: "لَـَٔايَـٰتٍ" ile "ايات" aynı anahtara düşer.
  function norm(s) {
    return s.replace(/[ً-ٰٟـۖ-ۭ]/g, '')
      .replace(/[ءؤئ]/g, '')
      .replace(/[إأآٱ]/g, 'ا').replace(/ى/g, 'ي').trim();
  }
  function kaçış(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
  // Fiil mastarı (-mak / -mek) kökü: "anlamak" → "anla", meal'deki çekimli "anlamazsınız" ile eşleşsin.
  function adaylar(karsilik) {
    var out = [];
    karsilik.toLocaleLowerCase('tr').split(/[\s,;()\/.:]+/).forEach(function (w) {
      if (w.length >= 3 && w !== 'ile' && w !== 'olan' && w !== 'için') out.push(w);
      if (/(mak|mek)$/.test(w) && w.length - 3 >= 3) out.push(w.slice(0, -3));
    });
    return out;
  }
  function eslesir(meal, adaylar) {
    var m = meal.toLocaleLowerCase('tr');
    for (var i = 0; i < adaylar.length; i++) {
      var a = adaylar[i];
      if (m === a || (a.length >= 4 && m.indexOf(a) === 0)) return true;
    }
    return false;
  }
  // Sözlükte aranacak biçimler: önce tam biçim, sonra ekleri ayıklanmış kök adayları.
  function kokler(kelime) {
    var n = norm(kelime), out = [n];
    ONEKLER.forEach(function (p) {
      if (n.indexOf(p) === 0 && n.length - p.length >= 3) out.push(n.slice(p.length));
    });
    out.slice().forEach(function (k) {
      SONEKLER.forEach(function (s) {
        if (k.length - s.length >= 3 && k.slice(-s.length) === s) out.push(k.slice(0, -s.length));
      });
    });
    return out;
  }
  function arapIskelet(kelime) {
    return Array.from(norm(kelime)).map(function (c) { return ARAP_ISKELET[c] || ''; }).join('');
  }
  function turkIskelet(kelime) {
    return Array.from(kelime.toLocaleLowerCase('tr')).map(function (c) { return TUR_ISKELET[c] || ''; }).join('');
  }

  function ayetiIsle(arEl, trEl) {
    if (arEl.dataset.renk) return;
    var kelimeler = arEl.textContent.trim().split(/\s+/).filter(Boolean);
    var parcalar = trEl.textContent.split(/([\p{L}’'’\-]+)/u);
    var renk = kelimeler.map(function () { return -1; });
    var atama = {};
    var sira = 0;

    // 1) Sözlük: Arapça biçim (ya da ekleri ayıklanmış kökü) → meal kelimesi
    kelimeler.forEach(function (k, i) {
      if (ZAMIR_DURAK.test(k)) return;
      var ad = null;
      kokler(k).some(function (kok) {
        if (SOZLUK[kok]) { ad = SOZLUK[kok]; return true; }
        return false;
      });
      if (!ad) {
        var n = norm(k);
        [n, n.replace(/^[وفبلك]/, '')].some(function (z) {
          if (ZAMIR[z]) { ad = ZAMIR[z]; return true; }
          return false;
        });
      }
      if (!ad) return;
      renk[i] = sira++;
      var a = adaylar(ad);
      for (var j = 1; j < parcalar.length; j += 2) {
        if (atama[j] === undefined && eslesir(parcalar[j], a)) { atama[j] = renk[i]; break; }
      }
    });

    // 2) İskelet: eşleşmeyen Arapça kelime ile eşleşmeyen meal kelimesi aynı ünsüzlerden ise birleşir.
    kelimeler.forEach(function (k, i) {
      var sk = arapIskelet(k);
      if (sk.length < 2) return;
      for (var j = 1; j < parcalar.length; j += 2) {
        if (atama[j] !== undefined) continue;
        var tk = turkIskelet(parcalar[j]);
        if (tk.length < 2 || tk !== sk) continue;
        if (renk[i] < 0) renk[i] = sira++;
        atama[j] = renk[i];
        break;
      }
    });

    // 3) Zamir eki: boyanmamış Arapça kelimenin sonundaki bitişik zamir (هم كم نا ني) meal'deki zamire bağlanır.
    kelimeler.forEach(function (k, i) {
      if (renk[i] >= 0) return;
      var n = norm(k);
      ZAMIR_EKI.some(function (kural) {
        if (n.length - kural.ek.length < 2 || n.slice(-kural.ek.length) !== kural.ek) return false;
        for (var j = 1; j < parcalar.length; j += 2) {
          if (atama[j] !== undefined) continue;
          if (kural.meal.indexOf(parcalar[j].toLocaleLowerCase('tr')) >= 0) {
            renk[i] = sira++;
            atama[j] = renk[i];
            return true;
          }
        }
        return false;
      });
    });

    arEl.innerHTML = kelimeler.map(function (k, i) {
      return renk[i] >= 0
        ? '<span class="rk" data-c="' + (renk[i] % PALET.length) + '">' + kaçış(k) + '</span>'
        : kaçış(k);
    }).join(' ');
    trEl.innerHTML = parcalar.map(function (p, j) {
      return (j % 2 === 1 && atama[j] !== undefined)
        ? '<span class="rk" data-c="' + (atama[j] % PALET.length) + '">' + kaçış(p) + '</span>'
        : kaçış(p);
    }).join('');
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
      Object.keys(veri).forEach(function (k) {
        var n = norm(k);
        if (!(n in SOZLUK)) SOZLUK[n] = veri[k];
      });
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
