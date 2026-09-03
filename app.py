from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime, timezone
import requests
import os
import time
import threading
import traceback


app = Flask(__name__)
CORS(app)


# =========================================================
# ENVIRONMENT VARIABLES
# =========================================================

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY")

SUPABASE_PROJECT_URL = "https://xfjroysinifwncfjvrsg.supabase.co"

WHATSAPP_VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN")
WHATSAPP_ACCESS_TOKEN = os.environ.get("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_BUSINESS_ACCOUNT_ID = os.environ.get(
    "WHATSAPP_BUSINESS_ACCOUNT_ID"
)


# =========================================================
# OPENROUTER AI MODELS
# =========================================================

OPENROUTER_PRIMARY_MODEL = "openai/gpt-oss-20b:free"

OPENROUTER_FREE_ROUTER_MODEL = "openrouter/free"


# =========================================================
# SUPABASE TABLE URLS
# =========================================================

CUSTOMERS_URL = SUPABASE_PROJECT_URL + "/rest/v1/customers"

BUSINESS_ACCOUNTS_URL = (
    SUPABASE_PROJECT_URL + "/rest/v1/business_accounts"
)

AUTOMATION_SETTINGS_URL = (
    SUPABASE_PROJECT_URL + "/rest/v1/automation_settings"
)

AI_CONVERSATIONS_URL = (
    SUPABASE_PROJECT_URL + "/rest/v1/ai_conversations"
)

INTEGRATIONS_URL = (
    SUPABASE_PROJECT_URL + "/rest/v1/integrations"
)

MESSAGES_URL = (
    SUPABASE_PROJECT_URL + "/rest/v1/messages"
)


# =========================================================
# TIME
# =========================================================

def now_iso():
    return datetime.now(timezone.utc).isoformat()


# =========================================================
# SUPABASE HEADERS
# =========================================================

def supabase_headers(prefer=None):

    headers = {
        "apikey": str(SUPABASE_SECRET_KEY or ""),
        "Authorization": "Bearer " + str(
            SUPABASE_SECRET_KEY or ""
        ),
        "Content-Type": "application/json"
    }

    if prefer:
        headers["Prefer"] = prefer

    return headers


# =========================================================
# WEBSITE
# =========================================================

@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/index.html")
def index_page():
    return send_from_directory(".", "index.html")


@app.route("/<path:filename>")
def serve_files(filename):

    if filename.endswith((".html", ".css", ".js")):
        return send_from_directory(".", filename)

    return "File not found", 404


# =========================================================
# API STATUS
# =========================================================

@app.route("/api/status")
def status():

    return jsonify({
        "status": "online",
        "message": "NexaFlow AI API is working"
    })


# =========================================================
# AUTHENTICATED USER
# =========================================================

def get_authenticated_user():

    authorization = request.headers.get("Authorization")

    if not authorization:
        return None

    if not authorization.startswith("Bearer "):
        return None

    access_token = authorization.replace(
        "Bearer ",
        "",
        1
    ).strip()

    if not access_token:
        return None

    if not SUPABASE_SECRET_KEY:

        print(
            "SUPABASE_SECRET_KEY is not configured."
        )

        return None

    try:

        response = requests.get(
            SUPABASE_PROJECT_URL + "/auth/v1/user",
            headers={
                "apikey": SUPABASE_SECRET_KEY,
                "Authorization":
                    "Bearer " + access_token
            },
            timeout=15
        )

        print(
            "Supabase authentication status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "Supabase authentication error:",
                response.text
            )

            return None

        user = response.json()

        if not user.get("id"):
            return None

        return user

    except Exception as error:

        print(
            "Authentication exception:",
            error
        )

        traceback.print_exc()

        return None


# =========================================================
# SYSTEM PROMPT
# =========================================================

NEXAFLOW_SYSTEM_PROMPT = """
You are NexaFlow AI, the intelligent conversational assistant inside the NexaFlow Business Management Platform.

Help with:

- Business management
- Customer service
- Marketing
- Sales
- Business ideas
- Business planning
- Mathematics
- Physics
- Engineering
- Education
- General knowledge
- Writing
- Communication
- Problem solving

Always use conversation history when supplied.

Understand short follow-up messages from context.

If the user says "give me an example", give an example of the current topic.

If the user says "another one", give a different example.

If the user says "solve it", solve the most recent relevant problem.

If the user says "why", explain the previous statement.

If the user says "make it easier", simplify the previous answer.

If the user says "continue" or "go on", continue the current topic.

For mathematics and physics:

- Explain clearly.
- Give formulas when useful.
- Define variables when useful.
- Show reasoning.
- Give examples when requested.
- Solve step by step when requested.

For education:

- Explain before giving examples when appropriate.
- Do not give an exercise answer unless requested.
- Correct mistakes politely.

For business:

- Give practical recommendations.
- Consider African and Cameroonian realities where relevant.
- Do not invent prices, statistics or regulations.

Do not claim to have performed an action that you did not perform.

Be accurate, natural, helpful and conversational.
"""


# =========================================================
# SUPABASE GENERIC HELPERS
# =========================================================

def supabase_get(url, params):

    return requests.get(
        url,
        headers=supabase_headers(),
        params=params,
        timeout=15
    )


def supabase_insert(url, data):

    return requests.post(
        url,
        headers=supabase_headers(
            "return=representation"
        ),
        json=data,
        timeout=15
    )


def supabase_update(url, params, data):

    return requests.patch(
        url,
        headers=supabase_headers(
            "return=representation"
        ),
        params=params,
        json=data,
        timeout=15
    )


def supabase_delete(url, params):

    return requests.delete(
        url,
        headers=supabase_headers(),
        params=params,
        timeout=15
    )


def first_row(response):

    try:
        data = response.json()

    except Exception:
        return None

    if isinstance(data, list) and data:
        return data[0]

    return None


# =========================================================
# AI CONVERSATION SAVE
# =========================================================

def save_ai_conversation(
    user_id,
    question,
    answer
):

    if not user_id:
        return False

    data = {
        "user_id": user_id,
        "question": question,
        "answer": answer,
        "created_at": now_iso()
    }

    try:

        response = supabase_insert(
            AI_CONVERSATIONS_URL,
            data
        )

        print(
            "AI conversation SAVE:",
            response.status_code,
            response.text
        )

        return response.status_code in (
            200,
            201
        )

    except Exception as error:

        print(
            "AI conversation SAVE exception:",
            error
        )

        traceback.print_exc()

        return False


# =========================================================
# OPENROUTER SINGLE MODEL REQUEST
# =========================================================

def call_openrouter_model(
    model,
    messages,
    title="NexaFlow AI"
):

    if not OPENROUTER_API_KEY:

        return None, {
            "type": "configuration",
            "message":
                "OPENROUTER_API_KEY is not configured.",
            "status_code": None,
            "model": model
        }

    url = (
        "https://openrouter.ai/api/v1/"
        "chat/completions"
    )

    headers = {
        "Authorization":
            "Bearer " + OPENROUTER_API_KEY,

        "Content-Type":
            "application/json",

        "HTTP-Referer":
            SUPABASE_PROJECT_URL,

        "X-Title":
            title
    }

    payload = {
        "model": model,
        "messages": messages
    }

    try:

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=90
        )

        print(
            "================================================"
        )

        print(
            "OpenRouter model:",
            model
        )

        print(
            "OpenRouter status:",
            response.status_code
        )

        print(
            "================================================"
        )

        try:
            result = response.json()

        except Exception:

            result = {
                "raw_response":
                    response.text
            }

        if response.status_code != 200:

            error_message = (
                result.get("error", {})
                if isinstance(result, dict)
                else result
            )

            print(
                "OpenRouter ERROR:",
                error_message
            )

            return None, {
                "type": "openrouter",
                "message":
                    str(error_message),
                "status_code":
                    response.status_code,
                "model":
                    model,
                "raw":
                    result
            }

        choices = result.get(
            "choices",
            []
        )

        if not choices:

            return None, {
                "type": "empty_response",
                "message":
                    "No AI response was returned.",
                "status_code":
                    response.status_code,
                "model":
                    model
            }

        answer = str(
            choices[0]
            .get("message", {})
            .get("content", "")
        ).strip()

        if not answer:

            return None, {
                "type": "empty_response",
                "message":
                    "AI returned an empty response.",
                "status_code":
                    response.status_code,
                "model":
                    model
            }

        return answer, None

    except requests.exceptions.Timeout:

        print(
            "OpenRouter TIMEOUT:",
            model
        )

        return None, {
            "type": "timeout",
            "message":
                "OpenRouter request timed out.",
            "status_code":
                None,
            "model":
                model
        }

    except requests.exceptions.RequestException as error:

        print(
            "OpenRouter REQUEST ERROR:",
            model,
            error
        )

        traceback.print_exc()

        return None, {
            "type": "request_exception",
            "message":
                str(error),
            "status_code":
                None,
            "model":
                model
        }

    except Exception as error:

        print(
            "OpenRouter EXCEPTION:",
            model,
            error
        )

        traceback.print_exc()

        return None, {
            "type": "exception",
            "message":
                str(error),
            "status_code":
                None,
            "model":
                model
        }


# =========================================================
# OPENROUTER AI WITH AUTOMATIC FREE FALLBACK
# =========================================================

def call_openrouter(
    messages,
    title="NexaFlow AI"
):

    models_to_try = [
        OPENROUTER_PRIMARY_MODEL,
        OPENROUTER_FREE_ROUTER_MODEL
    ]

    last_error = None

    retryable_status_codes = {
        402,
        404,
        408,
        409,
        429,
        500,
        502,
        503,
        504
    }

    for index, model in enumerate(
        models_to_try
    ):

        print(
            "AI MODEL ATTEMPT:",
            index + 1,
            "of",
            len(models_to_try),
            model
        )

        answer, error = call_openrouter_model(
            model,
            messages,
            title
        )

        if answer:

            print(
                "AI MODEL SUCCESS:",
                model
            )

            return answer, None

        last_error = error or {
            "type": "unknown",
            "message":
                "Unknown OpenRouter error.",
            "status_code":
                None,
            "model":
                model
        }

        status_code = last_error.get(
            "status_code"
        )

        print(
            "AI MODEL FAILED:",
            model,
            "status:",
            status_code
        )

        if (
            index == 0
            and status_code in retryable_status_codes
        ):

            print(
                "Trying OpenRouter free-model router..."
            )

            time.sleep(0.5)

            continue

        if index == 0:

            print(
                "Primary model failed."
            )

            print(
                "Trying fallback model anyway..."
            )

            time.sleep(0.5)

            continue

        break

    print(
        "================================================"
    )

    print(
        "ALL OPENROUTER AI MODELS FAILED"
    )

    print(
        "Last error:",
        last_error
    )

    print(
        "================================================"
    )

    return None, last_error




         



    


                
            


# =========================================================
# CUSTOMERS - UPDATE
# =========================================================

@app.route(
    "/api/customers/<customer_id>",
    methods=["PATCH"]
)
def update_customer(customer_id):

    user = get_authenticated_user()

    if not user:

        return jsonify({
            "error":
                "Invalid or expired login session."
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    allowed_fields = {
        "name",
        "phone",
        "email",
        "location",
        "message",
        "ai_reply",
        "status",
        "notes"
    }

    update_data = {}

    for field in allowed_fields:

        if field in data:

            value = data.get(field)

            if value is None:
                value = ""

            update_data[field] = str(
                value
            ).strip()

    if not update_data:

        return jsonify({
            "error":
                "No customer information was provided."
        }), 400

    try:

        response = supabase_update(
            CUSTOMERS_URL,
            {
                "id":
                    "eq." + str(customer_id),

                "user_id":
                    "eq." + user["id"]
            },
            update_data
        )

        if response.status_code not in (
            200,
            204
        ):

            return jsonify({
                "success": False,
                "error":
                    "Unable to update customer: "
                    + response.text
            }), response.status_code

        return jsonify({
            "success":
                True,

            "customer":
                first_row(response),

            "message":
                "Customer updated successfully."
        })

    except Exception as error:

        print(
            "Customer PATCH exception:",
            error
        )

        traceback.print_exc()

        return jsonify({
            "success": False,
            "error":
                "Unable to update customer: "
                + str(error)
        }), 500


# =========================================================
# CUSTOMERS - DELETE
# =========================================================

@app.route(
    "/api/customers/<customer_id>",
    methods=["DELETE"]
)
def delete_customer(customer_id):

    user = get_authenticated_user()

    if not user:

        return jsonify({
            "error":
                "Invalid or expired login session."
        }), 401

    try:

        response = supabase_delete(
            CUSTOMERS_URL,
            {
                "id":
                    "eq." + str(customer_id),

                "user_id":
                    "eq." + user["id"]
            }
        )

        if response.status_code not in (
            200,
            204
        ):

            return jsonify({
                "success": False,
                "error":
                    "Unable to delete customer: "
                    + response.text
            }), response.status_code

        return jsonify({
            "success":
                True,

            "message":
                "Customer deleted successfully."
        })

    except Exception as error:

        print(
            "Customer DELETE exception:",
            error
        )

        traceback.print_exc()

        return jsonify({
            "success": False,
            "error":
                "Unable to delete customer: "
                + str(error)
        }), 500


# =========================================================
# CUSTOMER COUNT
# =========================================================

@app.route(
    "/api/customers/count",
    methods=["GET"]
)
def customer_count():

    user = get_authenticated_user()

    if not user:

        return jsonify({
            "error":
                "Invalid or expired login session."
        }), 401

    try:

        response = supabase_get(
            CUSTOMERS_URL,
            {
                "select":
                    "id",

                "user_id":
                    "eq." + user["id"]
            }
        )

        if response.status_code != 200:

            return jsonify({
                "error":
                    "Unable to load customer count: "
                    + response.text
            }), response.status_code

        customers = response.json()

        return jsonify({
            "success":
                True,

            "count":
                len(customers)
        })

    except Exception as error:

        print(
            "Customer COUNT exception:",
            error
        )

        traceback.print_exc()

        return jsonify({
            "success": False,
            "error":
                "Unable to load customer count: "
                + str(error)
        }), 500


# =========================================================
# BUSINESS ACCOUNT - GET
# =========================================================

@app.route(
    "/api/business-account",
    methods=["GET"]
)
def get_business_account():

    user = get_authenticated_user()

    if not user:

        return jsonify({
            "error":
                "Invalid or expired login session."
        }), 401

    try:

        response = supabase_get(
            BUSINESS_ACCOUNTS_URL,
            {
                "select":
                    "*",

                "user_id":
                    "eq." + user["id"],

                "limit":
                    "1"
            }
        )

        if response.status_code != 200:

            return jsonify({
                "success": False,
                "error":
                    "Unable to load business account: "
                    + response.text
            }), response.status_code

        account = first_row(response)

        return jsonify({
            "success":
                True,

            "business_account":
                account
        })

    except Exception as error:

        print(
            "Business account GET exception:",
            error
        )

        traceback.print_exc()

        return jsonify({
            "success": False,
            "error":
                "Unable to load business account: "
                + str(error)
        }), 500


# =========================================================
# BUSINESS ACCOUNT - SAVE
# =========================================================

@app.route(
    "/api/business-account",
    methods=["POST"]
)
def save_business_account():

    user = get_authenticated_user()

    if not user:

        return jsonify({
            "error":
                "Invalid or expired login session."
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    allowed_fields = {
        "business_name",
        "owner_name",
        "email",
        "phone",
        "address",
        "city",
        "country",
        "industry",
        "description",
        "website",
        "logo_url",
        "slogan"
    }

    business_data = {
        "user_id":
            user["id"]
    }

    for field in allowed_fields:

        if field in data:

            value = data.get(field)

            if value is None:
                value = ""

            business_data[field] = str(
                value
            ).strip()

    business_data["updated_at"] = now_iso()

    try:

        existing_response = supabase_get(
            BUSINESS_ACCOUNTS_URL,
            {
                "select":
                    "id",

                "user_id":
                    "eq." + user["id"],

                "limit":
                    "1"
            }
        )

        existing = first_row(
            existing_response
        )

        if existing and existing.get("id"):

            response = supabase_update(
                BUSINESS_ACCOUNTS_URL,
                {
                    "id":
                        "eq." + str(
                            existing["id"]
                        ),

                    "user_id":
                        "eq." + user["id"]
                },
                business_data
            )

        else:

            business_data["created_at"] = now_iso()

            response = supabase_insert(
                BUSINESS_ACCOUNTS_URL,
                business_data
            )

        if response.status_code not in (
            200,
            201,
            204
        ):

            return jsonify({
                "success": False,
                "error":
                    "Unable to save business account: "
                    + response.text
            }), response.status_code

        return jsonify({
            "success":
                True,

            "business_account":
                first_row(response),

            "message":
                "Business account saved successfully."
        })

    except Exception as error:

        print(
            "Business account SAVE exception:",
            error
        )

        traceback.print_exc()

        return jsonify({
            "success": False,
            "error":
                "Unable to save business account: "
                + str(error)
        }), 500
                        


# =========================================================
# OPENROUTER AI WITH AUTOMATIC FREE FALLBACK
# =========================================================

def call_openrouter(
    messages,
    title="NexaFlow AI"
):

    models_to_try = [
        OPENROUTER_PRIMARY_MODEL,
        OPENROUTER_FREE_ROUTER_MODEL
    ]

    last_error = None

    retryable_status_codes = {
        402,
        404,
        408,
        409,
        429,
        500,
        502,
        503,
        504
    }

    for index, model in enumerate(
        models_to_try
    ):

        print(
            "AI MODEL ATTEMPT:",
            index + 1,
            "of",
            len(models_to_try),
            model
        )

        answer, error = call_openrouter_model(
            model,
            messages,
            title
        )

        if answer:

            print(
                "AI MODEL SUCCESS:",
                model
            )

            return answer, None

        last_error = error or {
            "type": "unknown",
            "message":
                "Unknown OpenRouter error.",
            "status_code":
                None,
            "model":
                model
        }

        status_code = last_error.get(
            "status_code"
        )

        print(
            "AI MODEL FAILED:",
            model,
            "status:",
            status_code
        )

        if (
            index == 0
            and status_code in retryable_status_codes
        ):

            print(
                "Trying OpenRouter free-model router..."
            )

            time.sleep(0.5)

            continue

        if index == 0:

            print(
                "Primary model failed."
            )

            print(
                "Trying fallback model anyway..."
            )

            time.sleep(0.5)

            continue

        break

    print(
        "================================================"
    )

    print(
        "ALL OPENROUTER AI MODELS FAILED"
    )

    print(
        "Last error:",
        last_error
    )

    print(
        "================================================"
    )

    return None, last_error

# =========================================================
# AI ASSISTANT
# =========================================================

@app.route(
    "/api/ai",
    methods=["POST"]
)
def ai_reply():

    data = request.get_json(
        silent=True
    ) or {}

    question = str(
        data.get(
            "question",
            ""
        )
    ).strip()

    conversation = data.get(
        "conversation",
        []
    )

    if not question:

        return jsonify({
            "answer":
                "Please enter your question."
        }), 400

    user = get_authenticated_user()

    user_id = (
        user.get("id")
        if user
        else None
    )

    messages = [{
        "role":
            "system",
        "content":
            NEXAFLOW_SYSTEM_PROMPT
    }]

    if isinstance(
        conversation,
        list
    ):

        for item in conversation:

            if not isinstance(
                item,
                dict
            ):
                continue

            role = item.get(
                "role"
            )

            content = item.get(
                "content"
            )

            if role not in (
                "user",
                "assistant"
            ):

                continue

            if content is None:

                continue

            content = str(
                content
            ).strip()

            if not content:

                continue

            messages.append({
                "role":
                    role,
                "content":
                    content
            })

    messages.append({
        "role":
            "user",
        "content":
            question
    })

    if len(messages) > 21:

        messages = (
            [messages[0]]
            + messages[-20:]
        )

    answer, error = call_openrouter(
        messages,
        "NexaFlow AI"
    )

    if not answer:

        print(
            "FINAL AI ASSISTANT ERROR:",
            error
        )

        return jsonify({
            "success":
                False,
            "answer":
                "NexaFlow AI is temporarily unable to respond. "
                "Please try again in a moment.",
            "error":
                "AI service temporarily unavailable."
        }), 503

    saved = save_ai_conversation(
        user_id,
        question,
        answer
    )

    return jsonify({
        "success":
            True,
        "answer":
            answer,
        "conversation_saved":
            saved
    })

# =========================================================
# CUSTOMERS - GET
# =========================================================

@app.route(
    "/api/customers",
    methods=["GET"]
)
def get_customers():

    user = get_authenticated_user()

    if not user:

        return jsonify({
            "error":
                "Invalid or expired login session."
        }), 401

    try:

        response = supabase_get(
            CUSTOMERS_URL,
            {
                "select":
                    "*",

                "user_id":
                    "eq." + user["id"],

                "order":
                    "created_at.desc"
            }
        )

        if response.status_code != 200:

            return jsonify({
                "error":
                    "Unable to load customers: "
                    + response.text
            }), response.status_code

        customers = response.json()

        return jsonify({
            "success":
                True,

            "customers":
                customers,

            "count":
                len(customers)
        })

    except Exception as error:

        print(
            "Customers GET exception:",
            error
        )

        traceback.print_exc()

        return jsonify({
            "error":
                "Unable to load customers: "
                + str(error)
        }), 500


# =========================================================
# CUSTOMERS - ADD
# =========================================================

@app.route(
    "/api/customers",
    methods=["POST"]
)
def add_customer():

    user = get_authenticated_user()

    if not user:

        return jsonify({
            "error":
                "Invalid or expired login session."
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    name = str(
        data.get(
            "name",
            data.get(
                "customer_name",
                ""
            )
        )
    ).strip()

    if not name:

        return jsonify({
            "error":
                "Customer name is required."
        }), 400

    customer_data = {
        "user_id":
            user["id"],

        "name":
            name,

        "phone":
            str(
                data.get(
                    "phone",
                    data.get(
                        "phone_number",
                        ""
                    )
                )
            ).strip(),

        "email":
            str(
                data.get(
                    "email",
                    ""
                )
            ).strip(),

        "location":
            str(
                data.get(
                    "location",
                    ""
                )
            ).strip(),

        "message":
            str(
                data.get(
                    "message",
                    data.get(
                        "customer_message",
                        ""
                    )
                )
            ).strip(),

        "ai_reply":
            str(
                data.get(
                    "ai_reply",
                    ""
                )
            ).strip(),

        "created_at":
            now_iso()
    }

    try:

        response = supabase_insert(
            CUSTOMERS_URL,
            customer_data
        )

        if response.status_code not in (
            200,
            201
        ):

            return jsonify({
                "success":
                    False,

                "error":
                    "Unable to save customer: "
                    + response.text
            }), response.status_code

        saved = (
            first_row(response)
            or customer_data
        )

        return jsonify({
            "success":
                True,

            "customer":
                saved,

            "message":
                "Customer saved successfully."
        })

    except Exception as error:

        print(
            "Customer SAVE exception:",
            error
        )

        traceback.print_exc()

        return jsonify({
            "success":
                False,

            "error":
                str(error)
        }), 500


# =========================================================
# UPDATE CUSTOMER FROM WHATSAPP
# =========================================================

def update_customer_whatsapp_message(
    user_id,
    customer_id,
    message_text
):

    if (
        not user_id
        or not customer_id
        or not message_text
    ):
        return False

    try:

        params = {
            "id":
                "eq." + str(
                    customer_id
                ),
            "user_id":
                "eq." + str(
                    user_id
                ),
            "select":
                "*"
        }

        response = supabase_get(
            CUSTOMERS_URL,
            params
        )

        if response.status_code != 200:

            print(
                "Customer lookup failed:",
                response.text
            )

            return False

        rows = response.json()

        if not rows:

            print(
                "Customer not found:",
                customer_id
            )

            return False

        current = rows[0]

        existing_message = str(
            current.get(
                "message",
                ""
            )
        ).strip()

        if existing_message:

            combined_message = (
                existing_message
                + "\n"
                + message_text
            )

        else:

            combined_message = message_text

        update_data = {
            "message":
                combined_message,
            "updated_at":
                now_iso()
        }

        update_response = supabase_patch(
            CUSTOMERS_URL,
            params,
            update_data
        )

        if update_response.status_code not in (
            200,
            204
        ):

            print(
                "Customer WhatsApp update failed:",
                update_response.text
            )

            return False

        return True

    except Exception as error:

        print(
            "Customer WhatsApp update exception:",
            error
        )

        traceback.print_exc()

        return False
def update_customer_ai_reply(
    user_id,
    customer_id,
    ai_reply
):

    if (
        not user_id
        or not customer_id
        or not ai_reply
    ):
        return False

    try:

        params = {
            "id":
                "eq." + str(
                    customer_id
                ),

            "user_id":
                "eq." + str(
                    user_id
                )
        }

        data = {
            "ai_reply":
                ai_reply,

            "updated_at":
                now_iso()
        }

        response = supabase_update(
            CUSTOMERS_URL,
            params,
            data
        )

        print(
            "CUSTOMER AI REPLY UPDATE:",
            response.status_code,
            response.text
        )

        return response.status_code in (
            200,
            204
        )

    except Exception as error:

        print(
            "Customer AI reply update exception:",
            error
        )

        traceback.print_exc()

        return False


# =========================================================
# CUSTOMERS - DELETE
# =========================================================

@app.route(
    "/api/customers/<int:customer_id>",
    methods=["DELETE"]
)
def delete_customer(customer_id):

    user = get_authenticated_user()

    if not user:

        return jsonify({
            "error":
                "Invalid or expired login session."
        }), 401

    try:

        response = supabase_delete(
            CUSTOMERS_URL,
            {
                "id":
                    "eq." + str(
                        customer_id
                    ),

                "user_id":
                    "eq." + user["id"]
            }
        )

        if response.status_code not in (
            200,
            204
        ):

            return jsonify({
                "error":
                    response.text
            }), response.status_code

        return jsonify({
            "success":
                True,

            "message":
                "Customer deleted successfully."
        })

    except Exception as error:

        print(
            "Customer DELETE exception:",
            error
        )

        traceback.print_exc()

        return jsonify({
            "error":
                str(error)
        }), 500


# =========================================================
# DASHBOARD
# =========================================================

@app.route(
    "/api/dashboard/stats",
    methods=["GET"]
)
def dashboard_stats():

    user = get_authenticated_user()

    if not user:

        return jsonify({
            "error":
                "Invalid or expired login session."
        }), 401

    user_id = user["id"]

    try:

        customers_response = supabase_get(
            CUSTOMERS_URL,
            {
                "select":
                    "id",

                "user_id":
                    "eq." + user_id
            }
        )

        conversations_response = supabase_get(
            AI_CONVERSATIONS_URL,
            {
                "select":
                    "id",

                "user_id":
                    "eq." + user_id
            }
        )

        business_response = supabase_get(
            BUSINESS_ACCOUNTS_URL,
            {
                "select":
                    "id",

                "user_id":
                    "eq." + user_id,

                "limit":
                    "1"
            }
        )

        messages_response = supabase_get(
            MESSAGES_URL,
            {
                "select":
                    "id,direction,status",

                "user_id":
                    "eq." + user_id,

                "platform":
                    "eq.whatsapp"
            }
        )

        customers = (
            customers_response.json()
            if customers_response.status_code == 200
            else []
        )

        conversations = (
            conversations_response.json()
            if conversations_response.status_code == 200
            else []
        )

        businesses = (
            business_response.json()
            if business_response.status_code == 200
            else []
        )

        whatsapp_messages = (
            messages_response.json()
            if messages_response.status_code == 200
            else []
        )

        incoming = len([
            x
            for x in whatsapp_messages
            if x.get("direction")
            == "inbound"
        ])

        outgoing = len([
            x
            for x in whatsapp_messages
            if x.get("direction")
            == "outbound"
        ])

        return jsonify({

            "success":
                True,

            "stats": {

                "customers":
                    len(customers),

                "ai_conversations":
                    len(conversations),

                "whatsapp_messages":
                    len(whatsapp_messages),

                "whatsapp_incoming":
                    incoming,

                "whatsapp_outgoing":
                    outgoing,

                "reports":
                    len(customers)
                    + len(conversations),

                "business_account":
                    1 if businesses
                    else 0
            }
        })

    except Exception as error:

        print(
            "Dashboard stats exception:",
            error
        )

        traceback.print_exc()

        return jsonify({
            "error":
                str(error)
        }), 500


# =========================================================
# AI CONVERSATIONS
# =========================================================

@app.route(
    "/api/ai/conversations",
    methods=["GET"]
)
def get_ai_conversations():

    user = get_authenticated_user()

    if not user:

        return jsonify({
            "error":
                "Invalid or expired login session."
        }), 401

    try:

        response = supabase_get(
            AI_CONVERSATIONS_URL,
            {
                "select":
                    "*",

                "user_id":
                    "eq." + user["id"],

                "order":
                    "created_at.desc"
            }
        )

        if response.status_code != 200:

            return jsonify({
                "error":
                    response.text
            }), response.status_code

        conversations = response.json()

        return jsonify({

            "success":
                True,

            "conversations":
                conversations,

            "count":
                len(conversations)
        })

    except Exception as error:

        print(
            "AI conversations GET exception:",
            error
        )

        traceback.print_exc()

        return jsonify({
            "error":
                str(error)
        }), 500


# =========================================================
# AUTOMATION - GET
# =========================================================

@app.route(
    "/api/automation",
    methods=["GET"]
)
def get_automation_settings():

    user = get_authenticated_user()

    if not user:

        return jsonify({
            "error":
                "Invalid or expired login session."
        }), 401

    try:

        response = supabase_get(
            AUTOMATION_SETTINGS_URL,
            {
                "select":
                    "*",

                "user_id":
                    "eq." + user["id"],

                "limit":
                    "1"
            }
        )

        if response.status_code != 200:

            return jsonify({
                "error":
                    response.text
            }), response.status_code

        rows = response.json()

        if rows:

            return jsonify({
                "automation":
                    rows[0]
            })

        return jsonify({

            "automation": {

                "user_id":
                    user["id"],

                "ai_replies":
                    True,

                "message_automation":
                    True,

                "task_automation":
                    True
            }
        })

    except Exception as error:

        print(
            "Automation GET exception:",
            error
        )

        traceback.print_exc()

        return jsonify({
            "error":
                str(error)
        }), 500


# =========================================================
# AUTOMATION - SAVE
# =========================================================

@app.route(
    "/api/automation",
    methods=["POST"]
)
def save_automation_settings():

    user = get_authenticated_user()

    if not user:

        return jsonify({
            "error":
                "Invalid or expired login session."
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    settings = {

        "user_id":
            user["id"],

        "ai_replies":
            bool(
                data.get(
                    "ai_replies",
                    True
                )
            ),

        "message_automation":
            bool(
                data.get(
                    "message_automation",
                    True
                )
            ),

        "task_automation":
            bool(
                data.get(
                    "task_automation",
                    True
                )
            ),

        "updated_at":
            now_iso()
    }

    try:

        existing_response = supabase_get(
            AUTOMATION_SETTINGS_URL,
            {
                "select":
                    "id",

                "user_id":
                    "eq." + user["id"],

                "limit":
                    "1"
            }
        )

        existing = (
            existing_response.json()
            if existing_response.status_code == 200
            else []
        )

        if existing:

            response = supabase_update(
                AUTOMATION_SETTINGS_URL,
                {
                    "user_id":
                        "eq." + user["id"]
                },
                settings
            )

        else:

            response = supabase_insert(
                AUTOMATION_SETTINGS_URL,
                settings
            )

        if response.status_code not in (
            200,
            201,
            204
        ):

            return jsonify({
                "error":
                    response.text
            }), response.status_code

        return jsonify({

            "success":
                True,

            "automation":
                first_row(response)
                or settings,

            "message":
                "Automation settings saved successfully."
        })

    except Exception as error:

        print(
            "Automation SAVE exception:",
            error
        )

        traceback.print_exc()

        return jsonify({
            "error":
                str(error)
        }), 500


# =========================================================
# AUTOMATION TOGGLE
# =========================================================

@app.route(
    "/api/automation/toggle",
    methods=["POST"]
)
def toggle_automation():

    user = get_authenticated_user()

    if not user:

        return jsonify({
            "error":
                "Invalid or expired login session."
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    setting = str(
        data.get(
            "setting",
            ""
        )
    ).strip()

    value = data.get(
        "value"
    )

    allowed = {
        "ai_replies",
        "message_automation",
        "task_automation"
    }

    if setting not in allowed:

        return jsonify({
            "error":
                "Invalid automation setting."
        }), 400

    if not isinstance(
        value,
        bool
    ):

        return jsonify({
            "error":
                "Automation value must be true or false."
        }), 400

    try:

        check = supabase_get(
            AUTOMATION_SETTINGS_URL,
            {
                "select":
                    "id",

                "user_id":
                    "eq." + user["id"],

                "limit":
                    "1"
            }
        )

        existing = (
            check.json()
            if check.status_code == 200
            else []
        )

        if existing:

            response = supabase_update(
                AUTOMATION_SETTINGS_URL,
                {
                    "user_id":
                        "eq." + user["id"]
                },
                {
                    setting:
                        value,

                    "updated_at":
                        now_iso()
                }
            )

        else:

            settings = {

                "user_id":
                    user["id"],

                "ai_replies":
                    True,

                "message_automation":
                    True,

                "task_automation":
                    True,

                "updated_at":
                    now_iso()
            }

            settings[setting] = value

            response = supabase_insert(
                AUTOMATION_SETTINGS_URL,
                settings
            )

        if response.status_code not in (
            200,
            201,
            204
        ):

            return jsonify({
                "error":
                    response.text
            }), response.status_code

        return jsonify({

            "success":
                True,

            "setting":
                setting,

            "value":
                value,

            "automation":
                first_row(response)
        })

    except Exception as error:

        print(
            "Automation toggle exception:",
            error
        )

        traceback.print_exc()

        return jsonify({
            "error":
                str(error)
        }), 500


# =========================================================
# BUSINESS
# =========================================================

@app.route(
    "/api/business",
    methods=["GET", "POST"]
)
def business_account():

    user = get_authenticated_user()

    if not user:

        return jsonify({
            "error":
                "Invalid or expired login session."
        }), 401

    user_id = user["id"]

    if request.method == "GET":

        try:

            response = supabase_get(
                BUSINESS_ACCOUNTS_URL,
                {
                    "select":
                        "*",

                    "user_id":
                        "eq." + user_id,

                    "limit":
                        "1"
                }
            )

            if response.status_code != 200:

                return jsonify({
                    "error":
                        response.text
                }), response.status_code

            rows = response.json()

            return jsonify({

                "business":
                    rows[0]
                    if rows
                    else None
            })

        except Exception as error:

            print(
                "Business GET exception:",
                error
            )

            traceback.print_exc()

            return jsonify({
                "error":
                    str(error)
            }), 500

    data = request.get_json(
        silent=True
    ) or {}

    business_data = {

        "user_id":
            user_id,

        "business_name":
            str(
                data.get(
                    "business_name",
                    ""
                )
            ).strip(),

        "owner_name":
            str(
                data.get(
                    "owner_name",
                    ""
                )
            ).strip(),

        "phone":
            str(
                data.get(
                    "phone",
                    ""
                )
            ).strip(),

        "email":
            str(
                data.get(
                    "email",
                    ""
                )
            ).strip(),

        "address":
            str(
                data.get(
                    "address",
                    ""
                )
            ).strip(),

        "description":
            str(
                data.get(
                    "description",
                    ""
                )
            ).strip(),

        "logo":
            str(
                data.get(
                    "logo",
                    ""
                )
            ).strip(),

        "updated_at":
            now_iso()
    }

    try:

        check = supabase_get(
            BUSINESS_ACCOUNTS_URL,
            {
                "select":
                    "id",

                "user_id":
                    "eq." + user_id,

                "limit":
                    "1"
            }
        )

        existing = (
            check.json()
            if check.status_code == 200
            else []
        )

        if existing:

            response = supabase_update(
                BUSINESS_ACCOUNTS_URL,
                {
                    "id":
                        "eq." + str(
                            existing[0]["id"]
                        ),

                    "user_id":
                        "eq." + user_id
                },
                business_data
            )

        else:

            response = supabase_insert(
                BUSINESS_ACCOUNTS_URL,
                business_data
            )

        if response.status_code not in (
            200,
            201
        ):

            return jsonify({
                "error":
                    response.text
            }), response.status_code

        return jsonify({

            "success":
                True,

            "business":
                first_row(response)
                or business_data,

            "message":
                "Business settings saved successfully."
        })

    except Exception as error:

        print(
            "Business SAVE exception:",
            error
        )

        traceback.print_exc()

        return jsonify({
            "error":
                str(error)
        }), 500
# =========================================================
# BUSINESS LOGO
# =========================================================

@app.route(
    "/api/business/logo",
    methods=["POST"]
)
def upload_business_logo():

    user = get_authenticated_user()

    if not user:

        return jsonify({
            "error":
                "Invalid or expired login session."
        }), 401

    if "logo" not in request.files:

        return jsonify({
            "error":
                "No logo file was provided."
        }), 400

    logo_file = request.files["logo"]

    if not logo_file.filename:

        return jsonify({
            "error":
                "No logo file was selected."
        }), 400

    allowed = (
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp"
    )

    if not logo_file.filename.lower().endswith(
        allowed
    ):

        return jsonify({
            "error":
                "Unsupported logo format."
        }), 400

    try:

        file_bytes = logo_file.read()

        if not file_bytes:

            return jsonify({
                "error":
                    "The selected logo file is empty."
            }), 400

        bucket = "business-logos"

        extension = (
            logo_file.filename
            .rsplit(".", 1)[-1]
            .lower()
        )

        file_path = (
            str(user["id"])
            + "/logo."
            + extension
        )

        storage_url = (
            SUPABASE_PROJECT_URL
            + "/storage/v1/object/"
            + bucket
            + "/"
            + file_path
        )

        response = requests.post(
            storage_url,
            headers={
                "apikey":
                    SUPABASE_SECRET_KEY,

                "Authorization":
                    "Bearer "
                    + SUPABASE_SECRET_KEY,

                "Content-Type":
                    logo_file.mimetype
                    or "application/octet-stream",

                "x-upsert":
                    "true"
            },
            data=file_bytes,
            timeout=30
        )

        print(
            "Logo upload status:",
            response.status_code
        )

        print(
            "Logo upload response:",
            response.text
        )

        if response.status_code not in (
            200,
            201
        ):

            return jsonify({
                "error":
                    "Unable to upload logo: "
                    + response.text
            }), response.status_code

        logo_url = (
            SUPABASE_PROJECT_URL
            + "/storage/v1/object/public/"
            + bucket
            + "/"
            + file_path
        )

        update_response = supabase_update(
            BUSINESS_ACCOUNTS_URL,
            {
                "user_id":
                    "eq." + user["id"]
            },
            {
                "logo":
                    logo_url,

                "updated_at":
                    now_iso()
            }
        )

        print(
            "Business logo database update:",
            update_response.status_code
        )

        if update_response.status_code not in (
            200,
            204
        ):

            return jsonify({
                "error":
                    "Logo uploaded but could not be saved "
                    "to the business profile: "
                    + update_response.text
            }), update_response.status_code

        return jsonify({

            "success":
                True,

            "logo":
                logo_url,

            "message":
                "Business logo uploaded successfully."
        })

    except Exception as error:

        print(
            "Business logo upload exception:",
            error
        )

        traceback.print_exc()

        return jsonify({
            "error":
                str(error)
        }), 500


# =========================================================
# WHATSAPP INTEGRATIONS - GET
# =========================================================

@app.route(
    "/api/integrations",
    methods=["GET"]
)
def get_integrations():

    user = get_authenticated_user()

    if not user:

        return jsonify({
            "error":
                "Invalid or expired login session."
        }), 401

    try:

        response = supabase_get(
            INTEGRATIONS_URL,
            {
                "select":
                    "*",

                "user_id":
                    "eq." + user["id"],

                "order":
                    "created_at.desc"
            }
        )

        if response.status_code != 200:

            return jsonify({
                "error":
                    response.text
            }), response.status_code

        rows = response.json()

        return jsonify({

            "success":
                True,

            "integrations":
                rows,

            "count":
                len(rows)
        })

    except Exception as error:

        print(
            "Integrations GET exception:",
            error
        )

        traceback.print_exc()

        return jsonify({
            "error":
                str(error)
        }), 500


# =========================================================
# WHATSAPP INTEGRATIONS - SAVE
# =========================================================

@app.route(
    "/api/integrations",
    methods=["POST"]
)
def save_integration():

    user = get_authenticated_user()

    if not user:

        return jsonify({
            "error":
                "Invalid or expired login session."
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    platform = str(
        data.get(
            "platform",
            "whatsapp"
        )
    ).strip().lower()

    if platform != "whatsapp":

        return jsonify({
            "error":
                "This endpoint currently supports WhatsApp only."
        }), 400

    account_name = str(
        data.get(
            "account_name",
            ""
        )
    ).strip()

    account_id = str(
        data.get(
            "account_id",
            WHATSAPP_BUSINESS_ACCOUNT_ID
            or ""
        )
    ).strip()

    access_token = str(
        data.get(
            "access_token",
            WHATSAPP_ACCESS_TOKEN
            or ""
        )
    ).strip()

    phone_number = str(
        data.get(
            "phone_number",
            ""
        )
    ).strip()

    phone_number_id = str(
        data.get(
            "phone_number_id",
            WHATSAPP_PHONE_NUMBER_ID
            or ""
        )
    ).strip()

    if not phone_number_id:

        return jsonify({
            "error":
                "WhatsApp phone number ID is required."
        }), 400

    integration = {

        "user_id":
            user["id"],

        "platform":
            "whatsapp",

        "account_name":
            account_name,

        "account_id":
            account_id,

        "access_token":
            access_token,

        "phone_number":
            phone_number,

        "status":
            "connected",

        "settings": {
            "phone_number_id":
                phone_number_id
        },

        "connected_at":
            now_iso(),

        "updated_at":
            now_iso()
    }

    try:

        check = supabase_get(
            INTEGRATIONS_URL,
            {
                "select":
                    "id",

                "user_id":
                    "eq." + user["id"],

                "platform":
                    "eq.whatsapp",

                "account_id":
                    "eq." + account_id,

                "limit":
                    "1"
            }
        )

        existing = (
            check.json()
            if check.status_code == 200
            else []
        )

        if existing:

            response = supabase_update(
                INTEGRATIONS_URL,
                {
                    "id":
                        "eq." + str(
                            existing[0]["id"]
                        ),

                    "user_id":
                        "eq." + user["id"]
                },
                integration
            )

        else:

            response = supabase_insert(
                INTEGRATIONS_URL,
                integration
            )

        if response.status_code not in (
            200,
            201
        ):

            return jsonify({
                "error":
                    response.text
            }), response.status_code

        return jsonify({

            "success":
                True,

            "integration":
                first_row(response)
                or integration,

            "message":
                "WhatsApp integration saved successfully."
        })

    except Exception as error:

        print(
            "Integration SAVE exception:",
            error
        )

        traceback.print_exc()

        return jsonify({
            "error":
                str(error)
        }), 500


# =========================================================
# WHATSAPP INTEGRATION DELETE
# =========================================================

@app.route(
    "/api/integrations/<int:integration_id>",
    methods=["DELETE"]
)
def delete_integration(integration_id):

    user = get_authenticated_user()

    if not user:

        return jsonify({
            "error":
                "Invalid or expired login session."
        }), 401

    try:

        response = supabase_delete(
            INTEGRATIONS_URL,
            {
                "id":
                    "eq." + str(
                        integration_id
                    ),

                "user_id":
                    "eq." + user["id"]
            }
        )

        if response.status_code not in (
            200,
            204
        ):

            return jsonify({
                "error":
                    response.text
            }), response.status_code

        return jsonify({

            "success":
                True,

            "message":
                "Integration deleted successfully."
        })

    except Exception as error:

        print(
            "Integration DELETE exception:",
            error
        )

        traceback.print_exc()

        return jsonify({
            "error":
                str(error)
        }), 500


# =========================================================
# WHATSAPP FIND INTEGRATION
# =========================================================

def find_whatsapp_integration(
    phone_number_id
):

    print(
        "========== WHATSAPP INTEGRATION LOOKUP =========="
    )

    print(
        "Incoming phone_number_id:",
        phone_number_id
    )

    if not phone_number_id:

        return None

    try:

        response = supabase_get(
            INTEGRATIONS_URL,
            {
                "select":
                    "*",

                "platform":
                    "eq.whatsapp"
            }
        )

        print(
            "Integration lookup status:",
            response.status_code
        )

        print(
            "Integration lookup response:",
            response.text
        )

        if response.status_code != 200:

            return None

        integrations = response.json()

        for integration in integrations:

            settings = (
                integration.get(
                    "settings"
                )
                or {}
            )

            saved_phone_number_id = str(
                settings.get(
                    "phone_number_id",
                    ""
                )
            ).strip()

            if (
                saved_phone_number_id
                == str(phone_number_id).strip()
            ):

                print(
                    "Matching WhatsApp integration found."
                )

                return integration

        if (
            WHATSAPP_PHONE_NUMBER_ID
            and str(
                WHATSAPP_PHONE_NUMBER_ID
            ).strip()
            == str(
                phone_number_id
            ).strip()
        ):

            print(
                "Using environment WhatsApp configuration."
            )

            return {
                "user_id":
                    None,

                "platform":
                    "whatsapp",

                "account_id":
                    WHATSAPP_BUSINESS_ACCOUNT_ID,

                "access_token":
                    WHATSAPP_ACCESS_TOKEN,

                "phone_number_id":
                    WHATSAPP_PHONE_NUMBER_ID,

                "settings": {
                    "phone_number_id":
                        WHATSAPP_PHONE_NUMBER_ID
                }
            }

        print(
            "No matching WhatsApp integration found."
        )

        return None

    except Exception as error:

        print(
            "WhatsApp integration lookup exception:",
            error
        )

        traceback.print_exc()

        return None


# =========================================================
# WHATSAPP CUSTOMER FIND OR CREATE
# =========================================================

def find_or_create_whatsapp_customer(
    user_id,
    phone,
    name=""
):

    if not user_id or not phone:

        return None

    phone = str(
        phone
    ).strip()

    name = str(
        name
    ).strip()

    try:

        response = supabase_get(
            CUSTOMERS_URL,
            {
                "select":
                    "*",

                "user_id":
                    "eq." + str(
                        user_id
                    ),

                "phone":
                    "eq." + phone,

                "limit":
                    "1"
            }
        )

        if response.status_code == 200:

            rows = response.json()

            if rows:

                customer = rows[0]

                if name and not customer.get(
                    "name"
                ):

                    update_response = supabase_update(
                        CUSTOMERS_URL,
                        {
                            "id":
                                "eq." + str(
                                    customer["id"]
                                ),

                            "user_id":
                                "eq." + str(
                                    user_id
                                )
                        },
                        {
                            "name":
                                name,

                            "updated_at":
                                now_iso()
                        }
                    )

                    if update_response.status_code in (
                        200,
                        204
                    ):

                        customer["name"] = name

                return customer

        customer_data = {

            "user_id":
                str(user_id),

            "name":
                name
                or phone,

            "phone":
                phone,

            "email":
                "",

            "location":
                "",

            "message":
                "",

            "ai_reply":
                "",

            "created_at":
                now_iso()
        }

        insert_response = supabase_insert(
            CUSTOMERS_URL,
            customer_data
        )

        if insert_response.status_code not in (
            200,
            201
        ):

            print(
                "WhatsApp customer creation failed:",
                insert_response.text
            )

            return None

        customer = (
            first_row(insert_response)
            or customer_data
        )

        print(
            "WhatsApp customer created:",
            customer
        )

        return customer

    except Exception as error:

        print(
            "WhatsApp customer find/create exception:",
            error
        )

        traceback.print_exc()

        return None


# =========================================================
# SAVE WHATSAPP MESSAGE
# =========================================================

def save_whatsapp_message(
    user_id,
    customer_id,
    phone,
    message_text,
    direction,
    status="received",
    message_id=None
):

    if not user_id:

        return None

    message_data = {

        "user_id":
            str(user_id),

        "customer_id":
            customer_id,

        "platform":
            "whatsapp",

        "phone":
            str(phone or ""),

        "message":
            str(message_text or ""),

        "direction":
            str(direction or ""),

        "status":
            str(status or ""),

        "external_message_id":
            str(message_id or ""),

        "created_at":
            now_iso()
    }

    try:

        response = supabase_insert(
            MESSAGES_URL,
            message_data
        )

        print(
            "WhatsApp message save status:",
            response.status_code
        )

        print(
            "WhatsApp message save response:",
            response.text
        )

        if response.status_code not in (
            200,
            201
        ):

            return None

        return (
            first_row(response)
            or message_data
        )

    except Exception as error:

        print(
            "WhatsApp message save exception:",
            error
        )

        traceback.print_exc()

        return None


# =========================================================
# WHATSAPP SEND MESSAGE
# =========================================================

def send_whatsapp_message(
    phone_number_id,
    access_token,
    recipient_phone,
    message_text
):

    if not (
        phone_number_id
        and access_token
        and recipient_phone
        and message_text
    ):

        return None

    url = (
        "https://graph.facebook.com/v20.0/"
        + str(phone_number_id)
        + "/messages"
    )

    payload = {

        "messaging_product":
            "whatsapp",

        "to":
            str(recipient_phone),

        "type":
            "text",

        "text": {
            "preview_url":
                False,

            "body":
                str(message_text)
        }
    }

    try:

        response = requests.post(
            url,
            headers={
                "Authorization":
                    "Bearer "
                    + str(access_token),

                "Content-Type":
                    "application/json"
            },
            json=payload,
            timeout=20
        )

        print(
            "WhatsApp send status:",
            response.status_code
        )

        print(
            "WhatsApp send response:",
            response.text
        )

        if response.status_code not in (
            200,
            201
        ):

            return None

        return response.json()

    except Exception as error:

        print(
            "WhatsApp send exception:",
            error
        )

        traceback.print_exc()

        return None


# =========================================================
# WHATSAPP AI RESPONSE
# =========================================================

def generate_whatsapp_ai_reply(
    customer_message,
    customer_name="",
    user_id=None
):

    business_context = ""

    if user_id:

        try:

            business_response = supabase_get(
                BUSINESS_ACCOUNTS_URL,
                {
                    "select":
                        "*",

                    "user_id":
                        "eq." + str(
                            user_id
                        ),

                    "limit":
                        "1"
                }
            )

            if business_response.status_code == 200:

                rows = business_response.json()

                if rows:

                    business = rows[0]

                    business_context = (
                        "\nBusiness information:\n"
                        "Business name: "
                        + str(
                            business.get(
                                "business_name",
                                ""
                            )
                        )
                        + "\nOwner: "
                        + str(
                            business.get(
                                "owner_name",
                                ""
                            )
                        )
                        + "\nPhone: "
                        + str(
                            business.get(
                                "phone",
                                ""
                            )
                        )
                        + "\nAddress: "
                        + str(
                            business.get(
                                "address",
                                ""
                            )
                        )
                        + "\nDescription: "
                        + str(
                            business.get(
                                "description",
                                ""
                            )
                        )
                    )

        except Exception as error:

            print(
                "Business context error:",
                error
            )

    system_prompt = """
You are the customer communication assistant for a business.

Reply professionally, politely and naturally.

Detect whether the customer is writing in English or French and answer in the same language.

You may:
- greet customers
- answer general questions
- explain services
- collect project information
- collect customer contact details
- explain training or course information
- ask useful follow-up questions
- acknowledge customer requests

Do NOT invent:
- prices
- quotations
- discounts
- contracts
- financial commitments
- technical specifications that require professional verification

For prices, quotations, contracts, major technical decisions, disputes or other sensitive business commitments, tell the customer that the request will be reviewed by the company/CEO.

Keep replies concise and suitable for WhatsApp.
""" + business_context

    if customer_name:

        system_prompt += (
            "\nCustomer name: "
            + customer_name
        )

    messages = [

        {
            "role":
                "system",

            "content":
                system_prompt
        },

        {
            "role":
                "user",

            "content":
                str(
                    customer_message
                )
        }
    ]

    answer, error = call_openrouter(
        messages,
        "TASSIMO WhatsApp AI"
    )

    if answer:

        return answer

    print(
        "WhatsApp AI reply failed:",
        error
    )

    return (
        "Thank you for contacting us. "
        "We have received your message and "
        "will get back to you shortly."
    )
# =========================================================
# SEND WHATSAPP MESSAGE THROUGH META
# =========================================================

def send_whatsapp_message(
    integration,
    recipient_phone,
    message_text
):

    if (
        not integration
        or not recipient_phone
        or not message_text
    ):
        return None

    settings = (
        integration.get(
            "settings"
        )
        or {}
    )

    phone_number_id = str(
        settings.get(
            "phone_number_id",
            WHATSAPP_PHONE_NUMBER_ID
            or ""
        )
    ).strip()

    access_token = str(
        integration.get(
            "access_token",
            WHATSAPP_ACCESS_TOKEN
            or ""
        )
    ).strip()

    if not phone_number_id:

        print(
            "WhatsApp send error: phone number ID missing."
        )

        return None

    if not access_token:

        print(
            "WhatsApp send error: access token missing."
        )

        return None

    url = (
        "https://graph.facebook.com/v23.0/"
        + phone_number_id
        + "/messages"
    )

    try:

        print(
            "Sending WhatsApp reply to:",
            recipient_phone
        )

        response = requests.post(

            url,

            headers={

                "Authorization":
                    "Bearer "
                    + access_token,

                "Content-Type":
                    "application/json"
            },

            json={

                "messaging_product":
                    "whatsapp",

                "to":
                    recipient_phone,

                "type":
                    "text",

                "text": {

                    "preview_url":
                        False,

                    "body":
                        message_text
                }
            },

            timeout=30
        )

        print(
            "WhatsApp SEND:",
            response.status_code,
            response.text
        )

        if response.status_code not in (
            200,
            201
        ):

            return None

        return response.json()

    except Exception as error:

        print(
            "WhatsApp SEND exception:",
            error
        )

        traceback.print_exc()

        return None


# =========================================================
# STORE OUTGOING WHATSAPP MESSAGE
# =========================================================

def store_whatsapp_outgoing_message(
    integration,
    customer,
    recipient_phone,
    message_text,
    whatsapp_response
):

    if not integration:
        return None

    user_id = integration.get(
        "user_id"
    )

    customer_id = (
        customer.get("id")
        if customer
        else None
    )

    response_messages = (
        whatsapp_response.get(
            "messages",
            []
        )
        if isinstance(
            whatsapp_response,
            dict
        )
        else []
    )

    external_message_id = ""

    if response_messages:

        external_message_id = str(
            response_messages[0].get(
                "id",
                ""
            )
        )

    data = {

        "user_id":
            user_id,

        "integration_id":
            integration.get("id"),

        "customer_id":
            customer_id,

        "platform":
            "whatsapp",

        "external_message_id":
            external_message_id,

        "direction":
            "outbound",

        "sender_name":
            "NexaFlow AI",

        "sender_phone":
            recipient_phone,

        "message":
            message_text,

        "ai_generated":
            True,

        "ai_reply":
            message_text,

        "status":
            "sent",

        "metadata": {
            "source":
                "nexaflow_ai"
        },

        "created_at":
            now_iso(),

        "updated_at":
            now_iso()
    }

    try:

        response = supabase_insert(
            MESSAGES_URL,
            data
        )

        print(
            "Outgoing WhatsApp SAVE:",
            response.status_code,
            response.text
        )

        if response.status_code not in (
            200,
            201
        ):

            return None

        return (
            first_row(
                response
            )
            or data
        )

    except Exception as error:

        print(
            "Outgoing WhatsApp SAVE exception:",
            error
        )

        traceback.print_exc()

        return None


# =========================================================
# UPDATE INCOMING MESSAGE
# =========================================================

def update_incoming_message_with_ai_reply(
    message_id,
    ai_reply
):

    if (
        not message_id
        or not ai_reply
    ):
        return False

    try:

        response = supabase_update(

            MESSAGES_URL,

            {
                "id":
                    "eq." + str(
                        message_id
                    )
            },

            {
                "ai_reply":
                    ai_reply,

                "status":
                    "replied",

                "updated_at":
                    now_iso()
            }
        )

        print(
            "Incoming message AI update:",
            response.status_code,
            response.text
        )

        return response.status_code in (
            200,
            204
        )

    except Exception as error:

        print(
            "Incoming message update exception:",
            error
        )

        traceback.print_exc()

        return False


# =========================================================
# PROCESS WHATSAPP AI REPLY
#
# IMPORTANT:
# This function runs in a BACKGROUND THREAD.
# The webhook no longer waits for it.
# =========================================================

def process_whatsapp_ai_reply(
    integration,
    stored_message
):

    try:

        if (
            not integration
            or not stored_message
        ):
            return False

        user_id = integration.get(
            "user_id"
        )

        if not user_id:
            return False

        print(
            "================================================"
        )

        print(
            "BACKGROUND WHATSAPP AI PROCESS START"
        )

        print(
            "User:",
            user_id
        )

        print(
            "Message ID:",
            stored_message.get("id")
        )

        print(
            "================================================"
        )

        if not whatsapp_automation_enabled(
            user_id
        ):

            print(
                "WhatsApp AI automation is disabled."
            )

            return False

        message_text = str(
            stored_message.get(
                "message",
                ""
            )
        ).strip()

        recipient_phone = str(
            stored_message.get(
                "sender_phone",
                ""
            )
        ).strip()

        if (
            not message_text
            or not recipient_phone
        ):

            print(
                "Missing message text or recipient phone."
            )

            return False

        customer_id = stored_message.get(
            "customer_id"
        )

        customer = None

        if customer_id:

            try:

                response = supabase_get(

                    CUSTOMERS_URL,

                    {
                        "select":
                            "*",

                        "id":
                            "eq." + str(
                                customer_id
                            ),

                        "user_id":
                            "eq." + user_id,

                        "limit":
                            "1"
                    }
                )

                if response.status_code == 200:

                    rows = response.json()

                    if rows:
                        customer = rows[0]

            except Exception as error:

                print(
                    "Customer retrieval exception:",
                    error
                )

                traceback.print_exc()

        # -------------------------------------------------
        # GENERATE AI
        # -------------------------------------------------

        print(
            "STEP 1: GENERATING AI RESPONSE"
        )

        ai_reply = generate_whatsapp_ai_reply(

            user_id,

            customer,

            message_text,

            current_message_id=
                stored_message.get("id")
        )

        if not ai_reply:

            print(
                "STEP 1 FAILED: AI could not generate reply."
            )

            return False

        print(
            "STEP 1 SUCCESS: AI generated:"
        )

        print(
            ai_reply
        )

        # -------------------------------------------------
        # SEND THROUGH META
        # -------------------------------------------------

        print(
            "STEP 2: SENDING AI RESPONSE THROUGH META"
        )

        whatsapp_response = send_whatsapp_message(

            integration,

            recipient_phone,

            ai_reply
        )

        if not whatsapp_response:

            print(
                "STEP 2 FAILED: Meta failed to send reply."
            )

            return False

        print(
            "STEP 2 SUCCESS: WhatsApp reply sent."
        )

        # -------------------------------------------------
        # SAVE OUTGOING MESSAGE
        # -------------------------------------------------

        print(
            "STEP 3: SAVING OUTGOING MESSAGE"
        )

        outgoing = store_whatsapp_outgoing_message(

            integration,

            customer,

            recipient_phone,

            ai_reply,

            whatsapp_response
        )

        if not outgoing:

            print(
                "STEP 3 FAILED: Could not save outgoing message."
            )

            # Message was sent even if database save failed.
            # Continue to update incoming message.
        else:

            print(
                "STEP 3 SUCCESS: Outgoing message saved."
            )

        # -------------------------------------------------
        # UPDATE INCOMING MESSAGE
        # -------------------------------------------------

        print(
            "STEP 4: UPDATING INCOMING MESSAGE"
        )

        incoming_updated = (
            update_incoming_message_with_ai_reply(

                stored_message.get("id"),

                ai_reply
            )
        )

        print(
            "Incoming message updated:",
            incoming_updated
        )

        # -------------------------------------------------
        # UPDATE CUSTOMER AI REPLY
        # -------------------------------------------------

        if customer_id:

            print(
                "STEP 5: UPDATING CUSTOMER AI REPLY"
            )

            updated = update_customer_ai_reply(

                user_id,

                customer_id,

                ai_reply
            )

            print(
                "Customer ai_reply field updated:",
                updated
            )

        print(
            "================================================"
        )

        print(
            "BACKGROUND WHATSAPP AI PROCESS COMPLETE"
        )

        print(
            "================================================"
        )

        return True

    except Exception as error:

        print(
            "================================================"
        )

        print(
            "CRITICAL WHATSAPP AI THREAD ERROR"
        )

        print(
            str(error)
        )

        traceback.print_exc()

        print(
            "================================================"
        )

        return False


# =========================================================
# START WHATSAPP AI BACKGROUND THREAD
# =========================================================

def start_whatsapp_ai_thread(
    integration,
    stored_message
):

    try:

        # Keep the worker non-daemon so the Python process does not discard
        # the WhatsApp AI job immediately after the webhook returns 200.
        thread = threading.Thread(

            target=process_whatsapp_ai_reply,

            args=(
                integration,
                stored_message
            ),

            daemon=False,
            name="whatsapp-ai-worker"
        )

        thread.start()

        print(
            "WHATSAPP AI BACKGROUND THREAD STARTED:",
            thread.name
        )

        return True

    except Exception as error:

        print(
            "Failed to start WhatsApp AI thread:",
            error
        )

        traceback.print_exc()

        return False


# =========================================================
# WHATSAPP WEBHOOK VERIFY
# =========================================================

@app.route(
    "/api/whatsapp/webhook",
    methods=["GET"]
)
def whatsapp_webhook_verify():

    mode = request.args.get(
        "hub.mode"
    )

    token = request.args.get(
        "hub.verify_token"
    )

    challenge = request.args.get(
        "hub.challenge"
    )

    if (
        mode == "subscribe"
        and token
        and WHATSAPP_VERIFY_TOKEN
        and token == WHATSAPP_VERIFY_TOKEN
    ):

        print(
            "WhatsApp webhook verification successful."
        )

        return challenge or "", 200

    print(
        "WhatsApp webhook verification failed."
    )

    return "Forbidden", 403


# =========================================================
# WHATSAPP WEBHOOK
#
# IMPORTANT:
# This endpoint now stores messages and immediately
# returns 200.
#
# AI processing happens AFTER this through threading.
# =========================================================

@app.route(
    "/api/whatsapp/webhook",
    methods=["POST"]
)
def whatsapp_webhook():

    print("========== WHATSAPP WEBHOOK START ==========")
    print("Webhook method:", request.method, flush=True)

    try:
        payload = request.get_json(silent=True) or {}
    except Exception as error:
        print("WHATSAPP PAYLOAD JSON ERROR:", error, flush=True)
        return jsonify({"success": True}), 200

    print("========== WHATSAPP PAYLOAD RECEIVED ==========")
    print(payload, flush=True)

    # Meta may send status-only events. They are valid webhooks and must
    # receive 200, but they do not contain an inbound customer message.
    if payload.get("object") != "whatsapp_business_account":
        print(
            "Webhook object is not whatsapp_business_account:",
            payload.get("object"),
            flush=True
        )
        return jsonify({
            "success": True,
            "processed": 0
        }), 200

    entries = payload.get("entry") or []
    processed = 0
    threads_started = 0
    status_events = 0
    errors = 0

    for entry in entries:

        for change in (
            entry.get("changes") or []
        ):

            value = change.get(
                "value"
            ) or {}

            field = change.get(
                "field"
            )

            print(
                "Webhook field:",
                field,
                flush=True
            )

            metadata = value.get(
                "metadata"
            ) or {}

            phone_number_id = str(
                metadata.get(
                    "phone_number_id"
                ) or ""
            ).strip()

            print(
                "META PHONE NUMBER ID:",
                phone_number_id,
                flush=True
            )

            # Do not silently lose a message if metadata is missing. The
            # integration lookup will still be attempted using the configured
            # phone number ID when available.
            lookup_phone_number_id = (
                phone_number_id
                or str(
                    WHATSAPP_PHONE_NUMBER_ID
                    or ""
                ).strip()
            )

            integration = find_whatsapp_integration(
                lookup_phone_number_id
            )

            if not integration:

                print(
                    "NO INTEGRATION FOUND FOR PHONE NUMBER ID:",
                    lookup_phone_number_id,
                    flush=True
                )

                errors += 1

                continue

            print(
                "MATCHED INTEGRATION:",
                integration.get("id"),
                flush=True
            )

            print(
                "MATCHED USER:",
                integration.get("user_id"),
                flush=True
            )

            messages = (
                value.get("messages")
                or []
            )

            statuses = (
                value.get("statuses")
                or []
            )

            if statuses and not messages:

                status_events += len(
                    statuses
                )

                print(
                    "STATUS EVENT RECEIVED:",
                    statuses,
                    flush=True
                )

            if not messages:

                print(
                    "NO INBOUND MESSAGES IN THIS WEBHOOK EVENT.",
                    flush=True
                )

                continue

            contacts = (
                value.get("contacts")
                or []
            )

            contact_names = {}

            for contact in contacts:

                wa_id = str(
                    contact.get(
                        "wa_id"
                    ) or ""
                ).strip()

                profile = (
                    contact.get(
                        "profile"
                    )
                    or {}
                )

                profile_name = str(
                    profile.get(
                        "name"
                    ) or ""
                ).strip()

                if wa_id:
                    contact_names[
                        wa_id
                    ] = profile_name

            # Meta normally sends one contact for the message batch, but use
            # the message's own sender ID whenever possible.
            default_contact_name = ""

            if contacts:

                default_contact_name = str(
                    (
                        contacts[0].get(
                            "profile"
                        )
                        or {}
                    ).get(
                        "name"
                    )
                    or ""
                ).strip()

            for incoming in messages:

                try:

                    external_message_id = str(
                        incoming.get(
                            "id"
                        ) or ""
                    ).strip()

                    print(
                        "INCOMING META MESSAGE ID:",
                        external_message_id,
                        flush=True
                    )

                    if not external_message_id:

                        print(
                            "SKIPPING MESSAGE: Meta message ID is missing.",
                            flush=True
                        )

                        errors += 1

                        continue

                    if whatsapp_message_exists(
                        external_message_id
                    ):

                        print(
                            "DUPLICATE MESSAGE:",
                            external_message_id,
                            flush=True
                        )

                        continue

                    sender_phone = str(
                        incoming.get(
                            "from"
                        ) or ""
                    ).strip()

                    message_type = str(
                        incoming.get(
                            "type"
                        ) or ""
                    ).strip().lower()

                    message_text = ""

                    if message_type == "text":

                        message_text = str(
                            (
                                incoming.get(
                                    "text"
                                )
                                or {}
                            ).get(
                                "body"
                            )
                            or ""
                        ).strip()

                    elif message_type == "button":

                        button = (
                            incoming.get(
                                "button"
                            )
                            or {}
                        )

                        message_text = str(
                            button.get(
                                "text"
                            )
                            or button.get(
                                "payload"
                            )
                            or ""
                        ).strip()

                    elif message_type == "interactive":

                        interactive = (
                            incoming.get(
                                "interactive"
                            )
                            or {}
                        )

                        interactive_type = str(
                            interactive.get(
                                "type"
                            )
                            or ""
                        ).strip()

                        if interactive_type == "button_reply":

                            reply = (
                                interactive.get(
                                    "button_reply"
                                )
                                or {}
                            )

                            message_text = str(
                                reply.get(
                                    "title"
                                )
                                or reply.get(
                                    "id"
                                )
                                or ""
                            ).strip()

                        elif interactive_type == "list_reply":

                            reply = (
                                interactive.get(
                                    "list_reply"
                                )
                                or {}
                            )

                            message_text = str(
                                reply.get(
                                    "title"
                                )
                                or reply.get(
                                    "description"
                                )
                                or reply.get(
                                    "id"
                                )
                                or ""
                            ).strip()

                        else:

                            message_text = (
                                "[interactive message]"
                            )

                    else:

                        message_text = (
                            "["
                            + message_type
                            + " message]"
                        )

                    sender_name = (
                        contact_names.get(
                            sender_phone
                        )
                        or default_contact_name
                    ).strip()

                    print(
                        "SENDER:",
                        sender_phone,
                        flush=True
                    )

                    print(
                        "CUSTOMER NAME:",
                        sender_name,
                        flush=True
                    )

                    print(
                        "MESSAGE TYPE:",
                        message_type,
                        flush=True
                    )

                    print(
                        "MESSAGE TEXT:",
                        message_text,
                        flush=True
                    )

                    if (
                        not sender_phone
                        or not message_text
                    ):

                        print(
                            "SKIPPING MESSAGE: sender phone or message text is empty.",
                            flush=True
                        )

                        errors += 1

                        continue

                    # -------------------------------------------------
                    # STORE INCOMING MESSAGE BEFORE STARTING AI
                    # -------------------------------------------------

                    stored = store_whatsapp_message(

                        integration,

                        sender_phone,

                        sender_name,

                        message_text,

                        external_message_id
                    )

                    if not stored:

                        print(
                            "FAILED TO STORE INCOMING MESSAGE:",
                            external_message_id,
                            flush=True
                        )

                        errors += 1

                        continue

                    processed += 1

                    print(
                        "INCOMING MESSAGE STORED:",
                        stored,
                        flush=True
                    )

                    # -------------------------------------------------
                    # START AI PROCESSING
                    # -------------------------------------------------

                    thread_started = start_whatsapp_ai_thread(

                        integration,

                        stored
                    )

                    print(
                        "AI THREAD STARTED:",
                        thread_started,
                        flush=True
                    )

                    if thread_started:

                        threads_started += 1

                    else:

                        errors += 1

                except Exception as error:

                    errors += 1

                    print(
                        "WHATSAPP MESSAGE PROCESSING ERROR:",
                        error,
                        flush=True
                    )

                    traceback.print_exc()

    print(
        "========== WHATSAPP WEBHOOK END ==========",
        flush=True
    )

    print(
        "Webhook summary:",
        {
            "processed":
                processed,

            "ai_threads_started":
                threads_started,

            "status_events":
                status_events,

            "errors":
                errors
        },
        flush=True
    )

    # Always acknowledge Meta after the webhook payload has been accepted.
    return jsonify({

        "success":
            True,

        "processed":
            processed,

        "ai_threads_started":
            threads_started,

        "status_events":
            status_events,

        "errors":
            errors
    }), 200


# =========================================================
# REPORTS
# =========================================================

@app.route(
    "/api/reports",
    methods=["GET"]
)
def get_reports():

    user = get_authenticated_user()

    if not user:

        return jsonify({
            "error":
                "Invalid or expired login session."
        }), 401

    user_id = user["id"]

    try:

        customers_response = supabase_get(
            CUSTOMERS_URL,
            {
                "select":
                    "*",

                "user_id":
                    "eq." + user_id,

                "order":
                    "created_at.desc"
            }
        )

        ai_response = supabase_get(
            AI_CONVERSATIONS_URL,
            {
                "select":
                    "*",

                "user_id":
                    "eq." + user_id,

                "order":
                    "created_at.desc"
            }
        )

        business_response = supabase_get(
            BUSINESS_ACCOUNTS_URL,
            {
                "select":
                    "*",

                "user_id":
                    "eq." + user_id,

                "limit":
                    "1"
            }
        )

        automation_response = supabase_get(
            AUTOMATION_SETTINGS_URL,
            {
                "select":
                    "*",

                "user_id":
                    "eq." + user_id,

                "limit":
                    "1"
            }
        )

        customers = (
            customers_response.json()
            if customers_response.status_code == 200
            else []
        )

        ai_conversations = (
            ai_response.json()
            if ai_response.status_code == 200
            else []
        )

        businesses = (
            business_response.json()
            if business_response.status_code == 200
            else []
        )

        automation_rows = (
            automation_response.json()
            if automation_response.status_code == 200
            else []
        )

        automation = (

            automation_rows[0]

            if automation_rows

            else {

                "ai_replies":
                    True,

                "message_automation":
                    True,

                "task_automation":
                    True
            }
        )

        return jsonify({

            "success":
                True,

            "report": {

                "business":
                    businesses[0]
                    if businesses
                    else None,

                "total_customers":
                    len(customers),

                "total_ai_conversations":
                    len(ai_conversations),

                "total_ai_replies":
                    len([

                        x

                        for x in ai_conversations

                        if str(
                            x.get(
                                "answer",
                                ""
                            )
                        ).strip()
                    ]),

                "automation":
                    automation,

                "customers":
                    customers,

                "ai_conversations":
                    ai_conversations
            }
        })

    except Exception as error:

        print(
            "Reports GET exception:",
            error
        )

        traceback.print_exc()

        return jsonify({
            "error":
                str(error)
        }), 500


# =========================================================
# APPLICATION START
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    print(
        "================================================"
    )

    print(
        "NexaFlow AI starting..."
    )

    print(
        "Port:",
        port
    )

    print(
        "WhatsApp AI background threading: ENABLED"
    )

    print(
        "WhatsApp webhook handler: ACTIVE / ROBUST PARSER ENABLED"
    )

    print(
        "WhatsApp phone number ID configured:",
        bool(WHATSAPP_PHONE_NUMBER_ID)
    )

    print(
        "WhatsApp access token configured:",
        bool(WHATSAPP_ACCESS_TOKEN)
    )

    print(
        "OpenRouter API key configured:",
        bool(OPENROUTER_API_KEY)
    )

    print(
        "Supabase secret key configured:",
        bool(SUPABASE_SECRET_KEY)
    )

    print(
        "================================================"
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
