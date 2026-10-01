"""Tender Clarity: understand a tender and prepare the next steps."""
import streamlit as st
from tender_clarity.analysis import AnalysisError, analyze_pages
from tender_clarity.pdf_reader import PDFInputError, extract_pages
from tender_clarity.providers.gemini import GeminiProvider

st.set_page_config(page_title="Tender Clarity", page_icon="🍃", layout="wide")
st.markdown("""
<style>
.block-container { max-width: 1080px; padding-top: 2.2rem; }
.tc-hero { padding: 2rem; border-radius: 22px; background: linear-gradient(115deg,#e8f5ec,#eef3ff); }
.tc-hero h1 { color: #12372a; margin-bottom: .3rem; }
.tc-muted { color: #52645b; }
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="tc-hero"><h1>Tender Clarity</h1><p><b>Every contractor deserves a clear shot.</b></p><p class="tc-muted">You do not need to be a big company to understand a tender. Let us make it clear.</p></div>', unsafe_allow_html=True)
st.write("")

if "analysis" not in st.session_state:
    st.session_state.analysis = None
    st.session_state.pages = None
    st.session_state.filename = None

st.subheader("Start with one tender")
st.write("Upload a text-based PDF. Tender Clarity will explain the opportunity, identify requirements and unclear points, and show where its findings came from.")
st.warning("Privacy notice: The tender's extracted text is sent to Google's Gemini Free Tier for analysis. Google may use free-tier content to improve its services, and human reviewers may process it. Upload only publicly available, non-sensitive tender documents. Tender Clarity does not claim that uploaded information is confidential.", icon="⚠️")
uploaded = st.file_uploader("Choose one tender PDF (maximum 20 MB and 100 pages; selectable text only)", type=["pdf"], accept_multiple_files=False, help="Scanned/image-only PDFs are not supported. This prototype does not use OCR.")

if uploaded is not None and st.button("Analyse tender", type="primary", use_container_width=True):
    st.session_state.analysis = None
    st.session_state.pages = None
    try:
        pages = extract_pages(uploaded.name, uploaded.getvalue())
        unreadable = [page.number for page in pages if not page.text]
        if unreadable:
            st.info("Some pages have no selectable text and cannot be analysed: " + ", ".join(map(str, unreadable)) + ". Findings must not treat their contents as stated.")
        try:
            api_key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            api_key = ""
        provider = GeminiProvider(api_key)
        with st.spinner("Reading the tender and checking source references…"):
            result = analyze_pages(pages, provider)
        st.session_state.analysis = result
        st.session_state.pages = {page.number: page.text for page in pages}
        st.session_state.filename = uploaded.name
    except PDFInputError as exc:
        st.error(str(exc))
    except AnalysisError as exc:
        st.error(str(exc))
    except Exception:
        st.error("Tender Clarity could not complete this analysis. Please try again later. No paid fallback was used.")

analysis = st.session_state.analysis
if analysis:
    st.success("Analysis ready. Check the source before relying on any important finding.")
    overview = analysis["overview"]
    st.header(overview.get("title") or st.session_state.filename or "Tender overview")
    meta = st.columns(3)
    meta[0].caption("Reference")
    meta[0].write(overview.get("reference") or "Not stated")
    meta[1].caption("Issuing organisation")
    meta[1].write(overview.get("issuer") or "Not stated")
    meta[2].caption("Submission deadline")
    meta[2].write(overview.get("submission_date") or "Not stated")
    st.write(overview.get("scope") or "Scope not clear from the available text.")
    if overview.get("what_matters_most"):
        st.info(overview["what_matters_most"], icon="🧭")
    st.header("Important findings")
    st.caption("STATED means the tender says it. CONCLUSION means Tender Clarity worked it out from the tender. UNCLEAR means the document does not give enough information.")
    icons = {"STATED": "📄", "CONCLUSION": "🧩", "UNCLEAR": "❔"}
    for finding in analysis["findings"]:
        category = finding["category"]
        st.markdown(f"### {icons[category]} {category} · {finding.get('title', 'Finding')}")
        st.write(finding.get("explanation", ""))
        if finding.get("why_it_matters"):
            st.caption("Why it matters: " + finding["why_it_matters"])
        if category == "UNCLEAR" and finding.get("missing_information"):
            st.info("Needs clarification: " + finding["missing_information"])
        for ref in finding.get("source_refs", []):
            if ref.get("verified"):
                with st.expander(f"View source · page {ref['page']}" + (f" · {ref.get('section')}" if ref.get("section") else "")):
                    st.caption("Extracted from the uploaded tender")
                    st.code(ref.get("excerpt", ""), language=None)
            else:
                st.caption(f"Source not verified · page reference {ref.get('page', 'unknown')}. Do not rely on this citation as proof.")
        st.divider()
    st.caption("The analysis helps with preparation; it does not predict or guarantee a tender outcome.")
    st.caption("Your analysis is available only in this browser session. Refreshing the page clears it.")
