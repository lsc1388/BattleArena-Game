######################載入套件######################
import pygame
from src.config import *

######################狀態管理系統######################


class StateManager:
    """
    遊戲狀態管理系統 - 處理遊戲狀態轉換和管理\n
    \n
    此系統負責：\n
    1. 遊戲狀態切換（選單、遊戲中、結束等）\n
    2. 狀態轉換邏輯驗證\n
    3. 狀態相關的資料管理\n
    4. 狀態切換時的清理工作\n
    """

    def __init__(self, game_engine):
        """
        初始化狀態管理系統\n
        \n
        參數:\n
        game_engine: 遊戲引擎主物件\n
        """
        self.game_engine = game_engine
        self.current_state = GAME_STATES["menu"]
        self.previous_state = None
        self.state_change_time = 0

        # 狀態轉換規則定義
        self.valid_transitions = {
            GAME_STATES["menu"]: [GAME_STATES["character_select"]],
            GAME_STATES["character_select"]: [
                GAME_STATES["menu"],
                GAME_STATES["difficulty_select"],
            ],
            GAME_STATES["difficulty_select"]: [
                GAME_STATES["character_select"],
                GAME_STATES["scene_select"],
            ],
            GAME_STATES["scene_select"]: [
                GAME_STATES["difficulty_select"],
                GAME_STATES["countdown"],
            ],
            GAME_STATES["countdown"]: [
                GAME_STATES["playing"],
            ],
            GAME_STATES["playing"]: [
                GAME_STATES["menu"],
                GAME_STATES["game_over"],
                GAME_STATES["paused"],
            ],
            GAME_STATES["game_over"]: [GAME_STATES["menu"], GAME_STATES["playing"]],
            GAME_STATES["paused"]: [GAME_STATES["playing"], GAME_STATES["menu"]],
        }

    def change_state(self, new_state_name):
        """
        切換遊戲狀態\n
        \n
        參數:\n
        new_state_name (str): 新狀態名稱\n
        \n
        回傳:\n
        bool: 是否成功切換狀態\n
        """
        # 檢查新狀態是否存在
        if new_state_name not in GAME_STATES.values():
            print(f"⚠️ 無效的遊戲狀態: {new_state_name}")
            return False

        new_state = (
            GAME_STATES[new_state_name]
            if new_state_name in GAME_STATES
            else new_state_name
        )

        # 檢查狀態轉換是否合法
        if not self._is_valid_transition(self.current_state, new_state):
            print(f"⚠️ 無效的狀態轉換: {self.current_state} -> {new_state}")
            return False

        # 執行狀態離開處理
        self._on_state_exit(self.current_state)

        # 更新狀態
        self.previous_state = self.current_state
        self.current_state = new_state
        self.state_change_time = pygame.time.get_ticks()

        # 執行狀態進入處理
        self._on_state_enter(new_state)

        print(f"🔄 狀態切換: {self.previous_state} -> {self.current_state}")
        return True

    def _is_valid_transition(self, from_state, to_state):
        """
        檢查狀態轉換是否合法\n
        \n
        參數:\n
        from_state (str): 來源狀態\n
        to_state (str): 目標狀態\n
        \n
        回傳:\n
        bool: 轉換是否合法\n
        """
        # 允許強制回到選單（緊急退出）
        if to_state == GAME_STATES["menu"]:
            return True

        # 檢查轉換規則
        if from_state in self.valid_transitions:
            return to_state in self.valid_transitions[from_state]

        return False

    def _on_state_exit(self, state):
        """
        狀態離開時的處理\n
        \n
        參數:\n
        state (str): 離開的狀態\n
        """
        if state == GAME_STATES["playing"]:
            # 離開遊戲狀態時暫停計時
            if hasattr(self.game_engine, "game_start_time"):
                current_time = pygame.time.get_ticks()
                self.game_engine.game_stats["game_time"] = (
                    current_time - self.game_engine.game_start_time
                ) / 1000

        elif state == GAME_STATES["character_select"]:
            # 重置選擇UI
            if hasattr(self.game_engine, "selection_ui"):
                self.game_engine.selection_ui.reset_selection()

    def _on_state_enter(self, state):
        """
        狀態進入時的處理\n
        \n
        參數:\n
        state (str): 進入的狀態\n
        """
        if state == GAME_STATES["menu"]:
            # 進入選單時重置某些設定
            pass

        elif state == GAME_STATES["character_select"]:
            # 進入角色選擇時設置UI
            if hasattr(self.game_engine, "selection_ui"):
                self.game_engine.selection_ui.current_selection_type = "character"
                self.game_engine.selection_ui.reset_selection()

        elif state == GAME_STATES["difficulty_select"]:
            # 進入難度選擇時設置UI
            if hasattr(self.game_engine, "selection_ui"):
                self.game_engine.selection_ui.current_selection_type = "difficulty"

        elif state == GAME_STATES["scene_select"]:
            # 進入場景選擇時設置UI
            if hasattr(self.game_engine, "selection_ui"):
                self.game_engine.selection_ui.current_selection_type = "scene"

        elif state == GAME_STATES["countdown"]:
            # 進入倒數計時狀態時初始化倒數計時器
            self.game_engine.countdown_start_time = pygame.time.get_ticks()
            self.game_engine.countdown_duration = 3000  # 3秒倒數（毫秒）

        elif state == GAME_STATES["playing"]:
            # 進入遊戲時記錄開始時間
            if (
                not hasattr(self.game_engine, "game_start_time")
                or self.game_engine.game_start_time == 0
            ):
                self.game_engine.game_start_time = pygame.time.get_ticks()

        elif state == GAME_STATES["game_over"]:
            # 進入遊戲結束狀態時停止計時
            if hasattr(self.game_engine, "game_start_time"):
                current_time = pygame.time.get_ticks()
                if self.game_engine.game_start_time > 0:
                    self.game_engine.game_stats["game_time"] = (
                        current_time - self.game_engine.game_start_time
                    ) / 1000

    def get_current_state(self):
        """
        取得當前遊戲狀態\n
        \n
        回傳:\n
        str: 當前狀態名稱\n
        """
        return self.current_state

    def get_previous_state(self):
        """
        取得上一個遊戲狀態\n
        \n
        回傳:\n
        str: 上一個狀態名稱\n
        """
        return self.previous_state

    def get_time_in_current_state(self):
        """
        取得在當前狀態的時間\n
        \n
        回傳:\n
        float: 在當前狀態的時間（秒）\n
        """
        current_time = pygame.time.get_ticks()
        return (current_time - self.state_change_time) / 1000

    def is_state(self, state_name):
        """
        檢查是否為指定狀態\n
        \n
        參數:\n
        state_name (str): 要檢查的狀態名稱\n
        \n
        回傳:\n
        bool: 是否為指定狀態\n
        """
        target_state = (
            GAME_STATES[state_name] if state_name in GAME_STATES else state_name
        )
        return self.current_state == target_state

    def can_transition_to(self, target_state_name):
        """
        檢查是否可以轉換到指定狀態\n
        \n
        參數:\n
        target_state_name (str): 目標狀態名稱\n
        \n
        回傳:\n
        bool: 是否可以轉換\n
        """
        target_state = (
            GAME_STATES[target_state_name]
            if target_state_name in GAME_STATES
            else target_state_name
        )
        return self._is_valid_transition(self.current_state, target_state)
