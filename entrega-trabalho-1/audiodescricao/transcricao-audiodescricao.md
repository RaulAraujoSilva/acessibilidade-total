# Transcrição da audiodescrição

Arquivo: `Acessibilidade-Total-uma-ferramenta-para-produz-padrao.pptx`

Cada bloco corresponde a uma faixa de áudio. A transcrição é obrigatória: audiodescrição sem ela não é auditável e exclui quem usa linha braille.

## slide-01

Slide 1 de 36. Acessibilidade Total. Um material por público, quando a produção deixa de ser o limite. Trabalho 1 · TCE 00191 — Documentos Acessíveis. Doutorado em Engenharia de Produção · UFF. Raul Araujo Silva.

## slide-02

Slide 2 de 36. Acessibilidade deste material. Alvo: WCAG 2.2 nível AA, via WCAG2ICT. Contraste em AAA (16,3:1). Três arquivos de cor: padrão, alto contraste e daltônico-seguro. Alt text, ordem de leitura conferida e transcrição linear em .docx. Audiodescrição embutida em cada slide, sem reprodução automática. Janela de Libras em cada slide, na versão em Libras, com glosa automática. NÃO entregue: revisão por intérprete, nem leitura por pessoa cega.

## slide-03

Slide 3 de 36. A hipótese. Acessibilidade supõe um material só. E se a suposição for economia?

## slide-04

Slide 4 de 36. Um material para todos, ou um para cada?. O Desenho Universal manda fazer um material que sirva a todos. A regra tem duas razões: não dar menos, e não deixar versões divergirem. Mas quem tem Libras como língua materna lê português como segunda língua. Para essa pessoa, parede de texto não fica acessível por ter alt text. A pergunta deste trabalho: e se produzir vários deixasse de ser inviável?

## slide-05

Slide 5 de 36. O que tornava inviável. 252. slides para escrever e revisar. Sete versões de trinta e seis slides, cada uma auditada. Mais trinta e seis faixas narradas e trinta e seis vídeos em Libras. Somam-se as descrições longas, uma por figura, em cada versão. Nenhuma equipe pequena faz isso à mão, e por isso ninguém fazia.

## slide-06

Slide 6 de 36. O que a automação muda, e o que não muda. Some o custo: as sete versões saem de um comando só. Some a deriva: todas nascem do mesmo roteiro, na mesma hora. Não some o dever de entregar a mesma informação a todos. Por isso a equivalência virou regra auditável, e não promessa.

## slide-07

Slide 7 de 36. O problema em um número. 10. regras no verificador nativo. Ele não vê tamanho de fonte, texto justificado nem entrelinha. Não vê o idioma dos trechos, nem texto sobre foto. Não vê daltonismo, nem cor como único meio de informação. Aceita 'foto1.png' como texto alternativo válido. E não vê absolutamente nada do PDF exportado.

## slide-08

Slide 8 de 36. Fundamentação: por que isto é obrigação, não gentileza. A cadeia normativa técnica, a lei brasileira e as armadilhas de citação.

## slide-09

Slide 9 de 36. De onde vem a exigência. A WCAG foi escrita para a web. O WCAG2ICT (WCAG to ICT) é o que a torna aplicável a um arquivo. Sem citá-lo, a fundamentação fica incompleta. Descrição da figura. Diagrama de quatro elos ligados por setas da esquerda para a direita. Primeiro elo: WCAG 2.2, do W3C, com os quatro princípios perceptível, operável, compreensível e robusto. Segundo elo: WCAG2ICT, que traduz cada critério para software e documentos que não são páginas web. Terceiro elo: o arquivo .pptx, onde o critério vira estrutura real, como placeholder de título e cabeçalho de tabela. Quarto elo: PDF/UA, a norma ISO 14289, formato em que a apresentação de fato circula.

## slide-10

Slide 10 de 36. A lei brasileira. Lei 13.146/2015 (LBI): acessibilidade é direito, não cortesia. A LBI define formato acessível como o que o leitor de tela reconhece. Lei 10.436/2002 e Decreto 5.626/2005: a Libras é língua, não legenda. e-MAG 3.1 e a Cartilha gov.br: a prática na administração federal. A LBI é o dever. A verificação técnica se faz contra WCAG e PDF/UA.

## slide-11

Slide 11 de 36. As normas ABNT que se aplicam. Conferidas no acervo ABNT do MPF (Ministério Público Federal): 45 normas. Tabela com 6 linhas e 2 colunas. Normas ABNT aplicáveis ao material e o uso de cada uma

## slide-12

Slide 12 de 36. Três citações erradas que este projeto recusa. NBR 17060:2022 é sobre aplicativos móveis. Não é norma de documento. NBR 17225:2025 é sobre conteúdo web. Também não alcança um .pptx. NBR 9050 é ambiente construído: rampas e pisos, não arquivos. NBR 15290:2005 está superada pela edição de 2016. O auditor sinaliza cada uma delas como fundamentação inválida.

## slide-13

Slide 13 de 36. O que a ferramenta faz. Um catálogo explícito, um auditor que o executa e um construtor que o obedece.

## slide-14

Slide 14 de 36. O que foi construído. Catálogo. 118 regras auditáveis. em 15 camadas, de metadados a composição. Auditor. Camadas A a I, N e O. as demais saem como não verificadas. Construtor. Deck acessível por construção. recusa roteiro que sairia errado. Exportação. PDF/UA validado. contra a ISO 14289, no veraPDF.

## slide-15

Slide 15 de 36. As 15 camadas do catálogo. Cada regra tem identificador estável, severidade e critério de origem. E também: como detectar e como corrigir. As camadas A a I, N e O são automáticas; J a M dependem de mídia ou de pessoa. Descrição da figura. Lista vertical de quinze camadas identificadas pelas letras A a O, com o número de regras de cada uma. A, documento e metadados, 6 regras. B, estrutura semântica, 10. C, ordem de leitura, 6. D, texto alternativo, 11. E, cor e contraste, 10. F, tipografia e legibilidade, 10. G, tabelas, 6. H, hiperlinks, 4. I, mídia, movimento e interação, 9. J, Libras e público surdo, 9. K, público cego e audiodescrição, 5. L, exportação e PDF/UA, 7. M, confirmação humana, 6 itens. N, design e composição, 12. O, pacote e versões paralelas, 7. Somam 118. As camadas A a I, N e O são verificadas automaticamente; as camadas J a M dependem de mídia, do PDF ou de uma pessoa, e saem no relatório como não verificadas.

## slide-16

Slide 16 de 36. Anatomia de uma regra. Regra D05, severidade Erro, critério WCAG 1.1.1. Falha: alt text com resíduo 'Descrição gerada automaticamente'. Detecção: automática, por expressão regular sobre o atributo descr. Correção: reescrever com curadoria humana e apagar o aviso. Sem os cinco campos, uma regra é opinião. Com eles, é auditável.

## slide-17

Slide 17 de 36. O que o auditor vê e o nativo não. Uma amostra da diferença de cobertura. Tabela com 7 linhas e 3 colunas. Comparação entre a cobertura do verificador nativo e a deste projeto

## slide-18

Slide 18 de 36. Achados que só apareceram porque medimos. 3 de 8. cores da paleta Okabe-Ito passam em contraste. A paleta crua reprova no critério 1.4.11 sobre fundo claro. Amarelo dá 1,24:1 e laranja 2,11:1, contra o mínimo de 3:1. O PDF exportado saiu com idioma 'en', e não português. E com título vazio: o leitor anunciava o nome do arquivo. Nada disso estava na literatura. Apareceu ao medir.

## slide-19

Slide 19 de 36. Fluxo de trabalho. Do roteiro ao PDF validado, com um portão em cada estágio.

## slide-20

Slide 20 de 36. O pipeline em sete estágios. Cada estágio tem um portão que pode reprovar. A correção volta para o roteiro, nunca para o arquivo gerado. Descrição da figura. Sequência numerada de sete estágios. Um, roteiro declarativo em YAML, com um bloco por slide. Dois, diagramas gerados em HTML e convertidos em imagem, uma versão por paleta. Três, construção do arquivo, com placeholder, idioma, contraste e ordem de leitura já corretos. Quatro, modos de cor: um arquivo por modo, com o mesmo conteúdo nos três. Cinco, auditoria do pptx contra as camadas A a N, exigindo zero erros e zero avisos. Seis, exportação para PDF com marcas de estrutura. Sete, validação do PDF no veraPDF. Se um portão reprova, a correção volta para o estágio um.

## slide-21

Slide 21 de 36. Acessível por construção, não por remediação. O construtor recusa roteiro que geraria slide inacessível. Título repetido: o build para e diz em quais slides. Figura sem alt text ou sem descrição longa: o build para. Link escrito como 'clique aqui': o build para. Não existe a opção de gerar errado e consertar depois.

## slide-22

Slide 22 de 36. O simulador de leitura. Escreve o que um leitor de tela anunciaria, na ordem em que anunciaria. Torna a ordem de leitura visível para quem enxerga. Não exige instalar leitor de tela nenhum. É um modelo do comportamento, não o comportamento. Não substitui o teste real: K03 exige NVDA (NonVisual Desktop Access).

## slide-23

Slide 23 de 36. Dois eixos de separação. Paleta troca a cor e nada mais: o texto tem de ser idêntico. Perfil troca o registro do texto, para outro público. Paleta: padrão, alto contraste e daltônico-seguro. Perfil: completo, Libras como primeira língua e leitura fácil. Sete arquivos, todos gerados do mesmo roteiro.

## slide-24

Slide 24 de 36. Sete versões, sete públicos. Tabela com 6 linhas e 3 colunas. As sete versões entregues, o público de cada uma e o que muda

## slide-25

Slide 25 de 36. O que separa acesso de segregação. Nenhuma versão dá menos: toda mensagem-chave está em todas. Nenhuma versão dá mais: nada existe só num arquivo. Qualquer pessoa pode abrir qualquer versão. A versão completa carrega tudo, e nunca falta nada a ninguém. As condições viraram as regras O quatro a O sete, verificadas por máquina.

## slide-26

Slide 26 de 36. Como usar. A ferramenta é uma skill, e skill hoje é formato aberto.

## slide-27

Slide 27 de 36. Uma skill, muitos agentes. Agent Skills é especificação aberta, publicada em dezembro de 2025. Uma pasta com SKILL.md, scripts, references e assets. A mesma pasta roda em produtos concorrentes, sem adaptação. Descrição da figura. No centro, a estrutura de uma skill: o arquivo SKILL.md com metadados e instruções, mais as pastas opcionais scripts, references e assets. Ao redor, os produtos que leem esse mesmo formato: Claude Code, OpenAI Codex, Cursor, GitHub Copilot, VS Code, Gemini CLI, JetBrains Junie, Goose, OpenCode e mais de trinta outros. O formato foi criado pela Anthropic e liberado como especificação aberta, e foi adotado por produtos concorrentes em poucas semanas.

## slide-28

Slide 28 de 36. Instalação em três passos. Passo 1: clonar o repositório público. Passo 2: rodar instalar.ps1 no Windows, ou instalar.sh no Linux e macOS. Passo 3: arrastar um arquivo .pptx para cima de auditar.bat. O instalador cria um ambiente isolado e não toca no Python do sistema. Ferramentas de sistema só são instaladas se você confirmar. Repositório do projeto no GitHub.

## slide-29

Slide 29 de 36. Uso dentro do agente. Claude Code: copiar a pasta para ~/.claude/skills/. Codex e demais: copiar para ~/.agents/skills/, ou .agents/skills/ no repo. Depois disso, basta pedir em linguagem natural. Exemplo: 'audite esta apresentação e me diga o que corrigir'. O agente carrega o catálogo sob demanda e executa os scripts.

## slide-30

Slide 30 de 36. Como o agente entra no processo. Você entrega um texto ou uma apresentação que já tem. O agente lê a skill e sabe as regras, os limites e a ordem dos passos. Ele roteiriza, constrói as sete versões, audita e relata o que falhou. Quem decide o que cada público precisa continua sendo você. O portão é do pipeline, não do agente: com erro aberto, não há entrega.

## slide-31

Slide 31 de 36. O que a máquina fez, e o que não fez. Fez: cento e dezoito regras, o código e as sete versões. Fez: achou defeitos que passaram por três revisões humanas. Não fez: revisar a glosa de Libras, que erra concordância espacial. Não fez: escolher o que cada público precisa saber. Não fez: substituir o teste com pessoas com deficiência.

## slide-32

Slide 32 de 36. O que a ferramenta não faz. Não escreve o conteúdo por você: o roteiro é humano. Não julga se o alt text está correto, só se ele é plausível. Não substitui teste com pessoa com deficiência. Não avalia contraste de texto sobre foto: manda para o olho humano. Não roda o verificador nativo: não existe API para isso.

## slide-33

Slide 33 de 36. Rigor: como sei que a ferramenta funciona. Um auditor não testado é uma opinião com sotaque técnico.

## slide-34

Slide 34 de 36. Testado nos dois sentidos. Enxerga o que foi plantado? Um deck com defeitos plantados, cada um com gabarito. Resultado: todos detectados. Regra do gabarito não acusada é defeito do auditor. Cala diante do que está certo? Um deck correto de propósito. Resultado: zero falsos positivos. Auditor que acusa tudo é tão inútil quanto o que não acusa nada.

## slide-35

Slide 35 de 36. Ausência de evidência não é conformidade.. O princípio que impede a ferramenta de virar um selo.

## slide-36

Slide 36 de 36. Esta apresentação foi auditada por si mesma. Gerada por código a partir do roteiro que a acompanha. Sete versões auditadas: zero erros e zero avisos em todas. Exportada em PDF com marcas de estrutura e identificador PDF/UA. Validada no veraPDF contra a ISO 14289, sem erros. O relatório de auditoria acompanha a entrega. Repositório com o código, o catálogo e este roteiro.
