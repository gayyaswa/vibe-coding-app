# Stock Portfolio Risk Analyzer — Claude Code Instructions

## What this project is
A Streamlit web app that loads a stock portfolio from CSV, auto-assigns each stock to one of 4 risk buckets (Less Risk / Moderate / Growth / Aggressive), and recommends rebalancing actions. Built as a vibe-coding project over 3 days.

Run with: `streamlit run app.py`
Tests: `python3 -m pytest tests/ -v` (30 tests, all pass)

## File map
```
app.py                      Streamlit UI — 5 sidebar sections
utils/categorizer.py        Risk bucket assignment + derived columns (market_value, pnl, etc.)
utils/rebalancer.py         Rebalancing math — bucket_summary() and compute_rebalancing()
data/portfolio_sample.csv   20 synthetic holdings, 5 per bucket
tests/test_categorizer.py   16 unit tests
tests/test_rebalancer.py    14 unit tests
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

### Day 2 — Visualization & Refactoring (planned)
Likely focus areas (confirm with user at start of session):
- [ ] Improve chart quality: better tooltips, consistent color legends, richer hover data
- [ ] Add treemap view — portfolio composition by sector and bucket in one chart
- [ ] Improve Gain/Loss section: add sparkline-style trend or % bar overlay
- [ ] Refactor app.py — extract each section into its own function or module (app.py is getting long)
- [ ] Add a portfolio health score widget based on bucket allocation vs common benchmarks

### Day 3 — AI Insights (planned)
Likely focus areas (confirm with user at start of session):
- [ ] Add an AI Insights section using the Claude API
- [ ] Insights to generate: portfolio risk commentary, rebalancing rationale, sector concentration warnings
- [ ] Consider prompt caching for repeated portfolio analysis
- [ ] Add to google_doc_content.html: Day 2 and Day 3 iterations + prompts

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

### Adding AI features (Day 3)
- Use the `anthropic` Python SDK
- Default model: `claude-sonnet-4-6`
- Include prompt caching on any repeated analysis calls (portfolio data as cached prefix)
- Keep AI calls in a separate `utils/insights.py` module — do not mix into app.py directly

## Risk bucket definitions (do not change without user confirmation)
| Bucket     | What goes in it |
|------------|----------------|
| Less Risk  | Treasuries, Gov Bonds, Money Market, stable blue-chips (JNJ, PG) |
| Moderate   | Gold (GLD, IAU), Retail (WMT, COST), Consumer Staples, Utilities |
| Growth     | Tech (AAPL, MSFT, NVDA), Healthcare (UNH), Consumer Discretionary (AMZN) |
| Aggressive | Crypto-adjacent (MSTR, COIN), Emerging Markets (EEM), speculative ETFs |

Ticker override takes priority over sector rule. Both are in `utils/categorizer.py`.

## Key design decisions (don't undo without checking)
- Sliders use manual sum-to-100 enforcement (not auto-adjust) — auto-adjust causes Streamlit rerun loops
- HOLD_THRESHOLD = $50 in rebalancer.py — prevents micro-transaction noise
- Rebalancing distributes bucket delta proportionally by current stock weight within each bucket
- Navigation is `st.sidebar.radio` (not tabs or pages/) — session state shared cleanly this way
