#!/usr/bin/env python3
"""
API Test Script for LangGraph Chatbot

This script tests all the main endpoints of the deployed chatbot API
and provides a comprehensive validation of the system.
"""

import requests
import json
import time
import sys
from typing import Dict, Any

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session_id = None
        
    def test_health(self) -> Dict[str, Any]:
        """Test the health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            return {
                "status": "success" if response.status_code == 200 else "failed",
                "response": response.json() if response.status_code == 200 else response.text,
                "status_code": response.status_code
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def test_root(self) -> Dict[str, Any]:
        """Test the root endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            return {
                "status": "success" if response.status_code == 200 else "failed",
                "response": response.json() if response.status_code == 200 else response.text,
                "status_code": response.status_code
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def test_create_session(self) -> Dict[str, Any]:
        """Test session creation"""
        try:
            response = self.session.post(f"{self.base_url}/sessions", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("session_id")
                return {
                    "status": "success",
                    "response": data,
                    "status_code": response.status_code
                }
            else:
                return {
                    "status": "failed",
                    "response": response.text,
                    "status_code": response.status_code
                }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def test_chat(self, message: str) -> Dict[str, Any]:
        """Test chat functionality"""
        try:
            payload = {"message": message}
            if self.session_id:
                payload["session_id"] = self.session_id
                
            response = self.session.post(
                f"{self.base_url}/chat",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            return {
                "status": "success" if response.status_code == 200 else "failed",
                "response": response.json() if response.status_code == 200 else response.text,
                "status_code": response.status_code
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def test_demo(self) -> Dict[str, Any]:
        """Test the demo endpoint"""
        try:
            response = self.session.post(f"{self.base_url}/demo", timeout=30)
            return {
                "status": "success" if response.status_code == 200 else "failed",
                "response": response.json() if response.status_code == 200 else response.text,
                "status_code": response.status_code
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def test_history(self) -> Dict[str, Any]:
        """Test conversation history retrieval"""
        if not self.session_id:
            return {"status": "skipped", "reason": "No session ID available"}
            
        try:
            response = self.session.get(f"{self.base_url}/sessions/{self.session_id}/history", timeout=10)
            return {
                "status": "success" if response.status_code == 200 else "failed",
                "response": response.json() if response.status_code == 200 else response.text,
                "status_code": response.status_code
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def run_full_test(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results"""
        print(f"🧪 Testing API at: {self.base_url}")
        print("=" * 60)
        
        results = {}
        
        # Test 1: Health Check
        print("1. Testing health endpoint...")
        results["health"] = self.test_health()
        print(f"   Status: {results['health']['status']}")
        
        # Test 2: Root endpoint
        print("2. Testing root endpoint...")
        results["root"] = self.test_root()
        print(f"   Status: {results['root']['status']}")
        
        # Test 3: Session creation
        print("3. Testing session creation...")
        results["session_creation"] = self.test_create_session()
        print(f"   Status: {results['session_creation']['status']}")
        if self.session_id:
            print(f"   Session ID: {self.session_id[:8]}...")
        
        # Test 4: Chat functionality
        print("4. Testing chat with simple question...")
        results["chat_simple"] = self.test_chat("Hello! What can you help me with?")
        print(f"   Status: {results['chat_simple']['status']}")
        
        # Test 5: Chat with Tesla question
        print("5. Testing chat with Tesla question...")
        results["chat_tesla"] = self.test_chat("Who is the CEO of Tesla?")
        print(f"   Status: {results['chat_tesla']['status']}")
        
        # Test 6: Demo endpoint
        print("6. Testing demo endpoint...")
        results["demo"] = self.test_demo()
        print(f"   Status: {results['demo']['status']}")
        
        # Test 7: History
        print("7. Testing conversation history...")
        results["history"] = self.test_history()
        print(f"   Status: {results['history']['status']}")
        
        print("=" * 60)
        
        # Summary
        successful_tests = sum(1 for test in results.values() if test.get("status") == "success")
        total_tests = len(results)
        
        print(f"🎯 Test Summary: {successful_tests}/{total_tests} tests passed")
        
        if successful_tests == total_tests:
            print("✅ All tests passed! API is working correctly.")
        elif successful_tests >= total_tests * 0.7:
            print("⚠️  Most tests passed. Some functionality may have issues.")
        else:
            print("❌ Many tests failed. API has significant issues.")
        
        return results

def main():
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "https://gen-ai-demo-rag-bot.onrender.com"
    
    tester = APITester(base_url)
    results = tester.run_full_test()
    
    # Save detailed results to file
    with open("api_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📝 Detailed results saved to: api_test_results.json")

if __name__ == "__main__":
    main()
