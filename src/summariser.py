import json
from groq import Groq
from src.utils import get_groq_api_key, clean_json_response

def get_groq_client():
    return Groq(api_key=get_groq_api_key())

def summarise_document(raw_text, filename):
    client = get_groq_client()
    word_count = len(raw_text.split())
    prompt = f"""You are an expert document analyst. Analyse the following document and return ONLY a valid JSON object.

Document name: {filename}
Document text:
{raw_text[:4000]}

Return ONLY this JSON, no extra text:
{{
  "summary": "3-4 sentence summary of what this document is about",
  "doc_type": "Type of document (Research Paper, Textbook, Report, Article, etc.)",
  "key_topics": ["topic1","topic2","topic3","topic4","topic5","topic6","topic7","topic8","topic9","topic10"],
  "language": "Language of the document",
  "main_theme": "One sentence describing the core subject"
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=800,
    )
    raw = clean_json_response(response.choices[0].message.content)
    try:
        result = json.loads(raw)
    except Exception:
        result = {
            "summary": "Could not auto-summarise. You can still ask questions below.",
            "doc_type": "Unknown",
            "key_topics": [],
            "language": "Unknown",
            "main_theme": filename,
        }
    result["word_count"] = word_count
    result["filename"] = filename
    return result

def compare_documents(text_a, name_a, text_b, name_b, topic):
    client = get_groq_client()
    prompt = f"""Compare these two documents on the topic: "{topic}"

Document 1 ({name_a}):
{text_a[:2000]}

Document 2 ({name_b}):
{text_b[:2000]}

Give a structured comparison:
1. What Document 1 says about "{topic}"
2. What Document 2 says about "{topic}"
3. Key similarities
4. Key differences
5. Which document covers this topic more thoroughly and why"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",   # ← FIXED: was llama3-70b-8192 (decommissioned)
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=1200,
    )
    return response.choices[0].message.content