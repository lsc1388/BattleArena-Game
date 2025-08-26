######################載入套件######################
import pygame
import math
from src.config import *
from src.utils.font_manager import font_manager

######################UI系統######################


class GameUI:
    """
    遊戲UI系統 - 處理所有遊戲介面元素的顯示\n
    \n
    此系統負責：\n
    1. 玩家生命值顯示（血條/數字）\n
    2. 武器資訊和彈藥計數\n
    3. 強化效果狀態顯示\n
    4. 遊戲計分和統計\n
    5. 技能冷卻時間指示\n
    6. 訊息提示系統\n
    """

    def __init__(self, screen_width, screen_height):
        """
        初始化UI系統\n
        \n
        參數:\n
        screen_width (int): 螢幕寬度\n
        screen_height (int): 螢幕高度\n
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        # 使用字體管理器獲取支援中文的字體
        self.font_large = font_manager.get_font("large")
        self.font_medium = font_manager.get_font("medium")
        self.font_small = font_manager.get_font("small")

        # 顯示字體資訊（除錯用）
        font_info = font_manager.get_available_fonts_info()
        print(f"🎨 使用字體: {font_info['current_chinese_font'] or '系統預設字體'}")

        # UI面板位置設定
        self.health_bar_pos = (20, 20)
        self.health_bar_size = (200, 20)
        self.weapon_info_pos = (20, 50)
        self.powerup_list_pos = (20, 100)
        self.score_pos = (screen_width - 150, 20)
        self.skill_cooldown_pos = (screen_width - 150, 60)

        # 訊息系統
        self.messages = []
        self.message_duration = 3000  # 3秒

        # 血量顯示模式（血條或數字）
        self.health_display_mode = "bar"  # 'bar' 或 'number'

    def update(self):
        """
        更新UI狀態（每幀呼叫）\n
        \n
        處理訊息過期、動畫效果等\n
        """
        current_time = pygame.time.get_ticks()

        # 清理過期訊息
        self.messages = [
            msg
            for msg in self.messages
            if current_time - msg["time"] < self.message_duration
        ]

    def draw(self, screen, player, enemies, score, game_stats):
        """
        繪製所有UI元素\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        player: 玩家物件\n
        enemies: 敵人列表\n
        score (int): 當前分數\n
        game_stats (dict): 遊戲統計資料\n
        """
        # 繪製玩家生命值
        self._draw_health_display(screen, player)

        # 繪製武器資訊
        self._draw_weapon_info(screen, player)

        # 繪製強化效果
        self._draw_powerup_effects(screen, player)

        # 繪製分數和統計
        self._draw_score_and_stats(screen, score, game_stats)

        # 繪製技能冷卻
        self._draw_skill_cooldown(screen, player)

        # 繪製敵人血量（在敵人頭上）
        self._draw_enemy_health_bars(screen, enemies)

        # 繪製訊息提示
        self._draw_messages(screen)

        # 繪製小地圖（可選）
        self._draw_minimap(screen, player, enemies)

    def _draw_health_display(self, screen, player):
        """
        繪製玩家生命值顯示\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        player: 玩家物件\n
        """
        if self.health_display_mode == "bar":
            self._draw_health_bar(screen, player)
        else:
            self._draw_health_number(screen, player)

    def _draw_health_bar(self, screen, player):
        """繪製血條"""
        x, y = self.health_bar_pos
        width, height = self.health_bar_size

        # 計算血量比例
        health_ratio = player.health / player.max_health

        # 背景（灰色）
        pygame.draw.rect(screen, COLORS["dark_gray"], (x, y, width, height))

        # 血條（根據血量變色）
        if health_ratio > 0.6:
            health_color = COLORS["green"]
        elif health_ratio > 0.3:
            health_color = COLORS["yellow"]
        else:
            health_color = COLORS["red"]

        health_width = int(width * health_ratio)
        if health_width > 0:
            pygame.draw.rect(screen, health_color, (x, y, health_width, height))

        # 邊框
        pygame.draw.rect(screen, COLORS["white"], (x, y, width, height), 2)

        # 數字標示
        health_text = f"{player.health}/{player.max_health}"
        text_surface = self.font_small.render(health_text, True, COLORS["white"])
        text_x = x + width // 2 - text_surface.get_width() // 2
        text_y = y + height // 2 - text_surface.get_height() // 2
        screen.blit(text_surface, (text_x, text_y))

    def _draw_health_number(self, screen, player):
        """繪製數字血量"""
        x, y = self.health_bar_pos

        # 根據血量選擇顏色
        health_ratio = player.health / player.max_health
        if health_ratio > 0.6:
            color = COLORS["green"]
        elif health_ratio > 0.3:
            color = COLORS["yellow"]
        else:
            color = COLORS["red"]

        health_text = f"生命值: {player.health}/{player.max_health}"
        text_surface = self.font_medium.render(health_text, True, color)
        screen.blit(text_surface, (x, y))

    def _draw_weapon_info(self, screen, player):
        """
        繪製武器資訊\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        player: 玩家物件\n
        """
        x, y = self.weapon_info_pos
        weapon_info = player.get_weapon_info()

        # 武器名稱
        weapon_text = f"武器: {weapon_info['name']}"
        text_surface = self.font_medium.render(weapon_text, True, COLORS["white"])
        screen.blit(text_surface, (x, y))

        # 彈藥資訊
        ammo_y = y + 25
        if weapon_info["is_reloading"]:
            ammo_text = "填裝中..."
            ammo_color = COLORS["yellow"]
        else:
            ammo_text = f"彈藥: {weapon_info['current_ammo']}/{weapon_info['max_ammo']}"
            # 彈藥不足時變紅色
            if weapon_info["current_ammo"] <= 2:
                ammo_color = COLORS["red"]
            else:
                ammo_color = COLORS["white"]

        text_surface = self.font_small.render(ammo_text, True, ammo_color)
        screen.blit(text_surface, (x, ammo_y))

        # 備用彈藥
        total_ammo_y = ammo_y + 20
        total_text = f"備彈: {weapon_info['total_ammo']}"
        text_surface = self.font_small.render(total_text, True, COLORS["gray"])
        screen.blit(text_surface, (x, total_ammo_y))

    def _draw_powerup_effects(self, screen, player):
        """
        繪製強化效果狀態\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        player: 玩家物件\n
        """
        x, y = self.powerup_list_pos
        powerups = player.get_powerup_status()

        if not powerups:
            return

        # 標題
        title_text = "強化效果:"
        text_surface = self.font_small.render(title_text, True, COLORS["white"])
        screen.blit(text_surface, (x, y))

        # 列出每個強化效果
        for i, powerup in enumerate(powerups):
            effect_y = y + 20 + i * 18

            # 效果名稱和剩餘時間
            time_left = int(powerup["remaining_time"])
            effect_text = f"• {powerup['name']} ({time_left}s)"

            # 根據剩餘時間選擇顏色
            if time_left > 3:
                color = COLORS["green"]
            elif time_left > 1:
                color = COLORS["yellow"]
            else:
                color = COLORS["red"]

            text_surface = self.font_small.render(effect_text, True, color)
            screen.blit(text_surface, (x, effect_y))

    def _draw_score_and_stats(self, screen, score, game_stats):
        """
        繪製分數和遊戲統計\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        score (int): 當前分數\n
        game_stats (dict): 遊戲統計資料\n
        """
        x, y = self.score_pos

        # 分數
        score_text = f"分數: {score}"
        text_surface = self.font_medium.render(score_text, True, COLORS["white"])
        screen.blit(text_surface, (x, y))

        # 擊殺數
        if "enemies_killed" in game_stats:
            kills_y = y + 25
            kills_text = f"擊殺: {game_stats['enemies_killed']}"
            text_surface = self.font_small.render(kills_text, True, COLORS["white"])
            screen.blit(text_surface, (x, kills_y))

        # 命中率
        if "shots_fired" in game_stats and game_stats["shots_fired"] > 0:
            accuracy_y = y + 45
            accuracy = (
                game_stats.get("shots_hit", 0) / game_stats["shots_fired"]
            ) * 100
            accuracy_text = f"命中率: {accuracy:.1f}%"
            text_surface = self.font_small.render(accuracy_text, True, COLORS["white"])
            screen.blit(text_surface, (x, accuracy_y))

    def _draw_skill_cooldown(self, screen, player):
        """
        繪製技能冷卻時間\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        player: 玩家物件\n
        """
        x, y = self.skill_cooldown_pos
        skill_info = player.get_skill_cooldown_info()

        if skill_info["ready"]:
            skill_text = "技能: 就緒"
            color = COLORS["green"]
        else:
            cooldown_minutes = int(skill_info["cooldown_remaining"] // 60)
            cooldown_seconds = int(skill_info["cooldown_remaining"] % 60)
            skill_text = f"技能: {cooldown_minutes}:{cooldown_seconds:02d}"
            color = COLORS["red"]

        text_surface = self.font_small.render(skill_text, True, color)
        screen.blit(text_surface, (x, y))

        # 添加技能說明
        skill_desc_y = y + 20
        skill_desc = "Q: 全螢幕攻擊(-10%血量)"
        desc_surface = self.font_small.render(skill_desc, True, COLORS["gray"])
        screen.blit(desc_surface, (x, skill_desc_y))

    def _draw_enemy_health_bars(self, screen, enemies):
        """
        繪製敵人血量條（在敵人頭上）\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        enemies: 敵人列表\n
        """
        for enemy in enemies:
            if not enemy.is_alive:
                continue

            # 計算血量條位置（敵人頭上）
            bar_width = 30
            bar_height = 4
            bar_x = enemy.x + (enemy.width - bar_width) // 2
            bar_y = enemy.y - 10

            # 計算血量比例
            health_ratio = enemy.health / enemy.max_health

            # 背景（深灰色）
            pygame.draw.rect(
                screen, COLORS["dark_gray"], (bar_x, bar_y, bar_width, bar_height)
            )

            # 血量條（根據血量變色）
            if health_ratio > 0.6:
                health_color = COLORS["green"]
            elif health_ratio > 0.3:
                health_color = COLORS["yellow"]
            else:
                health_color = COLORS["red"]

            health_width = int(bar_width * health_ratio)
            if health_width > 0:
                pygame.draw.rect(
                    screen, health_color, (bar_x, bar_y, health_width, bar_height)
                )

    def _draw_messages(self, screen):
        """
        繪製訊息提示\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        """
        # 訊息顯示在螢幕中央偏上
        message_x = self.screen_width // 2
        message_start_y = 100

        current_time = pygame.time.get_ticks()

        for i, message in enumerate(self.messages):
            # 計算訊息透明度（基於剩餘時間）
            time_left = self.message_duration - (current_time - message["time"])
            alpha = min(255, int(255 * (time_left / 1000)))  # 最後1秒淡出

            if alpha <= 0:
                continue

            # 繪製訊息
            message_y = message_start_y + i * 30
            color = message.get("color", COLORS["white"])

            # 如果訊息有特殊顏色需求
            if message.get("type") == "powerup":
                color = COLORS["yellow"]
            elif message.get("type") == "damage":
                color = COLORS["red"]
            elif message.get("type") == "achievement":
                color = COLORS["green"]

            text_surface = self.font_medium.render(message["text"], True, color)
            text_rect = text_surface.get_rect(center=(message_x, message_y))
            screen.blit(text_surface, text_rect)

    def _draw_minimap(self, screen, player, enemies):
        """
        繪製小地圖（右下角）\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        player: 玩家物件\n
        enemies: 敵人列表\n
        """
        # 小地圖設定
        minimap_size = 100
        minimap_x = self.screen_width - minimap_size - 20
        minimap_y = self.screen_height - minimap_size - 20

        # 小地圖背景
        pygame.draw.rect(
            screen,
            COLORS["dark_gray"],
            (minimap_x, minimap_y, minimap_size, minimap_size),
        )
        pygame.draw.rect(
            screen,
            COLORS["white"],
            (minimap_x, minimap_y, minimap_size, minimap_size),
            2,
        )

        # 縮放比例
        scale_x = minimap_size / self.screen_width
        scale_y = minimap_size / self.screen_height

        # 繪製玩家位置（藍點）
        player_map_x = minimap_x + int(player.x * scale_x)
        player_map_y = minimap_y + int(player.y * scale_y)
        pygame.draw.circle(screen, COLORS["blue"], (player_map_x, player_map_y), 3)

        # 繪製敵人位置（紅點）
        for enemy in enemies:
            if enemy.is_alive:
                enemy_map_x = minimap_x + int(enemy.x * scale_x)
                enemy_map_y = minimap_y + int(enemy.y * scale_y)
                pygame.draw.circle(screen, COLORS["red"], (enemy_map_x, enemy_map_y), 2)

    def add_message(self, text, message_type="info", color=None):
        """
        添加訊息提示\n
        \n
        參數:\n
        text (str): 訊息內容\n
        message_type (str): 訊息類型（'info', 'powerup', 'damage', 'achievement'）\n
        color (tuple): 自訂顏色（可選）\n
        """
        message = {
            "text": text,
            "type": message_type,
            "time": pygame.time.get_ticks(),
            "color": color,
        }
        self.messages.append(message)

        # 限制訊息數量
        if len(self.messages) > 5:
            self.messages.pop(0)

    def set_health_display_mode(self, mode):
        """
        設定血量顯示模式\n
        \n
        參數:\n
        mode (str): 顯示模式（'bar' 或 'number'）\n
        """
        if mode in ["bar", "number"]:
            self.health_display_mode = mode

    def draw_game_over_screen(self, screen, score, stats):
        """
        繪製遊戲結束畫面\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        score (int): 最終分數\n
        stats (dict): 遊戲統計資料\n
        """
        # 半透明背景
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill(COLORS["black"])
        screen.blit(overlay, (0, 0))

        # 遊戲結束標題
        title_text = "遊戲結束"
        title_surface = self.font_large.render(title_text, True, COLORS["red"])
        title_rect = title_surface.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 - 100)
        )
        screen.blit(title_surface, title_rect)

        # 最終分數
        score_text = f"最終分數: {score}"
        score_surface = self.font_medium.render(score_text, True, COLORS["white"])
        score_rect = score_surface.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 - 50)
        )
        screen.blit(score_surface, score_rect)

        # 統計資料
        if "enemies_killed" in stats:
            kills_text = f"擊殺敵人: {stats['enemies_killed']}"
            kills_surface = self.font_small.render(kills_text, True, COLORS["white"])
            kills_rect = kills_surface.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2 - 20)
            )
            screen.blit(kills_surface, kills_rect)

        # 重新開始提示
        restart_text = "按 R 重新開始，按 ESC 返回主選單"
        restart_surface = self.font_small.render(restart_text, True, COLORS["yellow"])
        restart_rect = restart_surface.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 + 50)
        )
        screen.blit(restart_surface, restart_rect)

    ######################角色與場景選擇界面######################

    def draw_character_select(self, screen, selected_character="cat"):
        """
        繪製角色選擇界面\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        selected_character (str): 當前選中的角色\n
        """
        # 清除背景
        screen.fill(COLORS["black"])
        
        # 標題
        title_text = "選擇你的角色"
        title_surface = font_manager.render_text(title_text, "large", COLORS["white"])
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 80))
        screen.blit(title_surface, title_rect)
        
        # 角色選項的基本設定
        characters = ["cat", "dog", "wolf"]
        character_names = {"cat": "🐱 敏捷貓", "dog": "🐶 勇敢狗", "wolf": "🐺 狂野狼"}
        character_skills = {
            "cat": "雷射光束 - 穿透攻擊",
            "dog": "火焰彈 - 爆炸傷害", 
            "wolf": "冰錐 - 減速效果"
        }
        
        # 計算角色卡片位置
        card_width = 200
        card_height = 280
        total_width = len(characters) * card_width + (len(characters) - 1) * 40
        start_x = (self.screen_width - total_width) // 2
        card_y = self.screen_height // 2 - card_height // 2
        
        for i, char_type in enumerate(characters):
            # 計算卡片位置
            card_x = start_x + i * (card_width + 40)
            
            # 判斷是否為選中角色
            is_selected = (char_type == selected_character)
            
            # 繪製角色卡片背景
            card_color = COLORS["yellow"] if is_selected else COLORS["gray"]
            card_border = COLORS["white"] if is_selected else COLORS["dark_gray"]
            
            # 外框
            pygame.draw.rect(screen, card_border, 
                           (card_x - 2, card_y - 2, card_width + 4, card_height + 4))
            # 內部背景
            pygame.draw.rect(screen, card_color, 
                           (card_x, card_y, card_width, card_height))
            
            # 角色頭像區域（用角色顏色填充的圓形）
            avatar_center = (card_x + card_width // 2, card_y + 60)
            avatar_radius = 35
            char_color = PLAYER_CHARACTERS[char_type]["color"]
            pygame.draw.circle(screen, char_color, avatar_center, avatar_radius)
            pygame.draw.circle(screen, COLORS["white"], avatar_center, avatar_radius, 3)
            
            # 角色名稱
            name_text = character_names[char_type]
            name_surface = font_manager.render_text(name_text, "medium", COLORS["black"])
            name_rect = name_surface.get_rect(center=(card_x + card_width // 2, card_y + 130))
            screen.blit(name_surface, name_rect)
            
            # 技能描述
            skill_text = character_skills[char_type]
            # 分行顯示技能描述
            skill_lines = skill_text.split(" - ")
            for j, line in enumerate(skill_lines):
                skill_surface = font_manager.render_text(line, "small", COLORS["dark_gray"])
                skill_rect = skill_surface.get_rect(center=(card_x + card_width // 2, card_y + 160 + j * 25))
                screen.blit(skill_surface, skill_rect)
            
            # 角色數據
            char_data = PLAYER_CHARACTERS[char_type]
            damage_text = f"傷害: {char_data['skill_damage']}"
            damage_surface = font_manager.render_text(damage_text, "small", COLORS["black"])
            damage_rect = damage_surface.get_rect(center=(card_x + card_width // 2, card_y + 220))
            screen.blit(damage_surface, damage_rect)
            
            # 選中提示
            if is_selected:
                select_text = "按 ENTER 確認"
                select_surface = font_manager.render_text(select_text, "small", COLORS["red"])
                select_rect = select_surface.get_rect(center=(card_x + card_width // 2, card_y + 250))
                screen.blit(select_surface, select_rect)
        
        # 操作提示
        control_text = "← → 方向鍵選擇角色，ENTER 確認，ESC 返回主選單"
        control_surface = font_manager.render_text(control_text, "small", COLORS["white"])
        control_rect = control_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
        screen.blit(control_surface, control_rect)

    def draw_scene_select(self, screen, selected_scene="lava"):
        """
        繪製場景選擇界面\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        selected_scene (str): 當前選中的場景\n
        """
        # 清除背景
        screen.fill(COLORS["black"])
        
        # 標題
        title_text = "選擇戰鬥場景"
        title_surface = font_manager.render_text(title_text, "large", COLORS["white"])
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 80))
        screen.blit(title_surface, title_rect)
        
        # 場景選項的基本設定
        scenes = ["lava", "mountain", "ice"]
        scene_names = {"lava": "🌋 熔岩地獄", "mountain": "⛰️ 高山戰場", "ice": "🧊 冰霜極地"}
        scene_effects = {
            "lava": "移動速度 +20%",
            "mountain": "技能冷卻 -25%", 
            "ice": "移動速度 -10%，技能冷卻 -15%"
        }
        
        # 計算場景卡片位置
        card_width = 220
        card_height = 300
        total_width = len(scenes) * card_width + (len(scenes) - 1) * 40
        start_x = (self.screen_width - total_width) // 2
        card_y = self.screen_height // 2 - card_height // 2
        
        for i, scene_type in enumerate(scenes):
            # 計算卡片位置
            card_x = start_x + i * (card_width + 40)
            
            # 判斷是否為選中場景
            is_selected = (scene_type == selected_scene)
            
            # 繪製場景卡片背景
            card_color = COLORS["cyan"] if is_selected else COLORS["gray"]
            card_border = COLORS["white"] if is_selected else COLORS["dark_gray"]
            
            # 外框
            pygame.draw.rect(screen, card_border, 
                           (card_x - 2, card_y - 2, card_width + 4, card_height + 4))
            # 內部背景
            pygame.draw.rect(screen, card_color, 
                           (card_x, card_y, card_width, card_height))
            
            # 場景圖示區域（用場景主題色填充的矩形）
            icon_rect = pygame.Rect(card_x + 40, card_y + 30, card_width - 80, 80)
            scene_data = BATTLE_SCENES[scene_type]
            theme_color = scene_data.get("theme_color", COLORS["white"])
            pygame.draw.rect(screen, theme_color, icon_rect)
            pygame.draw.rect(screen, COLORS["white"], icon_rect, 3)
            
            # 場景名稱
            name_text = scene_names[scene_type]
            name_surface = font_manager.render_text(name_text, "medium", COLORS["black"])
            name_rect = name_surface.get_rect(center=(card_x + card_width // 2, card_y + 140))
            screen.blit(name_surface, name_rect)
            
            # 場景效果描述
            effect_text = scene_effects[scene_type]
            effect_surface = font_manager.render_text(effect_text, "small", COLORS["dark_gray"])
            effect_rect = effect_surface.get_rect(center=(card_x + card_width // 2, card_y + 170))
            screen.blit(effect_surface, effect_rect)
            
            # 詳細效果數據
            speed_mult = scene_data.get("speed_multiplier", 1.0)
            cooldown_mult = scene_data.get("skill_cooldown_multiplier", 1.0)
            
            detail_y = card_y + 200
            if speed_mult != 1.0:
                speed_change = int((speed_mult - 1.0) * 100)
                speed_text = f"速度: {speed_change:+d}%"
                speed_surface = font_manager.render_text(speed_text, "small", COLORS["black"])
                speed_rect = speed_surface.get_rect(center=(card_x + card_width // 2, detail_y))
                screen.blit(speed_surface, speed_rect)
                detail_y += 25
                
            if cooldown_mult != 1.0:
                cooldown_change = int((1.0 - cooldown_mult) * 100)
                cooldown_text = f"技能冷卻: {cooldown_change:+d}%"
                cooldown_surface = font_manager.render_text(cooldown_text, "small", COLORS["black"])
                cooldown_rect = cooldown_surface.get_rect(center=(card_x + card_width // 2, detail_y))
                screen.blit(cooldown_surface, cooldown_rect)
            
            # 選中提示
            if is_selected:
                select_text = "按 ENTER 確認"
                select_surface = font_manager.render_text(select_text, "small", COLORS["red"])
                select_rect = select_surface.get_rect(center=(card_x + card_width // 2, card_y + 270))
                screen.blit(select_surface, select_rect)
        
        # 操作提示
        control_text = "← → 方向鍵選擇場景，ENTER 確認，ESC 返回角色選擇"
        control_surface = font_manager.render_text(control_text, "small", COLORS["white"])
        control_rect = control_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
        screen.blit(control_surface, control_rect)
