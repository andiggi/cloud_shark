import pulumi
import pulumi_aws as aws
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get environment variables
email_address = os.getenv('EMAIL_ADDRESS')
report_schedule = os.getenv('REPORT_SCHEDULE', 'cron(0 9 * * ? *)')  # Daily at 9 AM UTC

if not email_address:
    raise Exception("EMAIL_ADDRESS must be set in .env file")

# Create SNS Topic for email notifications
sns_topic = aws.sns.Topic("cost-report-topic",
    display_name="AWS Cost Report Notifications"
)

# Subscribe email to SNS topic
sns_subscription = aws.sns.TopicSubscription("cost-report-email-subscription",
    topic=sns_topic.arn,
    protocol="email",
    endpoint=email_address
)

# Create IAM role for Lambda
lambda_role = aws.iam.Role("cost-reporter-lambda-role",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            }
        }]
    })
)

# Attach policies to Lambda role
lambda_basic_policy = aws.iam.RolePolicyAttachment("lambda-basic-execution",
    role=lambda_role.name,
    policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
)

# Custom policy for Cost Explorer and SNS
lambda_custom_policy = aws.iam.RolePolicy("lambda-custom-policy",
    role=lambda_role.id,
    policy=sns_topic.arn.apply(lambda arn: json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ce:GetCostAndUsage",
                    "ce:GetCostForecast"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "sns:Publish"
                ],
                "Resource": arn
            }
        ]
    }))
)

# Create Lambda function
lambda_function = aws.lambda_.Function("cost-reporter-lambda",
    role=lambda_role.arn,
    runtime="python3.11",
    handler="index.lambda_handler",
    code=pulumi.FileArchive("./lambda"),
    timeout=60,
    memory_size=256,
    environment=aws.lambda_.FunctionEnvironmentArgs(
        variables={
            "SNS_TOPIC_ARN": sns_topic.arn,
        }
    )
)

# Create EventBridge rule for scheduling
eventbridge_rule = aws.cloudwatch.EventRule("cost-reporter-schedule",
    description="Trigger cost reporter Lambda function",
    schedule_expression=report_schedule
)

# Grant EventBridge permission to invoke Lambda
lambda_permission = aws.lambda_.Permission("eventbridge-invoke-permission",
    action="lambda:InvokeFunction",
    function=lambda_function.name,
    principal="events.amazonaws.com",
    source_arn=eventbridge_rule.arn
)

# Create EventBridge target
eventbridge_target = aws.cloudwatch.EventTarget("cost-reporter-target",
    rule=eventbridge_rule.name,
    arn=lambda_function.arn
)

# Export outputs
pulumi.export("sns_topic_arn", sns_topic.arn)
pulumi.export("lambda_function_name", lambda_function.name)
pulumi.export("eventbridge_rule_name", eventbridge_rule.name)