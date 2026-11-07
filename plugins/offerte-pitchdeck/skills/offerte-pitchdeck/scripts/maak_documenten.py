#!/usr/bin/env python3
"""Maakt een offerte (docx) en een pitchdeck (pptx) uit één JSON-bestand.

Gebruik:
    python3 maak_documenten.py <offerte.json> <uitvoermap>

Het script rekent zelf de bedragen uit (subtotaal, btw per tarief, totaal),
zodat er in de offerte geen rekenfouten komen. Het verzint niets: wat in de
JSON ontbreekt, komt als [INVULLEN: ...] in de documenten.

Nodig: python-docx en python-pptx
    python3 -m pip install --user python-docx python-pptx
"""
import json
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP

try:
    from docx import Document
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Pt, RGBColor as DocxRGB, Cm
    from pptx import Presentation
    from pptx.dml.color import RGBColor as PptxRGB
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.enum.text import PP_ALIGN
    from pptx.util import Inches, Pt as PPt
except ImportError:
    sys.exit(
        "python-docx of python-pptx ontbreekt. Installeer met:\n"
        "  python3 -m pip install --user python-docx python-pptx"
    )

INVUL = "[INVULLEN: {}]"



def KOP(o, u_vorm, je_vorm):
    """Kop in de aanspreekvorm uit de offerte ("u" of "je"; standaard u)."""
    return je_vorm if str(o.get("aanspreekvorm", "u")).strip().lower() == "je" else u_vorm

def hexkleur(waarde, standaard):
    w = (waarde or standaard).lstrip("#")
    if not re.fullmatch(r"[0-9a-fA-F]{6}", w):
        w = standaard.lstrip("#")
    return tuple(int(w[i : i + 2], 16) for i in (0, 2, 4))


def geld(bedrag):
    """€ 1.234,50"""
    q = Decimal(bedrag).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    heel, dec = f"{q:,.2f}".split(".")
    return f"€ {heel.replace(',', '.')},{dec}"


def tekst(waarde, wat):
    return waarde if waarde not in (None, "", []) else INVUL.format(wat)


def bereken(regels):
    rijen, subtotaal, per_tarief = [], Decimal(0), {}
    for r in regels:
        prijs = r.get("prijs")
        aantal = Decimal(str(r.get("aantal", 1)))
        tarief = int(r.get("btw", 21))
        if prijs is None:
            rijen.append((r, aantal, None, tarief))
            continue
        bedrag = (Decimal(str(prijs)) * aantal).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        subtotaal += bedrag
        per_tarief[tarief] = per_tarief.get(tarief, Decimal(0)) + bedrag
        rijen.append((r, aantal, bedrag, tarief))
    btw = {t: (b * Decimal(t) / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) for t, b in per_tarief.items()}
    totaal = subtotaal + sum(btw.values(), Decimal(0))
    open_prijs = any(b is None for _, _, b, _ in rijen)
    return rijen, subtotaal, btw, totaal, open_prijs


def aantal_tekst(a):
    if a == a.to_integral():
        return str(int(a))
    return format(a.normalize(), "f").replace(".", ",")


# ---------------------------------------------------------------- offerte (docx)

def cel_kleur(cel, rgb):
    tcPr = cel._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), "%02X%02X%02X" % rgb)
    tcPr.append(shd)


def maak_offerte(d, rijen, subtotaal, btw, totaal, open_prijs, pad):
    stijl = d.get("huisstijl", {})
    prim = hexkleur(stijl.get("primair"), "#1B2A4A")
    acc = hexkleur(stijl.get("accent"), "#F28C28")
    font = stijl.get("lettertype") or "Calibri"
    b, k, o = d.get("bedrijf", {}), d.get("klant", {}), d.get("offerte", {})

    doc = Document()
    for s in doc.sections:
        s.left_margin = s.right_margin = Cm(2.2)
        s.top_margin = s.bottom_margin = Cm(2)
    normaal = doc.styles["Normal"]
    normaal.font.name = font
    normaal.font.size = Pt(10.5)
    for naam in ("Heading 1", "Heading 2"):
        h = doc.styles[naam]
        h.font.name = font
        h.font.color.rgb = DocxRGB(*prim)
        h.font.bold = True
    doc.styles["Heading 1"].font.size = Pt(20)
    doc.styles["Heading 2"].font.size = Pt(13)

    # Kop met logo en afzender
    kop = doc.add_table(rows=1, cols=2)
    links, rechts = kop.rows[0].cells
    logo = stijl.get("logo")
    if logo and os.path.isfile(os.path.expanduser(logo)):
        links.paragraphs[0].add_run().add_picture(os.path.expanduser(logo), width=Cm(3))
    else:
        r = links.paragraphs[0].add_run(tekst(b.get("naam"), "bedrijfsnaam"))
        r.bold, r.font.size, r.font.color.rgb = True, Pt(16), DocxRGB(*prim)
    regels_afzender = [b.get("naam"), b.get("adres"), b.get("postcode_plaats"), b.get("email"), b.get("telefoon"), b.get("website")]
    p = rechts.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.add_run("\n".join(x for x in regels_afzender if x)).font.size = Pt(9)

    doc.add_paragraph()
    p = doc.add_paragraph()
    for regel in [k.get("bedrijf") or INVUL.format("bedrijf klant"), f"t.a.v. {tekst(k.get('contact'), 'contactpersoon')}", k.get("adres"), k.get("postcode_plaats")]:
        if regel:
            p.add_run(regel + "\n")

    doc.add_heading(f"Offerte: {tekst(o.get('onderwerp'), 'onderwerp')}", level=1)
    meta = doc.add_table(rows=3, cols=2)
    for i, (l, w) in enumerate([("Offertenummer", tekst(o.get("nummer"), "nummer")), ("Datum", tekst(o.get("datum"), "datum")), ("Geldig tot", tekst(o.get("geldig_tot"), "geldig tot"))]):
        meta.cell(i, 0).text, meta.cell(i, 1).text = l, w
        meta.cell(i, 0).paragraphs[0].runs[0].bold = True

    doc.add_paragraph()
    doc.add_paragraph(f"Beste {tekst(o.get('aanhef_naam') or k.get('contact'), 'naam')},")
    doc.add_paragraph(tekst(o.get("inleiding"), "korte inleiding: dank voor het gesprek en waar deze offerte over gaat"))

    def blok(titel, items, wat):
        doc.add_heading(titel, level=2)
        if not items:
            doc.add_paragraph(INVUL.format(wat))
        for it in items or []:
            doc.add_paragraph(it, style="List Bullet")

    blok(KOP(o, "Uw situatie", "Jouw situatie"), o.get("situatie"), "situatie uit het gesprek")
    blok(KOP(o, "Wat u wilt bereiken", "Wat je wilt bereiken"), o.get("doelen"), "doelen van de klant")

    doc.add_heading("Onze aanpak", level=2)
    fases = o.get("aanpak") or []
    if not fases:
        doc.add_paragraph(INVUL.format("aanpak in fases"))
    for i, f in enumerate(fases, 1):
        p = doc.add_paragraph()
        r = p.add_run(f"{i}. {f.get('fase', '')}")
        r.bold = True
        if f.get("duur"):
            p.add_run(f"  ({f['duur']})").italic = True
        doc.add_paragraph(f.get("omschrijving", ""))

    if o.get("planning"):
        doc.add_heading("Planning", level=2)
        doc.add_paragraph(o["planning"])

    # Prijstabel
    doc.add_heading("Investering", level=2)
    t = doc.add_table(rows=1, cols=4)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for cel, kop_t in zip(t.rows[0].cells, ["Omschrijving", "Aantal", "Prijs", "Bedrag"]):
        cel.text = kop_t
        cel_kleur(cel, prim)
        run = cel.paragraphs[0].runs[0]
        run.bold, run.font.color.rgb = True, DocxRGB(255, 255, 255)
    for r, aantal, bedrag, tarief in rijen:
        cellen = t.add_row().cells
        cellen[0].text = r.get("omschrijving", "")
        cellen[1].text = f"{aantal_tekst(aantal)} {r.get('eenheid', '')}".strip()
        cellen[2].text = geld(r["prijs"]) if r.get("prijs") is not None else INVUL.format("prijs")
        cellen[3].text = geld(bedrag) if bedrag is not None else INVUL.format("bedrag")
    def somregel(label, waarde, vet=False):
        cellen = t.add_row().cells
        cellen[0].merge(cellen[2])
        cellen[0].text, cellen[3].text = label, waarde
        if vet:
            for c in (cellen[0], cellen[3]):
                c.paragraphs[0].runs[0].bold = True
                cel_kleur(c, (0xF2, 0xF2, 0xF2))
    extra = " (zonder open posten)" if open_prijs else ""
    somregel("Subtotaal excl. btw" + extra, geld(subtotaal))
    for tarief in sorted(btw):
        somregel(f"Btw {tarief}%", geld(btw[tarief]))
    somregel("Totaal incl. btw" + extra, geld(totaal), vet=True)
    for rij in t.rows:
        for c, breedte in zip(rij.cells, (Cm(8.5), Cm(2.5), Cm(2.8), Cm(3))):
            c.width = breedte
        for c in rij.cells[1:]:
            for p in c.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if open_prijs:
        doc.add_paragraph(INVUL.format("niet alle prijzen staan in de prijslijst; totaal is nog niet compleet"))

    blok("Voorwaarden", o.get("voorwaarden"), "voorwaarden")

    doc.add_heading("Volgende stap", level=2)
    doc.add_paragraph(tekst(o.get("volgende_stap"), "volgende stap"))
    doc.add_paragraph()
    doc.add_paragraph("Akkoord namens " + tekst(k.get("bedrijf"), "bedrijf klant") + ":")
    doc.add_paragraph("Naam: ______________________    Datum: ____________    Handtekening: ______________________")

    doc.add_paragraph()
    doc.add_paragraph(tekst(d.get("afsluiting"), "groet en naam"))

    voet = doc.sections[0].footer.paragraphs[0]
    voet.alignment = WD_ALIGN_PARAGRAPH.CENTER
    onderdelen = [b.get("naam"), f"KvK {b['kvk']}" if b.get("kvk") else INVUL.format("KvK-nummer"),
                  f"btw {b['btw']}" if b.get("btw") else INVUL.format("btw-nummer"), f"IBAN {b['iban']}" if b.get("iban") else None]
    vr = voet.add_run(" · ".join(x for x in onderdelen if x))
    vr.font.size, vr.font.color.rgb = Pt(8), DocxRGB(*acc)
    doc.save(pad)


# ---------------------------------------------------------------- pitchdeck (pptx)

def maak_deck(d, rijen, subtotaal, btw, totaal, open_prijs, pad):
    stijl = d.get("huisstijl", {})
    prim = PptxRGB(*hexkleur(stijl.get("primair"), "#1B2A4A"))
    acc = PptxRGB(*hexkleur(stijl.get("accent"), "#F28C28"))
    font = stijl.get("lettertype") or "Calibri"
    wit, donker, grijs = PptxRGB(255, 255, 255), PptxRGB(0x22, 0x22, 0x22), PptxRGB(0x6B, 0x72, 0x80)
    b, k, o = d.get("bedrijf", {}), d.get("klant", {}), d.get("offerte", {})
    logo = stijl.get("logo")
    logo = os.path.expanduser(logo) if logo and os.path.isfile(os.path.expanduser(logo)) else None

    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    leeg = prs.slide_layouts[6]
    W, H = prs.slide_width, prs.slide_height

    def vlak(slide, x, y, w, h, kleur):
        s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
        s.fill.solid()
        s.fill.fore_color.rgb = kleur
        s.line.fill.background()
        return s

    def tekstvak(slide, x, y, w, h, regels, grootte=20, kleur=donker, vet=False, uitlijning=PP_ALIGN.LEFT):
        tb = slide.shapes.add_textbox(x, y, w, h)
        tf = tb.text_frame
        tf.word_wrap = True
        for i, regel in enumerate(regels if isinstance(regels, list) else [regels]):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = uitlijning
            r = p.add_run()
            r.text = regel
            r.font.size, r.font.bold, r.font.name = PPt(grootte), vet, font
            r.font.color.rgb = kleur
            p.space_after = PPt(grootte * 0.6)
        return tb

    def inhoud(titel, nummer):
        s = prs.slides.add_slide(leeg)
        vlak(s, 0, 0, Inches(0.25), H, acc)
        tekstvak(s, Inches(0.8), Inches(0.5), Inches(11), Inches(1), titel, 34, prim, True)
        vlak(s, Inches(0.8), Inches(1.45), Inches(1.2), Inches(0.07), acc)
        tekstvak(s, Inches(0.8), H - Inches(0.6), Inches(8), Inches(0.4), f"{b.get('naam', '')}  ·  {k.get('bedrijf', '')}", 11, grijs)
        tekstvak(s, W - Inches(1.3), H - Inches(0.6), Inches(0.8), Inches(0.4), str(nummer), 11, grijs, uitlijning=PP_ALIGN.RIGHT)
        if logo:
            s.shapes.add_picture(logo, W - Inches(2.3), Inches(0.45), height=Inches(0.7))
        return s

    def punten(titel, items, wat, nummer):
        s = inhoud(titel, nummer)
        items = items or [INVUL.format(wat)]
        y = Inches(2.0)
        for it in items[:5]:
            vlak(s, Inches(0.9), y + Inches(0.12), Inches(0.18), Inches(0.18), acc)
            tekstvak(s, Inches(1.3), y, Inches(11), Inches(0.9), it, 22)
            y += Inches(0.95)

    # 1 Titel
    s = prs.slides.add_slide(leeg)
    vlak(s, 0, 0, W, H, prim)
    vlak(s, Inches(0.8), Inches(3.55), Inches(1.6), Inches(0.09), acc)
    tekstvak(s, Inches(0.8), Inches(1.6), Inches(11.5), Inches(1.9), tekst(o.get("onderwerp"), "onderwerp"), 46, wit, True)
    tekstvak(s, Inches(0.8), Inches(3.9), Inches(11.5), Inches(1), f"Voorstel voor {tekst(k.get('bedrijf'), 'bedrijf klant')}", 24, wit)
    tekstvak(s, Inches(0.8), H - Inches(1.2), Inches(11.5), Inches(0.5), f"{b.get('naam', '')}  ·  {o.get('datum', '')}", 14, wit)
    if logo:
        s.shapes.add_picture(logo, W - Inches(2.6), Inches(0.6), height=Inches(0.9))

    # 2-3 Situatie en doelen
    punten(KOP(o, "Waar u nu staat", "Waar je nu staat"), o.get("situatie"), "situatie", 2)
    punten(KOP(o, "Wat u wilt bereiken", "Wat je wilt bereiken"), o.get("doelen"), "doelen", 3)

    # 4 Aanpak als fases naast elkaar
    s = inhoud("Onze aanpak", 4)
    fases = (o.get("aanpak") or [{"fase": INVUL.format("fase"), "omschrijving": ""}])[:4]
    breedte = (W - Inches(1.6) - Inches(0.3) * (len(fases) - 1)) / len(fases)
    for i, f in enumerate(fases):
        x = Inches(0.8) + i * (breedte + Inches(0.3))
        vlak(s, x, Inches(2.0), breedte, Inches(0.9), prim)
        tekstvak(s, x + Inches(0.15), Inches(2.1), breedte - Inches(0.3), Inches(0.8), f"{i + 1}. {f.get('fase', '')}", 18, wit, True)
        vlak(s, x, Inches(2.9), breedte, Inches(3.4), PptxRGB(0xF4, 0xF5, 0xF7))
        regels = [f.get("omschrijving", "")] + ([f"Duur: {f['duur']}"] if f.get("duur") else [])
        tekstvak(s, x + Inches(0.15), Inches(3.05), breedte - Inches(0.3), Inches(3.1), regels, 15)

    # 5 Planning
    punten("Planning", [o["planning"]] if o.get("planning") else o.get("planning_punten"), "planning", 5)

    # 6 Investering
    s = inhoud("Investering", 6)
    getoond = [r for r in rijen][:6]
    tabel = s.shapes.add_table(len(getoond) + 2, 2, Inches(0.8), Inches(2.0), Inches(8.2), Inches(0.5) * (len(getoond) + 2)).table
    tabel.columns[0].width, tabel.columns[1].width = Inches(5.9), Inches(2.3)
    def zet(cel, waarde, vet=False, kleur=donker, rechts=False):
        cel.text = waarde
        p = cel.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.RIGHT if rechts else PP_ALIGN.LEFT
        p.runs[0].font.size, p.runs[0].font.bold, p.runs[0].font.name = PPt(16), vet, font
        p.runs[0].font.color.rgb = kleur
    zet(tabel.cell(0, 0), "Onderdeel", True, wit)
    zet(tabel.cell(0, 1), "Bedrag", True, wit, True)
    for c in (tabel.cell(0, 0), tabel.cell(0, 1)):
        c.fill.solid(); c.fill.fore_color.rgb = prim
    for i, (r, aantal, bedrag, _) in enumerate(getoond, 1):
        zet(tabel.cell(i, 0), r.get("omschrijving", ""))
        zet(tabel.cell(i, 1), geld(bedrag) if bedrag is not None else INVUL.format("bedrag"), rechts=True)
        for c in (tabel.cell(i, 0), tabel.cell(i, 1)):
            c.fill.solid(); c.fill.fore_color.rgb = wit
    zet(tabel.cell(len(getoond) + 1, 0), "Totaal excl. btw" + (" (zonder open posten)" if open_prijs else ""), True)
    zet(tabel.cell(len(getoond) + 1, 1), geld(subtotaal), True, rechts=True)
    for c in (tabel.cell(len(getoond) + 1, 0), tabel.cell(len(getoond) + 1, 1)):
        c.fill.solid(); c.fill.fore_color.rgb = PptxRGB(0xF4, 0xF5, 0xF7)
    vlak(s, Inches(9.5), Inches(2.0), Inches(3.0), Inches(2.4), prim)
    tekstvak(s, Inches(9.7), Inches(2.2), Inches(2.6), Inches(0.5), "Totaal incl. btw" + (" *" if open_prijs else ""), 14, wit)
    tekstvak(s, Inches(9.7), Inches(2.75), Inches(2.6), Inches(0.8), geld(totaal), 28, wit, True)
    tekstvak(s, Inches(9.7), Inches(3.6), Inches(2.6), Inches(0.7), f"Geldig tot {tekst(o.get('geldig_tot'), 'datum')}", 12, wit)
    if open_prijs:
        tekstvak(s, Inches(9.5), Inches(4.6), Inches(3.0), Inches(1), "* " + INVUL.format("nog niet alle prijzen bekend"), 12, acc)

    # 7 Waarom wij
    punten(f"Waarom {b.get('naam') or 'wij'}", d.get("waarom_wij"), "waarom jullie", 7)

    # 8 Volgende stap
    s = prs.slides.add_slide(leeg)
    vlak(s, 0, 0, W, H, prim)
    tekstvak(s, Inches(0.8), Inches(1.8), Inches(11.5), Inches(1), "Volgende stap", 40, wit, True)
    vlak(s, Inches(0.8), Inches(2.9), Inches(1.6), Inches(0.09), acc)
    tekstvak(s, Inches(0.8), Inches(3.3), Inches(11.5), Inches(1.6), tekst(o.get("volgende_stap"), "volgende stap"), 24, wit)
    contact = "  ·  ".join(x for x in [b.get("contactpersoon"), b.get("email"), b.get("telefoon")] if x)
    tekstvak(s, Inches(0.8), H - Inches(1.3), Inches(11.5), Inches(0.6), contact, 16, wit)

    prs.save(pad)


def tel_invullen(pad_docx, pad_pptx):
    n = 0
    for p in Document(pad_docx).paragraphs:
        n += p.text.count("[INVULLEN")
    for t in Document(pad_docx).tables:
        for rij in t.rows:
            for c in rij.cells:
                n += c.text.count("[INVULLEN")
    m = 0
    for slide in Presentation(pad_pptx).slides:
        for sh in slide.shapes:
            if sh.has_text_frame:
                m += sh.text_frame.text.count("[INVULLEN")
            if sh.has_table:
                for rij in sh.table.rows:
                    for c in rij.cells:
                        m += c.text.count("[INVULLEN")
    return n, m


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    with open(sys.argv[1], encoding="utf-8") as f:
        d = json.load(f)
    uit = os.path.expanduser(sys.argv[2])
    os.makedirs(uit, exist_ok=True)
    rijen, subtotaal, btw, totaal, open_prijs = bereken(d.get("offerte", {}).get("regels", []))
    nr = re.sub(r"[^\w-]+", "-", str(d.get("offerte", {}).get("nummer") or "concept")).strip("-")
    pad_docx = os.path.join(uit, f"offerte-{nr}.docx")
    pad_pptx = os.path.join(uit, f"pitchdeck-{nr}.pptx")
    maak_offerte(d, rijen, subtotaal, btw, totaal, open_prijs, pad_docx)
    maak_deck(d, rijen, subtotaal, btw, totaal, open_prijs, pad_pptx)
    n, m = tel_invullen(pad_docx, pad_pptx)
    print(json.dumps({
        "offerte": pad_docx, "pitchdeck": pad_pptx,
        "subtotaal": geld(subtotaal), "btw": {f"{t}%": geld(v) for t, v in btw.items()}, "totaal": geld(totaal),
        "invullen_offerte": n, "invullen_deck": m, "prijs_ontbreekt": open_prijs,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
