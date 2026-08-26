# scripts

| Arquivo | Estado | O que faz |
|---|---|---|
| `grade.py` | pronto | A regua do projeto: margens, faixas, 12 colunas, escala tipografica e tolerancias |
| `gerar_modelo.py` | pronto | Produz o modelo proprio: mata a CAIXA ALTA do template do Office e poe cada placeholder na grade |
| `audit_design.py` | pronto | Camada N: proporcao, margem, sobreposicao, ordem visual com heranca, area ociosa, caixa alta herdada |
| `verificar_ambiente.py` | pronto | Diz o que voce tem, o que falta, **para que serve cada coisa** e o comando exato para instalar |
| `a11y_lib.py` | pronto | Acesso ao que o `python-pptx` nao expoe: alt text, marca de decorativo, ordem de leitura, idioma dos runs, heranca de tamanho de fonte, tabelas, secoes |
| `audit_contrast.py` | pronto | Resolve cor efetiva (tema + `clrMap` + `lumMod`/`lumOff`/`tint`/`shade`) e calcula contraste WCAG |
| `audit_pptx.py` | pronto | Auditor estatico das camadas A a I e N; camadas J a M saem como *nao verificado* |
| `simular_leitura.py` | pronto | Escreve o que um leitor de tela anunciaria, na ordem em que anunciaria |
| `build_deck.py` | pronto | Constroi o deck acessivel POR CONSTRUCAO a partir de um roteiro YAML/JSON; recusa roteiro que geraria slide inacessivel |
| `export_pdfua.py` | pronto | Exportacao COM com `DocStructureTags=True`, corrige `/Lang` e `/Title`, grava o identificador PDF/UA-1 no XMP |
| `audit_pdf.py` | pronto | Camada L: pypdf (rapido) + veraPDF (ISO 14289) + PAC como passo humano |
| `gen_diagramas.py` | pronto | Diagramas tecnicos via HTML->PNG, uma versao por paleta; texto sempre exato |
| `audit_pacote.py` | pronto | Camada O: paridade de texto e de recursos entre as versoes de cor do mesmo material |
| `embutir_audio.py` | pronto | Poe a audiodescricao DENTRO do deck, sem autoplay, com alt text e ordem de leitura ajustada |
| `libras_caminho_a.py` | pronto | Grava a janela de Libras pelo VLibras Widget, local e sem conta gov.br |
| `embutir_libras.py` | pronto | Poe a janela de Libras na capa do deck, sem autoplay, com o alt text declarando que a glosa e automatica |
| `montar_tudo.py` | pronto | Roda o pipeline com portao em cada estagio, um deck por modo de cor |
| `gen_images.py` | a fazer | Figuras via gpt-image-2, com alt text e descricao longa no mesmo passo |
| `gen_audiodesc.py` | pronto | Audiodescricao narrada (ElevenLabs) + transcricao obrigatoria |
| `gen_libras.py` | parcial | Roteiro SRT e glosa; o video pelo renderizador Unity esbarrou nos bundles (ver `libras_caminho_a.py`, que resolve por outro caminho) |
| `gen_transcricao.py` | pronto | Transcricao linear em `.docx` com estilos de titulo reais |

## Auditar um arquivo

```bash
python scripts/audit_pptx.py deck.pptx --md relatorio.md --json achados.json
```

Sai com codigo 1 se houver Erro ou Aviso em aberto - serve direto em CI.

O relatorio traz, por regra: `ID | severidade | criterio | onde | detalhe`, mais a
**lista explicita do que nao foi verificado**. Ausencia de evidencia nao e conformidade.

## Ver a ordem de leitura

```bash
python scripts/simular_leitura.py deck.pptx --ignorados
```

Mostra a sequencia de anuncio slide a slide, incluindo o que fica em silencio por
estar marcado como decorativo. E um modelo do comportamento, nao o comportamento:
nao substitui a regra K03, que exige o percurso real com NVDA.

## Do roteiro ao PDF validado

```bash
python scripts/build_deck.py roteiro.yaml -o deck.pptx --todos-os-modos
python scripts/audit_pptx.py deck.pptx --md auditoria-pptx.md
python scripts/export_pdfua.py deck.pptx -o deck.pdf
python scripts/audit_pdf.py deck.pdf --md auditoria-pdf.md
```

Cada portao devolve codigo 1 se houver Erro ou Aviso em aberto. A correcao vai
para o ROTEIRO, nunca para o `.pptx` gerado: remediar o arquivo a mao e divida
que se perde no proximo build.

## Dependencias

Só `audit_pptx.py` e `simular_leitura.py` rodam com **uma** biblioteca (`python-pptx`).
Os demais pedem mais - rode `verificar_ambiente.py` para saber exatamente o que falta
e por que.
