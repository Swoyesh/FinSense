from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from .pinecone_store import load_user_index
from langchain.chains.combine_documents import create_stuff_documents_chain
from .input_detail import prompt

def personal_chat(input:str, store):
    retriever = store.as_retriever(search_type="similarity", search_kwargs={"k":3})

    llm = ChatOpenAI(temperature=0.4, max_tokens=500)

    question_answering_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
    rag_chain = create_retrieval_chain(retriever, question_answering_chain)

    response = rag_chain.invoke({"input": input, "question": input})

    return response