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
- **Bullet System**: Managed centrally by `BulletManager`, spawned by player/enemy actions
- **Configuration-Driven**: All game mechanics defined in `WEAPON_CONFIGS`, `AI_CONFIGS`, `POWERUP_EFFECTS`

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

### Entity State Management

All entities follow this pattern:

- **Health/Alive tracking**: `self.health`, `self.is_alive`
- **Position system**: `self.x`, `self.y` with `update(screen_width, screen_height)`
- **Collision interface**: `get_rect()` method for pygame.Rect
- **Drawing method**: `draw(screen)` with state-based colors

### Weapon & Combat System

```python
# Weapons defined in config.py - modify there for balance
WEAPON_CONFIGS = {
    "pistol": {"max_ammo": 12, "fire_rate": 300, "damage": 25},
    # Each weapon has ammo, reload, fire rate, damage, speed
}
```

- **Player shooting**: Returns `shot_data` dict with bullet array
- **Ammo management**: Separate `current_ammo` and `total_ammo` tracking
- **Reload system**: Time-based with `is_reloading` state

### Game State Architecture

**State machine**: `GAME_STATES["menu" | "playing" | "game_over"]`

- Each state has dedicated input handling and rendering methods
- Centralized in `BattleArenaGame` class with state-specific methods

## Essential Workflows

### Adding New Weapons

1. Define in `WEAPON_CONFIGS` (config.py)
2. Add key binding in `KEYS` config
3. Implement switch logic in `Player.handle_weapon_switch()`
4. Test ammo management and fire rate

### Modifying AI Behavior

- **Configuration**: Change `AI_CONFIGS` for difficulty balancing
- **Movement patterns**: Modify `Enemy.update()` - pattern types: "simple", "tactical", "advanced"
- **Shooting logic**: Adjust accuracy and fire_rate in config

### Performance Optimization

- **Font caching**: `FontManager` pre-loads fonts - don't create new fonts each frame
- **Collision batching**: `CollisionSystem.check_all_collisions()` processes all interactions once
- **Entity pooling**: Consider reusing bullet objects for better performance

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
