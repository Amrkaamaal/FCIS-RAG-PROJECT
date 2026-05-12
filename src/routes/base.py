import os

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["base"])


@router.get("/")
def health_check():
  return {
      "status": "ok",
      "name": os.getenv("APP_NAME", "RAG-Project"),
  }
