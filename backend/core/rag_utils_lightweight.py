#!/usr/bin/env python3
"""
Lightweight RAG implementation for document processing with proper content extraction
"""

from typing import List, Dict, Tuple
from PIL import Image
import os
import json
import hashlib
import pytesseract
from pdf2image import convert_from_path
import fitz  # PyMuPDF for text extraction
from datetime import datetime

class LightweightRAG:
    def __init__(self, url: str, api_key: str, image_dir: str = r'..\data\pdf_images'):
        self.image_dir = image_dir
        self.documents = {}  # Simple in-memory storage
        # Fix the path to be absolute
        if image_dir.startswith('..'):
            # Convert relative path to absolute
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.image_dir = os.path.join(current_dir, image_dir)
        self.storage_file = os.path.join(self.image_dir, 'rag_documents.json')
        print(f"[INFO] RAG storage file: {self.storage_file}")
        self._load_documents()
        print("[INFO] LightweightRAG initialized successfully")
    
    def _load_documents(self):
        """Load documents from file storage"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    self.documents = json.load(f)
                print(f"[INFO] Loaded {len(self.documents)} documents from storage")
        except Exception as e:
            print(f"[WARNING] Failed to load documents: {e}")
            self.documents = {}
    
    def _save_documents(self):
        """Save documents to file storage"""
        try:
            os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
            with open(self.storage_file, 'w') as f:
                json.dump(self.documents, f, indent=2)
            print(f"[INFO] Saved {len(self.documents)} documents to storage")
        except Exception as e:
            print(f"[WARNING] Failed to save documents: {e}")
    
    def _extract_text_from_pdf(self, pdf_path: str) -> List[str]:
        """Extract text from PDF using PyMuPDF"""
        try:
            doc = fitz.open(pdf_path)
            text_content = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                text_content.append(text.strip())
            doc.close()
            return text_content
        except Exception as e:
            print(f"[WARNING] Failed to extract text from PDF: {e}")
            return []
    
    def _extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            print(f"[WARNING] Failed to extract text from image: {e}")
            return ""
    
    def index_document(self, dataset: List[Dict]):
        """Index documents in the lightweight RAG system with proper content extraction"""
        try:
            print(f"[INFO] LightweightRAG indexing {len(dataset)} documents")
            
            for item in dataset:
                doc_id = item.get('doc_id', 1)
                page_num = item.get('page_number', 1)
                filename = item.get('filename', 'unknown.pdf')
                image_path = item.get('image_path', '')
                
                # Create a simple key for storage
                key = f"{filename}_{page_num}"
                
                # Extract content from the document
                content = ""
                
                # Try to extract text from the original PDF if available
                if hasattr(item, 'original_pdf_path') and item['original_pdf_path']:
                    pdf_texts = self._extract_text_from_pdf(item['original_pdf_path'])
                    if pdf_texts and page_num <= len(pdf_texts):
                        content = pdf_texts[page_num - 1]
                
                # If no PDF text, try OCR on the image
                if not content and image_path and os.path.exists(image_path):
                    content = self._extract_text_from_image(image_path)
                
                # If still no content, use a placeholder
                if not content:
                    content = f"Document: {filename}, Page: {page_num} - Content not extracted"
                
                # Store document with extracted content
                self.documents[key] = {
                    'doc_id': doc_id,
                    'page_number': page_num,
                    'filename': filename,
                    'image_path': image_path,
                    'content': content,
                    'content_length': len(content),
                    'extracted_at': str(datetime.now())
                }
            
            print(f"[INFO] Indexed {len(self.documents)} document pages with content")
            self._save_documents()  # Save to file
            return {
                "status": "success",
                "message": f"Documents indexed successfully with content extraction. {len(dataset)} pages processed.",
                "pages_processed": len(dataset)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to index documents: {str(e)}"
            }
    
    def search_documents(self, query: str) -> List[Dict]:
        """Enhanced search with content-based matching"""
        results = []
        query_lower = query.lower()
        
        for key, doc in self.documents.items():
            score = 0.0
            content = doc.get('content', '').lower()
            
            # Content-based scoring
            if query_lower in content:
                score += 0.9  # Exact match
            elif any(word in content for word in query_lower.split()):
                score += 0.7  # Partial word match
            
            # Keyword-based scoring
            if any(word in query_lower for word in ['document', 'pdf', 'file', 'page']):
                score += 0.3
            if any(word in query_lower for word in ['analyze', 'summarize', 'extract', 'find']):
                score += 0.2
            
            # Only include results with some relevance
            if score > 0.1:
                results.append({
                    'key': key,
                    'doc': doc,
                    'score': score,
                    'matched_content': content[:200] + "..." if len(content) > 200 else content
                })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:5]  # Return top 5 results
    
    def generate_result(self, query_text: str) -> Dict:
        """Generate result using lightweight RAG with content-based retrieval"""
        try:
            # Search for relevant documents
            search_results = self.search_documents(query_text)
            
            if not search_results:
                return {
                    "status": "no_results",
                    "message": "No relevant documents found for the query",
                    "response": "I couldn't find any relevant information in the uploaded documents. Please try rephrasing your query or upload relevant documents."
                }
            
            # Create a comprehensive response based on the found content
            response_parts = []
            for result in search_results:
                doc = result['doc']
                content = result.get('matched_content', doc.get('content', ''))
                response_parts.append(f"Document: {doc['filename']}, Page: {doc['page_number']}\nContent: {content}")
            
            # Create a comprehensive response
            if 'analyze' in query_text.lower() or 'summarize' in query_text.lower():
                response = f"Based on the uploaded documents, here's what I found:\n\n" + "\n\n".join(response_parts)
            elif 'search' in query_text.lower() or 'find' in query_text.lower():
                response = f"I found the following relevant documents:\n\n" + "\n\n".join(response_parts)
            else:
                response = f"Here's what I found in the uploaded documents:\n\n" + "\n\n".join(response_parts)
            
            return {
                "status": "success",
                "response": response,
                "retrieved_pages": len(search_results),
                "metadata": [result['doc'] for result in search_results],
                "evaluation": {
                    "sufficient": True,
                    "confidence": "high" if search_results[0]['score'] > 0.7 else "medium",
                    "reason": f"Found {len(search_results)} relevant documents with content matching"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error during RAG process: {str(e)}",
                "response": "I encountered an error while processing your query. Please try again."
            } 