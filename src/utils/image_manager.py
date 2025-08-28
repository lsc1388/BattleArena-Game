######################載入套件######################
import pygame
import os
from src.config import *

######################圖片管理類別######################


class ImageManager:
    """
    圖片管理器 - 負責載入、縮放和快取角色圖片\n
    \n
    此類別提供：\n
    1. 角色圖片的載入和快取\n
    2. 圖片縮放和格式轉換\n
    3. 錯誤處理和降級顯示\n
    4. 圓形遮罩處理\n
    \n
    採用單例模式，確保全域只有一個圖片管理器實例\n
    """

    _instance = None

    def __new__(cls):
        """
        單例模式實作\n
        確保只有一個 ImageManager 實例存在\n
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """
        初始化圖片管理器\n
        \n
        設定快取字典和預設參數\n
        注意：不在此處預載入圖片，因為 pygame.display 可能尚未初始化\n
        """
        if self._initialized:
            return

        self._initialized = True
        self.image_cache = {}  # 圖片快取
        self.character_images = {}  # 角色圖片快取

        # 不在初始化時預載入圖片，改為延遲載入

    def _preload_character_images(self):
        """
        預載入所有角色圖片\n
        \n
        在遊戲啟動時就載入所有角色圖片，避免遊戲中的延遲\n
        """
        for character_type, config in CHARACTER_CONFIGS.items():
            if "image_path" in config:
                # 載入選擇界面用的圖片（較大）
                selection_image = self.load_character_image(
                    character_type, size=(120, 120), for_selection=True
                )

                # 載入遊戲中用的圖片（較小）
                game_image = self.load_character_image(
                    character_type, size=(PLAYER_SIZE, PLAYER_SIZE), for_selection=False
                )

    def load_character_image(
        self, character_type, size=(PLAYER_SIZE, PLAYER_SIZE), for_selection=False
    ):
        """
        載入角色圖片\n
        \n
        參數:\n
        character_type (str): 角色類型 ("cat", "dog", "wolf")\n
        size (tuple): 圖片尺寸 (width, height)\n
        for_selection (bool): 是否用於選擇界面（影響快取鍵值）\n
        \n
        回傳:\n
        pygame.Surface: 處理後的角色圖片，如果載入失敗則返回幾何形狀\n
        """
        # 建立快取鍵值
        cache_key = f"{character_type}_{size[0]}x{size[1]}_{'selection' if for_selection else 'game'}"

        # 檢查快取
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]

        character_config = CHARACTER_CONFIGS.get(character_type)
        if not character_config or "image_path" not in character_config:
            # 沒有圖片配置，使用幾何形狀
            return self._create_fallback_image(character_config, size)

        image_path = character_config["image_path"]

        try:
            # 計算圖片的完整路徑
            # 如果是絕對路徑，直接使用
            if os.path.isabs(image_path):
                full_path = image_path
            else:
                # 相對路徑，從專案根目錄開始計算
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                full_path = os.path.join(project_root, image_path)
            
            print(f"🔍 嘗試載入圖片: {character_type} - {full_path}")

            if not os.path.exists(full_path):
                print(f"圖片檔案不存在: {full_path}")
                return self._create_fallback_image(character_config, size)

            # 載入並處理圖片
            raw_image = pygame.image.load(full_path)
            print(f"✅ 成功載入角色圖片: {character_type} - {full_path}")

            # 檢查 pygame 顯示是否已初始化
            try:
                raw_image = raw_image.convert_alpha()
            except pygame.error:
                # 如果顯示未初始化，只使用 convert()
                raw_image = raw_image.convert()

            # 縮放圖片
            scaled_image = pygame.transform.scale(raw_image, size)

            # 直接使用縮放後的圖片，不再套用圓形遮罩
            processed_image = scaled_image

            # 快取處理後的圖片
            self.image_cache[cache_key] = processed_image
            return processed_image

        except pygame.error as e:
            print(f"載入角色圖片失敗 ({character_type}): {e}")
            return self._create_fallback_image(character_config, size)
        except Exception as e:
            print(f"處理角色圖片時發生錯誤 ({character_type}): {e}")
            return self._create_fallback_image(character_config, size)

    def _create_fallback_image(self, character_config, size):
        """
        創建降級顯示圖片（幾何形狀）\n
        \n
        當圖片載入失敗時，使用幾何形狀代替\n
        \n
        參數:\n
        character_config (dict): 角色配置資訊\n
        size (tuple): 圖片尺寸\n
        \n
        回傳:\n
        pygame.Surface: 幾何形狀圖片\n
        """
        surface = pygame.Surface(size, pygame.SRCALPHA)
        center_x, center_y = size[0] // 2, size[1] // 2

        if character_config:
            color = character_config["color"]
            character_type = character_config.get("name", "未知")
        else:
            color = COLORS["gray"]
            character_type = "未知"

        # 根據角色類型繪製不同形狀
        if "貓" in character_type:
            # 貓 - 圓形
            pygame.draw.circle(surface, color, (center_x, center_y), min(size) // 2 - 2)
            pygame.draw.circle(
                surface, COLORS["white"], (center_x, center_y), min(size) // 2 - 2, 2
            )
        elif "狗" in character_type:
            # 狗 - 方形
            rect_size = min(size) - 4
            rect_x = (size[0] - rect_size) // 2
            rect_y = (size[1] - rect_size) // 2
            pygame.draw.rect(surface, color, (rect_x, rect_y, rect_size, rect_size))
            pygame.draw.rect(
                surface, COLORS["white"], (rect_x, rect_y, rect_size, rect_size), 2
            )
        elif "狼" in character_type:
            # 狼 - 三角形
            triangle_size = min(size) - 4
            points = [
                (center_x, center_y - triangle_size // 2),  # 頂點
                (center_x - triangle_size // 2, center_y + triangle_size // 2),  # 左下
                (center_x + triangle_size // 2, center_y + triangle_size // 2),  # 右下
            ]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, COLORS["white"], points, 2)
        else:
            # 預設 - 圓形
            pygame.draw.circle(surface, color, (center_x, center_y), min(size) // 2 - 2)
            pygame.draw.circle(
                surface, COLORS["white"], (center_x, center_y), min(size) // 2 - 2, 2
            )

        return surface

    def get_character_image_for_selection(self, character_type):
        """
        取得角色選擇界面用的圖片\n
        \n
        參數:\n
        character_type (str): 角色類型\n
        \n
        回傳:\n
        pygame.Surface: 選擇界面用的角色圖片\n
        """
        return self.load_character_image(
            character_type, size=(120, 120), for_selection=True
        )

    def get_character_image_for_game(self, character_type):
        """
        取得遊戲中用的角色圖片\n
        \n
        參數:\n
        character_type (str): 角色類型\n
        \n
        回傳:\n
        pygame.Surface: 遊戲中用的角色圖片\n
        """
        return self.load_character_image(
            character_type, size=(PLAYER_SIZE, PLAYER_SIZE), for_selection=False
        )

    def clear_cache(self):
        """
        清除圖片快取\n
        \n
        釋放記憶體，通常在遊戲結束時呼叫\n
        """
        self.image_cache.clear()
        self.character_images.clear()


# 創建全域圖片管理器實例
image_manager = ImageManager()
