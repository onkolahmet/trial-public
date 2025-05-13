import yaml
from src.database.db_service import DatabaseService
from src.evaluation.evaluator import SuggestionEvaluator

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

config = load_config()

db_service = DatabaseService(config.get("database", {}).get("path", "evaluations.db"))
evaluator = SuggestionEvaluator("config.yaml")