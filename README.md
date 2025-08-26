# 🎯 BattleArena Game

一個使用 Python 和 Pygame 開發的雙人射擊對戰遊戲，玩家可以與 AI 對手進行激烈的戰鬥！

## 🎮 遊戲特色

### 核心玩法

- **AI 對戰系統**：與智能電腦對手對戰
- **三種難度等級**：弱、中、強三種 AI 挑戰
- **多武器系統**：手槍、步槍、散彈槍可自由切換
- **彈藥管理**：有限彈藥和自動填裝機制
- **特殊技能**：短暫無敵和速度加成技能

### 驚喜包系統

- 🔥 **火力增強**：提升子彈攻擊力
- 🎯 **彈藥補給**：補充所有武器彈藥
- 💥 **散彈模式**：單次發射五顆子彈

### 自訂設定

- **生命值設定**：可調整初始血量（50-200）
- **血量顯示**：支援血條和數字兩種顯示模式
- **難度選擇**：三種 AI 智能等級

## 🕹️ 操作控制

### 基本操作

- `W/A/S/D` - 角色移動
- `空白鍵` - 射擊
- `R` - 手動填裝
- `Q` - 使用特殊技能

### 武器切換

- `1` - 切換至手槍
- `2` - 切換至步槍
- `3` - 切換至散彈槍

### 系統操作

- `ESC` - 暫停/返回選單
- `H` - 切換血量顯示模式（選單中）
- `+/-` - 調整初始血量（選單中）

## 🚀 快速開始

### 系統需求

- Python 3.7 或更高版本
- Pygame 2.0 或更高版本

### 安裝步驟

1. **克隆專案**

   ```bash
   git clone <repository-url>
   cd BattleArena-Game
   ```

2. **安裝依賴**

   ```bash
   pip install pygame
   ```

3. **運行遊戲**
   ```bash
   python main.py
   ```

## 🎯 遊戲玩法

### 開始遊戲

1. 運行遊戲後進入主選單
2. 調整遊戲設定（難度、血量等）
3. 按空白鍵開始遊戲

### 戰鬥策略

- 合理運用三種武器的特性
- 善用驚喜包增強戰力
- 注意彈藥管理，適時填裝
- 運用技能在關鍵時刻逃脫

### 得分系統

- 擊敗敵人：+100 分
- 拾取驚喜包：+50 分
- 追求更高分數和生存時間！

## 🛠️ 專案結構

```
BattleArena-Game/
├── main.py                 # 主程式入口
├── src/                    # 源代碼目錄
│   ├── config.py          # 遊戲設定檔
│   ├── entities/          # 遊戲物件
│   │   ├── player.py      # 玩家類別
│   │   ├── enemy.py       # AI敵人類別
│   │   ├── bullet.py      # 子彈系統
│   │   └── powerup.py     # 驚喜包系統
│   ├── systems/           # 遊戲系統
│   │   └── collision.py   # 碰撞檢測系統
│   └── ui/                # 使用者介面
│       └── game_ui.py     # 遊戲UI系統
├── assets/                # 資源檔案目錄
└── README.md              # 專案說明
```

## 🎨 開發特色

### 程式架構

- **模組化設計**：清晰的程式結構，易於維護
- **物件導向**：使用類別封裝遊戲邏輯
- **系統分離**：UI、碰撞、物件管理各自獨立

### 技術亮點

- **智能 AI 系統**：三種不同行為模式的 AI 對手
- **彈道物理**：真實的子彈軌跡和散彈效果
- **狀態管理**：完整的遊戲狀態機制
- **碰撞檢測**：精確的矩形碰撞檢測

## 🔧 自訂與擴展

### 修改遊戲設定

編輯 `src/config.py` 檔案可調整：

- 武器屬性（傷害、射速、彈藥容量）
- AI 行為參數（精確度、移動速度）
- 驚喜包效果和出現機率
- 畫面尺寸和幀率

### 添加新功能

遊戲採用模組化設計，可輕鬆擴展：

- 新增武器類型
- 設計新的 AI 行為模式
- 創建更多驚喜包效果
- 實作多人對戰模式

## 📄 開發資訊

- **開發語言**：Python 3.x
- **遊戲引擎**：Pygame
- **專案類型**：單人射擊遊戲
- **開發模式**：物件導向程式設計

## 🎉 開始遊戲吧！

現在就運行 `python main.py` 開始你的射擊對戰之旅！挑戰不同難度的 AI 對手，收集強化道具，創造屬於你的最高分記錄！

## Combat & Resources

### Ammunition System

- **Limited Ammo**: Strategic ammunition management required
- **Auto-Reload**: Automatic reloading when ammunition is depleted
- **Tactical Gameplay**: Players must find cover and avoid attacks during reload periods

### Special Abilities

- **Unique Skills**: Character-specific or universal special abilities
- **Tactical Variety**: Skills add depth and strategic options to combat
- **Cooldown System**: Balanced ability usage with cooldown mechanics

### Power-Up Drops (Random Loot)

Surprise packages that randomly drop during battles, featuring:

- **Extra Ammunition**: Additional bullets for extended combat
- **Damage Boost**: Enhanced bullet damage for increased lethality
- **Multi-Shot**: Fire five bullets simultaneously for devastating attacks
- **Special Effects**: Various other combat enhancements

## Customization & Environments

### Battle Scenes

- **Multiple Arenas**: Various battle environments to choose from
- **Diverse Layouts**: Each scene offers unique tactical opportunities
- **Environmental Strategy**: Use terrain and cover to your advantage

### Appearance System

- **Player Customization**: Personalize your character's appearance and clothing
- **AI Customization**: Even computer opponents have switchable outfits
- **Visual Variety**: Multiple costume options for enhanced personalization

## Development Roadmap

### Confirmed Features

- [x] WASD movement controls
- [x] Three AI difficulty levels
- [x] Weapon switching system
- [x] Limited ammunition with auto-reload
- [x] Random power-up drops
- [x] Multiple battle scenes
- [x] Character customization

### Pending Decisions

1. **Health Display Method**:
   - Numerical display vs. health bar visualization
   - User preference settings
2. **Special Abilities Design**:
   - Character-specific vs. universal skills
   - Cooldown and resource consumption mechanics
   - Skill tree progression system
3. **Power-Up Balance**:
   - Drop rates and probability distribution
   - Variety of power-up types
   - Game balance considerations
4. **AI Difficulty Differentiation**:
   - **Easy**: Lower attack frequency, reduced accuracy
   - **Medium**: Balanced attack patterns, moderate accuracy
   - **Hard**: High attack frequency, precise aim, advanced skill usage

## Technical Requirements

### System Requirements

- **OS**: Windows 10/11, macOS 10.14+, or Linux Ubuntu 18.04+
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Graphics**: DirectX 11 compatible graphics card
- **Storage**: 2GB available space

### Development Stack

- **Engine**: Unity 2022.3 LTS (recommended)
- **Programming Language**: C#
- **Graphics**: 2D/3D rendering pipeline
- **Audio**: Unity Audio System
- **Version Control**: Git with GitHub

## Getting Started

### Installation

1. Clone the repository:
   `ash
git clone https://github.com/yourusername/BattleArena-Game.git
`
2. Open the project in Unity Hub
3. Load the main scene from Assets/Scenes/MainMenu.unity
4. Press Play to start development testing

### How to Play

1. **Main Menu**: Select game mode and difficulty
2. **Character Selection**: Choose your character and customize appearance
3. **Arena Selection**: Pick your preferred battle environment
4. **Combat**: Use WASD for movement, engage enemies, manage ammunition
5. **Strategy**: Collect power-ups, use special abilities, and survive!

## Contributing

We welcome contributions to BattleArena Game! Please read our contributing guidelines before submitting pull requests.

### Development Guidelines

- Follow C# coding standards
- Add unit tests for new features
- Update documentation for API changes
- Ensure cross-platform compatibility

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

- **Developer**: [Your Name]
- **Email**: [your.email@example.com]
- **GitHub**: [@yourusername](https://github.com/yourusername)
- **Project Link**: [https://github.com/yourusername/BattleArena-Game](https://github.com/yourusername/BattleArena-Game)

## Acknowledgments

- Unity Technologies for the game engine
- Community contributors and testers
- Open source asset creators

---

** Star this repository if you find it interesting!**

_Last updated: August 26, 2025_
