from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from src.api.models import EvaluationRequest, Evaluation
from src.api.services import (
    evaluate_single_suggestion,
    get_all_evaluations,
    get_evaluation_by_id
)
from src.api.tasks import process_batch_evaluation
from src.utils.file_utils import get_suggestion_pairs
app = FastAPI(title="Legal Contract Suggestion Evaluator")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/evaluate", response_model=Evaluation)
async def evaluate_suggestion(evaluation_req: EvaluationRequest):
    """Evaluate a suggestion based on request and response"""
    return evaluate_single_suggestion(evaluation_req)

@app.post("/evaluate/batch")
async def evaluate_batch(background_tasks: BackgroundTasks):
    """Evaluate all suggestion pairs in the data directory"""
    pairs = get_suggestion_pairs()
    
    if not pairs:
        raise HTTPException(status_code=404, detail="No suggestion pairs found")

    background_tasks.add_task(process_batch_evaluation, pairs)
    
    return {
        "message": f"Batch evaluation of {len(pairs)} pairs started in the background",
        "status": "processing",
        "next_steps": [
            "Processing may take several minutes to complete",
            "Check server logs for progress updates",
            "Use GET /evaluations to view results as they become available",
            f"Estimated completion time: ~{len(pairs) * 3 // 60 + 1} minutes"
        ],
        "total_pairs": len(pairs)
    }

@app.get("/evaluations")
async def get_evaluations():
    """Get all evaluations from the database"""
    return get_all_evaluations()

@app.get("/evaluations/{evaluation_id}")
async def get_evaluation(evaluation_id: int):
    """Get a specific evaluation by ID with request and reponse"""
    try:
        return get_evaluation_by_id(evaluation_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))