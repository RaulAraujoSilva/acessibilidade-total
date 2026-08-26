"""
audit_design — camada N do catalogo: design e composicao.

Um slide pode cumprir as 98 regras de semantica e contraste e ainda estar
desalinhado, com figura esticada e conteudo cortado pelo rodape. Acessivel e
bem-feito nao sao a mesma coisa, e o catalogo precisa cobrir as duas.

As regras aqui nasceram de defeitos MEDIDOS num deck que a auditoria A-M havia
aprovado com zero erros:

  N01  figuras distorcidas entre 28% e 48% (add_picture com largura E altura)
  N02  tabela terminando no fim exato do slide, sob a faixa do rodape
  N04  slide de secao com o corpo ACIMA do titulo
  N09  titulo em CAIXA ALTA por heranca do layout

Todas as medidas vem de scripts/grade.py, para construtor e auditor lerem a
mesma regua.
"""
from __future__ import annotations

import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import a11y_lib as A
import grade as G


def _onde(i, el=None, extra=""):
    s = "slide %d" % i
    if el is not None:
        s += " · %s" % (A.shape_name(el) or A.local(el))
    if extra:
        s += " · %s" % extra
    return s


def _cm(v):
    return v / G.EMU_CM


def _sobrepoe(a, b, folga=0):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (ax + aw - folga <= bx or bx + bw - folga <= ax
                or ay + ah - folga <= by or by + bh - folga <= ay)


def _area_interseccao(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    dx = max(0, min(ax + aw, bx + bw) - max(ax, bx))
    dy = max(0, min(ay + ah, by + bh) - max(ay, by))
    return dx * dy


# ==========================================================================
def auditar(prs, rep):
    for r in ("N01", "N02", "N03", "N04", "N05", "N06", "N07", "N08",
              "N09", "N10"):
        rep.check(r)

    topos_titulo = {}

    for i, slide in enumerate(prs.slides, 1):
        formas = []
        for el in A.iter_shape_elements(slide.shapes._spTree):
            if A.is_hidden(el):
                continue
            box, origem = A.resolve_xfrm(slide, el)
            decorativo = A.is_decorative(el)
            formas.append({"el": el, "box": box, "origem": origem,
                           "dec": decorativo,
                           "titulo": A.is_title_placeholder(el)})

        _n09_caixa_alta(slide, i, formas, rep)
        _n01_proporcao(slide, i, rep)
        _n02_area_segura(i, formas, rep)
        _n03_sobreposicao(i, formas, rep)
        _n04_ordem_visual(i, formas, rep)
        layout_nome = ""
        try:
            layout_nome = slide.slide_layout.name or ""
        except Exception:
            pass
        _n05_ocupacao(i, formas, rep, layout_nome)
        _n06_grade(i, formas, rep)
        _n08_variedade(slide, i, rep)
        _n10_figura_pequena(i, formas, rep)

        for f in formas:
            if f["titulo"] and f["box"]:
                layout = ""
                try:
                    layout = slide.slide_layout.name or ""
                except Exception:
                    pass
                topos_titulo.setdefault(layout, []).append((i, f["box"][1]))

    _n07_titulo_consistente(topos_titulo, rep)


# --------------------------------------------------------------------------
def _n01_proporcao(slide, i, rep):
    """Figura esticada. Tolerancia de 1%: acima disso ja se ve."""
    try:
        from PIL import Image
    except ImportError:
        rep.unverified("N01", "E", "design",
                       "Pillow ausente: nao da para conferir proporcao de imagem",
                       _onde(i))
        return
    for shape in slide.shapes:
        if shape.__class__.__name__ != "Picture":
            continue
        try:
            im = Image.open(io.BytesIO(shape.image.blob))
            nativa = im.width / im.height
        except Exception:
            continue
        if not shape.width or not shape.height:
            continue
        render = shape.width / shape.height
        erro = abs(render - nativa) / nativa
        if erro > G.TOL_PROPORCAO:
            rep.fail("N01", "E", "design", _onde(i, shape._element),
                     "figura distorcida em %.1f%% — proporção nativa %.3f, "
                     "renderizada %.3f. Encaixe na caixa em vez de esticar"
                     % (erro * 100, nativa, render))


def _n02_area_segura(i, formas, rep):
    """Nada de conteudo fora da margem, e nada no rodape."""
    for f in formas:
        if f["dec"] or not f["box"]:
            continue
        l, t, w, h = f["box"]
        if t + h > G.RODAPE_Y + G.TOL_GRADE:
            rep.fail("N02", "E", "design", _onde(i, f["el"]),
                     "termina em %.2f cm, invadindo a faixa reservada do rodapé "
                     "(a partir de %.2f cm) — conteúdo cortado"
                     % (_cm(t + h), _cm(G.RODAPE_Y)))
        elif not G.dentro_da_area_segura(f["box"]):
            rep.fail("N02", "E", "design", _onde(i, f["el"]),
                     "fora da margem de segurança de %.1f cm: caixa "
                     "(%.2f, %.2f) a (%.2f, %.2f) cm"
                     % (_cm(G.MARGEM), _cm(l), _cm(t), _cm(l + w), _cm(t + h)))


def _n03_sobreposicao(i, formas, rep):
    uteis = [f for f in formas if not f["dec"] and f["box"]]
    for a in range(len(uteis)):
        for b in range(a + 1, len(uteis)):
            fa, fb = uteis[a], uteis[b]
            if not _sobrepoe(fa["box"], fb["box"], folga=G.TOL_GRADE):
                continue
            inter = _area_interseccao(fa["box"], fb["box"])
            menor = min(fa["box"][2] * fa["box"][3], fb["box"][2] * fb["box"][3])
            if menor and inter / menor > 0.10:
                rep.fail("N03", "A", "design", _onde(i, fa["el"]),
                         "sobrepõe %r em %.0f%% da área — um dos dois fica "
                         "parcialmente escondido"
                         % (A.shape_name(fb["el"]) or "?", inter / menor * 100))


def _sao_colunas(uteis):
    """True se as formas (fora o titulo) formam colunas que nao se cruzam."""
    corpo = [f for f in uteis if not f["titulo"]]
    if len(corpo) < 2:
        return False
    faixas = []
    for f in sorted(corpo, key=lambda f: f["box"][0]):
        l, _t, w, _h = f["box"]
        if faixas and l < faixas[-1][1] - G.TOL_GRADE:
            faixas[-1] = (faixas[-1][0], max(faixas[-1][1], l + w))
        else:
            faixas.append((l, l + w))
    return len(faixas) >= 2


def _n04_ordem_visual(i, formas, rep):
    """
    Ordem de leitura contra ordem visual, com a posicao RESOLVIDA.

    A regra C02 olha so o xfrm do slide; aqui a heranca entra, e e por isso
    que esta pega o caso do corpo acima do titulo.
    """
    uteis = [f for f in formas if not f["dec"] and f["box"]]
    if len(uteis) < 2:
        return
    banda = max(1, G.ALTURA // 12)
    atual = list(range(len(uteis)))
    esperado = sorted(atual, key=lambda k: (uteis[k]["box"][1] // banda,
                                            uteis[k]["box"][0]))
    if atual == esperado:
        return
    # Layout em colunas paralelas: ler uma coluna inteira e depois a outra e
    # tao correto quanto ler linha a linha — e e o que faz sentido numa
    # comparacao lado a lado. Aceita a ordem coluna-a-coluna tambem.
    por_coluna = sorted(atual, key=lambda k: (uteis[k]["box"][0],
                                              uteis[k]["box"][1]))
    if atual == por_coluna and _sao_colunas(uteis):
        return

    titulo = next((k for k, f in enumerate(uteis) if f["titulo"]), None)
    if titulo is not None and esperado.index(titulo) != 0:
        acima = uteis[esperado[0]]
        rep.fail("N04", "E", "design", _onde(i, acima["el"]),
                 "aparece ACIMA do título (y=%.2f cm contra %.2f cm), mas é "
                 "anunciado depois — a leitura contradiz o que se vê"
                 % (_cm(acima["box"][1]), _cm(uteis[titulo]["box"][1])))
    else:
        nomes = [A.shape_name(uteis[k]["el"]) or "?" for k in atual[:5]]
        rep.fail("N04", "E", "design", _onde(i),
                 "ordem de leitura diverge do fluxo visual (posição resolvida "
                 "por herança). Ordem anunciada: %s" % ", ".join(nomes))


# Capa, secao, citacao e encerramento sao slides de respiro por definicao:
# espaco vazio ali e escolha, nao desperdicio.
LAYOUTS_ESPACADOS = {"capa", "seção", "secao", "citação", "citacao",
                     "encerramento"}


def _n05_ocupacao(i, formas, rep, layout=""):
    """Area de CONTEUDO ociosa demais. Slide vazio a toa desperdica projecao."""
    if (layout or "").strip().lower() in LAYOUTS_ESPACADOS:
        return
    uteis = [f for f in formas if not f["dec"] and f["box"]]
    if not uteis:
        return
    # so a faixa de conteudo: a faixa do titulo e naturalmente parcial
    area_util = (G.LARGURA - 2 * G.MARGEM) * (G.RODAPE_Y - G.CONTEUDO_Y)
    if area_util <= 0:
        return
    # o menor retangulo que contem tudo diz mais que a soma das caixas
    corpo = [f for f in uteis if not f["titulo"]]
    if not corpo:
        return
    uteis = corpo
    x0 = min(f["box"][0] for f in uteis)
    y0 = max(G.CONTEUDO_Y, min(f["box"][1] for f in uteis))
    x1 = max(f["box"][0] + f["box"][2] for f in uteis)
    y1 = max(f["box"][1] + f["box"][3] for f in uteis)
    envolvente = (x1 - x0) * (y1 - y0)
    ocioso = 1 - envolvente / area_util
    if ocioso > G.OCIOSO_MAX:
        rep.fail("N05", "A", "design", _onde(i),
                 "%.0f%% da área útil ociosa — o conteúdo ocupa só de %.1f a "
                 "%.1f cm na vertical. Aumente o corpo ou traga mais conteúdo"
                 % (ocioso * 100, _cm(y0), _cm(y1)))


def _n06_grade(i, formas, rep):
    """Bordas que quase se alinham, e nao alinham: o olho percebe."""
    uteis = [f for f in formas if not f["dec"] and f["box"]]
    esquerdas = sorted({f["box"][0] for f in uteis})
    for a in range(len(esquerdas) - 1):
        d = esquerdas[a + 1] - esquerdas[a]
        if 0 < d <= G.TOL_GRADE * 3:
            rep.fail("N06", "A", "design", _onde(i),
                     "duas bordas esquerdas a %.2f cm e %.2f cm: diferença de "
                     "%.2f cm, pequena demais para ser intenção e grande "
                     "demais para passar despercebida"
                     % (_cm(esquerdas[a]), _cm(esquerdas[a + 1]), _cm(d)))
            break


def _n07_titulo_consistente(topos, rep):
    for layout, itens in topos.items():
        alturas = {}
        for slide_no, topo in itens:
            alturas.setdefault(round(topo / G.EMU_CM, 1), []).append(slide_no)
        if len(alturas) > 1:
            detalhe = " · ".join("%.1f cm nos slides %s"
                                 % (a, ", ".join(map(str, s[:4])))
                                 for a, s in sorted(alturas.items()))
            rep.fail("N07", "A", "design", "layout %r" % layout,
                     "título em alturas diferentes no mesmo layout: %s" % detalhe)


def _n08_variedade(slide, i, rep):
    """Excesso de tamanhos e de cores no mesmo slide vira ruido visual."""
    tamanhos, cores = set(), set()
    for el in A.iter_shape_elements(slide.shapes._spTree, recurse_groups=True):
        if A.is_decorative(el):
            continue
        for p_el, _cel in A.iter_all_paragraphs(el):
            for r_el in A.iter_runs(p_el):
                if not A.run_text(r_el).strip():
                    continue
                props = A.run_props(r_el)
                if props["sz"]:
                    tamanhos.add(props["sz"])
                rPr = props["rPr"]
                if rPr is not None:
                    for clr in rPr.iter(A.q("a:srgbClr")):
                        cores.add(clr.get("val"))
                        break
    if len(tamanhos) > 4:
        rep.fail("N08", "A", "design", _onde(i),
                 "%d tamanhos de fonte no mesmo slide (%s pt) — a hierarquia "
                 "se perde quando tudo é destaque"
                 % (len(tamanhos), ", ".join(str(t // 100)
                                             for t in sorted(tamanhos))))
    if len(cores) > 4:
        rep.fail("N08", "A", "design", _onde(i),
                 "%d cores de texto no mesmo slide" % len(cores))


def _n09_caixa_alta(slide, i, formas, rep):
    for f in formas:
        cap, origem = A.resolve_caps(slide, f["el"])
        if cap not in ("all", "small"):
            continue
        texto = " ".join(A.paragraph_text(p)
                         for p in A.iter_paragraphs(f["el"])).strip()
        if not texto:
            continue
        rep.fail("N09", "E", "design · 1.4.8", _onde(i, f["el"]),
                 "renderizado em CAIXA ALTA por herança do %s (cap=%r). O texto "
                 "no XML está em caixa mista, então a regra F06 não vê — mas na "
                 "tela sai tudo em maiúsculas, o que suprime ascendentes e "
                 "descendentes: %r" % (origem, cap, texto[:40]))


def _n10_figura_pequena(i, formas, rep):
    for f in formas:
        if f["dec"] or not f["box"]:
            continue
        if A.local(f["el"]) != "pic":
            continue
        menor = min(f["box"][2], f["box"][3])
        if menor < G.FIGURA_MIN:
            rep.fail("N10", "A", "design", _onde(i, f["el"]),
                     "figura com menor lado de %.1f cm; abaixo de %.1f cm o "
                     "detalhe se perde na projeção"
                     % (_cm(menor), _cm(G.FIGURA_MIN)))
