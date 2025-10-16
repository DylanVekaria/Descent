from __future__ import annotations

import math
import random
from typing import Iterable, Optional

import pygame

from .art import enemy_sprite, pickup_sprite, player_sprite, projectile_sprite
from .character_data import CharacterProfile
from .constants import RUN_COLORS
from .enemy_data import EnemyProfile
from .weapon import WeaponInstance


class Player(pygame.sprite.Sprite):
    def __init__(
        self,
        character: CharacterProfile,
        weapon: WeaponInstance,
        position: pygame.Vector2,
        upgraded_stats: dict[str, float] | None = None,
    ):
        super().__init__()
        self.character = character
        self.weapon = weapon
        self.base_stats = (upgraded_stats or character.stats).copy()
        self.stats = self.base_stats.copy()
        self.base_max_hp = int(self.base_stats.get("max_hp", 90))
        self.perm_hp_bonus = 0.0
        self.max_hp = int(self.base_max_hp)
        self.hp = float(self.max_hp)
        self.base_speed = self.base_stats.get("speed", 200)
        self.perm_speed_bonus = 0.0
        self.temp_speed_bonus = 0.0
        self.pickup_speed_bonus = 0.0
        self.pickup_speed_timer = 0.0
        self.speed = self.base_speed
        self.base_damage = self.base_stats.get("damage", 1.0)
        self.perm_damage_bonus = 0.0
        self.temp_damage_bonus = 0.0
        self.damage_multiplier = self.base_damage
        self.base_crit = self.base_stats.get("crit", 0.05)
        self.perm_crit_bonus = 0.0
        self.temp_crit_bonus = 0.0
        self.crit_chance = self.base_crit
        self.base_focus = self.base_stats.get("focus", 1.0)
        self.perm_focus_bonus = 0.0
        self.temp_focus_bonus = 0.0
        self.focus_multiplier = self.base_focus
        self.weapon.apply_modifiers(self.damage_multiplier, self.focus_multiplier)
        self.image = player_sprite(character.primary_color, character.secondary_color)
        self.rect = self.image.get_rect(center=position)
        self.velocity = pygame.Vector2(0, 0)
        self.invincible_timer = 0.0
        self.base_shield = float(self.base_stats.get("shield", 0.0))
        self.shield = float(self.base_shield)
        self.overdrive_timer = 0.0

    def update(self, dt: float) -> None:
        if self.invincible_timer > 0:
            self.invincible_timer = max(0.0, self.invincible_timer - dt)
        if self.overdrive_timer > 0:
            self.overdrive_timer = max(0.0, self.overdrive_timer - dt)
            if self.overdrive_timer == 0:
                self.temp_damage_bonus = 0.0
                self.temp_focus_bonus = 0.0
                self.temp_speed_bonus = 0.0
                self.temp_crit_bonus = 0.0
                self.refresh_stats()
        if self.pickup_speed_timer > 0:
            self.pickup_speed_timer = max(0.0, self.pickup_speed_timer - dt)
            if self.pickup_speed_timer == 0:
                self.pickup_speed_bonus = 0.0
                self.refresh_stats()
        displacement = self.velocity * dt
        self.rect.centerx += displacement.x
        self.rect.centery += displacement.y

    def move(self, direction: pygame.Vector2) -> None:
        if direction.length_squared() > 0:
            direction = direction.normalize()
        self.velocity = direction * self.speed

    def take_damage(self, amount: float) -> None:
        if self.invincible_timer > 0:
            return
        if self.shield > 0:
            absorbed = min(amount, self.shield)
            self.shield -= absorbed
            amount -= absorbed
        if amount <= 0:
            return
        self.hp = max(0.0, self.hp - amount)
        self.invincible_timer = 0.6

    def heal(self, amount: float) -> None:
        self.hp = min(self.max_hp, self.hp + amount)

    def refresh_stats(self) -> None:
        self.max_hp = int(self.base_max_hp + self.perm_hp_bonus)
        if self.hp > self.max_hp:
            self.hp = float(self.max_hp)
        self.speed = (
            self.base_speed + self.perm_speed_bonus + self.temp_speed_bonus + self.pickup_speed_bonus
        )
        self.damage_multiplier = self.base_damage + self.perm_damage_bonus + self.temp_damage_bonus
        self.focus_multiplier = self.base_focus + self.perm_focus_bonus + self.temp_focus_bonus
        self.crit_chance = self.base_crit + self.perm_crit_bonus + self.temp_crit_bonus
        if self.weapon:
            self.weapon.apply_modifiers(self.damage_multiplier, self.focus_multiplier)

    def apply_permanent_bonus(self, stat: str, amount: float) -> None:
        if stat == "damage":
            self.perm_damage_bonus += amount
        elif stat == "speed":
            self.perm_speed_bonus += amount
        elif stat == "focus":
            self.perm_focus_bonus += amount
        elif stat == "crit":
            self.perm_crit_bonus += amount
        elif stat == "max_hp":
            self.perm_hp_bonus += amount
        self.refresh_stats()
        if stat == "max_hp":
            self.hp = min(self.max_hp, self.hp + amount)

    def apply_temp_bonus(
        self,
        *,
        damage: float = 0.0,
        focus: float = 0.0,
        speed: float = 0.0,
        crit: float = 0.0,
        duration: float = 0.0,
    ) -> None:
        self.temp_damage_bonus = damage
        self.temp_focus_bonus = focus
        self.temp_speed_bonus = speed
        self.temp_crit_bonus = crit
        self.overdrive_timer = duration
        self.refresh_stats()

    def grant_shield(self, amount: float) -> None:
        self.shield = min(self.max_hp * 1.5, self.shield + amount)

    def reset_pickup_speed(self, bonus: float, duration: float) -> None:
        self.pickup_speed_bonus = self.base_speed * bonus
        self.pickup_speed_timer = duration
        self.refresh_stats()


class Projectile(pygame.sprite.Sprite):
    def __init__(self, position: pygame.Vector2, direction: pygame.Vector2, speed: float, damage: float, color):
        super().__init__()
        self.direction = direction.normalize()
        self.speed = speed
        self.damage = damage
        self.image = projectile_sprite(color)
        self.rect = self.image.get_rect(center=position)

    def update(self, dt: float) -> None:
        movement = self.direction * self.speed * dt
        self.rect.centerx += movement.x
        self.rect.centery += movement.y


class Enemy(pygame.sprite.Sprite):
    def __init__(self, profile: EnemyProfile, stage_modifier: float, position: pygame.Vector2):
        super().__init__()
        self.profile = profile
        self.max_hp = int(profile.max_hp * stage_modifier)
        self.hp = float(self.max_hp)
        self.speed = profile.speed * stage_modifier
        self.damage = profile.damage * stage_modifier
        self.behavior = profile.behavior
        self.image = enemy_sprite(profile.key)
        # Apply tint overlay
        tint_surface = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        tint_surface.fill((*profile.tint, 80))
        self.image.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        self.rect = self.image.get_rect(center=position)
        self.cooldown = random.uniform(0.4, 1.2)

    def update(self, dt: float, player_position: pygame.Vector2) -> None:
        self.cooldown = max(0.0, self.cooldown - dt)
        direction = pygame.Vector2(player_position) - pygame.Vector2(self.rect.center)
        if self.behavior == "orbit" and direction.length_squared() > 0:
            angle = math.atan2(direction.y, direction.x) + math.pi / 2
            direction = pygame.Vector2(math.cos(angle), math.sin(angle))
        elif self.behavior == "strafer" and direction.length_squared() > 0:
            angle = math.atan2(direction.y, direction.x)
            direction = pygame.Vector2(math.cos(angle), math.sin(angle))
        elif self.behavior == "charger" and direction.length_squared() > 0:
            direction = direction.normalize()
        else:
            direction = pygame.Vector2(0, 0)

        if direction.length_squared() > 0:
            direction = direction.normalize()
        movement = direction * self.speed * dt
        self.rect.centerx += movement.x
        self.rect.centery += movement.y

    def take_damage(self, amount: float) -> None:
        self.hp = max(0.0, self.hp - amount)


class Pickup(pygame.sprite.Sprite):
    def __init__(self, pickup_type: str, payload, position: pygame.Vector2, color):
        super().__init__()
        self.pickup_type = pickup_type
        self.payload = payload
        self.image = pickup_sprite(color)
        self.rect = self.image.get_rect(center=position)
        self.bounce_timer = 0.0
        self.base_y = float(self.rect.centery)

    def update(self, dt: float) -> None:
        self.bounce_timer += dt
        offset = math.sin(self.bounce_timer * 5) * 6
        self.rect.centery = int(self.base_y + offset)


class SupportDrone(pygame.sprite.Sprite):
    def __init__(
        self,
        owner: Player,
        orbit_radius: float,
        damage: float,
        fire_delay: float,
        duration: float,
        color: Optional[tuple[int, int, int]] = None,
    ) -> None:
        super().__init__()
        self.owner = owner
        self.orbit_radius = orbit_radius
        self.damage = damage
        self.fire_delay = fire_delay
        self.duration = duration
        self.timer = duration
        self.angle = random.uniform(0, math.tau)
        self.cooldown = random.uniform(0.2, fire_delay)
        palette = color or RUN_COLORS["player_secondary"]
        self.image = projectile_sprite(palette)
        self.rect = self.image.get_rect(center=owner.rect.center)

    def update(
        self,
        dt: float,
        enemies: Iterable[Enemy],
        projectiles: pygame.sprite.Group,
        damage_bonus: float = 0.0,
    ) -> None:
        if not self.owner or self.owner.hp <= 0:
            self.kill()
            return
        self.timer = max(0.0, self.timer - dt)
        if self.timer == 0:
            self.kill()
            return
        self.angle += dt * 2.4
        center = pygame.Vector2(self.owner.rect.center)
        offset = pygame.Vector2(math.cos(self.angle), math.sin(self.angle)) * self.orbit_radius
        self.rect.center = (int(center.x + offset.x), int(center.y + offset.y))
        self.cooldown = max(0.0, self.cooldown - dt)
        if self.cooldown > 0:
            return
        enemy_list = [enemy for enemy in enemies if enemy.alive()]
        if not enemy_list:
            return
        target = min(enemy_list, key=lambda e: pygame.Vector2(e.rect.center).distance_to(self.rect.center))
        direction = pygame.Vector2(target.rect.center) - pygame.Vector2(self.rect.center)
        if direction.length_squared() == 0:
            return
        projectile = Projectile(
            position=pygame.Vector2(self.rect.center),
            direction=direction.normalize(),
            speed=420,
            damage=self.damage * (1.0 + damage_bonus),
            color=RUN_COLORS["loot"],
        )
        projectiles.add(projectile)
        self.cooldown = self.fire_delay

