"""FPS estimator and bottleneck analysis.

Heuristic, calibrated off the same GPU/CPU gaming indices as the Gaming axis
score (core/scoring.py) — no real benchmark database is wired up, so these
are relative estimates for comparing settings/builds, not measured FPS.
"""
from dataclasses import dataclass

from core import scoring

REFERENCE_SCALE = 240  # tuned so a top-tier build hits ~180fps at 1080p/Ultra in a demanding title

GAMES = [
    {"id": "cyberpunk2077", "name": "Cyberpunk 2077", "demand": 0.95, "cpu_weight": 0.20},
    {"id": "starfield", "name": "Starfield", "demand": 0.85, "cpu_weight": 0.30},
    {"id": "baldurs_gate_3", "name": "Baldur's Gate 3", "demand": 0.60, "cpu_weight": 0.45},
    {"id": "apex_legends", "name": "Apex Legends", "demand": 0.55, "cpu_weight": 0.35},
    {"id": "fortnite", "name": "Fortnite", "demand": 0.50, "cpu_weight": 0.35},
    {"id": "minecraft", "name": "Minecraft", "demand": 0.35, "cpu_weight": 0.65},
    {"id": "cs2", "name": "Counter-Strike 2", "demand": 0.30, "cpu_weight": 0.50},
    {"id": "valorant", "name": "Valorant", "demand": 0.20, "cpu_weight": 0.50},
]

RESOLUTIONS = {"1080p": 1.0, "1440p": 0.65, "4K": 0.38}
SETTINGS_PRESETS = {"Low": 1.4, "Medium": 1.15, "High": 1.0, "Ultra": 0.8}
UPSCALING_MODES = {"Off": 1.0, "Balanced": 1.35, "Performance": 1.6}
RAY_TRACING_MULTIPLIER = 0.55
FRAME_GEN_MULTIPLIER = 1.8

_GAMES_BY_ID = {g["id"]: g for g in GAMES}


@dataclass
class BottleneckInsight:
    severity: str  # "error" | "warning"
    title: str
    why: str
    impact: str
    fix: str


def find_game(game_id: str) -> dict:
    return _GAMES_BY_ID.get(game_id, GAMES[0])


def estimate_fps(
    parts: dict,
    game_id: str,
    resolution: str = "1080p",
    settings: str = "High",
    ray_tracing: bool = False,
    upscaling: str = "Off",
    frame_gen: bool = False,
) -> int:
    game = find_game(game_id)
    gpu_idx = scoring.gpu_gaming_index(parts.get("gpu"))
    cpu_idx = scoring.cpu_gaming_index(parts.get("cpu"))
    if gpu_idx == 0 and cpu_idx == 0:
        return 0

    combined = gpu_idx * (1 - game["cpu_weight"]) + cpu_idx * game["cpu_weight"]
    base_fps = (combined / 100) * REFERENCE_SCALE / max(game["demand"], 0.05)

    fps = base_fps
    fps *= RESOLUTIONS.get(resolution, 1.0)
    fps *= SETTINGS_PRESETS.get(settings, 1.0)
    if ray_tracing:
        fps *= RAY_TRACING_MULTIPLIER
    fps *= UPSCALING_MODES.get(upscaling, 1.0)
    if frame_gen:
        fps *= FRAME_GEN_MULTIPLIER

    return max(1, round(fps))


def analyze_bottleneck(parts: dict) -> list[BottleneckInsight]:
    insights: list[BottleneckInsight] = []
    gpu, cpu, ram = parts.get("gpu"), parts.get("cpu"), parts.get("ram")

    if gpu and cpu:
        gpu_idx = scoring.gpu_gaming_index(gpu)
        cpu_idx = scoring.cpu_gaming_index(cpu)
        gap = gpu_idx - cpu_idx
        if gap > 20:
            insights.append(BottleneckInsight(
                severity="warning",
                title="CPU Bottleneck",
                why=f"Your GPU (index {gpu_idx}) significantly outperforms your CPU (index {cpu_idx}).",
                impact="The CPU can't feed the GPU fast enough, especially at 1080p or high refresh "
                       "rates — you won't see the GPU's full potential.",
                fix="Consider a CPU with more cores/threads, or expect bigger gains at higher "
                    "resolutions where the GPU becomes the limiting factor instead.",
            ))
        elif gap < -20:
            insights.append(BottleneckInsight(
                severity="warning",
                title="GPU Bottleneck",
                why=f"Your CPU (index {cpu_idx}) significantly outperforms your GPU (index {gpu_idx}).",
                impact="Frame rates will be capped by the GPU well below what your CPU could "
                       "otherwise drive, especially at higher resolutions and settings.",
                fix="Consider a stronger GPU, or lower resolution/settings to better match "
                    "your CPU's headroom.",
            ))

    if ram:
        if ram["capacity_gb"] < 16:
            insights.append(BottleneckInsight(
                severity="warning",
                title="Memory Bottleneck",
                why=f"Only {ram['capacity_gb']}GB of RAM is installed.",
                impact="Modern games and background processes can exceed this, causing stutters "
                       "or the system swapping to disk.",
                fix="Upgrade to at least 16GB — 32GB for the smoothest multitasking-while-gaming experience.",
            ))
    else:
        insights.append(BottleneckInsight(
            severity="error",
            title="No RAM Selected",
            why="No RAM is selected for this build yet.",
            impact="FPS and bottleneck estimates can't account for memory until RAM is chosen.",
            fix="Pick RAM in the Parts tab.",
        ))

    return insights
