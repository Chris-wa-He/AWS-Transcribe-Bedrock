# Development Guide

This guide covers development setup and workflows for the AWS Transcribe Bedrock Voice Assistant project.

## Quick Start

1. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install dependencies**:
   ```bash
   poetry install
   ```

3. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your AWS credentials
   ```

4. **Run the application**:
   ```bash
   poetry run python main.py
   # or
   make run
   ```

## Development Workflow

### Using Poetry Commands

- **Install dependencies**: `poetry install`
- **Add new dependency**: `poetry add package-name`
- **Add dev dependency**: `poetry add --group dev package-name`
- **Run application**: `poetry run python main.py`
- **Activate shell**: `poetry shell`
- **Show dependencies**: `poetry show --tree`

### Using Make Commands

- **Install**: `make install`
- **Run app**: `make run`
- **Activate shell**: `make shell`
- **Format code**: `make format`
- **Lint code**: `make lint`
- **Run tests**: `make test`
- **Clean cache**: `make clean`

## Code Quality

### Formatting with Black
```bash
poetry run black *.py
# or
make format
```

### Linting with Flake8
```bash
poetry run flake8 *.py
# or
make lint
```

### Type Checking with MyPy
```bash
poetry run mypy *.py
```

## Testing

### Running Tests
```bash
poetry run pytest
# or
make test
```

### Adding Tests
Create test files in a `tests/` directory following the pattern `test_*.py`.

## Project Structure

```
AWS-Transcribe-Bedrock/
├── main.py              # Application entry point
├── ui.py                # Gradio UI components
├── aws_services.py      # AWS service integrations
├── config.py            # Configuration management
├── logger.py            # Logging setup
├── run.py               # Alternative runner script
├── pyproject.toml       # Poetry configuration
├── Makefile             # Development commands
├── .env.example         # Environment template
├── .gitignore           # Git ignore rules
├── README.md            # Main documentation
├── README.zh.md         # Chinese documentation
└── DEVELOPMENT.md       # This file
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1

# S3 Configuration
S3_BUCKET_NAME=your-bucket-name

# Optional: Specific AWS Profile
AWS_PROFILE=your-profile-name
```

## Dependencies

### Production Dependencies
- **boto3**: AWS SDK for Python
- **gradio**: Web UI framework
- **python-dotenv**: Environment variable management
- **requests**: HTTP library

### Development Dependencies
- **pytest**: Testing framework
- **black**: Code formatter
- **flake8**: Code linter
- **mypy**: Static type checker

## Troubleshooting

### Poetry Issues
- **Lock file conflicts**: `poetry lock --no-update`
- **Cache issues**: `poetry cache clear pypi --all`
- **Virtual env issues**: `poetry env remove python && poetry install`

### Python Version Issues
- This project requires Python 3.10+
- Check version: `python --version`
- Use pyenv if needed: `pyenv install 3.10.0 && pyenv local 3.10.0`

### AWS Configuration
- Verify credentials: `aws sts get-caller-identity`
- Check region: `aws configure get region`
- Test S3 access: `aws s3 ls s3://your-bucket-name`

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and test: `make test`
4. Format code: `make format`
5. Lint code: `make lint`
6. Commit changes: `git commit -am "Add feature"`
7. Push branch: `git push origin feature-name`
8. Create Pull Request

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create git tag: `git tag v0.1.0`
4. Push tag: `git push origin v0.1.0`

## Additional Resources

- [Poetry Documentation](https://python-poetry.org/docs/)
- [AWS Transcribe Documentation](https://docs.aws.amazon.com/transcribe/)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Gradio Documentation](https://gradio.app/docs/)