from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class CharacterProfile:
    name: str
    title: str
    description: str
    stats: Dict[str, float]
    primary_color: Tuple[int, int, int]
    secondary_color: Tuple[int, int, int]
    starting_keywords: Tuple[str, ...]


CHARACTERS: List[CharacterProfile] = [
    CharacterProfile(
        name="Kaia",
        title="The Rift Diver",
        description="A scientist-turned-explorer who bends reality to slip between attacks.",
        stats={"max_hp": 90, "speed": 210, "damage": 1.0, "crit": 0.1, "focus": 1.2},
        primary_color=(102, 255, 178),
        secondary_color=(45, 197, 253),
        starting_keywords=("void", "adaptive"),
    ),
    CharacterProfile(
        name="Bram",
        title="The Spire Warden",
        description="Heavy armor and heavier hits make Bram a relentless frontliner.",
        stats={"max_hp": 140, "speed": 170, "damage": 1.25, "crit": 0.05, "focus": 0.9},
        primary_color=(255, 184, 108),
        secondary_color=(255, 147, 79),
        starting_keywords=("fortified", "guardian"),
    ),
    CharacterProfile(
        name="Rin",
        title="The Prism Slinger",
        description="Channels pure light into volatile refracting salvos.",
        stats={"max_hp": 80, "speed": 230, "damage": 0.9, "crit": 0.2, "focus": 1.3},
        primary_color=(255, 220, 128),
        secondary_color=(252, 240, 193),
        starting_keywords=("radiant", "mobile"),
    ),
    CharacterProfile(
        name="Sahr",
        title="The Hexed",
        description="Wields corruptive ichor that siphons foes to feed the swarm.",
        stats={"max_hp": 95, "speed": 200, "damage": 1.1, "crit": 0.12, "focus": 1.1},
        primary_color=(171, 129, 255),
        secondary_color=(121, 71, 191),
        starting_keywords=("void", "poison"),
    ),
    CharacterProfile(
        name="Eryn",
        title="The Resonant",
        description="Synchronizes to battlefield rhythms, accelerating reloads and fire tempo.",
        stats={"max_hp": 85, "speed": 220, "damage": 1.05, "crit": 0.08, "focus": 1.4},
        primary_color=(115, 255, 215),
        secondary_color=(64, 180, 160),
        starting_keywords=("tempo", "chain"),
    ),
    CharacterProfile(
        name="Jiro",
        title="The Emberblade",
        description="Imbues shots with roaring flame that leaves searing trails.",
        stats={"max_hp": 100, "speed": 205, "damage": 1.15, "crit": 0.1, "focus": 1.0},
        primary_color=(255, 109, 87),
        secondary_color=(255, 189, 103),
        starting_keywords=("burn", "aggressive"),
    ),
    CharacterProfile(
        name="Nova",
        title="The Aurora",
        description="Manipulates gravitational lightfields for piercing orbitals.",
        stats={"max_hp": 105, "speed": 210, "damage": 1.05, "crit": 0.15, "focus": 1.05},
        primary_color=(132, 206, 235),
        secondary_color=(82, 146, 205),
        starting_keywords=("auric", "control"),
    ),
    CharacterProfile(
        name="Mara",
        title="The Myriad",
        description="A hive of drones that overwhelm with sheer projectile count.",
        stats={"max_hp": 75, "speed": 215, "damage": 0.85, "crit": 0.12, "focus": 1.6},
        primary_color=(186, 255, 201),
        secondary_color=(90, 177, 120),
        starting_keywords=("swarm", "drone"),
    ),
    CharacterProfile(
        name="Quen",
        title="The Breaker",
        description="Knocks enemies off balance with concussive blasts.",
        stats={"max_hp": 120, "speed": 180, "damage": 1.2, "crit": 0.07, "focus": 0.95},
        primary_color=(255, 82, 82),
        secondary_color=(255, 144, 144),
        starting_keywords=("stagger", "kinetic"),
    ),
    CharacterProfile(
        name="Iska",
        title="The Bloom",
        description="Radiates regenerative spores that keep allies alive and enemies weak.",
        stats={"max_hp": 110, "speed": 190, "damage": 0.95, "crit": 0.05, "focus": 1.2},
        primary_color=(150, 255, 102),
        secondary_color=(90, 204, 90),
        starting_keywords=("support", "poison"),
    ),
    CharacterProfile(
        name="Lune",
        title="The Silencer",
        description="A patient hunter who thrives on precision critical hits.",
        stats={"max_hp": 85, "speed": 195, "damage": 1.3, "crit": 0.2, "focus": 0.9},
        primary_color=(111, 255, 233),
        secondary_color=(64, 175, 162),
        starting_keywords=("sniper", "silent"),
    ),
    CharacterProfile(
        name="Tari",
        title="The Maelstrom",
        description="Harnesses volatile storms to lash at clustered foes.",
        stats={"max_hp": 95, "speed": 215, "damage": 1.0, "crit": 0.1, "focus": 1.3},
        primary_color=(115, 170, 255),
        secondary_color=(72, 105, 217),
        starting_keywords=("storm", "chain"),
    ),
]

