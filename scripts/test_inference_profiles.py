#!/usr/bin/env python3
"""
测试inference profile功能
Test inference profile functionality
"""
import os
import sys
import json
import boto3
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from voice_assistant.aws_services import get_boto3_session
from dotenv import load_dotenv

def test_inference_profiles():
    """测试inference profile功能"""
    print("=== 测试 Inference Profile 功能 ===")
    print("=== Testing Inference Profile Functionality ===\n")
    
    # 加载环境变量
    load_dotenv()
    
    # 获取boto3会话
    session = get_boto3_session()
    bedrock_client = session.client("bedrock-runtime")
    bedrock_management = session.client("bedrock")
    
    # 测试消息
    test_message = "Hello, this is a test message for inference profile."
    
    # 获取所有可用的基础模型
    print("1. 获取所有可用的基础模型...")
    try:
        response = bedrock_management.list_foundation_models()
        models = response.get("modelSummaries", [])
        
        # 过滤Claude和Nova模型
        claude_nova_models = []
        for model in models:
            model_id = model.get("modelId", "")
            model_name = model.get("modelName", "")
            provider_name = model.get("providerName", "")
            
            if model.get("outputModalities", []) == ["TEXT"]:
                is_claude = (
                    "claude" in model_id.lower()
                    or "claude" in model_name.lower()
                    or provider_name.lower() == "anthropic"
                )
                is_nova = "nova" in model_id.lower() or "nova" in model_name.lower()
                
                if is_claude or is_nova:
                    claude_nova_models.append({
                        "id": model_id,
                        "name": model_name,
                        "provider": provider_name
                    })
        
        print(f"找到 {len(claude_nova_models)} 个Claude和Nova模型:")
        for model in claude_nova_models:
            print(f"  - {model['name']} ({model['id']})")
        
    except Exception as e:
        print(f"获取模型列表失败: {e}")
        return
    
    print("\n2. 测试直接模型调用...")
    
    # 测试一些常见模型的直接调用
    test_models = [
        "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "anthropic.claude-3-7-sonnet-20250219-v1:0",  # 这个应该会失败
        "anthropic.claude-opus-4-20250514-v1:0",      # 这个应该会失败
        "amazon.nova-pro-v1:0",
        "amazon.nova-lite-v1:0"
    ]
    
    direct_call_results = {}
    
    for model_id in test_models:
        print(f"\n  测试模型: {model_id}")
        try:
            response = bedrock_client.converse(
                modelId=model_id,
                messages=[{"role": "user", "content": [{"text": test_message}]}],
                inferenceConfig={
                    "maxTokens": 100,
                    "temperature": 0.0,
                    "topP": 1.0,
                },
            )
            
            output = response.get("output", {})
            message = output.get("message", {})
            content = message.get("content", [])
            
            result_text = ""
            for item in content:
                if "text" in item:
                    result_text += item["text"]
            
            direct_call_results[model_id] = {
                "success": True,
                "response": result_text[:100] + "..." if len(result_text) > 100 else result_text
            }
            print(f"    ✅ 成功: {result_text[:50]}...")
            
        except Exception as e:
            direct_call_results[model_id] = {
                "success": False,
                "error": str(e)
            }
            print(f"    ❌ 失败: {str(e)}")
    
    print("\n3. 测试inference profile调用...")
    
    # 测试inference profile调用
    inference_profiles = [
        "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        "us.anthropic.claude-opus-4-20250514-v1:0",
        "us.anthropic.claude-sonnet-4-20250514-v1:0",
        "us.amazon.nova-pro-v1:0",
        "us.amazon.nova-lite-v1:0"
    ]
    
    inference_profile_results = {}
    
    for profile_id in inference_profiles:
        print(f"\n  测试inference profile: {profile_id}")
        try:
            response = bedrock_client.converse(
                modelId=profile_id,
                messages=[{"role": "user", "content": [{"text": test_message}]}],
                inferenceConfig={
                    "maxTokens": 100,
                    "temperature": 0.0,
                    "topP": 1.0,
                },
            )
            
            output = response.get("output", {})
            message = output.get("message", {})
            content = message.get("content", [])
            
            result_text = ""
            for item in content:
                if "text" in item:
                    result_text += item["text"]
            
            inference_profile_results[profile_id] = {
                "success": True,
                "response": result_text[:100] + "..." if len(result_text) > 100 else result_text
            }
            print(f"    ✅ 成功: {result_text[:50]}...")
            
        except Exception as e:
            inference_profile_results[profile_id] = {
                "success": False,
                "error": str(e)
            }
            print(f"    ❌ 失败: {str(e)}")
    
    print("\n4. 结果总结...")
    print("\n直接模型调用结果:")
    for model_id, result in direct_call_results.items():
        status = "✅ 成功" if result["success"] else "❌ 失败"
        print(f"  {model_id}: {status}")
        if not result["success"]:
            print(f"    错误: {result['error']}")
    
    print("\nInference Profile调用结果:")
    for profile_id, result in inference_profile_results.items():
        status = "✅ 成功" if result["success"] else "❌ 失败"
        print(f"  {profile_id}: {status}")
        if not result["success"]:
            print(f"    错误: {result['error']}")
    
    # 分析结果
    print("\n5. 分析结果...")
    
    # 检查哪些模型只能通过inference profile调用
    only_inference_profile = []
    both_work = []
    neither_work = []
    
    for model_id in test_models:
        # 找到对应的inference profile
        profile_id = None
        if "anthropic.claude-3-5-sonnet-20241022-v2:0" in model_id:
            profile_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        elif "anthropic.claude-3-7-sonnet-20250219-v1:0" in model_id:
            profile_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
        elif "anthropic.claude-opus-4-20250514-v1:0" in model_id:
            profile_id = "us.anthropic.claude-opus-4-20250514-v1:0"
        elif "amazon.nova-pro-v1:0" in model_id:
            profile_id = "us.amazon.nova-pro-v1:0"
        elif "amazon.nova-lite-v1:0" in model_id:
            profile_id = "us.amazon.nova-lite-v1:0"
        
        if profile_id:
            direct_success = direct_call_results.get(model_id, {}).get("success", False)
            profile_success = inference_profile_results.get(profile_id, {}).get("success", False)
            
            if not direct_success and profile_success:
                only_inference_profile.append(model_id)
            elif direct_success and profile_success:
                both_work.append(model_id)
            elif not direct_success and not profile_success:
                neither_work.append(model_id)
    
    print(f"\n只能通过inference profile调用的模型 ({len(only_inference_profile)}):")
    for model in only_inference_profile:
        print(f"  - {model}")
    
    print(f"\n两种方式都可以调用的模型 ({len(both_work)}):")
    for model in both_work:
        print(f"  - {model}")
    
    print(f"\n两种方式都无法调用的模型 ({len(neither_work)}):")
    for model in neither_work:
        print(f"  - {model}")
    
    # 结论
    print("\n6. 结论:")
    if len(only_inference_profile) > 0:
        print("✅ 发现有些模型只能通过inference profile调用")
        print("   建议修改代码以支持inference profile模式")
    else:
        print("❌ 没有发现只能通过inference profile调用的模型")
        print("   当前的黑名单机制可能仍然需要")
    
    if len(both_work) > 0:
        print("✅ 发现有些模型两种方式都可以调用")
        print("   可以考虑统一使用inference profile以获得更好的性能")

if __name__ == "__main__":
    test_inference_profiles()