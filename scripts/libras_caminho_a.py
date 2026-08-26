"""
libras_caminho_a — grava a janela de Libras capturando o VLibras Widget.

COMO SE CHEGOU AQUI. A primeira tentativa falhou por um motivo bobo: a pagina
era montada com `set_content`, e assim o botao de acesso do widget nunca ficava
clicavel. Servindo a MESMA pagina por HTTP de verdade, o widget abre, o avatar
3D renderiza e a traducao roda. Dois detalhes custaram tempo e ficam anotados:

  1. O elemento `[vw-access-button]` tem ALTURA ZERO — e um marcador. O botao
     visivel e criado pelo plugin na borda direita da janela.
  2. O player desenha num canvas dentro de SHADOW DOM.
     `document.querySelector('canvas')` devolve nada mesmo com o avatar na
     tela. Nao use isso para saber se carregou; use a captura.
  3. Selecao feita por `window.getSelection()` NAO dispara a traducao: o
     plugin escuta eventos reais de mouse. E preciso arrastar o mouse.

    python scripts/libras_caminho_a.py --texto "..." -o libras/resumo.mp4
    python scripts/libras_caminho_a.py --arquivo resumo.txt -o libras/resumo.mp4

Exige: playwright + chromium (`playwright install chromium`) e ffmpeg no PATH.
Roda em modo COM JANELA: o WebGL do avatar nao renderiza em headless puro.
"""
from __future__ import annotations

import argparse
import base64
import http.server
import os
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading
import time

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

PAGINA = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>Roteiro em Libras</title>
<style>
  body {{ margin:0; padding:48px 56px; background:#FFFFFF; color:#111111;
         font:24px/1.6 'Segoe UI',Calibri,Arial,sans-serif; }}
  #alvo {{ max-width:820px; }}
</style></head><body>
<div id="alvo">{texto}</div>
<div vw class="enabled">
  <div vw-access-button class="active"></div>
  <div vw-plugin-wrapper><div class="vw-plugin-top-wrapper"></div></div>
</div>
<script src="https://vlibras.gov.br/app/vlibras-plugin.js"></script>
<script>
  window.addEventListener('load', function () {{
    new window.VLibras.Widget('https://vlibras.gov.br/app');
  }});
</script>
</body></html>
"""


def _servir(pasta, porta=0):
    """Porta 0: o sistema escolhe uma livre. Porta fixa colide com uma
    execucao anterior que nao encerrou o servidor."""
    class Silencioso(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=pasta, **kw)

        def log_message(self, *a):
            pass

    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", porta), Silencioso)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def gravar(texto: str, saida: str, segundos: int = 150, largura: int = 1280,
           altura: int = 800, fps: int = 12) -> dict:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError("playwright ausente: pip install playwright && "
                           "playwright install chromium")
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg ausente no PATH")

    tmp = tempfile.mkdtemp(prefix="libras_")
    quadros = os.path.join(tmp, "frames")
    os.makedirs(quadros)
    with open(os.path.join(tmp, "index.html"), "w", encoding="utf-8") as f:
        f.write(PAGINA.format(texto=texto))

    srv, porta = _servir(tmp)
    capturados = 0

    try:
        with sync_playwright() as pw:
            nav = pw.chromium.launch(headless=False, args=[
                "--use-gl=angle", "--use-angle=gl",
                "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
            pg = nav.new_page(viewport={"width": largura, "height": altura})
            pg.goto("http://127.0.0.1:%d/index.html" % porta, wait_until="load")
            time.sleep(8)

            # o botao visivel fica na borda direita; o [vw-access-button] tem
            # altura zero e nao serve de alvo
            pg.mouse.click(largura - 30, altura // 2)
            time.sleep(16)          # o player Unity demora a subir

            # NAO clicar no botao de expandir: ele muda a geometria do player
            # e invalida o recorte, cortando o avatar ao meio.
            #
            # O player inteiro vive em SHADOW DOM: nenhum elemento posicionado
            # aparece no documento principal, entao nao da para medir o
            # retangulo pelo DOM. A ancora e geometrica: o painel ocupa uma
            # faixa fixa junto a borda direita, logo abaixo do topo.
            caixa = [largura - 316, 176, 312, 452]
            caixa[0] = max(0, caixa[0])
            caixa[3] = min(caixa[3], altura - caixa[1])

            # selecao por ARRASTE de mouse: e o que dispara a traducao
            alvo = pg.evaluate(
                "() => { const r = document.getElementById('alvo')"
                ".getBoundingClientRect(); return [Math.round(r.x),"
                " Math.round(r.y), Math.round(r.width), Math.round(r.height)]; }")
            pg.mouse.move(alvo[0] + 4, alvo[1] + 10)
            pg.mouse.down()
            pg.mouse.move(alvo[0] + alvo[2] - 8, alvo[1] + alvo[3] - 6, steps=30)
            pg.mouse.up()
            time.sleep(2)

            # Captura quadro a quadro por screenshot recortado.
            #
            # Tentei o screencast do CDP, que seria mais rapido: ele entrega 1
            # a 3 quadros e para, tanto com ack dentro do handler quanto
            # bombeando os eventos com wait_for_timeout. Nao insisti — o laco
            # de screenshot funciona e a limitacao esta declarada abaixo.
            #
            # LIMITE CONHECIDO: cada screenshot custa ~0,35 s, o que da cerca
            # de 3 quadros por segundo. O video sai no tempo REAL (o fps de
            # montagem e o medido, nao o pedido), mas a sinalizacao fica
            # entrecortada. Serve para conferencia e para compor a janela;
            # para publicacao, prefira o portal VLibras Video.
            # Para sozinho quando o avatar fica imovel.
            #
            # O texto de teste sinalizava por ~65 s, mas a captura seguia ate o
            # tempo pedido e o player voltava a tela de abertura: o video
            # terminava com dois minutos de logo. Comparar quadros consecutivos
            # resolve sem depender do DOM, que aqui vive em shadow root.
            from PIL import Image, ImageChops

            intervalo = 1.0 / fps
            t0 = time.time()
            fim_captura = t0 + segundos
            anterior = None
            parados = 0
            descartado = 0.0
            limite_parado = int(fps * 5)      # 5 s sem movimento encerra

            while time.time() < fim_captura:
                inicio = time.time()
                destino = os.path.join(quadros, "q%05d.png" % capturados)
                try:
                    pg.screenshot(path=destino,
                                  clip={"x": caixa[0], "y": caixa[1],
                                        "width": caixa[2], "height": caixa[3]})
                    capturados += 1
                except Exception:
                    break

                try:
                    with Image.open(destino) as im:
                        atual = im.convert("L").resize((80, 116))
                    if anterior is not None:
                        dif = ImageChops.difference(atual, anterior)
                        movimento = sum(
                            i * n for i, n in enumerate(dif.histogram())) / 9280.0
                        parados = parados + 1 if movimento < 1.2 else 0
                        if parados >= limite_parado and capturados > fps * 8:
                            for k in range(capturados - parados, capturados):
                                alvo_ = os.path.join(quadros, "q%05d.png" % k)
                                if os.path.exists(alvo_):
                                    os.remove(alvo_)
                            capturados -= parados
                            descartado = parados * intervalo
                            break
                    anterior = atual
                except Exception:
                    pass

                resta = intervalo - (time.time() - inicio)
                if resta > 0:
                    time.sleep(resta)
            # desconta o trecho parado que foi descartado, senao o fps medido
            # sai baixo e o video toca em camera lenta
            decorrido = max(1.0, time.time() - t0 - descartado)
            caixa_final = list(caixa)
            nav.close()
    finally:
        srv.shutdown()

    if capturados < 10:
        shutil.rmtree(tmp, ignore_errors=True)
        raise RuntimeError("captura vazia: %d quadros" % capturados)

    # renumera: o corte do trecho parado deixa buracos na sequencia
    restantes = sorted(f for f in os.listdir(quadros) if f.endswith(".png"))
    for novo_i, nome in enumerate(restantes):
        alvo_ = os.path.join(quadros, "z%05d.png" % novo_i)
        os.rename(os.path.join(quadros, nome), alvo_)
    capturados = len(restantes)

    # fps REAL medido, nao o pedido: cada screenshot custa mais que o
    # intervalo alvo, e montar no fps nominal deixa o video acelerado — a
    # sinalizacao fica rapida demais para ser lida
    fps_real = max(1.0, capturados / max(decorrido, 0.001))

    os.makedirs(os.path.dirname(os.path.abspath(saida)) or ".", exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-framerate", "%.3f" % fps_real,
         "-i", os.path.join(quadros, "z%05d.png"),
         "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", saida],
        capture_output=True, timeout=600)
    tamanho = os.path.getsize(saida) if os.path.exists(saida) else 0
    shutil.rmtree(tmp, ignore_errors=True)
    return {"quadros": capturados, "segundos": decorrido, "fps_real": fps_real,
            "arquivo": saida, "bytes": tamanho}


def main():
    ap = argparse.ArgumentParser(description="Grava a janela de Libras (caminho A)")
    ap.add_argument("--texto")
    ap.add_argument("--arquivo")
    ap.add_argument("-o", "--saida", default="libras/janela-libras.mp4")
    ap.add_argument("--segundos", type=int, default=150)
    ap.add_argument("--fps", type=int, default=12)
    args = ap.parse_args()

    texto = args.texto
    if args.arquivo:
        with open(args.arquivo, encoding="utf-8") as f:
            texto = f.read().strip()
    if not texto:
        print("informe --texto ou --arquivo")
        return 2

    try:
        r = gravar(texto, args.saida, args.segundos, fps=args.fps)
    except RuntimeError as e:
        print("ERRO: %s" % e)
        return 2

    print("gravado: %s" % r["arquivo"])
    print("  %d quadros · %.0f s · %.1f fps reais · %.1f MB"
          % (r["quadros"], r["segundos"], r["fps_real"], r["bytes"] / 1048576))
    print("\nRevise antes de publicar: glosa automática erra concordância "
          "espacial e classificadores (regra J05).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
