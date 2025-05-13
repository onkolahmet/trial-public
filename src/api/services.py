from src.api.dependencies import db_service, evaluator
from src.api.models import EvaluationRequest, Evaluation
from typing import Dict, Any
import uuid

def evaluate_single_suggestion(evaluation_req: EvaluationRequest) -> Evaluation:
    """Evaluate a single suggestion"""
    request_id = str(uuid.uuid4())
    request_dict = evaluation_req.request.dict()
    response_dict = evaluation_req.response.dict()

    evaluation_result = evaluator.evaluate(request_dict, response_dict)
    
    db_service.store_evaluation(
        request_id,
        request_dict,
        response_dict,
        evaluation_result
    )
    
    return {
        "request_id": request_id,
        "evaluation": evaluation_result
    }

def get_all_evaluations() -> Dict[str, Any]:
    """Get all evaluations from database"""
    evaluations = db_service.get_all_evaluations()
    formatted_evaluations = []
    
    for eval in evaluations:
        formatted_eval = {
            "id": eval["id"],
            "request_id": eval["request_id"],
            "compliance_score": eval["compliance_score"],
            "minimal_edits_score": eval["minimal_edits_score"],
            "example_usage_score": eval["example_usage_score"],
            "overall_score": eval["overall_score"],
            "created_at": eval["created_at"]
        }
        formatted_evaluations.append(formatted_eval)
    
    return {"evaluations": formatted_evaluations}

def get_evaluation_by_id(evaluation_id: int) -> Dict[str, Any]:
    """Get evaluation by ID"""
    evaluation = db_service.get_evaluation(evaluation_id)
    if not evaluation:
        raise ValueError("Evaluation not found")
    return evaluation