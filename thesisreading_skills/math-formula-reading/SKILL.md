---
name: math-formula-reading
description: Use when academic paper understanding depends on formulas, symbols, derivations, proofs, objectives, loss functions, algorithms, theorem statements, or notation consistency.
---

# Math Formula Reading

## Purpose

Explain and audit the mathematical layer of a paper: notation, formulas, derivations, objectives, assumptions, and algorithmic math.

## Inputs

Accept:

```json
{
  "paper_id": "string",
  "source": {"type": "text|notes", "path": "parsed-paper.md", "text": "optional formula context"},
  "reading_goal": "string",
  "constraints": {"language": "zh|en|auto", "depth": "standard|deep", "output_format": "markdown|json|both"},
  "state": {"ingestion": {}, "decomposition": {}}
}
```

Use `assets/math-analysis-template.json` for structured output. Read `references/math-contract.md` before changing fields.

## Workflow

1. Collect candidate formulas from `state.ingestion.formulas_hint`, equation references, algorithm blocks, and nearby prose.
2. Build a symbol table before explaining derivations.
3. For each important formula, identify purpose, inputs, outputs, assumptions, and where it appears in the method or experiment.
4. Reconstruct derivations step by step only when the source supports them; mark missing algebra explicitly.
5. Flag undefined symbols, overloaded notation, inconsistent dimensions, hidden assumptions, and formulas that control experimental interpretation.

## Outputs

Return:

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
  "warnings": []
}
```

## Quality Rules

- Do not invent missing derivation steps; state when a step is inferred.
- Keep formula explanations tied to the paper's notation, not generic textbook notation.
- Track symbol scope because papers often reuse letters across sections.
- If formulas are image-only or OCR-corrupted, request `paper-ingestion` or visual inspection before final interpretation.
