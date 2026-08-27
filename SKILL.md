---
name: acessibilidade-total
description: >
  Produção e auditoria de apresentações acessíveis (PowerPoint .pptx e PDF/UA) segundo
  WCAG 2.2 AA via WCAG2ICT, ISO 14289 (PDF/UA), LBI 13.146/2015 e e-MAG. Cobre texto
  alternativo e descrição longa, ordem de leitura, contraste e paleta cega-segura,
  tipografia para dislexia, tabelas semânticas, janela de Libras (VLibras),
  audiodescrição narrada, transcrição linear e exportação PDF marcada. Use ao criar,
  converter ou auditar qualquer apresentação de slides, ao receber pedido de "deck
  acessível", "acessibilidade em PowerPoint", "alt text", "ordem de leitura", "Libras",
  "audiodescrição", "daltonismo", "WCAG", "PDF/UA" ou "leitor de tela".
license: MIT
compatibility: >
  Auditor roda em qualquer sistema com Python e python-pptx. Exportação de PDF
  marcado exige Windows com PowerPoint instalado (COM). Opcionais:
  OPENAI_API_KEY, ELEVENLABS_API_KEY, Docker, ffmpeg, veraPDF.
metadata:
  version: "0.4.0"
  author: RaulAraujoSilva
  repositorio: https://github.com/RaulAraujoSilva/acessibilidade-total
---

# Acessibilidade Total — apresentações

Produz decks **acessíveis por construção** e os audita contra um catálogo explícito de regras.
Remediar depois é caro e frágil; nascer certo é barato.

---

## Princípios que governam tudo o que se faz aqui

1. **Um artefato para todos.** Desenho Universal, não uma versão por deficiência. Modos de cor
   são variações de paleta do mesmo conteúdo — nunca conteúdos diferentes.
2. **Estrutura antes de estética.** *Placeholder* antes de caixa de texto; tabela real antes de
   print de tabela.
3. **Silêncio é recurso.** O que é decorativo é marcado como decorativo. Ruído acústico exclui.
4. **Saída de modelo não é entrega.** Todo alt text, descrição e glosa gerados passam por
   curadoria humana antes de sair.
5. **Ausência de evidência não é conformidade.** O que não foi verificado entra no relatório
   como *não verificado*.
6. **Degradar é permitido; degradar em silêncio, não.** O relatório diz o que não foi entregue e
   por quê.

---

## Referências — carregue sob demanda

| Arquivo | Quando ler |
|---|---|
| `references/01-normas-e-legislacao.md` | Fundamentar; evitar as citações erradas (NBR 17060 e NBR 9050 **não** se aplicam a documento) |
| `references/02-catalogo-auditoria.md` | **Sempre que auditar.** 118 regras em 15 camadas, com ID, severidade, detecção e correção |
| `references/03-ferramentas-e-plugins.md` | Escolher ferramenta e saber o que ela não vê |
| `references/04-ooxml-cookbook.md` | Mexer no XML: alt text, decorativo, ordem, tabela, tema |
| `references/05-alt-text-e-audiodescricao.md` | Escrever alt text, descrição longa, roteiro de AD |
| `references/06-libras.md` | Janela de Libras e VLibras |
| `references/07-cor-e-tipografia.md` | Paleta, contraste, fonte, os três modos |
| `references/08-exportacao-pdfua.md` | Exportar e validar o PDF |
| `references/09-design-e-composicao.md` | **Composição**: grade, proporção, eixo Z, tipos de slide. Um slide acessível não é um slide feio |
| `references/10-versoes-por-publico.md` | **Versões por público**: Libras como primeira língua e leitura fácil. O que separa acesso de segregação, e a base legal de cada um |

---

## Onde esta skill mora

`Agent Skills` é especificação aberta (agentskills.io). A mesma pasta funciona em
produtos diferentes — muda só o diretório:

| Agente | Diretório |
|---|---|
| Claude Code | `~/.claude/skills/acessibilidade-total/` |
| Codex, Cursor, Copilot, Gemini CLI e demais | `~/.agents/skills/acessibilidade-total/` |
| Só para um repositório | `.agents/skills/acessibilidade-total/` no próprio repo |

O nome do diretório **precisa** ser igual ao campo `name` do frontmatter.

---

## Antes de qualquer coisa: conferir o ambiente

```bash
python scripts/verificar_ambiente.py
```

Diz o que está instalado, o que falta, **para que serve cada peça** e o comando exato de
instalação. O auditor roda com **uma** biblioteca (`python-pptx`); todo o resto é opcional e
desliga um pedaço específico, nunca o conjunto. Se faltar algo, `instalar.ps1` (Windows) ou
`instalar.sh` (macOS/Linux) resolve.

**NVDA não é requisito de produção.** Não é preciso para criar, converter nem auditar. Cobre
só a regra K03 — a evidência de que a ordem de leitura funciona na prática. Para inspecionar a
ordem sem instalar nada, use `scripts/simular_leitura.py`, que escreve o que o leitor de tela
anunciaria. É um modelo do comportamento, não o comportamento: não satisfaz a K03.

---

## Atalho: o kit inteiro num comando

```bash
python scripts/montar_tudo.py pasta-do-roteiro/ -o entrega/     --perfis completo,libras,leitura_facil     --libras-por-slide     --com-audio entrega/audiodescricao
```

Onze estágios com portão em cada um. O do estágio 3 **para** o pipeline se sobrar
Erro ou Aviso: exportar PDF de um `.pptx` reprovado só propaga o defeito para o
formato em que o material de fato circula.

| Flag | Para quê |
|---|---|
| `--perfis` | versões por público: `completo`, `libras`, `leitura_facil` |
| `--libras-por-slide` | grava e embute **uma janela de Libras por slide** no perfil `libras` |
| `--com-audio PASTA` | embute a audiodescrição nos perfis que a preveem |
| `--com-libras VIDEO` | janela única na capa (só para perfis com `libras_na_capa`) |
| `--perfis-todos-os-modos` | força cada perfil nas três paletas |
| `--pdf-todos-os-modos` | exporta um PDF por versão, não só o padrão |
| `--sem-diagramas` | reaproveita as figuras já geradas (poupa chamadas de API) |
| `--sem-pdf` · `--sem-modos` · `--arquivo-unico` | recortes e o desenho legado |

**Qual recurso vai em qual versão** está em `build_deck.RECURSOS`, e a regra
**O07** confere o arquivo contra esse mapa — nos dois sentidos: recurso que
falta e recurso que sobra.


## Fluxo de produção

### 0. Enquadrar
Identificar o conteúdo-fonte, o público, o meio (projeção, distribuição, ambos) e o entregável
final. Definir o nível alvo — padrão: **WCAG 2.2 AA**, com AAA no contraste de texto.

### 1. Roteirizar — ou **importar**
O ponto de partida real quase nunca é um roteiro em branco: é um `.pptx` que precisa ficar
acessível, ou um texto que precisa virar apresentação. `scripts/importar.py` cobre os dois:

```bash
python scripts/importar.py apresentacao.pptx -o pasta/   # recupera título, texto,
python scripts/importar.py texto.md          -o pasta/   # tabela, figura e notas
```

Ele **não inventa conteúdo**: o que falta sai como `[FALTA: ...]` e o build recusa o roteiro
enquanto o marcador estiver lá. Alt text adivinhado passa despercebido; a ausência dele, não.

Escrevendo do zero: cada slide com título **único**, mensagem única, elementos visuais previstos,
e a **`mensagem_chave`** — uma frase que resume o slide. Ela alimenta os perfis de público e é o
que a regra O04 compara entre versões. Aplicar aqui o sufixo de continuidade (`(1 de 3)`) —
depois é retrabalho.

### 2. Figuras
`scripts/gen_diagramas.py` monta diagramas técnicos em HTML e os converte em PNG — **uma versão
por paleta**, texto sempre exato, sem custo de API. Na paleta daltônica cada série ganha um
**ângulo de hachura próprio**: quem não distingue as cores distingue a trama, e quem imprime em
preto e branco também.

Para cada figura, escrever **no mesmo passo**:
- alt text de até ~150 caracteres, que responde *por que a figura está no slide*;
- descrição longa, que vai para as Anotações do orador.

**Figura sem esse par não entra no deck.** Regra do pipeline, não recomendação.


### 3. Construir
`scripts/gerar_modelo.py` produz `assets/modelo-acessivel.pptx` — **não use o template padrão
do Office**: ele traz `cap="all"` no layout de seção e posiciona o corpo acima do título.
`scripts/build_deck.py` monta o `.pptx` sobre esse modelo e a grade de `scripts/grade.py`:
*placeholders* reais, títulos únicos, `lang="pt-BR"` em todo run, paleta de
`assets/paleta-okabe-ito.json`, `firstRow` nas tabelas, decorativos marcados, ordem de leitura
explícita no `spTree`, metadados preenchidos.

### 4. Versões — dois eixos
**Paleta** (`padrao`, `alto_contraste`, `daltonico`) troca a cor e **nada mais**: entre paletas o
texto tem de ser idêntico. **Perfil de público** troca o registro do texto de propósito:

| Perfil | Público | O que muda |
|---|---|---|
| `completo` | todos — a versão que não falta nada a ninguém | nada |
| `libras` | Libras como primeira língua | texto reduzido à `mensagem_chave`, corpo 28pt, **4 das 12 colunas reservadas** e janela em todo slide |
| `leitura_facil` | deficiência cognitiva, TDAH | uma ideia por slide, corpo 30pt |

O texto reduzido **não é gerado**: vem do campo `mensagem_chave` que cada slide declara. Resumo
automático produziria uma terceira versão do conteúdo, com risco de dizer outra coisa — e sem
`mensagem_chave` o build **recusa** o perfil.

`libras` sai nas **três paletas**: quem não ouve depende inteiramente do canal visual.
`leitura_facil` sai só no padrão.

A fundamentação — inclusive o que **não** sustenta cada versão — está em
`references/10-versoes-por-publico.md`.


### 5. Enriquecer — o recurso segue o sentido que ele serve
Este é o passo em que mais se erra por excesso de zelo: embutir tudo em tudo **não é paridade**,
é peso morto. A audiodescrição atende quem não enxerga; a janela de Libras atende quem tem Libras
como primeira língua.

- **Audiodescrição** — `gen_audiodesc.py` (ElevenLabs) escreve as faixas e a transcrição
  obrigatória; `embutir_audio.py` põe cada faixa **dentro** do slide, sem reprodução automática,
  com alt text e o controle reordenado no `spTree` logo após o título. Entregar as faixas numa
  pasta ao lado cumpre a regra K02, mas quase ninguém abre a pasta.
- **Janela de Libras** — `gen_libras_slides.py` grava **uma por slide** (cache por hash do texto,
  manifesto com a taxa de quadros medida) e `embutir_libras.py --por-slide` as embute.
  `gen_libras.py` produz o `.srt` e a glosa.
  **Alvo de 24–25 fps**: não há mínimo normativo na NBR 15290, mas a ITU-T H.Sup1 recomenda ≥25 e
  a literatura mostra perda de compreensão abaixo de 10. A regra **J07** reprova abaixo de 15.
  Para gerar em lote sem navegador, a receita do renderizador Unity está em
  `references/06-libras.md` — inclusive a armadilha da imagem que concatena propaganda.
- **Legendas ao vivo** — **não** são propriedade do arquivo (verificado no objeto de automação):
  são preferência da máquina de quem apresenta. Entregam-se como instrução (regra J04).
- **Transcrição linear** em `.docx` com estilos de título reais (`gen_transcricao.py`).

**Nada disso substitui revisão humana.** Glosa automática erra concordância espacial e
classificadores; alt text gerado passa por curadoria antes de sair.


### 6. Exportar
`scripts/export_pdfua.py` — COM, `DocStructureTags=True`. Nunca "Imprimir para PDF".
Ele ainda corrige `/Lang` e `/Title`, que o PowerPoint entrega errados, e grava o
identificador PDF/UA-1 no XMP — sem ele o veraPDF reprova.

### 7. Auditar
`audit_pptx.py` (A–I e N) + `audit_contrast.py` + `audit_design.py` + `audit_pdf.py` (L) +
**`audit_pacote.py` (O)**. O laço volta ao passo 3 **até zerar Erros e Avisos**.

A camada **O** é a que olha o *conjunto*: paridade de texto entre paletas (O01/O02), equivalência
de mensagem-chave entre perfis (O04/O05), declaração de público (O06) e coerência com o mapa de
recursos (O07). Rode-a **depois** de embutir a mídia — é o arquivo como entregue que vale:

```bash
python scripts/audit_pacote.py entrega/*.pptx --md entrega/auditoria-pacote.md
```

A camada M (confirmação humana) sai como lista de pendências com instruções — nunca como item
aprovado sem evidência. Antes de fechar, rode `simular_leitura.py` e **leia a saída**.


## Fluxo de auditoria de um arquivo de terceiros

1. Rodar `audit_pptx.py` e ler o catálogo camada por camada.
2. Abrir o Painel de Ordem de Leitura e o Painel de Seleção e conferir C01 a C06 a olho.
3. Verificador nativo (M01) — lembrando que ele só cobre 10 regras.
4. NVDA com Speech Logger (M02) e anexar o log.
5. Escala de cinza (M03) e simulação de daltonismo (M04).
6. Exportar e validar em veraPDF e PAC.
7. Emitir o relatório: por regra, `ID · severidade · veredito · onde · evidência`, com contagem
   por severidade e a **lista explícita do que não foi verificado**.

---

## Erros que este projeto existe para não cometer

- Caixa de texto solta no lugar de *placeholder* — mata a estrutura na origem.
- Slide sem título porque a foto ocupa tudo — o título deve existir e ser ocultado, nunca
  apagado.
- Reordenar o retângulo de fundo para consertar a ordem de leitura, e com isso encobrir o texto
  — o certo é marcá-lo como decorativo.
- Aceitar o alt text da IA com o carimbo "Descrição gerada automaticamente".
- Usar a paleta Okabe-Ito crua como cor de texto — ela reprova em contraste sobre fundo claro.
- Justificar o texto.
- Célula mesclada em tabela.
- "Imprimir para PDF".
- Citar a ABNT NBR 17060 como fundamento — ela é sobre aplicativos móveis e páginas web, não
  sobre documentos.
- Entregar legenda ao vivo e chamar de acessibilidade em Libras.
