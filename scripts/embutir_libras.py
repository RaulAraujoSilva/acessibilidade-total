"""
embutir_libras — poe a janela de Libras DENTRO do deck.

Mesma razao do `embutir_audio.py`: entregar o vídeo numa pasta ao lado cumpre a
regra J01, e quase ninguem abre a pasta. A pergunta "como acesso a Libras?" e a
prova de que o recurso existia e nao estava ao alcance.

O video vai na CAPA, na faixa livre a direita: e o primeiro slide que qualquer
pessoa ve, e a capa e o unico layout com meia largura sobrando — em qualquer
outro ele cobriria texto e reprovaria em N03.

Cuidados que vem do catalogo:
  I04  sem autoplay e sem loop — quem decide assistir e o usuario
  D10  o objeto de midia recebe texto alternativo
  J05  a glosa e automatica: o alt text DIZ isso, nao esconde
  N01  proporcao preservada; a janela nao pode ser esticada
  N02  dentro da area segura, fora da faixa do rodape
  O02  vai nos TRES modos, senao uma versao fica sem o recurso

Precisa do PowerPoint instalado (COM), porque o python-pptx nao insere video.

    python scripts/embutir_libras.py deck.pptx libras/janela-libras.mp4
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

PT = 12700                       # COM trabalha em pontos: 1 pt = 12700 EMU
NATIVO = (312, 452)              # o recorte que libras_caminho_a.py produz

ALT = ("Janela de Libras com o resumo deste material. A glosa é automática "
       "e não foi revisada por intérprete; o roteiro em SRT acompanha.")


def _caixa(nativo):
    """Faixa livre da capa, a direita, com a proporcao nativa preservada."""
    caixa_w = G.larg(4)
    caixa_h = G.cm(10.0)
    w, h, dx, dy = G.encaixar(nativo[0], nativo[1], caixa_w, caixa_h)
    x = G.x(8) + dx
    y = G.CONTEUDO_Y + dy
    return x, y, w, h


def _tamanho_nativo(video):
    """Le a resolucao real do arquivo; sem ffprobe, usa o recorte conhecido."""
    import shutil
    import subprocess

    if not shutil.which("ffprobe"):
        return NATIVO
    try:
        saida = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height", "-of", "csv=p=0",
             video], capture_output=True, text=True, timeout=30).stdout
        w, h = (int(v) for v in saida.strip().split(",")[:2])
        return (w, h) if w and h else NATIVO
    except Exception:
        return NATIVO


def embutir(pptx: str, video: str, slide_no: int = 1) -> dict:
    import win32com.client as win32

    pptx, video = os.path.abspath(pptx), os.path.abspath(video)
    if not os.path.exists(video):
        raise RuntimeError("video nao encontrado: %s" % video)

    x, y, w, h = _caixa(_tamanho_nativo(video))

    app = win32.Dispatch("PowerPoint.Application")
    pres = app.Presentations.Open(pptx, WithWindow=False)
    try:
        slide = pres.Slides(slide_no)
        # se ja houver uma janela embutida, troca em vez de empilhar
        for forma in list(slide.Shapes):
            if forma.Name == "Janela de Libras":
                forma.Delete()
        midia = slide.Shapes.AddMediaObject2(
            video, LinkToFile=0, SaveWithDocument=-1,
            Left=x // PT, Top=y // PT, Width=w // PT, Height=h // PT)
        midia.Name = "Janela de Libras"
        midia.AlternativeText = ALT
        try:
            fmt = midia.AnimationSettings.PlaySettings
            fmt.PlayOnEntry = 0          # sem autoplay (regra I04)
            fmt.LoopUntilStopped = 0
            fmt.HideWhileNotPlaying = 0
        except Exception:
            pass
        pres.Save()
    finally:
        try:
            pres.Close()
        except Exception:
            pass

    return {"slide": slide_no, "bytes": os.path.getsize(pptx),
            "caixa_cm": (round(w / G.cm(1), 1), round(h / G.cm(1), 1))}


def main():
    ap = argparse.ArgumentParser(description="Embute a janela de Libras no deck")
    ap.add_argument("pptx")
    ap.add_argument("video")
    ap.add_argument("--slide", type=int, default=1)
    args = ap.parse_args()

    try:
        r = embutir(args.pptx, args.video, args.slide)
    except Exception as e:
        print("ERRO: %s" % e)
        print("\nExige Windows com PowerPoint instalado. Sem ele, entregue o")
        print("vídeo na pasta ao lado e diga no LEIA-ME onde ele está.")
        return 2

    print("janela de Libras no slide %d · %.1f × %.1f cm · arquivo com %.1f MB"
          % (r["slide"], r["caixa_cm"][0], r["caixa_cm"][1],
             r["bytes"] / 1048576))
    print("\nSem reprodução automática. A glosa é automática e o alt text diz "
          "isso (regra J05).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
