#!/usr/bin/env python3
"""
Task definitions for agents
"""

from crewai import Task
from core.rag_singleton import rag
from .agents import multimodal_agent

def build_task(query: str, dataset: list = None):
    """Build a task for the multimodal agent"""
    def task_logic(_):
        try:
            results = rag.generate_result(query)
            if isinstance(results, dict) and results.get('status') == 'success':
                return results.get('response', f"Processed query: {query}")
            elif isinstance(results, dict) and results.get('status') == 'no_results':
                return f"fallback:{query}"
            else:
                return f"fallback:{query}"
        except Exception as e:
            print(f"Error in task_logic: {e}")
            return f"fallback:{query}"

    return Task(
        description=f"Retrieve info about: {query}",
        expected_output="A JSON response answering the query.",
        agent=multimodal_agent,
        steps=[task_logic]
    )

def build_chat_task(query: str):
    """Build a task for the chat agent"""
    def task_logic(_):
        return f"Chat response to: {query}"

    return Task(
        description=f"Respond to chat message: {query}",
        expected_output="A friendly and helpful chat response.",
        agent=None,  # Will be set when used
        steps=[task_logic]
    )

def build_document_task(query: str):
    """Build a task for the document agent"""
    def task_logic(_):
        try:
            results = rag.generate_result(query)
            if isinstance(results, dict) and results.get('status') == 'success':
                return results.get('response', f"Document analysis: {query}")
            else:
                return f"Document analysis not available for: {query}"
        except Exception as e:
            return f"Document analysis error: {e}"

    return Task(
        description=f"Analyze documents for: {query}",
        expected_output="Document analysis and insights.",
        agent=None,  # Will be set when used
        steps=[task_logic]
    )

def build_research_task(query: str):
    """Build a task for the research agent"""
    def task_logic(_):
        return f"Research response to: {query}"

    return Task(
        description=f"Research topic: {query}",
        expected_output="Comprehensive research findings.",
        agent=None,  # Will be set when used
        steps=[task_logic]
    )

def build_lightweight_task(query: str):
    """Build a task for the lightweight agent"""
    def task_logic(_):
        return f"Quick response to: {query}"

    return Task(
        description=f"Quick response to: {query}",
        expected_output="A simple and direct response.",
        agent=None,  # Will be set when used
        steps=[task_logic]
    ) 