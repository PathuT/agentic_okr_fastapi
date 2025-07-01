from langchain_core.prompts import ChatPromptTemplate

results_compiler_prompt = ChatPromptTemplate.from_template("""
You are an OKR evaluation assistant. Based on the structured state below, compile a clear and professional evaluation report for the user.

State:
- Objective: {objective}
- Key Results: {key_results}
- Metadata Title: {title}
- Metadata Description: {description}
- Trend Score: {trend_score}
- Content Exists: {content_exists}
- Scores: Relevance={relevance_score}, Credibility={credibility_score}, Completeness={completeness_score}
- Discrepancy Report:
{discrepancy_report}

Instructions:
1. Summarize the content in 2 sentences.
2. Confirm if content exists (True/False).
3. Present the AI scores (relevance, credibility, completeness) and compute total out of 100.
4. Offer 3–5 recommendations for improvement based on discrepancy report.
5. Write a detailed feedback paragraph (4–5 lines) using a professional tone.

Respond strictly in valid JSON format with the following keys:
- content_summary: string
- content_exists: boolean
- ai_scores: object with keys "relevance", "credibility", "completeness", and "total"
- recommendations: list of 3–5 strings
- detailed_feedback: string
""")
