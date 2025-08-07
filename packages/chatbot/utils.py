"""
Utility functions for the template chatbot

This module provides helper functions for environment setup, 
session management, and common operations.
"""

import os
import uuid
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def setup_environment() -> Dict[str, str]:
    """
    Set up environment variables and validate required keys
    
    Returns:
        Dictionary containing validated environment variables
    """
    load_dotenv()
    
    # Required environment variables
    required_vars = ["OPENAI_API_KEY"]
    env_vars = {}
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            raise ValueError(f"Required environment variable {var} not found")
        env_vars[var] = value
    
    # Optional environment variables
    optional_vars = {
        "LANGSMITH_API_KEY": None,
        "LANGCHAIN_PROJECT": "template-chatbot"
    }
    
    for var, default in optional_vars.items():
        env_vars[var] = os.getenv(var, default)
    
    # Configure LangSmith tracing if API key is available
    if env_vars["LANGSMITH_API_KEY"]:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = env_vars["LANGCHAIN_PROJECT"]
        logger.info("LangSmith tracing enabled")
    else:
        logger.info("LangSmith tracing disabled (no API key)")
    
    return env_vars

def generate_session_id() -> str:
    """Generate a unique session ID"""
    return str(uuid.uuid4())

def validate_session_id(session_id: str) -> bool:
    """Validate that a session ID is a valid UUID"""
    try:
        uuid.UUID(session_id)
        return True
    except ValueError:
        return False

def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent

def ensure_directories_exist():
    """Ensure required directories exist"""
    project_root = get_project_root()
    
    directories = [
        project_root / "rag_storage",
        project_root / "prompts",
        project_root / "faq"
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)
        logger.debug(f"Ensured directory exists: {directory}")

def format_conversation_history(messages) -> str:
    """
    Format conversation history for display
    
    Args:
        messages: List of BaseMessage objects
        
    Returns:
        Formatted string representation of the conversation
    """
    if not messages:
        return "No conversation history available."
    
    formatted = []
    for msg in messages:
        role = "Human" if hasattr(msg, 'type') and msg.type == "human" else "Assistant"
        content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
        formatted.append(f"{role}: {content}")
    
    return "\n".join(formatted)

def check_rag_storage_exists() -> bool:
    """Check if RAG storage directory exists and contains data"""
    storage_path = get_project_root() / "rag_storage"
    
    if not storage_path.exists():
        return False
    
    # Check if there are any files in the storage directory
    return any(storage_path.iterdir())

def check_faq_exists() -> bool:
    """Check if FAQ file exists"""
    faq_path = get_project_root() / "faq" / "faq.md"
    return faq_path.exists()

def get_system_status() -> Dict[str, Any]:
    """
    Get system status for debugging and monitoring
    
    Returns:
        Dictionary with system status information
    """
    try:
        env_vars = setup_environment()
        
        status = {
            "environment": {
                "openai_api_key_configured": bool(env_vars.get("OPENAI_API_KEY")),
                "langsmith_configured": bool(env_vars.get("LANGSMITH_API_KEY")),
                "langchain_project": env_vars.get("LANGCHAIN_PROJECT")
            },
            "storage": {
                "rag_storage_exists": check_rag_storage_exists(),
                "faq_exists": check_faq_exists()
            },
            "paths": {
                "project_root": str(get_project_root()),
                "rag_storage": str(get_project_root() / "rag_storage"),
                "faq_path": str(get_project_root() / "faq" / "faq.md")
            }
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return {"error": str(e)}

def print_system_status():
    """Print formatted system status"""
    status = get_system_status()
    
    if "error" in status:
        print(f"❌ System Status Error: {status['error']}")
        return
    
    print("🔧 System Status")
    print("=" * 50)
    
    # Environment
    print("📋 Environment:")
    env = status["environment"]
    print(f"  ✅ OpenAI API Key: {'Configured' if env['openai_api_key_configured'] else '❌ Missing'}")
    print(f"  {'✅' if env['langsmith_configured'] else '⚠️'} LangSmith: {'Configured' if env['langsmith_configured'] else 'Not configured (optional)'}")
    print(f"  📊 Project: {env['langchain_project']}")
    
    # Storage
    print("\n💾 Storage:")
    storage = status["storage"]
    print(f"  {'✅' if storage['rag_storage_exists'] else '⚠️'} RAG Storage: {'Available' if storage['rag_storage_exists'] else 'Not created (run create_vector_storage.py)'}")
    print(f"  {'✅' if storage['faq_exists'] else '⚠️'} FAQ: {'Available' if storage['faq_exists'] else 'Missing FAQ file'}")
    
    # Paths
    print("\n📁 Paths:")
    paths = status["paths"]
    print(f"  📂 Project Root: {paths['project_root']}")
    print(f"  🗃️ RAG Storage: {paths['rag_storage']}")
    print(f"  📄 FAQ File: {paths['faq_path']}")
    
    print("=" * 50)

class ChatbotLogger:
    """Enhanced logging for chatbot operations"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.logger = logging.getLogger(f"chatbot.{session_id}")
    
    def log_user_input(self, user_input: str):
        """Log user input"""
        self.logger.info(f"User input: {user_input[:100]}...")
    
    def log_route_decision(self, decision: str, question: str):
        """Log routing decision"""
        self.logger.info(f"Route decision: {decision} for question: {question[:50]}...")
    
    def log_answer_generated(self, source: str, answer_length: int):
        """Log answer generation"""
        self.logger.info(f"Answer generated from {source}: {answer_length} characters")
    
    def log_answer_graded(self, grade: str, attempts: int):
        """Log answer grading"""
        self.logger.info(f"Answer graded as {grade} (attempt {attempts})")
    
    def log_error(self, error: str, context: str = ""):
        """Log errors with context"""
        self.logger.error(f"Error in {context}: {error}")

def create_example_env_file():
    """Create an example .env file with required variables"""
    env_path = get_project_root().parent / ".env.example"
    
    env_content = """# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# LangSmith Tracing (Optional)
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=template-chatbot

# Tavily Search (Optional - for future web search capabilities)
TAVILY_API_KEY=your_tavily_api_key_here
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"📝 Example .env file created at: {env_path}")
    print("Please copy this to .env and fill in your actual API keys.")

if __name__ == "__main__":
    # Run system diagnostics
    print_system_status()
    print("\n" + "="*50)
    create_example_env_file()