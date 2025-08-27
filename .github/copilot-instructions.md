# BattleArena Game — AI Coding Agent Guide<!-- BattleArena Game — AI Coding Agent Guide --><!-- BattleArena Game — AI Coding Agent Guide -->

Essential knowledge for AI coding agents to be immediately productive in this codebase. Focuses on architecture patterns, critical integration points, and project-specific conventions.Essential knowledge for AI coding agents to be immediately productive in this codebase. Focuses on architecture patterns, critical integration points, and project-specific conventions.Essential knowledge for AI coding agents to be immediately productive in this codebase. Focuses on archite**Quick Reference Examples**

## 🏗️ Architecture Overview## 🏗️ Architecture Overview**Config Access**: `weapon_data = WEAPON_CONFIGS[self.current_weapon]`

**Project**: Pygame 2D shooting game with character selection, multiple weapons, and AI opponents.**Message Display**: `self.game_ui.add_message("彈藥不足", "warning", COLORS["yellow"])`

**Entry Point**: `main.py` → `BattleArenaGame` class manages game loop and state machine:**Project**: Pygame 2D shooting game with character selection, multiple weapons, and AI opponents.**Character Skills**: Defined in `CHARACTER_CONFIGS[type]["skill"]` with damage, cooldown, effect_color

- State flow: menu → character_select → scene_select → playing → game_over

- Core pattern: Event handling → Update logic → Render → Repeat at 60 FPS**Scene Backgrounds**: `SCENE_CONFIGS[scene]["background_color"]` for environment customization

**Module Structure**:**Entry Point**: `main.py` → `BattleArenaGame` class manages game loop and state machine:

- `src/entities/`: Game objects (Player, Enemy, Bullet, PowerUp) - each implements `update()`, `get_rect()`, `draw()`, `is_alive`

- `src/systems/`: Service boundaries (CollisionSystem centralizes all collision detection)## 🎯 Critical Project-Specific Patterns

- `src/ui/`: Interface layers (GameUI, SelectionUI) with Chinese font support via font_manager

- `src/utils/`: Shared utilities (FontManager singleton for Chinese text rendering)- State flow: menu → character_select → scene_select → playing → game_over

- `src/config.py`: **All configuration data** - never hardcode game values

- Core pattern: Event handling → Update logic → Render → Repeat at 60 FPS**State Machine Flow**: Menu → character_select → scene_select → playing → game_over (see `main.py:BattleArenaGame`)

## 🔒 Critical Integration Points (DO NOT MODIFY ARBITRARILY)

**Module Structure**:**Skill System**: 3-second duration skills with visual effects and health cost - use `Player.use_skill()` and check `Player.is_skill_active()`

**Font Management**: Always use `font_manager.render_text(text, size, color)` or `font_manager.get_font(size)`:

```python- `src/entities/`: Game objects (Player, Enemy, Bullet, PowerUp) - each implements `update()`, `get_rect()`, `draw()`, `is_alive`**Level Progression**: Automatic enemy type switching between levels, track `level_enemies_killed`vs`LEVEL_CONFIGS[level]["enemy_count"]`

from src.utils.font_manager import font_manager

surface = font_manager.render_text("遊戲文字", "medium", COLORS["white"])- `src/systems/`: Service boundaries (CollisionSystem centralizes all collision detection)

`````

- `src/ui/`: Interface layers (GameUI, SelectionUI) with Chinese font support via font_manager**Chinese Font Handling**: FontManager automatically detects system fonts, use `font_manager.render_text()` consistently

**Collision System**: All interactions handled by `CollisionSystem.check_all_collisions()`. Never implement custom collision loops:

```python- `src/utils/`: Shared utilities (FontManager singleton for Chinese text rendering)

collision_results = self.collision_system.check_all_collisions(

    self.player, self.enemies, self.bullet_manager, self.powerup_manager- `src/config.py`: **All configuration data** - never hardcode game values**AI Difficulty Scaling**: All AI properties in `AI_CONFIGS` affect enemy accuracy, health, and behavior patternspatterns, critical integration points, and project-specific conventions.

)

```## 🔒 Critical Integration Points (DO NOT MODIFY ARBITRARILY)## 🏗️ Architecture Overview



**Configuration-Driven Design**: All balance values live in `src/config.py`:**Font Management**: Always use `font_manager.render_text(text, size, color)` or `font_manager.get_font(size)`:**Project**: Pygame 2D shooting game with character selection, multiple weapons, and AI opponents.

- `WEAPON_CONFIGS`: damage, ammo, reload times, fire_rate, special properties (spread, bullet_count)

- `CHARACTER_CONFIGS`: skills, colors, cooldowns, attributes (attack_power, fire_rate, speed, health multipliers)```python**Entry Point**: `main.py`→`BattleArenaGame` class manages game loop and state machine:

- `AI_CONFIGS`: difficulty levels, accuracy, behavior patterns, health

- `POWERUP_EFFECTS`: duration, multipliers, instant effects, weapon unlocksfrom src.utils.font_manager import font_manager

- `LEVEL_CONFIGS`: enemy types, counts, descriptions, completion messages

- `SCENE_CONFIGS`: background colors, accent colors, descriptionssurface = font_manager.render_text("遊戲文字", "medium", COLORS["white"])- State flow: menu → character_select → scene_select → playing → game_over

- `AI_ENEMY_TYPES`: health, speed/accuracy modifiers, damage, attack frequency

````- Core pattern: Event handling → Update logic → Render → Repeat at 60 FPS

## 🎯 Entity System Patterns



**Standard Entity Interface**:

```python**Collision System**: All interactions handled by `CollisionSystem.check_all_collisions()`. Never implement custom collision loops:**Module Structure**:

def update(self, screen_width, screen_height):

    # Position updates and boundary checks



def get_rect(self):```python- `src/entities/`: Game objects (Player, Enemy, Bullet, PowerUp) - each implements `update()`, `get_rect()`, `draw()`, `is_alive`

    return pygame.Rect(self.x, self.y, self.width, self.height)

collision_results = self.collision_system.check_all_collisions(- `src/systems/`: Service boundaries (CollisionSystem centralizes all collision detection)

def draw(self, screen):

    # Render entity with character-specific colors/emojis    self.player, self.enemies, self.bullet_manager, self.powerup_manager- `src/ui/`: Interface layers (GameUI, SelectionUI) with Chinese font support via font_manager



# Health management (entities with health))- `src/utils/`: Shared utilities (FontManager singleton for Chinese text rendering)

self.health = initial_value

self.is_alive = self.health > 0```- `src/config.py`: **All configuration data** - never hardcode game values



# State management (all entities)

self.is_active = True  # For bullets, powerups

```**Configuration-Driven Design**: All balance values live in `src/config.py`:## 🔒 Critical Integration Points (DO NOT MODIFY ARBITRARILY)



**Manager Pattern for Collections**:

```python

# BulletManager handles all bullet lifecycle- `WEAPON_CONFIGS`: damage, ammo, reload times, fire_rate, special properties (spread, bullet_count)**Font Management**: Always use `font_manager.render_text(text, size, color)` or `font_manager.get_font(size)`:

self.bullet_manager.create_bullet(x, y, angle, speed, damage, owner)

self.bullet_manager.update(screen_width, screen_height)- `CHARACTER_CONFIGS`: skills, colors, cooldowns, attributes (attack_power, fire_rate, speed, health multipliers)

self.bullet_manager.draw(screen)

- `AI_ENEMY_TYPES`: health, speed/accuracy modifiers, damage, attack frequency (zombie→alien progression)```python

# PowerUpManager handles spawning and pickup logic

self.powerup_manager.spawn_powerup_on_enemy_death(x, y)- `POWERUP_EFFECTS`: duration, multipliers, instant effects, weapon unlocksfrom src.utils.font_manager import font_manager

`````

- `LEVEL_CONFIGS`: enemy types, counts, descriptions, completion messagessurface = font_manager.render_text("遊戲文字", "medium", COLORS["white"])

**Safe Entity Removal Pattern**:

`` python- `SCENE_CONFIGS`: background colors, accent colors, descriptions ``

for entity in entities[:]: # Create copy for safe iteration

    if not entity.is_alive:

        entities.remove(entity)

```## 🎯 Entity System Patterns**Collision System**: All interactions handled by `CollisionSystem.check_all_collisions()`. Never implement custom collision loops:

## 🎯 Critical Project-Specific Patterns

**State Machine Flow**: Menu → character_select → scene_select → playing → game_over (see `main.py:BattleArenaGame`)**Standard Entity Interface**:```python

**Skill System**: 3-second duration skills with visual effects and health cost - use `Player.use_skill()` and check `Player.is_skill_active()`collision_results = self.collision_system.check_all_collisions(

**Level Progression**: Automatic enemy type switching between levels, track `level_enemies_killed` vs `LEVEL_CONFIGS[level]["enemy_count"]````python self.player, self.enemies, self.bullet_manager, self.powerup_manager

**Chinese Font Handling**: FontManager automatically detects system fonts, use `font_manager.render_text()` consistentlydef update(self, screen_width, screen_height):)

**AI Difficulty Scaling**: All AI properties in `AI_CONFIGS` affect enemy accuracy, health, and behavior patterns # Position updates and boundary checks```

## 🎮 Quick Reference Examples

**Config Access**: `weapon_data = WEAPON_CONFIGS[self.current_weapon]`def get_rect(self):**Configuration-Driven Design**: All balance values live in `src/config.py`:

**Message Display**: `self.game_ui.add_message("彈藥不足", "warning", COLORS["yellow"])` return pygame.Rect(self.x, self.y, self.width, self.height)

**Character Skills**: Defined in `CHARACTER_CONFIGS[type]["skill"]` with damage, cooldown, effect_color- `WEAPON_CONFIGS`: damage, ammo, reload times, fire_rate, special properties (spread, bullet_count)

**Scene Backgrounds**: `SCENE_CONFIGS[scene]["background_color"]` for environment customizationdef draw(self, screen):- `CHARACTER_CONFIGS`: skills, colors, cooldowns, attributes (attack_power, fire_rate, speed, health multipliers)

## 🛠️ Development Workflow # Render entity with character-specific colors/emojis- `AI_CONFIGS`: difficulty levels, accuracy, behavior patterns, health

**Run Game**: `python main.py` (direct execution, no `if __name__ == "__main__":` needed)- `POWERUP_EFFECTS`: duration, multipliers, instant effects, weapon unlocks

**Run Tests**: `pytest -q` or `pytest tests/` (uses pytest framework)# Health management (entities with health)- `LEVEL_CONFIGS`: enemy types, counts, descriptions, completion messages

**Debug Keys**: F1 (spawn boss), F2 (complete level) for testingself.health = initial_value- `SCENE_CONFIGS`: background colors, accent colors, descriptions

## 📋 Code Style Requirementsself.is_alive = self.health > 0- `AI_ENEMY_TYPES`: health, speed/accuracy modifiers, damage, attack frequency

**Naming**: snake_case (variables/functions), PascalCase (classes), SCREAMING_SNAKE_CASE (constants)

**Comments**: Use Chinese docstrings for public methods, `######################` for section separators# State management (all entities)## 🎯 Entity System Patterns

**Imports**: Group by standard/third-party/local, use absolute imports from `src/`self.is_active = True # For bullets, powerups

## ⚠️ Common Pitfalls to Avoid```**Standard Entity Interface**:

- Never hardcode values - use `src/config.py` configurations

- Always use `font_manager` for text rendering (handles Chinese fonts)

- Don't implement custom collision detection - use `CollisionSystem`**Manager Pattern for Collections**:```python

- Use manager classes for bullets/powerups, not direct entity lists

- Remember safe iteration patterns when removing entitiesdef update(self, screen_width, screen_height):

- Character attributes are multipliers applied to base values, not absolute values

````python # Position updates and boundary checks

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

        ---
        applyTo: "**"
        ---

        # BattleArena — Copilot 指引（簡潔版）

        以下指引為讓 AI 編碼代理能快速在此專案中工作所需的關鍵知識：專案架構、重要整合點、常用程式碼模式與開發流程。

        1. 入口與整體架構
            - 入口：`main.py`，核心類別 `BattleArenaGame` 管理狀態機（menu → character_select → scene_select → playing → game_over）。
            - 模組劃分：`src/entities/`（Player、Enemy、Bullet、PowerUp）、`src/systems/`（CollisionSystem）、`src/ui/`（GameUI, SelectionUI）、`src/utils/`（font_manager）、`src/config.py`（所有遊戲數值與設定）。

        2. 關鍵約定與模式
            - 配置驅動：所有遊戲參數（weapon、level、AI）集中在 `src/config.py`，請勿硬編碼數值。
            - 實體介面：每個 entity 實作 `update(screen_w, screen_h)`, `get_rect()`, `draw(screen)`, `is_alive`。
            - 管理器模式：Bullet/PowerUp 有 manager 類別負責建立、更新與清理（safe removal: iterate over copy `for e in entities[:]`）。
            - 碰撞：所有交互請透過 `CollisionSystem.check_all_collisions()`，不要寫自訂碰撞迴圈。

        3. UI / 字型
            - 文字請使用 `font_manager.render_text(text, size, color)` 或 `font_manager.get_font(size)`，專案以繁體中文為主。
            - 快速訊息：用 `game_ui.add_message(text, type, color)` 顯示臨時通知。

        4. 控制與輸入習慣
            - 連續輸入與事件分離：使用 `_handle_continuous_input()` 處理 WASD 與滑鼠持續操作，事件處理用一般事件回呼。
            - 重要按鍵：WASD（移動）、滑鼠左鍵（射擊）、1-5（武器切換）、Q（技能）、R（重裝）、C（切換準星）、ESC（返回選單）。

        5. 新增/變更要點（範例）
            - 新武器：在 `WEAPON_CONFIGS` 新增設定，並確認 `Player.handle_weapon_switch()` 支援該鍵位與 ammo/reload 行為。
            - 新敵人：在 `AI_ENEMY_TYPES` 加入並在 `BattleArenaGame._spawn_enemy()` 對應 spawn；測試 `Enemy.update()` 行為。
            - 新 power-up：在 `POWERUP_EFFECTS` 定義，實作 `PowerUp.apply_effect()` 並讓 `Player.update_powerups()` 處理效果。

        6. 開發 / 執行 / 測試
            - 執行遊戲：在專案根目錄執行 `python main.py`（專案在 main.py 直接呼叫 game loop）。
            - 單元測試：專案使用 pytest（檢視 `tests/`），在修改後請執行 `pytest -q` 驗證。若 CI 存在，遵循其環境變數與 Python 版本。

        7. 風格與格式（可被 agent 自動遵守）
            - 命名：snake_case（變數/函式）、PascalCase（類別）、SCREAMING_SNAKE_CASE（常數）。
            - 註解：公開方法需繁體中文 docstring；使用 `######################` 作區塊分隔。

        8. 不可任意修改的整合點
            - `src/config.py`：平衡與參數來源。
            - `CollisionSystem`：集中碰撞邏輯，避免分散實作。
            - `font_manager`：統一文字渲染與字型快取。

        9. 探索快速參考（關鍵檔案）
            - `main.py`（入口、狀態機）
            - `src/config.py`（所有設定）
            - `src/systems/collision.py`（碰撞匯流處）
            - `src/utils/font_manager.py`（字型渲染）
            - `src/entities/`（Player, Enemy, Bullet, PowerUp）

        10. 變更紀錄與回饋
            - 若你看到功能性衝突或需要新增 CI 指令，請回報並提供最小可重現步驟。

        ---
        請審閱這份簡潔指引，告訴我是否要把某些細節擴充為範例片段（例如 `CollisionSystem.check_all_collisions()` 的使用方式或 `WEAPON_CONFIGS` 範例）。
**Skill System**: 3-second duration skills with visual effects and health cost - use `Player.use_skill()` and check `Player.is_skill_active()`
````
