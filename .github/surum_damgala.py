import re, sys, pathlib
kok, sha = pathlib.Path(sys.argv[1]), sys.argv[2][:10]
BEKCI = ('<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate"><meta http-equiv="Pragma" content="no-cache">'
 '<script>(function(){var S="%s";function yokla(){var m=location.pathname.match(/^\\/[^\\/]+\\//),b=m?m[0]:"/";'
 'fetch(b+"surum.json?t="+Date.now(),{cache:"no-store"}).then(function(r){return r.json()}).then(function(j){'
 'if(j.sha&&j.sha.slice(0,10)!==S){var u=new URL(location.href);if(u.searchParams.get("v")===j.sha.slice(0,10))return;'
 'u.searchParams.set("v",j.sha.slice(0,10));location.replace(u.toString())}}).catch(function(){})}'
 'yokla();addEventListener("pageshow",function(e){if(e.persisted)yokla()});'
 'document.addEventListener("visibilitychange",function(){if(!document.hidden)yokla()})})();</script>') % sha
ATR = re.compile(r'''((?:href|src)\s*=\s*["'])(?![a-z]+:|//|#|data:)([^"'?#]+\.(?:html|js|css|json))(\?[^"'#]*)?''', re.I)
DIN = re.compile(r'''(\+\s*'\.(?:js|json|html)')''')
for p in kok.rglob('*.html'):
    s = p.read_text(encoding='utf-8', errors='surrogateescape')
    s = ATR.sub(lambda m: m.group(1) + m.group(2) + '?v=' + sha, s)
    s = DIN.sub(lambda m: m.group(1)[:-1] + "?v=" + sha + "'", s)
    if 'surum.json?t=' not in s:
        s = re.sub(r'<head[^>]*>', lambda m: m.group(0) + BEKCI, s, count=1) if re.search(r'<head[^>]*>', s) else BEKCI + s
    p.write_text(s, encoding='utf-8', errors='surrogateescape')
for p in kok.rglob('*.js'):
    s = p.read_text(encoding='utf-8', errors='surrogateescape'); t = DIN.sub(lambda m: m.group(1)[:-1] + "?v=" + sha + "'", s)
    if t != s: p.write_text(t, encoding='utf-8', errors='surrogateescape')
