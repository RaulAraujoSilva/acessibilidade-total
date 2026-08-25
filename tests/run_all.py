"""Roda a suite completa: gera os dois decks e valida o auditor nos dois sentidos."""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
PASSOS = [("gera deck-armadilha", "make_deck_ruim.py"),
          ("gera deck de controle", "make_deck_bom.py"),
          ("detecta o que foi plantado", "test_auditor.py"),
          ("nao acusa o que esta certo", "test_falso_positivo.py"),
          ("constroi o que o auditor aprova", "test_build.py")]
falhou = 0
for titulo, script in PASSOS:
    print("\n>>> %s (%s)" % (titulo, script))
    r = subprocess.run([sys.executable, os.path.join(HERE, script)])
    if r.returncode:
        falhou += 1
print("\n%s" % ("TUDO OK" if not falhou else "%d PASSO(S) FALHARAM" % falhou))
sys.exit(1 if falhou else 0)
