---
name: synthesis-and-notes
description: Use when academic paper reading outputs must be merged into summaries, critiques, study notes, review comments, flashcards, comparison memos, or final reading deliverables.
---

# Synthesis And Notes

## Purpose

Merge upstream reading artifacts into a clear final answer, paper note, critique, study aid, or review memo.

## Inputs

Accept:

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

Use `assets/final-note-template.md` and `assets/synthesis-template.json` for final outputs. Read `references/synthesis-contract.md` before changing fields.

## Workflow

1. Check upstream coverage before synthesizing. Mention missing or low-confidence upstream artifacts.
2. Choose the note style from the user request: outline, Cornell note, review memo, flashcards, comparison, or direct answer.
3. Merge claims across decomposition, math, visuals, experiments, and related work. Resolve conflicts by citing evidence and confidence.
4. Separate summary, evidence, critique, limitations, open questions, and review cards.
5. Keep the final result usable for later review: concise headings, stable anchors, and explicit evidence references.

## Outputs

Return:

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
  "warnings": []
}
```

## Quality Rules

- Do not hide uncertainty; surface extraction gaps and missing analyses.
- Keep critique grounded in evidence from upstream state.
- Do not add external background unless the user asked for it or it was verified.
- Make final notes scannable enough for later study.
