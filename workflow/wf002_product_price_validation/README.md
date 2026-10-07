# Product Price Validation Workflow (LangGraph)

## Overview
This LangGraph workflow validates product pricing data supplied by an internal system against a vendor’s price list. It:

1. **Loads** raw price records from configurable data sources.  
2. **Matches** products by SKU, separating matched and unmatched items.  
3. **Compares** internal and vendor prices, calculating the percentage difference and flagging any product whose price deviation exceeds a configurable threshold (default = 10 %).  
4. **Generates** a structured validation report that includes:
   - Summary statistics (total matched, flagged, passed, unmatched)  
   - Detailed results for each flagged/passed product  
   - Any errors encountered during execution  

The workflow is built with **LangGraph**’s `StateGraph` abstraction, allowing each step to be a pure function that receives and returns a typed state object (`WF002State`).  

---

## Data Flow

```
START → load_prices → match_products → compare_prices → generate_report → END
```

| Step | Input (state fields) | Processing | Output (state fields) |
|------|----------------------|------------|-----------------------|
| **load_prices** | `internal_prices_source`, `vendor_prices_source` | Reads JSON/CSV (via `tools.read_data.read_data`) and stores raw records. | `internal_records`, `vendor_records`, `execution_steps`, `errors` |
| **match_products** | `internal_records`, `vendor_records` | Builds SKU dictionaries, validates price values, creates `MatchedProduct` objects for items present in both sources, and records unmatched SKUs. | `matched_products`, `unmatched_products`, `execution_steps`, `errors` |
| **compare_prices** | `matched_products` | For each `MatchedProduct`, computes `percentage_difference` (via `tools.calculate.calculate`) and checks against a 10 % threshold. Produces `ValidationResult` objects with status **PASS** or **FLAG**. | `validation_results`, `execution_steps`, `errors` |
| **generate_report** | `validation_results`, `unmatched_products`, `errors` | Summarises the validation, separates flags/passes, and builds the final result payload. | `final_result`, `execution_steps` |

The state is passed immutably from node to node, accumulating `execution_steps` (human‑readable log) and `errors` (any exception or validation issue). The final payload (`final_result`) can be returned directly to a caller, stored, or sent downstream.

---

## Nodes Used

| Node | Function | Key Responsibilities |
|------|----------|-----------------------|
| **load_prices** | `load_prices(state: WF002State) -> WF002State` | • Reads internal and vendor price files.<br>• Populates `internal_records` and `vendor_records`.<br>• Logs step and captures I/O errors. |
| **match_products** | `match_products(state: WF002State) -> WF002State` | • Indexes records by SKU.<br>• Validates price fields (non‑negative, non‑zero).<br>• Creates `MatchedProduct` objects for SKU present in both sources.<br>• Records unmatched SKUs and any data‑quality errors. |
| **compare_prices** | `compare_prices(state: WF002State) -> WF002State` | • Calls `tools.calculate.calculate` to compute percentage difference.<br>• Uses a threshold comparison to decide **PASS** vs **FLAG**.<br>• Generates a list of `ValidationResult` objects. |
| **generate_report** | `generate_report(state: WF002State) -> WF002State` | • Aggregates results into a concise report dictionary.<br>• Separates flagged and passed items.<br>• Includes summary counts, unmatched SKUs, and any accumulated errors. |

All nodes are pure functions that **receive** a `WF002State` instance, **mutate** its fields, and **return** the same instance for the next step.

---

## Code Structure

```
product_price_validation/
│
├─ graph.py          # Workflow definition & compilation
├─ state.py          # Typed state model (inherits BaseWorkflowState)
├─ models.py         # Pydantic data models: MatchedProduct, ValidationResult
├─ nodes.py          # Implementations of the four workflow nodes
├─ tools/
│   ├─ __init__.py
│   ├─ read_data.py      # read_data(source) → {"records": [...]}
│   └─ calculate.py      # calculate(operation, **kwargs) → {"status": "...", "result": ...}
└─ workflow/
    └─ base.py           # BaseWorkflowState (provided by the project)
```

### `graph.py`
* Imports `StateGraph`, `START`, `END` from **LangGraph**.
* Imports the typed state (`WF002State`) and node functions.
* Registers each node with a unique name.
* Connects nodes with directed edges to form the linear pipeline.
* Returns a compiled graph ready to be executed (`workflow.compile()`).

### `state.py`
* Extends `BaseWorkflowState` (a generic dict‑like container with type hints).
* Declares all fields used throughout the workflow:
  - Sources (`internal_prices_source`, `vendor_prices_source`)
  - Raw records (`internal_records`, `vendor_records`)
  - Matching results (`matched_products`, `unmatched_products`)
  - Validation output (`validation_results`)
  - Execution metadata (`execution_steps`, `errors`, `final_result` – added dynamically)

### `models.py`
* **`MatchedProduct`** – Holds a SKU and the two price values that will be compared.
* **`ValidationResult`** – Holds the comparison outcome, including the computed percentage difference and a status flag (`PASS` / `FLAG`).

Both models inherit from **Pydantic** `BaseModel`, providing validation, serialization (`model_dump()`), and type safety.

### `nodes.py`
* Implements the four core functions referenced in `graph.py`.
* Uses helper utilities:
  - `tools.read_data.read_data` – abstracts file format handling (CSV, JSON, etc.).
  - `tools.calculate.calculate` – centralised math operations (`percentage_difference`, `threshold_comparison`).
* Each function updates the shared `WF002State`:
  - Appends human‑readable messages to `execution_steps`.
  - Appends any exception or data‑quality issue to `errors`.
  - Stores intermediate and final results in dedicated state fields.

### `tools/`
* **`read_data.py`** – Reads a file path or URL and returns a dict with a `records` list. (Implementation not shown; assumed to raise on I/O errors.)
* **`calculate.py`** – Provides reusable calculations:
  - `"percentage_difference"` → `abs((current - base) / base * 100)`
  - `"threshold_comparison"` → evaluates `value > threshold` (or other operators) and returns a boolean.
  - Returns a uniform response: `{"status": "success"|"error", "result": <value>, "message": <optional>}`.

### `workflow/base.py`
* Supplies `BaseWorkflowState`, a lightweight wrapper around a dict that supports attribute‑style access (`state["field"]` and `state.field`).

---

## Getting Started

```bash
# Install dependencies (LangGraph, Pydantic, etc.)
pip install langgraph pydantic

# Clone the repository (or copy the package into your project)
git clone https://github.com/your-org/product_price_validation.git
cd product_price_validation
```

### Running the workflow

```python
from product_price_validation.graph import create_product_price_validation_graph

# Prepare initial state
initial_state = {
    "internal_prices_source": "data/internal_prices.json",
    "vendor_prices_source": "data/vendor_prices.json",
    "execution_steps": [],
    "errors": []
}

# Build and execute
graph = create_product_price_validation_graph()
final_state = graph.invoke(initial_state)

# The report lives in final_state["final_result"]
print(final_state["final_result"])
```

*Replace the source paths with your actual data files.*  
The workflow will log each step in `execution_steps` and collect any problems in `errors`. The final report contains a concise summary and detailed lists of flagged, passed, and unmatched SKUs.

---

## Extending the Workflow

* **Threshold customization** – expose the threshold (currently `10.0`) as a state field (`price_deviation_threshold`) and pass it to `compare_prices`.
* **Additional checks** – add new nodes (e.g., currency conversion, historical price trend analysis) and insert them between existing edges.
* **Parallel processing** – replace the linear `StateGraph` with a `ConditionalGraph` or `ParallelGraph` if you need to run independent checks concurrently.

---

## License
This workflow is released under the MIT License. See `LICENSE` for details.