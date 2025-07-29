import tempfile
from fastapi import UploadFile
from typing import List
from backend.core.utils import PdfConverter
from backend.core.rag_singleton import rag  # Singleton instance
from backend.agents.agents import agent
from backend.agents.tasks import build_task
from crewai import Crew

converter = PdfConverter()

async def process_documents(files: List[UploadFile]):
    all_data = []
    for file in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        data = converter.convert(tmp_path)
        all_data.extend(data)
    rag.index_document(all_data)
    return {"status": "Documents processed and indexed."}

async def process_query(query: str):
    dataset = []  # Replace with actual cache/store logic
    task = build_task(query, dataset)
    crew = Crew(agents=[agent], tasks=[task])
    result = crew.kickoff()  
    return {"response": result}