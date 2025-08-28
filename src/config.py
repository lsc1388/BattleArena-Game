######################載入套件######################
import pygame

######################基本設定######################

# 螢幕設定
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
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
    "gold": (255, 215, 0),
}

# 玩家設定
PLAYER_SIZE = 40
PLAYER_SPEED = 5
PLAYER_DEFAULT_HEALTH = 200

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
    "health_pack": {
        "name": "補血包",
        "instant": True,  # 立即效果
        "heal_amount": 50,  # 補血量
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
    "fire": pygame.K_SPACE,
    "reload": pygame.K_r,
    "weapon_1": pygame.K_1,
    "weapon_2": pygame.K_2,
    "weapon_3": pygame.K_3,
    "weapon_4": pygame.K_4,
    "weapon_5": pygame.K_5,
    "skill": pygame.K_q,
    # 滑鼠控制相關
    "mouse_fire": 1,  # 滑鼠右鍵（pygame.BUTTON_RIGHT）
}

# 角色設定（玩家可選角色）
CHARACTER_CONFIGS = {
    "cat": {
        "name": "貓",
        "emoji": "🐱",
        "color": (255, 165, 0),  # 橙色
        "image_path": "assets/characters/cat-removebg-preview.png",  # 角色圖片路徑
        "fallback_image_path": "assets/characters/cat.jpg",  # 備用圖片路徑
        "attributes": {
            "attack_power": 1.3,  # 高攻擊力（130%）
            "fire_rate": 0.7,  # 低射速（70%）
            "speed": 1.0,  # 正常速度
            "health": 1.0,  # 正常血量
        },
        "skill": {
            "name": "雷射技能",
            "type": "laser",
            "description": "發射強力雷射光束 - 技能攻擊方向跟隨滑鼠指標",
            "damage": 100,
            "effect_color": (255, 255, 0),  # 黃色雷射
            "cooldown": 10000,  # 10秒
            "health_cost_percent": 10,
            "duration": 3000,  # 技能持續3秒
        },
    },
    "dog": {
        "name": "狗",
        "emoji": "🐶",
        "color": (139, 69, 19),  # 棕色
        "image_path": "assets/characters/dog-removebg-preview.png",  # 角色圖片路徑
        "fallback_image_path": "assets/characters/dog.jpg",  # 備用圖片路徑
        "attributes": {
            "attack_power": 1.0,  # 平衡攻擊力（100%）
            "fire_rate": 1.0,  # 平衡射速（100%）
            "speed": 1.0,  # 平衡速度
            "health": 1.0,  # 平衡血量
        },
        "skill": {
            "name": "火焰技能",
            "type": "fire",
            "description": "釋放燃燒火焰 - 技能攻擊方向跟隨滑鼠指標",
            "damage": 75,
            "effect_color": (255, 69, 0),  # 紅橙色火焰
            "cooldown": 10000,
            "health_cost_percent": 10,
            "duration": 3000,  # 技能持續3秒
        },
    },
    "wolf": {
        "name": "狼",
        "emoji": "🐺",
        "color": (105, 105, 105),  # 灰色
        "image_path": "assets/characters/wolf-removebg-preview.png",  # 角色圖片路徑
        "fallback_image_path": "assets/characters/wolf.jpg",  # 備用圖片路徑
        "attributes": {
            "attack_power": 0.8,  # 低攻擊力（80%）
            "fire_rate": 1.5,  # 高射速（150%）
            "speed": 1.2,  # 高速度（120%）
            "health": 0.9,  # 略低血量（90%）
        },
        "skill": {
            "name": "冰凍技能",
            "type": "ice",
            "description": "冰凍敵人並造成傷害 - 技能攻擊方向跟隨滑鼠指標",
            "damage": 125,
            "effect_color": (173, 216, 230),  # 淺藍色冰
            "cooldown": 10000,
            "health_cost_percent": 10,
            "duration": 3000,  # 技能持續3秒
        },
    },
}

# 場景設定
SCENE_CONFIGS = {
    "lava": {
        "name": "岩漿場景",
        "emoji": "🌋",
        "background_color": (139, 0, 0),  # 深紅色
        "accent_color": (255, 69, 0),  # 橙紅色
        "effect": "heat_damage",  # 可能的環境效果
        "description": "炎熱的岩漿地帶",
    },
    "mountain": {
        "name": "高山場景",
        "emoji": "⛰️",
        "background_color": (105, 105, 105),  # 灰色
        "accent_color": (169, 169, 169),  # 淺灰色
        "effect": "thin_air",  # 可能的環境效果
        "description": "高聳的山峰地帶",
    },
    "ice": {
        "name": "冰原場景",
        "emoji": "🧊",
        "background_color": (70, 130, 180),  # 鋼藍色
        "accent_color": (173, 216, 230),  # 淺藍色
        "effect": "slippery",  # 可能的環境效果
        "description": "寒冷的冰雪世界",
    },
    "desert": {
        "name": "沙漠場景",
        "emoji": "🏜️",
        "background_color": (238, 203, 173),  # 沙漠色
        "accent_color": (255, 218, 185),  # 淺沙色
        "effect": "heat_wave",  # 可能的環境效果
        "description": "炎熱乾燥的沙漠",
    },
}

# AI 對手類型設定
AI_ENEMY_TYPES = {
    "robot": {
        "name": "機器人",
        "emoji": "🤖",
        "color": (128, 128, 128),  # 金屬灰
        "base_health": 50,  # 機器人生命為50
        "speed_modifier": 1.0,
        "accuracy_modifier": 1.2,  # 機器人瞄準較準
        "description": "機械化戰鬥單位",
        "damage": 20,
        "attack_frequency": 1500,  # 1.5秒攻擊頻率
    },
    "alien": {
        "name": "外星人",
        "emoji": "👽",
        "color": (0, 255, 0),  # 綠色
        "base_health": 100,  # 外星人生命為100
        "speed_modifier": 1.3,  # 外星人移動較快
        "accuracy_modifier": 1.0,
        "description": "神秘的外星生物",
        "damage": 35,
        "attack_frequency": 3000,  # 3秒攻擊頻率
    },
    "zombie": {
        "name": "殭屍",
        "emoji": "🧟",
        "color": (0, 100, 0),  # 深綠色
        "base_health": 150,  # 殭屍生命為150
        "speed_modifier": 0.7,  # 殭屍移動較慢
        "accuracy_modifier": 0.8,  # 殭屍瞄準較差
        "description": "不死的怪物",
        "damage": 25,
        "attack_frequency": 2000,  # 2秒攻擊頻率
    },
    "boss": {
        "name": "BOSS",
        "emoji": "👹",
        "color": (180, 0, 180),  # 紫色
        "base_health": 500,  # BOSS 預設生命
        "speed_modifier": 0.6,
        "accuracy_modifier": 1.0,
        "description": "強大的頭目級敵人",
        "damage": 50,
        "attack_frequency": 1200,
    },
}

# 遊戲狀態
GAME_STATES = {
    "menu": "menu",
    "character_select": "character_select",
    "difficulty_select": "difficulty_select",  # 新增難度選擇狀態
    "scene_select": "scene_select",
    "playing": "playing",
    "game_over": "game_over",
    "paused": "paused",
}

# 難度級別設定
DIFFICULTY_CONFIGS = {
    "easy": {
        "name": "簡單",
        "emoji": "😊",
        "description": "適合新手玩家，敵人數量較少",
        "multiplier": 0.7,  # 敵人生命值倍率
    },
    "medium": {
        "name": "中等",
        "emoji": "😐",
        "description": "平衡的挑戰難度，適合一般玩家",
        "multiplier": 1.0,  # 敵人生命值倍率
    },
    "hard": {
        "name": "困難",
        "emoji": "😤",
        "description": "高挑戰性，適合經驗豐富的玩家",
        "multiplier": 1.3,  # 敵人生命值倍率
    },
}

# 關卡設定（按難度分級）
LEVEL_CONFIGS = {
    "easy": {
        1: {
            "name": "第一關 - 殭屍來襲",
            "enemy_counts": {"zombie": 3},
            "enemy_count": 3,
            "scene": "mountain",  # 預設場景
            "description": "擊敗 3 個殭屍",
            "completion_message": "第一關完成！準備迎接外星人入侵！",
        },
        2: {
            "name": "第二關 - 外星人入侵",
            "enemy_counts": {"alien": 5},
            "enemy_count": 5,
            "scene": "desert",  # 沙漠背景
            "description": "擊敗 5 個外星人",
            "completion_message": "第二關完成！小心混合的敵人與 BOSS！",
        },
        3: {
            "name": "第三關 - 混合來襲與 BOSS",
            "enemy_counts": {"zombie": 7, "alien": 5},
            "enemy_count": 12,  # 合計數
            "scene": "lava",  # 岩漿背景
            "boss": True,
            "description": "擊敗 7 個殭屍與 5 個外星人，然後擊敗 BOSS",
            "completion_message": "已擊敗 BOSS！恭喜完成遊戲！",
        },
    },
    "medium": {
        1: {
            "name": "第一關 - 殭屍來襲",
            "enemy_counts": {"zombie": 5},
            "enemy_count": 5,
            "scene": "mountain",  # 預設場景
            "description": "擊敗 5 個殭屍",
            "completion_message": "第一關完成！準備迎接外星人入侵！",
        },
        2: {
            "name": "第二關 - 外星人入侵",
            "enemy_counts": {"alien": 7},
            "enemy_count": 7,
            "scene": "desert",  # 沙漠背景
            "description": "擊敗 7 個外星人",
            "completion_message": "第二關完成！小心混合的敵人與 BOSS！",
        },
        3: {
            "name": "第三關 - 混合來襲與 BOSS",
            "enemy_counts": {"zombie": 10, "alien": 7},
            "enemy_count": 17,  # 合計數
            "scene": "lava",  # 岩漿背景
            "boss": True,
            "description": "擊敗 10 個殭屍與 7 個外星人，然後擊敗 BOSS",
            "completion_message": "已擊敗 BOSS！恭喜完成遊戲！",
        },
    },
    "hard": {
        1: {
            "name": "第一關 - 殭屍來襲",
            "enemy_counts": {"zombie": 7},
            "enemy_count": 7,
            "scene": "mountain",  # 預設場景
            "description": "擊敗 7 個殭屍",
            "completion_message": "第一關完成！準備迎接外星人入侵！",
        },
        2: {
            "name": "第二關 - 外星人入侵",
            "enemy_counts": {"alien": 10},
            "enemy_count": 10,
            "scene": "desert",  # 沙漠背景
            "description": "擊敗 10 個外星人",
            "completion_message": "第二關完成！小心混合的敵人與 BOSS！",
        },
        3: {
            "name": "第三關 - 混合來襲與 BOSS",
            "enemy_counts": {"zombie": 15, "alien": 10},
            "enemy_count": 25,  # 合計數
            "scene": "lava",  # 岩漿背景
            "boss": True,
            "description": "擊敗 15 個殭屍與 10 個外星人，然後擊敗 BOSS",
            "completion_message": "已擊敗 BOSS！恭喜完成遊戲！",
        },
    },
}
