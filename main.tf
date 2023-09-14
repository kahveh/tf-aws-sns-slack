data "aws_caller_identity" "current" {}
data "aws_partition" "current" {}
data "aws_region" "current" {}

locals {
  sns_topic_arn        = var.sns_topic_arn
  lambda_function_name = try(var.lambda_function_name, "sns-notify-slack")
  lambda_handler       = try(split(".", basename(var.lambda_source_path))[0], "notify_slack")

  lambda_policy_document = {
    sid       = "AllowWriteToCloudwatchLogs"
    effect    = "Allow"
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = [replace("${try(aws_cloudwatch_log_group.this.arn, "")}:*", ":*:*", ":*")]
  }

  lambda_policy_document_kms = {
    sid       = "AllowKMSDecrypt"
    effect    = "Allow"
    actions   = ["kms:Decrypt"]
    resources = [var.kms_key_arn]
  }

}

## SNS
resource "aws_sns_topic_subscription" "sns_notify_slack" {
  topic_arn           = local.sns_topic_arn
  protocol            = "lambda"
  endpoint            = module.lambda.lambda_function_arn
  filter_policy       = var.subscription_filter_policy
  filter_policy_scope = var.subscription_filter_policy_scope
}

## CloudWatch
resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/lambda/${local.lambda_function_name}"
  retention_in_days = var.cloudwatch_log_group_retention_in_days
  kms_key_id        = var.cloudwatch_log_group_kms_key_id

  tags = merge(var.tags, var.cloudwatch_log_group_tags)
}

## IAM
data "aws_iam_policy_document" "lambda" {
  dynamic "statement" {
    for_each = concat([local.lambda_policy_document], var.kms_key_arn != "" ? [local.lambda_policy_document_kms] : [])
    content {
      sid       = statement.value.sid
      effect    = statement.value.effect
      actions   = statement.value.actions
      resources = statement.value.resources
    }
  }
}

## Lambda
module "lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  function_name = local.lambda_function_name
  description   = var.lambda_description

  handler                        = "${local.lambda_handler}.lambda_handler"
  source_path                    = var.lambda_source_path != null ? "${path.root}/${var.lambda_source_path}" : "${path.module}/lambda"
  recreate_missing_package       = var.recreate_missing_package
  runtime                        = "python3.11"
  timeout                        = 30
  kms_key_arn                    = var.kms_key_arn
  reserved_concurrent_executions = var.reserved_concurrent_executions
  ephemeral_storage_size         = var.lambda_function_ephemeral_storage_size

  publish = true

  environment_variables = {
    SLACK_WEBHOOK_URL = var.slack_webhook_url
    SLACK_CHANNEL     = var.slack_channel
    SLACK_USERNAME    = var.slack_username
    SLACK_EMOJI       = var.slack_emoji
    LOG_EVENTS        = var.log_events ? "True" : "False"
  }

  create_role               = var.lambda_role == ""
  lambda_role               = var.lambda_role
  role_name                 = "${var.iam_role_name_prefix}-${local.lambda_function_name}"
  role_permissions_boundary = var.iam_role_boundary_policy_arn
  role_tags                 = var.iam_role_tags
  role_path                 = var.iam_role_path
  policy_path               = var.iam_policy_path

  attach_cloudwatch_logs_policy = false
  attach_policy_json            = true
  policy_json                   = try(data.aws_iam_policy_document.lambda.json, "")

  use_existing_cloudwatch_log_group = true
  attach_network_policy             = var.lambda_function_vpc_subnet_ids != null

  # Dead Letter
  dead_letter_target_arn    = var.lambda_dead_letter_target_arn
  attach_dead_letter_policy = var.lambda_attach_dead_letter_policy

  # VPC
  vpc_subnet_ids         = var.lambda_function_vpc_subnet_ids
  vpc_security_group_ids = var.lambda_function_vpc_security_group_ids

  # S3 Bucket
  store_on_s3 = var.lambda_function_store_on_s3
  s3_bucket   = var.lambda_function_s3_bucket
  tags        = merge(var.tags, var.lambda_function_tags)

  allowed_triggers = {
    AllowExecutionFromSNS = {
      principal  = "sns.amazonaws.com"
      source_arn = local.sns_topic_arn
    }
  }

  depends_on = [aws_cloudwatch_log_group.this]
}
