"""
Teste de integracao: o construtor tem de produzir algo que o AUDITOR aprove.

E o fecho do ciclo. De nada adianta um construtor que gera slide bonito e um
auditor que reprova o resultado: um dos dois esta errado.

    python tests/test_build.py
"""
from __future__ import annotations

import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from audit_pptx import audit, NAO_CONFORME  # noqa: E402
from build_deck import ErroDeRoteiro, construir  # noqa: E402

EXEMPLO = os.path.join(ROOT, "exemplos", "roteiro-exemplo.yaml")

# Usado quando PyYAML nao esta instalado (a CI instala so python-pptx).
ROTEIRO_MINIMO = {
    "apresentacao": {
        "titulo": "Deck de integração do construtor",
        "autor": "Suíte de testes",
        "idioma": "pt-BR",
    },
    "slides": [
        {"tipo": "capa", "titulo": "Capa do teste de integração",
         "subtitulo": "Gerado por build_deck"},
        {"tipo": "secao", "titulo": "Seção de exemplo",
         "conteudo": ["Cabeçalho de seção com uma linha de apoio."]},
        {"titulo": "Slide de texto simples",
         "conteudo": ["Primeira linha do corpo.", "Segunda linha do corpo."],
         "notas": "Notas do orador."},
        {"titulo": "Slide com tabela de dados",
         "conteudo": ["Tabela só para dados."],
         "tabela": {"alt": "Limiares de contraste por tamanho de texto",
                    "cabecalho": ["Texto", "AA"],
                    "linhas": [["Normal", "4,5:1"], ["Grande", "3:1"]]}},
        {"titulo": "Slide com link descritivo",
         "conteudo": ["O texto do link diz o destino."],
         "links": [{"texto": "Diretrizes WCAG 2.2 do W3C",
                    "url": "https://www.w3.org/TR/WCAG22/"}]},
    ],
}


def carregar():
    try:
        import yaml  # noqa: F401
        from build_deck import carregar_roteiro
        return carregar_roteiro(EXEMPLO), "exemplos/roteiro-exemplo.yaml"
    except ImportError:
        return ROTEIRO_MINIMO, "roteiro embutido (PyYAML ausente)"


def auditar(caminho, rotulo):
    rep = audit(caminho)
    ruins = [f for f in rep.findings if f["veredito"] == NAO_CONFORME]
    c = rep.counts()
    print("  %-22s %d Erros, %d Avisos, %d Dicas"
          % (rotulo, c.get("E", 0), c.get("A", 0), c.get("D", 0)))
    for f in ruins:
        print("      %s %s | %s | %s"
              % (f["severidade"], f["regra"], f["onde"], f["detalhe"][:80]))
    return ruins


def testa_recusa(roteiro_ruim, esperado):
    """O construtor tem de PARAR antes de gerar um slide inacessivel."""
    try:
        with tempfile.TemporaryDirectory() as d:
            construir(roteiro_ruim, os.path.join(d, "x.pptx"))
    except ErroDeRoteiro as e:
        ok = esperado.lower() in str(e).lower()
        print("  %-22s %s" % (esperado, "recusou corretamente" if ok
                              else "recusou, mas por outro motivo: %s" % e))
        return ok
    print("  %-22s ACEITOU — deveria ter recusado" % esperado)
    return False


def main() -> int:
    roteiro, fonte = carregar()
    print("=" * 72)
    print("Construtor -> auditor  (fonte: %s)" % fonte)
    print("=" * 72)

    falhas = 0
    with tempfile.TemporaryDirectory() as d:
        simples = os.path.join(d, "deck_simples.pptx")
        construir(roteiro, simples)
        falhas += len(auditar(simples, "deck simples"))

        modos = os.path.join(d, "deck_modos.pptx")
        construir(roteiro, modos, com_modos=True)
        falhas += len(auditar(modos, "deck com 3 modos"))

    print("\nO construtor recusa roteiro que produziria slide inacessivel:")
    import copy
    checagens = []

    r = copy.deepcopy(roteiro)
    r["slides"][2]["titulo"] = r["slides"][1]["titulo"]
    checagens.append(testa_recusa(r, "titulo repetido"))

    r = copy.deepcopy(roteiro)
    r["slides"][2]["conteudo"] = ["linha"] * 7
    checagens.append(testa_recusa(r, "limite e 6"))

    r = copy.deepcopy(roteiro)
    r["slides"][4]["links"] = [{"texto": "clique aqui", "url": "https://exemplo.org"}]
    checagens.append(testa_recusa(r, "link nao descritivo"))

    r = copy.deepcopy(roteiro)
    r["apresentacao"]["titulo"] = ""
    checagens.append(testa_recusa(r, "apresentacao.titulo"))

    falhas += sum(1 for c in checagens if not c)

    print("\n%s" % ("TUDO OK" if not falhas else "%d PROBLEMA(S)" % falhas))
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
