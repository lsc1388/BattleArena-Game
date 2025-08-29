######################載入套件######################
import pygame
import os
from src.config import SOUND_CONFIGS


######################物件類別######################
class SoundManager:
    """
    音效管理器 - 統一管理遊戲中所有音效的載入和播放\n
    \n
    此類別負責：\n
    1. 初始化 pygame 音效系統\n
    2. 載入和緩存音效檔案\n
    3. 提供簡單的音效播放介面\n
    4. 處理音效載入失敗的情況\n
    \n
    使用方式:\n
    sound_manager = SoundManager()\n
    sound_manager.play_sound('race_start')\n
    sound_manager.play_weapon_sound('shotgun')\n
    """

    def __init__(self):
        """
        初始化音效管理器\n
        \n
        初始化步驟：\n
        1. 啟動 pygame mixer 音效系統\n
        2. 設定音效緩衝區大小和品質\n
        3. 載入所有配置的音效檔案\n
        4. 準備音效字典供快速存取\n
        """
        # 初始化 pygame 音效系統，設定合適的參數
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.init()

        # 儲存載入的音效檔案
        self.sounds = {}

        # 載入所有音效檔案
        self._load_sounds()

    def _load_sounds(self):
        """
        載入所有音效檔案到記憶體中\n
        \n
        從 SOUND_CONFIGS 載入音效設定，包含：\n
        - 檔案路徑\n
        - 音量設定\n
        - 錯誤處理\n
        \n
        如果音效檔案載入失敗，會印出錯誤訊息但不會中斷遊戲\n
        """
        for sound_name, sound_config in SOUND_CONFIGS.items():
            try:
                # 取得音效檔案的完整路徑
                sound_path = sound_config["file_path"]

                # 檢查檔案是否存在
                if not os.path.exists(sound_path):
                    print(f"音效檔案不存在: {sound_path}")
                    continue

                # 載入音效檔案
                sound = pygame.mixer.Sound(sound_path)

                # 設定音量（0.0 到 1.0 之間）
                sound.set_volume(sound_config["volume"])

                # 儲存到字典中供後續使用
                self.sounds[sound_name] = sound

                print(f"成功載入音效: {sound_name}")

            except pygame.error as e:
                # pygame 載入音效失敗
                print(f"載入音效 {sound_name} 失敗: {e}")
            except Exception as e:
                # 其他未預期的錯誤
                print(f"載入音效 {sound_name} 時發生錯誤: {e}")

    def play_sound(self, sound_name):
        """
        播放指定名稱的音效\n
        \n
        參數:\n
        sound_name (str): 音效名稱，對應 SOUND_CONFIGS 中的 key\n
        \n
        使用範例:\n
        sound_manager.play_sound('race_start')  # 播放開始音效\n
        sound_manager.play_sound('plasma_gun')  # 播放電漿槍音效\n
        \n
        錯誤處理:\n
        - 如果音效不存在，印出警告訊息但不會中斷遊戲\n
        - 如果播放失敗，捕獲例外並印出錯誤訊息\n
        """
        if sound_name not in self.sounds:
            print(f"找不到音效: {sound_name}")
            return

        try:
            # 播放音效（不等待播放完成）
            self.sounds[sound_name].play()
        except pygame.error as e:
            print(f"播放音效 {sound_name} 失敗: {e}")

    def play_weapon_sound(self, weapon_type):
        """
        根據武器類型播放對應的射擊音效\n
        \n
        參數:\n
        weapon_type (str): 武器類型，來自 WEAPON_CONFIGS 的 key\n
        \n
        武器音效對應:\n
        - shotgun: 霰彈槍音效\n
        - rifle, pistol: 電漿槍音效\n
        \n
        使用範例:\n
        sound_manager.play_weapon_sound('shotgun')  # 播放霰彈槍音效\n
        sound_manager.play_weapon_sound('rifle')    # 播放步槍音效\n
        """
        # 根據武器類型決定要播放的音效
        if weapon_type == "shotgun":
            self.play_sound("shotgun")
        elif weapon_type in ["rifle", "pistol"]:
            self.play_sound("plasma_gun")
        else:
            print(f"未知的武器類型: {weapon_type}")

    def play_victory_sound(self):
        """
        播放勝利音效\n
        \n
        當玩家完成關卡或獲得勝利時播放特殊的勝利音效\n
        \n
        使用範例:\n
        sound_manager.play_victory_sound()  # 在遊戲勝利時播放\n
        """
        self.play_sound("victory")

    def play_death_sound(self):
        """
        播放死亡音效\n
        \n
        當玩家死亡時播放特殊的死亡音效\n
        \n
        使用範例:\n
        sound_manager.play_death_sound()  # 在玩家死亡時播放\n
        """
        self.play_sound("death")

    def play_skill_sound(self):
        """
        播放技能音效\n
        \n
        當玩家使用技能時播放特殊的技能音效\n
        \n
        使用範例:\n
        sound_manager.play_skill_sound()  # 在使用技能時播放\n
        """
        self.play_sound("skill_use")

    def play_powerup_pickup_sound(self):
        """
        播放道具拾取音效\n
        \n
        當玩家拾取道具時播放特殊的拾取音效\n
        \n
        使用範例:\n
        sound_manager.play_powerup_pickup_sound()  # 在拾取道具時播放\n
        """
        self.play_sound("powerup_pickup")

    def play_level3_boss_music(self):
        """
        播放第3關BOSS戰專用背景音樂\n
        \n
        使用 pygame.mixer.music 播放長時間的背景音樂\n
        這比 pygame.mixer.Sound 更適合播放大型音樂檔案\n
        \n
        使用範例:\n
        sound_manager.play_level3_boss_music()  # 在第3關BOSS戰開始時播放\n
        """
        try:
            # 停止當前播放的背景音樂
            pygame.mixer.music.stop()

            # 載入第3關BOSS音樂
            music_path = SOUND_CONFIGS["level3_boss_music"]["file_path"]
            pygame.mixer.music.load(music_path)

            # 設定音量
            volume = SOUND_CONFIGS["level3_boss_music"]["volume"]
            pygame.mixer.music.set_volume(volume)

            # 播放音樂（循環播放）
            pygame.mixer.music.play(-1)  # -1 表示無限循環

            print(f"✅ 開始播放第3關BOSS音樂 (音量: {volume})")

        except Exception as e:
            print(f"❌ 播放第3關BOSS音樂失敗: {e}")

    def stop_background_music(self):
        """
        停止背景音樂\n
        \n
        停止當前播放的背景音樂\n
        """
        try:
            pygame.mixer.music.stop()
            print("⏹️ 背景音樂已停止")
        except Exception as e:
            print(f"❌ 停止背景音樂失敗: {e}")

    def set_master_volume(self, volume):
        """
        設定主音量\n
        \n
        參數:\n
        volume (float): 音量大小，範圍 0.0 到 1.0\n
        \n
        注意: 這會影響所有已載入的音效\n
        """
        volume = max(0.0, min(1.0, volume))  # 確保音量在有效範圍內

        for sound in self.sounds.values():
            # 重新計算每個音效的音量（原始音量 * 主音量）
            original_volume = sound.get_volume()
            sound.set_volume(original_volume * volume)


# 創建全域音效管理器實例
sound_manager = SoundManager()
