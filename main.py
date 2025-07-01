from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
from bson import ObjectId

from langgraph_flow.okr_parser_graph import build_okr_parser_graph
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

# CORS configuration to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the OKR parser LangGraph
graph = build_okr_parser_graph()

# MongoDB connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["okr_database"]
results_collection = db["compiled_results"]

# Utility to convert MongoDB ObjectId to string
def fix_object_id(doc):
    doc["_id"] = str(doc["_id"])
    return doc

# Existing OKR Parser API
@app.get("/parse-okr/")
async def parse_okr(url: str = Query(...)):
    initial_state = {
        "input_url": url,
        "parsed_okr": None,
        "metadata": None
    }
    result = await graph.ainvoke(initial_state)
    return result

# Fetch all compiled OKR results for dashboard
@app.get("/dashboard/results", response_model=List[dict])
async def get_all_compiled_results():
    try:
        cursor = results_collection.find({})
        results = await cursor.to_list(length=None)
        return [fix_object_id(doc) for doc in results]
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
