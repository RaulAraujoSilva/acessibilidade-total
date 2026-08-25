"""
Valida o auditor contra o deck-armadilha.

A pergunta que este teste responde nao e "o deck esta bom?" — ele e ruim de
proposito. E "o auditor enxerga o que foi plantado?". Regra do gabarito que
nao for acusada e defeito DO AUDITOR.

    python tests/make_deck_ruim.py && python tests/test_auditor.py
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

from audit_pptx import audit, NAO_CONFORME  # noqa: E402
from make_deck_ruim import GABARITO, SAIDA  # noqa: E402


def main() -> int:
    if not os.path.exists(SAIDA):
        print("deck-armadilha ausente. Rode antes: python tests/make_deck_ruim.py")
        return 2

    rep = audit(SAIDA)
    acusadas = {f["regra"] for f in rep.findings if f["veredito"] == NAO_CONFORME}
    esperadas = set(GABARITO)

    faltando = sorted(esperadas - acusadas)
    extras = sorted(acusadas - esperadas)

    print("=" * 72)
    print("Regras do gabarito: %d | acusadas pelo auditor: %d"
          % (len(esperadas), len(acusadas & esperadas)))
    print("=" * 72)

    if faltando:
        print("\nFALHAS DO AUDITOR — plantadas mas nao detectadas:")
        for r in faltando:
            print("   %s" % r)
    else:
        print("\nTodas as %d regras plantadas foram detectadas." % len(esperadas))

    if extras:
        print("\nDetectadas alem do gabarito (nao sao erro — o deck e ruim mesmo,")
        print("mas confira se nao ha falso positivo):")
        for r in extras:
            exemplos = [f for f in rep.findings
                        if f["regra"] == r and f["veredito"] == NAO_CONFORME]
            print("   %s — %s" % (r, exemplos[0]["detalhe"][:88]))

    c = rep.counts()
    print("\nResumo do relatorio: %d Erros, %d Avisos, %d Dicas, %d nao verificados"
          % (c.get("E", 0), c.get("A", 0), c.get("D", 0), c.get("nao_verificado", 0)))

    return 1 if faltando else 0


if __name__ == "__main__":
    sys.exit(main())
