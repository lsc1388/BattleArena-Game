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

######################主遊戲類別######################


class BattleArenaGame:
    """
    BattleArena 主遊戲類別 - 統籌整個遊戲的運行\n
    \n
    此類別負責：\n
    1. 遊戲狀態管理（選單、遊戲中、結束）\n
    2. 所有遊戲物件的協調和更新\n
    3. 事件處理和輸入控制\n
    4. 遊戲邏輯和勝負判定\n
    5. 畫面渲染和音效管理\n
    """

    def __init__(self):
        """
        初始化遊戲系統\n
        """
        # 初始化pygame
        pygame.init()

        # 建立遊戲視窗
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("BattleArena - 射擊對戰遊戲")

        # 時鐘控制
        self.clock = pygame.time.Clock()

        # 遊戲狀態
        self.game_state = GAME_STATES["menu"]
        self.running = True

        # 遊戲設定
        self.player_max_health = PLAYER_DEFAULT_HEALTH
        self.enemy_difficulty = "medium"
        self.health_display_mode = "number"  # 預設使用數字顯示

        # 角色和場景選擇
        self.selected_character = "cat"  # 預設角色
        self.selected_difficulty = "easy"  # 預設難度
        self.selected_scene = "lava"  # 預設場景

        # 初始化遊戲系統
        self._init_game_systems()

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
        self.enemy_spawn_count = 1  # 當前應該存在的敵人數量
        self.enemy_types_pool = ["robot", "alien", "zombie"]  # 敵人類型池
        self.current_level_enemy_type = "zombie"  # 當前關卡的敵人類型

    def start_new_game(self):
        """
        開始新遊戲\n
        \n
        重置所有遊戲狀態並創建新的遊戲物件\n
        """
        # 重置遊戲狀態
        self.game_state = GAME_STATES["playing"]
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
        self.game_start_time = pygame.time.get_ticks()
        self.last_skill_activation = 0
        self.last_skill_damage_time = 0

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
        self.enemy_spawn_count = 1  # 重置敵人數量
        # 根據 LEVEL_CONFIGS 決定當前關卡的敵人池（可能為混合）
        level_config = LEVEL_CONFIGS[self.selected_difficulty][self.current_level]
        self.current_level_enemy_counts = level_config.get("enemy_counts", {})
        # 設置關卡場景
        if "scene" in level_config:
            self.selected_scene = level_config["scene"]
        self.enemies.clear()

        # 創建初始敵人（生成一隻以啟動流程）
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

    def _spawn_enemy(self):
        """
        生成新敵人\n
        \n
        在螢幕上方隨機位置生成敵人，根據當前關卡選擇敵人類型\n
        """
        # 隨機選擇生成位置（螢幕上方）
        enemy_x = random.randint(50, SCREEN_WIDTH - ENEMY_SIZE - 50)
        enemy_y = random.randint(50, 150)

        # 根據當前關卡選擇敵人類型（支援混合）
        level_config = LEVEL_CONFIGS[self.selected_difficulty][self.current_level]
        enemy_counts = level_config.get("enemy_counts", {})

        # 如果是第三關且已經完成所有普通敵人但還沒生成 BOSS，則生成 BOSS
        if level_config.get("boss", False):
            total_needed = level_config.get("enemy_count", 0)
            # 計算目前已經擊殺與場上的普通敵人數
            current_alive_normal = len(
                [e for e in self.enemies if e.enemy_type != "boss" and e.is_alive]
            )
            killed = self.level_enemies_killed

            # 如果普通敵人已全部產生並被擊殺且沒有 BOSS 在場，就生成 BOSS
            if killed >= total_needed and not any(
                e.enemy_type == "boss" for e in self.enemies
            ):
                boss_x = SCREEN_WIDTH // 2 - ENEMY_SIZE * 3 // 2
                boss_y = 80
                boss = Enemy(boss_x, boss_y, self.enemy_difficulty, "boss")
                self.enemies.append(boss)
                self.game_ui.add_message("BOSS 出現！", "achievement", COLORS["purple"])
                return

        # 若為一般生成，從 enemy_counts 池中隨機抽一種類型
        if enemy_counts:
            types = []
            for t, cnt in enemy_counts.items():
                # 將每種敵人加入權重列表，讓出現機率與需求數量成比例
                types.extend([t] * max(1, cnt))
            enemy_type = random.choice(types)
        else:
            # 回退：若沒有指定則使用 zombie
            enemy_type = "zombie"

        # 創建敵人
        enemy = Enemy(enemy_x, enemy_y, self.enemy_difficulty, enemy_type)
        self.enemies.append(enemy)

    def handle_events(self):
        """
        處理所有遊戲事件\n
        \n
        包括按鍵輸入、視窗事件等\n
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 處理滑鼠點擊事件
                self._handle_mouse_click(event.button, event.pos)

            # 優先處理選擇界面事件
            elif self.game_state in [
                GAME_STATES["character_select"],
                GAME_STATES["difficulty_select"],  # 新增難度選擇狀態
                GAME_STATES["scene_select"],
            ]:
                selection_result = self.selection_ui.handle_input(event)
                self._handle_selection_result(selection_result)

            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)

        # 處理連續按鍵
        if self.game_state == GAME_STATES["playing"] and self.player:
            self._handle_continuous_input()

    def _handle_mouse_click(self, button, pos):
        """
        處理滑鼠點擊事件
        根據 target.prompt.md 規格：
        - 射擊控制：滑鼠左鍵發射子彈
        - 重新開始：滑鼠右鍵重新開始遊戲

        參數:
        button (int): 滑鼠按鈕（1=左鍵, 3=右鍵）
        pos (tuple): 滑鼠點擊位置
        """
        if self.game_state == GAME_STATES["playing"] and self.player:
            if button == 1:  # 滑鼠左鍵 - 射擊
                # 朝滑鼠位置射擊（準心正中心）
                shot_data = self.player.shoot(target_pos=pos)
                if shot_data:
                    # 發射子彈
                    for bullet_info in shot_data["bullets"]:
                        self.bullet_manager.create_bullet(
                            bullet_info["x"],
                            bullet_info["y"],
                            bullet_info["angle"],
                            bullet_info["speed"],
                            bullet_info["damage"],
                            "player",
                        )
                    self.game_stats["shots_fired"] += len(shot_data["bullets"])
            elif button == 3:  # 滑鼠右鍵 - 重新開始遊戲
                self.start_new_game()

        elif self.game_state == GAME_STATES["game_over"]:
            if button == 3:  # 滑鼠右鍵 - 重新開始遊戲
                self.start_new_game()
        elif self.game_state == GAME_STATES["menu"]:
            if button == 3:  # 選單中也可以右鍵重啟（清除設定）
                self.player_max_health = PLAYER_DEFAULT_HEALTH
                self.enemy_difficulty = "medium"
                self.selected_character = "cat"
                self.selected_scene = "lava"

    def _handle_selection_result(self, result):
        """
        處理選擇界面的結果

        參數:
        result (dict): 選擇結果
        """
        action = result.get("action", "none")

        if action == "back_to_menu":
            self.game_state = GAME_STATES["menu"]
        elif action == "character_selected":
            self.selected_character = result["character"]
            self.game_state = GAME_STATES["difficulty_select"]  # 改為跳轉到難度選擇
            self.selection_ui.current_selection_type = "difficulty"  # 設置選擇類型
        elif action == "difficulty_selected":
            self.selected_difficulty = result["difficulty"]
            self.game_state = GAME_STATES["scene_select"]
            self.selection_ui.current_selection_type = "scene"  # 設置選擇類型
        elif action == "scene_selected":
            self.selected_scene = result["scene"]
            self.selected_character = result["character"]
            # 選擇完畢，開始遊戲
            self.start_new_game()

    def _handle_keydown(self, key):
        """
        處理按鍵按下事件\n
        \n
        參數:\n
        key: 按下的按鍵\n
        """
        if self.game_state == GAME_STATES["menu"]:
            # 選單狀態的按鍵處理
            if key == pygame.K_SPACE:
                # 進入角色選擇
                self.game_state = GAME_STATES["character_select"]
                self.selection_ui.reset_selection()
            elif key == pygame.K_1:
                self.enemy_difficulty = "weak"
            elif key == pygame.K_2:
                self.enemy_difficulty = "medium"
            elif key == pygame.K_3:
                self.enemy_difficulty = "strong"
            elif key == pygame.K_h:
                # 切換血量顯示模式
                if self.health_display_mode == "bar":
                    self.health_display_mode = "number"
                else:
                    self.health_display_mode = "bar"
                self.game_ui.set_health_display_mode(self.health_display_mode)
            elif key == pygame.K_PLUS or key == pygame.K_EQUALS:
                # 增加玩家血量
                self.player_max_health = min(200, self.player_max_health + 10)
            elif key == pygame.K_MINUS:
                # 減少玩家血量
                self.player_max_health = max(50, self.player_max_health - 10)

        elif self.game_state == GAME_STATES["playing"]:
            # 遊戲中的按鍵處理
            if key == pygame.K_ESCAPE:
                self.game_state = GAME_STATES["menu"]
            elif key == KEYS["reload"]:
                if self.player:
                    if self.player.start_reload():
                        self.game_ui.add_message("填裝中...", "info", COLORS["yellow"])
            elif key == KEYS["weapon_1"]:
                if self.player and self.player.handle_weapon_switch("1"):
                    self.game_ui.add_message("切換至手槍", "info")
            elif key == KEYS["weapon_2"]:
                if self.player and self.player.handle_weapon_switch("2"):
                    self.game_ui.add_message("切換至步槍", "info")
            elif key == KEYS["weapon_3"]:
                if self.player and self.player.handle_weapon_switch("3"):
                    self.game_ui.add_message("切換至散彈槍", "info")
            elif key == KEYS["weapon_4"]:
                if self.player and self.player.handle_weapon_switch("4"):
                    self.game_ui.add_message("切換至機關槍", "info")
            elif key == KEYS["weapon_5"]:
                if self.player and self.player.handle_weapon_switch("5"):
                    self.game_ui.add_message("切換至衝鋒槍", "info")
            elif key == KEYS["skill"]:
                if self.player:
                    skill_result = self.player.use_skill()
                    if skill_result["success"]:
                        # 顯示技能啟動訊息
                        skill_message = f"{skill_result['skill_name']}啟動！"
                        self.game_ui.add_message(
                            skill_message,
                            "achievement",
                            skill_result["effect_color"],
                        )
                        self.game_ui.add_message(
                            f"消耗生命值 {skill_result['health_cost']}",
                            "damage",
                            COLORS["red"],
                        )

                        # 記錄技能啟動（持續傷害將在update中處理）
                        self.last_skill_activation = pygame.time.get_ticks()
                    else:
                        self.game_ui.add_message(
                            skill_result["reason"], "info", COLORS["yellow"]
                        )
            elif key == pygame.K_c:
                # 切換準心顯示
                self.game_ui.crosshair_enabled = not self.game_ui.crosshair_enabled
                if self.game_ui.crosshair_enabled:
                    self.game_ui.add_message("準心已開啟", "info", COLORS["green"])
                else:
                    self.game_ui.add_message("準心已關閉", "info", COLORS["orange"])

            # 開發/測試用快捷鍵（F1: 立即召喚 BOSS, F2: 標記當前關卡已完成）
            elif key == pygame.K_F1:
                # 直接在場上生成 BOSS（如果還沒生成）
                if not any(e.enemy_type == "boss" for e in self.enemies):
                    boss_x = SCREEN_WIDTH // 2 - ENEMY_SIZE * 3 // 2
                    boss_y = 80
                    boss = Enemy(boss_x, boss_y, self.enemy_difficulty, "boss")
                    self.enemies.append(boss)
                    self.game_ui.add_message(
                        "測試: 已召喚 BOSS", "info", COLORS["purple"]
                    )
            elif key == pygame.K_F2:
                # 標記本關卡已完成（快速跳關）
                level_config = LEVEL_CONFIGS.get(self.selected_difficulty, {}).get(
                    self.current_level, {}
                )
                self.level_enemies_killed = level_config.get("enemy_count", 0)
                self.game_ui.add_message(
                    "測試: 本關標記為已完成", "info", COLORS["blue"]
                )

        elif self.game_state == GAME_STATES["game_over"]:
            # 遊戲結束狀態的按鍵處理
            if key == pygame.K_r:
                self.start_new_game()
            elif key == pygame.K_ESCAPE:
                self.game_state = GAME_STATES["menu"]

    def _handle_continuous_input(self):
        """
        處理需要連續檢測的輸入（WASD移動，滑鼠準心）\n
        根據 target.prompt.md 規格：\n
        - 移動控制：WASD 控制角色位置，滑鼠無法控制移動\n
        - 射擊準心：滑鼠移動準心，子彈命中位置為準心正中心\n
        """
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        # 只使用鍵盤控制移動，不傳入滑鼠位置進行移動控制
        self.player.handle_input(keys, mouse_pos=None, mouse_buttons=None)

        # 處理滑鼠射擊（左鍵連續按住時持續射擊）
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:  # 滑鼠左鍵
            # 朝準心位置射擊
            shot_data = self.player.shoot(target_pos=mouse_pos)
            if shot_data:
                # 發射子彈
                for bullet_info in shot_data["bullets"]:
                    self.bullet_manager.create_bullet(
                        bullet_info["x"],
                        bullet_info["y"],
                        bullet_info["angle"],
                        bullet_info["speed"],
                        bullet_info["damage"],
                        "player",
                    )

                self.game_stats["shots_fired"] += len(shot_data["bullets"])

    def update_game(self):
        """
        更新遊戲邏輯（每幀呼叫）\n
        """
        if self.game_state != GAME_STATES["playing"]:
            return

        # 更新遊戲時間
        current_time = pygame.time.get_ticks()
        self.game_stats["game_time"] = (current_time - self.game_start_time) / 1000

        # 更新玩家
        if self.player and self.player.is_alive:
            self.player.update(SCREEN_WIDTH, SCREEN_HEIGHT)
        else:
            # 玩家死亡，遊戲結束
            if not self.game_completed:  # 只有在未完成遊戲時才視為失敗
                self.game_state = GAME_STATES["game_over"]
            return

        # 檢查遊戲完成條件
        if self.game_completed:
            self.game_state = GAME_STATES["game_over"]
            return

        # 處理技能持續效果
        self._update_skill_effects()

        # 更新敵人
        enemies_killed_this_frame = 0
        for enemy in self.enemies[:]:
            if enemy.is_alive:
                enemy.update(self.player, SCREEN_WIDTH, SCREEN_HEIGHT)

                # 敵人射擊（支援單發 dict 或 多發 list 回傳）
                shot_data = enemy.shoot(self.player)
                if shot_data:
                    # 如果回傳為 list，表示多發子彈（例如 BOSS 放射攻擊）
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

        # 檢查關卡完成條件
        self._check_level_completion()

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

        # AI增殖機制：依據關卡設定生成敵人
        if not self.game_completed:
            # 檢查是否需要生成新敵人（僅在關卡未完成時）
            current_enemy_count = len([e for e in self.enemies if e.is_alive])
            level_config = LEVEL_CONFIGS[self.selected_difficulty][self.current_level]
            remaining_enemies_needed = (
                level_config["enemy_count"] - self.level_enemies_killed
            )

            if current_enemy_count == 0 and remaining_enemies_needed > 0:
                # 如果沒有敵人了但還需要更多敵人，就生成一個
                self._spawn_enemy()
            elif current_enemy_count < 2 and remaining_enemies_needed > 1:
                # 如果敵人太少且還需要很多敵人，保持至少2個在場上
                self._spawn_enemy()

    def _update_skill_effects(self):
        """
        更新技能持續效果\n
        \n
        處理技能的持續傷害效果，每秒對所有敵人造成傷害\n
        """
        if not self.player or not self.player.is_skill_active():
            return

        current_time = pygame.time.get_ticks()

        # 每秒造成一次傷害
        if current_time - self.last_skill_damage_time >= 1000:
            skill_info = self.player.get_active_skill_info()
            if skill_info:
                enemies_hit = 0
                for enemy in self.enemies:
                    if enemy.is_alive:
                        # 每秒造成技能傷害的1/3（因為持續3秒）
                        damage_per_second = skill_info["damage"] // 3
                        if enemy.take_damage(damage_per_second):
                            enemies_hit += 1
                        else:
                            # 敵人被技能擊殺
                            enemies_hit += 1

                if enemies_hit > 0:
                    self.game_ui.add_message(
                        f"技能持續傷害：{enemies_hit} 個敵人",
                        "info",
                        skill_info["effect_color"],
                    )

                self.last_skill_damage_time = current_time

    def _check_level_completion(self):
        """
        檢查關卡完成條件\n
        \n
        根據 target.prompt.md 規格：\n
        - 第一關：擊殺 3 個殭屍\n
        - 第二關：擊殺 5 個外星人\n
        - 完成所有關卡後顯示「你贏了」\n
        """
        if self.game_completed:
            return

        level_config = LEVEL_CONFIGS[self.selected_difficulty][self.current_level]

        # 如果關卡有 BOSS，先判斷 BOSS 是否存在且已被擊敗
        if level_config.get("boss", False):
            # 如果 BOSS 在場且已死亡，視為關卡完成
            boss_alive = any(
                e.enemy_type == "boss" and e.is_alive for e in self.enemies
            )
            if not boss_alive and self.level_enemies_killed >= level_config.get(
                "enemy_count", 0
            ):
                # 完成第三關（含 BOSS）
                self.game_ui.add_message(
                    level_config["completion_message"], "achievement", COLORS["green"]
                )
                self.game_completed = True
                self.enemies.clear()
                return

        # 一般情況：檢查是否已擊殺足夠的普通敵人
        required = level_config.get("enemy_count", 0)
        if self.level_enemies_killed >= required:
            # 如果還有下一關則進入下一關
            self.game_ui.add_message(
                level_config.get("completion_message", "關卡完成！"),
                "achievement",
                COLORS["green"],
            )

            if self.current_level < len(LEVEL_CONFIGS[self.selected_difficulty]):
                # 進入下一關
                self.current_level += 1
                self.level_enemies_killed = 0
                # 重新設置敵人池
                next_level_config = LEVEL_CONFIGS[self.selected_difficulty][
                    self.current_level
                ]
                self.current_level_enemy_counts = next_level_config.get(
                    "enemy_counts", {}
                )
                # 更新場景背景
                if "scene" in next_level_config:
                    self.selected_scene = next_level_config["scene"]
                self.enemies.clear()

                # 顯示新關卡資訊
                self.game_ui.add_message(
                    f"{next_level_config['name']}", "achievement", COLORS["blue"]
                )
                self.game_ui.add_message(
                    f"{next_level_config['description']}", "info", COLORS["yellow"]
                )
            else:
                # 沒有更多關卡，直接完成遊戲
                self.game_completed = True
                self.enemies.clear()
                self.game_ui.add_message(
                    "遊戲完成！",
                    "achievement",
                    COLORS["gold"] if "gold" in COLORS else COLORS["yellow"],
                )

    def _process_collision_results(self, results):
        """
        處理碰撞檢測結果\n
        \n
        參數:\n
        results (dict): 碰撞檢測結果\n
        """
        # 處理玩家被擊中
        if results["player_hit"]:
            self.game_ui.add_message("受到攻擊！", "damage", COLORS["red"])

        # 處理敵人被擊中
        for hit_info in results["enemies_hit"]:
            self.game_stats["shots_hit"] += hit_info["bullets_count"]
            if hit_info["killed"]:
                self.game_ui.add_message("敵人被擊敗！", "achievement", COLORS["green"])

        # 處理驚喜包拾取
        for powerup_info in results["powerups_collected"]:
            self.game_stats["powerups_collected"] += 1
            self.game_ui.add_message(
                powerup_info["message"], "powerup", COLORS["yellow"]
            )
            self.score += 50  # 拾取道具獲得分數

    def draw_menu(self):
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

        # 選單選項
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
            if item:  # 跳過空字串
                color = COLORS["yellow"] if "按" in item else COLORS["white"]
                text_surface = font_manager.render_text(item, "small", color)
                text_rect = text_surface.get_rect(
                    center=(SCREEN_WIDTH // 2, start_y + i * 18)
                )
                self.screen.blit(text_surface, text_rect)

    def draw_game(self):
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

    def draw_game_over(self):
        """
        繪製遊戲結束畫面\n
        """
        # 先繪製遊戲畫面作為背景
        self.draw_game()

        # 繪製遊戲結束UI，傳入遊戲完成狀態
        self.game_ui.draw_game_over_screen(
            self.screen, self.score, self.game_stats, self.game_completed
        )

    def render(self):
        """
        渲染當前遊戲狀態\n
        """
        if self.game_state == GAME_STATES["menu"]:
            self.draw_menu()
        elif self.game_state in [
            GAME_STATES["character_select"],
            GAME_STATES["difficulty_select"],  # 新增難度選擇狀態
            GAME_STATES["scene_select"],
        ]:
            self.selection_ui.draw(self.screen)
        elif self.game_state == GAME_STATES["playing"]:
            self.draw_game()
        elif self.game_state == GAME_STATES["game_over"]:
            self.draw_game_over()

        # 更新顯示
        pygame.display.flip()

    def run(self):
        """
        主遊戲迴圈\n
        """
        while self.running:
            # 處理事件
            self.handle_events()

            # 更新遊戲邏輯
            self.update_game()

            # 渲染畫面
            self.render()

            # 控制幀率
            self.clock.tick(FPS)

        # 清理並退出
        pygame.quit()


######################主程式執行點######################


def main():
    """
    主程式進入點\n
    \n
    創建遊戲實例並開始運行\n
    """
    try:
        # 創建並運行遊戲
        print("🎮 開始初始化遊戲...")
        game = BattleArenaGame()
        print("🎮 遊戲初始化完成，開始運行...")
        game.run()

    except Exception as e:
        import traceback

        print(f"遊戲運行發生錯誤: {e}")
        print("詳細錯誤信息:")
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)


# 直接執行主程式
main()
