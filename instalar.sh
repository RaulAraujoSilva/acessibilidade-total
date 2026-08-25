#!/usr/bin/env bash
# Prepara o ambiente da skill acessibilidade-total em Linux/macOS.
#
#   ./instalar.sh                  # tudo o que roda fora do Windows
#   ./instalar.sh --somente-auditor
#
# NOTA: a exportacao de PDF com marcas de estrutura depende do PowerPoint
# instalado (COM) e so funciona no Windows. O AUDITOR roda em qualquer sistema.
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$RAIZ"
SOMENTE_AUDITOR=0
[[ "${1:-}" == "--somente-auditor" ]] && SOMENTE_AUDITOR=1

titulo() { echo; echo "=========================================================================="; echo " $1"; echo "=========================================================================="; }
ok()     { echo "  [ok] $1"; }
passo()  { echo "  -> $1"; }
aviso()  { echo "  [!]  $1"; }

titulo "acessibilidade-total — instalacao"

PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done
if [[ -z "$PY" ]]; then
  echo "  [x] Python 3 nao encontrado."
  echo "      Debian/Ubuntu: sudo apt install python3 python3-venv"
  echo "      macOS:         brew install python"
  exit 1
fi
ok "Python encontrado ($($PY --version))"

if [[ ! -d .venv ]]; then
  passo "Criando o ambiente isolado em .venv..."
  "$PY" -m venv .venv
fi
VPY=".venv/bin/python"
ok "Ambiente isolado pronto"

passo "Instalando as bibliotecas Python..."
"$VPY" -m pip install --upgrade pip --quiet
if [[ $SOMENTE_AUDITOR -eq 1 ]]; then
  "$VPY" -m pip install "python-pptx>=1.0.2" --quiet
  ok "Instalado o minimo para auditar"
else
  "$VPY" -m pip install -r requirements.txt --quiet
  ok "Bibliotecas instaladas"
fi

if [[ $SOMENTE_AUDITOR -eq 0 ]]; then
  if command -v docker >/dev/null 2>&1; then
    read -r -p "  Baixar a imagem Docker do veraPDF (~500 MB, dispensa Java)? [s/N] " r
    [[ "$r" =~ ^[sSyY] ]] && docker pull verapdf/cli
  else
    aviso "Docker ausente: veraPDF indisponivel (regra L07 nao verificada)."
  fi
  aviso "PAC, CCA e NVDA sao ferramentas Windows. Em Linux/macOS use, no lugar:"
  echo "        veraPDF (PDF/UA) e o leitor de tela nativo — Orca no Linux,"
  echo "        VoiceOver no macOS."
fi

titulo "Verificando o que ficou instalado"
"$VPY" scripts/verificar_ambiente.py || true

titulo "Pronto"
cat <<'FIM'
  Para auditar uma apresentacao:

      .venv/bin/python scripts/audit_pptx.py arquivo.pptx --md relatorio.md

  Para ver o que um leitor de tela anunciaria:

      .venv/bin/python scripts/simular_leitura.py arquivo.pptx
FIM
echo
