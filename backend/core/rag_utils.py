#!/usr/bin/env python3
"""
RAG (Retrieval-Augmented Generation) utilities
"""

from typing import List, Dict, Tuple
from PIL import Image
from .colpali_client import ColpaliClient
from .qdrant_utils import VectorDBClient
import google.generativeai as genai
import os

class MultiModalRAG:
    def __init__(self, url: str, api_key: str, image_dir: str = r'..\data\pdf_images'):
        self.colpali = ColpaliClient()
        self.qdrant = VectorDBClient(url, api_key)
        self.collection = 'test'
        self.image_dir = image_dir
        self._init_collection()
        
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        print("[INFO] MultiModalRAG initialized successfully")
        
    def _init_collection(self):
        collections = self.qdrant._get_collections().collections
        if not any(col.name == self.collection for col in collections):
            print(f"[INFO] Creating collections...")
            self.qdrant.create_collection()
        else:
            print(f"[INFO] Collection already exists")
            
    def index_document(self, dataset: List[Dict]):
        print("[INFO] Preparing point structures for Qdrant...")
        points = self.qdrant.create_points(self.colpali, dataset)
        
        print("[INFO] Inserting data into Qdrant...")
        self.qdrant.insert_data(points, dataset)
        
    def query(self, query_text: str) -> List[Dict]:
        print(f"[INFO] Generating embedding for query: '{query_text}'")
        query_embeddings = self.colpali.get_query_embeddings(query_text)
        
        print("[INFO] Performing vector search in Qdrant...")
        response = self.qdrant.search(user_query=query_embeddings)
        
        # Extract points from QueryResponse object
        results = response.points if hasattr(response, 'points') else []
        print(f"[INFO] Found {len(results)} matching results")
        
        return results
    
    def get_result_images(self, search_result: List, dataset: List[Dict] = None) -> List[Tuple[Image.Image, Dict]]:        
        retrieved_images = []
        for result in search_result:
            if hasattr(result, 'payload'):
                payload = result.payload
                score = result.score
            else:
                payload = result.get("payload", {})
                score = result.get('score', 0)
                
            doc_id = payload.get("doc_id")
            page_num = payload.get("page_num")
            filename = payload.get("source")
            
            # Construct image path from metadata
            pdf_name_without_ext = filename.replace('.pdf', '')
            image_filename = f"doc_{doc_id}_page_{page_num}_{pdf_name_without_ext}.png"
            image_path = os.path.join(self.image_dir, image_filename)  # Use your actual image directory
            
            try:
                # Load image from disk
                image = Image.open(image_path)
                metadata = {
                    'doc_id': doc_id,
                    'page_number': page_num,
                    'filename': filename,
                    'score': score
                }
                retrieved_images.append((image, metadata))
                print(f"[INFO] Retrieved image: {filename}, page {page_num}, score: {score:.3f}")
            except FileNotFoundError:
                print(f"[WARNING] Image file not found: {image_path}")
            except Exception as e:
                print(f"[ERROR] Failed to load image {image_path}: {e}")
        
        return retrieved_images
    
    def search_and_retrieve(self, query_text: str, top_k: int = 5) -> List[Tuple[Image.Image, Dict]]:
        """
        Complete workflow: search for relevant pages and retrieve their images
        """
        # Get search results
        search_results = self.query(query_text)
        
        # Limit results if needed
        if top_k and len(search_results) > top_k:
            search_results = search_results[:top_k]
        
        # Retrieve corresponding images
        retrieved_images = self.get_result_images(search_results)
        
        print(f"[INFO] Retrieved {len(retrieved_images)} images for query: '{query_text}'")
        return retrieved_images
    
    def prepare_for_gemini(self, retrieved_images: List[Tuple[Image.Image, Dict]]) -> List[Image.Image]:
        """Prepare images for Gemini processing"""
        return [img for img, _ in retrieved_images]
    
    def evaluate_retrieval_quality(self, retrieved_images: List[Tuple[Image.Image, Dict]], query: str) -> Dict:
        """Evaluate the quality of retrieved images"""
        if not retrieved_images:
            return {"quality": "poor", "reason": "No images retrieved"}
        
        # Simple quality metrics
        avg_score = sum(metadata['score'] for _, metadata in retrieved_images) / len(retrieved_images)
        num_images = len(retrieved_images)
        
        quality = "excellent" if avg_score > 0.8 else "good" if avg_score > 0.6 else "poor"
        
        return {
            "quality": quality,
            "avg_score": avg_score,
            "num_images": num_images,
            "query": query
        }
    
    def generate_result(self, query_text: str) -> Dict:
        """
        Generate a comprehensive result using multimodal RAG
        """
        try:
            # Search and retrieve images
            retrieved_images = self.search_and_retrieve(query_text)
            
            if not retrieved_images:
                return {
                    "status": "no_results",
                    "message": "No relevant documents found for your query.",
                    "response": "I couldn't find any relevant information in the uploaded documents. Please try rephrasing your query or upload relevant documents."
                }
            
            # Evaluate retrieval quality
            quality_metrics = self.evaluate_retrieval_quality(retrieved_images, query_text)
            
            # Prepare images for Gemini
            images_for_gemini = self.prepare_for_gemini(retrieved_images)
            
            # Generate multimodal response
            prompt = f"""
            Based on the following query and the retrieved document images, provide a comprehensive answer.
            
            Query: {query_text}
            
            Please analyze the document images and provide:
            1. A direct answer to the query
            2. Key information from the documents
            3. Document references (filename and page numbers)
            
            Be specific and reference the document content accurately.
            """
            
            if images_for_gemini:
                # Use multimodal model with images
                response = self.model.generate_content([prompt, *images_for_gemini])
            else:
                # Fallback to text-only
                response = self.model.generate_content(prompt)
            
            return {
                "status": "success",
                "response": response.text,
                "quality_metrics": quality_metrics,
                "num_images_processed": len(images_for_gemini)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing query: {str(e)}",
                "response": "I encountered an error while processing your query. Please try again."
            } 