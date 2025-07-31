# 故障排除指南 | Troubleshooting Guide

本文档提供了常见问题的解决方案和故障排除步骤。

This document provides solutions for common issues and troubleshooting steps.

## 常见错误 | Common Errors

### 1. S3上传错误 | S3 Upload Errors

#### 错误信息 | Error Message
```
上传到S3失败: expected string or bytes-like object, got 'NoneType'
Upload to S3 failed: expected string or bytes-like object, got 'NoneType'
```

#### 可能原因 | Possible Causes
- 音频文件路径为空或无效
- Gradio文件对象处理问题
- 文件上传失败

#### 解决方案 | Solutions
1. **检查音频文件**：确保已正确录制或上传音频文件
2. **重新上传**：尝试重新录制或上传音频文件
3. **检查文件格式**：确保使用支持的音频格式（mp3, mp4, wav, flac, ogg, amr, webm）
4. **检查文件大小**：确保文件大小不超过2GB

### 2. AWS配置错误 | AWS Configuration Errors

#### 错误信息 | Error Message
```
S3存储桶名称未配置
S3 bucket name not configured
```

#### 解决方案 | Solutions
1. **检查.env文件**：
   ```bash
   # 确保.env文件包含以下配置
   S3_BUCKET_NAME=your-bucket-name
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_REGION=your-region
   ```

2. **创建S3存储桶**：
   ```bash
   aws s3 mb s3://your-bucket-name --region your-region
   ```

3. **验证AWS凭证**：
   ```bash
   aws sts get-caller-identity
   ```

### 3. AWS权限错误 | AWS Permission Errors

#### 错误信息 | Error Message
```
AWS访问权限不足，请检查IAM权限
Insufficient AWS access permissions, please check IAM permissions
```

#### 解决方案 | Solutions
1. **检查IAM权限**：确保您的AWS用户或角色具有以下权限：
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "s3:PutObject",
           "s3:GetObject",
           "transcribe:StartTranscriptionJob",
           "transcribe:GetTranscriptionJob",
           "bedrock:InvokeModel",
           "bedrock:Converse",
           "bedrock:ListFoundationModels"
         ],
         "Resource": "*"
       }
     ]
   }
   ```

2. **验证存储桶访问**：
   ```bash
   aws s3 ls s3://your-bucket-name
   ```

### 4. Bedrock模型访问错误 | Bedrock Model Access Errors

#### 错误信息 | Error Message
```
使用Bedrock优化文本失败
Failed to optimize text using Bedrock
```

#### 解决方案 | Solutions
1. **检查模型访问权限**：在AWS控制台中启用Bedrock模型访问
2. **验证模型可用性**：
   ```bash
   aws bedrock list-foundation-models --region your-region
   ```
3. **检查区域支持**：确保您的区域支持Bedrock服务

### 5. 转录失败 | Transcription Failures

#### 错误信息 | Error Message
```
转录音频失败
Failed to transcribe audio
```

#### 解决方案 | Solutions
1. **检查音频质量**：确保音频清晰，无损坏
2. **检查文件格式**：使用支持的音频格式
3. **检查文件大小**：确保文件不超过2GB
4. **检查网络连接**：确保网络连接稳定

## 配置验证 | Configuration Validation

### 使用内置配置检查 | Using Built-in Configuration Check

应用启动时会自动检查配置，您也可以在界面中查看配置状态：

The application automatically checks configuration on startup, and you can also view configuration status in the interface:

1. 打开应用界面 | Open the application interface
2. 展开"配置状态"部分 | Expand the "Configuration Status" section
3. 查看配置错误和警告 | Review configuration errors and warnings

### 手动验证步骤 | Manual Validation Steps

1. **检查环境变量**：
   ```bash
   # 检查.env文件是否存在
   ls -la .env
   
   # 查看环境变量
   cat .env
   ```

2. **测试AWS连接**：
   ```bash
   # 验证AWS凭证
   aws sts get-caller-identity
   
   # 测试S3访问
   aws s3 ls s3://your-bucket-name
   
   # 测试Transcribe服务
   aws transcribe list-transcription-jobs --region your-region
   
   # 测试Bedrock服务
   aws bedrock list-foundation-models --region your-region
   ```

3. **检查Python依赖**：
   ```bash
   poetry show
   # 或
   pip list
   ```

## 日志分析 | Log Analysis

### 日志文件位置 | Log File Locations

- **应用日志** | Application Logs: `logs/voice_assistant.log`
- **服务调用日志** | Service Call Logs: `logs/service_calls.log`
- **LLM调用日志** | LLM Call Logs: `logs/llm_calls.log`

### 查看日志 | Viewing Logs

```bash
# 查看最新的应用日志
tail -f logs/voice_assistant.log

# 查看错误日志
grep -i error logs/voice_assistant.log

# 查看特定时间的日志
grep "2024-01-01" logs/voice_assistant.log
```

## 性能优化 | Performance Optimization

### 音频文件优化 | Audio File Optimization

1. **文件大小**：尽量使用较小的音频文件以加快上传速度
2. **音频质量**：使用适中的音频质量（不需要过高的采样率）
3. **文件格式**：推荐使用wav或mp3格式

### 网络优化 | Network Optimization

1. **区域选择**：选择距离您最近的AWS区域
2. **网络连接**：确保稳定的网络连接
3. **并发限制**：避免同时处理多个大文件

## 获取帮助 | Getting Help

### 启用详细日志 | Enable Verbose Logging

在.env文件中添加：
```bash
LOG_LEVEL=DEBUG
```

### 收集诊断信息 | Collecting Diagnostic Information

运行以下命令收集系统信息：

```bash
# 系统信息
python --version
poetry --version

# AWS配置
aws --version
aws configure list

# 应用配置
poetry run python -c "from config import get_configuration_status; import json; print(json.dumps(get_configuration_status(), indent=2))"
```

### 联系支持 | Contact Support

如果问题仍然存在，请提供以下信息：

If the problem persists, please provide the following information:

1. 错误消息的完整文本 | Complete error message text
2. 相关日志文件内容 | Relevant log file contents
3. 系统配置信息 | System configuration information
4. 重现问题的步骤 | Steps to reproduce the issue

## 常见问题FAQ | Frequently Asked Questions

### Q: 为什么我的音频文件上传失败？
**A**: 检查文件格式是否支持，文件大小是否超过2GB，以及网络连接是否稳定。

### Q: 如何更改AWS区域？
**A**: 在.env文件中修改AWS_REGION变量，然后重启应用。

### Q: 为什么Bedrock优化失败？
**A**: 确保您的AWS账户已启用Bedrock服务，并且有权限访问所选的模型。

### Q: 如何提高转录准确性？
**A**: 使用高质量的音频文件，确保语音清晰，减少背景噪音。

### Q: 应用启动很慢怎么办？
**A**: 检查网络连接，确保AWS服务可访问，考虑选择更近的AWS区域。