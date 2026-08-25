# Acessibilidade Total (Total Accessibility)

**A Claude Code skill that builds and audits accessible presentations** — PowerPoint `.pptx` and
PDF/UA — against WCAG 2.2 AA (through WCAG2ICT), ISO 14289, Brazil's Inclusion Act (Law
13.146/2015) and e-MAG.

*[Versão em português](README.md)* — the reference material is written in Brazilian Portuguese.

> **Status:** knowledge base and audit catalogue complete. Pipeline scripts in progress.

---

## Why it exists

PowerPoint's built-in Accessibility Checker covers **10 rules**. It does not look at font size,
justified text, line spacing, the language tag on individual text runs, text over photographs,
colour used as the only carrier of meaning, colour blindness, alt text *quality* (it accepts
`photo1.png` as a valid description), long descriptions, "click here" links, animation, target
size, sign language, audio description, or anything at all in the exported PDF.

This repository is the missing part: **98 auditable rules**, each with a stable ID, a severity,
its source criterion, how to detect it and how to fix it.

---

## What's inside

| | |
|---|---|
| **Audit catalogue** | 13 layers, 98 rules — from document metadata to PDF/UA and human confirmation |
| **OOXML cookbook** | Where every accessibility feature lives in the XML, extracted from real files rather than recalled |
| **Computed colour-blind-safe palette** | Okabe-Ito with variants that actually pass contrast, with measured numbers |
| **Automated sign language** | VLibras paths (LGPLv3, open source), without depending on a government login |
| **Audio description** | Alt text, long description, narrated track and transcript — all four layers |
| **PDF/UA export** | COM automation with document structure tags, plus validation |

---

## Findings that motivated the project

- **The raw Okabe-Ito palette fails WCAG 1.4.11 on a light background.** Yellow measures 1.24:1,
  orange 2.11:1, sky blue 2.16:1 — against a 3:1 minimum. Only three of the eight colours pass.
  The repository ships pre-computed darkened variants.
- **The exported PDF's `/Title` comes out empty** when the `.pptx` has no title in its document
  properties — and since `DisplayDocTitle` is on by default, screen readers fall back to
  announcing the file name.
- **The exported PDF's `/Lang` comes out as `pt`, not `pt-BR`.**
- **The native checker cannot be automated**: no object model returns its results.
- **`.pptx` has no runtime palette switching.** The macro-free answer is a hub slide backed by
  Custom Shows.
- **ABNT NBR 17060 covers mobile applications**, not documents — a frequent miscitation in
  document-accessibility work. NBR 17225:2025 is likewise web-scoped.
- **The current edition of ABNT NBR 15290 is 2016** (reconfirmed 11 Dec 2025), yet the edition
  circulating freely online is the superseded 2005 first edition. The repository carries the sign
  language window parameters checked against the full text, plus the caveat that applying them to
  a slide is **an analogy** — the standard governs television — which must be stated in the report.

---

## Install

```bash
git clone https://github.com/RaulAraujoSilva/acessibilidade-total
```

As a Claude Code skill, place or point the folder at your skills directory:

```
~/.claude/skills/acessibilidade-total/
```

Requirements: Python with `python-pptx`, `pywin32`, `pypdf`, `pymupdf`; Windows with PowerPoint
installed for the COM operations. Optional: `OPENAI_API_KEY` (figures), `ELEVENLABS_API_KEY`
(audio description), Docker and ffmpeg (sign language), veraPDF (validation).

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

Built for an assignment in **TCE 00191 — Accessible Documents**, a doctoral course in Production
Engineering at Universidade Federal Fluminense, Brazil. Published for anyone who needs to
produce genuinely accessible material rather than merely pass a checker.

## Licence

MIT. Contributions welcome — especially corrections from disabled people using material produced
with this skill.
