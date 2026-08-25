# tests

Dois testes, em sentidos opostos. Auditor só presta se passar nos dois.

| Teste | Pergunta que responde |
|---|---|
| `test_auditor.py` | O auditor **enxerga** o que foi plantado? |
| `test_falso_positivo.py` | O auditor **se cala** diante do que está certo? |

```bash
python tests/run_all.py
```

## `deck_ruim.pptx` — o deck-armadilha

Gerado por `make_deck_ruim.py`, com **33 defeitos plantados**, cada um anotado com a regra
do catálogo que tem obrigação de acusá-lo (a lista `GABARITO`). Regra do gabarito que não
for acusada é defeito **do auditor**, não do deck.

Cobre: metadados vazios, `lang="en-US"` em texto português, slide sem título, títulos
repetidos, caixa de texto solta, lista digitada com hífen, título fora da ordem de leitura,
imagem sem alt, alt igual a nome de arquivo, alt com prefixo "Imagem de", resíduo de
"Descrição gerada automaticamente", alt longo demais, decorativo com `descr` simultâneo,
contraste baixo em texto normal e em texto grande, preto puro sobre branco puro, fonte com
serifa, corpo abaixo de 18pt, parágrafo justificado, itálico e CAIXA ALTA, tabela sem
cabeçalho com célula mesclada e coluna vazia, link com URL crua, link "clique aqui" e alvo
de clique minúsculo.

## `deck_bom.pptx` — o deck de controle

Gerado por `make_deck_bom.py`. Correto de propósito. Qualquer não conformidade aqui é
**falso positivo**, e o teste falha. Os 14 itens que saem como *não verificado* (camadas
J, K, L e M) são esperados: dependem de mídia, do PDF exportado ou de um humano.

> Os `.pptx` são artefatos gerados e não vão para o repositório. Os geradores são a fonte
> da verdade.
