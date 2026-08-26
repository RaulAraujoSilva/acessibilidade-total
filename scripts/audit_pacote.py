"""
audit_pacote — camada O: o pacote entregue e as versoes paralelas.

As camadas A a N auditam UM arquivo. Esta audita o CONJUNTO, e existe por causa
de uma decisao: os modos de cor deixaram de conviver num arquivo so e passaram a
ser arquivos separados.

O desenho antigo — hub e tres secoes no mesmo .pptx — garantia a paridade de
graca, porque os tres modos nasciam do mesmo laco. Em troca, punia justamente
quem navega em sequencia: de 85 slides, 57 eram repeticao, e a transcricao
linear saia com o conteudo tres vezes.

Arquivos separados resolvem isso e criam um risco novo: as versoes podem
divergir. O projeto inteiro se apoia em "o que nao foi verificado nao e
conformidade", entao a paridade virou teste, nao promessa.

    python scripts/audit_pacote.py deck-padrao.pptx deck-alto-contraste.pptx \\
        deck-daltonico-seguro.pptx --md auditoria-pacote.md

| Regra | Sev | O que pega |
|-------|-----|------------|
| O01   | E   | Texto divergente entre as versoes |
| O02   | E   | Recurso presente numa versao e ausente noutra |
| O03   | A   | Pacote sem arquivo que declare qual versao e qual |

O que NAO e divergencia: a paleta (e o proposito das versoes) e o titulo do
documento nas propriedades, que leva o nome do modo de proposito — e o que o
leitor de tela anuncia ao abrir.
"""
from __future__ import annotations

import argparse
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import a11y_lib as A

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

NAO_CONFORME = "nao conforme"
NAO_VERIFICADO = "nao verificado"

# nomes de arquivo que servem como declaracao do pacote (regra O03)
DECLARACOES = ("leia-me.md", "leiame.md", "readme.md", "leia-me.txt")


class Pacote:
    def __init__(self, arquivos):
        self.arquivos = arquivos
        self.findings = []
        self.evaluated = set()

    def check(self, regra):
        self.evaluated.add(regra)

    def fail(self, regra, sev, criterio, onde, detalhe):
        self.evaluated.add(regra)
        self.findings.append({
            "regra": regra, "severidade": sev, "criterio": criterio,
            "veredito": NAO_CONFORME, "onde": onde, "detalhe": detalhe})

    def unverified(self, regra, sev, criterio, detalhe, onde="—"):
        self.findings.append({
            "regra": regra, "severidade": sev, "criterio": criterio,
            "veredito": NAO_VERIFICADO, "onde": onde, "detalhe": detalhe})

    def counts(self):
        c = defaultdict(int)
        for f in self.findings:
            if f["veredito"] == NAO_CONFORME:
                c[f["severidade"]] += 1
            else:
                c["nao_verificado"] += 1
        return dict(c)


def _texto_do_slide(slide):
    """
    Tudo o que uma pessoa LE ou OUVE no slide, em ordem de leitura.

    Inclui alt text e descricao longa: sao conteudo para quem usa leitor de
    tela, e uma versao que perdesse a descricao seria conteudo diferente por
    deficiencia — exatamente o que a camada O existe para impedir.
    """
    pedacos = []
    for el in A.iter_shape_elements(slide.shapes._spTree):
        if A.is_decorative(el):
            continue
        alt = (A.get_alt_text(el) or "").strip()
        if alt:
            pedacos.append("[alt] " + alt)
        for p_el, _ in A.iter_all_paragraphs(el):
            t = "".join(r.text or "" for r in p_el.iter(A.q("a:t"))).strip()
            if t:
                pedacos.append(t)
    try:
        notas = slide.notes_slide.notes_text_frame.text.strip()
    except Exception:
        notas = ""
    if notas:
        pedacos.append("[notas] " + notas)
    return pedacos


def _recursos_do_slide(slide):
    """Que recursos o slide carrega, sem olhar o conteudo deles."""
    r = defaultdict(int)
    for el in A.iter_shape_elements(slide.shapes._spTree):
        if A.media_kind(el):
            r["midia"] += 1
        elif el.tag == A.q("p:pic"):
            r["figura"] += 1
        elif el.tag == A.q("p:graphicFrame") and el.find(".//" + A.q("a:tbl")) is not None:
            r["tabela"] += 1
    return dict(r)


def _ler(caminho):
    from pptx import Presentation

    prs = Presentation(caminho)
    slides = list(prs.slides)
    return {
        "caminho": caminho,
        "nome": os.path.basename(caminho),
        "slides": len(slides),
        "texto": [_texto_do_slide(s) for s in slides],
        "recursos": [_recursos_do_slide(s) for s in slides],
    }


def auditar(arquivos, pasta=None) -> Pacote:
    rep = Pacote(arquivos)
    if len(arquivos) < 2:
        rep.unverified("O01", "E", "paridade entre versoes",
                       "so um arquivo informado — nao ha o que comparar")
        rep.unverified("O02", "E", "paridade de recursos",
                       "so um arquivo informado — nao ha o que comparar")
    else:
        versoes = [_ler(a) for a in arquivos]
        _o01(rep, versoes)
        _o02(rep, versoes)

    _o03(rep, pasta or (os.path.dirname(os.path.abspath(arquivos[0]))
                        if arquivos else "."))
    return rep


def _o01(rep, versoes):
    """Texto divergente entre as versoes."""
    rep.check("O01")
    base = versoes[0]
    for outra in versoes[1:]:
        if outra["slides"] != base["slides"]:
            rep.fail("O01", "E", "versoes paralelas com o mesmo conteudo",
                     "%s x %s" % (base["nome"], outra["nome"]),
                     "contagem de slides diferente: %d e %d"
                     % (base["slides"], outra["slides"]))
            continue
        for i, (a, b) in enumerate(zip(base["texto"], outra["texto"]), 1):
            if a == b:
                continue
            rep.fail("O01", "E", "versoes paralelas com o mesmo conteudo",
                     "slide %d · %s x %s" % (i, base["nome"], outra["nome"]),
                     _diferenca(a, b))


def _diferenca(a, b):
    faltando = [x for x in a if x not in b]
    sobrando = [x for x in b if x not in a]
    partes = []
    if faltando:
        partes.append("so na 1a: %s" % " | ".join(t[:60] for t in faltando[:3]))
    if sobrando:
        partes.append("so na 2a: %s" % " | ".join(t[:60] for t in sobrando[:3]))
    if not partes:
        partes.append("mesmo texto, ordem de leitura diferente")
    return "; ".join(partes)


def _o02(rep, versoes):
    """Recurso presente numa versao e ausente noutra."""
    rep.check("O02")
    base = versoes[0]
    for outra in versoes[1:]:
        if outra["slides"] != base["slides"]:
            continue      # ja acusado em O01
        for i, (a, b) in enumerate(zip(base["recursos"], outra["recursos"]), 1):
            if a == b:
                continue
            for chave in set(a) | set(b):
                if a.get(chave, 0) != b.get(chave, 0):
                    rep.fail(
                        "O02", "E", "mesmo recurso em todas as versoes",
                        "slide %d · %s x %s" % (i, base["nome"], outra["nome"]),
                        "%s: %d em %s, %d em %s — conteudo diferente por "
                        "deficiencia e segregacao"
                        % (chave, a.get(chave, 0), base["nome"],
                           b.get(chave, 0), outra["nome"]))


def _o03(rep, pasta):
    """O pacote precisa dizer qual arquivo e qual, e para quem."""
    rep.check("O03")
    try:
        nomes = {n.lower() for n in os.listdir(pasta)}
    except OSError:
        nomes = set()
    if not (nomes & set(DECLARACOES)):
        rep.fail("O03", "A", "pacote com declaracao de versoes", pasta,
                 "nenhum LEIA-ME.md no pacote: quem recebe tres arquivos "
                 "precisa saber qual abrir e por que")


def render(rep: Pacote, pasta="") -> str:
    c = rep.counts()
    erros, avisos = c.get("E", 0), c.get("A", 0)
    nv = c.get("nao_verificado", 0)
    L = ["# Auditoria do pacote — camada O", ""]
    L.append("**Arquivos:** " + ", ".join("`%s`" % os.path.basename(a)
                                          for a in rep.arquivos))
    L.append("")
    L.append("| Severidade | Não conformes |")
    L.append("|---|---|")
    L.append("| Erro | **%d** |" % erros)
    L.append("| Aviso | **%d** |" % avisos)
    L.append("| Não verificado | %d |" % nv)
    L.append("")
    if erros == 0 and avisos == 0:
        L.append("As versões carregam **o mesmo conteúdo e os mesmos recursos**. "
                 "Diferem apenas na paleta, que é o propósito delas.")
        L.append("")
    for f in rep.findings:
        L.append("- **%s** · %s · %s — %s"
                 % (f["regra"], f["severidade"], f["onde"], f["detalhe"]))
    if rep.findings:
        L.append("")
    L.append("> Paridade verificada por comparação de texto, alt text, notas e "
             "recursos, slide a slide. O título do documento leva o nome do "
             "modo de propósito e não entra na comparação.")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(
        description="Camada O: paridade entre as versoes de um pacote")
    ap.add_argument("arquivos", nargs="+")
    ap.add_argument("--md")
    ap.add_argument("--pasta", help="onde procurar o LEIA-ME (regra O03)")
    args = ap.parse_args()

    rep = auditar(args.arquivos, args.pasta)
    texto = render(rep, args.pasta or "")
    if args.md:
        with open(args.md, "w", encoding="utf-8") as f:
            f.write(texto)
        print("relatorio em %s" % args.md)
    else:
        print(texto)

    c = rep.counts()
    return 1 if (c.get("E", 0) or c.get("A", 0)) else 0


if __name__ == "__main__":
    sys.exit(main())
