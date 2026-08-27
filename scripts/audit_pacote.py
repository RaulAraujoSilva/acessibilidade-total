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

PUBLICO = {
    "completo": "todos — é a versão que não falta nada a ninguém",
    "libras": "Libras como primeira língua",
    "leitura_facil": "deficiência cognitiva, TDAH, leitura fácil",
}


def _conta(n, singular, plural):
    if not n:
        return "—"
    return "%d %s" % (n, singular if n == 1 else plural)


class Pacote:
    def __init__(self, arquivos):
        self.arquivos = arquivos
        self.perfis = {}
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
        # a linha [chave] fica FORA da comparacao literal: ela e a ancora de
        # equivalencia entre perfis, e entre paletas ela seria so ruido
        notas = nl_sem_chave(notas)
    if notas:
        pedacos.append("[notas] " + notas)
    return pedacos


def nl_sem_chave(notas):
    return "\n".join(l for l in notas.splitlines()
                      if not l.strip().startswith("[chave]")).strip()


def mensagem_chave(slide):
    """A frase que resume o slide, gravada pelo construtor nas notas."""
    try:
        notas = slide.notes_slide.notes_text_frame.text
    except Exception:
        return ""
    for linha in notas.splitlines():
        if linha.strip().startswith("[chave]"):
            return linha.strip()[len("[chave]"):].strip()
    return ""


def _recursos_do_slide(slide):
    """Que recursos o slide carrega, sem olhar o conteudo deles."""
    r = defaultdict(int)
    for el in A.iter_shape_elements(slide.shapes._spTree):
        kind = A.media_kind(el)
        if kind:
            # audio e video contados a parte: "1 midia" nao distingue uma faixa
            # de audiodescricao de uma janela de Libras, e a diferenca e o
            # ponto inteiro da separacao por perfil
            r[kind if kind in ("audio", "video") else "midia"] += 1
        elif el.tag == A.q("p:pic"):
            r["figura"] += 1
        elif el.tag == A.q("p:graphicFrame") and el.find(".//" + A.q("a:tbl")) is not None:
            r["tabela"] += 1
    return dict(r)


def _perfil_do_nome(caminho):
    """O perfil sai do nome do arquivo: -libras, -leitura-facil, ou completo."""
    nome = os.path.basename(caminho).lower()
    if "-libras" in nome:
        return "libras"
    if "-leitura-facil" in nome:
        return "leitura_facil"
    return "completo"


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
        "chaves": [mensagem_chave(s) for s in slides],
        "perfil": _perfil_do_nome(caminho),
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
        for v in versoes:
            rep.perfis.setdefault(v["perfil"], {
                "arquivo": v["nome"],
                "audio": sum(r.get("audio", 0) for r in v["recursos"]),
                "video": sum(r.get("video", 0) for r in v["recursos"]),
            })

        # DENTRO de um perfil, as versoes so mudam de paleta: o texto tem de
        # ser identico (O01/O02). ENTRE perfis, o texto muda de proposito —
        # comparar literal reprovaria por construcao. O que se exige la e
        # equivalencia de mensagem (O04/O05).
        por_perfil = {}
        for v in versoes:
            por_perfil.setdefault(v["perfil"], []).append(v)

        for grupo in por_perfil.values():
            if len(grupo) > 1:
                _o01(rep, grupo)
                _o02(rep, grupo)
        if len(por_perfil) == 1:
            rep.check("O04")
            rep.check("O05")
        else:
            _o04_o05(rep, por_perfil)
        _o07(rep, versoes)

    _o03(rep, pasta or (os.path.dirname(os.path.abspath(arquivos[0]))
                        if arquivos else "."))
    _o06(rep, arquivos)
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


def _o04_o05(rep, por_perfil):
    """
    Equivalencia entre PERFIS de publico.

    Aqui o texto e diferente de proposito — uma versao com Libras como primeira
    lingua nao repete o portugues do original. O que nao pode mudar e a
    MENSAGEM. Sem uma ancora explicita, "equivalente" seria promessa; com a
    linha [chave] gravada nas notas, vira teste.

    O04 pega o que SUMIU numa versao. O05 pega o que APARECEU so numa —
    duas versoes que dizem coisas diferentes sao duas verdades, nao duas
    apresentacoes do mesmo material.
    """
    rep.check("O04")
    rep.check("O05")

    base_nome = "completo" if "completo" in por_perfil else sorted(por_perfil)[0]
    base = por_perfil[base_nome][0]
    chaves_base = [c for c in base["chaves"] if c]

    if not chaves_base:
        rep.unverified("O04", "E", "equivalencia entre perfis",
                       "nenhuma mensagem-chave gravada — sem ela a equivalência "
                       "entre versões de público não é verificável")
        return

    for nome, grupo in por_perfil.items():
        if nome == base_nome:
            continue
        outra = grupo[0]
        faltando = [c for c in chaves_base if c not in outra["chaves"]]
        sobrando = [c for c in outra["chaves"] if c and c not in base["chaves"]]

        for c in faltando[:6]:
            rep.fail("O04", "E", "toda mensagem em todas as versoes",
                     "%s x %s" % (base["nome"], outra["nome"]),
                     "mensagem ausente na versão %r: %r — reduzir texto não "
                     "pode virar omitir conteúdo" % (nome, c[:60]))
        for c in sobrando[:6]:
            rep.fail("O05", "E", "nenhuma versao acrescenta conteudo",
                     "%s x %s" % (base["nome"], outra["nome"]),
                     "mensagem que só existe na versão %r: %r — versões que "
                     "dizem coisas diferentes são duas verdades"
                     % (nome, c[:60]))


def _o07(rep, versoes):
    """
    A divergencia de recurso entre perfis tem de ser a DECLARADA.

    Sem esta regra, `build_deck.RECURSOS` seria uma intencao escrita em codigo
    que nenhum auditor le — e tirar um recurso por engano ficaria indistinguivel
    de tirar por desenho. E exatamente a diferenca entre "recurso segue o
    sentido que serve" e "essa versao esta faltando coisa".
    """
    rep.check("O07")
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from build_deck import recursos_do_perfil
    except Exception:
        rep.unverified("O07", "A", "divergencia de recurso declarada",
                       "nao foi possivel ler o mapa RECURSOS de build_deck")
        return

    for v in versoes:
        esperado = recursos_do_perfil(v["perfil"])
        tem_audio = sum(r.get("audio", 0) for r in v["recursos"]) > 0
        n_video = sum(r.get("video", 0) for r in v["recursos"])

        if tem_audio != esperado["audio"]:
            rep.fail("O07", "A", "divergencia de recurso declarada", v["nome"],
                     "audiodescrição %s, mas o perfil %r a declara como %s — "
                     "recurso a mais ou a menos que o desenho prevê"
                     % ("presente" if tem_audio else "ausente", v["perfil"],
                        "esperada" if esperado["audio"] else "dispensada"))

        if esperado["libras_por_slide"] and n_video < v["slides"]:
            rep.fail("O07", "A", "divergencia de recurso declarada", v["nome"],
                     "o perfil %r prevê uma janela de Libras por slide, e há "
                     "%d janela(s) para %d slides"
                     % (v["perfil"], n_video, v["slides"]))


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


def _o06(rep, arquivos):
    """
    Cada versao tem de dizer, no proprio arquivo, para quem ela e.

    O titulo do documento e o que o leitor de tela anuncia ao abrir. Uma versao
    de publico que nao se identifica ali obriga a pessoa a descobrir pelo nome
    do arquivo — ou a nao descobrir.
    """
    from pptx import Presentation

    rep.check("O06")
    for caminho in arquivos:
        perfil = _perfil_do_nome(caminho)
        if perfil == "completo":
            continue
        titulo = (Presentation(caminho).core_properties.title or "").lower()
        marca = {"libras": "libras", "leitura_facil": "leitura fácil"}[perfil]
        if marca not in titulo:
            rep.fail("O06", "A", "versao declara seu publico",
                     os.path.basename(caminho),
                     "o título do documento não diz que esta é a versão %r — "
                     "é o que o leitor de tela anuncia ao abrir" % perfil)


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
        L.append("Todas as versões carregam **a mesma informação**: nenhuma "
                 "mensagem-chave falta e nenhuma sobra.")
        L.append("")
    # O recurso NAO e o mesmo em toda versao, e afirmar que e seria falso. Esta
    # tabela e derivada do arquivo, nao escrita a mao: e o relatorio dizendo o
    # que ele mediu, em vez de repetir uma promessa.
    if rep.perfis:
        L.append("### O que cada versão carrega")
        L.append("")
        L.append("| Versão | Público | Audiodescrição | Janela de Libras |")
        L.append("|---|---|---|---|")
        for nome, dados in sorted(rep.perfis.items()):
            L.append("| `%s` | %s | %s | %s |"
                     % (dados["arquivo"], PUBLICO.get(nome, nome),
                        _conta(dados["audio"], "faixa", "faixas"),
                        _conta(dados["video"], "janela", "janelas")))
        L.append("")
        L.append("> Recurso segue **o sentido que ele serve**: a audiodescrição "
                 "atende quem não enxerga, a janela de Libras atende quem tem "
                 "Libras como primeira língua. Exigir todo recurso em toda "
                 "versão não seria paridade — seria peso morto.")
        L.append("")
    for f in rep.findings:
        L.append("- **%s** · %s · %s — %s"
                 % (f["regra"], f["severidade"], f["onde"], f["detalhe"]))
    if rep.findings:
        L.append("")
    L.append("> Entre **paletas** compara-se texto, alt text, notas e recursos, "
             "slide a slide (O01/O02). Entre **perfis de público** compara-se a "
             "mensagem-chave (O04/O05), porque ali o texto muda de propósito. "
             "O título do documento leva o nome da versão e fica fora da "
             "comparação.")
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
