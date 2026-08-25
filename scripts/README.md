# scripts

| Arquivo | Estado | O que faz |
|---|---|---|
| `a11y_lib.py` | pronto | Acesso ao que o `python-pptx` não expõe: alt text, marca de decorativo, ordem de leitura, idioma dos runs, herança de tamanho de fonte, tabelas, seções |
| `audit_contrast.py` | pronto | Resolve cor efetiva (tema + `clrMap` + `lumMod`/`lumOff`/`tint`/`shade`) e calcula contraste WCAG |
| `audit_pptx.py` | pronto | Auditor estático das camadas A a I; camadas J a M saem como *não verificado* |
| `export_pdfua.py` | a fazer | Exportação COM com `DocStructureTags=True` |
| `audit_pdf.py` | a fazer | Validação PDF/UA (veraPDF, PAC) |
| `build_deck.py` | a fazer | Constrói o deck acessível por construção |
| `gen_images.py` | a fazer | Figuras via gpt-image-2, com alt text e descrição longa no mesmo passo |
| `gen_audiodesc.py` | a fazer | Audiodescrição narrada + transcrição |
| `gen_libras.py` | a fazer | Janela de Libras via VLibras |
| `gen_transcricao.py` | a fazer | Transcrição linear em `.docx` acessível |

## Auditar um arquivo

```bash
python scripts/audit_pptx.py deck.pptx --md relatorio.md --json achados.json
```

Sai com código 1 se houver Erro ou Aviso em aberto — serve direto em CI.

O relatório traz, por regra: `ID · severidade · critério · onde · detalhe`, mais a
**lista explícita do que não foi verificado**. Ausência de evidência não é conformidade.
