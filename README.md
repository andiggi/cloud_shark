
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
### 🚀 Quick start
```bash
git clone https://github.com/andiggi/cloud_shark.git
cd cloud_shark
pulumi up   
```

## Prerequisites

 - An AWS account with permissions to create S3 buckets.
 - AWS credentials configured in your environment (for example via AWS CLI or environment variables).
 - Python 3.6 or later installed.
 - Pulumi CLI already installed and logged in.
 
 ## Gotchas
  - Sometimes email for SNS subscription is not sent, 
      login to AWS console and resend the email for confirmation

 ## Getting Started

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
 pulumi config get aws:region
 pulumi config set aws:region us-west-2
 ```

 ## Outputs

 Once deployed, the stack exports:

 - `bucket_name` — the ID of the created S3 bucket.

 Retrieve outputs with:
 ```bash
 pulumi stack output bucket_name
 ```

 ## Next Steps

 - Customize `__main__.py` to add or configure additional resources.
 - Explore the Pulumi AWS SDK: https://www.pulumi.com/registry/packages/aws/
 - Break your infrastructure into modules for better organization.
 - Integrate into CI/CD pipelines for automated deployments.

 ## Help and Community

 If you have questions or need assistance:
 - Pulumi Documentation: https://www.pulumi.com/docs/
 - Community Slack: https://slack.pulumi.com/
 - GitHub Issues: https://github.com/pulumi/pulumi/issues

 Contributions and feedback are always welcome!