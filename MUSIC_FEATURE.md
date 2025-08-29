# 🎵 第 3 關 BOSS 音樂功能說明

## 📋 功能概述

當玩家到達第 3 關時，遊戲會自動播放從 YouTube 下載的史詩級 BOSS 戰背景音樂。

## 🎯 觸發條件

- ✅ 玩家完成第 2 關後自動進入第 3 關
- ✅ 玩家直接選擇第 3 關開始遊戲
- ✅ 音樂會循環播放直到關卡結束

## 🔧 技術實現

### 音樂來源

- **YouTube 連結**: https://www.youtube.com/watch?v=QwPiELmMFXs
- **檔案格式**: MP3
- **檔案大小**: 6.33 MB
- **儲存位置**: `音效/level3_boss_music.mp3`

### 播放系統

- **使用技術**: `pygame.mixer.music` (適合長時間背景音樂)
- **音量設定**: 90% (0.9)
- **播放模式**: 循環播放 (`play(-1)`)
- **優勢**: 比 `pygame.mixer.Sound` 更適合大型音樂檔案

### 系統整合

- **配置檔**: `src/config.py` - 音樂檔案路徑和音量設定
- **音效管理**: `src/utils/sound_manager.py` - 播放和停止功能
- **遊戲引擎**: `src/core/game_engine.py` - 第 3 關檢測和觸發

## 🎮 使用方式

### 在遊戲中體驗

1. 啟動遊戲：`python main.py`
2. 選擇角色、難度、場景
3. 完成第 1 關和第 2 關
4. 進入第 3 關時會自動播放 BOSS 音樂

### 手動測試

```python
# 快速測試音樂播放
from src.utils.sound_manager import sound_manager
sound_manager.play_level3_boss_music()
```

## 🔊 音效設定

### 音量調整

在 `src/config.py` 中修改：

```python
"level3_boss_music": {
    "volume": 0.9,  # 調整此值 (0.0 到 1.0)
}
```

### 停止音樂

```python
sound_manager.stop_background_music()
```

## 🐛 問題排除

### 如果聽不到音樂

1. **檢查系統音量**: 確保電腦音量未靜音
2. **檢查檔案**: 確認 `音效/level3_boss_music.mp3` 存在
3. **重新下載**: 使用 `yt-dlp` 重新下載音樂檔案
4. **測試音效**: 檢查其他遊戲音效是否正常

### 控制台訊息

正常運作時會看到：

```
✅ 開始播放第3關BOSS音樂 (音量: 0.9)
進入第3關！播放BOSS音樂
```

## 🎯 功能特色

- 🎵 **史詩級音樂**: 來自專業 DnD BOSS 音樂合集
- 🔄 **自動循環**: 音樂會持續播放直到關卡結束
- 🎚️ **音量優化**: 設定為 90%音量，確保清楚聽見
- 🚀 **無縫整合**: 自動檢測第 3 關並播放，無需手動操作
- 💾 **高效播放**: 使用背景音樂系統，不影響遊戲效能

---

_音樂來源：YouTube DnD Boss Music Playlist_
_實現日期：2025 年 8 月 29 日_
