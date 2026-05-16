---
name: paper-decomposition
description: Use when reliable academic paper text exists and the paper needs section structure, problem statement, contributions, assumptions, method flow, claims, limitations, or a reading outline.
---

# Paper Decomposition

## Purpose

Convert parsed paper text into a section map, claim graph, method outline, and downstream reading handoff.

## Inputs

Accept:

```json
{
  "paper_id": "string",
  "source": {"type": "text|notes", "path": "parsed-paper.md or text path", "text": "optional"},
  "reading_goal": "string",
  "constraints": {"language": "zh|en|auto", "depth": "triage|standard|deep", "output_format": "markdown|json|both"},
  "state": {"ingestion": {}}
}
```

Use `assets/decomposition-template.json` for structured output. Read `references/decomposition-contract.md` before changing fields.

## Workflow

1. Check ingestion quality first. If text is missing, low-confidence, or lacks page anchors, route back to `paper-ingestion`.
2. Build a section map from headings, abstract, introduction, method, experiments, conclusion, appendix, and references.
3. Extract the paper's problem, motivation, thesis, claimed contributions, assumptions, method steps, evidence hooks, and limitations.
4. Link every major claim to page, section, figure, table, or equation evidence.
5. Produce open questions and recommend targeted next skills: math, figures/tables, experiments, related work, or synthesis.

## Outputs

Return:

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

## Quality Rules

- Do not treat author claims as proven facts; label them as claims until experiments or analysis support them.
- Preserve page and section anchors for all extracted points.
- Separate "what the paper says" from interpretation or critique.
- If structure is inferred rather than explicit, mark confidence as `medium` or `low`.
