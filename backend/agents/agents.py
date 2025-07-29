from crewai import Agent
from backend.agents.tools import search_web
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
agent = Agent(
    role="Multimodal Retrieval Agent",
    goal="Answer queries using local data or fallback to web",
    backstory="You are a research assistant trained in visual document understanding. "
              "Your job is to retrieve relevant pages from internal documents and fall back to the internet if needed.",
    tools=[search_web],
    verbose=True,
    llm='gemini/gemini-2.5-flash'
)