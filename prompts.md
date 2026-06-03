# Prompts Log

Track every AI prompt used during vibe coding, organized by day and iteration.
Format: **Prompt / Conversation Arc** → Result → Key Observation

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

## Day 2 — Visualization & Refactoring (2026-06-02)
*Focus: Tab navigation, treemap + visual-first overview, blue/grey theme, portfolio health score, app.py refactor with design patterns*

---

**Arc 1 — Session resume: CLAUDE.md did its job**
> "I thought we had a plan we finished day 1 and going to continue day 2 improvement. Can you read that from claude.md?"

Result: AI immediately recalled the full Day 2 plan from CLAUDE.md with zero re-explanation needed. Confirmed focus areas before touching any code.
Observation: This was the first real test of the cross-session persistence setup from Day 1. The AI picked up exactly where Day 1 ended — bucket definitions, slider behavior rules, target file structure, all intact.

---

**Arc 2 — Learning by asking: "What is a treemap?"**
> "What is a treemap view?" (after it appeared in the Day 2 brainstorm)

Result: AI explained the concept, then — on request — produced an ASCII mockup of how the portfolio would look as a treemap before any code was written.
Observation: Asking "what is this?" before agreeing to build it was the right instinct. The ASCII mockup let me mentally validate the UI and decide it was worth building. I now use mockups as a standard check before approving any visualization feature.

---

**Arc 3 — Navigation redesign: pushing back on the default**
> "What if instead of pages navigation on the left side we have it as tabs on the top and on clicking tab each UI component load?"

Result: AI proposed two options (Option A: slim sidebar + tabs, Option B: no sidebar). Chose Option A. `st.tabs()` replaced `st.sidebar.radio()`, sidebar now holds only data management and filters.
Observation: The Day 1 design was sidebar-first because it was the fastest path. Day 2 was the right moment to challenge it. The AI didn't resist the change — it modeled both options and let me decide.

---

**Arc 4 — Theme clarification: correcting a misunderstanding**
> "I would like to see consistent blue shades, white and grey mixture. It doesn't make sense to keep different risk colors — similar to what we have."

AI proposed changing `BUCKET_COLORS` (risk bucket colors) to blue shades. I pushed back:
> "Previous colors you had — less risk, moderate, growth, aggressive — if it fits well with blue/grey you can keep the original colors for that."

Result: AI distinguished between *chrome* (page background, sidebar, cards, chart backgrounds → blue/grey) and *data colors* (risk bucket colors → kept as-is). `config.toml` + CSS overrides applied to chrome only. `BUCKET_COLORS` unchanged.
Observation: The AI misread my intent on first pass. Catching that before code was written saved a significant rollback. Critical reading of AI responses — not just accepting the first interpretation — is a skill worth developing.

---

**Arc 5 — Injecting engineering philosophy as standing instructions**
> "In general in my code I try and use these design patterns heavily: Strategy, Pipeline Processing chain, Facade, Factory, Dependency Injection and Registry. I want this patterns to be added to your instruction and want it to use those patterns when appropriate."

Result: Patterns added to `CLAUDE.md` with a table mapping each pattern to where it applies in this codebase. Agent memory updated with `feedback_design_patterns.md`. Day 2 refactor implemented using: Strategy (categorizer), Pipeline (data flow), Facade (PortfolioFacade), Factory (HealthScoreFactory), Registry (BENCHMARK_REGISTRY). `app.py` went from 306 lines to ~60 lines.
Observation: This was the highest-leverage prompt of Day 2. One instruction permanently reshaped not just today's code but every future session. CLAUDE.md is not just documentation — it is the AI's standing orders.

---

**Arc 6 — Session state: bringing Angular knowledge into Streamlit**
> "In general I am not a big fan of having session state in the application. I come from Angular UI where state is managed via Angular Signals or NgRx Signal Store — centralized in memory, not browser storage."

Result: Architecture shifted from storing the enriched DataFrame in session state to storing only raw inputs (`raw_df`, `targets`). `PortfolioFacade` is now derived on every run rather than stored. Documented in both code and plan as a "stateless-as-possible" pattern.
Observation: Bringing knowledge from a different framework (Angular) into a Streamlit discussion produced a better design. The AI didn't dismiss the mental model — it mapped it to what Streamlit can actually support and found the closest equivalent.

---

**Arc 7 — Plan Mode as a design checkpoint**
> [Used /plan before starting implementation. Reviewed the plan. Commented on Facade decomposition and session state.]

Result: Plan updated before any code was written — Facade decomposition path documented for future, session state approach revised. Implementation started only after plan approval.
Observation: Entering Plan Mode before a large refactor is now part of my workflow. The cost of pausing to review is low. The cost of discovering a structural mistake mid-implementation is high.

---

**Arc 8 — Capturing operational knowledge as a project skill**
> "Can we add it [streamlit run command] as a skill for future use?"

Result: `.claude/skills/run-app/SKILL.md` created. Added `~/Library/Python/3.9/bin` to `~/.zshrc` PATH. Future sessions can launch the app with `/run` without re-discovering the command.
Observation: Skills are how you stop re-solving the same setup problem every session. This is distinct from CLAUDE.md (which is about architecture and conventions) — skills are about operational commands the AI should be able to execute without thinking.

---

## Day 3 — AI Insights (planned: 2026-06-03)
*Focus: Claude API integration, portfolio commentary, prompt caching*

<!-- Add prompts here as Day 3 progresses -->
