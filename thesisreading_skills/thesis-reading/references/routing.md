# Thesis Reading Routing

This file defines when to use each subskill and the input/output schema each one must honor.

## Shared Objects

### `ReadingRequest`

```json
{
  "paper_id": "string; stable id such as firstauthor-year-keyword",
  "source": {
    "type": "pdf|text|metadata|notes|image",
    "path": "string; optional local path",
    "text": "string; optional extracted text",
    "metadata": {}
  },
  "reading_goal": "string; user's concrete objective",
  "constraints": {
    "language": "zh|en|auto",
    "depth": "triage|standard|deep",
    "output_format": "markdown|json|both",
    "time_budget_minutes": "number|null"
  },
  "state": {}
}
```

### `SkillResult`

```json
{
  "skill": "string",
  "paper_id": "string",
  "status": "complete|partial|blocked",
  "confidence": "high|medium|low",
  "artifacts": [
    {
      "type": "json|markdown|text|image|csv",
      "path": "string|null",
      "description": "string"
    }
  ],
  "findings": [
    {
      "claim": "string",
      "evidence": "page/section/table/figure/span reference",
      "confidence": "high|medium|low"
    }
  ],
  "handoff": {
    "recommended_next_skills": ["string"],
    "state_patch": {}
  },
  "warnings": ["string"]
}
```

## Default Pipelines

### Quick Triage

`paper-ingestion` only if source is PDF or extraction quality is unknown, then `paper-decomposition`, then `synthesis-and-notes`.

Goal: identify topic, problem, contribution, method, core evidence, and whether to read deeply.

### Full Reading / 完整阅读

`paper-ingestion` -> `paper-decomposition` -> parallel [`math-formula-reading`, `figure-table-reading`, `experiment-analysis`] -> `related-work-mapping` -> `synthesis-and-notes`.

Use when the user asks for a complete read, full reading, 精读, 完整阅读, full paper review, or comprehensive notes. The three middle analyses should run independently from the shared `ingestion` and `decomposition` state:

- `math-formula-reading`: formulas, derivations, symbols, objectives, losses, algorithms, theorems, or notation.
- `figure-table-reading`: figures, tables, plots, architecture diagrams, qualitative examples, and visual evidence.
- `experiment-analysis`: experimental design, datasets, metrics, baselines, ablations, significance, validity, and reproducibility.

`related-work-mapping` runs after those analyses so it can position the contribution with awareness of the method, evidence, and limitations. `synthesis-and-notes` runs last and merges all available upstream artifacts into the final note.

### Deep Technical Reading

`paper-ingestion` -> `paper-decomposition` -> targeted `math-formula-reading`, `figure-table-reading`, and `experiment-analysis` -> `synthesis-and-notes`.

Goal: reconstruct the paper's argument and technical mechanism.

### Reproduction-Oriented Reading

`paper-ingestion` -> `paper-decomposition` -> `experiment-analysis` -> `math-formula-reading` if objective/loss details matter -> `figure-table-reading` for architecture/results -> `synthesis-and-notes`.

Goal: recover implementation details, data, metrics, baselines, hyperparameters, and missing reproducibility information.

### Literature Positioning

`paper-ingestion` if needed -> `paper-decomposition` -> `related-work-mapping` -> `synthesis-and-notes`.

Goal: locate novelty, citation lineage, adjacent methods, and research gaps.

## Subskill Routing and Schemas

## 1. `paper-ingestion`

Use when:

- Source is a PDF, scanned PDF, image, or mixed text/image paper.
- The extracted text may be incomplete, out of reading order, or missing tables/formulas.
- The user asks for OCR, PDF parsing, layout parsing, metadata extraction, page-level segmentation, or conversion to Markdown/JSON.

Avoid when:

- The user already provides clean full text with page references and no visual/layout questions.

Input schema:

```json
{
  "paper_id": "string",
  "source": {
    "type": "pdf|image|text",
    "path": "required for pdf/image",
    "text": "optional fallback text",
    "metadata": {"doi": "optional", "title": "optional"}
  },
  "reading_goal": "string",
  "constraints": {
    "language": "zh|en|auto",
    "depth": "triage|standard|deep",
    "output_format": "json|markdown|both",
    "ocr": "auto|force|off",
    "extract_images": "boolean"
  },
  "state": {}
}
```

Output schema:

```json
{
  "skill": "paper-ingestion",
  "paper_id": "string",
  "status": "complete|partial|blocked",
  "confidence": "high|medium|low",
  "artifacts": [
    {"type": "json", "path": "parsed-paper.json", "description": "page, block, metadata, and quality package"},
    {"type": "markdown", "path": "parsed-paper.md", "description": "reading-order text with page anchors"}
  ],
  "findings": [
    {"claim": "Detected title/authors/abstract or extraction issue", "evidence": "metadata/page reference", "confidence": "high|medium|low"}
  ],
  "handoff": {
    "recommended_next_skills": ["paper-decomposition"],
    "state_patch": {
      "ingestion": {
        "pages": [],
        "sections_hint": [],
        "figures_hint": [],
        "tables_hint": [],
        "formulas_hint": [],
        "quality": {}
      }
    }
  },
  "warnings": ["missing OCR dependency, low text density, rotated pages, unreadable figures"]
}
```

## 2. `paper-decomposition`

Use when:

- Reliable paper text exists and the user needs structure, thesis, contribution, assumptions, method, limitations, or section-by-section reading.
- The user asks "这篇论文讲了什么", "主要贡献是什么", "方法流程是什么", or wants a structured outline.

Input schema:

```json
{
  "paper_id": "string",
  "source": {"type": "text|notes", "path": "parsed-paper.md or text path", "text": "optional"},
  "reading_goal": "string",
  "constraints": {"language": "zh|en|auto", "depth": "triage|standard|deep", "output_format": "markdown|json|both"},
  "state": {"ingestion": {}}
}
```

Output schema:

```json
{
  "skill": "paper-decomposition",
  "paper_id": "string",
  "status": "complete|partial|blocked",
  "confidence": "high|medium|low",
  "artifacts": [{"type": "json", "path": "decomposition.json", "description": "section and claim graph"}],
  "findings": [
    {"claim": "problem statement", "evidence": "section/page", "confidence": "high|medium|low"},
    {"claim": "main contribution", "evidence": "section/page", "confidence": "high|medium|low"}
  ],
  "handoff": {
    "recommended_next_skills": ["math-formula-reading", "figure-table-reading", "experiment-analysis", "synthesis-and-notes"],
    "state_patch": {
      "decomposition": {
        "sections": [],
        "claims": [],
        "method_steps": [],
        "open_questions": []
      }
    }
  },
  "warnings": []
}
```

## 3. `math-formula-reading`

Use when:

- Meaning depends on equations, symbols, derivations, proofs, objectives, loss functions, algorithms, theorem statements, or notation consistency.
- The user asks to explain a formula, derive a step, build a symbol table, or verify math claims.

Input schema:

```json
{
  "paper_id": "string",
  "source": {"type": "text|notes", "path": "parsed-paper.md", "text": "optional formula context"},
  "reading_goal": "string",
  "constraints": {"language": "zh|en|auto", "depth": "standard|deep", "output_format": "markdown|json|both"},
  "state": {"ingestion": {}, "decomposition": {}}
}
```

Output schema:

```json
{
  "skill": "math-formula-reading",
  "paper_id": "string",
  "status": "complete|partial|blocked",
  "confidence": "high|medium|low",
  "artifacts": [{"type": "json", "path": "math-analysis.json", "description": "formula map and symbol table"}],
  "findings": [
    {"claim": "formula purpose or derivation step", "evidence": "equation/page/section", "confidence": "high|medium|low"}
  ],
  "handoff": {
    "recommended_next_skills": ["experiment-analysis", "synthesis-and-notes"],
    "state_patch": {
      "math": {
        "symbols": [],
        "formulas": [],
        "derivations": [],
        "ambiguities": []
      }
    }
  },
  "warnings": ["unreadable equation image, missing definition, inconsistent notation"]
}
```

## 4. `figure-table-reading`

Use when:

- Figures, tables, plots, architecture diagrams, screenshots, qualitative examples, or result tables contain important evidence.
- The user asks to interpret a graph/table, compare rows, explain an architecture figure, or extract values.

Input schema:

```json
{
  "paper_id": "string",
  "source": {"type": "pdf|image|text|notes", "path": "pdf/image/parsed path", "text": "optional caption/table text"},
  "reading_goal": "string",
  "constraints": {"language": "zh|en|auto", "depth": "triage|standard|deep", "output_format": "markdown|json|both"},
  "state": {"ingestion": {"figures_hint": [], "tables_hint": []}, "decomposition": {}}
}
```

Output schema:

```json
{
  "skill": "figure-table-reading",
  "paper_id": "string",
  "status": "complete|partial|blocked",
  "confidence": "high|medium|low",
  "artifacts": [{"type": "json", "path": "figures-tables.json", "description": "figure/table inventory and interpretations"}],
  "findings": [
    {"claim": "visual evidence or table comparison", "evidence": "figure/table/page", "confidence": "high|medium|low"}
  ],
  "handoff": {
    "recommended_next_skills": ["experiment-analysis", "synthesis-and-notes"],
    "state_patch": {
      "visuals": {
        "figures": [],
        "tables": [],
        "numeric_results": [],
        "visual_uncertainties": []
      }
    }
  },
  "warnings": ["low-resolution image, cropped table, ambiguous axis, missing caption"]
}
```

## 5. `experiment-analysis`

Use when:

- The user asks about experimental validity, metrics, datasets, baselines, ablations, significance, reproducibility, error analysis, or whether the evidence supports the claims.
- Result interpretation depends on comparing methods or understanding evaluation protocol.

Input schema:

```json
{
  "paper_id": "string",
  "source": {"type": "text|notes", "path": "parsed-paper.md", "text": "optional"},
  "reading_goal": "string",
  "constraints": {"language": "zh|en|auto", "depth": "standard|deep", "output_format": "markdown|json|both"},
  "state": {"decomposition": {}, "visuals": {}, "math": {}}
}
```

Output schema:

```json
{
  "skill": "experiment-analysis",
  "paper_id": "string",
  "status": "complete|partial|blocked",
  "confidence": "high|medium|low",
  "artifacts": [{"type": "json", "path": "experiment-analysis.json", "description": "datasets, metrics, baselines, ablations, and validity notes"}],
  "findings": [
    {"claim": "evidence strength or experimental limitation", "evidence": "table/figure/section/page", "confidence": "high|medium|low"}
  ],
  "handoff": {
    "recommended_next_skills": ["related-work-mapping", "synthesis-and-notes"],
    "state_patch": {
      "experiments": {
        "datasets": [],
        "metrics": [],
        "baselines": [],
        "ablations": [],
        "validity_threats": [],
        "reproduction_notes": []
      }
    }
  },
  "warnings": ["missing variance, no statistical test, unclear split, weak baseline, unavailable code"]
}
```

## 6. `related-work-mapping`

Use when:

- The user asks about novelty, contribution positioning, schools of thought, citation network, precursor methods, follow-up work, or missing related work.
- The final answer needs to compare this paper with other papers.

Input schema:

```json
{
  "paper_id": "string",
  "source": {"type": "text|metadata|notes", "path": "parsed-paper.md", "text": "optional related work/citations"},
  "reading_goal": "string",
  "constraints": {"language": "zh|en|auto", "depth": "triage|standard|deep", "output_format": "markdown|json|both"},
  "state": {"decomposition": {}, "experiments": {}}
}
```

Output schema:

```json
{
  "skill": "related-work-mapping",
  "paper_id": "string",
  "status": "complete|partial|blocked",
  "confidence": "high|medium|low",
  "artifacts": [{"type": "json", "path": "related-work-map.json", "description": "citation clusters and novelty positioning"}],
  "findings": [
    {"claim": "positioning or novelty statement", "evidence": "citation/section/page", "confidence": "high|medium|low"}
  ],
  "handoff": {
    "recommended_next_skills": ["synthesis-and-notes"],
    "state_patch": {
      "related_work": {
        "clusters": [],
        "key_citations": [],
        "claimed_novelty": [],
        "missing_or_uncertain_links": []
      }
    }
  },
  "warnings": ["citation metadata incomplete, external search not performed, ambiguous novelty claim"]
}
```

## 7. `synthesis-and-notes`

Use when:

- The user asks for summary, critique, study notes, review comments, flashcards, reusable reading notes, comparison memo, or final answer.
- Multiple subskill outputs need to be merged.

Input schema:

```json
{
  "paper_id": "string",
  "source": {"type": "notes|text", "path": "state/artifact paths", "text": "optional"},
  "reading_goal": "string",
  "constraints": {
    "language": "zh|en|auto",
    "depth": "triage|standard|deep",
    "output_format": "markdown|json|both",
    "note_style": "outline|cornell|review|flashcards|comparison"
  },
  "state": {
    "ingestion": {},
    "decomposition": {},
    "math": {},
    "visuals": {},
    "experiments": {},
    "related_work": {}
  }
}
```

Output schema:

```json
{
  "skill": "synthesis-and-notes",
  "paper_id": "string",
  "status": "complete|partial|blocked",
  "confidence": "high|medium|low",
  "artifacts": [
    {"type": "markdown", "path": "paper-note.md", "description": "final reading note"},
    {"type": "json", "path": "paper-note.json", "description": "structured synthesis"}
  ],
  "findings": [
    {"claim": "final synthesized conclusion", "evidence": "source artifact/page/section", "confidence": "high|medium|low"}
  ],
  "handoff": {
    "recommended_next_skills": [],
    "state_patch": {
      "synthesis": {
        "summary": "",
        "critical_takeaways": [],
        "open_questions": [],
        "review_cards": []
      }
    }
  },
  "warnings": ["some upstream artifacts missing, low extraction confidence, external context not verified"]
}
```

## Handoff Quality Rules

- Preserve page, section, figure, table, and equation anchors whenever possible.
- Mark uncertain claims as `confidence: low`; do not smooth over extraction gaps.
- Keep machine-readable outputs JSON-compatible even when the final user-facing note is Markdown.
- If the user asks a narrow question, route only to the necessary subskills rather than running the full pipeline.
- If a subskill is not implemented yet, use this routing document as the contract and perform the work manually under the same schema.
