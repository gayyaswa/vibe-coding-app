# Day 1 Planning — Architecture & Foundation
**Date:** 2026-06-01  
**Session type:** Greenfield — no prior codebase  
**Planning approach:** Clarifying prompts in conversation (no formal Plan Mode session)

---

## What I was trying to figure out

I had a rough idea — a stock portfolio app that buckets holdings by risk. But I didn't know:
- How many buckets, and what goes in each one
- Whether sector rules alone would be enough, or if I needed ticker-level overrides
- How the rebalancing math should work — should it concentrate sells on one stock or distribute?
- What the Streamlit structure should look like across 5 sections

The planning happened through the first prompts. The AI asked clarifying questions before writing code, which forced me to think through things I hadn't consciously decided yet.

---

## Key decisions made during planning

### 1. Risk classification: sector-only vs. two-layer lookup

**What I considered:** Just use sector rules — Technology → Growth, Commodities → Moderate, etc.

**What I chose:** Two-layer lookup: ticker override first, sector rule as fallback.

**Why:** I knew MSTR (MicroStrategy) is effectively a Bitcoin proxy even though its sector label says "Technology." Pure sector rules would put it in Growth, but I wanted it in Aggressive. The ticker override layer let me express that judgment explicitly. This was my first clear lesson in how AI and human domain knowledge divide the work: the AI structures the framework, the human fills in the judgment calls the AI can't make independently.

---

### 2. Rebalancing HOLD threshold: zero tolerance vs. noise floor

**What I considered:** Label every stock with a non-zero delta as BUY or SELL — technically correct.

**What I chose:** Deltas under $50 labeled HOLD.

**Why:** When I saw the raw output — "SELL $2.14 of MMF" — I knew immediately it was wrong in practice even if mathematically right. I proposed the $50 threshold; the AI implemented it. Lesson: AI output needs human review not just for correctness, but for *usefulness*. The code was right. The judgment about what makes output actionable was mine.

---

### 3. Delta distribution: concentrated vs. proportional

**What I considered:** Sell the most overweight stock in a bucket first (concentrated approach — simpler logic).

**What I chose:** Distribute bucket delta proportionally across all stocks by current weight.

**Why:** The AI presented both options neutrally. I had to think about what kind of investor this app is for — passive vs. active. Proportional distribution matched a passive investor philosophy: spread changes evenly rather than concentrating in one name. This was less about AI capability and more about me clarifying my own design intent. Prompts that force a choice reveal assumptions you didn't know you had.

---

### 4. Slider sum constraint: auto-adjust vs. manual enforcement

**What I considered:** Auto-adjust sibling sliders so total always stays at 100% as the user drags.

**What I chose:** Independent sliders + real-time sum display + warning + disabled confirm button.

**Why:** I wanted auto-adjust — it felt like better UX. The AI explained *before writing any code* why it would break Streamlit's rerun model: every slider change triggers a full page rerun, and auto-adjusting other sliders during a rerun creates an infinite loop. I didn't know this constraint existed. Understanding it before building saved a refactor later. Trusting the AI on framework-specific constraints I hadn't hit before was an early lesson in when to defer.

---

## What the planning produced

- 4 risk buckets: Less Risk / Moderate / Growth / Aggressive
- 5-section Streamlit UI: Portfolio Overview, Allocation Dashboard, Rebalancing Engine, Sector Breakdown, Gain/Loss Summary
- `utils/categorizer.py`: two-layer classification (ticker override + sector fallback)
- `utils/rebalancer.py`: proportional delta distribution, $50 HOLD threshold
- 30 unit tests across `test_categorizer.py` (16) and `test_rebalancer.py` (14) — all passed on first run

---

## What I learned about planning with AI

The biggest insight from Day 1: **one natural-language prompt replaced an entire design doc.** Describing the app in plain language and letting the AI ask clarifying questions surfaced decisions I hadn't consciously made yet. By the end of the first conversation, the full architecture was clear — not because I had planned it in advance, but because the back-and-forth forced me to articulate it.
