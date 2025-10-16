from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

import random


@dataclass(frozen=True)
class WeaponProfile:
    name: str
    base_damage: float
    fire_rate: float
    projectile_speed: float
    spread: float
    magazine: int
    reload_time: float
    color: Tuple[int, int, int]
    keywords: Tuple[str, ...]


BASE_TYPES: Dict[str, Dict[str, float]] = {
    "Pulse": {"damage": 7.0, "fire_rate": 6.0, "speed": 520.0, "spread": 4.0, "magazine": 16, "reload": 1.4},
    "Burst": {"damage": 5.0, "fire_rate": 9.0, "speed": 480.0, "spread": 6.0, "magazine": 24, "reload": 1.7},
    "Rail": {"damage": 14.0, "fire_rate": 2.3, "speed": 860.0, "spread": 1.0, "magazine": 6, "reload": 2.2},
    "Scatter": {"damage": 4.0, "fire_rate": 3.2, "speed": 460.0, "spread": 14.0, "magazine": 12, "reload": 1.9},
    "Nova": {"damage": 6.5, "fire_rate": 5.2, "speed": 540.0, "spread": 8.0, "magazine": 18, "reload": 1.6},
    "Arc": {"damage": 8.0, "fire_rate": 4.1, "speed": 600.0, "spread": 5.0, "magazine": 14, "reload": 1.5},
}

MANUFACTURERS: Dict[str, Dict[str, float]] = {
    "Helix": {"damage": 0.9, "fire_rate": 1.1, "spread": 0.9, "keywords": ("stabilized",)},
    "Vyr": {"damage": 1.1, "fire_rate": 1.0, "speed": 1.05, "keywords": ("kinetic",)},
    "Axiom": {"damage": 1.0, "fire_rate": 1.2, "magazine": 1.2, "keywords": ("auto",)},
    "Myriad": {"damage": 0.95, "fire_rate": 1.05, "magazine": 1.4, "reload": 0.8, "keywords": ("swarm",)},
    "Obsidian": {"damage": 1.3, "fire_rate": 0.7, "speed": 1.2, "keywords": ("piercing",)},
    "Aurora": {"damage": 1.05, "fire_rate": 1.05, "speed": 1.1, "keywords": ("auric",)},
}

ELEMENTS: Dict[str, Dict[str, float]] = {
    "Pyre": {"damage": 1.2, "dot": 1.5, "keywords": ("burn",)},
    "Frost": {"damage": 1.0, "slow": 0.7, "keywords": ("slow",)},
    "Volt": {"damage": 0.95, "chain": 2.0, "keywords": ("chain",)},
    "Toxin": {"damage": 1.1, "dot": 2.1, "keywords": ("poison",)},
    "Radiant": {"damage": 1.0, "crit": 1.25, "keywords": ("radiant",)},
    "Umbral": {"damage": 1.15, "lifesteal": 0.05, "keywords": ("void",)},
}

ELEMENT_COLORS = {
    "Pyre": (255, 109, 87),
    "Frost": (132, 206, 235),
    "Volt": (115, 255, 215),
    "Toxin": (150, 255, 102),
    "Radiant": (255, 220, 128),
    "Umbral": (171, 129, 255),
}


TOTAL_WEAPONS = len(BASE_TYPES) * len(MANUFACTURERS) * len(ELEMENTS)


def generate_weapon_catalog() -> List[WeaponProfile]:
    catalog: List[WeaponProfile] = []
    for base_name, base in BASE_TYPES.items():
        for maker_name, maker in MANUFACTURERS.items():
            for element_name, element in ELEMENTS.items():
                damage = base["damage"] * maker.get("damage", 1.0) * element["damage"]
                fire_rate = base["fire_rate"] * maker.get("fire_rate", 1.0)
                projectile_speed = base["speed"] * maker.get("speed", 1.0)
                spread = base["spread"] * maker.get("spread", 1.0)
                magazine = max(4, int(base["magazine"] * maker.get("magazine", 1.0)))
                reload_time = base["reload"] * maker.get("reload", 1.0)
                keywords = (
                    base_name.lower(),
                    maker_name.lower(),
                    element_name.lower(),
                ) + maker.get("keywords", ()) + element.get("keywords", ())

                name = f"{element_name} {maker_name} {base_name}"
                color = ELEMENT_COLORS[element_name]
                catalog.append(
                    WeaponProfile(
                        name=name,
                        base_damage=round(damage, 2),
                        fire_rate=round(fire_rate, 2),
                        projectile_speed=round(projectile_speed, 2),
                        spread=round(spread, 2),
                        magazine=magazine,
                        reload_time=round(reload_time, 2),
                        color=color,
                        keywords=keywords,
                    )
                )
    return catalog


WEAPON_CATALOG: List[WeaponProfile] = generate_weapon_catalog()


def random_weapon(exclude: Iterable[str] | None = None) -> WeaponProfile:
    exclude = set(exclude or ())
    choices = [weapon for weapon in WEAPON_CATALOG if weapon.name not in exclude]
    if not choices:
        return random.choice(WEAPON_CATALOG)
    return random.choice(choices)


