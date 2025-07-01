from langchain_core.prompts import ChatPromptTemplate

content_verifier_prompt = ChatPromptTemplate.from_template(
    """You are a content evaluation agent.
Given the following title and metadata:

TITLE: "{title}"
METADATA: "{meta_description}"

Evaluate based on the following:

1. Relevance to professional OKRs or career development (40 points)
2. Credibility of source and quality of content (30 points)
3. Completeness of the description and context (30 points)

Return your output in this format:
{{
  "relevance": <score_out_of_50>,
  "credibility": <score_out_of_30>,
  "completeness": <score_out_of_20>,
  "verdict": "pass" or "fail" (if total < 60/100, fail)
}}"""
)
