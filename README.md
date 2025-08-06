# AI Chatbot with Smart Routing & RAG

A production-ready chatbot built with LangChain, LangGraph, and OpenAI that intelligently routes questions and provides context-aware answers.

## What it does

This chatbot automatically decides how to handle your questions:
- **FAQ questions** → Quick answers from built-in knowledge
- **Company research** → Searches through document database (RAG)  
- **General questions** → Uses OpenAI's GPT-4o-mini

The bot remembers your conversation, grades its own answers, and retries if needed. Everything is logged to LangSmith for monitoring.

## Features

- 🧠 **Smart routing** with confidence scoring
- 📚 **RAG system** with ChromaDB vector storage
- 💾 **Conversation memory** across sessions
- 🔄 **Self-evaluation** and answer improvement
- 🚀 **REST API** ready for deployment
- 📊 **LangSmith integration** for observability
- 🐳 **Docker support** for easy deployment

## Quick Start

1. **Install dependencies**
   ```bash
   uv sync
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your OPENAI_API_KEY
   ```

3. **Build knowledge base**
   ```bash
   uv run python chatbot/rag_input_documents/create_vector_storage.py
   ```

4. **Run the chatbot**
   ```bash
   # Command line interface
   uv run python chatbot/runner.py
   
   # Or start API server
   uv run uvicorn api_server:app --reload
   ```

## Deployment

Ready to deploy to Render.com with included Docker configuration. See `DEPLOY_RENDER.md` for detailed instructions.

## Project Structure

- `chatbot/` - Core chatbot logic and workflow
- `api_server.py` - FastAPI wrapper for REST API
- `rag_input_documents/` - Documents for knowledge base
- `rag_storage/` - Vector database files