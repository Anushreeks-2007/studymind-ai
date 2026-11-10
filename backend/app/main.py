from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ml.pipeline import StudyMindPipeline
from backend.app.database import (
    initialize_database,
    save_documents,
    get_all_documents
)


app = FastAPI(
    title="StudyMind AI",
    description="Context-aware information and decision support system",
    version="1.0"
)

pipeline = StudyMindPipeline(n_clusters=3)


class DocumentRequest(BaseModel):
    documents: list[str]


class QueryRequest(BaseModel):
    query: str
    top_k: int = 3


@app.on_event("startup")
def startup():
    """Initialize SQLite and restore previously saved documents."""

    initialize_database()

    saved_documents = get_all_documents()

    if saved_documents:
        pipeline.memory.add_documents(saved_documents)


@app.get("/")
def home():
    return {"message": "StudyMind AI API is running!"}


@app.post("/process")
def process_documents(request: DocumentRequest):
    try:
        if len(request.documents) <= pipeline.n_clusters:
            raise ValueError(
                "Please provide at least 4 documents."
            )

        save_documents(request.documents)

        all_documents = get_all_documents()

        result = pipeline.process_documents(all_documents)

        return result

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/ask")
def ask_question(request: QueryRequest):
    try:
        results = pipeline.ask(
            request.query,
            request.top_k
        )

        return {"results": results}

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))