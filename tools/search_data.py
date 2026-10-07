"""
Generic tool to search structured business data.
Provides a mock implementation using local JSON data files.
Can be swapped out for a real DB/API backend.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

# Path to the mock data directory relative to this file
MOCK_DATA_DIR = Path(__file__).parent.parent / "mock_data"

def search_data(
    source: str,
    filters: Optional[Dict[str, Any]] = None,
    fields: Optional[List[str]] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Search structured business data across different sources.

    Args:
        source: The name of the data source to query (e.g., 'orders', 'employees', 'products').
        filters: A dictionary of field-value pairs to filter by. Supports exact matches.
        fields: A list of field names to include in the returned records. If None, returns all fields.
        limit: The maximum number of records to return.

    Returns:
        A dictionary containing:
            - 'matches': List of matching records.
            - 'count': Number of matching records.
            - 'source': The queried data source.
            - 'metadata': Additional useful information (e.g., status, applied filters).

    Examples:
        >>> search_data(source="orders", filters={"order_id": "ORD-1001"})
        >>> search_data(source="employees", filters={"availability": "available"}, fields=["name", "role"])
    """
    filters = filters or {}
    
    # Resolve the data source (mock implementation)
    file_path = MOCK_DATA_DIR / f"{source}.json"
    
    if not file_path.exists():
        return {
            "matches": [],
            "count": 0,
            "source": source,
            "metadata": {
                "error": f"Unknown source: '{source}'. Data file not found.",
                "status": "error"
            }
        }
        
    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return {
            "matches": [],
            "count": 0,
            "source": source,
            "metadata": {
                "error": f"Malformed data in source '{source}': {str(e)}",
                "status": "error"
            }
        }
    except Exception as e:
         return {
            "matches": [],
            "count": 0,
            "source": source,
            "metadata": {
                "error": f"Error reading source '{source}': {str(e)}",
                "status": "error"
            }
        }
       
    if not isinstance(data, list):
        return {
            "matches": [],
            "count": 0,
            "source": source,
            "metadata": {
                "error": f"Malformed data in source '{source}': expected a list of records.",
                "status": "error"
            }
        }

    # Apply filters
    results = []
    for record in data:
        if not isinstance(record, dict):
            continue
        
        # Check all filters for exact match
        match = True
        for k, v in filters.items():
            if record.get(k) != v:
                match = False
                break
                
        if match:
            results.append(record)

    # Apply fields selection
    if fields:
        projected_results = []
        for record in results:
            projected = {k: v for k, v in record.items() if k in fields}
            projected_results.append(projected)
        results = projected_results

    # Apply limit
    if limit is not None and limit > 0:
        results = results[:limit]

    return {
        "matches": results,
        "count": len(results),
        "source": source,
        "metadata": {
            "status": "success",
            "applied_filters": filters,
            "limit": limit,
            "returned_fields": fields if fields else "all"
        }
    }
