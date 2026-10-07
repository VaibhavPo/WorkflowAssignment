import os
import json
import csv
from typing import Any, Dict, List, Optional

try:
    import openpyxl
except ImportError:
    openpyxl = None


def generate_output(
    workflow_id: str,
    workflow_name: str,
    executed_steps: List[str],
    result_data: Any,
    warnings: Optional[List[str]] = None,
    errors: Optional[List[str]] = None,
    output_format: str = "text",
    output_dir: str = ".",
    output_filename: Optional[str] = None
) -> str:
    """
    Convert workflow results into clean, user-facing outputs and optionally save them to a file.
    
    Args:
        workflow_id (str): ID of the workflow (e.g. 'WF003')
        workflow_name (str): Name of the workflow
        executed_steps (List[str]): List of steps that were executed
        result_data (Any): The output data of the workflow
        warnings (Optional[List[str]]): Optional list of warnings encountered
        errors (Optional[List[str]]): Optional list of errors encountered
        output_format (str): Desired output format ('text', 'json', 'csv', 'xlsx')
        output_dir (str): Directory to save the output file
        output_filename (Optional[str]): Specific filename. If not provided, it defaults to {workflow_id}_output.{format}
        
    Returns:
        str: A human-readable string containing the formatted workflow summary and file reference.
        
    Examples:
        >>> generate_output(
        ...     workflow_id="WF003",
        ...     workflow_name="Data Validation",
        ...     executed_steps=["Load CSV", "Validate Rows"],
        ...     result_data=[{"row": 1, "status": "valid"}],
        ...     output_format="csv"
        ... )
    """
    if warnings is None:
        warnings = []
    if errors is None:
        errors = []

    valid_formats = {"text", "json", "csv", "xlsx"}
    if output_format not in valid_formats:
        return f"Error: Invalid output format '{output_format}'. Must be one of {valid_formats}."

    if output_format == "xlsx" and openpyxl is None:
        return "Error: openpyxl is not installed. Cannot write XLSX files."

    # Format human readable summary
    steps_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(executed_steps))
    
    if result_data is None:
        result_str = "No result data produced."
    elif isinstance(result_data, (dict, list)):
        try:
            result_str = json.dumps(result_data, indent=2)
        except TypeError:
            result_str = str(result_data)
    else:
        result_str = str(result_data)

    text_output = (
        f"Selected Workflow:\n{workflow_id} - {workflow_name}\n\n"
        f"Steps Executed:\n{steps_str}\n\n"
    )

    if warnings:
        text_output += "Warnings:\n" + "\n".join(f"- {w}" for w in warnings) + "\n\n"
    if errors:
        text_output += "Errors:\n" + "\n".join(f"- {e}" for e in errors) + "\n\n"
    
    text_output += f"Result:\n{result_str}\n"

    # Persist file
    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        return f"{text_output}\n\nFile Write Error: Could not create output directory: {e}"
    
    if output_filename is None:
        output_filename = f"{workflow_id}_output.{output_format}"
    
    file_path = os.path.join(output_dir, output_filename)
    
    try:
        if output_format == "text":
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text_output)
                
        elif output_format == "json":
            payload = {
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "steps_executed": executed_steps,
                "warnings": warnings,
                "errors": errors,
                "result": result_data
            }
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(payload, f, indent=2)
            except TypeError as e:
                return f"{text_output}\n\nFile Write Error: Could not serialize result_data to JSON. ({e})"
                
        elif output_format == "csv":
            if not isinstance(result_data, list):
                return f"{text_output}\n\nFile Write Error: result_data must be a list of dictionaries to output as CSV."
            if len(result_data) > 0 and not isinstance(result_data[0], dict):
                return f"{text_output}\n\nFile Write Error: result_data must be a list of dictionaries to output as CSV."
            
            with open(file_path, "w", encoding="utf-8", newline="") as f:
                if len(result_data) > 0:
                    writer = csv.DictWriter(f, fieldnames=result_data[0].keys())
                    writer.writeheader()
                    writer.writerows(result_data)
                else:
                    f.write("No data\n")
                    
        elif output_format == "xlsx":
            if not isinstance(result_data, list):
                return f"{text_output}\n\nFile Write Error: result_data must be a list of dictionaries to output as XLSX."
            if len(result_data) > 0 and not isinstance(result_data[0], dict):
                return f"{text_output}\n\nFile Write Error: result_data must be a list of dictionaries to output as XLSX."
            
            wb = openpyxl.Workbook()
            ws = wb.active
            if len(result_data) > 0:
                headers = list(result_data[0].keys())
                ws.append(headers)
                for row in result_data:
                    ws.append([row.get(h) for h in headers])
            else:
                ws.append(["No data"])
            wb.save(file_path)

        text_output += f"\nFile successfully generated at: {file_path}"
        
    except Exception as e:
        text_output += f"\n\nFile Write Error: An error occurred while writing the file: {e}"

    return text_output
