#!/usr/bin/env python3
"""
模型列表测试脚本
Model list test script
"""
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Import after path modification
from voice_assistant.aws_services import get_available_models  # noqa: E402
from voice_assistant.config import BEDROCK_MODEL_ID  # noqa: E402


def main():
    """测试模型列表功能"""
    print("🤖 Bedrock模型列表测试 | Bedrock Model List Test")
    print("=" * 60)

    print(f"📋 默认模型ID | Default Model ID: {BEDROCK_MODEL_ID}")
    print()

    try:
        models = get_available_models()
        print(
            f"✅ 成功获取到 {len(models)} 个Claude和Nova模型 | Successfully got {len(models)} Claude and Nova models"
        )
        print()

        # 按系列分组显示 | Display grouped by series
        claude_models = [m for m in models if "claude" in m["name"].lower()]
        nova_models = [m for m in models if "nova" in m["name"].lower()]

        if claude_models:
            print("🧠 Claude系列模型 | Claude Series Models:")
            for i, model in enumerate(claude_models, 1):
                print(f"  {i}. {model['name']}")
                print(f"     ID: {model['id']}")
                if model["id"] == BEDROCK_MODEL_ID:
                    print("     ⭐ (默认模型 | Default Model)")
                print()

        if nova_models:
            print("🌟 Nova系列模型 | Nova Series Models:")
            for i, model in enumerate(nova_models, 1):
                print(f"  {i}. {model['name']}")
                print(f"     ID: {model['id']}")
                if model["id"] == BEDROCK_MODEL_ID:
                    print("     ⭐ (默认模型 | Default Model)")
                print()

        # 验证默认模型是否在列表中 | Verify default model is in the list
        default_model_found = any(m["id"] == BEDROCK_MODEL_ID for m in models)
        if default_model_found:
            print("✅ 默认模型在可用列表中 | Default model is in available list")
        else:
            print("⚠️  默认模型不在可用列表中 | Default model is not in available list")

        # 显示模型统计 | Show model statistics
        print(f"\n📊 模型统计 | Model Statistics:")
        print(f"   Claude模型数量 | Claude models: {len(claude_models)}")
        print(f"   Nova模型数量 | Nova models: {len(nova_models)}")
        print(f"   总计 | Total: {len(models)}")

    except Exception as e:
        print(f"❌ 获取模型列表失败 | Failed to get model list: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
