---
name: thesis-reading
description: Use when reading, analyzing, reviewing, or taking notes on academic papers, theses, dissertations, arXiv PDFs, conference papers, or research articles across multiple reading subtasks.
---

# Thesis Reading

## Purpose

Use this as the dispatcher for research-paper reading. It decides which specialized reading skill should run, keeps schemas consistent, and assembles the final reading package.

## Start Here

1. Identify the user's reading goal: quick triage, deep understanding, reproduction, literature mapping, critique, or notes.
2. Read `references/routing.md` when choosing subskills, planning handoffs, or validating input/output schemas.
3. Use `assets/reading-state-template.json` to keep shared state across subskills.
4. Use `assets/paper-note-template.md` for the final human-readable note unless the user requests another format.

## Default Pipelines

- For `Full Reading` / `完整阅读` / `精读`, run `paper-ingestion` -> `paper-decomposition`, then run `math-formula-reading`, `figure-table-reading`, and `experiment-analysis` as independent parallel analyses, then run `related-work-mapping`, then finish with `synthesis-and-notes`.
- For narrow questions, route only to the relevant subskills instead of forcing the full pipeline.

## Dispatch Rules

- Start with `paper-ingestion` when the source is a PDF, scanned PDF, image-only paper, multi-column layout, extracted text with uncertain quality, or the user asks to parse/OCR/convert a paper.
- Use `paper-decomposition` after reliable text exists and the user needs section-level structure, claims, assumptions, method steps, or contribution extraction.
- Use `math-formula-reading` when formulas, symbols, proofs, derivations, optimization objectives, losses, theorems, or notation are central to the user's question.
- Use `figure-table-reading` when results depend on figures, tables, architecture diagrams, plots, qualitative examples, or visual evidence.
- Use `experiment-analysis` when the user asks about datasets, metrics, baselines, ablations, statistical significance, validity, reproducibility, or experimental design.
- Use `related-work-mapping` when the user asks how the work fits prior work, citation lineage, novelty, positioning, missing references, or research gaps.
- Use `synthesis-and-notes` when the user wants summaries, critiques, review notes, flashcards, study plans, comparison notes, or final reading outputs.

## Shared Contract

Every subskill should accept a JSON-compatible object with:

```json
{
  "paper_id": "stable local id or citation key",
  "source": {"type": "pdf|text|metadata|notes", "path": "optional local path", "text": "optional text"},
  "reading_goal": "what the user wants to learn or produce",
  "constraints": {"language": "zh|en|auto", "depth": "triage|standard|deep", "output_format": "markdown|json|both"},
  "state": {}
}
```

Every subskill should return:

```json
{
  "skill": "subskill-name",
  "paper_id": "same id",
  "status": "complete|partial|blocked",
  "confidence": "high|medium|low",
  "artifacts": [],
  "findings": [],
  "handoff": {"recommended_next_skills": [], "state_patch": {}},
  "warnings": []
}
```

## Output Discipline

Keep claims tied to evidence. If the source extraction is weak, say so before interpreting the paper. Do not invent missing equations, table values, citations, or experimental details.
