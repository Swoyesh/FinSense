from langchain_core.prompts import ChatPromptTemplate

system_prompt = (
    "You are a financial expert. Use the following pieces of context to answer the question at the end. "
    "If you don't know the answer, just say that you don't know, don't try to make up an answer. "
    "Use three sentences maximum. "
    "Context: {context} "
    "Question: {question} "
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])