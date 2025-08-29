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
        self.weapon_images = {}  # 武器圖片快取

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
            # 嘗試載入圖片
            full_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), image_path
            )

            if not os.path.exists(full_path):
                print(f"圖片檔案不存在: {full_path}")
                return self._create_fallback_image(character_config, size)

            # 載入並處理圖片
            raw_image = pygame.image.load(full_path)

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
        創建降級顯示圖片（優先使用備用圖片，然後是幾何形狀）\n
        \n
        當主要圖片載入失敗時，先嘗試載入備用圖片，如果備用圖片也失敗，則使用幾何形狀代替\n
        \n
        參數:\n
        character_config (dict): 角色配置資訊\n
        size (tuple): 圖片尺寸\n
        \n
        回傳:\n
        pygame.Surface: 備用圖片或幾何形狀圖片\n
        """
        # 首先嘗試載入備用圖片
        fallback_image = self._try_load_fallback_image(character_config, size)
        if fallback_image:
            return fallback_image

        # 如果備用圖片也載入失敗，則創建幾何形狀
        return self._create_geometric_shape(character_config, size)

    def _try_load_fallback_image(self, character_config, size):
        """
        嘗試載入備用圖片（優先使用配置中指定的備用圖片路徑）\n
        \n
        參數:\n
        character_config (dict): 角色配置資訊\n
        size (tuple): 圖片尺寸\n
        \n
        回傳:\n
        pygame.Surface: 備用圖片，如果載入失敗則返回 None\n
        """
        if not character_config:
            return None

        # 優先使用配置中指定的備用圖片路徑
        fallback_path = character_config.get("fallback_image_path")

        if fallback_path:
            try:
                # 嘗試載入配置中指定的備用圖片
                full_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    fallback_path,
                )

                if not os.path.exists(full_path):
                    print(f"🔄 配置的備用圖片檔案不存在: {full_path}")
                else:
                    print(f"🔄 載入配置的備用圖片: {fallback_path}")
                    raw_image = pygame.image.load(full_path)

                    # 檢查 pygame 顯示是否已初始化
                    try:
                        raw_image = raw_image.convert_alpha()
                    except pygame.error:
                        raw_image = raw_image.convert()

                    # 縮放圖片
                    scaled_image = pygame.transform.scale(raw_image, size)

                    print(f"✅ 成功載入配置的備用圖片: {fallback_path}")
                    return scaled_image

            except Exception as e:
                print(f"❌ 載入配置的備用圖片失敗 ({fallback_path}): {e}")

        # 如果沒有配置備用圖片或載入失敗，使用預設的備用圖片
        default_fallback_paths = {
            "cat": "assets/characters/cat.jpg",  # 原始的貓圖片
            "dog": "assets/characters/dog.jpg",  # 原始的狗圖片
            "wolf": "assets/characters/wolf.jpg",  # 原始的狼圖片
        }

        # 根據角色類型獲取預設備用圖片路徑
        character_name = character_config.get("name", "")
        default_fallback_path = None

        if "貓" in character_name:
            default_fallback_path = default_fallback_paths.get("cat")
        elif "狗" in character_name:
            default_fallback_path = default_fallback_paths.get("dog")
        elif "狼" in character_name:
            default_fallback_path = default_fallback_paths.get("wolf")

        if not default_fallback_path:
            return None

        try:
            # 嘗試載入預設備用圖片
            full_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                default_fallback_path,
            )

            if not os.path.exists(full_path):
                print(f"🔄 預設備用圖片檔案不存在: {full_path}")
                return None

            print(f"🔄 載入預設備用圖片: {default_fallback_path}")
            raw_image = pygame.image.load(full_path)

            # 檢查 pygame 顯示是否已初始化
            try:
                raw_image = raw_image.convert_alpha()
            except pygame.error:
                raw_image = raw_image.convert()

            # 縮放圖片
            scaled_image = pygame.transform.scale(raw_image, size)

            print(f"✅ 成功載入預設備用圖片: {default_fallback_path}")
            return scaled_image

        except Exception as e:
            print(f"❌ 載入預設備用圖片失敗 ({default_fallback_path}): {e}")
            return None

    def _create_geometric_shape(self, character_config, size):
        """
        創建幾何形狀圖片\n
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

        print(f"🔶 使用幾何形狀作為最終備用方案: {character_type}")

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

    def load_weapon_image(self, weapon_type, size=(40, 40)):
        """
        載入武器圖片\n
        \n
        參數:\n
        weapon_type (str): 武器類型 ("pistol", "rifle", "shotgun", "machinegun", "submachinegun")\n
        size (tuple): 圖片尺寸 (width, height)\n
        \n
        回傳:\n
        pygame.Surface: 處理後的武器圖片，如果載入失敗則返回預設圖示\n
        """
        # 建立快取鍵值
        cache_key = f"weapon_{weapon_type}_{size[0]}x{size[1]}"

        # 檢查快取
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]

        weapon_config = WEAPON_CONFIGS.get(weapon_type)
        if not weapon_config or "image_path" not in weapon_config:
            # 沒有圖片配置，使用預設圖示
            return self._create_weapon_fallback_image(weapon_type, size)

        image_path = weapon_config["image_path"]

        try:
            # 嘗試載入圖片 - 修正路徑計算
            # __file__ 位於 src/utils/image_manager.py
            # 需要回到專案根目錄：src/utils -> src -> 專案根目錄
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            full_path = os.path.join(project_root, image_path)

            if not os.path.exists(full_path):
                print(f"武器圖片檔案不存在: {full_path}")
                return self._create_weapon_fallback_image(weapon_type, size)

            # 載入並處理圖片
            raw_image = pygame.image.load(full_path)

            # 檢查 pygame 顯示是否已初始化
            try:
                raw_image = raw_image.convert_alpha()
            except pygame.error:
                # 如果顯示未初始化，只使用 convert()
                raw_image = raw_image.convert()

            # 縮放圖片
            scaled_image = pygame.transform.scale(raw_image, size)

            # 快取處理後的圖片
            self.image_cache[cache_key] = scaled_image
            print(f"✅ 成功載入武器圖片: {weapon_type} - {image_path}")
            return scaled_image

        except pygame.error as e:
            print(f"載入武器圖片失敗 ({weapon_type}): {e}")
            return self._create_weapon_fallback_image(weapon_type, size)
        except Exception as e:
            print(f"處理武器圖片時發生錯誤 ({weapon_type}): {e}")
            return self._create_weapon_fallback_image(weapon_type, size)

    def _create_weapon_fallback_image(self, weapon_type, size):
        """
        創建武器預設圖示（當圖片載入失敗時使用）\n
        \n
        參數:\n
        weapon_type (str): 武器類型\n
        size (tuple): 圖片尺寸\n
        \n
        回傳:\n
        pygame.Surface: 武器預設圖示\n
        """
        surface = pygame.Surface(size, pygame.SRCALPHA)
        center_x, center_y = size[0] // 2, size[1] // 2

        # 根據武器類型選擇顏色和形狀
        weapon_colors = {
            "pistol": COLORS["gray"],  # 手槍 - 灰色
            "rifle": COLORS["dark_gray"],  # 步槍 - 深灰色
            "shotgun": (139, 69, 19),  # 霰彈槍 - 棕色
            "machinegun": (64, 64, 64),  # 機關槍 - 暗灰色
            "submachinegun": (105, 105, 105),  # 衝鋒槍 - 中灰色
        }

        weapon_name = WEAPON_CONFIGS.get(weapon_type, {}).get("name", weapon_type)
        color = weapon_colors.get(weapon_type, COLORS["gray"])

        print(f"🔶 使用預設武器圖示: {weapon_name}")

        # 根據武器類型繪製不同形狀
        if weapon_type == "pistol":
            # 手槍 - 小矩形
            rect_size = min(size) // 2
            rect_x = (size[0] - rect_size) // 2
            rect_y = (size[1] - rect_size) // 2
            pygame.draw.rect(surface, color, (rect_x, rect_y, rect_size, rect_size))
            pygame.draw.rect(
                surface, COLORS["white"], (rect_x, rect_y, rect_size, rect_size), 1
            )

        elif weapon_type == "rifle":
            # 步槍 - 長矩形
            rect_width = size[0] - 4
            rect_height = size[1] // 3
            rect_x = 2
            rect_y = (size[1] - rect_height) // 2
            pygame.draw.rect(surface, color, (rect_x, rect_y, rect_width, rect_height))
            pygame.draw.rect(
                surface, COLORS["white"], (rect_x, rect_y, rect_width, rect_height), 1
            )

        elif weapon_type == "shotgun":
            # 霰彈槍 - 粗短矩形
            rect_width = size[0] - 6
            rect_height = size[1] // 2
            rect_x = 3
            rect_y = (size[1] - rect_height) // 2
            pygame.draw.rect(surface, color, (rect_x, rect_y, rect_width, rect_height))
            pygame.draw.rect(
                surface, COLORS["white"], (rect_x, rect_y, rect_width, rect_height), 2
            )
            # 添加槍管裝飾
            barrel_y = rect_y + rect_height // 4
            pygame.draw.line(
                surface,
                COLORS["white"],
                (rect_x + 2, barrel_y),
                (rect_x + rect_width - 2, barrel_y),
                1,
            )

        elif weapon_type == "machinegun":
            # 機關槍 - 複雜形狀
            # 主體
            main_width = size[0] - 4
            main_height = size[1] // 2
            main_x = 2
            main_y = (size[1] - main_height) // 2
            pygame.draw.rect(surface, color, (main_x, main_y, main_width, main_height))
            # 槍管
            barrel_width = main_width // 3
            barrel_height = main_height // 2
            barrel_x = main_x + main_width - barrel_width
            barrel_y = main_y - barrel_height // 2
            pygame.draw.rect(
                surface, color, (barrel_x, barrel_y, barrel_width, barrel_height)
            )
            pygame.draw.rect(
                surface, COLORS["white"], (main_x, main_y, main_width, main_height), 1
            )

        elif weapon_type == "submachinegun":
            # 衝鋒槍 - 中等大小
            rect_width = size[0] - 8
            rect_height = size[1] // 3
            rect_x = 4
            rect_y = (size[1] - rect_height) // 2
            pygame.draw.rect(surface, color, (rect_x, rect_y, rect_width, rect_height))
            # 添加握把
            grip_width = rect_width // 4
            grip_height = rect_height + 4
            grip_x = rect_x + rect_width // 4
            grip_y = rect_y - 2
            pygame.draw.rect(surface, color, (grip_x, grip_y, grip_width, grip_height))
            pygame.draw.rect(
                surface, COLORS["white"], (rect_x, rect_y, rect_width, rect_height), 1
            )

        else:
            # 預設 - 圓形
            pygame.draw.circle(surface, color, (center_x, center_y), min(size) // 2 - 2)
            pygame.draw.circle(
                surface, COLORS["white"], (center_x, center_y), min(size) // 2 - 2, 1
            )

        return surface

    def get_weapon_image(self, weapon_type, size=(40, 40)):
        """
        取得武器圖片（公開介面）\n
        \n
        參數:\n
        weapon_type (str): 武器類型\n
        size (tuple): 圖片尺寸\n
        \n
        回傳:\n
        pygame.Surface: 武器圖片\n
        """
        return self.load_weapon_image(weapon_type, size)

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
        self.weapon_images.clear()


# 創建全域圖片管理器實例
image_manager = ImageManager()
