"""
Improved LangChain Chatbot Server - Clean version with all enhancements
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import uuid
import os
import logging
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from packages.chatbot.main import TemplateChatbot, create_chatbot
    logger.info("Successfully imported chatbot components")
except ImportError as e:
    logger.error(f"Failed to import chatbot: {e}")
    raise

# Create FastAPI app
app = FastAPI(
    title="LangChain Chatbot API - Improved",
    description="Advanced LangGraph chatbot with routing metadata",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Session storage
chatbot_sessions = {}
MAX_SESSIONS = 100

# === Pydantic Models ===

class ChatInput(BaseModel):
    message: str = Field(..., description="The user's message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")

class RoutingInfo(BaseModel):
    primary_route: str = Field(..., description="Initial routing decision")
    final_source: str = Field(..., description="Final source that provided the answer") 
    answer_quality: str = Field(..., description="Quality assessment")
    rephrase_attempts: int = Field(..., description="Number of rephrasing attempts")
    failed_sources: List[str] = Field(..., description="Sources that failed")
    question_evolution: Optional[Dict[str, str]] = Field(None, description="Question changes")

class EnhancedMetadata(BaseModel):
    message_count: int = Field(..., description="Total messages in conversation")
    routing_info: RoutingInfo = Field(..., description="Detailed routing information")
    session_active: bool = Field(..., description="Whether session is active")

class ChatOutput(BaseModel):
    response: str = Field(..., description="The AI's response")
    session_id: str = Field(..., description="Session ID")
    metadata: Optional[EnhancedMetadata] = Field(None, description="Enhanced response metadata")

# === Helper Functions ===

async def get_or_create_chatbot(session_id: str) -> TemplateChatbot:
    if len(chatbot_sessions) >= MAX_SESSIONS:
        oldest_session = next(iter(chatbot_sessions))
        del chatbot_sessions[oldest_session]
        logger.info(f"Cleaned up old session: {oldest_session}")
    
    if session_id not in chatbot_sessions:
        chatbot_sessions[session_id] = await create_chatbot(session_id=session_id)
        logger.info(f"Created new chatbot session: {session_id}")
    
    return chatbot_sessions[session_id]

# === Main Routes ===

@app.post("/chat", response_model=ChatOutput)
async def chat_endpoint(request: ChatInput):
    """
    Enhanced chat endpoint with real routing metadata
    
    **Routing Logic:**
    - FAQ: Simple factual questions (e.g., "Who is the CEO of Tesla?")
    - RAG: Specific data queries (e.g., "What was Apple's revenue in 2024?") 
    - LLM: General knowledge (e.g., "How does machine learning work?")
    """
    try:
        # Input validation
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if len(request.message) > 2000:
            raise HTTPException(status_code=400, detail="Message too long (max 2000 characters)")
        
        session_id = request.session_id or str(uuid.uuid4())
        chatbot = await get_or_create_chatbot(session_id)
        
        # Process message with metadata
        chat_result = await chatbot.chat_with_metadata(request.message.strip())
        response = chat_result["response"]
        routing_metadata = chat_result["routing_metadata"]
        
        history = chatbot.get_conversation_history()
        
        # Build structured metadata
        routing_info = RoutingInfo(
            primary_route=routing_metadata["primary_route"],
            final_source=routing_metadata["final_source"],
            answer_quality=routing_metadata["answer_quality"],
            rephrase_attempts=routing_metadata["rephrase_attempts"],
            failed_sources=routing_metadata["failed_sources"],
            question_evolution={
                "original": routing_metadata["original_question"],
                "final": routing_metadata["final_question"]
            } if routing_metadata["original_question"] != routing_metadata["final_question"] else None
        )
        
        metadata = EnhancedMetadata(
            message_count=len(history),
            routing_info=routing_info,
            session_active=True
        )
        
        return ChatOutput(
            response=response,
            session_id=session_id,
            metadata=metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")

@app.get("/test")
async def test_endpoint():
    """
    Testing guide with examples for different routing scenarios
    """
    return {
        "message": "🧪 Chatbot Testing Guide",
        "routing_tests": {
            "faq_routing": {
                "description": "Test FAQ routing with simple factual questions",
                "example_questions": [
                    "Who is the CEO of Tesla?",
                    "What is Tesla's main business?",
                    "Who founded Apple?"
                ],
                "curl_command": "curl -X POST 'http://localhost:0/chat' -H 'Content-Type: application/json' -d '{\"message\": \"Who is the CEO of Tesla?\"}'"
            },
            "rag_routing": {
                "description": "Test RAG routing with specific data queries",
                "example_questions": [
                    "What was Apple's revenue in 2024?",
                    "What was Tesla's net income last year?",
                    "Show me Intel's financial performance"
                ],
                "curl_command": "curl -X POST 'http://localhost:8000/chat' -H 'Content-Type: application/json' -d '{\"message\": \"What was Apple revenue in 2024?\"}'"
            },
            "llm_routing": {
                "description": "Test LLM routing with general knowledge questions",
                "example_questions": [
                    "How does machine learning work?",
                    "Explain quantum computing",
                    "What is the difference between AI and ML?"
                ],
                "curl_command": "curl -X POST 'http://localhost:8000/chat' -H 'Content-Type: application/json' -d '{\"message\": \"How does machine learning work?\"}'"
            }
        },
        "expected_metadata": {
            "primary_route": "The initial routing decision (faq/rag/llm)",
            "final_source": "Actual source that provided the answer",
            "answer_quality": "Quality assessment (good/bad)",
            "rephrase_attempts": "Number of question rephrasing attempts"
        }
    }

@app.get("/health")
async def health_check():
    """Health check with improvements indicator"""
    return {
        "status": "healthy",
        "service": "langchain-chatbot-improved",
        "version": "1.1.0", 
        "active_sessions": len(chatbot_sessions),
        "improvements": "✅ Enhanced routing metadata, input validation, testing guides"
    }

@app.get("/")
async def root():
    """Enhanced API overview"""
    return {
        "message": "🚀 LangChain Chatbot API v1.1 - Enhanced",
        "description": "Advanced chatbot with real-time routing metadata",
        
        "key_improvements": [
            "✅ Real routing metadata in responses",
            "✅ Input validation and error handling", 
            "✅ Structured response models",
            "✅ Testing guide with examples",
            "✅ Enhanced documentation"
        ],
        
        "endpoints": {
            "chat": "/chat - Main chat with routing metadata",
            "test": "/test - Testing guide with examples",
            "health": "/health - Health check with improvements",
            "docs": "/docs - Complete API documentation"
        },
        
        "quick_test": {
            "faq_test": "curl -X POST 'http://localhost:8000/chat' -H 'Content-Type: application/json' -d '{\"message\": \"Who is the CEO of Tesla?\"}'",
            "rag_test": "curl -X POST 'http://localhost:8000/chat' -H 'Content-Type: application/json' -d '{\"message\": \"What was Apple revenue in 2024?\"}'",
            "llm_test": "curl -X POST 'http://localhost:8000/chat' -H 'Content-Type: application/json' -d '{\"message\": \"Explain machine learning\"}'"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
