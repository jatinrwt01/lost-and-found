import math
from typing import Any, Dict, List, Optional, Union
from algorithms.metrics import measure_daa

SEARCHABLE_FIELDS = ("title", "category", "description", "serial_tag")


def _compute_lps(pattern: str) -> List[int]:
    m = len(pattern)
    lps = [0] * m
    length = 0
    i = 1

    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1

    return lps


def _kmp_search(text: str, pattern: str, lps: List[int]) -> bool:
    n = len(text)
    m = len(pattern)

    if m == 0:
        return True
    if n < m:
        return False

    i = 0  # index for text
    j = 0  # index for pattern

    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1
            if j == m:
                return True
        else:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1

    return False


def _extract_searchable_text(item: Dict[str, Any], idx: int) -> str:
    tokens = []
    for field in SEARCHABLE_FIELDS:
        if field not in item:
            continue
        val = item[field]
        if val is None:
            continue
        if isinstance(val, bool) or not isinstance(val, str):
            raise ValueError(
                f"Field '{field}' in item at index {idx} must be a string or None, got {val!r}"
            )
        if val:
            tokens.append(val)
    return " ".join(tokens)


def _kmp_input_size(*args: Any, **kwargs: Any) -> int:
    items = args[0] if len(args) >= 1 else kwargs.get("items", [])
    pattern = args[1] if len(args) >= 2 else kwargs.get("pattern", "")

    m = len(pattern) if isinstance(pattern, str) else 0
    if not isinstance(items, list):
        return m

    n = 0
    for idx, item in enumerate(items):
        if isinstance(item, dict):
            try:
                text = _extract_searchable_text(item, idx)
                n += len(text)
            except Exception:
                pass
    return n + m


@measure_daa(
    algorithm="Knuth-Morris-Pratt (KMP)",
    unit="Unit IV",
    complexity="O(n + m)",
    input_size_fn=_kmp_input_size,
)
def kmp_search_items(items: List[Dict[str, Any]], pattern: str) -> List[Dict[str, Any]]:
    if not isinstance(items, list):
        raise ValueError(f"items must be a list, got {type(items).__name__}")

    if not isinstance(pattern, str):
        raise ValueError(f"pattern must be a string, got {type(pattern).__name__}")

    extracted_texts: List[str] = []
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"Item at index {idx} must be a dictionary, got {type(item).__name__}")
        searchable_text = _extract_searchable_text(item, idx)
        extracted_texts.append(searchable_text)

    if len(pattern) == 0:
        return [dict(item) for item in items]

    norm_pattern = pattern.casefold()
    lps = _compute_lps(norm_pattern)

    matched_items: List[Dict[str, Any]] = []
    for idx, item in enumerate(items):
        norm_text = extracted_texts[idx].casefold()
        if _kmp_search(norm_text, norm_pattern, lps):
            matched_items.append(dict(item))

    return matched_items


RK_BASE = 257
RK_MODULUS = 1_000_000_007


def _hash_string(s: str, base: int = RK_BASE, modulus: int = RK_MODULUS) -> int:
    h = 0
    for char in s:
        h = (h * base + ord(char)) % modulus
    return h


def _verify_match(text: str, start_idx: int, pattern: str) -> bool:
    for k in range(len(pattern)):
        if text[start_idx + k] != pattern[k]:
            return False
    return True


def _rabin_karp_search(
    text: str,
    pattern: str,
    base: int = RK_BASE,
    modulus: int = RK_MODULUS,
) -> bool:
    n = len(text)
    m = len(pattern)

    if m == 0:
        return True
    if n < m:
        return False

    pattern_hash = _hash_string(pattern, base, modulus)
    window_hash = _hash_string(text[:m], base, modulus)
    h = pow(base, m - 1, modulus)

    for i in range(n - m + 1):
        if window_hash == pattern_hash:
            if _verify_match(text, i, pattern):
                return True

        if i < n - m:
            c_out = ord(text[i])
            c_in = ord(text[i + m])
            window_hash = ((window_hash - c_out * h) * base + c_in) % modulus
            if window_hash < 0:
                window_hash += modulus

    return False


def _rk_input_size(*args: Any, **kwargs: Any) -> int:
    text = args[0] if len(args) >= 1 else kwargs.get("text", "")
    watchlist = args[1] if len(args) >= 2 else kwargs.get("watchlist", [])

    n = len(text) if isinstance(text, str) else 0
    if not isinstance(watchlist, list):
        return n

    p_total = 0
    for p in watchlist:
        if isinstance(p, str) and not isinstance(p, bool):
            p_total += len(p)

    return n + p_total


@measure_daa(
    algorithm="Rabin-Karp",
    unit="Unit IV",
    complexity="O(n * P) worst case, O(n * d + P) average",
    input_size_fn=_rk_input_size,
)
def rabin_karp_watchlist_scan(text: str, watchlist: List[str]) -> Dict[str, Any]:
    if not isinstance(text, str):
        raise ValueError(f"text must be a string, got {type(text).__name__}")

    if not isinstance(watchlist, list):
        raise ValueError(f"watchlist must be a list, got {type(watchlist).__name__}")

    for idx, pattern in enumerate(watchlist):
        if isinstance(pattern, bool) or not isinstance(pattern, str):
            raise ValueError(
                f"Watchlist pattern at index {idx} must be a string, got {pattern!r}"
            )

    unique_patterns: List[str] = []
    seen_norm: set = set()
    for p in watchlist:
        norm_p = p.casefold()
        if norm_p not in seen_norm:
            seen_norm.add(norm_p)
            unique_patterns.append(p)

    matched_norm_set: set = set()
    norm_text = text.casefold()
    n = len(norm_text)

    for p in unique_patterns:
        norm_p = p.casefold()
        if len(norm_p) == 0:
            matched_norm_set.add(norm_p)

    by_length: Dict[int, Dict[int, List[str]]] = {}
    for p in unique_patterns:
        norm_p = p.casefold()
        m = len(norm_p)
        if m == 0 or m > n:
            continue
        p_hash = _hash_string(norm_p)
        by_length.setdefault(m, {}).setdefault(p_hash, []).append(norm_p)

    for m, hash_map in by_length.items():
        if not hash_map:
            continue

        h = pow(RK_BASE, m - 1, RK_MODULUS)
        window_hash = _hash_string(norm_text[:m])

        for i in range(n - m + 1):
            if window_hash in hash_map:
                candidates = hash_map[window_hash]
                for cand in list(candidates):
                    if cand not in matched_norm_set and _verify_match(norm_text, i, cand):
                        matched_norm_set.add(cand)
                        candidates.remove(cand)
                if not candidates:
                    del hash_map[window_hash]
                    if not hash_map:
                        break

            if i < n - m:
                c_out = ord(norm_text[i])
                c_in = ord(norm_text[i + m])
                window_hash = ((window_hash - c_out * h) * RK_BASE + c_in) % RK_MODULUS
                if window_hash < 0:
                    window_hash += RK_MODULUS

    matched_patterns = [p for p in unique_patterns if p.casefold() in matched_norm_set]
    flagged = len(matched_patterns) > 0

    return {
        "flagged": flagged,
        "matched_patterns": matched_patterns,
    }


def _extract_partition_id(
    item: Dict[str, Any],
    idx: int,
    partition_name: str,
    specific_key: str,
) -> int:
    if not isinstance(item, dict):
        raise ValueError(
            f"{partition_name} at index {idx} must be a dictionary, got {type(item).__name__}"
        )

    has_specific = specific_key in item
    has_item_id = "item_id" in item

    if not has_specific and not has_item_id:
        raise ValueError(
            f"{partition_name} at index {idx} missing required ID key ('{specific_key}' or 'item_id')"
        )

    if has_specific and has_item_id:
        val_spec = item[specific_key]
        val_id = item["item_id"]
        if val_spec != val_id:
            raise ValueError(
                f"{partition_name} at index {idx} has conflicting IDs: '{specific_key}'={val_spec!r} vs 'item_id'={val_id!r}"
            )
        resolved_id = val_spec
    elif has_specific:
        resolved_id = item[specific_key]
    else:
        resolved_id = item["item_id"]

    if isinstance(resolved_id, bool) or not isinstance(resolved_id, int):
        raise ValueError(
            f"{partition_name} at index {idx} has non-integer ID: {resolved_id!r}"
        )

    if resolved_id <= 0:
        raise ValueError(
            f"{partition_name} at index {idx} has non-positive ID: {resolved_id}"
        )

    return resolved_id


class _FlowEdge:
    __slots__ = ("u", "v", "cap", "cost", "score", "rev")

    def __init__(self, u: Any, v: Any, cap: int, cost: float, score: float = 0.0) -> None:
        self.u = u
        self.v = v
        self.cap = cap
        self.cost = cost
        self.score = score
        self.rev: Optional["_FlowEdge"] = None


def _add_flow_edge(
    adj: Dict[Any, List[_FlowEdge]],
    u: Any,
    v: Any,
    cap: int,
    cost: float,
    score: float = 0.0,
) -> None:
    e1 = _FlowEdge(u, v, cap, cost, score)
    e2 = _FlowEdge(v, u, 0, -cost, score)
    e1.rev = e2
    e2.rev = e1
    adj[u].append(e1)
    adj[v].append(e2)


def _bipartite_input_size(*args: Any, **kwargs: Any) -> int:
    lost = args[0] if len(args) >= 1 else kwargs.get("lost_items", [])
    found = args[1] if len(args) >= 2 else kwargs.get("found_items", [])
    sm = args[2] if len(args) >= 3 else kwargs.get("score_matrix", {})

    size_l = len(lost) if isinstance(lost, list) else 0
    size_f = len(found) if isinstance(found, list) else 0

    edge_count = 0
    if isinstance(sm, dict):
        for _k, inner in sm.items():
            if isinstance(inner, dict):
                for _fk, s in inner.items():
                    if isinstance(s, (int, float)) and not isinstance(s, bool):
                        if math.isfinite(s) and s > 0.0:
                            edge_count += 1

    return size_l + size_f + edge_count


@measure_daa(
    algorithm="Global Bipartite Matching",
    unit="Unit IV",
    complexity="O(K * V * E)",
    input_size_fn=_bipartite_input_size,
)
def global_bipartite_match(
    lost_items: List[Dict[str, Any]],
    found_items: List[Dict[str, Any]],
    score_matrix: Dict[Any, Any],
) -> Dict[str, Any]:
    if not isinstance(lost_items, list):
        raise ValueError(f"lost_items must be a list, got {type(lost_items).__name__}")

    if not isinstance(found_items, list):
        raise ValueError(f"found_items must be a list, got {type(found_items).__name__}")

    if not isinstance(score_matrix, dict):
        raise ValueError(f"score_matrix must be a dictionary, got {type(score_matrix).__name__}")

    seen_lost = set()
    for idx, item in enumerate(lost_items):
        lid = _extract_partition_id(item, idx, "lost_item", "lost_id")
        if lid in seen_lost:
            raise ValueError(f"Duplicate lost item ID {lid} found at index {idx}")
        seen_lost.add(lid)

    seen_found = set()
    for idx, item in enumerate(found_items):
        fid = _extract_partition_id(item, idx, "found_item", "found_id")
        if fid in seen_found:
            raise ValueError(f"Duplicate found item ID {fid} found at index {idx}")
        seen_found.add(fid)

    valid_candidate_edges: List[Tuple[int, int, float]] = []
    for lost_k, inner_dict in score_matrix.items():
        if isinstance(lost_k, bool) or not isinstance(lost_k, int):
            raise ValueError(f"score_matrix outer key must be an integer, got {lost_k!r}")
        if lost_k not in seen_lost:
            raise ValueError(f"score_matrix contains lost_id {lost_k} not present in lost_items")
        if not isinstance(inner_dict, dict):
            raise ValueError(f"score_matrix[{lost_k}] must be a dictionary, got {type(inner_dict).__name__}")

        for found_k, score_val in inner_dict.items():
            if isinstance(found_k, bool) or not isinstance(found_k, int):
                raise ValueError(f"score_matrix[{lost_k}] inner key must be an integer, got {found_k!r}")
            if found_k not in seen_found:
                raise ValueError(f"score_matrix[{lost_k}] contains found_id {found_k} not present in found_items")

            if isinstance(score_val, bool) or not isinstance(score_val, (int, float)):
                raise ValueError(
                    f"Score for pair ({lost_k}, {found_k}) must be numeric, got {score_val!r}"
                )

            score_flt = float(score_val)
            if not math.isfinite(score_flt):
                raise ValueError(
                    f"Score for pair ({lost_k}, {found_k}) must be finite, got {score_flt}"
                )

            if score_flt > 0.0:
                valid_candidate_edges.append((lost_k, found_k, score_flt))

    sorted_lost = sorted(seen_lost)
    sorted_found = sorted(seen_found)

    if not sorted_lost or not sorted_found or not valid_candidate_edges:
        return {"pairs": [], "max_matches": 0}

    S = ("source", 0)
    T = ("sink", 0)
    all_nodes = [S] + [("lost", uid) for uid in sorted_lost] + [("found", vid) for vid in sorted_found] + [T]
    adj: Dict[Any, List[_FlowEdge]] = {node: [] for node in all_nodes}

    for uid in sorted_lost:
        _add_flow_edge(adj, S, ("lost", uid), cap=1, cost=0.0)

    for vid in sorted_found:
        _add_flow_edge(adj, ("found", vid), T, cap=1, cost=0.0)

    sorted_candidates = sorted(valid_candidate_edges, key=lambda x: (x[0], x[1]))
    for uid, vid, s in sorted_candidates:
        _add_flow_edge(adj, ("lost", uid), ("found", vid), cap=1, cost=-s, score=s)

    K = min(len(sorted_lost), len(sorted_found))
    num_nodes = len(all_nodes)

    for _ in range(K):
        dist: Dict[Any, float] = {node: float("inf") for node in all_nodes}
        dist[S] = 0.0
        parent_edge: Dict[Any, Optional[_FlowEdge]] = {node: None for node in all_nodes}

        for _step in range(num_nodes - 1):
            updated = False
            for node in all_nodes:
                d_u = dist[node]
                if d_u == float("inf"):
                    continue
                for edge in adj[node]:
                    if edge.cap > 0:
                        cand_dist = d_u + edge.cost
                        if cand_dist < dist[edge.v]:
                            dist[edge.v] = cand_dist
                            parent_edge[edge.v] = edge
                            updated = True
            if not updated:
                break

        if dist[T] == float("inf") or dist[T] >= 0.0:
            break

        curr = T
        while curr != S:
            p_edge = parent_edge[curr]
            p_edge.cap -= 1
            p_edge.rev.cap += 1
            curr = p_edge.u

    pairs: List[Dict[str, Any]] = []
    for uid in sorted_lost:
        lost_node = ("lost", uid)
        for edge in adj[lost_node]:
            if edge.v[0] == "found" and edge.cap == 0 and edge.score > 0.0:
                pairs.append({
                    "lost_id": uid,
                    "found_id": edge.v[1],
                    "score": edge.score,
                })
                break

    pairs.sort(key=lambda p: p["lost_id"])

    return {
        "pairs": pairs,
        "max_matches": len(pairs),
    }


class _BitonicItem:
    __slots__ = ("is_real", "score", "original_index", "payload")

    def __init__(self, is_real: bool, score: Union[int, float], original_index: int, payload: Dict[str, Any]):
        self.is_real = is_real
        self.score = score
        self.original_index = original_index
        self.payload = payload

    def canonical_key(self) -> tuple:
        # Real items rank higher than dummies (1 vs 0).
        # Tied scores rank higher for smaller original indices (-idx).
        return (1 if self.is_real else 0, self.score, -self.original_index)


def _is_less_canonical(a: _BitonicItem, b: _BitonicItem) -> bool:
    return a.canonical_key() < b.canonical_key()


def _bitonic_merge(arr: List[_BitonicItem], low: int, cnt: int, dir_up: bool) -> None:
    if cnt <= 1:
        return
    k = cnt // 2
    for i in range(low, low + k):
        j = i + k
        # Ascending swaps if arr[j] < arr[i]; descending reverses to swap if arr[i] < arr[j].
        should_swap = (
            _is_less_canonical(arr[j], arr[i])
            if dir_up
            else _is_less_canonical(arr[i], arr[j])
        )
        if should_swap:
            arr[i], arr[j] = arr[j], arr[i]
    _bitonic_merge(arr, low, k, dir_up)
    _bitonic_merge(arr, low + k, k, dir_up)


def _bitonic_sort(arr: List[_BitonicItem], low: int, cnt: int, dir_up: bool) -> None:
    if cnt <= 1:
        return
    k = cnt // 2
    _bitonic_sort(arr, low, k, True)
    _bitonic_sort(arr, low + k, k, False)
    _bitonic_merge(arr, low, cnt, dir_up)


@measure_daa(
    algorithm="Bitonic Sort",
    unit="Unit IV",
    complexity="O(n log^2 n)",
    input_size_fn=lambda candidates, *args, **kwargs: len(candidates) if isinstance(candidates, list) else 0,
)
def bitonic_sort_scores(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(candidates, list):
        raise ValueError(f"candidates must be a list, got {type(candidates).__name__}")

    n = len(candidates)
    if n == 0:
        return {"sorted_candidates": []}

    items: List[_BitonicItem] = []
    for idx, cand in enumerate(candidates):
        if not isinstance(cand, dict):
            raise ValueError(f"Candidate at index {idx} must be a dict, got {type(cand).__name__}")
        if "score" not in cand:
            raise ValueError(f"Candidate at index {idx} missing required 'score' field")

        score = cand["score"]
        if isinstance(score, bool):
            raise ValueError(f"Candidate at index {idx} score must not be a boolean")
        if not isinstance(score, (int, float)):
            raise ValueError(f"Candidate at index {idx} score must be numeric, got {type(score).__name__}")
        if isinstance(score, float) and (math.isnan(score) or math.isinf(score)):
            raise ValueError(f"Candidate at index {idx} score must be a finite number")

        items.append(_BitonicItem(True, score, idx, dict(cand)))

    # Pad up to next power of 2
    p = 1 if n == 1 else 1 << (n - 1).bit_length()
    for d in range(p - n):
        dummy_dict = {"pad": True, "score": None}
        items.append(_BitonicItem(False, 0, d, dummy_dict))

    _bitonic_sort(items, 0, p, False)

    return {"sorted_candidates": [item.payload for item in items]}

