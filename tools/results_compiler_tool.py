import logging
import json
import re
from typing import List
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from prompts.results_compiler_prompt import results_compiler_prompt

# Logger Setup
logger = logging.getLogger("results_compiler_tool")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# LLM Setup
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
chain = results_compiler_prompt | llm

@tool
async def compile_results_tool(
    objective: str,
    key_results: List[str],
    title: str,
    description: str,
    trend_score: int,
    content_exists: bool,
    relevance_score: int,
    credibility_score: int,
    completeness_score: int,
    discrepancy_report: str,
) -> dict:
    """
    Compiles content summary, scores, and recommendations from state.
    """

    input_vars = {
        "objective": objective,
        "key_results": key_results,
        "title": title,
        "description": description,
        "trend_score": trend_score,
        "content_exists": content_exists,
        "relevance_score": relevance_score,
        "credibility_score": credibility_score,
        "completeness_score": completeness_score,
        "discrepancy_report": discrepancy_report,
    }

    logger.info("📨 Invoking Gemini with input variables:")
    logger.info(json.dumps(input_vars, indent=2))

    try:
        result = await chain.ainvoke(input_vars)
        raw_content = result.content.strip()
        logger.info("📥 Raw response:\n%s", raw_content)

        # 🧹 Clean out markdown code block if present
        if raw_content.startswith("```json"):
            raw_content = re.sub(r"^```json\s*|\s*```$", "", raw_content.strip(), flags=re.DOTALL)

        parsed = json.loads(raw_content)
        logger.info(" Successfully parsed JSON output from chain.")
        return parsed

    except Exception as e:
        logger.error("❌ Failed to parse JSON from Gemini response.")
        logger.error("Exception: %s", str(e))
        return {
            "content_summary": "Could not parse summary.",
            "content_exists": content_exists,
            "ai_scores": {
                "relevance": relevance_score,
                "credibility": credibility_score,
                "completeness": completeness_score,
                "total": relevance_score + credibility_score + completeness_score,
            },
            "recommendations": [],
            "detailed_feedback": "AI could not generate proper feedback. Try refining input."
        }