import os
from typing import Dict

# Simple fallback RAG implementation
class SimpleRAG:
    def __init__(self, url: str, api_key: str):
        self.url = url
        self.api_key = api_key
        print("[INFO] SimpleRAG initialized successfully")
    
    def generate_result(self, query_text: str) -> Dict:
        """Generate a simple result without heavy dependencies"""
        try:
            return {
                "status": "success",
                "response": f"I understand your query: '{query_text}'. This is a simple response from the RAG system.",
                "quality_metrics": {"quality": "basic"},
                "num_images_processed": 0
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing query: {str(e)}",
                "response": "I encountered an error while processing your query. Please try again."
            }

class RAGSingleton:
    """Lazy-loaded RAG singleton"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RAGSingleton, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._rag = None
            self._initialized = True
    
    def _initialize_rag(self):
        """Lazy initialize RAG when first accessed"""
        if self._rag is None:
            try:
                from .rag_utils import MultiModalRAG
                from app_config import QDRANT_URL, QDRANT_API_KEY
                self._rag = MultiModalRAG(url=QDRANT_URL, api_key=QDRANT_API_KEY)
                print("[INFO] MultiModalRAG initialized successfully")
            except ImportError as e:
                print(f"[WARNING] Could not import MultiModalRAG: {e}")
                print("[INFO] Using SimpleRAG fallback")
                self._rag = SimpleRAG(url="", api_key="")
            except Exception as e:
                print(f"[WARNING] Error initializing MultiModalRAG: {e}")
                print("[INFO] Using SimpleRAG fallback")
                self._rag = SimpleRAG(url="", api_key="")
    
    def generate_result(self, query_text: str) -> Dict:
        """Generate result using lazy-loaded RAG"""
        if self._rag is None:
            self._initialize_rag()
        return self._rag.generate_result(query_text)

# Create singleton instance
rag = RAGSingleton() 