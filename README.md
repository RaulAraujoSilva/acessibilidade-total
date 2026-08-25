# Acessibilidade Total

**Skill para Claude Code que produz e audita apresentações acessíveis** — PowerPoint `.pptx` e
PDF/UA — segundo WCAG 2.2 AA (via WCAG2ICT), ISO 14289, LBI 13.146/2015 e e-MAG.

*[English version](README.en.md)*

> **Status:** base de conhecimento e catálogo de auditoria completos. Scripts do pipeline em
> construção.

---

## Por que existe

O Verificador de Acessibilidade do PowerPoint cobre **10 regras**. Ele não vê tamanho de fonte,
texto justificado, entrelinha, idioma dos trechos de texto, texto sobre foto, cor como único
meio de informação, daltonismo, qualidade do texto alternativo (aceita `foto1.png` como
descrição válida), descrição longa, links "clique aqui", animação, alvo de clique, Libras,
audiodescrição, nem qualquer coisa do PDF exportado.

Este repositório é o que falta: **~75 regras auditáveis**, cada uma com ID estável, severidade,
critério de origem, como detectar e como corrigir.

---

## O que traz

| | |
|---|---|
| **Catálogo de auditoria** | 12 camadas, ~75 regras — de metadados a PDF/UA e confirmação humana |
| **Cookbook OOXML** | Onde cada recurso mora no XML, extraído de arquivos reais, não de memória |
| **Paleta cega-segura calculada** | Okabe-Ito com variantes que de fato passam em contraste, com os números medidos |
| **Libras automatizado** | Caminhos com VLibras (LGPLv3, código aberto), sem depender de login |
| **Audiodescrição** | Alt text, descrição longa, faixa narrada e transcrição — as quatro camadas |
| **Exportação PDF/UA** | Automação por COM com marcas de estrutura, e validação |

---

## Achados que motivam o projeto

- **A paleta Okabe-Ito crua reprova no WCAG 1.4.11 sobre fundo claro.** Amarelo dá 1,24:1,
  laranja 2,11:1, azul-céu 2,16:1 — contra o mínimo de 3:1. Só três das oito cores passam. O
  repositório traz as variantes escurecidas já calculadas.
- **O `/Title` do PDF sai vazio** quando o `.pptx` não tem título nas propriedades — e como o
  `DisplayDocTitle` vem ativo, o leitor de tela passa a anunciar o nome do arquivo.
- **O `/Lang` do PDF exportado sai como `pt`, não `pt-BR`.**
- **O verificador nativo não é automatizável**: não existe objeto de automação que devolva seus
  resultados.
- **`.pptx` não tem troca de paleta em tempo de exibição.** A solução sem macro é um hub com
  Apresentações Personalizadas.
- **ABNT NBR 17060 é sobre aplicativos móveis e páginas web**, não sobre documentos — é uma
  citação errada frequente em trabalhos de acessibilidade documental.

---

## Instalação

```bash
git clone https://github.com/RaulAraujoSilva/acessibilidade-total
```

Como skill do Claude Code, copie ou aponte a pasta para o diretório de skills:

```
~/.claude/skills/acessibilidade-total/
```

Dependências: Python com `python-pptx`, `pywin32`, `pypdf`, `pymupdf`. Windows com PowerPoint
instalado para as operações via COM. Opcionais: `OPENAI_API_KEY` (figuras),
`ELEVENLABS_API_KEY` (audiodescrição), Docker e ffmpeg (Libras), veraPDF (validação).

---

## Estrutura

```
SKILL.md                              roteiro operacional
references/01-normas-e-legislacao.md  fundamentação e armadilhas de citação
references/02-catalogo-auditoria.md   ← o coração: as ~75 regras
references/03-ferramentas-e-plugins.md
references/04-ooxml-cookbook.md
references/05-alt-text-e-audiodescricao.md
references/06-libras.md
references/07-cor-e-tipografia.md
references/08-exportacao-pdfua.md
assets/paleta-okabe-ito.json          contrastes calculados, não estimados
scripts/                              pipeline (em construção)
```

---

## Princípios

1. Um artefato para todos — Desenho Universal, não uma versão por deficiência.
2. Estrutura antes de estética.
3. Silêncio é recurso: o decorativo é marcado como decorativo.
4. Saída de modelo não é entrega — toda descrição gerada passa por curadoria humana.
5. Ausência de evidência não é conformidade.
6. Degradar é permitido; degradar em silêncio, não.

---

## Origem

Nasceu do Trabalho 1 da disciplina **TCE 00191 — Documentos Acessíveis** (Doutorado em
Engenharia de Produção, UFF). Publicado para servir a quem precisa produzir material acessível
de verdade, e não apenas passar no verificador.

## Licença

MIT. Contribuições bem-vindas — em especial correções vindas de pessoas com deficiência que
usem o material produzido com esta skill.
