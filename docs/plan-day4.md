# Day 4 Planning — Architecture Hardening & Documentation
**Date:** 2026-06-03  
**Session type:** Refactoring + documentation + deliverable production  
**Planning approach:** Extended Plan Mode session covering 5 independent workstreams

---

## What I was trying to figure out

Day 4 had no new features. The goal was to take a working 3-day prototype and harden it into something that could represent professional-quality work publicly on GitHub — and produce the video and documentation deliverables required by the course.

The planning session covered four distinct areas that rarely come up together: module architecture, code commenting conventions, public GitHub presence, and a video script for a 5-minute recorded walkthrough. The unusual scope meant the plan had to sequence the workstreams correctly so later steps (README, Google Doc URL conversion) could use the correct file paths after the module migration.

---

## Key decisions made during planning

### 1. Rename `utils/` → `portfolio/`

**What I decided:** Rename the top-level package from the generic `utils/` to `portfolio/` — a domain-specific name that communicates what the package contains without reading any of its files.

**Options considered:**
- Keep `utils/` — minimal change, familiar convention
- Use `domain/` — DDD terminology, more generic
- Use `core/` — common in many frameworks but semantically vague
- Use `portfolio/` — clearly names the domain

**Why portfolio/:** A new reader who has never seen this codebase sees `from portfolio.classification import ...` and knows immediately what domain they're in. `from utils.categorizer import ...` tells them nothing. Naming is documentation.

**What was rejected and why:** `domain/` and `core/` felt like framework conventions rather than project conventions. The project is about portfolios; the package should say so.

---

### 2. One class per file, named after the class

**What I decided:** Every class lives in its own file. The file name is the full snake_case of the class name: `HealthScoreFactory` → `health_score_factory.py`, `InsightStrategy` → `insight_strategy.py`.

**Options considered:**
- Group by role within a file (e.g., all strategies in one `strategies.py`)
- Use short in-context names (`base.py`, `factory.py`)
- Full class name as file name

**Why full class name:** The contract is simple and deterministic: you can find any class without searching. `CompositeClassifier` is in `composite_classifier.py`. Period. Short in-context names (`base.py`) lose meaning when the package grows past 3 files. Full names stay navigable at any scale.

**What was rejected:** Grouping by role would have replicated the original problem — multiple classes in one file, requiring you to know the grouping convention to find a class.

---

### 3. Class docstrings and business logic comments

**What I decided:**
- Every class gets one-line docstring: what the class IS in the domain, and which design pattern it implements
- Inline comments only for non-obvious WHYs: hidden constraints, business rules, workarounds
- No comments for code that is self-explanatory from its names

**Key business logic that received comments:**
- `HOLD_THRESHOLD = 50.0` — prevents micro-transaction noise
- Proportional delta distribution — why weight-based not equal-split
- Ticker-over-sector priority in `CompositeClassifier` — the Bitcoin proxy exception
- Manual sum-to-100 sliders — the Streamlit rerun loop problem
- LCEL chain construction — why built at init for prompt caching

**Why this split:** Class docstrings compress the mental model of what a system is. Inline comments explain constraints that are invisible from the code. They serve different readers: docstrings serve someone orienting to the system; inline comments serve someone debugging or modifying specific logic.

---

### 4. Video script attribution

**What I decided:** The video script needed explicit accuracy about what came from my engineering experience vs. what the AI contributed.

**The problem:** First drafts of the script implied the AI discovered the design patterns through critique. This is factually wrong. The patterns (Strategy, Facade, Pipeline, Factory, Registry, DI) came from production engineering experience, were documented in CLAUDE.md before Day 1 code was written, and were given to the AI as mandatory conventions to implement.

**Why this matters:** The video is a course deliverable being evaluated on AI-assisted development as a practice. Misrepresenting where the architectural judgment came from would give a false picture of what vibe coding looks like at a professional level. The accurate picture is: engineering experience sets the architectural contract; the AI implements it faithfully and fast.

**What the revision changed:** Two sections — Architecture Deep Dive and Key Learnings — were rewritten to make clear that Day 1 was an intentional fast prototype, Day 2 was where engineering discipline kicked in (patterns documented before refactoring), and the AI's role throughout was skilled implementation within constraints I set.

---

### 5. README architecture diagrams

**What I decided:** Three Mermaid diagrams in the README:
1. App layers (CSV → Facade → domain sub-packages → views)
2. Data flow sequence diagram (user interaction → pipeline → LLM streaming)
3. Domain module layout (all files in portfolio/)

**Why Mermaid over images:** Mermaid diagrams render natively on GitHub without any external tooling. They are version-controlled as code. They update when the architecture changes (if you update the diagram). An image file becomes stale and no one knows.

**Why three diagrams:** Each answers a different question. The app layers diagram answers "how is this structured?" The sequence diagram answers "what happens when I click?" The module layout diagram answers "where does each class live?"

---

## What the planning produced

- A sequenced 5-workstream plan (W1: migration → W2: comments → W3: CLAUDE.md → W4: URLs → W5: README + script)
- Migration order that avoids broken intermediate states (create new package first, delete old only after tests pass)
- A video script that accurately attributes engineering judgment to the engineer and implementation speed to the AI
- README structure with three Mermaid diagrams that communicate the architecture to a first-time reader

---

## What I learned about planning and documentation

**Documentation is design.** Deciding that `portfolio/insights/insight_strategy.py` is the correct location for `InsightStrategy` is an architectural decision, not a filing decision. The module structure communicates the mental model of the system.

**The video script was the most revealing artifact.** Writing a script forces you to state, on the record, what you actually did. The revision process — catching and correcting the attribution — was a clearer articulation of the human/AI collaboration model than anything in the code or plan documents.

**README Mermaid diagrams close the loop.** Days 1–3 produced running code and planning documents. Day 4's README connects them: a new reader can understand the architecture, the data flow, and the module layout without reading any of the plan documents. The diagrams are the summary of three days of design decisions.

---

## Day 4 Addendum — Cross-project tooling and demo GIF

### 6. User-level custom commands

**What I decided:** Create two commands at `~/.claude/commands/` — `generate-demo-gif` and `init-readme` — so any future Claude Code project can produce a demo GIF and a structured README in one invocation.

**Options considered:**
- Project-level `.claude/skills/` — available only within this project
- User-level `~/.claude/commands/` — available in every Claude Code project on this machine
- Manual documentation each time — no automation, high repetition cost

**Why user-level:** The GIF generation recipe and the README template are project-agnostic workflows, not this project's operational knowledge. A skill that lives only in this repo's `.claude/` folder dies with this repo. A user-level command is a permanent addition to how I work.

**What was rejected:** Project-level skills were the obvious placement since we already have one (`run-app`). The distinction that changed the decision: `run-app` is specific to this project's Streamlit launch command; `generate-demo-gif` is a recipe that detects the framework and adapts. That adaptability belongs at the user level.

---

### 7. Demo GIF production

**What I decided:** Run `/generate-demo-gif` to produce `docs/demo.gif` cycling through all 6 tabs, and wire it into the top of `README.md` immediately after the tagline.

**How it worked:** The command read the project (detected Streamlit, identified 6 tabs), wrote `scripts/generate_demo_gif.py` tailored to this app, installed Playwright + Pillow, ran the script to capture each tab, stitched into a GIF, and updated `README.md` automatically. No manual steps.

**Result:** 200KB GIF committed to `docs/demo.gif`. README already had `![App demo](docs/demo.gif)` on line 7 — the command inserted it without being told where to put it.

**What I learned:** The investment in a user-level command is recovered on the first use. Building the command and running it in the same session made the GIF appear faster than writing the Playwright script from scratch would have. Automation at the tooling level compounds the same way CLAUDE.md conventions do at the coding level.
