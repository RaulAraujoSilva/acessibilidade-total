"""
audit_pdf — camada L do catalogo: o PDF exportado.

Tres niveis, do mais barato ao mais caro:

  1. pypdf        — milissegundos. Pega o erro grosseiro: PDF sem marcas,
                    sem idioma, sem titulo, sem arvore de tags.
  2. veraPDF      — conformidade estrita com a ISO 14289 (PDF/UA-1).
                    Roda por Docker, sem exigir Java na maquina.
  3. PAC          — passo humano. Responde outra pergunta: nao "cumpre a
                    norma?", e sim "e utilizavel por tecnologia assistiva?".

    python scripts/audit_pdf.py deck.pdf [--md relatorio.md] [--sem-verapdf]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audit_pptx import NAO_CONFORME, NAO_VERIFICADO, Report

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

TAGS_TITULO = {"/H", "/H1", "/H2", "/H3", "/H4", "/H5", "/H6"}


# ==========================================================================
# Nivel 1 — pypdf
# ==========================================================================
def _percorrer_tags(no, saida, profundidade=0, limite=40000):
    """Coleta (tipo, dicionario) de cada no da arvore de estrutura."""
    if len(saida) >= limite or profundidade > 60:
        return
    try:
        no = no.get_object() if hasattr(no, "get_object") else no
    except Exception:
        return
    if isinstance(no, list):
        for filho in no:
            _percorrer_tags(filho, saida, profundidade + 1, limite)
        return
    if not hasattr(no, "get"):
        return
    tipo = no.get("/S")
    if tipo is not None:
        saida.append((str(tipo), no))
    filhos = no.get("/K")
    if filhos is not None:
        _percorrer_tags(filhos, saida, profundidade + 1, limite)


def auditar_estrutura(pdf: str, rep: Report):
    from pypdf import PdfReader

    reader = PdfReader(pdf)
    raiz = reader.trailer["/Root"]
    base = os.path.basename(pdf)

    for r in ("L01", "L02", "L03", "L04", "L05"):
        rep.check(r)

    # --- L01: o PDF esta marcado? -----------------------------------------
    marcado = False
    mi = raiz.get("/MarkInfo")
    if mi is not None:
        mi = mi.get_object() if hasattr(mi, "get_object") else mi
        marcado = bool(mi.get("/Marked"))
    tem_arvore = "/StructTreeRoot" in raiz

    if not marcado or not tem_arvore:
        rep.fail("L01", "E", "ISO 14289", base,
                 "PDF sem marcas de estrutura (/Marked=%s, /StructTreeRoot=%s) — "
                 "provavel 'Imprimir para PDF', que destroi tags, ordem de leitura "
                 "e texto alternativo" % (marcado, tem_arvore))
        return reader  # sem arvore, o resto da camada L nao faz sentido

    # --- L02: idioma -------------------------------------------------------
    lang = str(raiz.get("/Lang") or "").strip()
    if not lang:
        rep.fail("L02", "E", "3.1.1", base, "/Lang ausente no catalogo")
    elif not lang.lower().startswith("pt"):
        rep.fail("L02", "E", "3.1.1", base,
                 "/Lang = %r — a sintese de voz vai ler portugues com fonetica "
                 "de outro idioma" % lang)

    # --- L03: titulo e DisplayDocTitle -------------------------------------
    titulo = str((reader.metadata or {}).get("/Title") or "").strip()
    vp = raiz.get("/ViewerPreferences")
    vp = vp.get_object() if hasattr(vp, "get_object") else vp
    mostra_titulo = bool(vp.get("/DisplayDocTitle")) if vp else False
    if not titulo:
        rep.fail("L03", "E", "2.4.2", base,
                 "/Title vazio — o leitor de tela anuncia o nome do arquivo. "
                 "Corrija na origem (regra A01) e reexporte")
    if not mostra_titulo:
        rep.fail("L03", "E", "2.4.2", base,
                 "/ViewerPreferences /DisplayDocTitle ausente ou falso: o leitor "
                 "usa o nome do arquivo mesmo havendo titulo")

    # --- L04 e L05: arvore de tags ----------------------------------------
    tags = []
    _percorrer_tags(raiz["/StructTreeRoot"].get_object().get("/K"), tags)
    tipos = [t for t, _ in tags]
    contagem = {}
    for t in tipos:
        contagem[t] = contagem.get(t, 0) + 1

    titulos = [t for t in tipos if t in TAGS_TITULO]
    if not titulos:
        rep.fail("L04", "E", "1.3.1", base,
                 "nenhuma tag de titulo (H1..H6) na arvore — a navegacao por "
                 "titulos nao existe no PDF, ainda que exista no .pptx")

    ths = [d for t, d in tags if t == "/TH"]
    sem_scope = [d for d in ths if not d.get("/A")]
    if ths and sem_scope:
        rep.fail("L05", "E", "1.3.1", base,
                 "%d de %d celulas de cabecalho (TH) sem atributo de escopo — "
                 "corrija no Acrobat Pro: Ferramenta de Edicao de Tabela > "
                 "Propriedades da Celula > Ambito" % (len(sem_scope), len(ths)))

    rep.tags = contagem
    return reader


# ==========================================================================
# Nivel 2 — veraPDF
# ==========================================================================
def _comando_verapdf():
    if shutil.which("verapdf"):
        return ["verapdf"], False
    if shutil.which("docker"):
        try:
            r = subprocess.run(["docker", "images", "-q", "verapdf/cli"],
                               capture_output=True, timeout=20, text=True)
            if (r.stdout or "").strip():
                return ["docker", "run", "--rm", "-v"], True
        except Exception:
            pass
    return None, False


def rodar_verapdf(pdf: str, rep: Report):
    rep.check("L07")
    cmd, via_docker = _comando_verapdf()
    if cmd is None:
        rep.unverified("L07", "E", "ISO 14289",
                       "veraPDF indisponivel. Instale com: docker pull verapdf/cli "
                       "(nao exige Java)", os.path.basename(pdf))
        return None

    pdf = os.path.abspath(pdf)
    pasta, arquivo = os.path.dirname(pdf), os.path.basename(pdf)
    if via_docker:
        argv = ["docker", "run", "--rm", "-v", "%s:/data" % pasta,
                "verapdf/cli", "--flavour", "ua1", "--format", "json",
                "/data/%s" % arquivo]
    else:
        argv = ["verapdf", "--flavour", "ua1", "--format", "json", pdf]

    try:
        r = subprocess.run(argv, capture_output=True, timeout=300, text=True,
                           encoding="utf-8", errors="replace")
    except Exception as e:
        rep.unverified("L07", "E", "ISO 14289",
                       "veraPDF nao executou: %s" % e, os.path.basename(pdf))
        return None

    saida = (r.stdout or "").strip()
    try:
        dados = json.loads(saida)
    except Exception:
        rep.unverified("L07", "E", "ISO 14289",
                       "veraPDF respondeu em formato inesperado (codigo %d)"
                       % r.returncode, os.path.basename(pdf))
        return None

    falhas = _extrair_falhas_verapdf(dados)
    if falhas is None:
        rep.unverified("L07", "E", "ISO 14289",
                       "nao foi possivel ler o veredito do veraPDF",
                       os.path.basename(pdf))
        return None
    if falhas:
        for regra, n, descricao in falhas[:15]:
            rep.fail("L07", "E", "ISO 14289 · %s" % regra,
                     os.path.basename(pdf),
                     "%d ocorrencia(s): %s" % (n, descricao[:150]))
        if len(falhas) > 15:
            rep.fail("L07", "E", "ISO 14289", os.path.basename(pdf),
                     "e mais %d regras de PDF/UA reprovadas" % (len(falhas) - 15))
    return falhas


def _extrair_falhas_verapdf(dados):
    """O JSON do veraPDF muda de forma entre versoes; procura o essencial."""
    try:
        pilha, vistos = [dados], 0
        falhas = []
        while pilha and vistos < 50000:
            no = pilha.pop()
            vistos += 1
            if isinstance(no, dict):
                if "ruleStatus" in no and no.get("ruleStatus") == "FAILED":
                    rid = no.get("specification", "") or ""
                    clause = no.get("clause") or (no.get("ruleId") or {}).get("clause", "")
                    test = (no.get("ruleId") or {}).get("testNumber", "")
                    n = no.get("failedChecks", 1)
                    desc = no.get("description", "") or ""
                    falhas.append(("%s %s-%s" % (rid, clause, test), n, desc))
                pilha.extend(no.values())
            elif isinstance(no, list):
                pilha.extend(no)
        return falhas
    except Exception:
        return None


# ==========================================================================
# Relatorio
# ==========================================================================
def render(rep: Report, pdf: str) -> str:
    c = rep.counts()
    L = ["# Auditoria do PDF — camada L\n",
         "**Arquivo:** `%s`\n" % os.path.basename(pdf)]
    tags = getattr(rep, "tags", None)
    if tags:
        principais = sorted(tags.items(), key=lambda kv: -kv[1])[:12]
        L.append("**Tags encontradas:** " +
                 ", ".join("`%s`×%d" % (t, n) for t, n in principais) + "\n")
    L.append("| Severidade | Não conformes |")
    L.append("|---|---|")
    L.append("| Erro | **%d** |" % c.get("E", 0))
    L.append("| Aviso | **%d** |" % c.get("A", 0))
    L.append("| Não verificado | %d |" % c.get("nao_verificado", 0))
    L.append("")

    naos = [f for f in rep.findings if f["veredito"] == NAO_CONFORME]
    if naos:
        L.append("## Não conformidades\n")
        L.append("| Regra | Sev | Critério | Detalhe |")
        L.append("|---|---|---|---|")
        for f in naos:
            L.append("| %s | %s | %s | %s |" % (
                f["regra"], f["severidade"], f["criterio"],
                f["detalhe"].replace("|", "\\|")))
        L.append("")

    nv = [f for f in rep.findings if f["veredito"] == NAO_VERIFICADO]
    if nv:
        L.append("## Não verificado\n")
        for f in nv:
            L.append("- **%s** — %s" % (f["regra"], f["detalhe"]))
        L.append("")

    L.append("## Passo humano que nenhum script substitui\n")
    L.append("- Abrir no **PAC** (`winget install axes4.PAC`) e conferir o Protocolo")
    L.append("  Matterhorn, a árvore de tags e a prévia de leitor de tela.")
    L.append("- veraPDF responde *\"cumpre a norma?\"*; o PAC responde *\"é utilizável")
    L.append("  de verdade?\"*. São perguntas diferentes: rode os dois.")
    return "\n".join(L)


def auditar(pdf: str, com_verapdf: bool = True) -> Report:
    rep = Report(pdf)
    auditar_estrutura(pdf, rep)
    if com_verapdf:
        rodar_verapdf(pdf, rep)
    else:
        rep.unverified("L07", "E", "ISO 14289",
                       "validacao veraPDF pulada por opcao (--sem-verapdf)",
                       os.path.basename(pdf))
    rep.unverified("L06", "A", "1.1.1",
                   "objetos decorativos como /Artifact — conferir no PAC",
                   os.path.basename(pdf))
    return rep


def main():
    ap = argparse.ArgumentParser(description="Valida um PDF contra a camada L")
    ap.add_argument("pdf")
    ap.add_argument("--md", dest="md_out")
    ap.add_argument("--sem-verapdf", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.pdf):
        print("arquivo nao encontrado: %s" % args.pdf)
        return 2

    rep = auditar(args.pdf, com_verapdf=not args.sem_verapdf)
    md = render(rep, args.pdf)
    if args.md_out:
        with open(args.md_out, "w", encoding="utf-8") as f:
            f.write(md)
        print("relatorio: %s" % args.md_out)
    print(md)

    c = rep.counts()
    return 1 if (c.get("E", 0) or c.get("A", 0)) else 0


if __name__ == "__main__":
    sys.exit(main())
