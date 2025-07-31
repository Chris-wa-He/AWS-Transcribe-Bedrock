"""
发言者文本提取模块，专门处理AWS Transcribe发言者划分结果的文本提取
Speaker text extraction module, specifically handles text extraction from AWS Transcribe speaker diarization results
"""

import logging

logger = logging.getLogger(__name__)

def extract_speaker_text_method1(segment, items):
    """
    方法1：基于时间戳匹配提取发言者文本
    Method 1: Extract speaker text based on timestamp matching
    """
    speaker_label = segment.get("speaker_label", "Unknown")
    start_time = float(segment.get("start_time", "0"))
    end_time = float(segment.get("end_time", "0"))
    
    segment_words = []
    
    # 遍历所有词汇项目，找到属于当前时间段的词汇
    for item in items:
        if item.get("type") == "pronunciation":
            item_start = float(item.get("start_time", "0"))
            item_end = float(item.get("end_time", "0"))
            
            # 检查词汇是否在当前发言者的时间段内（允许一定的时间重叠）
            if (item_start >= start_time - 0.1 and item_end <= end_time + 0.1) or \
               (item_start < end_time and item_end > start_time):  # 重叠检查
                word_content = item.get("alternatives", [{}])[0].get("content", "")
                if word_content:
                    segment_words.append(word_content)
        elif item.get("type") == "punctuation":
            item_start = float(item.get("start_time", start_time))
            # 标点符号通常没有end_time，使用start_time
            if start_time - 0.1 <= item_start <= end_time + 0.1:
                punct_content = item.get("alternatives", [{}])[0].get("content", "")
                if punct_content and segment_words:
                    # 将标点符号附加到最后一个词
                    segment_words[-1] += punct_content
    
    return " ".join(segment_words).strip()

def extract_speaker_text_method2(segment, full_transcript, total_duration):
    """
    方法2：基于时间比例从完整转录文本中提取
    Method 2: Extract based on time ratio from full transcript
    """
    start_time = float(segment.get("start_time", "0"))
    end_time = float(segment.get("end_time", "0"))
    
    if total_duration <= 0:
        return ""
    
    start_ratio = start_time / total_duration
    end_ratio = end_time / total_duration
    
    start_char = int(len(full_transcript) * start_ratio)
    end_char = int(len(full_transcript) * end_ratio)
    
    # 确保索引在有效范围内
    start_char = max(0, min(start_char, len(full_transcript)))
    end_char = max(start_char, min(end_char, len(full_transcript)))
    
    extracted_text = full_transcript[start_char:end_char].strip()
    
    # 尝试在单词边界处截断，避免截断单词
    if extracted_text and start_char > 0:
        # 向前查找单词边界
        while start_char > 0 and full_transcript[start_char-1] not in [' ', '\n', '\t']:
            start_char -= 1
    
    if extracted_text and end_char < len(full_transcript):
        # 向后查找单词边界
        while end_char < len(full_transcript) and full_transcript[end_char] not in [' ', '\n', '\t', '.', ',', '!', '?']:
            end_char += 1
    
    return full_transcript[start_char:end_char].strip()

def extract_speaker_text_method3(segment, speaker_labels_data):
    """
    方法3：直接从speaker_labels数据结构中提取
    Method 3: Extract directly from speaker_labels data structure
    """
    # 有些AWS Transcribe版本可能在segment中直接包含文本
    if "text" in segment:
        return segment["text"]
    
    # 或者在items中包含文本
    if "items" in segment:
        segment_words = []
        for item in segment["items"]:
            if item.get("type") == "pronunciation":
                word_content = item.get("alternatives", [{}])[0].get("content", "")
                if word_content:
                    segment_words.append(word_content)
            elif item.get("type") == "punctuation":
                punct_content = item.get("alternatives", [{}])[0].get("content", "")
                if punct_content and segment_words:
                    segment_words[-1] += punct_content
        return " ".join(segment_words).strip()
    
    return ""

def extract_speaker_segments(transcript_data, enable_speaker_diarization):
    """
    综合提取发言者片段文本的主函数
    Main function to comprehensively extract speaker segment text
    """
    if not enable_speaker_diarization or "speaker_labels" not in transcript_data["results"]:
        return None
    
    speaker_labels = transcript_data["results"]["speaker_labels"]
    segments = speaker_labels.get("segments", [])
    
    if not segments:
        logger.warning("发言者划分已启用但未找到segments数据 | Speaker diarization enabled but no segments data found")
        return None
    
    # 获取完整转录文本和总时长
    full_transcript = transcript_data["results"]["transcripts"][0]["transcript"]
    items = transcript_data["results"].get("items", [])
    
    # 尝试获取总时长
    total_duration = 0
    if items:
        # 从最后一个有时间戳的项目获取总时长
        for item in reversed(items):
            if "end_time" in item:
                total_duration = float(item["end_time"])
                break
    
    speaker_segments = []
    
    for i, segment in enumerate(segments):
        speaker_label = segment.get("speaker_label", f"Unknown_{i}")
        start_time = float(segment.get("start_time", "0"))
        end_time = float(segment.get("end_time", "0"))
        
        # 尝试多种方法提取文本
        segment_text = ""
        
        # 方法1：基于时间戳匹配
        try:
            segment_text = extract_speaker_text_method1(segment, items)
            if segment_text:
                logger.debug(f"方法1成功提取片段 {i+1} 文本: '{segment_text[:30]}...' | Method 1 successfully extracted segment {i+1} text: '{segment_text[:30]}...'")
        except Exception as e:
            logger.debug(f"方法1提取失败: {str(e)} | Method 1 extraction failed: {str(e)}")
        
        # 方法2：如果方法1失败，尝试基于时间比例
        if not segment_text and total_duration > 0:
            try:
                segment_text = extract_speaker_text_method2(segment, full_transcript, total_duration)
                if segment_text:
                    logger.debug(f"方法2成功提取片段 {i+1} 文本: '{segment_text[:30]}...' | Method 2 successfully extracted segment {i+1} text: '{segment_text[:30]}...'")
            except Exception as e:
                logger.debug(f"方法2提取失败: {str(e)} | Method 2 extraction failed: {str(e)}")
        
        # 方法3：如果前两种方法都失败，尝试直接从segment数据中提取
        if not segment_text:
            try:
                segment_text = extract_speaker_text_method3(segment, speaker_labels)
                if segment_text:
                    logger.debug(f"方法3成功提取片段 {i+1} 文本: '{segment_text[:30]}...' | Method 3 successfully extracted segment {i+1} text: '{segment_text[:30]}...'")
            except Exception as e:
                logger.debug(f"方法3提取失败: {str(e)} | Method 3 extraction failed: {str(e)}")
        
        # 如果所有方法都失败，使用占位符
        if not segment_text:
            segment_text = f"[片段 {i+1}: 无法提取文本内容]"
            logger.warning(f"所有方法都无法提取片段 {i+1} 的文本 | All methods failed to extract text for segment {i+1}")
        
        speaker_segments.append({
            "speaker": speaker_label,
            "start_time": start_time,
            "end_time": end_time,
            "text": segment_text
        })
    
    logger.info(f"成功提取 {len(speaker_segments)} 个发言者片段 | Successfully extracted {len(speaker_segments)} speaker segments")
    
    # 记录提取结果的统计信息
    non_empty_segments = [seg for seg in speaker_segments if seg["text"] and not seg["text"].startswith("[片段")]
    logger.info(f"其中 {len(non_empty_segments)} 个片段包含有效文本 | {len(non_empty_segments)} segments contain valid text")
    
    return speaker_segments