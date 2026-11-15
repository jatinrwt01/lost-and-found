from typing import Any, Dict, List, Optional
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


def _partition(arr: List[Dict[str, Any]], low: int, high: int, key: str) -> int:
    pivot = arr[high][key]
    i = low - 1

    for j in range(low, high):
        if arr[j][key] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

        arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def _quick_sort_recursive(arr: List[Dict[str, Any]], low: int, high: int, key: str) -> None:
    if low < high:
        pi = _partition(arr, low, high, key)
        _quick_sort_recursive(arr, low, pi - 1, key)
        _quick_sort_recursive(arr, pi + 1, high, key)


def _quick_sort(items: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
    if len(items) <= 1:
        return list(items)

    arr = list(items)
    _quick_sort_recursive(arr, 0, len(arr) - 1, key)
    return arr


@measure_daa(
    algorithm="Merge Sort",
    unit="Unit I",
    complexity="O(n log n)",
    input_size_fn=lambda *args, **kwargs: len(args[0]) if args else len(kwargs.get("items", [])),
)
def _sort_items_merge(items: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
    return _merge_sort(items, key)


@measure_daa(
    algorithm="Quick Sort",
    unit="Unit I",
    complexity="O(n log n) average case",
    input_size_fn=lambda *args, **kwargs: len(args[0]) if args else len(kwargs.get("items", [])),
)
def _sort_items_quick(items: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
    return _quick_sort(items, key)


def sort_items(items: List[Dict[str, Any]], key: str, method: str = "merge") -> Dict[str, Any]:
    if method == "merge":
        return _sort_items_merge(items, key)
    if method == "quick":
        return _sort_items_quick(items, key)

    raise ValueError(f"Unsupported sorting method: '{method}'. Only 'merge' and 'quick' are supported.")


@measure_daa(
    algorithm="Binary Search",
    unit="Unit I",
    complexity="O(log n)",
    input_size_fn=lambda *args, **kwargs: len(args[0]) if args else len(kwargs.get("sorted_items", [])),
)
def binary_search_item_id(sorted_items: List[Dict[str, Any]], target_id: int) -> Dict[str, Any]:
    low = 0
    high = len(sorted_items) - 1

    while low <= high:
        mid = (low + high) // 2
        current_id = sorted_items[mid]["item_id"]

        if current_id == target_id:
            return sorted_items[mid]
        elif current_id < target_id:
            low = mid + 1
        else:
            high = mid - 1

    return None
