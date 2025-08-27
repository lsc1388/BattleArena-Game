######################載入套件######################
import pygame
import math
from src.config import *

######################碰撞檢測系統######################


class CollisionSystem:
    """
    碰撞檢測系統 - 統一處理遊戲中所有物件的碰撞邏輯\n
    \n
    此系統負責：\n
    1. 玩家與敵人子彈的碰撞\n
    2. 敵人與玩家子彈的碰撞\n
    3. 玩家與驚喜包的碰撞\n
    4. 所有物件與地圖邊界的碰撞\n
    5. 碰撞後的效果處理\n
    """

    def __init__(self):
        """
        初始化碰撞檢測系統\n
        """
        self.collision_events = []  # 儲存本幀的碰撞事件

    def check_all_collisions(self, player, enemies, bullet_manager, powerup_manager):
        """
        檢查所有物件之間的碰撞\n
        \n
        這是主要的碰撞檢測方法，每幀呼叫一次\n
        \n
        參數:\n
        player: 玩家物件\n
        enemies: 敵人列表\n
        bullet_manager: 子彈管理系統\n
        powerup_manager: 驚喜包管理系統\n
        \n
        回傳:\n
        dict: 碰撞結果摘要\n
        """
        # 清空上一幀的碰撞事件
        self.collision_events.clear()

        collision_summary = {
            "player_hit": False,
            "enemies_hit": [],
            "powerups_collected": [],
            "bullets_destroyed": 0,
        }

        # 1. 檢查敵人子彈與玩家的碰撞
        player_hits = self._check_bullets_vs_player(player, bullet_manager)
        if player_hits:
            collision_summary["player_hit"] = True
            collision_summary["bullets_destroyed"] += len(player_hits)

        # 2. 檢查玩家子彈與敵人的碰撞
        enemy_hits = self._check_bullets_vs_enemies(enemies, bullet_manager)
        collision_summary["enemies_hit"] = enemy_hits
        collision_summary["bullets_destroyed"] += len(enemy_hits)

        # 3. 檢查玩家與驚喜包的碰撞
        powerup_pickups = powerup_manager.check_player_pickups(player)
        collision_summary["powerups_collected"] = powerup_pickups

        return collision_summary

    def _check_bullets_vs_player(self, player, bullet_manager):
        """
        檢查敵人子彈與玩家的碰撞\n
        \n
        參數:\n
        player: 玩家物件\n
        bullet_manager: 子彈管理系統\n
        \n
        回傳:\n
        list: 擊中玩家的子彈列表\n
        """
        hit_bullets = bullet_manager.check_collision_with_single_target(
            player, "player"
        )

        # 處理每個擊中的子彈
        total_damage = 0
        for bullet in hit_bullets:
            total_damage += bullet.damage

            # 記錄碰撞事件
            self.collision_events.append(
                {
                    "type": "player_hit",
                    "damage": bullet.damage,
                    "bullet_owner": bullet.owner,
                    "position": (bullet.x, bullet.y),
                }
            )

        # 對玩家造成傷害
        if total_damage > 0:
            player.take_damage(total_damage)

        return hit_bullets

    def _check_bullets_vs_enemies(self, enemies, bullet_manager):
        """
        檢查玩家子彈與敵人的碰撞\n
        \n
        參數:\n
        enemies: 敵人列表\n
        bullet_manager: 子彈管理系統\n
        \n
        回傳:\n
        list: 被擊中的敵人資訊列表\n
        """
        hit_enemies = []

        for enemy in enemies[:]:  # 使用切片避免在迴圈中修改列表
            if not enemy.is_alive:
                continue

            # 檢查這個敵人是否被玩家子彈擊中
            hit_bullets = bullet_manager.check_collision_with_single_target(
                enemy, "enemy"
            )

            if hit_bullets:
                # 計算總傷害
                total_damage = sum(bullet.damage for bullet in hit_bullets)

                # 對敵人造成傷害
                enemy.take_damage(total_damage)

                # 記錄擊中事件
                hit_info = {
                    "enemy": enemy,
                    "damage": total_damage,
                    "bullets_count": len(hit_bullets),
                    "killed": not enemy.is_alive,
                }
                hit_enemies.append(hit_info)

                # 記錄碰撞事件
                self.collision_events.append(
                    {
                        "type": "enemy_hit",
                        "enemy": enemy,
                        "damage": total_damage,
                        "position": (enemy.x, enemy.y),
                        "killed": not enemy.is_alive,
                    }
                )

        return hit_enemies

    def check_circular_collision(
        self, obj1_x, obj1_y, obj1_radius, obj2_x, obj2_y, obj2_radius
    ):
        """
        圓形碰撞檢測（更精確的碰撞檢測）\n
        \n
        參數:\n
        obj1_x, obj1_y (float): 第一個物件的中心座標\n
        obj1_radius (float): 第一個物件的半徑\n
        obj2_x, obj2_y (float): 第二個物件的中心座標\n
        obj2_radius (float): 第二個物件的半徑\n
        \n
        回傳:\n
        bool: 是否發生碰撞\n
        """
        distance = math.sqrt((obj1_x - obj2_x) ** 2 + (obj1_y - obj2_y) ** 2)
        return distance <= (obj1_radius + obj2_radius)

    def check_line_circle_collision(
        self, line_start, line_end, circle_center, circle_radius
    ):
        """
        線段與圓形的碰撞檢測\n
        \n
        用於子彈軌跡與圓形物件的精確碰撞檢測\n
        \n
        參數:\n
        line_start (tuple): 線段起始點座標 (x, y)\n
        line_end (tuple): 線段結束點座標 (x, y)\n
        circle_center (tuple): 圓心座標 (x, y)\n
        circle_radius (float): 圓半徑\n
        \n
        回傳:\n
        bool: 是否發生碰撞\n
        """
        # 計算線段向量
        line_vec = (line_end[0] - line_start[0], line_end[1] - line_start[1])
        line_length_sq = line_vec[0] ** 2 + line_vec[1] ** 2

        if line_length_sq == 0:
            # 線段長度為0，視為點碰撞
            return self.check_circular_collision(
                line_start[0],
                line_start[1],
                0,
                circle_center[0],
                circle_center[1],
                circle_radius,
            )

        # 計算從線段起點到圓心的向量在線段上的投影
        to_circle = (circle_center[0] - line_start[0], circle_center[1] - line_start[1])
        projection = (
            to_circle[0] * line_vec[0] + to_circle[1] * line_vec[1]
        ) / line_length_sq

        # 限制投影在線段範圍內
        projection = max(0, min(1, projection))

        # 計算線段上最接近圓心的點
        closest_point = (
            line_start[0] + projection * line_vec[0],
            line_start[1] + projection * line_vec[1],
        )

        # 檢查最接近點與圓心的距離
        distance = math.sqrt(
            (closest_point[0] - circle_center[0]) ** 2
            + (closest_point[1] - circle_center[1]) ** 2
        )

        return distance <= circle_radius

    def check_boundary_collisions(self, obj, screen_width, screen_height):
        """
        檢查物件與螢幕邊界的碰撞\n
        \n
        參數:\n
        obj: 要檢查的物件（需要有 x, y, width, height 屬性）\n
        screen_width (int): 螢幕寬度\n
        screen_height (int): 螢幕高度\n
        \n
        回傳:\n
        dict: 碰撞資訊，包含碰撞的邊界\n
        """
        collisions = {
            "left": obj.x < 0,
            "right": obj.x + obj.width > screen_width,
            "top": obj.y < 0,
            "bottom": obj.y + obj.height > screen_height,
        }

        return collisions

    def resolve_boundary_collision(self, obj, screen_width, screen_height):
        """
        解決物件與邊界的碰撞（將物件推回邊界內）\n
        \n
        參數:\n
        obj: 要處理的物件\n
        screen_width (int): 螢幕寬度\n
        screen_height (int): 螢幕高度\n
        """
        if obj.x < 0:
            obj.x = 0
        elif obj.x + obj.width > screen_width:
            obj.x = screen_width - obj.width

        if obj.y < 0:
            obj.y = 0
        elif obj.y + obj.height > screen_height:
            obj.y = screen_height - obj.height
