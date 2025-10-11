import json
import sys
import os
from server.worker.main import process_pr

if __name__ == "__main__":
    data_file = sys.argv[1] if len(sys.argv) > 1 else "/app/pr_data.json"
    output_dir = "/app/results"  # Changed to match Docker mount
    os.makedirs(output_dir, exist_ok=True)

    with open(data_file, "r") as f:
        pr_data = json.load(f)

    try:
        result = process_pr(pr_data)  
        
        # Optionally save result to output_dir
        result_file = os.path.join(output_dir, f"result_{pr_data.get('pr_number', 'unknown')}.json")
        with open(result_file, "w") as rf:
            json.dump(result, rf, indent=2)
        
        print("[Runner]  Done processing PR:", result)
    except Exception as e:
        print(f"[Runner] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)