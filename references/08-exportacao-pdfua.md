# 08 — Exportação e PDF/UA

> A apresentação circula em PDF, não em `.pptx`. Se a semântica não sobreviver à exportação,
> todo o trabalho anterior foi decorativo.
>
> Os resultados abaixo foram **medidos** exportando um arquivo real pelo PowerPoint desta
> máquina e inspecionando o PDF resultante.

---

## 1. A regra que não tem exceção

**"Imprimir para PDF" destrói tudo.** A impressora virtual rasteriza: tags, ordem de leitura,
texto alternativo e estrutura de tabela viram um mosaico de pixels e vetores sem lógica. Para a
tecnologia assistiva, o arquivo passa a ser uma página em branco.

O caminho correto:

- **Windows:** `Arquivo › Salvar uma Cópia` (ou Exportar) › PDF › botão **Opções** › marcar
  **"Marcas de estrutura do documento para acessibilidade"**.
- **macOS:** `Arquivo › Salvar Como` › PDF › escolher **"Melhor para distribuição eletrônica e
  acessibilidade"**. Nunca a opção baseada em Quartz/impressão.

---

## 2. Automatizado, via COM

```python
import win32com.client as w, os

app = w.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(os.path.abspath("deck.pptx"), WithWindow=False)
pres.ExportAsFixedFormat(
    os.path.abspath("deck.pdf"),
    2,      # FixedFormatType: 2 = PDF
    2,      # Intent: qualidade de impressão
    0,      # FrameSlides
    1,      # HandoutOrder
    1,      # OutputType: slides
    0,      # PrintHiddenSlides
    None, 1, "",
    True,   # IncludeDocProperties
    True,   # KeepIRMSettings
    True,   # DocStructureTags  <-- o parâmetro que importa
    True,   # BitmapMissingFonts
    False,  # UseISO19005_1 (PDF/A-1)
)
pres.Close(); app.Quit()
```

`DocStructureTags` é opcional e tem padrão `True`, mas **passe explicitamente**: é a linha que
documenta a intenção e sobrevive a quem editar o script depois.

> Detalhe operacional aprendido na prática: não chame `app.Quit()` entre duas exportações
> reaproveitando o mesmo objeto `Application` — o objeto morre e a chamada seguinte falha com
> `AttributeError`. Abra e feche uma instância por exportação, ou não encerre entre elas.

---

## 3. O que o PowerPoint já entrega — verificado

Inspeção do PDF exportado com `DocStructureTags=True`:

| Chave do catálogo | Valor observado | Regra |
|---|---|---|
| `/MarkInfo` | `{'/Marked': True}` | L01 |
| `/StructTreeRoot` | presente | L04 |
| `/Lang` | **`pt`** | L02 |
| `/ViewerPreferences` | `{'/DisplayDocTitle': True}` | L03 |
| `/Title` nos metadados | **vazio** | L03 |

Duas descobertas que viram regra de auditoria:

1. **`/Lang` sai como `pt`, não `pt-BR`.** É aceitável como código de idioma, mas se o material
   depender da variante brasileira para a síntese de voz, ajuste nas propriedades do documento
   após a exportação.
2. **`/Title` sai vazio quando o `.pptx` não tem `dc:title`.** A falha A01 não fica no `.pptx`:
   ela se propaga e vira a falha L03 no PDF. Com `DisplayDocTitle` já ativo e título vazio, o
   leitor de tela anuncia o nome do arquivo. Corrigir na origem resolve os dois.

---

## 4. O que o PowerPoint não entrega, e precisa de remediação

| Problema | Onde corrigir |
|---|---|
| `TH` exportado sem `/Scope` de linha ou coluna | Acrobat Pro › Ferramenta de Edição de Tabela › Propriedades da Célula › Âmbito |
| Numeração de slide no rodapé virando artefato solto ou sumindo da árvore | Painel de Ordem (ícone Z) do Acrobat |
| Blocos órfãos e hierarquia de títulos quebrada | Percorrer a árvore de tags e reatribuir `H1` a `H6` |
| **Anotações do orador desaparecem** na exportação padrão | Exportar Páginas de Anotações à parte, ou publicar a transcrição linear em `.docx` |

O último ponto é grave neste projeto: as **descrições longas moram nas Notas** (regra D07). Se o
PDF é o único entregável, elas somem. Por isso a transcrição linear (K04) não é um extra — ela é
o que preserva a descrição longa fora do `.pptx`.

---

## 5. Validação

```bash
# conformidade estrita com a ISO 14289 (PDF/UA-1)
verapdf --flavour ua1 deck.pdf

# alternativa em linha de comando
pdfa11y deck.pdf
```

E o **PAC 2024** na interface gráfica, que testa o Protocolo Matterhorn e traz uma
pré-visualização de leitor de tela e a árvore de tags.

Rode os dois: o veraPDF responde "está conforme a norma?"; o PAC responde "é utilizável por
tecnologia assistiva?". As duas perguntas são diferentes, e um PDF pode passar numa e falhar na
outra.

### Verificação rápida em Python

```python
from pypdf import PdfReader
root = PdfReader("deck.pdf").trailer["/Root"]
assert root.get("/MarkInfo", {}).get("/Marked") is True      # L01
assert "/StructTreeRoot" in root                              # L04
assert root.get("/Lang")                                      # L02
assert root.get("/ViewerPreferences", {}).get("/DisplayDocTitle") is True  # L03
```

Isso pega os erros grosseiros em milissegundos, antes de acionar validador pesado. Não substitui
o veraPDF nem o PAC.

---

## 6. Ordem de operações

```
corrigir no .pptx  →  exportar com DocStructureTags  →  verificar no veraPDF e no PAC
        ↑                                                        |
        +------- se falhou, corrigir NA ORIGEM ------------------+
```

Remediar no Acrobat o que podia ter sido corrigido no PowerPoint é dívida técnica: a correção se
perde na próxima exportação. Acrobat é para o que **só** existe no PDF — `/Scope`, ordem de
artefatos de rodapé, tags órfãs da própria conversão.
