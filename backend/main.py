import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
import torch
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from huggingface_hub import InferenceClient
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langdetect import detect

HF_TOKEN = os.getenv("HUGGING_FACE_HUB_TOKEN", "")
API_KEY   = os.getenv("API_KEY", "secret226")
DATA_DIR  = os.getenv("DATA_DIR", "/app/data")

client = InferenceClient(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    token=HF_TOKEN,
    provider="novita"        
)

def generate_text(prompt: str, max_length: int = 1000) -> str:
    response = client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_length,
        temperature=0.7,
        top_p=0.9,
    )
    return response.choices[0].message.content.strip()


print(f"📂 Loading documents from {DATA_DIR}…")
documents = []
for filename in os.listdir(DATA_DIR):
    filepath = os.path.join(DATA_DIR, filename)
    try:
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(filepath)
        elif filename.endswith(".txt"):
            loader = TextLoader(filepath, encoding="utf-8")
        else:
            continue
        documents.extend(loader.load())
        print(f"   ✓ {filename}")
    except Exception as e:
        print(f"   ✗ {filename}: {e}")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=100,
    separators=["\n\n", "\n", ". ", " ", ""]
)
chunks = splitter.split_documents(documents)
print(f"Created {len(chunks)} chunks")

device = "cuda" if torch.cuda.is_available() else "cpu"
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    model_kwargs={"device": device},
)
FAISS_INDEX_PATH = "/app/faiss_index"

if os.path.exists(os.path.join(FAISS_INDEX_PATH, "index.faiss")):
    print("Loading existing FAISS index…")
    vectordb = FAISS.load_local(
        FAISS_INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
else:
    print("Building FAISS index from documents…")
    vectordb = FAISS.from_documents(chunks, embeddings)
    vectordb.save_local(FAISS_INDEX_PATH)
    print("✅ FAISS index saved")
print("✅ Vector store ready")


def detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "en"


def create_rag_prompt(query: str, context: str) -> str:
    lang = detect_language(query)
    if lang == "ar":
        return (
            "أنت مساعد ذكاء اصطناعي مفيد للشركات. "
            "أجب فقط باستخدام المعلومات من السياق أدناه.\n\n"
            f"السياق:\n{context}\n\n"
            f"سؤال الموظف: {query}"
        )
    return (
        "You are a helpful enterprise AI assistant. "
        "Answer ONLY using information from the context below.\n\n"
        f"CONTEXT:\n{context}\n\n"
        f"QUESTION: {query}"
    )


def ask_question(question: str, max_length: int = 1000) -> dict:
    docs    = vectordb.similarity_search(question, k=3)
    context = "\n\n".join(
        f"[Doc {i+1}]\n{d.page_content}" for i, d in enumerate(docs)
    )
    prompt  = create_rag_prompt(question, context)
    answer  = generate_text(prompt, max_length)

    return {"question": question, "answer": answer, "language": detect_language(question)}



app = FastAPI(
    title="🦙 Enterprise AI Assistant — Llama 3",
    description="RAG Q&A powered by Meta Llama 3 8B Instruct (EN + AR)",
    version="2.0.0",
)


class QueryRequest(BaseModel):
    question: str
    max_length: Optional[int] = 1000


def verify_key(authorization: str):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    if authorization.removeprefix("Bearer ") != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/")
async def root():
    return {"message": "Enterprise AI Assistant", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "ok", "model": "Meta-Llama-3-8B-Instruct"}


@app.post("/ask")
async def api_ask(request: QueryRequest, authorization: str = Header(...)):
    verify_key(authorization)
    try:
        return ask_question(request.question, request.max_length or 1000)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate")
async def api_generate(request: QueryRequest, authorization: str = Header(...)):
    verify_key(authorization)
    try:
        return {"response": generate_text(request.question, request.max_length or 1000)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
