import sys
import os
import json

sys.path.insert(0, os.path.abspath("."))

def load_env_file(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env_file('.env.local')
load_env_file('.env')

from src.features.product_analysis.domain.product_request import validate_product_request
from src.features.product_analysis.application.product_analysis_use_case import ProductAnalysisUseCase

def main():
    print("--- Starting REAL E2E Product Analysis Test ---")
    base_dir = os.path.abspath(".")
    
    raw_request = {
        "productName": "Ashwagandha Wellness Tablet",
        "category": "Ayurveda-Aahar",
        "form": "Tablet",
        "description": "Standardized herbal tablet formulation intended for general wellness, using traditional processing methods.",
        "ingredients": [
            {"name": "Ashwagandha (Withania somnifera)", "quantity": "500", "unit": "mg"},
            {"name": "Pippali (Piper longum)", "quantity": "50", "unit": "mg"},
            {"name": "Black Pepper", "quantity": "25", "unit": "mg"}
        ],
        "jurisdiction": "India"
    }

    req = validate_product_request(raw_request)
    use_case = ProductAnalysisUseCase(base_dir=base_dir)

    original_complete = use_case._get_llm().complete
    def debug_complete(system_prompt, user_prompt, max_tokens=4000, **kwargs):
        print(f"Calling OpenRouter with max_tokens={max_tokens}, kwargs={kwargs}...")
        res = original_complete(system_prompt, user_prompt, max_tokens=max_tokens, **kwargs)
        with open("scratch/raw_llm_response.txt", "w", encoding="utf-8") as f:
            f.write(res)
        print("Raw LLM response saved to scratch/raw_llm_response.txt")
        return res
        
    use_case._get_llm().complete = debug_complete

    result = use_case.execute(req)
    
    with open("scratch/analysis_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        
    print("Execution completed successfully.")

if __name__ == "__main__":
    main()
