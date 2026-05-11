from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

import os

from services.preprocessing import (
    load_and_process_catalog
)

from services.embeddings import (
    load_embedding_model,
    load_or_generate_embeddings
)

from services.faiss_service import (
    load_or_create_faiss_index
)

from services.bm25_service import (
    build_bm25
)

from services.llm import (
    load_groq_client,
    generate_agent_response
)


load_dotenv()

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)


catalog = None

embedding_model = None

embeddings = None

index = None

bm25 = None

groq_client = None


app = FastAPI(
    title="SHL Recommendation Agent"
)

class Message(BaseModel):

    role: str

    content: str


class RecommendationRequest(BaseModel):

    messages: List[Message]


@app.on_event("startup")
async def startup_event():

    global catalog
    global embedding_model
    global embeddings
    global index
    global bm25
    global groq_client

    print("loading resources...")

    # catalog

    catalog = load_and_process_catalog(
        "data/shl_product_catalog.json"
    )

    # embedding model

    embedding_model = load_embedding_model()

    # embeddings

    embeddings = load_or_generate_embeddings(
        processed_catalog=catalog,
        model=embedding_model
    )

    # faiss

    index = load_or_create_faiss_index(
        embeddings
    )

    # bm25

    bm25 = build_bm25(
        catalog
    )

    # groq

    groq_client = load_groq_client(
        GROQ_API_KEY
    )

    print("startup complete")


@app.get("/health")
async def health_check():

    return {
        "status": "ok"
    }


@app.post("/chat")
async def chat(
    request: RecommendationRequest
):

    result = generate_agent_response(


        messages=[
            m.model_dump()
            for m in request.messages
        ],

        groq_client=groq_client,

        embedding_model=embedding_model,

        index=index,

        bm25=bm25,

        catalog=catalog
    )

    return result