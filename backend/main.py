from fastapi import FastAPI
from backend.api.routes import router

app = FastAPI(title="Multimodal RAG Agent API")
app.include_router(router)