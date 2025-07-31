.PHONY: install run shell clean lint format test help config-test model-test aws-diagnose model-validation inference-profile-test fallback-test

# Default target
help:
	@echo "Available commands:"
	@echo "  install                - Install dependencies using Poetry"
	@echo "  run                    - Run the voice assistant application"
	@echo "  shell                  - Activate Poetry shell"
	@echo "  clean                  - Clean up cache and temporary files"
	@echo "  lint                   - Run code linting with flake8"
	@echo "  format                 - Format code with black"
	@echo "  test                   - Run tests with pytest"
	@echo "  config-test            - Test application configuration"
	@echo "  model-test             - Test Bedrock model filtering"
	@echo "  aws-diagnose           - Diagnose AWS credentials and permissions"
	@echo "  model-validation       - Test model validation and filtering logic"
	@echo "  inference-profile-test - Test inference profile functionality"
	@echo "  fallback-test          - Test new inference profile fallback mechanism"

# Install dependencies
install:
	poetry install

# Run the application
run:
	poetry run python main.py

# Run using script
run-script:
	poetry run python scripts/run.py

# Activate Poetry shell
shell:
	poetry shell

# Clean up
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

# Lint code
lint:
	poetry run flake8 src/ tests/ scripts/ main.py

# Format code
format:
	poetry run black src/ tests/ scripts/ main.py

# Run tests
test:
	poetry run pytest

# Test configuration
config-test:
	poetry run python tests/test_config.py

# Test model filtering
model-test:
	poetry run python tests/test_models.py

# Diagnose AWS credentials and permissions
aws-diagnose:
	poetry run python scripts/diagnose_aws.py

# Test model validation and filtering logic
model-validation:
	poetry run python scripts/test_model_validation.py

# Test inference profile functionality
inference-profile-test:
	poetry run python scripts/test_inference_profiles.py

# Test new inference profile fallback mechanism
fallback-test:
	poetry run python scripts/test_new_fallback.py