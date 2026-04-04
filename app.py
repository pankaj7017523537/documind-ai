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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

* { font-family: 'Rajdhani', sans-serif; }
#MainMenu, footer { visibility: hidden; }
header { background: transparent !important; }
.block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
.stApp { background: #04060f !important; }

#neural-bg {
    position: fixed; top: 0; left: 0;
    width: 100vw; height: 100vh;
    z-index: 0; pointer-events: none;
}
section[data-testid="stSidebar"], section.main { position: relative; z-index: 1; }

/* ── SIDEBAR TOGGLE always visible ── */
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    z-index: 999999 !important;
}
button[aria-label="Open sidebar"]:hover {
    box-shadow:   0 0 28px rgba(0,212,255,0.9),
                  0 0 56px rgba(245,197,24,0.45) !important;
    transform: scale(1.15) !important;
}

/* ── SIDEBAR ── */
div[data-testid="stSidebar"] {
    background: rgba(4,6,15,0.97) !important;
    border-right: 1px solid rgba(0,212,255,0.1) !important;
    backdrop-filter: blur(30px) !important;
}
div[data-testid="stSidebar"] > div { background: transparent !important; }
div[data-testid="stSidebar"] * { color: #dce8ff !important; }
.main .block-container { background: rgba(4,6,15,0.55); backdrop-filter: blur(10px); }

/* ══════════════════════════════════════════════════════
   GRADIENT NEON BUTTONS — unique gradient per button
   Technique: transparent border + background-clip trick
══════════════════════════════════════════════════════ */
div[data-testid="stButton"] > button {
    position: relative !important;
    width: 100% !important;
    border-radius: 50px !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    padding: 0.6rem 1rem !important;
    background: linear-gradient(#04060f, #04060f) padding-box,
                linear-gradient(135deg, #00D4FF, #0066FF) border-box !important;
    border: 2px solid transparent !important;
    color: #00D4FF !important;
    box-shadow: 0 0 15px rgba(0,212,255,0.4) !important;
    transition: all 0.3s ease !important;
}

div[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 25px rgba(0,212,255,0.8) !important;
    color: #fff !important;
}

/* ── Process Documents: Gold→Magenta ── */
div[data-testid="stSidebar"] .stButton:nth-of-type(1) > button {
    background:
        linear-gradient(#04060f, #04060f) padding-box,
        linear-gradient(135deg, #F5C518 0%, #FF2D78 100%) border-box !important;
    border: 2px solid transparent !important;
    color: #F5C518 !important;
    text-shadow: 0 0 8px rgba(245,197,24,0.85) !important;
    box-shadow: 0 0 14px rgba(245,197,24,0.4), 0 0 30px rgba(255,45,120,0.15) !important;
}
div[data-testid="stSidebar"] .stButton:nth-of-type(1) > button:hover {
    background:
        rgba(245,197,24,0.05) padding-box,
        linear-gradient(135deg, #F5C518, #FF2D78) border-box !important;
    box-shadow: 0 0 28px rgba(245,197,24,0.85), 0 0 55px rgba(255,45,120,0.35) !important;
    color: #fff !important; text-shadow: 0 0 16px #F5C518 !important;
    transform: translateY(-3px) scale(1.04) !important;
}

/* ── Q&A Chat: Cyan→Blue ── */
div[data-testid="stSidebar"] .stButton:nth-of-type(2) > button {
    background:
        linear-gradient(#04060f, #04060f) padding-box,
        linear-gradient(135deg, #00D4FF 0%, #0066FF 100%) border-box !important;
    border: 2px solid transparent !important;
    color: #00D4FF !important;
    text-shadow: 0 0 8px rgba(0,212,255,0.85) !important;
    box-shadow: 0 0 14px rgba(0,212,255,0.4), 0 0 28px rgba(0,102,255,0.12) !important;
}
div[data-testid="stSidebar"] .stButton:nth-of-type(2) > button:hover {
    background: rgba(0,212,255,0.04) padding-box, linear-gradient(135deg, #00D4FF, #0066FF) border-box !important;
    box-shadow: 0 0 28px rgba(0,212,255,0.85), 0 0 55px rgba(0,102,255,0.3) !important;
    color: #fff !important; text-shadow: 0 0 16px #00D4FF !important;
    transform: translateY(-3px) scale(1.04) !important;
}

/* ── Document Summary: Violet→Pink ── */
div[data-testid="stSidebar"] .stButton:nth-of-type(3) > button {
    background:
        linear-gradient(#04060f, #04060f) padding-box,
        linear-gradient(135deg, #BF5FFF 0%, #FF2D78 100%) border-box !important;
    border: 2px solid transparent !important;
    color: #BF5FFF !important;
    text-shadow: 0 0 8px rgba(191,95,255,0.85) !important;
    box-shadow: 0 0 14px rgba(191,95,255,0.4), 0 0 28px rgba(255,45,120,0.12) !important;
}
div[data-testid="stSidebar"] .stButton:nth-of-type(3) > button:hover {
    background: rgba(191,95,255,0.04) padding-box, linear-gradient(135deg, #BF5FFF, #FF2D78) border-box !important;
    box-shadow: 0 0 28px rgba(191,95,255,0.85), 0 0 55px rgba(255,45,120,0.3) !important;
    color: #fff !important; text-shadow: 0 0 16px #BF5FFF !important;
    transform: translateY(-3px) scale(1.04) !important;
}

/* ── Quiz Mode: Green→Cyan ── */
div[data-testid="stSidebar"] .stButton:nth-of-type(4) > button {
    background:
        linear-gradient(#04060f, #04060f) padding-box,
        linear-gradient(135deg, #00FF87 0%, #00D4FF 100%) border-box !important;
    border: 2px solid transparent !important;
    color: #00FF87 !important;
    text-shadow: 0 0 8px rgba(0,255,135,0.85) !important;
    box-shadow: 0 0 14px rgba(0,255,135,0.4), 0 0 28px rgba(0,212,255,0.12) !important;
}
div[data-testid="stSidebar"] .stButton:nth-of-type(4) > button:hover {
    background: rgba(0,255,135,0.04) padding-box, linear-gradient(135deg, #00FF87, #00D4FF) border-box !important;
    box-shadow: 0 0 28px rgba(0,255,135,0.85), 0 0 55px rgba(0,212,255,0.3) !important;
    color: #fff !important; text-shadow: 0 0 16px #00FF87 !important;
    transform: translateY(-3px) scale(1.04) !important;
}

/* ── Compare Documents: Orange→Red ── */
div[data-testid="stSidebar"] .stButton:nth-of-type(5) > button {
    background:
        linear-gradient(#04060f, #04060f) padding-box,
        linear-gradient(135deg, #FF8C00 0%, #FF2D78 100%) border-box !important;
    border: 2px solid transparent !important;
    color: #FF8C00 !important;
    text-shadow: 0 0 8px rgba(255,140,0,0.85) !important;
    box-shadow: 0 0 14px rgba(255,140,0,0.4), 0 0 28px rgba(255,45,120,0.12) !important;
}
div[data-testid="stSidebar"] .stButton:nth-of-type(5) > button:hover {
    background: rgba(255,140,0,0.04) padding-box, linear-gradient(135deg, #FF8C00, #FF2D78) border-box !important;
    box-shadow: 0 0 28px rgba(255,140,0,0.85), 0 0 55px rgba(255,45,120,0.3) !important;
    color: #fff !important; text-shadow: 0 0 16px #FF8C00 !important;
    transform: translateY(-3px) scale(1.04) !important;
}

/* ── Main area primary actions: Gold→Cyan ── */
section.main .stButton > button {
    background:
        linear-gradient(#04060f, #04060f) padding-box,
        linear-gradient(135deg, #F5C518 0%, #00D4FF 100%) border-box !important;
    border: 2px solid transparent !important;
    color: #F5C518 !important;
    text-shadow: 0 0 8px rgba(245,197,24,0.8) !important;
    box-shadow: 0 0 14px rgba(245,197,24,0.35), 0 0 28px rgba(0,212,255,0.12) !important;
}
section.main .stButton > button:hover {
    background: rgba(245,197,24,0.04) padding-box, linear-gradient(135deg, #F5C518, #00D4FF) border-box !important;
    box-shadow: 0 0 28px rgba(245,197,24,0.8), 0 0 55px rgba(0,212,255,0.3) !important;
    color: #fff !important; text-shadow: 0 0 16px #F5C518 !important;
    transform: translateY(-3px) scale(1.04) !important;
}

/* ── Topic chips in horizontal rows: Purple→Cyan ── */
section.main div[data-testid="stHorizontalBlock"] .stButton > button {
    font-size: 0.54rem !important;
    padding: 0.28rem 0.5rem !important;
    background:
        linear-gradient(#04060f, #04060f) padding-box,
        linear-gradient(135deg, #BF5FFF 0%, #00D4FF 100%) border-box !important;
    border: 1.5px solid transparent !important;
    color: #BF5FFF !important;
    text-shadow: 0 0 6px rgba(191,95,255,0.7) !important;
    box-shadow: 0 0 10px rgba(191,95,255,0.28) !important;
}
section.main div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    background: rgba(191,95,255,0.04) padding-box, linear-gradient(135deg, #BF5FFF, #00D4FF) border-box !important;
    box-shadow: 0 0 20px rgba(191,95,255,0.75), 0 0 38px rgba(0,212,255,0.25) !important;
    color: #fff !important; text-shadow: 0 0 12px #BF5FFF !important;
    transform: translateY(-2px) scale(1.03) !important;
}

/* ══════════ HERO ══════════ */
.hero-row { display:flex; align-items:center; gap:16px; margin-bottom:0.3rem; }
.hero-title {
    font-family: 'Orbitron', monospace !important;
    font-size: 2.5rem; font-weight: 900; line-height: 1;
    background: linear-gradient(135deg, #F5C518 0%, #00D4FF 55%, #BF5FFF 100%);
    background-size: 200% auto;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    animation: shimmer 4s linear infinite;
}
@keyframes shimmer { to { background-position: 200% center; } }
.hero-sub { font-size:1rem; color:rgba(200,220,255,0.4) !important; margin-bottom:1.2rem; letter-spacing:0.4px; }
.ai-badge {
    display:inline-flex; align-items:center; gap:6px;
    padding:0.22rem 0.9rem;
    background:rgba(245,197,24,0.06); border:1px solid rgba(245,197,24,0.32);
    border-radius:20px; font-size:0.7rem; color:#F5C518 !important;
    font-weight:600; margin-bottom:0.9rem; letter-spacing:0.5px;
    font-family:'Orbitron',monospace;
}

/* ══════════ FEATURE CARDS — 2-col grid ══════════ */
.feature-grid { display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1.5rem; }
.feature-card {
    border-radius:16px; padding:1.4rem 1.2rem;
    position:relative; overflow:hidden; transition:all 0.35s ease;
}
.feature-card.cyan {
    background: linear-gradient(#04060f,#04060f) padding-box,
                linear-gradient(135deg, rgba(0,212,255,0.45), rgba(0,102,255,0.2)) border-box;
    border:1px solid transparent;
}
.feature-card.purple {
    background: linear-gradient(#04060f,#04060f) padding-box,
                linear-gradient(135deg, rgba(191,95,255,0.45), rgba(255,45,120,0.2)) border-box;
    border:1px solid transparent;
}
.feature-card.green {
    background: linear-gradient(#04060f,#04060f) padding-box,
                linear-gradient(135deg, rgba(0,255,135,0.45), rgba(0,212,255,0.2)) border-box;
    border:1px solid transparent;
}
.feature-card.gold {
    background: linear-gradient(#04060f,#04060f) padding-box,
                linear-gradient(135deg, rgba(245,197,24,0.45), rgba(255,45,120,0.2)) border-box;
    border:1px solid transparent;
}
.feature-card::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; }
.feature-card.cyan::before   { background:linear-gradient(90deg,transparent,#00D4FF,transparent); }
.feature-card.purple::before { background:linear-gradient(90deg,transparent,#BF5FFF,transparent); }
.feature-card.green::before  { background:linear-gradient(90deg,transparent,#00FF87,transparent); }
.feature-card.gold::before   { background:linear-gradient(90deg,transparent,#F5C518,transparent); }
.feature-card:hover { transform:translateY(-5px); }
.feature-card.cyan:hover   { box-shadow:0 14px 42px rgba(0,212,255,0.2); }
.feature-card.purple:hover { box-shadow:0 14px 42px rgba(191,95,255,0.2); }
.feature-card.green:hover  { box-shadow:0 14px 42px rgba(0,255,135,0.2); }
.feature-card.gold:hover   { box-shadow:0 14px 42px rgba(245,197,24,0.2); }
.feature-icon { font-size:1.8rem; margin-bottom:0.5rem; }
.feature-title { font-family:'Orbitron',monospace; font-size:0.76rem; font-weight:700; margin-bottom:0.35rem; }
.feature-title.cyan   { color:#00D4FF !important; }
.feature-title.purple { color:#BF5FFF !important; }
.feature-title.green  { color:#00FF87 !important; }
.feature-title.gold   { color:#F5C518 !important; }
.feature-desc { font-size:0.82rem; color:rgba(200,220,255,0.48) !important; line-height:1.55; }

/* ══════════ MISC ══════════ */
.section-heading {
    font-family:'Orbitron',monospace; font-size:1.35rem; font-weight:800;
    background:linear-gradient(135deg,#F5C518,#00D4FF);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
    margin-bottom:1rem;
}
.glow-line {
    height:1px; border:none;
    background:linear-gradient(90deg,transparent,rgba(245,197,24,0.38),rgba(0,212,255,0.38),transparent);
    margin:1rem 0;
}
.chat-user {
    background:linear-gradient(135deg,rgba(245,197,24,0.08),rgba(255,45,120,0.05));
    border:1px solid rgba(245,197,24,0.18); border-radius:18px 18px 4px 18px;
    padding:12px 18px; margin:10px 0; color:#fff !important;
}
.chat-bot {
    background:rgba(0,212,255,0.05); border:1px solid rgba(0,212,255,0.16);
    border-radius:18px 18px 18px 4px; padding:12px 18px; margin:10px 0; color:#fff !important;
}
.source-box {
    background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06);
    border-radius:8px; padding:8px 14px; margin-top:6px;
    font-size:0.8rem; color:rgba(200,220,255,0.48) !important;
}
.summary-card {
    background:rgba(0,212,255,0.05); border-left:3px solid #00D4FF;
    border-radius:0 12px 12px 0; padding:1rem 1.25rem;
    margin-bottom:1rem; color:rgba(220,240,255,0.82) !important; line-height:1.7;
}
.q-card {
    background:rgba(191,95,255,0.05); border:1px solid rgba(191,95,255,0.17);
    border-radius:14px; padding:1.1rem 1.3rem; margin-bottom:1rem; color:#fff !important;
}
.correct-ans {
    background:rgba(0,255,135,0.1); border:1px solid rgba(0,255,135,0.28);
    border-radius:8px; padding:5px 14px; color:#00FF87 !important; display:inline-block; margin:3px 0;
}
.wrong-ans {
    background:rgba(255,45,120,0.1); border:1px solid rgba(255,45,120,0.28);
    border-radius:8px; padding:5px 14px; color:#FF2D78 !important; display:inline-block; margin:3px 0;
}
.normal-ans { padding:5px 14px; display:inline-block; margin:3px 0; color:rgba(200,220,255,0.5) !important; }
.score-card { text-align:center; padding:2.5rem; border-radius:20px; margin-bottom:1.5rem; backdrop-filter:blur(10px); }
.topic-chip {
    display:inline-block; background:rgba(0,212,255,0.06); border:1px solid rgba(0,212,255,0.22);
    color:#00D4FF !important; border-radius:20px; padding:4px 14px; font-size:0.8rem; margin:3px;
}
.sidebar-logo {
    font-family:'Orbitron',monospace; font-size:1.18rem; font-weight:900;
    background:linear-gradient(135deg,#F5C518,#00D4FF);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.sidebar-tagline { font-size:0.63rem; color:rgba(200,220,255,0.28) !important; }
.nav-section {
    font-family:'Orbitron',monospace; font-size:0.5rem; font-weight:700;
    color:rgba(245,197,24,0.42) !important; text-transform:uppercase; letter-spacing:2.5px; margin:0.6rem 0 0.3rem;
}
.doc-badge {
    background:rgba(0,212,255,0.05); border:1px solid rgba(0,212,255,0.16);
    border-radius:8px; padding:5px 10px; margin-bottom:5px;
    font-size:0.76rem; color:rgba(200,220,255,0.62) !important;
}
.powered-by { font-size:0.56rem; color:rgba(200,220,255,0.16) !important; text-align:center; margin-top:0.5rem; }
.stTextArea textarea, .stTextInput input {
    background:rgba(255,255,255,0.03) !important; border:1px solid rgba(0,212,255,0.16) !important;
    border-radius:10px !important; color:#dce8ff !important; font-family:'Rajdhani',sans-serif !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color:#00D4FF !important; box-shadow:0 0 0 2px rgba(0,212,255,0.1),0 0 14px rgba(0,212,255,0.14) !important;
}
.stTextArea label, .stTextInput label { color:rgba(200,220,255,0.52) !important; }
div[data-testid="stMetric"] {
    background:rgba(255,255,255,0.03); border:1px solid rgba(0,212,255,0.1); border-radius:12px; padding:1rem;
}
div[data-testid="stMetric"] label { color:rgba(200,220,255,0.42) !important; }
div[data-testid="stMetric"] div { color:#dce8ff !important; }
.stSelectbox label,.stSlider label,.stFileUploader label,.stRadio label,.stRadio>div { color:rgba(200,220,255,0.68) !important; }
.stSelectbox>div>div { background:rgba(255,255,255,0.03) !important; border-color:rgba(0,212,255,0.16) !important; color:#dce8ff !important; }
div[data-testid="stInfo"]    { background:rgba(0,212,255,0.07)  !important; border-color:rgba(0,212,255,0.26)  !important; color:#dce8ff !important; }
div[data-testid="stWarning"] { background:rgba(245,197,24,0.07) !important; border-color:rgba(245,197,24,0.26) !important; color:#dce8ff !important; }
div[data-testid="stError"]   { background:rgba(255,45,120,0.07) !important; border-color:rgba(255,45,120,0.26) !important; color:#dce8ff !important; }
div[data-testid="stSuccess"] { background:rgba(0,255,135,0.07)  !important; border-color:rgba(0,255,135,0.26)  !important; color:#dce8ff !important; }
div[data-testid="stProgressBar"]>div>div { background:linear-gradient(90deg,#00D4FF,#BF5FFF) !important; }
button[data-baseweb="tab"] { color:rgba(200,220,255,0.42) !important; font-family:'Orbitron',monospace !important; font-size:0.62rem !important; }
button[data-baseweb="tab"][aria-selected="true"] { color:#F5C518 !important; border-bottom-color:#F5C518 !important; }
hr { border-color:rgba(255,255,255,0.05) !important; }
p,li,span,div,h1,h2,h3,h4,h5 { color:rgba(200,220,255,0.83); }
strong { color:#fff !important; }
details { background:rgba(255,255,255,0.02) !important; border:1px solid rgba(255,255,255,0.06) !important; border-radius:12px !important; }
details summary { color:rgba(200,220,255,0.68) !important; }
</style>

<canvas id="neural-bg"></canvas>
<script>
(function(){
    /* ── Neural network animated canvas ── */
    const canvas = document.getElementById('neural-bg');
    const ctx    = canvas.getContext('2d');
    function resize(){ canvas.width=window.innerWidth; canvas.height=window.innerHeight; }
    resize();
    window.addEventListener('resize', resize);

    const PALETTE = {
        gold:   [245,197,24],
        cyan:   [0,212,255],
        purple: [191,95,255],
    };
    const nodes = Array.from({length:95}, ()=>({
        x:  Math.random()*canvas.width,
        y:  Math.random()*canvas.height,
        vx: (Math.random()-0.5)*0.28,
        vy: (Math.random()-0.5)*0.28,
        r:  Math.random()*2+0.8,
        hue: ['gold','cyan','cyan','purple'][Math.floor(Math.random()*4)],
        phase: Math.random()*Math.PI*2,
    }));

    function draw(){
        ctx.clearRect(0,0,canvas.width,canvas.height);
        const t = Date.now()*0.001;
        /* connections */
        for(let i=0;i<nodes.length;i++){
            for(let j=i+1;j<nodes.length;j++){
                const dx=nodes[i].x-nodes[j].x, dy=nodes[i].y-nodes[j].y;
                const d=Math.sqrt(dx*dx+dy*dy);
                if(d<115){
                    const a=(1-d/115)*0.17;
                    const [r,g,b]=PALETTE[nodes[i].hue];
                    ctx.strokeStyle=`rgba(${r},${g},${b},${a})`;
                    ctx.lineWidth=0.5;
                    ctx.beginPath(); ctx.moveTo(nodes[i].x,nodes[i].y); ctx.lineTo(nodes[j].x,nodes[j].y); ctx.stroke();
                }
            }
        }
        /* nodes */
        for(const n of nodes){
            const pf=0.72+0.28*Math.sin(t*1.4+n.phase);
            const [r,g,b]=PALETTE[n.hue];
            /* halo */
            const gr=ctx.createRadialGradient(n.x,n.y,0,n.x,n.y,n.r*5*pf);
            gr.addColorStop(0,`rgba(${r},${g},${b},0.5)`);
            gr.addColorStop(1,`rgba(${r},${g},${b},0)`);
            ctx.beginPath(); ctx.arc(n.x,n.y,n.r*5*pf,0,Math.PI*2);
            ctx.fillStyle=gr; ctx.fill();
            /* core */
            ctx.beginPath(); ctx.arc(n.x,n.y,n.r*pf,0,Math.PI*2);
            ctx.fillStyle=`rgba(${r},${g},${b},0.92)`; ctx.fill();
            n.x+=n.vx; n.y+=n.vy;
            if(n.x<0||n.x>canvas.width)  n.vx*=-1;
            if(n.y<0||n.y>canvas.height) n.vy*=-1;
        }
        requestAnimationFrame(draw);
    }
    draw();
})();
</script>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "vector_store":None,"all_docs":[],"file_metadata":{},
        "summaries":{},"rag_chain":None,"chat_history":[],
        "quiz_questions":[],"quiz_answers":{},"quiz_submitted":False,
        "quiz_results":None,"quiz_mode":None,
        "active_tab":"chat","processed_files":[],
        "chat_input_buffer":"","topic_subject_default":"",
    }
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k]=v

init_state()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">⬡ DocuMind AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">Intelligent Document Intelligence</div>', unsafe_allow_html=True)
    st.divider()

    api_key = get_groq_api_key()
    if not api_key or api_key == "your_groq_api_key_here":
        st.error("⚠️ GROQ_API_KEY not configured.")
        st.markdown("Get a free key at [console.groq.com](https://console.groq.com)")
        st.stop()

    st.markdown('<div class="nav-section">📂 Documents</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")

    process_btn = st.button("🚀 Process Documents", use_container_width=True)

    if process_btn and uploaded_files:
        file_names = [f.name for f in uploaded_files]
        if file_names != st.session_state.processed_files:
            with st.spinner("📖 Reading and indexing..."):
                vs,docs,meta = process_pdfs(uploaded_files)
                st.session_state.vector_store   = vs
                st.session_state.all_docs       = docs
                st.session_state.file_metadata  = meta
                st.session_state.rag_chain      = build_rag_chain(vs)
                st.session_state.chat_history   = []
                st.session_state.summaries      = {}
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
            pages = st.session_state.file_metadata.get(fname,{}).get("pages","?")
            st.markdown(f'<div class="doc-badge">📄 {fname[:26]}{"…" if len(fname)>26 else ""} · {pages}p</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="nav-section">🗂 Navigate</div>', unsafe_allow_html=True)
    if st.button("💬 Q&A Chat",          use_container_width=True): st.session_state.active_tab="chat";    st.rerun()
    if st.button("📋 Document Summary",  use_container_width=True): st.session_state.active_tab="summary"; st.rerun()
    if st.button("🧩 Quiz Mode",          use_container_width=True): st.session_state.active_tab="quiz";    st.rerun()
    if st.button("🔍 Compare Documents", use_container_width=True): st.session_state.active_tab="compare"; st.rerun()
    st.divider()
    st.markdown('<div class="powered-by">Powered by LangChain · Groq LLaMA 3 · FAISS</div>', unsafe_allow_html=True)

# ── HERO — Neural-network SVG logo + title (no folder icon) ───────────────────
neural_svg = """<svg width="52" height="52" viewBox="0 0 52 52" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="rg1" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#F5C518"/><stop offset="100%" stop-color="#F5C518" stop-opacity="0"/></radialGradient>
    <radialGradient id="rg2" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#00D4FF"/><stop offset="100%" stop-color="#00D4FF" stop-opacity="0"/></radialGradient>
    <radialGradient id="rg3" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#BF5FFF"/><stop offset="100%" stop-color="#BF5FFF" stop-opacity="0"/></radialGradient>
  </defs>
  <!-- edges -->
  <line x1="9" y1="13" x2="26" y2="7"  stroke="#F5C518" stroke-width="0.75" stroke-opacity="0.5"/>
  <line x1="9" y1="13" x2="26" y2="26" stroke="#F5C518" stroke-width="0.75" stroke-opacity="0.35"/>
  <line x1="9" y1="26" x2="26" y2="7"  stroke="#00D4FF" stroke-width="0.75" stroke-opacity="0.35"/>
  <line x1="9" y1="26" x2="26" y2="26" stroke="#00D4FF" stroke-width="0.75" stroke-opacity="0.5"/>
  <line x1="9" y1="39" x2="26" y2="26" stroke="#BF5FFF" stroke-width="0.75" stroke-opacity="0.4"/>
  <line x1="9" y1="39" x2="26" y2="45" stroke="#BF5FFF" stroke-width="0.75" stroke-opacity="0.5"/>
  <line x1="26" y1="7"  x2="43" y2="13" stroke="#F5C518" stroke-width="0.75" stroke-opacity="0.5"/>
  <line x1="26" y1="26" x2="43" y2="13" stroke="#00D4FF" stroke-width="0.75" stroke-opacity="0.4"/>
  <line x1="26" y1="26" x2="43" y2="39" stroke="#BF5FFF" stroke-width="0.75" stroke-opacity="0.5"/>
  <line x1="26" y1="45" x2="43" y2="39" stroke="#BF5FFF" stroke-width="0.75" stroke-opacity="0.4"/>
  <line x1="9"  y1="13" x2="9"  y2="26" stroke="#F5C518" stroke-width="0.55" stroke-opacity="0.28"/>
  <line x1="9"  y1="26" x2="9"  y2="39" stroke="#00D4FF" stroke-width="0.55" stroke-opacity="0.28"/>
  <line x1="43" y1="13" x2="43" y2="39" stroke="#BF5FFF" stroke-width="0.55" stroke-opacity="0.28"/>
  <!-- halos -->
  <circle cx="9"  cy="13" r="5"   fill="url(#rg1)" opacity="0.7"/>
  <circle cx="9"  cy="26" r="5"   fill="url(#rg2)" opacity="0.7"/>
  <circle cx="9"  cy="39" r="5"   fill="url(#rg3)" opacity="0.7"/>
  <circle cx="26" cy="7"  r="5"   fill="url(#rg1)" opacity="0.7"/>
  <circle cx="26" cy="26" r="6.5" fill="url(#rg2)" opacity="0.8"/>
  <circle cx="26" cy="45" r="5"   fill="url(#rg3)" opacity="0.7"/>
  <circle cx="43" cy="13" r="5"   fill="url(#rg1)" opacity="0.7"/>
  <circle cx="43" cy="39" r="5"   fill="url(#rg3)" opacity="0.7"/>
  <!-- cores -->
  <circle cx="9"  cy="13" r="2.2" fill="#F5C518"/>
  <circle cx="9"  cy="26" r="2.2" fill="#00D4FF"/>
  <circle cx="9"  cy="39" r="2.2" fill="#BF5FFF"/>
  <circle cx="26" cy="7"  r="2.2" fill="#F5C518"/>
  <circle cx="26" cy="26" r="2.8" fill="#00D4FF"/>
  <circle cx="26" cy="45" r="2.2" fill="#BF5FFF"/>
  <circle cx="43" cy="13" r="2.2" fill="#F5C518"/>
  <circle cx="43" cy="39" r="2.2" fill="#BF5FFF"/>
</svg>"""

st.markdown(f"""
<div class="ai-badge">⚡ AI-Powered Document Intelligence</div>
<div class="hero-row">
  {neural_svg}
  <span class="hero-title">DocuMind AI</span>
</div>
<div class="hero-sub">Upload PDFs → instant summaries · smart Q&amp;A with citations · auto quizzes · document comparison</div>
""", unsafe_allow_html=True)

# ── Empty state — feature cards only when nothing loaded ───────────────────────
if not st.session_state.vector_store:
    st.markdown("""
    <div style="background:rgba(245,197,24,0.03);border:2px dashed rgba(245,197,24,0.16);
                border-radius:16px;padding:1.8rem;text-align:center;margin-bottom:1.4rem;">
        <div style="font-size:2rem;margin-bottom:0.4rem;">📂</div>
        <div style="color:rgba(200,220,255,0.32);font-size:0.9rem;">
            Upload your PDF documents from the sidebar and click
            <strong style="color:#F5C518;">Process Documents</strong> to get started
        </div>
    </div>
    <div class="feature-grid">
        <div class="feature-card cyan">
            <div class="feature-icon">💬</div>
            <div class="feature-title cyan">Smart Q&amp;A</div>
            <div class="feature-desc">Ask anything — get accurate answers with exact source citations from your documents.</div>
        </div>
        <div class="feature-card purple">
            <div class="feature-icon">📋</div>
            <div class="feature-title purple">Auto Summary</div>
            <div class="feature-desc">Instant structured summary, key topics, doc type and word count for every PDF.</div>
        </div>
        <div class="feature-card green">
            <div class="feature-icon">🧩</div>
            <div class="feature-title green">Quiz Generator</div>
            <div class="feature-desc">Auto-generate quizzes from your PDFs or on any topic — Easy, Medium or Hard.</div>
        </div>
        <div class="feature-card gold">
            <div class="feature-icon">🔍</div>
            <div class="feature-title gold">Doc Compare</div>
            <div class="feature-desc">Compare two documents on any topic you specify — find similarities and differences.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 – Q&A CHAT
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.active_tab == "chat":
    st.markdown('<div class="section-heading">💬 Ask Anything</div>', unsafe_allow_html=True)
    first_file = st.session_state.processed_files[0] if st.session_state.processed_files else None
    if first_file and first_file in st.session_state.summaries:
        topics = st.session_state.summaries[first_file].get("key_topics",[])
        if topics:
            st.markdown("**💡 Quick topic chips — click to ask:**")
            cols = st.columns(min(len(topics),5))
            for i,topic in enumerate(topics[:5]):
                with cols[i%5]:
                    if st.button(f"🔹 {topic}", key=f"chip_{i}"):
                        chip_q = f"Explain {topic} based on the document"
                        st.session_state.chat_history.append({"role":"user","content":chip_q})
                        with st.spinner(f"🤔 Thinking about '{topic}'..."):
                            result = ask_question(st.session_state.rag_chain, chip_q)
                        st.session_state.chat_history.append({"role":"assistant","content":result["answer"],"sources":result["sources"]})
                        st.rerun()
    st.markdown('<hr class="glow-line">', unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        if msg["role"]=="user":
            st.markdown(f'<div class="chat-user">👤 <b>You:</b> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="chat-bot">🧠 <b>DocuMind:</b></div>', unsafe_allow_html=True)
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("📌 Sources", expanded=False):
                    for src in msg["sources"]:
                        st.markdown(f'<div class="source-box">{src["label"]}<br><em>{src["excerpt"]}...</em></div>', unsafe_allow_html=True)
    st.text_area("Ask a question:", placeholder="e.g. What is the main argument of this document?", key="chat_input_widget", height=80)
    col_ask,col_clear = st.columns([4,1])
    with col_ask:
        ask_btn = st.button("🔍 Ask DocuMind", use_container_width=True)
    with col_clear:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.chat_history=[]
            st.session_state.rag_chain=build_rag_chain(st.session_state.vector_store)
            st.rerun()
    question = st.session_state.get("chat_input_widget","").strip()
    if ask_btn and question:
        st.session_state.chat_history.append({"role":"user","content":question})
        with st.spinner("🤔 Thinking..."):
            result = ask_question(st.session_state.rag_chain, question)
        st.session_state.chat_history.append({"role":"assistant","content":result["answer"],"sources":result["sources"]})
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 – SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "summary":
    st.markdown('<div class="section-heading">📋 Document Summaries</div>', unsafe_allow_html=True)
    for fname in st.session_state.processed_files:
        summary = st.session_state.summaries.get(fname,{})
        if not summary: continue
        with st.expander(f"📄 {fname}", expanded=True):
            c1,c2,c3 = st.columns(3)
            c1.metric("Document Type", summary.get("doc_type","—"))
            c2.metric("Word Count",    f"{summary.get('word_count',0):,}")
            c3.metric("Language",      summary.get("language","—"))
            st.markdown('<hr class="glow-line">', unsafe_allow_html=True)
            st.markdown("**🎯 Main Theme**"); st.info(summary.get("main_theme","—"))
            st.markdown("**📝 Summary**")
            st.markdown(f'<div class="summary-card">{summary.get("summary","—")}</div>', unsafe_allow_html=True)
            topics = summary.get("key_topics",[])
            if topics:
                st.markdown("**🏷️ Key Topics**")
                st.markdown("".join([f'<span class="topic-chip">{t}</span>' for t in topics]), unsafe_allow_html=True)
            pages = st.session_state.file_metadata.get(fname,{}).get("pages",0)
            st.markdown(f"---\n📄 **{pages} pages** indexed and searchable")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 – QUIZ
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "quiz":
    st.markdown('<div class="section-heading">🧩 Quiz Mode</div>', unsafe_allow_html=True)
    if not st.session_state.quiz_questions and not st.session_state.quiz_submitted:
        tab_pdf,tab_topic = st.tabs(["📄 Quiz from Uploaded PDF","📚 Quiz from Any Topic"])
        with tab_pdf:
            st.markdown("Generate a quiz based on your uploaded documents.")
            selected_file = st.selectbox("Choose document:", st.session_state.processed_files)
            c1,c2 = st.columns(2)
            num_q      = c1.slider("Questions",5,20,10,key="pdf_num_q")
            difficulty = c2.selectbox("Difficulty",["Easy","Medium","Hard"],index=1,key="pdf_diff")
            if st.button("🎯 Generate PDF Quiz", use_container_width=True):
                raw_text = st.session_state.file_metadata.get(selected_file,{}).get("raw_text","")
                if not raw_text:
                    st.error("Could not extract text from this document.")
                else:
                    with st.spinner("🧠 Generating quiz from document..."):
                        try:
                            questions = generate_quiz_from_pdf(raw_text, num_q, difficulty)
                            if questions:
                                st.session_state.quiz_questions=questions; st.session_state.quiz_answers={}
                                st.session_state.quiz_submitted=False; st.session_state.quiz_results=None
                                st.session_state.quiz_mode=f"PDF: {selected_file}"; st.rerun()
                            else: st.error("Could not generate quiz. Try a different document.")
                        except Exception as e: st.error(f"Error: {str(e)}")
        with tab_topic:
            st.markdown("Generate a quiz on **any subject** — no PDF needed.")
            st.markdown("**🔥 Popular subjects — click to select:**")
            pcols = st.columns(4)
            for i,subj in enumerate(POPULAR_SUBJECTS[:16]):
                with pcols[i%4]:
                    if st.button(subj, key=f"pop_{i}", use_container_width=True):
                        st.session_state["topic_subject_default"]=subj; st.rerun()
            st.markdown("---")
            typed_topic = st.text_area("Selected subject / type any topic:",
                placeholder="e.g. Photosynthesis, French Revolution, React Hooks...",
                value=st.session_state.get("topic_subject_default",""), height=80)
            c1,c2 = st.columns(2)
            num_q_t = c1.slider("Questions",5,20,10,key="topic_num_q")
            diff_t  = c2.selectbox("Difficulty",["Easy","Medium","Hard"],index=1,key="topic_diff")
            if st.button("🎯 Generate Topic Quiz", use_container_width=True):
                chosen = typed_topic.strip()
                if not chosen: st.warning("Please enter a topic or click a subject above.")
                else:
                    with st.spinner(f"🧠 Generating quiz on '{chosen}'..."):
                        try:
                            questions = generate_quiz_from_topic(chosen, num_q_t, diff_t)
                            if questions:
                                st.session_state.quiz_questions=questions; st.session_state.quiz_answers={}
                                st.session_state.quiz_submitted=False; st.session_state.quiz_results=None
                                st.session_state.quiz_mode=f"Topic: {chosen}"
                                st.session_state["topic_subject_default"]=""; st.rerun()
                            else: st.error("Could not generate quiz. Please try again.")
                        except Exception as e: st.error(f"Error generating quiz: {str(e)}")

    elif st.session_state.quiz_questions and not st.session_state.quiz_submitted:
        questions = st.session_state.quiz_questions
        st.markdown(f"### 📝 {st.session_state.quiz_mode}")
        st.markdown(f"**{len(questions)} questions** · Select an answer for each then submit")
        answered = sum(1 for i in range(len(questions)) if st.session_state.quiz_answers.get(i) is not None)
        st.progress(answered/len(questions) if len(questions)>0 else 0, text=f"Progress: {answered}/{len(questions)} answered")
        st.divider()
        for i,q in enumerate(questions):
            st.markdown(f'<div class="q-card"><b>Q{i+1}. {q["question"]}</b></div>', unsafe_allow_html=True)
            current = st.session_state.quiz_answers.get(i,None)
            opts = ["— Select an answer —"]+q["options"]
            choice = st.radio(f"Q{i+1}:", options=opts,
                index=0 if current is None else (opts.index(current) if current in opts else 0),
                key=f"quiz_radio_{i}", label_visibility="collapsed")
            if choice!="— Select an answer —": st.session_state.quiz_answers[i]=choice
        st.divider()
        c1,c2 = st.columns([3,1])
        with c1:
            if st.button("✅ Submit Quiz & See Results", use_container_width=True):
                final = {i:st.session_state.quiz_answers.get(i,questions[i]["options"][0]) for i in range(len(questions))}
                results = evaluate_quiz(questions, final)
                st.session_state.quiz_results=results; st.session_state.quiz_answers=final
                st.session_state.quiz_submitted=True; st.rerun()
        with c2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.quiz_questions=[]; st.session_state.quiz_answers={}
                st.session_state.quiz_submitted=False; st.rerun()

    elif st.session_state.quiz_submitted and st.session_state.quiz_results:
        r=st.session_state.quiz_results
        cmap={"green":"rgba(0,255,135,0.08)","blue":"rgba(0,212,255,0.08)","orange":"rgba(245,197,24,0.08)","red":"rgba(255,45,120,0.08)"}
        bg=cmap.get(r["grade_color"],"rgba(255,255,255,0.04)")
        st.markdown(f"""<div class="score-card" style="background:{bg};border:1px solid rgba(255,255,255,0.07)">
          <h1 style="font-size:4rem;margin:0;color:#fff;font-family:'Orbitron',monospace">{r['percentage']}%</h1>
          <h2 style="margin:6px 0;color:#F5C518;font-family:'Orbitron',monospace">{r['grade']}</h2>
          <p style="color:rgba(200,220,255,0.48)">{r['correct']} correct out of {r['total']}</p>
          <p style="color:rgba(200,220,255,0.62)">{r['message']}</p>
        </div>""", unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        c1.metric("✅ Correct",r["correct"]); c2.metric("❌ Wrong",r["wrong"]); c3.metric("📊 Score",f"{r['percentage']}%")
        st.divider(); st.markdown("### 📖 Detailed Answer Review")
        for i,res in enumerate(r["results"]):
            icon="✅" if res["is_correct"] else "❌"
            with st.expander(f"{icon} Q{i+1}: {res['question'][:80]}...", expanded=False):
                for opt in res["options"]:
                    if opt==res["correct_answer"] and res["is_correct"] and opt==res["user_answer"]:
                        st.markdown(f'<span class="correct-ans">✅ {opt} — Your answer (Correct!)</span>', unsafe_allow_html=True)
                    elif opt==res["correct_answer"]:
                        st.markdown(f'<span class="correct-ans">✅ {opt} — Correct answer</span>', unsafe_allow_html=True)
                    elif opt==res["user_answer"] and not res["is_correct"]:
                        st.markdown(f'<span class="wrong-ans">❌ {opt} — Your answer</span>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<span class="normal-ans">  {opt}</span>', unsafe_allow_html=True)
                st.markdown(f"**💡 Explanation:** {res['explanation']}")
        st.divider()
        if st.button("🔄 Take Another Quiz", use_container_width=True):
            st.session_state.quiz_questions=[]; st.session_state.quiz_submitted=False
            st.session_state.quiz_results=None; st.session_state.quiz_answers={}; st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 – COMPARE  ← FIX: manual topic text field + correct function call
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "compare":
    st.markdown('<div class="section-heading">🔍 Compare Documents</div>', unsafe_allow_html=True)
    if len(st.session_state.processed_files) < 2:
        st.warning("⚠️ Please upload at least **2 documents** to use comparison mode.")
    else:
        c1,c2 = st.columns(2)
        doc_a     = c1.selectbox("Document A:", st.session_state.processed_files, key="doc_a")
        remaining = [f for f in st.session_state.processed_files if f!=doc_a]
        doc_b     = c2.selectbox("Document B:", remaining, key="doc_b")

        # ── Manual topic input (was missing — caused the blank + missing-arg error) ──
        st.markdown("""
        <div style="margin:0.8rem 0 0.3rem;font-size:0.82rem;color:rgba(200,220,255,0.55);">
            🎯 <strong style="color:#F5C518;">Comparison Focus Topic</strong>
            <span style="color:rgba(200,220,255,0.35);font-size:0.75rem;"> — optional, leave blank for a general comparison</span>
        </div>""", unsafe_allow_html=True)
        compare_topic = st.text_input(
            label="Comparison topic",
            placeholder="e.g. Machine Learning methods · climate change policy · financial risk · key arguments ...",
            label_visibility="collapsed",
            key="compare_topic_input",
        )

        if st.button("🔍 Compare Documents", use_container_width=True):
            raw_a = st.session_state.file_metadata.get(doc_a,{}).get("raw_text","")
            raw_b = st.session_state.file_metadata.get(doc_b,{}).get("raw_text","")
            if not raw_a or not raw_b:
                st.error("Could not extract text from one or both documents.")
            else:
                # Build topic — user input or auto-generated fallback
                topic_str = compare_topic.strip() if compare_topic.strip() else \
                            f"general comparison between '{doc_a}' and '{doc_b}'"
                with st.spinner(f"🔍 Comparing on: *{topic_str}*..."):
                    try:
                        comparison = compare_documents(raw_a, doc_a, raw_b, doc_b, topic_str)
                        st.markdown("### 📊 Comparison Results")
                        st.markdown(f'<div class="summary-card">{comparison}</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error comparing documents: {str(e)}")