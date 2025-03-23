"""
配置模块，负责加载环境变量和提供配置信息
Configuration module, responsible for loading environment variables and providing configuration information
"""
import os
from dotenv import load_dotenv

# 加载环境变量 | Load environment variables
load_dotenv()

# AWS配置 | AWS configuration
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

# Transcribe支持的音频格式 | Audio formats supported by Transcribe
SUPPORTED_AUDIO_FORMATS = ['mp3', 'mp4', 'wav', 'flac', 'ogg', 'amr', 'webm']
DEFAULT_AUDIO_FORMAT = 'wav'

# Bedrock模型配置 | Bedrock model configuration
BEDROCK_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
BEDROCK_MAX_TOKENS = 1000

# 提示词模板 | Prompt template
OPTIMIZATION_PROMPT = """Please optimize and correct the following transcribed text. 
Fix any grammatical errors, improve clarity, and make it more coherent while 
preserving the original meaning:

{text}

Optimized text:"""
