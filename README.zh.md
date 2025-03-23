# 语音助手 - AWS Transcribe 和 Bedrock

本应用程序提供了一个基于网页的语音输入界面，使用 AWS Transcribe 进行转录，并使用 AWS Bedrock 的 Claude 3 Sonnet (Nova Lite) 模型进行优化。

## 功能特点

- 通过计算机麦克风进行语音录制
- 支持多种音频格式上传（mp3, mp4, wav, flac, ogg, amr, webm）
- 使用 AWS Transcribe 进行实时转录（支持多种语言，自动检测）
- 使用 AWS Bedrock 的 Claude 3 Sonnet 模型优化文本
- 并排显示原始转录和优化后的文本
- 基于 Gradio 的网页界面
- 支持麦克风录音和音频文件上传
- 从账户中可用的 AWS Bedrock 模型中选择模型
- 可自定义文本优化提示词
- 全面的日志系统，支持日志文件自动轮换

## 系统要求

- Python 3.8+
- AWS 账户，需要访问：
  - Amazon Transcribe
  - Amazon Bedrock（需要有 Claude 3 Sonnet 模型访问权限）
  - Amazon S3（用于存储音频文件）
- 已配置 AWS 凭证

## 安装步骤

1. 克隆此仓库：
   ```
   git clone https://github.com/yourusername/transcribe-test.git
   cd transcribe-test
   ```

2. 安装所需依赖：
   ```
   pip install -r requirements.txt
   ```

3. 基于提供的 `.env.example` 创建 `.env` 文件：
   ```
   cp .env.example .env
   ```

4. 编辑 `.env` 文件，填入您的 AWS 凭证和 S3 存储桶信息。

## 使用方法

1. 运行应用程序：
   ```
   python main.py
   ```

2. 应用程序将在您的网页浏览器中打开，包含两个选项卡：
   - **录音**：使用麦克风录制音频
   - **上传音频**：上传预先录制的音频文件

3. 高级设置（可选）：
   - 点击"高级设置"展开额外选项
   - 从下拉列表中选择不同的 Bedrock 模型
   - 自定义用于文本优化的提示词

4. 麦克风录音：
   - 点击"开始录音"开始录制您的声音
   - 清晰地对着麦克风说话
   - 完成后点击"停止录音"
   - 点击"处理录音"开始处理

5. 文件上传：
   - 点击"上传"并选择音频文件（支持格式：mp3, mp4, wav, flac, ogg, amr, webm）
   - 点击"处理上传的音频"开始处理

6. 应用程序将处理您的音频：
   - 左侧面板将显示来自 AWS Transcribe 的原始转录
   - 右侧面板将显示来自 AWS Bedrock 的优化文本

## 注意事项

- 应用程序使用 AWS Transcribe 的自动语言识别功能。
- 您需要创建一个 S3 存储桶用于存储临时音频文件。
- 确保您的 AWS 账户具有 Transcribe 和 Bedrock 服务的必要权限。

## 故障排除

- 如果遇到身份验证错误，请验证 `.env` 文件中的 AWS 凭证。
- 对于音频录制问题，请检查麦克风设置和权限。
- 如果 Bedrock 处理失败，请确保您的 AWS 账户有权访问 Claude 3 Sonnet 模型。

## 日志系统

应用程序包含全面的日志系统，记录关键操作信息：

- **应用程序日志**：记录在 `logs/voice_assistant.log`
- **服务调用日志**：记录在 `logs/service_calls.log`
- **LLM 调用日志**：记录在 `logs/llm_calls.log`

所有日志文件在达到 10MB 时自动轮换，保留多个备份文件。
