# Optimized Prompts for AI CI Failure Triage Demo

## 1. GitHub Actions Workflow
Create a simple GitHub Actions workflow for a Python project that intentionally fails tests.
Requirements:
- checkout code
- setup Python 3.11
- install dependencies from app/requirements.txt
- run pytest
- capture the pytest output into a file called pytest-output.txt
- allow the workflow to continue even if pytest fails
- create failure_context.json from the pytest output
- run scripts/analyze_failure.py after the test step
- write the AI analysis output to the GitHub Actions Step Summary
The AI analysis step must always run even if pytest fails. Use:
- continue-on-error: true for pytest
- if: always() for the failure context, AI analysis, and summary steps
Also include:
- permissions for id-token and contents
- aws-actions/configure-aws-credentials@v4
- OIDC role assumption for a role named github-bedrock-role
- AWS region us-east-1
Save the AI output to analysis-output.json and print it to both:
1. stdout
2. $GITHUB_STEP_SUMMARY

## 2. Bedrock Model Prompt
You are a DevOps CI failure analyzer.
Your job is to analyze Python test failures and determine the root cause.
Return ONLY valid JSON with exactly these fields:
{
  "failure_type": "test_failure | syntax_error | dependency_error | unknown",
  "severity": "low | medium | high",
  "root_cause": "short explanation of the real cause",
  "confidence": 0.0,
  "explanation": "clear explanation of why the failure happened",
  "recommended_fix": "specific action the developer should take"
}
Do not repeat the logs.
Do not include markdown.
Return only JSON.
Repository: {repository_name}
Failing Step: {step_name}
Failure logs:
{error_output}

## 3. Human-Readable Summary
Create a Python script that reads analysis-output.json and prints a Markdown summary for the GitHub Actions Step Summary, using bold labels and clear formatting for each field.

---
These prompts and steps led to a robust, readable, and automated AI CI failure triage demo pipeline.
