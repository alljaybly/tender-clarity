"""Evidence categories and returned citation checks use only the extracted page text."""
import json
import unittest
from pathlib import Path

from tender_clarity.analysis import AnalysisError, analyze_pages
from tender_clarity.models import validate_analysis
from tender_clarity.pdf_reader import extract_pages
from tender_clarity.sources import validate_result_sources, validate_source_ref

ROOT = Path(__file__).resolve().parents[1]


def fixture_result():
    return {
        "overview": {"title": "Synthetic cleaning tender", "reference": "TC-SYN-2026-001", "issuer": "Fictional Sample Municipality", "opening_date": "1 October 2026", "submission_date": "30 October 2026 at 11:00", "contract_period": "12 months", "scope": "Cleaning two fictional locations", "eligibility_summary": "Tax-compliance evidence is mandatory", "what_matters_most": "Deadline, tax evidence, scoring, and staffing"},
        "findings": [
            {"id": "F1", "category": "STATED", "title": "Tax evidence is mandatory", "explanation": "A bidder must submit valid tax-compliance evidence.", "why_it_matters": "Omission makes the bid non-responsive.", "priority": "CRITICAL", "missing_information": "", "source_refs": [{"page": 1, "section": "2. Mandatory eligibility", "excerpt": "Failure to include the tax-compliance evidence makes the bid non-responsive."}]},
            {"id": "F2", "category": "CONCLUSION", "title": "Plan the weekend team", "explanation": "The work plan needs two Saturday cleaners, one Sunday cleaner, and a supervisor.", "why_it_matters": "Clause 5 points to the schedule in clause 8.", "priority": "IMPORTANT", "missing_information": "", "source_refs": [{"page": 1, "section": "5. Staffing reference", "excerpt": "The tenderer must provide personnel according to the weekend coverage in clause 8 and include staffing numbers in the work plan."}, {"page": 2, "section": "8. Weekend coverage schedule", "excerpt": "For the Civic Office, the tenderer must provide two cleaners from 08:00 to 16:00 on Saturdays and one cleaner from 08:00 to 12:00 on Sundays."}]},
            {"id": "F3", "category": "UNCLEAR", "title": "Consumables allocation needs clarification", "explanation": "The municipality may supply some consumables, but the tender does not say which or how much.", "why_it_matters": "The contractor cannot accurately price the uncertain share.", "priority": "IMPORTANT", "missing_information": "List, quantities, and supply dates.", "source_refs": [{"page": 2, "section": "7. Cleaning consumables", "excerpt": "No list of items, quantities, or supply dates is provided."}]},
        ],
        "checklist": [],
        "next_actions": [],
    }


class FakeProvider:
    def __init__(self, result):
        self.result = result
    def analyze(self, _text):
        return self.result


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = extract_pages("synthetic_cleaning_tender.pdf", (ROOT / "fixtures" / "synthetic_cleaning_tender.pdf").read_bytes())
        cls.page_map = {p.number: p.text for p in cls.pages}

    def test_provider_neutral_shape_keeps_three_evidence_categories(self):
        result = validate_analysis(fixture_result())
        self.assertEqual({f["category"] for f in result["findings"]}, {"STATED", "CONCLUSION", "UNCLEAR"})

    def test_ai_returned_page_excerpts_are_checked_against_fixture(self):
        result = analyze_pages(self.pages, FakeProvider(fixture_result()))
        self.assertTrue(all(ref["verified"] for f in result["findings"] for ref in f["source_refs"]))
        conclusion_refs = result["findings"][1]["source_refs"]
        self.assertEqual([ref["page"] for ref in conclusion_refs], [1, 2])

    def test_mismatched_or_nonexistent_source_is_not_verified(self):
        self.assertFalse(validate_source_ref({"page": 1, "excerpt": "This sentence does not occur in the tender."}, self.page_map))
        self.assertFalse(validate_source_ref({"page": 99, "excerpt": "Tax compliance"}, self.page_map))

    def test_invalid_evidence_label_is_rejected(self):
        result = fixture_result()
        result["findings"][0]["category"] = "WINNING_GUARANTEE"
        with self.assertRaisesRegex(ValueError, "invalid evidence category"):
            validate_analysis(result)

    def test_provider_failure_stops_without_partial_analysis(self):
        class OfflineProvider:
            def analyze(self, _text):
                raise AnalysisError("Gemini Free Tier quota is unavailable or exhausted.")
        with self.assertRaisesRegex(AnalysisError, "quota"):
            analyze_pages(self.pages, OfflineProvider())


    def test_gemini_quota_error_is_a_clear_stop(self):
        from types import SimpleNamespace
        from google.genai.errors import APIError
        from tender_clarity.providers.gemini import GeminiProvider
        quota = APIError(429, {"error": {"code": 429, "status": "RESOURCE_EXHAUSTED", "message": "quota exhausted"}})
        def fail(**_kwargs):
            raise quota
        provider = object.__new__(GeminiProvider)
        provider.client = SimpleNamespace(models=SimpleNamespace(generate_content=fail))
        with self.assertRaisesRegex(AnalysisError, "Free Tier quota.*no paid service"):
            provider.analyze("small safe test text")
    def test_gemini_service_unavailable_is_not_misreported_as_quota_or_network_failure(self):
        from types import SimpleNamespace
        from google.genai.errors import APIError
        from tender_clarity.providers.gemini import GeminiProvider
        unavailable = APIError(503, {"error": {"code": 503, "status": "UNAVAILABLE", "message": "temporary test message"}})
        def fail(**_kwargs):
            raise unavailable
        provider = object.__new__(GeminiProvider)
        provider.client = SimpleNamespace(models=SimpleNamespace(generate_content=fail))
        with self.assertRaisesRegex(AnalysisError, r"temporarily unavailable \(HTTP 503, UNAVAILABLE\)"):
            provider.analyze("small synthetic fixture text")

if __name__ == "__main__":
    unittest.main()


