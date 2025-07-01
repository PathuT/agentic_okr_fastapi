from langchain_core.tools import tool
from typing import List, Optional, Dict, Any
import httpx
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tavily API configuration
TAVILY_API_URL = "https://api.tavily.com/search"  # Verify this is correct
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

@tool()
async def tavily_trend_check_tool(
    keywords: List[str], 
    timeframe: str = "month",
    region: str = "global",
    max_results: int = 10
) -> Dict[str, Any]:
    """
    Calls Tavily API with keywords and returns trend analysis data.
    
    Args:
        keywords: List of keywords to analyze trends for
        timeframe: Time period for trend analysis (day, week, month, year)
        region: Geographic region for trend analysis
        max_results: Maximum number of results to return
        
    Returns:
        Dictionary containing trend analysis results
    """
    if not TAVILY_API_KEY:
        logger.error("TAVILY_API_KEY environment variable not set")
        return {
            "success": False,
            "error": "API key not configured",
            "trend_score": 0,
            "trend_summary": "API key not available"
        }

    if not keywords:
        return {
            "success": False,
            "error": "No keywords provided",
            "trend_score": 0,
            "trend_summary": "No keywords to analyze"
        }

    query = " ".join(keywords)
    logger.info(f"Analyzing trends for keywords: {keywords}")

    headers = {
        "Authorization": f"Bearer {TAVILY_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "query": query,
        "search_depth": "advanced",
        "topic": "news",
        "max_results": max_results,
        "include_answer": True,
        "include_raw_content": False,
        # Add timeframe and region if Tavily supports them
        # "timeframe": timeframe,
        # "region": region,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            logger.info(f"Making request to Tavily API: {TAVILY_API_URL}")
            response = await client.post(TAVILY_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Process Tavily response - adjust based on actual API response format
            results = data.get("results", [])
            answer = data.get("answer", "")
            
            # Calculate a simple trend score based on result count and recency
            trend_score = min(len(results) * 10, 100)  # Cap at 100
            
            # Create trend summary
            if results:
                recent_titles = [result.get("title", "") for result in results[:3]]
                trend_summary = f"Found {len(results)} recent mentions. Recent topics: {', '.join(recent_titles[:2])}"
                if answer:
                    trend_summary += f"\n\nSummary: {answer[:200]}..."
            else:
                trend_summary = "No recent trend data found for these keywords"

            logger.info(f"Successfully analyzed trends. Score: {trend_score}")
            
            return {
                "success": True,
                "trend_score": trend_score,
                "trend_summary": trend_summary,
                "query": query,
                "results_count": len(results),
                "raw_results": results[:5],  # Include top 5 results
                "answer": answer
            }

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error from Tavily API: {e.response.status_code}"
            if e.response.status_code == 401:
                error_msg += " - Invalid API key"
            elif e.response.status_code == 429:
                error_msg += " - Rate limit exceeded"
            
            logger.error(f"{error_msg} - {e.response.text}")
            return {
                "success": False,
                "error": error_msg,
                "trend_score": 0,
                "trend_summary": "Error fetching trend data due to API error"
            }
            
        except httpx.TimeoutException:
            logger.error("Timeout occurred while calling Tavily API")
            return {
                "success": False,
                "error": "Request timeout",
                "trend_score": 0,
                "trend_summary": "Error fetching trend data due to timeout"
            }
            
        except Exception as e:
            logger.error(f"Unexpected error calling Tavily API: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "trend_score": 0,
                "trend_summary": "Error fetching trend data due to unexpected error"
            }