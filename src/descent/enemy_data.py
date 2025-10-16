from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class EnemyProfile:
    key: str
    name: str
    description: str
    max_hp: int
    speed: float
    damage: float
    behavior: str
    tint: Tuple[int, int, int]


ENEMIES: List[EnemyProfile] = [
    EnemyProfile(
        key="wraith",
        name="Echo Wraith",
        description="Phases erratically and fires void bolts.",
        max_hp=40,
        speed=120,
        damage=8,
        behavior="orbit",
        tint=(214, 82, 165),
    ),
    EnemyProfile(
        key="cultist",
        name="Acolyte of the Depth",
        description="Maintains distance while channeling volleys.",
        max_hp=60,
        speed=90,
        damage=10,
        behavior="strafer",
        tint=(233, 196, 229),
    ),
    EnemyProfile(
        key="golem",
        name="Basalt Golem",
        description="Slow juggernaut that charges in straight lines.",
        max_hp=110,
        speed=75,
        damage=14,
        behavior="charger",
        tint=(205, 186, 150),
    ),
]

STAGE_MODIFIERS: Dict[int, Dict[str, float]] = {
    1: {"hp": 1.0, "damage": 1.0, "speed": 1.0},
    2: {"hp": 1.2, "damage": 1.1, "speed": 1.05},
    3: {"hp": 1.5, "damage": 1.2, "speed": 1.1},
    4: {"hp": 1.8, "damage": 1.35, "speed": 1.15},
    5: {"hp": 2.2, "damage": 1.5, "speed": 1.2},
}

