"""
General utility functions.
"""
import hashlib
import logging
from typing import Any, Dict, List, Optional
import json

logger = logging.getLogger(__name__)


def hash_data(data: Any) -> str:
    """
    Creates a SHA-256 hash of the input data (after converting it to JSON string).
    Useful for generating unique identifiers or checking data integrity.
    """
    json_string = json.dumps(data, sort_keys=True, default=str) # default=str handles non-serializable objects
    return hashlib.sha256(json_string.encode()).hexdigest()


def safe_get_nested_dict(d: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    """
    Safely gets a value from a nested dictionary using a list of keys.
    Returns default if any key in the chain is missing.
    """
    current = d
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def format_currency(amount: float, currency: str = None) -> str:
    """
    Formats a numerical amount into a currency string.
    This is a very basic example; consider using libraries like Babel for robust formatting.
    """
    # Note: This is a simplified formatter.
    # For advanced formatting (locales, symbols), use a library like babel.numbers.format_currency
    if currency is None:
        return f"{amount:,.2f} UNKNOWN_CURRENCY"

    if currency.upper() == "CNY":
        return f"\u00a5{amount:,.2f}"
    elif currency.upper() == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def chunks(lst: List[Any], n: int):
    """
    Yield successive n-sized chunks from lst.
    Useful for processing large lists in smaller batches.
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# Example usage of helpers:
# if __name__ == "__main__":
#     my_dict = {"level1": {"level2": {"level3": "found_it"}}}
#     result = safe_get_nested_dict(my_dict, ["level1", "level2", "level3"])
#     print(result) # Output: found_it
#     print(hash_data({"key": "value"}))