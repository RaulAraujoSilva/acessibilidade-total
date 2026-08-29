# Trabalho 1 — TCE 00191, Documentos Acessíveis

**Acessibilidade Total: uma ferramenta para produzir e auditar apresentações acessíveis**
Raul Araujo Silva · Doutorado em Engenharia de Produção · UFF

---

## Qual arquivo abrir

Sete arquivos. Os três primeiros têm **exatamente o mesmo texto** e mudam só a paleta; os dois
últimos têm o mesmo **conteúdo** num registro diferente. Qualquer pessoa pode abrir qualquer um.

| Abra este | Se você | O que muda |
|---|---|---|
| `…-padrao.pptx` | não tem preferência — **é o arquivo principal** | contraste 16,3:1 |
| `…-alto-contraste.pptx` | tem baixa visão, ou vai projetar em sala clara | contraste 21:1 |
| `…-daltonico-seguro.pptx` | tem discromatopsia | matizes separados, 15,9:1 |
| `…-libras-*.pptx` (três paletas) | tem **Libras como primeira língua** | pouco texto e **janela de Libras em cada slide**, a 25 fps |
| `…-leitura-facil-padrao.pptx` | tem deficiência cognitiva, TDAH, ou quer o essencial | **uma ideia por slide**, texto maior |

A versão em Libras sai nas **três paletas** porque quem não ouve depende inteiramente do canal
visual — contraste ali não é conforto, é acesso.

### Por que existem versões por público, se o princípio é "um artefato para todos"

Porque o princípio foi escrito contra outra coisa: contra entregar ao deficiente uma versão
**pior**. Uma versão com Libras como primeira língua não dá menos — dá o mesmo conteúdo na
**primeira língua** do interlocutor. É o modelo que a **LBI 13.146/2015, art. 28, IV** consagra,
com as palavras *"Libras como primeira língua"* e *"língua portuguesa como segunda língua"* no
texto da lei.

E isso não é promessa: `auditoria-pacote.md` verifica, slide a slide, que **toda mensagem-chave
da versão base aparece em todas as versões** (regra O04) e que **nenhuma versão acrescenta
conteúdo que as outras não têm** (O05). Reduzir texto não pode virar omitir conteúdo.

## Onde está cada recurso

**O recurso segue o sentido que ele serve.** A audiodescrição atende quem não enxerga; a janela
de Libras atende quem tem Libras como primeira língua. Exigir todo recurso em toda versão não
seria paridade — seria peso morto, e ainda embaralharia o que cada arquivo de fato oferece.

Por isso **os arquivos sem Libras não têm Libras nenhuma**. Havia antes uma janela avulsa na capa
dos demais, como "porta de entrada": ela não servia a quem precisa de Libras — num deck em que os
outros 35 slides não a têm, uma janela isolada é selo, não acesso. Quem precisa da versão em
Libras a encontra aqui e no slide de acessibilidade, que a nomeiam.

| Recurso | Serve quem | Em quais arquivos |
|---|---|---|
| **Audiodescrição** em cada um dos 36 slides | não enxerga | `padrao`, `alto-contraste`, `daltonico-seguro`, `leitura-facil` |
| **Janela de Libras** em cada um dos 36 slides | Libras como primeira língua | **só** os três `libras` |
| Transcrição linear e faixas soltas | linha braille, leitura sequencial | o pacote inteiro |
| Transcrição linear | `transcricao.docx`, com estilos de título reais |
| Descrição longa das figuras | nas Anotações do orador, slide a slide |
| PDF marcado | `…-padrao.pdf`, com identificador PDF/UA-1 |

## Os relatórios

Todos trazem **data, hora e o commit** que os gerou, no cabeçalho. Um relatório sem data não é
evidência: não dá para saber se ele descreve o arquivo que está na pasta ou um anterior.

| Arquivo | O que é |
|---|---|
| `auditoria-pptx-<versão>.md` | Camadas A a N de cada arquivo, **como entregue** — com a mídia dentro |
| `auditoria-pacote.md` | Camada O: paridade entre paletas e equivalência entre versões de público |
| `auditoria-pdf.md` | Camada L: veraPDF contra a ISO 14289 |
| `leitura-simulada.md` | O que um leitor de tela anunciaria, na ordem em que anunciaria |
| `libras/slides/manifesto.json` | Uma linha por slide: o texto sinalizado, o arquivo e a **taxa de quadros medida** |

**Como fecharam:** os sete decks em **0 erro e 0 aviso**; o pacote (camada O) em **0 erro e
0 aviso**; o PDF em **0 erro e 0 aviso** no veraPDF, com 36 marcas `/Slide` e identificador
PDF/UA-1. O que sobra em cada relatório está na lista de **não verificados** — e não verificado
não é aprovado.

Nos relatórios dos `.pptx`, as regras **L01 e L07** aparecem como não verificadas porque aquele
auditor lê o `.pptx`, não o PDF. Quem responde por elas é o `auditoria-pdf.md`, e lá as duas
estão cumpridas.

## O que este material entrega

- Texto alternativo em toda figura, e descrição longa nas Anotações.
- Ordem de leitura conferida, com o título sempre em primeiro.
- Contraste medido, não estimado; paleta cega-segura com variantes calculadas.
- Tabelas com linha de cabeçalho, sem célula mesclada, com cor explícita.
- Audiodescrição e Libras **dentro** do arquivo, sem reprodução automática.
- Janela de Libras a **25 quadros por segundo**, medidos arquivo a arquivo. Não há mínimo
  normativo na NBR 15290; o número vem da **ITU-T H.Sup1** (≥25 fps), do renderizador oficial do
  VLibras (`--framerate 24`) e da literatura empírica, que mostra perda de compreensão abaixo de
  10 fps.
- Composição verificada: proporção, margem, faixa de rodapé, sobreposição, grade, transbordo.

## O que este material NÃO entrega

Está aqui porque uma declaração de acessibilidade que só lista acertos é propaganda.

- **Libras revisada por intérprete.** A glosa é automática e erra concordância espacial e
  classificadores. É insumo, não tradução fechada (regra J05).
- **Redação dos perfis revisada.** As mensagens-chave são um primeiro corte. Reduzir texto sem
  perder mensagem é trabalho de redação, e ele merece uma segunda leitura humana.
- **Leitura fácil nas três paletas.** Ela sai só no modo padrão. A versão em Libras sai nas três,
  porque quem não ouve depende inteiramente do canal visual; a de leitura fácil não tem esse
  argumento, e quem precisar de contraste tem as três paletas da versão completa.
  `--perfis-todos-os-modos` gera todas.
- **PDF nos três modos.** Só o padrão foi exportado (`--pdf-todos-os-modos` gera os três).
- **Legendas ao vivo.** Não são propriedade do arquivo: são configuração da máquina de quem
  apresenta. O catálogo trata como instrução, não como conformidade auditável.
- **Leitura por pessoa com deficiência.** É o teste que vale mais que todos os outros, e não
  foi feito.

### O tamanho, dito com todas as letras

O pacote tem **209 MB**. Os três arquivos em Libras pesam **33,2 MB cada**, porque carregam os 36
vídeos; os quatro demais pesam **15,9 MB**, porque carregam as 36 faixas de áudio. Isso é o preço
de a mídia estar **dentro** do arquivo em vez de numa pasta que ninguém abre — e é uma troca
deliberada, não um descuido. Quem precisar de arquivos leves gera sem `--com-audio` e sem
`--libras-por-slide`: os decks caem para menos de 1 MB, e a mídia continua no pacote, em
`audiodescricao/` e `libras/slides/`.

## Pendências da camada M — o que nenhum script substitui

- [ ] **Verificador nativo do PowerPoint nos sete arquivos como estão agora.** Ele foi rodado em
      26/08/2026, e o que apontou virou a regra **N11** — a faixa do rodapé e o filete de acento
      foram para o Slide Master. Mas isso foi **antes** de a mídia entrar: 36 objetos de áudio ou
      de vídeo por arquivo mudam a ordem de leitura, e a conferência precisa ser refeita.
- [ ] Percurso com NVDA (NonVisual Desktop Access) e Speech Logger, com o log anexado
- [ ] Escala de cinza do Windows (`Win+Ctrl+C`) e simulação de daltonismo (Color Oracle)
- [ ] Conferência no PAC, além do veraPDF: são perguntas diferentes
- [ ] Leitura de todo o texto alternativo, um a um
- [ ] Revisão da glosa de Libras por intérprete, e da redação dos dois perfis

## Como reproduzir — inclusive a partir do seu próprio material

```bash
git clone https://github.com/RaulAraujoSilva/acessibilidade-total
cd acessibilidade-total && ./instalar.ps1

# de uma apresentação que você já tem, ou de um texto:
python scripts/importar.py sua-apresentacao.pptx -o meu-material/

# e então o pipeline inteiro:
python scripts/montar_tudo.py meu-material/ -o entrega/ \
    --perfis completo,libras,leitura_facil \
    --libras-por-slide --caminho-libras video \
    --com-audio entrega/audiodescricao
```

O código, o catálogo das 118 regras em 15 camadas e o roteiro desta apresentação estão em
https://github.com/RaulAraujoSilva/acessibilidade-total sob licença MIT.
