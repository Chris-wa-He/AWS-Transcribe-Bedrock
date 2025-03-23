"""
主程序入口，负责启动应用程序
"""
from ui import create_ui

if __name__ == "__main__":
    demo = create_ui()
    demo.launch(share=False)
