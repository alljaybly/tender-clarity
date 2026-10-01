"""Tender Clarity: understand a tender and prepare the next steps."""

import streamlit as st

from tender_clarity.analysis import AnalysisError, analyze_pages
from tender_clarity.pdf_reader import PDFInputError, extract_pages
from tender_clarity.providers.gemini import GeminiProvider

st.set_page_config(page_title="Tender Clarity", page_icon="🍃", layout="wide")
st.markdown("""
<style>
:root { --green: #176b52; --ink: #17251f; --mint: #eaf5ef; }
.block-container { max-width: 1080px; padding-top: 2.2rem; }
.tc-hero { padding: 2rem; border-radius: 22px; background: linear-gradient(115deg,#e8f5ec,#eef3ff); }
.tc-hero h1 { color: #12372a; margin-bottom: .3rem; }
.tc-muted { color: #52645b; }
</style>
""", unsafe_allow_html=True)


def render_source_refs(refs):
    for ref in refs:
        if ref.get("verified"):
            section = f" · {ref.get('section')}" if ref.get("section") else ""
            with st.expander(f"View source · page {ref['page']}{section}"):
                st.caption("Extracted from the uploaded tender")
                st.code(ref.get("excerpt", ""), language=None)
        else:
            st.caption(f"Source not verified · page reference {ref.get('page', 'unknown')}. Do not rely on this citation as proof.")


def render_checklist(items, next_actions):
    st.header("Preparation checklist")
    if not items:
        st.info("No preparation actions were returned. Review the findings and source text before deciding what to do next.")
        return

    statuses = st.session_state.checklist_statuses
    completed = 0
    critical_outstanding = 0
    for index, item in enumerate(items, start=1):
        item_id = item.get("id") or f"item-{index}"
        initial_status = item.get("status", "TO_DO")
        current_status = statuses.get(item_id, initial_status)
        importance = item.get("importance", "IMPORTANT")
        is_complete = current_status == "COMPLETED"
        label = "I have received clarification and updated my plan" if initial_status == "NEEDS_CLARIFICATION" else "Mark this task complete"
        widget_key = f"checklist_done_{st.session_state.analysis_version}_{item_id}"
        with st.container(border=True):
            checked = st.checkbox(label, value=is_complete, key=widget_key)
            if checked:
                current_status = "COMPLETED"
                statuses[item_id] = current_status
                completed += 1
                st.markdown(f"### ✓ Completed: {item.get('action', 'Preparation task')}")
                st.caption("Status: Completed")
            else:
                current_status = "NEEDS_CLARIFICATION" if initial_status == "NEEDS_CLARIFICATION" else "TO_DO"
                statuses[item_id] = current_status
                st.markdown(f"### {item.get('action', 'Preparation task')}")
                if current_status == "NEEDS_CLARIFICATION":
                    st.warning("Status: Needs clarification. Keep this open until you receive an answer and update your plan.")
                else:
                    st.caption("Status: To do")
                if importance == "CRITICAL":
                    critical_outstanding += 1
            if importance == "CRITICAL":
                st.error("Critical requirement", icon="⚠️")
            elif item.get("optional") or importance == "OPTIONAL":
                st.caption("Optional or recommended")
            else:
                st.caption("Important action")
            if item.get("why_it_matters"):
                st.write("**Why it matters:** " + item["why_it_matters"])
            if item.get("required"):
                st.write("**What you need:** " + item["required"])
            if item.get("completion_evidence"):
                st.write("**How to know it is complete:** " + item["completion_evidence"])
            if item.get("finding_id"):
                st.caption("Related finding: " + item["finding_id"])
            render_source_refs(item.get("source_refs", []))

    progress_col, risk_col = st.columns(2)
    progress_col.metric("Checklist progress", f"{completed} of {len(items)} completed")
    risk_col.metric("Critical items outstanding", critical_outstanding)
    if critical_outstanding:
        st.warning(f"{critical_outstanding} critical item(s) remain open. Completing this checklist does not guarantee a tender outcome.")

    if next_actions:
        st.subheader("Next actions")
        for number, action in enumerate(next_actions, start=1):
            text = action.get("action", "") if isinstance(action, dict) else str(action)
            if text:
                st.write(f"{number}. {text}")


st.markdown('<div class="tc-hero"><h1>Tender Clarity</h1><p><b>Every contractor deserves a clear shot.</b></p><p class="tc-muted">You do not need to be a big company to understand a tender. Let us make it clear.</p></div>', unsafe_allow_html=True)
st.write("")

if "analysis" not in st.session_state:
    st.session_state.analysis = None
    st.session_state.pages = None
    st.session_state.filename = None
    st.session_state.checklist_statuses = {}
    st.session_state.analysis_version = 0

st.session_state.setdefault("checklist_statuses", {})

st.session_state.setdefault("analysis_version", 0)

st.subheader("Start with one tender")
st.write("Upload a text-based PDF. Tender Clarity will explain the opportunity, identify requirements and unclear points, and show where its findings came from.")
st.warning("Privacy notice: The tender's extracted text is sent to Google's Gemini Free Tier for analysis. Google may use free-tier content to improve its services, and human reviewers may process it. Upload only publicly available, non-sensitive tender documents. Tender Clarity does not claim that uploaded information is confidential.", icon="⚠️")

uploaded = st.file_uploader("Choose one tender PDF (maximum 20 MB and 100 pages; selectable text only)", type=["pdf"], accept_multiple_files=False, help="Scanned/image-only PDFs are not supported. This prototype does not use OCR.")

if uploaded is not None and st.button("Analyse tender", type="primary", width="stretch"):
    st.session_state.analysis = None
    st.session_state.pages = None
    st.session_state.checklist_statuses = {}
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
        st.session_state.analysis_version += 1
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
        render_source_refs(finding.get("source_refs", []))
        st.divider()

    render_checklist(analysis.get("checklist", []), analysis.get("next_actions", []))
    st.caption("The analysis helps with preparation; it does not predict or guarantee a tender outcome.")
    st.caption("Your analysis is available only in this browser session. Refreshing the page clears it.")
