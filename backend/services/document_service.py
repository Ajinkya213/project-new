import tempfile
import os
from werkzeug.datastructures import FileStorage
from typing import List
from core.utils import PdfConverter
from core.rag_singleton import rag
import asyncio

converter = PdfConverter()

class DocumentService:
    """Service for processing and indexing documents"""
    
    def __init__(self):
        self.converter = converter
    
    def process_documents(self, files: List[FileStorage]):
        """Process uploaded PDF documents"""
        try:
            all_data = []
            for file in files:
                if file.filename.lower().endswith('.pdf'):
                    # Save file temporarily
                    temp_dir = tempfile.gettempdir()
                    temp_path = os.path.join(temp_dir, file.filename)
                    file.save(temp_path)
                    
                    # Convert PDF to images
                    data = self.converter.convert(temp_path)
                    all_data.extend(data)
                    
                    # Clean up temp file
                    os.unlink(temp_path)
                    
                    print(f"[INFO] Processed {file.filename}: {len(data)} pages")
                else:
                    print(f"[WARNING] Skipped {file.filename}: not a PDF file")
            
            if all_data:
                # Index documents in RAG system
                try:
                    rag.index_document(all_data)
                    return {
                        "status": "success",
                        "message": f"Documents processed and indexed successfully. {len(all_data)} pages processed.",
                        "pages_processed": len(all_data)
                    }
                except Exception as e:
                    return {
                        "status": "error",
                        "message": f"Failed to index documents: {str(e)}",
                        "pages_processed": len(all_data)
                    }
            else:
                return {
                    "status": "error",
                    "message": "No valid PDF documents found to process."
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Document processing failed: {str(e)}"
            }
    
    def get_document_info(self):
        """Get information about indexed documents"""
        try:
            # This would normally query the RAG system for document info
            return {
                "status": "success",
                "documents_indexed": "Available",
                "rag_system": "Active"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get document info: {str(e)}"
            }
    
    async def process_documents_async(self, files: List[FileStorage]):
        """Async version of document processing from the feature folder"""
        all_data = []
        for file in files:
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, file.filename)
            file.save(temp_path)
            data = self.converter.convert(temp_path)
            all_data.extend(data)
            os.unlink(temp_path)
        
        try:
            rag.index_document(all_data)
            return {"status": "Documents processed and indexed."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def process_query_async(self, query: str):
        """Async version of query processing from the feature folder"""
        try:
            from agents.agents import multimodal_agent
            from agents.tasks import build_task
            from crewai import Crew
            
            dataset = []  # Replace with actual cache/store logic
            task = build_task(query, dataset)
            crew = Crew(agents=[multimodal_agent], tasks=[task])
            result = crew.kickoff()
            
            if hasattr(result, 'raw'):
                response_text = str(result.raw)
            elif hasattr(result, 'result'):
                response_text = str(result.result)
            else:
                response_text = str(result)
            
            return {"response": response_text}
        except Exception as e:
            return {"response": f"Error processing query: {str(e)}"}

# Create document service instance
document_service = DocumentService() 