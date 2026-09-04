from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os, re, json, uuid, requests, secrets, time
from datetime import datetime

try:
    from ml_model.predictor import predict as ml_predict
    ML_READY = True
except Exception:
    ml_predict = None
    ML_READY = False

load_dotenv()
ROOT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=".", static_url_path="")
ALLOWED_ORIGINS = [x.strip() for x in os.getenv("ALLOWED_ORIGINS", "").split(",") if x.strip()]
CORS(app, resources={r"/api/*": {"origins": ALLOWED_ORIGINS or "*"}})
app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_REQUEST_BYTES", "16384"))

RATE_LIMIT = int(os.getenv("RATE_LIMIT", "30"))
RATE_WINDOW = int(os.getenv("RATE_WINDOW_SECONDS", "60"))
_rate = {}

def client_key():
    return request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()

def rate_limited():
    now = time.time(); key = client_key(); bucket = _rate.get(key, [])
    bucket = [t for t in bucket if now - t < RATE_WINDOW]
    if len(bucket) >= RATE_LIMIT:
        _rate[key] = bucket
        return True
    bucket.append(now); _rate[key] = bucket
    return False

@app.before_request
def security_gate():
    if request.path.startswith("/api/") and rate_limited():
        return jsonify({"error": "Too many requests. Please try again shortly."}), 429

@app.after_request
def security_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    resp.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if request.path.startswith("/api/"):
        resp.headers["Cache-Control"] = "no-store"
    return resp

AI_API_KEY = os.getenv("AI_API_KEY", "").strip()
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1/chat/completions").strip()
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini").strip()

SESSIONS = {}
CONCEPTS = {
    "inheritance": "Inheritance lets a new class reuse fields and methods of an existing class. The existing class is the parent/superclass and the new class is the child/subclass.",
    "type casting": "Type casting converts a value from one data type to another. Widening is generally automatic; narrowing is explicit and can lose information.",
    "polymorphism": "Polymorphism means one interface or method name can represent different behavior. In Java, method overriding is a common runtime form.",
    "encapsulation": "Encapsulation bundles data and methods together and controls direct access to internal state, commonly using private fields and public methods.",
    "knn": "K-Nearest Neighbors predicts a class by looking at the K closest training examples according to a distance measure.",
    "machine learning": "Machine learning uses data to learn patterns that can be used to make predictions or decisions without writing every rule explicitly.",
    "operating system": "An operating system manages hardware and provides services such as process management, memory management, files, devices, and security.",
    "process": "A process is a program in execution. It has its own execution state and resources managed by the operating system.",
    "data structures": "Data structures organize data so operations such as access, insertion, deletion, and search can be performed efficiently.",
    "python": "Python is a high-level programming language known for readable syntax and a large ecosystem of libraries.",
}

def get_session(sid):
    if not sid or sid not in SESSIONS:
        sid = str(uuid.uuid4())
        SESSIONS[sid] = {"history": [], "mastery": {}, "last_topic": None}
    return sid, SESSIONS[sid]

def detect_intent(text):
    if ML_READY:
        intent, _, confidence, _ = ml_predict(text)
        if confidence >= 0.45:
            return intent
    t = text.lower()
    if any(x in t for x in ["quiz", "test me", "mcq", "questions"]): return "quiz"
    if any(x in t for x in ["study plan", "timetable", "schedule", "prepare for exam"]): return "plan"
    if any(x in t for x in ["simplify", "beginner", "eli5", "simple terms"]): return "simplify"
    if any(x in t for x in ["i don't understand", "dont understand", "confused", "still confused"]): return "remediate"
    return "explain"

def detect_topic(text):
    if ML_READY:
        _, topic, _, confidence = ml_predict(text)
        if confidence >= 0.45:
            return topic
    t = text.lower()
    for k in sorted(CONCEPTS, key=len, reverse=True):
        if k in t: return k
    return None

def fallback_response(text, state):
    intent = detect_intent(text)
    topic = detect_topic(text) or state.get("last_topic") or "this topic"
    state["last_topic"] = topic
    mastery = state["mastery"].get(topic, 0)

    if intent in ("simplify", "remediate"):
        base = CONCEPTS.get(topic, f"I can help you break {topic} into smaller ideas.")
        state["mastery"][topic] = max(0, mastery - 1)
        return f"Let's reset and make it easier.\n\n{base}\n\nThink of it as: **idea → small example → check yourself**.\n\nQuick check: can you explain {topic} in one sentence without using the textbook wording?"

    if intent == "quiz":
        state["mastery"][topic] = min(100, mastery + 5)
        return f"🧠 **StudyMind Micro-Quiz — {topic.title()}**\n\n1. What is the main idea of {topic}?\nA) A random rule\nB) The core concept described above\nC) A hardware component\nD) None of these\n\nReply with **1A/1B/1C/1D**. I’ll use your answer to decide whether the next question should be easier or harder."

    if intent == "plan":
        return "📚 **Adaptive 7-day study plan**\n\nDay 1 — Learn the core concepts\nDay 2 — Work through 3 examples\nDay 3 — Practice without notes\nDay 4 — Take a 10-question diagnostic quiz\nDay 5 — Revisit weak concepts\nDay 6 — Timed exam-style practice\nDay 7 — Final recall test\n\nStudyMind’s difference: your quiz performance can be used to shift more time toward weak concepts instead of giving every topic equal time."

    base = CONCEPTS.get(topic)
    if base:
        state["mastery"][topic] = min(100, mastery + 2)
        return f"**{topic.title()}**\n\n{base}\n\n🔎 **Active recall:** Before I give you another explanation, tell me one example of {topic}. Your answer will determine the next difficulty level."

    return "I can help you learn that. Tell me the subject and topic, and I’ll break it into: **concept → example → active-recall check → adaptive practice**."

def ai_response(text, history, state):
    if not AI_API_KEY:
        return fallback_response(text, state), "adaptive-local"
    system = """You are StudyMind, an adaptive academic tutor. Do not behave like a generic answer bot. For learning questions, explain clearly, then include a short active-recall check. Adjust difficulty based on the student's recent answers. If asked for a quiz, give one question at a time unless explicitly asked otherwise. If asked for a study plan, prioritize weak areas. Be concise and student-friendly. Never claim to have measured mastery unless the backend has evidence."""
    messages = [{"role":"system","content":system}] + history[-10:] + [{"role":"user","content":text}]
    try:
        r = requests.post(AI_BASE_URL, headers={"Authorization":f"Bearer {AI_API_KEY}","Content-Type":"application/json"}, json={"model":AI_MODEL,"messages":messages,"temperature":0.5}, timeout=20)
        r.raise_for_status()
        data = r.json()
        content = data["choices"][0]["message"]["content"]
        return content, "llm"
    except Exception:
        return fallback_response(text, state), "adaptive-local-fallback"

@app.get("/")
def home():
    return send_from_directory(ROOT, "index.html")

@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict): return jsonify({"error":"Invalid JSON body"}), 400
    text = str(data.get("message", "")).strip()
    if not text: return jsonify({"error":"Message is required"}), 400
    if len(text) > 4000: return jsonify({"error":"Message is too long (max 4000 characters)."}), 413
    supplied_sid = str(data.get("session_id", "")).strip()
    if supplied_sid and (len(supplied_sid) > 64 or not re.fullmatch(r"[a-f0-9-]{36}", supplied_sid)):
        return jsonify({"error":"Invalid session_id"}), 400
    sid, state = get_session(supplied_sid)
    reply, engine = ai_response(text, state["history"], state)
    state["history"].append({"role":"user","content":text})
    state["history"].append({"role":"assistant","content":reply})
    intent = detect_intent(text)
    topic = state.get("last_topic")
    ml_confidence = None
    if ML_READY:
        _, _, intent_conf, topic_conf = ml_predict(text)
        ml_confidence = {"intent": round(intent_conf, 3), "topic": round(topic_conf, 3)}
    return jsonify({"session_id":sid,"response":reply,"engine":engine,"intent":intent,"topic":topic,"mastery":state["mastery"],"ml_confidence":ml_confidence})

@app.post("/api/session/new")
def new_session():
    sid = str(uuid.uuid4()); SESSIONS[sid] = {"history": [], "mastery": {}, "last_topic": None}
    return jsonify({"session_id":sid})

@app.get("/api/health")
def health():
    return jsonify({"status":"ok","ai_configured":bool(AI_API_KEY),"ml_model_ready":ML_READY,"time":datetime.utcnow().isoformat()+"Z"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
