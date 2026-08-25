"""
montar_tudo — roda o pipeline inteiro, com portao em cada estagio.

    python scripts/montar_tudo.py exemplos/apresentacao -o entrega

Espera na pasta de entrada:
    roteiro.yaml     obrigatorio
    diagramas.yaml   opcional

Produz na pasta de saida:
    figuras/                 diagramas, uma versao por paleta
    <nome>.pptx              o deck, com hub e tres modos de cor
    auditoria-pptx.md        camadas A a I
    leitura-simulada.md      o que o leitor de tela anunciaria
    transcricao.docx         transcricao linear (regra K04)
    <nome>.pdf               PDF marcado, com identificador PDF/UA
    auditoria-pdf.md         camada L, incluindo veraPDF

O portao do estagio 5 PARA o pipeline se sobrar Erro ou Aviso. Isso e
proposital: exportar um PDF a partir de um .pptx reprovado so propaga o
defeito para o formato em que o material de fato circula.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def titulo(n, texto):
    print("\n" + "=" * 74)
    print(" %d. %s" % (n, texto))
    print("=" * 74)


def montar(entrada: str, saida: str, com_modos=True, com_pdf=True,
           parar_no_portao=True) -> int:
    import build_deck
    import gen_transcricao
    import simular_leitura
    from audit_pptx import audit as auditar_pptx
    from audit_pptx import render_markdown

    entrada, saida = os.path.abspath(entrada), os.path.abspath(saida)
    os.makedirs(saida, exist_ok=True)
    roteiro_arq = os.path.join(entrada, "roteiro.yaml")
    if not os.path.exists(roteiro_arq):
        print("roteiro.yaml nao encontrado em %s" % entrada)
        return 2

    # ---- 1. diagramas ---------------------------------------------------
    spec = os.path.join(entrada, "diagramas.yaml")
    if os.path.exists(spec):
        titulo(1, "Diagramas (uma versao por paleta)")
        import gen_diagramas
        mapa, _ = gen_diagramas.gerar(spec, os.path.join(saida, "figuras"))
        for nome, arqs in mapa.items():
            print("   %-24s %d paletas" % (nome, len(arqs)))
    else:
        titulo(1, "Diagramas — nenhum diagramas.yaml, pulando")

    # ---- 2. construcao ---------------------------------------------------
    titulo(2, "Construcao do .pptx")
    roteiro = build_deck.carregar_roteiro(roteiro_arq)
    nome_base = "".join(c for c in roteiro["apresentacao"]["titulo"][:48]
                        if c.isalnum() or c in " -_").strip().replace(" ", "-")
    pptx = os.path.join(saida, nome_base + ".pptx")

    anterior = os.getcwd()
    try:
        os.chdir(saida)   # os caminhos de figura no roteiro sao relativos
        build_deck.construir(roteiro, pptx, com_modos=com_modos)
    except build_deck.ErroDeRoteiro as e:
        print("\nERRO DE ROTEIRO: %s" % e)
        print("\nO build parou de proposito. Corrija o ROTEIRO, nao o .pptx.")
        return 2
    finally:
        os.chdir(anterior)

    from pptx import Presentation
    print("   %s" % os.path.basename(pptx))
    print("   %d slides" % len(Presentation(pptx).slides._sldIdLst))

    # ---- 3. auditoria do .pptx ------------------------------------------
    titulo(3, "Auditoria do .pptx (camadas A a I)")
    rep = auditar_pptx(pptx)
    md = os.path.join(saida, "auditoria-pptx.md")
    with open(md, "w", encoding="utf-8") as f:
        f.write(render_markdown(rep, pptx))
    c = rep.counts()
    print("   %d Erros · %d Avisos · %d Dicas · %d nao verificados"
          % (c.get("E", 0), c.get("A", 0), c.get("D", 0),
             c.get("nao_verificado", 0)))
    print("   %s" % os.path.basename(md))

    if (c.get("E", 0) or c.get("A", 0)):
        from audit_pptx import NAO_CONFORME
        print("\n   PORTAO FECHADO — nao conformidades em aberto:")
        for f_ in [x for x in rep.findings if x["veredito"] == NAO_CONFORME][:15]:
            print("      %s %s | %s | %s"
                  % (f_["severidade"], f_["regra"], f_["onde"], f_["detalhe"][:70]))
        if parar_no_portao:
            print("\n   Exportar PDF a partir daqui so propaga o defeito.")
            print("   Corrija o roteiro e rode de novo.")
            return 1

    # ---- 4. leitura simulada --------------------------------------------
    titulo(4, "Leitura simulada")
    prs = Presentation(pptx)
    slides = list(prs.slides)
    blocos = [simular_leitura.simular_slide(s, i, len(slides))
              for i, s in enumerate(slides, 1)]
    leitura = os.path.join(saida, "leitura-simulada.md")
    with open(leitura, "w", encoding="utf-8") as f:
        f.write("# Leitura simulada — %s\n\n" % os.path.basename(pptx))
        f.write("O que um leitor de tela anunciaria, na ordem em que anunciaria.\n"
                "Modelo do comportamento, nao o comportamento: nao substitui a "
                "regra K03.\n\n")
        for b in blocos:
            f.write("```\n" + "\n".join(b) + "\n```\n\n")
    print("   %s" % os.path.basename(leitura))

    # ---- 5. transcricao --------------------------------------------------
    titulo(5, "Transcricao linear (.docx)")
    docx = os.path.join(saida, "transcricao.docx")
    try:
        cont = gen_transcricao.gerar(pptx, docx)
        print("   %d slides · %d figuras · %d tabelas · %d descricoes longas"
              % (cont["slides"], cont["figuras"], cont["tabelas"],
                 cont["descricoes_longas"]))
        print("   %s" % os.path.basename(docx))
    except ImportError:
        print("   python-docx ausente — transcricao NAO gerada (regra K04)")

    # ---- 6 e 7. PDF ------------------------------------------------------
    if not com_pdf:
        print("\n   PDF pulado por opcao (--sem-pdf)")
        return 0

    titulo(6, "Exportacao para PDF marcado")
    try:
        import export_pdfua
        pdf = os.path.splitext(pptx)[0] + ".pdf"
        export_pdfua.exportar(pptx, pdf)
        cp = Presentation(pptx).core_properties
        r = export_pdfua.corrigir_metadados(
            pdf, titulo=(cp.title or "").strip() or None,
            idioma=(cp.language or "pt-BR").strip(),
            autor=(cp.author or "").strip() or None)
        print("   /Lang  %r -> %r" % (r["antes"]["Lang"], r["depois"]["Lang"]))
        if r["estrutura_preservada"]:
            export_pdfua.marcar_pdfua(pdf, (cp.title or "").strip(),
                                      (cp.author or "").strip(),
                                      (cp.language or "pt-BR").strip())
            print("   identificador PDF/UA-1 gravado")
        print("   %s" % os.path.basename(pdf))
    except Exception as e:
        print("   exportacao indisponivel: %s" % e)
        print("   (exige Windows com PowerPoint instalado)")
        return 0

    titulo(7, "Validacao do PDF (camada L)")
    import audit_pdf
    rep_pdf = audit_pdf.auditar(pdf)
    md_pdf = os.path.join(saida, "auditoria-pdf.md")
    with open(md_pdf, "w", encoding="utf-8") as f:
        f.write(audit_pdf.render(rep_pdf, pdf))
    cp2 = rep_pdf.counts()
    print("   %d Erros · %d Avisos · %d nao verificados"
          % (cp2.get("E", 0), cp2.get("A", 0), cp2.get("nao_verificado", 0)))
    print("   %s" % os.path.basename(md_pdf))

    print("\n" + "=" * 74)
    print(" Pacote em %s" % saida)
    print("=" * 74)
    print(" Falta a camada M, que nenhum script substitui:")
    print("   - Verificador nativo do PowerPoint (Revisao > Verificar Acessibilidade)")
    print("   - NVDA com Speech Logger, percorrendo o deck")
    print("   - Escala de cinza do Windows (Win+Ctrl+C)")
    print("   - Simulacao de protanopia, deuteranopia e tritanopia")
    print("   - Leitura de todo alt text, um a um")
    return 1 if (cp2.get("E", 0) or cp2.get("A", 0)) else 0


def main():
    ap = argparse.ArgumentParser(description="Roda o pipeline completo")
    ap.add_argument("entrada", help="pasta com roteiro.yaml e diagramas.yaml")
    ap.add_argument("-o", "--saida", default="entrega")
    ap.add_argument("--sem-modos", action="store_true")
    ap.add_argument("--sem-pdf", action="store_true")
    ap.add_argument("--seguir-mesmo-reprovado", action="store_true")
    args = ap.parse_args()
    return montar(args.entrada, args.saida,
                  com_modos=not args.sem_modos,
                  com_pdf=not args.sem_pdf,
                  parar_no_portao=not args.seguir_mesmo_reprovado)


if __name__ == "__main__":
    sys.exit(main())
