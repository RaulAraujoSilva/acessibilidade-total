# Leitura simulada — Acessibilidade-Total-uma-ferramenta-para-produz-padrao.pptx

O que um leitor de tela anunciaria, na ordem em que anunciaria.

> Isto e um **modelo** do comportamento, nao o comportamento. Nao substitui a regra K03, que exige o percurso real com NVDA. Serve para discutir a ordem de leitura antes do teste — e para quem enxerga entender o que quem nao enxerga vai receber.

```
Slide 1 de 36: "Acessibilidade Total"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Um material por público, quando a produção deixa de ser o limite
   Trabalho 1 · TCE 00191 — Documentos Acessíveis
   Doutorado em Engenharia de Produção · UFF
   Raul Araujo Silva
   [Ctrl+Shift+S — notas do orador]
      TCE — Tópicos em Ciência e Engenharia, disciplina 00191, Documentos Acessíveis. Esta apresentação é sobre a ferramenta que a construiu. Ela foi gerada por código a partir de um roteiro, auditada contra 118 regras e exportada em PDF validado contra a ISO 14289. O relatório de auditoria acompanha a entrega.
```

```
Slide 2 de 36: "Acessibilidade deste material"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Alvo: WCAG 2.2 nível AA, via WCAG2ICT. Contraste em AAA (16,3:1).
   Três arquivos de cor: padrão, alto contraste e daltônico-seguro.
   Alt text, ordem de leitura conferida e transcrição linear em .docx.
   Audiodescrição embutida em cada slide, sem reprodução automática.
   Janela de Libras em cada slide, na versão em Libras, com glosa automática.
   NÃO entregue: revisão por intérprete, nem leitura por pessoa cega.
   [Ctrl+Shift+S — notas do orador]
      [chave] Este material tem alt text, audiodescrição narrada e versão em Libras.
      Uma declaração de acessibilidade que só lista acertos é propaganda. A que lista as lacunas é documento técnico. Estas linhas mudaram duas vezes durante a produção: o material prometeu o vídeo em Libras, a promessa caiu quando o primeiro spike falhou, e voltou quando a causa da falha apareceu — a página era montada em memória, e o widget só abre servido por HTTP. A ressalva sobre a glosa fica: entregar a janela não é o mesmo que entregar tradução revisada. Corrigir a declaração nos dois sentidos é parte do método.
```

```
Slide 3 de 36: "A hipótese"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Acessibilidade supõe um material só. E se a suposição for economia?
```

```
Slide 4 de 36: "Um material para todos, ou um para cada?"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   O Desenho Universal manda fazer um material que sirva a todos.
   A regra tem duas razões: não dar menos, e não deixar versões divergirem.
   Mas quem tem Libras como língua materna lê português como segunda língua.
   Para essa pessoa, parede de texto não fica acessível por ter alt text.
   A pergunta deste trabalho: e se produzir vários deixasse de ser inviável?
   [Ctrl+Shift+S — notas do orador]
      [chave] Perguntamos se vale fazer um material para cada público.
      A LBI, no artigo 28, inciso quatro, fala em Libras como primeira língua e português escrito como segunda língua. Se a lei reconhece duas línguas, entregar só uma e chamar de universal é conveniência, não princípio. A pergunta não é retórica: ela só faz sentido agora, porque o custo de produzir mudou.
```

```
Slide 5 de 36: "O que tornava inviável"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   252
   slides para escrever e revisar
   Sete versões de trinta e seis slides, cada uma auditada.
   Mais trinta e seis faixas narradas e trinta e seis vídeos em Libras.
   Somam-se as descrições longas, uma por figura, em cada versão.
   Nenhuma equipe pequena faz isso à mão, e por isso ninguém fazia.
   [Ctrl+Shift+S — notas do orador]
      [chave] Fazer sete versões à mão custaria centenas de horas.
      Este é o número que sustenta a regra de um artefato só. Ele não vem da ética: vem do orçamento. Vale dizer isso com todas as letras, porque é o que a automação muda — e o que ela não muda.
```

```
Slide 6 de 36: "O que a automação muda, e o que não muda"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Some o custo: as sete versões saem de um comando só.
   Some a deriva: todas nascem do mesmo roteiro, na mesma hora.
   Não some o dever de entregar a mesma informação a todos.
   Por isso a equivalência virou regra auditável, e não promessa.
   [Ctrl+Shift+S — notas do orador]
      [chave] A automação tira o custo, não tira o dever.
      Das duas razões do artefato único, a automação derruba uma e reforça a outra. O custo cai. A divergência entre versões, que era o segundo medo, passa a ser verificada por máquina a cada build — algo que a produção manual nunca teve.
```

```
Slide 7 de 36: "O problema em um número"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   10
   regras no verificador nativo
   Ele não vê tamanho de fonte, texto justificado nem entrelinha.
   Não vê o idioma dos trechos, nem texto sobre foto.
   Não vê daltonismo, nem cor como único meio de informação.
   Aceita 'foto1.png' como texto alternativo válido.
   E não vê absolutamente nada do PDF exportado.
   [Ctrl+Shift+S — notas do orador]
      [chave] O verificador do PowerPoint vê só 10 regras.
      As dez regras estão documentadas pela própria Microsoft. Não são um defeito: são um piso. O problema é tratá-las como teto. Um arquivo pode passar limpo no verificador nativo e ainda assim ser inutilizável.
```

```
Slide 8 de 36: "Fundamentação: por que isto é obrigação, não gentileza"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   A cadeia normativa técnica, a lei brasileira e as armadilhas de citação.
```

```
Slide 9 de 36: "De onde vem a exigência"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   A WCAG foi escrita para a web.
   O WCAG2ICT (WCAG to ICT) é o que a torna aplicável a um arquivo.
   Sem citá-lo, a fundamentação fica incompleta.
   imagem, A WCAG 2.2 chega ao arquivo .pptx pelo WCAG2ICT e termina no PDF/UA
   [Ctrl+Shift+S — notas do orador]
      [chave] A exigência vem da lei e das normas técnicas.
      Este é o elo que quase todo trabalho de acessibilidade documental pula. Aplicar WCAG a um .pptx sem mencionar o WCAG2ICT é aplicar uma norma de web a algo que não é web, sem dizer com que autoridade.
      Descrição da figura: Diagrama de quatro elos ligados por setas da esquerda para a direita. Primeiro elo: WCAG 2.2, do W3C, com os quatro princípios perceptível, operável, compreensível e robusto. Segundo elo: WCAG2ICT, que traduz cada critério para software e documentos que não são páginas web. Terceiro elo: o arquivo .pptx, onde o critério vira estrutura real, como placeholder de título e cabeçalho de tabela. Quarto elo: PDF/UA, a norma ISO 14289, formato em que a apresentação de fato circula.
```

```
Slide 10 de 36: "A lei brasileira"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Lei 13.146/2015 (LBI): acessibilidade é direito, não cortesia.
   A LBI define formato acessível como o que o leitor de tela reconhece.
   Lei 10.436/2002 e Decreto 5.626/2005: a Libras é língua, não legenda.
   e-MAG 3.1 e a Cartilha gov.br: a prática na administração federal.
   A LBI é o dever. A verificação técnica se faz contra WCAG e PDF/UA.
   [Ctrl+Shift+S — notas do orador]
      [chave] A lei brasileira obriga material acessível.
      Escrever "conforme a LBI" sem apontar o critério técnico é retórica, não auditoria. A lei diz que tem de ser acessível; quem diz se está acessível é a norma técnica.
```

```
Slide 11 de 36: "As normas ABNT que se aplicam"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Conferidas no acervo ABNT do MPF (Ministério Público Federal): 45 normas.
   Normas ABNT aplicáveis ao material e o uso de cada uma
   tabela, 6 linhas, 2 colunas
     linha de cabecalho: Norma vigente | Uso neste material
     linha 1 — Norma vigente: NBR 15290:2016, Uso neste material: Parâmetros da janela de Libras
     linha 2 — Norma vigente: NBR 16452:2016, Uso neste material: Diretrizes da audiodescrição
     linha 3 — Norma vigente: NBR 15610-3:2016, Uso neste material: Libras na TV digital
     linha 4 — Norma vigente: NBR 15599:2008, Uso neste material: Comunicação na prestação de serviços
     linha 5 — Norma vigente: ISO 24495-1:2024, Uso neste material: Linguagem simples
   [Ctrl+Shift+S — notas do orador]
      [chave] Poucas normas ABNT valem para documento.
      A NBR 15290 vigente é a de 2016, confirmada em dezembro de 2025. A edição que circula livremente na internet é a de 2005, superada. Conferir a edição antes de citar é o que separa fundamentação de citação decorativa.
```

```
Slide 12 de 36: "Três citações erradas que este projeto recusa"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   NBR 17060:2022 é sobre aplicativos móveis. Não é norma de documento.
   NBR 17225:2025 é sobre conteúdo web. Também não alcança um .pptx.
   NBR 9050 é ambiente construído: rampas e pisos, não arquivos.
   NBR 15290:2005 está superada pela edição de 2016.
   O auditor sinaliza cada uma delas como fundamentação inválida.
   [Ctrl+Shift+S — notas do orador]
      [chave] Muita gente cita a norma errada.
      Estas quatro aparecem com frequência em trabalhos de acessibilidade documental. Todas foram verificadas no acervo do CB-040, uma a uma, e a constatação virou regra no catálogo.
```

```
Slide 13 de 36: "O que a ferramenta faz"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Um catálogo explícito, um auditor que o executa e um construtor que o obedece.
```

```
Slide 14 de 36: "O que foi construído"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Catálogo
   118 regras auditáveis
   em 15 camadas, de metadados a composição
   Auditor
   Camadas A a I, N e O
   as demais saem como não verificadas
   Construtor
   Deck acessível por construção
   recusa roteiro que sairia errado
   Exportação
   PDF/UA validado
   contra a ISO 14289, no veraPDF
   [Ctrl+Shift+S — notas do orador]
      [chave] Construímos uma ferramenta que produz e audita.
      A ordem importa: primeiro o catálogo, depois o auditor que o executa, depois o construtor que já nasce obedecendo. Construir antes de saber o que seria verificado teria produzido mais um gerador de slides bonitos.
```

```
Slide 15 de 36: "As 15 camadas do catálogo"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Cada regra tem identificador estável, severidade e critério de origem.
   E também: como detectar e como corrigir.
   As camadas A a I, N e O são automáticas; J a M dependem de mídia ou de pessoa.
   imagem, As 15 camadas do catálogo, de metadados do documento até design e composição
   [Ctrl+Shift+S — notas do orador]
      [chave] O catálogo tem 118 regras em 15 camadas.
      A camada M nunca é aprovada por script. Ela lista o que só um humano pode confirmar, e fica no relatório como pendência explícita.
      Descrição da figura: Lista vertical de quinze camadas identificadas pelas letras A a O, com o número de regras de cada uma. A, documento e metadados, 6 regras. B, estrutura semântica, 10. C, ordem de leitura, 6. D, texto alternativo, 11. E, cor e contraste, 10. F, tipografia e legibilidade, 10. G, tabelas, 6. H, hiperlinks, 4. I, mídia, movimento e interação, 9. J, Libras e público surdo, 9. K, público cego e audiodescrição, 5. L, exportação e PDF/UA, 7. M, confirmação humana, 6 itens. N, design e composição, 12. O, pacote e versões paralelas, 7. Somam 118. As camadas A a I, N e O são verificadas automaticamente; as camadas J a M dependem de mídia, do PDF ou de uma pessoa, e saem no relatório como não verificadas.
```

```
Slide 16 de 36: "Anatomia de uma regra"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Regra D05, severidade Erro, critério WCAG 1.1.1.
   Falha: alt text com resíduo 'Descrição gerada automaticamente'.
   Detecção: automática, por expressão regular sobre o atributo descr.
   Correção: reescrever com curadoria humana e apagar o aviso.
   Sem os cinco campos, uma regra é opinião. Com eles, é auditável.
   [Ctrl+Shift+S — notas do orador]
      [chave] Cada regra diz como achar e como corrigir.
      O Microsoft 365 gera alt text por visão computacional e carimba o resultado. O carimbo é útil: ele denuncia que ninguém revisou. A regra existe porque descrição automática não revisada não é descrição.
```

```
Slide 17 de 36: "O que o auditor vê e o nativo não"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Uma amostra da diferença de cobertura.
   Comparação entre a cobertura do verificador nativo e a deste projeto
   tabela, 7 linhas, 3 colunas
     linha de cabecalho: Verificação | Nativo | Aqui
     linha 1 — Verificação: Alt text presente, Nativo: sim, Aqui: sim
     linha 2 — Verificação: Qualidade do alt text, Nativo: não, Aqui: sim
     linha 3 — Verificação: Tamanho de fonte, Nativo: não, Aqui: sim
     linha 4 — Verificação: Texto justificado, Nativo: não, Aqui: sim
     linha 5 — Verificação: Idioma de cada trecho, Nativo: não, Aqui: sim
     linha 6 — Verificação: Contraste sobre foto, Nativo: não, Aqui: manda ao humano
   [Ctrl+Shift+S — notas do orador]
      [chave] O nosso auditor vê o que o nativo não vê.
      A última linha é a mais honesta da tabela. Texto sobre fotografia não tem resposta automática confiável: o auditor marca como não verificado e manda para o olho humano, em vez de chutar.
```

```
Slide 18 de 36: "Achados que só apareceram porque medimos"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   3 de 8
   cores da paleta Okabe-Ito passam em contraste
   A paleta crua reprova no critério 1.4.11 sobre fundo claro.
   Amarelo dá 1,24:1 e laranja 2,11:1, contra o mínimo de 3:1.
   O PDF exportado saiu com idioma 'en', e não português.
   E com título vazio: o leitor anunciava o nome do arquivo.
   Nada disso estava na literatura. Apareceu ao medir.
   [Ctrl+Shift+S — notas do orador]
      [chave] Medir revelou erros que ninguém via.
      Nenhum desses três achados estava em nenhuma fonte consultada. Todos apareceram ao medir arquivos reais nesta máquina. É a diferença entre repetir a literatura e verificar.
```

```
Slide 19 de 36: "Fluxo de trabalho"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Do roteiro ao PDF validado, com um portão em cada estágio.
```

```
Slide 20 de 36: "O pipeline em sete estágios"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Cada estágio tem um portão que pode reprovar.
   A correção volta para o roteiro, nunca para o arquivo gerado.
   imagem, Pipeline de sete estágios, do roteiro em YAML até o PDF validado
   [Ctrl+Shift+S — notas do orador]
      [chave] O material nasce do roteiro e passa por portões.
      Remediar o .pptx à mão é dívida técnica: a correção se perde no próximo build. Por isso o laço volta para o roteiro.
      Descrição da figura: Sequência numerada de sete estágios. Um, roteiro declarativo em YAML, com um bloco por slide. Dois, diagramas gerados em HTML e convertidos em imagem, uma versão por paleta. Três, construção do arquivo, com placeholder, idioma, contraste e ordem de leitura já corretos. Quatro, modos de cor: um arquivo por modo, com o mesmo conteúdo nos três. Cinco, auditoria do pptx contra as camadas A a N, exigindo zero erros e zero avisos. Seis, exportação para PDF com marcas de estrutura. Sete, validação do PDF no veraPDF. Se um portão reprova, a correção volta para o estágio um.
```

```
Slide 21 de 36: "Acessível por construção, não por remediação"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   O construtor recusa roteiro que geraria slide inacessível.
   Título repetido: o build para e diz em quais slides.
   Figura sem alt text ou sem descrição longa: o build para.
   Link escrito como 'clique aqui': o build para.
   Não existe a opção de gerar errado e consertar depois.
   [Ctrl+Shift+S — notas do orador]
      [chave] O slide já nasce certo.
      Isto inverte o custo. Remediar é caro e some no próximo build; nascer certo é barato e permanente. O construtor é a aplicação do catálogo no momento da escrita, e não da conferência.
```

```
Slide 22 de 36: "O simulador de leitura"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Escreve o que um leitor de tela anunciaria, na ordem em que anunciaria.
   Torna a ordem de leitura visível para quem enxerga.
   Não exige instalar leitor de tela nenhum.
   É um modelo do comportamento, não o comportamento.
   Não substitui o teste real: K03 exige NVDA (NonVisual Desktop Access).
   [Ctrl+Shift+S — notas do orador]
      [chave] Dá para ouvir o que o leitor de tela diria.
      Exemplo de saída: 'Slide 2 de 16, O que o verificador nativo não enxerga. Link, Diretrizes WCAG 2.2 do W3C. Tabela, 3 linhas, 2 colunas. Linha de cabeçalho: Camada, Cobertura nativa.'
```

```
Slide 23 de 36: "Dois eixos de separação"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Paleta troca a cor e nada mais: o texto tem de ser idêntico.
   Perfil troca o registro do texto, para outro público.
   Paleta: padrão, alto contraste e daltônico-seguro.
   Perfil: completo, Libras como primeira língua e leitura fácil.
   Sete arquivos, todos gerados do mesmo roteiro.
   [Ctrl+Shift+S — notas do orador]
      [chave] Separamos por paleta de cor e por público.
      A distinção entre os dois eixos é o que permite auditar. Entre paletas a exigência é texto idêntico. Entre perfis o texto muda de propósito, e o que se compara é a mensagem-chave que cada slide declara. Comparar literalmente entre perfis reprovaria por construção.
```

```
Slide 24 de 36: "Sete versões, sete públicos"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   As sete versões entregues, o público de cada uma e o que muda
   tabela, 6 linhas, 3 colunas
     linha de cabecalho: Versão | Para quem | O que carrega
     linha 1 — Versão: padrão, Para quem: uso geral, O que carrega: audiodescrição em cada slide
     linha 2 — Versão: alto contraste, Para quem: baixa visão, sala clara, O que carrega: audiodescrição, 21:1
     linha 3 — Versão: daltônico-seguro, Para quem: discromatopsia, O que carrega: audiodescrição, hachura
     linha 4 — Versão: libras (3 paletas), Para quem: Libras como 1ª língua, O que carrega: janela em cada slide
     linha 5 — Versão: leitura fácil, Para quem: cognitivo, atenção, O que carrega: uma ideia por slide
   [Ctrl+Shift+S — notas do orador]
      [chave] Cada versão tem um público e recursos próprios.
      O recurso segue o sentido que ele serve. A audiodescrição atende quem não enxerga e por isso não vai no arquivo em Libras, onde seriam treze megabytes de faixas que aquele público não usa. A janela de Libras não vai nos demais, porque uma janela avulsa num material que não tem Libras nos outros vinte e sete slides é selo, não acesso.
```

```
Slide 25 de 36: "O que separa acesso de segregação"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Nenhuma versão dá menos: toda mensagem-chave está em todas.
   Nenhuma versão dá mais: nada existe só num arquivo.
   Qualquer pessoa pode abrir qualquer versão.
   A versão completa carrega tudo, e nunca falta nada a ninguém.
   As condições viraram as regras O quatro a O sete, verificadas por máquina.
   [Ctrl+Shift+S — notas do orador]
      [chave] Versão diferente só vale se der a mesma informação.
      Esta é a resposta à objeção óbvia: versão por deficiência costuma ser versão pior. O que impede isso aqui não é boa intenção, é teste. O auditor compara as mensagens-chave entre as versões e reprova tanto o que falta quanto o que sobra. Sem essa verificação, equivalente seria palavra.
```

```
Slide 26 de 36: "Como usar"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   A ferramenta é uma skill, e skill hoje é formato aberto.
```

```
Slide 27 de 36: "Uma skill, muitos agentes"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Agent Skills é especificação aberta, publicada em dezembro de 2025.
   Uma pasta com SKILL.md, scripts, references e assets.
   A mesma pasta roda em produtos concorrentes, sem adaptação.
   imagem, A mesma pasta de skill roda em Claude Code, Codex, Cursor e mais de 30 agentes
   [Ctrl+Shift+S — notas do orador]
      [chave] A ferramenta funciona em vários assistentes.
      A consequência prática é que a ferramenta não fica presa a um fornecedor. Quem usa Codex instala exatamente a mesma pasta, em outro diretório.
      Descrição da figura: No centro, a estrutura de uma skill: o arquivo SKILL.md com metadados e instruções, mais as pastas opcionais scripts, references e assets. Ao redor, os produtos que leem esse mesmo formato: Claude Code, OpenAI Codex, Cursor, GitHub Copilot, VS Code, Gemini CLI, JetBrains Junie, Goose, OpenCode e mais de trinta outros. O formato foi criado pela Anthropic e liberado como especificação aberta, e foi adotado por produtos concorrentes em poucas semanas.
```

```
Slide 28 de 36: "Instalação em três passos"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Passo 1: clonar o repositório público.
   Passo 2: rodar instalar.ps1 no Windows, ou instalar.sh no Linux e macOS.
   Passo 3: arrastar um arquivo .pptx para cima de auditar.bat.
   O instalador cria um ambiente isolado e não toca no Python do sistema.
   Ferramentas de sistema só são instaladas se você confirmar.
   link, Repositório do projeto no GitHub
   [Ctrl+Shift+S — notas do orador]
      [chave] Instalar leva três passos.
      O auditor roda com uma única biblioteca, o python-pptx. Todo o resto é opcional e desliga um pedaço específico, nunca o conjunto.
```

```
Slide 29 de 36: "Uso dentro do agente"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Claude Code: copiar a pasta para ~/.claude/skills/.
   Codex e demais: copiar para ~/.agents/skills/, ou .agents/skills/ no repo.
   Depois disso, basta pedir em linguagem natural.
   Exemplo: 'audite esta apresentação e me diga o que corrigir'.
   O agente carrega o catálogo sob demanda e executa os scripts.
   [Ctrl+Shift+S — notas do orador]
      [chave] Você pede em português e o agente faz.
      O carregamento é progressivo: o agente lê só o nome e a descrição da skill no início, e carrega o corpo e as referências apenas quando a tarefa pede. É o que permite manter um catálogo de 118 regras sem ocupar contexto à toa.
```

```
Slide 30 de 36: "Como o agente entra no processo"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Você entrega um texto ou uma apresentação que já tem.
   O agente lê a skill e sabe as regras, os limites e a ordem dos passos.
   Ele roteiriza, constrói as sete versões, audita e relata o que falhou.
   Quem decide o que cada público precisa continua sendo você.
   O portão é do pipeline, não do agente: com erro aberto, não há entrega.
   [Ctrl+Shift+S — notas do orador]
      [chave] Você pede em português e o agente conduz o pipeline.
      A diferença entre isto e pedir slides a um modelo de linguagem é o portão. O agente não decide se está bom: ele roda o auditor, e o auditor recusa. Foi assim que apareceram os defeitos que ninguém tinha visto, inclusive dentro do próprio auditor.
```

```
Slide 31 de 36: "O que a máquina fez, e o que não fez"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Fez: cento e dezoito regras, o código e as sete versões.
   Fez: achou defeitos que passaram por três revisões humanas.
   Não fez: revisar a glosa de Libras, que erra concordância espacial.
   Não fez: escolher o que cada público precisa saber.
   Não fez: substituir o teste com pessoas com deficiência.
   [Ctrl+Shift+S — notas do orador]
      [chave] A máquina produziu e auditou, mas julgar continua humano.
      Vale ser específico sobre os defeitos: uma regra do catálogo saía como conforme sem nunca ter sido verificada, e a primeira janela de Libras entregue tinha dois quadros e meio por segundo, abaixo de qualquer condição já testada na literatura. Os dois apareceram porque alguém olhou, não porque a automação avisou.
```

```
Slide 32 de 36: "O que a ferramenta não faz"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Não escreve o conteúdo por você: o roteiro é humano.
   Não julga se o alt text está correto, só se ele é plausível.
   Não substitui teste com pessoa com deficiência.
   Não avalia contraste de texto sobre foto: manda para o olho humano.
   Não roda o verificador nativo: não existe API para isso.
   [Ctrl+Shift+S — notas do orador]
      [chave] A ferramenta não substitui teste com pessoas.
      Ferramenta que promete resolver acessibilidade sozinha vende conformidade, não acessibilidade. O limite declarado é parte do produto.
```

```
Slide 33 de 36: "Rigor: como sei que a ferramenta funciona"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Um auditor não testado é uma opinião com sotaque técnico.
```

```
Slide 34 de 36: "Testado nos dois sentidos"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Enxerga o que foi plantado?
   Um deck com defeitos plantados, cada um com gabarito.
   Resultado: todos detectados.
   Regra do gabarito não acusada é defeito do auditor.
   Cala diante do que está certo?
   Um deck correto de propósito.
   Resultado: zero falsos positivos.
   Auditor que acusa tudo é tão inútil quanto o que não acusa nada.
   [Ctrl+Shift+S — notas do orador]
      [chave] Testamos se acusa o erro e se aprova o certo.
      Na primeira execução o resultado foi 32 de 33, e a falha era do gabarito, não do auditor: eu havia plantado texto cinza a 20 pontos esperando a regra E01, mas 20 pontos é texto grande, e a regra correta é a E02.
```

```
Slide 35 de 36: "Ausência de evidência não é conformidade."
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   O princípio que impede a ferramenta de virar um selo
   [Ctrl+Shift+S — notas do orador]
      O que não pôde ser verificado entra no relatório como não verificado, nunca como aprovado. A camada M lista o que só um humano confirma: verificador nativo, NVDA, escala de cinza, simulação de daltonismo, e a leitura por uma pessoa com deficiência — que vale mais que todo o resto. Este é o princípio que impede a ferramenta de virar um selo: conformidade técnica é piso, não prova.
```

```
Slide 36 de 36: "Esta apresentação foi auditada por si mesma"
   imagem, Audiodescrição narrada deste slide. A transcrição está no arquivo transcricao-audiodescricao.md
   Gerada por código a partir do roteiro que a acompanha.
   Sete versões auditadas: zero erros e zero avisos em todas.
   Exportada em PDF com marcas de estrutura e identificador PDF/UA.
   Validada no veraPDF contra a ISO 14289, sem erros.
   O relatório de auditoria acompanha a entrega.
   link, Repositório com o código, o catálogo e este roteiro
   [Ctrl+Shift+S — notas do orador]
      [chave] Esta apresentação passou na própria auditoria.
      O relatório é a prova. Sem ele, esta lista seria só uma afirmação sobre a própria qualidade, que é exatamente o tipo de coisa que a ferramenta existe para não aceitar.
```
