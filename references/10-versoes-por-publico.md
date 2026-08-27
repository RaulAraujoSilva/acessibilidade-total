# 10 — Versões por público

> Este arquivo existe porque uma decisão deste projeto colidiu com um princípio dele mesmo.
> `SKILL.md` diz, no princípio nº 1: *"Um artefato para todos. Desenho Universal, não uma versão
> por deficiência."* E o auditor reprova com a frase *"conteúdo diferente por deficiência é
> segregação"*. Ainda assim, entregar a mesma parede de texto em português a quem tem **Libras
> como primeira língua** não é desenho universal: é indiferença com boa consciência.
>
> O princípio não cai. Ele ganha um teste.

---

## 1. O que separa acesso de segregação

O princípio foi escrito contra a prática de entregar ao deficiente uma versão **pior**. Uma
versão com pouco texto e Libras em todo slide não dá menos — dá o mesmo conteúdo na **primeira
língua** do interlocutor. As cinco condições abaixo são o que torna essa diferença verificável,
e não retórica:

| # | Condição | Como se verifica |
|---|---|---|
| 1 | Nenhuma versão dá **menos** | **O04** — toda mensagem-chave da base aparece em todas |
| 2 | Nenhuma versão dá **mais** | **O05** — nada exclusivo; duas versões que dizem coisas diferentes são duas verdades |
| 3 | A escolha é **de todos** | `LEIA-ME.md` abre por *qual arquivo abrir e por quê* (**O03**) |
| 4 | A base continua acessível **sozinha** | a versão extra é acréscimo, não desculpa para a base ser ruim |
| 5 | Cada versão **se declara** | **O06** — o público vai no `dc:title`, que é o que o leitor de tela anuncia ao abrir |

Sem a condição 1 e 2 verificadas, "versão equivalente" é promessa. A âncora é o campo
`mensagem_chave` do roteiro, que o construtor grava nas notas como `[chave] …` e o
`audit_pacote.py` compara entre perfis.

## 1.1 Que recurso vai em que versão

O recurso segue **o sentido que ele serve**. Parece óbvio dito assim, e ainda assim este projeto
errou uma rodada inteira nisso: entregou o deck de Libras com **28 faixas de audiodescrição**,
13,7 dos seus 14,3 MB, para um público que não as usa.

O erro veio de aplicar ao eixo de público uma regra escrita para o eixo de cor. A **O02**
— *"recurso presente numa versão e ausente noutra"* — existe porque as três paletas têm de ser
o mesmo arquivo com outra cor. Entre **perfis** ela se inverte: forçar todo recurso em toda
versão não é paridade, é peso morto, e ainda embaralha para quem abre o arquivo o que aquela
versão de fato oferece.

| Recurso | Serve quem | Onde vai |
|---|---|---|
| **Audiodescrição narrada** | não enxerga | `completo` e `leitura_facil` |
| **Janela de Libras em todo slide** | tem Libras como primeira língua | `libras` |
| **Janela de Libras na capa** | qualquer pessoa, como porta de entrada | todas as versões |
| **Alto contraste / paleta cega-segura** | baixa visão e discromatopsia | eixo de cor, não de perfil |
| **Transcrição linear** | linha braille, leitura sequencial, revisão | uma, para o pacote |

> **A versão `completo` carrega tudo.** É a que nunca falta nada a ninguém, e é para ela que o
> `LEIA-ME.md` manda quem estiver em dúvida — inclusive quem for surdocego, que precisa da
> transcrição e da audiodescrição ao mesmo tempo. As versões de perfil são **especializações**,
> nunca o único caminho.

Por isso a camada O roda **O01 e O02 dentro de um perfil** (entre paletas) e **O04/O05 entre
perfis** (equivalência de mensagem). O que se cobra entre públicos é que a **informação** não
mude — não que o **suporte** seja o mesmo.

**Dois eixos, dois testes.** *Modo de cor* troca a paleta e nada mais: entre modos o texto tem de
ser **idêntico** (O01/O02). *Perfil de público* troca o registro do texto de propósito — comparar
literalmente reprovaria por construção.

---

## 2. Perfil `libras` — Libras como primeira língua

### A base legal, com as palavras da lei

**Lei 13.146/2015 (LBI), art. 28, IV** — é a citação central, porque traz a tese em texto legal:

> oferta de educação bilíngue, em **Libras como primeira língua** e na modalidade escrita da
> língua portuguesa **como segunda língua**, em escolas e classes bilíngues e em escolas
> inclusivas

**Decreto 5.626/2005, art. 24** — melhor âncora que a NBR 15290 para material de curso, porque
fala de material visual de ensino, não de televisor:

> A **programação visual** dos cursos de nível médio e superior […] na modalidade de educação a
> distância, deve dispor de sistemas de acesso à informação como **janela com tradutor e
> intérprete de Libras** […]

Complementam: **Decreto 5.626, art. 14 §1º II, VI e VII** (português escrito como segunda língua
para alunos surdos; avaliação coerente com aprendizado de segunda língua; conhecimento expresso
em Libras registrado em vídeo), **art. 22 §1º** (Libras e português como línguas de instrução),
e **LBI art. 68 §3º** (produção de artigos em formato acessível, *"inclusive em Libras"*).

### O contra-argumento, enfrentado de frente

**Lei 10.436/2002, art. 4º, parágrafo único:**

> A Língua Brasileira de Sinais - Libras **não poderá substituir** a modalidade escrita da língua
> portuguesa.

Quem defender "menos texto + Libras" sem tratar disso perde a discussão numa linha. A resposta:
o dispositivo veda **substituir** — suprimir o português —, não veda **reduzir com bilinguismo**.
A versão mantém as duas línguas e muda a ordem de precedência. E a LBI art. 28 IV, posterior e de
hierarquia legal equivalente, consagra explicitamente o modelo L1/L2.

### O que NÃO fundamenta esta versão

- **"Conforming alternate version" do WCAG não serve para Libras.** A definição exige que a
  versão alternativa entregue a mesma informação *"in the same human language"*. Libras é outra
  língua. O conceito WCAG que trata de sinais é o **1.2.6 Sign Language (AAA)**, e ele cobre
  *áudio pré-gravado em mídia sincronizada* — não slide estático.
- **LBI art. 63** é sítio da internet; **art. 67** é radiodifusão. Escopo errado.
- **Não existe norma brasileira sobre slides com janela de Libras.** Aplicar a NBR 15290 —
  *"acessibilidade em comunicação **na televisão**"* — a um slide é **analogia**, e deve ser
  declarada como tal no relatório.

### Regra editorial

| Item | Valor |
|---|---|
| Parágrafos por slide | no máximo **2** |
| Palavras por parágrafo | no máximo **14** |
| Frases por parágrafo | **1** — uma ideia por vez |
| Corpo | 28pt |
| Faixa da janela | **4 das 12 colunas**, reservadas no layout |
| Janela | **9,11 × 13,20 cm** — acima dos mínimos de 8,47 e 9,53 cm |

Três colunas dariam 7,39 cm e reprovariam. A faixa fica **vazia no layout**: sem ela a janela
cobriria texto e reprovaria em N03 — foi por isso que, na primeira entrega, a janela existia só
na capa.

---

## 3. Perfil `leitura_facil` — deficiência cognitiva e TDAH

### O que existe, e o que não existe

**Não há norma brasileira de Leitura Fácil.** Quem diz isso é a própria
**ABNT NBR ISO 24495-1:2024**, que é de *Linguagem Simples* e distingue as duas por escrito:

> Linguagem Simples não é para ser confundida com Leitura Fácil. A **Linguagem Simples pode ser
> usada para o público em geral**, enquanto a **Leitura Fácil é usada para pessoas com
> dificuldades de compreensão de leitura**.

E a própria ISO exclui acessibilidade do seu escopo (item 1): *"It does not include existing
technical guidance about accessibility"*. Ela fundamenta a **redação**, não a conformidade — foi
por isso que a regra F09 teve o critério reatribuído.

Atenção à data: a ISO é de **2023**; a adoção brasileira é de **2024**.

### O que fundamenta

- **LBI art. 3º, V** põe **"linguagem simples, escrita e oral"** dentro da definição legal de
  comunicação, desde 2015.
- **Lei 14.129/2021, art. 3º, VII** — *"o uso de linguagem clara e compreensível a qualquer
  cidadão"* (as palavras da lei são "clara e compreensível", não "simples").
- **Inclusion Europe, "Information for all"** e **IFLA, "Guidelines for easy-to-read materials"**
  (Nomura, Skat Nielsen & Tronbacke, 2010) — as duas referências internacionais de Leitura Fácil.
- **W3C COGA, "Making Content Usable"** — é *Working Group Note*, **não norma**; o próprio
  documento diz que a publicação *"does not imply endorsement by the W3C Membership"*. Cite como
  boa prática. Dos 8 objetivos, o **Objective 3** (*Use Clear and Understandable Content*) é o
  que se aplica inteiro a documento; os que tratam de *undo*, autenticação e memória entre etapas
  pressupõem aplicação web.
- **WCAG**: para texto de documento valem **1.4.8**, **3.1.3**, **3.1.4** e **3.1.5** — e os
  quatro são **AAA**, meta voluntária, não obrigação legal. Os critérios 3.2.6, 3.3.7, 3.3.8,
  2.4.11 e 2.2.6 **não se aplicam**: pressupõem formulário, autenticação, foco de teclado ou
  conjunto de páginas web.

### A métrica

**WCAG 3.1.5** pede conteúdo que não exija leitura acima do *"lower secondary education level"* —
o que, na classificação da UNESCO, corresponde ao 9º ano. O equivalente operacional em português
é o **Flesch adaptado** (Martins, Ghiraldelo, Nunes & Oliveira Jr., ICMSC-USP nº 28, 1996):

```
248,835 − [1,015 × (palavras ÷ frases)] − [84,6 × (sílabas ÷ palavras)]
```

| Faixa | Leiturabilidade | Grau |
|---|---|---|
| 100–75 | muito fácil | 1º a 5º ano |
| **75–50** | **fácil** | **6º a 9º ano** |
| 50–25 | difícil | ensino médio |
| 25–0 | muito difícil | superior |

Alvo do perfil: **≥ 50**. A fórmula foi obtida em fonte secundária (UFRGS/TEXTECC); o original de
1996 está no repositório da USP em digitalização de baixa qualidade, e isso fica declarado.

### Regra editorial

Uma ideia por slide; no máximo **3 parágrafos** de **18 palavras**, **uma frase** cada; corpo a
**30pt**; voz ativa; sem metáfora; número como dígito; sigla expandida na primeira ocorrência
(F10); alinhamento à esquerda, nunca justificado (F04).

> **Divergência declarada.** IFLA aceita fonte com serifa em texto corrido (*"a clear serif type
> (like Times and Garamond) … are good choices"*); Inclusion Europe proíbe (*"Never use serif
> fonts"*). Este projeto segue a Inclusion Europe, por coerência com a regra F01. Não se deve
> apresentar "as diretrizes internacionais" como bloco unânime.

---

## 4. Como se produz

```bash
python scripts/montar_tudo.py roteiro/ -o entrega/ \
    --perfis completo,libras,leitura_facil --libras-por-slide
```

Cada slide do roteiro declara uma `mensagem_chave`. Os perfis derivam dela — o texto reduzido
**não é gerado por resumo automático**, que produziria uma terceira versão do conteúdo com risco
de dizer outra coisa. Quem quiser mais que a mensagem-chave escreve `libras:` ou `facil:` no
slide. Sem `mensagem_chave`, o build **recusa** o perfil, e a mensagem diz por quê: reduzir texto
é trabalho de redação, não de código.

---

## 5. Gerar Libras em escala — o que existe, inclusive pago

A pergunta é justa: capturar a tela de um widget é um recurso de última hora, não uma solução.
O levantamento abaixo foi verificado — endpoints testados ao vivo, imagens Docker abertas byte a
byte, páginas de preço lidas.

| Opção | Faz **Libras**? | Gera arquivo de vídeo? | Em lote / API? | Custo |
|---|---|---|---|---|
| **VLibras auto-hospedado** (`vlibras-video-core:3.4.1`) | **Sim** | **Sim** (frames → mp4) | Sim, você controla o laço | **R$ 0** |
| Endpoint público `/translate` | Sim (só a glosa) | Não | Sim, 300 req/min, 0,2 s | R$ 0, sem login |
| `POST /video` oficial | Sim | Sim | **401 num gateway** | — |
| `video.vlibras.gov.br` | Sim | Sim | Não (web, manual) | Grátis, exige gov.br |
| **Hand Talk** | **Sim** | **Não** — SDK de navegador | Não | Sem preço público |
| **Rybená** | **Sim** | Sim (serviço, ≤ 90 s) | Sem API | Sem preço público |
| Signapse · Kara · SignAll · Silence Speaks | **NÃO** — ASL/BSL/NZSL | Sim | Sim | US$ 1,50–2,00/min |
| **LIBRAS.SE** (intérprete humano) | **Sim** | Sim, ProRes 4444 com alpha | Por contato | **R$ 100–450/min** |

Três conclusões que economizam tempo de quem repetir a busca:

1. **O pelotão de IA fotorrealista não serve.** Signapse, Kara, SignAll e Silence Speaks fazem
   ASL, BSL ou NZSL. **Nenhuma faz Libras.** Isso elimina o mercado internacional inteiro.
2. **Hand Talk faz Libras, mas não entrega arquivo.** É um SDK WebGL com `translate()`, `pause()`,
   `repeat()` — nenhum método para exportar vídeo nem para obter a glosa. Contratá-la trocaria uma
   captura de tela por outra, agora paga.
3. **A qualidade real tem preço, e é humana.** Para ~5 minutos de vídeo, a LIBRAS.SE sai por
   **R$ 500** no prazo de 7 dias, com intérprete certificado.

### A ressalva que o relatório precisa carregar

Avatar com glosa por regras **não tem classificador, expressão facial gramatical nem uso do
espaço de sinalização** — os três são estrutura da língua, não ornamento. O próprio
`video.vlibras.gov.br` desaconselha o uso em *"produções audiovisuais, cursos, aulas,
seminários"*, porque a tradução automática não sincroniza.

Num trabalho **sobre** acessibilidade, o caminho defensável não é escolher entre os dois: é gerar
o material completo pelo pipeline automático e contratar humano para dois ou três trechos,
**documentando a comparação**. O contraste vira conteúdo, e a limitação deixa de ser desculpa
para virar achado.
