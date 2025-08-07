#!/usr/bin/env python3
"""
Runner script for the Gradio Chat Interface
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from gradio_example.gradio_ui import create_gradio_interface

if __name__ == "__main__":
    print("🤖 AI Chatbot with Smart Routing - Gradio Interface")
    print("=" * 50)
    
    # Create and launch the interface
    interface = create_gradio_interface()
    
    print("\n🚀 Starting Gradio interface...")
    print("📱 The interface will open in your browser automatically")
    print("🔗 API: https://gen-ai-demo-rag-bot.onrender.com/")
    print("\n💡 Try asking:")
    print("   • 'Who is the CEO of Tesla?' (FAQ routing)")
    print("   • 'What was Apple's revenue in 2024?' (RAG routing)")
    print("   • 'How does machine learning work?' (LLM routing)")
    print("\n⚡ Press Ctrl+C to stop")
    
    try:
        interface.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=False,
            debug=False,
            show_error=True,
            inbrowser=True,  # Automatically open browser
            favicon_path=None
        )
    except KeyboardInterrupt:
        print("\n👋 Gradio interface stopped")
    except Exception as e:
        print(f"\n❌ Error starting interface: {e}")
        sys.exit(1)
