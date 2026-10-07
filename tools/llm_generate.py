import os
import json
import requests
from typing import Dict, Any, Optional, Union

def llm_generate(
    task: str,
    instructions: str,
    input_data: Union[Dict[str, Any], str],
    output_schema: Dict[str, Any],
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate or classify data using a generic LLM interface.

    Args:
        task: The high-level task description.
        instructions: Detailed instructions for the LLM.
        input_data: The input data to process.
        output_schema: A JSON schema dict defining the expected output format.
        model: The LLM model to use. Defaults to GROK_MODEL env var or 'grok-beta'.

    Returns:
        Structured data matching the output_schema, or a structured error dictionary.
    """
    api_key = os.environ.get("LLM_API_KEY")
    api_url = os.environ.get("LLM_API_URL", "https://api.xai.com/v1/chat/completions")
    selected_model = model or os.environ.get("LLM_MODEL", "grok-beta")

    if not api_key:
        return {
            "error": "Configuration Error",
            "message": "LLM_API_KEY environment variable is missing.",
            "status_code": None
        }

    # Construct the prompt
    system_prompt = (
        f"You are a helpful assistant. Your task is: {task}\n"
        f"Instructions: {instructions}\n"
        f"You must return the result as a valid JSON object matching this JSON schema:\n"
        f"{json.dumps(output_schema, indent=2)}\n"
        "Do not include any markdown formatting like ```json or any other text before or after the JSON."
    )
    
    user_prompt = f"Input Data:\n{json.dumps(input_data, indent=2) if isinstance(input_data, dict) else input_data}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": selected_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]
        
        # Attempt to clean markdown if model hallucinated it
        content_clean = content.strip()
        if content_clean.startswith("```json"):
            content_clean = content_clean[7:]
        if content_clean.endswith("```"):
            content_clean = content_clean[:-3]
        content_clean = content_clean.strip()
        
        result = json.loads(content_clean)
        return result
        
    except requests.exceptions.RequestException as e:
        status_code = e.response.status_code if getattr(e, 'response', None) is not None else None
        return {
            "error": "API Error",
            "message": str(e),
            "status_code": status_code
        }
    except json.JSONDecodeError as e:
        return {
            "error": "Malformed Response",
            "message": f"Failed to parse LLM response as JSON: {str(e)}",
            "raw_content": content if 'content' in locals() else None,
            "status_code": 200
        }
    except Exception as e:
        return {
            "error": "Unexpected Error",
            "message": str(e),
            "status_code": None
        }

if __name__ == "__main__":
    # Small local testing snippet
    task = "Keyword Classification"
    instructions = "Classify the given keyword into one of the types."
    input_data = "buy cheap running shoes"
    output_schema = {
        "type": "object",
        "properties": {
            "keyword": {"type": "string"},
            "intent": {"type": "string", "enum": ["informational", "commercial", "transactional", "navigational"]}
        },
        "required": ["keyword", "intent"]
    }
    
    print("Testing missing config:", llm_generate(task, instructions, input_data, output_schema))
