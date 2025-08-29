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
        3. 準備空的音效字典（音效將按需載入）\n
        """
        # 初始化 pygame 音效系統，設定合適的參數
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.init()

        # 儲存載入的音效檔案（初始為空，按需載入）
        self.sounds = {}

        print("🎵 音效系統已就緒（音效將按需載入）")

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
        # 如果音效尚未載入，先載入它
        if sound_name not in self.sounds:
            self._load_single_sound(sound_name)

        if sound_name not in self.sounds:
            print(f"找不到或無法載入音效: {sound_name}")
            return

        try:
            # 播放音效（不等待播放完成）
            self.sounds[sound_name].play()
        except pygame.error as e:
            print(f"播放音效 {sound_name} 失敗: {e}")

    def _load_single_sound(self, sound_name):
        """
        載入單一音效檔案（按需載入）

        參數:
        sound_name (str): 要載入的音效名稱
        """
        if sound_name not in SOUND_CONFIGS:
            return

        sound_config = SOUND_CONFIGS[sound_name]
        try:
            # 取得音效檔案的完整路徑
            sound_path = sound_config["file_path"]

            # 檢查檔案是否存在
            if not os.path.exists(sound_path):
                print(f"音效檔案不存在: {sound_path}")
                return

            # 載入音效檔案
            sound = pygame.mixer.Sound(sound_path)

            # 檢查是否需要截取特定時間段
            if "start_time" in sound_config and "end_time" in sound_config:
                start_time = sound_config["start_time"]
                end_time = sound_config["end_time"]

                try:
                    # 使用 pygame.sndarray 處理音效截取
                    import numpy as np
                    from pygame import sndarray

                    # 轉換音效為 numpy 陣列
                    sound_array = sndarray.array(sound)

                    # 獲取音效的採樣率（假設為 22050Hz，pygame 的預設值）
                    sample_rate = 22050

                    # 計算開始和結束的樣本索引
                    start_sample = int(start_time * sample_rate)
                    end_sample = int(end_time * sample_rate)

                    # 確保索引在有效範圍內
                    start_sample = max(0, start_sample)
                    end_sample = min(len(sound_array), end_sample)

                    # 截取指定時間段的音效
                    if len(sound_array.shape) > 1:
                        # 立體聲
                        trimmed_array = sound_array[start_sample:end_sample]
                    else:
                        # 單聲道，轉換為立體聲
                        mono_trimmed = sound_array[start_sample:end_sample]
                        trimmed_array = np.column_stack((mono_trimmed, mono_trimmed))

                    # 轉換回 pygame.mixer.Sound
                    sound = sndarray.make_sound(trimmed_array.astype(np.int16))

                    print(f"按需載入音效片段: {sound_name} ({start_time}-{end_time}秒)")

                except ImportError:
                    print(
                        f"⚠️ numpy 未安裝，無法截取音效片段，使用完整音效: {sound_name}"
                    )
                except Exception as e:
                    print(f"⚠️ 截取音效片段失敗，使用完整音效: {sound_name}, 錯誤: {e}")

            # 設定音量（0.0 到 1.0 之間）
            sound.set_volume(sound_config["volume"])

            # 檢查是否有速度倍率設定（用於機關槍加速音效）
            if "speed_multiplier" in sound_config:
                speed_multiplier = sound_config["speed_multiplier"]
                # 使用 pygame.sndarray 處理音效速度調整
                try:
                    import numpy as np
                    from pygame import sndarray

                    # 轉換音效為 numpy 陣列
                    sound_array = sndarray.array(sound)

                    # 如果是立體聲，取平均值轉為單聲道
                    if len(sound_array.shape) > 1:
                        sound_array = np.mean(sound_array, axis=1)

                    # 計算新的長度（速度快2倍，長度變一半）
                    new_length = int(len(sound_array) / speed_multiplier)

                    # 重新取樣音效
                    step = len(sound_array) / new_length
                    indices = np.arange(new_length) * step
                    resampled = np.interp(
                        indices, np.arange(len(sound_array)), sound_array
                    )

                    # 轉換回 pygame.mixer.Sound
                    resampled = resampled.astype(np.int16)
                    if len(sound_array.shape) == 1:
                        # 單聲道轉立體聲
                        stereo_array = np.column_stack((resampled, resampled))
                    else:
                        stereo_array = resampled

                    sound = sndarray.make_sound(stereo_array)
                    sound.set_volume(sound_config["volume"])

                    print(f"按需載入加速音效: {sound_name} (速度: {speed_multiplier}x)")

                except ImportError:
                    print(
                        f"⚠️ numpy 未安裝，無法調整音效速度，使用原始音效: {sound_name}"
                    )
                except Exception as e:
                    print(f"⚠️ 調整音效速度失敗，使用原始音效: {sound_name}, 錯誤: {e}")

            # 儲存到字典中供後續使用
            self.sounds[sound_name] = sound

            if (
                "speed_multiplier" not in sound_config
                and "start_time" not in sound_config
            ):
                print(f"按需載入音效: {sound_name}")

        except pygame.error as e:
            # pygame 載入音效失敗
            print(f"載入音效 {sound_name} 失敗: {e}")
        except Exception as e:
            # 其他未預期的錯誤
            print(f"載入音效 {sound_name} 時發生錯誤: {e}")

    def play_weapon_sound(self, weapon_type):
        """
        根據武器類型播放對應的射擊音效\n
        \n
        參數:\n
        weapon_type (str): 武器類型，來自 WEAPON_CONFIGS 的 key\n
        \n
        武器音效對應:\n
        - shotgun: 霰彈槍音效\n
        - pistol: 手槍音效（電漿槍音效）\n
        - rifle: 步槍音效（電漿槍音效）\n
        - submachinegun: 衝鋒槍音效（電漿槍音效）\n
        - machinegun: 機關槍音效（電漿槍音效2倍速度）\n
        \n
        使用範例:\n
        sound_manager.play_weapon_sound('shotgun')       # 播放霰彈槍音效\n
        sound_manager.play_weapon_sound('pistol')        # 播放手槍音效\n
        sound_manager.play_weapon_sound('rifle')         # 播放步槍音效\n
        sound_manager.play_weapon_sound('submachinegun') # 播放衝鋒槍音效\n
        sound_manager.play_weapon_sound('machinegun')    # 播放機關槍音效（2倍速）\n
        """
        # 根據武器類型決定要播放的音效
        if weapon_type == "shotgun":
            self.play_sound("shotgun")
        elif weapon_type == "pistol":
            self.play_sound("pistol")
        elif weapon_type == "rifle":
            self.play_sound("rifle")
        elif weapon_type == "submachinegun":
            self.play_sound("submachinegun")
        elif weapon_type == "machinegun":
            self.play_sound("machinegun")
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


# 全域音效管理器實例（延遲初始化）
sound_manager = None


def get_sound_manager():
    """
    獲取音效管理器實例（延遲初始化）

    第一次呼叫時才會初始化SoundManager，避免程式啟動時的阻塞
    """
    global sound_manager
    if sound_manager is None:
        print("🎵 初始化音效系統...")
        sound_manager = SoundManager()
        print("✅ 音效系統初始化完成")
    return sound_manager
