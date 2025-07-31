"""
AWS服务模块，负责与AWS Transcribe和Bedrock交互
AWS Services module, responsible for interacting with AWS Transcribe and Bedrock
"""
import json
import time
import urllib.request
from datetime import datetime
import os
import boto3
import mimetypes

from .config import (
    S3_BUCKET_NAME,
    SUPPORTED_AUDIO_FORMATS,
    DEFAULT_AUDIO_FORMAT,
    BEDROCK_MODEL_ID,
    BEDROCK_MAX_TOKENS,
    OPTIMIZATION_PROMPT,
)

# 导入日志模块 | Import logging module
from .logger import (
    logger,
    log_service_call,
    log_llm_call,
    log_llm_response,
)

# 导入输出格式化模块 | Import output formatting module
from .output_formatter import format_combined_output

# 导入发言者文本提取模块 | Import speaker text extraction module
from .speaker_text_extractor import extract_speaker_segments

# 初始化AWS客户端 | Initialize AWS clients
# 支持AWS Profile配置 | Support AWS Profile configuration
def get_boto3_session():
    """获取boto3会话，支持AWS Profile"""
    aws_profile = os.getenv("AWS_PROFILE")
    if aws_profile:
        logger.info(f"使用AWS Profile: {aws_profile} | Using AWS Profile: {aws_profile}")
        return boto3.Session(profile_name=aws_profile)
    else:
        logger.info("使用默认AWS凭证 | Using default AWS credentials")
        return boto3.Session()

# 创建AWS客户端 | Create AWS clients
session = get_boto3_session()
s3_client = session.client("s3")
transcribe_client = session.client("transcribe")
bedrock_client = session.client("bedrock-runtime")
bedrock_management = session.client("bedrock")

# 模型ID到inference profile ID的映射 | Mapping from model ID to inference profile ID
def get_inference_profile_id(model_id):
    """
    将模型ID转换为对应的inference profile ID
    Convert model ID to corresponding inference profile ID
    """
    # 基础模型ID到inference profile ID的映射
    model_to_profile_mapping = {
        # Claude 模型
        "anthropic.claude-3-5-sonnet-20241022-v2:0": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        "anthropic.claude-3-5-sonnet-20240620-v1:0": "us.anthropic.claude-3-5-sonnet-20240620-v1:0",
        "anthropic.claude-3-7-sonnet-20250219-v1:0": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        "anthropic.claude-3-5-haiku-20241022-v1:0": "us.anthropic.claude-3-5-haiku-20241022-v1:0",
        "anthropic.claude-3-haiku-20240307-v1:0": "us.anthropic.claude-3-haiku-20240307-v1:0",
        "anthropic.claude-3-opus-20240229-v1:0": "us.anthropic.claude-3-opus-20240229-v1:0",
        "anthropic.claude-3-sonnet-20240229-v1:0": "us.anthropic.claude-3-sonnet-20240229-v1:0",
        "anthropic.claude-opus-4-20250514-v1:0": "us.anthropic.claude-opus-4-20250514-v1:0",
        "anthropic.claude-sonnet-4-20250514-v1:0": "us.anthropic.claude-sonnet-4-20250514-v1:0",
        
        # Nova 模型
        "amazon.nova-pro-v1:0": "us.amazon.nova-pro-v1:0",
        "amazon.nova-lite-v1:0": "us.amazon.nova-lite-v1:0",
        "amazon.nova-micro-v1:0": "us.amazon.nova-micro-v1:0",
        "amazon.nova-premier-v1:0": "us.amazon.nova-premier-v1:0",
        
        # Meta Llama 模型
        "meta.llama3-1-405b-instruct-v1:0": "us.meta.llama3-1-405b-instruct-v1:0",
        "meta.llama3-1-70b-instruct-v1:0": "us.meta.llama3-1-70b-instruct-v1:0",
        "meta.llama3-1-8b-instruct-v1:0": "us.meta.llama3-1-8b-instruct-v1:0",
        
        # DeepSeek 模型
        "deepseek.r1-v1:0": "us.deepseek.r1-v1:0",
    }
    
    # 如果有直接映射，返回inference profile ID
    if model_id in model_to_profile_mapping:
        return model_to_profile_mapping[model_id]
    
    # 如果已经是inference profile ID格式，直接返回
    if model_id.startswith("us."):
        return model_id
    
    # 对于其他模型，尝试直接使用（可能支持直接调用）
    return model_id


def try_model_with_fallback(model_id, bedrock_client, messages, inference_config):
    """
    尝试使用模型调用，如果失败则尝试inference profile
    Try to call model, fallback to inference profile if failed
    """
    # 首先尝试直接调用模型
    try:
        logger.debug(f"尝试直接调用模型: {model_id} | Trying direct model call: {model_id}")
        response = bedrock_client.converse(
            modelId=model_id,
            messages=messages,
            inferenceConfig=inference_config,
        )
        logger.info(f"直接模型调用成功: {model_id} | Direct model call successful: {model_id}")
        return response, model_id
    except Exception as e:
        error_str = str(e)
        # 检查是否是需要inference profile的错误
        if "on-demand throughput isn't supported" in error_str or "inference profile" in error_str:
            logger.info(f"模型 {model_id} 需要使用inference profile，尝试转换 | Model {model_id} requires inference profile, trying conversion")
            
            # 获取inference profile ID
            profile_id = get_inference_profile_id(model_id)
            
            if profile_id != model_id:  # 如果有不同的profile ID
                try:
                    logger.debug(f"尝试使用inference profile: {profile_id} | Trying inference profile: {profile_id}")
                    response = bedrock_client.converse(
                        modelId=profile_id,
                        messages=messages,
                        inferenceConfig=inference_config,
                    )
                    logger.info(f"Inference profile调用成功: {profile_id} | Inference profile call successful: {profile_id}")
                    return response, profile_id
                except Exception as profile_error:
                    logger.warning(f"Inference profile {profile_id} 调用也失败: {str(profile_error)} | Inference profile {profile_id} call also failed: {str(profile_error)}")
                    raise profile_error
            else:
                logger.error(f"无法找到模型 {model_id} 的inference profile | Cannot find inference profile for model {model_id}")
                raise e
        else:
            # 其他类型的错误，直接抛出
            logger.error(f"模型调用失败: {model_id}, 错误: {error_str} | Model call failed: {model_id}, error: {error_str}")
            raise e


@log_service_call("list_models")
def get_available_models():
    """
    获取账户中可用的Claude和Nova系列Bedrock模型列表
    Get available Claude and Nova series Bedrock models in the account
    """
    try:
        # 获取所有可用的基础模型 | Get all available foundation models
        response = bedrock_management.list_foundation_models()

        # 过滤出Claude和Nova系列的文本生成模型 | Filter Claude and Nova series text generation models
        filtered_models = []
        for model in response.get("modelSummaries", []):
            model_id = model.get("modelId", "")
            model_name = model.get("modelName", "")
            provider_name = model.get("providerName", "")

            # 只包含支持文本生成的模型 | Only include models that support text generation
            if model.get("outputModalities", []) == ["TEXT"]:
                # 检查是否是Claude或Nova系列模型 | Check if it's Claude or Nova series model
                is_claude = (
                    "claude" in model_id.lower()
                    or "claude" in model_name.lower()
                    or provider_name.lower() == "anthropic"
                )

                is_nova = "nova" in model_id.lower() or "nova" in model_name.lower()

                if is_claude or is_nova:
                    # 创建友好的显示名称 | Create friendly display name
                    if is_claude:
                        # Claude模型的友好名称 | Friendly name for Claude models
                        if "claude-3-5-sonnet" in model_id.lower():
                            display_name = "Claude 3.5 Sonnet"
                        elif "claude-3-sonnet" in model_id.lower():
                            display_name = "Claude 3 Sonnet"
                        elif "claude-3-haiku" in model_id.lower():
                            display_name = "Claude 3 Haiku"
                        elif "claude-3-opus" in model_id.lower():
                            display_name = "Claude 3 Opus"
                        elif "claude-2" in model_id.lower():
                            display_name = "Claude 2"
                        else:
                            display_name = f"Claude - {model_name}"
                    else:
                        # Nova模型的友好名称 | Friendly name for Nova models
                        if "nova-pro" in model_id.lower():
                            display_name = "Nova Pro"
                        elif "nova-lite" in model_id.lower():
                            display_name = "Nova Lite"
                        elif "nova-micro" in model_id.lower():
                            display_name = "Nova Micro"
                        else:
                            display_name = f"Nova - {model_name}"

                    filtered_models.append(
                        {
                            "id": model_id,
                            "name": display_name,
                            "provider": provider_name,
                            "model_name": model_name,
                        }
                    )

        # 按模型系列和名称排序：Claude优先，然后是Nova | Sort by model series and name: Claude first, then Nova
        def sort_key(model):
            name = model["name"].lower()
            if "claude" in name:
                # Claude模型排序：3.5 Sonnet > 3 Opus > 3 Sonnet > 3 Haiku > 2
                if "3.5 sonnet" in name:
                    return (0, 0)
                elif "3 opus" in name:
                    return (0, 1)
                elif "3 sonnet" in name:
                    return (0, 2)
                elif "3 haiku" in name:
                    return (0, 3)
                elif "2" in name:
                    return (0, 4)
                else:
                    return (0, 5)
            elif "nova" in name:
                # Nova模型排序：Pro > Lite > Micro
                if "pro" in name:
                    return (1, 0)
                elif "lite" in name:
                    return (1, 1)
                elif "micro" in name:
                    return (1, 2)
                else:
                    return (1, 3)
            else:
                return (2, 0)

        filtered_models.sort(key=sort_key)

        logger.info(
            f"获取到 {len(filtered_models)} 个可用的Claude和Nova模型 | Got {len(filtered_models)} available Claude and Nova models"
        )

        # 记录找到的模型 | Log found models
        for model in filtered_models:
            logger.debug(
                f"可用模型: {model['name']} ({model['id']}) | Available model: {model['name']} ({model['id']})"
            )

        return filtered_models

    except Exception as e:
        logger.error(f"获取模型列表失败: {str(e)} | Failed to get model list: {str(e)}")
        # 返回默认的Claude和Nova模型 | Return default Claude and Nova models
        default_models = [
            {
                "id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                "name": "Claude 3.5 Sonnet (默认)",
            },
            {
                "id": "anthropic.claude-3-sonnet-20240229-v1:0",
                "name": "Claude 3 Sonnet (默认)",
            },
            {
                "id": "anthropic.claude-3-haiku-20240307-v1:0",
                "name": "Claude 3 Haiku (默认)",
            },
            {"id": "amazon.nova-pro-v1:0", "name": "Nova Pro (默认)"},
            {"id": "amazon.nova-lite-v1:0", "name": "Nova Lite (默认)"},
            {"id": "amazon.nova-micro-v1:0", "name": "Nova Micro (默认)"},
        ]
        logger.info(
            f"使用默认模型列表，包含 {len(default_models)} 个模型 | Using default model list with {len(default_models)} models"
        )
        return default_models


def get_file_extension(file_path):
    """
    获取文件扩展名
    Get file extension
    """
    _, extension = os.path.splitext(file_path)
    return extension[1:].lower() if extension else ""


def get_media_format(file_path):
    """
    根据文件路径确定媒体格式
    Determine media format based on file path
    """
    extension = get_file_extension(file_path)

    # 检查是否是支持的格式 | Check if it's a supported format
    if extension in SUPPORTED_AUDIO_FORMATS:
        return extension

    # 尝试通过MIME类型判断 | Try to determine by MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        if mime_type.startswith("audio/"):
            format_from_mime = mime_type.split("/")[-1]
            if format_from_mime in SUPPORTED_AUDIO_FORMATS:
                return format_from_mime

    # 默认返回wav格式 | Default to wav format
    logger.warning(
        f"无法确定文件格式 '{file_path}'，使用默认格式 '{DEFAULT_AUDIO_FORMAT}' | Cannot determine file format '{file_path}', using default format '{DEFAULT_AUDIO_FORMAT}'"
    )
    return DEFAULT_AUDIO_FORMAT


@log_service_call("s3_upload")
def upload_to_s3(audio_path):
    """
    上传音频文件到S3并返回S3 URI
    Upload audio file to S3 and return S3 URI
    """
    try:
        # 验证输入参数 | Validate input parameters
        if not audio_path:
            error_msg = "音频文件路径为空 | Audio file path is empty"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if not isinstance(audio_path, str):
            error_msg = f"音频文件路径必须是字符串，当前类型: {type(audio_path)} | Audio file path must be a string, current type: {type(audio_path)}"
            logger.error(error_msg)
            raise TypeError(error_msg)

        # 检查文件是否存在 | Check if file exists
        if not os.path.exists(audio_path):
            error_msg = (
                f"音频文件不存在: {audio_path} | Audio file does not exist: {audio_path}"
            )
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        # 检查是否是文件而不是目录 | Check if it's a file and not a directory
        if not os.path.isfile(audio_path):
            error_msg = (
                f"路径不是有效的文件: {audio_path} | Path is not a valid file: {audio_path}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 检查S3存储桶名称是否配置 | Check if S3 bucket name is configured
        if not S3_BUCKET_NAME:
            error_msg = "S3存储桶名称未配置，请检查环境变量 S3_BUCKET_NAME | S3 bucket name not configured, please check environment variable S3_BUCKET_NAME"
            logger.error(error_msg)
            raise ValueError(error_msg)

        file_name = os.path.basename(audio_path)
        file_size = os.path.getsize(audio_path)

        # 检查文件大小 | Check file size
        if file_size == 0:
            error_msg = f"音频文件为空: {file_name} | Audio file is empty: {file_name}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 检查文件大小限制（AWS Transcribe限制为2GB）| Check file size limit (AWS Transcribe limit is 2GB)
        max_size = 2 * 1024 * 1024 * 1024  # 2GB in bytes
        if file_size > max_size:
            error_msg = f"音频文件过大: {file_size} 字节，最大支持 2GB | Audio file too large: {file_size} bytes, maximum supported is 2GB"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info(
            f"开始上传文件 '{file_name}' ({file_size} 字节) 到 S3 存储桶 '{S3_BUCKET_NAME}' | Start uploading file '{file_name}' ({file_size} bytes) to S3 bucket '{S3_BUCKET_NAME}'"
        )

        s3_key = f"audio/{file_name}"
        s3_client.upload_file(audio_path, S3_BUCKET_NAME, s3_key)
        s3_uri = f"s3://{S3_BUCKET_NAME}/{s3_key}"

        logger.info(f"文件上传成功: {s3_uri} | File upload successful: {s3_uri}")
        return s3_uri

    except (ValueError, TypeError, FileNotFoundError) as e:
        # 这些是我们自定义的验证错误，直接抛出 | These are our custom validation errors, throw directly
        raise Exception(f"上传到S3失败: {str(e)} | Upload to S3 failed: {str(e)}")
    except Exception as e:
        logger.error(f"上传到S3失败: {str(e)} | Upload to S3 failed: {str(e)}")
        # 检查是否是AWS权限问题 | Check if it's an AWS permission issue
        if "AccessDenied" in str(e):
            raise Exception(
                f"上传到S3失败: AWS访问权限不足，请检查IAM权限 | Upload to S3 failed: Insufficient AWS access permissions, please check IAM permissions"
            )
        elif "NoSuchBucket" in str(e):
            raise Exception(
                f"上传到S3失败: S3存储桶 '{S3_BUCKET_NAME}' 不存在 | Upload to S3 failed: S3 bucket '{S3_BUCKET_NAME}' does not exist"
            )
        else:
            raise Exception(f"上传到S3失败: {str(e)} | Upload to S3 failed: {str(e)}")


@log_service_call("transcribe")
def transcribe_audio(s3_uri, audio_path, enable_speaker_diarization=False):
    """
    使用AWS Transcribe转录音频并返回转录文本和元数据
    Transcribe audio using AWS Transcribe and return transcription text and metadata
    
    Args:
        s3_uri: S3音频文件URI
        audio_path: 本地音频文件路径
        enable_speaker_diarization: 是否启用发言者划分
    
    Returns:
        dict: 包含转录文本、识别语言、发言者信息等的字典
    """
    try:
        # 创建转录任务 | Create transcription job
        job_name = f"transcription-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 确定媒体格式 | Determine media format
        media_format = get_media_format(audio_path)

        logger.info(
            f"开始转录任务 {job_name}，媒体格式: {media_format}，发言者划分: {enable_speaker_diarization} | Starting transcription job {job_name}, media format: {media_format}, speaker diarization: {enable_speaker_diarization}"
        )

        # 构建转录任务参数 | Build transcription job parameters
        job_params = {
            "TranscriptionJobName": job_name,
            "Media": {"MediaFileUri": s3_uri},
            "MediaFormat": media_format,
            "IdentifyLanguage": True,  # 启用自动语言识别 | Enable automatic language identification
        }

        # 如果启用发言者划分，添加相关设置 | If speaker diarization is enabled, add related settings
        if enable_speaker_diarization:
            job_params["Settings"] = {
                "ShowSpeakerLabels": True,
                "MaxSpeakerLabels": 10,  # 最多识别10个发言者 | Maximum 10 speakers
            }

        # 启动转录任务 | Start transcription job
        transcribe_client.start_transcription_job(**job_params)

        # 等待转录完成 | Wait for transcription to complete
        start_time = time.time()
        while True:
            status = transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
            )
            job_status = status["TranscriptionJob"]["TranscriptionJobStatus"]

            if job_status in ["COMPLETED", "FAILED"]:
                break

            # 每30秒记录一次等待状态 | Log waiting status every 30 seconds
            elapsed = time.time() - start_time
            if int(elapsed) % 30 == 0:
                logger.info(
                    f"转录任务 {job_name} 正在进行中，已等待 {int(elapsed)} 秒 | Transcription job {job_name} in progress, waited for {int(elapsed)} seconds"
                )

            time.sleep(1)

        if status["TranscriptionJob"]["TranscriptionJobStatus"] == "COMPLETED":
            transcript_uri = status["TranscriptionJob"]["Transcript"][
                "TranscriptFileUri"
            ]

            # 获取转录结果 | Get transcription result
            response = urllib.request.urlopen(transcript_uri)
            transcript_data = json.loads(response.read().decode("utf-8"))

            # 获取识别的语言 | Get identified language
            identified_language = status["TranscriptionJob"].get(
                "LanguageCode", "unknown"
            )
            
            # 获取语言置信度 | Get language confidence
            language_identification = status["TranscriptionJob"].get(
                "LanguageIdentification", []
            )
            language_confidence = 0.0
            if language_identification:
                for lang_info in language_identification:
                    if lang_info.get("LanguageCode") == identified_language:
                        language_confidence = lang_info.get("Score", 0.0)
                        break

            logger.info(
                f"转录完成，识别的语言: {identified_language} (置信度: {language_confidence:.2f}) | Transcription completed, identified language: {identified_language} (confidence: {language_confidence:.2f})"
            )

            # 获取基本转录文本 | Get basic transcription text
            transcript_text = transcript_data["results"]["transcripts"][0]["transcript"]
            
            # 构建返回结果 | Build return result
            result = {
                "transcript": transcript_text,
                "language_code": identified_language,
                "language_confidence": language_confidence,
                "speaker_labels": None,
                "segments": None
            }

            # 如枟启用了发言者划分，处理发言者信息 | If speaker diarization is enabled, process speaker information
            if enable_speaker_diarization:
                # 使用专门的文本提取模块处理发言者文本 | Use specialized text extraction module to process speaker text
                speaker_segments = extract_speaker_segments(transcript_data, enable_speaker_diarization)
                
                if speaker_segments:
                    result["speaker_labels"] = transcript_data["results"].get("speaker_labels")
                    result["segments"] = speaker_segments
                    
                    logger.info(
                        f"发言者划分完成，识别到 {len(set(seg['speaker'] for seg in speaker_segments))} 个发言者，共 {len(speaker_segments)} 个片段 | Speaker diarization completed, identified {len(set(seg['speaker'] for seg in speaker_segments))} speakers with {len(speaker_segments)} segments"
                    )
                    
                    # 记录每个片段的详细信息用于调试
                    for i, seg in enumerate(speaker_segments[:3]):  # 只记录前3个片段
                        logger.debug(
                            f"片段 {i+1}: {seg['speaker']} ({seg['start_time']:.1f}s-{seg['end_time']:.1f}s) - '{seg['text'][:50]}...' | Segment {i+1}: {seg['speaker']} ({seg['start_time']:.1f}s-{seg['end_time']:.1f}s) - '{seg['text'][:50]}...'"
                        )
                else:
                    logger.warning("发言者划分已启用但未能提取到有效的发言者片段 | Speaker diarization enabled but failed to extract valid speaker segments")

            logger.info(
                f"转录文本长度: {len(transcript_text)} 字符 | Transcription text length: {len(transcript_text)} characters"
            )

            return result
        else:
            error_reason = status["TranscriptionJob"].get(
                "FailureReason", "未知原因 | Unknown reason"
            )
            logger.error(f"转录失败: {error_reason} | Transcription failed: {error_reason}")
            raise Exception(
                f"转录失败: {error_reason} | Transcription failed: {error_reason}"
            )

    except Exception as e:
        logger.error(f"转录音频失败: {str(e)} | Failed to transcribe audio: {str(e)}")
        raise Exception(f"转录音频失败: {str(e)} | Failed to transcribe audio: {str(e)}")


def optimize_with_bedrock(text, model_id=None, custom_prompt=None):
    """
    使用AWS Bedrock的converse API优化文本
    Optimize text using AWS Bedrock's converse API
    """
    # 如果没有指定模型，使用默认模型
    if not model_id:
        model_id = BEDROCK_MODEL_ID
        logger.info(f"未指定模型，使用默认模型: {model_id} | No model specified, using default model: {model_id}")

    # 如果没有指定自定义提示词，使用默认提示词 | If no custom prompt is specified, use the default prompt
    if not custom_prompt:
        prompt = OPTIMIZATION_PROMPT.format(text=text)
    else:
        # 确保自定义提示词中包含{text}占位符 | Ensure custom prompt contains {text} placeholder
        if "{text}" in custom_prompt:
            prompt = custom_prompt.format(text=text)
        else:
            # 如果没有占位符，将文本附加到提示词后面 | If no placeholder, append text to the prompt
            prompt = f"{custom_prompt}\n\n{text}"

    # 记录LLM调用开始 | Record LLM call start
    call_id = log_llm_call(model_id, prompt=prompt, custom_prompt=custom_prompt)
    start_time = time.time()

    try:
        logger.info(
            f"开始使用模型 {model_id} 优化文本 | Start optimizing text using model {model_id}"
        )

        # 准备调用参数
        messages = [{"role": "user", "content": [{"text": prompt}]}]
        inference_config = {
            "maxTokens": BEDROCK_MAX_TOKENS,
            "temperature": 0.0,
            "topP": 1.0,
        }

        # 使用新的fallback机制调用模型
        response, actual_model_id = try_model_with_fallback(
            model_id, bedrock_client, messages, inference_config
        )

        # 从响应中提取文本 | Extract text from response
        output = response.get("output", {})
        message = output.get("message", {})
        content = message.get("content", [])

        # 合并所有文本内容 | Combine all text content
        result_text = ""
        for item in content:
            if "text" in item:
                result_text += item["text"]

        # 记录LLM响应 | Record LLM response
        duration = time.time() - start_time
        log_llm_response(call_id, result_text, duration)

        # 如果实际使用的模型与请求的不同，记录日志
        if actual_model_id != model_id:
            logger.info(
                f"实际使用的模型: {actual_model_id} (请求的模型: {model_id}) | Actually used model: {actual_model_id} (requested model: {model_id})"
            )

        logger.info(
            f"文本优化完成，响应长度: {len(result_text)} 字符，耗时: {duration:.2f} 秒 | Text optimization completed, response length: {len(result_text)} characters, time taken: {duration:.2f} seconds"
        )
        return result_text if result_text else "无法获取优化文本 | Unable to get optimized text"

    except Exception as e:
        # 记录失败的LLM调用 | Record failed LLM call
        duration = time.time() - start_time
        log_llm_response(
            call_id, f"错误: {str(e)} | Error: {str(e)}", duration
        )

        logger.error(
            f"使用Bedrock优化文本失败: {str(e)} | Failed to optimize text using Bedrock: {str(e)}"
        )
        raise Exception(
            f"使用Bedrock优化文本失败: {str(e)} | Failed to optimize text using Bedrock: {str(e)}"
        )


@log_service_call("process_audio")
def process_audio(audio_file, model_id=None, custom_prompt=None, enable_speaker_diarization=False):
    """
    处理音频文件并返回转录和优化结果
    Process audio file and return transcription and optimization results
    
    Args:
        audio_file: 音频文件
        model_id: Bedrock模型ID
        custom_prompt: 自定义提示词
        enable_speaker_diarization: 是否启用发言者划分
    
    Returns:
        tuple: (转录结果字典, 优化文本, 语言信息, 发言者信息)
    """
    try:
        # 增强输入验证 | Enhanced input validation
        if not audio_file:
            error_msg = "未提供音频文件 | No audio file provided"
            logger.warning(error_msg)
            return f"输入错误: {error_msg} | Input error: {error_msg}", "", "", ""

        # 检查音频文件类型 | Check audio file type
        if isinstance(audio_file, str):
            audio_path = audio_file
        elif hasattr(audio_file, "name"):
            # Gradio文件对象 | Gradio file object
            audio_path = audio_file.name
        else:
            error_msg = f"不支持的音频文件类型: {type(audio_file)} | Unsupported audio file type: {type(audio_file)}"
            logger.error(error_msg)
            return f"输入错误: {error_msg} | Input error: {error_msg}", "", "", ""

        # 验证音频文件路径 | Validate audio file path
        if not audio_path or audio_path.strip() == "":
            error_msg = "音频文件路径为空 | Audio file path is empty"
            logger.warning(error_msg)
            return f"输入错误: {error_msg} | Input error: {error_msg}", "", "", ""

        logger.info(
            f"开始处理音频文件: {audio_path} (类型: {type(audio_file)})，发言者划分: {enable_speaker_diarization} | Start processing audio file: {audio_path} (type: {type(audio_file)}), speaker diarization: {enable_speaker_diarization}"
        )

        # 检查环境配置 | Check environment configuration
        if not S3_BUCKET_NAME:
            error_msg = "S3存储桶名称未配置，请检查 .env 文件中的 S3_BUCKET_NAME | S3 bucket name not configured, please check S3_BUCKET_NAME in .env file"
            logger.error(error_msg)
            return f"配置错误: {error_msg} | Configuration error: {error_msg}", "", "", ""

        # 上传到S3 | Upload to S3
        try:
            s3_uri = upload_to_s3(audio_path)
        except Exception as upload_error:
            logger.error(
                f"S3上传失败: {str(upload_error)} | S3 upload failed: {str(upload_error)}"
            )
            return f"上传错误: {str(upload_error)} | Upload error: {str(upload_error)}", "", "", ""

        # 转录音频 | Transcribe audio
        try:
            transcribe_result = transcribe_audio(s3_uri, audio_path, enable_speaker_diarization)
        except Exception as transcribe_error:
            logger.error(
                f"转录失败: {str(transcribe_error)} | Transcription failed: {str(transcribe_error)}"
            )
            return (
                f"转录错误: {str(transcribe_error)} | Transcription error: {str(transcribe_error)}",
                "",
                "",
                ""
            )

        # 提取转录文本 | Extract transcription text
        transcript_text = transcribe_result["transcript"]
        
        # 使用新的格式化模块生成优化的输出 | Use new formatting module to generate optimized output
        language_info, speaker_info = format_combined_output(transcribe_result, enable_speaker_diarization)

        # 使用Bedrock优化 | Optimize using Bedrock
        try:
            optimized_text = optimize_with_bedrock(
                transcript_text, model_id, custom_prompt
            )
        except Exception as bedrock_error:
            logger.error(
                f"Bedrock优化失败: {str(bedrock_error)} | Bedrock optimization failed: {str(bedrock_error)}"
            )
            # 即使优化失败，也返回转录文本 | Even if optimization fails, return transcription text
            return (
                transcript_text,
                f"优化错误: {str(bedrock_error)} | Optimization error: {str(bedrock_error)}",
                language_info,
                speaker_info
            )

        logger.info("音频处理完成 | Audio processing completed")
        return transcript_text, optimized_text, language_info, speaker_info

    except Exception as e:
        logger.error(f"处理音频失败: {str(e)} | Failed to process audio: {str(e)}")
        return f"处理错误: {str(e)} | Processing error: {str(e)}", "", "", ""
