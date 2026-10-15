
import json
import re
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from io import BytesIO
from html import escape

import ollama
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, PageBreak
)
from docx import Document
from docx.shared import Inches, Pt, RGBColor


# ============================================================
# 1. PROJECT CONFIGURATION
# ============================================================

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent
OUTPUT_DIR = PROJECT_DIR / "outputs"
DATA_DIR = PROJECT_DIR / "data"
DB_PATH = DATA_DIR / "trendpilot_memory.db"

MODEL_NAME = "qwen2.5:3b"
OLLAMA_HOST = "http://localhost:11434"
MAX_HISTORY_TURNS = 12

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
client = ollama.Client(host=OLLAMA_HOST)

st.set_page_config(
    page_title="TrendPilot | AI Content Studio",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# 2. STYLING: COMPACT, CHATGPT-LIKE, SINGLE VIEWPORT
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root {
  --bg:#080d19; --panel:rgba(17,26,45,.92); --line:rgba(135,160,205,.22);
  --cyan:#67e8f9; --muted:#9eacc4; --text:#eef4ff;
}
html, body, [data-testid="stAppViewContainer"] {
  background:var(--bg); color:var(--text); font-family:Inter,sans-serif;
}
[data-testid="stAppViewContainer"] { isolation:isolate; position:relative; }
[data-testid="stAppViewContainer"]::before {
  content:""; position:fixed; inset:-25%; z-index:-2; pointer-events:none;
  background:
    radial-gradient(ellipse at 12% 15%,rgba(37,99,235,.24),transparent 35%),
    radial-gradient(ellipse at 82% 25%,rgba(124,58,237,.20),transparent 35%),
    radial-gradient(ellipse at 52% 90%,rgba(8,145,178,.14),transparent 38%);
  animation:aurora 18s ease-in-out infinite alternate;
}
[data-testid="stAppViewContainer"]::after {
  content:""; position:fixed; inset:0; z-index:-1; pointer-events:none; opacity:.13;
  background-image:linear-gradient(rgba(148,163,184,.08) 1px,transparent 1px),
    linear-gradient(90deg,rgba(148,163,184,.08) 1px,transparent 1px);
  background-size:46px 46px;
}
@keyframes aurora { from{transform:translate(-1%,-1%) scale(1)}
to{transform:translate(2%,1%) scale(1.08)} }
#MainMenu, footer, [data-testid="stToolbar"] {visibility:hidden;}
[data-testid="stHeader"] {background:transparent;height:0;}
.block-container {max-width:1900px;padding-top:.65rem;padding-bottom:.45rem;}
.hero {
  padding:.85rem 1.15rem; margin-bottom:.75rem; border:1px solid var(--line);
  border-radius:17px; background:linear-gradient(120deg,rgba(15,23,42,.97),rgba(20,31,57,.9));
  display:flex; align-items:center; justify-content:space-between; gap:1rem;
}
.brand {font-size:1.65rem;font-weight:800;letter-spacing:-.8px;color:#f8fbff;}
.brand span {color:var(--cyan);text-shadow:0 0 20px rgba(103,232,249,.28);}
.subtitle {font-size:.76rem;color:var(--muted);margin-top:.15rem;}
.status-pill {border:1px solid rgba(103,232,249,.3);border-radius:99px;padding:5px 9px;
  color:#a5f3fc;background:rgba(8,145,178,.12);font-size:.65rem;font-weight:700;white-space:nowrap;}
.panel {border:1px solid var(--line);border-radius:15px;padding:.85rem;background:var(--panel);
  box-shadow:0 10px 30px rgba(0,0,0,.14);margin-bottom:.6rem;}
.panel-heading {font-size:.98rem;font-weight:750;color:var(--cyan);margin-bottom:.2rem;}
.panel-caption {font-size:.74rem;color:var(--muted);margin-bottom:.55rem;}
.section-card {border:1px solid rgba(113,145,200,.18);background:rgba(13,22,41,.75);
  border-radius:12px;padding:.75rem .9rem;margin:.45rem 0;overflow-wrap:anywhere;}
.section-title {color:#a5f3fc;font-size:.87rem;font-weight:700;margin-bottom:.4rem;}
.idea-item {border-left:2px solid #60a5fa;padding:.3rem .6rem;margin:.3rem 0;
  background:rgba(96,165,250,.06);border-radius:0 7px 7px 0;line-height:1.45;}
.stTextInput input,.stTextArea textarea,.stSelectbox [data-baseweb="select"] {
  background:rgba(10,17,32,.9)!important;color:#eef4ff!important;border-color:var(--line)!important;
  border-radius:9px!important;
}
.stTextInput label,.stTextArea label,.stSelectbox label,.stCheckbox label {color:#d9e5f8!important;}
.stTextArea textarea {min-height:145px!important;font-size:.92rem!important;line-height:1.5!important;}
div.stButton>button,div.stDownloadButton>button,[data-testid="stFormSubmitButton"] button {
  width:100%;min-height:38px;border-radius:9px;border:1px solid rgba(103,232,249,.32);
  background:linear-gradient(110deg,#2563eb,#6d28d9);color:white;font-weight:700;
}
div.stButton>button:hover,div.stDownloadButton>button:hover,[data-testid="stFormSubmitButton"] button:hover {
  border-color:#67e8f9;box-shadow:0 0 20px rgba(96,165,250,.2);color:white;
}
div[data-testid="stTabs"] button {color:#cbd5e1!important;font-weight:650;}
div[data-testid="stTabs"] button[aria-selected="true"] {color:#67e8f9!important;}
div[data-testid="stMetric"] {border:1px solid var(--line);border-radius:10px;padding:.55rem;background:rgba(15,23,42,.6);}
div[data-testid="stMetricValue"] {font-size:1.15rem;}
.footer-note {text-align:center;color:#71809a;font-size:.68rem;margin-top:.2rem;}
.chat-line {padding:.55rem .7rem;border-radius:10px;margin:.35rem 0;line-height:1.55;white-space:pre-wrap;}
.chat-user {background:rgba(37,99,235,.16);border:1px solid rgba(96,165,250,.18);}
.chat-assistant {background:rgba(17,26,45,.8);border:1px solid var(--line);}
.small-muted {color:var(--muted);font-size:.72rem;}
@media(max-width:850px) {
 .block-container{padding:.55rem .65rem;}
 .hero{padding:.7rem;}.brand{font-size:1.35rem;}
 .stTextArea textarea{min-height:110px!important;}
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# 3. SQLITE: PERSISTENT CONVERSATIONAL MEMORY
# ============================================================

def init_memory():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )""")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            preference_key TEXT PRIMARY KEY,
            preference_value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )""")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS content_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            audience TEXT NOT NULL,
            platform TEXT NOT NULL,
            content_json TEXT NOT NULL,
            saved_path TEXT,
            created_at TEXT NOT NULL
        )""")

def save_message(conversation_id, role, message):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO conversations (conversation_id, role, message, created_at) VALUES (?, ?, ?, ?)",
            (conversation_id, role, message, datetime.now().isoformat(timespec="seconds"))
        )

def get_conversation(conversation_id, limit=MAX_HISTORY_TURNS):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT role, message FROM conversations
            WHERE conversation_id=?
            ORDER BY id DESC LIMIT ?
        """, (conversation_id, limit * 2)).fetchall()
    return [dict(r) for r in reversed(rows)]

def get_recent_memory(limit=8):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT id, topic, audience, platform, saved_path, created_at
            FROM content_memory ORDER BY id DESC LIMIT ?
        """, (limit,)).fetchall()
    return [dict(r) for r in rows]

def remember_task(topic, audience, platform, content, saved_path):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO content_memory
            (topic, audience, platform, content_json, saved_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (topic, audience, platform, json.dumps(content, ensure_ascii=False),
              str(saved_path), datetime.now().isoformat(timespec="seconds")))

def get_preferences():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT preference_key, preference_value FROM user_preferences").fetchall()
    return {k: v for k, v in rows}

def save_preference(key, value):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        INSERT INTO user_preferences(preference_key,preference_value,updated_at)
        VALUES(?,?,?)
        ON CONFLICT(preference_key) DO UPDATE SET
        preference_value=excluded.preference_value, updated_at=excluded.updated_at
        """, (key, value, datetime.now().isoformat(timespec="seconds")))

init_memory()
if "conversation_id" not in st.session_state:
    st.session_state["conversation_id"] = "default"
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = get_conversation(st.session_state["conversation_id"])


# ============================================================
# 4. OLLAMA AND HELPERS
# ============================================================

def ask_llm(prompt, system=None, temperature=0.4, history=None):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    if history:
        for item in history:
            if item.get("role") in ("user", "assistant"):
                messages.append({"role": item["role"], "content": item["message"]})
    messages.append({"role": "user", "content": prompt})
    response = client.chat(
        model=MODEL_NAME,
        messages=messages,
        # JSON mode makes Ollama constrain the response to valid JSON.
        format="json",
        options={"temperature": temperature, "num_ctx": 12288, "num_predict": 3072},
    )
    return response["message"]["content"]

def parse_json_response(raw):
    if isinstance(raw, dict):
        return raw
    text = str(raw).strip()
    text = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", text, flags=re.IGNORECASE).strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        parsed = json.loads(text[start:end + 1])
        if isinstance(parsed, dict):
            return parsed
    raise ValueError("The model did not return valid JSON.")

def save_pdf(result):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm,
        topMargin=17*mm, bottomMargin=17*mm, title=f"TrendPilot - {result.get('topic','Content Plan')}"
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TPTitle", parent=styles["Title"], textColor=colors.HexColor("#173b72"), fontSize=20, leading=24, spaceAfter=8))
    styles.add(ParagraphStyle(name="TPHeading", parent=styles["Heading2"], textColor=colors.HexColor("#087e9b"), fontSize=13, leading=16, spaceBefore=9, spaceAfter=5))
    styles.add(ParagraphStyle(name="TPBody", parent=styles["BodyText"], fontSize=9.5, leading=14, spaceAfter=5))
    story = [
        Paragraph("TrendPilot Content Plan", styles["TPTitle"]),
        Paragraph(f"<b>Topic:</b> {escape(str(result.get('topic','')))}", styles["TPBody"]),
        Paragraph(f"<b>Audience:</b> {escape(str(result.get('audience','')))}", styles["TPBody"]),
        Paragraph(f"<b>Platform:</b> {escape(str(result.get('platform','')))}", styles["TPBody"]),
        Paragraph(f"<b>Tone:</b> {escape(str(result.get('tone','')))}", styles["TPBody"]),
        Spacer(1, 8),
    ]
    content = result.get("content", {})
    labels = {
        "ideas": "Content Ideas", "caption": "Caption", "hashtags": "Hashtags",
        "reel_script": "Reel Script", "titles_thumbnails": "Titles & Thumbnail Text",
        "improvements": "Improvement Suggestions"
    }
    for key, value in content.items():
        story.append(Paragraph(escape(labels.get(key, key.title())), styles["TPHeading"]))
        if isinstance(value, list):
            items = [ListItem(Paragraph(escape(str(v)), styles["TPBody"])) for v in value]
            story.append(ListFlowable(items, bulletType="bullet", leftIndent=16))
        elif isinstance(value, dict):
            for k, v in value.items():
                story.append(Paragraph(f"<b>{escape(k.replace('_',' ').title())}:</b> {escape(str(v))}", styles["TPBody"]))
        else:
            story.append(Paragraph(escape(str(value)).replace("\n", "<br/>"), styles["TPBody"]))
        story.append(Spacer(1, 5))
    doc.build(story)
    return buffer.getvalue()

def save_docx(result):
    doc = Document()
    doc.add_heading("TrendPilot Content Plan", 0)
    doc.add_paragraph(f"Topic: {result.get('topic','')}")
    doc.add_paragraph(f"Audience: {result.get('audience','')}")
    doc.add_paragraph(f"Platform: {result.get('platform','')}")
    doc.add_paragraph(f"Tone: {result.get('tone','')}")
    content = result.get("content", {})
    labels = {
        "ideas": "Content Ideas", "caption": "Caption", "hashtags": "Hashtags",
        "reel_script": "Reel Script", "titles_thumbnails": "Titles & Thumbnail Text",
        "improvements": "Improvement Suggestions"
    }
    for key, value in content.items():
        doc.add_heading(labels.get(key, key.title()), level=1)
        if isinstance(value, list):
            for item in value:
                doc.add_paragraph(str(item), style="List Bullet")
        elif isinstance(value, dict):
            for k, v in value.items():
                p = doc.add_paragraph()
                p.add_run(k.replace("_", " ").title() + ": ").bold = True
                p.add_run(str(v))
        else:
            doc.add_paragraph(str(value))
    doc.add_paragraph(f"Generated by TrendPilot on {result.get('generated_at','')}")
    output = BytesIO()
    doc.save(output)
    return output.getvalue()

def make_markdown(result):
    lines = [
        f"# TrendPilot Content Plan: {result.get('topic','')}", "",
        f"**Audience:** {result.get('audience','')}",
        f"**Platform:** {result.get('platform','')}",
        f"**Tone:** {result.get('tone','')}", ""
    ]
    labels = {
        "ideas": "Content Ideas", "caption": "Caption", "hashtags": "Hashtags",
        "reel_script": "Reel Script", "titles_thumbnails": "Titles & Thumbnail Text",
        "improvements": "Improvement Suggestions"
    }
    for key, value in result.get("content", {}).items():
        lines += [f"## {labels.get(key,key.title())}", ""]
        if isinstance(value, list):
            lines += [f"- {v}" for v in value]
        elif isinstance(value, dict):
            lines += [f"**{k.replace('_',' ').title()}:** {v}" for k,v in value.items()]
        else:
            lines.append(str(value))
        lines.append("")
    return "\n".join(lines)


def search_web_sources(query, max_results=5):
    """Lightweight web search. Returns titles, URLs, and snippets; gracefully falls back if unavailable."""
    try:
        import requests
        from bs4 import BeautifulSoup
        url = "https://html.duckduckgo.com/html/"
        response = requests.post(
            url,
            data={"q": query},
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"},
            timeout=7,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for item in soup.select(".result"):
            a = item.select_one(".result__title a")
            snippet = item.select_one(".result__snippet")
            if not a:
                continue
            title = a.get_text(" ", strip=True)
            href = a.get("href", "")
            if "uddg=" in href:
                from urllib.parse import urlparse, parse_qs
                href = parse_qs(urlparse(href).query).get("uddg", [href])[0]
            results.append({
                "title": title,
                "url": href,
                "snippet": snippet.get_text(" ", strip=True) if snippet else ""
            })
            if len(results) >= max_results:
                break
        return results
    except Exception as exc:
        return [{"title": "Web search unavailable", "url": "", "snippet": f"Could not retrieve live search results: {exc}"}]


def research_topic_if_needed(topic, audience, user_request):
    """Search the web for research-heavy requests instead of letting the model invent specifics."""
    combined = f"{topic or ''} {audience or ''} {user_request or ''}".lower()
    triggers = (
        "university", "universities", "college", "colleges", "best", "top ",
        "compare", "comparison", "pros and cons", "research", "latest",
        "current", "rankings", "fees", "admission", "schools", "hospitals",
        "products", "companies", "statistics"
    )
    if not any(word in combined for word in triggers):
        return []
    query = f"{topic or user_request} {audience or ''} official website features pros cons"
    results = search_web_sources(query, max_results=5)
    # If this is about Lahore universities, search official university/program and HEC pages.
    if "universit" in combined and "lahore" in combined:
        results += search_web_sources(
            "Lahore BS Computer Science official LUMS FAST NUCES Punjab University COMSATS ITU UET Lahore HEC",
            max_results=4
        )
    seen, unique = set(), []
    for item in results:
        url = item.get("url", "")
        key = url or item.get("title", "")
        if key and key not in seen and item.get("title") != "Web search unavailable":
            seen.add(key)
            unique.append(item)
    return unique[:10]


def build_prompt(topic, audience, platform, tone, duration, mode, user_request, history, preferences, research_sources=None):
    return f"""
You are TrendPilot, a professional social content strategist and scriptwriter. This is a continuing conversation.
Remember prior context and follow the user's latest request. If the user asks to revise
something from the conversation, revise it instead of starting over. If they mention
"same style", "make it shorter", "continue", or "change the platform", use the prior
conversation and preferences.

SAVED USER PREFERENCES:
{json.dumps(preferences, ensure_ascii=False, indent=2)}

WEB RESEARCH RESULTS (use these facts, compare evidence, and cite URLs in the response):
{json.dumps(research_sources or [], ensure_ascii=False, indent=2)}

RECENT CONVERSATION:
{json.dumps(history[-MAX_HISTORY_TURNS:], ensure_ascii=False, indent=2)}

CURRENT SETTINGS:
Topic: {topic or "(infer from conversation)"}
Audience: {audience or "(infer from conversation)"}
Platform: {platform}
Tone: {tone}
Reel duration: {duration} seconds
Selected mode: {mode}

LATEST USER REQUEST:
{user_request}

Return ONLY one valid JSON object with these fields:
{{
  "response_text": "A natural, clean, ChatGPT-style response in readable text.",
  "ideas": [{{"title":"specific idea","hook":"opening hook","angle":"what the content covers","audience_value":"why viewers care"}}],
  "caption": "caption when useful",
  "hashtags": ["5 hashtags when useful"],
  "reel_script": {{
    "hook": "Exact opening words, with estimated seconds",
    "scenes": [
      {{
        "time": "00:00-00:05",
        "voiceover": "Complete spoken dialogue for this time segment",
        "visual": "Specific shot/action/on-screen demonstration",
        "on_screen_text": "Short text shown on screen"
      }}
    ],
    "full_voiceover": "Complete continuous script ready to read aloud",
    "visual_suggestion": "Overall filming/editing direction",
    "closing_line": "Exact closing words and call to action",
    "estimated_duration_seconds": {duration}
  }},
  "titles_thumbnails": [
    {{"title":"...", "thumbnail_text":"...", "content_angle":"..."}}
  ],
  "improvements": ["actionable suggestion 1", "suggestion 2", "suggestion 3"],
  "research_summary": [
    {{"name":"university or organization","characteristics":["verified characteristic"],"pros":["evidence-based advantage"],"cons":["evidence-based limitation or trade-off"],"source_urls":["URL"]}}
  ],
  "sources": [{{"title":"source title","url":"https://...","used_for":"what this source supports"}}],
  "remembered_preferences": {{"tone":"...", "platform":"...", "audience":"..."}}
}}

MODE RULES:
- Content Plan: provide useful ideas, caption, a complete duration-matched reel/video script, titles/thumbnails, and improvements.
- Reel + Hashtags: provide a full timestamped, duration-matched reel/video script, caption, relevant hashtags, and title/thumbnail if useful.
- Everything: provide all relevant sections.
- For every topic, use the same general-purpose workflow; do not hardcode university-specific content. Detect research needs from the request. For factual/current/comparison requests, use available research results; for creative requests, do not waste time on unnecessary search.
- If this is a follow-up request, treat it as an edit to the most recent relevant result unless the user clearly starts a new topic. Preserve all unchanged details, audience, platform, tone, and format. Never ask the user to repeat the prior result when it exists in history. Briefly state what changed.
- For Content Plan and Everything modes, ALWAYS return exactly 3 concrete content ideas. Each idea must include a specific title, hook, angle, and audience_value. Never return an empty ideas list for these modes. For Reel + Hashtags, provide at least 3 ideas if the user asks for ideas.
- Do not leave required fields empty. Empty lists are allowed only for sections irrelevant to the selected mode or request.
- For research/comparison requests (universities, colleges, products, organizations, etc.), first use the supplied web research results. Identify real named options, compare them on clear criteria, and include specific evidence-based characteristics, pros, cons, and source URLs. Never invent named examples, rankings, alumni success stories, or unsupported claims. If web search is unavailable, clearly say the comparison is not live-verified and ask the user to enable/fix research rather than fabricating details.
- For university selection, shortlist 3-5 real universities that match the location/program. Explain curriculum or specialization, practical learning, campus/student opportunities, affordability/admissions only when supported by sources. Pros and cons must be specific; distinguish sourced facts from judgement/trade-offs.
- Do not claim live trend data or live trending hashtags.
- Use polished, specific, audience-aware writing. Avoid clichés, vague advice, repeated points, clickbait without payoff, and generic intros. Each recommendation must be actionable and fit the requested platform. Make response_text a helpful summary, not a replacement for the detailed structured fields. Do not include JSON in response_text.
- VIDEO SCRIPT LENGTH IS IMPORTANT: create a genuinely speakable script that fits the selected duration.
- The "response_text" must be a useful multi-paragraph editorial brief, not one generic introductory sentence. For research videos, summarize the shortlist and comparison, then the key takeaways. Do not put the whole script only into response_text; fill reel_script and research_summary in detail.
- For research-based video scripts, structure the narrative as: hook/question, research method/criteria, each named option with concrete strengths and trade-offs, who each option may suit, balanced conclusion, and CTA. Mention source links in a sources section, not awkwardly in every spoken sentence.
- Aim for about 2 to 2.5 spoken words per second (rough guide: 30 seconds = 60-75 words; 60 seconds = 120-150 words; 90 seconds = 180-225 words; 120 seconds = 240-300 words). Adjust for pauses and demonstrations.
- Split the reel/video into timestamped scenes that cover the whole selected duration from 00:00 to the ending. Do not stop after the hook or give only a short summary.
- Every scene must include complete spoken dialogue, a concrete visual direction, and on-screen text. Make the scenes flow naturally.
- The full_voiceover must contain the entire spoken script, not a summary, and should align with the scene dialogue and selected duration.
- Include a hook, useful step-by-step explanation/examples, transitions where appropriate, and a closing CTA.
- Avoid generic filler, repeated points, unsupported statistics, and unfinished sentences. Give concrete steps and examples; every sentence should provide value.
- Ensure timestamped scenes cover the complete duration and their dialogue matches the complete voiceover. Do not use placeholders or ellipses instead of actual content.
- For Content Plan, Reel + Hashtags, and Everything modes, include a detailed reel_script whenever the user is requesting video/reel content or a duration is selected.
- If the user explicitly asks only for hashtags or another narrow item, focus on that request rather than forcing a full script.
"""

def save_content_files(result):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    json_path = OUTPUT_DIR / f"trendpilot_{stamp}.json"
    md_path = OUTPUT_DIR / f"trendpilot_{stamp}.md"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(make_markdown(result), encoding="utf-8")
    result["saved_json"] = str(json_path)
    result["saved_markdown"] = str(md_path)
    return json_path, md_path

def run_agent(topic, audience, platform, tone, duration, mode, user_request, history):
    started = time.perf_counter()
    preferences = get_preferences()
    research_sources = research_topic_if_needed(topic, audience, user_request)
    prompt = build_prompt(topic, audience, platform, tone, duration, mode, user_request, history, preferences, research_sources)
    system = (
        "You are TrendPilot. Respond naturally and clearly like a helpful assistant. "
        "Use prior conversation when relevant. Return one valid JSON object only."
    )
    raw = ask_llm(prompt, system=system, temperature=0.3)
    try:
        generated = parse_json_response(raw)
    except (ValueError, json.JSONDecodeError) as first_error:
        # One recovery attempt: explicitly ask the model to repair malformed JSON.
        repair_prompt = f"""
The previous response was not valid JSON. Repair it and return ONE complete,
valid JSON object only. Do not add Markdown fences or commentary.
Keep the same content and required keys.

Parser error: {first_error}
Previous response:
{raw}
"""
        repaired_raw = ask_llm(repair_prompt, system=system, temperature=0.1)
        generated = parse_json_response(repaired_raw)

    # Enforce duration-matched scripts instead of trusting the model's estimate.
    # A script under ~1.8 spoken words/second is likely too short.
    script = generated.get("reel_script")
    script_requested = mode in ("Content Plan", "Reel + Hashtags", "Everything")
    if isinstance(script, dict) and script_requested:
        target_seconds = int(duration or 30)
        target_min_words = max(60, int(target_seconds * 2.0))
        target_ideal_words = int(target_seconds * 2.25)

        scenes = script.get("scenes", [])
        if not isinstance(scenes, list):
            scenes = []
        scene_voiceover = " ".join(
            str(scene.get("voiceover", "")).strip()
            for scene in scenes if isinstance(scene, dict)
        ).strip()
        full_voiceover = str(script.get("full_voiceover", "")).strip()
        if len(full_voiceover.split()) < len(scene_voiceover.split()):
            full_voiceover = scene_voiceover
            script["full_voiceover"] = full_voiceover

        if len(full_voiceover.split()) < target_min_words:
            length_prompt = f"""
The reel script below is too short. Rewrite and EXPAND it into a complete, natural,
ready-to-speak script for a {target_seconds}-second video.
Required: at least {target_min_words} spoken words; aim for about {target_ideal_words}.
Keep the same topic, audience, language, tone, and key message. Do not pad by repeating
sentences. Add useful explanation, concrete examples, transitions, and a closing CTA.
For comparison/research topics, preserve real named entities and concrete researched characteristics,
pros/cons, and source-backed details. Never replace named examples with vague phrases like "some universities".
Divide the whole duration into timestamped scenes that cover 00:00 through {target_seconds:02d}
seconds. Each scene must contain its complete voiceover, visual direction, and on-screen text.
The full_voiceover field must contain the complete spoken script and should match the scenes.
Return ONLY valid JSON with this structure:
{{
 "hook": "opening spoken line",
 "scenes": [{{"time":"00:00-00:05","voiceover":"complete dialogue","visual":"specific visual","on_screen_text":"short text"}}],
 "full_voiceover": "complete continuous spoken script",
 "visual_suggestion": "overall filming/editing direction",
 "closing_line": "closing CTA",
 "estimated_duration_seconds": {target_seconds}
}}
Current script to improve:
{json.dumps(script, ensure_ascii=False)}
"""
            try:
                expanded_raw = ask_llm(
                    length_prompt,
                    system="You are a professional short-form video scriptwriter. Follow word-count requirements carefully and return valid JSON only.",
                    temperature=0.25,
                )
                expanded = parse_json_response(expanded_raw)
                expanded_script = expanded.get("reel_script", expanded)
                if isinstance(expanded_script, dict):
                    expanded_voiceover = str(expanded_script.get("full_voiceover", "")).strip()
                    expanded_scenes = expanded_script.get("scenes", [])
                    if len(expanded_voiceover.split()) < target_min_words and isinstance(expanded_scenes, list):
                        expanded_voiceover = " ".join(
                            str(scene.get("voiceover", "")).strip()
                            for scene in expanded_scenes if isinstance(scene, dict)
                        ).strip()
                    if len(expanded_voiceover.split()) > len(full_voiceover.split()):
                        expanded_script["full_voiceover"] = expanded_voiceover
                        generated["reel_script"] = expanded_script
                        script = expanded_script
                        full_voiceover = expanded_voiceover
            except Exception as length_error:
                # Keep the original content if repair fails; report the quality issue below.
                pass

        final_words = len(str(script.get("full_voiceover", "")).split())
        issues = []
        if final_words < target_min_words:
            issues.append(
                f"Script is still short: {final_words} words for {target_seconds}s; "
                f"aim for at least {target_min_words} words. Ask TrendPilot to expand the script."
            )
        generated["_script_quality_issues"] = issues

    # Validate required content ideas; repair missing ideas once with a focused call.
    ideas = generated.get("ideas")
    if mode in ("Content Plan", "Everything") and (not isinstance(ideas, list) or len(ideas) < 3):
        ideas_prompt = f"""
Create exactly 3 distinct, specific content ideas for this topic: {topic or user_request}
Audience: {audience or 'general audience'}
Platform: {platform}; tone: {tone}
Latest request: {user_request}
Research snippets (if any): {json.dumps(research_sources[:6], ensure_ascii=False)}
Return ONLY valid JSON: {{"ideas":[{{"title":"...","hook":"...","angle":"...","audience_value":"..."}}]}}
Do not repeat ideas. Do not invent facts or claim research succeeded if sources are unavailable.
"""
        try:
            ideas_raw = ask_llm(ideas_prompt, system="You are a precise content strategist. Return exactly three useful ideas in valid JSON.", temperature=0.25)
            ideas_fixed = parse_json_response(ideas_raw).get("ideas", [])
            if isinstance(ideas_fixed, list) and len(ideas_fixed) >= 3:
                generated["ideas"] = ideas_fixed[:3]
        except Exception:
            pass

    # Flag failed live research rather than implying it succeeded.
    if any(item.get("title") == "Web search unavailable" for item in (research_sources or [])) or (
        research_sources and not any(item.get("url") for item in research_sources)
    ):
        generated["research_warning"] = "Live web search did not return usable source links. Treat current facts and comparisons as unverified."

    # Store learned user preferences only when the model supplies non-empty values.
    prefs = generated.get("remembered_preferences", {})
    if isinstance(prefs, dict):
        for key, value in prefs.items():
            if isinstance(value, str) and value.strip() and value.lower() not in ("unknown", "none", "null"):
                save_preference(key, value.strip())

    content = {k: generated.get(k) for k in [
        "ideas", "caption", "hashtags", "reel_script", "titles_thumbnails", "improvements",
        "research_summary", "sources", "research_warning"
    ] if generated.get(k) not in (None, "", [])}
    result = {
        "topic": topic or "Follow-up conversation",
        "audience": audience or preferences.get("audience", "Not specified"),
        "platform": platform,
        "tone": tone,
        "duration_seconds": duration,
        "mode": mode,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "response_text": generated.get("response_text", "").strip(),
        "content": content,
        "web_research_used": any(bool(item.get("url")) and item.get("title") != "Web search unavailable" for item in research_sources),
        "research_sources": research_sources,
        "quality_check": {"valid": bool(generated.get("response_text")), "issues": generated.get("_script_quality_issues", [])},
    }
    result["execution_seconds"] = round(time.perf_counter() - started, 2)
    json_path, md_path = save_content_files(result)
    result["saved_json"] = str(json_path)
    result["saved_markdown"] = str(md_path)
    remember_task(result["topic"], result["audience"], platform, result, json_path)
    return result

def safe_markdown(text):
    # st.markdown supports standard markdown; model output remains text, not raw HTML.
    return str(text or "").strip()


# ============================================================
# 5. HEADER
# ============================================================

st.markdown("""
<div class="hero">
  <div>
    <div class="brand">Trend<span>Pilot</span></div>
    <div class="subtitle">LOCAL AI CONTENT STUDIO · CONTEXT-AWARE CHAT</div>
  </div>
  <div class="status-pill">● QWEN 2.5 3B · LOCAL</div>
</div>
""", unsafe_allow_html=True)

# Compact history list in the left column.
def list_conversations(limit=12):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("""
            SELECT conversation_id,
                   MAX(id) AS last_id,
                   MAX(created_at) AS last_time,
                   MAX(CASE WHEN role='user' THEN message ELSE '' END) AS last_user
            FROM conversations
            GROUP BY conversation_id
            ORDER BY last_id DESC
            LIMIT ?
        """, (limit,)).fetchall()
    return rows

left, right = st.columns([2.5, 7.5], gap="medium")

with left:
    st.markdown('<div class="panel-heading">WORKSPACE</div>', unsafe_allow_html=True)
    mode = st.radio(
        "Create",
        ["Content Plan", "Reel + Hashtags", "Everything"],
        index=2,
        horizontal=False,
        key="mode_choice",
    )
    topic = st.text_input("Topic", placeholder="e.g. AI tools for students", key="topic_input")
    audience = st.text_input("Audience", placeholder="e.g. University students", key="audience_input")
    platform = st.selectbox("Platform", ["Instagram", "YouTube", "TikTok", "LinkedIn", "Facebook"], key="platform_choice")
    tone = st.selectbox("Writing style", ["Engaging", "Professional", "Educational", "Friendly", "Bold"], key="tone_choice")
    duration = st.select_slider("Video duration", options=[15, 30, 45, 60, 90, 120], value=30, key="duration_choice")

    st.markdown("---")
    st.markdown('<div class="panel-heading">CHAT HISTORY</div>', unsafe_allow_html=True)
    st.caption("Compact · select a conversation to reopen")
    history_rows = list_conversations()
    if history_rows:
        options = {
            f"{(r[3] or 'Conversation').replace(chr(10), ' ')[:32]} · {r[2][:16]}": r[0]
            for r in history_rows
        }
        labels = list(options.keys())
        selected_label = st.selectbox("Previous chats", labels, label_visibility="collapsed", key="history_select")
        if st.button("Open selected chat", use_container_width=True):
            st.session_state["conversation_id"] = options[selected_label]
            st.session_state["chat_messages"] = get_conversation(options[selected_label])
            st.rerun()
    else:
        st.caption("Your conversations will appear here.")
    if st.button("+ New chat", use_container_width=True):
        new_id = datetime.now().strftime("chat_%Y%m%d_%H%M%S_%f")
        st.session_state["conversation_id"] = new_id
        st.session_state["chat_messages"] = []
        st.session_state.pop("last_result", None)
        st.rerun()
    st.markdown('<div class="small-muted">Your chats are saved locally in SQLite.</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel-heading">CONTENT WORKSPACE</div>', unsafe_allow_html=True)
    st.caption("Enter your first request, then use the same box for follow-up edits. Results appear below.")

    # Keep a navigable set of result versions for the current conversation.
    if "result_versions" not in st.session_state:
        st.session_state["result_versions"] = {}
    current_id = st.session_state["conversation_id"]
    st.session_state["result_versions"].setdefault(current_id, [])
    if "result_index" not in st.session_state:
        st.session_state["result_index"] = {}
    st.session_state["result_index"].setdefault(current_id, max(0, len(st.session_state["result_versions"][current_id]) - 1))

    # Prompt stays at the top. The previous chat transcript is intentionally not repeated here.
    with st.form("chat_request_form", clear_on_submit=True):
        user_request = st.text_area(
            "Message TrendPilot",
            placeholder="Describe what to create, or request an edit to the previous result. Example: Keep the same topic, strengthen the hook, add a practical example, and make the script a complete 60 seconds.",
            height=105,
            key="user_request",
        )
        send = st.form_submit_button("✦ Send / Continue", use_container_width=True)

    versions = st.session_state["result_versions"][current_id]
    idx = st.session_state["result_index"].get(current_id, max(0, len(versions)-1))
    nav_left, nav_mid, nav_right = st.columns([1, 2, 1])
    with nav_left:
        if st.button("← Previous", disabled=(not versions or idx <= 0), use_container_width=True, key="prev_result"):
            st.session_state["result_index"][current_id] = idx - 1
            st.rerun()
    with nav_mid:
        if versions:
            st.caption(f"Result {idx + 1} of {len(versions)} · Use arrows to review earlier versions")
        else:
            st.caption("Your generated results will appear here")
    with nav_right:
        if st.button("Newer →", disabled=(not versions or idx >= len(versions)-1), use_container_width=True, key="next_result"):
            st.session_state["result_index"][current_id] = idx + 1
            st.rerun()

if send:
    if not user_request.strip():
        st.warning("Please enter a request first.")
    else:
        conversation_id = st.session_state["conversation_id"]
        previous = get_conversation(conversation_id)
        save_message(conversation_id, "user", user_request.strip())
        previous.append({"role": "user", "message": user_request.strip()})
        with st.spinner("TrendPilot is generating your content..."):
            try:
                result = run_agent(
                    topic=topic.strip(), audience=audience.strip(), platform=platform,
                    tone=tone.lower(), duration=duration, mode=mode,
                    user_request=user_request.strip(), history=previous[:-1]
                )
                answer = result["response_text"] or make_markdown(result)
                save_message(conversation_id, "assistant", answer)
                st.session_state["chat_messages"] = get_conversation(conversation_id)
                st.session_state["last_result"] = result
                st.session_state.setdefault("result_versions", {}).setdefault(conversation_id, []).append(result)
                st.session_state.setdefault("result_index", {})[conversation_id] = len(st.session_state["result_versions"][conversation_id]) - 1
                st.session_state.pop("generation_error", None)
                st.rerun()
            except Exception as exc:
                st.session_state["generation_error"] = str(exc)
                st.error(f"Generation failed: {exc}")

if st.session_state.get("generation_error"):
    st.error("Generation failed: " + st.session_state["generation_error"])

# Results and exports
current_id = st.session_state.get("conversation_id", "default")
versions = st.session_state.get("result_versions", {}).get(current_id, [])
selected_idx = st.session_state.get("result_index", {}).get(current_id, max(0, len(versions)-1))
result = versions[selected_idx] if versions and 0 <= selected_idx < len(versions) else st.session_state.get("last_result")
if result:
    st.markdown("---")
    st.markdown("### Content result")
    if result.get("response_text"):
        st.markdown(safe_markdown(result["response_text"]))
    research_warning = result.get("content", {}).get("research_warning")
    if research_warning:
        st.warning(research_warning)
    research_items = result.get("content", {}).get("research_summary", [])
    if research_items:
        st.markdown("### Research comparison")
        for item in research_items:
            if not isinstance(item, dict):
                continue
            st.markdown(f"#### {item.get('name', 'Option')}")
            if item.get("characteristics"):
                st.markdown("**Characteristics**")
                for value in item["characteristics"]:
                    st.markdown(f"- {value}")
            col_pro, col_con = st.columns(2)
            with col_pro:
                st.markdown("**Pros**")
                for value in item.get("pros", []):
                    st.markdown(f"- {value}")
            with col_con:
                st.markdown("**Cons / trade-offs**")
                for value in item.get("cons", []):
                    st.markdown(f"- {value}")
            for url in item.get("source_urls", []):
                if str(url).startswith("http"):
                    st.markdown(f"[Source]({url})")
    source_items = result.get("content", {}).get("sources", [])
    if source_items:
        with st.expander("Research sources", expanded=False):
            for source in source_items:
                if isinstance(source, dict) and source.get("url"):
                    st.markdown(f"- [{source.get('title', source['url'])}]({source['url']}) — {source.get('used_for','')}")
    if result.get("web_research_used"):
        with st.expander("Web search results used", expanded=False):
            for source in result.get("research_sources", []):
                if source.get("url"):
                    st.markdown(f"- [{source.get('title', source['url'])}]({source['url']})\n  {source.get('snippet','')}")
    content = result.get("content", {})
    pretty_labels = {
        "ideas": "Content Ideas", "caption": "Caption", "hashtags": "Hashtags",
        "reel_script": "Reel Script", "titles_thumbnails": "Titles & Thumbnail Text",
        "improvements": "Improvement Suggestions"
    }
    for key, value in content.items():
        st.markdown(f"#### {pretty_labels.get(key, key.title())}")
        if key == "reel_script" and isinstance(value, dict):
            script = value
            if script.get("hook"):
                st.markdown("**Opening hook**")
                st.write(script["hook"])
            if script.get("full_voiceover"):
                st.markdown("**Complete voiceover**")
                st.markdown(safe_markdown(script["full_voiceover"]))
                st.caption(f"Voiceover word count: {len(str(script['full_voiceover']).split())} · Target duration: {result.get('duration_seconds')} seconds")
            if script.get("scenes"):
                st.markdown("**Scene-by-scene storyboard**")
                for idx, scene in enumerate(script["scenes"], 1):
                    if not isinstance(scene, dict):
                        st.write(scene)
                        continue
                    with st.expander(f"Scene {idx} · {scene.get('time', 'Time not set')}", expanded=(idx == 1)):
                        st.markdown("**Voiceover**")
                        st.write(scene.get("voiceover", ""))
                        st.markdown("**Visual direction**")
                        st.write(scene.get("visual", ""))
                        st.markdown("**On-screen text**")
                        st.write(scene.get("on_screen_text", ""))
            if script.get("visual_suggestion"):
                st.markdown("**Overall visual direction**")
                st.write(script["visual_suggestion"])
            if script.get("closing_line"):
                st.markdown("**Closing line / CTA**")
                st.write(script["closing_line"])
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    st.markdown("- " + " · ".join(f"**{k.replace('_',' ').title()}:** {v}" for k, v in item.items()))
                else:
                    st.markdown(f"- {item}")
        elif isinstance(value, dict):
            for subkey, subvalue in value.items():
                st.markdown(f"**{subkey.replace('_',' ').title()}:**")
                st.write(subvalue)
        else:
            st.write(value)
    for issue in result.get("quality_check", {}).get("issues", []):
        st.warning(issue)

    pdf_bytes = save_pdf(result)
    docx_bytes = save_docx(result)
    col_pdf, col_docx, col_json = st.columns(3)
    with col_pdf:
        st.download_button(
            "↓ Save as PDF", data=pdf_bytes,
            file_name="TrendPilot_Content_Plan.pdf", mime="application/pdf",
            use_container_width=True
        )
    with col_docx:
        st.download_button(
            "↓ Save as Word", data=docx_bytes,
            file_name="TrendPilot_Content_Plan.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
    with col_json:
        st.download_button(
            "↓ Save as JSON", data=json.dumps(result, ensure_ascii=False, indent=2),
            file_name="TrendPilot_Content_Plan.json", mime="application/json",
            use_container_width=True
        )

st.markdown('<div class="footer-note">TRENDPILOT · LOCAL AI CONTENT STUDIO · SAVED MEMORY · EXPORT AS PDF OR WORD</div>', unsafe_allow_html=True)
