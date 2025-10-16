from __future__ import annotations

import math
import random

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
        self.stats = (upgraded_stats or character.stats).copy()
        self.max_hp = int(self.stats["max_hp"])
        self.hp = float(self.max_hp)
        self.speed = self.stats["speed"]
        self.damage_multiplier = self.stats["damage"]
        self.crit_chance = self.stats["crit"]
        self.focus_multiplier = self.stats["focus"]
        self.weapon.apply_modifiers(self.damage_multiplier, self.focus_multiplier)
        self.image = player_sprite(character.primary_color, character.secondary_color)
        self.rect = self.image.get_rect(center=position)
        self.velocity = pygame.Vector2(0, 0)
        self.invincible_timer = 0.0

    def update(self, dt: float) -> None:
        if self.invincible_timer > 0:
            self.invincible_timer = max(0.0, self.invincible_timer - dt)
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
        self.hp = max(0.0, self.hp - amount)
        self.invincible_timer = 0.6

    def heal(self, amount: float) -> None:
        self.hp = min(self.max_hp, self.hp + amount)


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
    def __init__(self, weapon_profile, position: pygame.Vector2):
        super().__init__()
        self.weapon_profile = weapon_profile
        self.image = pickup_sprite(RUN_COLORS["loot"])
        self.rect = self.image.get_rect(center=position)
        self.bounce_timer = 0.0
        self.base_y = float(self.rect.centery)

    def update(self, dt: float) -> None:
        self.bounce_timer += dt
        offset = math.sin(self.bounce_timer * 5) * 6
        self.rect.centery = int(self.base_y + offset)

