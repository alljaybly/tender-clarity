---
doc: checklist
status: approved
---

# Build Checklist

Build mode: learn � explain each verified slice in plain language, then guide the learner through its check.

## Slices

- [x] **1. Upload a sample tender and inspect source-grounded findings**
  Becomes usable: A locally running app accepts a clearly labelled synthetic PDF and shows AI findings labelled STATED, CONCLUSION, or UNCLEAR, with source excerpts that can be checked against extracted pages.
  Why now: This proves the distinctive evidence-backed analysis kernel early and exposes PDF, model, and citation risks before building the rest of the workspace.
  PRD ref: `prd.md > The Core Journey`, `prd.md > Tender upload and analysis`, `prd.md > Tender overview and critical findings`, `prd.md > States and Boundaries`
  Spec ref: `spec.md > The Core Journey Through the System`, `spec.md > Stack`, `spec.md > Where It Runs and How Someone Tries It`, `spec.md > Components`, `spec.md > Data Model`, `spec.md > Important Failure Modes`
  Build: Bootstrap Streamlit; create a fictional, non-sensitive PDF fixture with a stated mandatory requirement, deadline, scoring criterion, ambiguous requirement, cost detail, and cross-page supporting information; add PDF validation/text extraction, provider-neutral result format, Gemini adapter, source matching, and a basic findings/source display. Add focused offline checks for extraction, evidence categories, citation match/mismatch, and quota failure. Run one live analysis of the fixture if free quota is available; never use a paid fallback.
  Verify (mechanical): Run `python -m unittest discover -s tests -v`; launch the app and analyze the fixture when free quota is available. Confirm the six examples exist in extracted page text and every returned reference shown as verified matches its extracted page. Confirm quota failure stops clearly.
  Learner check: Upload the synthetic fixture; inspect a STATED, CONCLUSION, and UNCLEAR finding; compare each �View source� excerpt with the fixture. Tell me what is clear or confusing before we continue.
  Commit: `Build source-grounded tender analysis`

- [x] **2. Turn findings into an interactive preparation checklist**
  Becomes usable: Ordered actions link to evidence; completion, progress, and critical outstanding counts update.
  Why now: This turns traceable findings into practical work and gives early feedback a chance to shape the workspace.
  PRD ref: `prd.md > Preparation checklist and next actions`, `prd.md > States and Boundaries`
  Spec ref: `spec.md > Components`, `spec.md > Data Model`, `spec.md > Look and Feel`
  Build: Add linked checklist actions, reasons, required information, completion evidence, source, importance and statuses; keep unclear items as clarification actions and progress in session state.
  Verify (mechanical): Run `python -m unittest discover -s tests -v`; complete and reopen an item, confirming progress, critical counts, and source links update.
  Learner check: Complete one item and inspect one clarification item. Tell me if each explains what to do, why it matters, what is needed, and how completion is known.
  Commit: `Add interactive tender preparation checklist`

- [ ] **3. Enter costs and see the viability arithmetic update**
  Becomes usable: ZAR costs and expected/benchmark value recalculate total cost, amount remaining, and estimated margin immediately.
  Why now: Adds the pursuit decision through transparent arithmetic after requirements are actionable.
  PRD ref: `prd.md > Cost worksheet`, `prd.md > States and Boundaries`
  Spec ref: `spec.md > Components`, `spec.md > Data Model`
  Build: Add labour, materials, transport, equipment, other expenses, overhead, and expected/benchmark value fields; calculate the approved formula and under-cost warning; show the estimate/no-bid-advice disclaimer.
  Verify (mechanical): Run `python -m unittest discover -s tests -v`; verify known inputs, blank/zero benchmark, and costs exceeding price; confirm recalculation.
  Learner check: Enter several costs and a benchmark value; tell me whether the results and estimate disclaimer are understandable.
  Commit: `Add contractor cost viability worksheet`

- [ ] **4. Download the complete Tender Clarity report**
  Becomes usable: A PDF report reflects current findings, sources, checklist, next actions, and cost values.
  Why now: The complete report depends on analysis and contractor edits being available first.
  PRD ref: `prd.md > Download report`, `prd.md > The Core Journey`
  Spec ref: `spec.md > Components`, `spec.md > Data Model`, `spec.md > Important Failure Modes`
  Build: Generate a report in memory with evidence labels, verified excerpts, checklist status, calculations, and disclaimers; finish clear failure messages without adding out-of-scope features.
  Verify (mechanical): Run `python -m unittest discover -s tests -v`; complete the sample workflow, edit checklist/costs, download and inspect the report, reject a scanned PDF, and simulate quota exhaustion with no paid fallback.
  Learner check: Complete the workflow, open the report, and tell me whether it makes clear what to prepare and what remains uncertain.
  Commit: `Generate complete tender preparation report`

## Hands-on Checkpoints

- [ ] Early usable behavior explored � after slice 1, inspect analysis and provide feedback before checklist/workspace refinements.
- [ ] Final kick-the-tires exploration and feedback completed � after slice 4.

## Final Review

- [ ] Final review complete � feedback resolved and learner confirms ready to ship

## Code Tour and App Map

- [ ] Learning activity complete � guided route, focused alternative, prior practice connected, or brief recap
- [ ] Optional edit and transfer reflection addressed � offered/declined/already covered/not applicable as appropriate
- [ ] `devpost/app-map.html` generated from finished code, checked, and shown, including a project-grounded practice to reuse

Activity and evidence: [what actually happened; real document/test/code references; unfinished work if interrupted]
Route and stops: [actual paths and symbols; guided stops completed, or reference-only route]
Edit outcome: [tried/kept/reverted/declined/not applicable; verification if changed]
Reflection: [offered/answered/declined/already covered � personal answer belongs only in the ignored profile]
Activity mode: [live app and editor, explicit static fallback, focused alternative, prior practice, or recap]

## Revisions
- Added safe HTTP-specific Gemini error messages and a synthetic-fixture diagnostic after the live API returned HTTP 503 UNAVAILABLE; the provider/model/request match current documented interfaces, and the service response indicates temporary model demand.

- Continued building with the controlled synthetic fixture after live Gemini returned HTTP 503 UNAVAILABLE; live service verification remains pending.

- Checklist slice verified with controlled results and citations matched against extracted synthetic PDF pages; live Gemini remains pending after the confirmed 503.
