
# 🦈 Cloud Shark — AWS Cost Reports by Email

> Automated cost reports for AWS — delivered daily, weekly, or monthly.

Cloud Shark runs entirely on AWS (Lambda + SNS + Cost Explorer).  
It keeps track of your AWS spending trends and sends cost summaries straight to your inbox.

✅ **Why use it**
- Stop surprise bills before they happen  
- Understand service-wise spend trends  
- Easy to fork / customize / self-host  
- 100 % open source — written in Python 🐍

---

 ## Outputs

 send email of cost assesment daily weekly, monthly and yearly
 Smaple email (truncated)
 ```
 ============================================================
AWS COST REPORT
Generated: 2025-11-07 00:00:00 UTC
============================================================

NOTE: AWS Cost Explorer data has a 24-48 hour delay.
Reports show costs from 2-3 days ago for accuracy.

📊 DAILY COSTS (2025-11-05)
📊 YEARLY COSTS (Last 12 Months)
------------------------------------------------------------
Total Cost: $15.34
Average Monthly Cost: $1.28

Top Services:
  • Amazon Registrar: $13.00
  • Tax: $2.34

```

### 🚀 Quick start
```bash
git clone https://github.com/andiggi/cloud_shark.git
cd cloud_shark
pulumi up   
```



## Prerequisites

 - AWS credentials configured in your environment (for example via AWS CLI or environment variables).
 - permissions needed:

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "LambdaCoreAccess",
      "Effect": "Allow",
      "Action": [
        "lambda:CreateFunction",
        "lambda:UpdateFunctionCode",
        "lambda:UpdateFunctionConfiguration",
        "lambda:InvokeFunction",
        "lambda:GetFunction",
        "lambda:ListFunctions"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CloudWatchLogsAccess",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    },
    {
      "Sid": "SNSAccess",
      "Effect": "Allow",
      "Action": [
        "sns:Publish",
        "sns:CreateTopic",
        "sns:Subscribe",
        "sns:ListTopics",
        "sns:GetTopicAttributes"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CostExplorerAccess",
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage",
        "ce:GetCostForecast",
        "ce:GetDimensionValues",
        "ce:GetReservationUtilization",
        "ce:GetSavingsPlansUtilization",
        "ce:GetSavingsPlansUtilizationDetails"
      ],
      "Resource": "*"
    }    
  ]
}

```
 - Python 3.6 or later installed.
 - Pulumi CLI already installed and logged in.
 
 ## Gotchas
  - setup pulumi first
  - make sure your access_key has the required permissions (tweak them removing what you feel not required, haven't tested extensively)
 
 ## pulumi setup - tentative

 1. First Generate a new project from this template:
    ```bash
    pulumi new aws-python
    ```
 2. Follow the prompts to set your project name and AWS region (default: `us-east-1`).
 3. Change into your project directory:
    ```bash
    cd <project-name>
    ```
 4. Preview the planned changes:
    ```bash
    pulumi preview
    ```
 5. Deploy the stack:
    ```bash
    pulumi up
    ```
 6. Tear down when finished:
    ```bash
    pulumi destroy
    ```

 ## Project Layout

 After running `pulumi new`, your directory will look like:
 ```
 ├── __main__.py         # Entry point of the Pulumi program
 ├── Pulumi.yaml         # Project metadata and template configuration
 ├── requirements.txt    # Python dependencies
 └── Pulumi.<stack>.yaml # Stack-specific configuration (e.g., Pulumi.dev.yaml)
 ```

 ## Configuration

 This template defines the following config value:

 - `aws:region` (string)
   The AWS region to deploy resources into.
   Default: `us-east-1`

 View or update configuration with:
 ```bash
 pulumi config set aws:region us-west-2
 ```


 
 ## Help and Community

 If you have questions or need assistance:
 - Pulumi Documentation: https://www.pulumi.com/docs/
 - Community Slack: https://slack.pulumi.com/
 - GitHub Issues: https://github.com/pulumi/pulumi/issues

 Contributions and feedback are always welcome!