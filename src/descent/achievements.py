"""Achievement definitions and evaluation helpers for Descent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Mapping

from . import meta

if TYPE_CHECKING:  # pragma: no cover - typing-only import
    from .meta import ProgressState


@dataclass(frozen=True)
class AchievementDefinition:
    """Describes an unlockable achievement."""

    key: str
    name: str
    description: str
    metric: str
    threshold: float
    scope: str = "run"
    reward_credits: int = 0
    hint: str = ""

    def is_met(
        self,
        run_stats: Mapping[str, float],
        totals: Mapping[str, float],
        progress: "ProgressState",
    ) -> bool:
        """Return True if the achievement is satisfied."""

        if self.scope == "run":
            value = float(run_stats.get(self.metric, 0))
            return value >= self.threshold
        if self.scope == "total":
            value = float(totals.get(self.metric, 0))
            return value >= self.threshold
        if self.scope == "meta":
            if self.metric == "maxed_tracks":
                maxed_tracks = 0
                for upgrades in progress.purchased.values():
                    for key, level in upgrades.items():
                        definition = meta.UPGRADE_DEFINITIONS.get(key)
                        if definition and level >= definition.max_level:
                            maxed_tracks += 1
                return maxed_tracks >= self.threshold
            if self.metric == "divers_with_upgrades":
                divers = sum(1 for upgrades in progress.purchased.values() if any(level > 0 for level in upgrades.values()))
                return divers >= self.threshold
            return False
        return False


ACHIEVEMENTS: Dict[str, AchievementDefinition] = {
    "first_blood": AchievementDefinition(
        key="first_blood",
        name="First Blood",
        description="Eliminate your first foe during a dive.",
        metric="kills",
        threshold=1,
        scope="run",
        reward_credits=40,
        hint="Drop into any expedition and dispatch a single enemy.",
    ),
    "combo_artist": AchievementDefinition(
        key="combo_artist",
        name="Combo Artist",
        description="Reach Combo Tier 3 in a single run.",
        metric="combo",
        threshold=30,
        scope="run",
        reward_credits=120,
        hint="Keep the pressure on and chain eliminations without slowing down.",
    ),
    "relic_archivist": AchievementDefinition(
        key="relic_archivist",
        name="Relic Archivist",
        description="Bind five relics during a single expedition.",
        metric="relics",
        threshold=5,
        scope="run",
        reward_credits=150,
        hint="Stack relic drops by maintaining a high combo multiplier.",
    ),
    "marathon_diver": AchievementDefinition(
        key="marathon_diver",
        name="Marathon Diver",
        description="Survive for 12 minutes in one session.",
        metric="duration",
        threshold=720.0,
        scope="run",
        reward_credits=220,
        hint="Upgrade vitality and keep moving to stretch each dive.",
    ),
    "arsenal_curator": AchievementDefinition(
        key="arsenal_curator",
        name="Arsenal Curator",
        description="Synchronize 40 different weapons across your career.",
        metric="weapons_synced",
        threshold=40,
        scope="total",
        reward_credits=260,
        hint="Experiment with every elemental archetype you uncover.",
    ),
    "lab_patron": AchievementDefinition(
        key="lab_patron",
        name="Lab Patron",
        description="Purchase 20 Dive Lab upgrades across any divers.",
        metric="upgrades_purchased",
        threshold=20,
        scope="total",
        reward_credits=280,
        hint="Invest your Aether into every specialization track.",
    ),
    "aether_magnate": AchievementDefinition(
        key="aether_magnate",
        name="Aether Magnate",
        description="Accumulate 10,000 Aether lifetime earnings.",
        metric="credits_earned",
        threshold=10000,
        scope="total",
        reward_credits=320,
        hint="Complete objectives and finish dives to bank more currency.",
    ),
    "ability_maestro": AchievementDefinition(
        key="ability_maestro",
        name="Ability Maestro",
        description="Trigger 75 signature abilities across your profile.",
        metric="abilities_used",
        threshold=75,
        scope="total",
        reward_credits=180,
        hint="Remember to unleash Q whenever your cooldown resets.",
    ),
    "vanguard_commander": AchievementDefinition(
        key="vanguard_commander",
        name="Vanguard Commander",
        description="Have upgrades purchased on six different divers.",
        metric="divers_with_upgrades",
        threshold=6,
        scope="meta",
        reward_credits=400,
        hint="Share the love—spend Aether on every specialist in the roster.",
    ),
    "lab_visionary": AchievementDefinition(
        key="lab_visionary",
        name="Lab Visionary",
        description="Max out ten upgrade tracks across all divers.",
        metric="maxed_tracks",
        threshold=10,
        scope="meta",
        reward_credits=600,
        hint="Push your favorite builds all the way to their capstone bonuses.",
    ),
}
