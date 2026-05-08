"""
STEP 4 — Flask Deployment
Kapil IT Skill HR Assistant
Modern UI Features:
✔ Dark / Light Toggle
✔ Settings Side Panel (NEW)
✔ New Chat
✔ Search Chats
✔ Recent Chats
✔ Login / Logout Bottom
"""

import os
import sys

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

# ---------------------------------------------------
# IMPORT RAG ENGINE
# ---------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from step3_rag_engine import HRPolicyRAG

# ---------------------------------------------------
# FLASK APP
# ---------------------------------------------------

app = Flask(__name__)
CORS(app)

print("[Flask] Loading HR RAG Engine...")

rag = HRPolicyRAG()

print("[Flask] Ready ✅")

# ---------------------------------------------------
# HTML UI
# ---------------------------------------------------

HTML_UI = r"""
<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Kapil IT Skill</title>

<style>

/* RESET */

*{
  margin:0;
  padding:0;
  box-sizing:border-box;
}

/* BODY */

body{
  font-family:'Segoe UI',sans-serif;
  height:100vh;
  overflow:hidden;
  display:flex;
  transition:0.3s;
}

/* DARK MODE */

body.dark{
  background:#0f172a;
  color:white;
}

/* LIGHT MODE */

body.light{
  background:#f1f5f9;
  color:#111827;
}

/* SIDEBAR */

.sidebar{
  width:300px;
  padding:20px;
  display:flex;
  flex-direction:column;
  border-right:1px solid rgba(255,255,255,0.1);
}

body.dark .sidebar{
  background:#020617;
}

body.light .sidebar{
  background:white;
  border-right:1px solid #d1d5db;
}

/* LOGO */

.logo{
  font-size:2rem;
  font-weight:700;
  color:#38bdf8;
}

.subtitle{
  margin-top:5px;
  margin-bottom:25px;
  color:#94a3b8;
  font-size:14px;
}

/* BUTTONS */

.side-btn{
  padding:14px;
  border:none;
  border-radius:12px;
  cursor:pointer;
  font-size:15px;
  transition:0.2s;
}

.side-btn:hover{
  transform:scale(1.02);
}

.primary{
  background:#2563eb;
  color:white;
  margin-bottom:20px;
}

.secondary{
  background:#1e293b;
  color:white;
}

.logout{
  background:transparent;
  border:1px solid #ef4444;
  color:#ef4444;
}

body.light .secondary{
  background:#e2e8f0;
  color:black;
}

/* SEARCH */

.search-box{
  padding:14px;
  border:none;
  border-radius:12px;
  outline:none;
  font-size:14px;
  margin-bottom:20px;
}

body.dark .search-box{
  background:#111827;
  color:white;
}

body.light .search-box{
  background:#e2e8f0;
}

/* HISTORY */

.history-title{
  margin-bottom:12px;
  font-weight:600;
}

.history{
  flex:1;
  overflow-y:auto;
}

.history-item{
  padding:12px;
  border-radius:10px;
  margin-bottom:10px;
  cursor:pointer;
  font-size:14px;
  transition:0.2s;
}

body.dark .history-item{
  background:#111827;
}

body.light .history-item{
  background:#e2e8f0;
}

.history-item:hover{
  background:#2563eb;
  color:white;
}

/* LOGIN LOGOUT */

.bottom-buttons{
  margin-top:auto;
  padding-top:20px;
}

.logout{
  margin-top:12px;
}

/* MAIN */

.main{
  flex:1;
  display:flex;
  flex-direction:column;
}

/* TOPBAR */

.topbar{
  height:70px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding:0 30px;
  border-bottom:1px solid rgba(255,255,255,0.1);
}

body.dark .topbar{
  background:#111827;
}

body.light .topbar{
  background:white;
  border-bottom:1px solid #d1d5db;
}

.topbar h2{
  font-size:22px;
}

/* TOPBAR RIGHT */

.topbar-right{
  display:flex;
  align-items:center;
  gap:18px;
}

/* STATUS */

.status{
  color:#22c55e;
  font-size:14px;
}

/* SETTINGS ICON */

.settings-icon{
  width:42px;
  height:42px;
  border:none;
  border-radius:50%;
  background:#2563eb;
  color:white;
  font-size:18px;
  cursor:pointer;
  transition:0.25s;
}

.settings-icon:hover{
  background:#1d4ed8;
  transform:rotate(90deg);
}
.theme-toggle{
  display:flex;
  align-items:center;
  justify-content:center;
  gap:12px;
}

.switch{
  position:relative;
  display:inline-block;
  width:60px;
  height:30px;
}

.switch input{
  opacity:0;
  width:0;
  height:0;
}

.slider{
  position:absolute;
  cursor:pointer;
  top:0;
  left:0;
  right:0;
  bottom:0;
  background:#334155;
  transition:.4s;
  border-radius:34px;
}

.slider:before{
  position:absolute;
  content:"";
  height:22px;
  width:22px;
  left:4px;
  bottom:4px;
  background:white;
  transition:.4s;
  border-radius:50%;
}

input:checked + .slider{
  background:#2563eb;
}

input:checked + .slider:before{
  transform:translateX(28px);
}

/* CHAT */

.chat-container{
  flex:1;
  overflow-y:auto;
  padding:30px;
  display:flex;
  flex-direction:column;
  gap:20px;
}

.message{
  max-width:75%;
  padding:16px;
  border-radius:18px;
  line-height:1.6;
}

.user{
  align-self:flex-end;
  background:#2563eb;
  color:white;
  border-bottom-right-radius:5px;
}

.bot{
  align-self:flex-start;
  border-bottom-left-radius:5px;
}

body.dark .bot{
  background:#1e293b;
}

body.light .bot{
  background:white;
  border:1px solid #d1d5db;
}

/* INPUT */

.input-area{
  display:flex;
  gap:15px;
  padding:20px;
  border-top:1px solid rgba(255,255,255,0.1);
}

body.dark .input-area{
  background:#111827;
}

body.light .input-area{
  background:white;
}

.input-area input{
  flex:1;
  padding:16px;
  border:none;
  border-radius:14px;
  outline:none;
  font-size:15px;
}

body.dark .input-area input{
  background:#1e293b;
  color:white;
}

body.light .input-area input{
  background:#e2e8f0;
}

.send-btn{
  background:#2563eb;
  border:none;
  color:white;
  padding:16px 24px;
  border-radius:14px;
  cursor:pointer;
  font-weight:bold;
}

.send-btn:hover{
  background:#1d4ed8;
}

/* NEW SETTINGS SIDE PANEL */

.settings-panel{
  position:fixed;
  top:0;
  right:-420px;
  width:420px;
  height:100%;
  z-index:1000;
  transition:.35s ease;
  padding:28px;
  box-shadow:-10px 0 30px rgba(0,0,0,.25);
}

.settings-panel.open{
  right:0;
}

body.dark .settings-panel{
  background:#0b1220;
  color:white;
}

body.light .settings-panel{
  background:white;
  color:black;
}

.settings-header{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom:30px;
}

.settings-title{
  font-size:26px;
  font-weight:700;
}

.close-settings{
  width:42px;
  height:42px;
  border:none;
  border-radius:50%;
  background:#ef4444;
  color:white;
  cursor:pointer;
  font-size:18px;
}

.setting-card{
  padding:18px;
  border-radius:16px;
  margin-bottom:18px;
}

body.dark .setting-card{
  background:#111827;
}

body.light .setting-card{
  background:#f1f5f9;
}

.setting-row{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom:18px;
}

.setting-row:last-child{
  margin-bottom:0;
}

/* OVERLAY */

.overlay{
  position:fixed;
  inset:0;
  background:rgba(0,0,0,.45);
  display:none;
  z-index:999;
}

.overlay.show{
  display:block;
}

/* SCROLLBAR */

::-webkit-scrollbar{
  width:6px;
}

::-webkit-scrollbar-thumb{
  background:#475569;
  border-radius:10px;
}

</style>
</head>
<body class="dark">

<div class="overlay" id="overlay" onclick="closeSettings()"></div>
<div class="settings-panel" id="settingsPanel">
  <div class="settings-header">
    <div class="settings-title">⚙️ Settings</div>
    <button class="close-settings" onclick="closeSettings()">✕</button>
  </div>

  <div class="setting-card">
    <div class="setting-row">
      <span>Dark / Light Mode</span>
      <label class="switch">
        <input type="checkbox" id="panelTheme" onchange="toggleModeFromPanel()">
        <span class="slider"></span>
      </label>
    </div>
  </div>

  <div class="setting-card">
    <div class="setting-row">
      <span>Notifications</span>
      <input type="checkbox" checked>
    </div>

    <div class="setting-row">
      <span>Privacy Mode</span>
      <input type="checkbox">
    </div>

    <div class="setting-row">
      <span>Account</span>
      <button class="send-btn" style="padding:10px 18px;">Manage</button>
    </div>
  </div>
</div>
<!-- SIDEBAR -->

<div class="sidebar">

  <div class="logo">💼 Kapil IT Skill</div>

  <div class="subtitle">
    Smart HR AI Assistant
  </div>

  <button class="side-btn primary"
          onclick="newChat()">
    ➕ New Chat
  </button>

  <input
    type="text"
    id="searchChat"
    class="search-box"
    placeholder="🔍 Search chats..."
    onkeyup="searchHistory()"
  >

  <div class="history-title">
    🕘 Recent Chats
  </div>

  <div class="history" id="history"></div>

  <div class="bottom-buttons">

    <button class="side-btn secondary"
            onclick="login()">
      🔐 Login
    </button>

    <button class="side-btn logout"
            onclick="logout()">
      🚪 Logout
    </button>

  </div>

</div>

<!-- MAIN -->

<div class="main">

  <div class="topbar">

    <h2>Kapil IT Skill - HR Assistant</h2>

    <div class="topbar-right">

      <div class="theme-toggle">

        <span>🌙</span>

        <label class="switch">
          <input type="checkbox"
                 id="modeToggle"
                 onchange="toggleMode()">
          <span class="slider"></span>
        </label>

        <span>☀️</span>

      </div>

      <div class="status">● AI Online</div>

      <button class="settings-icon"
              onclick="openSettings()">
        ⚙️
      </button>

    </div>

  </div>

  <div class="chat-container" id="chat">

    <div class="message bot">
      👋 Hello! Welcome to Kapil IT Skill HR Assistant.
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

  </div>

  <div class="input-area">

    <input
      type="text"
      id="q"
      placeholder="Ask your HR question..."
      onkeydown="if(event.key==='Enter') askQuestion()"
    >

    <button class="send-btn"
            onclick="askQuestion()">
      Send
    </button>

  </div>

</div>

<script>

let historyData=[];

function addMessage(text,type){
  const msg=document.createElement("div");
  msg.className="message "+type;
  msg.innerHTML=text;
  document.getElementById("chat").appendChild(msg);
  msg.scrollIntoView({behavior:"smooth"});
}

async function askQuestion(){

  const input=document.getElementById("q");
  const query=input.value.trim();

  if(!query) return;

  addMessage(query,"user");
  saveHistory(query);

  input.value="";

  const typing=document.createElement("div");
  typing.className="message bot";
  typing.innerHTML="Typing...";
  document.getElementById("chat").appendChild(typing);

  try{
    const response=await fetch('/ask',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        query:query,
        top_k:3
      })
    });

    const data=await response.json();

    typing.remove();

    addMessage(
      data.answer || "No response found",
      "bot"
    );
  }
  catch(error){
    typing.remove();
    addMessage("Error: "+error.message,"bot");
  }
}

function newChat(){
  document.getElementById("chat").innerHTML=
  `<div class="message bot">👋 New chat started successfully!</div>`;
}

function toggleMode(){

  const body=document.body;
  const toggle=document.getElementById("modeToggle");
  const panelToggle=document.getElementById("panelTheme");

  if(toggle.checked){
    body.classList.remove("dark");
    body.classList.add("light");
    panelToggle.checked=true;
  }else{
    body.classList.remove("light");
    body.classList.add("dark");
    panelToggle.checked=false;
  }
}

function toggleModeFromPanel(){
  const panel=document.getElementById("panelTheme");
  const main=document.getElementById("modeToggle");
  main.checked=panel.checked;
  toggleMode();
}

function openSettings(){
  document.getElementById("settingsPanel").classList.add("open");
  document.getElementById("overlay").classList.add("show");
}

function closeSettings(){
  document.getElementById("settingsPanel").classList.remove("open");
  document.getElementById("overlay").classList.remove("show");
}

function login(){
  alert("Login Successful ✅");
}

function logout(){
  alert("Logout Successful ✅");
}

function saveHistory(text){
  historyData.push(text);
  renderHistory();
}

function renderHistory(){

  const history=document.getElementById("history");
  history.innerHTML="";

  history.slice;

  historyData.slice().reverse().forEach(item=>{

    const div=document.createElement("div");
    div.className="history-item";
    div.innerText=item;

    div.onclick=()=>{
      document.getElementById("q").value=item;
    };

    history.appendChild(div);

  });
}

function searchHistory(){

  const value=document
    .getElementById("searchChat")
    .value
    .toLowerCase();

  const items=document.querySelectorAll(".history-item");

  items.forEach(item=>{
    item.style.display=
      item.innerText.toLowerCase().includes(value)
      ? "block"
      : "none";
  });

}

</script>

</body>
</html>

"""
# ---------------------------------------------------
# ROUTES
# ---------------------------------------------------

@app.route("/")
def home():
    return render_template_string(HTML_UI)


@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json(force=True)

    query = data.get("query", "").strip()

    top_k = int(data.get("top_k", 3))

    if not query:
        return jsonify({
            "error": "Query cannot be empty"
        }), 400

    try:

        result = rag.ask(query, top_k=top_k)

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


@app.route("/health")
def health():

    return jsonify({
        "status": "ok",
        "model": "Kapil IT Skill HR Assistant"
    })


# ---------------------------------------------------
# RUN SERVER
# ---------------------------------------------------

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print(" Kapil IT Skill — HR Assistant ")
    print(" Open Browser → http://127.0.0.1:5000 ")
    print("=" * 60 + "\n")

    app.run(
        debug=False,
        host="0.0.0.0",
        port=5000
    )
