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
| `references/02-catalogo-auditoria.md` | **Sempre que auditar.** 98 regras em 13 camadas, com ID, severidade, detecção e correção |
| `references/03-ferramentas-e-plugins.md` | Escolher ferramenta e saber o que ela não vê |
| `references/04-ooxml-cookbook.md` | Mexer no XML: alt text, decorativo, ordem, tabela, tema |
| `references/05-alt-text-e-audiodescricao.md` | Escrever alt text, descrição longa, roteiro de AD |
| `references/06-libras.md` | Janela de Libras e VLibras |
| `references/07-cor-e-tipografia.md` | Paleta, contraste, fonte, os três modos |
| `references/08-exportacao-pdfua.md` | Exportar e validar o PDF |

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

## Atalho: o pipeline inteiro num comando

```bash
python scripts/montar_tudo.py pasta-do-roteiro/ -o entrega/
```

Roda os sete estágios com portão em cada um. O portão do estágio 3 **para** o
pipeline se sobrar Erro ou Aviso: exportar PDF de um `.pptx` reprovado só propaga
o defeito para o formato em que o material de fato circula.

---

## Fluxo de produção

### 0. Enquadrar
Identificar o conteúdo-fonte, o público, o meio (projeção, distribuição, ambos) e o entregável
final. Definir o nível alvo — padrão: **WCAG 2.2 AA**, com AAA no contraste de texto.

### 1. Roteirizar
Derivar do material-fonte a lista de slides, cada um com: título **único**, mensagem única,
elementos visuais previstos. Aplicar aqui o sufixo de continuidade (`(1 de 3)`) — depois é
retrabalho.

### 2. Figuras
Gerar as ilustrações (`scripts/gen_images.py`, gpt-image-2). Para cada figura, escrever **no
mesmo passo**:
- alt text de até ~150 caracteres, que responde *por que a figura está no slide*;
- descrição longa, que vai para as Anotações do orador.

**Figura sem esse par não entra no deck.** Regra do pipeline, não recomendação.

### 3. Construir
`scripts/build_deck.py` monta o `.pptx` a partir de layouts do Slide Master:
*placeholders* reais, títulos únicos, `lang="pt-BR"` em todo run, paleta de
`assets/paleta-okabe-ito.json`, `firstRow` nas tabelas, decorativos marcados, ordem de leitura
explícita no `spTree`, metadados preenchidos.

### 4. Modos de exibição
Slide-hub com hiperlinks para três seções paralelas — Padrão, Alto contraste, Daltônico-seguro —
cada uma registrada como Apresentação Personalizada. Um arquivo, sem macro. Alvos de clique com
no mínimo 24×24 px CSS (228600 EMU).

### 5. Enriquecer
- Audiodescrição por slide (`gen_audiodesc.py`), com transcrição, sem autoplay.
- Janela de Libras (`gen_libras.py`): tenta o caminho A, depois o B, e **registra o nível
  alcançado**.
- Legendas ao vivo pré-configuradas.
- Transcrição linear em `.docx` com estilos de título reais (`gen_transcricao.py`).

### 6. Exportar
`scripts/export_pdfua.py` — COM, `DocStructureTags=True`. Nunca "Imprimir para PDF".
Ele ainda corrige `/Lang` e `/Title`, que o PowerPoint entrega errados, e grava o
identificador PDF/UA-1 no XMP — sem ele o veraPDF reprova.

### 7. Auditar
`audit_pptx.py` + `audit_contrast.py` + `audit_pdf.py` produzem o relatório por regra. O laço
volta ao passo 3 **até zerar Erros e Avisos**. A camada M do catálogo (confirmação humana) sai
como lista de pendências com instruções — nunca como item aprovado sem evidência.

Antes de fechar, rode `simular_leitura.py` e **leia a saída**: é a forma mais barata de
perceber que a ordem de leitura está certa no XML mas errada no sentido.

---

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
