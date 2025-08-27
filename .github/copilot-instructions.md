<!-- BattleArena Game — AI Coding Agent Guide --><!-- BattleArena Game — AI Coding Agent Guide -->



Essential knowledge for AI coding agents to be immediately productive in this codebase. Focuses on architecture patterns, critical integration points, and project-specific conventions.Essential knowledge for AI coding agents to be immediately productive in this codebase. Focuses on archite**Quick Reference Examples**



## 🏗️ Architecture Overview**Config Access**: `weapon_data = WEAPON_CONFIGS[self.current_weapon]`

**Message Display**: `self.game_ui.add_message("彈藥不足", "warning", COLORS["yellow"])`

**Project**: Pygame 2D shooting game with character selection, multiple weapons, and AI opponents.**Character Skills**: Defined in `CHARACTER_CONFIGS[type]["skill"]` with damage, cooldown, effect_color

**Scene Backgrounds**: `SCENE_CONFIGS[scene]["background_color"]` for environment customization

**Entry Point**: `main.py` → `BattleArenaGame` class manages game loop and state machine:

## 🎯 Critical Project-Specific Patterns

- State flow: menu → character_select → scene_select → playing → game_over

- Core pattern: Event handling → Update logic → Render → Repeat at 60 FPS**State Machine Flow**: Menu → character_select → scene_select → playing → game_over (see `main.py:BattleArenaGame`)



**Module Structure**:**Skill System**: 3-second duration skills with visual effects and health cost - use `Player.use_skill()` and check `Player.is_skill_active()`



- `src/entities/`: Game objects (Player, Enemy, Bullet, PowerUp) - each implements `update()`, `get_rect()`, `draw()`, `is_alive`**Level Progression**: Automatic enemy type switching between levels, track `level_enemies_killed` vs `LEVEL_CONFIGS[level]["enemy_count"]`

- `src/systems/`: Service boundaries (CollisionSystem centralizes all collision detection)

- `src/ui/`: Interface layers (GameUI, SelectionUI) with Chinese font support via font_manager**Chinese Font Handling**: FontManager automatically detects system fonts, use `font_manager.render_text()` consistently

- `src/utils/`: Shared utilities (FontManager singleton for Chinese text rendering)

- `src/config.py`: **All configuration data** - never hardcode game values**AI Difficulty Scaling**: All AI properties in `AI_CONFIGS` affect enemy accuracy, health, and behavior patternspatterns, critical integration points, and project-specific conventions.



## 🔒 Critical Integration Points (DO NOT MODIFY ARBITRARILY)## 🏗️ Architecture Overview



**Font Management**: Always use `font_manager.render_text(text, size, color)` or `font_manager.get_font(size)`:**Project**: Pygame 2D shooting game with character selection, multiple weapons, and AI opponents.



```python**Entry Point**: `main.py` → `BattleArenaGame` class manages game loop and state machine:

from src.utils.font_manager import font_manager

surface = font_manager.render_text("遊戲文字", "medium", COLORS["white"])- State flow: menu → character_select → scene_select → playing → game_over

```- Core pattern: Event handling → Update logic → Render → Repeat at 60 FPS



**Collision System**: All interactions handled by `CollisionSystem.check_all_collisions()`. Never implement custom collision loops:**Module Structure**:



```python- `src/entities/`: Game objects (Player, Enemy, Bullet, PowerUp) - each implements `update()`, `get_rect()`, `draw()`, `is_alive`

collision_results = self.collision_system.check_all_collisions(- `src/systems/`: Service boundaries (CollisionSystem centralizes all collision detection)

    self.player, self.enemies, self.bullet_manager, self.powerup_manager- `src/ui/`: Interface layers (GameUI, SelectionUI) with Chinese font support via font_manager

)- `src/utils/`: Shared utilities (FontManager singleton for Chinese text rendering)

```- `src/config.py`: **All configuration data** - never hardcode game values



**Configuration-Driven Design**: All balance values live in `src/config.py`:## 🔒 Critical Integration Points (DO NOT MODIFY ARBITRARILY)



- `WEAPON_CONFIGS`: damage, ammo, reload times, fire_rate, special properties (spread, bullet_count)**Font Management**: Always use `font_manager.render_text(text, size, color)` or `font_manager.get_font(size)`:

- `CHARACTER_CONFIGS`: skills, colors, cooldowns, attributes (attack_power, fire_rate, speed, health multipliers)

- `AI_ENEMY_TYPES`: health, speed/accuracy modifiers, damage, attack frequency (zombie→alien progression)```python

- `POWERUP_EFFECTS`: duration, multipliers, instant effects, weapon unlocksfrom src.utils.font_manager import font_manager

- `LEVEL_CONFIGS`: enemy types, counts, descriptions, completion messagessurface = font_manager.render_text("遊戲文字", "medium", COLORS["white"])

- `SCENE_CONFIGS`: background colors, accent colors, descriptions```



## 🎯 Entity System Patterns**Collision System**: All interactions handled by `CollisionSystem.check_all_collisions()`. Never implement custom collision loops:



**Standard Entity Interface**:```python

collision_results = self.collision_system.check_all_collisions(

```python    self.player, self.enemies, self.bullet_manager, self.powerup_manager

def update(self, screen_width, screen_height):)

    # Position updates and boundary checks```



def get_rect(self):**Configuration-Driven Design**: All balance values live in `src/config.py`:

    return pygame.Rect(self.x, self.y, self.width, self.height)

- `WEAPON_CONFIGS`: damage, ammo, reload times, fire_rate, special properties (spread, bullet_count)

def draw(self, screen):- `CHARACTER_CONFIGS`: skills, colors, cooldowns, attributes (attack_power, fire_rate, speed, health multipliers)

    # Render entity with character-specific colors/emojis- `AI_CONFIGS`: difficulty levels, accuracy, behavior patterns, health

- `POWERUP_EFFECTS`: duration, multipliers, instant effects, weapon unlocks

# Health management (entities with health)- `LEVEL_CONFIGS`: enemy types, counts, descriptions, completion messages

self.health = initial_value- `SCENE_CONFIGS`: background colors, accent colors, descriptions

self.is_alive = self.health > 0- `AI_ENEMY_TYPES`: health, speed/accuracy modifiers, damage, attack frequency



# State management (all entities)## 🎯 Entity System Patterns

self.is_active = True  # For bullets, powerups

```**Standard Entity Interface**:



**Manager Pattern for Collections**:```python

def update(self, screen_width, screen_height):

```python    # Position updates and boundary checks

# BulletManager handles all bullet lifecycle

self.bullet_manager.create_bullet(x, y, angle, speed, damage, owner)def get_rect(self):

self.bullet_manager.update(screen_width, screen_height)    return pygame.Rect(self.x, self.y, self.width, self.height)

self.bullet_manager.draw(screen)

def draw(self, screen):

# PowerUpManager handles spawning and pickup logic    # Render entity with character-specific colors/emojis

self.powerup_manager.spawn_powerup_on_enemy_death(x, y)

```# Health management (entities with health)

self.health = initial_value

**Safe Entity Removal Pattern**:self.is_alive = self.health > 0



```python# State management (all entities)

for entity in entities[:]:  # Create copy for safe iterationself.is_active = True  # For bullets, powerups

    if not entity.is_alive:```

        entities.remove(entity)

```**Manager Pattern for Collections**:



## 🕹️ Input System Architecture```python

# BulletManager handles all bullet lifecycle

**Mouse Controls** (per CROSSHAIR_SYSTEM.md):self.bullet_manager.create_bullet(x, y, angle, speed, damage, owner)

self.bullet_manager.update(screen_width, screen_height)

- Left click: Shoot at crosshair position (precise targeting)self.bullet_manager.draw(screen)

- Right click: Restart game

- Mouse movement: Updates crosshair position only (NO character movement)# PowerUpManager handles spawning and pickup logic

self.powerup_manager.spawn_powerup_on_enemy_death(x, y)

**Keyboard Controls**:```



- WASD: Character movement (only method for player positioning)**Safe Entity Removal Pattern**:

- 1-5: Weapon switching

- Q: Character special skill (10s cooldown, 10% health cost)```python

- R: Manual reloadfor entity in entities[:]:  # Create copy for safe iteration

- C: Toggle crosshair display    if not entity.is_alive:

- ESC: Return to menu        entities.remove(entity)

- H: Toggle health display mode (bar/number, menu only)```

- +/-: Adjust player health (menu only)

## 🕹️ Input System Architecture

**Continuous Input Handling**: Use `_handle_continuous_input()` pattern for WASD movement and mouse shooting, separate from discrete key events

**Mouse Controls** (per CROSSHAIR_SYSTEM.md):

## 🎯 Critical Project-Specific Patterns

- Left click: Shoot at crosshair position (precise targeting)

**State Machine Flow**: Menu → character_select → scene_select → playing → game_over (see `main.py:BattleArenaGame`)- Right click: Restart game

- Mouse movement: Updates crosshair position only (NO character movement)

**Skill System**: 3-second duration skills with visual effects and health cost - use `Player.use_skill()` and check `Player.is_skill_active()`

**Keyboard Controls**:

**Level Progression**: Automatic enemy type switching between levels, track `level_enemies_killed` vs `LEVEL_CONFIGS[level]["enemy_count"]`

- Level 1: 3 zombies (25 damage, 2s attack frequency) - WASD: Character movement (only method for player positioning)

- Level 2: 5 aliens (35 damage, 3s attack frequency)- 1-5: Weapon switching

- Q: Character special skill (10s cooldown, 10% health cost)

**Chinese Font Handling**: FontManager automatically detects system fonts, use `font_manager.render_text()` consistently- R: Manual reload

- C: Toggle crosshair display

**Character System**: Each character has unique attributes and skills:- ESC: Return to menu

- Cat: High attack (130%), low fire rate (70%), laser skill- H: Toggle health display mode (bar/number, menu only)

- Dog: Balanced (100%), fire skill  - +/-: Adjust player health (menu only)

- Wolf: High fire rate (150%), low attack (80%), ice skill

**Continuous Input Handling**: Use `_handle_continuous_input()` pattern for WASD movement and mouse shooting, separate from discrete key events

## 🎨 UI System Conventions

## 🎨 UI System Conventions

**Chinese Text Support**: All UI text in Traditional Chinese with proper font fallbacks

**Message System**: `game_ui.add_message(text, type, color)` for temporary notifications**Chinese Text Support**: All UI text in Traditional Chinese with proper font fallbacks

**Health Display**: Toggle between bar/number modes via H key in menu**Message System**: `game_ui.add_message(text, type, color)` for temporary notifications

**Crosshair**: Smart color-coding (white→orange→red→yellow) based on ammo status**Health Display**: Toggle between bar/number modes via H key in menu

**Crosshair**: Smart color-coding (white→orange→red→yellow) based on ammo status

## ⚙️ Common Development Workflows

## ⚙️ Common Development Workflows

**Adding New Weapon**:

**Adding New Weapon**:

1. Define in `WEAPON_CONFIGS` with damage, ammo, fire_rate, special properties

2. Update `Player.handle_weapon_switch()` for key binding1. Define in `WEAPON_CONFIGS` with damage, ammo, fire_rate, special properties

3. Test ammo consumption and reload mechanics2. Update `Player.handle_weapon_switch()` for key binding

3. Test ammo consumption and reload mechanics

**Adding New Enemy Type**:

**Adding New Enemy Type**:

1. Add to `AI_ENEMY_TYPES` with health, speed, accuracy modifiers

2. Update enemy spawn logic in `BattleArenaGame._spawn_enemy()`1. Add to `AI_ENEMY_TYPES` with health, speed, accuracy modifiers

3. Ensure proper behavior in `Enemy.update()` method2. Update enemy spawn logic in `BattleArenaGame._spawn_enemy()`

3. Ensure proper behavior in `Enemy.update()` method

**Adding New PowerUp**:

**Adding New PowerUp**:

1. Define in `POWERUP_EFFECTS` with duration/instant properties

2. Implement in `PowerUp.apply_effect()` and `Player.update_powerups()`1. Define in `POWERUP_EFFECTS` with duration/instant properties

3. Add spawn chance in `PowerUpManager.spawn_powerup_on_enemy_death()`2. Implement in `PowerUp.apply_effect()` and `Player.update_powerups()`

3. Add spawn chance in `PowerUpManager.spawn_powerup_on_enemy_death()`

**Adding New Level**:

**Adding New Level**:

1. Add entry to `LEVEL_CONFIGS` with enemy_type, enemy_count, description

2. Update level completion logic in `BattleArenaGame._check_level_completion()`1. Add entry to `LEVEL_CONFIGS` with enemy_type, enemy_count, description

3. Consider enemy spawn patterns in main game loop2. Update level completion logic in `BattleArenaGame._check_level_completion()`

3. Consider enemy spawn patterns in main game loop

## 🐛 Development & Debugging

## 🐛 Development & Debugging

**Run Game**: `python main.py` (no `if __name__ == "__main__"` needed)

**Run Game**: `python main.py` (no `if __name__ == "__main__"` needed)

**Collision Debugging**: Enable event logging in `CollisionSystem.get_collision_events()`

**Collision Debugging**: Enable event logging in `CollisionSystem.get_collision_events()`

**Performance**: Font manager caches fonts; collision system batches checks; entity managers handle cleanup

**Performance**: Font manager caches fonts; collision system batches checks; entity managers handle cleanup

## 📋 Code Style Requirements

## 📋 Code Style Requirements

- **Naming**: snake_case (variables/functions), PascalCase (classes), SCREAMING_SNAKE_CASE (constants)

- **Comments**: Traditional Chinese docstrings for public methods; inline comments explaining complex logic- **Naming**: snake_case (variables/functions), PascalCase (classes), SCREAMING_SNAKE_CASE (constants)

- **Modules**: Use clear block separators `######################載入套件######################`- **Comments**: Traditional Chinese docstrings for public methods; inline comments explaining complex logic

- **Error Handling**: Graceful fallbacks (e.g., font loading failures, missing config keys)- **Modules**: Use clear block separators `######################載入套件######################`

- **Error Handling**: Graceful fallbacks (e.g., font loading failures, missing config keys)

## 🚀 Quick Reference Examples

## 🚀 Quick Reference Examples

**Config Access**: `weapon_data = WEAPON_CONFIGS[self.current_weapon]`

**Message Display**: `self.game_ui.add_message("彈藥不足", "warning", COLORS["yellow"])`**Config Access**: `weapon_data = WEAPON_CONFIGS[self.current_weapon]`

**Character Skills**: Defined in `CHARACTER_CONFIGS[type]["skill"]` with damage, cooldown, effect_color**Message Display**: `self.game_ui.add_message("彈藥不足", "warning", COLORS["yellow"])`

**Scene Backgrounds**: `SCENE_CONFIGS[scene]["background_color"]` for environment customization**Character Skills**: Defined in `CHARACTER_CONFIGS[type]["skill"]` with damage, cooldown, effect_color
**Scene Backgrounds**: `SCENE_CONFIGS[scene]["background_color"]` for environment customization
