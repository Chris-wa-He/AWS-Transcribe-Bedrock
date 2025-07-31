# 项目结构说明 | Project Structure Guide

## 项目概述 | Project Overview

语音助手项目是一个基于AWS服务的语音转录和文本优化应用程序，采用模块化设计，便于用户理解和使用。

The Voice Assistant project is a voice transcription and text optimization application based on AWS services, designed with a modular structure for easy understanding and usage.

## 📁 项目目录结构 | Project Directory Structure

```
AWS-Transcribe-Bedrock/
├── 📄 README.md                    # 主要使用说明 | Main usage guide
├── 📄 README.zh.md                 # 中文使用说明 | Chinese usage guide
├── 📄 main.py                      # 应用程序入口 | Application entry point
├── 📄 requirements.txt             # Python依赖列表 | Python dependencies
├── 📄 pyproject.toml              # Poetry配置文件 | Poetry configuration
├── 📄 .env.example                # 环境变量示例 | Environment variables example
├── 📄 LICENSE                     # 开源许可证 | Open source license
│
├── 📁 src/voice_assistant/         # 核心应用代码 | Core application code
│   ├── 📄 __init__.py             # Python包初始化 | Python package init
│   ├── 📄 main.py                 # 主程序逻辑 | Main program logic
│   ├── 📄 ui.py                   # 用户界面模块 | User interface module
│   ├── 📄 aws_services.py         # AWS服务集成 | AWS services integration
│   ├── 📄 config.py               # 配置管理 | Configuration management
│   ├── 📄 logger.py               # 日志系统 | Logging system
│   ├── 📄 output_formatter.py     # 输出格式化 | Output formatting
│   └── 📄 speaker_text_extractor.py # 发言者文本提取 | Speaker text extraction
│
├── 📁 docs/                       # 用户文档 | User documentation
│   ├── 📄 README.md               # 文档索引 | Documentation index
│   ├── 📄 NEW_FEATURES.md         # 新功能说明 | New features guide
│   ├── 📄 OUTPUT_OPTIMIZATION.md  # 输出优化说明 | Output optimization guide
│   ├── 📄 AWS_CREDENTIALS_SETUP.md # AWS凭证配置 | AWS credentials setup
│   ├── 📄 AWS_PROFILE_SETUP.md    # AWS配置文件设置 | AWS profile setup
│   ├── 📄 TROUBLESHOOTING.md      # 故障排除指南 | Troubleshooting guide
│   └── 📄 BEDROCK_MODEL_ERRORS.md # Bedrock错误处理 | Bedrock error handling
│
├── 📁 config/                     # 配置文件目录 | Configuration files
├── 📁 logs/                       # 日志文件目录 | Log files directory
└── 📁 scripts/                    # 辅助脚本 | Helper scripts
```

## 🔧 核心模块说明 | Core Modules Description

### 📄 main.py
应用程序的主入口点，负责启动Gradio界面和初始化系统。

Main entry point of the application, responsible for starting the Gradio interface and system initialization.

### 📁 src/voice_assistant/
包含所有核心功能模块的主要代码目录。

Main code directory containing all core functional modules.

#### 🎯 主要模块 | Main Modules

**ui.py** - 用户界面模块
- 创建和管理Gradio网页界面
- 处理用户交互和文件上传
- 显示转录结果和优化文本
- 提供高级设置选项（模型选择、发言者划分等）

**aws_services.py** - AWS服务集成
- 管理AWS Transcribe转录服务
- 集成AWS Bedrock文本优化
- 处理S3文件上传和存储
- 实现发言者划分功能

**config.py** - 配置管理
- 加载环境变量和配置文件
- 管理AWS凭证和区域设置
- 定义支持的音频格式和模型参数

**logger.py** - 日志系统
- 提供结构化日志记录
- 支持日志文件自动轮换
- 记录服务调用和错误信息

**output_formatter.py** - 输出格式化
- 格式化语言识别结果
- 美化发言者信息显示
- 提供友好的时间和置信度格式

**speaker_text_extractor.py** - 发言者文本提取
- 从AWS Transcribe结果中提取发言者文本
- 实现多种文本提取策略
- 处理时间戳匹配和文本分割

## 📚 文档结构说明 | Documentation Structure

### 🚀 快速开始文档
- **README.md** - 完整的安装和使用指南
- **README.zh.md** - 中文版使用指南

### 📖 功能说明文档
- **NEW_FEATURES.md** - 详细的新功能介绍
- **OUTPUT_OPTIMIZATION.md** - 输出格式优化说明

### ⚙️ 配置指南
- **AWS_CREDENTIALS_SETUP.md** - AWS凭证配置步骤
- **AWS_PROFILE_SETUP.md** - AWS配置文件设置方法

### 🔧 问题解决
- **TROUBLESHOOTING.md** - 常见问题和解决方案
- **BEDROCK_MODEL_ERRORS.md** - Bedrock模型错误处理

## 🗂️ 配置和数据目录 | Configuration and Data Directories

### 📁 config/
存储应用程序配置文件，包括：
- 模型配置参数
- 服务端点设置
- 默认提示词模板

### 📁 logs/
存储应用程序运行日志，包括：
- `voice_assistant.log` - 主应用程序日志
- `service_calls.log` - AWS服务调用日志
- `llm_calls.log` - Bedrock模型交互日志

### 📁 scripts/
包含辅助脚本，用于：
- 环境设置和检查
- 配置验证
- 系统诊断

## 🔄 应用程序工作流程 | Application Workflow

```
用户输入音频 → S3上传 → AWS Transcribe转录 → 文本优化 → 结果显示
     ↓              ↓           ↓              ↓         ↓
  录音/上传    →   临时存储  →   语音识别    →  Bedrock优化 → 格式化输出
                              ↓
                         发言者划分(可选)
```

## 📦 依赖管理 | Dependency Management

### Poetry方式（推荐）
- `pyproject.toml` - Poetry项目配置
- `poetry.lock` - 锁定的依赖版本

### pip方式
- `requirements.txt` - pip依赖列表

## 🌐 多语言支持 | Multi-language Support

项目支持中英双语：
- 界面文本支持中英文显示
- 文档提供中英文版本
- 错误信息包含双语说明
- 输出结果采用双语格式

## 🔐 安全和配置 | Security and Configuration

### 环境变量管理
- `.env.example` - 环境变量模板
- `.env` - 实际配置文件（不包含在版本控制中）

### AWS凭证安全
- 支持AWS Profile配置（推荐）
- 支持环境变量配置
- 不在代码中硬编码凭证信息

## 📊 日志和监控 | Logging and Monitoring

应用程序提供详细的日志记录：
- **操作日志** - 记录用户操作和系统状态
- **服务调用日志** - 记录AWS服务调用详情
- **错误日志** - 记录异常和错误信息
- **性能日志** - 记录处理时间和性能指标

## 🎯 使用建议 | Usage Recommendations

### 新用户入门
1. 阅读 `README.md` 了解基本功能
2. 按照安装指南配置环境
3. 参考配置文档设置AWS凭证
4. 运行应用程序开始使用

### 功能探索
1. 查看 `NEW_FEATURES.md` 了解最新功能
2. 尝试不同的模型和设置选项
3. 使用发言者划分功能处理多人对话

### 问题解决
1. 查看 `logs/` 目录中的日志文件
2. 参考 `TROUBLESHOOTING.md` 寻找解决方案
3. 检查AWS配置和权限设置

---

*这个项目结构设计注重用户体验和功能模块化，便于理解、使用和维护。*

*This project structure is designed with focus on user experience and functional modularity, making it easy to understand, use, and maintain.*