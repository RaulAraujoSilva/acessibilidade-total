"""
grade — o sistema de medidas do projeto.

Um slide acessivel nao e um slide feio. Composicao tambem se audita, e para
auditar e preciso primeiro DECIDIR onde as coisas ficam. Este modulo e essa
decisao, num lugar so, para o construtor e o auditor lerem a mesma regua.

Tudo em EMU (914400 por polegada, 360000 por centimetro).
"""
from __future__ import annotations

EMU_CM = 360000
EMU_POL = 914400


def cm(valor: float) -> int:
    return int(round(valor * EMU_CM))


# --------------------------------------------------------------------------
# Area do slide
# --------------------------------------------------------------------------
LARGURA = cm(33.87)          # 13,333 pol — 16:9
ALTURA = cm(19.05)           # 7,5 pol

MARGEM = cm(1.4)             # margem de seguranca: nada de conteudo fora dela

# Faixas verticais fixas. O rodape e ZONA PROIBIDA para conteudo — foi
# exatamente ali que a tabela do deck anterior perdeu a ultima linha.
TITULO_Y = cm(1.4)
TITULO_H = cm(2.2)
CONTEUDO_Y = cm(4.2)
CONTEUDO_FIM = cm(17.4)
CONTEUDO_H = CONTEUDO_FIM - CONTEUDO_Y
RODAPE_Y = cm(17.9)          # daqui para baixo, so decorativo
FAIXA_H = cm(0.55)           # espessura da faixa estetica do rodape

# --------------------------------------------------------------------------
# Grade horizontal: 12 colunas
# --------------------------------------------------------------------------
COLUNAS = 12
MEDIANIZ = cm(0.5)
UTIL = LARGURA - 2 * MARGEM
COLUNA = (UTIL - (COLUNAS - 1) * MEDIANIZ) // COLUNAS


def x(coluna: int) -> int:
    """Coordenada X do inicio da coluna (0 a 11)."""
    return MARGEM + coluna * (COLUNA + MEDIANIZ)


def larg(n: int) -> int:
    """Largura de um bloco que ocupa n colunas."""
    return n * COLUNA + (n - 1) * MEDIANIZ


def bloco(coluna: int, n: int, y: int, altura: int):
    """(left, top, width, height) de um bloco na grade."""
    return x(coluna), y, larg(n), altura


# --------------------------------------------------------------------------
# Escala tipografica, em pontos
# --------------------------------------------------------------------------
TIPO = {
    "capa": 46,
    "titulo": 34,
    "secao": 40,
    "corpo": 24,
    "corpo_denso": 20,
    "apoio": 18,
    "tabela": 18,
    "cartao_titulo": 22,
    "cartao_corpo": 18,   # piso da regra F02
    "destaque_numero": 96,
    "destaque_rotulo": 26,
    "citacao": 32,
    "credito": 18,
    "display_min": 40,    # a partir daqui e display, nao corpo de leitura
}

ENTRELINHA_CORPO = 150000     # 1,5
ENTRELINHA_TITULO = 100000    # 1,0 — display nao precisa de 1,5 (regra F05)

# --------------------------------------------------------------------------
# Tolerancias usadas pela camada N do catalogo
# --------------------------------------------------------------------------
TOL_PROPORCAO = 0.01          # N01: 1% de erro de proporcao ja e visivel
TOL_GRADE = cm(0.12)          # N06: abaixo disso, considera-se alinhado
OCIOSO_MAX = 0.42             # N05: fracao maxima da area util vazia
FIGURA_MIN = cm(6.0)          # N10: menor lado util de uma figura


def dentro_da_area_segura(box) -> bool:
    l, t, w, h = box
    return (l >= MARGEM - TOL_GRADE and t >= MARGEM - TOL_GRADE
            and l + w <= LARGURA - MARGEM + TOL_GRADE
            and t + h <= RODAPE_Y + TOL_GRADE)


def encaixar(nativo_w: int, nativo_h: int, caixa_w: int, caixa_h: int):
    """
    Encaixa uma figura na caixa PRESERVANDO a proporcao (regra N01).

    Devolve (largura, altura, folga_x, folga_y). A folga serve para centralizar
    dentro da caixa em vez de esticar — esticar era o defeito que distorcia
    todas as figuras do deck anterior entre 28% e 48%.
    """
    if not nativo_w or not nativo_h:
        return caixa_w, caixa_h, 0, 0
    escala = min(caixa_w / nativo_w, caixa_h / nativo_h)
    w = int(nativo_w * escala)
    h = int(nativo_h * escala)
    return w, h, (caixa_w - w) // 2, (caixa_h - h) // 2
