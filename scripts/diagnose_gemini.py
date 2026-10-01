"""
Live integration diagnostic for the fictional fixture only.

This makes one normal Gemini Free Tier request. It reads the local Streamlit key
but never prints it or tender text. Only status, category counts, and citation
verification counts are displayed.
"""
from collections import Counter
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tender_clarity.analysis import analyze_pages
from tender_clarity.pdf_reader import extract_pages
from tender_clarity.providers.gemini import GeminiProvider, MODEL

settings = tomllib.loads((ROOT / ".streamlit" / "secrets.toml").read_text(encoding="utf-8"))
api_key = str(settings.get("GEMINI_API_KEY", "")).strip()
print(f"model={MODEL}")
print(f"api_key_configured={bool(api_key)}")
if not api_key:
    raise SystemExit("No key loaded from local Streamlit secrets; no request was sent.")

fixture = ROOT / "fixtures" / "synthetic_cleaning_tender.pdf"
pages = extract_pages(fixture.name, fixture.read_bytes())
try:
    result = analyze_pages(pages, GeminiProvider(api_key))
except Exception as exc:
    root_error = exc.__cause__ or exc
    # Do not print exception strings or HTTP response bodies; only safe metadata.
    code = getattr(root_error, "code", None) or getattr(root_error, "status_code", None)
    api_status = getattr(root_error, "status", None)
    print(f"error_type={type(root_error).__name__}")
    print(f"http_code={code}")
    print(f"api_status={api_status}")
    raise SystemExit(str(exc))

categories = Counter(item.get("category", "INVALID") for item in result["findings"])
refs = [ref for item in result["findings"] for ref in item.get("source_refs", [])]
verified = sum(bool(ref.get("verified")) for ref in refs)
print("analysis_ok=True")
print(f"finding_categories={dict(categories)}")
print(f"source_refs_verified={verified}/{len(refs)}")
print("all_three_categories_present=" + str(set(categories) == {"STATED", "CONCLUSION", "UNCLEAR"}))
