######################載入套件######################
import pygame
import math
from src.config import *

######################物件類別######################


class Bullet:
    """
    子彈類別 - 處理子彈的移動、碰撞和生命週期\n
    \n
    此類別負責管理：\n
    1. 子彈的直線移動和角度計算\n
    2. 螢幕邊界檢測和生命週期管理\n
    3. 碰撞檢測支援\n
    4. 不同類型子彈的視覺效果\n
    \n
    屬性:\n
    x, y (float): 子彈在螢幕上的位置座標\n
    velocity_x, velocity_y (float): 子彈的移動速度向量\n
    damage (int): 子彈造成的傷害值\n
    size (int): 子彈的大小（正方形邊長）\n
    owner (str): 發射者類型（'player' 或 'enemy'）\n
    is_active (bool): 子彈是否仍然有效\n
    """

    def __init__(self, x, y, angle, speed, damage, owner="player"):
        """
        初始化子彈物件\n
        \n
        參數:\n
        x (float): 初始 X 座標位置\n
        y (float): 初始 Y 座標位置\n
        angle (float): 發射角度（度數），0 度為向上\n
        speed (float): 子彈移動速度，像素/幀\n
        damage (int): 子彈傷害值，範圍 1-100\n
        owner (str): 發射者類型，'player' 或 'enemy'\n
        """
        # 位置設定
        self.x = x
        self.y = y
        self.size = BULLET_SIZE

        # 傷害和所有者
        self.damage = damage
        self.owner = owner

        # 狀態管理
        self.is_active = True

        # 計算移動速度向量
        # 角度轉換：pygame 的座標系統 Y 軸向下為正
        # 所以 0 度（向上）對應 -90 度的數學角度
        rad_angle = math.radians(angle - 90)
        self.velocity_x = speed * math.cos(rad_angle)
        self.velocity_y = speed * math.sin(rad_angle)

    def update(self, screen_width, screen_height):
        """
        更新子彈位置和狀態（每幀呼叫）\n
        \n
        處理：\n
        1. 根據速度向量更新位置\n
        2. 檢查是否超出螢幕邊界\n
        3. 更新生命週期狀態\n
        \n
        參數:\n
        screen_width (int): 螢幕寬度\n
        screen_height (int): 螢幕高度\n
        \n
        回傳:\n
        bool: 子彈是否仍然有效\n
        """
        if not self.is_active:
            return False

        # 更新位置
        self.x += self.velocity_x
        self.y += self.velocity_y

        # 檢查是否超出螢幕邊界
        if (
            self.x < -self.size
            or self.x > screen_width + self.size
            or self.y < -self.size
            or self.y > screen_height + self.size
        ):
            self.is_active = False

        return self.is_active

    def check_collision(self, target):
        """
        檢查與目標物件的碰撞\n
        \n
        使用矩形碰撞檢測算法\n
        \n
        參數:\n
        target: 目標物件，需要有 get_rect() 方法或 x, y, width, height 屬性\n
        \n
        回傳:\n
        bool: 是否發生碰撞\n
        """
        if not self.is_active:
            return False

        # 建立子彈的碰撞矩形
        bullet_rect = pygame.Rect(self.x, self.y, self.size, self.size)

        # 取得目標的碰撞矩形
        if hasattr(target, "get_rect"):
            target_rect = target.get_rect()
        else:
            target_rect = pygame.Rect(target.x, target.y, target.width, target.height)

        # 檢查矩形重疊
        return bullet_rect.colliderect(target_rect)

    def hit_target(self):
        """
        子彈擊中目標後的處理\n
        \n
        將子彈設為無效狀態，準備從遊戲中移除\n
        """
        self.is_active = False

    def draw(self, screen):
        """
        繪製子彈\n
        \n
        根據發射者類型顯示不同顏色：\n
        - 玩家子彈：黃色\n
        - 敵人子彈：紅色\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        """
        if not self.is_active:
            return

        # 根據發射者決定顏色
        if self.owner == "player":
            color = COLORS["yellow"]  # 玩家子彈用黃色
        else:
            color = COLORS["red"]  # 敵人子彈用紅色

        # 畫子彈方塊
        pygame.draw.rect(screen, color, (self.x, self.y, self.size, self.size))

        # 加個邊框讓子彈更明顯
        border_color = COLORS["white"] if self.owner == "player" else COLORS["black"]
        pygame.draw.rect(
            screen, border_color, (self.x, self.y, self.size, self.size), 1
        )

    def get_rect(self):
        """
        取得碰撞檢測用的矩形\n
        \n
        回傳:\n
        pygame.Rect: 碰撞檢測矩形\n
        """
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def get_center(self):
        """
        取得子彈中心點座標\n
        \n
        回傳:\n
        tuple: (center_x, center_y) 中心點座標\n
        """
        return (self.x + self.size / 2, self.y + self.size / 2)

    def get_position(self):
        """
        取得子彈位置資訊\n
        \n
        回傳:\n
        dict: 包含位置和移動方向的資訊\n
        """
        return {
            "x": self.x,
            "y": self.y,
            "velocity_x": self.velocity_x,
            "velocity_y": self.velocity_y,
            "speed": math.sqrt(self.velocity_x**2 + self.velocity_y**2),
            "angle": math.degrees(math.atan2(self.velocity_y, self.velocity_x)) + 90,
        }


######################技能追蹤子彈類別######################


class SkillBullet(Bullet):
    """
    技能追蹤子彈類別 - 能夠自動追蹤指定敵人的特殊子彈\n
    \n
    此類別繼承自 Bullet，額外提供：\n
    1. 自動尋找並追蹤指定的敵人\n
    2. 彎曲軌跡移動\n
    3. 技能特效視覺效果\n
    4. 多次穿透攻擊能力\n
    5. 3秒生命時間限制\n
    \n
    屬性:\n
    target (object): 當前追蹤的目標敵人\n
    tracking_speed (float): 追蹤轉向速度\n
    max_tracking_distance (float): 最大追蹤距離\n
    skill_type (str): 技能類型（'laser', 'fire', 'ice'）\n
    effect_color (tuple): 技能特效顏色\n
    pierce_count (int): 剩餘穿透次數\n
    lifetime (int): 子彈生命時間（毫秒）\n
    start_time (int): 子彈創建時間\n
    """

    def __init__(
        self,
        x,
        y,
        angle,
        speed,
        damage,
        owner,
        skill_type,
        effect_color,
        enemies,
        target_enemy=None,
        lifetime=3000,
    ):
        """
        初始化技能追蹤子彈\n
        \n
        參數:\n
        x (float): 初始 X 座標位置\n
        y (float): 初始 Y 座標位置\n
        angle (float): 初始發射角度（度數）\n
        speed (float): 子彈移動速度\n
        damage (int): 子彈傷害值\n
        owner (str): 發射者類型（通常是 'player'）\n
        skill_type (str): 技能類型（'laser', 'fire', 'ice'）\n
        effect_color (tuple): 技能特效顏色 RGB\n
        enemies (list): 可追蹤的敵人列表\n
        target_enemy (object): 指定追蹤的特定敵人，如果為None則自動尋找最近敵人\n
        lifetime (int): 子彈生命時間（毫秒），預設3秒\n
        """
        # 調用父類別初始化
        super().__init__(x, y, angle, speed, damage, owner)

        # 技能追蹤特性
        self.skill_type = skill_type
        self.effect_color = effect_color
        self.enemies_list = enemies  # 存儲敵人列表參考
        self.target = target_enemy  # 指定的目標敵人
        self.tracking_speed = 3.0  # 追蹤轉向速度（每幀最大轉向度數）
        self.max_tracking_distance = 400  # 最大追蹤距離
        self.pierce_count = 3  # 可穿透敵人數量（增加以攻擊更多敵人）

        # 生命時間管理
        self.lifetime = lifetime  # 子彈生命時間（毫秒）
        self.start_time = pygame.time.get_ticks()  # 記錄創建時間

        # 如果沒有指定目標，尋找最近的敵人
        if self.target is None:
            self._find_nearest_target()

        # 技能特效軌跡記錄
        self.trail_positions = []
        self.max_trail_length = 10  # 增加軌跡長度

    def _find_nearest_target(self):
        """
        尋找最近的活著敵人作為追蹤目標\n
        """
        if not self.enemies_list:
            return

        nearest_enemy = None
        min_distance = float("inf")

        bullet_center_x = self.x + self.size / 2
        bullet_center_y = self.y + self.size / 2

        for enemy in self.enemies_list:
            if enemy.is_alive:
                # 計算敵人中心點
                enemy_center_x = enemy.x + enemy.width / 2
                enemy_center_y = enemy.y + enemy.height / 2

                # 計算距離
                distance = math.sqrt(
                    (enemy_center_x - bullet_center_x) ** 2
                    + (enemy_center_y - bullet_center_y) ** 2
                )

                # 只追蹤在有效範圍內的敵人
                if distance < self.max_tracking_distance and distance < min_distance:
                    min_distance = distance
                    nearest_enemy = enemy

        self.target = nearest_enemy

    def _update_tracking(self):
        """
        更新追蹤邏輯 - 調整子彈方向朝向目標\n
        """
        if not self.target or not self.target.is_alive:
            # 目標死亡或消失，重新尋找目標
            self._find_nearest_target()
            return

        # 計算子彈和目標的中心點
        bullet_center_x = self.x + self.size / 2
        bullet_center_y = self.y + self.size / 2
        target_center_x = self.target.x + self.target.width / 2
        target_center_y = self.target.y + self.target.height / 2

        # 檢查目標是否還在追蹤範圍內
        distance = math.sqrt(
            (target_center_x - bullet_center_x) ** 2
            + (target_center_y - bullet_center_y) ** 2
        )

        if distance > self.max_tracking_distance:
            # 目標太遠，重新尋找目標
            self._find_nearest_target()
            return

        # 計算朝向目標的角度
        target_angle_rad = math.atan2(
            target_center_y - bullet_center_y, target_center_x - bullet_center_x
        )

        # 計算當前移動角度
        current_angle_rad = math.atan2(self.velocity_y, self.velocity_x)

        # 計算角度差
        angle_diff = target_angle_rad - current_angle_rad

        # 正規化角度差到 -π 到 π 之間
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi

        # 限制轉向速度
        max_turn_rad = math.radians(self.tracking_speed)
        if abs(angle_diff) > max_turn_rad:
            angle_diff = max_turn_rad if angle_diff > 0 else -max_turn_rad

        # 計算新的移動角度
        new_angle_rad = current_angle_rad + angle_diff

        # 計算新的速度向量（保持相同速度大小）
        current_speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
        self.velocity_x = current_speed * math.cos(new_angle_rad)
        self.velocity_y = current_speed * math.sin(new_angle_rad)

    def update(self, screen_width, screen_height):
        """
        更新技能子彈狀態（覆寫父類別方法）\n
        \n
        參數:\n
        screen_width (int): 螢幕寬度\n
        screen_height (int): 螢幕高度\n
        \n
        回傳:\n
        bool: 子彈是否仍然有效\n
        """
        if not self.is_active:
            return False

        # 檢查生命時間是否已過
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.lifetime:
            self.is_active = False
            return False

        # 記錄軌跡位置（用於特效繪製）
        self.trail_positions.append((self.x + self.size / 2, self.y + self.size / 2))
        if len(self.trail_positions) > self.max_trail_length:
            self.trail_positions.pop(0)

        # 更新追蹤邏輯
        self._update_tracking()

        # 調用父類別的位置更新
        return super().update(screen_width, screen_height)

    def check_collision(self, target):
        """
        檢查碰撞（覆寫父類別方法以支援穿透）\n
        \n
        參數:\n
        target: 目標物件\n
        \n
        回傳:\n
        bool: 是否發生碰撞\n
        """
        collision = super().check_collision(target)

        if collision and self.pierce_count > 0:
            # 穿透攻擊：不立即失效，減少穿透次數
            self.pierce_count -= 1
            if self.pierce_count <= 0:
                self.is_active = False
            return True
        elif collision:
            # 沒有穿透次數，正常失效
            self.is_active = False
            return True

        return False

    def draw(self, screen):
        """
        繪製技能追蹤子彈（覆寫父類別方法）\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        """
        if not self.is_active:
            return

        # 繪製軌跡特效
        self._draw_skill_trail(screen)

        # 繪製子彈本體（比普通子彈大一點）
        skill_size = self.size + 4
        skill_x = self.x - 2
        skill_y = self.y - 2

        # 根據技能類型決定視覺效果
        if self.skill_type == "laser":
            # 雷射：明亮的核心 + 光暈效果
            # 外圈光暈
            pygame.draw.circle(
                screen,
                tuple(min(255, c + 100) for c in self.effect_color),
                (int(skill_x + skill_size / 2), int(skill_y + skill_size / 2)),
                skill_size // 2 + 3,
            )
            # 內核
            pygame.draw.circle(
                screen,
                self.effect_color,
                (int(skill_x + skill_size / 2), int(skill_y + skill_size / 2)),
                skill_size // 2,
            )

        elif self.skill_type == "fire":
            # 火焰：橙紅漸變 + 火花效果
            # 外層火焰
            fire_outer = (255, 69, 0)  # 橙紅色
            fire_inner = (255, 255, 0)  # 黃色

            pygame.draw.circle(
                screen,
                fire_outer,
                (int(skill_x + skill_size / 2), int(skill_y + skill_size / 2)),
                skill_size // 2 + 2,
            )
            pygame.draw.circle(
                screen,
                fire_inner,
                (int(skill_x + skill_size / 2), int(skill_y + skill_size / 2)),
                skill_size // 2 - 1,
            )

        elif self.skill_type == "ice":
            # 冰凍：藍白漸變 + 冰晶效果
            ice_outer = (100, 149, 237)  # 藍色
            ice_inner = (230, 230, 250)  # 淡紫白

            # 六角形冰晶形狀
            center_x = int(skill_x + skill_size / 2)
            center_y = int(skill_y + skill_size / 2)
            radius = skill_size // 2

            # 畫六角形
            points = []
            for i in range(6):
                angle = i * 60
                x = center_x + math.cos(math.radians(angle)) * radius
                y = center_y + math.sin(math.radians(angle)) * radius
                points.append((int(x), int(y)))

            if len(points) > 2:
                pygame.draw.polygon(screen, ice_outer, points)

            # 內部圓形
            pygame.draw.circle(screen, ice_inner, (center_x, center_y), radius - 2)

        # 繪製白色邊框增加對比度
        pygame.draw.circle(
            screen,
            COLORS["white"],
            (int(skill_x + skill_size / 2), int(skill_y + skill_size / 2)),
            skill_size // 2,
            1,
        )

    def _draw_skill_trail(self, screen):
        """
        繪製技能軌跡特效\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        """
        if len(self.trail_positions) < 2:
            return

        # 根據技能類型繪製不同的軌跡
        for i in range(len(self.trail_positions) - 1):
            # 計算軌跡點的透明度（越舊越透明）
            alpha_factor = i / len(self.trail_positions)
            trail_alpha = int(alpha_factor * 150)

            # 創建帶透明度的顏色
            trail_color = (*self.effect_color, trail_alpha)

            # 軌跡點大小（越舊越小）
            trail_size = int(3 + alpha_factor * 5)

            # 繪製軌跡點
            trail_x, trail_y = self.trail_positions[i]

            if self.skill_type == "laser":
                # 雷射軌跡：直線光束
                if i > 0:
                    prev_x, prev_y = self.trail_positions[i - 1]
                    pygame.draw.line(
                        screen,
                        self.effect_color,
                        (int(prev_x), int(prev_y)),
                        (int(trail_x), int(trail_y)),
                        max(1, trail_size // 2),
                    )
            else:
                # 火焰和冰凍軌跡：點狀軌跡
                pygame.draw.circle(
                    screen, self.effect_color, (int(trail_x), int(trail_y)), trail_size
                )


######################子彈管理系統######################


class BulletManager:
    """
    子彈管理系統 - 統一管理所有子彈的生命週期\n
    \n
    此類別負責：\n
    1. 子彈的產生和初始化\n
    2. 批量更新所有子彈狀態\n
    3. 自動清理無效子彈\n
    4. 提供碰撞檢測接口\n
    5. 批量繪製所有子彈\n
    \n
    屬性:\n
    bullets (list): 所有活躍子彈的列表\n
    """

    def __init__(self):
        """
        初始化子彈管理系統\n
        """
        self.bullets = []

    def create_bullet(self, x, y, angle, speed, damage, owner="player"):
        """
        創建新子彈\n
        \n
        參數:\n
        x (float): 初始 X 座標位置\n
        y (float): 初始 Y 座標位置\n
        angle (float): 發射角度（度數）\n
        speed (float): 子彈移動速度\n
        damage (int): 子彈傷害值\n
        owner (str): 發射者類型\n
        \n
        回傳:\n
        Bullet: 新創建的子彈物件\n
        """
        bullet = Bullet(x, y, angle, speed, damage, owner)
        self.bullets.append(bullet)
        return bullet

    def create_skill_bullet(
        self,
        x,
        y,
        angle,
        speed,
        damage,
        owner,
        skill_type,
        effect_color,
        enemies,
        target_enemy=None,
        lifetime=3000,
    ):
        """
        創建技能追蹤子彈\n
        \n
        參數:\n
        x (float): 初始 X 座標位置\n
        y (float): 初始 Y 座標位置\n
        angle (float): 發射角度（度數）\n
        speed (float): 子彈移動速度\n
        damage (int): 子彈傷害值\n
        owner (str): 發射者類型\n
        skill_type (str): 技能類型（'laser', 'fire', 'ice'）\n
        effect_color (tuple): 技能特效顏色\n
        enemies (list): 可追蹤的敵人列表（保留以便向後相容）\n
        target_enemy (Enemy): 要追蹤的特定敵人物件（新參數）\n
        lifetime (int): 子彈生命時間（毫秒），預設3秒\n
        \n
        回傳:\n
        SkillBullet: 新創建的技能子彈物件\n
        """
        skill_bullet = SkillBullet(
            x,
            y,
            angle,
            speed,
            damage,
            owner,
            skill_type,
            effect_color,
            enemies,
            target_enemy,
            lifetime,
        )
        self.bullets.append(skill_bullet)
        return skill_bullet

    def create_scatter_shot(
        self,
        x,
        y,
        base_angle,
        speed,
        damage,
        bullet_count,
        spread_angle,
        owner="player",
    ):
        """
        創建散彈射擊\n
        \n
        在指定角度範圍內創建多發子彈\n
        \n
        參數:\n
        x (float): 發射起始 X 座標\n
        y (float): 發射起始 Y 座標\n
        base_angle (float): 基準發射角度（度數）\n
        speed (float): 子彈移動速度\n
        damage (int): 每發子彈的傷害值\n
        bullet_count (int): 子彈數量\n
        spread_angle (float): 散布角度範圍\n
        owner (str): 發射者類型\n
        \n
        回傳:\n
        list: 創建的子彈列表\n
        """
        created_bullets = []

        if bullet_count == 1:
            # 單發子彈，直接射擊
            bullet = self.create_bullet(x, y, base_angle, speed, damage, owner)
            created_bullets.append(bullet)
        else:
            # 多發子彈，計算散布角度
            angle_step = spread_angle / (bullet_count - 1) if bullet_count > 1 else 0
            start_angle = base_angle - spread_angle / 2

            for i in range(bullet_count):
                angle = start_angle + i * angle_step
                bullet = self.create_bullet(x, y, angle, speed, damage, owner)
                created_bullets.append(bullet)

        return created_bullets

    def update(self, screen_width, screen_height):
        """
        更新所有子彈狀態\n
        \n
        處理所有子彈的移動和生命週期，自動清理無效子彈\n
        \n
        參數:\n
        screen_width (int): 螢幕寬度\n
        screen_height (int): 螢幕高度\n
        """
        # 更新所有子彈並收集還活著的子彈
        active_bullets = []

        for bullet in self.bullets:
            if bullet.update(screen_width, screen_height):
                active_bullets.append(bullet)

        # 更新子彈列表（移除無效子彈）
        self.bullets = active_bullets

    def check_collisions_with_targets(self, targets, target_type):
        """
        檢查子彈與目標列表的碰撞\n
        \n
        只檢查不同陣營的碰撞（玩家子彈 vs 敵人，敵人子彈 vs 玩家）\n
        \n
        參數:\n
        targets (list): 目標物件列表\n
        target_type (str): 目標類型（'player' 或 'enemy'）\n
        \n
        回傳:\n
        list: 碰撞事件列表，每個事件包含 {'bullet': bullet, 'target': target}\n
        """
        collisions = []

        for bullet in self.bullets[:]:  # 使用切片避免在迴圈中修改列表
            if not bullet.is_active:
                continue

            # 檢查陣營：玩家子彈只能打敵人，敵人子彈只能打玩家
            if (bullet.owner == "player" and target_type == "enemy") or (
                bullet.owner == "enemy" and target_type == "player"
            ):

                for target in targets:
                    if bullet.check_collision(target):
                        collisions.append(
                            {
                                "bullet": bullet,
                                "target": target,
                                "damage": bullet.damage,
                            }
                        )
                        bullet.hit_target()  # 子彈擊中後失效
                        break  # 一顆子彈只能打中一個目標

        return collisions

    def check_collision_with_single_target(self, target, target_type):
        """
        檢查子彈與單一目標的碰撞\n
        \n
        參數:\n
        target: 目標物件\n
        target_type (str): 目標類型（'player' 或 'enemy'）\n
        \n
        回傳:\n
        list: 碰撞的子彈列表\n
        """
        hit_bullets = []

        for bullet in self.bullets[:]:
            if not bullet.is_active:
                continue

            # 檢查陣營匹配
            if (bullet.owner == "player" and target_type == "enemy") or (
                bullet.owner == "enemy" and target_type == "player"
            ):

                if bullet.check_collision(target):
                    hit_bullets.append(bullet)
                    bullet.hit_target()

        return hit_bullets

    def draw(self, screen):
        """
        繪製所有子彈\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面物件\n
        """
        for bullet in self.bullets:
            bullet.draw(screen)

    def get_bullets_by_owner(self, owner):
        """
        取得指定發射者的子彈列表\n
        \n
        參數:\n
        owner (str): 發射者類型（'player' 或 'enemy'）\n
        \n
        回傳:\n
        list: 符合條件的子彈列表\n
        """
        return [
            bullet
            for bullet in self.bullets
            if bullet.owner == owner and bullet.is_active
        ]

    def get_bullet_count(self):
        """
        取得當前活躍子彈數量\n
        \n
        回傳:\n
        int: 活躍子彈總數\n
        """
        return len(self.bullets)

    def clear_all_bullets(self):
        """
        清除所有子彈\n
        \n
        用於遊戲重置或場景切換時\n
        """
        self.bullets.clear()

    def clear_bullets_by_owner(self, owner):
        """
        清除指定發射者的所有子彈\n
        \n
        參數:\n
        owner (str): 發射者類型（'player' 或 'enemy'）\n
        """
        self.bullets = [bullet for bullet in self.bullets if bullet.owner != owner]

    def get_stats(self):
        """
        取得子彈統計資訊\n
        \n
        回傳:\n
        dict: 統計資訊，包含各類型子彈數量\n
        """
        player_bullets = len([b for b in self.bullets if b.owner == "player"])
        enemy_bullets = len([b for b in self.bullets if b.owner == "enemy"])

        return {
            "total": len(self.bullets),
            "player_bullets": player_bullets,
            "enemy_bullets": enemy_bullets,
        }
