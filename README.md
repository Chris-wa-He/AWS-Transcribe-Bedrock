# Voice Assistant with AWS Transcribe and Bedrock

This application provides a web-based interface for voice input, which is then transcribed using AWS Transcribe and optimized using AWS Bedrock's Claude and Nova models.

[中文文档](README.zh.md) | [项目结构](PROJECT_STATUS.md)

## Features

- Voice recording through your computer's microphone
- Audio file upload support for multiple formats (mp3, mp4, wav, flac, ogg, amr, webm)
- Real-time transcription using AWS Transcribe (supports multiple languages with automatic detection)
- **🆕 Language identification display** with confidence scores
- **🆕 Speaker diarization** to identify and label different speakers in audio
- Text optimization using AWS Bedrock's Claude and Nova models
- Side-by-side display of original transcription and optimized text
- Web-based interface using Gradio
- Support for both microphone recording and audio file upload
- **Claude and Nova model selection** from available AWS Bedrock models in your account
- Customizable prompts for text optimization
- Comprehensive logging system with rotating log files
- Enhanced error handling and configuration validation

## Prerequisites

- Python 3.10+
- Poetry (for dependency management)
- AWS account with access to:
  - Amazon Transcribe
  - Amazon Bedrock (with Claude and Nova model access)
  - Amazon S3 (for storing audio files)
- AWS credentials configured

## Installation

### Method 1: Using Poetry (Recommended)

1. Clone this repository:
   ```bash
   git clone git@github.com:Chris-wa-He/AWS-Transcribe-Bedrock.git
   cd AWS-Transcribe-Bedrock
   ```

2. Install Poetry if you haven't already:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

4. Create a `.env` file based on the provided `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Configure AWS credentials (choose one method):
   
   **Method A: Using AWS Profile (Recommended)**
   ```bash
   # Configure AWS CLI with your credentials
   aws configure --profile my-bedrock-profile
   
   # Edit .env file to use the profile
   # Comment out AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
   # Uncomment and set:
   # AWS_PROFILE=my-bedrock-profile
   ```
   
   **Method B: Using Access Keys**
   ```bash
   # Edit .env file with your AWS credentials and S3 bucket information
   AWS_ACCESS_KEY_ID=your_real_access_key
   AWS_SECRET_ACCESS_KEY=your_real_secret_key
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=your-s3-bucket-name
   ```

### Method 2: Using pip (Legacy)

1. Clone this repository:
   ```bash
   git clone git@github.com:Chris-wa-He/AWS-Transcribe-Bedrock.git
   cd AWS-Transcribe-Bedrock
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on the provided `.env.example`:
   ```bash
   cp .env.example .env
   ```

4. Configure AWS credentials (choose one method):
   
   **Method A: Using AWS Profile (Recommended)**
   ```bash
   # Configure AWS CLI with your credentials
   aws configure --profile my-bedrock-profile
   
   # Edit .env file to use the profile
   # Comment out AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
   # Uncomment and set:
   # AWS_PROFILE=my-bedrock-profile
   ```
   
   **Method B: Using Access Keys**
   ```bash
   # Edit .env file with your AWS credentials and S3 bucket information
   AWS_ACCESS_KEY_ID=your_real_access_key
   AWS_SECRET_ACCESS_KEY=your_real_secret_key
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=your-s3-bucket-name
   ```

## Usage

### Using Poetry (Recommended)

1. Run the application:
   ```bash
   poetry run python main.py
   ```
   
   Or activate the virtual environment and run directly:
   ```bash
   poetry shell
   python main.py
   ```

### Using pip (Legacy)

1. Run the application:
   ```bash
   python main.py
   ```

2. The application will open in your web browser with two tabs:
   - **录音 (Recording)**: Use your microphone to record audio
   - **上传音频 (Upload Audio)**: Upload pre-recorded audio files

3. Advanced Settings (optional):
   - Click on "Advanced Settings" to expand additional options
   - Select a different Bedrock model from the dropdown list (Claude and Nova series)
   - **🆕 Enable Speaker Diarization**: Check this box to identify and label different speakers in multi-person conversations
   - Customize the prompt used for text optimization

4. **🆕 New Features**:
   - **Language Identification**: Automatically displays the detected language and confidence score
   - **Speaker Diarization**: When enabled, identifies up to 10 different speakers and shows their speech segments with timestamps

5. For microphone recording:
   - Click "Start Recording" to begin recording your voice
   - Speak clearly into your microphone
   - Click "Stop Recording" when you're done
   - Click "处理录音 (Process Recording)" to start processing

6. For file upload:
   - Click "Upload" and select an audio file (supported formats: mp3, mp4, wav, flac, ogg, amr, webm)
   - Click "处理上传的音频 (Process Uploaded Audio)" to start processing

7. The application will process your audio:
   - The left panel will show the raw transcription from AWS Transcribe
   - The right panel will show the optimized text from AWS Bedrock
   - **🆕 Enhanced Language Information** will be displayed with friendly language names, confidence levels, and language codes
   - **🆕 Rich Speaker Information** will be displayed with speaker statistics, time distribution, and detailed conversation timeline (if enabled)

## 🎨 Enhanced Output Display

The application now features beautifully formatted output with:

### Language Identification Display
- 🌍 **Friendly Language Names**: "英语(美国) | English (US)" instead of "en-US"
- 📊 **Descriptive Confidence Levels**: "非常高 | Very High" for scores ≥0.9
- 🔤 **Complete Language Information**: Code, name, and confidence in one view

### Speaker Diarization Display
- 👥 **Speaker Statistics**: Total speakers, duration, and language information
- 📈 **Speaker Distribution**: Time percentage and segment count for each speaker
- 📝 **Detailed Timeline**: Chronological conversation with formatted timestamps
- 🕐 **Time Formatting**: "00:05-00:10 (时长 00:05 | Duration 00:05)"
- 👤 **Friendly Speaker Names**: "发言者A | Speaker A" instead of "spk_0"

For detailed information about the enhanced output format, see [docs/OUTPUT_OPTIMIZATION.md](docs/OUTPUT_OPTIMIZATION.md).

## Notes

- The application uses AWS Transcribe's automatic language identification feature.
- You need to have an S3 bucket created for storing the temporary audio files.
- Make sure your AWS account has the necessary permissions for Transcribe and Bedrock services.
- **Model Compatibility**: The application uses an intelligent inference profile fallback mechanism. When a model requires an inference profile (like Claude 3.5 Sonnet v2, Claude 3.7 Sonnet, Claude 4 series), the system automatically detects this and seamlessly switches to the appropriate inference profile without user intervention.

## Troubleshooting

### Common Issues

#### Audio Upload Errors
If you encounter errors like "expected string or bytes-like object, got 'NoneType'", this usually means:
- No audio file was provided or the file path is invalid
- The audio file is corrupted or empty
- Network issues during file upload

**Solutions:**
- Ensure you have recorded or uploaded a valid audio file
- Check that the file format is supported (mp3, mp4, wav, flac, ogg, amr, webm)
- Verify the file size is under 2GB
- Try re-recording or re-uploading the audio

#### Configuration Errors
The application will check your configuration on startup and display any issues:
- **S3_BUCKET_NAME not set**: Add your S3 bucket name to the .env file
- **AWS credentials missing**: Configure your AWS access keys or use AWS profiles
- **Region not specified**: Set your preferred AWS region

#### AWS Permission Issues
- Verify your AWS credentials: `aws sts get-caller-identity`
- Check S3 bucket access: `aws s3 ls s3://your-bucket-name`
- Ensure your IAM user/role has permissions for S3, Transcribe, and Bedrock services

### Getting Help

For detailed troubleshooting steps, see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

### Logs

Check the application logs in the `logs/` directory:
- `voice_assistant.log` - General application logs
- `service_calls.log` - AWS service call logs
- `llm_calls.log` - Bedrock model interaction logs
