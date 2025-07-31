# AWS Profile 配置指南 | AWS Profile Setup Guide

## 🎯 为什么使用AWS Profile？| Why Use AWS Profile?

使用AWS Profile比直接在.env文件中存储凭证更安全、更灵活：

**优势 | Advantages:**
- ✅ **安全性更高** - 凭证存储在AWS CLI配置中，不会意外提交到Git
- ✅ **多账户支持** - 可以轻松切换不同的AWS账户和角色
- ✅ **统一管理** - 与其他AWS工具共享相同的凭证配置
- ✅ **支持临时凭证** - 可以使用STS临时凭证和角色

## 🛠️ 配置步骤 | Setup Steps

### 1. 安装和配置AWS CLI

```bash
# 检查是否已安装AWS CLI
aws --version

# 如果未安装，可以通过以下方式安装：
# macOS (使用Homebrew)
brew install awscli

# 或者使用pip
pip install awscli
```

### 2. 配置默认Profile

```bash
# 配置默认profile
aws configure

# 系统会提示输入：
# AWS Access Key ID [None]: AKIA1234567890EXAMPLE
# AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
# Default region name [None]: us-east-1
# Default output format [None]: json
```

### 3. 配置命名Profile（推荐）

```bash
# 配置命名profile
aws configure --profile my-bedrock-profile

# 或者手动编辑配置文件
# ~/.aws/credentials
[my-bedrock-profile]
aws_access_key_id = AKIA1234567890EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# ~/.aws/config
[profile my-bedrock-profile]
region = us-east-1
output = json
```

### 4. 配置应用使用Profile

编辑项目根目录的`.env`文件：

```bash
# 注释掉Access Key配置
# AWS_ACCESS_KEY_ID=your_access_key_id
# AWS_SECRET_ACCESS_KEY=your_secret_access_key

# 使用AWS Profile
AWS_PROFILE=my-bedrock-profile
AWS_REGION=us-east-1

# S3配置
S3_BUCKET_NAME=your-s3-bucket-name
```

## 🧪 验证配置 | Verify Configuration

### 1. 测试AWS CLI

```bash
# 测试默认profile
aws sts get-caller-identity

# 测试指定profile
aws sts get-caller-identity --profile my-bedrock-profile

# 测试Bedrock访问
aws bedrock list-foundation-models --region us-east-1 --profile my-bedrock-profile
```

### 2. 测试应用配置

```bash
# 运行应用的AWS诊断
make aws-diagnose

# 或者测试配置
make config-test
```

## 🔄 多Profile管理 | Multiple Profile Management

### 创建多个Profile

```bash
# 开发环境
aws configure --profile dev-bedrock
# 生产环境  
aws configure --profile prod-bedrock
# 测试环境
aws configure --profile test-bedrock
```

### 切换Profile

只需要修改`.env`文件中的`AWS_PROFILE`值：

```bash
# 切换到开发环境
AWS_PROFILE=dev-bedrock

# 切换到生产环境
AWS_PROFILE=prod-bedrock
```

## 🔐 高级配置 | Advanced Configuration

### 使用IAM角色

```bash
# ~/.aws/config
[profile bedrock-role]
role_arn = arn:aws:iam::123456789012:role/BedrockAccessRole
source_profile = default
region = us-east-1
```

### 使用SSO

```bash
# 配置SSO
aws configure sso

# ~/.aws/config
[profile bedrock-sso]
sso_start_url = https://my-company.awsapps.com/start
sso_region = us-east-1
sso_account_id = 123456789012
sso_role_name = BedrockDeveloper
region = us-east-1
```

### 使用MFA

```bash
# ~/.aws/config
[profile bedrock-mfa]
role_arn = arn:aws:iam::123456789012:role/BedrockMFARole
source_profile = default
mfa_serial = arn:aws:iam::123456789012:mfa/username
region = us-east-1
```

## 🚨 故障排除 | Troubleshooting

### 常见问题

1. **Profile不存在**
   ```bash
   # 检查可用的profiles
   aws configure list-profiles
   ```

2. **权限不足**
   ```bash
   # 检查当前身份
   aws sts get-caller-identity --profile your-profile
   ```

3. **区域不匹配**
   ```bash
   # 检查profile配置
   aws configure get region --profile your-profile
   ```

### 调试命令

```bash
# 查看当前配置
aws configure list --profile your-profile

# 查看所有profiles
cat ~/.aws/credentials
cat ~/.aws/config

# 测试特定服务访问
aws bedrock list-foundation-models --profile your-profile --region us-east-1
```

## 📝 最佳实践 | Best Practices

1. **使用命名Profile** - 避免使用默认profile，使用有意义的名称
2. **最小权限原则** - 只授予必要的权限
3. **定期轮换凭证** - 定期更新Access Keys
4. **使用临时凭证** - 在可能的情况下使用STS临时凭证
5. **环境分离** - 为不同环境使用不同的profiles

## 🔗 相关文档 | Related Documentation

- [AWS CLI配置文档](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
- [AWS Profile配置](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html)
- [IAM最佳实践](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

---

配置完成后，应用将自动使用指定的AWS Profile进行所有AWS服务调用！🎉