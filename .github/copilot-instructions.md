<!-- BattleArena Game — AI Coding Agent Guide -->

Essential knowledge for AI coding agents to be immediately productive in this codebase. Focuses on architecture patterns, critical integration points, and project-specific conventions.

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

- `WEAPON_CONFIGS`: damage, ammo, reload times, special properties
- `CHARACTER_CONFIGS`: skills, colors, cooldowns
- `AI_CONFIGS`: difficulty levels, accuracy, behavior patterns
- `POWERUP_EFFECTS`: duration, multipliers, instant effects

## 🎯 Entity System Patterns

**Standard Entity Interface**:

```python
def update(self, screen_width, screen_height):
    # Position updates and boundary checks

def get_rect(self):
    return pygame.Rect(self.x, self.y, self.width, self.height)

def draw(self, screen):
    # Render entity with character-specific colors/emojis

# Health management
self.health = initial_value
self.is_alive = self.health > 0
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
- Q: Character special skill (30s cooldown, 10% health cost)
- R: Manual reload
- C: Toggle crosshair display

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
