import ollama, json, re

class LLMService:
    def __init__(self, model_name="llama3:8b", timeout=120):
        self.model_name = model_name
        self.timeout = timeout
        
        # Ensure model is available
        self._ensure_model_available()
    
    def _ensure_model_available(self):
        """Ensure the model is available locally"""
        try:
            # List models to see if our model is available
            models = ollama.list()
            model_names = [m.get('name') for m in models.get('models', [])]
            
            if self.model_name not in model_names:
                print(f"Model {self.model_name} not found locally. Pulling it now...")
                ollama.pull(self.model_name)
        except Exception as e:
            print(f"Warning: Could not verify model availability: {e}")
            print(f"Attempting to use {self.model_name} anyway.")
    
    def evaluate_suggestion(self, request, response, evaluation_prompt):
        """Use the LLM to evaluate a suggestion"""
        # Construct the prompt for evaluation
        prompt = self._construct_evaluation_prompt(request, response, evaluation_prompt)
        
        try:
            # Get model response
            result = ollama.generate(
                model=self.model_name, 
                prompt=prompt,
                options={
                    "num_predict": 512,     
                    "temperature": 0.1,     
                    "top_p": 0.9,           
                    "repeat_penalty": 1.2,  
                    "num_thread": 4
                }
            )
            
            return self._parse_evaluation_result(result.get('response', ''))
        except Exception as e:
            print(f"Error during model evaluation: {e}")
            # Return default values if model fails
            return {
                "compliance_score": 0.0,
                "minimal_edits_score": 0.0,
                "example_usage_score": 0.0,
                "overall_score": 0.0
            }
    
    def _construct_evaluation_prompt(self, request, response, evaluation_prompt):
        """Format the prompt for the LLM"""
        # Extract relevant fields from request and response
        rule = request.get("rule", "No rule provided")
        explanation = request.get("explanation", "No explanation provided")
        example_language = request.get("exampleLanguage", "No example language provided")
        original_texts = response.get("originalTexts", ["No original texts provided"])
        suggestions = response.get("suggestions", ["No suggestions provided"])
        
        # Format original texts and suggestions for the prompt
        original_texts_str = "\n".join([f"Text {i+1}: {text}" for i, text in enumerate(original_texts)])
        suggestions_str = "\n".join([f"Suggestion {i+1}: {suggestion}" for i, suggestion in enumerate(suggestions)])
        
        # Format the prompt
        return evaluation_prompt.format(
            rule=rule,
            explanation=explanation,
            example_language=example_language,
            original_texts=original_texts_str,
            suggestions=suggestions_str
        )
    
    def _parse_evaluation_result(self, result_text):
        """Parse the LLM output into structured evaluation metrics with better error handling"""
        # First, try to extract JSON directly
        try:
            # Look for JSON patterns in the text
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                json_str = json_match.group(0)
                
                # Clean up the JSON string - remove comments and any trailing commas
                # This handles cases where the model includes comments after values
                clean_json = re.sub(r'//.*?(\n|$)', '', json_str)  # Remove // comments
                clean_json = re.sub(r'/\*.*?\*/', '', clean_json, flags=re.DOTALL)  # Remove /* */ comments
                clean_json = re.sub(r',(\s*[}\]])', r'\1', clean_json)  # Fix trailing commas

                clean_json = re.sub(r"(?<!\\)'", '"', clean_json)  # Replace unescaped single quotes with double quotes
                # Try to parse the cleaned JSON
                try:
                    result_dict = json.loads(clean_json)
                    return self._validate_evaluation_result(result_dict)
                except json.JSONDecodeError as e:
                    print(f"Error parsing cleaned JSON: {e}")
                    print(f"Cleaned JSON: {clean_json}")
                    # Fall through to the manual parsing logic
        except Exception as e:
            print(f"JSON extraction failed: {e}")
        
        # If JSON parsing fails, try to extract scores using regex
        print("Falling back to regex extraction for evaluation results")
        scores = {}
        
        score_patterns = {
            "compliance_score": r'compliance_score"?\s*:\s*(\d+(?:\.\d+)?)',
            "minimal_edits_score": r'minimal_edits_score"?\s*:\s*(\d+(?:\.\d+)?)',
            "example_usage_score": r'example_usage_score"?\s*:\s*(\d+(?:\.\d+)?)',
            "overall_score": r'overall_score"?\s*:\s*(\d+(?:\.\d+)?)'
        }
        
        # Extract scores
        for key, pattern in score_patterns.items():
            match = re.search(pattern, result_text, re.IGNORECASE | re.DOTALL)
            if match:
                try:
                    scores[key] = float(match.group(1))
                except:
                    scores[key] = 0.0
            else:
                scores[key] = 0.0
        
        
        return self._validate_evaluation_result(scores)


    def _validate_evaluation_result(self, result_dict):
        """Validate and ensure all required fields are present in the evaluation result"""
        # Ensure all required fields are present
        required_fields = [
            "compliance_score", 
            "minimal_edits_score",
            "example_usage_score",
            "overall_score"
        ]
                        
        
        # Ensure scores are numeric and within range
        for field in required_fields:
            try:
                result_dict[field] = float(result_dict[field])
                # Clamp to 0-10 range
                result_dict[field] = max(0.0, min(10.0, result_dict[field]))
            except (ValueError, TypeError):
                result_dict[field] = 0.0
        
        return result_dict