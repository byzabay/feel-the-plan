"""Build the example page: python3 examples/build_example.py [out.html]   (default: examples/example.html)

A made-up app ("Pocket Planner") and a made-up user, to show the parts of a page:
lanes (who or what does the work), columns (steps), boxes with status tags, wires, a hover card with facts,
and a second tab with the sub-flow of one step (opened from that box's card with page.go).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import lanes  # noqa: E402
import page  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "example.html")

# ---------------------------------------------------------------- tab 1: the whole sign-up
LANES = [
    {"k": "you", "name": "You", "sub": "the developer", "tone": "you", "icon": "user"},
    {"k": "web", "name": "Browser app", "sub": "what the user sees", "tone": "app", "icon": "monitor"},
    {"k": "api", "name": "API server", "tone": "code", "icon": "server"},
    {"k": "db", "name": "Database", "tone": "db", "icon": "database"},
    {"k": "mail", "name": "Email service", "tone": "mail", "icon": "mail"},
    {"k": "ai", "name": "AI model", "tone": "ai", "icon": "brain"},
]
COLS = [
    {"k": "c1", "lv": "1", "name": "Fill in the form", "ex": "Sam types sam@example.com"},
    {"k": "c2", "lv": "2", "name": "Check and create", "ex": "Email is free, so the account is made"},
    {"k": "c3", "lv": "3", "name": "Save the user"},
    {"k": "c4", "lv": "4", "name": "Say welcome"},
    {"k": "c5", "lv": "5", "name": "Pick a first tip"},
    {"k": "c6", "lv": "6", "name": "Land on the dashboard"},
]

MAIL_CARD = (
    page.facts([
        ("What it does", "Sends one welcome email with a link to confirm the address."),
        ("Runs on", "A background job on the API server, so sign-up never waits for the email."),
        ("Status", "Off until the sending domain is verified."),
        ("Data in", "<code>user.email</code>, <code>user.name</code>"),
    ])
    + page.miniflow([("inbox", "Queue"), ("file-text", "Fill template"), ("send", "Send"), ("eye", "Opened")])
    + "<p>" + page.go("2", "Open the welcome-email sub-flow") + "</p>"
)
TIP_CARD = (
    page.facts([
        ("What it does", "Reads the new user's answers and picks one tip for their first day."),
        ("Model", "Claude Haiku, with Gemini Flash-Lite as a fallback"),
        ("Status", "Idea: not built yet."),
        ("Cost", "About a tenth of a cent per sign-up (made-up number)."),
    ])
    + page.prompt_block("Show the prompt", "## Task\nPick **one** tip for {{USER_NAME}}.\n\n- Keep it under 20 words\n- Use `plain` language")
)

NODES = [
    {"id": "ship", "lane": "you", "col": "c1", "kind": "human", "icon": "code", "t": "You ship the form", "tags": ["device:Your laptop"]},
    {"id": "form", "lane": "web", "col": "c1", "n": 1, "icon": "user-check", "t": "Sign-up form", "b": "Name, email, password", "tags": ["live"]},
    {"id": "signup", "lane": "api", "col": "c2", "n": 2, "icon": "shield-check", "t": "POST /signup", "b": "Checks the email is free and hashes the password", "tags": ["live", "cloud:Hosted"]},
    {"id": "users", "lane": "db", "col": "c3", "n": 3, "kind": "store", "icon": "database", "t": "users table", "b": "One new row", "tags": ["live"]},
    {"id": "welcome", "lane": "mail", "col": "c4", "n": 4, "icon": "mail", "t": "Welcome email", "b": "Hover or tap for details", "tags": ["off"], "detail": MAIL_CARD},
    {"id": "tip", "lane": "ai", "col": "c5", "n": 5, "kind": "ai", "icon": "lightbulb", "t": "First-day tip", "b": "Hover or tap for details", "tags": ["idea", "ai"], "detail": TIP_CARD},
    {"id": "dash", "lane": "web", "col": "c6", "n": 6, "icon": "layout-grid", "t": "Dashboard", "b": "Shows the tip at the top", "tags": ["next"]},
    {"id": "watch", "lane": "you", "col": "c6", "kind": "human", "icon": "activity", "t": "You watch sign-ups", "tags": ["app:Admin page"]},
]
EDGES = [
    {"f": "ship", "t": "form", "k": "dash", "lbl": "deploy"},
    {"f": "form", "t": "signup", "n": "1", "key": "The browser sends the form to the API."},
    {"f": "signup", "t": "users", "k": "data", "n": "2", "key": "The API writes the new user (green = a write)."},
    {"f": "signup", "t": "welcome", "k": "email", "n": "3", "key": "The API queues the welcome email."},
    {"f": "users", "t": "tip", "k": "dash", "lbl": "reads profile"},
    {"f": "tip", "t": "dash", "n": "4", "key": "The tip shows on the dashboard."},
    {"f": "dash", "t": "watch", "k": "loop", "lbl": "new sign-up"},
]
SPEC1 = {"id": "d1", "title": "What happens when a user signs up", "lanes": LANES, "cols": COLS, "nodes": NODES, "edges": EDGES}

# ---------------------------------------------------------------- tab 2: the welcome email up close
SPEC2 = {
    "id": "d2", "title": "Welcome email sub-flow",
    "lanes": [
        {"k": "api", "name": "API server", "tone": "code", "icon": "server"},
        {"k": "mail", "name": "Email service", "tone": "mail", "icon": "mail"},
        {"k": "user", "name": "New user", "sub": "Sam (made up)", "tone": "person", "icon": "user"},
    ],
    "cols": [
        {"k": "q", "lv": "1", "name": "Queue the job"},
        {"k": "r", "lv": "2", "name": "Fill the template"},
        {"k": "s", "lv": "3", "name": "Send"},
        {"k": "o", "lv": "4", "name": "Open and confirm"},
    ],
    "nodes": [
        {"id": "job", "lane": "api", "col": "q", "icon": "inbox", "t": "Job queued", "tags": ["live"]},
        {"id": "tpl", "lane": "api", "col": "r", "icon": "file-text", "t": "welcome.html", "b": "Name and confirm link filled in", "tags": ["live"]},
        {"id": "send", "lane": "mail", "col": "s", "icon": "send", "t": "Send via provider", "tags": ["off"]},
        {"id": "open", "lane": "user", "col": "o", "kind": "human", "icon": "check", "t": "Sam clicks Confirm", "tags": ["next"]},
    ],
    "edges": [
        {"f": "job", "t": "tpl"},
        {"f": "tpl", "t": "send", "k": "email"},
        {"f": "send", "t": "open", "k": "email"},
        {"f": "open", "t": "job", "k": "loop", "lbl": "confirmed"},
    ],
}

h1, d1 = lanes.render(SPEC1)
h2, d2 = lanes.render(SPEC2)

tab1 = (page.what("As a developer, I can see every step a new user's sign-up goes through, and which parts are live.",
                  [("Where does the welcome email actually get sent from?", "a made-up teammate")])
        + h1
        + page.qbox("Q1", "Should the welcome email wait for the AI tip?", "No, send it straight away",
                    "Sign-up should never wait on a slow model.")
        + page.note_box())
tab2 = (page.what("As a developer, I can follow the welcome email from the queue to the user's inbox.")
        + h2
        + '<div class="rbox"><h4>Why a queue</h4><p>The sign-up request returns as soon as the job is queued. '
          'If the email provider is down, the job retries later and the user still gets in.</p></div>')

nav = page.tabs_nav([{"key": "1", "num": "1", "name": "Sign-up"}, {"key": "2", "num": "2", "name": "Welcome email"}], "Steps")
sections = page.section("1", True, tab1) + "\n" + page.section("2", False, tab2)
html = page.page(
    "Sign-up flow example", "Example page: every name and number is made up.",
    "Example page · made-up app and data",
    '<header class="intro"><h1>What happens when a user signs up</h1>'
    "<p>Pocket Planner is a made-up app. Read left to right; hover or tap a box with a card.</p></header>",
    "", nav, sections, "Made-up example.", look="v4")

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print("wrote", OUT, "tab 1:", d1.width, "x", d1.height, "crossings", d1.crossings, "| tab 2 crossings", d2.crossings,
      *(d1.notes + d2.notes))
