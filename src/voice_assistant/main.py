"""
主模块，负责启动应用程序
Main module, responsible for starting the application
"""
from .ui import create_ui
from .logger import logger
from .config import validate_configuration


def check_startup_configuration():
    """
    检查启动配置并显示警告
    Check startup configuration and display warnings
    """
    errors, warnings = validate_configuration()

    if errors:
        logger.error(
            "配置错误检测到，应用可能无法正常工作 | Configuration errors detected, application may not work properly"
        )
        for error in errors:
            logger.error(f"- {error}")
        print("\n❌ 配置错误 | Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
        print("\n请检查您的 .env 文件配置 | Please check your .env file configuration\n")

    if warnings:
        logger.warning("配置警告检测到 | Configuration warnings detected")
        for warning in warnings:
            logger.warning(f"- {warning}")
        print("\n⚠️  配置警告 | Configuration Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
        print("")

    if not errors and not warnings:
        logger.info("配置检查通过 | Configuration check passed")
        print("✅ 配置检查通过 | Configuration check passed")

    return len(errors) == 0


def main():
    """
    主函数，启动应用程序
    Main function, starts the application
    """
    print("🎤 启动语音助手应用 | Starting Voice Assistant Application")
    print("=" * 60)

    logger.info("启动语音助手应用 | Starting voice assistant application")

    # 检查配置 | Check configuration
    config_valid = check_startup_configuration()

    if not config_valid:
        print("⚠️  检测到配置错误，但应用仍将启动。请在使用前修复配置问题。")
        print(
            "   Configuration errors detected, but application will still start. Please fix configuration issues before use."
        )
        print("")

    try:
        demo = create_ui()
        print("🌐 正在启动Web界面... | Starting web interface...")
        demo.launch(share=False)
    except Exception as e:
        logger.error(f"启动应用失败: {str(e)} | Failed to start application: {str(e)}")
        print(f"\n❌ 启动失败 | Startup failed: {str(e)}")
        print("请检查错误日志和配置 | Please check error logs and configuration")
    finally:
        logger.info("应用程序已关闭 | Application closed")
        print("\n👋 应用程序已关闭 | Application closed")


if __name__ == "__main__":
    main()
