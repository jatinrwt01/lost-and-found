import functools
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    current_app,
)
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# In-memory mock users for decoupled frontend development (MOCK_MODE=True)
MOCK_USERS = [
    {
        "user_id": 1,
        "name": "Campus Admin",
        "roll_no": "ADMIN001",
        "email": "admin@campus.edu",
        "password_hash": generate_password_hash("admin123"),
        "role": "admin",
    },
    {
        "user_id": 2,
        "name": "Anshu Kala",
        "roll_no": "2024CS01",
        "email": "anshu@campus.edu",
        "password_hash": generate_password_hash("password123"),
        "role": "student",
    },
]


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


@auth_bp.app_context_processor
def inject_user():
    """Make current user info available in all Jinja templates."""
    return {
        "current_user": session.get("name"),
        "current_role": session.get("role"),
        "current_user_id": session.get("user_id"),
        "current_roll_no": session.get("roll_no"),
        "is_authenticated": session.get("user_id") is not None,
        "is_admin": session.get("role") == "admin",
    }


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("items.feed"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "").strip()

        if not identifier or not password:
            flash("Please provide roll number/email and password.", "danger")
            return render_template("login.html")

        # Database lookup if available and MOCK_MODE is disabled
        user = None
        if not current_app.config.get("MOCK_MODE", True):
            try:
                from database.db import get_db
                db = get_db()
                user = db.execute(
                    "SELECT * FROM users WHERE roll_no = ? OR email = ?",
                    (identifier, identifier),
                ).fetchone()
            except Exception as e:
                current_app.logger.warning(f"Database lookup failed, falling back to mock: {e}")

        # Fallback to mock users
        if user is None:
            for u in MOCK_USERS:
                if u["roll_no"].lower() == identifier.lower() or u["email"].lower() == identifier.lower():
                    if check_password_hash(u["password_hash"], password):
                        user = u
                        break
        else:
            if not check_password_hash(user["password_hash"], password):
                user = None

        if user:
            session.clear()
            session["user_id"] = user["user_id"]
            session["name"] = user["name"]
            session["roll_no"] = user["roll_no"]
            session["email"] = user["email"]
            session["role"] = user["role"]
            flash(f"Welcome back, {user['name']}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("items.feed"))
        else:
            flash("Invalid roll number/email or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("items.feed"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        roll_no = request.form.get("roll_no", "").strip().upper()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "student")

        if not (name and roll_no and email and password):
            flash("All fields are required.", "danger")
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
            # Store in mock users
            new_id = len(MOCK_USERS) + 1
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
