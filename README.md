# ThesisReading Skills

ThesisReading Skills is a local skill bundle for academic paper reading. It provides one dispatcher skill plus seven focused subskills for PDF ingestion, paper decomposition, formulas, figures/tables, experiments, related work, and final notes.

## Skills

```text
thesisreading_skills/
├── thesis-reading/              # Dispatcher and routing
├── paper-ingestion/             # PDF/OCR/layout parsing
├── paper-decomposition/         # Structure, claims, methods
├── math-formula-reading/        # Formulas, derivations, symbols
├── figure-table-reading/        # Figures, tables, visual evidence
├── experiment-analysis/         # Experiments, metrics, ablations
├── related-work-mapping/        # Citations, novelty, positioning
└── synthesis-and-notes/         # Summary, critique, notes, cards
```

## Install

Copy each skill directory into your local skills directory. Copy the children of `thesisreading_skills`, not the wrapper folder itself.

Codex:

```bash
cp -r thesisreading_skills/* ~/.codex/skills/
```

Claude Code:

```bash
cp -r thesisreading_skills/* ~/.claude/skills/
```

Restart Codex or Claude Code after copying.

Expected installed layout:

```text
~/.codex/skills/
├── thesis-reading/SKILL.md
├── paper-ingestion/SKILL.md
├── paper-decomposition/SKILL.md
└── ...
```

## Use

Invoke the dispatcher for whole-paper workflows:

```text
Use $thesis-reading to do a Full Reading / 完整阅读 of this paper.
```

Full Reading route:

```text
paper-ingestion
-> paper-decomposition
-> parallel [math-formula-reading, figure-table-reading, experiment-analysis]
-> related-work-mapping
-> synthesis-and-notes
```

You can also invoke a subskill directly, for example:

```text
Use $paper-ingestion to parse this PDF into JSON and Markdown artifacts.
Use $math-formula-reading to explain the objective and symbols.
Use $experiment-analysis to evaluate baselines, metrics, and ablations.
```

## PDF Parser

`paper-ingestion` includes a local parser:

```bash
python thesisreading_skills/paper-ingestion/scripts/parse_pdf.py paper.pdf --out-dir parsed/paper --ocr auto --extract-images
```

The parser prefers `PyMuPDF`, then `pdfplumber`, then `pypdf`/`PyPDF2`. OCR is optional and requires `PyMuPDF`, `Pillow`, and `pytesseract`.

## Test

Run the repository validation:

```bash
python -m unittest discover -s tests -v
```

The tests check skill structure, frontmatter, JSON templates, `agents/openai.yaml`, and the PDF parser entry point.

## Repository Notes

- Keep README, tests, and CI at repository root.
- Do not add README files inside individual skill directories; skill folders should contain only `SKILL.md`, `agents/`, `assets/`, `references/`, and scripts when needed.
- If you rename a skill, update `thesis-reading/references/routing.md` and tests together.
