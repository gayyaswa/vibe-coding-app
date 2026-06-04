# Day 3 Planning — AI Insights + Visualization Polish
**Date:** 2026-06-03  
**Session type:** Feature addition + UI polish  
**Planning approach:** Extended Plan Mode session — multiple rounds of brainstorming before any code

---

## What I was trying to figure out

Day 3 had two goals going in: add AI-powered portfolio insights using the Claude API, and upgrade the portfolio visualization from rectangles to something prettier. The planning session grew longer than Days 1 or 2 because the AI feature involved real design decisions — not just *what* to build, but *how* to architect it so it stays maintainable and open-source safe.

---

## Key decisions made during planning

### 1. Visualization: treemap rectangles → sunburst circles

**What I considered:**
- Sunburst chart (radial/circular, same hierarchy as treemap, Plotly-native)
- Packed bubble chart (visually striking, no hierarchy — harder in Plotly without D3)
- Icicle chart (still rectangular, just oriented differently — less of a shape change)

**What I chose:** Sunburst.

**Why:** Same data, same hierarchy (Portfolio → risk_bucket → ticker), same BUCKET_COLORS — but arc/circular shapes instead of rectangles. Plotly-native means zero extra libraries. The key bonus: click any risk bucket arc and it zooms in to show only that bucket's holdings — the treemap couldn't do that cleanly. One file changed ([views/overview.py](../views/overview.py)), nothing else touched.

---

### 2. Tab styling: flat defaults → curved borders with separation

**What I decided:** CSS injection via `st.markdown()` targeting Streamlit's BaseWeb tab classes. Curved top corners (`border-radius: 12px 12px 0px 0px`), gap between tabs (`gap: 8px`), active tab filled with primaryColor (`#1565C0`). All colors sourced from `config.toml` — no new hex values scattered through views.

**Scope:** One CSS block in [app.py](../app.py), before the `st.tabs()` call. Nothing else touched.

---

### 3. Allocation slider: invisible delta → bold ▲▼ feedback

**What I noticed:** `current_pcts` was computed in the allocation view but never shown. Users had no way to see how far a slider was from their actual current allocation without mentally subtracting.

**What I chose:** After each slider, show `▲ +10.0% from current (24.3%)` in blue for increases, `▼ -5.0%` in red for decreases — rendered bold directly below each slider. Under 0.5% delta shows a muted "● At current allocation" line.

**Scope:** 10 lines inside the existing loop in [views/allocation.py](../views/allocation.py).

---

### 4. AI tech stack: raw Anthropic SDK vs. LangChain

**What I considered:** Use the `anthropic` Python SDK directly — simpler, fewer dependencies, supports Anthropic's prompt caching natively.

**What I chose:** LangChain (`langchain-anthropic` + `langchain-core`) with LCEL chains.

**Why:** Model portability. With LangChain, swapping Claude for GPT-4o or Gemini in the future is one import change and one constructor line — the chain, prompts, streaming, and tests all stay identical. For a course project kept open on GitHub, demonstrating model-agnostic architecture is valuable.

**The tradeoff:** Anthropic's `cache_control: {"type": "ephemeral"}` prompt caching (server-side, 90% cost reduction on repeated context) isn't cleanly supported through LangChain's abstraction. Replaced with LangChain's `InMemoryCache` — which handles the more common case (user clicks Regenerate on the same insight) without any API call.

**This was worth documenting explicitly** because it's a real architectural tradeoff, not a clear winner. Portability vs. provider-specific optimization. For this app's scale and purpose, portability wins.

---

### 5. LLM as injected dependency, not hardcoded

**What I decided:** The `ChatAnthropic` LLM is created once in [views/insights.py](../views/insights.py) from the API key, then injected into `InsightsFacade`, which passes it into each strategy via `InsightFactory.create(type, llm)`. Each strategy stores the LLM and builds its own LCEL chain in `__init__`.

**Why:** Fully testable — tests inject a mock LLM, no real API calls needed. Swapping models = one line in the view, zero changes in `utils/`. This is the Dependency Injection pattern already in CLAUDE.md's standing instructions — it applied naturally here.

**Future thought:** If a second AI feature is added later, a higher-level `AIFacade` routing to multiple feature facades makes sense. Not built now — no hypothetical architecture for a feature that doesn't exist yet.

---

### 6. Insight types: 3 planned → 2 chosen

**What was planned:** Risk commentary + Rebalancing rationale + Sector concentration.

**What I chose:** Rebalancing rationale + Sector concentration only.

**Why:** Risk commentary overlaps significantly with what the Portfolio Health Score already shows (bucket deviations vs. benchmarks). Adding it would have been repetitive. Two focused, distinct insight types are more valuable than three overlapping ones.

---

### 7. Open-source safety: API key management

**The problem:** The project is kept on GitHub and shared with course instructors. A hardcoded or accidentally committed API key would be a real issue.

**What I decided:**
- API key read via Streamlit secrets: `st.secrets.get("ANTHROPIC_API_KEY")` with `os.environ` fallback
- `.streamlit/secrets.toml` — gitignored, real key lives here for local dev and demo recording
- `.streamlit/secrets.toml.example` — committed to GitHub, template for others to fill in
- Tab always visible even without a key — instructor sees the full UI layout and cards, just with Generate buttons disabled and a clear setup message

**Why visible-but-disabled over hidden:** The AI Insights feature is a significant part of Day 3. If the tab hid itself when no key was present, the instructor would never know it existed unless they set up a key first. Visible-but-disabled communicates "this feature exists and here's how to enable it" — which is the right message for a course submission.

---

### 8. UX decisions: streaming, session caching, missing targets guard

- **Streaming:** Responses appear token-by-token via `st.write_stream()` + LangChain's `chain.stream()`. Feels alive, gives instant feedback.
- **Session caching:** Full response saved to `st.session_state[f"insight_{type}"]` after stream completes. Tab switches don't re-trigger generation. "Regenerate" button clears the key.
- **Missing targets guard:** Rebalancing Rationale Generate button is `disabled=True` until targets are set in Allocation Dashboard. Forces meaningful context before generating. Sector Concentration is always enabled (no targets needed).

---

## Architecture of utils/insights.py

Follows the same Strategy + Registry + Factory + Facade chain already in `utils/health.py`:

```
INSIGHT_REGISTRY              dict: type name → strategy class
InsightStrategy (abstract)    __init__(llm), build_prompt_template(), build_context(), build_question()
RebalancingRationaleInsight   LCEL chain: ChatPromptTemplate | ChatAnthropic | StrOutputParser
SectorConcentrationInsight    LCEL chain: ChatPromptTemplate | ChatAnthropic | StrOutputParser
InsightFactory                create(type, llm) → InsightStrategy
InsightsFacade                stream_insight(type) → generator of token strings
```

---

## What I learned about planning with AI

**Longer planning pays off more for AI features.** The Day 3 planning session was longer than Days 1 and 2 combined — but it produced zero mid-implementation reversals. Every architectural choice (LangChain vs. SDK, DI pattern, streaming UX, session caching, key management) was decided before touching code.

**Planning is where you learn what you actually want.** The "3 insight types → 2" decision happened during brainstorming, not implementation. So did the LangChain choice, the DI pattern, and the visible-but-disabled key handling. If I had just started coding Day 3's features, I would have discovered these decisions mid-build — more expensive, more disruptive.

**AI planning sessions have a multiplier effect on implementation.** The more thoroughly you plan with the AI, the less you have to explain during implementation. The AI that helped plan also implemented — and because the decisions were already made and recorded, implementation was mechanical execution of an agreed design.
