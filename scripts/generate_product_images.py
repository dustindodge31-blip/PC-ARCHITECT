"""One-time (re-runnable) script: generates a stylized product image for every
part in app/data/parts_catalog.json using Gemini's image-generation model, and
saves them to app/assets/products/<part_id>.png.

These are AI-generated illustrations, not real photos of the actual SKUs --
good enough to replace flat category icons, not accurate enough to represent
a specific product's real appearance. Skips any part that already has an
image, so it's safe to re-run after adding new catalog parts.

Usage: python scripts/generate_product_images.py [--force]
"""
import base64
import json
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))

from core.env import ENV_PATH  # noqa: E402
import os  # noqa: E402

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
IMAGE_MODEL = "gemini-2.5-flash-image"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{IMAGE_MODEL}:generateContent"

CATALOG_PATH = ROOT / "app" / "data" / "parts_catalog.json"
OUTPUT_DIR = ROOT / "app" / "assets" / "products"

CATEGORY_STYLE = {
    "cpu": "a computer CPU processor chip, top-down view showing the metal integrated heat spreader",
    "motherboard": "a PC motherboard, top-down view showing the PCB, chipset, and expansion slots",
    "ram": "a pair of desktop RAM memory sticks with a low-profile heatsink",
    "gpu": "a desktop graphics card with a triple-fan cooler shroud, three-quarter angle",
    "storage": "a compact M.2 NVMe solid state drive stick",
    "psu": "a modular ATX power supply unit, front-facing with cable connectors visible",
    "case": "a mid-tower PC case with tempered glass side panel, three-quarter angle, closed",
    "cooler": "a CPU cooler (either a tower air cooler with fan, or an AIO liquid cooler radiator and pump)",
}

PROMPT_TEMPLATE = (
    "Professional studio product photo of {subject}. Clean, realistic, modern PC hardware "
    "aesthetic with black/dark grey styling and subtle RGB accent lighting. Centered, isolated "
    "on a plain transparent/white background, soft studio lighting, no text, no logos, no brand "
    "names, no watermark, no packaging, no hands."
)


def load_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def generate_image(category: str) -> bytes:
    prompt = PROMPT_TEMPLATE.format(subject=CATEGORY_STYLE[category])
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE"]},
    }
    response = httpx.post(API_URL, params={"key": GEMINI_API_KEY}, json=payload, timeout=60.0)
    response.raise_for_status()
    data = response.json()
    parts = data["candidates"][0]["content"]["parts"]
    for part in parts:
        inline = part.get("inlineData") or part.get("inline_data")
        if inline and inline.get("data"):
            return base64.b64decode(inline["data"])
    raise RuntimeError(f"No image data in response: {json.dumps(data)[:300]}")


def main():
    if not GEMINI_API_KEY:
        print("No GEMINI_API_KEY found (check .env). Aborting.")
        sys.exit(1)

    force = "--force" in sys.argv
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    catalog = load_catalog()

    total = sum(len(parts) for parts in catalog.values())
    done = 0
    for category, parts in catalog.items():
        for part in parts:
            done += 1
            out_path = OUTPUT_DIR / f"{part['id']}.png"
            if out_path.exists() and not force:
                print(f"[{done}/{total}] skip (exists): {part['id']}")
                continue
            print(f"[{done}/{total}] generating: {part['id']} ({part['name']})...")
            try:
                image_bytes = generate_image(category)
                out_path.write_bytes(image_bytes)
                print(f"  saved {out_path.name} ({len(image_bytes)} bytes)")
            except Exception as e:
                print(f"  FAILED: {e}")
            time.sleep(1.0)  # be polite to the API

    print("Done.")


if __name__ == "__main__":
    main()
