#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BattleArena 基本功能測試腳本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.entities.player import Player
from src.entities.enemy import Enemy
from src.entities.bullet import BulletManager
from src.entities.powerup import PowerUpManager
from src.systems.collision import CollisionSystem
from src.ui.game_ui import GameUI
from src.config import *

def test_player_creation():
    """測試玩家創建和角色選擇"""
    print("🧪 測試玩家創建...")
    
    # 測試不同角色類型
    for character_type in CHARACTER_TYPES.keys():
        player = Player(100, 100, 100, character_type=character_type)
        print(f"✅ 角色 {character_type} 創建成功")
        
        # 測試技能
        skill_info = player.get_skill_cooldown_info()
        print(f"   - 技能冷卻資訊: {skill_info}")
        
        # 測試武器
        weapon_info = player.get_weapon_info()
        print(f"   - 武器資訊: {weapon_info['name']}")

def test_enemy_creation():
    """測試敵人創建和類型"""
    print("\n🧪 測試敵人創建...")
    
    # 測試不同敵人類型
    for enemy_type in ENEMY_TYPES.keys():
        enemy = Enemy(200, 200, "medium", enemy_type=enemy_type)
        print(f"✅ 敵人 {enemy_type} 創建成功")
        print(f"   - 血量: {enemy.health}/{enemy.max_health}")
        print(f"   - 存活狀態: {enemy.is_alive}")

def test_shooting_system():
    """測試射擊系統"""
    print("\n🧪 測試射擊系統...")
    
    bullet_manager = BulletManager()
    player = Player(100, 500, 100, character_type="cat")
    
    # 確保有彈藥
    player.weapons["pistol"]["current_ammo"] = 10
    
    # 測試普通射擊
    shot_result = player.shoot(bullet_manager)
    if shot_result:
        print(f"✅ 普通射擊成功: {shot_result['bullet_count']} 發子彈")
    else:
        print("❌ 普通射擊失敗 - 可能冷卻中或沒有彈藥")
    
    # 重置射擊冷卻
    player.last_shot_time = 0
    
    # 測試散彈射擊
    player.powerups["scatter_shot"] = {"remaining_time": 10.0}
    shot_result = player.shoot(bullet_manager)
    if shot_result:
        print(f"✅ 散彈射擊成功: {shot_result['bullet_count']} 發子彈")
    
    print(f"   - 子彈管理器統計: {bullet_manager.get_stats()}")

def test_powerup_system():
    """測試 PowerUp 系統"""
    print("\n🧪 測試 PowerUp 系統...")
    
    powerup_manager = PowerUpManager()
    player = Player(100, 500, 100)
    
    # 生成不同類型的 PowerUp
    for powerup_type in POWERUP_EFFECTS.keys():
        powerup = powerup_manager.spawn_powerup_at_position(300, 300, powerup_type)
        print(f"✅ PowerUp {powerup_type} 創建成功")
        
        # 測試玩家撿取
        if player.get_rect().colliderect(powerup.get_rect()):
            player.apply_powerup(powerup_type)
            print(f"   - 玩家撿取 {powerup_type} 成功")

def test_skill_system():
    """測試技能系統"""
    print("\n🧪 測試技能系統...")
    
    collision_system = CollisionSystem()
    enemies = []
    
    # 創建一些敵人
    for i in range(3):
        enemy = Enemy(i * 100, 100, "medium")
        enemies.append(enemy)
    
    # 測試不同角色技能
    for character_type in CHARACTER_TYPES.keys():
        player = Player(200, 500, 100, character_type=character_type)
        
        # 重置技能冷卻時間（繞過冷卻限制進行測試）
        player.last_skill_time = 0
        
        skill_result = player.use_skill()
        
        if skill_result.get("success"):
            print(f"✅ {character_type} 技能使用成功")
            
            # 應用技能效果
            collision_system.apply_skill_effects(skill_result, enemies, 800, 600)
            print(f"   - 技能名稱: {skill_result['name']}")
            print(f"   - 技能傷害: {skill_result['damage']}")
        else:
            print(f"❌ {character_type} 技能失敗: {skill_result.get('reason', '未知原因')}")

def test_collision_system():
    """測試碰撞系統"""
    print("\n🧪 測試碰撞系統...")
    
    collision_system = CollisionSystem()
    bullet_manager = BulletManager()
    powerup_manager = PowerUpManager()
    
    # 創建測試物件
    player = Player(100, 500, 100)
    enemies = [Enemy(200, 200, "medium")]
    
    # 創建子彈
    bullet_manager.create_bullet(200, 300, 90, 10, 25, "player")
    
    # 創建 PowerUp
    powerup_manager.spawn_powerup_at_position(120, 480, "fire_boost")
    
    # 測試碰撞檢測
    collision_results = collision_system.check_all_collisions(
        player, enemies, bullet_manager, powerup_manager
    )
    
    print(f"✅ 碰撞系統測試完成")
    print(f"   - 子彈擊中: {len(collision_results.get('bullet_hits', []))}")
    print(f"   - PowerUp 撞到: {len(collision_results.get('powerup_pickups', []))}")

def test_ui_system():
    """測試 UI 系統"""
    print("\n🧪 測試 UI 系統...")
    
    try:
        game_ui = GameUI(800, 600)
        print("✅ GameUI 創建成功")
        
        # 測試訊息系統
        game_ui.add_message("測試訊息", "info")
        print("✅ 訊息系統正常")
        
        # 測試血量顯示模式
        game_ui.set_health_display_mode("number")
        print("✅ 血量顯示模式設定成功")
        
    except Exception as e:
        print(f"❌ UI 測試失敗: {e}")

def run_all_tests():
    """運行所有測試"""
    print("🚀 開始 BattleArena 基本功能測試")
    print("=" * 50)
    
    try:
        test_player_creation()
        test_enemy_creation()
        test_shooting_system()
        test_powerup_system()
        test_skill_system()
        test_collision_system()
        test_ui_system()
        
        print("\n" + "=" * 50)
        print("🎉 所有基本測試完成！")
        
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()