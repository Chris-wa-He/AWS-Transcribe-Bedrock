#!/usr/bin/env python3
"""
配置测试脚本
Configuration test script
"""
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Import after path modification
from voice_assistant.config import get_configuration_status  # noqa: E402


def main():
    """测试配置并显示详细信息"""
    print("🔧 配置测试 | Configuration Test")
    print("=" * 50)

    # 获取配置状态
    status = get_configuration_status()

    # 显示配置状态
    if status["valid"]:
        print("✅ 配置验证通过 | Configuration validation passed")
    else:
        print("❌ 配置验证失败 | Configuration validation failed")
        print("\n错误 | Errors:")
        for error in status["errors"]:
            print(f"  - {error}")

    if status["warnings"]:
        print("\n⚠️  警告 | Warnings:")
        for warning in status["warnings"]:
            print(f"  - {warning}")

    # 显示当前配置
    print("\n📋 当前配置 | Current Configuration:")
    print("-" * 30)
    for key, value in status["config"].items():
        print(f"{key}: {value}")

    # 检查.env文件
    print("\n📄 .env文件检查 | .env File Check:")
    print("-" * 30)
    if os.path.exists(".env"):
        print("✅ .env文件存在 | .env file exists")
        with open(".env", "r") as f:
            lines = f.readlines()
            print(f"📝 包含 {len(lines)} 行配置 | Contains {len(lines)} configuration lines")
    else:
        print("❌ .env文件不存在 | .env file does not exist")
        print("💡 请从 .env.example 复制并配置 | Please copy from .env.example and configure")

    # 检查.env.example文件
    if os.path.exists(".env.example"):
        print("✅ .env.example文件存在 | .env.example file exists")
    else:
        print("❌ .env.example文件不存在 | .env.example file does not exist")

    # 返回状态码
    return 0 if status["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
