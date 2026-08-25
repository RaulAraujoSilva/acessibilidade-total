# 03 — Ferramentas, plug-ins e o que cada um realmente cobre

> A pergunta certa não é "qual ferramenta usar", é **"o que esta ferramenta não vê"**.
> Nenhuma delas cobre o catálogo inteiro. A tabela abaixo diz onde cada uma cega.

---

## 1. Nativo do PowerPoint

### Verificador de Acessibilidade
`Revisão › Verificar Acessibilidade`

Cobre **exatamente 10 regras documentadas**, e nada além:

| Severidade | Regra |
|---|---|
| Erro | Todo conteúdo não textual tem texto alternativo |
| Erro | Tabelas especificam informação de cabeçalho de coluna |
| Erro | Todas as seções têm nomes significativos |
| Erro | Todos os slides têm título |
| Aviso | Tabela tem estrutura simples |
| Aviso | Contraste suficiente entre texto e plano de fundo |
| Aviso | Legendas ocultas incluídas em áudio e vídeo inseridos |
| Aviso | A ordem de leitura dos objetos no slide é lógica |
| Dica | Os nomes de seção do arquivo são exclusivos |
| Dica | Os títulos dos slides são exclusivos |

Mais o item de *Serviços Inteligentes*: **"Texto alternativo sugerido"**, que lista as imagens
com descrição gerada por IA para revisão.

**O que ele não vê** — e é por isso que este projeto existe: tamanho de fonte, alinhamento
justificado, entrelinha, itálico e caixa alta, idioma dos runs, texto sobre foto ou gradiente,
cor como único meio de informação, daltonismo, qualidade do alt text (ele aceita `foto1.png`
como descrição válida), descrição longa, links "clique aqui", animação e flash, alvo de clique,
Libras, audiodescrição e qualquer coisa do PDF exportado.

> **Não é automatizável.** Não existe objeto de automação que devolva os resultados do
> verificador. `Application.CommandBars.ExecuteMso` no máximo abre o painel. Por isso o
> auditor deste projeto reimplementa as 10 regras e a conferência no painel fica como passo
> humano registrado (M01).

### Painel de Ordem de Leitura
`Revisão › Verificar Acessibilidade › Painel de Ordem de Leitura`
Lista **de cima para baixo** = ordem em que o leitor de tela anuncia. Permite remover um item
da ordem por caixa de seleção (equivale a marcar como decorativo). Não renomeia nem oculta.

### Painel de Seleção
`Página Inicial › Organizar › Painel de Seleção` (Alt+F10)
Lista **de baixo para cima** = empilhamento do eixo Z. É a mesma lista do painel anterior,
invertida. Aqui se renomeia objeto e se oculta camada pelo ícone do olho — é assim que se faz
um título existir para o leitor de tela sem aparecer no slide.

### Legendas e Subtítulos ao Vivo
`Apresentação de Slides › Configurações de Legenda`
Transcreve a fala em tempo real e traduz para outro idioma na tela. Acomodação valiosa para
pessoas surdas oralizadas, participantes estrangeiros e neurodivergentes — mas **não substitui
Libras**, que é língua própria e não tradução do português.

---

## 2. Add-ins de terceiros

| Ferramenta | Plataforma | O que agrega sobre o nativo | Licença |
|---|---|---|---|
| **Grackle Office** | Add-in Word + PowerPoint | Dezenas de critérios além dos 10 nativos, remediação guiada e **pré-visualização de leitor de tela** — é a alternativa comercial mais próxima do que este catálogo faz | Comercial |
| **CommonLook Office** (Allyant) | Add-in Word/PPT/Excel | Constrói a acessibilidade na origem e controla a exportação Office → PDF | Comercial |
| **axes4 / axesPDF** | Word (axesWord) e verificação de PDF | Referência em PDF/UA; a base do PAC | Comercial + PAC gratuito |

---

## 3. PDF/UA — depois da exportação

| Ferramenta | Uso | Comando |
|---|---|---|
| **PAC 2024** | Padrão-ouro gratuito. Testa o Protocolo Matterhorn e mostra a árvore de tags e a pré-visualização de leitor de tela | Interface gráfica, Windows |
| **veraPDF** | Validador aberto PDF/A e PDF/UA, com CLI e Docker — é o que entra no pipeline automatizado | `verapdf --flavour ua1 arquivo.pdf` |
| **Adobe Acrobat Pro** | Remediação fina: Table Editor (define `/Scope` dos `TH`), Tag Tree, painel Ordem | Interface gráfica |
| **speedata/pdfa11y** | Validador de linha de comando alternativo | CLI |

> PAC e veraPDF **não são intercambiáveis**: o veraPDF verifica conformidade estrita com a ISO;
> o PAC verifica se o documento é de fato utilizável por tecnologia assistiva. Rodar os dois.

---

## 4. Leitores de tela — a prova real

| Leitor | Situação | Papel na auditoria |
|---|---|---|
| **NVDA** | Gratuito, código aberto, Windows | Leitor de referência do projeto |
| **JAWS** | Comercial, Windows | Segunda opinião, base instalada corporativa |
| **Narrador** | Nativo do Windows | Verificação rápida |
| **VoiceOver** | Nativo do macOS/iOS | Paridade em Mac |

**Atalhos que o auditor precisa saber usar:**

| Ação | Tecla |
|---|---|
| Alternar entre painéis (miniaturas, slide, notas, faixa) | `F6` / `Ctrl+F6` |
| Percorrer os objetos do slide na ordem de leitura | `Tab` |
| Ler as anotações do orador | `Ctrl+Shift+S` |
| Lista de elementos e links (NVDA) | `Insert+F7` |
| Ativar o Visualizador de Fala (NVDA) | `NVDA+n` › Ferramentas › Visualizador de Fala |

**Evidência auditável:** o Visualizador de Fala mostra na tela, mas não grava em arquivo. Para
gerar prova anexável ao relatório, use o add-on **Speech Logger**, que escreve a fala em texto,
ou a biblioteca `@guidepup/guidepup`, que expõe a fala do NVDA por socket para automação.

---

## 5. Cor

| Ferramenta | Uso |
|---|---|
| **TPGi Colour Contrast Analyser (CCA)** | Conta-gotas de tela; é a referência para conferir o cálculo do script |
| **WebAIM Contrast Checker** | Verificação rápida por HEX, na web |
| **Color Oracle** | Simula protanopia, deuteranopia e tritanopia na tela inteira, em tempo real |
| **Coblis** | Simulador online, por imagem |
| **Filtros de Cor do Windows** | `Win+Ctrl+C` — escala de cinza do sistema, para o teste E06 |

> O teste decisivo de 1.4.1 é barato: ligue a escala de cinza e leia o slide. Se alguma
> informação sumiu, a cor estava sozinha.

---

## 6. Libras

| Ferramenta | Situação | Automação |
|---|---|---|
| **VLibras** (SGD/MGISP + UFPB) | Gratuito, **LGPLv3, código aberto** | Suíte completa: Widget e Plugin (JS), Desktop (Windows), Vídeo (portal) e API. Repositórios em `github.com/spbgovbr-vlibras`, imagens no Docker Hub, pacote `vlibras-translate` no PyPI |
| **Hand Talk** | Comercial | API/plugin |
| **Rybená** | Comercial | Plugin |

Detalhes de implantação e dos caminhos automatizáveis: `06-libras.md`.

---

## 7. Áudio e legenda

| Ferramenta | Uso |
|---|---|
| **ElevenLabs** | Locução da audiodescrição em PT-BR |
| **Whisper** | Transcrição e geração de SRT a partir de áudio |
| **ffmpeg** | Montagem e conversão de mídia, embutir a janela de Libras |

---

## 8. Guias de referência para conferir o catálogo

- **WebAIM — Word and PowerPoint Accessibility Evaluation Guide**: procedimento de avaliação,
  campo a campo.
- **Section 508 — PowerPoint 365 Authoring and Testing Guide** e a checklist do PowerPoint 2016;
  o AED CoP mantém uma série em vídeo de 14 partes sobre autoria e teste.
- **Mass.gov — Microsoft PowerPoint Accessibility Testing Checklist**.
- **Microsoft — Regras do Verificador de Acessibilidade** (a fonte das 10 regras acima).

Quando o catálogo deste repositório divergir de qualquer um deles, **a divergência é registrada
e justificada**, nunca resolvida em silêncio.
