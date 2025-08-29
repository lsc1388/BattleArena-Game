# 場景資料夾結構說明

## 概述

此資料夾包含 BattleArena Game 的所有場景相關資源，按照遊戲中的四個場景進行組織。

## 場景類型

根據 `src/config.py` 中的 `SCENE_CONFIGS` 配置，遊戲包含以下四個場景：

### 1. 岩漿場景 (lava) 🌋

- **主色調**：深紅色 (#8B0000)
- **強調色**：橙紅色 (#FF4500)
- **環境效果**：熱傷害 (heat_damage)
- **描述**：炎熱的岩漿地帶
- **使用關卡**：第三關 BOSS 戰

### 2. 高山場景 (mountain) ⛰️

- **主色調**：灰色 (#696969)
- **強調色**：淺灰色 (#A9A9A9)
- **環境效果**：稀薄空氣 (thin_air)
- **描述**：高聳的山峰地帶
- **使用關卡**：第一關

### 3. 冰原場景 (ice) 🧊

- **主色調**：鋼藍色 (#4682B4)
- **強調色**：淺藍色 (#ADD8E6)
- **環境效果**：滑溜表面 (slippery)
- **描述**：寒冷的冰雪世界

### 4. 沙漠場景 (desert) 🏜️

- **主色調**：沙漠色 (#EECBAD)
- **強調色**：淺沙色 (#FFDAB9)
- **環境效果**：熱浪 (heat_wave)
- **描述**：炎熱乾燥的沙漠
- **使用關卡**：第二關

## 資料夾結構

每個場景資料夾包含三個子資料夾：

```
assets/scenes/
├── lava/
│   ├── backgrounds/    # 岩漿場景背景圖片
│   ├── effects/        # 岩漿場景特效資源
│   └── sounds/         # 岩漿場景音效檔案
├── mountain/
│   ├── backgrounds/    # 高山場景背景圖片
│   ├── effects/        # 高山場景特效資源
│   └── sounds/         # 高山場景音效檔案
├── ice/
│   ├── backgrounds/    # 冰原場景背景圖片
│   ├── effects/        # 冰原場景特效資源
│   └── sounds/         # 冰原場景音效檔案
├── desert/
│   ├── backgrounds/    # 沙漠場景背景圖片
│   ├── effects/        # 沙漠場景特效資源
│   └── sounds/         # 沙漠場景音效檔案
└── README.md           # 此說明文件
```

## 各子資料夾用途

### backgrounds/

存放場景背景圖片，建議格式：

- PNG 或 JPG 格式
- 解析度：800x600 像素（配合遊戲螢幕尺寸）
- 命名範例：`lava_background.png`, `mountain_bg.jpg`

### effects/

存放場景特效相關資源，包括：

- 粒子效果圖片
- 動畫序列圖片
- 環境裝飾物圖片
- 命名範例：`lava_particles.png`, `snow_effect.png`

### sounds/

存放場景專屬音效檔案，包括：

- 環境音效（風聲、火聲等）
- 背景音樂
- 特殊效果音
- 建議格式：MP3, WAV, OGG
- 命名範例：`lava_ambient.mp3`, `mountain_wind.wav`

## 開發注意事項

1. **檔案命名**：使用描述性的英文名稱，避免中文檔名
2. **檔案大小**：控制圖片和音效檔案大小，避免影響遊戲載入速度
3. **相容性**：確保使用的格式與 Pygame 相容
4. **配置整合**：新增的資源需要在 `src/config.py` 中相應配置

## 使用範例

要在程式中載入場景資源，可以參考以下路徑格式：

```python
# 載入岩漿場景背景
background_path = "assets/scenes/lava/backgrounds/lava_background.png"

# 載入沙漠場景音效
sound_path = "assets/scenes/desert/sounds/desert_wind.mp3"

# 載入冰原場景特效
effect_path = "assets/scenes/ice/effects/snow_particles.png"
```
