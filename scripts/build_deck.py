"""
build_deck — monta um .pptx ACESSIVEL POR CONSTRUCAO a partir de um roteiro.

A ideia central: nao existe etapa de remediacao. Cada slide nasce com
placeholder de titulo real, titulo unico, lang="pt-BR" em todo run, contraste
calculado antes de escrever, entrelinha 1,5, alinhamento a esquerda, tabela com
linha de cabecalho, elemento estetico marcado como decorativo e ordem de leitura
igual ao fluxo visual.

    python scripts/build_deck.py roteiro.yaml -o deck.pptx
    python scripts/build_deck.py roteiro.yaml -o deck.pptx --modos

O roteiro e YAML (ou JSON). Ver exemplos/roteiro-exemplo.yaml.

REGRA DE OURO: se uma figura nao tiver alt text E descricao longa, o build
FALHA. Nao existe figura sem descricao neste pipeline.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

import a11y_lib as A
import audit_contrast as C

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PALETA = os.path.join(RAIZ, "assets", "paleta-okabe-ito.json")

# Layouts do template padrao do python-pptx
LAYOUT_CAPA, LAYOUT_CONTEUDO, LAYOUT_SECAO, LAYOUT_SO_TITULO = 0, 1, 2, 5

LARGURA, ALTURA = Inches(13.333), Inches(7.5)
MARGEM = Inches(0.9)
ALVO_MIN_EMU = 228600  # 24 px CSS a 96 dpi (regra I07)


class ErroDeRoteiro(Exception):
    """O roteiro pede algo que produziria um slide inacessivel."""


# ==========================================================================
# Tema
# ==========================================================================
class Tema:
    """Cores e tipografia de um modo de exibicao."""

    def __init__(self, nome, fundo, texto, destaque, sobre_destaque, series):
        self.nome = nome
        self.fundo = fundo
        self.texto = texto
        self.destaque = destaque
        self.sobre_destaque = sobre_destaque
        self.series = series
        self.fonte = "Calibri"

    def rgb(self, hexv):
        return RGBColor.from_string(hexv.lstrip("#").upper())

    def contraste_texto(self):
        return C.contrast_ratio(C.hex_to_rgb(self.texto), C.hex_to_rgb(self.fundo))


def carregar_temas():
    with open(PALETA, encoding="utf-8") as f:
        p = json.load(f)
    marcas = {s["nome"]: s["marca_min_3_1"] for s in p["series"]}
    txt = {s["nome"]: s["texto_min_4_5_1"] for s in p["series"]}
    return {
        "padrao": Tema(
            "Modo padrão", p["fundos"]["padrao"], p["textos"]["sobre_claro"],
            txt["azul"], "#FFFFFF",
            [marcas["azul"], marcas["laranja"], marcas["verde_azulado"],
             marcas["roxo_avermelhado"]]),
        "alto_contraste": Tema(
            "Modo alto contraste", p["fundos"]["alto_contraste"],
            p["textos"]["sobre_escuro"], "#F0E442", "#000000",
            ["#56B4E9", "#E69F00", "#009E73", "#F0E442"]),
        "daltonico": Tema(
            "Modo daltônico-seguro", p["fundos"]["daltonico_seguro"],
            p["textos"]["sobre_claro"], txt["azul"], "#FFFFFF",
            [marcas["azul"], marcas["laranja"], marcas["cinza"], marcas["vermelhao"]]),
    }


# ==========================================================================
# Primitivas acessiveis
# ==========================================================================
def pintar_fundo(slide, tema):
    """Fundo solido explicito — evita branco puro (regra E08)."""
    cSld = slide._element.find(A.q("p:cSld"))
    antigo = cSld.find(A.q("p:bg"))
    if antigo is not None:
        cSld.remove(antigo)
    bg = etree.Element(A.q("p:bg"))
    bgPr = etree.SubElement(bg, A.q("p:bgPr"))
    fill = etree.SubElement(bgPr, A.q("a:solidFill"))
    clr = etree.SubElement(fill, A.q("a:srgbClr"))
    clr.set("val", tema.fundo.lstrip("#").upper())
    etree.SubElement(bgPr, A.q("a:effectLst"))
    cSld.insert(0, bg)


def formatar(tf, tema, tamanho, cor=None, negrito=False, entrelinha=150000):
    """
    Aplica tipografia acessivel a um text frame inteiro:
    tamanho explicito, sans-serif, cor com contraste, alinhamento a esquerda,
    entrelinha 1,5 e lang em todo run.
    """
    cor = cor or tema.texto
    for p in tf.paragraphs:
        p.alignment = PP_ALIGN.LEFT
        pPr = p._p.get_or_add_pPr()
        for antigo in pPr.findall(A.q("a:lnSpc")):
            pPr.remove(antigo)
        lnSpc = etree.Element(A.q("a:lnSpc"))
        etree.SubElement(lnSpc, A.q("a:spcPct")).set("val", str(entrelinha))
        pPr.insert(0, lnSpc)
        for r in p.runs:
            r.font.size = Pt(tamanho)
            r.font.name = tema.fonte
            r.font.bold = negrito
            r.font.color.rgb = tema.rgb(cor)
            rPr = r._r.find(A.q("a:rPr"))
            if rPr is not None:
                rPr.set("lang", "pt-BR")


def nomear(shape, nome):
    """Nome legivel no Painel de Selecao (regra C05)."""
    c = A.get_cNvPr(shape._element)
    if c is not None:
        c.set("name", nome)


def remover_placeholders_vazios(slide):
    """Placeholder vazio vira 'Clique para editar' fantasma e ruido no leitor."""
    for shape in list(slide.shapes):
        el = shape._element
        if A.get_ph(el) is None:
            continue
        texto = " ".join(A.paragraph_text(p) for p in A.iter_paragraphs(el)).strip()
        if not texto:
            el.getparent().remove(el)


# ==========================================================================
# Blocos de slide
# ==========================================================================
def _titulo(slide, texto, tema, tamanho=40):
    if slide.shapes.title is None:
        raise ErroDeRoteiro("layout sem placeholder de titulo")
    slide.shapes.title.text = texto
    nomear(slide.shapes.title, "Título do slide")
    formatar(slide.shapes.title.text_frame, tema, tamanho, negrito=True,
             entrelinha=110000)
    slide.shapes.title.text_frame.word_wrap = True


def _corpo(slide, linhas, tema, tamanho=22, idx=1):
    if not linhas:
        return None
    ph = slide.placeholders[idx]
    nomear(ph, "Conteúdo principal")
    tf = ph.text_frame
    tf.word_wrap = True
    tf.text = linhas[0]
    for l in linhas[1:]:
        tf.add_paragraph().text = l
    formatar(tf, tema, tamanho)
    return ph


def _resolver_arquivo(fig, modo):
    """
    'arquivo' pode ser um caminho unico ou um mapa por modo de exibicao.

    Diagrama gerado por HTML sai numa versao por paleta; cada modo recebe a
    sua, em vez de reaproveitar a versao clara sobre fundo preto.
    """
    arq = fig["arquivo"]
    if isinstance(arq, dict):
        return arq.get(modo) or arq.get("padrao") or next(iter(arq.values()))
    return arq


def _imagem(slide, fig, tema, esq, topo, larg, alt_, modo="padrao"):
    """Imagem com alt text obrigatorio e cartao de fundo nos modos escuros."""
    arq = _resolver_arquivo(fig, modo)
    if not os.path.exists(arq):
        raise ErroDeRoteiro("figura do modo %r nao encontrada: %s" % (modo, arq))
    if not fig.get("alt", "").strip():
        raise ErroDeRoteiro("figura sem alt text: %s" % arq)
    if not fig.get("descricao_longa", "").strip():
        raise ErroDeRoteiro("figura sem descricao longa: %s" % arq)

    # Em fundo escuro, a figura clara precisa de um cartao para nao "flutuar".
    if C.relative_luminance(C.hex_to_rgb(tema.fundo)) < 0.2:
        cartao = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, esq - Inches(0.12), topo - Inches(0.12),
            larg + Inches(0.24), alt_ + Inches(0.24))
        cartao.fill.solid()
        cartao.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        cartao.line.fill.background()
        cartao.shadow.inherit = False
        nomear(cartao, "Cartão de fundo da figura")
        A.set_decorative(cartao._element, True)

    pic = slide.shapes.add_picture(arq, esq, topo, larg, alt_)
    nomear(pic, fig.get("nome") or "Figura")
    A.set_alt_text(pic._element, fig["alt"].strip())
    return pic


def _tabela(slide, tab, tema, esq, topo, larg):
    cab = tab["cabecalho"]
    linhas = tab["linhas"]
    if not tab.get("alt", "").strip():
        raise ErroDeRoteiro("tabela sem alt text")
    if tab.get("tamanho", 18) < 18:
        raise ErroDeRoteiro(
            "tabela pedindo %dpt: celula tambem e texto e o piso e 18pt "
            "(regra F02). Tabela que so cabe menor e densa demais para um "
            "slide — reduza colunas ou quebre em duas" % tab["tamanho"])
    for l in linhas:
        if len(l) != len(cab):
            raise ErroDeRoteiro("linha com %d celulas para %d colunas"
                                % (len(l), len(cab)))
    altura = Inches(0.55) * (len(linhas) + 1)
    gf = slide.shapes.add_table(len(linhas) + 1, len(cab), esq, topo, larg, altura)
    nomear(gf, tab.get("nome") or "Tabela de dados")
    A.set_alt_text(gf._element, tab["alt"].strip())
    t = gf.table
    t.first_row = True
    if tab.get("primeira_coluna"):
        t.first_col = True
    for ci, v in enumerate(cab):
        cel = t.cell(0, ci)
        cel.text = str(v)
        cel.vertical_anchor = MSO_ANCHOR.MIDDLE
        formatar(cel.text_frame, tema, tab.get("tamanho", 18),
                 cor=tema.sobre_destaque, negrito=True, entrelinha=100000)
    for ri, linha in enumerate(linhas, 1):
        for ci, v in enumerate(linha):
            cel = t.cell(ri, ci)
            cel.text = str(v)
            cel.vertical_anchor = MSO_ANCHOR.MIDDLE
            formatar(cel.text_frame, tema, tab.get("tamanho", 18),
                     entrelinha=100000)
    return gf


def _validar_link(texto):
    """Texto de link tem de dizer para onde leva (regras H01/H02)."""
    if A.RE_URL.match(texto) or texto.strip().lower().strip(" .:;!?") in A.VAGUE_LINK:
        raise ErroDeRoteiro(
            "texto de link nao descritivo: %r — escreva o destino no proprio "
            "texto, como 'Diretrizes WCAG 2.2 do W3C'" % texto)


def _escrever_corpo(tf, linhas, links, tema, tamanho):
    """
    Escreve texto e links NO MESMO placeholder.

    Link em caixa de texto solta reprova em B05: caixa solta nao tem semantica.
    Como paragrafo do placeholder, o link herda a estrutura e o alvo de clique
    passa a ser a area do placeholder, bem acima dos 24x24 px CSS da regra I07.
    """
    primeiro = True
    for l in linhas:
        if primeiro:
            tf.text = l
            primeiro = False
        else:
            tf.add_paragraph().text = l

    runs_link = []
    for lk in links:
        _validar_link(lk["texto"])
        par = tf.paragraphs[0] if primeiro else tf.add_paragraph()
        primeiro = False
        r = par.add_run()
        r.text = lk["texto"]
        r.hyperlink.address = lk["url"]
        runs_link.append(r)

    formatar(tf, tema, tamanho)
    for r in runs_link:
        r.font.color.rgb = tema.rgb(tema.destaque)
        r.font.underline = True  # nunca so pela cor (regra E10)


def _rodape_decorativo(slide, tema):
    faixa = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0),
                                   ALTURA - Inches(0.18), LARGURA, Inches(0.18))
    faixa.fill.solid()
    faixa.fill.fore_color.rgb = tema.rgb(tema.destaque)
    faixa.line.fill.background()
    faixa.shadow.inherit = False
    nomear(faixa, "Faixa estética do rodapé")
    A.set_decorative(faixa._element, True)


# ==========================================================================
# Montagem de um slide
# ==========================================================================
def montar_slide(prs, spec, tema, sufixo="", modo="padrao"):
    tipo = spec.get("tipo", "conteudo")
    titulo = spec["titulo"] + sufixo

    if tipo == "capa":
        slide = prs.slides.add_slide(prs.slide_layouts[LAYOUT_CAPA])
        pintar_fundo(slide, tema)
        _titulo(slide, titulo, tema, 48)
        sub = spec.get("subtitulo", "")
        if sub:
            linhas = sub if isinstance(sub, list) else [sub]
            ph = slide.placeholders[1]
            nomear(ph, "Subtítulo")
            ph.text_frame.word_wrap = True
            _escrever_corpo(ph.text_frame, linhas, [], tema, 22)
    elif tipo == "secao":
        slide = prs.slides.add_slide(prs.slide_layouts[LAYOUT_SECAO])
        pintar_fundo(slide, tema)
        _titulo(slide, titulo, tema, 44)
        if spec.get("conteudo"):
            _corpo(slide, spec["conteudo"], tema, 20)
    else:
        tem_figura = bool(spec.get("figura"))
        tem_tabela = bool(spec.get("tabela"))
        # SEMPRE o layout com placeholder de conteudo. Usar "So Titulo" e
        # desenhar caixas de texto por cima e exatamente o erro que a regra
        # B05 existe para pegar; o placeholder e redimensionado no lugar.
        slide = prs.slides.add_slide(prs.slide_layouts[LAYOUT_CONTEUDO])
        pintar_fundo(slide, tema)
        _titulo(slide, titulo, tema, 36)

        topo = Inches(1.85)
        linhas = spec.get("conteudo", [])
        links = spec.get("links", [])
        larg_corpo = Inches(5.4) if tem_figura else LARGURA - 2 * MARGEM
        alt_corpo = Inches(1.7) if tem_tabela else Inches(4.3)

        corpo = slide.placeholders[1]
        nomear(corpo, "Conteúdo principal")
        corpo.left, corpo.top = MARGEM, topo
        corpo.width, corpo.height = larg_corpo, alt_corpo
        corpo.text_frame.word_wrap = True
        _escrever_corpo(corpo.text_frame, linhas, links, tema,
                        spec.get("tamanho", 22))

        # A ordem de insercao (titulo, corpo, figura/tabela) ja e o fluxo
        # visual esquerda->direita, cima->baixo (regra C02).
        if tem_figura:
            esq = MARGEM + larg_corpo + Inches(0.4) if (linhas or links) else Inches(3.2)
            _imagem(slide, spec["figura"], tema, esq, topo,
                    LARGURA - esq - MARGEM, Inches(3.6), modo)
        if tem_tabela:
            topo_tab = topo + alt_corpo + Inches(0.2) if (linhas or links) else topo
            _tabela(slide, spec["tabela"], tema, MARGEM, topo_tab,
                    LARGURA - 2 * MARGEM)

    remover_placeholders_vazios(slide)
    _rodape_decorativo(slide, tema)

    notas = spec.get("notas", "")
    fig = spec.get("figura")
    if fig and fig.get("descricao_longa"):
        longa = "Descrição da figura: " + fig["descricao_longa"].strip()
        notas = (notas + "\n\n" + longa).strip() if notas else longa
    if notas:
        slide.notes_slide.notes_text_frame.text = notas

    return slide


# ==========================================================================
# Roteiro
# ==========================================================================
def carregar_roteiro(caminho):
    with open(caminho, encoding="utf-8") as f:
        bruto = f.read()
    if caminho.lower().endswith((".yaml", ".yml")):
        try:
            import yaml
        except ImportError:
            raise ErroDeRoteiro(
                "roteiro em YAML exige PyYAML. Rode: pip install pyyaml "
                "(ou converta o roteiro para .json)")
        return yaml.safe_load(bruto)
    return json.loads(bruto)


def validar_roteiro(r):
    """Falha cedo e com mensagem util, antes de gerar qualquer coisa."""
    if "apresentacao" not in r or "slides" not in r:
        raise ErroDeRoteiro("roteiro precisa das chaves 'apresentacao' e 'slides'")
    ap = r["apresentacao"]
    for campo in ("titulo", "autor"):
        if not str(ap.get(campo, "")).strip():
            raise ErroDeRoteiro("apresentacao.%s e obrigatorio (regra A01/A04)" % campo)
    vistos = {}
    for i, s in enumerate(r["slides"], 1):
        t = str(s.get("titulo", "")).strip()
        if not t:
            raise ErroDeRoteiro("slide %d sem titulo (regra B01/B02)" % i)
        if t.lower() in vistos:
            raise ErroDeRoteiro(
                "titulo repetido nos slides %d e %d: %r — use sufixo de "
                "continuidade, como '(1 de 2)' (regra B03)"
                % (vistos[t.lower()], i, t))
        vistos[t.lower()] = i
        if len(s.get("conteudo", [])) > 6:
            raise ErroDeRoteiro(
                "slide %d com %d paragrafos; o limite e 6 (regra F07)"
                % (i, len(s["conteudo"])))


# ==========================================================================
# Construcao
# ==========================================================================
def construir(roteiro, saida, com_modos=False):
    validar_roteiro(roteiro)
    temas = carregar_temas()
    ap = roteiro["apresentacao"]

    prs = Presentation()
    prs.slide_width, prs.slide_height = LARGURA, ALTURA

    modos = ["padrao"]
    if com_modos:
        modos += ["alto_contraste", "daltonico"]

    indices = {}
    if com_modos:
        hub = _montar_hub(prs, temas["padrao"], modos, temas)

    for modo in modos:
        tema = temas[modo]
        sufixo = "" if modo == "padrao" else " · %s" % tema.nome.replace("Modo ", "")
        primeiro = len(prs.slides._sldIdLst)
        for spec in roteiro["slides"]:
            montar_slide(prs, spec, tema, sufixo, modo)
        indices[modo] = (primeiro, len(prs.slides._sldIdLst) - 1)

    cp = prs.core_properties
    cp.title = ap["titulo"]
    cp.author = ap["autor"]
    cp.language = ap.get("idioma", "pt-BR")
    cp.subject = ap.get("assunto", "")
    cp.keywords = ap.get("palavras_chave", "")
    cp.comments = ap.get("resumo", "")

    prs.save(saida)

    if com_modos:
        _gravar_secoes(saida, indices, temas)
    return indices


def _montar_hub(prs, tema, modos, temas):
    """Slide-hub com um item por modo. Sem macro, sem caixa de texto solta."""
    slide = prs.slides.add_slide(prs.slide_layouts[LAYOUT_CONTEUDO])
    pintar_fundo(slide, tema)
    _titulo(slide, "Escolha o modo de exibição", tema, 40)

    rotulos = {"padrao": "Modo padrão",
               "alto_contraste": "Modo alto contraste",
               "daltonico": "Modo daltônico-seguro"}
    descr = {"padrao": "fundo off-white e texto quase-preto, contraste 16,3:1",
             "alto_contraste": "fundo preto e texto branco, contraste 21:1",
             "daltonico": "paleta com matizes maximamente separados"}

    corpo = slide.placeholders[1]
    nomear(corpo, "Modos disponíveis")
    corpo.left, corpo.top = MARGEM, Inches(1.9)
    corpo.width, corpo.height = LARGURA - 2 * MARGEM, Inches(4.4)
    tf = corpo.text_frame
    tf.word_wrap = True
    linhas = ["Os três modos têm o mesmo conteúdo. Muda só a paleta.",
              "Use as seções do arquivo para ir ao modo que enxergar melhor."]
    linhas += ["%s — %s" % (rotulos[m], descr[m]) for m in modos]
    _escrever_corpo(tf, linhas, [], tema, 20)
    return slide


def _gravar_secoes(caminho, indices, temas):
    """Escreve p14:sectionLst — uma secao por modo (regra B07/B08)."""
    import shutil
    import zipfile
    from uuid import uuid4

    tmp = caminho + ".tmp"
    with zipfile.ZipFile(caminho) as zin:
        itens = {n: zin.read(n) for n in zin.namelist()}

    xml = itens["ppt/presentation.xml"].decode("utf-8")
    root = etree.fromstring(itens["ppt/presentation.xml"])
    sldIdLst = root.find(A.q("p:sldIdLst"))
    ids = [s.get("id") for s in sldIdLst]

    NS14 = "http://schemas.microsoft.com/office/powerpoint/2010/main"
    etree.register_namespace("p14", NS14)

    extLst = root.find(A.q("p:extLst"))
    if extLst is None:
        extLst = etree.SubElement(root, A.q("p:extLst"))
    ext = etree.SubElement(extLst, A.q("p:ext"))
    ext.set("uri", "{521415D9-36F7-43E2-AB2F-B90AF26B5E84}")
    secLst = etree.SubElement(ext, "{%s}sectionLst" % NS14)

    blocos = [("Hub de modos", 0, 0)]
    for modo, (ini, fim) in indices.items():
        blocos.append((temas[modo].nome, ini, fim))

    for nome, ini, fim in blocos:
        sec = etree.SubElement(secLst, "{%s}section" % NS14)
        sec.set("name", nome)
        sec.set("id", "{%s}" % str(uuid4()).upper())
        lst = etree.SubElement(sec, "{%s}sldIdLst" % NS14)
        for i in range(ini, fim + 1):
            if i < len(ids):
                etree.SubElement(lst, "{%s}sldId" % NS14).set("id", ids[i])

    itens["ppt/presentation.xml"] = etree.tostring(
        root, xml_declaration=True, encoding="UTF-8", standalone=True)

    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for nome, dados in itens.items():
            zout.writestr(nome, dados)
    shutil.move(tmp, caminho)


def main():
    ap = argparse.ArgumentParser(description="Constroi um .pptx acessivel")
    ap.add_argument("roteiro")
    ap.add_argument("-o", "--saida", default="deck.pptx")
    ap.add_argument("--modos", action="store_true",
                    help="gera hub + 3 modos de cor no mesmo arquivo")
    args = ap.parse_args()

    try:
        roteiro = carregar_roteiro(args.roteiro)
        indices = construir(roteiro, args.saida, args.modos)
    except ErroDeRoteiro as e:
        print("ERRO DE ROTEIRO: %s" % e)
        print("\nO build parou de proposito: gerar o arquivo assim produziria um")
        print("slide inacessivel. Corrija o roteiro, nao o .pptx.")
        return 2

    prs = Presentation(args.saida)
    print("gerado: %s" % args.saida)
    print("slides: %d" % len(prs.slides._sldIdLst))
    if args.modos:
        for modo, (i, f) in indices.items():
            print("  %-16s slides %d a %d" % (modo, i + 1, f + 1))
    print("\nAudite agora:")
    print("  python scripts/audit_pptx.py %s --md relatorio.md" % args.saida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
