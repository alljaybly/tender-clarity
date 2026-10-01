"""PDF report generation keeps current evidence, checklist, and cost details."""
import unittest
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

from tender_clarity.report import generate_report


class ReportGenerationTests(unittest.TestCase):
    def sample_analysis(self):
        return {
            "overview": {
                "title": "Synthetic cleaning tender",
                "reference": "TC-SYN-2026-001",
                "issuer": "Fictional Sample Municipality",
                "opening_date": "1 October 2026",
                "submission_date": "30 October 2026 at 11:00",
                "contract_period": "12 months",
                "scope": "Fictional cleaning services",
                "eligibility_summary": "Tax evidence required",
                "what_matters_most": "Deadline and mandatory tax evidence",
            },
            "findings": [
                {"id": "f1", "category": "STATED", "title": "Mandatory certificate", "explanation": "Include the valid certificate.", "why_it_matters": "Omission can make the bid non-responsive.", "source_refs": [{"page": 1, "section": "2. Eligibility", "excerpt": "A valid certificate must be submitted with the bid.", "verified": True}]},
                {"id": "f2", "category": "CONCLUSION", "title": "Plan weekend staffing", "explanation": "The work plan should include weekend coverage.", "why_it_matters": "The staffing clause points to a later schedule.", "source_refs": [{"page": 1, "section": "5. Staffing", "excerpt": "Read clause 8 for the weekend schedule.", "verified": True}]},
                {"id": "f3", "category": "UNCLEAR", "title": "Consumables need clarification", "explanation": "Supply details are incomplete.", "why_it_matters": "This affects pricing.", "missing_information": "Items, quantities, and supply dates are not stated.", "source_refs": [{"page": 2, "section": "7. Consumables", "excerpt": "No list of items or quantities is provided.", "verified": False}]},
            ],
            "checklist": [
                {"id": "a1", "action": "Confirm certificate is ready", "why_it_matters": "Mandatory submission item.", "required": "Valid certificate", "completion_evidence": "File is ready to include.", "importance": "CRITICAL", "status": "TO_DO", "source_refs": [{"page": 1, "section": "2. Eligibility", "excerpt": "A valid certificate must be submitted with the bid.", "verified": True}]},
                {"id": "a2", "action": "Clarify consumables allocation", "why_it_matters": "It affects the cost estimate.", "required": "Authority response", "completion_evidence": "Answer recorded and plan updated.", "importance": "IMPORTANT", "status": "NEEDS_CLARIFICATION", "source_refs": [{"page": 2, "section": "7. Consumables", "excerpt": "No list of items or quantities is provided.", "verified": False}]},
            ],
            "next_actions": [{"action": "Ask who supplies consumables.", "related_ids": ["a2"]}],
        }

    def test_pdf_contains_overview_findings_sources_checklist_and_costs(self):
        costs = {"labour": 1000, "materials": 500, "transport": 100, "equipment": 200, "overheads": 150, "other": 50}
        pdf_bytes = generate_report(self.sample_analysis(), {"a1": "COMPLETED"}, costs, 2500)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))
        reader = PdfReader(BytesIO(pdf_bytes))
        text = " ".join(page.extract_text() or "" for page in reader.pages)

        expected_content = [
            "Tender preparation report", "Fictional Sample Municipality", "30 October 2026 at 11:00",
            "STATED", "CONCLUSION", "UNCLEAR", "Verified source - page 1",
            "Verified excerpt: A valid certificate must be submitted with the bid.",
            "UNVERIFIED source reference - page 2", "Unverified model excerpt",
            "Confirm certificate is ready", "Completed", "Clarify consumables allocation",
            "Needs Clarification", "1 of 2 completed", "Ask who supplies consumables.",
            "Total estimated costs", "R 2,000.00", "R 2,500.00", "R 500.00", "20.00%",
            "estimates based only", "not accounting or financial advice",
        ]
        normalized = " ".join(text.split())
        for phrase in expected_content:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, normalized)

    def test_zero_contract_value_is_reported_without_inventing_margin(self):
        pdf_bytes = generate_report(self.sample_analysis(), {}, {"labour": 100}, 0)
        text = " ".join(page.extract_text() or "" for page in PdfReader(BytesIO(pdf_bytes)).pages)
        self.assertIn("Not available because the entered contract value is R 0.00", text)
        self.assertIn("WARNING: The entered contract value is below the estimated costs", text)


if __name__ == "__main__":
    unittest.main()