"""Regenerate the clearly fictional Tender Clarity PDF fixture."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "fixtures" / "synthetic_cleaning_tender.pdf"
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="FixtureTitle", parent=styles["Title"], textColor=colors.HexColor("#12372A"), fontSize=18, leading=22, spaceAfter=8))
styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], textColor=colors.HexColor("#176B52"), spaceBefore=9, spaceAfter=4))
styles.add(ParagraphStyle(name="Body", parent=styles["BodyText"], leading=15, spaceAfter=6))
styles.add(ParagraphStyle(name="Notice", parent=styles["BodyText"], backColor=colors.HexColor("#FFF1C2"), borderPadding=7, spaceAfter=10, fontSize=9))
def p(text, style="Body"):
    return Paragraph(text, styles[style])
def stamp(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#66736C"))
    canvas.drawString(20 * mm, 12 * mm, "SYNTHETIC TEST DOCUMENT - NOT A REAL PROCUREMENT")
    canvas.drawRightString(A4[0] - 20 * mm, 12 * mm, f"Page {doc.page}")
    canvas.restoreState()
story = [
    p("SYNTHETIC TEST TENDER", "FixtureTitle"),
    p("<b>TEST MATERIAL ONLY:</b> This fictional sample was created for Tender Clarity software testing. It is not an actual tender and contains no real organisation or personal information.", "Notice"),
    p("Tender reference: TC-SYN-2026-001<br/>Issuing organisation: Fictional Sample Municipality<br/>Issue date: 1 October 2026"),
    p("1. Scope of work", "Section"),
    p("Provide routine cleaning services for the fictional Civic Office and Works Depot. The contract period is 12 months, from 1 November 2026 to 31 October 2027."),
    p("2. Mandatory eligibility", "Section"),
    p("A bidder must submit valid evidence of tax compliance with its bid. Failure to include the tax-compliance evidence makes the bid non-responsive."),
    p("3. Submission deadline", "Section"),
    p("Bids open on 1 October 2026. The closing deadline is 30 October 2026 at 11:00 South African Standard Time. Late bids will not be accepted."),
    p("4. Evaluation", "Section"),
    p("Price is worth 80 points. Specific-goal preference is worth 20 points. The highest total score is evaluated for award, subject to responsiveness and the stated conditions."),
    p("5. Staffing reference", "Section"),
    p("The tenderer must provide personnel according to the weekend coverage in clause 8 and include staffing numbers in the work plan. Read clause 8 on the next page to identify the coverage schedule."),
    PageBreak(),
    p("SYNTHETIC TEST TENDER - CONTINUED", "FixtureTitle"),
    p("6. Pricing information", "Section"),
    p("Submit one monthly service price for the full 12-month period. The price must include labour, transport, equipment and cleaning consumables."),
    p("7. Cleaning consumables - clarification needed", "Section"),
    p("The municipality may provide some cleaning consumables when available. No list of items, quantities, or supply dates is provided. Bidders should ask which party is responsible for each consumable before finalising the cost calculation."),
    p("8. Weekend coverage schedule", "Section"),
    p("For the Civic Office, the tenderer must provide two cleaners from 08:00 to 16:00 on Saturdays and one cleaner from 08:00 to 12:00 on Sundays. One supervisor must be responsible for the weekend team."),
    p("For the Works Depot, one cleaner is required on Saturdays from 09:00 to 13:00. The tender does not state whether the supervisor may also perform cleaning work; request clarification if this changes the staffing calculation."),
    p("Fixture examples for analysis", "Section"),
    p("This sample intentionally includes a direct mandatory requirement, dates, evaluation points, cost information, an incomplete consumables instruction, and a staffing requirement whose cross-page interpretation links clause 5 on page 1 with clause 8 on page 2."),
]
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=18*mm, bottomMargin=20*mm, title="Synthetic Tender Clarity Test Fixture")
doc.build(story, onFirstPage=stamp, onLaterPages=stamp)
print(f"Created {OUTPUT} ({OUTPUT.stat().st_size} bytes)")
