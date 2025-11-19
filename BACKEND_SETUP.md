# =============================================================================
# FINSENSE - BACKEND SETUP GUIDE
# =============================================================================

## Installation & Setup

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
# or
source venv/bin/activate      # Linux/Mac
```

### 2. Install Dependencies

**For Development (includes testing, linting, Jupyter):**
```bash
pip install -r requirements-dev.txt
```

**For Production (lightweight):**
```bash
pip install -r requirements-prod.txt
```

**For ML/Data Science Work (Jupyter, TensorFlow, etc.):**
```bash
pip install -r requirements-ml.txt
```

**For Everything (main requirements):**
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the `backend/` directory:
```env
# API Keys
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_environment

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/finsense

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256

# CORS Settings
FRONTEND_URL=http://localhost:5173
```

### 4. Run Backend Server

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at: **http://localhost:8000**
API Docs: **http://localhost:8000/docs**

---

## Dependency Organization

| File | Purpose | Size | Usage |
|------|---------|------|-------|
| `requirements.txt` | Main production dependencies | ~50 packages | Default |
| `requirements-prod.txt` | Lightweight for deployment | ~35 packages | Docker/Production |
| `requirements-dev.txt` | Development + testing tools | Includes main + dev | Local development |
| `requirements-ml.txt` | ML/Data science extras | Includes main + ML | Notebooks, training |

---

## Key Dependencies Breakdown

### Web Framework
- **FastAPI** - Modern async web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

### Database
- **SQLAlchemy** - ORM
- **asyncpg** - Async PostgreSQL driver

### ML/NLP
- **Transformers** - HuggingFace models (MiniLM, BERT)
- **PyTorch** - Deep learning framework
- **scikit-learn** - ML algorithms
- **statsmodels** - Statistical modeling

### Time Series
- **statsmodels** - ARIMA, exponential smoothing
- **statsforecast** - Fast forecasting

### LLM & RAG
- **LangChain** - LLM orchestration
- **Pinecone** - Vector database
- **Groq SDK** - Fast LLM inference

### Authentication
- **python-jose** - JWT tokens
- **bcrypt** - Password hashing

---

## Updating Dependencies

### Freeze current environment
```bash
pip freeze > requirements-current.txt
```

### Update specific package
```bash
pip install --upgrade package_name
```

### Update all packages
```bash
pip install --upgrade -r requirements.txt
```

---

## Troubleshooting

### PyTorch CPU-only build
If you want to switch to GPU (CUDA):
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### spaCy model download
If using spaCy NLP:
```bash
python -m spacy download en_core_web_sm
```

### Conflicting dependencies
If you get conflicts:
```bash
pip install --force-reinstall -r requirements.txt
```

---

## Performance Notes

- ✅ **Torch CPU build** (~2GB) - Lightweight, no GPU needed
- ✅ **Async database driver (asyncpg)** - Non-blocking DB calls
- ✅ **Optional TensorFlow** - Only in requirements-ml.txt (5GB+ if installed)
- ✅ **Pinecone cloud** - No local vector DB overhead

---
