---
name: figure-table-reading
description: Use when academic paper understanding depends on figures, tables, plots, architecture diagrams, result grids, qualitative examples, captions, axes, or visual evidence.
---

# Figure Table Reading

## Purpose

Interpret visual evidence in a paper and convert figures/tables into grounded claims, comparisons, and uncertainty notes.

## Inputs

Accept:

```json
{
  "paper_id": "string",
  "source": {"type": "pdf|image|text|notes", "path": "pdf/image/parsed path", "text": "optional caption/table text"},
  "reading_goal": "string",
  "constraints": {"language": "zh|en|auto", "depth": "triage|standard|deep", "output_format": "markdown|json|both"},
  "state": {"ingestion": {"figures_hint": [], "tables_hint": []}, "decomposition": {}}
}
```

Use `assets/figures-tables-template.json` for structured output. Read `references/visual-contract.md` before changing fields.

## Workflow

1. Inventory figures and tables from ingestion hints, captions, page text, and image assets when available.
2. For each item, identify its role: method diagram, main result, ablation, qualitative example, failure case, dataset description, or appendix support.
3. Extract axes, metrics, row/column meanings, compared methods, units, and any visible uncertainty measures.
4. Convert visual evidence into claims with exact figure/table/page anchors.
5. Flag ambiguous axes, cropped values, unreadable legends, missing captions, or chart/table values that require manual inspection.

## Outputs

Return:

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
  "warnings": []
}
```

## Quality Rules

- Distinguish directly read values from visually estimated values.
- Do not rank methods from a plot unless axes, metrics, and directionality are clear.
- Preserve caption wording when it affects interpretation.
- Treat table extraction as partial when row/column alignment is uncertain.
