######################載入套件######################
import pygame
import math
from src.config import *

######################物件類別######################


class Player:
    """
    玩家角色類別 - 處理玩家的所有行為和狀態\n
    \n
    此類別負責管理：\n
    1. 玩家移動控制（WASD按鍵）\n
    2. 生命值和狀態管理\n
    3. 武器切換和彈藥系統\n
    4. 技能冷卻和特殊效果\n
    5. 碰撞檢測和邊界限制\n
    \n
    屬性:\n
    x, y (float): 玩家在螢幕上的位置座標\n
    width, height (int): 玩家的尺寸大小\n
    health (int): 當前生命值，範圍 0-max_health\n
    max_health (int): 最大生命值，可由玩家自訂\n
    speed (float): 移動速度，像素/幀\n
    current_weapon (str): 當前使用的武器類型\n
    weapons (dict): 所有武器的狀態和彈藥資訊\n
    powerups (dict): 當前生效的強化效果\n
    is_reloading (bool): 是否正在填裝彈藥\n
    """

    def __init__(self, x, y, max_health=PLAYER_DEFAULT_HEALTH):
        """
        初始化玩家角色\n
        \n
        參數:\n
        x (float): 初始 X 座標位置\n
        y (float): 初始 Y 座標位置\n
        max_health (int): 最大生命值，預設為 100，範圍 50-200\n
        """
        # 位置和尺寸設定
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE

        # 生命值設定
        self.max_health = max_health
        self.health = max_health
        self.is_alive = True

        # 移動相關
        self.speed = PLAYER_SPEED
        self.velocity_x = 0
        self.velocity_y = 0

        # 武器系統初始化
        self.current_weapon = "pistol"
        self.weapons = {}
        self._init_weapons()

        # 射擊相關
        self.last_shot_time = 0
        self.is_reloading = False
        self.reload_start_time = 0

        # 強化效果系統
        self.powerups = {}

        # 技能系統
        self.skill_cooldown = 0
        self.last_skill_time = 0

        # 輸入狀態追蹤
        self.keys_pressed = set()

    def _init_weapons(self):
        """
        初始化所有武器的彈藥和狀態\n
        \n
        為每種武器設定：\n
        - 當前彈藥數量\n
        - 總備用彈藥\n
        - 是否解鎖（預設只有手槍已解鎖）\n
        """
        for weapon_type, config in WEAPON_CONFIGS.items():
            self.weapons[weapon_type] = {
                "current_ammo": config["max_ammo"],  # 當前彈夾裡的子彈
                "total_ammo": config["max_ammo"] * 3,  # 總備用彈藥
                "unlocked": weapon_type
                in ["pistol", "rifle", "shotgun"],  # 基本武器已解鎖
            }

    def handle_input(self, keys, mouse_pos=None, mouse_buttons=None):
        """
        處理玩家輸入控制\n
        \n
        支援兩種控制模式：\n
        1. 滑鼠控制：滑鼠位置控制移動，右鍵射擊\n
        2. 鍵盤控制：WASD移動，空白鍵射擊\n
        \n
        參數:\n
        keys (pygame.key): pygame 按鍵狀態物件\n
        mouse_pos (tuple): 滑鼠位置座標 (x, y)，可選\n
        mouse_buttons (tuple): 滑鼠按鍵狀態，可選\n
        """
        # 記錄當前按下的按鍵
        self.keys_pressed.clear()

        # 重置移動速度
        self.velocity_x = 0
        self.velocity_y = 0

        # 滑鼠控制模式（優先使用滑鼠控制）
        if mouse_pos is not None:
            self._handle_mouse_movement(mouse_pos)
        else:
            # 鍵盤控制模式（WASD）
            self._handle_keyboard_movement(keys)

    def _handle_mouse_movement(self, mouse_pos):
        """
        處理滑鼠移動控制\n
        \n
        玩家會朝著滑鼠位置移動，但保持合理的移動速度\n
        \n
        參數:\n
        mouse_pos (tuple): 滑鼠位置座標 (x, y)\n
        """
        mouse_x, mouse_y = mouse_pos

        # 計算玩家中心點
        player_center_x = self.x + self.width // 2
        player_center_y = self.y + self.height // 2

        # 計算滑鼠與玩家的距離
        distance_x = mouse_x - player_center_x
        distance_y = mouse_y - player_center_y

        # 計算總距離
        total_distance = math.sqrt(distance_x**2 + distance_y**2)

        # 如果滑鼠離玩家太近就不移動，避免震盪
        if total_distance < 20:
            return

        # 計算移動方向（單位向量）
        if total_distance > 0:
            direction_x = distance_x / total_distance
            direction_y = distance_y / total_distance

            # 設定移動速度
            self.velocity_x = direction_x * self.speed
            self.velocity_y = direction_y * self.speed

            # 記錄移動方向（用於UI顯示等）
            if abs(direction_x) > abs(direction_y):
                if direction_x > 0:
                    self.keys_pressed.add("right")
                else:
                    self.keys_pressed.add("left")
            else:
                if direction_y > 0:
                    self.keys_pressed.add("down")
                else:
                    self.keys_pressed.add("up")

    def _handle_keyboard_movement(self, keys):
        """
        處理鍵盤移動控制（WASD）\n
        \n
        參數:\n
        keys (pygame.key): pygame 按鍵狀態物件\n
        """
        # 檢查移動按鍵（WASD）
        if keys[KEYS["move_left"]]:
            self.velocity_x = -self.speed
            self.keys_pressed.add("left")
        if keys[KEYS["move_right"]]:
            self.velocity_x = self.speed
            self.keys_pressed.add("right")
        if keys[KEYS["move_up"]]:
            self.velocity_y = -self.speed
            self.keys_pressed.add("up")
        if keys[KEYS["move_down"]]:
            self.velocity_y = self.speed
            self.keys_pressed.add("down")

        # 斜向移動時速度調整（讓斜向移動不會比較快）
        if self.velocity_x != 0 and self.velocity_y != 0:
            # 用畢氏定理算出斜向移動時應該要多慢
            diagonal_speed = self.speed / math.sqrt(2)
            if self.velocity_x > 0:
                self.velocity_x = diagonal_speed
            else:
                self.velocity_x = -diagonal_speed
            if self.velocity_y > 0:
                self.velocity_y = diagonal_speed
            else:
                self.velocity_y = -diagonal_speed

    def handle_weapon_switch(self, weapon_key):
        """
        處理武器切換邏輯\n
        \n
        參數:\n
        weapon_key (str): 武器按鍵（'1', '2', '3', '4', '5'）\n
        \n
        回傳:\n
        bool: 是否成功切換武器\n
        """
        weapon_map = {
            "1": "pistol",
            "2": "rifle",
            "3": "shotgun",
            "4": "machinegun",
            "5": "submachinegun",
        }

        if weapon_key in weapon_map:
            new_weapon = weapon_map[weapon_key]

            # 檢查武器是否已解鎖
            if self.weapons[new_weapon]["unlocked"]:
                # 如果正在填裝，先取消填裝
                if self.is_reloading:
                    self.is_reloading = False

                self.current_weapon = new_weapon
                return True

        return False

    def start_reload(self):
        """
        開始填裝彈藥\n
        \n
        檢查是否可以填裝：\n
        - 當前彈夾未滿\n
        - 有備用彈藥\n
        - 沒有正在填裝\n
        \n
        回傳:\n
        bool: 是否成功開始填裝\n
        """
        weapon_config = WEAPON_CONFIGS[self.current_weapon]
        weapon_state = self.weapons[self.current_weapon]

        # 檢查是否需要填裝
        if (
            weapon_state["current_ammo"] < weapon_config["max_ammo"]
            and weapon_state["total_ammo"] > 0
            and not self.is_reloading
        ):

            self.is_reloading = True
            self.reload_start_time = pygame.time.get_ticks()
            return True

        return False

    def update_reload(self):
        """
        更新填裝狀態\n
        \n
        檢查填裝是否完成，如果完成就補充彈藥\n
        """
        if not self.is_reloading:
            return

        current_time = pygame.time.get_ticks()
        weapon_config = WEAPON_CONFIGS[self.current_weapon]

        # 檢查填裝時間是否足夠
        if current_time - self.reload_start_time >= weapon_config["reload_time"]:
            # 填裝完成，補充彈藥
            weapon_state = self.weapons[self.current_weapon]

            # 計算需要補充多少子彈
            ammo_needed = weapon_config["max_ammo"] - weapon_state["current_ammo"]
            ammo_to_add = min(ammo_needed, weapon_state["total_ammo"])

            # 更新彈藥數量
            weapon_state["current_ammo"] += ammo_to_add
            weapon_state["total_ammo"] -= ammo_to_add

            # 結束填裝狀態
            self.is_reloading = False

    def can_shoot(self):
        """
        檢查是否可以射擊\n
        \n
        條件：\n
        - 有子彈\n
        - 沒有在填裝\n
        - 射擊冷卻時間已過\n
        \n
        回傳:\n
        bool: 是否可以射擊\n
        """
        if self.is_reloading:
            return False

        weapon_state = self.weapons[self.current_weapon]
        if weapon_state["current_ammo"] <= 0:
            return False

        # 檢查射擊冷卻時間
        current_time = pygame.time.get_ticks()
        weapon_config = WEAPON_CONFIGS[self.current_weapon]

        if current_time - self.last_shot_time < weapon_config["fire_rate"]:
            return False

        return True

    def shoot(self):
        """
        執行射擊動作\n
        \n
        消耗彈藥並記錄射擊時間\n
        \n
        回傳:\n
        dict: 射擊資訊，包含子彈數量和散布角度\n
        """
        if not self.can_shoot():
            return None

        # 消耗彈藥
        weapon_state = self.weapons[self.current_weapon]
        weapon_config = WEAPON_CONFIGS[self.current_weapon]
        weapon_state["current_ammo"] -= 1

        # 記錄射擊時間
        self.last_shot_time = pygame.time.get_ticks()

        # 準備射擊資料
        shot_data = {
            "damage": weapon_config["damage"],
            "speed": weapon_config["bullet_speed"],
            "bullets": [],
        }

        # 檢查是否有散彈效果（散彈槍或強化效果）
        bullet_count = 1
        spread_angle = 0

        if weapon_config.get("spread", False):
            # 散彈槍本身的散彈效果
            bullet_count = weapon_config["bullet_count"]
            spread_angle = 30  # 散彈角度範圍
        elif "scatter_shot" in self.powerups:
            # 散彈強化效果
            bullet_count = POWERUP_EFFECTS["scatter_shot"]["bullet_count"]
            spread_angle = 25

        # 檢查火力增強效果
        damage_multiplier = 1.0
        if "fire_boost" in self.powerups:
            damage_multiplier = POWERUP_EFFECTS["fire_boost"]["damage_multiplier"]

        # 產生子彈資料
        for i in range(bullet_count):
            if bullet_count == 1:
                # 單發子彈，直線射擊
                angle = 0
            else:
                # 多發子彈，計算散布角度
                angle_step = spread_angle / (bullet_count - 1)
                angle = -spread_angle / 2 + i * angle_step

            bullet_info = {
                "x": self.x + self.width / 2,
                "y": self.y,
                "angle": angle,
                "damage": weapon_config["damage"] * damage_multiplier,
                "speed": weapon_config["bullet_speed"],
            }
            shot_data["bullets"].append(bullet_info)

        return shot_data

    def use_skill(self):
        """
        使用特殊技能 - 全螢幕範圍攻擊\n
        \n
        技能效果：\n
        - 冷卻時間：2分鐘（120秒）\n
        - 生命值消耗：10%當前最大生命值\n
        - 攻擊範圍：整個視窗\n
        - 傷害：對所有敵人造成大量傷害\n
        \n
        回傳:\n
        dict: 技能使用結果，包含是否成功和技能資訊\n
        """
        current_time = pygame.time.get_ticks()

        # 檢查技能冷卻時間（2分鐘 = 120000毫秒）
        skill_cooldown_duration = 120000
        if current_time - self.last_skill_time < skill_cooldown_duration:
            return {"success": False, "reason": "技能冷卻中"}

        # 檢查生命值是否足夠（需要至少10%生命值）
        skill_cost = int(self.max_health * 0.1)
        if self.health <= skill_cost:
            return {"success": False, "reason": "生命值不足"}

        # 消耗生命值
        self.health -= skill_cost

        # 確保生命值不會為0（至少保留1點）
        if self.health <= 0:
            self.health = 1

        # 啟動技能效果
        skill_damage = 200  # 技能傷害值
        self.last_skill_time = current_time

        return {
            "success": True,
            "damage": skill_damage,
            "range": "fullscreen",  # 全螢幕範圍
            "effect_type": "area_damage",
            "health_cost": skill_cost,
        }

    def apply_powerup(self, powerup_type):
        """
        套用強化效果\n
        \n
        參數:\n
        powerup_type (str): 強化類型（'fire_boost', 'ammo_refill', 'scatter_shot', 'machinegun_powerup', 'submachinegun_powerup'）\n
        """
        current_time = pygame.time.get_ticks()

        if powerup_type == "ammo_refill":
            # 立即補充所有武器彈藥
            for weapon_type, weapon_state in self.weapons.items():
                weapon_config = WEAPON_CONFIGS[weapon_type]
                weapon_state["current_ammo"] = weapon_config["max_ammo"]
                weapon_state["total_ammo"] = weapon_config["max_ammo"] * 3
        elif powerup_type in ["machinegun_powerup", "submachinegun_powerup"]:
            # 武器解鎖效果
            effect_config = POWERUP_EFFECTS[powerup_type]
            weapon_type = effect_config["weapon_unlock"]

            # 解鎖武器
            self.weapons[weapon_type]["unlocked"] = True

            # 添加額外彈藥
            bonus_ammo = effect_config["ammo_bonus"]
            self.weapons[weapon_type]["total_ammo"] += bonus_ammo

            # 如果彈夾是空的就填滿
            if self.weapons[weapon_type]["current_ammo"] == 0:
                weapon_config = WEAPON_CONFIGS[weapon_type]
                self.weapons[weapon_type]["current_ammo"] = weapon_config["max_ammo"]
        else:
            # 時間性強化效果
            effect_config = POWERUP_EFFECTS[powerup_type]
            self.powerups[powerup_type] = {
                "start_time": current_time,
                "duration": effect_config["duration"],
            }

    def update_powerups(self):
        """
        更新所有強化效果的時間\n
        \n
        移除已過期的強化效果\n
        """
        current_time = pygame.time.get_ticks()
        expired_powerups = []

        for powerup_type, powerup_data in self.powerups.items():
            if "duration" in powerup_data:
                if (
                    current_time - powerup_data["start_time"]
                    >= powerup_data["duration"]
                ):
                    expired_powerups.append(powerup_type)

        # 移除過期的強化效果
        for powerup_type in expired_powerups:
            del self.powerups[powerup_type]

    def take_damage(self, damage):
        """
        承受傷害\n
        \n
        參數:\n
        damage (int): 傷害數值\n
        \n
        回傳:\n
        bool: 是否仍然存活\n
        """
        # 檢查是否有無敵效果
        if "skill_boost" in self.powerups and self.powerups["skill_boost"].get(
            "invincible", False
        ):
            return True  # 無敵狀態不受傷害

        self.health -= damage

        # 確保生命值不會低於0
        if self.health <= 0:
            self.health = 0
            self.is_alive = False

        return self.is_alive

    def heal(self, amount):
        """
        回復生命值\n
        \n
        參數:\n
        amount (int): 回復數值\n
        """
        self.health += amount

        # 確保生命值不會超過最大值
        if self.health > self.max_health:
            self.health = self.max_health

    def update(self, screen_width, screen_height):
        """
        更新玩家狀態（每幀呼叫）\n
        \n
        處理：\n
        1. 位置更新和邊界檢查\n
        2. 填裝狀態更新\n
        3. 強化效果時間管理\n
        4. 技能效果套用\n
        \n
        參數:\n
        screen_width (int): 螢幕寬度\n
        screen_height (int): 螢幕高度\n
        """
        # 套用技能速度加成
        current_speed = self.speed
        if "skill_boost" in self.powerups:
            current_speed *= self.powerups["skill_boost"]["speed_boost"]

        # 更新位置
        self.x += self.velocity_x
        self.y += self.velocity_y

        # 邊界檢查 - 不讓玩家跑出螢幕
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > screen_width:
            self.x = screen_width - self.width

        if self.y < 0:
            self.y = 0
        elif self.y + self.height > screen_height:
            self.y = screen_height - self.height

        # 更新各種系統狀態
        self.update_reload()
        self.update_powerups()

    def draw(self, screen):
        """
        繪製玩家角色\n
        \n
        根據當前狀態顯示不同顏色：\n
        - 正常：藍色\n
        - 填裝中：黃色\n
        - 技能狀態：紫色\n
        - 生命值低：紅色\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        """
        # 根據狀態決定顏色
        color = COLORS["blue"]  # 預設藍色

        if "skill_boost" in self.powerups:
            color = COLORS["purple"]  # 技能狀態用紫色
        elif self.is_reloading:
            color = COLORS["yellow"]  # 填裝中用黃色
        elif self.health < self.max_health * 0.3:
            color = COLORS["red"]  # 血量低用紅色

        # 畫玩家方塊
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))

        # 畫邊框讓玩家更明顯
        pygame.draw.rect(
            screen, COLORS["white"], (self.x, self.y, self.width, self.height), 2
        )

    def get_rect(self):
        """
        取得碰撞檢測用的矩形\n
        \n
        回傳:\n
        pygame.Rect: 碰撞檢測矩形\n
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def get_weapon_info(self):
        """
        取得當前武器資訊\n
        \n
        回傳:\n
        dict: 武器狀態資訊\n
        """
        weapon_config = WEAPON_CONFIGS[self.current_weapon]
        weapon_state = self.weapons[self.current_weapon]

        return {
            "name": weapon_config["name"],
            "current_ammo": weapon_state["current_ammo"],
            "max_ammo": weapon_config["max_ammo"],
            "total_ammo": weapon_state["total_ammo"],
            "is_reloading": self.is_reloading,
        }

    def get_powerup_status(self):
        """
        取得當前強化效果狀態\n
        \n
        回傳:\n
        list: 生效中的強化效果列表\n
        """
        current_time = pygame.time.get_ticks()
        active_powerups = []

        for powerup_type, powerup_data in self.powerups.items():
            if "duration" in powerup_data:
                remaining_time = powerup_data["duration"] - (
                    current_time - powerup_data["start_time"]
                )
                if remaining_time > 0:
                    effect_name = POWERUP_EFFECTS.get(powerup_type, {}).get(
                        "name", powerup_type
                    )
                    active_powerups.append(
                        {
                            "name": effect_name,
                            "remaining_time": remaining_time / 1000,  # 轉成秒
                        }
                    )

        return active_powerups

    def get_skill_cooldown_info(self):
        """
        取得技能冷卻時間資訊\n
        \n
        回傳:\n
        dict: 技能冷卻狀態資訊\n
        """
        current_time = pygame.time.get_ticks()
        skill_cooldown_duration = 120000  # 2分鐘
        time_since_last_skill = current_time - self.last_skill_time

        if time_since_last_skill < skill_cooldown_duration:
            cooldown_remaining = (
                skill_cooldown_duration - time_since_last_skill
            ) / 1000
            return {
                "ready": False,
                "cooldown_remaining": cooldown_remaining,
                "total_cooldown": skill_cooldown_duration / 1000,
            }
        else:
            return {
                "ready": True,
                "cooldown_remaining": 0,
                "total_cooldown": skill_cooldown_duration / 1000,
            }
