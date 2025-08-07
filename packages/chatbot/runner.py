"""
Command Line Interface for the Template Chatbot

This module provides an interactive CLI for testing and using the chatbot.
It includes session management, conversation history, and system diagnostics.
"""

import asyncio
import sys
import signal
from pathlib import Path
from typing import Optional
import logging

# Add the project root directory to the Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from packages.chatbot.main import MainChatbot, create_chatbot
from packages.chatbot.utils import (
    print_system_status, 
    generate_session_id
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ChatbotCLI:
    """Command Line Interface for the Template Chatbot"""
    
    def __init__(self):
        self.chatbot: Optional[MainChatbot] = None
        self.session_id: Optional[str] = None
        self.running = True
        
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n👋 Goodbye! Thanks for using the Template Chatbot!")
        self.running = False
        sys.exit(0)
    
    async def initialize_chatbot(self) -> bool:
        """Initialize the chatbot and return success status"""
        try:
            print("🤖 Initializing Template Chatbot...")
            self.session_id = generate_session_id()
            self.chatbot = await create_chatbot(self.session_id)
            print(f"✅ Chatbot initialized successfully!")
            print(f"📝 Session ID: {self.session_id}...")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize chatbot: {e}")
            print("💡 Please check your .env file and ensure all required dependencies are installed.")
            return False
    
    def display_welcome_message(self):
        """Display the welcome message and instructions"""
        print("\n" + "="*70)
        print("🤖 Welcome to the Template AI Chatbot!")
        print("="*70)
        print("📚 This chatbot can help you with:")
        print("   • FAQ questions (simple, direct questions)")
        print("   • RAG queries (complex questions using document knowledge)")
        print("   • General knowledge (powered by GPT-4o-mini)")
        print()
        print("💬 Commands:")
        print("   • Type your question and press Enter")
        print("   • 'help' - Show available commands")
        print("   • 'status' - Show system status")
        print("   • 'history' - Show conversation history")
        print("   • 'reset' - Start a new conversation")
        print("   • 'quit' or 'exit' - Exit the chatbot")
        print("   • Ctrl+C - Quick exit")
        print("="*70)
    
    def display_help(self):
        """Display help information"""
        print("\n📖 Help - Available Commands:")
        print("-" * 40)
        print("🔤 Regular conversation:")
        print("   Just type your question and press Enter")
        print()
        print("🛠️ Special commands:")
        print("   help     - Show this help message")
        print("   status   - Check system status and configuration")
        print("   history  - View conversation history")
        print("   reset    - Start a fresh conversation")
        print("   quit     - Exit the chatbot")
        print("   exit     - Exit the chatbot")
        print()
        print("💡 Tips:")
        print("   • Be specific in your questions for better results")
        print("   • The system will automatically route your question to the best source")
        print("   • If you get a poor answer, try rephrasing your question")
        print("-" * 40)
    
    async def show_conversation_history(self):
        """Display the conversation history"""
        if not self.chatbot:
            print("❌ Chatbot not initialized")
            return
        
        try:
            messages = self.chatbot.get_conversation_history()
            if not messages:
                print("📝 No conversation history yet. Start chatting!")
                return
            
            print(f"\n📚 Conversation History (Session: {self.session_id}...):")
            print("-" * 50)
            
            for i, message in enumerate(messages, 1):
                role = "🧑 You" if hasattr(message, 'type') and message.type == "human" else "🤖 Assistant"
                content = message.content
                
                # Truncate long messages for better display
                if len(content) > 200:
                    content = content[:200] + "..."
                
                print(f"{i}. {role}: {content}")
                print()
            
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ Error retrieving conversation history: {e}")
    
    async def reset_conversation(self):
        """Reset the conversation"""
        if not self.chatbot:
            print("❌ Chatbot not initialized")
            return
        
        try:
            self.chatbot.reset_conversation()
            self.session_id = self.chatbot.session_id
            print(f"🔄 Conversation reset! New session: {self.session_id}...")
        except Exception as e:
            print(f"❌ Error resetting conversation: {e}")
    
    def show_system_status(self):
        """Display system status"""
        print("\n🔍 System Status Check:")
        print_system_status()
    
    async def process_user_input(self, user_input: str) -> bool:
        """
        Process user input and return whether to continue
        
        Args:
            user_input: The user's input string
            
        Returns:
            True to continue the conversation, False to exit
        """
        user_input = user_input.strip()
        
        # Handle empty input
        if not user_input:
            return True
        
        # Handle special commands
        if user_input.lower() in ['quit', 'exit']:
            return False
        
        elif user_input.lower() == 'help':
            self.display_help()
            return True
        
        elif user_input.lower() == 'status':
            self.show_system_status()
            return True
        
        elif user_input.lower() == 'history':
            await self.show_conversation_history()
            return True
        
        elif user_input.lower() == 'reset':
            await self.reset_conversation()
            return True
        
        # Regular conversation
        else:
            await self.handle_chat_message(user_input)
            return True
    
    async def handle_chat_message(self, user_input: str):
        """Handle a regular chat message"""
        if not self.chatbot:
            print("❌ Chatbot not initialized")
            return
        
        try:
            print("\n🤔 Thinking...")
            
            # Get response from chatbot
            response = await self.chatbot.chat(user_input)
            
            # Display response
            print(f"\n🤖 Assistant: {response}")
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            print(f"\n❌ Sorry, I encountered an error: {e}")
            print("💡 Please try rephrasing your question or check your configuration.")
    
    async def run_interactive_mode(self):
        """Run the interactive chat mode"""
        while self.running:
            try:
                # Get user input
                user_input = input("\n🧑 You: ").strip()
                
                # Process input
                should_continue = await self.process_user_input(user_input)
                
                if not should_continue:
                    break
                    
            except KeyboardInterrupt:
                # Handle Ctrl+C
                break
            except EOFError:
                # Handle Ctrl+D
                break
            except Exception as e:
                logger.error(f"Unexpected error in interactive mode: {e}")
                print(f"❌ Unexpected error: {e}")
        
        print("\n👋 Goodbye! Thanks for using the Template Chatbot!")
    
    async def run_demo_mode(self):
        """Run a demonstration with predefined questions"""
        print("\n🎬 Running Demo Mode...")
        print("This will test the chatbot with various types of questions.")
        
        demo_questions = [
            "Who is the CEO of Tesla?",
            "How much was the net income of Intel in 2024?",
            "How does machine learning work?"
        ]
        
        for i, question in enumerate(demo_questions, 1):
            print(f"\n{'='*60}")
            print(f"Demo Question {i}: {question}")
            print("-" * 40)
            
            try:
                response = await self.chatbot.chat(question)
                print(f"🤖 Response: {response}")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("="*60)
            
            # Small pause between questions
            await asyncio.sleep(1)
        
        print("\n✅ Demo completed!")

async def main():
    """Main CLI function"""
    cli = ChatbotCLI()
    
    # Check if this is a demo run
    demo_mode = len(sys.argv) > 1 and sys.argv[1].lower() == 'demo'
    
    # Show initial system status
    if not demo_mode:
        print("🔍 Checking system status...")
        cli.show_system_status()
        print()
    
    # Initialize chatbot
    if not await cli.initialize_chatbot():
        print("\n💡 Setup steps:")
        print("1. Create a .env file with your OPENAI_API_KEY")
        print("2. Run: python -m pip install -r requirements.txt")
        print("3. Create vector storage: python rag_input_documents/create_vector_storage.py")
        return
    
    # Display welcome message
    if not demo_mode:
        cli.display_welcome_message()
    
    # Run appropriate mode
    try:
        if demo_mode:
            await cli.run_demo_mode()
        else:
            await cli.run_interactive_mode()
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
        print(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    # Handle different Python versions
    try:
        asyncio.run(main())
    except AttributeError:
        # Python < 3.7 compatibility
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())