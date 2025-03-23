# Voice Assistant with AWS Transcribe and Bedrock

This application provides a web-based interface for voice input, which is then transcribed using AWS Transcribe and optimized using AWS Bedrock's Claude 3 Sonnet (Nova Lite) model.

## Features

- Voice recording through your computer's microphone
- Audio file upload support for multiple formats (mp3, mp4, wav, flac, ogg, amr, webm)
- Real-time transcription using AWS Transcribe (supports multiple languages with automatic detection)
- Text optimization using AWS Bedrock's Claude 3 Sonnet model
- Side-by-side display of original transcription and optimized text
- Web-based interface using Gradio
- Support for both microphone recording and audio file upload
- Model selection from available AWS Bedrock models in your account
- Customizable prompts for text optimization

## Prerequisites

- Python 3.8+
- AWS account with access to:
  - Amazon Transcribe
  - Amazon Bedrock (with Claude 3 Sonnet model access)
  - Amazon S3 (for storing audio files)
- AWS credentials configured

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/transcribe-test.git
   cd transcribe-test
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on the provided `.env.example`:
   ```
   cp .env.example .env
   ```

4. Edit the `.env` file with your AWS credentials and S3 bucket information.

## Usage

1. Run the application:
   ```
   python main.py
   ```

2. The application will open in your web browser with two tabs:
   - **录音 (Recording)**: Use your microphone to record audio
   - **上传音频 (Upload Audio)**: Upload pre-recorded audio files

3. Advanced Settings (optional):
   - Click on "Advanced Settings" to expand additional options
   - Select a different Bedrock model from the dropdown list
   - Customize the prompt used for text optimization

4. For microphone recording:
   - Click "Start Recording" to begin recording your voice
   - Speak clearly into your microphone
   - Click "Stop Recording" when you're done
   - Click "处理录音 (Process Recording)" to start processing

5. For file upload:
   - Click "Upload" and select an audio file (supported formats: mp3, mp4, wav, flac, ogg, amr, webm)
   - Click "处理上传的音频 (Process Uploaded Audio)" to start processing

6. The application will process your audio:
   - The left panel will show the raw transcription from AWS Transcribe
   - The right panel will show the optimized text from AWS Bedrock

## Notes

- The application uses AWS Transcribe's automatic language identification feature.
- You need to have an S3 bucket created for storing the temporary audio files.
- Make sure your AWS account has the necessary permissions for Transcribe and Bedrock services.

## Troubleshooting

- If you encounter authentication errors, verify your AWS credentials in the `.env` file.
- For issues with audio recording, check your microphone settings and permissions.
- If Bedrock processing fails, ensure you have access to the Claude 3 Sonnet model in your AWS account.
