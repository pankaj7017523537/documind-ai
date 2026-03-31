from groq import Groq
from src.utils import get_groq_api_key, format_source

# Direct Groq client - bypasses langchain-groq entirely (no reasoning_format issue)
_client = None

def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=get_groq_api_key())
    return _client

SYSTEM_PROMPT = """You are DocuMind, an expert AI document assistant. Answer questions based ONLY on the provided document context.

Rules:
- Answer only from the context. If not found, say "I couldn't find this in the uploaded documents."
- Be specific and reference relevant parts of the document.
- Keep answers clear, structured, and helpful."""

class SimpleRAGChain:
    """Simple RAG chain that uses Groq directly without langchain-groq."""
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5},
        )
        self.chat_history = []  # list of (human, ai) tuples
    
    def invoke(self, inputs):
        question = inputs.get("question", "")
        
        # Retrieve relevant docs
        docs = self.retriever.invoke(question)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Build chat history string
        history_str = ""
        for human, ai in self.chat_history[-6:]:  # last 6 turns
            history_str += f"Human: {human}\nAssistant: {ai}\n\n"
        
        # Build messages for Groq
        user_content = f"""Context from documents:
{context}

Chat History:
{history_str}
Question: {question}"""

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_content},
        ]
        
        # Call Groq directly - no reasoning_format involved
        response = get_client().chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            max_tokens=1500,
        )
        
        answer = response.choices[0].message.content
        
        # Update history
        self.chat_history.append((question, answer))
        
        return {
            "answer": answer,
            "source_documents": docs,
        }


def build_rag_chain(vector_store):
    return SimpleRAGChain(vector_store)


def ask_question(chain, question):
    result = chain.invoke({"question": question})
    answer = result.get("answer", "No answer returned.")
    source_docs = result.get("source_documents", [])
    
    seen = set()
    sources = []
    for doc in source_docs:
        label = format_source(doc)
        if label not in seen:
            seen.add(label)
            sources.append({
                "label": label,
                "excerpt": doc.page_content[:250].strip(),
            })
    
    return {"answer": answer, "sources": sources}