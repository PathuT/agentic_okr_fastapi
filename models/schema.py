from typing import TypedDict, Optional, Literal, Dict, Any
from pydantic import BaseModel

class OKRParserState(TypedDict, total=False):
    input_url: str
    parsed_okr: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    title: Optional[str]
    duplicate_check_result: Optional[Literal["pass", "fail"]]
    content_verification_result: Optional[str]
    credibility_score: Optional[float]
    relevance_score: Optional[float]
    completeness_score: Optional[float]
    final_verdict: Optional[Literal["pass", "fail"]]
    discrepancy_report: Optional[str]
    trend_score: Optional[float]
    trend_summary: Optional[str]
    compiled_results: Optional[Dict[str, Any]]

class ContentVerifierInput(BaseModel):
    input_url: str
    metadata: Optional[Dict[str, Any]] = None
    duplicate_check_result: Optional[Literal["pass", "fail"]] = None
