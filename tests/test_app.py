"""Streamlit screen and checklist interaction checks with controlled data."""
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest
from tender_clarity.pdf_reader import extract_pages
from tender_clarity.sources import validate_result_sources

ROOT = Path(__file__).resolve().parents[1]


def controlled_analysis():
    source_tax = {"page": 1, "section": "2. Mandatory eligibility", "excerpt": "Failure to include the tax-compliance evidence makes the bid non-responsive.", "verified": True}
    source_unclear = {"page": 2, "section": "7. Cleaning consumables", "excerpt": "No list of items, quantities, or supply dates is provided.", "verified": True}
    source_staff_1 = {"page": 1, "section": "5. Staffing reference", "excerpt": "Read clause 8 on the next page to identify the coverage schedule.", "verified": True}
    source_staff_2 = {"page": 2, "section": "8. Weekend coverage schedule", "excerpt": "For the Civic Office, the tenderer must provide two cleaners from 08:00 to 16:00 on Saturdays and one cleaner from 08:00 to 12:00 on Sundays.", "verified": True}
    return {
        "overview": {"title": "Synthetic cleaning tender", "reference": "TC-SYN-2026-001", "issuer": "Fictional Sample Municipality", "opening_date": "1 October 2026", "submission_date": "30 October 2026 at 11:00", "contract_period": "12 months", "scope": "Fictional cleaning services", "eligibility_summary": "Tax evidence required", "what_matters_most": "Deadline and mandatory tax evidence"},
        "findings": [
            {"id": "tax-finding", "category": "STATED", "title": "Tax evidence is mandatory", "explanation": "A bidder must submit tax evidence.", "why_it_matters": "Omission makes the bid non-responsive.", "priority": "CRITICAL", "missing_information": "", "source_refs": [source_tax]},
            {"id": "staff-finding", "category": "CONCLUSION", "title": "Plan weekend staff", "explanation": "The staffing plan should include the cited weekend schedule.", "why_it_matters": "The staffing clause refers to a later schedule.", "priority": "IMPORTANT", "missing_information": "", "source_refs": [source_staff_1, source_staff_2]},
            {"id": "materials-finding", "category": "UNCLEAR", "title": "Consumables need clarification", "explanation": "Supply details are incomplete.", "why_it_matters": "The contractor needs this for pricing.", "priority": "IMPORTANT", "missing_information": "Items, quantities, and supply dates.", "source_refs": [source_unclear]},
        ],
        "checklist": [
            {"id": "tax-action", "finding_id": "tax-finding", "action": "Confirm tax-compliance evidence", "why_it_matters": "It is mandatory and omission can make the bid non-responsive.", "required": "Valid tax-compliance evidence", "completion_evidence": "The current evidence file is ready to include.", "importance": "CRITICAL", "optional": False, "status": "TO_DO", "source_refs": [source_tax]},
            {"id": "materials-action", "finding_id": "materials-finding", "action": "Clarify cleaning consumables", "why_it_matters": "The supply arrangement affects costs.", "required": "A list and quantities of supplied consumables", "completion_evidence": "The authority's answer is recorded and the cost plan updated.", "importance": "IMPORTANT", "optional": False, "status": "NEEDS_CLARIFICATION", "source_refs": [source_unclear]},
        ],
        "next_actions": [{"action": "Confirm tax evidence is ready.", "related_ids": ["tax-action"]}],
    }


class StreamlitChecklistTests(unittest.TestCase):
    def test_home_screen_renders_upload_and_privacy_warning(self):
        app = AppTest.from_file(str(ROOT / "app.py")).run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.file_uploader), 1)
        self.assertEqual(len(app.button), 0)  # The Analyse button appears after a PDF is selected.
        self.assertTrue(app.warning)
        self.assertTrue(any("Tender Clarity" in (item.value or "") for item in app.markdown))

    def test_controlled_results_allow_checking_actions_without_gemini(self):
        app = AppTest.from_file(str(ROOT / "app.py")).run()
        fixture = ROOT / "fixtures" / "synthetic_cleaning_tender.pdf"
        pages = extract_pages(fixture.name, fixture.read_bytes())
        page_texts = {page.number: page.text for page in pages}
        analysis = validate_result_sources(controlled_analysis(), page_texts)
        all_refs = [ref for item in analysis["findings"] + analysis["checklist"] for ref in item["source_refs"]]
        self.assertTrue(all(ref["verified"] for ref in all_refs))
        app.session_state["analysis"] = analysis
        app.session_state["pages"] = page_texts
        app.session_state["filename"] = fixture.name
        app.session_state["checklist_statuses"] = {}
        app.session_state["analysis_version"] = 1
        app.run()

        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "0 of 2 completed")
        self.assertEqual(app.metric[1].value, "1")
        self.assertTrue(any("Needs clarification" in item.value for item in app.warning))
        self.assertTrue(any("page 1" in item.label for item in app.expander))

        app.checkbox(key="checklist_done_1_tax-action").check().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "1 of 2 completed")
        self.assertEqual(app.metric[1].value, "0")
        self.assertEqual(app.session_state["checklist_statuses"]["tax-action"], "COMPLETED")
        self.assertEqual(app.session_state["checklist_statuses"]["materials-action"], "NEEDS_CLARIFICATION")

        app.checkbox(key="checklist_done_1_materials-action").check().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "2 of 2 completed")
        self.assertEqual(app.session_state["checklist_statuses"]["materials-action"], "COMPLETED")

        app.checkbox(key="checklist_done_1_tax-action").uncheck().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "1 of 2 completed")
        self.assertEqual(app.metric[1].value, "1")
        self.assertEqual(app.session_state["checklist_statuses"]["tax-action"], "TO_DO")


if __name__ == "__main__":
    unittest.main()
