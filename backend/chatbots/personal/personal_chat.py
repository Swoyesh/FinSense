# from langchain_openai import ChatOpenAI
# from langchain.chains import create_retrieval_chain
# from .pinecone_store import load_user_index
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from .input_detail import prompt

# def personal_chat(input:str, store):
#     retriever = store.as_retriever(search_type="similarity", search_kwargs={"k":3})

#     llm = ChatOpenAI(temperature=0.4, max_tokens=500)

#     question_answering_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
#     rag_chain = create_retrieval_chain(retriever, question_answering_chain)

#     response = rag_chain.invoke({"input": input, "question": input})

#     return response

import os
from dotenv import load_dotenv
from groq import Groq
from langchain_core.documents import Document
from .pinecone_store import load_user_index
from .input_detail import prompt

load_dotenv()

GROQ_CLIENT = Groq(api_key=os.getenv("GROQ_API_KEY"))

def personal_chat(input_text: str, store):
    """
    Perform a personal RAG-based chat using Groq client.
    Args:
        input_text (str): The user's question.
        store: Your vector store object with `.as_retriever()` method.
    Returns:
        dict: Response containing the answer and source documents.
    """
    retriever = store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    
    relevant_docs = retriever.invoke(input_text)
    
    context_text = "\n".join([doc.page_content for doc in relevant_docs])
    
    messages = prompt.format_messages(context=context_text, input=input_text)
    
    groq_messages = [
        {"role": "system" if msg.type == "system" else "user", "content": msg.content}
        for msg in messages
    ]
    
    response = GROQ_CLIENT.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=groq_messages,
        temperature=0.4,
        max_tokens=500
    )
    
    answer = response.choices[0].message.content
    
    return {
        "answer": answer,
        "input": input_text,
        "context": relevant_docs  
    }