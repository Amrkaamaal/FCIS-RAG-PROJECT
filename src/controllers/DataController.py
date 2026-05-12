import os
from typing import Dict, Any

from fastapi import UploadFile

from controllers.indexer import run_pipeline


class DataController:
    def __init__(self):
        self.documents_dir = os.getenv("DOCUMENTS_DIR", "assets/documents/job_pdfs")

    async def save_upload(self, file: UploadFile) -> Dict[str, Any]:
        filename = os.path.basename(file.filename or "")
        if not filename:
            raise ValueError("Missing filename")

        ext = os.path.splitext(filename)[1].lower()
        if ext not in {".pdf"}:
            raise ValueError("Only PDF files are supported")

        os.makedirs(self.documents_dir, exist_ok=True)
        dest_path = os.path.join(self.documents_dir, filename)

        content = await file.read()
        if not content:
            raise ValueError("Uploaded file is empty")

        with open(dest_path, "wb") as handle:
            handle.write(content)

        return {
            "status": "ok",
            "filename": filename,
            "path": dest_path,
        }

    def process_files(self, chunk_size: int, overlap: int, do_reset: bool) -> Dict[str, Any]:
        os.environ["FILE_CHUNK_SIZE"] = str(chunk_size)
        os.environ["FILE_CHUNK_OVERLAP"] = str(overlap)

        run_pipeline(
            documents_dir=self.documents_dir,
            db_path=os.getenv("VECTOR_DB_PATH", "assets/db/qdrant_data"),
            collection_name=os.getenv("COLLECTION_NAME", "job_documents"),
            reset=do_reset,
        )

        return {
            "status": "ok",
            "chunk_size": chunk_size,
            "overlap": overlap,
            "reset": do_reset,
        }
