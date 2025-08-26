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
        self.health_display_mode = "bar"

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

        # 創建玩家
        player_start_x = SCREEN_WIDTH // 2 - PLAYER_SIZE // 2
        player_start_y = SCREEN_HEIGHT - 100
        self.player = Player(player_start_x, player_start_y, self.player_max_health)

        # 創建初始敵人
        self._spawn_enemy()

        # 清空所有管理系統
        self.bullet_manager.clear_all_bullets()
        self.powerup_manager.clear_all_powerups()

        # 顯示遊戲開始訊息
        self.game_ui.add_message("遊戲開始！", "achievement", COLORS["green"])

    def _spawn_enemy(self):
        """
        生成新敵人\n
        \n
        在螢幕上方隨機位置生成敵人\n
        """
        # 隨機選擇生成位置（螢幕上方）
        enemy_x = random.randint(50, SCREEN_WIDTH - ENEMY_SIZE - 50)
        enemy_y = random.randint(50, 150)

        # 創建敵人
        enemy = Enemy(enemy_x, enemy_y, self.enemy_difficulty)
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
            # 選單狀態的按鍵處理
            if key == pygame.K_SPACE:
                self.start_new_game()
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
            elif key == KEYS["skill"]:
                if self.player and self.player.use_skill():
                    self.game_ui.add_message(
                        "技能啟動！", "achievement", COLORS["purple"]
                    )

        elif self.game_state == GAME_STATES["game_over"]:
            # 遊戲結束狀態的按鍵處理
            if key == pygame.K_r:
                self.start_new_game()
            elif key == pygame.K_ESCAPE:
                self.game_state = GAME_STATES["menu"]

    def _handle_continuous_input(self):
        """
        處理需要連續檢測的輸入（如移動和射擊）\n
        """
        keys = pygame.key.get_pressed()

        # 處理移動
        self.player.handle_input(keys)

        # 處理射擊
        if keys[KEYS["fire"]]:
            shot_data = self.player.shoot()
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
            f"血量顯示: {'血條' if self.health_display_mode == 'bar' else '數字'} (按 H 切換)",
            "",
            "操作說明:",
            "WASD - 移動",
            "空白鍵 - 射擊",
            "R - 填裝",
            "1/2/3 - 切換武器",
            "Q - 使用技能",
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
        game = BattleArenaGame()
        game.run()

    except Exception as e:
        print(f"遊戲運行發生錯誤: {e}")
        pygame.quit()
        sys.exit(1)


# 直接執行主程式
main()
