# SEO Keyword Classification Workflow (WF008)

## Overview
This LangGraph workflow automates the end‑to‑end processing of SEO keyword lists:

1. **Load** raw keyword data from a configurable source.  
2. **Deduplicate** and normalise the keywords.  
3. **Classify** each keyword (intent, priority) and **map** it to a product category / landing page using LLM reasoning and optional product‑category context.  
4. **Export** a structured JSON report that includes a summary, any errors, and the full classified dataset.

The workflow is defined as a deterministic state‑machine (`StateGraph`) that guarantees a single linear path from `START` → `END`, making it easy to debug, test, and extend.

---

## Data Flow

```
START
  │
  ▼
load_keywords ──► deduplicate_keywords ──► classify_and_map ──► generate_export ──► END
```

| Step | Input (from state) | Processing | Output (stored back in state) |
|------|--------------------|------------|------------------------------|
| **load_keywords** | `keyword_source` (path/URL), optional `execution_steps`, `errors` | Reads the source file via `tools.read_data`, validates the presence of a `keyword` column, stores raw records in `keyword_records`. | Updated `keyword_records`, `execution_steps`, `errors`. |
| **deduplicate_keywords** | `keyword_records` | Normalises each keyword (`strip().lower()`), removes duplicates, stores the cleaned list in `deduplicated_keywords`. | Updated `deduplicated_keywords`, `execution_steps`. |
| **classify_and_map** | `deduplicated_keywords`, `product_category_info` | Sends a structured prompt to the LLM (`tools.llm_generate`) with a JSON schema. The LLM returns classifications that are parsed into `ClassifiedKeyword` Pydantic models and stored in `classified_keywords`. | Updated `classified_keywords`, `execution_steps`, `errors`. |
| **generate_export** | `classified_keywords`, `errors` | Builds the final result payload: status, full dataset, summary statistics, and any accumulated errors. Stores it in `final_result`. | Updated `final_result`, `execution_steps`. |

The **state** (`WF008State`) travels through each node, accumulating data, execution logs, and error messages. When the graph reaches `END`, the caller can read `state["final_result"]` for the complete output.

---

## Nodes Used

| Node | Function | Key Responsibilities |
|------|----------|----------------------|
| `load_keywords` | `nodes.load_keywords` | • Reads the source file (CSV, JSON, etc.) using `tools.read_data`. <br>• Verifies that a `keyword` column exists (or an alias). <br>• Populates `state["keyword_records"]`. |
| `deduplicate_keywords` | `nodes.deduplicate_keywords` | • Normalises keywords (lower‑case, trimmed). <br>• Removes duplicates deterministically. <br>• Stores the unique list in `state["deduplicated_keywords"]`. |
| `classify_and_map` | `nodes.classify_and_map` | • Constructs an LLM task with clear instructions and a JSON output schema. <br>• Sends the deduplicated keywords + optional `product_category_info` to `tools.llm_generate`. <br>• Parses the LLM response into `ClassifiedKeyword` objects. <br>• Handles LLM errors and records them. |
| `generate_export` | `nodes.generate_export` | • Serialises the `ClassifiedKeyword` models to plain dictionaries. <br>• Computes a summary (total, high‑priority count, mapped count). <br>• Packages everything (status, dataset, summary, errors) into `state["final_result"]`. |

All nodes receive and return the same `WF008State` instance, allowing the graph to thread a single mutable state object through the pipeline.

---

## Code Structure

```
wf008_seo_keyword/
│
├─ graph.py          # Definition & compilation of the StateGraph
├─ state.py          # WF008State definition (inherits BaseWorkflowState)
├─ nodes.py          # All node implementations (load, dedupe, classify, export)
├─ models.py         # Pydantic model for a classified keyword
│
├─ tools/
│   ├─ read_data.py          # Helper to read CSV/JSON/etc. (returns {"records": [...], "columns": [...]})
│   └─ llm_generate.py       # Wrapper around the LLM provider (returns JSON adhering to schema)
│
└─ workflow/
    └─ base.py               # BaseWorkflowState (provides dict‑like behaviour)
```

### `graph.py`
* Imports `StateGraph`, `START`, `END` from **LangGraph**.
* Registers the four nodes.
* Connects them in a linear chain.
* Returns a compiled graph ready to be executed:

```python
from wf008_seo_keyword.graph import create_seo_keyword_graph
workflow = create_seo_keyword_graph()
result_state = workflow.invoke(initial_state)   # initial_state is a dict matching WF008State fields
```

### `state.py`
* Sub‑class of `BaseWorkflowState` (provides dict‑like access and validation).
* Declares the fields that travel through the workflow:
  * `keyword_source` – path/URL to the raw data file.
  * `product_category_info` – optional free‑form text describing product categories.
  * `keyword_records` – raw rows after loading.
  * `deduplicated_keywords` – list after deduplication.
  * `classified_keywords` – list of `ClassifiedKeyword` objects.

### `nodes.py`
* **`load_keywords`** – reads data, validates column, populates `keyword_records`.
* **`deduplicate_keywords`** – normalises and removes duplicate keywords.
* **`classify_and_map`** – builds LLM prompt, calls `llm_generate`, converts response to `ClassifiedKeyword`.
* **`generate_export`** – creates the final JSON payload (`final_result`).

### `models.py`
* `ClassifiedKeyword` – Pydantic model with fields:
  * `keyword`, `intent`, `category`, `mapped_page`, `priority`.
* Guarantees type safety and easy serialisation (`model_dump()`).

### `tools/`
* **`read_data.py`** – abstracted I/O; supports CSV, JSON, Excel, etc., and returns a uniform dict.
* **`llm_generate.py`** – encapsulates the LLM call (e.g., OpenAI, Anthropic). Handles schema validation and returns either `{ "classifications": [...] }` or an error dict.

---

## Getting Started

### Prerequisites
```bash
python >=3.9
pip install langgraph pydantic
# plus any LLM SDK required by tools.llm_generate (e.g., openai)
```

### Example Usage

```python
from wf008_seo_keyword.graph import create_seo_keyword_graph

# 1️⃣ Prepare the initial state
initial_state = {
    "keyword_source": "data/seo_keywords.csv",
    "product_category_info": "Electronics > Phones, Laptops, Accessories",
    # optional: you can pre‑populate execution_steps / errors if you want
}

# 2️⃣ Build and run the workflow
workflow = create_seo_keyword_graph()
final_state = workflow.invoke(initial_state)

# 3️⃣ Retrieve the result
result = final_state["final_result"]
print(result["status"])
print("Summary:", result["summary"])
# Export to file if needed
import json
with open("output/seo_classification.json", "w") as f:
    json.dump(result, f, indent=2)
```

### Testing
The workflow is deterministic; you can unit‑test each node in isolation:

```python
from wf008_seo_keyword.nodes import deduplicate_keywords
from wf008_seo_keyword.state import WF008State

state = WF008State(keyword_source="", product_category_info=None, keyword_records=[
    {"keyword": "  iPhone  "},
    {"keyword": "iphone"},
    {"keyword": "Galaxy S21"},
])
new_state = deduplicate_keywords(state)
assert len(new_state["deduplicated_keywords"]) == 2
```

---

## Extending the Workflow

* **Add parallel branches** – e.g., a separate node for sentiment analysis before classification.
* **Swap the LLM provider** – modify `tools/llm_generate.py` without touching the graph.
* **Persist intermediate results** – store `state["keyword_records"]` to a DB or S3 inside a new node.

Because the graph is built from pure functions that accept and return the same state object, any new node can be dropped into the chain with a single `workflow.add_node` and an edge definition.

---

## License
This example workflow is provided under the MIT License. Feel free to adapt, redistribute, or integrate it into your own projects.