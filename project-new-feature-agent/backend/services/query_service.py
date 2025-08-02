import tempfile
import os
from werkzeug.datastructures import FileStorage
from typing import List
from core.utils import PdfConverter
from core.rag_singleton import rag  # Singleton instance
from agents.agents import agent
from agents.tasks import build_task
from crewai import Crew

converter = PdfConverter()

async def process_documents(files: List[FileStorage]):
    all_data = []
    for file in files:
        temp_dir=tempfile.gettempdir()
        temp_path=os.path.join(temp_dir,file.filename)
        file.save(temp_path)
        data = converter.convert(temp_path)
        all_data.extend(data)
        os.unlink(temp_path)
    rag.index_document(all_data)
    return {"status": "Documents processed and indexed."}

async def process_query(query: str):
    dataset = []  # Replace with actual cache/store logic
    task = build_task(query, dataset)
    crew = Crew(agents=[agent], tasks=[task])
    result = crew.kickoff()
    if hasattr(result, 'raw'):
        response_text = str(result.raw)
    elif hasattr(result, 'result'):
        response_text = str(result.result)
    else:
        response_text = str(result)
    
    return {"response": response_text}