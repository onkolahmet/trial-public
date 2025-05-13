import os
import yaml
from src.models.llm_service import LLMService

class SuggestionEvaluator:
    def __init__(self, config_path="config.yaml"):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize LLM service
        model_name = self.config.get('model', {}).get('name', 'llama3:8b')
        timeout = self.config.get('model', {}).get('timeout', 120)
        self.llm_service = LLMService(model_name, timeout)
        
        # Load evaluation weights
        self.weights = self.config.get('evaluation', {}).get('weights', {
            'compliance': 0.4,
            'minimal_edits': 0.3,
            'example_usage': 0.3
        })
        
        # Load evaluation prompt template
        prompt_path = os.path.join('src', 'evaluation', 'prompt_templates', 'evaluation_prompt.txt')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.evaluation_prompt = f.read()
    
    def evaluate(self, request, response):
        """Evaluate a suggestion using both LLM and automated metrics"""
        # Get LLM evaluation
        llm_evaluation = self.llm_service.evaluate_suggestion(
            request, response, self.evaluation_prompt
        )

        # Combine evaluations (prefer LLM evaluation, but fall back to automated metrics if needed)
        final_evaluation = llm_evaluation.copy()
        
        # Weight overall score
        weighted_scores = [
            final_evaluation.get("compliance_score", 0) * self.weights.get('compliance', 0.4),
            final_evaluation.get("minimal_edits_score", 0) * self.weights.get('minimal_edits', 0.3),
            final_evaluation.get("example_usage_score", 0) * self.weights.get('example_usage', 0.3)
        ]
        
        final_evaluation["overall_score"] = sum(weighted_scores)

        print(final_evaluation)
        
        return final_evaluation
