import json
import sys

def main():
    input_file = "analysis-output.json"
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    summary = (
        f"**Failure Type:** {data.get('failure_type', '')}\n\n"
        f"**Severity:** {data.get('severity', '')}\n\n"
        f"**Root Cause:** {data.get('root_cause', '')}\n\n"
        f"**Confidence:** {data.get('confidence', '')}\n\n"
        f"**Explanation:** {data.get('explanation', '')}\n\n"
        f"**Recommended Fix:** {data.get('recommended_fix', '')}\n"
    )
    print(summary)

if __name__ == "__main__":
    main()
