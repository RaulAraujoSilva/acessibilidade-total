"""
libras_caminho_a — grava a janela de Libras capturando o VLibras Widget.

QUALIDADE, ANTES DE TUDO. A primeira versao deste script montava o video a
partir de um laco de `page.screenshot`, e cada screenshot custava ~0,4 s: o
resultado saia a **2,5 quadros por segundo**. Isso nao e "qualidade baixa", e
provavelmente **ininteligivel**:

  - nao ha taxa de quadros normativa na ABNT NBR 15290 (ela regula dimensao,
    posicao, contraste e foco);
  - a **ITU-T H.Sup1** recomenda **>= 25 fps** para conversacao em lingua de
    sinais;
  - o proprio renderizador oficial do VLibras usa `--framerate 24`;
  - a literatura empirica (Hooper et al., *Sign Language Studies* 8(1), 2007;
    Tran et al., ASSETS 2013) mostra perda de compreensao **abaixo de 10 fps**.

2,5 fps esta abaixo da condicao mais baixa ja testada em qualquer desses
estudos. Em Libras o movimento E fonologia — o parametro M — e a expressao
facial carrega marcacao gramatical.

A SAIDA: o filtro **`gfxcapture`** do ffmpeg (8.0+), que captura a janela pela
API Windows.Graphics.Capture. Ele pega o conteudo composto pela GPU, nao se
contamina com oclusao de outra janela, recorta na propria captura e entrega
tempo real. Resultado medido: **25 fps e 462x670 px**, contra 2,5 fps e 312x452.

DUAS ARMADILHAS QUE CUSTARAM TEMPO E FICAM ANOTADAS:

  1. O `gfxcapture` devolve **pixels FISICOS**; a pagina reporta pixels CSS.
     Com o Windows a 150%, `devicePixelRatio` diz 1.0 e a captura vem 1,483x
     maior. Recortar com a medida da pagina cai no lugar errado — e o primeiro
     recorte saiu numa area branca. Por isso ha uma **sonda**: captura 1 s da
     janela inteira, mede a largura real e deriva a escala.
  2. O libx264 recusa dimensao impar; o recorte e arredondado para par.

E as tres do widget, que continuam valendo:

  3. A pagina **precisa** ser servida por HTTP. Montada com `set_content`, o
     botao de acesso nunca fica clicavel — foi essa a causa da falha original.
  4. O elemento `[vw-access-button]` tem **altura zero**; e um marcador. O botao
     visivel e desenhado pelo plugin na borda direita.
  5. `window.getSelection()` **nao** dispara a traducao: o plugin escuta eventos
     reais de mouse.

    python scripts/libras_caminho_a.py --texto "..." -o libras/resumo.mp4
    python scripts/libras_caminho_a.py --arquivo resumo.txt -o libras/resumo.mp4

Exige: playwright + chromium (`playwright install chromium`) e ffmpeg 8.0+ no
PATH. Roda em modo COM JANELA: o WebGL do avatar nao renderiza em headless puro.
"""
from __future__ import annotations

import argparse
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

TITULO_PAGINA = "Roteiro em Libras"
FPS_ALVO = 25            # ITU-T H.Sup1 recomenda >= 25 para lingua de sinais
CAIXA_CSS = (316, 176, 312, 452)   # (recuo da direita, topo, largura, altura)

PAGINA = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>{titulo}</title>
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


def _ffmpeg_gfx(recorte, segundos, saida, fps=FPS_ALVO):
    """ffmpeg capturando a janela do navegador pelo titulo."""
    filtro = ("gfxcapture=window_title='(?i)%s':max_framerate=30:"
              "capture_cursor=0,fps=%d,hwdownload,format=bgra%s,format=yuv420p"
              % (TITULO_PAGINA, fps, recorte))
    return subprocess.Popen(
        ["ffmpeg", "-y", "-filter_complex", filtro, "-t", "%.2f" % segundos,
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", saida],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def _par(v):
    v = int(round(v))
    return v - (v % 2)


def _medir_escala(pg, tmp):
    """
    Descobre quantos pixels fisicos a captura tem por pixel CSS da pagina.

    Sem isto o recorte cai no lugar errado em qualquer tela que nao esteja a
    100%: `devicePixelRatio` reporta 1.0 e a captura vem 1,483x maior.
    """
    sonda = os.path.join(tmp, "_sonda.mp4")
    _ffmpeg_gfx(",crop=trunc(iw/2)*2:trunc(ih/2)*2", 1, sonda).communicate(timeout=90)
    dim = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=width,height",
         "-of", "csv=p=0", sonda], capture_output=True, text=True).stdout.strip()
    if not dim:
        raise RuntimeError("a sonda nao capturou a janela — ela esta visivel?")
    cap_w = int(dim.split(",")[0])
    m = pg.evaluate("() => ({ow: window.outerWidth,"
                    " cromo: window.outerHeight - window.innerHeight})")
    try:
        os.remove(sonda)
    except OSError:
        pass
    return cap_w / m["ow"], m["cromo"]


def _selecionar(pg):
    """Arraste real de mouse — e o que dispara a traducao."""
    alvo = pg.evaluate(
        "() => { const r = document.getElementById('alvo')"
        ".getBoundingClientRect(); return [Math.round(r.x),"
        " Math.round(r.y), Math.round(r.width), Math.round(r.height)]; }")
    pg.mouse.move(alvo[0] + 4, alvo[1] + 10)
    pg.mouse.down()
    pg.mouse.move(alvo[0] + alvo[2] - 8, alvo[1] + alvo[3] - 6, steps=30)
    pg.mouse.up()


def _duracao_estimada(texto, folga=6.0):
    """
    Quanto tempo gravar. A mesma taxa que o gerador de SRT usa (145 ppm),
    com folga para o avatar terminar o ultimo sinal.
    """
    return max(8.0, len(texto.split()) / 145.0 * 60.0 + folga)


def gravar(texto: str, saida: str, segundos: int = None, largura: int = 1280,
           altura: int = 800, fps: int = FPS_ALVO) -> dict:
    r = gravar_lote([("unico", texto)], os.path.dirname(os.path.abspath(saida)),
                    largura=largura, altura=altura, fps=fps,
                    segundos=segundos)["unico"]
    if os.path.abspath(r["arquivo"]) != os.path.abspath(saida):
        shutil.move(r["arquivo"], saida)
        r["arquivo"] = saida
    return r


def gravar_lote(itens, pasta: str, largura: int = 1280, altura: int = 800,
                fps: int = FPS_ALVO, segundos: int = None) -> dict:
    """
    Grava um video por item, reaproveitando UMA sessao de navegador.

    `itens` e uma lista de (nome, texto). O setup custa 24 s — 8 s de carga
    mais 16 s para o player Unity subir — e pagar isso por video tornaria um
    lote de 28 slides inviavel. Amortizado, o custo por video vira o tempo de
    sinalizacao mais um respiro.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError("playwright ausente: pip install playwright && "
                           "playwright install chromium")
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg ausente no PATH")
    if not shutil.which("ffprobe"):
        raise RuntimeError("ffprobe ausente no PATH (vem com o ffmpeg)")

    os.makedirs(pasta, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="libras_")
    with open(os.path.join(tmp, "index.html"), "w", encoding="utf-8") as f:
        f.write(PAGINA.format(titulo=TITULO_PAGINA, texto=itens[0][1]))

    srv, porta = _servir(tmp)
    feitos = {}

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

            escala, cromo = _medir_escala(pg, tmp)
            recuo, topo, larg_c, alt_c = CAIXA_CSS
            recorte = ",crop=%d:%d:%d:%d" % (
                _par(larg_c * escala), _par(alt_c * escala),
                int(round((largura - recuo) * escala)),
                int(round((topo + cromo) * escala)))

            for nome, texto in itens:
                alvo = os.path.join(pasta, "%s.mp4" % nome)
                dur = segundos if segundos else _duracao_estimada(texto)
                # troca o texto sem recarregar a pagina: recarregar mataria o
                # player Unity e devolveria os 24 s de setup
                pg.evaluate("(t) => { document.getElementById('alvo').textContent = t; }",
                            texto)
                time.sleep(0.4)
                proc = _ffmpeg_gfx(recorte, dur, alvo, fps)
                time.sleep(1.0)
                _selecionar(pg)
                proc.communicate(timeout=dur + 120)
                feitos[nome] = {
                    "arquivo": alvo,
                    "segundos": dur,
                    "bytes": os.path.getsize(alvo) if os.path.exists(alvo) else 0,
                }
                time.sleep(1.0)

            caixa_final = (_par(larg_c * escala), _par(alt_c * escala))
            nav.close()
    finally:
        srv.shutdown()
        shutil.rmtree(tmp, ignore_errors=True)

    for r in feitos.values():
        r.update({"fps": fps, "escala": round(escala, 4),
                  "px": "%dx%d" % caixa_final})
    return feitos


def fps_do_arquivo(caminho: str) -> float:
    """Taxa de quadros real de um mp4 — usada pela regra J07."""
    saida = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=avg_frame_rate", "-of", "csv=p=0", caminho],
        capture_output=True, text=True).stdout.strip()
    try:
        num, den = saida.split("/")
        return float(num) / float(den) if float(den) else 0.0
    except Exception:
        return 0.0


def main():
    ap = argparse.ArgumentParser(description="Grava a janela de Libras (caminho A)")
    ap.add_argument("--texto")
    ap.add_argument("--arquivo")
    ap.add_argument("-o", "--saida", default="libras/janela-libras.mp4")
    ap.add_argument("--segundos", type=int, default=None,
                    help="fixa a duração; por padrão é estimada pelo texto")
    ap.add_argument("--fps", type=int, default=FPS_ALVO)
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

    real = fps_do_arquivo(r["arquivo"])
    print("gravado: %s" % r["arquivo"])
    print("  %s · %.0f s · %.1f fps reais · %.1f MB"
          % (r["px"], r["segundos"], real, r["bytes"] / 1048576))
    if real < 15:
        print("\nAVISO (J07): abaixo de 15 fps a sinalização perde compreensão.")
    print("\nRevise antes de publicar: glosa automática erra concordância "
          "espacial e classificadores (regra J05).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
