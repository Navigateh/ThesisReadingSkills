---
name: experiment-analysis
description: Use when academic paper reading requires analysis of experimental design, datasets, metrics, baselines, ablations, statistical significance, validity, reproducibility, or evidence strength.
---

# Experiment Analysis

## Purpose

Evaluate whether a paper's experiments support its claims and recover the details needed for critique or reproduction.

## Inputs

Accept:

```json
{
  "paper_id": "string",
  "source": {"type": "text|notes", "path": "parsed-paper.md", "text": "optional"},
  "reading_goal": "string",
  "constraints": {"language": "zh|en|auto", "depth": "standard|deep", "output_format": "markdown|json|both"},
  "state": {"decomposition": {}, "visuals": {}, "math": {}}
}
```

Use `assets/experiment-analysis-template.json` for structured output. Read `references/experiment-contract.md` before changing fields.

## Workflow

1. Map claims from `state.decomposition.claims` to the experiments that are supposed to support them.
2. Extract datasets, tasks, splits, metrics, baselines, implementation settings, compute budget, ablations, and statistical reporting.
3. Compare evidence strength against the paper's stated claims.
4. Identify threats to validity: weak baselines, missing variance, unclear preprocessing, data leakage risk, insufficient ablations, or unavailable code.
5. Produce reproduction notes and downstream synthesis findings.

## Outputs

Return:

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
  "warnings": []
}
```

## Quality Rules

- Keep result numbers tied to exact tables, figures, or page anchors.
- Report missing variance or missing statistical tests as evidence limitations.
- Separate empirical findings from author interpretation.
- Do not assume code, data, or hyperparameters exist unless the paper states them or external verification was performed.
