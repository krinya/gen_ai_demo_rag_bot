"""
FastAPI wrapper for the LangGraph chatbot - Render optimized
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
import os
import sys
from pathlib import Path
import asyncio
import logging

# Add chatbot directory to path for imports
sys.path.append(str(Path(__file__).parent / "chatbot"))

from chatbot.main import TemplateChatbot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LangGraph Chatbot API",
    description="Advanced chatbot with routing, RAG, and conversation memory",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str = Field(..., description="The message to send to the chatbot", example="Who is the CEO of Tesla?")
    session_id: Optional[str] = Field(None, description="Optional session ID to continue a conversation", example="550e8400-e29b-41d4-a716-446655440000")
    context: Optional[str] = Field("", description="Additional context for the conversation", example="We are discussing electric vehicles")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What can you tell me about Tesla's 2024 performance?",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "context": "Looking for detailed financial information"
            }
        }

class ChatResponse(BaseModel):
    response: str = Field(..., description="The chatbot's response", example="Tesla is led by CEO Elon Musk and is known for electric vehicles and sustainable energy solutions.")
    session_id: str = Field(..., description="The session ID for this conversation", example="550e8400-e29b-41d4-a716-446655440000")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "Tesla is an electric vehicle and clean energy company founded by Elon Musk. In 2024, Tesla continued to be a leader in the EV market with strong sales growth and expanding Supercharger networks.",
                "session_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }

class SessionResponse(BaseModel):
    session_id: str = Field(..., description="The unique session ID", example="550e8400-e29b-41d4-a716-446655440000")
    message: str = Field(..., description="Confirmation message", example="New session created successfully")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message", example="Error processing message: OpenAI API key not configured")
    session_id: Optional[str] = Field(None, description="Session ID if available")
    
class HistoryMessage(BaseModel):
    type: str = Field(..., description="Message type: 'human' or 'ai'", example="human")
    content: str = Field(..., description="Message content", example="Who is the CEO of Tesla?")
    timestamp: Optional[str] = Field(None, description="Message timestamp if available")

class HistoryResponse(BaseModel):
    session_id: str = Field(..., description="Session ID", example="550e8400-e29b-41d4-a716-446655440000")
    history: List[HistoryMessage] = Field(..., description="Conversation history")

# Store chatbot instances (in production, use Redis or similar)
# For Render, we'll use in-memory store with cleanup
chatbot_instances = {}
MAX_SESSIONS = 100  # Limit sessions to prevent memory issues

async def get_chatbot(session_id: str) -> TemplateChatbot:
    """Get or create chatbot instance for session with memory management"""
    if session_id not in chatbot_instances:
        # Clean up old sessions if we're at the limit
        if len(chatbot_instances) >= MAX_SESSIONS:
            # Remove oldest session (simple FIFO cleanup)
            oldest_session = next(iter(chatbot_instances))
            del chatbot_instances[oldest_session]
            logger.info(f"Cleaned up old session: {oldest_session}")
        
        chatbot_instances[session_id] = TemplateChatbot(session_id=session_id)
        logger.info(f"Created new chatbot session: {session_id}")
    
    return chatbot_instances[session_id]

@app.post("/chat", response_model=ChatResponse, responses={
    200: {"description": "Successful response", "model": ChatResponse},
    500: {"description": "Internal server error", "model": ErrorResponse}
})
async def chat(request: ChatRequest):
    """
    Send a message to the chatbot and get an AI response.
    
    The chatbot uses intelligent routing to determine the best knowledge source:
    - **FAQ**: For simple questions about company information
    - **RAG**: For detailed questions requiring document search
    - **LLM**: For general knowledge and creative tasks
    
    **Example usage:**
    ```bash
    curl -X POST "/chat" \\
         -H "Content-Type: application/json" \\
         -d '{"message": "Who is the CEO of Tesla?", "session_id": "your-session-id"}'
    ```
    """
    try:
        # Use provided session_id or create new one
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get chatbot instance
        chatbot = await get_chatbot(session_id)
        
        # Process message
        response = await chatbot.chat(request.message, request.context)
        
        return ChatResponse(
            response=response,
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        error_msg = "I apologize, but I encountered an error while processing your request. Please try again."
        
        # Check for specific error types
        if "openai" in str(e).lower() or "api" in str(e).lower():
            error_msg = "I'm currently unable to access my AI capabilities. Please check the API configuration or try again later."
        elif "rag" in str(e).lower() or "chroma" in str(e).lower():
            error_msg = "I'm having trouble accessing my knowledge base. The basic chat functionality should still work."
        
        return ChatResponse(
            response=error_msg,
            session_id=request.session_id or str(uuid.uuid4())
        )

@app.post("/sessions", response_model=SessionResponse)
async def create_session():
    """
    Create a new chat session.
    
    Each session maintains its own conversation history and context.
    Use the returned session_id in subsequent chat requests to maintain conversation continuity.
    
    **Example usage:**
    ```bash
    curl -X POST "/sessions"
    ```
    
    **Returns:** A new session ID that you can use for chat requests.
    """
    session_id = str(uuid.uuid4())
    # Pre-create chatbot instance
    await get_chatbot(session_id)
    
    return SessionResponse(
        session_id=session_id,
        message="New session created successfully"
    )

@app.delete("/sessions/{session_id}", responses={
    200: {"description": "Session deleted successfully"},
    404: {"description": "Session not found"}
})
async def delete_session(session_id: str):
    """
    Delete a chat session and free up memory.
    
    This will permanently remove the session and all its conversation history.
    
    **Example usage:**
    ```bash
    curl -X DELETE "/sessions/550e8400-e29b-41d4-a716-446655440000"
    ```
    """
    if session_id in chatbot_instances:
        del chatbot_instances[session_id]
        return {"message": f"Session {session_id} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.get("/sessions/{session_id}/history", response_model=HistoryResponse, responses={
    200: {"description": "Conversation history retrieved", "model": HistoryResponse},
    404: {"description": "Session not found"}
})
async def get_conversation_history(session_id: str):
    """
    Get the conversation history for a specific session.
    
    Returns all messages (both user and AI) in chronological order.
    
    **Example usage:**
    ```bash
    curl "/sessions/550e8400-e29b-41d4-a716-446655440000/history"
    ```
    """
    if session_id not in chatbot_instances:
        raise HTTPException(status_code=404, detail="Session not found")
    
    chatbot = chatbot_instances[session_id]
    history = chatbot.get_conversation_history()
    
    # Format history for API response
    formatted_history = []
    for msg in history:
        formatted_history.append(HistoryMessage(
            type="human" if "HumanMessage" in str(type(msg)) else "ai",
            content=msg.content,
            timestamp=getattr(msg, 'additional_kwargs', {}).get('timestamp', None)
        ))
    
    return HistoryResponse(
        session_id=session_id, 
        history=formatted_history
    )

@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {
        "status": "healthy", 
        "service": "langraph-chatbot-api",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production")
    }

@app.get("/")
async def root():
    """
    Root endpoint with API information and quick links.
    
    Provides an overview of the chatbot API capabilities and available endpoints.
    """
    return {
        "message": "🤖 LangGraph Chatbot API",
        "description": "Advanced AI chatbot with smart routing, RAG capabilities, and conversation memory",
        "version": "1.0.0",
        "features": [
            "Smart question routing (FAQ/RAG/LLM)",
            "ChromaDB vector search",
            "Conversation memory",
            "Self-evaluation and improvement",
            "LangSmith tracing"
        ],
        "endpoints": {
            "chat": "/chat - Send messages to the chatbot",
            "sessions": "/sessions - Manage chat sessions",
            "docs": "/docs - Interactive API documentation",
            "health": "/health - Service health check"
        },
        "quick_start": {
            "1": "POST /sessions - Create a new session",
            "2": "POST /chat with your session_id - Start chatting",
            "3": "GET /sessions/{id}/history - View conversation"
        },
        "example_questions": [
            "Who is the CEO of Tesla?",
            "What are Tesla's 2024 financial highlights?",
            "How does machine learning work?",
            "What can you help me with?"
        ]
    }

# Add a demo endpoint for testing different question types
@app.post("/demo")
async def demo_questions():
    """
    Demo endpoint that tests the chatbot with example questions.
    
    This endpoint demonstrates the different routing capabilities:
    - FAQ questions for quick facts
    - RAG questions for document-based answers  
    - General LLM questions for creative responses
    """
    demo_questions = [
        {"type": "FAQ", "question": "Who is the CEO of Tesla?"},
        {"type": "RAG", "question": "What are Tesla's key financial metrics for 2024?"},
        {"type": "LLM", "question": "Explain how electric vehicles work"}
    ]
    
    results = []
    session_id = str(uuid.uuid4())
    chatbot = await get_chatbot(session_id)
    
    for demo in demo_questions:
        try:
            response = await chatbot.chat(demo["question"])
            results.append({
                "question_type": demo["type"],
                "question": demo["question"],
                "response": response[:200] + "..." if len(response) > 200 else response,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "question_type": demo["type"],
                "question": demo["question"],
                "response": f"Error: {str(e)}",
                "status": "error"
            })
    
    return {
        "session_id": session_id,
        "demo_results": results,
        "note": "These examples show how the chatbot routes different types of questions to appropriate knowledge sources."
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
