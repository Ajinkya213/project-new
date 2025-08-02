from crewai.tools import tool
from tavily import TavilyClient
import os
from backend.core.rag_singleton import rag 

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY") or "your-tavily-api-key"

@tool("Web Search Tool")
def search_web(query: str) -> str:
    """Search the web using Tavily."""
    client = TavilyClient(api_key=TAVILY_API_KEY)
    try:
        results = client.search(query=query, max_results=3)
        return "\n".join([r["content"] for r in results["results"]])
    except Exception as e:
        return f"Search failed: {e}"

@tool("Document Retrival tool")
def retrive_from_document(query:str)->str:
    """
    Retrieve relevant content from the document database based on the user's query.
    """
    try:
        result=rag.generate_result(query)
        if result['status']=="success":
            return result
        elif result['status']=="no_results":
            return result['message']
        else:
            return f"Error: {result['message']}"
    except Exception as e:
        return f"Retrival failed: {e}"
    