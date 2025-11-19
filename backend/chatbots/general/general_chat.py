import os
from dotenv import load_dotenv
from groq import Groq
from langchain_core.documents import Document
from .input_detail import prompt

load_dotenv()

GROQ_CLIENT = Groq(api_key=os.getenv("GROQ_API_KEY"))

def general_chat(input_text: str, store):
    """
    Perform a general RAG-based chat using Groq client.
    """
    retriever = store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    relevant_docs = retriever.invoke(input_text)
    context_text = "\n".join([doc.page_content for doc in relevant_docs])
    
    messages = prompt.format_messages(context=context_text, input=input_text)
    
    groq_messages = [
        {"role": "system" if msg.type == "system" else "user", "content": msg.content}
        for msg in messages
    ]
    
    completion = GROQ_CLIENT.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=groq_messages,
        temperature=0.4,
        max_tokens=500,
        top_p=1,
        stream=True
    )
    
    response_text = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            response_text += chunk.choices[0].delta.content
    
    return response_text