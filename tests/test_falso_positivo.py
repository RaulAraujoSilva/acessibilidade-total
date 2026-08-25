"""
Teste inverso: o auditor nao pode acusar um deck correto.

Um auditor que acusa tudo e tao inutil quanto um que nao acusa nada — o
usuario aprende a ignorar o relatorio. Aqui, qualquer nao conformidade e
falso positivo, e o teste falha.

    python tests/make_deck_bom.py && python tests/test_falso_positivo.py
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, HERE)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from audit_pptx import audit, NAO_CONFORME, NAO_VERIFICADO  # noqa: E402
from make_deck_bom import SAIDA  # noqa: E402

# Itens que SEMPRE saem como nao verificados: dependem de midia, do PDF
# exportado ou de um humano. Nao sao falso positivo.
NV_ESPERADOS = {"J01", "J02", "J04", "K02", "K03", "K04",
                "L01", "L07", "M01", "M02", "M03", "M04", "M05", "M06"}


def main() -> int:
    if not os.path.exists(SAIDA):
        print("deck de controle ausente. Rode antes: python tests/make_deck_bom.py")
        return 2

    rep = audit(SAIDA)
    fps = [f for f in rep.findings if f["veredito"] == NAO_CONFORME]
    nv_extra = [f for f in rep.findings
                if f["veredito"] == NAO_VERIFICADO and f["regra"] not in NV_ESPERADOS]

    print("=" * 72)
    print("Deck de controle — falsos positivos: %d | nao verificados inesperados: %d"
          % (len(fps), len(nv_extra)))
    print("=" * 72)

    for f in fps:
        print("  FALSO POSITIVO  %s %s | %s | %s"
              % (f["severidade"], f["regra"], f["onde"], f["detalhe"][:90]))
    for f in nv_extra:
        print("  INDETERMINADO   %s | %s | %s"
              % (f["regra"], f["onde"], f["detalhe"][:90]))

    if not fps and not nv_extra:
        print("\nNenhum falso positivo. O auditor so acusa o que esta errado.")
    return 1 if (fps or nv_extra) else 0


if __name__ == "__main__":
    sys.exit(main())
