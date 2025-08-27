<!-- BattleArena Game — AI Coding Agent Guide -->

Essential knowledge for AI coding agents to be immediately productive in this codebase. Focuses on archite**Quick Reference Examples**

**Config Access**: `weapon_data = WEAPON_CONFIGS[self.current_weapon]`
**Message Display**: `self.game_ui.add_message("彈藥不足", "warning", COLORS["yellow"])`
**Character Skills**: Defined in `CHARACTER_CONFIGS[type]["skill"]` with damage, cooldown, effect_color
**Scene Backgrounds**: `SCENE_CONFIGS[scene]["background_color"]` for environment customization

## 🎯 Critical Project-Specific Patterns

**State Machine Flow**: Menu → character_select → scene_select → playing → game_over (see `main.py:BattleArenaGame`)

**Skill System**: 3-second duration skills with visual effects and health cost - use `Player.use_skill()` and check `Player.is_skill_active()`

**Level Progression**: Automatic enemy type switching between levels, track `level_enemies_killed` vs `LEVEL_CONFIGS[level]["enemy_count"]`

**Chinese Font Handling**: FontManager automatically detects system fonts, use `font_manager.render_text()` consistently

**AI Difficulty Scaling**: All AI properties in `AI_CONFIGS` affect enemy accuracy, health, and behavior patternspatterns, critical integration points, and project-specific conventions.

## 🏗️ Architecture Overview

**Project**: Pygame 2D shooting game with character selection, multiple weapons, and AI opponents.

**Entry Point**: `main.py` → `BattleArenaGame` class manages game loop and state machine:

- State flow: menu → character_select → scene_select → playing → game_over
- Core pattern: Event handling → Update logic → Render → Repeat at 60 FPS

**Module Structure**:

- `src/entities/`: Game objects (Player, Enemy, Bullet, PowerUp) - each implements `update()`, `get_rect()`, `draw()`, `is_alive`
- `src/systems/`: Service boundaries (CollisionSystem centralizes all collision detection)
- `src/ui/`: Interface layers (GameUI, SelectionUI) with Chinese font support via font_manager
- `src/utils/`: Shared utilities (FontManager singleton for Chinese text rendering)
- `src/config.py`: **All configuration data** - never hardcode game values

## 🔒 Critical Integration Points (DO NOT MODIFY ARBITRARILY)

**Font Management**: Always use `font_manager.render_text(text, size, color)` or `font_manager.get_font(size)`:

```python
from src.utils.font_manager import font_manager
surface = font_manager.render_text("遊戲文字", "medium", COLORS["white"])
```

**Collision System**: All interactions handled by `CollisionSystem.check_all_collisions()`. Never implement custom collision loops:

```python
collision_results = self.collision_system.check_all_collisions(
    self.player, self.enemies, self.bullet_manager, self.powerup_manager
)
```

**Configuration-Driven Design**: All balance values live in `src/config.py`:

- `WEAPON_CONFIGS`: damage, ammo, reload times, fire_rate, special properties (spread, bullet_count)
- `CHARACTER_CONFIGS`: skills, colors, cooldowns, attributes (attack_power, fire_rate, speed, health multipliers)
- `AI_CONFIGS`: difficulty levels, accuracy, behavior patterns, health
- `POWERUP_EFFECTS`: duration, multipliers, instant effects, weapon unlocks
- `LEVEL_CONFIGS`: enemy types, counts, descriptions, completion messages
- `SCENE_CONFIGS`: background colors, accent colors, descriptions
- `AI_ENEMY_TYPES`: health, speed/accuracy modifiers, damage, attack frequency

## 🎯 Entity System Patterns

**Standard Entity Interface**:

```python
def update(self, screen_width, screen_height):
    # Position updates and boundary checks

def get_rect(self):
    return pygame.Rect(self.x, self.y, self.width, self.height)

def draw(self, screen):
    # Render entity with character-specific colors/emojis

# Health management (entities with health)
self.health = initial_value
self.is_alive = self.health > 0

# State management (all entities)
self.is_active = True  # For bullets, powerups
```

**Manager Pattern for Collections**:

```python
# BulletManager handles all bullet lifecycle
self.bullet_manager.create_bullet(x, y, angle, speed, damage, owner)
self.bullet_manager.update(screen_width, screen_height)
self.bullet_manager.draw(screen)

# PowerUpManager handles spawning and pickup logic
self.powerup_manager.spawn_powerup_on_enemy_death(x, y)
```

**Safe Entity Removal Pattern**:

```python
for entity in entities[:]:  # Create copy for safe iteration
    if not entity.is_alive:
        entities.remove(entity)
```

## 🕹️ Input System Architecture

**Mouse Controls** (per CROSSHAIR_SYSTEM.md):

- Left click: Shoot at crosshair position (precise targeting)
- Right click: Restart game
- Mouse movement: Updates crosshair position only (NO character movement)

**Keyboard Controls**:

- WASD: Character movement (only method for player positioning)
- 1-5: Weapon switching
- Q: Character special skill (10s cooldown, 10% health cost)
- R: Manual reload
- C: Toggle crosshair display
- ESC: Return to menu
- H: Toggle health display mode (bar/number, menu only)
- +/-: Adjust player health (menu only)

**Continuous Input Handling**: Use `_handle_continuous_input()` pattern for WASD movement and mouse shooting, separate from discrete key events

## 🎨 UI System Conventions

**Chinese Text Support**: All UI text in Traditional Chinese with proper font fallbacks
**Message System**: `game_ui.add_message(text, type, color)` for temporary notifications
**Health Display**: Toggle between bar/number modes via H key in menu
**Crosshair**: Smart color-coding (white→orange→red→yellow) based on ammo status

## ⚙️ Common Development Workflows

**Adding New Weapon**:

1. Define in `WEAPON_CONFIGS` with damage, ammo, fire_rate, special properties
2. Update `Player.handle_weapon_switch()` for key binding
3. Test ammo consumption and reload mechanics

**Adding New Enemy Type**:

1. Add to `AI_ENEMY_TYPES` with health, speed, accuracy modifiers
2. Update enemy spawn logic in `BattleArenaGame._spawn_enemy()`
3. Ensure proper behavior in `Enemy.update()` method

**Adding New PowerUp**:

1. Define in `POWERUP_EFFECTS` with duration/instant properties
2. Implement in `PowerUp.apply_effect()` and `Player.update_powerups()`
3. Add spawn chance in `PowerUpManager.spawn_powerup_on_enemy_death()`

**Adding New Level**:

1. Add entry to `LEVEL_CONFIGS` with enemy_type, enemy_count, description
2. Update level completion logic in `BattleArenaGame._check_level_completion()`
3. Consider enemy spawn patterns in main game loop

## 🐛 Development & Debugging

**Run Game**: `python main.py` (no `if __name__ == "__main__"` needed)

**Collision Debugging**: Enable event logging in `CollisionSystem.get_collision_events()`

**Performance**: Font manager caches fonts; collision system batches checks; entity managers handle cleanup

## 📋 Code Style Requirements

- **Naming**: snake_case (variables/functions), PascalCase (classes), SCREAMING_SNAKE_CASE (constants)
- **Comments**: Traditional Chinese docstrings for public methods; inline comments explaining complex logic
- **Modules**: Use clear block separators `######################載入套件######################`
- **Error Handling**: Graceful fallbacks (e.g., font loading failures, missing config keys)

## 🚀 Quick Reference Examples

**Config Access**: `weapon_data = WEAPON_CONFIGS[self.current_weapon]`
**Message Display**: `self.game_ui.add_message("彈藥不足", "warning", COLORS["yellow"])`
**Character Skills**: Defined in `CHARACTER_CONFIGS[type]["skill"]` with damage, cooldown, effect_color
**Scene Backgrounds**: `SCENE_CONFIGS[scene]["background_color"]` for environment customization
