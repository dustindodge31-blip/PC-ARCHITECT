# PC Architect — Epic Backlog

Tracks implementation work as Epics mapped to the original Master Vision Document's phased roadmap. One epic at a time; each completed epic is committed and pushed to GitHub.

| Epic | Maps to handoff phase | Status |
|---|---|---|
| Epic 1 — Foundation & Desktop Test Harness | Phase 1 | ✅ Done |
| Epic 2 — Visual Identity & Home Dashboard | Phase 1 (UI) | 🚧 In progress |
| Epic 3 — Build Creator Redesign + Build Score Engine | Phase 2 + Phase 4 (scoring) | Backlog |
| Epic 4 — AI Architect | Phase 3 | Backlog (needs LLM integration decision) |
| Epic 5 — Performance Estimators (FPS, bottleneck analysis) | Phase 4 | Backlog |
| Epic 6 — Price Tracking | Phase 6 | Backlog |
| Epic 7 — Community & Cloud Sync | Phase 5 | Backlog |
| Epic 8 — 3D Workbench / AR | Phase 7 | Backlog |

## Epic 1 — Foundation & Desktop Test Harness ✅
- Parts catalog (`app/core/catalog.py`, `app/data/parts_catalog.json`)
- Live compatibility engine (`app/core/compatibility.py`)
- SQLite build storage (`app/core/storage.py`)
- Flet phone-frame desktop test shell: phone-sized frameless window, status bar, notch, home indicator, draggable, remembers position (`app/main.py`, `app/ui/phone_frame.py`, `app/core/window_state.py`)
- Git repo wired to GitHub remote

## Epic 2 — Visual Identity & Home Dashboard 🚧
- Swappable accent-theme system (infrastructure; one theme active for now)
- Redesigned Home dashboard: greeting, AI Architect entry card, category quick-filters, My Builds cards with provisional score badges
- 5-item bottom nav: Home, Builds, AI, Prices, Profile (AI/Prices stubbed)
