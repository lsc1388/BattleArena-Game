######################載入套件######################
import pygame
import math
import random
from src.config import *

######################物件類別######################


class Enemy:
    """
    AI 敵人類別 - 處理電腦對手的行為和戰鬥邏輯\n
    \n
    此類別負責管理：\n
    1. 三種難度等級的AI行為（弱/中/強）\n
    2. 智能移動模式和路徑規劃\n
    3. 瞄準系統和射擊邏輯\n
    4. 生命值和狀態管理\n
    5. 與玩家的戰術互動\n
    \n
    屬性:\n
    x, y (float): 敵人在螢幕上的位置座標\n
    width, height (int): 敵人的尺寸大小\n
    health (int): 當前生命值\n
    max_health (int): 最大生命值（依難度而定）\n
    difficulty (str): AI難度等級（'weak', 'medium', 'strong'）\n
    accuracy (float): 瞄準精確度（0.0-1.0）\n
    fire_rate (int): 射擊頻率（毫秒）\n
    move_pattern (str): 移動模式類型\n
    """

    def __init__(self, x, y, difficulty="medium", enemy_type=None):
        """
        初始化AI敵人\n
        \n
        參數:\n
        x (float): 初始 X 座標位置\n
        y (float): 初始 Y 座標位置\n
        difficulty (str): AI難度等級，可選 'weak', 'medium', 'strong'\n
        enemy_type (str): 敵人類型，可選 'robot', 'alien', 'zombie'，如果為None則根據難度自動選擇\n
        """
        # 位置和尺寸設定
        self.x = x
        self.y = y
        self.width = ENEMY_SIZE
        self.height = ENEMY_SIZE

        # 難度設定
        self.difficulty = difficulty
        self.config = AI_CONFIGS[difficulty]

        # 敵人類型設定
        if enemy_type is None:
            enemy_type = self.config.get("preferred_enemy_type", "robot")
        self.enemy_type = enemy_type
        self.enemy_config = ENEMY_TYPES.get(enemy_type, ENEMY_TYPES["robot"])

        # 生命值設定
        self.max_health = self.config["health"]
        self.health = self.max_health
        self.is_alive = True

        # 移動相關
        self.speed = ENEMY_SPEEDS[difficulty]
        self.velocity_x = 0
        self.velocity_y = 0

        # 戰鬥相關
        self.accuracy = self.config["accuracy"]
        self.fire_rate = self.config["fire_rate"]
        self.last_shot_time = 0

        # AI行為系統
        self.move_pattern = self.config["move_pattern"]
        self.target_x = x
        self.target_y = y
        self.direction_change_time = 0
        self.behavior_timer = 0

        # 特殊能力系統
        self.special_ability = self.enemy_config.get("special_ability")
        self.ability_config = ENEMY_ABILITIES.get(self.special_ability, {})
        self.ability_cooldown = 0
        self.last_ability_time = 0
        
        # 能力相關狀態
        self.shield_active = False
        self.shield_start_time = 0
        self.last_regen_time = 0
        
        # 狀態效果
        self.slow_factor = 1.0
        self.slow_end_time = 0
        self.dot_damage = 0
        self.dot_end_time = 0
        self.last_dot_time = 0

        # 追蹤和瞄準系統
        self.last_known_player_pos = None
        self.prediction_offset = (0, 0)
        self.dodge_direction = random.choice([-1, 1])

        # 狀態機
        self.state = "patrol"  # 可能狀態: patrol, chase, attack, dodge
        self.state_timer = 0

    def update_ai_behavior(self, player, screen_width, screen_height):
        """
        更新AI行為邏輯（每幀呼叫）\n
        \n
        根據難度等級執行不同的AI策略：\n
        - 弱AI：簡單移動和射擊\n
        - 中AI：戰術移動和預測瞄準\n
        - 強AI：高級戰術和技能運用\n
        \n
        參數:\n
        player: 玩家物件\n
        screen_width (int): 螢幕寬度\n
        screen_height (int): 螢幕高度\n
        """
        current_time = pygame.time.get_ticks()

        # 更新狀態計時器
        self.state_timer += 1

        # 計算與玩家的距離和角度
        distance_to_player = self._calculate_distance_to_player(player)
        angle_to_player = self._calculate_angle_to_player(player)

        # 根據難度選擇AI行為
        if self.move_pattern == "simple":
            self._simple_ai_behavior(
                player, distance_to_player, angle_to_player, screen_width, screen_height
            )
        elif self.move_pattern == "tactical":
            self._tactical_ai_behavior(
                player, distance_to_player, angle_to_player, screen_width, screen_height
            )
        elif self.move_pattern == "advanced":
            self._advanced_ai_behavior(
                player, distance_to_player, angle_to_player, screen_width, screen_height
            )

    def _simple_ai_behavior(self, player, distance, angle, screen_width, screen_height):
        """
        簡單AI行為（弱AI）\n
        \n
        特點：\n
        - 基本的追蹤移動\n
        - 較慢的射擊頻率\n
        - 較低的瞄準精度\n
        - 簡單的移動模式\n
        \n
        參數:\n
        player: 玩家物件\n
        distance (float): 與玩家的距離\n
        angle (float): 對玩家的角度\n
        screen_width, screen_height (int): 螢幕尺寸\n
        """
        # 簡單的狀態機：巡邏 -> 發現玩家 -> 攻擊
        if distance > 200:
            # 距離太遠，隨機移動巡邏
            self.state = "patrol"
            self._random_movement(screen_width, screen_height)
        else:
            # 發現玩家，開始攻擊
            self.state = "attack"

            # 緩慢接近玩家（保持一定距離）
            if distance > 150:
                self._move_towards_player(player, 0.5)  # 較慢的接近速度
            elif distance < 100:
                self._move_away_from_player(player, 0.3)  # 簡單後退
            else:
                # 在適當距離，停止移動專心射擊
                self.velocity_x = 0
                self.velocity_y = 0

    def _tactical_ai_behavior(
        self, player, distance, angle, screen_width, screen_height
    ):
        """
        戰術AI行為（中AI）\n
        \n
        特點：\n
        - 戰術移動和繞行\n
        - 預測性瞄準\n
        - 維持最適攻擊距離\n
        - 基本的躲避機制\n
        \n
        參數:\n
        player: 玩家物件\n
        distance (float): 與玩家的距離\n
        angle (float): 對玩家的角度\n
        screen_width, screen_height (int): 螢幕尺寸\n
        """
        optimal_distance = 180  # 最適攻擊距離

        if distance > 300:
            # 主動尋找和接近玩家
            self.state = "chase"
            self._move_towards_player(player, 0.8)
        elif distance < optimal_distance - 30:
            # 太近了，戰術後退
            self.state = "dodge"
            self._tactical_retreat(player, screen_width, screen_height)
        elif distance > optimal_distance + 30:
            # 太遠了，戰術接近
            self.state = "chase"
            self._tactical_approach(player, screen_width, screen_height)
        else:
            # 在最適距離，圍繞玩家移動並射擊
            self.state = "attack"
            self._circle_strafe(player, screen_width, screen_height)

    def _advanced_ai_behavior(
        self, player, distance, angle, screen_width, screen_height
    ):
        """
        高級AI行為（強AI）\n
        \n
        特點：\n
        - 複雜的移動策略\n
        - 高精度預測瞄準\n
        - 動態戰術調整\n
        - 高級躲避技術\n
        \n
        參數:\n
        player: 玩家物件\n
        distance (float): 與玩家的距離\n
        angle (float): 對玩家的角度\n
        screen_width, screen_height (int): 螢幕尺寸\n
        """
        # 複雜的狀態機，考慮更多因素
        player_health_ratio = player.health / player.max_health
        my_health_ratio = self.health / self.max_health

        # 根據雙方血量調整戰術
        if my_health_ratio < 0.3:
            # 血量低時採用保守戰術
            self._defensive_tactics(player, distance, screen_width, screen_height)
        elif player_health_ratio < 0.3:
            # 玩家血量低時採用激進戰術
            self._aggressive_tactics(player, distance, screen_width, screen_height)
        else:
            # 正常情況下的戰術行為
            self._adaptive_tactics(player, distance, angle, screen_width, screen_height)

    def _defensive_tactics(self, player, distance, screen_width, screen_height):
        """血量低時的防守戰術"""
        # 保持遠距離，利用地形掩護
        if distance < 250:
            self._evasive_retreat(player, screen_width, screen_height)
        else:
            self._hit_and_run(player, screen_width, screen_height)

    def _aggressive_tactics(self, player, distance, screen_width, screen_height):
        """玩家血量低時的激進戰術"""
        # 積極進攻，壓制玩家
        if distance > 150:
            self._aggressive_approach(player)
        else:
            self._close_combat(player, screen_width, screen_height)

    def _adaptive_tactics(self, player, distance, angle, screen_width, screen_height):
        """自適應戰術（根據情況調整）"""
        # 分析玩家移動模式並做出反應
        if self.state_timer % 180 == 0:  # 每3秒重新評估戰術
            self._analyze_player_behavior(player)

        # 執行當前戰術
        if distance < 120:
            self._close_range_tactics(player, screen_width, screen_height)
        elif distance < 220:
            self._medium_range_tactics(player, screen_width, screen_height)
        else:
            self._long_range_tactics(player, screen_width, screen_height)

    def _move_towards_player(self, player, speed_factor=1.0):
        """
        朝玩家方向移動\n
        \n
        參數:\n
        player: 玩家物件\n
        speed_factor (float): 速度調整係數\n
        """
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            # 正規化方向向量
            dx /= distance
            dy /= distance

            # 套用速度
            self.velocity_x = dx * self.speed * speed_factor
            self.velocity_y = dy * self.speed * speed_factor

    def _move_away_from_player(self, player, speed_factor=1.0):
        """遠離玩家移動"""
        dx = self.x - player.x
        dy = self.y - player.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            dx /= distance
            dy /= distance

            self.velocity_x = dx * self.speed * speed_factor
            self.velocity_y = dy * self.speed * speed_factor

    def _circle_strafe(self, player, screen_width, screen_height):
        """圍繞玩家移動（繞圈攻擊）"""
        # 計算垂直於玩家方向的移動
        dx = player.x - self.x
        dy = player.y - self.y

        # 計算垂直向量（90度旋轉）
        perpendicular_x = -dy * self.dodge_direction
        perpendicular_y = dx * self.dodge_direction

        distance = math.sqrt(
            perpendicular_x * perpendicular_x + perpendicular_y * perpendicular_y
        )
        if distance > 0:
            perpendicular_x /= distance
            perpendicular_y /= distance

            self.velocity_x = perpendicular_x * self.speed * 0.7
            self.velocity_y = perpendicular_y * self.speed * 0.7

        # 偶爾改變繞行方向
        if self.state_timer % 120 == 0:
            self.dodge_direction *= -1

    def _random_movement(self, screen_width, screen_height):
        """隨機移動模式（巡邏用）"""
        current_time = pygame.time.get_ticks()

        # 每2秒改變一次移動方向
        if current_time - self.direction_change_time > 2000:
            self.target_x = random.randint(50, screen_width - 50)
            self.target_y = random.randint(50, screen_height - 50)
            self.direction_change_time = current_time

        # 朝目標位置移動
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 10:
            dx /= distance
            dy /= distance
            self.velocity_x = dx * self.speed * 0.5
            self.velocity_y = dy * self.speed * 0.5
        else:
            self.velocity_x = 0
            self.velocity_y = 0

    def _calculate_distance_to_player(self, player):
        """計算與玩家的距離"""
        dx = player.x - self.x
        dy = player.y - self.y
        return math.sqrt(dx * dx + dy * dy)

    def _calculate_angle_to_player(self, player):
        """計算對玩家的角度"""
        dx = player.x - self.x
        dy = player.y - self.y
        return math.degrees(math.atan2(dy, dx))

    def can_shoot(self):
        """
        檢查是否可以射擊\n
        \n
        回傳:\n
        bool: 是否可以射擊\n
        """
        current_time = pygame.time.get_ticks()
        return current_time - self.last_shot_time >= self.fire_rate

    def calculate_shot_angle(self, player):
        """
        計算射擊角度（包含預測性瞄準）\n
        \n
        根據AI難度調整瞄準精確度和預測能力\n
        考慮特殊能力對精確度的影響\n
        \n
        參數:\n
        player: 玩家物件\n
        \n
        回傳:\n
        float: 射擊角度（度數）\n
        """
        # 基本角度計算
        base_dx = player.x + player.width / 2 - (self.x + self.width / 2)
        base_dy = player.y + player.height / 2 - (self.y + self.height / 2)

        # 預測性瞄準（根據玩家移動速度）
        if self.move_pattern in ["tactical", "advanced"]:
            # 計算玩家移動預測
            prediction_time = 0.5  # 預測0.5秒後的位置
            predicted_x = (
                base_dx + player.velocity_x * prediction_time * 60
            )  # 60fps假設
            predicted_y = base_dy + player.velocity_y * prediction_time * 60

            base_dx = predicted_x
            base_dy = predicted_y

        # 計算角度
        angle = math.degrees(math.atan2(base_dy, base_dx)) + 90  # +90調整為向上為0度

        # 基礎精確度
        accuracy = self.accuracy
        
        # 特殊能力加成
        if self.special_ability == "precision_shooting":
            accuracy += self.ability_config.get("accuracy_bonus", 0.2)
            accuracy = min(1.0, accuracy)  # 確保不超過100%

        # 根據精確度添加隨機誤差
        accuracy_error = (1.0 - accuracy) * 30  # 最大30度誤差
        angle += random.uniform(-accuracy_error, accuracy_error)

        return angle

    def shoot(self, player):
        """
        執行射擊動作\n
        \n
        參數:\n
        player: 玩家物件（用於瞄準）\n
        \n
        回傳:\n
        dict: 射擊資訊，如果不能射擊則回傳 None\n
        """
        if not self.can_shoot():
            return None

        # 記錄射擊時間
        self.last_shot_time = pygame.time.get_ticks()

        # 計算射擊角度
        angle = self.calculate_shot_angle(player)

        # 準備射擊資料
        shot_data = {
            "x": self.x + self.width / 2,
            "y": self.y + self.height / 2,
            "angle": angle,
            "speed": BULLET_SPEED,
            "damage": BULLET_DAMAGE,
            "owner": "enemy",
        }

        return shot_data

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
        # 檢查能量護盾
        if (self.special_ability == "energy_shield" and self.shield_active):
            damage_reduction = self.ability_config.get("damage_reduction", 0.3)
            damage = int(damage * (1.0 - damage_reduction))
        
        self.health -= damage

        # 確保生命值不會低於0
        if self.health <= 0:
            self.health = 0
            self.is_alive = False

        # 受傷時可能改變行為模式
        if self.health < self.max_health * 0.5:
            # 血量低於50%時變得更加謹慎
            if self.move_pattern == "simple":
                self.move_pattern = "tactical"  # 升級AI行為

        return self.is_alive

    def update(self, player, screen_width, screen_height):
        """
        更新敵人狀態（每幀呼叫）\n
        \n
        參數:\n
        player: 玩家物件\n
        screen_width (int): 螢幕寬度\n
        screen_height (int): 螢幕高度\n
        """
        if not self.is_alive:
            return

        # 更新特殊能力
        self._update_special_abilities()

        # 更新AI行為
        self.update_ai_behavior(player, screen_width, screen_height)

        # 更新位置（考慮減速效果）
        effective_velocity_x = self.velocity_x * self.slow_factor
        effective_velocity_y = self.velocity_y * self.slow_factor
        
        self.x += effective_velocity_x
        self.y += effective_velocity_y

        # 邊界檢查
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > screen_width:
            self.x = screen_width - self.width

        if self.y < 0:
            self.y = 0
        elif self.y + self.height > screen_height:
            self.y = screen_height - self.height

    def _update_special_abilities(self):
        """
        更新敵人特殊能力\n
        """
        current_time = pygame.time.get_ticks()
        
        # 更新狀態效果
        self._update_status_effects(current_time)
        
        if self.special_ability == "energy_shield":
            # 能量護盾邏輯
            shield_cooldown = self.ability_config.get("cooldown", 10000)
            shield_duration = self.ability_config.get("shield_duration", 3000)
            
            # 檢查是否應該啟動護盾
            if (not self.shield_active and 
                current_time - self.last_ability_time >= shield_cooldown):
                self.shield_active = True
                self.shield_start_time = current_time
                self.last_ability_time = current_time
            
            # 檢查護盾是否應該結束
            if (self.shield_active and 
                current_time - self.shield_start_time >= shield_duration):
                self.shield_active = False
                
        elif self.special_ability == "regeneration":
            # 生命再生邏輯
            heal_interval = self.ability_config.get("heal_interval", 1000)
            heal_rate = self.ability_config.get("heal_rate", 2)
            max_heal_percent = self.ability_config.get("max_heal_percent", 0.5)
            
            if (current_time - self.last_regen_time >= heal_interval and
                self.health < self.max_health * max_heal_percent):
                self.health = min(self.health + heal_rate, 
                                int(self.max_health * max_heal_percent))
                self.last_regen_time = current_time

    def _update_status_effects(self, current_time):
        """
        更新狀態效果（減速、持續傷害等）\n
        
        參數:\n
        current_time (int): 當前時間\n
        """
        # 更新減速效果
        if current_time > self.slow_end_time:
            self.slow_factor = 1.0
        
        # 更新持續傷害
        if current_time < self.dot_end_time:
            if current_time - self.last_dot_time >= 1000:  # 每秒造成傷害
                self.take_damage(self.dot_damage)
                self.last_dot_time = current_time
        else:
            self.dot_damage = 0

    def apply_slow_effect(self, slow_factor, duration):
        """
        應用減速效果\n
        
        參數:\n
        slow_factor (float): 減速係數（0.5表示減速50%）\n
        duration (int): 持續時間（毫秒）\n
        """
        current_time = pygame.time.get_ticks()
        self.slow_factor = slow_factor
        self.slow_end_time = current_time + duration

    def apply_dot_effect(self, damage_per_second, duration):
        """
        應用持續傷害效果\n
        
        參數:\n
        damage_per_second (int): 每秒傷害\n
        duration (int): 持續時間（毫秒）\n
        """
        current_time = pygame.time.get_ticks()
        self.dot_damage = damage_per_second
        self.dot_end_time = current_time + duration
        self.last_dot_time = current_time

    def draw(self, screen):
        """
        繪製敵人\n
        \n
        根據敵人類型和狀態顯示不同顏色：\n
        - 基本顏色：根據敵人類型\n
        - 護盾效果：藍色光暈\n
        - 受傷狀態：顏色變暗\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        """
        if not self.is_alive:
            return

        # 根據敵人類型決定基本顏色
        base_color = self.enemy_config["color"]

        # 根據血量調整顏色深度
        health_ratio = self.health / self.max_health
        if health_ratio < 0.5:
            # 血量低時顏色變暗
            base_color = tuple(int(c * 0.7) for c in base_color)

        # 畫敵人方塊
        pygame.draw.rect(screen, base_color, (self.x, self.y, self.width, self.height))

        # 特殊效果繪製
        if self.special_ability == "energy_shield" and self.shield_active:
            # 繪製護盾效果（藍色邊框）
            shield_color = (0, 100, 255)
            pygame.draw.rect(
                screen, shield_color, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 3
            )

        # 狀態效果指示
        if self.slow_factor < 1.0:
            # 減速效果（藍色光暈）
            slow_color = (0, 191, 255)
            pygame.draw.rect(
                screen, slow_color, (self.x - 1, self.y - 1, self.width + 2, self.height + 2), 2
            )
            
        if self.dot_damage > 0:
            # 持續傷害效果（紅色光暈）
            dot_color = (255, 0, 0)
            pygame.draw.rect(
                screen, dot_color, (self.x - 1, self.y - 1, self.width + 2, self.height + 2), 1
            )

        # 畫邊框
        pygame.draw.rect(
            screen, COLORS["white"], (self.x, self.y, self.width, self.height), 2
        )

        # 顯示敵人類型指示器（角落小圓點）
        indicator_size = 4
        indicator_color = COLORS["white"]
        
        if self.enemy_type == "robot":
            indicator_color = (128, 128, 128)  # 灰色
        elif self.enemy_type == "alien":
            indicator_color = (0, 255, 0)     # 綠色
        elif self.enemy_type == "zombie":
            indicator_color = (139, 69, 19)   # 棕色

        pygame.draw.circle(
            screen,
            indicator_color,
            (int(self.x + self.width - 6), int(self.y + 6)),
            indicator_size,
        )

    def get_rect(self):
        """
        取得碰撞檢測用的矩形\n
        \n
        回傳:\n
        pygame.Rect: 碰撞檢測矩形\n
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def get_info(self):
        """
        取得敵人狀態資訊\n
        \n
        回傳:\n
        dict: 敵人狀態資訊\n
        """
        return {
            "difficulty": self.difficulty,
            "enemy_type": self.enemy_type,
            "enemy_name": self.enemy_config["name"],
            "health": self.health,
            "max_health": self.max_health,
            "accuracy": self.accuracy,
            "state": self.state,
            "position": (self.x, self.y),
            "special_ability": self.special_ability,
            "shield_active": getattr(self, "shield_active", False),
        }

    # 額外的高級AI方法
    def _tactical_retreat(self, player, screen_width, screen_height):
        """戰術撤退"""
        # 計算最佳撤退方向（考慮地圖邊界）
        retreat_directions = []

        # 檢查各個方向的可行性
        directions = [
            (-1, -1),
            (0, -1),
            (1, -1),
            (-1, 0),
            (1, 0),
            (-1, 1),
            (0, 1),
            (1, 1),
        ]

        for dx, dy in directions:
            new_x = self.x + dx * self.speed * 2
            new_y = self.y + dy * self.speed * 2

            if (
                0 <= new_x <= screen_width - self.width
                and 0 <= new_y <= screen_height - self.height
            ):
                # 計算這個方向是否遠離玩家
                distance_to_player = math.sqrt(
                    (new_x - player.x) ** 2 + (new_y - player.y) ** 2
                )
                current_distance = math.sqrt(
                    (self.x - player.x) ** 2 + (self.y - player.y) ** 2
                )

                if distance_to_player > current_distance:
                    retreat_directions.append((dx, dy, distance_to_player))

        if retreat_directions:
            # 選擇最遠的方向
            best_direction = max(retreat_directions, key=lambda x: x[2])
            self.velocity_x = best_direction[0] * self.speed
            self.velocity_y = best_direction[1] * self.speed

    def _tactical_approach(self, player, screen_width, screen_height):
        """戰術接近"""
        # 不直接衝向玩家，而是採用曲折路線
        angle_to_player = self._calculate_angle_to_player(player)

        # 添加隨機偏移角度
        offset_angle = random.uniform(-45, 45)
        approach_angle = math.radians(angle_to_player + offset_angle)

        self.velocity_x = math.cos(approach_angle) * self.speed * 0.8
        self.velocity_y = math.sin(approach_angle) * self.speed * 0.8

    def _analyze_player_behavior(self, player):
        """分析玩家行為模式"""
        # 記錄玩家位置變化，分析移動模式
        if self.last_known_player_pos:
            dx = player.x - self.last_known_player_pos[0]
            dy = player.y - self.last_known_player_pos[1]

            # 根據玩家移動模式調整自己的戰術
            if abs(dx) > abs(dy):
                # 玩家偏好水平移動
                self.prediction_offset = (dx * 2, 0)
            else:
                # 玩家偏好垂直移動
                self.prediction_offset = (0, dy * 2)

    def _evasive_retreat(self, player, screen_width, screen_height):
        """血量低時的規避撤退"""
        # 計算最安全的撤退路線（遠離玩家且靠近邊界）
        retreat_directions = []

        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            new_x = self.x + math.cos(rad) * self.speed * 3
            new_y = self.y + math.sin(rad) * self.speed * 3

            if (
                0 <= new_x <= screen_width - self.width
                and 0 <= new_y <= screen_height - self.height
            ):
                distance_from_player = math.sqrt(
                    (new_x - player.x) ** 2 + (new_y - player.y) ** 2
                )
                retreat_directions.append(
                    (math.cos(rad), math.sin(rad), distance_from_player)
                )

        if retreat_directions:
            best_retreat = max(retreat_directions, key=lambda x: x[2])
            self.velocity_x = best_retreat[0] * self.speed
            self.velocity_y = best_retreat[1] * self.speed

    def _hit_and_run(self, player, screen_width, screen_height):
        """遊擊戰術"""
        # 快速接近射擊後立即撤退
        if self.state_timer % 120 < 60:  # 前半段接近
            self._move_towards_player(player, 0.8)
        else:  # 後半段撤退
            self._move_away_from_player(player, 1.0)

    def _aggressive_approach(self, player):
        """激進接近"""
        # 直線衝向玩家
        self._move_towards_player(player, 1.2)

    def _close_combat(self, player, screen_width, screen_height):
        """近距離戰鬥"""
        # 在玩家附近快速移動
        if self.state_timer % 60 < 30:
            self._circle_strafe(player, screen_width, screen_height)
        else:
            self._move_towards_player(player, 0.5)

    def _close_range_tactics(self, player, screen_width, screen_height):
        """近距離戰術"""
        # 使用圍繞攻擊
        self._circle_strafe(player, screen_width, screen_height)

    def _medium_range_tactics(self, player, screen_width, screen_height):
        """中距離戰術"""
        # 保持距離的側向移動
        angle_to_player = self._calculate_angle_to_player(player)
        perpendicular_angle = math.radians(angle_to_player + 90)

        self.velocity_x = math.cos(perpendicular_angle) * self.speed * 0.6
        self.velocity_y = math.sin(perpendicular_angle) * self.speed * 0.6

    def _long_range_tactics(self, player, screen_width, screen_height):
        """遠距離戰術"""
        # 緩慢接近同時保持射擊
        self._move_towards_player(player, 0.3)
