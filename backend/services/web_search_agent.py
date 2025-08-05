#!/usr/bin/env python3
"""
Simple web search agent using Tavily
"""

import os
from tavily import TavilyClient
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class WebSearchAgent:
    """Simple web search agent using Tavily and Gemini"""
    
    def __init__(self):
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        
        # Configure Gemini if available
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
    
    def search_web(self, query: str) -> str:
        """Search the web using Tavily"""
        try:
            if not self.tavily_key or self.tavily_key == "your-tavily-api-key":
                return "Search failed: TAVILY_API_KEY not configured. Please set your Tavily API key in environment variables."
            
            client = TavilyClient(api_key=self.tavily_key)
            results = client.search(query=query, max_results=5)
            
            if not results or not results.get("results"):
                return "No search results found."
            
            # Extract content from results
            content_list = []
            for result in results["results"]:
                if "content" in result:
                    content_list.append(result["content"])
            
            if content_list:
                return "\n\n".join(content_list)
            else:
                return "Search completed but no content found."
                
        except Exception as e:
            return f"Search failed: {str(e)}"
    
    def process_query(self, query: str) -> str:
        """Process a query with web search and AI synthesis"""
        try:
            # First, search the web
            search_results = self.search_web(query)
            
            if "Search failed" in search_results:
                return search_results
            
            # If we have Gemini, synthesize the results
            if self.model and search_results:
                prompt = f"""
                Based on the following web search results, provide a comprehensive answer to the query: "{query}"
                
                Search Results:
                {search_results}
                
                Please provide a well-structured response that directly answers the query using the search results.
                """
                
                response = self.model.generate_content(prompt)
                return response.text
            else:
                # Return search results directly if no AI synthesis available
                return f"Web Search Results for '{query}':\n\n{search_results}"
                
        except Exception as e:
            return f"Error processing query: {str(e)}"
    
    def is_configured(self) -> bool:
        """Check if the agent is properly configured"""
        return bool(self.tavily_key and self.tavily_key != "your-tavily-api-key")

# Create web search agent instance
web_search_agent = WebSearchAgent() 