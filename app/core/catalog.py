"""Loads the parts catalog from the seed JSON file."""
import json
from pathlib import Path
from functools import lru_cache

CATALOG_PATH = Path(__file__).resolve().parent.parent / "data" / "parts_catalog.json"

CATEGORIES = ["cpu", "motherboard", "ram", "gpu", "storage", "psu", "case", "cooler"]

CATEGORY_LABELS = {
    "cpu": "CPU",
    "motherboard": "Motherboard",
    "ram": "RAM",
    "gpu": "Graphics Card",
    "storage": "Storage",
    "psu": "Power Supply",
    "case": "Case",
    "cooler": "CPU Cooler",
}


@lru_cache(maxsize=1)
def load_catalog() -> dict:
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def parts_for(category: str) -> list[dict]:
    return load_catalog().get(category, [])


def find_part(category: str, part_id: str) -> dict | None:
    for part in parts_for(category):
        if part["id"] == part_id:
            return part
    return None
