
from flask import Flask, jsonify, request, session, redirect, send_from_directory, render_template
from flask_cors import CORS
from datetime import datetime, timezone, timedelta
import os
import json
import uuid
import requests
import traceback

# ============================================================
# TASSIMO BTP CONSTRUCTION SARL
# Unified AI Business Management Platform
# One-file backend designed for the complete 10-module roadmap.
# Production secrets MUST be supplied through Render environment
# variables. No secret is stored in this source file.
# ============================================================

app = Flask(__name__)

# Stable secret key for login sessions
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "change-this-in-render"
)

# Login/session configuration
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_PATH="/",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=12),
)

CORS(
    app,
    supports_credentials=True
)

APP_NAME = "TASSIMO BTP CONSTRUCTION SARL"
CEO_NAME = "TAGNE Simo Innocant"
SLOGAN = "Together, let us build excellence."
SUPPORTED_LANGUAGES = ["en", "fr"]

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = (
    os.environ.get("SUPABASE_SECRET_KEY")
    or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    or os.environ.get("SUPABASE_ANON_KEY", "")
)
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_PRIMARY_MODEL = os.environ.get(
    "OPENROUTER_MODEL", "openai/gpt-oss-20b:free"
)
OPENROUTER_FALLBACK_MODEL = "openrouter/free"

WHATSAPP_VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN", "")
WHATSAPP_ACCESS_TOKEN = os.environ.get("WHATSAPP_ACCESS_TOKEN", "")
WHATSAPP_PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_BUSINESS_ACCOUNT_ID = os.environ.get("WHATSAPP_BUSINESS_ACCOUNT_ID", "")
META_GRAPH_VERSION = os.environ.get("META_GRAPH_VERSION", "v20.0")
INSTAGRAM_VERIFY_TOKEN = os.environ.get("INSTAGRAM_VERIFY_TOKEN", "")
INSTAGRAM_ACCESS_TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
TIKTOK_ACCESS_TOKEN = os.environ.get("TIKTOK_ACCESS_TOKEN", "")
TIKTOK_CLIENT_KEY = os.environ.get("TIKTOK_CLIENT_KEY", "")
LINKEDIN_ACCESS_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")
LINKEDIN_ORGANIZATION_ID = os.environ.get("LINKEDIN_ORGANIZATION_ID", "")
YOUTUBE_ACCESS_TOKEN = os.environ.get("YOUTUBE_ACCESS_TOKEN", "")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
YOUTUBE_CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID", "")
AI_AUTO_PUBLISH = os.environ.get("AI_AUTO_PUBLISH", "true").lower() == "true"


FACEBOOK_VERIFY_TOKEN = os.environ.get("FACEBOOK_VERIFY_TOKEN", "")
FACEBOOK_PAGE_ACCESS_TOKEN = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "")

CEO_EMAIL = os.environ.get("CEO_EMAIL", "")
CEO_PASSWORD = os.environ.get("CEO_PASSWORD", "")

TABLES = {
    "customers",
    "business_accounts",
    "automation_settings",
    "ai_conversations",
    "integrations",
    "messages",
    "projects",
    "inventory",
    "suppliers",
    "expenses",
    "payments",
    "invoices",
    "quotations",
    "receipts",
    "training_courses",
    "trainers",
    "students",
    "classes",
    "attendance",
    "digital_courses",
    "leads",
    "tasks",
    "campaigns",
    "documents",
    "approvals",
    "notifications",
}

# ------------------------------------------------------------
# Localization
# ------------------------------------------------------------

TEXT = {
    "en": {
        "login_required": "Authentication required.",
        "invalid_credentials": "Invalid CEO credentials.",
        "login_ok": "Login successful.",
        "logout_ok": "Logged out.",
        "saved": "Saved successfully.",
        "not_found": "Record not found.",
        "invalid_data": "Invalid data.",
        "ai_unavailable": "AI service is not configured or is temporarily unavailable.",
        "approval_required": "CEO approval is required for this action.",
    },
    "fr": {
        "login_required": "Authentification requise.",
        "invalid_credentials": "Identifiants du CEO invalides.",
        "login_ok": "Connexion réussie.",
        "logout_ok": "Déconnexion réussie.",
        "saved": "Enregistré avec succès.",
        "not_found": "Enregistrement introuvable.",
        "invalid_data": "Données invalides.",
        "ai_unavailable": "Le service IA n'est pas configuré ou est temporairement indisponible.",
        "approval_required": "L'approbation du CEO est requise pour cette action.",
    },
}


def language():
    value = request.args.get("lang") or request.headers.get("X-Language")
    if value not in SUPPORTED_LANGUAGES:
        value = session.get("language", "en")
    return value


def t(key):
    return TEXT.get(language(), TEXT["en"]).get(key, key)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


# ------------------------------------------------------------
# Supabase REST layer
# ------------------------------------------------------------

def supabase_configured():
    return bool(SUPABASE_URL and SUPABASE_KEY)


def supabase_headers(prefer=None):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    if prefer:
        headers["Prefer"] = prefer
    return headers


def sb_url(table):
    return f"{SUPABASE_URL}/rest/v1/{table}"


def sb_select(table, params=None):
    if not supabase_configured():
        return []
    try:
        response = requests.get(
            sb_url(table),
            headers=supabase_headers(),
            params=params or {},
            timeout=20,
        )
        if response.status_code >= 400:
            return []
        data = response.json()
        return data if isinstance(data, list) else []
    except Exception:
        return []


def sb_insert(table, payload, select=True):
    if not supabase_configured():
        return None
    try:
        prefer = "return=representation" if select else "return=minimal"
        response = requests.post(
            sb_url(table),
            headers=supabase_headers(prefer),
            json=payload,
            timeout=20,
        )
        if response.status_code >= 400:
            return None
        data = response.json() if response.content else None
        if isinstance(data, list):
            return data[0] if data else None
        return data
    except Exception:
        return None


def sb_update(table, filters, payload):
    if not supabase_configured():
        return None
    try:
        response = requests.patch(
            sb_url(table),
            headers=supabase_headers("return=representation"),
            params=filters,
            json=payload,
            timeout=20,
        )
        if response.status_code >= 400:
            return None
        data = response.json() if response.content else None
        return data[0] if isinstance(data, list) and data else data
    except Exception:
        return None


def sb_delete(table, filters):
    if not supabase_configured():
        return False
    try:
        response = requests.delete(
            sb_url(table),
            headers=supabase_headers("return=minimal"),
            params=filters,
            timeout=20,
        )
        return response.status_code < 400
    except Exception:
        return False


def sb_count(table):
    if not supabase_configured():
        return 0
    try:
        headers = supabase_headers("count=exact")
        response = requests.get(
            sb_url(table),
            headers=headers,
            params={"select": "id", "limit": "1"},
            timeout=20,
        )
        content_range = response.headers.get("Content-Range", "")
        if "/" in content_range:
            return int(content_range.split("/")[-1])
        data = response.json()
        return len(data) if isinstance(data, list) else 0
    except Exception:
        return 0


# ------------------------------------------------------------
# Authentication
# ------------------------------------------------------------

def authentication_configured():
    return bool(CEO_EMAIL and CEO_PASSWORD)


def session_authenticated():
    return bool(session.get("authenticated"))


def resolve_ceo_user():
    # Never invent a UUID. Use an actual business_accounts user_id only.
    rows = sb_select(
        "business_accounts",
        {"select": "user_id", "limit": "1"},
    )
    if rows and rows[0].get("user_id"):
        return {"id": rows[0]["user_id"]}
    return None


def get_authenticated_user():
    if not session_authenticated():
        return None
    return session.get("user") or resolve_ceo_user()


def login_page():
    return """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TASSIMO BTP — CEO Login</title>
<style>
*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;
background:linear-gradient(135deg,#101828,#183b56);min-height:100vh;
display:flex;align-items:center;justify-content:center;padding:20px}
.card{width:100%;max-width:430px;background:#fff;border-radius:24px;padding:30px;
box-shadow:0 20px 60px #0005}.logo{width:70px;height:70px;border-radius:18px;
background:#183b56;color:#fff;display:grid;place-items:center;font-size:30px;
margin:auto}.center{text-align:center}.muted{color:#667085}.field{margin:16px 0}
label{display:block;margin-bottom:7px;font-weight:700}input{width:100%;padding:14px;
border:1px solid #d0d5dd;border-radius:12px;font-size:16px}button{width:100%;
padding:14px;border:0;border-radius:12px;background:#183b56;color:#fff;
font-weight:700;font-size:16px;cursor:pointer}.row{display:flex;gap:8px;margin-top:14px}
.lang{background:#eef2f6;color:#183b56}.error{color:#b42318;margin-top:12px}
</style></head>
<body><main class="card">
<div class="logo">🏗️</div><div class="center">
<h2>TASSIMO BTP CONSTRUCTION SARL</h2><p class="muted" id="loginTitle">Tableau de bord du CEO</p>
</div><form id="login">
<div class="field"><label id="emailLabel">E-mail</label><input id="email" type="email" required></div>
<div class="field"><label id="passwordLabel">Mot de passe</label><input id="password" type="password" required></div>
<button id="signInBtn">Se connecter</button><div id="error" class="error"></div></form>
<div class="row"><button class="lang" onclick="setLang('en')" type="button">English</button>
<button class="lang" onclick="setLang('fr')" type="button">Français</button></div>
<script>
const loginLang=localStorage.getItem('lang')||'fr';
const loginI18n={fr:{title:'Tableau de bord du CEO',email:'E-mail',password:'Mot de passe',sign:'Se connecter',english:'English',french:'Français',failed:'Échec de la connexion.'},en:{title:'CEO Dashboard',email:'Email',password:'Password',sign:'Sign in',english:'English',french:'Français',failed:'Login failed.'}};
function paintLogin(){const d=loginI18n[loginLang];document.documentElement.lang=loginLang;document.getElementById('loginTitle').textContent=d.title;document.getElementById('emailLabel').textContent=d.email;document.getElementById('passwordLabel').textContent=d.password;document.getElementById('signInBtn').textContent=d.sign;}
function setLang(x){localStorage.setItem('lang',x);location.reload()}
paintLogin();
document.getElementById('login').onsubmit=async e=>{
 e.preventDefault();
 const r=await fetch('/login',{
 method:'POST',
 credentials:'same-origin',
 headers:{'Content-Type':'application/json'},
 body:JSON.stringify({
  email:email.value,
  password:password.value
 })
});
 const d=await r.json(); if(r.ok) location.href='/'; else error.textContent=d.error||loginI18n[loginLang].failed;
}
</script></main></body></html>"""


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if session_authenticated():
            return redirect("/")
        return login_page()

    data = request.get_json(silent=True) or request.form.to_dict()
    email = str(data.get("email", "")).strip()
    password = str(data.get("password", ""))

    if not authentication_configured():
        return jsonify({
            "error": "CEO_EMAIL and CEO_PASSWORD are not configured in Render."
        }), 503

    if email != CEO_EMAIL or password != CEO_PASSWORD:
        return jsonify({"error": t("invalid_credentials")}), 401

    session.clear()
    session.permanent = True
    session["authenticated"] = True
    session["language"] = "en"
    user = resolve_ceo_user()
    if user:
        session["user"] = user
    return jsonify({"message": t("login_ok"), "redirect": "/"})


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/api/auth/me")
def auth_me():
    if not session_authenticated():
        return jsonify({"authenticated": False}), 401
    return jsonify({
        "authenticated": True,
        "name": CEO_NAME,
        "business": APP_NAME,
        "language": session.get("language", "en"),
        "user": get_authenticated_user(),
    })


def protected(fn):
    from functools import wraps

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session_authenticated():
            return jsonify({"error": t("login_required")}), 401
        return fn(*args, **kwargs)

    return wrapper


# ------------------------------------------------------------
# Business profile / settings
# ------------------------------------------------------------

DEFAULT_PROFILE = {
    "business_name": APP_NAME,
    "ceo_name": CEO_NAME,
    "slogan": SLOGAN,
    "country": "Cameroon",
    "city": "Douala",
    "language": "fr",
    "services": [
        "Construction",
        "Renovation",
        "Design",
        "Civil Engineering",
        "Professional Training",
        "Digital Courses",
    ],
}


def profile_payload():
    rows = sb_select(
        "business_accounts",
        {"select": "*", "limit": "1"},
    )
    if rows:
        profile = DEFAULT_PROFILE.copy()
        profile.update(rows[0])
        return profile
    return DEFAULT_PROFILE.copy()


@app.route("/api/profile", methods=["GET", "POST", "PUT"])
@protected
def profile_api():
    if request.method == "GET":
        return jsonify(profile_payload())

    data = request.get_json(silent=True) or {}
    data["updated_at"] = utc_now()
    existing = sb_select(
        "business_accounts",
        {"select": "id,user_id", "limit": "1"},
    )
    saved = None
    if existing and existing[0].get("id"):
        saved = sb_update(
            "business_accounts",
            {"id": f"eq.{existing[0]['id']}"},
            data,
        )
    else:
        user = get_authenticated_user()
        if user and user.get("id"):
            data["user_id"] = user["id"]
        saved = sb_insert("business_accounts", data)
    return jsonify({"message": t("saved"), "profile": saved or data})


@app.route("/api/settings", methods=["GET", "POST", "PUT"])
@protected
def settings_api():
    if request.method == "GET":
        rows = sb_select(
            "automation_settings",
            {"select": "*", "limit": "1"},
        )
        return jsonify(rows[0] if rows else {
            "language": "fr",
            "auto_reply_enabled": True,
            "ai_enabled": True,
            "approval_required_for_quotes": True,
            "approval_required_for_finance": True,
            "approval_required_for_contracts": True,
            "approval_required_for_technical_decisions": True,
        })

    data = request.get_json(silent=True) or {}
    data["updated_at"] = utc_now()
    rows = sb_select(
        "automation_settings",
        {"select": "id", "limit": "1"},
    )
    saved = (
        sb_update("automation_settings", {"id": f"eq.{rows[0]['id']}"}, data)
        if rows else sb_insert("automation_settings", data)
    )
    return jsonify({"message": t("saved"), "settings": saved or data})


# ------------------------------------------------------------
# Generic business data engine
# This keeps the one-file architecture extensible without
# creating dozens of Python modules.
# ------------------------------------------------------------

RESOURCE_MAP = {
    "customers": "customers",
    "leads": "leads",
    "projects": "projects",
    "inventory": "inventory",
    "suppliers": "suppliers",
    "expenses": "expenses",
    "payments": "payments",
    "invoices": "invoices",
    "quotations": "quotations",
    "receipts": "receipts",
    "trainers": "trainers",
    "students": "students",
    "classes": "classes",
    "attendance": "attendance",
    "training-courses": "training_courses",
    "digital-courses": "digital_courses",
    "tasks": "tasks",
    "campaigns": "campaigns",
    "documents": "documents",
    "approvals": "approvals",
    "notifications": "notifications",
    "messages": "messages",
    "integrations": "integrations",
    "ai-conversations": "ai_conversations",
}


def normalize_record(data):
    record = dict(data)
    now = utc_now()
    record.setdefault("created_at", now)
    record["updated_at"] = now
    return record


def customer_identity(data):
    phone = str(data.get("phone", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    name = str(data.get("name", "")).strip()
    return phone, email, name


def upsert_customer(data):
    data = normalize_record(data)
    phone, email, _ = customer_identity(data)

    if phone:
        existing = sb_select(
            "customers",
            {
                "select": "*",
                "phone": f"eq.{phone}",
                "limit": "1",
            },
        )

        if existing:
            saved = sb_update(
                "customers",
                {"id": f"eq.{existing[0]['id']}"},
                data,
            )

            if not saved:
                return {
                    "_error": "Customer update failed in Supabase."
                }

            return saved

    if email:
        existing = sb_select(
            "customers",
            {
                "select": "*",
                "email": f"eq.{email}",
                "limit": "1",
            },
        )

        if existing:
            saved = sb_update(
                "customers",
                {"id": f"eq.{existing[0]['id']}"},
                data,
            )

            if not saved:
                return {
                    "_error": "Customer update failed in Supabase."
                }

            return saved

    saved = sb_insert("customers", data)

    if not saved:
        return {
            "_error": "Customer could not be saved to Supabase."
        }

    return saved

 


@app.route("/api/customers", methods=["GET", "POST", "PUT", "DELETE"])
@protected
def customers_api():
    if request.method == "GET":
        rows = sb_select("customers", {
            "select": "*",
            "order": "created_at.desc",
        })
        return jsonify({"customers": rows})

    data = request.get_json(silent=True) or {}

 if request.method == "POST":
    saved = upsert_customer(data)

    if isinstance(saved, dict) and saved.get("_error"):
        return jsonify({
            "error": saved["_error"]
        }), 400

    return jsonify({
        "message": t("saved"),
        "customer": saved
    }), 201

    record_id = data.get("id") or request.args.get("id")
    if not record_id:
        return jsonify({"error": t("invalid_data")}), 400

    if request.method == "PUT":
        data.pop("id", None)
        saved = sb_update("customers", {"id": f"eq.{record_id}"}, normalize_record(data))
        return jsonify({"message": t("saved"), "customer": saved})

    return jsonify({"deleted": sb_delete("customers", {"id": f"eq.{record_id}"})})


@app.route("/api/<resource>", methods=["GET", "POST", "PUT", "DELETE"])
@protected
def generic_resource(resource):
    if resource not in RESOURCE_MAP:
        return jsonify({"error": "Unknown resource."}), 404

    table = RESOURCE_MAP[resource]

    if request.method == "GET":
        params = {"select": "*", "order": "created_at.desc"}
        limit = request.args.get("limit")
        if limit:
            params["limit"] = limit
        rows = sb_select(table, params)
        return jsonify({"data": rows, "resource": resource})

    data = request.get_json(silent=True) or {}

    if request.method == "POST":
        saved = sb_insert(table, normalize_record(data))
        return jsonify({"message": t("saved"), "data": saved or data}), 201

    record_id = data.get("id") or request.args.get("id")
    if not record_id:
        return jsonify({"error": t("invalid_data")}), 400

    if request.method == "PUT":
        data.pop("id", None)
        saved = sb_update(
            table,
            {"id": f"eq.{record_id}"},
            normalize_record(data),
        )
        return jsonify({"message": t("saved"), "data": saved})

    return jsonify({"deleted": sb_delete(table, {"id": f"eq.{record_id}"})})


# ------------------------------------------------------------
# AI system
# ------------------------------------------------------------

NEXAFLOW_SYSTEM_PROMPT = f"""
You are the AI business assistant inside {APP_NAME}.
CEO: {CEO_NAME}
Location: Douala, Cameroon.
Slogan: {SLOGAN}

Business areas:
construction, renovation, design, civil engineering, professional training,
digital courses, customer service, marketing, projects, inventory, finance,
documents and business operations.

Rules:
- Support English and French.
- Detect the customer's language and answer in that language.
- Be practical and professional.
- Use Cameroon context and XAF/CFA when money is discussed.
- You may prepare estimates, quotations, recommendations, drafts and reports.
- Never pretend that a price, contract, purchase, legal commitment or sensitive
  technical decision has been approved by the CEO.
- Flag sensitive decisions for CEO approval.
- Never invent customer records, database IDs, credentials or integrations.
"""


def call_openrouter(messages, model):
    if not OPENROUTER_API_KEY:
        return None
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": request.host_url.rstrip("/"),
                "X-Title": APP_NAME,
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": 0.4,
            },
            timeout=60,
        )
        if response.status_code >= 400:
            return None
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception:
        return None


def ai_answer(question, conversation=None, context=None):
    conversation = conversation or []
    context = context or {}
    system = NEXAFLOW_SYSTEM_PROMPT + "\nBusiness context:\n" + json.dumps(
        context, ensure_ascii=False, default=str
    )
    messages = [{"role": "system", "content": system}]
    for item in conversation[-12:]:
        if isinstance(item, dict) and item.get("role") in {"user", "assistant"}:
            messages.append({
                "role": item["role"],
                "content": str(item.get("content", "")),
            })
    messages.append({"role": "user", "content": question})

    answer = call_openrouter(messages, OPENROUTER_PRIMARY_MODEL)
    if not answer:
        answer = call_openrouter(messages, OPENROUTER_FALLBACK_MODEL)
    return answer


@app.route("/api/ai", methods=["POST"])
@protected
def ai_assistant():
    data = request.get_json(silent=True) or {}
    question = str(data.get("question", "")).strip()
    conversation = data.get("conversation", [])
    context = data.get("context", {})

    if not question:
        return jsonify({"error": t("invalid_data")}), 400

    answer = ai_answer(question, conversation, context)
    if not answer:
        return jsonify({"error": t("ai_unavailable")}), 503

    record = {
        "user_message": question,
        "ai_reply": answer,
        "language": language(),
        "created_at": utc_now(),
    }
    sb_insert("ai_conversations", record)

    return jsonify({
        "answer": answer,
        "language": language(),
        "approval_required": requires_ceo_approval(question),
    })


def requires_ceo_approval(text):
    sensitive = [
        "contract", "contrat", "purchase", "achat", "buy", "acheter",
        "price", "prix", "quote", "devis", "quotation", "devis",
        "payment", "paiement", "loan", "prêt", "legal", "juridique",
        "dispute", "litige", "commit", "engagement", "safety", "sécurité",
    ]
    lowered = text.lower()
    return any(word in lowered for word in sensitive)


@app.route("/api/ai/estimate", methods=["POST"])
@protected
def ai_estimate():
    data = request.get_json(silent=True) or {}
    description = str(data.get("description", "")).strip()
    if not description:
        return jsonify({"error": t("invalid_data")}), 400

    prompt = f"""
Prepare a construction estimation assistance draft for:
{description}

Return structured sections:
1. Scope
2. Assumptions
3. Materials
4. Quantities
5. Labour
6. Equipment
7. Estimated cost in XAF
8. Risks
9. Items requiring CEO/technical approval

Clearly label all prices as estimates, not approved quotations.
"""
    answer = ai_answer(prompt, context={"business": profile_payload()})
    if not answer:
        return jsonify({"error": t("ai_unavailable")}), 503
    return jsonify({
        "estimate": answer,
        "approval_required": True,
        "message": t("approval_required"),
    })


# ------------------------------------------------------------
# Customer communication / CRM
# ------------------------------------------------------------

def detect_language(text):
    text = str(text).lower()
    french_words = {
        "bonjour", "merci", "devis", "prix", "construction",
        "maison", "chantier", "combien", "je", "vous", "pour",
    }
    score = sum(1 for word in french_words if word in text)
    return "fr" if score >= 2 else "en"


def store_message(channel, direction, customer_id=None, sender=None, text=""):
    return sb_insert("messages", {
        "channel": channel,
        "direction": direction,
        "customer_id": customer_id,
        "sender": sender,
        "message": text,
        "language": detect_language(text),
        "created_at": utc_now(),
    })


def whatsapp_send(to, text):
    if not (WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID):
        return {"ok": False, "error": "WhatsApp credentials are not configured."}

    url = (
        f"https://graph.facebook.com/v20.0/"
        f"{WHATSAPP_PHONE_NUMBER_ID}/messages"
    )
    try:
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": text},
            },
            timeout=30,
        )
        return {
            "ok": response.status_code < 400,
            "status": response.status_code,
            "data": response.json() if response.content else {},
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def process_whatsapp_message(phone, name, text, message_id=None):
    customer = upsert_customer({
        "name": name or phone,
        "phone": phone,
        "source": "whatsapp",
        "language": detect_language(text),
        "last_message": text,
        "last_contact_at": utc_now(),
    })

    customer_id = customer.get("id") if isinstance(customer, dict) else None
    store_message("whatsapp", "incoming", customer_id, phone, text)

    context = {
        "customer": customer,
        "channel": "whatsapp",
        "customer_message": text,
    }
    reply = ai_answer(text, context=context)

    if not reply:
        lang = detect_language(text)
        reply = (
            "Merci pour votre message. Notre équipe vous répondra bientôt."
            if lang == "fr"
            else "Thank you for your message. Our team will get back to you shortly."
        )

    sent = whatsapp_send(phone, reply)
    store_message("whatsapp", "outgoing", customer_id, WHATSAPP_PHONE_NUMBER_ID, reply)

    sb_insert("ai_conversations", {
        "customer_id": customer_id,
        "channel": "whatsapp",
        "user_message": text,
        "ai_reply": reply,
        "external_message_id": message_id,
        "language": detect_language(text),
        "created_at": utc_now(),
    })

    return {"customer": customer, "reply": reply, "sent": sent}


@app.route("/webhook/whatsapp", methods=["GET", "POST"])
def whatsapp_webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if (
            mode == "subscribe"
            and WHATSAPP_VERIFY_TOKEN
            and token == WHATSAPP_VERIFY_TOKEN
        ):
            return challenge or "", 200
        return "Forbidden", 403

    payload = request.get_json(silent=True) or {}
    try:
        entries = payload.get("entry", [])
        for entry in entries:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                for message in value.get("messages", []):
                    phone = message.get("from", "")
                    message_id = message.get("id")
                    text = (
                        message.get("text", {}).get("body", "")
                        if message.get("type") == "text"
                        else ""
                    )
                    contacts = value.get("contacts", [])
                    name = (
                        contacts[0].get("profile", {}).get("name", "")
                        if contacts else ""
                    )
                    if phone and text:
                        process_whatsapp_message(phone, name, text, message_id)
        return jsonify({"received": True})
    except Exception:
        traceback.print_exc()
        return jsonify({"received": True}), 200


# ------------------------------------------------------------
# Facebook webhook / messaging foundation
# ------------------------------------------------------------

@app.route("/webhook/facebook", methods=["GET", "POST"])
def facebook_webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == FACEBOOK_VERIFY_TOKEN:
            return challenge or "", 200
        return "Forbidden", 403

    payload = request.get_json(silent=True) or {}
    for entry in payload.get("entry", []):
        for messaging in entry.get("messaging", []):
            sender = messaging.get("sender", {}).get("id")
            message = messaging.get("message", {})
            text = message.get("text", "")
            if sender and text:
                customer = upsert_customer({
                    "name": f"Facebook {sender}",
                    "external_id": sender,
                    "source": "facebook",
                    "language": detect_language(text),
                    "last_message": text,
                    "last_contact_at": utc_now(),
                })
                customer_id = customer.get("id") if isinstance(customer, dict) else None
                store_message("facebook", "incoming", customer_id, sender, text)
                reply = ai_answer(
                    text,
                    context={"customer": customer, "channel": "facebook"},
                )
                if reply:
                    store_message("facebook", "outgoing", customer_id, "TASSIMO BTP", reply)
    return jsonify({"received": True})


# ------------------------------------------------------------
# Analytics / reporting / business intelligence
# ------------------------------------------------------------

def safe_sum(rows, field):
    total = 0.0
    for row in rows:
        try:
            total += float(row.get(field) or 0)
        except (ValueError, TypeError):
            pass
    return total


@app.route("/api/dashboard")
@protected
def dashboard_api():
    customers = sb_count("customers")
    projects = sb_count("projects")
    inventory = sb_count("inventory")
    students = sb_count("students")
    leads = sb_count("leads")
    pending = sb_count("approvals")

    expenses = sb_select("expenses", {"select": "*"})
    payments = sb_select("payments", {"select": "*"})
    quotations = sb_select("quotations", {"select": "*"})

    return jsonify({
        "business": profile_payload(),
        "ceo": CEO_NAME,
        "stats": {
            "customers": customers,
            "projects": projects,
            "inventory_items": inventory,
            "students": students,
            "leads": leads,
            "pending_approvals": pending,
            "expenses": safe_sum(expenses, "amount"),
            "payments": safe_sum(payments, "amount"),
            "quotation_value": safe_sum(quotations, "total"),
        },
        "modules": list(RESOURCE_MAP.keys()),
        "language": language(),
    })


@app.route("/api/analytics")
@protected
def analytics_api():
    customers = sb_select("customers", {"select": "created_at,source,language"})
    projects = sb_select("projects", {"select": "status,budget,progress"})
    expenses = sb_select("expenses", {"select": "amount,category,created_at"})
    payments = sb_select("payments", {"select": "amount,method,created_at"})
    students = sb_select("students", {"select": "created_at,status"})

    return jsonify({
        "customers": {
            "total": len(customers),
            "by_source": count_by(customers, "source"),
            "by_language": count_by(customers, "language"),
        },
        "projects": {
            "total": len(projects),
            "by_status": count_by(projects, "status"),
            "average_progress": average_number(projects, "progress"),
            "budget": safe_sum(projects, "budget"),
        },
        "finance": {
            "expenses": safe_sum(expenses, "amount"),
            "payments": safe_sum(payments, "amount"),
            "expenses_by_category": sum_by(expenses, "category", "amount"),
        },
        "training": {
            "students": len(students),
            "by_status": count_by(students, "status"),
        },
    })


def count_by(rows, field):
    result = {}
    for row in rows:
        key = row.get(field) or "unknown"
        result[key] = result.get(key, 0) + 1
    return result


def sum_by(rows, group_field, value_field):
    result = {}
    for row in rows:
        key = row.get(group_field) or "other"
        try:
            value = float(row.get(value_field) or 0)
        except (ValueError, TypeError):
            value = 0
        result[key] = result.get(key, 0) + value
    return result


def average_number(rows, field):
    values = []
    for row in rows:
        try:
            values.append(float(row.get(field)))
        except (ValueError, TypeError):
            pass
    return round(sum(values) / len(values), 2) if values else 0


@app.route("/api/reports/<report_type>")
@protected
def reports_api(report_type):
    report_tables = {
        "customers": "customers",
        "projects": "projects",
        "finance": "expenses",
        "payments": "payments",
        "training": "students",
        "inventory": "inventory",
        "sales": "quotations",
        "messages": "messages",
    }
    table = report_tables.get(report_type)
    if not table:
        return jsonify({"error": "Unknown report."}), 404
    rows = sb_select(table, {"select": "*", "order": "created_at.desc"})
    return jsonify({
        "report": report_type,
        "generated_at": utc_now(),
        "rows": rows,
        "count": len(rows),
    })


@app.route("/api/business-intelligence", methods=["GET", "POST"])
@protected
def business_intelligence():
    if request.method == "GET":
        return jsonify({
            "enabled": bool(OPENROUTER_API_KEY),
            "features": [
                "customer insights",
                "sales pipeline analysis",
                "project risk analysis",
                "cash-flow assistance",
                "inventory alerts",
                "training performance",
                "marketing recommendations",
            ],
        })

    data = request.get_json(silent=True) or {}
    question = data.get(
        "question",
        "Analyze current business performance and give practical recommendations.",
    )
    dashboard = dashboard_api().get_json()
    answer = ai_answer(
        question,
        context={"dashboard": dashboard, "profile": profile_payload()},
    )
    if not answer:
        return jsonify({"error": t("ai_unavailable")}), 503
    return jsonify({"insight": answer})


# ------------------------------------------------------------
# CEO approvals
# ------------------------------------------------------------

@app.route("/api/approvals", methods=["GET", "POST", "PUT"])
@protected
def approvals_api():
    if request.method == "GET":
        rows = sb_select("approvals", {"select": "*", "order": "created_at.desc"})
        return jsonify({"approvals": rows})

    data = request.get_json(silent=True) or {}
    data = normalize_record(data)
    data.setdefault("status", "pending")
    data.setdefault("requested_by", "AI")
    saved = sb_insert("approvals", data) if request.method == "POST" else None

    if request.method == "PUT":
        record_id = data.pop("id", None)
        decision = str(data.get("status", "")).lower()
        if decision not in {"approved", "rejected", "pending"}:
            return jsonify({"error": t("invalid_data")}), 400
        saved = sb_update(
            "approvals",
            {"id": f"eq.{record_id}"},
            {"status": decision, "updated_at": utc_now()},
        )

    return jsonify({"message": t("saved"), "approval": saved})


# ------------------------------------------------------------
# Health / integrations
# ------------------------------------------------------------

@app.route("/api/status")
def status():
    return jsonify({
        "ok": True,
        "application": APP_NAME,
        "version": "2.0-unified",
        "time": utc_now(),
        "supabase_configured": supabase_configured(),
        "openrouter_configured": bool(OPENROUTER_API_KEY),
        "whatsapp_configured": bool(
            WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID
        ),
        "facebook_configured": bool(FACEBOOK_PAGE_ACCESS_TOKEN),
    })


@app.route("/api/integrations/status")
@protected
def integrations_status():
    return jsonify({
        "supabase": supabase_configured(),
        "openrouter": bool(OPENROUTER_API_KEY),
        "whatsapp": bool(WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID),
        "facebook": bool(FACEBOOK_PAGE_ACCESS_TOKEN),
        "instagram": bool(INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_BUSINESS_ACCOUNT_ID),
        "tiktok": bool(TIKTOK_ACCESS_TOKEN),
        "linkedin": bool(LINKEDIN_ACCESS_TOKEN and LINKEDIN_ORGANIZATION_ID),
        "youtube": bool(YOUTUBE_ACCESS_TOKEN or YOUTUBE_API_KEY),
        "ai_auto_publish": AI_AUTO_PUBLISH,
        "render": True,
        "github": True,
    })


# ------------------------------------------------------------
# Unified multi-channel messaging + AI publishing intelligence
# ------------------------------------------------------------

SOCIAL_CHANNELS = ["whatsapp", "facebook", "instagram", "tiktok", "linkedin", "youtube"]

def _post_json(url, headers=None, payload=None, timeout=30):
    try:
        r = requests.post(url, headers=headers or {}, json=payload or {}, timeout=timeout)
        try:
            data = r.json()
        except Exception:
            data = {"raw": r.text}
        return {"ok": r.status_code < 400, "status": r.status_code, "data": data}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

def social_send(channel, recipient, text, metadata=None):
    metadata = metadata or {}
    if channel == "whatsapp":
        return whatsapp_send(recipient, text)
    if channel == "facebook" and FACEBOOK_PAGE_ACCESS_TOKEN:
        url = f"https://graph.facebook.com/{META_GRAPH_VERSION}/me/messages"
        return _post_json(url, {"Authorization": f"Bearer {FACEBOOK_PAGE_ACCESS_TOKEN}", "Content-Type": "application/json"}, {"recipient": {"id": recipient}, "message": {"text": text}})
    if channel == "instagram" and INSTAGRAM_ACCESS_TOKEN:
        url = f"https://graph.facebook.com/{META_GRAPH_VERSION}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/messages"
        return _post_json(url, {"Authorization": f"Bearer {INSTAGRAM_ACCESS_TOKEN}", "Content-Type": "application/json"}, {"recipient": {"id": recipient}, "message": {"text": text}})
    return {"ok": False, "error": f"{channel} outbound API is not configured or approved."}

def ai_content_strategy(channel, objective="engagement", audience="potential construction and renovation customers"):
    prompt = (
        f"Create a social media content strategy for TASSIMO BTP CONSTRUCTION SARL on {channel}. "
        f"Objective: {objective}. Target audience: {audience}. "
        "Use Cameroon context. Recommend hook, format, CTA, topic, posting angle and measurable KPI. "
        "Use previous performance data when supplied; do not invent performance numbers."
    )
    return ai_answer(prompt, context={"channel": channel, "objective": objective, "audience": audience})

def save_social_post(channel, text, media_url="", status="draft", target_audience="", campaign=""):
    return sb_insert("social_posts", {
        "channel": channel, "content": text, "media_url": media_url, "status": status,
        "target_audience": target_audience, "campaign": campaign, "ai_generated": True,
        "created_at": utc_now(), "updated_at": utc_now()
    })

def save_social_metrics(channel, post_id, metrics):
    clean = {k: metrics.get(k, 0) for k in (
        "impressions", "reach", "likes", "comments", "shares", "saves",
        "clicks", "video_views", "watch_time", "conversions", "ad_spend"
    )}
    impressions = float(clean.get("impressions") or 0)
    interactions = sum(float(clean.get(k) or 0) for k in ("likes", "comments", "shares", "saves", "clicks"))
    clean["engagement_rate"] = round((interactions / impressions) * 100, 4) if impressions else 0
    clean.update({"channel": channel, "post_id": post_id, "measured_at": utc_now()})
    return sb_insert("social_metrics", clean)

def ai_learning_report(channel=None):
    params = {"select": "*", "order": "measured_at.desc", "limit": "500"}
    if channel:
        params["channel"] = f"eq.{channel}"
    rows = sb_select("social_metrics", params)
    if not rows:
        return {"channel": channel or "all", "data": [], "recommendation": "No performance data is stored yet. Start publishing and collecting metrics."}
    summary = {}
    for r in rows:
        ch = r.get("channel", "unknown")
        summary.setdefault(ch, {"posts": 0, "impressions": 0, "interactions": 0, "clicks": 0, "conversions": 0})
        summary[ch]["posts"] += 1
        summary[ch]["impressions"] += float(r.get("impressions") or 0)
        summary[ch]["interactions"] += sum(float(r.get(k) or 0) for k in ("likes", "comments", "shares", "saves"))
        summary[ch]["clicks"] += float(r.get("clicks") or 0)
        summary[ch]["conversions"] += float(r.get("conversions") or 0)
    return {"channel": channel or "all", "summary": summary, "recommendation": ai_answer(
        "Analyze this social/advertising performance data and recommend what TASSIMO BTP should change in its next video, image or text post. "
        "Identify the strongest audience signals, hooks, formats, topics, CTAs and channels. Do not invent facts. Data: " + json.dumps(summary, default=str)
    )}

@app.route("/api/messages", methods=["GET", "POST"])
@protected
def unified_messages_api():
    if request.method == "GET":
        channel = request.args.get("channel", "").strip().lower()
        params = {"select": "*", "order": "created_at.desc", "limit": "500"}
        if channel in SOCIAL_CHANNELS or channel == "ai":
            params["channel"] = f"eq.{channel}"
        return jsonify({"messages": sb_select("messages", params), "channels": SOCIAL_CHANNELS + ["ai"]})
    data = request.get_json(silent=True) or {}
    channel = str(data.get("channel", "")).lower().strip()
    text = str(data.get("message", "")).strip()
    recipient = str(data.get("recipient", "")).strip()
    if channel not in SOCIAL_CHANNELS or not text:
        return jsonify({"error": "Channel and message are required."}), 400
    result = social_send(channel, recipient, text, data) if recipient else {"ok": False, "error": "Recipient is required."}
    sb_insert("messages", {"channel": channel, "direction": "outgoing", "sender": "TASSIMO AI", "message": text, "language": detect_language(text), "created_at": utc_now()})
    return jsonify({"sent": result.get("ok", False), "result": result})

@app.route("/api/messages/ai-draft", methods=["POST"])
@protected
def messages_ai_draft():
    data = request.get_json(silent=True) or {}
    text = str(data.get("message", "")).strip()
    channel = str(data.get("channel", "whatsapp")).lower()
    if not text:
        return jsonify({"error": "Message is required."}), 400
    answer = ai_answer(text, context={"channel": channel, "customer": data.get("customer", {})})
    return jsonify({"draft": answer, "approval_required": requires_ceo_approval(text)})

@app.route("/api/social/ai-post", methods=["POST"])
@protected
def ai_social_post():
    data = request.get_json(silent=True) or {}
    channels = data.get("channels") or SOCIAL_CHANNELS
    if isinstance(channels, str):
        channels = [channels]
    objective = str(data.get("objective", "engagement and qualified leads"))
    audience = str(data.get("audience", "customers interested in construction, renovation, design and training in Cameroon"))
    topic = str(data.get("topic", ""))
    results = []
    for channel in [c for c in channels if c in SOCIAL_CHANNELS]:
        prompt = (f"Create a ready-to-publish {channel} post for TASSIMO BTP. Topic: {topic or 'a useful construction/renovation insight'}. "
                  f"Objective: {objective}. Target audience: {audience}. "
                  "Use the channel's appropriate style. Make it specific, credible, concise and action-oriented. "
                  "Do not invent projects, prices or results. Return only the post copy.")
        copy = ai_answer(prompt, context={"channel": channel, "audience": audience})
        saved = save_social_post(channel, copy or "", status="approved_for_ai_publish", target_audience=audience)
        results.append({"channel": channel, "copy": copy, "saved": saved})
    return jsonify({"ai_generated": True, "auto_publish_enabled": AI_AUTO_PUBLISH, "results": results})

@app.route("/api/social/learning", methods=["GET"])
@protected
def social_learning():
    return jsonify(ai_learning_report(request.args.get("channel") or None))

@app.route("/api/social/metrics", methods=["POST"])
@protected
def social_metrics():
    data = request.get_json(silent=True) or {}
    channel = str(data.get("channel", "")).lower()
    if channel not in SOCIAL_CHANNELS:
        return jsonify({"error": "Unsupported channel."}), 400
    saved = save_social_metrics(channel, data.get("post_id", ""), data)
    return jsonify({"saved": saved, "learning": ai_learning_report(channel)})


# ------------------------------------------------------------
# Built-in bilingual responsive dashboard
# This is intentionally self-contained so future pages can use
# the same application shell without changing the Flask server.
# ------------------------------------------------------------

DASHBOARD_HTML = r"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TASSIMO BTP — Business Manager</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
:root{--nav:#102a43;--nav2:#183b56;--bg:#f4f7fb;--card:#fff;--text:#172b4d;--muted:#667085;
--line:#e4e7ec;--accent:#e0a72e}
*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;background:var(--bg);color:var(--text)}
button,input,select,textarea{font:inherit}.app{display:flex;min-height:100vh}.side{width:255px;background:var(--nav);
color:#fff;position:fixed;inset:0 auto 0 0;padding:18px 12px;overflow:auto}.brand{padding:12px 10px 20px;
border-bottom:1px solid #ffffff22}.brand b{display:block;font-size:17px}.brand small{opacity:.7}
.nav{margin-top:12px}.nav button{width:100%;background:none;border:0;color:#fff;text-align:left;padding:11px 12px;
border-radius:10px;margin:2px 0;cursor:pointer}.nav button:hover,.nav button.active{background:#ffffff18}
.main{margin-left:255px;width:calc(100% - 255px)}header{height:70px;background:#fff;border-bottom:1px solid var(--line);
display:flex;align-items:center;justify-content:space-between;padding:0 24px;position:sticky;top:0;z-index:4}
.menu{display:none}.content{padding:24px}.title h1{margin:0}.muted{color:var(--muted)}.cards{display:grid;
grid-template-columns:repeat(4,1fr);gap:15px;margin:20px 0}.card{background:var(--card);border:1px solid var(--line);
border-radius:16px;padding:18px;box-shadow:0 4px 15px #10182808}.stat{font-size:28px;font-weight:800;margin-top:8px}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}.panel{background:#fff;border:1px solid var(--line);
border-radius:16px;padding:18px}.actions{display:flex;gap:9px;flex-wrap:wrap}.btn{border:0;border-radius:10px;
padding:11px 14px;background:var(--nav2);color:#fff;cursor:pointer}.btn.alt{background:#eef2f6;color:var(--nav2)}
table{width:100%;border-collapse:collapse}th,td{padding:10px;border-bottom:1px solid var(--line);text-align:left}
.form{display:grid;gap:10px}.form input,.form textarea,.form select{padding:11px;border:1px solid #d0d5dd;border-radius:10px}
.badge{display:inline-block;padding:5px 9px;border-radius:99px;background:#eef2f6;font-size:12px}
#toast{position:fixed;right:18px;bottom:18px;background:#102a43;color:#fff;padding:13px 17px;border-radius:10px;display:none}
@media(max-width:850px){.side{transform:translateX(-100%);transition:.2s;z-index:10}.side.open{transform:none}.main{margin-left:0;width:100%}
.menu{display:block;border:0;background:none;font-size:24px}.cards{grid-template-columns:repeat(2,1fr)}.grid{grid-template-columns:1fr}
.content{padding:15px}header{padding:0 15px}}@media(max-width:480px){.cards{grid-template-columns:1fr 1fr}.stat{font-size:22px}}
</style></head>
<body><div class="app">
<aside class="side" id="side"><div class="brand"><b>🏗️ TASSIMO BTP</b><small>Système de gestion d’entreprise</small></div>
<nav class="nav" id="nav"></nav></aside>
<section class="main"><header><button class="menu" onclick="side.classList.toggle('open')">☰</button>
<div><b id="pageTitle">Tableau de bord</b><div class="muted" id="welcome"></div></div>
<div class="actions"><button class="btn alt" onclick="setLang('en')">EN</button><button class="btn alt" onclick="setLang('fr')">FR</button>
<button class="btn" onclick="logout()">Déconnexion</button></div></header><main class="content" id="content"></main></section></div>
<div id="toast"></div>
<script>
const modules=[
 ['dashboard','📊','Dashboard','Tableau de bord'],['customers','👥','Customers','Clients'],['messages','💬','Messages','Messages'],
 ['leads','🎯','Leads & Sales','Prospects & Ventes'],['marketing','📣','Marketing','Marketing'],['projects','🏗️','Projects','Projets'],
 ['construction','📐','Construction AI','IA Construction'],['inventory','📦','Inventory','Stock'],['finance','💰','Finance','Finances'],
 ['documents','📄','Documents','Documents'],['training','🎓','Professional Training','Formation professionnelle'],['digital-courses','💻','Digital Courses','Cours numériques'],
 ['analytics','📈','Analytics','Analyses'],['reports','📋','Reports','Rapports'],['automation','⚙️','Automation','Automatisation'],
 ['ai','🤖','AI Assistant','Assistant IA'],['approvals','✅','CEO Approvals','Approbations du CEO'],['integrations','🔗','Integrations','Intégrations'],
 ['settings','⚙','Settings','Paramètres'],['admin','🔐','Administration','Administration']
];
const I18N={
 en:{business_os:'Business Operating System',logout:'Logout',welcome:'Welcome',slogan:'Together, let us build excellence.',activity:'Business Activity',quick_actions:'Quick Actions',
 customers:'Customers',expenses:'Expenses',inventory_items:'Inventory Items',leads:'Leads',payments:'Payments',pending_approvals:'Pending Approvals',projects:'Projects',quotation_value:'Quotation Value',students:'Students',records:'Records',
 add_customer:'Add Customer',add_project:'Add Project',add_expense:'Add Expense',ask_ai:'Ask AI',refresh:'Refresh',all:'All',loading:'Loading...',no_records:'No records yet.',no_messages:'No messages yet.',
 unified_messages:'Unified Messages',channel:'Channel',direction:'Direction',message:'Message',language:'Language',time:'Time',incoming:'Incoming',outgoing:'Outgoing',
 ai_publishing:'AI Publishing',ai_publish_desc:'AI creates the content strategy and posts across connected channels.',topic:'Topic',target_customers:'Target customers',generate_ai_posts:'Generate AI Posts',
 learning:'Ad & Content Learning',learning_desc:'AI studies impressions, reach, clicks, engagement, views, comments, shares, saves and conversions to improve the next post.',analyze:'Analyze Performance',
 generate:'Generating...',analyzing:'Analyzing...',no_customers:'No customers found.',
 new_customer:'New Customer',edit_customer:'Edit Customer',save_customer:'Save Customer',cancel:'Cancel',search_customers:'Search customers...',name:'Name',phone:'Phone',company:'Company',location:'Location',status:'Status',source:'Source',last_message:'Last Message',created:'Created',category:'Category',description:'Description',budget:'Budget',progress:'Progress',actions:'Actions',edit:'Edit',delete:'Delete',active:'Active',lead:'Lead',inactive:'Inactive',
 ai_assistant:'AI Assistant',ask_question:'Ask a question in English or French.',send:'Send',construction_ai:'Construction AI',describe_work:'Describe the building, renovation or civil engineering work...',estimate:'Generate Estimate Assistance',reports:'Reports',automation:'Automation',integrations:'Integrations',settings:'Settings',admin:'Administration',
 business_profile:'Business Profile',save:'Save',saved:'Saved successfully',customer_analytics:'Customer Analytics',finance:'Finance',report_customers:'Customers',report_projects:'Projects',report_finance:'Finance',report_payments:'Payments',report_training:'Training',report_inventory:'Inventory',report_sales:'Sales',report_messages:'Messages',
 permissions:'CEO authentication, permissions, security, integrations, database and operational controls are centralized here.',unknown:'Unknown resource.'},
 fr:{business_os:'Système de gestion d’entreprise',logout:'Déconnexion',welcome:'Bonjour',slogan:'Construisons l’excellence ensemble.',activity:'Activité de l’entreprise',quick_actions:'Actions rapides',
 customers:'Clients',expenses:'Dépenses',inventory_items:'Articles en stock',leads:'Prospects',payments:'Paiements',pending_approvals:'Approbations en attente',projects:'Projets',quotation_value:'Valeur des devis',students:'Étudiants',records:'Enregistrements',
 add_customer:'Ajouter un client',add_project:'Ajouter un projet',add_expense:'Ajouter une dépense',ask_ai:'Demander à l’IA',refresh:'Actualiser',all:'Tous',loading:'Chargement...',no_records:'Aucun enregistrement pour le moment.',no_messages:'Aucun message pour le moment.',
 unified_messages:'Centre de messagerie',channel:'Canal',direction:'Sens',message:'Message',language:'Langue',time:'Heure',incoming:'Entrant',outgoing:'Sortant',
 ai_publishing:'Publication par l’IA',ai_publish_desc:'L’IA crée la stratégie de contenu et publie sur les canaux connectés.',topic:'Sujet',target_customers:'Clients cibles',generate_ai_posts:'Générer les publications IA',
 learning:'Apprentissage publicitaire et contenu',learning_desc:'L’IA analyse les impressions, la portée, les clics, l’engagement, les vues, les commentaires, les partages, les enregistrements et les conversions afin d’améliorer la prochaine publication.',analyze:'Analyser les performances',
 generate:'Génération...',analyzing:'Analyse...',no_customers:'Aucun client trouvé.',
 new_customer:'Nouveau client',edit_customer:'Modifier le client',save_customer:'Enregistrer le client',cancel:'Annuler',search_customers:'Rechercher un client...',name:'Nom',phone:'Téléphone',company:'Entreprise',location:'Localisation',status:'Statut',source:'Source',last_message:'Dernier message',created:'Date de création',category:'Catégorie',description:'Description',budget:'Budget',progress:'Avancement',actions:'Actions',edit:'Modifier',delete:'Supprimer',active:'Actif',lead:'Prospect',inactive:'Inactif',
 ai_assistant:'Assistant IA',ask_question:'Posez une question en français ou en anglais.',send:'Envoyer',construction_ai:'IA Construction',describe_work:'Décrivez les travaux de construction, rénovation ou génie civil...',estimate:'Générer une assistance d’estimation',reports:'Rapports',automation:'Automatisation',integrations:'Intégrations',settings:'Paramètres',admin:'Administration',
 business_profile:'Profil de l’entreprise',save:'Enregistrer',saved:'Enregistré avec succès',customer_analytics:'Analyse des clients',finance:'Finances',report_customers:'Clients',report_projects:'Projets',report_finance:'Finances',report_payments:'Paiements',report_training:'Formation',report_inventory:'Stock',report_sales:'Ventes',report_messages:'Messages',
 permissions:'L’authentification du CEO, les autorisations, la sécurité, les intégrations, la base de données et les contrôles opérationnels sont centralisés ici.',unknown:'Ressource inconnue.'}
};

// Central bilingual UI layer: every interface label must have EN + FR values.
Object.assign(I18N.en,{ dashboard:'Dashboard',messages:'Messages',business:'Business',activity_label:'Activity',quick_actions_label:'Quick Actions', customers_label:'Customers',expenses_label:'Expenses',inventory_items_label:'Inventory Items',leads_label:'Leads',payments_label:'Payments', pending_approvals_label:'Pending Approvals',projects_label:'Projects',quotation_value_label:'Quotation Value',students_label:'Students', add_customer_label:'Add Customer',add_project_label:'Add Project',add_expense_label:'Add Expense',ask_ai_label:'Ask AI', no_messages_label:'No messages yet.',records_label:'Records'});
Object.assign(I18N.fr,{ dashboard:'Tableau de bord',messages:'Messages',business:'Entreprise',activity_label:'Activité',quick_actions_label:'Actions rapides', customers_label:'Clients',expenses_label:'Dépenses',inventory_items_label:'Articles en stock',leads_label:'Prospects',payments_label:'Paiements', pending_approvals_label:'Approbations en attente',projects_label:'Projets',quotation_value_label:'Valeur des devis',students_label:'Étudiants', add_customer_label:'Ajouter un client',add_project_label:'Ajouter un projet',add_expense_label:'Ajouter une dépense',ask_ai_label:'Demander à l’IA', no_messages_label:'Aucun message pour le moment.',records_label:'Enregistrements'});
function tr(key){return (I18N[lang]&&I18N[lang][key])||I18N.en[key]||key}
function channelLabel(c){const m={whatsapp:'WhatsApp',facebook:'Facebook',instagram:'Instagram',tiktok:'TikTok',linkedin:'LinkedIn',youtube:'YouTube',ai:'🤖 TASSIMO AI'};return m[c]||c}
function directionLabel(v){return v==='incoming'?tr('incoming'):v==='outgoing'?tr('outgoing'):v||''}
function resourceLabel(r){const map={customers:'customers',projects:'projects',inventory:'inventory_items',leads:'leads',finance:'finance',expenses:'expenses',payments:'payments',documents:'documents',training:'report_training','digital courses':'digital-courses',approvals:'pending_approvals',messages:'messages',message:'messages'};const key=map[r]||r;return tr(key)}
function fieldLabel(k){const map={name:'name',phone:'phone',email:'email',company:'company',location:'location',status:'status',source:'source',last_message:'last_message',created_at:'created',amount:'payments',category:'category',description:'description',budget:'budget',progress:'progress',total:'quotation_value'};return tr(map[k]||k.replaceAll('_',' '))}
let lang=localStorage.getItem('lang')||'fr';
function label(m){return lang==='fr'?m[3]:m[2]}
function renderShellLabels(){document.querySelector('.brand small').textContent=tr('business_os');document.querySelector('header .btn:not(.alt)').textContent=tr('logout')}
nav.innerHTML=modules.map(m=>`<button id="n-${m[0]}" onclick="openPage('${m[0]}')">${m[1]} ${label(m)}</button>`).join('');
function setLang(x){lang=x;localStorage.setItem('lang',x);location.reload()}
function toast(x){const toastEl=document.getElementById('toast');toastEl.textContent=x;toastEl.style.display='block';setTimeout(()=>toastEl.style.display='none',2500)}
async function api(url,opt={}){opt.headers={...(opt.headers||{}),'Content-Type':'application/json','X-Language':lang};const r=await fetch(url,opt);if(r.status===401){location.href='/login';return null}const d=await r.json();if(!r.ok)throw new Error(d.error||tr('unknown'));return d}
async function logout(){location.href='/logout'}
// ============================================================
// COMPLETE BILINGUAL UI ENGINE
// Every platform-generated interface string is translated at runtime.
// Customer names, customer messages and database values are NEVER translated.
// ============================================================
const EXTRA_EN_FR={
  'Business Operating System':'Système de gestion d’entreprise',
  'Logout':'Déconnexion','Dashboard':'Tableau de bord','Customers':'Clients','Expenses':'Dépenses',
  'Inventory Items':'Articles en stock','Leads':'Prospects','Leads & Sales':'Prospects & Ventes','Payments':'Paiements',
  'Pending Approvals':'Approbations en attente','Projects':'Projets','Quotation Value':'Valeur des devis','Students':'Étudiants',
  'Quick Actions':'Actions rapides','Business Activity':'Activité de l’entreprise','Activity':'Activité',
  '+ Customer':'+ Ajouter un client','+ Project':'+ Ajouter un projet','+ Expense':'+ Ajouter une dépense','Ask AI':'Demander à l’IA',
  'Open Messages':'Ouvrir la messagerie','Refresh':'Actualiser','All':'Tous','Loading...':'Chargement...',
  'No records yet.':'Aucun enregistrement pour le moment.','No messages yet.':'Aucun message pour le moment.',
  'Unified Messages':'Centre de messagerie','Channel':'Canal','Direction':'Sens','Message':'Message','Language':'Langue','Time':'Heure',
  'Incoming':'Entrant','Outgoing':'Sortant','AI Publishing':'Publication par l’IA',
  'AI creates the content strategy and posts across connected channels.':'L’IA crée la stratégie de contenu et publie sur les canaux connectés.',
  'Topic':'Sujet','Target customers':'Clients cibles','Generate AI Posts':'Générer les publications IA',
  'Ad & Content Learning':'Apprentissage publicitaire et contenu','Analyze Performance':'Analyser les performances',
  'Generating...':'Génération...','Analyzing...':'Analyse...','No customers found.':'Aucun client trouvé.',
  'New Customer':'Nouveau client','Edit Customer':'Modifier le client','Save Customer':'Enregistrer le client','Cancel':'Annuler',
  'Search customers...':'Rechercher un client...','Customer name':'Nom du client','Name':'Nom','Phone':'Téléphone','Email':'E-mail',
  'Company':'Entreprise','Location':'Localisation','Status':'Statut','Source':'Source','Last Message':'Dernier message','Created':'Créé le',
  'Date Created':'Date de création','Category':'Catégorie','Description':'Description','Budget':'Budget','Progress':'Avancement',
  'Actions':'Actions','Edit':'Modifier','Delete':'Supprimer','Active':'Actif','Inactive':'Inactif','Lead':'Prospect',
  'AI Assistant':'Assistant IA','Ask a question in English or French.':'Posez une question en français ou en anglais.',
  'Send':'Envoyer','Construction AI':'IA Construction','Describe the building, renovation or civil engineering work...':'Décrivez les travaux de construction, rénovation ou génie civil...',
  'Generate Estimate Assistance':'Générer une assistance d’estimation','Reports':'Rapports','Automation':'Automatisation',
  'Integrations':'Intégrations','Settings':'Paramètres','Administration':'Administration','Business Profile':'Profil de l’entreprise',
  'Save':'Enregistrer','Saved successfully':'Enregistré avec succès','Customer Analytics':'Analyse des clients','Finance':'Finances',
  'Training':'Formation','Inventory':'Stock','Sales':'Ventes','Messages':'Messages','Unknown resource.':'Ressource inconnue.',
  'Load Automation Settings':'Charger les paramètres d’automatisation','Business Name':'Nom de l’entreprise','Country':'Pays','City':'Ville',
  'CEO authentication, permissions, security, integrations, database and operational controls are centralized here.':'L’authentification du CEO, les autorisations, la sécurité, les intégrations, la base de données et les contrôles opérationnels sont centralisés ici.',
  'AI replies, language detection, customer intent, follow-ups and CEO approval controls.':'Réponses IA, détection de langue, intention du client, relances et contrôles d’approbation du CEO.',
  'Open Messages':'Ouvrir la messagerie','Records':'Enregistrements','Loading':'Chargement','Request failed':'La requête a échoué',
  'Authentication required.':'Authentification requise.','Invalid credentials.':'Identifiants invalides.','Login successful.':'Connexion réussie.',
  'Logged out.':'Déconnexion réussie.','Invalid data.':'Données invalides.','Not found.':'Ressource introuvable.',
  'Internal server error.':'Erreur interne du serveur.','Unsupported channel.':'Canal non pris en charge.',
  'CEO approval may be required.':'Une approbation du CEO peut être requise.'
};
const EXTRA_FR_EN=Object.fromEntries(Object.entries(EXTRA_EN_FR).map(([en,fr])=>[fr,en]));
function applyBilingualText(){
  const map=lang==='fr'?EXTRA_EN_FR:EXTRA_FR_EN;
  const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
  let node;
  while(node=walker.nextNode()){
    if(node.parentElement && ['SCRIPT','STYLE'].includes(node.parentElement.tagName)) continue;
    const raw=node.nodeValue;
    const trimmed=raw.trim();
    if(map[trimmed]) node.nodeValue=raw.replace(trimmed,map[trimmed]);
  }
  document.querySelectorAll('input[placeholder],textarea[placeholder],select[aria-label],button[aria-label]').forEach(el=>{
    const attr=el.hasAttribute('placeholder')?'placeholder':'aria-label';
    const value=el.getAttribute(attr);
    if(value && map[value]) el.setAttribute(attr,map[value]);
  });
  document.documentElement.lang=lang;
}
function enforceBilingualUI(){applyBilingualText()}
let bilingualObserver=null;
function startBilingualObserver(){
  if(bilingualObserver) bilingualObserver.disconnect();
  bilingualObserver=new MutationObserver(()=>{
    clearTimeout(window.__bilingualTimer);
    window.__bilingualTimer=setTimeout(applyBilingualText,20);
  });
  bilingualObserver.observe(document.body,{childList:true,subtree:true,characterData:true});
  applyBilingualText();
}
function openPage(p){
  if(p==='customers'){
    window.location.href='/customers';
    return;
  }

  document.querySelectorAll('.nav button').forEach(x=>x.classList.remove('active'));
  document.getElementById('n-'+p)?.classList.add('active');
  document.getElementById('pageTitle').textContent=modules.find(x=>x[0]===p)?.[lang==='fr'?3:2]||p;
  document.getElementById('welcome').textContent='';
  side.classList.remove('open');
  window['page_'+p]?window['page_'+p]():pageGeneric(p);
  setTimeout(enforceBilingualUI,80);
}


renderShellLabels();
startBilingualObserver();
async function page_dashboard(){
content.innerHTML=`<div class="title"><h1>${tr('welcome')}, TAGNE Simo Innocant</h1><p class="muted">${tr('slogan')}</p></div><div class="cards" id="cards"></div><div class="grid"><div class="panel"><h3>${tr('activity')}</h3><canvas id="chart"></canvas></div><div class="panel"><h3>${tr('quick_actions')}</h3><div class="actions"><button class="btn" onclick="openPage('customers')">+ ${tr('add_customer')}</button><button class="btn" onclick="openPage('projects')">+ ${tr('add_project')}</button><button class="btn" onclick="openPage('finance')">+ ${tr('add_expense')}</button><button class="btn" onclick="openPage('ai')">${tr('ask_ai')}</button></div></div></div><div class="panel" style="margin-top:18px"><h3>💬 ${tr('unified_messages')}</h3><div id="dashboardMessages" class="muted">${tr('loading')}</div><button class="btn alt" style="margin-top:12px" onclick="openPage('messages')">${lang==='fr'?'Ouvrir la messagerie':'Open Messages'}</button></div>`;
const d=await api('/api/dashboard');if(!d)return;
const statKeys=['customers','expenses','inventory_items','leads','payments','pending_approvals','projects','quotation_value'];
cards.innerHTML=statKeys.map(k=>`<div class="card"><div class="muted">${tr(k)}</div><div class="stat">${typeof d.stats[k]==='number'?Math.round(d.stats[k]*100)/100:d.stats[k]??0}</div></div>`).join('');
new Chart(document.getElementById('chart'),{type:'bar',data:{labels:[tr('customers'),tr('projects'),tr('leads'),tr('students')],datasets:[{label:tr('records'),data:[d.stats.customers,d.stats.projects,d.stats.leads,d.stats.students]}]}});
try{const md=await api('/api/messages');const rows=md?.messages||[];dashboardMessages.innerHTML=rows.length?rows.slice(0,5).map(r=>`<div style="padding:9px 0;border-bottom:1px solid #eee"><b>${channelLabel(r.channel||'')}</b> · ${directionLabel(r.direction)}<br>${escapeHtml(String(r.message||'').slice(0,180))}</div>`).join(''):tr('no_messages')}catch(e){dashboardMessages.textContent=tr('no_messages')}
}

let customerRows=[];

async function page_customers(){
content.innerHTML=`<div class="panel"><div class="actions" style="align-items:center">
<h2 style="margin-right:auto">${lang==='fr'?'Clients':'Customers'}</h2>
<button class="btn" onclick="showCustomerForm()">+ ${lang==='fr'?'Nouveau client':'Add Customer'}</button>
<button class="btn alt" onclick="loadCustomers()">↻ ${lang==='fr'?'Actualiser':'Refresh'}</button>
</div>
<div class="form" style="margin:15px 0"><input id="customerSearch" placeholder="${lang==='fr'?'Rechercher un client...':'Search customers...'}" oninput="renderCustomers()"></div>
<div id="customerForm"></div><div id="customerTable" class="muted">Loading...</div></div>`;
await loadCustomers();
}

async function loadCustomers(){const d=await api('/api/customers');if(!d)return;customerRows=d.customers||[];renderCustomers()}

function renderCustomers(){
const q=(document.getElementById('customerSearch')?.value||'').toLowerCase().trim();
const rows=customerRows.filter(r=>!q||Object.values(r).some(v=>String(v??'').toLowerCase().includes(q)));
const wrap=document.getElementById('customerTable');if(!wrap)return;
if(!rows.length){wrap.innerHTML=`<p>${lang==='fr'?'Aucun client trouvé.':'No customers found.'}</p>`;return}
const keys=['name','phone','email','company','location','status','source','last_message','created_at'];
wrap.innerHTML=`<div style="overflow:auto"><table><thead><tr>${keys.map(k=>`<th>${customerLabel(k)}</th>`).join('')}<th>Actions</th></tr></thead><tbody>
${rows.map(r=>`<tr>${keys.map(k=>`<td>${escapeHtml(r[k]??'')}</td>`).join('')}
<td><button class="btn alt" onclick="editCustomer('${escapeJs(r.id||'')}')">${lang==='fr'?'Modifier':'Edit'}</button>
<button class="btn alt" onclick="deleteCustomer('${escapeJs(r.id||'')}')">${lang==='fr'?'Supprimer':'Delete'}</button></td></tr>`).join('')}</tbody></table></div>`;
}

function customerLabel(k){const l={name:lang==='fr'?'Nom':'Name',phone:lang==='fr'?'Téléphone':'Phone',email:'Email',company:lang==='fr'?'Entreprise':'Company',location:lang==='fr'?'Localisation':'Location',status:lang==='fr'?'Statut':'Status',source:'Source',last_message:lang==='fr'?'Dernier message':'Last message',created_at:lang==='fr'?'Date de création':'Created'};return l[k]||k}
function escapeHtml(v){return String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function escapeJs(v){return String(v).replace(/\\/g,'\\\\').replace(/'/g,"\\'")}

function showCustomerForm(c={}){
const f=document.getElementById('customerForm');if(!f)return;
f.innerHTML=`<div class="panel" style="margin-bottom:15px"><h3>${c.id?(lang==='fr'?'Modifier le client':'Edit Customer'):(lang==='fr'?'Nouveau client':'Add Customer')}</h3>
<div class="form">
<input id="c_name" placeholder="${lang==='fr'?'Nom du client':'Customer name'}" value="${escapeHtml(c.name||'')}">
<input id="c_phone" placeholder="${lang==='fr'?'Téléphone / WhatsApp':'Phone / WhatsApp'}" value="${escapeHtml(c.phone||'')}">
<input id="c_email" type="email" placeholder="Email" value="${escapeHtml(c.email||'')}">
<input id="c_company" placeholder="${lang==='fr'?'Entreprise':'Company'}" value="${escapeHtml(c.company||'')}">
<input id="c_location" placeholder="${lang==='fr'?'Localisation':'Location'}" value="${escapeHtml(c.location||'')}">
<select id="c_status"><option value="active" ${c.status==='active'?'selected':''}>${lang==='fr'?'Actif':'Active'}</option><option value="lead" ${c.status==='lead'?'selected':''}>${lang==='fr'?'Prospect':'Lead'}</option><option value="inactive" ${c.status==='inactive'?'selected':''}>${lang==='fr'?'Inactif':'Inactive'}</option></select>
<div class="actions"><button class="btn" onclick="saveCustomer('${escapeJs(c.id||'')}')">${lang==='fr'?'Enregistrer':'Save Customer'}</button><button class="btn alt" onclick="document.getElementById('customerForm').innerHTML=''">${lang==='fr'?'Annuler':'Cancel'}</button></div>
</div></div>`;
}

async function saveCustomer(id){
const data={name:c_name.value.trim(),phone:c_phone.value.trim(),email:c_email.value.trim(),company:c_company.value.trim(),location:c_location.value.trim(),status:c_status.value};
if(!data.name&&!data.phone&&!data.email){toast(lang==='fr'?'Veuillez saisir au moins un nom, téléphone ou email.':'Enter at least a name, phone or email.');return}
try{await api('/api/customers'+(id?'?id='+encodeURIComponent(id):''),{method:id?'PUT':'POST',body:JSON.stringify(id?{...data,id}:data)});
toast(lang==='fr'?'Client enregistré avec succès.':'Customer saved successfully.');customerForm.innerHTML='';await loadCustomers()
}catch(e){toast(e.message)}
}

function editCustomer(id){const c=customerRows.find(r=>String(r.id)===String(id));if(c)showCustomerForm(c)}
async function deleteCustomer(id){if(!id)return;if(!confirm(lang==='fr'?'Supprimer ce client ?':'Delete this customer?'))return;try{await api('/api/customers?id='+encodeURIComponent(id),{method:'DELETE',body:JSON.stringify({id})});toast(lang==='fr'?'Client supprimé.':'Customer deleted.');await loadCustomers()}catch(e){toast(e.message)}}

async function page_messages(){content.innerHTML=`<div class="panel"><div class="actions"><h2 style="margin-right:auto">💬 ${tr('unified_messages')}</h2><button class="btn" onclick="loadMessages()">↻ ${tr('refresh')}</button></div><div class="actions" style="margin:15px 0">${['all','whatsapp','facebook','instagram','tiktok','linkedin','youtube','ai'].map(c=>`<button class="btn alt" onclick="loadMessages('${c}')">${c==='all'?'🌐 '+tr('all'):channelLabel(c)}</button>`).join('')}</div><div class="grid"><div class="panel"><h3>🤖 ${tr('ai_publishing')}</h3><p class="muted">${tr('ai_publish_desc')}</p><input id="postTopic" placeholder="${tr('topic')}"><input id="postAudience" placeholder="${tr('target_customers')}"><button class="btn" onclick="generateAIPost()">${tr('generate_ai_posts')}</button><pre id="postResult" style="white-space:pre-wrap"></pre></div><div class="panel"><h3>📈 ${tr('learning')}</h3><p class="muted">${tr('learning_desc')}</p><button class="btn" onclick="loadLearning()">${tr('analyze')}</button><pre id="learningResult" style="white-space:pre-wrap"></pre></div></div><div id="messageList" class="muted">${tr('loading')}</div></div>`;await loadMessages()}
async function loadMessages(channel=''){const d=await api('/api/messages'+(channel&&channel!=='all'?'?channel='+encodeURIComponent(channel):''));const rows=d?.messages||[];messageList.innerHTML=rows.length?`<div style="overflow:auto"><table><thead><tr><th>${tr('channel')}</th><th>${tr('direction')}</th><th>${tr('message')}</th><th>${tr('language')}</th><th>${tr('time')}</th></tr></thead><tbody>${rows.map(r=>`<tr><td>${channelLabel(r.channel||'')}</td><td>${directionLabel(r.direction)}</td><td>${escapeHtml(String(r.message||'').slice(0,180))}</td><td>${r.language==='fr'?'Français':r.language==='en'?'English':r.language||''}</td><td>${r.created_at||''}</td></tr>`).join('')}</tbody></table></div>`:`<p>${tr('no_messages')}</p>`}
async function generateAIPost(){postResult.textContent=tr('generate');try{const d=await api('/api/social/ai-post',{method:'POST',body:JSON.stringify({channels:['whatsapp','facebook','instagram','tiktok','linkedin','youtube'],topic:postTopic.value,audience:postAudience.value,language:lang})});postResult.textContent=JSON.stringify(d,null,2)}catch(e){postResult.textContent=e.message}}
async function loadLearning(){learningResult.textContent=tr('analyzing');try{const d=await api('/api/social/learning');learningResult.textContent=JSON.stringify(d,null,2)}catch(e){learningResult.textContent=e.message}}
async function page_leads(){await pageTable('leads','/api/leads','leads')}
async function page_projects(){await pageTable('projects','/api/projects','projects')}
async function page_inventory(){await pageTable('inventory','/api/inventory','inventory')}
async function page_finance(){await pageTable('finance','/api/expenses','expenses')}
async function page_documents(){await pageTable('documents','/api/documents','documents')}
async function page_training(){await pageTable('training','/api/students','students')}
async function page_digital_courses(){await pageTable('digital-courses','/api/digital-courses','digital-courses')}
async function page_approvals(){await pageTable('approvals','/api/approvals','approvals')}
async function pageTable(title,url,resource){content.innerHTML=`<div class="panel"><div class="actions"><h2 style="margin-right:auto">${resourceLabel(resource)}</h2><button class="btn" onclick="openPage('${title}')">↻ ${tr('refresh')}</button></div><div id="tableWrap" class="muted">${tr('loading')}</div></div>`;try{const d=await api(url);const rows=d?.customers||d?.data||d?.approvals||[];if(!rows.length){tableWrap.innerHTML=`<p>${tr('no_records')}</p>`;return}const keys=[...new Set(rows.flatMap(x=>Object.keys(x)))].slice(0,8);tableWrap.innerHTML=`<div style="overflow:auto"><table><thead><tr>${keys.map(k=>`<th>${fieldLabel(k)}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${keys.map(k=>`<td>${escapeHtml(r[k]??'')}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`}catch(e){tableWrap.textContent=e.message}}
async function page_ai(){content.innerHTML=`<div class="panel"><h2>🤖 ${tr('ai_assistant')}</h2><p class="muted">${tr('ask_question')}</p><div class="form"><textarea id="q" rows="5" placeholder="${lang==='fr'?'Posez votre question sur les clients, projets, devis, marketing ou finances...':'Ask about customers, projects, estimates, marketing or finance...'}"></textarea><button class="btn" onclick="askAI()">${tr('send')}</button></div><pre id="answer" style="white-space:pre-wrap"></pre></div>`}
async function askAI(){answer.textContent='...';try{const d=await api('/api/ai',{method:'POST',body:JSON.stringify({question:q.value})});answer.textContent=d.answer+(d.approval_required?(lang==='fr'?'\n\n⚠ Une approbation du CEO peut être requise.':'\n\n⚠ CEO approval may be required.'):'')}catch(e){answer.textContent=e.message}}
async function page_construction(){content.innerHTML=`<div class="panel"><h2>📐 ${tr('construction_ai')}</h2><textarea id="desc" rows="6" style="width:100%;padding:12px" placeholder="${tr('describe_work')}"></textarea><br><br><button class="btn" onclick="estimate()">${tr('estimate')}</button><pre id="est" style="white-space:pre-wrap"></pre></div>`}
async function estimate(){est.textContent='...';try{const d=await api('/api/ai/estimate',{method:'POST',body:JSON.stringify({description:desc.value})});est.textContent=d.estimate+'\n\n'+d.message}catch(e){est.textContent=e.message}}
async function page_analytics(){content.innerHTML=`<div class="grid"><div class="panel"><h3>${tr('customer_analytics')}</h3><canvas id="ac"></canvas></div><div class="panel"><h3>${tr('finance')}</h3><canvas id="af"></canvas></div></div>`;const d=await api('/api/analytics');new Chart(ac,{type:'doughnut',data:{labels:Object.keys(d.customers.by_source),datasets:[{data:Object.values(d.customers.by_source)}]}});new Chart(af,{type:'bar',data:{labels:Object.keys(d.finance.expenses_by_category),datasets:[{label:tr('expenses'),data:Object.values(d.finance.expenses_by_category)}]}})}
async function page_reports(){const names=['customers','projects','finance','payments','training','inventory','sales','messages'];content.innerHTML=`<div class="panel"><h2>${tr('reports')}</h2><div class="actions">${names.map(x=>`<button class="btn alt" onclick="loadReport('${x}')">${tr('report_'+x)}</button>`).join('')}</div><pre id="report" style="white-space:pre-wrap"></pre></div>`}
async function loadReport(x){try{const d=await api('/api/reports/'+x);report.textContent=JSON.stringify(d,null,2)}catch(e){report.textContent=e.message}}
async function page_automation(){content.innerHTML=`<div class="panel"><h2>${tr('automation')}</h2><p>${lang==='fr'?'Réponses IA, détection de langue, intention du client, relances et contrôles d’approbation du CEO.':'AI replies, language detection, customer intent, follow-ups and CEO approval controls.'}</p><button class="btn" onclick="loadSettings()">${lang==='fr'?'Charger les paramètres d’automatisation':'Load Automation Settings'}</button><pre id="set" style="white-space:pre-wrap"></pre></div>`}
async function loadSettings(){const d=await api('/api/settings');set.textContent=JSON.stringify(d,null,2)}
async function page_integrations(){const d=await api('/api/integrations/status');content.innerHTML=`<div class="cards">${Object.entries(d).map(([k,v])=>`<div class="card"><b>${k==='ai_auto_publish'?'Publication automatique IA':k}</b><div class="stat">${v?'✓':'—'}</div></div>`).join('')}</div>`}
async function page_settings(){const d=await api('/api/profile');const labels={business_name:lang==='fr'?'Nom de l’entreprise':'Business Name',ceo_name:'CEO',slogan:lang==='fr'?'Slogan':'Slogan',country:lang==='fr'?'Pays':'Country',city:lang==='fr'?'Ville':'City'};content.innerHTML=`<div class="panel"><h2>${tr('business_profile')}</h2><div class="form">${['business_name','ceo_name','slogan','country','city'].map(k=>`<label>${labels[k]}<input id="p_${k}" value="${escapeHtml(d[k]||'')}"></label>`).join('')}<button class="btn" onclick="saveProfile()">${tr('save')}</button></div></div>`}
async function saveProfile(){const data={};['business_name','ceo_name','slogan','country','city'].forEach(k=>data[k]=document.getElementById('p_'+k).value);await api('/api/profile',{method:'POST',body:JSON.stringify(data)});toast(tr('saved'))}
async function page_admin(){content.innerHTML=`<div class="panel"><h2>${tr('admin')}</h2><p>${tr('permissions')}</p><pre id="status"></pre></div>`;const d=await api('/api/status');status.textContent=JSON.stringify(d,null,2)}
openPage('dashboard');
</script></body></html>"""
@app.route("/customers")
@protected
def customers_page():
    return render_template("customers.html")
@app.route("/")
def home():
    if not session_authenticated():
        return redirect("/login")

    response = app.make_response(DASHBOARD_HTML)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/index.html")
def index_page():
    if not session_authenticated():
        return redirect("/login")

    response = app.make_response(DASHBOARD_HTML)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return response


# ------------------------------------------------------------
# Error handling
# ------------------------------------------------------------

@app.errorhandler(404)
def not_found(error):
    if request.path.startswith("/api/") or request.path.startswith("/webhook/"):
        return jsonify({"error": "Not found."}), 404
    return redirect("/")


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error."}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
