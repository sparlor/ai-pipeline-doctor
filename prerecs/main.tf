terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
    github = {
      source  = "integrations/github"
      version = ">= 5.0.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

provider "github" {
}

resource "github_repository" "repo" {
  name        = "ai-pipeline-doctor"
  description = "Terraform setup for AWS Bedrock and GitHub Actions integration"
  visibility     = "public"
  
}

resource "aws_iam_openid_connect_provider" "github" {
	url = "https://token.actions.githubusercontent.com"
	client_id_list = ["sts.amazonaws.com"]
	thumbprint_list = ["6938fd4d98bab03faadb97b343968651c0fdc123"] # GitHub OIDC thumbprint
}

# IAM Role for GitHub Actions
resource "aws_iam_role" "github_actions" {
	name = "github-actions-bedrock-role"

	assume_role_policy = jsonencode({
		Version = "2012-10-17"
		Statement = [
			{
				Effect = "Allow"
				Principal = {
					Federated = aws_iam_openid_connect_provider.github.arn
				}
				Action = "sts:AssumeRoleWithWebIdentity"
				Condition = {
					StringLike = {
						"token.actions.githubusercontent.com:sub" = "repo:sparlor/ai-pipeline-doctor:*"
					}
				}
			}
		]
	})
}

# IAM Policy for Bedrock and Logs
resource "aws_iam_policy" "github_actions_policy" {
	name        = "github-actions-bedrock-logs-policy"
	description = "Policy for Bedrock InvokeModel and CloudWatch Logs"
	policy      = jsonencode({
		Version = "2012-10-17"
		Statement = [
			{
				Effect = "Allow"
				Action = [
					"bedrock:InvokeModel",
					"logs:CreateLogGroup",
					"logs:CreateLogStream"
				]
				Resource = "*"
			}
		]
	})
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "github_actions_attach" {
	role       = aws_iam_role.github_actions.name
	policy_arn = aws_iam_policy.github_actions_policy.arn
}