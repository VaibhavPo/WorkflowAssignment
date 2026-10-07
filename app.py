import streamlit as st
import tempfile
import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import StructuredTool
from langchain_core.messages import HumanMessage, AIMessage

from workflow.registry import list_workflows
import importlib

from workflow import discover_workflows
# Dynamically discover and register all workflows in the workflow directory
discover_workflows()

load_dotenv()

st.set_page_config(page_title="Workflow Chatbot", layout="wide")
st.title("Workflow Automation Chatbot")
st.markdown(
    "Interact with registered workflows through natural language using the LLM Router."
)

# Initialize chat history
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {
        "Chat 1": [
            AIMessage(content="Hello! I am your AI Workflow router. Ask me to run tasks like checking inventory restock.")
        ]
    }
    st.session_state.current_chat = "Chat 1"

if "file_registry" not in st.session_state:
    st.session_state["file_registry"] = {}

if "rename_chat" not in st.session_state:
    st.session_state.rename_chat = None

# Sidebar for configuration and file uploads
with st.sidebar:
    st.header("Actions")
    if st.button("Start New Chat", use_container_width=True):
        new_chat_name = f"Chat {len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions[new_chat_name] = [
            AIMessage(
                content="Hello! I am your AI Workflow router. Ask me to run tasks like checking inventory restock."
            )
        ]
        st.session_state.current_chat = new_chat_name
        st.session_state.file_registry = {}
        st.rerun()

    st.header("Previous Chats")
    
    if st.session_state.rename_chat:
        st.write(f"**Rename: {st.session_state.rename_chat}**")
        new_name = st.text_input("New Name", value=st.session_state.rename_chat, label_visibility="collapsed")
        c1, c2 = st.columns(2)
        if c1.button("Save", use_container_width=True):
            old_name = st.session_state.rename_chat
            if new_name and new_name != old_name and new_name not in st.session_state.chat_sessions:
                # Maintain order by recreating dict
                new_sessions = {}
                for k, v in st.session_state.chat_sessions.items():
                    if k == old_name:
                        new_sessions[new_name] = v
                    else:
                        new_sessions[k] = v
                st.session_state.chat_sessions = new_sessions
                if st.session_state.current_chat == old_name:
                    st.session_state.current_chat = new_name
            st.session_state.rename_chat = None
            st.rerun()
        if c2.button("Cancel", use_container_width=True):
            st.session_state.rename_chat = None
            st.rerun()
        st.divider()
        
    for chat_name in list(st.session_state.chat_sessions.keys()):
        cols = st.columns([0.6, 0.2, 0.2])
        
        # Indicator for active chat instead of bright primary color
        display_name = f"» {chat_name}" if chat_name == st.session_state.current_chat else chat_name
        
        if cols[0].button(display_name, key=f"sel_{chat_name}", use_container_width=True):
            st.session_state.current_chat = chat_name
            st.session_state.file_registry = {}
            st.rerun()
            
        if cols[1].button("Ren", key=f"ren_{chat_name}", help="Rename chat"):
            st.session_state.rename_chat = chat_name
            st.rerun()
            
        if cols[2].button("Del", key=f"del_{chat_name}", help="Delete chat"):
            if len(st.session_state.chat_sessions) > 1:
                del st.session_state.chat_sessions[chat_name]
                if st.session_state.current_chat == chat_name:
                    st.session_state.current_chat = list(st.session_state.chat_sessions.keys())[0]
                    st.session_state.file_registry = {}
                st.rerun()
            else:
                st.error("Cannot delete the last chat.")

# Link the active chat session to the messages variable
st.session_state.messages = st.session_state.chat_sessions[st.session_state.current_chat]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message("user" if isinstance(message, HumanMessage) else "assistant"):
        st.markdown(message.content)
        if hasattr(message, "additional_kwargs") and "dataframes" in message.additional_kwargs:
            for title, df_data in message.additional_kwargs["dataframes"].items():
                st.write(f"**{title}**")
                st.dataframe(df_data)


from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import json

class WorkflowRouterResult(BaseModel):
    workflow_id: Optional[str] = Field(description="The ID of the matched workflow (e.g., 'WF001', 'WF002', 'WF003', 'WF004', 'WF005'). Use null if no supported workflow clearly matches.")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0.")
    reason: str = Field(description="Reason for selecting this workflow or null.")
    required_inputs: List[str] = Field(description="List of required input keys for this workflow.")
    missing_inputs: List[str] = Field(description="List of required inputs that are missing from the request and workspace context.")
    extracted_parameters: Dict[str, Any] = Field(description="Dictionary of extracted parameters to pass to the workflow. Keys must match the workflow's input_requirements. Values should be the extracted values or exact filenames.")

# Accept user input
if user_input := st.chat_input(
    "Ask me to run a workflow (e.g., 'Which products need restocking?')",
    accept_file="multiple",
    file_type=["csv", "xlsx"]
):
    groq_api_key = os.getenv("GROQ_API_KEY", "")
    if not groq_api_key:
        st.error("Please enter your Groq API Key in the .env file.")
        st.stop()
        
    prompt_text = getattr(user_input, "text", user_input)
    uploaded_files = getattr(user_input, "files", []) if hasattr(user_input, "files") else []
    
    if uploaded_files:
        for f in uploaded_files:
            if f.name not in st.session_state["file_registry"]:
                ext = os.path.splitext(f.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                    tmp.write(f.getvalue())
                    st.session_state["file_registry"][f.name] = tmp.name

    if not prompt_text and uploaded_files:
        prompt_text = f"Uploaded {len(uploaded_files)} files."

    st.session_state.messages.append(HumanMessage(content=prompt_text))
    with st.chat_message("user"):
        st.markdown(prompt_text)

    with st.chat_message("assistant"):
        with st.spinner("Thinking and routing..."):
            try:
                # Initialize LLM
                model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
                llm = ChatGroq(model=model_name, api_key=groq_api_key)
                
                file_registry = st.session_state.get("file_registry", {})
                available_files = list(file_registry.keys())
                
                from workflow.registry import list_workflows, get_workflow
                workflows = list_workflows()
                
                workflow_definitions = ""
                for wf in workflows:
                    workflow_definitions += f"- ID: {wf.workflow_id}\n"
                    workflow_definitions += f"  Name: {wf.workflow_name}\n"
                    workflow_definitions += f"  Purpose: {wf.description}\n"
                    workflow_definitions += f"  Input requirements: {wf.input_requirements}\n\n"
                
                # Construct a prompt for the router
                router_prompt = (
                    "You are an AI Workflow Router.\n"
                    "Your job is to select the correct workflow based on the user's request.\n"
                    f"Available Files in Workspace: {available_files}\n\n"
                    "Available Workflows:\n"
                    f"{workflow_definitions}\n"
                    "Instructions:\n"
                    "1. Match the user's intent to one of the workflow IDs. Consider previous conversation context to maintain the workflow intent.\n"
                    "2. Do NOT invent new workflow IDs. Only use the ones provided. If none match, return null.\n"
                    "3. Extract any parameters provided in the user request or available files into `extracted_parameters`.\n"
                    "4. CRITICAL: If a workflow requires an input (like 'task') and a suitable file is in the Available Files (like 'tasks.csv'), map the file name to the required input key in `extracted_parameters` (e.g., {'task': 'tasks.csv'}).\n"
                    "5. Evaluate `input_requirements`. If an input is mapped in `extracted_parameters`, it is NOT missing.\n"
                    "6. Base your decision on intent, workflow capabilities, and provided inputs.\n"
                    "7. You MUST ALWAYS return the structured output (call the tool). NEVER respond with conversational text. If you need more information from the user, report it in the `missing_inputs` field of the structured output.\n"
                )
                
                # Chat history context
                messages_for_router = [("system", router_prompt)]
                # Add recent context to provide conversational continuity without large loops
                for msg in st.session_state.messages[-4:]:
                    role = "user" if isinstance(msg, HumanMessage) else "assistant"
                    messages_for_router.append((role, msg.content))

                # Route
                llm_router = llm.with_structured_output(WorkflowRouterResult)
                router_result: WorkflowRouterResult = llm_router.invoke(messages_for_router)
                
                # Log for debugging/observability
                with st.expander("Routing Trace (Debug)", expanded=False):
                    st.write(f"**Router Decision:** {router_result.workflow_id} (Confidence: {router_result.confidence:.2f})")
                    st.write(f"**Reason:** {router_result.reason}")
                    st.write(f"**Required Inputs:** {router_result.required_inputs}")
                    st.write(f"**Missing Inputs:** {router_result.missing_inputs}")
                    st.write(f"**Extracted Params:** {router_result.extracted_parameters}")

                final_response_text = ""
                
                if not router_result.workflow_id or router_result.workflow_id not in [wf.workflow_id for wf in workflows]:
                    final_response_text = "I'm sorry, I couldn't find a supported workflow that matches your request. Can you please clarify?"
                elif router_result.missing_inputs:
                    final_response_text = f"To proceed with the {router_result.workflow_id} workflow, I need the following missing inputs: {', '.join(router_result.missing_inputs)}."
                else:
                    # Execute workflow natively
                    wf_meta = get_workflow(router_result.workflow_id)
                    
                    # Prepare isolated state for this request
                    state = {
                        "execution_steps": [],
                        "errors": [],
                    }
                    
                    # Resolve filenames to actual paths
                    for k, v in router_result.extracted_parameters.items():
                        if isinstance(v, str) and v in file_registry:
                            state[k] = file_registry[v]
                        else:
                            state[k] = v
                    
                    with st.expander("Execution Trace (Debug)", expanded=False):
                        st.write(f"**Execution:** Starting {wf_meta.workflow_id}...")
                        
                        import time
                        import uuid
                        from datetime import datetime, timezone
                        from tools.csv_logger import log_workflow_execution
                        log_path = os.path.join(os.getcwd(), "workflow_execution_logs.csv")
                        start_time = time.time()
                        exec_id = str(uuid.uuid4())
                        ts = datetime.now(timezone.utc).isoformat()
                        
                        try:
                            # Run LangGraph workflow
                            res = wf_meta.graph_factory().invoke(state)
                            end_time = time.time()
                            execution_time = end_time - start_time
                            
                            final_result = res.get("final_result", {})
                            status = final_result.get('status', 'unknown')
                            errors = res.get("errors", [])
                            error_msg = "; ".join(errors) if errors else ""
                            
                            # Log successful or handled error executions
                            failed_step = ""
                            if status in ["failed", "completed_with_errors"] and res.get("execution_steps"):
                                for step in reversed(res["execution_steps"]):
                                    if "Failed" in step or "Error" in step:
                                        failed_step = step.split(":")[0]
                                        break
                                        
                            log_workflow_execution(
                                log_file_path=log_path,
                                execution_id=exec_id,
                                workflow_id=wf_meta.workflow_id,
                                timestamp=ts,
                                status=status,
                                failed_step=failed_step,
                                error=error_msg,
                                execution_time=round(execution_time, 2),
                                slowest_step="",
                                slowest_step_sec=0.0
                            )
                            
                            st.write(f"**Result Status:** {status}")
                            st.json(final_result)
                            
                            # Formatting the final result using the LLM as a pure response formatter
                            formatter_prompt = (
                                "You are an AI assistant formatting the result of a workflow execution.\n"
                                f"Workflow Executed: {wf_meta.workflow_name}\n"
                                f"User Request: {prompt_text}\n"
                                f"Workflow Result: {json.dumps(final_result)}\n\n"
                                "Instructions:\n"
                                "1. Provide a brief natural language summary of the workflow result.\n"
                                "2. Do NOT invent or hallucinate information.\n"
                                "3. If the workflow returned errors, communicate them clearly.\n"
                                "4. NOTE: Any large datasets (lists of items) in the result will be automatically displayed to the user as an interactive table below your summary. DO NOT try to format the entire dataset in your text response. Just provide a high-level summary.\n"
                                "5. Be concise and helpful.\n"
                            )
                            
                            formatter_response = llm.invoke([("system", formatter_prompt)])
                            final_response_text = formatter_response.content
                            
                        except Exception as wf_e:
                            end_time = time.time()
                            execution_time = end_time - start_time
                            
                            # Log uncaught exceptions
                            log_workflow_execution(
                                log_file_path=log_path,
                                execution_id=exec_id,
                                workflow_id=wf_meta.workflow_id,
                                timestamp=ts,
                                status="failed",
                                failed_step="app_routing",
                                error=str(wf_e),
                                execution_time=round(execution_time, 2),
                                slowest_step="",
                                slowest_step_sec=0.0
                            )
                            
                            final_response_text = f"An error occurred while executing the workflow: {str(wf_e)}"
                            st.write(f"**Error:** {str(wf_e)}")
                
                st.markdown(final_response_text)
                
                # Extract list of dicts to display as dataframe
                dfs = {}
                if 'final_result' in locals() and isinstance(final_result, dict):
                    for key, value in final_result.items():
                        if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                            title = key.replace('_', ' ').title()
                            dfs[title] = value
                            st.write(f"**{title}**")
                            st.dataframe(value)
                
                ai_msg = AIMessage(content=final_response_text)
                if dfs:
                    ai_msg.additional_kwargs["dataframes"] = dfs
                st.session_state.messages.append(ai_msg)
                
            except Exception as e:
                st.error(f"Routing Error: {str(e)}")
