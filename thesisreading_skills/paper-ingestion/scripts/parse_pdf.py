#!/usr/bin/env python3
"""Parse academic PDFs into page-anchored JSON and Markdown artifacts."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


SCHEMA_VERSION = "paper-ingestion.v1"
SECTION_RE = re.compile(
    r"^\s*((\d+(\.\d+)*)|[IVX]+)\s+[\w\"'`(\[]|^\s*"
    r"(abstract|introduction|background|related work|method|methods|approach|model|"
    r"experiments?|evaluation|results?|discussion|limitations?|conclusion|references)"
    r"\s*$",
    re.IGNORECASE,
)
FIGURE_RE = re.compile(r"^\s*(fig\.?|figure)\s+\d+[\.:]?\s+(.+)", re.IGNORECASE)
TABLE_RE = re.compile(r"^\s*table\s+\d+[\.:]?\s+(.+)", re.IGNORECASE)
FORMULA_RE = re.compile(
    r"(=|<=|>=|\\sum|\\prod|\\int|\\frac|\\sqrt|\\theta|\\lambda|\\alpha|\\beta|"
    r"\\gamma|\u2211|\u220f|\u222b|\u221a|\u2264|\u2265|\u2260|\u2248|\u00b1|\u221e|"
    r"\([0-9]{1,3}\)\s*$)"
)


def import_optional(module_name: str) -> Optional[Any]:
    try:
        return importlib.import_module(module_name)
    except Exception:
        return None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean_text(text: Optional[str]) -> str:
    if not text:
        return ""
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def page_quality(text: str, min_chars: int, ocr_used: bool) -> Dict[str, Any]:
    lines = [line for line in text.splitlines() if line.strip()]
    chars = len(text)
    return {
        "char_count": chars,
        "word_count": word_count(text),
        "line_count": len(lines),
        "low_text": chars < min_chars,
        "ocr_used": ocr_used,
    }


def normalize_metadata(metadata: Optional[Dict[str, Any]]) -> Dict[str, str]:
    if not metadata:
        return {}
    normalized: Dict[str, str] = {}
    for key, value in metadata.items():
        if value is None:
            continue
        clean_key = str(key).strip().lstrip("/").lower()
        clean_value = str(value).strip()
        if clean_value:
            normalized[clean_key] = clean_value
    return normalized


def choose_parser(requested: str) -> Tuple[str, Any]:
    if requested in {"auto", "pymupdf"}:
        fitz = import_optional("fitz")
        if fitz is not None:
            return "pymupdf", fitz
        if requested == "pymupdf":
            raise RuntimeError("PyMuPDF is not installed. Install pymupdf or use --parser auto.")

    if requested in {"auto", "pdfplumber"}:
        pdfplumber = import_optional("pdfplumber")
        if pdfplumber is not None:
            return "pdfplumber", pdfplumber
        if requested == "pdfplumber":
            raise RuntimeError("pdfplumber is not installed. Install pdfplumber or use --parser auto.")

    if requested in {"auto", "pypdf"}:
        pypdf = import_optional("pypdf")
        if pypdf is not None:
            return "pypdf", pypdf
        pypdf2 = import_optional("PyPDF2")
        if pypdf2 is not None:
            return "PyPDF2", pypdf2
        if requested == "pypdf":
            raise RuntimeError("Neither pypdf nor PyPDF2 is installed.")

    raise RuntimeError(
        "No supported PDF parser found. Install one of: pymupdf, pdfplumber, pypdf, PyPDF2."
    )


def maybe_ocr_page(
    fitz: Any,
    page: Any,
    mode: str,
    native_text: str,
    min_chars: int,
    dpi: int,
    warnings: List[str],
) -> Tuple[str, bool, str]:
    if mode == "off":
        source = "native" if native_text else "empty"
        return native_text, False, source

    should_ocr = mode == "force" or len(native_text) < min_chars
    if not should_ocr:
        return native_text, False, "native"

    pytesseract = import_optional("pytesseract")
    pil_image = import_optional("PIL.Image")
    if pytesseract is None or pil_image is None:
        warnings.append("OCR requested but pytesseract or Pillow is not installed.")
        source = "native" if native_text else "empty"
        return native_text, False, source

    try:
        scale = dpi / 72.0
        pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
        image = pil_image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        ocr_text = clean_text(pytesseract.image_to_string(image))
    except Exception as exc:
        warnings.append(f"OCR failed: {exc}")
        source = "native" if native_text else "empty"
        return native_text, False, source

    if mode == "force":
        return ocr_text, True, "ocr" if ocr_text else "empty"

    if len(ocr_text) > max(len(native_text) * 1.2, min_chars):
        return ocr_text, True, "ocr"

    if ocr_text and native_text:
        return native_text, True, "native+ocr"
    return native_text or ocr_text, bool(ocr_text), "ocr" if ocr_text else "empty"


def extract_images_with_fitz(
    doc: Any,
    page: Any,
    page_number: int,
    image_dir: Path,
    warnings: List[str],
) -> List[Dict[str, Any]]:
    images: List[Dict[str, Any]] = []
    seen_xrefs = set()
    try:
        image_infos = page.get_images(full=True)
    except Exception as exc:
        warnings.append(f"Image listing failed on page {page_number}: {exc}")
        return images

    for idx, info in enumerate(image_infos, start=1):
        xref = info[0]
        if xref in seen_xrefs:
            continue
        seen_xrefs.add(xref)
        try:
            extracted = doc.extract_image(xref)
            ext = extracted.get("ext", "bin")
            data = extracted.get("image", b"")
            if not data:
                continue
            name = f"page-{page_number:04d}-image-{idx:02d}.{ext}"
            target = image_dir / name
            target.write_bytes(data)
            rects = page.get_image_rects(xref)
            bbox = list(rects[0]) if rects else None
            images.append(
                {
                    "image_id": f"p{page_number}-img{idx}",
                    "path": str(target),
                    "xref": xref,
                    "bbox": bbox,
                    "width": extracted.get("width"),
                    "height": extracted.get("height"),
                    "extension": ext,
                }
            )
        except Exception as exc:
            warnings.append(f"Image extraction failed on page {page_number}: {exc}")
    return images


def parse_with_pymupdf(path: Path, args: argparse.Namespace, warnings: List[str]) -> Dict[str, Any]:
    fitz = import_optional("fitz")
    if fitz is None:
        raise RuntimeError("PyMuPDF is not installed.")

    doc = fitz.open(str(path))
    image_dir = Path(args.out_dir) / "images"
    if args.extract_images:
        image_dir.mkdir(parents=True, exist_ok=True)

    pages: List[Dict[str, Any]] = []
    for page_index in range(len(doc)):
        page = doc[page_index]
        page_number = page_index + 1
        page_warnings: List[str] = []
        native_text = clean_text(page.get_text("text"))
        text, ocr_used, text_source = maybe_ocr_page(
            fitz,
            page,
            args.ocr,
            native_text,
            args.ocr_min_chars,
            args.ocr_dpi,
            page_warnings,
        )

        blocks: List[Dict[str, Any]] = []
        try:
            for block_index, block in enumerate(page.get_text("blocks"), start=1):
                if len(block) < 5:
                    continue
                block_text = clean_text(str(block[4]))
                if not block_text:
                    continue
                block_type = "text" if len(block) < 7 or block[6] == 0 else "image"
                blocks.append(
                    {
                        "block_id": f"p{page_number}-b{block_index}",
                        "type": block_type,
                        "bbox": [float(block[0]), float(block[1]), float(block[2]), float(block[3])],
                        "text": block_text,
                    }
                )
        except Exception as exc:
            page_warnings.append(f"Text block extraction failed: {exc}")

        images = []
        if args.extract_images:
            images = extract_images_with_fitz(doc, page, page_number, image_dir, page_warnings)

        rect = page.rect
        pages.append(
            {
                "page_number": page_number,
                "width": float(rect.width),
                "height": float(rect.height),
                "rotation": int(page.rotation),
                "text": text,
                "text_source": text_source,
                "text_blocks": blocks,
                "images": images,
                "quality": page_quality(text, args.ocr_min_chars, ocr_used),
                "warnings": page_warnings,
            }
        )

    toc = []
    try:
        for level, title, page_number in doc.get_toc(simple=True):
            toc.append({"level": level, "title": title, "page_number": page_number})
    except Exception as exc:
        warnings.append(f"TOC extraction failed: {exc}")

    return {
        "parser_name": "pymupdf",
        "metadata": normalize_metadata(doc.metadata),
        "document": {"page_count": len(pages), "toc": toc},
        "pages": pages,
        "image_extraction": "available" if args.extract_images else "disabled",
        "capabilities": {"text_blocks": True, "ocr": True, "images": True, "toc": True},
    }


def parse_with_pdfplumber(path: Path, args: argparse.Namespace, warnings: List[str]) -> Dict[str, Any]:
    pdfplumber = import_optional("pdfplumber")
    if pdfplumber is None:
        raise RuntimeError("pdfplumber is not installed.")

    pages: List[Dict[str, Any]] = []
    with pdfplumber.open(str(path)) as pdf:
        for page_index, page in enumerate(pdf.pages, start=1):
            page_warnings: List[str] = []
            try:
                text = clean_text(page.extract_text() or "")
            except Exception as exc:
                page_warnings.append(f"Text extraction failed: {exc}")
                text = ""

            if args.ocr == "force" or (args.ocr == "auto" and len(text) < args.ocr_min_chars):
                page_warnings.append("OCR requested but this parser cannot render pages; retry with PyMuPDF.")

            text_blocks = []
            if text:
                text_blocks.append(
                    {
                        "block_id": f"p{page_index}-b1",
                        "type": "text",
                        "bbox": [0.0, 0.0, float(page.width), float(page.height)],
                        "text": text,
                    }
                )

            pages.append(
                {
                    "page_number": page_index,
                    "width": float(page.width),
                    "height": float(page.height),
                    "rotation": int(getattr(page, "rotation", 0) or 0),
                    "text": text,
                    "text_source": "native" if text else "empty",
                    "text_blocks": text_blocks,
                    "images": [],
                    "quality": page_quality(text, args.ocr_min_chars, False),
                    "warnings": page_warnings,
                }
            )

        metadata = normalize_metadata(getattr(pdf, "metadata", {}) or {})

    return {
        "parser_name": "pdfplumber",
        "metadata": metadata,
        "document": {"page_count": len(pages), "toc": []},
        "pages": pages,
        "image_extraction": "unavailable" if args.extract_images else "disabled",
        "capabilities": {"text_blocks": False, "ocr": False, "images": False, "toc": False},
    }


def page_box_size(page: Any) -> Tuple[float, float]:
    box = getattr(page, "mediabox", None) or getattr(page, "mediaBox", None)
    if box is None:
        return 0.0, 0.0
    try:
        return float(box.width), float(box.height)
    except Exception:
        try:
            return float(box[2]) - float(box[0]), float(box[3]) - float(box[1])
        except Exception:
            return 0.0, 0.0


def parse_with_pypdf(path: Path, args: argparse.Namespace, warnings: List[str], module_name: str) -> Dict[str, Any]:
    module = import_optional(module_name)
    if module is None:
        raise RuntimeError(f"{module_name} is not installed.")

    reader = module.PdfReader(str(path))
    pages: List[Dict[str, Any]] = []
    for page_index, page in enumerate(reader.pages, start=1):
        page_warnings: List[str] = []
        try:
            text = clean_text(page.extract_text() or "")
        except Exception as exc:
            page_warnings.append(f"Text extraction failed: {exc}")
            text = ""

        if args.ocr == "force" or (args.ocr == "auto" and len(text) < args.ocr_min_chars):
            page_warnings.append("OCR requested but this parser cannot render pages; retry with PyMuPDF.")

        width, height = page_box_size(page)
        text_blocks = []
        if text:
            text_blocks.append(
                {
                    "block_id": f"p{page_index}-b1",
                    "type": "text",
                    "bbox": [0.0, 0.0, width, height],
                    "text": text,
                }
            )

        rotation = 0
        try:
            rotation = int(page.get("/Rotate", 0) or 0)
        except Exception:
            rotation = int(getattr(page, "rotation", 0) or 0)

        pages.append(
            {
                "page_number": page_index,
                "width": width,
                "height": height,
                "rotation": rotation,
                "text": text,
                "text_source": "native" if text else "empty",
                "text_blocks": text_blocks,
                "images": [],
                "quality": page_quality(text, args.ocr_min_chars, False),
                "warnings": page_warnings,
            }
        )

    return {
        "parser_name": module_name,
        "metadata": normalize_metadata(getattr(reader, "metadata", {}) or {}),
        "document": {"page_count": len(pages), "toc": []},
        "pages": pages,
        "image_extraction": "unavailable" if args.extract_images else "disabled",
        "capabilities": {"text_blocks": False, "ocr": False, "images": False, "toc": False},
    }


def iter_page_lines(pages: Iterable[Dict[str, Any]]) -> Iterable[Tuple[int, str]]:
    for page in pages:
        page_number = int(page["page_number"])
        for line in page.get("text", "").splitlines():
            line = line.strip()
            if line:
                yield page_number, line


def detect_sections(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sections: List[Dict[str, Any]] = []
    seen = set()
    for page_number, line in iter_page_lines(pages):
        if len(line) > 120:
            continue
        if SECTION_RE.search(line):
            key = (page_number, line.lower())
            if key in seen:
                continue
            seen.add(key)
            sections.append({"page_number": page_number, "heading": line})
    return sections


def detect_visual_hints(pages: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    figures: List[Dict[str, Any]] = []
    tables: List[Dict[str, Any]] = []
    for page_number, line in iter_page_lines(pages):
        if len(line) > 600:
            continue
        figure_match = FIGURE_RE.match(line)
        if figure_match:
            figures.append({"page_number": page_number, "caption": line})
            continue
        table_match = TABLE_RE.match(line)
        if table_match:
            tables.append({"page_number": page_number, "caption": line})
    return figures, tables


def detect_formula_hints(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    formulas: List[Dict[str, Any]] = []
    for page_number, line in iter_page_lines(pages):
        if len(line) > 220:
            continue
        if FIGURE_RE.match(line) or TABLE_RE.match(line):
            continue
        symbol_count = len(re.findall(r"[=+\-*/^_<>]", line))
        if symbol_count >= 2 or FORMULA_RE.search(line):
            formulas.append({"page_number": page_number, "text": line})
    return formulas[:200]


def document_quality(pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    page_count = len(pages)
    low_text_pages = [
        page["page_number"] for page in pages if page.get("quality", {}).get("low_text", False)
    ]
    total_chars = sum(page.get("quality", {}).get("char_count", 0) for page in pages)
    text_pages = sum(1 for page in pages if page.get("quality", {}).get("char_count", 0) > 0)
    return {
        "page_count": page_count,
        "text_pages": text_pages,
        "low_text_pages": low_text_pages,
        "total_chars": total_chars,
        "avg_chars_per_page": round(total_chars / page_count, 2) if page_count else 0,
        "needs_ocr_review": bool(low_text_pages),
    }


def infer_status_and_confidence(quality: Dict[str, Any], warnings: List[str], page_warnings: List[str]) -> Tuple[str, str]:
    if quality["page_count"] == 0:
        return "blocked", "low"
    if quality["text_pages"] == 0:
        return "blocked", "low"
    low_ratio = len(quality["low_text_pages"]) / max(quality["page_count"], 1)
    if low_ratio > 0.5 or any("OCR requested" in warning for warning in page_warnings):
        return "partial", "low"
    if warnings or page_warnings or low_ratio > 0.1:
        return "partial", "medium"
    if quality["avg_chars_per_page"] >= 800:
        return "complete", "high"
    return "complete", "medium"


def guess_title(metadata: Dict[str, str], pages: List[Dict[str, Any]]) -> Optional[str]:
    title = metadata.get("title")
    if title and len(title) > 4:
        return title
    if not pages:
        return None
    for line in pages[0].get("text", "").splitlines()[:20]:
        line = line.strip()
        if 8 <= len(line) <= 220 and not re.search(r"^(arxiv|abstract|proceedings|conference)\b", line, re.I):
            return line
    return None


def build_markdown(result: Dict[str, Any]) -> str:
    ingestion = result["ingestion"]
    quality = ingestion["quality"]
    lines: List[str] = []
    lines.append("# Parsed Paper")
    lines.append("")
    lines.append(f"- Paper ID: {result['paper_id']}")
    lines.append(f"- Source: {ingestion['source']['path']}")
    lines.append(f"- Parser: {ingestion['parser']['name']}")
    lines.append(f"- Status: {result['status']}")
    lines.append(f"- Confidence: {result['confidence']}")
    lines.append("")
    lines.append("## Quality")
    lines.append("")
    lines.append(f"- Pages: {quality['page_count']}")
    lines.append(f"- Text pages: {quality['text_pages']}")
    lines.append(f"- Low-text pages: {quality['low_text_pages']}")
    if result["warnings"]:
        lines.append(f"- Warnings: {'; '.join(result['warnings'])}")
    else:
        lines.append("- Warnings: none")
    lines.append("")

    metadata = ingestion.get("metadata", {})
    if metadata:
        lines.append("## Metadata")
        lines.append("")
        for key in sorted(metadata):
            lines.append(f"- {key}: {metadata[key]}")
        lines.append("")

    if ingestion.get("document", {}).get("toc"):
        lines.append("## Table of Contents")
        lines.append("")
        for item in ingestion["document"]["toc"]:
            indent = "  " * max(int(item.get("level", 1)) - 1, 0)
            lines.append(f"- {indent}{item.get('title', '')} (page {item.get('page_number', '')})")
        lines.append("")

    if ingestion.get("sections_hint"):
        lines.append("## Detected Section Hints")
        lines.append("")
        for item in ingestion["sections_hint"]:
            lines.append(f"- Page {item['page_number']}: {item['heading']}")
        lines.append("")

    lines.append("## Page Text")
    lines.append("")
    for page in ingestion["pages"]:
        page_number = page["page_number"]
        lines.append(f'<a id="page-{page_number}"></a>')
        lines.append("")
        lines.append(f"### Page {page_number}")
        lines.append("")
        if page.get("warnings"):
            lines.append(f"_Warnings: {'; '.join(page['warnings'])}_")
            lines.append("")
        text = page.get("text", "").strip()
        lines.append(text if text else "_No extractable text detected._")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def make_result(path: Path, args: argparse.Namespace) -> Dict[str, Any]:
    warnings: List[str] = []
    parser_name, _parser_module = choose_parser(args.parser)

    if parser_name == "pymupdf":
        parsed = parse_with_pymupdf(path, args, warnings)
    elif parser_name == "pdfplumber":
        parsed = parse_with_pdfplumber(path, args, warnings)
    elif parser_name in {"pypdf", "PyPDF2"}:
        parsed = parse_with_pypdf(path, args, warnings, parser_name)
    else:
        raise RuntimeError(f"Unsupported parser: {parser_name}")

    pages = parsed["pages"]
    sections = detect_sections(pages)
    figures, tables = detect_visual_hints(pages)
    formulas = detect_formula_hints(pages)
    quality = document_quality(pages)
    all_page_warnings = [
        warning for page in pages for warning in page.get("warnings", [])
    ]
    status, confidence = infer_status_and_confidence(quality, warnings, all_page_warnings)

    paper_id = args.paper_id or path.stem
    ingestion = {
        "schema": SCHEMA_VERSION,
        "source": {
            "type": "pdf",
            "path": str(path.resolve()),
            "sha256": sha256_file(path),
        },
        "parser": {
            "name": parsed["parser_name"],
            "ocr": args.ocr,
            "image_extraction": parsed["image_extraction"],
            "capabilities": parsed["capabilities"],
        },
        "metadata": parsed["metadata"],
        "document": parsed["document"],
        "pages": pages,
        "sections_hint": sections,
        "figures_hint": figures,
        "tables_hint": tables,
        "formulas_hint": formulas,
        "quality": quality,
    }

    findings: List[Dict[str, str]] = []
    title = guess_title(parsed["metadata"], pages)
    if title:
        findings.append(
            {
                "claim": f"Detected likely title: {title}",
                "evidence": "metadata or page 1 text",
                "confidence": "medium" if title != parsed["metadata"].get("title") else "high",
            }
        )
    findings.append(
        {
            "claim": f"Extracted {quality['text_pages']} text pages from {quality['page_count']} pages.",
            "evidence": "document quality summary",
            "confidence": confidence,
        }
    )

    result = {
        "skill": "paper-ingestion",
        "paper_id": paper_id,
        "status": status,
        "confidence": confidence,
        "artifacts": [],
        "findings": findings,
        "handoff": {
            "recommended_next_skills": ["paper-decomposition"],
            "state_patch": {
                "ingestion": {
                    "source_path": str(path.resolve()),
                    "pages": [
                        {
                            "page_number": page["page_number"],
                            "char_count": page["quality"]["char_count"],
                            "text_source": page["text_source"],
                            "warnings": page["warnings"],
                        }
                        for page in pages
                    ],
                    "sections_hint": sections,
                    "figures_hint": figures,
                    "tables_hint": tables,
                    "formulas_hint": formulas,
                    "quality": quality,
                }
            },
        },
        "warnings": warnings + all_page_warnings,
        "ingestion": ingestion,
    }
    return result


def write_outputs(result: Dict[str, Any], out_dir: Path, output_prefix: str, write_json: bool, write_markdown: bool) -> Dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    artifacts: List[Dict[str, Any]] = []

    if write_json:
        json_path = out_dir / f"{output_prefix}.json"
        json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        artifacts.append(
            {
                "type": "json",
                "path": str(json_path),
                "description": "page, block, metadata, and quality package",
            }
        )

    if write_markdown:
        markdown_path = out_dir / f"{output_prefix}.md"
        markdown_path.write_text(build_markdown(result), encoding="utf-8")
        artifacts.append(
            {
                "type": "markdown",
                "path": str(markdown_path),
                "description": "reading-order text with page anchors",
            }
        )

    result["artifacts"] = artifacts

    if write_json:
        json_path = out_dir / f"{output_prefix}.json"
        json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse an academic PDF into paper-ingestion JSON and Markdown artifacts."
    )
    parser.add_argument("pdf", help="Path to the source PDF.")
    parser.add_argument("--out-dir", default="parsed-paper", help="Directory for generated artifacts.")
    parser.add_argument("--paper-id", default="", help="Stable paper id. Defaults to PDF stem.")
    parser.add_argument("--output-prefix", default="parsed-paper", help="Output filename prefix.")
    parser.add_argument(
        "--parser",
        choices=["auto", "pymupdf", "pdfplumber", "pypdf"],
        default="auto",
        help="PDF backend to use.",
    )
    parser.add_argument(
        "--ocr",
        choices=["auto", "force", "off"],
        default="auto",
        help="OCR mode. OCR requires PyMuPDF, Pillow, and pytesseract.",
    )
    parser.add_argument(
        "--ocr-min-chars",
        type=int,
        default=200,
        help="Native text chars below this threshold trigger OCR in auto mode.",
    )
    parser.add_argument("--ocr-dpi", type=int, default=200, help="Rendering DPI for OCR.")
    parser.add_argument("--extract-images", action="store_true", help="Extract embedded images when supported.")
    parser.add_argument("--json-only", action="store_true", help="Write JSON only.")
    parser.add_argument("--markdown-only", action="store_true", help="Write Markdown only.")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"error: PDF not found: {pdf_path}", file=sys.stderr)
        return 2
    if not pdf_path.is_file():
        print(f"error: source is not a file: {pdf_path}", file=sys.stderr)
        return 2

    if args.json_only and args.markdown_only:
        print("error: choose only one of --json-only or --markdown-only", file=sys.stderr)
        return 2

    try:
        result = make_result(pdf_path, args)
        write_json = not args.markdown_only
        write_markdown = not args.json_only
        result = write_outputs(
            result,
            Path(args.out_dir),
            args.output_prefix,
            write_json=write_json,
            write_markdown=write_markdown,
        )
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(
        {
            "status": result["status"],
            "confidence": result["confidence"],
            "paper_id": result["paper_id"],
            "artifacts": result["artifacts"],
            "warnings": result["warnings"],
        },
        indent=2,
        ensure_ascii=False,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
