# AI Chatbot with Smart Routing & RAG

An example of a chatbot that intelligently routes questions. It decides whether to use FAQ knowledge, search documents via RAG, or call GPT-4o-mini based on your question.

## Features

- **Smart routing** - Automatically chooses the best response method
- **RAG system** - ChromaDB vector storage for document search
- **Memory** - Remembers conversation history across sessions
- **Self-evaluation** - Grades and improves its own answers
- **REST API** - Ready for deployment with FastAPI
- **Monitoring** - LangSmith integration for observability

## 🌐 Live Demo

**API**: https://gen-ai-demo-rag-bot.onrender.com/
- **Documentation**: https://gen-ai-demo-rag-bot.onrender.com/docs  

### Quick API Test
```bash
# Check status
curl https://gen-ai-demo-rag-bot.onrender.com/health

# Create session and chat
curl -X POST https://gen-ai-demo-rag-bot.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Who is the CEO of Tesla?", "session_id": "YOUR_SESSION_ID"}'
```

Visit the [interactive docs](https://gen-ai-demo-rag-bot.onrender.com/docs) to test all endpoints directly in your browser.

## Quick Start

### Local Development with UV

1. **Install dependencies**
   ```bash
   uv sync
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Add your OPENAI_API_KEY to .env
   ```

3. **Build knowledge base**
   ```bash
   uv run python packages/chatbot/rag_input_documents/create_vector_storage.py
   ```

4. **Run locally**
   ```bash
   # Command line chatbot
   uv run python packages/chatbot/runner.py
   
   # API server
   uv run uvicorn app.server:app --reload
   ```

## 🚀 Deployment

**Live on**: https://gen-ai-demo-rag-bot.onrender.com/

Ready to deploy to Render with Docker. Fork this repo, connect to Render, add your `OPENAI_API_KEY`, and deploy.

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API overview |
| `/health` | GET | Health check |
| `/docs` | GET | Interactive documentation |
| `/chat` | POST | Send message |

## 📁 Project Structure

```
gen_ai_demo_rag_bot/
├── app/
│   ├── __init__.py
│   └── server.py                  # FastAPI REST API
├── packages/
│   └── chatbot/                   # Core chatbot logic
│       ├── main.py                # Main chatbot class
│       ├── create_graph.py        # LangGraph workflow
│       ├── runner.py              # CLI interface (run with uv)
│       ├── utils.py               # Utility functions
│       ├── prompts/               # Prompt templates
│       ├── faq/                   # FAQ knowledge base
│       ├── rag_input_documents/   # Source documents for RAG
│       └── rag_storage/           # Vector database files
├── main.py                        # Main entry point
├── Dockerfile                     # Docker configuration
├── pyproject.toml                 # UV dependencies & config
└── README.md                      # This file
```

## Example Usage

```python
import requests

# Create your session uuid from your app
session_id = "your session uuid"

response = requests.post(
   "https://gen-ai-demo-rag-bot.onrender.com/chat",
   json={"message": "What can you tell me about Tesla?",
   "session_id": session_id}
)

print(response.json()["response"])
```