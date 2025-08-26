######################載入套件######################
import pygame
import os
from src.config import FONT_CONFIGS

######################字體管理系統######################


class FontManager:
    """
    字體管理系統 - 處理繁體中文字體的載入和管理\n
    \n
    此系統負責：\n
    1. 自動偵測系統中可用的中文字體\n
    2. 提供統一的字體獲取介面\n
    3. 處理字體載入失敗的降級方案\n
    4. 快取字體物件以提升效能\n
    """

    def __init__(self):
        """
        初始化字體管理系統\n
        """
        pygame.font.init()

        # 字體快取
        self._font_cache = {}

        # 尋找可用的中文字體
        self.chinese_font_name = self._find_chinese_font()

        # 載入所有常用字體大小
        self._preload_fonts()

    def _find_chinese_font(self):
        """
        尋找系統中可用的中文字體\n
        \n
        回傳:\n
        str: 可用的中文字體名稱，如果都找不到則回傳None\n
        """
        # 獲取系統字體列表
        system_fonts = pygame.font.get_fonts()

        # 嘗試尋找指定的中文字體
        for font_name in FONT_CONFIGS["chinese_fonts"]:
            # 將字體名稱轉換為pygame格式（小寫，空格替換為底線）
            pygame_font_name = font_name.lower().replace(" ", "")

            # 檢查是否在系統字體列表中
            if pygame_font_name in system_fonts:
                print(f"✅ 找到中文字體: {font_name}")
                return font_name

            # 嘗試直接載入字體（Windows系統）
            try:
                test_font = pygame.font.SysFont(font_name, 24)
                if test_font:
                    print(f"✅ 成功載入中文字體: {font_name}")
                    return font_name
            except:
                continue

        print("⚠️ 未找到指定的中文字體，使用系統預設字體")
        return None

    def _preload_fonts(self):
        """
        預載入常用字體大小到快取中\n
        """
        for size_name, size_value in FONT_CONFIGS["sizes"].items():
            font_key = f"{size_name}_{size_value}"
            self._font_cache[font_key] = self._create_font(size_value)

    def _create_font(self, size):
        """
        創建指定大小的字體物件\n
        \n
        參數:\n
        size (int): 字體大小\n
        \n
        回傳:\n
        pygame.font.Font: 字體物件\n
        """
        try:
            if self.chinese_font_name:
                # 使用找到的中文字體
                return pygame.font.SysFont(self.chinese_font_name, size)
            else:
                # 使用系統預設字體
                return pygame.font.Font(None, size)
        except Exception as e:
            print(f"⚠️ 字體載入失敗: {e}，使用預設字體")
            return pygame.font.Font(None, size)

    def get_font(self, size_name=None, size_value=None):
        """
        獲取指定大小的字體物件\n
        \n
        參數:\n
        size_name (str): 字體大小名稱（'large', 'medium', 'small', 'tiny'）\n
        size_value (int): 直接指定字體大小數值\n
        \n
        回傳:\n
        pygame.font.Font: 字體物件\n
        \n
        使用範例:\n
        font = font_manager.get_font('large')  # 使用預設大小\n
        font = font_manager.get_font(size_value=32)  # 使用自訂大小\n
        """
        # 確定要使用的字體大小
        if size_name and size_name in FONT_CONFIGS["sizes"]:
            size = FONT_CONFIGS["sizes"][size_name]
            cache_key = f"{size_name}_{size}"
        elif size_value:
            size = size_value
            cache_key = f"custom_{size}"
        else:
            # 預設使用medium大小
            size = FONT_CONFIGS["sizes"]["medium"]
            cache_key = f"medium_{size}"

        # 檢查快取
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]

        # 創建新字體並加入快取
        font = self._create_font(size)
        self._font_cache[cache_key] = font
        return font

    def render_text(
        self, text, font_size="medium", color=(255, 255, 255), antialias=True
    ):
        """
        渲染文字為Surface物件\n
        \n
        參數:\n
        text (str): 要渲染的文字內容\n
        font_size (str): 字體大小名稱\n
        color (tuple): 文字顏色 (R, G, B)\n
        antialias (bool): 是否使用反鋸齒\n
        \n
        回傳:\n
        pygame.Surface: 渲染後的文字Surface\n
        """
        font = self.get_font(font_size)
        return font.render(text, antialias, color)

    def get_text_size(self, text, font_size="medium"):
        """
        獲取文字的尺寸\n
        \n
        參數:\n
        text (str): 文字內容\n
        font_size (str): 字體大小名稱\n
        \n
        回傳:\n
        tuple: (width, height) 文字的寬度和高度\n
        """
        font = self.get_font(font_size)
        return font.size(text)

    def get_available_fonts_info(self):
        """
        獲取字體系統資訊（用於除錯）\n
        \n
        回傳:\n
        dict: 包含字體系統資訊的字典\n
        """
        return {
            "current_chinese_font": self.chinese_font_name,
            "available_system_fonts_count": len(pygame.font.get_fonts()),
            "cached_fonts_count": len(self._font_cache),
            "font_configs": FONT_CONFIGS,
        }


# 全域字體管理器實例
font_manager = FontManager()
