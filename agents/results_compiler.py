from tools.results_compiler_tool import compile_results_tool
import json
import re
from db.mongo_client import results_collection
from datetime import datetime

async def run_results_compiler(state: dict) -> dict:
    objective = state.get("parsed_okr", {}).get("objective", "")
    key_results = state.get("parsed_okr", {}).get("key_results", [])
    metadata = state.get("metadata", {})
    title = metadata.get("title", "")
    description = metadata.get("meta_description", "")
    trend_score = state.get("trend_score", 0)
    discrepancy_report = state.get("discrepancy_report", "")
    
    content_exists = bool(description and len(description.strip()) > 30)

    # Parse scores from content_verification_result
    verification_str = state.get("content_verification_result", "")
    try:
        # Extract the first JSON block inside triple backticks
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", verification_str, flags=re.DOTALL)
        if json_match:
            clean_json = json_match.group(1)
            verification_data = json.loads(clean_json)
        else:
            # fallback if no markdown found but raw JSON present
            json_inline = re.search(r"\{.*?\}", verification_str, flags=re.DOTALL)
            if json_inline:
                verification_data = json.loads(json_inline.group(0))
            else:
                verification_data = {}

        relevance = int(verification_data.get("relevance", 0))
        credibility = int(verification_data.get("credibility", 0))
        completeness = int(verification_data.get("completeness", 0))

    except Exception as e:
        print(f"❌ Failed to parse verification JSON: {e}")
        relevance, credibility, completeness = 0, 0, 0

    tool_input = {
        "objective": objective,
        "key_results": key_results,
        "title": title,
        "description": description,
        "trend_score": trend_score,
        "content_exists": content_exists,
        "relevance_score": relevance,
        "credibility_score": credibility,
        "completeness_score": completeness,
        "discrepancy_report": discrepancy_report,
    }

    compiled_result = await compile_results_tool.ainvoke(tool_input)

    document = {
        "timestamp": datetime.utcnow(),
        "input_url": state.get("input_url", ""),
        "objective": objective,
        "key_results": key_results,
        "metadata": metadata,
        "trend_score": trend_score,
        "content_exists": content_exists,
        "scores": {
            "relevance": relevance,
            "credibility": credibility,
            "completeness": completeness,
        },
        "discrepancy_report": discrepancy_report,
        "compiled_result": compiled_result,
    }

    await results_collection.insert_one(document)

    state["compiled_results"] = compiled_result
    return state
