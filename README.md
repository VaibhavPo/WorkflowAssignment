# Workflow Assignment Chatbot

This project is a highly scalable, dynamic workflow-based chatbot application built with Streamlit and LangGraph. It allows users to interact with various automated workflows seamlessly through a conversational interface.

## Features

- **Dynamic Registry System:** Workflows are automatically discovered and added to the chatbot without needing to modify the core application logic.
- **LLM Routing:** An intelligent router automatically reads the registry and routes user queries to the appropriate workflow.
- **Plug-and-Play Architecture:** Easily scale to hundreds of workflows without merge conflicts.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/VaibhavPo/WorkflowAssignment
   cd WorkflowAssignment
   ```

2. **Set up environment variables:**
   Copy the provided `.env.example` to `.env` and fill in your API keys (e.g., Groq API key).

   ```bash
   cp .env.example .env
   ```

3. **Install dependencies:**
   Make sure you have Python installed, then install the required packages (Streamlit, LangGraph, etc.):
   ```bash
   pip install -r requirements.txt
   ```
   > **Note:** The requirements are kept unpinned to avoid version conflicts across different environments. However, if you encounter legacy or compatibility errors, this project was built and successfully tested with: `Python 3.13.7`,`langgraph==1.2.14`, `streamlit==1.65.0`, `pandas==3.0.6`, `pydantic==2.10.4`, and `langchain-groq==1.1.3`.

## Usage

To run the application, start the Streamlit server:

```bash
python -m streamlit run app.py
```

This will launch the web interface where you can interact with the chatbot and trigger the available workflows.

## How to Add a New Workflow

We built a highly scalable, dynamic registry system to minimize friction. You don't need to do anything in the chatbot code itself (like `app.py`).

### The Path of Least Resistance

To make creating a new workflow as low-friction as possible, follow this plug-and-play template. For example, if you want to create a new workflow `WF003`, simply create a new folder `workflow/wf003_your_workflow_name/` and include these standard files:

- **`__init__.py`**: This is the most important file. You define a `WorkflowMetadata` object here (with its description and trigger prompt) and call `registry.register()`. This exposes it to the chatbot.
- **`state.py`**: Define your workflow's state by extending `BaseWorkflowState`.
- **`graph.py`**: Define your LangGraph node edges (`StateGraph`).
- **`nodes.py`**: Write the actual Python functions that execute your logic. **Note:** You should heavily reuse functions from the `tools/` folder (like `read_data` or `calculate`) here to save time.
- **`models.py`** _(Optional)_: Any Pydantic models you need for structured data validation.

### The `tools/` Directory

When building new workflows, avoid rewriting standard logic. The `tools/` folder contains pre-built, reusable utilities designed to be shared across all workflows:

- **Data Handling:** Scripts like `read_data.py` heavily utilize `pandas`, `numpy`, and `openpyxl` to seamlessly read and process CSV and Excel files.
- **API Communication:** Scripts like `llm_generate.py` utilize the `requests` library to fetch and interact with endpoints.

By importing from `tools/`, you keep your workflow's `nodes.py` clean, lightweight, and maintainable.

### How Auto-Discovery Works

Inside `workflow/__init__.py`, there is a `discover_workflows()` function. When your Streamlit chatbot starts, it runs this function, which automatically scans the `workflow/` directory for any subfolders starting with `wf` (like `wf001_...`, `wf002_...`).

It automatically imports them, and their metadata (name, description, trigger) is added to the global registry. The chatbot's LLM router automatically reads this registry. This means the moment you create a new workflow, the chatbot instantly knows about it and can route user queries to it!

By keeping workflows completely isolated in their own folders and relying on the auto-discovery registry, you can scale this up to hundreds of workflows without ever creating merge conflicts or breaking the core chatbot application.
