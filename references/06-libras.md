# 06 — Libras

> Libras é **língua**, não legenda. Um deck com legenda em português não está acessível a quem
> tem o português como segunda língua e a Libras como primeira. Legenda ao vivo e janela de
> Libras atendem públicos diferentes e não se substituem.

Fundamento: **Lei 10.436/2002** (reconhece a Libras), **Decreto 5.626/2005** (regulamenta seu
uso e difusão), **LBI 13.146/2015**. Parâmetros técnicos da janela: **ABNT NBR 15290**.

---

## 1. VLibras — o que é e o que não exige

Suíte gratuita e **de código aberto (LGPLv3)**, do Ministério da Gestão e Inovação em Serviços
Públicos (Secretaria de Governo Digital) com o MDHC e a UFPB.

| Componente | O que faz |
|---|---|
| **VLibras Plugin / Widget** | JavaScript; traduz o texto de uma página para Libras com avatar 3D. Chrome, Firefox, Safari |
| **VLibras Desktop** | Aplicativo Windows; traduz texto selecionado em qualquer programa |
| **VLibras Vídeo** | Portal que gera vídeo em Libras a partir de vídeo legendado ou de `.srt` |
| **API do Tradutor** | Recebe texto em português e devolve a **glosa**; recebe glosa e devolve vídeo |
| **WikiLibras** | Colaboração no dicionário de sinais |

**O login gov.br só existe no portal hospedado.** O código é aberto e roda local. Repositórios
em `github.com/spbgovbr-vlibras` — `vlibras-translator-api`, `vlibras-translator-text-core`,
`vlibras-translator-video-core` — com imagem `vlibras/translator-video` no Docker Hub e o pacote
`vlibras-translate` no PyPI (módulo Python e CLI `vlibras-translate` / `vlibras-translate-file`).

Limites do portal, quando ele for usado: `.mp4` até 500 MB, `.srt` até 600 palavras.

---

## 2. Os três níveis de entrega

O auditor **registra qual nível foi efetivamente alcançado**. Degradar é aceitável; degradar em
silêncio, não.

### Nível 1 — Janela de Libras em vídeo, automatizada (alvo)

**Caminho A — captura do Widget.** O Widget público roda em Chrome dirigido por Playwright; a
fala do avatar é capturada por *screencast* do CDP e montada em MP4 pelo ffmpeg.
Exige modo *headed* com GPU: **WebGL não renderiza em headless puro**. É o caminho leve e o
primeiro a tentar.

**Caminho B — pilha self-hosted.** `docker compose` com `translator-text-core`,
`translator-video-core` e a API (MongoDB, RabbitMQ, Redis, Node). Mais robusto e reprodutível,
porém os repositórios têm base antiga (Node 10, Ubuntu 18.04) e podem exigir ajuste de imagem.

Em ambos, o MP4 resultante entra no slide como janela de Libras.

### Nível 2 — Vídeo pelo portal VLibras Vídeo

Gera-se o `.srt` do roteiro e submete-se ao portal. Passo manual, com login.

### Nível 3 — Degrade documentado

Glosa gerada por `vlibras-translate`, `.srt` do roteiro entregue junto, e um slide de
acessibilidade com QR para o VLibras Widget e instruções do VLibras Desktop. **O relatório diz,
com todas as letras, que a janela de Libras não foi produzida e por quê.**

---

## 3. A janela de Libras no slide (regras J01 a J05)

- **Posição e tamanho:** conforme os parâmetros da **ABNT NBR 15290**. Consulte o texto da norma
  antes de auditar e **não use números de memória** — esta é uma das regras em que um valor
  inventado causa mais dano que a ausência da regra.
- **Contraste:** o avatar precisa se destacar do fundo; fundo neutro e uniforme atrás da janela.
- **Não sobrepor** texto, legenda ou informação essencial.
- **Permanência:** a janela não pode aparecer e sumir entre slides do mesmo bloco de conteúdo.
- **Controle:** nunca em autoplay em loop (I04); o usuário controla a reprodução.

---

## 4. Legendas e Subtítulos ao Vivo — complementar, não substituto

`Apresentação de Slides › Configurações de Legenda`: define idioma falado e idioma exibido,
posição da legenda e ativação automática. Transcreve a fala do apresentador em tempo real e pode
traduzir.

Atende pessoas surdas oralizadas, pessoas com perda auditiva parcial, público estrangeiro e
participantes neurodivergentes. **Não atende** quem tem a Libras como primeira língua. Deixar a
legenda ao vivo pré-configurada no arquivo é a regra J04; ela não zera a J01.

---

## 5. Revisão humana

Tradução automática português → Libras produz glosa aproximada, com erros de concordância
espacial e de classificadores. Sempre que possível, a glosa e o vídeo passam por **intérprete ou
pessoa surda** (regra J05). Como em D05, saída de modelo não revisada não é entrega.

---

## Fontes

- VLibras — https://www.vlibras.gov.br/ · Suíte no Software Público Brasileiro
- Repositórios — https://github.com/spbgovbr-vlibras
- `vlibras-translate` — PyPI
- VLibras Vídeo — https://video.vlibras.gov.br/
- ABNT NBR 15290:2005 — Acessibilidade em comunicação na televisão
- Lei 10.436/2002 · Decreto 5.626/2005 · Lei 13.146/2015
