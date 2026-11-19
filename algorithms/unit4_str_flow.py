from typing import Any, Dict, List, Optional
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
