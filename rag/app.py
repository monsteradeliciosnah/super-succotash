from __future__ import annotations
import io, os, hashlib, pathlib, re
from typing import List, Dict, Optional
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from loguru import logger

# Optional imports with graceful fallback
try:
    import faiss  # type: ignore
    FAISS_OK = True
except Exception:
    FAISS_OK = False
try:
    from sentence_transformers import SentenceTransformer
    ST = SentenceTransformer("all-MiniLM-L6-v2")
    ST_OK = True
except Exception:
    ST_OK = False

app = FastAPI(title="Mini RAG Service")

class Settings(BaseSettings):
    store_dir: str = "rag_store"
settings = Settings()
pathlib.Path(settings.store_dir).mkdir(parents=True, exist_ok=True)

def _hash_text(t: str) -> str:
    import hashlib
    return hashlib.sha1(t.encode("utf-8")).hexdigest()

def _chunk(text: str, sz: int = 600, overlap: int = 100) -> List[str]:
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunk = " ".join(words[i:i+sz])
        chunks.append(chunk)
        i += sz - overlap
    return chunks

def _embed_texts(texts: List[str]):
    if ST_OK:
        return ST.encode(texts, convert_to_numpy=True)
    # fallback: crude hashing based vector
    import numpy as np
    vecs = []
    for t in texts:
        h = int(_hash_text(t), 16)
        v = np.array([(h >> (i*8)) & 0xFF for i in range(64)], dtype="float32")
        vecs.append(v / (v.max() or 1))
    return np.vstack(vecs)

class IngestResponse(BaseModel):
    chunks: int
    ok: bool

@app.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(...)):
    text = ""
    raw = await file.read()
    name = file.filename or "upload"
    if name.lower().endswith(".md") or name.lower().endswith(".txt"):
        text = raw.decode("utf-8", errors="ignore")
    elif name.lower().endswith(".pdf"):
        from pdfminer.high_level import extract_text
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(raw); tmp.flush()
            text = extract_text(tmp.name) or ""
    else:
        text = raw.decode("utf-8", errors="ignore")
    chunks = _chunk(text)
    vecs = _embed_texts(chunks)
    import numpy as np, json
    np.save(os.path.join(settings.store_dir, "vectors.npy"), vecs)
    with open(os.path.join(settings.store_dir, "chunks.json"), "w") as f:
        import json; json.dump(chunks, f)
    return IngestResponse(chunks=len(chunks), ok=True)

class SearchRequest(BaseModel):
    q: str
    k: int = 5

class SearchHit(BaseModel):
    text: str
    score: float

class SearchResponse(BaseModel):
    hits: List[SearchHit]

@app.post("/search", response_model=SearchResponse)
async def search(req: SearchRequest):
    import json, numpy as np
    chunks = json.load(open(os.path.join(settings.store_dir, "chunks.json")))
    vecs = np.load(os.path.join(settings.store_dir, "vectors.npy"))
    qv = _embed_texts([req.q])[0]
    sims = vecs @ qv / (np.linalg.norm(vecs, axis=1) * (np.linalg.norm(qv) or 1))
    idx = np.argsort(-sims)[: req.k]
    hits = [SearchHit(text=chunks[i], score=float(sims[i])) for i in idx]
    return SearchResponse(hits=hits)
