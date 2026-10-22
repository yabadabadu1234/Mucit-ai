import re, copy

class Q(str):
    pass

_tok = re.compile(r'\s*(\(|\)|"(?:\\.|[^"\\])*"|[^\s()"]+)')

def parse(text):
    pos = 0
    stack = [[]]
    for m in _tok.finditer(text):
        t = m.group(1)
        if t == '(':
            stack.append([])
        elif t == ')':
            x = stack.pop()
            stack[-1].append(x)
        elif t[0] == '"':
            stack[-1].append(Q(t[1:-1].replace('\\"', '"').replace('\\\\', '\\')))
        else:
            stack[-1].append(t)
    assert len(stack) == 1
    return stack[0][0]

def dump(node, ind=0):
    if isinstance(node, Q):
        return '"' + node.replace('\\', '\\\\').replace('"', '\\"') + '"'
    if isinstance(node, str):
        return node
    if isinstance(node, (int, float)):
        return repr(node)
    inner = ' '.join(dump(n) for n in node)
    return '(' + inner + ')'

def find(node, name):
    return [c for c in node[1:] if isinstance(c, list) and c and c[0] == name]

def first(node, name):
    r = find(node, name)
    return r[0] if r else None
