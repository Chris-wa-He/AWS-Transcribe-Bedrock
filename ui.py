"""
用户界面模块，负责创建和管理Gradio界面
"""
import gradio as gr
from aws_services import process_audio

def create_ui():
    """创建Gradio用户界面"""
    with gr.Blocks(title="语音助手 - AWS Transcribe & Bedrock") as demo:
        gr.Markdown("# 语音助手 - AWS Transcribe & Bedrock")
        gr.Markdown("使用您的麦克风录制语音，系统将通过AWS Transcribe自动识别语言并转录，然后使用Bedrock优化文本。")
        
        with gr.Row():
            audio_input = gr.Audio(
                sources=["microphone", "upload"], 
                type="filepath",
                label="录音或上传音频"
            )
        
        with gr.Row():
            process_button = gr.Button("处理音频")
        
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
        
        # 设置事件处理
        process_button.click(
            fn=process_audio,
            inputs=[audio_input],
            outputs=[transcribe_output, llm_output]
        )
        
        # 也可以在录音完成后自动处理
        audio_input.change(
            fn=process_audio,
            inputs=[audio_input],
            outputs=[transcribe_output, llm_output]
        )
    
    return demo
