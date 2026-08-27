# 06 — Libras

> Libras é **língua**, não legenda. Um deck com legenda em português não está acessível a quem
> tem o português como segunda língua e a Libras como primeira. Legenda ao vivo e janela de
> Libras atendem públicos diferentes e não se substituem.

Fundamento: **Lei 10.436/2002** (reconhece a Libras), **Decreto 5.626/2005** (regulamenta seu
uso e difusão), **LBI 13.146/2015**. Parâmetros técnicos da janela: **ABNT NBR 15290:2016** —
atenção à edição, a de 2005 está superada e é a que mais circula na internet.

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

### O que o spike de 25/08/2026 apurou

Vale registrar para ninguém reinvestigar do zero.

**Caminho A (captura do Widget):** o widget carrega e inicializa
(`window.VLibras` presente, sem erro de console), mas o botão de acesso não é
clicável numa página sintética montada por `set_content` — o player Unity só
carrega depois desse clique. Faltou servir a página por HTTP de verdade.

**Caminho B (renderização local):** avançou bem mais. O renderizador **existe e é
invocável direto**, sem RabbitMQ nem MongoDB. Dentro de
`vlibras/translator-video:3.1.0` (436 MB):

| Caminho | O que é |
|---|---|
| `/dist/player/VLibras-Video.x86_64` | binário Unity standalone do avatar |
| `/usr/bin/xvfb-run`, `/usr/bin/Xvfb` | display virtual, já instalados |
| `/usr/bin/ffmpeg` | montagem dos quadros em vídeo |

A chamada, lida em `/dist/player/playerwrapper.py`:

```
VLibras-Video.x86_64 --id <tag> --glosapath <arquivo> --videopath <dir>     --width 720 --height 900 --speed 150 --framerate 24     --avatar icaro --subtitle off --bundlespath <BUNDLES>
```

O arquivo de glosa tem o formato `0#GLOSA EM MAIÚSCULAS`.

**O bloqueio:** os *bundles* de sinais (`VIDEOMAKER_BUNDLES_DIR`) não estão nessa
imagem nem em `vlibras/video-core:4.0.0` — são servidos em execução pelo serviço
`dicionario` (`vlibras/dicionario`, ~347 MB). **Quem retomar deve começar por
subir o `dicionario` e descobrir por onde ele publica os bundles.**

### Nível 3 — Degrade documentado

Glosa gerada por `vlibras-translate`, `.srt` do roteiro entregue junto, e um slide de
acessibilidade com QR para o VLibras Widget e instruções do VLibras Desktop. **O relatório diz,
com todas as letras, que a janela de Libras não foi produzida e por quê.**

---

## 3. A janela de Libras: os parâmetros da norma

Fonte: **ABNT NBR 15290** (edição vigente **2016**, confirmada em 11.12.2025), seção 7 —
*Diretrizes para a janela de LIBRAS*. Os valores dimensionais abaixo foram lidos no texto
integral da norma, item **7.1.3 Recorte ou wipe**.

### Dimensão e posição (7.1.3)

| Requisito | Valor |
|---|---|
| Altura da janela | **no mínimo metade da altura da tela** |
| Largura da janela | **no mínimo um quarto da largura da tela** |
| Posição | de modo a **não ser encoberta pela tarja da legenda oculta** |
| Deslocamento | se a janela precisar mudar de posição, deve haver **continuidade da imagem** |

### Qualidade da janela (7.1.2)

- Contrastes nítidos **tanto em cores quanto em preto e branco**.
- Contraste entre o pano de fundo e os elementos do intérprete.
- O foco deve abranger **toda a movimentação e gesticulação** do intérprete.
- Iluminação sem sombras nos olhos e sem ofuscamento.

### Interpretação e visualização (7.1.4)

- Vestimenta, pele e cabelo do intérprete **contrastantes entre si e com o fundo**; evitar fundo
  e vestimenta em tons próximos ao da pele.
- **No recorte não se inclui nem se sobrepõe nenhuma outra imagem.**

### Estúdio (7.1.1)

Espaço entre intérprete e fundo para não gerar sombras; iluminação adequada; câmera em tripé
fixo; marcação no solo delimitando a movimentação.

### Transposição para o slide — e a ressalva honesta

A NBR 15290 regula **televisão**. Aplicá-la a um slide é analogia, não subsunção: onde a norma
diz "tela do televisor", o auditor lê "área útil do slide". A analogia é defensável e é o melhor
parâmetro brasileiro disponível, mas **deve ser declarada como analogia no relatório**, e não
apresentada como conformidade formal com a norma.

Em 16:9 (33,87 cm × 19,05 cm), os mínimos ficam em **9,53 cm de altura** e **8,47 cm de
largura** — o que, na prática, é uma janela grande. Um avatar miniaturizado no canto reprova.

Complementarmente, a **ABNT NBR 15610-3:2016** (TV digital terrestre — Parte 3: Língua de Sinais)
trata especificamente do transporte de Libras e vale a consulta quando o entregável for vídeo.

### Gerar em lote: renderizar, não fotografar a tela

A captura do widget por `gfxcapture` funciona e entrega 25 fps, mas é o pior caminho disponível:
depende de janela visível, de *timing*, e custa ~45 s por vídeo. **Renderizar é melhor** — e a
receita está verificada dentro da própria imagem oficial.

> **Use `vlibras/vlibras-video-core:3.4.1`, não `translator-video:3.1.0`.** A 3.1.0 concatena um
> **vídeo de propaganda** no fim de toda saída (`ffmpeg.concat(video_stream, ad_stream)`, com o
> `ad720x900.mp4` embutido na imagem). Todos os seus vídeos terminariam com o carimbo gov.br.

**1. Glosa — endpoint público, sem login.**

```
POST https://traducao2.vlibras.gov.br/translate
Content-Type: application/json
{"text": "..."}
```

Medido: **HTTP 200 em ~0,19 s**, `x-ratelimit-limit: 300`/min, limite de 5.000 caracteres, sem
cookie nem token. É o mesmo endpoint que o pipeline oficial usa — está no `settings.ini` da
imagem. Devolve, por exemplo:

```
ACESSIBILIDADE DIGITAL&COMPUTADOR GARANTIR TODO PESSOA PODER&POSSIBILIDADE USAR INTERNET [PONTO]
```

O `POST /video` do mesmo host devolve **401** — mas o código-fonte da API **não tem middleware de
autenticação**: o 401 vem de um gateway na frente da instância de produção. Quem sobe a API
própria tem `/video` aberto.

**2. Bundles de sinais — públicos.**

`https://dicionario2-dth.vlibras.gov.br/static/BUNDLES/2018.3.1/LINUX/BR/<SINAL>`, e o índice com
**23.403 sinais** em `/static/TREES/2018.3.1.json`. A plataforma é **LINUX** — está escrito no
`StreamingAssets/config.json` que acompanha o binário (`"dictionaryURL": ".../2018.3.1/LINUX/"`).
AssetBundle é por plataforma e **não é intercambiável**: `WEBGL` não serve ao player Linux.

**3. Formato da glosa.** Arquivo `.txt` UTF-8, uma linha por bloco:

```
0#CATALOGAR TER 117 REGRA 15 CAMADA [PONTO]
```

`TEMPO_MS#GLOSA` (a ordem é controlada por `"timeGlosaOrder"` no `config.json`). `&` separa
sinais compostos; pontuação vai em colchetes: `[PONTO]`, `[INTERROGAÇÃO]`, `[EXCLAMAÇÃO]`. Fora
do padrão, o binário sai com código 1 e a mensagem *"Glosa file is empty or does not match
pattern"*.

**4. Render.** O binário **não produz mp4** — ele escreve JPGs numa pasta, e o mp4 sai do ffmpeg
depois. `--videopath` é um **diretório**, não um arquivo. E ele exige um display X (por isso a
imagem instala `xvfb`).

```bash
xvfb-run VLibras-Video.x86_64 --id <tag> --glosapath g.txt --videopath frames/     --width 720 --height 900 --speed 150 --framerate 24 --avatar icaro     --subtitle off --bundlespath /bundles
ffmpeg -framerate 24 -pattern_type glob -i 'frames/img_*.jpg' -pix_fmt yuv420p out.mp4
```

Avatares: `icaro`, `hozana` e, na 3.4.1, `guga`. Existe ainda um `--region` (sinal regionalizado
por UF) que o wrapper oficial nunca passa.

**Não é preciso fila.** RabbitMQ, MongoDB, Redis e o worker ficam fora do caminho crítico: são
quatro comandos.


### Taxa de quadros — o parâmetro que faltava

**Não há mínimo normativo.** A NBR 15290 regula dimensão, posição, contraste, foco e estúdio;
não fixa taxa de quadros. O número adotado vem da convergência de três fontes:

| Fonte | Número |
|---|---|
| **ITU-T H.Sup1** — conversação em língua de sinais por vídeo de baixa taxa | **≥ 25 fps** |
| Renderizador oficial do VLibras (`playerwrapper.py`) | `--framerate 24` |
| EN 301 549, citada na RTC Accessibility User Requirements (W3C) | ≥ 20 fps |
| Hooper et al., *Sign Language Studies* 8(1), 2007 · Tran et al., ASSETS 2013 | perda de compreensão **abaixo de 10 fps** |

Adota-se **24–25 fps**; **15 fps é o piso** da regra J07. A primeira janela deste projeto saiu a
**2,5 fps** — abaixo da condição mais baixa já testada em qualquer desses estudos. Em Libras o
movimento **é** fonologia (parâmetro M) e a expressão facial carrega marcação gramatical: aquela
janela não era "de qualidade baixa", era provavelmente **ininteligível**.

A correção foi trocar o laço de `page.screenshot` (~0,4 s por quadro) pelo filtro **`gfxcapture`**
do ffmpeg 8.0+, que captura a janela pela API Windows.Graphics.Capture: pega o conteúdo composto
pela GPU, não se contamina com oclusão e recorta na própria captura. Medido: **25 fps e
462×670 px**, contra 2,5 fps e 312×452.

> **Armadilha do recorte.** O `gfxcapture` devolve pixels **físicos**; a página reporta pixels
> **CSS**. Com o Windows a 150%, `devicePixelRatio` diz 1.0 e a captura vem 1,483× maior — o
> primeiro recorte caiu numa área branca. Por isso o gravador faz uma **sonda** de 1 s da janela
> inteira e deriva a escala antes de recortar.


### Demais regras da camada J

- **Permanência:** a janela não pode aparecer e sumir entre slides do mesmo bloco de conteúdo.
- **Controle:** nunca em autoplay em loop (I04); o usuário controla a reprodução.

---

## 4. Legendas e Subtítulos ao Vivo — complementar, não substituto

`Apresentação de Slides › Configurações de Legenda`: define idioma falado e idioma exibido,
posição da legenda e ativação automática. Transcreve a fala do apresentador em tempo real e pode
traduzir.

Atende pessoas surdas oralizadas, pessoas com perda auditiva parcial, público estrangeiro e
participantes neurodivergentes. **Não atende** quem tem a Libras como primeira língua.

**Isto não se configura no arquivo.** Verificado no objeto de automação do PowerPoint: nem
`SlideShowSettings` nem `Application.Options` expõem legenda, idioma falado ou idioma exibido.
São preferências da máquina de quem apresenta. A regra J04 foi reescrita de acordo: ela virou
uma **instrução de entrega**, não uma conformidade auditável no `.pptx`. Prometer o contrário
seria vender como propriedade do documento algo que o documento não carrega.

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
- **ABNT NBR 15290:2016** — Acessibilidade em comunicação na televisão (seção 7). Ficha e texto
  integral no acervo ABNT Coleção/MPF: https://www.abntcolecao.com.br/mpf/grid.aspx
- **ABNT NBR 15610-3:2016** — TV digital terrestre — Acessibilidade — Parte 3: Língua de Sinais
- Lei 10.436/2002 · Decreto 5.626/2005 · Lei 13.146/2015
