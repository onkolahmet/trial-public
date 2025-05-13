from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class PrecedentId(BaseModel):
    id: str

class SuggestionRequest(BaseModel):
    precedentId: List[PrecedentId]
    explanation: str
    rule: Optional[str] = None
    exampleLanguage: Optional[str] = None

class SuggestionResponse(BaseModel):
    suggestions: List[str]
    originalTexts: Optional[List[str]] = None

class EvaluationRequest(BaseModel):
    request: SuggestionRequest
    response: SuggestionResponse

class Evaluation(BaseModel):
    request_id: str
    evaluation: Dict[str, Any]