"""Validate AI source excerpts against text extracted from the same page."""

import re
from typing import Any


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def validate_source_ref(ref: dict[str, Any], page_texts: dict[int, str]) -> bool:
    page = ref.get("page")
    excerpt = ref.get("excerpt")
    if not isinstance(page, int) or isinstance(page, bool) or page not in page_texts:
        return False
    if not isinstance(excerpt, str) or len(normalize_text(excerpt)) < 12:
        return False
    return normalize_text(excerpt) in normalize_text(page_texts[page])


def validate_result_sources(result: dict[str, Any], page_texts: dict[int, str]) -> dict[str, Any]:
    """Add an app-owned verification flag; never trust an AI-supplied flag."""
    for finding in result.get("findings", []):
        for ref in finding.get("source_refs", []):
            ref["verified"] = validate_source_ref(ref, page_texts)
    for item in result.get("checklist", []):
        for ref in item.get("source_refs", []):
            ref["verified"] = validate_source_ref(ref, page_texts)
    return result
