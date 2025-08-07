# Gradio Chat Interface

A beautiful web interface for the AI Chatbot with Smart Routing capabilities.

## Features

- 🎨 **Modern UI** - Clean, responsive design with Gradio
- 🧭 **Routing Insights** - See how the AI decides between FAQ/RAG/LLM
- 💡 **Pre-built Examples** - Quick-test buttons for each routing type
- 🔄 **Session Management** - Maintain conversation history
- 📱 **Real-time Updates** - Live routing information display
- ⚡ **Easy to Use** - Just click and chat!

## Quick Start

```bash
# Run the Gradio interface
uv run python gradio_example/run_ui.py
```

The interface will automatically open in your browser at `http://127.0.0.1:7860`

## Example Queries

### 🔍 FAQ Questions (Quick Facts)
- "Who is the CEO of Tesla?"
- "Who is the CEO of Apple?"
- "Who founded Google?"
- "When was Amazon founded?"

### 📚 RAG Questions (Data Retrieval)
- "What was Apple's revenue in 2024?"
- "Tell me about Tesla's financial performance"
- "What are Google's main business segments?"
- "Show me Intel's recent earnings data"

### 🧠 LLM Questions (General Knowledge)
- "How does machine learning work?"
- "Explain artificial intelligence in simple terms"
- "What are the benefits of electric vehicles?"
- "How do stock markets work?"

## Interface Overview

### Main Chat Area
- **Chat History**: Displays conversation with timestamps
- **Message Input**: Type your questions here
- **Send Button**: Submit your message
- **Session Management**: Create new sessions or clear chat

### Routing Insights Panel
- **Route Type**: Shows FAQ/RAG/LLM decision
- **Confidence Score**: How confident the AI is in its routing
- **Explanation**: Why this route was chosen
- **Alternatives**: Other routes considered

### Example Buttons
- **Quick Testing**: Click any example to try it instantly
- **Organized by Type**: Examples grouped by routing type
- **Color Coded**: Visual indicators for each route type

## Customization

### API Endpoint
The interface connects to the deployed API at `https://gen-ai-demo-rag-bot.onrender.com/`

To use a local API, modify the `API_BASE_URL` in `gradio_ui.py`:
```python
API_BASE_URL = "http://localhost:8000"  # For local development
```

### Styling
The interface uses a custom CSS theme. You can modify the styling in the `css` parameter of `gr.Blocks()`.

### Examples
Add your own example queries by modifying the `EXAMPLE_QUERIES` dictionary in `gradio_ui.py`.

## Troubleshooting

### Connection Issues
- Check that the API is accessible: `curl https://gen-ai-demo-rag-bot.onrender.com/health`
- Verify your internet connection
- The interface shows API health status at the top

### Port Already in Use
If port 7860 is busy, modify the `server_port` in `run_ui.py`:
```python
interface.launch(server_port=7861)  # Use different port
```

### Dependencies
Make sure you have the required packages:
```bash
uv add gradio requests
```

## Development

### File Structure
```
gradio_example/
├── gradio_ui.py      # Main Gradio interface code
├── run_ui.py         # Runner script
└── README.md         # This file
```

### Adding Features
The interface is modular and easy to extend:
- Add new example categories in `EXAMPLE_QUERIES`
- Modify routing display in `format_routing_info()`
- Customize chat formatting in `format_chat_message()`
- Add new UI components in `create_gradio_interface()`
