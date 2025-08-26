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

        # 遊戲選擇狀態
        self.selected_character = "cat"  # 預設角色
        self.selected_scene = "mountain"  # 預設場景
        self.character_menu_index = 0  # 角色選單索引
        self.scene_menu_index = 0  # 場景選單索引

        # 初始化遊戲系統
        self._init_game_systems()

        # 遊戲統計
        self.score = 0
        self.game_stats = {
            "enemies_killed": 0,
            "shots_fired": 0,
            "shots_hit": 0,
            "powerups_collected": 0,
            "game_time": 0,
        }

        # 計時器
        self.game_start_time = 0

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

        # 遊戲物件列表
        self.enemies = []
        self.player = None

    def start_new_game(self):
        """
        開始新遊戲\n
        \n
        重置所有遊戲狀態並創建新的遊戲物件\n
        """
        # 重置遊戲狀態
        self.game_state = GAME_STATES["playing"]
        self.score = 0
        self.game_stats = {
            "enemies_killed": 0,
            "shots_fired": 0,
            "shots_hit": 0,
            "powerups_collected": 0,
            "game_time": 0,
        }
        self.game_start_time = pygame.time.get_ticks()

        # 創建玩家（使用選擇的角色）
        player_start_x = SCREEN_WIDTH // 2 - PLAYER_SIZE // 2
        player_start_y = SCREEN_HEIGHT - 100
        self.player = Player(
            player_start_x, 
            player_start_y, 
            self.player_max_health, 
            character_type=self.selected_character
        )

        # 應用場景效果
        self._apply_scene_effects()

        # 創建初始敵人（使用隨機敵人類型）
        self._spawn_enemy()

        # 清空所有管理系統
        self.bullet_manager.clear_all_bullets()
        self.powerup_manager.clear_all_powerups()

        # 顯示遊戲開始訊息
        character_name = CHARACTER_TYPES[self.selected_character]["name"]
        scene_name = SCENE_CONFIGS[self.selected_scene]["name"]
        self.game_ui.add_message(f"角色: {character_name} | 場景: {scene_name}", "achievement", COLORS["green"])
        self.game_ui.add_message("遊戲開始！", "achievement", COLORS["yellow"])

    def _apply_scene_effects(self):
        """
        應用場景特殊效果\n
        """
        scene_config = SCENE_CONFIGS[self.selected_scene]
        
        # 根據場景調整玩家屬性
        if self.selected_scene == "lava":
            # 岩漿場景：火焰傷害加成
            if hasattr(self.player, 'powerups'):
                self.player.powerups["fire_boost"] = {
                    "remaining_time": float('inf'),  # 永久效果
                    "source": "scene_effect"
                }
        elif self.selected_scene == "ice":
            # 冰場景：移動速度減少
            if hasattr(self.player, 'speed'):
                self.player.speed *= 0.85  # 減少15%移動速度

    def _spawn_enemy(self):
        """
        生成新敵人\n
        \n
        在螢幕上方隨機位置生成敵人\n
        """
        # 隨機選擇生成位置（螢幕上方）
        enemy_x = random.randint(50, SCREEN_WIDTH - ENEMY_SIZE - 50)
        enemy_y = random.randint(50, 150)

        # 隨機選擇敵人類型
        enemy_types = list(ENEMY_TYPES.keys())
        enemy_type = random.choice(enemy_types)

        # 創建敵人（使用類型和難度）
        enemy = Enemy(enemy_x, enemy_y, self.enemy_difficulty, enemy_type=enemy_type)
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

            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)

        # 處理連續按鍵
        if self.game_state == GAME_STATES["playing"] and self.player:
            self._handle_continuous_input()

    def _handle_keydown(self, key):
        """
        處理按鍵按下事件\n
        \n
        參數:\n
        key: 按下的按鍵\n
        """
        if self.game_state == GAME_STATES["menu"]:
            self._handle_menu_keydown(key)
        elif self.game_state == GAME_STATES["character_select"]:
            self._handle_character_select_keydown(key)
        elif self.game_state == GAME_STATES["scene_select"]:
            self._handle_scene_select_keydown(key)
        elif self.game_state == GAME_STATES["playing"]:
            self._handle_playing_keydown(key)
        elif self.game_state == GAME_STATES["game_over"]:
            self._handle_game_over_keydown(key)

    def _handle_menu_keydown(self, key):
        """處理主選單按鍵"""
        if key == pygame.K_SPACE or key == pygame.K_RETURN:
            # 開始角色選擇
            self.game_state = GAME_STATES["character_select"]
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

    def _handle_character_select_keydown(self, key):
        """處理角色選擇按鍵"""
        character_types = list(CHARACTER_TYPES.keys())
        
        if key == pygame.K_UP:
            self.character_menu_index = (self.character_menu_index - 1) % len(character_types)
            self.selected_character = character_types[self.character_menu_index]
        elif key == pygame.K_DOWN:
            self.character_menu_index = (self.character_menu_index + 1) % len(character_types)
            self.selected_character = character_types[self.character_menu_index]
        elif key == pygame.K_RETURN:
            # 進入場景選擇
            self.game_state = GAME_STATES["scene_select"]
        elif key == pygame.K_ESCAPE:
            # 返回主選單
            self.game_state = GAME_STATES["menu"]

    def _handle_scene_select_keydown(self, key):
        """處理場景選擇按鍵"""
        scene_types = list(SCENE_CONFIGS.keys())
        
        if key == pygame.K_UP:
            self.scene_menu_index = (self.scene_menu_index - 1) % len(scene_types)
            self.selected_scene = scene_types[self.scene_menu_index]
        elif key == pygame.K_DOWN:
            self.scene_menu_index = (self.scene_menu_index + 1) % len(scene_types)
            self.selected_scene = scene_types[self.scene_menu_index]
        elif key == pygame.K_RETURN:
            # 開始遊戲
            self.start_new_game()
        elif key == pygame.K_ESCAPE:
            # 返回角色選擇
            self.game_state = GAME_STATES["character_select"]

    def _handle_playing_keydown(self, key):
        """處理遊戲中按鍵"""
        if key == pygame.K_ESCAPE:
            # 暫停或返回選單
            self.game_state = GAME_STATES["menu"]
        elif key == pygame.K_r:
            # 重新開始遊戲
            self.start_new_game()
        elif key == pygame.K_q and self.player:
            # 使用技能
            skill_result = self.player.use_skill()
            if skill_result.get("success"):
                # 應用技能效果
                self.collision_system.apply_skill_effects(
                    skill_result, self.enemies, SCREEN_WIDTH, SCREEN_HEIGHT
                )
                self.game_ui.add_message(
                    f"使用技能: {skill_result['name']}", "achievement"
                )
        elif self.player and key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
            # 武器切換
            self.player.handle_weapon_switch(str(key - pygame.K_0))

    def _handle_game_over_keydown(self, key):
        """處理遊戲結束按鍵"""
        if key == pygame.K_r:
            # 重新開始遊戲
            self.start_new_game()
        elif key == pygame.K_ESCAPE:
            # 返回主選單
            self.game_state = GAME_STATES["menu"]

    def _handle_continuous_input(self):
        """
        處理需要連續檢測的輸入（如移動和射擊）\n
        """
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        # 處理滑鼠右鍵重開遊戲
        if mouse_buttons[2]:  # 右鍵（索引2）
            # 防止重複觸發，需要檢查是否剛按下
            if not hasattr(self, '_right_mouse_pressed'):
                self._right_mouse_pressed = True
                self.start_new_game()
        else:
            self._right_mouse_pressed = False

        # 處理移動（滑鼠優先，如果沒有滑鼠移動則使用鍵盤）
        self.player.handle_input(keys, mouse_pos, mouse_buttons)

        # 處理射擊（支援滑鼠左鍵和空白鍵）
        should_shoot = (
            keys[KEYS["fire"]] or mouse_buttons[0]
        )  # 空白鍵或滑鼠左鍵（索引0）

        if should_shoot:
            # 使用更新的射擊方法，直接通過 BulletManager 創建子彈
            shot_result = self.player.shoot(self.bullet_manager)
            if shot_result:
                # 統計射擊次數
                self.game_stats["shots_fired"] += shot_result["bullet_count"]
            # 使用更新的射擊方法，直接通過 BulletManager 創建子彈
            shot_result = self.player.shoot(self.bullet_manager)
            if shot_result:
                # 統計射擊次數
                self.game_stats["shots_fired"] += shot_result["bullet_count"]

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
            self.game_state = GAME_STATES["game_over"]
            return

        # 更新敵人
        for enemy in self.enemies[:]:
            if enemy.is_alive:
                enemy.update(self.player, SCREEN_WIDTH, SCREEN_HEIGHT)

                # 敵人射擊
                shot_data = enemy.shoot(self.player)
                if shot_data:
                    self.bullet_manager.create_bullet(
                        shot_data["x"],
                        shot_data["y"],
                        shot_data["angle"],
                        shot_data["speed"],
                        shot_data["damage"],
                        shot_data["owner"],
                    )
            else:
                # 移除死亡的敵人
                self.enemies.remove(enemy)
                self.game_stats["enemies_killed"] += 1
                self.score += 100

                # 敵人死亡時可能掉落道具
                self.powerup_manager.spawn_powerup_on_enemy_death(enemy.x, enemy.y)

                self.game_ui.add_message(f"+100 分", "achievement", COLORS["yellow"])

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

        # 檢查是否需要生成新敵人
        if len(self.enemies) == 0:
            self._spawn_enemy()
        elif len(self.enemies) < 2 and random.random() < 0.005:  # 小機率生成第二個敵人
            self._spawn_enemy()

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
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_surface, title_rect)

        # 副標題
        subtitle_text = "射擊對戰遊戲"
        subtitle_surface = font_manager.render_text(
            subtitle_text, "medium", COLORS["gray"]
        )
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, 190))
        self.screen.blit(subtitle_surface, subtitle_rect)

        # 選單選項
        menu_items = [
            "按 SPACE 開始遊戲",
            "",
            "遊戲設定:",
            f"AI難度: {AI_CONFIGS[self.enemy_difficulty]['name']} (按 1/2/3 切換)",
            f"玩家血量: {self.player_max_health} (+/-調整)",
            f"血量顯示: {'數字' if self.health_display_mode == 'number' else '血條'} (按 H 切換)",
            "",
            "操作說明:",
            "滑鼠 - 移動（滑鼠位置控制角色移動）",
            "滑鼠右鍵 - 射擊",
            "或使用 WASD - 移動，空白鍵 - 射擊",
            "R - 填裝",
            "1/2/3/4/5 - 切換武器",
            "Q - 使用技能（消耗10%生命值，全螢幕攻擊）",
            "ESC - 返回選單",
        ]

        start_y = 250
        for i, item in enumerate(menu_items):
            if item:  # 跳過空字串
                color = COLORS["yellow"] if "按" in item else COLORS["white"]
                text_surface = font_manager.render_text(item, "small", color)
                text_rect = text_surface.get_rect(
                    center=(SCREEN_WIDTH // 2, start_y + i * 25)
                )
                self.screen.blit(text_surface, text_rect)

    def draw_game(self):
        """
        繪製遊戲畫面\n
        """
        # 背景
        self.screen.fill(COLORS["black"])

        # 繪製遊戲物件
        if self.player:
            self.player.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        self.bullet_manager.draw(self.screen)
        self.powerup_manager.draw(self.screen)

        # 繪製UI
        self.game_ui.draw(
            self.screen, self.player, self.enemies, self.score, self.game_stats
        )

    def draw_game_over(self):
        """
        繪製遊戲結束畫面\n
        """
        # 先繪製遊戲畫面作為背景
        self.draw_game()

        # 繪製遊戲結束UI
        self.game_ui.draw_game_over_screen(self.screen, self.score, self.game_stats)

    def render(self):
        """
        渲染當前遊戲狀態\n
        """
        if self.game_state == GAME_STATES["menu"]:
            self.draw_menu()
        elif self.game_state == GAME_STATES["character_select"]:
            self.draw_character_selection()
        elif self.game_state == GAME_STATES["scene_select"]:
            self.draw_scene_selection()
        elif self.game_state == GAME_STATES["playing"]:
            self.draw_game()
        elif self.game_state == GAME_STATES["game_over"]:
            self.draw_game_over()

        # 更新顯示
        pygame.display.flip()

    def draw_character_selection(self):
        """
        繪製角色選擇畫面\n
        """
        # 清空螢幕
        self.screen.fill(COLORS["black"])
        
        # 使用 GameUI 繪製角色選擇選單
        self.game_ui.draw_character_selection_menu(self.screen, self.selected_character)

    def draw_scene_selection(self):
        """
        繪製場景選擇畫面\n
        """
        # 清空螢幕
        self.screen.fill(COLORS["black"])
        
        # 使用 GameUI 繪製場景選擇選單
        self.game_ui.draw_scene_selection_menu(self.screen, self.selected_scene)

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
        game = BattleArenaGame()
        game.run()

    except Exception as e:
        print(f"遊戲運行發生錯誤: {e}")
        pygame.quit()
        sys.exit(1)


# 直接執行主程式
main()
