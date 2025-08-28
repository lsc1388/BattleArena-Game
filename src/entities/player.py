######################載入套件######################
import pygame
import math
from src.config import *
from src.utils.image_manager import image_manager
from src.utils.sound_manager import sound_manager

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

    def __init__(self, x, y, max_health=PLAYER_DEFAULT_HEALTH, character_type="cat"):
        """
        初始化玩家角色\n
        \n
        參數:\n
        x (float): 初始 X 座標位置\n
        y (float): 初始 Y 座標位置\n
        max_health (int): 最大生命值，預設為 100，範圍 50-200\n
        character_type (str): 角色類型 ("cat", "dog", "wolf")\n
        """
        # 位置和尺寸設定
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE

        # 角色設定
        self.character_type = character_type
        self.character_config = CHARACTER_CONFIGS.get(
            character_type, CHARACTER_CONFIGS["cat"]
        )

        # 生命值設定（應用角色血量倍率）
        health_multiplier = self.character_config["attributes"]["health"]
        self.max_health = int(max_health * health_multiplier)
        self.health = self.max_health
        self.is_alive = True

        # 移動相關（應用角色速度倍率）
        speed_multiplier = self.character_config["attributes"]["speed"]
        self.speed = PLAYER_SPEED * speed_multiplier
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
        self.active_skill = None  # 當前啟用的技能
        self.skill_start_time = 0  # 技能開始時間

        # 輸入狀態追蹤
        self.keys_pressed = set()
        self.mouse_position = (0, 0)  # 儲存滑鼠位置用於技能方向控制

        # 載入角色圖片
        self.character_image = image_manager.get_character_image_for_game(
            self.character_type
        )

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
        根據新規格：\n
        - 移動控制：WASD 控制角色位置（固定使用鍵盤）\n
        - 射擊準心：滑鼠移動準心，子彈命中位置為準心正中心\n
        - 技能方向：當技能啟動時，技能攻擊方向跟隨滑鼠位置\n
        \n
        參數:\n
        keys (pygame.key): pygame 按鍵狀態物件\n
        mouse_pos (tuple): 滑鼠位置座標 (x, y)，用於準心顯示和技能方向控制\n
        mouse_buttons (tuple): 滑鼠按鍵狀態，暫時保留但不用於移動控制\n
        """
        # 記錄當前按下的按鍵
        self.keys_pressed.clear()

        # 重置移動速度
        self.velocity_x = 0
        self.velocity_y = 0

        # 儲存滑鼠位置用於技能方向控制
        if mouse_pos:
            self.mouse_position = mouse_pos

        # 始終使用鍵盤控制移動（WASD）
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
        - 射擊冷卻時間已過（應用角色射速倍率）\n
        \n
        回傳:\n
        bool: 是否可以射擊\n
        """
        if self.is_reloading:
            return False

        weapon_state = self.weapons[self.current_weapon]
        if weapon_state["current_ammo"] <= 0:
            return False

        # 檢查射擊冷卻時間（應用角色射速倍率）
        current_time = pygame.time.get_ticks()
        weapon_config = WEAPON_CONFIGS[self.current_weapon]

        # 角色射速倍率影響射擊間隔（射速高則間隔短）
        fire_rate_multiplier = self.character_config["attributes"]["fire_rate"]
        adjusted_fire_rate = weapon_config["fire_rate"] / fire_rate_multiplier

        if current_time - self.last_shot_time < adjusted_fire_rate:
            return False

        return True

    def shoot(self, target_pos=None):
        """
        執行射擊動作\n
        \n
        消耗彈藥並記錄射擊時間\n
        \n
        參數:\n
        target_pos (tuple): 目標位置 (x, y)，如果提供則朝該方向射擊\n
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

        # 播放武器射擊音效
        sound_manager.play_weapon_sound(self.current_weapon)

        # 計算射擊角度
        if target_pos:
            # 朝目標位置射擊
            player_center_x = self.x + self.width / 2
            player_center_y = self.y + self.height / 2
            target_x, target_y = target_pos

            dx = target_x - player_center_x
            dy = target_y - player_center_y

            # 計算角度（degrees）
            base_angle = math.degrees(math.atan2(dy, dx)) + 90  # +90調整為向上為0度
        else:
            # 預設向上射擊
            base_angle = 0

        # 準備射擊資料（應用角色攻擊力倍率）
        attack_power_multiplier = self.character_config["attributes"]["attack_power"]
        base_damage = weapon_config["damage"] * attack_power_multiplier

        shot_data = {
            "damage": base_damage,
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
                angle = base_angle
            else:
                # 多發子彈，計算散布角度
                angle_step = spread_angle / (bullet_count - 1)
                angle = base_angle - spread_angle / 2 + i * angle_step

            bullet_info = {
                "x": self.x + self.width / 2,
                "y": self.y,
                "angle": angle,
                "damage": base_damage * damage_multiplier,
                "speed": weapon_config["bullet_speed"],
            }
            shot_data["bullets"].append(bullet_info)

        return shot_data

    def use_skill(self, enemies_list=None):
        """
        使用角色專屬技能 - 自動追蹤所有AI敵人\n
        \n
        不同角色的技能效果：\n
        - 貓：雷射技能 - 高精準度追蹤攻擊所有敵人\n
        - 狗：火焰技能 - 持續燃燒追蹤攻擊所有敵人\n
        - 狼：冰凍技能 - 減緩所有敵人並造成追蹤傷害\n
        \n
        技能統一設定：\n
        - 冷卻時間：10秒\n
        - 生命值消耗：10%當前最大生命值\n
        - 自動追蹤所有活著的敵人\n
        - 發射多個追蹤子彈攻擊所有目標\n
        - 技能效果持續3秒\n
        \n
        參數:\n
        enemies_list (list): 可追蹤的敵人列表\n
        \n
        回傳:\n
        dict: 技能使用結果，包含是否成功和技能資訊\n
        """
        current_time = pygame.time.get_ticks()
        skill_config = self.character_config["skill"]

        # 檢查技能冷卻時間
        if current_time - self.last_skill_time < skill_config["cooldown"]:
            remaining_time = (
                skill_config["cooldown"] - (current_time - self.last_skill_time)
            ) / 1000
            return {"success": False, "reason": f"技能冷卻中 ({remaining_time:.1f}秒)"}

        # 檢查生命值是否足夠
        skill_cost = int(self.max_health * (skill_config["health_cost_percent"] / 100))
        if self.health <= skill_cost:
            return {"success": False, "reason": "生命值不足"}

        # 檢查是否有敵人可以攻擊
        alive_enemies = (
            [enemy for enemy in enemies_list if enemy.is_alive] if enemies_list else []
        )
        if not alive_enemies:
            return {"success": False, "reason": "沒有可攻擊的敵人"}

        # 消耗生命值
        self.health -= skill_cost

        # 確保生命值不會為0（至少保留1點）
        if self.health <= 0:
            self.health = 1

        # 記錄技能使用時間
        self.last_skill_time = current_time

        # 播放技能音效
        sound_manager.play_skill_sound()

        # 計算玩家中心點作為發射起點
        start_x = self.x + self.width / 2
        start_y = self.y

        # 創建針對每個敵人的子彈資料列表
        bullets_data = []
        for i, enemy in enumerate(alive_enemies):
            # 計算朝向每個敵人的初始角度
            enemy_center_x = enemy.x + enemy.width / 2
            enemy_center_y = enemy.y + enemy.height / 2

            dx = enemy_center_x - start_x
            dy = enemy_center_y - start_y
            initial_angle = math.degrees(math.atan2(dy, dx)) + 90  # +90調整為向上為0度

            bullet_data = {
                "x": start_x,
                "y": start_y,
                "angle": initial_angle,
                "speed": 200,  # 技能子彈速度
                "damage": skill_config["damage"],
                "skill_type": skill_config["type"],
                "effect_color": skill_config["effect_color"],
                "target_enemy": enemy,  # 指定這個子彈追蹤的特定敵人
                "enemies": alive_enemies,  # 完整敵人列表，用於重新尋找目標
                "lifetime": 3000,  # 3秒生命時間
                "start_time": current_time,
            }
            bullets_data.append(bullet_data)

        # 根據角色類型返回不同的技能效果
        return {
            "success": True,
            "character_type": self.character_type,
            "skill_type": skill_config["type"],
            "skill_name": skill_config["name"],
            "damage": skill_config["damage"],
            "effect_color": skill_config["effect_color"],
            "range": "auto_tracking_all",  # 追蹤所有敵人
            "health_cost": skill_cost,
            "description": skill_config["description"],
            "duration": 3000,  # 3秒持續時間
            "targets_count": len(alive_enemies),
            "bullets_data": bullets_data,  # 多個子彈的資料
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
        elif powerup_type == "health_pack":
            # 立即回復血量
            effect_config = POWERUP_EFFECTS[powerup_type]
            heal_amount = effect_config["heal_amount"]
            self.heal(heal_amount)
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

    def update_skill_effects(self):
        """
        更新技能效果狀態\n
        \n
        檢查技能是否已經結束，並清除過期的技能效果\n
        """
        if self.active_skill:
            current_time = pygame.time.get_ticks()
            skill_elapsed_time = current_time - self.active_skill["start_time"]

            if skill_elapsed_time >= self.active_skill["duration"]:
                # 技能時間結束
                self.active_skill = None

    def is_skill_active(self):
        """
        檢查技能是否正在啟用中\n
        \n
        回傳:\n
        bool: 技能是否正在啟用\n
        """
        return self.active_skill is not None

    def get_active_skill_info(self):
        """
        取得當前啟用技能的資訊\n
        \n
        回傳:\n
        dict: 技能資訊，如果沒有技能啟用則回傳 None\n
        """
        if not self.active_skill:
            return None

        current_time = pygame.time.get_ticks()
        remaining_time = self.active_skill["duration"] - (
            current_time - self.active_skill["start_time"]
        )

        return {
            "type": self.active_skill["type"],
            "effect_color": self.active_skill["effect_color"],
            "remaining_time": max(0, remaining_time) / 1000,  # 轉成秒
            "damage": self.active_skill["damage"],
        }

    def is_enemy_in_skill_range(self, enemy):
        """
        檢查敵人是否在技能攻擊範圍內\n
        \n
        注意：新版技能系統使用自動追蹤子彈，此方法已廢棄\n
        保留用於向後相容性，總是回傳 False\n
        \n
        參數:\n
        enemy: 敵人物件\n
        \n
        回傳:\n
        bool: 總是回傳 False（技能現在通過追蹤子彈實現）\n
        """
        # 技能現在通過追蹤子彈實現，不再使用範圍檢測
        return False

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
            if self.is_alive:  # 只在第一次死亡時播放音效
                sound_manager.play_death_sound()
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
        self.update_skill_effects()

    def draw(self, screen):
        """
        繪製玩家角色\n
        \n
        使用真實角色圖片，並根據角色狀態添加邊框效果：\n
        - 填裝中：黃色邊框\n
        - 技能狀態：紫色邊框\n
        - 生命值低：紅色邊框\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        """
        # 繪製角色圖片
        if self.character_image:
            screen.blit(self.character_image, (self.x, self.y))
        else:
            # 降級顯示：使用幾何形狀
            base_color = self.character_config["color"]
            pygame.draw.rect(
                screen, base_color, (self.x, self.y, self.width, self.height)
            )

        # 根據狀態決定邊框顏色
        border_color = None
        border_width = 2

        if self.active_skill:
            # 技能啟用時顯示技能效果顏色邊框
            border_color = self.active_skill["effect_color"]
            border_width = 3
        elif "skill_boost" in self.powerups:
            border_color = COLORS["purple"]  # 技能狀態用紫色
        elif self.is_reloading:
            border_color = COLORS["yellow"]  # 填裝中用黃色
        elif self.health < self.max_health * 0.3:
            border_color = COLORS["red"]  # 血量低用紅色
        else:
            border_color = COLORS["white"]  # 預設白色邊框

        # 繪製邊框
        if border_color:
            pygame.draw.rect(
                screen,
                border_color,
                (self.x, self.y, self.width, self.height),
                border_width,
            )

        # 在角色上方顯示角色類型標識（簡化的圖示）
        self._draw_character_indicator(screen)

    def _draw_character_indicator(self, screen):
        """
        在角色上方繪製角色類型指示器

        參數:
        screen (pygame.Surface): 遊戲畫面物件
        """
        indicator_size = 8
        indicator_x = self.x + self.width // 2 - indicator_size // 2
        indicator_y = self.y - 15

        # 根據角色類型繪製不同形狀的指示器
        if self.character_type == "cat":
            # 貓 - 橙色圓形（代表敏捷）
            pygame.draw.circle(
                screen,
                self.character_config["color"],
                (indicator_x + indicator_size // 2, indicator_y + indicator_size // 2),
                indicator_size // 2,
            )
        elif self.character_type == "dog":
            # 狗 - 棕色方形（代表忠誠可靠）
            pygame.draw.rect(
                screen,
                self.character_config["color"],
                (indicator_x, indicator_y, indicator_size, indicator_size),
            )
        elif self.character_type == "wolf":
            # 狼 - 灰色三角形（代表野性）
            points = [
                (indicator_x + indicator_size // 2, indicator_y),
                (indicator_x, indicator_y + indicator_size),
                (indicator_x + indicator_size, indicator_y + indicator_size),
            ]
            pygame.draw.polygon(screen, self.character_config["color"], points)

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
        skill_cooldown_duration = self.character_config["skill"]["cooldown"]
        time_since_last_skill = current_time - self.last_skill_time

        if time_since_last_skill < skill_cooldown_duration:
            cooldown_remaining = (
                skill_cooldown_duration - time_since_last_skill
            ) / 1000
            return {
                "ready": False,
                "cooldown_remaining": cooldown_remaining,
                "total_cooldown": skill_cooldown_duration / 1000,
                "skill_name": self.character_config["skill"]["name"],
            }
        else:
            return {
                "ready": True,
                "cooldown_remaining": 0,
                "total_cooldown": skill_cooldown_duration / 1000,
                "skill_name": self.character_config["skill"]["name"],
            }
