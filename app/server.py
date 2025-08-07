"""
LangChain Chatbot Server with Interactive Documentation
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
    from packages.chatbot.main import MainChatbot, create_chatbot
    logger.info("Successfully imported chatbot components")
except ImportError as e:
    logger.error(f"Failed to import chatbot: {e}")
    raise

# Create FastAPI app with enhanced documentation
app = FastAPI(
    title="🤖 Chatbot with inteligent routing (FAQ/ RAG / LLM) - Demo API",
    description=f"""
    AI Chatbot with Intelligent Routing
    
    This API provides a chatbot that automatically routes questions to the most appropriate source:
    
    - FAQ: Simple factual questions (CEO names, company info)
    - RAG: Specific data queries (financial data, detailed company information)  
    - LLM: General knowledge questions (explanations, how-to guides)
    
    Try it out directly in the docs below!
    
    Each endpoint includes ready-to-test examples. Just click "Try it out" and modify the examples.
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "API Support",
        "email": "menyhert.kristof@gmail.com",
    }
)

# Session storage
chatbot_sessions = {}
MAX_SESSIONS = 100

# === Enhanced Pydantic Models with Interactive Examples ===

class ChatInput(BaseModel):
    """Input model for chat requests with ready-to-test examples"""
    message: str = Field(
        ..., 
        description="Your message to the chatbot",
        example="Who is the CEO of Tesla?"
    )
    session_id: Optional[str] = Field(
        None, 
        description="Optional session ID for conversation continuity",
        example="my-chat-session-123"
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "message": "Who is the CEO of Tesla?",
                    "session_id": "test-session-1"
                },
                {
                    "message": "What was Apple's revenue in 2024?",
                    "session_id": "test-session-2"  
                },
                {
                    "message": "How does machine learning work?"
                }
            ]
        }

class RoutingInfo(BaseModel):
    """Detailed information about how the question was routed and processed"""
    primary_route: str = Field(
        ..., 
        description="Initial routing decision (faq/rag/llm)",
        example="faq"
    )
    final_source: str = Field(
        ..., 
        description="Final source that provided the answer",
        example="faq_handler"
    ) 
    answer_quality: str = Field(
        ..., 
        description="Quality assessment of the answer",
        example="good"
    )
    rephrase_attempts: int = Field(
        ..., 
        description="Number of question rephrasing attempts",
        example=0
    )
    failed_sources: List[str] = Field(
        ..., 
        description="Sources that failed before finding the answer",
        example=[]
    )
    question_evolution: Optional[Dict[str, str]] = Field(
        None, 
        description="How the question was modified during processing",
        example={"original": "Who runs Tesla?", "final": "Who is the CEO of Tesla?"}
    )

class EnhancedMetadata(BaseModel):
    """Comprehensive metadata about the chat session and response"""
    message_count: int = Field(
        ..., 
        description="Total messages in this conversation",
        example=1
    )
    routing_info: RoutingInfo = Field(
        ..., 
        description="Detailed routing and processing information"
    )
    session_active: bool = Field(
        ..., 
        description="Whether the session is currently active",
        example=True
    )

class ChatOutput(BaseModel):
    """Complete chat response with metadata"""
    response: str = Field(
        ..., 
        description="The AI chatbot's response to your message",
        example="Elon Musk is the CEO of Tesla."
    )
    session_id: str = Field(
        ..., 
        description="Session ID for this conversation",
        example="test-session-1"
    )
    metadata: Optional[EnhancedMetadata] = Field(
        None, 
        description="Detailed metadata about routing and processing"
    )

# === Helper Functions ===

async def get_or_create_chatbot(session_id: str) -> MainChatbot:
    if len(chatbot_sessions) >= MAX_SESSIONS:
        oldest_session = next(iter(chatbot_sessions))
        del chatbot_sessions[oldest_session]
        logger.info(f"Cleaned up old session: {oldest_session}")
    
    if session_id not in chatbot_sessions:
        chatbot_sessions[session_id] = await create_chatbot(session_id=session_id)
        logger.info(f"Created new chatbot session: {session_id}")
    
    return chatbot_sessions[session_id]

# === Main Chat Endpoint ===

@app.post("/chat", response_model=ChatOutput, tags=["💬 Chat"])
async def chat_endpoint(request: ChatInput):
    """
    ## 🚀 Main Chat Endpoint
    
    Send a message to the AI chatbot and get an intelligent response with routing metadata.
    
    ### 🎯 Routing Logic:
    - **FAQ**: Simple factual questions → `"Who is the CEO of Tesla?"`
    - **RAG**: Specific data queries → `"What was Apple's revenue in 2024?"`  
    - **LLM**: General knowledge → `"How does machine learning work?"`
    
    ### 📋 Try These Examples:
    
    **FAQ Example:**
    ```json
    {"message": "Who is the CEO of Tesla?"}
    ```
    
    **RAG Example:**
    ```json
    {"message": "What was Apple's revenue in 2024?"}
    ```
    
    **LLM Example:**
    ```json
    {"message": "Explain quantum computing"}
    ```
    
    ### 🔄 Session Continuity:
    Include a `session_id` to maintain conversation history across multiple requests.
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

# === Testing and Information Endpoints ===

@app.get("/examples", tags=["📚 Documentation"])
async def get_examples():
    """
    ## 📋 Ready-to-Test Examples
    
    Get example messages for each routing type. Copy these examples directly into the `/chat` endpoint above!
    """
    return {
        "message": "🧪 Copy these examples to test different routing types",
        "examples": {
            "faq_examples": {
                "description": "Simple factual questions → Routes to FAQ handler",
                "try_these": [
                    {"message": "Who is the CEO of Tesla?"},
                    {"message": "What is Tesla's main business?"},
                    {"message": "Who founded Apple?"},
                    {"message": "What does Google do?"}
                ]
            },
            "rag_examples": {
                "description": "Specific data queries → Routes to RAG system",
                "try_these": [
                    {"message": "What was Apple's revenue in 2024?"},
                    {"message": "Show me Tesla's financial performance"},
                    {"message": "What was Intel's net income last year?"},
                    {"message": "Tell me about Amazon's recent earnings"}
                ]
            },
            "llm_examples": {
                "description": "General knowledge → Routes to LLM",
                "try_these": [
                    {"message": "How does machine learning work?"},
                    {"message": "Explain quantum computing"},
                    {"message": "What is the difference between AI and ML?"},
                    {"message": "How do neural networks learn?"}
                ]
            }
        },
        "tips": {
            "session_continuity": "Add a session_id to maintain conversation history",
            "metadata": "Check the response metadata to see routing decisions",
            "testing": "Try borderline questions to see how routing adapts"
        }
    }

@app.get("/health", tags=["🔧 System"])
async def health_check():
    """## ❤️ Health Check
    
    Verify that the chatbot service is running properly."""
    return {
        "status": "healthy",
        "service": "langchain-chatbot-rag-demo",
        "version": "2.0.0", 
        "active_sessions": len(chatbot_sessions),
        "features": [
            "✅ Interactive documentation",
            "✅ Enhanced routing metadata", 
            "✅ Input validation",
            "✅ Ready-to-test examples"
        ]
    }

@app.get("/", tags=["📚 Documentation"])
async def root():
    """
    ## 🚀 Welcome to the LangChain Chatbot API
    
    ### Quick Start Guide:
    1. **Go to `/docs`** - Interactive API documentation
    2. **Try the `/chat` endpoint** - Send messages to the AI
    3. **Check `/examples`** - Get ready-to-test examples
    4. **Monitor with `/health`** - System status
    
    ### 🎯 How It Works:
    The chatbot intelligently routes your questions to the best source:
    - **FAQ** for simple facts
    - **RAG** for specific data 
    - **LLM** for explanations
    """
    return {
        "message": "🤖 LangChain Chatbot API v2.0",
        "description": "Intelligent AI chatbot with automatic routing",
        "interactive_docs": "/docs",
        "quick_start": {
            "step_1": "Visit /docs for interactive testing",
            "step_2": "Try the /chat endpoint with example messages",
            "step_3": "Check /examples for ready-to-test queries",
            "step_4": "Monitor system health at /health"
        },
        "routing_system": {
            "faq": "Simple factual questions (Who is the CEO of Tesla?)",
            "rag": "Specific data queries (What was Apple's revenue?)",
            "llm": "General knowledge (How does ML work?)"
        },
        "features": [
            "🔄 Automatic intelligent routing",
            "📊 Detailed response metadata",
            "💬 Session-based conversations", 
            "🚀 Interactive documentation",
            "✅ Input validation & error handling"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
