######################載入套件######################
import pygame

######################基本設定######################

# 螢幕設定
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# 顏色設定
COLORS = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "orange": (255, 165, 0),
    "purple": (128, 0, 128),
    "gray": (128, 128, 128),
    "dark_gray": (64, 64, 64),
}

# 玩家設定
PLAYER_SIZE = 40
PLAYER_SPEED = 5
PLAYER_DEFAULT_HEALTH = 100

# 敵人設定
ENEMY_SIZE = 35
ENEMY_SPEEDS = {
    "weak": 2,  # 弱AI移動速度
    "medium": 3,  # 中AI移動速度
    "strong": 4,  # 強AI移動速度
}

# 子彈設定
BULLET_SIZE = 8
BULLET_SPEED = 10
BULLET_DAMAGE = 25

# 武器設定
WEAPON_CONFIGS = {
    "pistol": {
        "name": "手槍",
        "max_ammo": 12,
        "reload_time": 2000,  # 毫秒
        "fire_rate": 300,  # 毫秒
        "damage": 25,
        "bullet_speed": 10,
    },
    "rifle": {
        "name": "步槍",
        "max_ammo": 30,
        "reload_time": 3000,
        "fire_rate": 150,
        "damage": 40,
        "bullet_speed": 12,
    },
    "shotgun": {
        "name": "散彈槍",
        "max_ammo": 8,
        "reload_time": 4000,
        "fire_rate": 800,
        "damage": 70,
        "bullet_speed": 8,
        "spread": True,  # 散彈效果
        "bullet_count": 5,  # 一次發射子彈數
    },
    "machinegun": {
        "name": "機關槍",
        "max_ammo": 100,
        "reload_time": 5000,
        "fire_rate": 100,  # 快速射擊
        "damage": 150,
        "bullet_speed": 15,
    },
    "submachinegun": {
        "name": "衝鋒槍",
        "max_ammo": 40,
        "reload_time": 3500,
        "fire_rate": 120,
        "damage": 120,
        "bullet_speed": 13,
    },
}

# 驚喜包設定
POWERUP_SIZE = 20
POWERUP_SPAWN_CHANCE = 0.1  # 10%掉落機率
POWERUP_EFFECTS = {
    "fire_boost": {
        "name": "火力增強",
        "duration": 5000,  # 毫秒
        "damage_multiplier": 1.5,
    },
    "ammo_refill": {"name": "彈藥補給", "instant": True},  # 立即效果
    "scatter_shot": {
        "name": "散彈模式",
        "duration": 8000,
        "bullet_count": 5,  # 一次發射五顆子彈
    },
    "machinegun_powerup": {
        "name": "機關槍",
        "instant": True,
        "weapon_unlock": "machinegun",
        "ammo_bonus": 200,  # 額外彈藥
    },
    "submachinegun_powerup": {
        "name": "衝鋒槍",
        "instant": True,
        "weapon_unlock": "submachinegun",
        "ammo_bonus": 120,  # 額外彈藥
    },
}

# AI 難度設定
AI_CONFIGS = {
    "weak": {
        "name": "弱",
        "health": 80,
        "accuracy": 0.3,  # 瞄準精確度
        "fire_rate": 1000,  # 攻擊頻率(毫秒)
        "move_pattern": "simple",  # 移動模式
    },
    "medium": {
        "name": "中",
        "health": 100,
        "accuracy": 0.6,
        "fire_rate": 700,
        "move_pattern": "tactical",
    },
    "strong": {
        "name": "強",
        "health": 120,
        "accuracy": 0.8,
        "fire_rate": 500,
        "move_pattern": "advanced",
    },
}

# 字體設定
FONT_CONFIGS = {
    "chinese_fonts": [
        "Microsoft JhengHei",  # 微軟正黑體
        "Microsoft YaHei",  # 微軟雅黑
        "SimHei",  # 黑體
        "PingFang TC",  # 蘋果繁體中文字體
        "Noto Sans CJK TC",  # Google 繁體中文字體
        "Arial Unicode MS",  # 通用字體
    ],
    "fallback_font": None,  # 系統預設字體
    "sizes": {"large": 36, "medium": 24, "small": 18, "tiny": 14},
}

# 按鍵設定
KEYS = {
    "move_up": pygame.K_w,
    "move_down": pygame.K_s,
    "move_left": pygame.K_a,
    "move_right": pygame.K_d,
    "fire": pygame.K_SPACE,  # 保留空白鍵作為備用
    "reload": pygame.K_r,
    "weapon_1": pygame.K_1,
    "weapon_2": pygame.K_2,
    "weapon_3": pygame.K_3,
    "weapon_4": pygame.K_4,
    "weapon_5": pygame.K_5,
    "skill": pygame.K_q,
    # 滑鼠控制相關
    "mouse_fire": 0,  # 滑鼠左鍵（pygame.BUTTON_LEFT）
    "mouse_restart": 2,  # 滑鼠右鍵（pygame.BUTTON_RIGHT）
}

# 遊戲狀態
GAME_STATES = {
    "menu": "menu",
    "character_select": "character_select",
    "scene_select": "scene_select",
    "playing": "playing",
    "game_over": "game_over",
    "paused": "paused",
}

######################角色配置系統######################

# 玩家角色設定
PLAYER_CHARACTERS = {
    "cat": {
        "name": "貓",
        "emoji": "🐱",
        "color": (255, 100, 150),  # 粉紅色
        "skill_name": "雷射光束",
        "skill_type": "laser",
        "skill_damage": 300,
        "skill_range": "line",
        "skill_description": "發射穿透性雷射，對直線上所有敵人造成傷害",
    },
    "dog": {
        "name": "狗",
        "emoji": "🐶",
        "color": (255, 140, 0),  # 橘色
        "skill_name": "火焰風暴",
        "skill_type": "fire",
        "skill_damage": 250,
        "skill_range": "area",
        "skill_description": "在周圍區域產生火焰，持續燃燒敵人",
    },
    "wolf": {
        "name": "狼",
        "emoji": "🐺",
        "color": (100, 150, 255),  # 冰藍色
        "skill_name": "冰霜爆發",
        "skill_type": "ice",
        "skill_damage": 200,
        "skill_range": "freeze",
        "skill_description": "凍結附近敵人並造成持續傷害",
    },
}

# AI敵人角色設定
ENEMY_CHARACTERS = {
    "robot": {
        "name": "機器人",
        "emoji": "🤖",
        "color": (150, 150, 150),  # 灰色
        "health_multiplier": 1.0,
        "speed_multiplier": 1.0,
        "accuracy_multiplier": 1.2,
    },
    "alien": {
        "name": "外星人",
        "emoji": "👽",
        "color": (100, 255, 100),  # 綠色
        "health_multiplier": 0.8,
        "speed_multiplier": 1.3,
        "accuracy_multiplier": 1.1,
    },
    "zombie": {
        "name": "殭屍",
        "emoji": "🧟",
        "color": (150, 100, 50),  # 棕色
        "health_multiplier": 1.5,
        "speed_multiplier": 0.7,
        "accuracy_multiplier": 0.8,
    },
}

######################場景配置系統######################

# 戰鬥場景設定
BATTLE_SCENES = {
    "lava": {
        "name": "岩漿場景",
        "emoji": "🌋",
        "background_color": (120, 20, 0),  # 深紅色
        "effect_color": (255, 100, 0),  # 橘紅色
        "theme_color": (255, 60, 0),  # 岩漿橘紅色
        "description": "高溫環境，子彈速度+10%",
        "bullet_speed_modifier": 1.1,
        "fire_rate_modifier": 0.9,  # 射擊間隔-10%
        "speed_multiplier": 1.2,  # 移動速度+20%
        "skill_cooldown_multiplier": 1.0,  # 技能冷卻無變化
        "special_effect": "heat",
    },
    "mountain": {
        "name": "高山場景",
        "emoji": "⛰️",
        "background_color": (100, 100, 100),  # 灰色
        "effect_color": (200, 200, 200),  # 淺灰色
        "theme_color": (120, 120, 120),  # 山脈灰色
        "description": "高海拔環境，移動速度+15%",
        "movement_speed_modifier": 1.15,
        "accuracy_modifier": 1.1,  # 瞄準精度+10%
        "speed_multiplier": 1.0,  # 移動速度無變化
        "skill_cooldown_multiplier": 0.75,  # 技能冷卻-25%
        "special_effect": "altitude",
    },
    "ice": {
        "name": "冰原場景",
        "emoji": "🧊",
        "background_color": (200, 230, 255),  # 淺藍色
        "effect_color": (150, 200, 255),  # 冰藍色
        "theme_color": (100, 180, 255),  # 冰藍色
        "description": "極寒環境，技能冷卻-20%",
        "skill_cooldown_modifier": 0.85,  # 技能冷卻-15%
        "movement_speed_modifier": 0.9,  # 移動稍慢-10%
        "speed_multiplier": 0.9,  # 移動速度-10%
        "special_effect": "frost",
    },
}
