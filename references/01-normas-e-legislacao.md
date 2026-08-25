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
condições de falha verificáveis — é exatamente o que o PAC 2024 testa.

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
| **Lei 10.436/2002** + **Decreto 5.626/2005** | Reconhecem a Libras como língua e regulamentam seu uso e difusão | Fundamento da janela de Libras |
| **e-MAG 3.1** | Modelo de Acessibilidade em Governo Eletrônico | Padrão brasileiro de referência para conteúdo digital público |
| **Cartilha de Acessibilidade gov.br, v2.1 (ago/2023)** | Orientação prática de conteúdo acessível na administração federal | Boas práticas em PT-BR |
| **ABNT NBR 15290:2005** | Acessibilidade em comunicação na televisão: legenda oculta, audiodescrição e **janela de Libras** | Parâmetros da janela de Libras |
| **ABNT NBR 16452:2016** | Acessibilidade na comunicação — **audiodescrição** | Diretrizes da faixa de AD |

### Armadilhas de citação — o auditor deve reprovar estas

- **ABNT NBR 17060:2022 não é norma de documentos.** Ela trata de acessibilidade em
  **aplicativos de dispositivos móveis e páginas web** (54 requisitos derivados da WCAG).
  Citá-la como fundamento de um `.pptx` é erro conceitual, e é um erro comum.
- **ABNT NBR 9050 é ambiente construído** (rampas, pisos, sinalização física). Não tem
  qualquer relação com documento digital.
- **WCAG sozinho, sem WCAG2ICT**, é fundamentação incompleta para arquivo não-web.
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
- ABNT NBR 15290:2005 · ABNT NBR 16452:2016
