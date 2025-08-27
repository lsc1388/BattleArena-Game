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

    def __init__(self, x, y, difficulty="medium", enemy_type="robot"):
        """
        初始化AI敵人\n
        \n
        參數:\n
        x (float): 初始 X 座標位置\n
        y (float): 初始 Y 座標位置\n
        difficulty (str): AI難度等級，可選 'weak', 'medium', 'strong'\n
        enemy_type (str): 敵人類型，可選 'robot', 'alien', 'zombie'\n
        """
        # 位置和尺寸設定
        self.x = x
        self.y = y
        self.width = ENEMY_SIZE
        self.height = ENEMY_SIZE

        # 敵人類型設定
        self.enemy_type = enemy_type
        self.type_config = AI_ENEMY_TYPES[enemy_type]

        # 難度設定
        self.difficulty = difficulty
        self.config = AI_CONFIGS[difficulty]

        # 生命值設定（結合類型修飾符）
        base_health = self.config["health"]
        self.max_health = int(base_health * self.type_config["health_modifier"])
        self.health = self.max_health
        self.is_alive = True

        # 移動相關（結合類型修飾符）
        base_speed = ENEMY_SPEEDS[difficulty]
        self.speed = base_speed * self.type_config["speed_modifier"]
        self.velocity_x = 0
        self.velocity_y = 0

        # 戰鬥相關（結合類型修飾符）
        base_accuracy = self.config["accuracy"]
        self.accuracy = base_accuracy * self.type_config["accuracy_modifier"]
        self.fire_rate = self.config["fire_rate"]
        self.last_shot_time = 0

        # AI行為系統
        self.move_pattern = self.config["move_pattern"]
        self.target_x = x
        self.target_y = y
        self.direction_change_time = 0
        self.behavior_timer = 0

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

        # 根據精確度添加隨機誤差
        accuracy_error = (1.0 - self.accuracy) * 30  # 最大30度誤差
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

        # 更新AI行為
        self.update_ai_behavior(player, screen_width, screen_height)

        # 更新位置
        self.x += self.velocity_x
        self.y += self.velocity_y

        # 邊界檢查
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > screen_width:
            self.x = screen_width - self.width

        if self.y < 0:
            self.y = 0
        elif self.y + self.height > screen_height:
            self.y = screen_height - self.height

    def draw(self, screen):
        """
        繪製敵人\n
        \n
        根據敵人類型和狀態顯示不同顏色和形狀：\n
        - 機器人：金屬灰色，方形\n
        - 外星人：綠色，圓形\n
        - 殭屍：深綠色，不規則形狀\n
        - 受傷狀態：顏色變暗\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        """
        if not self.is_alive:
            return

        # 根據敵人類型決定基本顏色
        base_color = self.type_config["color"]

        # 根據血量調整顏色深度
        health_ratio = self.health / self.max_health
        if health_ratio < 0.5:
            # 血量低時顏色變暗
            base_color = tuple(int(c * 0.7) for c in base_color)

        # 根據敵人類型繪製不同形狀
        if self.enemy_type == "robot":
            # 機器人 - 方形
            pygame.draw.rect(
                screen, base_color, (self.x, self.y, self.width, self.height)
            )
            pygame.draw.rect(
                screen, COLORS["white"], (self.x, self.y, self.width, self.height), 2
            )

            # 機器人特有的天線
            antenna_x = self.x + self.width // 2
            antenna_y = self.y - 5
            pygame.draw.line(
                screen,
                COLORS["white"],
                (antenna_x, antenna_y),
                (antenna_x, antenna_y - 8),
                2,
            )
            pygame.draw.circle(screen, COLORS["yellow"], (antenna_x, antenna_y - 8), 3)

        elif self.enemy_type == "alien":
            # 外星人 - 圓形
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            radius = self.width // 2
            pygame.draw.circle(screen, base_color, (center_x, center_y), radius)
            pygame.draw.circle(screen, COLORS["white"], (center_x, center_y), radius, 2)

            # 外星人特有的眼睛
            eye_size = 4
            eye1_x, eye1_y = center_x - 8, center_y - 5
            eye2_x, eye2_y = center_x + 8, center_y - 5
            pygame.draw.circle(screen, COLORS["black"], (eye1_x, eye1_y), eye_size)
            pygame.draw.circle(screen, COLORS["black"], (eye2_x, eye2_y), eye_size)

        elif self.enemy_type == "zombie":
            # 殭屍 - 不規則形狀
            pygame.draw.rect(
                screen, base_color, (self.x, self.y, self.width, self.height)
            )
            pygame.draw.rect(
                screen, COLORS["white"], (self.x, self.y, self.width, self.height), 2
            )

            # 殭屍特有的破損效果（小缺口）
            damage_spots = [
                (self.x + 5, self.y + 5, 6, 6),
                (self.x + self.width - 8, self.y + self.height - 8, 5, 5),
                (self.x + self.width // 2, self.y + 2, 4, 4),
            ]
            for spot in damage_spots:
                pygame.draw.rect(screen, COLORS["black"], spot)

        # 顯示敵人類型指示器（角落標識）
        self._draw_type_indicator(screen)

    def _draw_type_indicator(self, screen):
        """
        繪製敵人類型指示器

        參數:
        screen (pygame.Surface): 遊戲畫面物件
        """
        indicator_size = 6
        indicator_x = self.x + self.width - 10
        indicator_y = self.y + 5

        # 根據敵人類型繪製不同指示器
        if self.enemy_type == "robot":
            # 機器人 - 金屬色方塊
            pygame.draw.rect(
                screen,
                (192, 192, 192),
                (indicator_x, indicator_y, indicator_size, indicator_size),
            )
        elif self.enemy_type == "alien":
            # 外星人 - 綠色圓點
            pygame.draw.circle(
                screen,
                (0, 255, 0),
                (indicator_x + indicator_size // 2, indicator_y + indicator_size // 2),
                indicator_size // 2,
            )
        elif self.enemy_type == "zombie":
            # 殭屍 - 暗綠色三角形
            points = [
                (indicator_x + indicator_size // 2, indicator_y),
                (indicator_x, indicator_y + indicator_size),
                (indicator_x + indicator_size, indicator_y + indicator_size),
            ]
            pygame.draw.polygon(screen, (0, 100, 0), points)

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
            "enemy_type": self.enemy_type,
            "type_name": self.type_config["name"],
            "difficulty": self.difficulty,
            "health": self.health,
            "max_health": self.max_health,
            "accuracy": self.accuracy,
            "state": self.state,
            "position": (self.x, self.y),
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
