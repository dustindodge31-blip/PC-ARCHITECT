# PC Architect — Epic Backlog

Tracks implementation work as Epics mapped to the original Master Vision Document's phased roadmap. One epic at a time; each completed epic is committed and pushed to GitHub.

| Epic | Maps to handoff phase | Status |
|---|---|---|
| Epic 1 — Foundation & Desktop Test Harness | Phase 1 | ✅ Done |
| Epic 2 — Visual Identity & Home Dashboard | Phase 1 (UI) | ✅ Done |
| Epic 3 — Build Creator Redesign + Build Score Engine | Phase 2 + Phase 4 (scoring) | ✅ Done |
| Epic 4 — AI Architect | Phase 3 | ✅ Done |
| Epic 5 — Performance Estimators (FPS, bottleneck analysis) | Phase 4 | ✅ Done |
| Epic 6 — Price Tracking | Phase 6 | ✅ Done |
| Epic 7 — Community & Cloud Sync | Phase 5 | Backlog |
| Epic 8 — 3D Workbench / AR | Phase 7 | Backlog |

## Epic 1 — Foundation & Desktop Test Harness ✅
- Parts catalog (`app/core/catalog.py`, `app/data/parts_catalog.json`)
- Live compatibility engine (`app/core/compatibility.py`)
- SQLite build storage (`app/core/storage.py`)
- Flet phone-frame desktop test shell: phone-sized frameless window, status bar, notch, home indicator, draggable, remembers position (`app/main.py`, `app/ui/phone_frame.py`, `app/core/window_state.py`)
- Git repo wired to GitHub remote

## Epic 2 — Visual Identity & Home Dashboard ✅
- Swappable accent-theme system (infrastructure; one theme active for now)
- Redesigned Home dashboard: greeting, AI Architect entry card, category quick-filters, My Builds cards with provisional score badges
- 5-item bottom nav: Home, Builds, AI, Prices, Profile (AI/Prices stubbed)

## Epic 3 — Build Creator Redesign + Build Score Engine ✅
- Real multi-axis Build Score engine (Gaming/Creator/Productivity/Cooling/Noise/Value → weighted overall + tier label + star rating), heuristic from catalog specs (`app/core/scoring.py`)
- Shared score widgets: circular badge, meter bar, star row (`app/ui/score_widgets.py`)
- Build Creator restructured into Overview (thumbnail, score badge, tier, meters) / Parts (icon-led picker rows) tabs with a persistent bottom bar (compatibility, price, power, save)
- Dashboard build cards now use the real scoring engine instead of Epic 2's placeholder

## Epic 4 — AI Architect ✅
- Gemini-powered build generation (`app/core/ai_architect.py`): Gemini picks real catalog part IDs only (structured JSON output, schema-constrained to actual IDs) and writes a short reasoning blurb — never invents specs/prices. Our own compatibility/scoring engines compute everything else.
- Single-shot AI Architect screen (`app/ui/ai_view.py`): prompt box, Generate button, loading state, inline error handling (bad key, network, parse failures)
- Results hand off into the existing Build Creator via a new `load_from_parts()` (`app/ui/build_creator.py`), with the AI's reasoning shown in a dismissible card on the Overview tab
- Gemini API key lives in the project's local `.env` (gitignored); model is `gemini-2.5-flash`, configurable via `GEMINI_MODEL`

## Epic 5 — Performance Estimators ✅
- FPS estimator (`app/core/performance.py`): 8 curated games, resolution/settings/ray-tracing/upscaling/frame-gen controls, heuristic FPS calibrated off the same GPU/CPU gaming indices as the Epic 3 scoring engine (`scoring.gpu_gaming_index`/`cpu_gaming_index`, extracted for reuse)
- Bottleneck analysis: flags GPU/CPU imbalance and low RAM with why/impact/fix explanations, distinct from `compatibility.py`'s "does it work" checks
- New third tab ("Performance") in Build Creator, alongside Overview and Parts

## Epic 6 — Price Tracking ✅
- Simulated price history (`app/core/price_history.py`): deterministic random walk per part ID (no real retail API), Current/Lowest/Highest/Average stats + a "Price Drop" indicator
- Wishlist persisted in the existing SQLite DB (`app/core/storage.py`: `wishlist` table + CRUD)
- New Prices screen (`app/ui/prices_view.py`) with a Wishlist / Browse All toggle — star any of the 35 catalog parts to track it
- `CATEGORY_ICONS` moved from `build_creator.py` to `ui/theme.py` so both screens share one source of truth
