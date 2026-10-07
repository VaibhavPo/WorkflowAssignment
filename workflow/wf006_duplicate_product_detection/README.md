# Duplicate Detection Workflow (WF006)

## Overview
This LangGraph workflow loads a product catalog, scans the records for duplicate items, groups them, and produces a structured result summarizing the findings.  
It is designed to:

1. **Ingest** a catalog from any source supported by the `read_data` utility.  
2. **Detect** duplicate products using two strategies:  
   - **Definite duplicates** – exact SKU matches.  
   - **Possible duplicates** – high textual similarity (≥ 0.85) between product name + category strings.  
3. **Emit** a JSON‑compatible result that includes:
   - All duplicate groups (with confidence scores and reasons).  
   - A summary (total products, counts of definite/possible duplicates).  
   - Execution steps and any errors that occurred.

The workflow is built with **LangGraph** and follows a simple linear graph: `START → load_catalog → detect_duplicates → generate_result → END`.

---

## Data Flow

| Step | Input (state) | Processing | Output (state) |
|------|---------------|------------|----------------|
| **START** | Empty or pre‑populated `WF006State` (e.g., `catalog_source`) | – | – |
| **load_catalog** | `catalog_source` (path/URL) | Calls `tools.read_data.read_data` to fetch the raw catalog and stores the list of records under `catalog_records`. Updates `execution_steps` and `errors` if needed. | `catalog_records`, `execution_steps`, `errors` |
| **detect_duplicates** | `catalog_records` | Iterates over records, builds groups using a visited‑set algorithm. Uses `tools.text_similarity.calculate_similarity` for attribute similarity. Emits a list of `DuplicateGroup` objects under `duplicate_groups`. Updates `execution_steps`. | `duplicate_groups`, `execution_steps` |
| **generate_result** | `duplicate_groups`, `catalog_records`, `errors` | Summarizes counts, formats each `DuplicateGroup` via `model_dump()`, and creates a final result dictionary (`final_result`). Updates `execution_steps`. | `final_result`, `execution_steps` |
| **END** | – | – | Workflow terminates; the caller can read `state["final_result"]`. |

The state object (`WF006State`) is passed **by reference** between nodes, so each node mutates the same state instance, preserving the cumulative execution log.

---

## Nodes Used

| Node | Function | Key Responsibilities |
|------|----------|----------------------|
| `load_catalog` | `nodes.load_catalog` | • Reads the catalog from `catalog_source`. <br>• Stores raw records in `catalog_records`. <br>• Logs success/failure in `execution_steps` and `errors`. |
| `detect_duplicates` | `nodes.detect_duplicates` | • Scans `catalog_records` for duplicate groups. <br>• Determines duplicate type (`definite_duplicate` or `possible_duplicate`). <br>• Calculates confidence (1.0 for exact SKU, similarity score for attribute match). <br>• Populates `duplicate_groups` with `DuplicateGroup` Pydantic models. |
| `generate_result` | `nodes.generate_result` | • Aggregates statistics (total products, counts per duplicate type). <br>• Serialises `DuplicateGroup` objects to plain dicts. <br>• Packages everything into `final_result` (status, groups, summary, errors). |

All nodes accept a single argument – the workflow state (`WF006State`) – and return the mutated state.

---

## Code Structure

```
workflow/
├── graph.py          # Definition & compilation of the LangGraph workflow
├── state.py          # Pydantic‑based state class (WF006State)
├── nodes.py          # Implementations of the three workflow nodes
├── models.py         # Pydantic model for a duplicate group
└── tools/
    ├── read_data.py          # Utility to load catalog data (CSV, JSON, etc.)
    └── text_similarity.py    # Wrapper around a similarity algorithm (e.g., cosine, Levenshtein)
```

### `graph.py`
* Imports `StateGraph`, `START`, `END` from LangGraph.
* Imports the custom state (`WF006State`) and node functions.
* Creates a `StateGraph` instance, registers the three nodes, wires them together, and returns a compiled graph via `create_duplicate_detection_graph()`.

### `state.py`
* Extends `BaseWorkflowState` (assumed to provide dict‑like behavior).
* Declares typed fields used throughout the workflow:
  - `catalog_source: str`
  - `catalog_records: List[Any]`
  - `duplicate_groups: List[Any]`
* Additional dynamic keys (`execution_steps`, `errors`, `final_result`) are added at runtime by the nodes.

### `nodes.py`
* **`load_catalog`** – Reads data, populates `catalog_records`, and records step status.
* **`detect_duplicates`** – Core duplicate‑detection algorithm:
  - Uses a visited‑set to avoid re‑processing records.
  - Checks exact SKU equality → definite duplicate.
  - Otherwise builds a combined attribute string (`product_name + category`) and computes similarity via `calculate_similarity`. If similarity > 0.85 → possible duplicate.
  - Constructs `DuplicateGroup` objects with product identifiers, type, confidence, and reason.
* **`generate_result`** – Summarises findings, serialises groups, and stores the final output.

### `models.py`
* Defines `DuplicateGroup` (a Pydantic model) with fields:
  - `products: List[str]`
  - `duplicate_type: str` (`definite_duplicate` or `possible_duplicate`)
  - `confidence: float`
  - `reason: str`

### `tools/`
* **`read_data.py`** – Abstracts file/URL reading; returns a dict with a `records` key.
* **`text_similarity.py`** – Provides `calculate_similarity(str1, str2)` returning a float in `[0, 1]`.

---

## Getting Started

```bash
# Install dependencies (LangGraph, Pydantic, any similarity libs)
pip install langgraph pydantic

# Run the workflow
python -c "
from workflow.graph import create_duplicate_detection_graph
from workflow.state import WF006State

state = WF006State(catalog_source='data/catalog.json')
graph = create_duplicate_detection_graph()
result_state = graph.invoke(state)
print(result_state['final_result'])
"
```

Replace `catalog_source` with the path or URL of your product catalog. The printed JSON will contain the duplicate groups and summary.