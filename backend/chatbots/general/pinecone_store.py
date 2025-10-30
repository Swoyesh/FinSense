from langchain.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
import os
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from .knowledge_base_loader import knowledge_base_creation

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
pc = Pinecone(api_key=PINECONE_API_KEY)

def download_huggingface_embeddings():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return embeddings

embeddings = download_huggingface_embeddings()

def create_general_index(docs):
    index_name = "finsense-new"

    if index_name not in [i.name for i in pc.list_indexes()]:
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            serverless_spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        print(f"Created new pinecone index: {index_name}")

    else:
        print(f"Pinecone index {index_name} already exists.")

    store = PineconeVectorStore.from_documents(
        documents = docs,
        index_name = index_name,
        embedding = embeddings
    )

    return store

def load_general_index():
    index_name = "finsense-new"
    return PineconeVectorStore.from_existing_index(index_name = index_name, embedding=embeddings)