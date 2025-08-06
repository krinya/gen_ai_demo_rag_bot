"""
FastAPI wrapper for the LangGraph chatbot - Render optimized
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
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
    message: str
    session_id: Optional[str] = None
    context: Optional[str] = ""

class ChatResponse(BaseModel):
    response: str
    session_id: str

class SessionResponse(BaseModel):
    session_id: str
    message: str

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

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the chatbot"""
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
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.post("/sessions", response_model=SessionResponse)
async def create_session():
    """Create a new chat session"""
    session_id = str(uuid.uuid4())
    # Pre-create chatbot instance
    await get_chatbot(session_id)
    
    return SessionResponse(
        session_id=session_id,
        message="New session created successfully"
    )

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session"""
    if session_id in chatbot_instances:
        del chatbot_instances[session_id]
        return {"message": f"Session {session_id} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.get("/sessions/{session_id}/history")
async def get_conversation_history(session_id: str):
    """Get conversation history for a session"""
    if session_id not in chatbot_instances:
        raise HTTPException(status_code=404, detail="Session not found")
    
    chatbot = chatbot_instances[session_id]
    history = chatbot.get_conversation_history()
    
    # Format history for API response
    formatted_history = []
    for msg in history:
        formatted_history.append({
            "type": "human" if "HumanMessage" in str(type(msg)) else "ai",
            "content": msg.content,
            "timestamp": getattr(msg, 'additional_kwargs', {}).get('timestamp', None)
        })
    
    return {"session_id": session_id, "history": formatted_history}

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
    """Root endpoint with API information"""
    return {
        "message": "LangGraph Chatbot API",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
