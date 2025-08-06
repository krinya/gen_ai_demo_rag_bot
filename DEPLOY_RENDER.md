# Deploy to Render Guide

## Quick Deploy to Render

### Option 1: One-Click Deploy (Recommended)
1. Fork this repository to your GitHub
2. Connect your GitHub to Render at [render.com](https://render.com)
3. Click "New Web Service" 
4. Select this repository
5. Render will auto-detect the Dockerfile
6. Set environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `LANGSMITH_API_KEY`: (Optional) Your LangSmith API key
7. Deploy!

### Option 2: Using Render Blueprint
1. Push this code to GitHub
2. In Render dashboard, go to "Blueprint"
3. Connect repository and select `render.yaml`
4. Set environment variables in Render dashboard
5. Deploy

### Option 3: Manual Setup
1. Create new Web Service in Render
2. Connect your GitHub repository
3. Configure:
   - **Runtime**: Docker
   - **Build Command**: (leave empty, uses Dockerfile)
   - **Start Command**: `uv run uvicorn api_server:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`

### Environment Variables to Set in Render:
- `OPENAI_API_KEY` (Required): Your OpenAI API key
- `LANGSMITH_API_KEY` (Optional): For tracing
- `LANGCHAIN_TRACING_V2`: true
- `LANGCHAIN_PROJECT`: langraph-chatbot-api

### After Deployment:
- Your API will be available at: `https://your-service-name.onrender.com`
- API docs: `https://your-service-name.onrender.com/docs`
- Health check: `https://your-service-name.onrender.com/health`

### Free Tier Limitations:
- Service sleeps after 15 minutes of inactivity
- 750 hours/month free
- First request after sleep takes ~30 seconds

### Scaling to Paid Plans:
- Faster cold starts
- Always-on services
- More memory and CPU
- Custom domains

## Local Testing:
```bash
# Test the API locally
uv run uvicorn api_server:app --reload

# Test endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"message": "Who is the CEO of Tesla?"}'
```

## Production Considerations:
- For persistent sessions, consider adding Redis
- For better performance, upgrade to paid Render plan
- Monitor usage and costs
- Set up proper logging and monitoring
