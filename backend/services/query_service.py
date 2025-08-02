#!/usr/bin/env python3
"""
Query Service for handling agent queries
"""

from typing import Dict, Any, Optional
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from agents import get_agent_by_type, get_agent_status, update_agent_status, agents
from agents.tasks import build_task, build_chat_task, build_document_task, build_research_task, build_lightweight_task
from .lightweight_agent import lightweight_agent
from .agent_selector import agent_selector
from crewai import Crew

load_dotenv()

class QueryService:
    """Service for handling agent queries"""
    
    def __init__(self):
        self.agents = {}
        self._agent_cache = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all agents"""
        try:
            # Initialize lightweight agent
            self.agents = {
                "lightweight": lightweight_agent
            }
            update_agent_status("lightweight", "online")
            print("[INFO] Lightweight agent initialized successfully")
            
            # Initialize CrewAI agents
            try:
                for agent_type, agent in agents.items():
                    if agent_type != "lightweight":
                        self._agent_cache[agent_type] = agent
                        update_agent_status(agent_type, "online")
                        print(f"[INFO] {agent_type} agent initialized successfully")
            except AttributeError:
                # If agents is not a dict, try to get agents individually
                agent_types = ["multimodal", "chat", "document", "research"]
                for agent_type in agent_types:
                    try:
                        agent = get_agent_by_type(agent_type)
                        if agent:
                            self._agent_cache[agent_type] = agent
                            update_agent_status(agent_type, "online")
                            print(f"[INFO] {agent_type} agent initialized successfully")
                    except Exception as e:
                        print(f"[WARNING] Failed to initialize {agent_type} agent: {e}")
            
        except Exception as e:
            print(f"Warning: Could not initialize agents: {e}")
            # Fallback: ensure lightweight agent is available
            try:
                self.agents = {
                    "lightweight": lightweight_agent
                }
                update_agent_status("lightweight", "online")
                print("[INFO] Lightweight agent initialized as fallback")
            except Exception as fallback_error:
                print(f"Critical: Could not initialize lightweight agent: {fallback_error}")
                self.agents = {}
    
    def _get_agent(self, agent_type: str):
        """Get agent from cache or agents dict"""
        # Check cache first
        if agent_type in self._agent_cache:
            return self._agent_cache[agent_type]
        
        # For lightweight agent, check the agents dict
        if agent_type == "lightweight":
            return self.agents.get("lightweight")
        
        # Try to get from agents module
        agent = get_agent_by_type(agent_type)
        if agent:
            self._agent_cache[agent_type] = agent
        return agent
    
    def _build_task_for_agent(self, query: str, agent_type: str):
        """Build appropriate task for agent type"""
        if agent_type == "multimodal":
            return build_task(query)
        elif agent_type == "chat":
            task = build_chat_task(query)
            task.agent = self._get_agent(agent_type)
            return task
        elif agent_type == "document":
            task = build_document_task(query)
            task.agent = self._get_agent(agent_type)
            return task
        elif agent_type == "research":
            task = build_research_task(query)
            task.agent = self._get_agent(agent_type)
            return task
        elif agent_type == "lightweight":
            task = build_lightweight_task(query)
            task.agent = self._get_agent(agent_type)
            return task
        else:
            # Default to multimodal task
            return build_task(query)
    
    def auto_select_agent(self, query: str) -> Dict[str, Any]:
        """Automatically select the best agent for a query"""
        reasoning = agent_selector.get_agent_reasoning(query)
        selected_agent = reasoning["selected_agent"]
        
        return {
            "selected_agent": selected_agent,
            "reasoning": reasoning,
            "confidence": reasoning["confidence"]
        }
    
    def process_query(self, query: str, agent_type: str = "lightweight", context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a query with the specified agent"""
        start_time = time.time()
        
        try:
            # Update agent status to processing
            update_agent_status(agent_type, "processing")
            
            agent = self._get_agent(agent_type)
            if not agent:
                update_agent_status(agent_type, "offline", False, time.time() - start_time)
                return {
                    "success": False,
                    "error": f"Agent type '{agent_type}' not found or failed to load. Please try the lightweight agent.",
                    "response": None,
                    "agent_type": agent_type
                }
            
            if agent_type == "lightweight":
                # Use lightweight agent directly
                response = agent.process_query(query)
                response_time = time.time() - start_time
                update_agent_status(agent_type, "online", True, response_time)
                
                return {
                    "success": True,
                    "response": response,
                    "agent_type": agent_type,
                    "query": query,
                    "response_time": round(response_time, 2)
                }
            else:
                # Use CrewAI for other agents
                task = self._build_task_for_agent(query, agent_type)
                
                crew = Crew(
                    agents=[agent],
                    tasks=[task],
                    verbose=True
                )
                
                result = crew.kickoff()
                response_time = time.time() - start_time
                update_agent_status(agent_type, "online", True, response_time)
                
                # Extract response from result
                if hasattr(result, 'raw'):
                    response_text = str(result.raw)
                elif hasattr(result, 'result'):
                    response_text = str(result.result)
                else:
                    response_text = str(result)
                
                return {
                    "success": True,
                    "response": response_text,
                    "agent_type": agent_type,
                    "query": query,
                    "response_time": round(response_time, 2)
                }
                
        except Exception as e:
            response_time = time.time() - start_time
            update_agent_status(agent_type, "offline", False, response_time)
            
            return {
                "success": False,
                "error": str(e),
                "response": None,
                "agent_type": agent_type,
                "response_time": round(response_time, 2)
            }
    
    def get_available_agents(self) -> Dict[str, str]:
        """Get list of available agents"""
        return {
            "multimodal": "Multimodal Retrieval Agent - Handles documents and web search",
            "chat": "Chat Assistant - General conversation and help",
            "document": "Document Analyst - Analyzes and extracts insights from documents",
            "research": "Research Assistant - Conducts comprehensive research",
            "lightweight": "Lightweight Assistant - Quick and simple responses"
        }
    
    def get_agent_status(self, agent_type: str = None) -> Dict[str, Any]:
        """Get agent status and statistics"""
        return get_agent_status(agent_type)
    
    def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        try:
            # Get all available agents
            all_agents = ["multimodal", "chat", "document", "research", "lightweight"]
            agent_statuses = get_agent_status()
            
            # Check overall health
            online_agents = sum(1 for status in agent_statuses.values() if status['status'] == 'online')
            total_agents = len(agent_statuses)
            
            overall_status = "healthy" if online_agents > 0 else "degraded"
            
            return {
                "status": overall_status,
                "available_agents": all_agents,
                "total_agents": total_agents,
                "online_agents": online_agents,
                "agent_statuses": agent_statuses,
                "message": f"Query service is {overall_status}"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "message": "Query service has issues"
            }

# Create service instance
query_service = QueryService() 