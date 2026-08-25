# scripts

| Arquivo | Estado | O que faz |
|---|---|---|
| `verificar_ambiente.py` | pronto | Diz o que voce tem, o que falta, **para que serve cada coisa** e o comando exato para instalar |
| `a11y_lib.py` | pronto | Acesso ao que o `python-pptx` nao expoe: alt text, marca de decorativo, ordem de leitura, idioma dos runs, heranca de tamanho de fonte, tabelas, secoes |
| `audit_contrast.py` | pronto | Resolve cor efetiva (tema + `clrMap` + `lumMod`/`lumOff`/`tint`/`shade`) e calcula contraste WCAG |
| `audit_pptx.py` | pronto | Auditor estatico das camadas A a I; camadas J a M saem como *nao verificado* |
| `simular_leitura.py` | pronto | Escreve o que um leitor de tela anunciaria, na ordem em que anunciaria |
| `export_pdfua.py` | a fazer | Exportacao COM com `DocStructureTags=True` |
| `audit_pdf.py` | a fazer | Validacao PDF/UA (veraPDF, PAC) |
| `build_deck.py` | a fazer | Constroi o deck acessivel por construcao |
| `gen_images.py` | a fazer | Figuras via gpt-image-2, com alt text e descricao longa no mesmo passo |
| `gen_audiodesc.py` | a fazer | Audiodescricao narrada + transcricao |
| `gen_libras.py` | a fazer | Janela de Libras via VLibras |
| `gen_transcricao.py` | a fazer | Transcricao linear em `.docx` acessivel |

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

## Dependencias

Só `audit_pptx.py` e `simular_leitura.py` rodam com **uma** biblioteca (`python-pptx`).
Os demais pedem mais - rode `verificar_ambiente.py` para saber exatamente o que falta
e por que.
