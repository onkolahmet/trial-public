from src.api.dependencies import db_service, evaluator
from typing import List, Dict, Any

def process_batch_evaluation(pairs: List[Dict[str, Any]]):
    """Process batch evaluation in the background"""
    for i, pair in enumerate(pairs):
        try:
            uuid = pair["uuid"]
            request_dict = pair["request"]
            response_dict = pair["response"]

            evaluation_result = evaluator.evaluate(request_dict, response_dict)
            
            db_service.store_evaluation(
                uuid,
                request_dict,
                response_dict,
                evaluation_result
            )
            
            print(f"Processed pair {i+1}/{len(pairs)}")
        except Exception as e:
            print(f"Error processing pair {i+1}: {e}")