"""
Lambda Function: Event-Driven Glue Job Orchestration
Triggers Glue ETL jobs when new data arrives in S3
Implements error handling, retry logic, and SNS notifications
"""

import json
import os
import boto3
from datetime import datetime
from typing import Dict, Any

glue_client = boto3.client('glue')
sns_client = boto3.client('sns')
s3_client = boto3.client('s3')

GLUE_JOB_NAME = os.environ['GLUE_JOB_NAME']
PROCESSED_JOB_NAME = os.environ['PROCESSED_JOB_NAME']
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']
ENVIRONMENT = os.environ['ENVIRONMENT']
DATABASE_NAME = os.environ['DATABASE_NAME']


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for S3 event-driven Glue job orchestration
    """
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract S3 event details
        s3_event = extract_s3_event_details(event)
        
        if not s3_event:
            return create_response(400, "Invalid S3 event")
        
        bucket_name = s3_event['bucket']
        object_key = s3_event['key']
        
        print(f"Processing S3 object: s3://{bucket_name}/{object_key}")
        
        # Validate file type
        if not is_valid_file_type(object_key):
            print(f"Skipping non-data file: {object_key}")
            return create_response(200, "File type not supported for processing")
        
        # Check if Glue job is already running
        if is_job_running(GLUE_JOB_NAME):
            print(f"Glue job {GLUE_JOB_NAME} is already running. Skipping trigger.")
            return create_response(200, "Job already running")
        
        # Start Glue ETL job
        job_run_id = start_glue_job(
            job_name=GLUE_JOB_NAME,
            bucket_name=bucket_name,
            object_key=object_key
        )
        
        print(f"Started Glue job: {GLUE_JOB_NAME}, Run ID: {job_run_id}")
        
        # Send success notification
        send_notification(
            subject=f"Glue Job Started - {GLUE_JOB_NAME}",
            message=f"Glue job triggered successfully.\n\n"
                   f"Job Name: {GLUE_JOB_NAME}\n"
                   f"Run ID: {job_run_id}\n"
                   f"Triggered by: s3://{bucket_name}/{object_key}\n"
                   f"Environment: {ENVIRONMENT}\n"
                   f"Timestamp: {datetime.utcnow().isoformat()}"
        )
        
        return create_response(
            200,
            f"Successfully triggered Glue job: {job_run_id}",
            {"job_run_id": job_run_id}
        )
        
    except Exception as e:
        error_message = f"Error triggering Glue job: {str(e)}"
        print(error_message)
        
        send_notification(
            subject=f"ERROR - Glue Job Trigger Failed",
            message=f"Failed to trigger Glue job.\n\n"
                   f"Error: {str(e)}\n"
                   f"Environment: {ENVIRONMENT}\n"
                   f"Timestamp: {datetime.utcnow().isoformat()}"
        )
        
        return create_response(500, error_message)


def extract_s3_event_details(event: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract bucket and key from EventBridge S3 event
    """
    try:
        detail = event.get('detail', {})
        bucket_name = detail.get('bucket', {}).get('name')
        object_key = detail.get('object', {}).get('key')
        
        if not bucket_name or not object_key:
            return None
        
        return {
            'bucket': bucket_name,
            'key': object_key
        }
    except Exception as e:
        print(f"Error extracting S3 event details: {str(e)}")
        return None


def is_valid_file_type(object_key: str) -> bool:
    """
    Check if file type is valid for processing
    """
    valid_extensions = ['.csv', '.json', '.parquet']
    return any(object_key.lower().endswith(ext) for ext in valid_extensions)


def is_job_running(job_name: str) -> bool:
    """
    Check if Glue job is currently running
    """
    try:
        response = glue_client.get_job_runs(
            JobName=job_name,
            MaxResults=1
        )
        
        if not response.get('JobRuns'):
            return False
        
        latest_run = response['JobRuns'][0]
        return latest_run['JobRunState'] in ['RUNNING', 'STARTING', 'STOPPING']
        
    except Exception as e:
        print(f"Error checking job status: {str(e)}")
        return False


def start_glue_job(job_name: str, bucket_name: str, object_key: str) -> str:
    """
    Start Glue ETL job with custom arguments
    """
    response = glue_client.start_job_run(
        JobName=job_name,
        Arguments={
            '--S3_INPUT_PATH': f"s3://{bucket_name}/{object_key}",
            '--TRIGGERED_BY': 'EventBridge',
            '--TRIGGER_TIME': datetime.utcnow().isoformat()
        }
    )
    
    return response['JobRunId']


def send_notification(subject: str, message: str) -> None:
    """
    Send SNS notification
    """
    try:
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message
        )
        print(f"Notification sent: {subject}")
    except Exception as e:
        print(f"Failed to send notification: {str(e)}")


def create_response(status_code: int, message: str, data: Dict = None) -> Dict[str, Any]:
    """
    Create standardized Lambda response
    """
    response = {
        'statusCode': status_code,
        'body': json.dumps({
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data or {}
        })
    }
    return response
