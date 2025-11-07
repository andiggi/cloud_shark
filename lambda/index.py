import boto3
import json
import os
from datetime import datetime, timedelta
from decimal import Decimal
import logging

# Initialize AWS clients
ce_client = boto3.client('ce')
sns_client = boto3.client('sns')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_cost_data(start_date, end_date, granularity='DAILY'):
    """Fetch cost data from AWS Cost Explorer"""
    try:
        print(f"Requesting cost data from {start_date} to {end_date}")
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity=granularity,
            Metrics=['UnblendedCost'],
            GroupBy=[
                {
                    'Type': 'DIMENSION',
                    'Key': 'SERVICE'
                }
            ]
        )
        logger.info(f"Cost data response: {json.dumps(response)}")
        
        # Debug output
        if response and 'ResultsByTime' in response:
            print(f"  Found {len(response['ResultsByTime'])} time periods")
            for idx, result in enumerate(response['ResultsByTime']):
                period_start = result.get('TimePeriod', {}).get('Start', 'Unknown')
                groups_count = len(result.get('Groups', []))
                print(f"  Period {idx + 1}: {period_start} - {groups_count} services")
        
        return response
    except Exception as e:
        print(f"Error fetching cost data: {str(e)}")
        return None

def format_currency(amount):
    """Format amount as currency"""
    return f"${float(amount):,.2f}"

def calculate_total_cost(cost_data):
    """Calculate total cost from cost data response"""
    if not cost_data or 'ResultsByTime' not in cost_data:
        return 0
    
    total = 0
    for result in cost_data['ResultsByTime']:
        for group in result.get('Groups', []):
            amount = group['Metrics']['UnblendedCost']['Amount']
            total += float(amount)
    
    return total

def get_top_services(cost_data, top_n=5):
    """Get top N services by cost"""
    service_costs = {}
    
    if not cost_data or 'ResultsByTime' not in cost_data:
        return []
    
    for result in cost_data['ResultsByTime']:
        for group in result.get('Groups', []):
            service = group['Keys'][0]
            amount = float(group['Metrics']['UnblendedCost']['Amount'])
            service_costs[service] = service_costs.get(service, 0) + amount
    
    # Sort by cost and get top N
    sorted_services = sorted(service_costs.items(), key=lambda x: x[1], reverse=True)
    return sorted_services[:top_n]

def create_report():
    """Generate cost report for daily, weekly, and monthly periods"""
    today = datetime.now().date()
    
    # AWS Cost Explorer has a delay - use data from 2 days ago
    # to ensure data is available
    one_day_ago = today - timedelta(days=1)
    two_days_ago = today - timedelta(days=2)
    week_ago = today - timedelta(days=9)  # Extended to account for delay
    month_ago = today - timedelta(days=32)  # Extended to account for delay
    year_ago = today - timedelta(days=360)  # Extended to account for delay
    
    # Format dates for API
    two_days_ago_str = one_day_ago.strftime('%Y-%m-%d')
    three_days_ago_str = two_days_ago.strftime('%Y-%m-%d')
    week_ago_str = week_ago.strftime('%Y-%m-%d')
    month_ago_str = month_ago.strftime('%Y-%m-%d')
    year_ago_str = year_ago.strftime('%Y-%m-%d')
    today_str = (today - timedelta(days=1)).strftime('%Y-%m-%d')  # Yesterday as end date
    
    print(f"Fetching cost data:")
    print(f"  Daily: {three_days_ago_str} to {two_days_ago_str}")
    print(f"  Weekly: {week_ago_str} to {today_str}")
    print(f"  Monthly: {month_ago_str} to {today_str}")
    
    # Fetch cost data
    daily_cost = get_cost_data(three_days_ago_str, two_days_ago_str)
    weekly_cost = get_cost_data(week_ago_str, two_days_ago_str)
    monthly_cost = get_cost_data(month_ago_str, two_days_ago_str)
    yearly_cost = get_cost_data(year_ago_str, two_days_ago_str)
    
    # Calculate totals
    daily_total = calculate_total_cost(daily_cost)
    weekly_total = calculate_total_cost(weekly_cost)
    monthly_total = calculate_total_cost(monthly_cost)
    yearly_total = calculate_total_cost(yearly_cost)
    
    print(f"Calculated totals:")
    print(f"  Daily: ${daily_total:.2f}")
    print(f"  Weekly: ${weekly_total:.2f}")
    print(f"  Monthly: ${monthly_total:.2f}")
    print(f"  Yearly: ${yearly_total:.2f}")
    
    # Get top services
    daily_top_services = get_top_services(daily_cost)
    weekly_top_services = get_top_services(weekly_cost)
    monthly_top_services = get_top_services(monthly_cost)
    yearly_top_services = get_top_services(yearly_cost)

    # Build report
    report = []
    report.append("=" * 60)
    report.append("AWS COST REPORT")
    report.append(f"Generated: {today.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    report.append("=" * 60)
    report.append("")
    
    # Add note about Cost Explorer delay
    report.append("NOTE: AWS Cost Explorer data has a 24-48 hour delay.")
    report.append("Reports show costs from 2-3 days ago for accuracy.")
    report.append("")
    
    # Check if we have any data
    if daily_total == 0 and weekly_total == 0 and monthly_total == 0:
        report.append("⚠️  WARNING: No cost data found!")
        report.append("")
        report.append("Possible reasons:")
        report.append("  • AWS account is very new (< 48 hours of usage)")
        report.append("  • Cost Explorer is not enabled (check AWS Console)")
        report.append("  • No AWS resources have been used yet")
        report.append("  • IAM permissions are missing")
        report.append("")
        report.append(f"Date ranges checked:")
        report.append(f"  Daily: {three_days_ago_str} to {two_days_ago_str}")
        report.append(f"  Weekly: {week_ago_str} to {today_str}")
        report.append(f"  Monthly: {month_ago_str} to {today_str}")
        report.append(f"  Yearly: {year_ago_str} to {today_str}")
        report.append("")
        return "\n".join(report)
    
    # Daily costs
    report.append(f"📊 DAILY COSTS ({three_days_ago_str})")
    report.append("-" * 60)
    report.append(f"Total Cost: {format_currency(daily_total)}")
    if daily_top_services:
        report.append("\nTop Services:")
        for service, cost in daily_top_services:
            report.append(f"  • {service}: {format_currency(cost)}")
    report.append("")
    
    # Weekly costs
    report.append("📊 WEEKLY COSTS (Last 7 Days)")
    report.append("-" * 60)
    report.append(f"Total Cost: {format_currency(weekly_total)}")
    report.append(f"Average Daily Cost: {format_currency(weekly_total / 7)}")
    if weekly_top_services:
        report.append("\nTop Services:")
        for service, cost in weekly_top_services:
            report.append(f"  • {service}: {format_currency(cost)}")
    report.append("")
    
    # Monthly costs
    report.append("📊 MONTHLY COSTS (Last 30 Days)")
    report.append("-" * 60)
    report.append(f"Total Cost: {format_currency(monthly_total)}")
    report.append(f"Average Daily Cost: {format_currency(monthly_total / 30)}")
    if monthly_top_services:
        report.append("\nTop Services:")
        for service, cost in monthly_top_services:
            report.append(f"  • {service}: {format_currency(cost)}")
    report.append("")

    # yearlt costs
    report.append("📊 YEARLY COSTS (Last 12 Months)")
    report.append("-" * 60 )
    report.append(f"Total Cost: {format_currency(yearly_total)}")
    report.append(f"Average Monthly Cost: {format_currency(yearly_total / 12)}")
    if yearly_top_services:
        report.append("\nTop Services:")
        for service, cost in yearly_top_services:
            report.append(f"  • {service}: {format_currency(cost)}")
    report.append("")   

    
    # Summary
    report.append("=" * 60)
    report.append("SUMMARY")
    report.append("=" * 60)
    report.append(f"Daily Cost:   {format_currency(daily_total)}")
    report.append(f"Weekly Cost:  {format_currency(weekly_total)}")
    report.append(f"Monthly Cost: {format_currency(monthly_total)}")
    report.append("")
    report.append(f"Projected Monthly Cost: {format_currency((monthly_total / 30) * 30)}")
    report.append("=" * 60)
    
    return "\n".join(report)

def send_email(report):
    """Send report via SNS"""
    sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')
    
    if not sns_topic_arn:
        print("ERROR: SNS_TOPIC_ARN environment variable not set")
        return False
    
    try:
        response = sns_client.publish(
            TopicArn=sns_topic_arn,
            Subject=f"AWS Cost Report - {datetime.now().strftime('%Y-%m-%d')}",
            Message=report
        )
        print(f"Email sent successfully. MessageId: {response['MessageId']}")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def lambda_handler(event, context):
    """Lambda handler function"""
    print("Starting AWS Cost Reporter...")
    
    try:
        # Generate report
        report = create_report()
        print("Report generated successfully")
        print(report)
        
        # Send email
        email_sent = send_email(report)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Cost report generated and sent successfully' if email_sent else 'Cost report generated but email failed',
                'report': report
            })
        }
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error: {str(e)}'
            })
        }