import streamlit as st
from src.pdf_processor import process_pdfs, get_raw_text_for_summary
from src.summariser import summarise_document, compare_documents
from src.rag_chain import build_rag_chain, ask_question
from src.quiz_engine import (
    generate_quiz_from_pdf, generate_quiz_from_topic,
    evaluate_quiz, POPULAR_SUBJECTS,
)
from src.utils import get_groq_api_key

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.main-title{font-size:2.2rem;font-weight:700;color:#185FA5;}
.sub-title{font-size:1rem;color:#666;margin-bottom:1.5rem;}
.summary-card{background:#F0F6FF;border-left:4px solid #185FA5;border-radius:8px;padding:1rem 1.25rem;margin-bottom:1rem;}
.source-box{background:#F8F9FA;border:1px solid #DEE2E6;border-radius:6px;padding:.6rem .9rem;margin-top:4px;font-size:.82rem;color:#555;}
.chat-user{background:#E6F1FB;border-radius:10px;padding:10px 14px;margin:6px 0;}
.chat-bot{background:#F0F4F8;border-radius:10px;padding:10px 14px;margin:6px 0;}
.q-card{background:#FAFAFA;border:1px solid #E0E0E0;border-radius:10px;padding:1.1rem 1.3rem;margin-bottom:1rem;}
.correct-ans{background:#EAF3DE;border-radius:6px;padding:4px 10px;color:#27500A;display:inline-block;margin:3px 0;}
.wrong-ans{background:#FCEBEB;border-radius:6px;padding:4px 10px;color:#791F1F;display:inline-block;margin:3px 0;}
.normal-ans{padding:4px 10px;display:inline-block;margin:3px 0;}
.score-card{text-align:center;padding:1.5rem;border-radius:12px;margin-bottom:1rem;}
.topic-chip{display:inline-block;background:#E6F1FB;color:#0C447C;border-radius:14px;padding:4px 12px;font-size:.78rem;font-weight:500;margin:3px;}
div[data-testid="stSidebar"]{background:#F7F9FC;}
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
        # FIX: Use a separate buffer key — never used as a widget key directly.
        # The text_area widget uses "chat_input_widget"; this buffer is used to
        # pre-populate it (e.g. when a topic chip is clicked).
        "chat_input_buffer": "",
        "topic_subject": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧠 DocuMind AI")
    st.markdown("*Your intelligent document assistant*")
    st.divider()

    api_key = get_groq_api_key()
    if not api_key or api_key == "your_groq_api_key_here":
        st.error("⚠️ GROQ_API_KEY not set")
        st.markdown("Get free key at [console.groq.com](https://console.groq.com)")
        st.stop()
    else:
        st.success("✅ API key connected")

    st.divider()
    st.markdown("#### 📁 Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload one or more PDF files",
        type=["pdf"],
        accept_multiple_files=True,
    )

    process_btn = st.button("🚀 Process Documents", use_container_width=True, type="primary")

    if process_btn and uploaded_files:
        file_names = [f.name for f in uploaded_files]
        if file_names != st.session_state.processed_files:
            with st.spinner("📖 Reading and indexing documents..."):
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
        st.markdown("#### 📚 Loaded Documents")
        for fname in st.session_state.processed_files:
            pages = st.session_state.file_metadata.get(fname, {}).get("pages", "?")
            st.markdown(f"- 📄 **{fname}** ({pages} pages)")

    st.divider()
    st.markdown("#### 🗂️ Navigate")
    if st.button("💬 Q&A Chat",          use_container_width=True): st.session_state.active_tab = "chat"
    if st.button("📋 Document Summary",  use_container_width=True): st.session_state.active_tab = "summary"
    if st.button("🧩 Quiz Mode",          use_container_width=True): st.session_state.active_tab = "quiz"
    if st.button("🔍 Compare Documents", use_container_width=True): st.session_state.active_tab = "compare"

    st.divider()
    st.markdown("<small>LangChain · Groq LLaMA 3 · FAISS · Streamlit</small>", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">🧠 DocuMind AI</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Upload PDFs → summaries, Q&A with citations, quizzes, document comparison</p>', unsafe_allow_html=True)

if not st.session_state.vector_store:
    st.info("👈 Upload PDF documents from the sidebar and click **Process Documents** to get started.")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown("#### 💬 Smart Q&A\nAsk anything with source citations")
    c2.markdown("#### 📋 Auto Summary\nInstant summary of every PDF")
    c3.markdown("#### 🧩 Quiz Generator\nQuiz from PDF or any topic")
    c4.markdown("#### 🔍 Doc Compare\nCompare two documents side by side")
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 – Q&A CHAT
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.active_tab == "chat":
    st.markdown("## 💬 Ask Anything")

    # ── Topic chips ──────────────────────────────────────────────────────────
    # KEY FIX: On click, directly call ask_question and add to chat history.
    # No text area involvement — this avoids ALL session_state widget conflicts
    # and instantly shows the answer without a second manual click.
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

    # ── Chat history ──────────────────────────────────────────────────────────
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

    # Plain text area — key is only ever read, never written to manually
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
        if st.button("🗒️ Clear Chat", use_container_width=True):
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
    st.markdown("## 📋 Document Summaries")

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
    st.markdown("## 🧩 Quiz Mode")

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
                        st.session_state["topic_subject"] = subj
                        st.rerun()

            st.markdown("---")

            st.text_area(
                "Selected subject / type any topic:",
                placeholder="e.g. Photosynthesis, French Revolution, React Hooks...",
                key="topic_subject",
                height=80,
            )

            c1, c2 = st.columns(2)
            num_q_t = c1.slider("Questions", 5, 20, 10, key="topic_num_q")
            diff_t  = c2.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1, key="topic_diff")

            if st.button("🎯 Generate Topic Quiz", type="primary", use_container_width=True):
                chosen = st.session_state.get("topic_subject", "").strip()
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
                                st.session_state["topic_subject"] = ""
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
        color_map = {"green": "#EAF3DE", "blue": "#E6F1FB", "orange": "#FAEEDA", "red": "#FCEBEB"}
        bg = color_map.get(r["grade_color"], "#F0F0F0")

        st.markdown(f"""
        <div class="score-card" style="background:{bg}">
          <h1 style="font-size:3rem;margin:0">{r['percentage']}%</h1>
          <h2 style="margin:4px 0">{r['grade']}</h2>
          <p style="font-size:1rem;color:#555">{r['correct']} correct out of {r['total']}</p>
          <p style="font-size:0.95rem">{r['message']}</p>
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
    st.markdown("## 🔍 Compare Documents")

    if len(st.session_state.processed_files) < 2:
        st.warning("⚠️ Please upload at least **2 documents** to use comparison mode.")
    else:
        c1, c2 = st.columns(2)
        doc_a = c1.selectbox("Document A:", st.session_state.processed_files, key="doc_a")
        remaining = [f for f in st.session_state.processed_files if f != doc_a]
        doc_b = c2.selectbox("Document B:", remaining, key="doc_b")

        compare_topic = st.text_input(
            "Topic to compare:",
            placeholder="e.g. climate change, machine learning...",
        )

        if st.button("🔍 Compare Now", type="primary", use_container_width=True):
            if not compare_topic.strip():
                st.warning("Please enter a topic.")
            else:
                text_a = st.session_state.file_metadata.get(doc_a, {}).get("raw_text", "")
                text_b = st.session_state.file_metadata.get(doc_b, {}).get("raw_text", "")
                with st.spinner(f"Comparing on '{compare_topic}'..."):
                    try:
                        comparison = compare_documents(text_a, doc_a, text_b, doc_b, compare_topic)
                        st.markdown(f"### 📊 Comparison: {compare_topic}")
                        st.markdown("---")
                        st.markdown(comparison)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")