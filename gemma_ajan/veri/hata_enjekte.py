"""Gerçek depoda otomatik hata enjeksiyonu: AST mutasyonu + mevcut testlerle öldürme denetimi.
Kullanım: python3 hata_enjekte.py DEPO_YOLU KAYNAK_DOSYA TEST_DOSYASI [en_çok_mutant]
Çıktı: kaç mutant, kaçını test öldürdü (= gerçek 'başarısız test' veren hata), örnek fark.
"""
import ast
import copy
import difflib
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CMP = {ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE, ast.GtE: ast.Gt, ast.Eq: ast.NotEq, ast.NotEq: ast.Eq,
       ast.In: ast.NotIn, ast.NotIn: ast.In, ast.Is: ast.IsNot, ast.IsNot: ast.Is}


def mutantlar(tree):
    sites = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for i, op in enumerate(node.ops):
                if type(op) in CMP:
                    sites.append(("cmp", node, i))
        elif isinstance(node, ast.BoolOp):
            sites.append(("bool", node, 0))
        elif isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub)):
            sites.append(("arith", node, 0))
        elif isinstance(node, ast.Constant) and type(node.value) is int and not isinstance(node.value, bool):
            sites.append(("const", node, 0))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            sites.append(("not", node, 0))
    return sites


def uygula(tree, kind, idx_node, i):
    t = copy.deepcopy(tree)
    nodes = [n for n in ast.walk(t)]
    orig = [n for n in ast.walk(tree)]
    node = nodes[orig.index(idx_node)]
    if kind == "cmp":
        node.ops[i] = CMP[type(node.ops[i])]()
    elif kind == "bool":
        node.op = ast.Or() if isinstance(node.op, ast.And) else ast.And()
    elif kind == "arith":
        node.op = ast.Sub() if isinstance(node.op, ast.Add) else ast.Add()
    elif kind == "const":
        node.value = node.value + 1
    elif kind == "not":
        node.__class__ = ast.Expr
        node.value = node.operand
    ast.fix_missing_locations(t)
    return t


def main():
    depo, kaynak, test = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 80
    rng = random.Random(3)
    tmp = Path(tempfile.mkdtemp()) / "r"
    shutil.copytree(depo, tmp, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    f = tmp / kaynak
    src = f.read_text()
    base = ast.parse(src)
    ref = ast.unparse(base)
    sites = mutantlar(base)
    rng.shuffle(sites)
    sonuc = {"derlenmez": 0, "öldü": 0, "yaşadı": 0}
    fonk = set()
    ornek = None
    for kind, node, i in sites[:limit]:
        try:
            mt = uygula(base, kind, node, i)
            m = ast.unparse(mt)
            compile(m, "m", "exec")
        except Exception:
            sonuc["derlenmez"] += 1
            continue
        if m == ref:
            sonuc["yaşadı"] += 1
            continue
        f.write_text(m)
        try:
            p = subprocess.run([sys.executable, "-m", "pytest", test, "-x", "-q", "-p", "no:cacheprovider"], cwd=tmp, env={**__import__("os").environ, "PYTHONPATH": str(tmp / "src")},
                               capture_output=True, text=True, timeout=60)
            killed = p.returncode != 0 and "failed" in p.stdout
        except subprocess.TimeoutExpired:
            killed = False
        sonuc["öldü" if killed else "yaşadı"] += 1
        if killed:
            fonk.add(getattr(node, "lineno", 0))
            if ornek is None:
                ornek = "".join(list(difflib.unified_diff(ref.splitlines(True), m.splitlines(True), "orijinal", "bozuk", n=1))[:14])
                ornek += "\n--- ilk başarısız test satırı ---\n" + "\n".join(l for l in p.stdout.splitlines() if l.startswith("FAILED"))[:300]
    f.write_text(src)
    n = sum(sonuc.values())
    print(f"mutant={n} (aday yer={len(sites)}) | testin öldürdüğü={sonuc['öldü']} ({sonuc['öldü'] / max(n, 1):.0%}) | "
          f"yaşayan/denk={sonuc['yaşadı']} | derlenmez={sonuc['derlenmez']} | ayrı kaynak satırı={len(fonk)}")
    print(ornek or "(örnek yok)")


if __name__ == "__main__":
    main()
