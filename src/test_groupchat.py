#!/usr/bin/env python3
"""测试AutoGen GroupChat"""
import os
from dotenv import load_dotenv
load_dotenv()

from autogen import ConversableAgent, GroupChat, GroupChatManager

config = {
    'config_list': [{
        'model': os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        'api_key': os.getenv('OPENAI_API_KEY'),
    }],
    'temperature': 0.7,
    'timeout': 15  # 加timeout
}

print("创建Agents...")
agent1 = ConversableAgent(
    name="Agent1",
    system_message="You are helpful. Reply in 1 sentence.",
    llm_config=config,
    human_input_mode="NEVER"
)

agent2 = ConversableAgent(
    name="Agent2",
    system_message="You are friendly. Reply in 1 sentence.",
    llm_config=config,
    human_input_mode="NEVER"
)

print("创建GroupChat...")
groupchat = GroupChat(
    agents=[agent1, agent2],
    messages=[],
    max_round=2,
    speaker_selection_method="auto"
)

print("创建Manager...")
manager = GroupChatManager(
    groupchat=groupchat,
    llm_config=config
)

print("开始讨论...")
try:
    result = agent1.initiate_chat(
        manager,
        message="Say hi",
        max_turns=2
    )
    print(f"\n✓ 讨论完成，消息数: {len(groupchat.messages)}")
    for msg in groupchat.messages:
        print(f"  - {msg}")
except Exception as e:
    import traceback
    print(f"\n✗ 讨论失败:")
    traceback.print_exc()
