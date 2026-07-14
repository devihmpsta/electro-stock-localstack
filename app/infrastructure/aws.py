import os
import logging
import boto3
from botocore.exceptions import ClientError
from flask import current_app

logger = logging.getLogger(__name__)

def get_aws_client(service_name: str):
    """
    Creates and returns a Boto3 client for the given service name, configured for LocalStack
    using environment variables or Flask configuration.
    """
    try:
        endpoint_url = current_app.config.get('AWS_ENDPOINT_URL')
        region_name = current_app.config.get('AWS_DEFAULT_REGION', 'ap-southeast-1')
        aws_access_key_id = current_app.config.get('AWS_ACCESS_KEY_ID', 'test')
        aws_secret_access_key = current_app.config.get('AWS_SECRET_ACCESS_KEY', 'test')
    except RuntimeError:
        # Outside of Flask application context, read environment variables directly
        endpoint_url = os.getenv('AWS_ENDPOINT_URL', 'http://localhost:4566')
        region_name = os.getenv('AWS_DEFAULT_REGION', 'ap-southeast-1')
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID', 'test')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY', 'test')

    return boto3.client(  # type: ignore
        service_name,
        endpoint_url=endpoint_url,
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

def get_s3_client():
    """Returns an S3 client configured for LocalStack."""
    return get_aws_client('s3')

def get_ec2_client():
    """Returns an EC2 client configured for LocalStack."""
    return get_aws_client('ec2')

def init_s3_bucket(app) -> None:
    """
    Initializes the required S3 buckets on startup using StorageService.
    Re-uploads any backed-up local files to restore persistence across LocalStack recreations.
    """
    with app.app_context():
        try:
            from app.application.services.storage import StorageService
            storage = StorageService()
            storage.create_bucket()
            
            # Restore local backups to S3 on startup
            import os
            uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
            if os.path.exists(uploads_dir):
                for filename in os.listdir(uploads_dir):
                    local_path = os.path.join(uploads_dir, filename)
                    if os.path.isfile(local_path):
                        logger.info(f"Restoring S3 backup for file '{filename}'...")
                        with open(local_path, 'rb') as f:
                            storage.s3_client.upload_fileobj(f, storage.bucket_name, filename)
                logger.info("S3 backup restoration complete.")
        except Exception as e:
            logger.error(f"Failed to initialize S3 bucket via StorageService: {e}")

