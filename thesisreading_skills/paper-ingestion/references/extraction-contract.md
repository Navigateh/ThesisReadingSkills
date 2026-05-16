# Paper Ingestion Extraction Contract

`scripts/parse_pdf.py` writes a `SkillResult` object with an `ingestion` payload.

## Top-Level Result

```json
{
  "skill": "paper-ingestion",
  "paper_id": "string",
  "status": "complete|partial|blocked",
  "confidence": "high|medium|low",
  "artifacts": [],
  "findings": [],
  "handoff": {
    "recommended_next_skills": ["paper-decomposition"],
    "state_patch": {"ingestion": {}}
  },
  "warnings": [],
  "ingestion": {}
}
```

## `ingestion`

```json
{
  "schema": "paper-ingestion.v1",
  "source": {
    "type": "pdf",
    "path": "absolute source path",
    "sha256": "file hash"
  },
  "parser": {
    "name": "pymupdf|pdfplumber|pypdf|PyPDF2",
    "ocr": "auto|force|off",
    "image_extraction": "available|unavailable|disabled",
    "capabilities": {}
  },
  "metadata": {},
  "document": {
    "page_count": 0,
    "toc": []
  },
  "pages": [
    {
      "page_number": 1,
      "width": 0,
      "height": 0,
      "rotation": 0,
      "text": "",
      "text_source": "native|ocr|native+ocr|empty",
      "text_blocks": [
        {
          "block_id": "p1-b1",
          "type": "text",
          "bbox": [0, 0, 0, 0],
          "text": ""
        }
      ],
      "images": [],
      "quality": {
        "char_count": 0,
        "word_count": 0,
        "line_count": 0,
        "low_text": true,
        "ocr_used": false
      },
      "warnings": []
    }
  ],
  "sections_hint": [],
  "figures_hint": [],
  "tables_hint": [],
  "formulas_hint": [],
  "quality": {
    "page_count": 0,
    "text_pages": 0,
    "low_text_pages": [],
    "total_chars": 0,
    "avg_chars_per_page": 0,
    "needs_ocr_review": false
  }
}
```

## Hints

Hints are best-effort extraction signals:

- `sections_hint`: likely section headings with page number and line text.
- `figures_hint`: captions starting with Figure/Fig.
- `tables_hint`: captions starting with Table.
- `formulas_hint`: short lines with equation-like symbols or numbering.

Downstream skills must cite hints as "detected" or "likely"; they are not authoritative.
