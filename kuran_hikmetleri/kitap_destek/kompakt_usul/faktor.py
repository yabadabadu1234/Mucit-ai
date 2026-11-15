"""Ikili matris çarpanlaması (formal kavramlarla, GreConD usulü): kelime x mana tablosunu en az sayıda
'dikdörtgen' (kavram) ile örter. Her dikdörtgen = bu kelimeler bu manaların hepsini taşır."""
import sys, json, math, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / 'kafes_ornek'))
import kafes3_kafes as K
HERE = pathlib.Path(__file__).resolve().parent
G, M = list(K.KELIME), list(K.MANA)
I = {(g, m) for g in G for m in M if m in K.KELIME[g]['anlam']}
def ext(B): return frozenset(g for g in G if all((g, m) in I for m in B))
def itn(A): return frozenset(m for m in M if all((g, m) in I for g in A))
U = set(I); F = []
while U:
    D = frozenset(); best = 0
    while True:
        cand = None
        for j in M:
            if j in D: continue
            A = ext(D | {j}); B = itn(A)
            v = sum(1 for g in A for m in B if (g, m) in U)
            if v > best: best, cand = v, (A, B)
        if cand is None: break
        A, D = cand
    A = ext(D); B = itn(A)
    F.append((A, B)); U -= {(g, m) for g in A for m in B}
# ölçüler (bit)
bit_hucre = math.log2(len(G) * len(M))
ham = len(I) * bit_hucre                      # her 1 hücresini (satır, sütun) diye yazmak
faktorlu = sum((len(A) * math.log2(len(G)) + len(B) * math.log2(len(M))) for A, B in F)
duz = len(G) * len(M)                          # bütün tabloyu bit bit yazmak
r = dict(kelime=len(G), mana=len(M), bir_sayisi=len(I), faktor=len(F),
         bit_tam_tablo=duz, bit_hucre_listesi=round(ham), bit_faktorlu=round(faktorlu),
         sikistirma_hucre_listesine_gore=round(ham / faktorlu, 2),
         faktorler=[dict(kelimeler=[K.KELIME[g]['ar'] for g in A], manalar=[K.MANA[m]['metin'] for m in B]) for A, B in F])
json.dump(r, open(HERE / 'faktor_rapor.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print({k: v for k, v in r.items() if k != 'faktorler'})
for f in r['faktorler']: print(len(f['kelimeler']), 'kelime ×', f['manalar'])
