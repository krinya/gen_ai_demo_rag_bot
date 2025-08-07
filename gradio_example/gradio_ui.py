"""
Advanced Gradio Chat Interface with Routing Insights
Shows the intelligent routing capabilities of the AI chatbot
"""

import gradio as gr
import requests
import uuid
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# API Configuration
API_BASE_URL = "https://gen-ai-demo-rag-bot.onrender.com"
CHAT_ENDPOINT = f"{API_BASE_URL}/chat"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"

# Pre-populated example queries by routing type (one per type)
EXAMPLE_QUERIES = {
    "FAQ": "Who is the CEO of Tesla?",
    "RAG": "What was Apple's revenue in 2024?", 
    "LLM": "How do you calculate price-to-earnings ratio?"
}

# Color schemes for different routing types
ROUTING_COLORS = {
    "faq": "🔍 #4CAF50",      # Green
    "rag": "📚 #2196F3",      # Blue  
    "llm": "🧠 #FF9800",      # Orange
    "general": "💭 #9E9E9E"   # Gray
}

def check_api_health() -> Tuple[bool, str]:
    """Check if the API is accessible"""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        if response.status_code == 200:
            return True, "✅ API is online and healthy"
        else:
            return False, f"❌ API returned status {response.status_code}. The free Render API may take up to 1 minute to start on the first request. Please wait 1 minute and try again."
    except requests.exceptions.RequestException as e:
        return False, f"❌ Cannot connect to API: {str(e)}. The free Render API may take up to 1 minute to start on the first request. Please wait 1 minute and try again."

def send_message_to_api(message: str, session_id: str) -> Dict:
    """Send message to the chatbot API"""
    try:
        payload = {
            "message": message,
            "session_id": session_id
        }
        
        response = requests.post(
            CHAT_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=150
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"API Error {response.status_code}: {response.text}",
                "response": "Sorry, I'm having trouble connecting to the server right now."
            }
            
    except requests.exceptions.Timeout:
        return {
            "error": "Request timeout",
            "response": "Sorry, the request took too long. Please try again."
        }
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Connection error: {str(e)}",
            "response": "Sorry, I can't connect to the server right now."
        }

def format_routing_info(routing_data: Dict) -> str:
    """Format routing information for display"""
    if not routing_data:
        return "No routing information available"
    
    primary_route = routing_data.get('primary_route', 'unknown')
    final_source = routing_data.get('final_source', primary_route)
    answer_quality = routing_data.get('answer_quality', 'unknown')
    
    # Get color and icon for the route
    color_info = ROUTING_COLORS.get(primary_route.lower(), ROUTING_COLORS['general'])
    icon, color = color_info.split(' ')
    
    info_lines = [
        f"**Route:** {icon} {primary_route.upper()}",
        f"**Source:** {final_source.upper()}",
        f"**Quality:** {answer_quality.title()}"
    ]
    
    # Add additional details if available
    rephrase_attempts = routing_data.get('rephrase_attempts', 0)
    if rephrase_attempts > 0:
        info_lines.append(f"**Rephrase attempts:** {rephrase_attempts}")
    
    failed_sources = routing_data.get('failed_sources', [])
    if failed_sources:
        info_lines.append(f"**Failed sources:** {', '.join(failed_sources)}")
    
    return "\n".join(info_lines)

def format_chat_message(message: str, is_user: bool, routing_info: Optional[Dict] = None) -> str:
    """Format a chat message with optional routing information"""
    timestamp = datetime.now().strftime("%H:%M")
    
    if is_user:
        return f"**👤 You** *({timestamp})*\n{message}"
    else:
        # Bot message with routing info
        route_indicator = ""
        if routing_info:
            primary_route = routing_info.get('primary_route', 'general').lower()
            color_info = ROUTING_COLORS.get(primary_route, ROUTING_COLORS['general'])
            icon = color_info.split(' ')[0]
            route_indicator = f" {icon}"
        
        return f"**🤖 Assistant{route_indicator}** *({timestamp})*\n{message}"

def chat_with_bot(message: str, history: List[Dict[str, str]], session_id: str, show_routing: bool) -> Tuple[List[Dict[str, str]], str, str, str]:
    """Main chat function"""
    if not message.strip():
        return history, "", "", session_id
    
    # Send message to API with persistent session ID
    api_response = send_message_to_api(message, session_id)
    
    # Extract response and routing info
    bot_response = api_response.get('response', 'Sorry, I encountered an error.')
    metadata = api_response.get('metadata', {})
    routing_info = metadata.get('routing_info', {})
    
    # Format routing information
    routing_display = ""
    if show_routing and routing_info:
        routing_display = format_routing_info(routing_info)
    
    # Add to chat history using messages format
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": bot_response})
    
    return history, "", routing_display, session_id

def load_example(example_text: str) -> str:
    """Load an example query into the input box"""
    return example_text

def create_gradio_interface():
    """Create and configure the Gradio interface"""
    
    # Check API health at startup
    is_healthy, health_status = check_api_health()
    
    with gr.Blocks(
        title="🤖 AI Chatbot with Smart Routing",
        theme=gr.themes.Soft(),
        css="""
        .routing-info {
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 12px;
            margin: 8px 0;
            border-radius: 4px;
        }
        .example-button {
            margin: 2px;
            font-size: 0.9em;
        }
        .health-status {
            font-weight: bold;
            padding: 8px;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        .session-indicator {
            color: #28a745;
            font-size: 0.9em;
            margin: 8px 0;
        }
        .footer-info {
            color: #6c757d;
            font-size: 0.9em;
            text-align: center;
            margin-top: 20px;
        }
        """
    ) as interface:
        
        # Header
        gr.Markdown("""
        # 🤖 Financial AI Chatbot with Smart Routing & RAG
        
        **A prototype showcasing advanced AI capabilities for financial Q&A**
        
        This intelligent chatbot answers financial questions about **5 major companies** (Apple, Google, Amazon, Tesla, Intel) using smart routing:
        
        - 🔍 **FAQ Route**: Quick facts (CEO names, founding dates, basic company info)
        - 📚 **RAG Route**: Detailed financial data from 2024 annual reports (revenue, profits, growth metrics)
        - 🧠 **LLM Route**: General explanations and complex financial concepts
        
        **🏗️ Architecture**: Built with LangChain, OpenAI GPT-4o-mini, ChromaDB vector storage, and deployed on Render.
        
        **📊 View the workflow**: [Architecture Diagram](https://github.com/krinya/gen_ai_demo_rag_bot/blob/main/packages/chatbot/chatbot_workflow_graph.png) | **💻 Source Code**: [GitHub Repository](https://github.com/krinya/gen_ai_demo_rag_bot/tree/main)
        
        ---
        """)
        
        # API Health Status
        health_display = gr.Markdown(
            value=f"<div class='health-status' style='background-color: {'#d4edda' if is_healthy else '#f8d7da'}'>{health_status}</div>",
            elem_classes=["health-status"]
        )
        
        # Hidden session ID state (persistent across interactions)
        session_state = gr.State(value=str(uuid.uuid4()))
        
        # Chat interface (full width)
        chatbot = gr.Chatbot(
            value=[],
            label="Chat History",
            height=500,
            show_label=True,
            type="messages"
        )
        
        with gr.Row():
            msg_input = gr.Textbox(
                placeholder="Ask about Apple, Google, Amazon, Tesla, or Intel financials...",
                label="Your Financial Question",
                scale=4,
                lines=1
            )
            send_btn = gr.Button("Send 📤", scale=1, variant="primary")
        
        # Example queries below chat interface
        gr.Markdown("### 💡 Try These Examples")
        
        with gr.Row():
            for route_type, example in EXAMPLE_QUERIES.items():
                color_info = ROUTING_COLORS.get(route_type.lower(), ROUTING_COLORS['general'])
                icon, color = color_info.split(' ')
                
                example_btn = gr.Button(
                    f"{icon} {example}",
                    size="sm",
                    elem_classes=["example-button"]
                )
                example_btn.click(
                    fn=load_example,
                    inputs=[gr.State(example)],
                    outputs=[msg_input]
                )
        
        # Settings and controls
        with gr.Row():
            show_routing = gr.Checkbox(
                value=True,
                label="Show routing insights",
                info="Display how the AI routes your questions"
            )
            clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")
            new_session_btn = gr.Button("🔄 New Session", variant="secondary")
            session_indicator = gr.Markdown("💾 **Memory Active** - I'll remember our conversation", elem_classes=["session-indicator"])
        
        # Routing insights at the bottom
        routing_info = gr.Markdown(
            value="*Routing information will appear here after sending a message*",
            label="🧭 Routing Insights",
            elem_classes=["routing-info"]
        )
        
        # Footer with deployment info
        gr.Markdown("""
        ---
        **🚀 Deployment Info**: This prototype is powered by a FastAPI backend deployed on [Render](https://render.com), 
        showcasing full-stack AI development skills with production-ready architecture.
        
        **🛠️ Tech Stack**: LangChain • OpenAI GPT-4o-mini • ChromaDB • FastAPI • Render • Gradio
        """, elem_classes=["footer-info"])
        
        # Event handlers
        def clear_chat():
            return [], ""
        
        def new_session():
            return str(uuid.uuid4()), [], ""
        
        # Button click events
        clear_btn.click(
            fn=clear_chat,
            outputs=[chatbot, routing_info]
        )
        
        new_session_btn.click(
            fn=new_session,
            outputs=[session_state, chatbot, routing_info]
        )
        
        # Chat submission events with loading
        def chat_wrapper(message, history, session_id, show_routing):
            # Show loading message
            if message.strip():
                # Add user message and loading response immediately
                loading_history = history + [
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": "🤔 Thinking... be patient, free servers are slow."}
                ]
                yield loading_history, "", "🔄 Processing your message...", session_id
                
                # Get actual response
                result_history, empty_input, routing_info, updated_session = chat_with_bot(message, history, session_id, show_routing)
                yield result_history, "", routing_info, updated_session
            else:
                yield history, "", "", session_id
        
        send_btn.click(
            fn=chat_wrapper,
            inputs=[msg_input, chatbot, session_state, show_routing],
            outputs=[chatbot, msg_input, routing_info, session_state]
        )
        
        msg_input.submit(
            fn=chat_wrapper,
            inputs=[msg_input, chatbot, session_state, show_routing],
            outputs=[chatbot, msg_input, routing_info, session_state]
        )
        
    return interface

if __name__ == "__main__":
    # Create and launch the interface
    interface = create_gradio_interface()
    
    print("🚀 Starting Gradio Chat Interface...")
    print(f"🔗 API Endpoint: {API_BASE_URL}")
    
    # Launch with configuration
    interface.launch(
        server_name="127.0.0.1",  # Local access only
        server_port=7860,
        share=False,
        debug=True,
        show_error=True,
        favicon_path=None,
        auth=None 
    )
