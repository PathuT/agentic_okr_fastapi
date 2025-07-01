# prompts/trend_discrepancy_prompt.py
from langchain_core.prompts import ChatPromptTemplate

trend_discrepancy_prompt = ChatPromptTemplate.from_template(
    """
You are an AI that analyzes discrepancies in OKRs.

OKR Objective: {objective}
Key Results: {key_results}

Content Metadata:
Title: {title}
Description: {description}

Trend Analysis:
Trend Score: {trend_score}
Summary: {trend_summary}

Based on the above, identify if there are discrepancies such as:
- Misalignment with objective/key results
- Low trend relevance (trend score < 60)
- Missing or incomplete data

Provide a structured JSON output with:
- discrepancy_found (true/false)
- issues (list of strings)
- suggestions (list of corrective actions)
"""
)
