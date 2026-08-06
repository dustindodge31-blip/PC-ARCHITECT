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
| Epic 9 — Real 3D Workbench / AR Mode | Phase 7 (deferred) | ✅ Done — confirmed working on a real Android device, see notes |

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

## Epic 9 — Real 3D Workbench / AR Mode ✅
- **Platform limitation discovered**: `flet_webview` (separate pip package from core `flet`) explicitly does not support Windows desktop — only Android, iOS, and macOS. On Windows it renders a graceful "Webview is not yet supported on this Platform" placeholder rather than crashing, but the actual 3D content can't be verified on this dev machine; needs testing on an Android/macOS build to confirm the real render.
- **CORS on `file://`**: browsers/WebViews block `fetch()`/XHR (used by the glTF loader) under `file://` origins. Fixed by `app/core/asset_server.py`, a tiny local `http.server` thread that serves `app/assets/` — the WebView loads `http://127.0.0.1:<port>/case_viewer.html` instead of a file path, which works identically across platforms.
- User sourced a Sketchfab Standard-licensed glTF PC case model (`app/assets/models/pc_case/`) — license explicitly permits commercial use and derivative works; credited in-viewer.
- `app/assets/case_viewer.html`: self-contained Three.js scene (classic non-module build for maximum WebView compatibility, `app/assets/vendor/three/`) with `GLTFLoader`, `OrbitControls` (drag-rotate, scroll-zoom, auto-rotate), and a light rig tuned for PBR metal materials without a full HDRI environment (capped metalness, ACES tone mapping).
- **Verified without relying on the unsupported Windows WebView**: installed Playwright + headless Chromium to load `case_viewer.html` directly over the local HTTP server and screenshot the actual Three.js output — confirmed the model loads and renders correctly (case geometry, vents, cable detail, lighting) independent of Flet's WebView wrapper.
- Wired into Build Creator's Workbench tab (`app/ui/build_creator.py`), replacing the flat case icon from Epic 8.
- **Confirmed working on a real Android device** — first-ever Android build of this app. Getting there required setting up the full Android toolchain from scratch (JDK 17, Android SDK cmdline-tools + platform 34/build-tools, Flutter SDK) and fixing three real, non-obvious bugs along the way:
  1. **Missing dependencies in the package**: `flet build apk` only looks for `requirements.txt` inside the app path being built (`app/`), not the project root where it actually lived — `supabase`/`python-dotenv`/`flet-webview` were silently omitted from every build. Fixed by keeping a copy at `app/requirements.txt` (must stay in sync with the root one).
  2. **Gradle wrapper breaks on `&` in the folder path**: the project's own path (`...\IvyTech & Cert Courses\...`) crashed Gradle's batch-based build wrapper (`'Cert' is not recognized...`) — a classic Windows cmd.exe metacharacter issue. Worked around by building from a clean clone at `C:\dev\pc_architect` instead of trying to patch Gradle's path handling.
  3. **Crash on launch**: `page.window.center()` and the other desktop window-management calls (size/position/frameless/dragging) don't exist on a real phone and hung for the full RPC timeout before crashing. Fixed in `app/main.py` by checking `page.platform` and skipping all `page.window.*` calls and the fake phone-frame bezel (`wrap_in_phone_frame`) on Android/iOS — the real device already has its own chrome.
  4. **`net::ERR_CLEARTEXT_NOT_PERMITTED`**: Android blocks plain HTTP by default, even to `127.0.0.1`, so the WebView couldn't reach the local asset server. Fixed with `android:usesCleartextTraffic="true"` in the generated `AndroidManifest.xml`; `scripts/patch_android_manifest.py` re-applies this if the build scaffold ever gets wiped (`flet clean` or a fresh clone) since it's not exposed as a `flet build` CLI flag.
- **The model still rendered blank on-device after all of the above** — three more root causes, found the hard way since none of them produced an error message:
  1. **`flet build apk` was silently crashing, every time, for hours**: a Windows-console `UnicodeEncodeError` (cp1252 can't encode a `✅` emoji `rich` tries to print) killed the build immediately after the JDK-config step, before Python packaging ever ran. Because the command was piped through `tail`, the pipeline's exit code reflected `tail` (0), not the real failure — every "Successfully" report was stale, and every reinstalled APK was byte-identical to the very first build. Confirmed by diffing `app.zip`'s contents/timestamp inside the built APK against the source. Fixed by exporting `PYTHONUTF8=1` / `PYTHONIOENCODING=utf-8` before invoking `flet build apk`, and by checking the real exit code (not piping through `tail`) from then on.
  2. **The WebView cached a stale copy of `case_viewer.html`** once real rebuilds started landing: the local asset server's ephemeral port got reused across app launches, and unlabeled HTTP responses let the WebView silently serve a `304`/cached body instead of fetching the new file — so code changes still didn't appear to do anything even once the build pipeline was fixed. Fixed by having `asset_server.py` send `Cache-Control: no-store`, strip incoming conditional-request headers, and cache-bust the entry URL with a `?v=<timestamp>` query param.
  3. **JavaScript was never executing in the WebView**: `flet_webview`'s `WebView` control doesn't enable JS by default; it must be turned on explicitly via `await webview.set_javascript_mode(JavaScriptMode.UNRESTRICTED)`, called once the control is mounted (`did_mount()` + `page.run_task(...)`, since `did_mount` itself isn't awaited). Without this, the page loaded and fired `on_page_started`/`on_page_ended` normally but silently never ran any script, including Three.js. Isolated with a minimal red→green static/JS test page before touching the real 3D code again.
  Also worth noting for future on-device debugging: the app process survives `adb install -r`, so a reinstalled APK can keep running old in-memory code until it's explicitly force-stopped (`adb shell am force-stop <package>`) — several "still broken" results during this investigation were actually stale processes, not stale builds.
- **Model went blank again after switching tabs and back**: Android's WebView doesn't reliably repaint its native rendering surface after its container is hidden/shown via simple visibility toggling (how the four Build Creator tabs switch) — calling `.reload()` on the existing control wasn't enough. Fixed by fully recreating the `WebView` control (new instance, fresh cache-busted URL, re-enabling JS mode) every time the Workbench tab is re-entered, forcing Android to dispose and rebuild the native view instead of reusing a broken surface.
- **Side quest, found while poking at the finished Workbench**: the AI Architect tab showed "No Gemini API key configured" on Android even though `.env` has a real key — Community/Supabase sign-in had the identical latent bug. Root cause: `ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"` in both `ai_architect.py` and `community.py` assumed the dev layout (`app/core/x.py` → three parents up to the project root), but `flet build apk` packages everything under `app/` as the bundle root, so on-device the same file sits at `core/x.py` and three parents up overshoots past anywhere `.env` could live. Fixed by centralizing resolution in `app/core/env.py`, which tries both the dev path and the packaged path; a copy of `.env` now lives at `app/.env` (gitignored, kept in sync manually, same pattern as `app/requirements.txt`) so it's actually inside the bundle to be found.
- Single-model proof of concept — no parts-swapping, no additional component models yet.

## Post-launch hardening (Sentry, Gemini rate limit, Community moderation, prebuilt shortcuts)
- **`flet build apk`/`aab` silently ignored a new dependency (`sentry-sdk`) added to `requirements.txt`**: `flet_cli`'s `build_base.py` only feeds `requirements.txt`'s contents into its change-detection hash when verbosity is `-vv` (`if self.verbose > 1: ... hash.update(reqs_txt_contents)`) — every build in this project up to this point used single `-v`, so adding a new package never registered as a change, and the build kept reusing a stale cached `site-packages` that predated it. The app then crashed on-device with `ModuleNotFoundError: No module named 'sentry_sdk'` despite it being correctly listed in `requirements.txt` and installed locally. **Always build with `-vv`, not `-v`, from now on** — confirmed via inspecting `sitepackages.zip` inside the built artifact directly (`unzip -l` on the APK's bundled `assets/sitepackages.zip`) rather than trusting the "Successfully built" message alone.
- Switching from `-v` to `-vv` on a build whose site-packages cache was already stale triggered a second, unrelated failure: partially-cleared caches ended up in an inconsistent state (`flet_webview` referenced as a local path dependency at `app/build/flutter-packages/flet_webview`, which didn't exist because a prior `--skip-site-packages` run had never populated it). Fixed by wiping `app/build/` entirely and doing one full clean rebuild, then re-applying the `AndroidManifest.xml` cleartext-traffic patch (wiped by the clean scaffold, as expected) and rebuilding once more.
- Added `app/core/ai_rate_limit.py`: a local per-device daily cap on AI Architect calls (default 15/day, `AI_ARCHITECT_DAILY_LIMIT` env override). This is a client-side guard against accidental overuse through the app's own UI, not a real security boundary — the Gemini key ships inside the app bundle and could in principle be extracted and used directly. A proper fix would proxy Gemini calls through a server holding the key (e.g. a Supabase Edge Function enforcing limits per authenticated user); noted as a follow-up, not yet done.
- Added a `reports` table + RLS policy to `supabase_schema.sql` and a report-build action in the Community feed (`community.report_build`, flag icon on other users' cards) — reports aren't surfaced anywhere in-app by design; check them via the Supabase Table Editor directly.
- Added in-app delete for a user's own published community builds (`community.delete_community_build`, trash icon on your own cards) — the privacy policy previously (incorrectly) claimed this already existed; now it's actually true.
- Added `app/core/prebuilts.py`: the Home dashboard's Gaming/Creator/AI-Workstation/Office category buttons previously all did the exact same thing (opened an empty Build Creator) — they now load a hand-curated starter build per category via the same `load_from_parts()` path AI Architect results use. "Custom" still opens empty, unchanged.
- Added a "prices are simulated" disclaimer to the Prices tab — the price history was always a deterministic random walk, not real retail data, and wasn't previously labeled as such.
- Added Sentry crash reporting (`SENTRY_DSN` in `.env`, initialized in `main.py` after the existing local `crash_log.txt` `sys.excepthook` so both fire on every uncaught exception — verified end-to-end with a forced test exception, not just by absence of errors at startup).
- **Moved the Gemini API key server-side**, closing the gap `ai_rate_limit.py` explicitly flagged as unsolved: added a `supabase/functions/gemini-proxy` Edge Function (Deno/TypeScript) that holds `GEMINI_API_KEY` as a Supabase secret and is the only thing that ever calls Gemini now — the key no longer ships inside the app bundle at all (confirmed by inspecting the built APK's bundled `.env` directly). This required AI Architect to start requiring sign-in (a real, deliberate UX change, confirmed with the user first): the proxy verifies the caller's Supabase JWT and enforces a genuine per-user daily cap (15/day) via a new `ai_usage` table, which can't be bypassed the way a client-side cap could. `app/core/ai_rate_limit.py` was deleted (superseded); `ai_architect.py` now calls the proxy via `community.current_access_token()` instead of Gemini directly.
  - **Real bug caught in the proxy's own first version, before it shipped**: the usage-check and usage-increment Supabase queries didn't check their `error` return value, so if the `ai_usage` table was ever missing or misconfigured, the function would silently treat it as "0 requests used" and let every request through unlimited — the exact opposite of what it's for. Caught by deliberately testing against the project *before* running the table-creation SQL (confirmed via a direct `GET /rest/v1/ai_usage` call returning 404) rather than assuming a 200 from Gemini meant the whole chain was correct. Fixed to fail closed (block with a clear 500 error) instead of failing open, redeployed, and reverified the same way.
  - Supabase CLI auth in this environment needed a personal access token (`supabase login`'s interactive browser flow doesn't work in a non-TTY shell) — generated once at supabase.com/dashboard/account/tokens, passed via `SUPABASE_ACCESS_TOKEN` env var for `link`/`secrets set`/`functions deploy`.
  - Privacy policy and the Data Safety form reference doc both updated to reflect: AI Architect now requires an account, prompts are relayed through the Supabase proxy rather than going directly to Google, and Sentry crash reporting (added earlier in this same hardening pass) was never actually disclosed in either document until now.
