import heapq
import math
from typing import Any, Dict, List, Optional
from algorithms.metrics import measure_daa

UNREACHABLE_SENTINEL = -1.0


@measure_daa(
    algorithm="Dijkstra's Algorithm",
    unit="Unit II",
    complexity="O((V + E) log V)",
    input_size_fn=lambda *args, **kwargs: len(args[0]) if args else len(kwargs.get("edges", [])),
)
def shortest_campus_path(edges: List[Dict[str, Any]], start_loc: int, end_loc: int) -> Dict[str, Any]:
    adj: Dict[int, List[tuple[int, float]]] = {}
    for edge in edges:
        dist = float(edge["distance_meters"])
        if not math.isfinite(dist) or dist < 0:
            raise ValueError(f"Invalid edge weight ({dist}). Distances must be non-negative finite numbers.")

        u = edge["src_loc_id"]
        v = edge["dst_loc_id"]
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
        "total_meters": distances[end_loc]
    }
