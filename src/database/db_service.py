import sqlite3
import json
from datetime import datetime
import os

class DatabaseService:
    def __init__(self, db_path="evaluations.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the database with required tables"""
        # Create directory if it doesn't exist
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create evaluations table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT,
            request JSON,
            response JSON,
            compliance_score REAL,
            minimal_edits_score REAL,
            example_usage_score REAL,
            overall_score REAL,
            created_at TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_evaluation(self, request_id, request, response, evaluation_result):
        """Store an evaluation in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if this request_id already exists
            cursor.execute("SELECT request_id FROM evaluations WHERE request_id = ?", (request_id,))
            existing = cursor.fetchone()
            
            # Ensure request and response are properly formatted
            if isinstance(request, str):
                try:
                    request = json.loads(request)
                except:
                    pass  # Keep as string if not valid JSON
            
            if isinstance(response, str):
                try:
                    response = json.loads(response)
                except:
                    pass  # Keep as string if not valid JSON
            
            # Serialize to JSON for storage
            request_json = json.dumps(request)
            response_json = json.dumps(response)
            
            if existing:
                # Update existing record
                cursor.execute('''
                UPDATE evaluations SET
                    request = ?,
                    response = ?,
                    compliance_score = ?,
                    minimal_edits_score = ?,
                    example_usage_score = ?,
                    overall_score = ?,
                    created_at = ?
                WHERE request_id = ?
                ''', (
                    request_json,
                    response_json,
                    evaluation_result.get("compliance_score", 0.0),
                    evaluation_result.get("minimal_edits_score", 0.0),
                    evaluation_result.get("example_usage_score", 0.0),
                    evaluation_result.get("overall_score", 0.0),
                    datetime.now().isoformat(),
                    request_id
                ))
                
                row_id = existing[0]
                print(f"Updated existing evaluation with file ID {request_id}")
            else:
                # Insert new record
                cursor.execute('''
                INSERT INTO evaluations (
                    request_id, request, response, 
                    compliance_score, minimal_edits_score, example_usage_score, 
                    overall_score, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    request_id,
                    request_json,
                    response_json,
                    evaluation_result.get("compliance_score", 0.0),
                    evaluation_result.get("minimal_edits_score", 0.0),
                    evaluation_result.get("example_usage_score", 0.0),
                    evaluation_result.get("overall_score", 0.0),
                    datetime.now().isoformat()
                ))
                
                row_id = cursor.lastrowid
                print(f"Created new evaluation with file ID {request_id}")
            
            conn.commit()
            return row_id
        
        except Exception as e:
            print(f"Error in store_evaluation: {e}")
            conn.rollback()
            return None
        
        finally:
            conn.close()
        
    def get_evaluation(self, evaluation_id):
        """Retrieve an evaluation by ID with properly parsed JSON"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM evaluations WHERE id = ?
        ''', (evaluation_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            result_dict = dict(result)
            # Parse JSON strings back to Python objects
            try:
                result_dict["request"] = json.loads(result_dict["request"])
                result_dict["response"] = json.loads(result_dict["response"])
            except Exception as e:
                print(f"Error parsing JSON from database: {e}")
            return result_dict
        return None
    
    def get_all_evaluations(self):
        """Retrieve all evaluations ranked by overall_score in ascending order with properly parsed JSON"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM evaluations ORDER BY id DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        formatted_results = []
        for row in results:
            result_dict = dict(row)
            try:
                result_dict["request"] = json.loads(result_dict["request"])
                result_dict["response"] = json.loads(result_dict["response"])
            except Exception as e:
                print(f"Error parsing JSON from database: {e}")
            formatted_results.append(result_dict)
        
        return formatted_results
