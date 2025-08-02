#!/usr/bin/env python3
"""
Intelligent Agent Selection Service
Automatically selects the best agent based on query content
"""

import re
from typing import Dict, List, Tuple

class AgentSelector:
    """Intelligent agent selection based on query analysis"""
    
    # Agent capabilities and keywords
    AGENT_KEYWORDS = {
        "multimodal": {
            "keywords": [
                "document", "file", "pdf", "image", "picture", "photo", "scan",
                "upload", "uploaded", "stored", "saved", "retrieve", "find in",
                "search document", "look up", "reference", "cite", "source"
            ],
            "patterns": [
                r"document.*",
                r"file.*",
                r"pdf.*",
                r"image.*",
                r"picture.*",
                r"photo.*",
                r"scan.*",
                r"upload.*",
                r"stored.*",
                r"saved.*",
                r"retrieve.*",
                r"find.*document",
                r"search.*document",
                r"look.*up",
                r"reference.*",
                r"cite.*",
                r"source.*"
            ]
        },
        "research": {
            "keywords": [
                "research", "study", "investigate", "explore", "analyze",
                "current", "latest", "recent", "news", "trend", "development",
                "what is", "how does", "why", "when", "where", "who",
                "explain", "describe", "tell me about", "find information",
                "search for", "look up", "investigate", "explore"
            ],
            "patterns": [
                r"research.*",
                r"study.*",
                r"investigate.*",
                r"explore.*",
                r"analyze.*",
                r"current.*",
                r"latest.*",
                r"recent.*",
                r"news.*",
                r"trend.*",
                r"development.*",
                r"what is.*",
                r"how does.*",
                r"why.*",
                r"when.*",
                r"where.*",
                r"who.*",
                r"explain.*",
                r"describe.*",
                r"tell me about.*",
                r"find information.*",
                r"search for.*",
                r"look up.*",
                r"investigate.*",
                r"explore.*"
            ]
        },
        "document": {
            "keywords": [
                "analyze", "extract", "summarize", "summary", "key points",
                "main points", "important", "highlight", "insights", "findings",
                "conclusion", "recommendation", "suggestion", "review",
                "examine", "study", "understand", "comprehend", "interpret"
            ],
            "patterns": [
                r"analyze.*",
                r"extract.*",
                r"summarize.*",
                r"summary.*",
                r"key points.*",
                r"main points.*",
                r"important.*",
                r"highlight.*",
                r"insights.*",
                r"findings.*",
                r"conclusion.*",
                r"recommendation.*",
                r"suggestion.*",
                r"review.*",
                r"examine.*",
                r"study.*",
                r"understand.*",
                r"comprehend.*",
                r"interpret.*"
            ]
        },
        "chat": {
            "keywords": [
                "hello", "hi", "hey", "how are you", "good morning", "good afternoon",
                "good evening", "thanks", "thank you", "please", "help", "assist",
                "conversation", "chat", "talk", "discuss", "opinion", "think",
                "feel", "emotion", "personal", "casual", "friendly", "informal"
            ],
            "patterns": [
                r"hello.*",
                r"hi.*",
                r"hey.*",
                r"how are you.*",
                r"good morning.*",
                r"good afternoon.*",
                r"good evening.*",
                r"thanks.*",
                r"thank you.*",
                r"please.*",
                r"help.*",
                r"assist.*",
                r"conversation.*",
                r"chat.*",
                r"talk.*",
                r"discuss.*",
                r"opinion.*",
                r"think.*",
                r"feel.*",
                r"emotion.*",
                r"personal.*",
                r"casual.*",
                r"friendly.*",
                r"informal.*"
            ]
        }
    }
    
    @staticmethod
    def analyze_query(query: str) -> Dict[str, float]:
        """Analyze query and return agent scores"""
        query_lower = query.lower().strip()
        scores = {
            "multimodal": 0.0,
            "research": 0.0,
            "document": 0.0,
            "chat": 0.0,
            "lightweight": 0.0  # Default fallback
        }
        
        # Check for keyword matches
        for agent, data in AgentSelector.AGENT_KEYWORDS.items():
            # Check exact keyword matches
            for keyword in data["keywords"]:
                if keyword in query_lower:
                    scores[agent] += 2.0
            
            # Check pattern matches
            for pattern in data["patterns"]:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    scores[agent] += 1.5
        
        # Special rules for better accuracy
        if len(query_lower.split()) <= 3:
            # Short queries are likely chat
            scores["chat"] += 1.0
        
        if any(word in query_lower for word in ["document", "file", "pdf", "upload"]):
            # Document-related queries
            scores["multimodal"] += 3.0
            scores["document"] += 2.0
        
        if any(word in query_lower for word in ["research", "study", "investigate", "current", "latest"]):
            # Research-related queries
            scores["research"] += 3.0
        
        if any(word in query_lower for word in ["analyze", "summarize", "extract", "insights"]):
            # Analysis-related queries
            scores["document"] += 3.0
        
        # Normalize scores
        max_score = max(scores.values())
        if max_score > 0:
            for agent in scores:
                scores[agent] = scores[agent] / max_score
        
        return scores
    
    @staticmethod
    def select_agent(query: str) -> Tuple[str, Dict[str, float]]:
        """Select the best agent for a query"""
        scores = AgentSelector.analyze_query(query)
        
        # Find the agent with the highest score
        best_agent = max(scores.items(), key=lambda x: x[1])
        
        # If no clear winner, default to lightweight
        if best_agent[1] < 0.3:
            return "lightweight", scores
        
        return best_agent[0], scores
    
    @staticmethod
    def get_agent_reasoning(query: str) -> Dict[str, any]:
        """Get detailed reasoning for agent selection"""
        selected_agent, scores = AgentSelector.select_agent(query)
        
        # Find the top 3 agents
        sorted_agents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        reasoning = {
            "selected_agent": selected_agent,
            "confidence": scores[selected_agent],
            "all_scores": scores,
            "top_agents": sorted_agents[:3],
            "query": query
        }
        
        return reasoning

# Create a singleton instance
agent_selector = AgentSelector() 