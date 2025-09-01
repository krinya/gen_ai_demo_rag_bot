"""
LangGraph Visualization Script

This script creates a visual representation of the chatbot's LangGraph workflow
directly from the actual template_main.py implementation, to see the real structure.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Import the actual chatbot class
import sys
from pathlib import Path
# Add project root to path for standalone execution
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from packages.chatbot.main import MainChatbot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_graph_image():
    """Generate and save the graph visualization from the actual chatbot implementation"""
    try:
        # Load environment
        load_dotenv()
        
        # Create an actual chatbot instance to get the real workflow
        chatbot = MainChatbot()
        
        # Get the compiled workflow from the chatbot
        app = chatbot.app
        
        # Generate the visualization
        output_path = Path(__file__).parent / "chatbot_workflow_graph.png"
        
        # Create the graph image using the actual workflow
        graph_image = app.get_graph().draw_mermaid_png()
        
        # Save to file
        with open(output_path, "wb") as f:
            f.write(graph_image)
        
        logger.info(f"✅ Graph visualization saved to: {output_path}")
        
        # Print workflow summary
        print("\n🔍 Workflow Analysis:")
        print("=" * 40)
        nodes = app.get_graph().nodes
        edges = app.get_graph().edges
        print(f"📊 Total nodes: {len(nodes)}")
        print(f"🔗 Total edges: {len(edges)}")
        print(f"📋 Nodes: {', '.join(nodes.keys())}")
        print("=" * 40)
        
        return str(output_path)
        
    except Exception as e:
        logger.error(f"Error generating graph visualization: {e}")
        logger.error(f"Make sure template_main.py is working correctly")
        return None

def main():
    """Main function to generate the graph visualization"""
    print("🎨 Generating LangGraph Workflow Visualization...")
    print("=" * 60)
    
    output_path = generate_graph_image()
    
    if output_path:
        print(f"✅ Success! Graph visualization saved to:")
        print(f"   📄 {output_path}")
        print("\n💡 You can now view the workflow structure visually!")
    else:
        print("❌ Failed to generate graph visualization")
        print("💡 Make sure you have graphviz installed: brew install graphviz")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
