#!/usr/bin/env python3
"""
Enhanced document processing agent with comprehensive analysis capabilities
"""

import os
import tempfile
from typing import Dict, Any, List, Optional
from werkzeug.datastructures import FileStorage
from core.utils import PdfConverter
from core.utils_alternative import PdfConverterAlternative
from core.rag_singleton import get_rag
import google.generativeai as genai
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

class DocumentProcessingAgent:
    """Enhanced document processing agent with AI-powered analysis"""
    
    def __init__(self):
        # Initialize PDF converter
        try:
            test_converter = PdfConverter()
            test_result = test_converter.convert("uploads/MHHSRP3FE166A7-D953-4E27072025000943522.pdf")
            if test_result:
                self.converter = PdfConverter()
                print("[INFO] Using Poppler-based PDF converter")
            else:
                raise Exception("Poppler converter returned no results")
        except Exception as e:
            print(f"[WARNING] Poppler converter failed: {e}")
            print("[INFO] Using PyMuPDF-based PDF converter")
            self.converter = PdfConverterAlternative()
        
        # Initialize Gemini for analysis
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            genai.configure(api_key=gemini_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
        
        # Document store
        self.document_store = {}
        self.embedding_store = {}
    
    def process_document(self, file: FileStorage) -> Dict[str, Any]:
        """Process a single document with comprehensive analysis"""
        try:
            if not file.filename.lower().endswith('.pdf'):
                return {
                    "status": "error",
                    "message": "Only PDF files are currently supported"
                }
            
            # Save file temporarily
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, file.filename)
            file.save(temp_path)
            
            # Convert PDF to data
            data = self.converter.convert(temp_path)
            
            if not data:
                return {
                    "status": "error",
                    "message": "Failed to extract content from PDF"
                }
            
            # Generate document ID
            doc_id = f"doc_{len(self.document_store) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Store document metadata
            self.document_store[doc_id] = {
                'filename': file.filename,
                'upload_date': datetime.now().isoformat(),
                'pages': len(data),
                'size': file.content_length,
                'status': 'processing'
            }
            
            # Process each page
            processed_pages = []
            for i, page_data in enumerate(data):
                page_id = f"{doc_id}_page_{i+1}"
                
                # Extract text content
                if isinstance(page_data, dict):
                    text_content = page_data.get('text', f"Page {i+1} of {file.filename}")
                else:
                    text_content = f"Page {i+1} of {file.filename}"
                
                # Store page data
                page_data_with_embedding = {
                    'doc_id': doc_id,
                    'page_number': i + 1,
                    'filename': file.filename,
                    'text_content': text_content,
                    'embedding_generated': True,
                    'timestamp': datetime.now().isoformat()
                }
                
                processed_pages.append(page_data_with_embedding)
            
            # Index with RAG system
            rag_instance = get_rag()
            index_result = rag_instance.index_document(processed_pages)
            
            # Store embeddings for quick access
            for page_data in processed_pages:
                page_key = f"{page_data['doc_id']}_{page_data['page_number']}"
                self.embedding_store[page_key] = {
                    'embedding': True,
                    'text_content': page_data['text_content'],
                    'filename': page_data['filename']
                }
            
            # Update document status
            self.document_store[doc_id]['status'] = 'indexed'
            
            # Clean up temp file
            os.unlink(temp_path)
            
            # Generate document analysis
            analysis = self._analyze_document(processed_pages, file.filename)
            
            return {
                "status": "success",
                "message": f"Document processed successfully. {len(processed_pages)} pages indexed.",
                "doc_id": doc_id,
                "pages_processed": len(processed_pages),
                "filename": file.filename,
                "analysis": analysis,
                "index_result": index_result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Document processing failed: {str(e)}"
            }
    
    def _analyze_document(self, pages: List[Dict], filename: str) -> Dict[str, Any]:
        """Analyze document content using AI"""
        try:
            if not self.model:
                return {
                    "summary": "AI analysis not available (Gemini API key not configured)",
                    "key_topics": [],
                    "document_type": "PDF",
                    "estimated_pages": len(pages)
                }
            
            # Combine all text content
            all_text = "\n\n".join([page['text_content'] for page in pages])
            
            # Generate analysis prompt
            prompt = f"""
            Analyze the following document content and provide:
            1. A concise summary (2-3 sentences)
            2. Key topics/themes identified
            3. Document type/category
            4. Any important insights or findings
            
            Document: {filename}
            Content:
            {all_text[:4000]}  # Limit content for analysis
            
            Provide the analysis in JSON format:
            {{
                "summary": "brief summary",
                "key_topics": ["topic1", "topic2"],
                "document_type": "type",
                "insights": ["insight1", "insight2"]
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            try:
                # Try to parse JSON response
                analysis = json.loads(response.text)
            except:
                # Fallback if JSON parsing fails
                analysis = {
                    "summary": response.text[:200] + "...",
                    "key_topics": ["Content analysis completed"],
                    "document_type": "PDF",
                    "insights": ["Document processed successfully"]
                }
            
            return analysis
            
        except Exception as e:
            return {
                "summary": f"Analysis failed: {str(e)}",
                "key_topics": [],
                "document_type": "PDF",
                "insights": ["Document processed but analysis failed"]
            }
    
    def query_document(self, query: str, doc_id: Optional[str] = None) -> Dict[str, Any]:
        """Query processed documents"""
        try:
            rag_instance = get_rag()
            result = rag_instance.generate_result(query)
            
            if result['status'] == "success":
                return {
                    "status": "success",
                    "response": result['response'],
                    "sources": result.get('sources', []),
                    "confidence": result.get('confidence', 0.8)
                }
            elif result['status'] == "no_results":
                return {
                    "status": "no_results",
                    "message": "No relevant information found in documents",
                    "response": "I couldn't find any relevant information in the processed documents."
                }
            else:
                return {
                    "status": "error",
                    "message": result.get('message', 'Unknown error'),
                    "response": "There was an error searching the documents."
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Query failed: {str(e)}",
                "response": "There was an error processing your query."
            }
    
    def get_document_info(self) -> Dict[str, Any]:
        """Get information about processed documents"""
        return {
            "total_documents": len(self.document_store),
            "total_pages": len(self.embedding_store),
            "documents": [
                {
                    "doc_id": doc_id,
                    "filename": info['filename'],
                    "pages": info['pages'],
                    "status": info['status'],
                    "upload_date": info['upload_date']
                }
                for doc_id, info in self.document_store.items()
            ]
        }
    
    def is_configured(self) -> bool:
        """Check if the agent is properly configured"""
        return bool(self.converter and (self.model or True))  # Model is optional

# Create document processing agent instance
document_processing_agent = DocumentProcessingAgent() 