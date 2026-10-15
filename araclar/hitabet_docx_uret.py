#!/usr/bin/env python3
"""
hitabet_docx_uret.py
Generates publication-grade, professionally styled Microsoft Word documents (.docx)
from the English and Turkish speech markdown texts:
- docs/planli_eskitme_hitabet_metni_en.md -> docs/planli_eskitme_hitabet_metni_en.docx
- docs/planli_eskitme_hitabet_metni_tr.md -> docs/planli_eskitme_hitabet_metni_tr.docx
"""

import os
import re
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

NAVY_HEX = "1B365D"
SLATE_NAVY_HEX = "2B4C7E"
DARK_SLATE_HEX = "374151"
BODY_CHARCOAL_HEX = "1F2937"
MUTED_GRAY_HEX = "64748B"
BORDER_GRAY_HEX = "CBD5E0"
CALLOUT_BG_HEX = "F1F5F9"
MATH_BG_HEX = "F8FAFC"
TEAL_HEX = "0F766E"
CRIMSON_HEX = "991B1B"
INDIGO_HEX = "4338CA"

COLOR_NAVY = RGBColor(0x1B, 0x36, 0x5D)
COLOR_SLATE_NAVY = RGBColor(0x2B, 0x4C, 0x7E)
COLOR_DARK_SLATE = RGBColor(0x37, 0x41, 0x51)
COLOR_BODY = RGBColor(0x1F, 0x29, 0x37)
COLOR_MUTED = RGBColor(0x64, 0x74, 0x8B)
COLOR_TEAL = RGBColor(0x0F, 0x76, 0x6E)
COLOR_CRIMSON = RGBColor(0x99, 0x1B, 0x1B)
COLOR_INDIGO = RGBColor(0x43, 0x38, 0xCA)

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>'))

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def set_cell_border_left_only(cell, color_hex="1B365D", sz="18"):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="none"/>
            <w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color_hex}"/>
            <w:bottom w:val="none"/>
            <w:right w:val="none"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)

def add_callout_box(doc, direction_text, lang='en'):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Inches(6.5)
    
    cell = tbl.cell(0, 0)
    set_cell_background(cell, CALLOUT_BG_HEX)
    set_cell_border_left_only(cell, color_hex=NAVY_HEX, sz="24")
    set_cell_margins(cell, top=100, bottom=100, left=160, right=140)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    
    clean_text = direction_text.strip()
    if clean_text.startswith('*(') and clean_text.endswith(')*'):
        clean_text = clean_text[2:-2].strip()
    elif clean_text.startswith('(') and clean_text.endswith(')'):
        clean_text = clean_text[1:-1].strip()
        
    tag = "SLIDE DISPLAY / ORATORICAL DIRECTION: " if lang == 'en' else "SUNUM PANOSU / HİTABET YÖNERGESİ: "
    r_icon = p.add_run(tag)
    r_icon.font.name = "Calibri"
    r_icon.font.size = Pt(8.5)
    r_icon.font.bold = True
    r_icon.font.color.rgb = COLOR_NAVY
    
    r_text = p.add_run(clean_text)
    r_text.font.name = "Calibri"
    r_text.font.size = Pt(9.5)
    r_text.font.italic = True
    r_text.font.color.rgb = COLOR_DARK_SLATE
    
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.space_after = Pt(2)
    spacer.paragraph_format.line_spacing = 0.5

def add_math_box(doc, header_title, items):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Inches(6.5)
    
    cell = tbl.cell(0, 0)
    set_cell_background(cell, MATH_BG_HEX)
    set_cell_border_left_only(cell, color_hex=MUTED_GRAY_HEX, sz="16")
    set_cell_margins(cell, top=120, bottom=120, left=160, right=140)
    
    p0 = cell.paragraphs[0]
    p0.paragraph_format.space_before = Pt(2)
    p0.paragraph_format.space_after = Pt(4)
    r_h = p0.add_run(header_title)
    r_h.font.name = "Calibri"
    r_h.font.size = Pt(9.5)
    r_h.font.bold = True
    r_h.font.color.rgb = COLOR_SLATE_NAVY
    
    for item in items:
        p = cell.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        
        clean_item = item.strip()
        if clean_item.startswith('* '):
            clean_item = clean_item[2:].strip()
        
        if ':' in clean_item:
            lbl, val = clean_item.split(':', 1)
            r_l = p.add_run(lbl + ": ")
            r_l.font.name = "Calibri"
            r_l.font.size = Pt(9.0)
            r_l.font.bold = True
            r_l.font.color.rgb = COLOR_NAVY
            
            r_v = p.add_run(val.strip())
            r_v.font.name = "Consolas"
            r_v.font.size = Pt(8.5)
            r_v.font.color.rgb = COLOR_BODY
        else:
            r_v = p.add_run(clean_item)
            r_v.font.name = "Consolas"
            r_v.font.size = Pt(8.5)
            r_v.font.color.rgb = COLOR_BODY
            
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.space_after = Pt(2)
    spacer.paragraph_format.line_spacing = 0.5

def parse_runs_into_paragraph(p, text, default_font_size=10.5, default_color=COLOR_BODY, default_italic=False):
    tokens = []
    pattern = re.compile(r'(\*\*[^*]+\*\*|\*[^*]+\*|[^*]+)')
    for match in pattern.finditer(text):
        chunk = match.group(0)
        if chunk.startswith('**') and chunk.endswith('**'):
            tokens.append((chunk[2:-2], True, False))
        elif chunk.startswith('*') and chunk.endswith('*'):
            tokens.append((chunk[1:-1], False, True))
        else:
            tokens.append((chunk, False, False))
            
    for text_part, is_bold, is_italic in tokens:
        run = p.add_run(text_part)
        run.font.name = "Calibri"
        run.font.size = Pt(default_font_size)
        run.font.bold = is_bold
        run.font.italic = is_italic or default_italic
        run.font.color.rgb = default_color

def setup_page_layout(doc, lang='en'):
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)
        section.different_first_page_header_footer = True
        
        # Header
        header = section.header
        p_hdr = header.paragraphs[0]
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_hdr.paragraph_format.space_after = Pt(4)
        hdr_text = "Planned Obsolescence: Juristic, Rational & Moral Ruling — Oratorical Address" if lang == 'en' else "Planlı Eskitme ve Platform Vesayeti Hukuki Modeli — Tam Hitabet Metni"
        r_hdr = p_hdr.add_run(hdr_text)
        r_hdr.font.name = "Calibri"
        r_hdr.font.size = Pt(8.5)
        r_hdr.font.italic = True
        r_hdr.font.color.rgb = COLOR_MUTED
        
        pBdr = parse_xml(f'''
            <w:pBdr {nsdecls("w")}>
                <w:bottom w:val="single" w:sz="6" w:space="3" w:color="{BORDER_GRAY_HEX}"/>
            </w:pBdr>
        ''')
        p_hdr._p.get_or_add_pPr().append(pBdr)
        
        # Footer
        footer = section.footer
        p_ftr = footer.paragraphs[0]
        p_ftr.paragraph_format.space_before = Pt(4)
        
        ftr_text = "Universal Jurisprudential Model | Oratorical Delivery" if lang == 'en' else "Evrensel Fıkhî Model | Hitabet ve Usul Risalesi"
        r_l = p_ftr.add_run(ftr_text)
        r_l.font.name = "Calibri"
        r_l.font.size = Pt(8.5)
        r_l.font.color.rgb = COLOR_MUTED
        
        p_ftr.paragraph_format.tab_stops.add_tab_stop(Inches(6.5), docx.enum.text.WD_TAB_ALIGNMENT.RIGHT)
        page_label = "\tPage " if lang == 'en' else "\tSayfa "
        r_tab = p_ftr.add_run(page_label)
        r_tab.font.name = "Calibri"
        r_tab.font.size = Pt(8.5)
        r_tab.font.color.rgb = COLOR_MUTED
        
        fld1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
        instr = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
        fld2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
        fld3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
        r_tab._r.extend([fld1, instr, fld2, fld3])
        
        of_label = " of " if lang == 'en' else " / "
        r_of = p_ftr.add_run(of_label)
        r_of.font.name = "Calibri"
        r_of.font.size = Pt(8.5)
        r_of.font.color.rgb = COLOR_MUTED
        
        fld4 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
        instr2 = parse_xml(r'<w:instrText %s xml:space="preserve"> NUMPAGES </w:instrText>' % nsdecls('w'))
        fld5 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
        fld6 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
        r_of._r.extend([fld4, instr2, fld5, fld6])
        
        pBdr_ftr = parse_xml(f'''
            <w:pBdr {nsdecls("w")}>
                <w:top w:val="single" w:sz="6" w:space="3" w:color="{BORDER_GRAY_HEX}"/>
            </w:pBdr>
        ''')
        p_ftr._p.get_or_add_pPr().append(pBdr_ftr)

def build_cover_header(doc, lang='en'):
    p_cat = doc.add_paragraph()
    p_cat.paragraph_format.space_before = Pt(0)
    p_cat.paragraph_format.space_after = Pt(4)
    cat_text = "FORMAL JURISTIC ORATION & METHODOLOGICAL TREATISE" if lang == 'en' else "FIKHÎ VE İKTİSADİ HİTABET METNİ & METODOLOJİK RİSALE"
    r_cat = p_cat.add_run(cat_text)
    r_cat.font.name = "Calibri"
    r_cat.font.size = Pt(9.5)
    r_cat.font.bold = True
    r_cat.font.color.rgb = COLOR_SLATE_NAVY
    
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(2)
    p_title.paragraph_format.space_after = Pt(4)
    p_title.paragraph_format.line_spacing = 1.1
    title_text = "PLANNED OBSOLESCENCE: ITS LEGAL, RATIONAL AND MORAL RULING" if lang == 'en' else "PLANLI ESKİTME VE PLATFORM TEKELLERİ HUKUKİ MODELİ"
    r_title = p_title.add_run(title_text)
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(20)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_NAVY
    
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(8)
    sub_text = "A Formal Juristic Address Based on Commutative Integrity, Strict Delictual Liability, and the Commons" if lang == 'en' else "İvaz Adaleti, Kusursuz Sorumluluk ve Ekolojik Müşterekler Çerçevesinde Tam Hitabet Metni"
    r_sub = p_sub.add_run(sub_text)
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(11.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = COLOR_DARK_SLATE
    
    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_before = Pt(0)
    p_meta.paragraph_format.space_after = Pt(12)
    meta_text = "Universal Jurisprudential Model  •  Four Archetypes  •  Six Juristic Harmonies  •  Eight Evidences" if lang == 'en' else "Evrensel Fıkhî Model  •  Dört Arketip  •  Altı Fıkhî Uyum  •  Sekiz Kat'î Delil"
    r_meta = p_meta.add_run(meta_text)
    r_meta.font.name = "Calibri"
    r_meta.font.size = Pt(9.0)
    r_meta.font.color.rgb = COLOR_MUTED
    
    pBdr = parse_xml(f'''
        <w:pBdr {nsdecls("w")}>
            <w:bottom w:val="single" w:sz="18" w:space="8" w:color="{NAVY_HEX}"/>
        </w:pBdr>
    ''')
    p_meta._p.get_or_add_pPr().append(pBdr)

def generate_docx_en(input_md_path, output_docx_path):
    print(f"[EN] Reading from: {input_md_path}")
    with open(input_md_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    doc = Document()
    setup_page_layout(doc, lang='en')
    build_cover_header(doc, lang='en')
    
    lines = content.split('\n')
    i = 0
    total_lines = len(lines)
    
    while i < total_lines:
        line = lines[i].strip()
        if not line:
            i += 1
            continue
            
        # Stage direction / slide callout
        if line.startswith('*(') and line.endswith(')*'):
            add_callout_box(doc, line, lang='en')
            i += 1
            continue
            
        # Mathematical Specification Block
        if line.startswith('Mathematical Specification:') or line.startswith('Mathematical & Jurisprudential Specification:') or line.startswith('THE MATHEMATICAL SPECIFICATION'):
            header_title = line
            math_items = []
            i += 1
            while i < total_lines:
                curr = lines[i]
                if not curr.strip():
                    if i + 1 < total_lines and (lines[i+1].startswith('* ') or lines[i+1].startswith('1. ') or lines[i+1].startswith('2. ') or lines[i+1].startswith('3. ') or lines[i+1].startswith('4. ') or lines[i+1].startswith('  ')):
                        i += 1
                        continue
                    else:
                        break
                if curr.startswith('* ') or curr.startswith('1. ') or curr.startswith('2. ') or curr.startswith('3. ') or curr.startswith('4. ') or curr.startswith('  ') or curr.startswith('*('):
                    math_items.append(curr)
                    i += 1
                else:
                    break
            add_math_box(doc, header_title, math_items)
            continue
            
        # Main Heading 1
        if line.startswith('MODEL ') or line.startswith('THE ROOT ') or line.startswith('CONCLUSION.') or line.startswith('THE JURISTIC ') or line.startswith('NOW THE DEFENSES'):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(16)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            
            run = p.add_run(line)
            run.font.name = "Calibri"
            run.font.size = Pt(13.0)
            run.font.bold = True
            run.font.color.rgb = COLOR_NAVY
            
            pBdr = parse_xml(f'''
                <w:pBdr {nsdecls("w")}>
                    <w:bottom w:val="single" w:sz="6" w:space="2" w:color="{BORDER_GRAY_HEX}"/>
                </w:pBdr>
            ''')
            p._p.get_or_add_pPr().append(pBdr)
            i += 1
            continue
            
        # Evidence Heading 2
        if line.startswith('OUR ') and 'EVIDENCE:' in line:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(13)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.keep_with_next = True
            
            run = p.add_run(line)
            run.font.name = "Calibri"
            run.font.size = Pt(11.5)
            run.font.bold = True
            run.font.color.rgb = COLOR_SLATE_NAVY
            i += 1
            continue
            
        # Section headings
        if line.startswith('The actors and their jurisdictional standing:') or line.startswith('The structural and economic parameters:'):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.keep_with_next = True
            
            run = p.add_run(line)
            run.font.name = "Calibri"
            run.font.size = Pt(11.0)
            run.font.bold = True
            run.font.color.rgb = COLOR_DARK_SLATE
            i += 1
            continue
            
        # Bullet lists
        if line.startswith('* '):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.15
            
            clean_bullet = line[2:].strip()
            r_b = p.add_run("•  ")
            r_b.font.name = "Calibri"
            r_b.font.size = Pt(10.5)
            r_b.font.bold = True
            r_b.font.color.rgb = COLOR_SLATE_NAVY
            
            if ':' in clean_bullet:
                head, desc = clean_bullet.split(':', 1)
                r_head = p.add_run(head + ":")
                r_head.font.name = "Calibri"
                r_head.font.size = Pt(10.5)
                r_head.font.bold = True
                r_head.font.color.rgb = COLOR_NAVY
                parse_runs_into_paragraph(p, " " + desc.strip(), default_font_size=10.5, default_color=COLOR_BODY)
            else:
                parse_runs_into_paragraph(p, clean_bullet, default_font_size=10.5, default_color=COLOR_BODY)
            i += 1
            continue
            
        # Indented sub-bullets
        if line.startswith('  ') or line.startswith('   '):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.5)
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2.5)
            p.paragraph_format.line_spacing = 1.15
            
            clean_sub = line.strip()
            if ':' in clean_sub:
                sub_head, sub_desc = clean_sub.split(':', 1)
                r_sh = p.add_run(sub_head + ": ")
                r_sh.font.name = "Calibri"
                r_sh.font.size = Pt(10.0)
                r_sh.font.bold = True
                r_sh.font.color.rgb = COLOR_SLATE_NAVY
                parse_runs_into_paragraph(p, sub_desc.strip(), default_font_size=10.0, default_color=COLOR_BODY)
            else:
                parse_runs_into_paragraph(p, clean_sub, default_font_size=10.0, default_color=COLOR_BODY)
            i += 1
            continue
            
        # Quotes
        if "The Qur'an commands in Surah An-Nisa" in line or "The Prophet, peace be upon him" in line:
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.35)
            p.paragraph_format.right_indent = Inches(0.2)
            p.paragraph_format.space_before = Pt(5)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.15
            
            pBdr = parse_xml(f'''
                <w:pBdr {nsdecls("w")}>
                    <w:left w:val="single" w:sz="14" w:space="8" w:color="{MUTED_GRAY_HEX}"/>
                </w:pBdr>
            ''')
            p._p.get_or_add_pPr().append(pBdr)
            parse_runs_into_paragraph(p, line, default_font_size=10.5, default_color=COLOR_DARK_SLATE, default_italic=False)
            i += 1
            continue
            
        # Labeled paragraphs
        if line.startswith('The claim:') or line.startswith('The proof:') or line.startswith('The rule:') or line.startswith('Model Proof:'):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(5)
            p.paragraph_format.space_after = Pt(5)
            p.paragraph_format.line_spacing = 1.15
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            
            lbl, rest = line.split(':', 1)
            r_lbl = p.add_run(lbl + ":")
            r_lbl.font.name = "Calibri"
            r_lbl.font.size = Pt(10.5)
            r_lbl.font.bold = True
            
            if lbl == 'The rule':
                r_lbl.font.color.rgb = COLOR_TEAL
            elif lbl == 'Model Proof':
                r_lbl.font.color.rgb = COLOR_INDIGO
            else:
                r_lbl.font.color.rgb = COLOR_NAVY
                
            parse_runs_into_paragraph(p, " " + rest.strip(), default_font_size=10.5, default_color=COLOR_BODY)
            i += 1
            continue
            
        # Defenses & Refutations
        if line.startswith('The first defense:') or line.startswith('The second defense:') or line.startswith('The third defense:') or line.startswith('The fourth defense:'):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.keep_with_next = True
            
            lbl, quote = line.split(':', 1)
            r_d = p.add_run(lbl + ": ")
            r_d.font.name = "Calibri"
            r_d.font.size = Pt(11.0)
            r_d.font.bold = True
            r_d.font.color.rgb = COLOR_DARK_SLATE
            
            r_q = p.add_run(quote.strip())
            r_q.font.name = "Calibri"
            r_q.font.size = Pt(10.5)
            r_q.font.italic = True
            r_q.font.color.rgb = COLOR_NAVY
            i += 1
            continue
            
        if line.startswith('The refutation:'):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(5)
            p.paragraph_format.line_spacing = 1.15
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            
            lbl, ref_text = line.split(':', 1)
            r_ref = p.add_run(lbl + ": ")
            r_ref.font.name = "Calibri"
            r_ref.font.size = Pt(10.5)
            r_ref.font.bold = True
            r_ref.font.color.rgb = COLOR_CRIMSON
            
            parse_runs_into_paragraph(p, ref_text.strip(), default_font_size=10.5, default_color=COLOR_BODY)
            i += 1
            continue
            
        # Numbered items
        if re.match(r'^\d+\.\s+', line):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.15
            
            num_match = re.match(r'^(\d+\.)\s+(.*)', line)
            num_str = num_match.group(1)
            rest_str = num_match.group(2)
            
            r_num = p.add_run(num_str + " ")
            r_num.font.name = "Calibri"
            r_num.font.size = Pt(10.5)
            r_num.font.bold = True
            r_num.font.color.rgb = COLOR_SLATE_NAVY
            
            parse_runs_into_paragraph(p, rest_str, default_font_size=10.5, default_color=COLOR_BODY)
            i += 1
            continue
            
        # Standard Body Paragraph
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        parse_runs_into_paragraph(p, line, default_font_size=10.5, default_color=COLOR_BODY)
        i += 1
        
    print(f"[EN] Saving generated document to: {output_docx_path}")
    doc.save(output_docx_path)
    file_size = os.path.getsize(output_docx_path)
    print(f"[EN] Successfully created! File size: {file_size} bytes")

def generate_docx_tr(input_md_path, output_docx_path):
    if not os.path.exists(input_md_path):
        return
    print(f"[TR] Reading from: {input_md_path}")
    with open(input_md_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    doc = Document()
    setup_page_layout(doc, lang='tr')
    build_cover_header(doc, lang='tr')
    
    lines = content.split('\n')
    i = 0
    total_lines = len(lines)
    
    while i < total_lines:
        line = lines[i].strip()
        if not line or line.startswith('# ') or line == '---':
            i += 1
            continue
            
        # Stage direction / slide callout
        if line.startswith('*(') and line.endswith(')*'):
            add_callout_box(doc, line, lang='tr')
            i += 1
            continue
            
        # Mathematical Specification Block
        if 'Matematiksel İspat' in line or 'Aksiyomlar' in line:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.keep_with_next = True
            r = p.add_run(line)
            r.font.name = "Calibri"
            r.font.size = Pt(11.0)
            r.font.bold = True
            r.font.color.rgb = COLOR_SLATE_NAVY
            i += 1
            continue
            
        # Main Heading 1
        if line.startswith('MODEL ') or line.startswith('KÖK TAVSİF') or line.startswith('NETİCE.') or line.startswith('ÜRETİCİ SAVUNMALARI'):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(16)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            
            run = p.add_run(line)
            run.font.name = "Calibri"
            run.font.size = Pt(13.0)
            run.font.bold = True
            run.font.color.rgb = COLOR_NAVY
            
            pBdr = parse_xml(f'''
                <w:pBdr {nsdecls("w")}>
                    <w:bottom w:val="single" w:sz="6" w:space="2" w:color="{BORDER_GRAY_HEX}"/>
                </w:pBdr>
            ''')
            p._p.get_or_add_pPr().append(pBdr)
            i += 1
            continue
            
        # Evidence Heading 2
        if 'DELİLİMİZ:' in line or 'DELİL:' in line:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(13)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.keep_with_next = True
            
            run = p.add_run(line)
            run.font.name = "Calibri"
            run.font.size = Pt(11.5)
            run.font.bold = True
            run.font.color.rgb = COLOR_SLATE_NAVY
            i += 1
            continue
            
        # Section headings
        if line.startswith('Aktörler ve') or line.startswith('Yapısal ve') or line.startswith('İşte değişkenler'):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.keep_with_next = True
            
            run = p.add_run(line)
            run.font.name = "Calibri"
            run.font.size = Pt(11.0)
            run.font.bold = True
            run.font.color.rgb = COLOR_DARK_SLATE
            i += 1
            continue
            
        # Bullet lists
        if line.startswith('* '):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.15
            
            clean_bullet = line[2:].strip()
            r_b = p.add_run("•  ")
            r_b.font.name = "Calibri"
            r_b.font.size = Pt(10.5)
            r_b.font.bold = True
            r_b.font.color.rgb = COLOR_SLATE_NAVY
            
            if ':' in clean_bullet:
                head, desc = clean_bullet.split(':', 1)
                r_head = p.add_run(head + ":")
                r_head.font.name = "Calibri"
                r_head.font.size = Pt(10.5)
                r_head.font.bold = True
                r_head.font.color.rgb = COLOR_NAVY
                parse_runs_into_paragraph(p, " " + desc.strip(), default_font_size=10.5, default_color=COLOR_BODY)
            else:
                parse_runs_into_paragraph(p, clean_bullet, default_font_size=10.5, default_color=COLOR_BODY)
            i += 1
            continue
            
        # Indented sub-bullets
        if line.startswith('  ') or line.startswith('   '):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.5)
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2.5)
            p.paragraph_format.line_spacing = 1.15
            
            clean_sub = line.strip()
            if ':' in clean_sub:
                sub_head, sub_desc = clean_sub.split(':', 1)
                r_sh = p.add_run(sub_head + ": ")
                r_sh.font.name = "Calibri"
                r_sh.font.size = Pt(10.0)
                r_sh.font.bold = True
                r_sh.font.color.rgb = COLOR_SLATE_NAVY
                parse_runs_into_paragraph(p, sub_desc.strip(), default_font_size=10.0, default_color=COLOR_BODY)
            else:
                parse_runs_into_paragraph(p, clean_sub, default_font_size=10.0, default_color=COLOR_BODY)
            i += 1
            continue
            
        # Labeled paragraphs
        if line.startswith('İddia:') or line.startswith('İspat:') or line.startswith('Hüküm:') or line.startswith('Model İspatı:') or line.startswith('Model İspat:'):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(5)
            p.paragraph_format.space_after = Pt(5)
            p.paragraph_format.line_spacing = 1.15
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            
            lbl, rest = line.split(':', 1)
            r_lbl = p.add_run(lbl + ":")
            r_lbl.font.name = "Calibri"
            r_lbl.font.size = Pt(10.5)
            r_lbl.font.bold = True
            
            if 'Hüküm' in lbl:
                r_lbl.font.color.rgb = COLOR_TEAL
            elif 'Model' in lbl:
                r_lbl.font.color.rgb = COLOR_INDIGO
            else:
                r_lbl.font.color.rgb = COLOR_NAVY
                
            parse_runs_into_paragraph(p, " " + rest.strip(), default_font_size=10.5, default_color=COLOR_BODY)
            i += 1
            continue
            
        # Savunma & İptal
        if 'savunma:' in line.lower() or 'savunması:' in line.lower():
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.keep_with_next = True
            
            if ':' in line:
                lbl, quote = line.split(':', 1)
                r_d = p.add_run(lbl + ": ")
                r_d.font.name = "Calibri"
                r_d.font.size = Pt(11.0)
                r_d.font.bold = True
                r_d.font.color.rgb = COLOR_DARK_SLATE
                
                r_q = p.add_run(quote.strip())
                r_q.font.name = "Calibri"
                r_q.font.size = Pt(10.5)
                r_q.font.italic = True
                r_q.font.color.rgb = COLOR_NAVY
            else:
                parse_runs_into_paragraph(p, line, default_font_size=10.5, default_color=COLOR_DARK_SLATE)
            i += 1
            continue
            
        if line.startswith('İptal ve Red:') or line.startswith('İptal:') or line.startswith('Red:'):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(5)
            p.paragraph_format.line_spacing = 1.15
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            
            lbl, ref_text = line.split(':', 1)
            r_ref = p.add_run(lbl + ": ")
            r_ref.font.name = "Calibri"
            r_ref.font.size = Pt(10.5)
            r_ref.font.bold = True
            r_ref.font.color.rgb = COLOR_CRIMSON
            
            parse_runs_into_paragraph(p, ref_text.strip(), default_font_size=10.5, default_color=COLOR_BODY)
            i += 1
            continue
            
        # Numbered items
        if re.match(r'^\d+\.\s+', line):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.15
            
            num_match = re.match(r'^(\d+\.)\s+(.*)', line)
            num_str = num_match.group(1)
            rest_str = num_match.group(2)
            
            r_num = p.add_run(num_str + " ")
            r_num.font.name = "Calibri"
            r_num.font.size = Pt(10.5)
            r_num.font.bold = True
            r_num.font.color.rgb = COLOR_SLATE_NAVY
            
            parse_runs_into_paragraph(p, rest_str, default_font_size=10.5, default_color=COLOR_BODY)
            i += 1
            continue
            
        # Standard Body Paragraph
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        parse_runs_into_paragraph(p, line, default_font_size=10.5, default_color=COLOR_BODY)
        i += 1
        
    print(f"[TR] Saving generated document to: {output_docx_path}")
    doc.save(output_docx_path)
    file_size = os.path.getsize(output_docx_path)
    print(f"[TR] Successfully created! File size: {file_size} bytes")

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    in_en = os.path.join(base_dir, 'docs', 'planli_eskitme_hitabet_metni_en.md')
    out_en = os.path.join(base_dir, 'docs', 'planli_eskitme_hitabet_metni_en.docx')
    generate_docx_en(in_en, out_en)
    
    in_tr = os.path.join(base_dir, 'docs', 'planli_eskitme_hitabet_metni_tr.md')
    out_tr = os.path.join(base_dir, 'docs', 'planli_eskitme_hitabet_metni_tr.docx')
    generate_docx_tr(in_tr, out_tr)
