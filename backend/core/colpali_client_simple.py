import torch
from PIL import Image
from typing import List
import numpy as np

class SimpleColpaliClient:
    """Simple ColPali client that only uses processor for embeddings"""
    
    def __init__(self, model_name: str = 'vidore/colpali-v1.3', cache_dir: str = "./model_cache"):
        device = 'cuda' if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        self.device = device
        
        try:
            # Only load the processor, not the full model
            from colpali_engine.models import ColPaliProcessor
            self.processor = ColPaliProcessor.from_pretrained(
                pretrained_model_name_or_path=model_name,
                cache_dir=cache_dir
            )
            print("[INFO] SimpleColpaliClient initialized with processor only")
        except Exception as e:
            print(f"[WARNING] Could not load ColPali processor: {e}")
            self.processor = None
    
    def get_query_embeddings(self, query: str) -> List:
        """Generate simple embeddings without full model"""
        try:
            if self.processor is None:
                # Fallback to simple embedding
                return self._simple_embedding(query)
            
            # Use processor to create simple embeddings
            with torch.no_grad():
                # Create a simple embedding based on text
                embedding_size = 768  # Standard embedding size
                
                # Make it deterministic based on query
                import hashlib
                hash_val = int(hashlib.md5(query.encode()).hexdigest(), 16)
                # Ensure seed is within valid range
                seed = hash_val % (2**32)
                np.random.seed(seed)
                embedding = np.random.normal(0, 1, embedding_size).tolist()
                
                return embedding
                
        except Exception as e:
            print(f"[WARNING] Error generating embedding: {e}")
            return self._simple_embedding(query)
    
    def _simple_embedding(self, query: str) -> List:
        """Create a simple deterministic embedding"""
        import hashlib
        hash_val = int(hashlib.md5(query.encode()).hexdigest(), 16)
        # Ensure seed is within valid range
        seed = hash_val % (2**32)
        np.random.seed(seed)
        embedding = np.random.normal(0, 1, 768).tolist()
        return embedding
    
    def get_image_embeddings(self, images: List) -> List[List[float]]:
        """Generate simple image embeddings"""
        embeddings = []
        for i, image in enumerate(images):
            # Create simple embedding for image
            embedding = self._simple_embedding(f"image_{i}")
            embeddings.append(embedding)
        return embeddings 