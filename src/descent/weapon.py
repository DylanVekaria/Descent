from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pygame

from .weapon_data import WeaponProfile


@dataclass
class Projectile:
    sprite: pygame.sprite.Sprite
    damage: float
    speed: float
    direction: pygame.Vector2


class WeaponInstance:
    def __init__(self, profile: WeaponProfile, damage_multiplier: float = 1.0, focus_multiplier: float = 1.0):
        self.profile = profile
        self.damage_multiplier = damage_multiplier
        self.focus_multiplier = focus_multiplier
        self.cooldown = 0.0
        self.ammo = profile.magazine
        self.reload_timer = 0.0

    def update(self, dt: float) -> None:
        if self.cooldown > 0:
            self.cooldown = max(0.0, self.cooldown - dt)
        if self.reload_timer > 0:
            self.reload_timer = max(0.0, self.reload_timer - dt)
            if self.reload_timer == 0:
                self.ammo = self.profile.magazine

    def trigger_reload(self) -> None:
        if self.reload_timer <= 0:
            self.reload_timer = self.profile.reload_time / max(0.1, self.focus_multiplier)
            self.cooldown = max(self.cooldown, 0.2)

    def ready(self) -> bool:
        return self.cooldown <= 0 and self.reload_timer <= 0 and self.ammo > 0

    def fire(self) -> None:
        self.cooldown = 1.0 / (self.profile.fire_rate * max(0.1, self.focus_multiplier))
        self.ammo -= 1
        if self.ammo <= 0:
            self.trigger_reload()

    def apply_modifiers(self, damage_multiplier: float, focus_multiplier: float) -> None:
        self.damage_multiplier = damage_multiplier
        self.focus_multiplier = focus_multiplier

    @property
    def damage(self) -> float:
        return self.profile.base_damage * self.damage_multiplier

