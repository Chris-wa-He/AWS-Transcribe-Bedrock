"""
配置模块，负责加载环境变量和提供配置信息
Configuration module, responsible for loading environment variables and providing configuration information
"""
import os
from dotenv import load_dotenv

# 加载环境变量 | Load environment variables
load_dotenv()

# AWS配置 | AWS configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Transcribe支持的音频格式 | Audio formats supported by Transcribe
SUPPORTED_AUDIO_FORMATS = ["mp3", "mp4", "wav", "flac", "ogg", "amr", "webm"]
DEFAULT_AUDIO_FORMAT = "wav"

# Bedrock模型配置 | Bedrock model configuration
BEDROCK_MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0"  # 默认使用Claude 3.5 Sonnet
BEDROCK_MAX_TOKENS = 1000

# 提示词模板 | Prompt template
OPTIMIZATION_PROMPT = """Please optimize and correct the following transcribed text. 
Fix any grammatical errors, improve clarity, and make it more coherent while 
preserving the original meaning:

{text}

Optimized text:"""


def validate_configuration():
    """
    验证应用程序配置是否完整
    Validate if application configuration is complete
    """
    errors = []
    warnings = []

    # 检查必需的环境变量 | Check required environment variables
    if not S3_BUCKET_NAME:
        errors.append(
            "S3_BUCKET_NAME 环境变量未设置 | S3_BUCKET_NAME environment variable not set"
        )

    # 检查AWS凭证 | Check AWS credentials
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
    aws_profile = os.getenv("AWS_PROFILE")

    if not aws_profile:  # 如果没有使用AWS Profile
        if not aws_access_key:
            warnings.append(
                "AWS_ACCESS_KEY_ID 环境变量未设置，将尝试使用默认凭证 | AWS_ACCESS_KEY_ID environment variable not set, will try to use default credentials"
            )
        if not aws_secret_key:
            warnings.append(
                "AWS_SECRET_ACCESS_KEY 环境变量未设置，将尝试使用默认凭证 | AWS_SECRET_ACCESS_KEY environment variable not set, will try to use default credentials"
            )

    if not aws_region:
        warnings.append(
            "AWS_REGION 环境变量未设置，将使用默认区域 | AWS_REGION environment variable not set, will use default region"
        )

    return errors, warnings


def get_configuration_status():
    """
    获取配置状态的详细信息
    Get detailed configuration status information
    """
    errors, warnings = validate_configuration()

    status = {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "config": {
            "s3_bucket": S3_BUCKET_NAME or "未配置 | Not configured",
            "aws_region": os.getenv("AWS_REGION")
            or os.getenv("AWS_DEFAULT_REGION")
            or "未配置 | Not configured",
            "aws_profile": os.getenv("AWS_PROFILE") or "未使用 | Not used",
            "bedrock_model": BEDROCK_MODEL_ID,
            "supported_formats": ", ".join(SUPPORTED_AUDIO_FORMATS),
        },
    }

    return status
