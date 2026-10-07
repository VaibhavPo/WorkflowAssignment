"""
Reusable column normalization and alias-resolution tool.

Purpose:
    Convert inconsistent CSV/XLSX column headers into canonical
    column names used by workflows.

Example:
    "SKU"              -> "sku"
    "Vendor SKU"       -> "sku"
    "Product SKU"      -> "sku"
    "Product Name"     -> "product_name"
    "Item Name"        -> "product_name"

This tool is deterministic. It does not use an LLM.
"""

import re
from typing import Dict, List, Tuple


# -------------------------------------------------------------------
# Canonical field definitions
# -------------------------------------------------------------------

COLUMN_ALIASES: Dict[str, List[str]] = {
    "sku": [
        "sku",
        "vendor sku",
        "product sku",
        "item sku",
        "product code",
        "item code",
        "stock keeping unit",
    ],

    "product_name": [
        "product name",
        "product",
        "item name",
        "item",
        "name",
        "product title",
        "item title",
    ],

    "category": [
        "category",
        "product category",
        "item category",
        "type",
    ],

    "price": [
        "price",
        "product price",
        "selling price",
        "unit price",
        "internal price",
    ],

    "vendor_price": [
        "vendor price",
        "supplier price",
        "supplier unit price",
        "vendor unit price",
    ],

    "current_stock": [
        "current stock",
        "stock",
        "inventory",
        "inventory stock",
        "available stock",
        "quantity in stock",
        "qty in stock",
    ],

    "minimum_stock": [
        "minimum stock",
        "min stock",
        "minimum quantity",
        "min quantity",
        "reorder level",
        "reorder point",
    ],

    "keyword": [
        "keyword",
        "search keyword",
        "search term",
        "query",
        "keyword phrase",
    ],
    
    "workflow_id": [
        "workflow id",
        "workflow",
        "wf id",
    ],
    
    "execution_status": [
        "execution status",
        "status",
        "result",
    ],
    
    "execution_time": [
        "execution time",
        "duration",
        "time ms",
        "time",
    ],
    
    "error_message": [
        "error message",
        "error",
        "error info",
    ],
    
    "step_name": [
        "step name",
        "step",
    ],
}


# -------------------------------------------------------------------
# Header normalization
# -------------------------------------------------------------------

def normalize_header(header: str) -> str:
    """
    Normalize formatting differences in a column header.

    Examples:
        " Vendor SKU "       -> "vendor_sku"
        "PRODUCT NAME"       -> "product_name"
        "Product-Name"       -> "product_name"
        "product   name"    -> "product_name"
    """

    if header is None:
        return ""

    value = str(header).strip().lower()

    # Replace &, -, / etc. with spaces
    value = re.sub(r"[^a-z0-9]+", " ", value)

    # Collapse multiple spaces
    value = re.sub(r"\s+", " ", value)

    return value.strip()


# -------------------------------------------------------------------
# Build normalized alias lookup
# -------------------------------------------------------------------

def _build_alias_lookup() -> Dict[str, str]:
    lookup = {}

    for canonical_name, aliases in COLUMN_ALIASES.items():

        # Canonical name itself is also a valid alias
        lookup[normalize_header(canonical_name)] = canonical_name

        for alias in aliases:
            lookup[normalize_header(alias)] = canonical_name

    return lookup


ALIAS_LOOKUP = _build_alias_lookup()


# -------------------------------------------------------------------
# Resolve one header
# -------------------------------------------------------------------

def resolve_column_name(header: str) -> str:
    """
    Convert a raw column header into its canonical name.

    If the header is not known, return the normalized header rather
    than guessing its meaning.
    """

    normalized = normalize_header(header)

    if normalized in ALIAS_LOOKUP:
        return ALIAS_LOOKUP[normalized]

    # Unknown column:
    # preserve it in normalized form instead of inventing a mapping.
    return normalized.replace(" ", "_")


# -------------------------------------------------------------------
# Resolve all columns
# -------------------------------------------------------------------

def normalize_columns(
    columns: List[str],
) -> Tuple[Dict[str, str], List[str]]:
    """
    Resolve all input columns.

    Returns:
        column_mapping:
            {
                "Vendor SKU": "sku",
                "Product Name": "product_name"
            }

        unresolved_columns:
            Columns for which no known alias exists.
    """

    mapping = {}
    unresolved = []

    for column in columns:

        canonical = resolve_column_name(column)

        mapping[column] = canonical

        normalized_original = normalize_header(column)

        if normalized_original not in ALIAS_LOOKUP:
            unresolved.append(column)

    return mapping, unresolved


# -------------------------------------------------------------------
# Apply mapping to a dataset
# -------------------------------------------------------------------

def apply_column_mapping(dataframe):
    """
    Rename dataframe columns using the shared canonical mapping.

    Returns:
        renamed_dataframe
        mapping
        unresolved_columns
    """

    original_columns = list(dataframe.columns)

    mapping, unresolved = normalize_columns(original_columns)

    renamed_dataframe = dataframe.rename(columns=mapping)

    return renamed_dataframe, mapping, unresolved


# -------------------------------------------------------------------
# Required-column validation
# -------------------------------------------------------------------

def validate_required_columns(
    dataframe,
    required_columns: List[str],
) -> List[str]:
    """
    Check whether required canonical columns exist.

    Example:
        required_columns = ["sku", "product_name"]
    """

    missing = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    return missing
