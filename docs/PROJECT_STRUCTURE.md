# 项目结构说明 | Project Structure

本文档描述了Voice Assistant项目的标准Python项目结构。

This document describes the standard Python project structure for the Voice Assistant project.

## 目录结构 | Directory Structure

```
AWS-Transcribe-Bedrock/
├── src/                          # 源代码目录 | Source code directory
│   └── voice_assistant/          # 主应用包 | Main application package
│       ├── __init__.py          # 包初始化文件 | Package initialization
│       ├── main.py              # 主应用模块 | Main application module
│       ├── ui.py                # 用户界面模块 | User interface module
│       ├── aws_services.py      # AWS服务集成 | AWS services integration
│       ├── config.py            # 配置管理 | Configuration management
│       └── logger.py            # 日志系统 | Logging system
├── tests/                        # 测试目录 | Tests directory
│   ├── __init__.py              # 测试包初始化 | Test package initialization
│   ├── test_config.py           # 配置测试 | Configuration tests
│   └── test_models.py           # 模型测试 | Model tests
├── docs/                         # 文档目录 | Documentation directory
│   ├── DEVELOPMENT.md           # 开发指南 | Development guide
│   ├── TROUBLESHOOTING.md       # 故障排除 | Troubleshooting guide
│   ├── README.zh.md             # 中文说明 | Chinese README
│   └── PROJECT_STRUCTURE.md     # 项目结构说明 | Project structure guide
├── scripts/                      # 脚本目录 | Scripts directory
│   └── run.py                   # 运行脚本 | Run script
├── config/                       # 配置文件目录 | Configuration files directory
│   └── .env.example             # 环境变量示例 | Environment variables example
├── logs/                         # 日志目录 | Logs directory
├── main.py                       # 应用入口点 | Application entry point
├── pyproject.toml               # Poetry配置 | Poetry configuration
├── requirements.txt             # pip依赖列表 | pip requirements
├── Makefile                     # 开发命令 | Development commands
├── README.md                    # 项目说明 | Project README
├── LICENSE                      # 许可证 | License
└── .gitignore                   # Git忽略文件 | Git ignore file
```

## 目录说明 | Directory Descriptions

### `src/voice_assistant/` - 源代码包
主要的应用程序代码，按功能模块组织：

Main application code, organized by functional modules:

- **`__init__.py`**: 包初始化，定义版本和导出 | Package initialization, defines version and exports
- **`main.py`**: 应用程序入口点和启动逻辑 | Application entry point and startup logic
- **`ui.py`**: Gradio用户界面组件 | Gradio user interface components
- **`aws_services.py`**: AWS服务集成（S3, Transcribe, Bedrock）| AWS services integration (S3, Transcribe, Bedrock)
- **`config.py`**: 配置管理和验证 | Configuration management and validation
- **`logger.py`**: 日志系统设置 | Logging system setup

### `tests/` - 测试目录
包含所有测试文件：

Contains all test files:

- **`test_config.py`**: 配置系统测试 | Configuration system tests
- **`test_models.py`**: 模型过滤功能测试 | Model filtering functionality tests

### `docs/` - 文档目录
项目文档和指南：

Project documentation and guides:

- **`DEVELOPMENT.md`**: 开发环境设置和工作流程 | Development environment setup and workflow
- **`TROUBLESHOOTING.md`**: 常见问题和解决方案 | Common issues and solutions
- **`README.zh.md`**: 中文版项目说明 | Chinese version of project README
- **`PROJECT_STRUCTURE.md`**: 本文件，项目结构说明 | This file, project structure guide

### `scripts/` - 脚本目录
实用脚本和工具：

Utility scripts and tools:

- **`run.py`**: 备用运行脚本 | Alternative run script

### `config/` - 配置目录
配置文件和模板：

Configuration files and templates:

- **`.env.example`**: 环境变量配置模板 | Environment variables configuration template

## 导入路径 | Import Paths

### 在包内部 | Within the Package
使用相对导入：
```python
from .config import BEDROCK_MODEL_ID
from .aws_services import get_available_models
```

### 从外部访问 | External Access
使用绝对导入：
```python
from voice_assistant.main import main
from voice_assistant.config import get_configuration_status
```

## 运行方式 | Running Methods

### 1. 主入口点 | Main Entry Point
```bash
python main.py
```

### 2. 使用Poetry | Using Poetry
```bash
poetry run python main.py
```

### 3. 使用Makefile | Using Makefile
```bash
make run
```

### 4. 使用脚本 | Using Script
```bash
python scripts/run.py
```

## 开发工作流 | Development Workflow

### 添加新功能 | Adding New Features
1. 在 `src/voice_assistant/` 中创建新模块
2. 在 `tests/` 中添加相应测试
3. 更新文档

### 测试 | Testing
```bash
# 运行所有测试
make test

# 配置测试
make config-test

# 模型测试
make model-test
```

### 代码质量 | Code Quality
```bash
# 格式化代码
make format

# 代码检查
make lint
```

## 优势 | Benefits

### 1. 标准化结构 | Standardized Structure
- 符合Python项目最佳实践
- 易于理解和维护
- 便于团队协作

### 2. 清晰的分离 | Clear Separation
- 源代码与测试分离
- 文档集中管理
- 配置文件独立存放

### 3. 可扩展性 | Scalability
- 易于添加新模块
- 支持包级别的组织
- 便于代码重用

### 4. 开发友好 | Developer Friendly
- 清晰的导入路径
- 统一的运行方式
- 完整的开发工具链

## 迁移说明 | Migration Notes

从旧的扁平结构迁移到新结构时：

When migrating from the old flat structure to the new structure:

1. **导入路径更新**: 所有内部导入改为相对导入
2. **测试路径调整**: 测试文件需要添加路径设置
3. **配置文件移动**: 环境变量示例移至config目录
4. **文档整理**: 相关文档移至docs目录

这种结构使项目更加专业化，便于维护和扩展。