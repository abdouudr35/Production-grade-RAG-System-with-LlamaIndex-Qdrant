from openai import OpenAI
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv 
import os
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


load_dotenv()
client = os.getenv("GROQ_API_KEY")
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3")
EMBED_DIM = 3072
splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)

def load_and_chunk_pdf(path:str) :
    docs = PDFReader().load_data(file=path)
    texts= [d.text for d in docs if getattr(d, "text", None)]
    chunks = []
    for t in texts: 
        chunks.extend(splitter.split_text(t))
    return chunks

def embed_texts(texts: list[str]) -> list[list[float]]:
    # LlamaIndex s'occupe de tout : il prend la liste de textes, 
    # génère les embeddings localement, et renvoie directement la liste de vecteurs.
    embeddings = embed_model.get_text_embedding_batch(texts)
    
    return embeddings


