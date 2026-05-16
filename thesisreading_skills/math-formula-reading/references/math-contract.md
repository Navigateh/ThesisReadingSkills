# Math Formula Reading Contract

## State Patch

```json
{
  "math": {
    "symbols": [
      {
        "symbol": "",
        "meaning": "",
        "scope": "global|section|equation|algorithm",
        "first_seen": "page/section/equation",
        "units_or_shape": "",
        "confidence": "high|medium|low"
      }
    ],
    "formulas": [
      {
        "formula_id": "eq1",
        "label": "",
        "latex_or_text": "",
        "purpose": "",
        "inputs": [],
        "outputs": [],
        "assumptions": [],
        "evidence": "page/section/equation",
        "confidence": "high|medium|low"
      }
    ],
    "derivations": [
      {
        "derivation_id": "d1",
        "from": "",
        "to": "",
        "steps": [],
        "missing_steps": [],
        "evidence": "",
        "confidence": "high|medium|low"
      }
    ],
    "ambiguities": [
      {
        "item": "",
        "issue": "undefined|overloaded|dimension mismatch|ocr corruption|missing derivation|other",
        "evidence": "",
        "impact": ""
      }
    ]
  }
}
```

## Required Findings

- Central objective/loss/formula if present.
- Symbol table for recurring notation.
- Any math ambiguity that affects interpretation or reproduction.

## Status Rules

- `complete`: important formulas are mapped with definitions and evidence.
- `partial`: formula extraction is incomplete or some symbols are unresolved.
- `blocked`: formula text/images are unreadable and no evidence is available.
