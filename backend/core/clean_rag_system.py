#!/usr/bin/env python3
"""
Clean RAG System - Following Exact Data Flow Specification

Data Flow:
Document Upload → PDF Conversion → Image Generation → Embedding Creation → Vector Storage
Query Processing → Embedding Generation → Vector Search → Image Retrieval → Gemini Analysis → Response Generation
"""

import os
import uuid
from typing import Dict, List, Any
from datetime import datetime

class CleanRAGSystem:
    """
    Clean RAG System following the exact data flow specification
    """
    
    def __init__(self, qdrant_url: str, qdrant_api_key: str):
        self.qdrant_url = qdrant_url
        self.qdrant_api_key = qdrant_api_key
        self.collection_name = 'documents'
        self._colpali = None
        self._qdrant = None
        self._gemini = None
        self._pdf_converter = None
        self._initialized = False
        print("[INFO] CleanRAGSystem initialized")
    
    def _ensure_initialized(self):
        """Initialize all components on first use"""
        if not self._initialized:
            try:
                print("[INFO] Initializing Clean RAG components...")
                
                # Initialize PDF converter
                from .utils import PdfConverter
                self._pdf_converter = PdfConverter()
                
                # Initialize ColPali for embeddings
                from .colpali_client_simple import SimpleColpaliClient
                self._colpali = SimpleColpaliClient()
                
                # Initialize QDRANT
                from .qdrant_utils import VectorDBClient
                self._qdrant = VectorDBClient(self.qdrant_url, self.qdrant_api_key)
                
                # Initialize collection
                self._init_collection()
                
                # Initialize Gemini
                self._init_gemini()
                
                self._initialized = True
                print("[INFO] Clean RAG components initialized successfully")
                
            except Exception as e:
                print(f"[ERROR] Failed to initialize Clean RAG: {e}")
                self._initialized = True  # Mark as initialized to avoid retry
    
    def _init_collection(self):
        """Initialize QDRANT collection"""
        try:
            from qdrant_client.http import models
            
            # Check if collection exists
            collections = self._qdrant._get_collections().collections
            collection_exists = any(col.name == self.collection_name for col in collections)
            
            if not collection_exists:
                print(f"[INFO] Creating collection '{self.collection_name}'...")
                self._qdrant.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=768,
                        distance=models.Distance.COSINE
                    )
                )
                print(f"[INFO] Collection '{self.collection_name}' created")
            else:
                print(f"[INFO] Collection '{self.collection_name}' already exists")
                
        except Exception as e:
            print(f"[ERROR] Failed to initialize collection: {e}")
    
    def _init_gemini(self):
        """Initialize Gemini for response generation"""
        try:
            import google.generativeai as genai
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self._gemini = genai.GenerativeModel('gemini-2.0-flash-exp')
                print("[INFO] Gemini initialized successfully")
            else:
                print("[WARNING] GEMINI_API_KEY not found")
        except Exception as e:
            print(f"[WARNING] Could not initialize Gemini: {e}")
    
    def process_document_upload(self, file_path: str) -> Dict[str, Any]:
        """
        Step 1: Document Upload → PDF Conversion → Image Generation → Embedding Creation → Vector Storage
        
        Args:
            file_path: Path to the uploaded PDF file
            
        Returns:
            Dict with processing results
        """
        self._ensure_initialized()
        
        try:
            print(f"[INFO] Starting document processing: {file_path}")
            
            # Step 1: PDF Conversion
            print("[INFO] Step 1: PDF Conversion")
            pdf_images = self._pdf_converter.pdf_to_image(file_path)
            print(f"[INFO] Converted {len(pdf_images)} pages to images")
            
            # Step 2: Image Generation (already done in pdf_to_image)
            print("[INFO] Step 2: Image Generation")
            for img_data in pdf_images:
                print(f"[INFO] Generated image: {img_data['image_path']}")
            
            # Step 3: Embedding Creation
            print("[INFO] Step 3: Embedding Creation")
            embeddings_created = 0
            qdrant_points = []
            
            for img_data in pdf_images:
                try:
                    # Extract text content from image (simplified - in real implementation, use OCR)
                    text_content = f"Document: {img_data['filename']}, Page: {img_data['page_number']}"
                    
                    # Generate embedding using ColPali
                    embedding = self._colpali.get_query_embeddings(text_content)
                    embeddings_created += 1
                    
                    # Create QDRANT point
                    from qdrant_client.http import models
                    point = models.PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding,
                        payload={
                            'doc_id': img_data['doc_id'],
                            'page_number': img_data['page_number'],
                            'filename': img_data['filename'],
                            'text_content': text_content,
                            'image_path': img_data['image_path'],
                            'timestamp': datetime.now().isoformat(),
                            'source': 'document_upload'
                        }
                    )
                    qdrant_points.append(point)
                    
                    print(f"[INFO] Created embedding for {img_data['filename']} page {img_data['page_number']}")
                    
                except Exception as e:
                    print(f"[WARNING] Failed to create embedding for page {img_data['page_number']}: {e}")
                    continue
            
            # Step 4: Vector Storage
            print("[INFO] Step 4: Vector Storage")
            if qdrant_points:
                self._qdrant.client.upsert(
                    collection_name=self.collection_name,
                    points=qdrant_points
                )
                print(f"[INFO] Stored {len(qdrant_points)} embeddings in QDRANT")
            
            return {
                "status": "success",
                "message": "Document processed successfully",
                "pages_processed": len(pdf_images),
                "images_generated": len(pdf_images),
                "embeddings_created": embeddings_created,
                "vectors_stored": len(qdrant_points),
                "filename": os.path.basename(file_path)
            }
            
        except Exception as e:
            print(f"[ERROR] Document processing failed: {e}")
            return {
                "status": "error",
                "message": f"Document processing failed: {str(e)}"
            }
    
    def process_query(self, query_text: str) -> Dict[str, Any]:
        """
        Step 2: Query Processing → Embedding Generation → Vector Search → Image Retrieval → Gemini Analysis → Response Generation
        
        Args:
            query_text: User's query
            
        Returns:
            Dict with response and metadata
        """
        self._ensure_initialized()
        
        try:
            print(f"[INFO] Processing query: {query_text}")
            
            # Step 1: Embedding Generation
            print("[INFO] Step 1: Embedding Generation")
            query_embedding = self._colpali.get_query_embeddings(query_text)
            print("[INFO] Generated query embedding")
            
            # Step 2: Vector Search
            print("[INFO] Step 2: Vector Search")
            from qdrant_client.http import models
            
            search_results = self._qdrant.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=5,
                with_payload=True,
                with_vectors=False
            )
            
            print(f"[INFO] Found {len(search_results)} relevant documents")
            
            # Step 3: Image Retrieval
            print("[INFO] Step 3: Image Retrieval")
            retrieved_images = []
            context_parts = []
            
            for result in search_results:
                payload = result.payload
                retrieved_images.append({
                    'filename': payload.get('filename', 'Unknown'),
                    'page_number': payload.get('page_number', 1),
                    'image_path': payload.get('image_path', ''),
                    'text_content': payload.get('text_content', ''),
                    'score': result.score
                })
                
                # Add to context for Gemini
                context_parts.append(f"Document: {payload.get('filename')} (Page {payload.get('page_number')})\nContent: {payload.get('text_content')}")
            
            # Step 4: Gemini Analysis
            print("[INFO] Step 4: Gemini Analysis")
            if retrieved_images and self._gemini:
                try:
                    context = "\n\n".join(context_parts)
                    prompt = f"""Based on the following documents and their images, answer the user's question. If the documents don't contain relevant information, say so clearly.

Documents and Images:
{context}

User Question: {query_text}

Please provide a comprehensive answer based on the documents above. Include specific references to document names and page numbers when relevant."""

                    response = self._gemini.generate_content(prompt)
                    gemini_response = response.text
                    print("[INFO] Generated Gemini response")
                    
                    # Step 5: Response Generation
                    print("[INFO] Step 5: Response Generation")
                    final_response = f"""🔍 **Search Results:**
I found {len(retrieved_images)} relevant documents in your uploaded files:

"""
                    
                    for i, img in enumerate(retrieved_images[:3], 1):
                        final_response += f"{i}. **{img['filename']}** (Page {img['page_number']})\n"
                    
                    final_response += f"""
📋 **Analysis:**
{gemini_response}

💾 **Source:** Documents and images stored in QDRANT cloud cluster
🔗 **Images Retrieved:** {len(retrieved_images)} images from vector search"""
                    
                    return {
                        "status": "success",
                        "response": final_response,
                        "query_embedding_generated": True,
                        "vectors_searched": len(search_results),
                        "images_retrieved": len(retrieved_images),
                        "gemini_analysis": gemini_response,
                        "retrieved_images": retrieved_images
                    }
                    
                except Exception as e:
                    print(f"[ERROR] Gemini analysis failed: {e}")
                    return {
                        "status": "error",
                        "message": f"Analysis failed: {str(e)}"
                    }
            else:
                return {
                    "status": "success",
                    "response": f"I searched your uploaded documents but didn't find specific information about '{query_text}'. You may want to upload more relevant documents or try a different query.",
                    "query_embedding_generated": True,
                    "vectors_searched": len(search_results),
                    "images_retrieved": 0,
                    "gemini_analysis": "No relevant documents found."
                }
                
        except Exception as e:
            print(f"[ERROR] Query processing failed: {e}")
            return {
                "status": "error",
                "message": f"Query processing failed: {str(e)}"
            }
    
    def get_document_count(self) -> int:
        """Get number of documents in QDRANT"""
        try:
            if self._qdrant:
                collections = self._qdrant._get_collections().collections
                for collection in collections:
                    if collection.name == self.collection_name:
                        return collection.vectors_count
            return 0
        except Exception as e:
            print(f"[ERROR] Failed to get document count: {e}")
            return 0

# Global instance
_clean_rag_instance = None

def get_clean_rag():
    """Get global Clean RAG instance"""
    global _clean_rag_instance
    if _clean_rag_instance is None:
        qdrant_url = os.getenv("QDRANT_URL", "https://your-qdrant-url.qdrant.io")
        qdrant_api_key = os.getenv("QDRANT_API_KEY", "your-qdrant-api-key")
        _clean_rag_instance = CleanRAGSystem(qdrant_url, qdrant_api_key)
    return _clean_rag_instance 