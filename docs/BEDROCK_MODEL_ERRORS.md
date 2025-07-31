# Bedrock模型错误处理指南 | Bedrock Model Error Handling Guide

## 🚨 常见错误 | Common Errors

### 1. 不支持按需调用错误 | On-Demand Throughput Not Supported Error

**错误信息 | Error Message:**
```
ValidationException: Invocation of model ID anthropic.claude-3-7-sonnet-20250219-v1:0 with on-demand throughput isn't supported. Retry your request with the ID or ARN of an inference profile that contains this model.
```

**原因 | Cause:**
某些较新的Bedrock模型（如Claude 3.7 Sonnet、Claude 4系列）不支持直接的按需调用，需要使用推理配置文件（inference profile）。

**解决方案 | Solutions:**

#### 方案1：自动模型切换（推荐）✅
应用已经实现了自动模型验证和切换功能：

- 当选择不支持的模型时，系统会自动切换到默认的支持模型
- 用户会看到日志提示模型已被更改
- 不需要用户手动操作

#### 方案2：手动选择支持的模型
在应用界面中选择以下支持按需调用的模型：

**推荐的Claude模型:**
- `anthropic.claude-3-5-sonnet-20241022-v2:0` (默认)
- `anthropic.claude-3-sonnet-20240229-v1:0`
- `anthropic.claude-3-haiku-20240307-v1:0`

**推荐的Nova模型:**
- `amazon.nova-pro-v1:0`
- `amazon.nova-lite-v1:0`
- `amazon.nova-micro-v1:0`

### 2. 不支持的模型列表 | Unsupported Models List

以下模型**不支持**按需调用，会被自动过滤或切换：

```
❌ anthropic.claude-3-7-sonnet-20250219-v1:0    # Claude 3.7 Sonnet
❌ anthropic.claude-opus-4-20250514-v1:0        # Claude Opus 4
❌ anthropic.claude-sonnet-4-20250514-v1:0      # Claude Sonnet 4
```

## 🔧 故障排除步骤 | Troubleshooting Steps

### 步骤1：检查当前模型配置
```bash
# 运行模型验证测试
make model-validation

# 查看可用模型列表
make model-test
```

### 步骤2：验证AWS配置
```bash
# 诊断AWS凭证和权限
make aws-diagnose
```

### 步骤3：检查应用日志
查看应用日志中的模型切换信息：
```
模型已从 anthropic.claude-3-7-sonnet-20250219-v1:0 更改为 anthropic.claude-3-5-sonnet-20241022-v2:0
```

## 🛡️ 预防措施 | Prevention Measures

### 1. 自动模型过滤
应用已实现以下保护机制：

- **模型黑名单**: 自动排除已知不支持的模型
- **模式匹配**: 检测模型名称中的不支持模式
- **自动切换**: 不支持的模型自动切换到默认模型

### 2. 用户界面优化
- 模型选择列表只显示支持按需调用的模型
- 不支持的模型不会出现在下拉菜单中
- 提供模型友好名称而不是技术ID

### 3. 日志和监控
- 详细的模型切换日志
- 错误处理和回退机制
- 用户友好的错误消息

## 📊 模型性能对比 | Model Performance Comparison

| 模型系列 | 支持状态 | 性能 | 成本 | 推荐用途 |
|---------|---------|------|------|---------|
| Claude 3.5 Sonnet | ✅ 支持 | 高 | 中等 | 通用文本处理 |
| Claude 3 Sonnet | ✅ 支持 | 中高 | 中等 | 平衡性能和成本 |
| Claude 3 Haiku | ✅ 支持 | 中等 | 低 | 快速响应场景 |
| Nova Pro | ✅ 支持 | 高 | 中等 | 复杂任务处理 |
| Nova Lite | ✅ 支持 | 中等 | 低 | 轻量级任务 |
| Nova Micro | ✅ 支持 | 低 | 很低 | 简单文本处理 |

## 🔮 未来支持 | Future Support

### 推理配置文件支持
未来版本可能会添加对推理配置文件的支持，以使用更新的模型：

```python
# 未来可能的实现
def create_inference_profile(model_id):
    """创建推理配置文件以支持新模型"""
    # 实现推理配置文件创建逻辑
    pass
```

### 动态模型检测
计划实现动态检测模型支持状态的功能：

```python
def check_model_support_dynamically(model_id):
    """动态检查模型是否支持按需调用"""
    # 实现动态检测逻辑
    pass
```

## 📞 获取帮助 | Getting Help

如果遇到模型相关问题：

1. **检查日志**: 查看 `logs/voice_assistant.log` 中的详细错误信息
2. **运行诊断**: 使用 `make aws-diagnose` 检查AWS配置
3. **验证模型**: 使用 `make model-validation` 测试模型支持状态
4. **查看文档**: 参考AWS Bedrock官方文档了解最新模型支持情况

## 🔗 相关资源 | Related Resources

- [AWS Bedrock用户指南](https://docs.aws.amazon.com/bedrock/latest/userguide/)
- [Bedrock模型支持文档](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)
- [推理配置文件文档](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html)

---

通过这些措施，应用现在能够自动处理模型兼容性问题，为用户提供无缝的体验！🎉