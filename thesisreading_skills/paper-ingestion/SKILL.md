---
name: paper-ingestion
description: Use when an academic paper, thesis, dissertation, or research article must be parsed from PDF, scanned PDF, OCR output, page images, or uncertain extracted text before deeper reading.
---

# Paper Ingestion

## Purpose

Convert source papers into a reliable, page-anchored ingestion package for downstream thesis-reading skills.

## Inputs

Accept a JSON-compatible request:

```json
{
  "paper_id": "string",
  "source": {
    "type": "pdf|image|text",
    "path": "required for pdf/image",
    "text": "optional fallback text",
    "metadata": {}
  },
  "reading_goal": "string",
  "constraints": {
    "language": "zh|en|auto",
    "depth": "triage|standard|deep",
    "output_format": "json|markdown|both",
    "ocr": "auto|force|off",
    "extract_images": false
  },
  "state": {}
}
```

Use `assets/ingestion-request-template.json` when the caller has not supplied structured input.

## Workflow

1. Confirm the source exists and decide whether OCR is needed.
2. Run `scripts/parse_pdf.py` for PDF sources.
3. Inspect the JSON quality fields before interpreting content.
4. Report extraction limits clearly: missing OCR dependencies, low text density, unreadable pages, weak layout order, or incomplete figure/table extraction.
5. Return both machine-readable artifacts and a concise handoff for `paper-decomposition`.

Example:

```bash
python thesisreading_skills/paper-ingestion/scripts/parse_pdf.py paper.pdf --out-dir parsed/paper --ocr auto --extract-images
```

## Outputs

Return:

```json
{
  "skill": "paper-ingestion",
  "paper_id": "string",
  "status": "complete|partial|blocked",
  "confidence": "high|medium|low",
  "artifacts": [
    {"type": "json", "path": "parsed-paper.json", "description": "page, block, metadata, and quality package"},
    {"type": "markdown", "path": "parsed-paper.md", "description": "reading-order text with page anchors"}
  ],
  "findings": [
    {"claim": "extraction or metadata finding", "evidence": "metadata/page reference", "confidence": "high|medium|low"}
  ],
  "handoff": {
    "recommended_next_skills": ["paper-decomposition"],
    "state_patch": {
      "ingestion": {
        "pages": [],
        "sections_hint": [],
        "figures_hint": [],
        "tables_hint": [],
        "formulas_hint": [],
        "quality": {}
      }
    }
  },
  "warnings": []
}
```

## Script Notes

`scripts/parse_pdf.py` prefers PyMuPDF, then pdfplumber, then pypdf/PyPDF2. OCR is optional and uses pytesseract plus PyMuPDF/Pillow when installed. The script still produces a clear partial result when OCR or image extraction is unavailable.

Read `references/extraction-contract.md` before changing the parser output schema.

## Quality Rules

- Never claim that text is complete unless quality checks support it.
- Preserve page anchors and source paths in all outputs.
- Treat formula, figure, and table detection as hints, not ground truth.
- If OCR is required but unavailable, return `partial` with a warning instead of silently continuing.
