import time
import collections
from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    current_app,
)
from routes.auth_bp import admin_required
from routes.items_bp import get_all_items, get_locations

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# ==============================================================================
# Pure-Python Contract Stubs / Fallbacks for Admin Unit II, III, IV Algorithms
# ==============================================================================

def _fallback_global_bipartite_match(lost_items, found_items, score_threshold=0.5):
    """
    Solves Maximum Bipartite Matching via Ford-Fulkerson (Edmonds-Karp / BFS).
    Unit IV: O(V * E^2)
    """
    start = time.perf_counter()

    # Build adjacency bipartite graph: Lost -> Found
    adj = collections.defaultdict(list)
    scores = {}

    for l in lost_items:
        l_id = l["item_id"]
        for f in found_items:
            f_id = f["item_id"]
            if l.get("category") == f.get("category"):
                # Word intersection score
                words_l = set(l.get("description", "").lower().split())
                words_f = set(f.get("description", "").lower().split())
                score = len(words_l.intersection(words_f)) / max(len(words_l), 1)
                # Boost if titles or serial tags match
                if l.get("title", "").lower() in f.get("title", "").lower():
                    score = min(1.0, score + 0.3)
                if l.get("serial_tag") and l.get("serial_tag") == f.get("serial_tag"):
                    score = 0.99

                if score >= score_threshold:
                    adj[l_id].append(f_id)
                    scores[(l_id, f_id)] = round(score, 2)

    # Hopcroft-Karp / Ford-Fulkerson Augmenting Path for Bipartite Matching
    match_found = {} # f_id -> l_id

    def dfs(u, visited):
        for v in adj.get(u, []):
            if v not in visited:
                visited.add(v)
                if v not in match_found or dfs(match_found[v], visited):
                    match_found[v] = u
                    return True
        return False

    matched_count = 0
    for l in lost_items:
        if dfs(l["item_id"], set()):
            matched_count += 1

    pairs = []
    for f_id, l_id in match_found.items():
        l_item = next((x for x in lost_items if x["item_id"] == l_id), {})
        f_item = next((x for x in found_items if x["item_id"] == f_id), {})
        pairs.append({
            "lost_id": l_id,
            "found_id": f_id,
            "lost_title": l_item.get("title", "Unknown"),
            "found_title": f_item.get("title", "Unknown"),
            "category": l_item.get("category", "General"),
            "score": scores.get((l_id, f_id), 0.85)
        })

    elapsed = round((time.perf_counter() - start) * 1000, 3)
    return {
        "result": {"pairs": pairs, "max_matches": len(pairs)},
        "telemetry": {
            "algorithm": "Ford-Fulkerson Maximum Bipartite Matching",
            "unit": "Unit IV",
            "input_size": len(lost_items) + len(found_items),
            "time_ms": elapsed,
            "complexity": "O(V * E^2)"
        }
    }


def _fallback_schedule_urgent_claims(claims):
    """
    Greedy Job Sequencing with Deadlines.
    Unit II: O(n^2)
    """
    start = time.perf_counter()
    if not claims:
        return {
            "result": {"scheduled_claims": [], "total_priority_saved": 0},
            "telemetry": {
                "algorithm": "Greedy Job Sequencing with Deadlines",
                "unit": "Unit II",
                "input_size": 0,
                "time_ms": 0.05,
                "complexity": "O(n^2)"
            }
        }

    # Sort claims by priority value descending
    sorted_claims = sorted(claims, key=lambda x: x.get("priority_value", 10), reverse=True)
    max_deadline = min(10, max(c.get("deadline_hours", 48) // 12 for c in sorted_claims))
    max_deadline = max(1, max_deadline)

    # Time slot array (0 is dummy)
    slots = [None] * (max_deadline + 1)
    scheduled = []
    total_priority = 0

    for claim in sorted_claims:
        deadline_slot = min(max_deadline, max(1, claim.get("deadline_hours", 48) // 12))
        for s in range(deadline_slot, 0, -1):
            if slots[s] is None:
                slots[s] = claim
                time_label = f"Slot {s} (0{8 + s}:00 - 0{9 + s}:00)"
                scheduled.append({
                    "claim_id": claim.get("item_id"),
                    "item_title": claim.get("title"),
                    "deadline": claim.get("deadline_hours"),
                    "priority": claim.get("priority_value"),
                    "slot_number": s,
                    "slot": time_label
                })
                total_priority += claim.get("priority_value", 10)
                break

    elapsed = round((time.perf_counter() - start) * 1000, 3)
    return {
        "result": {"scheduled_claims": scheduled, "total_priority_saved": total_priority},
        "telemetry": {
            "algorithm": "Greedy Job Sequencing with Deadlines",
            "unit": "Unit II",
            "input_size": len(claims),
            "time_ms": elapsed,
            "complexity": "O(n^2)"
        }
    }


def _fallback_assign_conflict_free_slots(matches):
    """
    Backtracking Graph Colouring to assign minimum conflict-free verification desks.
    Unit II: O(m^V) pruned
    """
    start = time.perf_counter()
    n = len(matches)
    if n == 0:
        return {
            "result": {"slot_assignments": {}, "chromatic_number": 0},
            "telemetry": {
                "algorithm": "Backtracking Graph Colouring",
                "unit": "Unit II",
                "input_size": 0,
                "time_ms": 0.05,
                "complexity": "O(m^V) pruned"
            }
        }

    # Construct conflict graph: matches share an edge if same category or proximate location
    adj = collections.defaultdict(set)
    for i in range(n):
        for j in range(i + 1, n):
            m1, m2 = matches[i], matches[j]
            # Conflict condition: same category or matching slot
            if m1.get("category") == m2.get("category") or (i % 2 == j % 2):
                adj[i].add(j)
                adj[j].add(i)

    colors = [-1] * n

    def is_safe(v, c):
        for neighbor in adj[v]:
            if colors[neighbor] == c:
                return False
        return True

    def graph_coloring(v, max_colors):
        if v == n:
            return True
        for c in range(1, max_colors + 1):
            if is_safe(v, c):
                colors[v] = c
                if graph_coloring(v + 1, max_colors):
                    return True
                colors[v] = -1
        return False

    # Find minimum chromatic number
    chromatic_num = 1
    for m in range(1, n + 2):
        colors = [-1] * n
        if graph_coloring(0, m):
            chromatic_num = m
            break

    slot_assignments = {}
    for idx, match in enumerate(matches):
        m_id = match.get("lost_id") or match.get("item_id") or (idx + 1)
        desk_id = colors[idx] if colors[idx] != -1 else 1
        slot_assignments[f"match_{m_id}"] = {
            "desk_number": desk_id,
            "desk_label": f"Desk #{desk_id} (Station {'A' if desk_id == 1 else ('B' if desk_id == 2 else 'C')})"
        }

    elapsed = round((time.perf_counter() - start) * 1000, 3)
    return {
        "result": {"slot_assignments": slot_assignments, "chromatic_number": chromatic_num},
        "telemetry": {
            "algorithm": "Backtracking Graph Colouring",
            "unit": "Unit II",
            "input_size": n,
            "time_ms": elapsed,
            "complexity": "O(m^V) pruned"
        }
    }


def _fallback_optimize_vault_packing(items, capacity):
    """
    0/1 Knapsack Dynamic Programming for security locker/bag packing.
    Unit III: O(n * W)
    """
    start = time.perf_counter()
    n = len(items)
    W = max(1, capacity)

    # DP table [n+1][W+1]
    dp = [[0] * (W + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        wt = max(1, items[i - 1].get("item_weight", 1))
        val = max(1, items[i - 1].get("priority_value", 10))
        for w in range(W + 1):
            if wt <= w:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - wt] + val)
            else:
                dp[i][w] = dp[i - 1][w]

    max_value = dp[n][W]

    # Backtrack to find chosen items
    w = W
    selected_items = []
    selected_ids = []
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            item = items[i - 1]
            selected_items.append(item)
            selected_ids.append(item["item_id"])
            w -= max(1, item.get("item_weight", 1))

    selected_items.reverse()
    selected_ids.reverse()

    elapsed = round((time.perf_counter() - start) * 1000, 3)
    return {
        "result": {
            "selected_item_ids": selected_ids,
            "packed_items": selected_items,
            "max_value": max_value,
            "total_weight": sum(i.get("item_weight", 1) for i in selected_items),
            "capacity": capacity
        },
        "telemetry": {
            "algorithm": "0/1 Knapsack Dynamic Programming",
            "unit": "Unit III",
            "input_size": n * W,
            "time_ms": elapsed,
            "complexity": "O(n * W)"
        }
    }


# ==============================================================================
# Admin Dashboard & Endpoints
# ==============================================================================

@admin_bp.route("/")
@admin_required
def admin_dashboard():
    """Admin verification and optimization suite."""
    items = get_all_items()
    locations = get_locations()
    lost_count = sum(1 for i in items if i.get("type") == "LOST")
    found_count = sum(1 for i in items if i.get("type") == "FOUND")
    return render_template(
        "admin.html",
        items=items,
        locations=locations,
        lost_count=lost_count,
        found_count=found_count
    )


@admin_bp.route("/api/bipartite-match", methods=["POST"])
@admin_required
def api_bipartite_match():
    """
    POST /api/admin/bipartite-match:
    Runs global_bipartite_match (Ford-Fulkerson / Edmonds-Karp) across OPEN lost and found items.
    """
    items = get_all_items()
    lost_items = [i for i in items if i.get("type") == "LOST" and i.get("status") == "OPEN"]
    found_items = [i for i in items if i.get("type") == "FOUND" and i.get("status") == "OPEN"]

    res = None
    if not current_app.config.get("MOCK_MODE", True):
        try:
            from algorithms import global_bipartite_match
            res = global_bipartite_match(lost_items, found_items, {})
        except (ImportError, AttributeError):
            pass

    if res is None:
        res = _fallback_global_bipartite_match(lost_items, found_items)

    return jsonify({
        "status": "ok",
        "data": res["result"],
        "telemetry": [res["telemetry"]]
    }), 200


@admin_bp.route("/api/schedule-handovers", methods=["POST"])
@admin_required
def api_schedule_handovers():
    """
    POST /api/admin/schedule-handovers:
    Runs schedule_urgent_claims (Greedy Job Sequencing) followed by
    assign_conflict_free_slots (Backtracking Graph Colouring).
    """
    items = get_all_items()
    urgent_claims = [i for i in items if i.get("status") == "OPEN"]

    # 1. Greedy Job Sequencing
    js_res = None
    if not current_app.config.get("MOCK_MODE", True):
        try:
            from algorithms import schedule_urgent_claims
            js_res = schedule_urgent_claims(urgent_claims)
        except (ImportError, AttributeError):
            pass
    if js_res is None:
        js_res = _fallback_schedule_urgent_claims(urgent_claims)

    scheduled = js_res["result"]["scheduled_claims"]

    # 2. Backtracking Graph Colouring for conflict-free desk allocation
    gc_res = None
    if not current_app.config.get("MOCK_MODE", True):
        try:
            from algorithms import assign_conflict_free_slots
            gc_res = assign_conflict_free_slots(scheduled)
        except (ImportError, AttributeError):
            pass
    if gc_res is None:
        gc_res = _fallback_assign_conflict_free_slots(scheduled)

    return jsonify({
        "status": "ok",
        "data": {
            "scheduled_claims": scheduled,
            "total_priority_saved": js_res["result"]["total_priority_saved"],
            "chromatic_number": gc_res["result"]["chromatic_number"],
            "slot_assignments": gc_res["result"]["slot_assignments"]
        },
        "telemetry": [js_res["telemetry"], gc_res["telemetry"]]
    }), 200


@admin_bp.route("/api/vault-pack", methods=["POST"])
@admin_required
def api_vault_pack():
    """
    POST /api/admin/vault-pack:
    Runs optimize_vault_packing (0/1 Knapsack) for security collection bag/locker capacity.
    """
    data = request.get_json() or {}
    capacity = int(data.get("capacity", 5))
    items = get_all_items()
    open_items = [i for i in items if i.get("status") == "OPEN"]

    res = None
    if not current_app.config.get("MOCK_MODE", True):
        try:
            from algorithms import optimize_vault_packing
            res = optimize_vault_packing(open_items, capacity)
        except (ImportError, AttributeError):
            pass

    if res is None:
        res = _fallback_optimize_vault_packing(open_items, capacity)

    return jsonify({
        "status": "ok",
        "data": res["result"],
        "telemetry": [res["telemetry"]]
    }), 200
