from tools.content_verifier_tool import content_verifier_tool

async def run_content_verifier_agent(state: dict) -> dict:
    """
    Agent wrapper: extracts fields from state, calls the tool with a dict, merges output back.
    """
    tool_result = await content_verifier_tool.ainvoke({
        "input_url": state.get("input_url", ""),
        "metadata": state.get("metadata"),
        "duplicate_check_result": state.get("duplicate_check_result"),
    })

    # Merge tool output keys back into the full state
    state.update(tool_result)
    return state
