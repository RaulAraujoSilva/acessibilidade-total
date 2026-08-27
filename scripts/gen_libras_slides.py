"""
gen_libras_slides — uma janela de Libras POR SLIDE, em lote.

Ate 26/08/2026 havia UMA janela, na capa. Duas coisas estavam erradas nisso, e
as duas ja estavam escritas em references/06-libras.md antes de alguem reparar:

  - *"a janela nao pode aparecer e sumir entre slides do mesmo bloco"* (§3);
  - *"um avatar miniaturizado no canto reprova"* — a janela da capa tinha
    6,9 cm de largura contra os 8,47 cm minimos da NBR 15290 por analogia.

O texto de cada video vem do PROPRIO SLIDE ja construido (`gen_libras.texto_do_slide`),
nao de um resumo escrito a parte: um terceiro texto divergiria dos outros dois.

    python scripts/gen_libras_slides.py deck-libras.pptx -o libras/slides/

Cache por hash: regravar 28 videos custa minutos, e o texto de um slide muda
sem que os outros 27 mudem. O manifesto guarda o hash do texto de cada slide.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gen_libras
import libras_caminho_a as L

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

MANIFESTO = "manifesto.json"

# Um mp4 de 0 byte EXISTE. O cache que so pergunta os.path.exists reaproveita o
# fracasso da rodada anterior e nunca mais grava aquele slide — foi o que
# aconteceu com os seis ultimos videos de um lote interrompido. O piso abaixo e
# generoso: um video de 12 s a 25 fps nao sai de 100 KB por acidente.
MINIMO_BYTES = 50 * 1024


def _hash(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]


def gerar(pptx: str, pasta: str, forcar: bool = False) -> dict:
    from pptx import Presentation

    os.makedirs(pasta, exist_ok=True)
    caminho_man = os.path.join(pasta, MANIFESTO)
    antigo = {}
    if os.path.exists(caminho_man) and not forcar:
        try:
            with open(caminho_man, encoding="utf-8") as f:
                antigo = json.load(f)
        except Exception:
            antigo = {}

    prs = Presentation(pptx)
    pendentes, manifesto = [], {}
    for i, slide in enumerate(prs.slides, 1):
        texto = gen_libras.texto_do_slide(slide).strip()
        nome = "slide-%02d" % i
        if not texto:
            manifesto[nome] = {"slide": i, "texto": "", "arquivo": None,
                               "hash": ""}
            continue
        h = _hash(texto)
        arquivo = os.path.join(pasta, nome + ".mp4")
        reaproveita = (antigo.get(nome, {}).get("hash") == h
                       and os.path.exists(arquivo)
                       and os.path.getsize(arquivo) >= MINIMO_BYTES)
        manifesto[nome] = {"slide": i, "texto": texto, "hash": h,
                           "arquivo": arquivo, "reaproveitado": reaproveita}
        if not reaproveita:
            pendentes.append((nome, texto))

    if pendentes:
        print("gravando %d vídeo(s); %d reaproveitado(s) do manifesto"
              % (len(pendentes), len(manifesto) - len(pendentes)))
        feitos = L.gravar_lote(pendentes, pasta)
        for nome, info in feitos.items():
            manifesto[nome].update({"bytes": info["bytes"],
                                    "segundos": info["segundos"],
                                    "px": info["px"]})
    else:
        print("nada a gravar: todos os vídeos estão em dia")

    for nome, m in manifesto.items():
        if m.get("arquivo") and os.path.exists(m["arquivo"]):
            m["fps"] = round(L.fps_do_arquivo(m["arquivo"]), 1)

    with open(caminho_man, "w", encoding="utf-8") as f:
        json.dump(manifesto, f, ensure_ascii=False, indent=2)

    com_video = [m for m in manifesto.values() if m.get("arquivo")
                 and os.path.exists(m["arquivo"])]
    piores = [m for m in com_video if m.get("fps", 0) < 15]
    return {"slides": len(manifesto), "com_video": len(com_video),
            "abaixo_de_15fps": len(piores), "manifesto": caminho_man,
            "pasta": pasta}


def main():
    ap = argparse.ArgumentParser(
        description="Grava uma janela de Libras por slide")
    ap.add_argument("pptx")
    ap.add_argument("-o", "--saida", default="libras/slides")
    ap.add_argument("--forcar", action="store_true",
                    help="ignora o cache e regrava tudo")
    args = ap.parse_args()

    try:
        r = gerar(args.pptx, args.saida, args.forcar)
    except RuntimeError as e:
        print("ERRO: %s" % e)
        return 2

    print("%d de %d slides com janela · %s"
          % (r["com_video"], r["slides"], r["manifesto"]))
    if r["abaixo_de_15fps"]:
        print("\nAVISO (J07): %d vídeo(s) abaixo de 15 fps — a sinalização "
              "perde compreensão." % r["abaixo_de_15fps"])
    print("\nRevise antes de publicar: glosa automática erra concordância "
          "espacial e classificadores (regra J05).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
