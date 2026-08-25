# 02 — Catálogo de auditoria

> **É isto que o auditor procura.** Cada regra tem ID estável, severidade, critério de origem,
> o que caracteriza a falha, como detectá-la e como corrigi-la.
>
> **Severidade:** `E` Erro (bloqueia a entrega) · `A` Aviso (corrigir salvo justificativa
> escrita) · `D` Dica (melhoria).
>
> **Detecção:** `AUTO` o script decide sozinho · `SEMI` o script levanta suspeita e um humano
> julga · `HUM` só humano.
>
> Regra de ouro do auditor: **ausência de evidência não é conformidade.** Item que não pôde ser
> verificado entra no relatório como *não verificado*, nunca como aprovado.

---

## A — Documento e metadados

| ID | Sev | Critério | O que caracteriza a falha | Detecção | Correção |
|---|---|---|---|---|---|
| A01 | E | 2.4.2 | `dc:title` vazio, ausente ou igual ao nome do arquivo | AUTO — `docProps/core.xml` | Título descritivo em Arquivo › Informações |
| A02 | E | 3.1.1 | `dc:language` ausente ou diferente do idioma real | AUTO | `core_properties.language = "pt-BR"` |
| A03 | E | 3.1.2 | Runs em PT-BR marcados `lang="en-US"` (padrão de instalação em inglês) | AUTO — `a:rPr/@lang` de todo `a:r` | Revisão › Idioma › Definir idioma de revisão, em todos os slides |
| A04 | A | — | Autor ausente ou "Usuário do Windows" | AUTO | Preencher autor |
| A05 | A | — | Nome de arquivo não descritivo (`Apresentação1.pptx`) | AUTO | Renomear |
| A06 | D | — | Tamanho de slide fora de 16:9 sem motivo | AUTO | Design › Tamanho do Slide |

## B — Estrutura semântica

| ID | Sev | Critério | O que caracteriza a falha | Detecção | Correção |
|---|---|---|---|---|---|
| B01 | E | 1.3.1, 2.4.2 | Slide sem *placeholder* de título (`ph type="title"` ou `ctrTitle`) | AUTO | Layout com título; nunca caixa de texto fazendo as vezes |
| B02 | E | 2.4.2 | Título presente mas vazio ou só com espaços | AUTO | Preencher |
| B03 | E | — | Dois slides com o mesmo título | AUTO | Sufixar: `Resultados (1 de 3)` |
| B04 | A | 2.4.2 | Slide de imagem cheia sem título nenhum | AUTO+HUM | Título no *placeholder*, oculto no Painel de Seleção ou movido para fora da tela — **nunca apagado** |
| B05 | E | 1.3.1 | Conteúdo em caixa de texto solta (`p:sp` sem `ph`) em vez de *placeholder* | AUTO | Usar layout do Slide Master; criar layout novo se preciso |
| B06 | A | 1.3.1 | Slide baseado no layout "Em Branco" | AUTO | Trocar por layout semântico |
| B07 | A | — | Seção com nome padrão (`Seção Padrão`, `Seção 3`) | AUTO | Renomear com sentido |
| B08 | D | — | Nomes de seção repetidos | AUTO | Diferenciar |
| B09 | A | 1.3.1 | Lista feita com hífen ou asterisco digitado em vez de marcador nativo | AUTO — parágrafo iniciado por hífen/asterisco com `a:buNone` | Aplicar marcador ou numeração nativa |
| B10 | A | 1.4.5 | Texto entregue como imagem (print de tabela, WordArt de conteúdo) | SEMI | Recriar como texto real |

## C — Ordem de leitura

| ID | Sev | Critério | O que caracteriza a falha | Detecção | Correção |
|---|---|---|---|---|---|
| C01 | E | 1.3.2 | Título não é o primeiro elemento na ordem de leitura | AUTO — posição no `p:spTree` | Reordenar no Painel de Ordem de Leitura |
| C02 | E | 1.3.2 | Ordem do `spTree` não acompanha o fluxo visual (cima para baixo, esquerda para direita) | AUTO, com tolerância de faixa horizontal | Reordenar |
| C03 | E | 1.1.1 | Objeto puramente estético participando da ordem de leitura | AUTO — sem `adec:decorative` e sem `descr` | Marcar como decorativo |
| C04 | A | 1.3.2 | Diagrama com mais de 5 formas soltas, cada uma anunciada isoladamente | AUTO | Agrupar (Ctrl+G) e pôr o alt text **no grupo** |
| C05 | A | — | Objetos com nome automático (`Rectangle 47`) | AUTO | Renomear no Painel de Seleção |
| C06 | A | 1.3.2 | Objeto fora da área do slide que ainda é lido, sem ser título oculto intencional | AUTO | Excluir ou marcar decorativo |

> **Armadilha do eixo Z.** Corrigir a ordem de leitura *move a camada visual*: um retângulo
> escuro atrás de texto branco, se reordenado, passa a encobrir o texto. A saída correta nunca é
> reordenar o retângulo — é **marcá-lo como decorativo**, o que o retira da ordem de leitura e o
> mantém na camada visual onde estava.

## D — Texto alternativo

| ID | Sev | Critério | O que caracteriza a falha | Detecção | Correção |
|---|---|---|---|---|---|
| D01 | E | 1.1.1 | Imagem, ícone, gráfico, SmartArt, grupo ou mídia sem alt text e sem marca de decorativo | AUTO | Descrever ou marcar decorativo |
| D02 | E | 1.1.1 | `descr` contendo apenas espaços | AUTO | Descrever |
| D03 | E | 1.1.1 | `descr` é nome de arquivo (`grafico1.png`) ou rótulo genérico (`imagem`, `figura`) | AUTO — regex de extensão e lista de genéricos | Reescrever |
| D04 | A | 1.1.1 | Começa com "Imagem de", "Foto de", "Gráfico de" — o leitor de tela já anuncia o tipo | AUTO | Remover o prefixo |
| D05 | E | 1.1.1 | Resíduo de IA: "Descrição gerada automaticamente", "O conteúdo gerado por IA pode estar incorreto" | AUTO | Reescrever com curadoria humana e apagar o aviso |
| D06 | A | 1.1.1 | `descr` acima de ~150 caracteres (alguns leitores truncam) | AUTO | Encurtar e mandar o detalhe para as Notas |
| D07 | E | 1.1.1 | Figura densa (gráfico, diagrama, infográfico) sem **descrição longa** nas Notas | SEMI | Escrever a descrição longa nas Anotações do orador |
| D08 | A | 3.1.1 | Alt text em PT-BR sem acentuação, ou em idioma diferente do slide | SEMI | Reescrever |
| D09 | A | 1.4.5 | Texto contido dentro da imagem não reproduzido no alt nem nas Notas | SEMI (OCR opcional) | Transcrever o texto |
| D10 | A | 1.1.1 | Vídeo ou áudio sem `descr` | AUTO | Descrever o objeto |
| D11 | E | 1.1.1 | Objeto marcado como decorativo **e** com `descr` preenchido — contradição semântica | AUTO | Escolher um dos dois |

> Um alt text bom responde **por que esta imagem está neste slide**, não o que ela contém.
> "Gráfico de linhas azul e branco" descreve pixels; "queda de 32% na receita do terceiro
> trimestre" descreve informação.

## E — Cor e contraste

| ID | Sev | Critério | O que caracteriza a falha | Detecção | Correção |
|---|---|---|---|---|---|
| E01 | E | 1.4.3 | Texto normal com contraste abaixo de 4,5:1 | AUTO — resolve tema e herança | Ajustar cor |
| E02 | E | 1.4.3 | Texto grande (18pt ou mais, ou 14pt negrito ou mais) abaixo de 3:1 | AUTO | Ajustar cor |
| E03 | D | 1.4.6 | Abaixo de 7:1 (meta AAA para corpo de texto) | AUTO | Escurecer ou clarear |
| E04 | A | 1.4.11 | Barra, linha, ícone, borda ou indicador de foco abaixo de 3:1 contra o fundo | AUTO | Usar a variante `marca_min_3_1` da paleta, ou contornar |
| E05 | E | 1.4.1 | Informação transmitida só por cor (legenda de gráfico, "itens em vermelho") | SEMI+HUM | Acrescentar forma, hachura ou rótulo direto |
| E06 | A | 1.4.1 | Conteúdo perde sentido em escala de cinza | SEMI (converte e compara) + HUM | Diferenciar por luminância |
| E07 | A | 1.4.1 | Séries indistinguíveis sob protanopia, deuteranopia ou tritanopia | SEMI (simulação e distância de cor) | Trocar pela paleta cega-segura |
| E08 | A | — | Fundo branco puro com texto preto puro (*glare*, síndrome de Irlen) | AUTO | Fundo `#FAF7F2`, texto `#1A1A1A` |
| E09 | A | 1.4.3 | Texto sobre foto ou gradiente — **o verificador nativo não detecta este caso** | SEMI (amostra a região) + HUM | Faixa sólida atrás do texto, ou sobreposição escurecida |
| E10 | A | 1.4.1 | Hiperlink distinguível apenas pela cor | AUTO | Manter o sublinhado |

> **A paleta Okabe-Ito crua reprova em 1.4.11 sobre fundo claro.** Contrastes medidos contra
> `#FAF7F2`: amarelo 1,24 · laranja 2,11 · azul-céu 2,16 · cinza 2,67 · roxo 2,86. Só verde-azulado
> (3,20), vermelhão (3,62) e azul (4,85) passam. Use as variantes escurecidas de
> `assets/paleta-okabe-ito.json` para preenchimento e **nunca a cor base como cor de texto**.

## F — Tipografia e legibilidade

| ID | Sev | Critério | O que caracteriza a falha | Detecção | Correção |
|---|---|---|---|---|---|
| F01 | A | — | Fonte com serifa ou decorativa no corpo do texto | AUTO — conjunto seguro: Arial, Calibri, Verdana, Tahoma, Segoe UI, Open Sans, Atkinson Hyperlegible | Trocar |
| F02 | E | 1.4.4 | Corpo de texto abaixo de 18pt (`sz` menor que 1800) | AUTO, com herança de layout e master | Aumentar; alvo 24pt ou mais |
| F03 | A | — | Título abaixo de 32pt | AUTO | Aumentar |
| F04 | E | — | Parágrafo justificado (`algn="just"`) — cria "rios de branco" | AUTO | Alinhar à esquerda |
| F05 | A | — | Entrelinha menor que 1,5 (`a:lnSpc/a:spcPct` abaixo de 150000) | AUTO | Ajustar |
| F06 | A | — | Itálico em bloco, sublinhado fora de link, ou frase inteira em CAIXA ALTA | AUTO | Usar negrito para destaque |
| F07 | A | — | Mais de 6 marcadores por slide, ou linha acima de ~70 caracteres | AUTO | Dividir o slide |
| F08 | D | — | Fonte não incorporada e fora do conjunto seguro | AUTO | Incorporar fontes ao salvar |

## G — Tabelas

| ID | Sev | Critério | O que caracteriza a falha | Detecção | Correção |
|---|---|---|---|---|---|
| G01 | E | 1.3.1 | Tabela sem linha de cabeçalho (`a:tblPr/@firstRow` diferente de 1) | AUTO | Design de Tabela › Linha de Cabeçalho |
| G02 | A | 1.3.1 | Tabela com rótulo de linha sem `firstCol` marcado | SEMI | Marcar Primeira Coluna |
| G03 | E | 1.3.1 | Células mescladas ou divididas (`gridSpan`, `rowSpan`, `vMerge`, `hMerge`) | AUTO | Desfazer a mesclagem; se for indispensável, quebrar em tabelas simples |
| G04 | A | 1.3.1 | Linha ou coluna inteiramente vazia usada como espaçador | AUTO | Espaçar pelas margens da célula |
| G05 | A | 1.1.1 | Tabela sem alt text ou sem resumo do que ela mostra | AUTO | Descrever |
| G06 | A | 1.3.1 | Tabela usada como recurso de layout (imagens lado a lado, coluna única) | SEMI | Substituir por *placeholders* de conteúdo |

> Uma célula mesclada corrompe a contagem de colunas do leitor de tela e desalinha a grade
> inteira a partir dali. Tabela que "precisa" de mesclagem é tabela complexa demais para um
> slide.

## H — Hiperlinks

| ID | Sev | Critério | O que caracteriza a falha | Detecção | Correção |
|---|---|---|---|---|---|
| H01 | A | 2.4.4 | Texto do link é a URL crua | AUTO | Texto descritivo: "Diretrizes WCAG 2.2 do W3C" |
| H02 | A | 2.4.4 | "clique aqui", "saiba mais", "leia mais", "aqui" | AUTO | Reescrever com o destino no próprio texto |
| H03 | A | 3.2.4 | Mesmo texto de link apontando para destinos diferentes | AUTO | Diferenciar os textos |
| H04 | D | 2.4.4 | Link ambíguo sem Dica de Tela | SEMI | Preencher a Dica de Tela |

## I — Mídia, movimento e interação

| ID | Sev | Critério | O que caracteriza a falha | Detecção | Correção |
|---|---|---|---|---|---|
| I01 | E | 1.2.2 | Vídeo sem legenda fechada (WebVTT) | AUTO — parte de legenda no pacote | Inserir Legendas |
| I02 | E | 1.2.1 | Áudio sem transcrição | SEMI | Transcrição nas Notas ou em anexo |
| I03 | A | 1.2.3, 1.2.5 | Vídeo sem audiodescrição nem descrição textual equivalente | SEMI | Faixa de AD ou descrição |
| I04 | A | 2.2.2 | Mídia em autoplay e loop por mais de 5 segundos sem controle de parada | AUTO — `p:mediaNode` com loop e autoplay | Remover o autoplay ou dar controle |
| I05 | E | 2.3.1 | Piscada mais de 3 vezes por segundo (transição "Flash", GIF piscante) | SEMI+HUM | Remover |
| I06 | A | — | Animações e transições fora do conjunto sóbrio (fade, appear) | AUTO — inventário de `p:animEffect` e `p:transition` | Simplificar |
| I07 | A | 2.5.8 | Alvo de clique do hub menor que 24×24 px CSS (228600 EMU) | AUTO | Ampliar o botão |
| I08 | A | 2.4.11, 2.4.13 | Hiperlink de navegação coberto por outro objeto, ou sem indicador de foco visível | SEMI+HUM | Reposicionar; indicador com 3:1 |
| I09 | A | 2.5.7 | Interação que depende de arrastar | HUM | Oferecer alternativa por clique único |

## J — Libras e público surdo

| ID | Sev | Critério | O que caracteriza a falha | Detecção | Correção |
|---|---|---|---|---|---|
| J01 | E | LBI · Lei 10.436/2002 · Dec. 5.626/2005 | Nenhuma via em Libras para o conteúdo principal | AUTO (presença de mídia) + HUM | Janela de Libras nos slides-chave ou vídeo-resumo |
| J02 | A | ABNT NBR 15290 | Janela de Libras com tamanho, posição ou contraste fora dos parâmetros da norma | HUM | Ajustar conforme a norma — **conferir os valores no texto da NBR 15290 antes de auditar; não usar número de memória** |
| J03 | A | — | Sem roteiro em SRT disponível junto ao material | AUTO | Gerar o SRT |
| J04 | A | — | Legendas ao vivo não pré-configuradas no arquivo | AUTO — `p:showPr` / configuração de legenda | Apresentação de Slides › Configurações de Legenda, idioma falado e exibido |
| J05 | D | — | Glosa gerada automaticamente e não revisada | HUM | Revisão por intérprete ou pessoa surda |

## K — Público cego e audiodescrição

| ID | Sev | Critério | O que caracteriza a falha | Detecção | Correção |
|---|---|---|---|---|---|
| K01 | E | 1.1.1 | Figura complexa sem descrição longa nas Notas | SEMI | Escrever a descrição longa |
| K02 | A | ABNT NBR 16452 | Sem faixa de audiodescrição e sem a transcrição dela | AUTO (presença) + HUM (qualidade) | Gerar a faixa e a transcrição |
| K03 | E | 1.3.2 | Ordem de leitura nunca testada com leitor de tela real | HUM (com evidência anexa) | Percorrer com NVDA e anexar o log de fala |
| K04 | A | — | Sem transcrição linear do deck em documento acessível | AUTO | Gerar o `.docx` com estilos de título reais |
| K05 | A | — | Notas do orador perdidas na exportação para PDF | AUTO | Exportar Páginas de Anotações à parte |

## L — Exportação e PDF/UA

| ID | Sev | Critério | O que caracteriza a falha | Detecção | Correção |
|---|---|---|---|---|---|
| L01 | E | ISO 14289 | PDF gerado por "Imprimir para PDF" — destrói todas as tags | AUTO (ausência de estrutura) | Reexportar com marcas de estrutura |
| L02 | E | 3.1.1 | PDF sem `/Lang` no catálogo | AUTO | Definir idioma nas propriedades |
| L03 | E | 2.4.2 | PDF sem `/Title`, ou sem `DisplayDocTitle` ativo | AUTO | Propriedades do documento |
| L04 | E | 1.3.1 | Árvore de tags sem H1..Hn, ou com hierarquia quebrada | AUTO (veraPDF/PAC) + HUM | Corrigir no Acrobat Pro |
| L05 | E | 1.3.1 | `TH` sem `/Scope` de linha ou coluna | AUTO | Table Editor do Acrobat Pro |
| L06 | E | 1.1.1 | Objeto decorativo que virou conteúdo em vez de `/Artifact` | AUTO | Remarcar |
| L07 | E | ISO 14289 | PAC 2024 ou veraPDF acusando erro de PDF/UA | AUTO | Remediar e revalidar |

## M — Confirmação humana (nenhuma entrega fecha sem esta camada)

| ID | O que fazer | Evidência que vai ao relatório |
|---|---|---|
| M01 | Rodar o Verificador de Acessibilidade nativo (Revisão › Verificar Acessibilidade) | Captura de tela do painel sem Erros nem Avisos |
| M02 | Percorrer o deck com NVDA: F6 entre painéis, Tab dentro do slide, Ctrl+Shift+S nas notas | Log do add-on Speech Logger |
| M03 | Ativar a escala de cinza do Windows e reler o deck | Captura de 3 slides críticos |
| M04 | Simular protanopia, deuteranopia e tritanopia (Color Oracle) | Captura por tipo |
| M05 | Ler, um a um, todos os alt text e descrições longas | Lista assinada de alt text revisados |
| M06 | Sempre que possível, submeter a uma pessoa com deficiência | Registro do retorno |

> M06 vale mais que M01 a M05 somados. Conformidade técnica é o piso, não a prova.

---

## Como o relatório deve sair

Para cada regra: `ID · severidade · veredito (conforme / não conforme / não verificado) · onde
(slide e objeto) · evidência`. O resumo traz a contagem por severidade e a **lista explícita do
que não foi verificado**. Entrega só é declarada conforme com zero `E` e zero `A` em aberto, e
com a camada M inteira registrada.
