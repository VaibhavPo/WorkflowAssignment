# Vendor File Processing Workflow (LangGraph)

## Overview
This LangGraph workflow reads a vendor‑provided data file, validates its contents against a simple schema, and produces a final result that includes:

* A cleaned dataset containing only the valid rows.  
* A summary of the validation (counts of valid/invalid rows).  
* A detailed report of any invalid rows.  
* An error log and execution trace.

The workflow is defined as a **state‑driven directed graph** using LangGraph’s `StateGraph`. Each node receives the shared workflow state, performs its task, updates the state, and passes it to the next node.

---

## Data Flow
```
START → read_vendor_file → validate_vendor_data → generate_result → END
```

| Step | Input (state fields) | Operation | Output (state updates) |
|------|----------------------|-----------|------------------------|
| **read_vendor_file** | `vendor_file_source` (path/URL) | Calls `tools.read_data.read_data` to load raw records. | `raw_records`, `execution_steps`, `errors` |
| **validate_vendor_data** | `raw_records` | Runs `tools.validate_data.validate_data` against a schema requiring `sku` and `product_name`. | `valid_rows`, `invalid_rows`, `validation_summary`, `invalid_row_report`, `execution_steps`, `errors` |
| **generate_result** | `valid_rows`, `validation_summary`, `invalid_row_report`, `errors` | Packages everything into a final result dictionary. | `final_result`, `execution_steps` |

The **state object** (`WF003State`) travels unchanged between nodes, accumulating logs, errors, and intermediate data. When the graph reaches `END`, the caller can retrieve `state["final_result"]`.

---

## Nodes Used
| Node | Function | Purpose |
|------|----------|---------|
| `read_vendor_file` | `nodes.read_vendor_file(state: WF003State) -> WF003State` | Reads the vendor file from the location specified in `vendor_file_source`. Stores raw records and logs success/failure. |
| `validate_vendor_data` | `nodes.validate_vendor_data(state: WF003State) -> WF003State` | Validates each raw record against a minimal schema (`sku` and `product_name` must be non‑empty). Separates valid/invalid rows, creates a summary, and records any validation errors. |
| `generate_result` | `nodes.generate_result(state: WF003State) -> WF003State` | Synthesizes the final output, marking the overall status, attaching the cleaned dataset, validation details, and any accumulated errors. |

All nodes are **pure functions** that accept the workflow state, mutate it, and return it, enabling deterministic execution and easy testing.

---

## Code Structure

```
/your_project/
│
├─ workflow/
│   ├─ base.py                # (provided by LangGraph) BaseWorkflowState definition
│   └─ vendor_processing/
│       ├─ __init__.py
│       ├─ graph.py           # Builds and compiles the StateGraph
│       ├─ nodes.py           # Node implementations (read, validate, generate)
│       └─ state.py           # WF003State dataclass extending BaseWorkflowState
│
├─ tools/
│   ├─ read_data.py          # read_data(source) → {"records": [...]}
│   └─ validate_data.py      # validate_data(records, schema) → ValidationResult
│
└─ README.md                 # ← This file
```

### `graph.py`
* Imports `StateGraph`, `START`, `END` from LangGraph.
* Imports the custom state class (`WF003State`) and node functions.
* **`create_vendor_file_processing_graph()`**:
  * Instantiates a `StateGraph` with `WF003State`.
  * Registers the three nodes.
  * Connects them in linear order (START → … → END).
  * Returns the compiled graph ready for execution (`graph = create_vendor_file_processing_graph()`).

### `nodes.py`
Contains the three node functions:

1. **`read_vendor_file`**
   * Retrieves `vendor_file_source` from the state.
   * Calls `tools.read_data.read_data`.
   * Populates `raw_records`, updates `execution_steps`, and records any exception in `errors`.

2. **`validate_vendor_data`**
   * Checks for the presence of records; logs an error if none.
   * Defines a simple schema (`sku`, `product_name` required, non‑empty).
   * Calls `tools.validate_data.validate_data`.
   * Stores `valid_rows`, `invalid_rows`, `validation_summary`, `invalid_row_report`.
   * Updates logs and error list.

3. **`generate_result`**
   * Builds a result dictionary with:
     * `status` (`success` or `completed_with_errors`),
     * `cleaned_dataset`,
     * `validation_summary`,
     * `invalid_row_report`,
     * `errors`.
   * Saves it under `final_result` and records the step.

### `state.py`
Defines the **workflow state model**:

```python
class WF003State(BaseWorkflowState):
    vendor_file_source: str
    raw_records: List[Dict[str, Any]]
    valid_rows: List[Dict[str, Any]]
    invalid_rows: List[Dict[str, Any]]
    validation_summary: Dict[str, int]
    invalid_row_report: List[Dict[str, Any]]
```

* Inherits from `BaseWorkflowState`, which provides dictionary‑like access (`state["key"]`) and type‑checking.
* Declares all fields that nodes may read or write, giving static‑type tools (mypy, IDEs) full visibility.

---

## Getting Started

```python
from workflow.vendor_processing.graph import create_vendor_file_processing_graph

# Build the graph
graph = create_vendor_file_processing_graph()

# Prepare initial state
initial_state = {
    "vendor_file_source": "data/vendor_2024_10.csv",
    "execution_steps": [],
    "errors": []
}

# Run the workflow
final_state = graph.invoke(initial_state)

# Access the result
result = final_state["final_result"]
print(result)
```

The `result` dictionary will contain the cleaned dataset, validation summary, any invalid‑row details, and a list of errors (if any).

---

## Extending the Workflow

* **Add preprocessing** – Insert a new node between `read_vendor_file` and `validate_vendor_data` for transformations (e.g., trimming whitespace).
* **Enrich validation** – Expand the schema in `validate_vendor_data` or plug in a more sophisticated validator.
* **Persist results** – Add a node after `generate_result` that writes `final_result` to a database or file system.

Because the graph is declarative, you only need to add the node function, register it with `workflow.add_node`, and adjust the edges accordingly. The state model can be extended by adding new attributes to `WF003State`.