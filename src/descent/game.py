from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import List, Optional

import pygame

from .art import player_sprite
from .character_data import CHARACTERS, CharacterProfile
from .constants import (
    COLOR_PALETTES,
    DIFFICULTY_PRESETS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TARGET_FPS,
    get_palette,
)
from .enemy_data import ENEMIES, STAGE_MODIFIERS
from .abilities import ABILITIES, AbilityProfile
from .achievements import ACHIEVEMENTS
from .entities import Enemy, Pickup, Player, Projectile, SupportDrone
from .meta import (
    UPGRADE_DEFINITIONS,
    apply_upgrades,
    award_credits,
    can_purchase_upgrade,
    load_progress,
    purchase_upgrade,
    record_run,
    update_settings,
    upgrade_summary,
)
from .relic_data import RelicProfile, random_relic
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
        self.progress = load_progress(self.characters)
        self.settings = self.progress.settings
        self.colors = get_palette(self.settings.color_profile)
        self.difficulty_profile = DIFFICULTY_PRESETS.get(
            self.settings.difficulty, DIFFICULTY_PRESETS["normal"]
        )
        self.meta_character_index = 0
        self.meta_category_index = 0
        self.meta_categories = list(UPGRADE_DEFINITIONS.keys())
        self.meta_message = ""
        self.meta_message_timer = 0.0
        self.selected_character: Optional[CharacterProfile] = None
        self.state = "main_menu"
        self.running = True
        self.main_menu_items = [
            ("Launch Expedition", self.enter_character_select),
            ("Dive Lab Upgrades", self.enter_meta_lab),
            ("Achievement Deck", self.enter_achievements),
            ("Command Console", self.enter_settings),
            ("Exit to Desktop", self.request_quit),
        ]
        self.main_menu_index = 0
        self.pause_menu_options = [
            ("Resume Dive", self.resume_run),
            ("Settings", self.enter_settings_from_pause),
            ("Abort Expedition", self.abort_to_main_menu),
        ]
        self.pause_index = 0
        self.settings_index = 0
        self.settings_items = [
            {"label": "Master Volume", "key": "master_volume", "type": "slider", "step": 0.05},
            {"label": "Music Volume", "key": "music_volume", "type": "slider", "step": 0.05},
            {"label": "Effects Volume", "key": "sfx_volume", "type": "slider", "step": 0.05},
            {
                "label": "Difficulty",
                "key": "difficulty",
                "type": "choices",
                "choices": list(DIFFICULTY_PRESETS.keys()),
            },
            {"label": "Screen Shake", "key": "screen_shake", "type": "toggle"},
            {"label": "Damage Numbers", "key": "damage_numbers", "type": "toggle"},
            {"label": "Auto Pause on Focus Loss", "key": "auto_pause", "type": "toggle"},
            {
                "label": "Color Profile",
                "key": "color_profile",
                "type": "choices",
                "choices": list(COLOR_PALETTES.keys()),
            },
            {"label": "Tutorial Prompts", "key": "show_tutorials", "type": "toggle"},
        ]
        self.achievements_scroll = 0
        self.achievement_notifications: List[tuple[str, float]] = []
        self.previous_state: Optional[str] = None
        self.settings_context = "main"

        self.player: Optional[Player] = None
        self.projectiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.pickups = pygame.sprite.Group()
        self.drones = pygame.sprite.Group()

        self.wave_state: Optional[WaveState] = None
        self.weapon_profile: WeaponProfile = random.choice(WEAPON_CATALOG)
        self.weapon_instance: Optional[WeaponInstance] = None
        self.stage_timer = 0.0
        self.kills = 0
        self.total_damage_dealt = 0.0
        self.total_damage_taken = 0.0
        self.pickup_cooldown = 0.0
        self.active_meta_levels: Optional[dict[str, int]] = None
        self.last_reward = 0
        self.combo_meter = 0
        self.combo_level = 0
        self.combo_timer = 0.0
        self.ability_timer = 0.0
        self.ability_cooldown_max = 0.0
        self.ability_flash_timer = 0.0
        self.ability_ready_notified = False
        self.run_message = ""
        self.run_message_timer = 0.0
        self.relics: List[RelicProfile] = []
        self.relic_effects: dict[str, float] = {}
        self.gravity_fields: List[dict[str, float]] = []
        self.dynamic_event_timer = 22.0
        self.elapsed_time = 0.0
        self.meta_drop_bonus = 0.0
        self.meta_bonus_reward = 0.0
        self.meta_starting_relics = 0
        self.highest_combo = 0
        self.ability_uses = 0
        self.relics_bound_run = 0
        self.weapons_synced_run = 0
        self.drones_deployed_run = 0
        self.reset_relic_effects()

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
                continue

            if self.state == "main_menu":
                self.handle_main_menu_event(event)
            elif self.state == "settings":
                self.handle_settings_event(event)
            elif self.state == "achievements":
                self.handle_achievements_event(event)
            elif self.state == "character_select":
                self.handle_character_select_event(event)
            elif self.state == "meta":
                self.handle_meta_event(event)
            elif self.state == "running":
                self.handle_running_event(event)
            elif self.state == "paused":
                self.handle_pause_event(event)
            elif self.state == "game_over":
                self.handle_game_over_event(event)

    def handle_main_menu_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_DOWN, pygame.K_s):
            self.main_menu_index = (self.main_menu_index + 1) % len(self.main_menu_items)
        elif event.key in (pygame.K_UP, pygame.K_w):
            self.main_menu_index = (self.main_menu_index - 1) % len(self.main_menu_items)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            _, action = self.main_menu_items[self.main_menu_index]
            action()
        elif event.key in (pygame.K_ESCAPE, pygame.K_q):
            self.request_quit()

    def handle_settings_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_ESCAPE, pygame.K_TAB):
            self.exit_settings()
            return
        if event.key in (pygame.K_DOWN, pygame.K_s):
            self.settings_index = (self.settings_index + 1) % len(self.settings_items)
            return
        if event.key in (pygame.K_UP, pygame.K_w):
            self.settings_index = (self.settings_index - 1) % len(self.settings_items)
            return
        item = self.settings_items[self.settings_index]
        key = item["key"]
        value = getattr(self.settings, key)
        if item["type"] == "slider" and event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
            delta = item.get("step", 0.05)
            if event.key in (pygame.K_LEFT, pygame.K_a):
                value = max(0.0, float(value) - delta)
            else:
                value = min(1.0, float(value) + delta)
            setattr(self.settings, key, value)
            self.apply_setting_update(key)
        elif item["type"] == "toggle" and event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d, pygame.K_RETURN, pygame.K_SPACE):
            setattr(self.settings, key, not bool(value))
            self.apply_setting_update(key)
        elif item["type"] == "choices" and event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
            choices = item.get("choices", [])
            if choices:
                index = choices.index(value) if value in choices else 0
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    index = (index - 1) % len(choices)
                else:
                    index = (index + 1) % len(choices)
                setattr(self.settings, key, choices[index])
                self.apply_setting_update(key)

    def handle_achievements_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_ESCAPE, pygame.K_TAB, pygame.K_BACKSPACE):
            self.state = self.previous_state or "main_menu"
            return
        max_scroll = max(0, len(ACHIEVEMENTS) - 7)
        if event.key in (pygame.K_DOWN, pygame.K_s):
            self.achievements_scroll = min(max_scroll, self.achievements_scroll + 1)
        elif event.key in (pygame.K_UP, pygame.K_w):
            self.achievements_scroll = max(0, self.achievements_scroll - 1)

    def handle_character_select_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_RIGHT, pygame.K_d):
            self.character_index = (self.character_index + 1) % len(self.characters)
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            self.character_index = (self.character_index - 1) % len(self.characters)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.start_run(self.characters[self.character_index])
        elif event.key in (pygame.K_u, pygame.K_TAB):
            self.enter_meta_lab()
        elif event.key == pygame.K_ESCAPE:
            self.state = "main_menu"

    def handle_meta_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_ESCAPE, pygame.K_TAB):
            self.state = "character_select"
            return
        if event.key in (pygame.K_RIGHT, pygame.K_d):
            self.meta_character_index = (self.meta_character_index + 1) % len(self.characters)
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            self.meta_character_index = (self.meta_character_index - 1) % len(self.characters)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.meta_category_index = (self.meta_category_index + 1) % len(self.meta_categories)
        elif event.key in (pygame.K_UP, pygame.K_w):
            self.meta_category_index = (self.meta_category_index - 1) % len(self.meta_categories)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.purchase_selected_upgrade()

    def handle_running_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_q:
            self.try_activate_ability()
        elif event.key == pygame.K_ESCAPE:
            self.pause_index = 0
            self.previous_state = "running"
            self.state = "paused"

    def handle_pause_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_ESCAPE, pygame.K_TAB):
            self.resume_run()
            return
        if event.key in (pygame.K_DOWN, pygame.K_s):
            self.pause_index = (self.pause_index + 1) % len(self.pause_menu_options)
        elif event.key in (pygame.K_UP, pygame.K_w):
            self.pause_index = (self.pause_index - 1) % len(self.pause_menu_options)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            _, action = self.pause_menu_options[self.pause_index]
            action()

    def handle_game_over_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.reset_to_select()

    def enter_character_select(self) -> None:
        self.previous_state = "main_menu"
        self.reset_to_select()

    def enter_meta_lab(self) -> None:
        self.previous_state = self.state
        self.state = "meta"
        if self.previous_state == "character_select":
            self.meta_character_index = self.character_index

    def enter_achievements(self) -> None:
        self.previous_state = self.state
        self.state = "achievements"
        self.achievements_scroll = 0

    def enter_settings(self) -> None:
        self.previous_state = self.state
        self.settings_context = "main"
        self.state = "settings"

    def enter_settings_from_pause(self) -> None:
        self.previous_state = "paused"
        self.settings_context = "pause"
        self.state = "settings"

    def resume_run(self) -> None:
        self.state = "running"
        self.previous_state = None

    def abort_to_main_menu(self) -> None:
        self.reset_to_select()
        self.state = "main_menu"
        self.previous_state = None

    def request_quit(self) -> None:
        self.running = False

    def exit_settings(self) -> None:
        if self.settings_context == "pause":
            self.state = "paused"
        elif self.previous_state:
            self.state = self.previous_state
        else:
            self.state = "main_menu"
        self.settings_context = "main"

    def apply_setting_update(self, key: str) -> None:
        value = getattr(self.settings, key)
        update_settings(self.progress, key, value)
        if key == "difficulty":
            self.difficulty_profile = DIFFICULTY_PRESETS.get(value, DIFFICULTY_PRESETS["normal"])
        elif key == "color_profile":
            self.colors = get_palette(str(value))

    def update_notifications(self, dt: float) -> None:
        if not self.achievement_notifications:
            return
        updated: List[tuple[str, float]] = []
        for text, timer in self.achievement_notifications:
            timer -= dt
            if timer > 0:
                updated.append((text, timer))
        self.achievement_notifications = updated

    def push_achievement_toast(self, text: str) -> None:
        self.achievement_notifications.append((text, 4.0))

    def update(self, dt: float) -> None:
        if self.meta_message_timer > 0:
            self.meta_message_timer = max(0.0, self.meta_message_timer - dt)
        if self.run_message_timer > 0:
            self.run_message_timer = max(0.0, self.run_message_timer - dt)
            if self.run_message_timer == 0:
                self.run_message = ""

        self.update_notifications(dt)

        if self.state in {"character_select", "meta", "main_menu", "settings", "achievements"}:
            return

        if self.state == "paused":
            return

        if self.state == "running" and self.player:
            self.elapsed_time += dt
            ability_haste = 1.0 + self.relic_effects.get("ability_haste", 0.0)
            self.ability_timer = max(0.0, self.ability_timer - dt * ability_haste)
            if self.ability_timer == 0 and self.ability_cooldown_max > 0 and not self.ability_ready_notified:
                self.push_run_message("Ability ready!", 1.4)
                self.ability_ready_notified = True
            self.update_combo(dt)
            self.update_dynamic_events(dt)
            self.update_fields(dt)

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

            self.player.rect.clamp_ip(self.screen.get_rect().inflate(-80, -80))

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

            for projectile in list(self.projectiles):
                projectile.update(dt)
                if not self.screen.get_rect().inflate(120, 120).colliderect(projectile.rect):
                    projectile.kill()

            drone_bonus = self.relic_effects.get("drone_damage", 0.0)
            for drone in list(self.drones):
                drone.update(dt, self.enemies, self.projectiles, drone_bonus)

            player_pos = pygame.Vector2(self.player.rect.center)
            for enemy in list(self.enemies):
                slow_factor = self.compute_slow_for_enemy(enemy)
                base_speed = enemy.speed
                enemy.speed = base_speed * slow_factor
                enemy.update(dt, player_pos)
                enemy.speed = base_speed
                self.tick_enemy_status(enemy, dt)
                if enemy.rect.colliderect(self.player.rect.inflate(-10, -10)):
                    damage = enemy.damage * dt * 0.6
                    if self.combo_level > 0:
                        damage *= max(0.2, 1.0 - self.relic_effects.get("combo_shield", 0.0))
                    self.player.take_damage(damage)
                    self.total_damage_taken += damage
                    if self.player.hp <= 0:
                        self.trigger_game_over()
                if not self.screen.get_rect().inflate(200, 200).colliderect(enemy.rect):
                    enemy.rect.clamp_ip(self.screen.get_rect().inflate(-120, -120))

            hits = pygame.sprite.groupcollide(self.enemies, self.projectiles, False, True)
            combo_multiplier = 1.0 + self.combo_level * 0.05
            for enemy, projectiles in hits.items():
                damage = sum(p.damage for p in projectiles) * combo_multiplier
                enemy.take_damage(damage)
                self.total_damage_dealt += damage
                pull_strength = self.relic_effects.get("gravity_rounds", 0.0)
                if pull_strength > 0 and self.player:
                    to_player = player_pos - pygame.Vector2(enemy.rect.center)
                    if to_player.length_squared() > 0:
                        enemy.rect.centerx += int(to_player.x * 0.03 * pull_strength)
                        enemy.rect.centery += int(to_player.y * 0.03 * pull_strength)
                if enemy.hp <= 0:
                    self.handle_enemy_defeat(enemy)

            if self.wave_state and self.wave_state.remaining_to_spawn > 0:
                self.stage_timer += dt
                if self.stage_timer >= 1.0:
                    self.stage_timer = 0.0
                    self.spawn_enemy_wave()

            if self.wave_state and self.wave_state.remaining_to_spawn <= 0 and len(self.enemies) == 0:
                self.advance_wave()

            self.pickups.update(dt)
            self.pickup_cooldown = max(0.0, self.pickup_cooldown - dt)
            if keys[pygame.K_e] and self.pickup_cooldown == 0:
                pickup = pygame.sprite.spritecollideany(self.player, self.pickups)
                if pickup:
                    pickup.kill()
                    if pickup.pickup_type == "weapon":
                        self.equip_weapon(pickup.payload)
                        if self.relic_effects.get("pickup_speed", 0.0) > 0:
                            self.player.reset_pickup_speed(
                                self.relic_effects["pickup_speed"],
                                8.0,
                            )
                    elif pickup.pickup_type == "relic":
                        self.attune_relic(pickup.payload)
                    self.pickup_cooldown = 0.4

    def draw(self) -> None:
        if self.state == "main_menu":
            self.draw_main_menu()
        elif self.state == "settings":
            self.draw_settings()
        elif self.state == "achievements":
            self.draw_achievements()
        elif self.state == "character_select":
            self.screen.fill(self.colors["void"])
            self.draw_character_select()
        elif self.state == "running":
            self.draw_arena()
            self.pickups.draw(self.screen)
            self.enemies.draw(self.screen)
            self.drones.draw(self.screen)
            self.projectiles.draw(self.screen)
            if self.player:
                self.screen.blit(self.player.image, self.player.rect)
            self.draw_ui()
            self.draw_achievement_toasts()
        elif self.state == "paused":
            self.draw_arena()
            self.pickups.draw(self.screen)
            self.enemies.draw(self.screen)
            self.drones.draw(self.screen)
            self.projectiles.draw(self.screen)
            if self.player:
                self.screen.blit(self.player.image, self.player.rect)
            self.draw_ui(dimmed=True)
            self.draw_pause_menu()
            self.draw_achievement_toasts()
        elif self.state == "meta":
            self.draw_meta_progression()
        elif self.state == "game_over":
            self.draw_arena()
            self.draw_game_over()
            self.draw_achievement_toasts()
        pygame.display.flip()

    def draw_character_select(self) -> None:
        character = self.characters[self.character_index]
        title_surface = self.font_large.render("Select Your Diver", True, self.colors["ui_accent"])
        self.screen.blit(title_surface, title_surface.get_rect(center=(SCREEN_WIDTH // 2, 120)))

        sprite = player_sprite(character.primary_color, character.secondary_color)
        self.screen.blit(sprite, sprite.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)))

        name_surface = self.font_medium.render(f"{character.name} — {character.title}", True, self.colors["loot"])
        self.screen.blit(name_surface, name_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120)))

        desc_lines = wrap_text(character.description, self.font_small, SCREEN_WIDTH - 200)
        for i, line in enumerate(desc_lines):
            text = self.font_small.render(line, True, (220, 220, 220))
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + 170 + i * 22))

        ability = ABILITIES[character.ability_key]
        ability_title = self.font_small.render(f"Ability: {ability.name}", True, self.colors["ui_accent"])
        self.screen.blit(ability_title, ability_title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 240)))
        ability_lines = wrap_text(ability.description, self.font_small, SCREEN_WIDTH - 240)
        for i, line in enumerate(ability_lines[:3]):
            desc = self.font_small.render(line, True, (200, 200, 200))
            self.screen.blit(desc, (SCREEN_WIDTH // 2 - desc.get_width() // 2, SCREEN_HEIGHT // 2 + 260 + i * 20))
        ability_hint = self.font_small.render(character.ability_summary, True, (160, 160, 160))
        self.screen.blit(ability_hint, ability_hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 330)))

        prompt = self.font_small.render("←/→ to browse, Enter to deploy", True, (200, 200, 200))
        self.screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)))
        upgrade_prompt = self.font_small.render("Press U/Tab for Dive Lab Upgrades", True, self.colors["ui_accent"])
        self.screen.blit(upgrade_prompt, upgrade_prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)))
        self.draw_achievement_toasts()

    def draw_main_menu(self) -> None:
        self.screen.fill(self.colors["void"])
        title = self.font_large.render("DESCENT", True, self.colors["ui_accent"])
        subtitle = self.font_small.render("Permutation Protocol", True, (200, 200, 200))
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 120)))
        self.screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 170)))

        for idx, (label, _) in enumerate(self.main_menu_items):
            rect = pygame.Rect(SCREEN_WIDTH // 2 - 240, 240 + idx * 70, 480, 58)
            pygame.draw.rect(self.screen, self.colors["ui_bg"], rect, border_radius=10)
            if idx == self.main_menu_index:
                pygame.draw.rect(self.screen, self.colors["ui_accent"], rect, 3, border_radius=10)
            text_color = self.colors["loot"] if idx == self.main_menu_index else (210, 210, 210)
            text = self.font_medium.render(label, True, text_color)
            self.screen.blit(text, text.get_rect(center=rect.center))

        stats = self.progress.statistics
        stats_lines = [
            f"Runs logged: {int(stats.get('runs_played', 0))}",
            f"Lifetime kills: {int(stats.get('total_kills', 0))}",
            f"Highest combo: {int(stats.get('highest_combo', 0))}",
            f"Deepest stage: {int(stats.get('deepest_stage', 0))}",
            f"Achievements: {int(stats.get('achievements_unlocked', 0))}/{len(ACHIEVEMENTS)}",
        ]
        for idx, line in enumerate(stats_lines):
            stat = self.font_small.render(line, True, (200, 200, 200))
            self.screen.blit(stat, (60, 260 + idx * 26))

        difficulty = self.font_small.render(
            f"Difficulty: {self.settings.difficulty.title()}  •  Palette: {self.settings.color_profile.replace('_', ' ').title()}",
            True,
            (190, 190, 190),
        )
        self.screen.blit(difficulty, difficulty.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)))
        self.draw_achievement_toasts()

    def draw_settings(self) -> None:
        self.screen.fill(self.colors["void"])
        title = self.font_large.render("Command Console", True, self.colors["ui_accent"])
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 90)))

        for idx, item in enumerate(self.settings_items):
            rect = pygame.Rect(SCREEN_WIDTH // 2 - 340, 180 + idx * 70, 680, 60)
            pygame.draw.rect(self.screen, self.colors["ui_bg"], rect, border_radius=10)
            if idx == self.settings_index:
                pygame.draw.rect(self.screen, self.colors["ui_accent"], rect, 3, border_radius=10)

            value = getattr(self.settings, item["key"])
            if item["type"] == "slider":
                display = f"{int(float(value) * 100)}%"
            elif item["type"] == "toggle":
                display = "On" if value else "Off"
            else:
                display = str(value).replace("_", " ").title()

            label = self.font_medium.render(item["label"], True, (220, 220, 220))
            value_surface = self.font_medium.render(display, True, self.colors["loot"])
            self.screen.blit(label, (rect.x + 20, rect.y + 14))
            self.screen.blit(value_surface, value_surface.get_rect(right=rect.right - 20, centery=rect.centery))

        hint = self.font_small.render("Enter to adjust • Esc to exit", True, (180, 180, 180))
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)))
        self.draw_achievement_toasts()

    def draw_achievements(self) -> None:
        self.screen.fill(self.colors["void"])
        title = self.font_large.render("Achievement Deck", True, self.colors["ui_accent"])
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 90)))

        achievements_list = list(ACHIEVEMENTS.values())
        visible_rows = 7
        max_scroll = max(0, len(achievements_list) - visible_rows)
        start = min(self.achievements_scroll, max_scroll)
        for idx in range(visible_rows):
            index = start + idx
            if index >= len(achievements_list):
                break
            achievement = achievements_list[index]
            record = self.progress.achievements.get(achievement.key)
            unlocked = record.unlocked if record else False
            rect = pygame.Rect(140, 180 + idx * 80, SCREEN_WIDTH - 280, 70)
            pygame.draw.rect(self.screen, self.colors["ui_bg"], rect, border_radius=12)
            if unlocked:
                pygame.draw.rect(self.screen, self.colors["loot"], rect, 2, border_radius=12)
            name_color = self.colors["loot"] if unlocked else (210, 210, 210)
            name = self.font_medium.render(achievement.name, True, name_color)
            self.screen.blit(name, (rect.x + 20, rect.y + 10))
            desc = self.font_small.render(achievement.description, True, (190, 190, 190))
            self.screen.blit(desc, (rect.x + 20, rect.y + 38))
            reward_text = self.font_small.render(
                f"Reward: {achievement.reward_credits} Aether",
                True,
                self.colors["ui_accent"] if unlocked else (160, 160, 160),
            )
            self.screen.blit(reward_text, reward_text.get_rect(right=rect.right - 20, centery=rect.centery))

        instructions = self.font_small.render("↑/↓ scroll • Esc to return", True, (190, 190, 190))
        self.screen.blit(instructions, instructions.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)))
        self.draw_achievement_toasts()

    def draw_pause_menu(self) -> None:
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))
        title = self.font_large.render("Paused", True, self.colors["ui_accent"])
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 140)))
        for idx, (label, _) in enumerate(self.pause_menu_options):
            rect = pygame.Rect(SCREEN_WIDTH // 2 - 220, 240 + idx * 70, 440, 58)
            pygame.draw.rect(self.screen, self.colors["ui_bg"], rect, border_radius=10)
            if idx == self.pause_index:
                pygame.draw.rect(self.screen, self.colors["ui_accent"], rect, 3, border_radius=10)
            text_color = self.colors["loot"] if idx == self.pause_index else (210, 210, 210)
            text = self.font_medium.render(label, True, text_color)
            self.screen.blit(text, text.get_rect(center=rect.center))

    def draw_achievement_toasts(self) -> None:
        if not self.achievement_notifications:
            return
        for idx, (text, timer) in enumerate(self.achievement_notifications[:3]):
            alpha = max(80, min(220, int(255 * (timer / 4.0))))
            rect = pygame.Rect(SCREEN_WIDTH // 2 - 260, 80 + idx * 70, 520, 54)
            toast = pygame.Surface(rect.size, pygame.SRCALPHA)
            toast.fill((*self.colors["ui_bg"], alpha))
            self.screen.blit(toast, rect)
            pygame.draw.rect(self.screen, self.colors["ui_accent"], rect, 2, border_radius=12)
            label = self.font_small.render(text, True, self.colors["loot"])
            self.screen.blit(label, label.get_rect(center=rect.center))

    def draw_arena(self) -> None:
        self.screen.fill(self.colors["void"])
        floor_color = self.colors["floor"]
        wall_color = self.colors["wall"]
        pygame.draw.rect(self.screen, floor_color, pygame.Rect(80, 80, SCREEN_WIDTH - 160, SCREEN_HEIGHT - 160))
        pygame.draw.rect(self.screen, wall_color, pygame.Rect(60, 60, SCREEN_WIDTH - 120, SCREEN_HEIGHT - 120), 8)
        for field in self.gravity_fields:
            position = (int(field["position"].x), int(field["position"].y))
            radius = int(field["radius"])
            pygame.draw.circle(self.screen, self.colors["field"], position, radius, 2)

    def draw_ui(self, dimmed: bool = False) -> None:
        if not self.player:
            return
        # Health bar
        ui_rect = pygame.Rect(30, 20, 400, 50)
        pygame.draw.rect(self.screen, self.colors["ui_bg"], ui_rect)
        hp_ratio = self.player.hp / self.player.max_hp
        pygame.draw.rect(
            self.screen,
            self.colors["player_secondary"],
            (ui_rect.x + 10, ui_rect.y + 10, int((ui_rect.width - 20) * hp_ratio), ui_rect.height - 20),
        )
        hp_text = self.font_small.render(f"Integrity {int(self.player.hp)}/{self.player.max_hp}", True, (255, 255, 255))
        self.screen.blit(hp_text, (ui_rect.x + 14, ui_rect.y + 14))
        if self.player.shield > 0:
            shield_ratio = min(1.0, self.player.shield / max(1, self.player.max_hp))
            shield_width = int((ui_rect.width - 20) * shield_ratio)
            pygame.draw.rect(
                self.screen,
                self.colors["shield"],
                (ui_rect.x + 10, ui_rect.y + 10, shield_width, ui_rect.height - 20),
                2,
            )

        # Weapon status
        weapon_rect = pygame.Rect(SCREEN_WIDTH - 430, 20, 400, 80)
        pygame.draw.rect(self.screen, self.colors["ui_bg"], weapon_rect)
        if self.weapon_instance:
            name_text = self.font_small.render(self.weapon_instance.profile.name, True, self.colors["loot"])
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

        if self.active_meta_levels:
            meta_parts = []
            for key in self.meta_categories:
                level = self.active_meta_levels.get(key, 0)
                meta_parts.append(f"{key[:3].title()} {level}")
            meta_text = self.font_small.render("Meta " + "  ".join(meta_parts), True, (180, 180, 180))
            self.screen.blit(meta_text, (30, 120))

        ability_rect = pygame.Rect(30, SCREEN_HEIGHT - 90, 260, 60)
        pygame.draw.rect(self.screen, self.colors["ui_bg"], ability_rect)
        if self.selected_character:
            ability = ABILITIES[self.selected_character.ability_key]
            ready = self.ability_timer == 0
            ratio = 0.0
            if self.ability_cooldown_max > 0:
                ratio = self.ability_timer / self.ability_cooldown_max
            if ratio > 0:
                pygame.draw.rect(
                    self.screen,
                    self.colors["cooldown"],
                    (
                        ability_rect.x + 10,
                        ability_rect.y + 10,
                        int((ability_rect.width - 20) * (1 - ratio)),
                        ability_rect.height - 20,
                    ),
                )
            label_color = self.colors["ui_accent"] if ready else (200, 200, 200)
            ability_name = self.font_small.render(f"{ability.name}", True, label_color)
            self.screen.blit(ability_name, (ability_rect.x + 16, ability_rect.y + 14))
            ability_hint = self.font_small.render("Q — Signature", True, (160, 160, 160))
            self.screen.blit(ability_hint, (ability_rect.x + 16, ability_rect.y + 36))

        combo_rect = pygame.Rect(320, 20, 180, 50)
        pygame.draw.rect(self.screen, self.colors["ui_bg"], combo_rect)
        combo_text = self.font_small.render(f"Combo {self.combo_meter} x{self.combo_level}", True, self.colors["combo"])
        self.screen.blit(combo_text, (combo_rect.x + 16, combo_rect.y + 16))

        relic_rect = pygame.Rect(SCREEN_WIDTH - 430, 110, 400, 150)
        pygame.draw.rect(self.screen, self.colors["ui_bg"], relic_rect)
        relic_header = self.font_small.render(f"Relics {len(self.relics)}", True, self.colors["loot"])
        self.screen.blit(relic_header, (relic_rect.x + 14, relic_rect.y + 12))
        for idx, relic in enumerate(self.relics[-5:]):
            relic_text = self.font_small.render(relic.name, True, (200, 200, 200))
            self.screen.blit(relic_text, (relic_rect.x + 14, relic_rect.y + 34 + idx * 22))

        pickup = pygame.sprite.spritecollideany(self.player, self.pickups)
        if pickup:
            if pickup.pickup_type == "weapon":
                text = "Press E to attune new weapon"
            else:
                text = "Press E to bind relic"
            prompt = self.font_small.render(text, True, self.colors["ui_accent"])
            self.screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)))

        if self.run_message_timer > 0 and self.run_message:
            message = self.font_small.render(self.run_message, True, self.colors["ui_accent"])
            self.screen.blit(message, message.get_rect(center=(SCREEN_WIDTH // 2, 80)))

        if dimmed:
            veil = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            veil.fill((0, 0, 0, 120))
            self.screen.blit(veil, (0, 0))

    def draw_game_over(self) -> None:
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        text = self.font_large.render("Run Lost", True, self.colors["danger"])
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
        reward_line = f"Aether stored: +{self.last_reward} (Total {self.progress.credits})"
        reward_text = self.font_small.render(reward_line, True, self.colors["loot"])
        self.screen.blit(reward_text, reward_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200)))
        prompt = self.font_small.render("Press Enter to recalibrate", True, (220, 220, 220))
        self.screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)))

    def start_run(self, character: CharacterProfile) -> None:
        self.selected_character = character
        self.reset_relic_effects()
        self.weapon_profile = random_weapon()
        upgraded_stats = apply_upgrades(character, self.progress)
        self.meta_drop_bonus = upgraded_stats.get("drop_bonus", 0.0)
        self.meta_bonus_reward = upgraded_stats.get("bonus_credits", 0.0)
        self.meta_starting_relics = int(upgraded_stats.get("starting_relics", 0))
        self.weapon_instance = WeaponInstance(
            self.weapon_profile,
            upgraded_stats.get("damage", character.stats["damage"]),
            upgraded_stats.get("focus", character.stats["focus"]),
        )
        self.player = Player(
            character,
            self.weapon_instance,
            pygame.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            upgraded_stats=upgraded_stats,
        )
        self.player_group = pygame.sprite.Group(self.player)
        self.projectiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.pickups = pygame.sprite.Group()
        self.drones = pygame.sprite.Group()
        self.wave_state = WaveState(stage=1, wave=1, remaining_to_spawn=0, alive_enemies=0)
        self.stage_timer = 0.0
        self.kills = 0
        self.total_damage_dealt = 0.0
        self.total_damage_taken = 0.0
        self.pickup_cooldown = 0.0
        self.combo_meter = 0
        self.combo_level = 0
        self.combo_timer = 0.0
        self.ability_timer = 0.0
        self.ability_cooldown_max = 0.0
        self.ability_ready_notified = False
        self.run_message = ""
        self.run_message_timer = 0.0
        self.gravity_fields = []
        self.dynamic_event_timer = 18.0
        self.elapsed_time = 0.0
        self.state = "running"
        self.active_meta_levels = upgrade_summary(character, self.progress)
        self.last_reward = 0
        self.highest_combo = 0
        self.ability_uses = 0
        self.relics_bound_run = 0
        self.weapons_synced_run = 0
        self.drones_deployed_run = 0
        self.spawn_wave()
        if self.meta_starting_relics > 0:
            for _ in range(self.meta_starting_relics):
                self.attune_relic(random_relic(exclude={r.key for r in self.relics}))
        self.push_run_message("Dive initialized", 2.0)

    def spawn_wave(self) -> None:
        if not self.wave_state:
            return
        stage = self.wave_state.stage
        base_count = 5 + stage * 2
        spawn_rate = self.difficulty_profile.get("spawn_rate", 1.0)
        enemy_count = max(3, int(round(base_count * spawn_rate)))
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
        diff = self.difficulty_profile
        hp_mod = modifier["hp"] * diff.get("enemy_hp", 1.0)
        speed_mod = modifier["speed"] * diff.get("enemy_speed", 1.0)
        damage_mod = modifier["damage"] * diff.get("enemy_damage", 1.0)
        enemy = Enemy(profile, hp_mod, position)
        enemy.speed = profile.speed * speed_mod
        enemy.damage = profile.damage * damage_mod
        self.enemies.add(enemy)
        self.wave_state.remaining_to_spawn -= 1

    def spawn_pickup(self, position) -> None:
        exclude = {self.weapon_instance.profile.name} if self.weapon_instance else set()
        weapon_profile = random_weapon(exclude=exclude)
        pickup = Pickup("weapon", weapon_profile, pygame.Vector2(position), self.colors["loot"])
        self.pickups.add(pickup)

    def spawn_relic(self, position) -> None:
        relic = random_relic(exclude={r.key for r in self.relics})
        pickup = Pickup("relic", relic, pygame.Vector2(position), self.colors["relic"])
        self.pickups.add(pickup)

    def advance_wave(self) -> None:
        if not self.wave_state:
            return
        self.wave_state.wave += 1
        if self.wave_state.wave > 3:
            self.wave_state.stage += 1
            self.wave_state.wave = 1
        heal_ratio = 0.2 + self.relic_effects.get("wave_heal", 0.0)
        self.player.heal(self.player.max_hp * heal_ratio)
        self.push_run_message(f"Wave cleared! Integrity +{int(heal_ratio * 100)}%", 1.4)
        self.spawn_wave()

    def equip_weapon(self, profile: WeaponProfile) -> None:
        if not self.player:
            return
        self.weapon_profile = profile
        self.weapon_instance = WeaponInstance(profile, self.player.damage_multiplier, self.player.focus_multiplier)
        self.player.weapon = self.weapon_instance
        self.player.refresh_stats()
        self.push_run_message(f"Attuned {profile.name}", 1.2)
        self.weapons_synced_run += 1

    def trigger_game_over(self) -> None:
        reward = int(
            self.kills * 3
            + (self.wave_state.stage if self.wave_state else 0) * 40
            + self.total_damage_dealt * 0.02
        )
        reward = max(25, reward)
        reward += int(self.meta_bonus_reward)
        reward += int(self.relic_effects.get("bonus_credits", 0.0))
        reward = int(reward * self.difficulty_profile.get("reward", 1.0))
        self.last_reward = reward
        award_credits(self.progress, reward)
        run_stats = {
            "kills": self.kills,
            "damage_dealt": self.total_damage_dealt,
            "damage_taken": self.total_damage_taken,
            "relics": self.relics_bound_run,
            "weapons": self.weapons_synced_run,
            "combo": self.highest_combo,
            "duration": self.elapsed_time,
            "stage": self.wave_state.stage if self.wave_state else 0,
            "credits": reward,
            "ability_uses": self.ability_uses,
        }
        unlocks = record_run(self.progress, run_stats)
        for achievement in unlocks:
            toast = f"{achievement.name} unlocked! +{achievement.reward_credits} Aether"
            self.push_achievement_toast(toast)
        self.state = "game_over"

    def push_run_message(self, text: str, duration: float = 1.6) -> None:
        self.run_message = text
        self.run_message_timer = duration

    def update_combo(self, dt: float) -> None:
        if self.combo_timer > 0:
            self.combo_timer = max(0.0, self.combo_timer - dt)
            if self.combo_timer == 0:
                self.combo_meter = 0
                self.combo_level = 0
        shield_ratio = self.relic_effects.get("combo_shield", 0.0)
        if self.combo_level > 0 and shield_ratio > 0 and self.player:
            desired = self.player.max_hp * shield_ratio
            if self.player.shield < desired:
                self.player.grant_shield(desired - self.player.shield)

    def update_dynamic_events(self, dt: float) -> None:
        rate = 1.0 + self.relic_effects.get("event_rate", 0.0)
        self.dynamic_event_timer -= dt * rate
        if self.dynamic_event_timer <= 0:
            self.trigger_dynamic_event()
            self.dynamic_event_timer = random.uniform(24.0, 38.0)

    def trigger_dynamic_event(self) -> None:
        if not self.player:
            return
        arena = pygame.Rect(120, 120, SCREEN_WIDTH - 240, SCREEN_HEIGHT - 240)
        event = random.choices(
            ["supply_drop", "relic_cache", "heal_field", "stasis"],
            weights=[4, 2, 3, 2],
        )[0]
        if event == "supply_drop":
            for _ in range(2):
                position = (
                    random.randint(arena.left, arena.right),
                    random.randint(arena.top, arena.bottom),
                )
                self.spawn_pickup(position)
            self.push_run_message("Supply drop located!", 2.0)
        elif event == "relic_cache":
            position = (
                random.randint(arena.left, arena.right),
                random.randint(arena.top, arena.bottom),
            )
            self.spawn_relic(position)
            self.push_run_message("Relic cache detected!", 2.0)
        elif event == "heal_field":
            self.player.heal(self.player.max_hp * 0.18)
            self.push_run_message("Restorative surge released!", 2.0)
        elif event == "stasis":
            field = {
                "position": pygame.Vector2(self.player.rect.center),
                "radius": 260.0,
                "slow": 0.45,
                "duration": 6.0,
            }
            self.gravity_fields.append(field)
            self.push_run_message("Temporal field deployed.", 2.0)

    def update_fields(self, dt: float) -> None:
        remaining: List[dict[str, float]] = []
        for field in self.gravity_fields:
            field["duration"] -= dt
            if field["duration"] > 0:
                remaining.append(field)
        self.gravity_fields = remaining

    def tick_enemy_status(self, enemy: Enemy, dt: float) -> None:
        ignite_timer = getattr(enemy, "ignite_timer", 0.0)
        if ignite_timer > 0:
            burn_damage = getattr(enemy, "ignite_damage", 0.0) * (1.0 + self.relic_effects.get("burn_bonus", 0.0))
            enemy.take_damage(burn_damage * dt)
            self.total_damage_dealt += burn_damage * dt
            enemy.ignite_timer = max(0.0, ignite_timer - dt)
            if enemy.hp <= 0:
                self.handle_enemy_defeat(enemy)
                return
        if hasattr(enemy, "temp_slow_timer") and enemy.temp_slow_timer > 0:
            enemy.temp_slow_timer = max(0.0, enemy.temp_slow_timer - dt)
        if hasattr(enemy, "stun_timer") and enemy.stun_timer > 0:
            enemy.stun_timer = max(0.0, enemy.stun_timer - dt)

    def compute_slow_for_enemy(self, enemy: Enemy) -> float:
        if hasattr(enemy, "stun_timer") and enemy.stun_timer > 0:
            return 0.0
        slow = 1.0
        if hasattr(enemy, "temp_slow_timer") and enemy.temp_slow_timer > 0:
            slow *= getattr(enemy, "temp_slow_factor", 0.6)
        enemy_pos = pygame.Vector2(enemy.rect.center)
        for field in self.gravity_fields:
            if enemy_pos.distance_to(field["position"]) <= field["radius"]:
                slow *= max(0.25, 1.0 - field["slow"])
        return max(0.1, slow)

    def handle_enemy_defeat(self, enemy: Enemy) -> None:
        enemy.kill()
        self.kills += 1
        if self.wave_state:
            self.wave_state.alive_enemies -= 1
        self.combo_meter += 1
        self.highest_combo = max(self.highest_combo, self.combo_meter)
        self.combo_timer = 5.0 + self.relic_effects.get("combo_extend", 0.0)
        new_level = max(self.combo_level, self.combo_meter // 10)
        if new_level > self.combo_level:
            self.combo_level = new_level
            self.push_run_message(f"Combo Tier {self.combo_level}!", 1.2)
        drop_chance = min(0.9, 0.25 + 0.05 * self.combo_level + self.meta_drop_bonus)
        if random.random() < drop_chance:
            self.spawn_pickup(enemy.rect.center)
        relic_chance = min(0.45, 0.1 + 0.03 * self.combo_level)
        if random.random() < relic_chance:
            self.spawn_relic(enemy.rect.center)
        if self.relic_effects.get("combo_drop", 0.0) > 0 and self.combo_level and self.combo_level % 5 == 0:
            self.spawn_pickup(enemy.rect.center)

    def try_activate_ability(self) -> None:
        if self.state != "running" or not self.player or not self.selected_character:
            return
        if self.ability_timer > 0:
            self.push_run_message("Ability recharging...", 0.8)
            return
        ability = ABILITIES[self.selected_character.ability_key]
        self.ability_uses += 1
        self.execute_ability(ability)
        combo_reduction = min(0.45, 0.05 * self.combo_level)
        cooldown = max(ability.cooldown * 0.4, ability.cooldown * (1.0 - combo_reduction))
        self.ability_timer = cooldown
        self.ability_cooldown_max = cooldown
        self.ability_ready_notified = False
        if self.relic_effects.get("ability_shield", 0.0) > 0:
            self.player.grant_shield(self.relic_effects["ability_shield"])
        self.ability_flash_timer = 0.5

    def execute_ability(self, ability: AbilityProfile) -> None:
        if not self.player:
            return
        self.push_run_message(f"{ability.name}!", 1.2)
        center = pygame.Vector2(self.player.rect.center)
        if ability.effect == "blink":
            mouse = pygame.mouse.get_pos()
            direction = pygame.Vector2(mouse) - center
            if direction.length_squared() > 0:
                offset = direction.normalize() * ability.magnitude
                new_pos = center + offset
                bounds = self.screen.get_rect().inflate(-120, -120)
                new_pos.x = max(bounds.left, min(bounds.right, new_pos.x))
                new_pos.y = max(bounds.top, min(bounds.bottom, new_pos.y))
                self.player.rect.center = (int(new_pos.x), int(new_pos.y))
            self.player.invincible_timer = ability.payload.get("invuln", 0.5)
        elif ability.effect == "overdrive":
            duration = ability.payload.get("duration", 5.0)
            self.player.apply_temp_bonus(
                damage=ability.magnitude,
                focus=ability.payload.get("focus", 0.0),
                speed=ability.payload.get("speed", 0.0),
                crit=ability.payload.get("crit", 0.0),
                duration=duration,
            )
            if ability.payload.get("shield"):
                self.player.grant_shield(ability.payload["shield"])
        elif ability.effect == "nova":
            count = int(ability.payload.get("projectiles", 12))
            for i in range(count):
                angle = (math.tau / count) * i
                direction = pygame.Vector2(math.cos(angle), math.sin(angle))
                damage = (self.weapon_instance.damage if self.weapon_instance else 14.0) * ability.magnitude
                speed = self.weapon_instance.profile.projectile_speed if self.weapon_instance else 520
                projectile = Projectile(
                    center,
                    direction,
                    speed,
                    damage,
                    self.weapon_instance.profile.color if self.weapon_instance else self.colors["loot"],
                )
                self.projectiles.add(projectile)
            ignite_duration = ability.payload.get("ignite", 0.0)
            if ignite_duration > 0:
                for enemy in self.enemies:
                    enemy.ignite_timer = ignite_duration
                    enemy.ignite_damage = 12.0 * ability.magnitude
        elif ability.effect == "summon_drone":
            drone = SupportDrone(
                self.player,
                orbit_radius=120.0,
                damage=ability.magnitude,
                fire_delay=ability.payload.get("fire_delay", 1.0),
                duration=ability.payload.get("duration", 14.0),
            )
            self.drones.add(drone)
            self.drones_deployed_run += 1
        elif ability.effect == "summon_drone_squad":
            count = int(ability.payload.get("count", 3))
            for _ in range(count):
                drone = SupportDrone(
                    self.player,
                    orbit_radius=random.uniform(110.0, 150.0),
                    damage=ability.magnitude,
                    fire_delay=ability.payload.get("fire_delay", 1.2),
                    duration=ability.payload.get("duration", 16.0),
                )
                self.drones.add(drone)
            self.drones_deployed_run += count
        elif ability.effect == "gravity":
            field = {
                "position": pygame.Vector2(self.player.rect.center),
                "radius": ability.magnitude,
                "slow": ability.payload.get("slow", 0.35),
                "duration": ability.payload.get("duration", 5.0),
            }
            self.gravity_fields.append(field)
        elif ability.effect == "shockwave":
            boost = 1.0 + self.relic_effects.get("shockwave_boost", 0.0)
            for enemy in list(self.enemies):
                delta = pygame.Vector2(enemy.rect.center) - center
                if delta.length_squared() == 0:
                    continue
                knock = delta.normalize() * ability.magnitude * boost
                enemy.rect.centerx += int(knock.x)
                enemy.rect.centery += int(knock.y)
                enemy.take_damage((self.weapon_instance.damage if self.weapon_instance else 10.0) * ability.payload.get("damage", 1.0))
                enemy.stun_timer = ability.payload.get("stun", 1.0)
                enemy.temp_slow_timer = enemy.stun_timer
                enemy.temp_slow_factor = 0.2
                if enemy.hp <= 0:
                    self.handle_enemy_defeat(enemy)
        elif ability.effect == "heal_shield":
            self.player.heal(self.player.max_hp * ability.magnitude)
            self.player.grant_shield(ability.payload.get("shield", self.player.max_hp * 0.2))
        elif ability.effect == "storm":
            chains = int(ability.payload.get("chains", 4))
            slow_factor = max(0.2, 1.0 - ability.payload.get("slow", 0.3))
            enemies = sorted(
                list(self.enemies),
                key=lambda e: center.distance_to(pygame.Vector2(e.rect.center)),
            )[:chains]
            for enemy in enemies:
                enemy.take_damage((self.weapon_instance.damage if self.weapon_instance else 16.0) * ability.magnitude)
                enemy.temp_slow_timer = 2.4
                enemy.temp_slow_factor = slow_factor
                if enemy.hp <= 0:
                    self.handle_enemy_defeat(enemy)

    def attune_relic(self, relic: RelicProfile) -> None:
        if not self.player:
            return
        self.relics.append(relic)
        self.relics_bound_run += 1
        self.apply_relic_effect(relic)
        self.push_run_message(f"Bound relic: {relic.name}", 2.0)

    def apply_relic_effect(self, relic: RelicProfile) -> None:
        effect = relic.effect
        if effect == "damage_bonus":
            self.relic_effects["damage_bonus"] += relic.value
            self.player.apply_permanent_bonus("damage", relic.value)
        elif effect == "ability_haste":
            self.relic_effects["ability_haste"] += relic.value
        elif effect == "combo_extend":
            self.relic_effects["combo_extend"] += relic.value
        elif effect == "combo_shield":
            self.relic_effects["combo_shield"] += relic.value
        elif effect == "wave_heal":
            self.relic_effects["wave_heal"] += relic.value
        elif effect == "focus_bonus":
            self.relic_effects["focus_bonus"] += relic.value
            self.player.apply_permanent_bonus("focus", 0.05)
        elif effect == "gravity_rounds":
            self.relic_effects["gravity_rounds"] += relic.value
        elif effect == "ability_shield":
            self.relic_effects["ability_shield"] += relic.value
        elif effect == "pickup_speed":
            self.relic_effects["pickup_speed"] = max(self.relic_effects.get("pickup_speed", 0.0), relic.value)
        elif effect == "drone_damage":
            self.relic_effects["drone_damage"] += relic.value
        elif effect == "event_rate":
            self.relic_effects["event_rate"] += relic.value
        elif effect == "crit_bonus":
            self.player.apply_permanent_bonus("crit", relic.value)
        elif effect == "shockwave_boost":
            self.relic_effects["shockwave_boost"] += relic.value
        elif effect == "burn_bonus":
            self.relic_effects["burn_bonus"] += relic.value
        elif effect == "max_hp":
            self.player.apply_permanent_bonus("max_hp", relic.value)
        elif effect == "bonus_credits":
            self.relic_effects["bonus_credits"] += relic.value
        elif effect == "combo_drop":
            self.relic_effects["combo_drop"] += relic.value
        self.player.refresh_stats()

    def reset_relic_effects(self) -> None:
        self.relics = []
        self.relic_effects = {
            "damage_bonus": 0.0,
            "ability_haste": 0.0,
            "combo_extend": 0.0,
            "combo_shield": 0.0,
            "wave_heal": 0.0,
            "focus_bonus": 0.0,
            "gravity_rounds": 0.0,
            "ability_shield": 0.0,
            "pickup_speed": 0.0,
            "drone_damage": 0.0,
            "event_rate": 0.0,
            "crit_bonus": 0.0,
            "shockwave_boost": 0.0,
            "burn_bonus": 0.0,
            "bonus_credits": 0.0,
            "combo_drop": 0.0,
        }
        self.gravity_fields = []

    def reset_to_select(self) -> None:
        self.state = "character_select"
        self.player = None
        self.projectiles.empty()
        self.enemies.empty()
        self.pickups.empty()
        self.drones.empty()
        self.wave_state = None
        self.active_meta_levels = None
        self.combo_meter = 0
        self.combo_level = 0
        self.combo_timer = 0.0
        self.run_message = ""
        self.run_message_timer = 0.0
        self.reset_relic_effects()

    def purchase_selected_upgrade(self) -> None:
        character = self.characters[self.meta_character_index]
        upgrade_key = self.meta_categories[self.meta_category_index]
        success, message = purchase_upgrade(self.progress, character, upgrade_key)
        if not success and can_purchase_upgrade(self.progress, character, upgrade_key):
            message = "Unable to purchase upgrade."
        self.meta_message = message
        self.meta_message_timer = 2.5

    def draw_meta_progression(self) -> None:
        self.screen.fill(self.colors["void"])
        title = self.font_large.render("Dive Lab Upgrades", True, self.colors["ui_accent"])
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 90)))

        credits = self.font_medium.render(f"Aether Bank: {self.progress.credits}", True, self.colors["loot"])
        self.screen.blit(credits, credits.get_rect(center=(SCREEN_WIDTH // 2, 150)))

        character = self.characters[self.meta_character_index]
        sprite = player_sprite(character.primary_color, character.secondary_color)
        self.screen.blit(sprite, sprite.get_rect(center=(SCREEN_WIDTH // 2 - 260, SCREEN_HEIGHT // 2)))
        name_text = self.font_medium.render(character.name, True, (230, 230, 230))
        self.screen.blit(name_text, (SCREEN_WIDTH // 2 - 320, SCREEN_HEIGHT // 2 + 160))

        upgrades = upgrade_summary(character, self.progress)
        for idx, key in enumerate(self.meta_categories):
            definition = UPGRADE_DEFINITIONS[key]
            level = upgrades.get(key, 0)
            cost = definition.cost_for_level(level)
            is_selected = idx == self.meta_category_index
            label_color = self.colors["loot"] if is_selected else (200, 200, 200)
            bg_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, 220 + idx * 80, 520, 70)
            pygame.draw.rect(self.screen, self.colors["ui_bg"], bg_rect)
            if is_selected:
                pygame.draw.rect(self.screen, self.colors["ui_accent"], bg_rect, 3)

            label = self.font_medium.render(definition.label, True, label_color)
            self.screen.blit(label, (bg_rect.x + 16, bg_rect.y + 10))
            level_text = f"Lv. {level}/{definition.max_level}"
            level_surface = self.font_small.render(level_text, True, (190, 190, 190))
            self.screen.blit(level_surface, (bg_rect.right - level_surface.get_width() - 18, bg_rect.y + 12))

            if level >= definition.max_level:
                cost_text = "MAXED"
                cost_color = self.colors["player_secondary"]
            else:
                cost_text = f"Cost {cost}"
                affordable = can_purchase_upgrade(self.progress, character, key)
                cost_color = self.colors["loot"] if affordable else (160, 160, 160)
            cost_surface = self.font_small.render(cost_text, True, cost_color)
            self.screen.blit(cost_surface, (bg_rect.right - cost_surface.get_width() - 18, bg_rect.y + 44))

            desc_lines = wrap_text(definition.description, self.font_small, bg_rect.width - 40)
            for i, line in enumerate(desc_lines[:2]):
                desc_surface = self.font_small.render(line, True, (180, 180, 180))
                self.screen.blit(desc_surface, (bg_rect.x + 18, bg_rect.y + 34 + i * 16))

        instructions = self.font_small.render(
            "←/→ change diver  •  ↑/↓ select upgrade  •  Enter buy  •  Tab exit",
            True,
            (200, 200, 200),
        )
        self.screen.blit(instructions, instructions.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)))

        if self.meta_message and self.meta_message_timer > 0:
            message_surface = self.font_small.render(self.meta_message, True, self.colors["loot"])
            self.screen.blit(message_surface, message_surface.get_rect(center=(SCREEN_WIDTH // 2, 200)))
        self.draw_achievement_toasts()


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

