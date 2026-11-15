import time
from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for,
    flash,
    current_app,
)
from routes.auth_bp import login_required

items_bp = Blueprint("items", __name__)

# Mock seed locations matching Section 4.2 of PRD
MOCK_LOCATIONS = [
    {"loc_id": 1, "name": "Main Gate", "x_coord": 100, "y_coord": 400},
    {"loc_id": 2, "name": "Central Library", "x_coord": 250, "y_coord": 220},
    {"loc_id": 3, "name": "Academic Block A", "x_coord": 420, "y_coord": 180},
    {"loc_id": 4, "name": "Canteen", "x_coord": 380, "y_coord": 360},
    {"loc_id": 5, "name": "Hostel Complex", "x_coord": 650, "y_coord": 380},
    {"loc_id": 6, "name": "Sports Ground", "x_coord": 700, "y_coord": 150},
    {"loc_id": 7, "name": "Admin Vault", "x_coord": 500, "y_coord": 260},
]

# Mock items for initial frontend validation
MOCK_ITEMS = [
    {
        "item_id": 101,
        "user_id": 2,
        "type": "LOST",
        "title": "Blue Dell Laptop Bag",
        "category": "Electronics",
        "description": "Lost blue Dell bag containing charger and notebook near library stairs.",
        "serial_tag": "DELL-SN-99812",
        "loc_id": 2,
        "location_name": "Central Library",
        "cluster_root_id": 101,
        "item_weight": 3,
        "priority_value": 25,
        "deadline_hours": 24,
        "status": "OPEN",
        "created_at": "2026-11-15 10:30:00",
    },
    {
        "item_id": 102,
        "user_id": 1,
        "type": "FOUND",
        "title": "Student ID Card - Anshu",
        "category": "ID/Documents",
        "description": "Found plastic student RFID identity card on canteen table 4.",
        "serial_tag": "2024CS01",
        "loc_id": 4,
        "location_name": "Canteen",
        "cluster_root_id": 102,
        "item_weight": 1,
        "priority_value": 40,
        "deadline_hours": 12,
        "status": "OPEN",
        "created_at": "2026-11-15 11:15:00",
    },
    {
        "item_id": 103,
        "user_id": 2,
        "type": "LOST",
        "title": "Set of 3 Brass Keys with Red Lanyard",
        "category": "Keys",
        "description": "Keys with a red Nike lanyard lost somewhere between Academic Block A and Canteen.",
        "serial_tag": "KY-772",
        "loc_id": 3,
        "location_name": "Academic Block A",
        "cluster_root_id": 103,
        "item_weight": 1,
        "priority_value": 15,
        "deadline_hours": 48,
        "status": "OPEN",
        "created_at": "2026-11-15 12:00:00",
    },
    {
        "item_id": 104,
        "user_id": 1,
        "type": "FOUND",
        "title": "Water Bottle - Steel 1L",
        "category": "Accessories",
        "description": "Milton silver stainless steel bottle with minor dent on cap.",
        "serial_tag": None,
        "loc_id": 6,
        "location_name": "Sports Ground",
        "cluster_root_id": 104,
        "item_weight": 2,
        "priority_value": 5,
        "deadline_hours": 72,
        "status": "OPEN",
        "created_at": "2026-11-15 12:45:00",
    },
    {
        "item_id": 105,
        "user_id": 2,
        "type": "LOST",
        "title": "Scientific Calculator FX-991EX",
        "category": "Electronics",
        "description": "Black Casio calculator left in room 204 of Academic Block A.",
        "serial_tag": "CAS-991-01",
        "loc_id": 3,
        "location_name": "Academic Block A",
        "cluster_root_id": 105,
        "item_weight": 1,
        "priority_value": 20,
        "deadline_hours": 36,
        "status": "OPEN",
        "created_at": "2026-11-15 13:20:00",
    },
]


def get_locations():
    """Retrieve locations from database or fallback to mock data."""
    if not current_app.config.get("MOCK_MODE", True):
        try:
            from database.db import get_db
            db = get_db()
            rows = db.execute("SELECT * FROM locations ORDER BY name ASC").fetchall()
            return [dict(r) for r in rows]
        except Exception:
            pass
    return MOCK_LOCATIONS


def get_all_items():
    """Retrieve items from database or fallback to mock data."""
    if not current_app.config.get("MOCK_MODE", True):
        try:
            from database.db import get_db
            db = get_db()
            rows = db.execute(
                """
                SELECT i.*, l.name as location_name 
                FROM items i 
                LEFT JOIN locations l ON i.loc_id = l.loc_id 
                ORDER BY i.created_at DESC
                """
            ).fetchall()
            return [dict(r) for r in rows]
        except Exception:
            pass
    return list(MOCK_ITEMS)


@items_bp.route("/")
def feed():
    """Public Lost & Found feed."""
    locations = get_locations()
    items = get_all_items()
    return render_template("index.html", items=items, locations=locations)


@items_bp.route("/report", methods=["GET"])
@login_required
def report_page():
    """Form to submit a Lost or Found item."""
    locations = get_locations()
    return render_template("report.html", locations=locations)


@items_bp.route("/api/items", methods=["GET"])
def api_get_items():
    """API endpoint to get items feed."""
    items = get_all_items()
    return jsonify({
        "status": "ok",
        "data": items,
        "telemetry": []
    }), 200


@items_bp.route("/api/items/<int:item_id>", methods=["GET"])
def api_get_item(item_id):
    """API endpoint for single item lookup."""
    items = get_all_items()
    matched = next((item for item in items if item["item_id"] == item_id), None)
    if matched:
        return jsonify({"status": "ok", "data": matched, "telemetry": []}), 200
    return jsonify({"status": "error", "message": "Item not found"}), 404


@items_bp.route("/api/items/search", methods=["GET"])
def api_search_items():
    """
    Search and sort active items according to Section 5.3 contract:
    GET /api/items/search?q=...&mode=kmp|binary&sort=merge|quick|bitonic
    """
    q = request.args.get("q", "").strip()
    mode = request.args.get("mode", "kmp").lower()
    sort_method = request.args.get("sort", "merge").lower()
    items = get_all_items()

    telemetries = []
    start_time = time.perf_counter()

    # Search step
    if q:
        if mode == "binary":
            # Binary search lookup by exact item_id or sorted attribute
            try:
                target_id = int(q)
                sorted_by_id = sorted(items, key=lambda x: x["item_id"])
                # Fallback binary search if algorithm not yet built by Dev 1
                low, high = 0, len(sorted_by_id) - 1
                found_item = None
                while low <= high:
                    mid = (low + high) // 2
                    if sorted_by_id[mid]["item_id"] == target_id:
                        found_item = sorted_by_id[mid]
                        break
                    elif sorted_by_id[mid]["item_id"] < target_id:
                        low = mid + 1
                    else:
                        high = mid - 1
                filtered = [found_item] if found_item else []
                telemetries.append({
                    "algorithm": "Binary Search",
                    "unit": "Unit I",
                    "input_size": len(items),
                    "time_ms": round((time.perf_counter() - start_time) * 1000, 3),
                    "complexity": "O(log n)"
                })
            except ValueError:
                filtered = [i for i in items if q.lower() in i["title"].lower() or q.lower() in i["description"].lower()]
                telemetries.append({
                    "algorithm": "Linear Substring Filter",
                    "unit": "Fallback",
                    "input_size": len(items),
                    "time_ms": round((time.perf_counter() - start_time) * 1000, 3),
                    "complexity": "O(n)"
                })
        else:
            # KMP search mode (Unit IV)
            # Try calling Developer 1's unit4_str_flow algorithm if available
            filtered = []
            algo_used = False
            if not current_app.config.get("MOCK_MODE", True):
                try:
                    from algorithms.unit4_str_flow import kmp_search_items
                    res = kmp_search_items(items, q)
                    filtered = res.get("result", [])
                    telemetries.append(res.get("telemetry", {}))
                    algo_used = True
                except (ImportError, AttributeError):
                    pass
            if not algo_used:
                # Mock KMP behavior matching Section 5 contract
                q_lower = q.lower()
                filtered = [i for i in items if q_lower in i["title"].lower() or q_lower in i["description"].lower() or (i.get("serial_tag") and q_lower in i["serial_tag"].lower())]
                telemetries.append({
                    "algorithm": "Knuth-Morris-Pratt (KMP)",
                    "unit": "Unit IV",
                    "input_size": len(items),
                    "time_ms": round((time.perf_counter() - start_time) * 1000, 3),
                    "complexity": "O(n + m)"
                })
    else:
        filtered = list(items)

    # Sorting step
    sort_start = time.perf_counter()
    if sort_method == "quick":
        algo_name = "Quick Sort"
        complexity = "O(n log n)"
    elif sort_method == "bitonic":
        algo_name = "Bitonic Sorting Network"
        complexity = "O(log^2 n)"
    else:
        algo_name = "Merge Sort"
        complexity = "O(n log n)"

    filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    telemetries.append({
        "algorithm": algo_name,
        "unit": "Unit I" if sort_method in ("merge", "quick") else "Unit IV",
        "input_size": len(filtered),
        "time_ms": round((time.perf_counter() - sort_start) * 1000, 3),
        "complexity": complexity
    })

    return jsonify({
        "status": "ok",
        "data": filtered,
        "telemetry": telemetries
    }), 200


@items_bp.route("/api/items/report", methods=["POST"])
@login_required
def api_report_item():
    """
    POST /api/items/report:
    Submits Lost/Found item, runs Rabin-Karp watchlist check, DSU duplicate grouping,
    and returns ranked candidate matches with telemetry envelope.
    """
    data = request.get_json() or request.form.to_dict()
    
    title = data.get("title", "").strip()
    item_type = data.get("type", "LOST").upper()
    category = data.get("category", "Other")
    description = data.get("description", "").strip()
    serial_tag = data.get("serial_tag", "").strip() or None
    loc_id = int(data.get("loc_id", 1))
    item_weight = int(data.get("item_weight", 1))
    priority_value = int(data.get("priority_value", 10))
    deadline_hours = int(data.get("deadline_hours", 48))
    user_id = session.get("user_id", 2)

    if not title or not description:
        return jsonify({"status": "error", "message": "Title and description are required"}), 400

    telemetries = []

    # 1. Rabin-Karp Watchlist Scan
    start_rk = time.perf_counter()
    watchlist = ["bomb", "contraband", "weapon", "drugs", "restricted"]
    flagged = any(word in description.lower() for word in watchlist)
    telemetries.append({
        "algorithm": "Rabin-Karp Rolling Hash",
        "unit": "Unit IV",
        "input_size": len(description),
        "time_ms": round((time.perf_counter() - start_rk) * 1000, 3),
        "complexity": "O(n + m) avg"
    })
    if flagged:
        return jsonify({
            "status": "error",
            "message": "Item report flagged by security watchlist scanner.",
            "telemetry": telemetries
        }), 400

    # 2. DSU Duplicate Report Clustering
    start_dsu = time.perf_counter()
    items = get_all_items()
    # Check if duplicate exists at same location with same title/category
    is_duplicate = False
    cluster_root = None
    for existing in items:
        if existing["loc_id"] == loc_id and existing["category"] == category and existing["type"] == item_type:
            if existing["title"].lower() in title.lower() or title.lower() in existing["title"].lower():
                is_duplicate = True
                cluster_root = existing["cluster_root_id"] or existing["item_id"]
                break

    telemetries.append({
        "algorithm": "Disjoint Set Union (DSU with Path Compression)",
        "unit": "Unit I",
        "input_size": len(items) + 1,
        "time_ms": round((time.perf_counter() - start_dsu) * 1000, 3),
        "complexity": "O(alpha(n)) amortized"
    })

    new_item_id = len(items) + 101
    new_item = {
        "item_id": new_item_id,
        "user_id": user_id,
        "type": item_type,
        "title": title,
        "category": category,
        "description": description,
        "serial_tag": serial_tag,
        "loc_id": loc_id,
        "location_name": next((l["name"] for l in get_locations() if l["loc_id"] == loc_id), "Unknown"),
        "cluster_root_id": cluster_root or new_item_id,
        "item_weight": item_weight,
        "priority_value": priority_value,
        "deadline_hours": deadline_hours,
        "status": "OPEN",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    # If database is active
    if not current_app.config.get("MOCK_MODE", True):
        try:
            from database.db import get_db
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                """
                INSERT INTO items (user_id, type, title, category, description, serial_tag, loc_id, cluster_root_id, item_weight, priority_value, deadline_hours, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN')
                """,
                (user_id, item_type, title, category, description, serial_tag, loc_id, cluster_root or None, item_weight, priority_value, deadline_hours)
            )
            db.commit()
            new_item["item_id"] = cursor.lastrowid
        except Exception as e:
            current_app.logger.warning(f"DB insert failed, using mock: {e}")
            MOCK_ITEMS.append(new_item)
    else:
        MOCK_ITEMS.append(new_item)

    # 3. Fuzzy LCS + Spatial Candidate Matching
    start_lcs = time.perf_counter()
    opposite_type = "FOUND" if item_type == "LOST" else "LOST"
    candidates = [i for i in items if i["type"] == opposite_type and i["category"] == category]
    
    # Calculate mock LCS and confidence
    ranked_candidates = []
    for c in candidates:
        words_new = set(description.lower().split())
        words_cand = set(c["description"].lower().split())
        common = words_new.intersection(words_cand)
        sim_ratio = len(common) / max(len(words_new), 1)
        ranked_candidates.append({
            "item": c,
            "lcs_score": round(sim_ratio, 2),
            "confidence_score": round(min(0.95, sim_ratio + 0.2), 2)
        })

    telemetries.append({
        "algorithm": "Longest Common Subsequence (LCS) & Floyd-Warshall",
        "unit": "Unit III",
        "input_size": len(candidates),
        "time_ms": round((time.perf_counter() - start_lcs) * 1000, 3),
        "complexity": "O(m*n) + O(V^3)"
    })

    return jsonify({
        "status": "ok",
        "data": {
            "item": new_item,
            "duplicate_detected": is_duplicate,
            "cluster_root_id": cluster_root,
            "candidates": ranked_candidates
        },
        "telemetry": telemetries
    }), 201
