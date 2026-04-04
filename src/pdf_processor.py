import os
import tempfile
import streamlit as st
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

@st.cache_resource(show_spinner=False)
def load_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

def extract_text_from_pdf(uploaded_file):
    docs = []
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    try:
        reader = PdfReader(tmp_path)
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            text = text.strip()
            if text:
                docs.append(Document(
                    page_content=text,
                    metadata={
                        "source": uploaded_file.name,
                        "page": page_num,
                        "total_pages": len(reader.pages),
                    }
                ))
    finally:
        os.unlink(tmp_path)
    return docs

def process_pdfs(uploaded_files):
    all_docs = []
    metadata = {}
    for f in uploaded_files:
        f.seek(0)
        docs = extract_text_from_pdf(f)
        all_docs.extend(docs)
        metadata[f.name] = {
            "pages": len(docs),
            "raw_text": " ".join([d.page_content for d in docs]),
        }
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " "],
    )
    chunks = splitter.split_documents(all_docs)
    embeddings = load_embeddings()
    vector_store = FAISS.from_documents(chunks, embeddings)
    return vector_store, all_docs, metadata

def get_raw_text_for_summary(all_docs, filename):
    texts = [d.page_content for d in all_docs if d.metadata.get("source") == filename]
    combined = " ".join(texts)
    return combined[:4000]
