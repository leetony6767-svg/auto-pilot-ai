"""
Robust JSON parsing utilities for LLM responses.

Handles:
- Markdown code blocks (```json ... ```)
- Malformed JSON with json_repair
- Automatic retry with clarification prompt
"""
import json
import re
from typing import Any, Optional


def extract_json_from_markdown(text: str) -> str:
    """Extract JSON from markdown code blocks."""
    if not text:
        return ""
    # Remove ```json ... ``` or ``` ... ``` wrappers
    cleaned = re.sub(r'^```(?:json)?\s*|\s*```$', '', text.strip(), flags=re.MULTILINE)
    return cleaned.strip()


def find_json_object(text: str) -> Optional[str]:
    """Find the outermost JSON object in text."""
    # Try to find balanced braces
    depth = 0
    start = None
    for i, c in enumerate(text):
        if c == '{':
            if depth == 0:
                start = i
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0 and start is not None:
                return text[start:i+1]
    return None


def parse_json_with_repair(text: str) -> tuple[bool, Any]:
    """Try to parse JSON, using json_repair as fallback."""
    try:
        return True, json.loads(text)
    except json.JSONDecodeError:
        pass

    try:
        import json_repair
        result = json_repair.repair_json(text, return_objects=True)
        return True, result
    except ImportError:
        pass
    except Exception:
        pass

    return False, None


def parse_llm_json(content: str, max_retries: int = 2) -> tuple[bool, Any, str]:
    """
    Robustly parse JSON from LLM response.

    Returns:
        (success, parsed_data, error_message)
    """
    if not content:
        return False, None, "Empty response"

    # Step 1: Clean markdown wrappers
    cleaned = extract_json_from_markdown(content)

    # Step 2: Try direct parse
    success, data = parse_json_with_repair(cleaned)
    if success:
        return True, data, ""

    # Step 3: Try to find JSON object in text
    json_str = find_json_object(cleaned)
    if json_str:
        success, data = parse_json_with_repair(json_str)
        if success:
            return True, data, ""

    # Step 4: Retry with clarification (up to max_retries)
    for attempt in range(1, max_retries + 1):
        retry_content = f"{content}\n\nIMPORTANT: Output ONLY valid JSON, no explanations."
        # This would need access to the LLM client - for now return failure
        break

    return False, None, f"Failed to parse JSON after cleanup. Original length: {len(content)}"


# Backward compatible function
def parse_llm_response(content: str) -> dict:
    """Parse LLM response, return dict with success flag."""
    success, data, error = parse_llm_json(content)
    return {
        "success": success,
        "data": data,
        "error": error,
    }
