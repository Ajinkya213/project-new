from core.rag_utils import MultiModalRAG
from config.settings import QDRANT_URL, QDRANT_API_KEY

rag = MultiModalRAG(url=QDRANT_URL, api_key=QDRANT_API_KEY)