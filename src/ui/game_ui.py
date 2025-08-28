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
        self.health_bar_pos = (20, 120)  # 調整位置避免與關卡資訊重疊
        self.health_bar_size = (200, 20)
        self.weapon_info_pos = (20, 150)  # 相應調整武器資訊位置
        self.powerup_list_pos = (20, 200)  # 相應調整強化效果位置
        self.score_pos = (screen_width - 220, 20)
        self.skill_cooldown_pos = (screen_width - 220, 90)  # 調整位置避免與命中率重疊

        # 訊息系統
        self.messages = []
        self.message_duration = 3000  # 3秒

        # 血量顯示模式（血條或數字）
        self.health_display_mode = "bar"  # 'bar' 或 'number'

        # 準心系統設定
        self.crosshair_enabled = True
        self.crosshair_size = 45  # 放大3倍：15 * 3 = 45
        self.crosshair_thickness = 2
        self.crosshair_gap = 5
        # 準心顏色配置 - 根據不同狀態變色
        self.crosshair_colors = {
            "normal": COLORS["white"],  # 正常狀態 - 白色
            "reloading": COLORS["yellow"],  # 重裝彈時 - 黃色
            "low_ammo": COLORS["orange"],  # 子彈不足 - 橘色
            "no_ammo": COLORS["red"],  # 沒有子彈 - 紅色
        }

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

    def draw(
        self,
        screen,
        player,
        enemies,
        score,
        game_stats,
        current_level=1,
        level_enemies_killed=0,
        powerup_manager=None,
    ):
        """
        繪製所有UI元素\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        player: 玩家物件\n
        enemies: 敵人列表\n
        score (int): 當前分數\n
        game_stats (dict): 遊戲統計資料\n
        current_level (int): 當前關卡數\n
        level_enemies_killed (int): 當前關卡已擊殺敵人數\n
        powerup_manager: 道具管理器（可選）\n
        """
        # 繪製關卡資訊（左上角）
        self._draw_level_info(screen, current_level, level_enemies_killed)

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

        # 繪製滑鼠準心
        self._draw_crosshair(screen, player)

        # 繪製小地圖（可選）
        self._draw_minimap(screen, player, enemies, powerup_manager)

    def _draw_level_info(self, screen, current_level, level_enemies_killed):
        """
        繪製關卡資訊顯示（左上角）\n
        \n
        根據 target.prompt.md 規格：在視窗左上角顯示關卡資訊\n
        使用支援繁體中文的字體進行顯示\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        current_level (int): 當前關卡數\n
        level_enemies_killed (int): 當前關卡已擊殺敵人數\n
        """
        # 關卡顯示位置設定（左上角，留出一些邊距）
        level_info_x = 20
        level_info_y = 20

        # 獲取當前關卡配置
        level_config = LEVEL_CONFIGS.get(current_level)
        if not level_config:
            return

        # 關卡標題顯示
        level_title = f"關卡 {current_level}"
        title_surface = font_manager.render_text(level_title, "medium", COLORS["white"])
        screen.blit(title_surface, (level_info_x, level_info_y))

        # 關卡名稱顯示（去掉前面的"第X關 - "部分）
        level_name = (
            level_config["name"].split(" - ")[-1]
            if " - " in level_config["name"]
            else level_config["name"]
        )
        name_y = level_info_y + 25
        name_surface = font_manager.render_text(level_name, "small", COLORS["yellow"])
        screen.blit(name_surface, (level_info_x, name_y))

        # 進度顯示
        progress_y = name_y + 20
        progress_text = f"進度: {level_enemies_killed}/{level_config['enemy_count']}"

        # 根據進度選擇顏色
        if level_enemies_killed >= level_config["enemy_count"]:
            progress_color = COLORS["green"]  # 完成時顯示綠色
        elif level_enemies_killed >= level_config["enemy_count"] * 0.7:
            progress_color = COLORS["yellow"]  # 接近完成時顯示黃色
        else:
            progress_color = COLORS["white"]  # 一般狀態顯示白色

        progress_surface = font_manager.render_text(
            progress_text, "small", progress_color
        )
        screen.blit(progress_surface, (level_info_x, progress_y))

        # 敵人類型顯示（支援單一類型或混合 enemy_counts）
        enemy_type_y = progress_y + 20
        # 若有單一 enemy_type 欄位，優先顯示
        if "enemy_type" in level_config:
            enemy_type_config = AI_ENEMY_TYPES.get(level_config["enemy_type"])
            if enemy_type_config:
                enemy_info = (
                    f"敵人: {enemy_type_config['emoji']} {enemy_type_config['name']}"
                )
                enemy_surface = font_manager.render_text(
                    enemy_info, "small", COLORS["white"]
                )
                screen.blit(enemy_surface, (level_info_x, enemy_type_y))
        elif "enemy_counts" in level_config:
            # 混合顯示各種敵人與數量
            counts = level_config.get("enemy_counts", {})
            parts = []
            for t, cnt in counts.items():
                cfg = AI_ENEMY_TYPES.get(t, {})
                emoji = cfg.get("emoji", "?")
                name = cfg.get("name", t)
                parts.append(f"{emoji}{name}x{cnt}")

            if parts:
                enemy_info = "敵人: " + ", ".join(parts)
                enemy_surface = font_manager.render_text(
                    enemy_info, "small", COLORS["white"]
                )
                screen.blit(enemy_surface, (level_info_x, enemy_type_y))

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
        text_surface = self.font_small.render(total_text, True, COLORS["white"])
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
        繪製技能冷卻時間和技能啟用狀態\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        player: 玩家物件\n
        """
        x, y = self.skill_cooldown_pos

        # 檢查技能是否正在啟用中
        if player.is_skill_active():
            active_skill_info = player.get_active_skill_info()
            if active_skill_info:
                # 技能啟用時顯示剩餘時間倒數
                remaining_time = active_skill_info["remaining_time"]
                skill_text = f"技能啟用中: {remaining_time:.1f}s"
                color = active_skill_info["effect_color"]

                # 添加閃爍效果
                current_time = pygame.time.get_ticks()
                if (current_time // 200) % 2 == 0:  # 每200ms閃爍
                    color = COLORS["white"]

                text_surface = font_manager.render_text(skill_text, "small", color)
                screen.blit(text_surface, (x, y))

                # 顯示技能名稱
                skill_name_y = y + 20
                skill_name = f"🔥 {active_skill_info.get('type', '技能').upper()}"
                name_surface = font_manager.render_text(
                    skill_name, "small", COLORS["yellow"]
                )
                screen.blit(name_surface, (x, skill_name_y))

                # 顯示技能進度條
                progress_y = y + 40
                self._draw_skill_progress_bar(
                    screen, x, progress_y, remaining_time, 3.0, color
                )

                return  # 技能啟用時不顯示冷卻資訊

        # 技能未啟用時顯示冷卻狀態
        skill_info = player.get_skill_cooldown_info()

        if skill_info["ready"]:
            skill_text = "技能: 就緒 (Q)"
            color = COLORS["green"]

            # 就緒時添加輕微閃爍
            current_time = pygame.time.get_ticks()
            if (current_time // 500) % 2 == 0:  # 每500ms閃爍
                color = COLORS["white"]
        else:
            cooldown_remaining = skill_info["cooldown_remaining"]
            skill_text = f"技能冷卻: {cooldown_remaining:.1f}s"
            color = COLORS["red"]

        text_surface = font_manager.render_text(skill_text, "small", color)
        screen.blit(text_surface, (x, y))

        # 添加技能說明
        skill_desc_y = y + 20
        skill_desc = "Q: 全螢幕攻擊(-10%血量)"
        desc_surface = font_manager.render_text(skill_desc, "small", COLORS["white"])
        screen.blit(desc_surface, (x, skill_desc_y))

        # 如果技能在冷卻中，顯示冷卻進度條
        if not skill_info["ready"]:
            progress_y = y + 40
            total_cooldown = skill_info["total_cooldown"]
            elapsed_time = total_cooldown - skill_info["cooldown_remaining"]
            progress = elapsed_time / total_cooldown
            self._draw_cooldown_progress_bar(screen, x, progress_y, progress)

    def _draw_skill_progress_bar(
        self, screen, x, y, remaining_time, total_time, skill_color
    ):
        """
        繪製技能剩餘時間進度條

        參數:
        screen (pygame.Surface): 遊戲畫面物件
        x, y (int): 進度條位置
        remaining_time (float): 剩餘時間（秒）
        total_time (float): 總持續時間（秒）
        skill_color (tuple): 技能顏色
        """
        bar_width = 120
        bar_height = 8

        # 計算進度（剩餘時間的比例）
        progress = remaining_time / total_time

        # 背景條
        pygame.draw.rect(screen, COLORS["dark_gray"], (x, y, bar_width, bar_height))

        # 進度條（從右往左消失）
        if progress > 0:
            progress_width = int(bar_width * progress)
            pygame.draw.rect(screen, skill_color, (x, y, progress_width, bar_height))

        # 邊框
        pygame.draw.rect(screen, COLORS["white"], (x, y, bar_width, bar_height), 1)

        # 時間文字
        time_text = f"{remaining_time:.1f}s"
        time_surface = font_manager.render_text(time_text, "small", COLORS["white"])
        text_x = x + bar_width + 5
        screen.blit(time_surface, (text_x, y - 2))

    def _draw_cooldown_progress_bar(self, screen, x, y, progress):
        """
        繪製技能冷卻進度條

        參數:
        screen (pygame.Surface): 遊戲畫面物件
        x, y (int): 進度條位置
        progress (float): 冷卻進度 (0.0 到 1.0)
        """
        bar_width = 120
        bar_height = 6

        # 背景條
        pygame.draw.rect(screen, COLORS["dark_gray"], (x, y, bar_width, bar_height))

        # 進度條（從左往右填滿）
        if progress > 0:
            progress_width = int(bar_width * progress)
            # 顏色隨進度變化：紅色 → 黃色 → 綠色
            if progress < 0.5:
                # 前半段：紅色到黃色
                red_component = 255
                green_component = int(255 * (progress * 2))
                color = (red_component, green_component, 0)
            else:
                # 後半段：黃色到綠色
                red_component = int(255 * (2 - progress * 2))
                green_component = 255
                color = (red_component, green_component, 0)

            pygame.draw.rect(screen, color, (x, y, progress_width, bar_height))

        # 邊框
        pygame.draw.rect(screen, COLORS["white"], (x, y, bar_width, bar_height), 1)

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

    def _draw_crosshair(self, screen, player):
        """
        繪製滑鼠準心 - 提供精確瞄準的視覺回饋\n
        \n
        在滑鼠位置繪製十字準心，包含以下特色：\n
        1. 可調整大小和厚度\n
        2. 中央留空隙便於瞄準\n
        3. 支援不同狀態的顏色變化\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        player (Player): 玩家物件，用於判斷準心顏色狀態\n
        """
        if not self.crosshair_enabled:
            return

        # 取得滑鼠位置
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # 根據玩家狀態決定準心顏色
        crosshair_color = self._get_crosshair_color(player)

        # 計算準心的線條位置
        half_size = self.crosshair_size // 2
        gap = self.crosshair_gap
        thickness = self.crosshair_thickness

        # 繪製水平線條（左右兩段）
        # 左邊線條
        pygame.draw.rect(
            screen,
            crosshair_color,
            (mouse_x - half_size, mouse_y - thickness // 2, half_size - gap, thickness),
        )
        # 右邊線條
        pygame.draw.rect(
            screen,
            crosshair_color,
            (mouse_x + gap, mouse_y - thickness // 2, half_size - gap, thickness),
        )

        # 繪製垂直線條（上下兩段）
        # 上邊線條
        pygame.draw.rect(
            screen,
            crosshair_color,
            (mouse_x - thickness // 2, mouse_y - half_size, thickness, half_size - gap),
        )
        # 下邊線條
        pygame.draw.rect(
            screen,
            crosshair_color,
            (mouse_x - thickness // 2, mouse_y + gap, thickness, half_size - gap),
        )

        # 在準心中央加上一個小點作為精確瞄準點
        pygame.draw.circle(screen, crosshair_color, (mouse_x, mouse_y), 1)  # 小點半徑

    def _get_crosshair_color(self, player):
        """
        根據玩家狀態決定準心顏色\n
        \n
        準心顏色規則：\n
        - 紅色：沒有子彈\n
        - 橘色：子彈不足（剩餘 < 25%）\n
        - 黃色：正在重裝彈\n
        - 白色：正常狀態\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        tuple: RGB顏色值\n
        """
        # 取得目前武器配置和子彈狀態
        weapon_config = WEAPON_CONFIGS.get(player.current_weapon, {})
        max_ammo = weapon_config.get("max_ammo", 30)

        # 取得當前武器的子彈數量
        current_ammo = 0
        if player.current_weapon in player.weapons:
            current_ammo = player.weapons[player.current_weapon].get("current_ammo", 0)

        # 檢查重裝彈狀態
        if hasattr(player, "is_reloading") and player.is_reloading:
            return self.crosshair_colors["reloading"]

        # 檢查子彈狀態
        if current_ammo <= 0:
            return self.crosshair_colors["no_ammo"]
        elif current_ammo < max_ammo * 0.25:  # 子彈少於25%
            return self.crosshair_colors["low_ammo"]
        else:
            return self.crosshair_colors["normal"]

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

            # 驗證顏色格式
            if not isinstance(color, (tuple, list)) or len(color) != 3:
                color = COLORS["white"]

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

    def _draw_minimap(self, screen, player, enemies, powerup_manager=None):
        """
        繪製小地圖（右下角）\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        player: 玩家物件\n
        enemies: 敵人列表\n
        powerup_manager: 道具管理器（可選）\n
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

        # 繪製道具位置
        if powerup_manager:
            for powerup in powerup_manager.powerups:
                if powerup.is_active:
                    powerup_map_x = minimap_x + int(powerup.x * scale_x)
                    powerup_map_y = minimap_y + int(powerup.y * scale_y)

                    # 根據道具類型選擇顏色和樣式（與主遊戲保持一致）
                    if powerup.powerup_type == "fire_boost":
                        # 火力增強：紅色主體 + 橘色光環
                        main_color = COLORS["red"]
                        effect_color = COLORS["orange"]
                        # 繪製光環效果
                        pygame.draw.circle(
                            screen, effect_color, (powerup_map_x, powerup_map_y), 4, 1
                        )
                        pygame.draw.circle(
                            screen, main_color, (powerup_map_x, powerup_map_y), 2
                        )

                    elif powerup.powerup_type == "ammo_refill":
                        # 彈藥補給：藍色主體 + 白色光環
                        main_color = COLORS["blue"]
                        effect_color = COLORS["white"]
                        # 繪製光環效果
                        pygame.draw.circle(
                            screen, effect_color, (powerup_map_x, powerup_map_y), 4, 1
                        )
                        pygame.draw.circle(
                            screen, main_color, (powerup_map_x, powerup_map_y), 2
                        )

                    elif powerup.powerup_type == "scatter_shot":
                        # 散彈模式：紫色主體 + 黃色光環
                        main_color = COLORS["purple"]
                        effect_color = COLORS["yellow"]
                        # 繪製光環效果
                        pygame.draw.circle(
                            screen, effect_color, (powerup_map_x, powerup_map_y), 4, 1
                        )
                        pygame.draw.circle(
                            screen, main_color, (powerup_map_x, powerup_map_y), 2
                        )

                    elif powerup.powerup_type == "machinegun_powerup":
                        # 機關槍：深紅色主體 + 紅色光環
                        main_color = (150, 0, 0)  # 深紅色
                        effect_color = COLORS["red"]
                        # 繪製光環效果
                        pygame.draw.circle(
                            screen, effect_color, (powerup_map_x, powerup_map_y), 4, 1
                        )
                        pygame.draw.rect(
                            screen,
                            main_color,
                            (powerup_map_x - 1, powerup_map_y - 1, 3, 3),
                        )

                    elif powerup.powerup_type == "submachinegun_powerup":
                        # 衝鋒槍：深藍色主體 + 藍色光環
                        main_color = (0, 0, 150)  # 深藍色
                        effect_color = COLORS["blue"]
                        # 繪製光環效果
                        pygame.draw.circle(
                            screen, effect_color, (powerup_map_x, powerup_map_y), 4, 1
                        )
                        pygame.draw.rect(
                            screen,
                            main_color,
                            (powerup_map_x - 1, powerup_map_y - 1, 3, 3),
                        )

                    elif powerup.powerup_type == "health_pack":
                        # 補血包：紅色主體 + 白色光環 + 十字標記
                        main_color = COLORS["red"]
                        effect_color = COLORS["white"]
                        # 繪製光環效果
                        pygame.draw.circle(
                            screen, effect_color, (powerup_map_x, powerup_map_y), 4, 1
                        )
                        pygame.draw.circle(
                            screen, main_color, (powerup_map_x, powerup_map_y), 2
                        )
                        # 繪製十字標記
                        pygame.draw.line(
                            screen,
                            effect_color,
                            (powerup_map_x - 1, powerup_map_y),
                            (powerup_map_x + 1, powerup_map_y),
                            1,
                        )
                        pygame.draw.line(
                            screen,
                            effect_color,
                            (powerup_map_x, powerup_map_y - 1),
                            (powerup_map_x, powerup_map_y + 1),
                            1,
                        )
                    else:
                        # 其他道具：綠色圓點（保持原有樣式）
                        pygame.draw.circle(
                            screen, COLORS["green"], (powerup_map_x, powerup_map_y), 2
                        )

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

    def draw_game_over_screen(self, screen, score, stats, game_completed=False):
        """
        繪製遊戲結束畫面\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        score (int): 最終分數\n
        stats (dict): 遊戲統計資料\n
        game_completed (bool): 是否完成所有關卡（勝利）\n
        """
        # 半透明背景
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill(COLORS["black"])
        screen.blit(overlay, (0, 0))

        # 根據遊戲狀態顯示不同標題
        if game_completed:
            title_text = "你贏了！"
            title_color = COLORS["green"]
        else:
            title_text = "遊戲結束"
            title_color = COLORS["red"]

        title_surface = self.font_large.render(title_text, True, title_color)
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

        # 顯示關卡完成狀態
        if game_completed:
            completion_text = "恭喜完成所有關卡！"
            completion_surface = self.font_small.render(
                completion_text, True, COLORS["yellow"]
            )
            completion_rect = completion_surface.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2 + 10)
            )
            screen.blit(completion_surface, completion_rect)

        # 重新開始提示
        restart_text = "按 R 重新開始，按 ESC 返回主選單"
        restart_surface = self.font_small.render(restart_text, True, COLORS["yellow"])
        restart_rect = restart_surface.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 + 50)
        )
        screen.blit(restart_surface, restart_rect)
