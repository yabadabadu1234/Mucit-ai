/* Renkli anlam (kelime meali): her Arapça kelime ile onun Türkçe karşılığı aynı renkte görünür.
 * Bir Arapça kelimenin karşılığı birden çok Türkçe sözcük olabilir; meal'de sahipsiz sözcük bırakılmaz.
 * Adımlar (her âyette, kelimelerin yaklaşık konumuna en yakın sözcük seçilir):
 *   1) kelime gövde + ön ek (و ف ب ل ك س) + bitişik zamir (ـه ـهم ـكم ـنا ...) olarak ayrılır;
 *      gövdenin sözlük karşılığı meal'de aranır;  2) ön ek ve zamir ekinin karşılığı aranır;
 *   3) ünsüz iskeleti aynı olan kelime ile sözcük birleşir;  4) kalan Arapça kelimelerle kalan
 *      içerik sözcükleri sayıca eşitse sırayla eşlenir;  5) geriye kalan sözcükler (de, ki, bir, ey…)
 *      komşu karşılığın parçası olur.
 * Veri: renk_sozluk.json, ilk tıklamada yüklenir. Kitap HTML'i şişmez. */
(function () {
  var PALET = ['#fde68a', '#a7f3d0', '#bfdbfe', '#fbcfe8', '#fecaca', '#ddd6fe',
               '#bae6fd', '#fed7aa', '#d9f99d', '#fca5a5', '#c7d2fe', '#99f6e4'];
  var SOZLUK = null;
  var BLOK = null; // nazm_blok.json: âyet metni → blok listesi (kelime-öbek verisi)
  var VAZIFE_RENK = {
    kasem: '#e9d5ff', fiil: '#fde68a', fail: '#a7f3d0', mubteda: '#bfdbfe', haber: '#fbcfe8',
    meful: '#fecaca', hal: '#ddd6fe', taalluk: '#bae6fd', sifat: '#fed7aa', sart: '#d9f99d',
    cevap: '#fca5a5', bag: '#c7d2fe', gaye: '#99f6e4', istisna: '#fde047', nida: '#f5d0fe',
    tekit: '#e7e5e4', diger: '#e2e8f0', ara: '#fef9c3'
  };
  var ONBELLEK = {};
  var DURAK = /^[ۖ-ۭ]+$/; // yalnız durak işareti (ۚ ۖ ۗ ۞ ۙ): kelime değildir

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

  // Sözlükte olmayan zamir ve edat gövdeleri (norm biçimi → meal karşılığı).
  var ZAMIR = {
    'هو': 'o, onu, ona, onda', 'هي': 'o, onu, ona, onda', 'هم': 'onlar, onları, onlara',
    'هما': 'onlar, ikisi, onları', 'هن': 'onlar, onları, onlara',
    'انت': 'sen, seni, sana, sende', 'انتم': 'siz, sizi, size, sizde', 'نحن': 'biz, bizi, bize, bizde',
    'انا': 'ben, beni, bana, bende',
    'له': 'onun, ona, onu', 'لها': 'onun, ona, onu', 'لهم': 'onların, onlara, onlar', 'لهما': 'onların, onlara',
    'لهن': 'onların, onlara, onlar', 'لك': 'senin, sana, seni', 'لكم': 'sizin, size, sizi',
    'لنا': 'bizim, bize, bizi', 'لي': 'benim, bana, beni',
    'به': 'onunla, ona, onda, bununla', 'بها': 'onunla, onda, bununla', 'بهم': 'onlarla, onlarda, onlara',
    'بهما': 'onlarla', 'بهن': 'onlarla', 'بك': 'seninle, sende', 'بنا': 'bizimle, bizde',
    'منه': 'ondan, onun', 'منها': 'ondan, onun', 'منهم': 'onlardan', 'منهن': 'onlardan', 'منكم': 'sizden, sizin',
    'عنه': 'ondan, onun', 'عنها': 'ondan, onun', 'عنهم': 'onlardan', 'فيه': 'onda, içinde, onun',
    'فيها': 'onda, içinde', 'فيهم': 'onlarda, içinde', 'فيهن': 'onlarda, içinde',
    'اليه': 'ona, ona doğru', 'اليها': 'ona, ona doğru', 'اليهم': 'onlara, onlara doğru',
    'اليكم': 'size, size doğru', 'معه': 'onunla, ile', 'معهم': 'onlarla, ile',
    'عليه': 'onun üzerine, ona, onun üstüne', 'عليها': 'onun üzerine', 'عليهم': 'onların üzerine, onlara',
    'عليهن': 'onların üzerine, onlara'
  };
  // Ön ek ve bitişik zamirin meal'deki karşılık sözcükleri.
  var ONEK_MEAL = {
    'و': ['ve'], 'ف': ['ve', 'böylece', 'ise', 'ama', 'fakat', 'artık'], 'ب': ['ile'],
    'ل': ['için'], 'ك': ['gibi'], 'س': ['yakında']
  };
  var SONEK_MEAL = {
    'ه': ['o', 'onu', 'ona', 'onun', 'ondan', 'onda', 'onunla'],
    'ها': ['o', 'onu', 'ona', 'onun', 'ondan', 'onda', 'onunla'],
    'هم': ['onlar', 'onları', 'onlara', 'onların', 'onlardan', 'onlarla', 'onlarda'],
    'هما': ['onlar', 'onları', 'onlara', 'onların', 'onlardan', 'onlarla', 'onlarda'],
    'هن': ['onlar', 'onları', 'onlara', 'onların', 'onlardan', 'onlarla', 'onlarda'],
    'كم': ['siz', 'sizi', 'size', 'sizin', 'sizden', 'sizinle'],
    'كن': ['siz', 'sizi', 'size', 'sizin', 'sizden', 'sizinle'],
    'ك': ['sen', 'seni', 'sana', 'senin', 'senden', 'seninle'],
    'ني': ['ben', 'beni', 'bana', 'benim', 'benden', 'benimle'],
    'ي': ['ben', 'beni', 'bana', 'benim', 'benden', 'benimle'],
    'نا': ['biz', 'bizi', 'bize', 'bizim', 'bizden', 'bizimle']
  };
  var ONEK_SECENEKLER = ['', 'و', 'ف', 'ب', 'ل', 'ك', 'س', 'وب', 'ول', 'وك', 'وس', 'فب', 'فل', 'فس'];
  var SONEK_SECENEKLER = ['', 'ه', 'ها', 'هم', 'هما', 'هن', 'كم', 'كن', 'ك', 'ني', 'ي', 'نا'];
  var SONEK_SOZLUKSUZ = ['هما', 'هم', 'هن', 'ها', 'كم', 'كن', 'نا', 'ني'];

  // Eşleşmeyen Türkçe sözcüğün hangi komşuya yapışacağı.
  var ONE_YAPIS = ['de', 'da', 'ki', 'mi', 'mı', 'mu', 'mü', 'ise', 'ile', 'için', 'gibi', 'olarak', 'kadar', 'bile', 'dahi'];
  var SONRA_YAPIS = ['bir', 'ey', 'bu', 'şu', 'o', 'her', 've', 'ya', 'yahut', 'veya', 'ama', 'fakat', 'çünkü',
                     'eğer', 'şayet', 'ne', 'hem'];

  // Hemzeler (ء ؤ ئ) ve harekeler atılır: "لَـَٔايَـٰتٍ" ile "ايات" aynı anahtara düşer.
  function norm(s) {
    return s.replace(/[ً-ٰـۖ-ۭ]/g, '')
      .replace(/[ءؤئ]/g, '')
      .replace(/[إأآٱ]/g, 'ا').replace(/ى/g, 'ي').replace(/\s+/g, ' ').trim();
  }
  function kaçış(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
  // Karşılık metninden aranacak Türkçe sözcükler; fiil mastarının (-mak/-mek) kökü de eklenir.
  function adaylar(karsilik, zamirMi) {
    var asgari = zamirMi ? 1 : 3, out = [];
    karsilik.toLocaleLowerCase('tr').split(/[\s,;()\/.:]+/).forEach(function (w) {
      if (w.length >= asgari && w !== 'ile' && w !== 'olan' && w !== 'için') out.push(w);
      if (/(mak|mek)$/.test(w) && w.length - 3 >= 3) out.push(w.slice(0, -3));
    });
    return out;
  }
  // Türkçe ekler gövdeyi uzatır/değiştirir (rab → rabbimiz, kitap → kitabı): ortak baş kısım yeterince uzunsa eşleşir.
  function ortakBas(a, b) {
    var n = Math.min(a.length, b.length), i = 0;
    while (i < n && a.charAt(i) === b.charAt(i)) i++;
    return i;
  }
  function eslesir(meal, aday) {
    for (var i = 0; i < aday.length; i++) {
      var a = aday[i];
      if (meal === a) return true;
      if (a.length >= 3 && meal.indexOf(a) === 0) return true;
      var o = ortakBas(a, meal);
      if (o >= 4 && o >= 0.7 * Math.min(a.length, meal.length)) return true;
    }
    return false;
  }
  function arapIskelet(kelime) {
    return Array.from(norm(kelime)).map(function (c) { return ARAP_ISKELET[c] || ''; }).join('');
  }
  function turkIskelet(kelime) {
    return Array.from(kelime).map(function (c) { return TUR_ISKELET[c] || ''; }).join('');
  }
  function sozlukte(govde) {
    if (SOZLUK[govde]) return { t: SOZLUK[govde], z: false };
    if (ZAMIR[govde]) return { t: ZAMIR[govde], z: true };
    return null;
  }
  function onekMeali(p) {
    var out = [];
    Array.from(p).forEach(function (h) { (ONEK_MEAL[h] || []).forEach(function (w) { out.push(w); }); });
    return out;
  }

  // Kelimeyi ön ek + gövde + zamir eki olarak ayırır; en az soyma ile sözlükte bulunan biçimi seçer.
  function ayristir(kelime) {
    var n0 = norm(kelime);
    if (ONBELLEK[n0]) return ONBELLEK[n0];
    var en = null, enMaliyet = 99;
    ONEK_SECENEKLER.forEach(function (p) {
      if (n0.indexOf(p) !== 0) return;
      var rest = n0.slice(p.length);
      var govdeler = [[rest, 0]];
      if (rest.indexOf('ال') === 0) govdeler.push([rest.slice(2), 2]);
      if (p && p.slice(-1) === 'ل' && rest.charAt(0) === 'ل') govdeler.push([rest.slice(1), 1]);
      govdeler.forEach(function (gv) {
        SONEK_SECENEKLER.forEach(function (s) {
          var g = gv[0];
          if (s && (g.length - s.length < 2 || g.slice(-s.length) !== s)) return;
          var govde = s ? g.slice(0, -s.length) : g;
          if (govde.length < 2) return;
          var m = p.length + gv[1] + s.length;
          if (m >= enMaliyet) return;
          var gl = sozlukte(govde);
          if (gl) { en = { gl: gl, p: p, s: s }; enMaliyet = m; }
        });
      });
    });
    var sonuc;
    if (en) {
      sonuc = { aday: adaylar(en.gl.t, en.gl.z), onek: onekMeali(en.p), sonek: SONEK_MEAL[en.s] || [] };
    } else {
      // Sözlükte yoksa yalnız ön ek harfi ve çok harfli zamir eki aranır.
      var r = n0, p2 = '', s2 = '';
      if ((r.charAt(0) === 'و' || r.charAt(0) === 'ف') && r.length - 1 >= 3) { p2 = r.charAt(0); r = r.slice(1); }
      if ('بلكس'.indexOf(r.charAt(0)) >= 0 && r.length - 1 >= 3) { p2 += r.charAt(0); r = r.slice(1); }
      SONEK_SOZLUKSUZ.some(function (s) {
        if (r.length - s.length >= 3 && r.slice(-s.length) === s) { s2 = s; return true; }
        return false;
      });
      sonuc = { aday: [], onek: onekMeali(p2), sonek: SONEK_MEAL[s2] || [] };
    }
    ONBELLEK[n0] = sonuc;
    return sonuc;
  }

  // Her blok bir sütun: üstte Arapça öbek, hemen altında Türkçe karşılığı.
  // Sütunlar sağdan sola dizilir (Arapça sırası); satır dolunca alt satıra geçer.
  function blokIsle(arEl, trEl, kayit) {
    arEl.innerHTML = '<div class="ayet-kutu">' + kayit.b.map(function (b) {
      return '<div class="blok" data-v="' + b[2] + '"><span class="blok-ar">' + kaçış(b[0]) +
        '</span><span class="blok-tr">' + kaçış(b[1]) + '</span></div>';
    }).join('') + '</div>';
    trEl.style.display = 'none';
    arEl.dataset.renk = '1';
    trEl.dataset.renk = '1';
  }

  function ayetiIsle(arEl, trEl) {
    if (arEl.dataset.renk) return;
    if (BLOK) {
      var kayit = BLOK[norm(arEl.textContent)];
      if (kayit) { blokIsle(arEl, trEl, kayit); return; }
    }
    var kelimeler = arEl.textContent.trim().split(/\s+/).filter(Boolean);
    var gercek = kelimeler.map(function (k) { return !DURAK.test(k); });
    var gs = [], say = 0;
    kelimeler.forEach(function (k, i) { gs[i] = gercek[i] ? say++ : -1; });
    var parcalar = trEl.textContent.split(/([\p{L}’'’\-]+)/u);
    var W = [];
    for (var j = 1; j < parcalar.length; j += 2) if (/\p{L}/u.test(parcalar[j])) W.push(j);
    // Birkaç âyetin mealini taşıyan pencere kartları ("(6–14) …") tek âyetin Arapçasıyla eşlenemez; dokunulmaz.
    if (/^\s*\(\d+\s*[–-]\s*\d+\)/.test(trEl.textContent) || W.length > 3 * say + 8) return;
    var ad = W.map(function (j) { return parcalar[j].toLocaleLowerCase('tr'); });
    var cw = W.map(function () { return -1; });
    var ci = kelimeler.map(function () { return -1; });
    var sira = 0;
    var cozum = kelimeler.map(function (k, i) { return gercek[i] ? ayristir(k) : null; });

    // Kelimenin yaklaşık konumuna en yakın, henüz sahibi olmayan uygun sözcük.
    function enYakin(i, uygun) {
      var beklenen = (gs[i] + 0.5) / Math.max(say, 1) * W.length, en = -1, fark = 1e9;
      for (var p = 0; p < W.length; p++) {
        if (cw[p] >= 0 || !uygun(ad[p])) continue;
        var f = Math.abs(p - beklenen);
        if (f < fark) { fark = f; en = p; }
      }
      return en;
    }
    function ata(i, p) {
      if (ci[i] < 0) ci[i] = sira++;
      cw[p] = ci[i];
    }

    // 1) gövdenin sözlük karşılığı
    kelimeler.forEach(function (k, i) {
      var c = cozum[i];
      if (!c || !c.aday.length) return;
      var p = enYakin(i, function (w) { return eslesir(w, c.aday); });
      if (p >= 0) ata(i, p);
    });
    // 2) ön ek (ve, ile, için …) ve 3) bitişik zamir (onlar, size, biz …)
    ['onek', 'sonek'].forEach(function (tur) {
      kelimeler.forEach(function (k, i) {
        var c = cozum[i];
        if (!c || !c[tur].length) return;
        var p = enYakin(i, function (w) { return c[tur].indexOf(w) >= 0; });
        if (p >= 0) ata(i, p);
      });
    });
    // 4) ünsüz iskeleti aynı olan kelime ile sözcük
    kelimeler.forEach(function (k, i) {
      if (!gercek[i] || ci[i] >= 0) return;
      var sk = arapIskelet(k);
      if (sk.length < 2) return;
      var p = enYakin(i, function (w) { var t = turkIskelet(w); return t.length >= 2 && t === sk; });
      if (p >= 0) ata(i, p);
    });
    // 5) Omurga: eşleşmiş kelimelerden meal konumu sıralı kalan en uzun dizi. Omurga aralarındaki
    //    eşleşmemiş Arapça kelimelerle eşleşmemiş içerik sözcükleri sırayla paylaştırılır.
    var cap = [];
    kelimeler.forEach(function (k, i) {
      if (ci[i] < 0) return;
      var mn = 1e9, mx = -1;
      cw.forEach(function (c, p) { if (c === ci[i]) { if (p < mn) mn = p; if (p > mx) mx = p; } });
      cap.push({ i: i, mn: mn, mx: mx });
    });
    var uz = cap.map(function () { return 1; }), geri = cap.map(function () { return -1; }), eniyi = -1;
    cap.forEach(function (a, x) {
      for (var y = 0; y < x; y++) {
        if (cap[y].mx < a.mn && uz[y] + 1 > uz[x]) { uz[x] = uz[y] + 1; geri[x] = y; }
      }
      if (eniyi < 0 || uz[x] > uz[eniyi]) eniyi = x;
    });
    var omurga = [];
    for (var x = eniyi; x >= 0; x = geri[x]) omurga.unshift(cap[x]);
    omurga.unshift({ i: -1, mn: -1, mx: -1 });
    omurga.push({ i: kelimeler.length, mn: W.length, mx: W.length });
    for (var g = 0; g + 1 < omurga.length; g++) {
      var U = [], M = [], t, p;
      for (t = omurga[g].i + 1; t < omurga[g + 1].i; t++) if (gercek[t] && ci[t] < 0) U.push(t);
      for (p = omurga[g].mx + 1; p < omurga[g + 1].mn; p++) {
        if (cw[p] < 0 && ONE_YAPIS.indexOf(ad[p]) < 0 && SONRA_YAPIS.indexOf(ad[p]) < 0) M.push(p);
      }
      if (!U.length || !M.length) continue;
      if (M.length >= U.length) {
        U.forEach(function (tk, u) {
          for (var y = Math.floor(u * M.length / U.length); y < Math.floor((u + 1) * M.length / U.length); y++) ata(tk, M[y]);
        });
      } else {
        M.forEach(function (pp, y) { ata(U[Math.floor((y + 0.5) * U.length / M.length)], pp); });
      }
    }
    // 6) hâlâ sahipsiz sözcükler komşu karşılığın parçası olur
    var ilk = cw.slice();
    for (var p = 0; p < W.length; p++) {
      if (cw[p] >= 0) continue;
      var sonraYapis = SONRA_YAPIS.indexOf(ad[p]) >= 0, hedef = -1, q;
      if (!sonraYapis) { for (q = p - 1; q >= 0; q--) if (cw[q] >= 0) { hedef = cw[q]; break; } }
      if (hedef < 0) { for (q = p + 1; q < W.length; q++) if (ilk[q] >= 0) { hedef = ilk[q]; break; } }
      if (hedef < 0) { for (q = p - 1; q >= 0; q--) if (cw[q] >= 0) { hedef = cw[q]; break; } }
      if (hedef >= 0) cw[p] = hedef;
    }

    arEl.innerHTML = kelimeler.map(function (k, i) {
      return ci[i] >= 0
        ? '<span class="rk" data-c="' + (ci[i] % PALET.length) + '">' + kaçış(k) + '</span>'
        : kaçış(k);
    }).join(' ');
    var cpos = {};
    W.forEach(function (j, p) { cpos[j] = cw[p]; });
    var html = [], b = 0;
    while (b < parcalar.length) {
      if (b % 2 === 1 && cpos[b] !== undefined && cpos[b] >= 0) {
        var c = cpos[b], son = b;
        while (son + 2 < parcalar.length && cpos[son + 2] === c && /^\s*$/.test(parcalar[son + 1])) son += 2;
        html.push('<span class="rk" data-c="' + (c % PALET.length) + '">' + kaçış(parcalar.slice(b, son + 1).join('')) + '</span>');
        b = son + 1;
      } else {
        html.push(kaçış(parcalar[b]));
        b++;
      }
    }
    trEl.innerHTML = html.join('');
    arEl.dataset.renk = '1';
    trEl.dataset.renk = '1';
  }

  function stil() {
    var s = document.createElement('style');
    s.textContent = Object.keys(VAZIFE_RENK).map(function (v) {
      return 'body.renk-acik .blok[data-v="' + v + '"]{background:' + VAZIFE_RENK[v] + ';}';
    }).join('\n') + '\n' + '.ayet-kutu{display:flex;flex-direction:row;flex-wrap:wrap;gap:6px 4px;direction:rtl;}' +
      '.blok{display:inline-flex;flex-direction:column;align-items:flex-end;border-radius:4px;padding:3px 6px;}' +
      '.blok-ar{direction:rtl;font-size:1.25em;line-height:1.9;}' +
      '.blok-tr{direction:ltr;font-size:.85em;color:#334155;text-align:left;}' + '\n' + PALET.map(function (c, i) {
      return 'body.renk-acik .rk[data-c="' + i + '"]{background:' + c + ';border-radius:3px;}';
    }).join('\n') + '\nbody.renk-acik .rk{padding:0 1px;}';
    document.head.appendChild(s);
  }

  function baslat(dugme) {
    dugme.disabled = true; dugme.textContent = 'Renkler yükleniyor…';
    Promise.all([
      fetch('renk_sozluk.json').then(function (r) { return r.json(); }),
      fetch('nazm_blok.json').then(function (r) { return r.json(); }).catch(function () { return null; })
    ]).then(function (sonuc) {
      var veri = sonuc[0];
      BLOK = sonuc[1];
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
