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

## 🌐 Live Demo

**Try the deployed API**: https://gen-ai-demo-rag-bot.onrender.com/

- **API Documentation**: https://gen-ai-demo-rag-bot.onrender.com/docs
- **Health Check**: https://gen-ai-demo-rag-bot.onrender.com/health

### Test the API
```bash
# Check if API is running
curl https://gen-ai-demo-rag-bot.onrender.com/health

# Get API overview and features
curl https://gen-ai-demo-rag-bot.onrender.com/

# Create a new chat session
curl -X POST https://gen-ai-demo-rag-bot.onrender.com/sessions

# Send a message (replace SESSION_ID with actual session ID)
curl -X POST https://gen-ai-demo-rag-bot.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Who is the CEO of Tesla?", "session_id": "YOUR_SESSION_ID"}'

# Get conversation history
curl https://gen-ai-demo-rag-bot.onrender.com/sessions/YOUR_SESSION_ID/history
```

### Interactive API Testing
Visit the **Swagger UI** for interactive testing: https://gen-ai-demo-rag-bot.onrender.com/docs

The interactive documentation allows you to:
- ✅ Test all endpoints directly in your browser
- ✅ See detailed request/response examples
- ✅ Try different question types and see routing in action
- ✅ View comprehensive API documentation

> **Note**: The chat functionality requires proper OpenAI API key configuration. The API infrastructure (sessions, health checks, documentation) is fully functional.

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

## 🚀 Deployment

### Live Production API
**Deployed on Render**: https://gen-ai-demo-rag-bot.onrender.com/

### Deploy Your Own
Ready to deploy to Render.com with included Docker configuration. 

**Quick Deploy**: 
1. Fork this repository
2. Connect to [Render.com](https://render.com)
3. Set your `OPENAI_API_KEY` environment variable
4. Deploy!

See detailed instructions in:
- `DEPLOY_RENDER.md` - Quick deployment guide
- `RENDER_DEPLOYMENT_TUTORIAL.md` - Comprehensive step-by-step tutorial

## 📡 API Endpoints

### Main Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and links |
| `/health` | GET | Health check for monitoring |
| `/docs` | GET | Interactive API documentation |
| `/chat` | POST | Send message to chatbot |
| `/sessions` | POST | Create new chat session |
| `/sessions/{id}/history` | GET | Get conversation history |
| `/sessions/{id}` | DELETE | Delete chat session |

### Example Usage
```python
import requests

# Create a session
session = requests.post("https://gen-ai-demo-rag-bot.onrender.com/sessions")
session_id = session.json()["session_id"]

# Chat with the bot
response = requests.post("https://gen-ai-demo-rag-bot.onrender.com/chat", 
    json={"message": "What can you tell me about Tesla?", "session_id": session_id})

print(response.json()["response"])
```

### Automated Testing
Run comprehensive API tests:
```bash
# Test the deployed API
uv run python test_api_comprehensive.py

# Test a different endpoint
uv run python test_api_comprehensive.py http://localhost:8000
```

The test script validates:
- ✅ Health and infrastructure endpoints
- ✅ Session management
- ✅ Chat functionality across different question types
- ✅ Conversation history tracking
- ✅ Error handling and response formats

## 📁 Project Structure

```
gen_ai_demo_rag_bot/
├── 📁 chatbot/                    # Core chatbot logic
│   ├── main.py                    # Main chatbot class
│   ├── create_graph.py            # LangGraph workflow
│   ├── runner.py                  # CLI interface
│   ├── utils.py                   # Utility functions
│   ├── 📁 prompts/                # Prompt templates
│   ├── 📁 faq/                    # FAQ knowledge base
│   ├── 📁 rag_input_documents/    # Source documents for RAG
│   └── 📁 rag_storage/            # Vector database files
├── 📁 template_basic/             # Template examples
│   ├── function_calling_routing_example.py
│   └── robust_routing_example.py
├── api_server.py                  # FastAPI REST API
├── main.py                        # Main entry point
├── Dockerfile                     # Docker configuration
├── render.yaml                    # Render deployment config
├── pyproject.toml                 # Dependencies & config
└── 📋 Documentation
    ├── README.md                  # This file
    ├── DEPLOY_RENDER.md           # Quick deploy guide
    └── RENDER_DEPLOYMENT_TUTORIAL.md  # Detailed tutorial
```