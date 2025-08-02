#!/usr/bin/env python3
"""
Agent definitions for the chat application
"""

import os
import google.generativeai as genai
from datetime import datetime
from crewai import Agent
from .tools import search_web, retrieve_from_document

# Configure Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Agent Status Tracking
class AgentStatus:
    """Track agent status and performance"""
    
    def __init__(self):
        self.status = "offline"
        self.last_activity = None
        self.total_queries = 0
        self.successful_queries = 0
        self.failed_queries = 0
        self.average_response_time = 0
        self.response_times = []
    
    def update_status(self, status: str):
        """Update agent status"""
        self.status = status
    
    def record_query(self, success: bool, response_time: float):
        """Record query performance"""
        self.total_queries += 1
        if success:
            self.successful_queries += 1
        else:
            self.failed_queries += 1
        
        self.response_times.append(response_time)
        if len(self.response_times) > 100:  # Keep last 100 times
            self.response_times.pop(0)
        
        self.average_response_time = sum(self.response_times) / len(self.response_times)
        self.last_activity = datetime.now()
    
    def get_stats(self):
        """Get agent statistics"""
        success_rate = (self.successful_queries / self.total_queries * 100) if self.total_queries > 0 else 0
        return {
            "status": self.status,
            "total_queries": self.total_queries,
            "successful_queries": self.successful_queries,
            "failed_queries": self.failed_queries,
            "success_rate": round(success_rate, 2),
            "average_response_time": round(self.average_response_time, 2),
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }

# Initialize agent status trackers
agent_statuses = {
    "multimodal": AgentStatus(),
    "chat": AgentStatus(),
    "document": AgentStatus(),
    "research": AgentStatus(),
    "lightweight": AgentStatus()
}

# Create the main multimodal agent (from feature folder)
multimodal_agent = Agent(
    role="Multimodal Retrieval Agent",
    goal="Answer queries using local data or fallback to web",
    backstory="You are a research assistant trained in visual document understanding. "
              "Your job is to retrieve relevant pages from internal documents (including the document name and the page number for the document) and fall back to the internet if needed.",
    tools=[search_web, retrieve_from_document],
    verbose=True,
    llm='gemini/gemini-2.5-flash',
    max_iter=3  # Limit iterations to avoid rate limits
)

# Create chat agent
chat_agent = Agent(
    role="Chat Assistant",
    goal="Provide helpful and engaging conversation",
    backstory="You are a friendly AI assistant that helps users with general questions and conversation. "
              "You provide clear, helpful responses and engage in natural conversation.",
    verbose=True,
    llm='gemini/gemini-2.5-flash',
    max_iter=2  # Limit iterations to avoid rate limits
)

# Create document analysis agent
document_agent = Agent(
    role="Document Analyst",
    goal="Analyze and extract insights from documents",
    backstory="You are an expert at analyzing documents and extracting key information, insights, and summaries. "
              "You can understand complex documents and provide clear analysis.",
    tools=[retrieve_from_document],
    verbose=True,
    llm='gemini/gemini-2.5-flash',
    max_iter=2  # Limit iterations to avoid rate limits
)

# Create research agent
research_agent = Agent(
    role="Research Assistant",
    goal="Conduct comprehensive research on topics",
    backstory="You are a research assistant that can search the web and analyze information to provide comprehensive answers. "
              "You gather information from multiple sources and synthesize findings.",
    tools=[search_web],
    verbose=True,
    llm='gemini/gemini-2.5-flash',
    max_iter=2  # Limit iterations to avoid rate limits
)

# Create lightweight agent (simple, fast responses)
lightweight_agent = Agent(
    role="Lightweight Assistant",
    goal="Provide quick and simple responses",
    backstory="You are a simple AI assistant that provides direct and helpful responses to basic queries. "
              "You focus on speed and clarity over complexity.",
    verbose=True,
    llm='gemini/gemini-2.5-flash',
    max_iter=1  # Limit iterations to avoid rate limits
)

# Agent mapping
agents = {
    "multimodal": multimodal_agent,
    "chat": chat_agent,
    "document": document_agent,
    "research": research_agent,
    "lightweight": lightweight_agent
}

def get_agent_by_type(agent_type: str):
    """Get agent by type"""
    return agents.get(agent_type)

def get_agent_status(agent_type: str = None):
    """Get agent status"""
    if agent_type:
        return agent_statuses.get(agent_type, AgentStatus()).get_stats()
    else:
        return {agent_type: status.get_stats() for agent_type, status in agent_statuses.items()}

def update_agent_status(agent_type: str, status: str, success: bool = None, response_time: float = None):
    """Update agent status and performance"""
    if agent_type in agent_statuses:
        agent_status = agent_statuses[agent_type]
        agent_status.update_status(status)
        if success is not None and response_time is not None:
            agent_status.record_query(success, response_time)

# Alias for compatibility with feature folder
agent = multimodal_agent 