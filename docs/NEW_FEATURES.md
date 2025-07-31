# 新增功能说明 | New Features Documentation

## 概述 | Overview

本次更新为transcribe模块添加了两个重要功能：
This update adds two important features to the transcribe module:

1. **语言识别显示** | Language Identification Display
2. **发言者划分功能** | Speaker Diarization Feature

## 功能详情 | Feature Details

### 1. 语言识别显示 | Language Identification Display

#### 功能描述 | Description
- 自动识别音频中的语言并显示识别结果
- 显示语言置信度分数
- 支持AWS Transcribe的所有语言识别功能

#### 显示信息 | Display Information
- 识别的语言代码（如：en-US, zh-CN, ja-JP等）
- 置信度分数（0.0-1.0）
- 双语显示格式

#### 示例输出 | Example Output
```
识别语言: en-US (置信度: 0.95) | Identified Language: en-US (Confidence: 0.95)
```

### 2. 发言者划分功能 | Speaker Diarization Feature

#### 功能描述 | Description
- 识别并标记音频中不同发言者的语音片段
- 支持最多10个发言者的识别
- 提供时间戳和发言者标签
- 适用于会议、访谈等多人对话场景

#### 功能特点 | Features
- **自动发言者检测**: 无需预先知道发言者数量
- **时间戳标记**: 每个语音片段都有开始和结束时间
- **发言者标签**: 自动分配发言者标签（如：spk_0, spk_1等）
- **文本分组**: 按发言者分组显示转录文本

#### 示例输出 | Example Output
```
识别到 2 个发言者 | Identified 2 speakers

**spk_0** (0s-5s): 大家好，欢迎参加今天的会议。

**spk_1** (6s-10s): 谢谢，很高兴能参与讨论。

**spk_0** (11s-15s): 那我们开始第一个议题吧。
```

## 界面更新 | UI Updates

### 新增控件 | New Controls

1. **发言者划分开关** | Speaker Diarization Toggle
   - 位置：高级设置面板中
   - 类型：复选框
   - 默认：关闭
   - 说明：启用后会增加处理时间但提供更详细的转录结果

2. **语言识别信息显示区** | Language Identification Display Area
   - 位置：输出区域下方左侧
   - 类型：只读文本框
   - 显示：识别的语言和置信度

3. **发言者信息显示区** | Speaker Information Display Area
   - 位置：输出区域下方右侧
   - 类型：只读文本框
   - 显示：发言者数量和按时间排序的发言内容

### 界面布局 | UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│                        标题和说明                            │
├─────────────────────────────────────────────────────────────┤
│                      高级设置面板                            │
│  ├─ 模型选择                                                │
│  ├─ 发言者划分开关 [新增]                                    │
│  └─ 自定义提示词                                            │
├─────────────────────────────────────────────────────────────┤
│                      音频输入选项卡                          │
├─────────────────────────────────────────────────────────────┤
│           转录输出          │         优化输出               │
├─────────────────────────────┼─────────────────────────────────┤
│      语言识别信息 [新增]     │      发言者信息 [新增]          │
├─────────────────────────────────────────────────────────────┤
│                        状态信息                              │
└─────────────────────────────────────────────────────────────┘
```

## 技术实现 | Technical Implementation

### 后端更新 | Backend Updates

#### 1. `transcribe_audio` 函数更新
```python
def transcribe_audio(s3_uri, audio_path, enable_speaker_diarization=False):
    # 新增参数：enable_speaker_diarization
    # 返回值：包含语言信息和发言者信息的字典
```

#### 2. `process_audio` 函数更新
```python
def process_audio(audio_file, model_id=None, custom_prompt=None, enable_speaker_diarization=False):
    # 新增参数：enable_speaker_diarization
    # 返回值：(转录文本, 优化文本, 语言信息, 发言者信息)
```

### AWS Transcribe 配置 | AWS Transcribe Configuration

#### 发言者划分设置 | Speaker Diarization Settings
```python
job_params = {
    "TranscriptionJobName": job_name,
    "Media": {"MediaFileUri": s3_uri},
    "MediaFormat": media_format,
    "IdentifyLanguage": True,
    "Settings": {
        "ShowSpeakerLabels": True,      # 启用发言者标签
        "MaxSpeakerLabels": 10,         # 最多10个发言者
    }
}
```

#### 语言识别增强 | Enhanced Language Identification
- 获取语言置信度分数
- 支持多语言识别结果
- 提供详细的语言识别信息

## 使用说明 | Usage Instructions

### 启用发言者划分 | Enable Speaker Diarization

1. 展开"高级设置"面板
2. 勾选"启用发言者划分"复选框
3. 录制或上传音频文件
4. 点击处理按钮
5. 查看发言者信息显示区的结果

### 查看语言识别结果 | View Language Identification Results

1. 处理任何音频文件（无需额外设置）
2. 查看"语言识别信息"显示区
3. 信息包含识别的语言代码和置信度

## 注意事项 | Important Notes

### 发言者划分 | Speaker Diarization
- ⏱️ **处理时间**: 启用发言者划分会增加处理时间
- 🎯 **准确性**: 在清晰的多人对话中效果最佳
- 📊 **限制**: 最多支持10个发言者
- 🔊 **音质要求**: 需要相对清晰的音频质量

### 语言识别 | Language Identification
- 🌍 **支持语言**: 支持AWS Transcribe的所有语言
- 📈 **置信度**: 置信度越高，识别越准确
- 🔄 **自动检测**: 无需手动指定语言

## 兼容性 | Compatibility

- ✅ 向后兼容：现有功能不受影响
- ✅ 可选功能：发言者划分为可选功能
- ✅ 默认行为：默认行为保持不变
- ✅ 错误处理：增强的错误处理和用户反馈

## 测试建议 | Testing Recommendations

### 测试场景 | Test Scenarios

1. **单人录音** | Single Speaker
   - 测试语言识别功能
   - 验证发言者划分关闭时的行为

2. **多人对话** | Multi-Speaker Conversation
   - 测试发言者划分功能
   - 验证时间戳准确性

3. **多语言音频** | Multi-Language Audio
   - 测试语言识别的准确性
   - 验证置信度显示

4. **音质测试** | Audio Quality Test
   - 测试不同音质下的表现
   - 验证错误处理机制

## 更新日志 | Changelog

### v1.1.0 (当前版本)
- ✨ 新增语言识别显示功能
- ✨ 新增发言者划分功能
- 🔧 更新UI界面布局
- 📝 增强错误处理和用户反馈
- 📚 添加功能说明文档

---

*如有问题或建议，请查看项目文档或提交Issue。*
*For questions or suggestions, please refer to the project documentation or submit an Issue.*