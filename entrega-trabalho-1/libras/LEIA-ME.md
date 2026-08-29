# Camada de Libras — o que foi entregue

**Arquivo de origem:** `Acessibilidade-Total-uma-ferramenta-para-produz.pptx`
**Blocos de conteúdo:** 28 · **duração estimada da narração:** 7 min 59 s

## Nível alcançado: 1 de 3 — vídeo gerado localmente, sem login gov.br

| Arquivo | O que é |
|---|---|
| `janela-libras-resumo.mp4` | Janela de Libras do resumo do trabalho · 312 × 452 px · 2 min 36 s |
| `roteiro-libras.srt` | Legenda cronometrada do material inteiro, pronta para o portal VLibras Vídeo |

A regra **J01 está atendida em parte**: existe janela de Libras, e ela cobre o
resumo do trabalho, não os 85 slides. O `.srt` continua sendo o insumo para
cobrir o restante pelo portal.

## Como o vídeo foi feito

`scripts/libras_caminho_a.py` sobe uma página local por HTTP, embute o **VLibras
Widget** oficial (gov.br), seleciona o texto com arraste real de mouse — que é o
que dispara a tradução — e captura a janela do avatar quadro a quadro. Sem conta
gov.br, sem Docker, sem envio do material para fora da máquina.

Três detalhes que custaram tempo e ficam registrados, porque quem repetir vai
esbarrar neles:

1. A página **precisa** ser servida por HTTP. Montada em memória
   (`set_content`), o botão de acesso do widget nunca fica clicável — foi essa,
   e só essa, a causa da falha da primeira tentativa.
2. O elemento `[vw-access-button]` tem **altura zero**; é um marcador. O botão
   visível é desenhado pelo plugin na borda direita da janela.
3. `window.getSelection()` **não** dispara a tradução: o plugin escuta eventos
   reais de mouse.

## Limites conhecidos deste vídeo

- **A glosa é automática e não passou por intérprete.** Ela erra concordância
  espacial e classificadores (regra J05). Para publicação, revise com
  intérprete de Libras ou refaça pelo portal.
- **A captura é entrecortada.** Cada quadro custa cerca de 0,4 s, o que dá
  ~2,5 quadros por segundo. O vídeo sai no tempo real — o `ffmpeg` monta no fps
  **medido**, não no pedido —, mas a sinalização fica com falhas de fluidez.
- **A janela vem sozinha, em arquivo separado.** Compor sobre o slide é a etapa
  seguinte, e é onde valem os parâmetros da ABNT NBR 15290:2016, item 7.1.3:
  altura de ao menos metade da tela e largura de ao menos um quarto — com a
  ressalva de que aplicá-los a um slide é analogia, porque a norma regula
  televisão.

## Os outros dois caminhos, se este não bastar

**Nível 2 — portal VLibras Vídeo (recomendado para publicar).**
Abra <https://video.vlibras.gov.br/>, entre com a conta gov.br, envie um vídeo da
apresentação junto com `roteiro-libras.srt`. Limites: `.mp4` até 500 MB e `.srt`
até 600 palavras.

**Nível 1 pelo renderizador Unity (alternativa local mais fiel).**
O binário `VLibras-Video.x86_64` já está na imagem
`vlibras/translator-video:3.1.0`, com Xvfb e ffmpeg, e aceita chamada direta —
sem RabbitMQ nem MongoDB. A chamada está no cabeçalho de
`scripts/gen_libras.py`. O que falta são os *bundles* de sinais
(`VIDEOMAKER_BUNDLES_DIR`), servidos pelo serviço `dicionario`. Quem retomar
começa por aí, não do zero.
