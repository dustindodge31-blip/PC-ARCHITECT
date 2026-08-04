"""Simulated price history — no real retail price API is wired up, so this is a
deterministic random walk seeded per part ID, not real market data. Good enough
to demonstrate price tracking (current/low/high/average, price-drop indicator).
"""
import hashlib
import random

DAYS = 90
DAILY_VOLATILITY = 0.02  # +/- 2% per day
MIN_FRACTION = 0.80  # floor: 80% of base price
MAX_FRACTION = 1.15  # ceiling: 115% of base price


def _seed_for(part_id: str) -> int:
    return int(hashlib.sha256(part_id.encode("utf-8")).hexdigest(), 16) % (2**32)


def price_series(part_id: str, base_price: float, days: int = DAYS) -> list[float]:
    rng = random.Random(_seed_for(part_id))
    price = base_price
    series = []
    for _ in range(days):
        change = rng.uniform(-DAILY_VOLATILITY, DAILY_VOLATILITY)
        price *= 1 + change
        price = max(base_price * MIN_FRACTION, min(base_price * MAX_FRACTION, price))
        series.append(round(price, 2))
    return series


def price_stats(part_id: str, base_price: float) -> dict:
    series = price_series(part_id, base_price)
    return {
        "current": series[-1],
        "lowest": min(series),
        "highest": max(series),
        "average": round(sum(series) / len(series), 2),
    }


def is_good_time_to_buy(stats: dict) -> bool:
    return stats["current"] <= stats["average"] * 0.97
