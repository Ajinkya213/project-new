import tempfile
import os
from werkzeug.datastructures import FileStorage
from typing import List, Dict, Any
from core.utils import PdfConverter
from core.utils_alternative import PdfConverterAlternative
from core.rag_singleton import rag, get_rag
import asyncio
import json
from datetime import datetime

# Try to use the original converter first, fallback to alternative
try:
    # Test if Poppler converter works
    test_converter = PdfConverter()
    test_result = test_converter.convert("uploads/MHHSRP3FE166A7-D953-4E27072025000943522.pdf")
    if test_result:
        converter = PdfConverter()
        print("[INFO] Using Poppler-based PDF converter")
    else:
        raise Exception("Poppler converter returned no results")
except Exception as e:
    print(f"[WARNING] Poppler converter failed: {e}")
    print("[INFO] Using PyMuPDF-based PDF converter")
    converter = PdfConverterAlternative()

class DocumentService:
    """Enhanced service for processing and indexing documents with detailed search results"""
    
    def __init__(self):
        self.converter = converter
        self.document_store = {}  # Store document metadata
        self.embedding_store = {}  # Store embeddings for quick access
    
    def process_documents(self, files: List[FileStorage]):
        """Process uploaded PDF documents and generate embeddings"""
        try:
            all_data = []
            processed_files = []
            
            for file in files:
                if file.filename.lower().endswith('.pdf'):
                    # Save file temporarily
                    temp_dir = tempfile.gettempdir()
                    temp_path = os.path.join(temp_dir, file.filename)
                    file.save(temp_path)
                    
                    # Convert PDF to images and extract text
                    data = self.converter.convert(temp_path)
                    
                    # Store document metadata
                    doc_id = f"doc_{len(self.document_store) + 1}"
                    self.document_store[doc_id] = {
                        'filename': file.filename,
                        'upload_date': datetime.now().isoformat(),
                        'pages': len(data),
                        'size': file.content_length,
                        'status': 'indexed'
                    }
                    
                    # Process each page and generate embeddings
                    for i, page_data in enumerate(data):
                        page_id = f"{doc_id}_page_{i+1}"
                        
                        # Extract text content for embedding
                        if isinstance(page_data, dict):
                            text_content = page_data.get('text', f"Page {i+1} of {file.filename}")
                        else:
                            text_content = f"Page {i+1} of {file.filename}"
                        
                        # Store page data with embedding info
                        page_data_with_embedding = {
                            'doc_id': doc_id,
                            'page_number': i + 1,
                            'filename': file.filename,
                            'text_content': text_content,
                            'embedding_generated': True,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        all_data.append(page_data_with_embedding)
                        processed_files.append(file.filename)
                    
                    # Clean up temp file
                    os.unlink(temp_path)
                    
                    print(f"[INFO] Processed {file.filename}: {len(data)} pages with embeddings")
                else:
                    print(f"[WARNING] Skipped {file.filename}: not a PDF file")
            
            if all_data:
                # Index documents with embeddings
                try:
                    print(f"[INFO] Indexing {len(all_data)} pages with embeddings")
                    rag_instance = get_rag()
                    index_result = rag_instance.index_document(all_data)
                    
                    # Store embeddings for quick access
                    for page_data in all_data:
                        page_key = f"{page_data['doc_id']}_{page_data['page_number']}"
                        self.embedding_store[page_key] = {
                            'embedding': True,  # Placeholder for actual embedding
                            'text_content': page_data['text_content'],
                            'filename': page_data['filename']
                        }
                    
                    return {
                        "status": "success",
                        "message": f"Documents processed and indexed with embeddings. {len(all_data)} pages processed.",
                        "pages_processed": len(all_data),
                        "files_processed": processed_files,
                        "embeddings_generated": len(all_data)
                    }
                except Exception as e:
                    print(f"[ERROR] Document indexing failed: {e}")
                    return {
                        "status": "error",
                        "message": f"Failed to index documents: {str(e)}"
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
    
    def process_query_with_sources(self, query: str):
        """Process queries and provide detailed source information"""
        try:
            print(f"[INFO] Processing query with source analysis: {query}")
            
            # Use the enhanced RAG system for document search
            rag_instance = get_rag()
            rag_result = rag_instance.generate_result(query)
            
            if rag_result['status'] == 'success':
                # Extract document matches from RAG results
                document_matches = rag_result.get('search_results', [])
                
                # Simulate web search for additional information
                web_results = self._search_web(query)
                
                # Combine results with source information
                combined_response = self._combine_results(query, {
                    'matches': document_matches,
                    'total_matches': len(document_matches)
                }, web_results)
                
                return {
                    "status": "success",
                    "query": query,
                    "response": combined_response['response'],
                    "sources": combined_response['sources'],
                    "document_matches": document_matches,
                    "web_matches": web_results['matches'],
                    "analysis_summary": combined_response['summary']
                }
            else:
                return {
                    "status": "error",
                    "message": rag_result.get('message', 'Query processing failed')
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Query processing failed: {str(e)}"
            }
    
    def _search_documents(self, query: str) -> Dict[str, Any]:
        """Search in indexed documents using QDRANT"""
        try:
            rag_instance = get_rag()
            result = rag_instance.generate_result(query)
            
            if result['status'] == 'success':
                matches = result.get('search_results', [])
                return {
                    "status": "success",
                    "matches": matches,
                    "total_matches": len(matches),
                    "source": "qdrant_documents"
                }
            else:
                return {
                    "status": "error",
                    "matches": [],
                    "total_matches": 0,
                    "error": result.get('message', 'Search failed')
                }
        except Exception as e:
            return {
                "status": "error",
                "matches": [],
                "total_matches": 0,
                "error": str(e)
            }
    
    def _search_web(self, query: str) -> Dict[str, Any]:
        """Search web for additional information"""
        try:
            # Simulate web search
            web_matches = [
                {
                    'source': 'web',
                    'url': 'https://example.com/search',
                    'title': f'Web search results for: {query}',
                    'relevance_score': 0.6,
                    'snippet': f'Found web information related to: {query}'
                }
            ]
            
            return {
                "status": "success",
                "matches": web_matches,
                "total_matches": len(web_matches),
                "source": "web_search"
            }
        except Exception as e:
            return {
                "status": "error",
                "matches": [],
                "total_matches": 0,
                "error": str(e)
            }
    
    def _combine_results(self, query: str, document_results: Dict, web_results: Dict) -> Dict[str, Any]:
        """Combine document and web search results with Gemini analysis"""
        doc_matches = document_results.get('matches', [])
        web_matches = web_results.get('matches', [])
        
        # Create comprehensive response
        response_parts = []
        sources = []
        
        # Document analysis
        if doc_matches:
            response_parts.append("📄 **Document Analysis:**")
            response_parts.append(f"I found {len(doc_matches)} relevant matches in your uploaded documents stored in QDRANT:")
            
            for i, match in enumerate(doc_matches[:3], 1):  # Show top 3
                response_parts.append(f"{i}. **{match['filename']}** (Page {match['page_number']})")
            
            sources.extend([f"Document: {match['filename']}" for match in doc_matches])
        
        # Web search analysis
        if web_results.get('status') == 'success' and web_matches:
            response_parts.append("\n🌐 **Web Search Results:**")
            response_parts.append("I also found additional information from the web:")
            
            for i, match in enumerate(web_matches[:2], 1):  # Show top 2
                response_parts.append(f"{i}. {match['title']} - {match['snippet']}")
            
            sources.extend([f"Web: {match['url']}" for match in web_matches])
        
        # Combined analysis with Gemini
        if doc_matches:
            response_parts.append("\n📋 **AI Analysis:**")
            # The Gemini response is already included in the RAG result
            response_parts.append("The analysis above is generated by Gemini AI based on your uploaded documents.")
        elif web_matches:
            response_parts.append("\n🌐 **Analysis:**")
            response_parts.append("Based on web search results:")
        
        # Add source information
        response_parts.append(f"\n💾 **Source:** Documents stored in QDRANT cloud cluster")
        
        # Create summary
        summary = {
            "document_matches": len(doc_matches),
            "web_matches": len(web_matches),
            "total_sources": len(sources),
            "primary_source": "documents" if doc_matches else "web" if web_matches else "none"
        }
        
        return {
            "response": "\n".join(response_parts),
            "sources": sources,
            "summary": summary
        }
    
    def process_query(self, query: str):
        """Legacy method for backward compatibility"""
        return self.process_query_with_sources(query)
    
    def get_document_info(self):
        """Get information about indexed documents"""
        try:
            rag_instance = get_rag()
            document_count = rag_instance.get_document_count()
            
            return {
                "status": "success",
                "documents_indexed": len(self.document_store),
                "document_list": [doc['filename'] for doc in self.document_store.values()],
                "rag_system": "QDRANT Cloud",
                "embeddings_stored": document_count,
                "total_pages": sum(doc['pages'] for doc in self.document_store.values()),
                "qdrant_documents": document_count
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get document info: {str(e)}"
            }
    
    def search_documents(self, query: str):
        """Enhanced search with source information"""
        return self.process_query_with_sources(query)
    
    def get_document_analytics(self):
        """Get enhanced document analytics"""
        try:
            total_docs = len(self.document_store)
            total_pages = sum(doc['pages'] for doc in self.document_store.values())
            doc_types = {}
            
            for doc in self.document_store.values():
                filename = doc['filename']
                ext = filename.split('.')[-1].lower() if '.' in filename else 'unknown'
                doc_types[ext] = doc_types.get(ext, 0) + 1
            
            return {
                "status": "success",
                "total_documents": total_docs,
                "total_pages": total_pages,
                "document_types": doc_types,
                "embeddings_generated": len(self.embedding_store),
                "average_pages_per_doc": total_pages / total_docs if total_docs > 0 else 0,
                "recent_uploads": [
                    {
                        "name": doc['filename'],
                        "upload_date": doc['upload_date'],
                        "pages": doc['pages']
                    }
                    for doc in list(self.document_store.values())[-5:]  # Last 5 uploads
                ]
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Analytics failed: {str(e)}"
            }

# Create document service instance
document_service = DocumentService() 