# 04 — Cookbook OOXML

> Onde cada recurso de acessibilidade mora dentro do `.pptx`. **Todos os trechos abaixo foram
> extraídos de arquivos reais gerados pelo PowerPoint nesta máquina**, não de memória.
>
> Namespaces usados:
> `a` = `http://schemas.openxmlformats.org/drawingml/2006/main` ·
> `p` = `http://schemas.openxmlformats.org/presentationml/2006/main` ·
> `adec` = `http://schemas.microsoft.com/office/drawing/2017/decorative`

---

## 1. Texto alternativo

Vive no atributo **`descr`** de `p:cNvPr`. O atributo `title` existe, mas leitores de tela o
ignoram na prática — **descreva sempre em `descr`**.

```xml
<p:cNvPr id="5" name="Diagrama" descr="Fluxo de tres etapas do processo"/>
```

**Ler (`python-pptx` não expõe isto na API pública):**

```python
def get_alt(shape):
    return shape._element._nvXxPr.cNvPr.get("descr", "")

def set_alt(shape, texto):
    shape._element._nvXxPr.cNvPr.set("descr", texto)
```

`_nvXxPr` funciona para `p:sp`, `p:pic`, `p:graphicFrame` e `p:grpSp`.

**Via COM (PowerPoint aberto):** `shape.AlternativeText = "..."`.

---

## 2. Marcar como decorativo — verificado

Não é um atributo, é uma **extensão** dentro de `p:cNvPr/a:extLst`, com URI fixa:

```xml
<p:cNvPr id="4" name="Faixa decorativa">
  <a:extLst>
    <a:ext uri="{FF2B5EF4-FFF2-40B4-BE49-F238E27FC236}">
      <a16:creationId xmlns:a16="http://schemas.microsoft.com/office/drawing/2014/main"
                      id="{F86E1011-D7AE-4BAE-E27B-F092179FBC20}"/>
    </a:ext>
    <a:ext uri="{C183D7F6-B498-43B3-948B-1728B52AA6E4}">
      <adec:decorative xmlns:adec="http://schemas.microsoft.com/office/drawing/2017/decorative"
                       val="1"/>
    </a:ext>
  </a:extLst>
</p:cNvPr>
```

- URI da extensão decorativa: **`{C183D7F6-B498-43B3-948B-1728B52AA6E4}`**
- A outra `a:ext`, `{FF2B5EF4-...}`, é apenas o `creationId` do PowerPoint — irrelevante para
  acessibilidade, mas **não a remova**: ela convive na mesma `a:extLst`.

**Via COM:** `shape.Decorative = True` — confirmado disponível no Office 365 desta máquina, e é
o caminho mais seguro, porque o PowerPoint escreve a extensão exatamente como espera lê-la.

**Detectar no auditor:**

```python
NS_DEC = "http://schemas.microsoft.com/office/drawing/2017/decorative"
def is_decorative(shape):
    cNvPr = shape._element._nvXxPr.cNvPr
    return any(e.get("val") == "1" for e in cNvPr.iter(f"{{{NS_DEC}}}decorative"))
```

> Regra D11: decorativo **e** `descr` preenchido ao mesmo tempo é contradição — o objeto está
> dizendo "me ignore" e "me leia" simultaneamente.

---

## 3. Título do slide e ordem de leitura

O título é o `p:sp` cujo `p:nvSpPr/p:nvPr/p:ph` tem `type="title"` ou `type="ctrTitle"`.

```xml
<p:ph type="title"/>
```

**A ordem de leitura é a ordem dos filhos de `p:spTree`.** Primeiro filho = primeiro anunciado.
Não existe atributo de ordem: reordenar significa mover o elemento no XML.

```python
spTree = slide.shapes._spTree
ordem = [sp for sp in spTree.iterchildren()
         if sp.tag.endswith(('}sp', '}pic', '}graphicFrame', '}grpSp', '}cxnSp'))]
```

Painel de Ordem de Leitura mostra esta lista **de cima para baixo**; o Painel de Seleção mostra
a **mesma lista invertida**. Mover no XML muda os dois — e muda a camada visual junto.

**Título oculto sem apagar:** ou se move o *placeholder* para fora da tela (`a:off` com `x`
negativo), ou se marca `hidden`:

```xml
<p:cNvPr id="2" name="Título 1" hidden="1"/>
```

---

## 4. Idioma

Idioma do documento, em `docProps/core.xml`:

```python
prs.core_properties.language = "pt-BR"
prs.core_properties.title = "Título descritivo da apresentação"
prs.core_properties.author = "Nome do autor"
```

Idioma de cada trecho de texto, no atributo `lang` de `a:rPr` — é aqui que mora a falha A03,
porque instalações em inglês marcam todo texto como `en-US` e o leitor de tela lê português com
fonética inglesa:

```xml
<a:r><a:rPr lang="pt-BR" sz="2400" dirty="0"/><a:t>Texto do slide</a:t></a:r>
```

Também conferir `a:endParaRPr` e os `a:defRPr` do layout e do master.

---

## 5. Tabelas

```xml
<a:tbl>
  <a:tblPr firstRow="1" bandRow="1"/>
  <a:tblGrid>...</a:tblGrid>
  <a:tr h="370840">
    <a:tc><a:txBody>...</a:txBody><a:tcPr/></a:tc>
  </a:tr>
</a:tbl>
```

| O que | Onde | Regra |
|---|---|---|
| Linha de cabeçalho | `a:tblPr/@firstRow="1"` | G01 |
| Primeira coluna como rótulo | `a:tblPr/@firstCol="1"` | G02 |
| Mesclagem horizontal | `a:tc/@gridSpan` maior que 1, e `@hMerge="1"` nas células absorvidas | G03 |
| Mesclagem vertical | `a:tc/@rowSpan` maior que 1, e `@vMerge="1"` | G03 |

Em `python-pptx`: `table.first_row = True` e `table.first_col = True`.

---

## 6. Tipografia

```xml
<a:pPr algn="just" marL="0" indent="0">
  <a:lnSpc><a:spcPct val="150000"/></a:lnSpc>
  <a:buChar char="•"/>
</a:pPr>
<a:rPr lang="pt-BR" sz="1800" b="1" i="1" u="sng"/>
```

| Propriedade | Atributo | Valor a exigir |
|---|---|---|
| Tamanho | `a:rPr/@sz` | centésimos de ponto: `1800` = 18pt (F02) |
| Negrito / itálico / sublinhado | `@b` / `@i` / `@u` | `i="1"` em bloco reprova (F06) |
| Alinhamento | `a:pPr/@algn` | `just` reprova (F04) |
| Entrelinha | `a:lnSpc/a:spcPct/@val` | mínimo `150000` (F05) |
| Marcador nativo | `a:buChar`, `a:buAutoNum` | ausência com hífen digitado reprova (B09) |
| Fonte | `a:latin/@typeface` | conjunto seguro (F01) |

> **Atenção à herança.** `sz` costuma estar ausente no slide e vir do *placeholder* no layout,
> e deste no master. Um auditor que só olha o slide dá falso negativo em F02 e falso positivo em
> E01. A cadeia a percorrer é: `a:rPr` do run → `a:pPr/a:defRPr` do parágrafo → `p:txStyles` do
> *placeholder* no layout → o mesmo no master → `p:defaultTextStyle` da apresentação.

---

## 7. Cores e o tema

Cor pode aparecer de duas formas:

```xml
<a:solidFill><a:srgbClr val="1A1A1A"/></a:solidFill>
<a:solidFill><a:schemeClr val="tx1"><a:lumMod val="75000"/></a:schemeClr></a:solidFill>
```

Para calcular contraste é preciso **resolver o tema**: ler `ppt/theme/theme1.xml`,
`a:clrScheme` (`dk1`, `lt1`, `dk2`, `lt2`, `accent1..6`, `hlink`, `folHlink`), mapear o alias do
slide (`p:clrMapOvr` / `p:clrMap`: `tx1` → `dk1`, `bg1` → `lt1` e assim por diante) e então
aplicar os modificadores na ordem em que aparecem: `lumMod`, `lumOff`, `tint`, `shade`, `alpha`.

Ignorar os modificadores é o erro mais comum de auditor de contraste caseiro: `tx1` com
`lumMod 75000` sobre `bg1` não é 21:1, é bem menos.

---

## 8. Mídia, animação e transição

| O que | Onde |
|---|---|
| Vídeo/áudio | `p:pic` com `p:nvPr/a:videoFile` ou `a:audioFile` |
| Legenda WebVTT | parte do pacote relacionada ao vídeo, tipo `application/vnd.ms-powerpoint.subtitle` |
| Autoplay e loop | `p:mediaNode` em `p:timing`; atributos de reprodução |
| Animações | `p:timing/p:tnLst`, com `p:animEffect` e `p:anim` |
| Transição do slide | `p:transition` no `p:sld` |

Para I06, basta inventariar os `p:animEffect` e `p:transition` e confrontar com o conjunto
permitido (fade, appear).

---

## 9. Seções

Extensão no `presentation.xml`:

```xml
<p14:sectionLst xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main">
  <p14:section name="Modo padrão" id="{...}">
    <p14:sldIdLst><p14:sldId id="256"/></p14:sldIdLst>
  </p14:section>
</p14:sectionLst>
```

Nome padrão (`Seção Padrão`, `Seção 1`) reprova em B07; nomes repetidos, em B08.

---

## 10. Apresentações Personalizadas

```xml
<p:custShowLst>
  <p:custShow name="Modo daltônico-seguro" id="0">
    <p:sldLst><p:sld r:id="rId7"/><p:sld r:id="rId8"/></p:sldLst>
  </p:custShow>
</p:custShowLst>
```

Via COM: `Presentation.SlideShowSettings.NamedSlideShows.Add(nome, indices)`.

> **Registro de uma promessa que o código não cumpria.** Este projeto documentou por um tempo
> que os modos de cor eram "três seções, cada uma registrada como Apresentação Personalizada".
> `p:custShowLst` nunca foi gravado — a navegação era só por Seções (§9), e os cartões do hub
> não tinham hiperlink nenhum. Hoje os modos são **arquivos separados** e nada disso é usado
> por padrão; a receita fica porque continua sendo OOXML válido para quem precisar.

---

## 11. Armadilhas do `python-pptx`

| Precisa | Situação |
|---|---|
| Alt text | Não exposto — acessar `cNvPr.get("descr")` |
| Decorativo | Não exposto — manipular `a:extLst`, ou usar COM |
| Ordem de leitura | Não exposta — reordenar filhos de `p:spTree` |
| Seções | Não expostas — manipular `p14:sectionLst` |
| Apresentações personalizadas | Não expostas — COM |
| Legenda de vídeo | Não exposta — COM |
| `core_properties` | **Exposto**: `title`, `author`, `language`, `subject`, `keywords` |
| `table.first_row` / `first_col` | **Exposto** |

Onde `python-pptx` não chega, o caminho confiável é o COM do PowerPoint instalado — ele escreve
o XML no formato que ele mesmo espera ler.
