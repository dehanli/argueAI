#!/usr/bin/env python3
"""
Batch replace Chinese comments with English in the codebase
"""

import os
import re

# Define translation mappings
translations = {
    # Common comment patterns
    "获取": "Get",
    "创建": "Create",
    "初始化": "Initialize",
    "配置": "Configuration",
    "加载": "Load",
    "环境变量": "environment variables",
    "数据库": "database",
    "项目根目录": "project root directory",
    "挂载静态文件": "Mount static files",
    "模板配置": "Template configuration",
    "连接管理器": "connection manager",
    "讨论": "discussion",
    "消息": "message",
    "角色": "role",
    "音色": "voice",
    "生成": "generate",
    "选择": "select",
    "文本": "text",
    "音频": "audio",
    "成功": "success",
    "失败": "failed",
    "错误": "error",
    "开始": "Starting",
    "完成": "completed",
    "处理": "processing",

    # Specific docstrings
    "主页": "Home page",
    "创建新的讨论": "Create new discussion",
    "获取讨论列表": "Get discussion list",
    "获取单个讨论": "Get single discussion",
    "获取讨论的所有消息": "Get all messages for discussion",
    "初始化讨论，生成角色": "Initialize discussion and generate roles",
    "更新讨论模式": "Update discussion mode",
    "接收用户消息": "Receive user message",
    "执行下一轮对话": "Execute next turn",
    "获取可用的音色列表": "Get available voice list",
    "创建声音克隆": "Create voice clone",

    # Print messages
    "未找到": "not found",
    "跳过": "skipping",
    "语音合成": "TTS synthesis",
    "无法克隆音色": "cannot clone voice",
    "开始TTS合成": "Starting TTS synthesis",
    "大小": "size",
    "TTS生成成功": "TTS generated successfully",
    "TTS生成失败": "TTS generation failed",
    "TTS错误": "TTS error",
    "开始创建音色克隆": "Starting voice clone creation",
    "音色克隆成功": "Voice clone created successfully",
    "音色克隆错误": "Voice clone error",
    "生成用户消息TTS": "Generating user message TTS",
    "用户TTS生成完成": "User TTS generation completed",
    "用户TTS生成失败": "User TTS generation failed",
    "生成TTS": "Generating TTS",
    "TTS生成完成": "TTS generation completed",
    "TTS生成失败": "TTS generation failed",

    # Comment patterns
    "读取音频文件": "Read audio file",
    "检查文件大小": "Check file size",
    "限制10MB": "limit 10MB",
    "检查文件格式": "Check file format",
    "调用Fish Audio API创建声音克隆": "Call Fish Audio API to create voice clone",
    "为每个角色分配音色": "Assign voice to each role",
    "创建讨论系统": "Create discussion system",
    "保存到内存": "Save to memory",
    "更新讨论状态": "Update discussion status",
    "获取session": "Get session",
    "更新模式": "Update mode",
    "添加用户消息到讨论历史": "Add user message to discussion history",
    "保存到数据库": "Save to database",
    "生成用户消息的TTS（如果提供了voice_id）": "Generate TTS for user message (if voice_id provided)",
    "获取音色并生成TTS": "Get voice and generate TTS",
    "讨论结束": "Discussion ended",
    "在线程池中执行next_turn": "Execute next_turn in thread pool",
    "音色名称映射": "Voice name mapping",
    "用户选择的音色ID": "User selected voice ID",

    # Chinese keywords for voice selection
    "老板": "boss",
    "专家": "expert",
    "教授": "professor",
    "导师": "mentor",
    "领导": "leader",
    "学生": "student",
    "年轻": "young",
    "小": "junior",
    "新人": "new",
    "温和": "gentle",
    "柔": "soft",
    "细心": "careful",
    "耐心": "patient",
    "激情": "passionate",
    "强势": "strong",
    "果断": "decisive",
    "直率": "direct",

    # JavaScript comments
    "可用音色列表": "Available voices list",
    "用户选择的音色": "User selected voice",
    "用户克隆的音色列表": "User cloned voices list",
    "发送用户选择的音色": "Send user selected voice",
    "创建讨论": "Create discussion",
    "初始化讨论（生成角色）": "Initialize discussion (generate roles)",
    "秒延迟后自动播放下一轮": "seconds delay before auto-playing next turn",
    "功能": "functionality",
    "开始录音": "Start recording",
    "停止所有音轨": "Stop all tracks",
    "更新计时器": "Update timer",
    "停止录音": "Stop recording",

    # Mode descriptions
    "讨论模式：auto（智能选择）或 round_robin（轮流发言）": "Discussion mode: auto (intelligent selection) or round_robin (take turns)",
    "字": "characters",
}

def translate_file(filepath):
    """Translate Chinese comments in a file to English"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Apply translations
        for chinese, english in translations.items():
            content = content.replace(chinese, english)

        # Only write if content changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Translated: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error translating {filepath}: {e}")
        return False

def main():
    # Files to translate
    files_to_translate = [
        "src/main.py",
        "src/tts_handler.py",
        "src/agents.py",
        "src/role_generator.py",
        "static/js/script.js",
    ]

    base_dir = "/Users/lubenwei/Desktop/multi-ai"

    translated_count = 0
    for file_path in files_to_translate:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            if translate_file(full_path):
                translated_count += 1
        else:
            print(f"⚠️  File not found: {full_path}")

    print(f"\n✅ Translation complete! {translated_count} files updated.")

if __name__ == "__main__":
    main()
