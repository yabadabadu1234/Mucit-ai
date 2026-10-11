"""python-docx tabanlı rapor üreticisi: yerel Word denklemleri (OMML), numaralı şekil/tablo/denklem."""
import copy
import hashlib
import json
import os
import re
import subprocess
import tempfile
import zipfile

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt, RGBColor
from lxml import etree

NS_M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
_CACHE_PATH = os.path.join(os.path.dirname(__file__), ".omml_cache.json")
try:
    _CACHE = json.load(open(_CACHE_PATH))
except Exception:
    _CACHE = {}


def _omml(latex, display):
    latex = re.sub(r"(?<=D)\(on\)", r"(\\mathrm{on})", latex)
    key = ("D:" if display else "I:") + latex
    if key in _CACHE:
        return _CACHE[key]
    src = ("$$%s$$" if display else "$%s$") % latex
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "t.docx")
        subprocess.run(["pandoc", "-f", "markdown", "-t", "docx", "-o", out],
                       input=src, text=True, check=True)
        xml = zipfile.ZipFile(out).read("word/document.xml").decode()
    tag = "oMathPara" if display else "oMath"
    m = re.search(r"<m:%s[ >].*?</m:%s>" % (tag, tag), xml, re.S)
    assert m, "OMML üretilemedi: " + latex
    _CACHE[key] = m.group(0)
    json.dump(_CACHE, open(_CACHE_PATH, "w"))
    return _CACHE[key]


def _math_el(latex, display=False):
    xml = _omml(latex, display)
    tag = "<m:oMathPara" if display else "<m:oMath"
    decl = tag + ' xmlns:m="%s" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"' % NS_M
    return parse_xml(xml.replace(tag, decl, 1))


FONT = "Times New Roman"


def _set_font(run, size=None, bold=None, italic=None, name=FONT, color=None):
    run.font.name = name
    rpr = run._r.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = parse_xml("<w:rFonts %s/>" % nsdecls("w"))
        rpr.insert(0, rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), name)
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)


def _shade(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml('<w:shd %s w:val="clear" w:color="auto" w:fill="%s"/>' % (nsdecls("w"), hex_fill)))


def _cell_borders(cell, val="single", sz=4):
    tcPr = cell._tc.get_or_add_tcPr()
    b = parse_xml('<w:tcBorders %s>' % nsdecls("w") + "".join(
        '<w:%s w:val="%s" w:sz="%d" w:space="0" w:color="000000"/>' % (s, val, sz)
        for s in ("top", "left", "bottom", "right")) + "</w:tcBorders>")
    tcPr.append(b)


class Doc:
    def __init__(self, lang="en", figword=None, tabword=None):
        self.lang = lang
        self.fw = figword or ("Figure" if lang == "en" else "Şekil")
        self.tw = tabword or ("Table" if lang == "en" else "Tablo")
        self.d = Document()
        s = self.d.sections[0]
        s.page_height, s.page_width = Cm(29.7), Cm(21.0)
        for a in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
            setattr(s, a, Cm(2.5))
        st = self.d.styles["Normal"]
        st.font.name = FONT
        st.font.size = Pt(12)
        st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
        pf = st.paragraph_format
        pf.line_spacing = 1.5
        pf.space_after = Pt(6)
        pf.space_before = Pt(0)
        pf.widow_control = True
        self.sec = 0
        self.sub = 0
        self.cnt = {"f": 0, "t": 0, "e": 0}
        self.labels = {}
        self._pending = []  # (paragraph, text, kw)
        self._footer()

    # ---------- sayfa altlığı ----------
    def _footer(self):
        p = self.d.sections[0].footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run()
        _set_font(r, 10)
        for t, txt in (("begin", None), (None, "PAGE"), ("end", None)):
            if t:
                e = parse_xml('<w:fldChar %s w:fldCharType="%s"/>' % (nsdecls("w"), t))
            else:
                e = parse_xml('<w:instrText %s xml:space="preserve"> %s </w:instrText>' % (nsdecls("w"), txt))
            r._r.append(e)

    # ---------- numaralama ----------
    def _num(self, kind):
        self.cnt[kind] += 1
        n = self.cnt[kind]
        if kind == "e":
            return "%d.%d" % (self.sec, n)
        if self.sub:
            return "%d.%d.%d" % (self.sec, self.sub, n)
        return "%d.%d" % (self.sec, n)

    # ---------- satır içi biçim ----------
    def _inline(self, par, text, size=None, bold=False, italic=False, color=None):
        text = text.replace("$^2$", "\u00b2").replace("$^{-1}$", "\u207b\u00b9").replace("$^{1/2}$", "^1/2")
        # önce kalın bölgeler (içinde $...$ olabilir)
        segs = re.split(r"(\*\*.+?\*\*)", text)
        if len(segs) > 1:
            for sg in segs:
                if not sg:
                    continue
                if sg.startswith("**") and sg.endswith("**") and len(sg) > 4:
                    self._inline(par, sg[2:-2], size, True, italic, color)
                else:
                    self._inline(par, sg, size, bold, italic, color)
            return
        parts = re.split(r"(\$[^$]+\$)", text)
        for part in parts:
            if not part:
                continue
            if part.startswith("$") and part.endswith("$") and len(part) > 2:
                lat = part[1:-1]
                mo = re.match(r"^\s*(>|<|\\geq|\\leq|\\approx|\\ll|\\gg)\s*(.*)$", lat)
                if mo:
                    sym = {">": ">", "<": "<", "\\geq": "\u2265", "\\leq": "\u2264", "\\approx": "\u2248", "\\ll": "\u226a", "\\gg": "\u226b"}[mo.group(1)]
                    r0 = par.add_run(sym + "\u200a"); _set_font(r0, size, bold, italic, color=color)
                    lat = mo.group(2)
                if lat.strip():
                    par._p.append(_math_el(lat, False))
                continue
            toks = re.split(r"(\*[^*\s][^*]*\*|`[^`]+`|\[\[[a-z]:[\w\-]+\]\])", part)
            for tk in toks:
                if not tk:
                    continue
                if tk.startswith("`"):
                    r = par.add_run(tk[1:-1]); _set_font(r, (size or 12) - 1, bold, italic, name="Courier New", color=color)
                elif tk.startswith("[["):
                    r = par.add_run("\u27e6" + tk[2:-2] + "\u27e7"); _set_font(r, size, bold, italic, color=color)
                    self._pending.append(r)
                elif tk.startswith("*") and tk.endswith("*") and len(tk) > 2:
                    r = par.add_run(tk[1:-1]); _set_font(r, size, bold, True, color=color)
                else:
                    r = par.add_run(tk); _set_font(r, size, bold, italic, color=color)

    # ---------- bloklar ----------
    def title_block(self, lines, fields):
        for i, (txt, sz, b) in enumerate(lines):
            p = self.d.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(txt); _set_font(r, sz, b)
        t = self.d.add_table(rows=len(fields), cols=2)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, (k, v) in enumerate(fields):
            c0, c1 = t.rows[i].cells
            c0.width, c1.width = Cm(5), Cm(9)
            for c, txt, b in ((c0, k, True), (c1, v, False)):
                c.paragraphs[0].paragraph_format.line_spacing = 1.15
                r = c.paragraphs[0].add_run(txt); _set_font(r, 12, b)
                _cell_borders(c)
        self.d.add_paragraph()

    def h(self, level, text):
        if level == 1:
            self.sec += 1
            self.sub = 0
            self.cnt = {"f": 0, "t": 0, "e": 0}
            up = text.upper() if self.lang == "en" else text.replace("i", "İ").replace("ı", "I").upper()
            label = "%d  %s" % (self.sec, up)
        elif level == 2:
            self.sub += 1
            self.cnt["f"] = 0
            self.cnt["t"] = 0
            label = "%d.%d  %s" % (self.sec, self.sub, text)
        else:
            label = text
        p = self.d.add_paragraph()
        p.paragraph_format.keep_with_next = True
        p.paragraph_format.space_before = Pt(12 if level < 3 else 6)
        p.paragraph_format.space_after = Pt(6)
        self._inline(p, label, size=12, bold=True, italic=(level == 3))
        return p

    def p(self, text, indent=False, size=None, align=None, keep=False):
        par = self.d.add_paragraph()
        if align == "j":
            par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if keep:
            par.paragraph_format.keep_with_next = True
        self._inline(par, text, size=size)
        return par

    def bullets(self, items, numbered=False, size=None):
        for i, it in enumerate(items, 1):
            par = self.d.add_paragraph()
            par.paragraph_format.left_indent = Cm(1.0)
            par.paragraph_format.first_line_indent = Cm(-0.6)
            par.paragraph_format.space_after = Pt(2)
            mark = ("%d. " % i) if numbered else "• "
            r = par.add_run(mark); _set_font(r, size)
            self._inline(par, it, size=size)

    def eq(self, latex, label=None):
        n = self._num("e")
        if label:
            self.labels["e:" + label] = "(%s)" % n
        t = self.d.add_table(rows=1, cols=3)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        ws = (Cm(1.25), Cm(12.5), Cm(2.25))
        for col, w in zip(t.columns, ws):
            col.width = w
        for c, w in zip(t.rows[0].cells, ws):
            c.width = w
        c1 = t.rows[0].cells[1]
        c1.paragraphs[0].paragraph_format.line_spacing = 1.0
        c1.paragraphs[0]._p.append(_math_el(latex, True))
        c2 = t.rows[0].cells[2]
        c2.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        c2.paragraphs[0].paragraph_format.line_spacing = 1.0
        r = c2.paragraphs[0].add_run("(%s)" % n); _set_font(r, 12)
        sp = self.d.add_paragraph(); sp.paragraph_format.space_after = Pt(0)
        sp.paragraph_format.line_spacing = 0.6

    def fig(self, label, path, caption, width_cm=14.5):
        n = self._num("f")
        self.labels["f:" + label] = "%s %s" % (self.fw, n)
        par = self.d.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.keep_with_next = True
        par.paragraph_format.line_spacing = 1.0
        par.add_run().add_picture(path, width=Cm(width_cm))
        cp = self.d.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp.paragraph_format.line_spacing = 1.0
        cp.paragraph_format.space_after = Pt(12)
        self._inline(cp, "%s %s  %s" % (self.fw, n, caption), size=10)

    def tab(self, label, header, rows, caption, widths=None, size=10, align_first_left=True, header_rows=1):
        n = self._num("t")
        self.labels["t:" + label] = "%s %s" % (self.tw, n)
        cp = self.d.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp.paragraph_format.keep_with_next = True
        cp.paragraph_format.line_spacing = 1.0
        cp.paragraph_format.space_after = Pt(4)
        self._inline(cp, "%s %s  %s" % (self.tw, n, caption), size=10)
        allrows = ([header] if header and not isinstance(header[0], list) else (header or [])) + rows
        ncol = max(len(r) for r in allrows)
        t = self.d.add_table(rows=len(allrows), cols=ncol)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        nh = (len(header) if header and isinstance(header[0], list) else (1 if header else 0))
        if widths:
            for col, w in zip(t.columns, widths):
                col.width = Cm(w)
        for i, row in enumerate(allrows):
            for j in range(ncol):
                txt = row[j] if j < len(row) else ""
                c = t.rows[i].cells[j]
                if widths:
                    c.width = Cm(widths[j])
                par = c.paragraphs[0]
                par.paragraph_format.line_spacing = 1.0
                par.paragraph_format.space_after = Pt(1)
                par.paragraph_format.keep_with_next = (i < len(allrows) - 1)
                par.alignment = WD_ALIGN_PARAGRAPH.LEFT if (j == 0 and align_first_left) else WD_ALIGN_PARAGRAPH.CENTER
                self._inline(par, str(txt), size=size, bold=(i < nh))
                _cell_borders(c)
                if i < nh:
                    _shade(c, "D9D9D9")
        if nh:
            trPr = t.rows[0]._tr.get_or_add_trPr()
            trPr.append(parse_xml('<w:tblHeader %s/>' % nsdecls("w")))
        for row in t.rows:
            trPr = row._tr.get_or_add_trPr()
            trPr.append(parse_xml('<w:cantSplit %s/>' % nsdecls("w")))
        sp = self.d.add_paragraph(); sp.paragraph_format.space_after = Pt(6)

    def code(self, text, caption=None, size=9):
        if caption:
            cp = self.d.add_paragraph()
            cp.paragraph_format.keep_with_next = True
            cp.paragraph_format.line_spacing = 1.0
            self._inline(cp, caption, size=10, bold=True)
        t = self.d.add_table(rows=1, cols=1)
        c = t.rows[0].cells[0]
        _cell_borders(c)
        _shade(c, "F2F2F2")
        first = True
        for line in text.rstrip("\n").split("\n"):
            par = c.paragraphs[0] if first else c.add_paragraph()
            first = False
            par.paragraph_format.line_spacing = 1.0
            par.paragraph_format.space_after = Pt(0)
            r = par.add_run(line if line else " ")
            _set_font(r, size, name="Courier New")
        sp = self.d.add_paragraph(); sp.paragraph_format.space_after = Pt(6)

    def box(self, title, lines, fill="EAF1FB", size=11):
        """Öğretici kutu (Türkçe rehberde)."""
        t = self.d.add_table(rows=1, cols=1)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        c = t.rows[0].cells[0]
        _cell_borders(c, sz=6)
        _shade(c, fill)
        par = c.paragraphs[0]
        par.paragraph_format.line_spacing = 1.15
        par.paragraph_format.space_after = Pt(3)
        self._inline(par, title, size=size, bold=True)
        for ln in lines:
            par = c.add_paragraph()
            par.paragraph_format.line_spacing = 1.15
            par.paragraph_format.space_after = Pt(3)
            self._inline(par, ln, size=size)
        sp = self.d.add_paragraph(); sp.paragraph_format.space_after = Pt(6)

    def pagebreak(self):
        self.d.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ---------- kaydet ----------
    def save(self, path):
        for r in self._pending:
            def sub(m):
                key = m.group(1)
                assert key in self.labels, "etiket yok: " + key
                return self.labels[key]
            r.text = re.sub(r"\u27e6([a-z]:[\w\-]+)\u27e7", sub, r.text)
        self.d.save(path)
