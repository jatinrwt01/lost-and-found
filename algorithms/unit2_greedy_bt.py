import heapq
import math
from typing import Any, Dict, Iterable, List, Optional, Set
from algorithms.metrics import measure_daa

UNREACHABLE_SENTINEL = -1.0


class _DisjointSetUnion:
    def __init__(self, elements: Iterable[int]) -> None:
        self.parent: Dict[int, int] = {elem: elem for elem in elements}
        self.rank: Dict[int, int] = {elem: 0 for elem in elements}

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False

        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1

        return True


@measure_daa(
    algorithm="Dijkstra's Algorithm",
    unit="Unit II",
    complexity="O((V + E) log V)",
    input_size_fn=lambda *args, **kwargs: len(args[0]) if args else len(kwargs.get("edges", [])),
)
def shortest_campus_path(edges: List[Dict[str, Any]], start_loc: int, end_loc: int) -> Dict[str, Any]:
    if not isinstance(start_loc, int) or isinstance(start_loc, bool):
        raise ValueError(f"start_loc must be an integer, got: {start_loc!r}")
    if not isinstance(end_loc, int) or isinstance(end_loc, bool):
        raise ValueError(f"end_loc must be an integer, got: {end_loc!r}")

    adj: Dict[int, List[tuple[int, float]]] = {}
    for edge in edges:
        dist_val = edge["distance_meters"]
        if isinstance(dist_val, bool):
            raise ValueError(f"Invalid edge weight ({dist_val!r}). Distances must be non-negative finite numbers.")
        try:
            dist = float(dist_val)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid edge weight ({dist_val!r}). Distances must be non-negative finite numbers.") from exc
        if not math.isfinite(dist) or dist < 0:
            raise ValueError(f"Invalid edge weight ({dist}). Distances must be non-negative finite numbers.")

        u = edge["src_loc_id"]
        v = edge["dst_loc_id"]
        if (
            not isinstance(u, int)
            or isinstance(u, bool)
            or not isinstance(v, int)
            or isinstance(v, bool)
        ):
            raise ValueError(f"Edge endpoints must be integers, got: src={u!r}, dst={v!r}")

        adj.setdefault(u, []).append((v, dist))
        adj.setdefault(v, []).append((u, dist))

    # Identity case: zero distance to self, valid even if location is not in edges.
    if start_loc == end_loc:
        return {"path": [start_loc], "total_meters": 0.0}

    if start_loc not in adj or end_loc not in adj:
        return {"path": [], "total_meters": UNREACHABLE_SENTINEL}

    pq: List[tuple[float, int]] = [(0.0, start_loc)]
    distances: Dict[int, float] = {start_loc: 0.0}
    parents: Dict[int, int] = {}
    visited: set[int] = set()

    while pq:
        curr_dist, u = heapq.heappop(pq)

        if u in visited:
            continue
        visited.add(u)

        if u == end_loc:
            break

        for v, weight in adj.get(u, []):
            new_dist = curr_dist + weight
            if v not in distances or new_dist < distances[v]:
                distances[v] = new_dist
                parents[v] = u
                heapq.heappush(pq, (new_dist, v))

    if end_loc not in visited:
        return {"path": [], "total_meters": UNREACHABLE_SENTINEL}

    path = []
    curr: Optional[int] = end_loc
    while curr is not None:
        path.append(curr)
        curr = parents.get(curr)
    path.reverse()

    return {
        "path": path,
        "total_meters": distances[end_loc],
    }


@measure_daa(
    algorithm="Kruskal's Algorithm",
    unit="Unit II",
    complexity="O(V + E log E)",
    input_size_fn=lambda *args, **kwargs: len(args[1]) if len(args) > 1 else len(kwargs.get("edges", [])),
)
def compute_dropbox_mst(num_nodes: int, edges: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(num_nodes, int) or isinstance(num_nodes, bool) or num_nodes < 0:
        raise ValueError(f"num_nodes must be a non-negative integer, got: {num_nodes}")

    for edge in edges:
        dist_val = edge["distance_meters"]
        if isinstance(dist_val, bool):
            raise ValueError(f"Invalid edge weight ({dist_val!r}). Distances must be non-negative finite numbers.")
        try:
            dist = float(dist_val)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid edge weight ({dist_val!r}). Distances must be non-negative finite numbers.") from exc
        if not math.isfinite(dist) or dist < 0:
            raise ValueError(f"Invalid edge weight ({dist}). Distances must be non-negative finite numbers.")

        u = edge["src_loc_id"]
        v = edge["dst_loc_id"]
        if (
            not isinstance(u, int)
            or isinstance(u, bool)
            or not isinstance(v, int)
            or isinstance(v, bool)
        ):
            raise ValueError(f"Edge endpoints must be integers, got: src={u}, dst={v}")
        if u < 1 or u > num_nodes or v < 1 or v > num_nodes:
            raise ValueError(f"Edge endpoint out of range [1, {num_nodes}]: src={u}, dst={v}")

    if num_nodes == 0 or not edges:
        return {"mst_edges": [], "total_cable_or_walk_meters": 0.0}

    sorted_edges = sorted(edges, key=lambda e: float(e["distance_meters"]))

    dsu = _DisjointSetUnion(range(1, num_nodes + 1))
    components = num_nodes
    mst_edges: List[Dict[str, Any]] = []
    total_weight: float = 0.0

    for edge in sorted_edges:
        u = edge["src_loc_id"]
        v = edge["dst_loc_id"]

        if u == v:
            continue

        if dsu.union(u, v):
            mst_edges.append(dict(edge))
            total_weight += float(edge["distance_meters"])
            components -= 1

            if components == 1:
                break

    return {
        "mst_edges": mst_edges,
        "total_cable_or_walk_meters": float(total_weight),
    }


@measure_daa(
    algorithm="Greedy Job Sequencing",
    unit="Unit II",
    complexity="O(n^2)",
    input_size_fn=lambda *args, **kwargs: len(args[0]) if args else len(kwargs.get("claims", [])),
)
def schedule_urgent_claims(claims: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not claims:
        return {"scheduled_claims": [], "total_priority_saved": 0}

    for claim in claims:
        p = claim.get("priority_value")
        if not isinstance(p, int) or isinstance(p, bool) or p < 0:
            raise ValueError(f"priority_value must be a non-negative integer, got: {p}")

        d = claim.get("deadline_hours")
        if not isinstance(d, int) or isinstance(d, bool):
            raise ValueError(f"deadline_hours must be an integer, got: {d}")

    # Skip claims with deadline_hours <= 0
    valid_claims = [c for c in claims if c["deadline_hours"] > 0]
    if not valid_claims:
        return {"scheduled_claims": [], "total_priority_saved": 0}

    # Sort descending by priority_value, then ascending by deadline_hours for deterministic tie-breaking
    sorted_claims = sorted(
        valid_claims,
        key=lambda c: (-c["priority_value"], c["deadline_hours"]),
    )

    n = len(claims)
    slots: Dict[int, Dict[str, Any]] = {}
    total_priority_saved = 0

    for claim in sorted_claims:
        max_slot = min(claim["deadline_hours"], n)
        for slot in range(max_slot, 0, -1):
            if slot not in slots:
                scheduled_item = dict(claim)
                scheduled_item["assigned_slot"] = slot
                slots[slot] = scheduled_item
                total_priority_saved += claim["priority_value"]
                break

    scheduled_claims = [slots[t] for t in range(1, n + 1) if t in slots]

    return {
        "scheduled_claims": scheduled_claims,
        "total_priority_saved": total_priority_saved,
    }


def _is_safe_color(node: int, color: int, color_map: Dict[int, int], adj: Dict[int, Set[int]]) -> bool:
    for neighbor in adj[node]:
        if color_map.get(neighbor) == color:
            return False
    return True


def _color_graph_backtracking(
    ordered_nodes: List[int],
    index: int,
    max_colors: int,
    color_map: Dict[int, int],
    adj: Dict[int, Set[int]],
) -> bool:
    if index == len(ordered_nodes):
        return True

    node = ordered_nodes[index]
    for color in range(1, max_colors + 1):
        if _is_safe_color(node, color, color_map, adj):
            color_map[node] = color
            if _color_graph_backtracking(ordered_nodes, index + 1, max_colors, color_map, adj):
                return True
            del color_map[node]

    return False


# Note on complexity:
# For a fixed m, testing m-colorability using backtracking has worst-case time complexity
# O(m^V) pruned by the safe-color neighborhood check.
# Finding the minimum chromatic number searches m sequentially from 1 to chi(G), taking
# sum_{k=1}^{chi(G)} O(k^V pruned) in aggregate.
@measure_daa(
    algorithm="Graph Coloring (Backtracking)",
    unit="Unit II",
    complexity="O(m^V) pruned",
    input_size_fn=lambda *args, **kwargs: len(args[0]) if args else len(kwargs.get("matches", [])),
)
def assign_conflict_free_slots(matches: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(matches, list):
        raise ValueError(f"matches must be a list, got {type(matches).__name__}")

    if not matches:
        return {"slot_assignments": {}, "chromatic_number": 0}

    seen_match_ids: Set[int] = set()
    for idx, m in enumerate(matches):
        if not isinstance(m, dict):
            raise ValueError(f"Match element at index {idx} must be a dictionary, got {type(m).__name__}")

        for field in ("match_id", "student_id", "admin_id"):
            if field not in m:
                raise ValueError(f"Match at index {idx} missing required field '{field}'")
            val = m[field]
            if not isinstance(val, int) or isinstance(val, bool) or val <= 0:
                raise ValueError(f"Match field '{field}' must be a positive integer, got {val!r}")

        match_id = m["match_id"]
        if match_id in seen_match_ids:
            raise ValueError(f"Duplicate match_id detected: {match_id}")
        seen_match_ids.add(match_id)

    # Build undirected conflict graph
    adj: Dict[int, Set[int]] = {m["match_id"]: set() for m in matches}
    n = len(matches)
    for i in range(n):
        m1 = matches[i]
        id1 = m1["match_id"]
        for j in range(i + 1, n):
            m2 = matches[j]
            id2 = m2["match_id"]
            if m1["student_id"] == m2["student_id"] or m1["admin_id"] == m2["admin_id"]:
                adj[id1].add(id2)
                adj[id2].add(id1)

    # Descending-degree vertex ordering for backtracking: color constrained vertices first.
    # Secondary sort by ascending match_id provides deterministic tie-breaking.
    ordered_nodes = sorted(adj.keys(), key=lambda node: (-len(adj[node]), node))

    for m in range(1, n + 1):
        color_map: Dict[int, int] = {}
        if _color_graph_backtracking(ordered_nodes, 0, m, color_map, adj):
            slot_assignments = {m_elem["match_id"]: color_map[m_elem["match_id"]] for m_elem in matches}
            return {
                "slot_assignments": slot_assignments,
                "chromatic_number": m,
            }

    return {"slot_assignments": {}, "chromatic_number": 0}
