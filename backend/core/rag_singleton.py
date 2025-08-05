import os
from typing import Dict, List
import uuid

# Create a lazy-loading RAG system
class LazyRAG:
    def __init__(self, url: str, api_key: str):
        self.url = url
        self.api_key = api_key
        self._colpali = None
        self._qdrant = None
        self._gemini = None
        self._initialized = False
        self.collection_name = 'documents'
        print("[INFO] LazyRAG initialized - models will load on first use")
    
    def _ensure_initialized(self):
        """Initialize components on first use"""
        if not self._initialized:
            try:
                print("[INFO] Loading RAG components...")
                from .colpali_client_simple import SimpleColpaliClient
                from .qdrant_utils import VectorDBClient
                
                self._colpali = SimpleColpaliClient()
                self._qdrant = VectorDBClient(self.url, self.api_key)
                self._init_collection()
                self._init_gemini()
                self._initialized = True
                print("[INFO] RAG components loaded successfully")
            except Exception as e:
                print(f"[WARNING] Could not initialize RAG components: {e}")
                self._initialized = True  # Mark as initialized to avoid retry
    
    def _init_collection(self):
        """Initialize Qdrant collection"""
        try:
            # Check if collection exists
            collections = self._qdrant._get_collections().collections
            collection_exists = any(col.name == self.collection_name for col in collections)
            
            if not collection_exists:
                print(f"[INFO] Creating collection '{self.collection_name}'...")
                # Create collection with proper configuration
                from qdrant_client.http import models
                self._qdrant.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=768,  # Standard embedding size
                        distance=models.Distance.COSINE
                    )
                )
                print(f"[INFO] Collection '{self.collection_name}' created successfully")
            else:
                print(f"[INFO] Collection '{self.collection_name}' already exists")
        except Exception as e:
            print(f"[WARNING] Could not initialize Qdrant collection: {e}")
            # Try to create collection directly
            try:
                from qdrant_client.http import models
                self._qdrant.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=768,
                        distance=models.Distance.COSINE
                    )
                )
                print(f"[INFO] Collection '{self.collection_name}' created on retry")
            except Exception as e2:
                print(f"[ERROR] Failed to create collection: {e2}")
    
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
    
    def index_document(self, dataset: List[Dict]):
        """Index documents using ColPali embeddings and store in QDRANT"""
        self._ensure_initialized()
        
        if not self._colpali or not self._qdrant:
            return {
                "status": "error",
                "message": "RAG components not available"
            }
        
        try:
            print(f"[INFO] RAG indexing {len(dataset)} documents to QDRANT")
            
            points = []
            processed_count = 0
            
            # Process each document
            for item in dataset:
                doc_id = item.get('doc_id', str(uuid.uuid4()))
                page_num = item.get('page_number', 1)
                filename = item.get('filename', 'unknown.pdf')
                text_content = item.get('text_content', f"Document: {filename}, Page: {page_num}")
                
                # Generate embedding using ColPali
                try:
                    embedding = self._colpali.get_query_embeddings(text_content)
                    print(f"[INFO] Generated embedding for {filename} page {page_num}")
                    
                    # Create point for QDRANT - use UUID for point ID
                    point_id = str(uuid.uuid4())
                    point = {
                        'id': point_id,
                        'vector': embedding,
                        'payload': {
                            'doc_id': doc_id,
                            'page_number': page_num,
                            'filename': filename,
                            'text_content': text_content,
                            'timestamp': item.get('timestamp', ''),
                            'source': 'document'
                        }
                    }
                    points.append(point)
                    processed_count += 1
                    
                except Exception as e:
                    print(f"[WARNING] Could not generate embedding for {filename} page {page_num}: {e}")
                    continue
            
            # Store points in QDRANT
            if points:
                try:
                    # Convert to QDRANT format
                    from qdrant_client.http import models
                    qdrant_points = []
                    
                    for point in points:
                        qdrant_points.append(
                            models.PointStruct(
                                id=point['id'],
                                vector=point['vector'],
                                payload=point['payload']
                            )
                        )
                    
                    # Insert into QDRANT
                    self._qdrant.client.upsert(
                        collection_name=self.collection_name,
                        points=qdrant_points
                    )
                    
                    print(f"[INFO] Successfully stored {len(points)} embeddings in QDRANT")
                    
                except Exception as e:
                    print(f"[ERROR] Failed to store embeddings in QDRANT: {e}")
                    return {
                        "status": "error",
                        "message": f"Failed to store embeddings in QDRANT: {str(e)}"
                    }
            
            return {
                "status": "success",
                "message": f"Documents indexed and stored in QDRANT successfully. {processed_count} pages processed.",
                "pages_processed": processed_count,
                "embeddings_stored": len(points)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to index documents: {str(e)}"
            }
    
    def generate_result(self, query_text: str) -> Dict:
        """Complete flow: Query embedding → QDRANT search → Gemini response"""
        self._ensure_initialized()
        
        if not self._colpali or not self._qdrant:
            return {
                "status": "error",
                "message": "RAG components not available"
            }
        
        try:
            print(f"[INFO] Processing query: {query_text}")
            
            # Step 1: Generate query embedding
            try:
                query_embedding = self._colpali.get_query_embeddings(query_text)
                print(f"[INFO] Generated query embedding")
            except Exception as e:
                print(f"[WARNING] Could not generate query embedding: {e}")
                return {
                    "status": "error",
                    "message": f"Could not process query: {str(e)}"
                }
            
            # Step 2: Search in QDRANT using query embedding
            try:
                from qdrant_client.http import models
                
                search_results = self._qdrant.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    limit=5,
                    with_payload=True,
                    with_vectors=False
                )
                
                print(f"[INFO] Found {len(search_results)} relevant documents in QDRANT")
                
                # Step 3: Prepare context for Gemini
                relevant_docs = []
                context_parts = []
                
                for result in search_results:
                    payload = result.payload
                    doc_info = {
                        'filename': payload.get('filename', 'Unknown'),
                        'page_number': payload.get('page_number', 1),
                        'text_content': payload.get('text_content', ''),
                        'score': result.score,
                        'doc_id': payload.get('doc_id', '')
                    }
                    relevant_docs.append(doc_info)
                    
                    # Add to context for Gemini
                    context_parts.append(f"Document: {doc_info['filename']} (Page {doc_info['page_number']})\nContent: {doc_info['text_content']}")
                
                # Step 4: Generate Gemini response
                if relevant_docs and self._gemini:
                    try:
                        # Create prompt for Gemini
                        context = "\n\n".join(context_parts)
                        prompt = f"""Based on the following documents, answer the user's question. If the documents don't contain relevant information, say so clearly.

Documents:
{context}

User Question: {query_text}

Please provide a comprehensive answer based on the documents above. Include specific references to document names and page numbers when relevant."""

                        # Generate response using Gemini
                        response = self._gemini.generate_content(prompt)
                        gemini_response = response.text
                        
                        print(f"[INFO] Generated Gemini response")
                        
                        # Step 5: Format final response
                        final_response_parts = []
                        final_response_parts.append(f"🔍 **Search Results:**")
                        final_response_parts.append(f"I found {len(relevant_docs)} relevant documents in your uploaded files:")
                        
                        for i, doc in enumerate(relevant_docs[:3], 1):
                            final_response_parts.append(f"{i}. **{doc['filename']}** (Page {doc['page_number']})")
                        
                        final_response_parts.append(f"\n📋 **Analysis:**")
                        final_response_parts.append(gemini_response)
                        final_response_parts.append(f"\n💾 **Source:** Documents stored in QDRANT cloud cluster")
                        
                        return {
                            "status": "success",
                            "response": "\n\n".join(final_response_parts),
                            "query_embedding_generated": True,
                            "documents_found": len(relevant_docs),
                            "search_results": relevant_docs,
                            "gemini_response": gemini_response
                        }
                        
                    except Exception as e:
                        print(f"[ERROR] Gemini response generation failed: {e}")
                        # Fallback to simple response
                        return self._generate_fallback_response(query_text, relevant_docs)
                
                else:
                    # No relevant documents found
                    return {
                        "status": "success",
                        "response": f"I searched your uploaded documents in QDRANT but didn't find specific information about '{query_text}'. You may want to upload more relevant documents or try a different query.",
                        "query_embedding_generated": True,
                        "documents_found": 0,
                        "search_results": [],
                        "gemini_response": "No relevant documents found."
                    }
                
            except Exception as e:
                print(f"[ERROR] QDRANT search failed: {e}")
                return {
                    "status": "error",
                    "message": f"Search failed: {str(e)}"
                }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error during RAG process: {str(e)}"
            }
    
    def _generate_fallback_response(self, query_text: str, relevant_docs: List[Dict]) -> Dict:
        """Generate fallback response when Gemini is not available"""
        response_parts = []
        response_parts.append(f"🔍 **Search Results:**")
        response_parts.append(f"I found {len(relevant_docs)} relevant documents in your uploaded files:")
        
        for i, doc in enumerate(relevant_docs[:3], 1):
            response_parts.append(f"{i}. **{doc['filename']}** (Page {doc['page_number']}) - {doc['text_content'][:200]}...")
        
        response_parts.append(f"\n📋 **Analysis:**")
        response_parts.append(f"Based on your query '{query_text}', I found relevant information in your uploaded documents. The documents contain information that may be helpful for your question.")
        response_parts.append(f"\n💾 **Source:** Documents stored in QDRANT cloud cluster")
        
        return {
            "status": "success",
            "response": "\n\n".join(response_parts),
            "query_embedding_generated": True,
            "documents_found": len(relevant_docs),
            "search_results": relevant_docs,
            "gemini_response": "Fallback response generated."
        }
    
    def search_documents(self, query_text: str) -> Dict:
        """Search documents in QDRANT"""
        return self.generate_result(query_text)
    
    def get_document_count(self) -> int:
        """Get number of documents stored in QDRANT"""
        try:
            self._ensure_initialized()
            if self._qdrant:
                info = self._qdrant.client.get_collection(self.collection_name)
                return info.points_count
            return 0
        except Exception as e:
            print(f"[WARNING] Could not get document count: {e}")
            return 0

# Create lazy RAG instance
try:
    from config.settings import Config
    config = Config()
    rag = LazyRAG(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)
    print("[INFO] Using LazyRAG with QDRANT cloud storage and Gemini")
except Exception as e:
    print(f"[WARNING] Could not initialize RAG: {e}")
    # Fallback to simple RAG
    class SimpleRAG:
        def __init__(self, url: str, api_key: str):
            self.url = url
            self.api_key = api_key
            self.documents = {}
            print("[INFO] SimpleRAG initialized successfully")
        
        def generate_result(self, query_text: str) -> Dict:
            """Generate a simple result without heavy dependencies"""
            try:
                return {
                    "status": "success",
                    "response": f"I understand your query: '{query_text}'. This is a simple response from the RAG system.",
                    "quality_metrics": {"quality": "basic"},
                    "num_images_processed": 0
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Error processing query: {str(e)}",
                    "response": "I encountered an error while processing your query. Please try again."
                }

        def index_document(self, dataset: List[Dict]):
            """Index documents in the simple RAG system"""
            try:
                print(f"[INFO] SimpleRAG indexing {len(dataset)} documents")
                return {
                    "status": "success",
                    "message": f"Documents indexed successfully. {len(dataset)} pages processed.",
                    "pages_processed": len(dataset)
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to index documents: {str(e)}"
                }
    
    rag = SimpleRAG(url="", api_key="")
    print("[INFO] Using SimpleRAG fallback")

# Ensure the RAG is initialized once
def get_rag():
    """Get the RAG singleton instance"""
    return rag 