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
