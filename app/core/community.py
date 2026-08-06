"""Supabase-backed community: auth, publishing builds, browsing the public
feed, and favoriting. Requires SUPABASE_URL / SUPABASE_ANON_KEY in .env —
see supabase_schema.sql for the tables this expects."""
import json
import os
from dataclasses import dataclass, field

from supabase import create_client

from core import community_session
from core.env import ENV_PATH  # noqa: F401 -- imported for its load_dotenv() side effect

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

_client = None


class CommunityError(Exception):
    """Raised with a user-facing message; UI should show e.args[0] directly."""


def _get_client():
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_ANON_KEY:
            raise CommunityError(
                "Community isn't configured yet. Add SUPABASE_URL and SUPABASE_ANON_KEY to .env."
            )
        _client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        tokens = community_session.load_tokens()
        if tokens:
            try:
                _client.auth.set_session(tokens[0], tokens[1])
            except Exception:
                community_session.clear_tokens()
    return _client


def _friendly_auth_error(e: Exception) -> str:
    message = str(e)
    if "Invalid login credentials" in message:
        return "Incorrect email or password."
    if "already registered" in message.lower() or "already exists" in message.lower():
        return "An account with that email already exists — try logging in instead."
    if "Password should be" in message:
        return "Password is too short (Supabase requires at least 6 characters)."
    return f"Community request failed: {message}"


@dataclass
class CommunityBuild:
    id: str
    name: str
    author_name: str
    price: float
    overall_score: int
    parts: dict
    favorite_count: int
    favorited_by_me: bool
    owned_by_me: bool


def current_user():
    client = _get_client()
    session = client.auth.get_session()
    return session.user if session else None


def sign_up(email: str, password: str) -> None:
    client = _get_client()
    try:
        response = client.auth.sign_up({"email": email, "password": password})
    except Exception as e:
        raise CommunityError(_friendly_auth_error(e)) from e
    if response.session:
        community_session.save_tokens(response.session.access_token, response.session.refresh_token)


def sign_in(email: str, password: str) -> None:
    client = _get_client()
    try:
        response = client.auth.sign_in_with_password({"email": email, "password": password})
    except Exception as e:
        raise CommunityError(_friendly_auth_error(e)) from e
    if response.session:
        community_session.save_tokens(response.session.access_token, response.session.refresh_token)


def sign_out() -> None:
    client = _get_client()
    try:
        client.auth.sign_out()
    except Exception:
        pass
    community_session.clear_tokens()


def publish_build(name: str, parts: dict, total_price: float, overall_score: int, author_name: str) -> None:
    client = _get_client()
    user = current_user()
    if not user:
        raise CommunityError("Sign in before publishing a build.")

    selection_ids = {cat: (p["id"] if p else None) for cat, p in parts.items()}
    try:
        client.table("community_builds").insert({
            "user_id": user.id,
            "author_name": author_name,
            "name": name,
            "parts_json": json.dumps(selection_ids),
            "price": total_price,
            "overall_score": overall_score,
        }).execute()
    except Exception as e:
        raise CommunityError(f"Couldn't publish: {e}") from e


def list_community_builds() -> list[CommunityBuild]:
    from core import catalog

    client = _get_client()
    user = current_user()

    try:
        builds_resp = client.table("community_builds").select("*").order("created_at", desc=True).execute()
        favorites_resp = client.table("favorites").select("build_id, user_id").execute()
    except Exception as e:
        raise CommunityError(f"Couldn't load the community feed: {e}") from e

    favorite_rows = favorites_resp.data or []
    counts: dict[str, int] = {}
    my_favorites: set[str] = set()
    for row in favorite_rows:
        counts[row["build_id"]] = counts.get(row["build_id"], 0) + 1
        if user and row["user_id"] == user.id:
            my_favorites.add(row["build_id"])

    results = []
    for row in builds_resp.data or []:
        selection_ids = json.loads(row["parts_json"])
        parts = {cat: (catalog.find_part(cat, pid) if pid else None) for cat, pid in selection_ids.items()}
        results.append(CommunityBuild(
            id=row["id"],
            name=row["name"],
            author_name=row["author_name"],
            price=row["price"],
            overall_score=row["overall_score"],
            parts=parts,
            favorite_count=counts.get(row["id"], 0),
            favorited_by_me=row["id"] in my_favorites,
            owned_by_me=bool(user and row["user_id"] == user.id),
        ))
    return results


def delete_community_build(build_id: str) -> None:
    client = _get_client()
    user = current_user()
    if not user:
        raise CommunityError("Sign in before deleting a build.")

    try:
        client.table("community_builds").delete().eq("id", build_id).eq("user_id", user.id).execute()
    except Exception as e:
        raise CommunityError(f"Couldn't delete: {e}") from e


def toggle_favorite(build_id: str, currently_favorited: bool) -> None:
    client = _get_client()
    user = current_user()
    if not user:
        raise CommunityError("Sign in before favoriting a build.")

    try:
        if currently_favorited:
            client.table("favorites").delete().eq("user_id", user.id).eq("build_id", build_id).execute()
        else:
            client.table("favorites").insert({"user_id": user.id, "build_id": build_id}).execute()
    except Exception as e:
        raise CommunityError(f"Couldn't update favorite: {e}") from e
