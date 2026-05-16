# Related Work Mapping Contract

## State Patch

```json
{
  "related_work": {
    "clusters": [
      {
        "cluster_id": "rw1",
        "name": "",
        "theme": "",
        "papers": [],
        "relationship_to_current_paper": "",
        "evidence": "",
        "confidence": "high|medium|low"
      }
    ],
    "key_citations": [
      {
        "citation_key": "",
        "title": "",
        "authors": [],
        "year": null,
        "role": "precursor|baseline|competing method|dataset|benchmark|theory|tool|survey|other",
        "why_it_matters": "",
        "evidence": "",
        "metadata_confidence": "high|medium|low"
      }
    ],
    "claimed_novelty": [
      {
        "claim": "",
        "contrast": "",
        "evidence": "",
        "supported_by_experiments": "yes|no|partial|unknown",
        "confidence": "high|medium|low"
      }
    ],
    "missing_or_uncertain_links": [
      {
        "topic_or_paper": "",
        "reason_to_check": "",
        "requires_external_search": true,
        "priority": "high|medium|low"
      }
    ]
  }
}
```

## Required Findings

- Main research cluster.
- Claimed novelty and contrast target.
- Key citations and baselines.
- External-search gaps, if any.

## Status Rules

- `complete`: related-work structure and novelty claims are grounded in paper text or verified metadata.
- `partial`: citation metadata is incomplete or external context was not checked.
- `blocked`: related-work/citation content is unavailable.
