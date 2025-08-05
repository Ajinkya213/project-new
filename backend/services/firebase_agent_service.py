#!/usr/bin/env python3
"""
Firebase Agent Service - Manages agent interactions with Firebase
"""

import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from services.firebase_auth_service import require_auth
from services.local_storage_service import local_storage_service
from services.firebase_chat_service import firebase_chat_service
from services.query_service import QueryService
from services.agent_selector import agent_selector
from services.api_key_service import api_key_service
# Import agent functions with updated names
from agents.agents import get_agent, update_agent_status
from core.rag_singleton import get_rag
import json

class FirebaseAgentService:
    """Firebase-integrated agent service with user authentication and file management"""
    
    def __init__(self):
        self.query_service = QueryService()
        self.rag = get_rag()
        self.user_sessions = {}  # Track user agent sessions
    
    def process_user_query(self, user_id: str, query: str, agent_type: str = None, 
                          session_id: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user query with Firebase authentication and file context"""
        try:
            start_time = time.time()
            
            # Auto-select agent if not specified
            if not agent_type:
                selected_agent, scores = agent_selector.select_agent(query)
                agent_type = selected_agent
                print(f"[INFO] Auto-selected agent: {agent_type} for user {user_id}")
            
            # Get API keys for the agent
            api_keys = api_key_service.get_api_key_for_agent(user_id, agent_type)
            
            # Check if required keys are available
            missing_keys = self._check_missing_keys(agent_type, api_keys)
            if missing_keys:
                return {
                    "success": False,
                    "error": f"Missing required API keys: {', '.join(missing_keys)}",
                    "agent_type": agent_type,
                    "missing_keys": missing_keys,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Get user's uploaded documents for context
            user_documents = self._get_user_documents(user_id)
            
            # Build enhanced context with user's files
            enhanced_context = self._build_user_context(user_id, user_documents, context)
            
            # Process query with selected agent using user's API keys
            result = self._process_with_agent(agent_type, query, enhanced_context, api_keys)
            
            # Record the interaction
            self._record_user_interaction(user_id, agent_type, query, result, session_id)
            
            # Update agent status
            response_time = time.time() - start_time
            update_agent_status(agent_type, "online", success=True, response_time=response_time)
            
            return {
                "success": True,
                "agent_type": agent_type,
                "query": query,
                "response": result.get("response", ""),
                "sources": result.get("sources", []),
                "metadata": result.get("metadata", {}),
                "user_documents_used": len(user_documents),
                "response_time": response_time,
                "api_keys_used": list(api_keys.keys()),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[ERROR] Agent processing failed for user {user_id}: {str(e)}")
            update_agent_status(agent_type or "unknown", "online", success=False)
            return {
                "success": False,
                "error": f"Agent processing failed: {str(e)}",
                "agent_type": agent_type,
                "timestamp": datetime.now().isoformat()
            }
    
    def _check_missing_keys(self, agent_type: str, api_keys: Dict[str, str]) -> List[str]:
        """Check which required API keys are missing for an agent"""
        agent_key_requirements = {
            'multimodal': ['GEMINI_API_KEY', 'TAVILY_API_KEY'],
            'document': ['GEMINI_API_KEY'],
            'research': ['TAVILY_API_KEY'],
            'lightweight': ['GEMINI_API_KEY'],
            'chat': ['GEMINI_API_KEY']
        }
        
        required_keys = agent_key_requirements.get(agent_type, ['GEMINI_API_KEY'])
        missing_keys = []
        
        for key_name in required_keys:
            if not api_keys.get(key_name):
                missing_keys.append(key_name)
        
        return missing_keys
    
    def _get_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's uploaded documents for context"""
        try:
            documents = local_storage_service.get_user_documents(user_id)
            return documents
        except Exception as e:
            print(f"[WARNING] Could not get user documents: {str(e)}")
            return []
    
    def _build_user_context(self, user_id: str, documents: List[Dict], 
                           base_context: Dict = None) -> Dict[str, Any]:
        """Build enhanced context with user's files and chat history"""
        context = base_context or {}
        
        # Add user's documents to context
        if documents:
            context["user_documents"] = [
                {
                    "filename": doc.get("original_filename", doc.get("filename")),
                    "file_type": doc.get("file_type"),
                    "file_size": doc.get("file_size"),
                    "upload_date": doc.get("created_at"),
                    "local_url": doc.get("local_url")
                }
                for doc in documents
            ]
        
        # Add user's recent chat history
        try:
            chat_sessions = firebase_chat_service.get_chat_sessions(user_id)
            if chat_sessions:
                # Get the most recent session
                latest_session = chat_sessions[0] if chat_sessions else None
                if latest_session:
                    session_data = firebase_chat_service.get_chat_session(
                        latest_session["id"], user_id
                    )
                    if session_data and session_data.get("messages"):
                        # Get last 5 messages for context
                        recent_messages = session_data["messages"][-5:]
                        context["recent_chat"] = [
                            {
                                "sender": msg["sender"],
                                "text": msg["text"],
                                "timestamp": msg["created_at"]
                            }
                            for msg in recent_messages
                        ]
        except Exception as e:
            print(f"[WARNING] Could not get chat history: {str(e)}")
        
        # Add user info
        context["user_id"] = user_id
        context["timestamp"] = datetime.now().isoformat()
        
        return context
    
    def _process_with_agent(self, agent_type: str, query: str, context: Dict[str, Any], 
                           api_keys: Dict[str, str]) -> Dict[str, Any]:
        """Process query with the specified agent using user's API keys"""
        try:
            # Set API keys in environment for this request
            original_keys = {}
            for key_name, key_value in api_keys.items():
                original_keys[key_name] = os.getenv(key_name)
                os.environ[key_name] = key_value
            
            try:
                if agent_type == "lightweight":
                    return self._process_lightweight(query, context)
                elif agent_type == "multimodal":
                    return self._process_multimodal(query, context)
                elif agent_type == "document":
                    return self._process_document(query, context)
                elif agent_type == "research":
                    return self._process_research(query, context)
                elif agent_type == "chat":
                    return self._process_chat(query, context)
                else:
                    # Fallback to lightweight
                    return self._process_lightweight(query, context)
            finally:
                # Restore original environment variables
                for key_name, original_value in original_keys.items():
                    if original_value is not None:
                        os.environ[key_name] = original_value
                    else:
                        os.environ.pop(key_name, None)
                
        except Exception as e:
            print(f"[ERROR] Agent processing failed: {str(e)}")
            return {
                "response": f"I encountered an error while processing your request: {str(e)}",
                "sources": [],
                "metadata": {"error": str(e)}
            }
    
    def _process_lightweight(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process with lightweight agent"""
        try:
            result = self.query_service.process_query(query, "lightweight", context)
            return {
                "response": result.get("response", ""),
                "sources": result.get("sources", []),
                "metadata": result.get("metadata", {})
            }
        except Exception as e:
            return {"response": f"Lightweight processing failed: {str(e)}", "sources": [], "metadata": {}}
    
    def _process_multimodal(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process with multimodal agent (RAG + web search)"""
        try:
            # Check if user has documents
            user_docs = context.get("user_documents", [])
            
            if user_docs:
                # Use RAG for document search
                rag_result = self.rag.generate_result(query)
                return {
                    "response": rag_result.get("gemini_response", "No relevant information found in your documents."),
                    "sources": rag_result.get("metadata", []),
                    "metadata": {
                        "retrieved_pages": rag_result.get("retrieved_pages", 0),
                        "evaluation": rag_result.get("evaluation", {})
                    }
                }
            else:
                # Fallback to web search
                return self._process_research(query, context)
                
        except Exception as e:
            return {"response": f"Multimodal processing failed: {str(e)}", "sources": [], "metadata": {}}
    
    def _process_document(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process with document analysis agent"""
        try:
            user_docs = context.get("user_documents", [])
            
            if user_docs:
                # Use RAG for document analysis
                rag_result = self.rag.generate_result(query)
                return {
                    "response": rag_result.get("gemini_response", "No documents available for analysis."),
                    "sources": rag_result.get("metadata", []),
                    "metadata": {
                        "analysis_type": "document",
                        "documents_analyzed": len(user_docs),
                        "evaluation": rag_result.get("evaluation", {})
                    }
                }
            else:
                return {
                    "response": "No documents available for analysis. Please upload some documents first.",
                    "sources": [],
                    "metadata": {"analysis_type": "document", "documents_available": 0}
                }
                
        except Exception as e:
            return {"response": f"Document analysis failed: {str(e)}", "sources": [], "metadata": {}}
    
    def _process_research(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process with research agent (web search)"""
        try:
            result = self.query_service.process_query(query, "web_search", context)
            return {
                "response": result.get("response", ""),
                "sources": result.get("sources", []),
                "metadata": {
                    "research_type": "web_search",
                    "sources_count": len(result.get("sources", []))
                }
            }
        except Exception as e:
            return {"response": f"Research failed: {str(e)}", "sources": [], "metadata": {}}
    
    def _process_chat(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process with chat agent"""
        try:
            result = self.query_service.process_query(query, "lightweight", context)
            return {
                "response": result.get("response", ""),
                "sources": [],
                "metadata": {"chat_type": "conversational"}
            }
        except Exception as e:
            return {"response": f"Chat processing failed: {str(e)}", "sources": [], "metadata": {}}
    
    def _record_user_interaction(self, user_id: str, agent_type: str, query: str, 
                                result: Dict[str, Any], session_id: str = None):
        """Record user interaction in Firestore"""
        try:
            interaction_data = {
                "user_id": user_id,
                "agent_type": agent_type,
                "query": query,
                "response": result.get("response", ""),
                "success": result.get("success", True),
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                "metadata": result.get("metadata", {})
            }
            
            # Store in Firestore
            db = self.rag.db  # Get Firestore client from RAG
            db.collection("user_interactions").add(interaction_data)
            
        except Exception as e:
            print(f"[WARNING] Could not record user interaction: {str(e)}")
    
    def get_user_agent_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's agent interaction history"""
        try:
            db = self.rag.db
            interactions = db.collection("user_interactions")\
                .where("user_id", "==", user_id)\
                .order_by("timestamp", direction="DESCENDING")\
                .limit(limit)\
                .stream()
            
            return [doc.to_dict() for doc in interactions]
        except Exception as e:
            print(f"[WARNING] Could not get user history: {str(e)}")
            return []
    
    def get_agent_analytics(self, user_id: str = None) -> Dict[str, Any]:
        """Get agent usage analytics"""
        try:
            db = self.rag.db
            
            if user_id:
                # User-specific analytics
                interactions = db.collection("user_interactions")\
                    .where("user_id", "==", user_id)\
                    .stream()
            else:
                # Global analytics
                interactions = db.collection("user_interactions").stream()
            
            agent_stats = {}
            total_interactions = 0
            
            for doc in interactions:
                data = doc.to_dict()
                agent_type = data.get("agent_type", "unknown")
                
                if agent_type not in agent_stats:
                    agent_stats[agent_type] = {
                        "total": 0,
                        "successful": 0,
                        "failed": 0
                    }
                
                agent_stats[agent_type]["total"] += 1
                total_interactions += 1
                
                if data.get("success", True):
                    agent_stats[agent_type]["successful"] += 1
                else:
                    agent_stats[agent_type]["failed"] += 1
            
            # Calculate success rates
            for agent_type, stats in agent_stats.items():
                if stats["total"] > 0:
                    stats["success_rate"] = (stats["successful"] / stats["total"]) * 100
                else:
                    stats["success_rate"] = 0
            
            return {
                "total_interactions": total_interactions,
                "agent_stats": agent_stats,
                "user_id": user_id
            }
            
        except Exception as e:
            print(f"[WARNING] Could not get analytics: {str(e)}")
            return {"error": str(e)}
    
    def get_available_agents_for_user(self, user_id: str) -> Dict[str, Any]:
        """Get available agents with user-specific context and API key status"""
        try:
            user_documents = self._get_user_documents(user_id)
            key_status = api_key_service.get_user_key_status(user_id)
            
            agents = {
                "lightweight": {
                    "name": "Lightweight Assistant",
                    "description": "Fast and efficient general-purpose assistant",
                    "available": key_status.get("GEMINI_API_KEY", {}).get("user_has_key", False),
                    "required_keys": ["GEMINI_API_KEY"],
                    "recommended_for": ["general questions", "quick answers", "conversation"]
                },
                "multimodal": {
                    "name": "Multimodal Agent",
                    "description": "Analyzes your uploaded documents and web content",
                    "available": all([
                        key_status.get("GEMINI_API_KEY", {}).get("user_has_key", False),
                        key_status.get("TAVILY_API_KEY", {}).get("user_has_key", False)
                    ]),
                    "documents_available": len(user_documents),
                    "required_keys": ["GEMINI_API_KEY", "TAVILY_API_KEY"],
                    "recommended_for": ["document analysis", "file search", "content retrieval"]
                },
                "document": {
                    "name": "Document Analyst",
                    "description": "Specialized in analyzing and extracting insights from documents",
                    "available": key_status.get("GEMINI_API_KEY", {}).get("user_has_key", False) and len(user_documents) > 0,
                    "documents_available": len(user_documents),
                    "required_keys": ["GEMINI_API_KEY"],
                    "recommended_for": ["document analysis", "summarization", "insights extraction"]
                },
                "research": {
                    "name": "Research Assistant",
                    "description": "Conducts comprehensive web research",
                    "available": key_status.get("TAVILY_API_KEY", {}).get("user_has_key", False),
                    "required_keys": ["TAVILY_API_KEY"],
                    "recommended_for": ["research", "current information", "web search"]
                },
                "chat": {
                    "name": "Chat Assistant",
                    "description": "Friendly conversational assistant",
                    "available": key_status.get("GEMINI_API_KEY", {}).get("user_has_key", False),
                    "required_keys": ["GEMINI_API_KEY"],
                    "recommended_for": ["conversation", "casual chat", "general discussion"]
                }
            }
            
            return {
                "user_id": user_id,
                "agents": agents,
                "total_documents": len(user_documents),
                "key_status": key_status
            }
            
        except Exception as e:
            print(f"[WARNING] Could not get available agents: {str(e)}")
            return {"error": str(e)}

# Global agent service instance
firebase_agent_service = FirebaseAgentService() 