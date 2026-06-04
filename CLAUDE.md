# Stock Portfolio Risk Analyzer — Claude Code Instructions

## What this project is
A Streamlit web app that loads a stock portfolio from CSV, auto-assigns each stock to one of 4 risk buckets (Less Risk / Moderate / Growth / Aggressive), recommends rebalancing actions, and scores the portfolio against 3 benchmarks. Built as a vibe-coding project over 3 days.

Run with: `streamlit run app.py`
Tests: `python3 -m pytest tests/ -v` (42 tests, all pass)

## File map
```
app.py                      Streamlit router — ~60 lines, tab navigation, PortfolioFacade, delegates to views/
views/overview.py           Portfolio Overview: treemap + health score cards + collapsible holdings table
views/allocation.py         Allocation Dashboard: donut chart + target sliders
views/rebalancing.py        Rebalancing Engine: BUY/SELL/HOLD table + delta bar chart
views/sector.py             Sector Breakdown: grouped bar + heatmap
views/gainloss.py           Gain/Loss Summary: P&L bar + table + cost vs market chart
views/__init__.py           apply_theme() helper — sets chart paper/plot background colors
utils/categorizer.py        Risk bucket assignment (Strategy pattern) + derived columns
utils/rebalancer.py         Rebalancing math — bucket_summary() and compute_rebalancing()
utils/facade.py             PortfolioFacade — single entry point for all views (Facade pattern)
utils/pipeline.py           PortfolioPipeline — sequential data transform steps (Pipeline pattern)
utils/health.py             BENCHMARK_REGISTRY + HealthScoreFactory (Registry + Factory patterns)
.streamlit/config.toml      Blue/grey UI theme (primaryColor, backgroundColor, etc.)
data/portfolio_sample.csv   20 synthetic holdings, 5 per bucket
tests/test_categorizer.py   16 unit tests
tests/test_rebalancer.py    14 unit tests
tests/test_health.py        12 unit tests (health score, benchmark registry, factory)
prompts.md                  Running log of every prompt used — update after every prompt
google_doc_content.html     Project documentation as HTML tables — edit this, paste into Google Docs
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
- [x] Portfolio Overview redesigned: treemap dominant, holdings table collapsed in expander
- [x] Portfolio Health Score: 3 benchmark comparisons (Conservative / Balanced / Aggressive Growth)
- [x] UI Theme: blue/grey chrome via .streamlit/config.toml + chart CSS overrides
- [x] Session state: inputs-only (raw_df, targets) — PortfolioFacade derived on every run
- [x] 42 unit tests (added 12 for health score), all passing

### Day 3 — AI Insights (planned)
Confirm focus areas with user at start of session:
- [ ] Add an AI Insights tab using the Claude API
- [ ] Insights to generate: portfolio risk commentary, rebalancing rationale, sector concentration warnings
- [ ] Use prompt caching on portfolio data (cached prefix) — portfolio DataFrame as context, insights as uncached suffix
- [ ] Update google_doc_content.html: Day 3 iterations + prompts + learnings

## Conventions to follow every session

### Always do after any code change
- Run `python3 -m pytest tests/ -v` before reporting work done
- If new functions are added to categorizer.py or rebalancer.py, add unit tests for them

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
- Keep AI calls in separate `utils/insights.py` + `views/insights.py` — do not mix into app.py directly
- API key via `st.secrets.get("ANTHROPIC_API_KEY")` with `os.environ` fallback
- AI tabs must degrade gracefully: always visible, Generate buttons disabled with clear instructions when no key

### Planning documents
- After each day's session, save a planning summary as `docs/plan-dayN.md`
- Content: key decisions made, options considered, what was rejected and why, what was learned
- Tone: learning-centered — capture the thinking and reasoning, not just the outcome
- Link the new plan from Section 6 of `google_doc_content.html`
- Companion to `prompts.md`: prompts.md tracks the conversation arcs, plan docs capture the architectural thinking that preceded them

## Risk bucket definitions (do not change without user confirmation)
| Bucket     | What goes in it |
|------------|----------------|
| Less Risk  | Treasuries, Gov Bonds, Money Market, stable blue-chips (JNJ, PG) |
| Moderate   | Gold (GLD, IAU), Retail (WMT, COST), Consumer Staples, Utilities |
| Growth     | Tech (AAPL, MSFT, NVDA), Healthcare (UNH), Consumer Discretionary (AMZN) |
| Aggressive | Crypto-adjacent (MSTR, COIN), Emerging Markets (EEM), speculative ETFs |

Ticker override takes priority over sector rule. Both are in `utils/categorizer.py`.

## Design patterns (apply when appropriate, do not force)
The user heavily uses these patterns — apply them when introducing new modules or refactoring:

| Pattern | Where it applies in this codebase |
|---|---|
| **Strategy** | Interchangeable algorithms — e.g. bucket classification rules, benchmark comparison logic, chart rendering per section |
| **Pipeline / Chain of Responsibility** | Sequential data transforms — e.g. CSV load → enrich → categorize → rebalance as explicit pipeline steps |
| **Facade** | Simplify complex subsystems — e.g. a single `PortfolioFacade` that wraps categorizer + rebalancer so views never import utils directly |
| **Factory** | Object creation — e.g. `ChartFactory` that produces consistently styled Plotly figures, `BenchmarkFactory` for health score presets |
| **Dependency Injection** | Pass collaborators in, don't hardcode — e.g. pass classification strategy into categorizer rather than calling it directly |
| **Registry** | Named lookup tables — e.g. `TICKER_OVERRIDE` and `SECTOR_RULES` are already registries; benchmark presets should follow the same pattern |

When adding a new module or refactoring an existing one, prefer these patterns over ad-hoc functions. Do not force patterns where a plain function is clearer.

## UI theme (do not deviate without confirmation)
- Overall app chrome: blue shades, white, and grey (sidebar, backgrounds, cards, table headers, borders)
- Risk bucket colors are UNCHANGED — Less Risk (blue), Moderate (green), Growth (orange), Aggressive (red) — these carry semantic meaning and complement the blue/grey backdrop
- `BUCKET_COLORS` in `categorizer.py` must NOT be changed
- Apply theme via `.streamlit/config.toml` and targeted CSS overrides in app.py — do not hardcode hex values scattered across views

## Key design decisions (don't undo without checking)
- Sliders use manual sum-to-100 enforcement (not auto-adjust) — auto-adjust causes Streamlit rerun loops
- HOLD_THRESHOLD = $50 in rebalancer.py — prevents micro-transaction noise
- Rebalancing distributes bucket delta proportionally by current stock weight within each bucket
- Navigation is `st.tabs()` (not sidebar radio) — tabs render at top of page, sidebar holds upload + filters only
