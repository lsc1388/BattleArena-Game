######################載入套件######################
import pygame
import math
from src.config import *
from src.utils.font_manager import font_manager

######################選擇介面類別######################


class SelectionUI:
    """
    角色和場景選擇界面類別

    此類別負責：
    1. 角色選擇界面的繪製和交互
    2. 場景選擇界面的繪製和交互
    3. 選擇狀態的管理
    4. 選擇確認和返回功能
    """

    def __init__(self, screen_width, screen_height):
        """
        初始化選擇界面

        參數:
        screen_width (int): 螢幕寬度
        screen_height (int): 螢幕高度
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        # 選擇狀態
        self.selected_character = None
        self.selected_scene = None
        self.current_selection_type = "character"  # "character" 或 "scene"

        # 選項配置
        self.character_options = list(CHARACTER_CONFIGS.keys())
        self.scene_options = list(SCENE_CONFIGS.keys())

        # 當前選中的索引
        self.character_index = 0
        self.scene_index = 0

        # 動畫效果
        self.animation_time = 0
        self.hover_effect = 0

    def handle_input(self, event):
        """
        處理選擇界面的輸入事件

        參數:
        event: pygame事件對象

        回傳:
        dict: 處理結果，包含動作類型和相關資料
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # 返回主選單
                return {"action": "back_to_menu"}

            elif event.key == pygame.K_LEFT:
                # 向左選擇
                if self.current_selection_type == "character":
                    self.character_index = (self.character_index - 1) % len(
                        self.character_options
                    )
                else:
                    self.scene_index = (self.scene_index - 1) % len(self.scene_options)
                return {"action": "selection_change"}

            elif event.key == pygame.K_RIGHT:
                # 向右選擇
                if self.current_selection_type == "character":
                    self.character_index = (self.character_index + 1) % len(
                        self.character_options
                    )
                else:
                    self.scene_index = (self.scene_index + 1) % len(self.scene_options)
                return {"action": "selection_change"}

            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # 確認選擇
                if self.current_selection_type == "character":
                    self.selected_character = self.character_options[
                        self.character_index
                    ]
                    self.current_selection_type = "scene"
                    return {
                        "action": "character_selected",
                        "character": self.selected_character,
                    }
                else:
                    self.selected_scene = self.scene_options[self.scene_index]
                    return {
                        "action": "scene_selected",
                        "scene": self.selected_scene,
                        "character": self.selected_character,
                    }

        return {"action": "none"}

    def draw_character_selection(self, screen):
        """
        繪製角色選擇界面

        參數:
        screen: pygame顯示表面
        """
        # 背景
        screen.fill(COLORS["black"])

        # 標題
        title_text = "選擇你的角色"
        title_surface = font_manager.render_text(title_text, "large", COLORS["white"])
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 60))
        screen.blit(title_surface, title_rect)

        # 角色選項
        options_start_x = self.screen_width // 2 - 300
        options_y = 150
        option_width = 200
        option_spacing = 200

        for i, character_key in enumerate(self.character_options):
            character_config = CHARACTER_CONFIGS[character_key]
            x = options_start_x + i * option_spacing

            # 選中效果
            is_selected = i == self.character_index

            # 繪製角色卡片
            self._draw_character_card(
                screen, character_config, x, options_y, is_selected
            )

        # 操作說明
        self._draw_controls_help(screen, "character")

    def draw_scene_selection(self, screen):
        """
        繪製場景選擇界面

        參數:
        screen: pygame顯示表面
        """
        # 背景
        screen.fill(COLORS["black"])

        # 標題
        title_text = "選擇戰鬥場景"
        title_surface = font_manager.render_text(title_text, "large", COLORS["white"])
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 60))
        screen.blit(title_surface, title_rect)

        # 顯示已選擇的角色
        if self.selected_character:
            char_config = CHARACTER_CONFIGS[self.selected_character]
            char_text = f"已選角色: {char_config['emoji']} {char_config['name']}"
            char_surface = font_manager.render_text(
                char_text, "medium", COLORS["yellow"]
            )
            char_rect = char_surface.get_rect(center=(self.screen_width // 2, 90))
            screen.blit(char_surface, char_rect)

        # 場景選項
        options_start_x = self.screen_width // 2 - 300
        options_y = 150
        option_spacing = 200

        for i, scene_key in enumerate(self.scene_options):
            scene_config = SCENE_CONFIGS[scene_key]
            x = options_start_x + i * option_spacing

            # 選中效果
            is_selected = i == self.scene_index

            # 繪製場景卡片
            self._draw_scene_card(screen, scene_config, x, options_y, is_selected)

        # 操作說明
        self._draw_controls_help(screen, "scene")

    def _draw_character_card(self, screen, character_config, x, y, is_selected):
        """
        繪製角色卡片

        參數:
        screen: pygame顯示表面
        character_config (dict): 角色配置
        x, y (int): 卡片位置
        is_selected (bool): 是否被選中
        """
        card_width = 180
        card_height = 200

        # 卡片背景
        card_color = COLORS["white"] if is_selected else COLORS["gray"]
        border_color = character_config["color"] if is_selected else COLORS["dark_gray"]
        border_width = 4 if is_selected else 2

        card_rect = pygame.Rect(x, y, card_width, card_height)
        pygame.draw.rect(screen, card_color, card_rect)
        pygame.draw.rect(screen, border_color, card_rect, border_width)

        # 角色emoji/圖示 (使用幾何形狀代替)
        icon_size = 60
        icon_x = x + card_width // 2 - icon_size // 2
        icon_y = y + 20
        pygame.draw.circle(
            screen,
            character_config["color"],
            (icon_x + icon_size // 2, icon_y + icon_size // 2),
            icon_size // 2,
        )

        # 角色名稱
        name_surface = font_manager.render_text(
            character_config["name"], "medium", COLORS["black"]
        )
        name_rect = name_surface.get_rect(center=(x + card_width // 2, y + 110))
        screen.blit(name_surface, name_rect)

        # 技能資訊
        skill_name = character_config["skill"]["name"]
        skill_surface = font_manager.render_text(
            skill_name, "small", COLORS["dark_gray"]
        )
        skill_rect = skill_surface.get_rect(center=(x + card_width // 2, y + 140))
        screen.blit(skill_surface, skill_rect)

        # 技能描述
        skill_desc = character_config["skill"]["description"]
        desc_surface = font_manager.render_text(skill_desc, "tiny", COLORS["dark_gray"])
        desc_rect = desc_surface.get_rect(center=(x + card_width // 2, y + 165))
        screen.blit(desc_surface, desc_rect)

        # 技能傷害資訊
        damage_text = f"傷害: {character_config['skill']['damage']}"
        damage_surface = font_manager.render_text(damage_text, "tiny", COLORS["red"])
        damage_rect = damage_surface.get_rect(center=(x + card_width // 2, y + 160))
        screen.blit(damage_surface, damage_rect)

        # 角色特性資訊
        attributes = character_config["attributes"]
        if character_config["name"] == "貓":
            trait_text = "高攻擊 / 低射速"
        elif character_config["name"] == "狗":
            trait_text = "平衡型角色"
        elif character_config["name"] == "狼":
            trait_text = "高射速 / 低攻擊"
        else:
            trait_text = "均衡型"

        trait_surface = font_manager.render_text(trait_text, "tiny", COLORS["blue"])
        trait_rect = trait_surface.get_rect(center=(x + card_width // 2, y + 175))
        screen.blit(trait_surface, trait_rect)

        # 選中提示
        if is_selected:
            select_text = "按 ENTER 選擇"
            select_surface = font_manager.render_text(
                select_text, "tiny", COLORS["green"]
            )
            select_rect = select_surface.get_rect(center=(x + card_width // 2, y + 190))
            screen.blit(select_surface, select_rect)

    def _draw_scene_card(self, screen, scene_config, x, y, is_selected):
        """
        繪製場景卡片

        參數:
        screen: pygame顯示表面
        scene_config (dict): 場景配置
        x, y (int): 卡片位置
        is_selected (bool): 是否被選中
        """
        card_width = 180
        card_height = 200

        # 卡片背景
        card_color = scene_config["background_color"] if is_selected else COLORS["gray"]
        border_color = (
            scene_config["accent_color"] if is_selected else COLORS["dark_gray"]
        )
        border_width = 4 if is_selected else 2

        card_rect = pygame.Rect(x, y, card_width, card_height)
        pygame.draw.rect(screen, card_color, card_rect)
        pygame.draw.rect(screen, border_color, card_rect, border_width)

        # 場景預覽 (使用幾何形狀代替圖片)
        preview_rect = pygame.Rect(x + 20, y + 20, card_width - 40, 100)
        pygame.draw.rect(screen, scene_config["background_color"], preview_rect)
        pygame.draw.rect(screen, scene_config["accent_color"], preview_rect, 3)

        # 添加場景特色元素
        if "lava" in scene_config.get("effect", ""):
            # 岩漿效果 - 紅色圓點
            for i in range(5):
                circle_x = x + 30 + i * 25
                circle_y = y + 50 + (i % 2) * 20
                pygame.draw.circle(screen, (255, 69, 0), (circle_x, circle_y), 8)
        elif "ice" in scene_config.get("effect", ""):
            # 冰原效果 - 藍色三角形
            for i in range(3):
                triangle_x = x + 40 + i * 35
                triangle_y = y + 70
                points = [
                    (triangle_x, triangle_y),
                    (triangle_x + 15, triangle_y - 20),
                    (triangle_x + 30, triangle_y),
                ]
                pygame.draw.polygon(screen, (173, 216, 230), points)
        elif "mountain" in scene_config.get("effect", ""):
            # 高山效果 - 灰色三角形
            for i in range(3):
                mountain_x = x + 35 + i * 30
                mountain_y = y + 80
                points = [
                    (mountain_x, mountain_y),
                    (mountain_x + 15, mountain_y - 30),
                    (mountain_x + 30, mountain_y),
                ]
                pygame.draw.polygon(screen, (169, 169, 169), points)

        # 場景名稱
        name_surface = font_manager.render_text(
            scene_config["name"], "medium", COLORS["white"]
        )
        name_rect = name_surface.get_rect(center=(x + card_width // 2, y + 130))
        screen.blit(name_surface, name_rect)

        # 場景描述
        desc_surface = font_manager.render_text(
            scene_config["description"], "small", COLORS["white"]
        )
        desc_rect = desc_surface.get_rect(center=(x + card_width // 2, y + 155))
        screen.blit(desc_surface, desc_rect)

        # 選中提示
        if is_selected:
            select_text = "按 ENTER 開始遊戲"
            select_surface = font_manager.render_text(
                select_text, "tiny", COLORS["yellow"]
            )
            select_rect = select_surface.get_rect(center=(x + card_width // 2, y + 180))
            screen.blit(select_surface, select_rect)

    def _draw_controls_help(self, screen, selection_type):
        """
        繪製操作說明

        參數:
        screen: pygame顯示表面
        selection_type (str): 選擇類型 ("character" 或 "scene")
        """
        help_y = self.screen_height - 100

        controls = ["← → 選擇", "ENTER 確認", "ESC 返回主選單"]

        if selection_type == "scene":
            controls.insert(0, "已選擇角色，現在選擇場景")

        for i, control_text in enumerate(controls):
            color = (
                COLORS["yellow"]
                if i == 0 and selection_type == "scene"
                else COLORS["white"]
            )
            control_surface = font_manager.render_text(control_text, "small", color)
            control_rect = control_surface.get_rect(
                center=(self.screen_width // 2, help_y + i * 20)
            )
            screen.blit(control_surface, control_rect)

    def reset_selection(self):
        """
        重置選擇狀態，返回角色選擇
        """
        self.selected_character = None
        self.selected_scene = None
        self.current_selection_type = "character"
        self.character_index = 0
        self.scene_index = 0

    def get_selection_info(self):
        """
        獲取當前選擇資訊

        回傳:
        dict: 包含角色和場景選擇的資訊
        """
        return {
            "character": self.selected_character,
            "scene": self.selected_scene,
            "character_config": (
                CHARACTER_CONFIGS.get(self.selected_character)
                if self.selected_character
                else None
            ),
            "scene_config": (
                SCENE_CONFIGS.get(self.selected_scene) if self.selected_scene else None
            ),
        }

    def draw(self, screen):
        """
        根據當前選擇類型繪製對應界面

        參數:
        screen: pygame顯示表面
        """
        if self.current_selection_type == "character":
            self.draw_character_selection(screen)
        else:
            self.draw_scene_selection(screen)
