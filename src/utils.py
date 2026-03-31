import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_groq_api_key():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        try:
            key = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass
    return key

def format_source(doc):
    meta = doc.metadata
    source = meta.get("source", "Unknown file")
    page = meta.get("page", None)
    filename = os.path.basename(source) if source else "Document"
    if page is not None:
        return f"📄 **{filename}** — Page {int(page) + 1}"
    return f"📄 **{filename}**"

def truncate(text, max_chars=300):
    return text[:max_chars] + "..." if len(text) > max_chars else text

def clean_json_response(text):
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:])
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()
