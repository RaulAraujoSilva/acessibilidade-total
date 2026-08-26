# 01 — Normas e legislação aplicáveis

> Para que serve este arquivo: dar ao autor e ao auditor a **fundamentação correta**, e impedir
> as citações erradas que são endêmicas em trabalhos de acessibilidade documental.

---

## 1. A cadeia normativa técnica

### WCAG 2.2 (W3C, outubro/2023)
Base de tudo. Quatro princípios (**POUR**): Perceptível, Operável, Compreensível, Robusto.
Nível de conformidade alvo padrão: **AA**. Esta skill mira AA como piso e AAA onde for barato
(contraste de texto, principalmente).

Critérios que mais aparecem em apresentações:

| CS | Nome | Onde morde num slide |
|---|---|---|
| 1.1.1 | Conteúdo não textual | Alt text de toda imagem, ícone, gráfico, SmartArt |
| 1.3.1 | Informações e relações | Placeholders, cabeçalho de tabela, listas nativas |
| 1.3.2 | Sequência com significado | Ordem de leitura (z-order) |
| 1.4.1 | Uso da cor | Legenda de gráfico só por cor = falha |
| 1.4.3 | Contraste (mínimo) | 4,5:1 normal · 3:1 texto grande |
| 1.4.4 | Redimensionar texto | Texto como imagem não escala |
| 1.4.5 | Imagens de texto | Print de tabela em vez de tabela real |
| 1.4.6 | Contraste (melhorado, AAA) | 7:1 normal · 4,5:1 grande |
| 1.4.11 | Contraste não textual | Barras, linhas, ícones, bordas: 3:1 |
| 2.2.2 | Pausar, parar, ocultar | GIF/vídeo em loop com autoplay > 5 s |
| 2.3.1 | Três flashes | Transições piscantes |
| 2.4.2 | Título da página | Título do slide e `dc:title` do arquivo |
| 2.4.4 | Finalidade do link | "clique aqui" e URL crua |
| 2.4.11 / 2.4.12 | Foco não obscurecido | Botões do hub cobertos por outro objeto |
| 2.4.13 | Aparência do foco | Indicador de foco com 3:1 e espessura mínima |
| 2.5.7 | Movimentos de arrastar | Interação que exige arrastar |
| 2.5.8 | Tamanho do alvo | Alvo de clique mínimo 24×24 px CSS |
| 3.1.1 / 3.1.2 | Idioma da página / de partes | `lang` do documento e dos trechos em outra língua |
| 3.3.7 | Entrada redundante | Formulário/macro pedindo o mesmo dado duas vezes |

### WCAG2ICT
**É a peça que autoriza aplicar WCAG a um `.pptx`.** As WCAG foram escritas para a web; o
WCAG2ICT é o documento do W3C que traduz cada critério para software e documentos não-web.
Sem citá-lo, aplicar WCAG a um arquivo do PowerPoint fica sem base formal.
Versão corrente: `wcag2ict-22`.

### ISO 14289-1 — PDF/UA
Padrão de acessibilidade do PDF. É o destino final do deck quando ele vira PDF.
Operacionalizado na prática pelo **Protocolo Matterhorn** (PDF Association), que lista as
condições de falha verificáveis — é exatamente o que o PAC testa.

### EN 301 549 (Europa) e Section 508 (EUA)
Ambas incorporam WCAG por referência. Relevantes quando o material circula fora do Brasil ou
em organismo internacional. A Section 508 mantém guias e checklists específicos de PowerPoint
em `section508.gov`, úteis como segunda opinião ao catálogo de auditoria.

---

## 2. A cadeia legal brasileira

| Norma | O que estabelece | Uso no deck |
|---|---|---|
| **Lei 13.146/2015 (LBI / Estatuto da Pessoa com Deficiência)** | Acessibilidade como direito; define formatos acessíveis como os reconhecíveis por leitor de tela e tecnologias assistivas | Fundamento jurídico principal |
| Lei 10.098/2000 | Normas gerais de acessibilidade | Fundamento anterior à LBI |
| **Lei 10.436/2002** + **Decreto 5.626/2005** | Reconhecem a Libras como língua e regulamentam seu uso e difusão. **Dec. art. 24**: a *programação visual* de cursos deve ter janela de Libras — melhor âncora que a NBR 15290 para material de ensino. **Lei art. 4º pu**: a Libras não pode *substituir* o português escrito | Fundamento da janela e da versão Libras-first |
| **LBI, art. 28, IV** | *"Libras como primeira língua e na modalidade escrita da língua portuguesa como segunda língua"* | Fundamento do perfil `libras`: para a pessoa surda, o português é L2 |
| **LBI, art. 3º, V** + **Lei 14.129/2021, art. 3º, VII** | Põem *linguagem simples* na definição legal de comunicação e *linguagem clara e compreensível* como princípio | Fundamento do perfil `leitura_facil` |
| **e-MAG 3.1** | Modelo de Acessibilidade em Governo Eletrônico | Padrão brasileiro de referência para conteúdo digital público |
| **Cartilha de Acessibilidade gov.br, v2.1 (ago/2023)** | Orientação prática de conteúdo acessível na administração federal | Boas práticas em PT-BR |

### Normas ABNT — situação verificada no acervo do CB-040

Conferido em 25/08/2026 no acervo **ABNT Coleção / MPF**
(`abntcolecao.com.br/mpf/grid.aspx`), que reúne **45 normas de acessibilidade** com o texto
integral disponível. Todas as edições abaixo constam como **Em Vigor**.

| Norma | Título | Situação | Uso no deck |
|---|---|---|---|
| **ABNT NBR 15290:2016** | Acessibilidade em comunicação na televisão | 19/12/2016, confirmada em 11.12.2025, 19 p. | **Parâmetros da janela de Libras** |
| **ABNT NBR 16452:2016** | Acessibilidade na comunicação — audiodescrição | 01/09/2016 | Diretrizes da faixa de AD |
| **ABNT NBR 15610-3:2016** | TV digital terrestre — Acessibilidade — Parte 3: Língua de Sinais (LIBRAS) | 15/12/2016 | Norma específica de Libras; complementa a 15290 |
| **ABNT NBR 15610-1:2011** e **15610-2:2012** | TV digital — Ferramentas de texto · Funcionalidades sonoras | Em vigor | Legendagem e áudio |
| **ABNT NBR 15599:2008** | Acessibilidade — Comunicação na prestação de serviços | Confirmada em 23.08.2023, 39 p. | Aplica-se ao contexto de **aula, palestra e evento**, não só ao arquivo |
| **ABNT NBR ISO 24495-1:2024** | Linguagem Simples — Parte 1: Princípios e diretrizes norteadores | 25/07/2024 | Acessibilidade cognitiva do texto dos slides |
| **ABNT NBR 17225:2025** | Acessibilidade em conteúdo e aplicações web — Requisitos | 11/03/2025, 69 p. | Expressão normativa brasileira das diretrizes WCAG — **escopo web**, ver ressalva abaixo |

> **Atenção à edição.** A NBR 15290 circula muito na internet na **primeira edição, de 2005**
> (há PDF integral no portal do CNMP). Essa edição está **superada** pela de 2016. Ao citar,
> escrever `ABNT NBR 15290:2016`. Os parâmetros dimensionais da janela de Libras, lidos no texto
> integral da edição de 2005 (item 7.1.3) e corroborados por fontes secundárias para a edição de
> 2016, seguem descritos em `06-libras.md`.

### Armadilhas de citação — o auditor deve reprovar estas

- **ABNT NBR 17060:2022 não é norma de documentos.** Ela trata de acessibilidade em
  **aplicativos de dispositivos móveis** (54 requisitos derivados da WCAG). Citá-la como
  fundamento de um `.pptx` é erro conceitual, e é um erro comum.
- **ABNT NBR 17225:2025 também é de escopo web**, não de documento. É a norma brasileira certa
  para *site*; para um `.pptx` o caminho normativo continua sendo WCAG 2.2 + WCAG2ICT. Citá-la
  como contexto é correto; citá-la como requisito aplicável ao arquivo, não.
- **ABNT NBR 9050 é ambiente construído** (rampas, pisos, sinalização física). Não tem
  qualquer relação com documento digital.
- **Citar a NBR 15290 como "de 2005"** — a edição vigente é a de **2016**.
- **WCAG sozinho, sem WCAG2ICT**, é fundamentação incompleta para arquivo não-web.
- **"Versão alternativa em conformidade" (WCAG) não vale para Libras.** A definição exige que a
  alternativa entregue a mesma informação *"in the same human language"* — Libras é outra língua.
  O critério WCAG sobre sinais é o 1.2.6 (AAA), e ele cobre áudio pré-gravado, não slide.
- **WCAG 3.2.6, 3.3.7, 3.3.8, 2.4.11 e 2.2.6 não se aplicam a documento estático.** Pressupõem
  formulário, autenticação, foco de teclado ou conjunto de páginas web. Para texto de documento
  valem 1.4.8, 3.1.3, 3.1.4 e 3.1.5 — e os quatro são **AAA**, meta voluntária.
- **Linguagem Simples não é Leitura Fácil**, e quem diz é a própria NBR ISO 24495-1:2024. Não há
  norma brasileira de Leitura Fácil; a referência é Inclusion Europe e IFLA.
- **A ISO 24495-1 exclui acessibilidade do próprio escopo** (item 1). Ela fundamenta a redação,
  não a conformidade.
- **A ISO 24495-1 é de 2023**; a adoção brasileira, NBR ISO 24495-1, é de **2024**. Escrever
  "ISO 24495-1:2024" mistura as duas.
- **W3C COGA não é norma** — é *Working Group Note*, e o próprio documento diz que não implica
  endosso do W3C. Cite como boa prática.
- **"Conformidade com a LBI"** não é um selo técnico verificável: a LBI é o dever legal;
  a verificação técnica se faz contra WCAG 2.2 AA + PDF/UA. Escrever "conforme a LBI" sem
  apontar o critério técnico é retórica, não auditoria.

---

## 3. Como citar no próprio deck

O slide de acessibilidade do deck deve declarar, de forma verificável:

1. Nível alvo (ex.: "WCAG 2.2 nível AA, via WCAG2ICT") e o que ficou em AAA.
2. Recursos entregues: alt text, ordem de leitura, audiodescrição, janela de Libras,
   transcrição, modos de cor, PDF/UA.
3. **O que não foi possível entregar** e por quê. Uma declaração de acessibilidade que só
   lista acertos é propaganda; a que lista as lacunas é documento técnico.

---

## Fontes

- WCAG 2.2 — https://www.w3.org/TR/WCAG22/ · tradução pt-BR: https://www.w3c.br/traducoes/wcag/wcag22-pt-BR/
- WCAG2ICT — https://www.w3.org/TR/wcag2ict-22/
- Section 508, presentations — https://www.section508.gov/create/presentations/
- LBI — Lei 13.146/2015, Planalto
- Cartilha gov.br de acessibilidade digital, v2.1
- **ABNT Coleção / MPF** — https://www.abntcolecao.com.br/mpf/grid.aspx — acervo com 45 normas
  de acessibilidade do CB-040, com texto integral disponível. É a via correta para conferir
  **edição vigente e data de confirmação** antes de citar qualquer NBR. O texto integral abre
  no visualizador próprio da ABNT; a ficha de cada norma (edição, páginas, objetivo, status)
  é consultável direto na página.
- ABNT NBR 15290:2016 · 16452:2016 · 15610-3:2016 · 15599:2008 · ISO 24495-1:2024 · 17225:2025
