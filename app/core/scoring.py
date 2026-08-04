"""Multi-axis Build Score engine.

Heuristic, computed from the spec attributes already in parts_catalog.json
(cores/threads, VRAM, TDP, RAM capacity, storage type, cooler headroom/noise).
There's no real benchmark data source wired up, so these are relative
estimates, not measured FPS/render numbers — good enough to compare builds
against each other, not to promise real-world performance.
"""
from core import compatibility

AXES = ("gaming", "creator", "productivity", "cooling", "noise", "value")

AXIS_LABELS = {
    "gaming": "Gaming",
    "creator": "Creator",
    "productivity": "Productivity",
    "cooling": "Cooling",
    "noise": "Noise",
    "value": "Value",
}

_OVERALL_WEIGHTS = {
    "gaming": 0.25,
    "creator": 0.2,
    "productivity": 0.2,
    "cooling": 0.15,
    "noise": 0.1,
    "value": 0.1,
}

_ISSUE_PENALTY = {"error": 15, "warning": 5}


def _clamp(value: float) -> int:
    return max(0, min(100, round(value)))


def _issue_penalty(parts: dict) -> float:
    issues = compatibility.check_build(parts)
    return sum(_ISSUE_PENALTY.get(issue.level, 0) for issue in issues)


def gpu_gaming_index(gpu: dict | None) -> int:
    """0-100 relative gaming capability of a GPU alone, used by both the Gaming
    axis score and the Performance tab's FPS estimator (core/performance.py)."""
    if not gpu:
        return 0
    return _clamp(min(100, gpu["vram_gb"] * 4 + gpu["tdp_w"] * 0.15))


def cpu_gaming_index(cpu: dict | None) -> int:
    """0-100 relative gaming capability of a CPU alone (see gpu_gaming_index)."""
    if not cpu:
        return 0
    return _clamp(min(100, cpu["cores"] * 6))


def score_gaming(parts: dict) -> int:
    gpu, cpu = parts.get("gpu"), parts.get("cpu")
    if not gpu and not cpu:
        return 0
    score = gpu_gaming_index(gpu) * 0.7 + cpu_gaming_index(cpu) * 0.3
    return _clamp(score - _issue_penalty(parts))


def score_creator(parts: dict) -> int:
    cpu, gpu, ram = parts.get("cpu"), parts.get("gpu"), parts.get("ram")
    if not any((cpu, gpu, ram)):
        return 0
    cpu_score = min(100, cpu["threads"] * 3.5) if cpu else 0
    gpu_score = min(100, gpu["vram_gb"] * 4) if gpu else 0
    ram_score = min(100, ram["capacity_gb"] * 1.5) if ram else 0
    score = cpu_score * 0.4 + gpu_score * 0.3 + ram_score * 0.3
    return _clamp(score - _issue_penalty(parts))


def score_productivity(parts: dict) -> int:
    cpu, ram, storage = parts.get("cpu"), parts.get("ram"), parts.get("storage")
    if not any((cpu, ram, storage)):
        return 0
    cpu_score = min(100, cpu["cores"] * 6) if cpu else 0
    ram_score = min(100, ram["capacity_gb"] * 1.5) if ram else 0
    storage_score = (100 if storage["type"] == "NVMe" else 60) if storage else 0
    score = cpu_score * 0.4 + ram_score * 0.3 + storage_score * 0.3
    return _clamp(score - _issue_penalty(parts))


def score_cooling(parts: dict) -> int:
    cpu, cooler = parts.get("cpu"), parts.get("cooler")
    if not cooler:
        return 0
    if not cpu:
        return _clamp(60)
    headroom = cooler["max_tdp_w"] / max(cpu["tdp_w"], 1)
    score = min(100, headroom * 80)
    return _clamp(score - _issue_penalty(parts))


def score_noise(parts: dict) -> int:
    cooler = parts.get("cooler")
    if not cooler:
        return 0
    return _clamp(cooler.get("noise_rating", 60))


def score_value(parts: dict, total_price: float) -> int:
    if total_price <= 0:
        return 0
    perf = (score_gaming(parts) + score_creator(parts) + score_productivity(parts)) / 3
    # Rough reference: ~$15 spent per point of average performance is "fair value".
    expected_price = perf * 15
    if expected_price <= 0:
        return 0
    ratio = expected_price / total_price
    return _clamp(50 * ratio)


def score_build(parts: dict, total_price: float) -> dict[str, int]:
    return {
        "gaming": score_gaming(parts),
        "creator": score_creator(parts),
        "productivity": score_productivity(parts),
        "cooling": score_cooling(parts),
        "noise": score_noise(parts),
        "value": score_value(parts, total_price),
    }


def overall_score(axis_scores: dict[str, int]) -> int:
    if not any(axis_scores.values()):
        return 0
    return _clamp(sum(axis_scores[axis] * _OVERALL_WEIGHTS[axis] for axis in AXES))


def score_tier(overall: int) -> str:
    if overall >= 90:
        return "S TIER"
    if overall >= 75:
        return "A TIER"
    if overall >= 60:
        return "B TIER"
    if overall >= 40:
        return "C TIER"
    return "D TIER"


def score_stars(overall: int) -> int:
    if overall <= 0:
        return 0
    return max(1, min(5, round(overall / 20)))
