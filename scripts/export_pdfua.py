"""
export_pdfua — exporta o .pptx para PDF PRESERVANDO a semantica.

"Imprimir para PDF" rasteriza: tags, ordem de leitura, texto alternativo e
estrutura de tabela viram pixels. Este script usa o caminho correto, via COM,
com DocStructureTags=True — e depois conserta as duas coisas que o PowerPoint
entrega erradas, medidas em arquivo real:

    /Lang  sai como "pt", nao "pt-BR"
    /Title sai VAZIO quando o .pptx nao tem dc:title

    python scripts/export_pdfua.py deck.pptx -o deck.pdf

So Windows: depende do PowerPoint instalado.
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

PP_FIXED_FORMAT_PDF = 2
PP_FIXED_INTENT_PRINT = 2
PP_OUTPUT_SLIDES = 1


class ErroDeExportacao(Exception):
    pass


# --------------------------------------------------------------------------
def exportar(pptx: str, pdf: str, notas: bool = False) -> str:
    """Exporta via COM com marcas de estrutura. Devolve o caminho do PDF."""
    try:
        import win32com.client as win32
    except ImportError:
        raise ErroDeExportacao(
            "pywin32 ausente. Rode: pip install pywin32\n"
            "Em Linux/macOS nao ha como exportar PDF marcado por script: use\n"
            "Arquivo > Salvar uma Copia > PDF > Opcoes > 'Marcas de estrutura\n"
            "do documento para acessibilidade'.")

    pptx = os.path.abspath(pptx)
    pdf = os.path.abspath(pdf)
    if not os.path.exists(pptx):
        raise ErroDeExportacao("arquivo nao encontrado: %s" % pptx)
    if os.path.exists(pdf):
        os.remove(pdf)

    app = win32.Dispatch("PowerPoint.Application")
    pres = None
    try:
        pres = app.Presentations.Open(pptx, WithWindow=False)
        pres.ExportAsFixedFormat(
            pdf,
            PP_FIXED_FORMAT_PDF,
            PP_FIXED_INTENT_PRINT,
            0,                       # FrameSlides
            1,                       # HandoutOrder
            2 if notas else PP_OUTPUT_SLIDES,   # 2 = paginas de anotacoes
            0,                       # PrintHiddenSlides
            None, 1, "",
            True,                    # IncludeDocProperties
            True,                    # KeepIRMSettings
            True,                    # DocStructureTags  <- o que importa
            True,                    # BitmapMissingFonts
            False,                   # UseISO19005_1 (PDF/A-1)
        )
    finally:
        # Nao chamar app.Quit() entre exportacoes reaproveitando o mesmo
        # objeto Application: o objeto morre e a chamada seguinte falha com
        # AttributeError. Fechamos so a apresentacao.
        if pres is not None:
            try:
                pres.Close()
            except Exception:
                pass

    if not os.path.exists(pdf):
        raise ErroDeExportacao("o PowerPoint nao gerou o arquivo: %s" % pdf)
    return pdf


# --------------------------------------------------------------------------
def corrigir_metadados(pdf: str, titulo: str = None, idioma: str = "pt-BR",
                       autor: str = None) -> dict:
    """
    Conserta /Lang e /Title no PDF ja exportado.

    O PowerPoint escreve /Lang="pt" e deixa /Title vazio quando o .pptx nao
    tem dc:title. Com DisplayDocTitle ativo e titulo vazio, o leitor de tela
    passa a anunciar o NOME DO ARQUIVO (regra L03).
    """
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import NameObject, create_string_object

    reader = PdfReader(pdf)
    antes = {
        "Lang": str(reader.trailer["/Root"].get("/Lang") or ""),
        "Title": str((reader.metadata or {}).get("/Title") or ""),
    }

    writer = PdfWriter(clone_from=pdf)
    raiz = writer._root_object
    raiz[NameObject("/Lang")] = create_string_object(idioma)

    from pypdf.generic import BooleanObject, DictionaryObject
    prefs = raiz.get("/ViewerPreferences")
    # o PowerPoint escreve /ViewerPreferences como referencia indireta
    if hasattr(prefs, "get_object"):
        prefs = prefs.get_object()
    if not isinstance(prefs, DictionaryObject):
        prefs = DictionaryObject()
        raiz[NameObject("/ViewerPreferences")] = prefs
    prefs[NameObject("/DisplayDocTitle")] = BooleanObject(True)

    meta = {}
    if titulo:
        meta["/Title"] = titulo
    if autor:
        meta["/Author"] = autor
    if meta:
        writer.add_metadata(meta)

    tmp = pdf + ".tmp"
    with open(tmp, "wb") as f:
        writer.write(f)
    os.replace(tmp, pdf)

    depois = PdfReader(pdf)
    return {
        "antes": antes,
        "depois": {
            "Lang": str(depois.trailer["/Root"].get("/Lang") or ""),
            "Title": str((depois.metadata or {}).get("/Title") or ""),
        },
        "estrutura_preservada": "/StructTreeRoot" in depois.trailer["/Root"],
    }


# --------------------------------------------------------------------------
XMP_PDFUA = """<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about=""
      xmlns:pdfuaid="http://www.aiim.org/pdfua/ns/id/">
   <pdfuaid:part>1</pdfuaid:part>
  </rdf:Description>
  <rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/">
   <dc:title><rdf:Alt><rdf:li xml:lang="x-default">{titulo}</rdf:li></rdf:Alt></dc:title>
   <dc:creator><rdf:Seq><rdf:li>{autor}</rdf:li></rdf:Seq></dc:creator>
   <dc:language><rdf:Bag><rdf:li>{idioma}</rdf:li></rdf:Bag></dc:language>
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>"""


def _escapar_xml(t: str) -> str:
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def marcar_pdfua(pdf: str, titulo: str, autor: str, idioma: str = "pt-BR") -> bool:
    """
    Escreve o identificador PDF/UA-1 no XMP.

    Sem ele o veraPDF reprova com "The PDF/UA version and conformance level of
    a file shall be specified using the PDF/UA Identification extension
    schema" — e essa foi a UNICA falha do PDF que o PowerPoint gerou.

    ATENCAO: isto e uma DECLARACAO de conformidade. So marque um arquivo que
    ja passa no resto da validacao; marcar um PDF quebrado e pior que nao
    marcar, porque mente para a tecnologia assistiva.
    """
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import DecodedStreamObject, NameObject

    xmp = XMP_PDFUA.format(titulo=_escapar_xml(titulo or ""),
                           autor=_escapar_xml(autor or ""),
                           idioma=_escapar_xml(idioma))

    writer = PdfWriter(clone_from=pdf)
    fluxo = DecodedStreamObject()
    fluxo.set_data(xmp.encode("utf-8"))
    fluxo[NameObject("/Type")] = NameObject("/Metadata")
    fluxo[NameObject("/Subtype")] = NameObject("/XML")
    ref = writer._add_object(fluxo)
    writer._root_object[NameObject("/Metadata")] = ref

    tmp = pdf + ".tmp"
    with open(tmp, "wb") as f:
        writer.write(f)
    os.replace(tmp, pdf)

    r = PdfReader(pdf)
    return "/StructTreeRoot" in r.trailer["/Root"]


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(
        description="Exporta .pptx para PDF com marcas de estrutura")
    ap.add_argument("pptx")
    ap.add_argument("-o", "--saida")
    ap.add_argument("--notas", action="store_true",
                    help="exporta as Paginas de Anotacoes num PDF a parte "
                         "(as notas somem da exportacao padrao)")
    ap.add_argument("--sem-correcao", action="store_true")
    ap.add_argument("--sem-pdfua", action="store_true",
                    help="nao declarar conformidade PDF/UA-1 no XMP")
    args = ap.parse_args()

    saida = args.saida or os.path.splitext(args.pptx)[0] + ".pdf"

    try:
        exportar(args.pptx, saida)
    except ErroDeExportacao as e:
        print("ERRO: %s" % e)
        return 2
    print("exportado: %s" % saida)

    if not args.sem_correcao:
        from pptx import Presentation
        cp = Presentation(args.pptx).core_properties
        r = corrigir_metadados(saida, titulo=(cp.title or "").strip() or None,
                               idioma=(cp.language or "pt-BR").strip(),
                               autor=(cp.author or "").strip() or None)
        print("  /Lang  %r -> %r" % (r["antes"]["Lang"], r["depois"]["Lang"]))
        print("  /Title %r -> %r" % (r["antes"]["Title"], r["depois"]["Title"]))
        if not r["estrutura_preservada"]:
            print("  ATENCAO: a arvore de tags NAO sobreviveu — nao distribua "
                  "este PDF (regra L01/L04)")
        elif not args.sem_pdfua:
            ok = marcar_pdfua(saida, (cp.title or "").strip(),
                              (cp.author or "").strip(),
                              (cp.language or "pt-BR").strip())
            print("  identificador PDF/UA-1 gravado no XMP%s"
                  % ("" if ok else " (mas a arvore se perdeu — verifique!)"))

    if args.notas:
        pdf_notas = os.path.splitext(saida)[0] + "-anotacoes.pdf"
        try:
            exportar(args.pptx, pdf_notas, notas=True)
            print("anotacoes: %s" % pdf_notas)
        except ErroDeExportacao as e:
            print("  nao foi possivel exportar as anotacoes: %s" % e)

    print("\nValide agora:")
    print("  python scripts/audit_pdf.py %s" % saida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
