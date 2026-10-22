import os, copy, glob
from sexp import parse, Q, find, first

SYMDIR = '/usr/share/kicad/symbols'
_cache = {}

def _lib(name):
    if name not in _cache:
        path = os.path.join(SYMDIR, name + '.kicad_sym')
        if not os.path.exists(path):
            path = os.path.join(os.path.dirname(__file__), 'kutuphane', name + '.kicad_sym')
        root = parse(open(path).read())
        d = {}
        for c in root[1:]:
            if isinstance(c, list) and c and c[0] == 'symbol':
                d[str(c[1])] = c
        _cache[name] = d
    return _cache[name]

def sembol(lib, ad):
    d = _lib(lib)
    node = d[ad]
    ext = first(node, 'extends')
    if ext is None:
        return copy.deepcopy(node)
    parent = sembol(lib, str(ext[1]))
    pname = str(parent[1])
    new = copy.deepcopy(parent)
    new[1] = Q(ad)
    for i, c in enumerate(new):
        if isinstance(c, list) and c and c[0] == 'symbol':
            sub = str(c[1])
            assert sub.startswith(pname)
            c[1] = Q(ad + sub[len(pname):])
    props = {str(p[1]): p for p in find(node, 'property')}
    for i, c in enumerate(new):
        if isinstance(c, list) and c and c[0] == 'property' and str(c[1]) in props:
            new[i] = copy.deepcopy(props[str(c[1])])
    return new

def pinler(node):
    out = []
    def walk(n, unit):
        for c in n[1:]:
            if isinstance(c, list) and c:
                if c[0] == 'symbol':
                    nm = str(c[1])
                    parts = nm.rsplit('_', 2)
                    u = int(parts[1]) if len(parts) == 3 else 0
                    walk(c, u)
                elif c[0] == 'pin':
                    at = first(c, 'at'); ln = first(c, 'length')
                    nmn = first(c, 'name'); num = first(c, 'number')
                    hide = 'hide' in c
                    out.append(dict(unit=unit, tip=c[1], x=float(at[1]), y=float(at[2]), a=float(at[3]),
                                    L=float(ln[1]), name=str(nmn[1]), num=str(num[1]), hide=hide))
    walk(node, 0)
    return out

def prop(node, k):
    for p in find(node, 'property'):
        if str(p[1]) == k:
            return str(p[2])
