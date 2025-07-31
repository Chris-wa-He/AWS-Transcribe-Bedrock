"""
用户界面模块，负责创建和管理Gradio界面
User interface module, responsible for creating and managing the Gradio interface
"""
import gradio as gr
from .aws_services import process_audio, get_available_models
from .config import (
    SUPPORTED_AUDIO_FORMATS,
    OPTIMIZATION_PROMPT,
    get_configuration_status,
)


def create_ui():
    """
    创建Gradio用户界面
    Create Gradio user interface
    """
    # 获取可用的模型列表 | Get available models list
    try:
        models = get_available_models()
        model_choices = {model["name"]: model["id"] for model in models}
    except Exception as e:
        print(f"获取模型列表失败: {str(e)} | Failed to get model list: {str(e)}")
        # 使用默认的Claude和Nova模型 | Use default Claude and Nova models
        model_choices = {
            "Claude 3.5 Sonnet (默认)": "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "Claude 3 Sonnet (默认)": "anthropic.claude-3-sonnet-20240229-v1:0",
            "Claude 3 Haiku (默认)": "anthropic.claude-3-haiku-20240307-v1:0",
            "Nova Pro (默认)": "amazon.nova-pro-v1:0",
            "Nova Lite (默认)": "amazon.nova-lite-v1:0",
            "Nova Micro (默认)": "amazon.nova-micro-v1:0",
        }

    with gr.Blocks(title="语音助手 - AWS Transcribe & Bedrock") as demo:
        gr.Markdown("# 语音助手 - AWS Transcribe & Bedrock")
        gr.Markdown("使用您的麦克风录制语音或上传音频文件，系统将通过AWS Transcribe自动识别语言并转录，然后使用Bedrock优化文本。")

        # 显示支持的文件格式 | Display supported file formats
        supported_formats = ", ".join(SUPPORTED_AUDIO_FORMATS)
        gr.Markdown(f"**支持的音频格式**: {supported_formats}")

        # 模型选择和提示词设置 | Model selection and prompt settings
        with gr.Accordion("高级设置 | Advanced Settings", open=False):
            model_dropdown = gr.Dropdown(
                choices=list(model_choices.keys()),
                value=list(model_choices.keys())[0],
                label="选择Bedrock模型 | Select Bedrock Model",
                info="选择用于优化文本的AWS Bedrock模型 | Select AWS Bedrock model for text optimization",
            )

            # 发言者划分开关 | Speaker diarization toggle
            speaker_diarization_checkbox = gr.Checkbox(
                label="启用发言者划分 | Enable Speaker Diarization",
                value=False,
                info="识别并标记不同发言者的语音片段 | Identify and label speech segments from different speakers",
            )

            custom_prompt = gr.Textbox(
                label="自定义提示词 | Custom Prompt",
                placeholder="输入自定义提示词，使用{text}作为转录文本的占位符 | Enter custom prompt, use {text} as placeholder for transcribed text",
                value=OPTIMIZATION_PROMPT,
                lines=5,
            )

            gr.Markdown(
                """
            **提示词说明 | Prompt Instructions**:
            - 使用 `{text}` 作为转录文本的占位符 | Use `{text}` as placeholder for transcribed text
            - 如果不包含 `{text}`，转录文本将被附加到提示词后面 | If `{text}` is not included, transcribed text will be appended to the prompt
            - 留空则使用默认提示词 | Leave empty to use default prompt
            
            **发言者划分说明 | Speaker Diarization Instructions**:
            - 启用后可识别最多10个不同的发言者 | When enabled, can identify up to 10 different speakers
            - 适用于会议、访谈等多人对话场景 | Suitable for meetings, interviews, and multi-person conversations
            - 会增加处理时间但提供更详细的转录结果 | Increases processing time but provides more detailed transcription results
            """
            )

        # 配置状态显示 | Configuration status display
        with gr.Accordion("配置状态 | Configuration Status", open=False):
            config_status = get_configuration_status()

            if config_status["valid"]:
                gr.Markdown(
                    "✅ **配置状态**: 所有必需配置已设置 | Configuration Status: All required configurations are set"
                )
            else:
                error_list = "\n".join(
                    [f"- {error}" for error in config_status["errors"]]
                )
                gr.Markdown(f"❌ **配置错误** | Configuration Errors:\n{error_list}")

            if config_status["warnings"]:
                warning_list = "\n".join(
                    [f"- {warning}" for warning in config_status["warnings"]]
                )
                gr.Markdown(f"⚠️ **配置警告** | Configuration Warnings:\n{warning_list}")

            # 显示当前配置 | Display current configuration
            gr.Markdown(
                f"""
            **当前配置 | Current Configuration**:
            - S3存储桶 | S3 Bucket: `{config_status['config']['s3_bucket']}`
            - AWS区域 | AWS Region: `{config_status['config']['aws_region']}`
            - AWS配置文件 | AWS Profile: `{config_status['config']['aws_profile']}`
            - Bedrock模型 | Bedrock Model: `{config_status['config']['bedrock_model']}`
            - 支持格式 | Supported Formats: `{config_status['config']['supported_formats']}`
            """
            )

        # 音频输入选项卡 | Audio input tabs
        with gr.Tabs():
            with gr.TabItem("录音 | Recording"):
                audio_input_mic = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    label="使用麦克风录音 | Use microphone to record",
                )
                process_mic_button = gr.Button(
                    "处理录音 | Process Recording", variant="primary"
                )

            with gr.TabItem("上传音频 | Upload Audio"):
                audio_input_upload = gr.Audio(
                    sources=["upload"],
                    type="filepath",
                    label=f"上传音频文件 | Upload audio file (支持 | Supported: {supported_formats})",
                )
                process_upload_button = gr.Button(
                    "处理上传的音频 | Process Uploaded Audio", variant="primary"
                )

        # 输出区域 | Output area
        with gr.Row():
            with gr.Column():
                transcribe_output = gr.Textbox(
                    label="AWS Transcribe 输出 | AWS Transcribe Output",
                    placeholder="转录文本将显示在这里... | Transcribed text will be displayed here...",
                    lines=10,
                )

            with gr.Column():
                llm_output = gr.Textbox(
                    label="Bedrock 优化输出 | Bedrock Optimized Output",
                    placeholder="优化后的文本将显示在这里... | Optimized text will be displayed here...",
                    lines=10,
                )

        # 语言识别和发言者信息显示区域 | Language identification and speaker information display area
        with gr.Row():
            with gr.Column():
                language_info = gr.Textbox(
                    label="语言识别信息 | Language Identification",
                    placeholder="识别的语言信息将显示在这里... | Identified language information will be displayed here...",
                    lines=2,
                    interactive=False,
                )

            with gr.Column():
                speaker_info = gr.Textbox(
                    label="发言者信息 | Speaker Information",
                    placeholder="发言者划分信息将显示在这里... | Speaker diarization information will be displayed here...",
                    lines=8,
                    interactive=False,
                )

        # 状态信息 | Status information
        status_info = gr.Markdown(
            "系统就绪，等待音频输入... | System ready, waiting for audio input..."
        )

        # 处理函数 | Processing function
        def process_with_options(audio_file, model_name, prompt, enable_speaker_diarization):
            """
            处理音频文件的包装函数，包含增强的错误处理
            Wrapper function for processing audio files with enhanced error handling
            """
            try:
                # 验证输入 | Validate inputs
                if not audio_file:
                    return (
                        "❌ 错误: 请先录制或上传音频文件 | Error: Please record or upload an audio file first",
                        "",
                        "",
                        "",
                    )

                # 获取选择的模型ID | Get selected model ID
                model_id = model_choices.get(model_name)
                if not model_id:
                    return (
                        f"❌ 错误: 无效的模型选择: {model_name} | Error: Invalid model selection: {model_name}",
                        "",
                        "",
                        "",
                    )

                # 验证提示词 | Validate prompt
                if prompt and len(prompt.strip()) > 10000:
                    return (
                        "❌ 错误: 自定义提示词过长，请限制在10000字符以内 | Error: Custom prompt too long, please limit to 10000 characters",
                        "",
                        "",
                        "",
                    )

                # 处理音频 | Process audio
                return process_audio(audio_file, model_id, prompt, enable_speaker_diarization)

            except Exception as e:
                error_msg = f"❌ 处理失败: {str(e)} | Processing failed: {str(e)}"
                return error_msg, "", "", ""

        # 状态更新函数 | Status update functions
        def update_status_recording():
            return "🎤 录音已就绪，点击'处理录音'按钮开始转录和优化... | Recording ready, click 'Process Recording' button to start transcription and optimization..."

        def update_status_uploaded():
            return "📁 音频已上传，点击'处理上传的音频'按钮开始转录和优化... | Audio uploaded, click 'Process Uploaded Audio' button to start transcription and optimization..."

        def update_status_completed():
            return "✅ 处理完成！您可以查看转录和优化结果 | Processing completed! You can view the transcription and optimization results"

        def update_status_processing():
            return "⏳ 正在处理中，请稍候... | Processing, please wait..."

        # 设置事件处理 | Set up event handling
        process_mic_button.click(
            fn=lambda: update_status_processing(),
            inputs=None,
            outputs=[status_info],
        ).then(
            fn=process_with_options,
            inputs=[audio_input_mic, model_dropdown, custom_prompt, speaker_diarization_checkbox],
            outputs=[transcribe_output, llm_output, language_info, speaker_info],
            show_progress=True,
        ).then(
            fn=update_status_completed,
            inputs=None,
            outputs=[status_info],
        )

        process_upload_button.click(
            fn=lambda: update_status_processing(),
            inputs=None,
            outputs=[status_info],
        ).then(
            fn=process_with_options,
            inputs=[audio_input_upload, model_dropdown, custom_prompt, speaker_diarization_checkbox],
            outputs=[transcribe_output, llm_output, language_info, speaker_info],
            show_progress=True,
        ).then(
            fn=update_status_completed,
            inputs=None,
            outputs=[status_info],
        )

        # 也可以在录音完成后自动处理 | Can also automatically process after recording is complete
        audio_input_mic.change(
            fn=update_status_recording,
            inputs=None,
            outputs=[status_info],
        )

        audio_input_upload.change(
            fn=update_status_uploaded,
            inputs=None,
            outputs=[status_info],
        )

    return demo
