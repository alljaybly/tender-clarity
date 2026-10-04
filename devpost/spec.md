---
doc: spec
status: approved
---

# Tender Clarity — Technical Spec

## How This Works, In Plain Language

Tender Clarity is one small Python web app. Streamlit draws the pages and handles the clicks, so there is no separate front-end app, database, or local AI model. The app reads selectable text from one PDF on the machine running it, adds page labels, asks Gemini Free Tier to organize that text, checks the returned source references, and displays the results. The same app runs locally first and can later be placed on Streamlit Community Cloud without a rewrite.

The laptop only runs the app and extracts text; the AI work runs on Google's free Gemini API. The app remembers one analysis in the active browser connection. If the page is refreshed or that connection ends, the analysis is lost. Cost arithmetic and the downloadable report are handled locally by the app. The AI provider is kept behind one small adapter, so a later provider change is limited to that adapter and configuration.

This keeps the local resource needs small for a 6 GB laptop. The tradeoff is that uploaded tender text is sent to Gemini. On its free tier, Google may use submitted content and responses to improve its products, and human reviewers may process it. The app must warn users before upload and must not claim confidentiality. Use public, non-sensitive tender documents only.

## The Core Journey Through the System

1. The browser opens the Streamlit app and shows the privacy warning, welcome message, and one-PDF upload control.
2. When the contractor selects a file, Streamlit passes its bytes to the Python app in memory. The PDF reader checks that it is a PDF, is at most 20 MB, has at most 100 pages, and contains extractable text. It does not save the original PDF to disk.
3. The PDF reader extracts text page by page, preserving 1-based page numbers and any section headings present in the extracted text. Image-only/scanned documents are rejected; no OCR is attempted.
4. The analysis service sends page-labelled text to the Gemini adapter. The adapter calls the configured Gemini Free Tier model and requests the provider-neutral Tender Clarity result format. No web search, external sources, or original PDF file upload is used.
5. The app validates the response shape, page numbers, and quoted source excerpts against the local extracted page text. Valid sources open in an in-app source panel. Unmatched or out-of-range references are visibly marked unverified and cannot be presented as verified evidence. This catches citation mismatches; it cannot prove that an AI interpretation is correct.
6. Streamlit displays the overview, evidence-labelled findings, checklist/progress, prioritized next actions, and the cost worksheet. Checklist edits and cost values stay in the active session. Cost totals, remaining amount, and margin are calculated in Python, not by AI.
7. When asked, ReportLab creates the complete report as PDF bytes. Streamlit sends the file to the browser's download control; the app does not create a permanent report file.
8. If Gemini reports a quota limit, the app displays a clear free-quota message and stops. It never retries with a paid service or model. A page refresh or ended browser connection loses the current analysis.

```text
Browser
  │ upload PDF and interact
  ▼
Single Streamlit/Python app ──► pypdf: validate and extract per-page text
  │                                      │
  │                          page-labelled text only
  │                                      ▼
  │                             Gemini provider adapter
  │                                      │
  │                             provider-neutral result
  ▼                                      ▼
Session data ◄──── source/shape validation ◄──── AI response
  │
  ├──► overview, findings, checklist, costs
  └──► ReportLab creates downloadable PDF
```

PRD ref: `prd.md > The Core Journey`, `prd.md > Tender upload and analysis`, `prd.md > Tender overview and critical findings`, `prd.md > Preparation checklist and next actions`, `prd.md > Cost worksheet`, `prd.md > Download report`, `prd.md > States and Boundaries`.

## Stack

- **Python 3.12** for the app and its small processing steps. It runs on Windows locally and is supported by Streamlit Community Cloud; Cloud currently defaults to Python 3.12. [Python downloads](https://www.python.org/downloads/), [Community Cloud deployment](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app).
- **Streamlit** for the browser interface, upload widget, session memory, and download control. It avoids a separate JavaScript build and server. [Streamlit docs](https://docs.streamlit.io/).
- **pypdf** for local PDF page count and text extraction. Text extraction is not OCR and can be inaccurate on complex layouts; scanned/image-only PDFs are unsupported. [pypdf text extraction](https://pypdf.readthedocs.io/en/stable/user/extract-text.html).
- **Google Gen AI Python SDK (`google-genai`)** for one Gemini API implementation behind the provider adapter. Use the stable model ID `gemini-3.8-flash` with structured JSON output. The current model supports a 1,048,576-token input limit and structured output; South Africa is an available region; free-tier request limits vary by model and project, are not guaranteed, and must be checked in AI Studio before use. [Gemini model details](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash), [structured output](https://ai.google.dev/gemini-api/docs/structured-output), [free-tier pricing](https://ai.google.dev/gemini-api/docs/pricing), [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits), [available regions](https://ai.google.dev/gemini-api/docs/available-regions).
- **ReportLab** to generate the requested downloadable PDF locally from current session data. [ReportLab User Guide](https://www.reportlab.com/docs/reportlab-userguide.pdf).
- **Python standard library** for JSON parsing, arithmetic, and basic input checks. A Pydantic model or a second validation framework is not necessary for this small prototype; use a documented JSON schema and explicit validation functions.

All application libraries are available without a software license fee. Pin the exact compatible package versions that work locally in `requirements.txt` before the optional deployment; use the same pins in both places. Do not add a paid SDK, paid model, OCR service, database, container, or separate frontend.

## Where It Runs and How Someone Tries It

### Local first

Requirements: Windows, Python 3.12, internet access for Gemini API requests, and a Gemini API key from an AI Studio project that remains on the Free Tier with no billing account attached.

1. Open PowerShell in the project folder.
2. Create and activate a local environment:

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the pinned free libraries:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Create `.streamlit/secrets.toml` locally with the Gemini key. This file must be ignored by Git and never committed. Do not paste the key into chat or source code. Streamlit reads local secrets from this file. [Streamlit secrets](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).
5. Start the app:

   ```powershell
   python -m streamlit run app.py
   ```

6. Open `http://localhost:8501` in a browser. Use a publicly available, non-sensitive tender PDF and complete the demo journey.

The API key must belong to a Free Tier Gemini project. Do not link a billing account, payment method, paid project, or automatic upgrade. If a free-tier key cannot be created or its quota is unavailable, analysis stops; the application has no paid fallback. Gemini Free Tier usage is $0, but the terms allow Google to use submitted prompts/documents and responses to improve products, and human reviewers may process them. [Gemini billing](https://ai.google.dev/gemini-api/docs/billing), [Gemini data terms](https://ai.google.dev/gemini-api/terms).

### Optional public test after local completion

Use Streamlit Community Cloud only after the local core journey has been verified. It is a free hosting option suitable for a small public experiment, not a reliability promise for a later commercial product. Deployment uses the app's GitHub repository; the repository and app must be public for anyone with the link to try it. The host can sleep after 12 hours without traffic, and its resource limits can change. If the free host is unavailable or unreliable, keep the app local and use the required demo video instead. [Deploy](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app), [sharing](https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app), [resource limits and hibernation](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app).

When deploying, add the Gemini key in Community Cloud's Secrets settings; never place it in GitHub. Ignore `.streamlit/secrets.toml`. Keep the app's pre-upload warning visible on the public version. Anyone with the public link can attempt to use the app and consume the free quota, so quota exhaustion must stop new analysis with a message. No billing is attached, so it cannot switch into paid usage.

Before optional deployment, manually verify the complete journey locally with one public text-based tender: upload and analysis, evidence labels and source excerpts, checklist completion/progress, cost recalculation with known inputs, and the downloaded PDF contents. Also verify that an image-only/scanned PDF is rejected and that a quota error stops without a paid fallback. The submission still needs a short demo video and public GitHub repository. Local operation is enough for the demo recording; deployment is optional and is a separate second stage.

## Look and Feel

Implement the PRD's welcoming, reassuring, professional style without a separate design system. Use a light, spacious single-column welcome/upload view and a clearly sectioned results workspace. Use plain-language headings, restrained color, and visible text labels plus icons for STATED, CONCLUSION, and UNCLEAR; color alone must not convey evidence status. The upload warning appears before the upload control and states that files/text are sent to Google's Gemini Free Tier, free-tier content may be used to improve its services, and users must upload only public/non-sensitive tenders. The interface must not say or imply that a file is private or confidential.

PRD ref: `prd.md > Screens and Layout`, `prd.md > Look and Feel`.

## Components

### Streamlit app and session workspace

Owns the welcome/upload view, visible privacy notice, analysis progress/error display, ordered results workspace, checklist interaction, cost input fields, progress count, and download button. Holds one analysis and its editable values in Streamlit session state for the active browser connection. Does not write source PDFs, results, or cost values to a database or permanent app storage.

Implements `prd.md > Screens and Layout`, `prd.md > Preparation checklist and next actions`, `prd.md > Cost worksheet`, `prd.md > States and Boundaries`.

### PDF validator and text extractor

Accepts one PDF only. Before extraction, reject files over 20 MB, over 100 pages, non-PDF files, encrypted/corrupt PDFs, or documents with no usable selectable text. Do not run OCR. Keep page text in memory with 1-based page number and extracted headings. If a document is scanned/image-only, show: “This PDF appears to contain scanned images rather than selectable text. Tender Clarity V1 cannot read it and does not use OCR. Please choose a text-based PDF.” If a document has some textless pages, identify those pages as not readable and prevent unsupported content from being described as stated.

Implements `prd.md > Tender upload and analysis`, `prd.md > States and Boundaries`.

### Provider-neutral analysis contract

Define one small shared result format in `models.py`, independent from any Gemini SDK types. The UI and report use only this format. At minimum it contains:

- `overview`: title/reference, issuer, opening and submission dates, contract period, scope, eligibility summary, and “what matters most”; unknown values are empty/UNCLEAR, not guessed.
- `findings[]`: stable ID, category (`STATED`, `CONCLUSION`, or `UNCLEAR`), title, plain-language explanation, why it matters, priority, missing information if unclear, and source references.
- `source_refs[]`: 1-based page, section text if found, and a short verbatim excerpt from that extracted page.
- `checklist[]`: stable ID, linked finding ID if applicable, action, why it matters, required document/information/calculation, completion evidence, importance/optional flags, and status (`TO_DO`, `COMPLETED`, or `NEEDS_CLARIFICATION`).
- `next_actions[]`: ordered short action text referencing related checklist/finding IDs.

Checklist completion status and contractor-entered cost inputs are app-owned session data, not generated by the model. Importance (critical/at risk/optional) is separate from completion status.

Implements `prd.md > Tender overview and critical findings`, `prd.md > Preparation checklist and next actions`.

### Gemini Free Tier adapter and analysis service

`providers/gemini_provider.py` is the only module that imports `google-genai`. Its adapter accepts the provider-neutral page-text input and returns the shared result format. `analysis.py` assembles the prompt and instructs the model that the tender is untrusted source material, not instructions; requires it to distinguish explicit statements, interpretations, and unknowns; and asks it to avoid unsupported claims. The API request uses `client.models.generate_content` with model `gemini-3.8-flash`, page-labelled text as `contents`, and a JSON schema through `response_mime_type="application/json"` plus `response_schema`. Read `GEMINI_API_KEY` from Streamlit secrets.

The app sends extracted text only. It does not use search grounding, file search, web access, or any other tool. The response is a proposed analysis, not verified truth. Free-tier quota/rate-limit errors (including HTTP 429), missing key, timeouts, refusals, or malformed output produce a clear message and no partial/fabricated analysis. Do not retry through any paid model/provider. When the free quota is exhausted, stop and tell the user to try again after quota reset or continue later; do not ask for billing setup.

The Gemini Free Tier currently lists zero input/output token prices for eligible models and free-tier rate limits are account/model-specific. Free-tier prompts and outputs may be used to improve Google products and may be reviewed by humans. Do not claim confidentiality. Do not attach Cloud billing or a payment method to the API project. [Python SDK call](https://ai.google.dev/api/generate-content), [structured output schema](https://ai.google.dev/gemini-api/docs/structured-output), [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits), [free pricing](https://ai.google.dev/gemini-api/docs/pricing), [unpaid-service data terms](https://ai.google.dev/gemini-api/terms).

Implements `prd.md > Tender upload and analysis`, `prd.md > Tender overview and critical findings`.

### Source-reference validator

For each model source reference, check that the page number exists and the quoted excerpt matches text extracted from that page after normalizing whitespace. Show a “View source” action only for verified references. If a reference fails validation, label it “Source not verified”; do not display it as proof. A verified excerpt shows its page and the original extracted text. The check validates the citation string/location, not the correctness of a conclusion.

Implements `prd.md > Tender overview and critical findings`.

### Cost calculator

A deterministic Python function sums the contractor's ZAR/R entries for labour, materials, transport, equipment, other expenses, and overhead. It calculates:

- Total estimated cost = sum of cost entries.
- Amount remaining = benchmark/expected contract value − total estimated cost.
- Estimated margin percentage = amount remaining ÷ benchmark/expected contract value × 100, only when the value is positive.

Recalculate on each edit. Show the under-cost warning when amount remaining is negative. Label figures as contractor estimates, not bid recommendations or accounting/financial advice. No AI call is made for these calculations.

Implements `prd.md > Cost worksheet`.

### PDF report generator

`report.py` creates a PDF in memory using ReportLab when the user chooses Download Report. Include the overview, each finding and evidence label, verified page/excerpt sources, checklist items and current status/progress, next actions, cost inputs and calculated results, and the estimate disclaimer. Do not save a permanent report file on the app host.

Implements `prd.md > Download report`.

## Data Model

- **Uploaded PDF:** Starts in the browser upload control; its bytes reach the local Streamlit process or, for the optional public app, the Streamlit Community Cloud process. Validate and parse in memory; never save the source PDF to disk or send the PDF binary to Gemini.
- **Extracted pages:** A temporary list of page number and extracted text held in memory for the request; page-labelled text is sent to Gemini. Discard after analysis/session ends.
- **AI result:** Gemini response text is parsed and validated into the shared analysis format. Store in Streamlit session state; never persist it in a database or a global/shared cache.
- **Checklist statuses and cost inputs:** Store in the same session state and update on user changes. Calculations derive from current numeric inputs.
- **Generated report:** Build PDF bytes from current session state and offer them to the browser download. Do not keep a server-side copy.
- **API key:** Local `.streamlit/secrets.toml`, ignored by Git; deployed version in Community Cloud Secrets. Never store it in source, frontend/browser data, or logs.
- **Session end or browser refresh:** Streamlit's Session State is tied to the active WebSocket; reload/disconnect clears the analysis, checklist progress, and costs. There is no recovery after that. [Session State behavior](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state).

## File Structure

```text
Tender-Clarity/
├── app.py                         # Streamlit screens, session state, interactions
├── tender_clarity/
│   ├── models.py                  # Provider-neutral analysis and checklist data
│   ├── pdf_reader.py              # Size/page checks and per-page text extraction
│   ├── analysis.py                # Prompt, provider call, result validation
│   ├── providers/
│   │   ├── base.py                # Small provider interface
│   │   └── gemini.py              # Gemini Free Tier SDK adapter only
│   ├── sources.py                 # Page/excerpt citation checks
│   ├── costs.py                   # Deterministic ZAR calculations
│   └── report.py                  # In-memory PDF report generation
├── .streamlit/
│   └── config.toml                # Upload cap and minimal app configuration
├── .gitignore                     # Exclude secrets and learner profile
├── requirements.txt               # Pinned free Python dependencies
├── README.md                      # Plain setup, privacy, local run, optional deploy
└── devpost/                       # Existing planning documents; learner profile ignored
```

The provider interface and Gemini implementation are deliberately small. No shared provider framework, plug-in system, database, migrations, or front-end build chain is planned for V1.

## External Services and Dependencies

### Gemini Developer API — Free Tier only

- **Purpose:** Convert page-labelled tender text into the provider-neutral analysis response.
- **Service/model:** Gemini API `gemini-3.8-flash`, through Google's official `google-genai` Python SDK.
- **Call:** One Python SDK `client.models.generate_content` call per analysis. It uses the `gemini-3.8-flash` model, page-labelled text as `contents`, and a JSON schema in the generation configuration (`response_mime_type="application/json"`, `response_schema=...`). The SDK calls the Gemini `generateContent` endpoint: `POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent`. The app expects JSON text in `response.text`, then parses and validates it.
- **Authentication:** `GEMINI_API_KEY` from a Free Tier AI Studio project with no billing account attached. A Google account/API key is required, but do not add billing or a payment method. The key remains server-side. New projects start on Free Tier; setting up billing is required to upgrade. [Billing and tier setup](https://ai.google.dev/gemini-api/docs/billing).
- **Cost:** $0 under the model's listed Free Tier input/output pricing. Do not enable billing, attach a payment method, use a paid project/model, or add a paid fallback.
- **Limits:** Per-project/model rate limits vary, are visible in AI Studio, and may change or be unavailable. If quota is not available, the app stops gracefully. The 1M model context limit is not a promise that the free tier accepts a particular request size.
- **Privacy:** On unpaid/free services, Google may use prompts, documents, and generated responses to develop and improve products; human reviewers may read/process some data. Display the warning before upload; accept only public, non-sensitive tender documents. The product must make no confidentiality claim.

## Important Failure Modes

- **Scanned/image-only PDF or unusable extracted text** → Reject before API call, explain that V1 reads selectable text only and does not use OCR, and ask for a text-based PDF.
- **File exceeds 20 MB or 100 pages, or is invalid/encrypted** → Reject before API call with the specific limit/reason; do not partially analyze it.
- **Free Gemini quota exhausted, API unavailable, or malformed/refused result** → Stop, preserve no fabricated/partial analysis, and show a plain message. No paid retry/fallback.
- **AI source reference does not match page text** → Mark it “Source not verified,” withhold the verified-source action, and do not treat it as proof.
- **Browser refresh or session disconnect** → Explain during the demo that this V1 has session-only data and does not restore the analysis.

## What Was Simplified and Why

- **One Streamlit/Python process** instead of a separate front end, back end, and database — fewer tools to install and debug on a 6 GB laptop; the same app can be hosted later.
- **Text extraction only** instead of OCR or PDF vision — avoids large local workloads, extra libraries/services, and unreliable text recognition; scanned PDFs are explicitly unsupported.
- **One Gemini Free Tier adapter** instead of an AI framework or multiple providers — no paid bill risk; provider-neutral data keeps a later swap localized.
- **Session memory** instead of permanent storage/accounts — matches the one-tender demo and avoids database setup; refresh loses progress.
- **Source excerpts rather than a full PDF viewer** — keeps evidence traceable without a separate document-rendering interface.
- **Free Streamlit Community Cloud as optional** instead of required deployment — the core demo works locally first; public hosting may sleep or be resource-limited.

## Decisions and Open Issues

- **Learner decision:** Zero-cost tools and services only. No paid API, host, database, subscriptions, or software. No payment method or billing account for the Gemini project; free quota exhaustion stops analysis.
- **Learner decision:** One text-based PDF per analysis, up to 20 MB and 100 pages; no OCR; scanned/image-only documents rejected with explanation.
- **Learner decision:** Gemini Free Tier is acceptable for publicly available, non-sensitive tender documents under the stated privacy terms and warning.
- **Learner decision:** Build and complete the core journey locally before any optional public deployment. A public test needs no accounts; use Streamlit Community Cloud only if it remains free and practical.
- **Learner decision:** Keep AI behind a small provider adapter and use a provider-neutral findings format for future changes.
- **Learner decision:** Keep current analysis, checklist, and costs in the active browser session only. No database or permanent storage.
- **Derived implementation decision:** Extract page text locally, send page-labelled text to Gemini rather than the original PDF, and validate returned page/excerpt references. This supports traceability and reduces what is sent, but does not guarantee semantic correctness.
- **Useful uncertainty and how to check it:** Free Gemini rate limits are not a guaranteed fixed allowance. Before the first live analysis, check the Gemini AI Studio project is Free Tier with no billing attached and inspect the active model quota. On quota exhaustion, show the stop message; do not enable billing or change providers automatically.
- **Implementation-time check:** Pin dependency versions that install and run locally, then deploy those same pins. Recheck Gemini model availability, Free Tier access, data terms, and Streamlit Community Cloud free-host status before optional public deployment.



