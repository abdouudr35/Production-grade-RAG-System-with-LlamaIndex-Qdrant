import logging 
from fastapi import FastAPI
import inngest 
import inngest.fast_api 
from inngest.experimental import ai 
from openai import AsyncOpenAI
from dotenv import load_dotenv
import uuid 
import os 
import datetime
from data_loader import load_and_chunk_pdf, embed_texts
from vector_db import QdrantStorage
from custom_types import RAGChunkAndSrc, RAGQueryResult, RAGSearchResult, RAGUpsertResult


load_dotenv()

inngest_client = inngest.Inngest(
    app_id = "rag_app",
    logger = logging.getLogger("uvicorn"),
    is_production=False,
    serializer=inngest.PydanticSerializer()
)

@inngest_client.create_function(
    fn_id="RAG: Ingest PDF",
    trigger=inngest.TriggerEvent(event="rag/ingest_pdf")
)

async def rag_ingest_pdf(ctx: inngest.Context) : 
    def _load(ctx: inngest.Context) -> RAGChunkAndSrc :
        pdf_path = ctx.event.data["pdf_path"]
        source_id = ctx.event.data.get("source_id", pdf_path)
        chunks = load_and_chunk_pdf(pdf_path)
        return RAGChunkAndSrc(chunks=chunks, source_id=source_id)
    def _upsert(chunks_and_src: RAGChunkAndSrc) -> RAGUpsertResult :

        chunks = chunks_and_src.chunks
        source_id = chunks_and_src.source_id
        vecs=embed_texts(chunks)
        ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, name=f"{source_id}:{i}")) for i in range(len(chunks))]
        payloads = [{"source": source_id, "text": chunks[i]} for i in range (len(chunks))]
        QdrantStorage().upsert(ids, vecs, payloads)
        return RAGUpsertResult(ingested=len(chunks))
    
    chunk_and_src = await ctx.step.run("load-and-chunk", lambda: _load(ctx), output_type=RAGChunkAndSrc )
    ingested = await ctx.step.run("embed-and-upsert", lambda: _upsert(chunk_and_src), output_type=RAGUpsertResult)
    return ingested.model_dump()

@inngest_client.create_function(
    fn_id="RAG: Query PDF", 
    # 1. On regroupe les deux événements dans une liste (attention à la virgule)
    trigger=[
        inngest.TriggerEvent(event="rag/query_pdf_ai"),
        inngest.TriggerEvent(event="rag/ingest_pdf")
    ],
    # 2. On utilise 'limit=' au lieu de 'count='
    throttle=inngest.Throttle(
        limit=2, 
        period=datetime.timedelta(minutes=1)
    ),
    rate_limit=inngest.RateLimit(
        limit=1,
        period=datetime.timedelta(hours=4),
        key="event.data.source_id",
    ),
)
async def rag_query_pdf_ai(ctx: inngest.Context):
    def _search(question : str, top_k: int=5):
        query_vec = embed_texts([question])[0]
        store = QdrantStorage()
        found = store.search(query_vec, top_k)
        return RAGSearchResult(contexts=found["contexts"], sources=found["sources"])
    
    question = ctx.event.data["question"]
    top_k = int(ctx.event.data.get("top_k", 5))
    
    found = await ctx.step.run("embed-and-search", lambda: _search(question, top_k ), output_type=RAGSearchResult)
    context_block = "\n\n".join(f"- {c}"for c in found.contexts) 
    user_content= (
        "Use the following context to answer the question. \n\n"
        f"Context:\n{context_block}\n\n"
        f"Question: {question}\n"
        "Answer concisely using the context above."
    )
    print("TEST DE LA CLE :", os.getenv("GROQ_API_KEY"))
   
  
    adapter = ai.openai.Adapter(
    auth_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1", # Keep this so it knows to route to Groq!
    model="llama-3.3-70b-versatile" 
)
    res = await ctx.step.ai.infer(
    "llm-answer",
    adapter=adapter,
    body={
        "max_tokens": 1024,
        "temperature": 0.2, # ⚠️ Corrige la faute de frappe de ta vidéo ici !
        "messages": [
          {  "role": "system","content": "You answer questions using only the provided context"}, 
          { 
              "role": "user", 
                "content": user_content # Use the exact name of the variable you created at line 68
          }

                
        ]
    }
)
    answer = res["choices"][0]["message"]["content"].strip()
    return{"answer": answer, "sources": found.sources, "num_contexts": len(found.contexts)}

app = FastAPI()
@app.get("/")
def home():
    return {"message": "Mon API RAG est bien en ligne !"}

inngest.fast_api.serve(app, inngest_client, [rag_ingest_pdf, rag_query_pdf_ai])

