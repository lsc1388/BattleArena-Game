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
    "cyan": (0, 200, 200),
    "light_blue": (150, 200, 255),
}

# 玩家設定
PLAYER_SIZE = 40
PLAYER_SPEED = 5
PLAYER_DEFAULT_HEALTH = 100

######################角色與場景設定######################

# 玩家角色設定（貓/狗/狼）
PLAYER_ROLES = {
    "cat": {"name": "貓", "color": (80, 150, 255)},
    "dog": {"name": "狗", "color": (255, 150, 80)},
    "wolf": {"name": "狼", "color": (180, 180, 255)},
}

# 敵人種類（機器人/外星人/殭屍）
ENEMY_TYPES = {
    "robot": {"name": "機器人", "color": (180, 180, 180)},
    "alien": {"name": "外星人", "color": (120, 255, 120)},
    "zombie": {"name": "殭屍", "color": (150, 200, 150)},
}

# 場景設定（岩漿/高山/冰原）
SCENE_CONFIGS = {
    "magma": {
        "name": "岩漿場景",
        "background": (20, 10, 10),
        "accent": (200, 50, 0),
        # 輕微環境效果：每秒對所有單位造成 1 傷害（模擬炎熱環境）
        "env_damage_per_sec": 1,
        "speed_multiplier": 1.0,
    },
    "mountain": {
        "name": "高山場景",
        "background": (15, 20, 25),
        "accent": (120, 120, 120),
        # 無持續傷害，保持標準速度
        "env_damage_per_sec": 0,
        "speed_multiplier": 1.0,
    },
    "ice": {
        "name": "冰原場景",
        "background": (10, 20, 35),
        "accent": (120, 180, 255),
        # 冰原讓移動更滑，給玩家一點速度加成
        "env_damage_per_sec": 0,
        "speed_multiplier": 1.1,
    },
}

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

######################技能設定######################

# 不同角色對應的技能參數（皆為全螢幕範圍，冷卻與血量消耗統一）
SKILL_CONFIGS = {
    "cooldown_ms": 120000,  # 2 分鐘
    "hp_cost_ratio": 0.1,   # 扣最大生命 10%
    "roles": {
        # 貓：雷射技能，瞬間高傷害
        "cat": {"type": "laser", "damage": 260},
        # 狗：火焰技能，附加燃燒持續傷害
        "dog": {"type": "fire", "damage": 120, "burn_dps": 8, "burn_duration_ms": 5000},
        # 狼：冰凍技能，減速/定身效果
        "wolf": {"type": "ice", "damage": 80, "freeze_duration_ms": 3500, "slow_ratio": 0.2},
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
    "fire": pygame.K_SPACE,
    "reload": pygame.K_r,
    "weapon_1": pygame.K_1,
    "weapon_2": pygame.K_2,
    "weapon_3": pygame.K_3,
    "weapon_4": pygame.K_4,
    "weapon_5": pygame.K_5,
    "skill": pygame.K_q,
    # 滑鼠控制相關（索引：0左鍵、1中鍵、2右鍵）
    "mouse_fire": 0,
}

# 遊戲狀態
GAME_STATES = {
    "menu": "menu",
    "playing": "playing",
    "game_over": "game_over",
    "paused": "paused",
}
