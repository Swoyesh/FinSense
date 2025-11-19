# FinSense - AI-Powered Personal Finance Management System

<div align="center">

![FinSense Banner](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green?style=flat-square) ![React](https://img.shields.io/badge/React-19.1+-61DAFB?style=flat-square) ![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

**An intelligent financial assistant that classifies transactions, forecasts budgets, and provides personalized financial insights using AI.**

[Features](#features) • [Tech Stack](#tech-stack) • [Quick Start](#quick-start) • [Architecture](#architecture) • [API Documentation](#api-documentation) • [Contributing](#contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
- [Architecture](#architecture)
- [Key Components](#key-components)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**FinSense** is an intelligent personal finance management system that combines machine learning, time-series forecasting, and natural language processing to help users:

- 📊 **Automatically classify** financial transactions into categories
- 💰 **Forecast budgets** using statistical models (ARIMA, Exponential Smoothing)
- 🤖 **Chat about finances** with an AI assistant powered by Groq LLM
- 📈 **Analyze spending patterns** with personalized insights
- 🔐 **Securely manage** financial data with authentication

Built as a **Final Year Project**, FinSense demonstrates full-stack development with production-grade ML integration.

---

## ✨ Features

### 💳 Transaction Classification (Dual Approach)
- **Speed Model** (MiniLM): ~200ms response time, instant local classification
- **Accuracy Model** (Groq LLM): 2-5s response time, higher precision with LLM
- Users choose between speed and accuracy based on their needs

### 📅 Budget Forecasting
- **Ensemble Forecasting**: Combines ARIMA, Exponential Smoothing, Linear Regression, and Simple Moving Average
- **Monthly Predictions**: Forecast spending patterns for next 1-3 months
- **Category-wise Budgets**: Per-category spending recommendations
- **Visual Analytics**: Interactive charts and downloadable Excel reports

### 💬 Intelligent Chatbot (3-Mode Operation)
1. **General Chat**: Finance knowledge base Q&A (Groq + RAG)
2. **Personal Chat**: Query your own transaction history (Groq + Pinecone Vector DB)
3. **SQL Chat**: Direct database queries in natural language

### 🔐 Security & Authentication
- JWT-based authentication with httpOnly cookies
- Async PostgreSQL with SQLAlchemy ORM
- User-scoped data isolation
- CORS protection with explicit origin whitelisting

### 📱 Responsive UI
- React 19 + Vite modern frontend
- Tailwind CSS styling
- Real-time API integration with error handling

---

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (async, modern, production-ready)
- **Database**: PostgreSQL with SQLAlchemy async ORM
- **Authentication**: JWT + httpOnly cookies
- **Server**: Uvicorn (ASGI)

### Machine Learning & NLP
- **Transaction Classification**: 
  - MiniLM (local, fast)
  - Groq LLM API (accurate, slower)
- **Intent Classification**: Hybrid custom classifier
- **Time Series Forecasting**: ARIMA, Exponential Smoothing, Linear Regression
- **Vector Embeddings**: Pinecone for RAG (Retrieval-Augmented Generation)

### Frontend
- **Framework**: React 19
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios

### Infrastructure
- **Vector Database**: Pinecone (cloud-hosted, multi-user support)
- **LLM Provider**: Groq (fast inference, cost-effective)
- **Deployment-Ready**: Docker, environment-based config

---

## 📁 Project Structure

```
FinSense/
├── backend/                           # FastAPI backend
│   ├── main.py                        # Entry point, route definitions
│   ├── auth.py                        # JWT authentication
│   ├── database.py                    # SQLAlchemy models & sessions
│   ├── transaction.py                 # Transaction operations
│   ├── budget.py                      # Budget & forecasting logic
│   ├── classification_helper.py       # Transaction classification
│   ├── intent_classifier/             # Intent classification models
│   ├── chatbots/                      # Chat functionality
│   │   ├── general/                   # General knowledge base chat
│   │   ├── personal/                  # Personal transaction chat
│   │   │   ├── personal_chat.py
│   │   │   ├── personal_docs.py
│   │   │   ├── pinecone_store.py      # Vector DB integration
│   │   │   └── text_sql/              # Natural language to SQL
│   │   └── chat_memory.py             # Conversation history
│   ├── forecast/                      # Time-series forecasting
│   │   ├── model.py                   # ARIMA/Ensemble logic
│   │   ├── cleaner_shaping.py         # Data preprocessing
│   ├── Visualize/                     # Visualization
│   │   ├── vis_forecast.py            # Matplotlib charts
│   │   └── img_converter.py           # Base64 image encoding
│   ├── templates/                     # HTML templates (if needed)
│   └── tests/                         # Unit tests
│
├── frontend1/                         # React frontend
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   ├── pages/
│   │   ├── context/                   # Auth context
│   │   ├── services/                  # API calls
│   │   └── styles/
│   └── public/
│
├── Modelling/                         # ML model training
│   ├── preprocessing.py               # Data preprocessing pipeline
│   ├── data_loader.py                 # Load training data
│   ├── config.py                      # ML configurations
│   └── converter.py                   # Label encoding utilities
│
├── models/                            # Pre-trained models (in .gitignore)
│   ├── MiniLM/                        # MiniLM checkpoint
│   ├── IntentClassifier/              # Intent model
│   ├── TimeSeriesBudget/              # Forecasting models
│   └── TransactionClassifier/         # Classification models
│
├── dataset/                           # Training data (in .gitignore)
│   ├── digital_wallet_transactions.csv
│   ├── esewa_transactions_balanced_final.csv
│   └── finance_time_series.csv
│
├── timeseries/                        # Forecasting notebooks
│   └── time_ser_mod.ipynb
│
├── transaction_classifier/            # BERT fine-tuning checkpoints (in .gitignore)
│   └── checkpoint-*/
│
├── requirements.txt                   # Main dependencies
├── requirements-dev.txt               # Development dependencies
├── requirements-prod.txt              # Production dependencies
├── requirements-ml.txt                # ML/data science extras
├── .gitignore                         # Git ignore rules
├── BACKEND_SETUP.md                   # Backend setup guide
└── README.md                          # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for frontend)
- **PostgreSQL 13+** (or SQLite for development)
- **Groq API Key** (get from https://console.groq.com)
- **Pinecone API Key** (get from https://www.pinecone.io)

### Installation

#### 1. Clone Repository
```bash
git clone https://github.com/Swoyesh/FinSense.git
cd FinSense
```

#### 2. Backend Setup

**Create virtual environment:**
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
# or
source venv/bin/activate      # Linux/Mac
```

**Install dependencies:**
```bash
pip install -r requirements-dev.txt  # For development
# or
pip install -r requirements-prod.txt # For production
```

**Configure environment:**
Create `backend/.env`:
```env
# API Keys
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/finsense

# Pinecone
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-west1-gcp

# Security
SECRET_KEY=your-super-secret-key-min-32-chars
ALGORITHM=HS256

# CORS
FRONTEND_URL=http://localhost:5173
```

#### 3. Frontend Setup

```bash
cd frontend1
npm install
npm run dev
```

Frontend runs at: **http://localhost:5173**

### Running the Application

#### Start Backend Server
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### Start Frontend
```bash
cd frontend1
npm run dev
```

#### Run Tests
```bash
pytest backend/tests/ -v
```

---

## 🏗 Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + Vite)                  │
│                   http://localhost:5173                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTP/REST API
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    BACKEND (FastAPI)                        │
│                   http://localhost:8000                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ API Routes:                                           │  │
│  │ • /auth/* (Login, Register, Verify)                  │  │
│  │ • /chat (Intent Classification + Response)           │  │
│  │ • /predict_speed (MiniLM Classification)             │  │
│  │ • /predict_accuracy (Groq LLM Classification)        │  │
│  │ • /budget (Forecasting + Visualization)              │  │
│  │ • /download/* (Excel Export)                         │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬──────────────┐
        │              │              │              │
┌───────▼──┐  ┌────────▼──────┐  ┌───▼────────┐  ┌─▼──────────┐
│PostgreSQL│  │    Groq LLM   │  │  Pinecone  │  │  MiniLM    │
│Database  │  │   (LLM API)   │  │  (Vector) │  │  (Local)   │
└──────────┘  └───────────────┘  └────────────┘  └────────────┘
```

### Data Flow: Transaction Classification

```
User Upload (Excel)
         ↓
    FastAPI Route
         ↓
Text Cleaning Pipeline
         ↓
    ┌────┴────┐
    │          │
    ▼ (Fast)   ▼ (Accurate)
MiniLM     Groq LLM
(200ms)    (2-5s)
    │          │
    └────┬─────┘
         ▼
    SQLAlchemy ORM
         ↓
    PostgreSQL Database
         ↓
    JSON Response + Excel Export
```

### Data Flow: Budget Forecasting

```
User Input (Income, Savings)
         ↓
Fetch User Transactions
         ↓
Data Cleaning & Reshaping
         ↓
    Monthly Aggregation
         ↓
Ensemble Forecasting:
├─ ARIMA Model
├─ Exponential Smoothing
├─ Linear Regression
└─ Simple Moving Average
         ↓
    Averaging Predictions
         ↓
Generate Matplotlib Chart
         ↓
Convert to Base64 PNG
         ↓
Create Excel Report
         ↓
JSON Response + Download Link
```

### Chatbot Flow

```
User Query
    ↓
Intent Classification (Hybrid Model)
    ├─ General Finance? → Knowledge Base RAG
    ├─ Personal Transactions? → SQL Query + Groq LLM
    └─ Other? → Helpful Response
    ↓
Groq LLM Response
    ↓
Conversation Memory Update
    ↓
JSON Response to Frontend
```

---

## 🔌 API Documentation

### Authentication Endpoints

#### Register
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

### Classification Endpoints

#### Speed Classification (MiniLM - Local)
```http
POST /predict_speed
Content-Type: multipart/form-data

file: <Excel file with transactions>
```

**Response:**
```json
[
  {
    "Description": "Coffee at Cafe",
    "Amount": 150.0,
    "Category": "Food & Dining"
  }
]
```

#### Accuracy Classification (Groq LLM)
```http
POST /predict_accuracy
Content-Type: multipart/form-data

file: <Excel file with transactions>
```

### Chat Endpoint

```http
POST /chat
Content-Type: application/json

{
  "text": "How much did I spend on groceries last month?"
}
```

**Response:**
```json
{
  "intent": "personal",
  "confidence": 0.95,
  "response": "You spent NPR 8,500 on groceries last month.",
  "sql_query": "SELECT SUM(amount) FROM transactions WHERE category='Groceries' AND user_id=1",
  "data": {"total": 8500}
}
```

### Budget Forecast Endpoint

```http
POST /budget
Content-Type: multipart/form-data

income: 50000
saving_amt: 10000
```

**Response:**
```json
{
  "message": "Budget generated successfully",
  "forecast": {
    "Food": 12000,
    "Transport": 5000,
    "Utilities": 3000
  },
  "budget": {
    "Food": 12500,
    "Transport": 5500
  },
  "image_data": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "forecast_month": "2025-12-01"
}
```

---

## ⚙️ Configuration

### Environment Variables

**Backend (.env):**
```env
# API Keys
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxx

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/finsense
DATABASE_DEBUG=false

# Pinecone
PINECONE_API_KEY=pcsk_xxxxxxxxxxxxx
PINECONE_ENVIRONMENT=us-west1-gcp

# Security
SECRET_KEY=your-min-32-character-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
FRONTEND_URL=http://localhost:5173

# Logging
LOG_LEVEL=INFO
```

### Model Configuration

Edit `backend/config.py` for:
- ARIMA (p, d, q) parameters
- Model paths
- Batch processing sizes
- Cache settings

---

## 🐳 Deployment

### Docker Setup

```dockerfile
# backend/Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements-prod.txt .
RUN pip install -r requirements-prod.txt

COPY . .

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/finsense
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=finsense
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Production Checklist
- [ ] Set `DEBUG=false`
- [ ] Update `SECRET_KEY` with strong random value
- [ ] Configure PostgreSQL with proper credentials
- [ ] Set up SSL/HTTPS
- [ ] Enable CORS only for production domain
- [ ] Set up monitoring & logging
- [ ] Configure backup strategy
- [ ] Test API rate limiting

---

## 📊 Performance Metrics

| Component | Latency | Notes |
|-----------|---------|-------|
| MiniLM Classification | ~200ms | Local, CPU |
| Groq LLM Classification | 2-5s | API call |
| Budget Forecast | 15-30s | Ensemble computation |
| Chatbot Response | 1-3s | Groq LLM + Vector search |
| DB Query | <100ms | Async PostgreSQL |

---

## 🤝 Contributing

Contributions are welcome! Follow these steps:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Development Workflow
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest backend/tests/ -v

# Format code
black backend/
isort backend/

# Lint code
flake8 backend/
pylint backend/
```

---

## 📝 Model Details

### Transaction Classification
- **Speed Model**: MiniLM fine-tuned on transaction descriptions
- **Accuracy Model**: Groq LLM (mixtral-8x7b-32768) with prompt engineering
- **Categories**: Food & Dining, Transport, Utilities, Entertainment, Medical, etc.

### Budget Forecasting
- **ARIMA**: Captures autocorrelation and trend
- **Exponential Smoothing**: Handles seasonal patterns
- **Linear Regression**: Trend component
- **Ensemble**: Averaging reduces variance

### Intent Classification
- **Hybrid Model**: Combines TF-IDF + custom rules
- **Intents**: general, personal, personal_rag, personal_sql
- **Confidence Threshold**: 0.5

---

## 📄 License

This project is licensed under the **MIT License** - see the LICENSE file for details.

---

## 👨‍💻 Author

**Swoyesh** - Final Year Project, 2025

---

## 🙏 Acknowledgments

- **Groq** - Fast LLM inference
- **Pinecone** - Vector database infrastructure
- **HuggingFace** - Pre-trained models
- **FastAPI** - Amazing web framework
- **React** - Modern UI library

---

## 📞 Support

For issues, questions, or suggestions:

1. **GitHub Issues**: Create an issue on the repository
2. **Email**: swoyesh@example.com
3. **Documentation**: See BACKEND_SETUP.md for setup help

---

<div align="center">

**Built with ❤️ for intelligent financial management**

⭐ If you find this project helpful, please consider giving it a star!

</div>
