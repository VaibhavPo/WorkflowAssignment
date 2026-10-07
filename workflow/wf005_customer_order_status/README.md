# WF005 – Order Status Retrieval Workflow

## Overview
This LangGraph workflow implements a simple **order‑status lookup** service.  
Given either an `order_id` or a `customer_email` (or both), it:

1. Validates that an identifier is present.  
2. Queries a SQLite `orders` table for the matching order.  
3. If an order is found, queries the `shipments` table for the related shipment.  
4. Builds a human‑readable status summary (or aggregates any errors).  
5. Returns a structured result object containing the order, shipment, summary, and any errors.

The workflow is built with **LangGraph**’s `StateGraph` abstraction, allowing each step to be a pure function that receives and returns a typed state object (`WF005State`).

---

## Data Flow
```
START → validate_identifier → search_order → search_shipment → summarize_status → generate_result → END
```

| Step | Input (state fields) | Processing | Output (state fields) |
|------|----------------------|------------|-----------------------|
| **validate_identifier** | `order_id`, `customer_email` | Checks that at least one identifier is supplied. | Adds `execution_steps` entry, populates `errors` if missing. |
| **search_order** | `order_id`, `customer_email`, `errors` | If no prior errors, builds a SQL query and calls `query_sqlite`. | On success: `order_info`; on failure: `errors`. Updates `execution_steps`. |
| **search_shipment** | `order_info`, `errors` | If an order was found and no errors, queries `shipments` by `order_id`. | May add `shipment_info`; always updates `execution_steps`. |
| **summarize_status** | `order_info`, `shipment_info`, `errors` | Generates a textual summary or concatenates error messages. | Sets `status_summary`; updates `execution_steps`. |
| **generate_result** | All accumulated fields | Packages everything into a final dictionary (`final_result`). | Adds `final_result` and final `execution_steps` entry. |

The **state object** (`WF005State`) is passed unchanged between nodes, with each node mutating only the fields it needs. Errors are short‑circuited: once an error is recorded, subsequent nodes either skip their work or simply propagate the error information.

---

## Nodes Used
| Node | Purpose | Key Logic |
|------|---------|-----------|
| `validate_identifier` | Ensure the request contains an identifier. | - Checks `order_id` and `customer_email`. <br> - Appends success/failure messages to `execution_steps`. |
| `search_order` | Retrieve order details from the `orders` table. | - Constructs a dynamic SQL query based on supplied identifiers.<br> - Calls `query_sqlite` and stores the first row in `order_info`.<br> - Handles DB errors and “order not found” cases. |
| `search_shipment` | Retrieve shipment details linked to the order. | - Uses `order_info.order_id` to query `shipments`.<br> - Stores the first row in `shipment_info` if present. |
| `summarize_status` | Build a human‑readable status message. | - If any errors exist, concatenates them.<br> - Otherwise creates a sentence describing order status and, when available, shipment status. |
| `generate_result` | Produce the final output payload. | - Creates a dict with `status`, `order_info`, `shipment_info`, `status_summary`, and `errors`. <br> - Marks the workflow as `success` or `completed_with_errors`. |

All nodes are pure functions that accept a `WF005State` instance and return the same instance after mutation.

---

## Code Structure

```
/project_root
│
├─ workflow/
│   └─ base.py                # Provides BaseWorkflowState (used by WF005State)
│
├─ tools/
│   └─ sqlite_db.py           # Implements query_sqlite helper used by nodes
│
├─ wf005/
│   ├─ __init__.py
│   ├─ graph.py               # Builds and compiles the StateGraph
│   ├─ nodes.py               # All node implementations (validate, search, summarize, generate)
│   └─ state.py               # Typed state definition (WF005State)
│
└─ README.md                  # ← This file
```

### `wf005/graph.py`
* Imports `StateGraph`, `START`, `END` from LangGraph.
* Imports the custom state class (`WF005State`) and all node functions.
* Instantiates a `StateGraph` with `WF005State`.
* Registers each node with a human‑readable name.
* Connects the nodes with directed edges to define the execution order.
* Calls `workflow.compile()` and returns the compiled graph for execution.

### `wf005/nodes.py`
* Contains the five node functions listed above.
* Each function:
  * Reads relevant fields from the incoming `WF005State`.
  * Performs its specific logic (validation, DB query, summary creation, etc.).
  * Updates `execution_steps`, `errors`, and any domain‑specific fields (`order_info`, `shipment_info`, `status_summary`).
  * Returns the mutated state.

* Relies on `tools.sqlite_db.query_sqlite` for all SQLite interactions, abstracting away connection handling.

### `wf005/state.py`
* Defines `WF005State`, a subclass of `BaseWorkflowState`.
* Declares optional typed attributes:
  * `order_id`, `customer_email`
  * `order_info`, `shipment_info`
  * `status_summary`
* Inherits generic dict‑like behavior from `BaseWorkflowState`, allowing node functions to treat the state as a mutable mapping (`state["key"] = value`).

### Supporting Files
* **`workflow/base.py`** – Provides the base class that gives the state dict‑like semantics and optional validation utilities.
* **`tools/sqlite_db.py`** – Implements `query_sqlite(sql, params)` returning a dict with keys `status` (`"success"`/`"error"`), `data` (list of rows), and `error` (error message if any).

---

## Running the Workflow

```python
from wf005.graph import create_order_status_graph

# Build the compiled graph once
order_status_graph = create_order_status_graph()

# Example input state
initial_state = {
    "order_id": "ORD12345",
    "customer_email": None,
    "execution_steps": [],
    "errors": []
}

# Execute
final_state = order_status_graph.invoke(initial_state)

# The result you care about:
print(final_state["final_result"])
```

The `final_result` dictionary will contain the status, any retrieved order/shipment data, a readable summary, and a list of errors (if any).  

--- 

*Feel free to extend the workflow (e.g., add caching, more detailed shipment tracking, or integration with external APIs) by adding new nodes and wiring them into the graph.*