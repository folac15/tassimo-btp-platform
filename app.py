from flask import Flask, jsonify, request, render_template_string
import os
from datetime import datetime

app = Flask(__name__)

# ============================================================
# TASSIMO BTP CONSTRUCTION SARL
# MODULE 1 - AI BUSINESS MANAGER & PLATFORM FOUNDATION
# ============================================================

COMPANY = {
    "name": "TASSIMO BTP CONSTRUCTION SARL",
    "ceo": "TAGNE Simo Innocant",
    "location": "Douala – Logpom, Cameroon",
    "slogan": "Together, let us build excellence."
}

MODULES = [
    {
        "id": 1,
        "icon": "🤖",
        "en": "AI Business Manager",
        "fr": "Gestionnaire IA"
    },
    {
        "id": 2,
        "icon": "📣",
        "en": "Marketing & Social Media",
        "fr": "Marketing & Réseaux sociaux"
    },
    {
        "id": 3,
        "icon": "👥",
        "en": "CRM & Customers",
        "fr": "CRM & Clients"
    },
    {
        "id": 4,
        "icon": "🏗️",
        "en": "Construction AI & Estimation",
        "fr": "IA Construction & Estimation"
    },
    {
        "id": 5,
        "icon": "📦",
        "en": "Projects & Operations",
        "fr": "Projets & Opérations"
    },
    {
        "id": 6,
        "icon": "💰",
        "en": "Finance & Documents",
        "fr": "Finance & Documents"
    },
    {
        "id": 7,
        "icon": "🎓",
        "en": "Professional Training",
        "fr": "Formation professionnelle"
    },
    {
        "id": 8,
        "icon": "🛒",
        "en": "Digital Training Store",
        "fr": "Boutique de formations"
    },
    {
        "id": 9,
        "icon": "📊",
        "en": "Analytics & Intelligence",
        "fr": "Analyses & Intelligence"
    },
    {
        "id": 10,
        "icon": "⚙️",
        "en": "Administration & Integrations",
        "fr": "Administration & Intégrations"
    }
]


# ============================================================
# DASHBOARD
# ============================================================

DASHBOARD_HTML = r"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">
<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<meta name="theme-color" content="#0f172a">

<title>TASSIMO BTP | AI Business Platform</title>

<style>

*{
    margin:0;
    padding:0;
    box-sizing:border-box;
}

:root{
    --primary:#0f172a;
    --secondary:#1e293b;
    --accent:#f59e0b;
    --accent-dark:#d97706;
    --background:#f1f5f9;
    --card:#ffffff;
    --text:#0f172a;
    --muted:#64748b;
    --border:#e2e8f0;
    --success:#16a34a;
    --danger:#dc2626;
}

body{
    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Arial,
        sans-serif;

    background:var(--background);
    color:var(--text);
    min-height:100vh;
}


/* ============================================================
   APP LAYOUT
   ============================================================ */

.app{
    display:flex;
    min-height:100vh;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

.sidebar{
    width:280px;
    background:var(--primary);
    color:white;
    position:fixed;
    left:0;
    top:0;
    bottom:0;
    overflow-y:auto;
    z-index:1000;
    transition:transform .3s ease;
}

.brand{
    padding:24px 20px;
    border-bottom:1px solid rgba(255,255,255,.1);
}

.brand-name{
    font-size:19px;
    font-weight:800;
    line-height:1.25;
}

.brand-subtitle{
    color:#94a3b8;
    font-size:12px;
    margin-top:6px;
}

.ceo-box{
    margin:18px 14px;
    padding:14px;
    background:rgba(255,255,255,.06);
    border-radius:14px;
}

.ceo-label{
    font-size:11px;
    color:#94a3b8;
    text-transform:uppercase;
    letter-spacing:.6px;
}

.ceo-name{
    margin-top:5px;
    font-size:14px;
    font-weight:700;
}

.navigation{
    padding:10px;
}

.nav-section{
    color:#64748b;
    font-size:10px;
    text-transform:uppercase;
    letter-spacing:1px;
    padding:14px 12px 7px;
}

.nav-item{
    width:100%;
    border:0;
    background:transparent;
    color:#cbd5e1;
    padding:12px;
    border-radius:10px;
    display:flex;
    align-items:center;
    gap:11px;
    text-align:left;
    cursor:pointer;
    margin-bottom:3px;
    font-size:13px;
    transition:.2s;
}

.nav-item:hover{
    background:rgba(255,255,255,.08);
    color:white;
}

.nav-item.active{
    background:var(--accent);
    color:#111827;
    font-weight:700;
}

.nav-icon{
    width:24px;
    text-align:center;
    font-size:17px;
}


/* ============================================================
   MAIN
   ============================================================ */

.main{
    margin-left:280px;
    width:calc(100% - 280px);
    min-width:0;
}

.topbar{
    height:74px;
    background:white;
    border-bottom:1px solid var(--border);
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding:0 28px;
    position:sticky;
    top:0;
    z-index:900;
}

.mobile-menu{
    display:none;
    border:0;
    background:transparent;
    font-size:25px;
    cursor:pointer;
}

.topbar-title{
    font-size:20px;
    font-weight:800;
}

.topbar-right{
    display:flex;
    align-items:center;
    gap:10px;
}

.language-btn{
    border:1px solid var(--border);
    background:white;
    border-radius:9px;
    padding:8px 11px;
    cursor:pointer;
    font-weight:700;
}

.ceo-avatar{
    width:38px;
    height:38px;
    border-radius:50%;
    background:var(--primary);
    color:white;
    display:flex;
    align-items:center;
    justify-content:center;
    font-weight:800;
}


/* ============================================================
   CONTENT
   ============================================================ */

.content{
    padding:28px;
    max-width:1600px;
    margin:auto;
}

.welcome{
    background:linear-gradient(
        135deg,
        #0f172a,
        #1e293b
    );

    color:white;
    border-radius:20px;
    padding:30px;
    margin-bottom:22px;
    position:relative;
    overflow:hidden;
}

.welcome:after{
    content:"";
    position:absolute;
    width:220px;
    height:220px;
    right:-80px;
    top:-90px;
    border-radius:50%;
    background:rgba(245,158,11,.18);
}

.welcome-label{
    color:#fbbf24;
    font-size:12px;
    font-weight:800;
    text-transform:uppercase;
    letter-spacing:1px;
}

.welcome h1{
    margin-top:7px;
    font-size:29px;
}

.welcome p{
    color:#cbd5e1;
    margin-top:8px;
    max-width:720px;
    line-height:1.6;
}


/* ============================================================
   KPI CARDS
   ============================================================ */

.stats{
    display:grid;
    grid-template-columns:
        repeat(4,minmax(0,1fr));
    gap:16px;
    margin-bottom:22px;
}

.stat-card{
    background:white;
    border:1px solid var(--border);
    border-radius:16px;
    padding:20px;
}

.stat-top{
    display:flex;
    justify-content:space-between;
    align-items:center;
}

.stat-icon{
    width:42px;
    height:42px;
    border-radius:11px;
    background:#f8fafc;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:20px;
}

.stat-label{
    color:var(--muted);
    font-size:12px;
    margin-top:15px;
}

.stat-value{
    font-size:27px;
    font-weight:800;
    margin-top:3px;
}


/* ============================================================
   AI COMMAND CENTER
   ============================================================ */

.ai-card{
    background:white;
    border:1px solid var(--border);
    border-radius:18px;
    padding:22px;
    margin-bottom:22px;
}

.section-title{
    font-size:17px;
    font-weight:800;
}

.section-subtitle{
    color:var(--muted);
    font-size:13px;
    margin-top:5px;
}

.ai-input-row{
    display:flex;
    gap:10px;
    margin-top:18px;
}

.ai-input{
    flex:1;
    border:1px solid var(--border);
    border-radius:11px;
    padding:13px 15px;
    outline:none;
    font-size:14px;
}

.ai-input:focus{
    border-color:var(--accent);
}

.ai-button{
    border:0;
    background:var(--accent);
    color:#111827;
    padding:0 20px;
    border-radius:11px;
    font-weight:800;
    cursor:pointer;
}

.ai-response{
    display:none;
    margin-top:14px;
    padding:14px;
    border-radius:11px;
    background:#f8fafc;
    border:1px solid var(--border);
    line-height:1.6;
    font-size:13px;
}


/* ============================================================
   MODULES
   ============================================================ */

.modules{
    display:grid;
    grid-template-columns:
        repeat(5,minmax(0,1fr));
    gap:14px;
}

.module-card{
    background:white;
    border:1px solid var(--border);
    border-radius:16px;
    padding:18px;
    cursor:pointer;
    transition:
        transform .2s,
        box-shadow .2s,
        border-color .2s;
}

.module-card:hover{
    transform:translateY(-2px);
    box-shadow:0 10px 25px rgba(15,23,42,.08);
    border-color:#cbd5e1;
}

.module-icon{
    font-size:26px;
}

.module-number{
    color:var(--muted);
    font-size:11px;
    margin-top:14px;
}

.module-name{
    font-weight:750;
    font-size:14px;
    margin-top:5px;
    line-height:1.35;
}


/* ============================================================
   MOBILE OVERLAY
   ============================================================ */

.overlay{
    display:none;
    position:fixed;
    inset:0;
    background:rgba(0,0,0,.45);
    z-index:999;
}


/* ============================================================
   RESPONSIVE TABLET
   ============================================================ */

@media(max-width:1200px){

    .modules{
        grid-template-columns:
            repeat(3,minmax(0,1fr));
    }

    .stats{
        grid-template-columns:
            repeat(2,minmax(0,1fr));
    }

}


/* ============================================================
   RESPONSIVE MOBILE
   ============================================================ */

@media(max-width:768px){

    .sidebar{
        transform:translateX(-100%);
        width:280px;
    }

    .sidebar.open{
        transform:translateX(0);
    }

    .overlay.show{
        display:block;
    }

    .main{
        margin-left:0;
        width:100%;
    }

    .topbar{
        padding:0 15px;
        height:64px;
    }

    .mobile-menu{
        display:block;
    }

    .topbar-title{
        font-size:16px;
        margin-right:auto;
        margin-left:10px;
    }

    .ceo-avatar{
        display:none;
    }

    .content{
        padding:15px;
    }

    .welcome{
        padding:22px;
        border-radius:16px;
    }

    .welcome h1{
        font-size:23px;
    }

    .stats{
        grid-template-columns:
            repeat(2,minmax(0,1fr));
        gap:10px;
    }

    .stat-card{
        padding:15px;
    }

    .stat-value{
        font-size:22px;
    }

    .ai-card{
        padding:16px;
    }

    .ai-input-row{
        flex-direction:column;
    }

    .ai-button{
        height:45px;
    }

    .modules{
        grid-template-columns:
            repeat(2,minmax(0,1fr));
        gap:10px;
    }

    .module-card{
        padding:14px;
    }

}


/* ============================================================
   SMALL PHONES
   ============================================================ */

@media(max-width:420px){

    .stats{
        grid-template-columns:1fr 1fr;
    }

    .module-name{
        font-size:13px;
    }

    .welcome p{
        font-size:13px;
    }

    .language-btn{
        padding:7px 9px;
    }

}

</style>

</head>


<body>

<div class="app">

    <div class="overlay"
         id="overlay"
         onclick="closeSidebar()">
    </div>


    <!-- SIDEBAR -->

    <aside class="sidebar" id="sidebar">

        <div class="brand">

            <div class="brand-name">
                TASSIMO BTP
            </div>

            <div class="brand-subtitle">
                CONSTRUCTION SARL
            </div>

        </div>


        <div class="ceo-box">

            <div class="ceo-label"
                 data-en="CEO / PDG"
                 data-fr="DG / PDG">
                CEO / PDG
            </div>

            <div class="ceo-name">
                TAGNE Simo Innocant
            </div>

        </div>


        <nav class="navigation">

            <div class="nav-section"
                 data-en="Main"
                 data-fr="Principal">
                Main
            </div>


            {% for module in modules %}

            <button
                class="nav-item {% if module.id == 1 %}active{% endif %}"
                onclick="selectModule({{ module.id }})">

                <span class="nav-icon">
                    {{ module.icon }}
                </span>

                <span
                    data-en="{{ module.en }}"
                    data-fr="{{ module.fr }}">
                    {{ module.en }}
                </span>

            </button>

            {% endfor %}

        </nav>

    </aside>


    <!-- MAIN -->

    <main class="main">


        <!-- TOPBAR -->

        <header class="topbar">

            <button
                class="mobile-menu"
                onclick="openSidebar()">
                ☰
            </button>

            <div class="topbar-title"
                 id="pageTitle">
                AI Business Manager
            </div>


            <div class="topbar-right">

                <button
                    class="language-btn"
                    onclick="toggleLanguage()"
                    id="languageButton">
                    FR
                </button>

                <div class="ceo-avatar">
                    TS
                </div>

            </div>

        </header>


        <!-- CONTENT -->

        <section class="content">


            <!-- WELCOME -->

            <div class="welcome">

                <div class="welcome-label"
                     data-en="TASSIMO AI BUSINESS PLATFORM"
                     data-fr="PLATEFORME DE GESTION IA TASSIMO">
                    TASSIMO AI BUSINESS PLATFORM
                </div>

                <h1
                    data-en="Welcome, CEO"
                    data-fr="Bienvenue, PDG">
                    Welcome, CEO
                </h1>

                <p
                    data-en="Your central business command center for construction, customers, marketing, finance, projects and professional training."
                    data-fr="Votre centre de contrôle central pour la construction, les clients, le marketing, les finances, les projets et la formation professionnelle.">
                    Your central business command center for construction,
                    customers, marketing, finance, projects and professional training.
                </p>

            </div>


            <!-- STATS -->

            <div class="stats">


                <div class="stat-card">

                    <div class="stat-top">

                        <div>
                            <div class="stat-label"
                                 data-en="CUSTOMERS"
                                 data-fr="CLIENTS">
                                CUSTOMERS
                            </div>

                            <div class="stat-value">
                                0
                            </div>
                        </div>

                        <div class="stat-icon">
                            👥
                        </div>

                    </div>

                </div>


                <div class="stat-card">

                    <div class="stat-top">

                        <div>
                            <div class="stat-label"
                                 data-en="PROJECTS"
                                 data-fr="PROJETS">
                                PROJECTS
                            </div>

                            <div class="stat-value">
                                0
                            </div>
                        </div>

                        <div class="stat-icon">
                            🏗️
                        </div>

                    </div>

                </div>


                <div class="stat-card">

                    <div class="stat-top">

                        <div>
                            <div class="stat-label"
                                 data-en="REVENUE"
                                 data-fr="REVENUS">
                                REVENUE
                            </div>

                            <div class="stat-value">
                                0 FCFA
                            </div>
                        </div>

                        <div class="stat-icon">
                            💰
                        </div>

                    </div>

                </div>


                <div class="stat-card">

                    <div class="stat-top">

                        <div>
                            <div class="stat-label"
                                 data-en="AI STATUS"
                                 data-fr="ÉTAT DE L'IA">
                                AI STATUS
                            </div>

                            <div class="stat-value"
                                 style="color:#16a34a;font-size:18px;"
                                 data-en="Ready"
                                 data-fr="Prête">
                                Ready
                            </div>
                        </div>

                        <div class="stat-icon">
                            🤖
                        </div>

                    </div>

                </div>

            </div>


            <!-- AI COMMAND CENTER -->

            <div class="ai-card">

                <div class="section-title"
                     data-en="AI Business Command Center"
                     data-fr="Centre de commande IA">
                    AI Business Command Center
                </div>

                <div class="section-subtitle"
                     data-en="Give the TASSIMO AI assistant a business command."
                     data-fr="Donnez une commande commerciale à l'assistant IA TASSIMO.">
                    Give the TASSIMO AI assistant a business command.
                </div>


                <div class="ai-input-row">

                    <input
                        id="aiCommand"
                        class="ai-input"
                        type="text"
                        placeholder="Example: Prepare today's business report"
                        data-placeholder-en="Example: Prepare today's business report"
                        data-placeholder-fr="Exemple : Prépare le rapport commercial d'aujourd'hui">

                    <button
                        class="ai-button"
                        onclick="runAI()"
                        data-en="Ask AI"
                        data-fr="Demander à l'IA">
                        Ask AI
                    </button>

                </div>


                <div
                    id="aiResponse"
                    class="ai-response">
                </div>

            </div>


            <!-- MODULES -->

            <div class="ai-card">

                <div class="section-title"
                     data-en="Business Modules"
                     data-fr="Modules de l'entreprise">
                    Business Modules
                </div>

                <div class="section-subtitle"
                     data-en="Your complete TASSIMO business system."
                     data-fr="Votre système complet de gestion TASSIMO.">
                    Your complete TASSIMO business system.
                </div>

            </div>


            <div class="modules">

                {% for module in modules %}

                <div
                    class="module-card"
                    onclick="selectModule({{ module.id }})">

                    <div class="module-icon">
                        {{ module.icon }}
                    </div>

                    <div class="module-number">
                        MODULE {{ module.id }}
                    </div>

                    <div
                        class="module-name"
                        data-en="{{ module.en }}"
                        data-fr="{{ module.fr }}">
                        {{ module.en }}
                    </div>

                </div>

                {% endfor %}

            </div>


        </section>

    </main>

</div>


<script>

let currentLanguage = "en";


const moduleNames = {
{% for module in modules %}
    {{ module.id }}: {
        en: "{{ module.en }}",
        fr: "{{ module.fr }}"
    }{% if not loop.last %},{% endif %}
{% endfor %}
};


function openSidebar(){

    document
        .getElementById("sidebar")
        .classList.add("open");

    document
        .getElementById("overlay")
        .classList.add("show");
}


function closeSidebar(){

    document
        .getElementById("sidebar")
        .classList.remove("open");

    document
        .getElementById("overlay")
        .classList.remove("show");
}


function selectModule(moduleId){

    const module = moduleNames[moduleId];

    document
        .getElementById("pageTitle")
        .textContent =
        module[currentLanguage];

    closeSidebar();

    document
        .querySelectorAll(".nav-item")
        .forEach((item, index) => {

            item.classList.toggle(
                "active",
                index === moduleId - 1
            );

        });

    if(moduleId !== 1){

        const response =
            document.getElementById("aiResponse");

        response.style.display = "block";

        response.textContent =
            currentLanguage === "en"
            ? module.en + " is part of the TASSIMO platform and will be activated during its development phase."
            : module.fr + " fait partie de la plateforme TASSIMO et sera activé pendant sa phase de développement.";

    }

}


function toggleLanguage(){

    currentLanguage =
        currentLanguage === "en"
        ? "fr"
        : "en";

    updateLanguage();

}


function updateLanguage(){

    document
        .querySelectorAll("[data-en]")
        .forEach(element => {

            element.textContent =
                element.getAttribute(
                    "data-" + currentLanguage
                );

        });


    const input =
        document.getElementById("aiCommand");

    input.placeholder =
        input.getAttribute(
            "data-placeholder-" + currentLanguage
        );


    document
        .getElementById("languageButton")
        .textContent =
        currentLanguage === "en"
        ? "FR"
        : "EN";


    const active =
        document.querySelector(
            ".nav-item.active"
        );

    if(active){

        const index =
            Array.from(
                document.querySelectorAll(
                    ".nav-item"
                )
            ).indexOf(active);

        if(index >= 0){

            document.getElementById(
                "pageTitle"
            ).textContent =
                moduleNames[index + 1][
                    currentLanguage
                ];

        }

    }

}


async function runAI(){

    const input =
        document.getElementById("aiCommand");

    const response =
        document.getElementById("aiResponse");

    const command =
        input.value.trim();

    if(!command){

        response.style.display = "block";

        response.textContent =
            currentLanguage === "en"
            ? "Please enter a command."
            : "Veuillez saisir une commande.";

        return;
    }


    response.style.display = "block";

    response.textContent =
        currentLanguage === "en"
        ? "TASSIMO AI is processing your command..."
        : "L'IA TASSIMO traite votre commande...";


    try{

        const result =
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
            await result.json();


        response.textContent =
            data.reply ||
            (
                currentLanguage === "en"
                ? "The AI command has been received."
                : "La commande IA a été reçue."
            );

    }
    catch(error){

        response.textContent =
            currentLanguage === "en"
            ? "The command was received, but the AI service is not connected yet."
            : "La commande a été reçue, mais le service IA n'est pas encore connecté.";

    }

}


document
    .getElementById("aiCommand")
    .addEventListener(
        "keydown",
        function(event){

            if(event.key === "Enter"){
                runAI();
            }

        }
    );

</script>

</body>
</html>
"""


# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def home():

    return render_template_string(
        DASHBOARD_HTML,
        modules=MODULES
    )


@app.route("/api/status")
def status():

    return jsonify({
        "success": True,
        "platform": "TASSIMO BTP CONSTRUCTION SARL",
        "status": "online",
        "module": 1,
        "module_name": "AI Business Manager & Foundation",
        "language_support": ["English", "French"],
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route("/api/company")
def company():

    return jsonify({
        "success": True,
        "company": COMPANY
    })


@app.route("/api/modules")
def modules():

    return jsonify({
        "success": True,
        "modules": MODULES
    })


@app.route("/api/ai", methods=["POST"])
def ai_command():

    data = request.get_json(silent=True) or {}

    command = str(
        data.get("command", "")
    ).strip()

    language = str(
        data.get("language", "en")
    ).lower()

    if not command:

        return jsonify({
            "success": False,
            "reply": (
                "Please enter a business command."
                if language != "fr"
                else
                "Veuillez saisir une commande commerciale."
            )
        }), 400


    # --------------------------------------------------------
    # OpenAI connection will be activated in the AI layer.
    # --------------------------------------------------------

    openai_key_exists = bool(
        os.getenv("OPENAI_API_KEY")
    )


    if not openai_key_exists:

        reply = (
            "Your command has been received by the "
            "TASSIMO AI Business Manager. The OpenAI "
            "intelligence connection will be activated "
            "during the AI integration stage."
            if language != "fr"
            else
            "Votre commande a été reçue par le "
            "Gestionnaire IA TASSIMO. La connexion "
            "à l'intelligence OpenAI sera activée "
            "pendant l'étape d'intégration de l'IA."
        )

        return jsonify({
            "success": True,
            "ai_connected": False,
            "reply": reply
        })


    return jsonify({
        "success": True,
        "ai_connected": True,
        "reply": (
            "AI connection detected. Full business intelligence "
            "processing will be activated as we complete the "
            "AI Business Manager module."
            if language != "fr"
            else
            "Connexion IA détectée. Le traitement complet de "
            "l'intelligence commerciale sera activé au fur et "
            "à mesure de la finalisation du module Gestionnaire IA."
        )
    })


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
