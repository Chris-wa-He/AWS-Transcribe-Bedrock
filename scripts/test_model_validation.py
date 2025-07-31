#!/usr/bin/env python3
"""
模型验证测试脚本
Model validation test script
"""
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Import after path modification
from voice_assistant.aws_services import (  # noqa: E402
    is_model_supported_for_on_demand,
    validate_model_for_inference,
    UNSUPPORTED_ON_DEMAND_MODELS
)
from voice_assistant.config import BEDROCK_MODEL_ID  # noqa: E402


def test_model_validation():
    """测试模型验证功能"""
    print("🧪 模型验证测试 | Model Validation Test")
    print("=" * 60)
    
    # 测试支持的模型
    print("\n✅ 支持按需调用的模型 | Models supporting on-demand throughput:")
    supported_models = [
        "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "anthropic.claude-3-sonnet-20240229-v1:0",
        "anthropic.claude-3-haiku-20240307-v1:0",
        "amazon.nova-pro-v1:0",
        "amazon.nova-lite-v1:0",
        "amazon.nova-micro-v1:0",
    ]
    
    for model in supported_models:
        is_supported = is_model_supported_for_on_demand(model)
        validated = validate_model_for_inference(model)
        status = "✅" if is_supported else "❌"
        print(f"   {status} {model}")
        if model != validated:
            print(f"      → 验证后: {validated}")
    
    # 测试不支持的模型
    print("\n❌ 不支持按需调用的模型 | Models NOT supporting on-demand throughput:")
    unsupported_models = [
        "anthropic.claude-3-7-sonnet-20250219-v1:0",
        "anthropic.claude-opus-4-20250514-v1:0", 
        "anthropic.claude-sonnet-4-20250514-v1:0",
    ]
    
    for model in unsupported_models:
        is_supported = is_model_supported_for_on_demand(model)
        validated = validate_model_for_inference(model)
        status = "✅" if is_supported else "❌"
        print(f"   {status} {model}")
        if model != validated:
            print(f"      → 验证后切换到: {validated}")
    
    # 测试黑名单
    print(f"\n🚫 黑名单模型数量 | Blacklisted models count: {len(UNSUPPORTED_ON_DEMAND_MODELS)}")
    for model in UNSUPPORTED_ON_DEMAND_MODELS:
        print(f"   - {model}")
    
    # 测试默认模型
    print(f"\n🎯 默认模型 | Default model: {BEDROCK_MODEL_ID}")
    default_supported = is_model_supported_for_on_demand(BEDROCK_MODEL_ID)
    print(f"   支持状态 | Support status: {'✅ 支持' if default_supported else '❌ 不支持'}")
    
    # 测试边界情况
    print("\n🔍 边界情况测试 | Edge case testing:")
    edge_cases = [
        None,  # 空值
        "",    # 空字符串
        "invalid-model-id",  # 无效模型ID
    ]
    
    for case in edge_cases:
        try:
            validated = validate_model_for_inference(case)
            print(f"   输入: {repr(case)} → 输出: {validated}")
        except Exception as e:
            print(f"   输入: {repr(case)} → 错误: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 模型验证测试完成 | Model validation test completed")


def main():
    """主函数"""
    test_model_validation()


if __name__ == "__main__":
    main()