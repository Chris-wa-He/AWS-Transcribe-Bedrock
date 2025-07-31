#!/usr/bin/env python3
"""
测试新的inference profile fallback机制
Test new inference profile fallback mechanism
"""
import os
import sys
import json
import boto3
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from voice_assistant.aws_services import try_model_with_fallback, get_boto3_session
from dotenv import load_dotenv

def test_fallback_mechanism():
    """测试新的fallback机制"""
    print("=== 测试新的 Inference Profile Fallback 机制 ===")
    print("=== Testing New Inference Profile Fallback Mechanism ===\n")
    
    # 加载环境变量
    load_dotenv()
    
    # 获取boto3会话
    session = get_boto3_session()
    bedrock_client = session.client("bedrock-runtime")
    
    # 测试消息
    test_message = "Please optimize this text: Hello world, this is a test."
    
    # 准备调用参数
    messages = [{"role": "user", "content": [{"text": test_message}]}]
    inference_config = {
        "maxTokens": 100,
        "temperature": 0.0,
        "topP": 1.0,
    }
    
    # 测试不同类型的模型
    test_cases = [
        {
            "name": "需要inference profile的Claude 3.5 Sonnet v2",
            "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "expected_fallback": True
        },
        {
            "name": "需要inference profile的Claude 3.7 Sonnet",
            "model_id": "anthropic.claude-3-7-sonnet-20250219-v1:0",
            "expected_fallback": True
        },
        {
            "name": "支持直接调用的Nova Pro",
            "model_id": "amazon.nova-pro-v1:0",
            "expected_fallback": False
        },
        {
            "name": "支持直接调用的Nova Lite",
            "model_id": "amazon.nova-lite-v1:0",
            "expected_fallback": False
        },
        {
            "name": "已经是inference profile格式的Claude 3.5 Sonnet",
            "model_id": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            "expected_fallback": False
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. 测试: {test_case['name']}")
        print(f"   模型ID: {test_case['model_id']}")
        
        try:
            response, actual_model_id = try_model_with_fallback(
                test_case['model_id'], 
                bedrock_client, 
                messages, 
                inference_config
            )
            
            # 检查是否发生了fallback
            fallback_occurred = actual_model_id != test_case['model_id']
            
            # 提取响应文本
            output = response.get("output", {})
            message = output.get("message", {})
            content = message.get("content", [])
            
            result_text = ""
            for item in content:
                if "text" in item:
                    result_text += item["text"]
            
            results.append({
                "test_case": test_case,
                "success": True,
                "actual_model_id": actual_model_id,
                "fallback_occurred": fallback_occurred,
                "response_preview": result_text[:100] + "..." if len(result_text) > 100 else result_text
            })
            
            print(f"   ✅ 成功")
            print(f"   实际使用的模型: {actual_model_id}")
            if fallback_occurred:
                print(f"   🔄 发生了fallback (从 {test_case['model_id']} 到 {actual_model_id})")
            else:
                print(f"   ➡️  直接调用成功")
            print(f"   响应预览: {result_text[:50]}...")
            
        except Exception as e:
            results.append({
                "test_case": test_case,
                "success": False,
                "error": str(e),
                "fallback_occurred": False
            })
            
            print(f"   ❌ 失败: {str(e)}")
        
        print()
    
    # 总结结果
    print("=" * 60)
    print("测试结果总结:")
    print("=" * 60)
    
    successful_tests = [r for r in results if r["success"]]
    failed_tests = [r for r in results if not r["success"]]
    fallback_tests = [r for r in successful_tests if r["fallback_occurred"]]
    direct_tests = [r for r in successful_tests if not r["fallback_occurred"]]
    
    print(f"总测试数: {len(results)}")
    print(f"成功: {len(successful_tests)}")
    print(f"失败: {len(failed_tests)}")
    print(f"发生fallback: {len(fallback_tests)}")
    print(f"直接调用成功: {len(direct_tests)}")
    
    print("\n发生fallback的测试:")
    for result in fallback_tests:
        test_case = result["test_case"]
        print(f"  - {test_case['name']}")
        print(f"    {test_case['model_id']} → {result['actual_model_id']}")
        expected = test_case.get("expected_fallback", False)
        if expected:
            print(f"    ✅ 符合预期 (预期会fallback)")
        else:
            print(f"    ⚠️  意外的fallback (预期直接调用)")
    
    print("\n直接调用成功的测试:")
    for result in direct_tests:
        test_case = result["test_case"]
        print(f"  - {test_case['name']}")
        print(f"    {result['actual_model_id']}")
        expected = test_case.get("expected_fallback", False)
        if not expected:
            print(f"    ✅ 符合预期 (预期直接调用)")
        else:
            print(f"    ⚠️  意外的直接调用 (预期会fallback)")
    
    if failed_tests:
        print("\n失败的测试:")
        for result in failed_tests:
            test_case = result["test_case"]
            print(f"  - {test_case['name']}")
            print(f"    错误: {result['error']}")
    
    # 验证机制是否按预期工作
    print("\n机制验证:")
    expected_fallbacks = [r for r in results if r["success"] and r["test_case"].get("expected_fallback", False)]
    actual_fallbacks = [r for r in results if r["success"] and r["fallback_occurred"]]
    
    if len(expected_fallbacks) == len(actual_fallbacks):
        print("✅ Fallback机制工作正常 - 所有预期需要fallback的模型都成功fallback了")
    else:
        print("⚠️  Fallback机制可能有问题 - fallback行为与预期不符")
    
    # 检查是否所有测试都成功
    if len(failed_tests) == 0:
        print("✅ 所有测试都成功 - 新的fallback机制工作正常")
    else:
        print(f"❌ 有 {len(failed_tests)} 个测试失败 - 需要进一步调试")

if __name__ == "__main__":
    test_fallback_mechanism()