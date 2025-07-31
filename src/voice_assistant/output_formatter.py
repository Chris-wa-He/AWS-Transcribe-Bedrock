"""
输出格式化模块，负责格式化转录结果和发言者信息的显示
Output formatting module, responsible for formatting transcription results and speaker information display
"""

def format_language_name(language_code):
    """
    将语言代码转换为友好的语言名称
    Convert language code to friendly language name
    """
    language_map = {
        'en-US': '英语(美国) | English (US)',
        'en-GB': '英语(英国) | English (UK)',
        'en-AU': '英语(澳大利亚) | English (Australia)',
        'zh-CN': '中文(简体) | Chinese (Simplified)',
        'zh-TW': '中文(繁体) | Chinese (Traditional)',
        'ja-JP': '日语 | Japanese',
        'ko-KR': '韩语 | Korean',
        'fr-FR': '法语 | French',
        'de-DE': '德语 | German',
        'es-ES': '西班牙语 | Spanish',
        'it-IT': '意大利语 | Italian',
        'pt-BR': '葡萄牙语(巴西) | Portuguese (Brazil)',
        'ru-RU': '俄语 | Russian',
        'ar-SA': '阿拉伯语 | Arabic',
        'hi-IN': '印地语 | Hindi',
        'th-TH': '泰语 | Thai',
        'vi-VN': '越南语 | Vietnamese',
        'nl-NL': '荷兰语 | Dutch',
        'sv-SE': '瑞典语 | Swedish',
        'da-DK': '丹麦语 | Danish',
        'no-NO': '挪威语 | Norwegian',
        'fi-FI': '芬兰语 | Finnish',
        'pl-PL': '波兰语 | Polish',
        'cs-CZ': '捷克语 | Czech',
        'hu-HU': '匈牙利语 | Hungarian',
        'ro-RO': '罗马尼亚语 | Romanian',
        'bg-BG': '保加利亚语 | Bulgarian',
        'hr-HR': '克罗地亚语 | Croatian',
        'sk-SK': '斯洛伐克语 | Slovak',
        'sl-SI': '斯洛文尼亚语 | Slovenian',
        'et-EE': '爱沙尼亚语 | Estonian',
        'lv-LV': '拉脱维亚语 | Latvian',
        'lt-LT': '立陶宛语 | Lithuanian',
        'mt-MT': '马耳他语 | Maltese',
        'ga-IE': '爱尔兰语 | Irish',
        'cy-GB': '威尔士语 | Welsh',
    }
    
    return language_map.get(language_code, f'{language_code} | {language_code}')


def format_confidence_level(confidence):
    """
    将置信度数值转换为描述性文字
    Convert confidence score to descriptive text
    """
    if confidence >= 0.9:
        return "非常高 | Very High"
    elif confidence >= 0.8:
        return "高 | High"
    elif confidence >= 0.7:
        return "中等 | Medium"
    elif confidence >= 0.6:
        return "较低 | Low"
    else:
        return "很低 | Very Low"


def format_speaker_name(speaker_label):
    """
    将发言者标签转换为友好的显示名称
    Convert speaker label to friendly display name
    """
    speaker_map = {
        'spk_0': '发言者A | Speaker A',
        'spk_1': '发言者B | Speaker B', 
        'spk_2': '发言者C | Speaker C',
        'spk_3': '发言者D | Speaker D',
        'spk_4': '发言者E | Speaker E',
        'spk_5': '发言者F | Speaker F',
        'spk_6': '发言者G | Speaker G',
        'spk_7': '发言者H | Speaker H',
        'spk_8': '发言者I | Speaker I',
        'spk_9': '发言者J | Speaker J',
    }
    
    return speaker_map.get(speaker_label, f'{speaker_label} | {speaker_label}')


def format_time_duration(start_time, end_time):
    """
    格式化时间段显示
    Format time duration display
    """
    def seconds_to_mmss(seconds):
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    start_formatted = seconds_to_mmss(start_time)
    end_formatted = seconds_to_mmss(end_time)
    duration = end_time - start_time
    duration_formatted = seconds_to_mmss(duration)
    
    return f"{start_formatted}-{end_formatted} (时长 {duration_formatted} | Duration {duration_formatted})"


def format_language_info(language_code, language_confidence):
    """
    格式化语言识别信息
    Format language identification information
    """
    language_name = format_language_name(language_code)
    confidence_level = format_confidence_level(language_confidence)
    
    info = f"🌍 **识别语言 | Identified Language**: {language_name}\n"
    info += f"📊 **置信度 | Confidence**: {language_confidence:.2f} ({confidence_level})\n"
    info += f"🔤 **语言代码 | Language Code**: {language_code}"
    
    return info


def format_speaker_info(transcribe_result, enable_speaker_diarization):
    """
    格式化发言者信息
    Format speaker information
    """
    if not enable_speaker_diarization:
        info = "👤 **发言者划分 | Speaker Diarization**\n"
        info += "❌ 发言者划分未启用\n"
        info += "💡 要启用此功能，请在高级设置中勾选'启用发言者划分'\n\n"
        info += "🌍 **语言信息 | Language Information**\n"
        info += f"📍 检测语言: {format_language_name(transcribe_result['language_code'])}\n"
        info += f"📊 置信度: {transcribe_result['language_confidence']:.2f} ({format_confidence_level(transcribe_result['language_confidence'])})"
        return info
    
    if not transcribe_result.get("segments"):
        info = "👤 **发言者划分 | Speaker Diarization**\n"
        info += "ℹ️ 发言者划分已启用，但未检测到多个发言者\n"
        info += "💡 这可能是因为：\n"
        info += "• 音频中只有一个发言者\n"
        info += "• 音频质量不够清晰\n"
        info += "• 发言者之间的声音特征相似\n\n"
        info += "🌍 **语言信息 | Language Information**\n"
        info += f"📍 检测语言: {format_language_name(transcribe_result['language_code'])}\n"
        info += f"📊 置信度: {transcribe_result['language_confidence']:.2f} ({format_confidence_level(transcribe_result['language_confidence'])})"
        return info
    
    # 有发言者信息的情况
    segments = transcribe_result["segments"]
    speakers = set(seg["speaker"] for seg in segments)
    
    # 统计信息 | Statistics
    total_duration = sum(seg["end_time"] - seg["start_time"] for seg in segments)
    speaker_stats = {}
    for seg in segments:
        speaker = seg["speaker"]
        duration = seg["end_time"] - seg["start_time"]
        if speaker not in speaker_stats:
            speaker_stats[speaker] = {"duration": 0, "segments": 0}
        speaker_stats[speaker]["duration"] += duration
        speaker_stats[speaker]["segments"] += 1
    
    # 构建输出
    info = f"👥 **发言者统计 | Speaker Statistics**\n"
    info += f"📊 识别到 {len(speakers)} 个发言者 | Identified {len(speakers)} speakers\n"
    info += f"⏱️ 总时长 | Total Duration: {total_duration:.1f}s\n"
    info += f"🌍 语言 | Language: {format_language_name(transcribe_result['language_code'])} ({transcribe_result['language_confidence']:.2f})\n\n"
    
    # 发言者统计 | Speaker statistics
    info += "📈 **发言者占比 | Speaker Distribution**\n"
    for speaker in sorted(speakers):
        speaker_name = format_speaker_name(speaker)
        duration = speaker_stats[speaker]["duration"]
        percentage = (duration / total_duration) * 100 if total_duration > 0 else 0
        segments_count = speaker_stats[speaker]["segments"]
        info += f"• {speaker_name}: {duration:.1f}s ({percentage:.1f}%) - {segments_count}段\n"
    
    info += "\n📝 **详细对话记录 | Detailed Conversation**\n"
    info += "─" * 50 + "\n"
    
    # 按时间顺序显示对话 | Display conversation in chronological order
    for i, segment in enumerate(segments, 1):
        speaker_name = format_speaker_name(segment["speaker"])
        time_info = format_time_duration(segment["start_time"], segment["end_time"])
        
        info += f"**{i:02d}. {speaker_name}**\n"
        info += f"🕐 {time_info}\n"
        info += f"💬 {segment['text']}\n\n"
    
    return info


def format_combined_output(transcribe_result, enable_speaker_diarization):
    """
    格式化组合输出，将语言信息和发言者信息整合
    Format combined output, integrating language and speaker information
    """
    language_info = format_language_info(
        transcribe_result['language_code'], 
        transcribe_result['language_confidence']
    )
    
    speaker_info = format_speaker_info(transcribe_result, enable_speaker_diarization)
    
    return language_info, speaker_info