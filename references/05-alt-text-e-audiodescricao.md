# 05 — Texto alternativo, descrição longa e audiodescrição

> Três camadas distintas, com funções distintas. Confundi-las é o erro mais comum.

| Camada | Onde vive | Extensão | Responde |
|---|---|---|---|
| **Alt text** | `descr` do objeto | 1 a 2 frases, ~150 caracteres | *Por que esta imagem está aqui?* |
| **Descrição longa** | Anotações do orador | Sem limite | *O que exatamente ela mostra?* |
| **Audiodescrição** | Faixa de áudio + transcrição | Roteirizada | *O que se vê, narrado no tempo* |

---

## 1. Alt text

### O método

1. Pergunte **por que a imagem está no slide**. A resposta é o alt text.
2. Escreva a conclusão, não o inventário visual.
3. Corte "Imagem de", "Foto de", "Gráfico de" — o leitor de tela já anuncia o tipo do objeto, e
   o prefixo produz a redundância irritante "imagem, imagem de um carro".
4. Fique abaixo de ~150 caracteres.
5. Se não couber, o alt text carrega a **conclusão** e remete: o detalhe vai para as Notas.

### Antes e depois

| Ruim | Por quê | Bom |
|---|---|---|
| `grafico_receita_v3.png` | Nome de arquivo (D03) | `Queda de 32% na receita do terceiro trimestre` |
| `Gráfico com linhas azuis e fundo branco. Descrição gerada automaticamente` | Resíduo de IA, sem informação (D05) | `Receita cai a partir de julho e não recupera até dezembro` |
| `Imagem de um fluxograma` | Prefixo e vazio (D04) | `Fluxo de quatro etapas, da solicitação ao arquivamento` |
| `Foto ilustrativa` | Se é só ilustração, não descreva | Marcar como decorativo (C03) |

### Decorativo ou descrito?

Marque como **decorativo** quando a imagem não acrescenta informação: linha separadora, moldura,
textura de fundo, foto de banco de imagens usada como enfeite. Silêncio é um recurso de
acessibilidade — obrigar alguém a ouvir "imagem, foto de pessoas sorrindo em escritório" a cada
slide é ruído, não inclusão.

Descreva quando a imagem **carrega informação que o texto do slide não repete**.

Se a imagem repete literalmente o que o slide já diz em texto, ela é decorativa — descrevê-la
faz o leitor de tela dizer tudo duas vezes.

### A armadilha da IA

O Microsoft 365 gera alt text automático por visão computacional e marca o resultado com
"Descrição gerada automaticamente". Essas descrições são literais e sem contexto. A intervenção
humana é obrigatória: reescreva **e apague o aviso**, senão o próprio verificador continua
sinalizando. Vale igualmente para descrições geradas por qualquer modelo, inclusive as deste
projeto — toda descrição gerada passa pela camada M05 antes da entrega.

---

## 2. Descrição longa

Vai nas **Anotações do orador**, onde o leitor de tela chega com `Ctrl+Shift+S`. É o lugar certo
para gráfico com muitos dados, diagrama com muitos nós, tabela renderizada como figura.

Estrutura que funciona:

1. **O que é** — tipo de representação e o que está sendo comparado.
2. **Como está organizada** — eixos, unidades, período, número de séries.
3. **Os dados** — os valores que importam, em texto corrido ou lista.
4. **A conclusão** — o que se deve concluir daquilo.

> Exemplo. Alt text: `Receita cai 32% no terceiro trimestre e não recupera`.
> Descrição longa: `Gráfico de linhas com a receita mensal de janeiro a dezembro de 2025, em
> milhões de reais. Uma única série. Janeiro 4,2; fevereiro 4,4; ... julho 4,1; agosto 2,9;
> setembro 2,8; ... dezembro 2,9. A queda concentra-se entre julho e agosto e o patamar
> posterior permanece estável, sem retomada.`

**Toda figura gerada por IA neste projeto entra no deck com o par alt text + descrição longa
escrito no mesmo passo da geração.** Figura sem o par não entra — é regra do pipeline, não
recomendação.

---

## 3. Audiodescrição

Referência: **ABNT NBR 16452** — audiodescrição é a narração suplementar dos elementos visuais
que não se compreendem apenas pelo áudio principal.

### Princípios de roteiro

- Descrever **o que se vê**, não o que se interpreta. "Ele cerra os punhos", não "ele fica
  furioso".
- Ordem: do geral ao particular, seguindo a leitura visual.
- Presente do indicativo, terceira pessoa, frases curtas.
- Não competir com a fala: a AD ocupa os silêncios.
- Não antecipar o que a narração principal vai dizer em seguida.
- Vocabulário do domínio do conteúdo, sem infantilizar.

### Neste projeto

Uma faixa por slide, gerada a partir da descrição longa já escrita, com a voz PT-BR configurada
(ElevenLabs). Entregue de duas formas, porque nenhuma sozinha atende a todos:

1. Áudio embutido no slide, com controle de reprodução — nunca em autoplay (I04).
2. Arquivos `.mp3` numerados por slide, mais a **transcrição em texto** — surdocegos usam a
   transcrição em linha braille, e a transcrição também é o que torna a AD auditável.

> Audiodescrição sem transcrição não é auditável e exclui quem usa braille. As duas andam
> juntas.

---

## 4. Transcrição linear do deck

Um `.docx` com estilos de título reais (Título 1 por slide), o texto de cada slide, o alt text,
a descrição longa e a indicação das mídias. É o que permite ler a apresentação inteira de forma
linear, e é também o material de estudo de quem não vai assistir à exposição oral.

---

## 5. Ordem de trabalho recomendada

```
figura gerada  →  alt text (≤150)  →  descrição longa (Notas)
                                    →  roteiro de AD  →  áudio + transcrição
                                    →  entra na transcrição linear
```

Escrever nesta ordem evita o retrabalho de descrever a mesma figura quatro vezes com quatro
níveis de detalhe incompatíveis entre si.
