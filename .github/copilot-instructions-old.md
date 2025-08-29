# BattleArena Game — AI Coding Agent Guide

Essential knowledge for AI coding agents to be immediately productive in this codebase. Focuses on architecture patterns, critical integration points, and project-specific conventions.

## 🏗️ Architecture Overview

**Project**: Pygame 2D shooting game with character selection, multiple weapons, and AI opponents.

**Entry Point**: `main.py` → `GameEngine` class manages game loop and state machine:

- State flow: menu → character_select → difficulty_select → scene_select → countdown → playing → game_over
- Core pattern: Event handling → Update logic → Render → Repeat at 60 FPS

**Module Structure**:

- `src/entities/`: Game objects (Player, Enemy, Bullet, PowerUp) - each implements `update()`, `get_rect()`, `draw()`, `is_alive`
- `src/systems/`: Service boundaries (CollisionSystem centralizes all collision detection)
- `src/ui/`: Interface layers (GameUI, SelectionUI) with Chinese font support via font_manager
- `src/utils/`: Shared utilities (FontManager singleton for Chinese text rendering, ImageManager for assets)
- `src/core/`: Core systems (StateManager, EventHandler, InputManager) for game architecture
- `src/config.py`: **All configuration data** - never hardcode game values

## 🔒 Critical Integration Points (DO NOT MODIFY ARBITRARILY)

**Font Management**: Always use `font_manager.render_text(text, size, color)` or `font_manager.get_font(size)`:

```python
from src.utils.font_manager import font_manager
surface = font_manager.render_text("遊戲文字", "medium", COLORS["white"])
```

**Sound System**: Use `SoundManager` singleton for all audio - never use pygame.mixer directly:

```python
from src.utils.sound_manager import sound_manager
sound_manager.play_weapon_sound(weapon_type)  # Auto-maps weapon to sound
sound_manager.play_victory_sound()  # Special game events
sound_manager.play_sound("race_start")  # Direct sound name
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
- `LEVEL_CONFIGS`: enemy types, counts, descriptions, completion messages (by difficulty: easy/medium/hard)
- `SCENE_CONFIGS`: background colors, accent colors, descriptions
- `AI_ENEMY_TYPES`: health, speed/accuracy modifiers, damage, attack frequency
- `DIFFICULTY_CONFIGS`: enemy health multipliers and descriptions
- `FONT_CONFIGS`: Chinese font preferences and size mappings
- `SOUND_CONFIGS`: audio file paths, volumes, descriptions for all game sounds

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

## 🎯 Critical Project-Specific Patterns

**State Machine Flow**: Menu → character_select → difficulty_select → scene_select → countdown → playing → game_over (see `GameEngine`)

**Skill System**: 3-second duration skills with visual effects and health cost - use `Player.use_skill()` and check `Player.is_skill_active()`

**Level Progression**: Automatic enemy type switching between levels, track `level_enemies_killed` vs `LEVEL_CONFIGS[difficulty][level]["enemy_count"]`

**Difficulty System**: Three-tier difficulty (easy/medium/hard) affects enemy counts, health multipliers, and level progression

**Chinese Font Handling**: FontManager automatically detects system fonts, use `font_manager.render_text()` consistently

**AI Difficulty Scaling**: All AI properties in `AI_CONFIGS` affect enemy accuracy, health, and behavior patterns

## 🎮 Quick Reference Examples

**Config Access**: `weapon_data = WEAPON_CONFIGS[self.current_weapon]`

**Message Display**: `self.game_ui.add_message("彈藥不足", "warning", COLORS["yellow"])`

**Character Skills**: Defined in `CHARACTER_CONFIGS[type]["skill"]` with damage, cooldown, effect_color

**Scene Backgrounds**: `SCENE_CONFIGS[scene]["background_color"]` for environment customization

**Level Configuration**: `LEVEL_CONFIGS[difficulty][level]` for enemy counts, boss flags, and scene settings

## 🛠️ Development Workflow

**Run Game**: `python main.py` (direct execution, no `if __name__ == "__main__":` needed)

**Run Tests**: Individual test files like `test_all_sounds.py` (no pytest framework currently)

**Debug Keys**: F1 (spawn boss), F2 (complete level) for testing

**Game Assets**: Character images in `assets/characters/` with both PNG and JPG fallbacks, sound files in `音效/` directory

## 📋 Code Style Requirements

**Naming**: snake_case (variables/functions), PascalCase (classes), SCREAMING_SNAKE_CASE (constants)

**Comments**: Use Chinese docstrings for public methods, `######################` for section separators

**Imports**: Group by standard/third-party/local, use absolute imports from `src/`

## ⚠️ Common Pitfalls to Avoid

- Never hardcode values - use `src/config.py` configurations
- Always use `font_manager` for text rendering (handles Chinese fonts)
- Always use `sound_manager` for audio - never use pygame.mixer directly
- Don't implement custom collision detection - use `CollisionSystem`
- Use manager classes for bullets/powerups, not direct entity lists
- Remember safe iteration patterns when removing entities
- Character attributes are multipliers applied to base values, not absolute values
