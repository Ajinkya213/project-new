#!/usr/bin/env python3
"""
Lightweight agent service for simple queries
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class LightweightAgent:
    """Simple lightweight agent using Gemini AI"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def process_query(self, query: str) -> str:
        """Process a query using Gemini AI"""
        try:
            response = self.model.generate_content(query)
            return response.text
        except Exception as e:
            return f"I encountered an error: {str(e)}"

# Create lightweight agent instance
lightweight_agent = LightweightAgent() 