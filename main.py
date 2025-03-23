"""
主模块，负责启动应用程序
Main module, responsible for starting the application
"""
from ui import create_ui
from logger import logger

def main():
    """
    主函数，启动应用程序
    Main function, starts the application
    """
    logger.info("启动语音助手应用 | Starting voice assistant application")
    demo = create_ui()
    demo.launch(share=False)
    logger.info("应用程序已关闭 | Application closed")

if __name__ == "__main__":
    main()
