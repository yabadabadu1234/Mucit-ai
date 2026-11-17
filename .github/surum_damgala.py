import re, sys, pathlib
kok, sha = pathlib.Path(sys.argv[1]), sys.argv[2][:10]
BEKCI = ('<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate"><meta http-equiv="Pragma" content="no-cache">'
 '<script>(function(){function tazele(){var u=new URL(location.href),t=+u.searchParams.get("t")||0;'
 'if(Date.now()-t>20000){u.searchParams.set("t",String(Date.now()));location.replace(u.toString());return true}return false}'
 'tazele();addEventListener("pageshow",function(e){if(e.persisted)tazele()});'
 'var gizli=0;document.addEventListener("visibilitychange",function(){if(document.hidden)gizli=Date.now();else if(gizli&&Date.now()-gizli>60000)tazele()})})();</script>')
ATR = re.compile(r'''((?:href|src)\s*=\s*["'])(?![a-z]+:|//|#|data:)([^"'?#]+\.(?:html|js|css|json))(\?[^"'#]*)?''', re.I)
DIN = re.compile(r'''(\+\s*'\.(?:js|json|html)')''')
for p in kok.rglob('*.html'):
    s = p.read_text(encoding='utf-8', errors='surrogateescape')
    s = ATR.sub(lambda m: m.group(1) + m.group(2) + '?v=' + sha, s)
    s = DIN.sub(lambda m: m.group(1)[:-1] + "?v=" + sha + "'", s)
    if 'tazele()' not in s:
        s = re.sub(r'<head[^>]*>', lambda m: m.group(0) + BEKCI, s, count=1) if re.search(r'<head[^>]*>', s) else BEKCI + s
    p.write_text(s, encoding='utf-8', errors='surrogateescape')
for p in kok.rglob('*.js'):
    s = p.read_text(encoding='utf-8', errors='surrogateescape'); t = DIN.sub(lambda m: m.group(1)[:-1] + "?v=" + sha + "'", s)
    if t != s: p.write_text(t, encoding='utf-8', errors='surrogateescape')
