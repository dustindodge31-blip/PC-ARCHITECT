"""Live compatibility checks between selected build components."""
from dataclasses import dataclass


@dataclass
class CompatIssue:
    level: str  # "error" | "warning"
    message: str


PSU_HEADROOM = 1.3  # recommend 30% headroom over estimated draw
BASELINE_SYSTEM_DRAW_W = 80  # motherboard, fans, storage, etc.


def check_build(parts: dict) -> list[CompatIssue]:
    """parts: dict of category -> part dict (or None if unselected)."""
    issues: list[CompatIssue] = []

    cpu = parts.get("cpu")
    mobo = parts.get("motherboard")
    ram = parts.get("ram")
    gpu = parts.get("gpu")
    psu = parts.get("psu")
    case = parts.get("case")
    cooler = parts.get("cooler")

    if cpu and mobo:
        if cpu["socket"] != mobo["socket"]:
            issues.append(CompatIssue(
                "error",
                f"CPU socket ({cpu['socket']}) does not match motherboard socket ({mobo['socket']})."
            ))

    if ram and mobo:
        if ram["type"] != mobo["ram_type"]:
            issues.append(CompatIssue(
                "error",
                f"RAM type ({ram['type']}) is not supported by motherboard (requires {mobo['ram_type']})."
            ))
        if ram["capacity_gb"] > mobo["max_ram_gb"]:
            issues.append(CompatIssue(
                "error",
                f"RAM capacity ({ram['capacity_gb']}GB) exceeds motherboard max ({mobo['max_ram_gb']}GB)."
            ))

    if mobo and case:
        if mobo["form_factor"] not in case["form_factors"]:
            issues.append(CompatIssue(
                "error",
                f"Motherboard form factor ({mobo['form_factor']}) is not supported by the selected case."
            ))

    if gpu and case:
        if gpu["length_mm"] > case["max_gpu_length_mm"]:
            issues.append(CompatIssue(
                "error",
                f"GPU length ({gpu['length_mm']}mm) exceeds case max GPU clearance ({case['max_gpu_length_mm']}mm)."
            ))

    if cooler and cpu:
        if cpu["socket"] not in cooler["sockets"]:
            issues.append(CompatIssue(
                "error",
                f"Cooler does not support CPU socket ({cpu['socket']})."
            ))
        if cpu["tdp_w"] > cooler["max_tdp_w"]:
            issues.append(CompatIssue(
                "warning",
                f"CPU TDP ({cpu['tdp_w']}W) may exceed cooler's rated capacity ({cooler['max_tdp_w']}W)."
            ))

    estimated_draw = estimate_power_draw(parts)
    if psu and estimated_draw:
        recommended = estimated_draw * PSU_HEADROOM
        if psu["wattage"] < estimated_draw:
            issues.append(CompatIssue(
                "error",
                f"PSU wattage ({psu['wattage']}W) is below estimated system draw ({estimated_draw:.0f}W)."
            ))
        elif psu["wattage"] < recommended:
            issues.append(CompatIssue(
                "warning",
                f"PSU wattage ({psu['wattage']}W) is below the recommended headroom "
                f"({recommended:.0f}W) for estimated draw ({estimated_draw:.0f}W)."
            ))

    return issues


def estimate_power_draw(parts: dict) -> float:
    total = BASELINE_SYSTEM_DRAW_W
    cpu = parts.get("cpu")
    gpu = parts.get("gpu")
    if cpu:
        total += cpu["tdp_w"]
    if gpu:
        total += gpu["tdp_w"]
    return total


def total_price(parts: dict) -> float:
    return sum(p["price"] for p in parts.values() if p)
