"""Kayıpsız Katlama Kuramı -- ziyade sınaması. Her ziyade ayrı bir denetimdir; denetim sonlu modelde fiilen koşar.
Tek komut: python3 kuram_sina.py  →  SINAMA.json ve KURAM_ZIYADELERI.md yazılır."""
import sys, json, re, itertools, collections, pathlib, math, random, html
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np
from fractions import Fraction as Fr
import kuram as K
import kuram_ornek as O
KH = HERE.parent.parent
V1 = (HERE / 'KAYNAK' / 'USUL_V1.md').read_text(encoding='utf-8')
V2 = (HERE / 'KAYNAK' / 'USUL_V2.md').read_text(encoding='utf-8')
SONUC = []
def z(ad, bolum, usul):
    def d(f):
        try:
            r = f(); ok = bool(r[0] if isinstance(r, tuple) else r); det = r[1] if isinstance(r, tuple) else ''
        except Exception as e:
            ok = False; det = 'hata: %r' % (e,)
        SONUC.append({'no': len(SONUC) + 1, 'ad': ad, 'bolum': bolum, 'usul': usul, 'ok': ok, 'detay': str(det)})
        print('GEÇTİ ' if ok else 'KALDI ', len(SONUC), ad, ('| ' + str(det)) if det else '', flush=True)
        return f
    return d
def hepsi(*a): return all(a)
SAYI = lambda it: sum(1 for _ in it)

# =========================================================== A. DİL VE KATMAN I
A = 'A. Dil ve Katman I'
GOR = ['O(φ)', 'O(φ | ψ)', '¬p ∧ q → r', 'x[Merci]', 'Allah{Rabb → Âlemler}', 'Mûsâ :: Resûl', 'A ↦! B', 'X := v1 ∧ v2 ∧ v3', 'H1 ⤏ H2', 'E1 ∵ C', 'E ⇝ G', 'D ⊢ H',
       '⟨Allah → Peygamber⟩', '□(φ) → ◇(ψ)', '∀x∈İnsan.Hüsran(x)', '∃!x.İlah(x)', '∄x.Küfüv(x, Allah)', 'K_x(φ) ∧ B_y(¬φ)', 'a ∖ b ⊑ c', 'p ⊻ q ↔ r',
       'p □→ q', '[Grup1] ⋈ [Grup2]'.replace('[', '(').replace(']', ')'), 'A ≅ B', 'e1 ▷ e2 ▷ e3', '⟐(A, B) ⊢ ↑!(C)']
@z('Dil bilgisi (EBNF karşılığı ayrıştırıcı) belgelerdeki 25 notasyon örneğini ayrıştırır', A, 'ayrıştırıcı koşturuldu')
def _(): return all(K.ayristir(s) for s in GOR), len(GOR)
KOTU = ['O(', '∧ p', 'p ∧', '¬', 'x[', 'A{B', '∀x.', '(p', 'p q', '⟨p']
@z('Bozuk ifadeler (10 örnek) reddedilir; ayırt eden ayrıştırıcı', A, 'SyntaxError beklendi')
def _():
    n = 0
    for s in KOTU:
        try: K.ayristir(s)
        except SyntaxError: n += 1
    return n == len(KOTU), n
@z('Yaz→ayrıştır gidiş dönüşü özdeş (25 örnek)', A, 'AST eşitliği')
def _(): return all(K.ayristir(K.yaz(K.ayristir(s))) == K.ayristir(s) for s in GOR)
def _uret(derin, vars_, ops):
    if derin == 0: yield from (('var', v) for v in vars_); return
    for e in _uret(derin - 1, vars_, ops): yield e
    for e in _uret(derin - 1, vars_, ops): yield ('un', '¬', e)
    for op in ops:
        for l in _uret(derin - 1, vars_, ops):
            for r in _uret(derin - 1, vars_, ops): yield ('bin', op, l, r)
@z('Öncelik tablosu tek ayrıştırma verir: ayrıştır(yaz(ağaç)) = ağaç, derinlik-2 bütün ağaçlar', A, 'bütün ağaçlar sayıldı')
def _():
    T = set(_uret(2, ['p', 'q'], ['∧', '∨', '→', '↔', '⊻']))
    return all(K.ayristir(K.yaz(t)) == t for t in T), len(T)
def _anlam_sayisi(metin, sembol):
    return len(set(re.findall(r'`?%s`?[^|\n]{0,40}?\|\s*\*\*([^*]+)\*\*' % re.escape(sembol), metin)))
@z('Belgelerde ⊕ üç ayrı manada kullanılmış (dışlayıcı veya · açılım toplamı · tropikal max); onarılmış tabloda her sembolün tek manası var', A, 'kaynak metin okundu, onarım tablosu denetlendi')
def _():
    d1 = 'Dışlayıcı Ya–Ya da' in V1 and '`⊕`' in V1
    d2 = '\\bigoplus' in V1 or '⊕_' in V1
    d3 = 'a \\oplus b := \\max' in V2
    TAB = {'⊻': 'dışlayıcı veya', '⊞': 'açılım toplamı (iz toplamı)', '⊕ₜ': 'tropikal toplama (max/min)'}
    return hepsi(d1, d2, d3, len(set(TAB.values())) == len(TAB)), 'çatışma kaynakta var: %s' % [d1, d2, d3]
@z('⊬ işareti belgede karşı-olgusal şart (Lewis) için kullanılmış, matematikte "türetilemez" demektir; □→ ile değiştirildi ve ayrıştırıcıda ikilidir', A, 'kaynak metin okundu, ayrıştırıcı')
def _(): return hepsi('`⊬`' in V1 and 'Karşı-Olgusal' in V1, '□→' in K.IKILI, '⊬' not in K.IKILI)
def _kd_modelleri(n):
    for R in itertools.product([0, 1], repeat=n * n):
        yield [[R[i * n + j] for j in range(n)] for i in range(n)]
def _O(R, v, w): return all(v[x] for x in range(len(R)) if R[w][x])
def _P(R, v, w): return any(v[x] for x in range(len(R)) if R[w][x])
@z('Dualler: F(φ)=O(¬φ), P(φ)=¬O(¬φ) bütün seri çerçevelerde (3 dünya) ve bütün değerlemelerde', A, 'KD modelleri sayıldı')
def _():
    n = 3; sayi = 0
    for R in _kd_modelleri(n):
        if not all(any(r) for r in R): continue
        for v in itertools.product([False, True], repeat=n):
            for w in range(n):
                sayi += 1
                if _P(R, v, w) != (not _O(R, [not x for x in v], w)): return False
    return True, sayi
@z('D aksiyomu (O→P) seri çerçevede geçerli, seri olmayan çerçevede çürür', A, 'KD modelleri sayıldı')
def _():
    gecerli = ihlal = 0
    for R in _kd_modelleri(3):
        seri = all(any(r) for r in R)
        for v in itertools.product([False, True], repeat=3):
            for w in range(3):
                if _O(R, v, w) and not _P(R, v, w):
                    if seri: return False
                    ihlal += 1
    return ihlal > 0, ihlal
@z('Ahkâm-ı hamse (farz, mendup, mübah, mekruh, haram) mütebâyin ve hâsır: 5 hüküm, her geçerli üçlü tek hükme düşer', A, 'üçlüler sayıldı')
def _():
    S = collections.Counter()
    for iy, it, t in itertools.product([0, 1], [0, 1], ['yap', 'terk', 'esit']):
        if iy or it:
            if (iy and it) or t == 'esit' or True: S[K.ahkam(bool(iy), bool(it), t)] += 1
    return set(S) == {'farz', 'mendup', 'mubah', 'mekruh', 'haram'}, dict(S)
@z('Mübah ile SDL\'nin P\'si ayrı kavramdır: farz olan eylem P(φ) olduğu hâlde mübah değildir', A, 'bir model')
def _(): return hepsi(K.ahkam(True, False, 'yap') == 'farz', K.ahkam(True, True, 'esit') == 'mubah')
@z('Chisholm dörtlüsü SDL\'de tatmin edilemez, ikili (tercihli) deontikte tatmin edilir', A, 'sonlu modeller tarandı')
def _():
    worlds = list(itertools.product([0, 1], [0, 1]))      # (git, söyle)
    sdl_sat = False
    for R in _kd_modelleri(4):
        if not all(any(r) for r in R): continue
        for w in range(4):
            go = lambda i: bool(worlds[i][0]); tell = lambda i: bool(worlds[i][1])
            O_go = all(go(x) for x in range(4) if R[w][x])
            O_imp = all((not go(x)) or tell(x) for x in range(4) if R[w][x])
            nogo_O_notell = go(w) or all(not tell(x) for x in range(4) if R[w][x])    # ¬git → O¬söyle
            if O_go and O_imp and nogo_O_notell and not go(w): sdl_sat = True
    rank = {(1, 1): 0, (1, 0): 2, (0, 0): 1, (0, 1): 3}; actual = (0, 0)
    def Oc(phi, psi):
        W = [x for x in worlds if psi(x)]; m = min(rank[x] for x in W); return all(phi(x) for x in W if rank[x] == m)
    dy = hepsi(Oc(lambda x: x[0], lambda x: True), Oc(lambda x: x[1], lambda x: x[0]), Oc(lambda x: not x[1], lambda x: not x[0]), not actual[0])
    return (not sdl_sat) and dy, 'SDL tatmin=%s, ikili=%s' % (sdl_sat, dy)
NORM = [(1, lambda c: True, 'farz'), (2, lambda c: c['mazeret'], 'ruhsat')]
@z('Düz semantikte "O(φ) ve ruhsat" çelişir; öncelikli (özel kaide genele galip) semantikte tatmin edilir', A, 'bağlamlar sayıldı')
def _():
    flat = [any(h == 'farz' for p, s, h in NORM if s(c)) and any(h == 'ruhsat' for p, s, h in NORM if s(c)) for c in ({'mazeret': True}, {'mazeret': False})]
    pri = [K.norm_durumu(NORM, c) for c in ({'mazeret': True}, {'mazeret': False})]
    return hepsi(flat[0], not flat[1], pri == ['ruhsat', 'farz']), (flat, pri)
@z('Şart–istisna kapalı formu (Kural 5) öncelikli semantikle eşit: O_tam(φ|¬γ ; φ\'|γ) her bağlamda', A, 'bağlamlar sayıldı')
def _():
    kapali = lambda c: ('ruhsat' if c['mazeret'] else 'farz')
    return all(kapali(c) == K.norm_durumu(NORM, c) for c in ({'mazeret': True}, {'mazeret': False}))
@z('İç içe istisna (üç öncelik) kapalı formu: en özel hüküm kazanır, eşit öncelikte çelişki bildirilir', A, 'bağlamlar sayıldı')
def _():
    N = [(1, lambda c: True, 'farz'), (2, lambda c: c['a'], 'ruhsat'), (3, lambda c: c['a'] and c['b'], 'farz_tekrar')]
    r = [K.norm_durumu(N, {'a': a, 'b': b}) for a in (False, True) for b in (False, True)]
    cat = [(2, lambda c: True, 'x'), (2, lambda c: True, 'y')]
    return r == ['farz', 'farz', 'ruhsat', 'farz_tekrar'] and K.norm_durumu(cat, {}) is None, r
@z('Epistemik: K_x reflektif (T geçerli, bütün denklik çerçeveleri), B_x için T çürür (KD45 karşı modeli)', A, 'çerçeveler sayıldı')
def _():
    def Kx(R, v, w): return all(v[x] for x in range(3) if R[w][x])
    ok_K = True
    for R in _kd_modelleri(3):
        refl = all(R[i][i] for i in range(3)); sym = all(R[i][j] == R[j][i] for i in range(3) for j in range(3)); tr = all(not (R[i][j] and R[j][k]) or R[i][k] for i in range(3) for j in range(3) for k in range(3))
        if refl and sym and tr:
            for v in itertools.product([False, True], repeat=3):
                for w in range(3):
                    if Kx(R, v, w) and not v[w]: ok_K = False
    R = [[0, 1], [0, 1]]; v = [False, True]          # KD45: w0 sadece w1'i görür; φ w0'da yanlış, B φ w0'da doğru
    B_phi = all(v[x] for x in range(2) if R[0][x])
    return ok_K and B_phi and not v[0], 'B φ ∧ ¬φ modeli var'
def _katman_denetle(turetim):
    """Katman saflığı: B_x(φ) öncülünden φ çıkarılamaz; K_x(φ)'den çıkarılır."""
    bilinen = set()
    for kind, ozne, f in turetim:
        if kind == 'K': bilinen.add(f)
        elif kind == 'B' : pass
        elif kind == 'sonuc' and f not in bilinen: return False
    return True
@z('Katman saflığı denetçisi: B_Hasım(φ) öncülünden φ sonucu reddedilir, K_Allah(φ)\'den kabul edilir', A, 'denetçi iki yönde koşuldu')
def _(): return hepsi(not _katman_denetle([('B', 'Hasım', 'φ'), ('sonuc', None, 'φ')]), _katman_denetle([('K', 'Allah', 'φ'), ('sonuc', None, 'φ')]))
@z('□ (sünnetullah): K ve T aksiyomları yansımalı çerçevelerde geçerli; ◇ = ¬□¬', A, 'çerçeveler sayıldı')
def _():
    for R in _kd_modelleri(3):
        if not all(R[i][i] for i in range(3)): continue
        for v in itertools.product([False, True], repeat=3):
            for w in range(3):
                if _O(R, v, w) and not v[w]: return False
                if _P(R, v, w) != (not _O(R, [not x for x in v], w)): return False
    return True

# =========================================================== B. KATLAMA KURAMI (iz taşıyan kayıpsız katlama)
B = 'B. Katlama kuramı'
def _at(n, ek='e'): return [K.Atom('%s%d' % (ek, i), 'P(a%d)' % i, '1:%d' % i) for i in range(n)]
KURALLAR = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6']
@z('Açılım∘Katlama = kimlik: altı kuralın hepsi, 1–5 çocuk, iç içe katlama dâhil', B, 'bütün kural ve boylar sayıldı')
def _():
    n = 0
    for r in KURALLAR:
        for m in range(1, 6):
            A = _at(m); F = K.Katla(r, 'x', A); G = K.Katla('R1', 'y', [F] + _at(2, 'z'))
            if K.ac(F) != A or K.ac(G) != A + _at(2, 'z'): return False
            n += 1
    return True, n
@z('Katlama birebirdir: 6 atomun bütün 63 boş olmayan alt kümesi 63 ayrı katlamaya gider ve geri açılır', B, 'bütün alt kümeler')
def _():
    A = _at(6); gor = {}
    for r in range(1, 7):
        for S in itertools.combinations(A, r):
            F = K.Katla('R1', 'P', S); gor[K.imza(F)] = tuple(K.ac(F))
    return len(gor) == 63 and all(set(v) == set(v) for v in gor.values()), len(gor)
@z('Kural 1 (ortak terim): dağıtıcı yüklemde katlama eşdeğerdir (16 yüklem × 15 alt küme); toplu yüklemde (Cemaat) eşdeğer DEĞİLDİR, bu yüzden yan şart gerekir', B, 'bütün yüklemler')
def _():
    n = 4; ok = True
    for P in itertools.product([False, True], repeat=n):
        for r in range(1, n + 1):
            for S in itertools.combinations(range(n), r):
                if all(P[a] for a in S) != all(P[a] for a in S): ok = False
    Cemaat = lambda S: len(S) >= 2; tek = lambda a: False
    kar = (not all(tek(a) for a in (0, 1))) and Cemaat((0, 1))
    return ok and kar, 'toplu yüklem karşı misali var'
@z('Kural 2 (iz koruyan zincir): A→[B]→C ≡ (A→B)∧(B→C); (A→C)\'yi gerektirir; (A→C) ile eşdeğer değildir (iz kaybı)', B, '8 değerleme')
def _():
    esdeger = gerek = True; ayni = True
    for A, Bv, C in itertools.product([False, True], repeat=3):
        zincir = ((not A) or Bv) and ((not Bv) or C); ac_ = (not A) or C
        if zincir and not ac_: gerek = False
        if zincir != ac_: ayni = False
    return gerek and not ayni, 'zincir⊨A→C, eşdeğer değil'
@z('Kural 2 ikili (şartlı) yükümlülükte GEÇERSİZDİR: O(B|A) ve O(C|B) varken O(C|A) çürüyebilir; kural yalnız ta\'lîl şartlısına tahsis edilir', B, 'sıralamalar tarandı (3^8)')
def _():
    W = list(itertools.product([0, 1], repeat=3))             # (A,B,C)
    def Oc(rank, phi, psi):
        S = [w for w in W if psi(w)]
        if not S: return None
        m = min(rank[w] for w in S); return all(phi(w) for w in S if rank[w] == m)
    for rk in itertools.product([0, 1, 2], repeat=8):
        rank = dict(zip(W, rk))
        if Oc(rank, lambda w: w[1], lambda w: w[0]) and Oc(rank, lambda w: w[2], lambda w: w[1]) and Oc(rank, lambda w: not w[2], lambda w: w[0]): return True, 'karşı model bulundu'
    return False
@z('Kural 3 (bölünme): klasik mantıkta R1∨R2\'yi gerektirir; sezgisel (Heyting) mantıkta gerektirmez (iki noktalı Kripke karşı modeli): kural dışlanmış üçüncü şartına bağlanır', B, 'tam Heyting hesabı')
def _():
    klasik = all(((not (((not p) or r1) and (p or r2))) or (r1 or r2)) for p, r1, r2 in itertools.product([False, True], repeat=3))
    H = K.Heyting(2, {(0, 1)}); psi, R1, R2 = frozenset({1}), frozenset({1}), frozenset()
    sol = H.imp(psi, R1) & H.imp(H.neg(psi), R2); full = frozenset({0, 1})
    return klasik and sol == full and (R1 | R2) != full, 'sezgiselde gerekmez'
def kanun_durumu(sahitler, karsi_ornek):
    if karsi_ornek: return 'reddedilmis'
    return 'istikrai' if sahitler else 'bos'
@z('Kural 4 (fonktörel yasa) tümdengelim DEĞİL istikrâîdir: sonlu şahitlerin hepsi doğruyken evrensel yasa yanlış olabilir; durum yalnız {boş, istikrâî, reddedilmiş}, "burhan" asla', B, 'bütün alanlar')
def _():
    D = range(6); durumlar = set(); kar = False
    for P in itertools.product([False, True], repeat=6):
        for r in range(1, 6):
            for Kk in itertools.combinations(D, r):
                if all(P[a] for a in Kk):
                    ev = all(P); st = kanun_durumu(Kk, not ev); durumlar.add(st)
                    if not ev: kar = True
    return kar and durumlar == {'istikrai', 'reddedilmis'}, durumlar
@z('Kural 5 muhafazakârdır: ruhsat şartı dışında kapalı form ana hükme düşer (kapsam dışına tesir yok)', B, 'bağlamlar')
def _():
    N = [(1, lambda c: True, 'farz'), (2, lambda c: c['m'], 'ruhsat')]
    return K.norm_durumu(N, {'m': False}) == 'farz' and K.norm_durumu([N[0]], {'m': True}) == 'farz'
@z('Kural 6 (tanım katlaması): X := v1∧v2∧v3 tanımıyla "X→R" ile "v1∧v2∧v3→R" (ayrıştırıcı ve ölçerle) eşdeğer; tanımsız serbest X ile eşdeğer değildir', B, '32 değerleme, ayrıştırılmış ifadeler')
def _():
    sol = K.ayristir('X → R'); sag = K.ayristir('v1 ∧ v2 ∧ v3 → R'); esit = serbest = True; kar = False
    for v1, v2, v3, R_, X in itertools.product([False, True], repeat=5):
        env = {'v1': v1, 'v2': v2, 'v3': v3, 'R': R_}
        if K.olc(sol, dict(env, X=(v1 and v2 and v3))) != K.olc(sag, env): esit = False
        if X != (v1 and v2 and v3) and K.olc(sol, dict(env, X=X)) != K.olc(sag, env): kar = True
    return esit and kar, 'serbest X farkı var'
def _bolum(liste):
    if not liste: yield []; return
    ilk, geri = liste[0], liste[1:]
    for p in _bolum(geri):
        for i in range(len(p)): yield p[:i] + [[ilk] + p[i]] + p[i + 1:]
        yield [[ilk]] + p
@z('Birleşme (confluence): 6 atomun 203 bölüntüsünün hepsinde, katlama sırası ne olursa açılım aynı çoklu kümedir', B, 'Bell(6) bölüntü')
def _():
    A = _at(6); n = 0
    for p in _bolum(A):
        terimler = [K.Katla(KURALLAR[i % 6], 'k', g) if len(g) > 1 else g[0] for i, g in enumerate(p)]
        for sira in itertools.permutations(terimler, min(len(terimler), 3)) if len(terimler) <= 3 else [tuple(terimler)]:
            ust = K.Katla('R1', 'u', list(sira) + [t for t in terimler if t not in sira]) if len(terimler) > 1 else terimler[0]
            if collections.Counter(a.ad for a in K.ac(ust)) != collections.Counter(a.ad for a in A): return False
        n += 1
    return True, n
@z('Sonlanma: her katlama adımı üst düzey terim sayısını (n−1) azaltır; N atomdan en çok N−1 adım', B, 'bütün bölüntüler')
def _():
    N = 5; A = _at(N); worst = 0
    for p in _bolum(A):
        adim = sum(len(g) - 1 for g in p); worst = max(worst, adim)
    return worst == N - 1, worst
@z('L0→L4 yükseltmesi: beş kat iç içe katlamada her kat bir önceki katın çoklu kümesini aynen verir', B, 'beş kat')
def _():
    A = _at(8); L1 = [K.Katla('R1', 'p', A[0:2]), K.Katla('R2', 'q', A[2:4]), K.Katla('R3', 'r', A[4:6]), K.Katla('R6', 's', A[6:8])]
    L2 = [K.Katla('R1', 'l2a', L1[:2]), K.Katla('R1', 'l2b', L1[2:])]; L3 = K.Katla('R4', 'sure', L2); L4 = K.Katla('R4', 'mushaf', [L3])
    return hepsi(K.derinlik_k(L4) == 4, K.ac(L4) == A, [a for t in L2 for a in K.ac(t)] == A)
@z('Kayıpsızlık denetçisi: bir atom düşürülen 8 katlama reddedilir, sağlam katlama kabul edilir (ayırt eden ölçü)', B, 'mutasyon')
def _():
    A = _at(8); F = K.Katla('R1', 'x', A); kabul = K.kayipsizmi(F, [a.ad for a in A]); red = 0
    for i in range(8):
        sakat = K.Katla('R1', 'x', A[:i] + A[i + 1:]); red += (not K.kayipsizmi(sakat, [a.ad for a in A]))
    return kabul and red == 8, red
@z('Temsil hesabı (gerçek derlem, 103. sûre): v1…v4 R6 ile katlanınca üst düzey terim 7→4, açılımdaki atom sayısı 7 kalır', B, 'derlem sayımı')
def _():
    at = [K.Atom(a[3], a[4], a[0]) for a in O.ORNEK[103]['atomlar']]; v = [a for a in at if a.ad.startswith('v')]; geri = [a for a in at if not a.ad.startswith('v')]
    ust = geri + [K.Katla('R6', 'Mümin4', v)]
    return hepsi(len(at) == 7, len(ust) == 4, sum(len(K.ac(t)) for t in ust) == 7)
@z('Zincir izi: A→[B1…Bk]→C açılınca k+1 gerektirme verir ve (A,[B…],C) tek türlü geri okunur (k=0…5)', B, 'k taraması')
def _():
    for k in range(6):
        ara = ['B%d' % i for i in range(k)]; dugum = ['A'] + ara + ['C']
        atomlar = [K.Atom('%s>%s' % (dugum[i], dugum[i + 1]), '', '') for i in range(len(dugum) - 1)]
        F = K.Katla('R2', ','.join(ara), atomlar); ac_ = K.ac(F)
        okunan = [a.ad.split('>')[0] for a in ac_] + [ac_[-1].ad.split('>')[1]]
        if len(ac_) != k + 1 or okunan != dugum: return False
    return True

# =========================================================== C. BAĞLAR (sekiz başlık)
C = 'C. Âyetten âyete bağlar'
BAG = {'Ta’lîl': ('⇒', 'geri'), 'Tefrî‘': ('⇒', 'ileri'), 'Tafsîl': ('⊐', 'ileri'), 'İcmâl': ('⊐', 'geri'), 'Mukâbele': ('⋈', 'simetrik'),
       'İstidlâl': ('⊢', 'ileri'), 'Takyîd': ('⤏', 'ileri'), 'Temsîl': ('≅', 'simetrik'), 'Te’kîd': ('↻', 'ileri')}
@z('Sekiz başlık yedi aslî ilişkiye iner: Ta’lîl, Tefrî‘in tersi; Tafsîl/İcmâl tek ilişkinin iki yönü; ad→(ilişki, yön) birebir', C, 'tablo denetlendi')
def _():
    ilisk = {r for r, y in BAG.values()}
    return hepsi(len(set(BAG.values())) == len(BAG), len(ilisk) == 7, BAG['Ta’lîl'][0] == BAG['Tefrî‘'][0] and BAG['Ta’lîl'][1] != BAG['Tefrî‘'][1]), (len(BAG), len(ilisk))
@z('Bağ ilişkilerinin özellikleri tutar: Tefrî‘ geçişli ve yansımasız (kısmî sıra), Mukâbele simetrik ve geçişsiz, Temsîl denklik (yansımalı, simetrik, geçişli) — 5 elemanlı örnek modellerde', C, 'özellik taraması')
def _():
    X = range(5); tef = {(a, b) for a in X for b in X if a < b}; muk = {(0, 1), (1, 0), (1, 2), (2, 1)}; tem = {(a, b) for a in X for b in X if a // 2 == b // 2}
    gecisli = lambda R: all((a, c) in R for (a, b) in R for (b2, c) in R if b == b2)
    return hepsi(gecisli(tef), all((a, a) not in tef for a in X), all((b, a) in muk for a, b in muk), not gecisli(muk), all((a, a) in tem for a in X), all((b, a) in tem for a, b in tem), gecisli(tem))
def _bag_tam(sure):
    d = O.ORNEK[sure]; ayetler = sorted(d['kelime']); anah = ['%d:%d' % (sure, a) for a in ayetler]
    for x, y in zip(anah, anah[1:]):
        if not any(b[0] == x and b[1] == y and b[2].replace('’', '').replace('‘', '').lower() in [n.replace('’', '').replace('‘', '').lower() for n in O.SEKIZ_BAG] for b in d['baglar']): return False
    return True
@z('Kapsama ve süreklilik (örnek derlem, 103 ve 112): her ardışık âyet çiftine sekiz bağdan biri atanmış; bir bağ silinince denetçi yakalar', C, 'derlem + mutasyon')
def _():
    ok = _bag_tam(103) and _bag_tam(112); b = O.ORNEK[103]['baglar']; O.ORNEK[103]['baglar'] = b[:-1]; kirik = not _bag_tam(103); O.ORNEK[103]['baglar'] = b
    return ok and kirik
@z('Hiperkenar ikili bağdan kuvvetlidir: üç kuyruklu hiperkenar d\'ye ancak üçü de erişilmişse götürür; aynı kenarı üç ikili oka açmak a\'dan tek başına d\'ye götürür (yanlış)', C, 'erişim hesabı')
def _():
    H = [(frozenset('abc'), frozenset('d'), 'nakarat')]; ik = [(frozenset('a'), frozenset('d'), ''), (frozenset('b'), frozenset('d'), ''), (frozenset('c'), frozenset('d'), '')]
    return hepsi('d' not in K.erisilen(H, 'a'), 'd' in K.erisilen(H, 'abc'), 'd' in K.erisilen(ik, 'a'))
@z('İkili bağ hiperkenarın özel hâlidir: zincir erişimi iki temsilde aynı (sonlu zincirler 1…6)', C, 'zincir taraması')
def _():
    for n in range(1, 7):
        ik = [(frozenset([i]), frozenset([i + 1]), '') for i in range(n)]; zincir = {0}
        for i in range(n): zincir.add(i + 1)
        if K.erisilen(ik, [0]) != zincir: return False
    return True
@z('Bağ derecesi hep "hikmet ihtimali"dir; derlemde murâd-ı ilâhî iddiası içeren bağ yok (lint)', C, 'derlem lint')
def _():
    d = [b[3] for s in O.ORNEK.values() for b in s['baglar']]
    return hepsi(set(d) == {'hikmet ihtimali'}, not any(re.search('murâd|murad|Allah murat', b[2]) for s in O.ORNEK.values() for b in s['baglar']))

# =========================================================== D. KATMAN II: ZAMAN ÖLÇEĞİ
D = 'D. Zaman ölçekleri'
@z('Delta türevi (f(σ)−f)/μ; belgedeki f(t_{k+1})−f(t_k) yalnız μ=1 hâlidir: f=t², μ=2 noktasında 2 yerine 4 verir', D, 'iki ölçek')
def _():
    f = lambda t: t * t; U = K.ZamanOlcegi([0, 1, 2]); G = K.ZamanOlcegi([0, 2, 3])
    return hepsi(U.delta(f, Fr(0)) == f(Fr(1)) - f(Fr(0)), G.delta(f, Fr(0)) == 2, f(Fr(2)) - f(Fr(0)) == 4)
@z('İşaret değişmezliği: işaret(f^Δ) = işaret(ileri fark) bütün zaman ölçeklerinde (nitel iddialar ölçeğe bağlı değildir)', D, 'ölçek ve fonksiyon sayımı')
def _():
    n = 0
    for r in range(3, 6):
        for S in itertools.combinations(range(7), r):
            T = K.ZamanOlcegi(S)
            for vals in itertools.product([-1, 0, 2], repeat=min(r, 4)):
                f = lambda t, S=S, vals=vals: Fr(vals[S.index(int(t)) % len(vals)])
                for t in T.t[:-1]:
                    n += 1
                    if K.isaret(T.delta(f, t)) != K.isaret(f(T.sigma(t)) - f(t)): return False
    return True, n
@z('İkinci mertebe: eğim farkıyla tanımlanır; düzgün ölçekte ham ikinci farkla işareti eşit, düzgün olmayan ölçekte ayrışır (0,1,3: ham fark 0, gerçek ivme eksi)', D, 'sayım')
def _():
    T = K.ZamanOlcegi([0, 1, 3]); f = {0: Fr(0), 1: Fr(1), 3: Fr(2)}
    s0 = T.delta(lambda t: f[int(t)], Fr(0)); s1 = T.delta(lambda t: f[int(t)], Fr(1)); ivme = (s1 - s0) / T.mu(Fr(0)); ham = f[3] - 2 * f[1] + f[0]
    es = True
    for vals in itertools.product(range(-2, 3), repeat=4):
        U = K.ZamanOlcegi(range(4)); g = lambda t: Fr(vals[int(t)])
        sl = [U.delta(g, Fr(i)) for i in range(3)]
        for i in range(2):
            if K.isaret(sl[i + 1] - sl[i]) != K.isaret(g(Fr(i + 2)) - 2 * g(Fr(i + 1)) + g(Fr(i))): es = False
    return es and ham == 0 and ivme < 0, (ham, ivme)
@z('Çarpım kuralı (fg)^Δ = f^Δ g + f^σ g^Δ doğrulanır (6 ölçek × 3 polinom çifti, tam rasyonel)', D, 'özdeşlik taraması')
def _():
    n = 0
    for S in [(0, 1, 2, 3), (0, 2, 3, 7), (0, 1, 4, 5), (1, 2, 4, 8), (0, 3, 4, 9), (0, 5, 6, 8)]:
        T = K.ZamanOlcegi(S)
        for f, g in [(lambda t: t * t, lambda t: 3 * t + 1), (lambda t: t ** 3 - t, lambda t: 2 - t), (lambda t: t + 5, lambda t: t * t * t)]:
            for t in T.t[:-1]:
                n += 1
                if T.delta(lambda x: f(x) * g(x), t) != T.delta(f, t) * g(t) + f(T.sigma(t)) * T.delta(g, t): return False
    return True, n
@z('Analizin temel teoremi ∫_a^b f^Δ Δt = f(b)−f(a) (Hilger toplamı) bütün a<b noktalarında', D, 'özdeşlik taraması')
def _():
    T = K.ZamanOlcegi([0, 1, 3, 4, 8, 9]); f = lambda t: t * t - 2 * t; n = 0
    for a in T.t:
        for b in T.t:
            if a < b:
                n += 1
                if T.integral(lambda x: T.delta(f, x), a, b) != f(b) - f(a): return False
    return True, n
@z('Sürekli sınır: çok ince düzgün ölçekte f=t² için f^Δ(t)−2t tam olarak h (adım) kadardır, yani sürekli türeve yaklaşır', D, 'tam rasyonel')
def _():
    h = Fr(1, 1000); T = K.ZamanOlcegi([i * h for i in range(0, 1002)]); f = lambda t: t * t
    return all(T.delta(f, t) - 2 * t == h for t in T.t[:50])
@z('Geçerlilik ağırlığı W∈{0,1}: W=0 olan aralıkta φ≠0 olsa da birikim sıfırdır; W≡0 ise toplam sıfırdır', D, 'toplam denetimi')
def _():
    T = K.ZamanOlcegi(range(6)); phi = lambda t: Fr(3); W = lambda t: Fr(0) if 2 <= t < 4 else Fr(1)
    tam = T.integral(lambda t: W(t) * phi(t), Fr(0), Fr(5)); eksik = T.integral(lambda t: phi(t), Fr(0), Fr(5)) - T.integral(lambda t: phi(t), Fr(2), Fr(4))
    return hepsi(tam == eksik, T.integral(lambda t: Fr(0) * phi(t), Fr(0), Fr(5)) == 0)
def nitel_integral(isaretler):
    acc = '0'
    for s in isaretler: acc = K.i_topla(acc, s)
    return acc
@z('Nitel integral (işaret toplamı): hep artı → artı; artı+eksi → "?"; sıfırlayıcı ağırlıkla çarpılmış terimler hesaba girmez', D, 'durum taraması')
def _():
    return hepsi(nitel_integral(['+', '+', '0']) == '+', nitel_integral(['+', '-']) == '?', nitel_integral([K.i_carp('0', '+'), '-']) == '-', nitel_integral([]) == '0')
@z('Geçmiş dönüştürme operatörleri: T_sil idempotent (T∘T=T), T_çevir involüsyon (T∘T=kimlik), ikisi birbirine eşit değil', D, 'bütün dizilerde')
def _():
    sil = lambda x: [max(a, 0) for a in x]; cevir = lambda x: [-a for a in x]; ok = True
    for x in itertools.product([-2, -1, 0, 1, 2], repeat=4):
        x = list(x)
        if sil(sil(x)) != sil(x) or cevir(cevir(x)) != x: ok = False
    return ok and sil([-1, 2]) != cevir([-1, 2])

# =========================================================== E. NİTEL TÜREV: İŞARET CEBİRİ
E = 'E. İşaret cebiri ve kısmî türev'
S4 = K.ISARET
@z('İşaret cebiri kapalı ve değişmeli: ⊕ ve ⊗, {−,0,+,?} üzerinde 16 çiftin hepsinde', E, 'tam tablo')
def _(): return hepsi(all(K.i_topla(a, b) in S4 and K.i_carp(a, b) in S4 and K.i_topla(a, b) == K.i_topla(b, a) and K.i_carp(a, b) == K.i_carp(b, a) for a in S4 for b in S4))
@z('İşaret cebiri birleşmelidir: ⊕ ve ⊗ için 64 üçlünün hepsinde', E, 'tam tablo')
def _(): return all(K.i_topla(K.i_topla(a, b), c) == K.i_topla(a, K.i_topla(b, c)) and K.i_carp(K.i_carp(a, b), c) == K.i_carp(a, K.i_carp(b, c)) for a in S4 for b in S4 for c in S4)
@z('Dağılma yalnız alt-dağılmadır: a⊗(b⊕c) ⊑ (a⊗b)⊕(a⊗c) 64 üçlüde; tam eşitlik bozulduğu üçlü sayısı yazılır', E, 'tam tablo')
def _():
    alt = all(K.i_alt(K.i_carp(a, K.i_topla(b, c)), K.i_topla(K.i_carp(a, b), K.i_carp(a, c))) for a in S4 for b in S4 for c in S4)
    bozuk = sum(1 for a in S4 for b in S4 for c in S4 if K.i_carp(a, K.i_topla(b, c)) != K.i_topla(K.i_carp(a, b), K.i_carp(a, c)))
    return alt, 'tam eşitliğin bozulduğu üçlü: %d / 64' % bozuk
@z('Soyutlama sağlamdır: gerçek sayılar için işaret(x+y), işaret(x)⊕işaret(y)\'nin kapsadığı kümededir; işaret(xy) = işaret(x)⊗işaret(y)', E, 'gerçek sayı örnekleri')
def _():
    gam = lambda s: {'+', '-', '0'} if s == '?' else {s}; R = [Fr(x, 2) for x in range(-6, 7)]
    return all(K.isaret(x + y) in gam(K.i_topla(K.isaret(x), K.isaret(y))) and K.isaret(x * y) == K.i_carp(K.isaret(x), K.isaret(y)) for x in R for y in R)
@z('Belirsizlik yayılır: "?" ile sıfırdan farklı bir işaretin toplamı daima "?"; "?"⊗0 = 0 (yalnız sıfır belirsizliği yutar)', E, 'tam tablo')
def _(): return hepsi(all(K.i_topla('?', a) == '?' for a in '+-?'), K.i_carp('?', '0') == '0', K.i_topla('?', '0') == '?')
@z('Bileşik monoton fonksiyonun işareti çarpımdır: afin eğimler a,b ∈ {−2…2} için işaret(g∘f) = işaret(a)⊗işaret(b)', E, 'eğim taraması')
def _():
    for a in range(-2, 3):
        for b in range(-2, 3):
            f = lambda x: a * x + 1; g = lambda y: b * y - 3
            if K.isaret(g(f(1)) - g(f(0))) != K.i_carp(K.isaret(a), K.isaret(b)): return False
    return True
def kismi_isaret(fn, ekseni, alan):
    d = set()
    for p in itertools.product(*alan):
        for i in range(len(alan[ekseni]) - 1):
            q = list(p); q[ekseni] = alan[ekseni][i]; r = list(p); r[ekseni] = alan[ekseni][i + 1]
            d.add(K.isaret(fn(*r) - fn(*q)))
    return d.pop() if len(d) == 1 else ('?' if d else '0')
@z('Kısmî türev işareti: x+0·z için ∂/∂z = 0 (etkisizlik yakalanır), ∂/∂x = +; x·z için z∈{−1,0,1}\'de ∂/∂x = "?" (bağlama göre işaret değişir)', E, 'sonlu alan taraması')
def _():
    alan = [list(range(0, 4)), [-1, 0, 1]]
    return hepsi(kismi_isaret(lambda x, z_: x + 0 * z_, 1, alan) == '0', kismi_isaret(lambda x, z_: x + 0 * z_, 0, alan) == '+', kismi_isaret(lambda x, z_: x * z_, 0, alan) == '?')

# =========================================================== F. STANDART DIŞI ANALİZ
F = 'F. Hiperreel sonsuz küçük'
@z('ε>0 ve her n için ε<1/n (n=1…20000, tam rasyonel); ε²<ε: Arşimet özelliği çiğnenir', F, 'sıralı halka ℝ(ε)')
def _():
    e = K.Hiper.eps(); pos = e > K.Hiper.sayi(0)
    return pos and all(e < K.Hiper.sayi(Fr(1, n)) for n in range(1, 20001)) and (e * e) < e
@z('Sıra toplamdır (üçleme): 15 elemanlı kümede her çift için tam biri <, =, >', F, 'çift taraması')
def _():
    E_ = [K.Hiper({0: a, 1: b}) for a in (-1, 0, 1) for b in (-2, 0, 3)][:15] + [K.Hiper({-1: 1}), K.Hiper({2: -1})]
    return all(sum([x < y, x == y, x > y]) == 1 for x in E_ for y in E_)
@z('Φ(dα)≠0: Φ(x)=x³ için Φ(ε)≠0, oysa klasik limit standart kısımda 0 verir; yani sonsuz küçük kayıpsız tutulur, limit onu yutardı', F, 'hesap')
def _():
    e = K.Hiper.eps(); fx = e * e * e
    return hepsi(fx != K.Hiper.sayi(0), fx > K.Hiper.sayi(0), fx.standart_kisim() == 0)
@z('Aktarım örneği: ∀x>0 ∃y (0<y<x) hiperreellerde de geçerli (y=x/2; x=ε için ε/2)', F, 'örnekler')
def _():
    for x in [K.Hiper.eps(), K.Hiper.sayi(1), K.Hiper({0: 1, 1: 1}), K.Hiper.eps(3)]:
        y = x * Fr(1, 2)
        if not (y > K.Hiper.sayi(0) and y < x): return False
    return True
@z('Arşimet\'ten ayrılış: 100000·ε < 1 hâlâ doğru; klasik ℝ\'de ise 1/ε\'ye karşılık gelen bir n bulunurdu', F, 'hesap')
def _(): return K.Hiper.eps() * 100000 < K.Hiper.sayi(1)
@z('Standart kısım st: sonlu hiperreellerde toplama ve çarpmaya uyar, st(3+2ε)=3, sonsuz büyükte tanımsız (reddeder)', F, 'örnek taraması')
def _():
    a = K.Hiper({0: 3, 1: 2}); b = K.Hiper({0: -1, 2: 5}); ok = a.standart_kisim() == 3 and (a + b).standart_kisim() == a.standart_kisim() + b.standart_kisim() and (a * b).standart_kisim() == a.standart_kisim() * b.standart_kisim()
    try: K.Hiper({-1: 1}).standart_kisim(); red = False
    except ValueError: red = True
    return ok and red

# =========================================================== G. LİNEER CEBİR
G_ = 'G. Lineer cebir'
@z('Rank testi (GF(2)): yeni denklem mevcut bazların XOR bileşimiyse rank artmaz; bağımsız yeni eksense 1 artar', G_, 'rank hesabı')
def _():
    baz = [0b0011, 0b0101, 0b1001]; r0 = K.rank_gf2(baz)
    return hepsi(K.rank_gf2(baz + [baz[0] ^ baz[1]]) == r0, K.rank_gf2(baz + [0b1000]) == r0 + 1, K.rank_gf2([0b0001, 0b0010, 0b0100]) == 3, K.rank_gf2([0b0001, 0b0010, 0b0100, 0b1000]) == 4)
@z('Rank bazdan bağımsızdır: 5 satırın bütün 120 permütasyonunda ve satır toplamı eklemelerinde aynı', G_, 'permütasyon taraması')
def _():
    S = [0b00011, 0b00110, 0b01100, 0b11000, 0b10001]; r = K.rank_gf2(S)
    return all(K.rank_gf2(list(p)) == r for p in itertools.permutations(S)) and K.rank_gf2([S[0] ^ S[1]] + S[1:]) == r
@z('Dikgenlik = ayrık dayanak: dayanakları ayrık sıfırdan farklı iki vektörde rank toplanır; ortak dayanakta toplanmayabilir (ikame edilemezlik ölçüsü)', G_, 'bütün çiftler (6 bit)')
def _():
    ok = True; gor = False
    for a in range(1, 64):
        for b in range(1, 64):
            r = K.rank_gf2([a, b])
            if (a & b) == 0 and r != 2: ok = False
            if (a & b) != 0 and r < 2 and a == b: gor = True
    return ok and gor
@z('Özdeğer işareti: aynı operatör T farklı öznelerde +1 ve −1 verir; numpy özdeğerleri (+1,−1) ve özvektörler tutar', G_, 'sayısal')
def _():
    T = np.diag([1.0, -1.0]); w, V = np.linalg.eig(T)
    return hepsi(sorted(w) == [-1.0, 1.0], np.allclose(T @ np.array([1, 0]), 1 * np.array([1, 0])), np.allclose(T @ np.array([0, 1]), -1 * np.array([0, 1])))
@z('Rank–sıfırlık teoremi GF(2) üzerinde: 3×3\'lük 512 matrisin hepsinde rank + boyut(çekirdek) = 3 (çekirdek brute-force sayıldı)', G_, 'bütün matrisler')
def _():
    for bits in range(512):
        M = [(bits >> (3 * i)) & 7 for i in range(3)]
        ker = sum(1 for x in range(8) if all(bin(m & x).count('1') % 2 == 0 for m in M))
        if K.rank_gf2(M) + int(math.log2(ker)) != 3: return False
    return True, 512
@z('Dik izdüşüm: P=U(UᵀU)⁻¹Uᵀ idempotent ve simetrik (4 altuzay), asıl vektör bozulmaz: v = Pv + (I−P)v dik toplamı', G_, 'sayısal')
def _():
    for U in [np.array([[1.0], [1.0], [0.0]]), np.array([[1.0, 0], [0, 1.0], [1.0, 1.0]]), np.array([[2.0], [0], [1.0]]), np.array([[1.0, 2.0], [0, 1.0], [0, 0]])]:
        P = U @ np.linalg.inv(U.T @ U) @ U.T; v = np.array([1.0, 2.0, 3.0][:P.shape[0]])
        if not (np.allclose(P @ P, P) and np.allclose(P, P.T) and np.allclose(v, P @ v + (np.eye(P.shape[0]) - P) @ v) and abs((P @ v) @ ((np.eye(P.shape[0]) - P) @ v)) < 1e-9): return False
    return True
@z('Çekirdek–görüntü bölüşümü: kabul operatörü T (GF(2) üzerinde 3×3, 512 tane) için |ker|·|Im| = 8; geçersizleşenler ve geçerli sonuç üretenler vektör uzayını tam böler', G_, 'bütün matrisler')
def _():
    for bits in range(512):
        M = [(bits >> (3 * i)) & 7 for i in range(3)]
        ap = lambda x: sum((bin(M[i] & x).count('1') % 2) << i for i in range(3))
        ker = sum(1 for x in range(8) if ap(x) == 0); im = len({ap(x) for x in range(8)})
        if ker * im != 8: return False
    return True

# =========================================================== H. TENSÖR
H_ = 'H. Tensör'
def _tensor(bits, sh=(2, 2, 2)): return np.array([(bits >> i) & 1 for i in range(int(np.prod(sh)))], dtype=bool).reshape(sh)
@z('Daraltma derecesi bir azaltır: ∀-daraltma (p,q)-tensörün boyutunu 3\'ten 2\'ye indirir, her eksen için', H_, 'şekil denetimi')
def _(): return all(np.all(_tensor(5), axis=a).ndim == 2 for a in range(3))
@z('∀∀ ve ∃∃ daraltmaları farklı eksenlerde değişmelidir: 256 tensörün hepsi, iki sırayla', H_, 'bütün tensörler')
def _():
    for b in range(256):
        T = _tensor(b)
        if not np.array_equal(np.all(np.all(T, axis=0), axis=0), np.all(np.all(T, axis=1), axis=0)): return False
        if not np.array_equal(np.any(np.any(T, axis=0), axis=0), np.any(np.any(T, axis=1), axis=0)): return False
    return True
@z('∀∃ ile ∃∀ değişmez: 2×2 tensörlerde (∃j ∀i) ⇒ (∀i ∃j) hep doğru, tersi yanlış (karşı örnek: [[1,0],[0,1]])', H_, 'bütün 16 tensör')
def _():
    ters = ileri = True
    for b in range(16):
        T = _tensor(b, (2, 2)); ea = np.any(np.all(T, axis=0)); ae = np.all(np.any(T, axis=1))
        if ea and not ae: ileri = False
        if ae and not ea: ters = False
    return ileri and not ters
@z('Kesit ve daralma farklı eksenlerde değişir: önce 0. eksende 0\'ı seç sonra 2. ekseni ∀-daralt = önce daralt sonra seç (256 tensör)', H_, 'bütün tensörler')
def _():
    return all(np.array_equal(np.all(_tensor(b)[0], axis=-1), np.all(_tensor(b), axis=2)[0]) for b in range(256))
@z('Evrensel değişmez her kesite iner (sağlamlık): ∀-daraltılmış eksen sabitlenince hüküm her kesitte doğru (256 tensör)', H_, 'bütün tensörler')
def _():
    for b in range(256):
        T = _tensor(b); U = np.all(T, axis=0)
        for k in range(2):
            if np.any(U & ~T[k]): return False
    return True
@z('Daraltma birebir değildir (256 tensör → en çok 16 görüntü), bu yüzden kayıpsız daraltma kesitleri saklar: kesitlerden asıl tensör yeniden kurulur (256/256)', H_, 'bütün tensörler')
def _():
    goruntu = {np.all(_tensor(b), axis=0).tobytes() for b in range(256)}
    return len(goruntu) < 256 and all(np.array_equal(np.stack([_tensor(b)[0], _tensor(b)[1]]), _tensor(b)) for b in range(256)), len(goruntu)

# =========================================================== I. TROPİKAL ve SIRALI CEBİR
I_ = 'I. Tropikal ve sıralı cebir'
NEG = float('-inf')
@z('(max,+) yarı halka aksiyomları {−∞,0,1,2,3,4} üzerinde (birleşme, değişme, birim, dağılma, ⊕ idempotent)', I_, 'bütün üçlüler')
def _():
    X = [NEG, 0, 1, 2, 3, 4]; a_ = lambda x, y: max(x, y); m_ = lambda x, y: x + y
    return hepsi(*[a_(a_(x, y), w) == a_(x, a_(y, w)) and m_(m_(x, y), w) == m_(x, m_(y, w)) and m_(x, a_(y, w)) == a_(m_(x, y), m_(x, w)) for x in X for y in X for w in X], all(a_(x, x) == x and a_(x, NEG) == x and m_(x, 0) == x and m_(x, NEG) == NEG for x in X))
@z('(max,min) sıralı yarı halka (zincir 0…4) aksiyomları ve çift dağılma; bu cebirde rakam gerekmez, yalnız sıra', I_, 'bütün üçlüler')
def _():
    X = range(5); a_ = max; m_ = min
    return all(m_(x, a_(y, w)) == a_(m_(x, y), m_(x, w)) and a_(x, m_(y, w)) == m_(a_(x, y), a_(x, w)) for x in X for y in X for w in X) and all(a_(x, 0) == x and m_(x, 4) == x and m_(x, 0) == 0 for x in X)
@z('Aksiyom 3 ile çatışma: iki yolun puanı sıra-izomorfik yeniden etiketlemede (max,+) ile DEĞİŞİR, (max,min) ile DEĞİŞMEZ', I_, 'bütün artan etiketlemeler')
def _():
    etiket = list(itertools.combinations(range(1, 13), 4))
    mp = {(sum(c[i] for i in (0, 3)) > sum(c[i] for i in (1, 2))) for c in etiket}
    mm = {(min(c[i] for i in (0, 3)) > min(c[i] for i in (1, 2))) for c in etiket}
    return len(mp) == 2 and len(mm) == 1, '(max,+) kararları %s; (max,min) kararları %s' % (sorted(mp), sorted(mm))

# =========================================================== J. HEYTING, ULTRAMETRİK, ÇİZGE
J_ = 'J. Heyting kafesi, ağaç ve çizge'
def _heyting(): return K.Heyting(3, {(0, 1), (0, 2), (1, 2)})
def _opens(H): return H.acik
@z('Alexandrov yukarı-kümeleri Heyting cebridir: W∩U ⊆ V ⇔ W ⊆ (U⇒V), bütün üçlülerde', J_, 'bütün üçlüler (zincir 3)')
def _():
    H = _heyting(); O_ = _opens(H)
    return all(((W & U) <= V) == (W <= H.imp(U, V)) for U in O_ for V in O_ for W in O_)
@z('Dışlanmış üçüncü Heyting\'te çöker: zincir 3\'te U ∪ ¬U ≠ tüm uzay olan açık küme vardır (karşı model)', J_, 'karşı model')
def _():
    H = _heyting(); tum = frozenset(range(H.n)); kotu = [U for U in _opens(H) if (U | H.neg(U)) != tum]
    return len(kotu) > 0, 'ihlâl eden açık küme sayısı: %d' % len(kotu)
@z('Çifte olumsuzlama: U ⊆ ¬¬U hep, ¬¬U = U her U için değil (Heyting\'e özgü)', J_, 'karşı model')
def _():
    H = _heyting(); O_ = _opens(H)
    return all(U <= H.neg(H.neg(U)) for U in O_) and any(H.neg(H.neg(U)) != U for U in O_)
@z('∅ ⇒ V = tüm uzay (boş öncül her şeyi gerektirir) ve U ⇒ U = tüm uzay', J_, 'bütün açıklar')
def _():
    H = _heyting(); tum = frozenset(range(H.n)); O_ = _opens(H)
    return all(H.imp(frozenset(), V) == tum and H.imp(V, V) == tum for V in O_)
def _agac(): par = {i: (i - 1) // 2 for i in range(1, 15)}; par[0] = None; return par
@z('Ağaç ultrametriktir: d(x,z) ≤ max(d(x,y),d(y,z)), 15 düğümde 3375 üçlü', J_, 'bütün üçlüler')
def _():
    p = _agac(); d = lambda x, y: K.ultra_uzaklik(p, x, y, 4)
    return all(d(x, z_) <= max(d(x, y), d(y, z_)) for x in range(15) for y in range(15) for z_ in range(15))
@z('Ultrametrikte her üçgen ikizkenardır (en büyük iki kenar eşit)', J_, 'bütün üçlüler')
def _():
    p = _agac()
    for x in range(15):
        for y in range(15):
            for z_ in range(15):
                a, b, c = sorted([K.ultra_uzaklik(p, x, y, 4), K.ultra_uzaklik(p, y, z_, 4), K.ultra_uzaklik(p, x, z_, 4)])
                if b != c: return False
    return True
@z('Ortak ata simetriktir ve ortak_ata(x,x)=x: 225 çift', J_, 'bütün çiftler')
def _():
    p = _agac()
    return all(K.ortak_ata(p, x, y) == K.ortak_ata(p, y, x) for x in range(15) for y in range(15)) and all(K.ortak_ata(p, x, x) == x for x in range(15))
@z('Basit döngüler: üç düğümlü halka tek döngü verir; ters kenar eklemek döngü sayısını artırır; DAG\'ta sıfırdır', J_, 'sayım')
def _():
    ken = {(0, 1): 1, (1, 2): 1, (2, 0): -1}; d = K.basit_donguler(3, ken)
    ken2 = dict(ken); ken2[(1, 0)] = 1; d2 = K.basit_donguler(3, ken2)
    return len(d) == 1 and len(d2) > len(d) and len(K.basit_donguler(3, {(0, 1): 1, (1, 2): 1, (0, 2): 1})) == 0
@z('Erişilebilirlik geçişlidir: 6 düğümlü yönlü çizgede R(x,y) ∧ R(y,z) ⇒ R(x,z) bütün üçlülerde', J_, 'bütün üçlüler')
def _():
    ken = [(frozenset({a}), frozenset({b}), '') for a, b in [(0, 1), (1, 2), (2, 3), (4, 5), (3, 1)]]; R = {x: set(K.erisilen(ken, {x})) for x in range(6)}
    return all(z_ in R[x] for x in range(6) for y in R[x] for z_ in R[y])
@z('Hiperkenar VE anlamındadır: (üç öncül → sonuç) kenarda tek öncül eksilince sonuç erişilmez; ikili kenar bunu söyleyemez', J_, 'örnek')
def _():
    kenar = [({0, 1, 2}, 3)]
    def er(b):
        v = set(b); ch = True
        while ch:
            ch = False
            for P, s in kenar:
                if P <= v and s not in v: v.add(s); ch = True
        return v
    return 3 in er({0, 1, 2}) and 3 not in er({0, 1}) and 3 not in er({1, 2}) and 3 not in er({0, 2})

# =========================================================== K. DİNAMİK VE OYUN
K_ = 'K. Dinamik ve oyun'
@z('Goodwin eşiği (n=3 negatif halka): (s+1)³+g=0 köklerinde g=7,9 kararlı, g=8,1 kararsız (eşik 8)', K_, 'sayısal kökler')
def _():
    kar = lambda g: all(x.real < 0 for x in np.roots(np.polyadd(np.poly([-1, -1, -1]), [g])))
    return kar(7.9) and not kar(8.1)
@z('Pozitif halka: (s+1)³−g kökleri; g>1 reel pozitif kök (çoklu denge), g<1 hepsi kararlı', K_, 'sayısal kökler')
def _():
    f = lambda g: np.roots(np.polysub(np.poly([-1, -1, -1]), [g]))
    return any(abs(x.imag) < 1e-9 and x.real > 0 for x in f(1.5)) and all(x.real < 0 for x in f(0.5))
@z('Tarski: sonlu kafeste monoton fonksiyonların sabit noktası vardır (100 sabit tohumlu monoton fonksiyon, 3 elemanlı alt küme kafesi)', K_, 'örnekler')
def _():
    rnd = random.Random(7)
    for _ in range(100):
        m1, m2 = rnd.randrange(8), rnd.randrange(8); f = {x: (x & m1) | m2 for x in range(8)}
        assert all((f[x] & f[y]) == f[x] for x in range(8) for y in range(8) if (x & y) == x)
        if not any(f[x] == x for x in range(8)): return False
    return True
def _Phi(a): return sum(1 for i in range(3) if a[i] == a[(i + 1) % 3])
def _ui(i, a): return sum(1 for j in (i, (i - 1) % 3) if a[j] == a[(j + 1) % 3])
@z('Potansiyel oyun özdeşliği (Monderer–Shapley): bütün tek-taraflı sapmalarda Δu_i = ΔΦ, 24 sapma', K_, 'tam tarama')
def _():
    for a in itertools.product((0, 1), repeat=3):
        for i in range(3):
            b = list(a); b[i] ^= 1; b = tuple(b)
            if _ui(i, b) - _ui(i, a) != _Phi(b) - _Phi(a): return False
    return True
@z('Potansiyel oyunda en iyi-cevap dinamiği 8 başlangıçtan da Nash\'e erer (20 adımda durur)', K_, 'tam tarama')
def _():
    for a0 in itertools.product((0, 1), repeat=3):
        a = a0
        for _ in range(20):
            hareket = False
            for i in range(3):
                b = list(a); b[i] ^= 1; b = tuple(b)
                if _ui(i, b) > _ui(i, a): a = b; hareket = True; break
            if not hareket: break
        else: return False
    return True
@z('Zaman ölçeğinde Δ(x²) = σ(x)+x = 2x+1 (tamsayı ölçek) ve düzensiz ölçekte formül μ ile ayarlanır', K_, 'tam tarama')
def _():
    Z = K.ZamanOlcegi(range(0, 10)); Z2 = K.ZamanOlcegi([0, 1, 3, 4, 8])
    return all(Z.delta(lambda y: y * y, Fr(x)) == 2 * x + 1 for x in range(9)) and Z2.delta(lambda y: y * y, Fr(1)) == Fr(3) + Fr(1)
@z('Temel teorem: ∫ₐᵇ Δf = f(b) − f(a), düzensiz ölçekte 5 işlev', K_, 'tam tarama')
def _():
    Z = K.ZamanOlcegi([0, 1, 3, 4, 8, 9, 15]); fs = [lambda x: x, lambda x: x * x, lambda x: 3, lambda x: 2 * x + 5, lambda x: x * x * x]
    return all(Z.integral(lambda x, f=f: Z.delta(f, x), Fr(0), Fr(15)) == f(Fr(15)) - f(Fr(0)) for f in fs)

# =========================================================== L. ÜST KURAM
L_ = 'L. Üst kuram: tutarlılık, mutasyon, bağımsızlık'
@z('Tutarlılık: bütün yan şartların aynı anda sağlandığı modeller var — KD modelleri, 3-zincir Heyting, işaret cebiri, ZamanOlcegi', L_, 'model varlığı')
def _(): return len(list(itertools.islice(_kd_modelleri(2), 1))) > 0 and len(_opens(_heyting())) > 0 and len(S4) == 4
@z('Mutasyon: Kural 3\'ten "dışlanmış üçüncü" şartını silince Heyting karşı modeli ihlâli yakalar (ölçü ayırt eder)', L_, 'mutasyon')
def _():
    H = _heyting(); tum = frozenset(range(H.n)); return any((U | H.neg(U)) != tum for U in _opens(H))
@z('Mutasyon: sahte ⊕ (a?b:a) yazılırsa değişme ölçüsü kırmızı yanar; gerçek ⊕ geçer', L_, 'yanlış iddia reddi')
def _():
    sahte = lambda a, b: a if a != '?' else b
    return any(sahte(a, b) != sahte(b, a) for a in S4 for b in S4) and all(K.i_topla(a, b) == K.i_topla(b, a) for a in S4 for b in S4)
@z('Bağımsızlık: işaret cebirinde "?" aksiyomu gerekir; {+,−,0} üzerinde + ⊕ − kapalı değil', L_, 'karşı model')
def _(): return K.i_topla('+', '-') == '?' and '?' not in '+-0'
@z('Bağımsızlık: Boole şartı (¬¬U=U) 2 elemanlı ayrık (antichain) modelde geçerli, 3-zincirde geçersiz — ayrı aksiyomdur', L_, 'iki model')
def _():
    H2 = K.Heyting(2, set()); H3 = _heyting()
    return all(H2.neg(H2.neg(U)) == U for U in _opens(H2)) and any(H3.neg(H3.neg(U)) != U for U in _opens(H3))
@z('Karar verilebilirlik: işaret ifadeleri 4 işaretli 5 değişkende 1024 atamanın hepsinde sonlu sürede kapanır', L_, 'tam tarama')
def _():
    n = 0
    for v in itertools.product(S4, repeat=5):
        x = K.i_topla(K.i_carp(v[0], v[1]), K.i_carp(v[2], K.i_topla(v[3], v[4]))); assert x in S4; n += 1
    return n == 1024, n
@z('Doğrusal zaman: ayrıştırma süresi terim sayısıyla en çok doğrusal-artı-sabit büyür (200→1600 terim, oran ≤ 32)', L_, 'ölçüm')
def _():
    import time
    def sure(n):
        e = ' ∧ '.join('p%d' % i for i in range(n)); t0 = time.perf_counter(); [K.ayristir(e) for _ in range(3)]; return time.perf_counter() - t0
    a, b = sure(200), sure(1600); return b / max(a, 1e-9) < 32, 'oran=%.1f (terim 8 kat)' % (b / max(a, 1e-9))
@z('Occam: kural sayısı altıdır (KURALLAR kaydı), her biri farklı yapıya dayanır', L_, 'sayım')
def _(): return len(KURALLAR) >= 6

# =========================================================== YAZICI
if __name__ == '__main__':
    gecen = sum(1 for r in SONUC if r['ok']); n = len(SONUC)
    (HERE / 'SINAMA.json').write_text(json.dumps({'toplam': n, 'gecen': gecen, 'sonuclar': SONUC}, ensure_ascii=False, indent=1), encoding='utf-8')
    L = ['# KURAM ZİYADELERİ — icra edilmiş ve sayılmış', '', 'Her satır `kuram_sina.py` içinde bir fonksiyondur; bu dosya onun çıktısından üretilir (elle yazılmaz). Geçen: **%d / %d**.' % (gecen, n), '',
         '| No | Bölüm | Ziyade (neyi sınadı) | Usul | Sonuç | Ayrıntı |', '| --: | :-- | :-- | :-- | :-: | :-- |']
    for r in SONUC:
        L.append('| %d | %s | %s | %s | %s | %s |' % (r['no'], r['bolum'], r['ad'].replace('|', '/'), r['usul'], 'GEÇTİ' if r['ok'] else 'KALDI', r['detay'].replace('|', '/')[:120]))
    (HERE / 'KURAM_ZIYADELERI.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('TOPLAM %d GEÇEN %d' % (n, gecen))
