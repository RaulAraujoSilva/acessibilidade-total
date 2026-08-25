"""
verificar_ambiente — diz o que voce tem, o que falta, e o que cada coisa faz.

Nenhuma dependencia e obrigatoria alem de python-pptx. Este script existe para
voce nao precisar adivinhar: para cada item ele responde
    (1) para que serve, (2) o que deixa de funcionar sem ele, (3) como instalar.

    python scripts/verificar_ambiente.py
    python scripts/verificar_ambiente.py --json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

WIN = sys.platform == "win32"

OK, FALTA, NA = "ok", "falta", "nao_se_aplica"
MARCA = {OK: "[ok]   ", FALTA: "[falta]", NA: "[n/a]  "}


# --------------------------------------------------------------------------
# Deteccao
# --------------------------------------------------------------------------
def tem_modulo(nome: str) -> bool:
    try:
        return importlib.util.find_spec(nome) is not None
    except (ImportError, ValueError):
        return False


def versao_modulo(nome: str) -> str:
    try:
        from importlib.metadata import version
        return version(nome)
    except Exception:
        return ""


def roda(cmd, timeout=8) -> bool:
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout, shell=False)
        return r.returncode == 0
    except Exception:
        return False


def tem_winget_pkg(pkg_id: str) -> bool:
    if not WIN or not shutil.which("winget"):
        return False
    try:
        r = subprocess.run(["winget", "list", "--id", pkg_id, "-e"],
                           capture_output=True, timeout=25, text=True,
                           encoding="utf-8", errors="replace")
        return r.returncode == 0 and pkg_id.lower() in (r.stdout or "").lower()
    except Exception:
        return False


def tem_powerpoint() -> bool:
    """Caminhos conhecidos primeiro; nada de varrer a arvore do Office."""
    if not WIN:
        return False
    import glob
    padroes = [
        r"C:\Program Files\Microsoft Office\root\Office*\POWERPNT.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office*\POWERPNT.EXE",
        r"C:\Program Files\Microsoft Office\Office*\POWERPNT.EXE",
        r"C:\Program Files (x86)\Microsoft Office\Office*\POWERPNT.EXE",
    ]
    for p in padroes:
        if glob.glob(p):
            return True
    return bool(shutil.which("POWERPNT.EXE"))


def tem_imagem_docker(nome: str) -> bool:
    if not shutil.which("docker"):
        return False
    try:
        r = subprocess.run(["docker", "images", "-q", nome],
                           capture_output=True, timeout=15, text=True)
        return bool((r.stdout or "").strip())
    except Exception:
        return False


# --------------------------------------------------------------------------
# Catalogo de dependencias
# --------------------------------------------------------------------------
def montar_itens():
    itens = []

    def add(nome, grupo, estado, serve, sem_ele, instalar, essencial=False, versao=""):
        itens.append({"nome": nome, "grupo": grupo, "estado": estado,
                      "serve": serve, "sem_ele": sem_ele,
                      "instalar": instalar, "essencial": essencial,
                      "versao": versao})

    # ---- Python ---------------------------------------------------------
    v = sys.version_info
    add("Python %d.%d" % (v.major, v.minor), "Base",
        OK if v >= (3, 9) else FALTA,
        "Roda todos os scripts da skill.",
        "Nada funciona.",
        "winget install Python.Python.3.12" if WIN else "sudo apt install python3",
        essencial=True, versao=sys.version.split()[0])

    # ---- Bibliotecas ----------------------------------------------------
    libs = [
        ("python-pptx", "pptx", True,
         "Le e escreve o arquivo .pptx. Traz junto lxml (XML), Pillow (imagens) "
         "e XlsxWriter.",
         "O AUDITOR NAO RODA. E a unica biblioteca realmente obrigatoria."),
        ("pypdf", "pypdf", False,
         "Le a estrutura interna do PDF: /Lang, /Title, /MarkInfo e a arvore de tags.",
         "Nao da para conferir se o PDF exportado saiu acessivel (camada L)."),
        ("pywin32", "win32com", False,
         "Conversa com o PowerPoint instalado (COM) para exportar PDF COM marcas "
         "de estrutura, e para marcar formas como decorativas do jeito que o "
         "proprio PowerPoint escreve.",
         "Nao da para exportar PDF acessivel por script. So Windows."),
        ("PyMuPDF", "fitz", False,
         "Extrai texto e imagens de PDFs de origem, para virar roteiro de slides.",
         "Nao da para converter um PDF em apresentacao automaticamente."),
        ("openai", "openai", False,
         "Gera as ilustracoes com gpt-image-2.",
         "Sem geracao de figuras. Voce ainda pode usar imagens proprias."),
        ("requests", "requests", False,
         "Chamadas HTTP: audiodescricao (ElevenLabs) e VLibras.",
         "Sem audiodescricao narrada e sem janela de Libras automatica."),
        ("python-docx", "docx", False,
         "Escreve a transcricao linear em .docx com estilos de titulo reais.",
         "Sem o documento de transcricao (regra K04)."),
        ("playwright", "playwright", False,
         "Dirige o Chrome para capturar o avatar do VLibras em video.",
         "Sem janela de Libras pelo caminho automatico."),
    ]
    for nome, mod, essencial, serve, sem_ele in libs:
        presente = tem_modulo(mod)
        if nome == "pywin32" and not WIN:
            add(nome, "Bibliotecas Python", NA, serve,
                "So existe no Windows; em Linux/macOS a exportacao PDF marcada "
                "nao esta disponivel.", "—")
            continue
        add(nome, "Bibliotecas Python", OK if presente else FALTA, serve, sem_ele,
            "pip install -r requirements.txt", essencial, versao_modulo(nome))

    if tem_modulo("playwright"):
        add("Chromium do Playwright", "Bibliotecas Python",
            OK if os.path.isdir(os.path.expanduser(
                "~/AppData/Local/ms-playwright" if WIN else "~/.cache/ms-playwright"))
            else FALTA,
            "O navegador que o Playwright controla.",
            "A captura do avatar do VLibras nao roda.",
            "playwright install chromium")

    # ---- Programas ------------------------------------------------------
    add("Microsoft PowerPoint", "Programas",
        OK if tem_powerpoint() else (FALTA if WIN else NA),
        "Exporta o PDF com marcas de estrutura (a unica forma que preserva a "
        "acessibilidade) e roda o Verificador de Acessibilidade nativo.",
        "Sem exportacao PDF/UA automatica. O auditor do .pptx continua rodando "
        "normalmente.",
        "Instalacao manual (licenca Microsoft 365).")

    add("Docker", "Programas", OK if shutil.which("docker") else FALTA,
        "Roda o veraPDF sem precisar instalar Java, e a pilha do VLibras.",
        "Valide o PDF pelo PAC, ou instale Java + veraPDF.",
        "winget install Docker.DockerDesktop" if WIN else "https://docs.docker.com/engine/install/")

    add("ffmpeg", "Programas", OK if shutil.which("ffmpeg") else FALTA,
        "Monta e converte video: junta a janela de Libras ao material.",
        "Sem montagem de video de Libras.",
        "winget install Gyan.FFmpeg" if WIN else "sudo apt install ffmpeg")

    # ---- Ferramentas de auditoria ---------------------------------------
    add("veraPDF", "Ferramentas de auditoria",
        OK if (shutil.which("verapdf") or tem_imagem_docker("verapdf/cli")) else FALTA,
        "Valida o PDF contra a norma ISO 14289 (PDF/UA). Responde: 'esta conforme "
        "a norma?'",
        "A regra L07 fica NAO VERIFICADA.",
        "docker pull verapdf/cli   (nao exige Java)")

    add("PAC (PDF Accessibility Checker)", "Ferramentas de auditoria",
        OK if tem_winget_pkg("axes4.PAC") else (FALTA if WIN else NA),
        "Checa o PDF pelo Protocolo Matterhorn e mostra a arvore de tags e uma "
        "previa de leitor de tela. Responde: 'e utilizavel de verdade?'",
        "A regra L07 fica so com o veraPDF, que responde outra pergunta.",
        "winget install axes4.PAC")

    add("Colour Contrast Analyser (CCA)", "Ferramentas de auditoria",
        OK if (tem_winget_pkg("TPGi.CCAe") or tem_winget_pkg("TPGi.CCA"))
        else (FALTA if WIN else NA),
        "Conta-gotas de contraste na tela. Serve para CONFERIR o calculo do "
        "auditor em casos que ele marca como indeterminado (texto sobre foto).",
        "A regra E09 depende so do olho.",
        "winget install TPGi.CCAe")

    add("NVDA (leitor de tela)", "Ferramentas de auditoria",
        OK if tem_winget_pkg("NVAccess.NVDA") else (FALTA if WIN else NA),
        "OPCIONAL. Nao e preciso para criar a apresentacao nem para a auditoria "
        "automatica. Serve a UM item: a evidencia de que a ordem de leitura "
        "funciona na pratica (regras K03/M02). Voce nao precisa ouvir nada: "
        "NVDA+S poe em modo silencioso e o Speech Viewer mostra em texto, na "
        "tela, tudo o que seria falado.",
        "As regras K03/M02 ficam NAO VERIFICADAS. Use "
        "scripts/simular_leitura.py como aproximacao automatica.",
        "winget install NVAccess.NVDA")

    # ---- Credenciais ----------------------------------------------------
    for var, serve, sem_ele in [
        ("OPENAI_API_KEY", "Geracao de figuras com gpt-image-2.",
         "Sem figuras geradas."),
        ("ELEVENLABS_API_KEY", "Locucao da audiodescricao em PT-BR.",
         "Sem faixa de audiodescricao narrada."),
    ]:
        add(var, "Credenciais (so para gerar conteudo)",
            OK if os.environ.get(var) else FALTA, serve, sem_ele,
            "Defina a variavel de ambiente %s" % var)

    return itens


# --------------------------------------------------------------------------
# Saida
# --------------------------------------------------------------------------
def imprimir(itens):
    print()
    print("=" * 78)
    print(" acessibilidade-total — verificacao de ambiente")
    print("=" * 78)

    grupos = []
    for it in itens:
        if it["grupo"] not in grupos:
            grupos.append(it["grupo"])

    faltando_essencial = []
    for g in grupos:
        print("\n%s" % g.upper())
        print("-" * 78)
        for it in [x for x in itens if x["grupo"] == g]:
            ver = (" %s" % it["versao"]) if it["versao"] else ""
            print("%s %s%s" % (MARCA[it["estado"]], it["nome"], ver))
            if it["estado"] == FALTA:
                print("          para que serve: %s" % _quebra(it["serve"]))
                print("          sem ele:        %s" % _quebra(it["sem_ele"]))
                print("          instalar:       %s" % it["instalar"])
                if it["essencial"]:
                    faltando_essencial.append(it["nome"])

    print("\n" + "=" * 78)
    if faltando_essencial:
        print(" FALTA O ESSENCIAL: %s" % ", ".join(faltando_essencial))
        print(" Rode:  pip install -r requirements.txt")
    else:
        print(" O essencial esta instalado — o auditor roda.")
        opcionais = [x["nome"] for x in itens if x["estado"] == FALTA]
        if opcionais:
            print(" Opcionais ausentes (cada um desliga um pedaco, nunca o todo):")
            print("   %s" % ", ".join(opcionais))
    print("=" * 78 + "\n")


def _quebra(texto, largura=62, recuo=" " * 26):
    palavras, linhas, atual = texto.split(), [], ""
    for p in palavras:
        if len(atual) + len(p) + 1 > largura:
            linhas.append(atual)
            atual = p
        else:
            atual = (atual + " " + p).strip()
    if atual:
        linhas.append(atual)
    return ("\n" + recuo).join(linhas)


def main():
    ap = argparse.ArgumentParser(description="Verifica o ambiente da skill")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    itens = montar_itens()
    if args.json:
        print(json.dumps(itens, ensure_ascii=False, indent=2))
    else:
        imprimir(itens)

    essencial_faltando = any(x["essencial"] and x["estado"] == FALTA for x in itens)
    return 1 if essencial_faltando else 0


if __name__ == "__main__":
    sys.exit(main())
