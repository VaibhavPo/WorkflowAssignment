# Employee Assignment Workflow (WF009)

## Overview
This LangGraph workflow automates the assignment of incoming tasks to the most suitable employees based on required skills, priority, and current workload.  

1. **Task ingestion** – Accepts a single task description or a CSV file containing multiple open tasks.  
2. **Skill extraction** – Uses an LLM to pull required technical/soft skills when they are not explicitly listed.  
3. **Employee data loading** – Pulls the full employee roster (including skills, capacity, and current workload) from a SQLite database.  
4. **Candidate ranking & selection** – Scores each employee against every task, taking both skill‑match and remaining capacity into account, then assigns the best candidate.  
5. **Result aggregation** – Returns a structured list of assignments (or escalation notices) together with an execution trace and any errors encountered.

The workflow is defined as a **state‑graph** (`StateGraph`) that moves deterministically from `START → parse_task → load_employee_data → rank_candidates → select_employee → END`.

---

## Data Flow

| Step | Input (state fields) | Processing | Output (state fields) |
|------|----------------------|------------|-----------------------|
| **START → parse_task** | `task` (string or file path), optional `required_skills`, `priority`, `deadline` | • If `task` points to a CSV, read all rows with status *open*.<br>• If a plain description, wrap it into a single task dict.<br>• When `required_skills` are missing, call `llm_generate` to extract them.<br>• Normalise skill strings into a list. | `tasks_to_process` (list of task dicts), `execution_steps`, `errors` |
| **parse_task → load_employee_data** | `errors` (must be empty to continue) | Query SQLite table `employees` via `query_sqlite`. | `employee_records` (raw DB rows), updated `execution_steps` / `errors` |
| **load_employee_data → rank_candidates** | No new data – placeholder node (kept for future extensions) | Currently a no‑op; passes state unchanged. | Same as input |
| **rank_candidates → select_employee** | `tasks_to_process`, `employee_records` | For each task:<br>1. Normalise required skills.<br>2. Compute **skill_match** (fraction of required skills present).<br>3. Compute **capacity_score** based on `(capacity - workload) / capacity` (penalised for high‑priority tasks with low capacity).<br>4. Combine into **overall_score** = 0.7·skill_match + 0.3·capacity_score.<br>5. Build a list of `RankedEmployee` objects, sort descending, pick the top candidate.<br>6. Update a mutable copy of employee workloads (each assignment consumes 0.1 capacity). | `assignments` (list of assignment dicts), `final_result` (status + assignments), updated `execution_steps`, `errors` |
| **select_employee → END** | – | Workflow terminates. | Final state returned to the caller. |

If any node records an error, subsequent nodes are still executed but the final result will be marked `completed_with_errors` and contain the collected error messages.

---

## Nodes Used

| Node | Function | Key Responsibilities |
|------|----------|----------------------|
| **parse_task** | `nodes.parse_task` | • Detects whether `task` is a CSV file or plain text.<br>• Extracts open tasks from CSV.<br>• Calls the LLM (`llm_generate`) to infer missing `required_skills`.<br>• Normalises skill strings into a list.<br>• Populates `tasks_to_process`. |
| **load_employee_data** | `nodes.load_employee_data` | • Executes `SELECT * FROM employees` against the SQLite DB.<br>• Stores raw employee rows in `employee_records`.<br>• Logs success/failure in `execution_steps`. |
| **rank_candidates** | `nodes.rank_candidates` | Placeholder for future ranking logic. Currently a pass‑through that returns the state unchanged. |
| **select_employee** | `nodes.select_employee` | • Iterates over every task and every employee.<br>• Calculates skill match, capacity score, and overall score.<br>• Constructs `RankedEmployee` Pydantic models for candidates that meet minimal thresholds.<br>• Picks the highest‑scoring employee, updates workload, and records the assignment.<br>• Handles escalation when no suitable candidate exists. |
| **END** | – | Terminates the graph and returns the final state. |

---

## Code Structure

```
wf009_employee_assignment/
│
├─ graph.py          # Builds and compiles the LangGraph StateGraph.
├─ state.py          # Definition of WF009State (inherits BaseWorkflowState).
├─ nodes.py          # All node implementations (parse_task, load_employee_data, …).
├─ models.py         # Pydantic model `RankedEmployee` used for candidate ranking.
├─ tools/
│   ├─ sqlite_db.py  # Helper that runs a query against the SQLite DB and returns a dict.
│   └─ llm_generate.py # Wrapper around the LLM that enforces a JSON schema output.
└─ workflow/
    └─ base.py       # (external) provides BaseWorkflowState used by WF009State.
```

### `graph.py`
* Imports `StateGraph`, `START`, `END`, the custom state class, and node callables.
* Registers each node with a symbolic name.
* Connects the nodes with directed edges to form the linear pipeline.
* Returns a compiled graph ready to be executed (`create_employee_assignment_graph()`).

### `state.py`
* Declares `WF009State` extending `BaseWorkflowState`.
* Typed fields include the incoming task data (`task`, `required_skills`, `priority`, `deadline`), intermediate collections (`tasks_to_process`, `assignments`), and the employee data (`employee_records`, `ranked_candidates`).

### `nodes.py`
* **parse_task** – Handles file I/O, CSV parsing, LLM skill extraction, and normalisation.
* **load_employee_data** – Calls `query_sqlite` and stores the result.
* **rank_candidates** – Currently a stub; kept for modularity.
* **select_employee** – Implements the core matching algorithm, creates `RankedEmployee` objects, updates workloads, and builds the final assignment payload.

### `models.py`
* Defines `RankedEmployee` (Pydantic) with fields:
  * `employee_id`, `employee_name`
  * `matched_skills` – list of skills that overlap with the task.
  * `skill_match`, `capacity_score`, `overall_score` – numeric scores used for ranking.

### `tools/`
* **sqlite_db.py** – Simple wrapper that executes a SQL query and returns `{ "status": "success", "data": [...] }` or an error dict.
* **llm_generate.py** – Sends a prompt + schema to the LLM, parses the JSON response, and returns a dict with either the extracted data or an error message.

---

## Getting Started

1. **Install dependencies** (LangGraph, Pydantic, SQLite driver, LLM client, etc.).  
   ```bash
   pip install langgraph pydantic sqlite3 <llm-client-package>
   ```

2. **Prepare the SQLite DB** – Ensure a table `employees` exists with at least the columns:  
   `employee_id`, `employee_name`, `skills` (comma‑separated string), `capacity` (numeric), `current_workload` (numeric).

3. **Run the workflow**  

   ```python
   from wf009_employee_assignment.graph import create_employee_assignment_graph

   # Example input state
   init_state = {
       "task": "tasks.csv",          # or a plain description string
       "required_skills": None,
       "priority": "high",
       "deadline": "2024-12-31"
   }

   graph = create_employee_assignment_graph()
   result_state = graph.invoke(init_state)
   print(result_state["final_result"])
   ```

4. **Inspect the output** – `final_result` contains:
   * `status` (`completed` or `completed_with_errors`)
   * `assignments` – list of per‑task assignment dictionaries.
   * `execution_steps` – human‑readable trace of what each node did.
   * `errors` – any issues that occurred during processing.

---

## Extending the Workflow

* **Add richer ranking** – Replace the placeholder `rank_candidates` node with a dedicated scoring engine (e.g., machine‑learning model) and keep the graph modular.
* **Parallel processing** – Split `select_employee` into per‑task sub‑graphs if you need concurrent assignment for very large task batches.
* **Persist results** – Append a new node after `select_employee` that writes assignments back to the database or a task‑management system.

--- 

*Happy automating!*