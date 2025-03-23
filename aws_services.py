"""
AWS服务模块，负责与AWS Transcribe和Bedrock交互
"""
import json
import time
import urllib.request
from datetime import datetime
import os
import boto3

from config import (
    S3_BUCKET_NAME, 
    AUDIO_FORMAT,
    BEDROCK_MODEL_ID, 
    BEDROCK_MAX_TOKENS, 
    BEDROCK_VERSION,
    OPTIMIZATION_PROMPT
)

# 初始化AWS客户端
s3_client = boto3.client('s3')
transcribe_client = boto3.client('transcribe')
bedrock_client = boto3.client('bedrock-runtime')

def upload_to_s3(audio_path):
    """上传音频文件到S3并返回S3 URI"""
    try:
        s3_key = f"audio/{os.path.basename(audio_path)}"
        s3_client.upload_file(audio_path, S3_BUCKET_NAME, s3_key)
        return f"s3://{S3_BUCKET_NAME}/{s3_key}"
    except Exception as e:
        raise Exception(f"上传到S3失败: {str(e)}")

def transcribe_audio(s3_uri):
    """使用AWS Transcribe转录音频并返回转录文本"""
    try:
        # 创建转录任务
        job_name = f"transcription-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 使用自动语言识别
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': s3_uri},
            MediaFormat=AUDIO_FORMAT,
            IdentifyLanguage=True  # 启用自动语言识别
        )
        
        # 等待转录完成
        while True:
            status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            time.sleep(1)
            
        if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
            transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            
            # 获取转录结果
            response = urllib.request.urlopen(transcript_uri)
            transcript_data = json.loads(response.read().decode('utf-8'))
            
            # 获取识别的语言（可选，用于日志或显示）
            identified_language = status['TranscriptionJob'].get('LanguageCode', 'unknown')
            print(f"识别的语言: {identified_language}")
            
            return transcript_data['results']['transcripts'][0]['transcript']
        else:
            raise Exception("转录失败")
            
    except Exception as e:
        raise Exception(f"转录音频失败: {str(e)}")

def optimize_with_bedrock(text):
    """使用AWS Bedrock优化文本"""
    try:
        # 准备提示词
        prompt = OPTIMIZATION_PROMPT.format(text=text)
        
        # 调用Bedrock模型
        response = bedrock_client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps({
                "anthropic_version": BEDROCK_VERSION,
                "max_tokens": BEDROCK_MAX_TOKENS,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        
        response_body = json.loads(response['body'].read().decode('utf-8'))
        return response_body['content'][0]['text']
        
    except Exception as e:
        raise Exception(f"使用Bedrock优化文本失败: {str(e)}")

def process_audio(audio_file):
    """处理音频文件并返回转录和优化结果"""
    try:
        # 上传到S3
        s3_uri = upload_to_s3(audio_file)
        
        # 转录音频
        transcript_text = transcribe_audio(s3_uri)
        
        # 使用Bedrock优化
        optimized_text = optimize_with_bedrock(transcript_text)
        
        return transcript_text, optimized_text
    except Exception as e:
        return f"处理错误: {str(e)}", ""
