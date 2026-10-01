"""Build a complete Tender Clarity report in memory as PDF bytes."""

from io import BytesIO
from typing import Any, Mapping
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, KeepTogether

from tender_clarity.costs import calculate_costs


def _text(value: Any) -> str:
    return escape(str(value if value not in (None, "") else "Not stated")).replace("\n", "<br/>")


def _paragraph(label: str, value: Any, style: ParagraphStyle) -> Paragraph:
    return Paragraph(f"<b>{_text(label)}:</b> {_text(value)}", style)


def generate_report(
    analysis: Mapping[str, Any],
    checklist_statuses: Mapping[str, str],
    cost_items: Mapping[str, Any],
    expected_contract_value: Any,
) -> bytes:
    """Generate the complete report from current session values, without saving it."""
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="Tender Clarity report",
        author="Tender Clarity",
    )
    base = getSampleStyleSheet()
    title_style = ParagraphStyle("TenderTitle", parent=base["Title"], textColor=colors.HexColor("#12372a"), alignment=TA_CENTER, spaceAfter=8)
    heading_style = ParagraphStyle("TenderHeading", parent=base["Heading2"], textColor=colors.HexColor("#176b52"), spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle("TenderBody", parent=base["BodyText"], leading=14, spaceAfter=5)
    small_style = ParagraphStyle("TenderSmall", parent=body_style, fontSize=8.5, leading=11, leftIndent=10, textColor=colors.HexColor("#47564f"))

    story = [
        Paragraph("Tender Clarity", title_style),
        Paragraph("Tender preparation report", base["Heading2"]),
        Paragraph("Use this report to understand the tender and organize preparation. Verify important requirements against the original tender.", body_style),
    ]

    overview = analysis.get("overview", {})
    story.append(Paragraph("Tender overview", heading_style))
    for label, key in (
        ("Tender title", "title"),
        ("Reference", "reference"),
        ("Issuing organisation", "issuer"),
        ("Opening date", "opening_date"),
        ("Submission deadline", "submission_date"),
        ("Contract period", "contract_period"),
        ("Scope", "scope"),
        ("Eligibility summary", "eligibility_summary"),
        ("What matters most", "what_matters_most"),
    ):
        story.append(_paragraph(label, overview.get(key), body_style))

    story.append(Paragraph("Important findings", heading_style))
    story.append(Paragraph("STATED means the tender says this. CONCLUSION means Tender Clarity derived it from the tender. UNCLEAR means the document does not provide enough information. An AI conclusion is an interpretation, not a direct tender quote.", body_style))
    findings = analysis.get("findings", [])
    if not findings:
        story.append(Paragraph("No findings were returned. Review the tender directly.", body_style))
    for finding in findings:
        category = str(finding.get("category", "UNCLEAR")).upper()
        story.append(Paragraph(f"{_text(category)} - {_text(finding.get('title', 'Finding'))}", base["Heading3"]))
        story.append(_paragraph("Explanation", finding.get("explanation"), body_style))
        if finding.get("why_it_matters"):
            story.append(_paragraph("Why it matters", finding["why_it_matters"], body_style))
        if category == "UNCLEAR":
            story.append(_paragraph("Unclear / needs clarification", finding.get("missing_information") or finding.get("explanation"), body_style))
        refs = finding.get("source_refs", [])
        if refs:
            story.append(Paragraph("Sources", body_style))
            for ref in refs:
                page = ref.get("page", "unknown")
                section = ref.get("section") or "Section not stated"
                if ref.get("verified"):
                    story.append(Paragraph(f"Verified source - page {_text(page)}, {_text(section)}", small_style))
                    if ref.get("excerpt"):
                        story.append(Paragraph(f"Verified excerpt: {_text(ref['excerpt'])}", small_style))
                else:
                    story.append(Paragraph(f"UNVERIFIED source reference - page {_text(page)}, {_text(section)}. Do not rely on this as proof.", small_style))
                    if ref.get("excerpt"):
                        story.append(Paragraph(f"Unverified model excerpt: {_text(ref['excerpt'])}", small_style))
        else:
            story.append(Paragraph("No source reference was provided. Verify this finding in the original tender.", small_style))

    story.append(Paragraph("Preparation checklist", heading_style))
    checklist = analysis.get("checklist", [])
    completed = 0
    if not checklist:
        story.append(Paragraph("No checklist actions were returned.", body_style))
    for index, item in enumerate(checklist, start=1):
        item_id = item.get("id") or f"item-{index}"
        status = checklist_statuses.get(item_id, item.get("status", "TO_DO"))
        if status == "COMPLETED":
            completed += 1
        action = item.get("action", "Preparation task")
        group = [Paragraph(f"{index}. {_text(action)} - {_text(status.replace('_', ' ').title())}", base["Heading3"])]
        if item.get("why_it_matters"):
            group.append(_paragraph("Why it matters", item["why_it_matters"], body_style))
        if item.get("required"):
            group.append(_paragraph("What is needed", item["required"], body_style))
        if item.get("completion_evidence"):
            group.append(_paragraph("How to know it is complete", item["completion_evidence"], body_style))
        group.append(_paragraph("Importance", item.get("importance", "IMPORTANT"), body_style))
        for ref in item.get("source_refs", []):
            if ref.get("verified"):
                group.append(Paragraph(f"Verified checklist source - page {_text(ref.get('page', 'unknown'))}, {_text(ref.get('section') or 'Section not stated')}", small_style))
                if ref.get("excerpt"):
                    group.append(Paragraph(f"Verified excerpt: {_text(ref['excerpt'])}", small_style))
            else:
                group.append(Paragraph(f"UNVERIFIED checklist source - page {_text(ref.get('page', 'unknown'))}. Do not rely on this as proof.", small_style))
        story.append(KeepTogether(group))
    story.append(_paragraph("Checklist progress", f"{completed} of {len(checklist)} completed", body_style))

    next_actions = analysis.get("next_actions", [])
    story.append(Paragraph("Next actions", heading_style))
    if next_actions:
        for index, action in enumerate(next_actions, start=1):
            text = action.get("action", "") if isinstance(action, Mapping) else str(action)
            if text:
                story.append(Paragraph(f"{index}. {_text(text)}", body_style))
    else:
        story.append(Paragraph("No next actions were returned.", body_style))

    story.append(Paragraph("Cost worksheet (ZAR estimates)", heading_style))
    cost_result = calculate_costs(cost_items, expected_contract_value)
    cost_labels = {
        "labour": "Labour", "materials": "Materials", "transport": "Transport",
        "equipment": "Equipment", "overheads": "Overheads", "other": "Other expenses",
    }
    for key, label in cost_labels.items():
        story.append(_paragraph(label, f"R {cost_result['cost_items'].get(key, 0):,.2f}", body_style))
    story.extend([
        _paragraph("Total estimated costs", f"R {cost_result['total_estimated_costs']:,.2f}", body_style),
        _paragraph("Entered expected / benchmark contract value", f"R {cost_result['expected_contract_value']:,.2f}", body_style),
        _paragraph("Amount remaining after listed costs", f"R {cost_result['amount_remaining']:,.2f}", body_style),
    ])
    if cost_result["margin_percent"] is None:
        story.append(_paragraph("Estimated margin", "Not available because the entered contract value is R 0.00.", body_style))
    else:
        story.append(_paragraph("Estimated margin", f"{cost_result['margin_percent']:.2f}%", body_style))
    if cost_result["below_estimated_cost"]:
        story.append(Paragraph("WARNING: The entered contract value is below the estimated costs entered by the contractor.", body_style))

    story.append(Paragraph("Important limits", heading_style))
    story.append(Paragraph("Cost figures and margin are estimates based only on contractor-entered amounts. They are not accounting or financial advice and do not recommend what price to bid. Tender Clarity does not predict or guarantee a tender outcome. Verify requirements, source excerpts, and unresolved questions in the original tender before submission.", body_style))
    document.build(story)
    return buffer.getvalue()