"""AI Architect: Gemini picks real catalog part IDs from a natural-language
request; our own compatibility/scoring engines compute everything else.
Gemini never invents specs, prices, or performance numbers.

The actual Gemini call happens server-side in the gemini-proxy Supabase Edge
Function (see supabase/functions/gemini-proxy/) -- the API key never ships
inside the app bundle, and the proxy enforces a real per-user daily cap that
can't be bypassed by extracting a client-side key. This means AI Architect
now requires being signed in; see community.current_access_token()."""
import json
import os
from dataclasses import dataclass, field

import httpx

from core import catalog, community
from core.env import ENV_PATH  # noqa: F401 -- imported for its load_dotenv() side effect

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
PROXY_URL = f"{SUPABASE_URL}/functions/v1/gemini-proxy" if SUPABASE_URL else None

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
    if not PROXY_URL or not SUPABASE_ANON_KEY:
        raise AIArchitectError(
            "AI Architect isn't configured yet. Add SUPABASE_URL and SUPABASE_ANON_KEY to .env."
        )

    try:
        access_token = community.current_access_token()
    except community.CommunityError as ex:
        raise AIArchitectError(str(ex)) from ex
    if not access_token:
        raise AIArchitectError("Sign in from your Profile to use AI Architect.")

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
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": SUPABASE_ANON_KEY,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(PROXY_URL, headers=headers, json=payload)
    except httpx.RequestError as e:
        raise AIArchitectError(f"Couldn't reach AI Architect: {e}") from e

    if response.status_code == 401:
        raise AIArchitectError("Sign in from your Profile to use AI Architect.")
    if response.status_code == 429:
        try:
            raise AIArchitectError(response.json().get("error", "Daily AI Architect limit reached."))
        except (json.JSONDecodeError, ValueError):
            raise AIArchitectError("Daily AI Architect limit reached. Try again tomorrow.")
    if response.status_code != 200:
        raise AIArchitectError(f"AI Architect request failed ({response.status_code}): {response.text[:200]}")

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
