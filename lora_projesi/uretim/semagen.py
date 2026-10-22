import math, uuid, os
from sexp import parse, dump, Q, find, first
from kutuphane import sembol, pinler, prop

POWER = {'GND': ('power', 'GND'), '+3V3': ('power', '+3V3'), '+5V': ('power', '+5V'),
         '+12V': ('power', '+12V'), '+1V8': ('power', '+1V8')}

def u():
    return str(uuid.uuid4())

def r4(v):
    return round(v + 0.0, 4)

class Parca:
    pass

class Sema:
    def __init__(self, ad, kagit='A2', baslik=''):
        self.ad = ad
        self.kagit = kagit
        self.baslik = baslik
        self.kok = u()
        self.parcalar = []
        self.libs = {}
        self.ogeler = []
        self.pwr_n = 0
        self.flg_n = 0
        self.bayrak = []
        self.grup_listesi = []
        self.refler = set()

    def lib(self, lib, ad):
        k = lib + ':' + ad
        if k not in self.libs:
            s = sembol(lib, ad)
            s[1] = Q(k)
            self.libs[k] = s
        return self.libs[k]

    def parca(self, ref, lib, ad, deger, fp, pinler_net, rot=None, dnp=False, grup=None, alanlar=None):
        assert ref not in self.refler, ref
        self.refler.add(ref)
        node = self.lib(lib, ad)
        ps = pinler(node)
        pins = [p for p in ps if p['unit'] in (0, 1)]
        if rot is None:
            rot = 0
            nonv = [p for p in pins if p['a'] in (0.0, 180.0)]
            if not nonv and len(pins) == 2:
                rot = 90
        c = Parca()
        c.ref, c.libad, c.deger, c.fp, c.pins, c.rot, c.dnp = ref, lib + ':' + ad, deger, fp, pins, rot, dnp
        c.net = {str(k): v for k, v in pinler_net.items()}
        c.grup = grup
        c.alanlar = alanlar or {}
        nums = {p['num'] for p in pins}
        for k in c.net:
            assert k in nums, (ref, k, sorted(nums))
        self.parcalar.append(c)
        return c

    def _xf(self, c, px, py):
        t = math.radians(c.rot)
        X = px * math.cos(t) - py * math.sin(t)
        Y = px * math.sin(t) + py * math.cos(t)
        return X, Y

    def _hazirla(self, c):
        rows = []
        lw = rw = 0.0
        minx = miny = 1e9; maxx = maxy = -1e9
        for p in c.pins:
            X, Y = self._xf(c, p['x'], p['y'])
            t = math.radians(p['a'] + c.rot)
            dx, dy = -math.cos(t), -math.sin(t)
            dx, dy = round(dx), round(dy)
            net = c.net.get(p['num'])
            wlab = (len(net) * 1.3 + 7.0) if net else 4.0
            if dx < 0: lw = max(lw, wlab)
            if dx > 0: rw = max(rw, wlab)
            minx = min(minx, X); maxx = max(maxx, X); miny = min(miny, Y); maxy = max(maxy, Y)
            rows.append((p, X, Y, dx, dy))
        c.rows = rows
        c.w = (maxx - minx) + lw + rw + 8
        c.h = (maxy - miny) + 12
        c.ox = -(minx) + lw + 4
        c.oy = maxy + 6

    def yerlestir(self, genislik=380.0, x0=15.0, y0=30.0):
        for c in self.parcalar:
            self._hazirla(c)
        x = x0; y = y0; satir_h = 0.0
        son_grup = object()
        for c in self.parcalar:
            if c.grup != son_grup:
                if x > x0:
                    y += satir_h + 14; x = x0; satir_h = 0.0
                if c.grup:
                    self.ogeler.append(('text', c.grup, x, y - 6))
                son_grup = c.grup
            if x + c.w > x0 + genislik:
                y += satir_h + 8; x = x0; satir_h = 0.0
            c.sx = round((x + c.ox) / 2.54) * 2.54
            c.sy = round((y + c.oy) / 2.54) * 2.54
            x += c.w + 6
            satir_h = max(satir_h, c.h)

    def _wire(self, x1, y1, x2, y2):
        self.ogeler.append(('wire', r4(x1), r4(y1), r4(x2), r4(y2)))

    def _etiket(self, net, x, y, dx, dy):
        self.ogeler.append(('label', net, r4(x), r4(y), dx, dy))

    def _power(self, net, x, y, rot=0):
        lib, ad = POWER[net]
        node = self.lib(lib, ad)
        self.pwr_n += 1
        self.ogeler.append(('power', lib + ':' + ad, net, r4(x), r4(y), '#PWR%03d' % self.pwr_n, rot))

    def bagla(self):
        for c in self.parcalar:
            for p, X, Y, dx, dy in c.rows:
                sx = c.sx + X; sy = c.sy - Y
                ox, oy = dx, -dy
                net = c.net.get(p['num'])
                if net is None:
                    if p['hide'] and p['tip'].startswith('power'):
                        continue
                    self.ogeler.append(('nc', r4(sx), r4(sy)))
                    continue
                ex, ey = sx + ox * 5.08, sy + oy * 5.08
                self._wire(sx, sy, ex, ey)
                if net in POWER:
                    self._power(net, ex, ey)
                else:
                    self._etiket(net, ex, ey, ox, oy)
                if net in self.bayrak:
                    self.bayrak.remove(net)
                    ox2, oy2 = ox, oy
                    # PWR_FLAG on the same stub end, offset
                    self.flg_n += 1
                    fx, fy = ex + ox * 7.62, ey + oy * 7.62
                    self._wire(ex, ey, fx, fy)
                    self.lib('power', 'PWR_FLAG')
                    self.ogeler.append(('power', 'power:PWR_FLAG', 'PWR_FLAG', r4(fx), r4(fy), '#FLG%03d' % self.flg_n, 0))

    def yaz(self, yol):
        self.yerlestir()
        self.bagla()
        out = []
        out.append('(kicad_sch (version 20230121) (generator eeschema)')
        out.append('  (uuid %s)' % self.kok)
        out.append('  (paper "%s")' % self.kagit)
        out.append('  (title_block (title "%s"))' % self.baslik)
        out.append('  (lib_symbols')
        for k, s in self.libs.items():
            out.append('    ' + dump(s))
        out.append('  )')
        for c in self.parcalar:
            out.append(self._parca_text(c))
        for o in self.ogeler:
            k = o[0]
            if k == 'wire':
                out.append('  (wire (pts (xy %s %s) (xy %s %s)) (stroke (width 0) (type default)) (uuid %s))' % (o[1], o[2], o[3], o[4], u()))
            elif k == 'nc':
                out.append('  (no_connect (at %s %s) (uuid %s))' % (o[1], o[2], u()))
            elif k == 'label':
                _, net, x, y, ox, oy = o
                if ox < 0:
                    ang, just = 180, 'right bottom'
                elif ox > 0:
                    ang, just = 0, 'left bottom'
                elif oy > 0:
                    ang, just = 270, 'right bottom'
                else:
                    ang, just = 90, 'left bottom'
                out.append('  (label "%s" (at %s %s %d) (effects (font (size 1.27 1.27)) (justify %s)) (uuid %s))' % (net, x, y, ang, just, u()))
            elif k == 'power':
                _, libad, val, x, y, ref, rot = o
                out.append(self._power_text(libad, val, x, y, ref, rot))
            elif k == 'text':
                out.append('  (text "%s" (at %s %s 0) (effects (font (size 2.54 2.54) bold) (justify left bottom)) (uuid %s))' % (o[1], r4(o[2]), r4(o[3]), u()))
        out.append('  (sheet_instances (path "/" (page "1")))')
        out.append(')')
        open(yol, 'w').write('\n'.join(out) + '\n')

    def _prop(self, k, v, x, y, hide=False, size=1.27):
        return '(property "%s" "%s" (at %s %s 0) (effects (font (size %s %s))%s))' % (k, v.replace('"', "'"), r4(x), r4(y), size, size, ' hide' if hide else '')

    def _parca_text(self, c):
        x, y = c.sx, c.sy
        p = []
        p.append('  (symbol (lib_id "%s") (at %s %s %d) (unit 1)' % (c.libad, r4(x), r4(y), c.rot))
        p.append('    (in_bom yes) (on_board yes) (dnp %s) (uuid %s)' % ('yes' if c.dnp else 'no', u()))
        p.append('    ' + self._prop('Reference', c.ref, x, y - c.h / 2 + 3))
        p.append('    ' + self._prop('Value', c.deger, x, y + c.h / 2 - 3))
        p.append('    ' + self._prop('Footprint', c.fp or '', x, y, hide=True))
        p.append('    ' + self._prop('Datasheet', '', x, y, hide=True))
        for k, v in c.alanlar.items():
            p.append('    ' + self._prop(k, v, x, y, hide=True))
        seen = set()
        for pin in c.pins:
            if pin['num'] in seen: continue
            seen.add(pin['num'])
            p.append('    (pin "%s" (uuid %s))' % (pin['num'], u()))
        p.append('    (instances (project "%s" (path "/%s" (reference "%s") (unit 1))))' % (self.ad, self.kok, c.ref))
        p.append('  )')
        return '\n'.join(p)

    def _power_text(self, libad, val, x, y, ref, rot):
        p = []
        p.append('  (symbol (lib_id "%s") (at %s %s %d) (unit 1)' % (libad, x, y, rot))
        p.append('    (in_bom yes) (on_board yes) (dnp no) (uuid %s)' % u())
        p.append('    ' + self._prop('Reference', ref, x, y - 3, hide=True))
        p.append('    ' + self._prop('Value', val, x, y + 3))
        p.append('    ' + self._prop('Footprint', '', x, y, hide=True))
        p.append('    ' + self._prop('Datasheet', '', x, y, hide=True))
        p.append('    (pin "1" (uuid %s))' % u())
        p.append('    (instances (project "%s" (path "/%s" (reference "%s") (unit 1))))' % (self.ad, self.kok, ref))
        p.append('  )')
        return '\n'.join(p)
