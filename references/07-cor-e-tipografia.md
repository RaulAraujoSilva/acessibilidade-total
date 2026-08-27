# 07 — Cor, contraste e tipografia

> Todos os números deste arquivo foram **calculados**, não estimados. Fórmula WCAG 2.x de
> luminância relativa, sobre a paleta em `assets/paleta-okabe-ito.json`.

---

## 1. Contraste: os limiares

| Situação | AA | AAA |
|---|---|---|
| Texto normal (abaixo de 18pt, ou de 14pt negrito) | 4,5:1 | 7:1 |
| Texto grande (18pt ou mais, ou 14pt negrito ou mais) | 3:1 | 4,5:1 |
| Elemento não textual: ícone, borda, barra de gráfico, indicador de foco | 3:1 | — |

O verificador nativo detecta baixo contraste **apenas sobre fundo sólido**. Texto sobre foto,
sobre gradiente ou sobre imagem com transparência passa batido — é a regra E09, e ela é manual.

---

## 2. A paleta cega-segura, com as ressalvas medidas

Okabe-Ito é o padrão de fato em visualização científica: oito matizes distinguíveis nos três
tipos de daltonismo, com **luminâncias diferentes entre si**, o que faz o material sobreviver à
escala de cinza.

### O que ninguém diz sobre ela

**A paleta crua reprova em 1.4.11 sobre fundo claro.** Contraste de cada cor base contra
`#FAF7F2`:

| Cor | HEX | vs fundo claro | Passa 3:1? |
|---|---|---|---|
| Amarelo | `#F0E442` | 1,24 | não |
| Laranja | `#E69F00` | 2,11 | não |
| Azul-céu | `#56B4E9` | 2,16 | não |
| Cinza | `#999999` | 2,67 | não |
| Roxo-avermelhado | `#CC79A7` | 2,86 | não |
| Verde-azulado | `#009E73` | 3,20 | sim |
| Vermelhão | `#D55E00` | 3,62 | sim |
| Azul | `#0072B2` | 4,85 | sim |

Conclusão prática: **as cores base servem de preenchimento em áreas grandes, mas não passam
sozinhas como marca fina nem como cor de texto.** Use as variantes calculadas:

| Cor | Base | Marca ≥3:1 | Texto ≥4,5:1 | Texto sobre a base |
|---|---|---|---|---|
| Laranja | `#E69F00` | `#BF8400` | `#986900` | escuro (7,73) |
| Azul-céu | `#56B4E9` | `#4897C4` | `#39779A` | escuro (7,54) |
| Verde-azulado | `#009E73` | `#009E73` | `#00825E` | escuro (5,09) |
| Amarelo | `#F0E442` | `#9A922A` | `#7A7422` | escuro (13,16) |
| Azul | `#0072B2` | `#0072B2` | `#0072B2` | **branco** (5,19) |
| Vermelhão | `#D55E00` | `#D55E00` | `#BB5300` | escuro (4,50) |
| Roxo | `#CC79A7` | `#C675A2` | `#9D5D81` | escuro (5,69) |
| Cinza | `#999999` | `#8E8E8E` | `#717171` | escuro (6,11) |

Atenção ao azul `#0072B2`: é a **única** cor da paleta que pede texto branco por cima; escuro
sobre ela dá 3,36 e reprova. Vermelhão com texto escuro dá 4,50 — passa raspando, então em corpo
de texto prefira outra combinação.

### Fundo e texto

| Papel | HEX | Contraste |
|---|---|---|
| Fundo padrão | `#FAF7F2` | — |
| Texto sobre claro | `#1A1A1A` | **16,29:1** |
| Fundo daltônico-seguro | `#F5F5F0` | com `#1A1A1A`: 15,91:1 |
| Fundo alto contraste | `#000000` | com `#FFFFFF`: 21:1 |

**Por que não branco puro com preto puro.** O branco `#FFFFFF` sob texto `#000000` produz
irradiação sobre os traços da tipografia (*glare* e halo), causando fadiga visual e agravando
sintomas da síndrome de Irlen. Off-white com quase-preto entrega 16,29:1 — muito acima do AAA —
sem o ofuscamento. É a regra E08.

---

## 3. Cor nunca sozinha (1.4.1)

Toda série, categoria ou estado recebe, além da cor, **pelo menos um** entre:

- forma distinta (círculo, triângulo, quadrado);
- hachura ou textura de preenchimento;
- rótulo direto no elemento — a melhor opção, porque também elimina a ida e volta à legenda;
- ícone com significado próprio.

**Teste de dois minutos:** ligue a escala de cinza do Windows (`Win+Ctrl+C`) e leia o deck. Se
alguma informação desapareceu, a cor estava sozinha. Depois, rode Color Oracle nos três tipos de
daltonismo.

---

## 4. Tipografia

### Fonte

Sans-serif bem calibrada: **Arial, Calibri, Verdana, Tahoma, Segoe UI, Open Sans**, ou
tipografias desenhadas para legibilidade como **Atkinson Hyperlegible** e **OpenDyslexic**.

As serifas produzem um borrão perceptual entre letras no cérebro disléxico; fontes de
rastreamento homogêneo evitam a fusão de caracteres, como `r` + `n` lidos como `m`.

### Escala

| Elemento | Mínimo | Alvo |
|---|---|---|
| Corpo de texto | 18pt | 24 a 32pt |
| Título | 32pt | 40pt ou mais |
| Rodapé e fonte da citação | 14pt | 16pt |

Projeção amplia a distância de leitura: o que é confortável na tela do autor pode ser ilegível
na quinta fileira.

### Composição

| Regra | Por quê |
|---|---|
| Alinhar à esquerda, com margem direita irregular | O texto justificado abre espaços desiguais entre palavras e cria "rios de branco", que interrompem a sacada ocular |
| Entrelinha 1,5 ou mais | Impede a permutação visual entre a linha atual e a seguinte |
| 60 a 70 caracteres por linha | Acima disso o olho perde o retorno de linha |
| Negrito para destaque | Itálico fragmenta as hastes; sublinhado interfere na base morfológica das letras |
| Nunca frase inteira em CAIXA ALTA | Suprime ascendentes e descendentes (`d` contra `p`) e transforma a palavra num bloco retangular, matando a leitura por forma global |
| No máximo 6 marcadores por slide | Carga cognitiva |

---

## 5. Os três modos de exibição

Decisão de arquitetura, revista em 26/08/2026: **um arquivo por modo**, gerados do mesmo roteiro.

| Modo | Arquivo | Fundo | Texto | Séries |
|---|---|---|---|---|
| Padrão | `…-padrao.pptx` | `#FAF7F2` | `#1A1A1A` | Okabe-Ito, variantes `marca_min_3_1` |
| Alto contraste | `…-alto-contraste.pptx` | `#000000` | `#FFFFFF` | cores base, que ganham contraste sobre preto |
| Daltônico-seguro | `…-daltonico-seguro.pptx` | `#F5F5F0` | `#1A1A1A` | subconjunto de matizes maximamente separados, com forma e rótulo reforçados |

O desenho anterior era um arquivo só, com slide-hub e três seções paralelas. Ele resolvia a
distribuição — um anexo, não três — e foi abandonado por um motivo que não estava na conta:
**de 85 slides, 57 eram o mesmo conteúdo em outra paleta.** Quem enxerga escolhe a paleta no hub
e ignora o resto; quem navega em sequência atravessa tudo três vezes. Pior: `gen_transcricao`
percorria o arquivo inteiro, então a **transcrição linear** — o artefato que mais importa para
quem lê assim — saía triplicada, com sufixo de modo nos títulos.

> Por que não uma troca de paleta em tempo real: o `.pptx` não tem esse recurso. Fazer com macro
> exigiria `.pptm`, que chega com macro bloqueada por Mark-of-the-Web quando o arquivo é baixado,
> e não funciona no PowerPoint Web nem no mobile. Isso continua verdadeiro — é o que fecha a
> porta para qualquer solução dentro de um arquivo só.

Com arquivos separados, **o modo fica nos metadados, não no conteúdo**: `cp.title` leva o nome do
modo, que é o que o leitor de tela anuncia ao abrir, e o texto dos slides permanece idêntico nos
três. É isso que torna a paridade verificável.

### Por que o modo daltônico parece igual ao padrão — e o que foi feito

A pergunta apareceu ao olhar os dois lado a lado, e é justa: o destaque é **exatamente a mesma
cor** (`#0072B2`) nos dois, e o fundo muda de `#FAF7F2` para `#F5F5F0` — diferença que ninguém
percebe.

**Isso está certo, e é o problema.** A paleta Okabe-Ito **já é cega-segura por construção**: ela
foi desenhada para que as oito cores permaneçam distinguíveis sob protanopia, deuteranopia e
tritanopia. O modo daltônico nunca esteve corrigindo uma paleta insegura — ele só troca duas
séries (verde-azulado e roxo-avermelhado por cinza e vermelhão), que colidem entre si em alguns
tipos. E como todo elemento dos diagramas já carrega **rótulo em texto**, a cor nunca foi o único
meio de informação: o critério 1.4.1 já estava atendido antes.

Só que uma versão que se anuncia como "daltônico-seguro" e entrega um fundo 2% mais frio **não se
sustenta** — promete uma diferença que não existe. Ou ela acrescenta algo real, ou não deveria ser
vendida como modo à parte.

O que ela passou a acrescentar é **codificação redundante**: na paleta daltônica cada série ganha
um **ângulo de hachura próprio** (45°, 135°, 90°, 0°…). A distinção deixa de depender de perceber
a cor — e passa a sobreviver também à impressão em preto e branco e à escala de cinza do Windows,
que é a regra M03. Implementado em `gen_diagramas._hachura`.

> A cor continua ali, e continua cega-segura. O que mudou é que ela deixou de ser **o único**
> canal, de fato e não apenas no rodapé do relatório.


Os três modos são **variações de paleta do mesmo conteúdo**, jamais versões com conteúdo
diferente. Conteúdo diferente por deficiência é segregação, não acessibilidade. Antes isso era
uma promessa do laço de construção; agora é a **camada O** do catálogo, que compara texto, alt
text, notas e recursos slide a slide e reprova a divergência.

`--arquivo-unico` continua gerando o desenho antigo, para quem precisa mesmo entregar um anexo só.
