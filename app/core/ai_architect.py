"""AI Architect: Gemini picks real catalog part IDs from a natural-language
request; our own compatibility/scoring engines compute everything else.
Gemini never invents specs, prices, or performance numbers."""
import json
import os
from dataclasses import dataclass, field

import httpx

from core import catalog
from core.env import ENV_PATH  # noqa: F401 -- imported for its load_dotenv() side effect

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

SYSTEM_INSTRUCTIONS = """You are the AI Architect inside PC Architect, a PC-building app. \
A user will describe what they want (budget, use case, games, workloads, aesthetic, etc). \
Choose exactly one part ID per category below from the AVAILABLE PARTS catalog that best fits \
their request, and briefly explain your reasoning (2-4 sentences, plain language, no markdown). \
You must only use part IDs that appear in the catalog below — never invent an ID, spec, or price."""


class AIArchitectError(Exception):
    """Raised with a user-facing message; UI should show e.args[0] directly."""


@dataclass
class AIBuildResult:
    name: str
    reasoning: str
    selection: dict[str, dict | None]
    warnings: list[str] = field(default_factory=list)


def _catalog_summary() -> str:
    sections = []
    for cat in catalog.CATEGORIES:
        parts = catalog.parts_for(cat)
        sections.append(f"{cat.upper()} options:\n" + json.dumps(parts, separators=(",", ":")))
    return "\n\n".join(sections)


def _response_schema() -> dict:
    return {
        "type": "OBJECT",
        "properties": {
            "build_name": {"type": "STRING"},
            "reasoning": {"type": "STRING"},
            "selection": {
                "type": "OBJECT",
                "properties": {
                    cat: {"type": "STRING", "enum": [p["id"] for p in catalog.parts_for(cat)]}
                    for cat in catalog.CATEGORIES
                },
                "required": catalog.CATEGORIES,
            },
        },
        "required": ["build_name", "reasoning", "selection"],
    }


async def generate_build(prompt: str) -> AIBuildResult:
    if not GEMINI_API_KEY:
        raise AIArchitectError(
            "No Gemini API key configured. Add GEMINI_API_KEY to the project's .env file."
        )

    payload = {
        "systemInstruction": {
            "parts": [{"text": SYSTEM_INSTRUCTIONS + "\n\nAVAILABLE PARTS:\n" + _catalog_summary()}]
        },
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": _response_schema(),
        },
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(API_URL, params={"key": GEMINI_API_KEY}, json=payload)
    except httpx.RequestError as e:
        raise AIArchitectError(f"Couldn't reach Gemini: {e}") from e

    if response.status_code in (401, 403):
        raise AIArchitectError(
            "Gemini rejected the API key (unauthorized). Get a valid key from Google AI Studio "
            "and update GEMINI_API_KEY in .env."
        )
    if response.status_code != 200:
        raise AIArchitectError(f"Gemini request failed ({response.status_code}): {response.text[:200]}")

    try:
        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(text)
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        raise AIArchitectError(f"Couldn't parse Gemini's response: {e}") from e

    warnings: list[str] = []
    selection: dict[str, dict | None] = {}
    for cat in catalog.CATEGORIES:
        part_id = parsed.get("selection", {}).get(cat)
        part = catalog.find_part(cat, part_id) if part_id else None
        if part_id and not part:
            warnings.append(f"Gemini picked an unknown {cat} part ID ({part_id}); left unset.")
        selection[cat] = part

    return AIBuildResult(
        name=parsed.get("build_name") or "AI Build",
        reasoning=parsed.get("reasoning", ""),
        selection=selection,
        warnings=warnings,
    )
