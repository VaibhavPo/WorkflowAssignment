# README.md

## Overview
This LangGraph workflow builds a **marketing campaign brief** from user‑provided inputs.  
It validates required fields, optionally reads product data from a file, and then asks an LLM to generate a structured JSON brief that follows a predefined schema. The workflow stops early if required inputs are missing, prompting the caller to supply them.

Typical use‑case:  
A marketing team supplies a campaign goal, dates, and optional product information. Running the workflow returns a ready‑to‑use brief (objective, audience, messaging, channels, checklist, etc.) or a clear error/status message if something is missing.

---

## Data Flow
```
START → validate_inputs → (conditional) → read_product_information → generate_brief → END
```

1. **Start** – The graph is instantiated with an empty `WF007State` (or a state pre‑populated by the caller).  
2. **validate_inputs** – Checks that `campaign_goal` and `campaign_dates` are present.  
   * If any are missing, `final_result.status` is set to **needs_input** and the graph jumps directly to **END**.  
   * If both are present, execution proceeds to **read_product_information**.  
3. **read_product_information** – If a `products_source` path is supplied, the node attempts to read the file via `tools.read_data`.  
   * Successful read → `product_records` populated.  
   * Failure or no source → `product_records` left empty, errors are logged but the workflow continues.  
4. **generate_brief** – Calls `tools.llm_generate` with a fixed task, instructions, the collected input data, and a JSON schema.  
   * On success, the LLM’s JSON output is stored in `campaign_brief` and `final_result.status` becomes **success**.  
   * On LLM error, `final_result.status` becomes **completed_with_errors** and the error is recorded.  
5. **End** – The compiled state (including `execution_steps`, `errors`, and `final_result`) is returned to the caller.

---

## Nodes Used
| Node | Purpose | Key Operations |
|------|---------|----------------|
| **validate_inputs** | Ensure mandatory campaign fields are present before any heavy processing. | - Checks `campaign_goal` and `campaign_dates`. <br> - Populates `final_result` with `needs_input` status and a helpful message when missing. <br> - Records step outcome in `execution_steps`. |
| **read_product_information** | Load optional product data from a file. | - Reads `products_source` via `tools.read_data`. <br> - Stores records in `product_records`. <br> - Logs any file‑read errors but does **not** abort the workflow. |
| **generate_brief** | Generate the final marketing brief using an LLM. | - Prepares a task description and strict instructions (no hallucination). <br> - Sends `campaign_goal`, `campaign_dates`, `target_audience`, `promotion`, and `product_records` to `tools.llm_generate`. <br> - Validates LLM response against the defined JSON schema. <br> - Updates `campaign_brief`, `final_result`, `execution_steps`, and `errors`. |

**Conditional Edge** – After `validate_inputs`, the workflow uses `should_continue(state)` to decide whether to end early (missing inputs) or continue to the next node.

---

## Code Structure
```
/your_project_root
│
├─ graph.py          # Definition and compilation of the StateGraph
├─ nodes.py          # Implementations of the three workflow nodes
├─ state.py          # Typed state model (WF007State) extending BaseWorkflowState
│
├─ tools/
│   ├─ read_data.py          # Helper to read product files (CSV, JSON, etc.)
│   └─ llm_generate.py       # Wrapper around the LLM API that enforces schema output
│
└─ workflow/
    └─ base.py               # BaseWorkflowState definition (provided by LangGraph)
```

### `graph.py`
* Imports `StateGraph`, `START`, `END` from LangGraph.
* Imports the custom state class (`WF007State`) and node functions.
* Defines `should_continue(state)` – decides whether to terminate early based on `final_result.status`.
* `create_marketing_campaign_graph()` builds the graph:
  * Registers nodes.
  * Connects edges, including the conditional edge after validation.
  * Returns a compiled graph ready for execution (`graph.compile()`).

### `nodes.py`
* **validate_inputs(state)** – Performs required‑field checks, updates `execution_steps` and `final_result` if inputs are missing.
* **read_product_information(state)** – Reads product data if a source file is supplied, handling errors gracefully.
* **generate_brief(state)** – Calls the LLM, enforces the output schema, stores the brief, and sets the final status.

All nodes receive and return the same `WF007State` instance, enabling seamless state mutation across steps.

### `state.py`
* Defines `WF007State`, a subclass of `BaseWorkflowState`.
* Typed attributes:
  * `campaign_goal`, `campaign_dates`, `products_source`, `target_audience`, `promotion` – optional strings supplied by the caller.
  * `product_records` – list of product objects read from the file.
  * `campaign_brief` – the JSON brief produced by the LLM.
* Inherits generic fields like `execution_steps`, `errors`, and `final_result` from `BaseWorkflowState`.

### `tools/`
* **read_data.py** – Abstracts file I/O (CSV, JSON, etc.) and returns a dict with a `records` key.
* **llm_generate.py** – Sends the prompt, instructions, and input data to the LLM, validates the response against the supplied JSON schema, and returns either `{ "error": False, "result": … }` or `{ "error": True, "message": … }`.

---

## Getting Started

```python
from graph import create_marketing_campaign_graph

# Example initial state
initial_state = {
    "campaign_goal": "Increase brand awareness for the new smartwatch line",
    "campaign_dates": "2024-11-01 to 2024-12-15",
    "products_source": "data/products.json",   # optional
    "target_audience": "Tech‑savvy millennials",
    "promotion": "Early‑bird 15% discount"
}

graph = create_marketing_campaign_graph()
result_state = graph.invoke(initial_state)

print(result_state["final_result"])
# => { "status": "success", "campaign_brief": { ... } }
```

If required fields are omitted, `final_result` will contain:

```json
{
  "status": "needs_input",
  "missing_inputs": ["campaign_goal", "campaign_dates"],
  "message": "Please provide the campaign goal, campaign dates."
}
```

---

## Extending the Workflow
* **Add more validation** – Insert extra nodes before `read_product_information` (e.g., date format checking).
* **Enrich product handling** – Enhance `read_product_information` to support multiple file formats or remote APIs.
* **Custom LLM prompts** – Modify `generate_brief` to accept a different `task` or additional instructions.

---

## License
This workflow is released under the MIT License. See the `LICENSE` file for details.