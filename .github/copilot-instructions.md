# BattleArena Game - AI Coding Instructions

## Architecture Overview

This is a **pygame-based 2D shooting game** with a clean modular architecture. The codebase follows strict Chinese development conventions and uses a **manager-pattern** for game systems.

### Key Components

- **`main.py`**: Single-class game orchestrator (`BattleArenaGame`) managing all subsystems
- **`src/config.py`**: Centralized configuration hub - modify this for game balance changes
- **`src/entities/`**: Player, Enemy, Bullet, PowerUp classes with state management
- **`src/systems/`**: CollisionSystem handles all physics interactions
- **`src/ui/`**: GameUI manages HUD, menus, and message overlays
- **`src/utils/`**: FontManager singleton for Chinese font handling

### System Interactions

- **State Flow**: `main.py` orchestrates → entities update → collision system processes → UI renders
- **Manager Pattern**: `BulletManager`, `PowerUpManager` handle object pools and lifecycle
- **Configuration-Driven**: All game mechanics defined in `WEAPON_CONFIGS`, `AI_CONFIGS`, `POWERUP_EFFECTS`
- **Chinese Localization**: FontManager singleton (`font_manager`) handles font detection and caching
- **Mouse + Keyboard Control**: Dual input system with mouse position movement and mouse clicking for shooting

## Critical Development Patterns

### Code Style Requirements ⚠️

```python
# ✅ ALWAYS use these patterns
######################區塊註解######################  # Block separators
def method_name(self):  # snake_case for functions/variables
    """
    完整的繁體中文文檔字串\n  # Documentation with \n breaks
    """
    # 每行重要邏輯都要有繁體中文註解說明在做什麼
```

**Critical Naming Convention**:

- Variables: `snake_case` (e.g., `enemy_spawn_count`, `current_weapon`)
- Classes: `PascalCase` (e.g., `BattleArenaGame`, `CollisionSystem`)
- Constants: `SCREAMING_SNAKE_CASE` (e.g., `SCREEN_WIDTH`, `PLAYER_SIZE`)

### Event-Driven Input Architecture

**Dual Input System**: The game uses both event-based and continuous input:

- **Event-based**: `_handle_mouse_click()`, `_handle_keydown()` for discrete actions
- **Continuous**: `_handle_continuous_input()` for movement and sustained actions
- **Mouse Control**: Player moves toward mouse position, shoots at mouse click location

```python
# ✅ Input handling pattern
def handle_events(self):
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_click(event.button, event.pos)
        elif event.type == pygame.KEYDOWN:
            self._handle_keydown(event.key)

def _handle_continuous_input(self):
    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    self.player.handle_input(keys, mouse_pos, mouse_buttons)
```

### Manager Pattern Architecture

**Critical**: All game objects use manager classes for lifecycle and pooling:

- **BulletManager**: `create_bullet()`, `update()`, `check_collision_with_single_target()`
- **PowerUpManager**: `spawn_powerup_on_enemy_death()`, `check_player_pickups()`
- **FontManager**: Singleton `font_manager.render_text()` - never create fonts directly

### Entity State Management

All entities follow this pattern:

- **Health/Alive tracking**: `self.health`, `self.is_alive`
- **Position system**: `self.x`, `self.y` with `update(screen_width, screen_height)`
- **Collision interface**: `get_rect()` method for pygame.Rect
- **Drawing method**: `draw(screen)` with state-based colors

### Configuration-Driven Development

**Essential workflow**: All game mechanics come from `src/config.py` dictionaries:

```python
# Game balance in config.py - modify these, not hardcoded values
WEAPON_CONFIGS = {
    "pistol": {"max_ammo": 12, "fire_rate": 300, "damage": 25},
    # Each weapon has ammo, reload, fire rate, damage, speed
}

# Usage in entities:
weapon_config = WEAPON_CONFIGS[self.current_weapon]  # ✅ Always use config
damage = weapon_config["damage"]  # ✅ Not hardcoded values
```

### Game State Architecture

**State machine**: `GAME_STATES["menu" | "character_select" | "scene_select" | "playing" | "game_over"]`

- Each state has dedicated input handling and rendering methods in `BattleArenaGame`
- Character/scene selection flow: menu → character_select → scene_select → playing
- UI handled by `SelectionUI` for selection states, `GameUI` for game states

### Chinese Font System (Critical)

**Always use the singleton `font_manager`**:

```python
from src.utils.font_manager import font_manager
text_surface = font_manager.render_text("文字", "medium", COLORS["white"])
# ❌ Never: pygame.font.Font() or pygame.font.SysFont() directly
```

- **Auto-detection**: Tries `"Microsoft JhengHei"`, `"Microsoft YaHei"`, fallbacks to system
- **Cached fonts**: Pre-loaded sizes ("large", "medium", "small", "tiny")
- **Graceful degradation**: Falls back to system fonts if Chinese fonts unavailable

## Essential Workflows

### Adding New Weapons

1. Define in `WEAPON_CONFIGS` (config.py) with all required properties
2. Add key binding in `KEYS` config if needed
3. Implement switch logic in `Player.handle_weapon_switch()`
4. Test ammo management and fire rate with new weapon config

### Adding New Character Types

1. Define in `CHARACTER_CONFIGS` with skill configuration
2. Update `SelectionUI` character selection if needed
3. Implement skill logic in `Player.use_skill()` method
4. Test skill cooldown, health cost, and damage effects

### Modifying AI Behavior

- **Configuration**: Change `AI_CONFIGS` for difficulty balancing
- **Movement patterns**: Modify `Enemy.update()` - pattern types: "simple", "tactical", "advanced"
- **Enemy types**: Add to `AI_ENEMY_TYPES` with health/speed/accuracy modifiers
- **Shooting logic**: Adjust accuracy and fire_rate in config

### Adding PowerUp Effects

1. Define effect in `POWERUP_EFFECTS` config with duration/instant properties
2. Implement pickup logic in `PowerUp.apply_effect()`
3. Handle duration tracking in `Player.update_powerups()`
4. Add visual effects in `PowerUp.draw()` method

### Performance Optimization

- **Font caching**: `FontManager` pre-loads fonts - don't create new fonts each frame
- **Collision batching**: `CollisionSystem.check_all_collisions()` processes all interactions once
- **Entity pooling**: Consider reusing bullet objects for better performance
- **Manager cleanup**: Use `clear_all_bullets()`, `clear_all_powerups()` for memory management

### Chinese Font Handling

**Critical**: Use the `font_manager` singleton, never create fonts directly:

```python
from src.utils.font_manager import font_manager
text_surface = font_manager.render_text("文字", "medium", COLORS["white"])
```

## Common Pitfalls & Solutions

### Configuration Changes

❌ **Don't** hardcode values - always use config.py constants  
✅ **Do** modify `WEAPON_CONFIGS`, `PLAYER_SPEED`, etc. in config.py

### Entity Lifecycle

❌ **Don't** forget `is_alive` checks before processing entities  
✅ **Do** use `for entity in entities[:]` pattern when removing during iteration

### Input Handling

❌ **Don't** mix event-based and continuous input types  
✅ **Do** use `handle_events()` for key presses, `_handle_continuous_input()` for WASD/shooting

### Collision Detection

❌ **Don't** implement custom collision logic  
✅ **Do** extend `CollisionSystem` methods - it handles all edge cases

## File Navigation Guide

- **Game mechanics**: Start with `src/entities/player.py` for combat system understanding
- **AI behavior**: Check `src/entities/enemy.py` movement patterns and difficulty configs
- **Performance tuning**: Examine `CollisionSystem` and `BulletManager` for optimization points
- **UI changes**: Modify `GameUI` class - handles all HUD elements and game states
- **Balance changes**: `src/config.py` contains all gameplay constants

## Running & Testing

```bash
python main.py  # No __main__ guard needed - direct execution
```

**Debug tools**: Enable collision event logging in `CollisionSystem.get_collision_events()`
