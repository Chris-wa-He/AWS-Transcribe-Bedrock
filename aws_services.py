"""
AWS服务模块，负责与AWS Transcribe和Bedrock交互
"""
import json
import time
import urllib.request
from datetime import datetime
import os
import boto3
import mimetypes

from config import (
    S3_BUCKET_NAME, 
    SUPPORTED_AUDIO_FORMATS,
    DEFAULT_AUDIO_FORMAT,
    BEDROCK_MODEL_ID, 
    BEDROCK_MAX_TOKENS,
    OPTIMIZATION_PROMPT
)

# 初始化AWS客户端
s3_client = boto3.client('s3')
transcribe_client = boto3.client('transcribe')
bedrock_client = boto3.client('bedrock-runtime')
bedrock_management = boto3.client('bedrock')

def get_available_models():
    """获取账户中可用的Bedrock模型列表"""
    try:
        # 获取所有可用的基础模型
        response = bedrock_management.list_foundation_models()
        
        # 过滤出支持文本生成的模型
        text_models = []
        for model in response.get('modelSummaries', []):
            model_id = model.get('modelId', '')
            # 只包含支持文本生成的模型
            if model.get('outputModalities', []) == ['TEXT']:
                # 添加模型ID和名称
                text_models.append({
                    'id': model_id,
                    'name': f"{model.get('providerName', 'Unknown')} - {model.get('modelName', 'Unknown')}"
                })
        
        # 按提供商和名称排序
        text_models.sort(key=lambda x: x['name'])
        
        return text_models
    except Exception as e:
        print(f"获取模型列表失败: {str(e)}")
        # 返回默认模型
        return [{'id': BEDROCK_MODEL_ID, 'name': 'Claude 3 Sonnet (默认)'}]

def get_file_extension(file_path):
    """获取文件扩展名"""
    _, extension = os.path.splitext(file_path)
    return extension[1:].lower() if extension else ""

def get_media_format(file_path):
    """根据文件路径确定媒体格式"""
    extension = get_file_extension(file_path)
    
    # 检查是否是支持的格式
    if extension in SUPPORTED_AUDIO_FORMATS:
        return extension
    
    # 尝试通过MIME类型判断
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        if mime_type.startswith('audio/'):
            format_from_mime = mime_type.split('/')[-1]
            if format_from_mime in SUPPORTED_AUDIO_FORMATS:
                return format_from_mime
    
    # 默认返回wav格式
    print(f"警告: 无法确定文件格式 '{file_path}'，使用默认格式 '{DEFAULT_AUDIO_FORMAT}'")
    return DEFAULT_AUDIO_FORMAT

def upload_to_s3(audio_path):
    """上传音频文件到S3并返回S3 URI"""
    try:
        s3_key = f"audio/{os.path.basename(audio_path)}"
        s3_client.upload_file(audio_path, S3_BUCKET_NAME, s3_key)
        return f"s3://{S3_BUCKET_NAME}/{s3_key}"
    except Exception as e:
        raise Exception(f"上传到S3失败: {str(e)}")

def transcribe_audio(s3_uri, audio_path):
    """使用AWS Transcribe转录音频并返回转录文本"""
    try:
        # 创建转录任务
        job_name = f"transcription-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 确定媒体格式
        media_format = get_media_format(audio_path)
        
        # 使用自动语言识别
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': s3_uri},
            MediaFormat=media_format,
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

def optimize_with_bedrock(text, model_id=None, custom_prompt=None):
    """使用AWS Bedrock的converse API优化文本"""
    # 如果没有指定模型ID，使用默认模型
    if not model_id:
        model_id = BEDROCK_MODEL_ID
    
    # 如果没有指定自定义提示词，使用默认提示词
    if not custom_prompt:
        prompt = OPTIMIZATION_PROMPT.format(text=text)
    else:
        # 确保自定义提示词中包含{text}占位符
        if "{text}" in custom_prompt:
            prompt = custom_prompt.format(text=text)
        else:
            # 如果没有占位符，将文本附加到提示词后面
            prompt = f"{custom_prompt}\n\n{text}"
    
    try:
        # 使用converse API调用Bedrock模型
        response = bedrock_client.converse(
            modelId=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            inferenceConfig={
                "maxTokens": BEDROCK_MAX_TOKENS,
                "temperature": 0.0,
                "topP": 1.0
            }
        )
        
        # 从响应中提取文本
        output = response.get("output", {})
        message = output.get("message", {})
        content = message.get("content", [])
        
        # 合并所有文本内容
        result_text = ""
        for item in content:
            if "text" in item:
                result_text += item["text"]
        
        return result_text if result_text else "无法获取优化文本"
        
    except Exception as e:
        # 如果converse API失败，回退到invoke_model API
        try:
            print(f"converse API失败: {str(e)}，尝试使用invoke_model API")
            
            # 检查模型提供商，不同提供商有不同的API格式
            provider = model_id.split('.')[0].lower()
            
            if provider == 'anthropic':
                # Anthropic模型使用特定的格式
                response = bedrock_client.invoke_model(
                    modelId=model_id,
                    body=json.dumps({
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": BEDROCK_MAX_TOKENS,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    })
                )
                
                # 解析响应
                response_body = json.loads(response['body'].read().decode('utf-8'))
                return response_body['content'][0]['text']
            
            elif provider == 'amazon':
                # Amazon Titan模型使用不同的格式
                response = bedrock_client.invoke_model(
                    modelId=model_id,
                    body=json.dumps({
                        "inputText": prompt,
                        "textGenerationConfig": {
                            "maxTokenCount": BEDROCK_MAX_TOKENS,
                            "temperature": 0,
                            "topP": 1
                        }
                    })
                )
                
                # 解析响应
                response_body = json.loads(response['body'].read().decode('utf-8'))
                return response_body.get('results', [{}])[0].get('outputText', "无法获取优化文本")
            
            else:
                # 其他模型使用通用格式
                response = bedrock_client.invoke_model(
                    modelId=model_id,
                    body=json.dumps({
                        "prompt": prompt,
                        "max_tokens": BEDROCK_MAX_TOKENS,
                        "temperature": 0
                    })
                )
                
                # 解析响应
                response_body = json.loads(response['body'].read().decode('utf-8'))
                return response_body.get('generation', "无法获取优化文本")
            
        except Exception as inner_e:
            raise Exception(f"使用Bedrock优化文本失败: 首先尝试converse API: {str(e)}，然后尝试invoke_model API: {str(inner_e)}")

def process_audio(audio_file, model_id=None, custom_prompt=None):
    """处理音频文件并返回转录和优化结果"""
    try:
        if not audio_file:
            return "请先录制或上传音频文件", ""
            
        # 上传到S3
        s3_uri = upload_to_s3(audio_file)
        
        # 转录音频
        transcript_text = transcribe_audio(s3_uri, audio_file)
        
        # 使用Bedrock优化
        optimized_text = optimize_with_bedrock(transcript_text, model_id, custom_prompt)
        
        return transcript_text, optimized_text
    except Exception as e:
        return f"处理错误: {str(e)}", ""
