# AWS凭证配置指南 | AWS Credentials Setup Guide

## 🔑 AWS凭证配置方法 | AWS Credentials Configuration Methods

### 方法1：使用.env文件 | Method 1: Using .env file

1. **获取AWS凭证 | Get AWS Credentials**
   - 登录AWS控制台 | Login to AWS Console
   - 进入IAM服务 | Go to IAM Service
   - 创建或使用现有用户 | Create or use existing user
   - 生成访问密钥 | Generate access keys

2. **编辑.env文件 | Edit .env file**
   ```bash
   # 替换为您的真实AWS凭证 | Replace with your real AWS credentials
   AWS_ACCESS_KEY_ID=AKIA...your_real_access_key
   AWS_SECRET_ACCESS_KEY=your_real_secret_key
   AWS_REGION=us-east-1
   
   # S3配置 | S3 Configuration
   S3_BUCKET_NAME=your-s3-bucket-name
   ```

### 方法2：使用AWS Profile | Method 2: Using AWS Profile

1. **配置AWS CLI | Configure AWS CLI**
   ```bash
   aws configure
   # 或使用命名配置文件 | Or use named profile
   aws configure --profile your-profile-name
   ```

2. **更新.env文件使用Profile | Update .env to use Profile**
   ```bash
   # 注释掉Access Key配置 | Comment out Access Key config
   # AWS_ACCESS_KEY_ID=
   # AWS_SECRET_ACCESS_KEY=
   
   # 使用AWS Profile | Use AWS Profile
   AWS_PROFILE=your-profile-name
   AWS_REGION=us-east-1
   
   S3_BUCKET_NAME=your-s3-bucket-name
   ```

### 方法3：使用环境变量 | Method 3: Using Environment Variables

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

## 🔐 所需权限 | Required Permissions

您的AWS用户需要以下权限 | Your AWS user needs these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:ListFoundationModels",
                "bedrock:InvokeModel",
                "transcribe:StartTranscriptionJob",
                "transcribe:GetTranscriptionJob",
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": "*"
        }
    ]
}
```

## 🧪 测试AWS凭证 | Test AWS Credentials

### 1. 测试基本连接 | Test Basic Connection
```bash
aws sts get-caller-identity
```

### 2. 测试Bedrock权限 | Test Bedrock Permissions
```bash
aws bedrock list-foundation-models --region us-east-1
```

### 3. 测试S3权限 | Test S3 Permissions
```bash
aws s3 ls s3://your-bucket-name
```

## ⚠️ 常见问题 | Common Issues

### 1. 区域问题 | Region Issues
- 确保AWS_REGION与您的资源区域匹配
- Bedrock服务在某些区域可能不可用

### 2. 权限问题 | Permission Issues
- 检查IAM用户是否有Bedrock访问权限
- 确认S3存储桶权限

### 3. 凭证格式问题 | Credential Format Issues
- Access Key ID通常以AKIA开头
- Secret Access Key是40字符的字符串
- 不要在凭证中包含空格或特殊字符

## 🔒 安全建议 | Security Recommendations

1. **不要提交凭证到Git** | Don't commit credentials to Git
   - .env文件已在.gitignore中
   - 使用.env.example作为模板

2. **定期轮换凭证** | Regularly rotate credentials
   - 定期更新Access Keys
   - 使用临时凭证（STS）

3. **最小权限原则** | Principle of least privilege
   - 只授予必要的权限
   - 使用资源级权限限制

## 🚀 快速修复 | Quick Fix

如果您急需测试应用，可以：

1. **使用AWS CLI配置** | Use AWS CLI configuration
   ```bash
   aws configure
   ```

2. **或者编辑.env文件** | Or edit .env file
   ```bash
   cp .env.example .env
   # 然后编辑.env文件，填入真实凭证
   ```

3. **验证配置** | Verify configuration
   ```bash
   make config-test
   ```