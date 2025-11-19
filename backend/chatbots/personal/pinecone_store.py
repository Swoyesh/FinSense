# from langchain_pinecone import PineconeVectorStore
# from langchain_openai import OpenAIEmbeddings
# from langchain.schema import Document
# from pinecone import Pinecone, ServerlessSpec
# import os
# from dotenv import load_dotenv

# load_dotenv()

# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY_PERSONAL")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# pc = Pinecone(api_key=PINECONE_API_KEY)
# embeddings = OpenAIEmbeddings(model = "text-embedding-3-small")

# def create_user_index(docs, user_id:int):
#     index_name = f"user-{user_id}-finance"

#     if index_name not in [i.name for i in pc.list_indexes()]:
#         pc.create_index(name=index_name, dimension=1536, metric="cosine", spec=ServerlessSpec(cloud="aws", region="us-east-1"))
#         print(f"Created new pinecone index: {index_name}")

#     else:
#         print(f"Pinecone index {index_name} already exists.")

#     langchain_docs = [Document(page_content=doc['text'], metadata=doc['metadata']) for doc in docs]

#     store = PineconeVectorStore.from_documents(
#         documents=langchain_docs,
#         embedding=embeddings,
#         index_name=index_name
#     )

#     return store

# def load_user_index(user_id:int):
#     index_name = f"user-{user_id}-finance"
#     return PineconeVectorStore.from_existing_index(index_name, embedding=embeddings)

from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY_PERSONAL")

pc = Pinecone(api_key=PINECONE_API_KEY)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def create_user_index(docs, user_id: int):
    index_name = f"user-{user_id}-finance"
    
    existing_indexes = [i.name for i in pc.list_indexes()]
    
    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=1536,  
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        print(f"Created new Pinecone index: {index_name}")
    else:
        print(f"Pinecone index {index_name} already exists.")
    
    langchain_docs = [
        Document(page_content=doc['text'], metadata=doc['metadata']) 
        for doc in docs
    ]
    
    store = PineconeVectorStore.from_documents(
        documents=langchain_docs,
        embedding=embeddings,
        index_name=index_name
    )
    
    return store

def load_user_index(user_id: int):
    index_name = f"user-{user_id}-finance"
    
    existing_indexes = [i.name for i in pc.list_indexes()]
    
    if index_name not in existing_indexes:
        print(f"Index {index_name} does not exist.")
        return None
    
    return PineconeVectorStore.from_existing_index(
        index_name=index_name,
        embedding=embeddings
    )