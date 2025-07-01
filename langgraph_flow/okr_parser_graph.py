from langgraph.graph import StateGraph
from agents.okr_parser import run_parser_agent
from agents.duplicate_checker import run_duplicate_checker
from agents.content_verifier import run_content_verifier_agent
from agents.trend_discrepancy_analyser import run_trend_discrepancy_analyzer
from agents.results_compiler import run_results_compiler 
from models.schema import OKRParserState

def build_okr_parser_graph():
    workflow = StateGraph(OKRParserState)

    # Nodes
    workflow.add_node("OKRParser", run_parser_agent)
    workflow.add_node("DuplicateChecker", run_duplicate_checker)
    workflow.add_node("ContentVerifier", run_content_verifier_agent)
    workflow.add_node("TrendDiscrepancyAnalyzer", run_trend_discrepancy_analyzer)
    workflow.add_node("ResultsCompiler", run_results_compiler)

    # Edges
    workflow.set_entry_point("OKRParser")
    workflow.add_edge("OKRParser", "DuplicateChecker")
    workflow.add_edge("DuplicateChecker", "ContentVerifier")
    workflow.add_edge("ContentVerifier", "TrendDiscrepancyAnalyzer")
    workflow.add_edge("TrendDiscrepancyAnalyzer", "ResultsCompiler") 
    workflow.set_finish_point("ResultsCompiler")  

    return workflow.compile()
