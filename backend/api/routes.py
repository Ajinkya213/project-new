from fastapi import APIRouter, UploadFile, File
from typing import List
from backend.services.query_service import process_query, process_documents

router = APIRouter()

@router.post("/upload/")
async def upload(files: List[UploadFile] = File(...)):
    return await process_documents(files)

@router.post("/query/")
async def query(query: str):
    return await process_query(query)