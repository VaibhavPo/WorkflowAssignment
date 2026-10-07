import os
import json
import uuid
import time
from datetime import datetime, timezone
from dotenv import load_dotenv

# Ensure workflows are discovered
from workflow import discover_workflows
from workflow.registry import list_workflows, get_workflow
from langchain_groq import ChatGroq
from app import WorkflowRouterResult
import pandas as pd

load_dotenv()

# Discover workflows
discover_workflows()

test_cases = [
    {
        "id": 1,
        "workflow_id": "WF001",
        "prompt": "Check the inventory and tell me which products need restocking. Also calculate how many units should be reordered for each one.",
        "files": ["data/sample_inventory.csv"]
    },
    {
        "id": 2,
        "workflow_id": "WF002",
        "prompt": "Validate our product prices against the vendor price list and show only products where the vendor price differs from ours by more than 10%.",
        "files": ["data/vendor_prices.csv", "data/products.csv"]
    },
    {
        "id": 3,
        "workflow_id": "WF003",
        "prompt": "Process this vendor Excel file. Clean the column names, identify rows missing either SKU or product name, and give me the cleaned data and invalid-row report.",
        "files": ["data/vendor_products.csv"]
    },
    {
        "id": 4,
        "workflow_id": "WF004",
        "prompt": "Generate product content for the following product:\nProduct name: UrbanTrail Backpack\nCategory: Travel & Outdoor Bags\nAttributes: 25L capacity, laptop compartment, water-resistant, multiple pockets\nMaterial: Polyester\nColor: Black\nTarget audience: College students and young professionals\nGenerate: A detailed product description, A short product description, An SEO title, A meta description",
        "files": []
    },
    {
        "id": 5,
        "workflow_id": "WF005",
        "prompt": "Check the status of order ORD-9999 and tell me its shipment and tracking information.",
        "files": ["data/orders.db"]
    },
    {
        "id": 6,
        "workflow_id": "WF006",
        "prompt": "Scan the product catalog for duplicates. Separate definite duplicates from possible duplicates and include your confidence for each possible match.",
        "files": ["data/products.csv"]
    },
    {
        "id": 7,
        "workflow_id": "WF007",
        "prompt": "Create a campaign brief for our new product collection. The target audience is young professionals and the promotion is 20% off.",
        "files": []
    },
    {
        "id": 8,
        "workflow_id": "WF008",
        "prompt": "Classify these keywords by search intent, remove duplicates, map them to the appropriate product/category pages, and identify the highest-priority keywords.",
        "files": ["data/keywords_inclusive.csv"]
    },
    {
        "id": 9,
        "workflow_id": "WF009",
        "prompt": "Assign this urgent development task to the best employee based on their skills and current workload. If nobody has both the required skills and enough capacity, escalate instead of assigning someone unsuitable.",
        "files": ["data/tasks.csv", "data/employee_data.csv"]
    },
    {
        "id": 10,
        "workflow_id": "WF010",
        "prompt": "Analyze the workflow execution logs and tell me which workflows are performing poorly. Include failure rate, average execution time, frequent errors, slow steps, and recommendations.",
        "files": ["data/workflow_logs.csv"]
    }
]

def update_readme():
    with open("README.md", "r") as f:
        content = f.read()

    if "## Test Prompts and Data Mapping" not in content:
        table_content = "\n## Test Prompts and Data Mapping\n\n"
        table_content += "| # | Workflow | Test prompt | Associated File(s) | Main thing being tested |\n"
        table_content += "|---|---|---|---|---|\n"
        table_content += '| 1 | WF001 | "Check the inventory and tell me which products need restocking. Also calculate how many units should be reordered for each one." | `data/sample_inventory.csv` | threshold + reorder calculation |\n'
        table_content += '| 2 | WF002 | "Validate our product prices against the vendor price list and show only products where the vendor price differs from ours by more than 10%." | `data/vendor_prices.csv`, `data/products.csv` | SKU matching + percentage decision |\n'
        table_content += '| 3 | WF003 | "Process this vendor Excel file. Clean the column names, identify rows missing either SKU or product name, and give me the cleaned data and invalid-row report." | `data/vendor_products.csv` | file ingestion + validation |\n'
        table_content += '| 4 | WF004 | "Create a product description, short description, SEO title and meta description for this product. Use only the attributes provided in the file and clearly identify anything that is missing." | `data/vendor_products.csv` | LLM generation + no hallucination |\n'
        table_content += '| 5 | WF005 | "Check the status of order ORD-9999 and tell me its shipment and tracking information." | `data/orders.db` | missing-order/error handling |\n'
        table_content += '| 6 | WF006 | "Scan the product catalog for duplicates. Separate definite duplicates from possible duplicates and include your confidence for each possible match." | `data/products.csv` | exact matching + similarity/confidence |\n'
        table_content += '| 7 | WF007 | "Create a campaign brief for our new product collection. The target audience is young professionals and the promotion is 20% off." | None | missing required inputs |\n'
        table_content += '| 8 | WF008 | "Classify these keywords by search intent, remove duplicates, map them to the appropriate product/category pages, and identify the highest-priority keywords." | `data/keywords_inclusive.csv` | classification + mapping + prioritization |\n'
        table_content += '| 9 | WF009 | "Assign this urgent development task to the best employee based on their skills and current workload. If nobody has both the required skills and enough capacity, escalate instead of assigning someone unsuitable." | `data/tasks.csv`, `data/employee_data.csv` | ranking + capacity + escalation |\n'
        table_content += '| 10 | WF010 | "Analyze the workflow execution logs and tell me which workflows are performing poorly. Include failure rate, average execution time, frequent errors, slow steps, and recommendations." | `data/workflow_logs.csv` | aggregation + threshold detection + reporting |\n'

        with open("README.md", "a") as f:
            f.write(table_content)
        print("Updated README.md with test cases.")
    else:
        print("README.md already contains test cases.")


def run_tests():
    groq_api_key = os.getenv("GROQ_API_KEY", "")
    if not groq_api_key:
        print("Error: GROQ_API_KEY not set.")
        return

    model_name = os.getenv("GROQ_MODEL", "llama3-8b-8192")
    llm = ChatGroq(model=model_name, api_key=groq_api_key)
    
    workflows = list_workflows()
    workflow_definitions = ""
    for wf in workflows:
        workflow_definitions += f"- ID: {wf.workflow_id}\n"
        workflow_definitions += f"  Name: {wf.workflow_name}\n"
        workflow_definitions += f"  Purpose: {wf.description}\n"
        workflow_definitions += f"  Input requirements: {wf.input_requirements}\n\n"

    llm_router = llm.with_structured_output(WorkflowRouterResult)
    
    results_md = "# Workflow Automation Test Results\n\n"
    results_md += f"Run Date: {datetime.now(timezone.utc).isoformat()}\n\n"

    for tc in test_cases:
        print(f"--- Running Test {tc['id']} ---")
        prompt = tc["prompt"]
        files = tc["files"]
        expected_wf = tc["workflow_id"]
        
        file_registry = {}
        for f in files:
            # use relative path as identifier, we will map it to absolute later
            if os.path.exists(f):
                file_registry[f] = os.path.abspath(f)
            else:
                print(f"Warning: File {f} not found!")
                
        available_files = list(file_registry.keys())

        router_prompt = (
            "You are an AI Workflow Router.\n"
            "Your job is to select the correct workflow based on the user's request.\n"
            f"Available Files in Workspace: {available_files}\n\n"
            "Available Workflows:\n"
            f"{workflow_definitions}\n"
            "Instructions:\n"
            "1. Match the user's intent to one of the workflow IDs.\n"
            "2. Extract any parameters provided in the user request or available files into `extracted_parameters`.\n"
            "3. If a workflow requires an input and a suitable file is in the Available Files, map the file name to the required input key.\n"
        )
        
        messages = [("system", router_prompt), ("user", prompt)]
        
        print("Routing...")
        try:
            router_result = llm_router.invoke(messages)
            print(f"Routed to: {router_result.workflow_id} (Confidence: {router_result.confidence:.2f})")
        except Exception as e:
            print(f"Router error: {e}")
            continue

        results_md += f"## Test {tc['id']}: {expected_wf}\n"
        results_md += f"**Prompt:** {prompt}\n"
        results_md += f"**Files Available:** {', '.join(files) if files else 'None'}\n"
        results_md += f"**Router Decision:** {router_result.workflow_id} (Expected: {expected_wf})\n"
        results_md += f"**Missing Inputs:** {router_result.missing_inputs}\n"
        
        if router_result.workflow_id and router_result.workflow_id == expected_wf:
            wf_meta = get_workflow(router_result.workflow_id)
            if not wf_meta:
                results_md += "> Workflow not implemented yet.\n\n"
                continue
                
            state = {
                "execution_steps": [],
                "errors": [],
            }
            
            # Map parameters
            for k, v in router_result.extracted_parameters.items():
                if isinstance(v, str) and v in file_registry:
                    state[k] = file_registry[v]
                else:
                    state[k] = v
                    
            print(f"Executing workflow {wf_meta.workflow_id}...")
            
            try:
                res = wf_meta.graph_factory().invoke(state)
                final_result = res.get("final_result", {})
                status = final_result.get('status', 'unknown')
                
                results_md += f"**Execution Status:** {status}\n\n"
                results_md += "### Output\n```json\n"
                results_md += json.dumps(final_result, indent=2)
                results_md += "\n```\n\n"
                print(f"Execution complete. Status: {status}")
            except Exception as e:
                results_md += f"**Execution Error:** {str(e)}\n\n"
                print(f"Execution failed: {e}")
        else:
            results_md += "> Router did not select the expected workflow or the workflow is not supported.\n\n"
            
    with open("test_results.md", "w") as f:
        f.write(results_md)
        
    print("Tests completed. Results saved to test_results.md")

if __name__ == "__main__":
    update_readme()
    run_tests()
