"""
LLM interaction and langchain utilities
Handles LLM initialization, embeddings, and RAG chain creation
"""

from typing import List, Optional, Callable, Any
import logging

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import SecretStr
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


from src.config import LLM_MODEL, EMBEDDING_MODEL, OPENAI_API_KEY, CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)


def get_llm(temperature: float = 0.7, streaming: bool = False):
    """
    Initialize and return LLM instance
    
    Args:
        temperature: Creativity level (0-1)
        streaming: Enable streaming responses
        
    Returns:
        ChatOpenAI instance
    """
    api_key = SecretStr(OPENAI_API_KEY) if OPENAI_API_KEY else None
    return ChatOpenAI(
        model=LLM_MODEL,
        api_key=api_key,
        temperature=temperature
    )


def get_embeddings():
    """Initialize and return embeddings model"""
    api_key = SecretStr(OPENAI_API_KEY) if OPENAI_API_KEY else None
    return OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=api_key
    )


def split_text(text: str, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into chunks for embedding"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    return splitter.split_text(text)


def create_rag_chain(
    retriever,
    llm=None,
    template: Optional[str] = None,
    metrics_provider: Optional[Callable[[str], str]] = None,
    history_provider: Optional[Callable[[], str]] = None,
):
    """
    Create a Retrieval-Augmented Generation chain
    
    Args:
        retriever: Document retriever function/chain
        llm: Language model (default: get_llm())
        template: Custom prompt template
        
    Returns:
        RAG chain
    """
    if llm is None:
        llm = get_llm()
    
    if template is None:
        template = """You are InsightForge, a Business Intelligence Assistant.
Use the provided context and metrics to answer the user's question.
If the answer is not supported by the context, say you do not know.

Chat History:
{history}

Context:
{context}

Metrics Summary:
{metrics}

Question: {question}

Answer with:
1) A short summary
2) Key insights as bullets
3) Recommendations as bullets (if applicable)
4) Data gaps or assumptions (if any)
"""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    metrics_runnable = RunnableLambda(lambda q: metrics_provider(q) if metrics_provider else "")
    history_runnable = RunnableLambda(lambda _: history_provider() if history_provider else "")

    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough(), "metrics": metrics_runnable, "history": history_runnable}
        | prompt
        | llm
    )
    
    return rag_chain


def create_qa_chain(llm=None) -> Any:
    """
    Create a standalone question-answer chain
    
    Args:
        llm: Language model (default: get_llm())
        
    Returns:
        QA chain
    """
    if llm is None:
        llm = get_llm()
    
    template = """Answer the following question based on your knowledge:

Question: {question}

Answer:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    qa_chain = prompt | llm
    
    return qa_chain


def summarize_documents(documents: List[Document], llm=None) -> str:
    """
    Summarize a list of documents
    
    Args:
        documents: List of Document objects
        llm: Language model (default: get_llm())
        
    Returns:
        Summary text
    """
    if llm is None:
        llm = get_llm()
    
    # Combine document content
    combined_text = "\n\n".join([doc.page_content for doc in documents])
    
    template = """Please provide a concise summary of the following text:

{text}

Summary:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm
    
    result = chain.invoke({"text": combined_text})
    content = result.content if hasattr(result, 'content') else result
    return str(content)
