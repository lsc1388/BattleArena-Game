######################載入套件######################
import pygame
import random
import math
from src.config import *

######################物件類別######################


class PowerUp:
    """
    驚喜包類別 - 處理隨機掉落的強化道具\n
    \n
    此類別負責管理：\n
    1. 三種強化效果的道具生成\n
    2. 道具的視覺效果和動畫\n
    3. 玩家拾取檢測\n
    4. 道具生命週期管理\n
    \n
    屬性:\n
    x, y (float): 道具在螢幕上的位置座標\n
    size (int): 道具的大小\n
    powerup_type (str): 強化類型（'fire_boost', 'ammo_refill', 'scatter_shot'）\n
    is_active (bool): 道具是否仍然可拾取\n
    spawn_time (int): 道具生成時間\n
    lifetime (int): 道具存在時間（毫秒）\n
    """

    def __init__(self, x, y, powerup_type=None):
        """
        初始化驚喜包道具\n
        \n
        參數:\n
        x (float): 初始 X 座標位置\n
        y (float): 初始 Y 座標位置\n
        powerup_type (str): 強化類型，如果為 None 則隨機選擇\n
        """
        # 位置和尺寸設定
        self.x = x
        self.y = y
        self.size = POWERUP_SIZE

        # 道具類型設定
        if powerup_type is None:
            # 隨機選擇一種強化類型
            self.powerup_type = random.choice(list(POWERUP_EFFECTS.keys()))
        else:
            self.powerup_type = powerup_type

        # 狀態管理
        self.is_active = True
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 15000  # 15秒後消失

        # 視覺效果
        self.pulse_timer = 0
        self.float_offset = 0
        self.rotation_angle = 0

    def update(self):
        """
        更新道具狀態（每幀呼叫）\n
        \n
        處理：\n
        1. 生命週期檢查\n
        2. 視覺動畫更新\n
        3. 閃爍效果（即將消失時）\n
        \n
        回傳:\n
        bool: 道具是否仍然有效\n
        """
        if not self.is_active:
            return False

        current_time = pygame.time.get_ticks()

        # 檢查是否超過生命週期
        if current_time - self.spawn_time > self.lifetime:
            self.is_active = False
            return False

        # 更新視覺動畫
        self.pulse_timer += 1
        self.float_offset = math.sin(self.pulse_timer * 0.1) * 2  # 上下浮動效果
        self.rotation_angle += 2  # 旋轉效果

        return True

    def check_pickup(self, player):
        """
        檢查玩家是否拾取道具\n
        \n
        參數:\n
        player: 玩家物件\n
        \n
        回傳:\n
        bool: 是否被拾取\n
        """
        if not self.is_active:
            return False

        # 建立道具的碰撞矩形
        powerup_rect = pygame.Rect(self.x, self.y, self.size, self.size)

        # 取得玩家的碰撞矩形
        player_rect = player.get_rect()

        # 檢查碰撞
        if powerup_rect.colliderect(player_rect):
            self.is_active = False
            return True

        return False

    def apply_effect(self, player):
        """
        將強化效果套用到玩家身上\n
        \n
        參數:\n
        player: 玩家物件\n
        \n
        回傳:\n
        str: 效果描述文字\n
        """
        player.apply_powerup(self.powerup_type)

        # 回傳效果描述
        effect_config = POWERUP_EFFECTS[self.powerup_type]
        return f"獲得 {effect_config['name']}!"

    def draw(self, screen):
        """
        繪製道具\n
        \n
        根據道具類型顯示不同顏色和特效：\n
        - 火力增強：紅色，有火焰效果\n
        - 彈藥補給：藍色，有光環效果\n
        - 散彈模式：紫色，有爆炸效果\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        """
        if not self.is_active:
            return

        # 檢查是否即將消失（閃爍效果）
        current_time = pygame.time.get_ticks()
        time_left = self.lifetime - (current_time - self.spawn_time)

        # 最後3秒開始閃爍
        if time_left < 3000:
            if (self.pulse_timer // 15) % 2 == 0:  # 閃爍頻率
                return  # 跳過繪製達到閃爍效果

        # 計算繪製位置（加上浮動效果）
        draw_x = self.x
        draw_y = self.y + self.float_offset

        # 根據道具類型選擇顏色和效果
        if self.powerup_type == "fire_boost":
            # 火力增強：紅色系
            main_color = COLORS["red"]
            effect_color = COLORS["orange"]
            self._draw_fire_effect(screen, draw_x, draw_y, main_color, effect_color)

        elif self.powerup_type == "ammo_refill":
            # 彈藥補給：藍色系
            main_color = COLORS["blue"]
            effect_color = COLORS["white"]
            self._draw_ammo_effect(screen, draw_x, draw_y, main_color, effect_color)

        elif self.powerup_type == "scatter_shot":
            # 散彈模式：紫色系
            main_color = COLORS["purple"]
            effect_color = COLORS["yellow"]
            self._draw_scatter_effect(screen, draw_x, draw_y, main_color, effect_color)

        elif self.powerup_type == "machinegun_powerup":
            # 機關槍：深紅色系
            main_color = (150, 0, 0)  # 深紅色
            effect_color = COLORS["red"]
            self._draw_weapon_effect(screen, draw_x, draw_y, main_color, effect_color)

        elif self.powerup_type == "submachinegun_powerup":
            # 衝鋒槍：深藍色系
            main_color = (0, 0, 150)  # 深藍色
            effect_color = COLORS["blue"]
            self._draw_weapon_effect(screen, draw_x, draw_y, main_color, effect_color)

        # 繪製主體方塊
        pygame.draw.rect(screen, main_color, (draw_x, draw_y, self.size, self.size))

        # 繪製邊框
        pygame.draw.rect(
            screen, COLORS["white"], (draw_x, draw_y, self.size, self.size), 2
        )

    def _draw_fire_effect(self, screen, x, y, main_color, effect_color):
        """繪製火力增強的火焰效果"""
        # 繪製火焰粒子效果
        for i in range(3):
            particle_x = x + random.randint(-3, self.size + 3)
            particle_y = y + random.randint(-3, 5)
            particle_size = random.randint(2, 4)

            pygame.draw.circle(
                screen, effect_color, (int(particle_x), int(particle_y)), particle_size
            )

    def _draw_ammo_effect(self, screen, x, y, main_color, effect_color):
        """繪製彈藥補給的光環效果"""
        # 繪製光環
        ring_radius = self.size // 2 + int(abs(math.sin(self.pulse_timer * 0.1)) * 5)
        center_x = int(x + self.size // 2)
        center_y = int(y + self.size // 2)

        pygame.draw.circle(screen, effect_color, (center_x, center_y), ring_radius, 2)

    def _draw_scatter_effect(self, screen, x, y, main_color, effect_color):
        """繪製散彈模式的爆炸效果"""
        # 繪製散射線條
        center_x = x + self.size // 2
        center_y = y + self.size // 2

        for i in range(8):
            angle = i * 45 + self.rotation_angle
            end_x = center_x + math.cos(math.radians(angle)) * 15
            end_y = center_y + math.sin(math.radians(angle)) * 15

            pygame.draw.line(
                screen, effect_color, (center_x, center_y), (int(end_x), int(end_y)), 2
            )

    def _draw_weapon_effect(self, screen, x, y, main_color, effect_color):
        """繪製武器道具的特殊效果"""
        # 繪製武器圖標效果
        center_x = int(x + self.size // 2)
        center_y = int(y + self.size // 2)

        # 繪製武器形狀（簡單的矩形代表槍械）
        weapon_width = self.size // 3
        weapon_height = self.size // 6
        weapon_x = center_x - weapon_width // 2
        weapon_y = center_y - weapon_height // 2

        pygame.draw.rect(
            screen, effect_color, (weapon_x, weapon_y, weapon_width, weapon_height)
        )

        # 繪製發光效果
        glow_radius = self.size // 2 + int(abs(math.sin(self.pulse_timer * 0.15)) * 8)
        pygame.draw.circle(screen, effect_color, (center_x, center_y), glow_radius, 1)

    def get_rect(self):
        """
        取得碰撞檢測用的矩形\n
        \n
        回傳:\n
        pygame.Rect: 碰撞檢測矩形\n
        """
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def get_info(self):
        """
        取得道具資訊\n
        \n
        回傳:\n
        dict: 道具狀態資訊\n
        """
        current_time = pygame.time.get_ticks()
        time_left = self.lifetime - (current_time - self.spawn_time)

        return {
            "type": self.powerup_type,
            "name": POWERUP_EFFECTS[self.powerup_type]["name"],
            "position": (self.x, self.y),
            "time_left": max(0, time_left / 1000),  # 轉成秒
            "is_active": self.is_active,
        }


######################驚喜包管理系統######################


class PowerUpManager:
    """
    驚喜包管理系統 - 統一管理所有道具的生成和更新\n
    \n
    此系統負責：\n
    1. 隨機生成道具\n
    2. 批量更新所有道具狀態\n
    3. 處理玩家拾取邏輯\n
    4. 自動清理過期道具\n
    5. 控制道具生成頻率\n
    """

    def __init__(self):
        """
        初始化驚喜包管理系統\n
        """
        self.powerups = []
        self.last_spawn_time = 0
        self.spawn_cooldown = 5000  # 5秒最少間隔
        self.max_powerups = 3  # 場上最多3個道具

    def update(self, screen_width, screen_height):
        """
        更新所有道具狀態並隨機生成新道具\n
        \n
        參數:\n
        screen_width (int): 螢幕寬度\n
        screen_height (int): 螢幕高度\n
        """
        # 更新現有道具
        active_powerups = []
        for powerup in self.powerups:
            if powerup.update():
                active_powerups.append(powerup)

        self.powerups = active_powerups

        # 嘗試生成新道具
        self._try_spawn_powerup(screen_width, screen_height)

    def _try_spawn_powerup(self, screen_width, screen_height):
        """
        嘗試生成新的驚喜包\n
        \n
        考慮因素：\n
        - 生成冷卻時間\n
        - 場上道具數量限制\n
        - 隨機機率\n
        \n
        參數:\n
        screen_width (int): 螢幕寬度\n
        screen_height (int): 螢幕高度\n
        """
        current_time = pygame.time.get_ticks()

        # 檢查冷卻時間
        if current_time - self.last_spawn_time < self.spawn_cooldown:
            return

        # 檢查場上道具數量
        if len(self.powerups) >= self.max_powerups:
            return

        # 隨機生成檢查
        if random.random() < POWERUP_SPAWN_CHANCE:
            self._spawn_random_powerup(screen_width, screen_height)
            self.last_spawn_time = current_time

    def _spawn_random_powerup(self, screen_width, screen_height):
        """
        在隨機位置生成隨機道具\n
        \n
        確保生成位置不會太靠近邊界\n
        \n
        參數:\n
        screen_width (int): 螢幕寬度\n
        screen_height (int): 螢幕高度\n
        """
        # 計算安全生成區域
        margin = 50
        safe_x = random.randint(margin, screen_width - margin - POWERUP_SIZE)
        safe_y = random.randint(margin, screen_height - margin - POWERUP_SIZE)

        # 創建新道具
        powerup = PowerUp(safe_x, safe_y)
        self.powerups.append(powerup)

    def spawn_powerup_at_position(self, x, y, powerup_type=None):
        """
        在指定位置生成道具\n
        \n
        參數:\n
        x (float): 生成 X 座標\n
        y (float): 生成 Y 座標\n
        powerup_type (str): 道具類型，None 為隨機\n
        \n
        回傳:\n
        PowerUp: 生成的道具物件\n
        """
        powerup = PowerUp(x, y, powerup_type)
        self.powerups.append(powerup)
        return powerup

    def check_player_pickups(self, player):
        """
        檢查玩家拾取道具\n
        \n
        參數:\n
        player: 玩家物件\n
        \n
        回傳:\n
        list: 被拾取的道具列表，包含效果描述\n
        """
        picked_up = []

        for powerup in self.powerups[:]:  # 使用切片避免在迴圈中修改列表
            if powerup.check_pickup(player):
                effect_message = powerup.apply_effect(player)
                picked_up.append(
                    {
                        "type": powerup.powerup_type,
                        "message": effect_message,
                        "powerup": powerup,
                    }
                )

        # 移除被拾取的道具
        self.powerups = [p for p in self.powerups if p.is_active]

        return picked_up

    def spawn_powerup_on_enemy_death(self, enemy_x, enemy_y):
        """
        敵人死亡時有機率掉落道具\n
        \n
        參數:\n
        enemy_x (float): 敵人死亡位置 X 座標\n
        enemy_y (float): 敵人死亡位置 Y 座標\n
        \n
        回傳:\n
        PowerUp: 掉落的道具物件，如果沒有掉落則為 None\n
        """
        # 30% 機率掉落道具
        if random.random() < 0.3:
            return self.spawn_powerup_at_position(enemy_x, enemy_y)
        return None

    def draw(self, screen):
        """
        繪製所有道具\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        """
        for powerup in self.powerups:
            powerup.draw(screen)

    def get_powerup_count(self):
        """
        取得當前道具數量\n
        \n
        回傳:\n
        int: 場上道具總數\n
        """
        return len(self.powerups)

    def clear_all_powerups(self):
        """
        清除所有道具\n
        \n
        用於遊戲重置或場景切換時\n
        """
        self.powerups.clear()

    def get_powerups_by_type(self, powerup_type):
        """
        取得指定類型的道具列表\n
        \n
        參數:\n
        powerup_type (str): 道具類型\n
        \n
        回傳:\n
        list: 符合類型的道具列表\n
        """
        return [p for p in self.powerups if p.powerup_type == powerup_type]

    def get_nearest_powerup(self, x, y):
        """
        取得最接近指定位置的道具\n
        \n
        參數:\n
        x (float): 參考位置 X 座標\n
        y (float): 參考位置 Y 座標\n
        \n
        回傳:\n
        tuple: (道具物件, 距離) 或 (None, float('inf'))\n
        """
        if not self.powerups:
            return None, float("inf")

        nearest_powerup = None
        min_distance = float("inf")

        for powerup in self.powerups:
            distance = math.sqrt((powerup.x - x) ** 2 + (powerup.y - y) ** 2)
            if distance < min_distance:
                min_distance = distance
                nearest_powerup = powerup

        return nearest_powerup, min_distance

    def set_spawn_rate(self, spawn_chance):
        """
        調整道具生成機率\n
        \n
        參數:\n
        spawn_chance (float): 新的生成機率（0.0-1.0）\n
        """
        # 更新全域設定（這樣設計不太好，但為了簡化）
        global POWERUP_SPAWN_CHANCE
        POWERUP_SPAWN_CHANCE = max(0.0, min(1.0, spawn_chance))

    def get_stats(self):
        """
        取得道具統計資訊\n
        \n
        回傳:\n
        dict: 統計資訊，包含各類型道具數量\n
        """
        stats = {
            "total": len(self.powerups),
            "fire_boost": 0,
            "ammo_refill": 0,
            "scatter_shot": 0,
            "machinegun_powerup": 0,
            "submachinegun_powerup": 0,
        }

        for powerup in self.powerups:
            if powerup.powerup_type in stats:
                stats[powerup.powerup_type] += 1

        return stats
