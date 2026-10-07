# Product Description Generation Workflow (WF004)

## Overview
This LangGraph workflow automates the creation of SEO‑friendly product copy.  
Given a set of product attributes (name, category, material, color, etc.), it:

1. **Validates** that all required attributes are present.  
2. **Generates** a full product description.  
3. **Derives** a concise short description.  
4. **Creates** an SEO‑optimized title.  
5. **Builds** a meta description suitable for search engine results.  
6. **Aggregates** everything into a final result object, including any missing information or errors encountered along the way.

The workflow is deterministic, linear, and fully typed through a custom `WF004State` model, making it easy to integrate into larger e‑commerce pipelines or content‑generation services.

---

## Data Flow
```
START → validate_attributes → generate_product_description
      → generate_short_description → generate_seo_title
      → generate_meta_description → generate_result → END
```

| Step | Input (state fields) | Processing | Output (state fields) |
|------|----------------------|------------|-----------------------|
| **validate_attributes** | Raw product fields (`product_name`, `category`, `attributes`, `material`, `color`, `target_audience`) | Checks each required field; records any that are missing. | `missing_information` (list) + appends a log entry to `execution_steps`. |
| **generate_product_description** | All product fields + `missing_information` | Calls `llm_generate` with a prompt to produce a full description, explicitly noting missing data when needed. | `product_description` (string) + log entry. |
| **generate_short_description** | `product_name`, `product_description`, `missing_information` | Calls LLM to condense the full description into a short version. | `short_description` (string) + log entry. |
| **generate_seo_title** | `product_name`, `category`, `product_description` | Calls LLM to craft an SEO‑friendly title. | `seo_title` (string) + log entry. |
| **generate_meta_description** | `seo_title`, `short_description` | Calls LLM to produce a meta description (< 160 chars). | `meta_description` (string) + log entry. |
| **generate_result** | All previously generated fields, `missing_information`, any accumulated `errors` | Packages everything into a single `final_result` dictionary and marks the overall status. | `final_result` (dict) + final log entry. |

Throughout the flow, two auxiliary state lists are maintained:

- `execution_steps`: Human‑readable trace of each node’s execution.
- `errors`: Collected error messages from any node that fails to obtain a valid LLM response.

---

## Nodes Used
| Node | Purpose | Key Operations |
|------|---------|----------------|
| **validate_attributes** | Ensures required product data is present. | Iterates over a predefined attribute list, builds `missing_information`, updates `execution_steps`. |
| **generate_product_description** | Produces a detailed, SEO‑aware product description. | Calls `llm_generate` with a rich prompt, respects `missing_information`, stores result in `product_description`. |
| **generate_short_description** | Creates a concise version of the description. | Calls `llm_generate` using the full description as context, stores result in `short_description`. |
| **generate_seo_title** | Generates a search‑engine‑friendly title. | Calls `llm_generate` with product name, category, and description, stores result in `seo_title`. |
| **generate_meta_description** | Generates a meta description for SERPs. | Calls `llm_generate` with the SEO title and short description, stores result in `meta_description`. |
| **generate_result** | Consolidates all outputs and status. | Builds `final_result` dict, sets overall `status`, records completion step. |

All nodes share the same signature: `def node(state: WF004State) -> WF004State`, allowing LangGraph to pass the mutable state object from one node to the next.

---

## Code Structure

```
project_root/
│
├─ workflow/
│   ├─ base.py                # Provides BaseWorkflowState (used by WF004State)
│
├─ tools/
│   └─ llm_generate.py        # Wrapper around the LLM API; returns dict matching output_schema
│
├─ wf004/
│   ├─ __init__.py
│   ├─ graph.py               # Builds and compiles the StateGraph
│   ├─ nodes.py               # All node implementations (validation + generation steps)
│   └─ state.py               # Typed state model (WF004State) extending BaseWorkflowState
│
└─ README.md                  # ← This file
```

### `graph.py`
- Imports `StateGraph`, `START`, `END` from LangGraph.
- Imports the custom state class `WF004State` and all node functions.
- Instantiates a `StateGraph` with `WF004State`.
- Registers each node with a unique name.
- Connects nodes linearly using `add_edge`.
- Compiles the graph and returns a runnable workflow via `create_product_description_graph()`.

### `nodes.py`
- Contains the six node functions listed above.
- Each node:
  1. Retrieves the current `execution_steps` and `errors` from the state (creating them if missing).
  2. Prepares `input_data` for the LLM based on the current state.
  3. Defines a JSON schema (`output_schema`) that the LLM must adhere to.
  4. Calls `llm_generate` with a task description, detailed instructions, the input data, and the schema.
  5. Handles success or error, updating the state accordingly and appending a step description.

### `state.py`
- Defines `WF004State`, a subclass of `BaseWorkflowState`.
- Declares all fields used throughout the workflow with appropriate optional typing.
- Fields include raw inputs (`product_name`, `category`, …), generated outputs (`product_description`, `short_description`, `seo_title`, `meta_description`), and auxiliary tracking fields (`missing_information`, `final_result`).

### `tools/llm_generate.py` (external to this workflow)
- Provides a thin wrapper around the chosen LLM provider.
- Accepts `task`, `instructions`, `input_data`, and `output_schema`.
- Returns a dictionary matching the schema or an error dict (`{"error": True, "message": "..."}).

---

## Getting Started

```bash
# Install dependencies (LangGraph, pydantic, your LLM SDK, etc.)
pip install -r requirements.txt

# Example usage
from wf004.graph import create_product_description_graph

workflow = create_product_description_graph()

initial_state = {
    "product_name": "EcoSmart Water Bottle",
    "category": "Outdoor Gear",
    "attributes": "BPA‑free, 1‑liter capacity",
    "material": "Stainless steel",
    "color": "Matte black",
    "target_audience": "Eco‑conscious hikers"
}

result_state = workflow.invoke(initial_state)
print(result_state["final_result"])
```

The `final_result` dictionary will contain the generated copy, any missing fields, and a status flag indicating success or partial failure.

---

## Extending the Workflow
- **Add parallel branches** (e.g., generate multiple tagline options) by creating additional nodes and using `add_edge` with branching logic.
- **Swap the LLM**: modify `tools/llm_generate.py` to point to a different model or provider without touching the workflow logic.
- **Enrich validation**: extend `validate_attributes` to perform type checks, regex validation, or external look‑ups.

Feel free to adapt the nodes, prompts, or schema to match your brand voice or SEO guidelines. Happy coding!