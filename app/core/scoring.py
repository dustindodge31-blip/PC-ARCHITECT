"""PROVISIONAL Architect Score heuristic for Epic 2's build cards.

This is a placeholder so build cards have a score badge to show. It is NOT the
real multi-axis scoring engine (Gaming/Creator/Productivity/Cooling/Noise/Value)
planned for Epic 3 — replace this module's use once that engine exists.
"""
from core import compatibility


def provisional_score(parts: dict) -> int:
    if not any(parts.values()):
        return 0

    score = 60.0
    cpu = parts.get("cpu")
    gpu = parts.get("gpu")
    ram = parts.get("ram")

    if cpu:
        score += min(cpu["cores"], 16) * 1.2
    if gpu:
        score += min(gpu["vram_gb"], 24) * 1.0
    if ram:
        score += min(ram["capacity_gb"], 64) * 0.15

    issues = compatibility.check_build(parts)
    score -= sum(10 if issue.level == "error" else 3 for issue in issues)

    return max(0, min(100, round(score)))
