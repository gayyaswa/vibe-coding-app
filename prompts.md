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

## Day 3 — AI Insights & Visualization Polish (2026-06-03)
*Focus: LangChain AI insights, sunburst visualization, tab/slider UX polish, planning documentation*

---

**Arc 1 — Brainstorming Day 3 scope + visualization upgrade**
> "Shall we look in day 3 of the plan and start brainstorming. I might want to add one more thing to plan — instead of treemap being rectangles, can we visualize into something prettier shapes? Also conventions should be adhered when we are updating documentation — it should center around my learning and share my thinking like we updated yesterday."

Result: Plan Mode session opened. Evaluated sunburst vs. packed bubbles vs. icicle chart via ASCII previews. Sunburst chosen. Day 3 scope set: sunburst, tab CSS, slider delta UX, AI insights, planning docs.
Observation: Brainstorming with ASCII previews before committing to any visualization is now a fixed habit. Seeing the shape before building it takes 2 minutes and saves a potential rebuild.

---

**Arc 2 — UX details: tab borders and slider delta**
> "Couple of high-level decisions for ai insight? Also tabs can we have some curvy border much prettier and add some separation on the border. Also when we change the allocation through slider let's show the text and % change below much bolder — right now % change isn't noticeable."

Result: Tab CSS (curved borders, gap, active state blue fill) and per-slider delta lines (▲ blue / ▼ red, bold) added to plan. Current_pcts was already computed but never surfaced — a silent UX gap.
Observation: The best UX feedback comes from using the app yourself and noticing what's missing. Both of these issues were invisible from the code but immediately obvious from the running app.

---

**Arc 3 — Deep dive into AI pipeline and tech stack**
> "Give me more details about the AI insight pipeline and tech stack involved?"

Result: Full pipeline diagram presented — click → InsightsFacade → InsightFactory → LCEL chain → Anthropic API → st.write_stream(). Token economy explained (cache hit = 10% cost). Portfolio context serialization format shown.
Observation: Understanding the full pipeline before approving it changed what I asked for next. The LangChain question came directly from understanding the SDK layer. Deep technical understanding before implementation is time well spent.

---

**Arc 4 — LangChain instead of Anthropic SDK**
> "Instead of Anthropic SDK can we introduce LangChain SDK abstraction? What I was given to understand with LangChain in the future I am free to use different models for such AI insights feature?"

Result: Architecture changed to LangChain LCEL (ChatAnthropic | ChatPromptTemplate | StrOutputParser). LLM injected as dependency. InMemoryCache replaces Anthropic prompt caching. Model swap = one import change.
Observation: This was a real tradeoff, not a free upgrade. Losing Anthropic's server-side caching was the cost of portability. Making that tradeoff explicitly — knowing what you're accepting and why — is different from just picking a framework because it sounds good.

---

**Arc 5 — Open-source API key safety**
> "I am planning to keep this project open and accessible in GitHub so my course instructor and even others can run this site — if so maybe Claude API keys will become problematic. I want this AI insights feature to be configurable and turned off. But I am planning to submit my app demo using a video where I can showcase the AI insights feature."

Result: Streamlit secrets design: .streamlit/secrets.toml gitignored, secrets.toml.example committed, tab always visible with disabled-but-explained state when no key.
Observation: Asking "who else will run this?" before shipping changed the design. The visible-but-disabled pattern communicates what the feature does to someone who can't run it — which is exactly what a course submission needs to do.

---

**Arc 6 — Planning documentation as project artifact**
> "Can we create individual plan detail and also link it part of day1, day2, day3 documentation to show the instructors and others effective use of such detailed planning? Also if you agree add it to the Claude convention as well."

Result: docs/plan-day1.md, plan-day2.md, plan-day3.md created capturing planning thinking per day. Section 6 (Planning Documents) added to google_doc_content.html. CLAUDE.md updated with planning convention.
Observation: Planning documents are the most honest record of a project. They show what was considered and rejected — the reasoning trail — which is harder to reconstruct from code alone. For a course submission demonstrating AI-assisted development, the planning record is as important as the final product.

---

## Day 4 — Architecture & Documentation (2026-06-03)
*Focus: Module restructuring, code conventions, public GitHub presence, video script*

---

**Arc 1 — Domain module architecture**
> "I would like to see different modules relevant to the domain rather than what we have now one simple utils module. For example, Insight can be a module and I want to see each class goes to its own python file so InsightStrategy base class on own file and the concrete different insight strategy implementations on their own files. Similarly for all other files let's come up with a detail plan."

Result: `utils/` renamed to `portfolio/` (domain-named). Split into 4 sub-packages: `classification/`, `rebalancing/`, `health/`, `insights/`. Each class in its own file named in full snake_case of the class name. All 48 tests still pass after migration.
Observation: Renaming `utils/` to `portfolio/` is a one-word change that communicates the domain clearly. Flat modules feel convenient; domain-organized packages communicate intent and make the codebase navigable to anyone who hasn't read it before.

---

**Arc 2 — Python naming conventions and class docstrings**
> "As far as Python file naming goes are we following a convention — I see in some cases _ is used. Also, can we add a comment to each class what it does in the code?"

Result: Convention formalized: one-class-per-file, file name = full snake_case of class name (e.g. `HealthScoreFactory` → `health_score_factory.py`). One-line docstring on every class stating its role and design pattern. Added to CLAUDE.md as standing conventions.
Observation: Naming consistency is not stylistic — it's navigational. Knowing `HealthScoreFactory` lives in `health_score_factory.py` means you can find any class in the codebase without searching.

---

**Arc 3 — Business logic comments**
> "Let's also comment in the code some of the important business logic that we have implemented. Let's also update the Claude convention to include all this recommendations."

Result: Inline comments added to 6 key non-obvious locations: HOLD_THRESHOLD, proportional delta distribution, ticker-over-sector priority, sum-to-100 slider enforcement, LCEL chain construction, pipeline step sequencing. All added to CLAUDE.md as a mandatory convention with a clear rule: comment the WHY, not the WHAT.
Observation: The best comments explain constraints that aren't visible in the code. A reader can see `HOLD_THRESHOLD = 50.0`; what they can't see is that removing it would flood users with micro-transaction recommendations. The comment closes that gap.

---

**Arc 4 — Video script**
> "This is a deliverable — I need a script so I can refer to and comment on the video walk-through of the application. Key learning especially technical acumen and various key insight prompts that led to high quality deliverable in terms of Architecture/Design, reusability, testability."

Result: 5-minute video script written to `docs/video-script.md` (gitignored). Script structured around: intro → problem & setup → 6-tab live demo → architecture deep dive → key learnings → close. Accurately credits engineering experience as the source of patterns, AI as the implementation accelerator.
Observation: The script needed two rounds of revision to get the attribution right. The first draft positioned the AI as discovering the patterns. The accurate version makes clear: the patterns came from production engineering experience, documented in CLAUDE.md before a line of code was written. That distinction matters for the video.

---

**Arc 5 — README and Google Doc GitHub links**
> "I need to update the README — maybe summarize overview of what this application is, a GIF walking through each tab to showcase the application. Also, an Architecture, Design Diagram and high-level sequence flow for the app. Google Doc eventually I am going to copy it to a cloud Google Doc which means all the internal references for various files should become absolute GitHub URLs."

Result: README rewritten with: 3-sentence project description, Quick Start, Architecture section with 3 Mermaid diagrams (app layers / data flow sequence / domain module layout), Design Patterns table, Testing section, Project Structure, Documentation links. All internal file references in `google_doc_content.html` and `docs/plan-day3.md` converted to `https://github.com/gayyaswa/vibe-coding-app/blob/main/` URLs.
Observation: A README is the first thing a viewer sees on GitHub. The Mermaid diagrams render natively without any extra tooling — they are the architecture documentation, not a link to architecture documentation.

---

**Arc 6 — Cross-project custom commands and demo GIF**
> "CLAUDE.md context and the plan file at ~/.claude/plans/... let's execute this plan?"
> "i generated demo.gif using the command can we update the readme with it?"
> "ok now let's follow the convention to document all this as day 4 plan implementation etc?"

Result: Two user-level custom commands created at `~/.claude/commands/`: `generate-demo-gif.md` and `init-readme.md`. `/generate-demo-gif` invoked to produce `docs/demo.gif` (200KB, cycling through all 6 tabs). README already wired the GIF at the top — command handled it automatically. All three files documented following project conventions.
Observation: User-level commands at `~/.claude/commands/` are available across every Claude Code project — a skill built once applies everywhere. This is different from project-level `.claude/skills/`: project skills capture operational knowledge for one project; user-level commands encode a repeatable workflow recipe you carry to any project.

