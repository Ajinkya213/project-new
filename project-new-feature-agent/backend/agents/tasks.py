from crewai import Task
from backend.core.rag_singleton import rag  # Singleton import
from backend.agents.agents import agent

def build_task(query: str, dataset: list):
    def task_logic(_):
        results = rag.generate_result(query, dataset)
        if "No relevant information found" in results:
            return f"fallback:{query}"
        return results

    return Task(
        description=f"Retrieve info about: {query}",
        expected_output="A JSON response answering the query.",
        agent=agent,
        steps=[task_logic]
    )