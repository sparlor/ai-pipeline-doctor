import sys
import json
import re
import boto3
import os

# Usage: python analyze_failure.py <input_file> <output_file> [repository_name] [step_name]

def classify_failure(log):
    if re.search(r'FAILED|AssertionError|assert ', log):
        return "test_failure"
    if re.search(r'SyntaxError', log):
        return "syntax_error"
    if re.search(r'No module named|ModuleNotFoundError|ImportError|Could not find a version', log):
        return "dependency_error"
    return "unknown"

def determine_severity(failure_type, log):
    if failure_type == "syntax_error":
        return "high"
    if failure_type == "dependency_error":
        return "high"
    if failure_type == "test_failure":
        if re.search(r'assert ', log):
            return "medium"
        return "low"
    return "medium"

def extract_root_cause(failure_type, log):
    if failure_type == "syntax_error":
        m = re.search(r'File ".*", line (\d+).*?\n\s*(.*)\n\s*\^\nSyntaxError: (.*)', log, re.DOTALL)
        if m:
            return f"Syntax error on line {m.group(1)}: {m.group(3)}"
        return "Syntax error detected"
    if failure_type == "dependency_error":
        m = re.search(r'No module named [\'\"](.*?)[\'\"]', log)
        if m:
            return f"Missing module: {m.group(1)}"
        m = re.search(r'Could not find a version that satisfies the requirement (.*?) ', log)
        if m:
            return f"Unresolved dependency: {m.group(1)}"
        return "Dependency error detected"
    if failure_type == "test_failure":
        m = re.search(r'AssertionError: (.*)', log)
        if m:
            return f"Assertion failed: {m.group(1)}"
        return "Test assertion failed"
    return "Unknown failure type"

def recommend_fix(failure_type, log):
    if failure_type == "syntax_error":
        return "Fix the syntax error as indicated in the traceback."
    if failure_type == "dependency_error":
        return "Install the missing or correct dependency in requirements.txt."
    if failure_type == "test_failure":
        return "Review the failing test and correct the code or test logic."
    return "Check the logs for more details."

def main():

    if len(sys.argv) < 3:
        print("Usage: python analyze_failure.py <input_file> <output_file> [repository_name] [step_name]", file=sys.stderr)
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    repository_name = sys.argv[3] if len(sys.argv) > 3 else ""
    step_name = sys.argv[4] if len(sys.argv) > 4 else ""

    with open(input_file, "r", encoding="utf-8") as f:
        log = f.read()

    # Build prompt for Bedrock Claude
    prompt = (
        "You are a DevOps CI failure analyzer.\n"
        "Your job is to analyze Python test failures and determine the root cause.\n"
        "Return ONLY valid JSON with exactly these fields:\n"
        "{\n  \"failure_type\": \"test_failure | syntax_error | dependency_error | unknown\",\n  \"severity\": \"low | medium | high\",\n  \"root_cause\": \"short explanation of the real cause\",\n  \"confidence\": 0.0,\n  \"explanation\": \"clear explanation of why the failure happened\",\n  \"recommended_fix\": \"specific action the developer should take\"\n}\n"
        "Do not repeat the logs.\n"
        "Do not include markdown.\n"
        "Return only JSON.\n"
        f"Repository: {repository_name}\n"
        f"Failing Step: {step_name}\n"
        f"Failure logs:\n{log}\n"
    )

    # Call AWS Bedrock Claude
    try:
        client = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION", "us-east-1"))
        model_id = "anthropic.claude-3-haiku-20240307-v1:0"
        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({"prompt": prompt, "max_tokens": 512})
        )
        result_json = json.loads(response["body"].read())
        ai_output = result_json.get("completion", "")
        # Try to parse the output as JSON
        try:
            ai_result = json.loads(ai_output)
        except Exception:
            ai_result = {"error": "AI output was not valid JSON", "raw": ai_output}
    except Exception as e:
        ai_result = {"error": f"Bedrock call failed: {e}"}

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(ai_result, f, indent=2)

    print(json.dumps(ai_result, indent=2))

if __name__ == "__main__":
    main()
