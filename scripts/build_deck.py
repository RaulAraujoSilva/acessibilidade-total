"""
build_deck — monta um .pptx ACESSIVEL E BEM COMPOSTO a partir de um roteiro.

Duas ideias governam este arquivo:

1. Nao existe etapa de remediacao. O slide nasce com placeholder de titulo
   real, titulo unico, lang="pt-BR" em todo run, contraste calculado antes de
   escrever, tabela com cabecalho, elemento estetico marcado como decorativo.

2. Acessivel nao e desculpa para feio. Toda posicao vem da grade de
   scripts/grade.py, figura NUNCA e esticada, e nada entra na faixa do rodape.
   O modelo e assets/modelo-acessivel.pptx, gerado por gerar_modelo.py — o
   template padrao do Office trazia CAIXA ALTA no layout de secao e o corpo
   posicionado ACIMA do titulo.

    python scripts/build_deck.py roteiro.yaml -o deck.pptx --todos-os-modos

REGRA DE OURO: figura sem alt text E descricao longa faz o build FALHAR.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Pt

import a11y_lib as A
import grade as G

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PALETA = os.path.join(RAIZ, "assets", "paleta-okabe-ito.json")
MODELO = os.path.join(RAIZ, "assets", "modelo-acessivel.pptx")

# Um arquivo POR MODO e o padrao. O desenho anterior — hub e tres secoes no
# mesmo arquivo — punia exatamente quem navega em sequencia: de 85 slides, 57
# eram o mesmo conteudo em outra paleta, e a transcricao linear saia triplicada.
MODOS = ("padrao", "alto_contraste", "daltonico")
SUFIXO = {"padrao": "-padrao",
          "alto_contraste": "-alto-contraste",
          "daltonico": "-daltonico-seguro"}

# ------------------------------------------------------------------------
# O segundo eixo: PERFIL DE PUBLICO
#
# Modo de cor troca a paleta e nada mais. Perfil troca o REGISTRO do texto —
# e por isso precisa de um teste que o modo nao precisava, para nao virar
# "versao pior para deficiente". As cinco condicoes estao em
# references/10-versoes-por-publico.md e viram as regras O04 a O06.
#
# libras         quem tem Libras como PRIMEIRA lingua. A LBI 13.146/2015, no
#                art. 28 IV, fala em "Libras como primeira língua e na
#                modalidade escrita da língua portuguesa como segunda língua".
#                Texto reduzido a mensagem-chave e janela de Libras em TODO
#                slide, com a faixa reservada no layout.
# leitura_facil  deficiencia cognitiva e TDAH. Uma ideia por slide.
#                NAO ha norma brasileira de Leitura Facil — a NBR ISO 24495-1
#                e de Linguagem Simples e diz, por escrito, que sao coisas
#                diferentes. A referencia e Inclusion Europe e IFLA.
# ------------------------------------------------------------------------
PERFIS = ("completo", "libras", "leitura_facil")
SUFIXO_PERFIL = {"completo": "", "libras": "-libras",
                 "leitura_facil": "-leitura-facil"}
ROTULO_PERFIL = {
    "completo": "completo",
    "libras": "Libras como primeira língua",
    "leitura_facil": "leitura fácil",
}
# Colunas reservadas para a janela de Libras. Tres colunas dariam 7,39 cm, e a
# NBR 15290 (por analogia) pede no minimo 8,47 cm de largura: quatro colunas.
COLUNAS_LIBRAS = 4

# ------------------------------------------------------------------------
# QUE RECURSO VAI EM QUE PERFIL — o recurso segue o SENTIDO que ele serve.
#
# Este mapa corrige um erro de conceito que durou uma rodada. A regra O02
# ("recurso presente numa versao e ausente noutra") foi escrita para o eixo de
# COR, onde os tres arquivos tem de ser identicos. Aplicada ao eixo de PUBLICO
# ela vira o oposto do que pretende: obriga o deck de Libras a carregar 28
# faixas de audiodescricao — 13,7 dos 14,3 MB do arquivo — para um publico que
# nao as usa. Isso nao e paridade, e peso morto.
#
#   audiodescricao   serve quem NAO ENXERGA. Vai no perfil completo e no de
#                    leitura facil, onde a narracao apoia a compreensao.
#   janela de Libras serve quem tem Libras como PRIMEIRA LINGUA. No perfil
#                    libras ela vai em TODO slide; nos demais, na capa, como
#                    porta de entrada.
#
# A versao `completo` continua carregando TUDO: e a que nunca falta nada a
# ninguem, e e para ela que o LEIA-ME manda quem estiver em duvida.
# `todas_as_paletas`: quem nao ouve depende INTEIRAMENTE do canal visual, entao
# a versao em Libras tambem sai em alto contraste e em daltonico-seguro. A de
# leitura facil nao tem esse argumento — sai no modo padrao, e quem precisar de
# contraste tem as tres paletas da versao completa.
# `libras_na_capa` e False em toda parte, de proposito. A janela solta na capa
# dos demais arquivos era uma "porta de entrada" — e virava exatamente o que
# este projeto recusa: um selo. Uma janela num slide, num deck que nao tem
# Libras nos outros 27, nao serve a quem precisa de Libras, e ainda sugere que
# serve. Quem precisa da versao em Libras a encontra pelo LEIA-ME e pelo slide
# de acessibilidade, que a nomeiam.
RECURSOS = {
    "completo":      {"audio": True,  "libras_por_slide": False,
                      "libras_na_capa": False, "todas_as_paletas": True},
    "libras":        {"audio": False, "libras_por_slide": True,
                      "libras_na_capa": False, "todas_as_paletas": True},
    "leitura_facil": {"audio": True,  "libras_por_slide": False,
                      "libras_na_capa": False, "todas_as_paletas": False},
}


def recursos_do_perfil(perfil):
    return RECURSOS.get(perfil, RECURSOS["completo"])

# Corpo maior nos perfis de publico. Nao e enfeite: com uma ideia por slide,
# manter 24pt deixaria o slide vazio e o texto pequeno ao mesmo tempo — e a
# regra 6 da Inclusion Europe pede tipo grande em material de leitura facil.
TIPO_PERFIL = {"completo": None, "libras": 28, "leitura_facil": 30}


class ErroDeRoteiro(Exception):
    """O roteiro pede algo que sairia inacessivel ou mal composto."""


# ==========================================================================
# Tema
# ==========================================================================
class Tema:
    def __init__(self, nome, fundo, texto, destaque, sobre_destaque, series,
                 fundo_celula=None, cartao=None):
        self.nome = nome
        self.fundo = fundo
        self.fundo_celula = fundo_celula or fundo
        self.cartao = cartao or fundo_celula or fundo
        self.texto = texto
        self.destaque = destaque
        self.sobre_destaque = sobre_destaque
        self.series = series
        self.fonte = "Calibri"

    def rgb(self, hexv):
        return RGBColor.from_string(hexv.lstrip("#").upper())


def carregar_temas():
    with open(PALETA, encoding="utf-8") as f:
        p = json.load(f)
    marcas = {s["nome"]: s["marca_min_3_1"] for s in p["series"]}
    txt = {s["nome"]: s["texto_min_4_5_1"] for s in p["series"]}
    return {
        "padrao": Tema("Modo padrão", p["fundos"]["padrao"],
                       p["textos"]["sobre_claro"], txt["azul"], "#FFFFFF",
                       [marcas["azul"], marcas["laranja"],
                        marcas["verde_azulado"], marcas["roxo_avermelhado"]],
                       fundo_celula="#FFFFFF", cartao="#FFFFFF"),
        "alto_contraste": Tema("Modo alto contraste", "#000000", "#FFFFFF",
                               "#F0E442", "#000000",
                               ["#56B4E9", "#E69F00", "#009E73", "#F0E442"],
                               fundo_celula="#000000", cartao="#141414"),
        "daltonico": Tema("Modo daltônico-seguro", p["fundos"]["daltonico_seguro"],
                          p["textos"]["sobre_claro"], txt["azul"], "#FFFFFF",
                          [marcas["azul"], marcas["laranja"], marcas["cinza"],
                           marcas["vermelhao"]],
                          fundo_celula="#FFFFFF", cartao="#FFFFFF"),
    }


# ==========================================================================
# Primitivas
# ==========================================================================
def layout_por_nome(prs, nome):
    for lay in prs.slide_layouts:
        if (lay.name or "").strip().lower() == nome.lower():
            return lay
    raise ErroDeRoteiro("layout %r ausente do modelo — rode gerar_modelo.py" % nome)


def pintar_fundo(slide, tema):
    cSld = slide._element.find(A.q("p:cSld"))
    antigo = cSld.find(A.q("p:bg"))
    if antigo is not None:
        cSld.remove(antigo)
    bg = etree.Element(A.q("p:bg"))
    bgPr = etree.SubElement(bg, A.q("p:bgPr"))
    fill = etree.SubElement(bgPr, A.q("a:solidFill"))
    etree.SubElement(fill, A.q("a:srgbClr")).set(
        "val", tema.fundo.lstrip("#").upper())
    etree.SubElement(bgPr, A.q("a:effectLst"))
    cSld.insert(0, bg)


def formatar(tf, tema, tamanho, cor=None, negrito=False,
             entrelinha=G.ENTRELINHA_CORPO):
    cor = cor or tema.texto
    for p in tf.paragraphs:
        p.alignment = PP_ALIGN.LEFT
        pPr = p._p.get_or_add_pPr()
        for antigo in pPr.findall(A.q("a:lnSpc")):
            pPr.remove(antigo)
        ln = etree.Element(A.q("a:lnSpc"))
        etree.SubElement(ln, A.q("a:spcPct")).set("val", str(entrelinha))
        pPr.insert(0, ln)
        for r in p.runs:
            r.font.size = Pt(tamanho)
            r.font.name = tema.fonte
            r.font.bold = negrito
            r.font.color.rgb = tema.rgb(cor)
            rPr = r._r.find(A.q("a:rPr"))
            if rPr is not None:
                rPr.set("lang", "pt-BR")


def sem_marcador(tf):
    """
    Tira o marcador de lista.

    Marcador e correto em lista de conteudo (a regra B09 exige o nativo, nao o
    hifen digitado), mas um numero em destaque, um titulo de cartao ou um
    subtitulo de capa nao sao itens de lista — e o bullet herdado do layout
    aparece ali como sujeira.
    """
    for p in tf.paragraphs:
        pPr = p._p.get_or_add_pPr()
        for tag in ("a:buChar", "a:buAutoNum", "a:buNone", "a:buBlip"):
            for antigo in pPr.findall(A.q(tag)):
                pPr.remove(antigo)
        pPr.append(etree.Element(A.q("a:buNone")))
        pPr.set("marL", "0")
        pPr.set("indent", "0")


def nomear(shape, nome):
    c = A.get_cNvPr(shape._element)
    if c is not None:
        c.set("name", nome)


def posicionar(shape, coluna, n, y, altura):
    shape.left, shape.top = G.x(coluna), y
    shape.width, shape.height = G.larg(n), altura


def remover_placeholders_vazios(slide):
    for shape in list(slide.shapes):
        el = shape._element
        if A.get_ph(el) is None:
            continue
        texto = " ".join(A.paragraph_text(p) for p in A.iter_paragraphs(el)).strip()
        if not texto:
            el.getparent().remove(el)


def _validar_link(texto):
    if A.RE_URL.match(texto) or texto.strip().lower().strip(" .:;!?") in A.VAGUE_LINK:
        raise ErroDeRoteiro(
            "texto de link nao descritivo: %r — escreva o destino no proprio "
            "texto, como 'Diretrizes WCAG 2.2 do W3C'" % texto)


def escrever(tf, linhas, links, tema, tamanho, cor=None, negrito=False,
             entrelinha=G.ENTRELINHA_CORPO):
    """Texto e links no MESMO placeholder — caixa solta reprova em B05."""
    tf.word_wrap = True
    primeiro = True
    for l in linhas:
        if primeiro:
            tf.text = l
            primeiro = False
        else:
            tf.add_paragraph().text = l
    runs_link = []
    for lk in links or []:
        _validar_link(lk["texto"])
        par = tf.paragraphs[0] if primeiro else tf.add_paragraph()
        primeiro = False
        r = par.add_run()
        r.text = lk["texto"]
        r.hyperlink.address = lk["url"]
        runs_link.append(r)
    formatar(tf, tema, tamanho, cor=cor, negrito=negrito, entrelinha=entrelinha)
    for r in runs_link:
        r.font.color.rgb = tema.rgb(tema.destaque)
        r.font.underline = True


def _pega(slide, idx):
    for ph in slide.placeholders:
        if ph.placeholder_format.idx == idx:
            return ph
    return None


# ==========================================================================
# Blocos
# ==========================================================================
def _titulo(slide, texto, tema, tamanho=None):
    if slide.shapes.title is None:
        raise ErroDeRoteiro("layout sem placeholder de titulo")
    t = slide.shapes.title
    t.text = texto
    nomear(t, "Título do slide")
    t.text_frame.word_wrap = True
    formatar(t.text_frame, tema, tamanho or G.TIPO["titulo"], negrito=True,
             entrelinha=G.ENTRELINHA_TITULO)


def mandar_para_tras(slide, shape):
    """
    Manda a forma para o fundo do eixo Z.

    Forma criada depois entra por ULTIMO no spTree e e desenhada POR CIMA — foi
    assim que os fundos de cartao cobriram o texto e os cartoes sairam vazios.
    Como o fundo e decorativo, ele ja esta fora da ordem de leitura, entao
    move-lo no eixo Z nao mexe no que o leitor de tela anuncia. E exatamente a
    saida que o catalogo indica na armadilha do eixo Z (regra C03).
    """
    spTree = slide.shapes._spTree
    el = shape._element
    spTree.remove(el)
    spTree.insert(2, el)   # depois de nvGrpSpPr e grpSpPr


def _cartao_de_fundo(slide, tema, caixa, nome="Cartão de fundo"):
    l, t, w, h = caixa
    forma = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, h)
    forma.fill.solid()
    forma.fill.fore_color.rgb = tema.rgb(tema.cartao)
    forma.line.color.rgb = tema.rgb(tema.destaque)
    forma.line.width = Pt(1.25)
    forma.shadow.inherit = False
    nomear(forma, nome)
    A.set_decorative(forma._element, True)
    mandar_para_tras(slide, forma)
    return forma


def _resolver_arquivo(fig, modo):
    arq = fig["arquivo"]
    if isinstance(arq, dict):
        return arq.get(modo) or arq.get("padrao") or next(iter(arq.values()))
    return arq


def _imagem(slide, fig, tema, caixa, modo="padrao"):
    """
    Figura ENCAIXADA na caixa, preservando a proporcao.

    Passar largura e altura ao add_picture foi o que distorceu todas as figuras
    do deck anterior, entre 28% e 48%. Aqui a caixa e o limite e a figura se
    encaixa dentro dela, centralizada na sobra (regra N01).
    """
    arq = _resolver_arquivo(fig, modo)
    if not os.path.exists(arq):
        raise ErroDeRoteiro("figura do modo %r nao encontrada: %s" % (modo, arq))
    if not fig.get("alt", "").strip():
        raise ErroDeRoteiro("figura sem alt text: %s" % arq)
    if not fig.get("descricao_longa", "").strip():
        raise ErroDeRoteiro("figura sem descricao longa: %s" % arq)

    from PIL import Image
    with Image.open(arq) as im:
        nw, nh = im.width, im.height

    l, t, cw, ch = caixa
    w, h, dx, dy = G.encaixar(nw, nh, cw, ch)
    pic = slide.shapes.add_picture(arq, l + dx, t + dy, w, h)
    nomear(pic, fig.get("nome") or "Figura")
    A.set_alt_text(pic._element, fig["alt"].strip())
    return pic


def _pintar_celula(cel, hexv):
    """Cor explicita: cor vinda do estilo da tabela nao e auditavel."""
    tcPr = cel._tc.get_or_add_tcPr()
    for antigo in list(tcPr):
        if A.local(antigo) in ("solidFill", "noFill", "gradFill", "blipFill",
                               "pattFill"):
            tcPr.remove(antigo)
    fill = etree.SubElement(tcPr, A.q("a:solidFill"))
    etree.SubElement(fill, A.q("a:srgbClr")).set("val", hexv.lstrip("#").upper())
    tcPr.remove(fill)
    tcPr.insert(0, fill)


def _tabela(slide, tab, tema, coluna, n, y):
    cab, linhas = tab["cabecalho"], tab["linhas"]
    if not tab.get("alt", "").strip():
        raise ErroDeRoteiro("tabela sem alt text")
    tamanho = tab.get("tamanho", G.TIPO["tabela"])
    if tamanho < 18:
        raise ErroDeRoteiro(
            "tabela pedindo %dpt: celula tambem e texto e o piso e 18pt (F02)"
            % tamanho)
    for l in linhas:
        if len(l) != len(cab):
            raise ErroDeRoteiro("linha com %d celulas para %d colunas"
                                % (len(l), len(cab)))

    # Tabela curta nao deve ficar espremida no topo de uma faixa enorme:
    # a linha cresce ate um teto e a tabela e centralizada na faixa restante.
    n_linhas = len(linhas) + 1
    disponivel = G.RODAPE_Y - y
    linha_h = max(G.cm(1.05), min(G.cm(1.75), disponivel // n_linhas))
    altura = linha_h * n_linhas
    if altura < disponivel:
        y += (disponivel - altura) // 3     # respira mais embaixo que em cima
    if y + altura > G.RODAPE_Y:
        cabem = max(1, int(disponivel / G.cm(1.05)) - 1)
        raise ErroDeRoteiro(
            "a tabela passaria %.1f cm da area util e entraria na faixa do "
            "rodape, perdendo a ultima linha (regra N02). Cabem %d linhas aqui: "
            "reduza ou divida em duas tabelas"
            % ((y + altura - G.RODAPE_Y) / G.EMU_CM, cabem))

    gf = slide.shapes.add_table(len(linhas) + 1, len(cab), G.x(coluna), y,
                                G.larg(n), altura)
    nomear(gf, tab.get("nome") or "Tabela de dados")
    A.set_alt_text(gf._element, tab["alt"].strip())
    t = gf.table
    t.first_row = True
    if tab.get("primeira_coluna"):
        t.first_col = True
    tblPr = t._tbl.find(A.q("a:tblPr"))
    if tblPr is not None:
        tblPr.set("bandRow", "0")

    for ci, v in enumerate(cab):
        cel = t.cell(0, ci)
        cel.text = str(v)
        cel.vertical_anchor = MSO_ANCHOR.MIDDLE
        _pintar_celula(cel, tema.destaque)
        formatar(cel.text_frame, tema, tamanho, cor=tema.sobre_destaque,
                 negrito=True, entrelinha=100000)
    for ri, linha in enumerate(linhas, 1):
        for ci, v in enumerate(linha):
            cel = t.cell(ri, ci)
            cel.text = str(v)
            cel.vertical_anchor = MSO_ANCHOR.MIDDLE
            _pintar_celula(cel, tema.fundo_celula)
            formatar(cel.text_frame, tema, tamanho, entrelinha=100000)
    return gf


def _altura_de_cartao(itens):
    """
    Altura pelo conteudo, nao pela faixa inteira.

    Cartao esticado ate o rodape fica com metade de ar dentro; cartao curto
    demais aperta o texto. Estima pelo numero de linhas do maior cartao.
    """
    maior = max(1 + len(it.get("texto", []) or []) for it in itens)
    h = G.cm(2.6) + maior * G.cm(1.5)
    # piso de 72% da faixa: abaixo disso a linha de cartoes fica solta no meio
    # do slide e a regra N05 acusa area ociosa, com razao
    return max(int(G.CONTEUDO_H * 0.72), min(G.CONTEUDO_H, h))


def _linha_de_cartoes(slide, tema, itens, y, altura, rotulo="Cartão"):
    """
    Cartoes com placeholder de verdade, um por cartao.

    Cartao desenhado com caixa de texto solta reprovaria em B05, e com razao:
    caixa solta nao carrega semantica. O fundo arredondado e decorativo; o
    texto mora no placeholder.
    """
    vao = 12 // len(itens)
    for k in range(len(itens)):
        _cartao_de_fundo(slide, tema, G.bloco(k * vao, vao, y, altura),
                         "Fundo do cartão %d" % (k + 1))
    for k, item in enumerate(itens):
        ph = _pega(slide, 1 + k)
        if ph is None:
            raise ErroDeRoteiro("modelo sem placeholder para o cartao %d" % (k + 1))
        nomear(ph, "%s %d: %s" % (rotulo, k + 1, item["titulo"][:26]))
        ph.left = G.x(k * vao) + G.cm(0.6)
        ph.top = y + G.cm(0.6)
        ph.width = G.larg(vao) - G.cm(1.2)
        ph.height = altura - G.cm(1.2)
        tf = ph.text_frame
        tf.word_wrap = True
        tf.text = item["titulo"]
        for l in item.get("texto", []) or []:
            tf.add_paragraph().text = l
        formatar(tf, tema, G.TIPO["cartao_corpo"])
        sem_marcador(tf)
        for r in tf.paragraphs[0].runs:
            r.font.size = Pt(G.TIPO["cartao_titulo"])
            r.font.bold = True
            r.font.color.rgb = tema.rgb(tema.destaque)
    for k in range(len(itens), 4):
        ph = _pega(slide, 1 + k)
        if ph is not None:
            ph._element.getparent().remove(ph._element)


# ==========================================================================
# Montagem
# ==========================================================================
def _tamanho(spec, perfil, base=None):
    """Tamanho do corpo: o do slide, senao o do perfil, senao o da escala."""
    if spec.get("tamanho"):
        return spec["tamanho"]
    return TIPO_PERFIL.get(perfil) or base or G.TIPO["corpo"]


def montar_slide(prs, spec, tema, sufixo="", modo="padrao",
                 perfil="completo"):
    tipo = spec.get("tipo", "conteudo")
    titulo = spec["titulo"] + sufixo
    linhas = spec.get("conteudo", []) or []
    links = spec.get("links", []) or []

    # No perfil de Libras a faixa da direita e reservada em TODO tipo de
    # slide: a janela nao pode aparecer e sumir entre slides do mesmo bloco,
    # e onde o layout nao reserva espaco ela cobre o conteudo (regra N03).
    estreito = COLUNAS_LIBRAS if perfil == "libras" else 0

    if tipo == "capa":
        slide = prs.slides.add_slide(layout_por_nome(prs, "Capa"))
        pintar_fundo(slide, tema)
        _titulo(slide, titulo, tema, G.TIPO["capa"])
        if estreito:
            posicionar(slide.shapes.title, 0, 8 - estreito // 2,
                       G.cm(4.2), G.cm(3.4))
        sub = spec.get("subtitulo", "")
        if sub:
            ph = _pega(slide, 1)
            nomear(ph, "Subtítulo")
            escrever(ph.text_frame, sub if isinstance(sub, list) else [sub],
                     [], tema, G.TIPO["corpo"])
            sem_marcador(ph.text_frame)

    elif tipo == "secao":
        slide = prs.slides.add_slide(layout_por_nome(prs, "Seção"))
        pintar_fundo(slide, tema)
        _titulo(slide, titulo, tema, G.TIPO["secao"])
        if estreito:
            posicionar(slide.shapes.title, 0, 10 - estreito,
                       G.cm(6.6), G.cm(3.4))
            apoio = _pega(slide, 1)
            if apoio is not None:
                posicionar(apoio, 0, 10 - estreito, G.cm(10.2), G.cm(2.4))
        if linhas:
            ph = _pega(slide, 1)
            nomear(ph, "Apoio da seção")
            escrever(ph.text_frame, linhas, [], tema, G.TIPO["apoio"],
                     cor=tema.destaque)
            sem_marcador(ph.text_frame)

    elif tipo == "destaque":
        slide = prs.slides.add_slide(layout_por_nome(prs, "Destaque"))
        pintar_fundo(slide, tema)
        _titulo(slide, titulo, tema)
        num = _pega(slide, 1)
        nomear(num, "Número em destaque")
        posicionar(num, 0, 4, G.CONTEUDO_Y, G.CONTEUDO_H)
        tf = num.text_frame
        tf.word_wrap = True
        tf.text = str(spec["numero"])
        if spec.get("rotulo"):
            tf.add_paragraph().text = spec["rotulo"]
        formatar(tf, tema, G.TIPO["destaque_numero"], cor=tema.destaque,
                 negrito=True, entrelinha=90000)
        sem_marcador(tf)
        # o numero e display e pode ter entrelinha apertada; o rotulo NAO e,
        # e entrelinha curta em texto de leitura reprova em F05
        for p in tf.paragraphs[1:]:
            pPr = p._p.get_or_add_pPr()
            for antigo_ln in pPr.findall(A.q("a:lnSpc")):
                pPr.remove(antigo_ln)
            ln = etree.Element(A.q("a:lnSpc"))
            etree.SubElement(ln, A.q("a:spcPct")).set(
                "val", str(G.ENTRELINHA_CORPO))
            pPr.insert(0, ln)
            for r in p.runs:
                r.font.size = Pt(G.TIPO["destaque_rotulo"])
                r.font.bold = False
                r.font.color.rgb = tema.rgb(tema.texto)
        lado = _pega(slide, 2)
        nomear(lado, "Explicação do destaque")
        posicionar(lado, 4, 8, G.CONTEUDO_Y, G.CONTEUDO_H)
        escrever(lado.text_frame, linhas, links, tema, G.TIPO["corpo"])

    elif tipo == "cartoes":
        slide = prs.slides.add_slide(layout_por_nome(prs, "Cartões"))
        pintar_fundo(slide, tema)
        _titulo(slide, titulo, tema)
        cartoes = spec["cartoes"]
        if not 2 <= len(cartoes) <= 4:
            raise ErroDeRoteiro("cartoes: use de 2 a 4 (recebi %d)" % len(cartoes))
        h = _altura_de_cartao(cartoes)
        _linha_de_cartoes(slide, tema, cartoes,
                          G.CONTEUDO_Y + (G.CONTEUDO_H - h) // 2, h)

    elif tipo == "citacao":
        slide = prs.slides.add_slide(layout_por_nome(prs, "Citação"))
        pintar_fundo(slide, tema)
        _titulo(slide, titulo, tema, G.TIPO["citacao"])
        if estreito:
            posicionar(slide.shapes.title, 0, 10 - estreito,
                       G.cm(5.6), G.cm(6.4))
            credito = _pega(slide, 1)
            if credito is not None:
                posicionar(credito, 0, 10 - estreito, G.cm(12.6), G.cm(2.4))
        if spec.get("credito"):
            ph = _pega(slide, 1)
            nomear(ph, "Crédito da citação")
            escrever(ph.text_frame, [spec["credito"]], [], tema,
                     G.TIPO["credito"], cor=tema.destaque)
            sem_marcador(ph.text_frame)

    elif tipo == "comparacao":
        slide = prs.slides.add_slide(layout_por_nome(prs, "Comparação"))
        pintar_fundo(slide, tema)
        _titulo(slide, titulo, tema)
        for k, col in enumerate(spec["colunas"][:2]):
            cab, corpo = _pega(slide, 1 + k * 2), _pega(slide, 2 + k * 2)
            nomear(cab, "Cabeçalho da coluna %d" % (k + 1))
            nomear(corpo, "Conteúdo da coluna %d" % (k + 1))
            escrever(cab.text_frame, [col["titulo"]], [], tema,
                     G.TIPO["cartao_titulo"], cor=tema.destaque, negrito=True)
            sem_marcador(cab.text_frame)
            escrever(corpo.text_frame, col.get("texto", []) or [], [], tema,
                     G.TIPO["corpo_denso"])

    else:
        tem_figura = bool(spec.get("figura"))
        tem_tabela = bool(spec.get("tabela"))
        # No perfil de Libras, as 4 colunas da direita ficam VAZIAS por desenho:
        # e a faixa onde a janela entra depois. Sem isso a janela cobriria texto
        # e reprovaria em N03 — foi por essa razao que ela vivia so na capa.
        largo = 12 - COLUNAS_LIBRAS if perfil == "libras" else 12
        nome_layout = ("Conteúdo com janela de Libras" if perfil == "libras"
                       else "Título e conteúdo")
        slide = prs.slides.add_slide(layout_por_nome(prs, nome_layout))
        pintar_fundo(slide, tema)
        _titulo(slide, titulo, tema)
        corpo = _pega(slide, 1)
        nomear(corpo, "Conteúdo principal")

        if tem_figura:
            # figura larga precisa de mais colunas, senao encolhe na altura e
            # cai abaixo do minimo legivel na projecao (regra N10)
            from PIL import Image
            with Image.open(_resolver_arquivo(spec["figura"], modo)) as _im:
                razao = _im.width / _im.height
            if perfil == "libras":
                # lado a lado, texto e figura ficariam ambos estreitos demais:
                # a figura caiu para 3,8 cm de menor lado e reprovou em N10.
                # Com a faixa da janela ocupando 4 colunas, o jeito e empilhar.
                alt_txt = G.cm(2.4) if (linhas or links) else 0
                if alt_txt:
                    posicionar(corpo, 0, largo, G.CONTEUDO_Y, alt_txt)
                    escrever(corpo.text_frame, linhas, links, tema,
                             _tamanho(spec, perfil))
                else:
                    corpo._element.getparent().remove(corpo._element)
                y_fig = G.CONTEUDO_Y + (alt_txt + G.cm(0.5) if alt_txt else 0)
                _imagem(slide, spec["figura"], tema,
                        G.bloco(0, largo, y_fig,
                                G.CONTEUDO_FIM - y_fig), modo)
            else:
                n_txt = 4 if razao >= 1.8 else 5
                posicionar(corpo, 0, n_txt, G.CONTEUDO_Y, G.CONTEUDO_H)
                escrever(corpo.text_frame, linhas, links, tema,
                         _tamanho(spec, perfil))
                _imagem(slide, spec["figura"], tema,
                        G.bloco(n_txt + 1, largo - n_txt - 1, G.CONTEUDO_Y,
                                G.CONTEUDO_H), modo)
        elif tem_tabela:
            alt_txt = G.cm(1.5) if (linhas or links) else 0
            if alt_txt:
                posicionar(corpo, 0, largo, G.CONTEUDO_Y, alt_txt)
                escrever(corpo.text_frame, linhas, links, tema,
                         spec.get("tamanho", G.TIPO["corpo_denso"]))
            else:
                corpo._element.getparent().remove(corpo._element)
            y_tab = G.CONTEUDO_Y + (alt_txt + G.cm(0.7) if alt_txt else 0)
            _tabela(slide, spec["tabela"], tema, 0, largo, y_tab)
        else:
            posicionar(corpo, 0, largo, G.CONTEUDO_Y, G.CONTEUDO_H)
            escrever(corpo.text_frame, linhas, links, tema,
                     _tamanho(spec, perfil))

    remover_placeholders_vazios(slide)

    notas = spec.get("notas", "")
    # A mensagem-chave viaja nas NOTAS, marcada. E o que permite a regra O04
    # comparar VERSOES COM TEXTOS DIFERENTES: sem uma ancora explicita,
    # "equivalente" seria palavra, nao verificacao.
    if spec.get("mensagem_chave"):
        marca = "[chave] " + spec["mensagem_chave"].strip()
        notas = (marca + "\n\n" + notas).strip() if notas else marca
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
            raise ErroDeRoteiro("roteiro em YAML exige PyYAML: pip install pyyaml")
        return yaml.safe_load(bruto)
    return json.loads(bruto)


def validar_roteiro(r):
    if "apresentacao" not in r or "slides" not in r:
        raise ErroDeRoteiro("roteiro precisa de 'apresentacao' e 'slides'")
    ap = r["apresentacao"]
    for campo in ("titulo", "autor"):
        if not str(ap.get(campo, "")).strip():
            raise ErroDeRoteiro("apresentacao.%s e obrigatorio (A01/A04)" % campo)
    vistos = {}
    for i, s in enumerate(r["slides"], 1):
        t = str(s.get("titulo", "")).strip()
        if not t:
            raise ErroDeRoteiro("slide %d sem titulo (B01/B02)" % i)
        if t.lower() in vistos:
            raise ErroDeRoteiro(
                "titulo repetido nos slides %d e %d: %r — use sufixo de "
                "continuidade (B03)" % (vistos[t.lower()], i, t))
        vistos[t.lower()] = i
        tipo = s.get("tipo", "conteudo")
        if len(s.get("conteudo", []) or []) > 6:
            raise ErroDeRoteiro("slide %d com %d paragrafos; o limite e 6 (F07)"
                                % (i, len(s["conteudo"])))
        if tipo == "destaque" and "numero" not in s:
            raise ErroDeRoteiro("slide %d: 'destaque' exige 'numero'" % i)
        if tipo == "cartoes" and not s.get("cartoes"):
            raise ErroDeRoteiro("slide %d: 'cartoes' exige a lista 'cartoes'" % i)
        if tipo == "comparacao" and len(s.get("colunas", []) or []) != 2:
            raise ErroDeRoteiro("slide %d: 'comparacao' exige 2 colunas" % i)


# ==========================================================================
# Perfil de publico: transforma o ROTEIRO, nao o slide
# ==========================================================================
# Orcamento de texto por perfil. Nao e gosto: sai da regra editorial de cada
# publico, e esta documentado em references/10-versoes-por-publico.md.
#   libras         a janela ocupa 4 das 12 colunas e o portugues e SEGUNDA
#                  lingua: o slide sustenta uma ideia, nao cinco.
#   leitura_facil  "1 idea per sentence" (Inclusion Europe, regra 19) e
#                  "avoid several actions in a single sentence" (IFLA).
ORCAMENTO = {
    "libras":        {"paragrafos": 2, "palavras": 14, "frases": 1},
    "leitura_facil": {"paragrafos": 3, "palavras": 18, "frases": 1},
}


def validar_perfil(roteiro, perfil):
    """Recusa no ROTEIRO o que sairia longo demais para o publico do perfil."""
    orc = ORCAMENTO.get(perfil)
    if not orc:
        return
    for i, spec in enumerate(roteiro["slides"], 1):
        if spec.get("tipo") in ("capa", "secao", "citacao"):
            continue
        linhas = spec.get("conteudo") or []
        if len(linhas) > orc["paragrafos"]:
            raise ErroDeRoteiro(
                "perfil %r, slide %d: %d parágrafos; o limite é %d"
                % (perfil, i, len(linhas), orc["paragrafos"]))
        for linha in linhas:
            n = len(linha.split())
            if n > orc["palavras"]:
                raise ErroDeRoteiro(
                    "perfil %r, slide %d: %d palavras numa linha; o limite é "
                    "%d — %r" % (perfil, i, n, orc["palavras"], linha[:50]))
            frases = [f for f in re.split(r"[.!?;]+", linha) if f.strip()]
            if len(frases) > orc["frases"]:
                raise ErroDeRoteiro(
                    "perfil %r, slide %d: %d frases numa linha; uma ideia por "
                    "frase — %r" % (perfil, i, len(frases), linha[:50]))


def perfilar(roteiro, perfil):
    """
    Devolve o roteiro reescrito para um perfil.

    O texto reduzido NAO e inventado aqui: ele vem do campo `mensagem_chave`,
    que o autor escreve uma vez por slide. Gerar um resumo automatico produziria
    uma terceira versao do conteudo, com risco de dizer outra coisa — e e
    exatamente isso que a regra O04 existe para impedir.

    Quem quiser mais que a mensagem-chave declara `libras:` ou `facil:` no
    slide, com a lista de paragrafos daquele perfil.
    """
    if perfil == "completo":
        return roteiro

    if perfil not in PERFIS:
        raise ErroDeRoteiro("perfil desconhecido: %r" % perfil)

    chave_extra = {"libras": "libras", "leitura_facil": "facil"}[perfil]
    novos = []
    for i, spec in enumerate(roteiro["slides"], 1):
        s2 = dict(spec)
        # Capa, secao e citacao nao levam corpo reduzido — mas o TITULO delas
        # encolhe junto com a faixa reservada, e titulo longo transborda (N12).
        # O override `libras: {titulo: ...}` vale para elas tambem.
        if spec.get("tipo") in ("capa", "secao", "citacao"):
            proprio = spec.get(chave_extra)
            if isinstance(proprio, dict) and proprio.get("titulo"):
                s2["titulo"] = proprio["titulo"]
            for k in ("libras", "facil"):
                s2.pop(k, None)
            novos.append(s2)
            continue

        proprio = spec.get(chave_extra)
        if isinstance(proprio, dict):
            # titulo proprio: em Libras, titulo longo ocupa duas linhas e
            # transborda a faixa (N12), e encurtar a fonte reprovaria em F03
            if proprio.get("titulo"):
                s2["titulo"] = proprio["titulo"]
            proprio = proprio.get("conteudo")
        if proprio:
            linhas = proprio if isinstance(proprio, list) else [proprio]
        elif spec.get("mensagem_chave"):
            linhas = [spec["mensagem_chave"]]
        else:
            raise ErroDeRoteiro(
                "slide %d (%r) nao tem 'mensagem_chave' nem %r — o perfil %r "
                "precisa de um dos dois. Reduzir texto e trabalho de redacao, "
                "nao de codigo (regra O04)"
                % (i, spec.get("titulo", "")[:40], chave_extra, perfil))

        s2["conteudo"] = linhas
        # tipos que dependem de blocos proprios voltam a ser conteudo simples:
        # cartao e comparacao carregam texto demais para estes perfis
        if spec.get("tipo") in ("cartoes", "comparacao", "destaque"):
            # esses tipos ocupam a largura toda e a janela cairia por cima
            # deles (N03). Viram conteudo simples, que respeita a faixa.
            s2["tipo"] = "conteudo"
            for k in ("cartoes", "colunas", "numero", "rotulo"):
                s2.pop(k, None)
        for k in (chave_extra, "libras", "facil"):
            s2.pop(k, None)
        novos.append(s2)

    return {"apresentacao": dict(roteiro["apresentacao"]), "slides": novos}


# ==========================================================================
def construir(roteiro, saida, modo="padrao", perfil="completo",
              com_modos=None):
    """
    Monta UM deck numa UNICA paleta.

    Sem sufixo de titulo: como os modos deixaram de conviver no mesmo arquivo,
    `spec["titulo"]` vai integro para os tres decks — e e isso que torna a
    paridade entre eles verificavel (regra O01). A regra B03, titulo repetido,
    continua satisfeita porque os titulos sao unicos DENTRO de cada arquivo.

    O modo fica nos METADADOS, nao no conteudo: `cp.title` leva o nome do modo,
    que e o que o leitor de tela anuncia ao abrir, sem sujar o texto comparado.
    """
    if com_modos is not None:
        # alias depreciado da assinatura antiga
        print("AVISO: construir(..., com_modos=) foi substituido por "
              "construir_conjunto(...); veja --arquivo-unico")
        if com_modos:
            return _construir_arquivo_unico(roteiro, saida)

    validar_roteiro(roteiro)
    roteiro = perfilar(roteiro, perfil)
    validar_perfil(roteiro, perfil)
    temas = carregar_temas()
    if modo not in temas:
        raise ErroDeRoteiro("modo desconhecido: %r" % modo)
    ap = roteiro["apresentacao"]

    if not os.path.exists(MODELO):
        raise ErroDeRoteiro(
            "modelo ausente: %s — rode antes: python scripts/gerar_modelo.py"
            % MODELO)
    prs = Presentation(MODELO)
    prs.slide_width, prs.slide_height = G.LARGURA, G.ALTURA

    tema = temas[modo]
    for spec in roteiro["slides"]:
        montar_slide(prs, spec, tema, "", modo, perfil)

    _accent_no_tema(prs, tema.destaque)
    _gravar_metadados(prs, ap, tema, perfil)
    prs.save(saida)
    return saida


def _accent_no_tema(prs, cor_hex):
    """
    Reescreve accent1 do tema com a cor de destaque do modo.

    A mobilia decorativa — filete e faixa do rodape — mora nos LAYOUTS desde
    que o Verificador nativo passou a lista-la no painel de ordem de leitura de
    cada slide. Como o layout e o mesmo para os tres modos, a cor dela nao pode
    ser fixa: vem do tema, e e aqui que o tema muda.
    """
    from pptx.opc.constants import RELATIONSHIP_TYPE as RT

    try:
        parte = prs.slide_masters[0].part.part_related_by(RT.THEME)
        raiz = etree.fromstring(parte.blob)
    except Exception:
        return False
    alvo_ = raiz.find(".//" + A.q("a:clrScheme") + "/" + A.q("a:accent1"))
    if alvo_ is None:
        return False
    for antigo in list(alvo_):
        alvo_.remove(antigo)
    etree.SubElement(alvo_, A.q("a:srgbClr")).set(
        "val", cor_hex.lstrip("#").upper())
    parte._blob = etree.tostring(raiz, xml_declaration=True, encoding="UTF-8",
                                 standalone=True)
    return True


def _gravar_metadados(prs, ap, tema, perfil="completo"):
    cp = prs.core_properties
    titulo = ap["titulo"]
    if perfil != "completo":
        # o publico da versao vai no titulo do documento, que e o que o leitor
        # de tela anuncia ao abrir — e nao no conteudo, que precisa continuar
        # comparavel entre as versoes (regra O01)
        titulo = "%s — versão %s" % (titulo, ROTULO_PERFIL[perfil])
    if tema is not None and tema.nome != "Modo padrão":
        # o que o leitor de tela anuncia ao abrir (DisplayDocTitle vem ativo)
        titulo = "%s — %s" % (titulo, tema.nome.lower())
    cp.title = titulo
    cp.author = ap["autor"]
    cp.language = ap.get("idioma", "pt-BR")
    cp.subject = ap.get("assunto", "")
    cp.keywords = ap.get("palavras_chave", "")
    cp.comments = ap.get("resumo", "")


def construir_conjunto(roteiro, pasta, base, modos=MODOS,
                       perfis=("completo",), arquivo_unico=False,
                       todos_os_modos=False):
    """
    Constroi um deck por modo e devolve {modo: caminho}.

    Com `arquivo_unico=True` volta ao desenho antigo: um so arquivo, com
    slide-hub e tres secoes. Fica disponivel porque ha quem precise entregar um
    anexo unico — mas nao e mais o padrao, e o motivo esta no topo deste arquivo.
    """
    os.makedirs(pasta, exist_ok=True)
    if arquivo_unico:
        saida = os.path.join(pasta, base + ".pptx")
        _construir_arquivo_unico(roteiro, saida)
        return {"arquivo_unico": saida}

    feitos = {}
    for perfil in perfis:
        # Perfil de publico so no modo padrao, por omissao. Os tres modos x tres
        # perfis dariam nove arquivos e 137 MB — e o deck de Libras sozinho, com
        # 28 videos, ja passa de 40 MB. Quem precisar do produto cartesiano pede
        # com --perfis-todos-os-modos, e o LEIA-ME declara a escolha.
        quer_todas = recursos_do_perfil(perfil).get("todas_as_paletas", False)
        modos_deste = modos if (quer_todas or todos_os_modos) else ("padrao",)
        for modo in modos_deste:
            nome = base + SUFIXO_PERFIL[perfil] + SUFIXO[modo] + ".pptx"
            saida = os.path.join(pasta, nome)
            construir(roteiro, saida, modo, perfil)
            feitos["%s/%s" % (perfil, modo)] = saida
    return feitos


def _construir_arquivo_unico(roteiro, saida):
    """O desenho legado: hub + tres secoes no mesmo .pptx."""
    validar_roteiro(roteiro)
    temas = carregar_temas()
    ap = roteiro["apresentacao"]

    if not os.path.exists(MODELO):
        raise ErroDeRoteiro(
            "modelo ausente: %s — rode antes: python scripts/gerar_modelo.py"
            % MODELO)
    prs = Presentation(MODELO)
    prs.slide_width, prs.slide_height = G.LARGURA, G.ALTURA

    _montar_hub(prs, temas["padrao"], list(MODOS))
    indices = {}
    for modo in MODOS:
        tema = temas[modo]
        # o sufixo existe SO aqui: sem ele, os titulos repetem no mesmo arquivo
        sufixo = "" if modo == "padrao" else " · %s" % tema.nome.replace("Modo ", "")
        primeiro = len(prs.slides._sldIdLst)
        for spec in roteiro["slides"]:
            montar_slide(prs, spec, tema, sufixo, modo)
        indices[modo] = (primeiro, len(prs.slides._sldIdLst) - 1)

    _gravar_metadados(prs, ap, None)
    prs.save(saida)
    _gravar_secoes(saida, indices, temas)
    return indices


def _montar_hub(prs, tema, modos):
    slide = prs.slides.add_slide(layout_por_nome(prs, "Cartões"))
    pintar_fundo(slide, tema)
    _titulo(slide, "Escolha o modo de exibição", tema)
    rotulos = {"padrao": "Modo padrão", "alto_contraste": "Modo alto contraste",
               "daltonico": "Modo daltônico-seguro"}
    descr = {"padrao": ["Fundo off-white e texto quase-preto.", "Contraste 16,3:1."],
             "alto_contraste": ["Fundo preto e texto branco.", "Contraste 21:1."],
             "daltonico": ["Matizes maximamente separados.", "Contraste 15,9:1."]}
    itens = [{"titulo": rotulos[m], "texto": descr[m]} for m in modos]
    h = _altura_de_cartao(itens)
    _linha_de_cartoes(slide, tema, itens,
                      G.CONTEUDO_Y + (G.CONTEUDO_H - h) // 2, h, "Modo")
    remover_placeholders_vazios(slide)
    slide.notes_slide.notes_text_frame.text = (
        "Os três modos têm exatamente o mesmo conteúdo. Muda só a paleta. "
        "Use as seções do arquivo para ir ao modo escolhido.")
    return slide


def _gravar_secoes(caminho, indices, temas):
    import shutil
    import zipfile
    from uuid import uuid4

    tmp = caminho + ".tmp"
    with zipfile.ZipFile(caminho) as zin:
        itens = {n: zin.read(n) for n in zin.namelist()}
    root = etree.fromstring(itens["ppt/presentation.xml"])
    ids = [s.get("id") for s in root.find(A.q("p:sldIdLst"))]

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
    ap.add_argument("-o", "--saida", default="deck.pptx",
                    help="arquivo de saida; com --todos-os-modos, prefixo")
    ap.add_argument("--todos-os-modos", action="store_true",
                    help="gera um arquivo por modo de cor (o padrao do pipeline)")
    ap.add_argument("--modo", default="padrao", choices=list(MODOS))
    ap.add_argument("--arquivo-unico", action="store_true",
                    help="desenho legado: hub e tres secoes num arquivo so")
    args = ap.parse_args()

    try:
        roteiro = carregar_roteiro(args.roteiro)
        if args.todos_os_modos or args.arquivo_unico:
            pasta = os.path.dirname(os.path.abspath(args.saida))
            base = os.path.splitext(os.path.basename(args.saida))[0]
            feitos = construir_conjunto(roteiro, pasta, base,
                                        arquivo_unico=args.arquivo_unico)
        else:
            feitos = {args.modo: construir(roteiro, args.saida, args.modo)}
    except ErroDeRoteiro as e:
        print("ERRO DE ROTEIRO: %s" % e)
        print("\nO build parou de proposito: o slide sairia inacessivel ou mal")
        print("composto. Corrija o ROTEIRO, nao o .pptx.")
        return 2

    for modo, caminho in feitos.items():
        prs = Presentation(caminho)
        print("%-16s %s (%d slides)"
              % (modo, os.path.basename(caminho), len(prs.slides._sldIdLst)))
    print("\nAudite agora:")
    for caminho in feitos.values():
        print("  python scripts/audit_pptx.py %s --md relatorio.md" % caminho)
    if len(feitos) > 1:
        print("  python scripts/audit_pacote.py %s"
              % " ".join(feitos.values()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
