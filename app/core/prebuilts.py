"""Hand-curated starter builds for the Home dashboard's category shortcuts.

Unlike AI Architect (which picks parts via Gemini per a free-text request),
these are fixed, deterministic picks -- tapping "Gaming" always loads the
same starting point, which the user can then tweak in Build Creator.
"""
from core import catalog

PREBUILDS = {
    "gaming": {
        "name": "Gaming Starter Build",
        "blurb": "A balanced gaming pick: a strong gaming CPU, a capable 1440p GPU, and room to grow. Swap any part to make it yours.",
        "parts": {
            "cpu": "cpu-7800x3d",
            "motherboard": "mb-b650",
            "ram": "ram-32-6000",
            "gpu": "gpu-4070super",
            "storage": "ssd-1tb-nvme",
            "psu": "psu-850",
            "case": "case-4000d",
            "cooler": "cool-aio240",
        },
    },
    "creator": {
        "name": "Creator Starter Build",
        "blurb": "Tuned for video editing and rendering: more cores, more RAM, more storage. Swap any part to make it yours.",
        "parts": {
            "cpu": "cpu-14700k",
            "motherboard": "mb-z790",
            "ram": "ram-64-6000",
            "gpu": "gpu-4070super",
            "storage": "ssd-2tb-nvme",
            "psu": "psu-850",
            "case": "case-o11",
            "cooler": "cool-nh-d15",
        },
    },
    "ai_workstation": {
        "name": "AI / Workstation Starter Build",
        "blurb": "Maxed on VRAM and memory for AI/ML workloads and heavy multitasking. Swap any part to make it yours.",
        "parts": {
            "cpu": "cpu-245k",
            "motherboard": "mb-z890",
            "ram": "ram-64-6000",
            "gpu": "gpu-4090",
            "storage": "ssd-2tb-nvme",
            "psu": "psu-1000",
            "case": "case-o11",
            "cooler": "cool-aio360",
        },
    },
    "office": {
        "name": "Office Starter Build",
        "blurb": "A quiet, budget-friendly build for everyday work and browsing. Swap any part to make it yours.",
        "parts": {
            "cpu": "cpu-7600x",
            "motherboard": "mb-b650m",
            "ram": "ram-16-6000",
            "gpu": "gpu-4060",
            "storage": "ssd-500gb-sata",
            "psu": "psu-550",
            "case": "case-4000d",
            "cooler": "cool-hyper212",
        },
    },
}


def get_prebuilt(key: str) -> tuple[str, str, dict] | None:
    """Returns (name, blurb, parts) with part IDs resolved to full catalog
    dicts, or None if there's no prebuilt for this key (e.g. "Custom")."""
    spec = PREBUILDS.get(key)
    if not spec:
        return None
    parts = {cat: catalog.find_part(cat, pid) for cat, pid in spec["parts"].items()}
    return spec["name"], spec["blurb"], parts
