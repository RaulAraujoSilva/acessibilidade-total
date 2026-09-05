# Prova de renderização direta de Libras

Data: 5 de setembro de 2026. Texto sintético: “A acessibilidade permite diferentes formas de ler o mesmo conteúdo”.

Serviço de glosa: `https://traducao2.vlibras.gov.br/translate`, POST JSON com texto. Índice público: `https://dicionario2-dth.vlibras.gov.br/static/TREES/2018.3.1.json`. Bundles Linux: `https://dicionario2-dth.vlibras.gov.br/static/BUNDLES/2018.3.1/LINUX/BR/` seguido do nome codificado do sinal.

Player extraído da imagem oficial `vlibras/vlibras-video-core:3.4.1`. Manifesto amd64: `sha256:71c0d550e99e7fe7a718088756e1011e6a2734aa1c87acb48b4300ed87316fc7`. Diretório na imagem: `translator-video-worker/core/player/`. As camadas foram conferidas por SHA-256 e somente os arquivos do player foram extraídos no acervo privado.

O arquivo de glosa usa UTF-8 e linhas `TEMPO#GLOSA`, por exemplo `0#...`. A codificação deve ser explícita: uma primeira tentativa com leitura local em codificação Windows incorreta corrompeu um termo acentuado e o player falhou. A tentativa corrigida finalizou com código zero e 289 JPGs. ffmpeg produziu MP4 de 11,56 segundos, 25 fps, 720×900 e 1.112.167 bytes. Renderização: 22,9445 segundos. Não inclui preparação, downloads e codificação. O ambiente foi Ubuntu no WSL e renderização por software llvmpipe.

```sh
xvfb-run -a /caminho/VLibras-Video.x86_64 --id teste --glosapath glosa.txt --videopath frames --width 720 --height 900 --speed 150 --framerate 25 --avatar icaro --subtitle off --bundlespath /caminho/bundles
ffmpeg -framerate 25 -pattern_type glob -i 'frames/img_*.jpg' -pix_fmt yuv420p libras.mp4
```

O adaptador web acrescenta cache por texto, avatar, FPS, hash do binário e versão declarada dos bundles, armazenado dentro do documento do usuário. O alinhamento disponível é por bloco completo, não por palavra. O cache não é compartilhado entre contas. As saídas não são automaticamente aprovadas.

Um segundo ensaio, usando o adaptador da aplicação no mesmo ambiente, levou 28,6812 segundos de ponta a ponta na primeira geração e 0,0542 segundo na recuperação do cache. As duas chamadas produziram a mesma chave de cache. Esse resultado é uma observação de um bloco, sem distribuição estatística ou validação linguística.

O [código da API de tradução](https://github.com/spbgovbr-vlibras/vlibras-translator-api) declara LGPL-3.0. Essa constatação não resolve a licença dos avatares, sinais, bibliotecas Unity e binário do player. Nenhum desses ativos foi incluído no Git. A conferência de redistribuição continua pendente.

Não foram medidos memória, falhas em textos extensos, taxa de sinais ausentes ou comparação em trechos idênticos à captura anterior. A inspeção de três quadros confirma enquadramento e mudança de pose; não certifica fluidez ou correção de Libras. Necessária revisão por pessoas fluentes em Libras, incluindo pessoas surdas. A eficiência de produção permanece requisito parcialmente atendido.

## Integração pelo navegador

O DOCX sintético D1 foi enviado pelo formulário, conferido, colocado na fila e reconstruído em DOCX, HTML, PPTX e PDF. Seus cinco blocos produziram cinco vídeos. O download autenticado do DOCX foi exercitado no navegador. Os tempos por bloco foram 29,36; 85,98; 119,89; 41,16 e 66,95 segundos, incluindo preparação de recursos e codificação. `results/ui-integration.json` registra durações e arquivos. O download opcional de bundles retornou recursos ausentes, como números e termos compostos de negação; ausência do bundle exato não determina por si só o que o avatar sinalizou. A tradução entregue exige revisão de sinais, datilologia e contexto.

Esse teste revelou e corrigiu limite de caminhos Windows e conversão de prefixos longos para WSL. O resultado não foi incluído retroativamente nas 36 medições documentais nem no tempo da primeira prova curta. A conta permanece no estado de revisão; não se registrou revisão humana fictícia.
