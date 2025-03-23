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

# 导入日志模块
from logger import logger, service_logger, log_service_call, log_llm_call, log_llm_response

# 初始化AWS客户端
s3_client = boto3.client('s3')
transcribe_client = boto3.client('transcribe')
bedrock_client = boto3.client('bedrock-runtime')
bedrock_management = boto3.client('bedrock')

@log_service_call("list_models")
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
        
        logger.info(f"获取到 {len(text_models)} 个可用的文本生成模型")
        return text_models
    except Exception as e:
        logger.error(f"获取模型列表失败: {str(e)}")
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
    logger.warning(f"无法确定文件格式 '{file_path}'，使用默认格式 '{DEFAULT_AUDIO_FORMAT}'")
    return DEFAULT_AUDIO_FORMAT

@log_service_call("s3_upload")
def upload_to_s3(audio_path):
    """上传音频文件到S3并返回S3 URI"""
    try:
        file_name = os.path.basename(audio_path)
        file_size = os.path.getsize(audio_path)
        logger.info(f"开始上传文件 '{file_name}' ({file_size} 字节) 到 S3")
        
        s3_key = f"audio/{file_name}"
        s3_client.upload_file(audio_path, S3_BUCKET_NAME, s3_key)
        s3_uri = f"s3://{S3_BUCKET_NAME}/{s3_key}"
        
        logger.info(f"文件上传成功: {s3_uri}")
        return s3_uri
    except Exception as e:
        logger.error(f"上传到S3失败: {str(e)}")
        raise Exception(f"上传到S3失败: {str(e)}")

@log_service_call("transcribe")
def transcribe_audio(s3_uri, audio_path):
    """使用AWS Transcribe转录音频并返回转录文本"""
    try:
        # 创建转录任务
        job_name = f"transcription-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 确定媒体格式
        media_format = get_media_format(audio_path)
        
        logger.info(f"开始转录任务 {job_name}，媒体格式: {media_format}")
        
        # 使用自动语言识别
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': s3_uri},
            MediaFormat=media_format,
            IdentifyLanguage=True  # 启用自动语言识别
        )
        
        # 等待转录完成
        start_time = time.time()
        while True:
            status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            job_status = status['TranscriptionJob']['TranscriptionJobStatus']
            
            if job_status in ['COMPLETED', 'FAILED']:
                break
                
            # 每30秒记录一次等待状态
            elapsed = time.time() - start_time
            if int(elapsed) % 30 == 0:
                logger.info(f"转录任务 {job_name} 正在进行中，已等待 {int(elapsed)} 秒")
                
            time.sleep(1)
            
        if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
            transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            
            # 获取转录结果
            response = urllib.request.urlopen(transcript_uri)
            transcript_data = json.loads(response.read().decode('utf-8'))
            
            # 获取识别的语言
            identified_language = status['TranscriptionJob'].get('LanguageCode', 'unknown')
            logger.info(f"转录完成，识别的语言: {identified_language}")
            
            transcript_text = transcript_data['results']['transcripts'][0]['transcript']
            logger.info(f"转录文本长度: {len(transcript_text)} 字符")
            
            return transcript_text
        else:
            error_reason = status['TranscriptionJob'].get('FailureReason', '未知原因')
            logger.error(f"转录失败: {error_reason}")
            raise Exception(f"转录失败: {error_reason}")
            
    except Exception as e:
        logger.error(f"转录音频失败: {str(e)}")
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
    
    # 记录LLM调用开始
    call_id = log_llm_call(model_id, prompt=prompt, custom_prompt=custom_prompt)
    start_time = time.time()
    
    try:
        logger.info(f"开始使用模型 {model_id} 优化文本")
        
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
        
        # 记录LLM响应
        duration = time.time() - start_time
        log_llm_response(call_id, result_text, duration)
        
        logger.info(f"文本优化完成，响应长度: {len(result_text)} 字符，耗时: {duration:.2f} 秒")
        return result_text if result_text else "无法获取优化文本"
        
    except Exception as e:
        logger.warning(f"converse API失败: {str(e)}，尝试使用invoke_model API")
        
        # 如果converse API失败，回退到invoke_model API
        try:
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
                result_text = response_body['content'][0]['text']
                
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
                result_text = response_body.get('results', [{}])[0].get('outputText', "无法获取优化文本")
                
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
                result_text = response_body.get('generation', "无法获取优化文本")
            
            # 记录LLM响应
            duration = time.time() - start_time
            log_llm_response(call_id, result_text, duration)
            
            logger.info(f"使用invoke_model API成功，响应长度: {len(result_text)} 字符，耗时: {duration:.2f} 秒")
            return result_text
            
        except Exception as inner_e:
            # 记录失败的LLM调用
            duration = time.time() - start_time
            log_llm_response(call_id, f"错误: {str(inner_e)}", duration)
            
            logger.error(f"使用Bedrock优化文本失败: 首先尝试converse API: {str(e)}，然后尝试invoke_model API: {str(inner_e)}")
            raise Exception(f"使用Bedrock优化文本失败: 首先尝试converse API: {str(e)}，然后尝试invoke_model API: {str(inner_e)}")

@log_service_call("process_audio")
def process_audio(audio_file, model_id=None, custom_prompt=None):
    """处理音频文件并返回转录和优化结果"""
    try:
        if not audio_file:
            logger.warning("未提供音频文件")
            return "请先录制或上传音频文件", ""
            
        logger.info(f"开始处理音频文件: {audio_file}")
        
        # 上传到S3
        s3_uri = upload_to_s3(audio_file)
        
        # 转录音频
        transcript_text = transcribe_audio(s3_uri, audio_file)
        
        # 使用Bedrock优化
        optimized_text = optimize_with_bedrock(transcript_text, model_id, custom_prompt)
        
        logger.info("音频处理完成")
        return transcript_text, optimized_text
    except Exception as e:
        logger.error(f"处理音频失败: {str(e)}")
        return f"处理错误: {str(e)}", ""
