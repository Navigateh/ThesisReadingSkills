# Paper Decomposition Contract

## State Patch

```json
{
  "decomposition": {
    "sections": [
      {
        "section_id": "s1",
        "title": "Abstract",
        "level": 1,
        "page_start": 1,
        "page_end": 1,
        "summary": "",
        "role": "abstract|introduction|background|method|experiment|result|discussion|conclusion|appendix|references|other"
      }
    ],
    "claims": [
      {
        "claim_id": "c1",
        "type": "problem|motivation|contribution|method|result|limitation|assumption",
        "text": "",
        "evidence": "page/section/figure/table/equation",
        "confidence": "high|medium|low",
        "supported_by": []
      }
    ],
    "method_steps": [
      {
        "step_id": "m1",
        "name": "",
        "description": "",
        "inputs": [],
        "outputs": [],
        "evidence": "",
        "depends_on": []
      }
    ],
    "open_questions": [
      {
        "question": "",
        "why_it_matters": "",
        "recommended_next_skill": ""
      }
    ]
  }
}
```

## Required Findings

- Problem statement.
- Main contribution list.
- Method summary.
- Most important uncertainty or limitation.

## Status Rules

- `complete`: section map and main claims are grounded with anchors.
- `partial`: text quality, missing sections, or weak anchors limit confidence.
- `blocked`: no usable paper text.
