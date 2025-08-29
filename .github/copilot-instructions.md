````instructions
# BattleArena Game — AI Coding Agent Guide

Essential knowledge for AI coding agents to be immediately productive in this codebase. Focuses on architecture patterns, critical integration points, and project-specific conventions.

## 🏗️ Architecture Overview

**Project**: Pygame 2D shooting game with character selection (貓/狗/狼), skill system, level progression, and Chinese UI.

**Entry Point**: `main.py` → `GameEngine` class manages game loop and state machine:

- State flow: menu → character_select → difficulty_select → scene_select → countdown → playing → game_over
- Core pattern: Event handling → Update logic → Render → Repeat at 60 FPS
- **Critical**: Direct execution (`main()` called immediately, no `if __name__ == "__main__":`)

**Module Structure**:

- `src/entities/`: Game objects (Player, Enemy, Bullet, PowerUp) - each implements `update()`, `get_rect()`, `draw()`, `is_alive`
- `src/systems/`: Service boundaries (CollisionSystem centralizes all collision detection)
- `src/ui/`: Interface layers (GameUI, SelectionUI) with Chinese font support via font_manager
- `src/utils/`: Shared utilities (FontManager singleton for Chinese text rendering, ImageManager for assets, SoundManager)
- `src/core/`: Core systems (StateManager, EventHandler, InputManager) for game architecture
- `src/config.py`: **All configuration data** - never hardcode game values
- `assets/`: Character images (`characters/cat-removebg-preview.png`, etc.) and weapon sprites
- `音效/`: Chinese-named sound directory with game audio files

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
sound_manager.play_level3_boss_music()  # Level 3 background music
sound_manager.stop_background_music()  # Stop background music
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
- `POWERUP_EFFECTS`: duration, multipliers, instant effects, weapon unlocks, **victory_star** (victory trigger)
- `LEVEL_CONFIGS`: enemy types, counts, descriptions, completion messages, **boss flags** (by difficulty: easy/medium/hard)
- `SCENE_CONFIGS`: background colors, accent colors, descriptions
- `AI_ENEMY_TYPES`: health, speed/accuracy modifiers, damage, attack frequency, **boss configuration**
- `DIFFICULTY_CONFIGS`: enemy health multipliers and descriptions
- `FONT_CONFIGS`: Chinese font preferences and size mappings
- `SOUND_CONFIGS`: audio file paths, volumes, descriptions for all game sounds, **level3_boss_music**

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
self.powerup_manager.spawn_victory_star_on_boss_death(boss_x, boss_y)
```

**Safe Entity Removal Pattern**:

```python
for entity in entities[:]:  # Create copy for safe iteration
    if not entity.is_alive:
        entities.remove(entity)
```

## 🎯 Critical Project-Specific Patterns

**Character System**: Three distinct characters with unique attributes and skills:
- 貓 (Cat): High attack (130%), low fire rate (70%), laser skill (yellow beam, 100 damage)
- 狗 (Dog): Balanced stats (100%), flame skill (fire particles, 75 damage)
- 狼 (Wolf): High fire rate (150%), low attack (80%), ice skill (crystal effects, 125 damage)

**Level Progression System**: Sequential enemy waves with automatic progression:
- Level 1: 3 zombies (25 damage, 2s attack frequency)
- Level 2: 5 aliens (35 damage, 3s attack frequency)
- **Level 3**: Mixed enemies + Boss battle with victory star collection
- Track `level_enemies_killed` vs `LEVEL_CONFIGS[difficulty][level]["enemy_count"]`

**Boss Battle Mechanics**: Level 3 features special boss encounter:
- Boss spawns after regular enemies are defeated
- Boss death triggers `victory_star` PowerUp spawn
- Player must collect victory star to complete the game
- Background music automatically plays for Level 3 (`level3_boss_music`)

**Victory Star System**: Special PowerUp for game completion:
- Only spawns when boss dies (`powerup_manager.spawn_victory_star_on_boss_death()`)
- Larger size (40px vs 20px), never expires (`lifetime = float('inf')`)
- Collection sets `player.victory_star_collected = True` for game victory
- Uses external image asset `invincibility-star-v0-bveezlamy4bc1-removebg-preview.png`

**Skill System**: 3-second duration skills with unique visual effects:
- All skills cost 10% max health, 10-second cooldown
- Use `Player.use_skill()` and check `Player.is_skill_active()`
- Each character has distinct particle/beam effects

**State Machine Flow**: Menu → character_select → difficulty_select → scene_select → countdown → playing → game_over (see `GameEngine`)

**Difficulty System**: Three-tier difficulty (easy/medium/hard) affects enemy counts, health multipliers, and AI behavior

**Chinese Localization**: All UI text in Traditional Chinese, FontManager handles system font detection

## 🎮 Quick Reference Examples

**Config Access**: `weapon_data = WEAPON_CONFIGS[self.current_weapon]`

**Message Display**: `self.game_ui.add_message("彈藥不足", "warning", COLORS["yellow"])`

**Character Skills**: Defined in `CHARACTER_CONFIGS[type]["skill"]` with damage, cooldown, effect_color

**Scene Backgrounds**: `SCENE_CONFIGS[scene]["background_color"]` for environment customization

**Level Configuration**: `LEVEL_CONFIGS[difficulty][level]` for enemy counts, boss flags, and scene settings

## 🛠️ Development Workflow

**Run Game**: `python main.py` (direct execution, no `if __name__ == "__main__":` needed)

**Manual Testing**: No automated testing framework - create individual test files for specific features (e.g., `test_complete_shotgun.py`, `test_bullet_image.py`)

**Debug Keys**: F1 (spawn boss), F2 (complete level), H (toggle health display), C (toggle crosshair), +/- (adjust player health in menu)

**Game Controls**: WASD (movement), Mouse (aim/shoot), Q (skill), R (reload), 1-5 (weapons), ESC (menu), Right-click (restart game)

**Game Assets**: Character images in `assets/characters/` with `-removebg-preview.png` format, sounds in `音效/` with Chinese filenames, victory star asset at project root

## 📋 Code Style Requirements

**Language**: Traditional Chinese comments and docstrings for all public methods

**Naming**: snake_case (variables/functions), PascalCase (classes), SCREAMING_SNAKE_CASE (constants)

**Comments**: Use `######################` for major section separators

**Imports**: Group by standard/third-party/local, use absolute imports from `src/`

**File Structure**: Follow existing pattern - entities for game objects, systems for services, ui for interfaces

## ⚠️ Common Pitfalls to Avoid

- Never hardcode values - use `src/config.py` configurations
- Always use `font_manager` for text rendering (handles Chinese fonts automatically)
- Always use `sound_manager` for audio - never use pygame.mixer directly
- Don't implement custom collision detection - use `CollisionSystem`
- Use manager classes for bullets/powerups, not direct entity lists
- Remember safe iteration patterns when removing entities
- Character attributes are multipliers applied to base values, not absolute values
- Test files are for manual verification, not automated testing
- Asset paths must match actual file names (case-sensitive)
- Sound files in `音效/` directory use Chinese naming convention

````
