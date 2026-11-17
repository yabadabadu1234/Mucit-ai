import json, os, time, random, urllib.request, urllib.error
UC = 'https://evren-llmapi.ssyz.org.tr/v1/chat/completions'
def _akis(model, mesajlar, max_tokens, sicaklik, parca):
    govde = json.dumps({'model': model, 'messages': mesajlar, 'max_tokens': max_tokens, 'temperature': sicaklik, 'stream': True,
                        'thinking': False, 'chat_template_kwargs': {'enable_thinking': False}}).encode()
    r = urllib.request.Request(UC, govde, {'Authorization': 'Bearer ' + os.environ['EVREN_API_KEY'], 'Content-Type': 'application/json', 'Accept': 'text/event-stream'})
    with urllib.request.urlopen(r, timeout=240) as y:
        for satir in y:
            s = satir.decode('utf-8', 'replace').strip()
            if not s.startswith('data:'): continue
            s = s[5:].strip()
            if s == '[DONE]': return True
            j = json.loads(s)
            if j.get('error'): raise RuntimeError(str(j['error']))
            ch = j.get('choices') or []
            if ch:
                parca.append((ch[0].get('delta') or {}).get('content') or '')
                if ch[0].get('finish_reason'): return ch[0]['finish_reason']
    raise ConnectionError('akış yarıda kesildi')
def sor(model, mesajlar, max_tokens=16000, deneme=30, sicaklik=0.2, devam=False, kayit=print):
    birikmis, son = '', None
    for d in range(deneme):
        parca = []
        m = mesajlar if not (devam and birikmis) else mesajlar + [{'role': 'assistant', 'content': birikmis}, {'role': 'user', 'content': 'Bağlantı kesildi. Yukarıdaki metnin tam kaldığı yerden, hiçbir şeyi tekrar etmeden devam et.'}]
        try:
            f = _akis(model, m, max_tokens, sicaklik, parca)
            return birikmis + ''.join(parca), f
        except urllib.error.HTTPError as e:
            if e.code == 429:
                bek = float(e.headers.get('Retry-After') or 30)
                kayit(f'  429 sınır ({e.read()[:120]!r}); {bek:.0f} sn bekleniyor')
                if devam: birikmis += ''.join(parca)
                time.sleep(bek + random.random() * 3); continue
            son = e
            if devam: birikmis += ''.join(parca)
            kayit(f'  deneme {d+1} düştü (HTTP {e.code})'); time.sleep(min(300, 5 * 2 ** min(d, 6)) * (0.5 + random.random()))
        except Exception as e:
            son = e
            if devam: birikmis += ''.join(parca)
            kayit(f'  deneme {d+1} düştü ({type(e).__name__}); {"birikmiş " + str(len(birikmis)) + " harf korunuyor" if devam else "baştan"}')
            time.sleep(min(300, 5 * 2 ** min(d, 6)) * (0.5 + random.random()))
    raise RuntimeError(f'{deneme} denemede olmadı: {son}')
