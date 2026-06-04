# Stock Portfolio Risk Analyzer — Claude Code Instructions

## What this project is
A Streamlit web app that loads a stock portfolio from CSV, auto-assigns each stock to one of 4 risk buckets (Less Risk / Moderate / Growth / Aggressive), recommends rebalancing actions, and scores the portfolio against 3 benchmarks. Built as a vibe-coding project over 4 days.

Run with: `streamlit run app.py`
Tests: `python3 -m pytest tests/ -v` (48 tests, all pass)

## File map
```
app.py                                      Streamlit router — ~115 lines, tab navigation, PortfolioFacade
views/overview.py                           Portfolio Overview: sunburst + health score cards + holdings table
views/allocation.py                         Allocation Dashboard: donut chart + target sliders
views/rebalancing.py                        Rebalancing Engine: BUY/SELL/HOLD table + delta bar chart
views/sector.py                             Sector Breakdown: grouped bar + heatmap
views/gainloss.py                           Gain/Loss Summary: P&L bar + table + cost vs market chart
views/insights.py                           AI Insights tab: streaming LangChain insight cards
views/__init__.py                           apply_theme() helper — sets chart paper/plot background colors

portfolio/facade.py                         PortfolioFacade — cross-cutting entry point for all views (Facade pattern)
portfolio/pipeline.py                       PortfolioPipeline — sequential data transform steps (Pipeline pattern)

portfolio/classification/
  registries.py                             TICKER_OVERRIDE, SECTOR_RULES, BUCKET_ORDER, BUCKET_COLORS
  classification_strategy.py               ClassificationStrategy Protocol
  ticker_override_strategy.py              TickerOverrideStrategy
  sector_rule_strategy.py                  SectorRuleStrategy
  composite_classifier.py                  CompositeClassifier + DEFAULT_CLASSIFIER
  enricher.py                              assign_risk_bucket()

portfolio/rebalancing/
  engine.py                                bucket_summary(), compute_rebalancing(), HOLD_THRESHOLD

portfolio/health/
  health_score.py                          HealthScore dataclass
  benchmarks.py                            BENCHMARK_REGISTRY
  health_score_factory.py                  HealthScoreFactory (Factory + Registry patterns)

portfolio/insights/
  insight_strategy.py                      InsightStrategy ABC (Strategy pattern)
  rebalancing_rationale_insight.py         RebalancingRationaleInsight
  sector_concentration_insight.py          SectorConcentrationInsight
  insight_factory.py                       InsightFactory + INSIGHT_REGISTRY
  insights_facade.py                       InsightsFacade

.streamlit/config.toml                     Blue/grey UI theme (primaryColor, backgroundColor, etc.)
data/portfolio_sample.csv                  20 synthetic holdings, 5 per bucket
tests/test_categorizer.py                  16 unit tests
tests/test_rebalancer.py                   14 unit tests
tests/test_health.py                       12 unit tests (health score, benchmark registry, factory)
tests/test_insights.py                     6 unit tests (LangChain insight strategies)
prompts.md                                 Running log of every prompt used — update after every prompt
google_doc_content.html                    Project documentation as HTML tables — edit this, paste into Google Docs
docs/plan-day*.md                          Per-day planning summaries: decisions, options, learnings
```

## Iteration plan

### Day 1 — COMPLETE (2026-06-01)
- [x] Risk bucket classification engine (categorizer.py)
- [x] Rebalancing math engine (rebalancer.py)
- [x] Full Streamlit app: Portfolio Overview, Allocation Dashboard, Rebalancing Engine, Sector Breakdown, Gain/Loss Summary
- [x] 30 unit tests, all passing
- [x] Project documentation (google_doc_content.html)

### Day 2 — Visualization & Refactoring — COMPLETE (2026-06-02)
- [x] Refactor app.py → views/ (overview, allocation, rebalancing, sector, gainloss) — ~60-line router
- [x] Add Strategy pattern to categorizer.py, Pipeline + Facade in utils/, Factory + Registry in health.py
- [x] Navigation: sidebar radio → st.tabs() (sidebar now holds upload + filters only)
- [x] Portfolio Overview redesigned: sunburst dominant, holdings table collapsed in expander
- [x] Portfolio Health Score: 3 benchmark comparisons (Conservative / Balanced / Aggressive Growth)
- [x] UI Theme: blue/grey chrome via .streamlit/config.toml + chart CSS overrides
- [x] Session state: inputs-only (raw_df, targets) — PortfolioFacade derived on every run
- [x] 42 unit tests (added 12 for health score), all passing

### Day 3 — AI Insights — COMPLETE (2026-06-03)
- [x] AI Insights tab: Rebalancing Rationale + Sector Concentration via LangChain + Claude Sonnet 4.6
- [x] InsightStrategy ABC + Registry + Factory for extensible insight types
- [x] LLM injected as dependency — testable without live API calls
- [x] Graceful degradation when ANTHROPIC_API_KEY is absent
- [x] 48 unit tests (added 6 for insights), all passing

### Day 4 — Architecture & Documentation — COMPLETE (2026-06-03)
- [x] Rename utils/ → portfolio/ (domain-named package)
- [x] Split into domain sub-packages: classification/, rebalancing/, health/, insights/
- [x] One class per file, named after the class in snake_case
- [x] Class docstrings on every class
- [x] Business logic inline comments on all key invariants
- [x] CLAUDE.md conventions consolidated
- [x] README: architecture diagrams, project overview, quick start
- [x] google_doc_content.html: absolute GitHub links for all file references
- [x] Video script saved to docs/video-script.md (gitignored)

## Conventions to follow every session

### Always do after any code change
- Run `python3 -m pytest tests/ -v` before reporting work done
- If new functions are added to `portfolio/classification/` or `portfolio/rebalancing/`, add unit tests

### Prompt tracking
- After every user prompt that produces a meaningful result, append it to `prompts.md` under the correct Day section
- Format: Prompt text → What it produced → Key observation

### Documentation updates
- If a new feature is added, update the relevant section in `google_doc_content.html`
- The Iterations table in the HTML should reflect actual completed iterations, not plans

### Adding AI features
- Use LangChain (`langchain-anthropic`, `langchain-core`) — not the raw Anthropic SDK — for model portability
- Default model: `claude-sonnet-4-6` via `ChatAnthropic`
- Inject the LLM as a dependency — create it in the view layer, pass it into Facade and Strategy classes
- Keep AI calls in `portfolio/insights/` + `views/insights.py` — do not mix into app.py directly
- API key via `st.secrets.get("ANTHROPIC_API_KEY")` with `os.environ` fallback
- AI tabs must degrade gracefully: always visible, Generate buttons disabled with clear instructions when no key

### Code conventions

#### Module organization
- Business logic lives in `portfolio/` — domain-named, not generic
- `portfolio/` is organized into domain sub-packages: `classification/`, `rebalancing/`, `health/`, `insights/`
- Each sub-package has an `__init__.py` that re-exports all public symbols
- Always import from the sub-package root, never from internal files:
  - Correct: `from portfolio.insights import InsightsFacade`
  - Wrong:   `from portfolio.insights.insights_facade import InsightsFacade`
- `portfolio/facade.py` and `portfolio/pipeline.py` stay at the top level — cross-cutting, no single domain
- When adding a new domain feature, create a new sub-package following this same layout

#### File naming
- One class per file; file name = full snake_case of the class name
  e.g. `InsightStrategy` → `insight_strategy.py`, `HealthScoreFactory` → `health_score_factory.py`
- Function-only modules: use a short descriptive noun — `engine.py`, `enricher.py`, `registries.py`
- Views stay as-is: one file per tab, named after the tab

#### Class docstrings
Every class must have a one-line docstring stating what the class IS in the domain and the design pattern it implements:
- Correct: `"""Single entry point for all views (Facade pattern); wraps classification, rebalancing, health, and insights."""`
- Wrong:   `"""This class calls bucket_summary() and returns results."""`

#### Inline comments
Add comments only when the WHY is non-obvious: hidden constraints, business rules, workarounds, non-obvious invariants.
Do not comment what the code does — well-named identifiers already say that.
Key business rules that must always carry a comment:
- `HOLD_THRESHOLD` — the $50 micro-transaction guard
- Proportional delta distribution — why weight-based, not equal-split
- Ticker-over-sector priority in `CompositeClassifier`
- Manual sum-to-100 slider enforcement — the auto-adjust rerun loop problem
- LCEL chain construction in `InsightStrategy.__init__` — why built at init for prompt caching

### Planning documents
- After each day's session, save a planning summary as `docs/plan-dayN.md`
- Content: key decisions made, options considered, what was rejected and why, what was learned
- Tone: learning-centered — capture the thinking and reasoning, not just the outcome
- Link the new plan from Section 6 of `google_doc_content.html`
- Companion to `prompts.md`: prompts.md tracks the conversation arcs, plan docs capture the architectural thinking

## Risk bucket definitions (do not change without user confirmation)
| Bucket     | What goes in it |
|------------|----------------|
| Less Risk  | Treasuries, Gov Bonds, Money Market, stable blue-chips (JNJ, PG) |
| Moderate   | Gold (GLD, IAU), Retail (WMT, COST), Consumer Staples, Utilities |
| Growth     | Tech (AAPL, MSFT, NVDA), Healthcare (UNH), Consumer Discretionary (AMZN) |
| Aggressive | Crypto-adjacent (MSTR, COIN), Emerging Markets (EEM), speculative ETFs |

Ticker override takes priority over sector rule. Both are in `portfolio/classification/`.

## Design patterns (apply when appropriate, do not force)
These patterns were deliberately chosen based on production engineering experience — apply them when introducing new modules or refactoring:

| Pattern | Where it applies in this codebase |
|---|---|
| **Strategy** | Interchangeable algorithms — e.g. `ClassificationStrategy` for bucket rules, `InsightStrategy` for AI insight types |
| **Pipeline / Chain of Responsibility** | Sequential data transforms — e.g. CSV load → enrich → categorize → rebalance as explicit `PortfolioPipeline` steps |
| **Facade** | Simplify complex subsystems — `PortfolioFacade` wraps all domain packages so views import nothing from `portfolio/` directly |
| **Factory** | Object creation — `HealthScoreFactory` for benchmark scores, `InsightFactory` for LangChain strategy instances |
| **Dependency Injection** | Pass collaborators in, don't hardcode — LLM injected into `InsightsFacade` and strategies for testability |
| **Registry** | Named lookup tables — `TICKER_OVERRIDE`, `SECTOR_RULES`, `BENCHMARK_REGISTRY`, `INSIGHT_REGISTRY` |

When adding a new module or refactoring an existing one, prefer these patterns over ad-hoc functions. Do not force patterns where a plain function is clearer.

## UI theme (do not deviate without confirmation)
- Overall app chrome: blue shades, white, and grey (sidebar, backgrounds, cards, table headers, borders)
- Risk bucket colors are UNCHANGED — Less Risk (blue), Moderate (green), Growth (orange), Aggressive (red) — these carry semantic meaning and complement the blue/grey backdrop
- `BUCKET_COLORS` in `portfolio/classification/registries.py` must NOT be changed
- Apply theme via `.streamlit/config.toml` and targeted CSS overrides in app.py — do not hardcode hex values scattered across views

## Key design decisions (don't undo without checking)
- Sliders use manual sum-to-100 enforcement (not auto-adjust) — auto-adjust causes Streamlit rerun loops
- `HOLD_THRESHOLD = 50.0` in `portfolio/rebalancing/engine.py` — prevents micro-transaction noise
- Rebalancing distributes bucket delta proportionally by current stock weight within each bucket (not equally)
- Navigation is `st.tabs()` (not sidebar radio) — tabs render at top of page, sidebar holds upload + filters only
- Session state stores inputs only (`raw_df`, `targets`) — `PortfolioFacade` is derived on every run
