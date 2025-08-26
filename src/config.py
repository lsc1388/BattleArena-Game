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
    "cyan": (0, 255, 255),
    "brown": (139, 69, 19),
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
POWERUP_SPAWN_CHANCE = 0.15  # 15%掉落機率（提高掉落率）
POWERUP_EFFECTS = {
    "fire_boost": {
        "name": "火力增強",
        "emoji": "🔥",
        "duration": 8000,  # 8秒
        "damage_multiplier": 1.5,
        "color": (255, 69, 0),
        "description": "提升50%攻擊力",
    },
    "ammo_refill": {
        "name": "彈藥補給", 
        "emoji": "🎯",
        "instant": True,
        "color": (0, 255, 255),
        "description": "補滿所有彈藥",
    },
    "scatter_shot": {
        "name": "散彈模式",
        "emoji": "💥", 
        "duration": 10000,  # 10秒
        "bullet_count": 5,
        "spread_angle": 25,
        "color": (255, 215, 0),
        "description": "一次發射五顆子彈",
    },
    "health_pack": {
        "name": "醫療包",
        "emoji": "❤️",
        "instant": True,
        "heal_amount": 30,
        "color": (255, 20, 147),
        "description": "回復30點生命值",
    },
    "speed_boost": {
        "name": "速度提升",
        "emoji": "⚡",
        "duration": 6000,  # 6秒
        "speed_multiplier": 1.5,
        "color": (255, 255, 0),
        "description": "提升50%移動速度",
    },
    "machinegun_powerup": {
        "name": "機關槍",
        "emoji": "🔫",
        "instant": True,
        "weapon_unlock": "machinegun",
        "ammo_bonus": 200,
        "color": (128, 128, 128),
        "description": "解鎖機關槍+200發彈藥",
    },
    "submachinegun_powerup": {
        "name": "衝鋒槍",
        "emoji": "🏹",
        "instant": True,
        "weapon_unlock": "submachinegun", 
        "ammo_bonus": 120,
        "color": (75, 0, 130),
        "description": "解鎖衝鋒槍+120發彈藥",
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
        "preferred_enemy_type": "zombie",  # 偏好的敵人類型
    },
    "medium": {
        "name": "中",
        "health": 100,
        "accuracy": 0.6,
        "fire_rate": 700,
        "move_pattern": "tactical",
        "preferred_enemy_type": "robot",
    },
    "strong": {
        "name": "強",
        "health": 120,
        "accuracy": 0.8,
        "fire_rate": 500,
        "move_pattern": "advanced",
        "preferred_enemy_type": "alien",
    },
}

# 敵人特殊能力設定
ENEMY_ABILITIES = {
    "precision_shooting": {
        "name": "精密射擊",
        "accuracy_bonus": 0.2,
        "fire_rate_bonus": 0.8,
        "description": "提升瞄準精度和射擊頻率",
    },
    "energy_shield": {
        "name": "能量護盾",
        "damage_reduction": 0.3,
        "shield_duration": 3000,
        "cooldown": 10000,
        "description": "定期啟動護盾減少30%傷害",
    },
    "regeneration": {
        "name": "生命再生",
        "heal_rate": 2,  # 每秒回復
        "heal_interval": 1000,
        "max_heal_percent": 0.5,  # 最多回復至50%血量
        "description": "緩慢回復生命值",
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
    # 選單導航
    "select": pygame.K_RETURN,
    "back": pygame.K_ESCAPE,
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
}

# 滑鼠控制設定
MOUSE_CONTROLS = {
    "move": "position",           # 滑鼠位置控制移動
    "fire": "left_button",        # 左鍵射擊
    "restart": "right_button",    # 右鍵重開
    "menu": "middle_button",      # 中鍵選單
}

# 角色類型設定
CHARACTER_TYPES = {
    "cat": {
        "name": "貓",
        "emoji": "🐱",
        "skill_name": "雷射技能",
        "skill_effect": "laser",
        "color": (255, 192, 203),  # 粉紅色
        "description": "敏捷的雷射射手",
    },
    "dog": {
        "name": "狗",
        "emoji": "🐶", 
        "skill_name": "火焰技能",
        "skill_effect": "fire",
        "color": (255, 140, 0),  # 橘色
        "description": "忠誠的火焰戰士",
    },
    "wolf": {
        "name": "狼",
        "emoji": "🐺",
        "skill_name": "冰凍技能", 
        "skill_effect": "ice",
        "color": (173, 216, 230),  # 淺藍色
        "description": "冷酷的冰霜獵手",
    },
}

# 敵人角色類型設定
ENEMY_TYPES = {
    "robot": {
        "name": "機器人",
        "emoji": "🤖",
        "color": (128, 128, 128),  # 灰色
        "description": "冷酷的機械戰士",
        "special_ability": "precision_shooting",
    },
    "alien": {
        "name": "外星人", 
        "emoji": "👽",
        "color": (0, 255, 0),  # 綠色
        "description": "神秘的外星侵略者",
        "special_ability": "energy_shield",
    },
    "zombie": {
        "name": "殭屍",
        "emoji": "🧟",
        "color": (139, 69, 19),  # 棕色
        "description": "不死的恐怖生物", 
        "special_ability": "regeneration",
    },
}

# 場景設定
SCENE_CONFIGS = {
    "lava": {
        "name": "岩漿場景",
        "emoji": "🌋",
        "background_color": (139, 0, 0),  # 深紅色
        "accent_color": (255, 69, 0),     # 紅橘色
        "description": "炙熱的火山環境",
        "environmental_effect": {
            "name": "熱浪",
            "damage_over_time": 2,
            "interval": 5000,  # 每5秒
        },
    },
    "mountain": {
        "name": "高山場景", 
        "emoji": "⛰️",
        "background_color": (105, 105, 105),  # 暗灰色
        "accent_color": (255, 255, 255),      # 白色
        "description": "崎嶇的山岳地形",
        "environmental_effect": {
            "name": "稀薄空氣",
            "movement_penalty": 0.8,  # 移動速度減少20%
        },
    },
    "ice": {
        "name": "冰原場景",
        "emoji": "🧊", 
        "background_color": (176, 196, 222),  # 淺鋼藍色
        "accent_color": (135, 206, 250),      # 天空藍
        "description": "嚴寒的冰雪世界",
        "environmental_effect": {
            "name": "寒風",
            "accuracy_penalty": 0.9,  # 瞄準精度降低10%
        },
    },
}

# 技能效果設定
SKILL_EFFECTS = {
    "laser": {
        "name": "雷射光束",
        "damage": 200,
        "visual_effect": "laser_beam",
        "color": (255, 255, 0),  # 黃色
        "duration": 1000,  # 毫秒
        "sound_effect": "laser_zap",
    },
    "fire": {
        "name": "火焰爆發", 
        "damage": 180,
        "visual_effect": "fire_explosion",
        "color": (255, 0, 0),  # 紅色
        "duration": 1500,
        "sound_effect": "fire_blast",
        "dot_damage": 20,  # 持續傷害
        "dot_duration": 3000,
    },
    "ice": {
        "name": "冰凍風暴",
        "damage": 160, 
        "visual_effect": "ice_storm",
        "color": (0, 191, 255),  # 深天空藍
        "duration": 2000,
        "sound_effect": "ice_crack",
        "slow_effect": 0.5,  # 減速50%
        "slow_duration": 5000,
    },
}

# 技能冷卻設定
SKILL_COOLDOWN_TIME = 120000  # 2分鐘（毫秒）
SKILL_HEALTH_COST_PERCENT = 0.1  # 10%生命值

# 血量顯示顏色設定
HEALTH_COLORS = {
    "high": (0, 255, 0),      # 綠色 (>60%)
    "medium": (255, 255, 0),  # 黃色 (30%-60%)
    "low": (255, 0, 0),       # 紅色 (<30%)
    "critical": (255, 0, 255), # 紫色 (<10%)
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
