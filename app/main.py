import os
from fastapi import FastAPI
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langserve import add_routes
from dotenv import load_dotenv

load_dotenv()

# 1. Cargar, dividir e indexar la base de conocimiento
loader = TextLoader("app/promtior_data.txt")
documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs = text_splitter.split_documents(documents)

# Los embeddings se generan localmente con sentence-transformers (no requiere API key)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(docs, embeddings)
retriever = vectorstore.as_retriever()

# 2. Crear la plantilla de prompt
template = """You are a helpful assistant for Promtior.

IMPORTANT RULES:
1. Detect the language of the Question and reply ONLY in that same language. If the question is in Spanish, your entire answer must be in Spanish. If the question is in English, your entire answer must be in English.
2. Be direct and natural. Do NOT start your answer with phrases like "Based on the provided document", "According to the context", "According to the provided documents", or any similar expression. Just answer directly.
3. Use only the information from the Context below to answer.
4. If the context does not contain enough information, say so briefly in the same language as the question.

Context:
{context}

Question: {question}

Answer (in the same language as the question):"""
prompt = ChatPromptTemplate.from_template(template)

# 3. Crear el modelo de lenguaje (Groq - tier gratuito)
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3,
)

# 4. Crear la cadena RAG
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 5. Crear la aplicación FastAPI y agregar la ruta de LangServe
app = FastAPI(
    title="Promtior Chatbot",
    version="1.0",
    description="Un chatbot para responder preguntas sobre Promtior.",
)

add_routes(
    app,
    rag_chain,
    path="/chatbot",
)

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
