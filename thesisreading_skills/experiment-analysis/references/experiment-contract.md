# Experiment Analysis Contract

## State Patch

```json
{
  "experiments": {
    "datasets": [
      {
        "name": "",
        "task": "",
        "split": "",
        "size": "",
        "preprocessing": "",
        "evidence": "",
        "confidence": "high|medium|low"
      }
    ],
    "metrics": [
      {
        "name": "",
        "definition": "",
        "direction": "higher_is_better|lower_is_better|unknown",
        "evidence": "",
        "confidence": "high|medium|low"
      }
    ],
    "baselines": [
      {
        "name": "",
        "role": "main baseline|prior sota|ablation baseline|traditional method|other",
        "fairness_notes": "",
        "evidence": "",
        "confidence": "high|medium|low"
      }
    ],
    "ablations": [
      {
        "component": "",
        "comparison": "",
        "result": "",
        "interpretation": "",
        "evidence": "",
        "confidence": "high|medium|low"
      }
    ],
    "validity_threats": [
      {
        "type": "internal|external|construct|statistical|reproducibility",
        "issue": "",
        "impact": "",
        "evidence": "",
        "severity": "high|medium|low"
      }
    ],
    "reproduction_notes": [
      {
        "item": "code|data|hyperparameter|compute|seed|preprocessing|environment|other",
        "status": "available|missing|unclear|partial",
        "details": "",
        "evidence": ""
      }
    ]
  }
}
```

## Required Findings

- Main empirical claim and evidence strength.
- Dataset/metric/baseline inventory.
- Ablation and statistical reporting status.
- Top reproducibility gaps.

## Status Rules

- `complete`: major claims are mapped to experiments and limitations.
- `partial`: results are extractable but some protocol or numbers are missing.
- `blocked`: experiment sections or tables are not available.
