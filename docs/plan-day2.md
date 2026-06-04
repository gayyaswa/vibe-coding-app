# Day 2 Planning — Visualization & Architecture Refactor
**Date:** 2026-06-02  
**Session type:** Iteration on a working Day 1 codebase  
**Planning approach:** Explicit Plan Mode session used before the large refactor (Arc 7)

---

## What I was trying to figure out

Day 1 left a working but monolithic app — `app.py` at 306 lines with all 5 sections inline. I wanted to:
- Make the portfolio visualization more compelling (treemap vs. table-first)
- Rethink the navigation (tabs vs. sidebar)
- Apply engineering patterns I use in production (Strategy, Pipeline, Facade, etc.)
- Establish a consistent blue/grey UI theme
- Add a portfolio health score feature

The Day 1 CLAUDE.md loaded automatically at the start — zero re-explanation of prior context needed. That was the first real test of the persistence setup and it worked exactly as intended.

---

## Key decisions made during planning

### 1. Portfolio Overview: table-first vs. visual-first

**What I considered:** Large holdings table as the primary view — data-dense, functional.

**What I chose:** Treemap as dominant visual, holdings table collapsed in an expander below.

**How I decided:** I asked "what is a treemap?" before agreeing to build it. The AI explained the concept, then I asked for an ASCII mockup of how the portfolio would actually look. Seeing the mockup — Portfolio → risk buckets → individual tickers, area = market value, colored by bucket — made the decision easy. **Brainstorming before approving prevented building something I'd regret.** This became a habit: request a visual mockup for any new chart type before committing to implementation.

---

### 2. Navigation: sidebar radio vs. tabs

**What I considered:** Sidebar radio navigation (Day 1 default — fastest path at the time).

**What I chose:** `st.tabs()` at the top, sidebar reserved for upload + filters only.

**How I decided:** I challenged the Day 1 default. The AI modeled two options — Option A (slim sidebar + top tabs) and Option B (no sidebar at all). Option A kept the sidebar's utility for data management while moving navigation to a more prominent position. The AI didn't resist the change to a Day 1 design decision — it modeled both options and let me decide. **The best design decisions come from the human challenging defaults, not the AI defending them.**

---

### 3. UI Theme: changing bucket colors vs. changing chrome

**What I considered:** A consistent blue/grey palette across the entire app.

**AI's first interpretation:** Change `BUCKET_COLORS` (Less Risk, Moderate, Growth, Aggressive) to blue shades.

**What I pushed back with:** "Previous colors — if they fit with blue/grey, keep them."

**What was chosen:** Blue/grey applied to chrome only (page background, sidebar, cards, chart backgrounds via `config.toml` + CSS). Risk bucket colors left unchanged — they carry semantic meaning.

**Why this mattered:** The AI misread my intent on first pass — it heard "blue/grey" and applied it everywhere including data colors. Catching that before coding saved a significant rollback. **Critical reading of AI responses — not just accepting the first interpretation — is a skill worth developing deliberately.**

---

### 4. Architecture: monolithic app.py vs. views/ + utils/ with patterns

**What I considered:** Leave `app.py` as-is and just add the new features inline (fastest).

**What I chose:** Full refactor — `views/` modules (one `render()` per tab) + `utils/` with Strategy, Pipeline, Facade, Factory, and Registry patterns. `app.py` → ~60-line router.

**How I decided:** I injected my engineering philosophy into CLAUDE.md as a standing instruction: *"use Strategy, Pipeline, Facade, Factory, DI, and Registry when appropriate."* This single instruction permanently reshaped not just today's code but every future session. The AI applied all 6 patterns correctly across 8 new files. **CLAUDE.md is not just documentation — it is the AI's standing orders.** The highest-leverage act of Day 2 was writing that one instruction, not the 8 files that resulted from it.

---

### 5. Session state: full app state vs. inputs only

**What I considered:** Store the enriched DataFrame in session state (full app state persisted across reruns).

**What I chose:** Store only raw inputs (`raw_df`, `targets`). `PortfolioFacade` derived on every run, never stored.

**How I decided:** I brought my Angular background into the discussion — "I prefer centralized state services, not scattered session storage. In Angular we'd use Signals or NgRx Signal Store." The AI mapped this mental model to what Streamlit can actually support and found the nearest equivalent: inputs-only state, everything computed on demand. **Bringing knowledge from a different framework produced a better design. The AI mapped the mental model rather than dismissing it.**

---

### 6. Plan Mode before the large refactor

I entered Plan Mode explicitly before starting the refactor. The plan was reviewed — Facade decomposition path noted, session state approach revised. Implementation started only after plan approval.

**Why this was the right call:** The refactor touched 8 files and introduced 5 new modules. A mid-implementation structural mistake on this scale would have been expensive to unwind. **The cost of pausing to plan is low. The cost of discovering a structural mistake mid-implementation is high.** Plan Mode as a checkpoint before large changes is now a fixed part of my workflow.

---

## What the planning produced

- `views/` — 5 view modules (overview, allocation, rebalancing, sector, gainloss), each with a `render()` function
- `utils/` — facade.py (PortfolioFacade), pipeline.py (PortfolioPipeline), health.py (HealthScoreFactory + BENCHMARK_REGISTRY)
- `categorizer.py` refactored with Strategy pattern
- `app.py` reduced from 306 → ~60 lines
- Portfolio health score: 3 benchmark cards (Conservative / Balanced / Aggressive Growth), score 0–100
- Blue/grey theme via `.streamlit/config.toml` + CSS overrides
- 42 unit tests (added 12 for health score), all passing

---

## What I learned about planning with AI

**Plan Mode as a design checkpoint:** Entering Plan Mode before a large refactor is distinct from just discussing it. The plan file forces the AI to commit to an approach before touching code — and gives me something concrete to push back on. Three times during Day 2 planning, I changed the plan before a single line was written.

**Instructions compound:** Day 2's highest-leverage act was adding 6 design patterns to CLAUDE.md. Those patterns shaped not just the Day 2 refactor but will shape every future session. Good instructions are investments — they pay dividends across multiple sessions.
