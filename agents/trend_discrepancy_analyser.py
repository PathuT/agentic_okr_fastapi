# agents/trend_discrepancy_analyzer.py
from langchain_google_genai import ChatGoogleGenerativeAI
from prompts.trend_discrepancy_prompt import trend_discrepancy_prompt
from tools.trend_analyzer_tool import tavily_trend_check_tool

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
chain = trend_discrepancy_prompt | llm

async def run_trend_discrepancy_analyzer(state: dict) -> dict:
    """
    1. Extract keywords from OKR or metadata
    2. Call Tavily tool to get trend data
    3. Call LLM with trend + OKR info to find discrepancies
    4. Return updated state with discrepancy report
    """
    objective = state.get("parsed_okr", {}).get("objective", "")
    key_results = state.get("parsed_okr", {}).get("key_results", [])
    metadata = state.get("metadata", {})
    title = metadata.get("title", "")
    description = metadata.get("meta_description", "")

    # Step 1: Extract keywords for trend check (simple example: split objective)
    keywords = objective.split()[:10]  # limit to 10 keywords for example

    # Step 2: Call Tavily tool
    trend_data = await tavily_trend_check_tool.ainvoke({"keywords": keywords})


    # Step 3: Call LLM with all data
    input_vars = {
        "objective": objective,
        "key_results": key_results,
        "title": title,
        "description": description,
        "trend_score": trend_data["trend_score"],
        "trend_summary": trend_data["trend_summary"],
    }

    discrepancy_report = await chain.ainvoke(input_vars)

    # Step 4: Update state with discrepancy report (raw string or parsed JSON)
    state["discrepancy_report"] = discrepancy_report.content.strip()
    state["trend_score"] = trend_data.get("trend_score", 0)
    state["trend_summary"] = trend_data.get("trend_summary", "")
    return state
