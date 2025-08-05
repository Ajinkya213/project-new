#!/usr/bin/env python3
"""
Lightweight agent service for simple queries
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class LightweightAgent:
    """Simple lightweight agent using Gemini AI"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                print("[INFO] Lightweight agent initialized with Gemini AI")
            except Exception as e:
                print(f"[WARNING] Failed to initialize Gemini AI: {e}")
                self.model = None
        else:
            print("[WARNING] GEMINI_API_KEY not found, using fallback mode")
            self.model = None
    
    def process_query(self, query: str, context: dict = None) -> str:
        """Process a query using Gemini AI or fallback"""
        try:
            if self.model:
                response = self.model.generate_content(query)
                return response.text
            else:
                # Fallback response when Gemini is not available
                return f"I'm here to help! You asked: '{query}'. I'm currently in fallback mode as the AI model is not configured. Please set your GEMINI_API_KEY environment variable to enable full AI capabilities."
        except Exception as e:
            print(f"[ERROR] Lightweight agent error: {e}")
            return f"I encountered an error while processing your request. Please try again. Error: {str(e)}"

# Create lightweight agent instance
lightweight_agent = LightweightAgent() 