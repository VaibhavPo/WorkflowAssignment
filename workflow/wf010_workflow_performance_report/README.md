# Performance Report Workflow (WF010)

## Overview
This LangGraph workflow automates the end‑to‑end generation of a performance report for a set of workflow executions.  

1. **Load raw execution logs** from a configurable source.  
2. **Calculate key metrics** (failure rate, average execution time, frequent errors, slow steps).  
3. **Flag under‑performing workflows** and ask an LLM to produce concise, data‑driven recommendations.  
4. **Assemble a final JSON report** that includes a summary, per‑workflow metrics, slow steps, recommendations, and any errors that occurred during processing.

The workflow is defined as a deterministic state‑machine where each node receives the shared `WF010State`, mutates it, and passes it to the next node.

---

## Data Flow

```
START
  │
  ▼
load_workflow_logs ──► calculate_metrics ──► generate_recommendations ──► generate_report ──► END
```

| Step | Input (state fields) | Output (state fields) | Purpose |
|------|----------------------|-----------------------|---------|
| **load_workflow_logs** | `log_source`, `execution_steps`, `errors` | `log_records`, updated `execution_steps`, `errors` | Reads the raw CSV/JSON log file, validates required columns, and stores the raw records. |
| **calculate_metrics** | `log_records` | `workflow_metrics`, `slow_steps`, `overall_summary`, updated `execution_steps` | Aggregates per‑workflow statistics, computes failure rates & average durations (using the `calculate` tool), identifies flagged workflows, and extracts the top‑10 slowest steps. |
| **generate_recommendations** | `workflow_metrics`, `errors`, `execution_steps` | `recommendations`, updated `execution_steps`, `errors` | If any workflow is flagged, calls the `llm_generate` tool with a strict prompt to produce 1‑3 actionable recommendations. |
| **generate_report** | All fields populated so far | `final_result` (the report JSON), updated `execution_steps` | Packages the summary, metrics, slow steps, recommendations, and any accumulated errors into a single result object. |

The **state object** (`WF010State`) is passed unchanged between nodes, ensuring a single source of truth throughout the pipeline.

---

## Nodes Used

| Node | Module | Description |
|------|--------|-------------|
| `load_workflow_logs` | `nodes.py` | Reads execution logs from `state.log_source` using `tools.read_data.read_data`. Handles missing columns, records errors, and stores the raw records in `state.log_records`. |
| `calculate_metrics` | `nodes.py` | Iterates over `log_records` to build per‑workflow and per‑step aggregates. Uses `tools.calculate.calculate` to compute failure rates and averages. Flags workflows that exceed `FAILURE_RATE_THRESHOLD` (10 %) or `AVERAGE_EXECUTION_TIME_THRESHOLD` (5 s). Stores metrics, slow‑step list, and an overall summary in the state. |
| `generate_recommendations` | `nodes.py` | Detects flagged workflows. When present, constructs a task + strict instructions and calls `tools.llm_generate.llm_generate` to obtain a list of recommendations. Guarantees no invented data. If no workflows are flagged, inserts a default “all good” message. |
| `generate_report` | `nodes.py` | Consolidates everything into `state.final_result`, a JSON‑serialisable dictionary with status, summary, metrics, slow steps, recommendations, and any errors. |

All nodes follow the same signature: `def node(state: WF010State) -> WF010State`.

---

## Code Structure

```
workflow/
│
├─ graph.py                # Definition & compilation of the StateGraph
├─ nodes.py                # All node implementations (load, calculate, recommend, report)
├─ state.py                # WF010State definition (inherits BaseWorkflowState)
│
├─ tools/
│   ├─ read_data.py        # read_data(source) → {"records": [...], "columns": [...]}
│   ├─ calculate.py        # calculate(metric_type, **kwargs) → {"status": "...", "result": ...}
│   └─ llm_generate.py     # llm_generate(task, instructions, input_data, output_schema)
│
└─ workflow/
    └─ base.py             # BaseWorkflowState (provides dict‑like behavior, validation, etc.)
```

### `graph.py`
* Imports `StateGraph`, `START`, `END` from LangGraph.
* Imports the custom state class (`WF010State`) and the four node functions.
* Instantiates a `StateGraph` with `WF010State`.
* Registers each node with a human‑readable name.
* Connects the nodes linearly from `START` to `END`.
* Returns the compiled graph ready for execution (`create_performance_report_graph()`).

### `nodes.py`
* **Constants** – thresholds for failure rate and average execution time.
* **`load_workflow_logs`** – reads data, validates columns, populates `log_records`.
* **`calculate_metrics`** – aggregates statistics, uses the `calculate` tool, builds:
  * `workflow_metrics` (per‑workflow dicts)
  * `slow_steps` (top‑10 slowest step‑level entries)
  * `overall_summary` (total, successful, failed counts)
* **`generate_recommendations`** – conditional LLM call; stores `recommendations`.
* **`generate_report`** – builds the final result dictionary (`final_result`).

### `state.py`
* Defines `WF010State` as a subclass of `BaseWorkflowState`.
* Declares typed attributes used throughout the workflow:
  * `log_source: str`
  * `log_records: List[Any]`
  * `workflow_metrics: List[Any]`
  * `slow_steps: List[Any]`
  * `overall_summary: dict`
  * `recommendations: List[str]`
* The base class provides dict‑like access (`state["key"]`) and validation helpers.

### `tools/`
* **`read_data.py`** – abstracts file I/O (CSV, JSON, etc.) and returns a uniform structure.
* **`calculate.py`** – generic statistical helper used for failure‑rate and average calculations; returns a status/result dict.
* **`llm_generate.py`** – thin wrapper around an LLM provider (OpenAI, Anthropic, etc.) that enforces a JSON schema on the output.

---

## Running the Workflow

```python
from workflow.graph import create_performance_report_graph

# Build the compiled graph
graph = create_performance_report_graph()

# Prepare the initial state
initial_state = {
    "log_source": "data/execution_logs.csv",   # path, URL, or any source understood by read_data
    "execution_steps": [],
    "errors": []
}

# Execute
final_state = graph.invoke(initial_state)

# The report is available under:
report = final_state["final_result"]
print(report)
```

*Make sure the `tools/` package is installed and that any required API keys for the LLM are set in the environment before invoking the graph.*

---

## Extending the Workflow

| What you might want to add | Where to modify |
|----------------------------|-----------------|
| Additional thresholds (e.g., memory usage) | Add constants & logic in `calculate_metrics`. |
| More detailed step‑level analysis | Enrich `slow_steps` creation in `calculate_metrics`. |
| Custom LLM prompts or multiple recommendation passes | Adjust `generate_recommendations` (task/instructions). |
| Persist the report to a database or file | Add a new node after `generate_report` and insert it into the graph before `END`. |

Because the workflow is built on LangGraph’s `StateGraph`, inserting, removing, or re‑ordering nodes only requires updating `graph.py` while keeping each node’s pure‑function signature intact.