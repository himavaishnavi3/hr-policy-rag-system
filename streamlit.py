import streamlit as st
import streamlit.components.v1 as components
import os
import sys

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Kit Skill Hub",
    page_icon="🤖",
    layout="wide"
)

# =========================================================
# IMPORT RAG ENGINE
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, BASE_DIR)

from step3_rag_engine import HRPolicyRAG

# =========================================================
# LOAD RAG
# =========================================================

@st.cache_resource
def load_rag():
    return HRPolicyRAG()

rag = load_rag()

# =========================================================
# HANDLE QUERY
# =========================================================

query = st.query_params.get("query", "")

answer = ""

if query:

    try:

        result = rag.ask(query, top_k=3)

        answer = result.get("answer", "No answer found.")

    except Exception as e:

        answer = f"Error: {str(e)}"

# =========================================================
# HTML UI
# =========================================================

HTML_UI = f"""

<!DOCTYPE html>
<html>

<head>

<style>

*{{
margin:0;
padding:0;
box-sizing:border-box;
}}

body{{
font-family:Segoe UI;
background:#0f172a;
color:white;
height:100vh;
display:flex;
overflow:hidden;
}}

.sidebar{{
width:300px;
background:#020617;
padding:20px;
display:flex;
flex-direction:column;
border-right:1px solid rgba(255,255,255,0.1);
}}

.logo-text{{
font-size:32px;
font-weight:bold;
color:#38bdf8;
margin-bottom:8px;
}}

.subtitle{{
color:#94a3b8;
margin-bottom:30px;
}}

.side-btn{{
padding:14px;
border:none;
border-radius:12px;
cursor:pointer;
font-size:15px;
margin-bottom:15px;
}}

.primary{{
background:#2563eb;
color:white;
}}

.secondary{{
background:#1e293b;
color:white;
}}

.logout{{
border:1px solid #ef4444;
background:transparent;
color:#ef4444;
}}

.search-box{{
padding:14px;
border:none;
border-radius:12px;
background:#111827;
color:white;
margin-bottom:20px;
}}

.history-title{{
margin-bottom:10px;
}}

.history{{
flex:1;
overflow-y:auto;
}}

.history-item{{
background:#111827;
padding:12px;
border-radius:10px;
margin-bottom:10px;
}}

.main{{
flex:1;
display:flex;
flex-direction:column;
}}

.topbar{{
height:70px;
background:#111827;
display:flex;
align-items:center;
justify-content:space-between;
padding:0 30px;
border-bottom:1px solid rgba(255,255,255,0.1);
}}

.status{{
color:#22c55e;
}}

.chat-container{{
flex:1;
padding:30px;
overflow-y:auto;
display:flex;
flex-direction:column;
gap:20px;
}}

.message{{
padding:16px;
border-radius:18px;
max-width:75%;
line-height:1.6;
}}

.user{{
background:#2563eb;
align-self:flex-end;
}}

.bot{{
background:#1e293b;
align-self:flex-start;
}}

.input-area{{
display:flex;
gap:15px;
padding:20px;
background:#111827;
}}

.input-area input{{
flex:1;
padding:16px;
border:none;
border-radius:14px;
background:#1e293b;
color:white;
}}

.send-btn{{
background:#2563eb;
color:white;
border:none;
padding:16px 24px;
border-radius:14px;
cursor:pointer;
}}

.switch{{
position:relative;
display:inline-block;
width:60px;
height:30px;
}}

.switch input{{
opacity:0;
width:0;
height:0;
}}

.slider{{
position:absolute;
cursor:pointer;
top:0;
left:0;
right:0;
bottom:0;
background:#334155;
transition:.4s;
border-radius:34px;
}}

.slider:before{{
position:absolute;
content:"";
height:22px;
width:22px;
left:4px;
bottom:4px;
background:white;
transition:.4s;
border-radius:50%;
}}

input:checked + .slider{{
background:#2563eb;
}}

input:checked + .slider:before{{
transform:translateX(28px);
}}

.settings-btn{{
background:#2563eb;
border:none;
width:42px;
height:42px;
border-radius:12px;
color:white;
font-size:18px;
cursor:pointer;
}}

.topbar-right{{
display:flex;
align-items:center;
gap:18px;
}}

.theme-toggle{{
display:flex;
align-items:center;
gap:10px;
}}

</style>

</head>

<body>

<div class="sidebar">

<div class="logo-text">
Kit Skill Hub
</div>

<div class="subtitle">
Smart HR AI Assistant
</div>

<button class="side-btn primary" onclick="newChat()">
➕ New Chat
</button>

<input
type="text"
class="search-box"
placeholder="🔍 Search chats..."
>

<div class="history-title">
🕘 Recent Chats
</div>

<div class="history" id="history"></div>

<div style="margin-top:auto;">

<button class="side-btn secondary">
🔐 Login
</button>

<button class="side-btn logout">
🚪 Logout
</button>

</div>

</div>

<div class="main">

<div class="topbar">

<h2>
Kit Skill Hub - HR Assistant
</h2>

<div class="topbar-right">

<div class="theme-toggle">

<span>🌙</span>

<label class="switch">

<input type="checkbox">

<span class="slider"></span>

</label>

<span>☀️</span>

</div>

<div class="status">
● AI Online
</div>

<button class="settings-btn">
⚙️
</button>

</div>

</div>

<div class="chat-container" id="chat">

<div class="message bot">

👋 Hello! Welcome to Kit Skill Hub HR Assistant.

<br><br>

Ask me anything about:

<br><br>

• HR Policies<br>
• Leave Rules<br>
• Attendance<br>
• Holidays<br>
• Salary<br>
• Work From Home

</div>

{"<div class='message user'>" + query + "</div>" if query else ""}

{"<div class='message bot'>" + answer + "</div>" if answer else ""}

</div>

<div class="input-area">

<input
type="text"
id="q"
placeholder="Ask your HR question..."
onkeydown="if(event.key==='Enter') askQuestion()"
>

<button class="send-btn" onclick="askQuestion()">
Send
</button>

</div>

</div>

<script>

let historyData=[];

function askQuestion(){{

const query=document.getElementById("q").value;

if(!query) return;

window.location.href =
"http://localhost:8501/?query=" + encodeURIComponent(query);

}}

function newChat(){{
window.location.href="http://localhost:8501";
}}

</script>

</body>
</html>

"""

# =========================================================
# DISPLAY HTML
# =========================================================

components.html(
    HTML_UI,
    height=1000,
    scrolling=True
)