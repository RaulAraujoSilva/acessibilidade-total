"""
a11y_lib — acesso ao que o python-pptx nao expoe.

Texto alternativo, marca de decorativo, ordem de leitura, idioma dos runs,
heranca de formatacao (slide -> layout -> master -> apresentacao) e secoes.

Todos os caminhos XML aqui foram verificados contra arquivos gerados pelo
proprio PowerPoint. Ver references/04-ooxml-cookbook.md.
"""
from __future__ import annotations

import re

# --------------------------------------------------------------------------
# Namespaces
# --------------------------------------------------------------------------
NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "adec": "http://schemas.microsoft.com/office/drawing/2017/decorative",
    "p14": "http://schemas.microsoft.com/office/powerpoint/2010/main",
}
URI_DECORATIVE = "{C183D7F6-B498-43B3-948B-1728B52AA6E4}"

EMU_PER_INCH = 914400
EMU_PER_CM = 360000


def q(tag: str) -> str:
    """'a:rPr' -> '{http://...}rPr'"""
    prefix, local = tag.split(":", 1)
    return "{%s}%s" % (NS[prefix], local)


def local(el) -> str:
    """Nome local da tag, sem namespace."""
    t = el.tag
    return t.split("}", 1)[1] if isinstance(t, str) and "}" in t else str(t)


# --------------------------------------------------------------------------
# Formas: identidade, alt text, decorativo
# --------------------------------------------------------------------------
SHAPE_TAGS = {"sp", "pic", "graphicFrame", "grpSp", "cxnSp"}


def get_cNvPr(el):
    """p:cNvPr da PROPRIA forma (nao de filhos, em caso de grupo)."""
    for child in el:
        name = local(child)
        if name.startswith("nv") and name.endswith("Pr"):
            found = child.find(q("p:cNvPr"))
            if found is not None:
                return found
    return None


def shape_id(el):
    c = get_cNvPr(el)
    return c.get("id") if c is not None else None


def shape_name(el) -> str:
    c = get_cNvPr(el)
    return (c.get("name") or "") if c is not None else ""


def get_alt_text(el) -> str:
    c = get_cNvPr(el)
    return (c.get("descr") or "") if c is not None else ""


def set_alt_text(el, texto: str) -> None:
    c = get_cNvPr(el)
    if c is not None:
        c.set("descr", texto)


def is_decorative(el) -> bool:
    c = get_cNvPr(el)
    if c is None:
        return False
    for dec in c.iter(q("adec:decorative")):
        if dec.get("val") in ("1", "true"):
            return True
    return False


def set_decorative(el, valor: bool = True) -> None:
    """
    Marca/desmarca a forma como decorativa, escrevendo a extensao que o
    PowerPoint le. Estrutura verificada em arquivo real:
      <p:cNvPr><a:extLst><a:ext uri="{C183D7F6-...}">
        <adec:decorative val="1"/></a:ext></a:extLst></p:cNvPr>
    """
    from lxml import etree

    c = get_cNvPr(el)
    if c is None:
        return
    extLst = c.find(q("a:extLst"))
    if extLst is None:
        extLst = etree.SubElement(c, q("a:extLst"))
    alvo = None
    for ext in extLst.findall(q("a:ext")):
        if ext.get("uri") == URI_DECORATIVE:
            alvo = ext
            break
    if not valor:
        if alvo is not None:
            extLst.remove(alvo)
        return
    if alvo is None:
        alvo = etree.SubElement(extLst, q("a:ext"))
        alvo.set("uri", URI_DECORATIVE)
    dec = alvo.find(q("adec:decorative"))
    if dec is None:
        dec = etree.SubElement(alvo, q("adec:decorative"))
    dec.set("val", "1")
    # o alt text tem de sair: decorativo com descr e contradicao (regra D11)
    if c.get("descr") is not None:
        del c.attrib["descr"]


def is_hidden(el) -> bool:
    c = get_cNvPr(el)
    return c is not None and c.get("hidden") in ("1", "true")


def get_hyperlink(el):
    """Devolve (r:id, tooltip) do hlinkClick da forma, ou (None, None)."""
    c = get_cNvPr(el)
    if c is None:
        return None, None
    h = c.find(q("a:hlinkClick"))
    if h is None:
        return None, None
    return h.get(q("r:id")), h.get("tooltip")


def iter_shape_elements(spTree, recurse_groups: bool = False):
    """Formas na ORDEM DE LEITURA (ordem do spTree)."""
    for child in spTree:
        if local(child) in SHAPE_TAGS:
            yield child
            if recurse_groups and local(child) == "grpSp":
                for sub in iter_shape_elements(child, recurse_groups=True):
                    yield sub


def count_group_children(el) -> int:
    if local(el) != "grpSp":
        return 0
    return sum(1 for c in el if local(c) in SHAPE_TAGS)


# --------------------------------------------------------------------------
# Placeholders
# --------------------------------------------------------------------------
def get_ph(el):
    """p:ph da forma, ou None se nao for placeholder."""
    for child in el:
        if local(child).startswith("nv") and local(child).endswith("Pr"):
            nvPr = child.find(q("p:nvPr"))
            if nvPr is not None:
                return nvPr.find(q("p:ph"))
    return None


def ph_type(el):
    ph = get_ph(el)
    if ph is None:
        return None
    return ph.get("type") or "body"  # ausencia de @type significa 'body'


def ph_idx(el):
    ph = get_ph(el)
    return ph.get("idx") if ph is not None else None


TITLE_TYPES = {"title", "ctrTitle"}


def is_title_placeholder(el) -> bool:
    return ph_type(el) in TITLE_TYPES


# --------------------------------------------------------------------------
# Geometria
# --------------------------------------------------------------------------
def get_xfrm(el):
    """(x, y, cx, cy) em EMU, ou None se a forma herda a posicao do layout."""
    for child in el:
        if local(child) in ("spPr", "grpSpPr", "xfrm"):
            xfrm = child if local(child) == "xfrm" else child.find(q("a:xfrm"))
            if xfrm is not None:
                off, ext = xfrm.find(q("a:off")), xfrm.find(q("a:ext"))
                if off is not None and ext is not None:
                    return (int(off.get("x")), int(off.get("y")),
                            int(ext.get("cx")), int(ext.get("cy")))
    # graphicFrame guarda o xfrm direto
    xfrm = el.find(q("p:xfrm"))
    if xfrm is not None:
        off, ext = xfrm.find(q("a:off")), xfrm.find(q("a:ext"))
        if off is not None and ext is not None:
            return (int(off.get("x")), int(off.get("y")),
                    int(ext.get("cx")), int(ext.get("cy")))
    return None


def is_offslide(el, slide_w: int, slide_h: int) -> bool:
    """Forma inteiramente fora da area util do slide."""
    box = get_xfrm(el)
    if box is None:
        return False
    x, y, cx, cy = box
    return x + cx <= 0 or y + cy <= 0 or x >= slide_w or y >= slide_h


# --------------------------------------------------------------------------
# Texto: paragrafos, runs, idioma, heranca
# --------------------------------------------------------------------------
def get_txBody(el):
    for child in el:
        if local(child) in ("txBody", "txbxContent"):
            return child
    return None


def iter_paragraphs(el):
    tx = get_txBody(el)
    if tx is None:
        return
    for p_el in tx.findall(q("a:p")):
        yield p_el


def iter_all_paragraphs(el):
    """
    Paragrafos da forma E das celulas de tabela.

    iter_paragraphs so alcanca o txBody direto da forma. Numa tabela, o texto
    vive em a:tbl/a:tr/a:tc/a:txBody, mais fundo, e ficava invisivel para as
    regras de tipografia e de idioma — celula a 15pt passava batido.
    """
    for p_el in iter_paragraphs(el):
        yield p_el, None
    for tbl in el.iter(q("a:tbl")):
        for ri, tr in enumerate(tbl.findall(q("a:tr"))):
            for ci, tc in enumerate(tr.findall(q("a:tc"))):
                tx = tc.find(q("a:txBody"))
                if tx is None:
                    continue
                for p_el in tx.findall(q("a:p")):
                    yield p_el, (ri, ci)


def paragraph_text(p_el) -> str:
    return "".join(t.text or "" for t in p_el.iter(q("a:t")))


def iter_runs(p_el):
    for r_el in p_el.findall(q("a:r")):
        yield r_el


def run_text(r_el) -> str:
    t = r_el.find(q("a:t"))
    return (t.text or "") if t is not None else ""


def run_lang(r_el):
    rPr = r_el.find(q("a:rPr"))
    return rPr.get("lang") if rPr is not None else None


def _rPr_attr(el, attr):
    if el is None:
        return None
    return el.get(attr)


def run_props(r_el):
    """sz (centesimos de pt), b, i, u declarados NO RUN. None = herdado."""
    rPr = r_el.find(q("a:rPr"))
    return {
        "sz": int(rPr.get("sz")) if _rPr_attr(rPr, "sz") else None,
        "b": _rPr_attr(rPr, "b") in ("1", "true"),
        "i": _rPr_attr(rPr, "i") in ("1", "true"),
        "u": _rPr_attr(rPr, "u"),
        "typeface": _typeface(rPr),
        "rPr": rPr,
    }


def _typeface(rPr):
    if rPr is None:
        return None
    latin = rPr.find(q("a:latin"))
    return latin.get("typeface") if latin is not None else None


def paragraph_props(p_el):
    """algn, entrelinha (spcPct em milesimos de %) e nivel declarados no paragrafo."""
    pPr = p_el.find(q("a:pPr"))
    algn = lvl = None
    line_pct = None
    defRPr_sz = None
    bullet = None
    if pPr is not None:
        algn = pPr.get("algn")
        lvl = int(pPr.get("lvl")) if pPr.get("lvl") else 0
        lnSpc = pPr.find(q("a:lnSpc"))
        if lnSpc is not None:
            pct = lnSpc.find(q("a:spcPct"))
            if pct is not None:
                line_pct = int(pct.get("val"))
        defRPr = pPr.find(q("a:defRPr"))
        if defRPr is not None and defRPr.get("sz"):
            defRPr_sz = int(defRPr.get("sz"))
        for tag in ("a:buChar", "a:buAutoNum", "a:buNone"):
            if pPr.find(q(tag)) is not None:
                bullet = tag.split(":")[1]
                break
    return {"algn": algn, "lvl": lvl or 0, "line_pct": line_pct,
            "defRPr_sz": defRPr_sz, "bullet": bullet}


# --- heranca de tamanho de fonte ------------------------------------------

def _lvl_defRPr_from_lstStyle(lstStyle, lvl: int):
    if lstStyle is None:
        return None
    tag = q("a:lvl%dpPr" % (lvl + 1))
    lvlPr = lstStyle.find(tag)
    if lvlPr is None:
        return None
    return lvlPr.find(q("a:defRPr"))


def _find_ph_in_part(part_el, want_type, want_idx):
    """Acha o placeholder correspondente no layout ou no master."""
    if part_el is None:
        return None
    cSld = part_el.find(q("p:cSld"))
    if cSld is None:
        return None
    spTree = cSld.find(q("p:spTree"))
    if spTree is None:
        return None
    fallback = None
    for sp in iter_shape_elements(spTree):
        t, i = ph_type(sp), ph_idx(sp)
        if t is None:
            continue
        if want_idx is not None and i == want_idx:
            return sp
        if t == want_type:
            fallback = fallback or sp
        if want_type in TITLE_TYPES and t in TITLE_TYPES:
            return sp
    return fallback


_MASTER_STYLE_FOR_PH = {
    "title": "titleStyle", "ctrTitle": "titleStyle",
    "body": "bodyStyle", "subTitle": "bodyStyle", "obj": "bodyStyle",
}


def resolve_font_size(slide, shape_el, p_el, r_el):
    """
    Tamanho efetivo em centesimos de ponto, e de onde veio.
    Cadeia: run -> paragrafo -> lstStyle da forma -> placeholder do layout ->
    placeholder do master -> p:txStyles do master -> defaultTextStyle.
    Devolve (sz, origem) — sz None significa indeterminado.
    """
    props = run_props(r_el)
    if props["sz"]:
        return props["sz"], "run"

    pp = paragraph_props(p_el)
    if pp["defRPr_sz"]:
        return pp["defRPr_sz"], "paragrafo"
    lvl = pp["lvl"]

    tx = get_txBody(shape_el)
    if tx is not None:
        d = _lvl_defRPr_from_lstStyle(tx.find(q("a:lstStyle")), lvl)
        if d is not None and d.get("sz"):
            return int(d.get("sz")), "lstStyle da forma"

    t, i = ph_type(shape_el), ph_idx(shape_el)
    if t is None:
        sz = _default_text_style_size(slide, lvl)
        if sz:
            return sz, "defaultTextStyle da apresentacao"
        return None, "indeterminado (caixa solta sem tamanho explicito)"

    layout = getattr(slide, "slide_layout", None)
    layout_el = layout._element if layout is not None else None
    lay_ph = _find_ph_in_part(layout_el, t, i)
    if lay_ph is not None:
        tx2 = get_txBody(lay_ph)
        if tx2 is not None:
            d = _lvl_defRPr_from_lstStyle(tx2.find(q("a:lstStyle")), lvl)
            if d is not None and d.get("sz"):
                return int(d.get("sz")), "layout"

    master = getattr(layout, "slide_master", None) if layout is not None else None
    master_el = master._element if master is not None else None
    if master_el is not None:
        mas_ph = _find_ph_in_part(master_el, t, i)
        if mas_ph is not None:
            tx3 = get_txBody(mas_ph)
            if tx3 is not None:
                d = _lvl_defRPr_from_lstStyle(tx3.find(q("a:lstStyle")), lvl)
                if d is not None and d.get("sz"):
                    return int(d.get("sz")), "master (placeholder)"

        styles = master_el.find(q("p:txStyles"))
        if styles is not None:
            style_name = _MASTER_STYLE_FOR_PH.get(t, "otherStyle")
            st = styles.find(q("p:%s" % style_name))
            d = _lvl_defRPr_from_lstStyle(st, lvl)
            if d is not None and d.get("sz"):
                return int(d.get("sz")), "master (txStyles/%s)" % style_name

    sz = _default_text_style_size(slide, lvl)
    if sz:
        return sz, "defaultTextStyle da apresentacao"
    return None, "indeterminado"


def _default_text_style_size(slide, lvl: int):
    """Ultimo elo da cadeia: p:defaultTextStyle em presentation.xml."""
    try:
        prs_el = slide.part.package.presentation_part._element
    except Exception:
        return None
    dts = prs_el.find(q("p:defaultTextStyle"))
    d = _lvl_defRPr_from_lstStyle(dts, lvl)
    if d is not None and d.get("sz"):
        return int(d.get("sz"))
    return None


def resolve_bold(shape_el, p_el, r_el) -> bool:
    props = run_props(r_el)
    if props["rPr"] is not None and props["rPr"].get("b") is not None:
        return props["b"]
    pPr = p_el.find(q("a:pPr"))
    if pPr is not None:
        d = pPr.find(q("a:defRPr"))
        if d is not None and d.get("b") is not None:
            return d.get("b") in ("1", "true")
    return False


# --------------------------------------------------------------------------
# Tabelas
# --------------------------------------------------------------------------
def get_tables(shape_el):
    """Devolve os elementos a:tbl dentro de um p:graphicFrame."""
    return list(shape_el.iter(q("a:tbl")))


def table_props(tbl):
    tblPr = tbl.find(q("a:tblPr"))
    first_row = tblPr is not None and tblPr.get("firstRow") in ("1", "true")
    first_col = tblPr is not None and tblPr.get("firstCol") in ("1", "true")
    rows = tbl.findall(q("a:tr"))
    merged = []
    empty_rows, empty_cols = [], []
    grid = []
    for ri, tr in enumerate(rows):
        cells = tr.findall(q("a:tc"))
        grid.append(cells)
        for ci, tc in enumerate(cells):
            if (tc.get("gridSpan") and int(tc.get("gridSpan")) > 1) or \
               (tc.get("rowSpan") and int(tc.get("rowSpan")) > 1) or \
               tc.get("hMerge") in ("1", "true") or tc.get("vMerge") in ("1", "true"):
                merged.append((ri, ci))
    for ri, cells in enumerate(grid):
        if cells and all(not _tc_text(tc).strip() for tc in cells):
            empty_rows.append(ri)
    if grid:
        ncols = max(len(c) for c in grid)
        for ci in range(ncols):
            col = [row[ci] for row in grid if ci < len(row)]
            if col and all(not _tc_text(tc).strip() for tc in col):
                empty_cols.append(ci)
    return {"first_row": first_row, "first_col": first_col,
            "n_rows": len(rows), "n_cols": len(grid[0]) if grid else 0,
            "merged": merged, "empty_rows": empty_rows, "empty_cols": empty_cols}


def _tc_text(tc) -> str:
    return "".join(t.text or "" for t in tc.iter(q("a:t")))


# --------------------------------------------------------------------------
# Apresentacao: secoes, tamanho, propriedades
# --------------------------------------------------------------------------
def get_sections(prs):
    """[(nome, [ids de slide])] a partir da extensao p14:sectionLst."""
    out = []
    for sec in prs._element.iter(q("p14:section")):
        ids = [s.get("id") for s in sec.iter(q("p14:sldId"))]
        out.append((sec.get("name") or "", ids))
    return out


def slide_size(prs):
    return prs.slide_width, prs.slide_height


def has_media(shape_el) -> bool:
    for tag in ("a:videoFile", "a:audioFile", "a:link", "p:oleObj"):
        try:
            if shape_el.find(".//" + q(tag)) is not None:
                return True
        except KeyError:
            continue
    return False


def media_kind(shape_el):
    if shape_el.find(".//" + q("a:videoFile")) is not None:
        return "video"
    if shape_el.find(".//" + q("a:audioFile")) is not None:
        return "audio"
    return None


# --------------------------------------------------------------------------
# Auxiliares de texto
# --------------------------------------------------------------------------
GENERIC_ALT = {
    "imagem", "image", "figura", "figure", "foto", "photo", "grafico",
    "gráfico", "chart", "picture", "img", "logo", "icone", "ícone", "icon",
    "diagrama", "tabela", "screenshot", "captura de tela", "sem descricao",
    "sem descrição", "descricao", "descrição", "alt", "texto alternativo",
}
RE_FILENAME = re.compile(
    r"\.(png|jpe?g|gif|bmp|svg|emf|wmf|tiff?|webp|pdf|mp4|mp3|wav)\s*$", re.I)
RE_AI_RESIDUE = re.compile(
    r"(descri[cç][aã]o gerada automaticamente|generated by ai|"
    r"conte[uú]do gerado por ia|ai[- ]generated|automatically generated)", re.I)
RE_ALT_PREFIX = re.compile(
    r"^\s*(uma?\s+)?(imagem|foto(grafia)?|figura|gr[aá]fico|ilustra[cç][aã]o|"
    r"captura de tela|screenshot|picture|image|photo|chart)\s+(de|do|da|dos|das|que|com|showing|of)\b",
    re.I)
RE_URL = re.compile(r"^\s*(https?://|www\.)", re.I)
VAGUE_LINK = {"clique aqui", "clique", "aqui", "leia mais", "saiba mais",
              "veja mais", "link", "mais", "click here", "here", "read more",
              "learn more", "this link", "este link"}

SANS_SAFE = {"arial", "calibri", "verdana", "tahoma", "segoe ui", "open sans",
             "helvetica", "helvetica neue", "roboto", "noto sans", "lato",
             "source sans pro", "atkinson hyperlegible", "opendyslexic",
             "arial narrow", "trebuchet ms", "franklin gothic book",
             "aptos", "aptos display"}


def looks_like_filename(s: str) -> bool:
    return bool(RE_FILENAME.search(s.strip()))


def is_generic_alt(s: str) -> bool:
    t = s.strip().lower().rstrip(".:;!? ")
    if not t:
        return False
    if t in GENERIC_ALT:
        return True
    return len(t) <= 3


def is_all_caps_sentence(s: str, min_words: int = 3) -> bool:
    words = [w for w in re.findall(r"[A-Za-zÀ-ÿ]{2,}", s)]
    if len(words) < min_words:
        return False
    return all(w.isupper() for w in words)


# Palavras que, escritas assim, estao necessariamente sem o acento devido.
# Sem esta lista, D08 acusava frases legitimas que simplesmente nao tem nenhuma
# palavra acentuada — como "A WCAG 2.2 chega ao arquivo pelo WCAG2ICT".
PALAVRAS_SEM_ACENTO = {
    "nao", "sao", "tambem", "voce", "ate", "apos", "alem", "atraves", "porem",
    "assessoria", "codigo", "pagina", "paginas", "tecnica", "tecnico", "publico",
    "publica", "unico", "unica", "ultimo", "ultima", "proprio", "propria",
    "criterio", "criterios", "referencia", "referencias", "descricao",
    "descricoes", "informacao", "informacoes", "acao", "acoes", "versao",
    "versoes", "opcao", "opcoes", "secao", "secoes", "atencao", "conteudo",
    "audio", "video", "videos", "area", "areas", "ideia", "titulo", "titulos",
    "numero", "numeros", "musica", "grafico", "graficos", "imagens",
    "acessivel", "acessiveis", "possivel", "possiveis", "nivel", "niveis",
    "minimo", "maximo", "obrigatorio", "necessario", "usuario", "usuarios",
    "relatorio", "auditoria", "sera", "esta", "tres", "ja", "so", "e",
    "orgao", "orgaos", "servico", "servicos", "excecao", "duvida", "voces",
    "aqui", "ambito", "avaliacao", "aplicacao", "traducao", "legenda",
}
RE_PALAVRA = re.compile(r"[a-zà-ÿ]+", re.I)


def falta_acento(s: str) -> bool:
    """True se o texto contem palavra que deveria estar acentuada e nao esta."""
    for w in RE_PALAVRA.findall(s.lower()):
        if w in PALAVRAS_SEM_ACENTO and w not in ("e", "so", "ja"):
            return True
    return False


def has_pt_accent(s: str) -> bool:
    return bool(re.search(r"[áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ]", s))
