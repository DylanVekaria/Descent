from __future__ import annotations

"""Relic definitions that drop during runs.

Relics provide long-term stat changes or reactive effects that stack for the
duration of a run. The game runtime aggregates relic bonuses to keep gameplay
logic simple.
"""

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional
import random


@dataclass(frozen=True)
class RelicProfile:
    key: str
    name: str
    description: str
    effect: str
    value: float
    tags: tuple[str, ...] = ()


RELICS: List[RelicProfile] = [
    RelicProfile(
        key="fractal_matrix",
        name="Fractal Matrix",
        description="Damage increases by 12% per stack.",
        effect="damage_bonus",
        value=0.12,
        tags=("offense",),
    ),
    RelicProfile(
        key="chrono_mote",
        name="Chrono Mote",
        description="Ability cooldowns recover 18% faster.",
        effect="ability_haste",
        value=0.18,
        tags=("utility",),
    ),
    RelicProfile(
        key="void_glass",
        name="Void Glass",
        description="Combo window extended by 1.5s per stack.",
        effect="combo_extend",
        value=1.5,
        tags=("combo",),
    ),
    RelicProfile(
        key="aetheric_vestige",
        name="Aetheric Vestige",
        description="Gain 8% damage reduction at full combo.",
        effect="combo_shield",
        value=0.08,
        tags=("defense",),
    ),
    RelicProfile(
        key="aurora_petals",
        name="Aurora Petals",
        description="Heal 6% integrity at the end of each wave.",
        effect="wave_heal",
        value=0.06,
        tags=("support",),
    ),
    RelicProfile(
        key="circuit_surge",
        name="Circuit Surge",
        description="Reloads 20% faster and grant 5% focus.",
        effect="focus_bonus",
        value=0.2,
        tags=("tempo",),
    ),
    RelicProfile(
        key="graviton_core",
        name="Graviton Core",
        description="Projectiles pull enemies inward slightly.",
        effect="gravity_rounds",
        value=0.65,
        tags=("control",),
    ),
    RelicProfile(
        key="phase_reservoir",
        name="Phase Reservoir",
        description="Gain a 30 integrity shield when ability is used.",
        effect="ability_shield",
        value=30.0,
        tags=("defense",),
    ),
    RelicProfile(
        key="storm_catalyst",
        name="Storm Catalyst",
        description="Weapon pickups also grant 12% move speed for 8s.",
        effect="pickup_speed",
        value=0.12,
        tags=("mobility",),
    ),
    RelicProfile(
        key="nanite_brood",
        name="Nanite Brood",
        description="Summoned drones deal 25% additional damage.",
        effect="drone_damage",
        value=0.25,
        tags=("summon",),
    ),
    RelicProfile(
        key="meridian_map",
        name="Meridian Map",
        description="Dynamic events trigger 20% more frequently.",
        effect="event_rate",
        value=0.2,
        tags=("exploration",),
    ),
    RelicProfile(
        key="resonant_orb",
        name="Resonant Orb",
        description="Critical chance increases by 6%.",
        effect="crit_bonus",
        value=0.06,
        tags=("offense",),
    ),
    RelicProfile(
        key="kinetic_ram",
        name="Kinetic Ram",
        description="Shockwave effects push 50% further.",
        effect="shockwave_boost",
        value=0.5,
        tags=("control",),
    ),
    RelicProfile(
        key="embershard",
        name="Embershard",
        description="Burning damage over time intensified by 30%.",
        effect="burn_bonus",
        value=0.3,
        tags=("burn",),
    ),
    RelicProfile(
        key="celestial_seed",
        name="Celestial Seed",
        description="Max integrity increases by 14.",
        effect="max_hp",
        value=14.0,
        tags=("support",),
    ),
    RelicProfile(
        key="phantom_coin",
        name="Phantom Coin",
        description="Gain +6 bonus Aether when a run ends.",
        effect="bonus_credits",
        value=6.0,
        tags=("economy",),
    ),
    RelicProfile(
        key="entropic_loop",
        name="Entropic Loop",
        description="Every fifth combo tier spawns an extra pickup.",
        effect="combo_drop",
        value=1.0,
        tags=("combo",),
    ),
]


def random_relic(exclude: Optional[Iterable[str]] = None) -> RelicProfile:
    excluded = set(exclude or ())
    pool = [relic for relic in RELICS if relic.key not in excluded]
    if not pool:
        pool = RELICS
    return random.choice(pool)


def get_relic(key: str) -> RelicProfile:
    lookup: Dict[str, RelicProfile] = {relic.key: relic for relic in RELICS}
    return lookup[key]

