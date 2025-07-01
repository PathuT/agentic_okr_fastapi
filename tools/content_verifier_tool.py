from langchain_core.tools import tool
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from prompts.content_verifier_prompt import content_verifier_prompt
from typing import Optional, Dict, Any, Literal

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
chain = content_verifier_prompt | llm | StrOutputParser()

@tool()
async def content_verifier_tool(
    input_url: str,
    metadata: Optional[Dict[str, Any]] = None,
    duplicate_check_result: Optional[Literal["pass", "fail"]] = None,
) -> dict:
    """
    Evaluates content quality by scoring relevance, credibility, and completeness 
    based on the provided title and metadata.
    """
    state_dict = {
        "input_url": input_url,
        "metadata": metadata,
        "duplicate_check_result": duplicate_check_result,
    }

    try:
        if duplicate_check_result != "pass":
            state_dict["content_verification_result"] = "skipped"
            return state_dict

        title = metadata.get("title", "") if metadata else ""
        description = metadata.get("meta_description", "") if metadata else ""

        if not title or not description:
            state_dict["content_verification_result"] = "missing_title_or_description"
            return state_dict

        result = await chain.ainvoke({
            "title": title,
            "meta_description": description
        })

        state_dict["content_verification_result"] = result.strip()
        return state_dict

    except Exception as e:
        print(f"❌ Error in content_verifier: {e}")
        state_dict["content_verification_result"] = "error"
        return state_dict
