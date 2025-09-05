
import os
import json
import math
from typing import List, Dict
from openai import OpenAI

DEFAULT_STORE_PATH = os.environ.get("RAG_STORE_PATH", "rag_store.json")

def get_client():
    return OpenAI()

EMBED_MODEL = os.environ.get("EMBED_MODEL", "text-embedding-3-small")

def chunk_markdown(text: str, target_size: int = 1000, overlap: int = 150) -> List[str]:
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for p in paras:
        if len(current) + len(p) + 2 <= target_size:
            current = (current + "\n\n" + p).strip()
        else:
            if current:
                chunks.append(current)
                tail = current[-overlap:] if overlap > 0 else ""
                current = (tail + "\n\n" + p).strip()
            else:
                start = 0
                while start < len(p):
                    end = min(start + target_size, len(p))
                    slice_ = p[start:end]
                    chunks.append(slice_)
                    if overlap > 0 and end < len(p):
                        start = end - overlap
                    else:
                        start = end
                current = ""
    if current:
        chunks.append(current)
    return chunks

def cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na == 0 or nb == 0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))

def load_store(path: str = DEFAULT_STORE_PATH) -> Dict:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"chunks": []}

def save_store(store: Dict, path: str = DEFAULT_STORE_PATH) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False)

def clear_store(path: str = DEFAULT_STORE_PATH) -> None:
    if os.path.exists(path):
        os.remove(path)

def embed_texts(texts: List[str]):
    client = get_client()
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]

def add_document_to_store(filename: str, content: str, store_path: str = DEFAULT_STORE_PATH) -> int:
    store = load_store(store_path)
    chunks = chunk_markdown(content)
    if not chunks:
        return 0
    embeddings = embed_texts(chunks)
    for text, emb in zip(chunks, embeddings):
        store["chunks"].append({
            "text": text,
            "source": os.path.basename(filename),
            "embedding": emb
        })
    save_store(store, store_path)
    return len(chunks)

def search(query: str, k: int = 4, store_path: str = DEFAULT_STORE_PATH):
    store = load_store(store_path)
    if not store["chunks"]:
        return []
    client = get_client()
    q_emb = client.embeddings.create(model=EMBED_MODEL, input=[query]).data[0].embedding
    scored = []
    for item in store["chunks"]:
        score = cosine_similarity(q_emb, item["embedding"])
        scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [{"score": float(s), "text": c["text"], "source": c["source"]} for s, c in scored[:k]]
