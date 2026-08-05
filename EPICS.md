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
| Epic 7 — Community & Cloud Sync | Phase 5 | ✅ Done |
| Epic 8 — Workbench (stylized 2D) | Phase 7 | ✅ Done (2D, not real 3D/AR — see notes) |
| Epic 9 — Real 3D Workbench / AR Mode | Phase 7 (deferred) | 🚧 In progress — single-model proof of concept working, see notes |

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

## Epic 7 — Community & Cloud Sync ✅
- Real backend: Supabase (Postgres + auth), scoped to auth + publish/browse + favorite for v1 (comments/following/contests deferred)
- Schema in `supabase_schema.sql` (run by the user in their Supabase SQL Editor): `community_builds` + `favorites` tables, RLS so anyone can read the public feed but only the owner can publish/favorite as themselves
- `app/core/community.py`: sign up/in/out, publish a local build, list the feed with favorite counts, toggle favorite — all against the real project
- `app/core/community_session.py`: persists the Supabase session locally (gitignored) so login survives app restarts
- `app/ui/community_view.py` (new) and `app/ui/profile_view.py` (now a stateful `ProfileView` with an auth section) — reached from Profile's "Browse Community" button, no dedicated nav tab (same pattern as My Builds/Performance)
- Credentials in `.env` as `SUPABASE_URL` / `SUPABASE_ANON_KEY` (the anon/publishable key — safe for client apps, respects RLS); verified end-to-end against the live project (sign-up, publish, feed, favorite toggle) before shipping

## Epic 8 — Workbench (stylized 2D) ✅
- Flet has no 3D engine, model loader, or AR/camera integration, and the original vision doc itself labels real 3D Workbench / AR Mode as "Future" — confirmed with the user to build a stylized 2D visualization instead, not real 3D.
- New fourth tab ("Workbench") in Build Creator, alongside Overview/Parts/Performance: a case outline with a live "X/8 components selected" count, and a tappable node per category showing filled (accent-colored, part name) or empty (muted, "Not selected") state. Tapping a node jumps to the Parts tab.
- Pure presentation over the existing `self.selected` build state — no new core/ module.
- Real 3D/AR remains a legitimate future project if ever pursued (would need an embedded WebView + Three.js + sourced 3D model assets), but is out of scope here.

## Epic 9 — Real 3D Workbench / AR Mode 🚧 (proof of concept)
- **Platform limitation discovered**: `flet_webview` (separate pip package from core `flet`) explicitly does not support Windows desktop — only Android, iOS, and macOS. On Windows it renders a graceful "Webview is not yet supported on this Platform" placeholder rather than crashing, but the actual 3D content can't be verified on this dev machine; needs testing on an Android/macOS build to confirm the real render.
- **CORS on `file://`**: browsers/WebViews block `fetch()`/XHR (used by the glTF loader) under `file://` origins. Fixed by `app/core/asset_server.py`, a tiny local `http.server` thread that serves `app/assets/` — the WebView loads `http://127.0.0.1:<port>/case_viewer.html` instead of a file path, which works identically across platforms.
- User sourced a Sketchfab Standard-licensed glTF PC case model (`app/assets/models/pc_case/`) — license explicitly permits commercial use and derivative works; credited in-viewer.
- `app/assets/case_viewer.html`: self-contained Three.js scene (classic non-module build for maximum WebView compatibility, `app/assets/vendor/three/`) with `GLTFLoader`, `OrbitControls` (drag-rotate, scroll-zoom, auto-rotate), and a light rig tuned for PBR metal materials without a full HDRI environment (capped metalness, ACES tone mapping).
- **Verified without relying on the unsupported Windows WebView**: installed Playwright + headless Chromium to load `case_viewer.html` directly over the local HTTP server and screenshot the actual Three.js output — confirmed the model loads and renders correctly (case geometry, vents, cable detail, lighting) independent of Flet's WebView wrapper.
- Wired into Build Creator's Workbench tab (`app/ui/build_creator.py`), replacing the flat case icon from Epic 8.
- Still single-model proof of concept — no parts-swapping, no additional component models. Next step (if pursued further) is testing on a real Android/macOS build to confirm the in-app embedding actually renders, not just the standalone browser test.
