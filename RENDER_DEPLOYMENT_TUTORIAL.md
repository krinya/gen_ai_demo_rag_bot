# Complete Render Deployment Tutorial for LangGraph Chatbot API

This tutorial will guide you through deploying your LangGraph chatbot API to Render, a modern cloud platform that makes deployment simple and fast.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Pre-Deployment Preparation](#pre-deployment-preparation)
3. [Method 1: One-Click Deploy (Recommended)](#method-1-one-click-deploy-recommended)
4. [Method 2: Using Render Blueprint](#method-2-using-render-blueprint)
5. [Method 3: Manual Deployment](#method-3-manual-deployment)
6. [Post-Deployment Setup](#post-deployment-setup)
7. [Testing Your Deployed API](#testing-your-deployed-api)
8. [Monitoring and Maintenance](#monitoring-and-maintenance)
9. [Troubleshooting](#troubleshooting)
10. [Production Optimizations](#production-optimizations)

## Prerequisites

Before starting, make sure you have:

### Required Accounts
- [ ] **GitHub Account**: Your code needs to be in a GitHub repository
- [ ] **Render Account**: Sign up at [render.com](https://render.com) (free tier available)
- [ ] **OpenAI Account**: With API access and credits

### Required API Keys
- [ ] **OpenAI API Key**: Get from [platform.openai.com](https://platform.openai.com)
- [ ] **LangSmith API Key**: (Optional) Get from [smith.langchain.com](https://smith.langchain.com)

### Local Development Environment
- [ ] **Python 3.12+**: Your project requires Python 3.12 or higher
- [ ] **UV Package Manager**: Already configured in your project
- [ ] **Git**: For version control

## Pre-Deployment Preparation

### Step 1: Verify Your Project Structure
Your project should have this structure (which you already have):
```
gen_ai_demo_rag_bot/
├── api_server.py          # FastAPI application
├── Dockerfile            # Docker configuration
├── render.yaml           # Render blueprint
├── pyproject.toml        # Python dependencies
├── uv.lock              # Lock file for dependencies
├── chatbot/             # Your chatbot module
│   ├── main.py
│   └── ...
└── template_basic/      # Template directory
```

### Step 2: Test Locally First
Before deploying, test your API locally:

```bash
# Navigate to your project directory
cd /Users/krinya/gen_ai_demo_rag_bot

# Create a .env file with your API keys
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
echo "LANGSMITH_API_KEY=your_langsmith_api_key_here" >> .env

# Run the API server
uv run uvicorn api_server:app --reload

# Test the health endpoint (in another terminal)
curl http://localhost:8000/health

# Test the chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

### Step 3: Push to GitHub
If you haven't already, push your code to GitHub:

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit your changes
git commit -m "Initial commit: LangGraph chatbot API ready for deployment"

# Add your GitHub remote (replace with your repository URL)
git remote add origin https://github.com/your-username/gen_ai_demo_rag_bot.git

# Push to GitHub
git push -u origin main
```

## Method 1: One-Click Deploy (Recommended)

This is the fastest and most straightforward method.

### Step 1: Sign Up for Render
1. Go to [render.com](https://render.com)
2. Click **"Get Started"**
3. Sign up using your GitHub account (recommended for easy integration)

### Step 2: Connect GitHub Repository
1. In your Render Dashboard, click **"New +"**
2. Select **"Web Service"**
3. Choose **"Connect a repository"**
4. Select your GitHub account
5. Find and select your `gen_ai_demo_rag_bot` repository
6. Click **"Connect"**

### Step 3: Configure Deployment Settings
Render will auto-detect your Dockerfile. Configure these settings:

**Basic Settings:**
- **Name**: `langraph-chatbot-api` (or your preferred name)
- **Region**: Choose closest to your users (e.g., Oregon, N. Virginia)
- **Branch**: `main`
- **Runtime**: `Docker` (should be auto-detected)

**Build & Deploy:**
- **Build Command**: Leave empty (Dockerfile handles this)
- **Start Command**: Leave empty (Dockerfile handles this)

**Advanced Settings:**
- **Health Check Path**: `/health`
- **Auto-Deploy**: `Yes` (deploy automatically on git push)

### Step 4: Set Environment Variables
In the Environment Variables section, add:

| Key | Value | Notes |
|-----|--------|-------|
| `OPENAI_API_KEY` | `your_actual_openai_api_key` | Required - Get from OpenAI |
| `LANGSMITH_API_KEY` | `your_langsmith_api_key` | Optional - For tracing |
| `LANGCHAIN_TRACING_V2` | `true` | Optional - Enable tracing |
| `LANGCHAIN_PROJECT` | `langraph-chatbot-api` | Optional - Project name |
| `ENVIRONMENT` | `production` | Optional - Environment flag |

⚠️ **Important**: Never commit API keys to your repository. Always set them as environment variables in Render.

### Step 5: Deploy
1. Click **"Create Web Service"**
2. Render will start building your application
3. Wait for the build and deployment to complete (usually 3-5 minutes)

## Method 2: Using Render Blueprint

This method uses the `render.yaml` file for automated configuration.

### Step 1: Access Render Blueprint
1. In your Render Dashboard, click **"New +"**
2. Select **"Blueprint"**
3. Choose **"Connect a repository"**
4. Select your repository

### Step 2: Configure Blueprint
1. Render will detect your `render.yaml` file
2. Review the configuration:
   ```yaml
   services:
     - type: web
       name: langraph-chatbot-api
       runtime: docker
       plan: starter
       region: oregon
   ```

### Step 3: Set Environment Variables
Since the blueprint has `sync: false` for sensitive variables, you'll need to set them manually:
1. After deployment starts, go to your service
2. Click **"Environment"** tab
3. Add the required environment variables as listed in Method 1

### Step 4: Deploy
1. Click **"Apply"** to deploy using the blueprint
2. Monitor the deployment progress

## Method 3: Manual Deployment

For complete control over the deployment process.

### Step 1: Create Web Service
1. Go to Render Dashboard
2. Click **"New +"** → **"Web Service"**
3. Choose **"Connect a repository"**

### Step 2: Manual Configuration
Set these values manually:

**Repository:**
- Select your GitHub repository
- Branch: `main`

**Settings:**
- Name: `langraph-chatbot-api`
- Runtime: `Docker`
- Region: Your preferred region
- Plan: `Starter` (free tier)

**Build Settings:**
- Build Command: (leave empty)
- Start Command: `uv run uvicorn api_server:app --host 0.0.0.0 --port $PORT`

**Advanced Settings:**
- Health Check Path: `/health`
- Auto-Deploy: `Yes`

### Step 3: Environment Variables
Add all required environment variables as shown in Method 1.

### Step 4: Deploy
Click **"Create Web Service"** to start deployment.

## Post-Deployment Setup

### Step 1: Verify Deployment
Once deployment is complete, you'll see:
- ✅ **Build Successful**
- ✅ **Deploy Successful** 
- Your service URL (e.g., `https://langraph-chatbot-api.onrender.com`)

### Step 2: Check Service Health
1. Click on your service URL
2. You should see:
   ```json
   {
     "message": "LangGraph Chatbot API",
     "docs": "/docs",
     "health": "/health",
     "version": "1.0.0"
   }
   ```

### Step 3: Test API Endpoints
Test key endpoints:

**Health Check:**
```bash
curl https://your-service-name.onrender.com/health
```

**Chat Endpoint:**
```bash
curl -X POST https://your-service-name.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

**API Documentation:**
Visit: `https://your-service-name.onrender.com/docs`

## Testing Your Deployed API

### Interactive API Testing
1. Go to `https://your-service-name.onrender.com/docs`
2. Use the interactive Swagger UI to test endpoints
3. Try these endpoints:
   - `POST /chat` - Send a message to the chatbot
   - `POST /sessions` - Create a new session
   - `GET /sessions/{session_id}/history` - Get conversation history

### Command Line Testing
```bash
# Store your service URL
SERVICE_URL="https://your-service-name.onrender.com"

# Test health
curl $SERVICE_URL/health

# Create a new session
SESSION_RESPONSE=$(curl -X POST $SERVICE_URL/sessions)
echo $SESSION_RESPONSE

# Extract session ID (you'll need to parse JSON)
SESSION_ID="your_extracted_session_id"

# Send a chat message
curl -X POST $SERVICE_URL/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What can you help me with?", "session_id": "'$SESSION_ID'"}'

# Get conversation history
curl $SERVICE_URL/sessions/$SESSION_ID/history
```

### Python Testing Script
Create a test script:

```python
import requests
import json

# Your deployed service URL
BASE_URL = "https://your-service-name.onrender.com"

# Create a new session
response = requests.post(f"{BASE_URL}/sessions")
session_id = response.json()["session_id"]
print(f"Created session: {session_id}")

# Send a message
chat_response = requests.post(f"{BASE_URL}/chat", json={
    "message": "Hello! Can you tell me about Tesla?",
    "session_id": session_id
})
print(f"Bot response: {chat_response.json()['response']}")

# Get conversation history
history = requests.get(f"{BASE_URL}/sessions/{session_id}/history")
print(f"Conversation history: {json.dumps(history.json(), indent=2)}")
```

## Monitoring and Maintenance

### Render Dashboard Monitoring
Monitor your application through the Render dashboard:

1. **Metrics Tab**: View CPU, memory, and network usage
2. **Logs Tab**: View application logs and errors
3. **Events Tab**: See deployment history and events

### Setting Up Alerts
1. Go to your service settings
2. Configure notification preferences
3. Set up alerts for:
   - Service failures
   - High resource usage
   - Deployment failures

### Log Monitoring
Your application logs are available in the Render dashboard:
- Access via **Logs** tab in your service
- Monitor for errors and performance issues
- Use logs for debugging deployed application

### Health Check Monitoring
Render automatically monitors your `/health` endpoint:
- Service is restarted if health checks fail
- Configure health check frequency in service settings

## Troubleshooting

### Common Issues and Solutions

#### 1. Build Failures
**Problem**: Docker build fails
**Solutions**:
- Check Dockerfile syntax
- Verify all files are committed to GitHub
- Check build logs in Render dashboard

#### 2. Environment Variable Issues
**Problem**: API keys not working
**Solutions**:
- Verify environment variables are set in Render dashboard
- Check variable names match your code
- Ensure no extra spaces in values

#### 3. Service Won't Start
**Problem**: Service fails to start
**Solutions**:
- Check start command is correct
- Verify port binding (`--port $PORT`)
- Review application logs for startup errors

#### 4. Health Check Failures
**Problem**: Health check endpoint failing
**Solutions**:
- Test `/health` endpoint locally
- Verify health check path in service settings
- Check if service is binding to correct port

#### 5. Memory Issues
**Problem**: Service running out of memory
**Solutions**:
- Monitor memory usage in dashboard
- Implement session cleanup in your code
- Consider upgrading to paid plan

#### 6. Cold Start Delays
**Problem**: First request takes long time
**Solutions**:
- This is expected on free tier (service sleeps after 15 min)
- Consider upgrading to paid plan for always-on service
- Implement warming strategies if needed

### Getting Help
- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **Render Community**: [community.render.com](https://community.render.com)
- **Support**: Available through Render dashboard

## Production Optimizations

### Free Tier Limitations
Your current setup uses Render's free tier with these limitations:
- **Sleep after inactivity**: Service sleeps after 15 minutes
- **750 hours/month**: Limited uptime
- **Cold starts**: ~30 seconds for first request after sleep
- **Memory limit**: 512 MB RAM

### Upgrading to Paid Plans

#### Starter Plan ($7/month):
- Always-on service (no sleeping)
- Faster cold starts
- 1 GB RAM
- Better for production use

#### Professional Plan ($25/month):
- 4 GB RAM
- Better performance
- Priority support

### Performance Optimizations

#### 1. Optimize Memory Usage
Add to your `api_server.py`:
```python
# Implement session cleanup
import gc
from datetime import datetime, timedelta

async def cleanup_old_sessions():
    """Clean up sessions older than 1 hour"""
    cutoff = datetime.now() - timedelta(hours=1)
    old_sessions = [
        session_id for session_id, chatbot in chatbot_instances.items()
        if hasattr(chatbot, 'created_at') and chatbot.created_at < cutoff
    ]
    
    for session_id in old_sessions:
        del chatbot_instances[session_id]
    
    if old_sessions:
        gc.collect()  # Force garbage collection
        logger.info(f"Cleaned up {len(old_sessions)} old sessions")
```

#### 2. Add Persistent Storage
For production, consider adding Redis for session storage:
```python
# Add to requirements
# redis>=4.0.0

# In api_server.py
import redis
import json

# Redis setup
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

async def get_chatbot_with_redis(session_id: str):
    """Get chatbot with Redis backing"""
    # Try to load from Redis
    session_data = redis_client.get(f"session:{session_id}")
    if session_data:
        # Restore chatbot state from Redis
        pass
    else:
        # Create new chatbot
        chatbot = TemplateChatbot(session_id=session_id)
        # Save to Redis
        redis_client.setex(f"session:{session_id}", 3600, json.dumps(chatbot.serialize()))
    
    return chatbot
```

#### 3. Add Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_response(message_hash: str):
    """Cache frequent responses"""
    pass
```

### Security Enhancements

#### 1. Add Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/chat")
@limiter.limit("10/minute")  # 10 requests per minute
async def chat(request: ChatRequest):
    # Your existing chat logic
    pass
```

#### 2. Add Input Validation
```python
from pydantic import validator

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[str] = ""
    
    @validator('message')
    def message_length(cls, v):
        if len(v) > 1000:
            raise ValueError('Message too long')
        return v
```

### Custom Domain Setup
If you upgrade to a paid plan:
1. Go to your service settings
2. Add custom domain
3. Configure DNS records
4. Enable SSL certificate

### Scaling Considerations
For high-traffic applications:
- Use multiple service instances
- Implement load balancing
- Use external databases (PostgreSQL, MongoDB)
- Consider microservices architecture

## Conclusion

You now have a comprehensive guide to deploy your LangGraph chatbot API to Render. The platform provides:

- **Easy deployment** with Docker support
- **Automatic HTTPS** and SSL certificates
- **Built-in monitoring** and logging
- **Flexible scaling** options
- **Free tier** to get started

Your API will be accessible at `https://your-service-name.onrender.com` with full documentation at the `/docs` endpoint.

Remember to:
- Monitor your usage and costs
- Keep your dependencies updated
- Implement proper error handling
- Consider upgrading to paid plans for production use

Good luck with your deployment! 🚀
