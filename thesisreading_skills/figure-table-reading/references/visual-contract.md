# Figure Table Reading Contract

## State Patch

```json
{
  "visuals": {
    "figures": [
      {
        "figure_id": "fig1",
        "page_number": 0,
        "caption": "",
        "role": "method|result|ablation|qualitative|dataset|failure|appendix|other",
        "description": "",
        "claims_supported": [],
        "confidence": "high|medium|low"
      }
    ],
    "tables": [
      {
        "table_id": "tab1",
        "page_number": 0,
        "caption": "",
        "role": "result|ablation|dataset|baseline|hyperparameter|appendix|other",
        "columns": [],
        "rows_summary": "",
        "claims_supported": [],
        "confidence": "high|medium|low"
      }
    ],
    "numeric_results": [
      {
        "item_id": "",
        "method": "",
        "dataset_or_task": "",
        "metric": "",
        "value": "",
        "direction": "higher_is_better|lower_is_better|unknown",
        "evidence": "table/figure/page",
        "confidence": "high|medium|low"
      }
    ],
    "visual_uncertainties": [
      {
        "item": "",
        "issue": "ambiguous axis|cropped value|low resolution|missing caption|table alignment|other",
        "evidence": "",
        "impact": ""
      }
    ]
  }
}
```

## Required Findings

- Main figure/table inventory.
- Key visual evidence for the paper's main claims.
- Any table/plot ambiguity that affects interpretation.

## Status Rules

- `complete`: important figures/tables are interpreted with anchors.
- `partial`: some visuals are missing, unreadable, or only captions are available.
- `blocked`: no usable visual or caption evidence.
