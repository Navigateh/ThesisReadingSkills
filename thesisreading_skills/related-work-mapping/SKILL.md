---
name: related-work-mapping
description: Use when academic paper reading requires novelty positioning, citation mapping, prior-work comparison, research lineage, schools of thought, missing references, or follow-up work.
---

# Related Work Mapping

## Purpose

Position a paper in its research context by mapping cited work, claimed novelty, comparison axes, and unresolved lineage questions.

## Inputs

Accept:

```json
{
  "paper_id": "string",
  "source": {"type": "text|metadata|notes", "path": "parsed-paper.md", "text": "optional related work/citations"},
  "reading_goal": "string",
  "constraints": {"language": "zh|en|auto", "depth": "triage|standard|deep", "output_format": "markdown|json|both"},
  "state": {"decomposition": {}, "experiments": {}}
}
```

Use `assets/related-work-map-template.json` for structured output. Read `references/related-work-contract.md` before changing fields.

## Workflow

1. Extract citation clusters from related work, introduction, method comparisons, and experiment baselines.
2. Identify the paper's claimed novelty and the dimensions used to distinguish it from prior work.
3. Map cited work into roles: precursor, competing method, baseline, dataset/benchmark, theory/tooling, or follow-up context supplied by the user.
4. Compare claimed novelty with method and experiment evidence from upstream state.
5. Mark gaps where external search is required; do not fabricate citation metadata.

## Outputs

Return:

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
  "warnings": []
}
```

## Quality Rules

- Clearly mark whether positioning is based only on the paper text or also on external search.
- Do not infer that an uncited paper is irrelevant; mark it as an open check.
- Keep baseline papers separate from conceptual ancestors.
- Tie novelty claims to the paper's own wording and evidence.
