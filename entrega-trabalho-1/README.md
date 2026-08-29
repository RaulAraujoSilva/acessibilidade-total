# Trabalho 1 — TCE 00191, Documentos Acessíveis

**Acessibilidade Total: uma ferramenta para produzir e auditar apresentações acessíveis**
Raul Araujo Silva · Doutorado em Engenharia de Produção · UFF

Esta pasta é a **entrega da disciplina**. Ela guarda tudo o que é leve — relatórios, transcrições,
figuras e o PDF. Os sete arquivos de apresentação e as faixas de mídia pesam 208 MB juntos e por
isso ficam nos **[Releases](https://github.com/RaulAraujoSilva/acessibilidade-total/releases/tag/trabalho-1)**,
não no histórico do repositório.

Comece pelo **[`LEIA-ME.md`](LEIA-ME.md)**: ele diz qual arquivo abrir, o que cada versão carrega
e — principalmente — o que este material **não** entrega.

## O que está aqui

| Arquivo | O que é |
|---|---|
| [`LEIA-ME.md`](LEIA-ME.md) | Guia da entrega: qual arquivo abrir, o que cada um carrega, o que falta |
| [`RESUMO-DA-SUBMISSAO.docx`](RESUMO-DA-SUBMISSAO.docx) | Resumo de duas páginas: a hipótese, as sete versões e a ferramenta |
| [`Acessibilidade-Total-uma-ferramenta-para-produz-padrao.pdf`](Acessibilidade-Total-uma-ferramenta-para-produz-padrao.pdf) | PDF marcado, com identificador PDF/UA-1 |
| [`transcricao.docx`](transcricao.docx) | Transcrição linear, com estilos de título reais |
| [`leitura-simulada.md`](leitura-simulada.md) | O que um leitor de tela anunciaria, na ordem em que anunciaria |
| `auditoria-pptx-<versão>.md` | Camadas A a N de cada arquivo, **como entregue** — com a mídia dentro |
| [`auditoria-pacote.md`](auditoria-pacote.md) | Camada O: paridade entre paletas e equivalência entre versões de público |
| [`auditoria-pdf.md`](auditoria-pdf.md) | Camada L: veraPDF contra a ISO 14289 |
| [`audiodescricao/transcricao-audiodescricao.md`](audiodescricao/transcricao-audiodescricao.md) | O texto das 36 faixas narradas |
| [`libras/manifesto.json`](libras/manifesto.json) | Uma linha por slide: o texto sinalizado, o arquivo e a taxa de quadros medida |
| `figuras/` | Os quatro diagramas, cada um nas três paletas |

## O que está nos Releases

Os arquivos que carregam a mídia dentro. Baixe **um** deles — não todos.

| Arquivo | Para quem | Tamanho |
|---|---|---|
| `…-padrao.pptx` | uso geral — **é o arquivo principal** | 15,9 MB |
| `…-alto-contraste.pptx` | baixa visão, ou projeção em sala clara | 15,8 MB |
| `…-daltonico-seguro.pptx` | discromatopsia | 15,9 MB |
| `…-leitura-facil-padrao.pptx` | deficiência cognitiva, TDAH | 15,9 MB |
| `…-libras-padrao.pptx` | Libras como primeira língua | 33,2 MB |
| `…-libras-alto-contraste.pptx` | Libras como primeira língua e baixa visão | 33,1 MB |
| `…-libras-daltonico-seguro.pptx` | Libras como primeira língua e discromatopsia | 33,2 MB |
| `midia-solta.zip` | quem prefere as faixas fora do arquivo | 43 MB |

Os quatro primeiros carregam **36 faixas de audiodescrição**; os três de Libras carregam
**36 vídeos de janela de Libras**, a 25 quadros por segundo. O recurso segue o sentido que ele
serve — a explicação está no `LEIA-ME.md`.

## Como este material fecha

| | |
|---|---|
| Os 7 arquivos, camadas A a N | **0 erro, 0 aviso** |
| Pacote, camada O (paridade entre versões) | **0 erro, 0 aviso** |
| PDF no veraPDF, contra a ISO 14289 | **0 erro, 0 aviso** |

O que sobra está na lista de **não verificados** de cada relatório — e não verificado não é
aprovado. A camada M, que só uma pessoa cumpre, segue aberta e está declarada no `LEIA-ME.md`.

## A ferramenta que produziu tudo isto

O código está na raiz deste repositório, sob licença MIT. É uma skill no formato aberto
**Agent Skills**: uma pasta com instruções, scripts e referências que agentes de código carregam
e executam.

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

O roteiro desta apresentação está em [`exemplos/apresentacao/`](../exemplos/apresentacao/), e o
catálogo das 118 regras em 15 camadas em
[`references/02-catalogo-auditoria.md`](../references/02-catalogo-auditoria.md).
