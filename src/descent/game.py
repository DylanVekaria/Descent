from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional

import pygame

from .art import player_sprite
from .character_data import CHARACTERS, CharacterProfile
from .constants import RUN_COLORS, SCREEN_HEIGHT, SCREEN_WIDTH, TARGET_FPS
from .enemy_data import ENEMIES, STAGE_MODIFIERS
from .entities import Enemy, Pickup, Player, Projectile
from .weapon import WeaponInstance
from .weapon_data import WEAPON_CATALOG, WeaponProfile, random_weapon


@dataclass
class WaveState:
    stage: int
    wave: int
    remaining_to_spawn: int
    alive_enemies: int


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Descent - Permutation Roguelite")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_large = pygame.font.Font(None, 64)

        self.characters: List[CharacterProfile] = CHARACTERS
        self.character_index = 0
        self.selected_character: Optional[CharacterProfile] = None
        self.state = "character_select"
        self.running = True

        self.player: Optional[Player] = None
        self.projectiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.pickups = pygame.sprite.Group()

        self.wave_state: Optional[WaveState] = None
        self.weapon_profile: WeaponProfile = random.choice(WEAPON_CATALOG)
        self.weapon_instance: Optional[WeaponInstance] = None
        self.stage_timer = 0.0
        self.kills = 0
        self.total_damage_dealt = 0.0
        self.total_damage_taken = 0.0
        self.pickup_cooldown = 0.0

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(TARGET_FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.state == "character_select":
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.character_index = (self.character_index + 1) % len(self.characters)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self.character_index = (self.character_index - 1) % len(self.characters)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.start_run(self.characters[self.character_index])
                elif self.state == "game_over" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.reset_to_select()

    def update(self, dt: float) -> None:
        if self.state == "character_select":
            return

        if self.state == "running" and self.player:
            keys = pygame.key.get_pressed()
            direction = pygame.Vector2(0, 0)
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                direction.y -= 1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                direction.y += 1
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                direction.x -= 1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                direction.x += 1
            self.player.move(direction)
            self.player.update(dt)
            if self.weapon_instance:
                self.weapon_instance.update(dt)

            # Keep player in bounds
            self.player.rect.clamp_ip(self.screen.get_rect().inflate(-80, -80))

            # Shooting
            mouse_pressed = pygame.mouse.get_pressed()[0]
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pressed and self.weapon_instance and self.weapon_instance.ready():
                direction = pygame.Vector2(mouse_pos) - pygame.Vector2(self.player.rect.center)
                if direction.length_squared() > 0:
                    self.weapon_instance.fire()
                    projectile = Projectile(
                        position=pygame.Vector2(self.player.rect.center),
                        direction=direction.normalize(),
                        speed=self.weapon_instance.profile.projectile_speed,
                        damage=self.weapon_instance.damage,
                        color=self.weapon_instance.profile.color,
                    )
                    self.projectiles.add(projectile)

            # Update projectiles
            for projectile in list(self.projectiles):
                projectile.update(dt)
                if not self.screen.get_rect().inflate(120, 120).colliderect(projectile.rect):
                    projectile.kill()

            # Update enemies
            for enemy in list(self.enemies):
                enemy.update(dt, pygame.Vector2(self.player.rect.center))
                if enemy.rect.colliderect(self.player.rect.inflate(-10, -10)):
                    self.player.take_damage(enemy.damage * dt * 0.6)
                    self.total_damage_taken += enemy.damage * dt * 0.6
                    if self.player.hp <= 0:
                        self.trigger_game_over()
                if not self.screen.get_rect().inflate(200, 200).colliderect(enemy.rect):
                    enemy.rect.clamp_ip(self.screen.get_rect().inflate(-120, -120))

            # Projectile collisions
            hits = pygame.sprite.groupcollide(self.enemies, self.projectiles, False, True)
            for enemy, projectiles in hits.items():
                damage = sum(p.damage for p in projectiles)
                enemy.take_damage(damage)
                self.total_damage_dealt += damage
                if enemy.hp <= 0:
                    enemy.kill()
                    self.kills += 1
                    if self.wave_state:
                        self.wave_state.alive_enemies -= 1
                    if random.random() < 0.25:
                        self.spawn_pickup(enemy.rect.center)
            if self.wave_state and self.wave_state.remaining_to_spawn > 0:
                self.stage_timer += dt
                if self.stage_timer >= 1.0:
                    self.stage_timer = 0.0
                    self.spawn_enemy_wave()

            if self.wave_state and self.wave_state.remaining_to_spawn <= 0 and len(self.enemies) == 0:
                self.advance_wave()

            # Pickups
            self.pickups.update(dt)
            self.pickup_cooldown = max(0.0, self.pickup_cooldown - dt)
            if keys[pygame.K_e] and self.pickup_cooldown == 0:
                pickup = pygame.sprite.spritecollideany(self.player, self.pickups)
                if pickup:
                    pickup.kill()
                    self.equip_weapon(pickup.weapon_profile)
                    self.pickup_cooldown = 0.4

    def draw(self) -> None:
        self.screen.fill(RUN_COLORS["void"])
        if self.state == "character_select":
            self.draw_character_select()
        elif self.state == "running":
            self.draw_arena()
            self.pickups.draw(self.screen)
            self.enemies.draw(self.screen)
            self.projectiles.draw(self.screen)
            if self.player:
                self.screen.blit(self.player.image, self.player.rect)
            self.draw_ui()
        elif self.state == "game_over":
            self.draw_arena()
            self.draw_game_over()
        pygame.display.flip()

    def draw_character_select(self) -> None:
        character = self.characters[self.character_index]
        title_surface = self.font_large.render("Select Your Diver", True, RUN_COLORS["ui_accent"])
        self.screen.blit(title_surface, title_surface.get_rect(center=(SCREEN_WIDTH // 2, 120)))

        sprite = player_sprite(character.primary_color, character.secondary_color)
        self.screen.blit(sprite, sprite.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)))

        name_surface = self.font_medium.render(f"{character.name} — {character.title}", True, RUN_COLORS["loot"])
        self.screen.blit(name_surface, name_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120)))

        desc_lines = wrap_text(character.description, self.font_small, SCREEN_WIDTH - 200)
        for i, line in enumerate(desc_lines):
            text = self.font_small.render(line, True, (220, 220, 220))
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + 170 + i * 22))

        prompt = self.font_small.render("←/→ to browse, Enter to deploy", True, (200, 200, 200))
        self.screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)))

    def draw_arena(self) -> None:
        floor_color = RUN_COLORS["floor"]
        wall_color = RUN_COLORS["wall"]
        pygame.draw.rect(self.screen, floor_color, pygame.Rect(80, 80, SCREEN_WIDTH - 160, SCREEN_HEIGHT - 160))
        pygame.draw.rect(self.screen, wall_color, pygame.Rect(60, 60, SCREEN_WIDTH - 120, SCREEN_HEIGHT - 120), 8)

    def draw_ui(self) -> None:
        if not self.player:
            return
        # Health bar
        ui_rect = pygame.Rect(30, 20, 400, 50)
        pygame.draw.rect(self.screen, RUN_COLORS["ui_bg"], ui_rect)
        hp_ratio = self.player.hp / self.player.max_hp
        pygame.draw.rect(
            self.screen,
            RUN_COLORS["player_secondary"],
            (ui_rect.x + 10, ui_rect.y + 10, int((ui_rect.width - 20) * hp_ratio), ui_rect.height - 20),
        )
        hp_text = self.font_small.render(f"Integrity {int(self.player.hp)}/{self.player.max_hp}", True, (255, 255, 255))
        self.screen.blit(hp_text, (ui_rect.x + 14, ui_rect.y + 14))

        # Weapon status
        weapon_rect = pygame.Rect(SCREEN_WIDTH - 430, 20, 400, 80)
        pygame.draw.rect(self.screen, RUN_COLORS["ui_bg"], weapon_rect)
        if self.weapon_instance:
            name_text = self.font_small.render(self.weapon_instance.profile.name, True, RUN_COLORS["loot"])
            self.screen.blit(name_text, (weapon_rect.x + 14, weapon_rect.y + 14))
            ammo_text = self.font_small.render(
                f"Ammo {self.weapon_instance.ammo}/{self.weapon_instance.profile.magazine}", True, (220, 220, 220)
            )
            self.screen.blit(ammo_text, (weapon_rect.x + 14, weapon_rect.y + 38))
            keyword_text = self.font_small.render(
                "Keywords: " + ", ".join(self.weapon_instance.profile.keywords[:4]),
                True,
                (180, 180, 180),
            )
            self.screen.blit(keyword_text, (weapon_rect.x + 14, weapon_rect.y + 58))

        # Stage info
        if self.wave_state:
            stage_text = self.font_small.render(
                f"Stage {self.wave_state.stage} • Wave {self.wave_state.wave} • Kills {self.kills}",
                True,
                (220, 220, 220),
            )
            self.screen.blit(stage_text, (30, 90))

        if pygame.sprite.spritecollideany(self.player, self.pickups):
            prompt = self.font_small.render("Press E to attune new weapon", True, RUN_COLORS["ui_accent"])
            self.screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)))

    def draw_game_over(self) -> None:
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        text = self.font_large.render("Run Lost", True, RUN_COLORS["danger"])
        self.screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)))
        stats_lines = [
            f"Stages cleared: {self.wave_state.stage - 1 if self.wave_state else 0}",
            f"Kills: {self.kills}",
            f"Damage dealt: {int(self.total_damage_dealt)}",
            f"Damage taken: {int(self.total_damage_taken)}",
        ]
        for i, line in enumerate(stats_lines):
            stat_text = self.font_medium.render(line, True, (230, 230, 230))
            self.screen.blit(stat_text, stat_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40 + i * 36)))
        prompt = self.font_small.render("Press Enter to recalibrate", True, (220, 220, 220))
        self.screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)))

    def start_run(self, character: CharacterProfile) -> None:
        self.selected_character = character
        self.weapon_profile = random_weapon()
        self.weapon_instance = WeaponInstance(self.weapon_profile, character.stats["damage"], character.stats["focus"])
        self.player = Player(character, self.weapon_instance, pygame.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.player_group = pygame.sprite.Group(self.player)
        self.projectiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.pickups = pygame.sprite.Group()
        self.wave_state = WaveState(stage=1, wave=1, remaining_to_spawn=0, alive_enemies=0)
        self.stage_timer = 0.0
        self.kills = 0
        self.total_damage_dealt = 0.0
        self.total_damage_taken = 0.0
        self.state = "running"
        self.spawn_wave()

    def spawn_wave(self) -> None:
        if not self.wave_state:
            return
        stage = self.wave_state.stage
        enemy_count = 5 + stage * 2
        self.wave_state.remaining_to_spawn = enemy_count
        self.wave_state.alive_enemies = enemy_count
        self.stage_timer = 0.0
        for _ in range(min(4, enemy_count)):
            self.spawn_enemy_wave()

    def spawn_enemy_wave(self) -> None:
        if not self.wave_state or self.wave_state.remaining_to_spawn <= 0:
            return
        profile = random.choice(ENEMIES)
        modifier = STAGE_MODIFIERS.get(self.wave_state.stage, STAGE_MODIFIERS[max(STAGE_MODIFIERS)])
        position = pygame.Vector2(
            random.randint(140, SCREEN_WIDTH - 140),
            random.randint(140, SCREEN_HEIGHT - 140),
        )
        enemy = Enemy(profile, modifier["hp"], position)
        enemy.speed *= modifier["speed"]
        enemy.damage *= modifier["damage"]
        self.enemies.add(enemy)
        self.wave_state.remaining_to_spawn -= 1

    def spawn_pickup(self, position) -> None:
        weapon_profile = random_weapon(exclude={self.weapon_instance.profile.name})
        pickup = Pickup(weapon_profile, pygame.Vector2(position))
        self.pickups.add(pickup)

    def advance_wave(self) -> None:
        if not self.wave_state:
            return
        self.wave_state.wave += 1
        if self.wave_state.wave > 3:
            self.wave_state.stage += 1
            self.wave_state.wave = 1
            self.player.heal(self.player.max_hp * 0.2)
        self.spawn_wave()

    def equip_weapon(self, profile: WeaponProfile) -> None:
        if not self.player:
            return
        self.weapon_profile = profile
        self.weapon_instance = WeaponInstance(profile, self.player.damage_multiplier, self.player.focus_multiplier)
        self.player.weapon = self.weapon_instance

    def trigger_game_over(self) -> None:
        self.state = "game_over"

    def reset_to_select(self) -> None:
        self.state = "character_select"
        self.player = None
        self.projectiles.empty()
        self.enemies.empty()
        self.pickups.empty()
        self.wave_state = None


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> List[str]:
    words = text.split()
    lines: List[str] = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

