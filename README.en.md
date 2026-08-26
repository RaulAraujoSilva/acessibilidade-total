# Acessibilidade Total (Total Accessibility)

[![testes](https://github.com/RaulAraujoSilva/acessibilidade-total/actions/workflows/testes.yml/badge.svg)](https://github.com/RaulAraujoSilva/acessibilidade-total/actions/workflows/testes.yml)
[![licence MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)

**Builds and audits accessible presentations** — PowerPoint `.pptx` and PDF/UA — against
WCAG 2.2 AA (through WCAG2ICT), ISO 14289, Brazil's Inclusion Act (Law 13.146/2015) and
e-MAG.

Works as a Claude Code skill **and** as a standalone command-line tool.

*[Versão em português](README.md)* — the reference material is written in Brazilian
Portuguese.

> **Status:** catalogue, auditor, deck builder, simulator, transcript, diagrams and
> PDF/UA export are done and tested. Narrated audio description and the sign
> language window are in progress.

---

## Getting started from scratch

You do not need to know how to program. Three steps.

### Windows

```powershell
git clone https://github.com/RaulAraujoSilva/acessibilidade-total
cd acessibilidade-total
.\instalar.ps1
```

The installer finds Python (and offers to install it), creates an isolated environment
inside the folder — **it does not touch your system Python** — and installs the libraries.
Then it **asks**, one by one, about the optional tools. Nothing system-wide is installed
without your confirmation.

To audit a file, **drag the `.pptx` onto `auditar.bat`**. The report opens by itself.

### macOS and Linux

```bash
git clone https://github.com/RaulAraujoSilva/acessibilidade-total
cd acessibilidade-total
./instalar.sh
.venv/bin/python scripts/audit_pptx.py deck.pptx --md report.md
```

The auditor runs anywhere. Only tagged-PDF export requires Windows, since it drives an
installed PowerPoint.

### I only want to audit

```powershell
.\instalar.ps1 -SomenteAuditor
```

Installs **one** library. That is enough.

### I don't know what I have installed

```bash
python scripts/verificar_ambiente.py
```

Lists everything, and for each missing item states **what it is for**, **what stops working
without it**, and **the exact install command**.

### As an agent skill

`Agent Skills` is an **open specification** (agentskills.io), created by Anthropic and
adopted by around 40 products. The same folder works in all of them — only the
destination directory changes:

| Agent | Where to copy the folder |
|---|---|
| Claude Code | `~/.claude/skills/acessibilidade-total/` |
| Codex, Cursor, Copilot, Gemini CLI and others | `~/.agents/skills/acessibilidade-total/` |
| Scoped to one repository | `.agents/skills/acessibilidade-total/` inside it |

The folder name must match the `name` field in `SKILL.md`. After that, just ask in
plain language: *"audit this presentation and tell me what to fix"*.

### The whole pipeline in one command

```bash
python scripts/montar_tudo.py roteiro-folder/ -o delivery/
```

Seven stages, each with a gate: diagrams, build, `.pptx` audit, simulated reading,
transcript, tagged PDF, veraPDF validation. The third gate **stops** the pipeline on
any Error or Warning — exporting a PDF from a failing file only propagates the defect.

---

## What each dependency does

The principle: **nothing is required beyond the essential**. Each missing piece disables one
capability, never the whole.

| Package | What it does | Without it |
|---|---|---|
| **python-pptx** | Reads and writes the `.pptx`. Pulls in `lxml`, `Pillow`, `XlsxWriter` | **The auditor will not run.** The only truly required one |
| **pywin32** | Drives installed PowerPoint to export PDF **with structure tags** — the only method that preserves accessibility. Windows only | No automated accessible PDF export |
| **pypdf** | Inspects the produced PDF: `/Lang`, `/Title`, `/MarkInfo`, tag tree | Cannot verify the exported PDF (layer L) |
| **PyMuPDF** | Extracts text and images from a source PDF to become a slide outline | No document-to-deck conversion |
| **python-docx** | Writes the linear transcript as `.docx` with real heading styles | No transcript (rule K04) |
| **openai** | Generates illustrations with gpt-image-2. Needs `OPENAI_API_KEY` | No generated figures |
| **requests** | HTTP for audio description (ElevenLabs) and VLibras | No narrated AD, no sign-language window |
| **playwright** | Drives Chrome to capture the VLibras avatar on video | No automated sign-language window |

External programs — all optional: **Docker** (runs veraPDF with no Java), **ffmpeg** (video
assembly), **PAC** (`winget install axes4.PAC`), **Colour Contrast Analyser**
(`winget install TPGi.CCAe`), **NVDA** (`winget install NVAccess.NVDA`).

---

## "Do I need to install NVDA? I'm not blind."

**No.** NVDA is not needed to build, convert or audit. It covers **one** catalogue item:
rule **K03**, the evidence that reading order works in practice. It is a measuring
instrument, not a production tool.

And it does not have to speak. How a sighted tester uses it: press `NVDA+S` until it reaches
**no speech**, then open the NVDA menu › Tools › **Speech Viewer**, which displays as text
everything that would be spoken. Leave NVDA with `Insert+Q`.

If you would rather install nothing, use the automated substitute:

```bash
python scripts/simular_leitura.py deck.pptx
```

It writes what a screen reader would announce, in the order it would announce it. That is a
**model** of the behaviour, not the behaviour — it does not satisfy K03, but it makes reading
order reviewable before the real test.

---

## Why it exists

PowerPoint's built-in Accessibility Checker covers **10 rules**. It does not look at font
size, justified text, line spacing, the language tag on individual text runs, text over
photographs, colour used as the only carrier of meaning, colour blindness, alt text
*quality* (it accepts `photo1.png` as a valid description), long descriptions, "click here"
links, animation, target size, sign language, audio description, or anything in the exported
PDF.

This repository is the missing part: **108 auditable rules**, each with a stable ID, a
severity, its source criterion, how to detect it and how to fix it.

---

## Findings that motivated the project

- **The raw Okabe-Ito palette fails WCAG 1.4.11 on a light background.** Yellow measures
  1.24:1, orange 2.11:1, sky blue 2.16:1 — against a 3:1 minimum. Only three of eight pass.
  Pre-computed darkened variants ship with the repo.
- **The exported PDF's `/Title` comes out empty** when the `.pptx` has no title in its
  document properties — and since `DisplayDocTitle` is on, screen readers fall back to the
  file name.
- **The exported PDF's `/Lang` comes out as `pt`, not `pt-BR`.**
- **The native checker cannot be automated**: no object model returns its results.
- **`.pptx` has no runtime palette switching.** The macro-free answer is a hub slide backed
  by Custom Shows.
- **ABNT NBR 17060 covers mobile applications**, not documents — a frequent miscitation.
  NBR 17225:2025 is likewise web-scoped.
- **The current edition of ABNT NBR 15290 is 2016** (reconfirmed 11 Dec 2025), yet the
  edition circulating online is the superseded 2005 one.

---

## How this is tested

Two tests in opposite directions, because an auditor that flags everything is as useless as
one that flags nothing:

| Test | Question | Result |
|---|---|---|
| `test_auditor.py` | Does it see what was planted? | **33/33** defects detected |
| `test_falso_positivo.py` | Does it stay quiet on correct input? | **0** false positives |

CI runs both on Ubuntu and Windows, Python 3.9 and 3.12, installing **only `python-pptx`** —
so if any script starts requiring more, CI breaks before the clone does.

---

## Principles

1. One artefact for everyone — universal design, not one version per disability.
2. Structure before aesthetics.
3. Silence is a feature: decorative objects are marked decorative.
4. Model output is not a deliverable — every generated description is human-reviewed.
5. Absence of evidence is not conformance.
6. Degrading is allowed; degrading silently is not.

---

## Origin

Built for an assignment in **TCE 00191 — Accessible Documents**, a doctoral course in
Production Engineering at Universidade Federal Fluminense, Brazil. Published for anyone who
needs to produce genuinely accessible material rather than merely pass a checker.

## Licence

MIT. Contributions welcome — especially corrections from disabled people using material
produced with this tool.
