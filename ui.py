"""
用户界面模块，负责创建和管理Gradio界面
"""
import gradio as gr
from aws_services import process_audio
from config import SUPPORTED_AUDIO_FORMATS

def create_ui():
    """创建Gradio用户界面"""
    with gr.Blocks(title="语音助手 - AWS Transcribe & Bedrock") as demo:
        gr.Markdown("# 语音助手 - AWS Transcribe & Bedrock")
        gr.Markdown("使用您的麦克风录制语音或上传音频文件，系统将通过AWS Transcribe自动识别语言并转录，然后使用Bedrock优化文本。")
        
        # 显示支持的文件格式
        supported_formats = ", ".join(SUPPORTED_AUDIO_FORMATS)
        gr.Markdown(f"**支持的音频格式**: {supported_formats}")
        
        with gr.Tabs():
            with gr.TabItem("录音"):
                audio_input_mic = gr.Audio(
                    sources=["microphone"], 
                    type="filepath",
                    label="使用麦克风录音"
                )
                process_mic_button = gr.Button("处理录音")
            
            with gr.TabItem("上传音频"):
                audio_input_upload = gr.Audio(
                    sources=["upload"], 
                    type="filepath",
                    label=f"上传音频文件 (支持: {supported_formats})"
                )
                process_upload_button = gr.Button("处理上传的音频")
        
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
        
        # 设置事件处理
        process_mic_button.click(
            fn=process_audio,
            inputs=[audio_input_mic],
            outputs=[transcribe_output, llm_output],
            show_progress=True
        ).then(
            fn=lambda: "处理完成！",
            inputs=None,
            outputs=[status_info]
        )
        
        process_upload_button.click(
            fn=process_audio,
            inputs=[audio_input_upload],
            outputs=[transcribe_output, llm_output],
            show_progress=True
        ).then(
            fn=lambda: "处理完成！",
            inputs=None,
            outputs=[status_info]
        )
        
        # 也可以在录音完成后自动处理
        audio_input_mic.change(
            fn=lambda: "正在处理录音...",
            inputs=None,
            outputs=[status_info]
        ).then(
            fn=process_audio,
            inputs=[audio_input_mic],
            outputs=[transcribe_output, llm_output]
        ).then(
            fn=lambda: "处理完成！",
            inputs=None,
            outputs=[status_info]
        )
        
        audio_input_upload.change(
            fn=lambda: "正在处理上传的音频...",
            inputs=None,
            outputs=[status_info]
        ).then(
            fn=process_audio,
            inputs=[audio_input_upload],
            outputs=[transcribe_output, llm_output]
        ).then(
            fn=lambda: "处理完成！",
            inputs=None,
            outputs=[status_info]
        )
    
    return demo
