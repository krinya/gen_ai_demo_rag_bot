"""
Chatbot Package

Professional LangGraph-based chatbot with smart routing capabilities.

This package provides:
- MainChatbot: Main chatbot class with LangGraph workflow
- Smart routing between FAQ, RAG, and LLM sources
- Conversation memory and session management
- Self-evaluation and answer improvement
- LangSmith tracing integration

Usage:
    from packages.chatbot import MainChatbot, create_chatbot
    
    chatbot = MainChatbot(session_id="unique-session")
    response = await chatbot.chat("Your question here")
"""

from .main import MainChatbot, create_chatbot
from .utils import print_system_status, generate_session_id

__version__ = "2.0.0"
__all__ = [
    "MainChatbot", 
    "create_chatbot",
    "print_system_status",
    "generate_session_id"
]
