######################載入套件######################
import pygame
import sys
import traceback
from src.core.game_engine import GameEngine

######################主程式執行點######################


def main():
    """
    主程式進入點\n
    \n
    創建遊戲引擎實例並開始運行\n
    """
    try:
        # 創建並運行遊戲
        print("🎮 開始初始化遊戲...")
        game_engine = GameEngine()
        print("🎮 遊戲初始化完成，開始運行...")
        game_engine.run()

    except Exception as e:
        print(f"遊戲運行發生錯誤: {e}")
        print("詳細錯誤信息:")
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)


# 直接執行主程式
main()
