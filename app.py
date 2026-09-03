import os
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask,
    jsonify,
    request,
    render_template_string,
    redirect,
    url_for,
    session
)

from flask_cors import CORS

from database import db


# ============================================================
# TASSIMO BTP CONSTRUCTION SARL
# MAIN APPLICATION
# ============================================================

app = Flask(__name__)

CORS(app)


# ============================================================
# SECURITY / AUTHENTICATION CONFIGURATION
# ============================================================

app.secret_key = os.getenv("FLASK_SECRET_KEY")

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=12)
)


CEO_EMAIL = os.getenv("CEO_EMAIL")
CEO_PASSWORD = os.getenv("CEO_PASSWORD")


def authentication_configured():
    """
    Check whether the CEO authentication credentials
    have been configured in the server environment.
    """

    return bool(
        app.secret_key
        and CEO_EMAIL
        and CEO_PASSWORD
    )


def login_required(view_function):
    """
    Protect dashboard and API routes.

    Unauthenticated browser requests are redirected
    to the login page.

    Unauthenticated API requests receive HTTP 401.
    """

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        if not session.get("authenticated"):

            if request.path.startswith("/api/"):

                return jsonify({
                    "success": False,
                    "authenticated": False,
                    "message": "Authentication required."
                }), 401

            return redirect(url_for("login"))

        return view_function(*args, **kwargs)

    return wrapped_view


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
# LOGIN PAGE
# ============================================================

LOGIN_HTML = r"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
TASSIMO BTP - CEO Login
</title>

<style>

*{
    margin:0;
    padding:0;
    box-sizing:border-box;
    font-family:Arial,sans-serif;
}

body{

    min-height:100vh;

    display:flex;

    align-items:center;

    justify-content:center;

    background:
        linear-gradient(
            135deg,
            #111827,
            #1e3a8a
        );

    padding:20px;

}

.login-container{

    width:100%;

    max-width:430px;

}

.login-card{

    background:white;

    border-radius:20px;

    padding:30px;

    box-shadow:
        0 20px 50px
        rgba(0,0,0,.25);

}

.logo{

    width:70px;

    height:70px;

    margin:0 auto 18px;

    border-radius:18px;

    background:#2563eb;

    color:white;

    display:flex;

    align-items:center;

    justify-content:center;

    font-size:35px;

}

h1{

    text-align:center;

    font-size:24px;

    color:#111827;

    margin-bottom:7px;

}

.subtitle{

    text-align:center;

    color:#6b7280;

    font-size:13px;

    margin-bottom:25px;

}

label{

    display:block;

    font-size:13px;

    font-weight:bold;

    color:#374151;

    margin-bottom:7px;

}

.field{

    margin-bottom:18px;

}

input{

    width:100%;

    padding:13px;

    border:1px solid #d1d5db;

    border-radius:9px;

    outline:none;

    font-size:14px;

}

input:focus{

    border-color:#2563eb;

    box-shadow:
        0 0 0 3px
        rgba(37,99,235,.12);

}

.login-button{

    width:100%;

    border:none;

    background:#2563eb;

    color:white;

    padding:14px;

    border-radius:9px;

    font-size:15px;

    font-weight:bold;

    cursor:pointer;

}

.login-button:hover{

    background:#1d4ed8;

}

.login-button:disabled{

    opacity:.65;

    cursor:not-allowed;

}

.error{

    display:none;

    background:#fee2e2;

    color:#991b1b;

    border:1px solid #fecaca;

    padding:11px;

    border-radius:8px;

    font-size:13px;

    margin-bottom:16px;

}

.info{

    text-align:center;

    color:#9ca3af;

    font-size:11px;

    margin-top:20px;

}

.language{

    display:flex;

    justify-content:center;

    gap:8px;

    margin-top:18px;

}

.language button{

    border:1px solid #d1d5db;

    background:white;

    padding:6px 11px;

    border-radius:7px;

    cursor:pointer;

    font-size:12px;

}

.language button.active{

    background:#2563eb;

    color:white;

    border-color:#2563eb;

}

@media(max-width:480px){

    .login-card{

        padding:24px 18px;

    }

    h1{

        font-size:21px;

    }

}

</style>

</head>

<body>

<div class="login-container">

    <div class="login-card">

        <div class="logo">
            🏗️
        </div>

        <h1>
            TASSIMO BTP
        </h1>

        <p class="subtitle"
           id="subtitle">
            CEO / Administrator Login
        </p>

        <div
            class="error"
            id="errorBox">
        </div>

        <form
            id="loginForm"
            onsubmit="login(event)">

            <div class="field">

                <label
                    id="emailLabel"
                    for="email">
                    CEO Email
                </label>

                <input
                    id="email"
                    type="email"
                    autocomplete="username"
                    required
                >

            </div>

            <div class="field">

                <label
                    id="passwordLabel"
                    for="password">
                    Password
                </label>

                <input
                    id="password"
                    type="password"
                    autocomplete="current-password"
                    required
                >

            </div>

            <button
                class="login-button"
                id="loginButton"
                type="submit">
                Login
            </button>

        </form>

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

        <p
            class="info"
            id="infoText">
            Authorized access only.
        </p>

    </div>

</div>


<script>

let currentLanguage = "en";


function setLanguage(language){

    currentLanguage = language;

    document
        .getElementById("enBtn")
        .classList
        .toggle(
            "active",
            language === "en"
        );

    document
        .getElementById("frBtn")
        .classList
        .toggle(
            "active",
            language === "fr"
        );


    if(language === "fr"){

        document
            .getElementById("subtitle")
            .textContent =
            "Connexion PDG / Administrateur";

        document
            .getElementById("emailLabel")
            .textContent =
            "Email du PDG";

        document
            .getElementById("passwordLabel")
            .textContent =
            "Mot de passe";

        document
            .getElementById("loginButton")
            .textContent =
            "Se connecter";

        document
            .getElementById("infoText")
            .textContent =
            "Accès réservé aux utilisateurs autorisés.";

        document
            .getElementById("email")
            .placeholder =
            "Email du PDG";

        document
            .getElementById("password")
            .placeholder =
            "Mot de passe";

    }else{

        document
            .getElementById("subtitle")
            .textContent =
            "CEO / Administrator Login";

        document
            .getElementById("emailLabel")
            .textContent =
            "CEO Email";

        document
            .getElementById("passwordLabel")
            .textContent =
            "Password";

        document
            .getElementById("loginButton")
            .textContent =
            "Login";

        document
            .getElementById("infoText")
            .textContent =
            "Authorized access only.";

        document
            .getElementById("email")
            .placeholder =
            "CEO email";

        document
            .getElementById("password")
            .placeholder =
            "Password";

    }

}


async function login(event){

    event.preventDefault();

    const email =
        document
            .getElementById("email")
            .value
            .trim();

    const password =
        document
            .getElementById("password")
            .value;

    const errorBox =
        document
            .getElementById("errorBox");

    const button =
        document
            .getElementById("loginButton");


    errorBox.style.display = "none";

    button.disabled = true;

    button.textContent =
        currentLanguage === "fr"
        ? "Connexion..."
        : "Signing in...";


    try{

        const response =
            await fetch(
                "/login",
                {
                    method:"POST",

                    headers:{
                        "Content-Type":
                            "application/json"
                    },

                    body:JSON.stringify({

                        email:email,

                        password:password

                    })
                }
            );


        const data =
            await response.json();


        if(data.success){

            window.location.href =
                "/";

            return;

        }


        errorBox.textContent =
            data.message ||
            (
                currentLanguage === "fr"
                ? "Email ou mot de passe incorrect."
                : "Incorrect email or password."
            );

        errorBox.style.display =
            "block";


    }catch(error){

        errorBox.textContent =
            currentLanguage === "fr"
            ? "Une erreur de connexion est survenue."
            : "A connection error occurred.";

        errorBox.style.display =
            "block";

    }


    button.disabled = false;

    button.textContent =
        currentLanguage === "fr"
        ? "Se connecter"
        : "Login";

}

</script>

</body>

</html>
"""


# ============================================================
# AUTHENTICATION ROUTES
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    # --------------------------------------------------------
    # If already authenticated, go directly to dashboard.
    # --------------------------------------------------------

    if request.method == "GET":

        if session.get("authenticated"):

            return redirect(url_for("dashboard"))

        return render_template_string(
            LOGIN_HTML
        )


    # --------------------------------------------------------
    # POST LOGIN
    # --------------------------------------------------------

    data = request.get_json(
        silent=True
    ) or {}


    email = str(
        data.get("email", "")
    ).strip()


    password = str(
        data.get("password", "")
    )


    # --------------------------------------------------------
    # Check server configuration
    # --------------------------------------------------------

    if not authentication_configured():

        return jsonify({
            "success": False,
            "message":
                "CEO authentication is not configured on the server."
        }), 500


    # --------------------------------------------------------
    # Validate credentials
    # --------------------------------------------------------

    if (
        email.lower() !=
        str(CEO_EMAIL).strip().lower()
        or
        password != CEO_PASSWORD
    ):

        return jsonify({
            "success": False,
            "message":
                "Incorrect email or password."
        }), 401


    # --------------------------------------------------------
    # Create authenticated session
    # --------------------------------------------------------

    session.clear()

    session.permanent = True

    session["authenticated"] = True

    session["role"] = "ceo"

    session["email"] = email


    return jsonify({
        "success": True,
        "message": "Login successful.",
        "role": "ceo"
    })


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# ============================================================
# AUTHENTICATION STATUS
# ============================================================

@app.route("/api/auth/me", methods=["GET"])
def api_auth_me():

    if not session.get("authenticated"):

        return jsonify({
            "success": True,
            "authenticated": False
        })


    return jsonify({

        "success": True,

        "authenticated": True,

        "role":
            session.get(
                "role",
                "ceo"
            ),

        "email":
            session.get(
                "email"
            )

    })


# ============================================================
# DATABASE / SYSTEM HELPERS
# ============================================================

def get_dashboard_data():

    """
    Collect the information needed by the CEO dashboard.

    The dashboard reads real information from Supabase
    through the central database layer.
    """

    stats = db.get_dashboard_stats()

    profile = db.get_company_profile()


    if not profile:

        profile = COMPANY.copy()


    return {

        "company": profile,

        "stats": stats,

        "modules": MODULES,

        "generated_at":
            datetime.utcnow().isoformat() + "Z"

    }


# ============================================================
# DASHBOARD PAGE
# ============================================================

@app.route("/")
@login_required
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
#
# This endpoint intentionally remains PUBLIC so Render/
# monitoring systems can verify that the application is alive.
# ============================================================

@app.route("/api/status", methods=["GET"])
def api_status():

    stats = db.get_dashboard_stats()


    return jsonify({

        "success": True,

        "application":
            "TASSIMO BTP CONSTRUCTION SARL",

        "status":
            "online",

        "database_connected":
            stats.get(
                "database_connected",
                False
            ),

        "timestamp":
            datetime.utcnow().isoformat() + "Z"

    })


# ============================================================
# API: COMPANY
# ============================================================

@app.route("/api/company", methods=["GET"])
@login_required
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
@login_required
def api_modules():

    return jsonify({

        "success": True,

        "modules": MODULES

    })


# ============================================================
# API: DASHBOARD STATISTICS
# ============================================================

@app.route("/api/dashboard", methods=["GET"])
@login_required
def api_dashboard():

    data = get_dashboard_data()


    return jsonify({

        "success": True,

        "company":
            data["company"],

        "stats":
            data["stats"],

        "modules":
            data["modules"],

        "generated_at":
            data["generated_at"]

    })


# ============================================================
# API: CUSTOMERS
# ============================================================

@app.route("/api/customers", methods=["GET"])
@login_required
def api_customers():

    customers =
        db.get_customers(
            limit=100
        )


    return jsonify({

        "success": True,

        "count":
            len(customers),

        "customers":
            customers

    })


# ============================================================
# API: PROJECTS
# ============================================================

@app.route("/api/projects", methods=["GET"])
@login_required
def api_projects():

    projects =
        db.get_projects(
            limit=100
        )


    return jsonify({

        "success": True,

        "count":
            len(projects),

        "projects":
            projects

    })


# ============================================================
# API: PAYMENTS
# ============================================================

@app.route("/api/payments", methods=["GET"])
@login_required
def api_payments():

    payments =
        db.get_payments(
            limit=100
        )


    return jsonify({

        "success": True,

        "count":
            len(payments),

        "payments":
            payments

    })


# ============================================================
# API: COURSES
# ============================================================

@app.route("/api/courses", methods=["GET"])
@login_required
def api_courses():

    courses =
        db.get_courses(
            limit=100
        )


    return jsonify({

        "success": True,

        "count":
            len(courses),

        "courses":
            courses

    })


# ============================================================
# API: AI COMMAND FOUNDATION
# ============================================================

@app.route("/api/ai", methods=["POST"])
@login_required
def api_ai():

    data =
        request.get_json(
            silent=True
        ) or {}


    command = str(

        data.get(
            "command",
            ""
        )

    ).strip()


    language = str(

        data.get(
            "language",
            "en"
        )

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

        os.getenv(
            "OPENAI_API_KEY"
        )

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

        "command":
            command,

        "language":
            language,

        "openai_configured":
            openai_configured,

        "response":
            response_text

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
    margin-bottom:3px;
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

<aside
    class="sidebar"
    id="sidebar">

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

        <!-- LOGOUT -->

        <button
            onclick="window.location.href='/logout'">

            🚪 Logout

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

                {{ company.get(
                    "name",
                    company.get(
                        "business_name",
                        "TASSIMO BTP CONSTRUCTION SARL"
                    )
                ) }}

            </h1>


            <p>

                CEO:

                {{ company.get(
                    "ceo",
                    company.get(
                        "ceo_name",
                        "TAGNE Simo Innocant"
                    )
                ) }}

            </p>


            <p>

                {{ company.get(
                    "location",
                    "Douala – Logpom, Cameroon"
                ) }}

            </p>


            <p>

                {{ company.get(
                    "slogan",
                    "Together, let us build excellence."
                ) }}

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

                    {{ stats.get(
                        "customers",
                        0
                    ) }}

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

                    {{ stats.get(
                        "projects",
                        0
                    ) }}

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

                    {{ stats.get(
                        "payments",
                        0
                    ) }}

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

                    {{ stats.get(
                        "courses",
                        0
                    ) }}

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
        .toggle(
            "active",
            language === "en"
        );


    document
        .getElementById("frBtn")
        .classList
        .toggle(
            "active",
            language === "fr"
        );


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
        document.getElementById(
            "aiCommand"
        );


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
        document.getElementById(
            "aiCommand"
        );


    const responseBox =
        document.getElementById(
            "aiResponse"
        );


    const command =
        input.value.trim();


    if(!command){

        responseBox.style.display =
            "block";


        responseBox.textContent =

            currentLanguage === "fr"

            ? "Veuillez entrer une commande."

            : "Please enter a command.";

        return;

    }


    responseBox.style.display =
        "block";


    responseBox.textContent =

        currentLanguage === "fr"

        ? "Traitement..."

        : "Processing...";


    try{

        const response =

            await fetch(
                "/api/ai",
                {

                    method:"POST",

                    headers:{
                        "Content-Type":
                            "application/json"
                    },

                    body:JSON.stringify({

                        command:
                            command,

                        language:
                            currentLanguage

                    })

                }
            );


        const data =
            await response.json();


        if(
            response.status === 401
            ||
            data.authenticated === false
        ){

            window.location.href =
                "/login";

            return;

        }


        responseBox.textContent =

            data.response

            ||

            data.message

            ||

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
