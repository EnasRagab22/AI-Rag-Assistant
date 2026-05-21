# 🦙 Enterprise AI Knowledge Assistant — Tips Hindawi

A bilingual (English + Arabic) AI assistant powered by **Meta Llama 3 8B Instruct**, built with a RAG (Retrieval-Augmented Generation) pipeline over company documents.

---

## 🗂️ Project Structure

```
enterprise-ai-assistant/
├── backend/
│   ├── main.py                  # FastAPI app + RAG pipeline
│   ├── requirements.txt         # Python dependencies
│   └── data/                    # Company documents (PDF, TXT)
├── frontend/
│   ├── app.py                   # Streamlit web UI
│   ├── requirements-frontend.txt
│   └── assets/
│       ├── icon.jpg
│       └── background.jpg
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── nginx.conf
├── Jenkinsfile                  # CI/CD pipeline
├── deploy.yml                   # Ansible playbook
├── .env.example                 # Environment variables template
├── .dockerignore
├── .gitignore
└── README.md
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| LLM | Meta Llama 3 8B Instruct (via HuggingFace) |
| RAG | LangChain + FAISS vector store |
| Embeddings | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Containerization | Docker + Docker Compose |
| CI/CD | Jenkins + Ansible |
| Reverse Proxy | Nginx |

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/your-org/enterprise-ai-assistant.git
cd enterprise-ai-assistant
```

### 2. Set up environment variables
```bash
cp .env.example .env
```

Edit `.env` and fill in your values:
```env
HUGGING_FACE_HUB_TOKEN=your_hf_token_here
API_KEY=your_secret_api_key
DATA_DIR=/app/data
HF_HOME=/app/.cache/huggingface
```

### 3. Add your company documents
Place your `.pdf` and `.txt` files inside `backend/data/`:
```
backend/data/
├── hr_policy.pdf
├── it_guidelines.txt
├── leave_policy.pdf
└── ...
```

### 4. Build and run
```bash
docker compose up -d --build
```

### 5. Access the app
| Service | URL |
|---|---|
| Frontend (Streamlit) | http://localhost:8522 |
| Backend (FastAPI) | http://localhost:5050 |
| API Docs (Swagger) | http://localhost:5050/docs |

---

## 🔑 Environment Variables

| Variable | Description | Default |
|---|---|---|
| `HUGGING_FACE_HUB_TOKEN` | HuggingFace API token for Llama 3 access | required |
| `API_KEY` | Bearer token to authenticate API requests | `secret226` |
| `DATA_DIR` | Path to company documents inside container | `/app/data` |
| `HF_HOME` | HuggingFace model cache directory | `/app/.cache/huggingface` |
| `API_URL` | Backend URL used by the frontend | `http://backend:8000` |

---

## 🌐 API Endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/` | Root — service status | ❌ |
| GET | `/health` | Health check | ❌ |
| POST | `/ask` | RAG question answering (EN + AR) | ✅ Bearer |
| POST | `/generate` | Raw text generation | ✅ Bearer |

### Example request
```bash
curl -X POST http://localhost:5050/ask \
  -H "Authorization: Bearer secret226" \
  -H "Content-Type: application/json" \
  -d '{"question": "How many annual leave days do I have?", "max_length": 500}'
```

### Example response
```json
{
  "question": "How many annual leave days do I have?",
  "answer": "According to the leave policy, employees are entitled to 21 annual leave days per year.",
  "language": "en"
}
```

---

## 🐳 Docker Images

| Image | Container | Port |
|---|---|---|
| `enterpriseaiassistant_tipshindawicompany-backend:latest` | `tips_hindawi_backend` | `5050` |
| `enterpriseaiassistant_tipshindawicompany-frontend:latest` | `tips_hindawi_frontend` | `8522` |

---

## 🔄 CI/CD Pipeline (Jenkins)

The `Jenkinsfile` defines the following stages:

```
Clean Workspace
      ↓
Checkout Code
      ↓
Down Containers
      ↓
Ensure SonarQube Running
      ↓
SonarQube Scan
      ↓
Create .env
      ↓
Deploy Stack (Ansible)
      ↓
Post Check
```

### Jenkins Credentials Required

| Credential ID | Type | Value |
|---|---|---|
| `github_cred` | Username/Password | GitHub login |
| `HF_TOKEN` | Secret text | HuggingFace token |
| `API_KEY` | Secret text | API bearer token |

---

## 📋 Ansible Playbook

Deploys the full stack locally using Docker commands:

```bash
ansible-playbook deploy.yml \
    -e "hf_token=your_hf_token" \
    -e "api_key=secret226"
```

**No inventory file needed** — runs on `localhost` with `connection: local`.

---

## 🌍 Bilingual Support

The assistant automatically detects the question language and responds accordingly:

- **English** → answers in English
- **Arabic (العربية)** → answers in Arabic

Example Arabic query:
```json
{"question": "كم عدد أيام الإجازة السنوية؟"}
```

---

## 📦 Adding New Documents

1. Place new `.pdf` or `.txt` files in `backend/data/`
2. Delete the cached FAISS index so it rebuilds:
```bash
docker exec tips_hindawi_backend rm -rf /app/faiss_index
docker restart tips_hindawi_backend
```
3. The index rebuilds automatically on next startup

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---|---|
| Backend unhealthy | Wait 2–3 min for Llama 3 to load. Check `docker logs tips_hindawi_backend` |
| FAISS index error | Delete `faiss_index/` folder and restart backend |
| Port already in use | Run `netsh interface ipv4 show excludedportrange protocol=tcp` (Windows) and change port in `docker-compose.yml` |
| HF token error | Make sure your token has Llama 3 access at huggingface.co/meta-llama |
| Arabic not detected | Ensure `langdetect` is installed and query has enough Arabic characters |

---

## 👨‍💻 Development

To run without Docker (for local development):

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
pip install -r requirements-frontend.txt
streamlit run app.py
```

---

## 📄 License

Internal project — Tips Hindawi Company. All rights reserved.

---

<div align="center">
  <p>Built with 💜 for Tips Hindawi</p>
  <p>Powered by Meta Llama 3 • LangChain • FastAPI • Streamlit</p>
</div>