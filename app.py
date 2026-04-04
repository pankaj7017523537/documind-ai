import streamlit as st
from src.pdf_processor import process_pdfs, get_raw_text_for_summary
from src.summariser import summarise_document, compare_documents
from src.rag_chain import build_rag_chain, ask_question
from src.quiz_engine import (
    generate_quiz_from_pdf, generate_quiz_from_topic,
    evaluate_quiz, POPULAR_SUBJECTS,
)
from src.utils import get_groq_api_key

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Modern CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif; }

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; }

.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    background-size: 400% 400%;
    animation: gradientShift 15s ease infinite;
}
@keyframes gradientShift {
    0%{background-position:0% 50%}
    50%{background-position:100% 50%}
    100%{background-position:0% 50%}
}

div[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.05) !important;
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255,255,255,0.1);
}
div[data-testid="stSidebar"] * { color: #fff !important; }

.hero-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.3rem;
    line-height: 1.2;
}
.hero-sub {
    font-size: 1.1rem;
    color: rgba(255,255,255,0.6);
    margin-bottom: 2rem;
    font-weight: 300;
}

.feature-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    backdrop-filter: blur(10px);
    height: 100%;
}
.feature-icon { font-size: 2.2rem; margin-bottom: 0.5rem; }
.feature-title { font-size: 1rem; font-weight: 600; color: #fff; margin-bottom: 0.3rem; }
.feature-desc { font-size: 0.82rem; color: rgba(255,255,255,0.55); }

.section-heading {
    font-size: 1.6rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 1rem;
}

.chat-user {
    background: linear-gradient(135deg, rgba(102,126,234,0.25), rgba(118,75,162,0.25));
    border: 1px solid rgba(102,126,234,0.3);
    border-radius: 16px 16px 4px 16px;
    padding: 12px 16px;
    margin: 8px 0;
    color: #fff;
}
.chat-bot {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px 16px 16px 4px;
    padding: 12px 16px;
    margin: 8px 0;
    color: #fff;
}

.summary-card {
    background: rgba(102,126,234,0.12);
    border-left: 4px solid #667eea;
    border-radius: 0 12px 12px 0;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
    color: rgba(255,255,255,0.9);
}

.source-box {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 8px 12px;
    margin-top: 6px;
    font-size: 0.82rem;
    color: rgba(255,255,255,0.6);
}

.q-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 1rem;
    color: #fff;
}

.correct-ans {
    background: rgba(52,211,153,0.2);
    border: 1px solid rgba(52,211,153,0.4);
    border-radius: 8px;
    padding: 4px 12px;
    color: #34d399;
    display: inline-block;
    margin: 3px 0;
}
.wrong-ans {
    background: rgba(248,113,113,0.2);
    border: 1px solid rgba(248,113,113,0.4);
    border-radius: 8px;
    padding: 4px 12px;
    color: #f87171;
    display: inline-block;
    margin: 3px 0;
}
.normal-ans { padding: 4px 12px; display: inline-block; margin: 3px 0; color: rgba(255,255,255,0.7); }

.score-card {
    text-align: center;
    padding: 2rem;
    border-radius: 20px;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(10px);
}

.topic-chip {
    display: inline-block;
    background: rgba(102,126,234,0.2);
    border: 1px solid rgba(102,126,234,0.4);
    color: #a5b4fc;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.78rem;
    font-weight: 500;
    margin: 3px;
}

.stButton > button {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(102,126,234,0.4) !important;
}

.stTextArea textarea, .stTextInput input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    color: #fff !important;
}

div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 1rem;
}
div[data-testid="stMetric"] label { color: rgba(255,255,255,0.6) !important; }
div[data-testid="stMetric"] div { color: #fff !important; }

details {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
}
details summary { color: rgba(255,255,255,0.8) !important; }

.stSelectbox label, .stSlider label, .stFileUploader label,
.stRadio label { color: rgba(255,255,255,0.8) !important; }

div[data-testid="stInfo"] { background: rgba(102,126,234,0.15) !important; border-color: #667eea !important; color: #fff !important; }
div[data-testid="stWarning"] { background: rgba(251,191,36,0.15) !important; color: #fff !important; }
div[data-testid="stError"] { background: rgba(248,113,113,0.15) !important; color: #fff !important; }
div[data-testid="stSuccess"] { background: rgba(52,211,153,0.15) !important; color: #fff !important; }

hr { border-color: rgba(255,255,255,0.1) !important; }

div[data-testid="stProgressBar"] > div > div { background: linear-gradient(90deg, #667eea, #f093fb) !important; }

button[data-baseweb="tab"] { color: rgba(255,255,255,0.6) !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #fff !important; border-bottom-color: #667eea !important; }

p, li, span, div { color: rgba(255,255,255,0.85); }

.sidebar-logo {
    font-size: 1.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea, #f093fb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.sidebar-tagline { font-size: 0.8rem; color: rgba(255,255,255,0.5) !important; }

.nav-section { font-size: 0.7rem; font-weight: 600; color: rgba(255,255,255,0.4) !important; text-transform: uppercase; letter-spacing: 1px; margin: 1rem 0 0.5rem 0; }

.doc-badge {
    background: rgba(102,126,234,0.2);
    border: 1px solid rgba(102,126,234,0.3);
    border-radius: 8px;
    padding: 6px 10px;
    margin-bottom: 6px;
    font-size: 0.82rem;
    color: rgba(255,255,255,0.8) !important;
}

.upload-hint {
    background: rgba(255,255,255,0.04);
    border: 2px dashed rgba(255,255,255,0.15);
    border-radius: 16px;
    padding: 2.5rem;
    text-align: center;
    margin: 1rem 0;
}
.upload-hint-icon { font-size: 3rem; margin-bottom: 0.5rem; }
.upload-hint-text { color: rgba(255,255,255,0.5) !important; font-size: 0.95rem; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "vector_store": None, "all_docs": [], "file_metadata": {},
        "summaries": {}, "rag_chain": None, "chat_history": [],
        "quiz_questions": [], "quiz_answers": {}, "quiz_submitted": False,
        "quiz_results": None, "quiz_mode": None,
        "active_tab": "chat", "processed_files": [],
        "chat_input_buffer": "",
        "topic_subject_default": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🧠 DocuMind AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">Your intelligent document assistant</div>', unsafe_allow_html=True)
    st.divider()

    # Silently validate API key — no success/error shown to user
    api_key = get_groq_api_key()
    if not api_key or api_key == "your_groq_api_key_here":
        st.error("⚠️ GROQ_API_KEY not configured.")
        st.markdown("Get a free key at [console.groq.com](https://console.groq.com)")
        st.stop()

    st.markdown('<div class="nav-section">📂 Documents</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    process_btn = st.button("🚀 Process Documents", use_container_width=True, type="primary")

    if process_btn and uploaded_files:
        file_names = [f.name for f in uploaded_files]
        if file_names != st.session_state.processed_files:
            with st.spinner("📖 Reading and indexing..."):
                vs, docs, meta = process_pdfs(uploaded_files)
                st.session_state.vector_store = vs
                st.session_state.all_docs = docs
                st.session_state.file_metadata = meta
                st.session_state.rag_chain = build_rag_chain(vs)
                st.session_state.chat_history = []
                st.session_state.summaries = {}
                st.session_state.processed_files = file_names

            with st.spinner("✨ Generating summaries..."):
                for f in uploaded_files:
                    raw = get_raw_text_for_summary(docs, f.name)
                    st.session_state.summaries[f.name] = summarise_document(raw, f.name)

            st.success(f"✅ {len(uploaded_files)} document(s) ready!")
            st.rerun()

    if st.session_state.processed_files:
        st.divider()
        st.markdown('<div class="nav-section">📚 Loaded</div>', unsafe_allow_html=True)
        for fname in st.session_state.processed_files:
            pages = st.session_state.file_metadata.get(fname, {}).get("pages", "?")
            st.markdown(f'<div class="doc-badge">📄 {fname[:22]}{"…" if len(fname)>22 else ""} · {pages}p</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="nav-section">🗂️ Navigate</div>', unsafe_allow_html=True)
    if st.button("💬 Q&A Chat",          use_container_width=True): st.session_state.active_tab = "chat"
    if st.button("📋 Document Summary",  use_container_width=True): st.session_state.active_tab = "summary"
    if st.button("🧩 Quiz Mode",          use_container_width=True): st.session_state.active_tab = "quiz"
    if st.button("🔍 Compare Documents", use_container_width=True): st.session_state.active_tab = "compare"

    st.divider()
    st.markdown('<div class="sidebar-tagline" style="text-align:center">Powered by LangChain · Groq · FAISS</div>', unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🧠 DocuMind AI</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Upload PDFs → get instant summaries, ask questions with citations, generate quizzes & compare documents</div>', unsafe_allow_html=True)

if not st.session_state.vector_store:
    st.markdown("""
    <div class="upload-hint">
        <div class="upload-hint-icon">📂</div>
        <div class="upload-hint-text">Upload your PDF documents from the sidebar and click <strong>Process Documents</strong> to get started</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""<div class="feature-card">
            <div class="feature-icon">💬</div>
            <div class="feature-title">Smart Q&A</div>
            <div class="feature-desc">Ask anything with accurate source citations</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="feature-card">
            <div class="feature-icon">📋</div>
            <div class="feature-title">Auto Summary</div>
            <div class="feature-desc">Instant structured summary of every PDF</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class="feature-card">
            <div class="feature-icon">🧩</div>
            <div class="feature-title">Quiz Generator</div>
            <div class="feature-desc">Quiz from PDF or any topic you choose</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown("""<div class="feature-card">
            <div class="feature-icon">🔍</div>
            <div class="feature-title">Doc Compare</div>
            <div class="feature-desc">Compare two documents side by side</div>
        </div>""", unsafe_allow_html=True)
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 – Q&A CHAT
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.active_tab == "chat":
    st.markdown('<div class="section-heading">💬 Ask Anything</div>', unsafe_allow_html=True)

    first_file = st.session_state.processed_files[0] if st.session_state.processed_files else None
    if first_file and first_file in st.session_state.summaries:
        topics = st.session_state.summaries[first_file].get("key_topics", [])
        if topics:
            st.markdown("**💡 Quick topic chips — click to ask:**")
            cols = st.columns(min(len(topics), 5))
            for i, topic in enumerate(topics[:5]):
                with cols[i % 5]:
                    if st.button(f"🔹 {topic}", key=f"chip_{i}"):
                        chip_q = f"Explain {topic} based on the document"
                        st.session_state.chat_history.append({"role": "user", "content": chip_q})
                        with st.spinner(f"🤔 Thinking about '{topic}'..."):
                            result = ask_question(st.session_state.rag_chain, chip_q)
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": result["answer"],
                            "sources": result["sources"],
                        })
                        st.rerun()

    st.divider()

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">👤 <b>You:</b> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bot">🧠 <b>DocuMind:</b></div>', unsafe_allow_html=True)
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("📌 Sources", expanded=False):
                    for src in msg["sources"]:
                        st.markdown(f'<div class="source-box">{src["label"]}<br><em>{src["excerpt"]}...</em></div>', unsafe_allow_html=True)

    st.text_area(
        "Ask a question about your documents:",
        placeholder="e.g. What is the main argument of this document?",
        key="chat_input_widget",
        height=80,
    )

    col_ask, col_clear = st.columns([4, 1])
    with col_ask:
        ask_btn = st.button("🔍 Ask DocuMind", type="primary", use_container_width=True)
    with col_clear:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.rag_chain = build_rag_chain(st.session_state.vector_store)
            st.rerun()

    question = st.session_state.get("chat_input_widget", "").strip()

    if ask_btn and question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.spinner("🤔 Thinking..."):
            result = ask_question(st.session_state.rag_chain, question)
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
        })
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 – SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "summary":
    st.markdown('<div class="section-heading">📋 Document Summaries</div>', unsafe_allow_html=True)

    for fname in st.session_state.processed_files:
        summary = st.session_state.summaries.get(fname, {})
        if not summary:
            continue
        with st.expander(f"📄 {fname}", expanded=True):
            c1, c2, c3 = st.columns(3)
            c1.metric("Document Type", summary.get("doc_type", "—"))
            c2.metric("Word Count",    f"{summary.get('word_count', 0):,}")
            c3.metric("Language",      summary.get("language", "—"))
            st.markdown("---")
            st.markdown("**🎯 Main Theme**")
            st.info(summary.get("main_theme", "—"))
            st.markdown("**📝 Summary**")
            st.markdown(f'<div class="summary-card">{summary.get("summary","—")}</div>', unsafe_allow_html=True)
            topics = summary.get("key_topics", [])
            if topics:
                st.markdown("**🏷️ Key Topics**")
                chips = "".join([f'<span class="topic-chip">{t}</span>' for t in topics])
                st.markdown(chips, unsafe_allow_html=True)
            pages = st.session_state.file_metadata.get(fname, {}).get("pages", 0)
            st.markdown(f"---\n📄 **{pages} pages** indexed and searchable")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 – QUIZ
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "quiz":
    st.markdown('<div class="section-heading">🧩 Quiz Mode</div>', unsafe_allow_html=True)

    if not st.session_state.quiz_questions and not st.session_state.quiz_submitted:
        st.markdown("### Choose how to generate your quiz")
        tab_pdf, tab_topic = st.tabs(["📄 Quiz from Uploaded PDF", "📚 Quiz from Any Topic"])

        with tab_pdf:
            st.markdown("Generate a quiz based on your uploaded documents.")
            selected_file = st.selectbox("Choose document:", st.session_state.processed_files)
            c1, c2 = st.columns(2)
            num_q      = c1.slider("Questions", 5, 20, 10, key="pdf_num_q")
            difficulty = c2.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1, key="pdf_diff")

            if st.button("🎯 Generate PDF Quiz", type="primary", use_container_width=True):
                raw_text = st.session_state.file_metadata.get(selected_file, {}).get("raw_text", "")
                if not raw_text:
                    st.error("Could not extract text from this document.")
                else:
                    with st.spinner("🧠 Generating quiz from document..."):
                        try:
                            questions = generate_quiz_from_pdf(raw_text, num_q, difficulty)
                            if questions:
                                st.session_state.quiz_questions = questions
                                st.session_state.quiz_answers   = {}
                                st.session_state.quiz_submitted = False
                                st.session_state.quiz_results   = None
                                st.session_state.quiz_mode      = f"PDF: {selected_file}"
                                st.rerun()
                            else:
                                st.error("Could not generate quiz. Try a different document.")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

        with tab_topic:
            st.markdown("Generate a quiz on **any subject** — no PDF needed.")
            st.markdown("**🔥 Popular subjects — click to select:**")
            pcols = st.columns(4)
            for i, subj in enumerate(POPULAR_SUBJECTS[:16]):
                with pcols[i % 4]:
                    if st.button(subj, key=f"pop_{i}", use_container_width=True):
                        st.session_state["topic_subject_default"] = subj
                        st.rerun()
            st.markdown("---")
            typed_topic = st.text_area(
                "Selected subject / type any topic:",
                placeholder="e.g. Photosynthesis, French Revolution, React Hooks...",
                value=st.session_state.get("topic_subject_default", ""),
                height=80,
            )
            c1, c2 = st.columns(2)
            num_q_t = c1.slider("Questions", 5, 20, 10, key="topic_num_q")
            diff_t  = c2.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1, key="topic_diff")
            if st.button("🎯 Generate Topic Quiz", type="primary", use_container_width=True):
                chosen = typed_topic.strip()
                if not chosen:
                    st.warning("Please enter a topic or click a subject above.")
                else:
                    with st.spinner(f"🧠 Generating quiz on '{chosen}'..."):
                        try:
                            questions = generate_quiz_from_topic(chosen, num_q_t, diff_t)
                            if questions:
                                st.session_state.quiz_questions = questions
                                st.session_state.quiz_answers   = {}
                                st.session_state.quiz_submitted = False
                                st.session_state.quiz_results   = None
                                st.session_state.quiz_mode      = f"Topic: {chosen}"
                                st.session_state["topic_subject_default"] = ""
                                st.rerun()
                            else:
                                st.error("Could not generate quiz. Please try again.")
                        except Exception as e:
                            st.error(f"Error generating quiz: {str(e)}")

    elif st.session_state.quiz_questions and not st.session_state.quiz_submitted:
        questions = st.session_state.quiz_questions
        st.markdown(f"### 📝 {st.session_state.quiz_mode}")
        st.markdown(f"**{len(questions)} questions** · Select an answer for each question then submit")

        answered = sum(
            1 for i in range(len(questions))
            if st.session_state.quiz_answers.get(i) is not None
        )
        st.progress(
            answered / len(questions) if len(questions) > 0 else 0,
            text=f"Progress: {answered}/{len(questions)} answered"
        )
        st.divider()

        for i, q in enumerate(questions):
            st.markdown(f'<div class="q-card"><b>Q{i+1}. {q["question"]}</b></div>', unsafe_allow_html=True)
            current = st.session_state.quiz_answers.get(i, None)
            options_with_placeholder = ["— Select an answer —"] + q["options"]
            choice = st.radio(
                f"Select answer for Q{i+1}:",
                options=options_with_placeholder,
                index=0 if current is None else options_with_placeholder.index(current) if current in options_with_placeholder else 0,
                key=f"quiz_radio_{i}",
                label_visibility="collapsed",
            )
            if choice != "— Select an answer —":
                st.session_state.quiz_answers[i] = choice
            st.markdown("")

        st.divider()
        c1, c2 = st.columns([3, 1])
        with c1:
            if st.button("✅ Submit Quiz & See Results", type="primary", use_container_width=True):
                final_answers = {}
                for i in range(len(questions)):
                    final_answers[i] = st.session_state.quiz_answers.get(i, questions[i]["options"][0])
                results = evaluate_quiz(questions, final_answers)
                st.session_state.quiz_results   = results
                st.session_state.quiz_answers   = final_answers
                st.session_state.quiz_submitted = True
                st.rerun()
        with c2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.quiz_questions = []
                st.session_state.quiz_answers   = {}
                st.session_state.quiz_submitted = False
                st.rerun()

    elif st.session_state.quiz_submitted and st.session_state.quiz_results:
        r = st.session_state.quiz_results
        color_map = {
            "green":  "rgba(52,211,153,0.15)",
            "blue":   "rgba(102,126,234,0.15)",
            "orange": "rgba(251,191,36,0.15)",
            "red":    "rgba(248,113,113,0.15)"
        }
        bg = color_map.get(r["grade_color"], "rgba(255,255,255,0.08)")

        st.markdown(f"""
        <div class="score-card" style="background:{bg};border:1px solid rgba(255,255,255,0.1)">
          <h1 style="font-size:3.5rem;margin:0;color:#fff">{r['percentage']}%</h1>
          <h2 style="margin:4px 0;color:#fff">{r['grade']}</h2>
          <p style="font-size:1rem;color:rgba(255,255,255,0.6)">{r['correct']} correct out of {r['total']}</p>
          <p style="font-size:0.95rem;color:rgba(255,255,255,0.7)">{r['message']}</p>
        </div>""", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("✅ Correct", r["correct"])
        c2.metric("❌ Wrong",   r["wrong"])
        c3.metric("📊 Score",   f"{r['percentage']}%")

        st.divider()
        st.markdown("### 📖 Detailed Answer Review")

        for i, res in enumerate(r["results"]):
            icon = "✅" if res["is_correct"] else "❌"
            with st.expander(f"{icon} Q{i+1}: {res['question'][:80]}...", expanded=False):
                st.markdown("**Options:**")
                for opt in res["options"]:
                    if opt == res["correct_answer"] and res["is_correct"] and opt == res["user_answer"]:
                        st.markdown(f'<span class="correct-ans">✅ {opt} — Your answer (Correct!)</span>', unsafe_allow_html=True)
                    elif opt == res["correct_answer"]:
                        st.markdown(f'<span class="correct-ans">✅ {opt} — Correct answer</span>', unsafe_allow_html=True)
                    elif opt == res["user_answer"] and not res["is_correct"]:
                        st.markdown(f'<span class="wrong-ans">❌ {opt} — Your answer</span>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<span class="normal-ans">&nbsp;&nbsp;{opt}</span>', unsafe_allow_html=True)
                st.markdown(f"**💡 Explanation:** {res['explanation']}")

        st.divider()
        if st.button("🔄 Take Another Quiz", type="primary", use_container_width=True):
            st.session_state.quiz_questions = []
            st.session_state.quiz_submitted = False
            st.session_state.quiz_results   = None
            st.session_state.quiz_answers   = {}
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 – COMPARE
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "compare":
    st.markdown('<div class="section-heading">🔍 Compare Documents</div>', unsafe_allow_html=True)

    if len(st.session_state.processed_files) < 2:
        st.warning("⚠️ Please upload at least **2 documents** to use comparison mode.")
    else:
        c1, c2 = st.columns(2)
        doc_a = c1.selectbox("Document A:", st.session_state.processed_files, key="doc_a")
        remaining = [f for f in st.session_state.processed_files if f != doc_a]
        doc_b = c2.selectbox("Document B:", remaining, key="doc_b")

        if st.button("🔍 Compare Documents", type="primary", use_container_width=True):
            raw_a = st.session_state.file_metadata.get(doc_a, {}).get("raw_text", "")
            raw_b = st.session_state.file_metadata.get(doc_b, {}).get("raw_text", "")
            if not raw_a or not raw_b:
                st.error("Could not extract text from one or both documents.")
            else:
                with st.spinner("🔍 Comparing documents..."):
                    try:
                        comparison = compare_documents(raw_a, doc_a, raw_b, doc_b)
                        st.markdown("### 📊 Comparison Results")
                        st.markdown(f'<div class="summary-card">{comparison}</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error comparing documents: {str(e)}")