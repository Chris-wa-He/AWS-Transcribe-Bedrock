"""
配置模块，负责加载环境变量和提供配置信息
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# AWS配置
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

# Transcribe支持的音频格式
SUPPORTED_AUDIO_FORMATS = ['mp3', 'mp4', 'wav', 'flac', 'ogg', 'amr', 'webm']
DEFAULT_AUDIO_FORMAT = 'wav'

# Bedrock模型配置
BEDROCK_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
BEDROCK_MAX_TOKENS = 1000

# 提示词模板
OPTIMIZATION_PROMPT = """Please optimize and correct the following transcribed text. 
Fix any grammatical errors, improve clarity, and make it more coherent while 
preserving the original meaning:

{text}

Optimized text:"""
