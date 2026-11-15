import functools
import time
from typing import Any, Callable, Dict, Optional

VALID_UNITS = {"Unit I", "Unit II", "Unit III", "Unit IV"}


def measure_daa(
    algorithm: str,
    unit: str,
    complexity: str,
    input_size_fn: Optional[Callable[..., int]] = None,
) -> Callable:
    if unit not in VALID_UNITS:
        raise ValueError(f"Invalid unit '{unit}'. Must be one of: {sorted(VALID_UNITS)}")

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Dict[str, Any]:
            if input_size_fn is not None:
                input_size = input_size_fn(*args, **kwargs)
            else:
                try:
                    input_size = len(args[0]) if args else 0
                except TypeError:
                    input_size = 0

            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            return {
                "result": result,
                "telemetry": {
                    "algorithm": algorithm,
                    "unit": unit,
                    "input_size": input_size,
                    "time_ms": round(elapsed_ms, 4),
                    "complexity": complexity,
                },
            }

        return wrapper

    return decorator
