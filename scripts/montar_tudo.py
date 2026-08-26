"""
montar_tudo — roda o pipeline inteiro, com portao em cada estagio.

    python scripts/montar_tudo.py exemplos/apresentacao -o entrega

Espera na pasta de entrada:
    roteiro.yaml     obrigatorio
    diagramas.yaml   opcional

Produz na pasta de saida:
    figuras/                      diagramas, uma versao por paleta
    <nome>-padrao.pptx            um deck POR MODO DE COR, com o mesmo conteudo
    <nome>-alto-contraste.pptx
    <nome>-daltonico-seguro.pptx
    auditoria-pptx-<modo>.md      camadas A a N, do arquivo como entregue
    auditoria-pacote.md           camada O: paridade entre as tres versoes
    leitura-simulada.md           o que o leitor de tela anunciaria
    transcricao.docx              transcricao linear (regra K04)
    <nome>-padrao.pdf             PDF marcado, com identificador PDF/UA
    auditoria-pdf.md              camada L, incluindo veraPDF

UM ARQUIVO POR MODO e o padrao desde 26/08/2026. Antes eram tres secoes num
arquivo so, com um slide-hub: 85 slides, dos quais 57 eram o mesmo conteudo em
outra paleta. Quem enxerga escolhia a paleta no hub e ignorava o resto; quem
navega em sequencia atravessava tudo tres vezes — e a transcricao linear, que e
o artefato que mais importa para quem le assim, saia triplicada. `--arquivo-unico`
volta ao desenho antigo para quem precisa entregar um anexo so.

O portao do estagio 3 PARA o pipeline se sobrar Erro ou Aviso em QUALQUER deck.
Isso e proposital: exportar um PDF a partir de um .pptx reprovado so propaga o
defeito para o formato em que o material de fato circula.
"""
from __future__ import annotations

import argparse
import os
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


def _auditar_deck(pptx, saida, rotulo):
    """Audita um deck e grava o relatorio. Devolve (contagem, caminho_md)."""
    from audit_pptx import audit as auditar_pptx
    from audit_pptx import render_markdown

    rep = auditar_pptx(pptx)
    md = os.path.join(saida, "auditoria-pptx-%s.md" % rotulo)
    with open(md, "w", encoding="utf-8") as f:
        f.write(render_markdown(rep, pptx))
    return rep, md


def _mostrar(rep, md):
    from audit_pptx import NAO_CONFORME

    c = rep.counts()
    print("   %d Erros · %d Avisos · %d Dicas · %d nao verificados"
          % (c.get("E", 0), c.get("A", 0), c.get("D", 0),
             c.get("nao_verificado", 0)))
    print("   %s" % os.path.basename(md))
    if c.get("E", 0) or c.get("A", 0):
        for f_ in [x for x in rep.findings if x["veredito"] == NAO_CONFORME][:8]:
            print("      %s %s | %s | %s"
                  % (f_["severidade"], f_["regra"], f_["onde"],
                     f_["detalhe"][:70]))
    return c


def montar(entrada: str, saida: str, com_modos=True, com_pdf=True,
           parar_no_portao=True, com_diagramas=True, arquivo_unico=False,
           pasta_audio=None, pdf_todos_os_modos=False,
           video_libras=None, perfis=("completo",),
           libras_por_slide=False, perfis_todos_os_modos=False) -> int:
    import build_deck
    import gen_transcricao
    import simular_leitura

    entrada, saida = os.path.abspath(entrada), os.path.abspath(saida)
    os.makedirs(saida, exist_ok=True)
    roteiro_arq = os.path.join(entrada, "roteiro.yaml")
    if not os.path.exists(roteiro_arq):
        print("roteiro.yaml nao encontrado em %s" % entrada)
        return 2

    # ---- 1. diagramas ---------------------------------------------------
    spec = os.path.join(entrada, "diagramas.yaml")
    # Regerar as figuras custa chamada de API a cada rodada. Quando so o texto
    # do roteiro mudou, --sem-diagramas reaproveita o que ja esta na pasta.
    if com_diagramas and os.path.exists(spec):
        titulo(1, "Diagramas (uma versao por paleta)")
        import gen_diagramas
        mapa, _ = gen_diagramas.gerar(spec, os.path.join(saida, "figuras"))
        for nome, arqs in mapa.items():
            print("   %-24s %d paletas" % (nome, len(arqs)))
    elif os.path.exists(spec):
        titulo(1, "Diagramas — reaproveitando as figuras já geradas")
    else:
        titulo(1, "Diagramas — nenhum diagramas.yaml, pulando")

    # ---- 2. construcao ---------------------------------------------------
    titulo(2, "Construcao dos .pptx" if not arquivo_unico
           else "Construcao do .pptx (arquivo unico, desenho legado)")
    roteiro = build_deck.carregar_roteiro(roteiro_arq)
    nome_base = "".join(c for c in roteiro["apresentacao"]["titulo"][:48]
                        if c.isalnum() or c in " -_").strip().replace(" ", "-")

    modos = build_deck.MODOS if com_modos else ("padrao",)
    anterior = os.getcwd()
    try:
        os.chdir(saida)   # os caminhos de figura no roteiro sao relativos
        feitos = build_deck.construir_conjunto(
            roteiro, saida, nome_base, modos=modos, perfis=perfis,
            arquivo_unico=arquivo_unico, todos_os_modos=perfis_todos_os_modos)
    except build_deck.ErroDeRoteiro as e:
        print("\nERRO DE ROTEIRO: %s" % e)
        print("\nO build parou de proposito. Corrija o ROTEIRO, nao o .pptx.")
        return 2
    finally:
        os.chdir(anterior)

    from pptx import Presentation
    for chave, caminho in feitos.items():
        print("   %-22s %s (%d slides)"
              % (chave, os.path.basename(caminho),
                 len(Presentation(caminho).slides._sldIdLst)))

    principal = (feitos.get("completo/padrao") or feitos.get("padrao")
                 or list(feitos.values())[0])

    # ---- 3. auditoria de cada deck ---------------------------------------
    titulo(3, "Auditoria dos .pptx (camadas A a N)")
    reprovado = False
    for chave, caminho in feitos.items():
        print("   -- %s" % os.path.basename(caminho))
        rep, md = _auditar_deck(caminho, saida, chave.replace("/", "-"))
        c = _mostrar(rep, md)
        reprovado = reprovado or bool(c.get("E", 0) or c.get("A", 0))

    if reprovado and parar_no_portao:
        print("\n   PORTAO FECHADO — exportar PDF daqui so propaga o defeito.")
        print("   Corrija o roteiro e rode de novo.")
        return 1

    # ---- 4. leitura simulada (so no deck principal) ----------------------
    # As versoes carregam o mesmo conteudo — a camada O verifica isso. Simular
    # a leitura das tres so encheria o relatorio de repeticao, que e exatamente
    # o defeito que a separacao veio corrigir.
    titulo(4, "Leitura simulada (modo padrão)")
    prs = Presentation(principal)
    slides = list(prs.slides)
    blocos = [simular_leitura.simular_slide(s, i, len(slides))
              for i, s in enumerate(slides, 1)]
    leitura = os.path.join(saida, "leitura-simulada.md")
    with open(leitura, "w", encoding="utf-8") as f:
        f.write("# Leitura simulada — %s\n\n" % os.path.basename(principal))
        f.write("O que um leitor de tela anunciaria, na ordem em que anunciaria.\n"
                "Modelo do comportamento, nao o comportamento: nao substitui a "
                "regra K03.\n\n")
        for b in blocos:
            f.write("```\n" + "\n".join(b) + "\n```\n\n")
    print("   %d slides · %s" % (len(slides), os.path.basename(leitura)))

    # ---- 5. transcricao ---------------------------------------------------
    titulo(5, "Transcricao linear (.docx)")
    docx = os.path.join(saida, "transcricao.docx")
    try:
        cont = gen_transcricao.gerar(principal, docx)
        print("   %d slides · %d figuras · %d tabelas · %d descricoes longas"
              % (cont["slides"], cont["figuras"], cont["tabelas"],
                 cont["descricoes_longas"]))
        print("   %s" % os.path.basename(docx))
    except ImportError:
        print("   python-docx ausente — transcricao NAO gerada (regra K04)")

    codigo = 0

    # ---- 6 e 7. PDF ------------------------------------------------------
    if not com_pdf:
        print("\n   PDF pulado por opcao (--sem-pdf)")
    else:
        alvos = list(feitos.values()) if pdf_todos_os_modos else [principal]
        titulo(6, "Exportacao para PDF marcado")
        pdfs = []
        try:
            import export_pdfua
            for caminho in alvos:
                pdf = os.path.splitext(caminho)[0] + ".pdf"
                export_pdfua.exportar(caminho, pdf)
                cp = Presentation(caminho).core_properties
                r = export_pdfua.corrigir_metadados(
                    pdf, titulo=(cp.title or "").strip() or None,
                    idioma=(cp.language or "pt-BR").strip(),
                    autor=(cp.author or "").strip() or None)
                if r["estrutura_preservada"]:
                    export_pdfua.marcar_pdfua(pdf, (cp.title or "").strip(),
                                              (cp.author or "").strip(),
                                              (cp.language or "pt-BR").strip())
                    print("   %s · /Lang %r -> %r · identificador PDF/UA-1"
                          % (os.path.basename(pdf), r["antes"]["Lang"],
                             r["depois"]["Lang"]))
                pdfs.append(pdf)
        except Exception as e:
            print("   exportacao indisponivel: %s" % e)
            print("   (exige Windows com PowerPoint instalado)")
            # Falha de exportacao nao pode sair com o mesmo codigo de sucesso:
            # num pipeline em laco, o silencio se multiplica.
            codigo = 3

        if pdfs:
            titulo(7, "Validacao do PDF (camada L)")
            import audit_pdf
            for pdf in pdfs:
                rep_pdf = audit_pdf.auditar(pdf)
                sufixo = "" if len(pdfs) == 1 else "-" + os.path.splitext(
                    os.path.basename(pdf))[0].rsplit("-", 1)[-1]
                md_pdf = os.path.join(saida, "auditoria-pdf%s.md" % sufixo)
                with open(md_pdf, "w", encoding="utf-8") as f:
                    f.write(audit_pdf.render(rep_pdf, pdf))
                cp2 = rep_pdf.counts()
                print("   %s · %d Erros · %d Avisos · %d nao verificados"
                      % (os.path.basename(md_pdf), cp2.get("E", 0),
                         cp2.get("A", 0), cp2.get("nao_verificado", 0)))
                if cp2.get("E", 0) or cp2.get("A", 0):
                    codigo = codigo or 1

    # ---- 8 e 9. midia embutida + reauditoria ------------------------------
    if libras_por_slide:
        titulo(8, "Janela de Libras POR SLIDE (perfil libras)")
        try:
            import embutir_libras
            import gen_libras_slides
            pasta_v = os.path.join(saida, "libras", "slides")
            alvos = [c for k, c in feitos.items() if k.startswith("libras/")]
            if alvos:
                r = gen_libras_slides.gerar(alvos[0], pasta_v)
                print("   %d de %d slides com janela"
                      % (r["com_video"], r["slides"]))
                if r["abaixo_de_15fps"]:
                    print("   AVISO J07: %d vídeo(s) abaixo de 15 fps"
                          % r["abaixo_de_15fps"])
                for caminho in alvos:
                    e = embutir_libras.embutir_por_slide(caminho, pasta_v)
                    print("   %-22s %d slides · %.1f × %.1f cm · %.1f MB"
                          % (os.path.basename(caminho), e["slides_com_janela"],
                             e["caixa_cm"][0], e["caixa_cm"][1],
                             e["bytes"] / 1048576))
        except Exception as e:
            print("   Libras por slide não embutida: %s" % e)
            codigo = codigo or 3

    if video_libras:
        titulo(8, "Janela de Libras embutida na capa")
        try:
            import embutir_libras
            for chave, caminho in feitos.items():
                if chave.startswith("libras/") and libras_por_slide:
                    continue          # esses recebem uma janela POR SLIDE
                r = embutir_libras.embutir(caminho, video_libras)
                print("   %-22s slide %d · %.1f × %.1f cm"
                      % (chave, r["slide"], r["caixa_cm"][0], r["caixa_cm"][1]))
        except Exception as e:
            print("   Libras nao embutida: %s" % e)
            codigo = codigo or 3

    if pasta_audio:
        titulo(9, "Audiodescricao embutida (em TODOS os modos)")
        # Nos tres, sem excecao: um deck sem audio seria conteudo diferente
        # por deficiencia, que e o que a regra O02 existe para impedir.
        try:
            import embutir_audio
            for chave, caminho in feitos.items():
                r = embutir_audio.embutir(caminho, pasta_audio)
                print("   %-22s %d slides · %.1f MB"
                      % (chave, r["slides_com_audio"], r["bytes"] / 1048576))
        except Exception as e:
            print("   audio nao embutido: %s" % e)
            print("   (exige Windows com PowerPoint instalado)")
            codigo = codigo or 3

    # Reauditar depois de embutir midia nao e zelo: o audio ja quebrou C01, C02
    # e N04 uma vez, porque o controle entrava no fim do spTree. O relatorio que
    # vale e o do arquivo COMO ENTREGUE, nao o de antes da midia.
    if video_libras or pasta_audio:
        titulo(10, "Reauditoria dos arquivos COMO ENTREGUES")
        for chave, caminho in feitos.items():
            print("   -- %s" % os.path.basename(caminho))
            rep, md = _auditar_deck(caminho, saida, chave.replace("/", "-"))
            c = _mostrar(rep, md)
            if c.get("E", 0) or c.get("A", 0):
                codigo = codigo or 1

    # ---- 10. paridade entre as versoes -----------------------------------
    if len(feitos) > 1:
        titulo(11, "Paridade entre as versoes (camada O)")
        import audit_pacote
        rep_p = audit_pacote.auditar(list(feitos.values()), saida)
        md_p = os.path.join(saida, "auditoria-pacote.md")
        with open(md_p, "w", encoding="utf-8") as f:
            f.write(audit_pacote.render(rep_p, saida))
        cp3 = rep_p.counts()
        print("   %d Erros · %d Avisos · %d nao verificados"
              % (cp3.get("E", 0), cp3.get("A", 0),
                 cp3.get("nao_verificado", 0)))
        print("   %s" % os.path.basename(md_p))
        for f_ in rep_p.findings[:6]:
            if f_["veredito"] == audit_pacote.NAO_CONFORME:
                print("      %s %s | %s" % (f_["severidade"], f_["regra"],
                                            f_["detalhe"][:70]))
        if cp3.get("E", 0) or cp3.get("A", 0):
            codigo = codigo or 1

    print("\n" + "=" * 74)
    print(" Pacote em %s" % saida)
    print("=" * 74)
    print(" Falta a camada M, que nenhum script substitui:")
    print("   - Verificador nativo do PowerPoint (Revisao > Verificar Acessibilidade)")
    print("   - NVDA com Speech Logger, percorrendo o deck")
    print("   - Escala de cinza do Windows (Win+Ctrl+C)")
    print("   - Simulacao de protanopia, deuteranopia e tritanopia")
    print("   - Leitura de todo alt text, um a um")
    return codigo


def main():
    ap = argparse.ArgumentParser(description="Roda o pipeline completo")
    ap.add_argument("entrada", help="pasta com roteiro.yaml e diagramas.yaml")
    ap.add_argument("-o", "--saida", default="entrega")
    ap.add_argument("--sem-modos", action="store_true",
                    help="gera so o modo padrao")
    ap.add_argument("--arquivo-unico", action="store_true",
                    help="desenho legado: hub e tres secoes num arquivo so")
    ap.add_argument("--sem-pdf", action="store_true")
    ap.add_argument("--pdf-todos-os-modos", action="store_true",
                    help="exporta um PDF por modo, nao so o padrao")
    ap.add_argument("--perfis", default="completo",
                    help="perfis de público, separados por vírgula: "
                         "completo,libras,leitura_facil")
    ap.add_argument("--perfis-todos-os-modos", action="store_true",
                    help="gera cada perfil nas 3 paletas (9 arquivos)")
    ap.add_argument("--libras-por-slide", action="store_true",
                    help="grava uma janela de Libras POR SLIDE no perfil libras")
    ap.add_argument("--com-libras", metavar="VIDEO",
                    help="embute a janela de Libras na capa de TODOS os modos")
    ap.add_argument("--com-audio", metavar="PASTA",
                    help="embute a audiodescricao dessa pasta em TODOS os modos")
    ap.add_argument("--sem-diagramas", action="store_true",
                    help="reaproveita as figuras da pasta de saída")
    ap.add_argument("--seguir-mesmo-reprovado", action="store_true")
    args = ap.parse_args()

    return montar(args.entrada, args.saida,
                  com_modos=not args.sem_modos,
                  com_pdf=not args.sem_pdf,
                  com_diagramas=not args.sem_diagramas,
                  arquivo_unico=args.arquivo_unico,
                  pasta_audio=args.com_audio,
                  video_libras=args.com_libras,
                  perfis=tuple(p.strip() for p in args.perfis.split(",") if p.strip()),
                  libras_por_slide=args.libras_por_slide,
                  perfis_todos_os_modos=args.perfis_todos_os_modos,
                  pdf_todos_os_modos=args.pdf_todos_os_modos,
                  parar_no_portao=not args.seguir_mesmo_reprovado)


if __name__ == "__main__":
    sys.exit(main())
