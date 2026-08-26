"""
importar — a porta de entrada: de um TEXTO ou de uma APRESENTACAO para o roteiro.

Sem isto a ferramenta so servia a quem escrevesse o `roteiro.yaml` a mao, e o
caso real e outro: a pessoa TEM um `.pptx` que precisa ficar acessivel, ou TEM
um texto que precisa virar apresentacao.

    python scripts/importar.py entrada.pptx -o pasta/     # apresentacao -> roteiro
    python scripts/importar.py texto.md     -o pasta/     # texto -> roteiro

O que sai e um `roteiro.yaml` que o pipeline inteiro consome:

    python scripts/montar_tudo.py pasta/ -o entrega/

DUAS REGRAS QUE GOVERNAM ESTE ARQUIVO:

1. **Nao inventa conteudo.** O que nao existe na origem sai como marcador
   `[FALTA: ...]`, e `validar_roteiro` recusa o roteiro enquanto o marcador
   estiver la. Um alt text gerado por adivinhacao e pior que a ausencia dele:
   a ausencia se ve, a adivinhacao passa.

2. **Nao remedia em silencio.** O relatorio de importacao diz o que veio, o que
   faltou e o que foi partido, para que a pessoa saiba onde precisa escrever.

O que a importacao de `.pptx` recupera: titulo de cada slide, paragrafos,
tabelas com cabecalho, figuras (arquivo, alt text existente) e as notas do
orador. O que ela NAO recupera: intencao. Slide sem titulo, alt text ausente ou
generico e tabela sem cabecalho viram marcador para alguem decidir.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import a11y_lib as A

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

FALTA = "[FALTA: %s]"
MAX_PARAGRAFOS = 6          # o mesmo limite de F07 que o construtor cobra
MAX_LINHA = 80              # WCAG 1.4.8


# ==========================================================================
# De uma apresentacao existente
# ==========================================================================
def de_pptx(caminho: str) -> tuple:
    from pptx import Presentation

    prs = Presentation(caminho)
    cp = prs.core_properties
    avisos = []

    slides = []
    for i, slide in enumerate(prs.slides, 1):
        spec, av = _slide_para_spec(slide, i)
        slides.append(spec)
        avisos.extend(av)

    roteiro = {
        "apresentacao": {
            "titulo": (cp.title or "").strip() or FALTA % "título da apresentação",
            "autor": (cp.author or "").strip() or FALTA % "autor",
            "idioma": (cp.language or "pt-BR").strip() or "pt-BR",
            "assunto": (cp.subject or "").strip(),
            "palavras_chave": (cp.keywords or "").strip(),
            "resumo": (cp.comments or "").strip(),
        },
        "slides": slides,
    }
    return roteiro, avisos


def _slide_para_spec(slide, numero):
    avisos = []
    titulo = ""
    paragrafos, figuras, tabelas = [], [], []

    for el in A.iter_shape_elements(slide.shapes._spTree):
        if A.is_decorative(el) or A.is_hidden(el):
            continue
        if A.is_title_placeholder(el):
            titulo = " ".join(A.paragraph_text(p).strip()
                              for p, _ in A.iter_all_paragraphs(el)).strip()
            continue
        if A.media_kind(el):
            avisos.append("slide %d: mídia embutida não é importada; ela é "
                          "regerada pelo pipeline" % numero)
            continue
        if el.tag == A.q("p:pic"):
            figuras.append(_figura(el, numero, avisos))
            continue
        tbl = el.find(".//" + A.q("a:tbl"))
        if el.tag == A.q("p:graphicFrame") and tbl is not None:
            tabelas.append(_tabela(el, tbl, numero, avisos))
            continue
        for p_el, celula in A.iter_all_paragraphs(el):
            if celula is not None:
                continue
            t = A.paragraph_text(p_el).strip()
            if t:
                paragrafos.append(t)

    if not titulo:
        titulo = FALTA % ("título do slide %d" % numero)
        avisos.append("slide %d: sem placeholder de título — o texto que "
                      "parecia título virou parágrafo (regra B01)" % numero)

    spec = {"titulo": titulo}
    if paragrafos:
        spec["conteudo"] = paragrafos
    if figuras:
        spec["figura"] = figuras[0]
        if len(figuras) > 1:
            avisos.append("slide %d: %d figuras; o roteiro leva uma por slide, "
                          "as outras precisam de slide próprio"
                          % (numero, len(figuras)))
    if tabelas:
        spec["tabela"] = tabelas[0]

    try:
        notas = slide.notes_slide.notes_text_frame.text.strip()
    except Exception:
        notas = ""
    if notas:
        spec["notas"] = notas

    return spec, avisos


def _figura(el, numero, avisos):
    alt = (A.get_alt_text(el) or "").strip()
    nome = A.shape_name(el) or "Figura"
    if not alt:
        alt = FALTA % ("texto alternativo da figura do slide %d" % numero)
        avisos.append("slide %d: figura sem texto alternativo (regra D01)" % numero)
    elif re.match(r"^(imagem|figura|picture|image|foto)\s*\d*$", alt, re.I) \
            or re.search(r"\.(png|jpe?g|gif|webp)$", alt, re.I):
        avisos.append("slide %d: alt text genérico (%r) — reescreva dizendo "
                      "POR QUE a figura está ali (regra D05)" % (numero, alt[:30]))
        alt = FALTA % ("texto alternativo real, o atual é %r" % alt[:30])
    return {
        "nome": nome,
        "arquivo": FALTA % "caminho do arquivo da figura, por modo de cor",
        "alt": alt,
        "descricao_longa": FALTA % ("descrição longa da figura do slide %d"
                                    % numero),
    }


def _tabela(el, tbl, numero, avisos):
    linhas = []
    for tr in tbl.iter(A.q("a:tr")):
        celulas = []
        for tc in tr.iter(A.q("a:tc")):
            texto = " ".join(A.paragraph_text(p).strip()
                             for p in tc.iter(A.q("a:p")))
            celulas.append(texto.strip())
        if any(celulas):
            linhas.append(celulas)

    tblPr = tbl.find(A.q("a:tblPr"))
    tem_cabecalho = tblPr is not None and tblPr.get("firstRow") == "1"
    if not tem_cabecalho:
        avisos.append("slide %d: tabela sem linha de cabeçalho — a primeira "
                      "linha foi assumida como cabeçalho (regra G01)" % numero)

    return {
        "nome": FALTA % ("nome da tabela do slide %d" % numero),
        "alt": FALTA % ("o que a tabela mostra, no slide %d" % numero),
        "cabecalho": linhas[0] if linhas else [],
        "linhas": linhas[1:] if len(linhas) > 1 else [],
    }


# ==========================================================================
# De um texto corrido
# ==========================================================================
def de_texto(caminho: str) -> tuple:
    with open(caminho, encoding="utf-8") as f:
        bruto = f.read()

    avisos = []
    blocos = _blocos_do_texto(bruto)
    if not blocos:
        raise SystemExit("texto vazio ou sem estrutura reconhecivel")

    titulo_geral = blocos[0]["titulo"]
    slides = [{
        "tipo": "capa",
        "titulo": titulo_geral,
        "subtitulo": [FALTA % "subtítulo, autor e contexto"],
    }]

    for b in blocos:
        # o titulo do documento vira a capa; repeti-lo como slide criaria um
        # slide vazio E um titulo duplicado, que a regra B03 reprova
        if b is blocos[0] and not b["paragrafos"]:
            continue
        partes = _partir(b["paragrafos"], avisos, b["titulo"])
        for k, pedaco in enumerate(partes, 1):
            t = b["titulo"] if len(partes) == 1 else "%s (%d de %d)" % (
                b["titulo"], k, len(partes))
            slides.append({"titulo": t, "conteudo": pedaco})

    roteiro = {
        "apresentacao": {
            "titulo": titulo_geral,
            "autor": FALTA % "autor",
            "idioma": "pt-BR",
            "assunto": "",
            "palavras_chave": "",
            "resumo": "",
        },
        "slides": slides,
    }
    return roteiro, avisos


def _blocos_do_texto(bruto):
    """
    Quebra por titulo de Markdown; sem titulo, por linha em branco.

    Nao ha adivinhacao semantica aqui de proposito: quem decide o que e um
    slide e a estrutura que o autor ja deu ao texto.
    """
    linhas = bruto.replace("\r\n", "\n").split("\n")
    blocos, atual = [], None
    for linha in linhas:
        m = re.match(r"^(#{1,6})\s+(.+?)\s*#*$", linha)
        if m:
            atual = {"titulo": m.group(2).strip(), "paragrafos": []}
            blocos.append(atual)
            continue
        t = linha.strip()
        if not t:
            continue
        t = re.sub(r"^[-*+•]\s+", "", t)
        if atual is None:
            atual = {"titulo": t[:60], "paragrafos": []}
            blocos.append(atual)
            continue
        atual["paragrafos"].append(t)
    return [b for b in blocos if b["titulo"]]


def _partir(paragrafos, avisos, titulo):
    """Um slide nao aguenta mais de 6 paragrafos nem linha acima de 80."""
    curtos = []
    for p in paragrafos:
        if len(p) <= MAX_LINHA:
            curtos.append(p)
            continue
        # quebra no fim de frase mais proximo do limite
        resto = p
        while len(resto) > MAX_LINHA:
            corte = resto.rfind(". ", 0, MAX_LINHA)
            if corte < 20:
                corte = resto.rfind(" ", 0, MAX_LINHA)
            if corte < 20:
                break
            curtos.append(resto[:corte + 1].strip())
            resto = resto[corte + 1:].strip()
        if resto:
            curtos.append(resto)
        avisos.append("%r: parágrafo acima de %d caracteres foi partido — "
                      "confira se a quebra faz sentido" % (titulo[:30], MAX_LINHA))

    if not curtos:
        return [[FALTA % "conteúdo deste slide"]]
    return [curtos[i:i + MAX_PARAGRAFOS]
            for i in range(0, len(curtos), MAX_PARAGRAFOS)]


# ==========================================================================
def escrever_yaml(roteiro, destino, avisos):
    try:
        import yaml
    except ImportError:
        import json
        with open(destino.replace(".yaml", ".json"), "w", encoding="utf-8") as f:
            json.dump(roteiro, f, ensure_ascii=False, indent=2)
        return destino.replace(".yaml", ".json")

    cabecalho = (
        "# Roteiro importado por scripts/importar.py.\n"
        "#\n"
        "# Os marcadores [FALTA: ...] sao propositais: a importacao nao inventa\n"
        "# conteudo. Preencha cada um antes de construir — o build recusa o\n"
        "# roteiro enquanto eles estiverem aqui.\n"
        "#\n"
        "# Depois: python scripts/montar_tudo.py <esta pasta> -o entrega/\n"
        "#\n")
    if avisos:
        cabecalho += "# Avisos da importacao:\n"
        for a in avisos[:40]:
            cabecalho += "#   - %s\n" % a
        cabecalho += "#\n"

    with open(destino, "w", encoding="utf-8") as f:
        f.write(cabecalho)
        yaml.safe_dump(roteiro, f, allow_unicode=True, sort_keys=False,
                       default_flow_style=False, width=100)
    return destino


def contar_faltas(roteiro):
    n = 0
    pilha = [roteiro]
    while pilha:
        atual = pilha.pop()
        if isinstance(atual, dict):
            pilha.extend(atual.values())
        elif isinstance(atual, list):
            pilha.extend(atual)
        elif isinstance(atual, str) and atual.startswith("[FALTA:"):
            n += 1
    return n


def main():
    ap = argparse.ArgumentParser(
        description="Importa .pptx ou texto para roteiro.yaml")
    ap.add_argument("entrada")
    ap.add_argument("-o", "--saida", default=".",
                    help="pasta onde o roteiro.yaml e escrito")
    args = ap.parse_args()

    if not os.path.exists(args.entrada):
        print("arquivo nao encontrado: %s" % args.entrada)
        return 2

    ext = os.path.splitext(args.entrada)[1].lower()
    if ext == ".pptx":
        roteiro, avisos = de_pptx(args.entrada)
        origem = "apresentação"
    elif ext in (".md", ".txt", ".markdown"):
        roteiro, avisos = de_texto(args.entrada)
        origem = "texto"
    else:
        print("extensao nao suportada: %s (use .pptx, .md ou .txt)" % ext)
        return 2

    os.makedirs(args.saida, exist_ok=True)
    destino = escrever_yaml(roteiro, os.path.join(args.saida, "roteiro.yaml"),
                            avisos)

    faltas = contar_faltas(roteiro)
    print("importado de %s: %d slides" % (origem, len(roteiro["slides"])))
    print("  %s" % destino)
    if avisos:
        print("\n%d aviso(s) da importação:" % len(avisos))
        for a in avisos[:15]:
            print("  - %s" % a)
        if len(avisos) > 15:
            print("  ... e mais %d" % (len(avisos) - 15))
    if faltas:
        print("\n%d marcador(es) [FALTA: ...] a preencher." % faltas)
        print("A importação NÃO inventa conteúdo: alt text adivinhado passa")
        print("despercebido, ausência de alt text não. Preencha e então rode:")
        print("  python scripts/montar_tudo.py %s -o entrega/" % args.saida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
