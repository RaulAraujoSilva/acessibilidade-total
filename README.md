# Acessibilidade Total

[![testes](https://github.com/RaulAraujoSilva/acessibilidade-total/actions/workflows/testes.yml/badge.svg)](https://github.com/RaulAraujoSilva/acessibilidade-total/actions/workflows/testes.yml)
[![licença MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-blue.svg)](LICENSE)

**Produz e audita apresentações acessíveis** — PowerPoint `.pptx` e PDF/UA — segundo
WCAG 2.2 AA (via WCAG2ICT), ISO 14289, LBI 13.146/2015 e e-MAG.

Funciona como skill do Claude Code **e** como ferramenta de linha de comando avulsa.

**Protótipo web de pesquisa:** [instalação e limites](web/README.md), [arquitetura](web/DESIGN.md) e [experimentos reproduzíveis](research/README.md). Inclui contas, chave OpenRouter própria cifrada, fila, importação de documentos, revisão e adaptador de renderização direta de Libras. A verificação local não constitui certificação de acessibilidade nem implantação pública pronta.

*[English version](README.en.md)*

> **Status:** catálogo, auditor, construtor, simulador, transcrição, diagramas e
> exportação PDF/UA prontos e testados. Audiodescrição narrada e janela de Libras
> em construção.

---

## Começando do zero

Você não precisa saber programar. São três passos.

### Windows

```powershell
git clone https://github.com/RaulAraujoSilva/acessibilidade-total
cd acessibilidade-total
.\instalar.ps1
```

O instalador cuida de tudo: acha o Python (e oferece instalá-lo se faltar), cria um ambiente
isolado dentro da própria pasta — **sem mexer no Python do seu sistema** — e instala as
bibliotecas. Depois **pergunta**, uma a uma, se você quer as ferramentas extras. Nada de
sistema é instalado sem você confirmar.

Para auditar um arquivo, **arraste o `.pptx` para cima do `auditar.bat`**. O relatório abre
sozinho.

### macOS e Linux

```bash
git clone https://github.com/RaulAraujoSilva/acessibilidade-total
cd acessibilidade-total
./instalar.sh
.venv/bin/python scripts/audit_pptx.py minha-apresentacao.pptx --md relatorio.md
```

O auditor roda em qualquer sistema. Só a exportação de PDF com marcas de estrutura exige
Windows, porque depende do PowerPoint instalado.

### Só quero auditar, nada mais

```powershell
.\instalar.ps1 -SomenteAuditor
```

Instala **uma** biblioteca. É o suficiente.

### Não sei o que tenho instalado

```bash
python scripts/verificar_ambiente.py
```

Lista tudo, e para cada item que falta diz **para que serve**, **o que deixa de funcionar
sem ele** e **o comando exato para instalar**.

### Como skill de um agente

`Agent Skills` é **especificação aberta** (agentskills.io), criada pela Anthropic e
adotada por cerca de 40 produtos. A mesma pasta funciona em todos — muda só o
diretório de destino:

| Agente | Onde copiar a pasta |
|---|---|
| Claude Code | `~/.claude/skills/acessibilidade-total/` |
| Codex, Cursor, Copilot, Gemini CLI e demais | `~/.agents/skills/acessibilidade-total/` |
| Só para um repositório | `.agents/skills/acessibilidade-total/` dentro dele |

O nome da pasta precisa ser igual ao campo `name` do `SKILL.md`. Depois disso, basta
pedir em linguagem natural: *"audite esta apresentação e me diga o que corrigir"*.

---

## O que cada dependência faz

O princípio é que **nada seja obrigatório além do essencial**. Cada peça que falta desliga
um pedaço, nunca o conjunto.

### O essencial — uma biblioteca

| | |
|---|---|
| **python-pptx** | Lê e escreve o arquivo `.pptx`. Traz junto `lxml` (processa o XML de dentro do arquivo), `Pillow` (imagens) e `XlsxWriter`. **Sem ela o auditor não roda.** É a única realmente obrigatória. |

### Para exportar e conferir o PDF

| | |
|---|---|
| **pywin32** | Conversa com o PowerPoint instalado para exportar PDF **com marcas de estrutura** — a única forma que preserva a acessibilidade. Sem ela, resta exportar à mão. Só Windows. |
| **pypdf** | Abre o PDF gerado e confere o miolo: `/Lang`, `/Title`, `/MarkInfo`, árvore de tags. |

### Para converter um documento em apresentação

| | |
|---|---|
| **PyMuPDF** | Extrai texto e imagens de um PDF de origem para virar roteiro de slides. |
| **python-docx** | Escreve a transcrição linear em `.docx` com estilos de título reais — é o que permite ler a apresentação inteira de forma linear no leitor de tela. |

### Para gerar conteúdo (opcional)

| | |
|---|---|
| **openai** | Gera as ilustrações com gpt-image-2. Exige `OPENAI_API_KEY`. |
| **requests** | Chamadas HTTP da audiodescrição (ElevenLabs) e do VLibras. |
| **playwright** | Dirige o Chrome para capturar o avatar do VLibras em vídeo (a janela de Libras). |

### Programas, não bibliotecas

| | Para que serve | Sem ele |
|---|---|---|
| **PowerPoint** | Exporta o PDF marcado; roda o Verificador nativo | O auditor do `.pptx` continua funcionando normalmente |
| **Docker** | Roda o veraPDF **sem instalar Java** | Valide o PDF pelo PAC |
| **ffmpeg** | Monta o vídeo da janela de Libras | Sem montagem de vídeo |

### Ferramentas de auditoria (todas opcionais)

| | Para que serve | Instalar |
|---|---|---|
| **veraPDF** | Valida o PDF contra a ISO 14289. Responde: *está conforme a norma?* | `docker pull verapdf/cli` |
| **PAC** | Checa o PDF pelo Protocolo Matterhorn, com árvore de tags e prévia de leitor de tela. Responde: *é utilizável de verdade?* | `winget install axes4.PAC` |
| **Colour Contrast Analyser** | Conta-gotas de contraste, para os casos que o auditor marca como indeterminado (texto sobre foto) | `winget install TPGi.CCAe` |
| **NVDA** | Leitor de tela — ver abaixo | `winget install NVAccess.NVDA` |

> veraPDF e PAC **não são intercambiáveis**: um pergunta se o arquivo cumpre a norma, o
> outro se ele é de fato usável por tecnologia assistiva. São perguntas diferentes.

---

## "Preciso instalar o NVDA? Eu não sou cego."

**Não.** O NVDA não é necessário para criar a apresentação, nem para converter, nem para
rodar a auditoria automática. Ele cobre **um único item** do catálogo: a regra **K03**, que
é a evidência de que a ordem de leitura funciona na prática. É instrumento de medida, não
de produção.

E ele **não precisa falar**. O jeito que testador vidente usa:

1. `NVDA+S` até chegar em **sem fala** — o programa fica mudo, mas continua respondendo.
2. Menu do NVDA › Ferramentas › **Visualizador de Fala** — abre uma janela que mostra, em
   texto, tudo o que seria falado.
3. Percorra o slide com `Tab` e leia a janela.
4. Para sair do NVDA a qualquer momento: `Insert+Q`.

Se você não quiser instalar nada, use o substituto automático:

```bash
python scripts/simular_leitura.py minha-apresentacao.pptx
```

Ele escreve o que um leitor de tela anunciaria, na ordem em que anunciaria:

```
Slide 1 de 2: "Por que a estrutura vem antes da estética"
   O leitor de tela navega pela hierarquia, não pelo desenho
   imagem, Hierarquia de três níveis, do título ao conteúdo e às notas
   (silêncio — Faixa estética do rodapé marcado como decorativo)

Slide 2 de 2: "O que o verificador nativo não enxerga"
   link, Diretrizes WCAG 2.2 do W3C
   tabela, 3 linhas, 2 colunas
     linha de cabeçalho: Camada | Cobertura nativa
     linha 1 — Camada: Texto alternativo, Cobertura nativa: Presença, não qualidade
```

É um **modelo** do comportamento, não o comportamento. Não substitui a regra K03 — mas
torna a ordem de leitura discutível antes do teste, e deixa quem enxerga entender o que
quem não enxerga vai receber.

---

## Por que este projeto existe

O Verificador de Acessibilidade do PowerPoint cobre **10 regras**. Ele não vê tamanho de
fonte, texto justificado, entrelinha, idioma dos trechos de texto, texto sobre foto, cor
como único meio de informação, daltonismo, qualidade do texto alternativo (aceita
`foto1.png` como descrição válida), descrição longa, links "clique aqui", animação, alvo de
clique, Libras, audiodescrição, nem qualquer coisa do PDF exportado.

Este repositório é o que falta: **118 regras auditáveis**, cada uma com ID estável,
severidade, critério de origem, como detectar e como corrigir.

---

## O que traz

| | |
|---|---|
| **Catálogo de auditoria** | 15 camadas, 118 regras — de metadados a PDF/UA, confirmação humana e composição |
| **Auditor automático** | Camadas A a I, N e O; as demais saem como *não verificado*, nunca aprovadas sem evidência |
| **Construtor** | Gera o deck a partir de um roteiro YAML e **recusa** o que produziria slide inacessível |
| **Exportação PDF/UA** | Corrige o que o PowerPoint erra e grava o identificador PDF/UA-1 |
| **Simulador de leitura** | O que o leitor de tela anunciaria, sem instalar leitor de tela |
| **Cookbook OOXML** | Onde cada recurso mora no XML, extraído de arquivos reais, não de memória |
| **Paleta cega-segura calculada** | Okabe-Ito com variantes que de fato passam em contraste, com os números medidos |
| **Libras automatizado** | Caminhos com VLibras (LGPLv3, código aberto), sem depender de login |
| **Audiodescrição** | Alt text, descrição longa, faixa narrada e transcrição — as quatro camadas |

---

## Achados que motivam o projeto

- **A paleta Okabe-Ito crua reprova no WCAG 1.4.11 sobre fundo claro.** Amarelo dá 1,24:1,
  laranja 2,11:1, azul-céu 2,16:1 — contra o mínimo de 3:1. Só três das oito cores passam.
  O repositório traz as variantes escurecidas já calculadas.
- **O `/Title` do PDF sai vazio** quando o `.pptx` não tem título nas propriedades — e como
  o `DisplayDocTitle` vem ativo, o leitor de tela passa a anunciar o nome do arquivo.
- **O `/Lang` do PDF exportado sai como `pt`, não `pt-BR`.**
- **O verificador nativo não é automatizável**: não existe objeto de automação que devolva
  seus resultados.
- **`.pptx` não tem troca de paleta em tempo de exibição.** Macro exigiria `.pptm`, que chega
  bloqueado por Mark-of-the-Web. A saída é **um arquivo por modo de cor**, gerados do mesmo
  roteiro e verificados um contra o outro.
- **ABNT NBR 17060 é sobre aplicativos móveis**, não sobre documentos — citação errada
  frequente. A NBR 17225:2025 também é de escopo web.
- **A NBR 15290 vigente é a de 2016** (confirmada em 11.12.2025), mas a que circula na
  internet é a de 2005, superada.

---

## Uso

### Começando de onde você está

O ponto de partida quase nunca é um roteiro em branco. É um `.pptx` que precisa ficar acessível,
ou um texto que precisa virar apresentação:

```bash
python scripts/importar.py apresentacao.pptx -o meu-material/
python scripts/importar.py artigo.md         -o meu-material/
```

Sai um `roteiro.yaml` com título, texto, tabelas, figuras e notas recuperados — e marcadores
`[FALTA: ...]` onde a origem não tinha o que é obrigatório. **A importação não inventa conteúdo**:
alt text adivinhado passa despercebido, ausência de alt text não.

### O pipeline inteiro num comando

```bash
python scripts/montar_tudo.py pasta-do-roteiro/ -o entrega/
```

Onze estágios com portão em cada um: diagramas → construção → auditoria dos `.pptx`
→ leitura simulada → transcrição → PDF marcado → veraPDF → Libras → audiodescrição →
reauditoria do arquivo **como entregue** → paridade entre versões. O portão do terceiro estágio
**para** o pipeline se sobrar Erro ou Aviso, porque exportar PDF de um arquivo reprovado só
propaga o defeito.

### Versões por público

```bash
python scripts/montar_tudo.py meu-material/ -o entrega/     --perfis completo,libras,leitura_facil --libras-por-slide
```

Além das três paletas, dois perfis: **`libras`**, com texto reduzido e janela de Libras em todo
slide (LBI art. 28 IV: *"Libras como primeira língua"*), e **`leitura_facil`**, uma ideia por
slide, para deficiência cognitiva e TDAH. As versões são verificadas umas contra as outras — o
que separa acesso de segregação está em `references/10-versoes-por-publico.md`, e é auditável.

### Passo a passo

```bash
# construir a partir de um roteiro declarativo
python scripts/build_deck.py roteiro.yaml -o deck.pptx --todos-os-modos

# auditar
python scripts/audit_pptx.py deck.pptx --md relatorio.md --json achados.json

# ver a ordem de leitura como um leitor de tela veria
python scripts/simular_leitura.py deck.pptx --md leitura.md

# exportar PDF marcado e validar contra a ISO 14289
python scripts/export_pdfua.py deck.pptx -o deck.pdf
python scripts/audit_pdf.py deck.pdf

# conferir o ambiente
python scripts/verificar_ambiente.py

# rodar a suíte de testes
python tests/run_all.py
```

O auditor sai com código 1 se houver Erro ou Aviso em aberto — serve direto em integração
contínua.

---

## Como isto é testado

Dois testes, em sentidos opostos, porque auditor que acusa tudo é tão inútil quanto o que
não acusa nada:

| Teste | Pergunta | Resultado |
|---|---|---|
| `test_auditor.py` | Enxerga o que foi plantado? | **33/33** defeitos detectados |
| `test_falso_positivo.py` | Se cala diante do que está certo? | **0** falsos positivos |

A integração contínua roda os dois em Ubuntu e Windows, com Python 3.9 e 3.12, instalando
**apenas `python-pptx`** — se algum script passar a exigir mais, o CI quebra antes de
quebrar na máquina de quem clonou.

---

## Estrutura

```
instalar.ps1 · instalar.sh            preparam o ambiente
auditar.bat                           arraste um .pptx para cima
requirements.txt                      dependências, cada uma explicada
SKILL.md                              roteiro operacional (Claude Code)
references/01-normas-e-legislacao.md  fundamentação e armadilhas de citação
references/02-catalogo-auditoria.md   ← o coração: as 118 regras
references/03-ferramentas-e-plugins.md
references/04-ooxml-cookbook.md
references/05-alt-text-e-audiodescricao.md
references/06-libras.md
references/07-cor-e-tipografia.md
references/08-exportacao-pdfua.md
scripts/                              construtor, auditor, simulador, exportador
exemplos/apresentacao/                roteiro e diagramas de um deck real
tests/                                deck-armadilha e deck de controle
assets/paleta-okabe-ito.json          contrastes calculados, não estimados
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
Engenharia de Produção, UFF). Publicado para servir a quem precisa produzir material
acessível de verdade, e não apenas passar no verificador.

## Licença

MIT. Contribuições bem-vindas — em especial correções vindas de pessoas com deficiência que
usem o material produzido com esta ferramenta.
