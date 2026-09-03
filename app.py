import os
from datetime import datetime

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS

from database import db


# ============================================================
# TASSIMO BTP CONSTRUCTION SARL
# MAIN APPLICATION
# ============================================================

app = Flask(__name__)
CORS(app)


# ============================================================
# COMPANY INFORMATION
# ============================================================

COMPANY = {
    "name": "TASSIMO BTP CONSTRUCTION SARL",
    "ceo": "TAGNE Simo Innocant",
    "location": "Douala – Logpom, Cameroon",
    "slogan": "Together, let us build excellence."
}


# ============================================================
# 10 PLATFORM MODULES
# ============================================================

MODULES = [
    {
        "id": 1,
        "name_en": "AI Business Manager",
        "name_fr": "Gestionnaire IA de l'entreprise",
        "icon": "🤖"
    },
    {
        "id": 2,
        "name_en": "Marketing & Social Media",
        "name_fr": "Marketing & Réseaux sociaux",
        "icon": "📣"
    },
    {
        "id": 3,
        "name_en": "CRM & Customer Communication",
        "name_fr": "CRM & Communication client",
        "icon": "👥"
    },
    {
        "id": 4,
        "name_en": "Construction AI & Estimation",
        "name_fr": "IA Construction & Estimation",
        "icon": "🏗️"
    },
    {
        "id": 5,
        "name_en": "Projects & Operations",
        "name_fr": "Projets & Opérations",
        "icon": "📋"
    },
    {
        "id": 6,
        "name_en": "Finance & Documents",
        "name_fr": "Finance & Documents",
        "icon": "💰"
    },
    {
        "id": 7,
        "name_en": "Professional Training",
        "name_fr": "Formation professionnelle",
        "icon": "🎓"
    },
    {
        "id": 8,
        "name_en": "Digital Training Store",
        "name_fr": "Boutique de formations numériques",
        "icon": "🛒"
    },
    {
        "id": 9,
        "name_en": "Analytics & Business Intelligence",
        "name_fr": "Analytique & Intelligence d'affaires",
        "icon": "📊"
    },
    {
        "id": 10,
        "name_en": "Administration & Integrations",
        "name_fr": "Administration & Intégrations",
        "icon": "⚙️"
    }
]


# ============================================================
# DATABASE / SYSTEM HELPERS
# ============================================================

def get_dashboard_data():
    """
    Collect the information needed by the CEO dashboard.

    The dashboard reads real information from Supabase through
    the central database layer.
    """

    stats = db.get_dashboard_stats()

    profile = db.get_company_profile()

    if not profile:
        profile = COMPANY.copy()

    return {
        "company": profile,
        "stats": stats,
        "modules": MODULES,
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }


# ============================================================
# DASHBOARD PAGE
# ============================================================

@app.route("/")
def dashboard():

    data = get_dashboard_data()

    return render_template_string(
        DASHBOARD_HTML,
        company=data["company"],
        stats=data["stats"],
        modules=data["modules"]
    )


# ============================================================
# API: SYSTEM STATUS
# ============================================================

@app.route("/api/status", methods=["GET"])
def api_status():

    stats = db.get_dashboard_stats()

    return jsonify({
        "success": True,
        "application": "TASSIMO BTP CONSTRUCTION SARL",
        "status": "online",
        "database_connected": stats.get(
            "database_connected",
            False
        ),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })


# ============================================================
# API: COMPANY
# ============================================================

@app.route("/api/company", methods=["GET"])
def api_company():

    profile = db.get_company_profile()

    if not profile:
        profile = COMPANY

    return jsonify({
        "success": True,
        "company": profile
    })


# ============================================================
# API: MODULES
# ============================================================

@app.route("/api/modules", methods=["GET"])
def api_modules():

    return jsonify({
        "success": True,
        "modules": MODULES
    })


# ============================================================
# API: DASHBOARD STATISTICS
# ============================================================

@app.route("/api/dashboard", methods=["GET"])
def api_dashboard():

    data = get_dashboard_data()

    return jsonify({
        "success": True,
        "company": data["company"],
        "stats": data["stats"],
        "modules": data["modules"],
        "generated_at": data["generated_at"]
    })


# ============================================================
# API: CUSTOMERS
# ============================================================

@app.route("/api/customers", methods=["GET"])
def api_customers():

    customers = db.get_customers(limit=100)

    return jsonify({
        "success": True,
        "count": len(customers),
        "customers": customers
    })


# ============================================================
# API: PROJECTS
# ============================================================

@app.route("/api/projects", methods=["GET"])
def api_projects():

    projects = db.get_projects(limit=100)

    return jsonify({
        "success": True,
        "count": len(projects),
        "projects": projects
    })


# ============================================================
# API: PAYMENTS
# ============================================================

@app.route("/api/payments", methods=["GET"])
def api_payments():

    payments = db.get_payments(limit=100)

    return jsonify({
        "success": True,
        "count": len(payments),
        "payments": payments
    })


# ============================================================
# API: COURSES
# ============================================================

@app.route("/api/courses", methods=["GET"])
def api_courses():

    courses = db.get_courses(limit=100)

    return jsonify({
        "success": True,
        "count": len(courses),
        "courses": courses
    })


# ============================================================
# API: AI COMMAND FOUNDATION
# ============================================================

@app.route("/api/ai", methods=["POST"])
def api_ai():

    data = request.get_json(silent=True) or {}

    command = str(
        data.get("command", "")
    ).strip()

    language = str(
        data.get("language", "en")
    ).lower()

    if not command:

        message = (
            "Please enter a command."
            if language != "fr"
            else
            "Veuillez entrer une commande."
        )

        return jsonify({
            "success": False,
            "message": message
        }), 400

    openai_configured = bool(
        os.getenv("OPENAI_API_KEY")
    )

    if language == "fr":

        response_text = (
            "Commande reçue. Le moteur IA central de "
            "TASSIMO BTP est en cours de connexion. "
            "L'intégration complète permettra à l'IA de "
            "coordonner les différents modules."
        )

    else:

        response_text = (
            "Command received. The central TASSIMO BTP AI "
            "engine is being connected. The complete "
            "integration will allow AI to coordinate the "
            "different platform modules."
        )

    return jsonify({
        "success": True,
        "command": command,
        "language": language,
        "openai_configured": openai_configured,
        "response": response_text
    })


# ============================================================
# DASHBOARD HTML
# ============================================================

DASHBOARD_HTML = r"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
TASSIMO BTP CONSTRUCTION SARL
</title>

<style>

*{
    margin:0;
    padding:0;
    box-sizing:border-box;
    font-family:Arial, sans-serif;
}

body{
    background:#f4f7fb;
    color:#1f2937;
    min-height:100vh;
}

/* =========================================================
   LAYOUT
========================================================= */

.app{
    display:flex;
    min-height:100vh;
}

.sidebar{
    width:260px;
    background:#111827;
    color:white;
    position:fixed;
    top:0;
    left:0;
    bottom:0;
    padding:20px 15px;
    z-index:1000;
    overflow-y:auto;
}

.main{
    margin-left:260px;
    width:calc(100% - 260px);
    min-height:100vh;
}

/* =========================================================
   SIDEBAR
========================================================= */

.brand{
    padding:10px;
    margin-bottom:25px;
}

.brand h2{
    font-size:18px;
    line-height:1.4;
}

.brand p{
    font-size:12px;
    color:#9ca3af;
    margin-top:5px;
}

.nav{
    display:flex;
    flex-direction:column;
    gap:7px;
}

.nav button{
    border:none;
    background:transparent;
    color:#d1d5db;
    text-align:left;
    padding:12px;
    border-radius:9px;
    cursor:pointer;
    font-size:14px;
}

.nav button:hover{
    background:#1f2937;
    color:white;
}

.nav button.active{
    background:#2563eb;
    color:white;
}

/* =========================================================
   MOBILE HEADER
========================================================= */

.mobile-header{
    display:none;
    height:65px;
    background:white;
    align-items:center;
    justify-content:space-between;
    padding:0 15px;
    border-bottom:1px solid #e5e7eb;
    position:sticky;
    top:0;
    z-index:900;
}

.menu-btn{
    border:none;
    background:#111827;
    color:white;
    width:42px;
    height:42px;
    border-radius:8px;
    font-size:20px;
    cursor:pointer;
}

.overlay{
    display:none;
    position:fixed;
    inset:0;
    background:rgba(0,0,0,.45);
    z-index:950;
}

/* =========================================================
   CONTENT
========================================================= */

.content{
    padding:25px;
}

.topbar{
    background:white;
    border-radius:15px;
    padding:20px;
    margin-bottom:20px;
    border:1px solid #e5e7eb;
}

.topbar h1{
    font-size:25px;
    margin-bottom:7px;
}

.topbar p{
    color:#6b7280;
    font-size:14px;
}

.language{
    margin-top:15px;
    display:flex;
    gap:8px;
}

.language button{
    border:1px solid #d1d5db;
    background:white;
    padding:7px 12px;
    border-radius:7px;
    cursor:pointer;
}

.language button.active{
    background:#2563eb;
    color:white;
    border-color:#2563eb;
}

/* =========================================================
   STATISTICS
========================================================= */

.stats{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:15px;
    margin-bottom:20px;
}

.stat{
    background:white;
    border:1px solid #e5e7eb;
    border-radius:15px;
    padding:20px;
}

.stat .icon{
    font-size:25px;
    margin-bottom:10px;
}

.stat h3{
    font-size:27px;
    margin-bottom:5px;
}

.stat p{
    color:#6b7280;
    font-size:13px;
}

/* =========================================================
   AI COMMAND
========================================================= */

.ai-box{
    background:#111827;
    color:white;
    border-radius:15px;
    padding:20px;
    margin-bottom:20px;
}

.ai-box h2{
    font-size:18px;
    margin-bottom:7px;
}

.ai-box p{
    color:#d1d5db;
    font-size:13px;
    margin-bottom:15px;
}

.ai-form{
    display:flex;
    gap:10px;
}

.ai-form input{
    flex:1;
    min-width:0;
    padding:13px;
    border:none;
    border-radius:8px;
    outline:none;
}

.ai-form button{
    border:none;
    background:#2563eb;
    color:white;
    padding:0 18px;
    border-radius:8px;
    cursor:pointer;
}

.ai-response{
    margin-top:15px;
    display:none;
    background:#1f2937;
    padding:12px;
    border-radius:8px;
    font-size:13px;
}

/* =========================================================
   MODULES
========================================================= */

.section-title{
    margin:25px 0 12px;
    font-size:19px;
}

.modules{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:15px;
}

.module{
    background:white;
    border:1px solid #e5e7eb;
    border-radius:15px;
    padding:18px;
    transition:.2s;
}

.module:hover{
    transform:translateY(-2px);
    box-shadow:0 5px 18px rgba(0,0,0,.06);
}

.module-icon{
    font-size:30px;
    margin-bottom:12px;
}

.module h3{
    font-size:15px;
    margin-bottom:7px;
}

.module p{
    font-size:12px;
    color:#6b7280;
}

/* =========================================================
   FOOTER
========================================================= */

.footer{
    text-align:center;
    color:#6b7280;
    font-size:12px;
    padding:30px 10px;
}

/* =========================================================
   TABLET
========================================================= */

@media(max-width:1000px){

    .stats{
        grid-template-columns:repeat(2,1fr);
    }

    .modules{
        grid-template-columns:repeat(2,1fr);
    }

}

/* =========================================================
   MOBILE
========================================================= */

@media(max-width:700px){

    .sidebar{
        transform:translateX(-100%);
        transition:.25s;
        width:270px;
    }

    .sidebar.open{
        transform:translateX(0);
    }

    .overlay.open{
        display:block;
    }

    .main{
        margin-left:0;
        width:100%;
    }

    .mobile-header{
        display:flex;
    }

    .content{
        padding:15px;
    }

    .topbar{
        padding:17px;
    }

    .topbar h1{
        font-size:21px;
    }

    .stats{
        grid-template-columns:1fr 1fr;
        gap:10px;
    }

    .stat{
        padding:15px;
    }

    .stat h3{
        font-size:23px;
    }

    .modules{
        grid-template-columns:1fr;
    }

    .ai-form{
        flex-direction:column;
    }

    .ai-form button{
        padding:12px;
    }

}

</style>

</head>

<body>

<div class="app">

<!-- ======================================================
     SIDEBAR
====================================================== -->

<aside class="sidebar" id="sidebar">

    <div class="brand">

        <h2>
            TASSIMO BTP
        </h2>

        <p>
            CONSTRUCTION SARL
        </p>

    </div>

    <nav class="nav">

        <button class="active">
            🏠 Dashboard
        </button>

        <button>
            🤖 AI Manager
        </button>

        <button>
            📣 Marketing
        </button>

        <button>
            👥 Customers / CRM
        </button>

        <button>
            🏗️ Construction
        </button>

        <button>
            📋 Projects
        </button>

        <button>
            💰 Finance
        </button>

        <button>
            🎓 Training
        </button>

        <button>
            🛒 Digital Store
        </button>

        <button>
            📊 Analytics
        </button>

        <button>
            ⚙️ Administration
        </button>

    </nav>

</aside>

<div
    class="overlay"
    id="overlay"
    onclick="closeMenu()">
</div>

<!-- ======================================================
     MAIN
====================================================== -->

<main class="main">

    <header class="mobile-header">

        <button
            class="menu-btn"
            onclick="openMenu()">
            ☰
        </button>

        <strong>
            TASSIMO BTP
        </strong>

        <span>
            🏗️
        </span>

    </header>

    <div class="content">

        <!-- COMPANY -->

        <section class="topbar">

            <h1 id="companyName">
                {{ company.get("name", "TASSIMO BTP CONSTRUCTION SARL") }}
            </h1>

            <p>
                CEO:
                {{ company.get("ceo", "TAGNE Simo Innocant") }}
            </p>

            <p>
                {{ company.get("location", "Douala – Logpom, Cameroon") }}
            </p>

            <p>
                {{ company.get("slogan", "Together, let us build excellence.") }}
            </p>

            <div class="language">

                <button
                    id="enBtn"
                    class="active"
                    onclick="setLanguage('en')">
                    English
                </button>

                <button
                    id="frBtn"
                    onclick="setLanguage('fr')">
                    Français
                </button>

            </div>

        </section>

        <!-- STATISTICS -->

        <section class="stats">

            <div class="stat">

                <div class="icon">
                    👥
                </div>

                <h3>
                    {{ stats.get("customers", 0) }}
                </h3>

                <p
                    data-en="Customers & Prospects"
                    data-fr="Clients & Prospects">
                    Customers & Prospects
                </p>

            </div>

            <div class="stat">

                <div class="icon">
                    🏗️
                </div>

                <h3>
                    {{ stats.get("projects", 0) }}
                </h3>

                <p
                    data-en="Construction Projects"
                    data-fr="Projets de construction">
                    Construction Projects
                </p>

            </div>

            <div class="stat">

                <div class="icon">
                    💳
                </div>

                <h3>
                    {{ stats.get("payments", 0) }}
                </h3>

                <p
                    data-en="Payments"
                    data-fr="Paiements">
                    Payments
                </p>

            </div>

            <div class="stat">

                <div class="icon">
                    🎓
                </div>

                <h3>
                    {{ stats.get("courses", 0) }}
                </h3>

                <p
                    data-en="Training Courses"
                    data-fr="Formations">
                    Training Courses
                </p>

            </div>

        </section>

        <!-- AI -->

        <section class="ai-box">

            <h2
                data-en="🤖 TASSIMO AI Business Manager"
                data-fr="🤖 Gestionnaire IA TASSIMO">
                🤖 TASSIMO AI Business Manager
            </h2>

            <p
                data-en="Give the AI a business command."
                data-fr="Donnez une commande commerciale à l'IA.">
                Give the AI a business command.
            </p>

            <div class="ai-form">

                <input
                    id="aiCommand"
                    type="text"
                    placeholder="Example: Show today's business report."
                >

                <button
                    onclick="sendAICommand()"
                    data-en="Send"
                    data-fr="Envoyer">
                    Send
                </button>

            </div>

            <div
                class="ai-response"
                id="aiResponse">
            </div>

        </section>

        <!-- MODULES -->

        <h2
            class="section-title"
            data-en="Platform Modules"
            data-fr="Modules de la plateforme">
            Platform Modules
        </h2>

        <section class="modules">

            {% for module in modules %}

            <div class="module">

                <div class="module-icon">
                    {{ module.icon }}
                </div>

                <h3 class="module-name">
                    {{ module.name_en }}
                </h3>

                <p
                    class="module-description"
                    data-en="{{ module.name_en }}"
                    data-fr="{{ module.name_fr }}">
                    {{ module.name_en }}
                </p>

            </div>

            {% endfor %}

        </section>

        <div class="footer">

            TASSIMO BTP CONSTRUCTION SARL © 2026

        </div>

    </div>

</main>

</div>

<script>

let currentLanguage = "en";


/* =========================================================
   MOBILE MENU
========================================================= */

function openMenu(){

    document
        .getElementById("sidebar")
        .classList
        .add("open");

    document
        .getElementById("overlay")
        .classList
        .add("open");
}


function closeMenu(){

    document
        .getElementById("sidebar")
        .classList
        .remove("open");

    document
        .getElementById("overlay")
        .classList
        .remove("open");
}


/* =========================================================
   LANGUAGE
========================================================= */

function setLanguage(language){

    currentLanguage = language;

    document
        .getElementById("enBtn")
        .classList
        .toggle("active", language === "en");

    document
        .getElementById("frBtn")
        .classList
        .toggle("active", language === "fr");


    document
        .querySelectorAll("[data-en]")
        .forEach(element => {

            element.textContent =
                element.getAttribute(
                    language === "fr"
                    ? "data-fr"
                    : "data-en"
                );

        });


    const input =
        document.getElementById("aiCommand");

    if(language === "fr"){

        input.placeholder =
            "Exemple : Affiche le rapport commercial d'aujourd'hui.";

    }else{

        input.placeholder =
            "Example: Show today's business report.";

    }

}


/* =========================================================
   AI COMMAND
========================================================= */

async function sendAICommand(){

    const input =
        document.getElementById("aiCommand");

    const responseBox =
        document.getElementById("aiResponse");

    const command =
        input.value.trim();


    if(!command){

        responseBox.style.display = "block";

        responseBox.textContent =
            currentLanguage === "fr"
            ? "Veuillez entrer une commande."
            : "Please enter a command.";

        return;
    }


    responseBox.style.display = "block";

    responseBox.textContent =
        currentLanguage === "fr"
        ? "Traitement..."
        : "Processing...";


    try{

        const response =
            await fetch("/api/ai", {

                method:"POST",

                headers:{
                    "Content-Type":
                        "application/json"
                },

                body:JSON.stringify({

                    command:command,

                    language:currentLanguage

                })

            });


        const data =
            await response.json();


        responseBox.textContent =
            data.response ||
            data.message ||
            (
                currentLanguage === "fr"
                ? "Aucune réponse."
                : "No response."
            );


    }catch(error){

        responseBox.textContent =
            currentLanguage === "fr"
            ? "Une erreur est survenue."
            : "An error occurred.";

    }

}

</script>

</body>

</html>
"""


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    port = int(
        os.getenv(
            "PORT",
            "5000"
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
