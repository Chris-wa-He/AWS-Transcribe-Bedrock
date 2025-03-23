"""
日志模块，负责记录应用程序的关键信息
Logging module, responsible for recording key information of the application
"""
import logging
import os
import time
import json
from logging.handlers import RotatingFileHandler
from datetime import datetime

# 创建日志目录 | Create log directory
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# 配置主日志记录器 | Configure main logger
def setup_logger():
    """
    设置并返回主日志记录器
    Set up and return the main logger
    """
    logger = logging.getLogger('voice_assistant')
    logger.setLevel(logging.INFO)
    
    # 防止日志重复 | Prevent duplicate logs
    if logger.handlers:
        return logger
    
    # 创建控制台处理器 | Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    
    # 创建文件处理器 (10MB 大小，保留 5 个备份) | Create file handler (10MB size, keep 5 backups)
    log_file = os.path.join(LOG_DIR, 'voice_assistant.log')
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    
    # 添加处理器到记录器 | Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# 创建服务调用日志记录器 | Create service call logger
def setup_service_logger():
    """
    设置并返回服务调用日志记录器
    Set up and return the service call logger
    """
    logger = logging.getLogger('service_calls')
    logger.setLevel(logging.INFO)
    
    # 防止日志重复 | Prevent duplicate logs
    if logger.handlers:
        return logger
    
    # 创建文件处理器 (10MB 大小，保留 10 个备份) | Create file handler (10MB size, keep 10 backups)
    log_file = os.path.join(LOG_DIR, 'service_calls.log')
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=10, encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_format = logging.Formatter('%(asctime)s - %(message)s')
    file_handler.setFormatter(file_format)
    
    # 添加处理器到记录器 | Add handler to logger
    logger.addHandler(file_handler)
    
    return logger

# 创建LLM调用日志记录器 | Create LLM call logger
def setup_llm_logger():
    """
    设置并返回LLM调用日志记录器
    Set up and return the LLM call logger
    """
    logger = logging.getLogger('llm_calls')
    logger.setLevel(logging.INFO)
    
    # 防止日志重复 | Prevent duplicate logs
    if logger.handlers:
        return logger
    
    # 创建文件处理器 (10MB 大小，保留 10 个备份) | Create file handler (10MB size, keep 10 backups)
    log_file = os.path.join(LOG_DIR, 'llm_calls.log')
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=10, encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_format = logging.Formatter('%(asctime)s - %(message)s')
    file_handler.setFormatter(file_format)
    
    # 添加处理器到记录器 | Add handler to logger
    logger.addHandler(file_handler)
    
    return logger

# 初始化日志记录器 | Initialize loggers
logger = setup_logger()
service_logger = setup_service_logger()
llm_logger = setup_llm_logger()

# 日志装饰器 | Log decorator
def log_service_call(service_name):
    """
    记录服务调用的装饰器
    Decorator for logging service calls
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            
            # 记录调用开始 | Log call start
            call_id = f"{service_name}_{int(start_time * 1000)}"
            service_logger.info(f"START - ID: {call_id} - Service: {service_name}")
            
            try:
                # 调用原始函数 | Call original function
                result = func(*args, **kwargs)
                
                # 计算执行时间 | Calculate execution time
                end_time = time.time()
                duration = end_time - start_time
                
                # 记录成功调用 | Log successful call
                log_data = {
                    "id": call_id,
                    "service": service_name,
                    "status": "success",
                    "start_time": start_datetime,
                    "duration_seconds": round(duration, 3),
                    "args": str(args) if args else None,
                    "kwargs": {k: v for k, v in kwargs.items() if k not in ['audio_file']}  # 排除大型二进制数据 | Exclude large binary data
                }
                
                # 对于特定服务，记录额外信息 | For specific services, log additional information
                if service_name == "transcribe":
                    if isinstance(result, str) and len(result) > 100:
                        log_data["result_preview"] = result[:100] + "..."
                        log_data["transcript_length"] = len(result)
                    else:
                        log_data["result"] = result
                
                service_logger.info(f"SUCCESS - {json.dumps(log_data)}")
                return result
                
            except Exception as e:
                # 计算执行时间 | Calculate execution time
                end_time = time.time()
                duration = end_time - start_time
                
                # 记录失败调用 | Log failed call
                log_data = {
                    "id": call_id,
                    "service": service_name,
                    "status": "error",
                    "start_time": start_datetime,
                    "duration_seconds": round(duration, 3),
                    "error": str(e),
                    "args": str(args) if args else None,
                    "kwargs": {k: v for k, v in kwargs.items() if k not in ['audio_file']}  # 排除大型二进制数据 | Exclude large binary data
                }
                service_logger.error(f"ERROR - {json.dumps(log_data)}")
                
                # 重新抛出异常 | Re-raise exception
                raise
                
        return wrapper
    return decorator

def log_llm_call(model_id, prompt=None, custom_prompt=None):
    """
    记录LLM调用信息
    Log LLM call information
    """
    call_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    call_id = f"llm_{int(time.time() * 1000)}"
    
    # 确定使用的提示词 | Determine the prompt used
    used_prompt = custom_prompt if custom_prompt else prompt
    if used_prompt and len(used_prompt) > 500:
        prompt_preview = used_prompt[:500] + "..."
    else:
        prompt_preview = used_prompt
    
    log_data = {
        "id": call_id,
        "timestamp": call_time,
        "model_id": model_id,
        "prompt_preview": prompt_preview,
        "prompt_length": len(used_prompt) if used_prompt else 0
    }
    
    llm_logger.info(json.dumps(log_data))
    return call_id

def log_llm_response(call_id, response_text, duration):
    """
    记录LLM响应信息
    Log LLM response information
    """
    if response_text and len(response_text) > 500:
        response_preview = response_text[:500] + "..."
    else:
        response_preview = response_text
    
    log_data = {
        "id": call_id,
        "duration_seconds": round(duration, 3),
        "response_preview": response_preview,
        "response_length": len(response_text) if response_text else 0
    }
    
    llm_logger.info(json.dumps(log_data))
