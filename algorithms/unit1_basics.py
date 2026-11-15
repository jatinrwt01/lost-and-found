from typing import Any, Dict, List
from algorithms.metrics import measure_daa


def _merge(left: List[Dict[str, Any]], right: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
    merged = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i][key] <= right[j][key]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def _merge_sort(items: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
    if len(items) <= 1:
        return list(items)

    mid = len(items) // 2
    left = _merge_sort(items[:mid], key)
    right = _merge_sort(items[mid:], key)
    return _merge(left, right, key)


@measure_daa(
    algorithm="Merge Sort",
    unit="Unit I",
    complexity="O(n log n)",
    input_size_fn=lambda items, *args, **kwargs: len(items),
)
def sort_items(items: List[Dict[str, Any]], key: str, method: str = "merge") -> Dict[str, Any]:
    if method != "merge":
        raise ValueError(f"Unsupported sorting method: '{method}'. Only 'merge' is supported.")

    return _merge_sort(items, key)
