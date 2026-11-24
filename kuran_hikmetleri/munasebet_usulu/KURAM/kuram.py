"""Kayıpsız Katlama Kuramı -- icra edilebilir çekirdek (dil, cebirler, katlama, modeller).
Bu dosya KURAM.md'deki her teoremin sonlu modelde koşan karşılığıdır; kuram_sina.py bunları ziyade ziyade sınar."""
import re, itertools, collections, math
from fractions import Fraction

# ===================================================================== 1. DİL
IKILI = {  # sembol: (bağlama gücü, çağrışım)  -- F: Bölüm 3.7 öncelik sırası (yüksekten düşüğe)
    '::': (90, 'L'),
    '∈': (60, 'L'), '⊂': (60, 'L'), '∖': (60, 'L'), '⊑': (60, 'L'), '≺': (60, 'L'), '↦!': (60, 'L'), '↦': (60, 'L'), '≅': (60, 'L'), '≇': (60, 'L'),
    '∧': (40, 'L'), '∨': (35, 'L'), '⊻': (35, 'L'), '→': (30, 'R'), '□→': (25, 'R'), '↔': (20, 'L'),
    '∵': (10, 'L'), '⇝': (10, 'L'), '▷': (10, 'L'), '⊢': (10, 'L'), '⇒': (10, 'L'), '⋈': (10, 'L'), '⤏': (10, 'L'), ':=': (10, 'L'), '≡': (10, 'L'),
}
TEKLI = {'¬', '□', '◇'}
NICELEYICI = {'∀': 'hepsi', '∃': 'en az bir', '∃!': 'tek', '∄': 'hiçbiri'}
_SEMBOLLER = sorted(set(list(IKILI) + list(TEKLI) + list(NICELEYICI)), key=lambda s: -len(s))
_KIMLIK = r"(?:[^\W_]|[⟐↑?])[\w'’⁺⁻₀₋₊_!⊥⊤]*|_\w+"
_TOK = re.compile(r'\s*(?:(%s)|(%s)|([()\[\]{}⟨⟩,|.]))' % (_KIMLIK, '|'.join(re.escape(s) for s in _SEMBOLLER)))

def tokenle(s):
    out, i = [], 0
    s = s.strip()
    while i < len(s):
        m = _TOK.match(s, i)
        if not m or m.end() == i: raise SyntaxError('tanınmayan simge: %r' % s[i:i + 12])
        out.append(m.group(1) or m.group(2) or m.group(3)); i = m.end()
        while i < len(s) and s[i].isspace(): i += 1
    return out

class Ayrac:
    def __init__(self, t): self.t = t; self.i = 0
    def bak(self): return self.t[self.i] if self.i < len(self.t) else None
    def al(self, x=None):
        v = self.bak()
        if v is None or (x is not None and v != x): raise SyntaxError('beklenen %r, görülen %r' % (x, v))
        self.i += 1; return v
    def ifade(self, asgari=0, durak=()):
        sol = self.tekli(durak)
        while True:
            op = self.bak()
            if op is None or op in durak or op not in IKILI: break
            g, c = IKILI[op]
            if g < asgari: break
            self.al(); sag = self.ifade(g + 1 if c == 'L' else g, durak); sol = ('bin', op, sol, sag)
        return sol
    def tekli(self, durak=()):
        v = self.bak()
        if v in TEKLI: self.al(); return ('un', v, self.tekli(durak))
        if v in NICELEYICI:
            self.al(); ad = self.al(); alan = None
            if self.bak() == '∈': self.al(); alan = self.al()
            self.al('.'); return ('q', v, ad, alan, self.ifade(0, durak))
        return self.sonek(self.asal(durak))
    def asal(self, durak):
        v = self.bak()
        if v == '(': self.al(); e = self.ifade(0, ()); self.al(')'); return e
        if v == '⟨': self.al(); e = self.ifade(0, ('⟩',)); self.al('⟩'); return ('ima', e)
        if v is None or not re.match(_KIMLIK, v): raise SyntaxError('ifade bekleniyordu, görülen %r' % v)
        self.al()
        if self.bak() == '(':
            self.al('('); args, ayr = [], ','
            if self.bak() != ')':
                while True:
                    args.append(self.ifade(0, (',', '|', ')')))
                    if self.bak() in (',', '|'): ayr = self.al()
                    else: break
            self.al(')'); return ('app', v, tuple(args), ayr)
        return ('var', v)
    def sonek(self, e):
        while self.bak() in ('[', '{'):
            if self.bak() == '[': self.al(); m = self.al(); self.al(']'); e = ('ref', e, m)
            else:
                self.al(); it = [self.ifade(0, (',', '}'))]
                while self.bak() == ',': self.al(); it.append(self.ifade(0, (',', '}')))
                self.al('}'); e = ('nit', e, tuple(it))
        return e

def ayristir(s):
    a = Ayrac(tokenle(s)); e = a.ifade()
    if a.bak() is not None: raise SyntaxError('artan simge: %r' % a.bak())
    return e

def yaz(e, ust=0):
    t = e[0]
    if t == 'var': return e[1]
    if t == 'app': return '%s(%s)' % (e[1], (' %s ' % e[3] if e[3] == '|' else ', ').join(yaz(a) for a in e[2]))
    if t == 'un': return e[1] + yaz(e[2], 100)
    if t == 'ima': return '⟨' + yaz(e[1]) + '⟩'
    if t == 'ref': return yaz(e[1], 100) + '[' + e[2] + ']'
    if t == 'nit': return yaz(e[1], 100) + '{' + ', '.join(yaz(x) for x in e[2]) + '}'
    if t == 'q': return e[1] + e[2] + ('∈' + e[3] if e[3] else '') + '.' + yaz(e[4])
    g, c = IKILI[e[1]]
    s = '%s %s %s' % (yaz(e[2], g + (0 if c == 'R' else 0.5)), e[1], yaz(e[3], g + (0.5 if c == 'R' else 0)))
    s = '%s %s %s' % (yaz(e[2], g if c == 'L' else g + 1), e[1], yaz(e[3], g + 1 if c == 'L' else g))
    return '(%s)' % s if g < ust else s

def tam_parantez(e):
    t = e[0]
    if t == 'var': return e[1]
    if t == 'app': return '%s[%s]' % (e[1], e[3].join(tam_parantez(a) for a in e[2]))
    if t == 'un': return '(%s %s)' % (e[1], tam_parantez(e[2]))
    if t == 'ima': return '<%s>' % tam_parantez(e[1])
    if t == 'ref': return '%s@%s' % (tam_parantez(e[1]), e[2])
    if t == 'nit': return '%s{%s}' % (tam_parantez(e[1]), ';'.join(tam_parantez(x) for x in e[2]))
    if t == 'q': return '(%s %s %s %s)' % (e[1], e[2], e[3], tam_parantez(e[4]))
    return '(%s %s %s)' % (tam_parantez(e[2]), e[1], tam_parantez(e[3]))

def degiskenler(e, acc=None):
    acc = set() if acc is None else acc
    t = e[0]
    if t == 'var': acc.add(e[1])
    elif t == 'app': [degiskenler(a, acc) for a in e[2]]
    elif t in ('un', 'ima'): degiskenler(e[-1] if t == 'un' else e[1], acc)
    elif t == 'ref': degiskenler(e[1], acc)
    elif t == 'nit': degiskenler(e[1], acc); [degiskenler(x, acc) for x in e[2]]
    elif t == 'q': degiskenler(e[4], acc)
    else: degiskenler(e[2], acc); degiskenler(e[3], acc)
    return acc

def olc(e, v):
    """Yalnız önermesel çekirdek: v = {ad: bool}"""
    t = e[0]
    if t == 'var': return v[e[1]]
    if t == 'un' and e[1] == '¬': return not olc(e[2], v)
    if t == 'bin':
        a, b = olc(e[2], v), olc(e[3], v)
        return {'∧': a and b, '∨': a or b, '⊻': a != b, '→': (not a) or b, '↔': a == b}[e[1]]
    raise ValueError('önermesel çekirdek dışı: ' + t)

# ===================================================================== 2. İŞARET CEBİRİ (nitel türev)
ISARET = ('-', '0', '+', '?')
def i_topla(a, b):
    if a == '0': return b
    if b == '0': return a
    if a == b and a in '+-': return a
    return '?'
def i_carp(a, b):
    if a == '0' or b == '0': return '0'
    if a == '?' or b == '?': return '?'
    return '+' if a == b else '-'
def i_ters(a): return {'+': '-', '-': '+', '0': '0', '?': '?'}[a]
def i_alt(x, y): return y == '?' or x == y             # x ⊑ y : x, y'den daha kesin
def isaret(x): return '+' if x > 0 else ('-' if x < 0 else '0')

# ===================================================================== 3. ZAMAN ÖLÇEĞİ
class ZamanOlcegi:
    def __init__(self, noktalar): self.t = sorted(Fraction(x) for x in noktalar)
    def sigma(self, x): i = self.t.index(x); return self.t[i + 1] if i + 1 < len(self.t) else x
    def mu(self, x): return self.sigma(x) - x
    def delta(self, f, x):
        m = self.mu(x)
        if m == 0: raise ValueError('sağ yoğun/son nokta: delta türevi tanımsız')
        return (f(self.sigma(x)) - f(x)) / m
    def integral(self, f, a, b): return sum((f(x) * self.mu(x) for x in self.t if a <= x < b), Fraction(0))

# ===================================================================== 4. HİPERREEL HALKA ℝ(ε) (ε > 0 sonsuz küçük)
class Hiper:
    """Σ a_k ε^k, k ∈ ℤ, sonlu; işareti en düşük kuvvetli sıfırdan farklı katsayı belirler (ε → 0⁺)."""
    def __init__(self, d=None):
        self.d = {k: Fraction(v) for k, v in (d or {}).items() if v != 0}
    @staticmethod
    def sayi(x): return Hiper({0: x})
    @staticmethod
    def eps(k=1): return Hiper({k: 1})
    def __add__(s, o):
        o = o if isinstance(o, Hiper) else Hiper.sayi(o); r = dict(s.d)
        for k, v in o.d.items(): r[k] = r.get(k, 0) + v
        return Hiper(r)
    __radd__ = __add__
    def __neg__(s): return Hiper({k: -v for k, v in s.d.items()})
    def __sub__(s, o): return s + (-(o if isinstance(o, Hiper) else Hiper.sayi(o)))
    def __mul__(s, o):
        o = o if isinstance(o, Hiper) else Hiper.sayi(o); r = {}
        for a, u in s.d.items():
            for b, v in o.d.items(): r[a + b] = r.get(a + b, 0) + u * v
        return Hiper(r)
    __rmul__ = __mul__
    def isaret(s):
        if not s.d: return 0
        k = min(s.d); return 1 if s.d[k] > 0 else -1
    def __lt__(s, o): return (s - o).isaret() < 0
    def __gt__(s, o): return (s - o).isaret() > 0
    def __eq__(s, o): return (s - o).isaret() == 0
    def __hash__(s): return hash(tuple(sorted(s.d.items())))
    def sonlu(s): return not s.d or min(s.d) >= 0
    def standart_kisim(s):
        if not s.sonlu(): raise ValueError('sonsuz büyük')
        return s.d.get(0, Fraction(0))

# ===================================================================== 5. HEYTING CEBRİ (sonlu posetin üst kümeleri)
class Heyting:
    def __init__(self, n, ust_ise):          # ust_ise: {(a,b)} a ≤ b
        self.n = n; self.le = set(ust_ise) | {(i, i) for i in range(n)}
        ch = True
        while ch:
            ch = False
            for (a, b) in list(self.le):
                for (c, d) in list(self.le):
                    if b == c and (a, d) not in self.le: self.le.add((a, d)); ch = True
        self.acik = [frozenset(s) for r in range(n + 1) for s in itertools.combinations(range(n), r) if all(y in s for x in s for y in range(n) if (x, y) in self.le)]
    def imp(self, U, V): return frozenset(x for x in range(self.n) if all((y not in U) or (y in V) for y in range(self.n) if (x, y) in self.le))
    def neg(self, U): return self.imp(U, frozenset())

# ===================================================================== 6. ULTRAMETRİK AĞAÇ
def agac_ata(parent, x):
    yol = [x]
    while parent[yol[-1]] is not None: yol.append(parent[yol[-1]])
    return yol
def derinlik(parent, x): return len(agac_ata(parent, x)) - 1
def ortak_ata(parent, x, y):
    a = set(agac_ata(parent, x))
    for z in agac_ata(parent, y):
        if z in a: return z
def ultra_uzaklik(parent, x, y, D):
    return 0 if x == y else D - derinlik(parent, ortak_ata(parent, x, y))
def kanonik(children, n):
    return tuple(sorted(kanonik(children, c) for c in children.get(n, ())))

# ===================================================================== 7. GF(2) RANK ve diğer lineer cebir
def rank_gf2(satirlar):
    taban = []
    for v in satirlar:
        for b in taban: v = min(v, v ^ b)
        if v: taban.append(v)
    return len(taban)

# ===================================================================== 8. ŞEKİL: SIGNED DİGRAF DÖNGÜLERİ
def basit_donguler(n, kenar):                     # kenar: {(i,j): +1/-1}
    sonuc = set()
    def git(bas, cur, yol):
        for (a, b), s in kenar.items():
            if a != cur: continue
            if b == bas: sonuc.add(tuple(_dondur(yol)))
            elif b not in yol and b > bas: git(bas, b, yol + [b])
    for bas in range(n): git(bas, bas, [bas])
    return sorted(sonuc)
def _dondur(y): return y
def dongu_kutbu(kenar, dongu):
    p = 1
    for i, a in enumerate(dongu): p *= kenar[(a, dongu[(i + 1) % len(dongu)])]
    return p

# ===================================================================== 9. HİPERGRAF
def erisilen(kenarlar, kaynak):
    """B-bağlantı: bir hiperkenar, bütün kuyrukları erişilmişse başlarını erişilmiş yapar."""
    e = set(kaynak); ch = True
    while ch:
        ch = False
        for kuyruk, bas, _ in kenarlar:
            if kuyruk <= e and not bas <= e: e |= bas; ch = True
    return e

# ===================================================================== 10. KATLAMA CEBİRİ (iz taşıyan terimler)
class Atom:
    def __init__(self, ad, bicim, kaynak): self.ad, self.bicim, self.kaynak = ad, bicim, kaynak
    def __repr__(self): return 'Atom(%s)' % self.ad
    def __eq__(s, o): return isinstance(o, Atom) and (s.ad, s.bicim, s.kaynak) == (o.ad, o.bicim, o.kaynak)
    def __hash__(s): return hash((s.ad, s.bicim, s.kaynak))
class Katla:
    def __init__(self, kural, kalan, cocuklar, sahit=()): self.kural, self.kalan, self.cocuklar, self.sahit = kural, kalan, tuple(cocuklar), tuple(sahit)
    def __repr__(self): return 'Katla(%s,%s)' % (self.kural, list(self.cocuklar))
def ac(t):
    if isinstance(t, Atom): return [t]
    out = []
    for c in t.cocuklar: out += ac(c)
    return out
def derinlik_k(t): return 0 if isinstance(t, Atom) else 1 + max(derinlik_k(c) for c in t.cocuklar)
def boyut(t): return 1 if isinstance(t, Atom) else 1 + sum(boyut(c) for c in t.cocuklar)
def imza(t):
    return ('A', t.ad) if isinstance(t, Atom) else ('K', t.kural, t.kalan, tuple(imza(c) for c in t.cocuklar))
def kayipsizmi(t, kapsanan):
    return collections.Counter(a.ad for a in ac(t)) == collections.Counter(kapsanan)

# ===================================================================== 11. ÖRTÜK YAPILAR: İSTİSNA, HASR, AHKAM
def istisna_turu(A, B):
    A, B = set(A), set(B)
    if not B: return 'bos'
    if B <= A: return 'muttasil'
    if not (A & B): return 'munkati'
    return 'karma'
def hasr(R, X, Y): return set(R.get(X, ())) == {Y}
def aidiyet(R, X, Y): return Y in R.get(X, ())
def ahkam(izin_yap, izin_terk, tercih):
    """tercih: 'yap' | 'terk' | 'esit'"""
    if not izin_yap and not izin_terk: raise ValueError('D aksiyomu ihlâli')
    if not izin_yap: return 'haram'
    if not izin_terk: return 'farz'
    return {'yap': 'mendup', 'terk': 'mekruh', 'esit': 'mubah'}[tercih]

# Emir/ruhsat: öncelikli (defeasible) normlar
def norm_durumu(normlar, ctx):
    """normlar: [(öncelik, şart(ctx)->bool, hüküm)]; ctx'te geçerli en yüksek öncelikli hüküm. Eşit öncelikte çelişki -> None."""
    uygun = [(p, h) for p, s, h in normlar if s(ctx)]
    if not uygun: return 'tanimsiz'
    top = max(p for p, h in uygun); H = {h for p, h in uygun if p == top}
    return H.pop() if len(H) == 1 else None
