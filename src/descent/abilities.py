from __future__ import annotations

"""Ability definitions for playable characters.

Each ability is intentionally data-driven so new characters can bind to them
without altering the runtime logic in :mod:`descent.game`. The ``effect``
field is interpreted by the game loop which applies the relevant gameplay
response (blink, nova, overdrive, etc.).
"""

from dataclasses import dataclass, field
from typing import Dict, Mapping


@dataclass(frozen=True)
class AbilityProfile:
    key: str
    name: str
    description: str
    cooldown: float
    effect: str
    magnitude: float
    payload: Mapping[str, float] = field(default_factory=dict)


ABILITIES: Dict[str, AbilityProfile] = {
    "rift_step": AbilityProfile(
        key="rift_step",
        name="Rift Step",
        description="Blink to the cursor and phase out of danger momentarily.",
        cooldown=8.0,
        effect="blink",
        magnitude=260.0,
        payload={"invuln": 0.6},
    ),
    "bastion_overdrive": AbilityProfile(
        key="bastion_overdrive",
        name="Bastion Overdrive",
        description="Overcharge armor plating, boosting damage and granting shields.",
        cooldown=14.0,
        effect="overdrive",
        magnitude=0.25,
        payload={"focus": 0.2, "speed": 35, "duration": 6.0, "shield": 45},
    ),
    "prism_barrage": AbilityProfile(
        key="prism_barrage",
        name="Prism Barrage",
        description="Emit refracted salvos that pierce enemies in every direction.",
        cooldown=11.0,
        effect="nova",
        magnitude=1.4,
        payload={"projectiles": 14, "pierce": 1},
    ),
    "swarm_convergence": AbilityProfile(
        key="swarm_convergence",
        name="Swarm Convergence",
        description="Summon a parasitic drone that siphons foes for sustained damage.",
        cooldown=16.0,
        effect="summon_drone",
        magnitude=28.0,
        payload={"duration": 18.0, "fire_delay": 0.9},
    ),
    "tempo_loop": AbilityProfile(
        key="tempo_loop",
        name="Tempo Loop",
        description="Double down on rhythm to heighten fire rate and movement speed.",
        cooldown=10.0,
        effect="overdrive",
        magnitude=0.18,
        payload={"focus": 0.35, "speed": 55, "duration": 5.0},
    ),
    "eruption_protocol": AbilityProfile(
        key="eruption_protocol",
        name="Eruption Protocol",
        description="Trigger a burning explosion that scorches everything nearby.",
        cooldown=12.0,
        effect="nova",
        magnitude=1.7,
        payload={"projectiles": 18, "ignite": 6.0},
    ),
    "gravity_well": AbilityProfile(
        key="gravity_well",
        name="Gravity Well",
        description="Compress local space, slowing enemies and amplifying damage taken.",
        cooldown=15.0,
        effect="gravity",
        magnitude=320.0,
        payload={"slow": 0.45, "duration": 5.5},
    ),
    "drone_command": AbilityProfile(
        key="drone_command",
        name="Drone Command",
        description="Deploy a trio of support drones that strafe the arena.",
        cooldown=20.0,
        effect="summon_drone_squad",
        magnitude=22.0,
        payload={"count": 3, "duration": 15.0, "fire_delay": 1.2},
    ),
    "shock_blast": AbilityProfile(
        key="shock_blast",
        name="Shock Blast",
        description="Detonate kinetic charges to shove enemies outward and stun.",
        cooldown=13.0,
        effect="shockwave",
        magnitude=220.0,
        payload={"damage": 1.1, "stun": 1.3},
    ),
    "bloom_aegis": AbilityProfile(
        key="bloom_aegis",
        name="Bloom Aegis",
        description="Burst restorative spores that heal allies and grant shielding.",
        cooldown=12.0,
        effect="heal_shield",
        magnitude=0.35,
        payload={"shield": 55},
    ),
    "eclipse_focus": AbilityProfile(
        key="eclipse_focus",
        name="Eclipse Focus",
        description="Enter an assassin trance, guaranteeing critical hits briefly.",
        cooldown=9.5,
        effect="overdrive",
        magnitude=0.3,
        payload={"crit": 0.4, "duration": 4.5},
    ),
    "maelstrom_surge": AbilityProfile(
        key="maelstrom_surge",
        name="Maelstrom Surge",
        description="Chain lightning erupts outward, slowing and shocking enemies.",
        cooldown=11.5,
        effect="storm",
        magnitude=1.25,
        payload={"chains": 5, "slow": 0.4},
    ),
}


def get_ability(key: str) -> AbilityProfile:
    return ABILITIES[key]

