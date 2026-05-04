"""
STEP 4 — Flask Deployment
Serves the HR RAG assistant as a REST API + web UI.
Run: python app.py  →  http://localhost:5000
"""

import os, sys
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

# Add project root so step3_rag_engine can be imported from anywhere
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from step3_rag_engine import HRPolicyRAG

app = Flask(__name__)
CORS(app)

print("[Flask] Initializing HR RAG engine...")
rag = HRPolicyRAG()
print("[Flask] Ready to serve ✅")

# ─── HTML UI ─────────────────────────────────────────────────────────────────
HTML_UI = r"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HR Policy Assistant</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', sans-serif; background: #f0f4f8; color: #333; }
    header {
      background: linear-gradient(135deg, #1a73e8, #0d47a1);
      color: white; padding: 20px 40px;
      display: flex; align-items: center; gap: 12px;
    }
    header h1 { font-size: 1.5rem; }
    .container { max-width: 860px; margin: 40px auto; padding: 0 20px; }
    .card {
      background: white; border-radius: 12px;
      padding: 28px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin-bottom: 24px;
    }
    .search-bar { display: flex; gap: 10px; }
    input[type=text] {
      flex: 1; padding: 14px 18px; font-size: 1rem;
      border: 2px solid #ddd; border-radius: 8px; outline: none;
      transition: border-color 0.2s;
    }
    input[type=text]:focus { border-color: #1a73e8; }
    button {
      background: #1a73e8; color: white; border: none;
      padding: 14px 24px; font-size: 1rem; border-radius: 8px;
      cursor: pointer; transition: background 0.2s;
    }
    button:hover { background: #1557b0; }
    button:disabled { background: #aaa; cursor: not-allowed; }
    .suggestions { margin-top: 14px; }
    .chip {
      display: inline-block; background: #e8f0fe; color: #1a73e8;
      padding: 6px 14px; border-radius: 20px; font-size: 0.85rem;
      margin: 4px; cursor: pointer; border: 1px solid #c5d8fb;
    }
    .chip:hover { background: #d2e3fc; }
    #result { display: none; }
    .badge {
      display: inline-block; background: #e8f5e9; color: #2e7d32;
      padding: 4px 12px; border-radius: 20px; font-size: 0.82rem;
      font-weight: 600; margin-bottom: 12px;
    }
    .conf { color: #888; font-size: 0.82rem; margin-left: 8px; }
    .answer {
      font-size: 1rem; line-height: 1.75; color: #222;
      white-space: pre-wrap; margin: 12px 0;
    }
    .answer strong { color: #1a73e8; }
    .sources { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
    .src-tag {
      background: #fff3e0; color: #e65100;
      padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;
      border: 1px solid #ffcc80;
    }
    .chunk {
      background: #f8f9fa; border-left: 4px solid #1a73e8;
      padding: 12px 16px; margin-top: 8px; border-radius: 0 8px 8px 0;
      font-size: 0.88rem; color: #555; line-height: 1.6;
    }
    .chunk-src { font-weight: 600; color: #1a73e8; font-size: 0.8rem; }
    .chunk-sc  { float: right; color: #888; font-size: 0.78rem; }
    .loader { text-align: center; padding: 20px; color: #888; display: none; }
    .error  { background: #fce4ec; color: #c62828; padding: 14px; border-radius: 8px; }
    hr.div  { border: none; border-top: 1px solid #eee; margin: 16px 0; }
    h3 { color: #444; font-size: 0.95rem; text-transform: uppercase;
         letter-spacing: 0.5px; margin-bottom: 8px; }
  </style>
</head>
<body>
<header>
  <span style="font-size:2rem">🏢</span>
  <div>
    <h1>HR Policy Assistant</h1>
    <small>Powered by RAG — Retrieval Augmented Generation</small>
  </div>
</header>
<div class="container">
  <div class="card">
    <div class="search-bar">
      <input type="text" id="q" placeholder="Ask an HR policy question..."
             onkeydown="if(event.key==='Enter') ask()">
      <button onclick="ask()" id="btn">Ask</button>
    </div>
    <div class="suggestions">
      <small style="color:#888">Try: </small>
      <span class="chip" onclick="set(this)">How many leave days per year?</span>
      <span class="chip" onclick="set(this)">Can I work from home?</span>
      <span class="chip" onclick="set(this)">What are the working hours?</span>
      <span class="chip" onclick="set(this)">What benefits do employees get?</span>
      <span class="chip" onclick="set(this)">When to submit travel claims?</span>
    </div>
  </div>
  <div class="loader" id="loader">⏳ Searching HR policies...</div>
  <div class="card" id="result">
    <div id="intentBadge"></div>
    <h3>📋 Answer</h3>
    <div class="answer" id="answerText"></div>
    <hr class="div">
    <h3>📄 Sources</h3>
    <div class="sources" id="sourcesDiv"></div>
    <div style="margin-top:16px">
      <h3>🔍 Retrieved Chunks</h3>
      <div id="chunksDiv"></div>
    </div>
  </div>
</div>
<script>
function set(el) { document.getElementById('q').value = el.textContent; ask(); }

async function ask() {
  const query = document.getElementById('q').value.trim();
  if (!query) return;
  document.getElementById('btn').disabled = true;
  document.getElementById('loader').style.display = 'block';
  document.getElementById('result').style.display = 'none';
  try {
    const res  = await fetch('/ask', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({query, top_k: 3})
    });
    const data = await res.json();
    if (data.error) {
      document.getElementById('result').innerHTML = '<div class="error">❌ ' + data.error + '</div>';
    } else {
      document.getElementById('intentBadge').innerHTML =
        '<span class="badge">🎯 ' + data.intent + '</span>' +
        '<span class="conf">Confidence: ' + (data.confidence*100).toFixed(0) + '%</span>';
      document.getElementById('answerText').innerHTML =
        data.answer.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      document.getElementById('sourcesDiv').innerHTML =
        data.sources.map(s => '<span class="src-tag">📑 ' + s + '</span>').join('');
      document.getElementById('chunksDiv').innerHTML =
        data.top_chunks.map(c =>
          '<div class="chunk"><span class="chunk-src">' + c.source + '</span>' +
          '<span class="chunk-sc">Score: ' + c.score.toFixed(3) + '</span>' +
          '<div style="margin-top:4px">' + c.text + '</div></div>'
        ).join('');
    }
    document.getElementById('result').style.display = 'block';
  } catch(e) {
    document.getElementById('result').innerHTML = '<div class="error">❌ ' + e.message + '</div>';
    document.getElementById('result').style.display = 'block';
  } finally {
    document.getElementById('btn').disabled = false;
    document.getElementById('loader').style.display = 'none';
  }
}
</script>
</body>
</html>
"""

# ─── Routes ──────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template_string(HTML_UI)

@app.route("/ask", methods=["POST"])
def ask():
    data  = request.get_json(force=True)
    query = data.get("query", "").strip()
    top_k = int(data.get("top_k", 3))
    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400
    try:
        result = rag.ask(query, top_k=top_k)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    return jsonify({"status": "ok", "model": "HR RAG Assistant"})

@app.route("/policies")
def policies():
    return jsonify({"policies": list(rag.policy_map.keys()),
                    "count": len(rag.policy_map)})

# ─── Entry Point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  HR Policy Assistant — Flask Server")
    print("  Open browser: http://127.0.0.1:5000")
    print("=" * 50 + "\n")
    app.run(debug=False, host="0.0.0.0", port=5000)
