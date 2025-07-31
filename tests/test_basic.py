#!/usr/bin/env python3
"""
基础测试
Basic tests
"""
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Import after path modification
from voice_assistant.config import SUPPORTED_AUDIO_FORMATS, DEFAULT_AUDIO_FORMAT  # noqa: E402


def test_config_constants():
    """测试配置常量"""
    assert DEFAULT_AUDIO_FORMAT == "wav"
    assert isinstance(SUPPORTED_AUDIO_FORMATS, list)
    assert len(SUPPORTED_AUDIO_FORMATS) > 0
    assert "wav" in SUPPORTED_AUDIO_FORMATS


def test_supported_formats():
    """测试支持的音频格式"""
    expected_formats = ["mp3", "mp4", "wav", "flac", "ogg", "amr", "webm"]
    for fmt in expected_formats:
        assert fmt in SUPPORTED_AUDIO_FORMATS


def test_imports():
    """测试基本导入"""
    try:
        from voice_assistant import config
        from voice_assistant import logger
        from voice_assistant import aws_services
        from voice_assistant import ui
        from voice_assistant import main
        assert True
    except ImportError as e:
        assert False, f"Import failed: {e}"