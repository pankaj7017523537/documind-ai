import streamlit as st
from src.pdf_processor import process_pdfs, get_raw_text_for_summary
from src.summariser import summarise_document, compare_documents
from src.rag_chain import build_rag_chain, ask_question
from src.quiz_engine import (
    generate_quiz_from_pdf, generate_quiz_from_topic,
    evaluate_quiz, POPULAR_SUBJECTS,
)
from src.utils import get_groq_api_key

st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "vector_store": None, "all_docs": [], "file_metadata": {},
        "summaries": {}, "rag_chain": None, "chat_history": [],
        "quiz_questions": [], "quiz_answers": {}, "quiz_submitted": False,
        "quiz_results": None, "quiz_mode": None,
        "active_tab": "chat", "processed_files": [],
        "topic_subject_default": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🧠 DocuMind AI")
    st.caption("Your intelligent document assistant")
    st.divider()

    api_key = get_groq_api_key()
    if not api_key or api_key == "your_groq_api_key_here":
        st.error("⚠️ GROQ_API_KEY not configured.")
        st.markdown("Get a free key at [console.groq.com](https://console.groq.com)")
        st.stop()

    st.subheader("📂 Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True,
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
    elif process_btn and not uploaded_files:
        st.warning("Please upload at least one PDF first.")

    if st.session_state.processed_files:
        st.divider()
        st.subheader("📚 Loaded Files")
        for fname in st.session_state.processed_files:
            pages = st.session_state.file_metadata.get(fname, {}).get("pages", "?")
            st.markdown(f"📄 **{fname[:25]}** · {pages}p")

    st.divider()
    st.subheader("🗂️ Navigate")
    if st.button("💬 Q&A Chat",          use_container_width=True): st.session_state.active_tab = "chat"
    if st.button("📋 Document Summary",  use_container_width=True): st.session_state.active_tab = "summary"
    if st.button("🧩 Quiz Mode",          use_container_width=True): st.session_state.active_tab = "quiz"
    if st.button("🔍 Compare Documents", use_container_width=True): st.session_state.active_tab = "compare"

    st.divider()
    st.caption("⚡ LangChain · Groq LLaMA 3 · FAISS")

# ── Main Header ───────────────────────────────────────────────────────────────
st.title("🧠 DocuMind AI")
st.markdown("Upload PDFs → instant summaries · smart Q&A · quizzes · document comparison")

if not st.session_state.vector_store:
    st.info("👈 Upload PDF documents from the sidebar and click **Process Documents** to get started.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💬 Smart Q&A", "Ask anything", "with citations")
    c2.metric("📋 Auto Summary", "Instant", "structured")
    c3.metric("🧩 Quiz Generator", "PDF or", "any topic")
    c4.metric("🔍 Doc Compare", "Side by", "side AI")
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 – Q&A CHAT
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.active_tab == "chat":
    st.header("💬 Ask Anything")

    first_file = st.session_state.processed_files[0] if st.session_state.processed_files else None
    if first_file and first_file in st.session_state.summaries:
        topics = st.session_state.summaries[first_file].get("key_topics", [])
        if topics:
            st.markdown("**💡 Quick topics — click to ask:**")
            cols = st.columns(min(len(topics), 5))
            for i, topic in enumerate(topics[:5]):
                with cols[i % 5]:
                    if st.button(f"{topic}", key=f"chip_{i}"):
                        chip_q = f"Explain {topic} based on the document"
                        st.session_state.chat_history.append({"role": "user", "content": chip_q})
                        with st.spinner(f"Thinking about '{topic}'..."):
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
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])
                if msg.get("sources"):
                    with st.expander("📌 Sources"):
                        for src in msg["sources"]:
                            st.caption(f"{src['label']} — {src['excerpt']}...")

    st.text_area("Ask a question:", placeholder="e.g. What is the main argument?", key="chat_input_widget", height=80)
    col_ask, col_clear = st.columns([4, 1])
    with col_ask:
        ask_btn = st.button("🔍 Ask DocuMind", type="primary", use_container_width=True)
    with col_clear:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.rag_chain = build_rag_chain(st.session_state.vector_store)
            st.rerun()

    question = st.session_state.get("chat_input_widget", "").strip()
    if ask_btn and question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.spinner("Thinking..."):
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
    st.header("📋 Document Summaries")

    for fname in st.session_state.processed_files:
        summary = st.session_state.summaries.get(fname, {})
        if not summary:
            continue
        with st.expander(f"📄 {fname}", expanded=True):
            c1, c2, c3 = st.columns(3)
            c1.metric("Type", summary.get("doc_type", "—"))
            c2.metric("Words", f"{summary.get('word_count', 0):,}")
            c3.metric("Language", summary.get("language", "—"))
            st.markdown("**🎯 Main Theme**")
            st.info(summary.get("main_theme", "—"))
            st.markdown("**📝 Summary**")
            st.markdown(summary.get("summary", "—"))
            topics = summary.get("key_topics", [])
            if topics:
                st.markdown("**🏷️ Key Topics:** " + " · ".join(topics))
            pages = st.session_state.file_metadata.get(fname, {}).get("pages", 0)
            st.caption(f"📄 {pages} pages indexed")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 – QUIZ
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "quiz":
    st.header("🧩 Quiz Mode")

    if not st.session_state.quiz_questions and not st.session_state.quiz_submitted:
        tab_pdf, tab_topic = st.tabs(["📄 Quiz from PDF", "📚 Quiz from Any Topic"])

        with tab_pdf:
            st.markdown("Generate a quiz from your uploaded documents.")
            selected_file = st.selectbox("Choose document:", st.session_state.processed_files)
            c1, c2 = st.columns(2)
            num_q = c1.slider("Questions", 5, 20, 10, key="pdf_num_q")
            difficulty = c2.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1, key="pdf_diff")
            if st.button("🎯 Generate PDF Quiz", type="primary", use_container_width=True):
                raw_text = st.session_state.file_metadata.get(selected_file, {}).get("raw_text", "")
                if not raw_text:
                    st.error("Could not extract text from this document.")
                else:
                    with st.spinner("🧠 Generating quiz..."):
                        try:
                            questions = generate_quiz_from_pdf(raw_text, num_q, difficulty)
                            if questions:
                                st.session_state.quiz_questions = questions
                                st.session_state.quiz_answers = {}
                                st.session_state.quiz_submitted = False
                                st.session_state.quiz_results = None
                                st.session_state.quiz_mode = f"PDF: {selected_file}"
                                st.rerun()
                            else:
                                st.error("Could not generate quiz.")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

        with tab_topic:
            st.markdown("Generate a quiz on **any subject** — no PDF needed.")
            st.markdown("**🔥 Popular subjects:**")
            pcols = st.columns(4)
            for i, subj in enumerate(POPULAR_SUBJECTS[:16]):
                with pcols[i % 4]:
                    if st.button(subj, key=f"pop_{i}", use_container_width=True):
                        st.session_state["topic_subject_default"] = subj
                        st.rerun()
            st.divider()
            typed_topic = st.text_area(
                "Type any topic:",
                placeholder="e.g. Photosynthesis, French Revolution...",
                value=st.session_state.get("topic_subject_default", ""),
                height=80,
            )
            c1, c2 = st.columns(2)
            num_q_t = c1.slider("Questions", 5, 20, 10, key="topic_num_q")
            diff_t = c2.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1, key="topic_diff")
            if st.button("🎯 Generate Topic Quiz", type="primary", use_container_width=True):
                chosen = typed_topic.strip()
                if not chosen:
                    st.warning("Please enter a topic.")
                else:
                    with st.spinner(f"🧠 Generating quiz on '{chosen}'..."):
                        try:
                            questions = generate_quiz_from_topic(chosen, num_q_t, diff_t)
                            if questions:
                                st.session_state.quiz_questions = questions
                                st.session_state.quiz_answers = {}
                                st.session_state.quiz_submitted = False
                                st.session_state.quiz_results = None
                                st.session_state.quiz_mode = f"Topic: {chosen}"
                                st.session_state["topic_subject_default"] = ""
                                st.rerun()
                            else:
                                st.error("Could not generate quiz.")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

    elif st.session_state.quiz_questions and not st.session_state.quiz_submitted:
        questions = st.session_state.quiz_questions
        st.markdown(f"### 📝 {st.session_state.quiz_mode}")
        answered = sum(1 for i in range(len(questions)) if st.session_state.quiz_answers.get(i) is not None)
        st.progress(answered / len(questions) if questions else 0, text=f"{answered}/{len(questions)} answered")
        st.divider()

        for i, q in enumerate(questions):
            st.markdown(f"**Q{i+1}. {q['question']}**")
            options_with_placeholder = ["— Select an answer —"] + q["options"]
            current = st.session_state.quiz_answers.get(i, None)
            choice = st.radio(
                f"Q{i+1}",
                options=options_with_placeholder,
                index=0 if current is None else options_with_placeholder.index(current) if current in options_with_placeholder else 0,
                key=f"quiz_radio_{i}",
                label_visibility="collapsed",
            )
            if choice != "— Select an answer —":
                st.session_state.quiz_answers[i] = choice
            st.divider()

        c1, c2 = st.columns([3, 1])
        with c1:
            if st.button("✅ Submit Quiz", type="primary", use_container_width=True):
                final_answers = {i: st.session_state.quiz_answers.get(i, questions[i]["options"][0]) for i in range(len(questions))}
                results = evaluate_quiz(questions, final_answers)
                st.session_state.quiz_results = results
                st.session_state.quiz_answers = final_answers
                st.session_state.quiz_submitted = True
                st.rerun()
        with c2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.quiz_questions = []
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.rerun()

    elif st.session_state.quiz_submitted and st.session_state.quiz_results:
        r = st.session_state.quiz_results
        st.metric("Score", f"{r['percentage']}%", r['grade'])
        c1, c2, c3 = st.columns(3)
        c1.metric("✅ Correct", r["correct"])
        c2.metric("❌ Wrong", r["wrong"])
        c3.metric("📊 Total", r["total"])
        st.info(r['message'])
        st.divider()
        st.markdown("### 📖 Answer Review")
        for i, res in enumerate(r["results"]):
            icon = "✅" if res["is_correct"] else "❌"
            with st.expander(f"{icon} Q{i+1}: {res['question'][:70]}..."):
                for opt in res["options"]:
                    if opt == res["correct_answer"] and opt == res["user_answer"]:
                        st.success(f"✅ {opt} — Your answer (Correct!)")
                    elif opt == res["correct_answer"]:
                        st.success(f"✅ {opt} — Correct answer")
                    elif opt == res["user_answer"] and not res["is_correct"]:
                        st.error(f"❌ {opt} — Your answer")
                    else:
                        st.markdown(f"　{opt}")
                st.info(f"💡 {res['explanation']}")
        st.divider()
        if st.button("🔄 Take Another Quiz", type="primary", use_container_width=True):
            st.session_state.quiz_questions = []
            st.session_state.quiz_submitted = False
            st.session_state.quiz_results = None
            st.session_state.quiz_answers = {}
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 – COMPARE
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "compare":
    st.header("🔍 Compare Documents")

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
                        st.markdown(comparison)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")