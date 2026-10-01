# Tender Clarity

A small, local-first proof of concept that turns one public, text-based tender PDF into plain-language, source-labelled findings. It uses the Gemini API Free Tier; it does not promise confidentiality, tender success, or paid fallback.

## Run locally (Windows)

1. Install Python 3.12.
2. In PowerShell, from this folder:

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

3. Create a Gemini API key in AI Studio on the Free Tier. Do not connect a billing account or payment method. Create `.streamlit/secrets.toml` containing:

   ```toml
   GEMINI_API_KEY = "your-key-here"
   ```

   Keep this local file private; it is excluded by `.gitignore`. The Free Tier may use submitted text to improve Google services. Use only publicly available, non-sensitive documents.
4. Start the app:

   ```powershell
   python -m streamlit run app.py
   ```

5. Open `http://localhost:8501`.

Upload one selectable-text PDF (maximum 20 MB and 100 pages). Scanned/image-only PDFs are rejected without OCR. Analysis and extracted text are kept in the active app session only. If Gemini quota is unavailable, the app stops; it never switches to a paid model.

## Repeatable test fixture

`fixtures/synthetic_cleaning_tender.pdf` is fictional test material, prominently labelled as synthetic and not a real tender. Regenerate it with:

```powershell
python scripts/create_test_fixture.py
```

It includes a mandatory tax-compliance requirement, deadline, scoring points, incomplete consumables details, cost information, and a staffing interpretation that connects page 1 with page 2.

Run local checks with:

```powershell
python -m unittest discover -s tests -v
```

A live AI check requires an available Gemini Free Tier key/quota. Compare verified source excerpts to the page text extracted from the fixture. No confidential tender should be used as a test fixture.

## Safe Gemini diagnostic

After adding your Free Tier key to `.streamlit/secrets.toml`, you can run:

```powershell
python scripts/diagnose_gemini.py
```

This sends one request using only the fictional test PDF. It never prints the API key or tender text; it reports only the model, API status, evidence-category counts, and page/excerpt verification counts. It uses no paid fallback. If it reports HTTP 503 `UNAVAILABLE`, Google is temporarily unable to serve the model; wait and retry later. HTTP 429 means stop until the free quota resets.
