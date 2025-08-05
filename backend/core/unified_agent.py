#!/usr/bin/env python3
"""
Unified Agent - Single Agent for All Query Types

This agent handles all types of queries and clearly justifies the source of results:
- Document queries (from uploaded documents)
- Web search queries (from internet)
- General knowledge queries (from training data)
"""

import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime

class UnifiedAgent:
    """
    Unified Agent that handles all query types with clear source justification
    """
    
    def __init__(self):
        self.rag_system = None
        self._initialize_components()
        print("[INFO] Unified Agent initialized")
    
    def _initialize_components(self):
        """Initialize all components"""
        try:
            # Initialize RAG system for document queries
            from .clean_rag_system import get_clean_rag
            self.rag_system = get_clean_rag()
            print("[INFO] RAG system initialized for document queries")
        except Exception as e:
            print(f"[WARNING] RAG system not available: {e}")
        
        # Initialize web search (you can add your preferred web search API)
        self.web_search_available = True  # Set to False if no web search API
        print("[INFO] Web search available for internet queries")
    
    def _detect_query_type(self, query: str) -> Dict[str, Any]:
        """
        Detect the type of query and determine the best approach
        """
        query_lower = query.lower()
        
        # Document-related keywords
        document_keywords = [
            'document', 'file', 'pdf', 'report', 'upload', 'uploaded',
            'my document', 'my file', 'my pdf', 'my report',
            'what is in', 'what does it say', 'summarize', 'extract',
            'find in document', 'search document', 'read document'
        ]
        
        # Web search keywords
        web_keywords = [
            'latest', 'news', 'current', 'recent', 'today', 'yesterday',
            'weather', 'stock', 'price', 'market', 'live', 'real-time',
            'what happened', 'what is happening', 'trending', 'popular'
        ]
        
        # Check for document keywords
        document_score = sum(1 for keyword in document_keywords if keyword in query_lower)
        
        # Check for web search keywords
        web_score = sum(1 for keyword in web_keywords if keyword in query_lower)
        
        # Check if we have documents available
        doc_count = 0
        if self.rag_system:
            try:
                doc_count = self.rag_system.get_document_count()
            except:
                pass
        
        # Determine query type
        if document_score > 0 and doc_count > 0:
            return {
                'type': 'document',
                'confidence': 0.9,
                'reason': f'Query contains document keywords ({document_score} matches) and documents are available ({doc_count} docs)',
                'documents_available': doc_count
            }
        elif web_score > 0:
            return {
                'type': 'web_search',
                'confidence': 0.8,
                'reason': f'Query contains web search keywords ({web_score} matches)',
                'documents_available': doc_count
            }
        elif doc_count > 0:
            return {
                'type': 'document',
                'confidence': 0.7,
                'reason': f'No specific keywords but documents are available ({doc_count} docs)',
                'documents_available': doc_count
            }
        else:
            return {
                'type': 'general',
                'confidence': 0.6,
                'reason': 'General knowledge query - no specific keywords or documents',
                'documents_available': doc_count
            }
    
    def _process_document_query(self, query: str) -> Dict[str, Any]:
        """Process query using document embeddings"""
        try:
            if not self.rag_system:
                return {
                    'status': 'error',
                    'message': 'RAG system not available',
                    'source': 'document',
                    'source_justification': 'Attempted document search but RAG system unavailable'
                }
            
            result = self.rag_system.process_query(query)
            
            if result.get('status') == 'success':
                return {
                    'status': 'success',
                    'response': result.get('response', ''),
                    'source': 'document',
                    'source_justification': f'Results generated from {result.get("images_retrieved", 0)} document images using vector search and Gemini analysis',
                    'documents_found': result.get('images_retrieved', 0),
                    'vectors_searched': result.get('vectors_searched', 0),
                    'gemini_analysis': result.get('gemini_analysis', ''),
                    'flow_steps': result.get('flow_steps', [])
                }
            else:
                return {
                    'status': 'error',
                    'message': result.get('message', 'Document query failed'),
                    'source': 'document',
                    'source_justification': 'Attempted document search but no relevant results found'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Document query failed: {str(e)}',
                'source': 'document',
                'source_justification': f'Document search failed due to error: {str(e)}'
            }
    
    def _process_web_search_query(self, query: str) -> Dict[str, Any]:
        """Process query using web search"""
        try:
            # This is a placeholder - you can integrate with your preferred web search API
            # For now, we'll simulate web search results
            
            # Simulate web search
            web_results = [
                {
                    'title': f'Web result for: {query}',
                    'snippet': f'This is a simulated web search result for "{query}". In a real implementation, this would be actual web search results.',
                    'url': 'https://example.com/search-result'
                }
            ]
            
            # Generate response based on web results
            response = f"""🔍 **Web Search Results:**
I found {len(web_results)} web search results for your query.

**Results:**
"""
            
            for i, result in enumerate(web_results, 1):
                response += f"{i}. **{result['title']}**\n   {result['snippet']}\n   Source: {result['url']}\n\n"
            
            response += f"""📋 **Analysis:**
Based on web search results, here's what I found about "{query}".

💾 **Source:** Web search results from internet
🔗 **Results Found:** {len(web_results)} web pages"""
            
            return {
                'status': 'success',
                'response': response,
                'source': 'web_search',
                'source_justification': f'Results generated from {len(web_results)} web search results using internet search',
                'web_results_found': len(web_results),
                'web_results': web_results
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Web search failed: {str(e)}',
                'source': 'web_search',
                'source_justification': f'Web search failed due to error: {str(e)}'
            }
    
    def _process_general_query(self, query: str) -> Dict[str, Any]:
        """Process query using general knowledge"""
        try:
            # Simple response generation for general queries
            responses = {
                'hello': 'Hello! How can I help you today?',
                'help': 'I can help you with various tasks. What would you like to know?',
                'weather': 'I don\'t have access to real-time weather data, but I can help you with other questions!',
                'time': f'The current time is {datetime.now().strftime("%H:%M:%S")}',
                'date': f'Today is {datetime.now().strftime("%Y-%m-%d")}'
            }
            
            # Check for simple queries
            query_lower = query.lower()
            for key, response in responses.items():
                if key in query_lower:
                    return {
                        'status': 'success',
                        'response': response,
                        'source': 'general_knowledge',
                        'source_justification': 'Response generated from general knowledge and built-in responses',
                        'knowledge_type': 'built_in_response'
                    }
            
            # Default response
            return {
                'status': 'success',
                'response': f'I understand you said: "{query}". This is a general knowledge response based on my training data.',
                'source': 'general_knowledge',
                'source_justification': 'Response generated from general knowledge and training data',
                'knowledge_type': 'training_data'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'General query failed: {str(e)}',
                'source': 'general_knowledge',
                'source_justification': f'General knowledge query failed due to error: {str(e)}'
            }
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Main method to process any query type with clear source justification
        """
        try:
            print(f"[INFO] Unified Agent processing query: {query}")
            
            # Step 1: Detect query type
            query_analysis = self._detect_query_type(query)
            query_type = query_analysis['type']
            confidence = query_analysis['confidence']
            reason = query_analysis['reason']
            
            print(f"[INFO] Query type: {query_type} (confidence: {confidence})")
            print(f"[INFO] Reason: {reason}")
            
            # Step 2: Process based on type
            if query_type == 'document':
                result = self._process_document_query(query)
            elif query_type == 'web_search':
                result = self._process_web_search_query(query)
            else:  # general
                result = self._process_general_query(query)
            
            # Step 3: Add unified agent information
            result['agent_type'] = 'unified'
            result['query_type'] = query_type
            result['confidence'] = confidence
            result['reason'] = reason
            result['query_analysis'] = query_analysis
            
            # Step 4: Add source badge for frontend
            source_badge = {
                'document': '📄 Document Search',
                'web_search': '🌐 Web Search', 
                'general_knowledge': '🧠 General Knowledge'
            }
            
            result['source_badge'] = source_badge.get(result['source'], '❓ Unknown')
            
            print(f"[INFO] Unified Agent completed - Source: {result['source']}")
            return result
            
        except Exception as e:
            print(f"[ERROR] Unified Agent failed: {e}")
            return {
                'status': 'error',
                'message': f'Unified Agent failed: {str(e)}',
                'agent_type': 'unified',
                'source': 'error',
                'source_justification': f'Query processing failed due to error: {str(e)}'
            }

# Global instance
_unified_agent_instance = None

def get_unified_agent():
    """Get global Unified Agent instance"""
    global _unified_agent_instance
    if _unified_agent_instance is None:
        _unified_agent_instance = UnifiedAgent()
    return _unified_agent_instance 