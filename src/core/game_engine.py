######################載入套件######################
import pygame
import sys
import random
from src.config import *
from src.entities.player import Player
from src.entities.enemy import Enemy
from src.entities.bullet import BulletManager
from src.entities.powerup import PowerUpManager
from src.systems.collision import CollisionSystem
from src.ui.game_ui import GameUI
from src.ui.selection_ui import SelectionUI
from src.utils.font_manager import font_manager
from src.core.state_manager import StateManager
from src.core.event_handler import EventHandler
from src.core.input_manager import InputManager

######################主遊戲引擎######################


class GameEngine:
    """
    主遊戲引擎 - 整合所有核心系統的中央控制器\n
    \n
    此引擎負責：\n
    1. 初始化和管理所有子系統\n
    2. 協調各系統之間的通訊\n
    3. 控制主遊戲迴圈\n
    4. 處理系統層級的錯誤\n
    """

    def __init__(self):
        """
        初始化遊戲引擎\n
        """
        # 初始化pygame
        pygame.init()

        # 建立遊戲視窗
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("BattleArena - 射擊對戰遊戲")

        # 時鐘控制
        self.clock = pygame.time.Clock()
        self.running = True

        # 初始化核心系統
        self.state_manager = StateManager(self)
        self.event_handler = EventHandler(self)
        self.input_manager = InputManager(self)

        # 遊戲設定（需在 _init_game_systems 之前定義）
        self.player_max_health = PLAYER_DEFAULT_HEALTH
        self.enemy_difficulty = "medium"
        self.health_display_mode = "number"

        # 角色和場景選擇
        self.selected_character = "cat"
        self.selected_difficulty = "easy"
        self.selected_scene = "lava"

        # 初始化遊戲系統
        self._init_game_systems()

        # 遊戲狀態變數
        self._init_game_state()

    def _init_game_systems(self):
        """
        初始化所有遊戲系統\n
        """
        # 遊戲物件管理系統
        self.bullet_manager = BulletManager()
        self.powerup_manager = PowerUpManager()
        self.collision_system = CollisionSystem()

        # UI系統
        self.game_ui = GameUI(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.game_ui.set_health_display_mode(self.health_display_mode)
        self.selection_ui = SelectionUI(SCREEN_WIDTH, SCREEN_HEIGHT)

        # 敵人管理
        self.enemies = []
        self.enemy_spawn_count = 1
        self.enemy_types_pool = ["robot", "alien", "zombie"]
        self.current_level_enemy_type = "zombie"

    def _init_game_state(self):
        """
        初始化遊戲狀態變數\n
        """
        # 遊戲統計
        self.score = 0
        self.current_level = 1
        self.level_enemies_killed = 0
        self.game_completed = False
        self.game_stats = {
            "enemies_killed": 0,
            "shots_fired": 0,
            "shots_hit": 0,
            "powerups_collected": 0,
            "game_time": 0,
        }

        # 計時器
        self.game_start_time = 0
        self.last_skill_activation = 0
        self.last_skill_damage_time = 0

        # 遊戲物件
        self.player = None

    def start_new_game(self):
        """
        開始新遊戲\n
        \n
        重置所有遊戲狀態並創建新的遊戲物件\n
        """
        # 重置遊戲狀態
        self.state_manager.change_state("playing")
        self._init_game_state()

        # 創建玩家（使用選擇的角色）
        player_start_x = SCREEN_WIDTH // 2 - PLAYER_SIZE // 2
        player_start_y = SCREEN_HEIGHT - 100
        self.player = Player(
            player_start_x,
            player_start_y,
            self.player_max_health,
            self.selected_character,
        )

        # 重置敵人系統
        self.enemy_spawn_count = 1
        level_config = LEVEL_CONFIGS[self.selected_difficulty][self.current_level]
        self.current_level_enemy_counts = level_config.get("enemy_counts", {})
        if "scene" in level_config:
            self.selected_scene = level_config["scene"]
        self.enemies.clear()

        # 創建初始敵人
        self._spawn_enemy()

        # 清空所有管理系統
        self.bullet_manager.clear_all_bullets()
        self.powerup_manager.clear_all_powerups()

        # 顯示遊戲開始訊息
        level_config = LEVEL_CONFIGS[self.selected_difficulty][self.current_level]
        self.game_ui.add_message(
            f"{level_config['name']}", "achievement", COLORS["green"]
        )
        self.game_ui.add_message(
            f"{level_config['description']}", "info", COLORS["yellow"]
        )

    def reset_game_settings(self):
        """
        重置遊戲設定為預設值\n
        """
        self.player_max_health = PLAYER_DEFAULT_HEALTH
        self.enemy_difficulty = "medium"
        self.selected_character = "cat"
        self.selected_scene = "lava"

    def _spawn_enemy(self):
        """
        生成新敵人\n
        """
        # 隨機選擇生成位置（螢幕上方）
        enemy_x = random.randint(50, SCREEN_WIDTH - ENEMY_SIZE - 50)
        enemy_y = random.randint(50, 150)

        # 根據當前關卡選擇敵人類型
        level_config = LEVEL_CONFIGS[self.selected_difficulty][self.current_level]
        enemy_counts = level_config.get("enemy_counts", {})

        # BOSS 生成邏輯
        if level_config.get("boss", False):
            total_needed = level_config.get("enemy_count", 0)
            current_alive_normal = len(
                [e for e in self.enemies if e.enemy_type != "boss" and e.is_alive]
            )
            killed = self.level_enemies_killed

            if killed >= total_needed and not any(
                e.enemy_type == "boss" for e in self.enemies
            ):
                boss_x = SCREEN_WIDTH // 2 - ENEMY_SIZE * 3 // 2
                boss_y = 80
                boss = Enemy(boss_x, boss_y, self.enemy_difficulty, "boss")
                self.enemies.append(boss)
                self.game_ui.add_message("BOSS 出現！", "achievement", COLORS["purple"])
                return

        # 一般敵人生成
        if enemy_counts:
            types = []
            for t, cnt in enemy_counts.items():
                types.extend([t] * max(1, cnt))
            enemy_type = random.choice(types)
        else:
            enemy_type = "zombie"

        enemy = Enemy(enemy_x, enemy_y, self.enemy_difficulty, enemy_type)
        self.enemies.append(enemy)

    def update_game(self):
        """
        更新遊戲邏輯（每幀呼叫）\n
        """
        if not self.state_manager.is_state("playing"):
            return

        # 更新輸入管理器
        self.input_manager.update_input_state()

        # 更新遊戲時間
        current_time = pygame.time.get_ticks()
        self.game_stats["game_time"] = (current_time - self.game_start_time) / 1000

        # 更新玩家
        if self.player and self.player.is_alive:
            self.player.update(SCREEN_WIDTH, SCREEN_HEIGHT)
        else:
            if not self.game_completed:
                self.state_manager.change_state("game_over")
            return

        # 檢查遊戲完成條件
        if self.game_completed:
            self.state_manager.change_state("game_over")
            return

        # 處理技能持續效果
        self._update_skill_effects()

        # 更新敵人
        self._update_enemies()

        # 更新子彈
        self.bullet_manager.update(SCREEN_WIDTH, SCREEN_HEIGHT)

        # 更新驚喜包
        self.powerup_manager.update(SCREEN_WIDTH, SCREEN_HEIGHT)

        # 處理碰撞
        collision_results = self.collision_system.check_all_collisions(
            self.player, self.enemies, self.bullet_manager, self.powerup_manager
        )

        # 處理碰撞結果
        self._process_collision_results(collision_results)

        # 更新UI
        self.game_ui.update()

        # AI增殖機制
        self._manage_enemy_spawning()

        # 檢查關卡完成條件
        self._check_level_completion()

    def _update_enemies(self):
        """
        更新敵人狀態\n
        """
        enemies_killed_this_frame = 0
        for enemy in self.enemies[:]:
            if enemy.is_alive:
                enemy.update(self.player, SCREEN_WIDTH, SCREEN_HEIGHT)

                # 敵人射擊
                shot_data = enemy.shoot(self.player)
                if shot_data:
                    if isinstance(shot_data, list):
                        for s in shot_data:
                            self.bullet_manager.create_bullet(
                                s["x"],
                                s["y"],
                                s["angle"],
                                s["speed"],
                                s["damage"],
                                s.get("owner", "enemy"),
                            )
                    elif isinstance(shot_data, dict):
                        self.bullet_manager.create_bullet(
                            shot_data["x"],
                            shot_data["y"],
                            shot_data["angle"],
                            shot_data["speed"],
                            shot_data["damage"],
                            shot_data.get("owner", "enemy"),
                        )
            else:
                # 移除死亡的敵人
                self.enemies.remove(enemy)
                self.game_stats["enemies_killed"] += 1
                self.level_enemies_killed += 1
                self.score += 100
                enemies_killed_this_frame += 1

                # 敵人死亡時可能掉落道具
                self.powerup_manager.spawn_powerup_on_enemy_death(enemy.x, enemy.y)
                self.game_ui.add_message(f"+100 分", "achievement", COLORS["yellow"])

    def _update_skill_effects(self):
        """
        更新技能持續效果\n
        """
        if not self.player or not self.player.is_skill_active():
            return

        current_time = pygame.time.get_ticks()

        if current_time - self.last_skill_damage_time >= 1000:
            skill_info = self.player.get_active_skill_info()
            if skill_info:
                enemies_hit = 0
                for enemy in self.enemies:
                    if enemy.is_alive:
                        damage_per_second = skill_info["damage"] // 3
                        if enemy.take_damage(damage_per_second):
                            enemies_hit += 1
                        else:
                            enemies_hit += 1

                if enemies_hit > 0:
                    self.game_ui.add_message(
                        f"技能持續傷害：{enemies_hit} 個敵人",
                        "info",
                        skill_info["effect_color"],
                    )

                self.last_skill_damage_time = current_time

    def _manage_enemy_spawning(self):
        """
        管理敵人生成\n
        """
        if not self.game_completed:
            current_enemy_count = len([e for e in self.enemies if e.is_alive])
            level_config = LEVEL_CONFIGS[self.selected_difficulty][self.current_level]
            remaining_enemies_needed = (
                level_config["enemy_count"] - self.level_enemies_killed
            )

            if current_enemy_count == 0 and remaining_enemies_needed > 0:
                self._spawn_enemy()
            elif current_enemy_count < 2 and remaining_enemies_needed > 1:
                self._spawn_enemy()

    def _check_level_completion(self):
        """
        檢查關卡完成條件\n
        """
        if self.game_completed:
            return

        level_config = LEVEL_CONFIGS[self.selected_difficulty][self.current_level]

        # BOSS 關卡檢查
        if level_config.get("boss", False):
            boss_alive = any(
                e.enemy_type == "boss" and e.is_alive for e in self.enemies
            )
            if not boss_alive and self.level_enemies_killed >= level_config.get(
                "enemy_count", 0
            ):
                self.game_ui.add_message(
                    level_config["completion_message"], "achievement", COLORS["green"]
                )
                self.game_completed = True
                self.enemies.clear()
                return

        # 一般關卡檢查
        required = level_config.get("enemy_count", 0)
        if self.level_enemies_killed >= required:
            self.game_ui.add_message(
                level_config.get("completion_message", "關卡完成！"),
                "achievement",
                COLORS["green"],
            )

            if self.current_level < len(LEVEL_CONFIGS[self.selected_difficulty]):
                # 進入下一關
                self.current_level += 1
                self.level_enemies_killed = 0
                next_level_config = LEVEL_CONFIGS[self.selected_difficulty][
                    self.current_level
                ]
                self.current_level_enemy_counts = next_level_config.get(
                    "enemy_counts", {}
                )
                if "scene" in next_level_config:
                    self.selected_scene = next_level_config["scene"]
                self.enemies.clear()

                self.game_ui.add_message(
                    f"{next_level_config['name']}", "achievement", COLORS["blue"]
                )
                self.game_ui.add_message(
                    f"{next_level_config['description']}", "info", COLORS["yellow"]
                )
            else:
                self.game_completed = True
                self.enemies.clear()
                self.game_ui.add_message(
                    "遊戲完成！", "achievement", COLORS.get("gold", COLORS["yellow"])
                )

    def _process_collision_results(self, results):
        """
        處理碰撞檢測結果\n
        """
        if results["player_hit"]:
            self.game_ui.add_message("受到攻擊！", "damage", COLORS["red"])

        for hit_info in results["enemies_hit"]:
            self.game_stats["shots_hit"] += hit_info["bullets_count"]
            if hit_info["killed"]:
                self.game_ui.add_message("敵人被擊敗！", "achievement", COLORS["green"])

        for powerup_info in results["powerups_collected"]:
            self.game_stats["powerups_collected"] += 1
            self.game_ui.add_message(
                powerup_info["message"], "powerup", COLORS["yellow"]
            )
            self.score += 50

    def render(self):
        """
        渲染當前遊戲狀態\n
        """
        current_state = self.state_manager.get_current_state()

        if current_state == GAME_STATES["menu"]:
            self._draw_menu()
        elif current_state in [
            GAME_STATES["character_select"],
            GAME_STATES["difficulty_select"],
            GAME_STATES["scene_select"],
        ]:
            self.selection_ui.draw(self.screen)
        elif current_state == GAME_STATES["playing"]:
            self._draw_game()
        elif current_state == GAME_STATES["game_over"]:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_menu(self):
        """
        繪製主選單\n
        """
        self.screen.fill(COLORS["black"])

        # 遊戲標題
        title_text = "BattleArena"
        title_surface = font_manager.render_text(title_text, "large", COLORS["white"])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_surface, title_rect)

        # 副標題
        subtitle_text = "射擊對戰遊戲"
        subtitle_surface = font_manager.render_text(
            subtitle_text, "medium", COLORS["gray"]
        )
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, 110))
        self.screen.blit(subtitle_surface, subtitle_rect)

        # 選單項目
        menu_items = [
            "按 SPACE 開始選擇角色",
            "",
            "遊戲設定:",
            f"AI難度: {AI_CONFIGS[self.enemy_difficulty]['name']} (按 1/2/3 切換)",
            f"玩家血量: {self.player_max_health} (+/-調整)",
            f"血量顯示: {'數字' if self.health_display_mode == 'number' else '血條'} (按 H 切換)",
            "",
            "角色系統:",
            "🐱 貓 - 高攻擊力，低射速，雷射技能",
            "🐶 狗 - 平衡型角色，火焰技能",
            "🐺 狼 - 高射速，低攻擊力，冰凍技能",
            "",
            "操作說明:",
            "WASD - 角色移動",
            "滑鼠移動 - 控制準心位置",
            "滑鼠左鍵 - 射擊（朝準心位置）",
            "滑鼠右鍵 - 重新開始遊戲",
            "R - 填裝彈藥",
            "1/2/3/4/5 - 切換武器",
            "Q - 使用角色技能（消耗10%生命值，冷卻10秒）",
            "C - 切換準心顯示",
            "ESC - 返回選單",
            "遊戲結束後：R重新開始 或 滑鼠右鍵重新開始",
        ]

        start_y = 140
        for i, item in enumerate(menu_items):
            if item:
                color = COLORS["yellow"] if "按" in item else COLORS["white"]
                text_surface = font_manager.render_text(item, "small", color)
                text_rect = text_surface.get_rect(
                    center=(SCREEN_WIDTH // 2, start_y + i * 18)
                )
                self.screen.blit(text_surface, text_rect)

    def _draw_game(self):
        """
        繪製遊戲畫面\n
        """
        # 根據選擇的場景設置背景
        try:
            if (
                hasattr(self, "selected_scene")
                and self.selected_scene
                and self.selected_scene in SCENE_CONFIGS
            ):
                scene_config = SCENE_CONFIGS[self.selected_scene]
                background_color = scene_config["background_color"]
            else:
                background_color = COLORS["black"]
        except Exception as e:
            print(f"場景背景設置錯誤: {e}, 使用預設黑色背景")
            background_color = COLORS["black"]

        self.screen.fill(background_color)

        # 繪製遊戲物件
        if self.player:
            self.player.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        self.bullet_manager.draw(self.screen)
        self.powerup_manager.draw(self.screen)

        # 繪製UI
        self.game_ui.draw(
            self.screen,
            self.player,
            self.enemies,
            self.score,
            self.game_stats,
            self.current_level,
            self.level_enemies_killed,
        )

    def _draw_game_over(self):
        """
        繪製遊戲結束畫面\n
        """
        self._draw_game()
        self.game_ui.draw_game_over_screen(
            self.screen, self.score, self.game_stats, self.game_completed
        )

    def run(self):
        """
        主遊戲迴圈\n
        """
        while self.running:
            # 處理事件
            self.event_handler.handle_events()

            # 更新遊戲邏輯
            self.update_game()

            # 渲染畫面
            self.render()

            # 控制幀率
            self.clock.tick(FPS)

        # 清理並退出
        pygame.quit()
