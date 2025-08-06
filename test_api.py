#!/usr/bin/env python3
"""
Test script for the LangGraph Chatbot API
"""
import requests
import json
import time

def test_api(base_url="http://localhost:8000"):
    """Test the API endpoints"""
    print(f"🧪 Testing API at {base_url}")
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
        return False
    
    # Test root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(base_url)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test create session
    print("\n3. Testing session creation...")
    try:
        response = requests.post(f"{base_url}/sessions")
        session_data = response.json()
        session_id = session_data["session_id"]
        print(f"   Status: {response.status_code}")
        print(f"   Session ID: {session_id}")
    except Exception as e:
        print(f"   Error: {e}")
        return False
    
    # Test chat - FAQ question
    print("\n4. Testing FAQ question...")
    try:
        chat_data = {
            "message": "Who is the CEO of Tesla?",
            "session_id": session_id
        }
        response = requests.post(f"{base_url}/chat", json=chat_data)
        print(f"   Status: {response.status_code}")
        chat_response = response.json()
        print(f"   Response: {chat_response['response'][:100]}...")
    except Exception as e:
        print(f"   Error: {e}")
        return False
    
    # Test chat - RAG question
    print("\n5. Testing RAG question...")
    try:
        chat_data = {
            "message": "What was Tesla's revenue in 2024?",
            "session_id": session_id
        }
        response = requests.post(f"{base_url}/chat", json=chat_data)
        print(f"   Status: {response.status_code}")
        chat_response = response.json()
        print(f"   Response: {chat_response['response'][:100]}...")
    except Exception as e:
        print(f"   Error: {e}")
        return False
    
    # Test conversation history
    print("\n6. Testing conversation history...")
    try:
        response = requests.get(f"{base_url}/sessions/{session_id}/history")
        print(f"   Status: {response.status_code}")
        history = response.json()
        print(f"   History length: {len(history['history'])} messages")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ API testing completed!")
    return True

if __name__ == "__main__":
    import sys
    
    # Allow custom URL for testing deployed version
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    success = test_api(base_url)
    exit(0 if success else 1)
