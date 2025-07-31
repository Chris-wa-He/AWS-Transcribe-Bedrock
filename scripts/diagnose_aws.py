#!/usr/bin/env python3
"""
AWS凭证诊断脚本
AWS Credentials Diagnostic Script
"""
import sys
import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from voice_assistant.config import get_configuration_status, S3_BUCKET_NAME  # noqa: E402


def test_aws_credentials():
    """测试AWS凭证配置"""
    print("🔍 AWS凭证诊断 | AWS Credentials Diagnosis")
    print("=" * 60)
    
    # 1. 检查环境变量
    print("\n1. 📋 环境变量检查 | Environment Variables Check:")
    print("-" * 40)
    
    env_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY', 
        'AWS_DEFAULT_REGION',
        'AWS_REGION',
        'AWS_PROFILE'
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            if 'KEY' in var:
                # 隐藏敏感信息
                display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            else:
                display_value = value
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ❌ {var}: 未设置 | Not set")
    
    # 2. 检查.env文件配置
    print("\n2. 📄 .env文件配置 | .env File Configuration:")
    print("-" * 40)
    
    try:
        status = get_configuration_status()
        aws_region = os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION') or 'Not set'
        print(f"   📍 AWS Region: {aws_region}")
        print(f"   🪣 S3 Bucket: {S3_BUCKET_NAME}")
        print(f"   ✅ 配置状态 | Config status: {'Valid' if status['valid'] else 'Invalid'}")
    except Exception as e:
        print(f"   ❌ 配置读取失败 | Config read failed: {e}")
    
    # 3. 测试AWS STS连接
    print("\n3. 🔐 AWS STS连接测试 | AWS STS Connection Test:")
    print("-" * 40)
    
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"   ✅ 连接成功 | Connection successful")
        print(f"   👤 用户ARN | User ARN: {identity.get('Arn')}")
        print(f"   🆔 账户ID | Account ID: {identity.get('Account')}")
    except NoCredentialsError:
        print("   ❌ 未找到AWS凭证 | No AWS credentials found")
        print("   💡 请配置AWS凭证 | Please configure AWS credentials")
        return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        print(f"   ❌ AWS错误 | AWS Error: {error_code}")
        print(f"   📝 错误信息 | Error message: {error_msg}")
        return False
    except Exception as e:
        print(f"   ❌ 连接失败 | Connection failed: {e}")
        return False
    
    # 4. 测试Bedrock服务
    print("\n4. 🤖 Bedrock服务测试 | Bedrock Service Test:")
    print("-" * 40)
    
    try:
        bedrock = boto3.client('bedrock', region_name='us-east-1')
        models = bedrock.list_foundation_models()
        model_count = len(models.get('modelSummaries', []))
        print(f"   ✅ Bedrock连接成功 | Bedrock connection successful")
        print(f"   📊 可用模型数量 | Available models: {model_count}")
        
        # 检查Claude和Nova模型
        claude_models = [m for m in models['modelSummaries'] if 'claude' in m['modelId'].lower()]
        nova_models = [m for m in models['modelSummaries'] if 'nova' in m['modelId'].lower()]
        
        print(f"   🧠 Claude模型 | Claude models: {len(claude_models)}")
        print(f"   🌟 Nova模型 | Nova models: {len(nova_models)}")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        print(f"   ❌ Bedrock错误 | Bedrock Error: {error_code}")
        print(f"   📝 错误信息 | Error message: {error_msg}")
        
        if error_code == 'UnrecognizedClientException':
            print("   💡 建议 | Suggestion: 检查AWS凭证和区域配置")
        elif error_code == 'AccessDeniedException':
            print("   💡 建议 | Suggestion: 检查IAM权限，确保有Bedrock访问权限")
            
        return False
    except Exception as e:
        print(f"   ❌ Bedrock测试失败 | Bedrock test failed: {e}")
        return False
    
    # 5. 测试S3服务
    print("\n5. 🪣 S3服务测试 | S3 Service Test:")
    print("-" * 40)
    
    try:
        bucket_name = S3_BUCKET_NAME
        
        if not bucket_name or bucket_name == 'your-s3-bucket-name':
            print("   ⚠️  S3存储桶未配置 | S3 bucket not configured")
            print("   💡 请在.env文件中设置S3_BUCKET_NAME")
        else:
            s3 = boto3.client('s3')
            s3.head_bucket(Bucket=bucket_name)
            print(f"   ✅ S3存储桶访问成功 | S3 bucket access successful")
            print(f"   🪣 存储桶名称 | Bucket name: {bucket_name}")
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"   ❌ S3错误 | S3 Error: {error_code}")
        if error_code == '404':
            print("   💡 存储桶不存在 | Bucket does not exist")
        elif error_code == '403':
            print("   💡 没有存储桶访问权限 | No bucket access permission")
    except Exception as e:
        print(f"   ❌ S3测试失败 | S3 test failed: {e}")
    
    print("\n" + "=" * 60)
    return True


def print_fix_suggestions():
    """打印修复建议"""
    print("\n🛠️  修复建议 | Fix Suggestions:")
    print("=" * 60)
    
    print("\n1. 配置AWS凭证 | Configure AWS Credentials:")
    print("   方法A | Method A: 使用AWS CLI")
    print("   aws configure")
    print()
    print("   方法B | Method B: 编辑.env文件")
    print("   # 替换为真实凭证 | Replace with real credentials")
    print("   AWS_ACCESS_KEY_ID=AKIA...")
    print("   AWS_SECRET_ACCESS_KEY=...")
    print("   AWS_REGION=us-east-1")
    
    print("\n2. 检查IAM权限 | Check IAM Permissions:")
    print("   确保用户有以下权限 | Ensure user has these permissions:")
    print("   - bedrock:ListFoundationModels")
    print("   - bedrock:InvokeModel") 
    print("   - transcribe:*")
    print("   - s3:GetObject, s3:PutObject")
    
    print("\n3. 验证区域设置 | Verify Region Settings:")
    print("   确保AWS_REGION与资源区域匹配")
    print("   Bedrock在某些区域可能不可用")
    
    print(f"\n📖 详细指南 | Detailed Guide:")
    print("   查看: docs/AWS_CREDENTIALS_SETUP.md")


def main():
    """主函数"""
    success = test_aws_credentials()
    
    if not success:
        print_fix_suggestions()
        sys.exit(1)
    else:
        print("\n🎉 所有AWS服务测试通过！| All AWS service tests passed!")
        print("   应用程序应该可以正常运行 | Application should work normally")


if __name__ == "__main__":
    main()