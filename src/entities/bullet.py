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
