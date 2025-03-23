"""
用户界面模块，负责创建和管理Gradio界面
"""
import gradio as gr
from aws_services import process_audio, get_available_models
from config import SUPPORTED_AUDIO_FORMATS, OPTIMIZATION_PROMPT

def create_ui():
    """创建Gradio用户界面"""
    # 获取可用的模型列表
    try:
        models = get_available_models()
        model_choices = {model['name']: model['id'] for model in models}
    except Exception as e:
        print(f"获取模型列表失败: {str(e)}")
        model_choices = {"Claude 3 Sonnet (默认)": "anthropic.claude-3-sonnet-20240229-v1:0"}
    
    with gr.Blocks(title="语音助手 - AWS Transcribe & Bedrock") as demo:
        gr.Markdown("# 语音助手 - AWS Transcribe & Bedrock")
        gr.Markdown("使用您的麦克风录制语音或上传音频文件，系统将通过AWS Transcribe自动识别语言并转录，然后使用Bedrock优化文本。")
        
        # 显示支持的文件格式
        supported_formats = ", ".join(SUPPORTED_AUDIO_FORMATS)
        gr.Markdown(f"**支持的音频格式**: {supported_formats}")
        
        # 模型选择和提示词设置
        with gr.Accordion("高级设置", open=False):
            model_dropdown = gr.Dropdown(
                choices=list(model_choices.keys()),
                value=list(model_choices.keys())[0],
                label="选择Bedrock模型",
                info="选择用于优化文本的AWS Bedrock模型"
            )
            
            custom_prompt = gr.Textbox(
                label="自定义提示词",
                placeholder="输入自定义提示词，使用{text}作为转录文本的占位符",
                value=OPTIMIZATION_PROMPT,
                lines=5
            )
            
            gr.Markdown("""
            **提示词说明**:
            - 使用 `{text}` 作为转录文本的占位符
            - 如果不包含 `{text}`，转录文本将被附加到提示词后面
            - 留空则使用默认提示词
            """)
        
        # 音频输入选项卡
        with gr.Tabs():
            with gr.TabItem("录音"):
                audio_input_mic = gr.Audio(
                    sources=["microphone"], 
                    type="filepath",
                    label="使用麦克风录音"
                )
                process_mic_button = gr.Button("处理录音", variant="primary")
            
            with gr.TabItem("上传音频"):
                audio_input_upload = gr.Audio(
                    sources=["upload"], 
                    type="filepath",
                    label=f"上传音频文件 (支持: {supported_formats})"
                )
                process_upload_button = gr.Button("处理上传的音频", variant="primary")
        
        # 输出区域
        with gr.Row():
            with gr.Column():
                transcribe_output = gr.Textbox(
                    label="AWS Transcribe 输出",
                    placeholder="转录文本将显示在这里...",
                    lines=10
                )
            
            with gr.Column():
                llm_output = gr.Textbox(
                    label="Bedrock 优化输出",
                    placeholder="优化后的文本将显示在这里...",
                    lines=10
                )
        
        # 状态信息
        status_info = gr.Markdown("系统就绪，等待音频输入...")
        
        # 处理函数
        def process_with_options(audio_file, model_name, prompt):
            # 获取选择的模型ID
            model_id = model_choices.get(model_name)
            # 处理音频
            return process_audio(audio_file, model_id, prompt)
        
        # 设置事件处理
        process_mic_button.click(
            fn=process_with_options,
            inputs=[audio_input_mic, model_dropdown, custom_prompt],
            outputs=[transcribe_output, llm_output],
            show_progress=True
        ).then(
            fn=lambda: "处理完成！",
            inputs=None,
            outputs=[status_info]
        )
        
        process_upload_button.click(
            fn=process_with_options,
            inputs=[audio_input_upload, model_dropdown, custom_prompt],
            outputs=[transcribe_output, llm_output],
            show_progress=True
        ).then(
            fn=lambda: "处理完成！",
            inputs=None,
            outputs=[status_info]
        )
        
        # 也可以在录音完成后自动处理
        audio_input_mic.change(
            fn=lambda: "录音已就绪，点击处理按钮开始转录和优化...",
            inputs=None,
            outputs=[status_info]
        )
        
        audio_input_upload.change(
            fn=lambda: "音频已上传，点击处理按钮开始转录和优化...",
            inputs=None,
            outputs=[status_info]
        )
    
    return demo
