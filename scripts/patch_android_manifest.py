"""Re-applies the Android cleartext-traffic fix after a fresh `flet build apk`
scaffold or `flet clean`. Not needed on ordinary rebuilds -- Flet's build
process only touches its own marked template sections, so this edit survives
those. Only needed if app/build/flutter/ gets wiped and regenerated fresh.

Why this exists: the in-app 3D Workbench viewer (Epic 9) serves its assets
over a local http://127.0.0.1 server (see app/core/asset_server.py) so the
WebView can use fetch()/XHR for the glTF model -- file:// URLs block those via
CORS. Android blocks plain HTTP ("cleartext") network traffic by default,
even to localhost, so the WebView fails to load with net::ERR_CLEARTEXT_NOT_PERMITTED
unless the app's manifest explicitly opts in.

Usage: python scripts/patch_android_manifest.py <path-to-cloned-repo>
(run after `flet build apk` has scaffolded app/build/flutter/ at least once)
"""
import sys
from pathlib import Path

MANIFEST_RELATIVE_PATH = "app/build/flutter/android/app/src/main/AndroidManifest.xml"
OLD = '        android:icon="@mipmap/ic_launcher">'
NEW = '        android:usesCleartextTraffic="true"\n        android:icon="@mipmap/ic_launcher">'


def main():
    repo_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    manifest_path = repo_root / MANIFEST_RELATIVE_PATH

    if not manifest_path.exists():
        print(f"Not found: {manifest_path}\nRun `flet build apk app` at least once first to scaffold it.")
        sys.exit(1)

    text = manifest_path.read_text(encoding="utf-8")
    if "usesCleartextTraffic" in text:
        print("Already patched.")
        return
    if OLD not in text:
        print("Expected manifest text not found -- Flet's template may have changed. Patch manually.")
        sys.exit(1)

    manifest_path.write_text(text.replace(OLD, NEW), encoding="utf-8")
    print(f"Patched {manifest_path}")


if __name__ == "__main__":
    main()
