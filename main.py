"""
主模块，负责启动应用程序
"""
from ui import create_ui
from logger import logger

def main():
    """主函数，启动应用程序"""
    logger.info("启动语音助手应用")
    demo = create_ui()
    demo.launch(share=False)
    logger.info("应用程序已关闭")

if __name__ == "__main__":
    main()
