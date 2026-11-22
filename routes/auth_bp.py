import functools
import secrets
from urllib.parse import urlparse

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    current_app,
    abort,
)
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# In-memory mock users for decoupled frontend development (aligned with database/seed.py)
MOCK_USERS = [
    {
        "user_id": 1,
        "name": "Admin Officer",
        "roll_no": "ADM001",
        "email": "admin@campus.edu",
        "password_hash": generate_password_hash("Admin@123"),
        "role": "admin",
    },
    {
        "user_id": 1,
        "name": "Campus Admin (Legacy Mock)",
        "roll_no": "ADMIN001",
        "email": "admin-mock@campus.edu",
        "password_hash": generate_password_hash("admin123"),
        "role": "admin",
    },
    {
        "user_id": 2,
        "name": "Aarav Sharma",
        "roll_no": "2023CS01",
        "email": "aarav@campus.edu",
        "password_hash": generate_password_hash("Student@123"),
        "role": "student",
    },
    {
        "user_id": 3,
        "name": "Anshu Kala",
        "roll_no": "2024CS01",
        "email": "anshu@campus.edu",
        "password_hash": generate_password_hash("password123"),
        "role": "student",
    },
]


# ---------------------------------------------------------------------------
# Security helpers
# ---------------------------------------------------------------------------

def _generate_csrf_token() -> str:
    """Generate and store a CSRF token in the session if not already set."""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]


def _validate_csrf() -> None:
    """Validate CSRF token from form data against session token. Abort 403 on mismatch."""
    token = request.form.get("csrf_token", "")
    expected = session.get("csrf_token", "")
    if not expected or not secrets.compare_digest(token, expected):
        abort(403)


def _safe_next_url(next_url: str | None) -> str | None:
    """
    Validate a redirect URL to prevent open-redirect attacks.
    Returns the URL only if it is a same-origin relative path starting with '/'.
    """
    if not next_url:
        return None
    parsed = urlparse(next_url)
    # Allow only relative paths: no scheme, no netloc, starts with '/'
    # Reject protocol-relative URLs like //evil.com
    if parsed.scheme or parsed.netloc:
        return None
    if not parsed.path.startswith("/"):
        return None
    return next_url


# ---------------------------------------------------------------------------
# Access-control decorators
# ---------------------------------------------------------------------------

def login_required(view):
    """Decorator to require login for a route."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get("user_id") is None:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return view(**kwargs)
    return wrapped_view


def admin_required(view):
    """Decorator to require admin privileges for a route."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get("user_id") is None:
            flash("Please log in as an administrator to continue.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        if session.get("role") != "admin":
            flash("Access denied: Administrator privileges required.", "danger")
            return redirect(url_for("items.feed"))
        return view(**kwargs)
    return wrapped_view


# ---------------------------------------------------------------------------
# Template context processor
# ---------------------------------------------------------------------------

@auth_bp.app_context_processor
def inject_user():
    """Make current user info and CSRF token available in all Jinja templates."""
    return {
        "current_user": session.get("name"),
        "current_role": session.get("role"),
        "current_user_id": session.get("user_id"),
        "current_roll_no": session.get("roll_no"),
        "is_authenticated": session.get("user_id") is not None,
        "is_admin": session.get("role") == "admin",
        "csrf_token": _generate_csrf_token(),
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("items.feed"))

    if request.method == "POST":
        _validate_csrf()

        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "").strip()

        if not identifier or not password:
            flash("Please provide roll number/email and password.", "danger")
            return render_template("login.html")

        user = None
        db_lookup_succeeded = False

        # Database lookup when MOCK_MODE is disabled
        if not current_app.config.get("MOCK_MODE", True):
            try:
                from database.db import get_db
                db = get_db()
                row = db.execute(
                    "SELECT * FROM users WHERE roll_no = ? OR email = ?",
                    (identifier, identifier),
                ).fetchone()
                db_lookup_succeeded = True
                if row:
                    if check_password_hash(row["password_hash"], password):
                        user = dict(row)
            except Exception as e:
                current_app.logger.warning(f"Database login lookup failed: {e}")

        # Fallback to mock only when DB is unavailable (not as a bypass for wrong passwords)
        if not db_lookup_succeeded:
            for u in MOCK_USERS:
                if u["roll_no"].lower() == identifier.lower() or u["email"].lower() == identifier.lower():
                    if check_password_hash(u["password_hash"], password):
                        user = u
                        break

        if user:
            session.clear()
            session["user_id"] = user["user_id"]
            session["name"] = user["name"]
            session["roll_no"] = user["roll_no"]
            session["email"] = user["email"]
            session["role"] = user["role"]
            flash(f"Welcome back, {user['name']}!", "success")
            next_page = _safe_next_url(request.args.get("next"))
            return redirect(next_page or url_for("items.feed"))
        else:
            flash("Invalid roll number/email or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("items.feed"))

    if request.method == "POST":
        _validate_csrf()

        name = request.form.get("name", "").strip()
        roll_no = request.form.get("roll_no", "").strip().upper()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        # Security: role is ALWAYS forced to 'student' on public registration.
        # Administrators can only be created via database seeding or direct DB access.
        role = "student"

        if not (name and roll_no and email and password):
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return render_template("register.html")

        pwd_hash = generate_password_hash(password)

        if not current_app.config.get("MOCK_MODE", True):
            try:
                from database.db import get_db
                db = get_db()
                db.execute(
                    "INSERT INTO users (name, roll_no, email, password_hash, role) VALUES (?, ?, ?, ?, ?)",
                    (name, roll_no, email, pwd_hash, role),
                )
                db.commit()
                flash("Registration successful! You may now log in.", "success")
                return redirect(url_for("auth.login"))
            except Exception as e:
                flash(f"Registration error: {e}", "danger")
                return render_template("register.html")
        else:
            # Store in mock users (MOCK_MODE only)
            new_id = max((u["user_id"] for u in MOCK_USERS), default=0) + 1
            MOCK_USERS.append({
                "user_id": new_id,
                "name": name,
                "roll_no": roll_no,
                "email": email,
                "password_hash": pwd_hash,
                "role": role,
            })
            flash("Registration successful! (MOCK MODE active). Please log in.", "success")
            return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
