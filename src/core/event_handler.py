######################載入套件######################
import pygame
from src.config import *
from src.utils.sound_manager import get_sound_manager

######################事件處理系統######################


class EventHandler:
    """
    事件處理系統 - 統一管理所有遊戲事件\n
    \n
    此系統負責：\n
    1. 鍵盤事件處理\n
    2. 滑鼠事件處理\n
    3. 系統事件處理（關閉視窗等）\n
    4. 不同遊戲狀態下的事件分發\n
    """

    def __init__(self, game_engine):
        """
        初始化事件處理系統\n
        \n
        參數:\n
        game_engine: 遊戲引擎主物件\n
        """
        self.game_engine = game_engine

    def handle_events(self):
        """
        處理所有遊戲事件\n
        \n
        包括按鍵輸入、視窗事件等\n
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_engine.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 處理滑鼠點擊事件
                self._handle_mouse_click(event.button, event.pos)

            # 優先處理選擇界面事件
            elif self.game_engine.state_manager.current_state in [
                GAME_STATES["character_select"],
                GAME_STATES["difficulty_select"],
                GAME_STATES["scene_select"],
            ]:
                selection_result = self.game_engine.selection_ui.handle_input(event)
                self._handle_selection_result(selection_result)

            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)

        # 處理連續按鍵
        if (
            self.game_engine.state_manager.current_state == GAME_STATES["playing"]
            and self.game_engine.player
        ):
            self._handle_continuous_input()

    def _handle_mouse_click(self, button, pos):
        """
        處理滑鼠點擊事件\n
        根據規格：\n
        - 射擊控制：滑鼠左鍵發射子彈\n
        - 重新開始：滑鼠右鍵重新開始遊戲\n
        \n
        參數:\n
        button (int): 滑鼠按鈕（1=左鍵, 3=右鍵）\n
        pos (tuple): 滑鼠點擊位置\n
        """
        current_state = self.game_engine.state_manager.current_state

        if current_state == GAME_STATES["playing"] and self.game_engine.player:
            if button == 1:  # 滑鼠左鍵 - 射擊
                # 朝滑鼠位置射擊（準心正中心）
                shot_data = self.game_engine.player.shoot(target_pos=pos)
                if shot_data:
                    # 發射子彈
                    for bullet_info in shot_data["bullets"]:
                        self.game_engine.bullet_manager.create_bullet(
                            bullet_info["x"],
                            bullet_info["y"],
                            bullet_info["angle"],
                            bullet_info["speed"],
                            bullet_info["damage"],
                            "player",
                            self.game_engine.player.current_weapon,
                        )
                    self.game_engine.game_stats["shots_fired"] += len(
                        shot_data["bullets"]
                    )
            elif button == 3:  # 滑鼠右鍵 - 重新開始遊戲
                self.game_engine.start_new_game()

        elif current_state == GAME_STATES["game_over"]:
            if button == 3:  # 滑鼠右鍵 - 重新開始遊戲
                self.game_engine.start_new_game()
        elif current_state == GAME_STATES["menu"]:
            if button == 3:  # 選單中也可以右鍵重啟（清除設定）
                self.game_engine.reset_game_settings()

    def _handle_selection_result(self, result):
        """
        處理選擇界面的結果\n
        \n
        參數:\n
        result (dict): 選擇結果\n
        """
        action = result.get("action", "none")

        if action == "back_to_menu":
            self.game_engine.state_manager.change_state("menu")
        elif action == "character_selected":
            self.game_engine.selected_character = result["character"]
            self.game_engine.state_manager.change_state("difficulty_select")
            self.game_engine.selection_ui.current_selection_type = "difficulty"
        elif action == "difficulty_selected":
            self.game_engine.selected_difficulty = result["difficulty"]
            self.game_engine.state_manager.change_state("scene_select")
            self.game_engine.selection_ui.current_selection_type = "scene"
        elif action == "scene_selected":
            self.game_engine.selected_scene = result["scene"]
            # 使用已保存的角色選擇，而不是可能被重置的UI數據
            if result.get("character"):
                self.game_engine.selected_character = result["character"]
            # 確保角色信息不為空
            if not self.game_engine.selected_character:
                self.game_engine.selected_character = "cat"  # 預設角色

            # 播放遊戲開始音效（添加錯誤處理）
            try:
                get_sound_manager().play_sound("race_start")
                print("✅ 播放遊戲開始音效")
            except Exception as e:
                print(f"⚠️ 播放開始音效失敗，但繼續遊戲: {e}")

            # 選擇完畢，進入倒數計時狀態
            print(f"🎯 場景選擇完成: {result['scene']}")
            print(f"🎯 準備進入倒數計時狀態...")
            success = self.game_engine.state_manager.change_state("countdown")
            if success:
                print("✅ 成功進入倒數計時狀態")
            else:
                print("❌ 進入倒數計時狀態失敗")

    def _handle_keydown(self, key):
        """
        處理按鍵按下事件\n
        \n
        參數:\n
        key: 按下的按鍵\n
        """
        current_state = self.game_engine.state_manager.current_state

        if current_state == GAME_STATES["menu"]:
            self._handle_menu_keys(key)
        elif current_state == GAME_STATES["playing"]:
            self._handle_game_keys(key)
        elif current_state == GAME_STATES["paused"]:
            self._handle_paused_keys(key)
        elif current_state == GAME_STATES["game_over"]:
            self._handle_game_over_keys(key)

    def _handle_menu_keys(self, key):
        """處理選單狀態的按鍵"""
        if key == pygame.K_SPACE:
            # 進入角色選擇
            self.game_engine.state_manager.change_state("character_select")
            self.game_engine.selection_ui.reset_selection()
        elif key == pygame.K_1:
            self.game_engine.enemy_difficulty = "weak"
        elif key == pygame.K_2:
            self.game_engine.enemy_difficulty = "medium"
        elif key == pygame.K_3:
            self.game_engine.enemy_difficulty = "strong"
        elif key == pygame.K_h:
            # 切換血量顯示模式
            if self.game_engine.health_display_mode == "bar":
                self.game_engine.health_display_mode = "number"
            else:
                self.game_engine.health_display_mode = "bar"
            self.game_engine.game_ui.set_health_display_mode(
                self.game_engine.health_display_mode
            )
        elif key == pygame.K_PLUS or key == pygame.K_EQUALS:
            # 增加玩家血量
            self.game_engine.player_max_health = min(
                200, self.game_engine.player_max_health + 10
            )
        elif key == pygame.K_MINUS:
            # 減少玩家血量
            self.game_engine.player_max_health = max(
                50, self.game_engine.player_max_health - 10
            )

    def _handle_game_keys(self, key):
        """處理遊戲中的按鍵"""
        if key == pygame.K_ESCAPE:
            # ESC 暫停遊戲
            self.game_engine.state_manager.pause_game()
        elif key == KEYS["reload"]:
            if self.game_engine.player:
                if self.game_engine.player.start_reload():
                    self.game_engine.game_ui.add_message(
                        "填裝中...", "info", COLORS["yellow"]
                    )
        elif key == KEYS["weapon_1"]:
            if (
                self.game_engine.player
                and self.game_engine.player.handle_weapon_switch("1")
            ):
                self.game_engine.game_ui.add_message("切換至手槍", "info")
        elif key == KEYS["weapon_2"]:
            if (
                self.game_engine.player
                and self.game_engine.player.handle_weapon_switch("2")
            ):
                self.game_engine.game_ui.add_message("切換至步槍", "info")
        elif key == KEYS["weapon_3"]:
            if (
                self.game_engine.player
                and self.game_engine.player.handle_weapon_switch("3")
            ):
                self.game_engine.game_ui.add_message("切換至散彈槍", "info")
        elif key == KEYS["weapon_4"]:
            if (
                self.game_engine.player
                and self.game_engine.player.handle_weapon_switch("4")
            ):
                self.game_engine.game_ui.add_message("切換至機關槍", "info")
        elif key == KEYS["weapon_5"]:
            if (
                self.game_engine.player
                and self.game_engine.player.handle_weapon_switch("5")
            ):
                self.game_engine.game_ui.add_message("切換至衝鋒槍", "info")
        elif key == KEYS["skill"]:
            self._handle_skill_activation()
        elif key == KEYS["use_health_pack"]:
            self._handle_use_health_pack()
        elif key == pygame.K_c:
            # 切換準心顯示
            self.game_engine.game_ui.crosshair_enabled = (
                not self.game_engine.game_ui.crosshair_enabled
            )
            if self.game_engine.game_ui.crosshair_enabled:
                self.game_engine.game_ui.add_message(
                    "準心已開啟", "info", COLORS["green"]
                )
            else:
                self.game_engine.game_ui.add_message(
                    "準心已關閉", "info", COLORS["orange"]
                )
        # 開發/測試用快捷鍵
        elif key == pygame.K_F1:
            self._spawn_boss_for_testing()
        elif key == pygame.K_F2:
            self._complete_level_for_testing()

    def _handle_game_over_keys(self, key):
        """處理遊戲結束狀態的按鍵"""
        if key == pygame.K_r:
            self.game_engine.start_new_game()
        elif key == pygame.K_ESCAPE:
            self.game_engine.state_manager.change_state("menu")

    def _handle_paused_keys(self, key):
        """
        處理暫停狀態的按鍵\n
        \n
        ESC - 繼續遊戲\n
        R - 重新開始當前關卡\n
        S - 回到場景選擇\n
        D - 回到難度選擇\n
        C - 回到角色選擇\n
        Q - 退出到主選單\n
        """
        if key == pygame.K_ESCAPE:
            # ESC 繼續遊戲
            self.game_engine.state_manager.resume_game()
        elif key == pygame.K_r:
            # R 重新開始當前關卡
            self.game_engine.restart_current_level()
        elif key == pygame.K_s:
            # S 回到場景選擇
            self.game_engine.restart_from_scene_select()
        elif key == pygame.K_d:
            # D 回到難度選擇
            self.game_engine.restart_from_difficulty_select()
        elif key == pygame.K_c:
            # C 回到角色選擇
            self.game_engine.restart_from_character_select()
        elif key == pygame.K_q:
            # Q 退出到主選單
            self.game_engine.state_manager.change_state("menu")

    def _handle_skill_activation(self):
        """處理技能啟動 - 創建自動追蹤敵人的技能子彈"""
        if self.game_engine.player:
            # 傳遞敵人列表給技能系統
            skill_result = self.game_engine.player.use_skill(self.game_engine.enemies)
            if skill_result["success"]:
                # 顯示技能啟動訊息
                skill_message = f"{skill_result['skill_name']}啟動！"
                self.game_engine.game_ui.add_message(
                    skill_message,
                    "achievement",
                    skill_result["effect_color"],
                )
                self.game_engine.game_ui.add_message(
                    f"消耗生命值 {skill_result['health_cost']}",
                    "damage",
                    COLORS["red"],
                )

                # 創建技能追蹤子彈（支援多目標）
                bullets_data = skill_result["bullets_data"]
                for bullet_data in bullets_data:
                    self.game_engine.bullet_manager.create_skill_bullet(
                        bullet_data["x"],
                        bullet_data["y"],
                        bullet_data["angle"],
                        bullet_data["speed"],
                        bullet_data["damage"],
                        "player",
                        bullet_data["skill_type"],
                        bullet_data["effect_color"],
                        bullet_data["enemies"],
                        bullet_data.get("target_enemy"),  # 新參數：特定目標敵人
                        bullet_data.get("lifetime", 3000),  # 新參數：生命時間，預設3秒
                    )

                # 記錄技能啟動
                self.game_engine.last_skill_activation = pygame.time.get_ticks()
            else:
                self.game_engine.game_ui.add_message(
                    skill_result["reason"], "info", COLORS["yellow"]
                )

    def _handle_use_health_pack(self):
        """
        處理使用補血包的邏輯\n
        """
        if self.game_engine.player:
            result = self.game_engine.player.use_health_pack()
            if result["success"]:
                # 成功使用補血包
                self.game_engine.game_ui.add_message(
                    f"使用補血包 +{result['heal_amount']} HP",
                    "healing",
                    COLORS["green"],
                )
                self.game_engine.game_ui.add_message(
                    f"剩餘補血包: {result['health_pack_count']}",
                    "info",
                    COLORS["white"],
                )
            else:
                # 使用失敗
                self.game_engine.game_ui.add_message(
                    result["reason"], "warning", COLORS["yellow"]
                )

    def _spawn_boss_for_testing(self):
        """開發測試用：生成BOSS"""
        if not any(e.enemy_type == "boss" for e in self.game_engine.enemies):
            from src.entities.enemy import Enemy

            boss_x = SCREEN_WIDTH // 2 - ENEMY_SIZE * 3 // 2
            boss_y = 80
            boss = Enemy(boss_x, boss_y, self.game_engine.enemy_difficulty, "boss")
            self.game_engine.enemies.append(boss)
            self.game_engine.game_ui.add_message(
                "測試: 已召喚 BOSS", "info", COLORS["purple"]
            )

    def _complete_level_for_testing(self):
        """開發測試用：完成關卡"""
        level_config = LEVEL_CONFIGS.get(self.game_engine.selected_difficulty, {}).get(
            self.game_engine.current_level, {}
        )
        self.game_engine.level_enemies_killed = level_config.get("enemy_count", 0)
        self.game_engine.game_ui.add_message(
            "測試: 本關標記為已完成", "info", COLORS["blue"]
        )

    def _handle_continuous_input(self):
        """
        處理需要連續檢測的輸入（WASD移動，滑鼠準心）\n
        根據規格：\n
        - 移動控制：WASD 控制角色位置\n
        - 射擊準心：滑鼠移動準心，子彈命中位置為準心正中心\n
        - 技能方向：當技能啟動時，技能攻擊方向跟隨滑鼠位置\n
        """
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        # 傳遞滑鼠位置，讓Player類別用於技能方向控制
        self.game_engine.player.handle_input(
            keys, mouse_pos=mouse_pos, mouse_buttons=None
        )

        # 處理滑鼠射擊（左鍵連續按住時持續射擊）
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:  # 滑鼠左鍵
            # 朝準心位置射擊
            shot_data = self.game_engine.player.shoot(target_pos=mouse_pos)
            if shot_data:
                # 發射子彈
                for bullet_info in shot_data["bullets"]:
                    self.game_engine.bullet_manager.create_bullet(
                        bullet_info["x"],
                        bullet_info["y"],
                        bullet_info["angle"],
                        bullet_info["speed"],
                        bullet_info["damage"],
                        "player",
                        self.game_engine.player.current_weapon,
                    )

                self.game_engine.game_stats["shots_fired"] += len(shot_data["bullets"])
