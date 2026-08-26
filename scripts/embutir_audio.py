"""
embutir_audio — poe a audiodescricao DENTRO do deck, slide a slide.

Entregar as faixas numa pasta ao lado ja cumpre a regra K02, mas quase ninguem
abre a pasta. Dentro do arquivo, o recurso existe onde a pessoa esta.

Tres cuidados que vem do proprio catalogo:
  I04  sem autoplay e sem loop — quem decide ouvir e o usuario
  D10  o objeto de midia recebe texto alternativo
  N02  o controle fica na area segura, nunca na faixa do rodape
  N03  o titulo encolhe uma coluna para o controle nao cobrir nada

Precisa do PowerPoint instalado (COM), porque o python-pptx nao insere audio.

    python scripts/embutir_audio.py deck.pptx audiodescricao/
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import grade as G

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# COM trabalha em pontos: 1 pt = 12700 EMU
PT = 12700
LADO = G.cm(1.5) // PT          # controle de audio, em pontos
MARGEM_PT = G.MARGEM // PT
LARG_PT = G.LARGURA // PT
TOPO_PT = G.TITULO_Y // PT


def embutir(pptx: str, pasta_audio: str, so_modo: str = None) -> dict:
    import win32com.client as win32

    pptx = os.path.abspath(pptx)
    pasta_audio = os.path.abspath(pasta_audio)
    faixas = sorted(f for f in os.listdir(pasta_audio) if f.endswith(".mp3"))
    if not faixas:
        raise RuntimeError("nenhum .mp3 em %s" % pasta_audio)

    app = win32.Dispatch("PowerPoint.Application")
    pres = app.Presentations.Open(pptx, WithWindow=False)
    postos = 0
    try:
        total = pres.Slides.Count
        # as faixas cobrem UM ciclo de conteudo; num deck com 3 modos o ciclo
        # se repete, entao o indice da faixa e ciclico a partir do hub
        n_faixas = len(faixas)
        for i in range(1, total + 1):
            slide = pres.Slides(i)
            # slide 1 e o hub: sem faixa propria
            if total > n_faixas and i == 1:
                continue
            pos = ((i - 2) % n_faixas) if total > n_faixas else (i - 1)
            if pos >= n_faixas:
                continue
            caminho = os.path.join(pasta_audio, faixas[pos])

            # O controle acompanha o TITULO, nao o topo do slide. Em capa,
            # secao e citacao o titulo fica no meio da tela; fixar o controle
            # no alto poria a leitura em conflito com o que se ve, e foi
            # exatamente o que a regra N04 acusou em 24 slides.
            topo = TOPO_PT
            try:
                if slide.Shapes.Title is not None:
                    topo = slide.Shapes.Title.Top
            except Exception:
                pass

            esq = LARG_PT - MARGEM_PT - LADO
            midia = slide.Shapes.AddMediaObject2(
                caminho, LinkToFile=0, SaveWithDocument=-1,
                Left=esq, Top=topo, Width=LADO, Height=LADO)
            midia.Name = "Audiodescrição do slide"
            midia.AlternativeText = (
                "Audiodescrição narrada deste slide. A transcrição está no "
                "arquivo transcricao-audiodescricao.md")
            try:
                fmt = midia.AnimationSettings.PlaySettings
                fmt.PlayOnEntry = 0        # sem autoplay (regra I04)
                fmt.LoopUntilStopped = 0
                fmt.HideWhileNotPlaying = 0
            except Exception:
                pass

            # o titulo encolhe uma coluna para nao ficar sob o controle
            try:
                titulo = slide.Shapes.Title
                if titulo is not None:
                    limite = esq - (G.MEDIANIZ // PT)
                    if titulo.Left + titulo.Width > limite:
                        titulo.Width = max(100, limite - titulo.Left)
            except Exception:
                pass
            postos += 1

        pres.Save()
    finally:
        try:
            pres.Close()
        except Exception:
            pass

    # A ordem de leitura e ajustada AQUI, no XML, e nao pelo ZOrder do COM:
    # contar passos de SendBackward e erro na certa, e na primeira tentativa o
    # controle foi parar ANTES do titulo, quebrando a regra C01 em todo slide.
    _reordenar(pptx)

    return {"faixas": len(faixas), "slides_com_audio": postos,
            "bytes": os.path.getsize(pptx)}


def _reordenar(pptx: str) -> int:
    """
    Poe o controle de audio logo DEPOIS do titulo no spTree.

    E o lugar semantico certo — "a audiodescricao DESTE slide" — e resolve o
    conflito entre a ordem de leitura e o que se ve, ja que o controle fica no
    alto do slide (regras C01 e N04).
    """
    from pptx import Presentation

    import a11y_lib as A

    prs = Presentation(pptx)
    movidos = 0
    for slide in prs.slides:
        spTree = slide.shapes._spTree
        titulo = midia = None
        for el in A.iter_shape_elements(spTree):
            if A.is_title_placeholder(el):
                titulo = el
            elif A.media_kind(el):
                midia = el
        if titulo is None or midia is None:
            continue
        filhos = list(spTree)
        if filhos.index(midia) == filhos.index(titulo) + 1:
            continue
        spTree.remove(midia)
        spTree.insert(list(spTree).index(titulo) + 1, midia)
        movidos += 1
    prs.save(pptx)
    return movidos


def main():
    ap = argparse.ArgumentParser(description="Embute a audiodescricao no deck")
    ap.add_argument("pptx")
    ap.add_argument("pasta_audio")
    args = ap.parse_args()

    try:
        r = embutir(args.pptx, args.pasta_audio)
    except Exception as e:
        print("ERRO: %s" % e)
        print("\nExige Windows com PowerPoint instalado. Sem ele, entregue as")
        print("faixas na pasta ao lado — a regra K02 aceita, e a transcrição")
        print("continua obrigatória.")
        return 2

    print("audiodescrição embutida em %d slides (%d faixas)"
          % (r["slides_com_audio"], r["faixas"]))
    print("arquivo agora com %.1f MB" % (r["bytes"] / 1048576))
    print("\nSem autoplay e sem loop: quem decide ouvir é o usuário (regra I04).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
