"""
gen_diagramas — diagramas tecnicos determinísticos, via HTML -> PNG.

POR QUE NAO gpt-image-2 AQUI: modelo de imagem ainda erra colocacao e
acentuacao de texto em PT-BR, e um diagrama tecnico com 10+ rotulos e
justamente o pior caso. Num material sobre acessibilidade, entregar um
diagrama com "acessibilidode" escrito e autodestruicao.

HTML -> PNG da tres coisas que o modelo nao da:
  1. texto exato, com acento certo, sempre;
  2. cores exatas — entao o mesmo diagrama sai nas TRES paletas, e cada modo
     de exibicao recebe a sua versao;
  3. resultado identico a cada execucao, entao o deck e reproduzivel.

gpt-image-2 continua util para figura ILUSTRATIVA (poucas palavras): ver
gen_images.py.

    python scripts/gen_diagramas.py --spec diagramas.yaml --saida figuras/
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PALETA = os.path.join(RAIZ, "assets", "paleta-okabe-ito.json")

LARGURA, ALTURA, ESCALA = 1200, 800, 2


# --------------------------------------------------------------------------
# Paletas
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# HACHURA POR SERIE — o modo daltonico nao muda so de cor, muda de TEXTURA.
#
# A observacao que originou isto: o modo daltonico e o padrao pareciam iguais.
# E eram, quase: a paleta Okabe-Ito ja e cega-segura por construcao, entao o
# modo daltonico nunca esteve corrigindo uma paleta insegura — ele so troca
# duas series (verde-azulado e roxo-avermelhado por cinza e vermelhao). Uma
# versao que promete diferenca e entrega um fundo 2% mais frio nao se sustenta.
#
# A diferenca real e **codificacao redundante**: cada serie ganha um angulo de
# hachura proprio. Quem nao distingue as cores distingue a trama; quem imprime
# em preto e branco tambem. WCAG 1.4.1 pede que a cor nao seja o unico meio —
# aqui ela deixa de ser, de fato e nao so no rodape do relatorio.
ANGULOS = (45, 135, 90, 0, 30, 120)


def _hachura(cor, i, ativa):
    """Faixa de cor com trama propria da serie. Sem `ativa`, cor lisa."""
    if not ativa:
        return "background:%s" % cor
    ang = ANGULOS[i % len(ANGULOS)]
    return ("background:repeating-linear-gradient(%ddeg, %s 0 6px, "
            "rgba(255,255,255,.55) 6px 11px)" % (ang, cor))


def carregar_paletas():
    with open(PALETA, encoding="utf-8") as f:
        p = json.load(f)
    marcas = {s["nome"]: s["marca_min_3_1"] for s in p["series"]}
    texto = {s["nome"]: s["texto_min_4_5_1"] for s in p["series"]}
    return {
        "padrao": {
            "fundo": p["fundos"]["padrao"], "texto": p["textos"]["sobre_claro"],
            "caixa": "#FFFFFF", "borda": texto["azul"], "destaque": texto["azul"],
            "sobre_destaque": "#FFFFFF", "suave": "#6B6B6B",
            "series": [marcas["azul"], marcas["laranja"], marcas["verde_azulado"],
                       marcas["roxo_avermelhado"], marcas["vermelhao"],
                       marcas["cinza"]],
        },
        "alto_contraste": {
            "fundo": "#000000", "texto": "#FFFFFF", "caixa": "#000000",
            "borda": "#FFFFFF", "destaque": "#F0E442", "sobre_destaque": "#000000",
            "suave": "#D0D0D0",
            "series": ["#56B4E9", "#E69F00", "#009E73", "#F0E442", "#CC79A7",
                       "#FFFFFF"],
        },
        "daltonico": {
            "hachura": True,
            "fundo": p["fundos"]["daltonico_seguro"],
            "texto": p["textos"]["sobre_claro"], "caixa": "#FFFFFF",
            "borda": texto["azul"], "destaque": texto["azul"],
            "sobre_destaque": "#FFFFFF", "suave": "#5A5A5A",
            "series": [marcas["azul"], marcas["laranja"], marcas["cinza"],
                       marcas["vermelhao"], texto["azul"], marcas["verde_azulado"]],
        },
    }


# --------------------------------------------------------------------------
# HTML
# --------------------------------------------------------------------------
CSS = """
* { margin:0; padding:0; box-sizing:border-box; }
body {
  width:%(w)dpx; min-height:%(h)dpx; background:%(fundo)s; color:%(texto)s;
  font-family:'Segoe UI',Calibri,Arial,sans-serif; padding:48px 56px;
  display:flex; flex-direction:column; gap:28px;
}
h1 { font-size:40px; font-weight:700; line-height:1.15; letter-spacing:-.4px; }
.sub { font-size:22px; color:%(suave)s; line-height:1.4; }
.cadeia { display:flex; align-items:stretch; gap:0; flex:1; }
.elo {
  flex:1; background:%(caixa)s; border:4px solid %(borda)s; border-radius:16px;
  padding:26px 22px; display:flex; flex-direction:column; gap:10px;
  justify-content:center;
}
.elo .t { font-size:29px; font-weight:700; line-height:1.15; }
.elo .d { font-size:20px; color:%(suave)s; line-height:1.35; }
.seta {
  display:flex; align-items:center; justify-content:center; width:64px;
  font-size:44px; font-weight:700; color:%(borda)s;
}
/* Trama por serie: no modo daltonico cada serie tem um angulo de hachura
   proprio, para que a distincao nao dependa de perceber a cor. */
.elo { position:relative; }
.elo .trama { height:14px; border-radius:7px; margin:0 0 12px; }
.camada { position:relative; overflow:hidden; }
.camada .trama-lateral {
  position:absolute; left:0; top:0; bottom:0; width:16px;
}
.camadas { display:flex; flex-direction:column; gap:12px; flex:1; }
.camada {
  display:flex; align-items:center; gap:20px; border-radius:12px;
  padding:14px 22px 14px 34px; background:%(caixa)s;
}
.camada .id {
  font-size:30px; font-weight:700; width:44px; text-align:center;
  color:%(texto)s;
}
.camada .nome { font-size:25px; font-weight:600; flex:1; }
.camada .qtd { font-size:21px; color:%(suave)s; white-space:nowrap; }
.passos { display:flex; flex-direction:column; gap:11px; flex:1; }
.passo { display:flex; align-items:center; gap:20px; }
.passo .n {
  width:56px; height:56px; border-radius:50%%; background:%(destaque)s;
  color:%(sobre_destaque)s; font-size:27px; font-weight:700;
  display:flex; align-items:center; justify-content:center; flex-shrink:0;
}
.passo .txt { font-size:25px; line-height:1.3; }
.passo .txt b { font-weight:700; }
.hub { display:flex; flex-direction:column; align-items:center; gap:24px; flex:1;
       justify-content:center; }
.nucleo {
  background:%(destaque)s; color:%(sobre_destaque)s; border-radius:18px;
  padding:22px 44px; font-size:34px; font-weight:700; text-align:center;
}
.satelites { display:flex; flex-wrap:wrap; gap:14px; justify-content:center;
             max-width:1000px; }
.satelite {
  background:%(caixa)s; border:3px solid %(borda)s; border-radius:12px;
  padding:14px 22px; font-size:24px; font-weight:600;
}
.rodape { font-size:19px; color:%(suave)s; line-height:1.35; }
"""


def _elo(item, cor, i=0, hachura=False):
    return ('<div class="elo" style="border-color:%s">'
            '<div class="trama" style="%s"></div>'
            '<div class="t">%s</div><div class="d">%s</div></div>'
            % (cor, _hachura(cor, i, hachura), item["titulo"],
               item.get("detalhe", "")))


def montar_html(spec, pal):
    larg = spec.get("largura", LARGURA)
    alt = spec.get("altura", ALTURA)
    corpo = []
    tipo = spec["tipo"]
    itens = spec.get("itens", [])

    if tipo == "cadeia":
        partes = []
        for i, it in enumerate(itens):
            partes.append(_elo(it, pal["series"][i % len(pal["series"])],
                               i, pal.get("hachura", False)))
            if i < len(itens) - 1:
                partes.append('<div class="seta">&#8594;</div>')
        corpo.append('<div class="cadeia">%s</div>' % "".join(partes))

    elif tipo == "camadas":
        linhas = []
        for i, it in enumerate(itens):
            cor = pal["series"][i % len(pal["series"])]
            linhas.append(
                '<div class="camada" style="border-left-color:%s">'
                '<div class="trama-lateral" style="%s"></div>'
                '<div class="id" style="color:%s">%s</div>'
                '<div class="nome">%s</div><div class="qtd">%s</div></div>'
                % (cor, _hachura(cor, i, pal.get("hachura", False)), cor,
                   it.get("id", ""), it["titulo"], it.get("detalhe", "")))
        corpo.append('<div class="camadas">%s</div>' % "".join(linhas))

    elif tipo == "passos":
        linhas = []
        for i, it in enumerate(itens, 1):
            cor = pal["series"][(i - 1) % len(pal["series"])]
            linhas.append(
                '<div class="passo"><div class="n" style="%s">%d</div>'
                '<div class="txt"><b>%s</b>%s</div></div>'
                % (_hachura(pal["destaque"], i - 1, pal.get("hachura", False)),
                   i, it["titulo"],
                   (" — " + it["detalhe"]) if it.get("detalhe") else ""))
        corpo.append('<div class="passos">%s</div>' % "".join(linhas))

    elif tipo == "hub":
        sat = "".join('<div class="satelite">%s</div>' % s for s in spec["satelites"])
        corpo.append('<div class="hub"><div class="nucleo">%s</div>'
                     '<div class="satelites">%s</div></div>'
                     % (spec["nucleo"], sat))
    else:
        raise ValueError("tipo de diagrama desconhecido: %r" % tipo)

    # Por padrao o diagrama NAO repete o proprio titulo: quem o carrega e o
    # titulo do slide, e repetir rouba espaco e faz o leitor de tela ouvir a
    # mesma frase duas vezes. cabecalho: true so para uso avulso.
    cabecalho = ""
    if spec.get("cabecalho"):
        cabecalho = "<h1>%s</h1>" % spec["titulo"]
        if spec.get("subtitulo"):
            cabecalho += '<div class="sub">%s</div>' % spec["subtitulo"]
    rodape = ('<div class="rodape">%s</div>' % spec["rodape"]) if spec.get("rodape") else ""

    css = CSS % dict(w=larg, h=alt, **pal)
    return ("<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'>"
            "<style>%s</style></head><body>%s%s%s</body></html>"
            % (css, cabecalho, "".join(corpo), rodape))


# --------------------------------------------------------------------------
# Renderizacao
# --------------------------------------------------------------------------
def renderizar(htmls, saidas):
    """Renderiza varios HTML de uma vez, reaproveitando o navegador."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError(
            "playwright ausente. Rode:\n"
            "  pip install playwright && playwright install chromium")

    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        for html, saida in zip(htmls, saidas):
            pagina = nav.new_page(device_scale_factor=ESCALA)
            pagina.set_content(html, wait_until="load")
            os.makedirs(os.path.dirname(os.path.abspath(saida)), exist_ok=True)
            # min-height, nao height: se o conteudo passar da altura pedida,
            # o diagrama CRESCE em vez de ser cortado. Medir por scrollHeight
            # (bounding box devolve a altura declarada, nao a real, e foi assim
            # que a ultima camada e o rodape sumiram na primeira versao).
            dim = pagina.evaluate(
                "() => ({w: document.body.scrollWidth,"
                " h: document.body.scrollHeight})")
            pagina.set_viewport_size({"width": int(dim["w"]),
                                      "height": int(dim["h"])})
            pagina.screenshot(path=saida)
            pagina.close()
        nav.close()


def gerar(spec_arquivo, pasta_saida, modos=("padrao", "alto_contraste", "daltonico")):
    with open(spec_arquivo, encoding="utf-8") as f:
        bruto = f.read()
    if spec_arquivo.lower().endswith((".yaml", ".yml")):
        import yaml
        specs = yaml.safe_load(bruto)
    else:
        specs = json.loads(bruto)

    paletas = carregar_paletas()
    htmls, saidas, mapa = [], [], {}

    for spec in specs["diagramas"]:
        nome = spec["nome"]
        mapa[nome] = {}
        for modo in modos:
            arq = os.path.join(pasta_saida, "%s-%s.png" % (nome, modo))
            htmls.append(montar_html(spec, paletas[modo]))
            saidas.append(arq)
            mapa[nome][modo] = arq.replace("\\", "/")
        if not spec.get("alt", "").strip():
            raise ValueError("diagrama %r sem alt text" % nome)
        if not spec.get("descricao_longa", "").strip():
            raise ValueError("diagrama %r sem descricao longa" % nome)

    renderizar(htmls, saidas)
    return mapa, specs["diagramas"]


def main():
    ap = argparse.ArgumentParser(description="Gera diagramas tecnicos por paleta")
    ap.add_argument("spec")
    ap.add_argument("-o", "--saida", default="figuras")
    args = ap.parse_args()

    try:
        mapa, specs = gerar(args.spec, args.saida)
    except (RuntimeError, ValueError) as e:
        print("ERRO: %s" % e)
        return 2

    for nome, arqs in mapa.items():
        print("%-24s %d paletas" % (nome, len(arqs)))
    print("\n%d diagramas · %d arquivos em %s/"
          % (len(mapa), sum(len(v) for v in mapa.values()), args.saida))
    return 0


if __name__ == "__main__":
    sys.exit(main())
