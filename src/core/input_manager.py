######################載入套件######################
import pygame
from src.config import *

######################輸入管理系統######################


class InputManager:
    """
    輸入管理系統 - 統一處理各種輸入設備的控制\n
    \n
    此系統負責：\n
    1. 鍵盤輸入的統一處理\n
    2. 滑鼠輸入的統一處理\n
    3. 輸入映射和自訂按鍵支援\n
    4. 輸入狀態的快取和管理\n
    """

    def __init__(self, game_engine):
        """
        初始化輸入管理系統\n
        \n
        參數:\n
        game_engine: 遊戲引擎主物件\n
        """
        self.game_engine = game_engine

        # 輸入狀態快取
        self.keys_pressed = set()
        self.keys_just_pressed = set()
        self.keys_just_released = set()
        self.previous_keys = pygame.key.get_pressed()

        # 滑鼠狀態
        self.mouse_pos = (0, 0)
        self.mouse_buttons = (False, False, False)
        self.previous_mouse_buttons = (False, False, False)

        # 輸入映射配置（可自訂）
        self.key_mappings = KEYS.copy()

        # 輸入鎖定（在某些狀態下禁用特定輸入）
        self.input_locks = {
            "movement": False,
            "shooting": False,
            "weapon_switch": False,
            "skill": False,
        }

    def update_input_state(self):
        """
        更新輸入狀態（每幀呼叫）\n
        \n
        收集鍵盤和滑鼠的狀態變化\n
        """
        # 更新鍵盤狀態
        current_keys = pygame.key.get_pressed()

        # 計算剛按下和剛釋放的按鍵
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()

        for i in range(len(current_keys)):
            # 剛按下（這幀按下，上幀沒按）
            if current_keys[i] and not self.previous_keys[i]:
                self.keys_just_pressed.add(i)
            # 剛釋放（這幀沒按，上幀按下）
            elif not current_keys[i] and self.previous_keys[i]:
                self.keys_just_released.add(i)

        # 更新持續按下的按鍵集合
        self.keys_pressed.clear()
        for i in range(len(current_keys)):
            if current_keys[i]:
                self.keys_pressed.add(i)

        self.previous_keys = current_keys

        # 更新滑鼠狀態
        self.mouse_pos = pygame.mouse.get_pos()
        self.previous_mouse_buttons = self.mouse_buttons
        self.mouse_buttons = pygame.mouse.get_pressed()

    def is_key_pressed(self, key_name):
        """
        檢查指定按鍵是否持續按下\n
        \n
        參數:\n
        key_name (str): 按鍵名稱（如 'move_up', 'fire'）\n
        \n
        回傳:\n
        bool: 是否按下\n
        """
        if key_name in self.key_mappings:
            key_code = self.key_mappings[key_name]
            return key_code in self.keys_pressed
        return False

    def is_key_just_pressed(self, key_name):
        """
        檢查指定按鍵是否剛剛按下\n
        \n
        參數:\n
        key_name (str): 按鍵名稱\n
        \n
        回傳:\n
        bool: 是否剛按下\n
        """
        if key_name in self.key_mappings:
            key_code = self.key_mappings[key_name]
            return key_code in self.keys_just_pressed
        return False

    def is_key_just_released(self, key_name):
        """
        檢查指定按鍵是否剛剛釋放\n
        \n
        參數:\n
        key_name (str): 按鍵名稱\n
        \n
        回傳:\n
        bool: 是否剛釋放\n
        """
        if key_name in self.key_mappings:
            key_code = self.key_mappings[key_name]
            return key_code in self.keys_just_released
        return False

    def get_movement_input(self):
        """
        獲取移動輸入向量\n
        \n
        回傳:\n
        tuple: (x, y) 移動方向向量，範圍 -1 到 1\n
        """
        if self.input_locks["movement"]:
            return (0, 0)

        move_x = 0
        move_y = 0

        if self.is_key_pressed("move_left"):
            move_x -= 1
        if self.is_key_pressed("move_right"):
            move_x += 1
        if self.is_key_pressed("move_up"):
            move_y -= 1
        if self.is_key_pressed("move_down"):
            move_y += 1

        return (move_x, move_y)

    def get_mouse_position(self):
        """
        獲取滑鼠位置\n
        \n
        回傳:\n
        tuple: (x, y) 滑鼠座標\n
        """
        return self.mouse_pos

    def is_mouse_button_pressed(self, button):
        """
        檢查滑鼠按鈕是否按下\n
        \n
        參數:\n
        button (int): 滑鼠按鈕（0=左鍵, 1=中鍵, 2=右鍵）\n
        \n
        回傳:\n
        bool: 是否按下\n
        """
        if 0 <= button < len(self.mouse_buttons):
            return self.mouse_buttons[button]
        return False

    def is_mouse_button_just_pressed(self, button):
        """
        檢查滑鼠按鈕是否剛剛按下\n
        \n
        參數:\n
        button (int): 滑鼠按鈕\n
        \n
        回傳:\n
        bool: 是否剛按下\n
        """
        if 0 <= button < len(self.mouse_buttons):
            return (
                self.mouse_buttons[button] and not self.previous_mouse_buttons[button]
            )
        return False

    def is_shooting_input_active(self):
        """
        檢查射擊輸入是否啟動\n
        \n
        回傳:\n
        bool: 是否應該射擊\n
        """
        if self.input_locks["shooting"]:
            return False

        # 滑鼠左鍵或空白鍵射擊
        return self.is_mouse_button_pressed(0) or self.is_key_pressed("fire")

    def get_weapon_switch_input(self):
        """
        獲取武器切換輸入\n
        \n
        回傳:\n
        str: 武器編號（"1", "2", "3", "4", "5"）或 None\n
        """
        if self.input_locks["weapon_switch"]:
            return None

        for i in range(1, 6):
            weapon_key = f"weapon_{i}"
            if self.is_key_just_pressed(weapon_key):
                return str(i)

        return None

    def is_reload_input(self):
        """
        檢查重新裝彈輸入\n
        \n
        回傳:\n
        bool: 是否按下重裝按鍵\n
        """
        return self.is_key_just_pressed("reload")

    def is_skill_input(self):
        """
        檢查技能輸入\n
        \n
        回傳:\n
        bool: 是否按下技能按鍵\n
        """
        if self.input_locks["skill"]:
            return False

        return self.is_key_just_pressed("skill")

    def set_input_lock(self, lock_type, locked):
        """
        設置輸入鎖定\n
        \n
        參數:\n
        lock_type (str): 鎖定類型（"movement", "shooting", "weapon_switch", "skill"）\n
        locked (bool): 是否鎖定\n
        """
        if lock_type in self.input_locks:
            self.input_locks[lock_type] = locked

    def is_input_locked(self, lock_type):
        """
        檢查輸入是否被鎖定\n
        \n
        參數:\n
        lock_type (str): 鎖定類型\n
        \n
        回傳:\n
        bool: 是否被鎖定\n
        """
        return self.input_locks.get(lock_type, False)

    def remap_key(self, action_name, new_key):
        """
        重新映射按鍵\n
        \n
        參數:\n
        action_name (str): 動作名稱\n
        new_key (int): 新的按鍵代碼\n
        """
        if action_name in self.key_mappings:
            old_key = self.key_mappings[action_name]
            self.key_mappings[action_name] = new_key
            print(f"🔧 按鍵重新映射: {action_name} {old_key} -> {new_key}")

    def get_key_mappings(self):
        """
        獲取當前按鍵映射\n
        \n
        回傳:\n
        dict: 按鍵映射字典\n
        """
        return self.key_mappings.copy()

    def reset_key_mappings(self):
        """
        重置按鍵映射為預設值\n
        """
        self.key_mappings = KEYS.copy()
        print("🔧 按鍵映射已重置為預設值")

    def clear_input_state(self):
        """
        清空輸入狀態（用於狀態切換等情況）\n
        """
        self.keys_pressed.clear()
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        print("🧹 輸入狀態已清空")
