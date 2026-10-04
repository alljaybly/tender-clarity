---
doc: prd
status: approved
---

# Tender Clarity — Product Requirements

A welcoming web tool that helps a small contractor turn one tender document into a plain-language, source-traceable preparation plan, checklist, and basic cost view.
Source: `scope.md > The Unique Kernel`, `scope.md > Who It's For`, `scope.md > The Core Loop`.

## The Core Journey

1. **Arrive.** The contractor sees a reassuring introduction, a plain explanation of what Tender Clarity does, and a prominent way to upload one tender. The message is that a small contractor can understand a tender and prepare properly; the product does not promise a win.
2. **Upload and analyze.** The contractor selects one tender document and starts analysis. The product prepares a plain-language overview, findings, and checklist from that document.
3. **Understand the opportunity.** In the Tender Clarity workspace, the contractor reviews the tender overview and the most important requirements, dates, evaluation criteria, documents, scope details, possible disqualification issues, and unclear information.
4. **Verify findings.** The contractor expands important findings, sees whether each is STATED, CONCLUSION, or UNCLEAR, and opens the relevant source reference and extracted tender text where available.
5. **Prepare.** The contractor works through an ordered checklist, marks tasks complete, tracks progress, and keeps critical or unresolved tasks visible.
6. **Review costs.** The contractor enters or edits cost estimates and an expected or benchmark contract value. Calculations update immediately in South African Rand (ZAR/R) and show whether the entered value covers estimated costs.
7. **Take the report.** The contractor downloads one complete report containing the analysis, evidence labels and sources, checklist and its current progress/statuses, and current cost results.

Source: `scope.md > The Core Loop`, `scope.md > What "Working" Looks Like`, `scope.md > The POC Boundary`.

## Screens and Layout

- **Welcome and upload:** A simple, welcoming first view with the Tender Clarity name, an encouraging message, a prominent upload action, a short explanation of the steps after upload, and a small “How it works” explanation for first-time users.
- **Tender workspace:** One clear workspace, ordered from high-level understanding to detailed preparation:
  1. Tender overview.
  2. Critical findings.
  3. Preparation checklist and progress.
  4. Cost worksheet.
  5. Prioritized next actions.
  6. Download Report action.

The layout should make the most important information visible first and allow the contractor to expand findings and return to their source without losing their place.

Source: `scope.md > The Core Loop`, `scope.md > What "Working" Looks Like`.

## Look and Feel

The experience should feel pleasing, helpful, motivational, and reassuring rather than like a complicated procurement system. The learner’s preferred messages are “You don't need to be a big company to understand a tender. Let's make it clear.” and “Every contractor deserves a clear shot.” Use a clean, modern, somewhat colorful but professional visual style. Keep the language plain and supportive. Use distinct labels and visual treatments for STATED, CONCLUSION, and UNCLEAR so the categories remain understandable without relying on color alone.

Source: `scope.md > Inspiration & Identity`; learner’s PRD interview answers about the welcome screen and evidence categories.

## Features and Behavior

### Tender upload and analysis

- The contractor can upload one tender document and start analysis.
- The analysis is based on the uploaded tender. External web search, previous tender or award research, and unrelated sources are not part of the prototype.
- The product generates a plain-language tender overview, important findings, an ordered preparation checklist, and prioritized next actions.
- Missing, ambiguous, or unsupported information must not be presented as a definite requirement. Where the tender does not provide enough information, the product identifies the gap as UNCLEAR.
- **Acceptance criteria:** After one usable tender is uploaded and analyzed, the workspace shows the tender overview and the findings, checklist, and next actions based on that document. If the document cannot be read well enough to support an analysis, the product explains the problem and does not present invented requirements as facts.

Source: `scope.md > The POC Boundary`, `scope.md > Explicitly Cut`.

### Tender overview and critical findings

- The overview presents the tender title/reference, issuing organisation, opening and submission dates, contract period, main scope, an eligibility summary, and “What matters most,” when that information is available in the document.
- The critical findings surface mandatory requirements, required forms and supporting documents, evaluation and point-scoring criteria, important dates, scope requirements, possible disqualification issues, cost inputs, and important unclear information.
- Each important finding has one clear evidence category:
  - **STATED — “The tender says this.”** Present the requirement in plain language and show its section/page reference and the relevant original text. Provide a “View source” action.
  - **CONCLUSION — “Tender Clarity worked this out from the tender.”** Mark it as an interpretation, briefly explain why, and show the supporting source sections/pages and extracted text where available.
  - **UNCLEAR — “The tender doesn't tell us enough.”** Explain what information is missing or ambiguous. Do not guess. Show relevant source context where available.
- The user can expand a finding and open its source context. A full document viewer is not required; a page/section reference and relevant extracted text are sufficient for the prototype.
- Important claims must not be shown without their evidence category. Do not claim the tool can predict or guarantee tender outcomes.
- **Acceptance criteria:** A contractor can distinguish a direct tender statement, an interpretation, and an unknown at a glance; expand a finding to inspect the explanation and source context; and return to the findings without losing their place.

Source: `scope.md > The Unique Kernel`, `scope.md > What "Working" Looks Like`, `scope.md > The POC Boundary`.

### Preparation checklist and next actions

- Convert important requirements and gaps into logically ordered, actionable checklist items.
- Each item explains:
  - What the contractor needs to do.
  - Why it matters.
  - What document, information, or calculation is needed.
  - How the contractor can tell the task is complete.
  - Its source reference and evidence context where applicable.
- The contractor can mark an item complete and reopen it to review its source. Completion updates the visible progress count immediately.
- Keep unresolved and critical items visible, even when other tasks are completed. If information is unclear, create a “Needs clarification” action rather than treating the matter as resolved.
- Use labels such as To do, Completed, Needs clarification, At risk/important, or Optional/recommended where useful. Criticality/importance must remain visible independently of completion.
- Show progress, for example “7 of 15 completed,” and the number of critical items outstanding.
- Show a short, prioritized, read-only list of next actions based on the analysis and checklist.
- **Acceptance criteria:** Marking an item complete changes its status and progress count. An unresolved requirement remains visibly unresolved. Reopening an item exposes its source context.

Source: `scope.md > The Core Loop`, `scope.md > What "Working" Looks Like`.

### Cost worksheet

- The contractor can enter and edit estimates for labour, materials, transport, equipment, other expenses, and overheads, plus an expected or benchmark contract value.
- Recalculate immediately when any value changes:
  - Estimated total cost.
  - Estimated amount remaining after costs.
  - Estimated margin amount and percentage, where margin percentage = (expected/benchmark contract value - estimated total costs) / expected/benchmark contract value × 100.
  - A clear warning when the entered contract value is below estimated costs.
- Present the figures in South African Rand (ZAR/R) as estimates based on user-entered values, not a recommended bid price or accounting/financial advice. Do not claim that a price is competitive or that it will win.
- **Acceptance criteria:** Editing an input updates the displayed calculations without requiring a new tender analysis. A value below estimated costs triggers the warning. Missing or zero contract value does not produce a misleading margin percentage.

Source: `scope.md > The POC Boundary`; learner’s PRD interview answer about cost inputs and calculations.

### Download report

- Provide one clear “Download Report” action that downloads the complete Tender Clarity report as a PDF.
- Include the tender overview, findings and their STATED/CONCLUSION/UNCLEAR labels, available source references and extracted text, checklist with current statuses/progress, prioritized next actions, and current cost results.
- Preserve the distinction between stated facts, conclusions, and unclear information in the downloaded report. Do not imply that download means the submission itself is complete or guaranteed to succeed.
- **Acceptance criteria:** The contractor can download and open a report containing the current analysis, checklist state, and cost results, with evidence labels and source references intact.

Source: `scope.md > The POC Boundary`; learner’s PRD interview answer about downloads.

## States and Boundaries

- **Before upload:** Show the welcoming explanation and upload action; no tender findings or checklist are shown.
- **Analyzing:** Make it clear that the uploaded tender is being processed and that results are not ready yet.
- **Analysis ready:** Show the workspace sections in the order described above.
- **Unreadable or insufficient document:** Explain that analysis could not be completed reliably and allow the contractor to try another document. Do not fill gaps with invented findings.
- **Unclear requirement:** Keep the finding labeled UNCLEAR and offer a clarification action; do not treat it as complete.
- **Cost value missing or zero:** Show entered cost totals where possible, but withhold the margin percentage if there is no usable contract-value basis.
- **No accounts or multiple-tender workflow:** The prototype handles one tender at a time and has no user accounts, payment system, or cloud document library.
- **Persistence:** Keep the analysis and checklist available for the current browser session. No account or permanent database is required.

Source: `scope.md > The POC Boundary`, `scope.md > Explicitly Cut`.

## Product Decisions

- Focus on one tender document and one end-to-end preparation journey, to keep the prototype coherent and demonstrable.
- Make the core journey interactive: upload and analyze, expand and verify findings, complete checklist items and see progress, edit cost inputs and see calculations update, and download one complete report.
- Distinguish STATED, CONCLUSION, and UNCLEAR findings so contractors can tell tender text from interpretation and unknown information.
- Keep web research, previous tender/award research, institutional deployment, advanced financial analysis, and win-probability claims outside the first build.
- Use a single ordered Tender Clarity workspace. Keep the overview and prioritized next actions read-only/generated; simplify source viewing to references and extracted text.
- Do not promise that completing the checklist or using the product guarantees success.

## What We're Building

A small contractor uploads one tender and receives a readable overview, critical evidence-labeled findings with source context, an ordered interactive checklist with progress, a simple editable cost/viability worksheet, prioritized next actions, and a downloadable report preserving those results and evidence distinctions.

## Deferred From the POC

- Separate downloads for the summary, checklist, findings, or worksheet; the prototype provides one complete report.
- Full document viewer; page/section references and extracted text are sufficient.
- External research into previous versions, contracts, awards, or comparable tenders, because the first version should keep its findings grounded in the uploaded document.
- Account system, multiple tenders, cloud storage, payments, or institutional deployment.
- Advanced financial analysis, market pricing advice, and winning-probability predictions.

## Possible Later Enhancements

Historical tender and pricing benchmarks from publicly available procurement information, with sources and dates and clear caveats about differences in scope, duration, location, inflation, and other factors. Potential delivery through governments, municipalities, procurement organizations, or small-business support programs.

## Non-Goals

- Predicting or guaranteeing tender success, because competitors and other external factors affect outcomes.
- Telling the contractor exactly what price to bid; the worksheet only calculates from the contractor’s own estimates and entered benchmark/value.
- Treating AI interpretations or missing information as facts.
- Replacing a procurement authority or completing and submitting the official tender on the contractor’s behalf.

## Open Questions

- **For 4-spec:** Choose a sensible maximum PDF file size and page count for the prototype; do not claim support for every tender PDF, including arbitrary long or scanned documents.
