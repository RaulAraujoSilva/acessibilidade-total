# 09 — Design e composição

> Um slide acessível não é um slide feio. Este arquivo existe porque um deck deste projeto
> passou nas 98 regras de A a M com **zero erros** — e tinha figura esticada em 48%, tabela
> cortada pela faixa do rodapé, apoio de seção acima do título e título em CAIXA ALTA.
>
> Acessibilidade cuida de semântica e contraste. Composição é outra coisa, e sem ela o
> resultado é correto e ruim.

---

## 1. Os defeitos que criaram esta camada

Todos medidos, nenhum de gosto.

| Medida | O que era |
|---|---|
| **48,1%** de erro de proporção | `add_picture` recebia largura **e** altura; a figura era esticada até caber |
| **19,05 cm** | fim da tabela num slide de 19,05 cm: a última linha ficava sob a faixa do rodapé |
| **8,07 cm × 12,24 cm** | apoio da seção acima do título, no layout "Section Header" do Office |
| `cap="all"` | no `slideLayout3.xml` do template padrão: o título saía em maiúsculas |

Os dois últimos passavam despercebidos porque **a regra olhava só o slide**. Posição e
transformação de caixa vinham do *layout*, e nada no slide denunciava.

---

## 2. A régua: `scripts/grade.py`

Construtor e auditor leem o mesmo arquivo. Sem isso, um constrói numa medida e o outro cobra
noutra.

| Medida | Valor |
|---|---|
| Área do slide | 33,87 × 19,05 cm (16:9) |
| Margem de segurança | 1,4 cm — nada de conteúdo fora dela |
| Faixa do título | 1,4 a 3,6 cm |
| Faixa de conteúdo | 4,2 a 17,4 cm |
| **Zona proibida** | a partir de 17,9 cm: só decorativo |
| Grade | 12 colunas, medianiz de 0,5 cm |

Escala tipográfica: capa 46pt · título 34pt · seção 40pt · corpo 24pt · corpo denso 20pt ·
apoio e tabela 18pt · número em destaque 96pt · citação 32pt. **A partir de 40pt o texto é
*display***, e as regras de leitura corrida (entrelinha 1,5) deixam de valer — pela mesma
razão que não valem para títulos.

---

## 3. Encaixar, nunca esticar

```python
escala = min(caixa_w / nativo_w, caixa_h / nativo_h)
```

A caixa é o limite; a figura se encaixa dentro dela e a sobra vira centralização. Passar
largura e altura ao mesmo tempo é o que produz a distorção — e 1% já se vê.

Figura larga (razão ≥ 1,8) precisa de **mais colunas**, senão encolhe na altura e cai abaixo do
mínimo legível na projeção.

---

## 4. A armadilha do eixo Z, de novo

Fundo de cartão criado depois do texto entra por último no `spTree` e é desenhado **por cima**.
Num teste real, os quatro cartões saíram vazios: o texto estava lá, escondido.

A saída é a mesma que o catálogo já indica na regra C03: como o fundo é **decorativo**, ele já
está fora da ordem de leitura, então movê-lo no eixo Z não muda nada do que o leitor de tela
anuncia. `mandar_para_tras()` o insere logo após `p:grpSpPr`.

---

## 5. Marcador é para lista

O `buChar` herdado do layout aparece antes de um número em destaque, de um título de cartão ou
de um subtítulo de capa — e vira sujeira. A regra B09 exige marcador **nativo em lista**; ela
não pede marcador em tudo. `sem_marcador()` aplica `a:buNone` onde não é lista.

---

## 6. Um vocabulário de slides, não um só

Todos com *placeholder* real — cartão desenhado com caixa de texto solta reprovaria em B05, e
com razão.

| Tipo | Para quê |
|---|---|
| `capa` · `secao` · `citacao` | respiro; isentos da regra de área ociosa |
| `conteudo` | texto, com figura ou tabela opcional |
| `destaque` | um número grande com rótulo, e a explicação ao lado |
| `cartoes` | de 2 a 4 blocos paralelos, com fundo decorativo |
| `comparacao` | duas colunas com cabeçalho próprio |

Em layout de colunas paralelas, **ler uma coluna inteira e depois a outra é tão correto quanto
ler linha a linha** — as regras C02 e N04 aceitam as duas ordens quando as colunas não se
cruzam.

---

## 7. O modelo é o lugar da decisão

`assets/modelo-acessivel.pptx`, gerado por `scripts/gerar_modelo.py`, é o que impede o template
do Office de decidir por nós. Ele remove todo `cap`, reposiciona cada *placeholder* na grade,
grava a paleta no `a:clrScheme` e renomeia os layouts para o vocabulário acima.

O gerador **valida o que produziu** antes de liberar: nenhuma caixa alta, título sempre acima do
corpo, nada na zona do rodapé, e todos os layouts capazes de gerar slide.

---

## 8. O que continua sendo humano

Nenhuma métrica substitui olhar. Os defeitos desta lista apareceram ao **renderizar o slide em
PNG e ver** — não numa contagem. Renderize ao menos um slide de cada tipo antes de fechar.
