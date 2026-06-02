# Prompts Log

Track every AI prompt used during vibe coding, organized by day and iteration.
Format: **Prompt** → Result → Observation

---

## Day 1 — Foundation (2026-06-01)
*Focus: Architecture, core engine, Streamlit app, unit tests, documentation*

---

**Prompt 1 — Define project scope**
> "Still stock portfolio but I want to bucketize stocks by risk factor and categories so let's say create 4 categories Less Risk, Moderate, Growth, Aggressive. Sector Retail and other necessary service stocks are Moderate. Gold, treasury moderate so on so forth."

Result: Full architecture designed in Plan Mode — 4 risk buckets, 5-section Streamlit UI, file structure, rebalancing math, implementation order.
Observation: One natural-language prompt replaced an entire design doc. AI asked clarifying questions before writing any code.

---

**Prompt 2 — Unit tests**
> "Can we also add unit tests for this and other functions that we might add?"

Result: 30 unit tests across `tests/test_categorizer.py` (16) and `tests/test_rebalancer.py` (14). All passed on first run.
Observation: Asking for tests mid-build (not after) caught a division-by-zero edge case in the rebalancer immediately.

---

**Prompt 3 — Project documentation**
> "Deliverable — can we work towards that? Submit a Google Doc explaining what you built. Include: project overview, datasets used, prompts you used during vibe coding, iterations you tried, and any learnings."

Result: `PROJECT_DOCUMENTATION.md` + `google_doc_content.html` with 5 structured sections, real portfolio stats pulled from live code.
Observation: AI read the actual codebase and ran the CSV to get real numbers — not fabricated content.

---

**Prompt 4 — Table format for Google Doc**
> "Let's create each of these sections as an independent table in the Google Doc."

Result: `google_doc_content.html` restructured into 5 color-coded tables — copy-paste into Google Docs preserves all formatting.
Observation: Output format instruction (tables vs prose) required zero back-and-forth.

---

**Prompt 5 — Cross-session context setup**
> "I know you have created iteration as something now but I am thinking today is day 1, I have plan to iterate the visualization and also maybe some refactoring, also add some AI insights. I have 2 more days to do this iterations and I want to track those as iterations and improvement. What should I create from Claude Code perspective so when I start a new session tomorrow all this are taken into account as instructions?"

Result: `CLAUDE.md` created (auto-loaded by Claude Code every session), `prompts.md` restructured by day, project memory saved in Claude's memory system.
Observation: CLAUDE.md is the primary persistence layer — it carries architecture decisions, conventions, and the iteration plan into every future session automatically.

---

**Prompt 6 — Document session persistence as a learning**
> "Can we also document this learning in project documentation? Keep it concise though — to highlight I am using Claude Agent feature by architecture to persist the previous workflow state and continuing."

Result: New row added to the Learnings table in `google_doc_content.html` explaining the two-layer persistence system (CLAUDE.md + agent memory) and how it enables multi-day continuity without re-explaining context.
Observation: The persistence architecture itself became a project learning worth documenting — using the tool well is as notable as what the tool built.

---

## Day 2 — Visualization & Refactoring (planned: 2026-06-02)
*Focus: Chart improvements, treemap, app.py refactor, portfolio health score*

<!-- Add prompts here as Day 2 progresses -->


---

## Day 3 — AI Insights (planned: 2026-06-03)
*Focus: Claude API integration, portfolio commentary, prompt caching*

<!-- Add prompts here as Day 3 progresses -->
