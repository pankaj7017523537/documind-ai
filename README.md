# 🧠 DocuMind AI

> An AI-powered document intelligence app — upload PDFs and instantly get summaries, answers, and quizzes!

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)](https://pankaj7017523537-documind-ai-app-ceqdnn.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.2-green?style=for-the-badge)](https://langchain.com)
[![Groq](https://img.shields.io/badge/Groq-LLM-orange?style=for-the-badge)](https://groq.com)

---

## 🌐 Live Demo

👉 **[Try DocuMind AI Now](https://pankaj7017523537-documind-ai-app-ceqdnn.streamlit.app/)**

---

## ✨ Features

- 📄 **Document Q&A** — Upload PDFs and ask any question, get accurate answers with source references using RAG
- 📝 **Smart Summarization** — Get concise summaries of single or multiple documents instantly
- 🔍 **Document Comparison** — Compare two documents and find key differences and similarities
- 🎯 **Quiz Generator** — Auto-generate quizzes from your uploaded PDFs or any topic you choose
- 🔥 **Topic Quiz** — Generate quizzes on any subject without needing a PDF

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| [Streamlit](https://streamlit.io) | Frontend & Deployment |
| [LangChain](https://langchain.com) | LLM Orchestration & RAG Pipeline |
| [Groq](https://groq.com) | Ultra-fast LLM Inference |
| [FAISS](https://faiss.ai) | Vector Database for Semantic Search |
| [HuggingFace](https://huggingface.co) | Sentence Embeddings (`all-MiniLM-L6-v2`) |
| [PyPDF2](https://pypdf2.readthedocs.io) | PDF Text Extraction |
| [Python 3.11](https://python.org) | Core Language |

---

## 🚀 Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/pankaj7017523537/documind-ai.git
cd documind-ai
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your API key
Create a `.env` file in the root folder:
```
GROQ_API_KEY=your_groq_api_key_here
```
Get your free API key at [console.groq.com](https://console.groq.com)

### 5. Run the app
```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
documind-ai/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml         # Streamlit theme configuration
└── src/
    ├── pdf_processor.py    # PDF loading & vector store creation
    ├── rag_chain.py        # RAG pipeline & question answering
    ├── summariser.py       # Document summarization
    ├── quiz_engine.py      # Quiz generation logic
    └── utils.py            # Utility functions & API key management
```

---

## 📸 How It Works

1. **Upload** one or more PDF documents
2. **Process** — app splits text into chunks and creates vector embeddings
3. **Ask** questions, get **summaries**, or generate a **quiz**
4. Powered by **Groq's ultra-fast LLM** for near-instant responses

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Your Groq API key (get it free at groq.com) |

---

## 👨‍💻 Author

**Pankaj** — Built with ❤️ using Streamlit & LangChain

---

## ⭐ Support

If you found this project useful, please give it a **star** ⭐ on GitHub — it means a lot!
