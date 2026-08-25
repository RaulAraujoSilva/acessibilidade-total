"""
Gera tests/deck_bom.pptx — o deck de controle.

Serve para o teste inverso: um auditor que acusa tudo e tao inutil quanto um
que nao acusa nada. Aqui NAO pode sobrar Erro nem Aviso. O que aparecer e
falso positivo do auditor.

    python tests/make_deck_bom.py
    python tests/test_falso_positivo.py
"""
from __future__ import annotations

import os
import sys

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))

import a11y_lib as A  # noqa: E402

SAIDA = os.path.join(HERE, "deck_bom.pptx")

FUNDO = RGBColor(0xFA, 0xF7, 0xF2)
TEXTO = RGBColor(0x1A, 0x1A, 0x1A)


def png_solido(path, cor=(0, 114, 178), w=240, h=160):
    import struct
    import zlib
    raw = b"".join(b"\x00" + bytes(cor) * w for _ in range(h))

    def chunk(t, d):
        c = t + d
        return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c))

    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n"
                + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw, 9))
                + chunk(b"IEND", b""))
    return path


def pinta_fundo(slide, rgb=FUNDO):
    """Fundo solido explicito no slide (evita branco puro — regra E08)."""
    cSld = slide._element.find(A.q("p:cSld"))
    bg = etree.SubElement(cSld, A.q("p:bg"))
    cSld.remove(bg)
    cSld.insert(0, bg)
    bgPr = etree.SubElement(bg, A.q("p:bgPr"))
    fill = etree.SubElement(bgPr, A.q("a:solidFill"))
    clr = etree.SubElement(fill, A.q("a:srgbClr"))
    clr.set("val", "%02X%02X%02X" % (rgb[0], rgb[1], rgb[2]))
    etree.SubElement(bgPr, A.q("a:effectLst"))


def formata(tf, tamanho=24, titulo=False):
    for p in tf.paragraphs:
        p.alignment = PP_ALIGN.LEFT
        pPr = p._pPr if p._pPr is not None else p._p.get_or_add_pPr()
        lnSpc = etree.SubElement(pPr, A.q("a:lnSpc"))
        pct = etree.SubElement(lnSpc, A.q("a:spcPct"))
        pct.set("val", "150000")
        pPr.remove(lnSpc)
        pPr.insert(0, lnSpc)
        for r in p.runs:
            r.font.size = Pt(tamanho)
            r.font.name = "Calibri"
            r.font.color.rgb = TEXTO
            rPr = r._r.find(A.q("a:rPr"))
            if rPr is not None:
                rPr.set("lang", "pt-BR")


def main():
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    img = png_solido(os.path.join(HERE, "_fig_bom.png"))

    # -- slide 1 -----------------------------------------------------------
    s1 = prs.slides.add_slide(prs.slide_layouts[1])
    pinta_fundo(s1)
    s1.shapes.title.text = "Por que a estrutura vem antes da estética"
    s1.shapes.title.element.find(A.q("p:nvSpPr")).find(A.q("p:cNvPr")).set(
        "name", "Título do slide 1")
    formata(s1.shapes.title.text_frame, 40, titulo=True)

    corpo = s1.placeholders[1]
    A.get_cNvPr(corpo._element).set("name", "Argumento principal")
    tf = corpo.text_frame
    tf.text = "O leitor de tela navega pela hierarquia, não pelo desenho"
    p = tf.add_paragraph()
    p.text = "Placeholder carrega semântica; caixa de texto solta não carrega"
    formata(tf, 24)

    # figura com alt text de verdade
    pic = s1.shapes.add_picture(img, Inches(9.2), Inches(2.0), Inches(3.4), Inches(2.3))
    A.get_cNvPr(pic._element).set("name", "Diagrama da hierarquia")
    A.set_alt_text(pic._element, "Hierarquia de três níveis, do título ao "
                                 "conteúdo e às notas do orador")

    # faixa puramente estética, marcada como decorativa
    from pptx.enum.shapes import MSO_SHAPE
    faixa = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.1),
                                Inches(13.333), Inches(0.25))
    A.get_cNvPr(faixa._element).set("name", "Faixa estética do rodapé")
    A.set_decorative(faixa._element, True)

    # -- slide 2: tabela e link -------------------------------------------
    s2 = prs.slides.add_slide(prs.slide_layouts[1])
    pinta_fundo(s2)
    s2.shapes.title.text = "O que o verificador nativo não enxerga"
    A.get_cNvPr(s2.shapes.title._element).set("name", "Título do slide 2")
    formata(s2.shapes.title.text_frame, 40)

    # o link vai DENTRO do placeholder de conteúdo — caixa de texto solta
    # reprovaria em B05, e com razão
    ref = s2.placeholders[1]
    A.get_cNvPr(ref._element).set("name", "Referência normativa")
    ref.top, ref.left = Inches(1.75), Inches(0.9)
    ref.width, ref.height = Inches(8), Inches(0.8)
    r = ref.text_frame.paragraphs[0].add_run()
    r.text = "Diretrizes WCAG 2.2 do W3C"
    r.hyperlink.address = "https://www.w3.org/TR/WCAG22/"
    formata(ref.text_frame, 24)

    gf = s2.shapes.add_table(3, 2, Inches(0.9), Inches(3.2), Inches(7.4), Inches(2.4))
    A.get_cNvPr(gf._element).set("name", "Tabela de cobertura")
    A.set_alt_text(gf._element, "Comparação entre o que o verificador nativo "
                                "cobre e o que fica de fora")
    t = gf.table
    t.first_row = True
    dados = [["Camada", "Cobertura nativa"],
             ["Texto alternativo", "Presença, não qualidade"],
             ["Tipografia", "Nenhuma"]]
    for ri, linha in enumerate(dados):
        for ci, v in enumerate(linha):
            cel = t.cell(ri, ci)
            cel.text = v
            formata(cel.text_frame, 20)

    # -- metadados corretos ------------------------------------------------
    cp = prs.core_properties
    cp.title = "Acessibilidade estrutural em apresentações"
    cp.author = "Raul Araujo Silva"
    cp.language = "pt-BR"

    prs.save(SAIDA)
    os.remove(img)
    print("gerado:", SAIDA)


if __name__ == "__main__":
    main()
