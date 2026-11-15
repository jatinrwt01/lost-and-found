import heapq
import math
from typing import Any, Dict, Iterable, List, Optional
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

    if num_nodes == 0:
        return {"mst_edges": [], "total_cable_or_walk_meters": 0.0}

    for edge in edges:
        dist = float(edge["distance_meters"])
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

    if not edges:
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
