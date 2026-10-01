"""Provider-neutral Tender Clarity response shape and validation."""

from __future__ import annotations

from typing import Any

CATEGORIES = {"STATED", "CONCLUSION", "UNCLEAR"}

ANALYSIS_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "overview": {"type": "OBJECT", "properties": {
            "title": {"type": "STRING"}, "reference": {"type": "STRING"},
            "issuer": {"type": "STRING"}, "opening_date": {"type": "STRING"},
            "submission_date": {"type": "STRING"}, "contract_period": {"type": "STRING"},
            "scope": {"type": "STRING"}, "eligibility_summary": {"type": "STRING"},
            "what_matters_most": {"type": "STRING"},
        }, "required": ["title", "reference", "issuer", "opening_date", "submission_date", "contract_period", "scope", "eligibility_summary", "what_matters_most"]},
        "findings": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "id": {"type": "STRING"}, "category": {"type": "STRING", "enum": ["STATED", "CONCLUSION", "UNCLEAR"]},
            "title": {"type": "STRING"}, "explanation": {"type": "STRING"},
            "why_it_matters": {"type": "STRING"}, "priority": {"type": "STRING", "enum": ["CRITICAL", "IMPORTANT", "OPTIONAL"]},
            "missing_information": {"type": "STRING"},
            "source_refs": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
                "page": {"type": "INTEGER"}, "section": {"type": "STRING"}, "excerpt": {"type": "STRING"}
            }, "required": ["page", "section", "excerpt"]}}
        }, "required": ["id", "category", "title", "explanation", "why_it_matters", "priority", "missing_information", "source_refs"]}},
        "checklist": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "id": {"type": "STRING"}, "finding_id": {"type": "STRING"}, "action": {"type": "STRING"},
            "why_it_matters": {"type": "STRING"}, "required": {"type": "STRING"},
            "completion_evidence": {"type": "STRING"}, "importance": {"type": "STRING", "enum": ["CRITICAL", "IMPORTANT", "OPTIONAL"]},
            "optional": {"type": "BOOLEAN"}, "status": {"type": "STRING", "enum": ["TO_DO", "COMPLETED", "NEEDS_CLARIFICATION"]},
            "source_refs": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
                "page": {"type": "INTEGER"}, "section": {"type": "STRING"}, "excerpt": {"type": "STRING"}
            }, "required": ["page", "section", "excerpt"]}}
        }, "required": ["id", "finding_id", "action", "why_it_matters", "required", "completion_evidence", "importance", "optional", "status", "source_refs"]}},
        "next_actions": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "action": {"type": "STRING"}, "related_ids": {"type": "ARRAY", "items": {"type": "STRING"}}
        }, "required": ["action", "related_ids"]}}
    },
    "required": ["overview", "findings", "checklist", "next_actions"]
}


def validate_analysis(data: Any) -> dict[str, Any]:
    """Reject malformed model output before it reaches the interface."""
    if not isinstance(data, dict) or not all(k in data for k in ("overview", "findings", "checklist", "next_actions")):
        raise ValueError("The analysis response is missing required sections.")
    if not isinstance(data["overview"], dict) or not isinstance(data["findings"], list):
        raise ValueError("The analysis response has an invalid overview or findings list.")
    if not isinstance(data["checklist"], list) or not isinstance(data["next_actions"], list):
        raise ValueError("The analysis response has an invalid checklist or next-actions list.")
    for finding in data["findings"]:
        if not isinstance(finding, dict) or finding.get("category") not in CATEGORIES:
            raise ValueError("A finding has an invalid evidence category.")
        if not isinstance(finding.get("source_refs"), list):
            raise ValueError("A finding has invalid source references.")
    return data
